# Contributing

Thanks for your interest in improving this dataset.

This repo is a hand-curated collection of YAML files, one per OCD division.
Contributions usually take one of two forms:

1. **Small corrections** — fixing a phone number, adding a source, updating
   a URL.
2. **Adding a new division** — curating a new county, place, district, etc.

Both are welcome. The repository is maintained for people, by people.

## Ground rules

- Curate, don't stub. Only add a file if you can populate real, verifiable
  data. A `sources` entry is expected on every file.
- Minimize edits. When correcting a file, touch only what's changing;
  don't re-order fields, reflow YAML, or sweep unrelated changes.
- Every fact should be attributable. Add a `sources:` entry linking to
  where you got the information.
- When in doubt, open an issue and ask before making the change.

## Setup

Requires Python 3.11+. Either `pip` + `venv` or [`uv`](https://docs.astral.sh/uv/)
works.

```sh
# with uv
uv venv
uv pip install -e '.[dev]'
source .venv/bin/activate

# or with pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Then install the pre-commit hook (optional but recommended):

```sh
pip install pre-commit
pre-commit install
```

## Workflow

### Fork & branch

1. Fork the repo on GitHub and clone your fork.
2. Create a branch per change: `git checkout -b fix-butte-elections-url`.

### Make the change

- For a correction: edit the relevant file under `data/`.
- For a new division: find its [OCD division id](https://github.com/opencivicdata/ocd-division-ids)
  first. The file path is derived mechanically from the id — the CLI will
  print it:

  ```sh
  divisions path ocd-division/country:us/state:ca/county:butte
  # → data/ca/county/butte.yml
  ```

  Create that file, populate the required fields, and add at least one
  `sources:` entry.

### Validate

Before committing, run the linter:

```sh
divisions lint
```

The linter checks:

- YAML parses
- Schema is valid (required fields present, types correct)
- The file path matches its `id`
- Type-specific required fields are present (see [SCHEMA.md](SCHEMA.md))

### Commit & PR

Write a descriptive commit message. For a data change, include:

- Which division you're changing and what changed
- Where you got the new information (should match the `sources:` entry
  you added)

Open a PR against `main`. In the description, re-state the provenance so
reviewers can verify the change without digging through the diff.

## Schema questions

Read [SCHEMA.md](SCHEMA.md) first. If a field you need doesn't exist:

- For one-off, organization-specific data, use the free-form `extras:`
  map. Namespace your keys (e.g. `extras.voterbloc.foo`) so the canonical
  record stays portable.
- If the field belongs in the core schema (another org would want it too),
  open an issue proposing the addition with 2–3 example divisions that
  would use it.

## Tests

If you change the schema, models, paths, or lint logic, add or update a
test in `tests/`:

```sh
pytest
```

## Data license

All data in this repository is released into the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
— see [LICENSE](LICENSE). This matches `openstates/people` and OCDEP 2's
own public-domain dedication. **By contributing you agree to waive all
copyright claims.**

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Be kind; assume good faith.
