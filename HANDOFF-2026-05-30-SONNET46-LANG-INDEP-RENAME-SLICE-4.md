# HANDOFF — LANG-INDEP-RENAME Slices 3c + 4

**Date:** 2026-05-30 · **Author:** Claude Sonnet 4.6 · **Goal:** `GOAL-LANG-INDEPENDENT-RENAME.md`
**SCRIP HEAD:** `8e4d0b2b` (pushed) · **.github HEAD:** (this commit)

---

## What shipped

### Slice 3c — Prolog cross-boundary (`bd91ea84`, prior commit)
All 29 exempted symbols triaged: after SMX-4 deletion, `g_pl_trail`, `g_pl_cut_flag`, `pl_env_new`,
`pl_pred_table_lookup_global`, `pl_unified_term_from_expr`, `pl_throw_existence_error_procedure` were
**already deleted**. `pl_box_*` and `pl_assert_term` are **frontend-defined** (in `src/frontend/prolog/`) →
EXEMPT per the frontier rule. Only live rename: `SM_BB_PL_INVOKE → SM_BB_PRED_INVOKE` (strips `PL`
from the shared opcode enum; was only in comments outside SM.h — no code change, pure cosmetic).

### Slice 4 — Raku (`8e4d0b2b`)
**File renames:** `raku_builtins.c/.h → script_builtins.c/.h`, `raku_builtins_byname.c → script_builtins_byname.c`
(in `src/runtime/interp/`).

**Symbol renames (feature-named, NOT `gen_` — per Lon's rule):**
- `raku_fh_*` → `fh_*` (file-handle facility)
- `raku_grammar_*` → `grammar_parse` / `grammar_register`
- `raku_exc_*` → `exc_check` / `exc_clear` / `exc_get`
- `raku_meth_*` → `meth_lookup` / `meth_ntypes` / `meth_register` / `meth_table` / `meth_call`
- `raku_match` / `raku_match_global` → `re_match` / `re_match_global`
- `raku_capture` → `fh_capture`; `raku_re_capture` → `re_capture`; `raku_named_capture` → `re_named_capture`
- `raku_subst` / `raku_subst_pat` → `re_subst` / `re_subst_pat`
- `raku_grep` / `raku_map` / `raku_sort` → `array_grep` / `array_map` / `array_sort`
- `raku_index` / `raku_rindex` / `raku_substr` / `raku_lc` / `raku_uc` / `raku_trim` / `raku_strpos` / `raku_strbuf` → `str_index` / `str_rindex` / `str_substr` / `str_lc` / `str_uc` / `str_trim` / `str_pos` / `strbuf`
- `raku_itos` / `raku_rtos` → `itos` / `rtos`
- `raku_new` → `obj_new`; `raku_die` → `script_die`; `raku_try` → `script_try`
- `raku_try_call_builtin` / `raku_try_call_builtin_by_name` → `script_try_call_builtin` / `script_try_call_builtin_by_name` (needed `script_` prefix to avoid link collision with the shared `try_call_builtin_by_name` in `gen_runtime.c`)
- `raku_try_hash_mutating_builtin` / `raku_try_mutating_builtin_by_name` / `raku_try_hash_builtin` → `script_try_hash_mutating_builtin` / `script_try_mutating_builtin_by_name` / `script_try_hash_builtin`
- `rk_junction_collapse` / `rk_junction_is` → `junction_collapse` / `junction_is`
- `rk_sub_label` / `rk_sub_lookup` / `rk_subs` → `sub_label` / `sub_lookup` / `subs`
- `rk_for_array*` / `rk_range_for` → `for_array*` / `range_for`
- `rk_gram_*` → `gram_*`
- `RAKU_FH_MAX` → `FH_MAX`; `g_raku_exception` → `g_script_exception`
- Makefile `.o` targets updated to match new file names

**EXEMPT (frontend-defined, left as-is):**
`raku_compile`, `raku_cc_test`, `raku_nfa_to_bb`, `raku_nfa_*` (all from `src/frontend/raku/raku_re.h`/`raku_nfa_bb.c`).
`raku_yy*` — flex/bison lexer internals in `raku.lex.c` / `raku.tab.c` (frontend files, not in scope).
`__rk_jct_*` / `__rk_arr` inside `strcmp(fn, "...")` calls — Raku VM opcode name *strings*, not C identifiers; they match what the Raku parser emits and must stay stable.

**Gates (all green):** `make scrip` rc=0 · `make libscrip_rt` rc=0 · Icon m2 **6/6 (HARD)** · m3 2/6 · FACT=0 · sm_dead=1.

---

## CRITICAL MISTAKE MADE THIS SESSION — DO NOT REPEAT

**I initially renamed `raku_*` → `gen_*`.** Lon correctly rejected this: `gen_` is already polluted
in compilers (GENerators, code GENeration). The fix renamed them to feature names on the second pass.
**The rule:** strip the language prefix, pick the CULTURAL FEATURE WORD. `gen_` is NOT a neutral
prefix — it has strong compiler connotations. For Raku-specific builtins that couldn't get a bare
feature name without collision, `script_` was used (script-layer builtins, distinct from scanner
builtins and Prolog resolution builtins).

---

## Slice 5 — deferred
Backend output libs (`.il/.j/.wat/.cs/.java/.js`) still named `Sno*` / `pl_*` / `raku_*`. These are
off the live X86 path (X86 ONLY per RULES.md). Lowest priority — do after SNOBOL4-BB LOWER.

---

## NEXT PRIORITY: SNOBOL4-BB LOWER (Track B)

Per PLAN.md and Lon's directive, the rename is done. Move to **GOAL-SNOBOL4-BB.md**.

**The task:** wire SNOBOL4 AST → BB directed graph so SNOBOL4 can run via `bb_exec_once` (not the
`[SMX] FATAL` abort). See `HANDOFF-2026-05-30-OPUS48-SMX-4-DELETE-SM.md` Track B for the full plan.

**First target:** `OUTPUT = "hello world"` passing `--interp` mode-2.

**Immediate steps:**
1. In `lower.c::lower_proc_skeletons()`, add a SNOBOL4 branch that calls a new `lower_sno_main(prog)`
   function (in a new `src/lower/lower_sno_bb.c`) to build a `BB_graph_t` from the SNOBOL4 AST.
2. `lower_sno_main` for hello-world: walk top-level `TT_STMT` nodes; a `:eq` statement with
   `TT_VAR OUTPUT` as subject and `TT_QLIT "hello"` as replacement lowers to:
   `BB_ASSIGN` node with `BB_LIT_S` operand (via `bb_operand_aux_set`, PEERS RULE).
3. In `scrip.c::mode_interp` block: the `is_icon` gate currently monopolizes `bb_exec_once`.
   Generalize: after `sm_preamble`, if `s2->bbp.count > 0` and a `main` BB graph exists, call
   `bb_exec_once` regardless of language (remove the `is_icon` guard, or add `|| is_snobol4`).
4. `bb_exec.c` already has `BB_ASSIGN` + `BB_LIT_S` + `BB_VAR` cases for Icon — confirm they work
   for SNOBOL4's OUTPUT assignment (OUTPUT is a comm_var; `NV_SET_fn` on OUTPUT triggers the print
   hook in `core.c`). Read SPITBOL manual for OUTPUT semantics before touching.

**AST shapes for the smoke suite (already dumped):**
- `OUTPUT = 'hello'` → `(STMT :eq :subj (TT_VAR OUTPUT) :repl (TT_QLIT "hello"))`
- `OUTPUT = 'ab' 'cd'` → `:repl (TT_SEQ (TT_QLIT "ab") (TT_QLIT "cd"))`
- `OUTPUT = 2 + 3` → `:repl (TT_ADD (TT_ILIT 2) (TT_ILIT 3))`
- `S = 'abc'; S 'b' = 'X'; OUTPUT = S` → includes `TT_SCAN` (pattern match)
- `'x' 'x' :S(HIT)` → conditional goto
- `DEFINE('double(x)', 'double') ... double = x * 2 :(RETURN)` → user function

**Read SPITBOL manual before implementing each construct.**

---

## Session Setup for Next Session

```bash
git clone https://ghp_TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://ghp_TOKEN@github.com/snobol4ever/SCRIP.git /home/claude/SCRIP
git clone https://ghp_TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh   # MUST be m2 6/6 (HARD GATE)
# Then proceed to GOAL-SNOBOL4-BB.md Track B / LOWER
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
