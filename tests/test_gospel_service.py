import pytest

from src.service.gospel import GospelNotFoundError, InvalidDateError, get_gospel


def test_get_gospel_for_specific_date_returns_metadata_only():
    result = get_gospel("2026-04-19")

    assert result == {
        "date": "2026-04-19",
        "timezone": "America/Edmonton",
        "source": "catholic-daily-readings",
        "records": [
            {
                "feast": "Third Sunday of Easter",
                "mass": "default",
                "lectionary_number": 44,
                "gospels": [
                    {"citation": "Luke 24:13-35", "sources": ["USCCB"]},
                ],
            }
        ],
    }


def test_get_gospel_preserves_multiple_masses_for_same_day():
    result = get_gospel("2026-04-02")

    assert [record["mass"] for record in result["records"]] == ["Chrism", "Supper"]
    assert result["records"][0]["gospels"] == [
        {"citation": "Luke 4:16-21", "sources": ["USCCB"]}
    ]
    assert result["records"][1]["gospels"] == [
        {"citation": "John 13:1-15", "sources": ["USCCB", "CatholicGallery", "CatholicOnline"]}
    ]


def test_get_gospel_uses_timezone_today_when_date_missing():
    result = get_gospel(today="2026-04-19")

    assert result["date"] == "2026-04-19"
    assert result["records"][0]["gospels"] == [
        {"citation": "Luke 24:13-35", "sources": ["USCCB"]}
    ]


def test_get_gospel_rejects_invalid_date_format():
    with pytest.raises(InvalidDateError):
        get_gospel("04/19/2026")


def test_get_gospel_raises_not_found_for_missing_date():
    with pytest.raises(GospelNotFoundError):
        get_gospel("2099-01-01")
