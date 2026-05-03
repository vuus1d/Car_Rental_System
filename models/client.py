class Client:
    def __init__(self, name):
        self.name = name
        self.rental_history = []

    def add_booking(self, booking):
        self.rental_history.append(booking)

    def __str__(self):
        return f"Client: {self.name}"