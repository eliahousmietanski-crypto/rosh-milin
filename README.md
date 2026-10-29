# ראש מילין

Application pour smartphone qui explique un mot hébreu lettre par lettre selon le livre du Rav Kook (Londres, 1917) : lettres, lettres finales, couronnes, voyelles et signes de cantillation.

**Ouvrir l'application :** https://eliahousmietanski-crypto.github.io/rosh-milin/

Sur Android (Chrome) : ouvrir le lien, menu ⋮ → « Installer l'application » ou « Ajouter à l'écran d'accueil ». Après la première ouverture, tout fonctionne sans internet. Seul le bouton de synthèse demande une connexion.

## Contenu

| Fichier | Rôle |
|---|---|
| `index.html` | L'application |
| `data.json` | Le texte du livre découpé par élément, et les résumés |
| `pages/` | Les 144 pages scannées |
| `sw.js` | Fonctionnement hors ligne |
| `source/rosh-milin.txt` | Le texte complet retranscrit, page par page |
| `tanakh.txt` | Le texte du תנ"ך (codex de Leningrad), un verset par ligne, pour trouver les occurrences d'un mot |
| `source/build_tanakh.py` | Fabrique `tanakh.txt` depuis les fichiers OSIS d'Open Scriptures |
| `corpus/` | Le זהר, le זהר חדש, les תיקוני זהר et les livres de רבי נחמן et de רבי נתן, un paragraphe par ligne |
| `source/build_sefaria.py` | Fabrique `corpus/` depuis l'export public de Sefaria |

Texte retranscrit depuis l'édition numérisée de hebrewbooks.org, avec les corrections de la page d'errata du livre. Les résumés en français sont une aide à la lecture et ne font pas partie du livre.

Le texte du תנ"ך vient du codex de Leningrad (Westminster Leningrad Codex, domaine public), dans l'édition d'Open Scriptures (https://github.com/openscriptures/morphhb, CC BY 4.0), qui indique aussi où finissent les lettres ajoutées devant les mots.

Le זהר, le זהר חדש, les תיקוני זהר et les livres de רבי נחמן (ליקוטי מוהר״ן, ספר המידות, סיפורי מעשיות, שיחות הר״ן) et de רבי נתן (ליקוטי הלכות, ליקוטי תפילות, ליקוטי עצות, חיי מוהר״ן, שבחי הר״ן) viennent de l'export public de Sefaria (https://github.com/Sefaria/Sefaria-Export). Les éditions numériques utilisées sont indiquées dans `corpus/index.json` ; Sefaria les donne comme domaine public, CC BY-NC ou de licence non précisée selon l'édition. Ces textes sont réservés à un usage non commercial.
