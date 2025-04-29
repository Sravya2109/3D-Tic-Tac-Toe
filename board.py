# board.py

import config

class Board:
    def __init__(self):
        self.grid = [[[None for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)]

    def make_move(self, layer, row, col, player):
        if self.grid[layer][row][col] is None:
            self.grid[layer][row][col] = player
            return True
        return False

    def available_moves(self):
        moves = []
        for l in range(config.GRID_SIZE):
            for r in range(config.GRID_SIZE):
                for c in range(config.GRID_SIZE):
                    if self.grid[l][r][c] is None:
                        moves.append((l, r, c))
        return moves

    def is_full(self):
        return all(self.grid[l][r][c] is not None for l in range(config.GRID_SIZE) for r in range(config.GRID_SIZE) for c in range(config.GRID_SIZE))

    def check_win(self, player):
        lines = []
        for l in range(4):
            for r in range(4):
                lines.append([self.grid[l][r][c] for c in range(4)])  # rows
                lines.append([self.grid[l][c][r] for c in range(4)])  # columns
            for c in range(4):
                lines.append([self.grid[c][r][l] for r in range(4)])  # pillars

        for l in range(4):
            lines.append([self.grid[l][i][i] for i in range(4)])
            lines.append([self.grid[l][i][3-i] for i in range(4)])

        for r in range(4):
            lines.append([self.grid[i][r][i] for i in range(4)])
            lines.append([self.grid[i][r][3-i] for i in range(4)])

        for c in range(4):
            lines.append([self.grid[i][i][c] for i in range(4)])
            lines.append([self.grid[i][3-i][c] for i in range(4)])

        lines.append([self.grid[i][i][i] for i in range(4)])
        lines.append([self.grid[i][i][3-i] for i in range(4)])
        lines.append([self.grid[i][3-i][i] for i in range(4)])
        lines.append([self.grid[3-i][i][i] for i in range(4)])

        for line in lines:
            if all(cell == player for cell in line):
                return True
        return False

    def clone(self):
        new_board = Board()
        for l in range(4):
            for r in range(4):
                for c in range(4):
                    new_board.grid[l][r][c] = self.grid[l][r][c]
        return new_board
