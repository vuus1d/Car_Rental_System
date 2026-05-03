from models.car import Car
from models.client import Client
from models.booking import Booking

def main():
    car1 = Car(1, "Toyota", "Camry", 2020, 50)
    client1 = Client("Nurasyl")

    booking1 = Booking(car1.car_id, client1.name, 3, 150)

    print(car1)
    print(client1)
    print(booking1)

    booking1.complete()
    print(booking1)

if __name__ == "__main__":
    main()