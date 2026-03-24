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
| **Prolog JVM** | `main` PJ-10 — fix jvm_arg_for_slot first-occurrence bug; rungs 01-05 PASS | `64d350a` PJ-10 | M-PJ-LISTS |

### CRITICAL NEXT ACTION (PJ-11)

**rung06 `lists` still silent — two bugs, one fixed, one remaining.**

**Bug 1 FIXED (PJ-10, commit `64d350a`):** `jvm_arg_for_slot[]` recorded LAST occurrence of a var slot across head args, not first. In `append([],L,L)` the scan overwrote `jvm_arg_for_slot[0]=1` with `jvm_arg_for_slot[0]=2`, so var cell loaded from arg2 instead of arg1. The second non-linear unify became `pj_unify(arg2,arg2)` — a self-unify no-op. arg1 `[c,d]` was never bound into `L`. Fix: `if (jvm_arg_for_slot[ht->ival] < 0)` guard — first occurrence wins.

**Bug 2 REMAINING:** After fix, `java Lists` still exits 0 with no output. `append` unification is now correct. The remaining issue: `write(L)` calls `pj_write(local4)` where `local4` is the `L` var cell (now a `"ref"` cell pointing at the result after unification). `pj_term_str` calls `pj_deref` at the top — this correctly follows the ref chain to the bound compound `.(a,.(b,.(c,.(d,[]))))`. The list-detection path (functor `"."`, arraylength==4) should then trigger. **Suspected cause:** `main` itself is silently failing — not a `pj_term_str` bug but a `main` body goal failure before `write` is reached. The `p_append_3` call in `main` returns null (ω) despite the fix. Need to confirm the fix actually compiled into the binary being tested — recheck by regenerating `.j` and inspecting `p_append_3_clause0` to confirm `aload 1` (not `aload 2`) is used for the var slot.

**Bootstrap PJ-11:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Confirm baseline: rungs 01-05 PASS (should be clean at 64d350a)
# Regenerate and inspect:
./sno2c -pl -jvm test/frontend/prolog/corpus/rung06_lists/lists.pro -o /tmp/l.j
grep -A 5 "p_append_3_clause0:" /tmp/l.j   # must show aload 1 for var slot
java -jar src/backend/jvm/jasmin.jar /tmp/l.j -d /tmp
java -cp /tmp Lists
# If still silent: add debug write before append call to confirm main entry,
# then step through append call to find where it returns null.
# Minimal repro: append([],[c,d],L), write(L), nl  — isolate base case.
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
