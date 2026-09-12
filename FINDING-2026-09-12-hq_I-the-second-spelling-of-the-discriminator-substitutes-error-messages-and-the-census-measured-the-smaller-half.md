# FINDING 2026-09-12 hq_I — the second spelling of the discriminator SUBSTITUTES error messages, and the census measured the smaller half

**Measured on** SCRIP `70a0bc6c0` · corpus `400e51634` · `RT_OPT=-O0` · measurer hq_I, 2026-09-12.
Found by **attempting** the CEO-600 cure and backing it out, not by censusing. The attempt is the
method here: every number below is one a static census could not have produced.

## 1. The census measured the smaller half, and the test said so

I threaded the capability through the arithmetic chain — `rt_div_zero` and `rt_real_zero_divisor`
taking `int icn` instead of asking `core_icn_active()`, and `RT_BINOP_ENTRY` generating `fn` and
`fn##_icn` from one shared static. It compiled clean, and the **dual-face mechanism is sound**: face
selection changes a *name*, so there is no call-site ABI change anywhere. That half should be reused.

Then, with `rt_div_zero` passing `icn=0`, **Icon's `1/0` still raised 201.** The `core_icn_active()`
branch I had just cured was never what produced it.

The real converter is the **inline copy at `core.c:2655`**, inside `core_runtime_error`, and
`core_runtime_error` has **67 runtime callers**. My reported figure — 6 emitter-visible roots, 27
call sites, 59 references — measured only the named predicate's callers.

⭐ **A census can see who CALLS a predicate. It cannot see which path actually produces the observed
behaviour.** Those are different questions, and I answered the second with evidence for the first.

## 2. The discriminator does not merely choose a FORMAT — it substitutes MESSAGES

```c
int ic = code == 2 ? 201 : code == 22 ? 106 : code;
const char *im = code == 2 ? "division by zero"
               : code == 22 ? "procedure or integer expected"
               : (ic >= 101 ? icn_errmsg(ic) : (msg ? msg : ""));
```

The clause `ic >= 101 ? icn_errmsg(ic)` assumes **any code ≥ 101 is an Icon error number**. It is not.
`core_runtime_error` is called with **37 distinct codes**, and **24 of them are ≥ 101**:

```
103 116 160 164 174 187 198 199 201 216 242 248 251 286 301 305 307 310 312 314 315 321 341 342
```

These are SNOBOL4-side codes. The collision is exact and live in the source: `core.c:849` raises
`core_runtime_error(201, "unload argument is not natural variable name")`, and `icn_errmsg(201)` is
`"division by zero"`. Under the Icon arm that call reports **division by zero** for an `UNLOAD`
argument problem — the caller's own message discarded and replaced by an unrelated one.

⛔ **This is latent, not live, and I am saying so rather than overclaiming**: `UNLOAD` is SNOBOL4's,
so no Icon program reaches that site today. The hazard is structural — the discriminator being wrong
does not merely change a report's shape, it swaps the sentence for a different error's sentence, on
**24 codes**. That is a much worse failure mode than the one the row was opened for, and it is a
second, independent argument for removing the ambient answer.

## 3. `core_runtime_error` answers seven questions; the discriminator is one

Threading a capability into it inherits all seven — which is exactly hq_U's warning today, after they
put an error code into a shared classification to answer one question and the `&ERRLIMIT` arm read
the same list for a different one, moving eleven codes on evidence about one.

1. compat mapping (`core_err_compat_map`) · 2. default message lookup for codes 1–39 ·
3. `&error`/errjmp trapping · 4. SETEXIT and `&ERRLIMIT` · 5. **report presentation (the
discriminator)** · 6. **code remap 2→201, 22→106 (the discriminator)** · 7. terminality and `exit(1)`.

## 4. What bounds the cure

Only **7 call sites** pass the two codes the discriminator actually remaps (5 in `arithmetic.c`, one
in `rt/rt.c`, one in `core.c`). So the *remap* half is bounded at 7, not 67. The *presentation* half
is what reaches all 67, and the open question — which I have NOT answered and will not guess — is
which codes an Icon program can reach `core_runtime_error` with at all. `icn_extfn.c` proves the set
is larger than {2, 22}.

## 5. The gate caught my own regression, by number

The slice regressed **202 → 201** (with `icn=0` the inline map collapses MOD onto DIV) and made
**204 vanish**. ARM B named both, in both modes. ⭐ A count would have reported "2 of 8 wrong" and
sent the next author hunting two missing raises, instead of showing that **MOD had collapsed onto
DIV** — precisely the uneven, partial drift hq_U predicted a regression here would look like.

Reverted. Tree re-measured clean: ARM A red, ARM B 16/16, nothing left behind.
