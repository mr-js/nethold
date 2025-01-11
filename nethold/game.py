import os
from board import Board

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

players_number = 0
players = []

while players_number < 2 or players_number > 8:
    try:
        players_number = int(input('Number of players [2 .. 8]: '))
    except ValueError:
        pass
        
for i in range(players_number):
    players.append(input('Player {} name: '.format(i + 1)))

board = Board(players)
board.players.showinfo()

while True:
    print('\n{}\n{}\n{}'.format('=' * 40, 'NEW HAND', '=' * 40))
    board.players.showstate()
    if board.hand():
        break
    input('\nPress Enter to continue to the next hand...')
    cls()

input('\nPress Enter to exit the game')