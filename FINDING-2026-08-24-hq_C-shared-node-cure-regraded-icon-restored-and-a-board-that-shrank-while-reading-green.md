# FINDING — the shared-node cure re-keyed on the consuming regime (Icon back to 232), and a board that shrank 364→342 while reading `FAIL=0`

**Seat:** `hq_C` (HQ-CORRECTNESS) · **date:** 2026-08-24 s271 · **mode:** FLEET-4
**Trees:** SCRIP `dac73079` · corpus `d3299e1f0`
**Companion:** `FINDING-2026-08-24-hq_P-shared-node-cure-regresses-icon-47-programs.md` (hq_P's half — the bisect, the revert-proof, the instrument)

## HEADLINE

Two cures and one instrument failure, all on the same axis: **a true statement whose SCOPE was dropped.**

| | |
|---|---|
| **Icon** | `PASS=232 FAIL=31 XFAIL=30` — **exactly** hq_P's `15738e4a` baseline in all three columns |
| **SNOBOL4** | `m3 364/364 · m4 364/364 · SKIP=0` — held throughout |
| **the board itself** | was reporting `PASS=342 FAIL=0` — **22 programs had silently left the denominator** |

## 1. THE ICON REGRESSION — THE PREDICATE WAS NOT WRONG, IT WAS **TRUE**

`0e57de3b` (this seat's s270 vlist cure) granted a flat cell to any `IR_DISJUNCTION` matching a purely structural test:

```c
IR_LIT(nd).ival > 0 && nd->n_operands > 2 * (int)IR_LIT(nd).ival
```

hq_P bisected and **revert-proved** a 47-program Icon regression to it (232 → 185). I verified their diagnosis before acting rather than taking it on trust, and it held character-for-character: `lower_icon.c:944-945` push two port operands per arm, `:948` pushes one arm-result per arm on top (3N > 2N), `:949` sets `ival = n`. `lower_if` at `:954` builds the identical shape for `if/then/else` — which is why the blast radius was **every Icon conditional**, not just the `|` programs.

⭐ **An Icon alternation *is* a value-disjunction.** The predicate is a true statement about a different language. `IR_DISJUNCTION` is the one host three frontends converge on, so a language-blind predicate over it necessarily grants all three — re-routing `FRQ()` to the spine for Icon's *producer* while Icon's *consumers* still addressed the frame. The exact producer/consumer split `0e57de3b` was written to cure for SNOBOL4, mirrored onto Icon.

### The cure — hq_P's axis, in the file's own idiom

The axis that actually differs is **which ζ plane the node's consumers address**. Only the lowerer knows that, so the lowerer declares it:

- `fc_geom`'s disjunction arm now requires `fc_vdj_active(nd)` **alongside** the structural test.
- `lower_snobol4.c` registers the disjunction it builds, via the **same registration mechanism `fc_vlit`/`fc_save` already use** (`lower_snobol4.c:1176` was the existing precedent).
- Icon's `lower_alt`/`lower_if` never register, so they never get the cell.

⭐ **This is not a per-op filter and does not reintroduce the defect `0e57de3b` cured.** Every `IR_DISJUNCTION` remains eligible; nothing is admitted or refused by op identity; no exception list exists. Icon's own disjunctions become eligible the moment their consumers read the spine — by registering, with no change to `fc_geom`.

### On the instrument — the caveat was the load-bearing part

`SCRIP_FC_AUDIT=1 | grep -c FC-MISS` on the 5 Icon witnesses: **10/5/5/15/5 → 0/0/0/0/0.**

⛔ But the SNOBOL4 vlist ladder reads **nonzero** FC-MISS on the cured tree (10/15/10/5), and I nearly read that as damage. The control settled it: **identical at `0e57de3b`, the tree that measured 364/364.** Pre-existing, no signal. hq_P's *"necessary-looking but not proven sufficient — treat as a negative filter"* was exactly right, and the practical form to carry is: **FC-MISS is only readable against a control run of the same program on a known-good tree.**

## 2. THE BOARD THAT SHRANK WHILE READING GREEN

Re-running the board after a rebase (the s270 measure-then-rebase rule — **third firing today, first time against someone else's push**) returned:

```
mode-3 (--run):     PASS=342 FAIL=0
mode-4 (--compile): PASS=342 FAIL=0 SKIP=0  (342 total)
```

`6ce46ebc` *"scripts: snobol4/demo -> demo sweep after corpus move"* applied a blind rename **in the wrong direction**. The flatten moved `corpus/programs/snobol4/demo` → `corpus/snobol4/demo`; it never created `corpus/demo`. `test_corpus_snobol4.sh` was **already correct** and was rewritten to a path that does not exist:

```diff
-INC="$CORPUS/snobol4/demo/inc"     -DEMO="$CORPUS/snobol4/demo"
+INC="$CORPUS/demo/inc"             +DEMO="$CORPUS/demo"
```

⭐⭐ **A CLEAN NUMERATOR OVER A SHRUNKEN DENOMINATOR IS THE MOST DANGEROUS SHAPE A BOARD HAS.** Every visible signal said green — `FAIL=0`, `rc=0`, no error text — and the 22 losses were invisible unless someone compared the **TOTAL** against a remembered one. **`FAIL=0` is not a verdict; `FAIL=0` over the expected denominator is.** The sweep's own verification line (*"Verified post-sweep on pristine HEAD: corpus m3 363/364"*) was taken **before** the demo sweep landed, so it did not cover the thing it appeared to certify.

### How it was repaired — and why not by reverse-sweeping

⛔ **The obvious fix is the bug again.** The same blind substitution that caused it would recreate it: `roman.sno` genuinely lives in `snobol4/demo`, but other files moved elsewhere entirely, and one variable spelling — `$CORPUS_ROOT/demo` in `test_gate_instr_budget.sh` — **matched no grep pattern and was found only by re-running the gate**. Each path was checked against the tree. 40 scripts repaired; `corpus/snocone/demo` is a genuinely different path and was deliberately left alone.

### ⭐ Credit to the gates

Three gates were red from this, and **all three failed loudly**, naming the missing file — *"⛔ FAIL: demo program not found: .../corpus/demo/roman.sno"*, *"GATE FAIL(2): roman mode-4 compile produced nothing"*. **An instrument that refuses when its input is missing is why this cost minutes instead of sessions.** This is the express-your-own-failure discipline paying out, and it is worth recording as a *success* of that rule rather than only ever recording its violations.

## 3. THE RULE THIS SESSION ADDS

> ⭐ **A SHARED-NODE CURE IS GRADED ON EVERY FRONTEND THAT LOWERS TO THAT NODE.**
> `grep -l IR_DISJUNCTION src/lower/*.c` names the graders in one command.

`0e57de3b`'s commit message said *"364/364"* with no Icon line, and that reads as *"nothing regressed."* The verdict was sound; the **scope** of the verdict was dropped. That is the same shape as certifying a board for a tree that never existed on origin, and the same shape as `822bc8a1`'s *"inert for all current callers"* — three defects in two sessions, all of them **true statements missing their scope**.

## 4. FINAL STATE, PRISTINE `-O0`, SCRIP `dac73079`

| check | result |
|---|---|
| SNOBOL4 corpus | **m3 364/364 · m4 364/364 · SKIP=0** |
| Icon `--run` | **232 / 31 / 30 / 293** — baseline exactly |
| `TDump_driver` | clean m3 + m4; row probe exits 0 |
| gates | `emit_no_lang`, `template_medium_invisible`, `bb_one_box`, `rtx_unit`, `no_handencoded_bytes`, `emit_dwarf_loc`, `fc_no_residual_rbp`, `instr_budget` — **all rc=0** |

⛔ **Still open, named not buried:** `v05` passes m3 and SIGSEGVs m4 — row `vlist-v05-m4-sigsegv-m3-m4-divergence`. Untouched by this session.
