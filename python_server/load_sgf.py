import sys
sys.path.append("..")
from go_game import Go_game,Rotater
import numpy as np
from create_book import extract_val,convert_move_to_num

def load_sgf(sgf,zobrist):
    def extract_val(line):
        return line.split("[")[1].split("]")[0]
    game = Go_game(zobrist)
    for line in sgf.splitlines():
        if line.startswith(";B") or line.startswith("(;B") or line.startswith(";W") or line.startswith("(;W") or line.startswith("AB"):
            extract_val(line)
            move = convert_move_to_num(extract_val(line))
            game.make_move(move)
    return game

def sync_to_equal_move(old_game, new_game):
    old_game.revert_move(amount=100)
    new_game.revert_move(amount=100)
    moves = []
    while 1:
        if not (np.array_equal(old_game.position[0],new_game.position[0]) and np.array_equal(old_game.position[1],new_game.position[1])):
            if new_game.revert_move(amount=1):
                moves.pop()
            break
        worked_old = old_game.forward(1) 
        worked_new = new_game.forward(1)
        if worked_new:
            moves.append(worked_new[0])
        if not (worked_old and worked_new):
            if worked_new:
                new_game.revert_move(amount=1)
                moves.pop()
            break
    return new_game,moves