# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 66, 2026-06-24)

**Gate: M3 124/3 XFAIL=0 NOREF=2. M4 124/3 ASMFAIL=0.** (NOREF=2: `chararr_probe` has no `.ref`; `recursion` has no `.ref`. `realparam` false-passes — its `.ref` is 1 byte `\n`; correct value `       3.0`; probe crashes rc=134.)

**What landed this session (SCRIP `cd4672a`):** `emit_bb.c` — fixed nested descriptor-arith representation mismatch. When a `IR_BINOP_GVAR_ARITH_SLOT` Arm-2 arith node has an operand that itself is a descriptor-producing nested arith BINOP (e.g. the `a.x*b.x` sub-product in `dot := a.x*b.x + a.y*b.y`), that operand's result lives in a 16-byte descriptor slot (tag@+0, value@+8 via `rt_num_arith`), but the Arm-2 read was using offset +0 (the tag field), yielding `6+6=12` instead of `3+8=11`. New `arith_emits_descr()` helper mirrors the dispatcher's Arm-1-vs-Arm-2 choice exactly: a BINOP emits a descriptor iff `bb_arith_is_dynamic` is true and *both* of its operands are call/idx-kind (or are themselves descriptor-emitting). When an Arm-2 operand satisfies this, its kind is normalized to `IR_CALL` so the existing `+8` value-read fires. Routing unchanged; bare-int chain (gvar/literal operands) untouched. Validated: SNOBOL feature `.s` 0/153 changed, SNOBOL bench OK=15/FAIL=0 identical, Prolog parity 115/0 identical, no Icon path hit, template byte-identity unchanged. M3/M4 123/4→124/3. `recparam3` CLOSED.

**Closed this session:** `recparam3` (`dot := a.x*b.x + a.y*b.y` — nested product sum over record fields).

**NEXT FRONTIERS (priority order):**

1. **Flat assign-RHS arith: gvar + call operand (Arm-2 bare-int vs IR_ASSIGN descriptor consumer).** `s := s + a[j]` → blank/"TABLE"/segfault. Affects `arr2dtype`, `arr2dtype2`, `arrparam`. Root cause fully diagnosed: the `IR_BINOP_GVAR_ARITH_SLOT` Arm-2 writes a **bare int** to slot+0, but the consuming `IR_ASSIGN` (via `flat_drive_gvar_assign_binop`, `emit_bb.c:3327`) reads that slot as a full **tagged descriptor** (`+0`=tag→rbx+0, `+8`=value→rbx+8), so the tag field receives the numeric result and the value field is garbage. This differs from the nested-product case (which was an Arm-2 *read* offset bug, not an Arm-2 *write* representation bug). The `t := t + f + 2` case works because its terminal assign hardcodes `mov [rbx+0],6` (DT_I) — but the gvar-assign-binop path does not. Fix shape: make the gvar-assign-binop path apply the DT_I tag when the RHS BINOP took Arm-2 (bare int), OR make Arm-2 write a full descriptor. The latter is principled but touches Arm-2's shared representation; beware cross-language regression — the fix landed in this session's early attempt regressed `alphacmp/enum2/pb33/pb34/pb35` until the correct `arith_emits_descr` predicate was applied. The flat case needs an analogous "Arm-2 output is bare int, not descriptor" signal at the assign consumer.

2. **`realparam.ref` gate-integrity fix.** Ref is 1 byte `\n`; correct value `       3.0`. Probe crashes rc=134 (`flat_drive_assign` missing α, real-valued fn param). Fix: update ref and treat as genuine crash.

3. **pcom self-compilation (deeper, after floor is real).** `var x: integer;` raises spurious `error(103)` from `searchid` — pointer-BST symbol table corrupts at scale. `procedure` decl segfaults rc=139 M3+M4.

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
