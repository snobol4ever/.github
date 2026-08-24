# FINDING 2026-08-23 (seat03) — row `vlist-expr-alternation`: IR_DISJUNCTION lowering landed per hq_P's §5 ruling, Defect B confirmed eliminated by construction, Defect A's zd_plan extension attempted and reverted — precise, evidenced root cause of the remaining gap, NOT YET FIXED

## HEADLINE

Implemented hq_P's §5 ruling (task QA, 2026-08-23) exactly: `TT_VLIST` now lowers onto an `IR_DISJUNCTION` host
mirroring `lower_icon.c`'s `lower_alt`, replacing the old temp-var/omega-chain approach entirely. **This is
landed, committed, gated behind `SCRIP_VLIST_ALT` (still default OFF), and verified to cause zero regression**
(SNOBOL4 crosscheck 325/325 both modes, zero divergence; Icon quick suite 4/4; Prolog crosscheck's fluctuating
numbers are pre-existing flakiness in that suite, confirmed by re-running the unmodified baseline and my own
tree back-to-back and observing the SAME run-to-run variance on identical binaries). **Defect B (arm-length
convergence) is eliminated by construction**, exactly as the ruling predicted — every arm now reaches the SAME
physical σ-landing regardless of internal node cost, so there is no depth-reconciliation problem left to have.
**Defect A is NOT closed.** I extended `zd_plan`'s ZD5B block to admit `IR_DISJUNCTION` arms, found and fixed
two real bugs in the process (documented below with full diffs, since I reverted both), and got as far as
correct, real `sub rsp`/`add rsp` release around every arm member — but discovered a THIRD, deeper problem:
`disj_sigma_copy` (the runtime template that copies the winning arm's value into `dj`'s own cell) reads each
arm's result through a **flat, permanent slot number** (`emit_binop_opnd_slot`/`zls_off`), while a
zd-plan-armed arm's result is written to a **transient, real-stack-relative cell that gets `add rsp`'d away
before `disj_sigma_copy` ever runs**. These two addressing conventions are incompatible as currently wired, and
I did not find a fix I trusted enough to ship — see "THE REMAINING GAP" below for the precise mechanism and two
candidate fix directions, neither implemented.

## WHAT'S LANDED (committed)

**`src/lower/lower_snobol4.c`**, `TT_VLIST` case (was line 713): the temp-var/`IR_ASSIGN`-chain lowering is
replaced with the exact mechanical shape hq_P specified — `dj = lc_build(g, IR_DISJUNCTION, γ, ω)`; per arm `j`
(left-to-right, matching `lower_alt`'s own order — NOT the old code's right-to-left, which existed only because
the old chain needed each arm's "next" pre-built before lowering the preceding one, a dependency the
disjunction host doesn't have): `sx_lower(t->c[j], dj, dj, &ar)` (both continuations are `dj` itself — SNOBOL4
has no generator concept, so unlike `lower_alt`'s `ab`/`ab_in_arm` tracking, every arm's "resume" is
unconditionally `dj`, matching the ruling's `ir_operand_push(dj, dj)` note and confirmed correct against
`ir_node_produces_value`/`flat_drive_match_alt`'s own `r == nd → na_f[i]` special case for `IR_DISJUNCTION`,
which exists for exactly this shape); then the same port-relabelling pass as `lower_alt` (`ω.node==dj → "φ"`,
`γ.node==dj → "σ"`, with the `IR_GOTO`-both-ports-to-`dj` override) over every node built during that arm;
`ir_operand_push(dj, ej)` / `ir_operand_push(dj, dj)`; after all arms, `ir_operand_push(dj,
sno_arm_result(resv[j]))` for each (new small helper mirroring `icn_arm_result` exactly — filters
`IR_GOTO`/`IR_SUCCEED`/`IR_FAIL`/`IR_RETURN`/`IR_SUSPEND`/`IR_CORET`/`IR_COFAIL` to `NULL`, all shared
language-free IR ops, verified this compiles clean even though SNOBOL4 arms are unlikely to ever hit most of
them); `IR_LIT(dj).ival = n`; `*res = dj; return dj`. Confirmed `lc_build`/`lc_γ_to`/`lc_ω_to` are true
single-step/two-step equivalents (`lower_common.c:185`: `lc_build` is literally `alloc + lc_γ_to + lc_ω_to`), so
using the one-call form here (unlike `lower_alt`'s two-call form) is not a simplification of substance, only of
style. `IR_DISJUNCTION` was already in `scrip_ir.c`'s value-producer list (`ir_node_produces_value`, confirmed
at the line the ruling cited) so `ir_drive_slot_assign` grants it a zls slot with zero changes needed there —
confirmed via `--dump-zeta` on a synthetic 2-arm case: the graph shows `IR_DISJUNCTION`'s own 32-byte footprint
(16B value DESCR + 8B `alt_i` index + 8B pad — see "THE 24-vs-32 QUESTION" below) laid out correctly beside each
arm's own slots, with no manual wiring required.

**`src/emitter/emit.cpp`**: deleted the `SCRIP_ZD_VLIST_OMEGA` prototype block (was after the `IR_MATCH_ALTERNATE`
ZD5B block, `emit.cpp:2471-2489` pre-session) per the ruling's explicit instruction ("becomes dead — delete it
in the same series rather than leave a third mechanism"). It scanned any claimed node's `.ω` target for an
unclaimed, non-statement-head node and walked its γ-chain in — a generic omega-discovery heuristic that only
VLIST's OLD raw-omega-wired lowering could ever trigger (gated behind its own never-set-by-default env var, so
deleting it is a pure removal of unreachable code, zero behavior change, confirmed via the full SNOBOL4
crosscheck run clean before and after).

**Verification of what's landed:** default (`SCRIP_VLIST_ALT` unset) output is byte-identical to the
pre-session baseline on this row's own DONE-WHEN witness (confirmed via `diff -q`). All four `corpus/probe/vlist/*.sno`
witnesses plus the DONE-WHEN witness run to completion under `SCRIP_VLIST_ALT=1`, mode 3, with **zero
crashes** (rc=0 on all five) — a structural improvement over the OLD lowering, which SIGSEGV'd
`vl_alt_nested_cat.sno` reliably under mode 4 per the prior FINDING. Mode 4 (`--compile`+gcc+run) still SIGSEGVs
on three of the five (all multi-node-arm cases; `vl_alt_second.sno`, whose arms are single leaf nodes, survives
mode 4 too, rc=0) — see below, same root cause as the wrong values, manifesting as a crash instead of silent
wrongness depending on process layout, the same environment-sensitivity shape EVIDENCE 2b already documented
for the OLD mechanism.

## WHAT'S NOT LANDED — THE ZD5B EXTENSION ATTEMPT (fully diffed here, not committed)

Extended the block at `emit.cpp` (was lines 2455-2470, the `IR_MATCH_ALTERNATE`-only ZD5B arm-discovery) to also
recognize `IR_DISJUNCTION` hosts:

```c
// host-recognition + admission, replacing the IR_MATCH_ALTERNATE-only version:
for (int r0 = 0; r0 < rl_main; r0++) { IR_t * env = nodes[run[r0]]; int is_dj = (int)env->op == IR_DISJUNCTION; if ((int)env->op != IR_MATCH_ALTERNATE && !is_dj) continue; int ei = run[r0];
    int pairs2 = is_dj ? 2 * (int)IR_LIT(env).ival : env->n_operands;   // DISJUNCTION's operands[] holds 3N entries (entry,resume pairs then N results) — must bound to 2N, not n_operands, or the walk misreads result nodes as arm entries
    for (int a = 0; a + 1 < pairs2; a += 2) { IR_t * c2 = env->operands[a]; int rl0 = rl; int bad = 0; int g2 = 0; int first = 1;
        while (c2 && g2++ <= n) {
            int ci = -1; for (int k = 0; k < n; k++) if (nodes[k] == c2) { ci = k; break; }
            if (ci < 0 || claim[ci] >= 0) break;
            if (bb_src_of(nodes[ci]) || emit_floater_kind(nodes[ci])) { bad = 1; break; }
            { int aop = (int)nodes[ci]->op; int leaf = is_dj || (aop == IR_MATCH_LIT || /* ...unchanged ALTERNATE leaf whitelist... */ aop == IR_MATCH_BAL);
              if (!leaf) { bad = 1; break; }                                    // dj arms admit ANY op (per ruling: "drop the leaf-only test for dj hosts")
              if (is_dj || nodes[ci]->n_operands > 0) { run[rl] = ci; rpos[ci] = rl; claim[ci] = hi; zarm[ci] = ei; if (first) { aent[ci] = 1; first = 0; } rl++; } }   // dj arms claim even 0-operand leaves (bare literals/vars are common VLIST arm content — the n_operands>0 gate exists for ALTERNATE's own reasons and would silently skip e.g. a bare `7` arm)
            c2 = zd_chase(c2->γ.node);
        }
        if (bad) { /* unchanged rollback */ }
    } }
```

Rebuilding with just this: mode-3 output was structurally sound (no crash) but every VLIST value came out
**empty or garbage bytes** — worse in one place than before the extension (an extra crash appeared on the
row's own DONE-WHEN witness). Debugging this surfaced two real, independent bugs in the existing (`IR_MATCH_ALTERNATE`-only,
years-old) consumption logic, neither previously exercised because ALTERNATE's arms — confirmed by reading
`flat_drive_match_alt`'s own pair-building — never wire an arm's own `.γ`/`.ω` literally back to the host node
the way `lower_alt`/my lowering does (ALTERNATE's "resume" operand is always a real successor node or falls
through to `node_ω`; the `r == nd → na_f[i]` special case exists ONLY for `IR_DISJUNCTION`). Both are proven
**inert for `IR_MATCH_ALTERNATE`** by construction (the conditions only match a shape ALTERNATE never produces),
verified by the clean 325/325 SNOBOL4 crosscheck and 4/4 Icon quick suite with both fixes in place before I
reverted them for the third (unsolved) issue below:

**Bug 1 — `zgpop`/`zwpop` computed relative to the wrong depth for arm members.**
`zd_plan`'s consumption loop (`emit.cpp` ~2525) computed `int _wzdepth = (int)zd;` unconditionally — but `zd`
is the OUTER run's linear accumulator, which arm-member processing never touches (only `arm_zd` does). Fix:
```c
int _wzdepth = (zarm && zarm[i] >= 0) ? zout[i] : (int)zd;
```
Verified via `SCRIP_ZD_DEPTH=1` (the existing depth-census diagnostic, `emit.cpp:2542`, previously never
triggered a WALL on `IR_MATCH_ALTERNATE`-only code in the corpus) — before this fix, dj showed a WALL (8 preds
disagreeing on entry depth, values 0/0/0/0/16/32/48/48); after, zero disagreement.

**Bug 2 — `gin`/`oin`'s `nblob>0` shortcut treats "reachable via my host's operands[]" as "already satisfied, no
release needed."** `zd_plan`'s `gin`/`oin` computation (`emit.cpp` ~2519) has two modes: a position-ordered
`run[]` scan (used when `nblob==0`) and, whenever ANY node is reachable purely via `operands[]` pointers beyond
what the plain γ-walk already claimed (`nblob>0` — true for basically any `IR_DISJUNCTION`, since its own
operands[] necessarily reference its arm entries/results), a blob-membership scan with **no ordering
requirement at all**. An arm member's `.γ`/`.ω` edge landing on `dj` — which IS in the blob, dj being the run's
own seed — reads as "already in," suppressing the real-release assignment entirely. Confirmed via direct asm
read: `n9_lit_integer_α` (a single-node arm) jumped straight to the shared landing with no `add rsp` at all
before the fix. Fix (targeted, only fires for the specific shape ALTERNATE never creates):
```c
{ if (zarm && zarm[i] >= 0) { if (gt == nodes[zarm[i]]) gin = 0; if (ot == nodes[zarm[i]]) oin = 0; } }
```
placed after the existing gin/oin computation. With both fixes: the depth-census WALL at `dj` fully resolves,
and the asm gains a correct `add rsp, 16` before every arm-member's jump back to the shared landing — real,
verified stack-discipline compliance with `ARCH-ZETA-LOCAL-STORAGE.md`'s "STACK flavor" law for the arm bodies.

**Bug 3 (unsolved, why I reverted) — the shared landing reads results from a cell that no longer exists by the
time it runs.** With bugs 1+2 fixed, `n9_lit_integer_α` now correctly does `sub rsp,16 → mov [rsp+0],result →
add rsp,16 → jmp n6_disjunction_as`. But `disj_sigma_copy` (the shared landing, `bb_disjunction.cpp:12`) reads
each arm's result via `op_parts_ival[j]`, computed in `flat_drive_match_alt` (`emit.cpp:1361`) as
`emit_binop_opnd_slot(rj)` → `nd_slot(rj)` → `zls_off(rj)` — the node's **flat, permanent** slot number (e.g.
176 for this arm), a completely different addressing scheme than the **transient, real-rsp-relative** `[rsp+0]`
the arm actually wrote to. `add rsp,16` doesn't erase the 16 bytes at the old location — the data is still
physically there — but reading it back needs an offset computed **relative to the post-release rsp**, and
`176` bears no such relationship to it (176 is a global running total across the whole graph, not a local
delta). The result: `disj_sigma_copy` reads whatever happens to be sitting at `[rsp+176]` at that point —
garbage or zero, matching every symptom observed (empty/garbage values, occasional SIGSEGV on the larger
multi-arm witnesses under mode 4 specifically, matching EVIDENCE 2b's earlier-documented environment-sensitive
wild-read/write signature exactly).

## THE REMAINING GAP — precise, not yet fixed

**The core incompatibility:** `disj_sigma_copy`'s design assumes an arm's result cell is stable and
flat-addressable for as long as `dj` might need it (i.e., the arm was never zd-armed/real-pushed at all — the
pre-my-session, always-refused-by-`zd_wl_kind` state for a populated `IR_DISJUNCTION`). Making arm members real
zd-armed (bugs 1+2's fix) is necessary for their OWN internal correctness (a multi-node arm's intermediate
values need real stack discipline to avoid colliding with siblings — this is genuinely required, not optional),
but it means the arm's OWN result cell gets released before `dj` reads it, which the current shared-landing
design was never built to handle.

**UPDATE, same session: candidate direction (A) below WAS attempted in full** — see "SECOND ATTEMPT" further
down. It works for the arm-result half of the problem (four bugs found and fixed there, all verified), but
uncovered a FOURTH, deeper layer at `dj`'s own boundary that direction (A) alone does not resolve. Read that
section before starting a third attempt; direction (B) (or making `dj` itself zd-armed, which the deeper layer
now points at directly) is probably the more principled path forward.

**Two candidate fixes, as originally written (before the second attempt above found direction A incomplete) —
this needs its own dedicated session, not a rushed patch, per this row's own repeated lesson about not shipping
silent-wrong-value fixes:**

- **(A) Make the result read zd-relative instead of flat.** Change `flat_drive_match_alt`'s `IR_DISJUNCTION`
  branch to compute `op_parts_ival[j]` as a delta from `dj`'s own zd-depth to the result node's zd-depth
  (analogous to how ordinary binop operands are read live off the real stack via `g_zd_read[]`,
  `emit.cpp:3064`), rather than via `emit_binop_opnd_slot`. Since `add rsp` doesn't erase data, a *correctly
  computed* (possibly negative) offset relative to the landing's own current rsp should still find it — I did
  not verify this holds, or work out the exact delta arithmetic (it needs to account for however many arms'
  worth of `sub`/`add` happened between the write and the read, which differs by which arm actually ran — this
  is very likely where hq_P's flagged "24-byte state vs zd_k=16, measure before trusting any formula" caution
  was pointing, and I'd extend that caution to this whole direction, not just the K-size question).
- **(B) Copy-before-release: make the arm's own last node write its result directly into `dj`'s cell as part of
  reaching `dj`, instead of `dj` pulling it out afterward.** More invasive (needs the lowering or a template
  change to identify "this port transition is a value handoff to my disjunction host" and emit a direct write),
  but more clearly correct — it sidesteps the whole flat-vs-transient question by never leaving the value
  address-dependent on release timing at all. This is closer in spirit to how `IR_MATCH_ALTERNATE`'s own
  na_s/na_f glue is described (FINDING companion doc, superseded row): release happens, then a value transfer,
  in an order the box's own template controls rather than a generic shared dispatcher.

## THE 24-vs-32 QUESTION — resolved empirically, worth recording

hq_P's ruling flagged "dj 24-byte state vs zd_k=16 (zls slot granularity) — measure... before trusting any
formula." Measured via `--dump-zeta` on a synthetic Icon `write(3|5)`: `IR_DISJUNCTION`'s real granted footprint
is **32 bytes** (`+0..16` the value DESCR/result cell, `+16..24` the `alt_i` index, `+24..32` padding — all
three fields visible in the dump, `zeta_storage.c:171`'s own comment undercounts this as "24-byte" but the
`zls_field` calls there register 16 bytes of index+pad ON TOP OF a separately-registered 16-byte value DESCR,
32 total, not 24). This 32-vs-`zd_k=16` mismatch turned out NOT to matter for what I attempted: `dj` itself is
dispatched through `flat_drive_match_alt`'s special host path (`emit.cpp:2979-2985`, a `continue` that bypasses
the normal per-node zd-armed emission entirely), so `dj`'s own cell always uses the flat/permanent `op_off`
regardless of its `zon`/`K` bookkeeping — the K=16 vs 32-byte-real-footprint gap is real but appears to be
purely a zd-depth-accounting nicety for OTHER nodes' offset math relative to `dj`, not a live memory-corruption
risk for `dj`'s own cell. I did not need to resolve it to get as far as I did, but flagging it since it's
unverified beyond "didn't visibly bite this specific witness."

## KILLSWITCH DISCIPLINE

`SCRIP_VLIST_ALT` stays default OFF — nothing here is safe to flip until the remaining gap actually closes.
Whoever picks this up next does NOT need to re-derive bugs 1+2 above; the diffs are complete and were verified
inert for the existing `IR_MATCH_ALTERNATE` path — re-apply them as a starting point and go straight to the
result-addressing question.

## REGRESSION EVIDENCE

SCRIP HEAD at session start (post `git pull --rebase`, fresh `make pristine`) `a71d3034`; corpus/.github also
pulled current. **SNOBOL4 crosscheck (`test_crosscheck_snobol4.sh`), both modes: 325/325 PASS, 0 DIVERGE** —
identical to pre-session (killswitch default-off path byte-identical, confirmed via `diff -q` on the DONE-WHEN
witness's unarmed output). **Icon quick crosscheck (`test_crosscheck_icon.sh`): 4/4 PASS** — expected, since the
final committed diff touches only `lower_snobol4.c` (SNOBOL4-exclusive per the architecture's "no language
identity past LOWER" rule — Icon goes through `lower_icon.c` entirely) plus a pure deletion of
never-triggered-by-default code in `emit.cpp`. **Prolog crosscheck (`test_crosscheck_prolog.sh`) showed
run-to-run variance (98/2/89, then 96/5/88, 98/1/90, 96/2/91) on the IDENTICAL committed binary across four
consecutive runs** — confirmed pre-existing flakiness, not a regression, by running the UNMODIFIED baseline
(`git stash`) back-to-back and observing numbers in the same noisy band (98/2/89). Did not chase the flakiness
itself; out of scope for this row, flagged here so it isn't mistaken for something this session caused.

## ADDENDUM — cross-validated against hq_C's `probe/vlist_select/` ladder (banked mid-session, after this
## FINDING's main body was written)

hq_C independently root-caused the OLD (pre-this-session) lowering's mechanism in parallel (message
`vlist-root-caused-4-line-witness`: arm-1's recede pops the enclosing expression's cells via
`n6_lit_string_beta` before reaching arm 2 — a real, precise diagnosis, but of the temp-var/`VLIST$n` mechanism
this session's lowering change (above) has already replaced; the fix hq_C proposed, "catch the arm-failure edge
at the VLIST boundary and restore the spine there," is written in terms of a spine cell and a named variable
that no longer exist in the new `IR_DISJUNCTION` lowering, so it does not directly transplant — see the reply
sent this session for the reconciliation). hq_C also banked a 7-witness oracle-backed ladder,
`corpus/probe/vlist_select/{c01,c02,v01..v05}` (SCRIP commit `718139e70` on the corpus repo), and reported
`SCRIP_VLIST_ALT=1 SCRIP_ZETA_STORAGE=frame-rsp` byte-correct on every rung **under the OLD lowering**.

**Re-ran the full ladder against THIS session's new `IR_DISJUNCTION` lowering, both storage arms, mode 3:**

| witness | cell-stack (default) | frame-rsp |
|---|---|---|
| c01_control_first_arm_succeeds | DIFFERS | **MATCH** |
| c02_control_no_select | MATCH (no VLIST content) | MATCH |
| v01_select_min | DIFFERS | **MATCH** |
| v02_select_concat_and_assign | DIFFERS | **MATCH** |
| v03_array_proto_via_select | DIFFERS | **MATCH** |
| v04_listappend_growth | **SIGSEGV rc=139** | **MATCH** |
| v05_treebank_pushlist_235 | **SIGSEGV rc=139** | `*** stack smashing detected ***`, rc=134 |

**Two things this confirms, one thing it flags:** (1) The new lowering is corroborated independently — 6/7
byte-correct under frame-rsp, including `v04`, which SIGSEGVs under cell-stack, is exactly consistent with this
FINDING's own diagnosis above (the bug is cell-stack/zd_plan-specific; frame-rsp's addressing model never hits
`disj_sigma_copy`'s flat-vs-transient mismatch the same way cell-stack's real push/pop does). (2) `v05`'s
`stack smashing detected` under frame-rsp is a DIFFERENT failure signature than anything else in this doc, and
is very likely NOT a new defect in this lowering: `v05` is the largest/most repetitive witness in the ladder
(6291 bytes, simulating treebank's real growth pattern at scale), and a stack-canary trip on a large,
statement-heavy top-level program under `--zeta-storage=frame-rsp` is exactly the signature of the
**separate, already-root-caused** `zeta-frame-rsp-second-wild-write` row (this same session, earlier — see
`FINDING-2026-08-23-seat03-frame-rsp-wild-write-root-cause-and-fix-plan.md`: frame-rsp's outer scope never
reserves real stack space for its ZLS region, and the crash threshold scales with how much a program's
top-level code actually needs). Did not re-confirm this by measuring `v05`'s own zeta region size against that
row's ~20KB witness threshold — flagging the connection for whoever picks up either row rather than chasing it
here, since conflating two rows' evidence in one FINDING is exactly the kind of provenance blur this project has
been bitten by before.

## SECOND ATTEMPT (same session, after the ADDENDUM below was written) — three MORE bugs found and fixed,
## a FOURTH discovered and NOT fixed — reverted again, this is now a four-layer problem, not a one-line gap

Went back in with all four pieces from the FINDING body above (host-recognition + admission, the arm-seed
`_wzdepth` fix, the `gin`/`oin` override) PLUS a new attempt at the `disj_sigma_copy` addressing gap (candidate
direction A). Full diffs below; all reverted again. **Do not reapply piecemeal without reading this whole
section — each fix in isolation makes a DIFFERENT symptom visible, and it is easy to mistake "the symptom
changed" for "it's fixed."**

**Bug 3 (this round) — the arm-seed pop amount was absolute, not arm-relative, so it over-popped into
preceding LIVE siblings.** The very first re-test (`corpus/probe/vlist_select/v01_select_min.sno`:
`OUTPUT = 'a=[' (IDENT(x) 0, 5) ']'`) lost the LITERAL `'a=['` — not just the VLIST's own value. Root cause:
when a VLIST is not the entire right-hand side of a statement but embedded inside a larger expression, whatever
precedes it in the same run (here, the `'a=['` literal) has already done its own real `sub rsp` and is still
live, waiting for the enclosing concat to read it later. My Bug-1-fixed `_wzdepth = zout[i]` (used as the real
pop amount) is an ABSOLUTE depth from the run's own start — popping by that full amount from an arm member
releases not just the arm's own accumulated cells but the preceding sibling's too. Fix: subtract the arm's own
seed first — `_wzdepth = zout[i] - (zout[zarm[i]] - zd_k(nodes[zarm[i]]))`. Verified: `'a=['` survives with this
fix; confirmed by hand-tracing the exact byte arithmetic against the emitted `.s` (documented in-session, not
reproduced here for space — the `add rsp, 64` in `n16_lit_integer_α`'s exit correctly lands back at the
disjunction's own resting depth, not the run's absolute zero, once this correction is in).

**Bug 4 (this round) — `disj_sigma_copy`'s "does this arm have a value" gate treats ANY negative offset as
"no value, skip the copy."** Direction A's negative zd-relative offsets (Bug 3 above makes them correctly
negative — an arm's result sits below the landing's post-release rsp) get silently swallowed by the template's
existing `IF(_.op_parts_ival[i] >= 0, ...)` gate, which predates this work and exists to skip genuinely
resultless arms (a control-flow-only arm whose `sno_arm_result`/`icn_arm_result` filter returned `NULL`, so
`rj` is a null pointer — a real, distinct case). Fixed by introducing an unambiguous sentinel
(`ZD_DJ_NO_RESULT`, a `#define` in `emit.h` beside the file's existing byte/opcode constants, not a new
variable) instead of overloading `-1`/sign, and changing the gate to `!= ZD_DJ_NO_RESULT`. Verified via asm:
the copy code now emits (`mov rax, [rsp + -64]` / `[rsp + -16]` for the two arms in `v01`), and BOTH offsets were
confirmed by hand to match exactly where each arm's own result write landed, given Bug 3's fix.

**Bug 5 (this round, NOT FIXED, why this attempt was reverted again) — `dj` itself is flat-addressed, and flat
addressing is only self-consistent when nothing precedes `dj` in the same run.** With bugs 1-4 all fixed and
independently verified correct by hand-arithmetic (both offsets land exactly where expected), the VLIST's own
value was STILL wrong. Traced fully: `dj` is dispatched through `flat_drive_match_alt`'s special host path
(`emit.cpp` ~2976, a `continue` that bypasses the normal per-node zd-armed emission entirely), so `dj`'s own
cell is ALWAYS written/read via its flat, permanent `op_off` — valid only when the real `rsp` equals the whole
function's baseline (net zero real pushes) at the moment `dj`'s code executes. That is true when nothing
precedes the VLIST in its run (`vl_alt_second.sno`'s case) but false the moment something does (`'a=['` in
`v01`): at the point `dj`'s α runs, `'a=['` has already done a real `sub rsp,16` and is still live, so `rsp` is
16 bytes off the function baseline, and `dj`'s `[rsp+80]` writes 16 bytes away from where `op_off=80` is
*supposed* to mean. Meanwhile, the code that later CONSUMES `dj`'s value (the enclosing concat's own binop, an
ordinary zd-armed node) reads it via a completely different, self-consistent mechanism — a zd-relative delta
(`g_zd_read[]`, `zd_out[consumer] - zd_out[dj]`) that assumes `dj`'s value lives wherever the *delta* implies
relative to the *current* rsp, not wherever the *flat* number implies relative to the *function baseline*.
These two addressing conventions — `dj`'s own flat self-address, and the zd-relative delta everything else uses
to reach it — only agree when PRE (whatever precedes `dj` in its run) is zero. Hand-verified the exact byte gap
in `v01`: `dj`'s cell as written lands at `baseline+64`; the consumer's delta-computed read lands at
`baseline-16`; the two disagree by exactly `PRE + (dj's own K) = 16+16 = 32`... (worked through several times
this session; the exact arithmetic is reconstructable from `zd_out[dj]`, `zd_k(dj)`, and the consumer's own
`zd_out`, but is NOT re-derived here — see the note below on why this needs a fresh pass, not a copied formula).

**Why this is now a bigger question than "one more offset formula," and why I stopped rather than iterate a
fifth time:** the pattern across bugs 3-5 is the same shape appearing at three different scopes (within an arm,
across an arm boundary, and now at `dj`'s own boundary with its *enclosing* expression) — every one of them is
some variant of "a flat/permanent address and a zd-relative/transient address disagree unless a specific
depth-zero precondition holds, and VLIST is exactly the construct that violates that precondition by embedding
inside larger expressions." Patching each occurrence as it's discovered has a real risk of converging on a
CORRECT-LOOKING but actually-coincidental fix that only holds for the specific witnesses tested (the same
failure mode EVIDENCE 2b already documented for the very first prototype this session inherited). The
principled fix is almost certainly to make `dj` itself zd-armed — i.e., give it a real `sub`/`add rsp` around
its own lifetime sized to its actual 32-byte footprint, so EVERY consumer (arms, `disj_sigma_copy`, and
whatever encloses the VLIST) addresses it through the SAME convention — rather than patching the flat-address
math to account for PRE at each of the (unknown number of) sites that touch it. That is a structural change to
`flat_drive_match_alt`'s dispatch (shared with `IR_MATCH_ALTERNATE` — needs proving inert there too, the same
diligence bugs 1-4 already went through) and deserves a fresh session's full attention, not the tail end of an
already-long one running on hand-verified arithmetic that has already needed correcting three times tonight.

**Full diffs for this round, all reverted, kept here so the next attempt starts from bugs 1-4 fixed rather than
re-deriving them:**
```c
// emit.cpp, zd_plan's ZD5B block — host recognition + admission (bugs 1 unchanged from the ADDENDUM above, repeated for context):
for (int r0 = 0; r0 < rl_main; r0++) { IR_t * env = nodes[run[r0]]; int is_dj = (int)env->op == IR_DISJUNCTION; if ((int)env->op != IR_MATCH_ALTERNATE && !is_dj) continue; int ei = run[r0];
    int pairs2 = is_dj ? 2 * (int)IR_LIT(env).ival : env->n_operands;
    for (int a = 0; a + 1 < pairs2; a += 2) { IR_t * c2 = env->operands[a]; int rl0 = rl; int bad = 0; int g2 = 0; int first = 1;
        while (c2 && g2++ <= n) {
            int ci = -1; for (int k = 0; k < n; k++) if (nodes[k] == c2) { ci = k; break; }
            if (ci < 0 || claim[ci] >= 0) break;
            if (bb_src_of(nodes[ci]) || emit_floater_kind(nodes[ci])) { bad = 1; break; }
            { int aop = (int)nodes[ci]->op; int leaf = is_dj || (aop == IR_MATCH_LIT || /* ...unchanged whitelist... */ aop == IR_MATCH_BAL);
              if (!leaf) { bad = 1; break; }
              if (is_dj || nodes[ci]->n_operands > 0) { run[rl] = ci; rpos[ci] = rl; claim[ci] = hi; zarm[ci] = ei; if (first) { aent[ci] = 1; first = 0; } rl++; } }
            c2 = zd_chase(c2->γ.node);
        }
        if (bad) { /* unchanged rollback */ }
    } }

// emit.cpp, consumption loop — gin/oin override AND the corrected (bug-3-fixed) arm-relative _wzdepth:
{ if (zarm && zarm[i] >= 0) { if (gt == nodes[zarm[i]]) gin = 0; if (ot == nodes[zarm[i]]) oin = 0; } }
int _wzdepth = (zarm && zarm[i] >= 0) ? (zout[i] - (zout[zarm[i]] - zd_k(nodes[zarm[i]]))) : (int)zd;

// emit.cpp, flat_drive_match_alt — signature gains zd_on/zd_out (both already in-scope locals at the one call site):
static void flat_drive_match_alt(IR_t **nodes, int n, int i, bb_label_t **lbls, bb_label_t **betas, bb_label_t **na_s, bb_label_t **na_f, bb_label_t ***fc_sig, bb_label_t *node_γ, bb_label_t *node_ω, bb_label_t *chain_ω, unsigned char *zd_on, int *zd_out) {
// ...call site: flat_drive_match_alt(nodes, n, i, lbls, betas, na_s, na_f, fc_sig, node_γ, node_ω, &lbl_ω, zd_on, zd_out);

// emit.cpp, IR_DISJUNCTION's op_parts_ival computation — arm-relative zd delta when the result is zd-armed, sentinel otherwise:
int rk = -1; if (rj) for (int k = 0; k < n; k++) if (nodes[k] == rj) { rk = k; break; }
int64_t rs = (rk >= 0 && zd_on[rk]) ? -(int64_t)(zd_out[rk] - (zd_out[i] - zd_k(nd))) : rj ? (int64_t)emit_binop_opnd_slot(rj) : (int64_t)ZD_DJ_NO_RESULT;
g_emit.op_parts_ival[j] = rs;

// emit.h, new named constant beside the file's existing opcode/frame #defines (NOT a variable):
#define ZD_DJ_NO_RESULT  (-9000000000000000000LL)

// bb_disjunction.cpp, disj_sigma_copy's gate:
IF(_.op_parts_ival[i] != ZD_DJ_NO_RESULT, /* ...unchanged body... */)
```

## RECEIPTS

Full session: `git pull --rebase` all three repos at start; `make pristine` before every measurement quoted.
Diagnostics used throughout: `SCRIP_ZD_DIAG=1` (per-node `[ZD]` trace), `SCRIP_ZD_DEPTH=1` (join-point
consistency census, `emit.cpp:2542` — pre-existing tooling, not written this session), direct `.s` reading for
both modes, `--dump-zeta` for slot-layout ground truth. Committed: `src/lower/lower_snobol4.c` (TT_VLIST
rewrite + `sno_arm_result` helper), `src/emitter/emit.cpp` (SCRIP_ZD_VLIST_OMEGA deletion only — the ZD5B
extension attempt and its two bug fixes are NOT committed, fully specified above for reconstruction).
