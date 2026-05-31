# HANDOFF 2026-05-27 — Opus 4.7 — PROLOG-BB: rung25-TERM-STRING

**Goal:** GOAL-PROLOG-BB.md — close the only remaining rung25 fixture
(`rung25_term_string_term_string.pl`) by registering `term_string/2` as a
recognized BB_BUILTIN. The previous session (rung25-TERM2ATOM-OPS, `b0093cd1`)
landed the operator-notation writer; this session is the trivial paired
follow-up that wires `term_string` itself.

**Result:** ✅ Closed. GATE-3 mode-2 **90/107 → 91/107** (+1). All other gates held.
SCRIP `66d283ad`. Net diff `+17 / -1` across two files.

## Gate ledger (this session, fresh build, before → after)

| Gate | Before (`b0093cd1`) | After (`66d283ad`) |
|---|---|---|
| GATE-1 smoke prolog | 5/5 | 5/5 |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) | 132/0 (5 ORACLE_MISS) |
| GATE-3 mode-2 (`--interp`) | 90/107 | **91/107** (+1) |
| GATE-3 mode-3 (`--run`) | 89/107 | **90/107** (+1) |
| GATE-4 mode-4 minimal | 4/4 | 4/4 |
| Full mode-4 corpus | 28/107 | 28/107 |
| FACT RULE grep | 0 | 0 |
| Sibling smokes (icon/sno/raku/rebus) | 5/5/5/4 | 5/5/5/4 |

## What was wrong

`term_string/2` was never registered. The goal-file open-work list captured it
exactly:

> **term_string/2** (rung25 — open). Not registered as a builtin at all; needs
> lower_pl.c recognizer + bb_exec.c arm. Same shape as term_to_atom — just calls
> pl_term_to_string and unifies.

Running the fixture before the fix: silent fall-through, exit 0, empty output.
No recognizer in `lower_pl.c`'s BB_BUILTIN block meant the call lowered to a
generic BB_PL_CALL to an undefined predicate, which fails immediately.

## What landed (mirror of term_to_atom; mechanical port)

### `src/lower/lower_pl.c` — recognizer (line 366, +1/-1)

Added `term_string` next to `term_to_atom` in the BB_BUILTIN OR-chain:

```c
|| (strcmp(fn,"term_to_atom")==0 && e->n==2)  || (strcmp(fn,"term_string")==0 && e->n==2)
|| (strcmp(fn,"atom_number")==0 && e->n==2)
```

### `src/lower/bb_exec.c` — outer string-builtin dispatcher (line 3367, +1)

One-line addition to the if-condition so `term_string` calls reach the inner
per-builtin chain inside the dispatcher:

```c
||strcmp(fn,"string_chars")==0||strcmp(fn,"string_codes")==0||strcmp(fn,"term_to_atom")==0
||strcmp(fn,"term_string")==0
||strcmp(fn,"atom_number")==0||strcmp(fn,"copy_term")==0||...
```

### `src/lower/bb_exec.c` — term_string arm (+15)

12 lines of logic + 2 comment lines, inserted directly after the term_to_atom arm:

```c
/* term_string/2: forward-only mirror of term_to_atom. SCRIP strings == atoms (text).        */
/* Same pl_term_to_string path: operator-notation writer landed in rung25-TERM2ATOM-OPS.    */
if (strcmp(fn,"term_string")==0) {
    if (d0 && d0->tag!=TERM_VAR) {
        extern char *pl_term_to_string(Term *);
        char *s = pl_term_to_string(d0);
        if (!s) { nd->value=FAILDESCR; return nd->ω; }
        Term *at = term_new_atom(prolog_atom_intern(s)); free(s);
        if (!unify(t1, at, &g_pl_trail)) { trail_unwind(&g_pl_trail,mark); nd->value=FAILDESCR; return nd->ω; }
    } else {
        nd->value=FAILDESCR; return nd->ω;
    }
    nd->value=INTVAL(1); return nd->γ;
}
```

Reverse direction (string → term parse) deliberately unsupported; fails cleanly.

## Why this is the right shape

- **`pl_term_to_string`** already exists and already produces operator notation
  (the rung25-TERM2ATOM-OPS work from the same day extended `pl_write_to_file`
  with the op-prec block from `pl_writeq_term`). Re-using it costs nothing.
- **`term_to_atom`** is the structural twin: same dispatcher arm, same
  bidirectional shape, same forward-only fallback. Mirroring it is mechanical.
- **SCRIP strings ≡ atoms.** Verified: no `TERM_STRING` tag, no `term_new_string`,
  no `pl_string_*` helpers anywhere in `src/`. Every string-producing builtin
  (`atom_string`, `string_to_atom`, `string_chars`, etc.) uses
  `term_new_atom(prolog_atom_intern(s))`. `term_string` follows the same
  convention — and `write(S)` prints identically either way, so the
  `.expected` file matches byte-for-byte.
- **No emitter code touched.** FACT RULE compliance mechanically preserved.
  Confirmed by `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/`
  outside `_templates/` and `emit_core.c` → 0.
- **Mode-3 lift is free.** Post-V-5, `--run` routes through `sm_interp_run`,
  which dispatches BB_BUILTIN the same way `--interp` does. So adding the arm
  to `bb_exec.c` lights up both modes at once. Confirmed: all 3 rung25
  fixtures pass under `--run` after the fix.

## Output (byte-identical to .expected)

```
$ ./scrip --interp .../rung25_term_string_term_string.pl
point(3,4)
42

$ ./scrip --run .../rung25_term_string_term_string.pl
point(3,4)
42
```

## Mode-4 gap (explicit non-goal)

The mode-4 backend has no `bb_builtin.cpp` arm for either `term_to_atom` or
`term_string`. Both fall through to the unknown-builtin stub, which emits a
`# unknown 'term_string'` comment + `jmp γ` and leaves the result var
unbound (`_` output). The mode-4 corpus count is **unchanged at 28/107**.

These two builtins are paired CAT-D-* candidates. The template arm pattern is
the same: a single effect helper `rt_pl_term_to_atom(int do_string, void *t0, int k1,i1,s1)`
that fans out via the `do_string` flag, with the template selecting on `fn`. The
helper would mirror CAT-D-6 (`atom_chars/atom_codes`) shape — Path A scalar a0,
Path B `BB_PL_STRUCT` literal a0 via `emit_build_compound_term` post-order walker.
Estimated +4 mode-4 PASS (3 rung25 + likely sister fixtures elsewhere).

## Files touched

```
 src/lower/bb_exec.c  | 15 +++++++++++++++
 src/lower/lower_pl.c |  3 ++-
 2 files changed, 17 insertions(+), 1 deletion(-)
```

## NEXT (unchanged from prior session, less term_string)

1. **CAT-A-3** (BB_PL_CALL + BB_CHOICE β-resume) — still Lon-directive blocked.
   Biggest single unlock (estimated +15-25 PASS).
2. **PJ-AGW-5** (cut-barrier ω-rewiring) — make rung07 produce `yes\nno` not
   `yes\nyes`. Emit machinery ready (CAT-RUNG07-1); semantic work pending.
3. **rung18 plus/3** (bidirectional arith) — goal file claims `bb_exec.c` has the
   mode-2 arm but 3 rung18 fixtures still FAIL. Investigate gap: probably arm
   incomplete or only handles forward (X+Y bound → Z), not reverse modes
   (X+Z bound → Y, Y+Z bound → X).
4. **term_to_atom + term_string mode-4 emit** (paired CAT-D-* candidate as
   described above).

## Watermarks

- SCRIP HEAD: `66d283ad`
- .github HEAD: pending watermark + this handoff + GOAL update + PLAN update
