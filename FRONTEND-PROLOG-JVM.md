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
| **Prolog JVM** | `main` PJ-13 — M-PJ-RECUR ✅ + M-PJ-BUILTINS ✅; rungs 01-09 PASS | `5197730` PJ-13 | M-PJ-CORPUS-R10 |

### CRITICAL NEXT ACTION (PJ-12)

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
| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus PASS | ❌ |

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
