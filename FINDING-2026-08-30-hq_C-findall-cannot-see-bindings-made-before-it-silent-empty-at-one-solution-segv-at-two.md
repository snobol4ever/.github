# FINDING 2026-08-30 hq_C — `findall/3` cannot see bindings made before it: silent `[]` at one solution, SIGSEGV at two

**Tree:** SCRIP `55b69790` · measured 2026-08-30, seat `hq_C`. Handed to this lane by hq_B (SCRIP
`741b6ab5`) as *"findall(X,G,Xs) with G = item(X) SIGSEGVs"*, found behind 24 graders that had been
refusing rc=2 over entries that were gradable all along.

## The claim — the crash is the visible half, and not the dangerous half

hq_B reported the SIGSEGV. Ablation shows the crash is a **consequence of a broader defect that also
produces silent wrong answers at rc=0**:

| program (facts `item(f1..fN)`) | scrip | swipl |
|---|---|---|
| `findall(X, item(X), Xs)` — literal goal | `[f1,f2,f3]` ✅ | `[f1,f2,f3]` |
| `G = item(X), call(G)` — variable goal, OUTSIDE findall | `f1` ✅ | `f1` |
| **1 fact**: `G = item(X), findall(X, G, Xs)` | **`[]` rc=0** ⛔ | `[f1]` |
| **2+ facts**: same program | **rc=139 SIGSEGV** ⛔ | `[f1,f2]` |
| `G = f1, findall(X, item(G), Xs)` — goal is NOT a variable | **`[]` rc=0** ⛔ | one solution |

⭐ **`G = item(X), write(G), nl, findall(X, G, Xs)` prints `item(_G0)` and THEN dies** with
`[PL] call: unbound goal`. The binding demonstrably exists immediately before `findall` and is not
visible inside it. The last row is the one that widens the claim: **the goal there is not a variable at
all** — an ordinary compound `item(G)` whose argument was bound outside — and it still loses the
binding. So this is not a meta-call defect.

**Characterization: bindings established before `findall/3` are not visible inside its goal.** When the
lost binding is the goal itself, `PLCK_META` reads it unbound, prints `[PL] call: unbound goal`, builds
a `PLCK_FAILK`, and the process then SIGSEGVs. When the lost binding is merely an argument, findall
quietly returns the wrong solution set at rc=0.

⛔ **The one-solution case is the more dangerous half and would pass a rc-only gate**: rc=0, no
diagnostic, and `[]` is a *plausible* answer for a findall. It is the plausible-zero class again.

## Where it is NOT

`src/runtime/by_name_dispatch.c:4597` (`PLCK_META`) is where the symptom is *printed*, and hq_B was
right that it is not the site: `plw_cell_deref()` is already called there and the cell is unbound
anyway. Confirmed here and extended — the non-variable-goal row above reaches a wrong answer **without
going through that site at all**, so any cure aimed at `:4597` would fix the message and not the defect.

The lowering is `lower_prolog.c:547`: findall threads its goal with `cx->beta = NULL` and a forced-fail
backedge to enumerate solutions. That backedge, not the meta-call, is the thing to examine — the
suspicion (stated as a hypothesis, **not measured**) is that the forced fail unwinds the trail past
findall's own entry mark and undoes bindings made by the caller.

## ⭐ For the pool — why the crash was the part that got reported

hq_B's grader sweep surfaced this as a SIGSEGV because a SIGSEGV is what a harness notices. The same
defect at one solution returns `[]` at rc=0 and would have sat in a green board indefinitely. **A defect
whose severity scales with input size is discovered at the size where it crashes and lives at the size
where it lies** — so when a crash is found, re-run the witness at the *smallest* input that still
exercises the path, because that is where the silent form is.

## Status

Not cured. Recorded with a full repro rather than filed as a row alone, per TRIO (a row is not a
handoff). The FAILK-then-SIGSEGV path is arguably a second, independent defect: an unbound goal is a
legitimate Prolog error condition (swipl raises `instantiation_error`) and must fail cleanly, never
crash — `main :- call(G).` with G unbound already exits rc=1 correctly, so the crash needs findall's
context.
