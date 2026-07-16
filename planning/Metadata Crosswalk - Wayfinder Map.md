# Metadata Crosswalk — Wayfinder Map (overview)

Hackathon effort, started 2026-07-16. The canonical map and tickets live in the OMI repo at `.scratch/metadata-crosswalk/` (map.md + issues/). This note is the human-readable overview; research summaries, crosswalk drafts, and decision records produced by the tickets will land in this Obsidian folder.

Diagrams of the architecture and data flow: [[Visualization - Crosswalk architecture and data flow]]. Pipeline spec: [[Design - RDF crosswalk pipeline]].

## Destination

A locked architecture decision — **RDF-pivot vs direct pairwise mappings** — plus documented, field-level, **bidirectional** crosswalk specs between **OEMetadata (v2.0 and following)** and **DataCite, DCAT-AP, and schema.org**, with information loss explicitly documented per field and direction. Ready to implement in OMI afterwards (implementation itself is a follow-up effort).

## Ground rules decided at charting

- Fidelity: best-effort with loss documented — every crosswalk records exactly which fields drop or approximate, per direction.
- Priority order: DataCite → DCAT-AP → schema.org.
- Crosswalks anchor to OEMetadata v2.0+; legacy records upgrade via OMI's existing version conversion first.
- Documents → this folder; code/spikes → a branch in the OMI repo (from `dev`).

## Decisions so far

- **Ticket 01 — Survey existing crosswalks between DataCite, DCAT-AP, and schema.org** — resolved 2026-07-16, full report: [[Research - Existing crosswalks DataCite DCAT-AP schema.org]]. Versions pinned (DataCite 4.7, DCAT-AP 3.0.1, DCAT 3, schema.org v30.0). All three pairwise edges have existing artifacts (W3C DCAT 3 Annex B, JRC CiteDCAT-AP, DataCite bolognese). Hub-and-spoke with DCAT-AP as hub is mostly viable: one serious DCAT-AP mapping + one thin OEMetadata→DataCite mapping; schema.org derivable nearly free. No DCAT-AP→DataCite crosswalk exists anywhere.
- **Ticket 07 — Decide: RDF-pivot or direct pairwise mappings** — resolved 2026-07-16, decided by the team: **RDF-first pivot with SHACL** (shapes validate, SHACL rules drive derivations). Pipeline spec: [[Design - RDF crosswalk pipeline]] — detect format → JSON→JSON-LD → rdflib graph → SHACL-rules crosswalk → serialize. Runtime loss logging is future work.

## Tickets

Takeable now (frontier):

- **Ticket 02 — Field inventory of OEMetadata v2** (research) — full field surface, classified, with loss candidates flagged; starts from the existing first-party mappings table.
- **Ticket 03 — Who are the consumers, and what do they minimally require?** (grilling, with the team) — DOI registration, portal harvesting, Google Dataset Search, reverse ingest — priorities and mandatory fields.

Blocked, in dependency order:

- **Ticket 04 — Crosswalk spec template + loss-documentation convention** (grilling) — blocked by 02, 03. Covers the human-readable docs; the machine-readable side is settled (SHACL rules).
- **Ticket 05 — OEMetadata → DataCite 4.7 thin export mapping** (research) — blocked by 01, 02, 04. Dedicated egress from the pivot graph; DataCite is not RDF-native.
- **Ticket 06 — Spike: OEMetadata as RDF — de-risk the SHACL pipeline** (prototype) — blocked by 02. JSON-LD context + sample SHACL rules to DCAT-AP + pySHACL SHACL-AF check.
- **Ticket 08 — Draft the OEMetadata ↔ DCAT-AP 3.0.1 crosswalk** (research) — upgrade of the first-party table, as JSON-LD context + SHACL rules; blocked by 04, 06.
- **Ticket 09 — Validate deriving schema.org via W3C DCAT 3 Annex B** (research) — blocked by 08.

## Fog (in scope, not yet ticketable)

Reverse-direction synthesis rules for imports into OEMetadata, validation of non-RDF outputs (DataCite export, schema.org JSON-LD), and the long-term home + versioning of the spec.

## Out of scope

Implementing production converters in OMI; operating publication pipelines (DOI minting, portal registration, embedding JSON-LD in OEP pages); runtime loss logging during transformations (declared future work by the team, 2026-07-16 — specs document expected loss statically).
