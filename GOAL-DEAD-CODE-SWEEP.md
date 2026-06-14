# GOAL-DEAD-CODE-SWEEP.md — Deterministic dead-code elimination

**Method (now reproducible):** `SCRIP/scripts/util_gc_dead_oracle.sh` — recompiles every TU with
`-ffunction-sections -fdata-sections` (injected through the Makefile `WARN` hook, which is
concatenated into CBASE/CRT/CXXRT but NOT the link line), re-links scrip with
`-Wl,--gc-sections -Wl,--print-gc-sections`, and writes the bare dead-function list to
`/tmp/dead_current.txt`. The linker proves, from the static call graph rooted at `main` + every
address-taken symbol, which `.text.<fn>` sections are unreachable. **Re-run after every removal
batch — the list is regenerated, never hand-maintained.** Current count: **580 dead** (562 after
backend-KEEP). Down from 601 (passes 1/1b/2) → 594 → 580 (pass 3).

**Attic convention:** dead snippets → `src/attic/<mirror-path>/file.c` with provenance header.
Whole-file-dead → `git mv` to `src/attic/<mirror-path>/file.c` + drop from Makefile (RT_PIC_SRCS
list entry AND the `scrip:` recipe compile line — most dead files appear in BOTH).

## ⛔ THE CLOSED-SUBGRAPH LAW (pass-3 finding — do-not-re-derive)

`--gc-sections` removes a dead caller AND its dead callees TOGETHER (whole unreachable subtree), so
the GC-linked oracle binary always links. **But the real build does NOT use `--gc-sections`** — so
piecemeal SOURCE removal of a leaf dead TU leaves *still-compiled dead callers* referencing the gone
symbols → `undefined reference` at link. The dead set is a CLOSED SUBGRAPH; only the COMPLETE closure
is atomically removable, OR a TU proven self-contained.

**Proof it bites:** pass-3 first attempt removed 6 fully-dead TUs at once → link failed on
`bb_cap_new`/`bb_cap_new_call`/`bb_arbno_new` (referenced by dead code in `emit_bb.c`+`rt.c`),
`interp_eval_ref` (dead caller `gen_runtime.c:185`), `name_commit_value` (dead caller
`name_save.c:123`). Those 4 callers are in PARTIAL-dead files that were not moved.

**Self-contained test (the safe-removal gate):** a fully-dead TU is removable in isolation iff, after
deletion, `make scrip` links with ZERO unresolved symbols. `ld` lists ALL unresolved refs before
failing, so one failed link names every entangled symbol at once. "Fully-dead TU" (every defined fn in
the dead list) is necessary but NOT sufficient — verify the link.

## VALIDATION METHODOLOGY (3 deterministic proofs, all required before a batch lands)

1. **GC-binary gate parity** — `SCRIP=/tmp/scrip_gc` (the `--gc-sections` binary, all dead fns
   physically stripped) passes smoke + pat-rung + fence identically to baseline. Proves the strips
   don't break the exercised SNOBOL4 paths.
2. **All-6-language emit identity** — `--compile` real-vs-GC, byte-identical after normalizing the
   non-deterministic BB label numbers (`sed -E 's/bb[0-9]+_/bbN_/g'`). Proves every language's
   parser/lower/emit pipeline is unaffected. (SNOBOL4/Pascal/Snocone/Rebus identical raw; Icon/Prolog
   differ ONLY in heap-derived label numerals — normalize and they match.)
3. **Zero emitted-call intersection** — `comm -12 <emitted-call-targets> /tmp/dead_current.txt` == 0
   over a broad multi-language corpus sample. Closes the one false-positive class the static oracle
   cannot see: a runtime fn called ONLY from emitted `call rt_*` strings (scrip prints the name, never
   statically references it). Currently EMPTY — no dead symbol is an emitted call target.

After landing: rebuild scrip + libscrip_rt, re-run smoke/pat-rung/fence (HARD floors: smoke 7/7/7,
pat-rung M4 19/19 0-SKIP / M3 15/19, fence TIER1=TIER2=0), then regenerate the oracle.

## Completed removals

**Pass 1/1b/2 (2026-06-14):** see git log 8e82507 / 492bf7b / 3f3786d. smx_dead_stubs, interp_ast
stubs, interp_globals diag/step symbols, gen_runtime sm_yield, rt.c weak stubs, ast_print width fns,
**ast_clone.c whole-file→attic**, emit_core.c 11 fns→attic.

**Pass 3 (2026-06-14) — 3 self-contained whole-dead TUs → attic (14 fns); all 3 validation proofs +
all-language emit-identity vs pre-removal binary confirmed; gates green zero-regress:**
- `src/runtime/core/invoke.c` → attic — `ARGVAL_fn`, `INVOKE_fn`
- `src/parser/rebus/rebus_emit.c` → attic — `emit_decl`, `emit_tree_expr`, `emit_tree_stmt`, `ind`,
  `next_label`, `pop_loop`, `push_loop`, `rebus_emit` (Rebus pipeline uses `rebus_lower`, not this)
- `src/parser/rebus/rebus_print.c` → attic — `indent`, `print_decl`, `print_tree`, `rebus_print`
- Makefile: 6 lines dropped (3 RT_PIC_SRCS entries + 3 recipe lines).
- **NEW:** `scripts/util_gc_dead_oracle.sh` (the reproducible oracle).

**POLICY: JVM / .NET / JS / WASM backend helpers are KEPT** even when dead under X86-ONLY. The oracle
flags 18 such (`js_*`/`jvm_*`/`net_*`/`wasm_*`); filter with `grep -vE '^(js_|jvm_|net_|wasm_)'`
before excision. Do NOT remove them.

## NEXT (do-not-re-derive)

Regenerate first: `bash scripts/util_gc_dead_oracle.sh` → `/tmp/dead_current.txt` (authoritative).

**Current fully-dead TUs (whole-file candidates — but apply the self-contained link test to EACH):**
- `tree.c` (7 fns: tree_new0/append/insert/prepend/remove + 2) — untested for entanglement
- `name_t.c` (4), `bb_boxes.c` (7), `interp_ref.c` (2) — **ENTANGLED** (pass-3 link proved dead callers
  in name_save.c / emit_bb.c+rt.c / gen_runtime.c reference them). Need coordinated closure removal:
  excise the dead caller fns from those partial-dead files in the SAME commit, OR remove the whole
  closure. Build the closure from `/tmp/dead_current.txt` + caller grep before attempting.

**Partial-dead clusters (per-function excision, the bulk ~560):** old interpreter-era runtime
(`rt_pat_*`, `resolve_*`, `rt_findall`/`rt_aggregate`/meta-interp — dead since the IR-interpreter
deletion), value-stack residue (`rt_push_*`/`rt_pop_*`/`rt_vstack_*`), Prolog GZ-cell arith
(`rt_pl_is_cell`/`rt_arith_cmp_nodes`/`gz_eval_cell`), the dead lex/yy accessor families
(`*_yyget_*`/`*_yyset_*`/`yy_*` per language), dead `lower_icon`/`lower_prolog`/`lower_pascal`/
`lower_raku` entries (superseded by unified lower dispatch; files are partial-dead). Each cluster:
verify in `/tmp/dead_current.txt`, excise bodies→attic with provenance, run the 3 proofs + gates,
regenerate oracle, commit.
