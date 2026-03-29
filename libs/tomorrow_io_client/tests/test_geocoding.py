import pytest
from unittest.mock import MagicMock, patch
import tomorrow_io_client.client as client_module
from tomorrow_io_client.client import get_tmrw_weather_tool

MOCK_API_KEY = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"  # pragma: allowlist secret


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("TOMORROW_IO_API_KEY", MOCK_API_KEY)
    client_module.reset_settings_cache()
    yield
    client_module.reset_settings_cache()


@pytest.fixture
def mock_geolocator():
    with patch("tomorrow_io_client.client.Nominatim") as mock_nominatim:
        mock_instance = MagicMock()
        mock_nominatim.return_value = mock_instance
        yield mock_instance


def test_geocoding_success(mock_geolocator, requests_mock):
    # Mock geolocator to return a location
    mock_location = MagicMock()
    mock_location.latitude = 45.0
    mock_location.longitude = -93.0
    mock_geolocator.geocode.return_value = mock_location

    # Mock Tomorrow.io API response
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={"timelines": {"hourly": []}},
        status_code=200,
    )

    # Call the tool with a city name
    result = get_tmrw_weather_tool("Minneapolis")

    # Verify geocoder was called
    mock_geolocator.geocode.assert_called_once_with("Minneapolis", limit=1)

    # Even if it fails later due to empty hourly data, we checked the geocoding part
    assert result["location"] == "Minneapolis"


def test_geocoding_failure_fallback(mock_geolocator, requests_mock):
    # Mock geolocator to return None (failure)
    mock_geolocator.geocode.return_value = None

    # Mock Tomorrow.io API response
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={"timelines": {"hourly": []}},
        status_code=200,
    )

    # Call the tool
    result = get_tmrw_weather_tool("UnknownPlace")

    # Verify geocoder was called
    mock_geolocator.geocode.assert_called_once_with("UnknownPlace", limit=1)

    # Should fallback to original string (sanitized)
    assert result["location"] == "UnknownPlace"


def test_no_geocoding_for_coordinates(mock_geolocator, requests_mock):
    # Mock Tomorrow.io API response
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={"timelines": {"hourly": []}},
        status_code=200,
    )

    # Call the tool with coordinates
    result = get_tmrw_weather_tool("45.0,-93.0")

    # Verify geocoder was NOT called
    mock_geolocator.geocode.assert_not_called()

    assert result["location"] == "45.0,-93.0"


def test_geocoding_exception_fallback(mock_geolocator, requests_mock):
    # Mock geolocator to raise an exception
    mock_geolocator.geocode.side_effect = Exception("Geocoding service down")

    # Mock Tomorrow.io API response
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={"timelines": {"hourly": []}},
        status_code=200,
    )

    # Call the tool
    result = get_tmrw_weather_tool("Minneapolis")

    # Should fallback to original string
    assert result["location"] == "Minneapolis"
