# MODE3-DISPATCH-GAP.md — mode-3 still runs `sm_interp_run` for 4/5 languages

**Surfaced:** 2026-05-28 (Sonnet, GOAL-RAKU-BB session)
**Status:** OPEN — directive collision plus empirical hard data, needs Lon's call

---

## Lon's directive (2026-05-28, stated 3+ times this session)

> "Ensure mode 3 is running flat-wired x86 SM's and BB's and not the interpreter
> versions which are reserved for SCRIP mode 2!"

Strict reading: mode-3 = **flat-wired x86 for SM AND BB**. `sm_interp_run` is
mode-2 only. Treated as binding.

## Empirical reality (verified 2026-05-28 with stderr probe)

Inserted one-line probe at `scrip.c:518` (the `sm_run_with_recovery(&s2->sm,
sm_interp_run)` fall-through in the `mode_run` branch). Ran `M3_TRACE_DISPATCH=1
./scrip --run test/raku/rk_class26.raku` — probe fired. Plain `--run` IS the C
interpreter for Raku today. Probe reverted before commit.

## Honest Raku corpus measurement (this session)

| Engine | Mechanism | rk_class26 | Total |
|---|---|---|---|
| `--interp` (true mode-2) | `sm_interp_run` | PASS | 23/33 |
| `--run` (called "mode-3" today) | `sm_interp_run` ← interpreter | PASS | 23/33 |
| `--run SCRIP_M3_NATIVE=1` (real mode-3) | `sm_run_native` flat-wired x86 | CRASH (segv after 2nd say) | **11/33, 20 crashes** |
| `--compile` (mode-4) | x86 binary, libscrip_rt | PASS | 26/33 |

The "Crosscheck 37/37" line in the GOAL-RAKU-BB watermark was meaningless: it
was comparing `sm_interp_run` output to `sm_interp_run` output and reporting
"modes 2 and 3 agree." Same engine, two flags.

## Per-test mode-3 (SCRIP_M3_NATIVE=1) results

```
PASS:  rk_arith rk_arrays rk_control rk_forloop rk_hash17 rk_hashes
       rk_str22 rk_strings rk_typed_vars rk_unless_until rk_vars  (11)
FAIL:  rk_junctions rk_stdio39                                    (2)
CRASH: rk_class26 rk_combinator rk_fileio38 rk_for_array
       rk_for_array_simple rk_for_array_underscore rk_gather rk_given
       rk_given18 rk_interp rk_map_grep_sort24 rk_range_for
       rk_re32 rk_re33 rk_re34 rk_re35 rk_re37 rk_regex23
       rk_subs rk_try_catch25                                     (20)
```

## What the conflicting prior directive says (2026-05-27)

`scrip.c:467-476` (CAT-D-12-S1, Opus 4.7, GOAL-PROLOG-BB):

> Per Lon directive (2026-05-27): mode-3 = "SM in-memory walk via sm_interp_run
> + BB flat-wired (bb_build_flat into bb_pool slab, sealed RX, jumped into from
> SM_BB_SWITCH)" — identical to how SNOBOL4 has worked all along.

That directive is the codebase's current operating principle. Lon's 2026-05-28
statement overrides it.

## What this session DID land

| Goal | Mode-2 | Mode-3 native | Mode-4 |
|---|---|---|---|
| rk_class26 (RECORD_REGISTER SM call + handler) | PASS ✅ | CRASH (sm_run_native engine issue) | PASS ✅ |

The fix is correct at the SM emission level (idempotent runtime call to
icn_record_register). Mode-3's crash is in `sm_run_native` itself — a different
engine, separate failure surface. The fix does not regress any path.

## What this session is NOT landing

- **No silent enforcement of strict mode-3.** Adding `abort()` at scrip.c:518
  breaks ~40 test scripts that invoke `scrip` without explicit mode flags
  (default = `--run`). Out of scope for one continue.
- **No `sm_run_native` repair.** 20 crashes across the corpus indicate the
  flat-wired SM engine has fundamental gaps for Raku (likely around method
  dispatch, gather/take, frame slots — overlapping with the open RK-BB-4 work).
  This is its own goal, not a side patch.

## Recommended path forward

Spin a goal — `GOAL-MODE3-NO-INTERP.md` (or fold into existing GOAL-RAKU-BB
as a new rung) — with structure mirroring IBB ground-zero:

1. Surface the C-interpreter fall-through with an `abort()` gated by env
   `SCRIP_M3_REQUIRE_NATIVE=1` (opt-in for tests/dev that want strict mode).
2. Switch the dispatch policy from "env opts you INTO native, else interpreter"
   to "env opts you INTO interpreter (legacy), else native (strict)." That
   inverts the bias.
3. Fix `sm_run_native` crashes one test at a time (20 to triage).
4. Update all 40+ test scripts that depend on the silent fall-through to
   either pass explicit `SCRIP_M3_LEGACY=1` or to expect the new native
   behavior.

Estimated scope: several sessions, one engine fix per failure cluster.

— Sonnet, 2026-05-28
