import os
import requests
from datetime import datetime, date, timedelta
from flask import current_app as app  # or from your Flask app if used directly



def fetch_rainfall_forecast(location: str, days: int = 30) -> list[tuple[date, float]]:
    """
    Fetches daily rainfall forecast (precip in mm) for the given location for a number of days.
    Returns a list of tuples: (date_obj, precip_mm).
    """
    base_url = os.getenv("API_BASE_URL")
    api_suffix_key = os.getenv(
        "API_SUFFIX")  # Example: /next30days?unitGroup=metric&include=days&key=YOUR_API_KEY&contentType=json

    if not base_url or not api_suffix_key:
        app.logger.error("Weather API URL or Suffix/Key not configured in environment variables.")
        raise ConnectionError("Weather API configuration is missing.")

    # The VisualCrossing API seems to take {location}/next{N}days?params
    # So, we construct the URL carefully. Assuming the suffix contains the query part.
    # If the API expects "next30days" to be part of the base_url or suffix, adjust accordingly.
    # For this example, assuming location is part of the path and 'nextXdays' is also handled.
    # A common pattern is base_url + location + "/next" + str(days) + "days" + api_suffix_key
    # The user's example was: base_url + location + suffix (where suffix included /next30days and key)
    # Let's adapt to that:

    # Ensure location is URL-encoded if it contains spaces or special characters
    # For VisualCrossing, it's typically part of the path, e.g., timeline/{location}/next{days}days
    # The user's original code had: "timeline/" + location + "/next30days?..."
    # So, the base_url should probably end before 'timeline/', or 'timeline/' should be part of it.
    # And suffix would start with '/next30days...' OR the number of days should be dynamic.

    # Let's assume base_url is like: "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/"
    # And suffix_key is like: "timeline/{location}/next{days}days?unitGroup=metric&include=days&key=YOURKEY&contentType=json"
    # This requires inserting location and days into the suffix_key template.
    # Or, simpler, if suffix_key is just the params: "?unitGroup=metric&key=YOURKEY..."
    # and the path construction is separate.

    # Based on user's Tkinter example:
    # complete_api_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + location + "/next30days?unitGroup=metric&include=days&key=WBGD4FB23FTPVH9NGQGV2QMSX&contentType=json"
    # So, base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    # And suffix = "/next30days?unitGroup=metric&include=days&key=YOUR_KEY&contentType=json" (location inserted between)

    # Let's use a more flexible approach where suffix might contain placeholders or be appended.
    # For this implementation, I'll assume suffix_key is everything *after* the location and day specifier.
    # E.g. WEATHER_API_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    # E.g. WEATHER_API_SUFFIX_KEY = "?unitGroup=metric&include=days&key=YOUR_API_KEY&contentType=json"
    # Then url = f"{base_url}/{location}/next{days}days{api_suffix_key}"

    # Using the structure from user's `fetch_and_store_weather_data` for `full_url`:
    # full_url = f"{base_url}{location}{suffix}"
    # This implies base_url ends before location, and suffix starts after location but includes day range and key.
    # Let's assume WEATHER_API_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    # And WEATHER_API_SUFFIX_KEY = "/next30days?unitGroup=metric&include=days&key=YOUR_API_KEY&contentType=json" (for 30 days fixed)
    # Or if we want dynamic days:
    # WEATHER_API_SUFFIX_TEMPLATE = "/next{}days?unitGroup=metric&include=days&key={}&contentType=json"
    # For simplicity, let's use the fixed 30 days as per original example.

    weather_api_key = os.getenv("API_KEY")  # If key is separate
    if not weather_api_key:
        app.logger.warning("WEATHER_API_KEY not set, attempting to use suffix as full query string.")

    # Constructing URL based on original Tkinter script's format
    # Assuming WEATHER_API_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    # And WEATHER_API_KEY is the actual key string.
    # The suffix part will be constructed.

    # Let's use the user's provided environment variable names:
    # base_url = os.getenv("API_BASE_URL")
    # suffix = os.getenv("API_SUFFIX") # This suffix should contain the key and other params
    # full_url = f"{base_url}{location}{suffix}"
    # This is the most direct interpretation of their `fetch_and_store_weather_data` env vars.

    api_base_url_env = os.getenv("API_BASE_URL")
    api_suffix_env = os.getenv("API_SUFFIX")

    if not api_base_url_env or not api_suffix_env:
        app.logger.error("API_BASE_URL or API_SUFFIX not configured.")
        raise ConnectionError("Weather API URL components are missing in environment variables.")

    # Ensure location is properly encoded if it contains spaces etc.
    # However, VisualCrossing often takes city names directly.
    full_url = f"{api_base_url_env}{location}{api_suffix_env}"

    app.logger.info(f"Fetching weather data from: {full_url}")

    try:
        response = requests.get(full_url, timeout=15)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        api_data = response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching weather data for {location}: {e}")
        raise ConnectionError(f"Could not fetch weather data: {e}")
    except ValueError as e:  # Includes JSONDecodeError
        app.logger.error(f"Error decoding weather API JSON response: {e}")
        raise ValueError(f"Invalid JSON response from weather API: {e}")

    rainfall_data = []
    if 'days' not in api_data or not isinstance(api_data['days'], list):
        app.logger.error(f"Unexpected API response structure for {location}. 'days' array missing or not a list.")
        raise ValueError("Weather API response format error: 'days' field is missing or invalid.")

    # Ensure we don't go out of bounds if API returns fewer days than requested
    num_forecast_days = min(days, len(api_data['days']))

    for i in range(num_forecast_days):
        day_data = api_data['days'][i]
        try:
            # Parse date string to date object
            # VisualCrossing 'datetime' is usually 'YYYY-MM-DD'
            forecast_date_str = day_data['datetime']
            forecast_date_obj = datetime.strptime(forecast_date_str, '%Y-%m-%d').date()

            precip_mm = 0.0
            # Check if 'precip' is present and if 'rain' is in 'preciptype'
            if day_data.get('precip') is not None:
                preciptype = day_data.get('preciptype')
                if preciptype is None or 'rain' in preciptype:  # Consider snow as non-collectable for simplicity
                    precip_mm = float(day_data['precip'])

            rainfall_data.append((forecast_date_obj, precip_mm))
        except KeyError as e:
            app.logger.warning(f"Missing key {e} in day data for {location} on index {i}. Using default.")
            # Decide on default: could skip day, or use 0 precip. For now, 0 precip.
            # If date is missing, this is more problematic. For now, assume date is present.
            # If date parsing fails, it will raise ValueError.
            # rainfall_data.append((datetime.today().date() + timedelta(days=i), 0.0)) # Fallback date
        except ValueError as e:
            app.logger.warning(f"Data type error for day data {location} on index {i}: {e}. Using default.")
            # rainfall_data.append((datetime.today().date() + timedelta(days=i), 0.0)) # Fallback date

    if len(rainfall_data) < days:
        app.logger.warning(
            f"Weather API returned only {len(rainfall_data)} days of forecast for {location}, requested {days}.")
        # Optionally, pad with 0 rainfall for remaining days if strict 30 days are needed by simulation
        # current_last_date = rainfall_data[-1][0] if rainfall_data else datetime.today().date() - timedelta(days=1)
        # for i in range(days - len(rainfall_data)):
        #    current_last_date += timedelta(days=1)
        #    rainfall_data.append((current_last_date, 0.0))

    return rainfall_data