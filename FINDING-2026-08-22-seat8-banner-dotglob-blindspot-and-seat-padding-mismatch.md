# FINDING 2026-08-22 seat8 — `s4e_msg.sh banner` PRINTED "NOTHING LANDED" OVER REAL, PUSHED WORK: TWO BUGS, BOTH FIXED

**Trigger:** ran `bash scripts/s4e_msg.sh banner` by hand (Lon asked to see it) right after a session that produced two real `.github` commits (a FINDING plus a `LIVE CURSOR` update on `diag-regs-stmt-and-bb`, both pushed, `handoff_status.sh` reporting COMPLETE). The banner printed **"⚠ NOTHING LANDED — tree is clean and safe to /clear, but this session produced NO commit and NO FINDING."** That is the exact "non-empty is not alive" false-signal class this project has been bitten by before (the missing-oracle all-FAIL board, the vacuous `MEDIUM_*` gate at s168) — this time in the one line Lon reads from a fleet seat. Investigated rather than trusted, per that same house habit.

## 1. BUG A — THE `.github` CLONE IS INVISIBLE TO FOUR OF THE SCRIPT'S OWN CHECKS

`banner`'s `cmts`/`onlyhere` computations and the `diverged` pre-rewrite-clone check all loop `for r in "$S4E"/*/`; `fleet`'s per-seat tree check loops `for r in "$root"/*/`. Bash's bare `*` glob does **not** match dot-directories by default, and `.github` is exactly that — so all four loops silently skip it, on every seat, every time, and always have (this predates today's session). Verified directly:
```
for r in /home/claude08/*/; do echo "$r"; done          → corpus/ SCRIP/                 (no .github)
( shopt -s dotglob; for r in /home/claude08/*/; do echo "$r"; done )  → .claude/ corpus/ .github/ SCRIP/
```
Consequence by call site:
- `cmts` (banner, line ~131): commits landed in `.github` this session never count — today's proximate trigger, since the loud "NOTHING LANDED" headline was itself added earlier today (Lon: *"Why are you not giving any feedback whatsoever as to the level of success?"*), turning a previously-cosmetic gap into a false headline.
- `onlyhere` (banner, "safe to /clear" gate): dirty or unpushed `.github` state reads as 0 regardless of the real tree — a seat with real uncommitted `.github` work could be told it's safe to `/clear` when it is not.
- `diverged` (banner, pre-rewrite-clone STOP check): a `.github` clone predating the 2026-08-21 `filter-repo` rewrite would never trip the "⛔ STOP — PRE-REWRITE CLONE" warning, the one guard that exists specifically to catch that class.
- `fleet`'s per-seat `dirty`/`unpushed` counts (Lon's whole-fleet health view): same blind spot, fleet-wide, every time `fleet` runs — Lon's own words on why this view exists: *"I'll not read much but I will check on the health."* A dashboard that can't see one of three repos in every seat is a bigger risk than one wrong banner line.

**Fix:** `shopt -s dotglob` added once, right after `set -u`. Audited every other glob in the file first (`*.claim`, `*.msg`, `*/*`  the topic-validator) — all are suffix/content-anchored, none can ever match a dot-led name in this system (messages are named `<epoch>-<seat>-<topic>.msg`, claims `<topic>.claim`, never leading-dot), so enabling it fleet-wide has no other observable effect. The one new entrant, `.claude/`, is not a git repo, so the pre-existing `[ -d "$r/.git" ] || continue` guard at every one of the four sites filters it out for free — confirmed by re-running `fleet` post-fix across all 12 seats + hq with no errors and no spurious rows.

## 2. BUG B — `$ME` WAS ZERO-PADDED TODAY, FINDING FILENAMES NEVER WERE

`fnd` (banner's FINDING-attribution count) greps added `.github` filenames for `-e "$ME"`. `$ME` became `seat08`-style today (SCRIP `568bf098`, "Lon s255": zero-padded seat ids fleet-wide). Checked the entire existing corpus:
```
ls FINDING-*.md | grep -c "seat0[0-9]"     → 0
ls FINDING-*.md | grep -c "seat[1-9][^0-9]" → 24
```
**Zero** of the 202 `FINDING-*.md` files in this repo — including both of my own from earlier this session — use the zero-padded spelling; all 24 seat-attributed ones use the old one (`seat8`, `seat4`, `seat1`, …). The zero-padding change touched `$ME` fleet-wide but nobody's file-naming habit, so `grep -ci -e "$ME"` against `seat08` matches **nothing, for any single-digit seat, permanently**, unless the row-topic string happens to also appear literally in the filename (coincidental, not general — it's why bug A's fix alone still under-attributes anything named the old way).

**Fix:** compute `mealt="${ME/#seat0/seat}"` (prefix-anchored, so `seat08→seat8`, `seat01→seat1`, … `seat09→seat9`; no-op for `hq`/`seat10`/`seat11`/`seat12`, which never had a single-digit form) and grep both spellings. Did not rename any existing FINDING file or change the naming convention going forward — that is a fleet-wide habit decision, not a detection-script bug, and is Lon/HQ's call, not mine.

## 3. VERIFIED FIXED, RE-MEASURED, NOT ASSUMED

Before: `bash scripts/s4e_msg.sh banner` → *"⚠ NOTHING LANDED... NO commit and NO FINDING."* — with two real pushed `.github` commits sitting in `git log` at the time.

After both fixes: `bash scripts/s4e_msg.sh banner` → `row OPEN · 2 commit(s) · 3 FINDING(s), attributed /12h` (correctly counting the two `.github` commits from this row and the three `diag-regs-stmt-and-bb`-attributed FINDINGs written across this session's lifetime), headline flipped to `⛔ FAILURE — do NOT /clear` for the correct reason at that moment (an uncommitted fix plus `SCRIP` having moved under concurrent fleet pushes) — i.e. the banner started telling the truth in both directions, not just the direction that happened to look good. `bash scripts/s4e_msg.sh fleet` re-run clean across all 12 seats + hq post-fix, no errors, `seat08` correctly showing its own dirty-then-clean tree at each stage. `bash -n scripts/s4e_msg.sh` clean before and after both edits.

## 4. WHAT THIS SESSION DID AND DID NOT DO

- Fixed `SCRIP/scripts/s4e_msg.sh` (2 small, additive edits — one `shopt`, one widened grep + one variable). Not codegen, not templates, not `x86_asm.h`, not a runtime sink — the regen sequence (RULES.md handoff step 4) does not apply. Committed and pushed to `SCRIP` (`63b78eef` → origin `6720fbc2`) ahead of this `.github` FINDING, per "push code repos before `.github`."
- Did not rename any `FINDING-*.md` file, and did not change the seat-naming convention — flagging the mismatch, not resolving which spelling is canonical going forward.
- Noted, not touched: `SCRIP` carried a stale, zero-diff "reverting commit `7dd59a06`" sequencer state (pre-dating this session, "all conflicts fixed" but never finalized) — out of scope for this row, and the subsequent `git pull --rebase` appears to have cleared the marker as a side effect (working tree clean, nothing lost — the resolution was already a no-op against HEAD). Not investigated further; unrelated to this FINDING's subject.
- `diag-regs-stmt-and-bb` itself is untouched by this detour — still correctly blocked, per the separate same-session FINDING `FINDING-2026-08-22-seat8-diag-regs-still-blocked-free-r11-closed-over-live-survivor.md`.

## 5. FOR HQ

Both fixes are live at `SCRIP` `6720fbc2`. Worth a fleet-wide broadcast rather than waiting for each seat to hit it independently — every seat's `.github`-only work has been under-counted by `banner`/`fleet` for as long as this script has existed, and the zero-padding gap bites every single-digit seat (1–9) the same way. No ruling needed to act on bug A (pure bug, no design tradeoff); bug B's fix is a tolerant detection widening, not a convention decision, so it also needed no ruling to land — surfacing both here so the fact is on record, not asking permission after the fact.
