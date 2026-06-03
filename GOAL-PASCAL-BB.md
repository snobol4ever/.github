# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes, from zero

**Repo:** SCRIP (frontend + lower) · corpus (reference compiler at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT PRIORITY — READ FIRST

**Seed the language. Get `scrip --interp hello.pas` to print `Hello World!`.** Then climb one
tiny rung at a time. **No test suite yet** — each rung is a single hand-written `.pas` probe whose
output you eyeball against `pint` (the reference P-machine in `corpus/programs/pascal/`). We grow the
corpus later, exactly the way every other SCRIP frontend grew.

```pascal
program hello(output);
begin
    writeln('Hello World!')
end.
```

The first real milestone is **PB-1..PB-3**: a lexer that emits the shared `TT_*` tokens, a parser
that builds the shared AST, and a LOWER hookup so the above lowers to the same IR a `print` lowers to
in the other languages. After that, Pascal rides rails SCRIP already has.

---

## The premise: we already have almost all of this

Pascal is a plain imperative language. Arithmetic, assignment, `if`/`while`/`for`/`repeat`, compound
statements, procedure/function calls with value/var parameters, return values — **SCRIP lowers every
one of these today** for Icon/Prolog/SNOBOL4. Pascal contributes *one* genuinely new construct:

> **Nested procedures and functions** — a routine declared inside another routine, able to read and
> write the enclosing routine's locals (uplevel / non-local addressing).

Everything else is wiring an existing AST shape to an existing lowering. The nested-function frame is
the rung that earns the "BB" in the title.

---

## Target dialect — the P4 subset, NOT full ISO 7185

The target is the **P4 Pascal subset** — the language `pcom` actually compiles — **not** full ISO 7185
Pascal. This keeps the scope closed and the rungs small. The authoritative spec is `pcom.pas`'s own
`const` declaration block plus `grammar/pascalp.y`. The practical bounds to remember:

- **Files:** only the predefined `text` files (`input`, `output`); no user-declared file variables.
- **`goto`:** intra-procedure only — no non-local jumps.
- **Sets:** small base type (`set of 0..58` in the P-machine).
- **Types present:** integer (a **16-bit `maxint = 32767`** target word), real, char, boolean, enumerated,
  subrange, `array`, `record`, `set`, pointer (`new`); value and `var` parameters; nested routines.
- **Absent:** first-class strings, `dispose`, and the later ISO niceties. If a probe needs something
  `pcom` rejects, it is **out of scope, not a bug.**

Climb only as far up this subset as the probes demand.

---

## ⚖ Provenance guardrail — the SCRIP frontend stays commercial-clean

The SCRIP Pascal frontend is **original C**, written fresh — same as every other SCRIP front end.
`pcom.pas` / `pint.pas` are a **private behavioral oracle**, used only to check SCRIP's output during
development. They are **never transliterated into the lowering, never linked into `scrip`, and never
shipped.** The *syntactic* reference is the MIT-licensed grammar; the *semantic* reference is `pint`'s
observable behavior plus the ISO/P4 subset above. This is what keeps the dual-licensed (AGPL + commercial)
SCRIP product free of ETH-authored code: **read the reference to learn what a construct *means*, then
write the C yourself.**

---

## The crux: nested-function frames ARE Byrd Boxes

A Byrd-Box graph **is already an activation-record stack** — that is what makes this fun. In the
P-machine, `mst` (mark stack) reserves a frame, `cup` enters it, and frames chain through a **static
link** so an inner routine can reach an outer routine's variables (the classic *display*). In SCRIP
that chain is **the parent-port thread of the BB graph** — no separate display array, no C frame
struct.

Design intent (to be refined at PB-7, not before):
- Each routine activation is a BB. Its **α/β/γ/ω ports** carry the four-port contract (Invariant 4);
  the **static link to the lexical parent** travels as the parent-port reference the BB already holds.
- **Uplevel variable access** = walk `level(use) − level(decl)` parent links and read the slot. The
  walk is port-chasing in the BB graph, which is exactly what the box machinery does for backtracking
  and generators in the other languages.
- **100% Byrd Boxes. Zero C Byrd-box functions** (Invariant 2). **Stackless** — the BB graph is the
  stack. No native call frame models a Pascal frame.

This is the whole reason to do Pascal as a BB language: it stresses the frame/scope dimension of the
BB model the way Prolog stresses backtracking and Icon stresses generators.

---

## Invariants (inherited from Command Central — these bind here too)

1. **No AST walking in modes 2/3/4.** Lower to IR, then interpret/emit.
2. **Zero C Byrd-box functions.** A Pascal frame is a BB, not a C function.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL; the static link rides
   the parent-port thread.
6. **Builder/consumer case rule.** UPPERCASE builds IR; lowercase consumes.
16. **THE RULE.** Once Pascal reaches mode-3/4, no byte is emitted unless it carries a BB/SM/XA opcode;
    every Pascal box is one `x86(...)` concatenation emitted by `bb_emit_x86` — `bb_bin_t` is abolished
    (see the FACT RULES in `GOAL-ICON-BB.md` / `GOAL-PROLOG-BB.md`). **This only matters from PB-9 on;
    the early rungs are mode-2 (`--interp`) only.**

---

## Where things live

| Thing | Path | Role |
|-------|------|------|
| **Reference compiler** | `corpus/programs/pascal/pcom.pas` | The grammar + semantics oracle. What does construct X mean? Read its P-code. |
| **Reference P-machine** | `corpus/programs/pascal/pint.pas` | The execution oracle. Run a probe here, diff SCRIP's output against it. |
| **Token + grammar blueprint** | `corpus/programs/pascal/grammar/pascalp.{l,y}` | The lex token rules map straight to a `TT_*` set; the yacc grammar scopes the parser. (MIT-licensed.) |
| **Bootstrap writeup + probes** | `corpus/programs/pascal/` (`README.md`, `recursion.pas`) | How the reference builds/self-hosts, plus our own Pascal probes. |
| Pascal frontend | `src/parser/` (new `pascal.l` + `pascal.y`, alongside the other 6) | Source → `TT_*` → shared AST. |
| Lowering | `src/lower/` (`lower2.c` / AST→IR) | Pascal AST → shared IR graph. Reuse existing arms; add nested-frame lowering at PB-7. |
| Mode-2 interpreter | `src/interp/IR_interp.c` | Executes the IR. The early-rung target. |
| BB templates | `src/emitter/BB_templates/` | Only from PB-9 (mode-3/4). |

**Start every Pascal session by reading the reference grammar** (`corpus/programs/pascal/grammar/pascalp.l`
for tokens, `pascalp.y` for the production shapes) — it is the cheapest possible spec for the front end.

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
# Sanity: the reference still self-hosts (see corpus/programs/pascal/README.md "bootstrap fixpoint").
```

To check a probe against the oracle:
```bash
cd /home/claude/corpus/programs/pascal
./pcom < probe.pas && cp prr prd && ./pint < /dev/null   # reference output (the oracle)
/home/claude/SCRIP/scrip --interp probe.pas              # SCRIP output — must match
```

---

## The Rung Ladder (each rung tiny; eyeball vs the oracle; no suite yet)

- [x] **PB-0 — Orient.** Build the reference `pcom`+`pint` (Session Setup). Read `grammar/pascalp.l`
  (tokens) and `pascalp.y` (productions). Skim the `case` in `pint.pas` for the opcode → semantics map.
  No SCRIP code yet — just know the spec.
- [x] **PB-1 — Lexer → `TT_*`.** Add the Pascal frontend lexer in `src/parser/`. **Minimal set first**:
  `program`, `begin`, `end`, identifier, string literal (`'...'`, with `''` escape), `(`, `)`, `;`,
  `.`, and the `writeln` builtin. Comments `(* *)` and `{ }`. Emit the shared `TT_*` stream. Defer the
  full keyword/operator table (it's all in `pascalp.l`) until the constructs need it.
- [x] **PB-2 — Parser → AST.** Parse program-heading + a block whose body is one compound statement
  containing a single `writeln('...')`. Build it from **existing AST node kinds** (program/block,
  statement-seq, builtin-call, string-literal). No new contract types.
- [x] **PB-3 — SEED: hello via LOWER + `--interp`.** Hook the Pascal AST into `src/lower/` so
  `writeln('Hello World!')` lowers to the same IR `print` uses elsewhere, and `scrip --interp hello.pas`
  prints `Hello World!`. **This is the Icon/Prolog/SNOBOL4 "hello" seed for Pascal.** ⟵ first green.
- [x] **PB-4 — Integers, `var`, assignment, `writeln(int)`.** ✅ 2026-06-02. `var i: integer; i := 2+3;
  writeln(i)` → byte-identical to `pint`. Implemented Pascal-specific `__pas_writeln`/`__pas_write`
  builtins (interleaved `(value,width)` arg pairs): integer right-justified in `max(w,digits)`,
  default width 10 (real default 20); string as-is; `__pas_writeln` appends `\n`. `:w` is a minimum
  width (full value emitted when it exceeds `w`). 16-bit overflow not yet matched (deferred; document).
- [x] **PB-5 — Control flow + `sieve.pas` gate.** ✅ DONE 2026-06-03. All control flow byte-identical to
  `pint` (`if/then/else`, bare `if`, `while/do`, `for/to`, `for/downto`, `repeat/until`, nested loops) via
  Pascal LOWER arms on real `TT_FOR`/`TT_REPEAT`/`TT_IF` nodes — NOT parser desugaring. `v_pascal_for`
  lowers **directly to IR** (composes IR nodes + wires the four ports by hand, like `v_pascal_repeat`; no
  synthetic AST). **`sieve.pas` gate MET**: 1-D `TT_IDX` load → `arr_get`, `TT_ASSIGN(TT_IDX)` store →
  `arr_set_pure` writeback (Pascal arms on the Raku array rail); `const` folding, array-var decl +
  pre-sized SOH-packed init prologue (`arr_set_pure` does NOT auto-grow), `true`/`false`→1/0, bare-boolean
  conditions wrapped `expr ≠ 0`, `sqr`→`__pas_sqr`. (Details in the session-4 watermark below.)
- [ ] **PB-6 — Top-level (flat) procedures & functions.** Definitions, value + `var` parameters, return
  values, calls. **No nesting yet.** Reuse the existing call machinery. **Target: `recursion.pas`**
  (`fact`, `fib` at top level) through `fact(7)`.
- [ ] **PB-7 — NESTED procedures & functions (THE NEW RUNG).** A routine declared inside another,
  reading/writing the enclosing locals. Implement the static-link-as-parent-port design above: each
  activation is a BB, uplevel access walks parent links, 100% BB, stackless. **Design it here, once,
  carefully** (it is the only construct SCRIP has never lowered). Probe: a nested helper that reads &
  mutates an enclosing routine's local **while the enclosing routine is still active** — e.g. a nested
  `partition` referencing the outer `quicksort`'s array parameter, or a nested proc that bumps an outer
  counter. (No closures — the P4 subset has no first-class/returnable functions, so a frame never
  outlives its parent; uplevel access is always to a live ancestor frame.)
- [ ] **PB-8 — Aggregates as needed.** `record`, `array`, `set`, pointers/`new`. Add only what later
  probes require; the reference `pint` store layout is the semantics oracle.
- [ ] **PB-9 — Cross onto compiled BBs (mode-3/4).** Convert Pascal's boxes to the `x86()` self-encoding
  API per the FACT RULES (one `x86(...)` concat per box, `bb_emit_x86`, no `bb_bin_t`). Rebase onto the
  shared `x86_asm.h` keystone first. Mirrors the template-revamp track the other languages are on. Only
  start once the mode-2 ladder above is comfortably green.

---

## Watermark (live state)

**2026-06-03 (session 4) — TT_FOR IR-DIRECT + PB-5 `sieve.pas` GATE MET (byte-identical to `pint`).**

**(1) TT_FOR now lowers DIRECTLY to IR (commit `9a2ae17`).** Per Lon's directive ("make your TT_FOR and
TT_REPEAT, follow Pascal at this level; the IR level is where things are generic & composable"),
`v_pascal_for` (`src/lower/lower.c`) no longer synthesizes `TT_ASSIGN/TT_WHILE/TT_SEQ_EXPR` AST and
re-lowers it. It now composes IR directly like `v_pascal_repeat`: init/cond/incr built as IR nodes, body
via `lower2`, the four ports wired by hand. NO wrapper node (cond.ω → loop-exit `γ_in`); the limit `to`
is a lowered sub-tree (so expression limits like `1 to n-1` work). Three Pascal-only helpers added just
before `v_pascal_for`: `pas_leaf_node` (bare IR_VAR/IR_LIT_I), `pas_binop_ll` (binop from two leaf
operands — increment `i±1`), `pas_binop_lt` (binop with op0 leaf + op1 a lowered sub-tree — condition
`i REL to`). All reachable only from `IR_LANG_PAS`. `v_pascal_repeat` was already IR-direct (untouched).

**(2) PB-5 `sieve.pas` gate MET** (arrays + const + sqr + booleans). Philosophy: keep `TT_IDX` faithful in
the parser; do the generic array translation at LOWERING, on the Raku `arr_get`/`arr_set_pure` rail.
- LOWER arms (`src/lower/lower.c`, both `IR_LANG_PAS`-gated): dedicated `case TT_IDX:` →
  `v_raku_det_call(cx,"arr_get",{base,idx},2,...)` (pulled `TT_IDX` out of the shared `TT_FIELD/...` group);
  in `v_assign`, `a[i]:=v` (TT_IDX LHS) → `v_raku_mutate_writeback(cx,base,"arr_set_pure",{base,idx,v},3,...)`
  = `a := arr_set_pure(a,i,v)`.
- PARSE-TIME (`src/parser/pascal/pascal.y`): **const** table + folding (`mk_ident` maps a const IDENT →
  `ilit`; `const_decl` records; `scalar_constant`/`constant`/`simple_type`/`type` now carry `<ival>`).
  **array** table (`var_decl` records name→high when `type` ival ≥ 0; the ARRAY `type` production carries
  the index `simple_type`'s high; bare `type: simple_type` → −1 so subrange-scalar vars are NOT mistaken
  for arrays). **init prologue** (`program:` prepends `a := <(high+1) "0" segments joined by SOH 0x01>` to
  main's body via `mk_array_fill`, because `arr_set_pure` does NOT auto-grow — the array MUST be pre-sized;
  raw index used so slots `0..low-1` are wasted but correct). `true`/`false`→`ilit(1)`/`ilit(0)` (both are
  plain IDENTs in the lexer); `sqr`→`__pas_sqr` via `map_io`. Tables reset per parse in `pascal_parse_string`.
- BOOLEAN ENCODING (the crux): `IR_IF` (`IR_interp.c:2287`) branches on `IS_FAIL_fn(cv)` — FAIL→else,
  non-FAIL→then. A stored boolean must survive the string-segment array round-trip, so it can't be FAIL.
  Encode true=`INTVAL(1)`/false=`INTVAL(0)` (round-trips: `arr_set_pure`→`to_cstring`→"1"/"0";
  `arr_get`→`elem_to_descr` strtol→`INTVAL`). A **bare-boolean** condition is then wrapped `expr ≠ 0`
  (`pas_cond` in pascal.y, applied in if/while/repeat): `1≠0`→non-FAIL (then), `0≠0`→FAIL (else).
  Relationals (TT_LT/LE/GT/GE/EQ/NE, per `pas_is_rel`) are left untouched (already success/FAIL). `and`/`or`
  are TT_MUL/TT_ADD in this grammar, so they wrap correctly too (`a*b≠0`, `a+b≠0`).
- RUNTIME: `__pas_sqr(x)` = x*x (int or real, single evaluation), added at the top of
  `script_try_call_builtin_by_name` (`src/runtime/builtins/script_builtins_byname.c`).

**Verification:** `sieve.pas` byte-identical to `pint` (25 primes, 2..97). Pascal regression 10/10 (hello,
pb4 widths, if/else, bare-if, while, repeat, for-to/downto). Icon mode-2 **12/12** + Prolog mode-2 **5/5**
HARD gates green. Raku `rk_arith`/`rk_arrays` `--interp` byte-identical. A stash → rebuild → re-run diff
proved ZERO behavioral change outside the Pascal path.

**Two residual issues (NOT introduced this session — flagged for attention):**
- `scripts/regenerate_parser_and_lexer_from_sources.sh` is `set -e` and ABORTS at the snobol4 flex step
  (it deletes/clobbers `snobol4.lex.c` and never reaches the Pascal stanza at the very end). Workaround
  used here: regenerate Pascal directly — `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y &&
  flex --noline -o pascal.lex.c pascal.l` — then `git checkout` the snobol4 generated files. Script wants a fix.
- `test/raku/rk_array_literal.raku` FAILS on the CLEAN baseline (proven by stash+rebuild) — pre-existing,
  not from this work, despite the session-2 watermark having listed it green. (`rk_arith`/`rk_arrays` pass.)

**Files touched (session 4):** `src/lower/lower.c`, `src/parser/pascal/pascal.{y,tab.c,tab.h}`, and the
by-name builtin dispatch (`__pas_sqr`). NOTE: this session rebased onto upstream RS-2 (`a149ce4`), which
dissolved `script_builtins_byname.c` into the new `src/runtime/by_name_dispatch.c` — so `__pas_sqr` landed
in `by_name_dispatch.c` (top of `script_try_call_builtin_by_name`), not the old file. Commits: `9a2ae17`
(TT_FOR IR-direct) + `f7cb3d5` (PB-5 sieve gate), both on top of `a149ce4`.

**Next:** PB-6 flat procs (`recursion.pas`: `fact`,`fib` at top level through `fact(7)`; mind 16-bit
maxint=32767 — `fact(8)` legitimately aborts in `pint`, so match that). Then PB-7 nested-function frames
(static-link-as-parent-port — the one construct SCRIP has never lowered; design carefully). Then PB-8
aggregates / PB-9 mode-3/4.

---

**✅ CROSS-LANGUAGE LOWER COUPLING EXCISED (session 3, 2026-06-02 — Lon: switch-TT_* / switch-LANG).**
The LOWER dispatch is now the correct shape where Pascal participates: **outer `switch(tree->t)` → inner
`switch(cx.lang)`**, choosing *add an arm* or *share an arm* at each cell. Concretely in `src/lower/lower.c`:
- TT_FNC call (`:860`): `switch (cx.lang) { case IR_LANG_ICN: v_det_call(...,1); case IR_LANG_PAS:
  v_det_call(...,0); }` — Icon and Pascal are **distinct arms** over the **shared** language-neutral
  builder `v_det_call(cx,e,allow_generator,...)` (the only per-lang knob is the generator check). Pascal
  no longer appears in any Icon-gated `||`.
- bare-`if` else-target in `v_if` (`:290`): `switch (cx.lang) { case IR_LANG_RKU: case IR_LANG_PAS:
  elseα=γ_in; ... }` — Raku and Pascal **share an arm** via C fall-through.
- TT_FOR (`:965`) / TT_REPEAT (`:761`): Pascal-only arms → `v_pascal_for` / `v_pascal_repeat` (down-tree
  special functions branch off once the (TT_*,LANG) context is landed).
**Result: 100% code sharing where behavior is identical, dedicated arms only where it diverges.** Verified
11/11 Pascal probes byte-identical to `pint`; Icon/Prolog/Raku/SNOBOL4 regression-green (Icon call path
behavior unchanged — `v_det_call(...,1)` is exactly the old inline code).

**Residual (non-LOWER) Icon adjacency — generic proc-registration infra, lower priority:**
`src/driver/polyglot.c:43,90,128` — `LANG_PASCAL` is gated *alongside* `LANG_ICN`/`LANG_RAKU` in the
init guard, proc-table collection, and `nparams` shape. These are language-neutral driver plumbing, not
LOWER semantics; break `LANG_PASCAL` into its own clauses when convenient for zero adjacency.

**2026-06-02 (session 2) — PB-4 GREEN + PB-5 CONTROL FLOW GREEN, ON PASCAL'S OWN RAIL.**
Pascal is no longer riding the Icon rail. It has its own identity end-to-end: parser tag
**`LANG_PASCAL`=6** (`src/parser/snobol4/scrip_cc.h`), IR graph tag **`IR_LANG_PAS`=7**
(`src/contracts/IR.h`), own proc-body walker **`lower_pascal_body`** (`src/lower/lower_program.c:217`),
own program-dispatch block (`lower_program.c:583`, returns `g_stage2.lang=IR_LANG_PAS`). Parser emits
**real AST nodes** (no desugaring): `TT_FOR[var,from,to,body]`+`v.ival`(downto), `TT_REPEAT[body,cond]`,
bare `TT_IF[cond,then]`. Realization lives in Pascal LOWER arms at the top of `lower_value`
(`src/lower/lower.c`): **`v_pascal_for`** (counted loop: synthesizes init+while+increment, reusing the
shared boxes) and **`v_pascal_repeat`** (post-tested until via direct four-port back-edge: `cond->ω=bα`).
Shared language-independent boxes (literal/binop/assign/`if`/`while`/seq) are reused via role dispatch.
Driver mode-2 is lang-agnostic (`scrip.c` `!is_icon && !is_prolog` branch finds `main`, runs
`IR_interp_once`). Also added `TT_SUCCEED`/`TT_FAIL` as no-op leaves in `lower_value` (empty statement,
language-independent). **11/11 probes byte-identical to `pint`**: hello, PB-4 (default-10 + multi-arg +
`:w` min-width), if/else, bare-if, while, for-to, for-downto, repeat-until, nested loops. Other frontends
regression-checked green (Icon hello, Prolog init, Raku rk_arith/rk_array_literal, SNOBOL4 pattern).

**⚠ (session 2 note — now RESOLVED in session 3, see top of watermark):** the lower.c call/if coupling
described below was excised by the switch-TT_*/switch-LANG refactor. Kept for history:
- `src/lower/lower.c:830` — Pascal calls rode **Icon's** det-call arm. **FIXED** → own arm + shared `v_det_call`.
- `src/lower/lower.c:289` — bare-`if` else-target rode **Raku's** branch. **FIXED** → shared arm via switch fall-through.
- `src/driver/polyglot.c:43,90,128` — generic proc-registration infra (still gated alongside Icon/Raku; low priority).

**Files touched session 2 (committed):** `src/contracts/IR.h`, `src/parser/snobol4/scrip_cc.h`,
`src/parser/pascal/pascal.{y,tab.c,tab.h}`, `src/driver/polyglot.c`, `src/lower/lower_program.c`,
`src/lower/lower.c`.

**Next:** (1) excise the coupling above (dedicated `v_pascal_call`); (2) PB-5 `sieve` array gate
(`TT_IDX`→`arr_get`, `TT_ASSIGN(TT_IDX)`→`arr_set_pure` Pascal arms + array-var decl/alloc + `sqr`);
(3) PB-6 flat procs (`recursion.pas`); (4) PB-7 nested-frame static-link-as-parent-port.

---

### Session 1 watermark (PB-0..PB-3 seed, superseded by the Pascal-rail rebuild above)

**2026-06-02 — PB-3 GREEN (seed alive), P4 case-sensitive only. The 7th frontend prints.**
`scrip --interp hello.pas` → `Hello World!`, byte-identical to the `pint` oracle. Also byte-identical
on a multi-statement + apostrophe-escape probe. Implemented PB-0..PB-3 via **Bison + Flex** (Lon
directive 2026-06-02 — the P4 grammar is clean SLR, one expected dangling-else shift/reduce conflict,
same as `pascalp.{l,y}`):

- `src/parser/pascal/pascal.l` — flex lexer, `%option prefix="pascal_yy"`. **Case-sensitive,
  lowercase-only P4 keywords; identifiers preserved verbatim** (Lon directive 2026-06-02: P4
  case-sensitive ONLY / P4 subset only, aligning Pascal with SCRIP's own case-sensitivity — dropped the
  earlier `caseless` + identifier-lowercasing). The all-lowercase P4 corpus is unaffected; mixed-case
  symbols (`BEGIN`, `WriteLn`) are now identifiers, not keywords (verified: uppercase `BEGIN` → parse
  error, as intended). Comments **both** `(* *)` and `{ }` (per PB-1 spec — but `pcom` itself only
  accepts `(* *)`, so oracle-comparison probes must avoid `{ }`; our `{ }` is a small ISO superset and
  the one spot to tighten if strict-P4-only is later wanted). String `'...'` with `''` escape via the
  single-regex `'([^']|'')*'` (no input/unput).
- `src/parser/pascal/pascal.y` — bison grammar adapted from the MIT `pascalp.y` (the goal's designated
  *syntactic* reference; original C, not transliterated from `pcom`). Full P4 statement/expression
  grammar present; declarations (label/const/type/var) parsed-and-discarded for now; AST built for
  statements + expressions. `writeln`→`write`, `write`→`writes` (SCRIP runtime `write` appends `\n`,
  `writes` does not).
- `src/parser/pascal/pascal_driver.{c,h}` — `pascal_compile()` → `pascal_parse_string()`.
- Generated `pascal.tab.{c,h}` + `pascal.lex.c` committed (regen via
  `scripts/regenerate_parser_and_lexer_from_sources.sh` — Pascal stanza added to that script at
  hand-off 2026-06-02).
- `Makefile`: pascal sources added to `SRCS` + three per-file compile rules (mirrors Raku). `make
  scrip` links them via the `$(OBJ)/*.o` glob.
- `src/driver/scrip.c`: `.pas` → `lang_pascal` → `pascal_compile`.

**Lowering reuse (the key seed decision):** Pascal rides the **Icon rail** for now — each routine is
emitted as a `TT_STMT{:lang=LANG_ICN, :subj=TT_PROC_DECL}`; the main program becomes
`TT_PROC_DECL{name="main", c[0]=TT_VAR, c[1]=TT_VLIST(params), c[2]=TT_PROGRAM(body)}`, exactly the
shape `lower_icon_body` consumes (requires `proc->n>=3`, body must be `TT_PROGRAM`). `writeln('...')`
lowers through the lang-independent `wire_det_builtin1` path (`IR_CALL dval=1.0` → `try_call_builtin_by_name`).
**Zero new lower.c / IR_interp.c / contract code** for the seed — the whole point of the goal's
"we already have almost all of this" premise. Top-level procedures/functions are collected flat (a
global `g_pascal_procs` accumulator) — correct for PB-6 flat procs; **nested-scope (PB-7) is NOT yet
modeled** (flattening loses lexical nesting — revisit at PB-7 with the static-link-as-parent-port design).

**Build:** `make scrip` clean (49 pascal symbols linked). Reference `pcom`+`pint` build under fpc.
Other frontends regression-checked (Icon `write`, Prolog `write` still green). Committed and pushed
(SCRIP + `.github`) at hand-off 2026-06-02.

**Next: PB-4 — integer output formatting (fully scoped 2026-06-02).** The grammar already parses
`var i: integer; i := 2+3; writeln(i)` and builds the right AST (`TT_ASSIGN` / `TT_ADD` / `TT_ILIT` /
`TT_VAR`), and the Icon rail **already executes the arithmetic + assignment correctly** (SCRIP computes
`5`). The ONLY gap is output formatting:

- **pint integer format rule (measured):** default field width **10**, right-justified, blank-padded
  (`5`→`␣␣␣␣␣␣␣␣␣5`, `42`→`␣␣␣␣␣␣␣␣42`, `12345`→`␣␣␣␣␣12345`). Explicit `:w` is a **minimum** width
  (`7:3`→`␣␣7`; `99:1`→`99` — full value emitted when it exceeds `w`). Strings print as-is (seed already
  matches). Reals/char/boolean formats: defer to a later rung.
- **Why it's non-trivial:** the shared `write`/`writes` builtin (`gen_runtime.c:506`) renders every arg
  generically via `descr_to_str` (integer → bare digits, no pad). Editing it would break Icon. There is
  **no** `right`/`left`/`repl`/`pad`/`format`/`concat` builtin in `script_builtins_byname.c` to pad with.
- **Recommended approach (descriptor-type dispatch — also solves the type problem):** add a small
  **Pascal-specific** runtime helper, e.g. `__pas_write(value, width)` / `__pas_writeln(value, width)`,
  registered in the byname dispatch. At runtime it inspects the descriptor: `IS_INT_fn` → right-justify
  per the width rule above (default 10 when width<0, else min-width); string → emit as-is; (reals etc.
  later). `writeln` variant appends `\n`. Then in `pascal.y` `mk_call`, route `write`/`writeln` to these
  helpers and pass width as a trailing arg — the grammar already parses `argument: expression COLON
  expression` (currently drops the `:w`; capture it instead, default -1). This keeps Pascal's
  type/width-dependent formatting *out* of the shared runtime. (Alternative: add a generic Icon-style
  `right`/`repl` primitive and synthesize padding in AST — more reusable but touches shared runtime.)
- **Validate** against `/tmp/w.pas` cases above (cat -A, byte-identical), then `sieve`-ward. Mind the
  16-bit `maxint=32767` overflow (match or document; `fact(8)` legitimately aborts in pint).

**Then:** PB-5 control flow (`sieve.pas`), PB-6 flat procs (`recursion.pas`), PB-7 nested-function
frames (the novel rung — replace the flat `g_pascal_procs` flattening with static-link-as-parent-port),
PB-8 aggregates, PB-9 mode-3/4 compiled BBs.

**Operational note:** PB-0..PB-3 are committed **locally only** (SCRIP `5fedaf7`, .github `b408d61e`) —
a container reset loses them. Persisting requires `git push` (the handoff step). Also still TODO: add a
Pascal stanza to `scripts/regenerate_parser_and_lexer_from_sources.sh`.
