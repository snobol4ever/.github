# FINDING 2026-09-12 hq_I — slice 1 landed, and the measurement says slice 2 is TWO sites, not sixty-seven

**Measured on** SCRIP `fc6ed7c5e` (slice 1 landed) · corpus `400e51634` · `RT_OPT=-O0` · measurer
hq_I, 2026-09-12. Instrumented `core_runtime_error` with a temporary probe, ran Icon programs,
removed the probe. Tree clean, gate re-verified at ARM B 16/16.

## Slice 1

The arithmetic error model is now chosen by the **lowerer** and passed as a capability instead of
being asked of two global cursors. `rt_div_zero` / `rt_real_zero_divisor` take it; `RT_BINOP_ENTRY`
generates two public faces per op; the Icon lowerer sets `BINOP_RAISE_ERRORS` and the template
selects `rt_div_raise` over `rt_div`.

⭐ **Face selection changes a NAME, not an ABI** — no call site passes an extra argument. That is what
made it affordable and it is the mechanism the remaining slices should reuse. The flag and the faces
are named for **what differs** (`_raise`), never for a language, so `test_gate_emit_no_lang.sh` still
passes: the emitter conditions on the IR graph and never on language.

## The measurement that sizes slice 2

I said I would not guess which codes an Icon program can reach `core_runtime_error` with. Probed:

| program set | Icon hits on `core_runtime_error` |
|---|---|
| arizona `general/errors.icn` | **0** |
| jcon `errors.icn` | **0** |
| jcon `misc.icn`, `others.icn` | **0** |
| the gate's 8 error witnesses + ad-hoc probes | **0** |

**Zero**, across the two files in the corpus whose entire purpose is to provoke error after error.
The SNOBOL4 control fired correctly in the same build (`1/0` → two hits at code 2), so the probe
works; Icon simply does not arrive there. Slice 1 removed the one route that did — division — by
sending it to `core_icn_error` directly.

⛔ **This does not make the inline discriminator harmless. It makes it nearly unreachable, which is
different, and the two remaining Icon call sites are the interesting part.**

## The two sites — and they are LIVE corruption, not latent

`src/runtime/icn_extfn.c` holds the only Icon-side calls:

| site | code | the message the caller passes | what `ic >= 101 ? icn_errmsg(ic)` substitutes |
|---|---|---|---|
| `:32` | 216 | "external function facility not provided by this runtime: *what*" | "external function not found" |
| `:111` | 301 | "too many arguments to an external function" | **"evaluation stack overflow"** |

The 301 case is the one to look at: an **arity** error would be reported as an **evaluation stack
overflow**. Not a reworded message — a different fault, with a different cause and a different fix.
Earlier I filed the 24-code substitution as *latent* because the SNOBOL4 side (`201` "unload
argument") is unreachable from Icon. These two are on the **Icon** side, so they are live whenever
reached. They are unreached today only because `cfuncs`/`extlvals` sit outside the baseline for want
of a vendored `libcfunc.so` — an accident of packaging, not a guard.

## What this means for the plan

Slice 2 was scoped at "presentation for 67 callers". **The measurement says it is 2 sites.** Give
`icn_extfn.c`'s two calls the Icon error path directly — with their own messages, which is also the
cure for the corruption above — and no Icon program reaches `core_runtime_error` at all. The inline
discriminator at `core.c:2655` is then dead for Icon and slice 3 deletes it rather than rewiring it.

⭐ **Third scope correction on this row, and each one came from running the code rather than reading
it.** 22 sites → 67 callers → 2 sites. The first two revisions were the census measuring who *calls*
a predicate; this one is measuring who *arrives*. Those are different questions, and only the last
one decides how much work there is.
