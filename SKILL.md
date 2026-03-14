---
name: weather.py
description: Get weather data from WeatherAPI.com. Use when the user asks about current weather conditions, forecasts, temperature, precipitation, or wants to know if they need an umbrella. Supports any location worldwide via city name, zip code, coordinates, or IP-based lookup.
compatibility: Requires 'weather.py' script in PATH with WEATHER_API_KEY environment variable set.
---

# Weather Data Tool

Get current weather conditions and forecasts using the `weather.py` CLI powered by WeatherAPI.com.

## Authentication

API key is loaded from environment variable:
```bash
export WEATHER_API_KEY="your_api_key_here"
```

Or passed directly: `weather.py --api-key YOUR_KEY <command>`

Get a free API key at: https://www.weatherapi.com/signup.aspx

## Commands Reference

### Current Weather
```bash
weather.py current --location "San Francisco"
weather.py current --location "94102"
weather.py current --location "51.5074,-0.1278"
weather.py current --location "auto"  # uses IP geolocation
```

Returns:
- Condition (sunny, cloudy, rain, etc.)
- Temperature (actual and feels-like)
- Wind speed, direction, and gusts
- Humidity and pressure
- Visibility
- Precipitation
- Cloud cover
- UV index

### Current Weather with Air Quality
```bash
weather.py current --location "Beijing" --aqi
weather.py current --location "Los Angeles" --aqi
```

Additional AQI data includes:
- EPA Air Quality Index
- PM2.5 and PM10 levels

### Weather Forecast
```bash
# 3-day forecast (default)
weather.py forecast --location "London"

# 7-day forecast
weather.py forecast --location "Tokyo" --days 7

# 14-day forecast (maximum)
weather.py forecast --location "Paris" --days 14
```

Returns for each day:
- Condition
- High/low temperatures
- Chance of rain/snow
- Expected precipitation
- Max wind speed
- Average humidity
- UV index
- Sunrise/sunset times

### Forecast with Alerts
```bash
weather.py forecast --location "Miami" --alerts
weather.py forecast --location "Houston" --days 5 --alerts
```

Includes active weather alerts:
- Severe weather warnings
- Flood watches
- Heat advisories
- Winter storm warnings

### Forecast with Hourly Breakdown
```bash
weather.py forecast --location "Chicago" --hourly
weather.py forecast --location "Denver" --days 3 --hourly
```

Adds hourly forecast for the current day:
- Temperature by hour
- Conditions
- Chance of rain
- Wind speed

### Full Featured Request
```bash
weather.py forecast --location "New York" --days 7 --aqi --alerts --hourly
```

## Location Formats

The `--location` parameter accepts many formats:

| Format | Example | Description |
|--------|---------|-------------|
| City name | `"London"` | Simple city lookup |
| City, Country | `"Paris, France"` | More specific |
| City, State | `"Portland, Oregon"` | US cities with same name |
| US Zip Code | `"10001"` | 5-digit zip |
| UK Postcode | `"SW1A 1AA"` | Full UK postcode |
| Canada Postal | `"M5V 3L9"` | Canadian postal code |
| Coordinates | `"48.8566,2.3522"` | Lat,lon format |
| IP Address | `"8.8.8.8"` | Any IP |
| Auto | `"auto"` | Your current IP location |
| Airport Code | `"JFK"` | IATA airport codes |

## Example Workflows

### Morning Weather Check
```bash
weather.py current --location "auto"
```

### Planning Outdoor Activity
```bash
# Check if it will rain this week
weather.py forecast --location "Seattle" --days 7

# Check UV for beach day
weather.py forecast --location "Miami Beach" --days 3
```

### Travel Preparation
```bash
# Check destination weather
weather.py forecast --location "Tokyo" --days 7 --alerts

# Check multiple cities
for city in "London" "Paris" "Rome"; do
  weather.py current --location "$city"
done
```

### Air Quality Check
```bash
weather.py current --location "Los Angeles" --aqi
weather.py current --location "Beijing" --aqi
```

### Severe Weather Monitoring
```bash
weather.py forecast --location "Houston" --alerts --days 3
```

## Understanding the Output

### Temperature
- Always shows both Fahrenheit and Celsius
- "Feels Like" accounts for wind chill and heat index

### UV Index Scale
| Value | Level | Recommendation |
|-------|-------|----------------|
| 0-2 | Low | No protection needed |
| 3-5 | Moderate | Wear sunscreen |
| 6-7 | High | Reduce sun exposure |
| 8-10 | Very High | Extra protection needed |
| 11+ | Extreme | Avoid sun exposure |

### Air Quality (EPA Index)
| Value | Level | Health Impact |
|-------|-------|---------------|
| 1 | Good | Safe for everyone |
| 2 | Moderate | Unusually sensitive people may be affected |
| 3 | Unhealthy (Sensitive) | Sensitive groups should reduce outdoor activity |
| 4 | Unhealthy | Everyone should reduce outdoor activity |
| 5 | Very Unhealthy | Avoid outdoor activity |
| 6 | Hazardous | Stay indoors |

### Precipitation Chance
- "Chance of Rain: 70%" means 70% probability of rain at some point
- "Expected: 0.5 in" means total expected accumulation

## Tips

- Use `auto` for quick local weather without typing location
- Add `--aqi` in cities with air quality concerns
- Use `--alerts` during storm season or severe weather periods
- The `--hourly` flag helps plan around specific times
- Coordinates work great for exact locations (parks, venues)
- Free API tier allows 1 million calls/month
