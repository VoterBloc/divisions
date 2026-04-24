# divisions

A hand-curated, hand-verifiable dataset of Open Civic Data (OCD) divisions
in the United States — states, counties, congressional districts, places,
state legislative districts, school districts, wards, precincts — published
as YAML files keyed by [OCD division id](https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html).

This repo is deliberately narrow in focus. It covers civic data that is
**hard to source programmatically**: governance structure, which offices
are elected vs. appointed, election-administration contacts, curated
external identifiers, prose summaries. Data that is already canonical
elsewhere (population, area, FIPS codes, boundary geometries) is permitted
but optional — prefer the original source.

Inspired by [openstates/people](https://github.com/openstates/people).

## Quick links

- [SCHEMA.md](SCHEMA.md) — field definitions and layout rules
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to add or correct data
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Data layout

Files are stored under `data/` at paths derived mechanically from the OCD
division id. The state is the first directory; subsequent directories
match the OCD type segment verbatim (`county/`, `cd/`, `place/`, …).

```
data/
  us.yml                         # ocd-division/country:us
  ca/
    state.yml                    # ocd-division/country:us/state:ca
    county/butte.yml             # .../state:ca/county:butte
    cd/1.yml                     # .../state:ca/cd:1
    place/chico.yml              # .../state:ca/place:chico
```

See [SCHEMA.md](SCHEMA.md) for the full field list and layout rules.

## Working with the data

Requires Python 3.11+. Install with `pip install -e '.[dev]'` (or use
[`uv`](https://docs.astral.sh/uv/)):

```sh
uv venv
uv pip install -e '.[dev]'
```

Commands:

```sh
divisions lint                   # validate everything under data/
divisions lint data/ca/state.yml # validate a single file
divisions show data/ca/state.yml # print normalized JSON
divisions path ocd-division/country:us/state:ca/county:butte
# → data/ca/county/butte.yml
divisions schema                 # regenerate schema/division.schema.json
```

Tests:

```sh
pytest
```

## Relationship to Open Civic Data

This repo builds on and complements
[Open Civic Data](https://open-civic-data.readthedocs.io/):

- OCD division ids from
  [`opencivicdata/ocd-division-ids`](https://github.com/opencivicdata/ocd-division-ids)
  are the primary keys.
- [OCDEP 2](https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html)
  defines the id format; we follow it exactly.
- OCD's own division object is minimal (id, country, display_name,
  geometries, children). This repo adds the hand-curated governance /
  elections metadata OCD doesn't track.

## License

Public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) —
see [LICENSE](LICENSE). Matches `openstates/people` and OCDEP 2's own
public-domain dedication. By contributing you agree to waive all
copyright claims.

## Acknowledgements

- [openstates/people](https://github.com/openstates/people) — the direct
  structural inspiration for this repo.
- [opencivicdata/ocd-division-ids](https://github.com/opencivicdata/ocd-division-ids)
  — canonical id registry.
- [unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators)
  — conventional id scheme names adopted in our `ids` map.
