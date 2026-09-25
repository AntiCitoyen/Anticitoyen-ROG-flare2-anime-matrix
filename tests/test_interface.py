"""Interfaces du lanceur par VRAIS clics (xdotool) : boutons ronds, tiroir/disque, arc, lancement, arrêt.

Nécessite un affichage X (xvfb-run en intégration continue) et xdotool ; ignoré sinon.
Le démon tourne avec un clavier factice (ANIMEMATRIX_FAUX_CLAVIER, voir conftest.py).
"""
import math
import os
import shutil
import subprocess
from tkinter import ttk

import pytest

pytestmark = pytest.mark.skipif(not os.environ.get("DISPLAY") or not shutil.which("xdotool"),
                                reason="affichage X et xdotool requis")


def click(x, y):
    subprocess.run(["xdotool", "mousemove", str(int(x)), str(int(y)), "click", "1"], check=True)


def run_steps(app, steps, delay=500):
    """Exécute des étapes (action, vérification) dans la boucle Tk ; renvoie les échecs."""
    failures = []

    def step(k=0):
        if k >= len(steps):
            app.destroy()
            return
        name, action, check = steps[k]

        def verify():
            try:
                ok = check()
            except Exception as exc:  # une vérification qui plante ne doit pas bloquer la boucle Tk
                ok = False
                name_err = f"{name} ({exc!r})"
                failures.append(name_err)
            else:
                if not ok:
                    failures.append(name)
            step(k + 1)
        try:
            action()
        except Exception as exc:
            failures.append(f"{name} : action ({exc!r})")
        app.after(delay, verify)
    app.after(1000, step)
    app.mainloop()
    return failures


@pytest.fixture
def launcher():
    import rog_flare2_ctl as ctl
    import rog_flare2_launcher as L

    def make(interface):
        L.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        L.INTERFACE_FILE.write_text(interface)
        return L.LauncherApp()
    yield make
    try:
        ctl.request("quit", timeout=2)
    except Exception:
        pass


@pytest.mark.parametrize("interface", ["drawer", "dial", "rounded"])
def test_round_interface_by_real_clicks(launcher, interface):
    import rog_flare2_ctl as ctl
    app = launcher(interface)
    ui = app.round_ui
    at = lambda x, y: click(app.winfo_rootx() + x, app.winfo_rooty() + y)  # noqa: E731
    steps = []
    if interface == "rounded":
        for i, (img, _txt, pw) in enumerate(ui.pills):
            x, y = ui.canvas.coords(img)
            steps.append((f"pilule {i}", lambda x=x, y=y, pw=pw: at(x + pw / 2, y + 16), lambda i=i: ui.open_section == i))
    else:
        ui.toggle_section(None)
        for i in range(4):
            b = ui.buttons[i]
            steps.append((f"bouton {i}", lambda b=b: at(b.cx, b.cy), lambda i=i: ui.open_section == i))
            closer = ui.close_overlay if interface == "dial" else b
            steps.append((f"referme {i}", lambda c=closer: at(c.cx, c.cy), lambda: ui.open_section is None))
    a = ui.arc
    ang = math.radians(a.start + a.sweep * 0.8)
    steps.append(("arc de luminosité", lambda: at(a.cx + a.r * math.cos(ang), a.cy + a.r * math.sin(ang)),
                  lambda: 70 <= ctl.request("status")["brightness"] <= 92))

    def launch_effect():
        ui.toggle_section(1, keep_open=True)
        app.update()
        btn = [w for w in ui.frames[1].winfo_children() if isinstance(w, ttk.Button)][0]
        click(btn.winfo_rootx() + btn.winfo_width() // 2, btn.winfo_rooty() + btn.winfo_height() // 2)
    steps.append(("lancer l'effet", launch_effect,
                  lambda: (ctl.request("status")["show"] or {}).get("type") == "effet"))
    steps.append(("aperçu reçu", lambda: None, lambda: bool(app.last_frame) and any(app.last_frame[4:])))
    if interface == "dial":
        steps.append(("referme le disque", lambda: at(ui.close_overlay.cx, ui.close_overlay.cy),
                      lambda: ui.open_section is None))
    stop = next(b for b in ui.all_buttons if b.command == app.stop_and_clear)
    steps.append(("arrêter", lambda: at(stop.cx, stop.cy), lambda: ctl.request("status")["show"] is None))
    assert run_steps(app, steps) == []


def test_classic_interface(launcher):
    import rog_flare2_ctl as ctl
    app = launcher("classic")
    steps = [("horloge", app.start_clock, lambda: ctl.request("status")["show"]["type"] == "horloge"),
             ("arrêter", app.stop_and_clear, lambda: ctl.request("status")["show"] is None)]
    assert run_steps(app, steps) == []


def test_effect_list_fully_visible_and_game_by_real_clicks(launcher):
    """Liste des effets entière (Moniteur système et jeux en fin de liste) ; un jeu se lance par clics."""
    import rog_flare2_ctl as ctl
    from rog_flare2_core import VERSION
    app = launcher("drawer")
    ui = app.round_ui
    assert VERSION in ui.canvas.itemcget(ui.sub_id, "text")
    frame = ui.frames[1]
    cb = [w for w in frame.winfo_children() if isinstance(w, ttk.Combobox)][0]
    assert int(cb["height"]) >= len(cb["values"])
    lb = cb.tk.eval(f"ttk::combobox::PopdownWindow {cb}") + ".f.l"

    def pick():
        i = list(cb["values"]).index("Snake (jeu)")
        x, y, _w, h = map(int, cb.tk.eval(f"{lb} bbox {i}").split())
        click(cb.tk.call("winfo", "rootx", lb) + x + 20, cb.tk.call("winfo", "rooty", lb) + y + h // 2)

    def launch():
        b = [w for w in frame.winfo_children() if isinstance(w, ttk.Button) and "Lancer" in str(w["text"])][0]
        click(b.winfo_rootx() + b.winfo_width() / 2, b.winfo_rooty() + b.winfo_height() / 2)

    steps = [("section", lambda: ui.toggle_section(1, keep_open=True), lambda: True),
             ("liste", lambda: click(cb.winfo_rootx() + cb.winfo_width() - 8,
                                     cb.winfo_rooty() + cb.winfo_height() / 2), lambda: True),
             ("choix", pick, lambda: cb.get() == "Snake (jeu)"),
             ("lancer", launch, lambda: (ctl.request("status")["show"] or {}).get("name") == "Snake (game)")]
    assert run_steps(app, steps, delay=900) == []
