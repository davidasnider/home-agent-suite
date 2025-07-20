from datetime import datetime, timezone

import requests
import tzlocal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Tomorrow.io weather API client.
    
    This class uses Pydantic's BaseSettings to automatically load configuration
    from environment variables or .env files.
    
    Attributes:
        tomorrow_io_api_key: API key for Tomorrow.io weather service
        base_url: Base URL for the Tomorrow.io API endpoints
    """
    tomorrow_io_api_key: str
    base_url: str = "https://api.tomorrow.io/v4/weather/forecast"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore values come from .env or environment variables


class TomorrowIoTool:
    """A tool for fetching and processing weather data from Tomorrow.io API.
    
    This class provides methods to retrieve and format weather forecasts
    for specified locations using the Tomorrow.io weather service.
    """
    
    def __init__(self):
        """Initialize the TomorrowIoTool with configuration settings.
        
        Uses the pre-initialized, shared instance of the settings which
        loads API keys and configuration from environment variables.
        """
        # Use the pre-initialized, shared instance of the settings.
        self.settings = settings

    def get_daily_summary(self, location: str) -> str:
        """Get a formatted daily weather summary for a specified location.
        
        Fetches hourly weather data from Tomorrow.io API and processes it into
        a human-readable summary broken down by time periods (morning, afternoon, evening).
        
        Args:
            location: The location to get weather for. Can be a city name, 
                     coordinates, or any format supported by Tomorrow.io API
                     (e.g., "40.7128,-74.0060", "London")
        
        Returns:
            A formatted string containing today's weather forecast with average
            temperature, precipitation probability, and cloud conditions for
            morning (8am-12pm), afternoon (12pm-5pm), and evening (5pm-10pm).
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
            requests.exceptions.RequestException: For other request-related errors
            
        Example:
            >>> tool = TomorrowIoTool()
            >>> summary = tool.get_daily_summary("New York, NY")
            >>> print(summary)
            Today's forecast - Morning (8am-12pm): Avg 72F, 10% rain chance, partly cloudy. 
            Afternoon (12pm-5pm): Avg 78F, 5% rain chance, sunny.
        """
        params = {
            "location": location,
            "timesteps": "1h",
            "units": "imperial",
            "apikey": self.settings.tomorrow_io_api_key,
        }
        response = requests.get(self.settings.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        # The v4 API returns timelines in data["timelines"]["hourly"]
        try:
            hours = data.get("timelines", {}).get("hourly", [])
        except (KeyError, TypeError):
            hours = []
        if not hours:
            return "No hourly weather data available."

        # Define time ranges for morning, afternoon, evening

        local_tz = tzlocal.get_localzone()
        today_local = datetime.now(local_tz).date()
        morning_hours = range(8, 12)  # 8am up to 12pm
        afternoon_hours = range(12, 17)  # 12pm up to 5pm
        evening_hours = range(17, 22)  # 5pm up to 10pm

        def summarize_period(hourly_data, hour_range):
            """Summarize weather data for a specific time period.
            
            Processes hourly weather data to calculate average conditions
            for a given range of hours in the current day.
            
            Args:
                hourly_data: List of hourly weather data entries from API
                hour_range: Range object specifying which hours to include
                
            Returns:
                String summary of average conditions for the period, or None
                if no data is available for the specified time range.
            """
            temps = []
            prec_probs = []
            clouds = []
            for entry in hourly_data:
                try:
                    dt_utc = datetime.fromisoformat(entry["time"]).astimezone(
                        timezone.utc
                    )
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

        # Build the summary string cleanly from available parts.
        summary_parts = []
        if morning:
            summary_parts.append(f"Morning (8am-12pm): {morning}")
        if afternoon:
            summary_parts.append(f"Afternoon (12pm-5pm): {afternoon}")
        if evening:
            summary_parts.append(f"Evening (5pm-10pm): {evening}")

        if not summary_parts:
            return "No forecast data available for today."

        return "Today's forecast - " + ". ".join(summary_parts) + "."


# This block allows the file to be run directly for debugging against the live API.
# It will not run when the module is imported by other code.
if __name__ == "__main__":
    print("--- Running TomorrowIoTool in Direct Debug Mode ---")
    tool = TomorrowIoTool()
    # Replace with any location you want to test live.
    test_location = "kalispell"
    print(f"Fetching weather summary for: {test_location}")
    try:
        live_summary = tool.get_daily_summary(location=test_location)
        print("\n--- Live API Weather Summary ---")
        print(live_summary)
    except requests.exceptions.RequestException as e:
        print("\n--- An API error occurred ---")
        print(f"Error: {e}")
