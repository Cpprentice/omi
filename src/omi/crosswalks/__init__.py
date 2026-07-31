from pathlib import Path

from rdflib import Graph


def get_path(crosswalk_name) -> Path:
    return Path(__file__).with_name(f'{crosswalk_name}.ttl')


def get_graph(crosswalk_name) -> Graph:
    crosswalk_path = get_path(crosswalk_name)
    g = Graph()
    g.parse(source=crosswalk_path, format='turtle')
    return g
