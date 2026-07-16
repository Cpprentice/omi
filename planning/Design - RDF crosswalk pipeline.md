# Design — RDF crosswalk pipeline

Captured 2026-07-16 from the hackathon team's specification, following the architecture decision (RDF-first with SHACL shapes + SHACL rules; see [[Metadata Crosswalk - Wayfinder Map]]).

## Process

```text
Get input data → ingest into rdflib graph → perform crosswalk → egress as RDF → output as file
```

## Needed functions

1. **Detect input file format** — sniff whether the input is OEMetadata JSON, JSON-LD, Turtle, RDF/XML, DataCite XML/JSON, etc.
2. **Transform input format into a format usable by rdflib** — see the [rdflib parser plugins](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.parsers/#rdflib.plugins.parsers). Notably: plain **JSON → JSON-LD**. Team decision (2026-07-16): reuse the **existing OEMetadata `@context`** — v2 records already carry an `@context` field, so OEMetadata is JSON-LD out of the box; the pivot expression builds on that context rather than a new one. (Open: verify the shipped context's coverage — do all crosswalk-relevant fields resolve to IRIs?)
3. **Create graph from input** — parse into an `rdflib.Graph`.
4. **Perform crosswalk** — the mapping is expressed as **SHACL rules** (SHACL-AF) executed over the graph; SHACL shapes validate before/after.
5. **Output in specified format** — serialize the derived graph (Turtle, JSON-LD, RDF/XML …); non-RDF targets (DataCite JSON/XML for DOI registration) need a dedicated egress step.

## Open points feeding back into the map

- The **JSON-LD context for OEMetadata v2** is the load-bearing artifact of step 2 — designed/de-risked in the RDF spike ticket, specified fully in the DCAT-AP crosswalk ticket.
- **SHACL rules engine**: verify pySHACL's SHACL-AF rule support (or alternatives) actually covers what the crosswalk needs — part of the spike.
- **Runtime loss logging** during the crosswalk step is future work (team decision, 2026-07-16); specs document expected loss statically.

## Status

Working design from the hackathon; feeds the spike (ticket 06), spec template (ticket 04), and DCAT-AP crosswalk (ticket 08).
