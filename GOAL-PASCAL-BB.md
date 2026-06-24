# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 63, 2026-06-15)

**Two things landed: (1) the documented NEXT FRONTIER closed, (2) a realloc cap-removal sweep.**

**(1) pcom M3/M4 first-output divergence CLOSED (`scrip.c`).** ROOT CAUSE: the mode-4 gvar-flat-chain block (`scrip.c` ~2520, shared Pascal+SNOBOL4) registered each compiled proc's fn address (`rt_proc_set_fn` in `proc_startup`) via `static int pidx_buf[64]`/`peak_buf[64]` guarded `if (n_procs<64)`. pcom has **103 procs**; all 103 bodies emitted (asm had every `<name>_α`), but only the first 64 got their fn pointer bound → calling an unregistered proc in M4 → `rt_call_named_proc` can't dispatch → FAIL → caller's `cmp eax,99; je ω` drops the chain. pcom calls many procs (incl. `initscalars`) before the first listing `write`, so M4 emitted nothing. FIX: both buffers → `malloc`'d, sized `s2->proc_count`; remove `<64` guards; free after. pcom tiny now M3==M4 byte-identical. Writeup: HANDOFF-2026-06-15-PASCAL-BB-M4-PROC-STARTUP-64-CAP-FIX.md.

**CORRECTION:** the prior handoff's "M4 emits line 1 but nothing more on richer input" was a stdout-BUFFERING ARTIFACT (pcom early-exit doesn't flush M4's block-buffered `output`; M3 in-process flushes). Under `stdbuf -oL` M3==M4 byte-identical. The M4 codegen divergence is CLOSED — do NOT re-open.

**(2) Realloc sweep — fixed caps → dynamic (Lon directive: no artificial limits):**
- `scrip.c`: `pidx_buf`/`peak_buf` (Pascal M4) and `proc_names_buf[64][128]` (Icon/Raku M4, also dropped its 128-char name cap) → `malloc`'d, sized by `proc_count`; store name pointers directly (no copy).
- `rt.c`: proc registry `g_rt_gen_procs` (was [512]) and name-save `g_name_save` (was [4096]) → realloc-grown via `rt_gen_proc_grow`/`rt_name_save_grow`; removed the `>=MAX`/`>MAX→FAILDESCR` guards. Recursion ceiling `PROC_FRAME_NEST_MAX` re-tied to actual arena capacity (`ARENA_QWORDS/NEST_QWORDS`) instead of 256. Dead `RT_PROC_MAX`/`NAME_SAVE_MAX` defines removed.
- `emit_bb.c`: `codegen_gvar_flat_chain_body` (the Pascal/SNOBOL4 gvar path) `nodes[]`/`queue[]` (was `CH_MAX=512`, loud abort) → realloc-grown; abort removed; free at the single return. A 600-call body now works both modes (was the 512 abort).

**GATE: M3 127/0 XFAIL=1, M4 127/0 XFAIL=1** (was 125/0; +2 probes `manyproc.pas` [70 procs, guards the 64-cap] and `longcall.pas` [520-call body, guards the CH_MAX]). Stress N∈{65..600} procs all M3==M4; SNOBOL4 M4 corpus 166 byte-identical; Icon `hello` clean; `--strict` template-medium-invisible 0.

**NEXT FRONTIERS (priority order):**
1. **pcom terminates after line 1 on a `const` decl — MODE-INDEPENDENT** (M3==M4 byte-identical, rc=0). `program t(output); const n=3; begin end.` emits line-1 listing then returns from main early. Path: `block` constsy → `constdeclaration` → `constant`/`new(lcp,konst)`/`with lcp^ do … klass:=konst`/`enterid` drops the chain. `var`/`for`/`begin-end` run further. Hunt in M3 alone: marker-instrument `constdeclaration`, or minimal probe of `with lcp^ do … klass:=konst` write into the `identifier` record's `konst:(values:valu)` variant field + `values.ival:=N` store (echoes the nested-aggregate-store class).
2. **`flat_drive_assign: missing α (lhs IR_VAR)` on long ASSIGN chains — MODE-INDEPENDENT.** Exposed (not caused) by the CH_MAX removal: a body of >~512 `g:=g+1` assigns aborts here (was previously masked by the CH_MAX=512 abort; both rc=134, no regression). Call-chains of the same length work. Far beyond pcom; deepest body-size limit.
3. **Remaining fixed caps not yet swept** (none affect pcom/realistic Pascal): `emit_bb.c` arg-subchain `CH_MAX` (~l.1937, already bounded by `OP_ARG_SLOT_MAX=16`) + descr-chain `CH_MAX` (~l.3218, Icon/descr path) + `FLAT_CHAIN_SET_MAX 512`. The frame arenas (`g_proc_frame_nest_arena`, `g_proc_arena`) CANNOT be naive realloc (live `fb` pointers survive across recursive calls) — need chunked allocation; already 64MB/4096-deep. `g_call_args[64]` (call arity) is an array-extern shared with the churning `by_name_dispatch.c` — low value, skipped.

There is no mode-2 `--interp` anymore (DE-INTERP); only `--run` (M3) and `--compile` (M4).

---

## Session Setup
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" ); done
bash /tmp/run_gate_m3.sh # must be 127/0
bash /tmp/run_gate_m4.sh # must be 127/0 (assemble+link+run; -no-pie). NEVER trust an M4 watermark not from this recipe.
```
Gate scripts (recreate in /tmp): loop `*.pas` in `corpus/programs/pascal`, skip `pcom/pint/ppp`, XFAIL `recursion.pas`; M3 = `scrip --run f < inp` vs `f.ref`; M4 = `scrip --compile` → `gcc -c` → link `out/libscrip_rt.so` (`-no-pie -lscrip_rt -lgc -lm -Wl,-rpath`) → run vs `f.ref`.

---

## Mechanism inventory
- **Rail:** `LANG_PASCAL`=6, `IR_LANG_PAS`=7, body walker `lower_pascal_body`.
- **Frame-as-BB:** `[fb+0]`=SL, `[fb+16+k*16]`=DESCR slot k. VAR params = cell addresses (IR_VAR_FRAME_REF/IR_ASSIGN_FRAME_REF). Migration: `decl_level>1 || byref_mask`; main stays NV. var-param-of-aggregate-element uses copy-in/out (`lower_pascal.c` rewrites `genlabel(agg[i])`→`tmp:=agg[i]; genlabel(tmp); agg[i]:=tmp`).
- **2D arrays:** rule `selector '[' expr_list ']'` (2 elts) → flat `BINOP_ADD(BINOP_MUL(i,ncols),j)`, `TT_IDX(a,flat)`. PEERS aux (`bb_operand_aux_set` in lower_binop) records both operands; `walk_bb_flat case IR_BINOP` wires them when `bb_child0==NULL` using `g_emit_cfg`. `lc_arg_block` = isolated subgraph; save/restore `g_emit_cfg` around `flat_emit_arg_subchain`.
- **Calls:** dval=2.0 → `rt_call_arr`; dval=3.0 → `rt_call_named_proc(_sl)`. `marshal_call_arg` (gvar) dispatch: pre-computed DESCR slot → inline-arith(+DT_I) → relop → nested slot → terminal CALL → LIT → varslot. Known issue: `marshal_single_call` allocs fresh slots bypassing `gvar_drive_call_arg_slots` → zeros.
- **Booleans:** INTVAL(1/0); `pas_cond`=`expr≠0`; and/or=MUL/ADD; not=`pas_flip_rel`. **Polymorphic relop (all 6, char-array/string-aware):** `IR_BINOP_GVAR_RELOP` arm (`bb_binop_gvar_relop.cpp`) → `rt_relop_descr2`→`binop_apply`; DT_I falls to int cmp. String-type hint set by `pas_rel`/`pas_is_strtyped` (`IR_LIT.dval=1.0`) for whole char-arrays, string lits, or `TT_IDX(TT_VAR,…)` of a char-array. CALL-vs-CALL ordering CLOSED.
- **goto/label:** pass-1 pre-registers IR_SUCCEED landings; intra-proc only.
- **I/O:** `__pas_writeln/__pas_write` interleaved (value,width). Default int=10, real=20, char=-2.
- **Char:** ordinals; charvar args wrapped `__pas_chr`. **Arrays/records/ptrs:** TT_IDX→`arr_get`; `a[i]:=v`→`arr_set_pure`; records=field-index arrays; sets=`__pas_set*/in`; nested record-in-record stored as `\x05`-separated string in parent SOH slot (`__pas_nrec_*`). **Functions:** body ends `IR_RETURN(dval 0)` reading `IR_VAR(funcname)`.

## Target dialect — P4 subset
`pcom.pas` + `grammar/pascalp.y`. integer=16-bit; array, record, set(0..58), pointer; value+var params; nested routines; goto intra-proc only. If pcom rejects a probe, out of scope.

## ⚖ Provenance
`pcom.pas`/`pint.pas` = behavioral oracle only — never transliterated. `.ref` = SCRIP width-10 integers (from M3, value-cross-checked vs fpc), NOT fpc's unpadded ints.

## Invariants
No AST walking in modes 3/4. Zero C Byrd-box functions. Four ports (α β γ ω). Modes 3/4 emit no byte outside `bb_emit_x86`.

## Where things live
| Thing | Path |
|-------|------|
| Oracle | `corpus/programs/pascal/pcom.pas` / `pint.pas` |
| Grammar | `corpus/programs/pascal/grammar/pascalp.{l,y}` |
| Probes | `corpus/programs/pascal/*.pas` |
| Frontend | `src/parser/pascal/pascal.{l,y}` |
| Lowering | `src/lower/lower_pascal.c` + `lower_program.c` |
| BB templates | `src/emitter/BB_templates/` |

## ⚠ Landmines
1. `rm -f scrip` before `make scrip` — no prerequisites.
2. Pascal regen ONLY: `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`. NEVER full regen. After editing `pascal.y` you MUST regen AND recompile `pascal.tab.o` (`rm -f scrip` alone leaves it stale).
3. `touch` templates before `make scrip` after any template edit.
4. After ANY runtime (`by_name_dispatch.c`/`rt/`) edit: `make libscrip_rt` (M4 links the external `.so`; M2/M3 use in-process).
5. Every `git pull --rebase` → `rm -f scrip && make` → full gate re-run.
6. Run ALL four language gates before pushing shared `emit_bb.c`/`emit_core.c`/`scrip.c`.
7. `lc_arg_block` = ISOLATED subgraph; save/restore `g_emit_cfg` around `flat_emit_arg_subchain`.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
