"""Jeux : règles de base, touches, fin de partie et records, touches via le démon."""
import numpy as np

import rog_flare2_effets as E
import rog_flare2_jeux as J
from rog_flare2_matrix_paint import LED_COUNT


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
