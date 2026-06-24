# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 64, 2026-06-24)

**Gate unchanged: M3 127/0 XFAIL=1, M4 127/0 XFAIL=1.** No code landed this session — diagnostic investigation only. pcom processes `begin end.` correctly in both modes.

**NEXT FRONTIERS (priority order):**

1. **pcom hangs (98% CPU, silent spin) on `const` decl — MODE-INDEPENDENT.**
   Repro: `printf 'program t(output);\nconst n=3;\nbegin end.\n' | scrip --run pcom.pas` → rc=124 timeout; same in M4. `var`/`type`/`begin-end` complete normally.
   **Diagnosis (Session 64):** NOT the `lcp^.values:=lvalu` nested-aggregate store (earlier theory). Capped-counter marker trace localizes the spin to `insymbol`'s `number:` case arm (pcom.pas l.425): the `repeat i:=i+1; if i<=digmax then digit[i]:=ch; nextch until chartp[ch]<>number` loop body runs up to but not including the `nextch` call — everything from `nextch` onward is dropped and the arm re-enters. `ch` stays `='3'` forever.
   **Key facts:**
   - `--dump-ir` on pcom: clean, zero warnings. Lowering is fine; defect is emitter-side.
   - `insymbol` IR: n=611 nodes, nslots=7; `i`/`digit`/`k` are `IR_VAR_FRAME` slots.
   - The *same* `number:` arm scans `3` correctly during statement parsing (`i:=3` lists fine). Identical emitted code, different runtime outcome → **call-chain-depth–dependent frame/state divergence**.
   - `__pbt2`/`__pbt3` (the `(ch='.')or(ch='e')` materialized booleans inside insymbol) are **named globals reused across 13 procs** (`pas_mat` counter resets to 0 per-proc). `nextch` itself uses no `__pbt`.
   - 8 standalone isolation probes (4-deep nesting, packed arrays, enum conditions, pcom-exact nextch, faithful case+repeat shape, callee boolean materialization, OR-relop loop conditions) all pass. Bug is emergent from pcom's scale/shape — same family as closed CH_MAX/slotmap/64-cap frontiers.
   **Two leading suspects:** (A) `IR_VAR_FRAME` slot for `i` aliasing a parent frame at the shallower const-path call depth (`block→constdeclaration→constant→insymbol` vs deeper statement path); (B) shared-global `__pbt` clobbered by another proc on the const call stack between materialize and test. **Decisive next experiment:** instrument the emitter's frame-slot assignment for insymbol and watch whether `i`'s `[r12+off]` collides with a live parent slot specifically on the const path.

2. **`flat_drive_assign: missing α (lhs IR_VAR)` on long ASSIGN chains — MODE-INDEPENDENT.** Body of >~512 `g:=g+1` assigns aborts (rc=134). Call-chains of same length work. Far beyond pcom; deepest body-size limit.

3. **Remaining fixed caps (none affect pcom):** `emit_bb.c` arg-subchain `CH_MAX` (~l.1937, bounded by `OP_ARG_SLOT_MAX=16`) + descr-chain `CH_MAX` (~l.3218) + `FLAT_CHAIN_SET_MAX 512`. Frame arenas cannot be naive realloc (live `fb` pointers); `g_call_args[64]` low value.

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
