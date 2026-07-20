"""# SHACL Transformation Patterns: Metadata Interoperability

This document outlines standardized patterns for mapping metadata schemas using SHACL-based transformation rules. These patterns address common challenges in achieving data interoperability between domain-specific vocabularies and broader standards like DCAT.

## The 'Target Class' Problem

In RDF-based metadata mapping, a fundamental challenge arises when the source schema and the target schema define entity boundaries differently. 

The **'Target Class' Problem** refers to the requirement of defining the scope of a transformation rule. When using SHACL for inference or transformation (e.g., using `sh:nodeShape` to define rules), we must determine:
1.  **Which entities** are subject to the transformation (the `sh:targetClass`).
2.  **How to handle** entities that might exist in the source dataset but do not have an explicit class definition matching the expected source `sh:targetClass`.

If the source graph is loosely typed or relies on implicit property-based typing, using `sh:targetClass` might fail to capture all intended instances. Conversely, over-broad targets lead to computational overhead and potential "collisions" where properties are incorrectly mapped to entities that share the same class but exist in different contexts.

---

## Pattern 1: Property-to-Property Mapping (Simple)

This pattern represents the simplest form of transformation: a direct mapping of a literal value from a source property in `oemetadata` to a target property in `dcat`.

### Description
We want to map the title field of a dataset entry defined in the `oemetadata` schema to the `dcterms:title` field within the `dcat:Record` (or `dcat:Dataset`) structure. This does not involve structural changes, only the projection of a value from a specific property path to a new predicate.

### SHACL Transformation Rule

```turtle
@prefix sh: [http://www.w3.org/ns/shacl#](http://www.w3.org/ns/shacl#) .
@prefix dcterms: [http://purl.org/dc/terms/](http://purl.org/dc/terms/) .
@prefix oemetadata: [https://github.com/OpenEnergyPlatform/oemetadata/blob/develop/oemetadata/v2/v20/context.json] .
@prefix dcat: [http://www.w3.org/ns/dcat#](http://www.w3.org/ns/dcat#) .

# Pattern: Direct Property Mapping
# This shape assumes the subject is an instance of an Oemetadata Dataset
ex:TopElementToDatasetRule
    a sh:NodeShape ;
    sh:targetSubjectsOf owl:versionInfo ;
    sh:rule [
        a sh:SPARQLRule ;
        sh:construct """
            PREFIX dac4: <http://datacite.org/schema/kernel-4#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            CONSTRUCT {
                $this a dcat:Dataset ;
                $this dct:title ?title .
            }
            WHERE {
                $this owl:versionInfo ?_ ;
                $this  dct:title ?title .
            }
        """ ;
    ] .