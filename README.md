# Trench Dive 🌊

A rare-answer trivia game in a single HTML file. Each dive is 7 prompts like “Name a fruit”. Any answer that fits counts, but rarer answers score more and sink your submarine deeper (up to 7,000 m).

| Tier | Points |
| --- | --- |
| Plankton | 10 |
| Too Clever (sounds wrong but is right) | 15 |
| Schooler | 30 |
| Rare | 60 |
| Deep Cut | 85 |
| Trench Treasure | 100 |

**Modes:** a Daily Dive (the same 7 prompts for everyone, with streaks and sharing) and Unlimited. There are about 560 prompts and 141,000 accepted answers, plus special Daily Dives on Easter, Halloween and Christmas.

## Play

Open `index.html` in any modern browser. It is fully self-contained apart from Google Fonts, which fall back to system fonts when offline. Progress is saved in the browser’s `localStorage`.

## Deploy to GitHub Pages

1. Upload this folder's contents to a GitHub repository (the website's **Add file → Upload files** works).
2. In **Settings → Pages**, set **Source** to **Deploy from a branch**, branch **main**, folder **/ (root)**, then **Save**.
3. The game goes live at `https://YOUR-NAME.github.io/REPO-NAME/` within a minute or two.

To update the game later, upload a new `index.html` over the old one. Shared Daily Dive results include the game’s address automatically when it is played from its own site.

### Tier feedback

Players can tap **“Tier feel wrong?”** after an answer. Flags are stored on their device, and **Settings → Tier feedback → Copy** gives a plain list. To collect feedback as GitHub issues instead, set this constant in `src/app.base.html` and rebuild:

```js
const FEEDBACK_URL = 'https://github.com/YOUR-NAME/YOUR-REPO/issues/new';
```

A **Send** button then opens a pre-filled issue.

## Build

```bash
python3 src/build.py        # writes index.html (the game) and src/built.html
python3 src/build.py test   # writes src/built.test.html, which exposes internals for tests
```

`src/build.py` joins the engine (`src/app.base.html`) with the content files. Its file list sets the load order, so new content files must be added there.

## Test

```bash
npm install
npx playwright install chromium
npm test
```

Each test prints `[]` when it passes. A single `ERR_NAME_NOT_RESOLVED` from the smoke test is expected offline, because Google Fonts can’t load. Set `CHROME_PATH` to use a specific Chromium binary.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | The built, playable game (this is what GitHub Pages serves) |
| `src/app.base.html` | Engine, styles, markup, ocean scene, achievements, categories, sharing, holidays, tutorial |
| `src/sfx.js` | All sound, synthesised with Web Audio (no audio files) |
| `src/gen_*.js`, `geo_*.js`, `expand_*.js` | Questions: `A(id, category, prompt, "Answer;Alias|Answer2|…")` |
| `src/extra_*.js` | Extra answers for existing questions: `XA(id, "…")` |
| `src/nzrank.js` | Tier overrides and post-processing |
| `src/drop.js` | Retired question ids |
| `tests/` | Playwright browser tests |
| `HANDOFF.md`, `NEW_CHAT_PROMPT.md` | Detailed development notes and content rules |

### Answer list format

Answers are listed most common first, and position sets the tier.

| Marker | Meaning |
| --- | --- |
| `!Answer` | Too Clever |
| `~S` `~R` `~D` `~T` | Everything after is at least Schooler, Rare, Deep Cut or Trench Treasure |
| `~LOCK` | In `XA()` batches: earlier answers keep their tiers, and later ones take exactly the tier of the latest marker (`~P` for Plankton) |
| `;` | Separates aliases |
