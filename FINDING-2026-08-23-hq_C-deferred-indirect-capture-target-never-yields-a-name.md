# FINDING — a deferred `$()` capture target is lowered to a DEREF, so it can never yield a name; and the obvious cure needs a `RETURN` landing thunks do not have

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Session:** s265 · **Date:** 2026-08-23
**Row:** `deferred-indirect-capture-target` — ⭐ **CURED s265 (SCRIP `P . *(...)` commit). This file's original verdict of NOT CURED is SUPERSEDED, and is kept below rather than deleted because the two reverted attempts are the reason the third one is shaped the way it is.**
**Origin:** `ceo` → `hq_C`, postoffice `bug-deferred-indirect-target`, measured at CEO s264 on Lon's order
**Status at first writing:** ⛔ NOTHING LANDED — two compiler edits built, measured, reverted.
**Status now:** ✅ **CURED.** Both arms byte-identical to `sbl -bf` in m3 **and** m4; the three probes pass; corpus 359/360 both modes, both emit gates rc=0, pristine.

## ⭐ THE CURE (added after the fact — read the diagnosis below first, it is why this shape)

The discrimination **cannot be re-derived at run time**: a name string and an ordinary string are the same bytes. That is precisely why the strict `by_name` gate must stay exactly as strict as it is — it is what correctly fails `. *("dum" "my")`. So the **lowerer carries the fact it already knows**, in the callee name, the same way the varname already carries `*`:

- `sno_expr_collect_nm()` mints an **`EXPRNM$`** thunk for a name-yielding deferred target
- that thunk lowers the **INNER** expression, so it returns the **name string** rather than the deref
- `rt_dcap_pump` treats an `EXPRNM$` callee as by-name and stores through it

⛔ **Chosen over the `"*$"` varname prefix this document proposed, and the reason matters:** three *other* sites in `pattern_match.c` (888, 956, 1008) decode that same `*` for deferred **pattern** evaluation, and a two-character prefix would have broken all three. A distinct thunk **name** leaves `varname + 1` a valid callee everywhere, so **exactly one** site changed instead of six. The design in § THE DESIGN THAT SHOULD WORK was sound in mechanism and wrong in carrier.

⛔ **A REGRESSION WAS CAUGHT IN FLIGHT AND IS WORTH THE INK.** The first dedup guard excluded *every* `want_name` entry from thunk sharing. That broke `140_pat_eval_double_fn_trick` and `141_pat_eval_double_fn_arbno` (corpus −2, caught by the gate, not by review). Only `EXPRNM$` thunks lower differently; `wn` thunks lower identically and were always safe to share. ⭐ **The broad guard is the one that looks more conservative, and it is the one that breaks things.**

⭐ **The `$` arm was cured by the same change, unexpectedly.** I had expected immediate assignment to need a second fix at a second site; it routes through the same pump. Recorded because I predicted otherwise.

## THE DIVERGENCE, REDUCED

CEO's witness was 6 lines with an `IDENT` predicate, a live `OUTPUT` side effect, and two chained captures. **All three are irrelevant.** The witness is three lines:

```
	subject = "HELLO WORLD"
	p = "HELLO" . *$("dummy")
	subject p	:S(ok)F(no)
```

| | `sbl -bf` | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `. *$("dummy")` conditional | `ok dummy=HELLO` | ⛔ `failed` | ⛔ `failed` |
| `$ *$("dummy")` immediate | `ok dummy=HELLO` | ⛔ `ok dummy=` | ⛔ `ok dummy=` |
| `. *note()` NRETURN twin | `ok dummy=HELLO` | ✅ | ✅ |

⭐ **m3 ≡ m4 holds** — this is not a medium split.

⛔ **THE IMMEDIATE ARM IS THE DANGEROUS ONE AND IT WAS NOT IN THE REPORT.** With `$` instead of `.`, SCRIP does not fail — it **succeeds and silently drops the assignment**. A wrong answer with no failure signal is worse than the named failure, and it would not have been found by re-running the reported witness.

**Ablation, all measured against `sbl -bf` — everything below AGREES and is not part of the defect:** `. $("dummy")` immediate-form (works — see why below) · `. *.dummy` (both fail) · `. *nmv` where `nmv = .dummy` (both `dummy=`) · `. *("dum" "my")` (both fail — a string is not a name, correctly) · `. nmv` · `. tgt`. The defect is **exactly** the deferred `$()` form, in both assignment operators.

## MECHANISM — FOUR HOPS, ALL CONFIRMED BY TRACE, NOT INFERRED

1. `lower_snobol4.c:1494` (`TT_CAPT_COND_ASGN`) and `:1518` (`TT_CAPT_IMMED_ASGN`) route a deferred target through `sno_expr_collect_wn` — the collector that marks a thunk **name-wanting** — **only when the target is `TT_FNC` with arguments**. `$("dummy")` is `TT_INDIRECT` (`tree_e` 7, confirmed via `SCRIP_EXPR_DBG`), so it falls to plain `sno_expr_collect` and the thunk is built with `want_name=0`.
2. With `want_name=0` the thunk gets no `SNO$WANTNM` prologue (`lower_snobol4.c:2274`).
3. ⛔ **BUT THAT IS NOT THE ROOT.** `sx_lower`'s `TT_INDIRECT` arm (`lower_snobol4.c:377`) emits `IR_DEREF` **unconditionally**. It is a compile-time decision that consults nothing — so even with `want_name=1` and `rt_g_want_name` set, the thunk still dereferences and returns the *value* of `dummy` (null), never the name.
4. `rt_dcap_pump` (`pattern_match.c:668-680`) sets `rt_g_want_name = 1`, calls the thunk, sees `by_name=0`, and the strict gate refuses:
   `[DCAP] STRICT-REFUSE target=*EXPR$0: returned a VALUE not a NAME (by_name=0, nm.v=0, nm.slen=0) -> rc=1 (match will fail at END)`

⭐ **WHY THE IMMEDIATE (non-deferred) FORM WORKS AND HID THIS.** `sno_capt_name` (`lower_snobol4.c:1272`) constant-folds `$(<literal>)` to the literal name at lower time, so `. $("dummy")` never reaches the thunk path at all. The working case and the broken case share no code. A form working is not evidence its deferred twin works.

## ⛔ WHAT WAS TRIED, MEASURED, AND REVERTED — RECORDED SO IT IS NOT RE-TRIED BLIND

**Attempt 1** — added a behavioural predicate `sno_expr_yields_name()` (`TT_INDIRECT` or `TT_FNC` with args) and used it at both capture sites in place of the inline `TT_FNC`-only test. **Measured: `want_name` went 0 → 1, and the behaviour did not change at all.** That is hop 1 only; hop 3 still derefs. Correct as far as it goes, useless alone.

**Attempt 2** — in `sno_expr_thunks_build`, for a name-wanting `TT_INDIRECT` thunk, lower the **inner** expression (yielding the name string `"dummy"`) and route the thunk's tail through `SNO$NRET`, the same marker `:(NRETURN)` uses — making the thunk behave exactly like the NRETURN twin that already works. This is the *right shape*: `rt_dcap_pump` already has an `IS_STR_fn(nm) → NV_SET_fn(ns, d)` branch that does precisely the correct thing with a returned name string.

⛔ **It does not complete, and the reason is structural:** `bb_emit_end: 1 unresolved forward reference(s): label='RETURN'`. `SNO$NRET` is emitted as a **label landing** registered against `NRETURN` (`lower_snobol4.c:1932/1936`) and depends on the enclosing function's `RETURN` landing. A thunk graph (`IR_DEFINE` with `ival = 3`) has no `RETURN` label, so the marker dangles. **Both edits reverted; the compiler is untouched.**

## THE DESIGN THAT SHOULD WORK, FOR WHOEVER TAKES THE ROW

Give the runtime the compile-time fact it is missing. The lowerer **knows statically** that `$(...)` denotes a name and that a bare concatenation does not — that discrimination must not be re-derived at run time, which is why the strict gate must stay exactly as strict as it is (it is what correctly fails `. *("dum" "my")`).

Encode it in the deferred-target name: emit `"*$" + thunk` for a name-yielding indirect target instead of `"*" + thunk`, lower the **inner** expression into the thunk, and have the consumer treat a returned STRING as a name without demanding `by_name`.

⛔ **Scope, counted, so nobody starts thinking it is one line:** the `*` prefix is decoded in **four** places in `pattern_match.c` (lines 668, 888, 956, 1008) and **two** templates (`bb_match_capture.cpp:50,94`) which emit x86. Every one must learn the two-character prefix, and BOTH-MEDIUM applies to the templates. This is a real change and wants its own session with the full gate set — it is not a tail-end edit.

## WITNESSES — COMMITTED, WITH ORACLE REFS

`corpus/probe/deferred_indirect_target/` — `dit_cond.sno` (the failure), `dit_imm.sno` (the **silent wrong answer**), `dit_nreturn_twin.sno` (the control that PASSES and isolates the defect to the `$()` path). Each `.ref` minted from `sbl -bf`.

## WHAT THIS BLOCKS

The inline arm of the Λ/λ feature (`GOAL-SNOBOL4-100.md`, measured addendum s264) — `ceo` routed it as blocking. The NRETURN-function arm is **not** blocked: `dit_nreturn_twin` passes today, so a lambda lowered through an NRETURN function works now.
