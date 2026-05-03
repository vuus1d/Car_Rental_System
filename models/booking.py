class Booking:
    def __init__(self, car_id, client_name, days, total_price):
        self.car_id = car_id
        self.client_name = client_name
        self.days = days
        self.total_price = total_price
        self.is_active = True

    def complete(self):
        self.is_active = False

    def __str__(self):
        status = "Active" if self.is_active else "Completed"
        return f"{self.client_name} rented car {self.car_id} for {self.days} days - {status}"