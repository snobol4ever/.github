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
| **Prolog JVM** | `main` PJ-9 — fix var-slot mismatch + non-linear head + pj_term_str; rungs 01-05 PASS | `5ae73e3` PJ-9 | M-PJ-LISTS |

### CRITICAL NEXT ACTION (PJ-10)

**rung06 `lists` silent failure — `pj_term_str` list path not triggering.**
`append([],[b,c],L)` now succeeds (base-case non-linear fix worked) but `write(L)` prints `_` instead of `[b,c]`. The list-detection path in `pj_term_str` checks `arraylength == 4` (arity-2 compound) but `[b,c]` is `.`(b,`.`(c,[])) — the outer cell has length 4, so the check should match. Suspect: the `pts_list_close` label is reachable from two paths (proper-nil tail and improper-tail fallthrough) with mismatched locals state — check Jasmin output for `pj_term_str` list section around `pts_list_close`.

Three bugs fixed in PJ-9 (see commit `5ae73e3`):
1. `jvm_arg_for_slot[]` replaces `is_direct_arg` slot==ai check — fixes `append([H|T],L,[H|R])` clause
2. Non-linear head unification via `seen_at[]` — fixes `append([],L,L)` base case
3. `pj_term_str` replaces old `pj_write` — handles compound/list recursively (list path has remaining bug)

**Bootstrap PJ-10:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Confirm baseline: rungs 01-05 PASS
# Debug: ./sno2c -pl -jvm /tmp/ap_base.pro -o /tmp/apb.j && javap -c /tmp/Lists.class | grep -A 50 pj_term_str
# Look at pts_list_close — fix locals/stack issue there
# Then test rung06: ./sno2c -pl -jvm test/frontend/prolog/corpus/rung06_lists/lists.pro -o /tmp/l.j
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
