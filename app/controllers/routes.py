from flask import Blueprint, jsonify, request
from datetime import datetime,date,time
from sqlalchemy.exc import OperationalError
from app.init_db import db
from app.models.user_data import UserData
from app.models.water_balance import WaterBalance
from app.api.weather_data_service import fetch_rainfall_forecast
from app.api.simulation_service import run_water_simulation
from app.api.simulation_service import run_water_simulation_fuzzy


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

        # Run PI controller simulation
        pi_simulation_daily_records = run_water_simulation(user_data, rainfall_forecast_tuples)
        
        # Run Fuzzy controller simulation
        fuzzy_simulation_daily_records = run_water_simulation_fuzzy(user_data, rainfall_forecast_tuples)
        
        pi_records_for_response_and_db = []

        # Process and save PI controller results to DB
        try:
            for day_record_dict in pi_simulation_daily_records:
                if isinstance(day_record_dict["date"], date):
                    date_str = day_record_dict["date"].isoformat()
                else:
                    # Assuming it's already a string if not a date object
                    date_str = str(day_record_dict["date"])

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
                        if key != 'date': # Don't try to update the primary key part of a composite or unique constraint
                            setattr(existing_record, key, value)
                    db.session.add(existing_record)
                    pi_records_for_response_and_db.append(existing_record.to_json())
                else:
                    new_record = WaterBalance(**db_dict)
                    db.session.add(new_record)
                    # We need to flush to get the ID if it's auto-generated and to_json() needs it,
                    # or ensure to_json() can handle it before commit.
                    # For simplicity, assuming to_json() works with the current state.
                    pi_records_for_response_and_db.append(new_record.to_json()) # This might need adjustment if to_json relies on committed state

            db.session.commit()
            # Re-fetch or ensure to_json() works correctly for newly added records if they were not complete
            # For this example, we assume `new_record.to_json()` worked with uncommitted data or `to_json` is robust.
            # A safer approach for new records might be to query them after commit or build JSON from db_dict.
            # However, to keep changes minimal to the existing structure:
            # We will use the pi_records_for_response_and_db list as built.

        except Exception as db_error:
            db.session.rollback()
            # Log the database error
            # current_app.logger.error(f"Database error: {str(db_error)}")
            return jsonify({"error": f"Database error: {str(db_error)}"}), 500
        
        # Prepare the final response
        response_data = {
            "pi_controller_results": pi_records_for_response_and_db,
            "fuzzy_controller_results": fuzzy_simulation_daily_records # Already a list of dicts
        }
        
        return jsonify(response_data), 200

    except ConnectionError as e:
        # current_app.logger.error(f"External API connection error: {str(e)}")
        return jsonify({"error": f"External API connection error: {str(e)}"}), 503
    except ValueError as e:
        # current_app.logger.error(f"Data processing error: {str(e)}")
        return jsonify({"error": f"Data processing error: {str(e)}"}), 400
    except Exception as e:
        # current_app.logger.error(f"An internal server error occurred: {str(e)}")
        db.session.rollback() # Ensure rollback on any other unexpected error
        return jsonify({"error": f"An internal server error occurred: {str(e)}"}), 500
