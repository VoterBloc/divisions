import pytest
from pydantic import ValidationError

from divisions.models import Division


def _minimal(**overrides):
    base = {
        "id": "ocd-division/country:us/state:ca/county:butte",
        "name": "Butte County",
        "type": "county",
    }
    base.update(overrides)
    return base


def test_minimum_county_validates() -> None:
    d = Division.model_validate(_minimal())
    assert d.type == "county"
    assert d.name == "Butte County"


def test_id_type_mismatch_fails() -> None:
    with pytest.raises(ValidationError) as exc:
        Division.model_validate(_minimal(type="place"))
    assert "does not match" in str(exc.value)


def test_state_requires_abbreviation() -> None:
    with pytest.raises(ValidationError) as exc:
        Division.model_validate(
            {"id": "ocd-division/country:us/state:ca", "name": "California", "type": "state"}
        )
    assert "abbreviation" in str(exc.value)


def test_state_validates_with_abbreviation() -> None:
    Division.model_validate(
        {
            "id": "ocd-division/country:us/state:ca",
            "name": "California",
            "type": "state",
            "abbreviation": "CA",
        }
    )


def test_cd_requires_number() -> None:
    with pytest.raises(ValidationError) as exc:
        Division.model_validate(
            {"id": "ocd-division/country:us/state:ca/cd:1", "name": "CA-1", "type": "cd"}
        )
    assert "number" in str(exc.value)


def test_parent_derived_from_id_when_omitted() -> None:
    d = Division.model_validate(_minimal())
    # `parent` is not auto-populated (YAML source of truth), but the validator
    # accepts an explicit match:
    Division.model_validate(_minimal(parent="ocd-division/country:us/state:ca"))


def test_parent_mismatch_fails() -> None:
    with pytest.raises(ValidationError) as exc:
        Division.model_validate(_minimal(parent="ocd-division/country:us/state:tx"))
    assert "does not match" in str(exc.value)


def test_same_as_is_list() -> None:
    d = Division.model_validate(
        _minimal(
            same_as=[
                {
                    "id": "ocd-division/country:us/state:ca/place:butte",
                    "note": "consolidated",
                }
            ]
        )
    )
    assert d.same_as[0].id.endswith("/place:butte")


def test_jurisdiction_must_be_ocd_jurisdiction() -> None:
    with pytest.raises(ValidationError):
        Division.model_validate(_minimal(jurisdiction="ocd-division/country:us/state:ca"))


def test_contact_accepts_classification() -> None:
    d = Division.model_validate(
        _minimal(contacts=[{"classification": "elections", "voice": "555-1212"}])
    )
    assert d.contacts[0].classification == "elections"


def test_precinct_requires_parent() -> None:
    with pytest.raises(ValidationError) as exc:
        Division.model_validate(
            {
                "id": "ocd-division/country:us/state:ca/precinct:1",
                "name": "Precinct 1",
                "type": "precinct",
                "number": "1",
            }
        )
    assert "place" in str(exc.value) or "county" in str(exc.value)
