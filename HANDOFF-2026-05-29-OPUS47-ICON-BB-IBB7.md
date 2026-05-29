# HANDOFF 2026-05-29 — Claude Opus 4.7 — GOAL-ICON-BB IBB-7 ✅

**To:** Next operator on GOAL-ICON-BB.
**Status:** IBB-7 closed and pushed. Repos clean and pulled.
**Commits:**
- one4all `d1c55b0c` — IBB-7: write(BB_VAR) + BB_ASSIGN flat-wire — corpus 13→17 PASS.
- .github (this handoff + GOAL-ICON-BB.md pruned 608→157 + watermark + next rung) — push at end of next session per RULES.

---

## What landed

Mode-3 now flat-wires Icon variable read (`BB_VAR`) and variable assign (`BB_ASSIGN`), and string-literal push (`BB_LIT_S`) which the assign needed. The trick is **AG-PURE deep-thread**: `lower_icn.c:2057-2068` rewires the rhs of a simple-var BB_ASSIGN to participate in the outer SEQ chain (`rhs->γ = bb`) and sets `bb->ival = 1`. Same for BB_CALL deep-threading (line 2080-2093, `bb->dval = 1.0`). The flat-driver must NOT re-walk the rhs/arg0 in that case — the SEQ chain already emitted it. Initial implementation missed this and double-emitted, producing duplicate rt_arith calls (visible only via instrumentation; runtime symptom was wrong values / SEGV-via-vstack-extra).

Files touched (one4all):
- `src/runtime/rt/rt.c` — added `rt_pop_write_any_nl` (DT_I/R/S dispatch), `rt_pop_nv_set` (clean consume, no re-push).
- `src/emitter/BB_templates/bb_var.cpp` — NEW. 32-byte slab: `movabs rdi,name; movabs rax,&rt_nv_get; call rax; jmp γ; β: jmp ω`.
- `src/emitter/BB_templates/bb_assign.cpp` — NEW. 32-byte slab: `movabs rdi,name; movabs rax,&rt_pop_nv_set; call rax; jmp γ; β: jmp ω`.
- `src/emitter/BB_templates/bb_lit_scalar.cpp` — added BB_LIT_S binary arm (was pass-through). 37-byte slab: `movabs rdi,sptr; mov esi,slen; movabs rax,&rt_push_str; call rax; jmp γ; β: jmp ω`.
- `src/emitter/BB_templates/bb_call.cpp` — `is_write_intexpr` extended to include BB_VAR; trailer fptr switches to `rt_pop_write_any_nl` when arg0 is BB_VAR.
- `src/emitter/BB_templates/bb_templates.h` — declared `bb_var`, `bb_assign`.
- `src/emitter/emit_core.c` — split BB_VAR and BB_ASSIGN out of the bb_call cluster, routed to their own templates.
- `src/emitter/emit_bb.c` — `flat_drive_assign` (new), `flat_drive_call_intexpr` (extended). Both gate on the deep-thread flag (ival==1 / dval==1.0 → skip the local walk; SEQ chain already did it). `walk_bb_flat` got `case BB_VAR` (FILL) and `case BB_ASSIGN` (flat_drive_assign), plus BB_VAR in the BB_CALL shape dispatch.
- `Makefile` — added compile recipes + source list entries for bb_var.cpp and bb_assign.cpp.

---

## Gates at handoff (one4all `d1c55b0c`)

```
smoke_icon                 PASS=5 FAIL=0
smoke_prolog               PASS=5 FAIL=0
smoke_unified_broker       PASS=39 FAIL=14   (matches IBB-6 baseline)
FACT                       0
canonical-5 mode-3         5/5 byte-identical m2 vs m3
mode-3 corpus              17 PASS / 45 FAIL / 186 ABORT / 2 SEGV  (over 250 m2-OK testable)
                           baseline 13 PASS; +4 NEW (rung10_augop_augplus/augstar/augsub_mod/break_while)
                           zero regressions
```

---

## Two known SEGVs at handoff — both pre-existing latent issues

`rung26_pow_pow_expr.icn` and `rung37_augop_pow.icn`. Both involve `^` (power) producing DT_R, then `write(x)` calling `rt_pop_write_any_nl` which does `fprintf(stdout, "%g\n", d.r)`. The `%g` path uses SSE state save which requires 16-byte stack alignment. Both programs were ABORTing in baseline (`bb_call unsupported shape arg0_kind=4` — BB_VAR); my IBB-7 fix progressed them PAST the abort, exposing this latent crash. Not a regression.

Diagnostic notes (saved you the bisect):
- `fprintf("%g", d)` in a standalone C program is fine.
- During slab execution, even my STDERR debug `fprintf` with `r=%g` SEGVs — confirming SSE is involved.
- xa_flat prologue currently emits 19 bytes (`movabs r10,Δ; cmp esi,0; jne β`) with NO stack adjustment.
- Slab entered from C via `fn(NULL,0)` — C compiler at call site has rsp%16==0 → inside slab rsp%16==8. Internal `call rax` → callee enters at rsp%16==0. By the book, that's correct.
- But: `%g` consistently SEGVs. So either the model above is wrong, or glibc's variadic path has stricter requirements than re-aligned-on-call. Worth investigating with a true minimal repro: an SVG-test slab containing just `movabs rdi,fmt; movsd xmm0,[real]; movabs rax,&fprintf; call rax`.

If the alignment hypothesis is right, the fix is in `src/emitter/XA_templates/xa_flat.cpp`:
- Prologue: add `sub rsp, 8` (4 bytes: `48 83 EC 08`) after the cmp/jne block, so rsp%16==0 inside the slab body.
- Epilogue: add `add rsp, 8` (4 bytes: `48 83 C4 08`) before `ret` in both succ and fail halves.

That touches ALL slabs (every Icon program in mode-3). Verify canonical-5 stays 5/5 byte-identical-with-m2 after the change.

---

## Next rung: IBB-8

In `.github/GOAL-ICON-BB.md` under "Rungs". TL;DR ordered by yield:
1. **DT_R fprintf SEGV** — fix once and the 2 SEGV programs become FAILs/PASSes; also unblocks every future DT_R write.
2. **relop in if-condition** (~16 cases) — `flat_drive_binop_tree: missing α or β child`. Relop currently reaches binop_tree with one child missing because the cond context expects a boolean shape.
3. **every E do body** (~4 cases) — `flat_drive_every` with `bb->β` set (body subgraph).
4. **write(BB_CALL)** — write of user-proc result. Needs BB_RETURN flat-wire so user procs leave value on vstack.
5. **user-proc dispatch (non-write fn calls)** — biggest remaining ABORT cluster; needs generic `rt_call_proc(name, narg)` helper or per-proc slab + jmp table.

---

## DO NOT (still applies)

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Walk SM or BB at runtime in modes 3/4.
- Add fields to `BB_t`.

---

## Resume protocol

```bash
cd /home/claude/one4all
git pull
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS=39 (HOLD)
# canonical-5 mode-3:
for f in /tmp/c5_*.icn; do diff <(./scrip --interp "$f") <(./scrip --run "$f") || echo FAIL; done
```

Then orient via `.github/GOAL-ICON-BB.md` (now pruned to 157 lines) and continue at IBB-8.

— Opus 4.7, 2026-05-29
