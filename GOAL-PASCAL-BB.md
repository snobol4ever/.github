# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 51, 2026-06-13)

**⚠ FLAGGED FOR LON — reverted a destructive upstream commit this session.**
A rebase pulled in `e50b089` ("mode3/4: enforce IR-NEVER-TOUCHED — bomb native emit at entry"), which inserted `(*(volatile char *)NULL)` at the `--compile` and `--run` entry blocks in `scrip.c`, making BOTH native modes SIGSEGV unconditionally (its own message: "RED BY DESIGN", and it references a follow-up to "purge" the entire IR-walking emitter). This broke every mode-3/4 gate (M3 1/105, M4 0/SKIP) and directly defeats this goal ("get modes 3 and 4 working"). Its premise misreads the architecture — PLAN.md states the EMITTER walks the IR graph to emit native code; RULES.md forbids **AST** walking in 2/3/4 and **SM/BB walking at RUNTIME**, not the emitter READING IR at emit time. Reverted exactly the two injected lines; an independent session converged on the same fix and the effective revert on `origin/main` is **`8b9a58e`** ("Revert mode3/4 entry bombs — emission read of IR is required & allowed"); my duplicate revert was deduplicated by rebase. Final `origin/main` = `76639bd`; all three gates rebuilt + re-verified at 106/0. **If IR-immutable enforcement is genuinely intended, do it via a compile-time gate/audit/refactor — never a runtime crash or by deleting the native emitter.**


**GATE STATUS:**
- M2 (--interp): **PASS=106 FAIL=0 XFAIL=1** ✓ STABLE — must not regress
- M3 (--run):    **PASS=106 FAIL=0 XFAIL=1** ✓ PARITY WITH M2
- M4 (--compile): **PASS=106 FAIL=0 SKIP=0 XFAIL=1** ✓ FULL PARITY (proper gate: `scrip --compile` → `gcc -c` → link `out/libscrip_rt.so` (`-lscrip_rt -lgc -lm -Wl,-rpath`) → run → cmp .ref; recipe = `corpus`'s `compile_mode4()` in `scripts/test_mode4_broad_corpus_snobol4.sh`)

**M4 GATE NOTE:** `--compile` emits GAS `.intel_syntax noprefix` text — assemble+link+run before comparing to .ref. Do NOT compare the raw asm text to .ref (false-fail). The `/tmp/run_gate_m4.sh` recreated each session uses the link-and-run recipe above.

**Landed this session (SCRIP fe009d9, 151caa1, 2c7bd6d; corpus 6abd1d34, c0bd9902, 4552cb45): 103→106 (+3 probes) — FULL char-array comparison surface in M3/M4 (all six relops × VAR/LIT_S/CALL).**
Session 50 closed only EQ/NE with ≥1 IR_CALL operand (alphacmp: `rw[i] = id`). This session generalized to the remaining char-array comparison shapes `pcom.pas` needs, all via the same type-polymorphic `rt_relop_descr2`→`binop_apply` descriptor arm (M2's SOH-normalized memcmp; DT_I falls through to integer cmp). The work is WIDENING DISPATCH GATES, not adding comparison logic.
- **`id = 'writeln '`** (char-array VAR vs **string LITERAL**), EQ/NE — was bombing `bb_binop_relop: shape mismatch`. Pascal runs on `g_gvar_flat_chain`; `bb_binop_relop`'s arms are all `g_descr_flat_chain`-gated → bomb. The LIT_S operand had no slot, so the gvar-relop inner guard fell through to `flat_drive_binop_tree`→`bb_binop_relop`. **Fix:** `emit_bb.c` admits IR_LIT_S in the gvar-relop outer guard; descriptor arm in `bb_binop_gvar_relop.cpp` gains a LIT_S sub-arm that builds a DT_S descriptor inline (lo=`DT_S`/slen0, hi=`lea [rip+sealed]`; slen0 → `binop_apply` uses strlen). LIT_S content sealed via `bb_intern_into` (rodata), distinct from `strtab_label` var-name sealing. Probe `chararrlit` (=111).
- **`a = b`** (char-array VAR vs VAR), EQ/NE — was SILENT WRONG (both whole-array DT_S collapse to 0 via `rt_gvar_get_int` on the integer fast path → `=` always true). No runtime type info at the gvar-relop dispatch, but the PARSER knows char-array identity. **Fix:** `pascal.y` `pas_rel`/`pas_is_strtyped` flag a relop node `v.ival=1` when both operands are string-typed (whole char-array VAR or string literal); `lower_pascal.c` `lower_binop` propagates the flag → `IR_LIT(op).dval=1.0` (dval was unused on IR_BINOP); `emit_bb.c` trigger reads dval==1.0 to force the descriptor arm. Probe `chararrvv` (=21).
- **`a < b` / `a >= 'lit'`** (char-array ORDERING < <= > >=) — VAR-vs-VAR took the int fast path; VAR-vs-LIT_S bombed the EQ/NE-only descriptor arm. **Fix:** `pas_rel` covers all six relops (new `pas_rel_or_set` keeps set subset/superset for LE/GE, else flags string LE/GE); `emit_bb.c` trigger restructured — `op_relop_descr` fires when op∈[LT..NE] AND both operands CALL/named-VAR/LIT_S AND (string-hint dval==1.0 OR a LIT_S operand OR session-50's EQ/NE+CALL); `bb_binop_gvar_relop.cpp` D predicate widened EQ/NE→[LT..NE] (arm body is relop-agnostic — passes op to `rt_relop_descr2`). Integer VAR-vs-VAR / VAR-vs-LIT_I stay inline. Probe `chararrord` (=707).



## ▶ GATE SCRIPTS (recreate in /tmp on each session)

```bash
cat > /tmp/run_gate.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
PASS=0; FAIL=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && { echo "SKIP (no ref): $f"; continue; }
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    got=$(timeout 6s /home/claude/SCRIP/scrip --interp "$f" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
done
echo "PASS=$PASS FAIL=$FAIL XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate.sh

cat > /tmp/run_gate_m3.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
PASS=0; FAIL=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && continue
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    got=$(timeout 6s /home/claude/SCRIP/scrip --run "$f" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
done
echo "PASS=$PASS FAIL=$FAIL XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate_m3.sh
```

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x scrip ] || { grep "error:" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /tmp/run_gate.sh    # must be 103/0
bash /tmp/run_gate_m3.sh # must be 103/0 (parity reached session 50)
```

---

## Mechanism inventory

- **Rail:** `LANG_PASCAL`=6, `IR_LANG_PAS`=7, body walker `lower_pascal_body`. Mode-2 = `!is_icon && !is_prolog` → `IR_interp_once`.
- **Frame-as-BB:** `[fb+0]`=SL, `[fb+16+k*16]`=DESCR slot k. VAR params = cell addresses (IR_VAR_FRAME_REF/IR_ASSIGN_FRAME_REF). Migration: `decl_level>1 || byref_mask`; main stays NV.
- **2D array indexing:** parser grammar rule `selector '[' expression_list ']'` for 2-element lists: creates flat index `BINOP_ADD(BINOP_MUL(i, ncols), j)` and `TT_IDX(a, flat_expr)` (2 children). Both operands of each BINOP point to the BINOP as their γ (non-linear chain). PEERS aux (`bb_operand_aux_set` in lower_binop) correctly records both operands — the ONLY place to get them. `walk_bb_flat case IR_BINOP:` wires PEERS aux → direct children when `bb_child0==NULL` using `g_emit_cfg` (saved/restored to the arg's subgraph before `flat_emit_arg_subchain`). `lc_arg_block` creates **isolated subgraphs** (separate `IR_graph_t*` from main); PEERS aux keyed to that subgraph, not main graph.
- **Calls:** dval=2.0 → `bb_call_byname_str` → `rt_call_arr`; dval=3.0 registered → `bb_call_gvar_userproc_str` → `rt_call_named_proc(_sl)`. `gvar_drive_call_arg_slots`: pre-evaluates all non-null arg entries. Terminal: `walk_bb_flat + bb_slot_get`. Non-terminal ending in CALL: `flat_emit_arg_subchain + bb_slot_get(res_last)` with `g_emit_cfg` set to arg subgraph. Non-terminal ending in arith BINOP: SKIP (leave slots[i]=-1; `marshal_call_arg` inline-arith handles correctly). `marshal_call_arg` dispatch (gvar): (1) `op_arg_slot[i]≥0` → pre-computed DESCR slot; (2) gvar inline-arith (`fin!=lf && arith_binop`) → compute + wrap DT_I; (3) gvar relop; (4) `bb_slot_get(lf)≥0` → nested slot; (5) `marshal_single_call` for terminal CALL; (6) LIT_I/S/F/NUL; (7) `bb_varslot` (BAD fallback). **Known issue**: `marshal_single_call` (called from step 5 OR from inline-arith when operand is a CALL) calls `bb_slot_alloc16(subs[j]->entry)` for argbase without going through gvar_drive_call_arg_slots → fresh empty slots → zeros.
- **Booleans:** INTVAL(1/0). `pas_cond` = `expr≠0`; and/or = TT_MUL/TT_ADD; not = `pas_flip_rel`. Relop→VAR: parser IF rewrite; other → `pas_bool` diamond. **Polymorphic relop, all six (< <= > >= = <>), char-array/string-aware:** the `IR_BINOP_GVAR_RELOP` descriptor arm in `bb_binop_gvar_relop.cpp` reconstructs both 16-byte DESCRs and calls `rt_relop_descr2`→`binop_apply` (M2's SOH-normalized string memcmp; DT_I falls through to integer cmp; the arm body passes `op_ival` straight through, so one arm serves all six relops). Operand sources: IR_CALL from slot [op_sa]/[op_sa+8]; named IR_VAR via `rt_gvar_get_descr`; IR_LIT_S built inline as DT_S (lo=DT_S/slen0, hi=`lea [rip+sealed]`, sealed via `bb_intern_into`). `emit_bb.c` sets `g_emit.op_relop_descr` when op∈[LT..NE] AND both operands ∈ {CALL, named-VAR, LIT_S} AND (string-type hint `IR_LIT(nd).dval==1.0` OR a LIT_S operand present OR EQ/NE-with-≥1-CALL). The **string-type hint** is set by the parser (`pas_rel`/`pas_is_strtyped` flag a relop AST node `v.ival=1` when both operands are whole char-array VARs or string literals) and carried `lower_binop` → `IR_LIT(op).dval=1.0`. Integer VAR-vs-VAR and VAR-vs-LIT_I keep the inline integer fast path. **Known gap:** CALL-vs-CALL ordering (`rw[i] < rw[j]`) has neither hint nor LIT_S → still integer fast path (EQ/NE-CALL trigger is EQ/NE-only); extend the hint to indexed char-array exprs if pcom needs it.
- **goto/label:** pass-1 pre-registers IR_SUCCEED landings; intra-proc only.
- **I/O:** `__pas_writeln/__pas_write` interleaved (value,width). Default int=10, real=20, char=-2.
- **Char:** ordinals. charvar args wrapped `mk_chr_wrap → TT_FNC(__pas_chr, val)`.
- **Arrays/records/pointers:** TT_IDX → `arr_get`; `a[i]:=v` → `arr_set_pure`. Records = field-index arrays. Sets = `__pas_set*/in`.
- **Functions:** body ends `IR_RETURN(dval 0)` reading `IR_VAR(funcname)`.

## Target dialect — P4 subset
`pcom.pas` + `grammar/pascalp.y`. integer=16-bit; array, record, set(0..58), pointer; value+var params; nested routines; goto intra-proc only. If pcom rejects a probe, out of scope.

## ⚖ Provenance
`pcom.pas`/`pint.pas` = behavioral oracle only — never transliterated.

## Invariants
No AST walking in modes 2/3/4. Zero C Byrd-box functions. Four ports (α β γ ω). Modes 3/4 emit no byte outside `bb_emit_x86`.

## Where things live
| Thing | Path |
|-------|------|
| Oracle | `corpus/programs/pascal/pcom.pas` / `pint.pas` |
| Grammar | `corpus/programs/pascal/grammar/pascalp.{l,y}` |
| Probes | `corpus/programs/pascal/*.pas` |
| Frontend | `src/parser/pascal/pascal.{l,y}` |
| Lowering | `src/lower/lower_pascal.c` + `lower_program.c` |
| Mode-2 interp | `src/interp/IR_interp.c` |
| BB templates | `src/emitter/BB_templates/` |

Start every Pascal session reading the reference grammar for constructs in play.

## ⚠ Landmines
1. `rm -f scrip` before `make scrip` — no prerequisites.
2. Pascal regen ONLY: `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`. NEVER full regen.
3. `touch` templates before `make scrip` after any template edit.
4. fpc: `apt-get update` first.
5. Every `git pull --rebase` → `rm -f scrip && make` → full gate re-run.
6. TEXT internal labels on gvar flat chain: shared `_.x86_uid`; key by `bb_node_id`.
7. `lc_arg_block` creates ISOLATED subgraphs (separate `IR_graph_t*`). PEERS aux is keyed to that graph. Save/restore `g_emit_cfg` around `flat_emit_arg_subchain` to use the correct graph for aux lookup.
