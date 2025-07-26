from datetime import datetime, timezone
import requests
import tzlocal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Tomorrow.io weather API client."""

    tomorrow_io_api_key: str
    base_url: str = "https://api.tomorrow.io/v4/weather/forecast"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


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
    params = {
        "location": location,
        "timesteps": "1h",
        "units": "imperial",
        "apikey": settings.tomorrow_io_api_key,
    }
    response = requests.get(settings.base_url, params=params)
    response.raise_for_status()
    data = response.json()
    try:
        hours = data.get("timelines", {}).get("hourly", [])
    except (KeyError, TypeError):
        hours = []
    if not hours:
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

    summary_parts = []
    if morning:
        summary_parts.append(f"Morning (8am-12pm): {morning}")
    if afternoon:
        summary_parts.append(f"Afternoon (12pm-5pm): {afternoon}")
    if evening:
        summary_parts.append(f"Evening (5pm-10pm): {evening}")

    if not summary_parts:
        return {
            "status": "error",
            "error_message": "No forecast data available for today.",
            "location": location,
            "forecast": None,
        }

    forecast = "Today's forecast - " + ". ".join(summary_parts) + "."
    return {"status": "success", "forecast": forecast, "location": location}


# Debug block for direct execution
if __name__ == "__main__":
    print("--- Running get_tmrw_weather_tool in Direct Debug Mode ---")
    test_location = "kalispell"
    print(f"Fetching weather summary for: {test_location}")
    try:
        live_summary = get_tmrw_weather_tool(location=test_location)
        print("\n--- Live API Weather Summary ---")
        print(live_summary)
    except requests.exceptions.RequestException as e:
        print("\n--- An API error occurred ---")
        print(f"Error: {e}")
