#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

import argparse
import os
import sys
from datetime import datetime
from typing import Any

import requests


BASE_URL = "http://api.weatherapi.com/v1"

CLI_EPILOG = '''\
Examples:
  weather.py current --location "San Francisco"
  weather.py current --location "94102" --aqi
  weather.py current --location "51.5,-0.1"
  weather.py forecast --location "London" --days 7
  weather.py forecast --location "Tokyo" --days 5 --alerts --hourly
  weather.py history --location "London" --date 2024-01-15
  weather.py history --location "NYC" --date 2024-06-01 --hourly

Location formats supported:
  - City name: "London", "New York"
  - US/UK/Canada postal codes: "10001", "SW1A 1AA", "M5V 3L9"
  - Coordinates: "48.8566,2.3522"
  - IP address: "auto" (uses your IP)
  - Airport code: "JFK", "LAX"
'''


class WeatherAPIError(Exception):
    '''Custom exception for WeatherAPI errors.'''
    pass


class WeatherClient:
    '''Simple HTTP client for WeatherAPI.com.'''

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
        })

    def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        '''Make a request to the WeatherAPI.'''
        params["key"] = self.api_key
        url = f"{BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200:
                error_msg = data.get("error", {}).get("message", "Unknown error")
                raise WeatherAPIError(f"API error: {error_msg}")

            return data

        except requests.exceptions.Timeout:
            raise WeatherAPIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Connection failed")
        except requests.exceptions.JSONDecodeError:
            raise WeatherAPIError("Invalid response from API")

    def get_current(self, location: str, aqi: bool = False) -> dict[str, Any]:
        '''Get current weather for a location.'''
        params = {
            "q": location,
            "aqi": "yes" if aqi else "no",
        }
        return self._request("current.json", params)

    def get_forecast(
        self,
        location: str,
        days: int = 3,
        aqi: bool = False,
        alerts: bool = False,
    ) -> dict[str, Any]:
        '''Get weather forecast for a location.'''
        params = {
            "q": location,
            "days": min(max(days, 1), 14),  # clamp to 1-14
            "aqi": "yes" if aqi else "no",
            "alerts": "yes" if alerts else "no",
        }
        return self._request("forecast.json", params)

    def get_history(self, location: str, date: str) -> dict[str, Any]:
        '''Get historical weather for a location and date.'''
        params = {"q": location, "dt": date}
        return self._request("history.json", params)


def format_location(loc: dict[str, Any]) -> str:
    '''Format location data for display.'''
    parts = [loc.get("name", "Unknown")]
    if loc.get("region") and loc["region"] != loc.get("name"):
        parts.append(loc["region"])
    if loc.get("country"):
        parts.append(loc["country"])
    return ", ".join(parts)


def format_wind(current: dict[str, Any]) -> str:
    '''Format wind information.'''
    mph = current.get("wind_mph", 0)
    kph = current.get("wind_kph", 0)
    direction = current.get("wind_dir", "")
    gust_mph = current.get("gust_mph", 0)

    wind_str = f"{mph} mph ({kph} km/h) {direction}"
    if gust_mph > mph:
        wind_str += f", gusts {gust_mph} mph"
    return wind_str


def format_precip(current: dict[str, Any]) -> str:
    '''Format precipitation information.'''
    mm = current.get("precip_mm", 0)
    inches = current.get("precip_in", 0)
    if mm > 0:
        return f"{inches} in ({mm} mm)"
    return "None"


def get_uv_level(uv: float) -> str:
    '''Get UV index level description.'''
    if uv <= 2:
        return "Low"
    elif uv <= 5:
        return "Moderate"
    elif uv <= 7:
        return "High"
    elif uv <= 10:
        return "Very High"
    else:
        return "Extreme"


def get_aqi_level(aqi: int) -> str:
    '''Get air quality level description (US EPA standard).'''
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy (Sensitive)"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def cmd_current(client: WeatherClient, args: argparse.Namespace) -> int:
    '''Display current weather conditions.'''
    try:
        data = client.get_current(args.location, aqi=args.aqi)
    except WeatherAPIError as e:
        print(f"Error: {e}")
        return 1

    loc = data.get("location", {})
    current = data.get("current", {})
    condition = current.get("condition", {})

    # Header
    print(f"\nCurrent Weather for {format_location(loc)}")
    print("=" * 60)

    # Local time
    localtime = loc.get("localtime", "")
    if localtime:
        print(f"  Local Time:    {localtime}")

    # Condition
    print(f"  Condition:     {condition.get('text', 'Unknown')}")

    # Temperature
    temp_f = current.get("temp_f", 0)
    temp_c = current.get("temp_c", 0)
    feels_f = current.get("feelslike_f", 0)
    feels_c = current.get("feelslike_c", 0)
    print(f"  Temperature:   {temp_f}°F ({temp_c}°C)")
    print(f"  Feels Like:    {feels_f}°F ({feels_c}°C)")

    # Wind
    print(f"  Wind:          {format_wind(current)}")

    # Humidity and pressure
    humidity = current.get("humidity", 0)
    pressure_in = current.get("pressure_in", 0)
    pressure_mb = current.get("pressure_mb", 0)
    print(f"  Humidity:      {humidity}%")
    print(f"  Pressure:      {pressure_in} in ({pressure_mb} mb)")

    # Visibility
    vis_miles = current.get("vis_miles", 0)
    vis_km = current.get("vis_km", 0)
    print(f"  Visibility:    {vis_miles} mi ({vis_km} km)")

    # Precipitation
    print(f"  Precipitation: {format_precip(current)}")

    # Cloud cover
    cloud = current.get("cloud", 0)
    print(f"  Cloud Cover:   {cloud}%")

    # UV Index
    uv = current.get("uv", 0)
    print(f"  UV Index:      {uv} ({get_uv_level(uv)})")

    # Air Quality (if requested)
    if args.aqi and "air_quality" in current:
        aq = current["air_quality"]
        # US EPA index is in us-epa-index field
        us_epa = aq.get("us-epa-index", 0)
        pm25 = aq.get("pm2_5", 0)
        pm10 = aq.get("pm10", 0)

        print()
        print("  Air Quality:")
        print(f"    EPA Index:   {us_epa} ({get_aqi_level(us_epa * 50)})")  # rough mapping
        print(f"    PM2.5:       {pm25:.1f} µg/m³")
        print(f"    PM10:        {pm10:.1f} µg/m³")

    print("=" * 60)
    return 0


def cmd_forecast(client: WeatherClient, args: argparse.Namespace) -> int:
    '''Display weather forecast.'''
    try:
        data = client.get_forecast(
            args.location,
            days=args.days,
            aqi=args.aqi,
            alerts=args.alerts,
        )
    except WeatherAPIError as e:
        print(f"Error: {e}")
        return 1

    loc = data.get("location", {})
    current = data.get("current", {})
    forecast = data.get("forecast", {})
    alerts = data.get("alerts", {}).get("alert", [])

    # Header
    print(f"\n{args.days}-Day Forecast for {format_location(loc)}")
    print("=" * 70)

    # Current conditions summary
    condition = current.get("condition", {})
    temp_f = current.get("temp_f", 0)
    temp_c = current.get("temp_c", 0)
    print(f"  Now: {condition.get('text', 'Unknown')} | {temp_f}°F ({temp_c}°C)")
    print()

    # Weather alerts
    if args.alerts and alerts:
        print("  WEATHER ALERTS:")
        print("  " + "-" * 66)
        for alert in alerts[:3]:  # limit to 3 alerts
            headline = alert.get("headline", "Unknown alert")
            severity = alert.get("severity", "")
            event = alert.get("event", "")
            print(f"  [{severity}] {event}")
            print(f"    {headline[:64]}...")
        print("  " + "-" * 66)
        print()

    # Get current hour for filtering today's hours
    try:
        current_hour = datetime.strptime(loc.get("localtime", ""), "%Y-%m-%d %H:%M").hour
    except ValueError:
        current_hour = 0

    # Daily forecasts
    forecastdays = forecast.get("forecastday", [])
    for day_idx, day_data in enumerate(forecastdays):
        date_str = day_data.get("date", "")
        day = day_data.get("day", {})
        astro = day_data.get("astro", {})

        # Parse date for display
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            date_display = date_obj.strftime("%b %d")
        except ValueError:
            day_name = ""
            date_display = date_str

        day_condition = day.get("condition", {}).get("text", "Unknown")
        max_f = day.get("maxtemp_f", 0)
        min_f = day.get("mintemp_f", 0)
        max_c = day.get("maxtemp_c", 0)
        min_c = day.get("mintemp_c", 0)

        # Precipitation chance
        rain_chance = day.get("daily_chance_of_rain", 0)
        snow_chance = day.get("daily_chance_of_snow", 0)

        # Total precipitation
        precip_in = day.get("totalprecip_in", 0)

        print(f"  {day_name}, {date_display}")
        print(f"    {day_condition}")
        print(f"    High: {max_f}°F ({max_c}°C)  |  Low: {min_f}°F ({min_c}°C)")

        if rain_chance > 0 or snow_chance > 0:
            precip_str = []
            if rain_chance > 0:
                precip_str.append(f"Rain: {rain_chance}%")
            if snow_chance > 0:
                precip_str.append(f"Snow: {snow_chance}%")
            print(f"    Chance: {' | '.join(precip_str)}")

        if precip_in > 0:
            print(f"    Expected: {precip_in} in")

        # Wind and humidity
        max_wind = day.get("maxwind_mph", 0)
        avg_humidity = day.get("avghumidity", 0)
        print(f"    Wind: up to {max_wind} mph  |  Humidity: {avg_humidity}%")

        # UV
        uv = day.get("uv", 0)
        print(f"    UV Index: {uv} ({get_uv_level(uv)})")

        # Sunrise/sunset
        sunrise = astro.get("sunrise", "")
        sunset = astro.get("sunset", "")
        if sunrise and sunset:
            print(f"    Sun: {sunrise} - {sunset}")

        # Hourly breakdown for this day (if requested)
        if args.hourly:
            hours = day_data.get("hour", [])
            is_today = (day_idx == 0)

            print()
            for hour_data in hours:
                hour_time = hour_data.get("time", "")
                try:
                    hour_obj = datetime.strptime(hour_time, "%Y-%m-%d %H:%M")
                    hour_num = hour_obj.hour
                except ValueError:
                    continue

                # For today, only show future hours
                if is_today and hour_num < current_hour:
                    continue

                temp_f = hour_data.get("temp_f", 0)
                condition = hour_data.get("condition", {}).get("text", "")
                rain_chance = hour_data.get("chance_of_rain", 0)
                wind_mph = hour_data.get("wind_mph", 0)

                time_display = hour_obj.strftime("%I %p").lstrip("0")
                rain_str = f" | Rain: {rain_chance}%" if rain_chance > 0 else ""
                print(f"      {time_display:>5}: {temp_f:>3.0f}°F  {condition:<18} Wind: {wind_mph:.0f} mph{rain_str}")

        print()

    print("=" * 70)
    return 0


def cmd_history(client: WeatherClient, args: argparse.Namespace) -> int:
    '''Display historical weather for a date.'''
    try:
        data = client.get_history(args.location, args.date)
    except WeatherAPIError as e:
        print(f"Error: {e}")
        return 1

    loc = data.get("location", {})
    forecast = data.get("forecast", {})
    forecastdays = forecast.get("forecastday", [])

    if not forecastdays:
        print("No historical data available for this date.")
        return 1

    day_data = forecastdays[0]
    date_str = day_data.get("date", args.date)
    day = day_data.get("day", {})
    astro = day_data.get("astro", {})

    # Parse date for display
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        date_display = date_obj.strftime("%B %d, %Y")
    except ValueError:
        day_name = ""
        date_display = date_str

    # Header
    print(f"\nHistorical Weather for {format_location(loc)}")
    print(f"{day_name}, {date_display}")
    print("=" * 60)

    # Condition
    day_condition = day.get("condition", {}).get("text", "Unknown")
    print(f"  Condition:     {day_condition}")

    # Temperature
    max_f = day.get("maxtemp_f", 0)
    min_f = day.get("mintemp_f", 0)
    max_c = day.get("maxtemp_c", 0)
    min_c = day.get("mintemp_c", 0)
    avg_f = day.get("avgtemp_f", 0)
    avg_c = day.get("avgtemp_c", 0)
    print(f"  High:          {max_f}°F ({max_c}°C)")
    print(f"  Low:           {min_f}°F ({min_c}°C)")
    print(f"  Average:       {avg_f}°F ({avg_c}°C)")

    # Wind
    max_wind = day.get("maxwind_mph", 0)
    max_wind_kph = day.get("maxwind_kph", 0)
    print(f"  Max Wind:      {max_wind} mph ({max_wind_kph} km/h)")

    # Humidity
    avg_humidity = day.get("avghumidity", 0)
    print(f"  Humidity:      {avg_humidity}%")

    # Precipitation
    precip_in = day.get("totalprecip_in", 0)
    precip_mm = day.get("totalprecip_mm", 0)
    if precip_in > 0:
        print(f"  Precipitation: {precip_in} in ({precip_mm} mm)")
    else:
        print(f"  Precipitation: None")

    # Visibility
    avg_vis_miles = day.get("avgvis_miles", 0)
    avg_vis_km = day.get("avgvis_km", 0)
    print(f"  Visibility:    {avg_vis_miles} mi ({avg_vis_km} km)")

    # UV Index
    uv = day.get("uv", 0)
    print(f"  UV Index:      {uv} ({get_uv_level(uv)})")

    # Sunrise/sunset
    sunrise = astro.get("sunrise", "")
    sunset = astro.get("sunset", "")
    if sunrise and sunset:
        print(f"  Sun:           {sunrise} - {sunset}")

    # Hourly breakdown (if requested)
    if args.hourly:
        hours = day_data.get("hour", [])
        print()
        print("  Hourly Breakdown:")
        print("  " + "-" * 56)

        for hour_data in hours:
            hour_time = hour_data.get("time", "")
            try:
                hour_obj = datetime.strptime(hour_time, "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            temp_f = hour_data.get("temp_f", 0)
            condition = hour_data.get("condition", {}).get("text", "")
            wind_mph = hour_data.get("wind_mph", 0)
            precip = hour_data.get("precip_in", 0)

            time_display = hour_obj.strftime("%I %p").lstrip("0")
            precip_str = f" | Precip: {precip} in" if precip > 0 else ""
            print(f"    {time_display:>5}: {temp_f:>3.0f}°F  {condition:<18} Wind: {wind_mph:.0f} mph{precip_str}")

    print("=" * 60)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Weather CLI - Get weather data from WeatherAPI.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CLI_EPILOG,
    )

    parser.add_argument(
        "--api-key", "-k",
        help="WeatherAPI.com API key (or set WEATHER_API_KEY env var)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Current weather command
    current_parser = subparsers.add_parser("current", help="Get current weather conditions")
    current_parser.add_argument(
        "--location", "-l",
        required=True,
        help="Location (city name, zip code, coordinates, or 'auto' for IP lookup)"
    )
    current_parser.add_argument(
        "--aqi",
        action="store_true",
        help="Include air quality data"
    )

    # Forecast command
    forecast_parser = subparsers.add_parser("forecast", help="Get weather forecast")
    forecast_parser.add_argument(
        "--location", "-l",
        required=True,
        help="Location (city name, zip code, coordinates, or 'auto' for IP lookup)"
    )
    forecast_parser.add_argument(
        "--days", "-d",
        type=int,
        default=3,
        help="Number of forecast days (1-14, default: 3)"
    )
    forecast_parser.add_argument(
        "--aqi",
        action="store_true",
        help="Include air quality data"
    )
    forecast_parser.add_argument(
        "--alerts",
        action="store_true",
        help="Include weather alerts"
    )
    forecast_parser.add_argument(
        "--hourly",
        action="store_true",
        help="Include hourly forecast for today"
    )

    # History command
    history_parser = subparsers.add_parser("history", help="Get historical weather")
    history_parser.add_argument(
        "--location", "-l",
        required=True,
        help="Location (city name, zip code, coordinates, or 'auto' for IP lookup)"
    )
    history_parser.add_argument(
        "--date", "-d",
        required=True,
        help="Date in YYYY-MM-DD format (from 2010-01-01 onwards)"
    )
    history_parser.add_argument(
        "--hourly",
        action="store_true",
        help="Include hourly breakdown"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Get API key
    api_key = args.api_key or os.environ.get("WEATHER_API_KEY")
    if not api_key:
        print("Error: API key required")
        print("Set WEATHER_API_KEY environment variable or use --api-key flag")
        print("Get a free API key at: https://www.weatherapi.com/signup.aspx")
        return 1

    # Create client and run command
    client = WeatherClient(api_key)

    if args.command == "current":
        return cmd_current(client, args)
    elif args.command == "forecast":
        return cmd_forecast(client, args)
    elif args.command == "history":
        return cmd_history(client, args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
