import requests
import logging
from typing import Any, Dict, Optional
from pydantic import SecretStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from common_logging.logging_utils import setup_logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuration settings for the Home Assistant client."""

    ha_url: Optional[HttpUrl] = None
    ha_token: Optional[SecretStr] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Lazily load settings."""
    return Settings()


def get_ha_headers() -> Dict[str, str]:
    """Get headers for Home Assistant API requests."""
    settings = get_settings()
    if not settings.ha_token:
        logger.error("Home Assistant token not found in settings.")
        raise ValueError("Home Assistant token not configured.")
    return {
        "Authorization": f"Bearer {settings.ha_token.get_secret_value()}",
        "Content-Type": "application/json",
    }


def get_state(entity_id: str) -> Dict[str, Any]:
    """
    Get the current state of a Home Assistant entity.

    Args:
        entity_id (str): The entity ID to query (e.g., 'light.living_room').

    Returns:
        dict: The state information or an error message.
    """
    settings = get_settings()
    if not settings.ha_url:
        return {"status": "error", "message": "Home Assistant URL not configured."}

    url = f"{str(settings.ha_url).rstrip('/')}/api/states/{entity_id}"
    try:
        logger.info(f"Querying state for entity: {entity_id}")
        response = requests.get(url, headers=get_ha_headers(), timeout=10)
        response.raise_for_status()
        return {"status": "success", "data": response.json(), "entity_id": entity_id}
    except Exception as e:
        logger.error(f"Failed to get state for {entity_id}: {e}")
        return {"status": "error", "message": str(e), "entity_id": entity_id}


def call_service(domain: str, service: str, entity_id: str, **kwargs) -> Dict[str, Any]:
    """
    Call a Home Assistant service.

    Args:
        domain (str): The service domain (e.g., 'light').
        service (str): The service to call (e.g., 'turn_on').
        entity_id (str): The entity ID to act upon.
        **kwargs: Additional service data.

    Returns:
        dict: The result of the service call or an error message.
    """
    settings = get_settings()
    if not settings.ha_url:
        return {"status": "error", "message": "Home Assistant URL not configured."}

    url = f"{str(settings.ha_url).rstrip('/')}/api/services/{domain}/{service}"
    payload = {"entity_id": entity_id, **kwargs}

    try:
        logger.info(f"Calling service {domain}.{service} for entity: {entity_id}")
        response = requests.post(
            url, headers=get_ha_headers(), json=payload, timeout=10
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json(), "entity_id": entity_id}
    except Exception as e:
        logger.error(f"Failed to call service {domain}.{service} for {entity_id}: {e}")
        return {"status": "error", "message": str(e), "entity_id": entity_id}


# Debug block
if __name__ == "__main__":
    setup_logging(service_name="home_assistant_client")
    print("Home Assistant Client check...")
    # Example usage (will probably fail without real config)
    # print(get_state("light.test"))
