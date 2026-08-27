# FINDING — `CLAUDE.md` drift audit: the top banner named the WRONG MODE, and three cured/retired facts still read as live

**Seat:** `hq_P` (HQ-PERFORMANCE, `/home/claude_P`) · **s273** · 2026-08-26
**Trees graded (after `merge --ff-only origin/main` in all three):** SCRIP `22af6afb` · corpus `14c5cf745` · .github `affa6c3f`
**Instrument:** execution and `ls`/`grep` census, never prose. Every claim below was re-taken on the pulled tree.

## Why this was worth a FINDING

`CLAUDE.md` is injected into every session in this root before anything else. A stale line there is not a stale
document — it is a **standing instruction**, and it outranks the seat's own reading of the tree. Four entries had
drifted past "approximate" into "actively wrong", and one of them was the file's first and largest banner.

## ⛔ 1. The mode banner named the wrong mode (worst of the four)

`CLAUDE.md` opened with `WHICH MODE ARE YOU IN? THERE ARE TWO. DUO IS THE DEFAULT.` and, in the paragraph below it,
**`If nobody has said FLEET, you are in DUO.`**

- `/home/resources/postoffice/MODE` line 1 reads **`FLEET-16`** (Lon, in-chat to CEO, 2026-08-24 s272 — he fired 4
  more over the 12).
- The `UserPromptSubmit` hook already injects `MODE: FLEET-16` at every prompt, and the MODE file's own header says
  *"never assume a mode from prose."*
- `SCRIP/scripts/s4e_msg.sh:31` carries the cure verbatim: *"s266 (ceo request, Lon reporting restarted seats
  assuming DUO): MODE IS COMPUTED, NEVER ASSUMED FROM PROSE."*

⭐ **So the harness was cured at s266 and the prose that caused the bug was never removed** — it sat in the banner for
seven sessions, telling each new session to assume the mode the harness had just been rebuilt to stop it assuming.
⭐ **This is the third instance of one shape:** THE LOOP step 1 (inbox check) and step 5 (banner) were both moved into
hooks for exactly this reason. **A law that depends on a seat remembering a default belongs in the harness, not in the
seat's good intentions.** This was the last of the three still uncured.
⚠️ Consequence, and it is the mode-specific one: in `FLEET-16`, an HQ that believes it is in DUO **cures defects that
belong to seats' rows**, bypassing the queue and the claim locks — two seats then edit one file each believing it owns
it. The DUO banner's own warning (filing a row is not a deliverable) inverts into the FLEET-mode error.
✅ **Cured in-file:** banner now says COMPUTE, cites the MODE path and the hook, keeps Lon's s261 quote as history and
marks it superseded, and adds a scope note separating the (permanent, mode-independent) repeal of the s256
delegate-only law from the (mode-scoped) question of *who* cures a given row.

## ⛔ 2. `make test` was documented as a false-green trap — it was CURED at s268, by this seat

The Testing section opened *"`make test` is a false-green trap … **There is no working `make` test target at all.**"*
**Measured:** `Makefile:75` is `test: scrip` with a real recipe running exactly the blocking set —
`test_corpus_snobol4.sh` → `test_gate_emit_no_lang.sh` → `test_gate_template_medium_invisible.sh` — failing loudly on
the first red. `test-ir`/`test-all` were **deleted rather than wired**, so they are hard errors now, not silent green.
⚠️ The Makefile comment at that line reads *"This target now runs THE blocking set named in CLAUDE.md"* — **the
Makefile was pointing at CLAUDE.md while CLAUDE.md was calling it a trap.** The cure's own record never closed the loop.
⭐ The trap's *lesson* is kept in the file after the retraction: a `.PHONY` name with no recipe exits **0**, so the
failure mode is a full green suite that ran nothing — prove a new target by making it FAIL once.

## ⛔ 3. The ζ-storage selector section invited an A/B campaign over flags that hard-fail

The section read *"the live architectural axis and is selectable at the command line — **expect to A/B with these**"*
and documented three flags. **Measured by execution: all three exit `rc=2`.**
`src/driver/scrip.c:818–820`, retired s270 (strip wave 4), driver's own message: *"the four zeta configs are ONE (Lon,
via CEO-11) — there is nothing left to select. Storage is cell-stack, port is forth, zeta is zls2, always."*
The env twins `SCRIP_ZETA_STORAGE` / `SCRIP_ZETA_PORT` are **gone from `src/` entirely** (zero occurrences) — no back door.
⚠️ **This is the most expensive possible stale entry in *this* root specifically:** `hq_P` owns one question (Ir at
fixed work), so "expect to A/B with these" reads as a whole measurement campaign whose every arm dies before running.
⭐ Kept: the ζ taxonomy is still real and still organizes the three ⭐100 goal files; `zeta_choices.h` still exists
(~68 `ZC_*` refs) as **compile-time constants describing the one configuration**, not a runtime menu; `--dump-zeta` is
live *and* now appears in the usage text. With the axis collapsed, mode-4 bakes no `rt_zeta_set_mode` call at all —
so an `.s` diff can no longer be explained away by a ζ override.

## ⛔ 4. `SCRIP/refs/` was documented as absent; it is present and populated

*"Right now `SCRIP/refs/` does not exist at all, so those greps silently return nothing."* — **false here.**
`refs/` holds `jcon-master/` (`tran/irgen.icn` present), `icon-master/` (45 `src/runtime/*.r`), `rakudo-main/`, `roast/`.
⚠️ The failure mode is quiet in both directions: still gitignored and per-root, so an empty grep is indistinguishable
from a real "no such construct" answer. Rule kept and sharpened: **`ls` it before you grep it, and never conclude "not
in upstream" from a grep you did not first prove was searching a populated tree.**

## Smaller corrections applied

| Claim | Was | Measured |
|---|---|---|
| `.github` entries | ~454 | **629** |
| `RULES.md` | "93 long lines — small file" | **183 lines** (~2× — it is read *in full*, so the size matters) |
| `FINDING-*.md` | 236+ | **395** |
| `ARCH-*.md` / `GOAL-*.md` | 23 / 99 | **29 / 100** |
| `scripts/*.sh` | 455 (502 entries) | **485 (535 entries)**; `scripts/scrip/` subdir gone |
| `test_gate_*` | 88 | **110** |
| `bb_*.cpp` templates | ~129 | **132** |
| corpus timeout advice | `timeout 30s` | board measures **32 s** — the advice **SIGTERMs a green board 2 s short** |
| `corpus/suites/` | unlisted | **top-level**, sibling of `crosscheck/`, read as `$CORPUS/suites` (`test_corpus_snobol4.sh:121`) |
| `IDEAS.txt` at root | claimed present | **absent in this root** (lives in `/home/claude`) |
| `scrip.c:791` | 791 | 792–793 |

⛔⭐ **The counts are not merely "approximate" — they moved mid-audit.** A single `git pull` taken *during* this work
moved `.github` 628→629, `RULES.md` 172→183, `ARCH-*` 28→29, `.sh` 483→485. **The census command is now in the file in
place of trusting the numbers.**

## ✅ Corpus denominator re-verified (documentation, NOT a gate verdict)

`m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 SKIP=0 · MISSING=0`, rc=0, **32 s** — twice: at SCRIP `b992564a`/corpus
`fea43840f`, then again at `22af6afb`/`14c5cf745`. ⚠️ Both incremental `make`, **not `make pristine`** — HQ-27 still
requires pristine before any *verdict*; this re-verifies the denominator only. The long-warned-about denominator
(321→341→364→362→365) is **holding at 365**.
⭐ **Worked example of FETCH-IS-NOT-CHECKOUT, and I walked into it myself:** the first reading was taken while all
three repos were BEHIND origin — it graded a world that no longer existed. 365 happened to survive the move; next time
it will not. **`merge --ff-only origin/main` in every repo BEFORE measuring, not after.**

## ⚠️ Cross-root exposure — NOT cured, and not mine to cure

The same stale entries live in the other roots' `CLAUDE.md` (measured, not assumed):

| Root | `make test` trap | ζ A/B invitation | `refs/` absent | DUO banner |
|---|---|---|---|---|
| `/home/claude` (`ceo`) | **2×** | **1×** | **1×** | 0 |
| `/home/claude_C` (`hq_C`) | **1×** | 0 | 0 | 0 |
| `/home/claude_P` (this) | cured | cured | cured | cured |

⭐ The DUO-banner defect was **unique to this root** — the other two never carried it.
⛔ Those two files are **owned by their seats**; per the mode table at `FLEET-16` I do not edit another seat's root.
Routed to `ceo` and `hq_C` by postoffice instead. The ζ line in the CEO root is the one worth acting on first — it is
the one that invites a dead measurement campaign.

## Authority / provenance

Everything above was verified by execution or census on the pulled tree at the commits named in the header. Nothing
here is inferred from prose, including from `CLAUDE.md`'s own. Where a reading was judgement rather than measurement
(the DUO/FLEET cure-vs-route boundary in § 1), the file says so and points at `ceo` rather than stating a ruling.
