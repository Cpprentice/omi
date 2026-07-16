from rdflib import Graph
from pyshacl import shacl_rules

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
