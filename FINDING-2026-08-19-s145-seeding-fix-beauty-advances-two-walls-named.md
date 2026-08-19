# FINDING s145 — THE SEEDING FIX LANDS: BEAUTY PARSES ITS OWN HEADER AND EMITS. TWO NEW WALLS, BOTH NAMED,
# ONE WITH A PRIME SUSPECT CARRYING RECEIPTS.

**Session:** 2026-08-19 s145 (HQ seat, Fable 5). SCRIP parent `6d47e61c` (pushed) + the M1-R0 seeding fix
staged in-tree at HQ; **commit gated on the 6-suite × 2-arm scorecard A/B running in background** — the full
diff is inline below so this FINDING is self-contained.

## THE FIX (M1-R0, executes s144 NEXT-SEAT (b)(c))
`src/runtime/core/core.c`, three edits, one killswitch:
1. `core_seed_names()` — `SCRIP_SEED_NAMES`, **default OFF = SPITBOL's true blank slate** (manual p.24); `=1`
   restores legacy pre-seeding byte-identically.
2. `core_lib_init`'s convenience block (`tab ht nl lf cr ff vt bs nul epsilon fSlash bSlash semicolon UCASE
   LCASE digits`) and the bare-`ALPHABET` seed: gated.
3. `NV_GET_fn`'s `"ALPHABET"` special-case (core.c:2213) — a SECOND site of the same class, hijacking the
   plain variable before the name table: gated. (`&ALPHABET` keyword reads never pass here —
   `rt_keyword_read_snobol4` serves the C array directly.)
```c
static int core_seed_names(void) { static int v = -1; if (v < 0) { const char * e = getenv("SCRIP_SEED_NAMES"); v = (e && *e == '1') ? 1 : 0; } return v; }
    if (core_seed_names()) NV_SET_fn("ALPHABET", BSTRVAL(alphabet, 256));
    if (core_seed_names()) {  /* the tab/ht/nl/.../digits block, unchanged inside */
    if (core_seed_names() && strcmp(name, "ALPHABET") == 0) return BSTRVAL(alphabet, 256);
```
**Gates so far:** witness `m1_alphabet_unreached_capture` green BOTH modes, `=1` restores legacy, mode-4 `.s`
md5 UNCHANGED (`e00674a3…` — runtime-only, zero codegen bytes). Oracle-truth probe now matches sbl on every
seeded name: `A[0] U[0] L[0] d[0] · nl[0] tab[0] semi[0]`.

## MEASURED — BEAUTY, BOTH MODES (input = beauty.sno, 40,971 bytes; oracle `-bf` = FIXED POINT, sanity green)
- **m4:** emits the 7-line header byte-true, then beauty's OWN `Parse Error` (its `mainErr1`, beauty.sno:617),
  echoes `START`, exits rc=0. NO ENGINE CRASH.
- **m3:** emits the same header (259 bytes) then **SIGSEGV in `zls_g_region` (`src/contracts/zeta_storage.c:930`)
  called from a JIT blob** — mode-3-only ζ-storage territory never reached before this fix.
- **Control (`SCRIP_SEED_NAMES=1`):** old behavior, no SEGV — both walls are DOWNSTREAM PROGRESS, not
  fix-caused corruption.
- **s144's original minimal repro is DEAD:** beauty on the single line `START` now echoes `START` = oracle.

## THE TWO WALLS
**B1 (both modes) — beauty's grammar rejects a line past the header.** PRIME SUSPECT WITH RECEIPTS:
`DATATYPE(null)` returns `"NULL"` in SCRIP where the oracle returns `"STRING"` (probe `eps=NULL` vs `eps=STRING`,
manual: DATATYPE of the null string is STRING) — and `ShiftReduce.inc`, beauty's parser CORE, calls DATATYPE
twice (XDump.inc ×4, TDump.inc ×1, assign.inc ×1, beauty.sno ×1). A one-site builtin fix with its own blast
radius: route to D-1' (next seat), verify with the m4 repro (clean, crash-free), then re-run self-host.
**B2 (m3 only) — `zls_g_region` SEGV.** ζ-storage, mode-3 slab path. Route to the ζ machinery per
GOAL-SNOBOL4-100's instrument; blocked on nothing (m4 gives B1 a crash-free lane meanwhile).

## ALSO ROUTED (same class, not this rung)
`NV_GET_fn` special-cases `STCOUNT/STNO/STLIMIT/ANCHOR/TRIM/FULLSCAN/CASE/MAXLNGTH/FTRACE/TRACE/ERRLIMIT/
CODE/FNCLEVEL/RTNTYPE` as bare names BEFORE table lookup (core.c:2199–2212) — a program's own variable named
`ANCHOR` etc. is likely hijacked identically (unprobed). **Lon's structural directive supersedes piecemeal
gating — KW-STATIC (grant recorded in GOAL-SNOBOL4-100 s145 cursor): "place all the keywords as statics in
the emitted asm and use direct references."** The special-case family dies wholesale there.
