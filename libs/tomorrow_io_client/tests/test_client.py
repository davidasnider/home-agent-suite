import pytest
import requests
import requests_mock
from tomorrow_io_client.client import TomorrowIoTool

MOCK_API_KEY = "test_api_key"
MOCK_LOCATION = "New York, NY"
MOCK_URL = "https://api.tomorrow.io/v4/weather/forecast"

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("TOMORROW_IO_API_KEY", MOCK_API_KEY)

SAMPLE_RESPONSE = {
    "timelines": {
        "hourly": [
            {"time": "2025-07-15T08:00:00Z", "values": {"temperature": 70, "precipitationProbability": 15, "cloudCover": 40}},
            {"time": "2025-07-15T09:00:00Z", "values": {"temperature": 72, "precipitationProbability": 10, "cloudCover": 20}},
            {"time": "2025-07-15T13:00:00Z", "values": {"temperature": 80, "precipitationProbability": 5, "cloudCover": 10}},
            {"time": "2025-07-15T14:00:00Z", "values": {"temperature": 84, "precipitationProbability": 5, "cloudCover": 5}},
            {"time": "2025-07-15T18:00:00Z", "values": {"temperature": 78, "precipitationProbability": 0, "cloudCover": 0}},
            {"time": "2025-07-15T19:00:00Z", "values": {"temperature": 76, "precipitationProbability": 0, "cloudCover": 0}},
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
