"""Construit tanakh_fr.txt : la traduction française de la Bible du Rabbinat (1899, sous la
direction du grand-rabbin Zadoc Kahn, domaine public), d'après l'export public de Sefaria
(version « Bible du Rabbinat 1899 [fr] »), verset par verset, avec la même numérotation que tanakh.txt.

Usage : python3 build_tanakh_fr.py <dossier des 39 fichiers 00.json … 38.json> > ../tanakh_fr.txt
"""
import sys, os, re, json


def clean(t):
    t = re.sub(r'<sup[^>]*>.*?</sup>|<i class="footnote">.*?</i>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def main(d):
    for b in range(39):
        text = json.load(open(os.path.join(d, '%02d.json' % b)))['text']
        for c, ch in enumerate(text):
            for v, verse in enumerate(ch):
                t = clean(verse) if isinstance(verse, str) else ''
                if t:
                    sys.stdout.write(f'{b} {c + 1} {v + 1}\t{t}\n')


if __name__ == '__main__':
    main(sys.argv[1])
