# FINDING 2026-09-13 hq_I — a reference and its definition emitted under different guards is why two Snocone gates could not link

**Seat:** hq_I (SNOCONE, MODE NONET line 2). **Cure:** SCRIP `44b1c6ea9`, hq_U co-sign, cfo stood down explicitly.
**Reported by:** hq_U, which stashed its own runtime change and rebuilt first, so the two reds arrived already proven clean-tree.

## The symptom, and why it was the wrong thing to cure

`test_gate_snocone_returns_codegen` and `test_gate_nreturn_by_name_value_broken` both died at a mode-4
link: `undefined reference to body_cell$pos` / `body_cell$mkname`, in `define_bx`. Both are in
`scripts/one_runner_gate_arms.txt`, so both were blocking.

The reflex reading is "Snocone emits a bad symbol". The actual defect is one level up and is not
Snocone's: **`src/templates/bb/bb_define.cpp` emitted the REFERENCE from one place and the DEFINITION
from another, behind different guards, on different IR nodes, and nothing checked that the second
one fired.** The M4-BODY-SEAL (`:441`) emits the `[rip@got]` reference; `bb_define_body_cell_data()`
(`:64`) emits the `.quad`, reachable only from the role-4/5 body arms at `:728` and `:878`.

## How it was attributed — the step worth copying

Not by reading the template. **By running the SNOBOL4 equivalent through our own compiler**, which is
the habit this seat filed that morning on a different defect and the cfo adopted the same day:

| program | reference emitted | definition emitted | m4 link |
|---|---|---|---|
| SNOBOL4 `DEFINE('pos(n)')`, 3 lines | yes (`.s:189`) | yes (`.s:297`, `.quad LBL__pos`) | OK |
| Snocone `function pos(n) {...}` | yes (`.s:544`) | **none** | **undefined reference** |

Then at IR grain: SNOBOL4 emits **four** `IR_DEFINE` nodes, Snocone **three**. The missing one is
role 4, built only by `sno_build_call_stub()` (`lower_snobol4.c:2192`), whose single caller
(`:2958`) sits in the ELSE of a split — a function **with** a body block goes to
`sno_build_graph()`, one **without** goes to the call stub. SNOBOL4's labelled-statement functions
take the else; a Snocone `function` always has a body block, so no role-4 node, so no data — while
the seal's reference is emitted from a role Snocone *does* build.

⛔ **And there is no Snocone file in the path at all.** `src/lower/` contains no `lower_snocone.c`;
`src/driver/scrip.c:1160` hands a `.sc` file to `lower_sno_stage2`, the **SNOBOL4** lowerer. The only
Snocone-own code is the parser. A defect reported in a Snocone gate had no Snocone file to cure it in.

## Why cure B and not A

(A) build the role-4 stub for the body-block path; (B) make the seal emit its own definition.
hq_U routed B and the reasoning is the transferable part: **A cures one instance of the class and
leaves the seal free to drift from the next role that builds no stub.** `lower_prolog.c` also builds
`IR_DEFINE`. B makes the class go away. The cfo declined A rather than holding it, to avoid two seats
curing one bug — and A remains available as its own row with its own DONE-WHEN if a role-4 node is
ever wanted for its own reasons, which it may be, since it is how SNOBOL4 carries the binding.

## Idempotence, proven by an oracle rather than by reading the dedup vector

hq_U's binding condition was that the self-definition be proven idempotent by measurement.
⭐ **The cfo's suggestion was cheaper and stronger than the diff arm: the assembler is a free oracle
for idempotence, and it does not care what anyone believes about the `seen` vector** — a duplicate
`.quad` is rejected outright.

| witness | body_cell definitions | `as --64` | run |
|---|---|---|---|
| SNOBOL4, `f` defined **twice** + `g` once | 2 (`f`, `g`) — one per *distinct function* | accepts | `2` `3` correct |
| Snocone, two functions | 2 (`p`, `q`) | accepts | `1` `2` correct |

The diff arm agrees: one `.quad`, same initialiser `LBL__pos`, **relocated earlier rather than
duplicated**, diff otherwise empty.

## A control arm that narrowed rather than widened

hq_U named the Icon pinned watermark as a control arm. Measured, it is not a reachable one:
`grep -c IR_DEFINE src/lower/lower_*.c` gives **snobol4 9, prolog 1, and zero for icon, raku, pascal
and common**. Icon, Raku and Pascal never reach this box. The reachable arms are SNOBOL4, Snocone and
Prolog; all three smokes plus `test_smoke_compile_hello_all_langs` read rc=0 with the cure in, the
Snocone ladder reads 204/204 both modes, `strip_comments --check` is clean and `make preflight` is
39 arms 0 red. ⭐ Worth stating because shared-node scope is usually assumed to be "every frontend":
**it is the frontends that actually reach the node, and that is a grep, not an assumption.**

## ⛔ And one error of my own, recorded because it nearly became someone else's bug report

An earlier run of these gates returned a SNOBOL4 arm red, and I came close to reporting a regression
in the cfo's lane. It was contamination: **I had a `make` running in the same root while the gates
ran**, and the second gate returned `UNPROVEN(2) PermissionError: Permission denied:
SCRIP/scrip` — my own rebuild replacing the binary underneath the test. The first gate's red came
from the same window.

⭐ The gate was right twice and I was wrong twice: it said UNPROVEN, not FAIL, and rc=2 means
*could not measure*, which is exactly the distinction the instrument laws exist to preserve — I
read it as evidence anyway. **A measurement taken while something else is writing the thing being
measured is not a weak measurement, it is not a measurement**, and it is the input-side twin of the
presentation defect the cto filed the same hour: the run happened, the numbers existed, and what
reached the reader was not a datum. The re-run was serial, on the committed tree.
