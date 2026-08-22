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

**All 6 planned features are now DONE (as of 2026-08-22).** Any further work on this app is
new scope, not part of this original plan — see "Conventions established" below for how to
carry the same build/test/deploy discipline forward.

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
