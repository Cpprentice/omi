"""Tests for the SHACL crosswalk transformations in omi.transformation."""

import datetime
import json
from pathlib import Path
from typing import cast

from pyshacl import shacl_rules
from rdflib import Dataset, Graph, URIRef

import omi.crosswalks
from omi.transformation import perform_crosswalk, transform_metadata

TEST_DATA_DIR = Path(__file__).parent / "test_data" / "transformation"
CROSSWALKS_DIR = Path(__file__).parents[1] / "src" / "omi" / "crosswalks"

def test_example_transformation():
    data_graph = Graph()
    data_graph.parse(TEST_DATA_DIR / "input_example.linkml.ttl")

    rule_graph = Graph()
    rule_graph.parse(CROSSWALKS_DIR / "simple_example.ttl")

    output_graph = cast("Dataset", shacl_rules(data_graph, shacl_graph=rule_graph, advanced=True))
    print(output_graph.serialize(format="longturtle"))
    new_triples = output_graph.default_graph - data_graph
    new_triples.bind("exOut", "http://example.org/schemaOut#")
    new_data_turtle = new_triples.serialize(format="longturtle")
    print(new_data_turtle)



def test_oem2dcat_transformation():
    data_graph = Graph()
    data_graph.parse(TEST_DATA_DIR / "oemetadata_v2-0-4.ttl")

    rule_graph = Graph()
    rule_graph.parse(CROSSWALKS_DIR / "oemetadata_2-0-4_to_dcat_3.ttl")

    output_graph = cast("Dataset", shacl_rules(data_graph, shacl_graph=rule_graph, advanced=True))
    print(output_graph.serialize(format="longturtle"))
    # new_triples = output_graph.default_graph - data_graph
    # new_triples.bind("exOut", "http://example.org/schemaOut#")
    #new_data_turtle = new_triples.serialize(format="longturtle")
    #print(new_data_turtle)
    #new_triples_path = Path("tests/test_data/transformation/new_triples.ttl")
    #new_triples.serialize(destination=str(new_triples_path.absolute()), format="longturtle")
    output_graph_path = TEST_DATA_DIR / "full_graph.ttl"
    output_graph.serialize(destination=str(output_graph_path), format="longturtle")


def test_xml_oem2datacite_transformation():
    timestamp = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = TEST_DATA_DIR.parent / f"output_{timestamp}.jsonld"
    with out_path.open("w", encoding="utf-8") as out_stream:
        transform_metadata(
            input_data_file_path=TEST_DATA_DIR / "datacite-example-full-v4.xml",
            crosswalk_file_path=CROSSWALKS_DIR / "datacite_4_7_to_oemetadata_2_0_4.ttl",
            output_stream=out_stream,
            output_format="json-ld",
        )


def _inject_local_oemetadata_context(descriptor: dict) -> None:
    context_file = Path(__file__).parent / "test_data" / "transformation" / "context.json"
    context = json.loads(context_file.read_text(encoding="utf-8"))
    descriptor["@context"] = context


def _load_result_graph(conversion: str) -> Graph:
    result_path = Path(__file__).parent / "test_data" / "transformation" / conversion / f"{conversion}.ttl"
    result_graph = Graph()
    result_graph.parse(source=result_path, format="turtle")
    return result_graph


def test_oem_to_dcat_transformation():
    input_dataset_file = Path(__file__).parent / "test_data" / "transformation" / "oem-to-dcat" / "oem-original.json"
    descriptor = json.loads(input_dataset_file.read_text(encoding="utf-8"))
    _inject_local_oemetadata_context(descriptor)

    input_dataset = Dataset()
    named_graph_uri = URIRef("https://example.com/ResultGraph")
    input_graph = input_dataset.graph(named_graph_uri)
    input_graph.parse(data=descriptor, format="json-ld")

    input_graph.serialize(destination=input_dataset_file.with_name("oem-original.ttl"), format="longturtle")

    _test_data = list(input_graph.query("""
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?parent ?this ?title ?description ?rel
    WHERE {
        ?parent dcat:dataset $this .
        $this dcterms:title ?title ;
            dcterms:description ?description .
        BIND(BNODE() AS ?rel) .
    }
"""))

    _test_data2 = list(input_graph.query("""
    PREFIX oeo: <https://openenergyplatform.org/ontology/oeo/>
    PREFIX dcterms: <http://purl.org/dc/terms/>

    SELECT ?creator ?parent $this
    WHERE {
        ?parent dcterms:contributor $this .
        $this oeo:RO_0000087 ?role .
        FILTER(?role = "DataCollector")
        BIND($this AS ?creator)
    }
"""))


    result_graph = perform_crosswalk(input_dataset, omi.crosswalks.get_path("oemetadata_2-0-4_to_dcat_3"))
    # result_graph = shacl_rules(
    #     input_dataset,
    #     shacl_graph=omi.crosswalks.get_graph('oemetadata_2-0-4_to_dcat_3'),
    #     advanced=True,
    #     inplace=False,
    #     debug=True,
    #     # target_graph_identifier=named_graph_uri
    # )

    # result_graph.bind('dcat1', 'http://www.w3.org/ns/dcat#')
    # result_graph.bind('dcterms1', 'http://purl.org/dc/terms/')

    result_graph.serialize(destination=input_dataset_file.with_name("oem-to-dcat-transformed.ttl"), format="longturtle")
    expected_graph = _load_result_graph("oem-to-dcat")
    _diff = expected_graph - result_graph


if __name__ == "__main__":
    test_oem_to_dcat_transformation()

