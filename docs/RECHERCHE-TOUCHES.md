# Recherche : profils et requêtes de l'interface des touches (64 octets)

**Statut** : recherche. Rien de ce qui suit n'est envoyé au clavier par le projet ; chaque essai demande l'accord
explicite du propriétaire du clavier, au moment de l'envoi.

## Ce qui est établi
- Interface 1 (usage page `0xFF00`), rapports de 64 octets : couleurs par touche `c0 81`, effets matériels
  `51 2C mode 00 vitesse luminosité …` (luminosité RGB globale = 5 crans, déjà gérée par `rog_flare2_rgb.py`),
  enregistrement `50 55`.
- Six profils en mémoire (1 à 5 personnalisables, 6 = défaut), bascule manuelle **Fn + 1 … 6** (caps.json,
  `profileHotKey`). Armoury Crate range les réglages par profil (`EffectInfomation_Profile1..6.xml`,
  `PUT …/matrix {profileID, …}`).
- Requêtes vues pendant la capture 06 (ouverture de la page du clavier), réponses sur 0x82 :
  | Envoi | Réponse | Sens |
  |---|---|---|
  | `12 00` | `12 00 00 00 14 00 03 00 06 04 06 04 …` | version du micrologiciel (octets 6, 5, 4 → 03.00.14), documenté par OpenRGB |
  | `12 12` | `12 12 00 00 02 05 …` | disposition du clavier (octets 4 et 5), documenté par OpenRGB |
  | `43 00` | `43 00 …` (écho) | inconnu ; `AacXA07::SetFunction` 0x04 envoie `43 <0/1>` (« bascule ») |

## Hypothèses (binaire `AacKbHal`, non vérifiées)
| Trame | Hypothèse |
|---|---|
| `51 00 00 00 p` | choisir le profil actif `p` (ID HAL 0x06, groupe « profils / réglages ») |
| `51 31 00 00 p` | appliquer le profil `p` après écriture de `HKLM\…\ArmouryHttp\6652` (ID HAL 0x14) |
| `50 40 00 00 01`, `50 40`, `50 11` | réglages génériques ASUS (sens inconnu) |
| `43 <0/1>` | bascule inconnue (mode jeu / verrouillage Windows ?) |

## Protocole d'essai proposé (à faire valider avant tout envoi)
1. **Lectures seules** `12 00` puis `12 12` : afficher la version du micrologiciel et la disposition dans
   `animematrix-ctl infos`. Risque nul attendu (requêtes documentées, envoyées par Armoury Crate à chaque
   ouverture de la page du clavier).
2. **Profil** : relever d'abord à la main le profil actif (Fn + 6 pour partir du profil par défaut), puis envoyer
   `51 00 00 00 01` une seule fois et regarder si l'éclairage passe au profil 1 ; retour par Fn + 6. **Jamais**
   `50 55` (enregistrement) pendant ces essais.
3. `43 00` / `43 01` seulement si 1 et 2 n'ont rien cassé, en notant ce qui change (touche Windows, Fn…).
