# Changelog

Every change to the format, newest first. While the format is a draft, a minor version can break records: each breaking change is marked **Breaking** with what to do about it.

## 0.5, 2026-10-15

- **Mirror records.** A `CODE` starting with `1` is a public mirror of an external database, generated automatically and never written by hand. `1CVE` mirrors every CVE: `CVE-YYYY-N` is `CIR-YYYY-1CVE-N`. A mirror only carries `meta`, `core` and `threat_intel`, all `CLEAR`. See [Mirror records](./SPEC.md#mirror-records).
- **Breaking: internal codes can no longer start with `1`.** The internal pattern is now `^CIR-\d{4}-[A-Z2-9][A-Z0-9]{1,7}-\d{4,}$`. Rename an internal code such as `1LAB` (e.g. to `LAB1`) and update the `based_on` fields that point to it.
- **JSON Schema.** [`cir.schema.json`](./cir.schema.json) (draft 2020-12) checks the structure of a record: fields, types, enums, patterns and conditional requirements. Rules that need computation or other files (CVSS score vs vector, date ordering, `sources[]` references, the authorities registry) stay with validators.
- `cir_version` is `"0.5"`.

## 0.1, 2026-10-12

First public draft.

- Four layers, each with its own TLP: `core`, `threat_intel`, `posture`, `context`. Sharing a record means dropping the layers an audience may not see.
- Identifiers `CIR-YYYY-CODE-NNNN`: codes starting with `0` are public authorities listed in [`authorities.yml`](./authorities.yml), with their OpenPGP signing key; anything else is internal.
- `meta.based_on`: an internal record extends a public one and inherits its `core` and `threat_intel`.
- `posture` holds no free text, no numbers and no names, so it can be aggregated by a CERT.
- Scoring method `cir-risk/0.1`: public priority and organizational risk, computed, never typed in.
- Full template [`cir.yml`](./cir.yml) and three [examples](./examples/).
