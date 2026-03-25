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
| **Prolog JVM** | `main` PJ-22 — M-PJ-STACK-LIMIT ✅ dynamic .limit stack; 9/9 rungs + 19/21 puzzles PASS | `cb0b4d0` PJ-22 | M-PJ-DISJ-ARITH |

### CRITICAL NEXT ACTION (PJ-23)

**Milestone: M-PJ-DISJ-ARITH — fix `(A;B;C)` inline disjunction silent failure in arithmetic body.**

Confirmed failing: puzzle_03 (silent output) and puzzle_11 (double-print).

**puzzle_03 root cause:** uses `differ6/6` with `=\=/2` (15 arithmetic inequalities) and `not_dorothy` with a 6-arm `( ; )` disjunction containing `->`. The `(;)` emitter in `pj_emit_goal` may misfire when arms contain `->` soft-cut. JVM emits but produces no output — the disjunction either always fails or short-circuits wrongly.

**puzzle_11 root cause:** double-print — solution found twice. `ages_ok` contains a `!` inside a body called from `puzzle`. The `!` seals β for `ages_ok` but the enclosing `puzzle` body continues to backtrack through `all_diff5`, re-binding the position variables and re-finding the same solution. Likely `cut_cs_seal` not propagating correctly across the `ages_ok` call boundary.

**Approach:** write a minimal reproducer for each, confirm swipl vs JVM divergence, then fix `pj_emit_goal` disjunction/cut wiring.

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
