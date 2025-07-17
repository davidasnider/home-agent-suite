import pytest
import requests
from tomorrow_io_client import TomorrowIoTool
from datetime import datetime, timezone

MOCK_API_KEY = "test_api_key"
MOCK_LOCATION = "New York, NY"
MOCK_URL = "https://api.tomorrow.io/v4/weather/forecast"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("TOMORROW_IO_API_KEY", MOCK_API_KEY)


SAMPLE_RESPONSE = {
    "timelines": {
        "hourly": [
            {
                "time": datetime.now(tz=timezone.utc)
                .replace(hour=8, minute=0, second=0, microsecond=0)
                .isoformat(),
                "values": {
                    "temperature": 70,
                    "precipitationProbability": 15,
                    "cloudCover": 40,
                },
            },
            {
                "time": datetime.now(tz=timezone.utc)
                .replace(hour=9, minute=0, second=0, microsecond=0)
                .isoformat(),
                "values": {
                    "temperature": 72,
                    "precipitationProbability": 10,
                    "cloudCover": 20,
                },
            },
            {
                "time": datetime.now(tz=timezone.utc)
                .replace(hour=13, minute=0, second=0, microsecond=0)
                .isoformat(),
                "values": {
                    "temperature": 80,
                    "precipitationProbability": 5,
                    "cloudCover": 10,
                },
            },
            {
                "time": datetime.now(tz=timezone.utc)
                .replace(hour=14, minute=0, second=0, microsecond=0)
                .isoformat(),
                "values": {
                    "temperature": 84,
                    "precipitationProbability": 5,
                    "cloudCover": 5,
                },
            },
            {
                "time": datetime.now(tz=timezone.utc)
                .replace(hour=18, minute=0, second=0, microsecond=0)
                .isoformat(),
                "values": {
                    "temperature": 78,
                    "precipitationProbability": 0,
                    "cloudCover": 0,
                },
            },
            {
                "time": datetime.now(tz=timezone.utc)
                .replace(hour=19, minute=0, second=0, microsecond=0)
                .isoformat(),
                "values": {
                    "temperature": 76,
                    "precipitationProbability": 0,
                    "cloudCover": 0,
                },
            },
        ]
    }
}


def test_get_daily_summary_success(requests_mock):
    requests_mock.get(MOCK_URL, json=SAMPLE_RESPONSE, status_code=200)
    tool = TomorrowIoTool()
    summary = tool.get_daily_summary(MOCK_LOCATION)
    assert "Today's forecast -" in summary
    assert "Morning" in summary
    assert "Afternoon" in summary
    assert "Evening" in summary
    assert "Avg" in summary


def test_get_daily_summary_api_error(requests_mock):
    requests_mock.get(MOCK_URL, status_code=500)
    tool = TomorrowIoTool()
    with pytest.raises(requests.exceptions.HTTPError):
        tool.get_daily_summary(MOCK_LOCATION)
