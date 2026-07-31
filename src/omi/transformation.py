"""Transformation Module for OMI to convert to and from OEMetadata"""

import io
import json
from pathlib import Path

from pyshacl import shacl_rules
from rdflib import Graph

from omi.crosswalks.xml_ingest import DATACITE_CONFIG, XmlIngestError, ingest_xml

"""
Idea of the process:
Get Input data -> ingest into rdflib graph ->  perform crosswalk -> egress as rdf () -> output as file

Needed Functions:
- Detect input file format
- Transform input format into useable format by rdflib -> see https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.parsers/#rdflib.plugins.parsers
    - json -> jsonld
- Create Graph from Input
- Perform Crosswalk -> (Mapping will be presented in shacl rules)
- Output in specified format
"""

# The forked/pinned OEMetadata JSON-LD context (see field inventory: the
# shipped context needs repair before use). Until the repaired context file
# lands here, plain JSON without '@context' is rejected loudly instead of
# silently ingesting zero triples.
OEM_CONTEXT_FILE = Path(__file__).parent / "contexts" / "oemetadata_v2.jsonld"


class TransformationError(Exception):
    """Raised when a transformation produces an error"""


def detect_file_format(input_data_file_path: Path) -> str:
    """Helper function that checks the file format and returns the format name.

    Parameters
    ----------
    input_data_file_path : Path
        Path to the input file

    Returns
    -------
    str
        The detected format (e.g., 'json', 'datacite-xml', 'turtle', 'n3', 'nt', 'rdfa', 'jsonld')

    Raises
    ------
    TransformationError
        If the file format cannot be detected or is not supported
    """
    suffix = input_data_file_path.suffix.lower()

    format_map = {
        '.json': 'json',
        '.jsonld': 'json-ld',
        # bare .xml is metadata-spec XML (DataCite kernel), handled by the
        # generic XML walker — NOT RDF/XML, which rdflib's 'xml' parser expects
        '.xml': 'datacite-xml',
        '.rdf': 'xml',
        '.ttl': 'turtle',
        '.turtle': 'turtle',
        '.n3': 'n3',
        '.nt': 'nt',
        '.ntriples': 'nt',
        '.html': 'rdfa',
        '.xhtml': 'rdfa',
    }

    file_format = format_map.get(suffix)

    if file_format is None:
        raise TransformationError(f"Unsupported file format: {suffix}. Supported formats: {list(format_map.keys())}")

    return file_format


def _load_oem_context() -> dict:
    """Load the pinned OEMetadata JSON-LD context for plain-JSON input.

    Returns
    -------
    dict
        The parsed context document (with an '@context' key)

    Raises
    ------
    TransformationError
        If no context file is available
    """
    if not OEM_CONTEXT_FILE.exists():
        raise TransformationError(
            "Plain JSON input carries no '@context' and the pinned OEMetadata context file "
            f"is missing ({OEM_CONTEXT_FILE}). Without a context every key would be dropped "
            "silently (0 triples). Provide '@context' in the input or add the context file."
        )
    return json.loads(OEM_CONTEXT_FILE.read_text(encoding='utf-8'))


def _transform_json_to_jsonld(input_data: dict) -> dict:
    """Transform plain JSON to JSON-LD format for rdflib consumption.

    Attaches the pinned OEMetadata context when the input has none — an empty
    context would silently drop every key.

    Parameters
    ----------
    input_data : dict
        The parsed JSON data

    Returns
    -------
    dict
        JSON-LD formatted data
    """
    if '@context' in input_data:
        return input_data
    oem_context = _load_oem_context()
    return {'@context': oem_context['@context'], **input_data}


def ingest_file(input_data_file_path: Path) -> Graph:
    """Ingest data from a file into an rdflib Graph.

    Handles various input formats including JSON (transformed to JSON-LD),
    JSON-LD, DataCite kernel XML (via the generic XML walker), RDF/XML,
    Turtle, N-Triples, etc.

    Parameters
    ----------
    input_data_file_path : Path
        Path to the input file

    Returns
    -------
    Graph
        An rdflib Graph containing the parsed data

    Raises
    ------
    TransformationError
        If the file cannot be parsed or the format is unsupported
    """
    file_format = detect_file_format(input_data_file_path)

    graph = Graph()

    if file_format == 'json':
        with open(input_data_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        jsonld_data = _transform_json_to_jsonld(json_data)

        graph.parse(data=json.dumps(jsonld_data), format='json-ld')
    elif file_format == 'json-ld':
        with open(input_data_file_path, 'r', encoding='utf-8') as f:
            jsonld_content = f.read()

        graph.parse(data=jsonld_content, format='json-ld')
    elif file_format == 'datacite-xml':
        try:
            graph = ingest_xml(input_data_file_path, DATACITE_CONFIG)
        except XmlIngestError as error:
            raise TransformationError(str(error)) from error
    else:
        graph.parse(str(input_data_file_path), format=file_format)

    if len(graph) == 0:
        raise TransformationError(
            f"Ingest of {input_data_file_path.name} produced 0 triples — "
            "likely a context/key mismatch (keys without IRI mappings are dropped silently)."
        )

    return graph


def perform_crosswalk(input_graph: Graph, crosswalk_file_path: Path) -> Graph:
    """Perform the crosswalk transformation on the input graph using SHACL rules.

    Runs the SHACL-AF rules (pySHACL Rules Expander Mode) and returns only the
    derived triples — the target-shaped staging graph.

    Parameters
    ----------
    input_graph : Graph
        The input rdflib Graph to transform
    crosswalk_file_path : Path
        Path to the SHACL rules file (expected in Turtle format)

    Returns
    -------
    Graph
        The derived rdflib Graph after applying SHACL rules
    """
    rules_graph = Graph()
    rules_graph.parse(str(crosswalk_file_path), format='turtle')

    output_graph = shacl_rules(input_graph, shacl_graph=rules_graph, advanced=True, inplace=False, debug=True)

    # shacl_rules() may return a Dataset (quads); keep only the new triples.
    # Staging namespaces differ from input namespaces by design, so rules
    # never need to re-assert an input triple.
    derived = Graph()
    for triple in output_graph.default_graph.triples((None, None, None)):
        if triple not in input_graph:
            derived.add(triple)

    # carry the crosswalk's namespace bindings (e.g. dck:, exOut:) along
    for prefix, namespace in rules_graph.namespaces():
        derived.bind(prefix, namespace)

    return derived


def egress_graph(graph: Graph, output_stream: io.IOBase, output_format: str = 'turtle') -> None:
    """Serialize and write the RDF graph to the output stream.

    Parameters
    ----------
    graph : Graph
        The rdflib Graph to serialize
    output_stream : io.IOBase
        The stream to write the output to
    output_format : str, optional
        The output format (default: 'turtle')
        Supported formats: 'turtle', 'n3', 'nt', 'pretty-xml', 'xml', 'json-ld'

    Raises
    ------
    TransformationError
        If the format is unsupported or serialization fails
    """
    # alias handling must happen before the supported-formats check
    aliases = {'rdf': 'xml', 'ttl': 'turtle', 'ntriples': 'nt'}
    output_format = aliases.get(output_format, output_format)

    supported_formats = ['turtle', 'n3', 'nt', 'pretty-xml', 'xml', 'json-ld']

    if output_format not in supported_formats:
        raise TransformationError(f"Unsupported output format: {output_format}. Supported: {supported_formats}")

    serialized = graph.serialize(format=output_format)

    if isinstance(serialized, bytes):
        output_stream.write(serialized.decode('utf-8'))
    else:
        output_stream.write(str(serialized))


def transform_metadata(input_data_file_path: Path, output_stream: io.IOBase, crosswalk_file_path: Path, output_format: str = 'turtle'):
    """Main function to perform transformation between different metadata standards.

    Parameters
    ----------
    input_data_file_path: pathlib.Path
        Source Metadata
    output_stream: io.IOBase
        Results are written here
    crosswalk_file_path: pathlib.Path
        Contains instructions to convert input to output
    output_format: str, optional
        The output format (default: 'turtle')
    """
    input_graph = ingest_file(input_data_file_path)

    output_graph = perform_crosswalk(input_graph, crosswalk_file_path)

    egress_graph(output_graph, output_stream, output_format)
    # TODO checking input data version against schema version in the crosswalk would be useful


if __name__ == '__main__':
    """Debug main for testing the transformation with SHACL crosswalk."""
    import sys
    import datetime

    def debug_transform(input_file: str = 'tests/test_data/transformation/datacite-example-full-v4.xml',
                        crosswalk_file: str = 'tests/test_data/transformation/datacite_4_7_to_oemetadata_2_0_4.ttl',
                        output_format: str = 'turtle',
                        output_file: str | None = None):
        """Execute a transformation and display debugging information.

        Parameters
        ----------
        input_file : str
            Path to input data file
        crosswalk_file : str
            Path to SHACL rules file
        output_format : str
            Output format (default: 'turtle')
        output_file : str, optional
            Path to save output. If None, prints to stdout and a timestamped file.
        """
        print("=" * 70)
        print("SHACL-BASED TRANSFORMATION DEBUG")
        print("=" * 70)

        input_path = Path(input_file)
        crosswalk_path = Path(crosswalk_file)

        # Validate files exist
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_path}")
            sys.exit(1)
        if not crosswalk_path.exists():
            print(f"ERROR: Crosswalk file not found: {crosswalk_path}")
            sys.exit(1)

        print(f"\nInput file: {input_path}")
        print(f"Crosswalk (SHACL rules): {crosswalk_path}")
        print(f"Output format: {output_format}")

        # Phase 1: Ingest
        print("\n[1] INGESTING INPUT...")
        try:
            input_graph = ingest_file(input_path)
            print(f"  ✓ Successfully ingested {input_path.name}")
            print(f"  ✓ Input graph has {len(input_graph)} triples")
        except Exception as e:
            print(f"  ✗ Ingest failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Phase 2: Crosswalk with SHACL
        print("\n[2] APPLYING SHACL CROSSWALK...")
        try:
            output_graph = perform_crosswalk(input_graph, crosswalk_path)
            print(f"  ✓ Crosswalk completed")
            print(f"  ✓ Derived graph has {len(output_graph)} triples")
        except Exception as e:
            print(f"  ✗ Crosswalk failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Phase 3: Egress
        print("\n[3] EGRESSING OUTPUT...")

        if output_file:
            out_path = Path(output_file)
        else:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            out_path = Path(f"output_{timestamp}.{output_format}")
        print(f"  Writing to: {out_path}")

        try:
            with open(out_path, 'w', encoding='utf-8') as out_stream:
                egress_graph(output_graph, out_stream, output_format)
            print(f"  ✓ Successfully wrote output")

            if not output_file:
                print("\n[OUTPUT PREVIEW]")
                print("-" * 40)
                content = out_path.read_text(encoding='utf-8')
                print(content[:1000])
                if len(content) > 1000:
                    print("...")
                print("-" * 40)
        except Exception as e:
            print(f"  ✗ Egress failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Summary
        print("\n" + "=" * 70)
        print("TRANSFORMATION COMPLETE")
        print("=" * 70)
        print(f"Input triples:   {len(input_graph)}")
        print(f"Derived triples: {len(output_graph)}")
        print(f"Output saved to: {out_path}")
        print("=" * 70)

    if len(sys.argv) > 1:
        args = sys.argv[1:]
        # debug_transform(
        #     input_file=args[0],
        #     crosswalk_file=args[1] if len(args) > 1 else 'src/omi/crosswalks/oemetadata_2-0-4_to_datacite_4_7_0.ttl',
        #     output_format=args[2] if len(args) > 2 else 'turtle',
        #     output_file=args[3] if len(args) > 3 else None,
        # )
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = Path(f"tests/test_data/output_{timestamp}.turtle")    
        with open(out_path, 'w', encoding='utf-8') as out_stream:
            test = transform_metadata(
                input_data_file_path=Path("tests/test_data/transformation/datacite-example-full-v4.xml"),
                crosswalk_file_path=Path("tests/test_data/transformation/datacite_4_7_to_oemetadata_2_0_4.ttl"),
                output_stream=out_stream
                )

    else:
        debug_transform()
