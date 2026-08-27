# FINDING 2026-08-27 hq_C — THE OPSYN DEFECT IS **NOT** REBINDING, **NOT** OPERATOR-SPECIFIC, **NOT** m4-ONLY, AND **NOT** NONDETERMINISTIC UB

**Row:** `conform-opsyn-operator-rebind-gz5-fatal` / R-8's residue, raised by seat06 as `q-opsyn-rebind-twice-nondeterministic`.
**Tree:** SCRIP `e052a502` · pristine `-O0`. Oracle `/home/resources/x64/bin/sbl -bf`.

## ⛔ FOUR FRAMING CLAIMS, ALL REFUTED BY MEASUREMENT

seat06 handed off a careful, honest brief: *"a runtime call-dispatch bug for OPSYN-established names in compiled mode … looks memory-layout-sensitive/nondeterministic … consistent with real UB moving gdb's own observation around,"* and recommended valgrind/ASan. **I ran the tool. It is clean, and each part of the frame is wrong** — which is worth more than the recommendation was.

| claim | measured |
|---|---|
| "rebind **twice**" | ⛔ **A SINGLE alias fails.** No rebinding required. |
| "**operator** dispatch" | ⛔ **A plain function-name alias fails**: `OPSYN('foo','cat',0)`, no operator anywhere. |
| "**compiled mode** (m4)" | ⛔ **m3 SIGSEGVs** on that witness — worse than m4, which merely goes silent. |
| "nondeterministic / UB" | ⛔ **Deterministic 5/5 in both modes, and valgrind reports `0 errors from 0 contexts`.** |

**THE MINIMAL WITNESS** (valid SNOBOL4 — the oracle runs it):

```
	DEFINE('cat(a,b)')	:(ce)
cat	cat = a b	:(RETURN)
ce
	OPSYN('foo', 'cat', 0)
	OUTPUT = foo('abc','def')
END
```

| arm | result |
|---|---|
| oracle `sbl -bf` | ✅ `abcdef` |
| scrip **m3** | ⛔ **SIGSEGV, rc=139, 5 of 5 runs** |
| scrip **m4** | ⛔ **rc=0, empty output, 5 of 5 runs** (silent wrong answer) |
| **valgrind** on the m4 arm | **0 errors** — not memory corruption |

⭐ **This is also an `m3 ≢ m4` DESIGN-INVARIANT violation** (crash vs silent-empty), which makes it this HQ's lane regardless of which row owns it.

## ⭐⭐ THE COMPILER IS ALREADY DOING THE RIGHT THING — THE RUNTIME IS THE BROKEN HALF

The original witness's own comment states the rule: *"An OPSYN'd operator is rebindable at RUNTIME, repeatedly — so no call site may cache its meaning."* Everyone (the brief included) read the defect as **caching**. **ASM-DIFF-FIRST on a true passing/failing sibling pair says the opposite:**

| witness | emitted at the `&` use site | result |
|---|---|---|
| one `OPSYN` | `.string "cat"` — **statically resolved**, direct call | ✅ works |
| two `OPSYN`s | `.string "&"` + `call rt_call_arr_bl@PLT` — **runtime by-name dispatch** | ⛔ empty |

**The compiler correctly REFUSES to cache once it cannot prove a single binding, and emits the by-name dispatch. The by-name dispatch is what fails.** ⛔ So the single-`OPSYN` case passing is not evidence the mechanism works — **it passes by never using it.** That masking is why this looked like a rebinding bug: the second binding is not what breaks it, it is merely what stops the compiler from routing around the broken path.

⛔ **AND IT EXPLAINS THE "RETROACTIVE" SYMPTOM.** In the two-`OPSYN` witness the **first** `OUTPUT`, sequenced *before* the second `OPSYN` executes, also goes empty. That looks impossible for a runtime-rebinding bug and is trivial for this one: both use sites were compiled to the same by-name dispatch, so both fail. Exit is clean (`rc=0`, exactly 2 bytes of stdout = two empty lines) — both statements ran and the expression evaluated to **null**.

## HYPOTHESIS FOR THE MECHANISM — CODE-READ, **NOT** MEASURED

`opsyn()` (`pattern_match.c:440-461`) ends in `register_fn_alias(nm, old)`. `register_fn_alias` (`core.c:2766`) searches `_func_buckets` for `oldname`; **on a miss it takes an `else` branch that builds a stub with `fe->fn = NULL` and `entry_label = fe->name`** — an alias pointing at nothing, which would resolve to null exactly as observed. ⚠️ **Whether `cat` is absent from `_func_buckets` at OPSYN time is NOT confirmed** — my gdb breakpoints did not bind into `libscrip_rt.so` and I stopped rather than guess. **That is the one thing the next session should measure first**, and it is one breakpoint: `register_fn_alias`, print `old_entry`.

## WHAT THIS MEANS FOR THE ROW

⛔ **Do not spend a session on valgrind/ASan.** That was the reasonable next step given the nondeterminism report; the nondeterminism does not reproduce here and valgrind is clean. **The apparent instability seat06 saw across rebuilds is consistent with the *masking* above** — whether a given build statically resolves or emits the by-name dispatch decides pass-vs-fail, and that can flip on unrelated codegen churn (several such commits landed the same day, including a wire-cross fix in `bcps_spine_gen_arm`). **A bug that is deterministic per-binary but flips between builds reads exactly like layout-sensitive UB and is not.**

⭐ **Recommended re-point:** *"an OPSYN alias resolves to null through the by-name dispatch path — single alias, plain function, both modes, m3 crashes"* — with the minimal witness above, graded against the oracle. The "rebind twice" and "compiled mode" qualifiers should come out of the name: they describe the conditions that stop the compiler masking the bug, not the bug.

⭐ **CREDIT WHERE IT IS DUE:** seat06 fixed the real GZ#5 FATAL this session (a parser bug — unary `!` never built `TT_OPSYN`, hardwired to `TT_POW`), cleared 17 of R-8's 19 witnesses at 365/365 with zero regressions, and **declined to claim the row done** on a DONE-WHEN their own change could not meet. Everything above is downstream of their narrowing; the frame being wrong is what a careful handoff is *for*.
