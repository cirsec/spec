# python tests/validate.py [schema] [records...]
# Validates CIR records against cir.schema.json; defaults to every example.
# A file named *.bad.yml must fail. Dates stay strings, like js-yaml's CORE schema.
import glob, json, sys, yaml
from jsonschema import Draft202012Validator
class L(yaml.SafeLoader): pass
L.yaml_implicit_resolvers = {k: [r for r in v if r[0] != 'tag:yaml.org,2002:timestamp'] for k, v in L.yaml_implicit_resolvers.items()}
args = sys.argv[1:] or ['cir.schema.json'] + sorted(glob.glob('examples/*.yml'))
schema = json.load(open(args[0])); Draft202012Validator.check_schema(schema); v = Draft202012Validator(schema)
bad = 0
for f in args[1:]:
    errs = sorted(v.iter_errors(yaml.load(open(f), L)), key=lambda e: list(e.path))
    want_fail = '.bad.' in f
    print(('FAIL ' if bool(errs) != want_fail else 'ok   ') + f.split('/')[-1], [f"{'/'.join(map(str, e.path))}: {e.message[:90]}" for e in errs][:4])
    bad += bool(errs) != want_fail
sys.exit(bad)
