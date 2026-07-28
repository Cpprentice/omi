from rdflib import Graph
from pyshacl import shacl_rules
from omi.transformation import transform_metadata
from pathlib import Path
import datetime

def test_example_transformation():
    data_graph = Graph()
    data_graph.parse("omi/tests/test_data/transformation/input_example.linkml.ttl")

    rule_graph = Graph()
    rule_graph.parse("omi/src/omi/crosswalks/simple_example.ttl")

    output_graph = shacl_rules(data_graph, shacl_graph=rule_graph, advanced=True)
    print(output_graph.serialize(format="longturtle"))
    new_triples = output_graph.default_graph - data_graph
    new_triples.bind("exOut", "http://example.org/schemaOut#")
    new_data_turtle = new_triples.serialize(format="longturtle")
    print(new_data_turtle)



def test_oem2dcat_transformation():
    data_graph = Graph()
    data_graph.parse("omi/tests/test_data/transformation/oemetadata_v2-0-4.ttl")

    rule_graph = Graph()
    rule_graph.parse("omi/src/omi/crosswalks/oemetadata_2-0-4_to_dcat_3.ttl")

    output_graph = shacl_rules(data_graph, shacl_graph=rule_graph, advanced=True)
    print(output_graph.serialize(format="longturtle"))
    # new_triples = output_graph.default_graph - data_graph
    # new_triples.bind("exOut", "http://example.org/schemaOut#")
    #new_data_turtle = new_triples.serialize(format="longturtle")
    #print(new_data_turtle)
    #new_triples_path = Path("tests/test_data/transformation/new_triples.ttl")
    #new_triples.serialize(destination=str(new_triples_path.absolute()), format="longturtle")
    output_graph_path = Path("tests/test_data/transformation/full_graph.ttl")
    output_graph.serialize(destination=str(output_graph_path.absolute()), format="longturtle")


def test_xml_oem2dcat_transformation():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(f"tests/test_data/output_{timestamp}.jsonld")    
    with open(out_path, 'w', encoding='utf-8') as out_stream:
        test = transform_metadata(
            input_data_file_path=Path("tests/test_data/transformation/datacite-example-full-v4.xml").absolute(),
            crosswalk_file_path=Path("src/omi/crosswalks/datacite_4_7_to_oemetadata_2_0_4.ttl").absolute(),
            output_stream=out_stream,
            output_format="json-ld"
            )

