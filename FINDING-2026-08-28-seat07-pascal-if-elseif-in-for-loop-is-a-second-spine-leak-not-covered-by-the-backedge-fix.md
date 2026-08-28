# FINDING — the original 64B/iter Pascal spine leak is already cured; a second, bigger leak survives for `for`-loops containing `if/elseif`, and it is NOT a one-line fix

Row: `pascal-m4-for-spine-leak-64b-per-iter` (seat07, FLEET-8/16 per the live `s4e_msg.sh` printout — `ARCH-FLEET-CEO.md`'s CURRENT MODE line said FLEET-16 but the live postoffice MODE read FLEET-8 at claim time; noting the discrepancy, not resolving it here).

## Part 1 — the diagnosed bug is CURED, verified causally

The row's own minimal witness (500-element array, two sequential `for` loops, no
branching) no longer reproduces at SCRIP HEAD `79873cc3` — 30/30 clean under
`setarch -R`, where the row's evidence recorded 30/30 SIGSEGV at `da6c8099`.

This is **not** a fluke of one green run. Bisected causally with the env killswitches
`748f7698` (`emit.cpp: fix nested-while-in-function SIGSEGV in zd_plan's ζ-depth
planner`, landed same evening for an unrelated SNOBOL4/Snocone/Rebus nested-while bug)
already carries:

| Config | witness500 × 10 under `setarch -R` |
|---|---|
| default (both fixes on) | 10/10 PASS |
| `SCRIP_ZD_BACKEDGE=0` | 10/10 **FAIL** (matches the row's original signature exactly) |
| `SCRIP_ZD_OMEGA_HEAD=0` | 10/10 PASS (this sub-fix is not the one that matters here) |
| both `=0` | 10/10 FAIL |

So: `748f7698`'s back-edge depth correction (`zd_plan`'s `gback`/`oback` mechanism)
cured this row's exact diagnosed shape as a side effect, before this row's assigned
seat ever touched code. `748f7698`'s own commit message and control-arm run never
mention Pascal — nobody knew.

## Part 2 — DONE-WHEN is still not met. A second, distinct, bigger leak remains

Running the row's own DONE-WHEN grid (all 9 named kernels, `echo 1 |`, `setarch -R`,
pristine `79873cc3`):

| kernel | result |
|---|---|
| bubble | **FAIL rc=139** |
| intmm | **FAIL rc=139** |
| queens | **FAIL rc=139** |
| quick | **FAIL rc=139** |
| perm | **FAIL rc=139** |
| sieve | PASS |
| towers | PASS |
| uplevel2 | PASS |
| uplevel3 | PASS |

Note the failing set is **not** the row's originally-named set (`bubble, intmm, queens,
quick, sieve`) — `sieve` now passes, `perm` now fails. Same count (5), different
membership. `perm`'s failure is plausibly unrelated (PROVENANCE.md already tracks
`perm.pas` under a separate, independent defect, "PAS-FOR-RECURSE" — not re-diagnosed
here, do not conflate per this row's own LINKS field).

### Minimal reproduction (ablated from `bubble.pas` itself, not built up from guesses)

```pascal
program p;
var sortlist: array[1..500] of integer;
    seed, biggest, littlest, i, temp: integer;
begin
  seed := 74755; biggest := 0; littlest := 0;
  for i := 1 to 500 do begin
    seed := (seed * 1309 + 13849) mod 65536;
    temp := seed;
    sortlist[i] := temp - (temp div 100000) * 100000 - 50000;
    if sortlist[i] > biggest then biggest := sortlist[i]
    else if sortlist[i] < littlest then littlest := sortlist[i]
  end;
  writeln(biggest); writeln(littlest)
end.
```
This is bubble's own fill loop, with the nested while-sort **removed entirely** —
still 10/10 SIGSEGV under `setarch -R`. Ablated further (see below), the trigger
reduces to: **a `for` loop whose body contains `if/then/elseif`**, using **`mod` or
`*`** anywhere in the loop body (plain `+`/`-`/`div` alone do not trigger it — this
looks like it's really about which operand/box shape the arithmetic produces feeding
the merge, not the opcode itself; not fully chased down, see Part 4).

**Confirmed a real per-iteration leak, not a size artifact** — array size pinned at
500, only the loop trip count varied:
```
loopN=8  → 10/10 PASS
loopN=9  → 10/10 FAIL
```
gdb, breaking at the loop-head box (`n11_var_α` in this witness) across iterations,
clean build:
```
rsp=0x7fffffffe080
rsp=0x7fffffffe220   (+0x1A0 = +416)
rsp=0x7fffffffe3c0   (+0x1A0)
rsp=0x7fffffffe560   (+0x1A0)
...
```
Constant **+416 bytes/iteration, upward** (RSP climbing toward/past the caller's
frame — same direction and same class as the row's own `RSP above RBP` signature,
just a bigger per-iteration multiple: 416B vs. the original 64B).

## Part 3 — root cause, precisely (not "probably")

`zd_plan()` (`src/emitter/emit.cpp:2479`) plans ζ-depth by building linear "runs":
starting at a head (index 0, or any node satisfying `bb_src_of()`), it walks
**only the γ edge** (`cur = zd_chase(cur->γ.node)`, line 2505) until it hits an
already-claimed node or a fresh statement boundary. **It never walks a node's ω edge.**

An `if/then/elseif` compiles (via `pas_cond`, called from `lower_if`/`lower_for`) to
chained `IR_BINOP_TEST` nodes whose **ω edge** is the "condition false, skip this arm"
path. The shared continuation after the whole if/elseif (here: the `for`-loop's own
increment sequence) is reachable **only via those ω edges** from some of its
predecessors (the "then" branch reaches it via a normal γ fall-through **and never
releases anything**; the "elseif false" exit reaches it via an ω edge **that does**
release, then the elseif's own arms fall through to the same place). Since the
γ-only run-walker never traverses an ω edge, this merge node is never included in
the run that contains its predecessors, and it is a *mid-statement* node, not a new
Pascal statement — so it also never independently qualifies as a `bb_src_of` head.

`748f7698` already anticipated "a node reachable only via a test's ω edge, needed as
a head" — that is exactly what its pass-2 `zd_omega_head()` (line 2477) is for:
```c
static int zd_omega_head(IR_t **nodes, int n, IR_t *t) {
    for (int k = 0; k < n; k++)
        if (nodes[k]->op == IR_CMP_TEST && zd_chase(nodes[k]->ω.node) == t) return 1;
    return 0;
}
```
**But it only recognizes `IR_CMP_TEST`.** Grepped across every lowerer:
- `IR_CMP_TEST` is built **only** in `src/lower/lower_snobol4.c:189`.
- `IR_BINOP_TEST` — what Pascal's `if`/`while`/`for` tests **and** Raku's `if` all
  build (`src/lower/lower_pascal.c:140,149,383`, `src/lower/lower_raku.c:126`) — is
  never checked.

So pass-2 is structurally SNOBOL4-only today; it cannot see this shape for Pascal
(or, unverified but plausible, for Raku's plain `if`) at all. Separately: grepped
every call site of `bb_src_note()` (the mechanism that lets a lowerer explicitly mark
a node as a legitimate re-plan head — SNOBOL4 calls it for **every statement**;
Raku calls it for loop condition/body/increment re-entry points) — **`lower_pascal.c`
calls it zero times, anywhere.** Pascal has no lowering-level fallback for this class
either.

## Part 4 — two fixes tried this session, both reverted; neither is safe to ship

Both attempts, findings, and reasons for reverting:

**(a) `emit.cpp:2477`, add `|| nodes[k]->op == IR_BINOP_TEST` to `zd_omega_head`.**
Grep-verified inert for SNOBOL4/Icon/Prolog/Snocone/Rebus (none ever construct an
`IR_BINOP_TEST` node, so the added disjunct can never fire for them — zero
cross-language risk from the opcode match itself). Confirmed via `SCRIP_ZD_DIAG=1`
that it does cause the previously-unplanned merge node to get freshly armed as its
own independent run (new `h=` entries appear that weren't there before). **But** that
new run resets to `zd=0` (`zd_plan`'s per-run baseline, `emit.cpp:2541`), and the
existing `gback`/`oback` cross-run correction from `748f7698` computes a jump-site's
release amount as `_wzdepth - _gbpre` assuming a single consistent baseline; against
a zero-reset run discovered this way it produced **negative** pop values (observed
`gpop=-288 wpop=-288`). Net effect on every repro above: **unchanged** — same rc=139,
same cliff, i.e. this edit is currently a no-op in outcome despite changing the
internal plan, and the negative-pop condition is a symptom of a real inconsistency I
did not chase further. Reverted; `git diff --stat` confirms clean.

**(b) `lower_pascal.c`'s `lower_if`, add `bb_src_note(γ, "pas_if_join", 0)`** —
mirroring SNOBOL4's own per-statement registration and Raku's loop-reentry
registration (both pre-existing, load-bearing uses of the same mechanism). This
**did** fix the `cliff2_15`-shape repro (array fixed 500, loop count 15, MUL) — but
did **not** fix `bub_d`/`bub_b` (the fuller bubble-shaped repros with `mod`+`div`
chains) or a same-family `cliff_15` variant, AND it introduced a **new regression**:
a previously-clean nested-`while`-loop bubble-sort witness with a plain `if`-swap
inside (`w_bsort.pas`, 15/15 PASS before) went to **15/15 FAIL** after this change.
A fix that trades one crash for another is not a fix. Reverted; `git diff --stat`
confirms clean.

**Working tree at handoff is byte-identical to origin `79873cc3`** — no partial or
speculative state was left in `src/`. (A local, unpushed `git stash` from an earlier
intermediate step also sits in this checkout; its contents are superseded by (a)
above and are not needed to reproduce anything in this FINDING — leaving it rather
than force-dropping it, since dropping a stash is a destructive git op this seat's
standing instructions ask to avoid without cause.)

## Part 5 — what actually needs to happen next (a hypothesis, not a plan someone is bound to)

Both (a) and (b) individually move a different piece of the puzzle without landing
it. The shape suggests the real fix needs **both** halves reconciled together, not
either alone:
1. Pascal's conditional/loop joins (`lower_if`'s `γ`, and plausibly `lower_while`'s
   `W`/`lower_for`'s `iv`) need to become registered heads — extending (b), but
   likely needs the SAME registration wherever multiple predecessors with different
   accumulated depths can reach one node, not just the one call site tried here.
2. AND/OR: a pass-2-discovered run (`zd_omega_head`) must not blindly reset to
   `zd=0` — it needs to seed its baseline from whichever predecessor edge is
   *discovering* it, so that `gback`/`oback` reconciliation has a single consistent
   coordinate system instead of two independently-zeroed ones meeting at a shared
   node. This is a real extension to `zd_plan`'s model (not currently designed to
   unify depth across a diamond's arms — it only unifies *operand availability*
   across arms via the existing `cm[]`/`nblob` blob mechanism, never *depth*).

This is shared, heavily-guarded emitter code (`zd_plan` backs every frontend's
codegen). Given two independent, plausible-looking single-file edits each produced
an incomplete-and/or-regressing result on direct empirical testing, I judged it
unsafe to keep iterating by trial and error without a much wider control-arm re-run
per attempt (SNOBOL4 blocking set + Icon watermark, per SHARED-NODE VERDICT SCOPE) —
recommend this row's next attempt route through hq_C given it is now an
emitter-shared-mechanism question, not a Pascal-lane-local one.

## Repro artifacts (not committed — ephemeral scratch, recreate from source above)
All witnesses in this FINDING are self-contained single files; none need corpus. The
full ablation ladder (bub_a through bub_g4, cliff/cliff2 at N=1..500) lived in this
seat's scratchpad and was not persisted — the two shown above (Part 2's bubble-derived
witness, Part 2's array-fixed/loop-varied pair) are sufficient to reproduce and
re-bisect from scratch in well under the time this session spent finding them.
