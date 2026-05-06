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