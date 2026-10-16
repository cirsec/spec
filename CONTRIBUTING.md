# Contributing

CIR is an open specification carried by [Hack in the Shell](https://hackintheshell.org), a French association. It gets better when it is tried on real issues: the most useful contribution is a record that does not fit.

## Report what does not fit

Open an [issue](https://github.com/cirsec/spec/issues) with:

- the situation (a real issue, anonymized if needed),
- what you tried to write in the record,
- what the format would not let you say, or let you say in two ways.

An issue is enough. You do not need to propose the fix.

## Propose a change

1. **Discuss it first in an issue**, unless it is a typo or a broken link. A format change affects every tool that reads CIR.
2. **Open a pull request** that changes, together:
   - [`SPEC.md`](./SPEC.md), the reference;
   - [`cir.schema.json`](./cir.schema.json), so tools can check the new rule;
   - [`cir.yml`](./cir.yml) and the [examples](./examples/) when a field is added or renamed;
   - [`CHANGELOG.md`](./CHANGELOG.md), under the next version, marked **Breaking** if an existing record could become invalid.
3. **Checks pass**: every example validates against the schema (`python tests/validate.py`).
4. **A maintainer reviews and merges.** Maintainers decide what goes in a version.

Rules of thumb for a change:

- **Reference, don't redefine.** If CVE, CVSS, CWE, OSV, VEX, ATT&CK or TLP already carry it, point to it.
- **Enums over free text**, and in `posture`, enums only.
- **One way to say one thing.**

## Become a public authority

Add your entry to [`authorities.yml`](./authorities.yml) with your OpenPGP signing key, in a pull request. The steps are on [cirsec.org/authorities](https://cirsec.org/authorities#apply).

## Versions

The format is a draft: `cir_version` follows the specification version, and a minor version can still break records while the draft lasts. Each version is listed in [`CHANGELOG.md`](./CHANGELOG.md) with what to do about breaking changes.

## License

Contributions are accepted under the [Apache 2.0](./LICENSE) license of the repository.
