"""Construit les fichiers de corpus/ à partir de l'export public de Sefaria :
https://storage.googleapis.com/sefaria-export/json/<catégorie>/<livre>/Hebrew/merged.json

Usage : python3 build_sefaria.py <dossier de téléchargement> <dossier corpus de sortie>
Les fichiers JSON manquants sont téléchargés dans le dossier de téléchargement.

Format de sortie, un paragraphe par ligne : « référence<TAB>texte ».
"""
import sys, os, re, json, urllib.parse, urllib.request

BASE = 'https://storage.googleapis.com/sefaria-export/json/'
# fichier de sortie -> (chemin Sefaria, nom affiché[, version à prendre au lieu de Hebrew/merged.json])
BOOKS = [
    ('zohar', 'Kabbalah/Zohar/Zohar', 'זהר'),
    ('zohar_chadash', 'Kabbalah/Zohar/Zohar Chadash', 'זהר חדש'),
    ('tikkunei_zohar', 'Kabbalah/Zohar/Tikkunei Zohar', 'תיקוני זהר'),
    ('likutei_moharan', 'Chasidut/Breslov/Likutei Moharan', 'ליקוטי מוהר״ן'),
    ('sefer_hamidot', 'Chasidut/Breslov/Sefer HaMiddot', 'ספר המידות'),
    ('sipurei_maasiyot', 'Chasidut/Breslov/Sippurei Maasiyot', 'סיפורי מעשיות'),
    ('sichot_haran', 'Chasidut/Breslov/Sichot HaRan', 'שיחות הר״ן'),
    ('shivchei_haran', 'Chasidut/Breslov/Shivchei HaRan', 'שבחי הר״ן'),
    ('chayei_moharan', 'Chasidut/Breslov/Chayei Moharan', 'חיי מוהר״ן'),
    ('likutei_halakhot', 'Chasidut/Breslov/Likutei Halakhot', 'ליקוטי הלכות'),
    ('likutei_tefilot', 'Chasidut/Breslov/Likutei Tefilot', 'ליקוטי תפילות'),
    ('likutei_etzot', 'Chasidut/Breslov/Likkutei Etzot', 'ליקוטי עצות'),
    # uniquement la version du גר״א, édition de Varsovie 1884 (pas la version de Kaplan ni les autres)
    ('sefer_yetzirah', 'Kabbalah/Sefer Yetzirah/Sefer Yetzirah Gra Version', 'ספר יצירה',
     'Hebrew/Sefer Yetzirah, Warsaw 1884.json'),
    ('gra_sefer_yetzirah', 'Kabbalah/Sefer Yetzirah/Commentary/HaGra on Sefer Yetzirah Gra Version', 'פירוש הגר״א'),
    ('shaarei_orah', "Kabbalah/Other Kabbalah Works/Sha'arei Orah", 'שערי אורה'),
    # l'original allemand de 1903 (domaine public) : les mots hébreux y sont en lettres hébraïques
    ('hirsch', 'Tanakh/Acharonim on Tanakh/Rav Hirsch on Torah', 'רש״ר הירש',
     'English/Der Pentateuch. Übersetzt und erläutert von Samson Raphael Hirsch, 1903 [de].json'),
]
SPLIT_AT = 12_000_000  # octets : un fichier plus gros est coupé à la première division du livre


def gem(n):
    s = ''
    for v, c in ((400, 'ת'), (300, 'ש'), (200, 'ר'), (100, 'ק')):
        while n >= v:
            s += c; n -= v
    if n == 15: return s + 'טו'
    if n == 16: return s + 'טז'
    return s + ('יכלמנסעפצ'[n // 10 - 1] if n >= 10 else '') + ('אבגדהוזחט'[n % 10 - 1] if n % 10 else '')


def daf(i):
    return gem(i // 2 + 1) + (' ע״א' if i % 2 == 0 else ' ע״ב')


VILNA = re.compile(r'<i data-overlay="Vilna Pages" data-value="(\d+)([ab])"></i>')


def clean(t):
    t = re.sub(r'<img[^>]*>', '', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = t.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', t).strip()


def walk(text, path, nums, out, talmud, state):
    """text : liste imbriquée ; nums : indices des niveaux déjà traversés."""
    if isinstance(text, str):
        m = VILNA.findall(text)
        page = state.get('page')
        t = clean(text)
        if m:
            if VILNA.match(text.lstrip()):  # le paragraphe commence une nouvelle page
                page = gem(int(m[0][0])) + (' ע״א' if m[0][1] == 'a' else ' ע״ב')
            state['page'] = gem(int(m[-1][0])) + (' ע״א' if m[-1][1] == 'a' else ' ע״ב')
            page = page or state['page']
        if not t:
            return
        ref = ', '.join(p for p in path if p)
        if nums:
            first = daf(nums[0]) if talmud else gem(nums[0] + 1)
            ref += (', ' if ref else '') + ' '.join([first] + [gem(n + 1) for n in nums[1:]])
        if page:
            ref += f' (דף {page})'
        out.append(ref + '\t' + t)
        return
    for i, x in enumerate(text or []):
        walk(x, path, nums + [i], out, talmud, state)


def node(schema, text, path, out, talmud, state):
    if schema and schema.get('nodes'):
        for n in schema['nodes']:
            key = n.get('key') or n.get('enTitle') or ''
            sub = text.get(key, text.get('', [])) if isinstance(text, dict) else []
            node(n, sub, path + [n.get('heTitle', '')], out, talmud, state)
    else:
        walk(text, path, [], out, talmud, state)


def load(dl, sefpath, version='Hebrew/merged.json'):
    f = os.path.join(dl, (sefpath + '/' + version).replace('/', '_'))
    if not os.path.exists(f):
        urllib.request.urlretrieve(BASE + urllib.parse.quote(sefpath + '/' + version), f)
    return json.load(open(f))


def main(dl, outdir):
    os.makedirs(outdir, exist_ok=True)
    index = []
    for name, sefpath, he, *version in BOOKS:
        d = load(dl, sefpath, *version)
        talmud = (d.get('sectionNames') or [''])[0] == 'Daf'
        schema = d.get('schema')
        parts = []  # (suffixe, lignes)
        if schema and schema.get('nodes'):
            for n in schema['nodes']:
                out = []
                key = n.get('key') or n.get('enTitle') or ''
                node(n, d['text'].get(key, []), [n.get('heTitle', '')], out, talmud, {})
                parts.append(out)
        else:
            out = []
            walk(d['text'], [], [], out, talmud, {})
            parts.append(out)
        # regroupe les divisions en fichiers de taille raisonnable
        files, cur, size = [], [], 0
        for p in parts:
            s = sum(len(l.encode()) + 1 for l in p)
            if cur and size + s > SPLIT_AT:
                files.append(cur); cur, size = [], 0
            cur += p; size += s
        files.append(cur)
        names = []
        for i, lines in enumerate(files):
            fn = name + (f'_{i + 1}' if len(files) > 1 else '') + '.txt'
            with open(os.path.join(outdir, fn), 'w') as fh:
                fh.write('\n'.join(lines) + '\n')
            names.append(fn)
        index.append({'id': name, 'he': he, 'files': names,
                      'source': d.get('versions') or [[d.get('versionTitle'), d.get('versionSource')]]})
        print(name, [os.path.getsize(os.path.join(outdir, n)) for n in names], file=sys.stderr)
    json.dump(index, open(os.path.join(outdir, 'index.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
