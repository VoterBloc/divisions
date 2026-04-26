# Division Schema

This document defines the YAML schema used in this repository to describe
[Open Civic Data (OCD)](https://opencivicdata.readthedocs.io/) divisions in
the **United States**: geographic / governmental entities like states,
counties, congressional districts, cities, school districts, and wards.

The repo is scoped to the US. OCD ids still use the canonical
`ocd-division/country:us/...` form for compatibility with the broader OCD
ecosystem, but the file layout assumes a single country.

The schema is intentionally stack-agnostic and aims to be useful to any
organization that needs a curated, hand-verifiable dataset of US civic
divisions. Organization-specific data belongs in the `extras` map or as
entries in the `ids` map so the canonical record stays portable.

## Relationship to Open Civic Data

This repo builds on, and is complementary to, the
[Open Civic Data (OCD)](https://open-civic-data.readthedocs.io/) ecosystem:

- **Identifiers** are [OCD division ids](https://open-civic-data.readthedocs.io/en/latest/ocdids.html)
  as defined by [OCDEP 2](https://open-civic-data.readthedocs.io/en/latest/proposals/0002.html).
  We don't mint new ids — we annotate the ones maintained in
  [`opencivicdata/ocd-division-ids`](https://github.com/opencivicdata/ocd-division-ids).
- **`sameAs` / `validFrom` / `validThrough`** carry the same meaning here as
  in OCDEP 2.
- OCD's own division [*object*](https://open-civic-data.readthedocs.io/en/latest/data/division.html)
  has only a handful of fields (id, country, display_name, geometries,
  children). This schema extends well beyond that with hand-curated
  governance/elections metadata. OCD-level fields stay canonical; everything
  else is our annotation.
- We use `name` (matching the openstates/people convention) where OCD uses
  `display_name` — they carry the same meaning.

## Scope — what belongs in a file

This repo is for **hand-curated** data that is otherwise **hard to source
programmatically**. The core value-add is:

- Governance structure (body names, number of seats, which offices are elected vs. appointed).
- Election administration contacts (office name, URL, phone, address).
- Prose summaries, mottos, nicknames, demonyms.
- Curated external identifiers and links.
- Attributable sources.

Data that is already available from official imports — population, area,
FIPS / GEOID, boundary geometries, established dates from Wikidata — is
*permitted* in every record but **never required**. Downstream consumers
should prefer their authoritative source (e.g. Census ACS, TIGER shapefiles)
over values in this repo for those fields. Include them here only when the
canonical source is wrong, ambiguous, or inconvenient.

## File layout

Files are stored under `data/` and their location on disk is derived from
the OCD division id:

```
data/
  us.yml                                   # ocd-division/country:us
  ca/
    state.yml                              # .../state:ca
    county/
      butte.yml                            # .../state:ca/county:butte
    cd/
      1.yml                                # .../state:ca/cd:1
    sldu/
      4.yml                                # .../state:ca/sldu:4
    sldl/
      3.yml                                # .../state:ca/sldl:3
    place/
      chico.yml                            # .../state:ca/place:chico
    school_district/
    judicial/
    ward/
    precinct/
```

- The US country record is `data/us.yml`.
- State records live at `data/{state}/state.yml` (`{state}` is the postal
  abbreviation, lowercased — `ca`, `tx`, `dc`, …).
- Each child type lives in a directory **named for the OCD type verbatim**
  (singular, matching the `<type>:<id>` segment in the OCD id): `county/`,
  `place/`, `cd/`, `sldu/`, `sldl/`, `school_district/`, `ward/`, etc.
- The filename (minus `.yml`) **must equal the OCD id's final-segment slug
  exactly** — no leading zeros, no transformation. OCDEP 2 strips leading
  zeros from numeric ids (`cd:1`, not `cd:01`), so `cd/1.yml` is correct.

Deeply nested divisions (wards within a place, precincts within a county)
currently flatten to `data/{state}/{type}/{parent_slug}-{number}.yml`.
This rule may be revisited as ward/precinct data grows.

## Fields

### Universal required fields

| Field  | Type   | Notes                                                     |
| ------ | ------ | --------------------------------------------------------- |
| `id`   | string | OCD division id, e.g. `ocd-division/country:us/state:ca`. |
| `name` | string | Canonical display name, e.g. "California".               |
| `type` | enum   | See [Types](#types) below.                                |

### Universal optional fields

| Field        | Type                | Notes                                                                                                        |
| ------------ | ------------------- | ------------------------------------------------------------------------------------------------------------ |
| `short_name` | string              | Terser display form (e.g. "LA County", "CA-33").                                                             |
| `parent`     | string              | OCD id of the immediate parent. If omitted the linter derives it from `id`.                                  |
| `aliases`    | list\[string]       | Alternate names the division is known by.                                                                    |
| `summary`    | string              | Prose paragraph describing the division. Recommended for consumer pages.                                     |
| `demonym`    | string              | e.g. "Californian", "Angeleno".                                                                              |
| `nicknames`  | list\[string]       | e.g. \["Golden State"].                                                                                      |
| `motto`      | string              | Official motto.                                                                                              |
| `website`    | string (url)        | Official government homepage.                                                                                |
| `timezone`   | string              | IANA tz name, e.g. `America/Los_Angeles`.                                                                    |
| `timezones`  | list\[string]       | When multiple zones apply.                                                                                   |
| `flag`       | string (url)        | URL to flag image.                                                                                           |
| `seal`       | string (url)        | URL to seal image.                                                                                           |
| `image`      | string (url)        | General representative image.                                                                                |
| `capital`    | string              | Capital city. Use for `country`, `state`, `territory`. Name or OCD id.                                       |
| `seat`       | string              | County seat. Use for `county`. Name or OCD id.                                                               |
| `established`| date                | ISO 8601 (`YYYY-MM-DD`). Optional — Wikidata often has this.                                                 |
| `dissolved`  | date                | Date the division ceased to exist, if applicable.                                                            |
| `valid_from` | date                | OCDEP 2 `validFrom` — when this division became valid.                                                       |
| `valid_through` | date             | OCDEP 2 `validThrough` — when this division ceased to be valid.                                              |
| `same_as`    | list\[object]       | OCDEP 2 `sameAs` entries: `{id, note}`. Use for consolidated city-counties (SF, Denver, Nashville, …).       |
| `other_names`| list\[object]       | Historical / alternate names: `{name, start_date?, end_date?}`. Same shape as openstates/people.             |
| `jurisdiction` | string            | OCD **jurisdiction** id (`ocd-jurisdiction/...`) for the governing body — distinct from the division id.     |
| `governance` | object              | Structure of government. See [governance](#governance). **High value — curate when known.**                  |
| `elections`  | object              | Election-administration contact. See [elections](#elections). **High value — curate when known.**            |
| `direct_democracy` | object        | State-level: does the state allow citizen initiative / referendum / recall. See [direct_democracy](#direct_democracy). |
| `elections_policy` | object        | State-level election *procedures* (runoff rules, etc.). See [elections_policy](#elections_policy). Distinct from `elections` (admin contact). |
| `voter_registration` | object      | State-level voter-registration policy (AVR, online, same-day). See [voter_registration](#voter_registration). |
| `civic_urls` | object              | Deterministic keys for the most common voter-facing URLs (register, check registration, polling place, ballot tracker, sample ballot). See [civic_urls](#civic_urls). |
| `contacts`   | list\[object]       | General contacts. See [contacts](#contacts).                                                                 |
| `population` | object              | Optional; census sources preferred. See [population](#population).                                           |
| `area`       | object              | Optional; TIGER sources preferred. See [area](#area).                                                        |
| `boundary`   | object              | Optional pointer to boundary source. See [boundary](#boundary).                                              |
| `ids`        | map\[string,string] | External identifiers. See [ids](#ids).                                                                       |
| `links`      | list\[object]       | See [links and sources](#links-and-sources).                                                                 |
| `sources`    | list\[object]       | Where information in this file was sourced from. **Every file should have at least one entry.**              |
| `extras`     | object              | Unvalidated free-form map. Namespace keys when open-sourcing (e.g. `voterbloc.foo`).                         |

### Type-specific required fields

The linter enforces only these beyond the universal requireds. Everything
else is optional.

| Type              | Additional required                                    |
| ----------------- | ------------------------------------------------------ |
| `state`           | `abbreviation` (postal code, e.g. `CA`).               |
| `cd`              | `number` (string — `"AL"` for at-large is allowed).    |
| `sldu`            | `number`.                                              |
| `sldl`            | `number`.                                              |
| `ward`            | `place` (OCD id of containing place), `number`.        |
| `precinct`        | `number`; one of `place` or `county`.                  |

All other types validate against universal requireds only.

### Types

The `type` enum corresponds to the final segment of the OCD id
(`ocd-division/country:us/state:ca/county:los_angeles` → `county`).

Currently recognized:

`country`, `state`, `territory`, `district`, `county`, `parish`, `borough`,
`cd`, `sldu`, `sldl`, `place`, `school_district`, `judicial`, `ward`,
`precinct`.

Additional values pass through the linter as-is. Prefer adding new types here
in a PR when they become common enough to warrant type-specific validation.

### governance

Describes how the division is governed. All keys optional — fill in what's
known and verifiable. The `elected_offices` map is an open map of
`office_name → bool` so each division can list the offices that actually
exist there.

```yaml
governance:
  form: board-of-supervisors          # board-of-supervisors, mayor-council, council-manager, commission, ...
  body_name: Board of Supervisors     # "Board of Supervisors", "City Council", "Commissioners Court"
  seats: 5
  term_years: 4
  term_limit: 12                      # integer years (cumulative) if limits apply; null when unknown
  has_term_limits: true               # explicit — decouples "no limits" from "not yet curated"
  partisan: false                     # are local races partisan on the ballot?
  at_large: false                     # e.g. single at-large CD, or place electing councilmembers at-large
  elected_offices:
    # Free-form map of office → whether the office is elected (vs. appointed).
    # Use snake_case keys. Include only offices that exist in this division.
    executive: false                  # e.g. elected county executive / mayor
    sheriff: true
    district_attorney: true
    assessor: true
    clerk_recorder: true
    treasurer_tax_collector: true
    auditor_controller: true
    superintendent_of_schools: true
    coroner: false                    # e.g. merged with sheriff
    # State-level:
    attorney_general: true
    secretary_of_state: true
  # State-only niceties:
  upper_chamber: Senate
  lower_chamber: Assembly
  is_unicameral: false                # true only for Nebraska
  executive:
    has_lt_governor: true             # false for AZ, ME, NH, NJ (no LG), etc.
    lt_gov_joint_ticket: true         # governor + LG run on one ticket
  # Place-only niceties:
  mayor_elected: true
```

### direct_democracy

State-level only. Does the state permit citizens to place items directly on
the ballot? These are well-tracked state facts (NCSL, Ballotpedia).

```yaml
direct_democracy:
  citizen_initiative: true            # citizens can put new laws on the ballot
  citizen_referendum: true            # citizens can put existing laws to a referendum vote
  recall: true                        # elected officials can be recalled by petition
```

Leave any field absent when unknown (don't set `false` for "not yet curated").

### elections_policy

State-wide election *procedures*. Distinct from `elections` (which is the
admin-contact block).

```yaml
elections_policy:
  runoff: false                       # majority-required runoff elections
  primary_type: open                  # closed | semi-closed | open | top-two | top-four | blanket
  vote_by_mail: no-excuse             # universal | no-excuse | excuse-required
  early_voting: true                  # in-person early voting
  ranked_choice: false                # RCV used in any state-level elections
```

`primary_type` values:
- `closed` — only registered party members can vote in that party's primary
- `semi-closed` — party members + unaffiliated can vote
- `open` — any voter can vote in any party's primary (pick on election day)
- `top-two` — all candidates on one primary ballot, top 2 advance (CA, WA)
- `top-four` — top 4 advance to an RCV general (AK)
- `blanket` — voter picks candidates in any party for any office (rare)

`vote_by_mail` values:
- `universal` — every registered voter is automatically mailed a ballot
- `no-excuse` — any voter can request a mail ballot for any reason
- `excuse-required` — voter must provide a listed excuse (traditional absentee)

### voter_registration

State voter-registration policies — tracked by NCSL and the Brennan Center.

```yaml
voter_registration:
  automatic: true                     # automatic voter registration (AVR) — typically via DMV
  online: true                        # online voter registration available
  same_day: true                      # same-day / election-day registration
  min_age: 18
  pre_registration_age: 16            # null if the state doesn't allow pre-registration
  registration_deadline_days: 15      # days before election (mail/postmark); moot if same_day is true
  voter_id_requirement: non_photo     # strict_photo | photo | non_strict_photo | non_photo | none
  felon_restoration: automatic_upon_release
```

`voter_id_requirement` values (per NCSL classification):
- `strict_photo` — photo ID required; voters without ID are turned away or vote provisionally
- `photo` — photo ID required but alternatives exist (affidavit, etc.)
- `non_strict_photo` — photo ID requested but other IDs or signatures accepted
- `non_photo` — any ID accepted, photo not required
- `none` — no ID required to vote

`felon_restoration` values:
- `automatic_upon_release` — voting rights restored automatically on release from prison
- `upon_completion` — rights restored after the full sentence is served (parole/probation ended)
- `application_required` — must apply / petition for restoration
- `never` — permanent disenfranchisement for some felonies
- `no_disenfranchisement` — felons always retain the right to vote (ME, VT, DC)

### civic_urls

A small, deterministic map of voter-facing URLs. Consumers that want to
answer "where do I register in CT?" shouldn't have to string-match on
free-form notes in `links:`. Every key is optional; add what the state
provides.

```yaml
civic_urls:
  register_to_vote: https://voterregistration.ct.gov/       # OVR entry point
  register_by_mail: https://.../voter-registration-form.pdf # paper form or "request a form" page
  check_registration: https://portal.ct.gov/.../voter-lookup
  find_polling_place: https://...
  request_absentee_ballot: https://...
  track_ballot: https://...
  sample_ballot: https://...
  voter_id_info: https://...           # what IDs are accepted at the polls
  elections_calendar: https://...      # upcoming election dates / calendar
  election_results: https://...        # official results portal / archive
  military_overseas_voting: https://...  # UOCAVA / military and overseas voter resources hub
```

`register_to_vote` is for true online registration (fill out and submit on
the site). `register_by_mail` is for downloadable paper forms or "request
a form" portals. A few states (AL, AR) have the latter without the former.

Put URLs that don't fit one of these keys in `links:`.

### elections

Contact information for the office that administers elections in this
division. This is one of the highest-value fields in the repo — it is
frequently needed by consumers and is not easily sourced in bulk.

```yaml
elections:
  office_name: Butte County Clerk-Recorder/Registrar of Voters
  office_url: https://clerk-recorder.buttecounty.net/elections
  office_phone: "(530) 552-3400"
  office_email: elections@buttecounty.net
  office_address: |
    155 Nelson Ave
    Oroville, CA 95965
```

### contacts

General-purpose contacts when `elections` isn't the right bucket. Field
shape mirrors openstates/people offices: each entry has an optional
`classification` (`primary`, `capitol`, `district`, `admin`, `elections`, …)
plus `note`, `address`, `voice`, `fax`, `email`.

```yaml
contacts:
  - classification: primary
    note: Main county office
    address: "25 County Center Drive, Oroville, CA 95965"
    voice: "(530) 538-7631"
```

### other_names

Alternate / historical names the division has been known by. Shape matches
openstates/people; `start_date` and `end_date` are optional.

```yaml
other_names:
  - name: Shannon County
    end_date: 2015-05-01
  - name: Oglala Lakota County
    start_date: 2015-05-01
```

### same_as

Used when the OCD-IDs project maintains aliases (typically consolidated
city-counties such as San Francisco, Denver, Nashville, New Orleans).

```yaml
same_as:
  - id: ocd-division/country:us/state:ca/place:san_francisco
    note: consolidated city-county
```

### jurisdiction

Optional pointer to the OCD *jurisdiction* id — the governing body tied to
this division, per [OCDEP 3](https://open-civic-data.readthedocs.io/en/latest/proposals/0003.html).
Handy for joining with openstates tooling that indexes on
`ocd-jurisdiction/...`.

```yaml
jurisdiction: ocd-jurisdiction/country:us/state:ca/place:los_angeles/government
```

### population

Optional. Prefer census imports downstream.

```yaml
population:
  count: 206309
  year: 2023
  source: census-acs-5yr
```

### area

Optional. Prefer TIGER/census sources downstream. Include either the
imperial (`_sqmi`) or metric (`_sqkm`) pair.

```yaml
area:
  land_sqmi: 1636.43
  water_sqmi: 31.7
  total_sqmi: 1668.13
```

### boundary

Optional pointer to an authoritative boundary source. Geometries are not
stored inline.

```yaml
boundary:
  source: https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/
  year: 2023
  geometry: https://example.org/butte_county.geojson
```

### ids

Free-form map of external identifiers. The linter does not enforce keys,
but please prefer these conventional names so consumers can join data
easily. Most are drawn from the OCD-IDs US CSV and
[`unitedstates/congress-legislators`](https://github.com/unitedstates/congress-legislators).

**Census / FIPS / GNIS.** Match OCD-IDs column names where they exist.

| Key                 | Meaning                                                       |
| ------------------- | ------------------------------------------------------------- |
| `census_geoid`      | Census GEOID (2020 vintage).                                  |
| `census_geoid_12`   | GEOID (2012 vintage). Include for redistricted CDs/SLDs.      |
| `census_geoid_14`   | GEOID (2014 vintage).                                         |
| `fips`              | Combined FIPS (legacy; prefer the split keys below).          |
| `fips_state`        | 2-digit state FIPS.                                           |
| `fips_county`       | 3-digit county FIPS.                                          |
| `fips_place`        | 5-digit place FIPS.                                           |
| `fips_cousub`       | County subdivision FIPS.                                      |
| `ansi`              | Census / USGS ANSI code.                                      |
| `gnis`              | USGS GNIS id for named places.                                |
| `nces`              | NCES / LEA id for school districts (OCD's `sch_dist_stateid`). |
| `osm_relation`      | OpenStreetMap relation id.                                    |

**Open Civic Data / legislative.**

| Key                       | Meaning                                                   |
| ------------------------- | --------------------------------------------------------- |
| `openstates_district`     | openstates district slug (matches OCD-IDs column).        |
| `openstates_jurisdiction` | `ocd-jurisdiction/...` for the governing body.            |

**Legislator / CD references.**

| Key          | Meaning                                                           |
| ------------ | ----------------------------------------------------------------- |
| `bioguide`   | Bioguide id (Congress).                                           |
| `govtrack`   | GovTrack id.                                                      |
| `thomas`     | THOMAS id (legacy; archival).                                     |
| `opensecrets`| OpenSecrets id (for CDs).                                         |

**General reference.**

| Key          | Meaning                                          |
| ------------ | ------------------------------------------------ |
| `wikidata`   | Q-id (e.g. `Q108046`).                           |
| `wikipedia`  | Wikipedia page title (spaces allowed).           |
| `dbpedia`    | DBpedia resource name.                           |
| `ballotpedia`| Ballotpedia page slug.                           |
| `google_kg`  | Google Knowledge Graph entity id.                |
| `votesmart`  | Project Vote Smart id.                           |

```yaml
ids:
  wikidata: Q108046
  wikipedia: Butte County, California
  ballotpedia: Butte_County,_California
  census_geoid: "05000US06007"
  fips_state: "06"
  fips_county: "007"
  osm_relation: "396486"
```

Additional, non-conventional identifiers can still be added; the list above
is a vocabulary recommendation, not a restriction.

### links and sources

```yaml
links:
  - url: https://www.buttecounty.net
    note: County homepage

sources:
  - url: https://en.wikipedia.org/wiki/Butte_County,_California
    note: general reference
    accessed: 2026-04-20
```

Every file should have at least one `sources` entry — this repo's value is
that its data is traceable.

## OCD id / file-path consistency

The linter checks that:

1. `id` parses as a valid OCD division id.
2. The id's final-segment type matches `type`.
3. The file path matches the id (country, state, pluralized type dir, slug,
   with zero-padding for numeric districts).
4. `parent`, if set, equals the OCD id with its last segment stripped.

## Example: Butte County, CA

```yaml
id: ocd-division/country:us/state:ca/county:butte
name: Butte County
type: county

seat: Oroville
demonym: Buttean
summary: >
  Butte County is in northern California's Sacramento Valley and Sierra
  Nevada foothills. The county seat is Oroville; its largest city is Chico.

website: https://www.buttecounty.net

governance:
  form: board-of-supervisors
  body_name: Board of Supervisors
  seats: 5
  partisan: false
  elected_offices:
    sheriff: true
    district_attorney: true
    assessor: true
    clerk_recorder: true
    treasurer_tax_collector: true
    auditor_controller: true
    superintendent_of_schools: true

elections:
  office_name: Butte County Clerk-Recorder/Registrar of Voters
  office_url: https://clerk-recorder.buttecounty.net/elections
  office_phone: "(530) 552-3400"

ids:
  wikidata: Q108046
  fips: "06007"
  geoid: "06007"
  ballotpedia: Butte_County,_California

links:
  - url: https://www.buttecounty.net
    note: County homepage
  - url: https://clerk-recorder.buttecounty.net/elections
    note: Elections office

sources:
  - url: https://www.buttecounty.net
    note: official county website
  - url: https://en.wikipedia.org/wiki/Butte_County,_California
    note: general reference
```
