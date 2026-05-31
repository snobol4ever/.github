# HANDOFF-2026-05-31-OPUS48-PROLOG-BB-PLG-0-AND-PLG-1.md

**Session:** Claude Opus 4.8, 2026-05-31.
**Goal:** GOAL-PROLOG-BB → PLG ladder.
**Result:** PLG-0 ✅ (audit) + PLG-1 ✅ (ground hello-world runs).
**Commits:** SCRIP `d17425a` (parent `cf6b7f6`); `.github` `b30ee6b8`.
**Both pushed to origin/main.**

---

## ⚠️ The first thing to know: the GOAL doc was stale

When this session opened, `GOAL-PROLOG-BB.md`'s "State at HEAD" entries (top one `1882bc6b`,
2026-05-30) described a Prolog engine that **no longer exists in the live path**. Between that
watermark and SCRIP HEAD `cf6b7f6`, the trunk was Ground-Zero rebuilt:

- **Stack Machine EXCISED.** `src/driver/scrip.c` aborts any non-Icon, non-SNOBOL4 language in
  `--interp`/`--run` with `[SMX] FATAL`. At session start `./scrip --interp hello.pl` → rc 134.
- **Old `lower.c` + `lower_pl.c` DELETED** (blob `d2d8c8e1`) for the unified four-port `lower.c`
  (formerly `lower2.c`). All of WAM-CP / PLR-J / PLR-K / GATE-2/3/SWI is archaeology now.
- Only **Icon + SNOBOL4** were live (via `lower_program.c`'s `lower()`); Prolog had **no arm**.

I added a **READ-FIRST banner** at the top of the PLG section of `GOAL-PROLOG-BB.md` saying exactly
this. Trust the banner + the PLG checkboxes, not the old State entries. The live gate is
`scripts/prove_lower2.sh` (topology) + per-rung mode-2 hello checks — NOT the old GATE numbers.

---

## PLG-0 — audit (doc-only) ✅

`SCRIP/doc/PLG-STACKLESS-AUDIT-2026-05-30.md`. Inventories the 6 value-stack/snapshot mechanisms
with file:line + reachability + keep/remove verdict. Headlines:

- The whole Prolog value-stack apparatus (`bb_node_state_t` snapshot/restore, `resolve_choice` CP
  ledger, `PlCallSt`, `g_resolve_trail`, `rt_pl_*` helpers, `bb_*.cpp` templates, `g_vstack`) is
  **compiled-but-unreachable** behind the SMX gate — dead by excision, not surgical-removal targets.
- **M1 critical caveat for PLG-7:** `bb_node_state_t` snapshot/restore has Prolog sites
  (`bb_exec.c` 918/937/3381/3392/3414/3429 — all dead) BUT **one LIVE Icon caller at
  `bb_exec.c:1589` (`case IR_CALL`)**. PLG-7 must NOT delete the struct until that Icon site is
  migrated under a separate Icon goal. The rung's own "Icon sites are SEPARATE" warning now has
  line numbers.
- M2 `resolve_choice` = KEEP THE IDEA (cursor/CP ledger); M3 `PlCallSt` = SPLIT (keep
  frame+mark+cursor, drop the embedded `act` snapshot=M1); M4 `g_resolve_trail` = KEEP (the trail);
  M5 `rt_pl_*`+templates = KEEP AS REFERENCE (semantic oracle for PLG-10); M6 `g_vstack` = ALREADY
  REMOVED (it's a bomb tripwire in `rt.c`).

---

## PLG-1 — ground hello-world runs ✅

`corpus/programs/prolog/hello.pl` (`main :- write('Hello, World!'), nl.`) now PRINTS
`Hello, World!` in mode-2. Prolog has crossed onto Byrd Boxes for the variable-free single-clause
tier.

### The key architectural finding
The new `lower_goal` write-family went through the **shared** `wire_det_builtin1` → `IR_CALL`,
which carries **Icon** write semantics (arg via the AG ring + a trailing newline) and has no `nl`.
Meanwhile `bb_exec.c` **already had a correct Prolog `IR_BUILTIN` arm** (`:3479+`: `pl_write` with
NO auto-newline; `nl` = `putchar('\n')`; plus is/comparison/findall/sort/format) that **nothing
produced**. PLG-1 connects the new lowerer to that existing-but-orphaned EXEC arm.

Verified distinct: Prolog `write(foo),nl,write(bar),nl` → `foo\nbar\n` (single newlines). Icon
`write` still double-spaces two writes → sibling semantics unbroken.

### The four files (all FACT-RULE clean — Prolog-only arms, no peer arm touched, FACT grep 0)

1. **`src/lower/lower.c`**
   - `g_term` — Prolog term in arg position → `IR_ATOM` / `IR_LOGICVAR` (slot in ival) / `IR_LIT_I`
     / `IR_LIT_F` / `IR_STRUCT` (functor=sval, args on the α-γ chain). The kinds `resolve_node_to_term`
     (`bb_exec.c:127`) materializes into a `Term*`. Successor to the deleted `lower_pl_term`.
   - `g_builtin` — write/writeln/print/nl → Prolog-OWNED `IR_BUILTIN` (sval=fn, ival=arity, args
     chained on `bb->α`, BOUNDED: resume→ω). NOT the shared `IR_CALL`. Successor to the deleted
     `lower_pl_new_Builtin`.
   - `nl` arm added to the GOAL `TT_QLIT` switch.
   - write/writeln/print arms in the GOAL `TT_FNC` switch re-pointed from `wire_det_builtin1` to
     `g_builtin`.
   - Public `lower2_clause_body_entry(bbg, clause, γ, ω, &α, &β)` — clause body goals (children
     after the head-arg patterns) → `IR_GCONJ` via `wire_seq`; bare fact (0 body goals) → `IR_SUCCEED`.

2. **`src/lower/lower_program.c`**
   - `lower_pl_clause_graph(clause)` — one TT_CLAUSE → a GOAL graph (PSUCC/PFAIL sentinels, entry=α).
   - `LANG_PL` arm in `lower()` — reads the `:- initialization(G[,main])` directive subject to get
     the goal predicate key (default `main/0`), looks it up in `resolve_pred_table` (populated by
     `polyglot_init`), lowers its clause body, registers proc `main` with the bb_idx. Mirrors the
     existing SNOBOL4/Icon arms.

3. **`src/driver/scrip.c`** — `mode_interp` Prolog arm: `bb_exec_once(main_bb)` (was the SMX abort).

4. **`src/lower/prove_lower2.c`** — `kname` extended (BLTIN/ATOM/STRCT/LVAR) + 2 PLG-1 proof cases
   (`write('hi')` → BLTIN+ATOM = 2 nodes; `nl` → bare BLTIN leaf = 1 node).

### Gates (this session)
- `prove_lower2.sh`: **35/35 PASS, 0 FAIL** (incl. the 2 new PLG-1 cases + the unchanged
  conj/disj/unify/compare Prolog cases — the write→IR_BUILTIN change re-shaped the conj proof to
  GCONJ(BUILTIN,ATOM,BUILTIN,ATOM)=5 nodes, still PASS).
- Prolog GATE-1 smoke: **0 → 1** (`write_atom` passes; `unify`/`arith`/`clause`/`recursion` are
  PLG-2/3/6 work).
- Siblings **byte-identical to baseline** (verified by stash → rebuild → compare): Icon mode-2 5/1,
  SNOBOL4 3/10. Those pre-existing failures are the mid-flight Ground-Zero rebuild, NOT my change.
- FACT grep: **0**. No x86 byte emitters introduced (emit is excised anyway).

### Note on the rung's "snapshot counter == 0" instruction
PLG-1's text asks to instrument a `bb_snapshot_state` counter and assert 0 for hello. Post-excision
that's moot for the ground case: the hello clause graph is a flat `GCONJ(BUILTIN,BUILTIN)` with NO
`IR_CALL`/`IR_CHOICE`/`IR_GOAL`, so no snapshot site is even reached. The instrumentation belongs to
PLG-2/3 when user-calls / clause-choice first appear. Documented in the GOAL doc PLG-1 entry.

---

## NEXT — PLG-2 (single non-recursive predicate WITH variables)

Target: `greet :- X = world, write(X), nl. :- greet.` (and the GATE-1 `unify`/`arith` smoke cases).

**The blocker is already diagnosed this session.** `=/2` lowers to `IR_UNIFY` and `write(X)` to
`IR_BUILTIN`+`IR_LOGICVAR`, but **the clause graph allocates no `g_resolve_env`**, so the
`IR_LOGICVAR` slot-0 read in `resolve_node_to_term` returns an unbound fresh var and `write(X)`
prints nothing (`/tmp/unify.pl` → empty, rc 0). PLG-2 must **allocate the per-activation env/frame**
(the `pl_foo_2_r`-locals / `ζ`-slot-vector analogue) and install it (`g_resolve_env`) before running
the clause graph, so slot 0 resolves to the term `=/2` bound. The clause's slot count is in
`clause->v.ival` (total vars) — that's the frame size. This is the **first appearance of the
per-activation frame** the whole PLG ladder is built around (the thing that replaces M1's snapshot).

Look at how the old engine installed the env: `resolve_bb_env_install` / `resolve_bb_env_save_push`
(`src/runtime/interp/resolve_runtime.h`) + the `genv` allocation pattern in `bb_exec.c`'s
`rt_pl_aggregate_all_term` (`:912` — `Term **genv = calloc(garity+16, ...)`, then
`g_resolve_env = genv`). For PLG-2 a single env allocated in `scrip.c`'s Prolog arm (or in
`lower_pl_clause_graph`'s driver shim) sized to `clause->v.ival`, installed before `bb_exec_once`,
should suffice for the non-recursive single-clause case. NO snapshot needed (PLG-2 invariant).

After PLG-2: PLG-3 (facts + first-solution call → needs `IR_GOAL` user-call + `IR_CHOICE` clause
dispatch re-grown), PLG-4 (backtracking enumeration), PLG-6 (recursion = the crux).

---

## Session-setup reminder for next time (post-excision; the old PLAN.md script still works)
```
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/prove_lower2.sh            # LIVE topology gate — must be 35/35 (+ your new cases)
bash scripts/test_smoke_prolog.sh       # GATE-1 — currently 1/5 (write_atom); grows with PLG rungs
./scrip --interp corpus/programs/prolog/hello.pl   # must print Hello, World!
```
The old `test_prolog_rung_suite.sh` / `test_crosscheck_prolog.sh` / `test_prolog_mode4_rung.sh`
exercise the excised path — expect them to be meaningless/aborting until the PLG ladder re-grows
the corresponding machinery. Develop against mode-2 (`--interp`) as the correctness reference.
