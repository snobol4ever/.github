# FRONTEND-PROLOG-JVM.md — Prolog → JVM Backend (L3)

Prolog frontend targeting JVM bytecode via Jasmin.
Reuses the existing Prolog IR pipeline (lex → parse → lower) unchanged.
New layer: `prolog_emit_jvm.c` — consumes `E_CHOICE/E_CLAUSE/E_UNIFY/E_CUT/E_TRAIL_*`
and emits Jasmin `.j` files, assembled by `jasmin.jar`.

**Session trigger phrase:** `"I'm working on Prolog JVM"`
**Session prefix:** `PJ` (e.g. PJ-7, PJ-8, ...)`
**Driver flag:** `snobol4x -pl -jvm foo.pl → foo.j → java -jar jasmin.jar foo.j`
**Oracle:** `snobol4x -pl -asm foo.pl` (ASM emitter, rungs 1–9 known good)
**Design reference:** BACKEND-JVM-PROLOG.md (term encoding, runtime helpers, Jasmin patterns)

*Session state → this file §NOW. Backend reference → BACKEND-JVM-PROLOG.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | `main` PJ-34 — M-PJ-DISJ-ARITH ✅ plain disj retry loop; puzzle_12 PASS; 17/20 | `453d969` PJ-34 | M-PJ-CUT-UCALL (puzzle_11/18 double-output) |

### CRITICAL NEXT ACTION (PJ-35)

**JVM baseline: 17/20 PASS. Remaining failures:**

1. **puzzle_11, 18** — answer printed TWICE. Root cause fully diagnosed:
   - `!` fires inside a predicate (`ages_ok`) whose last clause has a body ucall.
   - Omega guard `if_icmpge omega` is **omitted** when `last_has_ucall=1` (PJ-16 design).
   - Without the guard, caller retries with cs=1, re-enters clause0, clamps `init_cs=1`, inner ucall resumes mid-stream → duplicate answer.
   - **Fix:** Add `p_NAME_ARITY_cutgamma_CI` label that returns `{base[nclauses]}` as cs. The `!` body path jumps to `cutgamma` instead of `gamma_CI`. Caller sees exhaustion sentinel on first retry → `call_omega` immediately.
   - In `prolog_emit_jvm.c` at `pj_emit_clause`: after each `gamma_CI` block, emit `cutgamma_CI` returning `base[nclauses]`. In `pj_emit_body`/`pj_emit_goal` cut branch: `goto cutgamma_CI` instead of `goto gamma_CI`.
   - New milestone: **M-PJ-CUT-UCALL**

2. **puzzle_03** — over-generates (56L vs 12L). `equal_sums`/`find_couples` multi-clause backtrack. Open: M-PJ-DISPLAY-BT.

**Changes landed PJ-34:**
- `prolog_emit_jvm.c`: plain `;` retry loop in `pj_emit_body` — tableswitch dispatch, `dj_alpha`/`dj_beta`/`dj_omega`, trail save/unwind per arm.
- `pj_count_disj_locals()` recursive — accounts for ucall locals inside disjunction arms. Fixes VerifyError regression on puzzle_16.
- puzzle_12 ✅ (was silent 0L). puzzle_16 regression fixed. 16→17/20.

**Bootstrap PJ-35:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm baseline: 17/20 PASS (puzzle_03, 11, 18 fail)
for i in $(seq -f "%02g" 1 20); do
  PUZZLE=puzzle_${i}; CLS=Puzzle_${i}
  ./sno2c -pl -jvm test/frontend/prolog/corpus/rung10_programs/${PUZZLE}.pro -o /tmp/${CLS}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${CLS}.j -d /tmp 2>/dev/null
  JVM=$(timeout 15 java -cp /tmp ${CLS} 2>/dev/null)
  ORACLE=$(timeout 15 swipl -q -g halt -t main test/frontend/prolog/corpus/rung10_programs/${PUZZLE}.pro 2>/dev/null)
  [ "$JVM" = "$ORACLE" ] && echo "${PUZZLE}: PASS" || echo "${PUZZLE}: FAIL"
done
# Then tackle M-PJ-CUT-UCALL:
# In prolog_emit_jvm.c, find pj_emit_clause gamma label emission (~line 2368)
# Add cutgamma_CI label returning base[nclauses] sentinel
# Wire cut path in pj_emit_body/pj_emit_goal to jump to cutgamma_CI
grep -n "gamma_\|cut_cs_seal\|ldc.*cut" src/frontend/prolog/prolog_emit_jvm.c | head -20
```

**Bootstrap PJ-23:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
# Confirm baseline: 9/9 rungs PASS, 19/21 rung10 PASS (03+11 still fail)
# Then: write minimal repro for (A;B;C) with -> arms, confirm swipl vs JVM
# Fix pj_emit_goal disjunction handling, re-run puzzle_03
```

**Bootstrap PJ-18:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
# Confirm baseline: rungs 01-09 + rung10 puzzles 01,02,04,05,06,14,16,17 JVM PASS
# Then rewrite puzzles 03,07,08,09,10,11,12,13,15,18,19,20 as proper search
# Test each: swipl first, then JVM
```

**Bootstrap PJ-17:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
# Confirm baseline: rungs 01-09 PASS
for rung in rung01_hello/hello rung02_facts/facts rung03_unify/unify rung04_arith/arith rung05_backtrack/backtrack rung06_lists/lists rung07_cut/cut rung08_recursion/recursion rung09_builtins/builtins; do
  base=$(basename $rung)
  cls=$(echo "$base" | python3 -c "import sys; s=sys.stdin.read().strip(); print(s[0].upper()+s[1:])")
  ./sno2c -pl -jvm test/frontend/prolog/corpus/$rung.pro -o /tmp/${cls}.j
  java -jar src/backend/jvm/jasmin.jar /tmp/${cls}.j -d /tmp 2>/dev/null
  result=$(timeout 5 java -cp /tmp $cls 2>/dev/null)
  expected=$(cat test/frontend/prolog/corpus/$rung.expected)
  [ "$result" = "$expected" ] && echo "$rung: PASS" || echo "$rung: FAIL"
done
# Run rung10 puzzles vs swipl oracle:
for f in puzzle_01 puzzle_02 puzzle_05 puzzle_06; do
  cls=$(echo "$f" | python3 -c "import sys; s=sys.stdin.read().strip(); print(s[0].upper()+s[1:])")
  ./sno2c -pl -jvm test/frontend/prolog/corpus/rung10_programs/${f}.pro -o /tmp/${cls}.j
  java -jar src/backend/jvm/jasmin.jar /tmp/${cls}.j -d /tmp 2>/dev/null
  jvm=$(timeout 10 java -cp /tmp $cls 2>/dev/null)
  oracle=$(timeout 10 swipl -q -g halt -t main test/frontend/prolog/corpus/rung10_programs/${f}.pro 2>/dev/null)
  [ "$jvm" = "$oracle" ] && echo "$f: PASS" || echo "$f: FAIL"
done
# Then tackle remaining stub puzzles starting with M-PZ-14 (easiest per FRONTEND-PROLOG.md)
```

### CRITICAL NEXT ACTION (PJ-15)

**Bug: nested user calls — inner call exhaustion wires to predicate ω instead of enclosing call β.**

Reproducer (`/tmp/minimal2.pro`):
```prolog
:- initialization(main). main :- test ; true.
item(a). item(b).
differ(X, X) :- !, fail.
differ(_, _).
test :- item(X), item(Y), differ(X, Y), write(X), write('-'), write(Y), write('\n'), fail.
```
Expected (swipl): `a-b\nb-a`. JVM: silent (no output, exits 0).

**Root cause:** In `pj_emit_body` line ~1665:
```c
J("%s:\n", call_ω);
JI("goto", lbl_outer_ω);   /* BUG: should retry enclosing call */
```
When `differ` (call7) is exhausted, `call7_omega → lbl_outer_omega → p_test_0_omega` (predicate fail). It should instead go to `call6_beta` (retry `item(Y)`). The correct wire is `call7_omega → call6_beta`.

`lbl_outer_ω` is the *predicate's* omega (skip to next clause). `lbl_ω` at the point of call7 emission is `call6_beta`. So the fix seems to be `goto lbl_ω` instead of `goto lbl_outer_ω`. **But:** changing to `lbl_ω` caused an infinite loop in PJ-14 testing — `call7_beta` retried `differ` which always fails (no more solutions), so it looped back to `call6_beta` without decrementing the cs. The cs for `differ` was stuck and `item(Y)` kept binding to `b` while `differ(b,b)` kept failing → `call6_beta` → `item(Y)` again → same binding → infinite loop.

**The actual fix needed:** When `call7_omega` fires (differ exhausted for the current X,Y binding), we need to advance `item(Y)`'s cs (retry item(Y) for a new Y), not retry `differ` with the same Y. This means `call7_omega` should reset `local_cs_7 = 0` (fresh differ) AND then goto `call6_beta` (which unwinds and retries item(Y)). The `local_cs` for `differ` must be reset to 0 before the beta jump, otherwise the next call to `differ` starts from an exhausted state.

**Bootstrap PJ-15:**
```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src
# Confirm baseline: rungs 01-09 PASS (see bootstrap in §NOW above)
# Then: test minimal2
cat > /tmp/minimal2.pro << 'EOF'
:- initialization(main). main :- test ; true.
item(a). item(b).
differ(X, X) :- !, fail.
differ(_, _).
test :- item(X), item(Y), differ(X, Y), write(X), write('-'), write(Y), write('\n'), fail.
EOF
./sno2c -pl -jvm /tmp/minimal2.pro -o /tmp/Minimal2.j
java -jar src/backend/jvm/jasmin.jar /tmp/Minimal2.j -d /tmp
timeout 3 java -cp /tmp Minimal2  # should print a-b\nb-a
# Fix: prolog_emit_jvm.c pj_emit_body, the call_ω label emission (~line 1665)
# Approach: on call_omega, reset local_cs to 0, then goto lbl_ω (enclosing beta)
```

**Rung 08 `recursion`: `fibonacci/2`, `factorial/2`.**

**Bootstrap PJ-13:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Confirm baseline: rungs 01-07 PASS
for rung in rung01_hello/hello rung02_facts/facts rung03_unify/unify rung04_arith/arith rung05_backtrack/backtrack rung06_lists/lists rung07_cut/cut; do
  base=$(basename $rung); cls=$(echo $base | sed 's/./\u&/')
  ./sno2c -pl -jvm test/frontend/prolog/corpus/$rung.pro -o /tmp/${cls}.j
  java -jar src/backend/jvm/jasmin.jar /tmp/${cls}.j -d /tmp 2>/dev/null
  result=$(timeout 5 java -cp /tmp $cls 2>/dev/null)
  expected=$(cat test/frontend/prolog/corpus/$rung.expected)
  [ "$result" = "$expected" ] && echo "$rung: PASS" || echo "$rung: FAIL"
done
# Then tackle rung08:
cat test/frontend/prolog/corpus/rung08_recursion/recursion.pro
./sno2c -pl -jvm test/frontend/prolog/corpus/rung08_recursion/recursion.pro -o /tmp/Recursion.j
java -jar src/backend/jvm/jasmin.jar /tmp/Recursion.j -d /tmp && timeout 5 java -cp /tmp Recursion
```

**PJ-12 fix summary (for context):**
Cut (`!`) in `pj_emit_body` now: (1) stores `base[nclauses]` into `cs_local` (seals β so next dispatch → omega), (2) continues emitting remaining body goals with `lbl_ω = lbl_pred_ω` (predicate omega, skipping all clauses). Three parameters added to `pj_emit_body`: `cut_cs_seal`, `cs_local_for_cut`, `lbl_pred_ω`. The `pj_emit_goal` cut branch does the same seal + `goto lbl_γ`.

---

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ |
| **M-PJ-LISTS** | Rung 6: `append/3`, `length/2`, `reverse/2` | ✅ |
| **M-PJ-CUT** | Rung 7: `differ/N`, closed-world `!, fail` | ✅ |
| **M-PJ-RECUR** | Rung 8: `fibonacci/2`, `factorial/2` | ✅ |
| **M-PJ-BUILTINS** | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | ✅ |
| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus PASS | ✅ |
| **M-PJ-PZ08** | puzzle_08 real Prolog search — swipl PASS | ✅ |
| **M-PJ-PZ09** | puzzle_09 real Prolog search — swipl PASS | ✅ |
| **M-PJ-PZ10** | puzzle_10 real Prolog search — swipl PASS | ✅ |
| **M-PJ-PZ11** | puzzle_11 real Prolog search — swipl PASS | ✅ |
| **M-PJ-NEQ** | `\=/2` emit missing in `pj_emit_goal` — JVM crashes with NoSuchMethodError | ✅ |
| **M-PJ-STACK-LIMIT** | Dynamic `.limit stack` via term depth walker — fixes VerifyError on deep compound terms | ✅ |
| **M-PJ-NAF-TRAIL** | `\+` trail: save mark before inner goal, unwind both paths — multi-arg user calls in `\+` | ✅ |
| **M-PJ-BODYFAIL-TRAIL** | Body-fail trail unwind: `bodyfail_N` trampoline per clause — head bindings now undone on body failure | ✅ |
| **M-PJ-BETWEEN** | `between/3` — synthetic p_between_3 method; cs encodes Low+offset | ✅ |
| **M-PJ-DISJ-ARITH** | Plain `;` retry loop in `pj_emit_body` — tableswitch dispatch, dj_alpha/beta/omega; puzzle_12 PASS | ✅ |
| **M-PJ-DISPLAY-BT** | puzzle_03 display/6 over-generation — `not_dorothy` 2-clause retry; ITE cut or source fix | ❌ |
| **M-PJ-CUT-UCALL** | `!` + ucall body: cut-gamma returns `base[nclauses]` sentinel — fixes puzzle_11/18 double-output | ❌ **NEXT** |
| **M-PJ-PZ-ALL-JVM** | All 20 puzzle solutions pass JVM — requires M-PJ-CUT-UCALL + M-PJ-DISPLAY-BT | ❌ |

**PJ-16 fix note:** True root cause of the `fail/retry` infinite loop was `pj_emit_clause` passing `α_retry_lbl` as `lbl_ω` to `pj_emit_body`. When the outermost body user-call exhausted, `call_ω` jumped to `α_retry_lbl` (clause head-retry), re-running the body from cs=0 forever. Fix: pass `ω_lbl` (next-clause dispatch) as `lbl_ω` to the top-level `pj_emit_body` call. Nested calls unaffected — they receive `call_β` from their own recursive emit site. `pj_is_always_fail()` helper also added for future use.

---

## Session Bootstrap (every PJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read §NOW above. Start at CRITICAL NEXT ACTION.
```

---

*FRONTEND-PROLOG-JVM.md = L3. ~3KB sprint content max. Archive ✅ milestones to MILESTONE_ARCHIVE.md on session end.*
