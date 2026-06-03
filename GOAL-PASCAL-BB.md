# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes, from zero

**Repo:** SCRIP (frontend + lower) · corpus (reference compiler at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT STATE — READ FIRST

**Watermark — PB-6b COMPLETE (parameterless function call). 2026-06-03, session 8. SCRIP HEAD = 521726d.**
PB-0..PB-7 + PB-6b green. **PB-6b (parameterless function call in expression) DONE.** A bare identifier in
`factor` that names a declared function now correctly generates a zero-arg call, not a variable read. Gate
`flatnoarg.pas` prints **`10`** (was `0`), byte-identical to `pint`. All PB-0..PB-7 probes + cross-language
baselines unchanged.

**The fix (two parts):**
- **Parser (`pascal.y`)**: Added `g_pas_funcs[256]` table + `pas_func_add`/`pas_is_func`. All `FUNCTIONSY`
  declarations (forward + full) call `pas_func_add(name)` at parse time. `mk_ident` now checks the table:
  if the name is a known function, return `mk_call(name, NULL)` (zero-arg `TT_FNC`) instead of `TT_VAR`.
  Reset `g_pas_nfunc = 0` in `pascal_parse_string`.
- **Lowerer (`lower.c`, `v_assign`)**: Added Pascal-guarded case for `TT_FNC` LHS (the result-variable
  assignment pattern `fn_name := expr` that now parses as `TT_ASSIGN(TT_FNC, expr)`): extract callee name
  from `lhs_t->c[0]->v.sval` and emit `IR_ASSIGN` with that name — same behavior as the former `TT_VAR` path.
  Comes before the `lhs_is_var` check; no other paths affected.

**Why this is correct:** Inside function `five`'s body, `five := 5` has LHS `selector → IDENT("five")` →
`mk_ident("five")` → now `mk_call("five", NULL)` (TT_FNC). The lowerer's new TT_FNC-LHS arm extracts "five"
→ `IR_ASSIGN("five", 5)`. "five" is not in the frame scope → NV write → correct result-var assignment.
Outside (in expression context), `five` in `g := five + five` → `TT_FNC` → `v_det_call` → `IR_CALL("five",
0)` → interpreter invokes `five`'s body → returns NV("five") = 5. Two calls sum to 10. ✓

**Zero cross-language regression (stash→rebuild→diff prescribed method not used; direct rebuild + suite run):**
Icon `--interp` full ladder **130 PASS / 117 FAIL / 36 XFAIL** identical to PB-7 baseline; Prolog honest
mode-2 **132/132, 0 ABORT** identical. All PB-0..PB-7 probes byte-identical, `flatnoarg.pas` now PASS.

**All prior context (PB-7 design model, static-link-as-static-chain, etc.) unchanged — see below.**

**The model (grounded in `pint`'s `base(ld)` + `lod/str (level−vlev)`):** a frame slot is value / reference
(PB-6) / *or now* reachable from a descendant via the static chain. `ProcEntry.decl_level` = lexical level the
routine is **declared** at (main scope = 1; top-level procs = 1, bodies run at 2; their nested = 2, bodies at 3…).
`GenFrame` gains `GenFrame *static_link` + `int level`. At call setup `static_link = pas_base(caller,
caller_level − callee_decl_level)` (the `mst (level−pflev)` rule), `frame.level = decl_level+1`. Uplevel access
reuses PB-6's `Loc` chase: `IR_VAR`/`IR_ASSIGN`, if the name isn't in the current frame's scope, walk
`static_link` (Pascal-guarded) and read/write the found `(frame,slot)` **before** the NV fallthrough. The chain
**bottoms out at NV**: a top-level proc's `static_link` is NULL, a walk reaching NULL resolves against NV — keeps
`sieve` globals + the accidental-pass `nested.pas` correct. Recursion is correct because each call captures the
**caller's** activation as the link before `frame_depth++`, so a nested helper always mutates its *own* parent
activation's local (the `nestrec` proof).

**Files (SCRIP, this commit):** `stage2.h` (`ProcEntry.decl_level`); `pascal.{y,tab.c,tab.h}` (lexical-level
counter via mid-rule `pas_proc_enter`/`pas_proc_exit` on `procedure_decl`'s block; previously-discarded
**non-array local var names** now captured per-proc and appended as a trailing `TT_VLIST` child whose container
`v.ival` carries `decl_level`; regen via the direct `bison -d -o pascal.tab.c pascal.y` workaround,
`pascal.lex.c`/`pascal.l` unchanged; the 1 s/r conflict is the pre-existing dangling-else, **no new conflict**);
`lower_program.c` (`is_function` made **type-aware** — return-var is `TT_VAR`, locals child is `TT_VLIST`, so a
procedure's trailing locals VLIST is never mistaken for a return-var; `lower_sc` = params **then** locals;
`decl_level` read off the locals VLIST); `IR_interp.c` (`pas_base`/`pas_uplevel_find`; `pas_loc_of_name` extended
to chase uplevel so a `var` actual that is an enclosing-frame local resolves too; static-link+level set at the
dval==3.0 call setup, Pascal-guarded; uplevel walk in `IR_VAR`/`IR_ASSIGN` before NV; param loop extended to seat
locals init `NULVCL`); `GenFrame` from `gen_runtime.h`.

**Probes (corpus/programs/pascal/, committed):** `nestrec.pas` byte-identical (`11,21,31`) — the gate;
`nestcount.pas` (sibling nested procs share an outer counter → `3`); `nest2.pas` (three-level nesting, innermost
does a **Δ2 grandparent** uplevel read+write and a Δ1 → `15,101`); `nestfunc.pas` (a nested **function** with its
own param reading uplevel `base`+`n` and returning → `213`). All PB-6 probes + `sieve`/`nested` stay
byte-identical; `recursion` matches through `fact(7)`.

**Proven zero cross-language regression (stash→rebuild→diff, the prescribed method):** Icon `--interp` full
ladder **130 PASS / 117 FAIL / 36 XFAIL identical baseline-vs-post**; Prolog honest mode-2 **132/132, 0 ABORT
identical**. Baseline `nestrec` confirmed `11,11,11`, post `11,21,31`. All edits stay isolated to the
`LANG_PASCAL`/`IR_LANG_PAS`-guarded path.

**SEPARATE GAP FOUND — parameterless function call in an expression (its own rung, NOT PB-7).** A bare identifier
in `factor` parses as `selector → mk_ident → TT_VAR` (a variable read); only `IDENT(...)` with parens becomes a
call. So a zero-arg function used in an expression (`x := f + f`) reads an unset variable → `0`. This hits **flat
functions too** (discriminating probe `flatnoarg.pas`, committed, XFAIL: oracle `10`, scrip `0`), so it is
orthogonal to nesting — no prior probe exposed it because `fact`/`fib`/`inner(k)` are all parameterized. The fix
needs its own design: the parser/lower must know which identifiers are **function names** and turn a non-local
bare-IDENT-that-is-a-function into a call (careful not to turn genuine variable reads into calls). Recommend as
the next small rung **PB-6b** before PB-8.

**16-bit overflow (still deferred).** `fact(8)`=40320 > `maxint`=32767: `pint` traps, SCRIP computes 40320. Its
own integer-model rung.

**PB-6 value+`var` params (sessions 5–6) — still green.** Value params + functions + procedures +
procedure-as-statement; `var` (pass-by-reference) via the unified slot-reference model (a frame slot is a value or
a reference to a location `(frame,slot)`/`(NULL,NV-name)`; setup resolves the actual's location in the caller,
chasing → transitivity + `f(a,a)` aliasing; `var` actuals that aren't simple variables still fall back to
by-value). `varparam`/`swap`/`alias`/`vartrans`/`varframe`/`varmix` byte-identical.

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
- [x] **PB-7 — NESTED procedures & functions (THE NEW RUNG).** A routine declared inside another,
  reading/writing the enclosing locals. **DONE** via static-link-as-static-chain: `ProcEntry.decl_level`,
  `GenFrame.static_link`+`level`, parser lexical-level counter + non-array-local capture, `lower_sc`
  params-then-locals, `pas_base(caller, caller_level−decl_level)` at call setup, uplevel walk in
  `IR_VAR`/`IR_ASSIGN` before NV. Gate `nestrec.pas` `11,21,31`; probes `nestcount`/`nest2`/`nestfunc`
  byte-identical; Icon 130/117/36 + Prolog 132/0/0 identical baseline-vs-post.
- [x] **PB-6b — Parameterless function call in an expression (SEPARATE GAP, recommend before PB-8).** A bare
  identifier in `factor` parses as a variable read, not a call; only `IDENT(...)` becomes a call. So a zero-arg
  function in an expression (`x := f`) reads an unset variable → `0`. Hits flat functions too (probe
  `flatnoarg.pas`, XFAIL: oracle `10`, scrip `0`) — orthogonal to nesting. Fix: parser/lower must know function
  names and promote a non-local bare-IDENT-that-is-a-function to a call (without turning genuine variable reads
  into calls). `pcom.pas` uses these heavily. **DONE**: `g_pas_funcs` table in parser; `mk_ident` promotes;
  `v_assign` TT_FNC-LHS arm handles `fn := expr` result-var assignment. `flatnoarg.pas` PASS (oracle 10). ✓
- [ ] **PB-8 — Aggregates as needed.** `record`, `array`, `set`, pointers/`new`. Add only what later probes
  require; `pint`'s store layout is the semantics oracle.
- [ ] **PB-9 — Cross onto compiled BBs (mode-3/4).** Convert Pascal's boxes to the `x86()` self-encoding API
  per the FACT RULES (one `x86(...)` concat per box, `bb_emit_x86`, no `bb_bin_t`). Rebase onto
  `x86_asm.h` first. Only after the mode-2 ladder is comfortably green.
