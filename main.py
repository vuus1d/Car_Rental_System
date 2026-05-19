from managers.file_manager import FileManager
from managers.rental_manager import RentalManager


def main():

    manager = RentalManager()

    manager.cars = FileManager.load_cars()

    while True:

        print("\n=== Car Rental System ===")
        print("1. Show cars")
        print("2. Rent car")
        print("3. Return car")
        print("4. Show statistics")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":

            manager.show_cars()

        elif choice == "2":

            try:

                car_id = int(input("Enter car ID: "))
                client_name = input("Enter your name: ")
                days = int(input("Enter number of days: "))

                manager.rent_car(car_id, client_name, days)

                FileManager.save_cars(manager.cars)

            except ValueError:

                print("Invalid input. Please enter numbers correctly.")

        elif choice == "3":

            try:

                car_id = int(input("Enter car ID to return: "))

                manager.return_car(car_id)

                FileManager.save_cars(manager.cars)

            except ValueError:

                print("Invalid car ID.")

        elif choice == "4":

            manager.show_statistics()

        elif choice == "5":

            print("Goodbye!")
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()