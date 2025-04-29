import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math
import random

GRID_SIZE = 4
CUBE_SPACING = 2
difficulty_depth = 2
winner = None
board = [[[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

vertices = (
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
)
edges = (
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,7),(7,6),(6,4),
    (0,4),(1,5),(2,7),(3,6)
)

def draw_grid():
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_LINES)
    for l in range(GRID_SIZE):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x = (c - 2) * CUBE_SPACING
                y = (r - 2) * CUBE_SPACING
                z = (l - 2) * CUBE_SPACING
                for edge in edges:
                    for vertex in edge:
                        vx = vertices[vertex][0] * 0.5 + x
                        vy = vertices[vertex][1] * 0.5 + y
                        vz = vertices[vertex][2] * 0.5 + z
                        glVertex3f(vx, vy, vz)
    glEnd()

def draw_spheres():
    for l in range(GRID_SIZE):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                token = board[l][r][c]
                if token:
                    x = (c - 2) * CUBE_SPACING
                    y = (r - 2) * CUBE_SPACING
                    z = (l - 2) * CUBE_SPACING
                    glPushMatrix()
                    glTranslatef(x, y, z)
                    if token == 'X':
                        glColor3f(0.2, 0.4, 1.0)
                    else:
                        glColor3f(1.0, 0.5, 0.0)
                    gluSphere(gluNewQuadric(), 0.4, 16, 16)
                    glPopMatrix()

def draw_winner_message(text):
    font = pygame.font.SysFont('Arial', 48, True)
    surface = font.render(text, True, (255, 0, 0))
    text_data = pygame.image.tostring(surface, "RGBA", True)

    # Switch to 2D rendering
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw at top center
    glRasterPos2f(400, 750)
    glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    # Restore 3D context
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def check_win(b, p):
    lines = []
    for l in range(4):
        for i in range(4):
            lines.append([b[l][i][j] for j in range(4)])
            lines.append([b[l][j][i] for j in range(4)])
    for i in range(4):
        for j in range(4):
            lines.append([b[k][i][j] for k in range(4)])
    for l in range(4):
        lines.append([b[l][i][i] for i in range(4)])
        lines.append([b[l][i][3-i] for i in range(4)])
    for i in range(4):
        lines.append([b[i][i][i] for i in range(4)])
        lines.append([b[i][i][3-i] for i in range(4)])
        lines.append([b[i][3-i][i] for i in range(4)])
        lines.append([b[3-i][i][i] for i in range(4)])
    return any(all(cell == p for cell in line) for line in lines)

def minimax(b, d, maximizing, alpha, beta):
    if check_win(b, 'O'): return 10
    if check_win(b, 'X'): return -10
    moves = [(l, r, c) for l in range(4) for r in range(4) for c in range(4) if b[l][r][c] is None]
    if not moves or d == 0: return 0
    if maximizing:
        max_eval = -float('inf')
        for m in moves:
            b[m[0]][m[1]][m[2]] = 'O'
            eval = minimax(b, d-1, False, alpha, beta)
            b[m[0]][m[1]][m[2]] = None
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for m in moves:
            b[m[0]][m[1]][m[2]] = 'X'
            eval = minimax(b, d-1, True, alpha, beta)
            b[m[0]][m[1]][m[2]] = None
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

def ai_move():
    best = -float('inf')
    move = None
    for l in range(4):
        for r in range(4):
            for c in range(4):
                if board[l][r][c] is None:
                    board[l][r][c] = 'O'
                    val = minimax(board, difficulty_depth, False, -float('inf'), float('inf'))
                    board[l][r][c] = None
                    if val > best:
                        best = val
                        move = (l, r, c)
    if move:
        board[move[0]][move[1]][move[2]] = 'O'

def distance_to_ray(p1, p2, point):
    px, py, pz = point
    dx, dy, dz = [p2[i] - p1[i] for i in range(3)]
    t = sum((point[i] - p1[i]) * (p2[i] - p1[i]) for i in range(3)) / sum((p2[i] - p1[i])**2 for i in range(3))
    t = max(0, min(1, t))
    closest = [p1[i] + t * (p2[i] - p1[i]) for i in range(3)]
    return math.sqrt(sum((closest[i] - point[i])**2 for i in range(3)))

def handle_click(x, y):
    model = glGetDoublev(GL_MODELVIEW_MATRIX)
    proj = glGetDoublev(GL_PROJECTION_MATRIX)
    view = glGetIntegerv(GL_VIEWPORT)
    y = view[3] - y
    near = gluUnProject(x, y, 0.0, model, proj, view)
    far = gluUnProject(x, y, 1.0, model, proj, view)
    closest = None
    min_d = float('inf')
    for l in range(4):
        for r in range(4):
            for c in range(4):
                if board[l][r][c] is None:
                    pos = ((c - 2)*CUBE_SPACING, (r - 2)*CUBE_SPACING, (l - 2)*CUBE_SPACING)
                    d = distance_to_ray(near, far, pos)
                    if d < 1 and d < min_d:
                        min_d = d
                        closest = (l, r, c)
    return closest

def select_difficulty():
    global difficulty_depth
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 48)
    options = [("Easy", 2), ("Difficult", 4), ("Insane", 6)]
    running = True
    while running:
        screen.fill((255, 255, 255))
        y = 200
        for label, depth in options:
            rect = pygame.Rect(250, y, 300, 60)
            pygame.draw.rect(screen, (0, 120, 200), rect)
            text = font.render(label, True, (255, 255, 255))
            screen.blit(text, (rect.x + 75, rect.y + 10))
            y += 100
        for event in pygame.event.get():
            if event.type == QUIT: sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 250 <= mx <= 550:
                    if 200 <= my <= 260:
                        difficulty_depth = 2
                        running = False
                    elif 300 <= my <= 360:
                        difficulty_depth = 4
                        running = False
                    elif 400 <= my <= 460:
                        difficulty_depth = 6
                        running = False
        pygame.display.update()

def main():
    global winner
    pygame.init()
    select_difficulty()
    pygame.display.set_mode((1000, 800), DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -30)

    clock = pygame.time.Clock()
    angle = 0
    player_turn = True

    while True:
        for e in pygame.event.get():
            if e.type == QUIT: sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1 and player_turn and not winner:
                mx, my = pygame.mouse.get_pos()
                pos = handle_click(mx, my)
                if pos:
                    board[pos[0]][pos[1]][pos[2]] = 'X'
                    if check_win(board, 'X'):
                        winner = "PLAYER WINS!"
                    player_turn = False
        if not player_turn and not winner:
            ai_move()
            if check_win(board, 'O'):
                winner = "AI WINS!"
            player_turn = True

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -30)
        glRotatef(angle, 1, 1, 0)
        angle += 0.3
        draw_grid()
        draw_spheres()
        if winner:
            draw_winner_message(winner)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
