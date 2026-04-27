class Car:
    def __init__(self, car_id, brand, model, year, price_per_day):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.year = year
        self.price_per_day = price_per_day
        self.is_available = True

    def rent(self):
        if not self.is_available:
            print("Car is already rented")
            return False
        self.is_available = False
        return True

    def return_car(self):
        self.is_available = True

    def __str__(self):
        status = "Available" if self.is_available else "Rented"
        return f"{self.car_id}: {self.brand} {self.model} ({self.year}) - {status}"