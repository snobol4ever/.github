# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION: canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / RULES.md. ZERO BINARY in any `bb_*.cpp`; `x86()` internals are the ONLY binary+text emitter.

## ⛔ LANGUAGE-BLIND BB/XA TEMPLATES
No language enums/guards in `src/emitter/BB_templates/` or `XA_templates/`; dispatch on IR shape only. Completion test: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` grep == 0.

**Repo:** SCRIP · corpus (`programs/pascal/`). **The 7th frontend.**

---

## ▶ CURRENT STATE (Session 54, 2026-06-13)

**Landed this session (SCRIP emitter + lower + parser): three pcom-porting fixes; gate watermark unchanged at 112/0 ×3 (pcom/pint are not gated — these advance their M3 compile-ability). pcom.pas now passes through three previously-fatal emit-time aborts.**
(1) **Frame-var as RHS of a global assign** (`g := nested_proc_local`): `IR_ASSIGN` whose `operands[0]` is `IR_VAR_FRAME`/`IR_VAR_FRAME_REF` was unhandled at all three dispatch layers and aborted in `flat_drive_assign` (`kind=172`). Fix = 3 coordinated edits: add `IR_VAR_FRAME`/`_REF` to the layer-1 flat dispatch (`emit_bb.c` ~2917) and layer-2 `walk_bb_node` dispatch (`emit_core.c` ~451) so both route to `flat_drive_gvar_assign`/`bb_gvar_assign`, plus a new `IR_VAR_FRAME`/`_REF` arm in `bb_gvar_assign.cpp` that loads the materialized 16-byte descriptor from `FRQ(op_a_slot)`/`FRQ(op_a_slot+8)` and calls `rt_gvar_assign_descr` (same shape as the IR_CALL arm). Template-only, language-blind. Verified M3+M4.
(2) **Recovered prior-session `g_pas_recbody_depth` field-resolution fix that was never compiled in.** `pascal.y` had the depth-guard (only call `pas_rectype_to_pend` when `g_pas_recbody_depth==0`, so a record-typed field inside a variant — e.g. `konst: (values: valu)` in `identifier` — does not clobber the enclosing record's pend list), but `rm -f scrip` leaves `pascal.tab.o` stale, so the fix wasn't in the binary. A `bison -d -o pascal.tab.c pascal.y` regen forced recompilation; `identifier.name` now resolves (`fi=0`). Re-validated all three gates 112/0 with the corrected parser. **LESSON: after editing `pascal.y` you MUST `bison` regen, and the rebuild must recompile `pascal.tab.o` — `rm -f scrip` alone is insufficient (it leaves the stale object).**
(3) **Unary minus in a value position.** `lower_unop` (unlike `lower_binop`) set no aux operands, so `-X` as an arg to `arr_set_pure`/`arr_get` either hit a missing-operand abort or produced an 8-byte raw int with no DT_I tag → corrupt 16-byte descriptor read by the marshaller (BINOP arith args carry the tag; UNOP did not). Fix: lower `-X` as the binary `0 - X` (`lower_pascal.c` `lower_unop`, TT_MNS only; TT_PLS/TT_NOT/TT_SIZE keep IR_UNOP), reusing the proven tag-carrying BINOP arith path. Min repros `arr[1] := -arr[1]`, `v.x := -v.x` → match M2. Gates 112/0 ×3.
(4) **Fixed a Pascal nested-proc emission regression from upstream `f9e6c02`** (SNOBOL4 DEFINE "abolish per-proc VIEW sub-graphs"). That commit routed the **Pascal** proc-emit loop (`scrip.c`) through new `gvar_flat_chain_build_at`/`_text_at` wrappers passing `proc_table[].sno_entry_idx`, which `sm_prog.c` defaults to **-1** for non-SNOBOL4 procs (intent: "resolve to `g->entry`"). But the wrappers `return NULL/1` (emit nothing) when `entry_idx < 0` — so **every Pascal proc body emitted nothing → empty output**, dropping 39 frame/nesting/param tests (M3 112→73). The fallback was in `bb_proc_entry()` but missing from the build wrappers. **Fix (`emit_bb.c`):** wrappers use `g->all[entry_idx]` only when in range, else keep `g->entry`. SNOBOL4 (`entry_idx≥0`) unchanged; verified SNOBOL4 DEFINE `DOUBLE(21)=42` M3==M4. Bisected cleanly (a06554a 112/0 → f9e6c02 73/39). **NOTE for all sessions: f9e6c02 ran SNOBOL/Icon/Prolog gates but NOT the 112-test Pascal gate — RUN ALL FOUR LANGUAGE GATES before pushing shared `emit_bb.c`/`emit_core.c`/`scrip_ir.c`/`scrip.c` changes.**

**pcom.pas NEXT BLOCKER (where to resume):** `flat_drive_assign: lhs must be IR_VAR (got kind=9 = IR_CALL)` — an `IR_ASSIGN` with **null sval** and an `IR_CALL` operand[0]. Produced in `lower_assign`'s TT_IDX path when the assignment base is not a simple variable (`bname == NULL`), e.g. nested indexed/field targets like `display[top].fname := …` (pervasive in pcom). Repro: `a[i].b := x` where `a` is an array of records. Likely fix: handle the null-sval + IR_CALL-operand assign shape in the `flat_drive_assign`/dispatch (route to the appropriate idx/field set driver instead of asserting IR_VAR). **Also still pending: an empty-procedure-call runtime bug** — calling a `begin end` proc breaks chain continuation in M3 (repros: empty proc called after a writeln, or as first stmt, silently halts the chain). pcom's `mark`/`release` (line ~300) are empty, so this matters once the compile-time aborts clear.

**GATE STATUS:**
- M2 (--interp): **PASS=112 FAIL=0 XFAIL=1** ✓ STABLE — must not regress
- M3 (--run):    **PASS=112 FAIL=0 XFAIL=1** ✓ PARITY WITH M2
- M4 (--compile): **PASS=112 FAIL=0 SKIP=0 XFAIL=1** ✓ FULL PARITY — stable across repeated runs (proper gate: `scrip --compile` → `gcc -c` → link `out/libscrip_rt.so` (`-no-pie -lscrip_rt -lgc -lm -Wl,-rpath`) → run → cmp .ref)

**M4 GATE NOTE:** `--compile` emits GAS `.intel_syntax noprefix` text — assemble+link+run before comparing to .ref. Do NOT compare the raw asm text to .ref (false-fail), and do NOT trust a watermark "M4 N/0" that wasn't produced by an assemble+link+run gate. The `/tmp/run_gate_m4.sh` recreated each session uses the link-and-run recipe above.

**Still open (next-session candidates, in priority order):**
1. **Enum `writeln`** — `pb36`/`pb37` print integer ordinals where the oracle prints the enum constant name (e.g. `blck`, `letter`). Needs a per-enum-type name table + parser tracking of enum-typed `writeln` args. Refs intentionally NOT created (would lock in wrong output).
2. **`array[char] of T`** — `chartp: array[char] of chtp` (pcom uses it heavily); char index type on arrays.
3. **CALL-vs-CALL ordering** relop (`rw[i] < rw[j]`) still on the integer fast path (carried from S51).

**Prior session (53): all three Pascal gates 106→112 (+6). Native-mode `if`-without-`else`-in-proc fix — a false `if`-without-`else` fell through to the proc FAIL port (`proc_ω`), spuriously failing the caller's stmt sequence so later stmts silently never ran. Root cause: `snoch` gvar flat-chain driver (`emit_bb.c` `codegen_gvar_flat_chain_body` ~3517) had γ→`IR_SUCCEED`→success but lacked the symmetric ω rule. One-line fix `else if (w && w->op == IR_SUCCEED) node_ω = &lbl_γ;`. Language-blind: also SNOBOL4 M3 162→168 / M4 152→158. Two sibling drivers (`xargsub` ~1846, `xchain` ~3061) share the shape, left untouched.**

**Prior session (52): M4 72→106 — `rt_proc_register` ABI fix (4-reg→3-arg SysV), landed upstream as `e089608` (this session's duplicate deduplicated by rebase).**



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

cat > /tmp/run_gate_m4.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
RT_DIR=/home/claude/SCRIP/out
SCRIP=/home/claude/SCRIP/scrip
PASS=0; FAIL=0; SKIP=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && continue
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    tmp=$(mktemp -d)
    if ! "$SCRIP" --compile "$f" > "$tmp/p.s" 2>/dev/null; then SKIP=$((SKIP+1)); rm -rf "$tmp"; continue; fi
    if ! gcc -c "$tmp/p.s" -o "$tmp/p.o" 2>/dev/null; then SKIP=$((SKIP+1)); rm -rf "$tmp"; continue; fi
    if ! gcc -no-pie "$tmp/p.o" -L"$RT_DIR" -lscrip_rt -lgc -lm -Wl,-rpath,"$RT_DIR" -o "$tmp/p.bin" 2>/dev/null; then SKIP=$((SKIP+1)); rm -rf "$tmp"; continue; fi
    got=$(timeout 6s "$tmp/p.bin" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
    rm -rf "$tmp"
done
echo "PASS=$PASS FAIL=$FAIL SKIP=$SKIP XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate_m4.sh
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
bash /tmp/run_gate.sh    # must be 106/0
bash /tmp/run_gate_m3.sh # must be 106/0
bash /tmp/run_gate_m4.sh # must be 106/0 (assemble+link+run; -no-pie). NEVER trust an M4 watermark not produced by this recipe.
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
