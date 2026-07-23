# FINDING 2026-07-23 CLAUDE — PL `\=`/2 STRANDED-SENTINEL FIXED (rung81) + NESTED-`->` BINDING-LEAK BANKED

## Summary

`\=`/2 (ISO/IEC 13211-1 §8.2.2, "not unifiable") was **completely broken in both mode-3 and
mode-4** — every use (even a bare `a \= b` goal) aborted with
`FATAL emit_drive: IR op=122 has no template in the universal driver`. It had **zero corpus
coverage** (28 `\=` mentions live only in benchmarks / other trees, none in
`programs/prolog/*.pl`), so the 161/161 rung suite was green while a core ISO predicate never
worked. FIXED by routing `\=` through the existing, working `lower_ite`, exactly as `\+`/`once`/
`ignore` already do — mirroring gprolog's own definition. New rung81 locks it in; suite 161→162 ×3.

## Root cause — an `IR_OP_COUNT` sentinel that was never materialized

`op=122` is not a real opcode: `IR_OP_COUNT == 122` is the enum terminator. The old `\=` arm in
`lower_prolog.c` (goal role, ~line 356) hand-rolled a soft-cut ITE out of **`IR_OP_COUNT`
placeholder nodes** carrying a `bb_ite_state_t *zi` in their `ival`:
```c
IR_t * commit = build(cx, IR_OP_COUNT, tf, ωfail); IR_LIT(commit).ival = (intptr_t) zi;
IR_t * gate   = build(cx, IR_OP_COUNT, es, ωfail); ...
IR_t * u      = build(cx, IR_OP_COUNT, commit, gate); ir_operand_push(u, term(...)); ...
```
These sentinels were evidently meant to be rewritten into real ITE machinery by a later
`zi`-keyed pass that either never existed or was removed. Nothing rewrote them, so the raw
`IR_OP_COUNT` nodes reached `emit_drive`, which correctly refuses to emit an unknown op. This was
a *never-worked* path, not a regression — the sibling ITE builtins were all migrated to
`lower_ite` and `\=` was left behind.

## Fix — delegate to `lower_ite`, matching gprolog's own source

gprolog `src/BipsPl/unify.pl:56-57` defines it verbatim:
```prolog
X \= Y :- \+ X = Y.
```
`\+` already lowers correctly via `lower_ite(cx, Cond, fail, true, ...)`. So `\=` is exactly
`( =(X,Y) -> fail ; true )`. The entire arm collapses to:
```c
if (!strcmp(nm, "\\=") && t->n == 2) {
    return lower_ite(cx, pl_synth_fnc2("=", t->c[0], t->c[1]),
                     pl_synth_qlit("fail"), pl_synth_qlit("true"), γnext, ωfail, entry_out);
}
```
13 lines deleted, 1 added. No new globals, no template change, no runtime change — pure LOWER
reuse ("write each piece of logic once"). `lower_prolog.c` compiles into both `scrip` and the
`.so`; both rebuilt.

## Verification — m2==m3==m4, byte-identical to gprolog 1.4.5

rung81 (`programs/prolog/rung81_neq_unify.pl`) covers: differing atoms, equal atoms (→else),
`f(X)\=f(a)` (unifiable→else), integers, `X=a` then `X\=b`, **binding purity via disjunction**
(`(X\=a ; true)` leaves `X` unbound), and a 2-arg compound. All 7 lines identical across scrip
m2/m3/m4 and gprolog. Binding purity confirmed against `\+`: both `\+ (X=a)` and `X \= a` under
`( ... ; true )` leave `X` unbound (the discard-bindings semantics is correct). Rung suite
**162/162 ×3**; smoke 5/5 ×3; no-value-stack PASS; no-new-global unchanged (only the pre-existing
`g_pl_disj_ctr` FAIL, floor 14 — NOT touched by this diff, `git diff | grep g_pl_disj_ctr` = 0).

## BANKED (its own rung / MONITOR hunt) — nested-`->` discards the inner condition's trail

Discovered while validating: **the bug is NOT `\=`-specific and NOT introduced here.** When a
`\+`/`\=` (whose body is itself an `->`) is used as the *condition* of an **outer** `->`, the
inner condition's bindings leak past the outer soft-cut:

| form | scrip | gprolog |
|---|---|---|
| `( (X \= a) ; true ), check(X)` | `unbound` ✓ | `unbound` |
| `( (X \= a) -> true ; true ), check(X)` | **`bound(a)`** ✗ | `unbound` |
| `( (\+ X = a) -> true ; true ), check(X)` | **`bound(a)`** ✗ | `unbound` |

The last two rows prove it is a **general nested-ITE / soft-cut trail-unwind defect** in
`lower_ite` (an inner `->` used as an outer `->`'s condition does not get its bindings unwound
when the outer commit fires). Affects `\+` identically, so `\=` merely inherits it. Per RULES.md
MONITOR-FIRST this should be bracketed with the 2-way sync-step monitor, not hand-chased — its own
rung. rung81 deliberately exercises only the correct disjunction form so it is a faithful,
non-flaky lock on the `\=` fix while this deeper defect stays banked.

## Files

- SCRIP `src/lower/lower_prolog.c` — `\=` arm → `lower_ite` (13−/1+).
- corpus `programs/prolog/rung81_neq_unify.pl` + `.expected` (baked from gprolog 1.4.5, m2==m3==m4).

---

## UPDATE — same session: `writeln`/1,/2 was the SAME stranded-sentinel class (rung82)

`writeln/1` and `writeln/2` crashed identically (`op=122`). Same root cause, second site: the
`is_builtin_exec(nm)` fallthrough arm (`lower_prolog.c` ~line 599) builds an `IR_OP_COUNT`
placeholder for **any** whitelisted builtin that has no earlier specific lowering arm. `write/1`
works because it has an explicit arm (`$write`); `writeln` was whitelisted (`g_pl_nl_builtins[]`)
and had a runtime handler (`by_name_dispatch.c:4175`, op `'W'`) but **no lowering arm**, so it hit
the sentinel.

**Fix (same reuse pattern):** `writeln(X)` ≡ `write(X), nl` and `writeln(S,X)` ≡ `write(S,X), nl(S)`.
Synthesize the `,`-conjunction and route through `goal()` — the exact idiom `forall`,
`setup_call_cleanup`, and `with_output_to` already use. Reuses the working `$write`/`$write2`/
`$nl0`/`$nl1` arms. No new globals, no runtime change, no template change.

**Oracle = swipl 9.0.4 (NOT gprolog).** gprolog 1.4.5 has no `writeln` (existence_error). swipl
confirms `writeln == write + nl`, UNQUOTED (`writeln('quoted atom')` → `quoted atom`, no quotes).
rung82 output byte-identical to swipl across atoms, lists, compounds, quoted atoms, operator terms,
`writeln` in a disjunction, and the `writeln/2` stream form (via `user_output`). Ground terms only
so `.expected` is engine-stable (var rendering `$` vs `_G` is a pre-existing `write/1` property,
kept out of the rung). Rung suite 162→163 ×3.

## The stranding arm is architecturally wrong (banked)

`op=122 == IR_OP_COUNT` reaching `emit_drive` is always a LOWER bug — a placeholder that no pass
rewrote. A sweep of the 72-entry builtin whitelist × arities 1–2 found the crash fires for every
whitelisted name/arity lacking a specific arm. **Most are wrong-arity noise that SHOULD fail, not
crash** (`arg/1`, `functor/1`, `sort/1`, `msort/1`, `atom_chars/1` …; the real preds are `arg/3`,
`functor/3`, etc.). The one genuine valid-arity crasher found: **`retractall/1`** (swipl accepts it,
scrip crashes; no `$retractall` runtime handler exists — needs a new handler + det-target entry,
its own rung). Deeper fix worth its own rung: make the fallthrough arm emit a clean
unknown/wrong-arity predicate error (fail or `existence_error`) instead of `IR_OP_COUNT`, so a
missing arm degrades gracefully instead of aborting the whole program.
