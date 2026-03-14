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
| **HEAD** | `fa98747` — EMERGENCY WIP: SPAT_USER_CALL denylist |

## Last Thing That Happened

### Root cause confirmed. Fix is structurally correct but T_FUNC not firing — one wiring issue remains.

**What this session established (architecturally important):**
- `sno_pat_*` / `engine.c` is a stopgap — NOT the destination
- Destination is compiled Byrd boxes (labeled goto C), same as `test/sprint*/` oracles
- Agreement recorded in PLAN.md: M-COMPILED-BYRD and M-PYTHON-UNIFIED are locked milestones
- Python pipeline (`lower.py`, `byrd_ir.py`, `emit_c_byrd.py`) is IP that must not be orphaned

**The bug:**

`materialise()` is called once per match AND once per ARBNO iteration via
`var_resolve_callback`. Every `SPAT_USER_CALL` node (nInc, nPush, nPop, Reduce,
reduce, TZ, etc.) fires inside `materialise()`. The stack-side-effect functions
(nInc, nPush, nPop, Reduce) must NOT fire at materialise time.

**Fix attempted — `fa98747`:**

Added `is_sideeffect_fn()` denylist: `nInc`, `nPop`, `nPush`, `Reduce`.
These now produce `T_FUNC` (deferred). All others stay on eager path.
`user_call_fn` handles `SNO_PATTERN` returns by calling `sno_match_pattern(r, subj)`.

**Why still 0/21:**

`user_call_fn` never fires. The `SPAT_USER_CALL nInc` debug line still appears
(confirming materialise is called per-ARBNO-iteration via var_resolve_callback) but
`user_call_fn: nInc` never prints — meaning the T_FUNC node is created but the engine
never PROCEED's it. The pattern fails BEFORE reaching the nInc T_FUNC node.

**Key insight from debug:**
```
SNO_PAT_DEBUG=1 output for subject "    X = 1\n":
  ENGINE_ENTRY slen=6 subj=X = 1
  engine_match_ex: slen=6 -> a=3 matched=0 end=0   ← CONCEDE immediately
```
The engine CONCEDEs at every starting position without ever firing T_FUNC.
This means the pattern tree rooted at snoCommand is failing before reaching nInc.

**The likely cause:**
`nInc` is the FIRST node in snoCommand:
  `snoCommand = nInc() FENCE(...)`
`nInc()` returns `sno_pat_cond(epsilon, "?")` — a conditional capture pattern.
When deferred as T_FUNC, it produces a zero-width node. But `sno_pat_cond` returns
a full SnoPattern — the T_FUNC just calls `sno_apply("nInc")` and gets back a pattern,
then calls `sno_match_pattern(r, subj)` on it. That sub-match spawns a NEW top-level
scan loop against the full subject — this is wrong. The returned pattern should be
matched at the CURRENT cursor position, not as a new top-level scan.

## One Next Action

**The right fix for nInc/nPush/nPop: materialise their returned pattern ONCE at
materialise time (it's always the same pattern — `epsilon . "?"`), but call the
function itself at match time via a two-phase approach.**

Specifically — `nInc()` always returns the same pattern structure. What changes
per-call is only the SIDE EFFECT (incrementing the counter). The pattern it returns
(`epsilon . "?"`) is always identical. So the fix is:

**Option A (simplest):** Call `nInc()` eagerly at materialise time to get the pattern
structure, BUT strip the side-effect by noting that `nInc` is called ONCE per match
(materialise is now called once per match at the top level). The var_resolve_callback
problem is that it re-materialises `snoCommand` per ARBNO iteration.

The REAL fix is to prevent `var_resolve_callback` from re-materialising `snoCommand`
on every ARBNO iteration. Instead, materialise `snoCommand` ONCE and reuse the
Pattern* tree. Cache it.

**Option B (correct, targeted):**
In `var_resolve_callback`, cache the materialised Pattern* per variable name.
If we've already materialised `snoCommand` this match, return the cached Pattern*.

```c
/* In var_resolve_callback — add a cache to MatchCtx */
typedef struct {
    const char *name;
    Pattern    *root;
} VarCache;

/* In MatchCtx, add: */
VarCache var_cache[32];
int      var_cache_n;

/* In var_resolve_callback: */
for (int i = 0; i < ctx->var_cache_n; i++)
    if (strcmp(ctx->var_cache[i].name, name) == 0)
        return ctx->var_cache[i].root;   /* reuse */
Pattern *root = materialise(sp, ctx);
ctx->var_cache[ctx->var_cache_n++] = (VarCache){name, root};
return root;
```

This means `snoCommand` is materialised ONCE per match (not once per ARBNO iteration).
`nInc`/`nPush`/`nPop` fire ONCE at materialise time (correct — they set up capture
wrappers) and the T_FUNC approach is not needed at all.

**Revert `fa98747` changes to `snobol4_pattern.c`** and implement Option B instead.

```bash
cd /home/claude/SNOBOL4-tiny

# Rebuild
R=src/runtime/snobol4
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin

# Test
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin
```

## Rebuild Commands

```bash
cd /home/claude/SNOBOL4-tiny

make -C src/sno2c

src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c

R=src/runtime/snobol4
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c \
    -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin

bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin

# Oracle
SNO=/home/claude/snobol4-2.3.3/snobol4
$SNO -f -P256k -I /home/claude/SNOBOL4-corpus/programs/inc \
    /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    < /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    > /tmp/beauty_oracle.sno 2>/dev/null
```

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-13 | SPAT_USER_CALL denylist (fa98747) — nInc/nPush/nPop/Reduce → T_FUNC | Eager call corrupts stack; but T_FUNC never fires — wrong approach |
| 2026-03-13 | Architecture recorded: sno_pat_* is stopgap, M-COMPILED-BYRD + M-PYTHON-UNIFIED locked | Agreement with Lon |
| 2026-03-13 | materialise-once: scan_start in EngineOpts/State, POS/TAB fixed, materialise outside scan loop | SPAT_USER_CALL called N times per match, corrupting parse stack |
| 2026-03-13 | ROOT CAUSE: materialise() called per scan position, not per match | Reduce() pops stack at materialise time → 0/21 |
