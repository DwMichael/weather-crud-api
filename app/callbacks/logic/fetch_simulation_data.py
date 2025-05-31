import requests

def fetch_simulation_data(location, tank_capacity, min_water_level, daily_use, roof_area):
    payload = {
        "tank_capacity": tank_capacity,
        "min_water_level": min_water_level,
        "daily_water_usage": daily_use,
        "rooftop_size": roof_area,
        "location": location,
    }
    response = requests.post("http://localhost:5000/api/simulation", json=payload)
    if response.status_code != 200:
        raise Exception("Błąd API: {}".format(response.text))
    return response.json()
