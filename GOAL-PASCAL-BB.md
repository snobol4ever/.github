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

**Watermark — session 21 (2026-06-06, Opus 4.8): PB-10a2 LANDED in TWO rungs, the second superseding the
first's mechanism. The boolean story is CLOSED IN ALL MODES.** Gate at close: **m2 44/1, m3 44/1,
m4 44/1 — UNIFORM**, the single fail being the recursion maxint pin, over 45 probes (+boolchain).
boolmix + boolchain oracle-exact m2/m3/m4; chains in if-condition position with proc calls verified all
modes. SNOBOL smoke 19/0. sieve.s + m4wexpr.s byte-identical vs the rebased base (stash-proven; the
HY-7d/7e concurrent push moved those baselines — old captures are stale, re-baseline after any rebase).

PB-10a2 mechanism v2 (`pas_bool_diamond`, lower.c — supersedes the same-session ring-mode IR_IF join,
which was m2-only): for `cx.lang==IR_LANG_PAS`, a RELATIONAL child of ANY v_binop lowers as the proven
statement-IF shape — relop γ→IR_LIT_I(1)→IR_ASSIGN(__pbtN), ω→IR_LIT_I(0)→IR_ASSIGN(__pbtN) — with the
diamond HOISTED AS A CHAIN PREFIX before the expression and a bare `IR_VAR(__pbtN)` left in operand
position. WHY the hoist (the m3/m4 FACT that forced it): `gvar_stmt_operand_refs` (emit_bb.c:2732)
resolves gvar-chain binop α/β by a STACK SIMULATION over the γ-spine (`gvar_chain_arity` pops/pushes per
node) — a consumer's operands must be the MOST RECENT pushes, so any in-place diamond interleaves junk
pushes (the relop, the arm assign) between sibling operand pushes and breaks every multi-operand case;
IR_IF has arity -1 = stack reset, which is why v1's join left the outer ADD with α=β NULL → raw IR_BINOP
→ walk_bb_node kind=7 unhandled → bb_gvar_assign op_a_slot==-1 bomb. With the prefix hoist, junk sits
below all expression pushes and every pop lines up; the resulting shapes are 100% pre-existing
(GVAR_RELOP branch, gvar lit-assign, gvar var read, GVAR_ARITH/ARITH_SLOT) — ZERO emitter changes,
LANGUAGE-BLIND rule untouched. m2 unchanged in behavior: arms store via ring(0)=lit, rd reads NV,
binop aux reads rd.value. NV temps `__pbt%d` (static counter, deterministic per run; P4 idents can't
collide with `__`).

RESIDUE (documented, no probe): (1) hoisting a RIGHT relop diamond over a LEFT non-relop operand
reorders evaluation when the left operand has side effects (function calls) — affects all modes
uniformly, diverges from pcom's strict l-to-r only for side-effecting boolean operand mixes;
(2) recursion can clobber an NV `__pbt` temp if a call in a LATER operand re-enters the same expression
— same hazard class as node-value aux reads, frame-slot temps would cure it if a probe ever forces it.

Session 20: PB-10b LANDED (SCRIP `1ad0019`) + PB-10c LANDED (SCRIP
`3ec6470`). The boolean m3/m4 story is closed. Gate at close: m2 42/2, m3 42/2, m4 42/2 — UNIFORM across
modes for the first time; the only fails are the standing pins boolmix.pas (PB-10a2) and recursion.pas
(16-bit maxint), identical in every mode. SNOBOL smoke 19/0. boolarg m3+m4 `1 0 1`; boolassign + boolnot
oracle-exact m2/m3/m4. sieve.s + m4wexpr.s byte-identical through both rungs. Re-verified green after
rebasing onto concurrent BB-FIXUP pushes (incl. the bb_builtin_*->bb_* rename).

PB-10b (bb_call.cpp, +44 lines): session 19's map executed verbatim — new arm in `marshal_call_arg` before
the gvar-read arm; γ-walk lf to the relop, require fin→IR_LIT_I(1) and relop→ω→IR_LIT_I(0);
`arith_operands(sg,...)` (both binop layouts); reuse `arith_opnd_a` (→rax, `bb_slot_alloc16` spill) +
`arith_opnd_b` (→rcx); `cmp rax,rcx` + conditional INTVAL(0/1) store; `arith_is_relop` + `relop_fail_mnem`
duplicated per RULES. ONE deviation, forced by the assembler: the map's label IDs 0/1 are NOT collision-safe
in mode-4 — the "uid per emitting box" premise is FALSE on the Pascal gvar flat chain (the WHOLE chain
shares one `_.x86_uid`; `.Lx4_0` was defined three times across the three show() calls; m3 passed because
BINARY label records ARE per-box). Fix per the session-17 single-call precedent: MEDIUM_TEXT labels
`.Lbrel%d_f/_e` keyed by `bb_node_id(relnd)`; MEDIUM_BINARY keeps per-box ids `idx*2/idx*2+1` (the LIT_S
namespace — an arg is one or the other, never both), guarded against X86_INTERNAL_MAX (16). FACT for all
future Pascal-chain work: never assume per-box uid for TEXT internal labels.

PB-10c (pascal.y only + direct regen): the sketched emitter arm was abandoned AFTER the mandated diagnosis.
Measured: the IR diamond is CORRECT (relop γ→LIT(1)→ASSIGN, ω→LIT(0)→ASSIGN, converging control); the bug
is `IR_ASSIGN(lit_i)` resolving its RHS at EMIT time to whichever single literal `assign.α` points at
(emit_core.c `walk_bb_node`: `op_a_node_kind = α->t`, `op_a_ival_sg = α->ival` — boolassign stmt 1 stored
constant 0, stmts 2-6 stored 1). The relop is UNREACHABLE from template handles (no back-pointers, nothing
in the emit context), so an emitter arm needs new dispatcher plumbing plus a redundant relop re-eval — and
the LANGUAGE-BLIND FACT RULE puts language-shaped behavior in parser/LOWER, never in a template arm. Fix:
the `assignment:` action rewrites `var := relop` (dst TT_VAR only) into the statement-IF
`TT_IF(relop, var:=1, var:=0)` — proven-green statement-IF + lit-assign shapes in ALL modes, gvar AND frame
destinations at once. The pas_bool diamond is retained where correct: the call-arg boundary (10b's arm) and
non-VAR destinations. RESIDUE (no probe forces these): `a[i] := relop` and `funcname := relop` (funcname
selector is TT_FNC via mk_ident) still ride the diamond → wrong in m3/m4 if ever exercised.

Landmines (re-confirmed): (1) `rm -f scrip` before `make scrip`; (2) `touch` templates before building;
(3) pascal regen ONLY via `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (1 s/r =
dangling-else), never the full regen script; (4) fpc on this image: `apt-get update` first, then plain
`apt-get install -y fpc` works (s19's liblzma 404 is cured by the update).

DEVIATION (PB-10a, documented): NOTSY emits `pas_flip_rel(pas_cond($2))` — boolean NOT stays in the
relop algebra (LT↔GE, LE↔GT, EQ↔NE; non-relop factor → `EQ(x,0)`, also correct for or-encoded stored
values >1) — because the spec'd `TT_IF(pas_cond(f),0,1)` measurably dies as an arith operand in m2 even
on the true path. `pas_bool` (relop → `TT_IF(relop,1,0)`) applies ONLY at the two value boundaries —
assignment RHS and call-arg value slot (width untouched) — so 10b/10c boundary IR shapes are exactly as
session 18 designed. FOURTH BUG (PB-10a2, NOT fixed): a FALSE relop as arith operand propagates
goal-failure and kills the m2 statement chain (`c := (i = 0) or b` prints nothing); TRUE leaks rv.
Fix is LOWER work (value-subgraphs don't run junctions).

Landmines (cost this session real time — do not skip): (1) `scrip:` Makefile target has NO
prerequisites — `rm -f scrip` before `make scrip` or the recipe never runs and your edit silently
doesn't take; (2) do NOT run `regenerate_parser_and_lexer_from_sources.sh` — it DELETED
`snobol4.lex.c` (aborts at the snobol4 flex step); regen pascal with
`cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`, restore any snobol4 casualties via
`git checkout -- src/parser/snobol4/...`; (3) template edits: `touch` the template before `make scrip`.

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

NEXT: the suite is clean AND UNIFORM (44/1 every mode) modulo the recursion maxint pin. Open candidates,
Lon picks: (a) the PB-10c residue shapes `a[i] := relop` / `funcname := relop` (still ride the value
diamond, no probe forces them); (b) case/goto remain TT_SUCCEED stubs until a probe forces them;
(c) the 16-bit maxint rung if recursion.pas is ever to go green.

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
- [x] **PB-10a — boolean operators: parser-only fix (m2 + sets up m3/m4).** LANDED session 19. Three
  audited bugs fixed in `pascal.y` only; parser regenerated. `pas_bool` (relop → `TT_IF(relop,1,0)`) at the
  two value boundaries: assignment RHS and call-arg value slot (width untouched). NOTSY deviates from the
  spec'd IF shape (measured: TT_IF as arith operand dies in m2 even when true) — emits
  `pas_flip_rel(pas_cond($2))` instead, keeping NOT in the relop algebra; boundary IR shapes for 10b/10c
  unchanged. Gate green: m2 41/0, m3 39/0, m4 39/0, SNOBOL smoke 19/0; probes
  nestvar/nestvar2/nestvar3 + boolassign + boolnot committed.
- [x] **PB-10a2 — relop/IF as arith operand (ALL MODES, two same-session rungs).** LANDED session 21
  (lower.c `pas_bool_diamond`: relational v_binop child → statement-IF-shaped diamond relop
  γ→LIT_I(1)→ASSIGN(__pbtN) / ω→LIT_I(0)→ASSIGN(__pbtN), HOISTED as a chain prefix, bare IR_VAR(__pbtN)
  in operand position; the prefix hoist is forced by the gvar-chain operand stack simulation — mechanism,
  the superseded v1 ring-IF join, and residues in watermark). Gate green: boolmix + boolchain (committed)
  oracle-exact m2/m3/m4 incl. double diamonds; suite 44/1 UNIFORM all modes (recursion pin only); SNOBOL
  smoke 19/0; sieve.s/m4wexpr.s byte-identical vs rebased base. Discovered session 19, pinned by XFAIL probe
  `boolmix.pas` (`c := not a or b` → oracle 0, scrip silent death). Fact: a relop operand of TT_ADD/TT_MUL
  is goal-directed in the IR — FALSE propagates failure and kills the statement chain; TRUE leaks rv as the
  value. A TT_IF operand dies on both paths (value-subgraphs don't run junctions). Fix lives in LOWER
  (`v_binop`/`lower_value_subgraph`): a relop operand must lower to a value-producing subgraph storing
  INTVAL(1)/INTVAL(0) with converging control, or the operand-subgraph executor must learn junctions.
  **Gate**: boolmix.pas m2 + chains `(i = 0) or b`, `not a or b`, `not a and b` all matching oracle.
- [x] **PB-10b — boolean marshal fix (m3/m4 call-arg).** LANDED session 20 (SCRIP `1ad0019`; map executed verbatim except TEXT label keying — see watermark). DIAGNOSED session 19 (zero code written; full
  implementation map + verified IR-shape facts in the watermark above — resume straight into
  `marshal_call_arg`, new arm before the gvar-read arm at bb_call.cpp:246). After PB-10a, the IR for `writeln(f(b_expr))`
  or `proc(relop)` has a `TT_IF(relop, 1, 0)` subgraph as the arg. Entry node of that subgraph is
  `IR_VAR_x` (lhs of relop), NOT the IR_BINOP; the γ-chase finds `fin=IR_LIT_I(1)` (then-branch) and the
  IR_BINOP itself sits between lf and fin with `ω→IR_LIT_I(0)`. The existing marshal falls into the gvar-read
  arm (reads lf=IR_VAR_x, emits x's value). Fix in `marshal_call_arg` (bb_call.cpp): walk γ chain from lf to
  find IR_BINOP with `arith_is_relop`; confirm `fin→t==IR_LIT_I(1)` and `relop_nd→ω→t==IR_LIT_I(0)`;
  `arith_operands` to get lhs/rhs; emit CMP + conditional INTVAL(0/1) store using `x86_jcc_id`/
  `x86_deflabel_id` (IDs 0,1 — safe for ≤1 relop arg per call). Also add `arith_is_relop` + `relop_fail_mnem`
  static helpers (duplicated per RULES, not shared). **Gate**: `boolarg.pas` m3+m4 (committed, oracle
  `1 0 1`; currently both print `1 1 1`) + m3/m4 of boolassign/boolnot; legacy 39 m3/m4 + SNOBOL smoke hold.
- [x] **PB-10c — boolean assignment RHS (m3/m4).** LANDED session 20 (SCRIP `3ec6470`; parser statement-IF rewrite — deviation from the emitter-arm sketch below, rationale in watermark). `b := pas_bool(relop)` lowers the RHS as
  `TT_IF(relop, 1, 0)`, producing an IR_IF subgraph. In gvar flat-chain mode the assignment template reads
  the RHS subgraph's "final" value by γ-chase; for a TT_IF subgraph the γ chase finds the then-branch
  literal (IR_LIT_I(1)) and emits a constant store — ignoring the conditional. Diagnose the exact IR shape
  produced by `v_assign(TT_ASSIGN(b, TT_IF(...)))` in gvar mode, then add the needed detection arm (likely
  in `bb_gvar_assign.cpp` or `bb_assign_frame.cpp`). **Gate**: m3+m4 boolassign/boolnot probes.

---

## The LB Ladder — LANGUAGE-BLIND BB/XA templates (Lon directive 2026-06-03)

- [x] **LB-1..8 + LB-3 + LB-FENCE — CLOSED** (sessions 13–14, SCRIP `37eefa1`/`95fdc2f`). COMPLETION TEST
  green: Tier-1 grep over `BB_templates/` + `XA_templates/` == 0. Single measured delta: raku m4
  `str_reverse` PASS→FAIL-loud (LB-1, pinned). Full matrix pins in git history (`.github` ~`965b047b`).
- [ ] **LB-7-NEW — post-audit inventory (NOT yet swept; concurrent ICN-SCAN sessions actively own these).**
  `# BOX ICN` tags in `bb_gen_scan.cpp:19,36`, `bb_keyword.cpp:23,32,43,54,64,73`, `bb_scan_any.cpp:19`,
  `bb_scan_match.cpp:20` (+ siblings `bb_scan_pos/tab/upto`). Sweep when ICN-SCAN settles, or fold into
  their next rung.
