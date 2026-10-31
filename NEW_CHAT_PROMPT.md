# Trench Dive — new chat handoff

## 1. What to do

1. Start a new Claude chat.
2. Attach **trench-dive.zip** (or download your repo from GitHub: Code → Download ZIP). It holds all the source, tests and notes.
3. Paste the prompt in section 2 as your first message.

---

## 2. Prompt to paste

> I'm King (NZ-based). I'm continuing development of **Trench Dive**, my Krillion-style trivia game, from a previous chat. The full project is in the attached **trench-dive.zip**. Please unzip it to `/home/claude`, then read `NEW_CHAT_PROMPT.md` and the top of `HANDOFF.md` (newest version notes first) before doing anything.
>
> **How I like to work:** be direct and honest, not agreeable. If I'm wrong, say "you're wrong" and explain why, and rate my ideas honestly out of 10 when relevant. If you're unsure, say so instead of guessing. When I ask for changes, just do them: build, test, publish and summarise.
>
> **Publishing:** after each change, only publish the existing artifact at https://claude.ai/artifact/WdDGq36Yd5qWvKbMEfB1sF (publish with that url). Don't rebuild the handoff zip or update notes unless I ask ("make the zip").
>
> **Unzip note:** the zip contains a top-level `trench-dive/` folder, so unzip to `/home/claude` and work in `/home/claude/trench-dive`.
>
> Current version is **v76**. Confirm you've loaded the project, then wait for my next request.

---

## 3. Project at a glance

- **Game:** a single-page HTML trivia game. Each dive has 7 prompts ("Name a…"). Rarer answers score more and sink the submarine deeper (max 7,000 m).
  - **Tiers:** Plankton 10, Too Clever 15, Schooler 30, Rare 60, Deep Cut 85, Trench Treasure 100.
  - **Modes:** Daily Dive (same 7 for everyone, 30 s per prompt) and Unlimited (30/45/60 s, default 30).
- **Size:** 558 questions, about 140,900 accepted answers. Start-up is about 0.5 s (answer lists are parsed lazily).
- **Features:**
  - an animated ocean scene, and creatures by depth zone
  - achievements (about 30, Bronze to Mythic levels) and a Categories tab
  - Daily Dive sharing, and holiday Daily Dives (Easter, Halloween, Christmas) where all seven prompts come from that holiday's pool (HOLI[h].qs)
  - a "Did you mean…" prompt for typos (it always asks, with the closest match; capitals never matter)
  - Settings, and Calmer motion

## 4. Files (in `/home/claude/trench-dive`)

- **`src/app.base.html`:** the engine, CSS, markup, scene, creatures, achievements, Categories tab, share sheet and holidays.
- **`src/build.py`:** builds `src/built.html`. `python3 src/build.py test` builds `built.test.html`, which exposes `window.__QS` and `window.__S`.
  - The file list in build.py decides load order. New content files must be added there.
- **Content files:**
  - `gen_*.js` (questions via `A(id, cat, prompt, "answers")`)
  - `geo_*.js`, `expand_*.js`, `gen_big.js`, `big_extra.js`
  - `extra_*.js` (extra answers via `XA(id, "answers")`)
  - `extra_local.js`, `extra_merge.js`, `clever.js`, `clever_real.js`
  - `nzrank.js` (tier overrides), `drop.js` (retired question ids)
- **Tests:** `PLAYWRIGHT=/home/claude/.npm-global/lib/node_modules/playwright CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome bash tests/run.sh` builds and runs all 8 tests. Each should print `[]`. smoke's single ERR_NAME_NOT_RESOLVED is expected (offline fonts). Keep single commands under 5 minutes.
- **Release:** `python3 src/build.py` writes `index.html` (the game, served by GitHub Pages) and `src/built.html`. Copy `index.html` into the artifact copy and publish to the artifact url. Only when asked: zip the project (excluding `scratch/` and `src/built*.html`) as `trench-dive/…` to `/mnt/user-data/outputs/trench-dive.zip`.

## 5. Content rules

**Answer list format:** `"Name;Alias|Name2|…"`.
- **Ranking:** order equals commonness, so the most common answers go first.
- **Tier floors:** `~S`, `~R`, `~D` and `~T` force everything after them to at least Schooler, Rare, Deep Cut or Trench Treasure.
- **Too Clever:** `!Answer` marks a Too Clever answer.

**Too Clever means only "sounds wrong but is technically correct":**
- **Valid examples:** banana for a berry, Antarctica for a desert, chicken for a dinosaur, the Caspian Sea for a lake.
- **Not valid:** puns or loosely related wordplay. They were all removed in v57, so don't add them back.
- **Optional:** most questions should have none.

**Regional balance:**
- **Lead with US/UK answers:** most guesses are American or English.
- **Regional extras:** NZ, Australian, Swiss and German answers belong in the tail as rarer answers, ranked from a global viewpoint (e.g. KiwiSaver is Rare, and Lamington crisps are Trench Treasure).

**Unsure items:** mark them with `? ` (question mark plus a space) and strip them before building with `re.sub(r'\|[^|"]*\?\s+(?=[|"])', '', s)`.
- Real titles ending in "?" are kept, because only "? " followed by a separator gets stripped.
- Don't invent facts (e.g. unverifiable NZ limited-edition crisp flavours). Leave them out, or ask King.

**Tier overrides (`nzrank.js`):**
- **Basic overrides:** `NZ_TIER[id] = { 'Name': tier }`. Add new ones with `Object.assign(NZ_TIER.x = NZ_TIER.x || {}, {...})`. A duplicate key in the object literal silently drops the earlier one.
- **Any-alias passes:** there's a Too Clever pass (deserts/lakes) that matches on any alias.
- **POST hooks:** use `POST[id]` for anything touching huge lists (k_movie about 20k, w_songs about 14k, w_cities about 23k). They run lazily on first use, which keeps start-up fast.
- **Raise-only pass:** lifts famous songs and films appended to those huge lists, and never demotes.

**Before adding a question:**
- **Id clashes:** check the id against all `gen_*`, `geo_*`, `expand_*` and `app.base.html` files and `drop.js`. Old questions use `add(` in app.base.html.
- **Size:** small closed lists are fine (King wants them kept).

**Categories:**
- **Codes:** geo, life, ent, food, sport, nat, gen, words, tech, music, sci, cult, hist, lit, biz, myth and nz. Names, colours and icons are in `CAT_NAMES`, `CAT_COL` and `CAT_IC`.
- **Thin:** Science (13), Mythology (9) and New Zealand (3, small on purpose).
- **Holiday pools:** a new holiday question must also be added to HOLI[h].qs in app.base.html, or it only appears in Unlimited.

## 6. Important engine facts

- **Unseen first:** Unlimited dives prefer questions the player hasn't met (`ACHS.stats.prompts`).
- **Daily numbering:** #1 is 29 Oct 2026 (`dailyNumber`).
- **Storage (localStorage):**
  - `trenchdive.v1` holds scores and daily records.
  - `trenchdive.settings.v1` holds settings.
  - `trenchdive.ach.v1` holds achievements, plus `catStats` per category.
- **Achievement levels:** defined in the `ACH` array (`lv` thresholds). On load, levels already reached under new thresholds unlock quietly.
- **Corner buttons:** Settings, Achievements and Categories. They hide only after 520 px of scrolling down, and reappear on any scroll up.

## 7. Ideas not yet done

- **Real tier data:** either a "this felt wrong" flag button, or logging real answers to rank by frequency. This is the biggest quality lever.
- **Older phones:** test on a real older phone. The file is about 2.5 MB.
- **More content:** more Science and Mythology questions, and more of the wordplay styles (before/after-word questions, rhymes, palindromes).
- **Sound:** subtle sound with a mute toggle.
- **Onboarding:** a first-dive explainer.
