# FINDING — s22k (2026-07-31, Claude)

## THE NOFC GAP IS A GRAPH-LEVEL JMP-ENTRY DECLINE, NOT AN ARG-MARSHALLING CONVERSION

**SCRIP `b3263e4f` (K collapse) · `05575235` (ZD-9) · feature `.s` artifacts regenerated.**

---

## 0. WATERMARK — RE-PROVEN AT BOTH ENDS, AND THE CURSOR WAS STALE

Measured at HEAD on entry, **before any edit**:

| | m3 | m4 | DIVERGE |
|---|---|---|---|
| **s22j LIVE CURSOR claimed** | 241 / 76 | 240 / 76 | 2 |
| **MEASURED at HEAD (s22k entry)** | **276 / 41** | **275 / 41 / 1** | **2** |

Total 317 both ways — same corpus, so this is a real +35, not a corpus change. The
`s22j FIX 2` (`bc4a3467`) and `ALT-NARY REJOIN` (`233b9f69`) commits landed AFTER the
cursor text was frozen. This is precisely the staleness class RULES.md's own FACT RULE
(a) describes: **prose asserting a number it cannot know.** The cursor is now updated.

⭐ **BENCHMARKS WERE ALSO STALE — AND MORE FAVOURABLY.** The cursor's NEXT RUNG banner
reads `OK=17 FAIL=0 CRASH=4` with `pattern_bt`, `pattern_bt_deep`, `roman`,
`eval_dynamic` crashing, and directs the next session at "the pattern-blob RBP regime"
with a `[rbp+64]`-past-a-48-byte-frame diagnosis. **MEASURED: 20 of 21 benchmarks match
the SPITBOL oracle in mode-3.** `pattern_bt`, `pattern_bt_deep` and `roman` are FIXED —
the ALT-NARY REJOIN commit fixed them, exactly as its own message predicted. A session
following that banner would have spent its budget re-diagnosing three already-fixed
programs.

⚠ **`eval_dynamic` IS NOT A CRASH. IT IS A TIMEOUT.** Measured scaling (n = 1000 → 8000
EVAL calls): SCRIP is **linear** at ~0.091 ms/call; SPITBOL is ~0.0006 ms/call. The
benchmark does 1,000,000 EVALs, so SCRIP needs ~91 s against a 30 s runner timeout.
**The gap is ~150× on EVAL throughput, not a correctness defect** — semantics are right
(a 3-iteration reduction matches the oracle exactly). Filing it as CRASH sent the
roadmap after a stack bug that does not exist.

---

## 1. RUNG ONE — THE TWO `K` AUTHORITIES ARE COLLAPSED (SCRIP `b3263e4f`)

s22j's own top finding was that `K` (the per-node zeta claim width) was spelled twice —
`zd_plan`'s depth model and the drive-loop staging site that feeds `op_fc_bytes` and
emits the α carve — and that editing one alone is a silent 16-byte stack skew on every
node of the admitted kind. Both now call one `zd_k()`.

**NEUTRALITY PROVEN, NOT ASSERTED.** Stash → rebuild → re-run → restore gave a
byte-identical crosscheck on both sides (276/41, 275/41/1, DIVERGE 2). This matters
because the change is *textually* an obvious identity substitution, and "obviously
identical" is exactly the reasoning that produced the two-authority bug in the first
place.

---

## 2. ⭐⭐⭐ THE MAIN FINDING — TWO CURSOR CLAIMS ARE WRONG

### 2a. The NOFC break set is 22, and it is ONE root cause, not two families

`SCRIP_NOFC=1` A/B set-diff (the cursor's own INSTRUMENT LAW — rank by break set, never
by decline count): **22 break, 0 fix.**

```
DEFINE (15) 083 084 085 086 088 090 097 100_roman 1012_func_locals
            161_pat_defer_fn_nested_match 204_gc_recursive_frames
            212_gc_args_in_flight test_math test_stack test_string
EVAL/CODE(4) 1016_eval 1019_eval_string 1020_code_label_transfer 1021_code_direct_goto
GOTO     (3) 214_indirect_goto 215_indirect_goto_cond 216_indirect_goto_computed
```

The cursor treats DEFINE ("Family A") and the jmp-entry EVAL/CODE class as SEPARATE,
and sizes Family A as a five-arm `bcps_arg_slot → FRQ(slot)` **arg-marshalling**
conversion (s22g measured that at −63).

⛔ **MEASURED, AND IT IS NOT THE ARG SIDE.** `SCRIP_LP_DIAG=1` on a 4-line DEFINE
reproducer:

```
[LP] prefix=proc_LBL__F n=4  armed=0 all_zd=0 jmp=1
[LP] prefix=proc_F      n=2  armed=0 all_zd=0 jmp=1
[LP] prefix=main        n=15 armed=3 all_zd=0 jmp=0
```

**`jmp=1 armed=0`: DEFINE'd proc bodies are `flat_jmp_entry` graphs, and `zd_plan`
declined every such graph WHOLESALE.** Every statement in every user proc was off the
zeta spine — not because arguments marshal through a flat slot, but because the graph
never reached the planner. **The arg side is DOWNSTREAM of a graph-level decline.**
Sizing this as a five-arm marshalling rung would have repeated the −63.

### 2b. The `SCRIP_NOFC` killswitch is ASYMMETRIC, so the gate figure is partly an instrument artifact

Minimised to `F = "lit"` inside a DEFINE and diffed the emitted code, default vs NOFC:

```
n1_lit_string_α:  sub rsp,16 ; mov [rsp+0],... ; mov [rsp+8],rax     <- producer, BOTH modes
n2_assign_α:      default:  mov rax,[rsp+0] ; mov rdx,[rsp+8] ; add rsp,16
                  NOFC:     mov rax,[rsp+128] ; mov rdx,[rsp+136]
```

The producer carves its cell and writes the spine **in both modes**. `nofc()` flips only
the CONSUMER's read (`vfc()` in `bb_assign_global.cpp`, `vfcc()` in
`bb_binop_concat_slot.cpp`), never withdrawing the producer's grant. So under NOFC the
declined statement reads a flat slot **nobody wrote** — null result, plus 16 B leaked per
statement. In default mode the FC arm was silently papering over a producer/consumer
mismatch by coincidentally reading the same address *and* performing the release.

⚠ **Consequence: the "NOFC gate = N programs" figure measures FC dependence AND the
killswitch's own asymmetry, mixed.** Do not treat it as a pure count of genuine FC
customers until the killswitch is symmetric.

⛔ **ONE ARM TESTED AND FALSIFIED — DO NOT RETRY AS SPELLED.** Gating
`fc_vread_register` / `fc_vbinop_register` on the killswitch (the obvious symmetric fix)
changed **nothing** — codegen byte-identical, all four reproducers unmoved. Those two
registries are not this producer's grant source. Reverted, not committed. The grant for
the DEFINE case comes through the graph-level path, which is §2a.

---

## 3. ZD-9 — GATE ONE IS CLEARED (SCRIP `05575235`)

`zd_plan`'s decline was a blanket `g_emit.flat_jmp_entry`. Refined to admit the
DEFINE-stub population only.

⭐ **THE PREDICATE IS NOT NEW — IT IS ALREADY LIVE AND MEASURED.** The DEFINE-STUB
DISCRIMINATOR at the `emit_chain` choke (`emit.cpp` `_stfj`) separates exactly these two
populations, and its comment records the prior falsification: *"admitting ALL jmp-entry
citizens regressed expr_eval/161/1016/1019"*. `zd_stub_ok()` reuses it minus its two
non-default env gates (`SCRIP_STMT_FRAME`, `SCRIP_CALL2BB`). `g_flat_frame_floor > 0` is
the DRIVER's own stub verdict — all four proc-emission loops in `scrip.c` set it from the
role-3-entry predicate exactly and only around DEFINE-stub emissions; PAT$ patprocs,
EVAL/CODE chains and rt pattern builds all leave it 0.

**MEASURED, default mode:**

| | m3 | m4 | DIVERGE |
|---|---|---|---|
| before | 276 / 41 | 275 / 41 / 1 | 2 |
| **after ZD-9** | **276 / 41** | **276 / 40 / 1** | 3 |

- **FIXED:** `151_pat_arbno_inline_fence_backtrack` (m4)
- **BROKEN:** nothing
- **DIVERGE 2→3 is MECHANICAL** — 151 now passes m4 while still failing m3. Not a new
  disagreement class.

Killswitch `SCRIP_ZD_STUB=0`; diagnostic `SCRIP_ZD_STUB_DIAG=1`.

⚠ **HONEST LIMIT — ZD-9 DOES NOT MOVE THE NOFC GATE. Still 22.** Correlated diag shows
why: gate 1 now passes, and the run declines one layer down.

```
[STUB] pat=0 gen=0 deep=0 genproc=0 resum=0 floor=272     <- admitted
[ZD] run h=0 len=2 DECLINED at i=0 (IR_SAVE_RESTORE op=14) <- gate 2
```

**The DEFINE blocker is now exactly ONE KIND, not a five-arm conversion.**

---

## 4. ⭐ NEXT — ORDERED

1. ⭐⭐⭐ **ADMIT `IR_SAVE_RESTORE` TO `zd_wl_kind`** — the sole remaining DEFINE blocker
   now that ZD-9 clears the graph gate. ⛔ The in-tree note at `emit.cpp:1849` warns it
   *"carries a conditional `g_emit`-mutating preamble that is the CALL2BB arg-window
   linkage (:989)"* — that preamble is the thing to read first. Expect the arg-window
   linkage, not the marshalling arms, to be the real work. This is the rung that moves
   the 15-program DEFINE half of the NOFC set.
2. ⭐⭐ **MAKE THE `SCRIP_NOFC` KILLSWITCH SYMMETRIC** so the gate figure means what it
   says. §2b names one falsified arm; the live grant path is graph-level. Until this
   lands, every NOFC count in this file and the cursor is an upper bound mixed with an
   instrument artifact.
3. ⭐⭐ **ZD-5 / `IR_MATCH_HEAD` (247 declines)** — unchanged, still the largest family
   and the 41-red `pat_*` mass. ⛔ In-tree note: admitting it ALONE segfaults.
4. **EVAL THROUGHPUT (~150× vs SPITBOL)** — new, and it is what actually gates
   `eval_dynamic`. A correctness rung will not fix it; it needs the EVAL compile path
   profiled. Not a stack bug.
5. Unchanged: `claws5`/`json` assembler-rejected codegen · the 130/131 clean-HEAD segv ·
   CARVE-ERAD per THE MODEL's three-step order.

---

## 5. METHOD NOTE — WHAT ACTUALLY FOUND THIS

Not a census. The decline census ranked `IR_MATCH_HEAD` 247 / `IR_CALL` 58 /
`IR_SAVE_RESTORE` 25 and would have sent this session at MATCH_HEAD. What found the
DEFINE root cause was **minimising to four lines, diffing the two emitted `.s` files, and
then reading `SCRIP_LP_DIAG` + `SCRIP_ZD_DIAG` together** — three instruments already in
the tree. s22j's INSTRUMENT LAW ("a decline census ranks opcodes, not blockers") holds and
should be extended: **when a family looks like a marshalling problem, check whether its
graphs reach the planner at all before sizing the conversion.**
