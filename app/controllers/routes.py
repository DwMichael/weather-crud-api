from flask import Blueprint, jsonify, request
from datetime import datetime,date,time
from sqlalchemy.exc import OperationalError
from app.init_db import db
from app.models.user_data import UserData
from app.models.water_balance import WaterBalance
from app.api.weather_data_service import fetch_rainfall_forecast
from app.api.simulation_service import run_water_simulation

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/connection', methods=['GET'])
def connection_check():
    db_status = "OK"
    db_error_message = None
    try:
        db.session.execute(db.text("SELECT 1"))
    except OperationalError as e:
        db_status = "Error"
        db_error_message = str(e)

    response_data = {
        "service_status": "OK",
        "message": "Hello! You've connected to the Weather Backend Service.",
        "timestamp": datetime.utcnow().isoformat(),
        "database_connection": db_status
    }
    if db_error_message:
        response_data["database_error_details"] = db_error_message

    status_code = 200 if db_status == "OK" else 503
    return jsonify(response_data), status_code


@routes_bp.route('/api/simulation', methods=['POST'])
def handle_simulation_request():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    required_fields = ["tank_capacity", "min_water_level", "daily_water_usage", "rooftop_size", "location"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing one or more required fields: {', '.join(required_fields)}"}), 400
    print("DANE OD USERA ", required_fields)
    try:
        user_data = UserData(
            tank_capacity=data["tank_capacity"],
            min_water_level=data["min_water_level"],
            daily_water_usage=data["daily_water_usage"],
            rooftop_size=data["rooftop_size"],
            location=data["location"],
            initial_water_level=data.get("initial_water_level")  # Optional
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        rainfall_forecast_tuples = fetch_rainfall_forecast(user_data.location, days=30)
        if not rainfall_forecast_tuples:
            return jsonify({"error": "Could not retrieve rainfall forecast data."}), 500


        simulation_daily_records = run_water_simulation(user_data, rainfall_forecast_tuples)
        saved_records_json = []

        try:
            for day_record_dict in simulation_daily_records:
                if isinstance(day_record_dict["date"], date):
                    date_str = day_record_dict["date"].isoformat()
                else:
                    date_str = day_record_dict["date"]

                db_dict = {
                    "date": date_str,
                    "water_amount": day_record_dict["water_amount_eod"],
                    "rainfall_amount": day_record_dict["rainfall_forecast_mm"],
                    "daily_consumption": day_record_dict["daily_consumption"],
                    "saved_water": day_record_dict["saved_water_from_rain"],
                    "pumped_up_water": day_record_dict["pumped_up_municipal_water"],
                    "pumped_out_water": day_record_dict["overflow_water_lost"]
                }

                existing_record = WaterBalance.query.filter_by(date=date_str).first()

                if existing_record:
                    for key, value in db_dict.items():
                        if key != 'date':
                            setattr(existing_record, key, value)
                    db.session.add(existing_record)
                    saved_records_json.append(existing_record.to_json())
                else:
                    new_record = WaterBalance(**db_dict)
                    db.session.add(new_record)
                    saved_records_json.append(new_record.to_json())

            db.session.commit()
            return jsonify(saved_records_json), 200

        except Exception as db_error:
            db.session.rollback()
            raise Exception(f"Database error: {str(db_error)}")

    except ConnectionError as e:
        return jsonify({"error": f"External API connection error: {str(e)}"}), 503
    except ValueError as e:
        return jsonify({"error": f"Data processing error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500