# FINDING-2026-08-04-CLAUDE-SN4-BB-PROBE-SUITE-141-PROBES-SEQUENCE-IS-WIRING-FENCE1-IS-FENCE0

## Session: 2026-08-04 (Sonnet)

## Summary

Zero SCRIP code commits. Deliverables = 141-probe BB test suite in `corpus/probe/bb/` with
pinned SPITBOL goldens, two theory results proved experimentally, and three new defect
classifications.

---

## Result 1 — SEQUENCE is pure LOWER wiring. No box, no ports, no cell.

Proved by deleting the `seq_*` box from `test_sno_1.c` and replacing it with eight static
edges assigned at LOWER time (Experiment A). Output byte-identical to original; re-proved
against `sbl -b` this session.

Rule (complete): for a sequence P = M1 M2 … Mn:
- `P_α → M1_α`  ·  `P_β → Mn_β`
- `Mi_γ → M(i+1)_α`  (i < n)  ·  `Mn_γ → P_γ`
- `Mi_ω → M(i-1)_β`  (i > 1)  ·  `M1_ω → P_ω`

Value: derived by the CONSUMER from its own entry cursor. `str(Σ+Δ0, Δ−Δ0)` is always
available at the consumer because patterns consume contiguously and the cursor is monotone
within one activation.

Consequence: the `cat()` accumulator bug in `test_sno_2/3.c` (seq = cat(seq, member)) is
structurally unreachable once sequence is wiring — no running total exists to double-count.

---

## Result 2 — Pattern leaf boxes carry no value cells. Derives from consumer entry cursor.

Experiment B extended Result 1 to the whole engine: deleted value cells of POS0, BIRD, BLUE,
LEN1, RPOS0, ARBNO, assign, write, and ARBNO_Δ0. Output still byte-identical. The value cell
is NEVER in the leaf — it belongs in whichever construct reads the matched extent, and that
construct already has its own entry cursor.

"DERIVE, DON'T ACCUMULATE" (ruling 3, `test_sno_1.c`) is a special case of this general rule.

---

## Result 3 — ALTERNATE irreducibly needs exactly one word. Proved negative.

Case 7 built: `'ABCZ' ? POS(0) ('AB'|'A'|LEN(2)) $ OUTPUT 'B' RPOS(0)`.
- Subject `AB` → arm 1 must be resumed.
- Subject `AXB` → arm 2 must be resumed.
Same compiled site, different runtime winner. Static wiring of `alt_β` to any fixed arm
fails one or the other. Tested F_X / F_AB / F_A against both subjects — only dynamic `alt_i`
passes both.

State requirement: one `int` per activation. No frame needed (word lives in ARBNO's depth
arena when inside ARBNO; plain scalar otherwise). Confirms the five-frame list in THE MODEL:
ALTERNATE correctly absent from it.

---

## Probe suite

**`corpus/probe/bb/`** — committed `04cc6415`.

```
probes/<ID>.sno    141 probes
probes/<ID>.ref    141 SPITBOL goldens (sbl -b)
gen_probes.py      families L A N X D F
gen_probes_fence.py families G H
mkrefs.sh          regenerate / --verify goldens
run_suite.sh       THE GATE — SCRIP vs .ref, XFAIL baseline
XFAIL.run          46 known-failing (mode-3, HEAD)
BB-PROBE-MATRIX.md all probes with oracle output recorded
SUITE.md           documentation
```

Families: **L** leaf/seq (20) · **A** alternate (13) · **N** ARBNO (21) · **X** nested ARBNO
(11) · **D** deferred `*` (13) · **F** fence basics (6) · **G** FENCE0 sprinkle (27) ·
**H** FENCE1 sprinkle (30).

Baseline: **95 pass / 46 xfail / 0 regression**, mode-3.

Hardening carried from `bb_witness_ladder.sh`:
- Crash detection via shell wait-status (SCRIP swallows SIGSEGV, exits 0).
- Every probe prints (minimum `=S`/`=F`) — silent probes cannot distinguish match from
  pre-print crash.

---

## Defect classification — 46 xfail split as three classes, not one

### Class 1 — correct output then crash (31 probes)

Families L (4) · N (5) · D (1) · F (5) · G (7) · H (19).

The semantics are almost entirely right; the teardown is not. 19 of 20 H-family
(FENCE1) failures are this shape. Predicted by W-1: FENCE1 is one of the five
constructs on the RBP-frame list. Logic landed, frame did not.

### Class 2 — crash before any output (5 probes)

`D10 N08 N09 N14 G14`. Deeper; investigate after Class 1 cleared.

### Class 3 — wrong output, no crash (3 probes)

**`D07`, `D08`**: `LEN(*N)` deferred integer does not evaluate.
  - `N = 3 ; 'abcdef' ? POS(0) LEN(*N) . OUTPUT` → oracle `abc`, SCRIP empty.
  - D08 (`SPAN $ N LEN(*N) . FIELD`, manual's worked example): gets N=12 right,
    FIELD empty.

**`H01`**: `FENCE(P)` implemented as bare `FENCE`. See below.

---

## Sharpest new finding: H01 — FENCE1 is FENCE0

The discriminating triple:

```
'ABCZ' ? POS(0) ('A' | 'AB') <fence?> ('CD' | 'C') 'Z' RPOS(0)
```

| probe | fence    | oracle | SCRIP   |
|-------|----------|--------|---------|
| G00   | none     | `=S`   | `=S` ✅ |
| G01   | `FENCE`  | `=F`   | `=F` then SIGSEGV |
| H01   | `FENCE(P)` | `=S` | **`=F`** ❌ deterministic, exit 0 |

`FENCE` (nullary, manual p.125): backs into it → whole match fails.
`FENCE(P)` (function, manual p.208): backs into it → alternatives within P stop being
examined, BUT components BEFORE the fence are still retried. Here `('A' | 'AB')` before the
fence should retry into `'AB'` and succeed. SCRIP routes the FENCE(P) failure edge to abort
instead, collapsing FENCE1 into FENCE0.

Three passing neighbours: G00, H05 `(('ab'|'a') 'cd')`, H07 `(('ab'|'a') 'bcd')`.
Bracket is tight. No crash in the way — cheap MONITOR-FIRST target.

---

## False green identified in `bb_witness_ladder.sh`

Row "ARBNO not retried + outer cap" is ✅ in the ladder. Same pattern as `N07` in the suite:

```
bare program (no trailing statement):  exit 0, ok
+ one trailing `OUTPUT = '=S'`:        SIGABRT, *** stack smashing detected ***
```

The ladder's programs END at the match statement. The corrupted RSP is never used; the
stack-canary check fires only when the function returns — which the ladder never does.
`N07` with a trailing statement fails 5/5, SIGABRT. BENCH timing line emits garbage
negatives (`lower=-828931713000.00ms`) confirming RSP landed on the bench struct.

REMEDY: add a trailing no-op statement to every ladder row. Not done this session —
that edit touches `bb_witness_ladder.sh` which is in the SCRIP repo and would require
regen ×4. Flagged for W-1c.0 session.

---

## Next rung

**W-1c.0 still open.** The bracket: "outer capture, no ARBNO" crashes with correct output.
Minimal reproducer from the suite: `L13` — `'abcd' ? ((LEN(2) . A) LEN(2)) . B`.
Passing neighbour: `L12` — `POS(0) LEN(4) . OUTPUT RPOS(0)` (inner member capture, no parens
on the outer). Trigger is a capture whose operand is a **parenthesized group**, not capture
per se.

Three candidates in order of cheapness:
1. `H01` — FENCE1/FENCE0 collapse, wrong output, no crash, exit 0.
2. `D07`/`D08` — `LEN(*N)` deferred integer, wrong output, no crash.
3. `L13` / W-1c.0 — sequence-capture crash, MONITOR-FIRST.
