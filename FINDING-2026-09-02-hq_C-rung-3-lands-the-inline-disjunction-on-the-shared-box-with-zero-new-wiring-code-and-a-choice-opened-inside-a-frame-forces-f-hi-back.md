# RUNG 3 — the inline disjunction is the shared box with ZERO new wiring code, and a choice opened INSIDE a frame forces `F.HI` back

**Seat** hq_C (HQ-COMPLETE) · **2026-09-02** · row `prolog-rung-3-inline-disjunction-as-the-choice-with-f-resd-in-the-enclosing-frame`
**Law** `RULES.md` § THE PROLOG REBUILD GATE · **Sovereign** `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E row 3, § B.5, § B.0, § A.1
**Started from origin** SCRIP `81b40ceb` (rung 6 merged on rung 2) · corpus `948d5bda` · .github `c052f94f`

## 1. The claim

`(A ; B ; …)` inside a clause body compiles to the SHARED `bb_disjunction` box with its cursor in the enclosing
activation frame — no `$disjN/k` hoisting, no synthetic predicate, no frame of its own — and the **wiring cost zero
new template code**. What the box did gain is the code that makes the choice real: a trail mark, one named rtx
helper, and an unwind on every branch step.

## 2. Fail-once, pass-once

| arm | tree | result |
|---|---|---|
| fail-once | clean origin `81b40ceb`, plain `make` | `test_prolog_ladder.sh --to 3` **rc=1**, rung 3 PASS=0 FAIL=2 (rungs 0–2 PASS 6/6). The DONE-WHEN short-circuits at its first clause |
| pass-once | this landing, `make pristine` | see § 6 |

## 3. What the wiring actually is — Icon's convention, not a new one

`pl_lower_disj` (`src/lower/lower_prolog.c`) builds `IR_DISJUNCTION` with **`lower_alt_impl`'s exact operand
convention**: `(entry_j, resume_j)` pairs, then N result operands — NULL for Prolog, because a Prolog branch forwards
no value — and rewrites the branch γ/ω edges that land on the node to σ/φ. `flat_drive_match_alt` and the existing
template then do everything: PAIR(j) = branch j's α, PAIR(N+j) = its β, PAIR(2N) = σ, PAIR(2N+1)/(2N+2) = φ.

⭐ **A deterministic branch has no resume, and that needed no special case.** It names the disjunction *itself* as its
`resume_j`, which the driver already maps to the φ landing — *a det branch's redo IS its failure*, which is Kulaš
S:disj exactly. The machinery SNOBOL4 alternation and Icon `|` have carried for years already spelled Prolog's
disjunction; the rung was mostly the work of noticing that.

`pl_lower_conj` gains `IR_DISJUNCTION` as a resumable kind, so goals to the right wire ω→its β and a clause ending in
one banks its β into `F.RES` through the rung-2 success trampoline.

## 4. Three measured defects, all fixed, none of them a mode divergence

Every one failed **identically in m3 and m4** — the ASM-DIFF-FIRST within-mode premise held throughout; there was
nothing to diff across modes.

**(a) A clause ending in a disjunction conceded to the graph ω instead of stepping to the next clause.**
`p :- (write(a);write(b)), nl, fail.  p.` printed `a b` and never reached clause 2. Rung 2's clause-step rewrite
(`ω == alt_fail → pl_step_lbl`, `γ == alt_ret[k] → ret_tr[k]`) sat at `emit.cpp:3242`, but the match-alt drive path
`continue`s at `:3147` — **before it**. ⭐ The rewrite was correct and unreachable: an early-`continue` drive arm is
invisible to every fix installed after it, and the fix's own tests all went through the late path. It is now applied
where `node_γ`/`node_ω` are first resolved (`:3100`); the late copy is left in place and is idempotent.

**(b) A branch that reduces to `true` printed NOTHING.** `p :- (true ; write(b)), write(k), nl, fail.  p.` produced
empty output where swipl prints `k` then `bk`. `true` lowers to `IR_SUCCEED`, which the RPO walk chases *through* and
never emits — so the driver's `nodes[k] == operands[2j]` lookup missed and `PAIR(j)` fell back to the node's own ω.
⭐ **An operand naming a node the emitter never emits is not a dangling pointer — it silently resolves to the
enclosing default**, and here the default was the one edge that inverts the answer: the branch entered the
disjunction's FAILURE instead of its success. `pl_disj_entry` chases `IR_SUCCEED` and synthesises an `IR_GOTO`
carrying an explicit σ γ when a branch reduces to `true`.

**(c) THE REAL ONE — the choice was real but its bindings could not be undone.**
`p :- ( X = a ; X = b ), write(X), nl, fail.  p.` printed `a` only; `d(X) :- (X = one ; X = two).` printed `one` only.

§ B.11's log rule logs a cell only at or above `[B+64]`, the choice frame's **top**. That is correct while every
choice IS a whole frame, because the thing that undoes a clause's bindings — the clause step — *re-seeds* `F.G[*]`
anyway. A disjunction opens a choice **inside** an activation, and its branch step re-seeds nothing: the frame's own
locals were bound and never logged, so branch 2 saw branch 1's bindings.

⛔ **The fold that made a choice BE a frame has no expression for a choice opened within one.** This is not a coding
slip; it is § B.5's `F.B := rbp` being under-specified, and § A.1 review C1 having retired `F.HI` on a premise
("a binder holding only `B` needs the frame top") that held only while the two were the same thing.

**Cure, landed.** `F.HI` returns as a threshold **word** at `[H+32]`:

* `pl_tr_needs_log` reads `*(char **)(B + 32)` instead of computing `B + 64`.
* The pinned prologue seeds `[H+32] := rbp + kt` — the frame top, byte-for-byte the rule rung 1 computed, so
  **rungs 0–2 emit and behave exactly as before**.
* `bb_disjunction`'s pinned α banks `r12` into the box's own pad word and calls **`rt_pl_disj_open(H, rbp)`**: writes
  `F.HI := rbp` (every cell of this activation now loggable) and raises `B` to `H` **only when the live choice is
  older than this frame or absent**. The φ glue unwinds `r12` to the banked mark through `rt_pl_tr_unwind`, the same
  named helper the rung-2 clause step uses.

⭐ **The "only when older" clause is the part a bare `F.B := rbp` gets wrong.** With a retained callee to the LEFT of
the disjunction (`q(A), (write(x) ; write(y))`) the youngest choice is *already* younger than this frame, this frame's
locals are already above `[B+64]` and already logged, and overwriting `B` would demote a live choice. Address order
decides it: a lower `B` is a younger choice, so `jb → leave it`.

`[H+32]` was verified free before it was claimed: no `rt_pl_dc_prep` appears in any Prolog `--compile` output, and no
emitted Prolog code referenced `[H+32]` on the rung-0..3 witnesses.

## 5. Instruments the mechanism change obliged, and what they were saying

* **`test_gate_pl_quad_regs.sh`** went red on `rt_pl_disj_open`'s `mov r13, rdi` — *correctly*. Enrolled by exact
  NAME in `QUAD_HELPER_RX`, one row, never a box-wide admission (rung-1 law).
* **`test_gate_pl_trail_mechanism.sh`** went red on `a cell younger than the youngest choice is bound but NOT logged`.
  ⭐ Worth reading closely: the check builds `cx.b` by hand as `(char *)&young + 16`, a synthetic `B` with no header
  behind it — so under the word rule it was dereferencing uninitialised stack. The gate was not wrong about the
  mechanism; it was **encoding the old rule in its fixture**. Its synthetic frames now carry a synthetic 64-byte
  header (`synth_b`), exactly as a real frame does, and a **13th check pins the new rule**: the same cell that is not
  logged at the seeded threshold IS logged once `F.HI` is lowered onto it.
* **`ALL.trace` rung-3 block re-cut whole** (`--to 3 --cut`), 56 → 26 lines, as corpus `100db9e3` re-cut rungs 0–2.
  The old block was the pre-cut machine — `$disj0/0`, `$trail_mark`, `$unwind_nothrow`, `suspend`. The new one is the
  Byrd disjunction and ends `Fail: disjunction -> p/0_step`, which is defect (a) visible in the trace. Rungs 0–2
  blocks verified byte-identical; block count 42 → 42.
* **`ladder__rung03_disjunction` (directive_85) leaves XFAIL** in all three places (ALL.pl banner, ALL.ref banner,
  ALL.csv column), promoted in the same commit the board proves it, `read_suite` rc=0 on the result.

## 6. Verdict arms — `make pristine` first (HQ-27), one uninterrupted DONE-WHEN run

`make pristine` rc=0, then the row's DONE-WHEN verbatim: **rc=0**.

| arm | reading |
|---|---|
| `test_prolog_ladder.sh --to 3` | ✅ **PASS 8/8** (4 witnesses × 2 modes), rung 3 PASS=2 FAIL=0 |
| `test_prolog_ladder.sh --only 6` | ✅ PASS 12/12 — rung 6 unmoved by the trail-rule change |
| `test_gate_pl_port_trace.sh --to 3` | ✅ **GATE PASS(0)**, 8 checks, killswitch + perturbation OK in both modes |
| `nm -D out/libscrip_rt.so` Prolog-only data symbols | ✅ **0** |
| `strip_comments.py --check` | ✅ rc=0 |
| `test_smoke_icon.sh` | ✅ **14/14 both modes** |
| `make test` | ✅ rc=0 — SNOBOL4 **m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0**, every gate OK |
| `test_gate_pl_quad_regs.sh` (last in `make test`) | ✅ **GATE PASS(0)** — 118 writes, 118 enrolled, 0 violations; 12 rtx routines reachable, `rt_pl_disj_open` enrolled by name |
| `test_gate_pl_trail_mechanism.sh` | ✅ **GATE PASS(0)**, now **13** checks (the 13th pins the lowered-`F.HI` rule) |
| **Icon STRICT rung suite** (control arm) | ✅ **PASS=264 FAIL=6 BADEXIT=1 XFAIL=27 TOTAL=298 in all three modes — the pinned watermark, UNCHANGED** |
| 12-witness disjunction battery vs swipl, both modes | ✅ **12/12** (3-way, nested both ways, conjunction branches, generator branch, unification branch, disjunction before/after a resumable call, disjunction inside a called predicate, `fail` branch, two disjunctions in one clause, `true` branch) |

⛔ **THE REBASE-BASELINE COROLLARY WAS PAID.** The push rebased onto `c9b9e144`, which landed while this rung was
in flight — so the pristine reading above is of a tree that no longer exists. **Re-proved end to end on the merged
tree** (SCRIP `9af884bd` · corpus `b26f38ea`): `make pristine` rc=0, DONE-WHEN **rc=0**, ladder `--to 3` PASS 8/8,
trace GATE PASS(0), quad GATE PASS(0) 28 witnesses, SNOBOL4 m3 1679/0 · m4 1679/0 SKIP=0, Icon smoke 14/14.

**REPORTED, not gating until rung 10 — the master board on the promoted master:**

```
SUITE_BOARD family=ALL total=400
  m3_pass=189 m3_fail=188 m3_crash=0 m3_hang=0 m3_unproven=0 m3_skip=0   m3_xfail=16 m3_xpass=7
  m4_pass=189 m4_fail=5   m4_crash=0 m4_hang=0 m4_unproven=0 m4_skip=183 m4_xfail=16 m4_xpass=7
```

189 of 400 both modes, from 169 at the rung-6 landing on this same master (verified: `git log 1f60f815..948d5bda -- tests/prolog/` is empty, so the two readings are of the same suite).

⭐ **Read the `m4_fail` 1 → 5 before quoting it as a regression — it is not one.** 23 entries stopped being
compile refusals: 19 became passes, 4 became `FAIL`s, and `directive_85` left the marked set as a pass; 5 more
marked-XFAIL entries flipped to XPASS. **Nothing that passed before fails now.** And all four new `FAIL`s read
`output matched but rc=0, expected 1` — the ANSWER is right; only the declared `want_rc` disagrees. All four
(`assertz_directive_{2,3,4}`, `asserta_assertz_directive_1`) are the same class as the pre-existing
`simple_program_97` that ceo already named: **entries with no `:- initialization(main).`**. Measured on all five:
`swipl -q -f E -t halt` prints NOTHING and exits 0, while SCRIP runs `main` through the `ninit == 0` fallback in
`lower_pl_stage2` and prints the right answer with rc=0 — **so SCRIP matches the oracle's rc and the pinned
`ALL.wantrc` matches neither.** The ref and the pin come from a recipe that no longer exists (hq_B's ruling: a ref
the recipe cannot produce is re-cut under the recipe). Rowed, not fixed here: it is a master-recipe question, and
the deeper half of it — *should the `ninit == 0` fallback run `main` at all, when the oracle does not?* — is a
semantics ruling, not a rung-3 defect.

⭐ **7 XPASSes are stale markers** (`directive_12/13/14/15`, `list_directive_1`, `atomconv_directive_1`,
`index_directive_1`) — up from 2 at rung 6. Rowed for promotion; a promotion moves the graded population and so
re-pins the optbypass watermark in the same commit, which is not this rung's commit.

## 7. What the next rung inherits

* **Rung 4 (cut) must read § A.1's `F.HI` row.** `B := B0` is no longer the whole of restoring a choice: a frame
  whose disjunction lowered `F.HI` still has it lowered, which over-logs (safe) but is not free. A cut that commits
  past a disjunction may restore `[H+32] := rbp + kt`; nothing requires it for correctness.
* `g->deterministic` was suspected in defect (c) and is **exonerated — it has no consumer anywhere in `src/`**
  (declared at `IR.h:217`, set by `lower_prolog.c`, read by nothing). A single-clause predicate whose body carries a
  choice is stamped deterministic today and it costs nothing; whoever gives that flag a consumer must fix the stamp
  first.
* The disjunction's σ glue still emits Icon's per-arm value-copy dispatch chain with every arm slot `-1` — dead
  compares for Prolog. Correct, not free; a rung-12/13 concern, not a correctness one.
