# FINDING — `boolptr` is NOT a "second diamond" defect: BOTH diamonds are broken, the first is masked, and the root is a per-op filter in `zd_omega_head`

**Seat:** hq_B · **Date:** 2026-08-29 · **Row:** `pascal-restore-prezeta`
(continuing seat05/seat08/seat09/seat10/seat12/seat15 — six prior passes)
**Not cured.** Mechanism is now established end-to-end, to the exact line, with a runtime witness.
A two-line candidate cure is given below **with the measured reason it is insufficient** — do not land it as-is.

## 0. WHAT LANDED THIS PASS: `SCRIP_ZD_MAP=1`, AND WHY IT MATTERED

`src/emitter/emit.cpp`. Prints, from **inside** `zd_plan()`, two tables keyed on the SAME `nodes[]` array:
`GRAPH` (per node: op, operand indices, γ/ω targets — all resolved *into that same array*) and `PLAN`
(per node: `claim`/`rpos`/`zon`/`zout`/`gpop`/`wpop`/`arm`). Inert unless the env var is set (static-cached
`getenv`); zero output and byte-identical behaviour when off.

⭐ **This retires the numbering trap for good, by removing the need to cross-reference at all.** seat12's
FINDING correctly warned that `[ZD]`'s `i=` and `--dump-ir`'s slot column are different orderings, and asked
the next actor to "find or build a way to tag nodes with a stable identifier readable from both dump paths."
The cheaper answer turned out to be: **don't use two dump paths.** Because γ/ω/operands are resolved into
`zd_plan`'s own array, the graph is legible without `--dump-ir` ever being opened. seat08 lost two sessions to
this trap and seat12 nearly lost a third; it cannot recur through this instrument.

## 1. ⛔ THE HEADLINE CORRECTION — "IT'S THE SECOND OCCURRENCE" IS AN ARTIFACT

seat12 proved by swap that the failure tracks **ordinal position**, not the relop kind. That measurement is
sound and I reproduce it. **The conclusion drawn from it is wrong.** `SCRIP_ZD_MAP` shows the two diamonds'
plans are *perfectly isomorphic* — identical claim pattern, identical relative depths, offset by exactly 272:

| | stmt1 `i>3` (looks correct) | stmt2 `i<3` (visibly wrong) |
|---|---|---|
| `IR_BINOP_TEST` | i=9  `zout=128` | i=32 `zout=400` |
| γ arm `LIT 1` / `ASSIGN` | i=10,11 `zout=144` | i=33,34 `zout=416` |
| ω arm `LIT 0` / `ASSIGN` | i=12,13 **unclaimed** `zon=0` | i=35,36 **unclaimed** `zon=0` |
| merge (read temp) | i=14 `zout=160` | i=37 `zout=432` |

**Both diamonds carry the identical defect.** The first one is *masked*: its ω path also skips its write, but
it skips onto a field that is still `false`, which is the answer the false branch wanted anyway. The second is
exposed only because stmt1 already set the field `true`.

**This model predicts all twelve prior measurements**, including every cell of seat12's swap table — which the
"second occurrence" model also fit, but for the wrong reason:

| i | stmt1 path | stmt1 printed | stmt2 path | stmt2 printed |
|---|---|---|---|---|
| 7 | γ → real write `1` | 1 ✓ | ω → **skipped**, field keeps `1` | 1 ✗ (want 0) |
| 1 | ω → **skipped**, field still `false` | 0 ✓ *by luck* | γ → real write `1` | 1 ✓ |
| 100 | γ → real write `1` | 1 ✓ | ω → **skipped**, keeps `1` | 1 ✗ (want 0) |

⭐ The `i=1` cell is the whole trap in one square: seat15 recorded stmt1 as "tracking the runtime branch
correctly" across i=7,1,100. It does not. At i=1 it **writes nothing at all** and the stale field happens to
read back as the right answer. A skipped write onto an already-correct field is indistinguishable from a
correct write *by output alone* — which is why six passes read stmt1 as the healthy control and only ever
interrogated stmt2.

## 2. THE CAUSAL CHAIN, EACH LINK MEASURED

1. **`zd_omega_head` (`emit.cpp:2498`) is a per-op filter.** It admits exactly one op:
   `if (nodes[k]->op == IR_CMP_TEST && zd_chase(nodes[k]->ω.node) == t)`. Pascal's relop lowers to
   **`IR_BINOP_TEST`** — a sibling in the same family. `emit.cpp:2731` already enumerates that whole family
   correctly for RPO (`IR_BINOP, IR_BINOP_TEST, IR_BINOP_RELOP_VAL, IR_UNOP, IR_UNOP_TEST, IR_NULLTEST_VAR,
   IR_COERCE_*, IR_CMP_TEST, IR_IDENT, IR_DIFFER`), so the narrow test at :2498 is an omission, not a
   deliberate narrowing. ⛔ This is the shape RULES.md bans ("no per-op filter within a BB family") and the
   same class as the `fc_geom` defect this row's own STEP 3 already cites.
2. **So the ω arm is never picked up as a pass-2 ω-head** → stays `claim=-1`, `zon=0`, compiled at ζ-depth 0.
3. **The test's ω edge unwinds the whole ζ stack.** `zwpop[i] = zout[i] - K` → for i=32, `add rsp,16` then
   `add rsp,384`, landing at ζ-depth 0. Correct for a statement-level concede; **wrong for a value diamond
   that reconverges.**
4. **The two arms reach the merge at different ζ depths** — γ at 416, ω at 16. The temp rendezvous still
   works (each arm's write and the merge's read are both rsp-relative and cancel), so the diamond *looks*
   fine in isolation. What does not survive is everything downstream.
5. **The consuming CALL reads its whole operand list at γ-depth offsets.** `n38 = __pas_field_set(p, idx, val)`
   is compiled for ζ-depth 448; on the ω path rsp sits 416 bytes higher, so every operand read misses.

**Runtime witness (gdb, break `by_name_dispatch.c:2729`, two-field variant so a correct index is non-zero):**

```
SET#1  (const→field, γ-free)  args[0]=1  args[1]=1  args[2]=1     <- all correct
SET#2  (relop→field, ω path)  args[0]=0  args[1]=0  args[2]=0     <- ALL THREE are garbage zeros
```

`__pas_field_set` then hits its own guard — `long n = ...args[0].i; if (n <= 0) { *out = args[2]; return 1; }` —
and **returns without writing anything.** The field silently keeps its previous value. That is the entire
visible bug.

⚠️ Note `args[2]` reading `0` is a **coincidence of garbage**, not a correctly-computed `false`. The row title
`pascal-relop-into-array-and-field-lvalues-loses-value` names the symptom accurately but points at the wrong
operand: the *value* is not what is lost — the whole operand vector is.

## 3. THE CANDIDATE CURE, AND THE MEASURED REASON IT IS NOT ENOUGH

Two lines, both removing a filter rather than adding a special case:

```c
/* emit.cpp:2498 — admit the sibling op */
if ((nodes[k]->op == IR_CMP_TEST || nodes[k]->op == IR_BINOP_TEST) && zd_chase(nodes[k]->ω.node) == t)
/* x86_asm.h:2156 — a reconverging arm needs a PUSH; the guard drops every negative pop silently */
if (site == X86H_JMP && port == X86P_GAMMA && _.op_zgpop != 0) s += x86_add("rsp", (long)_.op_zgpop);
```

Both are required; **neither does anything alone** (measured — the `!=0` guard alone is a no-op, because
without link 1 no negative `gpop` is ever produced). `x86_add` already encodes negative immediates correctly
in BOTH media (sign-extended imm8, else `u32le` two's-complement imm32; text prints `add rsp, -240`), so
BOTH-MEDIUM is satisfied by construction — only the caller's `> 0` guard blocked it.

**Measured effect — 5 of 6 witnesses cured, 1 regressed:**

```
boolptr.pas   11 -> 10 ✓ (the row's own witness)   d_relop_then_const  10 -> 10 ✓
c_threestmt  111 -> 100 ✓                          e_const_then_const  10 -> 10 ✓
f_const_then_relop 11 -> 10 ✓                      g_relop_norb         1 -> 0  ✓
a_plainvar    10 -> 11 ⛔ REGRESSION (was correct)
```

⛔ **Do not land it.** The reason is precise and is the real remaining work: with link 1 in place the ω arm
becomes **its own run, and every run in `zd_plan` starts at `int zd = 0`.** So the arm writes the shared temp
at a *depth-0-relative* address, the push then corrects rsp for the merge, and the merge reads at a
*depth-272-relative* address. The two arms now rendezvous at different addresses. `boolptr` survives this
because its temp write lands on a frame slot that still coincides; `a_plainvar`'s does not.

## 4. NEXT ACTOR — ONE SPECIFIC CHANGE, NOT A SEARCH

**Seed the ω-head run's starting depth from the test node instead of from zero.** `zd_plan`'s per-run
accumulator is unconditionally `int zd = 0;` inside the `if (ok)` block. A run entered from a *reconverging*
ω port must start at the test's pre-`K` depth, and that test's `zwpop` must then not unwind to 0. Get those
two consistent and the temp rendezvous, the operand vector, and the merge depth all agree without any push at
all — the `!= 0` guard above becomes unnecessary rather than load-bearing, which is the sign the fix is right.

⛔ **Grade it across every frontend before landing** (SHARED-NODE LAW): `zd_plan` and `x86_asm.h` are on the
path of all seven languages. `a_plainvar` (below) is the cheapest regression detector found so far — it is a
plain `boolean` local with no pointer, no field, and it broke *first*.

**Witnesses, all reproducible from this file** (`corpus/tests/pascal/boolptr.pas` is the committed one; the
rest are throwaways, kept out of the corpus deliberately since the row is mid-bisect and STEP 1 forbids moving
the denominator):

```pascal
{ a_plainvar — the regression detector. expect 1,0 }
program a(output); var b : boolean; i : integer;
begin i := 7; b := i > 3; if b then writeln(1) else writeln(0);
              b := i < 3; if b then writeln(1) else writeln(0) end.
{ f_const_then_relop — proves it is not "the second diamond": the relop here is the FIRST
  relop in the procedure and still fails, because it is not the first FIELD WRITE. expect 1,0 }
program f(output); type rp = ^rec; rec = record f : boolean end; var p : rp; i : integer;
begin i := 7; new(p); p^.f := true;  if p^.f then writeln(1) else writeln(0);
                      p^.f := i < 3; if p^.f then writeln(1) else writeln(0) end.
```

## 4b. ⭐ THIS ROOT IS ALREADY NAMED IN ANOTHER ROW, AND COVERS 2 OF THE 4 STANDING PASCAL FAILURES

The Pascal gates fail on exactly four probes in both modes — `boolidx`, `boolptr`, `deep5`, `pb34` (measured
this pass under `make pristine`; the same four every prior pass left untouched, so nothing here is a
regression). Sorting them by this diagnosis:

- **`boolptr`** — this FINDING's witness. Field lvalue. ✔ diagnosed to the line.
- **`boolidx`** — `a[0] := i > j` … ×4. **Same defect through an ARRAY lvalue.** `SCRIP_ZD_MAP` shows four
  `IR_BINOP_TEST` diamonds (i=11,23,35,47 — one per array assignment), each with an ω target, and 20
  unclaimed nodes. This is the "array" half of the parked row
  `pascal-relop-into-array-and-field-lvalues-loses-value`.
- **`deep5`** — unrelated: `BOMB — bb_var_frame: PAS-DISPLAY L>=4 fallback unimplemented`. A missing
  feature that names itself honestly; belongs to the uplevel/nested-proc family, not here.
- **`pb34`** — prints `2` where the ref says `1`; sets + `repeat`/`until`. Not shown to share this root.

⭐ **`test_gate_pascal_m3.sh:79` already names this defect, in prose, in a comment** — fbench's XFAIL is
recorded as blocked on `pascal-m4-for-spine-leak-64b-per-iter`, described there as "*zd_plan misses
IR_BINOP_TEST merge points*". That row's one-line description was right all along; what was missing was the
mechanism, the line, and the runtime witness. Curing it should close `boolptr` + `boolidx`, unblock
`pascal-fbench-nested-function-self-assign-null-name` (BLOCKED-ON that row), and very likely retire
`pascal-relop-into-array-and-field-lvalues-loses-value` — which is currently parked
`GRANT-NEEDED:lon-new-global-permission` for a global it does not need.

⛔ **Gate legibility defect, noted not fixed:** both Pascal gates print `FAIL=4` and never name the four. The
names exist — the scripts write them to `RESULTS` (default `/tmp/m3_results.tsv`) — but nothing echoes them,
so the summary a reader actually sees forces every session to re-derive the failing set. This row's own STEP 2
requires "the failing set by name, not just a count", and the gate that grades the row does not supply it.
Left alone deliberately this pass: touching the gate mid-bisect moves the instrument while it is in use.

## 5. DISPOSITION

`SCRIP_ZD_MAP` landed (inert, graded). Behavioural changes **reverted** — the tree carries the instrument
only, and `boolptr` still prints `1,1`. Sent to hq_C (correctness owner). The likely-duplicate queue row
`pascal-relop-into-array-and-field-lvalues-loses-value` is almost certainly this same defect reached through
an array lvalue instead of a field; it is parked `GRANT-NEEDED:lon-new-global-permission`, and on this
diagnosis **it needs no new global at all** — worth re-reading before anyone requests that grant.
