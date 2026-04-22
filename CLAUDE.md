# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Hand-curated YAML metadata for US [OCD divisions](https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html) —
states, counties, congressional districts, places, state-leg districts,
school districts, wards, precincts. One file per division, keyed by OCD
division id. Inspired by `openstates/people`.

**US-only.** Don't add country scoping for other nations.

## Commands

```sh
uv venv && uv pip install -e '.[dev]'   # set up
.venv/bin/pytest                        # run tests
.venv/bin/pytest tests/test_paths.py::test_parsed_parent_id   # single test
.venv/bin/divisions lint                # validate all YAML under data/
.venv/bin/divisions lint data/ca/state.yml
.venv/bin/divisions show <file.yml>     # print normalized JSON
.venv/bin/divisions path <ocd-id>       # print canonical file path for an id
.venv/bin/divisions schema              # regenerate schema/division.schema.json
```

## Architecture

The schema has **one canonical definition**: `src/divisions/models.py`
(pydantic). `SCHEMA.md` and `schema/division.schema.json` are downstream —
after changing a model, re-run `divisions schema` to refresh the JSON
Schema, and update `SCHEMA.md` by hand to keep the human-readable doc in
sync.

File paths are **derived mechanically** from OCD ids by
`src/divisions/paths.py`. The linter (`src/divisions/lint.py`) enforces
that every YAML's location matches its `id`. Rules:

- `data/us.yml` for the country.
- `data/{state}/state.yml` for a state (`{state}` is lowercased postal —
  `ca`, `dc`, …). DC uses OCD type `district` but lives at `data/dc/state.yml`.
- `data/{state}/{type}/{slug}.yml` for everything else. **The directory
  name is the OCD type segment verbatim (singular)** — `county/`, `place/`,
  `cd/`, `sldu/`, `school_district/`. Do not pluralize.
- The filename (minus `.yml`) is the OCD id's last-segment slug exactly —
  no leading zeros (`cd/1.yml`, never `cd/01.yml`), per OCDEP 2.
- Nested under a state-child (e.g. `place:new_york/council_district:36`)
  flattens to `{parent_slug}-{slug}.yml` in the leaf type's dir.

Use `divisions path <ocd-id>` rather than guessing.

## Schema conventions that are easy to get wrong

- **`capital` vs `seat`** — `capital` only for `country`, `state`,
  `territory`. `seat` only for `county`. Not interchangeable.
- **`same_as` is a list of `{id, note}`** (not a string). Use for
  consolidated city-counties (SF, Denver, Nashville, New Orleans).
- **`jurisdiction`** is an `ocd-jurisdiction/...` id (governing body), not
  an `ocd-division/...` id.
- **Type-specific required fields are intentionally minimal**: `state`
  requires `abbreviation`; `cd`/`sldu`/`sldl` require `number`; `ward`
  requires `place`+`number`; `precinct` requires `number` plus one of
  `place`/`county`. Nothing else is enforced beyond universal `id`/`name`/`type`.
- **`ids` map has a recommended vocabulary** (census_geoid, fips_state,
  fips_county, ansi, gnis, nces, bioguide, govtrack, wikidata, wikipedia,
  ballotpedia, osm_relation, openstates_jurisdiction, …). See SCHEMA.md's
  "ids" section. Linter does not enforce keys, but prefer these names.

## Scope — what belongs in a file

This repo is for data that is **hard to source programmatically**:
governance structure, `elected_offices` maps, election-administration
contacts (`elections` block), prose `summary`, mottos, nicknames, demonyms,
curated identifiers and links.

Fields like `population`, `area`, `fips`, `boundary`, `established` *exist*
in the schema but should be left empty unless the census / wikidata source
is wrong or missing. Consumers of this data should prefer census/TIGER for
those facts. Don't spend curation effort on them.

Every file should have at least one `sources:` entry. The linter emits a
soft warning when missing.

## PR / edit discipline

- Minimize diffs. Don't reorder fields or reflow YAML when fixing a
  single value.
- New division files must be populated with real verifiable data — no
  stubs. Cite sources.
- OCD ids themselves require rough consensus (see OCDEP 2). Before adding
  a file under a new `type:` segment, confirm the id exists in
  [`opencivicdata/ocd-division-ids`](https://github.com/opencivicdata/ocd-division-ids)
  or flag it for discussion.

## License

TBD — README notes CC0 is the recommended default (matching
`openstates/people` and OCDEP 2).
