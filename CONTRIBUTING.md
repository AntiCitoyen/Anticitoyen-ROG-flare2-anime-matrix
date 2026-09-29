# Contributing — Contribuer

## 🇬🇧 English

### Contributions welcome

AniMe Matrix for Linux drives the AniMe Matrix display (312 mini-LEDs) and the key lighting of the ASUS ROG Strix
Flare II Animate keyboard, without Armoury Crate or Windows: launcher, `animematrixd` daemon, effects, packages.
Bug reports, USB captures of the keyboard, translations, effects, ideas and pull requests are all welcome.

- Quick feedback on an idea or a bug: open an [issue](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
- Security problems: do **not** open an issue, follow [`SECURITY.md`](SECURITY.md).
- Translations: [`docs/TRADUIRE.md`](docs/TRADUIRE.md) (19 languages, JSON catalogues in `locale/`).
- A new effect does not need a pull request: it can ship as an extension, see [`docs/EXTENSIONS.md`](docs/EXTENSIONS.md).

### Contribution workflow

The project uses the fork-and-pull model.

1. In your fork, create a branch with a meaningful name.
2. Make your change, meeting the [quality standards](#quality-standards) below.
3. Open a pull request against `main`.
4. A maintainer reviews it. Address every comment; amend your commits and force-push your branch rather than
   stacking "fix review" commits.
5. Once approved, a maintainer merges it. Your commits keep your authorship.

Do not change the version number or `packaging/changelog`: releases (version in `rog_flare2_core.py`, changelog,
packages, release notes) are made by a maintainer.

### Request for comments

To get feedback on a direction before writing the whole thing, open a pull request whose title starts with `[RFC]`,
based on the current code. Write down in the pull request what was concluded.

### Quality standards

The repository is written in **French**: comments, docstrings, documentation and commit messages. Code identifiers
may stay in English. If French is a barrier, write in English and a maintainer will translate — the content matters
more than the language.

Before opening a pull request (system packages used by the CI: `xvfb xdotool imagemagick lintian dbus python3-gi`):

```bash
python3 -m venv .venv
.venv/bin/pip install pillow numpy hidapi pynput python-xlib pytest ruff
.venv/bin/ruff check --select F,E9 --exclude polywollywin,rog_flare2_matrix_paint.py,parse_usbpcap.py .
dbus-run-session -- xvfb-run -a -s "-screen 0 1920x1080x24" .venv/bin/python -m pytest -q tests
packaging/build-deb.sh && lintian --fail-on error dist/*.deb
```

The tests never touch a real keyboard (`ANIMEMATRIX_FAUX_CLAVIER`, see `tests/conftest.py`); the interface tests
click for real with `xdotool` on a virtual display.

Your contribution must meet these standards:

- **One logical change per commit**, with a descriptive message (title ≤ 72 characters, then the why).
- **Every commit passes the test suite.** A fix or a new behaviour comes with a test that **fails without your
  change**; a test that cannot fail is not a test.
- **Nothing is sent to the keyboard without proof.** A new command or report must come from a USB capture of the
  official software, documented in [`docs/PROTOCOL.md`](docs/PROTOCOL.md) (method and tools:
  `parse_usbpcap.py`, `rog_flare2_replay_capture.py`). Never send guessed bytes: the keyboard has onboard memory and
  profiles, and a wrong frame can change them.
- **The daemon owns the keyboard.** The launcher asks it through `rog_flare2_ctl`; a tool that writes directly (the
  LED editor) first sends `release` to the daemon and gives the keyboard back with `resume`.
- **Tk is only touched from the main thread.** A worker thread hands its result over (`set_status`, a queue polled
  with `after()`), and a window is never destroyed from inside one of its own canvas bindings (`after_idle`).
- **Every user-facing text goes through `_()`** and into the catalogues: `locale/_cles.json` and a translation in
  every `locale/<code>.json`, then `.venv/bin/python tests/i18n_modele.py` regenerates `locale/_source.json`
  (`tests/test_i18n_docs.py` checks it all). Placeholders (`{name}`, `{n}`…) stay as is.
- **The README exists in 19 languages** (`README.md` and `docs/readme/`): a change to its anchors, links or commands
  is made in every translation; the tests compare them.
- **Third-party code keeps its origin and licence**: `polywollywin/` (MIT, see `polywollywin/ORIGINE.md`) and the
  original tools of the upstream project (see *Credits* in the README).
- **Comments explain why**, especially where a decision looks arbitrary.
- **No personal data** in tracked files: no home paths (`/home/<name>`), e-mail addresses, tokens or keyboard serial
  numbers; USB captures you share must not contain anything else.
- **Explain your pull request**: the reasoning behind each change and the testing done (distribution, X11 or
  Wayland, keyboard firmware if you tested on the hardware).
- **You answer for every line you submit**, whatever tools helped you write it.

### Developer Certificate of Origin

AniMe Matrix for Linux is released under the [MIT licence](LICENSE). To make sure every contribution is correctly
attributed and licensed, each commit must carry a `Signed-off-by` line, by which you agree to the Developer
Certificate of Origin 1.1 (<https://developercertificate.org/>):

```
Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the
    best of my knowledge, is covered under an appropriate open
    source license and I have the right under that license to
    submit that work with modifications, whether created in whole
    or in part by me, under the same open source license (unless
    I am permitted to submit under a different license), as
    indicated in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including
    all personal information I submit with it, including my
    sign-off) is maintained indefinitely and may be redistributed
    consistent with this project or the open source license(s)
    involved.
```

Use `git commit -s`. A stable pseudonym is accepted, as long as it identifies you consistently across your
contributions. Forgot it? `git commit --amend -s`.

---

## 🇫🇷 Français

### Les contributions sont les bienvenues

AniMe Matrix pour Linux pilote l'écran AniMe Matrix (312 mini-LED) et l'éclairage des touches du clavier ASUS ROG
Strix Flare II Animate, sans Armoury Crate ni Windows : lanceur, démon `animematrixd`, effets, paquets. Rapports de
bogue, captures USB du clavier, traductions, effets, idées et demandes de fusion sont les bienvenus.

- Avis rapide sur une idée ou un bogue : ouvrez un [ticket](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
- Problème de sécurité : n'ouvrez **pas** de ticket, suivez [`SECURITY.md`](SECURITY.md).
- Traductions : [`docs/TRADUIRE.md`](docs/TRADUIRE.md) (19 langues, catalogues JSON dans `locale/`).
- Un nouvel effet n'a pas besoin de demande de fusion : il peut vivre en extension, voir
  [`docs/EXTENSIONS.md`](docs/EXTENSIONS.md).

### Déroulement

Le projet suit le modèle « fork and pull ».

1. Dans votre fork, créez une branche au nom parlant.
2. Faites votre changement en respectant les [exigences de qualité](#exigences-de-qualité) ci-dessous.
3. Ouvrez une demande de fusion (pull request) vers `main`.
4. Une personne de l'équipe la relit. Répondez à chaque remarque ; modifiez vos commits et repoussez votre branche
   (push forcé) plutôt que d'empiler des commits « correction de relecture ».
5. Une fois acceptée, elle est fusionnée par l'équipe. Vos commits gardent leur auteur.

Ne changez ni le numéro de version ni `packaging/changelog` : les versions (numéro dans `rog_flare2_core.py`,
changelog, paquets, notes de version) sont faites par l'équipe.

### Demande de commentaires

Pour un avis sur une direction avant de tout écrire, ouvrez une demande de fusion dont le titre commence par `[RFC]`,
bâtie sur le code actuel. Notez dans la demande ce qui a été conclu.

### Exigences de qualité

Le dépôt est rédigé **en français** : commentaires, docstrings, documentation et messages de commit. Les
identifiants du code peuvent rester en anglais. Si le français vous bloque, écrivez en anglais : l'équipe traduira
— le fond compte plus que la langue.

Avant d'ouvrir une demande (paquets système utilisés par l'intégration continue :
`xvfb xdotool imagemagick lintian dbus python3-gi`) :

```bash
python3 -m venv .venv
.venv/bin/pip install pillow numpy hidapi pynput python-xlib pytest ruff
.venv/bin/ruff check --select F,E9 --exclude polywollywin,rog_flare2_matrix_paint.py,parse_usbpcap.py .
dbus-run-session -- xvfb-run -a -s "-screen 0 1920x1080x24" .venv/bin/python -m pytest -q tests
packaging/build-deb.sh && lintian --fail-on error dist/*.deb
```

Les tests ne touchent jamais un vrai clavier (`ANIMEMATRIX_FAUX_CLAVIER`, voir `tests/conftest.py`) ; les tests des
interfaces cliquent pour de vrai avec `xdotool` sur un affichage virtuel.

Votre contribution doit respecter ces règles :

- **Un changement logique par commit**, avec un message parlant (titre ≤ 72 caractères, puis le pourquoi).
- **Chaque commit passe la suite de tests.** Un correctif ou un comportement neuf arrive avec un test qui **échoue
  sans votre changement** ; un test qui ne peut pas échouer n'est pas un test.
- **Rien n'est envoyé au clavier sans preuve.** Une commande ou un rapport neuf vient d'une capture USB du logiciel
  officiel, documentée dans [`docs/PROTOCOL.md`](docs/PROTOCOL.md) (méthode et outils : `parse_usbpcap.py`,
  `rog_flare2_replay_capture.py`). N'envoyez jamais d'octets devinés : le clavier a une mémoire et des profils
  embarqués, et une trame fausse peut les modifier.
- **Le clavier appartient au démon.** Le lanceur passe par `rog_flare2_ctl` ; un outil qui écrit directement
  (l'éditeur de LED) envoie d'abord `release` au démon et lui rend le clavier par `resume`.
- **Tk n'est touché que depuis le fil principal.** Un fil de travail rend son résultat (`set_status`, file lue par
  `after()`), et une fenêtre n'est jamais détruite depuis une liaison de son propre canevas (`after_idle`).
- **Tout texte affiché passe par `_()`** et entre dans les catalogues : `locale/_cles.json` et une traduction dans
  chaque `locale/<code>.json`, puis `.venv/bin/python tests/i18n_modele.py` régénère `locale/_source.json`
  (`tests/test_i18n_docs.py` vérifie le tout). Les accolades (`{nom}`, `{n}`…) restent telles quelles.
- **Le README existe en 19 langues** (`README.md` et `docs/readme/`) : un changement de ses ancres, liens ou
  commandes se fait dans chaque traduction ; les tests les comparent.
- **Le code tiers garde son origine et sa licence** : `polywollywin/` (MIT, voir `polywollywin/ORIGINE.md`) et les
  outils d'origine du projet amont (voir *Crédits* dans le README).
- **Les commentaires expliquent le pourquoi**, surtout là où une décision paraît arbitraire.
- **Aucune donnée personnelle** dans les fichiers suivis : ni chemin personnel (`/home/<nom>`), ni courriel, ni
  jeton, ni numéro de série de clavier ; les captures USB partagées ne doivent rien contenir d'autre.
- **Expliquez votre demande** : la raison de chaque changement et les essais faits (distribution, X11 ou Wayland,
  micrologiciel du clavier si vous avez essayé sur le matériel).
- **Vous répondez de chaque ligne soumise**, quels que soient les outils qui vous ont aidé à l'écrire.

### Certificat d'origine du développeur

AniMe Matrix pour Linux est publié sous [licence MIT](LICENSE). Pour que chaque contribution soit correctement
attribuée et placée sous licence, chaque commit porte une ligne `Signed-off-by`, par laquelle vous acceptez le
Developer Certificate of Origin 1.1 (<https://developercertificate.org/>), reproduit en anglais dans la section
ci-dessus : ce texte fait foi dans sa langue d'origine.

Utilisez `git commit -s`. Un pseudonyme stable est accepté, pourvu qu'il vous identifie de façon constante d'une
contribution à l'autre. Oubli ? `git commit --amend -s`.
