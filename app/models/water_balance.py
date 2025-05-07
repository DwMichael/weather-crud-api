import os
from app.init_db import db
from datetime import datetime, date

class WaterBalance(db.Model):
    __tablename__ = 'water_balance'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    water_amount = db.Column(db.Float)
    rainfall_amount = db.Column(db.Float)
    daily_consumption = db.Column(db.Float)
    saved_water = db.Column(db.Float)
    pumped_up_water = db.Column(db.Float)
    pumped_out_water = db.Column(db.Float)

    def to_json(self):
        return {
            "id": self.id,
            "date": self.date if isinstance(self.date, str) else self.date.isoformat(),
            "water_amount": self.water_amount,
            "rainfall_amount": self.rainfall_amount,
            "daily_consumption": self.daily_consumption,
            "saved_water": self.saved_water,
            "pumped_up_water": self.pumped_up_water,
            "pumped_out_water": self.pumped_out_water
        }
