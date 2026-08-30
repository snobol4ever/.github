# FINDING — a real defect precisely characterized, NOT fixed: when a mixed int/real relational
# comparison succeeds, Icon promotes the returned operand to match the wider type (`6.2 ~= 4` returns
# `4.0`, not `4`) — SCRIP always returns the operand's raw, original descriptor, unpromoted, in every
# call site checked. This is the SAME symptom already named (uninvestigated) in the `ck.icn` FINDING
# earlier today; `arith.icn` is a second, independent witness. Root mechanism now confirmed precisely,
# but a real fix touches at least two call sites and needs a genuine coercion helper, not a one-line
# reorder — a different shape of change than this row's last three cures. Also: a separate, unexplained
# oddity found and flagged, not chased.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`** (Class C).

## 1. The symptom, confirmed against the oracle before tracing anything

```
write(6.2 ~= 4)   -- oracle: 4.0   -- SCRIP (via a variable, see §3): 4
write(6.2 >= 4)   -- oracle: 4.0   -- same
write(4 ~= 6.2)   -- oracle: 6.2  (b already real, no promotion needed -- consistent, not a new case)
```
`rung36_jcon_arith.icn`'s own `numtest(6.2, 4)` row shows exactly this: `a ~= b`, `a >= b`, `a > b`
each print `4` where `.expected` has `4.0`. This is the SAME class of bug already named — but not
investigated — in `FINDING-2026-08-30-seat01-icon-cset-real-formatting-cured-and-ck-icn-further-
characterized.md`'s `ck.icn` section ("a mixed int/real comparison result loses its real-ness"). Two
independent witnesses now.

## 2. Root mechanism, traced via the emitted `.s`, not guessed

Compiled `numtest(6.2, 4); write(a ~= b | "---")` and read the assembly directly. The comparison
itself is correct — `call rt_jct_relop@PLT`, `test eax,eax` branches on success/failure exactly right.
**But the VALUE stored as the expression's result, on success, is a straight copy of operand `b`'s
descriptor from its pre-call stack slots** (`mov rax,[rsp+32]; mov [dest],rax; mov rax,[rsp+40]; mov
[dest+8],rax`) — the two registers `b` was loaded into *before* the call, untouched by whatever
`rt_jct_relop` computed. `rt_jct_relop`/`c_rt_jct_relop`/`rt_jct_relop_impl`
(`src/runtime/by_name_dispatch.c:4863+`) all return a plain `int` — no value, no promotion
information, nothing for the caller to use even if it wanted to.

**Confirmed this is not a one-off in the codegen path**: `by_name_dispatch.c:4780`, a *different*,
generic by-name relop dispatch (`rt_jct_relop(a,b,oc) ? (string-relop special case ? rt_str_coerce(b) :
b) : FAILDESCR`), has the **identical** shape — string relops already get a coercion
(`rt_str_coerce`), numeric relops fall through to bare `b`, unpromoted. The string case is the proof
this project already recognizes "the returned operand needs coercing to match what the comparison
actually did" as a real requirement — it just was never extended to numbers.

**Not a quick fix, unlike this row's last three cures**: those were each a single wrong/missing
condition in one function. This needs an actual "promote to match" numeric coercion (real if either
operand is real, matching the oracle's own `4 ~= 6.2 → 6.2` / `6.2 ~= 4 → 4.0` behavior), applied at
**every** site that currently does the bare-copy — at least the two named here, possibly more not yet
searched for. Landing it safely means finding all of them, which this pass did not do.

## 3. A separate, unexplained oddity — found, not chased

A real number as a **direct literal** in a relop fails outright where the **same value through a
variable** succeeds:
```
write(6.2 ~= 4)              -- SCRIP: nothing printed (rc=0, no error)
numtest(6.2,4): write(a~=b)  -- SCRIP: 4   (via parameters -- succeeds, wrong VALUE per above)
```
Even `write(6.2 ~= 4.0)` (real vs real, both literal) fails silently. This reproduces with a bare
`write(EXPR)`, no `| fallback`, so a real failure (not merely "wrong value") is the visible symptom.
**Not investigated past confirming it's real and reproducible** — could be a constant-folding pass
treating this differently than the runtime path, could be something else. A distinct lead from §2,
named separately so it isn't conflated with the promotion bug.

## 4. Not attempted

No code touched. This row's own established discipline (Site-1 Pascal investigation, `&level`'s entry
side) is to characterize precisely and hand off rather than force a fix whose full call-site footprint
isn't yet mapped — same call here. Concrete next steps, in order: (1) grep for every other site doing
the "return b's pre-call descriptor unchanged" pattern near a `rt_jct_relop`/`rt_relop_overload` call,
not just the two found here; (2) design the promotion helper (real if either operand is real — the
oracle's own rule, already confirmed); (3) separately, isolate the literal-vs-variable discrepancy with
a smaller repro before assuming it's related.

## 5. State

SCRIP tree clean (`git status --short` empty throughout). Mailing hq_P.
