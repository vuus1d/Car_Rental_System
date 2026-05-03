from models.car import Car
from models.client import Client

def main():
    car1 = Car(1, "Toyota", "Camry", 2020, 50)
    client1 = Client("Nurasyl")

    print(car1)
    print(client1)

if __name__ == "__main__":
    main()