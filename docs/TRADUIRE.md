# Traduire AniMe Matrix

L'interface existe en 19 langues. Toute correction est bienvenue, et une nouvelle langue aussi.

## Avec Weblate (le plus simple)

Le projet est traduit en ligne sur **Hosted Weblate** : on corrige dans le navigateur, sans outil ni compte GitHub
(le lien apparaîtra ici et dans le README dès l'ouverture du projet). Weblate propose ensuite les changements au
dépôt.

## Directement dans le dépôt

- `locale/<code>.json` : un fichier par langue, `"texte source": "traduction"`.
- `locale/_source.json` : le texte français de chaque clé (fichier de base pour Weblate) ;
  `locale/_cles.json` : où chaque texte apparaît. Ces deux fichiers ne se traduisent pas.
- Les accolades (`{nom}`, `{n}`, `{version}`…) restent telles quelles.
- Textes courts : ce sont des boutons et des étiquettes d'une petite fenêtre.
- Vérification : `.venv/bin/python -m pytest -q tests/test_i18n_docs.py`.

Nouvelle langue : copier `locale/en.json` en `locale/<code>.json`, traduire, ajouter le code dans
`rog_flare2_i18n.py` (`LANGUAGES`) et ouvrir une demande de fusion.

## Pour la personne qui ouvre le projet Weblate

Sur <https://hosted.weblate.org> (offre gratuite « Libre » pour les projets sous licence libre) :

1. Créer le projet **AniMe Matrix**, puis un composant **Interface** :
   - dépôt : `https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git`, branche `main` ;
   - format : **JSON file** ; masque des fichiers : `locale/*.json` ;
   - fichier de base monolingue : `locale/_source.json` ; langue source : **français** ;
   - filtre des langues : `^[a-z]{2}(-[A-Z]{2})?$` (écarte `_source` et `_cles`).
2. Envoi des traductions : « Demandes de fusion GitHub » (Weblate ouvre une demande de fusion), ou clé SSH de
   Weblate ajoutée comme clé de déploiement en écriture du dépôt.
3. Ajouter le lien du projet et son badge dans le README.
