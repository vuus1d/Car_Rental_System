from models.car import Car
from models.client import Client
from managers.rental_manager import RentalManager


def main():
    manager = RentalManager()

    car1 = Car(1, "Toyota", "Camry", 2020, 50)
    car2 = Car(2, "BMW", "X5", 2022, 120)

    client1 = Client("Nurasyl")

    manager.add_car(car1)
    manager.add_car(car2)

    manager.add_client(client1)

    manager.show_cars()


if __name__ == "__main__":
    main()