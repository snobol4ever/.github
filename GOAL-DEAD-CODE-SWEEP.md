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

---

## SESSION HANDOFF (2026-06-15) — batches 1+2 landed, 68 removable remain

## ⛔ COMMITTED ≠ LANDED ≠ HANDED-OFF — `git push` OR IT NEVER HAPPENED
The build container's git is EPHEMERAL — destroyed at session end. A local `git commit` is invisible
to the next session, which clones `origin/main`. **Nothing is durable until `git push` succeeds.**
Therefore:
- NEVER report a batch "landed", gates "green for the record", or a hand-off "complete/done" until
  push is CONFIRMED for **every repo touched** (here: SCRIP **and** `.github` — they push separately).
- Confirm with: `git rev-list --count @{u}..HEAD` — must print `0` in each repo. Anything >0 means
  unpushed = not done. (`git status` saying "nothing to commit, working tree clean" does NOT mean
  pushed — it only means committed locally.)
- `git config user.name/user.email` is per-repo in this container; set it in EACH repo before
  committing (`.github` did not inherit it from SCRIP and silently failed a commit this session).
- This was violated on 2026-06-15: a hand-off was declared while all commits were local-only; the work
  would have been lost entirely had the push not been caught afterward. Push is step 0 of any hand-off.

**Oracle now: 103 dead / 18 backend-KEEP / 68 removable.** Down from 580 at session start.
Tools committed to the SCRIP repo: `scripts/util_dead_cutter.py`, `scripts/util_dead_sweep.py`.

### Landed this session (committed AND pushed to origin/main — SCRIP `2a35216..2c38d15`)
- **Batch 1 — `1308f79`**: 440 GC-proven-dead functions across 52 files → attic (interpreter-era
  runtime corpse: rt_runtime.c 81, rt.c 67, pattern_match.c 44, resolution.c 32, core.c 30,
  unification.c 29, emit_* ~30, …). 4 whole-file-dead TUs dropped from Makefile (tree.c, name_t.c,
  bb_boxes.c, interp_ref.c). All-6-language suites NON-DECREASING vs a true base-env build;
  proof-3 emitted-call ∩ dead = 0.
- **Batch 2 — `8d6d528`**: 22 single-def dead parser helpers (snobol4.lex.c / snobol4.tab.c /
  raku.tab.c / snocone_parse.tab.c). Gates green, all-lang hello matrix unchanged.

### Reusable tooling (NOW IN REPO — persists)
- `scripts/util_dead_cutter.py` — brace-aware C top-level splitter. `lex_items(src)` →
  [('func',name,text)|('sep'|'pp'|'other',...)]. VALIDATED against `nm` across arithmetic/emit_bb/
  rt_runtime/flex files. Cannot merge two functions (each body's braces balance independently) so it
  never erroneously cuts a live function; over-extracted macro/keyword "names" are harmless (never in
  the dead set). Header `static inline`s are invisible to it (correct — they live in headers).
- `scripts/util_dead_sweep.py` — `apply <commit>`: cuts dead bodies → `src/attic/<mirror>` with
  provenance, drops the preceding separator, rewrites the live file. Params via env `SWEEP_DEAD`
  (dead-name list, one per line) + `SWEEP_FILES` (files to process). `map` prints the per-file cut map.
- Oracle: `scripts/util_gc_dead_oracle.sh` → `/tmp/dead_current.txt`. Re-run after every batch.

### THE REMAINING 68 — exact plan (do-not-re-derive)
Build removable set: `grep -vE '^_Z' /tmp/dead_current.txt | grep -vE '^(js_|jvm_|net_|wasm_)'`, then
append demangled non-backend mangled names. Categories:

1. **44 prefix-renamed flex accessors** (`pascal_yy*`, `raku_yy*`, `rebus_yy*`). HAZARD: flex
   `%option prefix` macro-renames so the SYMBOL is `pascal_yyget_in` but SOURCE TEXT is `yyget_in`;
   the text-matching cutter will NOT find them by symbol. **Method:** per generated-lexer file, detect
   its prefix (common prefix of its `*_yylex` symbol in `nm`, or the `#define yyget_in <P>_yyget_in`
   lines), then for each dead symbol `<P>_yyX` cut SOURCE text `yyX` from that ONE file. Within a
   single prefixed lexer the text→symbol map is 1:1. Files: pascal.lex.c (`pascal`), raku.lex.c +
   lex.raku.c (`raku`), lex.rebus.c (`rebus`).
2. **14 unprefixed yy/input** (`yyget_in/out/leng/lineno/text/debug`, `yyset_*`, `input`, `yyunput`,
   `yy_scan_string`, `yy_init_globals`) = the UNPREFIXED symbols = **snobol4.lex.c ONLY** (snobol4's
   lexer has no prefix). Same TEXT appears in the other 4 lexers but compiles to prefixed symbols
   there — cut these **only from snobol4.lex.c** (set SWEEP_FILES to just that file), never globally.
3. **5 real multi-def ambiguities** — cut the DEAD def, KEEP the live one; verify per-TU with
   `nm /tmp/si_objs/<obj>.o`:
   - `rt_in_native_chunk` — cut ONLY the `__attribute__((weak))` stub in stmt_exec.c; rt.c strong def
     (`return g_native_chunk_depth>0`) is LIVE.
   - `collect_procs` (lower_icon.c, lower_pascal.c), `parse_expr` (icon_parse.c, snobol4.tab.c),
     `stmt_init` (interp_globals.c, scrip.c), `stmt_subj` (lower_icon.c, lower_prolog.c, lower_raku.c).
4. **4 bomb family** (`bomb_bytes`, `bomb_intern`, `bomb_text`, `u8` in emit_str.cpp) — deferred for
   FACT-RULE caution (`bomb_bytes` is the named "sole legacy exception"). They are dead so removal is
   link-safe; the rule governs NEW byte-emission sites, not retention of a dead copy. Confirm w/ Lon.
5. **1 straggler** `lower_flat_set_cap_fixup` — no verbatim source match (macro-built name or TU not
   in srcfiles scan). `grep -rn` before cutting.

### Validation protocol per batch (mandatory, all non-decreasing)
1. apply → `make scrip` → `make libscrip_rt`.
2. Floors: smoke M4 7/7 · pat-rung M4 19/19 0-SKIP · fence TIER1=TIER2=0.
3. All-language: hello matrix (snobol4/snocone/icon/prolog/raku ROW-MATCH; **rebus drift is
   PRE-EXISTING/identical-to-base — ignore**) + per-language suites (test_icon_rung_suite /
   test_prolog_rung_suite / test_raku_ir_full_suite / test_snocone_hand_suite /
   test_mode4_only_corpus_snobol4). Base-env parity dir was `/tmp/base_env/` (rebuild if gone:
   stash → make scrip + libscrip_rt → copy → pop).
4. proof-3 only if runtime (`rt_*`) names involved (the 5 multidef might): emit `--compile` over a
   6-language corpus sample, scrape `call <sym>`, intersect dead — must be 0.
5. Commit **AND `git push` (verify `git rev-list --count @{u}..HEAD` == 0 in every repo touched — see
   the ⛔ rule at the top of this section)**, then re-run oracle (fixpoint; count shrinks monotonically
   toward the 18 backend-KEEP floor). A batch is not "landed" until its push is confirmed.

### Known non-issues (do not chase)
- mode-2 (`--interp`) 0/N everywhere — IR interpreter deleted in a prior session (dead column).
- rebus mode-4 FATALs `[SBB] …main BB graph not found` at BASE too — pre-existing, not the sweep.
- icon/prolog/raku/snocone suites show stable XFAIL/EXCISED/FAIL counts identical to base.

### Completion criterion
Oracle removable count → 0 (only the 18 backend-KEEP js_/jvm_/net_/wasm_ remain), with all gates
green and all-language suites non-decreasing, **and every commit pushed to `origin/main` in both
repos** (`git rev-list --count @{u}..HEAD` == 0). Then the sweep is DONE.
