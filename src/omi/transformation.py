"""Transformation Module for OMI to convert to and from OEMetadata"""


import io
from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.plugin import plugins, Parser, Serializer
from typing import Optional, Union
import json
from pyshacl import validate, shacl_rules

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
        The detected format (e.g., 'json', 'xml', 'turtle', 'n3', 'nt', 'rdfa', 'jsonld')
        
    Raises
    ------
    TransformationError
        If the file format cannot be detected or is not supported
    """
    suffix = input_data_file_path.suffix.lower()
    
    format_map = {
        '.json': 'json',
        '.jsonld': 'json-ld',
        '.xml': 'xml',
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

def _transform_json_to_jsonld(input_data: dict) -> dict:
    """Transform plain JSON to JSON-LD format for rdflib consumption.
    
    This is a basic transformation that wraps the input in a JSON-LD structure.
    For more complex transformations, additional context mapping would be needed.
    
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
    
    jsonld_data = {
        '@context': {},
        **input_data
    }
    return jsonld_data


def ingest_file(input_data_file_path: Path) -> Graph:
    """Ingest data from a file into an rdflib Graph.
    
    Handles various input formats including JSON (transformed to JSON-LD),
    JSON-LD, XML/RDF, Turtle, N-Triples, etc.
    
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
    else:
        graph.parse(str(input_data_file_path), format=file_format)
    
    return graph


def perform_crosswalk(input_graph: Graph, crosswalk_file_path: Path) -> Graph:
    """Perform the crosswalk transformation on the input graph using SHACL rules.
    
    Applies SHACL validation and inference to transform the input graph
    according to the rules defined in the crosswalk file.
    
    Parameters
    ----------
    input_graph : Graph
        The input rdflib Graph to transform
    crosswalk_file_path : Path
        Path to the SHACL rules file (expected in Turtle format)
        
    Returns
    -------
    Graph
        The transformed rdflib Graph after applying SHACL rules
    """
    HERE = Path(__file__).parent
    DCK = Namespace("https://schema.datacite.org/meta/kernel-4/#")

    # Apply SHACL rules to transform the input graph
    # Load the SHACL rules from the crosswalk file
    rules_graph = Graph()
    rules_graph.parse(str(crosswalk_file_path), format='turtle')
    
    # Apply SHACL validation with inference
    
    output_graph = shacl_rules(input_graph, shacl_graph=rules_graph, advanced=True, inplace=False)
    
    # 3. Thin egress: DataCite is not RDF-native, so serialize the staged
    #    dck: terms into a real DataCite REST payload (mandatory kernel field).
    titles = sorted(str(o) for s, o in output_graph.subject_objects(DCK.title))
    
    derived = Graph()
    for triple in output_graph.triples((None, None, None)):
        if triple not in input_graph:
            derived.add(triple)
    derived.bind("dck", DCK)
    
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
    supported_formats = ['turtle', 'n3', 'nt', 'pretty-xml', 'xml', 'json-ld', 'ntriples']
    
    if output_format not in supported_formats:
        raise TransformationError(f"Unsupported output format: {output_format}. Supported: {supported_formats}")
    
    if output_format == 'rdf':
        output_format = 'xml'
    elif output_format == 'ttl':
        output_format = 'turtle'
    
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
    # from oemetadata.v2.v20.example import OEMETADATA_V20_EXAMPLE

    ## CPPrentice testing
    _g = ingest_file(Path('tests/test_data/transformation/oemetadata_v2-0-4.jsonld'))
    print(_g.serialize(format="longturtle"))
    _ = 42
    ## CPPRentice testing end
    
    def debug_transform(input_file: str = 'tests/test_data/transformation/oemetadata_v2-0-4.jsonld',
                        crosswalk_file: str = 'src/omi/crosswalks/oemetadata_2-0-4_to_datacite_4_6_0.ttl',
                        output_format: str = 'turtle',
                        output_file: str = None):
        """Execute a transformation and display debugging information.
        
        Parameters
        ----------
        input_file : str
            Path to input data file (default: testing_mapping_input_valid_jsonld.jsonld)
        crosswalk_file : str
            Path to SHACL rules file (default: shacl_rules.ttl)
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
            print(f"  ✓ Output graph has {len(output_graph)} triples")
            
            # Display SHACL validation results if available
            if hasattr(output_graph, 'conforms'):
                print(f"  SHACL Validation: {'CONFORMS' if output_graph.conforms else 'DOES NOT CONFORM'}")
            if hasattr(output_graph, 'validation_text') and output_graph.validation_text:
                print(f"  Validation report: {output_graph.validation_text[:200]}")
        except Exception as e:
            print(f"  ✗ Crosswalk failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Phase 3: Egress
        print("\n[3] EGRESSING OUTPUT...")
        
        # Determine output destination
        if output_file:
            out_path = Path(output_file)
            print(f"  Writing to: {out_path}")
            out_stream = open(out_path, 'w', encoding='utf-8')
        else:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            out_path = Path(f"output_{timestamp}.{output_format}")
            print(f"  Writing to: {out_path} (and stdout)")
            out_stream = open(out_path, 'w', encoding='utf-8')
        
        try:
            egress_graph(output_graph, out_stream, output_format)
            out_stream.close()
            print(f"  ✓ Successfully wrote output")
            
            # Also print to stdout for quick inspection
            if not output_file:
                print("\n[OUTPUT PREVIEW]")
                print("-" * 40)
                with open(out_path, 'r') as f:
                    content = f.read()
                    print(content[:1000])  # First 1000 chars
                    if len(content) > 1000:
                        print("...")
                    print("-" * 40)
        except Exception as e:
            print(f"  ✗ Egress failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            if not output_file and 'out_stream' in locals():
                out_stream.close()
        
        # Summary
        print("\n" + "=" * 70)
        print("TRANSFORMATION COMPLETE")
        print("=" * 70)
        print(f"Input triples:  {len(input_graph)}")
        print(f"Output triples: {len(output_graph)}")
        print(f"Output saved to: {out_path}")
        print("=" * 70)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        # Custom arguments
        args = sys.argv[1:]
        input_file = args[0] if len(args) > 0 else None
        crosswalk = args[1] if len(args) > 1 else None
        out_fmt = args[2] if len(args) > 2 else None
        out_file = args[3] if len(args) > 3 else None
        
        debug_transform(
            input_file=input_file if input_file else 'testing_mapping_input_valid_jsonld.jsonld',
            crosswalk_file=crosswalk if crosswalk else 'shacl_rules.ttl',
            output_format=out_fmt if out_fmt else 'turtle',
            output_file=out_file
        )
    else:
        # Default: use the specified files
        debug_transform()
        