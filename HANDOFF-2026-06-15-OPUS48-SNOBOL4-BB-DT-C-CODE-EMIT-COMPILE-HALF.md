# HANDOFF 2026-06-15 · Opus 4.8 · SNOBOL4-BB · DT_C (CODE) — COMPILE HALF LANDED

**SCRIP base `cf50707` (EVAL DT_E) + 1 commit this session: `476af37`.**
Task (Lon): "PIVOT! We have DT_E in addition to DT_P. Do DT_C (CODE) next. Same drill."

## TL;DR

DT_C's **compile half** now follows the exact DT_E drill and is LANDED + behavior-neutral.
DT_C's **execution half is NOT the same drill** — and that is a real, verified architectural
finding, not a shortcut. DT_P/DT_E are invoked by a **C-level call from a runtime function**
(`rt_dtp_run` from the match stmt; `rt_eval_run` from `EXPVAL_fn`). CODE is invoked by the
**program's own Goto control flow** (`:(L)` or `:<C>`), which is **100% baked at emit time** in
the native chain. There is **no runtime goto/label-resolution mechanism in the emitter at all** —
so the program-level `42` requires a NEW rung (a runtime goto-resolution box), staged below.

## WHAT LANDED (`476af37`) — the compile half (DT_E-drill analog)

`src/runtime/runtime_eval.c`:
- NEW `code_build_chain(s)`: `bb_pool_init()` (lazy, idempotent — lets mode-4 standalone build,
  same as `eval_build_chain`) → `sno_parse_string_ast(s, NULL)` (the **whole-program** parser;
  its latent NULL-return bug was fixed in cf50707) → `lower_snobol4(prog)` → `gvar_flat_chain_build(g)`
  → `bb_box_fn`.
- `code()` REWRITTEN: was storing the raw AST in `DT_C` (`slen=0`); now wraps the emitted
  `bb_box_fn` as **DT_C with `slen=3`** (the twin of DT_E `slen=3` = "emitted chain"), `d.ptr = fn`.
- `EXPVAL_fn` DT_C branch REWRITTEN: `slen==3` → run the chain via **`rt_eval_run`** on a dedicated
  zeroed frame buffer (`int64_t code_frame[512]`), return `NULVCL`. CODE runs for **side effects**
  (OUTPUT, gvar assigns); unlike EVAL there is no result gvar to read back. `rt_eval_run` is
  **reused, not cloned** (NO-DUPLICATED-LOGIC: "run a chain fn on a frame" is one operation; the
  value-return is simply ignored for CODE).
- `exec_code` DELETED → excised to `src/attic/runtime/runtime_eval.c` with a provenance header.
  It was the **AST-walking CODE interpreter**: it iterated `prog->c[]` and called `eval_node()` on
  every subj/pat/repl. `eval_node` is a `[B0b]` BOMB (the mode-1 AST evaluator was deleted), so the
  old CODE path **aborted at runtime**. It violated BOTH "NO AST WALKING IN MODES 2/3/4" and was
  interpreter residue (DE-INTERP-aligned).
- Vestigial `extern const char *exec_code(...)` decls dropped from `driver_globals.c`,
  `driver_private.h`, `scrip.c` (only `EXPVAL_fn` ever actually called it).

**Proof (m3==m4==sbl):** `C = CODE(' OUTPUT = 42'); OUTPUT = DATATYPE(C)` → `CODE` in all three;
the chain emits with no bomb. (Before: stored a bomb-AST.)

**Gates GREEN, non-decreasing (behavior-neutral — CODE was inert/bombing before):**
smoke M3 7/7 · M4 7/7 HARD · pat-rung M4 19/19 0-SKIP (M3 15 — pre-existing) · fence TIER1=TIER2=0.

## WHY THE EXECUTION HALF IS A SEPARATE RUNG (do-not-re-derive — all VERIFIED this session)

1. **The parser COLLAPSES `:<C>` (direct-goto-on-value) and `:(C)` (label-goto) into the IDENTICAL
   AST `:go C`.** Verified: `--dump-ast` of `X = 1 :<C>` and `X = 1 :(C)` are byte-identical
   (`... :go C`). CODE's defining semantic — "transfer to the *pointer value* held in C" — is LOST
   at parse time. So faithful `:<C>` needs either a parser mark (Bison — the careful area the EVAL
   follow-up already flagged) OR a runtime gvar-type check.
2. **`resolve(cx, name)` (lower_snobol4.c:71) returns NULL for any unknown label → the goto silently
   falls through to `nxt`** (the goto-lowering site sets `γ_tgt = ω_tgt = nxt`, lower_snobol4.c
   ~946-951). This is THE seam where a runtime goto-resolution box must be inserted.
3. **There is NO runtime goto/label-resolution in the native emitter — even INDIRECT goto `:($X)`
   is unimplemented.** Verified with a non-adjacent target:
   `X='TGT' :($X)` / `OUTPUT='FALLTHROUGH-WRONG'` / `TGT OUTPUT='INDIRECT-OK'` →
   oracle prints only `INDIRECT-OK`; SCRIP m3 AND m4 print `FALLTHROUGH-WRONG` then `INDIRECT-OK`
   (i.e. it fell through). The main program is ONE chain (`gvar_flat_chain_build(sbbg)`, called once
   as `fn(rt_frame(),0)` — scrip.c ~2782) with labels baked as chain positions; **no name→address
   table exists at runtime.**
4. Consequence: DT_P/DT_E reach their invoker via a returning **C call**; a CODE block is reached by
   a **control transfer inside the program's baked flow**. Not the same shape.

## NEXT RUNG — `:<C>`→DT_C runtime jump box (gives the program-level `42`)

LOWEST-RISK design (behavior-neutral by construction):
- At the goto-lowering site, when `resolve()` returns NULL, build a NEW IR box (e.g. `IR_GOTO_DYN`)
  carrying `{ gvar_name, nxt_fallback }` INSTEAD of falling straight through to `nxt`.
- New BB template (BOTH mediums) `bb_goto_dyn.cpp`: at runtime `NV_GET(name)`; if it is a **DT_C with
  `slen==3`** → invoke the emitted block (`rt_eval_run`-style, or `jmp` its `bb_box_fn` entry) ; ELSE
  → behave EXACTLY as today (go to `nxt`). Because existing programs' gotos resolve at compile time
  (`resolve` succeeds) the new box NEVER fires for them, and the non-DT_C else-branch preserves the
  current silent fall-through ⇒ provably behavior-neutral; gate as such.
- This covers the common case (block runs its statements then falls out the bottom → returns → main
  continues). The probe `C = CODE(' OUTPUT = 42 :(DONE)') :<C>` (DONE = the line after `:<C>`) then
  yields `42` because `nxt` IS the DONE line.
- 13-site-style checklist for the new IR kind (cf. the "stream-fn by-var kind-split = 13 sites"
  hard-won fact): `contracts/IR.h` enum + `scrip_ir.c` names · `lower_snobol4.c` goto-lowering branch
  (build `IR_GOTO_DYN` at the resolve-NULL seam) · `emit_core.c` dispatch case · new
  `BB_templates/bb_goto_dyn.cpp` (+ `bb_templates.h`) · `Makefile` RT_PIC_SRCS (+recipe) ·
  `walk_bb_flat` if it needs port wiring · `emit_per_kind_audit` if it enumerates kinds.

DEEPER rung (after the above): `:(L)` where L is a label **inside** a CODE block, plus block→main
gotos (`:(DONE)` to a SPECIFIC main label ≠ nxt). Both need a **runtime label-name→emitted-address
table for the main chain** (does not exist — see finding #3). The manual's "labels in the fragment
override main-program labels" and "falls out the bottom → program terminates" semantics live here.
This is the genuine large piece; the `:<C>` box above is the demonstrable first step.

## FILES
`src/runtime/runtime_eval.c` · `src/attic/runtime/runtime_eval.c` · `src/driver/driver_globals.c` ·
`src/driver/driver_private.h` · `src/driver/scrip.c`.

## Session Setup reminder
Build: `bash scripts/install_system_packages.sh && bash scripts/build_scrip.sh && make libscrip_rt`.
Oracle: `git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64`; `x64/bin/sbl -b f.sno`.
m4 run: `scrip --compile --target=x86 f.sno > f.s && as f.s -o f.o && gcc -no-pie f.o -Lout -lscrip_rt -Wl,-rpath,out -Wl,--allow-shlib-undefined -lm -o f.bin && ./f.bin`.
