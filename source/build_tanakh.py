"""Construit tanakh.txt à partir du codex de Leningrad (WLC, domaine public),
dans l'édition OSIS d'Open Scriptures : https://github.com/openscriptures/morphhb

Usage : python3 build_tanakh.py <dossier contenant Gen.xml, Exod.xml, …> > ../tanakh.txt

Format de sortie, une ligne par verset : « livre chapitre verset<TAB>texte ».
- Les mots sont séparés par une espace ; le מקף (־) est conservé collé.
- « / » sépare les lettres ajoutées devant le mot (ו, ה, ב, כ, ל, מ…) du mot lui-même.
- Un כתיב est écrit entre ( ), le קרי qui le suit entre [ ].
"""
import sys, os
import xml.etree.ElementTree as ET

BOOKS = ['Gen', 'Exod', 'Lev', 'Num', 'Deut', 'Josh', 'Judg', '1Sam', '2Sam', '1Kgs', '2Kgs',
         'Isa', 'Jer', 'Ezek', 'Hos', 'Joel', 'Amos', 'Obad', 'Jonah', 'Mic', 'Nah', 'Hab', 'Zeph',
         'Hag', 'Zech', 'Mal', 'Ps', 'Prov', 'Job', 'Song', 'Ruth', 'Lam', 'Eccl', 'Esth', 'Dan',
         'Ezra', 'Neh', '1Chr', '2Chr']
NS = '{http://www.bibletechnologies.net/2003/OSIS/namespace}'
PREFIX_CODES = {'C', 'R', 'Rd', 'Td', 'Ti'}  # conjonction, préposition, article, ה interrogatif


def word(w):
    """Texte du mot, avec « / » seulement entre les préfixes et le mot."""
    text = ''.join(w.itertext())
    parts = text.split('/')
    morph = w.get('morph', '')
    codes = morph[1:].split('/') if morph else []
    if len(codes) != len(parts):
        return text.replace('/', '')
    n = 0
    while n < len(parts) - 1 and codes[n] in PREFIX_CODES and codes[n + 1][:2] != 'Sp':
        n += 1
    return ''.join(parts[:n]) + ('/' if n else '') + ''.join(parts[n:])


def verse(v):
    out = []  # liste de mots ; un mot qui finit par ־ se colle au suivant
    for el in v:
        tag = el.tag[len(NS):]
        if tag == 'w':
            t = word(el)
            out.append('(' + t + ')' if el.get('type') == 'x-ketiv' else t)
        elif tag == 'seg':
            typ = el.get('type')
            if typ == 'x-maqqef' and out:
                out[-1] += '־'
            elif typ == 'x-paseq':
                out.append('׀')
            elif typ == 'x-sof-pasuq' and out:
                out[-1] += '׃'
            elif typ in ('x-large', 'x-small', 'x-suspended', 'x-reversednun'):
                if typ == 'x-reversednun':
                    continue
                out.append(''.join(el.itertext()))
        elif tag == 'note':
            for r in el.iter(NS + 'rdg'):
                if r.get('type') == 'x-qere':
                    out.append('[' + ' '.join(word(w) for w in r.iter(NS + 'w')) + ']')
    s = ''
    for t in out:
        s += t if (not s or s.endswith('־')) else ' ' + t
    return s


def main(d):
    for i, b in enumerate(BOOKS):
        root = ET.parse(os.path.join(d, b + '.xml')).getroot()
        for v in root.iter(NS + 'verse'):
            _, c, n = v.get('osisID').split('.')
            sys.stdout.write(f'{i} {c} {n}\t{verse(v)}\n')


if __name__ == '__main__':
    main(sys.argv[1])
