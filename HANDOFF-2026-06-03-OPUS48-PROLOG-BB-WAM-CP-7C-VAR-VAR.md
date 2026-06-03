# HANDOFF 2026-06-03 (Opus 4.8) — Prolog WAM-CP-7c: var-var unify 3→1 calls (gprolog-grounded)

## TL;DR
WAM-CP-7c DONE. Distinct var-var unify (`X = Y`, two logic vars in different slots) now emits ONE
`rt_pl_unify_var_var(lslot, rslot)` call instead of THREE (2×`rt_node_to_term` + 1×`rt_unify_terms`).
Grounded in the canonical gprolog WAM (`src/EnginePl/unify.c`). **SCRIP HEAD `5dff1a8`** (pushed).
GATE-3 byte-identical: m2 111/111 · m3 111/111 · m4 75/0/36. (Earlier same day: PL-HY-FENCE gate `1a0127e`.)

## Canonical grounding (uploaded gprolog sources, per CONSULT-CANONICAL-SOURCES rule)
`refs/gprolog-master/src/EnginePl/unify.c`, the `TAG_REF_MASK × TAG_REF_MASK` branch: DEREF both, then
`u_adr > v_adr` → bind u→v; `v_adr > u_adr` → bind v→u; **equal (same cell, `X=X`) → no bind, no trail,
return TRUE.** SCRIP's existing `prolog_unify.c:unify()` already implements exactly this law (`term_deref`
both; `t1==t2` → 1; either `TERM_VAR` → `bind` with `trail_push` iff `var_slot != -1`). So WAM-CP-7c is a
CALL-COUNT optimization, not a semantics change — the var-var path was already correct via the 3-call route.

## What landed (SCRIP `5dff1a8`, 2 files / +17 lines)
- **`src/runtime/unification.c`** — new `int rt_pl_unify_var_var(int lslot, int rslot)`: materializes each env
  slot exactly as `rt_node_to_term(IR_LOGICVAR, slot)` does (deref `g_resolve_env[slot]`, or `term_new_var`
  + store if NULL), then returns `rt_unify_terms(lt, rt_)`. Reuses the audited `unify()` (deref / `X==X` noop
  / trailed bind) — nothing re-implemented. Placed right after `rt_unify_const`, same slot-materialization idiom.
- **`src/emitter/BB_templates/bb_unify.cpp`** — new arm BELOW the self-unify check, ABOVE var-const:
  `if (lk == IR_LOGICVAR && rk == IR_LOGICVAR)` (li!=ri guaranteed, self-unify caught above) →
  `mov edi,li; mov esi,ri; call rt_pl_unify_var_var; <u_tail>`. Pure `x86()` concat (0 raw-byte producers —
  medium-invisible). `extern "C"` decl added beside the other rt_unify externs (mirrors `rt_unify_const`,
  which is also declared locally, not in rt.h — header untouched).

## Verification
- `X=Y, Y=hello`: emits **1× `rt_pl_unify_var_var`** (was 2×`rt_node_to_term`+1×`rt_unify_terms`) + 1×`rt_unify_const` (Y=hello unchanged). Runs → `hello`.
- Backtracking trail test (`p(1).p(2).p(3). main:-X=Y,p(Y),write(X),nl,fail.`): m4 prints `1 2 3` — **identical to m2 interp** (X tracks Y across all solutions; bind trailed + undone correctly).
- GATE-1 smoke m2 5/5 (m3 unify FAIL = known harness artifact). GATE-3 **m2 111/111 · m3 111/111 byte-identical · m4 75/0/36** — unchanged baseline.
- Gates touched-area: `test_gate_pl_no_value_stack.sh` PASS; `test_gate_bb_one_box.sh` PASS; `test_gate_no_bb_bin_t.sh` 0; FACT greps `seg_byte/SL_B` 0, `g_vstack` 0.
- Build: `make libscrip_rt` + `make -j4 scrip` rc=0 (pre-existing INTVAL/REALVAL + bb_lit %d warnings only).
- **Build gotcha noted:** scrip links `/tmp/si_objs/*.o` by glob; the incremental rule rebuilt `bb_unify.o` but the FIRST relink used a STALE `scrip`. `rm /tmp/si_objs/bb_unify.o && make scrip` forced the correct relink. If an emitter edit "doesn't take," force-rebuild its `.o` then `make scrip`.

## FACT-RULE integrity
`.github` edit to `GOAL-PROLOG-BB.md` = 2 Prolog-only regions (WAM-CP open-list 7c line → `[x]`; gate-table
caption). NO-C-BYRD-BOX block byte-identical across all five GOAL-*-BB (`5e81271…`). No FACT block touched.
Corpus `.s` artifacts regenerate from the emitter (suite diffs `.expected`, not `.s` text) — left CLEAN
(`git checkout -- programs/prolog/*.s`); the leaner var-var `.s` belongs to whoever next regenerates+commits
the corpus, with their own verification (same convention as the 2026-06-03 audit handoff).

## NEXT (unblocked) vs (needs Lon)
**Unblocked, mechanical, WAM-CP track:**
- **WAM-CP-9 (rest)** — committed-ITE node; bare `!` in `(A;B)` through truncate; retire `g_pl_cut_flag`.
- **WAM-CP-11** — deep-backtracking arg restore (`saved_args`) + nested choices.
- **WAM-CP-12** — determinism detection → CP elision at lower-time (this is the absent "CP-elision" shape PL-HY-2 referenced).
- **PL-INDEX-L2-1** — Level-2 hash dispatch for first-arg indexing (O(1) when >8 clauses).

**Blocked on Lon:** PL-HY-1c (g_pl_flat_chain lowerer design sign-off); reclassify PL-HY-2/3/4/5.
**m4 75→86:** the 36 EXCISED rungs still need a runtime substrate (findall/retract/assertz/aggregate/
catch-throw/dcg_generate/compound+float unify) — PLG-9g / PLG-10 / WAM-CP-13.

## Build / verify recipe
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh            # GATE-1 m2 5/5
bash scripts/test_prolog_rung_suite.sh       # GATE-3 m2 111/111, m3 111/111, m4 75/0/36
bash scripts/test_gate_bb_one_box.sh ; bash scripts/test_gate_pl_no_value_stack.sh   # PASS
# var-var spot check:
printf ':- initialization(main).\nmain :- X = Y, Y = hello, write(X), nl.\n' > /tmp/vv.pl
./scrip --compile --target=x86 /tmp/vv.pl 2>/dev/null </dev/null | grep -c rt_pl_unify_var_var   # 1
git -C /home/claude/corpus checkout -- programs/prolog/*.s   # suite regenerates .s; re-clean
```
Authors: LCherryholmes · Claude Opus 4.8
