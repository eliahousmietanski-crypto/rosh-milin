"""Construit letters.json : pour chaque lettre, les passages des autres livres qui parlent
explicitement de cette lettre (pas seulement du mot qui s'écrit pareil).

Repères utilisés :
- אותיות דרבי עקיבא : toutes les sections rangées sous « אות X » ;
- ailleurs : le nom de la lettre écrit avec guillemets (בי״ת, חי״ת…), « אות X »,
  ou la forme araméenne du זהר « את X׳ » (sauf ה׳, qui est le nom de Dieu).

Usage : python3 build_letters.py <dossier corpus> > ../letters.json
"""
import sys, os, re, json

LETTERS = 'אבגדהוזחטיכלמנסעפצקרשת'
NAMES = {'א': 'אלף', 'ב': 'בית', 'ג': 'גימל', 'ד': 'דלת', 'ה': 'הא', 'ו': 'ויו|ואו', 'ז': 'זין', 'ח': 'חית',
         'ט': 'טית', 'י': 'יוד', 'כ': 'כף', 'ל': 'למד', 'מ': 'מם', 'נ': 'נון', 'ס': 'סמך', 'ע': 'עין',
         'פ': 'פא|פה', 'צ': 'צדי', 'ק': 'קוף', 'ר': 'ריש', 'ש': 'שין', 'ת': 'תיו|תו'}
# fichier -> (onglet de l'application, nom du livre, nombre de passages gardés par lettre)
BOOKS = [
    ('otiyot_rabbi_akiva', 'otiyot', 'אותיות דרבי עקיבא', 99),
    ('sefer_yetzirah', 'yetzirah', 'ספר יצירה', 4),
    ('gra_sefer_yetzirah', 'yetzirah', 'פירוש הגר״א', 4),
    ('zohar_1', 'zohar', 'זהר', 5), ('zohar_2', 'zohar', 'זהר', 3),
    ('zohar_chadash', 'zohar', 'זהר חדש', 4), ('tikkunei_zohar', 'zohar', 'תיקוני זהר', 4),
    ('shaarei_orah', 'shaarei', 'שערי אורה', 3),
    ('likutei_moharan', 'nachman', 'ליקוטי מוהר״ן', 4),
    ('likutei_halakhot_2', 'natan', 'ליקוטי הלכות', 2), ('likutei_halakhot_3', 'natan', 'ליקוטי הלכות', 2),
    ('likutei_halakhot_4', 'natan', 'ליקוטי הלכות', 2),
]
MARKS = re.compile(r'[֑-ׇ]')
Q = '["\'״׳]'


# « אות X » ne désigne la lettre que dans ces livres ; ailleurs (Breslov, זהר) c'est souvent un numéro de paragraphe
OT_BOOKS = {'sefer_yetzirah', 'gra_sefer_yetzirah', 'shaarei_orah'}


def patterns(l, ot):
    name = NAMES[l]
    alts = []
    for n in name.split('|'):
        alts.append(n[:-1] + Q + n[-1])           # בי״ת
    if ot:
        alts.append('ה?אות ' + l + '(?:' + Q + '|(?![א-ת]))')  # אות ב
    if l != 'ה':
        alts.append('את ' + l + "['׳]")             # את ב׳ (araméen du זהר)
    return re.compile('(?<![א-ת])(?:' + '|'.join(alts) + ')(?![א-ת])')


def excerpt(text, plain, m, size=420):
    # retrouve la position dans le texte avec voyelles : on compte les caractères non-signes
    want, i, k = m.start(), 0, 0
    while i < len(text) and k < want:
        if not MARKS.match(text[i]): k += 1
        i += 1
    a = max(0, i - size // 2)
    b = min(len(text), i + size)
    s = text[a:b]
    if a > 0: s = '…' + s.split(' ', 1)[-1]
    if b < len(text): s = s.rsplit(' ', 1)[0] + '…'
    return s


def main(d):
    out = {l: [] for l in LETTERS}
    for fname, src, he, cap in BOOKS:
        pats = {l: patterns(l, fname in OT_BOOKS) for l in LETTERS}
        lines = open(os.path.join(d, fname + '.txt')).read().split('\n')
        refs = open(os.path.join(d, fname + '.refs')).read().split('\n')
        found = {l: [] for l in LETTERS}
        for n, line in enumerate(lines):
            if '\t' not in line: continue
            ref, text = line.split('\t', 1)
            plain = MARKS.sub('', text)
            if fname == 'otiyot_rabbi_akiva':
                m = re.search(r'אות ([א-ת])', ref)
                if m and m.group(1) in found:
                    found[m.group(1)].append((99, ref, text, refs[n], text))   # texte entier : le midrash est rangé par lettre
                continue
            for l in LETTERS:
                ms = list(pats[l].finditer(plain))
                if ms:
                    found[l].append((len(ms), ref, excerpt(text, plain, ms[0]), refs[n], text))
        for l in LETTERS:
            # les passages qui parlent le plus de la lettre d'abord
            for score, ref, text, link, full in sorted(found[l], key=lambda x: -x[0])[:cap]:
                e = {'src': src, 'book': he, 'ref': ref, 'text': text, 'link': link}
                if full != text: e['full'] = full   # l'extrait est coupé : le paragraphe entier, pour « lire tout le passage »
                out[l].append(e)
    json.dump(out, sys.stdout, ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    main(sys.argv[1])
