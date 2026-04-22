"""Pydantic models for the division YAML schema.

This is the canonical definition of the schema. The JSON Schema committed at
`schema/division.schema.json` is regenerated from these models.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from divisions.paths import parse_ocd_id

# ---------------------------------------------------------------------------
# Known division types. Others are permitted — validation still runs, but no
# type-specific required-field checks are enforced.
# ---------------------------------------------------------------------------

KNOWN_TYPES: set[str] = {
    "country",
    "state",
    "territory",
    "district",
    "county",
    "parish",
    "borough",
    "cd",
    "sldu",
    "sldl",
    "place",
    "school_district",
    "judicial",
    "ward",
    "precinct",
    "council_district",
    "anc",
    "hoa",
    "ed",
}

# Keys in governance.elected_offices are free-form. This set is used only to
# spell-check / autocomplete in editor tooling; unknown keys pass.
KNOWN_ELECTED_OFFICES: set[str] = {
    "executive",
    "sheriff",
    "district_attorney",
    "assessor",
    "clerk_recorder",
    "clerk",
    "recorder",
    "treasurer",
    "treasurer_tax_collector",
    "tax_collector",
    "auditor",
    "auditor_controller",
    "controller",
    "superintendent_of_schools",
    "coroner",
    "public_defender",
    "registrar_of_voters",
    "surveyor",
}

DivisionType = str  # kept loose — enforced in validator against KNOWN_TYPES


# ---------------------------------------------------------------------------
# Sub-objects
# ---------------------------------------------------------------------------


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class _BaseAllowExtra(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class Link(_Base):
    url: HttpUrl
    note: str | None = None


class Source(_Base):
    url: HttpUrl
    note: str | None = None
    accessed: date | None = None


class Contact(_Base):
    classification: str | None = None  # primary, capitol, district, admin, elections, ...
    note: str | None = None
    address: str | None = None
    voice: str | None = None
    fax: str | None = None
    email: str | None = None


class SameAs(_Base):
    id: str
    note: str | None = None

    @field_validator("id")
    @classmethod
    def _valid_ocd_id(cls, v: str) -> str:
        parse_ocd_id(v)
        return v


class OtherName(_Base):
    name: str
    start_date: date | None = None
    end_date: date | None = None


class Elections(_Base):
    office_name: str | None = None
    office_url: HttpUrl | None = None
    office_phone: str | None = None
    office_email: str | None = None
    office_address: str | None = None


class ExecutiveStructure(_Base):
    """State / territory / district executive branch shape."""

    has_lt_governor: bool | None = None
    lt_gov_joint_ticket: bool | None = None  # meaningful only if has_lt_governor


class Governance(_BaseAllowExtra):
    form: str | None = None
    body_name: str | None = None
    seats: int | None = None
    term_years: int | None = None
    term_limit: int | None = None
    has_term_limits: bool | None = None
    partisan: bool | None = None
    at_large: bool | None = None
    elected_offices: dict[str, bool] | None = None

    # State-only niceties:
    upper_chamber: str | None = None
    lower_chamber: str | None = None
    is_unicameral: bool | None = None
    executive: ExecutiveStructure | None = None

    # Place-only niceties:
    mayor_elected: bool | None = None


class DirectDemocracy(_Base):
    """Does the state permit citizens to place items on the ballot?"""

    citizen_initiative: bool | None = None
    citizen_referendum: bool | None = None
    recall: bool | None = None


class ElectionsPolicy(_Base):
    """State-wide election procedures (vs. `elections` which is admin contact)."""

    runoff: bool | None = None


class VoterRegistration(_Base):
    """State voter-registration policies."""

    automatic: bool | None = None  # AVR
    online: bool | None = None
    same_day: bool | None = None  # SDR / EDR


class Population(_Base):
    count: int | None = None
    year: int | None = None
    source: str | None = None


class Area(_Base):
    land_sqmi: float | None = None
    water_sqmi: float | None = None
    total_sqmi: float | None = None
    land_sqkm: float | None = None
    water_sqkm: float | None = None
    total_sqkm: float | None = None


class Boundary(_Base):
    source: HttpUrl | None = None
    year: int | None = None
    geometry: HttpUrl | None = None


# ---------------------------------------------------------------------------
# Division model
# ---------------------------------------------------------------------------


class Division(_Base):
    """A civic division — state, county, CD, place, etc."""

    # --- universal required -----------------------------------------------
    id: str
    name: str
    type: str

    # --- universal optional -----------------------------------------------
    short_name: str | None = None
    parent: str | None = None
    aliases: list[str] = Field(default_factory=list)
    summary: str | None = None

    demonym: str | None = None
    nicknames: list[str] = Field(default_factory=list)
    motto: str | None = None

    website: HttpUrl | None = None
    timezone: str | None = None
    timezones: list[str] = Field(default_factory=list)

    flag: HttpUrl | None = None
    seal: HttpUrl | None = None
    image: HttpUrl | None = None

    capital: str | None = None  # for country / state / territory
    seat: str | None = None  # for county (the county seat)

    established: date | None = None
    dissolved: date | None = None
    valid_from: date | None = None
    valid_through: date | None = None
    same_as: list[SameAs] = Field(default_factory=list)
    other_names: list[OtherName] = Field(default_factory=list)
    jurisdiction: str | None = None  # ocd-jurisdiction/...

    governance: Governance | None = None
    elections: Elections | None = None
    direct_democracy: DirectDemocracy | None = None
    elections_policy: ElectionsPolicy | None = None
    voter_registration: VoterRegistration | None = None
    contacts: list[Contact] = Field(default_factory=list)

    population: Population | None = None
    area: Area | None = None
    boundary: Boundary | None = None

    ids: dict[str, str] = Field(default_factory=dict)
    links: list[Link] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)

    extras: dict[str, Any] = Field(default_factory=dict)

    # --- type-specific optional (validated for presence below as needed) --
    iso_3166_1: str | None = None  # for country
    iso_3166_2: str | None = None  # e.g. US-CA
    abbreviation: str | None = None  # postal code for state
    fips: str | None = None  # optional everywhere
    number: str | None = None  # for cd/sldu/sldl/ward/precinct; string to allow "AL"
    cycle: int | None = None  # redistricting cycle (e.g. 2020)
    place: str | None = None  # parent OCD id for ward
    county: str | None = None  # parent OCD id for precinct (when applicable)
    district_type: str | None = None  # for school_district
    court_type: str | None = None  # for judicial

    # ----------------------------------------------------------------------
    # Validators
    # ----------------------------------------------------------------------

    @field_validator("id")
    @classmethod
    def _valid_ocd_id(cls, v: str) -> str:
        parse_ocd_id(v)  # raises on malformed
        return v

    @field_validator("parent")
    @classmethod
    def _valid_optional_ocd_id(cls, v: str | None) -> str | None:
        if v is None:
            return v
        parse_ocd_id(v)
        return v

    @field_validator("jurisdiction")
    @classmethod
    def _valid_jurisdiction_id(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.startswith("ocd-jurisdiction/"):
            raise ValueError(f"jurisdiction must start with 'ocd-jurisdiction/': {v!r}")
        return v

    @field_validator("type")
    @classmethod
    def _type_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("type must be a non-empty string")
        return v

    @model_validator(mode="after")
    def _check_consistency(self) -> Division:
        parsed = parse_ocd_id(self.id)

        # id leaf-segment type must match `type`
        if parsed.leaf_type != self.type:
            raise ValueError(
                f"id leaf segment type ({parsed.leaf_type!r}) does not match "
                f"type field ({self.type!r})"
            )

        # parent, if set, must match the derived parent id
        derived_parent = parsed.parent_id
        if self.parent is not None and self.parent != derived_parent:
            raise ValueError(
                f"parent ({self.parent!r}) does not match id-derived parent ({derived_parent!r})"
            )

        # type-specific required fields
        required = _TYPE_REQUIRED.get(self.type, ())
        missing = [f for f in required if getattr(self, f, None) in (None, "", [])]
        if missing:
            raise ValueError(f"type={self.type!r} requires field(s): {', '.join(missing)}")

        # ward/precinct parent consistency
        if self.type == "ward" and self.place is not None:
            parse_ocd_id(self.place)
        if self.type == "precinct":
            if self.place is None and self.county is None:
                raise ValueError("type=precinct requires one of `place` or `county`")

        return self


# Type-specific required fields. Intentionally minimal — most extra data is
# optional because it is often better sourced from Census/TIGER imports.
_TYPE_REQUIRED: dict[str, tuple[str, ...]] = {
    "state": ("abbreviation",),
    "cd": ("number",),
    "sldu": ("number",),
    "sldl": ("number",),
    "ward": ("number", "place"),
    "precinct": ("number",),
}
