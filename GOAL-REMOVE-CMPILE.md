# GOAL-REMOVE-CMPILE — Excise CMPILE, Unify on Bison/Flex Parser

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** CMPILE.c is not compiled into the scrip binary; all three
parse entry points (program, expression, statement-block) route through
snobol4.tab.c/snobol4.lex.c; omega driver PASS=15/15; beauty suite PASS≥15.

## Why

CMPILE.c is a hand-written recursive-descent parser running in parallel
with bison/flex (snobol4.tab.c + snobol4.lex.c). It produces `CMPND_t`
trees with SIL `stype` constants (VARTYP=3, FNCTYP=5, BINGFN, …) that
are completely separate from the `EKind` enum in `ir.h` used by `EXPR_t`.
The bridge `cmpnd_to_expr()` is incomplete — unhandled stypes (e.g. BINGFN
for `~`) leak raw stype integers into EXPR_t kind fields, causing silent
misroutes in `interp_eval_pat` and elsewhere.

CMPILE is NOT dead code — `snobol4_pattern.c` does `#include "CMPILE.c"`
directly (line 24), pulling in ~3000 lines unconditionally. This must be
removed.

## The Omega Bug Context (what triggered this)

S-1 of GOAL-TWO-STEP-HUNT (omega driver) required routing `EVAL(string)`
through `interp_eval_pat`. The hook `g_eval_str_hook → _eval_str_impl_fn`
was added. The CMPILE parse path produced `CMPND_t` with `BINGFN(~)` at
stype=22 leaking into EXPR_t kind field — unrecognised by `interp_eval_pat`
— causing EVAL("(pat ~ 'id') $ tx *LEQ(...)") to fail.

The fix is the bison path. `_eval_str_impl_fn` already calls
`parse_expr_pat_from_str` (new function in snobol4.tab.c). That function
exists but returns null because the bison grammar puts bare expressions
into `s->subject` (not `s->pattern`) when parsed as a statement.

## Three Parse Entry Points

| Entry | Input | Current (CMPILE) | Replacement (bison) |
|-------|-------|-----------------|---------------------|
| **CODE_t** | FILE* or path | `cmpile_file()` → `cmpile_lower()` | `sno_parse(FILE*, name)` — already exists |
| **Expression** | bare expr string | `cmpile_eval_expr()` → `cmpnd_to_expr()` | `parse_expr_pat_from_str(src)` — new in snobol4.tab.c |
| **Statement block** | multi-stmt string | `cmpile_string()` → `cmpile_lower()` | `sno_parse_string(src)` — new in snobol4.tab.c |

## Key Design: parse_expr_pat_from_str

Lives inside `snobol4.tab.c` where `Lex`, `PP`, `g_lx`, `snobol4_parse`
are all defined. Cannot be implemented outside that TU.

**Wrapping strategy** — confirmed by session investigation:
- `parse_expr_from_str("LEN(1)")` calls `parse_expr(lx)` which returns
  `prog->head->subject`. For bare expressions bison puts the expr in
  `subject`. This already works for simple cases.
- The problem: `parse_expr_from_str` returns subject of first stmt, which
  for `_SNO_DUMMY_ LEN(1)` is `_SNO_DUMMY_` (the var), not `LEN(1)`.
- **Correct wrapper**: pass `src` directly (no dummy prefix). Bison parses
  `LEN(1)` as a subject expression. Return `s->subject` (not s->pattern).
- For pattern-context expressions with `$`, `@`, `*`: bison grammar already
  handles these in the subject/pattern position. Return `s->pattern` if
  set, else `s->subject`.

**Unit test required** (S-1 gate) — compile standalone against snobol4.tab.c
+ snobol4.lex.c and verify:
```
parse_expr_pat_from_str("LEN(1)")              → E_FNC kind, sval="LEN"
parse_expr_pat_from_str("@txOfs $ *LEN(1)")   → non-null, has E_CAPT_CURSOR
parse_expr_pat_from_str("(pat ~ 'id') $ tx")  → non-null, no BINGFN leak
```

## Key Design: sno_parse_string

```c
CODE_t *sno_parse_string(const char *src) {
    Lex lx = {0};
    lex_open_str(&lx, src, strlen(src), 0);
    CODE_t *prog = calloc(1, sizeof *prog);
    PP p = {prog, NULL};
    g_lx = &lx;
    snobol4_parse(&p);
    return prog;
}
```
Lives in `snobol4.tab.c`. Declared in `scrip_cc.h`.

## Call Sites to Migrate

| File | Function | CMPILE call | Replacement |
|------|----------|-------------|-------------|
| `eval_code.c` | `eval_expr()` | `cmpile_eval_expr`→`cmpnd_to_expr`→`eval_node` | `parse_expr_from_str(src)`→`eval_node` |
| `eval_code.c` | `CONVE_fn()` | `cmpile_eval_expr`→`cmpnd_to_expr` | `parse_expr_pat_from_str(src)` returns EXPR_t*, wrap as DT_E |
| `eval_code.c` | `code()` | `cmpile_string`→`cmpile_lower` | `sno_parse_string(src)` |
| `eval_code.c` | alt-pattern rebuild (line ~299) | `eval_via_cmpile` restring | `parse_expr_pat_from_str` |
| `snobol4_pattern.c` | `compile_to_expression()` | `cmpile_eval_expr`→`cmpnd_to_expr` | `parse_expr_pat_from_str(src)` wrap as DT_E |
| `snobol4_pattern.c` | `eval_via_cmpile()` | `EXPR()`→`cmpnd_to_expr`→`eval_node` | `parse_expr_pat_from_str(src)`→`interp_eval_pat` (call via hook) |
| `scrip.c` | `_eval_str_impl_fn()` | already calls `parse_expr_pat_from_str` ✓ | fix S-1 so it works |
| `scrip.c` | `cmpile_lower()` bridge | full CMPILE pipeline | remove; `--dump-parse` routes via `sno_parse_string` + IR dump |
| `scrip.c` | `cmpile_init/add_include` | CMPILE init | remove entirely |

## Current State of scrip Binary (session 2026-04-13)

- S-1..S-6 complete — CMPILE fully removed from scrip binary
- `nm scrip | grep -i cmpile` → CLEAN
- `parse_expr_pat_from_str` fixed: direct src, appends \\n, returns s->pattern||s->subject
- `sno_parse_string` added to snobol4.tab.c, declared in scrip_cc.h
- `eval_code.c`, `snobol4_pattern.c`, `scrip.c` all off CMPILE
- Beauty suite: PASS=15/18 (Gen/TDump/XDump pre-existing pat_cat stderr noise)
- omega driver: PASS=15/15
- HEAD: 476fd067 on origin/main
- NOTE: upstream Prolog commit (bca2b79a) added prolog_interp.h; `make scrip` needs
  that header present — scrip binary from session is valid, rebuild may need header fix

## Steps

- [x] **S-1** — Fix `parse_expr_pat_from_str` in `snobol4.tab.c`.
  Pass `src` directly (no `_SNO_DUMMY_` prefix). Return `s->pattern` if
  set, else `s->subject`. Run unit test (standalone binary against
  snobol4.tab.c + snobol4.lex.c). Gate: all three unit test cases non-null
  with correct kind values, no BINGFN leakage.

- [x] **S-2** — Add `sno_parse_string` to `snobol4.tab.c`. Declare in
  `scrip_cc.h`. Gate: `code("OUTPUT = 'hello'")` executes correctly.

- [x] **S-3** — Migrate `eval_code.c` off CMPILE:
  - `eval_expr()` → `parse_expr_from_str` → `eval_node`
  - `CONVE_fn()` → `parse_expr_pat_from_str`, wrap result as DT_E
  - `code()` → `sno_parse_string`
  - Remove `#include CMPILE.h`, `extern cmpnd_to_expr`, `extern cmpile_lower`
  Gate: beauty suite PASS≥14.

- [x] **S-4** — Migrate `snobol4_pattern.c` off CMPILE:
  - `compile_to_expression()` → `parse_expr_pat_from_str`, wrap as DT_E
  - `eval_via_cmpile()` → `parse_expr_pat_from_str` → route via
    `g_eval_pat_hook` / direct `interp_eval_pat` if available, else `eval_node`
  - Remove `#include "CMPILE.c"` (line 24)
  - Remove `cmpnd_to_expr()` definition
  Gate: beauty suite PASS≥14.

- [x] **S-5** — Migrate `scrip.c` off CMPILE:
  - Remove `#include CMPILE.h`
  - Remove `cmpile_lower()` bridge function (~40 lines)
  - Replace `--dump-parse` with `sno_parse_string` + IR printer, or remove flag
  - Remove `cmpile_init()`, `cmpile_add_include()` calls
  Gate: `scrip --run` works; beauty suite PASS≥14.

- [x] **S-6** — Verify CMPILE fully removed:
  `make scrip` clean; `nm scrip | grep -i cmpile` empty;
  `grep -r '#include.*CMPILE' src/` empty.

- [x] **S-7** — omega driver PASS=15/15.
  `parse_expr_pat_from_str` now correctly handles all EVAL(string) cases
  via `g_eval_str_hook`. Gate: omega driver passes all 15 tests.

- [x] **S-8** — Full beauty suite: PASS≥15 (omega fixed + no regression).

## Commit identity
Always: `LCherryholmes` / `lcherryh@yahoo.com`

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```
