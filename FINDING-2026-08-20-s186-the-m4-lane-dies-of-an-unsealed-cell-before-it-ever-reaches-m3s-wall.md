# FINDING — 2026-08-20 s186 (seat8 `/home/claude8`, Claude Opus 5; queue row 2 `m1-m4-lane`)
# ⭐ THE M1 MODE-4 LANE, MEASURED FOR THE FIRST TIME: m4 STOPS AT THE SAME INPUT LINE AS m3 AND PRODUCES THE SAME BYTES, BUT IT DIES OF A DIFFERENT AND EARLIER WALL — AN AB fn_cell THAT THE COMPILER PROCESS SEALED AND THE EMITTED BINARY NEVER INHERITED.

**ROW TYPE: MEASUREMENT.** Nothing was fixed. The three instrument defects found on the way are routed as their own row (`m1-board-instrument`), per the brief's "a fix found on the way gets its own row so this one stays one deliverable".

**WATERMARK.** SCRIP `fb2d505c` · corpus `f1bbf8d0` · `make pristine` before every verdict (HQ-27) · RT_OPT `-O0` (O0-DEV, unlabelled numbers below are wall-clock at `-O0`). Oracle `x64/bin/sbl` verified ALIVE before any table was trusted (PLAN.md 1b: an absent oracle prints a plausible, entirely false all-FAIL board). All 8 checked-in `m1_lad_*.ref` re-verified against the live oracle this session — **zero oracle drift**.

---

## 1. THE BOARD READING — m4's FIRST EVER

```
=== M1 PROGRESS BOARD — beauty.sno fed INCREASING PREFIXES OF ITSELF (622 lines total) ===
    judge = live oracle (sbl -bf) on the same input; full-file rung also checked for the FIXED POINT
   lines  m3 (--run)               m4 (--compile)
       1  PASS                     PASS
       2  PASS                     PASS
       5  PASS                     PASS
      10  SEGV                     rc1
      20  SEGV                     rc1
      40  SEGV                     rc1
      80  SEGV                     rc1
     160  SEGV                     rc1
     320  SEGV                     rc1
     622  SEGV                     rc1
------------------------------------------------------------
M3 rungs green: 3/10   first red at: 10
M4 rungs green: 3/10   first red at: 10
```

**Hand-bisected `--rungs "5 6 7 8 9 10"` (the script's own `--bisect` is m3-only; see §5):**

```
       5  PASS   PASS        7  PASS   PASS        9  SEGV   rc1
       6  PASS   PASS        8  SEGV   rc1        10  SEGV   rc1
M3 first red at: 8     M4 first red at: 8
```

⭐ **BOTH MODES FAIL FIRST AT LINE 8 — the bare label `START`.** Lines 1–7 are comment lines, which beauty echoes through `Line POS(0) ANY('*-')` → `OUTPUT = Line` without ever reaching `Src POS(0) *Parse *Space RPOS(0)`. Line 8 is the first line that makes the input a program to be parsed. The brief's stated bisect trigger — *"--bisect if the m3 and m4 first-red lines differ"* — **does not fire: they are the same line.** The modes disagree about the DEATH, never about the LOCATION.

**m4 COMPILES AND LINKS BEAUTY CLEANLY AT EVERY RUNG.** No rung produced `COMPILE-FAIL` or `LINK-FAIL`. `--compile` emits 12,911,745 bytes / 172,891 lines of `.s`; `gcc -no-pie` links a 1,827,976-byte binary. Every m4 red is a RUN-TIME red.

---

## 2. THE DELIVERABLE — PER-WITNESS m3 BESIDE m4

| witness | bytes | oracle | m3 | m4 | stdout m3≡m4 | stdout==ref |
|---|---|---|---|---|---|---|
| `m1_lad_empty` | 1 | ok | **SEGV** rc139 | **rc1** Error 22 | **YES** | no / no |
| `m1_lad_barelabel` | 2 | ok | **SEGV** rc139 | **rc1** Error 22 | **YES** | no / no |
| `m1_lad_end` | 4 | ok | **SEGV** rc139 | **rc1** Error 22 | **YES** | no / no |
| `m1_lad_comment` | 9 | ok | **SEGV** rc139 | **rc1** Error 22 | **YES** | no / no |
| `m1_lad_stmt` | 11 | ok | DIFF rc0 | DIFF rc0 | **YES** | no / no |
| `m1_lad_labelstmt` | 12 | ok | DIFF rc0 | DIFF rc0 | **YES** | no / no |
| `m1_lad_two` | 18 | ok | DIFF rc0 | DIFF rc0 | **YES** | no / no |
| `m1_lad_match` | 20 | ok | DIFF rc0 | DIFF rc0 | **YES** | no / no |

Both failure modes are **STABLE 5/5** (m4 `rc=1` ×5; m3 `rc=139` ×5) — neither is the intermittent load-dependent class s184 recorded DORMANT.

⭐ **THE m3 ≡ m4 DESIGN INVARIANT HOLDS ON OUTPUT EVERYWHERE, INCLUDING THE MILESTONE RUNG.** Full self-host (`beauty.sno` fed itself): m3 **259 bytes md5 `e883e4b862ba`** rc=139 · m4 **259 bytes md5 `e883e4b862ba`** rc=1 · **byte-identical**, and the same md5 s183/s184 recorded. The oracle half of M1 was re-proved in passing: `sbl -bf beauty.sno < beauty.sno` = **40971 bytes == the 40971-byte input**, still the fixed point. **m4 is not "further behind" m3. It emits exactly the same wrong bytes and then dies differently.**

---

## 3. ARE m4's WALLS THE SAME CLASSES AS m3's?

### CLASS B — **SAME CLASS, BOTH MEDIA.**
`Parse Error` + `Src`, rc=0, graded by DIFF. m3 and m4 stdout byte-identical on all four class-B witnesses. Nothing mode-specific. **Corroborates HQ-75 s183 independently:** if the blocker is the two-level `*defer` floor (`defer-depth-floor`), then it is a LOWER/graph-level defect that both media inherit from one codegen — which is exactly the shape measured here. Class B needs no m4 row of its own.

### CLASS A — **NOT THE SAME. m4 HAS ITS OWN, EARLIER WALL.**
m3 dies of the known wild jump — `SIGSEGV` at `0x00007ffff7ffd000 in _rtld_global`, then `#1 0x0`: the exact signature s182 addendum 1 recorded and s183 named the pass-thru continuation defect (row `m1-composed-wild-jump`, ARCH-PASSTHRU law 0a/2).
**m4 never reaches it.** It raises `** Error 22 in statement 0 / Undefined function called` first, from `rt_ab_undef_fn_stub` (`rt.c:511`).

---

## 4. ⛔ THE m4-ONLY CLASS, NAMED — `m4-eval-fragment-reallocates-unsealed-cells`

**MEASURED, NOT INFERRED. AB fn-cell census taken at the fault in both modes (gdb, `g_ab_fn_names`/`g_ab_fn_cells`, `emit.cpp:1463-1477`):**

| | m3 (`./scrip beauty.sno`) | m4 (linked binary) |
|---|---|---|
| cells allocated at fault | **408** | **13** |
| sealed | **393** | **0** |
| holding `rt_ab_undef_fn_stub` | **15** — every one an `alpha$EXPR$*` fragment thunk | **13 — ALL OF THEM** |
| `alpha$Shift` | **sealed** slot 73 `0x7fffee024014` | **STUB** |
| `alpha$Reduce` | **sealed** slot 75 `0x7fffee025014` | **STUB** |
| `alpha$nTop` | **sealed** slot 129 `0x7fffee040014` | **STUB** |

The m4 table in full — 3 main-image procs + 10 EVAL thunks, none sealed:
`alpha$Reduce · alpha$nTop · alpha$Shift · alpha$EXPR${173,170,171,172,157,158,168,149,169,3F3}`

**⭐ THE MECHANISM IN ONE SENTENCE: in m4 the seal happens in the COMPILER process and is thrown away, and the emitted binary's own runtime fragment compiler then re-allocates the same names and finds them unsealed.**

Two independent receipts:

**(a) The m4 `.s` bakes no cell at all.** `grep -c` over the 172,891-line emitted assembly: `alpha$` → **0**, `fn_cell` → **0**, `rt_ab_undef_fn_stub` → **0**. Nothing about the AB cell store survives the TEXT medium. (This is `bb_ab_cell_addr` answering NULL for TEXT by design, RULES s172 — the design is not at fault here; the point is that *nothing takes its place at run time*.)

**(b) The allocation road, at one breakpoint.** `bb_ab_slot_for(fname="alpha$Reduce")` in the running m4 binary:

```
#0  bb_ab_slot_for (fname="alpha$Reduce")        emit.cpp:1468
#1  bb_ab_fn_cell_ptr (fname="alpha$Reduce")     emit.cpp:1477
#2  operator() (closure)                         bb_call_proc_staged.cpp:341
#3  bcps_det_arm ()                              bb_call_proc_staged.cpp:316
#4  bb_call_proc_staged_str (pBB=0x4f28f0)       bb_call_proc_staged.cpp:1092
#5  bb_call (pBB=0x4f28f0)                       bb_call.cpp:523
#6  walk_bb_node_inner / walk_bb_node            emit.cpp:1309 / :991
#8  emit_drive                                   emit.cpp:1571
#9  codegen_flat_chain_body (prefix="proc_flat") emit.cpp:3292
#10 emit_chain                                   emit.cpp:3630
#11 eval_thunks_emit_from (pc0=0)                runtime_eval.c:249
```

The EVAL source being compiled at that moment is beauty's own grammar rule, verbatim from the frame:
`epsilon . *Reduce('ExprList', *(GT(nTop(), 1) nTop()))`
— i.e. the runtime fragment compiler, building beauty's grammar (`semantic.inc` builds every rule via EVAL), requests `alpha$Reduce` for a **main-image** callee, `bb_ab_slot_for` allocates a fresh slot initialised to `rt_ab_undef_fn_stub` (`emit.cpp:1472`), and that stub address is baked into the fragment's `x86_jmp_via_cell` site. The arrival at the stub is by JUMP, not CALL, so the crash has no honest caller frame — frame #1 resolves to `g_call_args` in `.bss`, which is stack residue, not a return address. **Do not read that frame as a location.**

**THIS IS s184's CLASS REACHING BEAUTY, BY A SECOND ROAD.** s184 (this seat, row `pat-eval-double-fn-arbno`) proved the same `alpha$<FN>`-holds-the-stub shape on `expr_eval` / `140` / `141` and named the cure site `bb_define_bind` (`bb_define.cpp:396`) for the STARTUP bake. What beauty adds is that the unsealed cell is minted **at run time, inside the emitted image, by `eval_thunks_emit_from`** — so a startup-bake-only seal will not necessarily cover it. `runtime_eval.c:251` already seals each fragment's OWN entry (D-18a, s161); it does not seal the **main-image callees** the fragment calls.

**⛔ HONEST UNKNOWN — WHETHER m3's WILD JUMP SITS BEHIND m4's ERROR 22.** I could not answer this without a fix, and this row does not fix. The pre-measurement that would have answered it was attempted and is recorded because it names the real cost of the cure: the 13 cells are **not** allocated in one pass — the first `eval_thunks_emit_from` call yields only **2** (`alpha$Reduce`, `alpha$nTop`), and the rest accumulate over later calls. A one-shot poke after the first emission leaves `Error 22` verbatim. **The seal rung must cover EVERY fragment emission, not just the first** — a fact the seal row should inherit rather than re-derive.

---

## 5. ⛔ THREE INSTRUMENT DEFECTS IN `board_beauty_m1.sh` — ROUTED, NOT FIXED HERE

1. **`--bisect` IS m3-ONLY AND STRUCTURALLY CANNOT ANSWER THIS ROW'S OWN QUESTION.** The loop is hardcoded `v="$(rung "$mid" m3)"` and gated on `[ -n "$first_red_m3" ]`. The brief instructs "--bisect if the m3 and m4 first-red lines differ" — had they differed, `--bisect` would have bisected m3 again. Hand-bisected via `--rungs` this session.
2. **THE m4 LANE RECOMPILES BEAUTY ON EVERY RUNG THOUGH THE COMPILE IS RUNG-INVARIANT.** `rung()` varies only **stdin** (`head -n "$n" $SRC > in.$n`); the compile is always `--compile … "$SRC"` on the whole `beauty.sno`. Ten identical compiles per default board.
3. **NO WITNESS MODE.** The 8-witness m3-vs-m4 table that IS this row's deliverable had to be built outside the board.

⛔ **AND THE BRIEF'S OWN COST ESTIMATE IS FALSIFIED — "expect it to be SLOW … use `--rungs` to thin it first" IS WRONG BY AN ORDER OF MAGNITUDE.** Measured: `--compile` **1.9 s**, `gcc -no-pie` assemble+link **0.4 s**, and the **full 10-rung board in BOTH modes = 60 s wall-clock**. No thinning is needed, and a seat that thins on the brief's advice reads a coarser ladder than it could have had for free. **A cost estimate carried in a brief and never measured is a false constraint on the seat that inherits it.**

---

## 6. WHAT THIS ROW CHANGES FOR M1

- **DOD item 2 (byte-identical fixed point in m3 AND m4) is now MEASURED on both lanes for the first time.** m4 = **0/2** exactly as m3 = **0/2**; both stop at input line 8; both emit the same 259 bytes on self-host.
- **`m1-composed-wild-jump` (CLASS A) stays an m3-lane row for now** — it cannot be worked from m4 until m4's earlier wall falls.
- **`m1-class-b-stmt-parse-error` (CLASS B) is mode-independent** and should be worked in whichever mode is cheaper to debug; m4's `.s` is human-readable, which makes m4 the *better* lane for it under ASM-DIFF-FIRST.
- **One NEW row:** `m4-eval-fragment-seal` — seal the main-image callees' `alpha$<FN>` cells for cells minted by `eval_thunks_emit_from`, covering every fragment emission. Codegen/runtime change ⇒ RULES step-4 regen mandatory + a killswitch with a proven byte-identical `=0` arm.
- **One NEW row:** `m1-board-instrument` — the three defects in §5.

**FILES TOUCHED BY THIS ROW: none in SCRIP, none in corpus.** No codegen was touched, so RULES step-4 `.s` regen carries no debt here.
