class Cell:
    "Klasa pojedynczej komórki labiryntu"
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # ściany: none(white), door(orange), climb(brown), notClimb(black)
        self.walls = {'top': 'climb', 'right': 'climb', 'bottom': 'climb', 'left': 'climb'}
        self.visited = False
        # zawartość: available(white), visited(gray), hidden(black),
        # playerOne(green, G), playerTwo(red, G), twoPlayers(yellow, G), item(I), key(K), end(Q)
        self.content = 'available'
        self.trap = False
