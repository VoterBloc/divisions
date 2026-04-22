from pathlib import Path

import pytest

from divisions.paths import expected_path, parse_ocd_id


@pytest.mark.parametrize(
    "ocd_id,expected",
    [
        ("ocd-division/country:us", Path("data/us.yml")),
        ("ocd-division/country:us/state:ca", Path("data/ca/state.yml")),
        (
            "ocd-division/country:us/state:ca/county:butte",
            Path("data/ca/county/butte.yml"),
        ),
        (
            "ocd-division/country:us/state:ca/cd:1",
            Path("data/ca/cd/1.yml"),
        ),
        (
            "ocd-division/country:us/state:ca/sldu:4",
            Path("data/ca/sldu/4.yml"),
        ),
        (
            "ocd-division/country:us/state:ca/place:chico",
            Path("data/ca/place/chico.yml"),
        ),
        (
            "ocd-division/country:us/district:dc",
            Path("data/dc/state.yml"),
        ),
        (
            "ocd-division/country:us/district:dc/ward:8",
            Path("data/dc/ward/8.yml"),
        ),
        (
            "ocd-division/country:us/state:ny/place:new_york/council_district:36",
            Path("data/ny/council_district/new_york-36.yml"),
        ),
    ],
)
def test_expected_path(ocd_id: str, expected: Path) -> None:
    assert expected_path(ocd_id) == expected


def test_parse_ocd_id_rejects_bad_country() -> None:
    with pytest.raises(ValueError):
        parse_ocd_id("ocd-division/country:usa/state:ca")


def test_parse_ocd_id_requires_prefix() -> None:
    with pytest.raises(ValueError):
        parse_ocd_id("country:us/state:ca")


def test_parsed_parent_id() -> None:
    parsed = parse_ocd_id("ocd-division/country:us/state:ca/county:butte")
    assert parsed.parent_id == "ocd-division/country:us/state:ca"
    assert parsed.leaf_type == "county"
    assert parsed.leaf_slug == "butte"
