# HANDOFF-2026-06-14-CLAUDE-RAKU-BB-GRAMMAR-PARSE-FOUNDATION.md

## Session: GOAL-RAKU-BB — grammar `.parse` end-to-end in all three modes (RK-GRAM foundation)

**SCRIP HEAD at open: `1b71e43`. At close: `f3b1837`** (1 commit landed, rebased cleanly over peer
`b7272f6` "Prolog δ/ε port eradication"). `.github` updated (this doc + watermark + RK-GRAM-3 rung note).

**Gates at close — Raku m2 35/35 (HARD ✓); m3 35/35; m4 35/35.** Peers invariant: Icon m2/m3/m4 = 12/12/12,
SNOBOL4 m4 7/7 (HARD ✓), NFA oracle 5/5. `g_vstack`=0, `bb_bin_t`=0. Smoke grew 31→35 (4 new grammar tests).

---

## What landed — `f3b1837`

Raku grammar `.parse` now runs end-to-end in mode 2 (`--interp`), mode 3 (`--run`), and mode 4 (`--compile`).
Subrule `<name>` references are inline-expanded into a single NFA pattern (the pre-existing `gram_expand`
path); `.parse` returns the matched string (truthy) on a full anchored match, or `NULVCL` (falsy) on no-match.

This is the **RK-GRAM grammar-parse FOUNDATION**. It is NOT RK-GRAM-3 (THE SEAM) — see SCOPE below.

### The gap that was closed (machinery existed, was never wired)

The grammar runtime was already present in `by_name_dispatch.c` but **unreachable**:
- `gram_expand(gname, body, flavor, ...)` — flattens `<name>` subrules by recursive inline substitution.
- `grammar_parse` (by-name) — expands TOP, builds an NFA, matches, returns subject-or-FAIL.

Two reasons it was dead:
1. **Rules were never registered.** `TT_GRAMMAR_DECL` and `TT_REGEX_DECL` lowered to a no-op `IR_SUCCEED`
   (`lower_raku.c`), so `gram_reg[]` stayed empty → `grammar_parse` always returned FAIL.
2. **`MyGram.parse(s)` could not find the grammar.** The parser lowers a `.new` receiver as a string literal
   but a generic `.method` receiver (`raku.y` `IDENT '.' IDENT '(' ... ')'`) as `var_node($1)`. So `MyGram`
   became a free `IR_VAR "MyGram"` → NUL at runtime (name lost) AND tripped the mode-3/4 EXCISE gate
   (`icn_graph_native_emittable_mode`: a free var that is neither assigned nor a parameter → `return 0`).

### The three coordinated edits

1. **`src/lower/lower_raku.c`**
   - `rk_discover_grammars(prog)` — new; called FIRST in `lower_raku_stage2` (before bodies are lowered).
     Walks `TT_GRAMMAR_DECL`, registers every `token/rule/regex` child via `rt_grammar_register(qname, body,
     flavor)` (qname = `"Gname::rulename"`, flavor 0/1/2 = token/rule/regex), and records each grammar NAME
     in a file-static set `g_rk_gram_names[]`.
   - In BOTH `lower` and `lower_rv`, the `case TT_VAR` now checks `rk_is_grammar_name(name)`: a grammar-name
     bareword lowers to **`IR_LIT_S`** (the name as a string literal) instead of `IR_VAR`. This is the keystone
     — the name now travels into `meth_call` as a string AND is no longer a free var, so the mode-3/4 gate
     stops excising. (Barewords matching a grammar are type references, never sigil'd vars, so this is safe
     everywhere.)
   - Synthesized-main loop (no `sub main`) now also skips `TT_GRAMMAR_DECL` (cleanliness; it produced a
     harmless `IR_SUCCEED` before).

2. **`src/runtime/by_name_dispatch.c`**
   - Public `rt_grammar_register` / `rt_grammar_count` / `rt_grammar_qname` / `rt_grammar_body` /
     `rt_grammar_flavor` / `rt_grammar_has_top` (thin wrappers over the existing static `gram_reg[]` +
     `gram_set`/`gram_get`).
   - `grammar_parse_core(gname, subj, out)` — factored from the old `grammar_parse` body; the `grammar_parse`
     by-name handler now calls it. **No-match returns `NULVCL`, not `FAILDESCR`.** (Returning `FAILDESCR`
     makes the `meth_call` node take its ω port → the whole assignment graph fails → empty output. `NULVCL`
     is falsy (`rt_rk_is_truthy`/`__rk_bool` treat `DT_SNUL` as false) but is NOT `IS_FAIL`, so the node takes
     γ, binds the falsy value, and `if ($r) {...} else {...}` correctly runs the else arm.)
   - `meth_call` gained a leading branch (BEFORE the `args[0].v != DT_DATA` class check): if the method is
     `"parse"`, nargs==3, and `args[0]` is a string naming a registered grammar TOP (`rt_grammar_has_top`),
     route to `grammar_parse_core`.

3. **`src/driver/scrip.c`** (mode-4 standalone startup)
   - The standalone binary starts with an empty `gram_reg[]`, so it must re-register. Mirroring the class
     `record_register` loop, the `icn_proc_startup` block now also emits, per registered rule:
     `.Lgramqn<i>`/`.Lgrambd<i>` as **`.byte` sequences** (immune to regex backslashes/quotes — a `.string`
     would mis-handle `\d`/`\w`), then `lea rdi,[qname]; lea rsi,[body]; mov edx,flavor; call
     rt_grammar_register@PLT`. The whole startup block + its call are now gated on
     `(n_procs>0 || n_cls_emit>0 || n_gram_emit>0)`. (`gram_reg[]` is populated during `lower_raku_stage2`,
     which runs in the scrip process before emit, so the enumerators see the rules at emit time.)

4. **`src/runtime/rt/rt.h`** — declarations for the six `rt_grammar_*` functions.

5. **`scripts/test_smoke_raku.sh`** — +4 tests: `grammar_token`, `grammar_subrule`, `grammar_multi_subrule`,
   `grammar_nomatch`.

---

## ⚠ KEY GOTCHA (cost real time — read before any runtime edit)

`scrip` **statically links the runtime** (`by_name_dispatch.c` etc. are compiled INTO the `scrip` binary).
`out/libscrip_rt.so` is used **only by mode-4 standalone binaries**. So modes 2/3 and mode 4 run DIFFERENT
copies of the runtime. After ANY edit to a runtime `.c`, rebuild **both**:
```bash
rm -f scrip && make scrip      # modes 2/3 (static runtime)
make libscrip_rt               # mode 4 (.so)
```
This session, rebuilding only `libscrip_rt` made mode 4 show the `NULVCL` fix while modes 2/3 ran stale and
appeared to "still fail" — a phantom bug. Always rebuild both; the smoke harness does.

---

## Compliance (all clean)

No C Byrd box (`grammar_parse_core` is `(const char*, const char*, DESCR_t*)`), no value stack
(`g_vstack`=0), no `bb_bin_t`, no templates touched (only runtime + lowerer + driver + smoke), no AST/IR walk
on the run path — `grammar_parse_core` operates on `char*`/`DESCR_t` only (`gram_expand` on strings, NFA build/
exec on strings). The mode-4 emission and `rk_discover_grammars` walk the AST/registry at COMPILE time (before
execution), which is sanctioned. `git stash` test confirmed the 5 `audit_concurrency_invariants.sh` VIOLATIONs
are PRE-EXISTING (identical count without the change) — stale `src/lower/lower.c` path + LOWER/EMITTER FACT
md5 drift in GOAL-ICON/PROLOG, as noted in prior handoffs.

---

## SCOPE — what this is NOT (and the next rung)

This is the **inline-expansion** path: subrules are textually flattened into ONE NFA pattern before matching.
It is NOT **RK-GRAM-3 (THE SEAM)** — the generator-PUMP that does resume-and-yield-next backtracking ACROSS
the subrule call boundary and builds a real Match tree. RK-GRAM-3 is now UNBLOCKED: grammars register and
`.parse` dispatches, so the PUMP work replaces the NFA call inside `grammar_parse_core` with the IR_* SUSPEND/
ALT/PUMP machinery (the same machinery scoped for the non-materialized map/grep PUMP) and yields a Match
object. The natural deliverable on top of a Match object is `$m<name>` / `$m[0]` named-and-positional capture
access (the lexer/AST already produce `VAR_NAMED_CAPTURE`/`VAR_CAPTURE`; today they ride the `~~` C matcher).

Today `.parse` returns the matched STRING (truthy) or `NULVCL` (falsy) — a Match approximation sufficient for
verdict + capture-free grammars (the 4 new smoke tests).

---

## Session Setup
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt   # BOTH — see gotcha above
bash scripts/test_smoke_raku.sh      # m2 35/35 HARD; m3 35/35; m4 35/35
bash scripts/test_smoke_icon.sh      # 12/12/12 HARD
bash scripts/test_smoke_snobol4.sh   # m4 7/7 HARD
bash scripts/test_gate_raku_nfa_oracle.sh   # 5/5
```

## ORDER OF WORK for next session
1. **RK-GRAM-3 (THE SEAM)** — swap `grammar_parse_core`'s NFA call for the generator PUMP (resume-and-yield-
   next across the subrule boundary); build a Match object; then `$m<name>`/`$m[n]` capture access.
2. (Independent, still available) GROUP A's real non-materialized map/grep PUMP, if a side-effecting/string
   map/grep test is added — shares RK-GRAM-3's PUMP machinery.

## Commit this session (pushed + verified on origin/main)
| Commit | Repo | What |
|---|---|---|
| `f3b1837` | SCRIP | Raku grammar `.parse` end-to-end (all 3 modes) — RK-GRAM grammar-parse foundation |
