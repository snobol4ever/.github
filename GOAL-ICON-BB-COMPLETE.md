# GOAL-ICON-BB-COMPLETE.md — All Icon Byrd-Box constructs working in modes 1, 2, 3 (then 4)

**Repo:** one4all (primary) + .github (this file)
**Sister docs:** `GOAL-CHUNKS.md` (parent umbrella), `GOAL-CHUNKS-STEP17.md`
(sibling — owns the proc/pred-table migration), `GOAL-LANG-ICON.md`
(Icon-frontend feature work — language coverage, builtins).
**Tracker:** carved sess 2026-05-10.  This goal exists because the
"Icon BB-box for every construct" property is *not* visible as a
single rung in either parent.  CHUNKS-STEP17 carves it implicitly
across CH-17i sub-rungs (every / suspend / bang-concat / section /
limit-random / iterate / alternate / …) but the closure property —
"every Icon construct that can appear inside a generator context
has a real lowering to SM" — is not stated as a single deliverable
anywhere.  This file states it.

**Done when:**

1. **Closure property (structural).**  Every AST kind reachable
   from a `--ir-run` PASS Icon program lowers via `sm_lower.c` to
   pure SM (no `emit_push_expr` + `SM_BB_PUMP` legacy fallthrough
   fires for any Icon program in the corpus).  The legacy
   fallthrough block at `sm_lower.c:1410-1418` is **deleted**
   (not just bypassed for migrated kinds — physically removed; any
   new generative AST kind must add its own lowering or build
   will fail loudly).

2. **Mode-1 byte-identical.**  `--ir-emit` output byte-identical
   to pre-rung baseline for every Icon program in the corpus.
   (Lowering changes are SM-side only; the IR layer is untouched.)

3. **Mode-3 HONEST parity.**  `SCRIP_NO_AST_WALK=1 ./scrip --sm-run <prog>`
   produces output byte-identical to `./scrip --ir-run <prog>` for
   every program in the `--ir-run` PASS set.  This is the *honest*
   gate: the env var enables a runtime tripwire (added in rung A0)
   that aborts SM dispatch if it reaches `coro_eval` /
   `interp_eval` / `call_user_function` / `execute_program` /
   `interp_eval_pat` / `interp_eval_ref`.  Output equality WITHOUT
   the env var (the cheat-blind gate) is necessary but not
   sufficient — programs can pass that today by silently using
   the AST walker.

4. **Mode-4 unblock.**  Every SM opcode emitted by Icon lowering
   has a `sm_codegen_x64` mirror.  No emitted-binary code path
   reaches an AST walker.  (Mode-4 *coverage* is owned by
   `GOAL-MODE4-EMIT.md`; this goal's deliverable is "the SM input
   to mode 4 is structurally complete".)

5. **`is_suspendable` and `coro_eval` retired for SM dispatch.**
   `coro_eval` may still serve `--ir-run` (mode 2's AST walker —
   that's its job).  But it is not reachable from SM dispatch
   under `SCRIP_NO_AST_WALK=1`.  This is the structural witness
   that there is no fallback under SM.

⛔ **Definition of "cheating" in this goal:** today, `./scrip --sm-run`
will silently invoke `coro_eval` for kinds that haven't been
migrated.  Output looks correct because mode 2's machinery does
the work.  This is "mode 3 with mode 2 in a trench coat."  The
goal is to make mode 3 stand on its own — every kind has a real
SM lowering, and SM dispatch never reaches into the AST walker.
The SCRIP_NO_AST_WALK env var is the dial that proves this.

---

## Why this file exists

The previous session (2026-05-10) attempted CH-17g-irrun-execution
Step 2 ahead of the per-kind migrations.  That tried to flip the
**driver** path before the **per-kind lowerings** were in place.
Result: routing `--ir-run` through `sm_call_proc` exposed every
still-legacy-fallthrough kind at runtime as a 76-program regression
(177→105 PASS).  The session correctly reverted and recorded
"file CH-17g-irrun-prep + CH-17i-table-mutators + CH-17i-icn-list-mutators
ahead of Step 2 retry".

Reading further, the gap is wider than three sub-rungs.  Six AST
kinds still hit the legacy fallthrough (`sm_lower.c:1410-1418`),
plus a larger set of generative reductions (binops with a generator
child, `s[i to j]`, `x := (1|2|3)`, etc.) lower correctly only
when their children are scalar.  The existing CH-17i sub-rungs
(every, suspend, bang-concat, section, limit-random) cover the
flagrant cases but don't state the closure property.

Proebsting's *Simple Translation of Goal-Directed Evaluation*
(1997) makes the property obvious: every Icon construct has a
four-port template (start, resume, succeed, fail) wired with
`goto`s.  JCON's `tran/irgen.icn` (Cary Coutant, 1559 lines, 69
`ir_a_<Construct>` procedures) is the executable proof —
*"every Icon construct"* means literally that.  This goal lifts
the closure property to a named deliverable and orders the
remaining work so it lands incrementally without breaking any
of the three modes.

Lon's framing (sess 2026-05-10): *"Seems to me we just lower Icon
to the wiring of the boxes and jump to the code."*  Correct.
That is what JCON does and what `sm_lower` already does for
migrated kinds.  This goal finishes the job.

---

## Architecture reminder

```
.icn → icon_parse() → AST_t* tree [LANG_ICN]
    --ir-emit   → ir_print_program(...)                       Mode 1
    --ir-run    → execute_program() → interp_eval()           Mode 2  (AST walker)
                  + coro_eval() for generators
    --sm-run    → sm_lower() → SM_Program → sm_interp_run()   Mode 3
    --jit-run   → sm_lower() → sm_codegen_x64() → run         Mode 3.5 (in-process JIT)
    --jit-emit  → sm_lower() → sm_codegen_x64() → standalone  Mode 4
                  binary linked against libscrip_rt.so only
```

**Goal-directed evaluation in SM:** every generator-context AST
kind lowers to a sequence ending in either `SM_SUSPEND_VALUE` (yield
to caller, swapcontext) or `SM_RETURN`/`SM_FRETURN` (succeed/fail
to caller).  Goal-directed retry is the caller's loop:
`bb_broker(BB_PUMP, ...)` re-enters the chunk via `swapcontext`
back to the suspended coroutine, which falls through to whatever
SM follows the `SM_SUSPEND_VALUE`.  No AST walking at runtime.

**The four ports map to SM as follows** (Proebsting §4 → one4all):
```
Proebsting       JCON ir.icn         one4all SM
─────────────    ─────────────       ──────────────────────────
start            ir_EnterInit        chunk entry pc (lower_expr)
resume           ir_ResumeValue      next SM instr after SM_SUSPEND_VALUE
succeed          ir_Succeed          push value + SM_SUSPEND_VALUE OR fall through
fail             ir_Fail             SM_FRETURN / SM_JUMP_F to outer fail label
goto             ir_Goto             SM_JUMP <label>
indirect goto    ir_IndirectGoto     SM_JUMP_REG (gate variable)
```

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```

Baseline gates (run all green BEFORE picking up the next rung):

```bash
bash scripts/test_smoke_icon.sh                    # PASS=5
bash scripts/test_smoke_unified_broker.sh          # PASS=49
bash scripts/test_isolation_ir_sm.sh               # PASS
bash scripts/test_smoke_scrip_all_modes.sh         # PASS=2
bash scripts/test_icon_ir_all_rungs.sh             # baseline 177/56/30 (or current)
bash scripts/test_icon_ir_all_rungs.sh --sm-run    # establishes --sm-run baseline
```

Per-rung gates are listed under each rung below.

---

## Self-detection / self-correction protocol

Each rung in this file is **self-detecting** (it tells you whether
it is needed and whether it is done) and **self-correcting**
(regression in any prior rung is caught immediately, with a clear
pointer to which rung broke).  No human-eyeballing of diffs.  No
"looks byte-identical to me".  The protocol is mechanical.

### What "works in mode 3" means — cheat detection

⛔ **Output equality is necessary but not sufficient.**  Today, a
program can run under `--sm-run` and produce identical output to
`--ir-run` because the `--sm-run` path silently falls back to
the AST walker (`coro_eval`) for any kind not yet migrated.  That
is the **cheat** this goal exists to eliminate.  A probe that only
checks output equality is blind to it.

A rung is **honestly complete** iff:
1. Output identical to `--ir-run` (oracle correctness)
2. **No `SM_PUSH_EXPR` fires** for the migrated kind across the corpus
3. **No `coro_eval(AST_t*)` call** is made from inside `sm_interp_run`'s
   call graph during execution of any program that exercises the
   migrated kind
4. The kind is no longer in the legacy-fallthrough block
   `sm_lower.c:1410-1418` (Phase A) or its scalar arm explicitly
   handles `is_suspendable(child)` via SM lowering rather than
   delegating to `coro_eval` (Phase B/C)

(1) is the oracle gate.  (2) is the audit-counter witness — set
`SCRIP_EXPRS_AUDIT=1` and parse the atexit summary line.  (3) is
the structural witness — the existing isolation gate
(`scripts/test_isolation_ir_sm.sh`) plus a runtime tripwire
described below.  (4) is the source-of-truth witness.

⛔ **The output-equality-only probe is the trap.**  A probe that
checks (1) alone will report "rung complete" while the cheat is
still happening.  Every probe in this file checks (2) and the
final-rung gate (A7) checks (4).  The runtime tripwire for (3)
is below.

### Runtime cheat tripwire — `SCRIP_NO_AST_WALK=1`

⛔ **Build-blocker subgoal.**  The goal depends on having a
runtime gate that aborts when SM dispatch reaches the AST walker.
This does not exist today.  Add it as a prerequisite rung:

#### A0 — CH-17i-cheat-tripwire — gate `coro_eval` against SM dispatch

- [ ] In `coro_runtime.c`, add a thread-local flag
      `int g_sm_dispatch_active = 0;` set to 1 at entry of
      `sm_interp_run` / `sm_call_proc` and back to 0 at exit.
- [ ] At top of `coro_eval`, if `getenv("SCRIP_NO_AST_WALK")` is set
      AND `g_sm_dispatch_active` is true, print
      `FATAL: coro_eval reached from SM dispatch (program=<...>, kind=<...>)`
      and `abort()`.  Otherwise no-op (mode 2 keeps working).
- [ ] Same gate at top of `interp_eval`, `interp_eval_pat`,
      `interp_eval_ref`, `call_user_function`, `execute_program`
      — the five symbols the existing isolation gate already names.
- [ ] **Detection probe:** the gate is functional iff a deliberate
      `coro_eval` call from inside SM dispatch (Phase A unmigrated
      kind under `SCRIP_NO_AST_WALK=1`) aborts.  Negative test:
      build, run a program known to hit `AST_BANG_BINARY` under
      `SCRIP_NO_AST_WALK=1 ./scrip --sm-run <prog>`, observe abort
      with kind name in message.
- [ ] **Completion probe:**  positive — without the env var, all
      modes work as before (smoke ×6 byte-identical).  Negative —
      every Phase-A unmigrated kind triggers the abort under
      `SCRIP_NO_AST_WALK=1` on a representative program.
- [ ] **Gate:** smoke ×6 byte-identical without env var; isolation
      gate PASS; new `scripts/test_icon_sm_no_ast_walk.sh` runs the
      Icon corpus under `SCRIP_NO_AST_WALK=1 --sm-run` and reports
      PASS=N where N grows as Phase A/B/C land (baseline N today
      is whatever passes without hitting any fallthrough — likely
      a small fraction of the 263).

A0 is the first rung.  Without it, every later rung's "honest
mode 3" claim is unverifiable and we ship a cheat-blind ladder.

### Captured baselines (run once at goal start)

The protocol depends on having known-good outputs to compare
against.  Run this **once at goal start, after A0 lands**, and
keep `baselines/` outside version control (working artifact).

The corpus path is **`/home/claude/corpus/programs/icon/`** — see
`CORPUS-LOCATIONS.md` for the canonical list of corpus paths.
This file's probes use `$CORPUS` with that as default.

```bash
cd /home/claude/one4all
mkdir -p baselines/icon-bb
export CORPUS="${CORPUS:-/home/claude/corpus/programs/icon}"

# 1. Per-program output md5s under --ir-run (the truth oracle)
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    out=$(./scrip --ir-run "$f" 2>&1)
    rc=$?
    echo "$name $rc $(echo -n "$out" | md5sum | cut -d' ' -f1)" \
         >> baselines/icon-bb/ir-run.md5
done

# 2. Per-program output md5s under --sm-run WITHOUT the cheat tripwire
#    (current state — programs may be silently falling back to AST walker).
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    out=$(./scrip --sm-run "$f" 2>&1)
    rc=$?
    echo "$name $rc $(echo -n "$out" | md5sum | cut -d' ' -f1)" \
         >> baselines/icon-bb/sm-run.md5
done

# 3. Per-program output md5s under --sm-run WITH the cheat tripwire
#    (the honest baseline — programs that abort here are NOT actually
#    working in mode 3 today, regardless of what (2) says).
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    out=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "$f" 2>&1)
    rc=$?
    echo "$name $rc $(echo -n "$out" | md5sum | cut -d' ' -f1)" \
         >> baselines/icon-bb/sm-run-honest.md5
done

# 4. Smoke set md5s (every rung must keep these byte-identical)
for s in icon snobol4 snocone prolog raku rebus; do
    bash scripts/test_smoke_${s}.sh 2>&1 | md5sum > baselines/icon-bb/smoke-${s}.md5
done
bash scripts/test_smoke_unified_broker.sh 2>&1 | md5sum \
    > baselines/icon-bb/smoke-unified-broker.md5

# 5. Audit counter baseline — every program's SM_PUSH_EXPR fire count
#    under --sm-run.  A7 requires this to reach all-zero corpus-wide.
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    fires=$(SCRIP_EXPRS_AUDIT=1 ./scrip --sm-run "$f" 2>&1 \
            | grep -oP 'SM_PUSH_EXPR=\K\d+' | head -1)
    fires=${fires:-0}
    echo "$name $fires" >> baselines/icon-bb/audit-fires.txt
done

# 6. Per-kind cheat-fire baseline — for each kind in the legacy-fallthrough
#    set, list every program that hits it.  This is the per-rung work list.
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    SCRIP_EXPRS_AUDIT=1 ./scrip --sm-run "$f" 2>&1 \
        | grep -oP '\[CHUNKS-AUDIT\] SM_PUSH_EXPR fired at pc=\d+ \(\K[^)]+' \
        | sort -u | while read kind; do
            echo "$kind $name" >> baselines/icon-bb/cheat-by-kind.txt
        done
done
sort baselines/icon-bb/cheat-by-kind.txt -o baselines/icon-bb/cheat-by-kind.txt
```

The `cheat-by-kind.txt` baseline is the **work plan witness**: it
lists which corpus programs each Phase A rung will affect.  The
rung's detection probe checks this baseline (the rung is needed
iff its kind appears in the baseline); the rung's completion
probe verifies the kind has been removed from the post-rung
re-capture of this baseline.

The `sm-run-honest.md5` baseline captures the **honest mode 3**
state — programs that produce wrong output (or abort) here are
not actually working in mode 3 today, even if their `sm-run.md5`
is correct.  Goal terminus: `sm-run-honest.md5` matches
`ir-run.md5` for every program in the `--ir-run` PASS set.

### Per-rung detection probe — kind-fire-based (Phase A)

Every Phase A rung's detection probe asks one question: **does
the migrated kind appear in `cheat-by-kind.txt`?**  If yes, rung
needed.  If no (e.g. closed by sister work), rung not needed.

### Per-rung completion probe — three witnesses, all must hold

(a) **Output witness:** anchor program byte-identical across modes
under both `--sm-run` and `SCRIP_NO_AST_WALK=1 --sm-run`.

(b) **Audit witness:** the migrated kind has zero `SM_PUSH_EXPR`
fires across the corpus (re-capture `cheat-by-kind.txt` and grep
for the kind name; expected zero matches).

(c) **Honest-corpus witness:** at least one program flipped from
"aborts under SCRIP_NO_AST_WALK" to "passes under SCRIP_NO_AST_WALK"
— this proves the rung produced a structurally honest gain, not
just an output-equivalent one.

### Regression tripwire (run at end of every rung)

```bash
bash scripts/test_smoke_icon.sh         | md5sum | diff - baselines/icon-bb/smoke-icon.md5
bash scripts/test_smoke_snobol4.sh      | md5sum | diff - baselines/icon-bb/smoke-snobol4.md5
bash scripts/test_smoke_snocone.sh      | md5sum | diff - baselines/icon-bb/smoke-snocone.md5
bash scripts/test_smoke_prolog.sh       | md5sum | diff - baselines/icon-bb/smoke-prolog.md5
bash scripts/test_smoke_raku.sh         | md5sum | diff - baselines/icon-bb/smoke-raku.md5
bash scripts/test_smoke_rebus.sh        | md5sum | diff - baselines/icon-bb/smoke-rebus.md5
bash scripts/test_smoke_unified_broker.sh | md5sum | diff - baselines/icon-bb/smoke-unified-broker.md5
```

Empty output from every `diff` = no regression.  Any non-empty
output names exactly which gate broke.

### Per-program forward audit (run after every Phase A rung)

```bash
export CORPUS="${CORPUS:-/home/claude/corpus/programs/icon}"

# Show every program whose --ir-run output md5 changed (must be empty
# until CH-17g-irrun-execution lands; --ir-run untouched by this goal):
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    out=$(./scrip --ir-run "$f" 2>&1)
    new_md5=$(echo -n "$out" | md5sum | cut -d' ' -f1)
    base=$(grep "^$name " baselines/icon-bb/ir-run.md5 | awk '{print $3}')
    [ "$new_md5" != "$base" ] && echo "REGRESSION: $name ir-run md5 $base → $new_md5"
done

# Show every program whose --sm-run-HONEST status changed.  This is
# the goal's real progress dial: programs flipping from "aborts under
# SCRIP_NO_AST_WALK" to "matches ir-run under SCRIP_NO_AST_WALK".
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    sm_h_out=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "$f" 2>&1)
    sm_h_md5=$(echo -n "$sm_h_out" | md5sum | cut -d' ' -f1)
    ir_md5=$(grep "^$name " baselines/icon-bb/ir-run.md5 | awk '{print $3}')
    sm_h_base=$(grep "^$name " baselines/icon-bb/sm-run-honest.md5 | awk '{print $3}')
    if [ "$sm_h_md5" = "$ir_md5" ] && [ "$sm_h_md5" != "$sm_h_base" ]; then
        echo "FLIPPED-HONEST: $name now matches ir-run under SCRIP_NO_AST_WALK"
    elif [ "$sm_h_md5" != "$ir_md5" ] && [ "$sm_h_base" = "$ir_md5" ]; then
        echo "REGRESSION-HONEST: $name was passing honest mode 3, now diverging"
    fi
done
```

`FLIPPED-HONEST` lines = real, structural progress.  Output
equality without `FLIPPED-HONEST` is the cheat.

### Bisection helper

If a `REGRESSION` shows up after a rung, walk one4all's git log
between baseline and HEAD; for each commit, rebuild and run the
regressing program; report which commit's parent was clean and
which commit broke it.  See script in
`scripts/icon_bb_bisect.sh` (created at A0 land).

### Audit-counter tripwire (final, A7)

After A7 lands, this assertion must hold across the entire Icon
corpus, in both `--sm-run` and `--jit-run`:

```bash
fail=0
export CORPUS="${CORPUS:-/home/claude/corpus/programs/icon}"
for f in $CORPUS/rung*.icn; do
    name=$(basename "$f" .icn)
    for mode in --sm-run --jit-run; do
        fires=$(SCRIP_EXPRS_AUDIT=1 ./scrip $mode "$f" 2>&1 \
                | grep -oP 'SM_PUSH_EXPR=\K\d+' | head -1)
        fires=${fires:-0}
        if [ "$fires" -ne 0 ]; then
            echo "FAIL: $name $mode SM_PUSH_EXPR=$fires (expected 0)"
            fail=1
        fi
    done
done
exit $fail
```

After A7, this script exits 0.  It is the closure-property
witness — Phase A is done iff this script passes AND
`baselines/icon-bb/sm-run-honest.md5` matches `ir-run.md5`
program-for-program (for the `--ir-run` PASS set).

### What "self-correcting" means in practice

Each rung's gate runs the **regression tripwire** above.  If any
diff is non-empty, the rung does not land — the offending change
is reverted on the spot, the breakage is investigated, and the
rung is restarted with the diagnosis recorded inline in the rung
(under `## Diagnosis` if it occurred).

The **forward audit** catches the case where the rung's intended
target works under output-equality but a different program
regresses on the **honest** corpus run.  The two scripts together
form the safety net.

The **bisection helper** is the recovery tool: if a regression
makes it past the gate (e.g. because two rungs landed in one
session), it tells you exactly which rung to revert.

---

## The seven AST kinds in the legacy fallthrough today

These six kinds at `src/runtime/x86/sm_lower.c:1410-1418` are the
**hard gap** — they emit the AST-pointer-on-stack legacy pattern
that breaks Mode 4:

```c
case AST_BANG_BINARY:    /*  E1 ! E2  — invoke E1 with list E2     */
case AST_LIMIT:          /*  E \ N    — limitation                 */
case AST_RANDOM:         /*  ?E       — random element / integer   */
case AST_SECTION:        /*  E[i:j]   — string/list section        */
case AST_SECTION_MINUS:  /*  E[i:-j]  — section with neg right     */
case AST_SECTION_PLUS:   /*  E[i:+j]  — section with rel right     */
    emit_push_expr(p, e);
    sm_emit(p, SM_BB_PUMP);
    return;
```

Plus the generative variant of `AST_LCONCAT` at `sm_lower.c:1389-1406`
(scalar variant already migrated CH-17i Phase 1, generative variant
still falls through).

These are Phase A.

## The generative-reduction set (`is_suspendable` returns 1 by recursion)

`coro_runtime.c:657-702` — kinds that are normally scalar but
become generative when one of their children is a generator.
Today the SM lowering for these emits scalar SM and works ONLY
when children are scalar.  When a generator appears as a child,
the code path that runs is the AST walker via `coro_eval`, NOT
the SM lowering.

```c
AST_ADD AST_SUB AST_MUL AST_DIV AST_MOD       /* arithmetic           */
AST_LT AST_LE AST_GT AST_GE AST_EQ AST_NE     /* numeric relops       */
AST_LLT AST_LLE AST_LGT AST_LGE AST_LEQ AST_LNE  /* string relops     */
AST_IDENTICAL                                 /*  ===                 */
AST_LCONCAT AST_CAT                           /*  |||  and  ||        */
AST_NONNULL AST_NULL                          /*  \E  and  /E         */
AST_IDX                                       /*  s[i to j]           */
AST_ASSIGN                                    /*  x := (1|2|3)        */
AST_REVASSIGN AST_REVSWAP                     /*  always generative   */
AST_FNC                                       /*  builtin w/ gen arg  */
                                              /*  user proc w/ suspend */
```

These are Phase B (generative reductions) and Phase C (the
control-flow constructs that need to stay generator-aware:
`while/until/repeat`, `if`, `not` when their conditions are
generators).

---

## The 11 rungs (atomic, byte-identical at every step)

Each rung migrates one AST kind (or one tightly-coupled cluster)
off legacy lowering onto a real SM lowering.  The shape is
identical across rungs — taken from CH-17i-every / CH-17i-suspend
which pioneered the pattern:

1. Add an `SM_BB_PUMP_<KIND>` opcode in `sm_prog.h` (or use the
   unified `SM_BB_PUMP_AST` if Lon's 2026-05-10 design lands first
   — see "Open design question" below).
2. Add a per-kind `g_<kind>_table` registry in `sm_interp.c` with
   `<kind>_table_register(AST_t*)` / `<kind>_table_lookup(int)` /
   `<kind>_table_reset()`.  Same lifetime model: borrowed AST
   pointers, populated by `sm_lower` at lower time, reset on
   `sm_program_free`.
3. Implement `h_bb_pump_<kind>` handler in `sm_interp.c`:
   `lookup → coro_eval → bb_broker(BB_PUMP, NULL, NULL); push
   NULVCL` (or whatever the kind's stack discipline requires).
4. Implement `h_bb_pump_<kind>` JIT mirror in `sm_codegen.c`.
5. In `sm_lower.c`, carve the kind out of the legacy fallthrough
   block; emit `sm_emit_i(p, SM_BB_PUMP_<KIND>, register(e))`.
6. Document validation in `docs/CHUNKS-icon-bb-<kind>-validation.md`.

**Net stack delta:** every BB-pump opcode pushes exactly one
descriptor (NULVCL for void-context, a real value for
value-context) so the trailing proc-body `SM_VOID_POP` balances.
This is the lesson from CH-17i-every: legacy SM_BB_PUMP was
net-stack-zero, which underflowed when `sm_call_proc` (CH-17g)
fell through the trailing VOID_POP.

### Probe helpers — `scripts/icon_bb_probes.sh`

Rather than repeat ~30 lines of probe code in every rung, the
detection / completion / regression patterns are factored into
two shell functions in `scripts/icon_bb_probes.sh`.  Each rung
calls them with its own kind list and test anchor.  Create the
script at goal start (committed to one4all):

```bash
#!/bin/bash
# icon_bb_probes.sh — detection/completion probes for GOAL-ICON-BB-COMPLETE rungs.
# Each function exits 0 on the "good" answer and 1 on the "bad" answer.
#
# Usage from a rung:
#   source scripts/icon_bb_probes.sh
#   bb_probe_detect  "A1" "AST_BANG_BINARY|AST_LCONCAT"  rung15_real_swap_lconcat
#   bb_probe_complete "A1" "AST_BANG_BINARY|AST_LCONCAT" rung15_real_swap_lconcat

set -u

# Detection: rung is needed iff one of {anchor program fires SM_PUSH_EXPR}
#                                  OR {any program fires SM_PUSH_EXPR for this kind set}
bb_probe_detect() {
    local rung="$1" kind_re="$2" anchor="$3"
    local fires
    fires=$(SCRIP_EXPRS_AUDIT=1 ./scrip --sm-run "${CORPUS}/${anchor}.icn" 2>&1 \
            | grep -cE "(${kind_re}).*SM_PUSH_EXPR fired")
    if [ "$fires" -gt 0 ]; then
        echo "$rung needed: anchor $anchor has $fires fires"
        return 0
    fi
    # Anchor clean — sweep corpus
    local total=0
    for f in ${CORPUS}/rung*.icn; do
        local n
        n=$(basename "$f" .icn)
        local c
        c=$(SCRIP_EXPRS_AUDIT=1 ./scrip --sm-run "$f" 2>&1 \
            | grep -cE "(${kind_re}).*SM_PUSH_EXPR fired")
        total=$((total + c))
    done
    if [ "$total" -gt 0 ]; then
        echo "$rung needed: corpus has $total fires for kinds /$kind_re/"
        return 0
    fi
    echo "$rung already closed (no fires)"
    return 1
}

# Completion: HONEST mode 3 — output equality is necessary but not sufficient.
#   (a) anchor sm-run output matches ir-run             [output witness]
#   (b) anchor passes under SCRIP_NO_AST_WALK=1         [structural witness]
#   (c) audit counter zero for kind set across corpus   [closure witness]
#   (d) smoke ×6 + unified-broker md5 unchanged         [no-regression]
#   (e) at least one corpus program flipped from
#       "aborts under SCRIP_NO_AST_WALK" to "matches"   [progress witness]
bb_probe_complete() {
    local rung="$1" kind_re="$2" anchor="$3"
    local fail=0

    # (a) anchor flips FAIL→PASS (output equality)
    local ir_out sm_out
    ir_out=$(./scrip --ir-run "${CORPUS}/${anchor}.icn" 2>&1)
    sm_out=$(./scrip --sm-run "${CORPUS}/${anchor}.icn" 2>&1)
    if [ "$ir_out" != "$sm_out" ]; then
        echo "$rung FAIL (a): anchor $anchor sm-run differs from ir-run"
        diff <(echo "$ir_out") <(echo "$sm_out") | head -5
        fail=1
    fi

    # (b) anchor honest under SCRIP_NO_AST_WALK
    local h_out
    h_out=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "${CORPUS}/${anchor}.icn" 2>&1)
    local h_rc=$?
    if [ "$h_rc" -ne 0 ] || [ "$h_out" != "$ir_out" ]; then
        echo "$rung FAIL (b): anchor $anchor cheats — fails under SCRIP_NO_AST_WALK"
        echo "  rc=$h_rc"
        diff <(echo "$ir_out") <(echo "$h_out") | head -5
        fail=1
    fi

    # (c) audit counter zero for kinds across corpus
    for f in ${CORPUS}/rung*.icn; do
        local n
        n=$(basename "$f" .icn)
        local c
        c=$(SCRIP_EXPRS_AUDIT=1 ./scrip --sm-run "$f" 2>&1 \
            | grep -cE "(${kind_re}).*SM_PUSH_EXPR fired")
        if [ "$c" -gt 0 ]; then
            echo "$rung FAIL (c): $n still has $c fires for /$kind_re/"
            fail=1
        fi
    done

    # (d) smoke set md5 unchanged
    local s cur base
    for s in icon snobol4 snocone prolog raku rebus; do
        cur=$(bash scripts/test_smoke_${s}.sh 2>&1 | md5sum | awk '{print $1}')
        base=$(awk '{print $1}' baselines/icon-bb/smoke-${s}.md5)
        if [ "$cur" != "$base" ]; then
            echo "$rung FAIL (d): smoke-$s md5 diverged"
            fail=1
        fi
    done

    # (e) progress witness — at least one corpus program flipped from
    #     "aborts honest" to "matches honest"
    local flipped=0
    for f in ${CORPUS}/rung*.icn; do
        local n
        n=$(basename "$f" .icn)
        local h_md5 ir_md5 base_h_md5
        h_md5=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "$f" 2>&1 \
                | md5sum | cut -d' ' -f1)
        ir_md5=$(grep "^$n " baselines/icon-bb/ir-run.md5 | awk '{print $3}')
        base_h_md5=$(grep "^$n " baselines/icon-bb/sm-run-honest.md5 | awk '{print $3}')
        [ "$h_md5" = "$ir_md5" ] && [ "$base_h_md5" != "$ir_md5" ] && \
            flipped=$((flipped + 1))
    done
    if [ "$flipped" -eq 0 ]; then
        echo "$rung WARN (e): no programs flipped honest-mode-3"
        echo "  (acceptable if rung is structural-only, e.g. opcode plumbing)"
    else
        echo "$rung gain: $flipped programs flipped honest-mode-3"
    fi

    [ "$fail" -eq 0 ] && echo "$rung complete"
    return $fail
}

# Convenience: scoreboard — counts of FLIPPED-HONEST / REGRESSION-HONEST /
# STILL_PASS / STILL_FAIL.  This is the dial for honest mode 3.
bb_probe_scoreboard() {
    local flipped=0 regressed=0 still_pass=0 still_fail=0
    for f in ${CORPUS}/rung*.icn; do
        local n
        n=$(basename "$f" .icn)
        local h_md5 ir_md5 base_h_md5
        h_md5=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "$f" 2>&1 \
                | md5sum | cut -d' ' -f1)
        ir_md5=$(grep "^$n " baselines/icon-bb/ir-run.md5 | awk '{print $3}')
        base_h_md5=$(grep "^$n " baselines/icon-bb/sm-run-honest.md5 | awk '{print $3}')
        if [ "$h_md5" = "$ir_md5" ] && [ "$base_h_md5" != "$ir_md5" ]; then
            flipped=$((flipped + 1))
        elif [ "$h_md5" != "$ir_md5" ] && [ "$base_h_md5" = "$ir_md5" ]; then
            regressed=$((regressed + 1))
        elif [ "$h_md5" = "$ir_md5" ]; then
            still_pass=$((still_pass + 1))
        else
            still_fail=$((still_fail + 1))
        fi
    done
    echo "honest-mode-3 scoreboard:"
    echo "  FLIPPED-HONEST=$flipped REGRESSION-HONEST=$regressed"
    echo "  STILL-PASSING-HONEST=$still_pass STILL-FAILING-HONEST=$still_fail"
    [ "$regressed" -eq 0 ]
}
```

### Per-rung usage pattern

Every rung's probes collapse to two lines:

```bash
source scripts/icon_bb_probes.sh

# Before coding the rung — confirm gap is real
bb_probe_detect   "<rung-id>" "<KIND_RE>" "<anchor-basename>"

# After coding the rung — confirm done + no regression
bb_probe_complete "<rung-id>" "<KIND_RE>" "<anchor-basename>"

# Quick portfolio view — flipped/regressed counts across whole corpus
bb_probe_scoreboard
```

### Phase A — drain the legacy fallthrough (sm_lower.c:1410-1418)

#### A1 — CH-17i-bang-concat-gen — `AST_BANG_BINARY` + `AST_LCONCAT` (generative variant)
- [ ] **JCON model:** `ir_a_Binop` (irgen.icn) with `closure` parameter wiring left-then-right generators.
- [ ] **Existing `bb_node_t` shape:** `coro_eval` already constructs `icn_bang_binary_state_t` and `icn_binop_gen_state_t` (see `coro_runtime.c` — search "ICN_BINOP_CONCAT").  Reuse via `coro_eval → bb_broker`.
- [ ] **Test anchor:** `test/icon/rung15_real_swap_lconcat.icn` — IR PASS, SM FAIL today (rc=134, "sm_interp: stack underflow").  Audit confirms `[CHUNKS-AUDIT] SM_PUSH_EXPR fired at pc=3 (legacy AST_t* path)`.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `sm_lower.c`.
- [ ] **Gate:** smoke ×6 byte-identical, isolation PASS, Icon corpus 263 byte-identical, NEW: `rung15_real_swap_lconcat --sm-run` byte-identical to `--ir-run` (`hello world\n`).
- [ ] Doc: `docs/CHUNKS-icon-bb-bang-concat-gen-validation.md`.

**Detection probe:**
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect   "A1" "AST_BANG_BINARY|AST_LCONCAT" "rung15_real_swap_lconcat"
```
**Completion probe:**
```bash
source scripts/icon_bb_probes.sh
bb_probe_complete "A1" "AST_BANG_BINARY|AST_LCONCAT" "rung15_real_swap_lconcat"
bb_probe_scoreboard
```

#### A2 — CH-17i-section — `AST_SECTION` + `AST_SECTION_MINUS` + `AST_SECTION_PLUS`
- [ ] **JCON model:** `ir_a_Sectionop` (irgen.icn).
- [ ] **Existing `bb_node_t` shape:** check `coro_eval` for `AST_SECTION*` arms.  If none, create `icn_section_state_t { subj, lo, hi, kind }` mirroring `icn_to_state_t`.
- [ ] **Test anchor:** any program using `s[1 to 3]` or `s[i:-1]` with a generator subscript.  Identify in survey.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `sm_lower.c`.
- [ ] **Gate:** standard set + named test anchor flips FAIL→PASS under `--sm-run`.
- [ ] Doc: `docs/CHUNKS-icon-bb-section-validation.md`.

**Probes** (anchor name TBD by survey; substitute when known):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect   "A2" "AST_SECTION|AST_SECTION_MINUS|AST_SECTION_PLUS" "<anchor>"
bb_probe_complete "A2" "AST_SECTION|AST_SECTION_MINUS|AST_SECTION_PLUS" "<anchor>"
bb_probe_scoreboard
```


#### A3 — CH-17i-limit-random — `AST_LIMIT` + `AST_RANDOM`
- [ ] **JCON model:** `ir_a_Limitation` (irgen.icn:113) — clean Proebsting four-port wiring with a `c` (counter), `t` (limit value), `one` (constant 1) tmps.
- [ ] **Existing `bb_node_t` shape:** check for `icn_limit_state_t` / `icn_random_state_t`.  Limit mirrors Proebsting `to`-with-counter; Random is one-shot per α (re-randomize on β).
- [ ] **Test anchor:** programs using `\` (e.g. `every write(seq() \ 5)`) and `?L` for list element pick.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `sm_lower.c`.
- [ ] **Gate:** standard set + corpus probe.
- [ ] Doc: `docs/CHUNKS-icon-bb-limit-random-validation.md`.

**Probes:**
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect   "A3" "AST_LIMIT|AST_RANDOM" "<anchor>"
bb_probe_complete "A3" "AST_LIMIT|AST_RANDOM" "<anchor>"
bb_probe_scoreboard
```


#### A4 — CH-17i-iterate — `AST_ITERATE` (single `!E`, distinct from `AST_BANG_BINARY`)
- [ ] **JCON model:** `ir_a_Unop` (irgen.icn) with closure for `!`.
- [ ] **Existing `bb_node_t` shape:** `icn_bb_iterate` (per `GOAL-LANG-ICON.md`'s box list).  Confirm in `coro_runtime.c`.
- [ ] **Test anchor:** `every write(!list)` programs.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `sm_lower.c`.
- [ ] **Gate:** standard set.
- [ ] Doc: `docs/CHUNKS-icon-bb-iterate-validation.md`.

**Probes:**
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect   "A4" "AST_ITERATE" "<anchor>"
bb_probe_complete "A4" "AST_ITERATE" "<anchor>"
bb_probe_scoreboard
```


#### A5 — CH-17i-alternate — `AST_ALTERNATE` (`E1 | E2` Icon generator alternation)
- [ ] **JCON model:** `ir_a_Alt` (irgen.icn) — wires `E1.fail → E2.start`, `E1.succeed → outer.succeed`, `E1.resume → E1.resume`, `E2.{fail,succeed,resume} → outer.{fail,succeed,E2.resume}`.
- [ ] **Existing `bb_node_t` shape:** check for `icn_alternate_state_t`.  Pure alternation, no per-side mutation.
- [ ] **Test anchor:** `every write(1 | 2 | 3)` programs.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `sm_lower.c`.
- [ ] **Gate:** standard set.
- [ ] Doc: `docs/CHUNKS-icon-bb-alternate-validation.md`.

**Probes:**
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect   "A5" "AST_ALTERNATE" "<anchor>"
bb_probe_complete "A5" "AST_ALTERNATE" "<anchor>"
bb_probe_scoreboard
```


#### A6 — CH-17i-seqexpr-gen — `AST_SEQ_EXPR` (generative variant; `;`-separated parens that produce sequences)
- [ ] **JCON model:** `ir_conjunction` (irgen.icn) — left-then-right with the right side's failure resuming the left.
- [ ] **Existing `bb_node_t` shape:** check for `icn_seq_expr_state_t`.  Identical to addition's structure (Proebsting §4.3) but discarding left's value.
- [ ] **Test anchor:** programs with parenthesized generator sequences.
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `sm_lower.c`.
- [ ] **Gate:** standard set.
- [ ] Doc: `docs/CHUNKS-icon-bb-seqexpr-gen-validation.md`.

**Probes:**
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect   "A6" "AST_SEQ_EXPR" "<anchor>"
bb_probe_complete "A6" "AST_SEQ_EXPR" "<anchor>"
bb_probe_scoreboard
```


#### A7 — CH-17i-fallthrough-delete — physically delete the legacy block
- [ ] **Scope.**  After A1-A6 land, the legacy fallthrough block at
      `sm_lower.c:1410-1418` has zero in-scope kinds left.  Delete it.
      Replace with a `default:` arm that calls
      `fprintf(stderr, "FATAL: sm_lower: unhandled AST kind %d (%s) — add to GOAL-ICON-BB-COMPLETE.md\\n", e->kind, ast_kind_name(e->kind)); abort();`
      so future generative AST kinds trip a build/runtime error
      instead of silently falling through.
- [ ] **Gate:** standard set + audit script across full Icon corpus
      reports zero `SM_PUSH_EXPR` fires for any program (extends
      the CH-17i-every/suspend audits).
- [ ] Doc: `docs/CHUNKS-icon-bb-fallthrough-delete-validation.md`.

**Detection probe** (A7 needed iff *any* program still fires SM_PUSH_EXPR):
```bash
fail=0
for f in test/icon/rung*.icn; do
    fires=$(SCRIP_EXPRS_AUDIT=1 ./scrip --sm-run "$f" 2>&1 | grep -c 'SM_PUSH_EXPR fired')
    [ "$fires" -gt 0 ] && fail=1 && echo "A7 needed: $(basename $f .icn) has $fires fires"
done
[ $fail -eq 0 ] && echo "A7 already closed (corpus clean)" && exit 1 || exit 0
```

**Completion probe** (closure witness — corpus + jit-run both clean):
```bash
fail=0
for f in test/icon/rung*.icn; do
    n=$(basename "$f" .icn)
    for mode in --sm-run --jit-run; do
        fires=$(SCRIP_EXPRS_AUDIT=1 ./scrip $mode "$f" 2>&1 | grep -c 'SM_PUSH_EXPR fired')
        [ "$fires" -gt 0 ] && { echo "A7 FAIL: $n $mode SM_PUSH_EXPR=$fires"; fail=1; }
    done
done
# Plus: confirm physical deletion — sm_lower.c must not contain `emit_push_expr` calls
grep -n 'emit_push_expr' src/runtime/x86/sm_lower.c | grep -v '^[0-9]*:static' && {
    echo "A7 FAIL: emit_push_expr still called in sm_lower.c"
    fail=1
}
# Plus: smoke set md5s unchanged
source scripts/icon_bb_probes.sh
bb_probe_scoreboard
exit $fail
```


### Phase B — generative reductions (kinds whose children may be generators)

These rungs do NOT touch the legacy fallthrough.  They extend the
SCALAR lowerings already in `sm_lower.c` to handle the case where
a child is a generator.  The pattern is JCON's `ir_binary` /
`ir_unary` "closure" parameter (irgen.icn:540-610): the scalar
operation becomes the closure that the outer generator-driver
calls on each pulled value.

In SM terms: when any child of an arithmetic / relational / concat
node is suspendable, the lowering becomes:

```
[lower child 0 as generator producing values via SM_SUSPEND_VALUE]
[lower child 1 as generator]
... 
SM_<scalar-op>             ; combines TOS-1 and TOS scalar values
SM_SUSPEND_VALUE           ; yield combined value
```

with goto-wired drivers around it that ask each child for the next
value when the current combination either fails (relops) or has
been delivered to the consumer.

### Probe pattern for Phase B/C — anchor-based

These rungs don't have a "fires-counter goes to zero" signal;
they have an "anchor program changes from FAIL→PASS" signal.  Add
a third helper to `scripts/icon_bb_probes.sh`:

```bash
# Detection: rung needed iff anchor under SCRIP_NO_AST_WALK either
#   aborts, or produces output != --ir-run.  (Plain --sm-run output
#   equality is NOT a sufficient detector — it may be passing via
#   the AST-walker fallback today.  That is the cheat this rung
#   eliminates.)
bb_probe_detect_anchor() {
    local rung="$1" anchor="$2"
    local ir h_out h_rc
    ir=$(./scrip --ir-run "${CORPUS}/${anchor}.icn" 2>&1)
    h_out=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "${CORPUS}/${anchor}.icn" 2>&1)
    h_rc=$?
    if [ "$h_rc" -ne 0 ] || [ "$ir" != "$h_out" ]; then
        echo "$rung needed: anchor $anchor cheats (rc=$h_rc) — output differs honest"
        return 0
    fi
    echo "$rung already closed: anchor $anchor honest"
    return 1
}

# Completion: anchor honest under SCRIP_NO_AST_WALK + scoreboard +
# smoke md5s clean.
bb_probe_complete_anchor() {
    local rung="$1" anchor="$2"
    local fail=0
    local ir h_out h_rc
    ir=$(./scrip --ir-run "${CORPUS}/${anchor}.icn" 2>&1)
    h_out=$(SCRIP_NO_AST_WALK=1 ./scrip --sm-run "${CORPUS}/${anchor}.icn" 2>&1)
    h_rc=$?
    if [ "$h_rc" -ne 0 ] || [ "$ir" != "$h_out" ]; then
        echo "$rung FAIL: anchor $anchor still cheats (rc=$h_rc)"
        diff <(echo "$ir") <(echo "$h_out") | head -5
        fail=1
    fi
    bb_probe_scoreboard || fail=1
    local s cur base
    for s in icon snobol4 snocone prolog raku rebus; do
        cur=$(bash scripts/test_smoke_${s}.sh 2>&1 | md5sum | awk '{print $1}')
        base=$(awk '{print $1}' baselines/icon-bb/smoke-${s}.md5)
        if [ "$cur" != "$base" ]; then
            echo "$rung FAIL: smoke-$s md5 diverged"
            fail=1
        fi
    done
    [ $fail -eq 0 ] && echo "$rung complete"
    return $fail
}
```

Each Phase B/C rung's probes are then:

```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "<rung-id>" "<anchor>"
bb_probe_complete_anchor "<rung-id>" "<anchor>"
```

Anchors named below are TBD pending a corpus survey — once a
representative `test/icon/*.icn` program is identified that
exercises the rung's exact pattern, fill it in.  The pattern of
the program matters more than its name; recommended shape is the
minimal repro from the JCON test corpus or hand-written.


#### B1 — CH-17i-arith-gen — `AST_ADD`/`SUB`/`MUL`/`DIV`/`MOD`/`MNS`/`PLS`/`POW` with generator children
- [ ] **JCON model:** `ir_binary` (irgen.icn) — Proebsting §4.3 directly.
- [ ] **Test anchor:** `every write((1 to 3) + (1 to 2))` — 6 outputs.
- [ ] Files: `sm_lower.c` (extend existing scalar arms with generator-child branch).
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-arith-gen-validation.md`.

**Probes** (anchor: minimal `every write((1 to 3) + (1 to 2))` program):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "B1" "<anchor>"
bb_probe_complete_anchor "B1" "<anchor>"
```


#### B2 — CH-17i-rel-gen — `AST_LT`/`LE`/`GT`/`GE`/`EQ`/`NE` + string variants with generator children
- [ ] **JCON model:** Proebsting §4.3 LessThan template — on cmp fail, resume the right child (goal-directed retry).
- [ ] **Test anchor:** `2 < (1 to 4)` — generates 3, 4 then fails.
- [ ] Files: `sm_lower.c` (extend existing scalar relop arms).
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-rel-gen-validation.md`.

**Probes** (anchor: minimal `every write(2 < (1 to 4))` program):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "B2" "<anchor>"
bb_probe_complete_anchor "B2" "<anchor>"
```


#### B3 — CH-17i-cat-gen — `AST_CAT` + `AST_LCONCAT` with generator children (any position)
- [ ] **JCON model:** `ir_binary` for `||` and `|||`.
- [ ] **Test anchor:** `every write("v=" || (1 to 3))` — 3 outputs.
- [ ] Files: `sm_lower.c` (extend existing scalar concat arms).  AST_LCONCAT scalar gen is A1; this is the multi-child / mixed-position case.
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-cat-gen-validation.md`.

**Probes** (anchor: minimal `every write("v=" || (1 to 3))` program):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "B3" "<anchor>"
bb_probe_complete_anchor "B3" "<anchor>"
```


#### B4 — CH-17i-deref-gen — `AST_NONNULL` (`\E`) + `AST_NULL` (`/E`) + `AST_IDENTICAL` (`===`) with generator children
- [ ] **JCON model:** `ir_unary` for `\` and `/`; `ir_binary` for `===`.
- [ ] **Test anchor:** `every write(\(1 | &null | 3))` — 1, 3.
- [ ] Files: `sm_lower.c`.
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-deref-gen-validation.md`.

**Probes** (anchor: minimal `every write(\(1 | &null | 3))` program):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "B4" "<anchor>"
bb_probe_complete_anchor "B4" "<anchor>"
```


#### B5 — CH-17i-idx-gen — `AST_IDX` with generator index children
- [ ] **JCON model:** `ir_a_Field` for `.` access; `ir` recursion for `[]` with generator index.
- [ ] **Test anchor:** `every write(s[1 to 3])` — 3 outputs.
- [ ] Files: `sm_lower.c` (extend existing AST_IDX arm).
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-idx-gen-validation.md`.

**Probes** (anchor: minimal `every write(s[1 to 3])` program):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "B5" "<anchor>"
bb_probe_complete_anchor "B5" "<anchor>"
```


#### B6 — CH-17i-assign-gen — `AST_ASSIGN` with generator RHS, `AST_REVASSIGN`, `AST_REVSWAP` (always generative)
- [ ] **JCON model:** `ir_a_Binop` for `:=`, special ports for `<-` / `<->` (rev-assign / rev-swap, which set up an undo via the trail).
- [ ] **Test anchor:** `every x := (1 to 3); write(x)` — 1, 2, 3.  `every x[3] <- 19` — leaves x[3] at prior value after every loop completes.
- [ ] Files: `sm_lower.c` (extend AST_ASSIGN arm; new arms for AST_REVASSIGN / AST_REVSWAP if not already present).
- [ ] **Gate:** standard set + named anchors.  Trail behavior verified in rev-variants.
- [ ] Doc: `docs/CHUNKS-icon-bb-assign-gen-validation.md`.

**Probes** (anchor: rev-assign / rev-swap with trail-undo behavior):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "B6" "<anchor>"
bb_probe_complete_anchor "B6" "<anchor>"
```


### Phase C — control-flow that must stay generator-aware

#### C1 — CH-17i-fnc-gen — `AST_FNC` with generator arg + user proc returning generator
- [ ] **Scope.**  This is the heaviest rung but most of the
      machinery already exists: `proc_table[i].entry_pc` is wired,
      `sm_call_proc` exists (`coro_runtime.c:561`), `proc_table_call`
      (line 588) routes the call.  What's missing: the *caller's*
      lowering of `AST_FNC` to drive the proc-as-generator (rather
      than calling it once and discarding subsequent yields).
- [ ] **JCON model:** `ir_a_Call` (irgen.icn).
- [ ] **Test anchor:** `every write(seq())` where `seq` is a user
      proc with `suspend i`.  Many programs in the corpus.
- [ ] Files: `sm_lower.c` (AST_FNC arm — branch on generator
      context vs scalar context), possibly `sm_interp.c` for a new
      `SM_CALL_PROC_GEN` opcode.
- [ ] **Gate:** standard set + corpus probe (every program using
      `every write(user_proc())`).
- [ ] Doc: `docs/CHUNKS-icon-bb-fnc-gen-validation.md`.

**Probes** (anchor: user proc with `suspend i` driven by `every write(seq())`):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "C1" "<anchor>"
bb_probe_complete_anchor "C1" "<anchor>"
```


#### C2 — CH-17i-loop-cond-gen — `AST_WHILE` / `AST_UNTIL` / `AST_REPEAT` with generator condition
- [ ] **Scope.**  When the condition expression is a generator,
      the loop pulls one value per iteration; failure of the
      generator terminates the loop.  Today's lowering treats
      conditions as scalar.
- [ ] **JCON model:** `ir_a_While` / `ir_a_Until` / `ir_a_Repeat`.
- [ ] **Test anchor:** `while (i := find("x", s)) do ...` —
      `find` is a generator returning successive match positions.
- [ ] Files: `sm_lower.c` (AST_WHILE/UNTIL/REPEAT arms).
- [ ] **Gate:** standard set + named anchors.
- [ ] Doc: `docs/CHUNKS-icon-bb-loop-cond-gen-validation.md`.

**Probes** (anchor: while loop with generator condition):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "C2" "<anchor>"
bb_probe_complete_anchor "C2" "<anchor>"
```


#### C3 — CH-17i-if-gen — `AST_IF` with generator condition (Proebsting §4.5 directly)
- [ ] **Scope.**  When `if E1 then E2 else E3`'s `E1` is a
      generator, today's lowering evaluates `E1` once.  Spec
      (Proebsting §4.5) says: evaluate `E1` exactly once for
      success/fail decision; the `if` itself generates `E2`
      sequence (or `E3`) until failure.  Already correct in
      one4all if `AST_IF` arm doesn't drive `E1` repeatedly —
      verify, then fix if needed.
- [ ] **JCON model:** `ir_a_If` (irgen.icn).
- [ ] **Test anchor:** `every write(if 1 = 1 then (1 to 3) else 0)` — 1, 2, 3.
- [ ] Files: `sm_lower.c` (AST_IF arm).  Note: requires the
      indirect-goto / `gate` pattern Proebsting §4.5 describes,
      currently emitted via `SM_JUMP_F` + label tables.
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-if-gen-validation.md`.

**Probes** (anchor: minimal `every write(if 1=1 then (1 to 3) else 0)`):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "C3" "<anchor>"
bb_probe_complete_anchor "C3" "<anchor>"
```


#### C4 — CH-17i-not-gen — `AST_NOT` with generator subexpression
- [ ] **JCON model:** `ir_a_Not` (irgen.icn:142) — `expr.success → outer.failure; expr.failure → key &null + outer.success`.  The `&` resume side `bounded`: not retried on β.
- [ ] **Test anchor:** `every write(not (1 = 2 | 1 = 3))` — once with `&null`.
- [ ] Files: `sm_lower.c` (AST_NOT arm).
- [ ] **Gate:** standard set + named anchor.
- [ ] Doc: `docs/CHUNKS-icon-bb-not-gen-validation.md`.

**Probes** (anchor: minimal `every write(not (1=2 | 1=3))`):
```bash
source scripts/icon_bb_probes.sh
bb_probe_detect_anchor   "C4" "<anchor>"
bb_probe_complete_anchor "C4" "<anchor>"
```


### Phase D — driver alignment (CH-17g — owned by CHUNKS-STEP17)

This phase is **owned by `GOAL-CHUNKS-STEP17.md`** and listed here
for sequencing only.  The previous session attempted CH-17g-irrun-execution
ahead of Phase A and reverted.  After Phases A, B, C land, CH-17g
becomes safe because every kind reachable by `--ir-run` has a real
SM lowering.

| Rung (in CHUNKS-STEP17) | Status |
|-------------------------|--------|
| CH-17g-irrun-prep — `_usercall_hook` Icon-builtin dispatch | sequenced after Phase C |
| CH-17g-irrun-execution — route `--ir-run` non-SNO through `sm_preamble + sm_run_with_recovery` | sequenced after CH-17g-irrun-prep |

### Phase E — close the gate (owned by CHUNKS-STEP17)

| Rung (in CHUNKS-STEP17)        | This goal's contribution |
|--------------------------------|--------------------------|
| CH-17i-mode3-completeness      | trivially satisfied for Icon (Phases A-D made it so) |
| CH-17i-mode4-icon-prolog       | mode-4 codegen mirrors landed alongside each Phase A-C rung |
| CH-17i-final-isolation         | `is_suspendable` and `coro_eval` no longer needed for Icon |

---

## Open design question — unified opcode vs per-kind opcode

The 2026-05-10 audit (sess GOAL-CHUNKS-STEP17.md §CH-17g-irrun-execution)
proposed a **unified opcode** `SM_BB_PUMP_AST` + a single shared
`g_ast_pump_table`, replacing the per-kind opcode shape that
CH-17i-every used.  Rationale: 5+ rungs in Phase A all have
identical handler bodies modulo the table they index.

**This file's recommendation:** adopt the unified opcode for
Phase A (rungs A1–A6).  CH-17i-every's existing `SM_BB_PUMP_EVERY`
stays as-is (preserves its already-validated test coverage); the
unified opcode is for the kinds that haven't yet migrated.  If a
later cleanup wants to consolidate `SM_BB_PUMP_EVERY` onto the
unified shape, that's its own (small) rung.

**For Phase B and C** the question is different: those aren't
"BB pump" wrappers — they're scalar-op lowerings that need to
spawn generator-drive sub-chunks for their generative children.
The right primitive is `SM_SUSPEND_VALUE` (already exists) and
goto-wired chunks (already exist).  No new opcode needed; the
work is in `sm_lower.c` recognizing `is_suspendable(child)` and
emitting the goto-wired four-port template instead of the scalar
sequence.

If Phase B reveals a recurring pattern that wants its own opcode
(e.g. "generator-driven binary op"), file a sub-rung for it.
Otherwise, Phase B is pure `sm_lower.c` work.

---

## Per-rung gates (delta from CHUNKS standard set)

The standard CHUNKS gate set, applied per-rung:

```bash
cd /home/claude/one4all
bash scripts/build_scrip.sh                                 # clean build
bash scripts/test_smoke_icon.sh                             # PASS=5
bash scripts/test_smoke_snobol4.sh                          # PASS=7
bash scripts/test_smoke_snocone.sh                          # PASS=5
bash scripts/test_smoke_prolog.sh                           # PASS=5
bash scripts/test_smoke_raku.sh                             # PASS=5
bash scripts/test_smoke_rebus.sh                            # PASS=4
bash scripts/test_smoke_unified_broker.sh                   # PASS=49
bash scripts/test_isolation_ir_sm.sh                        # PASS
bash scripts/test_smoke_scrip_all_modes.sh                  # PASS=2
bash scripts/test_icon_ir_all_rungs.sh                      # 177/56/30 byte-identical
```

**Per-rung delta:** named test anchor flips FAIL→PASS under
`--sm-run` (and `--jit-run`), byte-identical to `--ir-run` output.

**Audit gate** (CH-17 series): set `SCRIP_EXPRS_AUDIT=1` and run
the full Icon corpus; the migrated kind's audit counter must
be zero (no `SM_PUSH_EXPR` fires for that kind on any program).

**Final-rung gate** (A7 — fallthrough delete): zero
`SM_PUSH_EXPR` fires across the entire Icon corpus, for every
program in `--ir-run` PASS, FAIL, and XFAIL buckets.  This
includes XFAIL programs because the audit measures the lowering
producer side, which runs regardless of whether the program
ultimately PASSes.

---

## File ownership

| Path                                          | This goal touches? |
|-----------------------------------------------|-------------------|
| `src/runtime/x86/sm_lower.c`                   | Yes (every rung)  |
| `src/runtime/x86/sm_prog.h`, `sm_prog.c`       | Yes (Phase A)     |
| `src/runtime/x86/sm_interp.h`, `sm_interp.c`   | Yes (Phase A)     |
| `src/runtime/x86/sm_codegen.c`                 | Yes (Phase A; JIT mirrors) |
| `src/runtime/interp/coro_runtime.c`            | Read-only ref     |
| `src/runtime/interp/coro_stmt.c`               | Read-only ref     |
| `src/ast/ast.h`                                | Read-only ref     |
| `tran/irgen.icn` (in jcon repo)                | Read-only ref (JCON gold) |
| `docs/CHUNKS-icon-bb-*-validation.md`          | Yes (per rung)    |

**No conflict** with parallel frontend sessions: this goal stays
within `src/runtime/x86/` and `src/ast/`, both of which are shared
files but no other goal touches them in the same way.  Coordinate
with CHUNKS-STEP17 (sibling).

---

## JCON reference — the gold

`/home/claude/jcon-extract/jcon-master/tran/irgen.icn` (when JCON
is checked out) — 1559 lines, 69 `ir_a_<Construct>` procedures,
one per Icon AST node.  Cary Coutant's executable proof that
"every Icon construct has a four-port template" is exactly that
many constructs and exactly that simple.

| AST kind in one4all       | JCON procedure (irgen.icn)        |
|---------------------------|-----------------------------------|
| AST_TO, AST_TO_BY         | (handled by ir_a_Binop with closure for `to`/`by`) |
| AST_LIMIT                 | `ir_a_Limitation` (line 113)      |
| AST_NOT                   | `ir_a_Not` (line 142)             |
| AST_ALTERNATE             | `ir_a_Alt` (search "ir_a_Alt")    |
| AST_CASE                  | `ir_a_Case`                       |
| AST_EVERY                 | `ir_a_Every`                      |
| AST_SECTION*              | `ir_a_Sectionop`                  |
| AST_FNC                   | `ir_a_Call`                       |
| AST_BINOP (arith/rel/cat) | `ir_a_Binop` → `ir_binary`        |
| AST_UNOP                  | `ir_a_Unop` → `ir_unary`          |
| AST_IF                    | `ir_a_If`                         |
| AST_RETURN                | `ir_a_Return`                     |
| AST_FAIL                  | `ir_a_Fail`                       |
| AST_SUSPEND               | `ir_a_Suspend`                    |
| AST_WHILE / UNTIL         | `ir_a_While` / `ir_a_Until`       |
| AST_REPEAT                | `ir_a_Repeat`                     |
| AST_SCAN                  | `ir_a_Scan`                       |
| AST_FIELD (`.field`)      | `ir_a_Field`                      |
| (all literals)            | `ir_a_Intlit` / `ir_a_Reallit` / `ir_a_Stringlit` / `ir_a_Csetlit` |

JCON's IR vocabulary (`tran/ir.icn`) is the four-port primitive
set in IR-record form:

```
ir_EnterInit       — start port (initial entry to the chunk)
ir_Goto            — direct goto (port wiring)
ir_IndirectGoto    — indirect goto via TmpLabel (Proebsting's "gate")
ir_Succeed         — succeed port (carries value + resumeLabel)
ir_Fail            — fail port
ir_ResumeValue     — resume port (with own failLabel for chaining)
ir_Create          — coexpression alloc (separate port set)
ir_CoRet / ir_CoFail — coexpression succeed/fail
ir_ScanSwap        — &subject/&pos save/restore (string scanning)
ir_chunk(label, insnList) — first-class chunk record
```

Proebsting's paper is the theory; JCON's `irgen.icn` is the
working implementation.  Both are in scope as primary references.

---

## Invariants (do not violate)

1. **Mode 1 byte-identical** at every rung.  `--ir-emit`'s
   stdout must match the pre-rung baseline.  This goal does not
   change IR-layer output.

2. **Icon `--ir-run` corpus 177/56/30 byte-identical** at every
   rung in this goal until CH-17g-irrun-execution lands.  Phases
   A/B/C touch only the SM lowering, not the AST walker.

3. **No `EXPR_t*` in SM bytecode.**  Every BB-pump opcode this goal
   adds takes an integer ID into a registry, never a raw pointer.
   This is the structural property that makes Mode 4 possible.

4. **Fallthrough delete is a one-way door.**  Once A7 lands, any
   future generative AST kind must add its own lowering; the
   `default:` arm aborts.  This is intentional — the closure
   property is preserved by the build itself.

5. **`is_suspendable` stays in sync.**  Whenever a kind is added
   to/removed from `is_suspendable` in `coro_runtime.c:657-702`,
   the corresponding lowering rung in this file must agree.  If
   `is_suspendable` says yes for kind K but `sm_lower` lowers K
   as scalar, programs that put a generator inside K will break
   silently.

---

## Closed rungs

### A3-seed-fix ✅ 2026-05-10 (sess Claude)

Unified the three independent `static unsigned long _rnd_seed = 12345UL`
LCG seeds (`coro_value.c::_rnd_seed`, `sm_interp.c::sm_rnd_seed`,
`interp_eval.c::_rnd_seed`) into one canonical
`unsigned long bb_icn_rnd_seed = 12345UL;` defined in `coro_value.c`
and externed via `coro_value.h`. All three sites now advance one
shared counter, so `--ir-run`, `--sm-run`, and the
SNOBOL4-evaluator AST_RANDOM fallback produce bit-identical
sequences for any program that exercises only one consumption path.

Files touched (5): `coro_value.h` (extern), `coro_value.c`
(definition + use site), `sm_interp.c` (include + use site),
`interp_eval.c` (include + use site). LCG algorithm and seed
value unchanged.

Honest mode-3 dial moved 116→117 (+1 PASS). The remaining
divergence in `rung36_jcon_random.icn` is no longer seed-driven;
it is caused by separate SM-mode gaps (`&lcase`/`&ucase` keyword
evaluation returns empty, `?L` for list-random raises
"Undefined function or operation"). Those gaps are out of scope
for this rung and belong to sibling SM-mode work.

Doc: `docs/CHUNKS-icon-bb-A3-seed-fix-validation.md`.

### A4 — CH-17i-alternate ✅ 2026-05-10 (sess Claude)

Migrated `AST_ALTERNATE` (`E1 | E2 | E3 | …`) off the SM default
`SM_PUSH_NULL` fallthrough onto a real lowering via `SM_BB_PUMP_AST`.
Same shape as A1's `AST_BANG_BINARY` and the A4-pulled-forward
`AST_ITERATE`: register the AST node in `g_ast_pump_table`, emit
`SM_BB_PUMP_AST` with the returned id; runtime drives
`coro_bb_alternate` (already implemented in `coro_runtime.c:1418`)
via `coro_eval` → `node.fn(node.ζ, α)` to pull the first value of
the alternation.

Pre-rung anchor `x := 1 | 2 | 3; write(x);` printed blank under
`--sm-run` (assigned `&null`); post-rung it prints `1` under all
three modes (ir-run, sm-run, honest sm-run). `every write(1|2|3)`
already worked pre-rung — `AST_EVERY`'s SM lowering takes a
different path; A4's contribution is the value-context use
(assignment, function arguments, etc.).

Files touched (1): `sm_lower.c` — added `case AST_ALTERNATE:`
arm immediately after `AST_ITERATE`.

Honest mode-3 dial moved 117→122 (+5 PASS). ir-run baseline
unchanged at 177/56/30. All smokes and unified_broker clean.

Doc: `docs/CHUNKS-icon-bb-alternate-validation.md`.

(Sessions that close further rungs append a paragraph here with
one4all hash, gates, and any honest deferrals.  Format mirrors
`GOAL-CHUNKS-STEP17.md`'s "Closed rungs" section.)

### CH-17g-smcall-proc ✅ 2026-05-11 (sess Claude Sonnet 4.6)

`SM_CALL_FN` for Icon user procs was dispatching through the SNOBOL4
NV-binding inline path (binding params into NV, jumping to body_pc).
But proc bodies lowered by CH-17b'' use `SM_LOAD_FRAME`/`SM_STORE_FRAME`
(frame-slot ABI) — params bound into NV were invisible to the body.
Fix: scan `proc_table` in `SM_CALL_FN` before DATA/NV dispatch; when
name matches a resolved `entry_pc`, call `sm_call_proc` directly.

Companion fix `CH-17g-smcall-proc-trampoline`: `proc_trampoline` was
calling `sm_call_proc(entry_pc)` unconditionally, but under `--ir-run`
the SM is freed after `sm_resolve_irrun_entry_pcs` — `g_current_sm_prog`
is NULL. Added the same guard as `proc_table_call` already had.

Files: `sm_interp.c` (`60656fce`), `coro_runtime.c` (`e0d7e4f5`).
ir-run: 177→186 (+9). Honest mode-3: 126→130 (+4).

### CH-17g-augop-inline ✅ 2026-05-11 (sess Claude Sonnet 4.6)

`AST_AUGOP` was lowered as `lower_expr(lhs) + lower_expr(rhs) + PUSH_LIT_I op
+ SM_CALL_FN AUGOP 3` — but `AUGOP` was not in `icn_try_call_builtin_by_name`
and even if it were, lhs was pushed as a value with no writeback slot.
Fix: for simple lhs (frame-slot or NV name), inline the read-compute-writeback:
`SM_LOAD_FRAME + [rhs] + SM_ADD/SUB/MUL/DIV/MOD/CONCAT + SM_STORE_FRAME`.
Complex/unsupported lhs still falls back to AUGOP call.

Files: `sm_lower.c` (`bb6d4ee7`). Honest mode-3: 130→140 (+10).

### CH-17g-loop-stack ✅ 2026-05-11 (sess Claude Sonnet 4.6)

`AST_WHILE` exits via `SM_JUMP_F` (condition FAILDESCR left on stack);
`AST_UNTIL` exits via `SM_JUMP_S` (condition result left on stack). Both
then emitted `SM_PUSH_NULL` without discarding the leftover condition value,
causing a stray value to accumulate and surface as extra output on the next
`write()`. Fix: emit `SM_VOID_POP` before `SM_PUSH_NULL` at both exit labels.

Files: `sm_lower.c` (`864fe914`). Honest mode-3: 140→143 (+3).

### CH-17g-scan ✅ 2026-05-11 (sess Claude Sonnet 4.6)

Three related Icon scanning fixes:
1. **AST_CSET**: default arm → `SM_PUSH_NULL`. Now `SM_PUSH_LIT_S(sval)` —
   cset chars as string, accepted by `any()`/`many()`/`upto()`.
2. **AST_SCAN** (Icon `?`): was using SNOBOL4 `lower_pat_expr` + `SM_EXEC_STMT`.
   Now: `[lower subject]` + `ICN_SCAN_PUSH` (saves context, sets
   `scan_subj`/`scan_pos=1`) + `SM_VOID_POP` + `[lower body]` + `ICN_SCAN_POP`
   (restores context, passes body result through).
3. **Scan builtins** added to `icn_try_call_builtin_by_name`: `ICN_SCAN_PUSH`,
   `ICN_SCAN_POP`, `any`, `many`, `upto`, `tab`, `move`, `match`, `find`.

Files: `sm_lower.c`, `interp_eval.c` (`d8760856`).
Honest mode-3: 143→152 (+9). ir-run: 186 unchanged.

**Next rung (A5 = seqexpr-gen / next gap):** Honest PASS=152/263. ABORT=1
(rung36_jcon_wordcnt segfault — pre-existing). Remaining 86 FAIL programs:
survey needed to identify next highest-yield gap category.

---

## Definitions

- **Closure property** — every Icon AST kind reachable by an
  `--ir-run` PASS program has a real SM lowering (not legacy
  fallthrough).  Stated as a single property because it's a
  single property; the previous CH-17i sub-rungs cover it
  piecewise without naming the closure.

- **Legacy fallthrough** — `sm_lower.c:1410-1418`, the catch-all
  block that emits `emit_push_expr + SM_BB_PUMP` for any AST kind
  not specifically handled.  This block is the gap.  This goal's
  A7 deletes it.

- **Generative reduction** — an AST kind that is normally scalar
  but becomes generative when one of its children is a generator.
  Phase B's territory.  `coro_runtime.c:is_suspendable` enumerates
  these (the recursive arms).

- **Goal-directed retry** — Proebsting's term for the relop
  pattern: when a comparison fails, the comparison's `resume`
  port asks the right operand for another value rather than
  failing the whole expression.  Phase B2's territory.

- **BB pump** — bb_broker(BB_PUMP, ...) drives a coroutine
  expression to its next yield.  In SM, the consumer-side opcode
  is `SM_BB_PUMP_<KIND>` for migrated kinds; legacy is
  `SM_BB_PUMP` (which pops an `EXPR_t*` off the SM value stack
  and walks the AST).
