# FINDING — THE RTCC VENEER DROPS THE DEAD r9 RELOAD, PER COMPILE, WHEN THE GVA TABLE IS EMPTY: hello.pl 7 → 0, every program WITH globals byte-identical (hq_P, 2026-09-02, s284, MODE `TRIO` read from the file)

**Row:** `rtcc-veneer-drops-the-r9-gva-reload-when-the-gva-table-is-empty` (rank 1; designed and measured pre-cut by hq_B on `f4532dea`, ruled "as a row" by ceo, owner after the cut hq_P). **Tree:** SCRIP `5a49419b` (proven on parent `9623ff55`, then rebased three times onto `bd6bacb7`, `7409bf45` and `7432838a` (pushed as `5a49419b`) — lower_icon.c, lower_pascal.c, bb_return.cpp, empty intersection with x86_asm.h — rebuilt and re-proved on each: reload counts, quad gate, ladder --to 0 on the rebased tree, and the row's DONE-WHEN incl. the board and the Icon watermark via `done` on the final one) · corpus `9c6489879` · `-O0`. **Diff:** 6 insertions / 3 deletions in `src/templates/x86/x86_asm.h`, nothing else.

## 1. The change

`r9` is `RTCC_GVA_REG`, the GVA base every SNOBOL4/Icon global read addresses through; because a C service may clobber it, the RTCC veneer reloads it from `rtccb+48` after every veneered call. `x86_rtcc_live_mask()` is the veneer mask with `RTCC_C_R9` cleared when this **compile's** `gva_count()` is 0; `x86_rtcc_clob`, `rtcc_wb` and `rtcc_rl` route through it, and every veneered-call emitter (`x86_rtcc_call`, `x86_rtcc_call_descr`, `x86_rtcc_call_descr_ops`) takes its mask from `x86_rtcc_clob` — no caller outside the header. BOTH-MEDIUM by construction: the mask parameter feeds `x86_rtcc_rl_bin` and `x86_rtcc_rl_text` alike.

**Why per compile is sound** (the thing a reviewer must be able to check): the GVA table is collected by a pass over **every** graph before any emission (`scrip.c` `gva_collect_reset` → `gva_collect_graph`/`gva_collect_icon_globals` → `gva_count`, lines 1289–1293 / 1481–1517 / 1573 / 1636 / 1779), so `gva_count()` is final when the first veneer is emitted; and every GVARQ consumer (`bb_var_global`, `bb_assign_global`, `bb_binop_gvar_arith`, `bb_call`, `bb_call_proc_staged`, `bb_define`, `bb_match_defer`, `xa_flat_sig_gq`) keys on `gva_index_of`, which cannot hit at count 0. With the count 0 the driver also emits no `rt_gva_island` setup, so `rtccb+48` never held a base to reload. ⛔ **Never per graph**: `rt_gen_spine_resume_enter` / `rt_gen_spine_pass_γ/ω` are mask-0 leaf calls in `x86_rtcc_clob_raw`, so a GVA-referencing graph resumed from a non-GVA generator graph would read an `r9` the generator's own C calls clobbered and nobody reloaded (hq_B's argument, kept verbatim in substance).

## 2. Measured (post-cut tree; every pre-cut number in the GOAL is VOID and was re-taken)

| program | `rtccb+48` before | after | `.s` diff vs before |
|---|---|---|---|
| `ladder__rung00_hello.pl` (the post-cut Prolog witness) | 7 | **0** | 7 lines removed, 0 added, 0 non-reload lines removed |
| `probe_loose_ab_undef_call.sno` (no eligible global) | 4 | **0** | 4 removed, 0 added, 0 non-reload |
| `demos/snobol4/hello/hello.sno` | 1 | **0** | 1 removed, 0 added, 0 non-reload |
| `arith_loop.sno` (globals) | 17 | 17 | byte-identical |
| `string_pattern.sno` | 24 | 24 | byte-identical |
| `ipxref.icn` · `rsg.icn` · `family_icon.icn` · `icon_parser.icn` · `icon_recognizer.icn` | 363 · 429 · 123 · 1020 · 611 | same | byte-identical, all five |

Control arms on the same tree, pre vs post: Icon all-rungs `--- Icon --run: PASS=263 FAIL=6 BADEXIT=1 XFAIL=27 MISSING=0 TOTAL=297 ---` on BOTH, FAIL/BADEXIT set identical (6 lines); ladder `--to 0` 2/2; port-trace gate PASS; quad gate PASS (5/5 seeds); Icon smoke m4 14/14; emit_no_lang OK; no_handencoded_bytes OK; template_medium_invisible OK; `strip_comments.py --check` 0. Prolog smoke 1/5 in every mode: the four reds are the **cut's own refusals**, verified by compiling each (`=` "rung 1 lands it", `is` "rung 6", multi-clause `fact/1` and `count/1` "rung 2"). `make test` on the first build: rc=0 in 744 s (m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0; optbypass watermark OK; quad gate PASS last). `make test` on the committed source (the comment block stripped, codegen-identical — `.s` of the whole control set byte-identical between the two builds): the row's computed `done` (DONE-WHEN = reload counts + gates + Icon watermark FAIL<=6/BADEXIT<=1 + SNOBOL4 board GATE OK) ran detached on the final pushed tree (SCRIP 5a49419b) and EXITED 0 -- row DONE, computed, after the push (the push went first on Lon's 'wrap it up now'; the fast arms had passed on that tree before it).

**What this is and is not.** It is an instruction-count reduction at fixed work on every program without a GVA cell (one `mov r9,[rip+rtccb+48]` per veneered call) — for Prolog that is every program, since a Prolog graph addresses no GVA cell (ARCH top table), so the ARCH page's "244 dead reloads per `nrev` compile" class is gone at the source. It is **not** a timing claim: no wall-clock or Ir number is quoted, and the pre-cut `nreverse.pl` 168 → 0 figure is void (nreverse refuses at rung 2).

## 3. Not landed from hq_B's 228-line patch, deliberately

- The four `x86_ripdisp_*` encoder forms + `XK_RIPDISP64/32`: their only consumer was the PL-DC pending-cursor poll the cut deleted. An encoder with zero consumers is the compiled-clean-changed-nothing trap; the form stays in the patch file for whoever needs `qword ptr [rip + sym+N]`.
- The `xa_flat.cpp` r12 → rax/rcx re-homes in the ICN-FR-3 zframe dc stub: Icon-only emission today (the PL-DC arms are gone), parked under Lon's PROLOG-ONLY order; the quad gate is the tripwire if a Prolog graph ever reaches that stub with an r12 scratch.

## 4. Two instrument defects found on the way

- **The row's minted DONE-WHEN could never fail.** It ended `… && tee … && grep -q REGRESS … && exit 1 || true`: `false && x || true` exits 0, so every earlier arm's failure was swallowed. Rewritten as a plain conjunction (hello 0 · probe 0 · arith_loop > 0 · ipxref > 0 · strip_comments · emit_no_lang · quad gate · ladder --to 0 · Icon watermark FAIL ≤ 6 BADEXIT ≤ 1 · board GATE OK), proven to exit 1 on HEAD (no `x86_rtcc_live_mask`) and 1 in an empty directory.
- **`strip_comments.py --check` is the zero-comment law's enforcement, and it caught me**: the explanatory block I first wrote above `x86_rtcc_live_mask` was the one file of 382 carrying a comment. The explanation lives here and in the commit message instead; the header carries only the separator form.

## 5. Open

- Whether any rtx asm routine reads `r9` as the GVA base on a path reachable from a no-global program: none is emitted-side (the board and Icon watermark say so on this tree); an asm-side read would be a defect in that routine, not in the mask.
