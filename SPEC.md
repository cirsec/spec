# CIR Specification

> **Status: draft (v0.1).** Sections are specified one layer at a time.

## Conventions

- Dates use ISO 8601 `YYYY-MM-DD`.
- Enumerated values are lowercase.
- TLP values follow [TLP 2.0](https://www.first.org/tlp/): `CLEAR`, `GREEN`, `AMBER`, `AMBER+STRICT`, `RED`.

## Root

| Field | Type | Required | Description |
|---|---|---|---|
| `cir_version` | string | yes | Version of the CIR specification the record follows, e.g. `"0.1"`. |
| `meta` | object | yes | Identity and lifecycle of the record. |
| `core` | object | no | Layer 1. |
| `threat_intel` | object | no | Layer 2. |
| `posture` | object | no | Layer 3. |
| `context` | object | no | Layer 4. |
| `tags` | list of string | no | Free classification tags. |

## `meta`

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Record identifier, see [Identifier rules](#identifier-rules). |
| `revision` | integer >= 1 | yes | Incremented on every update of the record. |
| `title` | string | yes | Short descriptive title. |
| `status` | enum | yes | `draft`, `published`, `rejected`, `withdrawn`. |
| `created` | date | yes | Creation date of the record. |
| `updated` | date | yes | Last update date. Must be >= `created`. |
| `tlp` | enum | no | TLP ceiling for the whole record, see [TLP rules](#tlp-rules). |
| `based_on` | string | no | `id` of a parent CIR this record extends (typically an internal record adding `posture` / `context` to a public one). |
| `aliases` | list of string | no | Alternative names, lowercase slugs (`^[a-z0-9]+(-[a-z0-9]+)*$`). |
| `authors` | list of object | no | `name` (required), `contact`, `org`. |
| `history` | list of object | no | `date` (required), `author`, `change` (required). |

### Identifier rules

```
CIR-YYYY-CODE-NNNN
```

- **Public** record: `^CIR-\d{4}-0[A-Z0-9]{0,7}-\d{4,}$`. `CODE` must be listed in [`authorities.yml`](./authorities.yml). `00` is the root authority.
- **Internal** record: `^CIR-\d{4}-[A-Z1-9][A-Z0-9]{1,7}-\d{4,}$`. Managed freely by the organization, not globally unique.

Whether a record is public is **derived from the code** (first character is `0`); there is no separate field for it.

### TLP rules

- Each layer carries its own `tlp`.
- `meta.tlp`, when set, is a ceiling: no layer may be less restrictive than it.
- Restriction order: `CLEAR` < `GREEN` < `AMBER` < `AMBER+STRICT` < `RED`.
- Exporting a record to an audience means dropping every layer whose `tlp` is more restrictive than what that audience may receive.

### Validation

- `id` matches one of the two patterns above.
- Public `id` → `CODE` exists in `authorities.yml`.
- `updated` >= `created`.
- `based_on`, when set, matches a valid `id` pattern and differs from `id`.
- No layer `tlp` is less restrictive than `meta.tlp`.

## Layers: common rules

- Every layer present in a record must have a `tlp`.
- A layer can be omitted entirely.
- A record with `meta.based_on` inherits the `core` and `threat_intel` layers of its parent when it omits them. This is the normal shape of an internal record adding `posture` and/or `context` to a public one.

## `core` (layer 1)

What the issue is. `core` references existing standards and never redefines them. Products and versions follow the [OSV](https://ossf.github.io/osv-schema/) model so records can be imported from and exported to OSV.

| Field | Type | Required | Description |
|---|---|---|---|
| `tlp` | enum | yes | TLP of the layer. |
| `summary` | string | yes | One-line summary. |
| `details` | string (markdown) | no | Full description. |
| `disclosed` | date | no | Public disclosure date, or internal report date for internal records. |
| `identifiers` | list of object | no | External identifiers designating this issue. |
| `references` | list of object | no | Typed links. |
| `affected` | list of object | no | Affected products and versions. |
| `weaknesses` | list of string | no | CWE identifiers (`^CWE-\d+$`). |
| `severity` | list of object | no | Severity scores, possibly from several sources. |
| `remediations` | list of object | no | Fixes, mitigations and workarounds. |

### `identifiers[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `cve`, `ghsa`, `osv`, `vendor`, `internal`, `other`. |
| `id` | string | yes | The identifier. `cve` must match `^CVE-\d{4}-\d{4,}$`, `ghsa` must match `^GHSA(-[23456789cfghjmpqrvwx]{4}){3}$`. |

`internal` identifiers (ticket, pentest report ID...) are forbidden in public records and dropped by any export to a public audience.

### `references[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `advisory`, `fix`, `report`, `article`, `package`, `web`, `other`. |
| `url` | string (URL) | yes | |

Exploits and PoCs are not references: they belong to `threat_intel`.

### `affected[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `product.vendor` | string | no | |
| `product.name` | string | yes | |
| `product.purl` | string | no | [Package URL](https://github.com/package-url/purl-spec). |
| `product.cpe` | string | no | CPE 2.3 string. |
| `ranges` | list of object | no | Version ranges. |
| `versions` | list of string | no | Explicit affected versions, when no range applies. |

At least one of `ranges` or `versions` is required.

#### `ranges[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `semver`, `ecosystem`, `git`. |
| `repo` | string (URL) | if `git` | Repository the commits belong to. |
| `events` | list of object | yes | Ordered list of single-key objects: `introduced`, `fixed`, `last_affected`. |

Event semantics follow OSV: a version is affected if it is at or after an `introduced` and before the next `fixed` (or at or before the next `last_affected`). `introduced: "0"` means "since the first version". Several `introduced` / `fixed` pairs in one range describe disjoint affected intervals. For `git` ranges, events are commit hashes.

### `severity[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `cvss_v3.1`, `cvss_v4.0`. |
| `vector` | string | yes | Full vector string including the `CVSS:x.y/` prefix. |
| `score` | number 0.0 to 10.0 | yes | Base score. Must match the score computed from `vector`. |
| `source` | enum | yes | `nvd`, `vendor`, `issuer`. |

### `remediations[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `upgrade`, `patch`, `config`, `workaround`, `none`. |
| `description` | string | yes | |
| `status` | enum | yes | `available`, `planned`, `none`. |
| `date` | date | no | Date the remediation became available. |
| `reference` | string (URL) | no | |

### `core` validation

- `cve` / `ghsa` identifiers match their patterns.
- No `internal` identifier in a public record.
- Each `affected[]` has `ranges` or `versions`.
- Each range has at least one `introduced` event; `git` ranges have a `repo`.
- `severity[].score` matches the score computed from `vector`.

## `threat_intel` (layer 2)

Who exploits the issue, how, and since when. Two principles: **everything is dated and sourced**, and **entities (actors, malware, campaigns) are references, not descriptions**.

| Field | Type | Required | Description |
|---|---|---|---|
| `tlp` | enum | yes | TLP of the layer. |
| `updated` | date | yes | Freshness of the layer. Also the snapshot date of every value in `signals`. |
| `exploitation` | object | no | Exploit availability and in-the-wild activity. |
| `priority` | object | no | Public priority, computed. See [Scoring](#scoring). |
| `signals` | object | no | Snapshots of external feeds. |
| `actors` | list of entity | no | Threat actors. |
| `malware` | list of entity | no | Malware families. Adds `family_type`. |
| `campaigns` | list of entity | no | Campaigns. |
| `attack` | list of object | no | MITRE ATT&CK technique/tactic pairs. |
| `targeting` | object | no | Targeted sectors and regions. |
| `iocs` | list of object | no | Inline indicators (small volume). |
| `ioc_bundles` | list of object | no | External indicator bundles (large volume). |
| `detections` | list of object | no | Public detection rules. |
| `timeline` | list of object | no | Dated events. |
| `sources` | list of object | no | Sources referenced by the other fields. |

### Confidence

Every assertion that carries a `confidence` uses: `low`, `medium`, `high`, `critical`.

### `exploitation`

| Field | Type | Required | Description |
|---|---|---|---|
| `maturity` | enum | no | `none`, `poc`, `functional`, `weaponized`. |
| `in_the_wild` | enum | no | `true`, `false`, `unknown`. |
| `first_seen` | date | no | First observed exploitation. |
| `exploits[]` | list of object | no | `type` (`poc`, `module`, `template`, `kit`, `writeup`), `source` (`github`, `exploitdb`, `metasploit`, `nuclei`, `other`), `url` (required), `date`. |

### `signals`

Values from external feeds are **stored, not resolved live**, so a record stays usable offline. They are a snapshot taken at `threat_intel.updated`: refreshing any signal means bumping `threat_intel.updated`.

| Field | Type | Description |
|---|---|---|
| `kev.listed` | boolean | Listed in CISA KEV. |
| `kev.date_added` | date | KEV `dateAdded`. |
| `kev.ransomware_use` | enum | KEV `knownRansomwareCampaignUse`: `known`, `unknown`. |
| `epss.score` | number 0 to 1 | EPSS probability. |
| `epss.percentile` | number 0 to 1 | EPSS percentile. |

### Entities (`actors[]`, `malware[]`, `campaigns[]`)

| Field | Type | Required | Description |
|---|---|---|---|
| `refs` | list of object | no | Identifiers of the same entity in several namespaces: `type` (`mitre`, `mlab`, `misp`, `malpedia`, `other`) and `id`. |
| `name` | string | yes | Display name. |
| `confidence` | enum | no | Confidence that this entity is linked to the issue. |
| `first_seen` | date | no | First observed link. |
| `sources` | list of string | no | `id`s from `sources[]`. |
| `family_type` | enum | no | `malware[]` only: `ransomware`, `botnet`, `miner`, `rat`, `loader`, `webshell`, `other`. |

A `mitre` ref for an actor must match `^G\d{4}$`, for malware `^S\d{4}$`, for a campaign `^C\d{4}$`.

### `attack[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `technique` | string | yes | `^T\d{4}(\.\d{3})?$` |
| `tactic` | string | yes | `^TA\d{4}$` |

### `targeting`

| Field | Type | Description |
|---|---|---|
| `sectors` | list of string | `all` or sectors (recommended list: `finance`, `health`, `energy`, `government`, `telecom`, `education`, `manufacturing`, `retail`, `transport`, `defense`, `technology`). |
| `regions` | list of string | ISO 3166-1 alpha-2 codes. |

### `iocs[]` and `ioc_bundles[]`

Inline `iocs` are meant for a handful of key indicators (about 50 at most). Large sets go to `ioc_bundles`.

| Field | Type | Required | Description |
|---|---|---|---|
| `iocs[].type` | enum | yes | `ip`, `domain`, `url`, `sha256`, `sha1`, `md5`, `pattern`, `other`. |
| `iocs[].value` | string | yes | |
| `iocs[].first_seen` / `last_seen` | date | no | |
| `iocs[].confidence` | enum | no | |
| `iocs[].sources` | list of string | no | |
| `ioc_bundles[].format` | enum | yes | `stix`, `misp`, `csv`. |
| `ioc_bundles[].url` | string (URL) | yes | |

### `detections[]`

Public detection rules only. What an organization actually deploys never goes here (see `posture`).

| Field | Type | Required | Description |
|---|---|---|---|
| `format` | enum | yes | `sigma`, `yara`, `suricata`, `snort`, `nuclei`, `kql`, `spl`. |
| `name` | string | no | |
| `url` | string (URL) | yes | |

### `timeline[]` and `sources[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `timeline[].date` | date | yes | |
| `timeline[].event` | string | yes | |
| `timeline[].sources` | list of string | no | |
| `sources[].id` | string | yes | Local to the record, unique, e.g. `s1`. |
| `sources[].name` | string | yes | |
| `sources[].url` | string (URL) | no | |
| `sources[].date` | date | no | |
| `sources[].reliability` | enum | no | Admiralty source reliability: `A` to `F`. |

### `threat_intel` validation

- Every `sources` reference points to an existing `sources[].id`.
- `sources[].id` values are unique.
- `mitre` refs and `attack[]` values match their patterns.
- `exploitation.first_seen` and `timeline[].date` are <= `updated`.

## `posture` (layer 3)

The state of **one entity** facing the issue, expressed **in generic terms only**. This layer is designed to be shared with a group or sector CERT, which can aggregate it across entities without learning anything about their assets.

**Hard rule: `posture` contains no free text, no numbers and no names.** Every value is an enum, a boolean, a date, or an identifier matching a pattern. If a need doesn't fit the enums, the enum is extended in the specification, not worked around in the record.

| Field | Type | Required | Description |
|---|---|---|---|
| `tlp` | enum | yes | TLP of the layer. `AMBER` recommended. |
| `updated` | date | yes | Date of this posture assessment. |
| `entity` | string | no | Pseudonymous ID assigned by the receiving CERT (`^[A-Z0-9][A-Z0-9-]{0,31}$`). Never the entity name. |
| `status` | object | yes | VEX-aligned status. |
| `prerequisites` | object | no | What exploitation actually requires at this entity. |
| `exposure` | object | no | Reachability and prevalence. |
| `controls` | list of object | no | Controls in place against this issue. |
| `detection` | object | no | Detection capability. |
| `impact` | object | no | What exploitation enables at this entity. |
| `remediation` | object | no | Feasibility and constraints of remediation. |

`posture` has no score field: its contribution to scoring (the exposure bucket) is derived, see [Scoring](#scoring).

### `status`

Aligned with [VEX](https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf), so a posture can be exported as a VEX statement.

| Field | Type | Required | Description |
|---|---|---|---|
| `state` | enum | yes | `not_affected`, `affected`, `mitigated`, `fixed`, `under_investigation`. |
| `justification` | enum | if `not_affected` | `component_not_present`, `vulnerable_code_not_present`, `vulnerable_code_not_in_execute_path`, `vulnerable_code_cannot_be_controlled_by_adversary`, `inline_mitigations_already_exist`. |

`mitigated` has no direct VEX equivalent and exports as `affected` with the controls as action statement.

### `prerequisites`

What exploitation actually requires at this entity. It differs from CVSS, which describes the issue in the abstract (e.g. a network vulnerability only exploitable with a non-default feature enabled).

| Field | Type | Description |
|---|---|---|
| `attack_vector` | enum | `network`, `adjacent`, `local`, `physical`. |
| `privileges` | enum | `none`, `low`, `high`. |
| `user_interaction` | boolean | |
| `configuration` | enum | `default`, `non_default`. |
| `conditions` | list of enum | `feature_enabled`, `specific_os`, `specific_version`, `network_position`, `valid_account`, `other`. |

### `exposure`

| Field | Type | Description |
|---|---|---|
| `reachability` | enum | `internet`, `partner`, `internal`, `isolated`, `not_deployed`. |
| `prevalence` | enum | `none`, `rare`, `common`, `widespread`. Qualitative bucket, never a count. |

### `controls[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `control` | enum | yes | `segmentation`, `waf`, `ips`, `edr`, `mfa`, `egress_filtering`, `hardening`, `app_allowlisting`, `virtual_patching`, `other`. |
| `effect` | enum | yes | `blocks`, `reduces`, `detects`. |
| `coverage` | enum | yes | `partial`, `full`. |
| `validated` | boolean | yes | `true` if tested (purple team, pentest, simulation), `false` if assumed. |

### `detection`

| Field | Type | Description |
|---|---|---|
| `capability` | enum | `none`, `partial`, `full`. |
| `layers` | list of enum | `network`, `endpoint`, `logs`, `waf`, `application`. |
| `validated` | boolean | `true` if detection was tested. |

### `impact`

| Field | Type | Description |
|---|---|---|
| `enables` | list of enum | `code_execution`, `data_access`, `privilege_escalation`, `lateral_movement`, `persistence`, `denial_of_service`. |
| `blast_radius` | enum | `component`, `host`, `segment`, `domain`, `organization`, `supply_chain`. |
| `chained_with` | list of string | CIR IDs or CVE IDs this issue chains with. |

### `remediation`

| Field | Type | Description |
|---|---|---|
| `feasibility` | enum | `easy`, `moderate`, `hard`, `blocked`. |
| `constraints` | list of enum | `legacy`, `vendor_dependency`, `downtime_required`, `certification`, `third_party_managed`. |

### `posture` validation

- No field outside this specification (unknown keys are rejected, so no free text can be added).
- All values match their enum, type or pattern.
- `status.justification` is present if and only if `status.state` is `not_affected`.
- `chained_with` entries match a CIR or CVE pattern.

## `context` (layer 4)

What the issue means for **one organization**: affected assets, business impact, decisions, remediation and communication. This layer never leaves the organization (`RED` by default). Unlike `posture`, free text and names are allowed, but structured fields come first.

| Field | Type | Required | Description |
|---|---|---|---|
| `tlp` | enum | yes | TLP of the layer. `RED` recommended. |
| `updated` | date | yes | Last update of this layer. |
| `org` | string | no | Organization or business unit. |
| `assets` | list of object | no | Key assets, inline. |
| `asset_selectors` | list of object | no | Queries against the source of truth, for large volumes. |
| `exploitation` | object | no | Whether the issue was exploited in this organization. |
| `business_impact` | object | no | Business and regulatory impact. |
| `decision` | object | no | Treatment decision. |
| `remediation` | object | no | Remediation tracking. |
| `communication` | list of object | no | Who was informed, when, how. |
| `score` | object | no | Organizational risk, computed. See [Scoring](#scoring). |
| `notes` | list of object | no | Free-text notes. |

### `assets[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `ref` | string | yes | Asset ID in the CMDB or inventory. |
| `name` | string | no | |
| `type` | enum | no | `server`, `workstation`, `application`, `database`, `network_device`, `cloud_resource`, `container`, `saas`, `ot`, `other`. |
| `environment` | enum | no | `prod`, `preprod`, `dev`, `test`. |
| `exposure` | enum | no | `internet`, `partner`, `internal`, `isolated`. |
| `criticality` | enum | no | `low`, `medium`, `high`, `critical`. |
| `data_classification` | enum | no | `public`, `internal`, `confidential`, `secret`. |
| `owner` | string | no | |
| `state` | enum | no | `affected`, `mitigated`, `fixed`, `not_affected`. |

### `asset_selectors[]`

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | enum | yes | `cmdb`, `edr`, `scanner`, `cloud`, `other`. |
| `query` | string | yes | Query in the source's own syntax. |
| `matched` | integer | no | Number of assets matched at `context.updated`. |

### `exploitation`

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | enum | yes | `none`, `suspected`, `confirmed`. |
| `incident_ref` | string | if `suspected` or `confirmed` | Incident ticket. CIR references incidents, it does not describe them. |

### `business_impact`

| Field | Type | Description |
|---|---|---|
| `confidentiality` / `integrity` / `availability` | enum | `none`, `low`, `medium`, `high`, `critical`. |
| `services` | list of string | Impacted business processes. |
| `data_at_risk` | list of enum | `personal`, `financial`, `health`, `credentials`, `ip`, `other`. |
| `regulatory` | list of enum | `gdpr`, `nis2`, `dora`, `pci_dss`, `hds`, `other`. |

### `decision`

| Field | Type | Required | Description |
|---|---|---|---|
| `action` | enum | yes | `fix`, `mitigate`, `accept`, `transfer`, `monitor`, `false_positive`. |
| `justification` | string | no | |
| `decided_by` | string | no | |
| `decided_on` | date | no | |
| `review_on` | date | if `accept`, `transfer` or `monitor` | A risk that is not fixed must be reviewed. Must be > `decided_on`. |
| `approved_by` | string | no | |

### `remediation`

| Field | Type | Required | Description |
|---|---|---|---|
| `owner` | string | no | Responsible team. |
| `assignee` | string | no | |
| `sla` | string | no | Internal SLA class, e.g. `P1-7d`. |
| `due` | date | no | Stored explicitly. Computing it from a policy is the tooling's job, not the format's. |
| `status` | enum | yes | `open`, `in_progress`, `resolved`, `verified`, `reopened`. |
| `tickets[]` | list of object | no | `system` (`jira`, `plane`, `servicenow`, `gitlab`, `github`, `other`), `id` (required), `url`. |
| `verified_on` | date | if `verified` | |
| `verified_by` | string | no | |
| `verification_method` | enum | no | `rescan`, `pentest`, `manual`, `other`. |

### `communication[]`

The communication log is what makes a CIR a shared reference across teams: who was informed, when and through which channel.

| Field | Type | Required | Description |
|---|---|---|---|
| `audience` | enum | yes | `soc`, `it_ops`, `dev`, `ciso`, `management`, `legal`, `dpo`, `business`, `cert`, `vendor`, `regulator`. |
| `date` | date | yes | |
| `channel` | enum | no | `email`, `ticket`, `meeting`, `chat`, `report`, `other`. |
| `by` | string | no | |

### `score`

| Field | Type | Description |
|---|---|---|
| `value` | number 0 to 10 | Organizational risk. |
| `level` | enum | `none`, `low`, `medium`, `high`, `critical`. |
| `method` | string | `cir-risk/0.1`, or an organization-specific method name. |

### `notes[]`

| Field | Type | Required |
|---|---|---|
| `date` | date | yes |
| `author` | string | no |
| `text` | string | yes |

### `context` validation

- `decision.review_on` is required when `decision.action` is `accept`, `transfer` or `monitor`, and must be after `decided_on`.
- `exploitation.incident_ref` is required when `exploitation.status` is `suspected` or `confirmed`.
- `remediation.verified_on` is required when `remediation.status` is `verified`.

## Scoring

Method: **`cir-risk/0.1`**.

Principles:

- **Deterministic**: scores are computed from the record fields only, never typed in.
- **Explainable**: additive points that a human can recompute in a meeting.
- **Versioned**: a stored score names its `method`; validators recompute it and reject mismatches.
- **Comparable**: the method is fixed, so a `high` means the same thing in every organization. An organization may store its own score under another `method` name, but `cir-risk` remains the comparable reference.

```
 core          threat_intel        posture            context
   |                |                 |                  |
 SEVERITY       EXPLOITATION       EXPOSURE            IMPACT
   0-3              0-3               0-3                0-3
   +-------+--------+                 |                  |
           |                          |                  |
   PUBLIC PRIORITY (0-6)              |                  |
           +--------------+-----------+------------------+
                          |
                   ORG RISK (0-12) + overrides
```

Inherited layers (`meta.based_on`) count as present.

### Inputs

**Severity** (from `core.severity`). The retained score is chosen by source (`issuer` > `vendor` > `nvd`), then by version (`cvss_v4.0` > `cvss_v3.1`).

| Retained CVSS score | Points |
|---|---|
| >= 9.0 | 3 |
| >= 7.0 | 2 |
| >= 4.0 | 1 |
| < 4.0 | 0 |
| no severity | 3 (worst case) |

**Exploitation** (from `threat_intel`).

| Bucket | Condition | Points |
|---|---|---|
| `active` | `exploitation.in_the_wild` is `true` or `signals.kev.listed` is `true` | 3 |
| `public` | `exploitation.maturity` is `poc`, `functional` or `weaponized` | 2 |
| `none` | otherwise | 0 |
| unknown | no `threat_intel` layer | 2 (treated as `public`) |

An unknown exploitation is treated as `public`, not `active`: internal issues rarely have threat intelligence, and an internal finding (e.g. pentest) implies a working proof of concept.

**Exposure** (from `posture`). The first matching bucket applies.

| Bucket | Condition | Points |
|---|---|---|
| `none` | `status.state` is `not_affected` or `fixed`, or `exposure.reachability` is `not_deployed` | override, see below |
| `contained` | `exposure.reachability` is `isolated`, or a control has `effect: blocks`, `coverage: full`, `validated: true` | 0 |
| `controlled` | `exposure.reachability` is `internal`, or a control has `effect: blocks` (partial or not validated), or a control has `effect: reduces`, `coverage: full`, `validated: true` | 2 |
| `open` | otherwise | 3 |
| unknown | no `posture` layer | 3 (worst case) |

**Impact** (from `context`). The highest value among `assets[].criticality`, `business_impact.confidentiality`, `business_impact.integrity` and `business_impact.availability`.

| Highest value | Points |
|---|---|
| `critical` | 3 |
| `high` | 2 |
| `medium` | 1 |
| `low`, `none` | 0 |
| unknown | 3 (worst case) |

Unknown severity, exposure and impact default to the worst case: an unknown risk is treated as a dangerous one, which also pushes organizations to fill their layers.

### Public priority

Computable without any organizational data. Stored in `threat_intel.priority`.

```
points = severity + exploitation        (0 to 6)
value  = round(points / 6 * 10, 1)
```

| Points | Level |
|---|---|
| 5 to 6 | `critical` |
| 4 | `high` |
| 2 to 3 | `medium` |
| 0 to 1 | `low` |

### Organizational risk

Stored in `context.score`.

```
points = severity + exploitation + exposure + impact     (0 to 12)
value  = round(points / 12 * 10, 1)
```

| Points | Level |
|---|---|
| 10 to 12 | `critical` |
| 7 to 9 | `high` |
| 4 to 6 | `medium` |
| 0 to 3 | `low` |

Overrides, applied in order:

1. Exposure bucket `none` → level `none`, value `0`.
2. `context.exploitation.status` is `confirmed` → level `critical` (value unchanged). The issue is an incident.
3. `signals.kev.listed` is `true` and exposure bucket is `open` → level at least `high`.

### Worked examples

| Record | Severity | Exploitation | Exposure | Impact | Result |
|---|---|---|---|---|---|
| `CIR-2021-00-0001` | 3 (CVSS 10.0) | 3 (KEV, in the wild) | n/a | n/a | Public priority 6 → **10.0 critical** |
| `CIR-2021-GRP-0003` | 3 (inherited) | 3 (inherited) | 0 (egress filtering blocks, full, validated) | 3 (critical asset) | 9 → **7.5 high** |
| `CIR-2026-LAB-0012` | 1 (CVSS 6.5) | 2 (unknown) | 3 (no posture) | 3 (no context) | 9 → **7.5 high** until the organization fills its layers |
