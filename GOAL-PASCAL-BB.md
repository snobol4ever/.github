# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 48, 2026-06-13)

**GATE STATUS:**
- M2 (--interp): **PASS=103 FAIL=0 XFAIL=1** ✓ STABLE — must not regress
- M3 (--run):    **PASS=97 FAIL=6 XFAIL=1** (+6 this session, +63 from baseline 34)
- M4 (--compile): same templates as M3; same failures expected

**Landed this session (SCRIP commit cba8a04): nested-frame static-link hops (91→97, +6)**
- `lower_pascal.c` `lower_var`/`lower_assign_var`: compute SL hop count (scope-chain depth from `cx->sc` to the declaring `found_sc`) and store in `IR_LIT(nd).dval` for IR_VAR_FRAME / IR_VAR_FRAME_REF / IR_ASSIGN_FRAME / IR_ASSIGN_FRAME_REF. Templates already consume `op_dval` via `FOR(0,(int)_.op_dval,…)` to walk the SL chain; dval was previously always 0 so every nested proc read/wrote its OWN frame.
- `lower_pascal.c` `lower_pascal_stage2`: call `lower_pascal_enum(prog, NULL, 0)` at entry. In the M3/M4 (`sm_preamble`) path `lower_pascal()` is never called, so `g_pas_proc_list` + parent pointers were empty when `build_scope_chain` ran → nested procs saw no outer scope and emitted gvar NV_GET. (Procs are flattened to top level by the parser; `assign_parents` level-arithmetic is the source of truth for parent links — do NOT delete it.)
- `emit_bb.c` `bb_prepare`: for IR_ASSIGN_FRAME/REF with VAR_FRAME (lk=5) or VAR_FRAME_REF (lk=6) RHS, propagate the RHS node's hop count + slot into `op_a_dval`/`op_a_ival_sg` so the assign templates address the correct outer frame.
- **Fixed**: nestvar, nestvar2, nestvar3, nestfunc, nestrec, nestshadow.

---

## ▶ REMAINING 6 FAILURES

**varframe** — `outer(p:integer)` passes its value-param `p` to `bump(var n)`. `lower_var` returns `IR_VAR "p"` (gvar) for `p` because outer is decl_level=1 with `sc->outer==NULL`, `sc->byref==0`, `sc->has_children==0` → `use_frame` false. `marshal_varparam_addr`'s `IR_VAR` arm then calls `rt_gvar_cell("p")` (the global) instead of LEA-ing outer's frame slot. M3 prints junk (`7507740`) for the first writeln. Fix: outer must use a frame so `p` lives in a slot whose address can be passed by-ref. Narrow signal needed (prior session: `|| cx->sc.nparams > 0` regressed arrparam). Likely: detect that this proc passes one of its own value-params as a var-param argument and force `use_frame` for that proc's params only.

**alphacmp** — `array[1..8] of char` equality (`rw[i] = id`). Char-array relop in gvar mode wrong (all 0). Needs a string/array compare path (memcmp-style via `rt_call_arr`) instead of scalar relop.

**boolidx** — `a[0] := i > j` stores a relop result into an array slot via `arr_set_pure`. The boolean-relop marshal arm in `marshal_call_arg` isn't firing when the value flows through `arr_set_pure` (all four print 1). Needs the relop→INTVAL(0/1) arm reached for the value arg of `arr_set_pure`.

**arr2dtype, arr2dtype3** — 2D array indexing with flat-index expression where the index operands are themselves `arr_get` calls. The flat-index BINOP (`i*ncols + j`) inside an `arr_get` subgraph isn't handled by the inline-arith path when operands are CALLs. (These were reported fixed in S47 but regressed/were never green on clean build — both print 0.)

**forward1** — forward-declared procedure (`forward` keyword). M3 prints nothing. The `DEFINE`/forward registration isn't wired so `second` is callable before its body; or the forward decl produces a duplicate/empty proc_table entry. Investigate proc_table dedup and whether `forward` body is lowered.

---

## ▶ PRIORITY ORDER

1. **varframe** — own value-param passed by-ref; narrow `use_frame` fix.
2. **arr2dtype/arr2dtype3** — inline-arith path for CALL operands in flat 2D index.
3. **boolidx** — relop-value arm for `arr_set_pure` value arg.
4. **alphacmp** — char-array equality via runtime compare.
5. **forward1** — forward-decl registration.

---

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
bash /tmp/run_gate_m3.sh # baseline 76/27
```

---

## Mechanism inventory

- **Rail:** `LANG_PASCAL`=6, `IR_LANG_PAS`=7, body walker `lower_pascal_body`. Mode-2 = `!is_icon && !is_prolog` → `IR_interp_once`.
- **Frame-as-BB:** `[fb+0]`=SL, `[fb+16+k*16]`=DESCR slot k. VAR params = cell addresses (IR_VAR_FRAME_REF/IR_ASSIGN_FRAME_REF). Migration: `decl_level>1 || byref_mask`; main stays NV.
- **2D array indexing:** parser grammar rule `selector '[' expression_list ']'` for 2-element lists: creates flat index `BINOP_ADD(BINOP_MUL(i, ncols), j)` and `TT_IDX(a, flat_expr)` (2 children). Both operands of each BINOP point to the BINOP as their γ (non-linear chain). PEERS aux (`bb_operand_aux_set` in lower_binop) correctly records both operands — the ONLY place to get them. `walk_bb_flat case IR_BINOP:` wires PEERS aux → direct children when `bb_child0==NULL` using `g_emit_cfg` (saved/restored to the arg's subgraph before `flat_emit_arg_subchain`). `lc_arg_block` creates **isolated subgraphs** (separate `IR_graph_t*` from main); PEERS aux keyed to that subgraph, not main graph.
- **Calls:** dval=2.0 → `bb_call_byname_str` → `rt_call_arr`; dval=3.0 registered → `bb_call_gvar_userproc_str` → `rt_call_named_proc(_sl)`. `gvar_drive_call_arg_slots`: pre-evaluates all non-null arg entries. Terminal: `walk_bb_flat + bb_slot_get`. Non-terminal ending in CALL: `flat_emit_arg_subchain + bb_slot_get(res_last)` with `g_emit_cfg` set to arg subgraph. Non-terminal ending in arith BINOP: SKIP (leave slots[i]=-1; `marshal_call_arg` inline-arith handles correctly). `marshal_call_arg` dispatch (gvar): (1) `op_arg_slot[i]≥0` → pre-computed DESCR slot; (2) gvar inline-arith (`fin!=lf && arith_binop`) → compute + wrap DT_I; (3) gvar relop; (4) `bb_slot_get(lf)≥0` → nested slot; (5) `marshal_single_call` for terminal CALL; (6) LIT_I/S/F/NUL; (7) `bb_varslot` (BAD fallback). **Known issue**: `marshal_single_call` (called from step 5 OR from inline-arith when operand is a CALL) calls `bb_slot_alloc16(subs[j]->entry)` for argbase without going through gvar_drive_call_arg_slots → fresh empty slots → zeros.
- **Booleans:** INTVAL(1/0). `pas_cond` = `expr≠0`; and/or = TT_MUL/TT_ADD; not = `pas_flip_rel`. Relop→VAR: parser IF rewrite; other → `pas_bool` diamond.
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
