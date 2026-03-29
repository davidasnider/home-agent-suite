import pytest
import home_assistant_client.client as client_module
from home_assistant_client.client import get_state, call_service

MOCK_URL = "http://homeassistant.local:8123"
MOCK_TOKEN = "dummy_token"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("HA_URL", MOCK_URL)
    monkeypatch.setenv("HA_TOKEN", MOCK_TOKEN)
    # Clear lru_cache for settings
    client_module.get_settings.cache_clear()
    yield
    client_module.get_settings.cache_clear()


def test_get_state_success(requests_mock):
    entity_id = "light.living_room"
    mock_response = {"entity_id": entity_id, "state": "on", "attributes": {}}
    requests_mock.get(
        f"{MOCK_URL}/api/states/{entity_id}", json=mock_response, status_code=200
    )

    result = get_state(entity_id)
    assert result["status"] == "success"
    assert result["data"]["state"] == "on"
    assert result["entity_id"] == entity_id


def test_get_state_failure(requests_mock):
    entity_id = "light.non_existent"
    requests_mock.get(f"{MOCK_URL}/api/states/{entity_id}", status_code=404)

    result = get_state(entity_id)
    assert result["status"] == "error"
    assert "404" in result["message"]


def test_call_service_success(requests_mock):
    domain = "light"
    service = "turn_on"
    entity_id = "light.living_room"
    mock_response = [{"entity_id": entity_id, "state": "on", "attributes": {}}]
    requests_mock.post(
        f"{MOCK_URL}/api/services/{domain}/{service}",
        json=mock_response,
        status_code=200,
    )

    result = call_service(domain, service, entity_id)
    assert result["status"] == "success"
    assert result["entity_id"] == entity_id


def test_call_service_failure(requests_mock):
    domain = "light"
    service = "invalid_service"
    entity_id = "light.living_room"
    requests_mock.post(f"{MOCK_URL}/api/services/{domain}/{service}", status_code=400)

    result = call_service(domain, service, entity_id)
    assert result["status"] == "error"
    assert "400" in result["message"]


def test_missing_config(monkeypatch):
    monkeypatch.delenv("HA_URL", raising=False)
    client_module.get_settings.cache_clear()

    result = get_state("light.test")
    assert result["status"] == "error"
    assert "Home Assistant URL not configured" in result["message"]
