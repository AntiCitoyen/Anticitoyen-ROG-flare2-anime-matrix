# Recherche : animations enregistrées dans le clavier

**Objectif** : que l'écran AniMe Matrix affiche une animation **sans logiciel sur le PC** (PC éteint, autre système), comme le permet Armoury Crate sous Windows en l'enregistrant dans le clavier.

**Statut** : recherche. Aucune commande inconnue n'est envoyée au clavier par ce projet.

## Ce que montrent les captures du dépôt

Analyse de `clock.cap`, `fill.cap` et `gif.cap` avec `parse_usbpcap.py` :

| Endpoint | Sens | Contenu | Rôle |
|---|---|---|---|
| `0x07` | hôte → clavier | 1024 octets `60 81 00 00` + 312 LED | trame d'affichage (seul type de commande vu) |
| `0x86` | clavier → hôte | 1024 octets `60 81 …` identiques | le clavier renvoie chaque trame (accusé de réception probable) |
| `0x81`, `0x84` | clavier → hôte | 8 et 21 octets | rapports de touches (clavier, touches multimédia) |
| `0x00`, `0x80` | contrôle | descripteurs USB | énumération |

**Aucune commande d'enregistrement** n'apparaît : ces captures ne contiennent que de l'affichage piloté par le PC. L'enregistrement dans le clavier passe par une autre action d'Armoury Crate, qu'il faut capturer.

## Autres sources

- **PolyWollyWin** (`transport.py`) documente une commande de **luminosité matérielle** : `60 a8 81 <niveau 0-3> ff` (même préfixe `0x60`). C'est un indice : les commandes du clavier semblent être de la forme `60 <commande> …`. Elle n'a pas été vérifiée par ce projet.
- Le **micrologiciel** annoncé par le clavier est `bcdDevice 3.14` (OpenRGB : version 03.00.14).

## Procédure de capture sûre (à faire sous Windows)

1. Installer **USBPcap** (fourni avec Wireshark) et **Armoury Crate**.
2. Démarrer la capture sur le concentrateur du clavier (`0b05:19fc`).
3. Dans Armoury Crate, créer une animation **très simple** (une seule LED allumée), puis l'**appliquer et l'enregistrer dans l'appareil**.
4. Arrêter la capture juste après, sans rien toucher d'autre.
5. Débrancher et rebrancher le clavier sur un PC **sans** Armoury Crate : noter si l'animation revient.
6. Déposer le fichier `.pcap` (ou `.cap`) dans un ticket du projet.

## Analyse prévue

- Lister toutes les commandes autres que `60 81` : `parse_usbpcap.py fichier.cap` (en-têtes et longueurs par endpoint).
- Identifier : début de transfert, blocs de données (probablement des trames de 312 octets), fin et validation.
- Comparer deux captures (animations différentes) pour séparer en-têtes et données.

## Règles de sécurité

- **Aucune trame inconnue** n'est rejouée sur le clavier sans l'accord explicite de son propriétaire, au moment de l'envoi.
- Les anciennes familles de protocole (`0x5E …` des portables, `0xEC …`) **ne sont pas** celles du clavier : ne jamais les envoyer (voir `docs/PROTOCOL.md`).
- En cas de blocage : débrancher et rebrancher ; sinon maintenir **Fn + Échap** 10 à 15 secondes.
