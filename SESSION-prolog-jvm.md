# SESSION-prolog-jvm.md — Prolog × JVM (snobol4x)

**Repo:** snobol4x · **Frontend:** Prolog · **Backend:** JVM (Jasmin)
**Session prefix:** `PJ` · **Trigger:** "playing with Prolog JVM"
**Driver:** `sno2c -pl -jvm foo.pl -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `sno2c -pl -asm foo.pl` (ASM emitter)

## Subsystems

| Subsystem | ARCH doc | Go there when |
|-----------|----------|---------------|
| Full milestone history | ARCH-prolog-jvm.md | reviewing completed work, milestone IDs |
| JVM Prolog runtime design | ARCH-jvm-prolog.md | term encoding, trail, clause dispatch |

---
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`
---

## §BUILD

```bash
cd snobol4x && make -C src
export JAVA_TOOL_OPTIONS=""   # suppress proxy JWT noise
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/prolog/prolog_emit_jvm.c` | JVM emitter + linker (~line 6995) |
| `test/frontend/prolog/plunit.pl` | plunit shim |
| SWI tests | `swipl-devel-master/tests/core/test_*.pl` (58 files) |

---

## §NOW — PJ-77a

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog JVM** | PJ-77a — corpus 30/30 | `b7b7aa7` | M-PJ-SWI-BASELINE |

### NEXT ACTION — PJ-78: M-PJ-SWI-BASELINE continued

**Task 1 — CRITICAL: `true(Expr)` opts variable-sharing fix**
- `test(name, X==y) :- Body` — bridge emits `pj_term_var()` for `X` in opts, disconnected from `X` in `Body`
- Fix: inline `pj_emit_body(body_goals) + pj_emit_goal(expr_check)` in same JVM frame
- E_CLAUSE layout: `children[0..n_args-1]` = head args, `children[n_args..]` = body goals

**Task 2 — remaining parse gaps** (run test_arith/unify/dcg/misc to find)

**Task 3 — throw/catch semantics** (test_exception.pl — 5 failures)

**SWI baseline so far:**
- `test_list.pl` — 0p/1f: `true(Expr)` opts variable-sharing gap
- `test_exception.pl` — 0p/5f/1s
- `test_arith/unify/dcg/misc.pl` — compile errors (parse gaps)

