# GOAL-ICON-BB-JCON.md — Icon ir-run FAIL triage: missing builtins, BB fixes, new test sources

**Repo:** one4all + corpus + .github
**Carved:** 2026-05-12
**Prerequisite:** GOAL-ICON-BB-NATIVE ✅ (one4all `7efdf09a`)

---

## Objective

Fix the 39 ir-run FAILs left after GOAL-ICON-BB-NATIVE.  Each step targets one
cluster of related failures, adds a focused test source to corpus if none exists,
and leaves all gates green.  Steps are ordered by risk-to-reward ratio (easiest
fixes first, regressions last).

---

## Baseline (one4all `7efdf09a`, 2026-05-12)

  ir-run:  PASS=196  FAIL=39  XFAIL=30  TOTAL=265
  honest:  PASS=259  FAIL=1   ABORT=0

### 39 FAILs by cluster

| # | Cluster | Tests | Root cause |
|---|---------|-------|------------|
| A | **Alternate filter in every** | rung13_alt_alt_filter | `every (x := A|B) > N` — BB_EVAL skips filter in alternate; only 0 of 3 values printed |
| B | **Table key iteration** | rung23_table_table_key | `key(t)` generator yields wrong count (30 vs 60) |
| C | **Missing builtins — proc/image** | rung36_jcon_args, rung36_jcon_record, rung36_jcon_lists, rung36_jcon_fncs1 | `proc("op",arity)` lookup + `image()` builtin |
| D | **Missing builtins — math** | rung36_jcon_mathfunc | `sin/cos/tan/exp/log/sqrt` + `floor/ceil/iand/ior/ixor/ishift` |
| E | **Missing builtins — string** | rung36_jcon_endetab, rung36_jcon_prepro | `detab/entab/center/left/right` with width/fill args |
| F | **Augop for non-numeric / partial** | rung36_jcon_augment | `^:=` with integer base (power augop wrong result) |
| G | **Coerce / type conversion** | rung36_jcon_coerce, rung36_jcon_numeric | `+x / -x / *x` as coerce ops; `integer := abs` returns function not &null |
| H | **Lexicographic string comparison** | rung36_jcon_lexcmp | `s1 << s2` etc. comparators not returning correct boolean for all cases |
| I | **Radix literals** | rung36_jcon_radix | `"2r111...111"` (large binary literals) overflow to -1 instead of big int |
| J | **String builtins partial** | rung36_jcon_string, rung36_jcon_string1 | `repl/trim` edge cases; `===` / `~===` identical-op augops |
| K | **Scan alternation** | rung36_jcon_scan, rung36_jcon_scan1, rung36_jcon_scan2 | `(A|B) ? body` scan alternation resumes incorrectly |
| L | **&pos / &subject negative pos** | rung36_jcon_subjpos, rung36_jcon_substring | negative position values (-5..-1) in &pos / &subject |
| M | **Keywords table** | rung36_jcon_kwds | missing keyword values in &keywords table (partial output) |
| N | **Level / profsum / ck** | rung36_jcon_level, rung36_jcon_profsum, rung36_jcon_ck | FP precision + `level()` builtin + `&allocated` |
| O | **Segfaults / crashes** | rung36_jcon_htprep, rung36_jcon_meander, rung36_jcon_kross | seg fault in hash-table, meander, kross programs |
| P | **Queens / genqueen partial** | rung36_jcon_queens, rung36_jcon_genqueen | 6-queens partial output (mutual conjunction every A&B) |
| Q | **Parse / mindfa / mffsol** | rung36_jcon_parse, rung36_jcon_mindfa, rung36_jcon_mffsol | stdin-dependent programs (need .stdin fixture) or complex I/O |
| R | **Random / large** | rung36_jcon_random | `&random` seeding reproducibility |

---

## Session Setup

  cd /home/claude/one4all
  bash scripts/build_scrip.sh

**⚠️ BB IMPLEMENTATION RULE (mandatory, no exceptions):**
Every step that implements or modifies a BB (builtin, proc-as-value, indirect
call, image, etc.) MUST begin by reading `jcon_irgen.icn` (located in the
.github repo root, cloned to /home/claude/.github/jcon_irgen.icn).
Specifically read the `ir_a_Call` and `ir_a_Ident` procedures to understand
how JCON represents the construct you are implementing at the IR/BB level.
Do NOT infer semantics from C source alone — the irgen is the spec.

---

## Gate protocol — every step must pass ALL of these before commit

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5  never regress
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=22 never regress (post-PB-8)
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS must not decrease
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS=259 must not decrease

---

## Steps

### IJ-1 — Alternate filter in `every` (Cluster A) ✅ sess 2026-05-12 (`c5bb0775`)

**Root cause:** TT_SEQ (conjunction &) had no coro_eval case — fell through to oneshot
which eagerly called bb_eval_value(TT_SEQ); first child (x:=1)>2 failed for x=1,2 → FAILDESCR.
**Fix:** Added TT_SEQ generator case in coro_eval: when c[0] is suspendable, build
icn_every_state_t with gen=coro_eval(c[0]), body=c[1], reusing coro_bb_every semantics.
ir-run 196→197.

- [x] Read coro_bb_alternate + bb_eval_value TT_ALTERNATE case.
- [x] Identify where the filter failure fails to resume the alternate.
- [x] Fix: TT_SEQ as filter conjunction generator in coro_eval.
- [x] Test source: rung13_alt_alt_filter.icn already exists.
- [x] GATE-1..4. Commit.

### IJ-2 — Table key iteration (Cluster B) ✅ sess 2026-05-12 (`8529aec9`)

**Root cause:** TT_FNC in bb_eval_value lacked coro_drive_node injection check.
coro_bb_cat injected drive_node=key(t), drive_val=k each tick, but TT_FNC ignored it
and re-evaluated key(t) fresh — building a new key_iterate box starting from alpha
every time. So t[1]=10 was read on every tick; total accumulated 10+10+10=30 not 60.
**Fix:** Added injection check `if (coro_drive_node && e == coro_drive_node) return coro_drive_val`
at top of TT_FNC case in bb_eval_value. Same pattern as TT_TO, TT_ITERATE, TT_BANG_BINARY, etc.
ir-run 197→198.

- [x] Read icn_builtin key — coro_bb_tbl_key_iterate was correct.
- [x] Fix: TT_FNC injection check in bb_eval_value (coro_value.c).
- [x] Test source: rung23_table_table_key.icn already exists.
- [x] GATE-1..4. Commit.

### IJ-3 — `proc()` builtin + indirect invocation (Cluster C)

**Target:** rung36_jcon_args, rung36_jcon_record, rung36_jcon_fncs1, rung36_jcon_lists
**Root cause:** `proc("~===", 2)` — lookup procedure object by name/arity.
Also: list image builtin `image(L)` for list display.

**⚠️ MANDATORY BEFORE CODING:** Read `jcon_irgen.icn` (in .github repo root)
in full, especially `ir_a_Call` and `ir_a_Ident`, to understand how JCON
represents proc values and indirect calls at the BB/IR level.
Every step in IJ-3 that touches a BB (proc-as-value, indirect invocation,
image) MUST be grounded in what jcon_irgen.icn actually emits — not inferred
from C source alone. Previous Claude skipped this and had to backtrack.

**Partial progress (one4all `2e0ce555`):**
- ✅ `raku_fh_name[]` filename table — `image(fh)` → `file(foo.baz)`
- ✅ `image()` extended: `list(n)`, `record(typename)`, `procedure name`, both paths
- ✅ `proc(name,arity)` builtin implemented (returns `DT_E` for user procs)
- ✅ `args(proc_val)` builtin — returns nparams / -2 for varargs
- ✅ `icn_proc_as_value()` in `coro_value.c` — bare proc name TT_VAR → `DT_E`/`DT_S`
- ✅ Indirect callee dispatch in `bb_eval_value` + `interp_eval.c` TT_FNC
- ✅ `lower.c emit_var_load`: Icon proc names → `SM_PUSH_VAR` → DT_E (not LOAD_FRAME SNUL)
- ✅ `sm_interp.c SM_PUSH_VAR`: promotes Icon proc names to DT_E descriptor
- ✅ `sm_interp.c SM_CALL_FN`: dispatches DT_E from frame slots via `FRAME.sc`
- ✅ `coro_runtime.c sm_call_proc`: copies `lower_sc` into `FRAME.sc`
- ✅ `coro_bb_indirect_callee`: new BB generator box for `(!plist)()` — generative callee
- ✅ `coro_value.c` indirect callee: handles DT_I (`3()` → `3`), DT_SNUL, DT_S proc names
- ✅ `sm_interp.c SM_RETURN`: Icon fall-off-end returns `NULVCL` not `FAILDESCR`
- ✅ `pv := p0; write(image(pv))` → `"procedure p0"` ✓; `pv()` → calls p0 ✓
- ✅ `every (!plist)()` with mixed int+proc drives generator correctly

**Remaining open issue — next session:**
`every write((!plist)())` — the SM/BB seam. Root cause hypothesis:
`coro_bb_fnc` calls `icn_call_builtin(z->call, z->args, z->nargs)` for write,
but `icn_call_builtin` RE-EVALUATES args from tree_t children, ignoring the
pre-computed `z->args[gen_idx]` that contains the result from `coro_bb_indirect_callee`.
So write sees a fresh oneshot eval of `(!plist)()` (→ FAILDESCR) instead of the
DT_E/NULVCL from the indirect callee. Fix: ensure the generative arg value flows
to the builtin via `coro_drive_node`/`coro_drive_val` injection (same pattern
as `coro_bb_fnc` already uses for other builtins with generative args — check
how it injects the value into the call node's child before calling icn_call_builtin).

- [x] Read JCON `ir_a_Call` in jcon_irgen.icn for proc semantics.
- [ ] Wire indirect DT_E/DT_S invocation in TT_FNC dispatch (coro_value.c + interp_eval.c).
- [ ] Verify `image(x)` produces correct string for lists, records, procedures.
- [ ] Write test source `rung37_proc_lookup.icn` if no focused test exists.
      Expected: proc("write",1) succeeds; proc("noexist",1) fails;
      proc("~===",2) returns the ~=== operator procedure.
- [ ] GATE-1..4. Commit.

### IJ-4 — Math builtins: trig + integer bitwise (Cluster D)

**Target:** rung36_jcon_mathfunc
**Missing:** sin/cos/tan/atan/exp/log/sqrt (floating-point math),
            iand/ior/ixor/ishift/icom (integer bitwise ops).

- [ ] Read jcon_irgen.icn `ir_a_Call` for math builtins.
- [ ] Implement missing math builtins in icn_builtins.c (sin/cos/tan/atan/exp/log/sqrt).
- [ ] Implement integer bitwise builtins: iand/ior/ixor/ishift/icom.
- [ ] Write test source `rung37_math_builtins.icn`:
      write(sin(0.0)), write(cos(0.0)), write(iand(12,10)), write(ior(12,10)),
      write(ishift(1,3)), write(sqrt(4.0)).
      Expected: 0.0, 1.0, 8, 14, 8, 2.0.
- [ ] GATE-1..4. Commit.

### IJ-5 — String formatting builtins: center/left/right/detab/entab (Cluster E)

**Target:** rung36_jcon_endetab, rung36_jcon_prepro
**Missing:** center(s,n,fill), left(s,n,fill), right(s,n,fill), detab(s,...), entab(s,...).

- [ ] Read Icon book definitions for center/left/right/detab/entab.
- [ ] Implement in icn_builtins.c.
      center(s,n,c): pad s to width n centered with fill char c (default space).
      left(s,n,c): left-justify. right(s,n,c): right-justify.
      detab(s,t1,...): expand tabs to spaces at tab stops t1,... (default every 8).
      entab(s,t1,...): compress spaces to tabs.
- [ ] Write test source `rung37_string_format.icn`:
      write(center("hi",6)), write(left("hi",6,".")), write(right("hi",6,".")),
      write(detab("\tabc")), write(entab("        x")).
      Expected: "  hi  ", "hi....", "....hi", "        abc", "\tx".
- [ ] GATE-1..4. Commit.

### IJ-6 — Augop for power and remaining missing augops (Cluster F)

**Target:** rung36_jcon_augment  (i ^:= 9 should give 19^9, not a wrong value)
**Root cause:** `^:=` augop — the power augop may compute base^exp but store wrong value
or the wrong operand order.

- [ ] Run rung36_jcon_augment with --ir-run --dump-sm to isolate the wrong SM sequence.
- [ ] Fix lower_augop or SM_ACOMP for the `^` case.
- [ ] Write test source `rung37_augops.icn` with i := 2; i ^:= 3; write(i) → 8.
- [ ] GATE-1..4. Commit.

### IJ-7 — Type coercion operators `+x / -x / *x` (Cluster G)

**Target:** rung36_jcon_coerce, rung36_jcon_numeric
**Root cause:** Unary +, -, * as coerce operators (not arithmetic):
  +x coerces to numeric (integer or real),
  -x coerces to numeric and negates,
  *x coerces to integer (truncate real).
  Also: `integer := abs` should store the function object, not &null.

- [ ] Read coro_value.c / bb_eval_value for TT_PLS / TT_MNS / TT_MUL unary cases.
- [ ] Fix: unary + must coerce string to number (not just negate).
- [ ] Fix: `integer` as lvalue for a function assignment — verify function values
      are assignable to variables without being called.
- [ ] Write test source `rung37_coerce.icn`:
      write(+"3"), write(-"3"), write(*3.7), x := abs; write(x(-4)) → 3, -3, 3, 4.
- [ ] GATE-1..4. Commit.

### IJ-8 — Lexicographic string comparison operators (Cluster H)

**Target:** rung36_jcon_lexcmp  (`s1 << s2`, `s1 <<= s2`, `s1 == s2`, `s1 ~== s2`, `s1 >>= s2`, `s1 >> s2`)
**Root cause:** String comparison operators return wrong values for some inputs
(empty string comparisons, equal strings, etc.).

- [ ] Run rung36_jcon_lexcmp --ir-run and diff expected. Isolate first wrong line.
- [ ] Fix string comparison operators in icn_builtins / bb_eval_value.
- [ ] Write test source `rung37_str_relop.icn`:
      write("a" << "b"), write("b" << "a"), write("a" == "a"), write("a" ~== "b") → a, fail, a, a.
- [ ] GATE-1..4. Commit.

### IJ-9 — Scan alternation resume (Cluster K)

**Target:** rung36_jcon_scan, rung36_jcon_scan1, rung36_jcon_scan2
**Root cause:** `(A|B) ? body` — when body fails, scan must resume the subject
generator (A|B) to try the next subject. Currently partial output shows the
alternation is not resumed after body failure.

- [ ] Read bb_eval_value TT_SCAN + coro_bb_alternate interaction.
- [ ] Fix: scan with generative subject must retry scan on each successive subject value.
- [ ] Write test source `rung37_scan_alt.icn`:
      every write(("abc"|"def") ? find("bc")) → 2 (finds in "abc", fails in "def").
- [ ] GATE-1..4. Commit.

### IJ-10 — &pos / &subject negative positions (Cluster L)

**Target:** rung36_jcon_subjpos, rung36_jcon_substring
**Root cause:** Icon positions are 1-based with negative values meaning from end.
Position -1 = last+1, -2 = last, etc. Some operations with negative pos fail or
return wrong results.

- [ ] Audit icn_pos_normalize / scan position handling for negative values.
- [ ] Fix: negative &pos assignments and substring operations with negative bounds.
- [ ] Write test source `rung37_neg_pos.icn`:
      "abcde" ? (tab(-2); write(&pos)) → 4; write("abcde"[-2:0]) → "de".
- [ ] GATE-1..4. Commit.

### IJ-11 — Missing &keywords table entries (Cluster M)

**Target:** rung36_jcon_kwds  (partial keyword table output)
**Root cause:** Several Icon keywords (&allocated, &clock, &collections, &current,
&main, &progname, &source, &storage, &time, &version) not implemented or returning &null.

- [ ] Diff expected vs actual for rung36_jcon_kwds to enumerate missing keywords.
- [ ] Implement missing keywords (at minimum stubs returning appropriate types/values).
- [ ] Write test source `rung37_keywords.icn`: write(&ascii), write(&null), write(type(&main)).
- [ ] GATE-1..4. Commit.

### IJ-12 — Queens mutual conjunction `every A & B` (Cluster P)

**Target:** rung36_jcon_queens, rung36_jcon_genqueen
**Root cause:** `every A & B` requires BOTH A and B to generate in conjunction
(cross-product semantics). Currently queens only outputs 6-Queens header, meaning
the mutual conjunction fails to drive both generators.

- [ ] Read JCON ir_a_Mutual in jcon_irgen.icn for conjunction semantics.
- [ ] Fix: TT_MUTUAL in bb_eval_value / coro_runtime — both arms must succeed for
      conjunction to succeed; either failing causes resume of the other.
- [ ] Write test source `rung37_mutual.icn`:
      every write((1|2) & (3|4)) → 3, 4, 3, 4 (cross product).
- [ ] GATE-1..4. Commit.

### IJ-13 — Segfaults: htprep / meander / kross (Cluster O)

**Target:** rung36_jcon_htprep, rung36_jcon_meander, rung36_jcon_kross
**Root cause:** Unknown — these three segfault. Must triage before fixing.
NOTE: gdb hw watchpoints are broken in this container (see RULES.md).
Use __builtin_trap + ASAN or fprintf instrumentation.

- [ ] Run each under ASAN build: `CFLAGS="-fsanitize=address" bash scripts/build_scrip.sh`.
- [ ] Identify crash site from ASAN output.
- [ ] Fix crash(es). Each program gets its own commit if different root causes.
- [ ] GATE-1..4. Commit per distinct fix.

### IJ-14 — stdin-dependent programs: mindfa / mffsol (Cluster Q)

**Target:** rung36_jcon_mindfa, rung36_jcon_mffsol
**Root cause:** These programs read from stdin. They need `.stdin` fixture files
in corpus matching the expected output.

- [ ] Read each program source. Determine what stdin input produces the .expected output.
- [ ] Write corpus/programs/icon/rung36_jcon_mindfa.stdin and rung36_jcon_mffsol.stdin.
- [ ] Verify test_icon_ir_all_rungs.sh picks up .stdin (it already does — see run_one()).
- [ ] GATE-1..4. Commit (corpus commit only, no one4all change).

### IJ-15 — `parse` program: complex expression parsing (Cluster Q)

**Target:** rung36_jcon_parse
**Root cause:** parse.icn is a full expression parser in Icon. Partial output
(19683.0, 1, -2) shows complex evaluation succeeding but some paths wrong.

- [ ] Diff expected vs actual to isolate first divergence.
- [ ] Fix root cause (likely a scan or string or numeric issue exposed after IJ-5/7/8).
- [ ] GATE-1..4. Commit.

### IJ-16 — `&random` seeding and large integer literals (Clusters R, I)

**Target:** rung36_jcon_random, rung36_jcon_radix
**Root cause:** &random keyword assignment for reproducible sequences; and
large binary radix literals like "2r111...111" (64+ bits) overflowing to -1
instead of arbitrary precision (or at least correct 64-bit signed value).

- [ ] Fix &random keyword read/write for reproducible sequences.
- [ ] Fix radix literal parsing for values > INT64_MAX (clamp or error message).
- [ ] Write test source `rung37_random_radix.icn`:
      &random := 0; write(?10), write(?10) → reproducible pair.
      write(integer("8r77")) → 63.
- [ ] GATE-1..4. Commit.

### IJ-17 — Remaining partial-output programs: level / profsum / ck (Cluster N)

**Target:** rung36_jcon_level, rung36_jcon_profsum, rung36_jcon_ck
**Root cause:** Mixed — level() builtin, &allocated keyword (storage counter),
floating-point precision differences. Triage each.

- [ ] Diff each expected. level() needs a builtin returning call-stack depth.
- [ ] &allocated needs a keyword returning integer bytes allocated.
- [ ] FP precision: if platform difference, XFAIL with a note.
- [ ] GATE-1..4. Commit.

---

## New test sources summary (to add to corpus/programs/icon/)

Each step above adds one focused test. Naming convention: `rung37_<topic>.icn`
with matching `rung37_<topic>.expected`. Steps IJ-14 add `.stdin` fixtures.

| File | Step | Tests |
|------|------|-------|
| rung37_proc_lookup.icn | IJ-3 | proc() builtin |
| rung37_math_builtins.icn | IJ-4 | sin/cos/iand/ior/ishift/sqrt |
| rung37_string_format.icn | IJ-5 | center/left/right/detab/entab |
| rung37_augops.icn | IJ-6 | ^:= and other augops |
| rung37_coerce.icn | IJ-7 | unary +x / -x / *x coerce |
| rung37_str_relop.icn | IJ-8 | << <<= == ~== >>= >> |
| rung37_scan_alt.icn | IJ-9 | scan with alternate subject |
| rung37_neg_pos.icn | IJ-10 | negative &pos / substring |
| rung37_keywords.icn | IJ-11 | &keywords stubs |
| rung37_mutual.icn | IJ-12 | every A & B conjunction |
| rung37_random_radix.icn | IJ-16 | &random + radix literals |

---

## Done when

  ir-run PASS ≥ 230 (from 196; all 39 FAILs addressed — some may become XFAIL with note).
  Honest PASS ≥ 259 (must not decrease).
  All 17 rung37 test sources in corpus, all passing.
  GATE-1..4 green throughout.

---

## Invariants — ANY violation stops the session

1. GATE-1: smoke_icon PASS=5. Never regress.
2. GATE-2: smoke_broker PASS=22. Never regress.
3. GATE-3: ir-run PASS must not decrease between steps.
4. GATE-4: honest PASS must not decrease between steps.
5. One cluster per step. No bundling. Each step gets its own commit.
6. Every new test source has a matching .expected file committed alongside it.
7. No corpus source modified to work around a runtime bug (RULES.md).

---

## Watermark

  Carved:       2026-05-12 (Claude Sonnet 4.6)
  one4all HEAD: b36d7655
  ir-run:       PASS=199 FAIL=36 XFAIL=30 TOTAL=265
  Current step: IJ-3 (next: fix every-inside-builtin-arg BB; rung37_every_in_arg.icn
                isolates it — image(every 1|2|3) → &null instead of 1,2,3;
                coro_bb_fnc needs to treat TT_EVERY arg as a generator not a oneshot.
                Also closed: IJ-4 math builtins, IJ-5 detab/entab, TK_AUGPOW fix.)
