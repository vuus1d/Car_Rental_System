import json


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