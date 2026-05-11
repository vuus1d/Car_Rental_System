import json
from models.car import Car


class FileManager:

    @staticmethod
    def save_cars(cars):

        data = []

        for car in cars:
            data.append({
                "car_id": car.car_id,
                "brand": car.brand,
                "model": car.model,
                "year": car.year,
                "price_per_day": car.price_per_day,
                "is_available": car.is_available
            })

        with open("data/cars.json", "w") as file:
            json.dump(data, file, indent=4)

        print("Cars saved successfully")

    @staticmethod
    def load_cars():

        cars = []

        with open("data/cars.json", "r") as file:

            data = json.load(file)

            for item in data:

                car = Car(
                    item["car_id"],
                    item["brand"],
                    item["model"],
                    item["year"],
                    item["price_per_day"]
                )

                car.is_available = item["is_available"]

                cars.append(car)

        return cars