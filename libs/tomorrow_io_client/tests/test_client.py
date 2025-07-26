import pytest
import requests
from tomorrow_io_client.client import get_tmrw_weather_tool
from datetime import datetime, timezone

MOCK_API_KEY = "test_api_key"
MOCK_LOCATION = "New York, NY"
MOCK_URL = "https://api.tomorrow.io/v4/weather/forecast"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("TOMORROW_IO_API_KEY", MOCK_API_KEY)


@pytest.fixture
def sample_response():
    """
    This fixture creates a sample API response from tomorrow.io.
    The timestamps are generated in UTC, but they are calculated to fall into
    morning, afternoon, and evening slots when converted to the local timezone
    where the tests are run. This makes the tests timezone-independent.
    """
    hourly_entries = []
    local_tz = datetime.now().astimezone().tzinfo
    local_now = datetime.now(local_tz)

    # Define target hours in local time for different parts of the day
    target_hours_map = {
        "morning": [8, 9],
        "afternoon": [13, 14],
        "evening": [18, 19],
    }

    # Dummy data for weather values
    weather_values = {
        8: {"temperature": 70, "precipitationProbability": 15, "cloudCover": 40},
        9: {"temperature": 72, "precipitationProbability": 10, "cloudCover": 20},
        13: {"temperature": 80, "precipitationProbability": 5, "cloudCover": 10},
        14: {"temperature": 84, "precipitationProbability": 5, "cloudCover": 5},
        18: {"temperature": 78, "precipitationProbability": 0, "cloudCover": 0},
        19: {"temperature": 76, "precipitationProbability": 0, "cloudCover": 0},
    }

    for _, hours in target_hours_map.items():
        for hour in hours:
            # Create a datetime for the target hour in the local timezone
            target_local_time = local_now.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            # Convert this local time to UTC
            target_utc_time = target_local_time.astimezone(timezone.utc)
            hourly_entries.append(
                {
                    "time": target_utc_time.isoformat(),
                    "values": weather_values[hour],
                }
            )

    return {"timelines": {"hourly": hourly_entries}}


def test_get_tmrw_weather_tool_success(requests_mock, sample_response):
    requests_mock.get(MOCK_URL, json=sample_response, status_code=200)
    summary = get_tmrw_weather_tool(MOCK_LOCATION)
    assert "Today's forecast -" in summary
    assert "Morning" in summary
    assert "Afternoon" in summary
    assert "Evening" in summary
    assert "Avg" in summary


def test_get_tmrw_weather_tool_api_error(requests_mock):
    requests_mock.get(MOCK_URL, status_code=500)
    with pytest.raises(requests.exceptions.HTTPError):
        get_tmrw_weather_tool(MOCK_LOCATION)


def test_get_tmrw_weather_tool_no_hourly_data(requests_mock):
    # API returns a valid response but with an empty hourly timeline
    empty_response = {"timelines": {"hourly": []}}
    requests_mock.get(MOCK_URL, json=empty_response, status_code=200)
    summary = get_tmrw_weather_tool(MOCK_LOCATION)
    assert summary == "No hourly weather data available."
