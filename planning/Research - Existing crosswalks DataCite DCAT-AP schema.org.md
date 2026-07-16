# Existing crosswalks between DataCite, DCAT-AP and schema.org

**Research date: 2026-07-16.** Prepared for the OEMetadata crosswalk hackathon effort. All claims cite primary sources (specs, standards bodies' repos, first-party docs).

## TL;DR

- All three pairwise links between the targets are already covered by official or first-party artifacts, though with varying freshness and direction:
  - **DCAT ↔ schema.org**: covered *inside the W3C DCAT 3 Recommendation itself* (non-normative Annex B, with a machine-readable RDF/OWL alignment file) ([W3C](https://www.w3.org/TR/vocab-dcat-3/#dcat-sdo)), plus a JRC **DCAT-AP → schema.org** mapping implemented as SPARQL CONSTRUCT queries ([ec-jrc](https://ec-jrc.github.io/dcat-ap-to-schema-org/)).
  - **DataCite → DCAT-AP**: covered by the EC Joint Research Centre's **CiteDCAT-AP** (XSLT, EUPL-1.2) ([ec-jrc](https://ec-jrc.github.io/datacite-to-dcat-ap/)) — but pinned to DataCite 4.4 / DCAT-AP 2.0.1 and one-directional.
  - **DataCite ↔ schema.org**: covered operationally by DataCite itself — DOI content negotiation returns schema.org JSON-LD ([DataCite support](https://support.datacite.org/docs/datacite-content-resolver)), implemented in the actively maintained MIT-licensed **bolognese** library ([datacite/bolognese](https://github.com/datacite/bolognese)).
- **Hub-and-spoke verdict**: mostly yes, with one caveat. OEMetadata already maintains a ~117-row first-party mapping to Dublin Core / DCAT / DCAT-AP.de / Frictionless / FOAF ([OEMetadata mappings](https://openenergyplatform.github.io/oemetadata/latest/oemetadata/metadata_mappings/)). Upgrading that one spoke (to DCAT-AP 3.0.1, machine-readable) buys the schema.org leg almost for free via the W3C Annex B alignment. The **DataCite leg is the exception**: no maintained DCAT-AP → DataCite crosswalk exists in that direction (CiteDCAT-AP only goes DataCite → DCAT-AP), so a thin direct OEMetadata → DataCite mapping is still needed if OEMetadata records must be exported for DOI registration. Net: **one serious mapping (DCAT-AP) + one thin mapping (DataCite), zero for schema.org.**

## Pinned versions as of 2026-07-16

| Standard | Current version | Date | Source |
|---|---|---|---|
| DataCite Metadata Schema | **4.7** | released 3 Mar 2026 | [schema.datacite.org](https://schema.datacite.org), [readthedocs (4.7)](https://datacite-metadata-schema.readthedocs.io/) |
| DCAT-AP (SEMIC) | **3.0.1** (recommendation); 3.0.2 draft in development | 3.0.1 published 4 Jun 2026 | [semiceu.github.io/DCAT-AP](https://semiceu.github.io/DCAT-AP/), [SEMICeu/DCAT-AP releases](https://github.com/SEMICeu/DCAT-AP/releases) |
| DCAT-AP HVD | 3.0.0 (recommendation); 3.0.1 draft, public review open until Sep 2026 | — | [semiceu.github.io/DCAT-AP](https://semiceu.github.io/DCAT-AP/) |
| W3C DCAT | **DCAT 3**, W3C Recommendation | 22 Aug 2024 | [w3.org/TR/vocab-dcat-3](https://www.w3.org/TR/vocab-dcat-3/) |
| schema.org | **v30.0** | 19 Mar 2026 | [schema.org releases](https://schema.org/docs/releases.html) |
| Google Dataset Search guidance | accepts schema.org `Dataset` **or** "equivalent structures represented in W3C's DCAT"; CSVW support experimental; required properties: `name`, `description` | current | [developers.google.com](https://developers.google.com/search/docs/appearance/structured-data/dataset) |

Note on DCAT-AP.de (targeted by OEMetadata's existing table): a German national profile of DCAT-AP; the OEMetadata table links DCAT-AP.de IRIs, which lag the SEMIC 3.0.1 baseline (see OEMetadata section below).

## 1. JRC CiteDCAT-AP — DataCite → DCAT-AP

- **What**: "the DataCite profile of DCAT-AP" — a full mapping of DataCite records into DCAT-AP RDF, in two profiles: a **core profile** (only what plain DCAT-AP can express) and an **extended profile** (all DataCite elements, using additional vocabularies) ([spec](https://ec-jrc.github.io/datacite-to-dcat-ap/), [repo](https://github.com/ec-jrc/datacite-to-dcat-ap)).
- **Versions**: maps **DataCite 4.4** (backward-compatible with earlier 4.x/3.x) to **DCAT-AP 2.0.1**, aligned with DCAT 2, GeoDCAT-AP 2.0.0 and StatDCAT-AP 1.0.1 ([spec](https://ec-jrc.github.io/datacite-to-dcat-ap/)). Three DataCite minor versions and one DCAT-AP major version behind current.
- **Tooling**: executable — the repo is ~93% **XSLT**, plus an OAI-PMH proxy proof of concept under `api/` ([repo](https://github.com/ec-jrc/datacite-to-dcat-ap)). Machine-actionable.
- **Maintenance**: maintained by JRC Units B.6 & G.I.4; last push 13 Feb 2025 (GitHub API); the spec labels itself a draft that "must be considered as unstable" ([spec](https://ec-jrc.github.io/datacite-to-dcat-ap/)).
- **License**: **EUPL-1.2** ([repo](https://github.com/ec-jrc/datacite-to-dcat-ap)).
- **Direction**: DataCite → DCAT-AP only. No reverse (DCAT-AP → DataCite) artifact exists here or anywhere else found in this research.
- **Reusability verdict**: the reference semantic mapping for the DataCite↔DCAT-AP pair; directly reusable for *importing* DataCite records, and the best available field-correspondence table to crib from when authoring an OEMetadata→DataCite export. Needs a version-gap review (4.4→4.7 added/changed properties; DCAT-AP 2→3 changes).

## 2. JRC DCAT-AP → schema.org

- **What**: JRC mapping of DCAT-AP terms to schema.org "to enhance their discoverability on the Web", one SPARQL CONSTRUCT query per DCAT-AP class ([spec](https://ec-jrc.github.io/dcat-ap-to-schema-org/), [repo](https://github.com/ec-jrc/dcat-ap-to-schema-org)).
- **Versions**: **DCAT-AP 2.0.1 → schema.org 12.0**, plus GeoDCAT-AP 2.0.0 and StatDCAT-AP 1.0.1 ([spec](https://ec-jrc.github.io/dcat-ap-to-schema-org/)).
- **Tooling**: executable — **SPARQL CONSTRUCT** queries, modular per class ([spec](https://ec-jrc.github.io/dcat-ap-to-schema-org/)). Machine-actionable.
- **Maintenance**: draft, "must be considered as unstable"; **stale** — last push 20 Oct 2022 (GitHub API). Intentionally partial: qualified relations and pending schema.org terms excluded, many entries marked TBD (categories, rights, versioning, provenance, quality, checksums) ([spec](https://ec-jrc.github.io/dcat-ap-to-schema-org/)).
- **License**: repo **EUPL-1.2** (GitHub API); documentation **CC BY 4.0** ([spec](https://ec-jrc.github.io/dcat-ap-to-schema-org/)).
- **Reusability verdict**: useful as a worked SPARQL implementation pattern, but superseded in authority by the W3C DCAT 3 Annex B (below) and stale on both ends. Reuse the approach, verify each mapping against Annex B.

## 3. W3C DCAT 3 Annex B — DCAT ↔ schema.org (the strongest link)

- **What**: the DCAT 3 Recommendation contains a dedicated (non-normative) appendix, "B. Alignment with Schema.org", with a class/property mapping table (dcat:Dataset→sdo:Dataset, dcat:Distribution→sdo:DataDownload, dcat:Catalog→sdo:DataCatalog, dcat:DataService→sdo:WebAPI, dcterms:title→sdo:name, etc.) ([W3C](https://www.w3.org/TR/vocab-dcat-3/#dcat-sdo)).
- **Machine-readable**: yes — "A recommended mapping from the revised DCAT (this document) to [SCHEMA-ORG] version 3.4 is available in an RDF file", axiomatized with `rdfs:subClassOf`, `rdfs:subPropertyOf`, `owl:equivalentClass`, `owl:equivalentProperty`, `skos:closeMatch`, plus `sdo:domainIncludes`/`sdo:rangeIncludes` ([W3C](https://www.w3.org/TR/vocab-dcat-3/#dcat-sdo)); the file is live at [w3c.github.io/dxwg/dcat/rdf/dcat-schema.ttl](https://w3c.github.io/dxwg/dcat/rdf/dcat-schema.ttl) (verified 2026-07-16: Turtle, imports schema.org and dcat, e.g. `dct:description owl:equivalentProperty schema:description`).
- **Versions**: DCAT 3 vs schema.org **3.4** — the schema.org side is old (current is 30.0), but the mapped core terms are long-stable.
- **Maintenance/license**: part of a W3C Recommendation maintained by the Dataset Exchange Working Group ([w3c/dxwg](https://github.com/w3c/dxwg)); W3C document/software licenses.
- **Direction**: expressed as OWL axioms (equivalences/subsumptions), so it is a *semantic* alignment usable in both directions, not a lossy one-way transform.
- **Reusability verdict**: the anchor artifact. Because schema.org itself derived its Dataset vocabulary from DCAT and Google Dataset Search consumes *both* schema.org and DCAT ([W3C](https://www.w3.org/TR/vocab-dcat-3/#dcat-sdo), [Google](https://developers.google.com/search/docs/appearance/structured-data/dataset)), the DCAT↔schema.org edge is the best-covered edge in the triangle. Reuse as-is.

## 4. Science-on-schema.org (ESIPFed)

- **What**: community conventions for publishing schema.org JSON-LD for scientific `Dataset` landing pages and repositories — a *profile/guidance* for schema.org use, not a crosswalk between standards ([repo](https://github.com/ESIPFed/science-on-schema.org)).
- **Version**: v1.3.2, 9 Jul 2024, archived on Zenodo (DOI 10.5281/zenodo.7884538) ([repo](https://github.com/ESIPFed/science-on-schema.org)).
- **Maintenance**: active — last push 22 Jan 2026 (GitHub API), monthly ESIP community meetings ([repo](https://github.com/ESIPFed/science-on-schema.org)).
- **License**: **Apache-2.0** (GitHub API).
- **Reusability verdict**: not a mapping to reuse, but the target profile to *conform to* if OEMetadata ever emits schema.org JSON-LD — it answers "which schema.org properties, in what shape" for research data, complementing Google's minimal requirements.

## 5. DataCite's own documented crosswalks

- **Official mapping suite (schema docs 4.7)**: the DataCite Metadata Schema documentation "Mappings" section covers **Dublin Core**, **Dublin Core Qualified**, a **Dublin Core local extension**, **FORCE11 Software Citation Principles**, and **PIDINST** — prose tables only; **no schema.org and no DCAT mapping is published there** ([readthedocs 4.7 mappings](https://datacite-metadata-schema.readthedocs.io/en/4.7/mappings/), [DC mapping 4.6](https://datacite-metadata-schema.readthedocs.io/en/4.6/mappings/dublincore/)).
- **DataCite → schema.org (operational)**: DOI content negotiation serves **schema.org JSON-LD** (`application/ld+json`) among its supported types (also RDF/XML, Turtle, Citeproc, Codemeta, BibTeX, RIS, JATS, DataCite XML/JSON); **DCAT and Dublin Core are not offered** ([content resolver docs](https://support.datacite.org/docs/datacite-content-resolver)).
- **bolognese**: DataCite's MIT-licensed Ruby gem implementing these conversions — reads and writes DataCite XML/JSON, schema.org JSON-LD, Citeproc, Codemeta, BibTeX, RIS; reads Crossref XML, RDF; actively maintained (v2.7.0, May 2026; last push 11 Jul 2026 per GitHub API) ([datacite/bolognese](https://github.com/datacite/bolognese)). Executable, bidirectional for DataCite↔schema.org.
- **OpenAIRE Guidelines for Data Archives**: an application profile *of* DataCite (not a crosswalk to DCAT/schema.org); v3 harmonized with DataCite schema 4.3 ([guidelines.openaire.eu](https://guidelines.openaire.eu/en/latest/data/index.html), [openaire/guidelines-data-archives](https://github.com/openaire/guidelines-data-archives)).
- **DataCite on DCAT**: nothing first-party found — the JRC CiteDCAT-AP (Section 1) is the de-facto reference for that pair.
- **Reusability verdict**: for the DataCite↔schema.org edge, prefer bolognese's mapping logic (first-party, executable, maintained) over writing anything new; the Dublin Core tables are a useful sanity-check vocabulary bridge since OEMetadata's own table already maps to DC.

## 6. OEMetadata's existing first-party mapping table

- **What**: OEMetadata already publishes a **~117-row field-level mapping table** from OEMetadata keys to **Dublin Core (dc/dcterms)**, **DCAT / DCAT-AP.de** (with DCAT-AP.de IRI links), **Frictionless Datapackage**, **FOAF**, plus **vCard** and location/temporal terms (locn, time, dcterms:Location, dcterms:PeriodOfTime); each row carries the OEMetadata badge level (Iron→Platinum) and a necessity level (mandatory/recommended/optional) ([OEMetadata mappings](https://openenergyplatform.github.io/oemetadata/latest/oemetadata/metadata_mappings/)).
- **Gaps**: **DataCite and schema.org do not appear** in the table; the DCAT column targets the German profile **DCAT-AP.de**, not SEMIC DCAT-AP 3.0.1; the table is an HTML/prose table, **not machine-actionable** ([OEMetadata mappings](https://openenergyplatform.github.io/oemetadata/latest/oemetadata/metadata_mappings/)).
- **Significance**: the OEMetadata→DCAT-AP spoke is already partially built first-party. Since DCAT-AP.de is a profile of DCAT-AP, most rows should carry over to DCAT-AP 3.0.1 with a delta review rather than a rewrite. The Frictionless column is also notable: given no official Frictionless↔DCAT mapping exists (Section 7), this table is itself one of the more complete Frictionless-to-DCAT alignments available.

## 7. Other reusable connectors (noted, not deep-dived)

- **Frictionless Data Package ↔ DCAT**: no official mapping in the Frictionless specs ([specs.frictionlessdata.io](https://specs.frictionlessdata.io/)); an open discussion issue ([frictionlessdata/project#551](https://github.com/frictionlessdata/project/issues/551)) and a community repo ([OSUKED/Frictionless-Data-to-DCAT](https://github.com/OSUKED/Frictionless-Data-to-DCAT)). Relevant because OEMetadata v2 is tabular-data-package-shaped — OEMetadata's own table partially fills this gap.
- **ckanext-dcat**: CKAN's DCAT extension — RDF endpoints and harvester with profiles for **DCAT-AP 1.1 / 2.1 / 3**, Google Dataset Search indexing support and Croissant ML output; AGPL-3.0; actively maintained (v2.4.3, May 2026) ([ckan/ckanext-dcat](https://github.com/ckan/ckanext-dcat)). A production-grade codebase to borrow DCAT-AP 3 serialization patterns from.
- **EUDAT B2FIND**: cross-domain crosswalks from DataCite, Dublin Core, ISO 19139 etc. into the DataCite-based B2FIND schema; mapfiles on GitHub ([EUDAT-B2FIND/md-mapping](https://github.com/EUDAT-B2FIND/md-mapping), [B2FIND provider docs](https://docs.eudat.eu/b2find/forproviders/)).
- **Independent multi-schema crosswalk table** (RDA-adjacent, Zenodo): mappings among Dublin Core, DataCite 4.3, DCAT 2.0, B2FIND and others ([zenodo.org/records/4420116](https://zenodo.org/records/4420116)) — secondary-ish, listed for completeness only.

## Machine-actionability & license summary

| Crosswalk | Executable? | Form | License |
|---|---|---|---|
| CiteDCAT-AP (DataCite→DCAT-AP) | Yes | XSLT + OAI-PMH proxy | EUPL-1.2 |
| JRC DCAT-AP→schema.org | Yes | SPARQL CONSTRUCT | EUPL-1.2 (code), CC BY 4.0 (doc) |
| W3C DCAT 3 Annex B | Yes | OWL/RDF alignment file (TTL) + prose table | W3C licenses |
| science-on-schema.org | No (guidance + JSON-LD examples) | prose + examples | Apache-2.0 |
| DataCite↔Dublin Core / PIDINST / FORCE11 | No | prose tables | DataCite docs |
| DataCite↔schema.org (bolognese) | Yes | Ruby library (powers content negotiation) | MIT |
| ckanext-dcat | Yes | Python library | AGPL-3.0 |
| OEMetadata mapping table | No | HTML table | (OEMetadata repo terms) |

## Assessment: hub-and-spoke vs three mappings

**Edge coverage between the three targets:**

- **DCAT ↔ schema.org — strong.** Owned by W3C inside the DCAT 3 Recommendation itself, with a machine-readable OWL alignment, and reinforced by Google accepting both formats interchangeably ([W3C](https://www.w3.org/TR/vocab-dcat-3/#dcat-sdo), [Google](https://developers.google.com/search/docs/appearance/structured-data/dataset)). Reusable as-is.
- **DataCite → DCAT-AP — good but dated and one-way.** CiteDCAT-AP is authoritative in provenance (EC JRC) and executable, but pinned to DataCite 4.4 / DCAT-AP 2.0.1 and only converts *from* DataCite ([ec-jrc](https://ec-jrc.github.io/datacite-to-dcat-ap/)).
- **DCAT-AP → DataCite — the weak edge.** No maintained artifact exists in this direction from any standards body. Chaining OEMetadata→DCAT-AP→DataCite is therefore not currently possible with off-the-shelf parts.
- **DataCite ↔ schema.org — solid, first-party, executable** (bolognese / content negotiation) ([datacite/bolognese](https://github.com/datacite/bolognese), [DataCite support](https://support.datacite.org/docs/datacite-content-resolver)) — but it solves *DataCite's* export problem, not OEMetadata's.

**Implication for OEMetadata:**

1. **Make DCAT-AP the hub spoke and invest there.** OEMetadata already has ~117 rows of OEMetadata→DC/DCAT/DCAT-AP.de mapping ([OEMetadata mappings](https://openenergyplatform.github.io/oemetadata/latest/oemetadata/metadata_mappings/)). The highest-value hackathon work is upgrading that table to SEMIC **DCAT-AP 3.0.1** and making it machine-actionable (e.g., JSON-LD context or SPARQL/py transform), rather than starting any new pairwise mapping from scratch.
2. **schema.org needs no independent OEMetadata mapping.** Derive it by chaining OEMetadata→DCAT-AP with the W3C Annex B alignment (and validate the output against Google's required `name`/`description` + recommended properties and science-on-schema.org conventions). Document the chain, don't maintain a third table.
3. **DataCite needs a thin direct mapping — the one genuine exception to pure hub-and-spoke.** Because the DCAT-AP→DataCite direction is uncovered, and because DataCite export exists chiefly for DOI registration (which demands DataCite's mandatory kernel: Identifier, Creator, Title, Publisher, PublicationYear, ResourceType per [schema 4.7](https://datacite-metadata-schema.readthedocs.io/)), a small direct OEMetadata→DataCite-4.7 mapping of the mandatory + relevant recommended properties is warranted. CiteDCAT-AP's tables can be read "backwards" as the starting vocabulary correspondence, and the *import* direction (DataCite→OEMetadata) can lean on CiteDCAT-AP + the DCAT-AP spoke.
4. **Caveats for chained crosswalks**: version skew (JRC artifacts at DCAT-AP 2.0.1 / DataCite 4.4 / schema.org 12.0 vs current 3.0.1 / 4.7 / 30.0), lossiness (JRC schema.org mapping has many TBDs), and OEMetadata-specific semantics (badge levels, energy-domain fields) that no third-party crosswalk will carry — those need explicit handling in the OEMetadata-owned spoke regardless of architecture.

**Bottom line**: not three independent mappings — **one full mapping (OEMetadata→DCAT-AP 3.0.1, evolving the existing table) + one thin mandatory-kernel mapping (OEMetadata→DataCite 4.7), with schema.org obtained via the W3C-maintained DCAT↔schema.org alignment.**

## Sources

- DataCite Metadata Schema — https://schema.datacite.org and https://datacite-metadata-schema.readthedocs.io/ (v4.7, 3 Mar 2026)
- DataCite schema 4.7 mappings — https://datacite-metadata-schema.readthedocs.io/en/4.7/mappings/
- DataCite Dublin Core mappings — https://datacite-metadata-schema.readthedocs.io/en/4.6/mappings/dublincore/ · https://datacite-metadata-schema.readthedocs.io/en/4.6/mappings/dublincore-qualified/
- DataCite content resolver — https://support.datacite.org/docs/datacite-content-resolver
- datacite/bolognese — https://github.com/datacite/bolognese
- OpenAIRE Guidelines for Data Archives — https://guidelines.openaire.eu/en/latest/data/index.html · https://github.com/openaire/guidelines-data-archives
- DCAT-AP (SEMIC) — https://semiceu.github.io/DCAT-AP/ · https://github.com/SEMICeu/DCAT-AP/releases
- W3C DCAT 3 Recommendation (22 Aug 2024), Annex B — https://www.w3.org/TR/vocab-dcat-3/#dcat-sdo
- DCAT→schema.org RDF alignment file — https://w3c.github.io/dxwg/dcat/rdf/dcat-schema.ttl (in https://github.com/w3c/dxwg)
- schema.org releases — https://schema.org/docs/releases.html (v30.0, 19 Mar 2026)
- Google Dataset Search structured data — https://developers.google.com/search/docs/appearance/structured-data/dataset
- JRC CiteDCAT-AP — https://ec-jrc.github.io/datacite-to-dcat-ap/ · https://github.com/ec-jrc/datacite-to-dcat-ap
- JRC DCAT-AP→schema.org — https://ec-jrc.github.io/dcat-ap-to-schema-org/ · https://github.com/ec-jrc/dcat-ap-to-schema-org
- science-on-schema.org — https://github.com/ESIPFed/science-on-schema.org (v1.3.2, DOI 10.5281/zenodo.7884538)
- OEMetadata mapping table — https://openenergyplatform.github.io/oemetadata/latest/oemetadata/metadata_mappings/
- Frictionless specs — https://specs.frictionlessdata.io/ · discussion https://github.com/frictionlessdata/project/issues/551 · community https://github.com/OSUKED/Frictionless-Data-to-DCAT
- ckanext-dcat — https://github.com/ckan/ckanext-dcat
- EUDAT B2FIND — https://docs.eudat.eu/b2find/forproviders/ · https://github.com/EUDAT-B2FIND/md-mapping
- Multi-schema crosswalk (Zenodo) — https://zenodo.org/records/4420116

*Repository maintenance dates and licenses verified via the GitHub API on 2026-07-16.*