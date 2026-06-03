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
- [ ] **PB-4 — Integers, `var`, assignment, `writeln(int)`.** `var i: integer; i := 2 + 3; writeln(i)`.
  Reuse existing integer literal / arithmetic / assignment / load-store IR. Remember the reference
  models a 16-bit `maxint = 32767` — match its overflow behavior or document the divergence.
- [ ] **PB-5 — Control flow.** `if/then/else`, `while/do`, `for/to`/`downto`, `repeat/until`. Reuse the
  existing conditional + loop boxes. **Target program: `sieve.pas`** (pure control flow + boolean array)
  — when SCRIP's `--interp` output matches `pint`'s primes-under-100, PB-5 is done.
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

**2026-06-02 — PB-3 GREEN (seed alive). The 7th frontend prints.** `scrip --interp hello.pas` →
`Hello World!`, byte-identical to the `pint` oracle. Also byte-identical on a multi-statement +
apostrophe-escape probe. Implemented PB-0..PB-3 via **Bison + Flex** (Lon directive 2026-06-02 — the
P4 grammar is clean SLR, one expected dangling-else shift/reduce conflict, same as `pascalp.{l,y}`):

- `src/parser/pascal/pascal.l` — flex lexer, `%option prefix="pascal_yy" caseless`. Case-insensitive
  keywords + lowercased identifiers (Pascal semantics). Comments **both** `(* *)` and `{ }` (per PB-1
  spec — note `pcom` itself only accepts `(* *)`, so oracle-comparison probes must avoid `{ }`; our
  `{ }` support is a clean ISO superset, not a divergence). String `'...'` with `''` escape via the
  single-regex `'([^']|'')*'` (no input/unput).
- `src/parser/pascal/pascal.y` — bison grammar adapted from the MIT `pascalp.y` (the goal's designated
  *syntactic* reference; original C, not transliterated from `pcom`). Full P4 statement/expression
  grammar present; declarations (label/const/type/var) parsed-and-discarded for now; AST built for
  statements + expressions. `writeln`→`write`, `write`→`writes` (SCRIP runtime `write` appends `\n`,
  `writes` does not).
- `src/parser/pascal/pascal_driver.{c,h}` — `pascal_compile()` → `pascal_parse_string()`.
- Generated `pascal.tab.{c,h}` + `pascal.lex.c` committed (regen via
  `scripts/regenerate_parser_and_lexer_from_sources.sh` — **Pascal stanza still needs adding to that
  script**; for now regenerate manually: `bison -d -o pascal.tab.c pascal.y && flex --noline -o
  pascal.lex.c pascal.l`).
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
Other frontends regression-checked (Icon `write`, Prolog `write` still green). `main` not yet committed
at time of writing — commit pending.

**Next: PB-4** (integers / `var` / assignment / `writeln(int)` — `sieve`-ward). The grammar already
parses these and builds `TT_ASSIGN` / `TT_ADD` / `TT_ILIT` / `TT_VAR`; what's unverified is whether the
Icon-rail lowering + `--interp` execute them correctly and whether `writeln(i)` (int arg) routes through
`write` properly. Eyeball `var i: integer; i := 2+3; writeln(i)` against `pint`. Watch the 16-bit
`maxint=32767` overflow semantics (document or match).
