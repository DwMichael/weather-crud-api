import os
import requests
from datetime import datetime, date, timedelta
from flask import current_app as app



def fetch_rainfall_forecast(location: str, days: int = 30) -> list[tuple[date, float]]:
    base_url = os.getenv("API_BASE_URL")
    api_suffix_key = os.getenv(
        "API_SUFFIX")

    if not base_url or not api_suffix_key:
        app.logger.error("Weather API URL or Suffix/Key not configured in environment variables.")
        raise ConnectionError("Weather API configuration is missing.")

    weather_api_key = os.getenv("API_KEY")
    if not weather_api_key:
        app.logger.warning("WEATHER_API_KEY not set, attempting to use suffix as full query string.")

    api_base_url_env = os.getenv("API_BASE_URL")
    api_suffix_env = os.getenv("API_SUFFIX")

    if not api_base_url_env or not api_suffix_env:
        app.logger.error("API_BASE_URL or API_SUFFIX not configured.")
        raise ConnectionError("Weather API URL components are missing in environment variables.")

    full_url = f"{api_base_url_env}{location}{api_suffix_env}"

    app.logger.info(f"Fetching weather data from: {full_url}")

    try:
        response = requests.get(full_url, timeout=15)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching weather data for {location}: {e}")
        raise ConnectionError(f"Could not fetch weather data: {e}")
    except ValueError as e:
        app.logger.error(f"Error decoding weather API JSON response: {e}")
        raise ValueError(f"Invalid JSON response from weather API: {e}")

    rainfall_data = []
    if 'days' not in api_data or not isinstance(api_data['days'], list):
        app.logger.error(f"Unexpected API response structure for {location}. 'days' array missing or not a list.")
        raise ValueError("Weather API response format error: 'days' field is missing or invalid.")

    num_forecast_days = min(days, len(api_data['days']))

    for i in range(num_forecast_days):
        day_data = api_data['days'][i]
        try:
            forecast_date_str = day_data['datetime']
            forecast_date_obj = datetime.strptime(forecast_date_str, '%Y-%m-%d').date()

            precip_mm = 0.0

            if day_data.get('precip') is not None:
                preciptype = day_data.get('preciptype')
                if preciptype is None or 'rain' in preciptype:  # Consider snow as non-collectable for simplicity
                    precip_mm = float(day_data['precip'])

            rainfall_data.append((forecast_date_obj, precip_mm))
        except KeyError as e:
            app.logger.warning(f"Missing key {e} in day data for {location} on index {i}. Using default.")
        except ValueError as e:
            app.logger.warning(f"Data type error for day data {location} on index {i}: {e}. Using default.")

    if len(rainfall_data) < days:
        app.logger.warning(
            f"Weather API returned only {len(rainfall_data)} days of forecast for {location}, requested {days}.")

    return rainfall_data