"""Construit corpus/otiyot_rabbi_akiva.txt à partir de Wikisource en hébreu (CC BY-SA) :
אלפא ביתא דרבי עקיבא (= אותיות דרבי עקיבא), נוסח א et נוסח ב,
d'après l'édition de י״ד אייזנשטיין, אוצר מדרשים.

Usage : python3 build_wikisource.py <dossier de téléchargement> <dossier corpus de sortie>

Format de sortie, un paragraphe par ligne : « référence<TAB>texte » ;
le fichier .refs donne pour chaque ligne le lien vers la page de Wikisource.
"""
import sys, os, re, time, urllib.parse, urllib.request

UA = 'rosh-milin-builder/1.0 (https://github.com/eliahousmietanski-crypto/rosh-milin)'
PAGES = [('אלפא ביתא דרבי עקיבא נוסח א', 'נוסח א'), ('אלפא ביתא דרבי עקיבא נוסח ב', 'נוסח ב')]
GEM = 'אבגדהוזחטיכלמנסעפצקרשת'


def gem(n):
    s = ''
    for v, c in ((400, 'ת'), (300, 'ש'), (200, 'ר'), (100, 'ק')):
        while n >= v:
            s += c; n -= v
    if n == 15: return s + 'טו'
    if n == 16: return s + 'טז'
    return s + ('יכלמנסעפצ'[n // 10 - 1] if n >= 10 else '') + ('אבגדהוזחט'[n % 10 - 1] if n % 10 else '')


def fetch(dl, title):
    f = os.path.join(dl, title.replace(' ', '_') + '.wiki')
    if not os.path.exists(f):
        url = 'https://he.wikisource.org/w/index.php?title=' + urllib.parse.quote(title.replace(' ', '_')) + '&action=raw'
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        data = urllib.request.urlopen(req).read().decode()
        if data.lstrip().startswith('<!DOCTYPE'):
            raise SystemExit('Wikisource a refusé la demande (trop de demandes) : réessayer dans une minute.')
        open(f, 'w').write(data)
        time.sleep(3)
    return open(f).read()


def clean(t):
    t = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>', '', t, flags=re.S)
    t = re.sub(r'\{\{[^{}]*\}\}', '', t)
    t = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', t)
    t = re.sub(r"'{2,}", '', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def main(dl, outdir):
    os.makedirs(dl, exist_ok=True)
    out, refs = [], []
    for title, nusach in PAGES:
        part, letter, n = '', '', 0
        for block in re.split(r'\n\s*\n', fetch(dl, title)):
            for line in block.split('\n'):
                m = re.match(r'^(=+)\s*(.*?)\s*\1\s*$', line)
                if m:
                    head = clean(m.group(2))
                    if head.startswith('חלק'):
                        part, letter, n = head, '', 0
                    else:
                        letter, n = head, 0
                    block = block.replace(line, '')
            t = clean(block)
            if not t:
                continue
            n += 1
            ref = ', '.join(x for x in (nusach, part, letter and 'אות ' + letter, gem(n)) if x)
            out.append(ref + '\t' + t)
            refs.append('https://he.wikisource.org/wiki/' + title.replace(' ', '_') + ('#' + letter if letter else ''))
    fn = os.path.join(outdir, 'otiyot_rabbi_akiva.txt')
    open(fn, 'w').write('\n'.join(out) + '\n')
    open(fn[:-4] + '.refs', 'w').write('\n'.join(refs) + '\n')
    print(len(out), 'paragraphes', os.path.getsize(fn), 'octets', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
