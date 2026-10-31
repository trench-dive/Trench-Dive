> New chat? Read NEW_CHAT_PROMPT.md first (prompt, workflow, rules). Version notes below, newest first.

# Trench Dive — Handoff & Continuation Package

## 1. Project summary & tech stack

**What it is:** a single-file HTML trivia game modelled on Krillion ("rare-answer" trivia). Each "dive" = 7 prompts, 25 s each. You type an answer; rarer answers score more points and sink your submarine deeper. Unlimited dives; best score/depth saved in `localStorage`.

**Stack:** plain HTML + CSS + vanilla JS (no framework, no build deps) + one `<canvas>` ocean scene. Google Fonts (Bricolage Grotesque, Figtree) are the only external resource. Dark single theme. Published as a private claude.ai Artifact (current link: https://claude.ai/artifact/WdDGq36Yd5qWvKbMEfB1sF) (single self-contained HTML; the host adds the doctype/head and a `[hidden]{display:none!important}` reset). Build step is a ~20-line Python concatenator (`src/build.py`).

**Files**
- `dist/trench-dive.html` — the finished, self-contained game (467 KB). This IS the latest published version (Artifact v3).
- `src/app.base.html` — UI + engine (CSS, markup, JS core, scene). Contains the original 50 hand-tiered questions inline (legacy 4-arg `add()` calls).
- `src/helper.js` (A() wrapper), `src/clever.js` (CLEVER overrides, currently empty), `src/extra.js` (EXTRA answers appended to existing question ids).
- Question data (all use `A(id, cat, prompt, "A|B;alias|C")`): `geo_a/b/c.js` (geography), `gen_a` (nature/science/tech), `gen_b` (entertainment/history/myth/lit), `gen_c` (food/sport/music/culture), `gen_d` (everyday life, landmarks), `gen_e/gen_f` (New Zealand), `gen_g` (songs, games, screen), `gen_h` (sport, brands, food, film stars).
- `src/build.py` — `python3 build.py` → `built.html`; `python3 build.py test` → `built.test.html` (exposes `window.__QS`, `window.__match`). `src/prune3.py` — helper to strip entries (`clean(file, {qid:[names]})`; also drops items ending " dup" or containing "?").
- `tests/` — Playwright (headless Chromium) scripts: `wrap.sh` (wraps a build in a publish-like skeleton incl. the `[hidden]` reset — REQUIRED or all screens show at once), `count.js` (question/dup/small-list/tier-coverage check), `flow.js` (fuzzy-match samples + two full dives + localStorage check), `smoke.js`, `home.js`, `scroll.js`, `list.js`. Scripts hardcode a scratchpad path and `/opt/npm-tools/node_modules/playwright` + `/opt/pw-browsers/chromium`; adjust.

**Data model / engine (in `app.base.html`)**
- Tiers (index → name, points, metres [= points × 10], colour): 0 Plankton 10/100 m grey `#aab4c0`; 1 Too Clever 15/150 m mint `#7fe3b0`; 2 Schooler 30/300 m light blue `#8fd4ff`; 3 Rare 60/600 m red `#ff5c5c`; 4 Deep Cut 85/850 m purple `#a778ff`; 5 Trench Treasure 100/1,000 m gold `#ffc65a`. Max per dive 700 pts = 7,000 m. Constants: `TIER_NAMES, TIER_PTS, M_PER_PT=10, MAX_DEPTH, SCENE_K=0.4` (displayed metres → canvas scene units 0–2800), `TIER_VARS/TIER_HEX`, `RANKS` (result titles: Shallows/Schooler/Thermocline/Deep Cut/Trench), `ZONES`.
- `A(id,cat,prompt,list)` → `add()` → `splitSix(list,id)`: list is ordered most→least obvious; auto-tiering: Plankton = top 20%, Deep Cut 15%, Trench Treasure ≈6% (min 1), Rare ≈27%, Schooler = remainder. "Too Clever" ONLY via a `!Item` prefix or `CLEVER[id]`. `EXTRA[id]` strings are appended before splitting; repeated names merge aliases. Entry syntax: `|` separates answers, `;` separates aliases. Legacy 4-tier `add(id,cat,prompt,t0,t1,t2,t3)` is flattened and re-split.
- Matching: `norm()` (lowercase, accents stripped, `&`→and, apostrophes dropped, leading "the" stripped, st→saint, mt→mount) → exact map / core (generic words like lake/river/mount dropped) / no-space lookup → plural variants → Damerau-Levenshtein fuzzy (max edits 1 for ≤7 chars, 2 for ≤12, 3 above; none ≤3 chars) → "Did you mean…?" confirm UI (timer pauses). Unknown answer → message + "Search Google ↗" link (opens a Google search in a new tab; does NOT score).
- Dive flow: 7 prompts, 25 s, correct ends the prompt, pass/timeout = 0, ≥3 geography prompts guaranteed (`GEO_MIN`), avoids repeating the previous dive's prompts. Save object `{bestPts,bestDepth,dives,totalPts,last[]}` in localStorage (key `trenchdive.v1`).
- Categories (`CAT_LABEL` in build.py): geo, gen, nat, sci, tech, ent, hist, myth, lit, food, sport, music, cult, nz, life.
- Scene: canvas `#sea` (fixed, full-screen): depth-based colour stops, sky/sun at surface, light rays, marine snow, critters (schools, whales, rays, jellies, squid, anglerfish — counts deliberately thinned), sea floor with vents, tier-coloured pulse rings and bubbles. `drawSub()` draws the yellow submarine (no pilot face, no shadow). The sub is positioned from `.sub-slot` via `slotCenter()` with page-scroll cancelled so it stays fixed while content scrolls.

**v76 (current) — summary of v62–v76:**
- **Live on GitHub Pages:** the build writes the game to `index.html` at the repo root (served with Pages → Deploy from a branch → main → / root). `src/built.html` is still written for tests. The old `dist/` folder and Actions workflow were removed (hidden `.github` folders don't survive drag-and-drop uploads).
- **Tests:** `bash tests/run.sh` builds and runs all 8 tests (count flow judge daily smoke home scroll tutorial). Set `PLAYWRIGHT` (path to the playwright package) and `CHROME_PATH` here: `/home/claude/.npm-global/lib/node_modules/playwright` and `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. Tests that load the real build mark the tutorial as seen; the test build skips it unless `window.__TUT` is set. The test build exposes `__ACH()` and `__save()` too.
- **Sound (v63, `src/sfx.js`):** all synthesised with Web Audio (bells, marimba, sonar with echo, bubbles, rumbles, dark reverb, ocean ambience that darkens with depth). Settings: Sound effects, Ocean ambience, Volume (no preview sound). `SFX.*` calls are wrapped so audio can never break the game.
- **Event categories (v64):** `hw` Halloween Special, `xm` Christmas Special, `ea` Easter Special. Questions in these categories appear only on their holiday (Daily and Unlimited). Holiday Daily Dives are fully themed (HOLI[h].qs). In Unlimited on the day, only unmet event prompts are pushed in (up to two per dive). Year-round holiday-ish questions: k_scary, king, hw_super, hw_phobia, ea_baby, ea_flowers, ea_eggwords, ea_cookegg, ea_rabbits. One-time resets: Halloween 2026 record (v62); Christmas/Easter category stats and prompts (v67).
- **`~LOCK` (v65, splitSix):** in XA batches, everything before `~LOCK` keeps its own tiers; answers after it take exactly the tier of the latest marker (`~P` Plankton, `~S`, `~R`, `~D`, `~T`; default Rare). Use it for every new XA batch, or appended answers shift the original tiers. A `+Name` after a lock is Schooler; duplicates merge their aliases into the existing answer.
- **Variety (v68):** question families (FAMS in app.base.html: startswith, byperson, wordplay, capitals, countries, franchise, sportsleague, myth, breeds, films, music, famous). Max one per family per dive (famous: two), Unlimited avoids families from the last dive, and prompts don't repeat within five dives (`save.hist`).
- **Categories tab (v67):** one goal per category, 50 answers = "Mastered ✓" (MASTER_AT); Special categories don't count toward the total.
- **Marlin achievement (v67):** no longer needs `document.hasFocus()` (focus sits outside the claude.ai frame).
- **Tutorial (v69):** 4-step first-dive intro (`trenchdive.tutorial.v1`); shown once to everyone; Settings → How to play. The countdown waits while it is open.
- **Tier feedback (v69):** "Tier feel wrong?" on the reveal screen → stored in `trenchdive.flags.v1`; Settings → Tier feedback → Copy. Set `FEEDBACK_URL` (repo's issues/new link) for a Send button that opens a pre-filled GitHub issue.
- **Share text:** includes the game's address when played from its own site (not claude.ai).
- **Content:** about 9,000 answers added since v61; jobs 287 → 582; new questions in gen_n17–gen_n23 (event sets, famous cats, units, weather, inventions, castles, queens, gameshows, knots, emojis, wedding, garden birds, square things, classroom, pirates, magicians, yoga, grandparent names, money slang, car parts, hospital, sound words, gym, bags, coats, appliances, salads, puzzles, knives, superpowers, playground, astronauts, kids' TV, holiday destinations, investing apps, pasta dishes, game fish, KFC menu, sports brands, ways to contact someone, outdoor sounds, fishing methods, deep-fried food, golf terms, ways to make money, types of card, Asian cities, meats, titles and ranks). Extra answers in extra_n16–extra_n19.
- **Retired list (drop.js, v75–v76):** King wants small closed lists and niche geography kept. v75 restored 120 questions; v76 retired 15 as too niche (Scottish/Welsh/Turkish/Russian/Mexican cities, New England, G7, G20, ASEAN, Spanish communities, French regions, Nordic-cross and crescent flags, halogens, Muses). Still retired: duplicates of active questions (board games, lakes, cheese, languages, car brands, watch brands, Summer Olympic hosts, martial arts), most NZ-local lists, most single-artist/creator lists, super-niche lists (Canary Islands, Bond/Doctor Who actors, Indian states).
- **Facts checked in Oct 2026:** Spain won the 2026 World Cup; Andy Burnham became UK PM on 20 July 2026 (added to ukpms).
- **Tier overrides added in nzrank.js:** countries (only Nauru, Palau, Antigua and Barbuda, St Vincent, São Tomé are Trench Treasure in k_country; Palestine Rare), jobs, regional answers in the new questions.

**v61:**
- The "Worth N pts: <answer>" hint after each answer is gone (#deepestLine stays hidden).
- Holiday Daily Dives: holidayFor(day) → Halloween (10-31), Christmas (12-25), Easter Sunday (easterDay(), anonymous Gregorian algorithm — checked 2024–2027). On those days dailyQuestions puts two seeded themed prompts (HOLI[h].qs) at positions 2 and 5 among five normal ones. Look: the Daily card is renamed (e.g. "Halloween Dive 🎃") with an accent (--hc); during the dive html.holi-dive tints the quiz card and puts the emoji on the prompt counter; the share card/text carry the holiday name, emoji and accent. Saved results store question ids, so changing a day's set never breaks a finished record.
- Share fix: streak now read from streakInfo().streak (it was always 0).
- Categories re-filed: authors and fictional detectives → Literature, wizards and witches → Mythology, famous paintings → Arts & Culture. New (gen_n16.js): famous battles, famous historical events (History), heroes of legend and folklore (Mythology), famous novels, Shakespeare characters (Literature). Category counts now: geo 56, life 44, ent 41, food 38, sport 29, nat 26, gen 21, words 19, tech 18, music 17, sci 12, cult 11, hist 9, lit 9, biz 9, myth 7, nz 3.

**v60:**
- 364 questions, ~127,600 answers; start-up ~0.5 s.
- Crisp flavours (k_chips) +~100: classics, Rare novelty/limited ones (garlic bread, Marmite, Builder's Breakfast, chicken & waffles, hedgehog…), Kiwi Green Onion (Deep Cut), Lamington (Trench Treasure).
- Birds: the question is now "Name a bird group (e.g. penguin)" (cat nat) with ~200 groups and families added (penguins, owls … bowerbirds, fairywrens, wattlebirds); species still accepted.
- Animals +~230; movies: 2019–2025 releases (the Wikipedia dataset ends at 2018) and world/German/Swiss/NZ/Aus cinema; songs: US/UK rap classics and 2024–25 hits.
- New (gen_n15.js): parts of a watch, parts of a bicycle, parts of a boat or ship, words before 'cake'.
- POST[id]: per-question tweak functions run lazily when a question is first built (add() → build). Use this for anything touching the huge lists (k_movie, w_songs, w_cities…) so start-up stays fast. The raise-only pass at the end of nzrank.js uses it: famous songs/films appended to the huge lists are lifted to Schooler/Rare, never demoted.

**v59:**
- 360 questions, ~126,900 answers.
- New (gen_n13.js): camera settings, territories/dependencies that aren't countries, capitals of states/provinces/regions (not national capitals: US, Australia, Canada, Germany, Switzerland, Austria, UK nations, India, Brazil, Mexico, Spain, Italy, France, China, Japan), places starting with Los/La/El/Las, golf courses (incl. NZ: Cape Kidnappers, Kauri Cliffs, Tara Iti…; Mini Golf is Too Clever), famous watch models (PRX, Overseas, Nautilus, Gentleman, Datejust… plus nicknames like Pepsi, Hulk, Kermit, Snoopy).
- New (gen_n14.js): cryptocurrencies, stock exchanges and indices, famous billionaires, bank accounts/financial products, company/brand mascots.
- Tier overrides: KiwiSaver Rare; Vacheron Constantin Overseas Schooler; Duo the Owl Schooler.

**v58:**
- Daily Dive numbering starts at 29 Oct 2026 = #1 (dailyNumber; it was counting from an arbitrary 1 June).
- Categories tab: button #catBtn under Achievements opens #catSheet. Summary tiles (answers given, top category, best average, categories mastered) and one card per category (CAT_NAMES / CAT_COL / CAT_IC for all 17 codes: geo, gen, nat, sci, tech, ent, hist, myth, lit, food, sport, music, cult, life, nz, words, biz): mastery badge (MASTERY [10, 25, 60, 120, 250] answers → Bronze…Mythic), prompts met / total with bar, answers and average points, tier-mix bar, rarest find. Data: ACHS.stats.catStats[cat] = {n, pts, t[7], best} recorded in achAnswer from now on; "prompts met" uses stats.prompts. New achievements Specialist (answers in one category: 25/60/120) and Polymath (categories with ≥10 answers: 3/6/10).
- Corner buttons (settings, achievements, categories) stay until 520 px of scrolling and hide only while scrolling down; they return on any scroll up.
- Achievement thresholds retuned (Too Clever max 10; hard ones lowered, easy first levels raised). On load, any level already reached under the new thresholds is unlocked quietly (dot shown, no toast flood).

**v57:**
- Too Clever now means only "surprising but technically correct" (e.g. banana for a berry). All pun-style "!" answers from v46–v56 files were removed (388); 21 genuine ones kept (Lucille Ball, Taco Cat, Bear Grylls, Pancake, Trojan Horse, Olympia, Cauliflower…), 20 turned into normal answers. clever_real.js adds real ones: berries (banana, tomato, avocado, aubergine, watermelon, pumpkin, cucumber, chilli, kiwifruit, persimmon), dinosaurs (chicken, birds, pigeon, ostrich), island nations (Australia), Europe (Kazakhstan, Azerbaijan), Asia (Egypt), capitals (Vatican City, Monaco), organs (skin). Deserts (Antarctica, Arctic) and lakes (Caspian/Dead/Aral Sea, Sea of Galilee, Salton Sea) are marked by a post-pass at the end of nzrank.js that matches any alias via coreOf(norm()) — CLEVER[] only matches the first name's core form.
- Restored the small questions the user wants: countries starting with A/B/C/G/I/L/M/N/P/T, US states starting with M/N, US states bordering Canada, Oceania capitals, NZ prime ministers, Will Smith films, NATO alphabet. (The letter/state/Oceania ones had been dropped by an older session's "under 25 answers" rule; a checking script that ignored capital letters made them look live.)
- Trench Dive animals: every creature is its own entry (Dumbo Octopus, Barracuda, Manta Ray, Fish, Starfish, Marlin…).
- Daily Dive sharing: "Share result" on Daily results opens a sheet (#shareSheet, at page level) with a preview card (Daily #N since 2026-06-01, date, depth, points, rank, glowing tier bubbles, streak) and spoiler-free text (⚪🟢🔵🔴🟣🟡, ⚫ pass). "Share…" uses navigator.share where available; "Copy result" tries navigator.clipboard, then execCommand('copy'), then selects the text with instructions. Verified: copy works, Esc closes.

**v56 — quality pass:**
- 332 questions, ~125,800 answers.
- Restored genuine titles ending in "?" that the old clean-up dropped (Do They Know It's Christmas?, Do You Hear What I Hear?, Mary, Did You Know?, What Child Is This?, Who's the Boss?, Are You Being Served?, Would I Lie to You?, Who Wants to Be a Millionaire?, Are You the One?, Wer wird Millionär?) with tier overrides. From now on unsure items are marked with "? " (question mark + space) and the clean-up regex only removes those: re.sub(r'\|[^|"]*\?\s+(?=[|"])', '', s).
- Retired weak questions: country-starting-with A/G/I/L/N/P/T, US states starting with M/N, US states bordering Canada, Oceania capitals, NZ prime ministers, NZ films, Will Smith films, NATO alphabet. "Martial art" merged into "combat sport" (its answers carried over).
- Too Clever added to big everyday questions that had none (extra_n14.js): singers (Singer sewing machine), capitals (Capital One), animals (Party Animal), countries (Country Music), movies, TV, cartoons, cars, colours, elements, trees, instruments, actors, footballers, athletes (Athlete's Foot), superheroes (Super Bowl), fruit.
- New (gen_n12.js): animals in Trench Dive (this game), Duolingo leagues (Bronze/Silver/Gold Plankton … Diamond Tournament Semifinals/Finals TT), words before 'fly', words ending in '-ology', words after 'fire', words before 'board', words that rhyme with 'blue', words/phrases starting with 'water'.

**v55:**
- 329 questions, ~125,400 answers.
- Balance check: lists should lead with US/UK answers (what most players guess); Swiss/German/NZ/Aus extras go in the tail.
- Rappers +~230 (US: East/West Coast, South, Chicago drill, underground; UK/Welsh: Ren (Rare), Ocean Wisdom (Deep Cut), The Streets, Wretch 32, Little Simz…); rock bands +~260 (punk/hardcore/ska/pop-punk/street punk from ~R incl. Rancid, Street Dogs, The Ticking Bombs, Stick to Your Guns; Kiwi bands ~D; The Rabble and Flirting with Disaster ~T); school subjects +~90 (Human Performance, Sports Studies, US/UK staples; Recess and Lunch are Too Clever); TV shows +US/UK (talk shows, panel shows, UK classics); athletes +US/UK.
- New (gen_n11.js): classic American food, classic British food, words containing 'cat', things with a shell, sticky things, countries with two-word names, things in a wallet.
- Icons: AIC.octopus is a faceless deep-sea silhouette (mantle, swept ear-fins, webbed skirt with curled arm tips); the Too Clever flying fish has a sleeker body, asymmetric forked tail, ray-lined wing and eye.
- Known casualty: the "drop answers flagged with ?" cleanup regex also strips genuine titles ending in "?" (e.g. "Would I Lie to You?"). Use a different marker for unsure items in future batches.

**v54:**
- Corrections always ask: a near-miss never counts by itself. With "Suggest corrections" on (SET.autocorrect), submitAnswer offers the single closest candidate (closestTo: edit distance via dl() over names and aliases) in a redesigned card — "Did you mean", the suggestion large with differing letters highlighted (diffMark: LCS, case-insensitive), "You typed" struck through, "Yes, use it (Enter)" / "No, keep typing (Esc)"; springs in, fades with Calmer motion; key hints hidden on touch screens. Capitals, accents and punctuation never trigger it (they already match exactly). With the setting off, near-misses are just "not on the board". Settings and Bearing text updated.
- Abyssal Visitor is a single-level achievement (saved levels above an achievement's max are clamped on load).
- Boats: launch, tender, skiff, scow, wherry, barque, waka ama, va'a, proa and ~40 more.

**v53:**
- 322 questions, ~123,900 answers.
- Achievements sheet renders one heading per group (Rarity, Diving, Daily, Skill, Ocean) — renderAch sorts ACH by group (newer achievements had been interleaved, so headings repeated).
- Icons redrawn: AIC.octopus (dumbo: dome head, ear-fins, scalloped skirt, eyes with highlights) and AIC.gauge (Into the Abyss: surface wave, plunging arrow, fading depth marks).
- New (gen_n9.js, gen_n10.js): famous authors (incl. German/Swiss/NZ), cat breeds, horse breeds (incl. Freiberger, Haflinger, Kaimanawa), pastries (incl. Gipfeli, Franzbrötchen, Golatsche), famous movie characters, famous rappers (incl. NZ/Aus/German/Swiss), words before 'man', famous wizards and witches (incl. Bibi Blocksberg, Die kleine Hexe), famous robots (real or fictional), famous dogs (real or fictional, incl. Barry the St Bernard, Hachikō).

**v52:**
- 312 questions, ~122,600 answers.
- Night Owl now counts dives finished 10pm–4am.
- New (gen_n8.js): words after 'sun', famous paintings, things in space, Halloween, famous bears (real or fictional), types of cake, words that rhyme with 'night', famous horses (real or fictional), things that are cold.
- extra_n11.js: European football clubs (+~300 incl. full Swiss Super League, German 1st–3rd tier, Austrian, Scandinavian, Balkan…), LEGO themes, Mario characters, Harry Potter characters, Disney villains, body parts, kitchen, garden shed, apple varieties (incl. Swiss/German), boxers.
- NZ_TIER additions via Object.assign: famous bears (Knut Rare, Wojtek Deep Cut), famous horses (Phar Lap/Winx/Makybe Diva/Black Caviar Rare, Sunline/Carbine Deep Cut, Kiwi TT), Swiss/German cakes and apples → Deep Cut.

**v51:**
- 303 questions, ~121,200 answers.
- Timer: Unlimited defaults to 30 s (one-time switch from the old 45 default, flag trenchdive.timer30); the Daily Dive is 30 s; tagline and Settings text updated; tests/judge.js expects 30 as default.
- Unlimited dives prefer questions you've never met (ACHS.stats.prompts), falling back to the usual fresh pool once fewer than 11 unseen remain. (With ~300 questions, a given question had only ~2–3% chance per dive before.)
- New achievements: Night Owl (dives 11pm–4am), Early Bird (5–8am), Marathon Session (dives in one day), Clutch Finish (Trench Treasure on the last prompt), No Passes, Deep Diver (total metres), Abyssal Visitor (watch the trench-floor dumbo ≥4 s, on screen, focused, no sheet open), Wings Over Water (flying fish launch in view). New icons in AIC: moon, sunrise, calendar, clutch, shield, anchor, octopus.
- New question styles (gen_n7.js): animal sounds, words before 'ball', words before 'house' (answers accept the first word alone, e.g. "Foot"), palindromes, famous duos, fictional detectives (incl. German TV), things that come in pairs, things that have keys, things at a fair or carnival.
- extra_n10.js: mountains (+~120 incl. Hakarimata → Trench Treasure, plural accepted), rivers (+~150 world), athletes, singers (incl. NZ/German/Swiss), sitcoms (incl. UK/Aus/NZ/German/Swiss), clothing brands (incl. NZ/Aus/German/Swiss).
- Gotcha: NZ_TIER is an object literal — a duplicated key silently drops the earlier one. Merge extra overrides with Object.assign (see the end of nzrank.js).

**v50 — content overhaul, part 5:**
- 294 questions, ~120,100 answers.
- New (gen_n6.js): famous YouTubers (282; MrBeast Plankton, TJR Schooler via ~S, Togi Rare via ~R, German/French/Spanish/Brazilian/Indian/Japanese creators from ~D), famous fishing spots (Lake Taupō, Bay of Islands, Tongariro River overridden to Rare), ski resorts / ski fields, famous chefs, famous comedians (incl. NZ, German and Swiss).
- extra_n9.js: round things (+~330 incl. sinkers, feijoas, the Greenwich time ball, contact juggling balls; all from ~R), cartoons (world classics; Pingu/Heidi/Maya the Bee etc. in the tail; Swiss/German block — Globi, Papa Moll, Die Maus, Sandmännchen, Pumuckl, Benjamin Blümchen, Bernd das Brot, Käpt'n Blaubär… — from ~D), fairy tales & nursery rhymes (Grimm under English + German names from ~R, Andersen, German legends, English rhymes; German nursery rhymes from ~D), Africa (historic/alternative names), inventors (incl. German/Swiss/NZ), Christmas songs (incl. German carols, NZ/Aussie ones), reality TV (incl. German formats).
- NZ_TIER (nzrank.js) is a general per-answer tier override by question id: l_stripes Okapi → Deep Cut; fishingspots NZ spots → Rare.

**v49 — content overhaul, part 4:**
- 289 questions, ~118,700 answers.
- New (gen_n5.js): F1 World Drivers' Champions (incl. Lando Norris, 2025), Olympic host cities (Summer + Winter, incl. Milan/Cortina 2026, Brisbane 2032), Ballon d'Or winners (men + women, to 2025), F1 teams past and present (w_f1teams; the old dropped "f1teams" id is in DROP).
- Landmarks question now reads "Name a famous landmark or tourist attraction" and has ~550 answers (worldwide + NZ: Hobbiton, Waitomo, Hamilton Gardens, Cathedral Cove, Mauao…).
- Batch E (extra_n6.js, nature): insects (giraffe weevil…), amphibians, snakes, sharks, whales/dolphins, primates, rodents, marsupials, birds of prey, dinosaurs, extinct animals, nocturnal and striped animals, zoo animals, pets, farm animals, rocks, gemstones, volcanoes, waterfalls, mountain ranges, deserts.
- Batch F (extra_n7.js, tech/everyday): card games (Monopoly Deal, Jass, Schafkopf…), Apple products (2025 iPhones; "iPhone Duo" added on the user's word, ~D), consoles, operating systems, browsers, social media, phone brands, PC parts, streaming services, tech companies, materials, tools, furniture, bathroom, office, camping, beach, shoes, hats, things with wheels / that fly / that are scary / yellow / round, fridge, breakfast, rooms, chores, school subjects.
- Batch G (extra_n8.js, food/culture): Italian, Japanese, Mexican, Indian dishes, breads, sauces, pasta, pizza toppings, sandwiches, soups, teas, coffees, spirits, beer styles, cereals, mythical creatures, painters, musicals, museums, stadiums, bridges.

**v48 — content overhaul, part 3:**
- 285 questions, ~116,300 answers; start-up ~0.4–0.7 s.
- Duplicate questions merged: old "cheese" → cheeses, old "boardgames" → w_boardgames (my new one had the same id as an old add() question). extra_merge.js carries their old answers over; both old ids are in DROP.
- New random-style questions (gen_n4.js): countries with 'land' in the name, animals starting with Q, things that are purple, stone fruit, words that rhyme with 'cat', plus beer brands (NZ/Australian beers ranked Rare+ for a global viewpoint).
- Big expansions of everyday questions (extra_n4.js, extra_n5.js, helper XA(id, list) appends to EXTRA): drinks, snacks, desserts, jobs, landmarks, hobbies, dances, fast food, soft drinks, chocolate bars, cocktails, ice cream flavours, holidays/festivals, transport, birds, dog breeds, insects, flowers, fruit, vegetables, spices/herbs, airlines, supermarkets, toys, video game franchises, superheroes, clothes, luxury brands. Anything I wasn't sure was correct was left out.
- Check for duplicate ids: the live question list must have unique ids (old questions use add() in app.base.html as well as A() in the gen files).

**v47 — content overhaul, part 2:**
- ~115,000 accepted answers. New question: golf clubs (gen_n3.js).
- Local places (extra_local.js): Waikato / Bay of Plenty / Auckland lakes, reservoirs, towns, suburbs, rivers and peaks, plus the retired Kiwi lists (NZ lakes, North/South Island towns, Auckland suburbs, NZ rivers, NZ mountains) reused as extra answers on w_lakes, nzcities, rivers and c_mountains. They rank in the tail (Rare → Trench Treasure: a global viewpoint).
- Country city questions now say "Name a town or city in …" (NZ: "town, suburb or city").
- The old "lakes" question is retired; its EXTRA is folded into w_lakes.
- More answers on existing questions (extra_n2.js, extra_n3.js): cheeses (+~250 niche, from ~D), AIs (+~300: model versions from ~R; McDonald's AI, Hark AI and the long tail from ~D), animals (+~280), tennis (+~150), NBA (+545 from a roster dataset), footballers (+~200), TV shows (+~280), actors (+~230), car models (+~200), F1 drivers (+~90).
- Rank markers now include "~S" (at least Schooler): ~S / ~R / ~D / ~T.

**v46 — content overhaul, part 1:**
- 281 live questions, ~113,000 accepted answers (was ~28,500).
- Big lists from open data, generated by tools_gen_big.py (needs /tmp/ds with npm all-the-cities + iso-639-3 and the downloaded datasets; see the script): src/big_extra.js (EXTRA for k_movie +20k Wikipedia films ranked by article length; uscities/ukcities/austcities/cancities/japancities/italycities/frcities/nzcities = all towns above a population threshold, by population) and src/gen_big.js (new: w_cities 23k world cities, w_lakes 747, w_languages 7.9k ISO 639-3 + hand-ranked head with dialects/creoles/Pacific languages, w_sp500, w_music 8.8k artists by Billboard weeks, w_songs 13.8k songs by best chart run). Each starts with a hand-ranked head of the obvious answers.
- New hand-made questions (src/gen_n1.js, gen_n2.js): animal groups, watch brands, fish, board games, currencies worth < US$1, countries with English as an official language, hairstyles, 2025 memes/trends, combat sports, aircraft, AIs, things you can measure in your body, cheeses, German/Austrian/Swiss food, one-word animals containing "ck", football jargon. src/extra_n1.js adds ~300 sports (incl. hornussen, schwingen, sepak takraw…), ~190 golfers (incl. women) and ~100 boat types.
- Too Clever now exists: "!Answer" items (starfish/jellyfish for fish, Baywatch for watches, gravy boat, Hamburger/Swiss Roll for DACH food, Touchdown for football jargon, Al Pacino for AIs, herd/pride for animal groups…), a few per question.
- Tiering (splitSix): small lists keep percentages; big lists cap Plankton at 35 and Schooler at 120 (Rare ≤300, Deep Cut ≤700), so the long tail is Trench Treasure. Hand-ranked lists can now use markers "~R" / "~D" / "~T": everything after is at least Rare / Deep Cut / Trench Treasure.
- Questions are built lazily (add() stores raw text; buildQ() parses on first use; getters/setters on entries, map, core, flat, keys, tok, topTier, tops). Start-up script ~0.6 s (was 1.9 s with all answers); the 23k-city question takes ~0.4 s the first time it's played. EXTRA can now live in any file.
- Retired: Kiwi-specific questions (birds, slang, te reo, native animals/trees, Auckland suburbs, NZ towns/beaches/mountains/lakes/rivers, All Blacks, Black Caps, Kiwi brands/food), x_nrl, pkmnstarters, eyeparts, and the old 221-answer "languages" (replaced by w_languages). NZ_TIER: Spark, One NZ, 2degrees → Deep Cut on the phone-network question.
- Gotcha: older questions are defined with both A(...) and add(...); the first definition of an id wins, so give new questions fresh ids (new ones use w_ or descriptive ids).

**v45:**
- Treasure chest on the trench floor (CHEST, drawChest at the end of drawSeabed): an open wooden chest (lid tipped back, dark inside, gold straps, rim and lock plate) with a heap of shaded gold coins, a few spilled on the sediment, a warm pulsing golden glow, twinkles and rising motes (static glow only with Calmer motion). Sits at ~0.66–0.7 of the width, sized to the screen.
- Deep dumbo octopus (DEEPDUMBO, updateDeepDumbo before drawSeabed): only while the floor is on screen; one at a time; first after 25–60 s, then every 40–90 s after the last leaves. It drifts in from off screen (18–32 px/s) and out the other side, with a soft pink glow so it reads in the dark. Its depth stays ≥ 6,900 m and above a ceiling clear of the floor's highest ripple and the chest's lid (allowing for its size and bob); every frame it also glides down, where there's room, to stay clear of the sub. Measured: 7,000 m+, clears the floor by ~80 px and the chest by ~57 px when passing over it.

**v44:**
- Front Row Seat (marlin catch) only counts if it was really watched: during the catch, time is accumulated only while the marlin is clearly inside the screen (x 60…W−60, y 80…H−80), no sheet (achievements/settings/surface) is open, the tab is visible and the window focused; it counts at the gulp only if it's being watched then and was watched for ≥2 s. (Before, only x was checked, so a catch above or below the visible area, e.g. with the dashboard scrolled, could award it.) Verified: watched counts; scrolled to the edge and panel-open don't.
- One new flame everywhere (teardrop with an S-curved tip and an inner flame): STREAK_FLAME (dashboard chip, orange→gold gradient with a pale inner flame and a double glow), FLAME_SVG (results orbs, white with a golden core), AIC.flame (Unbroken achievement, monotone with a translucent inner flame).
- Marlin achievement icon redrawn as a real marlin: spear bill, tall sail-like dorsal sweeping back, crescent tail, pectoral fin.

**v43:**
- Flying fish redrawn simpler: one clean silhouette (no eye): spindle body, forked tail that bends from its base, a far fin behind and a near fin over the body (folded fins lie along the side when swimming). flyfishShape(s, wing, t, ph, air, tb), where tb is the tail-beat strength (hard while swimming, rising or taxiing on the surface; resting in a glide). Fins unfold with a small overshoot (f.wo), flex gently in the glide, and fold quickly before re-entry; a faint wobble in the air. Smaller (school 22·s, flyers 24·s).
- Rarer: 2 schools (was 3), first appearance after 40–180 s, away 90–180 s after swimming off.
- Too Clever tier symbol is now a glowing monotone flying fish (Bearing SVG; the result reveal, achievements and results copy it from there).

**v42:**
- Flying fish (type 'flyfish', 3 schools of 5–9, pinned 5–14 m below the surface, fast: sp 14–22). Rarely seen: they start hidden and, after swimming off, stay away 40–90 s (rewander). About 10% of marlin visits (when the camera is shallow) target a flying-fish school, bringing it in from the side. On the strike launchFlyers() sends ~55% (at least 2) into the air (FLYERS): angled rise underwater → splash → fins snap open → a low glide (peaks ~70 px, up to ~3.5 s, tail sculling the surface), often one skip (small splash), then a splash back in. The rest flee underwater; the school stays away 45–75 s and returns just out of sight at its own pace (c.caught path). Flyers and splashes are drawn after drawSky/drawBirds (the sky is painted after the creatures and would hide them). flyfishShape(s, wing, t, ph, air) draws both the swimming (folded) and flying (spread, darker silhouette, outlined fins) forms.
- Schools vary from 4 to 14 fish (c.n). Slightly fewer animals near the surface (zone gap 175 px, one extra small school instead of two).
- Entering animals keep a constant speed: no cruise-in boost; enterFromEdge places them 0.6 of their margin off screen (0.5 after a catch).
- Daily results from the dashboard: the camera starts at the surface, the results page is held while it sinks to the dive's depth (settle sets target = S.wrapDepth; it was never being set, so the sink wasn't happening), and it fades in at ~95% of the descent. Measured: 0 → 4,200 m in ~3.8 s, results appear at ~4,190 m.

**v41:**
- Animals never turn around (turnAt 0; no off-screen flips either). The c.turn animation code remains but is unused.
- Unlimited timer options are 30 / 45 / 60 s (default 45; an old saved 90 becomes 45).
- Removed completely: the Ask Claude judge (JUDGE, judgePrompt, judgeAnswer, the settings row, the note, the "No, I meant…" option, the "checked by Claude" tag) and the Google search link. Unlisted answers just say "not on the board". tests/judge.js now tests this, the timer options, and achievements.
- Dashboard → dive: the camera snaps to 0 m at the page swap (no glide from the dashboard's scroll depth).
- One-time reset of today's Daily Dive (flag trenchdive.dailyReset.v41).
- ACHIEVEMENTS (localStorage trenchdive.ach.v1 = {stats, lvl, unseen}). 18 achievements / 72 levels in five groups (Rarity, Diving, Daily, Skill, Ocean), levels Bronze → Silver → Gold → Platinum → Mythic (LV_COL). ACH defines id, icon (tier icons t0–t5 reuse the Bearing SVGs, others in AIC), stat, level thresholds and desc(n). achFresh() backfills from existing saves (lifetime tiers, dives, daily done, best streak/depth, total points) and unlocks those quietly. achAnswer(q, r) runs in finishPrompt (tier counts, quick ≤5 s, buzzer ≤3 s left, categories, prompts seen); achDive() runs in finishDive (dives, daily, streak, depth, points, clean sweep, trench floor, most TTs in a dive); the marlin catch counts when its gulp happens on screen. achCheck() queues a toast for every new level. Settings → Reset also clears achievements.
- UI: trophy button under the settings gear (fades on scroll with it; pulsing dot when something new is earned). Achievements sheet: summary + overall bar, grouped cards with ringed icon in level colour, pips, next-level description, animated progress bar and count; cards stagger in. Toasts: one at a time, bottom right on desktop (slide in on a springy curve, icon pops with sparkles, a shine sweeps across, slide out after 4.8 s); on phones they drop in from the top so they never cover the result or buttons. Calmer motion: fade only.

**v40:**
- Page arrivals: the staggered riseIn animation (which fought the HUD/card uiBob animation and jolted) is replaced by transitions: .arriving (start state) → .settling (eased move). On the quiz the HUD and surface button settle down from the top and the card glides up 120 ms later; other pages ease up as one. The card no longer changes size during the countdown: the answer area stays in the layout (invisible, disabled) and the countdown is laid over it (positioned each tick, once the page is showing). Measured on Play again: HUD ≤4 px and card ≤6 px per frame (was a 34–111 px snap).
- Turning around: c.turn animation (1.1–1.8 s): the animal slows to a stop mid-turn, narrows to edge-on (horizontal scale |cos|), flips at the midpoint (position kept) and picks up the other way. Max 2 px/frame.
- After a marlin catch (m.c.caught): the rest of the school keeps fleeing until clear of the screen (scatter floor 0.36 while fleeing), counts as gone when ≥85% of its margin out or when it wraps (rewander), stays away exactly 10 s, then comes back just out of sight (enterFromEdge near=0.5) at its own pace, no cruise-in boost. Ordinary strikes are unchanged (back after 10 s with the brisk cruise-in).
- Squid ink: emitted from the funnel just under the head during a big jet, fired backward past the arms (110–230 px/s, quickly slowing), starting as a thin squirt and blooming into large black clouds.

**v39:**
- Disappearing fish: WRAP_M was smaller than how far some animals actually reach (a fish school's spread, wider still when scattered), so they wrapped/hid while still partly on screen. Margins now cover each animal's full reach (school 210, lantern 120, hatchet 110, barracuda 160, squid 190, eel 230, siph 220…); marlin-scared schools only count as gone once fully off screen. Instrumented check: 0 animals vanished while partly visible at 120/600/2,600/5,600/6,800 m, including with the marlin hunting.
- Marlin catch: room needed ahead reduced to 170 px with harder braking, so catches also happen on phones; MARLIN.forceCatch (test hook) forces one. Verified: every forced catch spends ~2.9 s grabbing/eating/gulping with marlin and fish fully on screen (390 px and 1280 px). Natural odds are 15% of strikes, and a strike only happens every 1–2 min when fish are near the surface, so expect a catch roughly once every 10 minutes on the dashboard.
- Rare reveal ink is red (.ink gradient) and there's much more of it: denser falling trail (every 40 ms, with extra puffs) and a burst of 36 puffs + a three-part billow + two wider follow-up billows.
- Ocean squid ink: the inky burst is now 7% of jets (was 20%); INK clouds are pitch black and dense (alpha up to ~0.97, slower thinning), so they hide whatever is behind them.

**v38:**
- Marlin survives page changes (swap no longer clears MARLIN.m).
- Animals never pop in mid-screen: enterFromEdge() places an animal just off the edge it swims from and has it cruise in (~120 px/s boost, c.enter) until it's in view. Used by the visibility guard, by marlin-scared schools returning, and by rewander, which now hides a wrapped animal for 1.5–10.5 s (c.hideUntil; not drawn, not counted) instead of shifting it along its loop (the old shift could drop it back inside the screen). Measured: 0 mid-screen pop-ins at 150/2,600/5,600 m; still 100% something-in-view.
- Marlin catch (15%, only with ≥260 px of room ahead): the catch logic runs before normal movement (it used to run after it, double-moving the marlin and keeping its 90 px/s floor). It brakes to ~16 px/s within ~100 px with a silvery fish wriggling across its jaws (0.6 s grab), thrashes its head while eating (~1.8 s), gulps (the fish shrinks, scale flecks drift up), then accelerates away (drawMarlin overlay + drawMarlinBody).
- "Worth 100 pts: …" is shown for every result except a Trench Treasure and in the Daily Dive. When space is tight the stage lifts, then goes .compact (smaller icon and title), then drops only the short description line, never the worth line.
- Squid rework: cruise on rippling fins (3–8 s), with a gentle bob and arm sway; then a single eased jet, or (20%) a burst of three strong jets that releases huge purple ink clouds (INK, stored in water depth so they move with the camera, grow, drift and fade over 3–4.5 s). Giant squid event removed (GSQ gone; ink drawing kept as drawInk).
- Jellyfish: the white sheen patch is removed.
- Periscope ripple: computed where the periscope mast actually crosses the moving waterline (wave formula at that x, with the sub's bob and tilt). Drawn only when the mast truly breaks the surface and the sub is settled at the surface (cam 0, no tween/rise/intro, not moving). Three gently expanding rings, a foam patch and fizzing bubbles.

**v37:**
- "Play again": beginDive keeps the camera deep (updateHud(true) used to snap it to 0); show('dive') from the results page sets scene.rise and holds the quiz page (.screen.hold) while the camera follows the sub up (sub glides from its results spot to its quiz spot; stays on screen); the page fades in at ~92% of the ascent; the countdown waits for the hold to clear (and starts from blank text).
- Gannets more solid (0.94 / far wing 0.72).
- Fewer schools at the top (zone gap 150 px, 2 extra small schools); lane spacing for solid animals is a full body width + 6 px (0 overlaps); drifting jellies may come to 0.8; vertical wander reduced to 4–14 px.
- Squid: only 2 seeded and none from the gap-filler; WRAP_M squid 170 (eel 190, siph 180) so they leave/enter fully off screen; squid, whales and eels never turn mid-screen and are never chosen by the visibility guard.
- More jellies (34 scattered from 900 m) and more lanternfish/hatchetfish in 1–4 km (gap 400 px); jellyfish brighter (stronger glow, bell 0.68, tentacles 0.72, a sheen).
- rewander(): when an animal wraps off one edge it stays away a random while (xo shift), comes back at a slightly different depth (±~35 units from home, not for free jellies), and 35% of the time turns round to re-enter from the side it left. Measured: 0 of ~100 exits reappeared on the opposite side within 1.5 s.
- Giant squid event (GSQ): every ~70–150 s on the quiz/results pages between 1,000 and 5,500 m, a 2.6× squid (drawSquid) with a pink glow rockets across in ~1 s jet pulses (≈150→1,100 px/s), routed ≥150 px above or below the sub, trailing purple ink clouds that billow and fade.
- Marlin-scared fish return after ~10 s.
- build.py now syntax-checks the built script with node --check and fails the build on errors (it caught a comment that had swallowed code again).

**v36:**
- Darkness: water STOPS now darken much sooner (deep blue by 400 m, dark navy by 800 m, near-black from ~1,500 m) and stay dark to 7,000 m. Sub lights are fully up by ~1,600 m; sun rays fade by ~550 m; animal depth fade over 2,500 m.
- Fauna, far less regimented: fillGaps() now has zone densities (≈15 animals per screen in 0–300 m, ≈4–5 below) with uneven allowed gaps and random placement inside each gap; 26 jellyfish scattered randomly through 1,100–6,700 m (c.free, they may share depths); 5 extra small schools near the surface; speeds vary 0.25–1.55×; most animals wander slowly up and down (c.ma/c.mf); animals turn around now and then (turnAt, position-preserving flip of dir via xo). Lane relaxation keeps only big silhouettes apart ((h1+h2)·0.62), and skips free jellies. Squid only below ~1,050 m, rarer, brighter (rgb 176,74,140 at 0.82) with a faint pink glow. Gulper eels and anglerfish bodies lightened so they read in the dark. Marlin-scared schools return after ~10 s.
- Trench floor: 6 tall swaying kelp strands with alternating blades and 14 seaweed clumps (KELP, seeded), drawn behind the starfish and urchins.
- Dive: slower and calmer. Tween 1.7–4.8 s with quadratic ease-in/out and only a 1.2% whisper past the mark; dive angle capped at ~0.3 rad (measured 5° for a Schooler, 14° for a Trench Treasure); braking nose-up ≤0.07 rad; pitch spring near-critically damped (22 / 9.4); smaller hop (4 px), settle bob (2.5 px) and sway (4 px).

**v35:**
- Root cause of "the ocean disappears at ~1,500 m": colorAt() and an old drawFloor() were still on the pre-stretch scale (0–2,800 units). The old floor rose into view at ~1,400 m and blacked out everything beneath it. drawFloor is removed; STOPS are now in metres (bright for longer, deep navy by 6,000 m, near-black only at 7,000 m) and colorAt takes metres. The sub's lights (dark), sun rays (to ~1,600 m) and animal depth fade are also in metres.
- New trench floor (drawSeabed): it sits just below the 7,000 m mark and only rises into view at the very bottom (80% down the screen at 7,000 m). Sediment gradient, a faint rim of light, rocks, 9 glowing starfish (pulsing, 5 colours) and 6 sea urchins (swaying spines with glowing tips). Fixed layout from a seeded RNG.
- Blobfish (drawBlobfish): a saggy pink blob with a drooping nose, grumpy mouth, tiny eye, fluttering pectoral and waggling tail; it jiggles as it drifts. Spawned from 6,500 m down and used by the gap-filler there.
- Gannets: a flap amount b.fa eases between flapping (1) and gliding (0). The wings finish their stroke into the glide; wing angle, wrist lag, body lift, rock and tail all blend, so nothing snaps. Glides sway and trim more.
- Marlin-scared schools that leave the screen get c.away = 70 s: not drawn, not counted by the visibility guard, and not chosen to swim back in.
- "Time's up" / "Passed" titles are white.
- Turtle front flippers ~13% shorter.
- More animals: gap-filler max gap 160 px; more fish schools near the top (≈206 animals, ~7 per screen; 0 lane overlaps).

**v34:**
- Sub body language now uses vU = scene.vel / DS (speed in the old scale). After the 5x stretch, the raw speed had saturated pitch, lead, propeller spin and the bubble trail.
- Dive animation: a short buoyancy hop before each dive (lift + nose-up, 0.48 s, from diveTo); springy pitch (spring 38, damping 8.5) so it overshoots and settles; a nose-up flare while braking (from smoothed acceleration); side-to-side sway scaled by speed; ballast-tank bubbles venting along the hull while sinking; a damped settling bob when a dive ends (scene.settle).
- Bug fix: the bubble update line had a comment swallowing "b.x += …; b.life += dt", so bubbles never wobbled.
- Marlin only hunts in bright water: target schools above ~300 m and the camera above ~350 m. It used to scatter schools down to ~900 m, where its dark silhouette is invisible, so fish seemed to bolt for no reason. Lanternfish darts are rarer and gentler.
- Twilight zone: lanternfish, hatchetfish, jellies and squid now start around 500–750 m; ordinary fish schools stay above ~750 m; barracuda 300–1,000 m.
- Always something to see: fillGaps() adds zone-appropriate animals wherever more than ~230 px of empty water separates two animals (down to the trench floor), and loopX now wraps each animal type with a size-based margin (WRAP_M) instead of a fixed 180 px, so small animals spend less time off screen. A live guard checks every 0.25 s and, if nothing has been in view, places the nearest animal at this depth just inside the edge it swims from. Measured in the live game: 98–100% of the time something is in view at every depth on 360–1280 px screens, with gaps of at most ~0.2 s. ~141 animals, 0 lane overlaps.

**v33:**
- The ocean is 5× taller: DS = 5, SCENE_K = 2800·DS / 7000 m = 2 scene units per metre, i.e. 3.4 px per metre on screen. A 100 m Plankton dive scrolls ~340 px; a 1,000 m Trench Treasure dive scrolls ~3,400 px. spawn() multiplies its (old-unit) bands by DS; every other depth threshold (darkness, light rays, depth fade, marlin range, lane clamp) is scaled by DS. Dive tweens retuned (1.2–3.8 s), ascents 1.6–3.6 s.
- Animals spread over the taller ocean, so there's open water between encounters (measured: 0–5 animals per screen depending on depth). A few more fish schools, jellies and lanternfish so it isn't empty. Lanes: 0 overlaps.
- Leaving a quiz or the results page: the camera follows the sub the whole way up. scene.rise records the sub's on-screen spot just before the page swap (in swap(), not later, which used to let it snap to its far-off surface spot); the sub glides smoothly from there to its waterline spot over the ascent, nose up, staying on screen (measured 284–398 px; at most 3 px per frame). The dashboard is held (.screen.hold) until ~66% of the ascent, then floats in.
- Gannets keep flying while the sky is scrolled out of view (updateBirds runs every frame; new birds only spawn when the sky is visible).

**v32:**
- Deep animals: the depth fade floor rose from 0.12 to 0.62, so silhouettes stay clearly visible all the way down.
- Every dive feels deeper: diveEase sinks further past the mark (0.075), near particles move at 3.2× camera speed going down, and a "rush" layer adds 12 long light streaks racing upward plus a darkening vignette, both scaled by descent speed (off with Calmer motion).
- Leaving a quiz (to the dashboard): subFx makes the sub shoot up nose-first (~0.5 s) and ease back down into place (1.8 s total) while the camera rises quickly (0.9–1.8 s). No bubble trail while rising, and near particles don't streak upward. scene.arriving holds the camera for the frame between the page swap and the glide starting (it used to snap to the surface).
- Unlimited card shows "Your best dive" with best points and depth (or "None yet, go set one") in the same two-line slot as the Daily countdown.
- Lesson: a code comment pasted mid-line silently commented out the rest of that line; node --check on the extracted script found it.

**v31:**
- Falling answers now travel to near the bottom of the screen (62–100% of the room below the sub by tier), shrinking to 0.86–0.54 and dimming as they go, so each answer looks like it sinks much further. Visual only.
- Plankton colour lightened to #d3dde6 (CSS --t0 and TIER_HEX[0]).
- Bearing/reveal icons: Rare is now a squid (arrowhead fins, mantle, eyes, arms and two long tentacles); Trench Treasure is a detailed open scallop with ridges, a hinge, a shaded and highlighted pearl, and two sparkles (currentColor + white).
- Bigger reveal bursts: Rare = 22 ink puffs + a three-part main billow + a second wider billow; Deep Cut = stronger flash and three expanding rings with 26 sparks; Trench Treasure = 26 coins (some larger) in a wide fountain, a flash and gold glints.

**v30:**
- Falling answers travel further (reach × 1.1/1.2/1.5/1.7/1.9/2.05 by tier, capped above DESCEND) and shrink slightly with depth, so higher tiers look like they sink deeper. Scores and real depth unchanged.
- Tier trails: Plankton, Too Clever, Schooler and Trench Treasure trail bubbles; Rare trails soft, curling ink puffs (inkPuff); Deep Cut pulses with a glow (.glowfall) and leaves glowing motes (glowMote).
- Reveal bursts (revealBurst, centred on the stage icon once it appears): Rare = a swirling ink cloud; Deep Cut = a faint flash, two expanding rings of light and sparks; Trench Treasure = a flash and 9 spinning gold coins that arc out under gravity and fade. Clouds/glows are drawn on #fxUnder (behind the result text); sparks and coins on #fxLayer (in front).
- Measured timing: the result appears ~2.2–3.1 s after answering, just after the sub stops.

**v29:**
- No more screen wipes: show() fades the old page out (220 ms, .leaving), swaps, staggers the new one in, and the camera/sub glide to where the new page needs them (startDescent works up or down; the sub eases on arrival, the dashboard only resumes scroll-following once the glide ends). The Daily-results descent uses the same path.
- Bug fix: the Surface button sat inside the HUD, whose bob animation (CSS translate) made it the button's containing block, so the "fixed" button rode on top of the depth readout. It's now a direct child of #dive: top-left at every width (scanned 320–1920 px, no overlap).
- New answer flow: the card sinks/fades away (.q-card.gone); fallAnswer() drops your answer with a "YOUR ANSWER" pill (tier colour, glowing unless Plankton) from just below the sub into the card's space, trailing bubbles; sway amplitude 30→3 px and a faster, accelerating fall for Deep Cut/Trench Treasure; it settles, waits for the camera to finish, fades. Then showStage(): glowing tier icon, tier name in caps, your answer, "+x points · sink y m", a short line (TIER_SAY), and in Unlimited the small "Worth 100 pts" line (dropped only if it can't fit). The block is lifted into free space above if needed so it never covers the sub or the DESCEND box. DESCEND ↓ (FINISH DIVE on the last prompt) is a small fixed box at the bottom whose border takes the tier colour on hover/focus.
- Every prompt (first included) opens with "Descending · the clock starts in 3, 2, 1" inside the card where the text box goes (question visible); then the text box and ring timer fade in and the clock starts. After DESCEND the card eases back up into place. The first prompt also sinks the sub from the surface.
- Marlin: waits off screen (up to 14 s) until its target school is actually on screen; sprints from a screen-relative distance with a stronger (still eased) kick, so it hits at ~650 px/s on phones and ~1,100–1,230 px/s on desktop; wider hit radius; fish scatter harder (bigger burst, more vertical spread) and flee faster for longer.
- Test builds set window.__FAST (short countdown and fall) so the suites stay quick.

**v28:** animation & transition pass.
- Page transitions: the veil is now a rising wash of water with bubbles (on → swap at 340 ms → out upward), and every new page's children rise in, staggered (.screen.enter, --n).
- Daily results from the dashboard: show('result', { descend: true }) skips the veil and runs startDescent(): a 1.8–4.2 s camera sink (descentEase: quick start, long gentle stop) from the surface to the dive depth, sub nearly level (pitch ≤ 0.12), depth counter counting up in step.
- Quiz entry: S.intro gates the first prompt. The card waits (.q-card.pre), input is locked, the clock doesn't run; "Descending · the clock starts in 3 / 2 / 1 / Dive!" in a panel below the sub (runIntro) while scene.intro sinks the sub from surfaced to its spot over 2.7 s, venting bubbles. Skipped with Calmer motion.
- Circular timer: the seconds sit inside an SVG ring (r 20, dasharray 125.66) that drains, colour aqua → amber (≤50%) → red (≤20%), pulsing when low.
- Buoyant submissions: popSubmission() flies a bubble chip with your answer from the input into the water (WAAPI), bursts DOM + canvas bubbles there, then a tier pop-up with the tier's Bearing icon glowing above the name and "+pts · +m". dipUI() makes the HUD and card dip and spring back (composite: 'add', so it layers on the bob).
- Submerged physics: a foreground parallax layer of 16 particles moving at 1.9× camera speed (streaks while sinking); HUD, card and results cards bob on slow sine animations (CSS translate, so transforms still work). All off with html.calm.
- Dashboard buttons simplified ("Today's dive" / "Same seven for everyone", "Dive any time" / "Fresh prompts every round"; duplicate line removed, countdown on two lines, CTAs aligned), softer glass highlight, bob 8 px.
- Tests: test builds also freeze the new looping UI animations; smoke clicks moving targets with force.

**v27:**
- Barracuda: calmer (surges ~0.07/s per school, smaller impulse, softer damped spring); a surging fish gapes its jaws (mouth cut out with destination-out inside asSilhouette, hinged lower jaw) and white teeth show briefly, then the jaw closes as it settles.
- Dashboard title: more room (padding 64 px top on phones / 46 px desktop, tagline 14 px below), and a continuous gentle wave: the title is split into per-letter spans (.ch, aria-hidden; h1 keeps an aria-label) animated with CSS `translate` (titleWave 3.6 s, staggered). "Dive" colour now on .dive.
- Mode cards bob gently (cardBob 6 s, Unlimited offset by half a cycle) using `translate`, so hover transforms still work. html.calm (set from the Calmer motion setting, kept in sync on save) turns both animations off; prefers-reduced-motion also stops them.
- Tests: test builds disable these two decorative animations (Playwright won't click elements that never stop moving); tests/smoke.js, which runs on the shipped file, clicks the mode cards with force.

**v26:** (also: 'Skip check' on a Claude answer check now takes effect immediately even if the check never answers; tests/judge.js uses a realistic 1.2 s stand-in delay, which fixed an intermittent test race)
- Whale is now a humpback: stocky body with separate top/bottom profiles, flat knobbly head (tubercles), deep throat bulge, blunt rounded snout, small dorsal fin on a hump with knuckles behind it, broad notched flukes with a ragged trailing edge that spread/flex with the stroke, and a very long rounded flipper with a scalloped (knobbed) leading edge (roundBlade()).
- Turtle flippers are rounded paddles (narrow at the shoulder, broad mid-blade, rounded tip).
- Extra motion: jellyfish rise on each bell contraction and sink between (c.jy), tentacles stream on the rise; manta rays alternate flapping and gliding spells with varying pace and gentle banking; fish schools get a "flash" every 8–18 s where a turn ripples fish to fish (narrowing + brightening); lanternfish groups dart (damped spring) with their lights flaring; dumbo octopus drifts further up and down and tilts; hatchetfish bob and tilt together.

**v25:** animal animation pass. Shared helpers: critterDt(c, t) (per-animal frame time), spinePath(L, n, half, cy) (body outline along a flexing spine, rounded nose), finBlade(). Multi-part animals are drawn through asSilhouette() so overlaps don't darken.
- Whale: travelling fluke stroke down a flexing body, flukes angle with the stroke, long humpback flipper sweeping, dorsal hump, occasional breath of bubbles.
- Dolphin: up-and-down tail drive with body flex, porpoising arcs with matching pitch, melon, curved dorsal fin, pectoral, bigger flukes, playful 1.4 s speed bursts every 6–15 s.
- Barracuda: 4 long pale fish holding station, pointed jaws, two dorsal fins, forked tails that flick (faster when darting); random darts with a damped spring back into place.
- Squid: jet cycle (0.32 s squeeze: mantle narrows, surges mantle-first, arms stream together; 1.1–1.9 s coast: mantle refills, arrowhead fins ripple, arms drift apart). Torpedo mantle, 8 arms + 2 club-tipped tentacles. Brighter (alpha 0.62) so it reads in the dark.
- Anglerfish: hinged lower jaw yawns open every ~11 s with needle teeth, waving tail fan, sculling pectoral, dorsal spines, eye glint; lure on a swaying rod that pulses and occasionally flickers bright.
- Snailfish: ghostly tadpole with a wave travelling down a long tail, fluttering pectoral fins.
- Gulper eel: the mouth gapes every ~15 s (jaws open wide with the pouch between).
- Lanes: relaxLanes() after spawning pulls animals toward their chosen depth while resolving any overlaps (0 overlaps at 390–1920 px). Lane sizes retuned (whale 72, ray 50, dolphin 42, squid 26, angler 42, eel 30, jelly 44, turtle 36); counts: deep fish schools 2, lanternfish 4, jellies 7+2, hatchetfish 3. With every animal in its own lane, turtles end up ~350–470 m and the dolphin ~600 m.

**v24:**
- Gannets: each burst picks a fresh beat count (flap 1–8, cruise 1–3) and each glide a fresh length (flap 0.35–2.95 s skewed short, cruise 0.9–3.3 s). Style weights: flap 32, cruise 22, climb 16, trio 15, dive 10, pair 4.
- Fix: hairline of water showing at the left edge of the sky. The wave paths stepped 12 px (6 px for the sun clip) from W down to 0 and stopped short of x = 0 unless W was a multiple of the step; they now finish exactly at the edge (measured: up to 189 colour units bluer before, 2–5 after). The foam line also runs to the right edge.
- Mode cards: text, CTA (auto width, min 190 px) and the line under it left-aligned; icon moved to the right (grid 1fr auto).
- Countdown shown as "03 hours 12 min 09 sec" (hmsLong, numbers bold) on the Daily card and Daily results; wraps as one unit on phones.

**v23:**
- Gannet glides are alive: the wing angle keeps swaying (two slow sine terms plus an occasional correcting half-flap; measured range 0.02–0.28 rad instead of a fixed 0.06), the hand trims, and the body rocks gently. About 1 in 3 flapping birds (incl. pairs/trios) are b.steady and flap the whole way across.
- Turtles rebuilt: stateful stroke cycle per turtle (c.tph). Both front flippers move together: power stroke down-and-back with a broad paddle, recovery up-and-forward feathered edge-on, wrist bend through the stroke; body surges forward (c.xo) and lifts on each power stroke; after 2–4 strokes a 1.3–2.7 s glide with flippers tucked back; rear flippers steer; head stretches with the stroke and slowly looks up/down; longer front flippers; domed carapace with a short tail. Drawn via asSilhouette() (parts at full opacity on a scratch canvas, faded once) so overlapping parts don't show darker patches.

**v22:**
- Gannets: head moves with the body again. 'away' removed. Weighted style mix that never repeats back to back (measured over 2,000 visits: flap 25%, cruise 21%, climb 17%, pair 15%, dive 12%, trio 10%). cruise = 2–3 beats then 1.4–2.6 s glides with gentle drift; climb = steadily gains or loses height with matching pitch; pair = two birds 34–60 px apart.
- Splash rebuilt around the real wave height at the entry point: a crown of thin spikes, a rising jet that pinches off a droplet, 12 ballistic droplets that disappear when they land, and foam/ripple rings clipped to the water so nothing draws over the sky.
- Marlin: never stops (min ~90–140 px/s stalk), and its acceleration eases in and out (m.a), so the strike builds from ~140 to ~1,000 px/s over ~1.4 s. Body and tail flex harder while accelerating.

**v21.1:** gannets back to silhouettes (one dark tone, far wing lighter for depth; no colours or outlines). Extra motion detail: head held nearly level while the body bobs on each beat, tail flexes with the stroke and fans when gliding or banking, wingtips flick at the turn of each stroke, the flying-away M rolls gently as it steers and its body rises on downstrokes.

**v21:**
- Gannets: 'soar' removed. Styles now flap / dive / flock / away. The trio is looser (60–130 px apart, ±35 px heights, ±12% speeds). They appear on the dashboard and on the quiz screen whenever the sky is in view (cleared once the surface is off screen). New look: white with black primaries, golden head, grey bill, far wing in shadow, thin outline. Animation: asymmetric wingbeat (quick downstroke), body lift on each beat, wings ease smoothly into glides (b.th lerp), dives bank first, then fold and plunge with a folded-wing flutter; bigger splash (tall spout, two rings, droplets).
- Settings: × at the top right. Edits are a draft until Save ("Done" when nothing changed, "Save changes" when something did); ×, Esc or tapping outside closes immediately unless there are unsaved changes, in which case it asks "Discard / Keep editing". Reset scores stays an immediate two-tap action.

**v20:**
- Marlin: every 60–120 s; ~12% smaller (L 155); stalks before the strike (slow cruise ≥ ~2.2 s on screen, easing to a crawl as it closes in) and only then sprints, so it's visible ~6 s on desktop and ~2.5 s on phones.
- Gannets (dashboard sky only, not with Calmer motion): BIRDS spawns every 25–35 s, low over the horizon below the title. Styles: 'flap' (side profile, bursts of 5 beats then a glide; broad swept two-segment wings seen from slightly above, the hand lags the stroke), 'soar' (stiff wings, banking, drifting), 'dive' (tilts, folds into an arrow, plunges, splash of droplets + ring at the waterline), 'flock' (loose trio, out of phase), 'away' (classic M silhouette from behind, beating and shrinking toward the horizon). Test builds expose window.__BIRDS.

**v19:**
- Marlin (rare event): MARLIN state runs on scene time; first visit after ~50–110 s, then every ~80–180 s, only when a fish school in the top ~900 m is on screen (skipped with Calmer motion). It enters from the far side at ~260 px/s, sprints to ~1,300 px/s once within ~460 px, and the school it passes gets scatter = 1: fish spread apart on individual angles, face and flee in the marlin's direction (c.xo offset in loopX), tails beat faster; it decays over ~3 s as they regroup. Silhouette with bill, sail (folds down at speed), pectoral/anal fins, beating crescent tail and faint speed trails. Cleared on page change. Test builds expose window.__MARLIN (set .next = 0 to trigger).
- Dashboard: waterline a little lower (max(26% of height, header + 44 px)); bigger gap between the title and tagline. Streak chip is now small and inline next to the "DAILY DIVE" label.

**v18:**
- A dive always starts at 0 m: show('dive') sets the camera to the dive depth before the page appears (the dashboard's scroll depth used to leak in and could even fire a zone banner).
- Quiz HUD: the zone name now sits above the depth bar (0 m / 7,000 m stay below it).
- Surface panel: the big orange top button is Surface, the lower one is Keep diving.
- Dashboard sub is pinned to the water while scrolling (no easing on the home page). The sun is clipped to the sky above the moving waterline, so waves pass in front of it.
- Header: eyebrow removed; "Trench Dive" centred on one line; tagline "7 PROMPTS – 45 SECONDS EACH – RARER ANSWERS SINK DEEPER" in small caps (one line from ~390 px wide up).
- Streak: new two-tone flame (white on the results orbs, gradient on the Daily card), and the Daily card chip is a dark ember pill with a glowing flame and "N day streak".

**v17:**
- Settings (gear, fixed top-right of the dashboard, fades out once you scroll): Autocorrect typos (default on: a single clear fuzzy match is accepted and the badge says "fixed from …"; off = "Did you mean…?"), Ask Claude about unlisted answers (only shown when the capability is live), Calmer motion (overrides the system setting; RM is now a let), Unlimited timer 45/60/90 s (Daily always 45; SECONDS is a let set in beginDive), Reset saved scores (moved here). Stored in localStorage 'trenchdive.settings.v1'.
- "How depth works" → THE BEARING: no card background, rows split by lines; left = glowing tier creature (plankton, octopus, school, manta, anglerfish, pearl in shell) + points/metres in the tier colour; right = name + short description. A note under it reflects the autocorrect setting.
- Dashboard: scrolling the page moves the camera down (scene.cam = scrollY / PXPM), so you sink and the sub is left behind at the surface. Title smaller, waterline higher (max(22% of height, header + 22 px)), bigger sun (r 42) clipped at the horizon. Mode cards equal height with CTAs aligned at the bottom; Unlimited gets "A fresh set every time"; Daily shows a streak chip when you have one.
- Sea life: fish schools spread wider (lane height 44), sea turtles back (2, near the surface) with a power-stroke flipper animation, head bob and body pitch.

**v16:**
- Card shows a small "PROMPT n OF 7" line above the question (#qCount).
- Quiz HUD for full screen: the Surface button is position:fixed at the top-left of the screen (round icon; "SURFACE" label from 560 px), restyled (glass pill + glossy blue icon disc). The prompt badge is absolutely centred over the row, and DEPTH lines up with the left end of the depth track. Under 1,060 px wide (where the button can't sit in the side margin) the HUD uses two rows: button + centred badge on top, DEPTH/SCORE below. Checked at 360–1920 px in both modes: no overlaps, badge centred to the pixel.
- slotScale(): the quiz sub can grow to 1.55× on screens ≥1100×700 (1.15× otherwise); used for both drawing and the waterline.

**v15:**
- Sub: drive shaft now runs from the propeller into the hull (plus a collar), so the propeller is attached. On entering a quiz the waterline sits at sub centre − 63 px × scale, so the periscope and antenna are above water and the body below.
- Quiz page: the mode pill is gone and the HUD is at the very top. A round ↑ Surface button (label shown at ≥560 px) is the first item of the stats row (hidden in Daily). The depth-track marker is a plain glowing dot.
- Question card is smaller: prompt and timer share a row (grid, prompt wraps, never overlaps), smaller prompt font and padding, answer box and button on one row on every screen. New stopwatch next to the seconds: a ring that empties with the time left and a hand that sweeps once per 5 s of play, driven by S.remaining, so it only moves while the clock runs.
- After a top-tier answer in Unlimited, no "Worth 100 pts" line.

**v14:**
- Quiz HUD: top row DEPTH | "PROMPT n OF 7" box with 7 progress segments (tier-coloured when answered, pulsing for the current one) | SCORE; below it a full-width depth track split into the five ocean zones (0–200 / 200–1,000 / 1,000–4,000 / 4,000–6,000 / 6,000–7,000 m) with 1,000 m ticks, a glowing fill, a mini-sub marker, and a legend (0 m · ZONE NAME pill · 7,000 m). The question card no longer repeats the prompt count.
- The sub starts in the water on the quiz page: the waterline (y0) is lifted above the sub slot (sub centre − 82 px × scale) so the whole sub, periscope included, is under the surface at 0 m.

**v13:** dive HUD (.hud2) replaces the depth card: "DEPTH" label + large metres (left), a slim depth bar with no background (middle, min 84 px), "SCORE" label + large points (right), with text shadows for legibility over sky and water and clamp() sizing for small phones. Progress dots and the zone label are removed from view (#pips hidden, #zoneName screen-reader only); the zone banner still announces each zone. Score updates the moment you answer (paintScore); depth ticks with the dive.

**v12:**
- Sea life: spawn() keeps every body at least 18 px under the waterline (dMin from HALF_H), so nothing is clipped by the surface. Two small fish schools (scale 0.5–0.65) are placed first in the top ~175 m. Shallow habitats widened so lanes still never overlap (check: 0 overlaps, highest top edge ~40 px below water).
- Dashboard buttons: long full-width pill CTAs, all caps (START / SEE RESULTS / DIVE) with down arrows either side. New icons: sunrise over waves (Daily), looping arrows around a fish (Unlimited). Unlimited dive count removed. Download card and its code (SELF_HTML, downloads capability) removed; tests/download.js deleted. Published with capabilities {sample} only.
- Daily Dive: no Quit button, nothing saved until the dive is finished (an unfinished record is discarded; reloading or leaving starts today's set again from prompt 1).
- Unlimited: the Quit button is now "↑ Surface" and opens a bottom sheet ("Head back to the surface?", current depth, Keep diving / Surface). The timer pauses while it's open; Esc or tapping outside keeps diving.

**v11:**
- Sea life never overlaps: spawn() gives every animal its own depth lane sized by HALF_H (half-height in px incl. bob/flaps/glow), searching up to 200 candidate depths and spilling slightly past its band if full. Big surface animals spawn first. Test-build check: 0 overlapping pairs. 41 animals; the Midnight Zone (1,000–4,000 m) now has ~20, including new hatchetfish (glowing bellies) and siphonophores (glowing chains).
- Dive animation fix: answering and pressing Next quickly used to restart the dive's ballast/wind-up each time, so the sub hovered at the surface. diveTo() now carries an in-progress dive straight on (carryEase), the opening is a short pause then accelerate/brake with a small overshoot (diveEase), and the camera never goes above the surface.
- Daily wrap-up shows "Best Daily Dive ever: X pts (Y m) · date" (or "New best Daily Dive!").
- Streak circles: glossy warm 3D orbs with a white flame SVG for days played; dark inset orbs otherwise.
- Prompt boards on the wrap-up: tier rows (count + points, "your answer" tag) that open one at a time; search shows matches from every tier.

**v10:** question header shows only "Prompt N of 7" (left) and the timer (right): no category chip, no answer count. SECONDS = 45. After answering: Unlimited shows one top-tier answer ("Worth 100 pts: X", never the player's own); Daily shows a tier line from TIER_LINE (e.g. Schooler "Swims with the school.") and reveals no answer.

**v9:**
- Depth is 10 m per point again: TIER_DEPTH = TIER_PTS x 10 (Plankton 100 m ... Trench Treasure 1,000 m), MAX_DEPTH 7,000 m. Gauge 0–7,000. Daily button depth is recomputed from tiers; "Your best" uses bestPts x 10. Scene scale is now 0.4 units/m (PXPM 1.7 kept, so a Trench Treasure still moves the ocean ~680 px); colour stops, darkness and creature habitats were re-mapped to it.
- Turtles removed. Manta rays redrawn (flapping wings, cephalic fins, whip tail) and moved near the surface (~20–275 m).
- Dashboard: the "Your dives" stats card and the prompts/answers count line are gone (save data and tiers counts are still kept for the wrap-up and streaks).
- Dive buttons redesigned: icon tile, glowing pill CTA, gold (Daily) / blue (Unlimited) themes, hover lift.

**v8.2:** about half as many animals again (27 in total: 3 fish schools, 1 each of turtle/dolphin/ray/whale/barracuda, 3 lanternfish groups, 5 jellies, 2 each of squid/eel/angler/dumbo, 3 snailfish). The sub is no longer tinted blue below the waterline on the dashboard (subLayer tint removed; the periscope ripple stays).

**v8.1:** creatures redrawn as silhouettes in the original style (pale schools/barracuda in bright water; dark turtles, dolphins, rays, whales, lanternfish bodies, dumbo octopus; glows only for deep-sea animals). The original drawSchool fish are back as the shallow fish (5 schools, 0–760 m); drawReef removed.

**v8:** 279 prompts, ~28,500 accepted answers.
- Ocean life by depth, sparse on purpose (~54 animals in total): sunlight zone reef fish/turtles/dolphins, twilight rays/whales/barracuda, lanternfish from ~850 m, midnight jellies/squid/gulper eels, abyss anglerfish/dumbo octopus, hadal snailfish. Shallow colours fade out with depth. Draw functions: drawReef/Turtle/Dolphin/Barracuda/Lantern/Eel/Dumbo/Snailfish.
- Dive animation: diveTo() runs a scripted tween per answer (duration 1–3.4 s by drop size): ballast-bubble burst, accelerate/brake easing with a soft overshoot, spring-smoothed nose-down pitch from velocity, the sub leads the camera slightly, propeller speed follows velocity, bubbles stream past as it sinks. The depth meter and gauge read the camera each frame (no CSS transitions), and a banner announces each zone crossing.
- New prompts in src/gen_k.js: animal, movie, sport, actor/actress, drink, supermarket item, car model, snack. More answers via src/expand_d.js and src/expand_e.js. NZ global rarity extended to the new boards.
- Matching: an exact answer name now always picks that entry even when another entry shares the alias (fixes a Trench Treasure scoring as Schooler).

**v7:**
- Depth comes from rarity via TIER_DEPTH = [50, 120, 400, 900, 1300, 1600] m (Plankton → Trench Treasure); points/ranks unchanged. MAX_DEPTH = 11,200 m (7 × 1,600). bestDepth is now the deepest dive (independent of best points); Daily records store depth, older records recompute it from their tiers.
- Real ocean zones (twilight 200 m, midnight 1,000 m, abyss 4,000 m, hadal 6,000 m); gauge 0–11,200 m.
- Scene: PXPM 1.7 (about 3× the visible descent per metre; a Trench Treasure moves the ocean ~680 px), colour stops and creature bands re-mapped to the real zones, about 3× more creatures, marine-snow streaks at speed.
- Sub: pilot removed (empty cockpit with a glowing instrument panel); all pink accents now orange.

**v6:**
- FIX: the file is now a complete standalone document (`<!DOCTYPE html>`, head, body, `[hidden]{display:none!important}`). Before, it relied on the old publish wrapper for those; the current publisher serves the file as-is, so all three screens rendered stacked on one page. tests/wrap.sh now copies the file unchanged so tests see exactly what ships.
- Pages: dashboard `#home`, dive `#daily` / `#play`, wrap-up `#results`, with history (Back/Forward work in a normal browser), a 170 ms fade between pages, scene and sub placed fresh per page, page titles, a Quit button (two taps; Daily progress is saved), and "‹ Dashboard" on results. Finishing a dive replaces the dive entry with #results, so Back goes to the dashboard. Reloading on #daily resumes the Daily.
- Submarine redrawn: glossy hull with red racing stripe, rivets, rim light, shrouded 3-blade propeller, red tail fins and dive planes, tower with railing and TD-1 marking, chrome periscope, antenna with blinking beacon, green/red nav lights, warm-lit portholes, pilot with cap and goggles in the front dome (waves now and then). Home: tower just under water, periscope and antenna tip out.
- Download: dashboard card "Download .html". Inside claude.ai it uses the `downloads` capability; anywhere else a normal Blob download. The copy is the page's own source captured at startup (only #app script, #app-css style and Google Fonts links kept). Published with capabilities {sample, downloads}. tests/download.js checks the saved copy loads and plays.

**v5:** 271 prompts, ~25,200 accepted answers (duplicates like "Lake Taupō"/"Taupō" now merge by core name).
- Home: intro text, sub floating just under the surface with periscope out (waterline adapts to the header height), Daily Dive + Unlimited cards, richer stats (deepest dive + mini gauge, dives, average, streak, best streak, Trench Treasures found, Daily Dives, answer-mix bar), "How depth works".
- Daily Dive: 7 prompts seeded from the NZ date (Pacific/Auckland), same for everyone; countdown to NZ midnight (DST-correct); progress saved per prompt so a reload resumes; once done it opens the results instead of replaying. Unlimited avoids today's Daily prompts until the Daily is done.
- Wrap-up page: Daily shows streak, best streak and a 7-day line; Unlimited shows Play again. Every prompt expands to its full board grouped by tier with search (names + aliases) and your answer highlighted.
- Save object adds `daily{YYYY-MM-DD:{done,pts,res[]}}` (pruned to 60 days), `tiers[7]` (6 tiers + passes), `bestStreak`.
- Tiering: Trench Treasure share 8% (min 2 per board, median 7); reveal says "N Trench Treasures on this board, including X".
- NZ global rarity: `src/nzrank.js` sets tiers for NZ answers on non-NZ boards (e.g. Air New Zealand = Rare, NZ dollar = Rare, Richie McCaw = Deep Cut). New prompts in `src/gen_j.js`: mobile networks, news outlets (NZ answers in the tail).
- Matching: single distinctive word ("LeBron", "Kendrick") accepts a unique match or offers a pick-list; "X tree" also tries "X".
- List expansion: `src/expand_a/b/c.js` via `X(id, list)`; "+Name" = common (start of Schooler), plain = tail, "!Name" = Too Clever. A probe of 815 realistic answers on 25 broad prompts went from 92% to 98% accepted (remaining misses are correct rejections).
- Tests: tests/daily.js (seeding, resume, no replay, streak, week line, boards/search, DST countdown) added.

**Previous state (v4):** 269 questions in rotation, ~23,100 accepted answers, every question ≥25 answers, no duplicate ids, all 5 non-clever tiers populated.
- v4 changes: `src/drop.js` removes 200 questions from rotation by id (single-artist song lists; single-creator film/book lists except Tom Hanks, Spielberg, Will Smith, Roald Dahl, Stephen King; anything under 25 answers; niche geography such as "city in Turkey"; niche trivia). Delete an id there to restore it.
- `src/gen_i.js`: 28 new broad Krillion-style prompts (country, superhero, something yellow, in the fridge, zoo animal, breakfast, cartoon character, solo singer, TV show, holiday, transport, body part, ice cream, chip flavours, hobby, dance, scientist/inventor, fairy tale, things that fly, athlete, office, round things, materials, reality TV, boats, kids' party games, fears, things with wheels).
- Dive mix: GEO_MIN 1, GEO_MAX 2, CAT_MAX 2 per other category (was "at least 3 geography").
- AI judge: published with `capabilities: {sample: {}}`. Unmatched answers (and "No, I meant X" on the typo prompt) go to Claude (`modelTier: quick`) with the prompt + board list; JSON verdict {valid, board, name, rarity, reason}. Board synonyms score that entry's tier; new valid answers score common→Plankton, uncommon→Schooler, rare→Rare, very_rare→Deep Cut (never Trench Treasure). Timer pauses while checking; "Skip check" aborts. Falls back to list-only marking when unavailable (downloaded file, signed out, consent declined).
- Fixes: EXTRA/CLEVER now load before the legacy inline questions (previously ignored for those); `+Item` in EXTRA ranks a common answer at the start of Schooler instead of the tail (tail placement gave common extras 100 pts); removed Dar es Salaam alias from Dodoma; flow.js now really plays a top-tier dive. New test: tests/judge.js (stubbed Claude + 2,000-dive mix check). Tests (count/flow/smoke/home/scroll) pass in headless Chromium; only error is the blocked Google Fonts request in the sandbox.

**Completed:** full game loop; six official-style tiers/points/depths with your colours; fuzzy match + confirm; best-score saving; redrawn submarine; thinned background; Google-search link for unmatched answers; large NZ, geography, pop-culture, sport, brand, food, everyday-life question packs; sub pinned on scroll.

**Known issues / limitations / next steps**
1. Automatic verification via Google is impossible from a static page (no API/CORS); only the search link exists. Real fix = more answers and aliases, or a tiny backend.
2. Rarity tiers are ESTIMATES from list order, not real popularity data; "Too Clever" is hand-flagged only (almost nothing flagged yet — add `!Item` entries / `CLEVER[id]`).
3. Official Krillion tier colours/art could not be read (only theme colour `#050a14` confirmed); the six colours are chosen by the user's description + my picks. A screenshot of the official UI would let you match exactly.
4. Data quality: lists were written from memory and pruned for padding/duplicates, but tails of long lists (obscure NZ places, sports/brand/film lists, song lists) may still contain doubtful entries — spot-check with `tests/list.js` and prune with `prune3.py`.
5. Single-answer ambiguity: aliases shared by two entries (e.g. "Congo", "Tigers") resolve to the lowest-tier match.
6. Ideas: more "Too Clever" flags; more aliases/misspellings; per-category stats; daily seed (Krillion-style one set of 7 per day); share-result button; sound; accessibility pass (reduced-motion is respected via `RM`); verify on real phones.
7. The published Artifact URL belongs to the old account; re-publish `dist/trench-dive.html` in the new account (see the master prompt).
