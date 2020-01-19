class Player:
    "Klasa gracza"
    def __init__(self):
        self.maxStamina = 0
        self.stamina = 0
        self.bottle = 1
        self.rope = 1
        self.trap = 1
        self.sonar = 1
        self.key = 0
        self.visited = []
        self.position = ''
