# OEMetadata Crosswalk – inkl. DataCite Mapping

Quelle der Basis-Spalten (OEMetadata Key, Badge, Dublin Core, DCAT necessity, DCAT-AP.de, IRI):
https://openenergyplatform.github.io/oemetadata/latest/oemetadata/metadata_mappings/

Die Spalte **DataCite** wurde ergänzt und bildet die OEMetadata-Felder auf Properties des
**DataCite Metadata Schema 4.x** ab (soweit ein sinnvolles Pendant existiert). Leere Zellen
bedeuten: kein direktes DataCite-Äquivalent vorhanden.

| # | OEMetadata Key | Badge | Dublin Core | DCAT necessity | DCAT-AP.de | DataCite |
|---|---|---|---|---|---|---|
| 1 | name | Iron | | mandatory | dcat:Dataset | Identifier (identifierType: DOI/other) |
| 2 | title | Bronze | | mandatory | dcat:Dataset / dct:title | Title |
| 3 | description | Bronze | description | mandatory | dcat:Dataset / dcterms:description | Description (descriptionType: Abstract) |
| 4 | id | Silver | identifier | optional | dcat:Dataset / dct:identifier | Identifier |
| 5 | resources | | type | mandatory | dcat:Dataset | RelatedIdentifier / RelationType: HasPart |
| 6 | name (resource) | Iron | | mandatory | dcat:Distribution / dcat:accessURL | – |
| 7 | topics | Bronze | coverage | mandatory | dcat:Distribution / dcat:accessURL | Subject |
| 8 | title (resource) | Silver | title | recommended | dcat:Distribution / dcterms:title | Title (TitleType: AlternativeTitle) |
| 9 | path | Bronze | identifier | mandatory | dcat:Distribution / dcat:accessURL | RelatedIdentifier / Identifier (URL) |
| 10 | description (resource) | Silver | description | optional | dcat:Distribution / dcterms:description | Description |
| 11 | languages | Gold | language | optional | dcat:Distribution / dcterms:language | Language |
| 12 | **subject** | | subject | | Datapackage | Subject (Container) |
| 13 | name (subject) | Platinum | | recommended | dcat:Dataset / dcat:theme | Subject |
| 14 | @id (subject) | Platinum | | recommended | dcat:Dataset / dcat:theme | Subject / subjectScheme + valueURI |
| 15 | keywords | Silver | subject | recommended | dcat:Dataset / dcat:keyword | Subject |
| 16 | publicationDate | Bronze | date | optional | dcat:Distribution / dcterms:issued | PublicationYear / Date (dateType: Issued) |
| 17 | **embargoPeriod** | | | | Datapackage | Date (dateType: Available / Withheld) |
| 18 | start (embargo) | Bronze | | optional | OEP | Date (dateType: Withheld, start) |
| 19 | end (embargo) | Bronze | | optional | OEP | Date (dateType: Available) |
| 20 | isActive | Bronze | | optional | OEP | – |
| 21 | **context** | | | | Datapackage | Creator / Contributor (Container) |
| 22 | title (context) | Gold | | recommended | vcard:fn | Creator / creatorName or Contributor / contributorName |
| 23 | homepage | Gold | | recommended | vcard:hasURL | nameIdentifier / affiliationIdentifier (URL) |
| 24 | documentation | Gold | | optional | dcat:Distribution / foaf:page | RelatedIdentifier / RelationType: IsDocumentedBy |
| 25 | sourceCode | Gold | | optional | dcat:Distribution / foaf:page | RelatedIdentifier / RelationType: IsSupplementTo |
| 26 | contact | Gold | | recommended | vcard:hasEmail | Contributor / contributorType: ContactPerson |
| 27 | grantNo | Gold | | optional | OEP | FundingReference / awardNumber |
| 28 | fundingAgency | Gold | | optional | OEP | FundingReference / funderName |
| 29 | fundingAgencyLogo | Gold | | optional | foaf:logo | – |
| 30 | publisher | Bronze | publisher | mandatory | dcat:Dataset / dcat:publisher | Publisher |
| 31 | publisherLogo | Gold | | optional | foaf:logo | – |
| 32 | **spatial** | | coverage | | Datapackage | GeoLocation (Container) |
| 33 | **location** | | | | dcterms:Location | GeoLocation |
| 34 | address | Silver | | optional | locn:Address / locn:fullAddress | GeoLocationPlace |
| 35 | @id (location) | Platinum | | optional | dcterms:Location / locn:geographicIdentifier | – |
| 36 | latitude | Gold | | optional | locn:Geometry / latitude | GeoLocationPoint / pointLatitude |
| 37 | longitude | Gold | | optional | locn:Geometry / longitude | GeoLocationPoint / pointLongitude |
| 38 | **extent** | | | | dcterms:Location | GeoLocationBox |
| 39 | name (extent) | Silver | | optional | dcterms:Location / geographicName | GeoLocationPlace |
| 40 | @id (extent) | Platinum | | optional | dcterms:Location / locn:geographicIdentifier | – |
| 41 | resolutionValue | Silver | | optional | dcat:Distribution / dcat:spatialResolutionInMeters | – |
| 42 | resolutionUnit | Silver | | optional | dcat:Distribution / dcat:spatialResolutionInMeters | – |
| 43 | boundingBox | Gold | | recommended | dcterms:Location / dcat:bbox | GeoLocationBox |
| 44 | crs | Gold | | optional | locn:Geometry / crs | – |
| 45 | **temporal** | | coverage | | dcterms:PeriodOfTime | Date (Container) |
| 46 | referenceDate | Silver | | optional | OEP | Date (dateType: Collected) |
| 47 | **timeseries** | | | | Datapackage | Date (Container) |
| 48 | start (timeseries) | Silver | | optional | dcterms:PeriodOfTime / time:hasBeginning | Date (dateType: Collected, start) |
| 49 | end (timeseries) | Silver | | optional | dcterms:PeriodOfTime / time:hasEnd | Date (dateType: Collected, end) |
| 50 | resolutionValue (ts) | Silver | | optional | dcat:Distribution / dcat:temporalResolution | – |
| 51 | resolutionUnit (ts) | Silver | | optional | dcat:Distribution / dcat:temporalResolution | – |
| 52 | alignment | Gold | | optional | OEP | – |
| 53 | aggregationType | Gold | | optional | OEP | – |
| 54 | **sources** | | source | | Datapackage | RelatedIdentifier / RelationType: IsDerivedFrom |
| 55 | title (source) | Bronze | | optional | BibTeX title | Title (within related work) |
| 56 | author (source) | Bronze | | optional | BibTeX author | Creator (within related work) |
| 57 | description (source) | Bronze | | optional | BibTeX note | Description |
| 58 | publicationYear (source) | Bronze | | optional | BibTeX year | PublicationYear |
| 59 | path (source) | Bronze | | optional | BibTeX howpublished | RelatedIdentifier / Identifier |
| 60 | **sourceLicenses** | | | | Datapackage | Rights (Container) |
| 61 | name (sourceLicense) | Bronze | | optional | OEP / spdx.org | RightsIdentifier |
| 62 | title (sourceLicense) | Bronze | | optional | OEP | Rights |
| 63 | path (sourceLicense) | Bronze | | optional | dcat:Distribution / dcterms:license | RightsURI |
| 64 | instruction | Bronze | | optional | OEP | – |
| 65 | attribution (sourceLicense) | Bronze | | optional | dcatde:licenseAttributionByText | Rights (attribution note) |
| 66 | copyrightStatement | Bronze | | optional | dcat:Distribution / dcterms:rights | Rights |
| 67 | **licenses** | | rights | | Datapackage | Rights (Container) |
| 68 | name (license) | Bronze | | optional | OEP / spdx.org | RightsIdentifier |
| 69 | title (license) | Bronze | | optional | OEP | Rights |
| 70 | path (license) | Bronze | | mandatory | dcat:Distribution / dcterms:license | RightsURI |
| 71 | instruction (license) | Bronze | | optional | OEP | – |
| 72 | attribution (license) | Bronze | creator | optional | dcatde:licenseAttributionByText | Rights (attribution note) |
| 73 | **contributors** | | contributor | | Datapackage | Contributor (Container) |
| 74 | title (contributor) | Bronze | | optional | foaf:name | contributorName |
| 75 | path (contributor) | Bronze | | optional | dcat:Dataset / dcterms:contributor | nameIdentifier |
| 76 | organization | Bronze | | optional | foaf:Organization | affiliation |
| 77 | roles | Bronze | | optional | dcat:Relationship / dcat:hadRole | contributorType |
| 78 | date (contributor) | Bronze | date | recommended | dcat:Distribution / dcterms:modified | Date (dateType: Updated) |
| 79 | object | Bronze | | optional | OEP | – |
| 80 | comment | Bronze | | optional | OEP | – |
| 81 | type | Gold | | | Datapackage | ResourceType |
| 82 | format | Gold | format | recommended | dcat:Distribution / dcterms:format | Format |
| 83 | encoding | Gold | | optional | OEP | – |
| 84 | **schema** | | | | Datapackage | – |
| 85 | **fields** | | | | Datapackage | – |
| 86 | name (field) | Iron | | optional | OEP | – |
| 87 | description (field) | Silver | | optional | OEP | – |
| 88 | type (field) | Iron | | optional | OEP | – |
| 89 | nullable | Iron | | optional | OEP | – |
| 90 | unit | Silver | | optional | OEP | – |
| 91 | **isAbout** | | | | Datapackage | Subject (Container) |
| 92 | name (isAbout) | Platinum | | optional | OEP | Subject |
| 93 | @id (isAbout) | Platinum | | optional | OEP | Subject / valueURI |
| 94 | **valueReference** | | | | Datapackage | – |
| 95 | value | Platinum | | optional | OEP | – |
| 96 | name (valueReference) | Platinum | | optional | OEP | – |
| 97 | @id (valueReference) | Platinum | | optional | OEP | – |
| 98 | primaryKey | Iron | | optional | OEP | – |
| 99 | **foreignKeys** | | relation | | Datapackage | RelatedIdentifier / RelationType: References |
| 100 | fields (foreignKeys) | Iron | | optional | OEP | – |
| 101 | **reference** | | | | Datapackage | – |
| 102 | resource (reference) | Iron | | optional | OEP | – |
| 103 | fields (reference) | Iron | | optional | OEP | – |
| 104 | **dialect** | | | | Datapackage | – |
| 105 | delimiter | Iron | | optional | OEP | – |
| 106 | decimalSeparator | Iron | | optional | OEP | – |
| 107 | @id (dialect) | Platinum | identifier | optional | OEP | – |
| 108 | @context | Platinum | | optional | dcat:Distribution / dcterms:conformsTo | – |
| 109 | **review** | | | | Datapackage | – |
| 110 | path (review) | | | optional | OEP | – |
| 111 | badge | | | optional | OEP | – |
| 112 | **metaMetadata** | | | | Datapackage | – |
| 113 | metadataVersion | | | optional | OEP | Version (Schema-Version) |
| 114 | **metadataLicense** | | | optional | OEP | RightsIdentifier |
| 115 | name (metadataLicense) | | | optional | OEP | RightsIdentifier |
| 116 | title (metadataLicense) | | | optional | OEP | Rights |
| 117 | path (metadataLicense) | | | optional | OEP | RightsURI |

## Anmerkungen zur DataCite-Zuordnung

- **Fett gedruckte** Zeilen (z.B. `**subject**`, `**contributors**`) sind Container-/Gruppenknoten aus OEMetadata ohne eigenen Skalarwert – die DataCite-Spalte verweist hier auf die entsprechende DataCite-Property-Gruppe.
- `–` bedeutet: kein sinnvolles DataCite-Pendant, da DataCite deutlich schlanker ist als OEMetadata/DCAT-AP (z.B. technische Feldbeschreibungen wie `schema.fields.type` oder `dialect.delimiter` haben keine Entsprechung im DataCite-Schema).
- Die Zuordnung `contributors.roles → contributorType` ist nur eine Annäherung: DataCite verwendet eine kontrollierte Vokabelliste für `contributorType` (z.B. ContactPerson, DataCollector, Editor, ProjectLeader, Researcher, etc.), die nicht 1:1 mit den OEMetadata-Rollenwerten übereinstimmt – hier braucht es ggf. eine eigene Cross-Mapping-Tabelle.
- `sources` (BibTeX-orientiert) lässt sich nur über `RelatedIdentifier` bzw. eingebettete `Creator`/`Title`/`PublicationYear` der referenzierten Ressource abbilden, nicht 1:1 als flaches Feld.
- Basis: DataCite Metadata Schema 4.4/4.5 (Stand: aktuelle Spezifikation unter https://schema.datacite.org/).


## Anmerkungen zum OEM-Context
- Root-Datensatz hat keinen Typ
- Resources haben auch keinen Typ
- resources ist eigentlich eine object property (Relation) wird aber im Context gemapped auf 
- dcat:Dataset, sollte stattdessen dct:hasPart sein
- resource wird gemapped auf dcat:Distribution, sollte dcat:Dataset sein (siehe dazu Doku DCAT3 bag of files)
