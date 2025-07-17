from datetime import datetime, timezone

import requests
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tomorrow_io_api_key: str
    base_url: str = "https://api.tomorrow.io/v4/weather/forecast"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()  # type: ignore values come from .env or environment variables

class TomorrowIoTool:
    def __init__(self):
        # Use the pre-initialized, shared instance of the settings.
        self.settings = settings

    def get_daily_summary(self, location: str) -> str:
        params = {"location": location, "timesteps": "1h", "units": "imperial", "apikey": self.settings.tomorrow_io_api_key}
        response = requests.get(self.settings.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        hours = data.get("timelines", {}).get("hourly", [])
        if not hours:
            return "No hourly weather data available."

        # Define time ranges for morning, afternoon, evening
        today = datetime.now(tz=timezone.utc).date()
        morning_hours = [8, 9, 10, 11, 12]
        afternoon_hours = [13, 14, 15, 16, 17]
        evening_hours = [18, 19, 20, 21]

        def summarize_period(hourly_data, hour_range):
            temps = []
            prec_probs = []
            clouds = []
            for entry in hourly_data:
                dt = datetime.fromisoformat(entry["time"].replace("Z", "+00:00")).astimezone(tz=timezone.utc)
                if dt.date() != today:
                    continue

                if dt.hour in hour_range:
                    values = entry.get("values", {})
                    temps.append(values.get("temperature", 0))
                    prec_probs.append(values.get("precipitationProbability", 0))
                    clouds.append(values.get("cloudCover", 0))
            if not temps:
                return None
            avg_temp = round(sum(temps) / len(temps))
            avg_prec = round(sum(prec_probs) / len(prec_probs))
            avg_cloud = round(sum(clouds) / len(clouds))
            # Cloud cover description
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

        summary = "Today's forecast - "
        if morning:
            summary += f"Morning (8am-12pm): {morning}. "
        if afternoon:
            summary += f"Afternoon (12pm-5pm): {afternoon}. "
        if evening:
            summary += f"Evening (6pm-9pm): {evening}."
        return summary.strip()
