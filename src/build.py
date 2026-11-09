import json, os, sys

data = json.load(open('data.min.json'))
if os.path.exists('images.json'):
    imgs = json.load(open('images.json'))
    notes = json.load(open('image_notes.json')) if os.path.exists('image_notes.json') else {}
    n = 0
    for f in data['factions']:
        for u in f['units']:
            url = imgs.get(f['id'], {}).get(u['id'])
            if url and url.startswith(('https://www.manticgames.com/', 'https://vault.manticgames.com/')):
                u['img'] = url
                note = notes.get(f['id'], {}).get(u['id'])
                if note:
                    u['imgNote'] = note
                n += 1
    print('images attached:', n)
html = open('app.html').read()
html = html.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
rules = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules.json')))
html = html.replace('__RULES__', json.dumps(rules, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
out = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
open(out, 'w').write(html)
print(out, len(html), 'bytes')
