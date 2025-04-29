# ai.py

import math
import random

def evaluate(board, player, opponent):
    if board.check_win(player):
        return 100
    elif board.check_win(opponent):
        return -100
    return 0

def minimax(board, depth, alpha, beta, maximizing, player, opponent):
    score = evaluate(board, player, opponent)

    if abs(score) == 10 or depth == 0 or board.is_full():
        return score

    if maximizing:
        max_eval = -math.inf
        for move in board.available_moves():
            new_board = board.clone()
            new_board.make_move(*move, player)
            eval = minimax(new_board, depth-1, alpha, beta, False, player, opponent)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in board.available_moves():
            new_board = board.clone()
            new_board.make_move(*move, opponent)
            eval = minimax(new_board, depth-1, alpha, beta, True, player, opponent)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, player, opponent, depth):
    best_value = -math.inf
    best_move = None

    for move in board.available_moves():
        new_board = board.clone()
        new_board.make_move(*move, player)
        move_value = minimax(new_board, depth-1, -math.inf, math.inf, False, player, opponent)

        if move_value > best_value:
            best_value = move_value
            best_move = move

    if best_move is None:
        return random.choice(board.available_moves())
    return best_move
