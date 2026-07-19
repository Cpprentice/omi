"""Tests for the generic XML → staging-graph walker (DataCite config)."""

from pathlib import Path

import pytest
from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef

from omi.crosswalks.xml_ingest import DATACITE_CONFIG, XmlIngestError, ingest_xml

DCK = Namespace("https://schema.datacite.org/meta/kernel-4/#")
RESOURCE = URIRef("https://doi.org/10.82433/B09Z-4K37")
EXAMPLE_XML = Path(__file__).parent / "test_data" / "transformation" / "datacite-example-full-v4.xml"


@pytest.fixture(scope="module")
def graph() -> Graph:
    """Ingest the full DataCite example once for all tests."""
    return ingest_xml(EXAMPLE_XML, DATACITE_CONFIG)


def test_write_datacite_turtle(graph: Graph) -> None:
    graph.serialize(destination=str(Path("tests/test_data/transformation/datacite_example.ttl").absolute()), format="longturtle")


def test_root_iri_is_minted_from_doi(graph: Graph) -> None:
    """The resource node IRI comes from the mandatory DOI identifier."""
    assert (RESOURCE, RDF.type, DCK.Resource) in graph


def test_no_blank_nodes(graph: Graph) -> None:
    """Skolemization: every node is an IRI, no blank nodes anywhere."""
    for subject, _, obj in graph:
        assert not isinstance(subject, BNode)
        assert not isinstance(obj, BNode)


def test_wrapper_collapse_creators(graph: Graph) -> None:
    """<creators><creator> collapses into repeated dck:creator properties."""
    creators = list(graph.objects(RESOURCE, DCK.creator))
    assert len(creators) == 2
    assert (RESOURCE, DCK.creators, None) not in graph


def test_creator_order_is_staged(graph: Graph) -> None:
    """Order-significant creators carry 1-based dck:position."""
    positions = sorted(
        int(graph.value(creator, DCK.position))
        for creator in graph.objects(RESOURCE, DCK.creator)
    )
    assert positions == [1, 2]


def test_attributed_element_becomes_node_with_value(graph: Graph) -> None:
    """An element with attributes stages as node: text -> dck:value, attributes -> properties."""
    identifier = graph.value(RESOURCE, DCK.identifier)
    assert isinstance(identifier, URIRef)
    assert graph.value(identifier, DCK.value) == Literal("10.82433/B09Z-4K37")
    assert graph.value(identifier, DCK.identifierType) == Literal("DOI")


def test_xml_lang_becomes_language_tag(graph: Graph) -> None:
    """xml:lang lands as an RDF language tag on the value literal."""
    title_values = {graph.value(t, DCK.value) for t in graph.objects(RESOURCE, DCK.title)}
    assert Literal("Example Title", lang="en") in title_values
    assert Literal("Example TranslatedTitle", lang="fr") in title_values


def test_titles_keep_title_type(graph: Graph) -> None:
    """TitleType attributes survive; the plain main title has none."""
    title_types = [graph.value(t, DCK.titleType) for t in graph.objects(RESOURCE, DCK.title)]
    assert sorted(str(t) for t in title_types if t is not None) == [
        "AlternativeTitle",
        "Subtitle",
        "TranslatedTitle",
    ]
    assert sum(1 for t in title_types if t is None) == 1


def test_text_only_repeated_elements_stay_plain_literals(graph: Graph) -> None:
    """sizes/formats wrappers collapse to plain literal properties."""
    assert set(graph.objects(RESOURCE, DCK.size)) == {Literal("1 MB"), Literal("90 pages")}
    # DCK["format"]: attribute access would hit str.format, an rdflib Namespace gotcha
    assert set(graph.objects(RESOURCE, DCK["format"])) == {Literal("application/xml"), Literal("text/plain")}


def test_polygon_is_not_collapsed_and_points_are_ordered(graph: Graph) -> None:
    """GeoLocationPolygon stays a node; its 5 points carry positions 1..5."""
    geo_location = graph.value(RESOURCE, DCK.geoLocation)
    polygon = graph.value(geo_location, DCK.geoLocationPolygon)
    assert polygon is not None
    points = list(graph.objects(polygon, DCK.polygonPoint))
    assert len(points) == 5
    positions = sorted(int(graph.value(p, DCK.position)) for p in points)
    assert positions == [1, 2, 3, 4, 5]


def test_nested_related_item_keeps_structure(graph: Graph) -> None:
    """RelatedItem nests its own collapsed creators/titles below the item node."""
    related_item = graph.value(RESOURCE, DCK.relatedItem)
    assert related_item is not None
    assert graph.value(related_item, DCK.relatedItemType) == Literal("Text")
    item_titles = list(graph.objects(related_item, DCK.title))
    assert len(item_titles) == 2


def test_invalid_xml_raises(tmp_path: Path) -> None:
    """Broken XML surfaces as XmlIngestError, not a bare parse error."""
    broken = tmp_path / "broken.xml"
    broken.write_text("<resource><unclosed></resource>")
    with pytest.raises(XmlIngestError):
        ingest_xml(broken, DATACITE_CONFIG)
