# Visualization — Crosswalk architecture and data flow

How the pieces of the metadata crosswalk work together. Companion to [[Design - RDF crosswalk pipeline]] and [[Metadata Crosswalk - Wayfinder Map]]. Status: reflects the decisions as of 2026-07-16.

## 1. The pipeline — how one record flows through

```mermaid
flowchart LR
    subgraph ingest["Ingest"]
        A[Input file] --> B{Detect<br/>format}
        B -->|OEMetadata JSON<br/>has @context| C[Treat as JSON-LD<br/>existing OEMetadata @context]
        B -->|Turtle / RDF-XML /<br/>JSON-LD| D[rdflib parser<br/>plugins]
    end

    C --> E[(rdflib Graph)]
    D --> E

    subgraph crosswalk["Crosswalk (SHACL)"]
        E --> F[SHACL shapes<br/>validate input]
        F --> G[SHACL rules SHACL-AF<br/>derive target triples]
        G --> H[SHACL shapes<br/>validate output]
    end

    subgraph egress["Egress"]
        H --> I{Output<br/>format}
        I -->|RDF| J[Serialize:<br/>Turtle / JSON-LD / RDF-XML]
        I -->|non-RDF target| K[Dedicated egress:<br/>DataCite JSON/XML]
    end

    J --> L[Output file]
    K --> L
```

Notes:

- OEMetadata v2 records already carry `@context`, so they parse as JSON-LD directly — the pivot expression reuses that context (open point: verify its per-field coverage).
- The mapping logic lives entirely in **SHACL rules**; the code around it is generic plumbing.
- Runtime loss logging (reporting dropped fields during the crosswalk step) is **future work**.

## 2. The standards map — hub-and-spoke

```mermaid
flowchart TD
    OEM["OEMetadata v2+<br/>(JSON-LD via @context)"]

    DCAT["DCAT-AP 3.0.1<br/>(hub)"]
    SDO["schema.org Dataset<br/>(v30.0)"]
    DC["DataCite 4.7"]

    OEM <-->|"SHACL rules<br/>(this effort — the serious mapping,<br/>upgrades the first-party 117-row table)"| DCAT
    DCAT <-->|"W3C DCAT 3 Annex B<br/>alignment (dcat-schema.ttl)<br/>— reusable as-is"| SDO
    OEM -->|"thin direct export<br/>(this effort — DataCite<br/>mandatory kernel, for DOIs)"| DC
    DC -->|"JRC CiteDCAT-AP XSLT<br/>(DataCite 4.4 → DCAT-AP 2.0.1,<br/>one-directional, dated)"| DCAT
    DC <-->|"DataCite bolognese<br/>(content negotiation)"| SDO

    style OEM fill:#1a6b4a,color:#fff
    style DCAT fill:#1f4e79,color:#fff
```

Reading the picture:

- **Two mappings to build, not three**: the serious OEMetadata ↔ DCAT-AP leg (SHACL rules) and a thin OEMetadata → DataCite export. schema.org falls out of the hub via the W3C alignment.
- The **DataCite → DCAT-AP** direction has an existing (dated) JRC artifact; **DCAT-AP → DataCite exists nowhere**, which is why the thin direct export leg is unavoidable.
- Reverse directions (imports into OEMetadata) ride the same edges backwards; synthesis rules for required OEMetadata fields are still fog on the map.

## 3. How the effort's artifacts feed each other

```mermaid
flowchart LR
    subgraph inputs["Existing assets"]
        T117["First-party mappings table<br/>(117 rows, DCAT-AP.de)"]
        CTX["Shipped OEMetadata<br/>@context"]
        ANNEXB["W3C DCAT 3 Annex B<br/>dcat-schema.ttl"]
    end

    subgraph tickets["Map tickets"]
        INV["02 Field inventory<br/>(running)"]
        CONS["03 Consumers<br/>(team, open)"]
        TMPL["04 Spec template"]
        SPIKE["06 SHACL spike"]
        DCITE["05 DataCite thin export"]
        DCATX["08 DCAT-AP crosswalk<br/>(SHACL rules)"]
        SDOV["09 schema.org validation"]
    end

    T117 --> INV
    CTX --> INV
    INV --> SPIKE
    INV --> TMPL
    CONS --> TMPL
    CONS --> DCITE
    TMPL --> DCITE
    TMPL --> DCATX
    SPIKE --> DCATX
    ANNEXB --> SDOV
    DCATX --> SDOV
```

Resolved so far: the crosswalk survey (versions + reusable artifacts) and the architecture decision (RDF-first with SHACL). Full status lives on the [[Metadata Crosswalk - Wayfinder Map]].