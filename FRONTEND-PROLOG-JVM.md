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
| **Prolog JVM** | `main` PJ-7 — M-PJ-BACKTRACK ✅ rung05 a/b/c pass; Greek port names throughout | `c6a8bda` PJ-7 | M-PJ-LISTS |

### CRITICAL NEXT ACTION (PJ-8)

**rung02 `facts` infinite loop** — pre-existing, not caused by PJ-7. `person(X), write(X), nl, fail ; true` loops forever outputting `person` atoms endlessly. Diagnose first before M-PJ-LISTS work. Suspect: disjunct alt wiring (`disj_alt1 → dg0_g → p_main_0_gamma_0`) causes main to re-enter on every `fail` instead of terminating.

**M-PJ-LISTS next** — rung06: `append/3`, `length/2`, `reverse/2`. γ formula fix (PJ-7) should handle these; resolve rung02 loop first.

**Greek port naming convention (PJ-7):**
- C local vars: `lbl_γ`, `lbl_ω`, `lbl_outer_ω`, `call_α`, `call_ω`, `call_β`, `g_γ`, `g_ω`, `γ_lbl`, `ω_lbl`, `α_lbl`, `α_retry_lbl`
- Generated Jasmin labels: `_alpha_`, `_alphafail_`, `_beta_`, `_gamma_`, `_omega` (ASCII — Jasmin constraint)
- No Greek in external C linkage (function names visible to linker)

**Bootstrap PJ-8:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Confirm baseline: rungs 01/03/04/05 PASS, rung02 loops (known bug)
./sno2c -pl -jvm test/frontend/prolog/corpus/rung05_backtrack/backtrack.pro -o /tmp/bt.j
java -jar src/backend/jvm/jasmin.jar /tmp/bt.j -d /tmp/ && timeout 5 java -cp /tmp Backtrack
# Expected: a\nb\nc
```

## Milestone Table

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-SCAFFOLD** | `-pl -jvm null.pl → null.j` assembles + exits 0 | ✅ |
| **M-PJ-HELLO** | `write('hello'), nl.` → JVM output `hello` | ✅ |
| **M-PJ-FACTS** | Rung 2: deterministic fact lookup | ✅ |
| **M-PJ-UNIFY** | Rung 3: head unification, compound terms | ✅ |
| **M-PJ-ARITH** | Rung 4: `is/2` arithmetic | ✅ |
| **M-PJ-BACKTRACK** | Rung 5: `member/2` — β port, all solutions | ✅ |
| **M-PJ-LISTS** | Rung 6: `append/3`, `length/2`, `reverse/2` | ❌ |
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
