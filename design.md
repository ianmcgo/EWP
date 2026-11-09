# Epic Warpath Army Builder – Design Notes

A single-file web app (`index.html`) for building Epic Warpath armies. No server, no build step needed to run it — open the file or host it on GitHub Pages.

## Data sources

- **Unit profiles, points, keywords, weapons, special rules, army rules, Strategic Orders, Battlefield Stratagems and the keyword glossary** were extracted from the *Epic Warpath Rulebook (1st Edition, MGEWM101)* PDF.
- **FAQ & Errata v1.2 (July 2026)** is applied on top. Units changed by errata show an orange `ERRATA` badge and a note in their profile listing exactly what changed.
- **Unit pictures** are linked (not copied) from Mantic's web store product galleries. If an image fails to load it is simply hidden.
- Checked against a Mantic Companion export of a Marauders list: all 21 units match on points, stats and weapons once errata v1.2 is applied.

### Errata v1.2 changes applied

| Faction | Unit / rule | Change |
|---|---|---|
| Asterians | Wraith | Noh Blasters renamed Light Plasma Cannon |
| Enforcers | Lieutenant | Sustained Attack removed from Genling 45 Laser Rifles; 40 → 35 pts |
| Enforcers | Shock-Resistant Armour (order) | Can't reduce below AP 0; doesn't affect non-AP attacks |
| Forge Fathers | Brokkr | 235 → 185 pts |
| Forge Fathers | Hammerfist Drop Troopers | + Anti-Grav |
| Forge Fathers | Nidavellir Drop-Fortress | Quick-fix (All Types) |
| GCPS | Hold the Line! | Infantry only (Heavy Infantry excluded) |
| GCPS | Rangers | Laser Carbines 6" → 9"; 145 → 150 pts |
| Marauders | Commando Heavies | Anti-Aircraft moved from HMGs to Missiles |
| Nameless | Latropod | SV 7+; 385 → 350 pts |
| Plague | Mule | + APC (already present in the parsed data) |
| Veer-Myn | Safety in Numbers | "each other friendly Unit" |
| Veer-Myn | Tangle | Tactician (Black, Orange) |
| Veer-Myn | The Technonest | The Spawning rewritten |
| All | Keywords | Anti-Grav, Chained Barrage, Fly, Heavy Armour rewritten |
| All | Stratagems | Quick Thinking renamed The Upper Hand; Bombardment Fire reworded |

## Company rules (validation)

Every Company is validated live. Slot counting:

| Slot | Rule |
|---|---|
| HQ | Exactly 1 per Company |
| Troop | 2 to 4 |
| Specialist | Up to 1 per Troop |
| Support | Up to 1 per 2 Troops/Specialists (any mix) |
| Super-heavy | Max 1 per Company; uses a Support slot |
| Command (Super-heavy) | Uses the HQ slot **and** a Support slot |
| Transport | Up to 1 per unit that is not a Walker, Vehicle, Super-heavy or Bike |
| Unique `[U]` | Once per army |

Command Transports are an option on the HQ unit itself (checkbox) and don't use a Transport slot.

The unit picker runs each unit through the same rules *before* you add it: units you can't take are greyed out with the exact reason ("Needs 1 more Troop/Specialist (1 Support per 2)"), so you never build an illegal list by accident.

## Code layout (all inside `index.html`)

- `DATA` – the faction/unit/glossary JSON, injected at build time.
- **State**: `lists` (all saved lists) and `cur` (the open list). Lists are stored in `localStorage` under `ewp_builder_lists_v1`; there's no account and no limit on the number of lists.
- `roles(u)` maps a unit to the slots it consumes; `counts()`/`caps()` compute usage and unlocked limits; `whyNot(u, company)` returns the blocking reason or `""`.
- `issues()` produces the plain-English validation list shown at the top of the army.
- Rendering is plain template strings (`renderBar`, `renderList`, `renderPicker`, `renderInfo`) re-run on every change; clicks are handled by one delegated listener keyed on `data-act`.
- `glossFor(keyword)` maps a keyword (including variants like `AP2`, `Blast (3)`, `Indirect (only)`) to its glossary entry for the tap-to-read popovers and the "Keywords in this list" section.

## Sharing, export, print

- **Share** encodes the list as base64url JSON in the URL hash (`#l=…`). Opening the link imports a copy. Links only work for other people when the page is hosted (e.g. GitHub Pages), not from a local file.
- **Export** gives a plain-text list (for forums/Discord) and a `.json` download that can be re-imported from *My Lists*.
- **Print** builds a print-only layout: every unit's full profile, the army rule, Strategic Orders, and only the keywords your list actually uses.

## Dice roller

- **D8 attack roll**: pick dice count and target number; optional Exploding 8s (each natural 8 that succeeds adds a bonus die, recursively). "Re-roll misses" re-rolls failed dice.
- **Command Dice**: "Use my army" loads 3 Black plus one die per Tactician colour in the list. After rolling you can tap dice to re-roll them, one per Command Unit in the list (per the rulebook). The CP tracker lets you spend points through the Round.
- **Targeting Die**: 3 On Target faces, and 5 scatter faces (3, 3, 4, 5, 6) with a random direction. The On Target image is rendered from the supplied Targeting Die STL.
- **Command Dice faces**:

  | Colour | Blank | 1 sword | 2 swords | 3 swords | Average CP |
  |---|---|---|---|---|---|
  | Black | 2 | 3 | 1 | – | 0.83 |
  | Orange | 1 | 3 | 2 | – | 1.17 |
  | Green | – | 2 | 3 | 1 | 1.83 |

  The faces can still be edited under "Command dice faces" if needed; the setting is saved in the browser (key `ewp_dice_v2`).

Randomness uses `crypto.getRandomValues`.

## Rebuilding

The source lives in `src/`:

- `src/parse.py` – extracts everything from the rulebook PDF into `data.json` (needs `pdfplumber`). It uses font and position information rather than plain text, because the army list pages are two-column stat cards.
- `src/build_data.py` – compacts the data and applies the errata.
- `src/build.py` – injects the data, the unit image URLs (`src/images.json`) and the Targeting Die image into `src/app.html`, writing `index.html`.

```
cd src
python3 parse.py path/to/Epic-Warpath-Rulebook.pdf
python3 build_data.py
python3 build.py ../index.html
```

When new errata comes out, add the changes to `build_data.py` and rebuild.

## Legal

Unofficial fan tool. Epic Warpath, its rules text and its product images are © Mantic Games. The rulebook isn't included in this repo.
