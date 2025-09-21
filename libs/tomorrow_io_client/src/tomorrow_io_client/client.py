"""
Tomorrow.io Weather API Client Module

This module provides a robust, production-ready client for the Tomorrow.io weather API,
specifically designed for integration with Google ADK agents and MCP systems.

The client handles API authentication, request formatting, response parsing, and
error handling while providing a simplified interface optimized for AI agent
consumption.

Key Features:
- Structured weather data retrieval
- Intelligent response summarization for LLM consumption
- Comprehensive error handling and logging
- Local timezone awareness
- Production-ready configuration management

API Integration:
- Tomorrow.io Forecast API v4
- Hourly weather data with 7-day forecasts
- Imperial units (Fahrenheit, miles, etc.)
- Location flexibility (city names, coordinates, zip codes)

For MCP and agentic AI systems, this client:
- Provides deterministic, structured responses
- Optimizes token usage with intelligent summarization
- Enables reliable weather-based decision making
- Supports conversational context with location memory
"""

from datetime import datetime, timezone
import re
import requests
import tzlocal
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from common_logging.logging_utils import setup_logging

import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuration settings for the Tomorrow.io weather API client."""

    tomorrow_io_api_key: SecretStr
    base_url: str = "https://api.tomorrow.io/v4/weather/forecast"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("tomorrow_io_api_key")
    def validate_api_key(cls, v):
        api_key = v.get_secret_value()
        if not re.match(r"^[a-zA-Z0-9_]{32,}$", api_key):
            raise ValueError(
                "Invalid Tomorrow.io API key format. "
                "Key must be at least 32 characters and contain only "
                "alphanumeric characters and underscores."
            )
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Initialized Tomorrow.io Settings with base_url=%s", self.base_url)


settings = Settings()  # type: ignore values come from .env or environment variables


def get_tmrw_weather_tool(location: str) -> dict:
    """
    Get a daily weather summary for a specified location using Tomorrow.io API.

    Args:
        location (str): The location to get weather for (city name, coordinates, etc.)

    Returns:
        dict: A dictionary with keys:
            - status (str): "success" or "error"
            - forecast (str): Weather summary if successful, else None
            - location (str): The location queried
            - error_message (str, optional): Present if status is "error"

    Example success:
        {
            "status": "success",
            "forecast": "Today's forecast - Morning (8am-12pm): ...",
            "location": "New York, NY"
        }
    Example error:
        {
            "status": "error",
            "error_message": "No hourly weather data available.",
            "location": "New York, NY"
        }
    """
    # Validate and sanitize location input
    if len(location) > 256:
        return {
            "status": "error",
            "error_message": "Location input is too long.",
            "location": location,
            "forecast": None,
        }

    sanitized_location = re.sub(r"[^a-zA-Z0-9\s,'-.]", "", location)
    if not sanitized_location:
        return {
            "status": "error",
            "error_message": "Invalid location input.",
            "location": location,
            "forecast": None,
        }

    params = {
        "location": sanitized_location,
        "timesteps": "1h",
        "units": "imperial",
        "apikey": settings.tomorrow_io_api_key.get_secret_value(),
    }
    try:
        logger.info("Requesting weather summary for location: %s", location)
        response = requests.get(settings.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info("Received weather data response for location: %s", location)
    except requests.RequestException as e:
        logger.error("API request failed for location %s: %s", location, e)
        return {
            "status": "error",
            "error_message": str(e),
            "location": location,
            "forecast": None,
        }
    try:
        hours = data.get("timelines", {}).get("hourly", [])
    except (KeyError, TypeError):
        hours = []
        logger.warning("Malformed response structure for location: %s", location)
    if not hours:
        logger.warning("No hourly weather data available for location: %s", location)
        return {
            "status": "error",
            "error_message": "No hourly weather data available.",
            "location": location,
            "forecast": None,
        }

    local_tz = tzlocal.get_localzone()
    today_local = datetime.now(local_tz).date()
    morning_hours = range(8, 12)
    afternoon_hours = range(12, 17)
    evening_hours = range(17, 22)

    def summarize_period(hourly_data, hour_range):
        logger.info("Summarizing weather for location: %s", location)
        temps = []
        prec_probs = []
        clouds = []
        for entry in hourly_data:
            try:
                dt_utc = datetime.fromisoformat(entry["time"]).astimezone(timezone.utc)
                dt_local = dt_utc.astimezone(local_tz)
                values = entry.get("values", {})
            except (ValueError, KeyError, TypeError):
                continue
            if dt_local.date() != today_local:
                continue
            if dt_local.hour in hour_range:
                temps.append(values.get("temperature", 0))
                prec_probs.append(values.get("precipitationProbability", 0))
                clouds.append(values.get("cloudCover", 0))
        if not temps:
            return None
        avg_temp = round(sum(temps) / len(temps))
        avg_prec = round(sum(prec_probs) / len(prec_probs))
        avg_cloud = round(sum(clouds) / len(clouds))
        if avg_cloud < 20:
            cloud_desc = "sunny"
        elif avg_cloud < 50:
            cloud_desc = "partly cloudy"
        else:
            cloud_desc = "cloudy"
        return f"Avg {avg_temp}F, {avg_prec}% rain chance, {cloud_desc}"

    morning = summarize_period(hours, morning_hours)
    afternoon = summarize_period(hours, afternoon_hours)
    evening = summarize_period(hours, evening_hours)
    logger.info(
        "Summary parts: morning=%s, afternoon=%s, evening=%s",
        morning[:40] if morning else None,
        afternoon[:40] if afternoon else None,
        evening[:40] if evening else None,
    )

    summary_parts = []
    if morning:
        summary_parts.append(f"Morning (8am-12pm): {morning}")
    if afternoon:
        summary_parts.append(f"Afternoon (12pm-5pm): {afternoon}")
    if evening:
        summary_parts.append(f"Evening (5pm-10pm): {evening}")

    if not summary_parts:
        logger.warning(
            "No forecast data available for today for location: %s", location
        )
        return {
            "status": "error",
            "error_message": "No forecast data available for today.",
            "location": location,
            "forecast": None,
        }

    forecast = "Today's forecast - " + ". ".join(summary_parts) + "."
    logger.info("Returning forecast for location %s: %s", location, forecast[:40])
    return {"status": "success", "forecast": forecast, "location": location}


# Debug block for direct execution
if __name__ == "__main__":
    setup_logging(service_name="tomorrow_io_client")
    logger.info("--- Running get_tmrw_weather_tool in Direct Debug Mode ---")
    test_location = "kalispell"
    logger.info(f"Fetching weather summary for: {test_location}")
    try:
        live_summary = get_tmrw_weather_tool(location=test_location)
        logger.info("--- Live API Weather Summary ---")
        logger.info(live_summary)
    except requests.exceptions.RequestException as e:
        logger.error("--- An API error occurred ---")
        logger.error(f"Error: {e}")
