# Origine

`effects.py` et `renderer.py` viennent de PolyWollyWin, de Mike Opitz :
https://github.com/MikeOpitz99/PolyWollyWin, commit `4c14981` (v3.25.0), licence MIT (`LICENSE`).

Copiés sans modification. L'adaptation Linux est dans `../rog_flare2_effets.py` :
capture audio par `parec` (moniteur de la sortie par défaut) au lieu de
sounddevice/Stereo Mix, envoi par le transport du dépôt. Non repris : l'interface
PySide6 (`app.py`), propre à Windows (registre, windll, barre des tâches).

Mise à jour : recopier les deux fichiers, puis `rog_flare2_effets.py --liste`.
