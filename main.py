from managers.file_manager import FileManager


def main():

    cars = FileManager.load_cars()

    while True:

        print("\n=== Car Rental System ===")
        print("1. Show cars")
        print("2. Exit")

        choice = input("Choose an option: ")

        if choice == "1":

            for car in cars:
                print(car)

        elif choice == "2":

            print("Goodbye!")
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()