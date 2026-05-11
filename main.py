from managers.file_manager import FileManager


def main():

    cars = FileManager.load_cars()

    for car in cars:
        print(car)


if __name__ == "__main__":
    main()