import pdfplumber, json, re, sys
from collections import defaultdict

PDF = sys.argv[1] if len(sys.argv) > 1 else 'rb.pdf'
pdf = pdfplumber.open(PDF)

FACTIONS = [('Asterians', 68, 75), ('Enforcers', 76, 83), ('Forge Fathers', 84, 91), ('GCPS', 92, 99),
            ('Marauders', 100, 107), ('Nameless', 108, 115), ('Plague', 116, 123), ('Veer-Myn', 124, 129)]
CATS = {'troop': 'Troop', 'specialist': 'Specialist', 'support': 'Support', 'transport': 'Transport',
        'hq': 'HQ', 'super-heavy': 'Super-Heavy', 'superheavy': 'Super-Heavy'}


def words(p):
    return p.extract_words(x_tolerance=1.5, extra_attrs=['size', 'fontname'])


def font(w):
    return w['fontname'].split('+')[-1]


def lines_of(ws, tol=2.5):
    ws = sorted(ws, key=lambda w: (round(w['top']), w['x0']))
    out = []
    for w in ws:
        if out and abs(out[-1][0]['top'] - w['top']) <= tol:
            out[-1].append(w)
        else:
            out.append([w])
    return [sorted(l, key=lambda w: w['x0']) for l in out]


def txt(ws):
    return ' '.join(w['text'] for w in sorted(ws, key=lambda w: (round(w['top']), w['x0'])))


def tidy(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('“', '"').replace('”', '"').replace('’', "'")
    return s


def dice_colors(page, img_boxes):
    if not img_boxes:
        return []
    im = page.to_image(resolution=150).original.convert('RGB')
    sc = 150 / 72
    res = []
    for b in img_boxes:
        cx, cy = (b['x0'] + b['x1']) / 2 * sc, (b['top'] + b['bottom']) / 2 * sc
        r, g, bl = im.getpixel((int(cx), int(cy)))
        if r > 140 and r > g + 40 and bl < 90:
            res.append('Orange')
        elif g > r and g > bl and g > 100:
            res.append('Green')
        elif r < 90 and g < 90 and bl < 90:
            res.append('Black')
        else:
            res.append(f'#{r:02x}{g:02x}{bl:02x}')
    return res


def parse_card(page, ws, hdr, next_top, side_x0, side_x1):
    tx = [w for w in hdr if w['text'] == 'Type'][0]
    htx = [w for w in hdr if w['text'] == 'HT'][0]
    usx = [w for w in hdr if w['text'] == 'US'][0]
    ptx = [w for w in hdr if w['text'] == 'Pts'][0]
    top0 = min(w['top'] for w in hdr) - 30
    body = sorted([w for w in ws if top0 <= w['top'] < next_top], key=lambda w: (w['top'], w['x0']))
    sp = [w for w in body if w['text'] == 'SP' and font(w) == 'Arial-BoldMT' and w['top'] > hdr[0]['top']]
    sp_top = sp[0]['top'] if sp else hdr[0]['top'] + 45
    head = [w for w in body if w['top'] < sp_top - 1 and w not in hdr]
    name_ws = [w for w in head if font(w) == 'Arial-BoldMT' and round(w['size']) == 10]
    rest = [w for w in head if w not in name_ws and w['top'] > hdr[0]['top']]
    type_ws = [w for w in rest if (w['x0'] + w['x1']) / 2 < htx['x0'] - 2]
    ht = [w['text'] for w in rest if abs((w['x0'] + w['x1']) / 2 - (htx['x0'] + htx['x1']) / 2) < 10]
    us = [w['text'] for w in rest if abs((w['x0'] + w['x1']) / 2 - (usx['x0'] + usx['x1']) / 2) < 12]
    pts = [w['text'] for w in rest if abs((w['x0'] + w['x1']) / 2 - (ptx['x0'] + ptx['x1']) / 2) < 12]
    name = tidy(txt(name_ws))
    unique = '[U]' in name
    name = name.replace('[U]', '').strip()
    m = re.search(r'\((\d+)\)\s*$', name)
    bases = int(m.group(1)) if m else None
    if m:
        name = name[:m.start()].strip()
    ttxt = tidy(txt(type_ws))
    tm = re.match(r'(.*?)\s*\((.*)\)$', ttxt)
    utype, usub = (tm.group(1), tm.group(2)) if tm else (ttxt, '')
    utype, usub = utype.strip(), usub.strip()
    if utype == 'Command' and not usub:
        pass
    if utype.startswith('Command ') and not tm:
        usub = utype[8:]
        utype = 'Command'
    stats_hdr = [w for w in body if abs(w['top'] - sp_top) < 2]
    stat_vals = {}
    after = [w for w in body if sp_top + 5 < w['top'] < sp_top + 25]
    for h in stats_hdr:
        if h['text'] in ('SP', 'SH', 'AS', 'AR', 'SV'):
            c = (h['x0'] + h['x1']) / 2
            cand = [w for w in after if abs((w['x0'] + w['x1']) / 2 - c) < 15]
            stat_vals[h['text']] = cand[0]['text'] if cand else ''
    kw_hdr = [w for w in body if w['text'] == 'Keywords' and font(w) == 'Arial-BoldMT' and w['top'] > sp_top]
    wp_hdr = [w for w in body if w['text'] == 'Weapons' and font(w) == 'Arial-BoldMT' and w['top'] > sp_top]
    kw_top = kw_hdr[0]['top'] if kw_hdr else sp_top + 30
    wp_top = wp_hdr[0]['top'] if wp_hdr else next_top
    kw_ws = [w for w in body if kw_top + 4 < w['top'] < wp_top - 2]
    kw_text = tidy(txt(kw_ws))
    tact = [w for w in kw_ws if w['text'].startswith('Tactician')]
    tact_colors = []
    if tact:
        t = tact[0]
        boxes = [i for i in page.images if abs((i['top'] + i['bottom']) / 2 - (t['top'] + t['bottom']) / 2) < 6
                 and t['x1'] - 2 < i['x0'] < t['x1'] + 60 and i['x1'] - i['x0'] < 15]
        boxes.sort(key=lambda b: b['x0'])
        tact_colors = dice_colors(page, boxes)
    keywords = split_kw(kw_text.replace('Reslience', 'Resilience'))
    if tact:
        keywords = [('Tactician (' + ', '.join(tact_colors) + ')') if k.startswith('Tactician') else k for k in keywords]
    opt = [w for w in body if w['text'] == 'Options' and font(w) == 'Arial-BoldMT' and w['top'] > wp_top]
    sr = [w for w in body if w['text'] == 'Special' and font(w) == 'Arial-BoldMT' and w['top'] > wp_top]
    wend = min([o['top'] for o in opt] + [s['top'] for s in sr] + [next_top])
    weapons = []
    if wp_hdr:
        wh = [w for w in body if abs(w['top'] - wp_top) < 2]
        rx = [w for w in wh if w['text'] == 'Range'][0]
        ax = [w for w in wh if w['text'] == 'ADice'][0]
        kx = [w for w in wh if w['text'] == 'Keywords'][0]
        rows = [w for w in body if wp_top + 4 < w['top'] < wend - 1]
        rows = [w for w in rows if not (round(w['size']) >= 10 and font(w) == 'ArialMT' and re.fullmatch(r'\d+', w['text']))]
        rcol = [w for w in rows if rx['x0'] - 6 <= (w['x0'] + w['x1']) / 2 <= rx['x1'] + 6]
        acol = [w for w in rows if ax['x0'] - 6 <= (w['x0'] + w['x1']) / 2 <= ax['x1'] + 6]
        kcol = [w for w in rows if w['x0'] >= ax['x1'] + 4 or (w['x0'] + w['x1']) / 2 > kx['x0'] - 8]
        kcol = [w for w in kcol if w not in rcol and w not in acol]
        ncol = [w for w in rows if w not in rcol and w not in acol and w not in kcol]
        rx_re = re.compile(r'^(A|-|\d+(-\d+)?)$')
        bad = [w for w in rcol if not rx_re.match(w['text'])]
        rcol = [w for w in rcol if w not in bad]
        ncol = ncol + bad
        anchors = sorted(rcol, key=lambda w: w['top'])
        groups = [{'y': (a['top'] + a['bottom']) / 2, 'range': a['text'], 'adice': '', 'name': [], 'kw': []} for a in anchors]
        for w in acol:
            y = (w['top'] + w['bottom']) / 2
            g = min(groups, key=lambda g: abs(g['y'] - y))
            g['adice'] = w['text']
        headers = []
        for ln in lines_of(ncol):
            y = sum((w['top'] + w['bottom']) / 2 for w in ln) / len(ln)
            g = min(groups, key=lambda g: abs(g['y'] - y)) if groups else None
            if g is None or abs(g['y'] - y) > 7.5:
                headers.append((y, tidy(txt(ln))))
            else:
                g['name'].append((y, ln))
        prev_g, prev_t = None, ''
        for ln in lines_of(kcol):
            y = sum((w['top'] + w['bottom']) / 2 for w in ln) / len(ln)
            g = min(groups, key=lambda g: abs(g['y'] - y))
            if prev_g is not None and prev_t.endswith(',') and g is not prev_g:
                g = prev_g
            g['kw'].append((y, ln))
            prev_g, prev_t = g, txt(ln).strip()
        for g in groups:
            nm = tidy(' '.join(txt(l) for _, l in sorted(g['name'], key=lambda t: t[0])))
            kws = tidy(' '.join(txt(l) for _, l in sorted(g['kw'], key=lambda t: t[0])))
            sub = None
            if nm.startswith('•'):
                nm = nm.lstrip('• ').strip()
                hs = [h for h in headers if h[0] < g['y']]
                sub = hs[-1][1] if hs else None
            choice = nm.endswith('*')
            nm = nm.rstrip('*').strip()
            weapons.append({'name': nm, 'group': sub, 'choose': choice, 'range': g['range'], 'adice': g['adice'],
                            'kw': '' if kws == '-' else kws})
    options = []
    if opt:
        o_end = min([s['top'] for s in sr if s['top'] > opt[0]['top']] + [next_top])
        ows = [w for w in body if opt[0]['top'] + 4 < w['top'] < o_end - 1
               and not (round(w['size']) >= 10 and re.fullmatch(r'\d+', w['text']))]
        for ln in lines_of(ows):
            t = tidy(txt(ln))
            om = re.search(r'single (.+?) as a Command Transport for \+(\d+)\s*pts', t)
            options.append({'text': t, 'pts': int(om.group(2)) if om else int((re.search(r'\+(\d+)', t) or [0, 0])[1]),
                            'transport': om.group(1) if om else None})
    rules = []
    if sr:
        rws = [w for w in body if sr[0]['top'] + 6 < w['top'] < next_top - 1
               and not (round(w['size']) >= 10 and font(w) == 'ArialMT' and re.fullmatch(r'\d+', w['text']))]
        cur = None
        for ln in lines_of(rws):
            bold = [w for w in ln if 'Bold' in font(w)]
            if bold and ln[0] in bold and bold[-1]['text'].endswith(':'):
                bi = ln.index(bold[-1])
                cur = {'name': tidy(txt(ln[:bi + 1])).rstrip(':'), 'text': tidy(txt(ln[bi + 1:]))}
                rules.append(cur)
            elif cur:
                cur['text'] = tidy(cur['text'] + ' ' + txt(ln))
            else:
                cur = {'name': '', 'text': tidy(txt(ln))}
                rules.append(cur)
    return {'name': name, 'bases': bases, 'unique': unique, 'type': utype, 'sub': usub,
            'ht': ht[0] if ht else '', 'us': us[0] if us else '', 'pts': int(pts[0]) if pts and pts[0].isdigit() else None,
            'stats': stat_vals, 'keywords': keywords, 'weapons': weapons, 'options': options, 'rules': rules}


def split_kw(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([':
            depth += 1
        if ch in ')]':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip() and cur.strip() != '-':
        out.append(cur.strip())
    return [k for k in out if k]


def faction_header(p):
    ws = words(p)
    d = {}
    sr = [w for w in ws if w['text'] == 'RULE' and font(w) == 'Arial-BoldMT']
    nerve = [w for w in ws if round(w['size']) == 20 and font(w) == 'Arial-BoldMT']
    d['nerve'] = nerve[0]['text'] if nerve else ''
    so = [w for w in ws if w['text'] == 'Orders' and round(w['size']) == 12]
    so_top = so[0]['top'] if so else 999
    rule_ws = [w for w in ws if sr and sr[0]['top'] + 4 < w['top'] < so_top - 2 and w['x0'] < 495]
    rls = []
    cur = None
    for ln in lines_of(rule_ws):
        if all(font(w) == 'Arial-BoldItalicMT' for w in ln):
            cur = {'name': tidy(txt(ln)), 'text': ''}
            rls.append(cur)
        elif cur:
            cur['text'] = tidy(cur['text'] + ' ' + txt(ln))
    d['rules'] = rls
    hdr = [w for w in ws if w['top'] > so_top and w['text'] in ('Name', 'Cost', 'When?', 'Effect') and font(w) == 'Arial-BoldMT']
    orders = []
    if len(hdr) >= 4:
        hy = hdr[0]['top']
        cx = {w['text']: w for w in hdr}
        card = [w for w in ws if w['text'] == 'Type' and font(w) == 'Arial-BoldMT' and w['top'] > hy]
        cats = [w for w in ws if font(w) == 'ASTERA' and round(w['size']) == 20 and w['top'] > hy]
        end = min([w['top'] for w in card] + [w['top'] for w in cats] + [p.height - 50]) - 2
        tw = [w for w in ws if hy + 5 < w['top'] < end]
        cost_l = cx['Cost']['x0'] - 12
        when_l = cx['When?']['x0'] - 30
        eff_l = cx['Effect']['x0'] - 140
        anchors = sorted([w for w in tw if cost_l <= w['x0'] < when_l and re.fullmatch(r'[\dX]+\+?(\(\d+\))?', w['text'])], key=lambda w: w['top'])
        ys = [(a['top'] + a['bottom']) / 2 for a in anchors]
        bounds = [hy] + [(ys[i] + ys[i + 1]) / 2 for i in range(len(ys) - 1)] + [end]
        for i, a in enumerate(anchors):
            seg = [w for w in tw if bounds[i] <= (w['top'] + w['bottom']) / 2 < bounds[i + 1]]
            nm = [w for w in seg if w['x0'] < cost_l]
            wh = [w for w in seg if when_l <= w['x0'] and w['x1'] < cx['Effect']['x0'] - 125 + 30 and w['x0'] < eff_l + 0]
            ef = [w for w in seg if w['x0'] >= eff_l]
            wh = [w for w in seg if when_l <= w['x0'] < eff_l]
            orders.append({'name': tidy(txt(nm)), 'cost': a['text'], 'when': tidy(txt(wh)), 'effect': tidy(txt(ef))})
    d['orders'] = orders
    return d


def parse_faction(name, p0, p1):
    cards = []
    cat_marks = []
    for pi in range(p0, p1 + 1):
        p = pdf.pages[pi]
        ws = words(p)
        for ln in lines_of([w for w in ws if font(w) == 'ASTERA' and round(w['size']) == 20]):
            key = re.sub(r'[\s]', '', txt(ln)).lower()
            if key in CATS:
                cat_marks.append((pi, ln[0]['top'], CATS[key]))
        mid = p.width / 2
        for side in (0, 1):
            x0, x1 = (0, mid) if side == 0 else (mid, p.width)
            sws = [w for w in ws if x0 <= (w['x0'] + w['x1']) / 2 < x1]
            hdrs = []
            for ln in lines_of(sws):
                t = [w['text'] for w in ln]
                if t[:4] == ['Type', 'HT', 'US', 'Pts']:
                    hdrs.append(ln)
            for i, h in enumerate(hdrs):
                nt = hdrs[i + 1][0]['top'] - 30 if i + 1 < len(hdrs) else p.height - 45
                cm = [c for c in cat_marks if c[0] == pi and h[0]['top'] - 30 < c[1] < nt and c[1] > h[0]['top']]
                if cm:
                    nt = min(nt, cm[0][1] - 2)
                c = parse_card(p, sws, h, nt, x0, x1)
                c['_pos'] = (pi, h[0]['top'], side)
                cards.append(c)
    cards.sort(key=lambda c: c['_pos'])
    for c in cards:
        pi, top, _ = c['_pos']
        prev = [m for m in cat_marks if (m[0], m[1]) < (pi, top)]
        c['cat'] = prev[-1][2] if prev else '?'
        del c['_pos']
    hdr = faction_header(pdf.pages[p0])
    return {'name': name, **hdr, 'units': cards}


def parse_glossary():
    g = []
    for pi in range(46, 51):
        p = pdf.pages[pi]
        ws = [w for w in words(p) if 40 < w['top'] < p.height - 45 and font(w) not in ('ASTERA',)]
        mid = p.width / 2
        for side in (0, 1):
            sws = [w for w in ws if (w['x0'] < mid) == (side == 0)]
            cur = None
            for ln in lines_of(sws):
                if all(font(w) == 'Arial-BoldMT' and round(w['size']) == 12 for w in ln):
                    cur = {'name': tidy(txt(ln)), 'text': ''}
                    g.append(cur)
                elif cur:
                    cur['text'] = tidy(cur['text'] + ' ' + txt(ln))
    return g


data = {'factions': [parse_faction(*f) for f in FACTIONS], 'glossary': parse_glossary()}
json.dump(data, open('data.json', 'w'), indent=1, ensure_ascii=False)
for f in data['factions']:
    print(f['name'], f['nerve'], len(f['units']), [r['name'] for r in f['rules']], [o['name'] for o in f['orders']])
print('glossary', len(data['glossary']))
