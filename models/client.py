from models.person import Person


class Client(Person):

    def __init__(self, name):

        super().__init__(name)

        self.rental_history = []

    def add_booking(self, booking):

        self.rental_history.append(booking)