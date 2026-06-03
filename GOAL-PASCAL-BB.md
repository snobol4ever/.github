# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes, from zero

**Repo:** SCRIP (frontend + lower) · corpus (reference compiler at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT STATE — READ FIRST

**Watermark — PB-6 COMPLETE (value + `var` params). 2026-06-03, session 6. SCRIP HEAD `aebf204` on `e09dcc2`.**
PB-0..PB-6 green. **PB-6 value-param portion** (session 5): value-parameter functions/procedures/calls,
`recursion.pas` byte-identical to `pint` through `fact(7)`, `proc_stmt.pas`/`addtwo.pas` byte-identical;
functions tagged with a return-var `c[3]` child on `TT_PROC_DECL`, body ends `IR_RETURN` whose `α` is
`IR_VAR(funcname)`, recursion correct because each call clears `FRAME.returning` before the enclosing NV write.

**PB-6 `var` (pass-by-reference) params DONE (session 6) — the unified slot-reference model.** Designed once
from `pint` (`lda`+`ind`/`sto` = a param slot holding an address that every use dereferences; the same `base()`
machinery PB-7 uplevel uses), NOT copy-out. A frame slot is either a **value** or a **reference to a location**
`(GenFrame*, slot)` or `(NULL, NV-name)` — top-level `main` runs frame-less so its vars (e.g. `varparam`'s `k`)
live in NV, the `(NULL,name)` case. `var`-param call setup resolves the actual's location **in the caller**
(chasing if the caller's own var is already a reference → gives transitivity + `f(a,a)` aliasing for free) and
installs it as the callee slot's reference; reads/writes chase to the home. **Files (SCRIP `aebf204`):**
`stage2.h` (`ProcEntry.byref_mask`), `pascal.{y,tab.c,tab.h}` (VARSY params sentinel-tagged; `mk_proc` folds the
byref bitmask onto the unused `TT_VLIST` container `v.ival` — no child clobbered, arity intact; regen via the
direct `bison -d -o pascal.tab.c pascal.y` workaround, `pascal.lex.c`/`pascal.l` unchanged), `polyglot.c`
(populate `byref_mask` from the VLIST, `LANG_PASCAL`-guarded), `gen_runtime.h` (`GenFrame` gains
`SlotRef slotref[]`), `IR_interp.c` (`pas_slot_read`/`pas_slot_write`/`pas_loc_of_name` chase helpers;
`IR_VAR`/`IR_ASSIGN` intercept reference slots **before** the `sv.v!=0` NV-fallthrough; install refs at the
dval==3.0 call setup, capturing `caller` before `frame_depth++`).

**Probes (corpus/programs/pascal/, committed):** `varparam.pas` byte-identical to `pint` (`7`); the
copy-out-would-fail cases all byte-identical — `swap.pas` (two-way), `alias.pas` (`addto(a,a)`→`11`),
`vartrans.pas` (var passed onward as var), `varframe.pas` (callee writes a live ancestor frame slot — the
PB-7-shaped case); `varmix.pas` confirms value params untouched. One honest limitation: a `var` actual that
isn't a simple variable (array element `a[i]`, record field) falls back to by-value (guarded
`call_blks[k]->entry->t == IR_VAR`); `pcom.pas` will eventually need it but no probe does yet.

**Proven zero cross-language regression (stash→rebuild→diff):** Icon `--interp` full ladder **130 PASS / 117
FAIL / 36 XFAIL identical baseline-vs-post** (the 117 are rung36 advanced reflection/scan/structures, not
Pascal); Prolog honest mode-2 **132/132, 0 ABORT**. Pascal edits stay isolated to the `LANG_PASCAL` path.

**16-bit overflow (still deferred, NOT a PB-6 blocker).** `fact(8)`=40320 > `maxint`=32767: `pint` traps
(ERangeError) with an unmatchable fpc crash dump; SCRIP computes 40320. Needs its own Pascal integer-model rung
(overflow detection + clean abort + writeln arg-eval ordering).

**Next — PB-7 (NESTED routines), DESIGNED, build held for Lon's nod on the static-link representation.** Gap
characterized by the discriminating probe `nestrec.pas` (committed): recursive `outer` with a nested `inner`
mutating a per-activation local — `pint` `11,21,31`, SCRIP `11,11,11` (because procedure **locals aren't
frame-scoped** — they fall through to one shared NV global; `fact`/`fib` only dodge this by using params + the
NV-return trick, and the simple `nested.pas` passes only *accidentally* via that shared NV). Frame-scoping locals
and static-link uplevel are **coupled** (frame-scoping alone regresses `nested.pas`), so PB-7 is one design.
Full design grounded in `pcom`/`pint` (lexical `level`, walk count `use_level−decl_level`, call static link
`mst (level−pflev)` = `base()`): each `ProcEntry` gains `decl_level`; `lower_sc` = params **then** locals;
`GenFrame` gains `GenFrame *static_link` (a **static chain, not a display** — matches `pint`, satisfies "no
separate display array", becomes the parent-port thread in mode-3/4); the chain **bottoms out at NV** for
frame-less `main` (top-level proc's `static_link`=NULL → walk reaching NULL resolves against NV — keeps `sieve`
globals + `nested.pas` from regressing); **uplevel access reuses the PB-6 `(frame,slot)` Loc + chase** — it just
produces the Loc by walking static links instead of by chasing a reference. Implementation plan + the
representation fork are in `HANDOFF-2026-06-03-OPUS48-PASCAL-BB-PB6-VARPARAM-PB7-DESIGN.md`. Deferred: per-activation
local arrays in nested/recursive procs (array-fill prologue still global-name-based; no probe needs it). Then
PB-8 aggregates / PB-9 mode-3/4.

**Two residual issues (NOT introduced by Pascal work — flagged for attention):**
- `scripts/regenerate_parser_and_lexer_from_sources.sh` is `set -e` and ABORTS at the snobol4 flex step
  (clobbers `snobol4.lex.c`, never reaches the Pascal stanza at the end). Workaround: regen Pascal directly —
  `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y && flex --noline -o pascal.lex.c pascal.l` —
  then `git checkout` the snobol4 generated files. Script wants a fix.
- `test/raku/rk_array_literal.raku` FAILS on the CLEAN baseline (pre-existing, proven by stash+rebuild).

**Lower-priority Icon adjacency (driver plumbing, not LOWER semantics):** `src/driver/polyglot.c:43,90,128`
— `LANG_PASCAL` is gated alongside `LANG_ICN`/`LANG_RAKU` in the init guard, proc-table collection, and
`nparams` shape. Break into its own clauses when convenient for zero adjacency.

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

- [x] **PB-0 — Orient.** Reference `pcom`+`pint` built; grammar/opcodes read.
- [x] **PB-1 — Lexer → `TT_*`.** Pascal flex lexer, case-sensitive lowercase-only P4 keywords, `(* *)`+`{ }`
  comments, `'...'` strings with `''` escape.
- [x] **PB-2 — Parser → AST.** Bison grammar from MIT `pascalp.y`; full P4 statement/expression grammar;
  declarations parsed (const/array tables built, rest discarded for now).
- [x] **PB-3 — SEED.** `scrip --interp hello.pas` prints `Hello World!`, byte-identical to `pint`.
- [x] **PB-4 — Integers, `var`, assignment, `writeln(int)`.** `__pas_writeln`/`__pas_write` width formatting,
  byte-identical to `pint`. (16-bit overflow deferred to PB-6.)
- [x] **PB-5 — Control flow + `sieve.pas` gate.** All control flow byte-identical to `pint` via Pascal LOWER
  arms on real `TT_FOR`/`TT_REPEAT`/`TT_IF` (IR-direct, not desugaring). Arrays + const + `sqr` + booleans;
  `sieve.pas` gate MET (25 primes, 2..97).

- [x] **PB-6 — Top-level (flat) procedures & functions.** Value params + functions + procedures +
  procedure-as-statement (session 5): `recursion.pas` byte-identical to `pint` through `fact(7)`. **`var`
  (pass-by-reference) params DONE** (session 6) via the unified slot-reference model — a frame slot is a value
  or a reference to a location `(frame,slot)`/`(NULL,NV-name)`; setup resolves the actual's location in the
  caller (chasing → transitivity + `f(a,a)` aliasing) and installs it as the callee slot's reference; the
  primitive PB-7 uplevel reuses. `varparam`/`swap`/`alias`/`vartrans`/`varframe` byte-identical to `pint`; zero
  cross-language regression proven (Icon 130/117/36, Prolog 132/0/0 identical baseline-vs-post). Open-but-not-a-
  blocker: `var` actuals that aren't simple variables (array element/field) fall back to by-value. **DEFERRED:
  16-bit overflow** (`fact(8)` aborts in `pint` with an unmatchable fpc crash dump) — its own integer-model rung.
- [ ] **PB-7 — NESTED procedures & functions (THE NEW RUNG).** A routine declared inside another,
  reading/writing the enclosing locals. Implement static-link-as-parent-port: each activation a BB, uplevel
  access walks parent links, 100% BB, stackless. **Design it here, once, carefully.** Probe: a nested helper
  that reads & mutates an enclosing routine's local **while the enclosing routine is still active** (e.g. a
  nested `partition` referencing the outer `quicksort`'s array, or a nested proc bumping an outer counter).
- [ ] **PB-8 — Aggregates as needed.** `record`, `array`, `set`, pointers/`new`. Add only what later probes
  require; `pint`'s store layout is the semantics oracle.
- [ ] **PB-9 — Cross onto compiled BBs (mode-3/4).** Convert Pascal's boxes to the `x86()` self-encoding API
  per the FACT RULES (one `x86(...)` concat per box, `bb_emit_x86`, no `bb_bin_t`). Rebase onto
  `x86_asm.h` first. Only after the mode-2 ladder is comfortably green.
