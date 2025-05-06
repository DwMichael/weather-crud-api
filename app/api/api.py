import os
from datetime import datetime, timedelta
import requests
from app.init_db import db
from app.models.water_balance import WaterBalance




def fetch_and_store_weather_data(location):
    try:
        base_url = os.getenv("API_BASE_URL")
        suffix = os.getenv("API_SUFFIX")
        full_url = f"{base_url}{location}{suffix}"
        print(f"FULL URL dane pogodowe z API: {full_url}")
        response = requests.get(full_url)
        print(f"RESPONSE dane pogodowe z API: {response}")
        data = response.json()
        print(f"Pobierano dane pogodowe z API: {data}")
        today = datetime.today().date()
        updates = 0
        inserts = 0
        unchanged = 0

        for i in range(30):
            forecast_date = today + timedelta(days=i)
            forecast_day = data['days'][i]


            temp = forecast_day.get('temp', 0.0)
            temp_min = forecast_day.get('tempmin', 0.0)
            temp_max = forecast_day.get('tempmax', 0.0)
            humidity = forecast_day.get('humidity', 0.0)
            precip = forecast_day.get('precip', 0.0)
            precip_type = forecast_day.get('preciptype', [])
            precip_type_str = ','.join(precip_type) if precip_type else ''
            wind_speed = forecast_day.get('windspeed', 0.0)
            conditions = forecast_day.get('conditions', '')


            existing = WaterBalance.query.filter_by(date=forecast_date).first()

            if existing:
                if (existing.temp != temp or
                        existing.temp_min != temp_min or
                        existing.temp_max != temp_max or
                        existing.humidity != humidity or
                        existing.precip != precip or
                        existing.precip_type != precip_type_str or
                        existing.wind_speed != wind_speed or
                        existing.conditions != conditions):

                    # Aktualizuj istniejący wpis
                    existing.temp = temp
                    existing.temp_min = temp_min
                    existing.temp_max = temp_max
                    existing.humidity = humidity
                    existing.precip = precip
                    existing.precip_type = precip_type_str
                    existing.wind_speed = wind_speed
                    existing.conditions = conditions
                    existing.updated_at = datetime.now()
                    updates += 1
                else:
                    unchanged += 1
            else:
                entry = WaterBalance(
                    date=forecast_date,
                    temp=temp,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    humidity=humidity,
                    precip=precip,
                    precip_type=precip_type_str,
                    wind_speed=wind_speed,
                    conditions=conditions,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.insert(entry)
                inserts += 1

            # Zatwierdź zmiany w bazie danych
        db.session.commit()
        print(f"Zaktualizowano bazę danych: {inserts} nowych wpisów, {updates} zaktualizowanych, {unchanged} bez zmian")
        return True
    except Exception as e:
        print(f"Wystąpił błąd podczas aktualizacji danych: {e}")
        db.session.rollback()  # Cofnij zmiany w przypadku błędu
        return False
