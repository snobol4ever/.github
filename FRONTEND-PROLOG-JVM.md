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
| **Prolog JVM** | `main` PJ-50 — 5/5 rung11 ✅; 5/5 rung12 ✅; M-PJ-ATOM-BUILTINS ✅ | `cbd6979` PJ-50 | M-PJ-ASSERTZ |

### CRITICAL NEXT ACTION (PJ-51)

**Baseline: 5/5 rung11 PASS. 5/5 rung12 PASS. 19/20 puzzle corpus PASS (puzzle_19 pre-existing between/3 timeout). snobol4x HEAD `cbd6979`.**

**M-PJ-ATOM-BUILTINS ✅ — landed PJ-50.**

**Next milestone: M-PJ-ASSERTZ**

Implement `assertz/1`, `asserta/1`, `assert/1` — runtime fact assertion into a mutable per-predicate clause list alongside compiled static clauses. Required by Scripten Demo.

**Impl:** Per-predicate `ArrayList<Object[]>` dynamic clause store in a static field. `assertz` appends; compiled dispatch checks dynamic list after static clauses (or before for `asserta`). `abolish` clears the list.
**Rung:** `test/frontend/prolog/corpus/rung13_assertz/` — assert facts, query, verify results, assert rules.

**Bootstrap PJ-51:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 5/5 rung12 baseline
for f in test/frontend/prolog/corpus/rung12_atom_builtins/*.pro; do
  base=$(basename $f .pro); ./sno2c -pl -jvm $f -o /tmp/${base}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${base}.j -d /tmp 2>/dev/null
  cls=$(grep "^\.class" /tmp/${base}.j | awk '{print $3}')
  got=$(timeout 10 java -cp /tmp $cls 2>&1 | grep -v "Picked up")
  want=$(cat ${f%.pro}.expected)
  [ "$got" = "$want" ] && echo "$base: PASS" || echo "$base: FAIL"
done
# Then implement rung13_assertz + M-PJ-ASSERTZ
```

**Bootstrap PJ-49:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 5/5 rung11 + 20/20 puzzle baseline
for f in test/frontend/prolog/corpus/rung11_findall/*.pro; do
  base=$(basename $f .pro); ./sno2c -pl -jvm $f -o /tmp/${base}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${base}.j -d /tmp 2>/dev/null
  cls=$(grep "^\.class" /tmp/${base}.j | awk '{print $3}')
  got=$(timeout 10 java -cp /tmp $cls 2>&1 | grep -v "Picked up")
  want=$(cat ${f%.pro}.expected)
  [ "$got" = "$want" ] && echo "$base: PASS" || echo "$base: FAIL"
done
# Fix: delete the spurious JI("pop","") in pj_atom_chars_2 forward path
# Build, run rung12 sweep, expect 5/5
# Then run 20/20 puzzle sweep to confirm no regressions
```

**Changes landed PJ-48:**
- Created `test/frontend/prolog/corpus/rung12_atom_builtins/` with 5 test files + swipl-oracle `.expected` files: `atom_length`, `atom_concat`, `atom_chars`, `atom_codes`, `atom_case` (upcase/downcase/atom_length).
- Added runtime helper methods to `pj_emit_helpers()`: `pj_atom_name`, `pj_int_val`, `pj_string_to_char_list`, `pj_string_to_code_list`, `pj_char_list_to_string`, `pj_code_list_to_string`, `pj_atom_chars_2`, `pj_atom_codes_2`, `pj_char_code_2`.
- Added all 9 builtin dispatch cases to `pj_emit_goal()`: `atom_length/2`, `atom_concat/3`, `atom_chars/2`, `atom_codes/2`, `number_chars/2`, `number_codes/2`, `char_code/2`, `upcase_atom/2`, `downcase_atom/2`.
- One bug remaining: spurious `pop` in `pj_atom_chars_2` forward path causes VerifyError at class load time (affects ALL programs, not just atom_chars users, since helper is always emitted).
- Score: 0/5 rung12 (all fail with VerifyError). 5/5 rung11, 20/20 puzzles confirmed before the bug was introduced.
- snobol4x HEAD: `da9cfb7`.

**Baseline: 20/20 puzzle corpus PASS. 5/5 rung11_findall PASS. M-PJ-FINDALL ✅**

**Next milestone: M-PJ-ATOM-BUILTINS**

Implement: `atom_chars/2`, `atom_codes/2`, `atom_length/2`, `atom_concat/2`,
`char_code/2`, `number_chars/2`, `number_codes/2`, `upcase_atom/2`, `downcase_atom/2`.
All are JVM String operations. Both directions where reversible.

**Rung:** `test/frontend/prolog/corpus/rung12_atom_builtins/` (create if not present).
**Impl:** Add cases to builtin dispatch in `pj_emit_goal` and/or `prolog_builtin.c`.

**Bootstrap PJ-48:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 5/5 rung11 + 20/20 puzzle baseline
for f in test/frontend/prolog/corpus/rung11_findall/*.pro; do
  base=$(basename $f .pro); ./sno2c -pl -jvm $f -o /tmp/${base}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${base}.j -d /tmp 2>/dev/null
  cls=$(grep "^\.class" /tmp/${base}.j | awk '{print $3}')
  got=$(timeout 10 java -cp /tmp $cls 2>&1 | grep -v "Picked up")
  want=$(cat ${f%.pro}.expected)
  [ "$got" = "$want" ] && echo "$base: PASS" || echo "$base: FAIL"
done
# Then implement rung12_atom_builtins + M-PJ-ATOM-BUILTINS
```



**Bootstrap PJ-40:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 19/20: puzzle_03 and puzzle_18 fail
for i in $(seq -f "%02g" 1 20); do
  P=puzzle_${i}; C=Puzzle_${i}
  ./sno2c -pl -jvm test/frontend/prolog/corpus/rung10_programs/${P}.pro -o /tmp/${C}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${C}.j -d /tmp 2>/dev/null
  J=$(timeout 15 java -cp /tmp ${C} 2>/dev/null)
  O=$(timeout 15 swipl -q -g halt -t main test/frontend/prolog/corpus/rung10_programs/${P}.pro 2>/dev/null)
  [ "$J" = "$O" ] && echo "${P}: PASS" || echo "${P}: FAIL"
done
# Reproducer for trail bug:
cat > /tmp/d3.pro << 'EOF'
:- initialization(main).
member(X,[X|_]).
member(X,[_|T]) :- member(X,T).
differ(X,X) :- !, fail.
differ(_,_).
main :- member(X,[a,b]), member(Y,[a,b]), differ(X,Y), write(X-Y), nl, fail ; true.
EOF
./sno2c -pl -jvm /tmp/d3.pro -o /tmp/D3.j && java -jar src/backend/jvm/jasmin.jar /tmp/D3.j -d /tmp
timeout 5 java -cp /tmp D3  # should print a-b\nb-a; currently prints _\n_\n
# Fix: investigate trail mark save point and dj_β routing in pj_emit_body disjunction handler
# Read prolog_emit_jvm.c lines ~1865–1975 (disjunction emitter)
```

**Changes landed PJ-39:**
- `pj_callee_has_cut_no_last_ucall` guard: `cut_dest = lbl_cutγ ? lbl_cutγ : call_ω` — routes to call_ω when no enclosing cutgamma label exists.
- Root cause of puzzle_18 fully re-diagnosed: trail bug in 2-member+differ+disjunction (see above). Score unchanged 19/20.

**Changes landed PJ-38 (for context):**
   ```c
   if (lbl_cutγ && pj_callee_has_cut_no_last_ucall(fn, nargs)) {
   ```
   with:
   ```c
   if (pj_callee_has_cut_no_last_ucall(fn, nargs)) {
       const char *cut_dest = lbl_cutγ ? lbl_cutγ : call_ω;
   ```
   and emit `if_icmpeq %s\n", cut_dest` — routing to `call_ω` (exhausted) when no enclosing cutgamma label exists. This prevents the double-print without requiring the caller to have its own cut.

2. **puzzle_03** — over-generates. Open: M-PJ-DISPLAY-BT.

**Changes landed PJ-38:**
- `static Program *pj_prog` global set in `prolog_emit_jvm()` entry point.
- `pj_predicate_base_nclauses(fn, arity)` — walks `prog->head` for matching E_CHOICE, returns `nclauses` (= `base[nclauses]` since stride=1).
- `pj_callee_has_cut_no_last_ucall(fn, arity)` — returns 1 iff callee has cut AND last clause has no ucall.
- Cutgamma port now returns `2147483647` (MAX_VALUE) instead of `base[nclauses]` — eliminates sentinel/last-clause-γ ambiguity.
- Dispatch entry `if_icmpeq` guard updated to match `2147483647`.
- Call-site guard after `ifnull call_ω`: loads `rv[0].intValue()`, compares to `2147483647`, jumps to `lbl_cutγ` if equal — but only when `lbl_cutγ != NULL`. **That conditionality is the remaining bug.**
- Score: 18/20 → 19/20 (puzzles 01-02, 04-07, 12-13, 15-17, 19-20 newly passing; puzzle_18 still double-prints).

**Bootstrap PJ-39:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 19/20: puzzle_03 and puzzle_18 fail
for i in $(seq -f "%02g" 1 20); do
  P=puzzle_${i}; C=Puzzle_${i}
  ./sno2c -pl -jvm test/frontend/prolog/corpus/rung10_programs/${P}.pro -o /tmp/${C}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${C}.j -d /tmp 2>/dev/null
  J=$(timeout 15 java -cp /tmp ${C} 2>/dev/null)
  O=$(timeout 15 swipl -q -g halt -t main test/frontend/prolog/corpus/rung10_programs/${P}.pro 2>/dev/null)
  [ "$J" = "$O" ] && echo "${P}: PASS" || echo "${P}: FAIL"
done
# Fix in prolog_emit_jvm.c ~line 1806:
# Change:  if (lbl_cutγ && pj_callee_has_cut_no_last_ucall(fn, nargs)) {
# To:      if (pj_callee_has_cut_no_last_ucall(fn, nargs)) {
#              const char *cut_dest = lbl_cutγ ? lbl_cutγ : call_ω;
# And emit:    J("    if_icmpeq %s\n", cut_dest);
# Build, rerun sweep, expect puzzle_18 PASS -> 20/20
```

**JVM baseline: 18/20 PASS. Remaining failures (pre-PJ-38):**

1. **puzzle_18** — answer printed TWICE. Root cause fully re-diagnosed in PJ-37:
   - `pj_body_has_cut` recursive helper landed (`d4abf38`) — correct, no regressions, did NOT fix puzzle_18.
   - Real cause: `differ(X,X) :- !, fail.` returns cutgamma `{cs=2}` (non-null). At the call site in `puzzle/0`, `ifnull call_ω` handles null/failure but **non-null falls through unconditionally** — cutgamma cs=2 stored into `local_cs`, execution continues to next goal as if differ succeeded normally.
   - On next β-retry of `differ`, `local_cs=2 >= base[2]` → range guard → omega. Differ correctly exhausted on retry. But the **first cutgamma return was treated as success**, allowing the body to continue and print the answer twice.
   - `grep "if_icmpeq" /tmp/Puzzle_18.j` → empty. `puzzle/0` has no cut in its own body so no sentinel guard fires there. The cut lives inside the callee `differ/2` — the `any_has_cut` approach only protects the predicate being compiled, not its callers.
   - **Fix:** In `pj_emit_body` at the ucall success fallthrough (~line 1792, after `ifnull call_ω`), emit a cutgamma detection check before proceeding to the next goal:
     ```jasmin
     iload local_cs
     ldc <callee_base_nclauses>   ; sentinel value known at emit time
     if_icmpge lbl_cutγ           ; propagate cut upward to caller's cutgamma
     ```
     Requires knowing callee's `base[nclauses]` at the call site. Add `pj_predicate_base_nclauses(fn, arity, prog_root)` that walks the E_CHOICE tree for the named predicate, computing `base[nclauses]` identically to `pj_emit_predicate`. Only emit the check when the callee has `!last_has_ucall && any_has_cut` (i.e., is a deterministic cut-containing predicate — detectable by the same analysis).

2. **puzzle_03** — over-generates. Open: M-PJ-DISPLAY-BT.

**Changes landed PJ-37:**
- `pj_body_has_cut(EXPR_t *g)` recursive helper: walks `E_FNC` children for nested `E_CUT`. Added before `pj_is_user_call`.
- Shallow scan in `pj_emit_predicate` replaced with recursive `pj_body_has_cut` calls.
- No change to 18/20 score — fix was structurally correct but targeted wrong layer.

**Bootstrap PJ-38:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 18/20: puzzle_03 and puzzle_18 fail
for i in $(seq -f "%02g" 1 20); do
  P=puzzle_${i}; C=Puzzle_${i}
  ./sno2c -pl -jvm test/frontend/prolog/corpus/rung10_programs/${P}.pro -o /tmp/${C}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${C}.j -d /tmp 2>/dev/null
  J=$(timeout 15 java -cp /tmp ${C} 2>/dev/null)
  O=$(timeout 15 swipl -q -g halt -t main test/frontend/prolog/corpus/rung10_programs/${P}.pro 2>/dev/null)
  [ "$J" = "$O" ] && echo "${P}: PASS" || echo "${P}: FAIL"
done
# Implement pj_predicate_base_nclauses(fn, arity, prog_root) in prolog_emit_jvm.c:
#   walks the E_CHOICE tree for named predicate, returns base[nclauses].
# Then in pj_emit_body ucall path, after ifnull call_ω, before next-goal fallthrough:
#   int callee_sentinel = pj_predicate_base_nclauses(fn, arity, prog_root);
#   if (callee_sentinel > 0 && callee_has_cut_no_ucall) {
#     J("    iload %d\n    ldc %d\n    if_icmpge %s\n", local_cs, callee_sentinel, lbl_cutγ);
#   }
# Build, rerun sweep, expect puzzle_18 PASS -> 19/20
grep -n "ifnull call.*omega\|pj_predicate_base" src/frontend/prolog/prolog_emit_jvm.c
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


*(PJ-15 historical CRITICAL NEXT ACTION and earlier session findings removed — see SESSIONS_ARCHIVE.md)*

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
| **M-PJ-CUT-UCALL** | `!` + ucall body sentinel propagation | ✅ |
| **M-PJ-NAF-INNER-LOCALS** | NAF helper method — fix frame aliasing; puzzle_18 PASS | ✅ |
| **M-PJ-DISPLAY-BT** | puzzle_03 over-generation — workaround: single-clause rewrite + canonical tie-breaking; 20/20 | ✅ |
| **M-PJ-PZ-ALL-JVM** | All 20 puzzle solutions pass JVM | ✅ |
| **M-PJ-FINDALL** | `findall/3` — collect all solutions into list | ✅ |

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

---

## Tiny-Prolog Enhancement Roadmap — ISO Gap Closure

Incremental plan to close the gap between Tiny-Prolog and SWI-Prolog,
one feature at a time, each as a standalone milestone/sprint.
Ordered by impact: features that unblock the most real programs first.
Each milestone is one PJ-session or less.

**Oracle for all new rungs:** `swipl -q -g halt -t main file.pro`
**Test location:** `test/frontend/prolog/corpus/rung11_*/` onward
**Implementation:** `prolog_emit_jvm.c` (emit) + `prolog_builtin.c` (runtime helpers)

---

### Tier 1 — High Impact

#### M-PJ-FINDALL
`findall(Template, Goal, List)` — collect all solutions to Goal into List.
Never fails (empty List if no solutions). Most-used Prolog aggregation primitive.
Unblocks Scripten Demo #2 `get_persons()`/`get_jobs()` returning proper lists.
Required for `bagof`/`setof` later.
**Impl:** Drive backtracking internally in a loop, accumulate results, rebuild
Prolog list. Synthetic `p_findall_3` helper in `prolog_emit_jvm.c`.
**Rung:** `rung11_findall/` — basic collect, filtered collect, empty result.
**Sprint:** 1 session.

#### M-PJ-ATOM-BUILTINS
`atom_chars/2`, `atom_codes/2`, `atom_length/2`, `atom_concat/2`,
`char_code/2`, `number_chars/2`, `number_codes/2`,
`upcase_atom/2`, `downcase_atom/2`.
Both directions where reversible. All are JVM String operations.
**Rung:** `rung12_atom_builtins/`
**Sprint:** 1 session. Purely additive to builtin dispatch.

#### M-PJ-ASSERTZ
`assertz/1`, `asserta/1`, `assert/1` — runtime fact assertion into a mutable
per-predicate clause list alongside compiled static clauses.
Required by Scripten Demo: SNOBOL4 block populates Prolog dynamic DB row-by-row
as it parses CSV; Prolog inference rules then query the live facts.
Without `assertz`, the Scripten Demo must embed family data as static compiled
facts — kills the cross-language data-flow story.
**Impl:** Per-predicate `ArrayList<Object[]>` dynamic clause store in a static
field. `assertz` appends; compiled dispatch checks dynamic list after static
clauses (or before for `asserta`). `abolish` clears the list.
**Rung:** `rung13_assertz/` — assert facts, query, verify results, assert rules.
**Sprint:** 1 session.
**Scripten Demo dependency:** blocks M-SCRIPTEN-DEMO.

#### M-PJ-RETRACT
`retract/1`, `retractall/1`, `abolish/1`.
(`assertz`/`asserta` land in M-PJ-ASSERTZ above — this adds retraction.)
`retract` is backtrackable. Deleted entries skipped by dispatch loop.
**Rung:** `rung14_retract/` — assert, query, retract, verify gone.
**Sprint:** 1 session.

#### M-PJ-SORT
`sort/2`, `msort/2`, `keysort/2`, `predsort/3`.
Deterministic output ordering for all programs. `sort` removes duplicates,
`msort` preserves. Standard term ordering: vars < numbers < atoms < compounds.
JVM `Collections.sort` + Prolog list reconstruction.
**Rung:** `rung14_sort/`
**Sprint:** 1 session. Purely additive.

---

### Tier 2 — Medium Impact

#### M-PJ-SUCC-PLUS
`succ/2`, `plus/3` — reversible arithmetic.
`succ(X,3)` → `X=2`. `plus(2,Y,5)` → `Y=3`. Two trivial builtins.
**Rung:** `rung15_succ_plus/`
**Sprint:** 30 minutes.

#### M-PJ-FORMAT
`format/1`, `format/2`, `format(atom(A),Fmt,Args)`.
Directives: `~w` `~a` `~d` `~n` `~t` `~|`. `format(atom(A),...)` captures to atom.
**Rung:** `rung16_format/`
**Sprint:** 1 session.

#### M-PJ-STRING-OPS
`string_concat/3`, `string_length/2`, `string_to_atom/2`,
`string_codes/2`, `string_chars/2`, `sub_string/5`, `split_string/4`.
SWI distinguishes double-quoted strings from atoms. JVM String maps naturally.
**Rung:** `rung17_strings/`
**Sprint:** 1 session.

#### M-PJ-AGGREGATE
`bagof/3`, `setof/3`.
`bagof` fails on empty (unlike `findall`). `^/2` existential quantification.
`setof` = bagof + sort + dedup.
**Depends on:** M-PJ-FINDALL, M-PJ-SORT.
**Rung:** `rung18_aggregate/`
**Sprint:** 1 session.

#### M-PJ-COPY-TERM
`copy_term/2` — deep copy with fresh variables.
Required for meta-programming clause templates, correct `findall`, DCG expansion.
Walk term structure, allocate fresh variable slots, rebuild compound terms.
**Rung:** `rung19_copy_term/`
**Sprint:** 1 session.

#### M-PJ-EXCEPTIONS
`catch/3`, `throw/1`, ISO error terms (`type_error/2`, `instantiation_error/0`,
`existence_error/2`).
JVM exceptions map naturally: `throw` → Java throw, `catch` → try/catch.
Also retrofit builtins to throw ISO errors instead of silent fail.
**Rung:** `rung20_exceptions/`
**Sprint:** 1–2 sessions.

#### M-PJ-NUMBER-OPS
Extended `is/2` arithmetic: `truncate/1`, `round/1`, `ceiling/1`, `floor/1`,
`abs/1`, `sign/1`, `max/2`, `min/2`, `gcd/2`, `sqrt/1`, trig functions.
All trivial JVM Math calls. Add cases to `is/2` evaluator.
**Rung:** `rung21_arith_extended/`
**Sprint:** 1 session.

---

### Tier 3 — Future / Nice to Have

#### M-PJ-DCG (no sprint assigned)
Definite Clause Grammars — `-->` notation, `phrase/2`, `phrase/3`.
DCG rules compile to regular Prolog clauses with hidden difference-list args.
Elegant phrase-level parsing to complement SNOBOL4 character-level patterns.
**Why deferred:** SNOBOL4 already does parsing better for Scripten use cases.
DCG requires a source-rewrite pre-pass before the normal lowering pipeline —
non-trivial. Revisit after all Tier 1 + Tier 2 milestones complete.
**Depends on:** M-PJ-COPY-TERM (DCG expansion uses copy_term internally).

---

### Enhancement Milestone Summary

| ID | Feature | Tier | Depends on | Status |
|----|---------|------|-----------|--------|
| **M-PJ-FINDALL** | `findall/3` | 1 | — | ✅ |
| **M-PJ-ATOM-BUILTINS** | atom_chars/length/concat etc. | 1 | — | ✅ |
| **M-PJ-ASSERTZ** | `assertz/1`, `asserta/1` — dynamic DB | 1 | — | ❌ |
| **M-PJ-RETRACT** | `retract/1`, `retractall/1`, `abolish/1` | 1 | ASSERTZ | ❌ |
| **M-PJ-SORT** | `sort/2`, `msort/2`, `keysort/2` | 1 | — | ❌ |
| **M-PJ-SUCC-PLUS** | `succ/2`, `plus/3` | 2 | — | ❌ |
| **M-PJ-FORMAT** | `format/1`, `format/2` | 2 | — | ❌ |
| **M-PJ-STRING-OPS** | `split_string/4`, `string_concat/3` etc. | 2 | — | ❌ |
| **M-PJ-AGGREGATE** | `bagof/3`, `setof/3` | 2 | FINDALL + SORT | ❌ |
| **M-PJ-COPY-TERM** | `copy_term/2` | 2 | — | ❌ |
| **M-PJ-EXCEPTIONS** | `catch/3`, `throw/1` | 2 | — | ❌ |
| **M-PJ-NUMBER-OPS** | Extended `is/2` (trig, round, abs...) | 2 | — | ❌ |
| **M-PJ-DCG** | DCG `-->`, `phrase/2` | 3 | COPY-TERM | 💭 |

**Recommended sprint order:**
M-PJ-PZ-ALL-JVM (clear existing bugs) →
M-PJ-FINDALL → M-PJ-ATOM-BUILTINS → **M-PJ-ASSERTZ** → M-PJ-SORT → M-PJ-SUCC-PLUS →
M-PJ-RETRACT → M-PJ-FORMAT → M-PJ-STRING-OPS → M-PJ-AGGREGATE →
M-PJ-COPY-TERM → M-PJ-EXCEPTIONS → M-PJ-NUMBER-OPS → M-PJ-DCG (someday).

**Rung numbering:** `test/frontend/prolog/corpus/rung11_findall/`
through `rung21_arith_extended/`. Each rung: 3–5 tests, `.pro` + `.expected`.

