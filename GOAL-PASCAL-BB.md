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

---

## ▶ CURRENT STATE — READ FIRST

**Watermark — session 14 (2026-06-04): LB-3 + LB-FENCE CLOSED · PB-9e-0 LANDED · PB-9e DESIGNED (build
held). SCRIP `f4a7187` (LB-3 = `95fdc2f`), corpus `10940fd`.** DEFINE is now its own IR shape (IR_CALL
dval=5.0, set by LOWER); the bb_call.cpp name-gate is DELETED; the LB ladder is COMPLETE — Tier-1 grep over
`BB_templates/`+`XA_templates/` = **0**, the FACT-RULE completion test. PB-9e is designed to turn-key
fidelity in **`SCRIP/PB-9E-DESIGN.md`** with two pinned failing gates: `nestrec` (oracle 11/21/31, m3
11/11/11 — recursion clobber) and NEW `nestshadow` (oracle 7/101, m3 107/107 — sibling-through-shadow;
structurally kills deepened NV shallow binding, which is dynamic-chain semantics). Baselines pinned at
HEAD this session: Pascal `--interp` **37/0/1** (XFAIL=recursion; +nestshadow); probes
hello/sieve/flatnoarg/recursion-fact7 m3+m4 byte-identical; SNOBOL4 smoke **19/0** (m2 7/0 HARD, m3 6/6,
m4 6/6 — the LB-3 named gate, NEVER MOVED); Icon smoke m2 **12/12** HARD (m3/m4 5/12 pre-existing);
Prolog smoke m2 **5/5** HARD, m4 5/0 (m3 `unify` FAIL stash-proven pre-existing); Snocone smoke 2/3
stash-proven pre-existing; raku smoke m2 **25/0** HARD, m3 1/1/23, m4 **1/1/23** (m4 FAIL=`str_reverse`,
the LB-1 delta, re-confirmed identical); all-langs m4 hello **5/1** (rebus pre-existing, exact pin);
lang-names gate output byte-identical pre/post LB-3 (exit-1 hits = LB-7-NEW ICN-SCAN emit_core sites,
concurrent-session-owned). Session-13 full-corpus pins (Icon 130/117/36, Prolog honest 136/0/0) not re-run.

Mechanisms that now exist (dispatch is shape-only, see git history for the full wall lists):
- DEFINE rides its own IR shape: IR_CALL **dval=5.0**, tagged by LOWER (lower.c SNO TT_FNC arm — name
  knowledge stays in LOWER per the FACT RULE); consumers shape-only: m2 interp generic arm, flat-chain
  driver FILL, chain-arity (arity-0, args ride counter blks), nested-call marshal, bb_call dispatch.
- gvar-chain operand heads include ω-edge-reachable chains (`gvar_chain_operand_refs`, emit_bb.c).
- IR_WHILE/IR_UNTIL, IR_IF, IR_RETURN are pure junctions under `g_gvar_flat_chain` (`jmp γ`; RETURN keeps
  the dval==2.0 fail-exit FRETURN contract; result rides NV — `rt_call_named_proc` reads `NV_GET_fn(name)`,
  which IS Pascal's funcname-as-return-variable model). Operand-pass α-clobber on RETURN is harmless now.
- Calls: registered procs dispatch at dval 2.0|3.0 → `bb_call_gvar_userproc_str` → `rt_call_named_proc`
  (NV-seats params; recursion-safe, 256-deep frame arena); unregistered+unknown-builtin names at dval
  2.0|3.0 → `bb_call_byname_str` → `rt_call_arr`; `marshal_call_arg` inlines nested CALL args picking the
  runtime entry by registration (its MEDIUM_BINARY idiom was fixed to load_ro+frame_lea).
- Templates `bb_binop_gvar_relop.cpp` + `bb_binop_gvar_arith_slot.cpp`: per-operand LIT-imm /
  VAR-via-`rt_gvar_get_int` / slot shapes via `bb_lk/bb_li/bb_rk/bb_ri`+`op_name1/2`+`op_sa/sb`; slot disp
  +8 for IR_CALL DESCRs, +0 for raw arith qwords; own slot doubles as rax stash; relop = stackless cmp,
  arith = raw qword at `op_off` matching `bb_gvar_assign`'s int-binop read.
- Icon NV-global assign is UNIFIED into `bb_gvar_assign` (descr first arm, modulo-ID byte-identical to the
  deleted fork; if Lon wants the originally-prescribed ABORT it is one line in that arm).

NEXT: **PB-9e-1** — the representation fork is surfaced in `SCRIP/PB-9E-DESIGN.md`, awaiting Lon's call on
(A) nested-only vs uniform slot migration (recommend nested-only, LB-3-style move-the-gate-last) and (B)
explicit `rt_call_named_proc_sl(...,void *sl)` vs in-band `args[np]` SL (recommend explicit); the recipe is
then turn-key — emit-time-constant `[fb+0]` hop chains, IR_VAR_FRAME/IR_ASSIGN_FRAME (ival=slot, dval=hops).
Known deeper Pascal m3/m4 walls, stash-proven never-passing (NOT regressions): rec2/ptr5 segv at
record-field/heap `__pas_*` arms.

---

## The Pascal rail (architecture facts that bind ongoing work)

Pascal has its own rail end-to-end: parser tag **`LANG_PASCAL`=6** (`src/parser/snobol4/scrip_cc.h`), IR tag
**`IR_LANG_PAS`=7** (`src/contracts/IR.h`), own body walker **`lower_pascal_body`** (`src/lower/lower_program.c`),
own program dispatch (`lower_program.c`). Parser emits **real AST** (no desugaring): `TT_FOR`/`TT_REPEAT`/
bare-`TT_IF`, and `TT_PROC_DECL` with `c[3]`=return-var present iff it's a function. LOWER dispatch shape is
**outer `switch(tree->t)` → inner `switch(cx.lang)`** — share an arm where behavior is identical, dedicated
arm where it diverges. `v_pascal_for` + `v_pascal_repeat` (`src/lower/lower.c`) lower **directly to IR**
(compose IR nodes, wire the four ports by hand; no synthetic AST). Driver mode-2 for Pascal is the
`!is_icon && !is_prolog` branch in `scrip.c` → finds `main`, runs `IR_interp_once`.

**Key design facts (PB-4/5/6):**
- **Output:** `__pas_writeln`/`__pas_write` take interleaved `(value,width)` arg pairs. Integer right-justified
  in `max(w,digits)`, default width 10 (real 20); string as-is; `:w` is a **minimum**; `__pas_writeln`
  appends `\n`. `__pas_sqr(x)`=x*x.
- **Arrays:** keep `TT_IDX` faithful in the parser; translate at LOWER on the Raku array rail — `TT_IDX` →
  `arr_get`; `a[i]:=v` → `a := arr_set_pure(a,i,v)`. `arr_set_pure` does NOT auto-grow, so the parser prepends
  an init prologue sizing the array to `high+1` SOH-packed "0" segments (raw index; slots `0..low-1` wasted).
- **Booleans:** `IR_IF` branches on `IS_FAIL_fn`. Stored booleans must survive the array round-trip, so encode
  true=`INTVAL(1)`/false=`INTVAL(0)`; a bare-boolean condition is wrapped `expr ≠ 0` (`pas_cond`). `and`/`or`
  are `TT_MUL`/`TT_ADD` in this grammar so they wrap too.
- **Functions:** body ends with `IR_RETURN`(dval 0.0) whose `α` is `IR_VAR(funcname)`; `fact := …` writes the
  NV global (funcname not in frame scope), `IR_RETURN` reads it back. Correct under recursion because each
  call clears `FRAME.returning` before the enclosing NV write.
- **Parse-time tables** (reset per parse): `const` folding, array name→high, `true`/`false`→`ilit(1/0)`,
  `sqr`→`__pas_sqr`.

---

## Target dialect — the P4 subset, NOT full ISO 7185

The target is the **P4 Pascal subset** — the language `pcom` actually compiles. Authoritative spec is
`pcom.pas`'s `const` block plus `grammar/pascalp.y`. Practical bounds:
- **Files:** only predefined `text` files (`input`, `output`); no user file variables.
- **`goto`:** intra-procedure only.
- **Sets:** small base type (`set of 0..58`).
- **Types:** integer (**16-bit `maxint = 32767`**), real, char, boolean, enumerated, subrange, `array`,
  `record`, `set`, pointer (`new`); value + `var` params; nested routines.
- **Absent:** first-class strings, `dispose`, later ISO niceties. If `pcom` rejects a probe, it is **out of
  scope, not a bug.** Climb only as far up this subset as the probes demand.

---

## ⚖ Provenance guardrail — the SCRIP frontend stays commercial-clean

The SCRIP Pascal frontend is **original C**, written fresh. `pcom.pas`/`pint.pas` are a **private behavioral
oracle**, used only to check SCRIP's output during development — **never transliterated into the lowering,
never linked into `scrip`, never shipped.** Syntactic reference = the MIT-licensed grammar; semantic
reference = `pint`'s observable behavior + the P4 subset above. Read the reference to learn what a construct
*means*, then write the C yourself.

---

## The crux: nested-function frames ARE Byrd Boxes (PB-7 design intent)

Pascal contributes **one** genuinely new construct: **nested procedures/functions** — a routine declared
inside another, able to read/write the enclosing routine's locals (uplevel / non-local addressing).
Everything else is wiring an existing AST shape to an existing lowering (arithmetic, assignment,
`if`/`while`/`for`/`repeat`, compound statements, value/`var` params, return values — all already lowered).

A Byrd-Box graph **is already an activation-record stack**. In the P-machine, `mst` reserves a frame, `cup`
enters it, and frames chain through a **static link** (the classic display). In SCRIP that chain is **the
parent-port thread of the BB graph** — no separate display array, no C frame struct.

Design intent (refine at PB-7, not before):
- Each routine activation is a BB; its **α/β/γ/ω** ports carry the four-port contract; the **static link to
  the lexical parent** travels as the parent-port reference the BB already holds.
- **Uplevel access** = walk `level(use) − level(decl)` parent links and read the slot (port-chasing).
- **100% Byrd Boxes, zero C Byrd-box functions, stackless.** No closures — the P4 subset has no
  first-class/returnable functions, so a frame never outlives its parent; uplevel access is always to a live
  ancestor frame.

This stresses the frame/scope dimension of the BB model the way Prolog stresses backtracking and Icon
stresses generators.

---

## Invariants (inherited from Command Central)

1. **No AST walking in modes 2/3/4.** Lower to IR, then interpret/emit.
2. **Zero C Byrd-box functions.** A Pascal frame is a BB, not a C function.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL; static link rides the
   parent-port thread.
6. **Builder/consumer case rule.** UPPERCASE builds IR; lowercase consumes.
16. **THE RULE.** From PB-9 on (mode-3/4): no byte emitted unless it carries a BB/SM/XA opcode; every box is
    one `x86(...)` concat emitted by `bb_emit_x86`; `bb_bin_t` is abolished. Early rungs are mode-2
    (`--interp`) only.

---

## Where things live

| Thing | Path | Role |
|-------|------|------|
| **Reference compiler** | `corpus/programs/pascal/pcom.pas` | Grammar + semantics oracle. |
| **Reference P-machine** | `corpus/programs/pascal/pint.pas` | Execution oracle. Diff SCRIP's output against it. |
| **Token + grammar blueprint** | `corpus/programs/pascal/grammar/pascalp.{l,y}` | lex tokens → `TT_*`; yacc grammar scopes the parser. (MIT.) |
| **Probes** | `corpus/programs/pascal/` (`recursion.pas`, `sieve.pas`, `README.md`) | Our own Pascal probes + bootstrap writeup. |
| Pascal frontend | `src/parser/pascal/pascal.{l,y}` | Source → `TT_*` → shared AST. |
| Lowering | `src/lower/lower.c` + `lower_program.c` | Pascal AST → shared IR; nested-frame lowering at PB-7. |
| Mode-2 interpreter | `src/interp/IR_interp.c` | Executes the IR. The early-rung target. |
| BB templates | `src/emitter/BB_templates/` | Only from PB-9 (mode-3/4). |

**Start every Pascal session by reading the reference grammar** (`pascalp.l` tokens, `pascalp.y` productions).

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/SCRIP/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
# Reference toolchain (the oracle) — build once with Free Pascal:
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
```

Check a probe against the oracle:
```bash
cd /home/claude/corpus/programs/pascal
./pcom < probe.pas && cp prr prd && ./pint < /dev/null   # reference output (the oracle)
/home/claude/SCRIP/scrip --interp probe.pas              # SCRIP output — must match
```

---

## The Rung Ladder

- [x] **PB-0..PB-8 + PB-6b — the full interpreter rail (mode-2).** Lexer → parser → LOWER → all control
  flow, flat+nested procs/functions, records/arrays/sets/pointers/`new`. Every gate byte-identical to
  `pint`; suite 35 PASS + recursion XFAIL. Details: git history sessions 1–9.
- [ ] **PB-9 — Cross onto compiled BBs (mode-3/4).** Per FACT RULES; design doc `SCRIP/PB-9-DESIGN.md`.
  - [x] **PB-9a..PB-9d** — seed · arith/assign/writeln(expr) · control flow (`sieve` gate) · flat
    procs/params (`recursion` through fact(7) gate). All landed sessions 11–13, all language-blind; gates
    in the watermark above.
  - [ ] **PB-9e — nested procs = the representation FORK (Lon's call).** Frame-as-BB, static link on the
    parent-port thread (Invariants 2 & 4, the PB-7 model). **DESIGNED session 14 → `SCRIP/PB-9E-DESIGN.md`**
    (turn-key; fork points A migration-scope / B rt-signature await Lon).
    - [x] **PB-9e-0** — discriminator probe `nestshadow.pas` (corpus `10940fd`): sibling-through-shadow,
      oracle 7/101, m2 PASS (suite 36→37/0/1), m3 107/107 expected-fail pinned. Together with `nestrec`
      (11/21/31 vs 11/11/11) this structurally kills the NV-shallow-binding shortcut.
    - [ ] **PB-9e-1** — SL plumbing + nested locals/params → frame slots; gates in the design doc.
    - [ ] **PB-9e-2** — var params across levels (SlotRef → cell address).
    - [ ] **PB-9e-3** — nested functions under recursion (`nestfunc`/`nestcount` m3+m4).

---

## The LB Ladder — LANGUAGE-BLIND BB/XA templates (Lon directive 2026-06-03, session 11)

Fix every violator inventoried in `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (audit at SCRIP `80ee2e3`; line
numbers drift — re-grep per step). Lon's mechanism for Tier-1 code arms: **replace the snippet with an
ABORT** (`x86_bomb` keeps the dispatch shape; surviving traffic fails LOUD and names itself). EVERY step:
run the named gate, pin before/after counts here, prove zero drift elsewhere.

- [x] **LB-1/2/4/5/6/7/8** — DONE (session 13, SCRIP `37eefa1`). Raku descr dval==2 arm ABORTed (measured
  delta: raku smoke m4 `str_reverse` PASS→FAIL-loud; all else zero drift); `bb_call_rk.cpp` deleted,
  `.Lrkarg`→`.Lcallarg`; Icon NV-global fork resolved AT THE UNIFICATION TARGET (modulo-ID byte-identical,
  fork deleted — abort would have collided with concurrent in-flight ICN-SCAN sessions);
  `bb_pl_op_floaty`→`bb_op_floaty`; Tier-2 audit-scope string sweep; Tier-3 comments deleted. Full pins in
  git history (`.github` log around `965b047b`).
- [x] **LB-3 — `DEFINE` name-gate → ELIMINATED via LOWER re-route** (session 14, SCRIP `95fdc2f`). Done
  re-route-FIRST exactly as directed: LOWER tags DEFINE IR_CALL dval=5.0; six single-line shape-only
  consumer edits (lower.c producer, m2 interp arm, flat-driver FILL, chain-arity, nested-marshal,
  bb_call dispatch); the `strcmp(fn,"DEFINE")` snippet DELETED outright — nothing left to abort. THE
  NAMED GATE NEVER MOVED: SNOBOL4 smoke 19/0 (m3 6/6, m4 6/6) byte-identical pre/post; zero drift
  everywhere (Snocone 2/3 + Prolog m3 `unify` stash-proven pre-existing; lang-names gate output
  byte-identical).
- [ ] **LB-7-NEW — post-audit inventory (NOT yet swept; concurrent ICN-SCAN sessions actively own these).**
  `# BOX ICN` tags in `bb_gen_scan.cpp:19,36`, `bb_keyword.cpp:23,32,43,54,64,73`, `bb_scan_any.cpp:19`,
  `bb_scan_match.cpp:20` (+ siblings `bb_scan_pos/tab/upto`). Sweep when ICN-SCAN settles, or fold into
  their next rung.
- [x] **LB-FENCE — CLOSED** (session 14). COMPLETION TEST green: Tier-1 grep over `BB_templates/` +
  `XA_templates/` == **0** (all eight audit items: 1/2/4/5/6/7/8 session 13, item 3 = LB-3 session 14).
  Full matrix pinned at `95fdc2f`: Pascal 37/0/1 + m3/m4 probes · Icon smoke m2 12/12 · Prolog smoke m2
  5/5 + m4 5/0 · SNOBOL4 19/0 · Raku 25/0 + m3 1/1/23 + m4 1/1/23 · all-langs m4 hello 5/1. Every
  LB-1..LB-8 delta accounted: the SINGLE measured delta is raku m4 `str_reverse` PASS→FAIL-loud (LB-1,
  pinned session 13, re-confirmed identical session 14); LB-2/4/5/6/7/8 byte-identical/modulo-ID (session
  13); LB-3 zero drift (stash-proven session 14). LB-7-NEW remains open BY DESIGN below — Tier-2-class
  `# BOX ICN` strings, outside the Tier-1 completion test, concurrent-ICN-SCAN-owned.

