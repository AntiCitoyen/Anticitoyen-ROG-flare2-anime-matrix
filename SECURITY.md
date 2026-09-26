# Security policy / Politique de sécurité

## 🇬🇧 English

### Supported versions

Only the latest release receives security fixes. Please update first (*Settings → Check for updates*,
`sudo apt update && sudo apt upgrade`, or the [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) page) and check that the problem is still there.

| Version | Supported |
|---|---|
| latest release | ✅ |
| older releases | ❌ |

### Reporting a vulnerability

**Please do not open a public issue.** Use GitHub's private reporting instead:
[Report a vulnerability](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/security/advisories/new)
(tab *Security → Report a vulnerability*).

Please include the version, your distribution and desktop session (X11 or Wayland), the steps to
reproduce, and what an attacker could achieve. You can write in English or French.

What to expect: an acknowledgement within 7 days, an assessment within 14 days, and for a confirmed
issue a fixed release as soon as possible, published with a GitHub security advisory crediting you
(unless you prefer not to be named).

### Scope

In scope: everything in this repository, in particular the parts that accept input from other
programs or from the network:

- the daemon socket (`$XDG_RUNTIME_DIR/animematrix.sock`) and the optional local HTTP API
  (`animematrixd --http`, 127.0.0.1 only, refuses requests coming from web pages);
- the web remote (off by default; local network, token required, restricted set of commands);
- the built-in updater (SHA-256 checked, package verified again as root before installation);
- the animation library download, settings backup and restore, keyboard memory writing;
- the shell integration for long commands (`animematrix-fin.sh`) and the udev rules.

Out of scope: effect extensions you install yourself (a `.py` file in the extensions folder runs with
your rights, by design), physical access to the computer, and vulnerabilities in third-party software
(Python, hidapi, ffmpeg, the desktop environment…) — please report those upstream.

---

## 🇫🇷 Français

### Versions prises en charge

Seule la dernière version reçoit les correctifs de sécurité. Mettez d'abord à jour (*Réglages →
Rechercher les mises à jour*, `sudo apt update && sudo apt upgrade`, ou la page
[Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)) et vérifiez que le problème existe toujours.

| Version | Prise en charge |
|---|---|
| dernière version | ✅ |
| versions précédentes | ❌ |

### Signaler une faille

**Merci de ne pas ouvrir de ticket public.** Utilisez le signalement privé de GitHub :
[Signaler une faille](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/security/advisories/new)
(onglet *Security → Report a vulnerability*).

Indiquez la version, votre distribution et votre session (X11 ou Wayland), les étapes pour reproduire
et ce qu'un attaquant pourrait obtenir. En français ou en anglais.

Ce qui suit : un accusé de réception sous 7 jours, une évaluation sous 14 jours et, pour une faille
confirmée, une version corrigée dès que possible, publiée avec un avis de sécurité GitHub qui vous
cite (sauf si vous préférez rester anonyme).

### Périmètre

Dans le périmètre : tout ce dépôt, en particulier ce qui reçoit des données d'autres programmes ou du
réseau :

- le socket du démon (`$XDG_RUNTIME_DIR/animematrix.sock`) et l'API HTTP locale facultative
  (`animematrixd --http`, 127.0.0.1 seulement, refuse les requêtes venant de pages web) ;
- la télécommande web (désactivée par défaut ; réseau local, jeton obligatoire, commandes restreintes) ;
- la mise à jour intégrée (SHA-256 vérifié, paquet revérifié en root avant installation) ;
- le téléchargement de la bibliothèque d'animations, la sauvegarde et la restauration des réglages,
  l'écriture dans la mémoire du clavier ;
- l'intégration au terminal pour les commandes longues (`animematrix-fin.sh`) et les règles udev.

Hors périmètre : les extensions d'effets que vous installez vous-même (un fichier `.py` du dossier des
extensions s'exécute avec vos droits, c'est voulu), l'accès physique à l'ordinateur, et les failles
des logiciels tiers (Python, hidapi, ffmpeg, l'environnement de bureau…) — à signaler à leurs auteurs.
