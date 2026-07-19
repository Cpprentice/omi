# Overview

- planning/Visualization - Crosswalk architecture and data flow.md

# Status Quo
- Pipeline to run tranformations
    - Supporting several input formats
    - Reading into RDF
    - Apply SPARQL Rules
    - Write to Output / Supporting ttl and json-ld fomrats
- A XML "walker" for xml file ingest into RDF - supports DataCite
- SPARQL Rules / Crosswalk
    - Test for DataCite to OEMetadata (Full)
    - Test OEMetadata to DataCite (Partial)
- Tests & Test Metadata for everything included in the repo

## Main files & directories we added 
- planning
- src/omi/crosswalks
- src/omi/transformation.py
- tests/test_data/transformation
- tests/test_xml_ingest.py
- tests/test_transformation.py



# Open Todos for the Metadata Transformation
- [ ] Check if we have to provide all transformations or can use existing ones
- [ ] Check via roundtrips for which metadata schema nesting information gets lost during transformation (e.g. datacite xml-> ingest to rdflib -> Output as xml)
- [ ] Implement checking for identified metadata from above todo
- [ ] Enable the reconstruction of nesting information either through templates and queries per item or LinkML
- [ ] Enable the output of the graph diff as additional information (old graph - new graph)
