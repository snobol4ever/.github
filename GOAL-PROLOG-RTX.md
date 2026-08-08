# GOAL-PROLOG-RTX.md — The Prolog Runtime in Optimized x86-64 Assembly

**Ladder `PL-RTX`**, minted s221-PL on Lon's directive (*"Notice how GOAL-SNOBOL4-RTX and GOAL-ICON-RTX
are proceeding with replacing the C runtime with highly optimized register-aware ASM code. You do the
same… y'all will become three."*). Runs CONCURRENTLY with `GOAL-SNOBOL4-RTX.md` (`SN4-RTX`),
`GOAL-ICON-RTX.md` (`ICON-RTX`), and `GOAL-PROLOG-BB.md` (the ζ / PL-SINK ladder).

**Contract:** `ARCH-PROLOG-RTX.md` — read before any rung. It records only Prolog's deltas; the shared
step 0 is `ARCH-SNOBOL4-RTX.md` §7. Refer to shared checks BY NAME, never by letter.

---

## ⛔⛔ SYMBOL OWNERSHIP LIVES IN `RTX-CLAIMS.md`, NOT HERE

One `.so`, ~20,000 lines, six languages, three RTX ladders. Check a symbol OUT there and **push the claim
BEFORE the work**. Run `CUR_SESSION=<n> bash scripts/util_rtx_claims.sh` at session start and close.
⛔ **Orientation reads the ledger's MESSAGE BOARD, not just the gate's exit code** — the gate reports rot;
the board reports what other sessions already did. (s224 lost most of a session to skipping this.)

⭐ Prolog's hot surface is almost entirely Prolog-EXCLUSIVE (`rt_pl_dop_*`), so this ladder rarely
arbitrates against SN4-RTX or ICON-RTX. ⛔ Its real constraint is the **SINK collision with its own BB
ladder** — see §SCOPE.

---

## ⛔ STANDING RULES THIS LADDER LEARNED THE HARD WAY (one line each; FINDINGs hold the derivations)

- **Every measurement records full path + `md5sum` AND the workload set + its size.** A bare integer in a
  ranking column is unfalsifiable. Five false claims trace to basename/workload identity going unrecorded.
- **Never write push status into a doc.** `scripts/handoff_status.sh` is the only ground truth.
  (RULES.md FACT RULE (a) — has now fired on this ladder **three sessions running**: s223, s224, s225.)
- **Never quote a watermark constant from prose; re-measure, or measure a PRISTINE control.** Doc
  constants here have gone stale twice (Prolog s210-era; Icon 251/12/30 → measured 252/11/30 at s226).
- **Verify rc==0 AND that the workload reaches the symbol BEFORE timing.** s223 published a table that
  had timed a crashing program (~100% compile phase).
- **Never time a sequential per-arm loop.** Cold page cache manufactured a 3.4× that was really a null.
  Interleave and warm, or report nothing.
- **Measure whether C can take the win before writing asm.** s224's one-line `$between` hoist took
  1.047× that an asm port would have claimed. "Replace C with asm" is a means, not the goal.
- **A pipeline destroys the `$?` you are trying to measure.**

---

## ⛔ CROSS-GATE FROM `GOAL-PROLOG-BB.md` s164 (indexed by Claude, 2026-08-08 — no new measurement here)

BB s164 measured repeated runs of ONE binary spanning **649–1246 ms (bimodal)** in this container class and
**disqualified wall time** for its ladder until a deterministic instrument exists. This ladder's owed perf
gates (NEXT 1: `bench_rtx_3arm.sh`, the ~1.10× trust floor) are wall-time instruments — **run the
same-binary-twice control (BB s164 item 9) and report its spread BEFORE quoting any new × figure**, and
note s223 already found `bench_rtx_3arm.sh` cannot grade Prolog (no self-timed `ms:` window). Conversely,
this ladder's exact dynamic-count boards are the instrument family BB s164 NEXT (a) is looking for — the
two files share one instrument problem and should share one solution.

---

## ⛔ LIVE CURSOR — s226-PL (2026-07-30) — **RTX-2-PL LANDED: `rt_pl_dop_unify` IS ASM. GATES GREEN, FALSIFICATION PROBE FIRES, NO-REGRESSION MEASURED AGAINST A PRISTINE BUILD. PERF NOT YET MEASURED.**

SCRIP at `a9e1369a` + this session's 4 files. RT_OPT=`-O0`. Watermark re-proven at session start and
said out loud: **Prolog 164/164 interp + 164/164 compile, FAIL=0.**

1. ⭐⭐ **RTX-2-PL IS ASSEMBLY.** `src/runtime/rtx/rtx_plunify.S`, family gate `PLUNIFY`
   (`SCRIP_RTX_PLUNIFY`), C body → `c_rt_pl_dop_unify`. `plw_unify_vals` de-static'd to
   `visibility("hidden")` (s187 precedent; **s214 axis 2 checked FIRST** — zero template refs, so it is
   never named in emitted mode-4 TEXT and `hidden` is safe).
2. ⛔ **SCOPE IS NARROW AND THE `.S` HEADER SAYS SO.** PL-SINK-1 already inlines the fast unify arm in the
   EMITTER, so an asm fast arm here would be **vacuous by construction** (the RTX-8-SLICE3 class). What is
   ported is the ceremony every arrival pays regardless of shape: `-O0` prologue/stack shuffle, the nargs
   guard, the unwind-floor save/set/restore, and **`rt_gc_point_arr` — a real `@plt` call whose body is
   `if (!g_gc_pending) return;`** — absorbed as an inline flag test with a cold arm. `plw_unify_vals` and
   `rt_pl_deref_val` REMAIN CALLS. **One crossing deleted per arrival, not the unifier. Do not let a later
   rung read this as "unify is ported."**
3. ⚠ **THE FLOOR IS SEMANTIC.** `g_plw_unwind_floor` feeds `plc_dead_cstack`, which makes `pl_trail_unwind`
   SKIP restores below `floor+16` — a wrong floor silently changes what survives backtracking. Verified
   from the C's **disassembly** (not its source shape) that `__builtin_frame_address(0)` is `rbp` after
   `push rbp; mov rbp,rsp` = `rsp_at_entry-8`; the port builds the same frame, so the value is bit-identical.
   Likewise read from disassembly: the `nargs!=2` arm never touches the floor or the safepoint.
4. ⭐⭐ **THE EVIDENCE IS THE PROBE, NOT THE GREENNESS.** Deliberately broken asm moves the battery
   **164/0 → 128/36 in BOTH modes** ⇒ the asm executes, coverage **36/164 = 22%**, and **m4 is real
   evidence** — the s214 "never close on m3 alone" trap discharged by measurement.
   Gate ON **164/164 + 164/164**; gate OFF (C fallback) **164/164 + 164/164**.
5. ⭐ **NO-REGRESSION MEASURED, NOT ASSUMED.** Stashed to a PRISTINE build and back:
   **Icon 252/11/30 pristine == 252/11/30 ported; SNOBOL4 broad_corpus 325/2 == 325/2.**
   ⇒ this file's old Icon constant (251/12/30) was **stale, not a regression** — third stale-constant hit.
6. ⭐⭐ **`rt_pl_dop_ix_g`'s LEDGER ROW DOES NOT REPRODUCE ON ITS OWN BOARD.** Measured over all 22 of
   `corpus/benchmarks/prolog/bench/` (all rc=0, md5s recorded): **7,017 arrivals / reach 13-of-22** vs the
   row's **289,004 / 15-of-22**, deterministic across two runs, dominant program (`meta_qsort.pl`)
   byte-identical to its `.expected`. **CONTROL: four rows in the SAME sweep reproduced digit-for-digit**
   (`unify` 1,108,786 · `unify_cs` 622,812 · `unify_ci` 41,622 · `unify_lst` 10,610), and `unify` on
   `puzzle_19` reproduced s224's **1,775,371** to the digit. ⇒ the row advertises *"the SINK-deferred
   `kk==4` arm is CLEAR"*, i.e. an available RTX target. **It is not one.** ⚠ `rt_pl_dop_mkc` also drifts
   (1,018,951 vs 1,018,100, +851) — smaller, unexplained, not chased.
7. ⛔ **CLAIM ORDERING VIOLATED, DELIBERATELY AND VISIBLY.** `RTX-CLAIMS.md` requires the claim pushed
   BEFORE the work; no credential was available, so the work was done first. **Nothing is pushed.** Any
   parallel PL-RTX session must treat `rt_pl_dop_unify` as contested until the row lands.

**WATERMARK:** SCRIP = `rtx_plunify.S` (new) + `by_name_dispatch.c` + `rtx_init.c` + `Makefile`, **local
only**. corpus = untouched. `.github` = this cursor (+ FINDING + ledger row owed).
Per RULES.md this handoff is **INCOMPLETE until `handoff_status.sh` prints HANDOFF COMPLETE.**

**NEXT (in order):**
1. ⭐ **Finish RTX-2-PL's owed gates:** `util_rtx_arm_census.sh` (`COMMITS > 0`),
   `test_gate_rtx_killswitch_sets.sh PLUNIFY <bench> 4 both pl`, and 3-arm `bench_rtx_3arm.sh`
   reporting **ON/PRISTINE**. ⚠ **Expect a small or null result and say so:** 1.1M board arrivals vs
   RTX-1-PL's 13.85M, so this may sit under the ~1.10× trust floor. A null at ~0 gate tax is FREE TO KEEP.
2. **Correct the `rt_pl_dop_ix_g` row** (own row, PL-RTX) with full-path+md5+workload keys, and re-audit
   every verdict derived from the s221 board with those keys.
3. **The three rulings below** — this ladder cannot legally proceed on the biggest prizes without them.

---

## ⛔ SUPERSEDED CURSORS — condensed (full text in git; each names its FINDING)

- **s225-PL** — The s221 board IS `corpus/benchmarks/prolog/bench/` (22 files, 22/22 rc=0), reproducing
  **2,060,043 / 19-of-22 to the digit** ⇒ item 0 closed twice over. **Rebutted s224's "two ledger verdicts
  falsified": nothing was falsified** — `rt_call_arr_gen` (0 / 0-of-22) and `rt_arg_stage` (8 / 1-of-22)
  reproduce digit-for-digit *on the board*, and s224's 2,815,800 / 812,824 reproduce digit-for-digit on
  `puzzle_19`, which is **not a board member**. Two correct measurements of two different workloads.
  ⇒ **ICON-RTX: your `BLOCKED:MEASURED-ZERO` on `rt_arg_stage` is CORRECT.** Also: PLCALL kill-switch gate
  PASSES on Prolog (m3 IDENTICAL=22 · m4 IDENTICAL=22 · GATE PASS) ⇒ RTX-1-PL's correctness case closed.
- **s224-PL** — Struck s223's item 0 (*"the van Roy corpus does not execute in mode 3"* — false; 19/21 run
  rc=0). Root-caused it to **basename-keyed measurement** (`crypt.pl`/`derive.pl` each exist in four
  directories; THREE files are named `queens.pl`, differing 33× by N). Landed the one-line `$between`
  hoist at the head of `rt_call_arr_gen`'s 14-arm `strcmp` chain — **1.047×, and its residual prize is call
  overhead only** ⇒ the dispatch cost was removable in C. ⚠ Its win belongs to `puzzle_19` and **may not be
  quoted board-wide** (that arm takes 0 calls on the board). Named the emitter-side successor: `bb_call.cpp`
  bakes the callee name as a `.string` literal though **the name is a COMPILE-TIME CONSTANT** — it could
  emit `call rt_pl_between_gen` directly, deleting the dispatch AND one crossing.
- **s223-PL** — RTX-1-PL landed as asm; **1.055× on 13,850,337 arrivals / 0 bails**; falsification probe
  164/0 → 111/53 both modes. Fixed `test_gate_rtx_killswitch_sets.sh` (hardcoded `*.sno` ⇒ no Prolog or
  Icon arm at all; added `EXT`). `bench_rtx_3arm.sh` still cannot grade Prolog (no self-timed `ms:` window).

---

## ⛔⛔ SCOPE — THE RULING THIS LADDER STILL NEEDS FROM LON

Nine of the top eleven Prolog symbols are SINK'd or claimed by an **OPEN** PL-SINK rung in
`GOAL-PROLOG-BB.md`, a concurrently running session.

| rank | symbol | corpus calls | reach | PL-SINK | SINK status | PL-RTX |
|---:|---|---:|---|---|---|---|
| 1 | `rt_pl_dop_trail_unwind` | 2,114,931 | 10/22 | SINK-9 | ⏳ OPEN | ⛔ COLLISION |
| 2 | `rt_proc_call_open_det` | 2,060,043 | 19/22 | none | — | ✅ **DONE s223** |
| 3 | `rt_pl_dop_unify` | 1,108,786 | **22/22** | SINK-1 | ✅ s142 | ✅ **DONE s226** (residue only) |
| 4 | `rt_pl_dop_mkc` | ~1,018,951 | 19/22 | SINK-3 | ✅ s145 | ⚠ reduced |
| 5 | `rt_pl_dop_cmp_ne` | 880,792 | 5/22 | SINK-7 | ⏳ OPEN | ⛔ COLLISION |
| 6 | `rt_pl_dop_unwind_nothrow` | 873,060 | 16/22 | SINK-9 | ⏳ OPEN | ⛔ COLLISION |
| 7 | `rt_pl_dop_is_v` | 735,898 | 14/22 | SINK-5 | ⏳ OPEN | ⛔ COLLISION |
| 8 | `rt_pl_dop_ax_sub` | 731,498 | 12/22 | SINK-6 | ⏳ OPEN | ⛔ COLLISION |
| 9 | `rt_pl_dop_unify_cs` | 622,812 | 12/22 | SINK-1 fam | ✅ | `FREE` |
| 10 | `rt_pl_dop_ax_add` | 573,678 | 6/22 | SINK-6 | ⏳ OPEN | ⛔ COLLISION |
| 11 | `rt_pl_dop_ix_g` | **7,017** ⬅ s226, NOT 289,004 | **13/22** | SINK-4 | ✅ s148 | ⛔ **NOT A TARGET** |
| — | `rt_pl_dop_trail_mark` | 22 | 22/22 | SINK-8 | ✅ s146 | ⛔ VESTIGIAL |

**THE QUESTION.** When a Prolog symbol is hot and has an open SINK rung, does it get **(a)** SINK,
**(b)** RTX, or **(c)** SINK for the guarded fast arm + RTX for the arm SINK defers to C?

⭐ **RECOMMENDED: (c)** — the only option under which both ladders keep working. RTX's honest scope is the
residue SINK refuses (SINK-4's `kk==4`, SINK-7's out-of-2⁵³ arm, SINK-6's `div`/`idiv`/`mod` guards and any
`DT_R`, SINK-5's non-`{I,R}` tags), plus every symbol with no SINK rung. Under (a) this ladder has ~2 live
rungs; under (b) two sessions fight over one emitter/runtime boundary per symbol.
⛔ **UNTIL RULED: work only `none`-rung symbols or SINK-deferred arms.** s226 read Lon's *"replace the C
runtime with ASM, continue"* as sanctioning the (c)-shaped residue port of rung 2 — **flagged here for
correction if that reading is wrong.**

**TWO MORE RULINGS OWED:** (ii) **DUAL-ENTRY** — may PL-RTX take `rt_jmp_frame_lexprep2` (13.85 M, exactly
1:1 with `open_det`, three-language, the highest-risk cluster on either ladder)? (iii) **arbitration with
ICON-RTX over `rt_arg_stage`** — ⚠ **s225 says this one is CLOSED: the row is correct, do not unblock.**

---

## THE LADDER

- [x] ✅ **RTX-1-PL — `rt_proc_call_open_det`** — landed s223, `rtx_plcall.S`, gate `PLCALL`.
      **1.055×** on 13,850,337 arrivals / 0 bails. Three of four C levels absorbed ⇒ no call on the success
      path. Kill-switch gate PASSES both modes (s225). Step-0 record deleted s226 — it lives in the `.S`
      header and the s221/s223 FINDINGs.
- [x] ✅ **RTX-2-PL — `rt_pl_dop_unify`** — landed s226, `rtx_plunify.S`, gate `PLUNIFY`. Wrapper/ceremony
      port only (see cursor item 2). Correctness gates green + probe fires. ⏳ **Perf gates still OWED.**
- [ ] **RTX-3-PL — the SINK-deferred arms** (scope option (c) only). SINK-4 `kk==4`; SINK-7 out-of-2⁵³
      (⚠ `x86_asm.h` has only ~12 xmm hits — verify encoder forms exist for BOTH media first); SINK-6
      `div`/`idiv`/`mod` guards (`b==0`, `b==−1`; `INT_MIN/−1` traps on x86) and any `DT_R`; SINK-5
      non-`{I,R}` tags. ⛔ Do not open before the §SCOPE ruling.
- [ ] **RTX-0d-PL — widen the workload set.** `queensn`+`queens` are ~78% of board arrivals; the board
      takes `rt_call_arr_gen` **zero** times while one rung-test program takes it 2.8 M ⇒ a **coverage hole
      in the ranking corpus**. Needs list/arith/IO-shaped run-phase workloads before ranking on rank alone.
      Mirrors ICON-RTX's RTX-21-ICN. Validated members so far: 22/22 of `bench/` + `puzzle_19`.
- [ ] **RTX-12-PL — eradication (LAST).** Delete gate + `c_*` body. Cross-language per ledger hard rule 4:
      needs all three watermarks green and every beneficiary row `DONE`.

**BANKED (inherited from `GOAL-PROLOG-BB.md`, all still live):** `unary_not.sno` emits a `.string` from
uninitialised memory (poisons every `.s` byte-identity sweep); engine-wide silent-fail on undefined
predicates; int/float standard-order conflation; lexer escape three-site/two-behaviour; NO-LCO segfault;
nested-`\+` binding leak; `retractall/1` gaps; `bench/meta_qsort.pl` exhausts the cterm island **under the
loop wrapper only** (path-specific — bank it narrowly).

---

## ARCHITECTURE NOTE — WHY PROLOG'S SURFACE LOOKS DIFFERENT

Prolog's hot symbols are `rt_pl_dop_*`: runtime sinks for lowered `$op` nodes emitted by `lower_prolog.c`
through the four-port (α/β/γ/ω, δ/ε) BB machine. They are **emitted-code-only** — measured ZERO on
`hello.pl` — so Prolog's absolute dynamic counts already ARE run-phase counts and ICON-RTX's compile-phase
confound does not apply to this family. ⚠ Non-`dop` targets (`rt_proc_*`, `rt_arg_stage`, `core_lib_init`)
are **not** covered; re-measure the floor per family. Prolog's surface is the largest of the three
languages (**112 distinct symbols** vs Icon's 90, SNOBOL4's 54) while being almost entirely uncontested.

**Modes:** two only — mode 3 (`--run`, BINARY in-process) and mode 4 (`--compile`, TEXT → as+gcc). One
`.S` links into both. ⛔ Never close a session on m3 alone.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
