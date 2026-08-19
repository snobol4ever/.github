# ⛔⭐⭐⭐⭐ GOAL-SCRIP-HQ — HEADQUARTERS: THE ONE COORDINATING SESSION

**Opened 2026-08-19 by Lon in-chat (HQ seat: Claude Opus 5 → Fable 5, max effort), verbatim in substance:** *"We've been at this for 4.5 months and today is the day … We are running this ONE and ONLY Claude Code session here as HQ, Headquarters. You are in charge of all the multiple sessions which I will fire as needed as you go along and design RUNGS and STEPS for the GOALS. We have three main GOAL files currently, GOAL-SNOBOL4-100, GOAL-ICON-100, and GOAL-PROLOG-100 … You will get the honor of surpassing Sonnet and reaching MILESTONE 1, the BEAUTY self host demo test."*

## THE MODEL — HQ ORCHESTRATES, SEATS MEASURE
ONE long-lived HQ session (Lon's terminal at `/home/claude`) + N disposable worker seats Lon fires on demand. HQ designs rungs and steps, writes dispatch briefs (below), verifies worker results, moves cursors, and keeps `PLAN.md` pointing the right way. Worker seats own the heavy work — builds, sweeps, gdb, scorecards — one rung per seat, push mid-session, move their goal file's LIVE CURSOR, die. **THE FRONT FILES STAY SOVEREIGN:** every technical rung lives in its front's ONE file (`GOAL-SNOBOL4-100.md` / `GOAL-ICON-100.md` / `GOAL-PROLOG-100.md`); this file holds ONLY the coordination layer — no SNOBOL4/Icon/Prolog rung is ever specified here in more detail than a pointer.

## ⛔ HQ LAWS
1. **HQ CONTEXT IS THE SCARCEST RESOURCE.** HQ reads FINDINGs, cursors, `results.tsv` tails, and diffs — never raw build logs, never full board transcripts, never goal-file bodies it isn't acting on. Summarize into files immediately; keep HQ replies dense.
2. **PUSH-BEFORE-DISPATCH.** Worker seats clone from `github.com/snobol4ever`. A brief describing an unpushed tree is a brief describing a tree no seat can see — every dispatch is preceded by pushed HEADs in every repo the brief touches.
3. **PULL-BEFORE-TRUST.** `git fetch`/`pull --rebase` every repo before reading state, dispatching, or building; worker pushes land continuously.
4. **VERIFY-BEFORE-QUOTE.** A worker's number becomes quotable only after its seat's `handoff_status.sh` said COMPLETE and the witness is pushed. Re-run cheap instruments; trust FINDINGs with internal receipts over prose claims (VERIFY-INHERITED-BLOCKERS is the parent law).
5. **ONE DISPATCH = ONE RUNG = ONE DELIVERABLE.** A brief needing "and then" twice is two briefs.
6. **EVERY DISPATCH IS WRITTEN HERE FIRST** (DISPATCH BOARD), so any seat can be re-fired verbatim and the plan survives HQ context loss or restart.
7. **RULES.md BINDS HQ TOO** — commit identity, credential ask in-chat, no new globals without grant, ASM-DIFF-FIRST, all template laws for any code HQ itself touches.
8. **HQ RESTART PROTOCOL:** read `PLAN.md` → `RULES.md` → this file (board + cursor) → the three front cursors (headline only). The memory system points here.

## DISPATCH PROTOCOL
Lon fires a seat with one line: **`here we go — you are HQ seat D-<n>: clone per PLAN.md Session Setup, open .github/GOAL-SCRIP-HQ.md, execute DISPATCH BOARD seat D-<n> exactly.`**
Every brief carries: front + rung pointer · setup deltas beyond PLAN.md's standard setup · the ONE deliverable · the gates · the handoff clause (cursor move + FINDING + push + `handoff_status.sh` verbatim). Seat numbering: per-front session counters continue (SNOBOL4 next = s146); D-numbers are HQ dispatch ids, stable across re-fires.

## DISPATCH BOARD — live

### D-1 — SNOBOL4 M1-R0: kill `core_lib_init`'s name pre-seeding — **READY (fire after push)**
**Front/rung:** GOAL-SNOBOL4-100 · executes the s144 NEXT-SEAT list items (b)–(e); item (a) is CLOSED (see s145 cursor: `NV_bind_gva` core.c:2347 `*cell = *p` copies the seeded value into the GVA cell at bind time — do not re-trace).
**Context to read:** GOAL-SNOBOL4-100 cursors s145+s144 · `FINDING-2026-08-17-s144-*.md`.
**Oracle truth (HQ-measured 2026-08-19, `probe_seed` vs live sbl):** bare `ALPHABET UCASE LCASE digits nl tab semicolon` are ALL empty in SPITBOL (`A[0] U[0] L[0] d[0] nl[0] tab[0] semi[0]`) and `epsilon` is a null STRING — while SCRIP seeds `A[256] U[26] L[26] d[10] nl[1] tab[1] semi[1]` and a PATTERN. Bare `ARB BAL REM FAIL` are PATTERN in BOTH engines (correct — keep).
**The fix:** gate the character/string convenience block `core.c:1816–1844` **plus** `NV_SET_fn("ALPHABET",…)` (~line 1663) behind `SCRIP_SEED_NAMES` (getenv, default OFF = manual-correct blank slate; =1 restores legacy byte-identically for bisects — killswitch-inversion discipline, R-7). KEEP the `ARB/BAL/FENCE/ABORT/FAIL/REM/SUCCEED` pattern-value registrations that follow. DO NOT touch `keywords.c`'s `&`-path (`rt_keyword_read*` hardcodes `&nl`/`&digits` etc. — a separate extension surface, out of scope). Note `runtime_shim.h INIT_fn`/`inc_init` is dead csnobol4-archive shim — ignore.
**The instrument (primary):** suite A/B on ONE build — both killswitch arms over `demos crosscheck patterns feature_test csnobol4_suite probes_misc` both modes. Any row that DEGRADES under default-OFF depended on the seeding: if it's a SCRIP-authored test, EDIT it to self-assign (manual-correct); if oracle-blessed, mint the exception loudly. Any row that IMPROVES was poisoned (the beauty class). HQ pre-census (bare-word files, corpus/SCRIP-test): nl 72/2 · epsilon 87/3 · UCASE 90/8 · LCASE 89/7 · digits 57/2 · tab 55/0 · ALPHABET 42/6 — most self-assign per beauty's own idiom; the A/B decides, not the grep.
**Gates:** full rebuild · witness `corpus/probe/m1/m1_alphabet_unreached_capture` green BOTH modes · suite A/B table in the FINDING · `.s` md5s must NOT move (runtime-.so change only; if they move, stop — scope leak).
**Then:** re-run beauty self-host both modes (`beauty.sno < beauty.sno`, oracle needs `-bf`), diff against the INPUT FILE. Byte-identical both modes ⇒ **M1 EARNED — say it in the cursor in capitals.** Else mint the FINDING on the first divergence + smallest repro, push, stop (END-OF-CONTEXT LAW).
**Handoff:** GOAL-SNOBOL4-100 cursor s146 · push all repos · `handoff_status.sh` verbatim.

### D-2 — SNOBOL4 demos: claws5 SIG11 ×3 root cause — **READY (fire after push; parallel-safe with D-1)**
**Front/rung:** GOAL-SNOBOL4-100 (demos suite; supports M1's beauty_suite weight, does not block M1-R0).
**Fact base (s145 demos board):** `claws5.sno`/`claws5-match.sno`/`claws5-match-fence.sno` SIG11 both modes at HEAD while sibling `treebank-match` PASSES; oracle runs claws5 fine (rows were graded, not ORACLE_FAIL). Inputs: `claws5.input`/`CLAWS5inTASA.dat`.
**Deliverable:** ASM-DIFF-FIRST root cause — ablate claws5-match toward the smallest SIG11 witness (mint into `corpus/probe/`), diff its `--compile` `.s` against a passing sibling; gdb only after. FINDING + witness pair pushed. A fix ONLY if it fits behind a killswitch with the standard gates; otherwise investigation-only is a complete deliverable.
**Handoff:** cursor move (their own s-number) + push + `handoff_status.sh` verbatim.

### Parked (design next, fire later): D-3 json RC1/RC1+TIMEOUT · D-4 porter RC1/ASM_FAIL + treebank RC1 · D-5 calculator-1 m4-only RC1 (m3≡m4 violation, likely cheap) · Icon/Prolog fronts get D-seats once their next rungs are cut by HQ from their own cursors.

## THE M1 CAMPAIGN — BEAUTY SELF-HOST (the one thing "today")
**Definition (Lon s117, unchanged):** `beauty.sno < beauty.sno` output byte-identical to the checked-in INPUT FILE, BOTH modes; no pinned md5 ever. Weights: beauty_self 20 + beauty_suite 15 of META 100.
**Chain of custody of the blocker:** s121–s133 defer/resume + port ladder → s141 ζ-SM instrument (beauty reads zero violations) → s142/143 ZSM crash cleared (SIGABRT→exit 0), `-INCLUDE` diagnosis RETRACTED → s144 root cause gdb-proven: `core_lib_init` pre-seeds `nl`/`tab`/… desyncing beauty's hand-built `&ALPHABET` grammar → s145 (HQ): `NV_bind_gva` mechanism closed by source; ARBNO-TAIL-BETA landed default ON (nested-ARBNO backtracking — beauty's grammar shape), demos 13/22 m3.
**Ladder:** M1-R0 = D-1 (the seeding fix) → M1-R1 = beauty fixed-point re-run (inside D-1) → M1-R2 = beauty_suite 17 drivers → M1-SUP (parallel, non-blocking) = D-2..D-5 demos remainder.

## THE CAMPAIGN SO FAR — measured from git 2026-08-19
| repo | commits | born | note |
|---|---|---|---|
| corpus | 1,844 | 2025-05-16 | Lon's SNOBOL4 hoard predates everything; org-era work from 2026-03 |
| .github | 9,148 | 2026-03-10 | HQ docs; the goal-file civilization; ~1,100–2,500 commits/month steady |
| one4all | 4,155 | 2026-03-10 | scrip-cc: SNOBOL4→C/NASM/JVM/MSIL/WASM; **frozen 2026-05-31 at Ground Zero** |
| SCRIP | 3,488 | 2026-05-31 | *"Initial commit — SCRIP fresh start from one4all working tree"*; the native-x86 era |
| **total** | **18,635** | | ~5.3 months of org effort; Lon authors ~97% of commits (seat identity law) |
**Milestone timeline:** M1 first earned s57 2026-04-28 on the one4all engine (VOID — to be re-earned native, per PLAN) · 2026-05-31 Ground Zero → SCRIP · 2026-08-15 s92/s93 SNOBOL4 consolidation (22 files → ONE) · 2026-08-15 s229 Icon consolidation · 2026-08-16 s165 Prolog consolidation · 2026-08-16 s117 fixed-point ruling · 2026-08-18 s144 beauty blocker root-caused · **2026-08-19 HQ stood up.**

## STATE BOARD — the three fronts (HQ-maintained)
| front | cursor | headline | next |
|---|---|---|---|
| SNOBOL4 | s145 (2026-08-19) | ARBNO-TAIL-BETA default ON · demos 13/22 m3 · 12/22 m4 · seeding blocker fully specified | **D-1 fires M1-R0** |
| Icon | s229 era (see file) | R-0 resurrect default arm; triple watermark at `07d6eae7` | HQ cuts next rung from its cursor before any D-seat |
| Prolog | s166 (2026-08-16) | R-0h landed; clause/recursion witnesses root-caused; PL-Z-1a γ-retain opt-in | same |

## LIVE CURSOR — HQ
**2026-08-19 HQ-1 (Fable 5):** file minted · history scan done (numbers above) · M1 ladder cut · D-1/D-2 briefs READY, gated on the credential push · SNOBOL4 s145 cursor moved in its own file · PLAN.md row added. NEXT: push all repos (credential asked in-chat) → Lon fires D-1 (+D-2 in parallel) → HQ verifies D-1's suite A/B and beauty re-run, then cuts M1-R2 or the next blocker rung from the FINDING.
