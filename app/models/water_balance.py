from app.init_db import db

class WaterBalance(db.Model):
    __tablename__ = 'water_balance'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    water_amount = db.Column(db.Float, nullable=False)
    rainfall_amount = db.Column(db.Float, nullable=False)
    daily_consumption = db.Column(db.Float, nullable=False)
    saved_water = db.Column(db.Float, nullable=False)
    pumped_up_water = db.Column(db.Float, nullable=False)
    pumped_out_water = db.Column(db.Float, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "water_amount": self.water_amount,
            "rainfall_amount": self.rainfall_amount,
            "daily_consumption": self.daily_consumption,
            "saved_water": self.saved_water,
            "pumped_up_water": self.pumped_up_water,
            "pumped_out_water": self.pumped_out_water
        }
