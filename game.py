from maze import *
from player import *

class Game:
    "Klasa gry"
    def __init__(self, size, mode, difficulty, aiDifficulty = None):
        self.mode = mode
        self.difficulty = difficulty
        self.aiDifficulty = aiDifficulty
        self.maze = Maze(size)
        self.players = [Player(), Player()]
        for player in self.players:
            player.position = self.maze.start
            player.maxStamina = int(size) * 10
            player.stamina = int(size) * 10
            player.visited.append(self.maze.start)
        self.key = False
        self.rope = False
        self.trap = False
        self.firstMove = True
        self.items = self.initItems(size)
        self.visited = []
        self.playerNumber = 0
        self.player = self.players[0]
        self.info = 'Początek gry'
        self.collectible = ''
        self.winner = ''
        self.full = True
        self.begin = False
        self.aiCounter = 0
        self.aiDirection = random.choice(['top', 'right', 'bottom', 'left'])


    def initItems(self, size):
        "Funkcja tworząca listę przedmiotów"
        items = []
        for i in range(int(int(size) ** 2 / 50)):
            items.append('bottle')
        for i in range(int(int(size) ** 2 / 50)):
            items.append('rope')
        for i in range(int(int(size) ** 2 / 50)):
            items.append('trap')
        for i in range(int(int(size) ** 2 / 50)):
            items.append('sonar')
        return items

    def clearVar(self):
        "Funkcja czyszcząca zmienne globalne przedmiotów"
        self.key = False
        self.rope = False
        self.trap = False

    def neighboursWallsContent(self, next, neighbours, content):
        "Funkcja sprawdzająca zawartość ścian sąsiednich komórek"
        if (next == neighbours['top'] and self.player.position.walls['top'] == content) or (
                next == neighbours['right'] and self.player.position.walls['right'] == content) or (
                next == neighbours['bottom'] and self.player.position.walls['bottom'] == content) or (
                next == neighbours['left'] and self.player.position.walls['left'] == content):
            return True
        else:
            return False

    def checkNextCell(self, next):
        "Funkcja sprawdzająca następną komórkę pod kątem zawartości"
        self.firstMove = False
        if next.content == 'end':
            self.collectible = 'end'
            return self.collectible
        elif next.content == 'key':
            self.player.key += 1
            self.collectible = 'Znalazłeś klucz'
            return self.collectible
        elif next.content == 'item':
            item = random.choice(self.items)
            if item == 'bottle':
                self.player.bottle += 1
                self.items.remove(item)
                self.collectible = 'Znalazłeś butelkę'
                return self.collectible
            elif item == 'rope':
                self.player.rope += 1
                self.items.remove(item)
                self.collectible = 'Znalazłeś linę'
                return self.collectible
            elif item == 'trap':
                self.player.trap += 1
                self.items.remove(item)
                self.collectible = 'Znalazłeś pułapkę'
                return self.collectible
            elif item == 'sonar':
                self.player.sonar += 1
                self.items.remove(item)
                self.collectible = 'Znalazłeś sonar'
                return self.collectible
        else:
            self.collectible = ''
            return self.collectible

    def changeCellsContent(self, next):
        "Funkcja zmieniająca zawartości opuszczanego pola i docelowego pola"
        if self.player.position.content == 'twoPlayers':
            if self.player == self.players[0]:
                self.player.position.content = 'playerTwo'
            else:
                self.player.position.content = 'playerOne'
        else:
            self.player.position.content = 'available'

        if next.content == 'playerOne' or next.content == 'playerTwo':
            next.content = 'twoPlayers'
        elif self.player == self.players[0]:
            next.content = 'playerOne'
        else:
            next.content = 'playerTwo'

        self.player.visited.append(self.player.position)
        self.clearVar()

    def checkTrap(self, noTrap):
        "Funkcja sprawdzająca obecność pułapki na docelowym polu"
        if self.player.position.trap == True:
            self.player.stamina = 0
            self.player.position.trap = False
            self.info = 'Trafiłeś na pułapkę'
            return self.info
        else:
            self.info = noTrap
            return self.info

    def setArea(self, cell, wall, area, doorArea, ropeArea):
        "Funkcja definiująca widoczną okolicę gracza"
        if cell != -1:
            if cell.walls[wall] == 'none':
                area.append(cell)
            if self.key == True and cell.walls[wall] == 'door':
                doorArea.append(cell)
            if self.rope == True and cell.walls[wall] == 'climb':
                ropeArea.append(cell)
