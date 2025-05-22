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

    # Parametry regulatora PI
    Kp = 0.8  # Wzmocnienie proporcjonalne
    Ki = 0.1  # Wzmocnienie całkujące
    integral_error = 0.0 # Błąd całkujący

    for day_index in range(num_simulation_days):
        forecast_date, daily_rainfall_mm = full_rainfall_forecast[day_index]

        pumped_up_for_reporting = 0.0
        overflow_for_reporting = 0.0
        water_consumed_today = daily_consumption

        # 1. Zużycie wody
        current_water_level -= water_consumed_today
        current_water_level = max(0, current_water_level)

        # 2. Zbieranie deszczówki
        rainwater_collected_liters = daily_rainfall_mm * roof_surface
        current_water_level += rainwater_collected_liters

        # 3. Obsługa przepełnienia
        if current_water_level > max_water_level:
            overflow_amount = current_water_level - max_water_level
            overflow_for_reporting += overflow_amount
            current_water_level = max_water_level

        # 4. Logika regulatora PI do pompowania wody
        if current_water_level < min_water_level_config:
            error = min_water_level_config - current_water_level # Uchyb regulacji
            integral_error += error # Akumulacja błędu
            
            # Opcjonalnie: Ograniczenie błędu całkowania (anti-windup)
            # integral_limit = tank_capacity
            # integral_error = max(-integral_limit, min(integral_error, integral_limit))

            # Ilość wody do napompowania wg regulatora PI
            pi_controlled_pump_amount = Kp * error + Ki * integral_error
            amount_to_attempt_pumping = max(0, pi_controlled_pump_amount)

            # Rzeczywista ilość napompowanej wody, uwzględniając pojemność zbiornika
            space_available_in_tank = max_water_level - current_water_level
            actual_pumped_this_step = min(amount_to_attempt_pumping, space_available_in_tank)
            actual_pumped_this_step = max(0, actual_pumped_this_step) 

            current_water_level += actual_pumped_this_step
            pumped_up_for_reporting = actual_pumped_this_step

            # Anti-windup: Korekta błędu całkowania, jeśli nie można było napompować żądanej ilości
            if amount_to_attempt_pumping > actual_pumped_this_step:
                unfulfilled_pumping = amount_to_attempt_pumping - actual_pumped_this_step
                integral_error -= unfulfilled_pumping 
        else:
            # Reset błędu całkowania, gdy poziom wody jest wystarczający
            integral_error = 0.0
        
        current_water_level = min(current_water_level, max_water_level)

        daily_result = {
            "date": forecast_date,
            "water_amount_eod": round(current_water_level, 2),
            "rainfall_forecast_mm": round(daily_rainfall_mm, 2),
            "daily_consumption": round(water_consumed_today, 2),
            "saved_water_from_rain": round(rainwater_collected_liters, 2),
            "pumped_up_municipal_water": round(pumped_up_for_reporting, 2),
            "overflow_water_lost": round(overflow_for_reporting, 2),
        }
        simulation_results.append(daily_result)

    return simulation_results