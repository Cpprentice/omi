"""
Generic XML → RDF staging-graph walker with per-spec configs.

Converts attribute-rich metadata XML (e.g. the DataCite kernel) into a
"staging" RDF graph that SHACL crosswalk rules can consume. The walker makes
no semantic decisions — it applies six mechanical conventions (see the
crosswalk pipeline design doc):

1. Plural wrapper elements (``<creators><creator>…``) collapse into repeated
   properties; the wrapper vanishes.
2. An element with attributes (or children) becomes a node: its text content
   goes to ``<ns>value``, each attribute becomes a property.
3. ``xml:lang`` becomes an RDF language tag on the value literal.
4. Elements listed as order-significant carry a 1-based ``<ns>position``.
5. Nodes get deterministic skolem IRIs (root IRI + ``#creator-1`` …);
   the graph contains no blank nodes.
6. Enumeration attributes stay plain literals — vocabulary translation is a
   SHACL rule's job, not the walker's.

Integration into the transformation module's ingest::

    from omi.xml_ingest import DATACITE_CONFIG, ingest_xml

    # in ingest_file(), route bare .xml files to the walker instead of
    # rdflib's RDF/XML parser (which cannot read DataCite kernel XML):
    elif file_format == "xml":
        graph = ingest_xml(input_data_file_path, DATACITE_CONFIG)

The same per-spec config is designed to drive the egress direction
(staging graph → dict → XML template) later.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from rdflib import RDF, Graph, Literal, Namespace, URIRef

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

XML_LANG_ATTRIBUTE = "{http://www.w3.org/XML/1998/namespace}lang"


class XmlIngestError(Exception):
    """Raised when XML cannot be converted into a staging graph."""


@dataclass(frozen=True)
class XmlWalkerConfig:
    """
    Per-spec configuration for the generic XML walker.

    Attributes
    ----------
    namespace: str
        Staging namespace all element/attribute names are minted in.
    prefix: str
        Prefix to bind the staging namespace to in the output graph.
    root_type: str
        Local name of the class the document root node is typed as.
    root_iri: Callable[[ET.Element], Optional[str]]
        Derives the root node IRI from the document (e.g. from the DOI).
        Returning None falls back to ``fallback_root_iri``.
    fallback_root_iri: str
        Root IRI used when ``root_iri`` finds no identity in the document.
    non_wrappers: frozenset[str]
        Elements never collapsed as wrappers even if they structurally look
        like one (e.g. ``geoLocationPolygon`` groups its ordered points).
    ordered: frozenset[str]
        Elements whose document order is significant; they receive a
        1-based ``<ns>position`` property.

    """

    namespace: str
    prefix: str
    root_type: str
    root_iri: Callable[[ET.Element], str | None]
    fallback_root_iri: str
    non_wrappers: frozenset = frozenset()
    ordered: frozenset = frozenset()


def _local_name(tag: str) -> str:
    """Strip the XML namespace part from a tag name."""
    return tag.rsplit("}", 1)[-1]


def _element_text(element: ET.Element) -> str:
    """Return stripped text content of an element ('' if none)."""
    return (element.text or "").strip()


def _is_wrapper(element: ET.Element, config: XmlWalkerConfig) -> bool:
    """
    Decide whether an element is a plural wrapper to collapse.

    A wrapper has no attributes, no text, at least one child, and all
    children share one tag — unless the config vetoes it.
    """
    children = list(element)
    if not children or element.attrib or _element_text(element):
        return False
    if _local_name(element.tag) in config.non_wrappers:
        return False
    first_tag = children[0].tag
    return all(child.tag == first_tag for child in children)


def _datacite_root_iri(root: ET.Element) -> str | None:
    """Mint the resource IRI from the DataCite mandatory DOI identifier."""
    for child in root:
        if _local_name(child.tag) == "identifier" and child.get("identifierType", "").upper() == "DOI":
            doi = _element_text(child)
            if doi:
                return f"https://doi.org/{doi}"
    return None


DATACITE_CONFIG = XmlWalkerConfig(
    namespace="https://schema.datacite.org/meta/kernel-4/#",
    prefix="dck",
    root_type="Resource",
    root_iri=_datacite_root_iri,
    fallback_root_iri="urn:omi:xml-ingest:datacite:resource",
    # geoLocationPolygon structurally looks like a wrapper (all children are
    # polygonPoint) but the polygon grouping and point order carry meaning.
    non_wrappers=frozenset({"geoLocationPolygon"}),
    ordered=frozenset({"creator", "contributor", "polygonPoint"}),
)


class _Walker:
    """Stateful walk of one XML document into one staging graph."""

    def __init__(self, config: XmlWalkerConfig) -> None:
        self.config = config
        self.namespace = Namespace(config.namespace)
        self.graph = Graph()
        self.graph.bind(config.prefix, self.namespace)

    def walk(self, root: ET.Element) -> Graph:
        """Convert the document rooted at `root` into the staging graph."""
        root_iri = self.config.root_iri(root) or self.config.fallback_root_iri
        subject = URIRef(root_iri)
        self.graph.add((subject, RDF.type, self.namespace[self.config.root_type]))
        self._walk_children(root, subject, fragment_base=root_iri)
        return self.graph

    def _walk_children(self, element: ET.Element, subject: URIRef, fragment_base: str) -> None:
        """Attach all children of `element` as properties of `subject`."""
        tag_counters: dict[str, int] = {}
        for child in element:
            if _is_wrapper(child, self.config):
                self._walk_children(child, subject, fragment_base)
            else:
                self._add_property(child, subject, fragment_base, tag_counters)

    def _add_property(
        self,
        element: ET.Element,
        subject: URIRef,
        fragment_base: str,
        tag_counters: dict[str, int],
    ) -> None:
        """Attach one non-wrapper element as a property of `subject`."""
        name = _local_name(element.tag)
        tag_counters[name] = tag_counters.get(name, 0) + 1
        index = tag_counters[name]
        predicate = self.namespace[name]

        language = element.attrib.get(XML_LANG_ATTRIBUTE)
        attributes = {k: v for k, v in element.attrib.items() if k != XML_LANG_ATTRIBUTE}
        children = list(element)
        text = _element_text(element)

        # Any attribute — including xml:lang — promotes the element to a node,
        # so one property always has one shape (rules never face literal-or-node).
        is_plain_literal = not element.attrib and not children and name not in self.config.ordered
        if is_plain_literal:
            self.graph.add((subject, predicate, Literal(text, lang=language)))
            return

        separator = "#" if "#" not in fragment_base else "-"
        node_iri = f"{fragment_base}{separator}{name}-{index}"
        node = URIRef(node_iri)
        self.graph.add((subject, predicate, node))
        if text:
            self.graph.add((node, self.namespace["value"], Literal(text, lang=language)))
        for attribute_name, attribute_value in attributes.items():
            self.graph.add((node, self.namespace[_local_name(attribute_name)], Literal(attribute_value)))
        if name in self.config.ordered:
            self.graph.add((node, self.namespace["position"], Literal(index)))
        self._walk_children(element, node, fragment_base=node_iri)


def ingest_xml(source: Union[Path, str], config: XmlWalkerConfig) -> Graph:
    """
    Ingest a metadata XML file into an RDF staging graph.

    Parameters
    ----------
    source: Union[Path, str]
        Path to the XML file.
    config: XmlWalkerConfig
        Per-spec walker configuration (e.g. ``DATACITE_CONFIG``).

    Returns
    -------
    Graph
        Staging graph in the config's namespace; no blank nodes.

    Raises
    ------
    XmlIngestError
        If the file cannot be parsed as XML.

    """
    try:
        tree = ET.parse(source)  # noqa: S314 - metadata files from known sources
    except ET.ParseError as error:
        raise XmlIngestError(f"Cannot parse XML file {source}: {error}") from error
    return _Walker(config).walk(tree.getroot())
