# ראש מילין

Application pour smartphone qui explique un mot hébreu lettre par lettre selon le livre du Rav Kook (Londres, 1917) : lettres, lettres finales, couronnes, voyelles et signes de cantillation.

**Ouvrir l'application :** https://eliahousmietanski-crypto.github.io/rosh-milin/

Sur Android (Chrome) : ouvrir le lien, menu ⋮ → « Installer l'application » ou « Ajouter à l'écran d'accueil ». Après la première ouverture, tout fonctionne sans internet. Seul le bouton de synthèse demande une connexion.

## Contenu

| Fichier | Rôle |
|---|---|
| `index.html` | L'application |
| `search.js` | La recherche dans le תנ"ך, le זהר et les livres de Breslov, dans un fil à part pour que l'écran ne fige pas |
| `data.json` | Le texte du livre découpé par élément, et les résumés |
| `pages/` | Les 144 pages scannées |
| `sw.js` | Fonctionnement hors ligne (les textes, eux, sont gardés par `search.js`) |
| `source/rosh-milin.txt` | Le texte complet retranscrit, page par page |
| `tanakh.txt` | Le texte du תנ"ך (codex de Leningrad), un verset par ligne, pour trouver les occurrences d'un mot |
| `source/build_tanakh.py` | Fabrique `tanakh.txt` depuis les fichiers OSIS d'Open Scriptures |
| `corpus/` | Le זהר (avec זהר חדש et תיקוני זהר), le ספר יצירה (version du גר״א) et le commentaire du גר״א, le שערי אורה, les livres de רבי נחמן et de רבי נתן, le commentaire de la Torah de Hirsch : un paragraphe par ligne |
| `source/build_sefaria.py` | Fabrique `corpus/` depuis l'export public de Sefaria ; chaque `.refs` donne, ligne par ligne, la référence du passage pour le lien vers le texte original |
| `source/build_wikisource.py` | Fabrique `corpus/otiyot_rabbi_akiva.txt` depuis Wikisource |

Texte retranscrit depuis l'édition numérisée de hebrewbooks.org, avec les corrections de la page d'errata du livre. Les résumés en français sont une aide à la lecture et ne font pas partie du livre.

Le texte du תנ"ך vient du codex de Leningrad (Westminster Leningrad Codex, domaine public), dans l'édition d'Open Scriptures (https://github.com/openscriptures/morphhb, CC BY 4.0), qui indique aussi où finissent les lettres ajoutées devant les mots.

Le זהר, le זהר חדש, les תיקוני זהר et les livres de רבי נחמן (ליקוטי מוהר״ן, ספר המידות, סיפורי מעשיות, שיחות הר״ן) et de רבי נתן (ליקוטי הלכות, ליקוטי תפילות, ליקוטי עצות, חיי מוהר״ן, שבחי הר״ן) viennent de l'export public de Sefaria (https://github.com/Sefaria/Sefaria-Export). Les éditions numériques utilisées sont indiquées dans `corpus/index.json` ; Sefaria les donne comme domaine public, CC BY-NC ou de licence non précisée selon l'édition. Ces textes sont réservés à un usage non commercial.

Le ספר יצירה (version du גר״א, Varsovie 1884) et le commentaire du גר״א, le שערי אורה de Rabbi Yossef Gikatilla et le commentaire de la Torah du Rav Samson Raphaël Hirsch (original allemand de 1903, domaine public) viennent aussi de Sefaria.

Le midrash אותיות דרבי עקיבא (אלפא ביתא דרבי עקיבא, נוסח א et נוסח ב, d'après l'édition de J. D. Eisenstein, אוצר מדרשים) vient de Wikisource en hébreu (https://he.wikisource.org/wiki/אלפא_ביתא_דרבי_עקיבא), sous licence CC BY-SA.
