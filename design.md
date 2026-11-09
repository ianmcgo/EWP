# Epic Warpath Army Builder – Design Notes

A single-file web app (`index.html`) for building Epic Warpath armies. No server, no build step needed to run it — open the file or host it on GitHub Pages.

## Data sources

- **Unit profiles, points, keywords, weapons, special rules, army rules, Strategic Orders, Battlefield Stratagems and the keyword glossary** were extracted from the *Epic Warpath Rulebook (1st Edition, MGEWM101)* PDF.
- **FAQ & Errata v1.2 (July 2026)** is applied on top. Units changed by errata show an orange `ERRATA` badge and a note in their profile listing exactly what changed.
- **Unit pictures** are linked (not copied) from Mantic's web store product galleries and the Mantic Vault (STL store) product images, using only images whose product is marked Epic Warpath. Units sold only in Reinforcement boxes use the box photo, captioned "Reinforcements box photo". Three units with no photo anywhere use a stand-in, also captioned: Saturation and Shield Tunnellers use the regular Tunneller, and the Peacekeeper Captain uses the Peacekeepers squad. Captions come from `src/image_notes.json`. If an image fails to load it is simply hidden.
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

## Rules links

The Summary panel's **Rules** section, the footer and the printout link to:
- **Rulebook PDF**: the rulebook PDF hosted on Mantic's own site (`manticgames.com/wp-content/uploads/2025/07/MGEWM101-Epic-Warpath-Rulebook-EN.pdf`), opened directly.
- **FAQ & Errata PDF**: free from Mantic's store.
- **Free online rules**: the Mantic Companion rules (free account required).

The rulebook itself isn't copied into this repo; the link points at Mantic's copy.

## Rules reference

(The reader's 🖨 Quick ref button prints the one-page rules reference.)


**📖 Rules** (header button, or the Rules tab on phones) opens a full-screen reader with all 15 chapters of the Epic Warpath Rules (version 1.1) from the Mantic Companion online rules:
- Chapter list on the left (a dropdown on phones), a Contents page, section jump buttons at the top of each chapter, and previous/next chapter buttons.
- **Search** across every section; results show the chapter, page and a highlighted snippet, and tapping one jumps to that section.
- The Keywords chapter is filled from the keyword glossary with FAQ & Errata v1.2 changes marked (the saved Companion page only had the heading).
- Diagrams are linked from the Companion site (`companion.manticgames.com/uploads/ewp/rules/…`), which serves them publicly. The saved pages' copies of the images were damaged by line-ending conversion when the pages were saved, so they aren't used.

The text was extracted from the saved Companion pages into `src/rules.json` (chapters → sections with marker, title, page and cleaned HTML) and injected at build time.

## Scenario generator

The fourth dice menu button, **Scenario**, follows the Battle Scenario steps in the rules:
- **Roll Scenario** rolls a D8 on each Scenario Parameter chart in order (Deployment Zones, Objectives, Scoring, Reserves Ratio) with a 3D throw of four D8s, then shows a card with each roll, its chart band and the full result text.
- The extra random rolls the charts call for are made automatically: which opposite corners deploy (Deployment 5–6) and which table edge the Static Objective line runs from (Objectives 7–8).
- **Game Length**: a "Roll for Round 6" button (D8, 5+ plays Round 6).
- **Recon Roll**: rolls 3 Black plus your list's Tactician dice and shows your total to compare with your opponent's.
- The current scenario is saved in the browser (`ewp_scenario_v1`), every roll goes into the Roll Log (tap a scenario log entry to reopen it), and there's a link to the full Scenarios chapter.

## Sharing, export, print

- **Share** encodes the list as base64url JSON in the URL hash (`#l=…`). Opening the link imports a copy. Links only work for other people when the page is hosted (e.g. GitHub Pages), not from a local file.
- **Export** gives a plain-text list (for forums/Discord) and a `.json` download that can be re-imported from *My Lists*.
- **Print** opens a dialog (choices are remembered) with four sections, each starting on a new page:
  1. **Army roster & summary**: centered header and stat strip, a compact roster table per Company plus Battlefield Stratagems, two-column unit profiles (identical units printed once with ×N), army rules, Strategic Orders and only the keywords your list uses. Long rules text stays left-aligned; headings, stats and tables are centered.
     Each part has its own checkbox under "Army summary": **Top summary** (name, faction, stat strip, validity), **Roster & points lists**, **Unit profiles**, **Army rules**, **Strategic Orders**, **Universal Tactical Orders** (Keep Going!, Fight On!, Courage! – also adds them to the command cards) and **Keywords**. If Army rules is off, the orders get their own section heading. `rosterHtml` tags each part with a marker and drops the unchecked ones.
  2. **Unit reference cards**: trading-card style at exactly 2.5 × 3.5 in, nine per page in a 3 × 3 grid. Each card has the name banner, a points badge in the faction colour, type/bases/slot line, the unit photo, a stat bar (SP SH AS AR SV HT US), keywords, a weapons table, Command Transport and special rules, and a footer with faction and Army Nerve. One card per unit type by default (×N shown), or one per unit taken.
  3. **Command cards**: the same card frame for your faction's Strategic Orders (CP badge, When box, effect), your Battlefield Stratagems (points badge, gold frame) and, if chosen, the Tactical Orders (grey frame).
  4. **One-page rules reference**: a three-column Letter/A4 sheet based on the rulebook's Quick Reference Sheets: round sequence, Command Phase, Action Tokens, Tactical Orders, Movement, Shooting with modifiers, Blast weapons, Assault with modifiers, Pinning, End Phase, key keywords, objectives and game end. Also available from the 🖨 Quick ref button in the rules reader.

  **Card style** (applies to unit and command cards): **Full colour** is the trading-card look with a dark frame and banners; **Printer friendly** is a white card with a soft grey outline, thin faction-colour accents and light rule lines, which uses far less ink; **Black & white** (works with either style) turns the faction colours grey and the photos greyscale. Unit photos sit on a white background and are shown whole (not cropped).

  **Cutting**: there are no cut lines. Cards sit edge to edge inside a full-bleed dark frame, so two straight cuts each way separate a sheet and every card keeps an even dark border even if a cut is slightly off. Print at 100% / Actual size with headers and footers off (page margin is 0.2 in).

  **Fitting**: each card's text auto-shrinks (7 pt down to about 5 pt) until it fits. Before going very small it shortens the photo, then drops it; if a card still overflows (very long Super-heavy rules), its special rules continue on a second card marked 1/2 and 2/2. Printing waits up to 4 s for unit photos to load.

## Dice roller

The dice panel opens on a menu of four big buttons (two by two on narrower screens):

- **D8** opens its options: number of dice, the target number, and Exploding 8s, then Roll. Exploding 8s starts unchecked every time the D8 screen opens, since few weapons have Sustained Attack or Vicious. If the last roll had misses, there's also "Re-roll misses from last roll".
- **Command** opens its options: Black/Orange/Green counts, "Use my army" (3 Black plus one die per Tactician colour in the list), the face settings, then Roll.
- **Target** rolls the Targeting Die straight away (3 On Target faces; scatter 3, 3, 4, 5, 6 with a random direction).

Results aren't shown on the option screens. They appear in the 3D roll and in the **Roll Log**, which sits at the bottom of every dice screen. The log keeps the last 60 rolls in the browser (`ewp_dice_log_v1`), each with its time, the dice (hits green, exploding 8s outlined, bonus dice dashed) and the total. It can be cleared.

**Command Die re-rolls**: after a Command roll you get one re-roll per Command Unit in your list. Tap a die in the 3D lineup and it hops and lands on a new face; with 3D off, tap the die in the latest log entry instead. Re-rolled dice are outlined in the log, and the entry's CP total updates.

**Command Dice faces**:

  | Colour | Blank | 1 sword | 2 swords | 3 swords | Average CP |
  |---|---|---|---|---|---|
  | Black | 2 | 3 | 1 | – | 0.83 |
  | Orange | 1 | 3 | 2 | – | 1.17 |
  | Green | – | 2 | 3 | 1 | 1.83 |

These can be edited under "Command dice faces"; the setting is saved in the browser (`ewp_dice_v2`).

### 3D roll animation

After a roll, the result bar has **Roll Again** (or press R), which repeats the same kind of roll in place: a new D8 pool with the current settings, a new Command Dice roll, or a new Targeting Die. After tapping a Command Die to re-roll it, the button re-rolls that die again while re-rolls remain, then switches to rolling the whole pool.


Every roll (D8 attacks, re-roll misses, Command Dice, a single Command Die re-roll, the Targeting Die) opens a full-screen 3D view:

1. **Throw** – dice are thrown up the mat from the bottom of the screen and bounce around inside the visible area: they hit the screen edges like walls, bump into each other, and roll to a stop on a grassland battle mat. A clack plays on each impact. When they stop, each die tips onto its rolled face.
2. **Line up** – the dice hop into neat rows facing the camera (a rising tick per die), sorted high to low. Hits get a gold ring; misses shrink slightly. The camera pulls back to fit large pools.
3. **Exploding 8s** – bonus dice are thrown as a second wave with an "Exploding 8s!" banner, then join the lineup on the next row.
4. **Result** – a chime plays and a result bar shows the total; **Confirm** (or Enter/Esc) returns to the dice options.

Tap the screen or press Space during a throw to skip to the lineup.

How it works:
- **three.js r128** is loaded from cdnjs only the first time you roll, so the builder stays light. If it can't load (offline), you get a toast and the flat results as before. Turning off "3D dice", or having *reduce motion* set in your OS, also uses the flat results.
- Results are always decided first with `crypto.getRandomValues`; the animation just shows them. Each die's final rotation is computed so the rolled face points up (or at the camera in the lineup) with its text upright (`restQuat` builds the rotation from each face's normal and "up" direction, which `faceFrames` reads from the geometry's UVs).
- **Physics** (`stepSim`, fixed 1/120 s steps): each die is a sphere collider with gravity, floor bounce and friction, rolling spin, and a ceiling so it never leaves the top of the view. The walls are the edges of the visible mat (`floorBox` raycasts the screen corners onto the floor, leaving room for the banner and result bar), so on a narrow phone screen dice ricochet off the sides instead of flying off. Dice-to-dice contacts are resolved with impulses and position correction (3 passes per step), and dice already lined up from an earlier wave act as fixed obstacles. The camera pulls back before a throw if the pool needs more floor space. When everything stops (or after 3.6 s), each die makes a short final tip onto its rolled face. Skipping runs the simulation instantly.
- Dice faces are drawn on canvases: D8s 1–8 with opposite faces summing to 9; the Targeting Die has 3 starbursts and 3, 3, 4, 5, 6 with a direction chevron (it settles at the same angle shown in the text); Command Dice use the face settings and are re-drawn if you edit them.
- The grass mat is generated on a canvas (mottled greens, dirt patches, grass strokes, tufts and pebbles), tiled under a vignette and fog.
- All sounds are synthesised with the Web Audio API (no audio files). There's a **Sound** toggle next to the 3D toggle; both are remembered.

Randomness uses `crypto.getRandomValues`.

## Rebuilding

The source lives in `src/`:

- `src/parse.py` – extracts everything from the rulebook PDF into `data.json` (needs `pdfplumber`). It uses font and position information rather than plain text, because the army list pages are two-column stat cards.
- `src/build_data.py` – compacts the data and applies the errata.
- `src/build.py` – injects the data and the unit image URLs (`src/images.json`) into `src/app.html`, writing `index.html`.

```
cd src
python3 parse.py path/to/Epic-Warpath-Rulebook.pdf
python3 build_data.py
python3 build.py ../index.html
```

When new errata comes out, add the changes to `build_data.py` and rebuild.

## Data corrections

A few Strategic Orders tables (Forge Fathers' Born of Fire, Marauders' Hunker Down and One Step Ahead, all of Plague and Veer-Myn) didn't extract cleanly from the PDF, so `build_data.py` overrides them with text transcribed from the page images (`ORDER_FIX`). Stray page numbers are also stripped from glossary text.

## Legal

Unofficial fan tool. Epic Warpath, its rules text and its product images are © Mantic Games. The rulebook isn't included in this repo.
