# GIF nets sur l'AniMe Matrix du ROG Strix Flare II Animate (outils Linux de ce dépôt)

## Ce que l'écran est vraiment
- 312 LED monochromes en 24 rangées décalées en diagonale, de 19 LED (haut) à 7 LED (bas), −1 toutes les deux rangées : un coin, pas un rectangle.
- Une valeur 0–255 par LED, sans correction gamma ; à l'œil on distingue 3 niveaux sûrs : éteint, faible (≈ 25 %), plein. Les dégradés n'existent pas.
- Pas d'isolation entre LED : une LED pleine éclaire ses voisines (halo). Une LED isolée entourée de noir reste nette ; deux formes se touchant fusionnent.
- Le lanceur (`rog_flare2_launcher.py`, `image_to_frame`) convertit chaque image en gris, la ramène à 24 lignes (LANCZOS), puis échantillonne chaque rangée sur toute la largeur de l'image, proportionnellement au nombre de LED de la rangée : la rangée du haut montre l'image en 19 points, celle du bas en 7. Un trait vertical dans la source devient donc une diagonale qui suit le bord du coin.

## Réglages
| Point | Règle | Pourquoi |
|---|---|---|
| Toile | 19 × 24 px, un pixel = une LED de la rangée du haut ; le lanceur ne rééchantillonne alors pas | toute autre taille passe par LANCZOS, qui floute |
| Détail | à placer dans le tiers haut (19 → 15 LED) ; le bas (≤ 10 LED) ne porte que des masses | résolution horizontale décroissante |
| Couleurs | gris, puis postérisation à 3 niveaux (0, 64, 255) ; contraste à fond | 3 niveaux perçus, halo qui aplatit le reste |
| Tramage | aucun (ni Floyd–Steinberg ni ordonné) : sur 19 LED avec halo, un tramage = bruit | le halo fait déjà le mélange |
| Traits | épaisseur 1 LED en vertical (les rangées sont séparées), ≥ 2 LED en horizontal, 1 LED de noir entre deux formes | halo entre voisines de la même rangée |
| Fond | noir pur, sujet blanc ; jamais d'inversion partielle | une zone claire large devient une flaque |
| Cadence | 8–12 images/s, durées GIF ≥ 80 ms (le lecteur impose ≥ 20 ms) ; supprimer les images quasi identiques | le rafraîchissement LED est ≈ 16 Hz, l'envoi USB en dessous |
| Luminosité | `--brightness 50` à `70` ; pas 100 | à 100 le halo mange les contours |
| Mouvement | lent, translation d'une LED par image au plus ; pas de vidéo réaliste | une LED = 4 mm, tout mouvement rapide devient un flou |
| Format | GIF gris, palette ≤ 4 couleurs, sans transparence, boucle infinie, image complète à chaque trame (pas de trames partielles) | `load_gif_frames` recompose sur une toile : les trames partielles s'empilent |

## Conversion

Le lanceur (*Convertir des GIF…*) et `animematrix-convertir` utilisent par défaut la **conversion intelligente** : recadrage sur le sujet, sujet clair sur fond noir (un dessin sur fond blanc est inversé), traits fins épaissis, contours renforcés pour les photos (sans nappe claire), 3 niveaux, images quasi identiques fusionnées, durées ≥ 80 ms. `--classique` garde la chaîne ImageMagick d'origine ci-dessous.

## Chaîne de préparation classique (ImageMagick, à partir de n'importe quel GIF)
```
convert entree.gif -coalesce -colorspace Gray -resize 19x24! -filter Lanczos \
        -contrast-stretch 2%x2% -posterize 3 -dither None -loop 0 sortie.gif
```
- `-resize 19x24!` force la toile ; remplacer `-filter Lanczos` par `-filter Point` pour un pixel-art déjà à cette taille.
- Pour garder la géométrie (un carré reste un carré) : option *Géométrie fidèle* du lanceur (ou `animematrix-ctl gif --fidele`). L'image 19 × 24 est posée sur le coin réel : la rangée r couvre les colonnes (r+1)//2 à 18, le bord droit est vertical et le bord gauche en diagonale ; ce qui dépasse à gauche en bas est perdu au lieu d'être étiré. L'écran est à peu près carré (19 pas de LED de large, 24 rangées espacées de 0,77 pas).
- Vérifier une image fixe avant d'animer : `rog_flare2_matrix_paint.py` montre le rendu LED par LED.
- Lecture : `rog_flare2_folder_player.py dossier --brightness 60`.

## Ce qui marche le mieux
Silhouettes, pictogrammes, texte de 1 à 3 lettres en haut, pulsations lentes, balayages d'une LED. Ce qui ne marche pas : photos, vidéos, dégradés, petits caractères, deux objets proches.

Sources : mesures du dépôt (`docs/PROTOCOL.md`, `image_to_frame`) ; Yoshi Walsh, « Mastering the AniMe Matrix » (G14 : halo, 3–4 niveaux perçus, 16 Hz, pas de gamma) — https://blog.yoshiwalsh.me/asus-anime-matrix/
