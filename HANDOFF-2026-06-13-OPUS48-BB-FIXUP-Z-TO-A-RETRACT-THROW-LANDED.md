# HANDOFF — GOAL-BB-FIXUP-Z-to-A — bb_retract_throw LANDED (18→0), cursor → bb_resolve

**Session:** Opus 4.8, lap 1, 5th session. **SCRIP @ daae44b** (commit `FIXUP bb_retract_throw: 18->0 CLEAN`, rebased on concurrent A→Z push d56de47).

## What landed
`src/emitter/BB_templates/bb_retract_throw.cpp` rewritten whole → **audit rc=0 CLEAN** (was 18 violations). Net −26 lines. One resolver sub-handler, two arms:
- **throw**: `hdr + emit_build_compound_term(ir_call_arg(pBB,0)) + mov rdi,rax + call rt_throw_term (3-arg both-medium) + jmp ω/def β/jmp ω`. The canonical builder (bb_resolve.cpp:93) handles scalar+struct+arith and uses the sealed `[rip+__]` lea internally — so the bespoke `rtt_ball_scalar` (unsealed lea + `rt_node_to_term@PLT`) and `rtt_lbl` helpers are gone.
- **retract/retractall**: bb_findall native-unsupported pattern — `g_sm_native_unsupported=1; hdr + jmp ω/def β/jmp ω` (literal Greek ports, both-medium).

Cleared: raw_bytes 6→0, medium_any 2→0, local_vars 1→0, multi_x86 →0, returns →2, helpers inlined-away.

## ⛔ PREMISE CORRECTION (the prior recipe + two prior watermarks were stale)
Prior entries said "THE FIX fixes the m3 compound-throw bug (m3=empty)." **False at HEAD.** Re-probed `catch(throw(my_err(1)),E,(write(caught(E)),nl))`:
- **m2** `--run`: `caught(my_err(1))` ✓
- **m3** `--run`: **PBB FATAL admission-abort** — "program not admitted by pl_gz_admit/pl_flat_body_root — no native blob covers it (GZ admission layer)". Not "empty"; the catch/throw program isn't admitted to native at all. This is the **admission tier** = genuinely separate subsystem (rule-5 exclusion), NOT this template.
- **m4** `--compile`→as+gcc: compiles+links, then **runtime BOMB** "lea: unsealed [rip + label] — use sealed [rip + __] (ptr,label)". From shared term-build/catch machinery (`my_err(1)` is IR_STRUCT → `emit_build_compound_term` / `bb_catch`), **not** bb_retract_throw's scalar arm.

So bb_retract_throw's throw arm is fired by **no passing native gate**. This commit is **behavior-neutral hygiene** (raw-bytes + MEDIUM_* are RULES.md absolutes that must go regardless), proven by **gate-equivalence**, NOT a functional fix. The earlier rt_throw≡rt_throw_term question is moot for landing: rt_throw (IR_interp.c:1325, no copy) and rt_throw_term (:1332, term_deref+bb_copy_term) differ, but only the latter (the path this commit uses, the one bb_findall/aggregate/atom_string already use) is canonical; neither is exercised by a passing gate.

Two prior assumptions disproven by reading, not theory:
1. **audit does NOT check CV9 (params) or CV10 (graph access)** — categories are emit_blind/neighbor_walk/bsize/raw_bytes/medium_any/emit_fmt/comments/blanks/locals/returns/helpers/sig_decls/over_col/multi_x86/bypass. rc=0 was thus reachable WITHOUT the resolver redesign the prior entries treated as blocking.
2. **`g_sm_native_unsupported` is vestigial** — whole-tree grep = writes only (bb_findall, bb_retract_throw) + def(emit_core.c:14)/decl(emit_core.h:69), **zero readers**. Doc handoffs (2026-05-29) describe a since-removed rc-134 abort consumer.

## Verification (green vs baseline)
byte_identity 4/0 · prolog m2 5/5 HARD, m3=m4 5/5 · icon m2 12/12 HARD, m3/m4 10/2 floor · bin_t 0 · handencoded 0 · vstack 3 · medium_invisible ok · sno_pat_reg HARD (TIER1+2) · snobol4-run ok · prove_lower & pl_m34_parity rc0 (both currently vacuous/dead-gate). m2 throw unchanged; m3/m4 throw abort/bomb identically (neutral). git diff = single file.
**Pre-existing reds, unchanged, NOT mine:** smoke_hello rc1 (rebus ROW-DRIFT, baseline 6/0→5/1, rebus ON HOLD per PLAN); purity rc1 (only `bb_call_write_slot.cpp:71` fprintf/abort — grep `bb_retract_throw` in purity log = 0).

## Cursor decision — ADVANCED to bb_resolve.cpp (flagged for Lon)
Advanced per (a) this file's own prior watermark condition "stays until audits rc=0 + gates green" (now met) and (b) the SOP (advance at rc=0 + green).
**⛔ NON-BLOCKING FLAG:** CV9 (params `pBB,fn,hdr`) + CV10 (`ir_call_arg`/`IR_LIT` graph access) on bb_retract_throw are **unmet and not audit-enforced**. They are dictated by the bb_resolve meta-resolver convention shared across its sub-handlers (bb_is_cmp/type_test/term_inspect/term_io/findall/retract_throw) and need the **resolver redesign** (give the builtins their own IR kinds + emit_core dispatch + bb_prepare `_.op_*` delivery, à la IR_ALT; TIER-S, multi-session). If you want the cursor HELD on bb_retract_throw until that lands, say so — I judged rc=0 sufficient to advance.

## NEXT FILE: bb_resolve.cpp (cursor is here now)
Known issues seen in passing (verify with `audit_bb_fixup_file.sh src/emitter/BB_templates/bb_resolve.cpp`):
- **Raw bytes** at the bdisp() bottom fallthrough: `if (MEDIUM_BINARY) return bytes(1,"\xE9")+u32le(0)+bytes(1,"\xE9")+u32le(0);` (the unknown-fn stub) — both-medium-ify like the unsupported pattern.
- This file DEFINES the canonical `emit_build_compound_term` (:93, both-medium, leave intact), `emit_build_conj_chain` (:25), `emit_term_from_node_bin` (:135), and the `bdisp`/`bb_resolve` dispatcher (:~145–168). It is the META-RESOLVER for IR_BUILTIN — touching its sub-handler signature is the CV9/CV10 resolver-redesign work above; doing bb_resolve's OWN hygiene (raw bytes, any MEDIUM_*, comments) is the cursor-stop task.
- bb_resolve is large and central — expect this to be a meatier stop than a leaf template.

## Session setup (verified working)
```
git config --global user.name "LCherryholmes"; git config --global user.email "lcherryh@yahoo.com"
git clone https://<TOKEN>@github.com/snobol4ever/SCRIP   # + .github
bash SCRIP/scripts/install_system_packages.sh
cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt   # libscrip_rt.so at out/
# probe: ./scrip --run f / --run f / --compile --target=x86 f (link: gcc -no-pie f.s -L$(pwd)/out -lscrip_rt ; LD_LIBRARY_PATH=$(pwd)/out)
```
Reminder: RULES.md absolute — do NOT read BB-REVAMP-TRACKER.md or unrelated goal files. Cursor handoff lives in this goal file's watermark, not the tracker.
