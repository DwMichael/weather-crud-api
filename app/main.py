import os
import time
from datetime import datetime, timedelta
from app.api.api import fetch_and_store_weather_data
from app.init_db import create_app


def schedule_weather_fetch():
    app = create_app()

    location = os.getenv("DEFAULT_LOCATION", "Warsaw, Poland")
    update_interval = 4 * 60 * 60

    print(f"Rozpoczęcie procesu aktualizacji pogody dla {location}")
    print(f"Interwał aktualizacji: {update_interval / 3600} godzin")

    try:
        while True:
            with app.app_context():
                print(f"Aktualizacja danych pogodowych o {datetime.now()}")
                fetch_and_store_weather_data(location)

            next_update = datetime.now() + timedelta(seconds=update_interval)
            print(f"Następna aktualizacja za {update_interval / 3600} godzin - {next_update}")
            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("Program zatrzymany przez użytkownika")
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
    finally:
        print("Zakończono działanie programu aktualizacji pogody")


if __name__ == "__main__":
    schedule_weather_fetch()