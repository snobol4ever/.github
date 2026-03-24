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
| **Prolog JVM** | `main` PJ-11 — M-PJ-LISTS ✅ rungs 01-06 PASS; clamp init_cs fix | `e3c30ab` PJ-11 | M-PJ-CUT |

### CRITICAL NEXT ACTION (PJ-12)

**Rung 07 `cut`: `differ/N`, closed-world `!, fail` pattern.**

**Bootstrap PJ-12:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Confirm baseline: rungs 01-06 PASS
for rung in rung01_hello/hello rung02_facts/facts rung03_unify/unify rung04_arith/arith rung05_backtrack/backtrack rung06_lists/lists; do
  base=$(basename $rung)
  ./sno2c -pl -jvm test/frontend/prolog/corpus/$rung.pro -o /tmp/${base}.j
  java -jar src/backend/jvm/jasmin.jar /tmp/${base}.j -d /tmp 2>/dev/null
  cls=$(ls /tmp/*.class | grep -i "$base" | head -1 | sed 's|.*/||;s|\.class||')
  echo -n "$rung: "; diff <(java -cp /tmp $cls 2>/dev/null | grep -v "Picked up") test/frontend/prolog/corpus/$rung.expected && echo PASS || echo FAIL
done
# Then tackle rung07:
cat test/frontend/prolog/corpus/rung07_cut/cut.pro
./sno2c -pl -jvm test/frontend/prolog/corpus/rung07_cut/cut.pro -o /tmp/Cut.j
java -jar src/backend/jvm/jasmin.jar /tmp/Cut.j -d /tmp && java -cp /tmp Cut
```

**Key design note for cut (from BACKEND-JVM-PROLOG.md §Cut Semantics):**
`E_CUT` seals β. In `pj_emit_body`, `g->kind == E_CUT` currently emits `goto lbl_γ`.
That is wrong — it must also seal the choice point so the caller cannot retry.
In the flat cs-dispatch model, cut means: store `base[nclauses]` into `cs_local`
before jumping to γ. On any subsequent retry, dispatch hits default:omega.

The `pj_emit_body` E_CUT case needs access to `base[nclauses]` for the enclosing
choice. Pass it down as a new parameter `int cut_cs_seal` (= `base[nclauses]`),
defaulting to -1 (no cut in scope). When `E_CUT` fires:
```jasmin
ldc <base[nclauses]>
istore <cs_local>       ; seal: next dispatch → omega
goto lbl_γ
```

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
| **M-PJ-CUT** | Rung 7: `differ/N`, closed-world `!, fail` | ❌ |
| **M-PJ-RECUR** | Rung 8: `fibonacci/2`, `factorial/2` | ❌ |
| **M-PJ-BUILTINS** | Rung 9: `functor/3`, `arg/3`, `=../2`, type tests | ❌ |
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
