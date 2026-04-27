from models.car import Car

def main():
    car1 = Car(1, "Toyota", "Camry", 2020, 50)

    print(car1)
    car1.rent()
    print(car1)
    car1.return_car()
    print(car1)

if __name__ == "__main__":
    main()