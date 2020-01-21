from cell import *
import random


class Maze:
    "Klasa labiryntu"
    def __init__(self, size):
        self.size = size
        self.start = ''
        self.cells = self.generateMaze()


    def generateMaze(self):
        "Funkcja generująca labirynt"
        cells = [[Cell(x, y) for y in range(self.size)] for x in range(self.size)]
        edges = []

        "Ustawienie krawędzi labiryntu"
        for x in range(self.size):
            for y in range(self.size):
                if x == 0:
                    cells[x][y].walls['top'] = 'notClimb'
                    edges.append(cells[x][y])
                if y == 0:
                    cells[x][y].walls['left'] = 'notClimb'
                    edges.append(cells[x][y])
                if x == self.size - 1:
                    cells[x][y].walls['bottom'] = 'notClimb'
                    edges.append(cells[x][y])
                if y == self.size - 1:
                    cells[x][y].walls['right'] = 'notClimb'
                    edges.append(cells[x][y])

        "Wybranie losowego wyjścia z labiryntu"
        end = random.choice(edges)
        current = end
        current.visited = True
        current.content = 'end'
        stack = []
        stack.append(current)

        "Generowanie labiryntu"
        while len(stack) > 0:

            "Szukanie sąsiadów"
            neighbouringCells = self.checkNeighbours(current, cells)
            neighbours = []
            if neighbouringCells['top'] != -1 and not neighbouringCells['top'].visited:
                neighbours.append(neighbouringCells['top'])

            if neighbouringCells['right'] != -1 and not neighbouringCells['right'].visited:
                neighbours.append(neighbouringCells['right'])

            if neighbouringCells['bottom'] != -1 and not neighbouringCells['bottom'].visited:
                neighbours.append(neighbouringCells['bottom'])

            if neighbouringCells['left'] != -1 and not neighbouringCells['left'].visited:
                neighbours.append(neighbouringCells['left'])

            "Wybór losowego dostępnego sąsiada"
            if len(neighbours) > 0:
                next = random.choice(neighbours)
                stack.append(current)
                if next == neighbouringCells['top']:
                    current.walls['top'] = 'none'
                    next.walls['bottom'] = 'none'
                if next == neighbouringCells['right']:
                    current.walls['right'] = 'none'
                    next.walls['left'] = 'none'
                if next == neighbouringCells['bottom']:
                    current.walls['bottom'] = 'none'
                    next.walls['top'] = 'none'
                if next == neighbouringCells['left']:
                    current.walls['left'] = 'none'
                    next.walls['right'] = 'none'
                current = next
                current.visited = True
            elif len(stack) > 0:
                current = stack.pop()

        "Dodatkowe usuwanie losowych ścian"
        self.changeWalls(cells, self.size ** 2 / 10, 'none')

        "Dodanie losowych drzwi"
        self.changeWalls(cells, self.size ** 2 / 50, 'door')

        "Dodanie losowych ścian niemożliwych do wspinaczki"
        self.changeWalls(cells, self.size ** 2 / 2.5, 'notClimb')

        "Ustalenie punktu startowego graczy"
        spawn = []
        for x in range(int(self.size / 2 - self.size / 10), int(self.size / 2 + self.size / 10)):
            for y in range(int(self.size / 2 - self.size / 10), int(self.size / 2 + self.size / 10)):
                spawn.append(cells[x][y])
        self.start = random.choice(spawn)
        self.start.content = 'player'

        "Losowe ustalenie lokacji kluczy"
        self.generateLocations(cells, 'available', 'key', self.size ** 2 / 50)

        "Losowe ustalenie lokacji przedmiotów"
        self.generateLocations(cells, 'available', 'item', self.size ** 2 / 12.5)

        return cells


    def checkNeighbours(self, cell, cells):
        "Funkcja zwracająca sąsiadujące pola podanej komórki"
        neighbours = {}
        if cell.x > 0:
            neighbours['top'] = cells[cell.x - 1][cell.y]
        else:
            neighbours['top'] = -1
        if cell.y < self.size - 1:
            neighbours['right'] = cells[cell.x][cell.y + 1]
        else:
            neighbours['right'] = -1
        if cell.x < self.size - 1:
            neighbours['bottom'] = cells[cell.x + 1][cell.y]
        else:
            neighbours['bottom'] = -1
        if cell.y > 0:
            neighbours['left'] = cells[cell.x][cell.y - 1]
        else:
            neighbours['left'] = -1
        return neighbours


    def changeWalls(self, cells, limit, wallContent):
        "Funkcja zmieniająca ściany w labiryncie"
        i = 0
        while i < limit:
            sublist = random.choice(cells)
            cell = random.choice(sublist)
            wall = random.choice(list(cell.walls.keys()))
            if cell.walls[wall] == 'climb' and not (wall == 'top' and cell.x == 0) and not (wall == 'right' and cell.y == self.size - 1) and not (
                    wall == 'bottom' and cell.x == self.size - 1) and not (wall == 'left' and cell.y == 0):
                if wallContent != 'door' or (wallContent == 'door'
                        and ((wall == 'top' and (cell.y == 0 or cells[cell.x][cell.y - 1].walls['top'] != 'none' or cells[cell.x][cell.y - 1].walls['right'] != 'none')
                        and (cell.y == self.size - 1 or cells[cell.x][cell.y + 1].walls['top'] != 'none' or cells[cell.x][cell.y + 1].walls['left'] != 'none'))
                        or (wall == 'right' and (cell.x == 0 or cells[cell.x - 1][cell.y].walls['right'] != 'none' or cells[cell.x - 1][cell.y].walls['bottom'] != 'none')
                        and (cell.x == self.size - 1 or cells[cell.x + 1][cell.y].walls['right'] != 'none' or cells[cell.x + 1][cell.y].walls['top'] != 'none'))
                        or (wall == 'bottom' and (cell.y == 0 or cells[cell.x][cell.y - 1].walls['bottom'] != 'none' or cells[cell.x][cell.y - 1].walls['right'] != 'none')
                        and (cell.y == self.size - 1 or cells[cell.x][cell.y + 1].walls['bottom'] != 'none' or cells[cell.x][cell.y + 1].walls['left'] != 'none'))
                        or (wall == 'left' and (cell.x == 0 or cells[cell.x - 1][cell.y].walls['left'] != 'none' or cells[cell.x - 1][cell.y].walls['bottom'] != 'none')
                        and (cell.x == self.size - 1 or cells[cell.x + 1][cell.y].walls['left'] != 'none' or cells[cell.x + 1][cell.y].walls['top'] != 'none')))):
                    cell.walls[wall] = wallContent
                    if wall == 'top':
                        cells[cell.x - 1][cell.y].walls['bottom'] = wallContent
                    if wall == 'right':
                        cells[cell.x][cell.y + 1].walls['left'] = wallContent
                    if wall == 'bottom':
                        cells[cell.x + 1][cell.y].walls['top'] = wallContent
                    if wall == 'left':
                        cells[cell.x][cell.y - 1].walls['right'] = wallContent
                    i += 1


    def generateLocations(self, cells, content, newContent, limit):
        "Funkcja generująca losowe lokacje dla przedmiotów"
        i = 0
        while i < limit:
            sublist = random.choice(cells)
            element = random.choice(sublist)
            if element.content == content:
                if element.x == 0 or cells[element.x - 1][element.y].content == content:
                    if element.x == self.size - 1 or cells[element.x + 1][element.y].content == content:
                        if element.y == 0 or cells[element.x][element.y - 1].content == content:
                            if element.y == self.size - 1 or cells[element.x][element.y + 1].content == content:
                                element.content = newContent
                                i += 1
