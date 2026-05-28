# GOAL-PROLOG-BB.md — Prolog: BB-land DCG per predicate + lower_pl DCG

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md — mirror; only port semantics and names differ.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:** `Prolog AST → lower_pl (AG-wired BB_t graph) → bb_exec.c (Mode 2/3) → bb_pl_*.cpp → x86 (Mode 4)`

**Target model (read before CP work):** `one4all/doc/SWIPL-STUDY-2026-05-28-OPUS.md` —
SWIPL engine study. The CP-stack model (idea #4) is the current track (WAM-CP rungs).

**Three modes:**
- **Mode 2 (`--interp`):** `sm_interp_run` → `SM_BB_SWITCH` → `pl_bb_dcg` → `bb_exec_once`. Correctness reference.
- **Mode 3 (`--run`):** routes through `sm_interp_run` for Prolog (AGW-1c) until `bb_pl_*.cpp` templates land (AGW-9). DO NOT TOUCH.
- **Mode 4 (`--compile --target=x86`):** emitter port-DFS walks BB graph, emits via `bb_pl_*.cpp`. Graph freed by `stage2_free_bb_after_emit` after emit.

**Absolute rules:** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports = Greek letters (α/β/γ/ω) only. No `rt_*` port-logic helpers (conversion/effect helpers like `trail_mark`/`unify`/`term_new_*` are OK).

**Port semantics:**
| Port | Direction | Prolog meaning |
|---|---|---|
| γ | inherited DOWN | success continuation |
| ω | inherited DOWN | failure continuation (pop choice + unwind trail) |
| α | synthesized UP | this node's fresh-solve entry |
| β | synthesized UP | this node's redo/retry entry |

---

---

## ⏳ WAM-CP — SWIPL-informed choice-point track (2026-05-28, Opus 4.7) ← CURRENT

**Lon-directed PIVOT.** After studying SWI-Prolog's engine (`pl-data.h`, `pl-vmi.c`,
`pl-wam.c`, `pl-incl.h`, `pl-index.c`) we have a target model. Full findings:
`one4all/doc/SWIPL-STUDY-2026-05-28-OPUS.md`. The headline: our stashed CAT-A-3 r12
resume-buffer is a *single choice-point record without the parent link* — the right
instinct, wrong scope. SWIPL's `struct choice { type; parent; mark; frame; value }`
on a parent-linked stack with one `BFR` backtrack register is the genuine article; it
makes cut trivial (truncate to barrier), unifies `;`/multi-clause/retry under one
primitive, and is the prerequisite for Last-Call Optimization (the principled fix for
the SEGFAULT-CLUSTER). **GNU Prolog study DONE** (`doc/GPROLOG-STUDY-2026-05-28-OPUS.md`,
2026-05-28): gprolog confirmed the exact CP frame layout (`wam_inst.h:90-104` — negative
offsets from register `B`: ALTB/CPB/EB/BB/HB/TRB/CSB/AB), the in-place-update retry
discipline (`retry_me_else` mutates ALTB, `trust_me` pops — the real model our `nd->state`
scan crudely emulates), one-assignment cut (`Pl_Cut: B = saved_B`), and the first-arg
indexing scheme (`switch_on_term` tag-dispatch over try/retry/trust chains — the WAM-CP-8
blueprint). It refined the WAM-CP-1 struct with `saved_args` (AB) + `stamp` (STAMP, for LCO).
**WAM-CP-1 substrate LANDED & gate-clean. NEXT: WAM-CP-2 (route BB_CHOICE through the CP
stack, mode-2, byte-identical).**

**Strategy: build the choice-point stack on TOP of our existing `Term*` boxes first
(no tagged-word rewrite yet), so every rung is small and nothing breaks. The big
tagged-word/global-stack migration (SWIPL idea #1) is a SEPARATE later track; the CP
model is designed to survive it.** Each rung holds ALL gates green and is bisectable.

### Dependency order (from the study)
```
WAM-CP-1  choice-point record + g_pl_bfr register (mode-2 first, Term* boxes)   ← foundation
WAM-CP-2  route BB_CHOICE multi-clause through the CP stack (replaces nd->state scan)
WAM-CP-3  route ;  (BB_PL_ALT) through the same CP stack
WAM-CP-4  cut = truncate CP list to frame barrier (retire g_pl_cut_flag)
WAM-CP-5  mode-4 emit: CP record is the r12 target (promote stashed CAT-A-3 buffer)
WAM-CP-6  Last-Call Optimization (needs CP stack: "no CP since frame?" → reuse frame)
WAM-CP-7  unify specialization B_UNIFY_{FF,VF,FV,VV,FC,VC}  (independent speed; any time)
WAM-CP-8  JIT first-arg indexing (needs CP model to know when a CP was elided)
[LATER track] tagged-word terms + global stack (SWIPL #1/#3) — separate goal file when ready
```

### Rungs & steps

- [x] **WAM-CP-1 — choice-point record + `g_pl_bfr`, mode-2 only. ✅ COMPLETE** (Opus 4.7,
  2026-05-28). GNU Prolog study landed first (`doc/GPROLOG-STUDY-2026-05-28-OPUS.md`) — it
  validated the layout as gprolog's CP frame (`wam_inst.h:90-104`) reduced to the live
  Term*-box subset, and added two fields the original sketch omitted: `saved_args` (gprolog
  AB — arg-register restore for WAM-CP-2) and `stamp` (gprolog STAMP — monotonic age for the
  WAM-CP-6 LCO "is B older than this frame?" test, so LCO needs no later struct change).
  Final record in `pl_runtime.h`: `typedef struct pl_choice { pl_cp_type type; struct
  pl_choice *parent; int trail_mark; Term **env; void *resume; Term **saved_args; int cursor;
  int stamp; }` + `pl_cp_type {PL_CP_CLAUSE,PL_CP_DISJ,PL_CP_RETRY}`. Register `pl_choice
  *g_pl_bfr=NULL` + `int g_pl_cp_stamp`. Helpers in `pl_runtime.c`: `pl_cp_push` (=gprolog
  Create: parent=old bfr, bump stamp), `pl_cp_current` (=B/Pl_Get_Current_Choice), `pl_cp_pop`
  (=Delete: bfr=BB), `pl_cp_truncate` (=Pl_Cut: bfr=barrier, frees younger frames). Reuses
  `g_pl_trail`+`trail_unwind` as TR/Pl_Untrail (no parallel trail). NO callers — pure
  substrate. Step B throwaway test (push3/truncate-to-1/pop/cut-to-null + stamp/cursor) all
  PASS. **All gates byte-identical:** GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 mode-2
  91/107, GATE-4 4/4, full mode-4 28/128, FACT RULE 0; sibling smokes icon 5/5 snocone 5/5
  raku 5/5 rebus 4/4 snobol4 13/13. Symbols present in both `scrip` and `libscrip_rt.so`.

- [ ] **WAM-CP-2 — BB_CHOICE multi-clause via CP stack (mode-2).** Replace the
  `bb_active_choice` runtime scan (`bb_exec.c:849`, `nd->state>0`) with: on first entry
  push a `pl_choice` (cursor=0, trail_mark=mark); on redo, `Undo` to `trail_mark`,
  advance cursor, try next clause; on exhaustion pop the CP. Behavior-IDENTICAL to today
  (same solutions, same order) — this is a refactor to the real model, not new semantics.
  Gate: GATE-1 5/5, GATE-2 132/0, GATE-3 mode-2 91/107 UNCHANGED, sibling smokes hold.
  - Step A: mode-2 BB_CHOICE arm pushes/reads CP instead of nd->state. Diff mode-2
    outputs byte-identical vs HEAD across all 107 rungs.
  - Step B: delete the now-dead `bb_active_choice` scan + `nd->state` choice bookkeeping
    (keep nd->state for non-choice uses). Re-verify byte-identical.
  - Step C: commit. GATE-3 mode-2 unchanged.

- [ ] **WAM-CP-3 — `;` (BB_PL_ALT) via CP stack (mode-2).** Same treatment for
  disjunction: left branch pushes a CP whose resume = right branch. Retires the
  separate alt bookkeeping. Gate: mode-2 byte-identical, all gates hold.

- [ ] **WAM-CP-4 — cut = truncate CP to barrier (mode-2).** Record the frame's CP
  barrier on clause entry; `!` truncates `g_pl_bfr` to it. Retire `g_pl_cut_flag`.
  This is where the CP model PAYS OFF — cut becomes one pointer assignment. Gate:
  rung07 (cut) + all cut-using rungs byte-identical; GATE-3 mode-2 unchanged or up.

- [ ] **WAM-CP-5 — mode-4 emit: CP record is the r12 target.** Promote the stashed
  CAT-A-3 buffer (`git stash@{0}`) to emit/read a `pl_choice` record instead of the bare
  5-qword pool buffer. The cursor-dispatcher in `bb_pl_choice.cpp` already has the right
  shape; point it at `g_pl_bfr`. Det/nondet split in `bb_pl_call.cpp` stays; the
  resumable path pushes a CP instead of `rt_pl_resume_alloc`. **This fixes the γ-leak**
  (CP is on a stack the frame teardown truncates — no dangling r12). FACT RULE stays 0
  (all bytes template-emitted). Gate: GATE-4 4/4 incl m4-choice, full mode-4 ≥ 28 +
  rung02/05/06/08 (expected mid-30s–45), GATE-1/2/3 unchanged, FACT RULE 0.
  - Step A: rebuild stash on current HEAD; apply the rt.h `Term`→`void*` fix (the one
    pending build error from the pre-pivot session: `rt_pl_env_current` decl in rt.h).
  - Step B: swap pool-buffer for CP-record push/pop; m4-choice canary must pass.
  - Step C: rung02/05/06/08 via x86 backend → PASS. Full mode-4 loop.
  - Step D: GATE-1/2/3 + sibling smokes + FACT RULE grep. Commit.

- [ ] **WAM-CP-6 — Last-Call Optimization.** At the last goal of a clause body, if
  `g_pl_bfr` is older than the current frame (no CP created since entry) and the call is
  deterministic, reuse the frame instead of pushing. Mode-2 first, then mode-4. This is
  the principled fix for the SEGFAULT-CLUSTER (deep tail recursion). Gate: a tail-rec
  rung (e.g. `count(0). count(N):-N>0,N1 is N-1,count(N1).` to 1e6) runs in O(1) stack.

- [ ] **WAM-CP-7 — unify specialization (independent, any time).** Lower the common
  unify shapes (var-vs-const, first-occurrence-var, var-vs-var) into distinct BB nodes
  with tiny templates instead of routing all through generic `unify()`. Pure speed,
  fully independent of CP work. Gate: byte-identical solutions, faster.

- [ ] **WAM-CP-8 — JIT first-arg clause indexing.** Build a first-argument hash index
  on multi-clause predicates so `p(b)` against `p(a)./p(b)./p(c).` jumps to clause 2 with
  NO choice point. Needs the CP model to know when a CP was elided. Big determinism +
  speed lever. Gate: indexed predicates produce identical solutions; semidet calls leave
  no CP (assert g_pl_bfr unchanged across a deterministic indexed call).

### Decision recorded
Stashed CAT-A-3 B–C (`git stash@{0}`, r12 buffer) is NOT abandoned — it is absorbed by
WAM-CP-5, which reuses its emit machinery (cursor-dispatcher, det/nondet split, _redo
trampoline) but backs it with the real CP record. The buffer-in-isolation γ-leak and
cut gaps are resolved by the stack model rather than patched.

---

## ⏳ LOWER-PIVOT — lower_pl.c → one-function-per-node (Icon style) (2026-05-28, Opus 4.7) — COMPLETE, superseded by WAM-CP

**Lon-directed PIVOT.** Migrate `lower_pl.c` from the ~460-line `lower_pl_goal`
mega-switch to Icon's named per-node builders (`lower_icn.c`'s `lower_icn_new_*_ag`,
which transcribe JCON `irgen.icn`'s `ir()`→`ir_a_*` shape). Behavior-neutral; every
commit byte-identical graphs. **Motivation: `lower_pl_new_Call` becomes the clean home
for CAT-A-3 β-resume (redo) — fix backtracking in the node that owns it.**

### Done — 3 commits at full watermark
- `7119e41d` — `lower_pl_new_Alt` (`;`, twin of `lower_icn_new_Alt_ag`), `lower_pl_new_Ite`
  (if-then-else, twin of `lower_icn_new_If_ag`), `lower_pl_new_Unify` (`=`),
  `lower_pl_new_Compare` (`>,<,>=,<=,=:=,=\=`).
- `4e555954` — `lower_pl_new_Conj` (`,` → BB_PL_SEQ, twin of `lower_icn_new_Conjunction_ag`;
  back-to-front γ/ω threading + resumable-β table + `bb_pl_seq_state_t` publishing),
  `lower_pl_new_Call` (0-arity atom-goal + general N-ary unified → BB_PL_CALL, twin of
  `ir_a_Call`/`bb_pl_call.cpp`). Forward-decl'd `flatten_comma` for Conj.
- `427050d8` — `lower_pl_new_Builtin` + `pl_builtin_style` classifier. Collapsed the six
  scattered inline builtin arms (write/is/compare AB-style; 1-arg type-tests; functor/arg/=..
  + atom-/string-/term- chain family; sort/msort/format/numbervars/writeq/retract/abolish)
  into ONE named per-node builder with three wiring styles (PL_BI_AB, PL_BI_TYPETEST,
  PL_BI_CHAIN; abolish via PL_BI_CHAIN_ABOLISH for its β=ω quirk). phrase/2,3 + findall/3
  kept as own builders per directive. Behavior-neutral: all 128 emitted .s byte-identical
  modulo bb-id counters + heap pointers in # BOX comments (normalized diff); all 128 mode-2
  outputs byte-identical. Net −27 lines. `lower_pl_goal` builtin dispatch now a single line.

Trivial leaves (cut, true/fail/nl atom-goals) stay inline (Icon does too).

### Gates (held across ALL THREE commits)
GATE-1 5/5 · GATE-2 132/0 (5 ORACLE_MISS) · GATE-3 mode-2 91/107 · GATE-4 4/4 ·
full mode-4 28/128 · FACT RULE 0 · sibling smokes icon 5/5 / snocone 5/5 / raku 5/5 /
rebus 4/4 / snobol4 13/13.

### NEXT — LOWER-PIVOT COMPLETE. Back to CAT-A-3 Steps B–D.
The pivot is done: every control/relational/structural/builtin construct is now a named
one-function-per-node builder (`lower_pl_new_Alt/Ite/Unify/Compare/Conj/Call/Builtin`),
matching Icon's `lower_icn_new_*` shape. `lower_pl_new_Call` is the clean home for the
CAT-A-3 β-resume (redo) work. Resume **CAT-A-3 Steps B–D** (mode-4 backtracking, +15–25
corpus). Design: `HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md` (always-r12
resume-buffer; JCON study confirmed cursor-in-caller-allocated-state). Step A substrate
already in `58142007`. Optionally interleave with PL-LOWER-REVAMP staged 0-4 (β-precision)
— Lon to sequence; recommend CAT-A-3 B-D first.

---

## ✅ rung25-TERM-STRING — term_string/2 REGISTERED AS BB_BUILTIN (2026-05-27, Opus 4.7)

**Closed.** `term_string/2` is now a recognized builtin in mode-2 (and mode-3 transparently via
the V-5 routing through `sm_interp_run`). Previously the predicate wasn't recognized at all —
corpus rungs fell through silently with exit 0 and empty output. GATE-3 mode-2 90/107 → **91/107**
(+1: `rung25_term_string_term_string`). one4all `66d283ad`.

**The gap:** rung25 has three fixtures —
- `rung25_term_string_term_to_atom.pl` (uses `term_to_atom/2`)
- `rung25_term_string_term_to_atom_arith.pl` (uses `term_to_atom/2` with `+`/`-` operator notation)
- `rung25_term_string_term_string.pl` (uses `term_string/2`)

The previous session's rung25-TERM2ATOM-OPS landed `pl_write_to_file`'s operator-notation block,
closing the first two. The third still failed because `term_string` had no recognizer in
`lower_pl.c` and no arm in `bb_exec.c`. The mode-2 lift was the cheap one — same shape as
`term_to_atom`, same output text (since SCRIP models strings as atoms throughout the runtime;
there is no separate `TERM_STRING` tag), same `pl_term_to_string` plumbing.

**What landed (mirror of `term_to_atom`; minimal +17/-1):**

### `lower_pl.c` — recognizer (line 366)
```c
|| (strcmp(fn,"term_to_atom")==0 && e->n==2)  || (strcmp(fn,"term_string")==0 && e->n==2)
|| (strcmp(fn,"atom_number")==0 && e->n==2)
```

### `bb_exec.c` — outer string-builtin dispatcher fn-match (line 3367)
One-line append to the if-condition so the term_string call reaches the inner per-builtin chain.

### `bb_exec.c` — term_string arm (12 lines, inserted directly after the term_to_atom arm)
```c
/* term_string/2: forward-only mirror of term_to_atom. SCRIP strings == atoms (text).        */
/* Same pl_term_to_string path: operator-notation writer landed in rung25-TERM2ATOM-OPS.    */
if (strcmp(fn,"term_string")==0) {
    if (d0 && d0->tag!=TERM_VAR) {
        extern char *pl_term_to_string(Term *);
        char *s = pl_term_to_string(d0);
        if (!s) { nd->value=FAILDESCR; return nd->ω; }
        Term *at = term_new_atom(prolog_atom_intern(s)); free(s);
        if (!unify(t1, at, &g_pl_trail)) { trail_unwind(&g_pl_trail,mark); nd->value=FAILDESCR; return nd->ω; }
    } else {
        nd->value=FAILDESCR; return nd->ω;
    }
    nd->value=INTVAL(1); return nd->γ;
}
```

Reverse direction (string → term parse) deliberately unsupported; fails cleanly, identical
to `term_to_atom`'s reverse stub. Needs a Prolog-term parser when wanted.

**Output (byte-identical to .expected):**
```
$ ./scrip --interp .../rung25_term_string_term_string.pl
point(3,4)
42
```

**Gate impact:**

| Gate | Before | After |
|---|---|---|
| GATE-1 (smoke) | 5/5 | 5/5 |
| GATE-2 (3-mode crosscheck) | 132/0 | 132/0 |
| **GATE-3 mode-2** | **90/107** | **91/107** (+1) |
| GATE-3 mode-3 (`--run`) | 89/107 | **90/107** (+1) |
| GATE-4 (mode-4 minimal) | 4/4 | 4/4 |
| Full mode-4 corpus | 28/107 | 28/107 |
| FACT RULE grep | 0 | 0 |
| Sibling smokes | all hold | all hold (icon 5/5, snocone 5/5, raku 5/5, rebus 4/4) |

**Why this fix is the right shape:**
- The exec helper `pl_term_to_string` already exists and already produces operator notation
  (the rung25-TERM2ATOM-OPS work from the same day).
- `term_to_atom` is the structural twin — same dispatcher block, same bidirectional shape, same
  forward-only fallback. Mirroring it is mechanical and matches the goal-file's NEXT directive:
  *"Same shape as term_to_atom — just calls pl_term_to_string and unifies."*
- Touched no emitter code, so FACT RULE compliance is mechanically preserved.
- Mode-4 emit gap remains (same as `term_to_atom` forward — both fall through to `_`); this is
  a paired CAT-D-* future item that should land both at once.

**Files touched:** `src/lower/lower_pl.c` (+1, -1 line) · `src/lower/bb_exec.c` (+16 lines).
Net diff `+17 / -1`.

**Next steps (unchanged from prior session, less term_string):**
- **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume) — still Lon-directive blocked.
- **PJ-AGW-5** (cut-barrier ω-rewiring) — separate semantic work.
- **rung18 plus/3** (bidirectional arith) — goal file claims `bb_exec.c` has mode-2 arm but
  3 rungs still OPEN; investigate gap.
- **term_to_atom + term_string mode-4 emit** (paired CAT-D-* candidate; both fall through to `_`).

---

## ✅ CAT-RUNG07-1 — BB_CUT WIRED INTO walk_bb_flat (FACT-RULE-ADJACENT FIX) (2026-05-27, Opus 4.7)

**Closed.** rung07_cut_cut no longer aborts during `--target=x86` emit with the diagnostic
`bb_emit_byte: non-BINARY-mode reach (mode=0, b=0xe9) — convert caller to a named bb_insn_*
helper`. The cut now routes through `bb_pl_cut.cpp` (already FILLED from AGW-9B-1 era) instead
of falling through `walk_bb_flat`'s `default:` arm.

**Bug:** `emit_bb.c walk_bb_flat` had no `case BB_CUT`. The default arm at line 775-779 calls
`emit_jmp_label(lbl_ω, JMP_JMP)` twice — `emit_jmp_label` is a BINARY-mode helper that
ultimately calls `bb_emit_byte(0xe9)` (the raw `JMP rel32` opcode). When `--target=x86` emits
text-mode `.s`, `bb_emit_mode != EMIT_BINARY_WIRED`, so the guard at `emit_core.c:109` aborts.

This bug was previously masked by CAT-C's pre-existing `BB_PL_VAR` garbage-sval segfault in
multi-clause recursive predicates — the rung07 emit crashed earlier in the pipeline before
ever reaching the cut. CAT-C's one-char fix at `lower_pl.c:65` unblocked emission, surfacing
the cut wiring gap. The ledger flagged it as "not a regression, flag for separate investigation."

**gdb trace** (rung07_cut_cut emit; breakpoint on `bb_emit_byte` when `bb_emit_mode != 1`):
```
#0 bb_emit_byte (b=233 '\351')                  emit_core.c:109
#1 ef_b1                                         emit_core.c:147
#2 emit_jmp_label (kind=JMP_JMP)                 emit_core.c:185
#3 walk_bb_flat (default arm)                    emit_bb.c:777
#4 flat_drive_pl_seq                             emit_bb.c:422
#5 walk_bb_flat                                  emit_bb.c:742
#6 flat_drive_pl_choice                          emit_bb.c:468
#7 walk_bb_flat                                  emit_bb.c:751
#8 pl_emit_callee_block_body (differ/2)          emit_bb.c:571
#9 sm_bb_switch                                  SM_templates/sm_bb_switch.cpp:42
```

The `!` (cut) inside `differ(X,X) :- !, fail.` lowers to `BB_CUT` (verified at
`lower_pl.c:306,313`); the dispatcher at `emit_core.c:542` already has the `BB_CUT → bb_pl_cut`
routing for the `walk_bb_node` path. The gap was only in `walk_bb_flat`'s switch.

**Fix:** one-line addition to `emit_bb.c walk_bb_flat`:
```c
case BB_CUT:        FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
```
plus a 7-line block comment documenting the trace + scope. `FILL` calls `walk_bb_node` →
`codegen_bb_dispatch` → `bb_pl_cut(nd)`. The template's TEXT arm emits:
```asm
α: # BOX PL_CUT
   call rt_pl_cut_set@PLT
   jmp γ
β: jmp γ
```

**Gate impact:**

| Gate | Before | After |
|---|---|---|
| GATE-1 (smoke) | 5/5 | 5/5 |
| GATE-2 (3-mode crosscheck) | 132/0 | 132/0 |
| GATE-3 mode-2 | 89/107 | 89/107 |
| GATE-3 mode-3 | 89/107 | 89/107 |
| GATE-4 (mode-4 minimal) | 4/4 | 4/4 |
| **Full mode-4 corpus** | 28/107 | 28/107 |
| **`bb_emit_byte` aborts in full corpus** | 1 (rung07_cut_cut) | **0** |
| FACT RULE grep | 0 | 0 |
| Sibling smokes | all hold | all hold |

**Scope honest accounting (0 PASS lift):** rung07_cut_cut still FAILs with wrong output
(`yes\nyes` instead of `yes\nno`) — the cut emits cleanly but doesn't actually block
backtracking through the `differ(X,X) :- !, fail. differ(_,_).` choice point. This is the
**PJ-AGW-5-CUT-BARRIER** ledger item — the full BB_CUT ω-rewiring for non-deterministic
conditions. CAT-RUNG07-1 fixes the FACT-RULE-adjacent emit-time abort; the semantic correctness
work continues under PJ-AGW-5.

**Why this fix is the right shape:**
- The template (`bb_pl_cut.cpp`) already exists and is correct for the deterministic case
  (its ledger predates this session; AGW-9B-1 era).
- The dispatcher (`emit_core.c codegen_bb_dispatch`) already routes BB_CUT to `bb_pl_cut`.
- The only gap was `walk_bb_flat`'s switch, which is precisely the byte-free recursion driver
  the FACT RULE blesses for owning labels but NOT bytes. Falling through to `default:` would
  emit bytes from the driver — itself a FACT-RULE-adjacent violation that the `bb_emit_byte`
  guard catches.

**Files touched:** `src/emitter/emit_bb.c` only — one substantive line (`case BB_CUT` arm),
seven-line block comment documenting trace + scope. Net diff `+8 / 0`.

**Next steps (unchanged from prior session):**
- **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume) — still blocked on Lon directive. Biggest
  single-step unlock (estimated +15-25 PASS).
- **PJ-AGW-5** (cut-barrier ω-rewiring for non-deterministic conditions) — separate semantic
  work to make rung07 actually produce `yes\nno` not `yes\nyes`. The emit machinery is now
  ready; the semantics still need the cut to retroactively prune the choice frame above it.

---

## ✅ CAT-D-11 — SORT/2 + MSORT/2 MODE-4 TEMPLATE (2026-05-27, Opus 4.7)

**Closed.** `sort/2` and `msort/2` now emit real four-port x86 in mode-4 (previously fell through
the `bb_pl_builtin` "unknown 'sort'" stub-comment + `jmp γ` arm, silently succeeding with the
result variable unbound → `_` output). All five `rung17_sort_*` corpus tests pass mode-4
byte-identical to `--interp` and to the `.expected` oracle.

**Pattern:** verbatim mirror of CAT-D-6 (`atom_chars/atom_codes`) two-path approach. Two effect
helpers in `bb_exec.c`:
- `rt_pl_sort_msort(int do_msort, int k0,i0,s0, int k1,i1,s1)` — 7 serializable scalars, 1 stack
  slot. Path A: scalar a0 (BB_PL_VAR bound to a list — future-proofing; corpus doesn't exercise
  this today since rung17 fixtures all pass list literals).
- `rt_pl_sort_msort_term(int do_msort, void *t0, int k1,i1,s1)` — 1 ptr + 3 scalars, all in regs.
  Path B: literal cons-cell a0 (BB_PL_STRUCT) built via `emit_build_compound_term` post-order
  walker, Term* arrives in rax post-build and moved to rsi.
- Shared static `sort_msort_common(int do_msort, Term *t0, Term *t1)` — direct port of
  `bb_exec.c` BB_BUILTIN sort/msort arm at lines 3505-3539. Walks cons list to collect elements
  (cap 4096); insertion-sort by `pl_term_compare` (stable for msort); dedup pass for sort
  (skipped for msort); builds reverse cons-list; unifies into t1 under trail mark.

`do_msort` flag (rdi) selects sort (0) vs msort (1); fn-name match in template picks the value.
No port logic in helpers — template owns the `test eax,eax / je ω / jmp γ / β:jmp ω` decision
triplet exactly like CAT-D-6 / CAT-D-10.

**Files touched:**
- `src/lower/bb_exec.c` — +56 lines: CAT-D-11 helper block (static `sort_msort_common` + two
  linkage entries) inserted between CAT-D-10 (`type_test_common`) and CAT-D-9 (`rt_pl_term_cmp`).
- `src/lower/bb_exec.h` — +5 lines: declarations for `rt_pl_sort_msort` and `rt_pl_sort_msort_term`.
- `src/emitter/BB_templates/bb_builtin.cpp` — +50 lines: CAT-D-11 dispatcher arm inserted between
  CAT-D-10 type-test arm and CAT-D-9b compound-term-cmp arm. Path B (BB_PL_STRUCT a0) checked
  first; falls through to Path A (scalar) otherwise. Both paths use `sub rsp,16` for SysV 16B
  alignment at call (Path A needs the slot for `s1`; Path B needs alignment for
  `emit_build_compound_term`'s internal `sub rsp,frame` recursion).

**Gate impact:**

| Gate | Before | After |
|---|---|---|
| GATE-1 (smoke) | 5/5 | 5/5 |
| GATE-2 (3-mode crosscheck) | 132/0 | 132/0 |
| GATE-3 mode-2 | 89/107 | 89/107 |
| GATE-3 mode-3 | 89/107 | 89/107 |
| GATE-4 (mode-4 minimal) | 4/4 | 4/4 |
| **Full mode-4 corpus** | 24/107 | **28/107** (+4) |
| FACT RULE grep | 0 | 0 |
| Sibling smokes | icon 5/5, raku 5/5, snobol4 13/13, snocone 5/5, rebus 4/4, prolog 5/5 | all hold |

**New mode-4 PASSes (+4):**
- `rung17_sort_sort_basic` — `sort([c,a,b,a], S), S = [A,B,C]` → `a\nb\nc`
- `rung17_sort_sort_already_sorted` — `sort([apple,banana,cherry], S)` → `apple\nbanana\ncherry`
- `rung17_sort_msort_basic` — `msort([c,a,b,a], S), S = [A,B,C,D]` → `a\na\nb\nc` (dupes preserved)
- `rung17_sort_msort_dupes` — `msort([b,b,a,a,c], S)` → `a\na\nb\nb\nc`

(`rung17_sort_sort_empty` was already passing — no list-pattern step downstream.)

**Verification:**
- `rt_pl_sort_msort_term@PLT` confirmed in emitted `.s` for all four newly-passing rungs (no
  stub-comment, no `unknown 'sort'` fallthrough).
- Downstream list-pattern unify in mode-4 (`S = [A,B,C]` after sort returns the bound list)
  works correctly — pre-validated with a `[a,b,c] = [X,Y,Z]` probe before committing the
  template arm to confirm the ledger's "verify list-pattern unify works downstream" concern
  was a no-op for the current tree.
- Mode-2 (`--interp`) unchanged for all five rung17 cases: identical byte-output before/after
  CAT-D-11.

**Next steps:**
- **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume) — still blocked on Lon directive on design
  (inline-on-demand vs resumable-call protocol). Largest single-step unlock (estimated +15-25
  PASS) — every `pred(X), …, fail` pattern, rung02/05/06 lists.
- **Pre-existing rung07_cut_cut** `bb_emit_byte: non-BINARY-mode reach (mode=0, b=0xe9)` —
  surfaced by CAT-C as a FACT-RULE-adjacent issue (raw `bb_emit_byte` callsite outside
  BINARY mode). Worth investigating as a clean side target.

---

## ✅ Closed milestones (terse, this dev cycle — full details in git log)

**CAT-D-12-S1** (`b95e4318`, Opus 4.7) — mode-3 (`--run`) routes through `sm_interp_run` (not the fork+exec
sham). scrip.c V-5 fake pipeline + `scrip_run_via_x86_pipeline` + `scrip_locate_rt_lib` deleted.
`bb_live=1` forces flat-wired BB. GATE-2 went 31/132 → 132/132 (real agreement).

**CAT-D-12-S2** (Opus 4.7) — mode-4 `functor/3`, `arg/3`, `=../2`. Eight new rt linkage symbols (scalar +
`_term` compound variants); three dispatcher blocks in `bb_builtin.cpp`. Pattern mirrors CAT-D-10. +1 corpus
(rung09_builtins).

**CAT-B** (`48ef0182`, Opus 4.7) — compound-term unify in BB_UNIFY mode-4. `f(X,a) = f(b,Y)` binds X=b, Y=a.
De-staticize `emit_build_compound_term` + new `build_operand_term` dispatcher in `bb_unify.cpp` routing
BB_PL_STRUCT operands through the walker; `push rax`/`pop rdi` swapped to 16-aligned scratch frame for
SysV. Zero new RT helpers. +1 corpus (rung03_unify).

**CAT-C** (`73dc587b`, Opus 4.7) — BB_PL_VAR garbage-sval SIGSEGV. `tree_t.v` is a union of sval/ival;
`tr_assign_slots` writes `v.ival = slot` LAST, destroying `v.sval`. `lower_pl.c:65` propagated the
resulting wild char* (e.g. `0x1` for slot 1) into BB_t (whose sval/ival are NOT a union); `bb_pl_call.cpp:50`
`strtab_label` SIGSEGV'd dereferencing it. One-char fix: `nd->sval = e->v.sval` → `nd->sval = NULL` for
`case TT_VAR`. +1 corpus (rung08_recursion). Surfaced the pre-existing rung07 `bb_emit_byte` issue closed
above as CAT-RUNG07-1.

**Earlier this cycle (one-liners):**
- **CAT-A** `af5c5ecd` — `*α_out = seq` (SEQ-in-ALT α-channel bug), +5 GATE-2.
- **CAT-A-2** `471ab202` — `flat_drive_pl_seq` resumability-aware ω-wiring; no numeric lift (gated on CAT-A-3).
- **CAT-D-1** `95f73bad` — atom_length/upcase_atom/downcase_atom, +2 GATE-2.
- **CAT-D-2..5** `bb8bb529` `ecb3b229` `52a78efb` — atom_concat / string_*  / atom_string / string_to_atom /
  copy_term mode-4 emit; aliased helpers, +6 rung.
- **CAT-D-6** `b60ebfa4` — atom_chars/atom_codes/string_chars/string_codes bidirectional; the two-path
  scalar/compound-literal template pattern that every subsequent CAT-D rung mirrors.
- **CAT-D-7** `d2ce06fc` — write(compound) recursive emit-time walker; rt_pl_write_var TERM_COMPOUND fix.
- **CAT-D-8** `710ee0b0` — BB_PL_ITE structural wrapper + flat_drive_pl_ite + bb_pl_ite.cpp.
- **CAT-D-9** `b1a37351` — 12 comparison ops (==, \\==, @<, @>, @=<, @>=, =:=, =\\=, <, >, <=, >=); was
  always-succeeds stub. +4 honest, -1 spurious. rt_pl_term_cmp + rt_pl_arith_cmp.
- **CAT-D-9b** `e15e86b0` — compound-term `==` correctness; emit_build_compound_term post-order walker;
  rt_pl_compound_build_n + rt_pl_term_cmp_terms. The reusable walker subsequent rungs lean on.
- **CAT-D-10** `c5fc7d3c`/`060aad55` — 11 1-arg type-tests (var/nonvar/atom/atomic/number/integer/float/
  compound/callable/is_list/ground); was silent always-succeeds. rt_pl_type_test + _term.

**Structural V-1..V-5 (RULES.md compliance, all CLOSED):**
- V-1: BB_PL_SEQ wrapper around clause body (lower_pl.c).
- V-2: `is/2` lowers to BB_ARITH (effect helper `rt_pl_is` for binary RHS).
- V-3: four structural templates filled (bb_pl_seq/call/choice/alt/cut all FILLED; EMPTY=0).
- V-4 `b95e4318`: mode-4 stopped rebuilding BB graph at runtime; `xa_pl_builder`+`rt_pl_b_*` family deleted
  (~390 LOC removed); each predicate flat-emits once under `.Lplpred_<name>_<arity>`.
- V-5: mode-3 (`--run`) collapsed to `sm_interp_run` (see CAT-D-12-S1 above).
- V-6 (open): confirm `pl_bb_dcg`/`bb_exec_*` only reachable from mode-2 dispatch. Audit grep, no code
  change expected.

---

## 🔴 Open work (priority order)

### CAT-A-3 — BB_PL_CALL + BB_CHOICE β-resume (DIRECTIVE: option (b); Step A landed)

Largest single-step unlock; estimated +15-25 mode-4 corpus PASS once landed. Every `pred(X), …, fail`
pattern (rung02 facts, rung05 backtrack, rung06 lists, etc.) gated on this.

**Lon chose option (b): resumable-call protocol** (not (a) inline-on-demand) — preserves single-emit.

**Step A DONE (`58142007`).** Runtime substrate, behavior-neutral: reused existing
`rt_pl_trail_mark()`/`rt_pl_trail_unwind(int)` (mark-by-value, per-call-site checkpoint, no LIFO
aliasing); added `pl_bb_env_install(Term**)` — non-freeing env install (counterpart to env_pop which
frees), needed because the resumable path keeps the callee env alive across redo. Not yet called by
any template. Full Steps B-D design in HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md.

**Steps B-D (NEXT, fresh context):** B = `bb_pl_choice.cpp` cursor-driven dispatcher (stack or r12
slots: cursor + trail_mark; clause-body ω rewired to dispatcher re-entry; cursor++ in pre advances).
C = `bb_pl_call.cpp` + PL_ENTRY arm: r12 resume-buffer ABI (state/cursor/trail_mark/callee_env) +
`.Lplpred_<name>_<arity>_redo` entry. D = verify rung02/05/06 + full corpus. Scope first cut to a
single rightmost BB_CHOICE per callee body (nested choices = follow-up). Recommend always-r12 (main
allocates a buffer too) to unify B and C. Two stub β sites remain until C: `bb_pl_call.cpp:97`,
`bb_pl_choice.cpp:58` (`β: jmp ω`).

### PJ-AGW-5 — Cut-barrier ω-rewiring for non-deterministic ITE conditions

Partial (`87ed9b24`): Prolog ITE β port routes to ω_in (lower_pl.c TT_IF) instead of re-entering Cond.
Stops the simplest re-evaluate-Cond loops (+3 net). **Still open:**
- rung07 cut_cut: `differ(X,X) :- !, fail. differ(_,_).` produces `yes\nyes` not `yes\nno`. The cut emits
  cleanly (CAT-RUNG07-1) but doesn't prune the choice frame above.
- rung15 one_of_two: ITE with abolished-pred Cond loops.
- Fix shape: dedicated stateful committed-ITE BB node (mirror Icon `BB_IF` at bb_exec.c:803) that runs
  Cond+chosen-branch in one node call and records the committed branch, rather than ALT-style port chaining.

### CAT-D — remaining mode-4 builtin coverage

- **CAT-D-11 ✅** (this session, see top-of-file).
- **plus/3 bidirectional** (rung18 — 3 remaining). If X+Y bound → unify Z; if X+Z bound → unify Y; etc.
  `bb_exec.c` has the mode-2 arm; template + 7-scalar effect helper needed.
- **term_to_atom/2 operator-notation writer ✅** (rung25 — done `b0093cd1`). pl_write_to_file now
  applies the same op-prec block as pl_writeq_term. Mode-2 only; mode-4 emit still TODO (term_to_atom
  not in the bb_builtin.cpp template; falls through to mode-4 `_` output).
- **term_string/2 ✅** (rung25 — done `66d283ad`). Registered as BB_BUILTIN forward-only mirror of
  term_to_atom; mode-2 +1. Mode-4 emit still TODO (same gap as term_to_atom).
- **catch/throw** (rung28 — 0/5). Lower as 3-arg BB_BUILTIN; exec arm uses setjmp/longjmp or global
  exception flag.
- **aggregate** (rung27 — 0/5). bagof/setof.
- **findall/3** mode-4 emit (currently mode-2 only). Effect helper + template arm.

### Other open

- **PL-RT-ASSERTZ** — runtime `assertz/asserta` inside a goal body (not just `:-` directive fold).
  Materialise fresh clause body BB graph at runtime and append to predicate's BB_CHOICE `zc->bodies[]`
  (inverse of abolish). Blocks rung15_then_reassert.
- **rung14** — `retract_all` loop, `retract_nonexistent` edge cases.
- **rung26_copy_term independent gap** — copy_term doesn't share var identity between A and B in mode-4
  (`copy_term(f(X,X), f(A,B))` → `A==B` should hold but doesn't); orthogonal to CAT-D-9b.
- **PJ-AGW-6b** — `BB_PAT_ARBNO`/DCG repetition port wiring (rung30 dcg_pushback_rest).
- **PJ-AGW-7** — LOWER sweep: no persistent aux in reset-cleared slots.
- **PJ-DEL-PUMP** (PP-1..10) — Tombstone `SM_BB_PUMP_PROC/SM/CASE` → `SM_UNUSED_7/8/9`.

### PL-LOWER-REVAMP — bring Prolog LOWER to Icon-LOWER (irgen.icn) fidelity

Investigation (Opus 4.7, 2026-05-28) vs the canonical four-port reference `tran/irgen.icn` (Jcon) and
our faithful Icon mirror `lower_icn.c`. irgen model: `ir_info(start,resume,failure,success)` = α/γ/ω/β;
`ir_init` mints all 4 labels per node; each `ir_a_*` proc wires its ports to children via `ir_chunk`
suspensions (logical labels → physical blocks). 43 `ir_a_*` procs, flat `case` dispatcher. `ir_a_Alt`
is the choice-point pattern (`MoveLabel`/`IndirectGoto` saved resume target). `lower_icn.c` hits this
bar: 9 `_ag` threaded fns (sig `cfg,e,γ_in,ω_in,&α_out,&β_out` = ir_info made physical) + 104
per-construct `_new_` dispatchers, 343 port refs. **`lower_pl.c` (624 lines, 219 port refs) gaps:**
(1) **monolithic** — all goal lowering in 2 mega-fns (`lower_pl_goal` ~340 lines, lines 166-508) vs
one-per-node; (2) **β by heuristic** — conjunction (lines 196-206) computes resume as "nearest
resumable predecessor" over a hardcoded {BB_PL_CALL,BB_CHOICE,BB_PL_ALT} set instead of irgen's
explicit per-node `resume` port — likely the root structural cause of the CAT-A-3 backtracking class
(rung02/05/06); (3) **no `bounded`/determinacy flag** (irgen threads one; we don't — cut/once handling
is ad-hoc). **Staged 0-4:** (0) add `bounded` int to the threaded sig + plumb everywhere, zero behavior
change — safe first commit; (1) split the monolith into per-construct fns (`lower_pl_conj/disj/ite/cut/
call/builtin`) mirroring lower_icn's `_new_`/`_ag` split; (2) replace the β-heuristic with explicit
per-node resume ports (deterministic node's β points to a fail-continuation, not a smeared neighbor;
conjunction then wires `goal[i].ω=goal[i-1].β` unconditionally per irgen); (3) make BB_CHOICE a
transliteration of `ir_a_Alt` (MoveLabel/IndirectGoto) — **unifies with CAT-A-3 Step C**: the r12
resume-buffer cursor is the run-time realization of irgen's saved-resume-label; (4) re-verify corpus
(same +15-25 unlock as CAT-A-3 — LOWER makes β edges precise, CAT-A-3 emitter lays them down; two
halves of one correctness story, they meet at the Alt model). Sequencing (before/after/interleaved
with CAT-A-3 B-D) — Lon to direct; recommend CAT-A-3 B-D first, then this. No code written yet.

---

## Rung state at HEAD (`58142007`, post-CAT-A-3-StepA)

| Gate | Count | Notes |
|---|---|---|
| GATE-1 (smoke) | 5/5 | unchanged |
| GATE-2 (3-mode crosscheck) | 132/0 | post V-5 real agreement |
| GATE-3 mode-2 (`--interp`) | **91/107** | +1 (rung25 term_string/2 registered) |
| GATE-3 mode-3 (`--run`) | **90/107** | +1 (transparent via sm_interp_run post-V-5) |
| GATE-4 (mode-4 minimal) | 4/4 | m4-seq/call/choice/alt all green |
| **Full mode-4 corpus** | **28/107** | unchanged (term_string mode-4 emit still TODO) |
| FACT RULE grep | 0 | full compliance |
| `bb_emit_byte` aborts in corpus | 0 | CAT-RUNG07-1 fix held |

**Mode-2 OPEN rungs (16/107):** rung15 (2 — one_of_two, then_reassert), rung18 (3 — plus/3), rung23 (1),
rung27 (5 — aggregate), rung28 (5 — catch/throw), rung30 (1 — dcg_pushback_rest).

---

## Session setup

```bash
cd /home/claude/one4all && bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_prolog.sh        # GATE-1
bash scripts/test_prolog_rung_suite.sh   # GATE-3
bash scripts/test_crosscheck_prolog.sh   # GATE-2
bash scripts/test_prolog_mode4_rung.sh   # GATE-4
```

Full mode-4 corpus: shell loop over `/home/claude/corpus/programs/prolog/rung*.pl` calling
`bash scripts/run_prolog_via_x86_backend.sh $f` and diffing against `.expected`.

---

## Architecture reference

### bb_exec.c ↔ x86 template translation

For each `case BB_FOO:` in `bb_exec.c`:
1. State in `BB_t` fields: `nd->state`, `nd->counter`, `nd->value`, `nd->ival` (persistent payload —
   survives `bb_reset`).
2. `entry==α → nd->state==0` (fresh); `entry==β → nd->state>0` (redo).
3. Return: store in `nd->value`, tail-call `nd->γ(nd)` or `nd->ω(nd)`.
4. No `rt_*` port helpers. Only effect helpers: `trail_mark`, `trail_unwind`, `unify`,
   `prolog_atom_intern`, `term_new_*`.

### Per-construct port wiring

| Construct | α | β | γ | ω |
|---|---|---|---|---|
| `BB_PL_SEQ` | first goal's α | last failing goal's β | `goal[i].γ = goal[i+1].α` | `goal[i].ω = goal[i-1].β` |
| `BB_CHOICE` | first alt's α | next clause α | each alt `.γ = γ_in` | `alt[i].ω = alt[i+1].α`; last `.ω = ω_in` |
| `BB_PL_CALL` | callee's α | callee's β | callee success → γ_in | callee exhausted → ω_in |
| `BB_UNIFY` | self | — | bind/match → γ_in | mismatch → ω_in |
| `BB_CUT` | self | — | γ_in | cut barrier → ω_in |
| leaf | self | — | γ_in | ω_in |

### Mode-4 emit pattern (CAT-D-1..11 verbatim)

1. **Effect helper** in `bb_exec.c`: serializable scalars only, calls `rt_pl_node_to_term` to materialize
   args, returns 1/0. NO port logic.
2. **Two-path template** in `bb_builtin.cpp` (or sibling):
   - Path A (scalar args): N-scalar SysV call (rdi/rsi/rdx/rcx/r8/r9, stack at `[rsp+0]` if >6 args).
   - Path B (compound-literal args, BB_PL_STRUCT): `emit_build_compound_term` post-order walker builds
     Term* in rax → moved to register; call `*_term` variant.
3. **Trail mark** on entry, **trail unwind** on fail.
4. Template owns `test eax, eax / je ω / jmp γ / β: jmp ω`.

### Pattern for new BB_BUILTIN

- Recognizer in `lower_pl.c` before the `findall` block.
- Exec arm in `bb_exec.c BB_BUILTIN` case before final `nd->value=FAILDESCR`.
- Args hang off `nd->α` γ-chain.
- Use `pl_node_to_term(nd->α)` to materialise args.

---

## Completed milestones (one-line summary)

**Infrastructure:** PJ-1..14 ✅ (BB substrate, lower_pl, SM_BB_SWITCH); PJ-AGW-1..6 ✅ (full AG lower_pl);
PA-1..3 ✅; PJ-DEL-ONCEPROC ✅; PJ-10a/b ✅ (BB_PL_* → BB_* rename); PJ-12 ✅ (SM/BB freed after emit).

**Builtins landed (mode-2 + mode-4):** write/writeln/nl, is/2, arith, all 12 comparison ops (CAT-D-9/9b),
functor/arg/=.. (CAT-D-12-S2), 11 type-tests (CAT-D-10), atom_length/upcase/downcase (CAT-D-1),
atom_concat/string_* (CAT-D-2/3), atom_string/string_to_atom (CAT-D-4), copy_term (CAT-D-5),
atom_chars/atom_codes/string_chars/string_codes (CAT-D-6), write(compound) (CAT-D-7), if-then-else
(CAT-D-8), **sort/msort (CAT-D-11)**, BB_CUT (CAT-RUNG07-1).

**Mode-2 only (mode-4 emit gap):** findall, atomic_list_concat, term_to_atom (forward),
**term_string (forward)**, atom_number, format, numbervars, writeq, write_canonical, print,
retract, retractall, abolish, assertz/asserta (directive fold).

**SNOBOL4 BB infrastructure landings (cross-cutting):** SBL-FN-RET/ARGS/EXEC-PATD/PAT-BLOB/IDX ✅;
SBL-PAT-PRIM ✅ (TAB still open); SBL-M4-ASM ✅ (mode-4 broad corpus 0→126); SBL-M4-OPDISPATCH ✅.
