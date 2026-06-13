# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 49, 2026-06-13)

**GATE STATUS:**
- M2 (--interp): **PASS=103 FAIL=0 XFAIL=1** ✓ STABLE — must not regress
- M3 (--run):    **PASS=102 FAIL=1 XFAIL=1** (+5 this session, from 97)
- M4 (--compile): same templates as M3; same failures expected

**Landed this session (SCRIP commits 4c22051, 76bfab3, 03c8240): 97→102 (+5)**
- **varframe, arr2dtype, arr2dtype3** (4c22051): `g_pas_has_nesting` was declared but never set (the local `pas_has_nesting` in `lower_pascal_stage2` was computed AFTER the proc-lowering loop, so `lower_var`/`lower_assign_var` always read 0). Now `lower_pascal_stage2` pre-computes `g_pas_has_nesting` BEFORE the loop using `proc_decl_level(proc)` (decl_level not yet set at that point) and `byref_mask` (set pre-lower in polyglot.c). Both `use_frame` conditions gained `|| (g_pas_has_nesting && is_own && slot < cx->sc.nparams)`: when ANY proc in the program is nested (decl_level>1) or has a byref param, the whole program routes calls through `rt_call_named_proc_sl` which stores params in frame slots, so own value-params must be read from frames not gvars. `arrparam` is safe — its `sumvec` is decl_level=1/byref=0, so the flag stays 0 there (verified).
- **boolidx** (76bfab3): `gvar_drive_call_arg_slots` (emit_bb.c) walked the relop diamond's γ chain to `res_last`=LIT_I(1) (the true arm) and pre-computed that arm's slot — but the false arm stores INTVAL(0) to a DIFFERENT slot, so the marshalled arg always read 1. Added a `relop_diamond` detection (scan γ chain for an integer relop whose ω is LIT_I(0) and res_last is LIT_I(1)) that SKIPS pre-computation, letting `marshal_call_arg`'s existing boolean-relop arm emit a single-slot INTVAL(0/1). Mirrors the existing arith-BINOP skip.
- **forward1** (03c8240): the gvar emit loops in scrip.c (both BINARY `--run` ~line 2908 and TEXT `--compile` ~line 2613) register AND emit each proc in ONE pass, so a call to a not-yet-emitted proc saw `rt_proc_is_registered`==false and emitted `bb_call_byname_str`→`rt_call_arr`→"Undefined function". Added a forward-decl pre-registration pass before each emit loop that registers all non-main procs (entry+frame+byref) so forward references emit `rt_call_named_proc`. (The Icon/Raku `--run` path already splits register-all/emit-all; this brings the gvar path in line.)

---

## ▶ REMAINING 1 FAILURE

**alphacmp** — `array[1..8] of char` equality (`rw[i] = id`, both char arrays). M2 PASSES via `binop_apply` (lower_common.c lines 95-116): for a numeric relop (BINOP_EQ) where BOTH operands are strings at runtime (`IS_STR_fn`), it does a `memcmp` with `norm_charseq` SOH-normalization. M3 emits an INTEGER `IR_BINOP_GVAR_RELOP` (`cmp rax,rcx` on descriptor words via `rt_gvar_get_int`) — `bb_binop_gvar_relop.cpp` has NO string path. Result: M3 prints 0 0 0 (all unequal); expected 2 0 0.

**ATTEMPTED + REVERTED this session** (parser-rewrite approach): added `pas_is_wholestr` + `pas_streq_or_bin` in pascal.y to rewrite EQOP/NEOP into `__pas_streq`/`__pas_strne` TT_FNC calls when an operand is a bare whole char-array VAR, plus `__pas_streq`/`__pas_strne` runtime builtins in by_name_dispatch.c delegating to `binop_apply(BINOP_EQ,...)`. Routing through a CALL was intended to deliver full DT_S descriptors (call-arg marshalling uses NV_GET, unlike the relop's rt_gvar_get_int). BUILD was clean, M2 stayed 103/0, but M3 still printed 0 0 0 AND `__pas_streq` appeared 0× in `--compile` output — so the rewrite did not take effect in the M3 emit path (the IR_CALL was not emitted as a by-name call, OR the EQOP rule rewrite did not fire for `rw[i] = id`; M2's correctness is independent since M2 was already correct via binop_apply on plain TT_EQ). Reverted both files to keep the gate green at 102/1.

**Next investigation for alphacmp:**
1. Confirm whether the parser rewrite actually fires for `rw[i] = id` — dump the AST/IR and check for a TT_FNC("__pas_streq",…) node. The EQOP rule is `expression EQOP simple_expression`; verify `$3` for a bare `id` is a TT_VAR (not wrapped) so `pas_is_wholestr` matches, and that `pas_is_chararr("id")` is true at that parse point.
2. If the rewrite fires but M3 doesn't emit a call: trace how a 2-arg builtin IR_CALL (dval=3.0, unregistered name) with a TT_IDX (arr_get) first arg flows through walk_bb_flat IR_CALL dispatch (emit_bb.c ~2729-2755) and bb_call.cpp (~546-549). The `is_intexpr_shape` path or arg-marshalling may be diverting it.
3. Alternative (template) approach: give `IR_BINOP_GVAR_RELOP` a string arm — when an operand is a runtime DT_S descriptor, call a runtime relop helper (e.g. wrap `binop_apply`). This matches M2 exactly but touches a language-blind template (RULES: dispatch on IR shape, no language guards) — higher risk; gate carefully.
Priority: low (1 test). Do not regress the 102.



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
