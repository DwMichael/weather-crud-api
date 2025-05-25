import os
import requests
from datetime import datetime, date, timedelta
from flask import current_app as app
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

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



def run_water_simulation_fuzzy(user_data: UserData, full_rainfall_forecast: list[tuple[date, float]]) -> list[dict]:

    tank_capacity = user_data.tank_capacity
    min_water_level_config = user_data.min_water_level
    daily_consumption = user_data.daily_water_usage
    roof_surface = user_data.rooftop_size


    max_water_level = tank_capacity * 0.95

    simulation_results = []
    current_water_level = user_data.initial_water_level if user_data.initial_water_level is not None else min_water_level_config
    current_water_level = max(0, min(current_water_level, max_water_level))

    # Definicja zmiennych lingwistycznych (wejścia)
    # Jak bardzo brakuje wody do poziomu minimalnego
    uchyb_poziomu_wody = ctrl.Antecedent(np.arange(0, tank_capacity * 0.5, 1), 'uchyb_poziomu_wody')
    # Prognozowana ilość opadów na dany dzień
    prognoza_opadow = ctrl.Antecedent(np.arange(0, 51, 1), 'prognoza_opadow')

    # Definicja zmiennej lingwistycznej (wyjście)
    # Ile wody należy dopompować
    ilosc_do_pompowania = ctrl.Consequent(np.arange(0, tank_capacity * 0.3, 1), 'ilosc_do_pompowania')

    # Funkcje przynależności dla uchybu poziomu wody
    uchyb_poziomu_wody['maly'] = fuzz.trimf(uchyb_poziomu_wody.universe, [0, 0, tank_capacity * 0.1])
    uchyb_poziomu_wody['sredni'] = fuzz.trimf(uchyb_poziomu_wody.universe, [tank_capacity * 0.05, tank_capacity * 0.15, tank_capacity * 0.25])
    uchyb_poziomu_wody['duzy'] = fuzz.trimf(uchyb_poziomu_wody.universe, [tank_capacity * 0.2, tank_capacity * 0.35, tank_capacity * 0.5])

    # Funkcje przynależności dla prognozy opadów
    prognoza_opadow['brak'] = fuzz.trimf(prognoza_opadow.universe, [0, 0, 5])
    prognoza_opadow['maly'] = fuzz.trimf(prognoza_opadow.universe, [2, 10, 20])
    prognoza_opadow['duzy'] = fuzz.trimf(prognoza_opadow.universe, [15, 25, 50])

    # Funkcje przynależności dla ilości wody do pompowania
    ilosc_do_pompowania['nic'] = fuzz.trimf(ilosc_do_pompowania.universe, [0, 0, tank_capacity * 0.01])
    ilosc_do_pompowania['malo'] = fuzz.trimf(ilosc_do_pompowania.universe, [tank_capacity * 0.005, tank_capacity * 0.05, tank_capacity * 0.1])
    ilosc_do_pompowania['duzo'] = fuzz.trimf(ilosc_do_pompowania.universe, [tank_capacity * 0.08, tank_capacity * 0.15, tank_capacity * 0.3])

    # Definicja reguł rozmytych
    # Jeśli brakuje dużo wody i nie ma prognozy opadów, pompuj dużo.
    regula1 = ctrl.Rule(uchyb_poziomu_wody['duzy'] & prognoza_opadow['brak'], ilosc_do_pompowania['duzo'])
    # Jeśli brakuje średnio wody i opady są małe, pompuj mało.
    regula2 = ctrl.Rule(uchyb_poziomu_wody['sredni'] & prognoza_opadow['maly'], ilosc_do_pompowania['malo'])
    # Jeśli brakuje mało wody, ale prognozowane są duże opady, nie pompuj.
    regula3 = ctrl.Rule(uchyb_poziomu_wody['maly'] & prognoza_opadow['duzy'], ilosc_do_pompowania['nic'])
    # Jeśli brakuje mało wody i nie ma opadów, pompuj mało.
    regula4 = ctrl.Rule(uchyb_poziomu_wody['maly'] & prognoza_opadow['brak'], ilosc_do_pompowania['malo'])
    # Jeśli brakuje średnio wody i nie ma opadów, pompuj dużo.
    regula5 = ctrl.Rule(uchyb_poziomu_wody['sredni'] & prognoza_opadow['brak'], ilosc_do_pompowania['duzo'])
    # Jeśli brakuje dużo wody, ale są małe opady, pompuj mało (bo coś spadnie).
    regula6 = ctrl.Rule(uchyb_poziomu_wody['duzy'] & prognoza_opadow['maly'], ilosc_do_pompowania['malo'])


    # Stworzenie systemu sterowania
    system_sterowania = ctrl.ControlSystem([regula1, regula2, regula3, regula4, regula5, regula6])
    symulacja_sterowania = ctrl.ControlSystemSimulation(system_sterowania)

    num_simulation_days = min(30, len(full_rainfall_forecast))

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

        # 4. Logika regulatora rozmytego do pompowania wody
        if current_water_level < min_water_level_config:
            error_poziomu = min_water_level_config - current_water_level
            symulacja_sterowania.input['uchyb_poziomu_wody'] = error_poziomu
            symulacja_sterowania.input['prognoza_opadow'] = daily_rainfall_mm

            try:
                symulacja_sterowania.compute()
                fuzzy_controlled_pump_amount = symulacja_sterowania.output['ilosc_do_pompowania']
            except Exception as e: # Proste obsłużenie błędu, gdyby reguły nie pokryły przypadku
                app.logger.error(f"Błąd w obliczeniach regulatora rozmytego: {e}, uchyb: {error_poziomu}, opad: {daily_rainfall_mm}")
                fuzzy_controlled_pump_amount = 0 # W razie błędu nie pompuj

            amount_to_attempt_pumping = max(0, fuzzy_controlled_pump_amount)

            space_available_in_tank = max_water_level - current_water_level
            actual_pumped_this_step = min(amount_to_attempt_pumping, space_available_in_tank)
            actual_pumped_this_step = max(0, actual_pumped_this_step)

            current_water_level += actual_pumped_this_step
            pumped_up_for_reporting = actual_pumped_this_step
        
        current_water_level = min(current_water_level, max_water_level)

        daily_result = {
            "date": forecast_date.isoformat() if isinstance(forecast_date, date) else str(forecast_date),
            "water_amount": round(current_water_level, 2),
            "rainfall_amount": round(daily_rainfall_mm, 2),
            "daily_consumption": round(water_consumed_today, 2),
            "saved_water": round(rainwater_collected_liters, 2),
            "pumped_up_water": round(pumped_up_for_reporting, 2),
            "pumped_out_water": round(overflow_for_reporting, 2),
        }
        simulation_results.append(daily_result)

    return simulation_results