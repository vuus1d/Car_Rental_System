from models.car import Car
from models.client import Client
from decorators import log_action
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

    @log_action
    def show_cars(self):

        print("\n========== CAR LIST ==========")

        if not self.cars:
            print("No cars available")
            return

        for car in self.cars:

            status = "Available"

            if not car.is_available:
                status = "Rented"

            print(
                f"ID: {car.car_id} | "
                f"{car.brand} {car.model} | "
                f"Year: {car.year} | "
                f"Price per day: ${car.price_per_day} | "
                f"Status: {status}"
            )

        print("================================")

    @log_action
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

    @log_action
    def return_car(self, car_id):
        for booking in self.bookings:

            if booking.car_id == car_id and booking.is_active:

                booking.complete()

                for car in self.cars:
                    if car.car_id == car_id:
                        car.return_car()

                        print("Car returned successfully")
                        return

        print("Active booking not found")
    def show_statistics(self):

        total_cars = len(self.cars)

        available_cars = 0
        rented_cars = 0

        for car in self.cars:

            if car.is_available:
                available_cars += 1
            else:
                rented_cars += 1

        print("\n=== Statistics ===")
        print(f"Total cars: {total_cars}")
        print(f"Available cars: {available_cars}")
        print(f"Rented cars: {rented_cars}")
        print("==============================")