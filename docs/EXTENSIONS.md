# Écrire un effet (extension)

Un effet est un fichier Python déposé dans **`~/.config/rog-flare2/effets/`**. Au démarrage, le lanceur et le démon `animematrixd` le chargent. L'effet apparaît alors dans l'onglet *Effets* (ou *Audio*) et dans `animematrix-ctl effet <nom>`.

> ⚠️ Une extension est du code exécuté avec vos droits. N'installez que des fichiers dont vous avez lu le contenu.

## Le minimum

```python
from effects import COLS, ROWS, BaseEffect   # moteur d'effets (polywollywin/effects.py)
import numpy as np

class MonEffet(BaseEffect):
    name = "Mon effet"                      # nom interne, unique
    noms = {"fr": "Mon effet", "en": "My effect"}   # facultatif : nom affiché selon la langue
    PARAMS = {                              # curseurs affichés dans le lanceur
        "speed": {"label": "Speed", "min": 10, "max": 300, "default": 100, "scale": 100.0},
    }

    def __init__(self, speed: float = 1.0):
        self.speed = speed
        self._t = 0.0

    def tick(self, dt: float) -> list[int]:
        """Appelée ~30 fois par seconde ; renvoie 312 valeurs 0-255 (ordre des LED du clavier)."""
        self._t += dt * self.speed
        frame = np.zeros((ROWS, COLS), dtype=np.float32)   # grille logique 12 x 37
        col = int(self._t * 10) % COLS
        frame[:, col] = 255
        return self._emit(frame)             # applique le masque et convertit en 312 octets
```

## Ce qu'il faut savoir

- **Grille** : 12 rangées logiques × 37 colonnes ; la rangée `r` n'a de LED que des colonnes `2r` à `36` (l'écran est un coin, pas un rectangle). `self._emit(frame)` ignore le reste.
- **Niveaux** : 0 à 255, mais à l'œil seuls trois niveaux se distinguent bien (éteint, faible, plein). Le halo entre LED voisines fait fusionner les formes proches (voir [GUIDE-GIF.md](GUIDE-GIF.md)).
- **Curseurs** (`PARAMS`) : entier de `min` à `max`, divisé par `scale` puis affecté à l'attribut du même nom, **en direct** pendant que l'effet tourne. Un réglage `{"type": "text"}` affiche un champ texte.
- **Effet audio** : dériver de `_AudioReactiveBase` (même module) pour apparaître dans l'onglet *Audio* ; `level, beat = self._audio_metrics(dt)` donne le niveau sonore et les battements (voir les visualiseurs de `effects.py`).
- **Erreurs** : une extension qui ne se charge pas est ignorée, le lanceur et le démon continuent de fonctionner.
- **Mise au point** : `animematrix-ctl effet "Mon effet"` après avoir relancé le démon (`animematrix-ctl quitter`).

Exemple complet : [`examples/effets/battement_coeur.py`](../examples/effets/battement_coeur.py) (un cœur qui bat, réglable en pulsations par minute).
