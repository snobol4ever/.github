# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER (Lon 2026-06-06)
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION (corrected): canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md / GOAL-RAKU-BB.md and RULES.md. ZERO BINARY emission anywhere in a `bb_*.cpp` (top level or helpers); `x86()` internals are the ONLY emitter of BINARY and TEXT.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

No language-specific logic in any BB or XA C++ template; templates dispatch on IR shape and
representation flags only. FORBIDDEN in `src/emitter/BB_templates/` + `XA_templates/`: language
enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named functions/files/dispatch arms,
hardcoded language-builtin names. Language-divergent behavior goes in the runtime (by-name dispatch)
or in LOWER (different IR shape → its own BB) — never a template arm. COMPLETION TEST: the Tier-1 grep
(`SCRIP/BB-TEMPLATES-LANG-AUDIT.md`) over both template dirs == 0.

**Repo:** SCRIP (frontend + lower) · corpus (reference at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT STATE (Session 44, 2026-06-12)

**GATE STATUS:**
- M2 (--interp): **PASS=103 FAIL=0 XFAIL=1** ✓ STABLE — must not regress
- M3 (--run):    **PASS=34 FAIL=69 XFAIL=1** — was 24/79 at session start, +10 from relop fix
- M4 (--compile): not yet measured (start here: `scrip --compile p.pas > p.s && gcc -no-pie p.s ...`)

**Git commits landed this session:**
- SCRIP: `gvar relop fix: use PEERS aux operands; extend llit/rlit for IR_LIT_NUL` (pushed)

---

## ▶ FIX 1 LANDED: gvar relop BOMB (+10 tests)

**Root cause (confirmed by IR analysis and trace):**
`gvar_stmt_operand_refs` (emit_bb.c) stack-simulates the γ-spine to wire IR_BINOP operands. For
the for-loop limit comparison (`lim_cmp`), it walks from the increment path (inc_assign → lim_var
→ lim_cmp) and wires `stk[sp-2]=inc_assign` and `stk[sp-1]=lim_var` as children. The correct
operands (lim_var=VAR(loop_var) and to_res=LIT_I(bound)) are in the PEERS aux
(set by `bb_operand_aux_set` in lower_for). With wrong children, condition 7
(`g_gvar_flat_chain && op_is_rel && bb_child0 && bb_child1 && simple`) fails because
`bb_child0 = inc_assign` (IR_ASSIGN, not LIT_I/VAR/has-slot). Falls to `flat_drive_binop_tree`
→ `IR_BINOP_RELOP` → `brr_ok()` requires `g_descr_flat_chain=1` (0 in gvar mode) → BOMB.

**Fix applied** (emit_bb.c, condition 7 in `walk_bb_flat case IR_BINOP:`):
Replaced strict `bb_child0 && bb_child1 && simple` condition with broader arm:
```c
} else if (g_gvar_flat_chain && op_is_rel) {
    int _na = 0;
    IR_t * const * _ax = g_emit_cfg ? bb_operand_aux_get(g_emit_cfg, nd, &_na) : (IR_t * const *)0;
    IR_t *_c0 = (_na >= 2 && _ax[0]) ? _ax[0] : bb_child0(nd);
    IR_t *_c1 = (_na >= 2 && _ax[1]) ? _ax[1] : bb_child1(nd);
    if (_c0 && _c1 && ((_c0->op==IR_LIT_I||_c0->op==IR_LIT_NUL)||(_c0->op==IR_VAR&&IR_LIT(_c0).sval)||bb_slot_get(_c0)>=0)
                   && ((_c1->op==IR_LIT_I||_c1->op==IR_LIT_NUL)||(_c1->op==IR_VAR&&IR_LIT(_c1).sval)||bb_slot_get(_c1)>=0)) {
        // emit IR_BINOP_GVAR_RELOP using _c0/_c1
    } else { flat_drive_binop_tree(nd, ...); }
```
Also `bb_binop_gvar_relop.cpp`: `gvr_llit/gvr_rlit` now include `IR_LIT_NUL` for nil-pointer relops.

---

## ▶ FIX 2 — NEXT PRIORITY: gvar callarg non-terminal (est. +35 tests)

**Root cause (confirmed by analysis of intparam.pas, charwrite.pas, writenl.pas):**

`gvar_callarg_admit` (emit_bb.c line 1699) and `gvar_drive_call_arg_slots` (line 1707) only
admit *terminal* arg entries: `icn_arg_entry_terminal(ae)` = true iff `ae->γ.node == NULL ||
ae->γ.node->op == IR_SUCCEED`. Every complex argument is rejected:

- `writeln(doubled(x))`: arg subgraph is `VAR(x)→CALL(doubled)→SUCCEED`. Entry=VAR(x),
  not terminal (γ→CALL). Rejected → `nadmit=0` → gvar_drive returns early → marshal_call_arg
  hits `else` path → `bb_varslot("x")` allocates FRESH (uninitialized) frame slot → writeln
  receives garbage DESCR → EMPTY output.

- `write(' ')` or `write('B')`: char literal `' '`/`'B'` lowered as `__pas_chrlit(LIT_I(32))`.
  Arg subgraph is `LIT_I(32)→CALL(__pas_chrlit)→SUCCEED`. Entry=LIT_I(32), not terminal. Same
  path → rejected → EMPTY.

- `writeln(arr[i])`: `arr_get` call is non-terminal. Rejected → EMPTY.

**ALL ~35 EMPTY-output tests share this root cause.**

**The fix** (in `gvar_drive_call_arg_slots`, lines 1707-1736 of emit_bb.c):

Replace the whole function with a version that:
1. Accepts ALL non-null entries (remove `gvar_callarg_admit` filter)
2. Tracks `res_last[i]` = last real node in γ chain per arg
3. For TERMINAL entries: keep existing `walk_bb_flat(res[i], arg_done, lbl_ω, arg_β)` + `slots[i] = bb_slot_get(res[i])`
4. For NON-TERMINAL entries: `flat_emit_arg_subchain(res[i], arg_done, lbl_ω)` + `slots[i] = bb_slot_get(res_last[i])`

```c
static void gvar_drive_call_arg_slots(IR_t *nd, bb_label_t *lbl_ω) {
    g_emit.op_arg_slot_n = 0;
    int nargs = (int)(nd ? IR_LIT(nd).ival : 0);
    IR_graph_t **subs = nd ? (IR_graph_t **)(intptr_t) IR_EXEC(nd).counter : NULL;
    if (nargs > OP_ARG_SLOT_MAX) return;
    IR_t *res[OP_ARG_SLOT_MAX]; IR_t *res_last[OP_ARG_SLOT_MAX]; int nadmit = 0;
    for (int i = 0; i < nargs; i++) {
        IR_t *ae = (subs && subs[i]) ? subs[i]->entry : NULL;
        { int guard = 0; while (ae && (ae->op == IR_SUCCEED || ae->op == IR_FAIL) && ae->γ.node && guard++ < 64) ae = ae->γ.node; }
        if (ae) {
            res[i] = ae; nadmit++;
            IR_t *last = ae; int g2 = 0;
            while (last->γ.node && last->γ.node->op != IR_SUCCEED && last->γ.node->op != IR_FAIL && g2++ < 512) last = last->γ.node;
            res_last[i] = last;
        } else { res[i] = NULL; res_last[i] = NULL; }
    }
    if (!nadmit) return;
    if (g_flat_slot_count < 16) (void)bb_slot_claim(16 - g_flat_slot_count);
    int slots[OP_ARG_SLOT_MAX];
    for (int i = 0; i < nargs; i++) {
        slots[i] = -1;
        if (!res[i]) continue;
        int id = g_flat_node_id++;
        bb_label_t *arg_done = emit_label_alloc("xgvarg%d_done", id);
        bb_label_t *arg_β    = emit_label_alloc("xgvarg%d_β",    id);
        g_gvar_callarg_live = 1;
        if (icn_arg_entry_terminal(res[i])) {
            walk_bb_flat(res[i], arg_done, lbl_ω, arg_β);
            slots[i] = bb_slot_get(res[i]);
        } else {
            flat_emit_arg_subchain(res[i], arg_done, lbl_ω);
            slots[i] = bb_slot_get(res_last[i]);
        }
        g_gvar_callarg_live = 0;
        emit_label_define_bb(arg_done);
    }
    for (int i = 0; i < nargs; i++) g_emit.op_arg_slot[i] = slots[i];
    g_emit.op_arg_slot_n = nargs;
}
```

**Why flat_emit_arg_subchain works in gvar mode:**
- When it processes CALL(doubled) (dval=3), walk_bb_flat hits the dval=3 arm which calls
  `gvar_drive_call_arg_slots` recursively for doubled's own args, then FILL → bb_call_gvar_userproc_str
  which allocates `resoff = bb_slot_alloc16(CALL_doubled)` and stores the result.
- After the chain walk, `bb_slot_get(CALL_doubled) = resoff` = the result slot.
- Similarly for CALL(__pas_chrlit): it calls `rt_call_arr("__pas_chrlit", [ord], 1)` → returns
  char DESCR → stored at resoff → `bb_slot_get(CALL_chrlit) = resoff`.
- The `slots[i]` then holds the correct result slot → marshal_call_arg copies it to argbase → 
  rt_call_arr("__pas_write/__pas_writeln", ...) → correct output.

**No regression risk:** existing terminal-entry code path is unchanged. Non-terminal path only
activates for entries that currently produce slots[i]=-1.

**Files to edit:** ONLY `src/emitter/emit_bb.c` lines 1707-1736 (the gvar_drive_call_arg_slots function).
Do NOT touch bb_call.cpp or marshal_call_arg — the existing machinery handles the rest.

---

## ▶ REMAINING 69 FAILURES — FULL CATEGORIZATION

After Fix 2 lands, the picture should shift dramatically. The post-Fix-2 estimate:

**Category A: EMPTY from non-terminal callarg (~35 tests) — FIXED BY FIX 2**
alias, arr2d, arr2d2, arr2d3, arr2dtype, arr2dtype2, arr2dtype3, arrparam, arrrec1, arrrec2,
char1, char3, charlit, chararr1, chararr2, chararr3, enumarr, enumsubarr, forward1, intparam,
m4wexpr, markrel, matmul, nestfunc, ptr1, ptr2, ptr4, ptr5, ptr6, ptr8, read1, rec1, rec2, rec3,
recparam, recparam2, recparam3, stdlib1, subarr, swap, varframe, varmix, varparam, varrec,
vartrans, with1, with2, with3

**Category B: writenl space (`write(' ')`)** — ALSO FIXED BY FIX 2 (char literal → __pas_chrlit chain)
writenl.pas: currently "helloworld" instead of "hello world"

**Category C: Boolean wrong values (~3 tests)**
boolarg.pas: `0` vs `1` — function returning boolean stored wrong
boolidx.pas: `1,1,1,1` vs `1,0,1,0` — boolean array indexing
boolptr.pas: `0` vs `1` — boolean through pointer

**Category D: char2 truncated**
char2.pas: outputs `less\nequal\ngreater` but missing final `A\nB` (char comparison partial)

**Category E: goto truncation (~3 tests)**
goto1.pas: outputs `5` but missing `15` (second value lost after goto)
goto2.pas: outputs `3\n16` but missing `1603`
goto3.pas: outputs `11` but missing `15`
Root cause: goto inside a loop body exits the graph traversal early

**Category F: Nested frame wrong values (~5 tests)**
nestvar.pas: `10` vs `11` — var param through nested frame not mutating correctly
nestvar2.pas: `5` vs `10`, nestvar3.pas: `3` vs `7` — outer frame var read from inner scope wrong
nestshadow.pas: `107` vs `7` — static link / shadowing wrong
nestrec.pas: `1` vs `11` — var param through nested frames wrong

**Category G: Set membership wrong (~4 tests)**
set2, set5, set6, set7: `0` vs expected count — `in` operator returns 0

**Category H: alphacmp char-array relop**
alphacmp.pas: `0` vs `2` — `rw[i] = id` char-array comparison wrong in gvar mode

**Category I: constreal crash**
constreal.pas: `[IBB] FATAL flat_drive_assign: lhs (α) must be IR` — LHS node is nil

**Category J: stdlib3 wrong**
stdlib3.pas: last value `0` vs `1` — `odd(n)` function wrong

**Category K: read2 wrong**
read2.pas: `0` vs `42` — reading from stdin returns 0 in --run mode

**Category L: char2 truncated (partial)**
char2.pas: gets `less\nequal\ngreater` correctly but misses char-char write at end

---

## ▶ PRIORITY ORDER AFTER FIX 2

1. **[Fix 2 — ~35+ tests] gvar_drive_call_arg_slots non-terminal** (see implementation above)
2. **[~5 tests] Nested frame wrong values** — static link chain for nestvar/nestshadow/nestrec
   Root cause: in gvar mode, outer frame variables not properly read from inner scope
3. **[~4 tests] Set membership** — `in` operator (`__pas_in`) returns 0
4. **[~3 tests] goto truncation** — graph traversal exits early on goto
5. **[~3 tests] Boolean issues** — boolarg, boolidx, boolptr
6. **[1 test] constreal crash** — flat_drive_assign lhs nil
7. **[1 test] alphacmp** — char-array relop needs string comparison in gvar mode

---

## ▶ GATE SCRIPTS (recreate in /tmp on each session)

```bash
# Mode 2 gate
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

# Mode 3 gate
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

## ▶ KEY ARCHITECTURE FACTS (gvar mode = mode 3)

- **gvar_flat_chain_build** (emit_bb.c ~3350): Pascal mode-3 path. Sets `g_gvar_flat_chain=1`,
  `g_descr_flat_chain=0`. Procedures compiled with this and registered via `rt_proc_set_fn`.
- **gvar_stmt_operand_refs** (emit_bb.c ~3222): pre-processing pass that stack-simulates the
  γ-spine to wire operand children. IR_BINOP has arity 2 → consumes 2 stack items. Problem:
  for-loop lim_cmp gets wrong children wired (inc_assign instead of to_res). FIX 1 addresses.
- **gvar_drive_call_arg_slots** (emit_bb.c ~1707): pre-evaluates CALL argument subgraphs.
  Currently only handles terminal entries. FIX 2 extends to non-terminal.
- **gvar_callarg_admit** (emit_bb.c ~1699): AFTER FIX 2 IS APPLIED, this function is no longer
  the gatekeeper. The new gvar_drive_call_arg_slots accepts all non-null entries directly.
- **lower_for** (lower_pascal.c ~274): Creates `lim_cmp` BINOP with aux via `bb_operand_aux_set`.
  Stack sim wires wrong children from inc_path. FIX 1 uses aux instead.
- **lower_binop** (lower_pascal.c ~133): ALL relops use `bb_operand_aux_set` for aux operands.
- **lower_call** (lower_pascal.c ~173): ALL function calls use dval=3.0.
- **bb_call** dispatch (BB_templates/bb_call.cpp ~482):
  - dval=3 + registered → bb_call_gvar_userproc_str → rt_call_named_proc(_sl)
  - dval=3 + NOT registered → bb_call_byname_str → rt_call_arr
- **marshal_call_arg** (bb_call.cpp ~234): dispatches by slot availability, then gvar arith/relop,
  then IR_CALL, then IR_LIT_I/S/F/NUL, then `else: bb_varslot(name)` (NV global by name).
  The `else` path allocates an UNINITIALIZED frame slot → wrong values.
- **bb_slot_alloc16 vs bb_slot_alloc**: both allocate frame slots. `alloc16` = 16-byte DESCR slot.
  The result slot of a CALL node is `bb_slot_alloc16(CALL_node)` inside the call template.
  `bb_slot_get(node)` retrieves the allocated slot for a node (-1 if not allocated).
- **IR_LIT_NUL**: nil pointer. `gvr_llit/gvr_rlit` in bb_binop_gvar_relop.cpp now include it
  (treats as value 0 for `cmp rax, rcx`).

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/SCRIP/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /tmp/run_gate.sh    # must be 103/0
bash /tmp/run_gate_m3.sh # baseline 34/69
```

---

## Mechanism inventory (how it works NOW)

- **Rail:** parser tag `LANG_PASCAL`=6, IR tag `IR_LANG_PAS`=7, body walker `lower_pascal_body`
  (`lower_program.c`). Parser emits real AST (TT_FOR/TT_REPEAT/bare-TT_IF; TT_PROC_DECL c[3]=ret-var
  iff function). LOWER dispatch: outer `switch(tree->t)` → inner `switch(cx.lang)`. Driver mode-2 =
  the `!is_icon && !is_prolog` branch in `scrip.c` → finds `main` → `IR_interp_once`.
- **Frame-as-BB:** nested frames + static links ride the parent-port thread; `[fb+0]`=SL,
  `[fb+16+k*16]`=DESCR slot k; hop chains are emit-time constants. Var params = cell addresses
  ({tag 0, ptr} DESCRs, verbatim 16-byte copy); REF kinds `IR_VAR_FRAME_REF`/`IR_ASSIGN_FRAME_REF` =
  one extra indirection. Migration trigger: `decl_level>1 || byref_mask`; main + flat programs stay NV
  (`rt_gvar_cell` gives NV globals stable cells).
- **Calls:** registered dval 2|3 → `bb_call_gvar_userproc_str` → `rt_call_named_proc(_sl)`;
  unregistered → `bb_call_byname_str` → `rt_call_arr`; DEFINE rides dval=5. `marshal_call_arg`
  γ-chases each arg subgraph to its final node; inlines CALL + nested-BINOP operands across BOTH binop
  layouts (direct α/β pointers AND the PEERS `operand_aux` sidecar — sidecar is keyed to the ARG
  SUBGRAPH's own graph, so `sg` is threaded through the marshal chain). Relop-diamond args: CMP +
  conditional INTVAL(0/1) store; TEXT internal labels keyed by `bb_node_id(relnd)`.
- **Booleans:** stored true=INTVAL(1)/false=INTVAL(0). Conditions wrap via `pas_cond` (`expr ≠ 0`);
  `and`/`or` = TT_MUL/TT_ADD (correct on 0/1 inputs); `not` = `pas_flip_rel(pas_cond)`. Relop
  assigned to a VAR or bare-funcname selector → parser statement-IF rewrite (`x:=1`/`x:=0` arms);
  other destinations (`a[i]`, `p^.f`) → `pas_bool` diamond in call-arg position, covered by the
  marshal arm. Relop as arith operand → `pas_bool_diamond` (lower.c): the diamond is HOISTED as a
  chain prefix with a bare `IR_VAR(__pbtN)` left in operand position — forced by
  `gvar_stmt_operand_refs`' stack simulation (a consumer's operands must be the most recent γ-spine
  pushes; IR_IF arity −1 = stack reset breaks any in-place diamond).
- **goto/label (PB-12):** parser → `TT_GOTO_U`(sval=label digits, strdup'd) + `TT_LABEL_DEF`(sval,
  c[0]=stmt). `lower_pascal_body` pass-1 recursively pre-registers one IR_SUCCEED landing per label
  (`bb_label_registry_*`, reset per body = per-proc scoping; both goto directions resolve). The
  `TT_LABEL_DEF` arm wires landing→γ to the inner α and exposes the LANDING as the statement's α;
  `TT_GOTO_U` lowers to an IR_SUCCEED hop with γ pinned to the landing (γ_in ignored). Zero new IR
  kinds, zero template work — m3/m4 came free. Intra-procedure only, matching pcom error 399.
- **I/O:** `__pas_writeln`/`__pas_write` take interleaved (value,width) pairs; int right-justified in
  max(w,digits), default width 10 (real 20); `:w` is a minimum. `__pas_sqr(x)`=x*x.
- **Char (PB-15):** chars stored as integer ordinals. `scalar_constant: STRINGCONST` len=1 →
  `(long long)s[0]` (for const/case/for-bounds). `factor: STRINGCONST` len=1 → `ilit(ord)`.
  `ord`/`chr` both → identity. `var c:char`/value-param `x:char` → `pas_charvar_add`. Write path:
  charvar args wrapped with `mk_chr_wrap` (→ `TT_FNC(__pas_chr, val)`) + width sentinel `-2`
  (default char width = 1). `__pas_chr` runtime: ordinal → 1-char GC string. Width `-2` →
  `fputc`; width ≥0 → `fprintf("%*s", w, s)`. Char lit in write position prints as int (no type
  info available at write call site for plain ilit). Charvar table global/unscoped (probes unaffected).
- **Arrays/records/pointers:** TT_IDX faithful in parser; LOWER → `arr_get`, `a[i]:=v` →
  `a := arr_set_pure(a,i,v)` (no auto-grow; parser prepends an init prologue sizing to high+1).
  Records = field-index arrays; `p^` = `__pas_deref`, `p^.f := v` = `__pas_field_set`,
  `new(p)` = `__pas_alloc(_rec)`. Sets = `__pas_set{,uni,int,dif}`/`__pas_in`.
- **case (PB-11):** parse-time desugar, no new IR. `case e of …` → TT_SEQ_EXPR(`__pctN := e`,
  if-chain): each arm = TT_IF(pas_cond(or-chain of `__pctN = const`), stmt) folded right-to-left into
  else slots; multi-label = TT_ADD of EQ diamonds (boolchain-proven). Temp stack depth 8 (nested
  cases), names strdup'd per leaf, counter reset per parse; labels = folded integer constants only.
- **Functions:** body ends with IR_RETURN(dval 0) whose α reads `IR_VAR(funcname)`; `f := …` writes
  the NV global (recursion-safe). Parse-time tables (reset per parse): const folding, array
  name→high, true/false→ilit(1/0), sqr→__pas_sqr.

## Target dialect — the P4 subset, NOT full ISO 7185

The language `pcom` actually compiles; spec = `pcom.pas` const block + `grammar/pascalp.y`. integer
is **16-bit maxint=32767**; real, char, boolean, enum, subrange, array, record, set (small base,
`0..58`), pointer (`new`); value + var params; nested routines; files = predefined text only; goto
intra-procedure only. Absent: first-class strings, `dispose`, later ISO. If pcom rejects a probe it
is out of scope, not a bug.

## ⚖ Provenance guardrail

The SCRIP Pascal frontend is original C. `pcom.pas`/`pint.pas` are a private behavioral oracle —
never transliterated into the lowering, never linked, never shipped. Syntax reference = the MIT
grammar; semantics = pint's observable behavior. Read what a construct means, then write the C
yourself.

## Invariants

No AST walking in modes 2/3/4. Zero C Byrd-box functions — a Pascal frame is a BB. Four ports
hard-wired (α β γ ω; static link on the parent-port thread). UPPERCASE builds IR, lowercase consumes.
THE RULE: modes 3/4 emit no byte outside a BB/SM/XA opcode via `bb_emit_x86`; `bb_bin_t` abolished.

## Where things live

| Thing | Path |
|-------|------|
| Reference compiler / P-machine (oracle) | `corpus/programs/pascal/pcom.pas` / `pint.pas` |
| Token + grammar blueprint (MIT) | `corpus/programs/pascal/grammar/pascalp.{l,y}` |
| Probes | `corpus/programs/pascal/*.pas` |
| Frontend | `src/parser/pascal/pascal.{l,y}` |
| Lowering | `src/lower/lower.c` + `lower_program.c` |
| Mode-2 interp | `src/interp/IR_interp.c` |
| BB templates (m3/m4) | `src/emitter/BB_templates/` |

Start every Pascal session by reading the reference grammar (`pascalp.l` tokens, `pascalp.y`
productions) for the constructs in play.

## ⚠ Landmines (each has cost real time)

1. `rm -f scrip` before `make scrip` — the target has no prerequisites; edits silently don't take.
2. Pascal regen ONLY via `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (1 s/r =
   dangling-else, expected). NEVER the full regen script (it deletes snobol4.lex.c).
3. `touch` templates before `make scrip` after any template edit.
4. fpc on this image: `apt-get update` first, then plain `apt-get install -y fpc`.
5. Concurrent pushes land mid-session: every `git pull --rebase` → `rm -f scrip && make` → FULL gate
   re-run. Byte-identity baselines go stale at every rebase — stash-prove against the rebased base,
   never against pre-rebase captures.
6. Never assume per-box uid for TEXT internal labels on the Pascal gvar flat chain — the whole chain
   shares one `_.x86_uid`; key labels by `bb_node_id`.
