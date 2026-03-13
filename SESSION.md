# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `smoke-tests` (2/4 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `40ea84f` — WIP: materialise-once fix (partial) — SPAT_USER_CALL root cause confirmed |

## Last Thing That Happened

### Root cause of 0/21 found and partially fixed. One targeted change will finish it.

**Previous session's diagnosis was WRONG.** `nInc` body IS emitted correctly. The real
bug is in `snobol4_pattern.c`: `materialise()` was called once per scan position (0..N),
not once per match. Every `SPAT_USER_CALL` node eagerly calls the SNOBOL4 function during
materialise. `Reduce("'snoStmt'", 7)` pops 7 items from the parse stack at materialise
time — corrupting it before the match runs.

**Fix attempted this session (`40ea84f`):**
- Added `scan_start` to `EngineOpts` and `State` in `engine.h`/`engine.c`
- Fixed `scan_POS`: `z->PI->n == z->DELTA + z->scan_start` (absolute position)
- Fixed `scan_TAB`: `z->PI->n - z->DELTA - z->scan_start`
- Moved `materialise()` outside the scan loop in `sno_match_pattern` → calls once
- Same fix in `sno_match_and_replace`

**Why 0/21 still:** The fix works at the top level, but `var_resolve_callback` (fired
by the engine for `T_VARREF` nodes inside `ARBNO`) still calls `materialise()` on each
ARBNO iteration. `ARBNO(*snoCommand)` uses T_VARREF, which calls `var_resolve_callback`,
which calls `materialise(spat_of(snoCommand), ctx)`. That materialise re-fires all
`SPAT_USER_CALL` nodes including `Reduce()` → stack corruption continues.

**Debug artifacts:**
```bash
# 1257 SPAT_USER_CALL fires per match (confirmed via SNO_PAT_DEBUG=1)
# All from var_resolve_callback re-materialising snoCommand per ARBNO iteration
```

## One Next Action

**Fix `SPAT_USER_CALL` to NEVER call functions eagerly — always produce `T_FUNC`.**

Then fix `T_FUNC` + `user_call_fn` to handle `SNO_PATTERN` return values by
sub-matching the returned pattern at the current cursor position.

```
Files to change: src/runtime/snobol4/snobol4_pattern.c, src/runtime/engine.c

Step 1 — snobol4_pattern.c SPAT_USER_CALL case (around line 597):
  DELETE the SNO_PATTERN and SNO_STR eager branches entirely.
  ALL paths produce T_FUNC. The function is never called at materialise time.

  Current code:
    SnoVal result = sno_apply(sp->str, sp->args, sp->nargs);
    if (result.type == SNO_PATTERN) { return materialise(spat_of(result), ctx); }
    if (result.type == SNO_STR)     { ... T_LITERAL ... }
    /* else T_FUNC */

  New code:
    /* Always defer — never call at materialise time.
     * Side-effect functions (nInc, Reduce) must not fire during materialise,
     * which is called once per match (and per ARBNO iteration via var_resolve_callback).
     * Pattern-returning functions (reduce, icase) get their sub-pattern matched
     * at engine time via the extended T_FUNC callback (see engine.c). */
    /* fall through to T_FUNC */

Step 2 — snobol4_pattern.c UCData struct: add sub-match context
  typedef struct {
      const char *name;
      SnoVal     *args;
      int         nargs;
      /* Set at match time by the engine before calling user_call_fn: */
      const char **subj_ptr;   /* pointer to current subject pointer */
      int         *delta_ptr;  /* pointer to current cursor position */
      int          omega;      /* subject length */
  } UCData;

Step 3 — engine.c T_FUNC<<2|PROCEED: pass subject+cursor to callback
  Before calling func(func_data), set UCData fields from Z:
    UCData *d = (UCData *)Z.PI->func_data;
    if (d) {
        d->subj_ptr  = &Z.SIGMA;   /* NOT mutable — just pass Z.SIGMA + Z.DELTA */
        d->delta_ptr = &Z.DELTA;   /* or use a dedicated "result_advance" field */
        d->omega     = Z.OMEGA;
    }
    void *r = Z.PI->func(Z.PI->func_data);

Step 4 — user_call_fn in snobol4_pattern.c:
  static void *user_call_fn(void *userdata) {
      UCData *d = (UCData *)userdata;
      SnoVal r = sno_apply(d->name, d->args, d->nargs);
      if (r.type == SNO_FAIL) return (void *)(intptr_t)-1;
      if (r.type == SNO_PATTERN) {
          /* Sub-match the returned pattern at current position */
          const char *subj = d->SIGMA + d->DELTA;   /* current position */
          int         rem  = d->OMEGA - d->DELTA;
          SnoMatch m = sno_match_at(r, subj, rem);   /* new helper */
          if (m.failed) return (void *)(intptr_t)-1;
          d->DELTA += m.end;  /* advance cursor */
          return (void *)(intptr_t)2;  /* new sentinel: "cursor advanced" */
      }
      return (void *)1;  /* succeed zero-width */
  }

Step 5 — engine.c T_FUNC<<2|PROCEED handle cursor advance:
  void *r = Z.PI->func(Z.PI->func_data);
  if (r == (void *)(intptr_t)-1) { a = CONCEDE; z_up_fail(&Z, &psi); break; }
  if (r == (void *)(intptr_t)2) {
      /* cursor was advanced by sub-match — update Z.DELTA */
      UCData *d = (UCData *)Z.PI->func_data;
      Z.delta = Z.DELTA = d->DELTA_result;  /* or however we thread it */
  }
  a = SUCCEED; z_up(&Z, &psi); break;
```

**Simpler alternative if the above is too complex:**
Add a `sno_match_sub(SnoVal pat, const char *subj, int start, int len)` function
to `snobol4_pattern.c` that materialises and runs a pattern against a sub-string
at a specific offset with no scan loop. Then in `user_call_fn` call it directly
using thread-local globals for subject+cursor (single-threaded, safe).

```bash
# After fix, rebuild and test:
cd /home/claude/SNOBOL4-tiny
make -C src/sno2c

R=src/runtime/snobol4
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin
# Target: 21/21
```

## Rebuild Commands

```bash
cd /home/claude/SNOBOL4-tiny

# sno2c rebuild
make -C src/sno2c

# beauty compile
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c

# beauty binary
R=src/runtime/snobol4
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c \
    -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin

# smoke tests
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin

# crosscheck suite (after smoke passes)
bash /home/claude/SNOBOL4-corpus/crosscheck/run_all.sh

# oracle
SNO=/home/claude/snobol4-2.3.3/snobol4
$SNO -f -P256k -I /home/claude/SNOBOL4-corpus/programs/inc \
    /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    < /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    > /tmp/beauty_oracle.sno 2>/dev/null

diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
```

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-13 | materialise-once: scan_start in EngineOpts/State, POS/TAB fixed, materialise outside scan loop | SPAT_USER_CALL called N times per match, corrupting parse stack |
| 2026-03-13 | ROOT CAUSE: materialise() called per scan position, not per match | Reduce() pops stack at materialise time → 0/21 |
| 2026-03-13 | phantom skip fix: check entry_label in already-detection | nInc_ phantom added despite nInc real fn present |
| 2026-03-13 | deferred var_fn in Capture struct — apply_captures calls fn at match time | capture var=? was NULL for *FuncCall() targets |
| 2026-03-13 | field assignment fix (sno_field_set) | sno_iset treated field as indirect var |
| 2026-03-13 | Sprint 3 (`beauty-runtime`) complete — clean exit | first run worked |
| 2026-03-13 | Sprint 2 (`smoke-tests`) complete — 21/21 | hand-rolled lex/parse works |
| 2026-03-12 | Bison/Flex → hand-rolled-parser | LALR(1) unfixable (139 RR) |
