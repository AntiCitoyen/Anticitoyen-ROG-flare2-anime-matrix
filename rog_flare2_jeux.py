"""Jeux jouables sur l'AniMe Matrix : Snake, Pong (seul ou à deux), Tetris, casse-briques, Invaders, Flappy.

Chaque jeu est un effet (moteur PolyWollyWin) qui tourne dans le démon ; le
lanceur lui transmet les touches (flèches, espace, Entrée) quand sa fenêtre a le
focus. Grille logique 12 × 37 : la rangée r n'a de LED que des colonnes 2r à 36.
Meilleurs scores : ~/.config/rog-flare2/scores.json.
"""
from __future__ import annotations

import json
import random
import sys as _sys
from pathlib import Path as _Path

import numpy as np

_sys.path.insert(0, str(_Path(__file__).parent / "polywollywin"))  # moteur d'effets
from effects import COLS, MASK_NP, ROWS, BaseEffect  # noqa: E402

from rog_flare2_core import CONFIG_DIR  # noqa: E402

SCORES_FILE = CONFIG_DIR / "scores.json"
DIM, MID, FULL = 45, 140, 255


def high_score(game: str, score: int | None = None) -> int:
    """Meilleur score du jeu ; l'enregistre si score le dépasse."""
    try:
        scores = json.loads(SCORES_FILE.read_text())
    except (OSError, ValueError):
        scores = {}
    best = int(scores.get(game, 0))
    if score is not None and score > best:
        scores[game] = best = score
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        SCORES_FILE.write_text(json.dumps(scores))
    return best


class GameEffect(BaseEffect):
    """Base : pas de simulation fixe (step), touches (on_key), fin de partie avec score défilant."""

    game = ""
    STEP = 0.15  # secondes par pas de jeu

    def __init__(self, speed: float = 1.0):
        self.speed = speed
        self._acc = 0.0
        self._over_text = None
        self.reset()

    def reset(self):
        self.score = 0
        self.over = False
        self._over_text = None

    def on_key(self, key: str):
        if self.over:
            if key in ("Return", "space", "KP_Enter"):
                self.reset()
            return
        self.key(key)

    def key(self, key: str):
        pass

    def step(self):
        raise NotImplementedError

    def draw(self, frame: np.ndarray):
        raise NotImplementedError

    def game_over(self):
        self.over = True
        best = high_score(self.game, self.score)
        from rog_flare2_effets import make_effect
        self._over_text = make_effect("Scroll Text", {"message": f"GAME OVER {self.score}  BEST {best}"})

    def tick(self, dt: float) -> list[int]:
        if self.over:
            return self._over_text.tick(dt)
        self._acc += dt * self.speed
        while self._acc >= self.STEP and not self.over:
            self._acc -= self.STEP
            self.step()
        frame = np.zeros((ROWS, COLS), dtype=np.float32)
        self.draw(frame)
        return self._emit(frame)


class SnakeGame(GameEffect):
    name = "Snake (game)"
    game = "snake"
    PARAMS = {"speed": {"label": "Speed", "min": 50, "max": 250, "default": 100, "scale": 100.0}}
    DIRS = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}

    def reset(self):
        super().reset()
        self.body = [(6, 26), (6, 25), (6, 24)]
        self.dir = self.next_dir = (0, 1)
        self._food()

    def _food(self):
        free = [(r, c) for r in range(ROWS) for c in range(COLS) if MASK_NP[r, c] and (r, c) not in self.body]
        self.food = random.choice(free)

    def key(self, key):
        d = self.DIRS.get(key)
        if d and (d[0] != -self.dir[0] or d[1] != -self.dir[1]):
            self.next_dir = d

    def step(self):
        self.dir = self.next_dir
        r, c = self.body[0][0] + self.dir[0], self.body[0][1] + self.dir[1]
        if not (0 <= r < ROWS and 0 <= c < COLS and MASK_NP[r, c]) or (r, c) in self.body[:-1]:
            self.game_over()
            return
        self.body.insert(0, (r, c))
        if (r, c) == self.food:
            self.score += 1
            self._food()
        else:
            self.body.pop()

    def draw(self, frame):
        for i, (r, c) in enumerate(self.body):
            frame[r, c] = FULL if i == 0 else MID
        frame[self.food] = FULL if int(self._acc * 20) % 2 == 0 else DIM


class PongGame(GameEffect):
    """Pong contre l'ordinateur, dans la bande du haut (rangées 0-5, colonnes 10-36)."""
    name = "Pong (game)"
    game = "pong"
    STEP = 0.07
    PARAMS = {"speed": {"label": "Speed", "min": 50, "max": 200, "default": 100, "scale": 100.0}}
    TOP, BOTTOM, LEFT, RIGHT = 0, 5, 10, 36

    def reset(self):
        super().reset()
        self.player = self.cpu = 2  # rangée du haut de la raquette (hauteur 2)
        self._serve(1)

    def _serve(self, direction):
        self.ball = [3.0, 23.0]
        self.vel = [random.choice((-0.5, 0.5)), 1.0 * direction]

    def key(self, key):
        if key == "Up":
            self.player = max(self.TOP, self.player - 1)
        elif key == "Down":
            self.player = min(self.BOTTOM - 1, self.player + 1)

    def step(self):
        b, v = self.ball, self.vel
        b[0] += v[0]
        b[1] += v[1]
        if b[0] < self.TOP or b[0] > self.BOTTOM:
            v[0] = -v[0]
            b[0] += 2 * v[0]
        target = b[0] - 0.5  # l'ordinateur suit la balle, un peu en retard
        if self.cpu < target - 0.5 and self.cpu < self.BOTTOM - 1:
            self.cpu += 1 if random.random() < 0.8 else 0
        elif self.cpu > target + 0.5 and self.cpu > self.TOP:
            self.cpu -= 1 if random.random() < 0.8 else 0
        for paddle_col, row, sign in ((self.LEFT + 1, self.player, 1), (self.RIGHT - 1, self.cpu, -1)):
            if round(b[1]) == paddle_col and row - 0.5 <= b[0] <= row + 1.5 and v[1] * sign < 0:
                v[1] = -v[1]
                v[0] = max(-1.0, min(1.0, v[0] + (b[0] - row - 0.5) * 0.5))
                if sign == 1:
                    self.score += 1
        if b[1] < self.LEFT:
            self.game_over()
        elif b[1] > self.RIGHT:
            self.score += 3  # point marqué contre l'ordinateur
            self._serve(-1)

    def draw(self, frame):
        for r in (self.player, self.player + 1):
            frame[r, self.LEFT] = FULL
        for r in (self.cpu, self.cpu + 1):
            frame[r, self.RIGHT] = MID
        frame[min(self.BOTTOM, max(self.TOP, int(round(self.ball[0])))), int(round(self.ball[1]))] = FULL
        frame[self.BOTTOM + 1, self.LEFT + 2:self.RIGHT + 1] = DIM  # bord bas du terrain


TETROMINOES = [
    [(0, 0), (0, 1), (0, 2), (0, 3)], [(0, 0), (0, 1), (1, 0), (1, 1)], [(0, 1), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (1, 2)], [(0, 2), (1, 0), (1, 1), (1, 2)], [(0, 1), (0, 2), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)],
]


class TetrisGame(GameEffect):
    """Tetris dans le rectangle de droite : 12 rangées × 10 colonnes (26-35), bords éclairés."""
    name = "Tetris (game)"
    game = "tetris"
    STEP = 0.45
    PARAMS = {"speed": {"label": "Speed", "min": 50, "max": 300, "default": 100, "scale": 100.0}}
    W, LEFT = 10, 26

    def reset(self):
        super().reset()
        self.board = np.zeros((ROWS, self.W), dtype=bool)
        self._spawn()

    def _spawn(self):
        self.piece = [list(p) for p in random.choice(TETROMINOES)]
        self.pos = [0, self.W // 2 - 2]
        if self._collides(self.piece, self.pos):
            self.game_over()

    def _cells(self, piece, pos):
        return [(pos[0] + r, pos[1] + c) for r, c in piece]

    def _collides(self, piece, pos):
        return any(not (0 <= r < ROWS and 0 <= c < self.W) or self.board[r, c] for r, c in self._cells(piece, pos))

    def key(self, key):
        moves = {"Left": (0, -1), "Right": (0, 1), "Down": (1, 0)}
        if key in moves:
            new = [self.pos[0] + moves[key][0], self.pos[1] + moves[key][1]]
            if not self._collides(self.piece, new):
                self.pos = new
        elif key in ("Up", "space"):
            h = max(r for r, _c in self.piece)
            rotated = [[c, h - r] for r, c in self.piece]
            if not self._collides(rotated, self.pos):
                self.piece = rotated

    def step(self):
        down = [self.pos[0] + 1, self.pos[1]]
        if not self._collides(self.piece, down):
            self.pos = down
            return
        for r, c in self._cells(self.piece, self.pos):
            self.board[r, c] = True
        full = [r for r in range(ROWS) if self.board[r].all()]
        if full:
            self.board = np.vstack([np.zeros((len(full), self.W), dtype=bool), np.delete(self.board, full, axis=0)])
            self.score += (0, 1, 3, 5, 8)[len(full)]
            self.STEP = max(0.12, 0.45 - 0.02 * self.score)
        self._spawn()

    def draw(self, frame):
        frame[:, self.LEFT - 1] = DIM
        frame[:, min(COLS - 1, self.LEFT + self.W)] = DIM
        frame[:, self.LEFT:self.LEFT + self.W][self.board] = MID
        for r, c in self._cells(self.piece, self.pos):
            frame[r, self.LEFT + c] = FULL


class BreakoutGame(GameEffect):
    """Casse-briques dans le rectangle de droite (colonnes 22-36), raquette en bas."""
    name = "Breakout (game)"
    game = "breakout"
    STEP = 0.08
    PARAMS = {"speed": {"label": "Speed", "min": 50, "max": 200, "default": 100, "scale": 100.0}}
    LEFT, RIGHT, PADDLE = 22, 36, 4

    def reset(self):
        super().reset()
        self.bricks = {(r, c) for r in range(3) for c in range(self.LEFT, self.RIGHT + 1)}
        self.paddle = 27
        self.ball = [9.0, 29.0]
        self.vel = [-1.0, random.choice((-1.0, 1.0))]

    def key(self, key):
        if key == "Left":
            self.paddle = max(self.LEFT, self.paddle - 2)
        elif key == "Right":
            self.paddle = min(self.RIGHT - self.PADDLE + 1, self.paddle + 2)

    def step(self):
        b, v = self.ball, self.vel
        nr, nc = b[0] + v[0], b[1] + v[1]
        if nc < self.LEFT or nc > self.RIGHT:
            v[1] = -v[1]
            nc = b[1] + v[1]
        if nr < 0:
            v[0] = -v[0]
            nr = b[0] + v[0]
        cell = (int(round(nr)), int(round(nc)))
        if cell in self.bricks:
            self.bricks.discard(cell)
            self.score += 1
            v[0] = -v[0]
            nr = b[0] + v[0]
            if not self.bricks:
                self.reset_bricks()
        if nr >= ROWS - 1:
            if self.paddle - 1 <= nc <= self.paddle + self.PADDLE:
                v[0] = -1.0
                v[1] = -1.0 if nc < self.paddle + self.PADDLE / 2 else 1.0
                nr = ROWS - 2
            else:
                self.game_over()
                return
        b[0], b[1] = nr, nc

    def reset_bricks(self):
        self.bricks = {(r, c) for r in range(3) for c in range(self.LEFT, self.RIGHT + 1)}
        self.STEP = max(0.04, self.STEP * 0.85)

    def draw(self, frame):
        for r, c in self.bricks:
            frame[r, c] = MID
        frame[ROWS - 1, self.paddle:self.paddle + self.PADDLE] = FULL
        frame[min(ROWS - 1, max(0, int(round(self.ball[0])))), int(round(self.ball[1]))] = FULL


class PongDuoGame(PongGame):
    """Pong à deux sur le même clavier : joueur 1 à gauche (Z/W et S), joueur 2 à droite (flèches)."""
    name = "Pong 2P (game)"
    game = "pong2"
    WIN = 5

    def reset(self):
        GameEffect.reset(self)
        self.player = self.cpu = 2
        self.points = [0, 0]
        self._serve(1)

    def key(self, key):
        k = key.lower()
        if k in ("w", "z"):
            self.player = max(self.TOP, self.player - 1)
        elif k == "s":
            self.player = min(self.BOTTOM - 1, self.player + 1)
        elif key == "Up":
            self.cpu = max(self.TOP, self.cpu - 1)
        elif key == "Down":
            self.cpu = min(self.BOTTOM - 1, self.cpu + 1)

    def step(self):
        b, v = self.ball, self.vel
        b[0] += v[0]
        b[1] += v[1]
        if b[0] < self.TOP or b[0] > self.BOTTOM:
            v[0] = -v[0]
            b[0] += 2 * v[0]
        for paddle_col, row, sign in ((self.LEFT + 1, self.player, 1), (self.RIGHT - 1, self.cpu, -1)):
            if round(b[1]) == paddle_col and row - 0.5 <= b[0] <= row + 1.5 and v[1] * sign < 0:
                v[1] = -v[1] * 1.05  # un peu plus vite à chaque renvoi
                v[0] = max(-1.0, min(1.0, v[0] + (b[0] - row - 0.5) * 0.5))
        if b[1] < self.LEFT or b[1] > self.RIGHT:
            winner = 1 if b[1] < self.LEFT else 0
            self.points[winner] += 1
            if self.points[winner] >= self.WIN:
                self.over = True
                from rog_flare2_effets import make_effect
                self._over_text = make_effect("Scroll Text", {
                    "message": f"PLAYER {winner + 1} WINS {max(self.points)}-{min(self.points)}"})
                return
            self._serve(1 if winner == 0 else -1)

    def draw(self, frame):
        super().draw(frame)
        for i in range(self.points[0]):  # points : petits traits sous le terrain
            frame[self.BOTTOM + 3, 14 + i * 2] = FULL
        for i in range(self.points[1]):
            frame[self.BOTTOM + 3, 36 - i * 2] = FULL


class InvadersGame(GameEffect):
    """Envahisseurs dans le rectangle de droite (colonnes 22-36) : canon en bas, flèches et Espace."""
    name = "Invaders (game)"
    game = "invaders"
    STEP = 0.05
    PARAMS = {"speed": {"label": "Speed", "min": 50, "max": 200, "default": 100, "scale": 100.0}}
    LEFT, RIGHT = 22, 36

    def reset(self):
        super().reset()
        self.wave = 0
        self._wave()

    def _wave(self):
        self.aliens = {(r, c) for r in (0, 2, 4) for c in range(self.LEFT + 1, self.RIGHT - 3, 2)}
        self.dir = 1
        self.ship = 29
        self.shots: list[list[int]] = []
        self.bombs: list[list[int]] = []
        self.ticks = 0
        self.march = max(4, 12 - 2 * self.wave)  # pas de jeu entre deux mouvements des envahisseurs

    def key(self, key):
        if key == "Left":
            self.ship = max(self.LEFT, self.ship - 1)
        elif key == "Right":
            self.ship = min(self.RIGHT, self.ship + 1)
        elif key in ("space", "Up") and len(self.shots) < 2:
            self.shots.append([ROWS - 2, self.ship])

    def step(self):
        self.ticks += 1
        for shot in self.shots:
            shot[0] -= 1
        for bomb in self.bombs:
            if self.ticks % 3 == 0:
                bomb[0] += 1
        for shot in list(self.shots):
            hit = (shot[0], shot[1])
            if hit in self.aliens:
                self.aliens.discard(hit)
                self.shots.remove(shot)
                self.score += 10
            elif shot[0] < 0:
                self.shots.remove(shot)
        self.bombs = [b for b in self.bombs if b[0] < ROWS]
        if any(b[0] == ROWS - 1 and b[1] == self.ship for b in self.bombs):
            self.game_over()
            return
        if not self.aliens:
            self.wave += 1
            self.score += 50
            self._wave()
            return
        if self.ticks % self.march == 0:
            cols = [c for _r, c in self.aliens]
            if (self.dir > 0 and max(cols) >= self.RIGHT) or (self.dir < 0 and min(cols) <= self.LEFT):
                self.aliens = {(r + 1, c) for r, c in self.aliens}
                self.dir = -self.dir
            else:
                self.aliens = {(r, c + self.dir) for r, c in self.aliens}
            if max(r for r, _c in self.aliens) >= ROWS - 2:
                self.game_over()
                return
            if random.random() < 0.5:
                r, c = random.choice(sorted(self.aliens))
                self.bombs.append([r + 1, c])

    def draw(self, frame):
        for r, c in self.aliens:
            frame[r, c] = MID
        for r, c in self.shots:
            if 0 <= r < ROWS:
                frame[r, c] = FULL
        for r, c in self.bombs:
            frame[r, c] = DIM + 40
        frame[ROWS - 1, max(self.LEFT, self.ship - 1):self.ship + 2] = FULL
        frame[ROWS - 2, self.ship] = FULL


class FlappyGame(GameEffect):
    """Oiseau qui bat des ailes (Espace ou flèche haut) entre des tuyaux, rectangle de droite."""
    name = "Flappy (game)"
    game = "flappy"
    STEP = 0.05
    PARAMS = {"speed": {"label": "Speed", "min": 50, "max": 200, "default": 100, "scale": 100.0}}
    LEFT, RIGHT, BIRD, GAP = 22, 36, 26, 4

    def reset(self):
        super().reset()
        self.y, self.vy = 5.0, 0.0
        self.pipes: list[list[int]] = []  # [colonne, rangée du haut de l'ouverture]
        self.ticks = 0

    def key(self, key):
        if key in ("space", "Up"):
            self.vy = -0.55

    def step(self):
        self.ticks += 1
        self.vy = min(0.6, self.vy + 0.07)
        self.y += self.vy
        if self.ticks % 3 == 0:
            for pipe in self.pipes:
                pipe[0] -= 1
            if pipe_passed := [p for p in self.pipes if p[0] == self.BIRD - 1]:
                self.score += len(pipe_passed)
            self.pipes = [p for p in self.pipes if p[0] >= self.LEFT]
            if not self.pipes or self.pipes[-1][0] <= self.RIGHT - 7:
                self.pipes.append([self.RIGHT, random.randint(1, ROWS - self.GAP - 1)])
        row = int(round(self.y))
        if row < 0 or row >= ROWS:
            self.game_over()
            return
        for col, top in self.pipes:
            if col == self.BIRD and not top <= row < top + self.GAP:
                self.game_over()
                return

    def draw(self, frame):
        for col, top in self.pipes:
            for r in range(ROWS):
                if not top <= r < top + self.GAP:
                    frame[r, col] = MID
        frame[max(0, min(ROWS - 1, int(round(self.y)))), self.BIRD] = FULL
        frame[max(0, min(ROWS - 1, int(round(self.y)))), self.BIRD - 1] = DIM + 60


GAMES = [SnakeGame, PongGame, PongDuoGame, TetrisGame, BreakoutGame, InvadersGame, FlappyGame]
