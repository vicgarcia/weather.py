# weather.py

A simple CLI for getting weather data from WeatherAPI.com.

## Features

- **Single-file executable** - Uses `uv run --script` with inline dependencies (PEP 723)
- **Current conditions** - Temperature, wind, humidity, UV, cloud cover, and more
- **Multi-day forecasts** - Up to 14 days with daily and hourly breakdowns
- **Air quality data** - EPA index, PM2.5, PM10 levels
- **Weather alerts** - Severe weather warnings and advisories
- **Flexible locations** - City names, zip codes, coordinates, airport codes, or IP lookup
- **Dual units** - Always shows both Fahrenheit/Celsius and imperial/metric

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- WeatherAPI.com API key (free tier available)

## Installation

```bash
# Clone and make executable
git clone https://github.com/vicgarcia/weather.py.git
cd weather.py
chmod +x weather.py

# Run
./weather.py --help

# Install
cp weather.py ~/.local/bin
chmod +x ~/.local/bin/weather.py

# Set API key
export WEATHER_API_KEY="your_api_key_here"
```

Get a free API key at: https://www.weatherapi.com/signup.aspx

## Commands

| Command | Description |
|---------|-------------|
| `current` | Get current weather conditions |
| `forecast` | Get weather forecast (1-14 days) |

## Usage

Set your API key via environment variable:
```bash
export WEATHER_API_KEY="your_api_key_here"
```

Or pass it as an argument: `--api-key YOUR_KEY`

### Current Weather

```bash
# By city name
weather.py current --location "San Francisco"

# By zip code
weather.py current --location "94102"

# By coordinates
weather.py current --location "37.7749,-122.4194"

# Auto-detect location via IP
weather.py current --location "auto"

# With air quality data
weather.py current --location "Beijing" --aqi
```

### Weather Forecast

```bash
# 3-day forecast (default)
weather.py forecast --location "London"

# 7-day forecast
weather.py forecast --location "Tokyo" --days 7

# With weather alerts
weather.py forecast --location "Miami" --days 5 --alerts

# With hourly breakdown
weather.py forecast --location "Chicago" --hourly

# Full featured
weather.py forecast --location "New York" --days 7 --aqi --alerts --hourly
```

## Location Formats

The `--location` parameter is flexible:

| Format | Example |
|--------|---------|
| City name | `"London"` |
| City, Country | `"Paris, France"` |
| City, State | `"Portland, Oregon"` |
| US Zip Code | `"10001"` |
| UK Postcode | `"SW1A 1AA"` |
| Canada Postal | `"M5V 3L9"` |
| Coordinates | `"48.8566,2.3522"` |
| IP Address | `"8.8.8.8"` |
| Auto (your IP) | `"auto"` |
| Airport Code | `"JFK"` |

## Command Options

### Current Command

| Option | Description |
|--------|-------------|
| `--location`, `-l` | Location to query (required) |
| `--aqi` | Include air quality data |

### Forecast Command

| Option | Default | Description |
|--------|---------|-------------|
| `--location`, `-l` | required | Location to query |
| `--days`, `-d` | 3 | Forecast days (1-14) |
| `--aqi` | off | Include air quality data |
| `--alerts` | off | Include weather alerts |
| `--hourly` | off | Include hourly forecast for today |

## Output Data

### Current Weather Includes

- Local time
- Condition (sunny, cloudy, rain, etc.)
- Temperature (actual and feels-like)
- Wind speed, direction, and gusts
- Humidity
- Barometric pressure
- Visibility
- Precipitation
- Cloud cover percentage
- UV index with level (Low/Moderate/High/Very High/Extreme)
- Air quality (with `--aqi`)

### Forecast Includes

- Daily high/low temperatures
- Weather condition
- Chance of rain/snow
- Expected precipitation
- Max wind speed
- Average humidity
- UV index
- Sunrise/sunset times
- Hourly breakdown (with `--hourly`)
- Active alerts (with `--alerts`)

## UV Index Reference

| Value | Level | Recommendation |
|-------|-------|----------------|
| 0-2 | Low | No protection needed |
| 3-5 | Moderate | Wear sunscreen |
| 6-7 | High | Reduce sun exposure |
| 8-10 | Very High | Extra protection needed |
| 11+ | Extreme | Avoid sun exposure |

## Air Quality Reference (EPA Index)

| Value | Level | Health Impact |
|-------|-------|---------------|
| 1 | Good | Safe for everyone |
| 2 | Moderate | Sensitive people may be affected |
| 3 | Unhealthy (Sensitive) | Sensitive groups reduce outdoor activity |
| 4 | Unhealthy | Everyone reduce outdoor activity |
| 5 | Very Unhealthy | Avoid outdoor activity |
| 6 | Hazardous | Stay indoors |

## Agent Skill

This project includes a `SKILL.md` file for use with AI coding agents (Claude Code, etc.). The skill enables natural language weather queries.

### Installation

```bash
# Create skills directory
mkdir -p /path/to/agent/skills

# Copy SKILL.md
cp /path/to/weather.py/SKILL.md /path/to/agent/skills/weather.py/SKILL.md

# Ensure weather.py is in PATH (see installation above)

# Set API key (in bashrc, zshrc, ...)
export WEATHER_API_KEY="your_api_key_here"
```

### Usage with Claude Code

Add the skills directory to your agent configuration, then interact naturally:

> "What's the weather like in San Francisco?"
> "Will it rain in Seattle this week?"
> "Check the UV index in Miami"
> "Is the air quality good in Beijing today?"
> "What's the forecast for my trip to Tokyo next week?"

The agent reads `SKILL.md` to understand available commands, parameters, and how to interpret weather data.

## API Information

- **Provider**: WeatherAPI.com
- **Free tier**: 1 million calls/month
- **Data sources**: Multiple weather data providers
- **Update frequency**: Every 10-15 minutes
- **Coverage**: Worldwide
