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
| **Prolog JVM** | `main` PJ-43 — **20/20** baseline confirmed; M-PJ-DISPLAY-BT root cause fully diagnosed (display/6 gamma cs re-enters gn chain on retry); minimal reproducer: chain_bug.pro 3 lines vs swipl 1 line | `38e4c39` PJ-43 | M-PJ-DISPLAY-BT: fix go/6 gamma cs pack — see CRITICAL NEXT ACTION (PJ-44) |

### CRITICAL NEXT ACTION (PJ-44)

**JVM baseline: 20/20 PASS. One remaining failure:**

1. **puzzle_03** — over-generates (M-PJ-DISPLAY-BT). **PJ-43:** root cause isolated — `display/6` gamma cs re-enters gn retry chain on external fail-loop. Minimal reproducer in Bootstrap PJ-44 below. Fix: inspect `p_go_6` gamma_0 cs pack.

**puzzle_18 is now FIXED (PJ-42).** Root cause was NAF frame aliasing — inner conjunction locals allocated at fixed offset `trail_local+1+n_vars+8` aliased outer clause locals. Fix: emit each `\+` inner goal into a synthetic `static naf_helper_N(...) Z` method with its own clean JVM frame. Helpers buffered in `pj_helper_buf` (tmpfile), flushed after each predicate's `.end method`. Committed at `38e4c39`.

   **Mechanism:** The `\+` emitter calls `pj_emit_goal` for the inner conjunction. The conjunction branch in `pj_emit_goal` (~line 1276) creates its own `int next_local_tmp = trail_local + 1 + n_vars + 8` — a LOCAL variable, NOT derived from `*next_local`. So inner ucall locals (for member/day_num/open calls inside the NAF) are allocated in a fixed frame region and `*next_local` is never advanced past them. When the NAF exits via `naf_ok` or `naf_fail`, the code can only zero locals in the `[naf_locals_start, naf_locals_end)` range — but since `*next_local` was not advanced, that range is empty. The inner `call20_beta … call25_beta` labels remain live in the outer frame. Outer retry chains can jump into them with stale cs values, causing the NAF conjunction to re-execute.

   **Fix (PJ-41):** In `pj_emit_goal`, conjunction branch (~line 1276), change `next_local_tmp` to use and update `*next_local` instead of a fixed offset:
   ```c
   // BEFORE (~line 1276):
   int next_local_tmp = trail_local + 1 + n_vars + 8;
   int ics = next_local_tmp++;
   int sco = next_local_tmp++;
   pj_emit_body(goal->children, nargs, lbl_γ, lbl_ω, lbl_ω,
                trail_local, var_locals, n_vars, &next_local_tmp, ics, sco, ...);

   // AFTER:
   int ics = (*next_local)++;
   int sco = (*next_local)++;
   JI("iconst_0", ""); J("    istore %d\n", ics);
   JI("iconst_0", ""); J("    istore %d\n", sco);
   pj_emit_body(goal->children, nargs, lbl_γ, lbl_ω, lbl_ω,
                trail_local, var_locals, n_vars, next_local, ics, sco, ...);
   ```
   Then in the NAF handler, `naf_locals_start`/`naf_locals_end` will bracket all inner locals and the zero loop will fire. **Run full 20-puzzle sweep immediately after — this conjunction path is hit everywhere.**

   **PJ-40 regression:** NAF calling `pj_emit_body` directly → 16/20 (lbl_outer_ω wiring wrong), reverted.

   **PJ-41 regression (NEW):** Conjunction fix (`*next_local` not local `next_local_tmp`) → puzzle_18 dropped to 0 lines. `*next_local` collided with used frame slots. Reverted. 19/20 preserved.

   **PJ-42 fix (NEXT):** Blunt zero-sweep at `naf_ok`/`naf_fail`: emit `iconst_0/istore N` for N in `[trail_local+1+n_vars+8 .. trail_local+1+n_vars+8+64)`. Zeros entire conjunction-local region unconditionally — safe (dead after NAF exits), no frame layout change.

   **Reproducer (minimal, still fails at 56850fd):**
   ```bash
   cat > /tmp/nafbug.pro << 'EOF'
   :- initialization(main).
   main :- puzzle ; true.
   member(X,[X|_]).
   member(X,[_|T]) :- member(X,T).
   differ(X,X) :- !, fail.
   differ(_,_).
   day_num(monday,1). day_num(tuesday,2). day_num(wednesday,3).
   open(shoe,monday). open(shoe,tuesday). open(bank,tuesday). open(bank,wednesday).
   next_day(monday,tuesday). next_day(tuesday,wednesday).
   prev_day(tuesday,monday). prev_day(wednesday,tuesday).
   store(S) :- member(S,[shoe,bank]).
   puzzle :-
       member(Today,[tuesday,wednesday]),
       store(SAb), store(SDe), differ(SAb,SDe),
       open(SAb,Today), open(SDe,Today),
       next_day(Today,Tomorrow), open(SDe,Tomorrow),
       prev_day(Today,Yesterday), open(SAb,Yesterday),
       \+ (member(D,[monday,tuesday,wednesday]),
           day_num(D,N), day_num(Today,NT), N < NT,
           open(SAb,D), open(SDe,D)),
       write(Today-SAb-SDe), nl, fail.
   EOF
   ./sno2c -pl -jvm /tmp/nafbug.pro -o /tmp/Nafbug.j
   java -jar src/backend/jvm/jasmin.jar /tmp/Nafbug.j -d /tmp
   timeout 5 java -cp /tmp Nafbug   # JVM prints extra lines; swipl prints correct subset
   ```

2. **puzzle_03** — over-generates. Open: M-PJ-DISPLAY-BT.

**Bootstrap PJ-44:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y --fix-missing default-jdk nasm libgc-dev swi-prolog
make -C snobol4x/src && cd snobol4x
# Confirm 20/20:
for i in $(seq -f "%02g" 1 20); do P=puzzle_${i}; C=Puzzle_${i}
  ./sno2c -pl -jvm test/frontend/prolog/corpus/rung10_programs/${P}.pro -o /tmp/${C}.j 2>/dev/null
  java -jar src/backend/jvm/jasmin.jar /tmp/${C}.j -d /tmp 2>/dev/null
  J=$(timeout 15 java -cp /tmp ${C} 2>/dev/null)
  O=$(timeout 15 swipl -q -g halt -t main test/frontend/prolog/corpus/rung10_programs/${P}.pro 2>/dev/null)
  [ "$J" = "$O" ] && echo "${P}: PASS" || echo "${P}: FAIL"
done
# Minimal reproducer (JVM=3 lines, swipl=1 line):
cat > /tmp/chain_bug.pro << 'EOF'
:- initialization(main).
gn(D,_,_,G,dorothy) :- G=:=D.
gn(_,J,_,G,jean)    :- G=:=J.
gn(_,_,V,G,virginia):- G=:=V.
go(D,J,V,GB,GJi,GT) :-
    gn(D,J,V,GB,N1), gn(D,J,V,GJi,N2), gn(D,J,V,GT,N3),
    write(N1-N2-N3), nl.
main :- go(2,1,3,3,2,1), fail ; write(done), nl.
EOF
./sno2c -pl -jvm /tmp/chain_bug.pro -o /tmp/ChainBug.j
java -jar src/backend/jvm/jasmin.jar /tmp/ChainBug.j -d /tmp
timeout 5 java -cp /tmp Chain_bug  # expect: 1 line + done
# Inspect gamma cs pack:
grep -n "p_go_6\|gamma_0\|iload 3\|ldc 0\|ldc 1" /tmp/ChainBug.j | head -40
# Hypothesis: gamma_0 cs = iload3 + ldc0 + iadd + iconst_1 + iadd
# where iload3 should be 0 (no inner retry) but encodes gn3 retry offset.
# Fix should be in pj_emit_gamma or the cs accumulation for deterministic body suffix.
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
| **M-PJ-CUT-UCALL** | `!` + ucall body sentinel propagation | ✅ |
| **M-PJ-NAF-INNER-LOCALS** | NAF helper method — fix frame aliasing; puzzle_18 PASS | ✅ |
| **M-PJ-PZ-ALL-JVM** | All 20 puzzle solutions pass JVM (puzzle_03 open) | ✅ |
| **M-PJ-DISPLAY-BT** | puzzle_03 over-generation — not_dorothy 2-clause retry | ❌ **NEXT** |

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

#### M-PJ-RETRACT
`retract/1`, `retractall/1`, `asserta/1`, `abolish/1`.
(We have `assertz` — this completes the dynamic DB set.)
`retract` is backtrackable. Requires mutable per-predicate clause list
alongside compiled static methods. Deleted entries skipped by dispatch loop.
**Rung:** `rung13_assert_retract/` — assert, query, retract, verify gone.
**Sprint:** 1–2 sessions.

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
| **M-PJ-FINDALL** | `findall/3` | 1 | — | ❌ |
| **M-PJ-ATOM-BUILTINS** | atom_chars/length/concat etc. | 1 | — | ❌ |
| **M-PJ-RETRACT** | `retract/1`, `retractall/1`, `asserta/1` | 1 | — | ❌ |
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
M-PJ-FINDALL → M-PJ-ATOM-BUILTINS → M-PJ-SORT → M-PJ-SUCC-PLUS →
M-PJ-RETRACT → M-PJ-FORMAT → M-PJ-STRING-OPS → M-PJ-AGGREGATE →
M-PJ-COPY-TERM → M-PJ-EXCEPTIONS → M-PJ-NUMBER-OPS → M-PJ-DCG (someday).

**Rung numbering:** `test/frontend/prolog/corpus/rung11_findall/`
through `rung21_arith_extended/`. Each rung: 3–5 tests, `.pro` + `.expected`.

