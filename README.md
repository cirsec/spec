# CIR - Cyber Issue Record

> **Status: draft (v0.1).** The format is not stable and fields may change.

## Why CIR

A CVE and its CVSS score tell you how severe a vulnerability is *in theory*. They don't tell you how severe it is *for you*, who is exploiting it, whether you can detect it, or what was decided about it. So every team (SOC, vuln management, dev, CISO, business) rewrites the same issue in its own tickets, emails and spreadsheets, and context is lost at every hop.

Internal issues have it worse: a pentest finding, a misconfiguration or an in-house bug has no CVE and no common format at all.

**CIR is a YAML record format that normalizes how a security issue is described and communicated**, for public vulnerabilities and internal ones alike.

CIR does **not** replace existing standards. It references and consumes them (CVE, GHSA, OSV, CVSS, CWE, EPSS, CISA KEV, MITRE ATT&CK) and adds the data they don't carry: threat intelligence, security posture and organizational context.

## The 4-layer model

A CIR record is split into four layers. Each layer carries its own TLP marking, so a record can be shared with a given audience simply by filtering out the layers they are not allowed to see.

```
┌──────────────────────────────────────────────────────────┐
│ 4. CONTEXT         org only               TLP:RED        │
│    affected assets, real exposure, business impact,      │
│    decision (fix / mitigate / accept), owner, SLA        │
├──────────────────────────────────────────────────────────┤
│ 3. POSTURE         community (CERT, ISAC) TLP:AMBER      │
│    exploit prerequisites, detectability, compensating    │
│    controls, chaining, blast radius                      │
├──────────────────────────────────────────────────────────┤
│ 2. THREAT INTEL    public / community     TLP:CLEAR      │
│    exploits, in-the-wild activity, actors, campaigns,    │
│    ATT&CK, IOCs, EPSS, KEV, timeline                     │
├──────────────────────────────────────────────────────────┤
│ 1. CORE            public                 TLP:CLEAR      │
│    references (CVE...), products, CVSS, CWE, mitigations │
└──────────────────────────────────────────────────────────┘
  META: id, cir_version, revision, authors, history
```

| Layer | Purpose | Typical audience |
|---|---|---|
| `core` | What the issue is. References existing identifiers, never redefines them. | Public |
| `threat_intel` | Who exploits it, how, and since when. | Public or community |
| `posture` | How the issue behaves in real environments, in generic terms. | Group CERT, sector ISAC |
| `context` | What it means for one organization and what was decided. | The organization only |

### Sharing rules

- Scores are **computed, never typed in**: a public priority from `core` + `threat_intel`, and an organizational risk from all four layers (see [Scoring](./SPEC.md#scoring)).
- **Public issues** have a `core` layer pointing to their CVE/GHSA. **Internal issues** use exactly the same structure, without external references and with a restrictive TLP.
- The `posture` layer is designed to be shared with a group or sector CERT **without leaking the `context` layer**. A CERT can aggregate posture data from many entities on the same CIR ("most entities mitigate through segmentation") without ever seeing which assets are affected.
- The `posture` layer must stay **generic and qualitative**: no hostnames, product names, rule names or asset counts. Enumerated values are preferred over free text so sensitive details don't slip in by accident.

## Identifier

```
CIR-YYYY-CODE-NNNN
```

| Part | Example | Meaning |
|---|---|---|
| `CIR` | | Constant prefix |
| `YYYY` | `2026` | Year of disclosure or discovery |
| `CODE` | `00`, `0CERTFR`, `LAB` | Issuer code, see below |
| `NNNN` | `0001` | Sequential number (4 digits minimum), unique within the code |

The first character of `CODE` decides whether a record is public:

| Code | Meaning |
|---|---|
| `00` | Root authority (the CIR project) |
| `0` + 1 to 7 alphanumerics, e.g. `0CERTFR` | Registered public authority, listed in [`authorities.yml`](./authorities.yml) |
| Anything not starting with `0`, e.g. `LAB`, `SNOW`, `P01` | Internal code, freely managed by the organization (not globally unique) |

Public authorities are added to the registry through a pull request reviewed by the maintainers. Validators reject a public code that is not in the registry.

## Template

The full template, with every field, is in [`cir.yml`](./cir.yml). The field-level specification is in [`SPEC.md`](./SPEC.md).

## Roadmap

- [x] Field-level specification (types, enums, required fields)
- [ ] JSON Schema as the source of truth
- [x] Scoring model: `cir-risk/0.1`
- [x] Examples: [`examples/`](./examples/)
- [ ] Reference CLI: validate, score, export by TLP
