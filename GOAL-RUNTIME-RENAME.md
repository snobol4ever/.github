# GOAL-RUNTIME-RENAME.md — Language-Independent De-Name (rename runtime/emitter symbols by CS concept)

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


**Split out of GOAL-SNOBOL4-BB.md 2026-06-02 (Lon directive) so it runs as its own session.**
This is the RENAME work (strip language tags, name by CS concept). The sibling REORG (organize files by
subsystem) is `GOAL-RUNTIME-REORG.md`. Both are MOVE/RENAME-only ⇒ behavior-neutral by construction.

Authoritative per-slice detail lives in the SCRIP `HANDOFF-*.md` files (esp.
`HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-LI-RUNTIME-DENAME-SLICE-1.md`).

---

## ⛔ SESSION START
1. Read this file in full.
2. Clone `.github`; read `PLAN.md`, `RULES.md`.
3. The five byte-identical FACT RULES (NO VALUE STACK, NO C BYRD-BOX, PER-BOX LOCAL STORAGE, SHARED-LOWERER,
   X86-64 REGISTER) live in `GOAL-SNOBOL4-BB.md` / `GOAL-ICON-BB.md` / `GOAL-PROLOG-BB.md` and apply unchanged.
4. Run `## Session Setup`. Find the first incomplete step. Do it as ONE gated slice.

---

## THE DIRECTIVE (Lon)

**The EMITTER and RUNTIME are LANGUAGE-INDEPENDENT.** Every emitter box, every runtime helper, every IR-facing name
is named by its **CS / industry-standard concept**, NOT by the source language that happens to exercise it. Strip
every language tag — `SNO`/`sno`, `ICN`/`icn`/`Icon`, `PL`/`pl`/`prolog`, `RAKU`/`raku`/`RK`/`rk`, `REB`/`rebus` —
from `src/emitter/**` + `src/runtime/**`. **WHY:** to remove the confusion that makes a session reading
`sno_flat_chain_build` while working Icon conclude "that's the other language, I'll write a new one," breeding
duplication. One concept → one name → one implementation.

**Scope:** `src/emitter/**` + `src/runtime/**`. FRONTEND `src/frontend/**` (parser/lexer) is OUT OF SCOPE — language
identity legitimately stops at the parser. **Definition-location is authoritative** — a token's *use* in runtime does
NOT make it runtime-owned (parser/driver-DEFINED symbols are held).

---

## ⛔ EXCLUSIONS — DO NOT STRIP
1. **`IR_LANG_SNO`/`IR_LANG_ICN`/`IR_LANG_PL`/`IR_LANG_RAKU` (+ bare `LANG_*`).** The shared lowerer + shared emitter
   dispatch branch on this (`switch (cx.lang)`); it NAMES the language the shared layer must know. **KEEP.**
2. **Snocone is a DIFFERENT language; `sno` ⊂ `snocone`.** `snocone`/`_snoc_*`/`snoch`/`snotypes` — stripping `sno`
   CORRUPTS them. **KEEP (no blanket `sno` sed).**
3. **`prologue`/`epilogue`** (assembly terms, not Prolog).
4. **Frontend-contract dispatch-name STRINGS** the parser mints + runtime strcmp-dispatches (`ICN_NULL`/`ICN_CASE_EQ`/
   `ICN_SCAN_*`/`__rk_jct_*`/`__rk_arr`/`set_prolog_flag`/`current_prolog_flag`) — renaming needs the out-of-scope
   frontends; the dispatch TABLE may move/rename, the string VALUES cannot.
5. **Emitted assembly LABEL-prefix / COMMENT strings** (`"icn_proc_%s"`, `"sno_flat"`, `s_comment("# BOX SNO …")`) —
   generated-output text, not source symbols; changing them risks cross-language label collisions + churns mode-4 .s.
6. **Parser/driver-DEFINED symbols** (`prolog_atom_*`, `pl_write*`, `Raku_nfa`/`raku_nfa_*`, `raku_re`,
   `g_raku_match`/`g_raku_subject`, `icn_ring_to_tree`, `has_non_sno`) and CONTRACTS-defined `STAGE2_PL_PRED_TABLE_SIZE`
   — held; suggest future DRIVER / CONTRACTS micro-slices.
7. **`RK_NFA_BB`** getenv() config-key (interface string).

---

## STATUS

**✅ EMITTER + RUNTIME DE-NAME COMPLETE (2026-06-02, Opus 4.8).** Six gated byte-identical slices cleared the WHOLE
in-scope surface:
- `a0478c4` (A) chain twins → concept-distinct (`gvar_*` global-var model / `descr_*` typed-DESCR-slot model)
- `d339c97` (B) `sno_prog_t`/`sno_stmt_t`→`prog_t`/`stmt_t`, `IR_SNO_PROG`→`IR_PROG`
- `12b820d` (C) the 49-member `rt_pl_*` runtime ABI family → `rt_*` (each builtin's own name = the CS concept;
  `rt_pl_arith`→`rt_arith` was "delete the dead value-stack `rt_arith` stub, then take the name")
- `a822f80` (D) emitter drivers by IR kind (`flat_drive_pl_*`→`conj/disj/choice/ite`, `flat_drive_alt_icn`→`gen_alt`,
  `flat_drive_icn_userproc`→`userproc`), `bb_prepare_pl`→`bb_prepare`, `codegen_pl_*`→`codegen_callee_block`/
  `codegen_clause_dispatch`, `hdr_has_pl_reg`/`reg_pl_count`→`hdr_has_reg`/`reg_count`, `XA_PL_*`→`XA_*`, rt.c const macros
- `34b1406` (E) `__rk_out`→`out_descr`, `RK_GRAM_MAX`→`GRAMMAR_MAX`, stale header guards match filenames
- `85677cb` (LI-FENCE) `scripts/test_gate_no_lang_names.sh` (teeth-verified, wired into Session Setup)

Also done earlier: `bb_rk_gather`→`bb_gather` (`0b86f9e`), `rk_marshal_call_arg`→`marshal_call_arg` (`db6d33d`),
`icn_cset_*`→`cset_*` (`a9ab14a`), `rt_pl_{unify,trail,compound_build_n,node_to_term}`→`rt_*` (`99fa787`),
`rt_icn_*`→`rt_*` (`ba6e912`), LI-0 comment purge (`062b0f9`). **No language-tagged FILENAMES** remain in
emitter/runtime.

**LI-CORE-1 done (`d8262f2`, Opus 4.8):** `SNO_INIT_fn`→`core_lib_init`. Investigation showed it was NOT
SNOBOL-specific: called unconditionally in `rt_init()` + the driver (not gated on `cx.lang==SNO`), body does
`GC_INIT`/`&ALPHABET`/monitor/trace + registers the SHARED builtin ABI (`add/sub/LT/GT/INTEGER…`) Icon and Prolog
lowered code call — the universal runtime-library init, so the `SNO_` tag actively misled (the exact directive WHY).
Blind strip to `INIT_fn` was impossible (collides with the existing shim). Dropped its now-dead `SNO_INIT_fn|SNOBOL`
carve-out from LI-FENCE ⇒ fence tightened. Gates byte-identical.

**SCOPE CORRECTION (the other names the old LI-CORE line listed are NOT in `core/` and NOT in this goal's scope):**
- `SnoRt` — emitter STRING-LITERALS only (`rt/SnoRt/init()V`, `void SnoRt::_init()`) naming the DORMANT JVM/.NET
  runtime classes (`SnoRt.j`/`SnoRt.il`). Exclusion #5 + X86-ONLY + they're backend FILENAMES. HELD.
- `SnoSaveEnt`/`SNO_SAVE_MAX`/`g_sno_save` — live in `src/interp/IR_interp.c` (mode-2 IR interpreter). OUT of the
  emitter+runtime scope — an INTERP micro-slice, not RUNTIME-RENAME.
- `SNO_LIB` — `src/driver/scrip.c` (driver-defined, exclusion #6) + dormant JS backend. OUT of scope.

**🔴 REMAINING — ONLY LI-CORE-2 (the genuine SNOBOL library):**
- [ ] **LI-CORE-2** — the SNOBOL runtime LIBRARY proper inside `src/runtime/core/` (the NV/keyword tables, the
  pattern engine, the SNOBOL builtins). This IS the SNOBOL execution model; renaming is a runtime-UNIFICATION
  question, NOT a mechanical strip. **Lon's naming decision; no blanket sed.** Coordinates with
  `GOAL-RUNTIME-REORG.md` (which dissolves `core/` by capability — "which subsystem owns the SNOBOL runtime" is the
  same question). Open Lon question from the LI-CORE-1 handoff: (a) leave the library named as-is and let REORG home
  it, or (b) unify/rename it as part of REORG.

---

## GATES (rename-only ⇒ byte-identical, EVERY commit)
```
m2 SNOBOL4 7/7 HARD · m2 Icon 12/12 HARD · m2 Prolog 5/5 HARD
prove_lower2 67 · no_bb_bin_t 0 · audit_concurrency_invariants OK · scripts/test_gate_no_lang_names.sh (LI-FENCE) holds
make scrip rc=0 AND make libscrip_rt rc=0
```
ANY gate delta = a real bug ⇒ revert. **Method:** word-boundary sed but WATCH `_str`/suffix variants; confirm target
free + no string-literal hits first; gate byte-identical after each slice; never start a rename you can't
finish+gate+commit.

---

## Session Setup
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_snobol4.sh | grep mode-2     # 7/7 HARD
bash scripts/test_smoke_icon.sh    | grep mode-2     # 12/12 HARD
bash scripts/test_smoke_prolog.sh  | grep mode-2     # 5/5 HARD
bash scripts/prove_lower2.sh       | grep -c PASS    # 67
bash scripts/test_gate_no_lang_names.sh              # LI-FENCE OK
bash scripts/audit_concurrency_invariants.sh         # OK
```

---

**Repo:** SCRIP + .github
**Watermark.** SCRIP `d8262f2` · .github this commit. (LI-CORE-1 `SNO_INIT_fn`→`core_lib_init` done + LI-FENCE tightened; only LI-CORE-2 — the genuine SNOBOL library in `core/` — pending Lon's unification decision, coordinates with RUNTIME-REORG.)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
