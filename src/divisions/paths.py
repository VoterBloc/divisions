"""OCD id ↔ filesystem path mapping.

The repository stores one file per division, placed at a path derived from
its OCD division id. See SCHEMA.md for the layout rules this module encodes.

This repo is scoped to the United States. OCD ids still use the canonical
`ocd-division/country:us/...` form for ecosystem compatibility, but the
directory layout does not carry a per-country prefix.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

OCD_DIVISION_PREFIX = "ocd-division/"

# OCDEP 2 allows lowercase UTF-8 letters, numerals, period, hyphen,
# underscore, tilde. We approximate UTF-8 letters with \w (broad, allows
# accented characters when the Python regex engine is in unicode mode).
_TYPE_RE = r"[a-z][a-z0-9_-]*"
_ID_RE = r"[\w.\-~]+"
_SEGMENT_RE = re.compile(rf"^({_TYPE_RE}):({_ID_RE})$", re.UNICODE)

# Directory name is the OCD type verbatim (singular). State-like types live
# directly under their state dir as `state.yml` and have no dir of their own.
STATE_LIKE_TYPES = {"state", "district", "territory"}


@dataclass(frozen=True)
class OcdId:
    """Parsed OCD division id."""

    raw: str
    segments: tuple[tuple[str, str], ...]  # e.g. (('country', 'us'), ('state', 'ca'))

    @property
    def country(self) -> str:
        kind, value = self.segments[0]
        if kind != "country":
            raise ValueError(f"OCD id does not start with country: {self.raw}")
        return value

    @property
    def leaf_type(self) -> str:
        return self.segments[-1][0]

    @property
    def leaf_slug(self) -> str:
        return self.segments[-1][1]

    @property
    def parent_id(self) -> str | None:
        if len(self.segments) <= 1:
            return None
        parent_segs = self.segments[:-1]
        return OCD_DIVISION_PREFIX + "/".join(f"{k}:{v}" for k, v in parent_segs)

    def state_segment(self) -> tuple[str, str] | None:
        """Return the state-like segment (state/district/territory), if any."""
        for kind, value in self.segments:
            if kind in STATE_LIKE_TYPES:
                return kind, value
        return None


def parse_ocd_id(value: str) -> OcdId:
    """Parse an OCD division id. Raises ValueError if malformed."""
    if not value.startswith(OCD_DIVISION_PREFIX):
        raise ValueError(f"OCD id must start with {OCD_DIVISION_PREFIX!r}: {value!r}")
    rest = value[len(OCD_DIVISION_PREFIX) :]
    if not rest:
        raise ValueError(f"OCD id is empty after prefix: {value!r}")
    segments: list[tuple[str, str]] = []
    for i, segment in enumerate(rest.split("/")):
        m = _SEGMENT_RE.match(segment)
        if not m:
            raise ValueError(f"OCD id segment {i} is invalid: {segment!r} (in {value!r})")
        segments.append((m.group(1), m.group(2)))
    if segments[0][0] != "country":
        raise ValueError(f"OCD id must begin with country: {value!r}")
    if len(segments[0][1]) != 2 or not segments[0][1].isalpha():
        raise ValueError(
            f"OCD country code must be a 2-letter ISO-3166-1 alpha-2 code: {segments[0][1]!r}"
        )
    return OcdId(raw=value, segments=tuple(segments))


def dir_for_type(type_: str) -> str | None:
    """Return the subdirectory name for a given type (the OCD type verbatim),
    or None if the type sits directly under its state dir (as `state.yml`)."""
    if type_ in STATE_LIKE_TYPES:
        return None
    return type_


def id_to_path(ocd_id: str, data_root: Path | str = "data") -> Path:
    """Compute the canonical path on disk for an OCD division id.

    >>> id_to_path('ocd-division/country:us')
    PosixPath('data/us.yml')
    >>> id_to_path('ocd-division/country:us/state:ca')
    PosixPath('data/ca/state.yml')
    >>> id_to_path('ocd-division/country:us/state:ca/county:butte')
    PosixPath('data/ca/county/butte.yml')
    >>> id_to_path('ocd-division/country:us/state:ca/cd:1')
    PosixPath('data/ca/cd/1.yml')
    >>> id_to_path('ocd-division/country:us/district:dc/ward:8')
    PosixPath('data/dc/ward/8.yml')
    >>> id_to_path('ocd-division/country:us/state:ny/place:new_york/council_district:36')
    PosixPath('data/ny/council_district/new_york-36.yml')
    """
    root = Path(data_root)
    parsed = parse_ocd_id(ocd_id)
    segs = parsed.segments

    # country-only:  data/{cc}.yml
    if len(segs) == 1:
        return root / f"{segs[0][1]}.yml"

    state_seg = parsed.state_segment()

    # state-like only:  data/{state}/state.yml
    if len(segs) == 2 and segs[1][0] in STATE_LIKE_TYPES:
        return root / segs[1][1] / "state.yml"

    if state_seg is None:
        # Unusual: a child of country that isn't a state. Put it under
        # data/{type_dir}/{slug}.yml.
        type_, slug = segs[-1]
        subdir = dir_for_type(type_) or type_
        return root / subdir / f"{slug}.yml"

    state_kind, state_value = state_seg
    # segments beyond country + state
    remainder = [seg for seg in segs if seg != (state_kind, state_value)][1:]
    type_, slug = segs[-1]

    if len(remainder) == 1:
        subdir = dir_for_type(type_) or type_
        return root / state_value / subdir / f"{slug}.yml"

    # Nested under a state-child (e.g. place → ward / council_district).
    # Flatten as `{parent_slug}-{slug}.yml` in the leaf type's directory.
    _, parent_slug = remainder[-2]
    subdir = dir_for_type(type_) or type_
    return root / state_value / subdir / f"{parent_slug}-{slug}.yml"


def expected_path(ocd_id: str, data_root: Path | str = "data") -> Path:
    """Alias for id_to_path — returns where the file for this id belongs."""
    return id_to_path(ocd_id, data_root)
