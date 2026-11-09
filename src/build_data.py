import json, re

d = json.load(open('data.json'))

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

out = {'factions': [], 'glossary': [], 'stratagems': []}
for f in d['factions']:
    fid = slug(f['name'])
    units = []
    seen = {}
    for u in f['units']:
        uid = slug(u['name'])
        if uid in seen:
            uid = uid + '-' + slug(u['cat'])
        seen[uid] = 1
        kws = [k.replace('Anti-grav', 'Anti-Grav') for k in u['keywords']]
        ws = []
        for w in u['weapons']:
            kw = w['kw'].replace('Primary Weapon Vicious', 'Primary Weapon, Vicious').replace('Indirect Only', 'Indirect (only)')
            ws.append([w['group'] or '', w['name'], w['range'], w['adice'], kw, 1 if w['choose'] else 0])
        cat = u['cat']
        role = cat
        if cat == 'Super-Heavy':
            role = 'Super-Heavy'
        ent = {'id': uid, 'n': u['name'], 'c': cat, 'b': u['bases'], 'u': 1 if u['unique'] else 0,
               't': u['type'], 'st': u['sub'], 'ht': u['ht'], 'us': u['us'], 'p': u['pts'],
               's': [u['stats'].get(k, '') for k in ('SP', 'SH', 'AS', 'AR', 'SV')], 'k': kws, 'w': ws}
        cmd_tr = [o for o in u['options'] if o['transport']]
        if cmd_tr:
            ent['ct'] = {'name': cmd_tr[0]['transport'], 'p': cmd_tr[0]['pts']}
        if u['rules']:
            ent['r'] = [[r['name'], r['text']] for r in u['rules']]
        units.append(ent)
    out['factions'].append({'id': fid, 'n': f['name'], 'nerve': f['nerve'],
                            'rules': [[r['name'], r['text']] for r in f['rules']],
                            'orders': [[o['name'], o['cost'], o['when'], o['effect']] for o in f['orders']],
                            'units': units})
ERR = []
def unit(fid, uid):
    f = next(x for x in out['factions'] if x['id'] == fid)
    return next(u for u in f['units'] if u['id'] == uid)
def mark(u, note):
    u.setdefault('e', []).append(note)
def weap(u, name):
    return next(w for w in u['w'] if w[1] == name)

u = unit('asterians', 'wraith'); weap(u, 'Noh Blasters')[1] = 'Light Plasma Cannon'; mark(u, 'Weapon renamed from Noh Blasters to Light Plasma Cannon')
u = unit('enforcers', 'lieutenant'); weap(u, 'Genling 45 Laser Rifles')[4] = ''; u['p'] = 35; mark(u, 'Sustained Attack removed from Genling 45 Laser Rifles; cost 40 → 35')
u = unit('forge-fathers', 'brokkr'); u['p'] = 185; mark(u, 'Cost 235 → 185')
u = unit('forge-fathers', 'hammerfist-drop-troopers'); u['k'] = sorted(u['k'] + ['Anti-Grav']); mark(u, 'Anti-Grav keyword added')
u = unit('forge-fathers', 'nidavellir-drop-fortress'); u['k'] = ['Quick-fix (All Types)' if k.startswith('Quick Fix') else k for k in u['k']]; mark(u, 'Quick Fix corrected to Quick-fix (All Types)')
u = unit('gcps', 'rangers'); weap(u, 'Laser Carbines')[2] = '9'; u['p'] = 150; mark(u, 'Laser Carbines range 6 → 9; cost 145 → 150')
u = unit('marauders', 'commando-heavies'); weap(u, 'HMGs')[4] = ''; weap(u, 'Missiles')[4] = 'AP1, Anti-Aircraft'; mark(u, 'Anti-Aircraft moved from HMGs to Missiles')
u = unit('nameless', 'latropod'); u['s'][4] = '7+'; u['p'] = 350; mark(u, 'SV - → 7+; cost 385 → 350')
u = unit('plague', 'plague-mule')
if 'APC' not in u['k']:
    u['k'] = sorted(u['k'] + ['APC'])

u = unit('veer-myn', 'tangle'); u['k'] = ['Tactician (Black, Orange)' if k.startswith('Tactician') else k for k in u['k']]; mark(u, 'Tactician set to (Black, Orange)')
u = unit('veer-myn', 'the-technonest')
u['r'] = [[n, 'When activated in the movement phase, this Unit can spend 1 CP to discard its Action Token (it does not move) and receive a Combat Token. It then rolls a single D8 and on a roll of 5+, a new unit of Crawlers is immediately created, embarked in the Nest (as long as there is enough capacity for it and you have enough models). The Technonest\'s activation then ends.'] if n == 'The Spawning' else [n, t] for n, t in u['r']]
mark(u, 'The Spawning rewritten')

fac_ = {f['id']: f for f in out['factions']}
ORDER_FIX = {
 ('forge-fathers', 'Born of Fire!'): (None, "Instead of using the Unit's normal weapon profile, use this profile: Incendiary Grenades – Range 9\", ADice 1, AP1, Ignores Cover, Pinning."),
 ('marauders', 'Hunker down'): ('When an Infantry or Heavy Infantry Unit activates in the movement phase.', 'Place a Status Marker on the Unit as a reminder. The Unit counts as In Cover until the end of the Round.'),
 ('marauders', 'One Step Ahead'): ('In the End Phase Special Rules step.', 'Choose a Unit within Command Radius of a friendly Command Unit to make an Advance move (for 1 Command Point) or a Sprint move (for 2 Command Points), following the normal rules. One Unit may be moved per friendly Command Unit In Play (pay the points for each Unit moving). If both sides have this ability, the Player with the initiative chooses which player moves all their units first. Units cannot move in Base contact with enemy units and are not given Combat tokens, and a Unit can only move once like this per Round.'),
 ('plague', 'Infection'): ('When a non-Vehicle, non-Super-Heavy Unit activates in the Movement Phase.', None),
 ('plague', 'Aura of Terror'): ('When a Unit Sprints and engages an enemy Unit in base-to-base contact. The Unit must be in Command Radius before it moves.', None),
 ('plague', 'Tear Apart'): ('When an Infantry or Heavy Infantry Unit attacks in an Assault.', None),
 ('veer-myn', 'Burrowing Attack'): ('When a Unit Sprints and engages an enemy Unit in an Assault in the Movement Phase.', 'The assaulting Unit ignores any Hindered charge modifier (other modifiers still apply). If the enemy Unit has Overwatch, its shooting attack against this Unit suffers a -1 to hit modifier. Now place a Status Marker on the charging Unit. Until the end of the Round, it has the Sustained Attack keyword when rolling to-hit in Assault.'),
 ('veer-myn', 'Overwhelm'): ('Immediately after another friendly Unit activated using the Keep Going! Tactical Order.', None),
 ('veer-myn', 'Narcotic Frenzy'): ('When an Infantry or Heavy Infantry Unit Sprints to engage an enemy Unit in an Assault in the Movement Phase.', None),
}
for (fid, on), (w, e) in ORDER_FIX.items():
    o = next(o for o in fac_[fid]['orders'] if o[0] == on)
    if w: o[2] = w
    if e: o[3] = e
fac_['gcps']['rules'][0][1] = fac_['gcps']['rules'][0][1].replace('GCPS Infantry Units', 'Infantry Units')
fac_['gcps']['rules'][0].append('Errata v1.2: applies to Infantry only — Heavy Infantry are excluded.')
fac_['veer-myn']['rules'][0][1] = 'When taking a Nerve test, this army\'s Units receive a +1 to the roll for each other friendly Unit within 6", up to a maximum of +2.'
fac_['veer-myn']['rules'][0].append('Errata v1.2: counts each other friendly Unit.')
for o in fac_['enforcers']['orders']:
    if o[0].startswith('Shock'):
        o[3] = o[3].rstrip() + ' This cannot reduce an attack below AP 0. This also does not affect attacks which do not have the Armour Piercing Keyword.'
        o.append('Errata v1.2')

gl = [[g['name'], g['text']] for g in d['glossary']]
GLX = {
 'Anti-Grav': "Units with the Anti-Grav Keyword may move over any other Bases or terrain up to Height 4 without penalty (they don't have to move round them). They will still be affected by Difficult Terrain as normal if starting or ending their move within it. They must still respect Unit Coherency and proximity rules once they finish moving and cannot end their move on or inside Impassable terrain. Units with this Keyword may also exit from a transport Vehicle that has the Fly Keyword.",
 'Fly': 'Units with the Fly Keyword operate above the battlefield and suffer less restriction of movement than their counterparts on the ground. They have a Height of 6 above the terrain level they are over. Flyers above this height cannot interact with ground targets meaningfully in the context of the game. This means that flyers may well have to steer around buildings. See page 44.',
 'Heavy Armour': 'When firing at a Unit with the Heavy Armour Keyword, weapons that do not have the Armour Piercing (AP) Keyword half the number of dice the Unit rolls to damage the target, rounding up.',
}
for g in gl:
    if g[0] in GLX:
        g[1] = GLX[g[0]] + ' [Errata v1.2]'
    if g[0] == 'Chained Barrage':
        i = g[1].find('original one.')
        g[1] = 'Units with this Keyword that fire Blast weapons, may place additional templates next to any previously placed template in this attack, not just the original one.' + g[1][i + len('original one.'):] + ' [Errata v1.2]'
gl.append(['Command Radius (n)', "Strategic Orders can only be used on friendly Units within the Command Radius (in inches) of a friendly Command Unit (at least one Base needs to be within range). Strategic Orders can be used on the Command Unit itself. Units out of the Command Radius of every friendly Command Unit cannot have Strategic Orders played on them."])
for g in gl:
    g[1] = re.sub(r'\s(4[6-9]|50)(?=\s*(\[Errata v1\.2\])?$)', '', g[1])
gl.sort(key=lambda g: g[0].lower())
out['glossary'] = gl
out['stratagems'] = [
    {'id': 'quick', 'n': 'The Upper Hand', 'p': 5, 'max': 1, 'd': 'Add +2 to your result when rolling for Initiative in Round 1 (including when re-rolling ties).'},
    {'id': 'hold', 'n': 'Take and Hold', 'p': 20, 'max': 1, 'd': 'At the end of a Round, use on a Dynamic Objective you claimed and scored that Round. Roll 1D8: on a 5+ the Objective starts the next Round Active, regardless of its current state.'},
    {'id': 'bombard', 'n': 'Bombardment Fire', 'p': 30, 'max': 1, 'd': 'From Round 2 onwards, any friendly Command Unit can use its Overwatch Action Token to call in the Bombardment; if it does, it may not fire any other weapons this turn, and its action ends once the attack is resolved. Pick a point on the table: Range Unlimited, ADice 1, AP1, Blast (4), Indirect (only), Pinning. Roll to scatter the first template, then place three more following the normal rules.'},
    {'id': 'intel', 'n': 'Covert Intel', 'tiers': [[1, 10], [2, 25], [3, 50]], 'unit': 'intel chance', 'd': 'Before the Recon roll, roll 1D8 per intel chance bought. Each 5+ means you begin the game with 1VP already scored.'},
    {'id': 'recon', 'n': 'Advanced Reconnaissance', 'dice': [['Black', 5], ['Orange', 10], ['Green', 15]], 'd': 'Buy as many Command Dice as you wish. They are used once, added to your Recon roll before deployment. If the player who wins the Recon roll used Advanced Reconnaissance, they add +1 to their Initiative roll for Round 1.'},
]
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open('data.min.json', 'w').write(s)
print(len(s), 'bytes', sum(len(f['units']) for f in out['factions']), 'units')
