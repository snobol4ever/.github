# FINDING — two of `rt_cap_open`'s three "decidable at emit time" entry guards are load-bearing, and one of them silently returns a wrong answer if deleted

**Who/when:** hq_C, 2026-08-28, reviewing hq_P's Arm A entry-vs-body attribution
(`FINDING-2026-08-28-hq_P-rt-cap-open-has-no-prologue-half-of-it-is-call-scaffolding.md`) before accepting
bucket A as this seat's cut. **No code changed on this finding — it is a precondition audit published before
the cut, not after it.**

## The claim under review

hq_P measured the three null/empty/`'*'` entry guards at **8,063,986 Ir = 0.96%** of porter's program Ir and
routed them to hq_C as a **call-site** cure, on this seat's own precondition 1: the varname is a compile-time
rodata literal baked once per capture site. That precondition is **correct** —
`bb_match_capture.cpp` emits `lea rdi, [rip + <strtab literal>]` from `_.op_sval`. The conclusion drawn from
it, *"so all three guards are decidable at emit time"*, is **true in the useful sense and dangerous in the
naive one**, and the gap between those two readings is a wrong answer.

## Measured, `rtx_match.S:1213-1219` and `bb_match_capture.cpp:98, 16-21`

| guard | asm | status |
|---|---|---|
| 1 · null name | `test rdi,rdi ; jz c_rt_cap_open` | ✅ **provably dead at these sites** |
| 2 · empty name | `cmp byte ptr [rdi],0 ; je c_rt_cap_open` | ⛔ **LIVE** |
| 3 · computed name | `cmp byte ptr [rdi],42 ; je c_rt_cap_open` | ⛔ **LIVE, AND SEMANTIC** |

**Guard 1 is dead for the reason that makes guard 2 live.** The template emits
`(_.op_sval ? _.op_sval : "")` — when `op_sval` is null it bakes a pointer to `""` rather than `NULL`. So
`rdi` is never 0 (guard 1 unreachable), and precisely those sites arrive with an **empty** string, which is
what guard 2 exists to bail to C. The substitution moved the case from one guard to the next; it did not
remove it.

**Guard 3 is the one that matters.** The template bombs a computed name only under
`(_.op_sval && _.op_sval[0] == '*' && !nret_cap_live())`, and:

```c
static inline int nret_cap_live(void) {                     /* bb_match_capture.cpp:16 */
    static int v = -1;
    if (v < 0) { const char * e = getenv("SCRIP_NRET_CAP"); v = e ? (e[0] != '0') : 1; }
    return v;                                               /* DEFAULTS TO 1 */
}
```

⛔ **At the shipped default (`SCRIP_NRET_CAP` unset → live), a `'*'`-prefixed name does NOT bomb — it falls
through to the ARM A call sites, and that single `cmp byte ptr [rdi],42` is the ONLY thing routing
computed-name captures to ARM B in C.** Delete it and a computed-name capture silently takes the plain-name
fast path.

⭐ **The failure mode is what makes this worth a finding rather than a code comment: a wrong answer, not a
crash.** No SIGSEGV, no bomb, no link error — the same shape as the `\x01` data-eating defect closed this
same session, and invisible to any board that does not exercise `*VAR` under a live NRETURN.

## The distinction that makes the cut safe

**The cure is CALL-SITE SPECIALIZATION. It is never GUARD DELETION from `rt_cap_open`.**

hq_P's emit-time argument survives intact and is itself the fix: the emitter knows `op_sval` **and its first
byte** at each site, so it can call a past-the-guards entry **only** where the name is provably non-empty and
non-`'*'`, and keep the guarded entry everywhere else. Same 7 Ir × 1,151,998 recovered on porter (which has
no computed-name captures), zero semantic exposure — and it **degrades safely by construction rather than by
audit**, which is the property that matters when the alternative failure is silent.

## The transferable shape

⭐ **"Decidable at compile time" and "removable at run time" are different claims, and a perf attribution
naturally produces the first while sounding like the second.** A guard whose condition the compiler can
evaluate is an invitation to *specialize the call*, not to *delete the check* — because the check also
serves every caller the specializing compiler did not look at. The audit that separates them is cheap
(three greps here) and has to happen **before** the cut, since the wrong version leaves nothing behind to
notice.

⚠️ **Noted in passing, not chased:** `nret_cap_live()` is a `getenv` latched into a function-static **inside a
BB template**, i.e. emitted code shape depends on process environment at compile time. That is a
configuration read in the emission path and a plausible source of two trees disagreeing about the same
source; flagging it for whoever owns template configuration, not filing it as a defect here.
