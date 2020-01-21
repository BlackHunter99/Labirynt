from flask import Flask, render_template, request, redirect, url_for, session
from game import *

app = Flask(__name__)
app.secret_key = 'extra secret key'

games = {}
gameNumber = 1


@app.route('/')
def mode():
    return render_template('mode.html')


@app.route('/settings')
def settings():
    mode = request.args.get('mode')
    return render_template('settings.html', mode=mode)


@app.route('/multiplayer')
def multiplayer():
    global games
    return render_template('multiplayer.html', games=games)


@app.route('/start', methods=['GET', 'POST'])
def start():
    global games, gameNumber
    mode = request.args.get('mode')
    size = request.form['size']
    difficulty = request.form['difficulty']
    aiDifficulty = None
    if mode == 'ai':
        aiDifficulty = request.form['aiDifficulty']
    game = Game(int(size), mode, difficulty, aiDifficulty)
    games[gameNumber] = game
    session['game'] = gameNumber
    gameNumber += 1
    if mode == 'multiplayer':
        session['player'] = 0
        game.full = False
        return redirect(url_for('wait', mode=mode, size=size, difficulty=difficulty))
    return render_template('start.html', mode=mode, size=size, difficulty=difficulty, game=game)


@app.route('/wait')
def wait():
    global games
    mode = request.args.get('mode')
    size = request.args.get('size')
    difficulty = request.args.get('difficulty')
    return render_template('wait.html', mode=mode, size=size, difficulty=difficulty, game=games[session['game']])


@app.route('/join')
def join():
    global games
    gameNumber = request.args.get('gameNumber')
    if games[int(gameNumber)].full == False:
        session['game'] = int(gameNumber)
        session['player'] = 1
        games[int(gameNumber)].full = True
    if games[int(gameNumber)] == games[int(session['game'])] and games[int(gameNumber)].begin == True:
        return redirect(url_for('game'))
    return render_template('join.html', game=games[session['game']], mode=games[session['game']].mode, size=games[session['game']].maze.size, difficulty=games[session['game']].difficulty)


@app.route('/game')
def game(x=None, y=None, item=None, action = None, endTurn=None):
    global games

    if x and y:
        pass
    else:
        x = request.args.get('x')
        y = request.args.get('y')

    if item:
        pass
    else:
        item = request.args.get('item')

    if action:
        pass
    else:
        action = request.args.get('action')

    if endTurn:
        pass
    else:
        endTurn = request.args.get('endTurn')

    currentGame = games[session['game']]
    currentGame.begin = True

    if currentGame.winner != '':
        return render_template('win.html', winner=currentGame.winner + 1)
    if currentGame.mode == 'multiplayer' and currentGame.playerNumber != session['player']:
        return render_template('game.html', wait=True)
    else:
        currentGame.player = currentGame.players[currentGame.playerNumber]
        area = []
        doorArea = []
        ropeArea = []

        "Sprawdzenie czy przesłane zostały współrzędne pola"
        if x and y:
            x = int(x)
            y = int(y)

            "Sprawdzenie czy pole docelowe jest w granicach labiryntu"
            if x >= 0 and y >= 0 and x <= currentGame.maze.size - 1 and y <= currentGame.maze.size - 1:
                next = currentGame.maze.cells[x][y]

                "Zapisanie sąsiadów obecnej pozycji gracza"
                neighbours = currentGame.maze.checkNeighbours(currentGame.player.position, currentGame.maze.cells)

                "Sprawdzenie czy pole docelowe sąsiaduje z obecną pozycją"
                if (neighbours['top'] != -1 and next == neighbours['top']) or (neighbours['right'] != -1 and next == neighbours['right']) or (
                        neighbours['bottom'] != -1 and next == neighbours['bottom']) or (neighbours['left'] != -1 and next == neighbours['left']):

                    "Sprawdzenie użycia przedmiotów i czy docelowe pole jest dostępne do danej akcji"
                    if currentGame.trap == True and currentGame.neighboursWallsContent(next, neighbours, 'none') == True:
                        if currentGame.player.stamina >= 20:
                            currentGame.firstMove = False

                            "Zmiana zawartości docelowego pola na pole z pułapką"
                            next.trap = True

                            currentGame.player.stamina -= 20
                            currentGame.player.trap -= 1
                            currentGame.clearVar()
                            currentGame.info = 'Zastawiłeś pułapkę'
                        else:
                            currentGame.clearVar()
                            currentGame.info = 'Za mało wytrzymałości'

                    elif currentGame.key == True and currentGame.neighboursWallsContent(next, neighbours, 'door') == True:
                        if currentGame.player.stamina > 0:

                            "Sprawdzenie zawartości następnego pola"
                            currentGame.collectible = currentGame.checkNextCell(next)
                            if currentGame.collectible == 'end':
                                currentGame.winner = currentGame.playerNumber
                                return render_template('win.html', winner=currentGame.winner + 1)

                            "Zmiana zawartości opuszczanego pola i docelowego pola"
                            currentGame.changeCellsContent(next)

                            "Usuwanie drzwi"
                            if next == neighbours['top']:
                                currentGame.player.position.walls['top'] = 'none'
                                next.walls['bottom'] = 'none'
                            elif next == neighbours['right']:
                                currentGame.player.position.walls['right'] = 'none'
                                next.walls['left'] = 'none'
                            elif next == neighbours['bottom']:
                                currentGame.player.position.walls['bottom'] = 'none'
                                next.walls['top'] = 'none'
                            elif next == neighbours['left']:
                                currentGame.player.position.walls['left'] = 'none'
                                next.walls['right'] = 'none'

                            currentGame.player.position = next
                            currentGame.player.stamina -= 10
                            currentGame.player.key -= 1

                            "Sprawdzenie obecności pułapki na docelowym polu"
                            currentGame.info = currentGame.checkTrap('Otworzyłeś drzwi')
                        else:
                            currentGame.clearVar()
                            currentGame.info = 'Za mało wytrzymałości'

                    elif currentGame.rope == True and currentGame.neighboursWallsContent(next, neighbours, 'climb') == True:
                        if currentGame.player.stamina >= 30:

                            "Sprawdzenie zawartości następnego pola"
                            currentGame.collectible = currentGame.checkNextCell(next)
                            if currentGame.collectible == 'end':
                                currentGame.winner = currentGame.playerNumber
                                return render_template('win.html', winner=currentGame.winner + 1)

                            "Zmiana zawartości opuszczanego pola i docelowego pola"
                            currentGame.changeCellsContent(next)

                            currentGame.player.position = next
                            currentGame.player.stamina -= 30
                            currentGame.player.rope -= 1

                            "Sprawdzenie obecności pułapki na docelowym polu"
                            currentGame.info = currentGame.checkTrap('Wspiąłeś się po ścianie')
                        else:
                            currentGame.clearVar()
                            currentGame.info = 'Za mało wytrzymałości'

                    elif currentGame.neighboursWallsContent(next, neighbours, 'none') == True:
                        if currentGame.player.stamina > 0:

                            "Sprawdzenie zawartości następnego pola"
                            currentGame.collectible = currentGame.checkNextCell(next)
                            if currentGame.collectible == 'end':
                                currentGame.winner = currentGame.playerNumber
                                return render_template('win.html', winner=currentGame.winner + 1)

                            "Zmiana zawartości opuszczanego pola i docelowego pola"
                            currentGame.changeCellsContent(next)

                            currentGame.player.position = next
                            currentGame.player.stamina -= 10

                            "Sprawdzenie obecności pułapki na docelowym polu"
                            currentGame.info = currentGame.checkTrap('Wykonałeś ruch')
                        else:
                            currentGame.clearVar()
                            currentGame.info = 'Za mało wytrzymałości'
                    else:
                        currentGame.clearVar()
                        currentGame.info = 'Zły ruch'
                else:
                    currentGame.clearVar()
                    currentGame.info = 'Zły ruch'
            else:
                currentGame.clearVar()
                currentGame.info = 'Zły ruch'

        "Użycie butelki z wodą"
        if item and item == 'bottle':
            if currentGame.player.bottle > 0:
                currentGame.firstMove = False
                currentGame.player.stamina = currentGame.player.maxStamina
                currentGame.player.bottle -= 1
                currentGame.clearVar()
                currentGame.info = 'Napiłeś się z butelki'
            else:
                currentGame.clearVar()
                currentGame.info = 'Nie masz już butelek'

        "Użycie klucza"
        if item and item == 'key':
            if currentGame.player.key > 0:
                currentGame.key = True
                currentGame.rope = False
                currentGame.trap = False
                currentGame.info = 'Wyciągnąłeś klucz'
            else:
                currentGame.clearVar()
                currentGame.info = 'Nie masz już kluczy'

        "Użycie liny"
        if item and item == 'rope':
            if currentGame.player.rope > 0:
                currentGame.rope = True
                currentGame.key = False
                currentGame.trap = False
                currentGame.info = 'Wyciągnąłeś linę'
            else:
                currentGame.clearVar()
                currentGame.info = 'Nie masz już lin'

        "Użycie pułapki"
        if item and item == 'trap':
            if currentGame.player.trap > 0:
                currentGame.trap = True
                currentGame.key = False
                currentGame.rope = False
                currentGame.info = 'Wyciągnąłeś pułapkę'
            else:
                currentGame.clearVar()
                currentGame.info = 'Nie masz już pułapek'

        "Akcja medytacji"
        if action and action == 'meditate':
            if currentGame.firstMove == True:
                currentGame.player.stamina = currentGame.player.maxStamina
                currentGame.playerNumber = (currentGame.playerNumber + 1) % 2
                currentGame.player = currentGame.players[currentGame.playerNumber]
                currentGame.firstMove = True
                currentGame.collectible = ''
                currentGame.clearVar()
                currentGame.info = 'Początek tury'
                if currentGame.mode == 'multiplayer':
                    return redirect(url_for('game', wait=True))
                else:
                    return redirect(url_for('game'))
            else:
                currentGame.clearVar()
                currentGame.info = 'Nie możesz medytować'

        "Zakończenie tury"
        if endTurn == '1':
            if currentGame.player.stamina < currentGame.player.maxStamina - 4 * currentGame.maze.size:
                currentGame.player.stamina = currentGame.player.stamina + 4 * currentGame.maze.size
            else:
                currentGame.player.stamina = currentGame.player.maxStamina
            currentGame.playerNumber = (currentGame.playerNumber + 1) % 2
            currentGame.player = currentGame.players[currentGame.playerNumber]
            currentGame.firstMove = True
            currentGame.collectible = ''
            currentGame.clearVar()
            currentGame.info = 'Początek tury'
            if currentGame.mode == 'multiplayer':
                return redirect(url_for('game', wait=True))
            else:
                return redirect(url_for('game'))

        "Sztuczna inteligencja"
        if currentGame.mode == 'ai' and currentGame.player != currentGame.players[0]:

            if currentGame.player.stamina == 4 * currentGame.maze.size and currentGame.player.bottle == 0 and currentGame.firstMove == True:
                return game(action='meditate')
            elif currentGame.player.stamina > 0:
                if currentGame.aiDifficulty == 'easy':
                    neighbours = []
                    if currentGame.player.position.x > 0 and currentGame.player.position.walls['top'] == 'none':
                        top = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                        neighbours.append(top)
                    if currentGame.player.position.y < currentGame.maze.size - 1 and currentGame.player.position.walls['right'] == 'none':
                        right = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                        neighbours.append(right)
                    if currentGame.player.position.x < currentGame.maze.size - 1 and currentGame.player.position.walls['bottom'] == 'none':
                        bottom = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                        neighbours.append(bottom)
                    if currentGame.player.position.y > 0 and currentGame.player.position.walls['left'] == 'none':
                        left = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                        neighbours.append(left)
                    move = random.choice(neighbours)
                elif currentGame.aiDifficulty == 'hard':
                    if currentGame.aiCounter == 0:
                        if currentGame.aiDirection == 'top' and currentGame.player.position.walls['top'] == 'none':
                            move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                        elif currentGame.aiDirection == 'right' and currentGame.player.position.walls['right'] == 'none':
                            move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                        elif currentGame.aiDirection == 'bottom' and currentGame.player.position.walls['bottom'] == 'none':
                            move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                        elif currentGame.aiDirection == 'left' and currentGame.player.position.walls['left'] == 'none':
                            move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                        else:
                            if currentGame.aiDirection == 'top':
                                if currentGame.player.position.walls['left'] == 'none':
                                    currentGame.aiDirection = 'left'
                                    currentGame.aiCounter -= 1
                                    move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                                elif currentGame.player.position.walls['bottom'] == 'none':
                                    currentGame.aiDirection = 'bottom'
                                    currentGame.aiCounter -= 2
                                    move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                                elif currentGame.player.position.walls['right'] == 'none':
                                    currentGame.aiDirection = 'right'
                                    currentGame.aiCounter -= 3
                                    move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                            elif currentGame.aiDirection == 'right':
                                if currentGame.player.position.walls['top'] == 'none':
                                    currentGame.aiDirection = 'top'
                                    currentGame.aiCounter -= 1
                                    move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                                elif currentGame.player.position.walls['left'] == 'none':
                                    currentGame.aiDirection = 'left'
                                    currentGame.aiCounter -= 2
                                    move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                                elif currentGame.player.position.walls['bottom'] == 'none':
                                    currentGame.aiDirection = 'bottom'
                                    currentGame.aiCounter -= 3
                                    move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                            elif currentGame.aiDirection == 'bottom':
                                if currentGame.player.position.walls['right'] == 'none':
                                    currentGame.aiDirection = 'right'
                                    currentGame.aiCounter -= 1
                                    move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                                elif currentGame.player.position.walls['top'] == 'none':
                                    currentGame.aiDirection = 'top'
                                    currentGame.aiCounter -= 2
                                    move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                                elif currentGame.player.position.walls['left'] == 'none':
                                    currentGame.aiDirection = 'left'
                                    currentGame.aiCounter -= 3
                                    move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                            elif currentGame.aiDirection == 'left':
                                if currentGame.player.position.walls['bottom'] == 'none':
                                    currentGame.aiDirection = 'bottom'
                                    currentGame.aiCounter -= 1
                                    move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                                elif currentGame.player.position.walls['right'] == 'none':
                                    currentGame.aiDirection = 'right'
                                    currentGame.aiCounter -= 2
                                    move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                                elif currentGame.player.position.walls['top'] == 'none':
                                    currentGame.aiDirection = 'top'
                                    currentGame.aiCounter -= 3
                                    move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                    else:
                        if currentGame.aiDirection == 'top':
                            if currentGame.player.position.walls['right'] == 'none':
                                currentGame.aiDirection = 'right'
                                currentGame.aiCounter += 1
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                            elif currentGame.player.position.walls['top'] == 'none':
                                currentGame.aiDirection = 'top'
                                move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                            elif currentGame.player.position.walls['left'] == 'none':
                                currentGame.aiDirection = 'left'
                                currentGame.aiCounter -= 1
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                            elif currentGame.player.position.walls['bottom'] == 'none':
                                currentGame.aiDirection = 'bottom'
                                currentGame.aiCounter -= 2
                                move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                        elif currentGame.aiDirection == 'right':
                            if currentGame.player.position.walls['bottom'] == 'none':
                                currentGame.aiDirection = 'bottom'
                                currentGame.aiCounter += 1
                                move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                            elif currentGame.player.position.walls['right'] == 'none':
                                currentGame.aiDirection = 'right'
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                            elif currentGame.player.position.walls['top'] == 'none':
                                currentGame.aiDirection = 'top'
                                currentGame.aiCounter -= 1
                                move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                            elif currentGame.player.position.walls['left'] == 'none':
                                currentGame.aiDirection = 'left'
                                currentGame.aiCounter -= 2
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                        elif currentGame.aiDirection == 'bottom':
                            if currentGame.player.position.walls['left'] == 'none':
                                currentGame.aiDirection = 'left'
                                currentGame.aiCounter += 1
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                            elif currentGame.player.position.walls['bottom'] == 'none':
                                currentGame.aiDirection = 'bottom'
                                move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                            elif currentGame.player.position.walls['right'] == 'none':
                                currentGame.aiDirection = 'right'
                                currentGame.aiCounter -= 1
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                            elif currentGame.player.position.walls['top'] == 'none':
                                currentGame.aiDirection = 'top'
                                currentGame.aiCounter -= 2
                                move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                        elif currentGame.aiDirection == 'left':
                            if currentGame.player.position.walls['top'] == 'none':
                                currentGame.aiDirection = 'top'
                                currentGame.aiCounter += 1
                                move = currentGame.maze.cells[currentGame.player.position.x - 1][currentGame.player.position.y]
                            elif currentGame.player.position.walls['left'] == 'none':
                                currentGame.aiDirection = 'left'
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y - 1]
                            elif currentGame.player.position.walls['bottom'] == 'none':
                                currentGame.aiDirection = 'bottom'
                                currentGame.aiCounter -= 1
                                move = currentGame.maze.cells[currentGame.player.position.x + 1][currentGame.player.position.y]
                            elif currentGame.player.position.walls['right'] == 'none':
                                currentGame.aiDirection = 'right'
                                currentGame.aiCounter -= 2
                                move = currentGame.maze.cells[currentGame.player.position.x][currentGame.player.position.y + 1]
                print(move.x, move.y)
                return game(x=str(move.x), y=str(move.y))
            elif currentGame.player.bottle > 0:
                return game(item='bottle')
            else:
                return game(endTurn='1')

        "Ustalenie otoczenia gracza"
        area.append(currentGame.player.position)
        neighbours = currentGame.maze.checkNeighbours(currentGame.player.position, currentGame.maze.cells)
        currentGame.setArea(neighbours['top'], 'bottom', area, doorArea, ropeArea)
        currentGame.setArea(neighbours['right'], 'left', area, doorArea, ropeArea)
        currentGame.setArea(neighbours['bottom'], 'top', area, doorArea, ropeArea)
        currentGame.setArea(neighbours['left'], 'right', area, doorArea, ropeArea)

        "Użycie sonaru"
        if item and item == 'sonar':
            if currentGame.player.sonar > 0:
                if currentGame.player.stamina >= 30:
                    for x in range(currentGame.player.position.x - int(currentGame.maze.size / 5), currentGame.player.position.x + int(currentGame.maze.size / 5 + 1)):
                        for y in range(currentGame.player.position.y - int(currentGame.maze.size / 5), currentGame.player.position.y + int(currentGame.maze.size / 5 + 1)):
                            if x >= 0 and y >= 0 and x < currentGame.maze.size and y < currentGame.maze.size:
                                area.append(currentGame.maze.cells[x][y])
                    currentGame.firstMove = False
                    currentGame.player.stamina -= 30
                    currentGame.player.sonar -= 1
                    currentGame.clearVar()
                    currentGame.info = 'Użyłeś sonaru'
                else:
                    currentGame.clearVar()
                    currentGame.info = 'Za mało wytrzymałości'
            else:
                currentGame.clearVar()
                currentGame.info = 'Nie masz już sonarów'

        if currentGame.difficulty != 'hard':
            currentGame.visited = currentGame.player.visited

        return render_template('game.html', game=currentGame, playerNumber=currentGame.playerNumber+1, area=area, doorArea=doorArea, ropeArea=ropeArea, visited=currentGame.visited, wait=False)


if __name__ == '__main__':
    app.run(debug = True)
