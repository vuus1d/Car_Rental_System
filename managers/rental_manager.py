from models.car import Car
from models.client import Client
from models.booking import Booking


class RentalManager:
    def __init__(self):
        self.cars = []
        self.clients = []
        self.bookings = []

    def add_car(self, car):
        self.cars.append(car)

    def add_client(self, client):
        self.clients.append(client)

    def show_cars(self):
        for car in self.cars:
            print(car)

    def rent_car(self, car_id, client_name, days):
        for car in self.cars:
            if car.car_id == car_id:

                if not car.is_available:
                    print("Car is already rented")
                    return

                total_price = days * car.price_per_day

                booking = Booking(
                    car_id,
                    client_name,
                    days,
                    total_price
                )

                self.bookings.append(booking)

                car.rent()

                print(f"Car rented successfully. Total price: ${total_price}")
                return

        print("Car not found")