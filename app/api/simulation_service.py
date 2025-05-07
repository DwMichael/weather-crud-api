import os
import requests
from datetime import datetime, date, timedelta
from flask import current_app as app  # or from your Flask app if used directly


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
    """
    Runs the 30-day water balance simulation.
    Returns a list of dictionaries, each representing a day's balance record.
    """
    tank_capacity = user_data.tank_capacity
    min_water_level_config = user_data.min_water_level  # Configured minimum
    daily_consumption = user_data.daily_water_usage
    roof_surface = user_data.rooftop_size

    # Max level is 95% of capacity
    max_water_level = tank_capacity * 0.95

    simulation_results = []

    # Determine initial water level for the simulation
    # If user provides one, use it. Otherwise, start at configured minimum.
    current_water_level = user_data.initial_water_level if user_data.initial_water_level is not None else min_water_level_config

    # Ensure initial level is within tank bounds
    current_water_level = max(0, min(current_water_level, max_water_level))

    # The simulation logic from Tkinter was for 61 steps (i=0 to 60) for 30 days.
    # Day 0: Initial state.
    # Day 1 (morning): Consumption. Day 1 (evening/next morning): Rain + Pump.
    # This means rainfall_forecast[0] is for the first day of rain collection.

    # Let's iterate 30 times, each iteration representing one full day cycle.
    num_simulation_days = min(30, len(full_rainfall_forecast))

    for day_index in range(num_simulation_days):
        forecast_date, daily_rainfall_mm = full_rainfall_forecast[day_index]

        # 1. Water Consumption at the start of the day (or end of previous)
        consumed_today = daily_consumption
        current_water_level -= consumed_today
        current_water_level = max(0, current_water_level)  # Cannot go below 0

        # 2. Rainwater Collection
        # Rainfall (mm) * roof surface (m^2) = liters of water (1mm on 1m^2 = 1 liter)
        rainwater_collected_liters = daily_rainfall_mm * roof_surface
        current_water_level += rainwater_collected_liters

        # Water saved is the amount of rainwater collected that fits in the tank up to max_water_level
        # and reduces the need for pumping or is stored.
        # This definition of "saved_water" might differ from Tkinter's.
        # Tkinter's `saved_water = rainfall_data[x] * roof_surface` was potential collection.
        # Let's track actual collected and used/stored.
        actual_saved_from_rain = rainwater_collected_liters  # Potential

        pumped_up_today = 0.0
        overflow_today = 0.0

        # 3. Check for overflow
        if current_water_level > max_water_level:
            overflow_today = current_water_level - max_water_level
            current_water_level = max_water_level
            # Adjust actual_saved_from_rain if overflow occurred due to rain
            # If (level before rain + rain) > max_level, then saved is only what fit.
            # This is complex. Let's simplify: actual_saved_from_rain is what was added.
            # The overflow_today captures the excess.

        # 4. Check if pumping is needed (after consumption and rain)
        if current_water_level < min_water_level_config:
            pumped_up_today = min_water_level_config - current_water_level
            current_water_level += pumped_up_today
            # Ensure pumping doesn't cause overflow (edge case if min_level_config > max_water_level, which is a config error)
            if current_water_level > max_water_level:
                pump_overflow = current_water_level - max_water_level
                overflow_today += pump_overflow  # Add to any previous rain overflow
                current_water_level = max_water_level
                pumped_up_today -= pump_overflow  # We pumped less effectively

        # Store results for the day
        daily_result = {
            "date": forecast_date,
            "water_amount_eod": round(current_water_level, 2),
            "rainfall_forecast_mm": round(daily_rainfall_mm, 2),
            "daily_consumption": round(consumed_today, 2),  # This is the user's configured daily consumption
            "saved_water_from_rain": round(rainwater_collected_liters, 2),  # Total potential rain collected
            "pumped_up_municipal_water": round(pumped_up_today, 2),
            "overflow_water_lost": round(overflow_today, 2),
        }
        simulation_results.append(daily_result)

    return simulation_results