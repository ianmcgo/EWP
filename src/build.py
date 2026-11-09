import json, os, sys

data = json.load(open('data.min.json'))
if os.path.exists('images.json'):
    imgs = json.load(open('images.json'))
    n = 0
    for f in data['factions']:
        for u in f['units']:
            url = imgs.get(f['id'], {}).get(u['id'])
            if url and url.startswith(('https://www.manticgames.com/', 'https://vault.manticgames.com/')):
                u['img'] = url
                n += 1
    print('images attached:', n)
html = open('app.html').read()
html = html.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
out = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
open(out, 'w').write(html)
print(out, len(html), 'bytes')
