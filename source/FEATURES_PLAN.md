# HS Code Finder — expansion plan (one feature per day)

This file tracks the "add features one at a time, one per day" plan for the HS Code Finder
PWA. It is read by a daily scheduled task that picks up the next PENDING item, builds it,
deploys it, and marks it DONE here as part of that day's work.

Live app: https://eliasmefleh-a11y.github.io/hs-code-finder/
Repo: https://github.com/eliasmefleh-a11y/hs-code-finder (public, GitHub Pages, root = deployed app)
Source of truth for the app's source (NOT deployed, reference-only): `source/hs_code_finder.html`
and `source/build_pwa.py` in this repo.

## Status

1. **Multi-item shipment calculator** — DONE (2026-08-21). Calculator supports multiple HS
   code + invoice value line items with add/remove, per-item breakdown, and a combined
   shipment total. Single-item use looks identical to the original one-code calculator.

2. **Auto-apply statutory minimum customs value** — DONE (2026-08-21). Calculator line
   items that have a parsed statutory minimum now show a quantity field. When entered,
   declared value (invoice) is compared against quantity × minimum (converted via the
   exchange rate); if declared is lower, customs charges are computed on the minimum
   instead, with a clear on-screen note explaining which value was used and why. Invoice
   value itself is never altered — only the customs-charges base. No quantity entered
   falls back to the original warning-only behavior.

3. **Data-freshness indicator + changelog** — DONE (2026-08-22). Added a "Updated [date]"
   badge next to the disclaimer bar and a "What's new" button opening an in-app changelog
   modal listing dated entries (env tax introduction, the 20/21 Aug feature releases, and
   this feature itself). Badge date is derived automatically from the newest changelog
   entry.

4. **Shareable quote / PDF export** — DONE (2026-08-22). "Export / print quote" button on the
   calculator renders the current breakdown (single or multi-item, including shipment total)
   into a printer-friendly black-on-white view (`#calcPrintArea`, shown only under
   `@media print`) and opens the browser print dialog — the user can "Save as PDF" from
   there. No PDF library bundled, so the app stays fully offline/dependency-free.

5. **Restricted-goods / permit flags as structured data** — DONE (2026-08-22). New
   `PERMIT_REQUIREMENTS` table (HS chapter/heading → ministry, longest-prefix-wins) sourced
   from Lebanon's Ministry of Economy and Trade "Survey on Non-Tariff Measures on Trade"
   (economy.gov.lb) and MOPH's published regulatory scope (pharma/cosmetics/medical devices).
   Surfaces as a blue "🛂 Permit: [Ministry]" chip on search results and a matching warning
   block in the calculator — distinct from the free-text "restrict" chip and the
   statutory-minimum chip. Explicitly presented as non-exhaustive (a heads-up, not a
   guarantee) in both the chip tooltip and the Details disclaimer.

6. **Preferential origin / FTA rates** — DONE (2026-08-22). Calculator line items get an
   optional "Preferential origin" selector (None / GAFTA / EU-EFTA). Selecting one zeroes
   out customs DUTY only (VAT/extra/environmental tax are unaffected — those are domestic
   taxes that apply regardless of origin), sourced from lebtrade.gov.lb and the U.S.
   Commercial Service's Lebanon Country Commercial Guide, both confirming duty-free
   treatment for qualifying goods with a valid certificate of origin. Shows an on-screen
   note stating the assumption (eligibility + certificate of origin) and, for agricultural
   chapters (01-24), an extra caveat that agri products can carry separate schedules or
   safeguard measures rather than guaranteed full exemption. No fabricated per-code rate
   table — this is a real, sourced duty-relief rule (0% on qualifying goods), not a guess.

**All 6 originally planned features are DONE (as of 2026-08-22).** Further work below is new
scope, chosen by the user after the plan finished — see "Conventions established" for how to
carry the same build/test/deploy discipline forward.

## Post-plan additions

7. **Shipping / insurance / broker fees** — DONE (2026-08-22). Optional shipment-level cost
   fields (Shipping, Insurance, Broker/agent fee — all USD) added next to the exchange rate
   field. When any are entered, a new "Other costs" block (or, for a single item, an
   "Other costs" block appended below the item) shows the breakdown and an all-in
   "Total landed cost, incl. shipping/insurance/broker" figure — kept visually separate from
   the existing "Total landed cost (goods + customs charges)" line so the two never blend.
   For multi-item shipments the extra costs are added once to the shipment total only (never
   per item, to avoid double-counting). Not persisted between sessions (unlike the exchange
   rate) since these are shipment-specific, not a stable default.

8. **Manual shipping-rate comparator** — DONE (2026-08-22). User asked for the app to "get the
   best prices from shipping companies" — no carrier (Maersk, DHL, local Lebanese forwarders,
   etc.) exposes a free public API for live quotes, so this ships as a manual comparator
   instead of a fabricated live-pricing feature: a "🚢 Compare shipping rates" button on the
   calculator opens a modal where the user enters the quotes they've already collected
   (carrier name, mode — sea/air/land-cross-border/courier, price USD, transit days, notes).
   Entries are ranked cheapest-first with a "💰 Cheapest" badge, and a "Use this rate" button
   applies the chosen price directly to the Shipping field so it flows into the landed-cost
   total. Entries are in-memory only (not persisted to Store, and reset whenever a new
   calculation starts via openCalculatorForCode) since quotes are shipment-specific.

9. **"Ask AI" shortcut** — DONE (2026-08-22). User asked for "a shortcut for AI in the app."
   Clarified scope first: the app is fully offline/dependency-free by design (no bundled API
   key, no backend), so this doesn't call an AI API directly or ship a hardcoded key. Instead,
   a 🤖 button on every search-result/favorite card, and a "🤖 Ask AI" link on each calculator
   line item, builds a plain-language question from that code's own data (description,
   duty/VAT/extra/environmental tax rates, permit flag if any) and opens it in Claude via the
   `claude.ai/new?q=...` deep link, which pre-fills the message composer for the user to review
   before sending — confirmed live via research (Aug 2026) as working today, though it's an
   observed/unofficial behavior, not a documented Anthropic API, so it could stop working
   without notice. The same question text is also copied to the clipboard as a fallback. No
   network calls are made by the app itself; requires the user to already be signed in to
   claude.ai in that browser tab.

## Data quality: full English translation

10. **Complete Arabic → English translation of all 5,379 tariff rows** — DONE, deployed
    live 2026-09-07 (built 2026-08-25). A separate, earlier project (started 2026-08-18, before the
    "one feature per day" plan above): 5,263 of the 5,379 GOV_TARIFF_DATA rows had only an
    Arabic description and no English text or search keywords, so searching in English
    silently missed most of the dataset. Split into 18 batches of ~300 rows
    (`/tmp/translate_batches/batch_0XX.json`), each translated by a dedicated agent that
    resolves the tariff book's hierarchical Arabic (parent heading + `→`/`-`-marked
    sub-item) into one natural standalone English description, plus 2-5 plain-English
    search keywords, written to `output_0XX.json`. Paused partway through (14/18 batches
    done) by a session usage limit; resumed via a scheduled trigger that finished the
    remaining 4 batches (07, 12, 13, 16) and merged all 18 into `hs_code_finder.html` by
    code. All 5,379 rows now have a real English description, rebuilt into
    `pwa/index.html`/`pwa_flat/index.html`, and verified **locally** with Playwright (100%
    coverage, English keyword search surfaces newly-translated codes, full regression of
    every other feature passed clean) — the pre-existing 116 rows that already had English
    were left untouched, and the merge matched every one of the 5,263 translated rows with
    zero left blank.

    **Deploy still outstanding**: the browser bridge to the user's desktop wasn't connected
    when this run reached the deploy step, and no git/gh credentials are available in this
    cloud container as a fallback. The next run should detect this note, skip straight to
    the deploy step (upload `pwa_flat/index.html` as-is — no rebuild needed), verify live,
    sync this file and `source/hs_code_finder.html` to the repo, then mark this DONE.
    **Update (2026-09-04)**: the current `pwa/index.html`/`pwa_flat/index.html` build now
    also includes item 11 below (Lebanese dialect auto-parts vocabulary), so a single deploy
    covers both outstanding items — no need to deploy them separately.

## Data quality: Lebanese dialect / colloquial search vocabulary

11. **Lebanese-Arabic dialect & French-loanword vocabulary expansion, auto-parts pass** —
    DONE, deployed live 2026-09-07 (built 2026-09-04). User reported that typing "frem" (Lebanese/French
    garage slang for brakes) returned nothing useful, and asked to broaden dialect coverage,
    "starting with auto parts." Root cause: the codebase already had an extensive
    `SYNONYM_GROUPS` dialect vocabulary (fruits/veg, meat/dairy, spices, kitchenware,
    construction/hardware, electronics, clothing, cosmetics, stationery, and a large existing
    automotive-parts section — clutch, gearbox, radiator, spark plug, starter, timing belt,
    steering, carburetor, alternator, etc.), but the existing brake group only had the
    compound phrase "colier frem" (brake caliper), not the standalone word "frem" a user
    would type alone.
    - Added standalone "frem"/"freim" to the existing brake group.
    - Verified against real `GOV_TARIFF_DATA` rows (not guessed) and added 4 new dialect
      groups plus one extension, each anchored to a real tariff-book HS line: brake pads /
      friction material ("بلاكيت"/plaquette, "تيل الفرامل" → HS 6813.20/6813.81/6813.89),
      brake fluid ("زيت الفرامل"/"سائل الفرامل" → HS 3819.00), vehicle wiring harness
      ("هارنس", "طاقم الأسلاك" → HS 8544.30), leaf/coil spring ("يايه" → HS 7320.10), and
      power-steering pump added to the existing steering-wheel group ("بمبة الدركسيون" → HS
      8708.94).
    - Deliberately did **not** add speculative terms with no matching row in the actual
      tariff data (e.g. fuel tank, AC condenser, tie-rod) rather than guess — consistent with
      this project's no-fabrication rule. Also deliberately excluded the bare 3-letter form
      "ياي" after testing showed it collides with unrelated rows via the app's direct
      substring-match path (same class of risk already documented for short words like
      "بن"/"خل" elsewhere in this file) — kept the longer, safe form "يايه" instead.
    - **Known pre-existing limitation surfaced by this testing (not introduced by this
      change, and not fixed here — out of scope for a vocabulary addition)**: when many rows
      tie at the same synonym-match score (e.g. searching "frem"/"فرامل" alone matches brake
      fluid, friction material, electromagnetic brakes, railway brakes, bicycle brakes, *and*
      the motor-vehicle brakes row all at once), the tie-break falls back to ascending HS
      chapter order, so the motor-vehicle-specific code (8708.30) — almost always what a
      Lebanese customs agent means — can land a few rows down the list rather than first.
      The word now correctly surfaces brake-related codes (previously it surfaced nothing),
      but a future pass could look at boosting vehicle-context rows in the tie-break if this
      turns out to matter in practice.
    - Verified with a dedicated Playwright test (`frem`/`freim`/`بلاكيت`/`تيل الفرامل`/
      `زيت الفرامل`/`هارنس`/`طاقم الأسلاك`/`يايه`/`بمبة الدركسيون` all resolve to the correct
      HS chapter) plus a full regression of Features 8, 9, and the item-10 translation data —
      all clean, zero new errors.
    - Rebuilt into `pwa/index.html`/`pwa_flat/index.html` and `HS_Code_Finder_PWA.zip`
      (md5-verified). Deployed live 2026-09-07 together with item 10 and the rebrand below.
    - Follow-up "everyday goods, broad pass" (2026-09-04, same day, user said "Everything
      lebanese use"): reviewed categories beyond auto parts for genuine gaps — i.e. Lebanese
      dialect/French-loanwords with no literal match in the tariff text, not already-covered
      ground (the existing vocabulary already has thorough food, household, hardware,
      electronics, clothing, cosmetics and stationery sections). Found and fixed 3 real gaps,
      each verified against an actual HS row:
      - Hookah/shisha ("أرجيلة"/"نرجيلة"/argileh/nargileh/hookah) → HS 9614.00 (smoking
        pipes). The government row doesn't mention hookahs at all under that official
        wording, so this needed two changes to actually work: added "hookah, shisha,
        argileh, nargileh, waterpipe" directly to that row's own English keyword field (so
        English search finds it), and a synonym group bridging the Arabic dialect words to
        "غلايين" (the plural that IS literally in the government text) rather than to the
        colloquial words themselves — a synonym group only helps if at least one member
        literally appears in the row it should match, which the colloquial words alone did
        not. Deliberately left "شيشة" out of the group: it's a plain substring of "حشيشة"
        (a common word across agriculture/pharmacy rows for herbs/hemp), so it already
        collides via the app's direct-Arabic-substring search step regardless of any group —
        confirmed by testing, and not fixable by a vocabulary change.
      - Propane/cooking-gas cylinder ("بمبة غاز"/"قنينة غاز"/"اسطوانة غاز") → HS 7311.00.
      - Building elevator ("أسانسير", the French loanword Lebanese actually say, vs. the
        literal-but-rarely-spoken "مصعد") → HS 8428.10.
      Considered and deliberately skipped (no matching HS row found, or already covered
      without a group): fuel tank, AC condenser, tie-rod end, e-cigarette/vape (no dataset
      row found for any of these); sunglasses, watches, toys, umbrellas, cigarette lighters
      (already have direct English keywords and/or the literal Arabic term embedded in their
      rows, so no dialect gap exists there).
    - Re-verified with an expanded Playwright test (all 3 new terms plus every round-1 term)
      and a full regression of Features 8, 9, and item 10's translation data — all clean.
      Rebuilt into `pwa/`/`pwa_flat/`/`HS_Code_Finder_PWA.zip` (md5-verified) — this
      supersedes the round-1 build note above. Deployed live 2026-09-07.
    - The user's original "Both, starting with auto parts" request is now substantively
      covered (auto parts + a broad everyday-goods pass). Future gaps, if any surface from
      real usage, should follow the same rule: verify against an actual `GOV_TARIFF_DATA` row
      before adding, never add a word on vibes alone.

## Conventions established (follow these exactly)

- **Single source of truth**: `hs_code_finder.html` (the master file). Never edit
  `pwa/index.html` or `pwa_flat/index.html` directly — they are generated.
- **Build**: `python3 build_pwa.py` (reads `hs_code_finder.html`, writes `pwa/index.html`
  and `pwa_flat/index.html`). If build_pwa.py's anchor strings no longer match after an
  edit, fix the anchors in build_pwa.py rather than hand-editing the generated files.
- **Deploy target**: the live site's `index.html` is the **flat** variant
  (`pwa_flat/index.html`, icon paths de-prefixed) — that's the file that gets uploaded to
  the repo root. `pwa/index.html` (icon-path variant) is a reference/local-testing build,
  not currently deployed anywhere separately.
- **Testing**: before every deploy, test with Playwright
  (`chromium.launch({executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox']})`)
  against a local `python3 -m http.server` serving the `pwa/` directory. Bypass the license
  paywall by seeding `localStorage.setItem('hscf_license', JSON.stringify({unlocked:true,
  key:'HSCF-LIFETIME-DEMO'}))` — note the key is `unlocked`, not `active`. Verify no
  console/page errors, correct math, and (for UI changes) a screenshot for visual QA.
- **Deploy mechanism**: no git/gh credentials are available in the cloud container for this
  repo — deploys go through the GitHub web upload UI via Chrome browser automation (the
  user's real browser, requires their desktop app to be open/connected):
  1. Navigate to `https://github.com/eliasmefleh-a11y/hs-code-finder/upload/main`
  2. Use the file_upload tool on the file input to upload `pwa_flat/index.html` as `index.html`
  3. **Wait for the upload progress bar to fully complete** before touching the commit
     message field — clicking too early is a known failure mode where the typed commit
     message silently doesn't land. Screenshot to confirm the upload finished (no
     "Uploading X of Y files" text, no progress bar) before proceeding.
  4. Click the commit-summary textbox, type a one-line commit message, screenshot to
     confirm the text actually landed (it sometimes doesn't on the first click — if the
     placeholder text is still showing, click again and retype).
  5. Scroll down, click "Commit changes".
  6. Navigate to `https://github.com/eliasmefleh-a11y/hs-code-finder/actions`, wait for the
     newest `pages-build-deployment` run to leave "In progress" (~35-55s typical).
  7. Navigate to `https://eliasmefleh-a11y.github.io/hs-code-finder/`, hard-reload
     (ctrl+shift+r), reload again after seeding the license key in localStorage, and use
     the javascript_tool to directly assert the new feature works correctly live (not just
     that the page loads).
  8. Also upload the updated `source/hs_code_finder.html`, `source/build_pwa.py`, and this
     `FEATURES_PLAN.md` (with today's item marked DONE and a one-line note) to the repo via
     the same upload flow, targeting `https://github.com/eliasmefleh-a11y/hs-code-finder/upload/main/source`
     for the two source files and `https://github.com/eliasmefleh-a11y/hs-code-finder/upload/main`
     for this plan file, so the next day's fresh session can fetch the current source via
     `curl -s https://raw.githubusercontent.com/eliasmefleh-a11y/hs-code-finder/main/source/hs_code_finder.html`
     and `.../main/FEATURES_PLAN.md` (public repo, no auth needed for raw fetches).
- **Deliverables**: after verifying live, rebuild `HS_Code_Finder_PWA.zip` from `pwa/`
  (`zip -r HS_Code_Finder_PWA.zip . -x ".*"` run from inside `pwa/`), verify its
  `index.html` md5sum matches `pwa/index.html`, then deliver both `hs_code_finder.html` and
  `HS_Code_Finder_PWA.zip` via SendUserFile, and update the Cowork artifact named
  `hs-code-finder` via `mcp__remote-devices__update_artifact` using the `hs_code_finder.html`
  file_uuid SendUserFile returns.
- **One feature per run.** Do not start a second feature in the same run even if time
  allows — mark today's DONE, stop, and let tomorrow's scheduled run pick up the next one.
- **If the Chrome browser tools / user's desktop aren't reachable** at run time (deploy
  step fails because there's no connected device), do NOT skip the feature as done. Finish
  and locally verify the code change, leave FEATURES_PLAN.md's item marked
  "BUILT, NOT YET DEPLOYED" with a short note, and end the run — the next scheduled run
  should detect that in-between state and retry the deploy before starting a new feature.
- **When all 6 items are DONE**: mark the plan complete at the top of this file, send the
  user a final wrap-up message, and disable this scheduled task
  (`mcp__claude-code-remote__update_trigger` with `enabled:false` using this run's own
  trigger id, which will be included in the run's prompt).

## Branding: Freight Solutions SAL rebrand

12. **Rebrand the app to match freightsolutionsal.com** — DONE (2026-09-07). User asked
    for the app to be rebranded with Freight Solutions SAL's actual logo and colors,
    uploaded their print logo (`logocmyk2forcups.pdf`, a CMYK file for cup printing) and
    said to match it to the live website. Research first, then applied:
    - Vectorized the exact "F" mark from the supplied PDF with `pdftocairo -svg` (no
      rasterizing/guessing the shape) and computed its precise bounding box
      (326.39,131.02 → 620.31,520.02) to crop a clean inline SVG `viewBox` — replacing the
      old generic ship/box icon in `.brand-mark` and in the app's PWA icon set.
    - Pulled the live site's actual computed styles via a real browser (not guessed):
      background `#0f172a` (dark navy), interactive/CTA blue `#0085ff`, headings in
      "Belleza", body in "Work Sans", company name displayed as "Freight Solutions sal".
      The print logo's flat CMYK navy (`#264391`) and the site's own logo GIF (a
      multi-tone blue gradient, sampled via canvas pixel analysis since the file couldn't
      be fetched directly from this sandbox) informed the icon gradient
      (`#0085ff` → `#003366`) rather than a flat color, to visually echo the real site
      asset instead of just reusing the print-only navy.
    - Updated `:root` CSS variables (`--bg`, `--accent`, new `--accent-dark`,
      `--accent-ink`) and every hardcoded rgba/hex that referenced the old accent, so the
      whole app repaints consistently rather than leaving stray old-brand colors in some
      components.
    - Added a "FREIGHT SOLUTIONS SAL" byline (linked to the website) next to the header
      title, and a "Built by Freight Solutions SAL — Moving Lebanese Business since 1978"
      line in the footer, both using the site's real tagline text.
    - Regenerated the full PWA icon set (icon-192/512, maskable variants, apple-touch-icon,
      favicon-16/32, favicon.ico) with the new logo+gradient via a small Pillow script
      (`/tmp/brand/make_icons.py`), replacing the old blue-green box icon everywhere;
      bumped the service worker's `CACHE_NAME` (v4/v3 → v5 in both `pwa/` and `pwa_flat/`)
      so previously-installed users actually pick up the new icons instead of serving the
      old ones from cache indefinitely.
    - Added Google Fonts (Belleza + Work Sans) via `<link>` tags — required updating
      `build_pwa.py`'s `HEAD_OLD`/`HEAD_NEW` anchors since the `<title>`→`<style>` gap
      changed; kept the actual `<title>` text unchanged (browser-tab text isn't part of
      what the user asked to rebrand) but updated the meta description, manifest
      `name`/`description`, and `theme-color`/`background_color` to `#0f172a` and mention
      Freight Solutions SAL.
    - Verified with a full regression (Features 8/9, item-10 translation data, both rounds
      of dialect-vocabulary tests) — all identical pass/fail results to before the rebrand,
      confirming no functional regressions from the CSS/header changes. Visually verified
      via screenshot against the live site's own screenshot.
    - Deployed live and verified on
      `https://eliasmefleh-a11y.github.io/hs-code-finder/` (2026-09-07, via GitHub web
      upload once the browser session was signed back into GitHub); this single deploy
      also carries items 10 and 11's previously-pending changes (full English translation +
      auto-parts/everyday-goods dialect vocabulary), since all three had been built but
      undeployed, blocked on the same browser-bridge connection.

## Search engine: Yamli-style Arabizi understanding + broad vocabulary round 3

13. **"Understand every word, Yamli-style"** — DONE (2026-09-07). User asked for the search to
    understand any word the way yamli.com does (typing Franco-Arabic/Arabizi and having it
    resolve to the right Arabic word), plus more Lebanese-dialect vocabulary for the 5,379
    codes. Investigation found the app ALREADY has a real dictionary-guided Arabizi beam-search
    engine (`arabiziCandidates`/`arabiziSuggestions`/`resolveArabiziPhrase`, `VOCAB`/`VOCAB_TRIE`
    built automatically from every word in the actual 5,379 rows + SYNONYM_GROUPS) — this is
    the Yamli mechanism the user was asking for; it just had one correctness bug and needed
    more curated dialect vocabulary on top of it, not a rebuild.
    - **Bug fix**: `TRANSLIT_ALTS_RAW`'s `"2"` (hamza) alternatives were `["ء","ق"]` — but
      `normalizeArabic()` collapses `أ/إ/آ/ا` to plain `ا` everywhere (including in `VOCAB_TRIE`),
      while bare `ء` is never touched by that normalization, so a "2"-initial word whose real
      spelling starts with `أ` (e.g. "2asanseer" → أسانسير/elevator) could never reach it —
      `ء` literally never equals `ا` after normalization. Fixed by adding `ا` as the primary
      alternative: `["2",["ا","ق","ء"]]`. Verified: "2asanseer" now correctly resolves to
      اسانسير (HS 8428.10); "2ahwe" → قهوة (the ق path) still resolves correctly, unchanged.
    - **Vocabulary round 3** (~30 new SYNONYM_GROUPS entries, each verified against a real
      GOV_TARIFF_DATA en/kw phrase before adding, same no-fabrication discipline as prior
      rounds): watches, general jewelry + rings/necklaces/earrings, toys/dolls/puzzles, tuna/
      salmon/squid/shrimp, baby stroller/walker/car-seat/infant-formula, pet food, sunglasses/
      eyeglasses/contact lenses, wheelchairs, thermometers, a cane/walking-stick bridge for
      "عكاز" (no distinct "crutch" HS row exists — bridged to the closest real one, 66.02),
      suitcases/backpacks/wallets, magazines, marble/granite, and guitar/piano/violin/drum.
    - Three additions were tested and found to collide, then fixed or dropped rather than
      shipped broken: "اسورة" (bracelet) is a literal substring of "ماسورة" (gun/pipe barrel)
      — dropped; "قرط" (earring) is a substring of "القرطم" (safflower oil) — dropped, its
      clean plural "اقراط" kept; bare "cane" is also the English word for sugarcane and tied
      against "cane molasses" rows — dropped in favor of the unambiguous 2-word "walking stick".
      Bare "سمك" (fish) and "ساعة يد" (wristwatch phrase) tested clean and were kept; bare
      "ساعة" (hour/watch homonym) tested dirty (matched unrelated machinery specs) and was
      deliberately left out.
    - **New, out-of-scope-to-fix observation** (documented in code comments at each spot):
      "مجوهرات" (general "jewelry") is a genuine tie, not a bug — the government's own official
      Arabic text for HS 42.02 (cases, including jewelry boxes) literally contains the word
      "مجوهرات" too, scoring exactly like the real chapter-71 jewelry rows via the app's direct-
      Arabic-substring step; chapter 42 wins only because of the pre-existing ascending-HS-
      chapter tie-break (same class of limitation already documented for "frem"/vehicle brakes).
      Typing a more specific term ("خاتم"/"سلسال"/"gold jewelry") correctly reaches chapter 71
      directly. "كتاب" (book) remains a literal substring of "الكتابة" (writing, appears in
      printing-ink rows) — same accepted root-collision class as "بن"/"خل"/"ياي".
    - Verified with a dedicated 46-case Playwright suite (all round-3 terms, the "2" fix via
      the real `resolveArabiziPhrase` → `runSearch` flow exactly as the UI uses it, and full
      regression of every prior round) — 46/46 passed, zero regressions.
    - Rebuilt into `pwa/`/`pwa_flat/`/`HS_Code_Finder_PWA.zip` (md5-verified).

14. **Arabizi coverage recheck / round 4** — DONE (2026-09-07). User asked to "recheck for words
    that are not there in arabizi to arabic" after spotting the "2" bug above, i.e. audit the
    transliteration engine itself for the same class of gap. Built a ~109-case coverage audit
    (`arabiziSuggestions()` called directly, bypassing SYNONYM_GROUPS, to isolate pure engine/
    VOCAB coverage) covering food, construction materials, auto parts, jewelry, optics, and more.
    - **Two real `TRANSLIT_ALTS_RAW` gaps found and fixed**: `"d"` never generated `ذ`, so
      "dahab" (ذهب/gold, a real VOCAB word used 8x in the dataset) could never resolve — Lebanese
      Arabizi very commonly collapses the "dh" digraph to plain "d". Fixed: `["d",["د","ض","ذ"]]`.
      `"i"` never generated `ا`, so "itar" (إطار/tire, a real VOCAB word used 15x) could never
      resolve — many words starting with a kasra-hamza sound get typed as plain "i" rather than
      "2i"/"ee". Fixed: `["i",["ي","","ا"]]`. Both verified against the real dataset before and
      after the fix.
    - **One systemic architecture gap found and fixed**: `buildVocabIndex()`'s loop over
      `SYNONYM_GROUPS` indexed each Arabic group member as ONE token — a multi-word phrase like
      "جنزير الكاما" (Kama chain) or "ساعة يد" (wristwatch) went into `VOCAB` as that whole string,
      never split into its individual words. Since Arabizi resolution requires an exact match to
      a stored `VOCAB` key, typing just the ONE word "جنزير" (chain, on its own — a real,
      meaningful, dataset-relevant word) could never resolve via Arabizi at all; it fell back to
      an unrelated fuzzy nearest-match ("خنزير"/pig). Confirmed `VOCAB.has()` was `false` for
      "جنزير", "مشايه", and "ساعه" before the fix. **Fixed** by also splitting any multi-word
      Arabic group member on whitespace and indexing each individual word (same `minLen=2`
      override already used for curated entries). This is a general fix, not limited to the
      three words that surfaced it — it applies across every multi-word phrase in
      `SYNONYM_GROUPS`. Verified via `VOCAB.has()`: "جنزير", "مشاية", "ساعة" (and "يد") are now
      all present; "jinzir" → جنزير, "mishaye" → مشاية, "sa3a" → ساعة now resolve exact via
      `arabiziSuggestions()`.
    - Checked for new short-word collision risk from the split (the only realistic downside of
      indexing more short words): only 20 words of length ≤2 exist in `VOCAB` total, all
      legitimate real words (e.g. "بن", "رز", "يد") — no unexpected new collision class.
    - Remaining ~11 audit "misses" were traced to imprecise test-authoring (wrong vowels/digits
      in my own Arabizi spellings, or expecting a normalized form that doesn't match the app's
      own `normalizeArabic()` unification rules), not real engine bugs — e.g. "aluminyom"/
      "sagayer" (wrong expected normalized string), "bara3i" (used digit "3"/ع instead of "8"/غ),
      "shasi"/"chassi" (no trailing vowel typed, so the app correctly can't generate the needed
      trailing ه), "karbiratir"/"klakson"/"sospansyon" (typed vowels don't match the real
      dataset word's actual letter sequence, e.g. "karbiratir" vs. the real "كاربوراتور").
    - Re-verified full 46-case round-3 regression suite: 46/46 still pass, zero regressions from
      these engine-level changes.
    - Rebuilt into `pwa/`/`pwa_flat/`/`HS_Code_Finder_PWA.zip` (md5-verified).

15. **User-corrected dialect spellings (round 5)** — DONE (2026-09-07). User (a native Lebanese
    speaker) directly corrected several of my own round-4 test spellings, which surfaced two more
    real gaps rather than just being spelling notes:
    - **"e" needed "ا" as a translit option**: the user's own natural spellings "se3a" (ساعة/
      watch) and "douleb" (دولاب/tire) both use "e" for what the dataset's real word spells as
      a mid-word alif — "sa3a"/"doulab" (with "a") already worked, but the equally-valid "e"
      spelling did not, because `"e"`'s alternatives were `["ي","","ه"]` with no `ا`. Fixed:
      `["e",["ي","","ه","ا"]]` (same fourth-option pattern as the "a"/"i" fixes). Verified:
      "se3a" now resolves both "سعة" (capacity) and "ساعة" (watch) as exact candidates — both
      are genuinely real dataset words, so both are surfaced as suggestion chips rather than
      one being force-ranked over the other (same principle as other documented ties); "douleb"
      now resolves "دولاب" exactly.
    - **"دولاب"/"دواليب" (tire) had NO bridge to actual tire results at all** — a real, higher-
      impact gap the user's correction exposed. "دولاب" already existed in `SYNONYM_GROUPS` but
      only as a "wardrobe/cabinet/closet" synonym; the tariff book's own tire rows (HS 4011) only
      ever use the formal word "إطار", so a customs agent typing the everyday word for tire
      ("بدي غيّر الدولاب") got furniture-hardware results, not tires — arguably the single most
      practically important gap found this round, since tires are a routine import/customs item.
      Fixed by adding "دولاب"/"دواليب" to the existing `["tire","tyre",...,"اطار",...]` group.
      Kept the pre-existing wardrobe mapping too rather than removing it — "دولاب" is a genuine
      homonym in Lebanese dialect (wheel/tire vs. wardrobe/cupboard), so both are real and both
      are now reachable; verified searching "دولاب" (and Arabizi "douleb"/"doulab") now returns
      HS 4011.x tire rows.
    - Also reconfirmed (no change needed, already correct): "khanzir" → خنزير (pig) resolves
      correctly and distinctly from "janzir"/"jinzir" → جنزير (chain) — the two are not confused.
    - Re-verified full 46-case regression suite (46/46) and the 109-case coverage audit (same
      98 OK / 11 pre-existing test-authoring misses as round 4, zero new regressions).
    - Rebuilt into `pwa/`/`pwa_flat/`/`HS_Code_Finder_PWA.zip` (md5-verified).
