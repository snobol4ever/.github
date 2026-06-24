# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 65, 2026-06-24)

**Gate: M3 123/4 XFAIL=0 NOREF=2.** (The prior "127/0" was a stale count; 127 = ref-bearing probe count, not passes. `realparam` false-passes on a whitespace-only `.ref` — fix the ref to `       3.0` and treat `realparam` as a genuine frontier-#2 crash.)

**What landed this session (SCRIP `dcd040a`):** `bb_call.cpp` — broadened `arith_kind_ok` and `arith_opnd_a/b` to route any call-kind operand (`IR_CALL`/`ir_is_call_kind`) into a temp slot via `marshal_single_call`, instead of silently gating out and collapsing to the left operand. M3 116/11→123/4. SNOBOL4 171/84 baseline-diffed — identical fail set, zero regressions.

**Closed since last session:** `const`-hang (commit `e706a9a`: `digit[]`/`strng[]` char-array backing in `insymbol` uninitialized).

**NEXT FRONTIERS (priority order):**

1. **Scalar assign-RHS arith with call+literal operand — MODE-INDEPENDENT.** `x := a[1] + 100` → blank output (rc=0); `x := a[1] + a[2]` → 7 (correct — two-call case already works). Affects `arr2dtype`, `arr2dtype2`, `arrparam`, `recparam3`. **Diagnosis:** the call-arg path fix (`bb_call.cpp`) does NOT cover the `IR_BINOP_GVAR_ARITH` / `IR_BINOP_GVAR_ARITH_SLOT` assign-RHS path (`emit_bb.c:247-253` + `bb_assign_frame*.cpp`). The blank output (not a wrong number, not a bomb) is consistent with a DT_I tag mismatch on a literal operand in that path; the call operand (`arr_get`) is already emitted correctly in the two-call case. **Decisive experiment:** dump the M4 `.s` for `x := a[1] + 100` and confirm whether `arr_get` is emitted but the literal's DT_I tag is missing from the result descriptor.

2. **`realparam.ref` gate-integrity fix.** The ref is whitespace-only (1 byte `\n`); correct value is `       3.0`. `realparam` aborts (rc=134 — frontier-#2 flat_drive_assign family) so it false-passes under string comparison and inflates the pass count by 1. Fix: update the ref and either mark it XFAIL or treat it as the genuine crash it is.

3. **pcom self-compilation (deeper, after floor is real).** `const n=3` no longer hangs; but `var x: integer;` raises spurious `error(103)` from `searchid` — pointer-BST symbol table corrupts at scale. `procedure` decl segfaults (rc=139 M3+M4). Endgame frontier.

No mode-2 `--interp` (DE-INTERP done); only `--run` (M3) and `--compile` (M4).

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
- **Booleans:** INTVAL(1/0); `pas_cond`=`expr≠0`; and/or=MUL/ADD; not=`pas_flip_rel`. **Polymorphic relop (all 6, char-array/string-aware):** `IR_BINOP_GVAR_RELOP` arm (`bb_binop_gvar_relop.cpp`) → `rt_relop_descr2`→`binop_apply`; DT_I falls to int cmp. String-type hint set by `pas_rel`/`pas_is_strtyped` (`IR_LIT.dval=1.0`) for whole char-arrays, string lits, or `TT_IDX(TT_VAR,…)` of a char-array.
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

## ⛔ FACT RULE — SESSION CLOSE REQUIRES CONFIRMED PUSH
"HANDOFF COMPLETE" (or any doneness claim) MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` shows this session's hash on origin for every touched repo. A local commit is NOT a session close — the bytes vanish with the sandbox. If push fails or credential is missing, report BLOCKED plainly and stop. The ONLY sanctioned source of a completion claim is the verbatim stdout of `bash scripts/handoff_status.sh` (auto-discovers all repos with an `origin` remote; prints `HANDOFF COMPLETE` exit-0 or `HANDOFF BLOCKED` exit-1). Paste it verbatim — never type the claim yourself.

## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN ASSISTANT PROSE AT SESSION CLOSE
At session close the assistant MUST NOT write "HANDOFF" in any self-authored sentence. It may only appear inside the pasted, unedited `handoff_status.sh` stdout. Use "session close", "session end", or "wrap-up" instead.
