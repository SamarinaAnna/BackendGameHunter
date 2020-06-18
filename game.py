

class Game:

    def __init__(self, id, creator_email, date, time, place, quantity, game_name, duration, description=''):
        self.id = id
        self.creator_email = creator_email
        self.date = date
        self.time = time
        self.place = place
        self.quantity = int(quantity)
        self.game_name = game_name
        self.duration = duration
        self.description = description

        self.players = [quantity]

    def set_id(self, id):
        self.id = id

    def set_creator_email(self, creator_email):
        self.creator_email = creator_email

    def set_date(self, date):
        self.date = date

    def set_time(self, time):
        self.time = time

    def set_place(self, place):
        self.place = place

    def set_quantity(self, quantity):
        self.quantity = int(quantity)

    def set_game_name(self, game_name):
        self.game_name = game_name

    def set_duration(self, duration):
        self.duration = duration

    def set_description(self, description):
        self.description = description

    def add_player(self, player):
        if len(self.players) < self.quantity:
            self.players += player

    def del_player(self, player):
        if player in self.players:
            self.players.remove(player)
