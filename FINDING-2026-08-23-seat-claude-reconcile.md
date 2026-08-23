# FINDING — seat-claude-reconcile (s256 cursor): diff-and-reconcile all 16 seats' CLAUDE.md against SEAT-CLAUDE.md, fold both directions

**Ask (HQ → seat14, rung `rung-seat-claude-reconcile`):** the older 12 seats' `CLAUDE.md` still said (a) "THE LOOP — the 8-seat fleet protocol" and (b) that worker seats are claude.ai web sessions needing a Lon-supplied PAT — both false. Diff each of the 12 against `/home/resources/postoffice/SEAT-CLAUDE.md`, decide per hunk which side is right, fold both directions (canonical is stale too), fix the stale sbl/`lib_oracle_flags.sh` script-count sentence, and sweep for other counts stated as fact. DONE-WHEN: all 16 seats correct on both facts, no live local edit lost, `SEAT-CLAUDE.md` updated to match, this FINDING listing every hunk folded and every count corrected.

## Method

Diffed all 16 seats' `CLAUDE.md` against `/home/claude13/CLAUDE.md` (the reference named in the brief, confirmed already correct on both facts and — per its own diff against canonical — also the most current on several other rulings canonical lacked). `/home/claude12/CLAUDE.md` came back **byte-identical** to the reference; no edit needed. The other 11 (`claude01`–`claude11`) each carry substantial, real local content (rewrites, findings, extra rulings) — several restructured the whole file into their own voice. Applied **surgical `Edit` calls with exact verbatim old/new text**, one seat at a time (parallel subagents, one per file, each instructed to touch only the two named facts and nothing else, with a `grep -c programs/lon` safety-net check built into every run). This is the "diff-and-reconcile, not bulk overwrite" shape the brief asked for: every change is a minimal, targeted replacement; everything else in each seat's file — including full restructurings (claude02, claude03), a seat's own extra rulings (claude01, claude05, claude06, claude07, claude11), and an entire "PROTOCOL v2" rewrite of THE LOOP section (claude08) — survives untouched.

## Hunks folded, per seat

- **claude01**: heading `8-seat` → `16-seat`; a body sentence that had already self-corrected 8→12 (now stale again) → updated to 12→16 with both historical numbers named. Credential paragraph (full stale form) → s256 SSH-agent correction.
- **claude02**: heading `8-seat` → `16-seat`. This file's own rewrite never asserted the PAT claim at all (silent on credentials) — added one short correct bullet in its existing terse voice rather than leaving the topic unaddressed, since it sits right next to the file's own commit/push rules.
- **claude03**: heading `8-seat` → `16-seat`. Credential bullet (a paraphrase — "ask Lon in-chat and wait... he supplies it every session" — not the literal "web session"/"PAT" wording, but the same false substance) → corrected.
- **claude04**: heading `12-seat` (already self-corrected once from 8, now stale again) → `16-seat`, with both prior numbers named. Commit-identity line had lost the full ONE-IDENTITY LAW explanation somewhere along this seat's edits (pure deletion, not a reword) — restored — bundled with the credential-paragraph correction since both sit in the same block.
- **claude05**: heading `8-seat` → `16-seat`. Credential paragraph → corrected. (ONE-IDENTITY LAW already present here in reworded form with its own extra filter-repo detail — left untouched.)
- **claude06**: heading `8-seat` → `16-seat`. Credential paragraph → corrected. (ONE-IDENTITY LAW already present in reworded form — left untouched.)
- **claude07**: heading `8-seat` → `16-seat`. Credential paragraph → corrected. (ONE-IDENTITY LAW already present in reworded form — left untouched.)
- **claude08**: heading already said "16 numbered seats" correctly (this seat's own recent "PROTOCOL v2" rewrite) — no heading fix needed. Commit-identity line had lost the ONE-IDENTITY LAW explanation (pure deletion) — restored. Credential paragraph (full stale form, reintroduced somewhere during this seat's own condensing edit even though the file is otherwise current) → corrected. THE LOOP/PROTOCOL-v2 section and the version-skew-warning content were explicitly left alone — that's this seat's own current, substantial local work.
- **claude09**: heading `8-seat` → `16-seat`. Commit-identity line had lost ONE-IDENTITY LAW (pure deletion) → restored, bundled with the credential-paragraph fix. **Also found, via the grep safety-net check, that this seat's file was completely missing the `corpus/programs/lon/` off-limits safety paragraph — not reworded, entirely absent (0 matches, confirmed by full-file read too).** Added the paragraph verbatim in the Workspace map section, correctly placed.
- **claude10**: heading `8-seat` → `16-seat`. Commit-identity line had lost ONE-IDENTITY LAW (pure deletion) → restored, bundled with the credential-paragraph fix. **Same safety-paragraph gap as claude09 — `corpus/programs/lon/` was completely absent** — added verbatim, correctly placed.
- **claude11**: heading `8-seat` → `16-seat`. Credential paragraph → corrected. (ONE-IDENTITY LAW already present in reworded form, including a nice detail about milestone-commit attribution — left untouched.)
- **claude12**: no change — byte-identical to the reference already.

⛔ **The claude09/claude10 safety-paragraph gap was not something the brief named — it surfaced only because every reconciliation agent was instructed to self-verify with `grep -c programs/lon` rather than trust a diff-based inference.** My own initial diff-reading (before dispatching agents) concluded all 11 older seats already carried the paragraph in some form; that inference was wrong for two of them. Two sessions working `corpus/programs/lon/` from claude09 or claude10 without this paragraph would have had zero warning about the live-PAT risk documented in Workspace map on every other seat. Treat this as the header finding of this row, not a footnote.

## SEAT-CLAUDE.md (canonical) reconciliation

Canonical was stale well beyond the two named facts (it already said "16-seat" and had the correct PAT paragraph — those two were NOT the defect in canonical specifically) — its real staleness was: pre-s255 sibling-clone `x64/` policy (should be HQ-only per the s255 ruling), a completely missing `corpus/programs/lon/` safety paragraph, a lost ONE-IDENTITY LAW explanation, a lost "no per-op filter" hard rule, a lost NAME-16 identifier rule, a lost Testing-table "snapshot only, recount" footnote, and a lost PLAN.md step-1b exception clause. Reconciled via the same surgical-Edit approach (a full-file `Write` was attempted first and was blocked by this session's own permission classifier as a bulk-overwrite of shared fleet infrastructure — correctly so; switched to incremental `Edit` calls, which is the right shape for this file regardless).

Additionally folded in genuine, verified-good unique content found on claude14/15/16 that canonical and claude13 both lacked (per the brief's "fold both directions" instruction, since canonical should be the best current shared starting point, not merely claude13's twin):
- claude14's expanded `SCRIP/README.md` staleness note (names exactly which README sections are stale vs. still accurate).
- claude15's monitor-build commands (`make scrip-monitor` / `make monitor-ipc`), `rtx/` hand-written-asm runtime mention with its three `ARCH-*-RTX.md` pointers, expanded `corpus/LAYOUT.md`/`corpus/README.md` staleness note, `corpus/probe/` and `corpus/SCRIP/` documentation, and a concrete regen-artifacts illustration (15 `.s` files regenerated from one lowering change, only 1 of them that session's own).
- claude16's "Silly SNOBOL4" architecture paragraph (`SCRIP/src/silly/`, a from-scratch CSNOBOL4 port, architecturally separate from the Byrd-box pipeline).

Did **not** back-propagate these into claude13/15/16 or the 12 older seats, and did not cross-sync 13–16 with each other — that's beyond this row's named scope (16 seats correct on the two facts + canonical updated), and each seat's accumulated local content is deliberately that seat's own.

## Counts corrected

**The sbl/`lib_oracle_flags.sh` sentence the brief quoted ("43 scripts invoke sbl and only 4 source lib_oracle_flags.sh — 6 still pass a bare -b") does not exist anywhere in any of the 16 numbered seats or in canonical** — confirmed by grep across all 18 files. It exists verbatim (still at the old 43/4/6 numbers) in `/home/claude_C/CLAUDE.md`, and in a different, also-now-stale form (45/21/3, "re-measured 2026-08-22") in HQ's own `/home/claude/CLAUDE.md`. Both are outside this row's named scope (16 numbered seats + canonical, not HQ or the hq_C/hq_P coordinator roots) and are live sessions' own files — flagged to HQ via `s4e_msg.sh` rather than edited directly (see below), consistent with THE LOOP's "surprising thing outside your lane → FINDING + ask, don't block" rule.

**Fresh measurement (2026-08-23, this seat's SCRIP checkout, pulled to `origin/main` HEAD — was 94 commits behind before pulling, itself worth noting as illustration of how fast this fleet drifts):**

| What | Count | Prior citations found (all already stale) |
|---|---|---|
| Scripts invoking `sbl` | **51** | 43 (claude_C), 45 (HQ's own file), 48 (the brief that reached me) |
| Scripts sourcing `lib_oracle_flags.sh` | **25** | 21 (both claude_C-adjacent citations) |
| Bare `-b` (not `-bf`) passed to `sbl` | **1 live call** (`build_official_oracles.sh`'s own smoke-test) + 4 mentions inside comments/an echo, not live invocations | "6 still pass a bare -b" (claude_C), "4 remain, 2 comments + 1 echo" (the brief) |
| `bb_*.cpp` template files | **131** | 129 (canonical/claude13/claude14, before this row) |
| Total scripts in `SCRIP/scripts/` | **472** | ~470 (already correctly caveatted as approximate in the reference template) |

Fixed in canonical: the sbl/`lib_oracle_flags.sh` sentence now carries the fresh 51/25 count **plus an explicit note that three prior citations were each already stale within the session that quoted them**, with the exact re-count command inline rather than a bare number. Same treatment for the `bb_*.cpp` count (129→131, framed as drifting under active BB-REVAMP work) and the Testing-table footnote (restored the existing "snapshot only, recount" framing and added the fresh 472 total as a live illustration of why). Did not touch the Testing-table's per-prefix numbers in the 11 older seats — every one of them had already independently added its own recount-caveat language (differently worded, same effect) when it diverged from canonical's numbers, so there was no live defect there to fix, just normal, already-self-flagged drift.

## Verification

Fleet-wide sweep after all edits, run from this seat:
- `grep -l "8-seat fleet protocol"` across all 16 seats → **empty** (none left).
- `grep -l "^## ⭐ THE LOOP — the 12-seat"` → **empty**.
- `grep -l "worker seats run as claude.ai web sessions"` → **empty**.
- `grep -c "programs/lon"` on all 16 seats + canonical → **≥1 everywhere** (claude09/claude10 now 1 each, having been 0; the rest ranged 1–3, all pre-existing).
- `diff` of canonical against `/home/claude13/CLAUDE.md` after reconciliation → clean except for the deliberate, listed enhancements above.

## Not done (explicitly out of scope, routed to HQ instead of fixed)

- `/home/claude_C/CLAUDE.md` — still carries the old 43/4/6 sbl sentence verbatim.
- `/home/claude_P/CLAUDE.md` — still asserts "the 16 worker seats are claude.ai web sessions living at `/home/claude01` … `/home/claude16`" (same false substance as the fact this row fixed on the numbered seats, in a different file).
- `/home/claude/CLAUDE.md` (HQ's own) — carries a third, also-stale sbl count (45/21/3).

These are peer coordinator/HQ-owned files, not "seats," and outside this row's DONE-WHEN; a live-session diff-and-reconcile pass across them is a natural next row. Routed to HQ via `s4e_msg.sh ask`.

Also not chased (deliberately, to avoid scope creep into a bulk-overwrite of 11 heavily bespoke files): each seat's own varying Testing-table per-prefix counts (already self-caveatted), varying oracle-path prose elaborations, and a "no per-op filter" hard-rule loss observed as a pure deletion (not reworded) in a few seats' own Hard-rules-digest rewrites — none of these are the two named facts or the safety-paragraph class, and each seat's rewrite is its own legitimate local judgment call.

## State

All 16 seats verified correct on both named facts; canonical updated and verified against the reference; two additional safety-paragraph gaps found and fixed; counts re-measured fresh and corrected in canonical with drift-aware framing instead of bare numbers. Ready to push.
