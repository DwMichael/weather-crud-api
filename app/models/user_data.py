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

