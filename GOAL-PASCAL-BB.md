# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes, from zero

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

**Repo:** SCRIP (frontend + lower) · corpus (reference compiler at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT STATE — READ FIRST

**Watermark — session 17 (2026-06-06): PB-9f CLOSED — record-field/heap m3-m4 wall down; the entire
Pascal probe corpus is 36/36 across m2+m3+m4** (every existing `.pas` probe green in every mode, including
the formerly-segv ptr5 and the whole rec/ptr/set families; recursion fact-7 line `7 5040 13` intact).

Root cause: `marshal_call_arg`'s inline gvar-arith arm (bb_call.cpp) admitted only LIT/VAR/FRAME operand
shapes; a BINOP arg with builtin-call operands (`arr_get`/`__pas_deref`) failed the gate and silently fell
through to ENTRY-node dispatch, marshaling the first prologue call alone as the whole arg
(left-operand-only — rec1 printed 3 = p.x). Fix, shape-only: recursive `marshal_arith_rax` + per-operand
ladders accepting LIT_I / VAR / VAR_FRAME / VAR_FRAME_REF / CALL dval 2|3|5 (via `marshal_single_call` to a
scratch slot, value read at +8) / nested arith BINOP; deep mismatches `x86_bomb`; shapes outside the set
keep the legacy silent fall-through (zero drift elsewhere). Legacy snippets + slot-allocation order kept
verbatim → byte-identity for old traffic BY CONSTRUCTION. TWO IR_BINOP layouts exist: direct α/β operand
pointers (v_det_call, lower.c:606/616) and the PEERS-RULE `operand_aux` sidecar with α/β NULL (v_binop,
lower.c:218) — the sidecar is keyed to the ARG SUBGRAPH's own graph (`lower_value_subgraph` allocs a fresh
blk), NOT `g_emit_cfg`, so `IR_graph_t * sg` is threaded through the whole marshal chain and
`arith_operands(sg,nd,&a,&b)` resolves either layout. Also fixed a pre-existing m4 label collision:
single-call marshal labels are now `bb_node_id(callnode)` instead of `_.nid` (two single-call args under
one owner box both emitted `.Lcallfn<ownerid>` — rec3's `writeln(q.x, q.y)`).

Gates: Pascal 36/36 m2+m3+m4; SNOBOL smoke 19/0 (m2 7, m3 6, m4 6); byte-identity stash-proof `sieve.s` /
`m4wexpr.s` (legacy inline-arith traffic) / sno `hello.s` / `083_define_simple_return.s` all cmp-identical
pre/post. Re-verified green after rebasing onto concurrent ICN-VAR-2 / PL-GZ-5c / BROK-0/2 / FIXUP pushes.

Mechanism inventory (terse; detail in git history + HANDOFF-*.md):
- Frame-as-BB (PB-7 model, implemented PB-9e): nested frames + static links ride the parent-port thread;
  `[fb+0]`=SL, `[fb+16+k*16]`=DESCR slot k; hop chains are emit-time constants. Var params = cell
  addresses ({tag 0, ptr} arg DESCRs, verbatim 16-byte copy, no runtime ABI change); `rt_gvar_cell` gives
  NV globals stable cells; REF kinds `IR_VAR_FRAME_REF`/`IR_ASSIGN_FRAME_REF` = one extra indirection.
  Migration trigger: `decl_level>1 || byref_mask!=0`; main stays unmigrated; flat programs untouched.
- Calls: registered dval 2.0|3.0 → `bb_call_gvar_userproc_str` → `rt_call_named_proc(_sl)`; unregistered →
  `bb_call_byname_str` → `rt_call_arr`; DEFINE rides dval=5.0. `marshal_call_arg` γ-chases each arg
  subgraph to its FINAL node, inlines nested CALL args, and inline-evaluates arith-BINOP-final chains
  (PB-9f).
- IR_WHILE/UNTIL/IF/RETURN are pure junctions under `g_gvar_flat_chain`; RETURN result rides NV
  (funcname-as-return-variable, recursion-safe). Binop templates `bb_binop_gvar_{relop,arith_slot}.cpp`:
  LIT-imm / VAR / slot operand shapes; slot disp +8 for DESCRs, +0 for raw qwords.

NEXT (candidate rungs, none blocking): (a) nested var-param hardening probes — hop>0 LEA paths supported
but only hop 0/1 gate-covered; (b) relop-final arg chains in the marshal still fall through silently
(cover or bomb); (c) `.Lcallarg%d_%d` LIT_S labels can collide for two string-arg operand calls under one
owner (no current traffic hits it); (d) LB-7-NEW below, parked on ICN-SCAN. New probes may open new walls —
the ladder stays open at PB-10. Landmine: Makefile compile rules for templates are explicit — `touch` the
template before `make scrip` or the .o may not rebuild.

---

## The Pascal rail (architecture facts that bind ongoing work)

Pascal has its own rail end-to-end: parser tag **`LANG_PASCAL`=6** (`src/parser/snobol4/scrip_cc.h`), IR tag
**`IR_LANG_PAS`=7** (`src/contracts/IR.h`), own body walker **`lower_pascal_body`** (`src/lower/lower_program.c`),
own program dispatch (`lower_program.c`). Parser emits **real AST** (no desugaring): `TT_FOR`/`TT_REPEAT`/
bare-`TT_IF`, and `TT_PROC_DECL` with `c[3]`=return-var present iff it's a function. LOWER dispatch shape is
**outer `switch(tree->t)` → inner `switch(cx.lang)`** — share an arm where behavior is identical, dedicated
arm where it diverges. `v_pascal_for` + `v_pascal_repeat` (`src/lower/lower.c`) lower **directly to IR**.
Driver mode-2 for Pascal is the `!is_icon && !is_prolog` branch in `scrip.c` → finds `main`, runs
`IR_interp_once`.

**Key design facts (PB-4/5/6):**
- **Output:** `__pas_writeln`/`__pas_write` take interleaved `(value,width)` arg pairs. Integer right-justified
  in `max(w,digits)`, default width 10 (real 20); string as-is; `:w` is a **minimum**; `__pas_writeln`
  appends `\n`. `__pas_sqr(x)`=x*x.
- **Arrays:** keep `TT_IDX` faithful in the parser; translate at LOWER on the Raku array rail — `TT_IDX` →
  `arr_get`; `a[i]:=v` → `a := arr_set_pure(a,i,v)`. `arr_set_pure` does NOT auto-grow, so the parser prepends
  an init prologue sizing the array to `high+1` SOH-packed "0" segments (raw index; slots `0..low-1` wasted).
- **Booleans:** `IR_IF` branches on `IS_FAIL_fn`. Stored booleans encode true=`INTVAL(1)`/false=`INTVAL(0)`;
  a bare-boolean condition is wrapped `expr ≠ 0` (`pas_cond`). `and`/`or` are `TT_MUL`/`TT_ADD` here so they
  wrap too.
- **Functions:** body ends with `IR_RETURN`(dval 0.0) whose `α` is `IR_VAR(funcname)`; `fact := …` writes the
  NV global, `IR_RETURN` reads it back. Correct under recursion.
- **Parse-time tables** (reset per parse): `const` folding, array name→high, `true`/`false`→`ilit(1/0)`,
  `sqr`→`__pas_sqr`.

---

## Target dialect — the P4 subset, NOT full ISO 7185

The target is the **P4 Pascal subset** — the language `pcom` actually compiles. Authoritative spec is
`pcom.pas`'s `const` block plus `grammar/pascalp.y`. Practical bounds:
- **Files:** only predefined `text` files (`input`, `output`).
- **`goto`:** intra-procedure only. **Sets:** small base type (`set of 0..58`).
- **Types:** integer (**16-bit `maxint = 32767`**), real, char, boolean, enumerated, subrange, `array`,
  `record`, `set`, pointer (`new`); value + `var` params; nested routines.
- **Absent:** first-class strings, `dispose`, later ISO niceties. If `pcom` rejects a probe, it is **out of
  scope, not a bug.**

---

## ⚖ Provenance guardrail — the SCRIP frontend stays commercial-clean

The SCRIP Pascal frontend is **original C**, written fresh. `pcom.pas`/`pint.pas` are a **private behavioral
oracle**, used only to check SCRIP's output during development — **never transliterated into the lowering,
never linked into `scrip`, never shipped.** Syntactic reference = the MIT-licensed grammar; semantic
reference = `pint`'s observable behavior + the P4 subset above. Read the reference to learn what a construct
*means*, then write the C yourself.

---

## Invariants (inherited from Command Central)

1. **No AST walking in modes 2/3/4.** Lower to IR, then interpret/emit.
2. **Zero C Byrd-box functions.** A Pascal frame is a BB, not a C function.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL; static link rides the
   parent-port thread.
6. **Builder/consumer case rule.** UPPERCASE builds IR; lowercase consumes.
16. **THE RULE.** Mode-3/4: no byte emitted unless it carries a BB/SM/XA opcode; every box is one
    `x86(...)` concat emitted by `bb_emit_x86`; `bb_bin_t` is abolished.

---

## Where things live

| Thing | Path | Role |
|-------|------|------|
| **Reference compiler** | `corpus/programs/pascal/pcom.pas` | Grammar + semantics oracle. |
| **Reference P-machine** | `corpus/programs/pascal/pint.pas` | Execution oracle. Diff SCRIP's output against it. |
| **Token + grammar blueprint** | `corpus/programs/pascal/grammar/pascalp.{l,y}` | lex tokens → `TT_*`; yacc grammar scopes the parser. (MIT.) |
| **Probes** | `corpus/programs/pascal/` | Our own Pascal probes + bootstrap writeup. |
| Pascal frontend | `src/parser/pascal/pascal.{l,y}` | Source → `TT_*` → shared AST. |
| Lowering | `src/lower/lower.c` + `lower_program.c` | Pascal AST → shared IR. |
| Mode-2 interpreter | `src/interp/IR_interp.c` | Executes the IR. |
| BB templates | `src/emitter/BB_templates/` | Modes 3/4. |

**Start every Pascal session by reading the reference grammar** (`pascalp.l` tokens, `pascalp.y` productions).

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/SCRIP/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt   # m4 runtime, out/libscrip_rt.so
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
# Reference toolchain (the oracle) — build once with Free Pascal:
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
```

Check a probe against the oracle (m2/m3; m4 = `--compile` → gcc -no-pie + out/libscrip_rt.so):
```bash
cd /home/claude/corpus/programs/pascal
./pcom < probe.pas && cp prr prd && ./pint < /dev/null   # reference output (the oracle)
/home/claude/SCRIP/scrip --interp probe.pas              # SCRIP output — must match
```

---

## The Rung Ladder

- [x] **PB-0..PB-8 + PB-6b** — the full interpreter rail (mode-2): lexer → parser → LOWER → all control
  flow, flat+nested procs/functions, records/arrays/sets/pointers/`new`. Suite green + recursion XFAIL
  (16-bit maxint). Sessions 1–9, git history.
- [x] **PB-9 — compiled BBs (modes 3/4).** Design `SCRIP/PB-9-DESIGN.md`.
  - [x] **PB-9a..9d** — seed · arith/assign/writeln(expr) · control flow (`sieve`) · flat procs/params
    (`recursion` fact-7). Sessions 11–13.
  - [x] **PB-9e (0/1/2/3)** — nested frames + static links + var params via cell addresses; frame-as-BB,
    SL on the parent-port thread. Design `SCRIP/PB-9E-DESIGN.md`; mechanism in inventory above.
    Sessions 14–16; HANDOFF-2026-06-04-OPUS48-PASCAL-BB-PB9E2-VARPARAMS.md.
  - [x] **PB-9f** — record-field/heap m3-m4 wall: inline-arith marshal accepts CALL + nested-BINOP
    operands across both binop layouts (operand_aux sidecar, sg threaded); single-call label fix.
    Session 17 (watermark above).
- [ ] **PB-10 — open.** No failing probe today; the next rung is whatever the next probe demands
  (candidates in NEXT above).

---

## The LB Ladder — LANGUAGE-BLIND BB/XA templates (Lon directive 2026-06-03)

- [x] **LB-1..8 + LB-3 + LB-FENCE — CLOSED** (sessions 13–14, SCRIP `37eefa1`/`95fdc2f`). COMPLETION TEST
  green: Tier-1 grep over `BB_templates/` + `XA_templates/` == 0. Single measured delta: raku m4
  `str_reverse` PASS→FAIL-loud (LB-1, pinned). Full matrix pins in git history (`.github` ~`965b047b`).
- [ ] **LB-7-NEW — post-audit inventory (NOT yet swept; concurrent ICN-SCAN sessions actively own these).**
  `# BOX ICN` tags in `bb_gen_scan.cpp:19,36`, `bb_keyword.cpp:23,32,43,54,64,73`, `bb_scan_any.cpp:19`,
  `bb_scan_match.cpp:20` (+ siblings `bb_scan_pos/tab/upto`). Sweep when ICN-SCAN settles, or fold into
  their next rung.
