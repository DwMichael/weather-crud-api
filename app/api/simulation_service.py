import os
import requests
from datetime import datetime, date, timedelta
from flask import current_app as app


class UserData:
    def __init__(self, tank_capacity, min_water_level, daily_water_usage, rooftop_size, location,
                 initial_water_level=None):
        try:
            self.tank_capacity = float(tank_capacity)
            self.min_water_level = float(min_water_level)
            self.daily_water_usage = float(daily_water_usage)
            self.rooftop_size = float(rooftop_size)
            self.location = str(location)
            self.initial_water_level = float(initial_water_level) if initial_water_level is not None else None
        except ValueError as e:
            raise ValueError(f"Invalid input type for UserData: {e}")

    def __repr__(self):
        return (f"UserData(tank_capacity={self.tank_capacity}, "
                f"min_water_level={self.min_water_level}, "
                f"daily_water_usage={self.daily_water_usage}, "
                f"rooftop_size={self.rooftop_size}, "
                f"location='{self.location}',"
                f"initial_water_level={self.initial_water_level})")



def run_water_simulation(user_data: UserData, full_rainfall_forecast: list[tuple[date, float]]) -> list[dict]:

    tank_capacity = user_data.tank_capacity
    min_water_level_config = user_data.min_water_level
    daily_consumption = user_data.daily_water_usage
    roof_surface = user_data.rooftop_size


    max_water_level = tank_capacity * 0.95

    simulation_results = []

    current_water_level = user_data.initial_water_level if user_data.initial_water_level is not None else min_water_level_config


    current_water_level = max(0, min(current_water_level, max_water_level))

    num_simulation_days = min(30, len(full_rainfall_forecast))

    for day_index in range(num_simulation_days):
        forecast_date, daily_rainfall_mm = full_rainfall_forecast[day_index]

        consumed_today = daily_consumption
        current_water_level -= consumed_today
        current_water_level = max(0, current_water_level)

        rainwater_collected_liters = daily_rainfall_mm * roof_surface
        current_water_level += rainwater_collected_liters

        pumped_up_today = 0.0
        overflow_today = 0.0

        if current_water_level > max_water_level:
            overflow_today = current_water_level - max_water_level
            current_water_level = max_water_level

        if current_water_level < min_water_level_config:
            pumped_up_today = min_water_level_config - current_water_level
            current_water_level += pumped_up_today

            if current_water_level > max_water_level:
                pump_overflow = current_water_level - max_water_level
                overflow_today += pump_overflow
                current_water_level = max_water_level
                pumped_up_today -= pump_overflow

        daily_result = {
            "date": forecast_date,
            "water_amount_eod": round(current_water_level, 2),
            "rainfall_forecast_mm": round(daily_rainfall_mm, 2),
            "daily_consumption": round(consumed_today, 2),
            "saved_water_from_rain": round(rainwater_collected_liters, 2),
            "pumped_up_municipal_water": round(pumped_up_today, 2),
            "overflow_water_lost": round(overflow_today, 2),
        }
        simulation_results.append(daily_result)

    return simulation_results