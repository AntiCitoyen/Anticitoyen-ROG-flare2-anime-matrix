"""Jeux : règles de base, touches, fin de partie et records, touches via le démon."""
import numpy as np

import rog_flare2_effets as E
import rog_flare2_jeux as J
from rog_flare2_matrix_paint import LED_COUNT
from rog_flare2_jeux import ROWS


def play(game, steps):
    for _ in range(steps):
        if game.over:
            break
        game.step()


def test_all_games_render():
    for g in J.GAMES:
        game = E.make_effect(g.name)
        for _ in range(20):
            assert len(game.tick(0.1)) == LED_COUNT


def test_snake_eats_then_hits_the_wall():
    s = J.SnakeGame()
    head = s.body[0]
    s.food = (head[0], head[1] + 1)
    s.step()
    assert s.score == 1 and len(s.body) == 4
    play(s, 40)  # tout droit vers la droite : le bord de l'écran
    assert s.over and J.high_score("snake") >= 1
    s.on_key("Return")
    assert not s.over and s.score == 0


def test_snake_cannot_reverse():
    s = J.SnakeGame()
    s.on_key("Left")  # demi-tour interdit
    assert s.next_dir == (0, 1)
    s.on_key("Up")
    assert s.next_dir == (-1, 0)


def test_tetris_clears_a_line():
    t = J.TetrisGame()
    t.board[-1, :] = True
    t.board[-1, 0] = False
    t.piece, t.pos = [[0, 0]], [J.ROWS - 1, 0]  # pièce d'une case qui comble le trou
    t.step()
    assert t.score == 1 and not t.board[-1].all()


def test_tetris_rotation_and_moves():
    t = J.TetrisGame()
    col = t.pos[1]
    t.on_key("Left")
    assert t.pos[1] == col - 1
    before = [list(c) for c in t.piece]
    t.on_key("Up")
    assert t.piece != before or before == [[0, 0], [0, 1], [1, 0], [1, 1]]  # le carré ne tourne pas


def test_breakout_breaks_bricks():
    b = J.BreakoutGame()
    b.ball, b.vel = [3.0, 30.0], [-1.0, 0.0]
    n = len(b.bricks)
    b.step()
    assert len(b.bricks) == n - 1 and b.score == 1


def test_pong_paddle_moves():
    p = J.PongGame()
    row = p.player
    p.on_key("Down")
    assert p.player == row + 1


def test_game_over_frame_scrolls():
    s = J.SnakeGame()
    s.game_over()
    frame = np.array(s.tick(0.5))
    assert frame.shape == (LED_COUNT,)


def test_daemon_forwards_keys(monkeypatch):
    import rog_flare2_demon as D
    from tests.test_demon import FakeTransport
    monkeypatch.setattr(D, "FlareTransport", FakeTransport)
    d = D.Daemon()
    try:
        assert d.handle({"cmd": "key", "key": "Up"})["ok"] is False  # pas de jeu
        d.handle({"cmd": "play", "show": {"type": "effet", "name": "Snake (game)"}})
        import time
        time.sleep(0.3)
        assert d.handle({"cmd": "key", "key": "Up"})["ok"]
        assert d.effect.next_dir == (-1, 0)
    finally:
        d.stop()


def test_pong_duo_points_and_winner():
    g = J.PongDuoGame()
    g.key("z")
    assert g.player == 1
    g.key("Down")
    assert g.cpu == 3
    for _ in range(g.WIN):
        g.ball, g.vel = [3.0, float(g.RIGHT)], [0.0, 1.0]  # balle qui sort à droite : point au joueur 1
        g.cpu = 0 if g.ball[0] > 2 else 4
        g.step()
    assert g.over and g.points[0] == g.WIN and "PLAYER 1 WINS" in g._over_text.message


def test_invaders_shot_kills_an_alien():
    g = J.InvadersGame()
    target = max(g.aliens)  # rangée la plus basse
    g.ship = target[1]
    g.key("space")
    for _ in range(ROWS):
        g.step()
        if g.score:
            break
    assert g.score == 10 and target not in g.aliens


def test_flappy_falls_without_flapping():
    g = J.FlappyGame()
    for _ in range(200):
        g.step()
        if g.over:
            break
    assert g.over


def test_flappy_flap_goes_up():
    g = J.FlappyGame()
    y0 = g.y
    g.key("space")
    g.step()
    assert g.y < y0
