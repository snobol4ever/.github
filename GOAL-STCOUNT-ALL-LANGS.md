# GOAL-STCOUNT-ALL-LANGS.md — Universal &STCOUNT / &STLIMIT for All Languages

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
**Done when:** `&STCOUNT` and `&STLIMIT` work as first-class keywords in all
six frontends (SNOBOL4, Icon, Prolog, Raku, Snocone, Rebus). Every statement
executed by any frontend increments `&STCOUNT`. Setting `&STLIMIT` terminates
execution when the count exceeds the limit. Programs can read `&STCOUNT` to
observe how many statements have executed. This is a SCRIP enhancement —
a shared capability added to classic and new languages alike.

---

## Motivation

SNOBOL4 has had `&STCOUNT` / `&STLIMIT` since SPITBOL. It is invaluable for:
- Detecting infinite loops (set `&STLIMIT = 10000000`)
- Instrumented testing (read `&STCOUNT` before and after a call)
- The in-process sync monitor (`GOAL-INPROC-MONITOR`) — hooks at SM_STNO
  (which already fires per statement and drives `&STCOUNT` in SNOBOL4)

The same infrastructure (`kw_stcount` / `kw_stlimit` globals, `comm_stno()`
function, `SM_STNO` opcode) already exists. Wiring it for the other five
frontends costs near zero — it is a keyword table lookup in `interp_eval`.

For Snocone and Rebus, `&STCOUNT` / `&STLIMIT` are especially valuable
because these languages have no built-in loop guard today. A Snocone while
loop with a bug runs forever. With `&STLIMIT` that becomes a clean error.

---

## Architecture — what already exists

```c
/* In interp.c (from SNOBOL4): */
long kw_stcount = 0;    /* &STCOUNT — incremented by comm_stno() */
long kw_stlimit = -1;   /* &STLIMIT — -1 means unlimited */

void comm_stno(void) {
    kw_stcount++;
    if (kw_stlimit >= 0 && kw_stcount > kw_stlimit)
        sno_runtime_error(22);  /* STLIMIT exceeded */
}
```

`SM_STNO` in `sm_interp.c` calls `comm_stno()` at every statement boundary.
`execute_program()` calls `comm_stno()` at every statement.

`&STCOUNT` and `&STLIMIT` are already keywords in the SNOBOL4 keyword dispatch
in `interp_eval`. The fix for other languages: make `interp_eval` handle
`E_KEYWORD` with `sval = "STCOUNT"` / `"STLIMIT"` regardless of `g_lang`.

---

## Steps

### Phase 1 — Make &STCOUNT / &STLIMIT language-agnostic in interp_eval

- [ ] **ST-1** — Audit keyword dispatch in `interp.c`.
  Find where `E_KEYWORD` sval is checked. Confirm `&STCOUNT` / `&STLIMIT`
  are currently gated on `g_lang == LANG_SNO` or handled only in SNOBOL4
  keyword table. Gate: make scrip clean.

- [ ] **ST-2** — Move `&STCOUNT` / `&STLIMIT` to the language-agnostic
  keyword block in `interp_eval`. Any `E_KEYWORD` with sval `"STCOUNT"` or
  `"STLIMIT"` returns `kw_stcount` / `kw_stlimit` regardless of g_lang.
  Gate: make scrip clean; PASS=31 FAIL=0.

- [ ] **ST-3** — Make `comm_stno()` fire for Icon, Prolog, Raku, Snocone, Rebus.
  Currently `execute_program()` calls `comm_stno()` at every stmt — but Icon
  statements route through `icn_call_proc` / `bb_broker` which may bypass it.
  Audit: does `SM_STNO` fire for LANG_ICN / LANG_PL stmts in sm_interp?
  Fix any gaps. Gate: `&STCOUNT` increments correctly for all six languages.

- [ ] **ST-4** — Test &STCOUNT in SNOBOL4 (regression):
  ```snobol4
          &STLIMIT = 1000000
          OUTPUT = &STCOUNT
  END
  ```
  Gate: outputs a small integer (number of stmts executed to that point).

- [ ] **ST-5** — Test &STCOUNT in Icon:
  ```icon
  procedure main()
    write(&STCOUNT);
  end
  ```
  Gate: outputs an integer (not zero, not error).

- [ ] **ST-6** — Test &STCOUNT in Prolog:
  ```prolog
  :- initialization(main).
  main :- X is &STCOUNT, write(X), nl.
  ```
  Gate: outputs an integer.
  Note: Prolog syntax for keywords may need a parser tweak — use `stcount`
  builtin predicate if `&` sigil is awkward in Prolog syntax.

- [ ] **ST-7** — Test &STCOUNT in Raku:
  ```raku
  sub main() { say(&STCOUNT); }
  ```
  Gate: outputs an integer.

- [ ] **ST-8** — Test &STCOUNT in Snocone:
  ```snocone
  OUTPUT = &STCOUNT
  ```
  Gate: outputs an integer.
  Snocone uses `&KEYWORD` syntax already (e.g. `&STLIMIT = 10000000`).

- [ ] **ST-9** — Test &STCOUNT in Rebus:
  Rebus: `OUTPUT := &STCOUNT` if `&` sigil is accepted, else wire as
  a builtin `stcount()` function.
  Gate: outputs an integer.

### Phase 2 — &STLIMIT as loop guard for all languages

- [ ] **ST-10** — Verify &STLIMIT terminates infinite loops for all languages.
  Write one infinite-loop test per language. Set &STLIMIT = 100.
  Confirm each exits with STLIMIT exceeded error, not hang.

  Tests:
  - SNOBOL4: `LOOP :(LOOP)` with `&STLIMIT = 100`
  - Icon: `while 1 = 1 do write("x")` with `&STLIMIT := 100`
  - Prolog: `loop :- loop. main :- loop.` with stlimit(100)
  - Raku: `while 1 { say("x") }` with `&STLIMIT = 100`
  - Snocone: `while (1) { OUTPUT = "x"; }` with `&STLIMIT = 100`
  - Rebus: `while 1 do OUTPUT := "x"` with `&STLIMIT = 100`

  Gate: all six terminate cleanly within the limit.

- [ ] **ST-11** — Write `scripts/test_stcount_all_langs.sh`.
  Runs ST-4 through ST-10 tests. Gate: all PASS.

### Phase 3 — Snocone &-keyword syntax

- [ ] **ST-12** — Add `&STCOUNT` and `&STLIMIT` to Snocone lexer/parser.
  Snocone already accepts `&STLIMIT = N` at top level (inherits from SNOBOL4).
  Confirm `&STCOUNT` reads correctly. If not: add `&`-keyword token to
  `snocone_lex.c` → maps to E_KEYWORD in IR.
  Gate: Snocone programs can read/set &STCOUNT and &STLIMIT.

- [ ] **ST-13** — Add `&STCOUNT` and `&STLIMIT` to Rebus lexer/parser.
  Rebus uses `:=` assignment. `&STLIMIT := 100` should work.
  If `&` not in Rebus lexer: add token or wire as `stcount()` builtin.
  Gate: Rebus programs can read/set &STCOUNT.

### Phase 4 — Additional SCRIP keywords (shared across all languages)

These are the SCRIP enhancements — shared keywords that any frontend can use:

- [ ] **ST-14** — `&TRACE` — statement-level trace flag.
  When non-zero: prints `[STNO label]` before each statement.
  Wire to `g_opt_trace` which already exists in interp.c.
  Available in all six languages via E_KEYWORD dispatch.
  Gate: `&TRACE = 1` in any language produces statement trace output.

- [ ] **ST-15** — `&ANCHOR` — pattern anchor flag (SNOBOL4 already has it).
  Wire to existing `kw_anchor` global for all languages that use
  pattern matching (SNOBOL4, Snocone, Rebus).
  Gate: `&ANCHOR = 1` forces anchored pattern match in Snocone.

- [ ] **ST-16** — `&ERRTYPE` / `&ERRLIMIT` — runtime error control.
  Wire existing SNOBOL4 error keyword infrastructure to all languages.
  Gate: `&ERRLIMIT = 5` limits errors in any language.

- [ ] **ST-17** — Document all shared SCRIP keywords in a new file:
  `src/driver/scrip_keywords.md`.
  List every `&KEYWORD` that works across all six frontends, with semantics.
  This becomes the reference for future frontend authors.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `kw_stcount`, `kw_stlimit`, `comm_stno()` |
| `src/runtime/x86/sm_interp.c` | `SM_STNO` → `comm_stno()` |
| `src/frontend/snobol4/snobol4.y` | SNOBOL4 keyword table (reference) |
| `src/frontend/snocone/snocone_lex.c` | Snocone lexer — add &-keywords |
| `src/frontend/rebus/lex.rebus.c` | Rebus lexer — add &-keywords |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every step.
- `&STCOUNT` / `&STLIMIT` behave identically in all languages.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=31
```

---

## Current state (2026-04-14, SCRIP HEAD 11d9e9c9)

ST-1 through ST-17 all open.
Next: ST-1 — audit keyword dispatch in interp.c.
