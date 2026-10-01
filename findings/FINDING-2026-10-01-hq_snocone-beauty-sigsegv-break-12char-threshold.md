# FINDING-2026-10-01-hq_snocone-beauty-sigsegv-break-12char-threshold

⛔ SUPERSEDED same day by FINDING-2026-10-01-hq_snocone-beauty-sigsegv-zd-plan-assign-cond-depth-mismatch.md. The
localization below (the `String = *SQ | *DQ` alternation in `Expr17`) is WRONG -- it was a plausible but unproven
read of the 12-char threshold alone. The real root cause, proven at the instruction level with real ELF symbols and
measured RSP deltas, is a stack-depth miscalculation in `GenTab()` (`corpus/library/Gen.sc`), a function with no
pattern alternation in it at all; `String`/`Expr17`/DEFER are not involved. The 12-char threshold is real but is a
side effect of flipping which branch of a DIFFERENT construct (`GenTab`'s `if (~(DUPL-based assign)) alt;`) runs.
The reproduction steps and the 11-vs-12 threshold measurement below are still accurate as *observations*; only the
"suspect construct" conclusion is retracted. Read the superseding finding first.

## Context
Task `snocone-every-suite-to-100-under-tenet-ceo-1383`. SncRungs 338/338, SncBench 16/16, SncDemo 22/23 — the one red is the Snocone self-host beauty demo (`corpus/demos/snocone/beauty/beauty.sc` + the 16-file `corpus/library/*.sc` chain declared in its `.chain` sidecar), SIGSEGV rc=139 in mode 3, confirmed also in mode 4 is implied by the task NOTE ("crashes in both modes"); this sitting measured mode 3 directly.

## Reproduction (measured, SCRIP `dd6007ab8` corpus `6a9d71b08`, RT_OPT=-O0)
Full repro: concatenate the 16 `corpus/library/*.sc` files (order per `beauty.chain`) + `beauty.sc`, run under `scrip` fed `corpus/demos/snocone/beauty/beauty.in` (14 lines) — SIGSEGV, fault address `0x8`, "emitted code, mode 3's slab", si_code=1 (SEGV_MAPERR).

**Reduced to ONE input line**, no change to the program: feeding the chain only `beauty.in`'s line 3 —
```
      '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' UNITS BREAK(',') . UNITS  :F(FRETURN)
```
— still crashes identically. Lines 1-2 alone do not crash.

**Byte-precise threshold** (bisected on the quoted-string length, trailing ` UNITS BREAK(',') . UNITS` held fixed, goto clause irrelevant):
- quoted content ≤ 11 chars → rc=0, correct output
- quoted content ≥ 12 chars → rc=139, same SIGSEGV signature every time
- the long string alone (no trailing ` UNITS BREAK(',') . UNITS`) does NOT crash
- the trailing part alone (no preceding long quoted string) does NOT crash
- content need not contain commas: a run of 12 `x` + one trailing comma crashes identically (rules out "comma count"; it's string length specific to the quoted-literal token)

## Crash site (gdb, `mov 0x8(%rcx),%rcx` with rcx=0)
```
=> mov    0x8(%rcx),%rcx      <- fault here, rcx==0, fault addr = 0x8
   add    $0x1f0,%rsp
   jmp    *%rcx
```
Backtrace is 22 unsymbolized frames inside the JIT slab (expected — mode 3 has no unwind info), landing in `NV_GET_fn` (`src/runtime/core/core.c:3517`) at the C boundary. The instruction shape (load a "next" field at +8, drop a large fixed stack delta, indirect-jump) matches the alternation record layout documented in `src/templates/bb/bb_match_alternate.cpp:36`: *"ALT-FLAT: 32B record carved at alpha -- cursor@0, beta-target@8, next-alternative@16... When an ARM leaves live frames at its gamma (a nested alternation, an ARBNO, a DEFER, a FENCE -- op_alt_cell) the beta target instead rides in a 16B cell..."* — i.e. this reads as a NULL beta-target on an alternation/DEFER arm.

**Monitor bracket REFUSED (rc=2), and that refusal is itself evidence**, not a dead end: plain and `--trace` runs both SIGSEGV (rc=139) but diverge in how much stdout they emit first (plain gets further). Timing-sensitive crash-point ⇒ consistent with a corrupting write earlier (while tokenizing the long string) whose effect (a clobbered pointer) is only touched/faulted-on later, at a point that shifts under trace instrumentation. Not a clean, deterministic single-instruction logic bug.

## This is NOT a generic runtime/BREAK bug, and NOT (as far as tested) a shared lowering bug
- A plain executed Snocone pattern match `X ? BREAK(',') . Z` on the identical 44-char string works correctly (no crash) — rules out "BREAK can't handle long strings."
- **Decisive cross-frontend test**: `corpus/demos/snobol4/beauty/beauty.sno` (618-line, self-contained, the un-ported SNOBOL4 original) run through the SAME `scrip` binary with the SAME byte-identical minimal input (both the 11-char-safe and 12-char-crash cases) — **works correctly in both cases, no crash.** Since CLAUDE.md states Snocone shares `lower_snobol4.c` with SNOBOL4 (no separate Snocone lowerer), and the shared C runtime/templates are identical either way, this strongly suggests the defect is not a blanket shared-runtime bug exercised identically by both frontends.
- The suspect construct, found by grepping both sources for quoted-string recognition: `corpus/demos/snocone/beauty/beauty.sc:15-17`
  ```
  DQ = '"' BREAK('"' nl) '"';
  SQ = "'" BREAK("'" nl) "'";
  String = *SQ | *DQ;
  ```
  is **byte-identical** (modulo SNOBOL4 column layout) to `corpus/demos/snobol4/beauty/beauty.sno:48-50`. Same source shape, same deferred-pattern alternation (`*SQ | *DQ` — indirect/DEFER pattern references under `|`, exactly the construct the bb_match_alternate.cpp comment calls out as using the dynamic op_alt_cell path), different frontends, different result. This points at the **Snocone parser's construction of the pattern AST for deferred-alternation** (or a Snocone-specific AST shape that hits a different, buggy branch of the otherwise-shared lowering/emission) rather than at beauty.sc's own logic, which is a faithful port.

## What's ruled out vs. still open
- Ruled out: comma-count-specific; BREAK itself; beauty-script-level porting error in this construct (textually identical to the working original); a monitor-safe deterministic single-site bug (it's timing-sensitive, i.e. probably a corrupting write, not just a missing null check at the fault site).
- Still open: the EXACT line inside the Snocone parser/lowering path that diverges from SNOBOL4's handling of `*SQ | *DQ`-shaped patterns. Three bounded isolation attempts did NOT reproduce with `String = *SQ | *DQ` alone, nor nested one level deeper (`Token = *Integer | *String`) as standalone 6-9 line programs — the trigger needs more of beauty's real grammar context (it has ~10+ arms combined in its real top-level token alternation, deeper FENCE/ARBNO nesting than my attempts). The 1-line-input/full-chain repro (above) remains the smallest FULLY reliable witness.
- Not yet determined whether the eventual fix lands in `src/parsers/snocone/` (Snocone-owned, hq_snocone's to fix freely) or in shared lowering exercised identically by both frontends but merely unexercised by beauty.sno's own coding style (would need control-arm handling per CLAUDE.md's shared-node landing rules). The cross-frontend test is evidence toward the former but does not fully exclude the latter.

## Suggested next step for whoever continues this
`--dump-ast` / `--dump-bb` on the minimal single-line repro (`$SCRATCH/beauty_chain.sc` + the one crashing line as stdin, or build a more faithful multi-arm nested-alternation standalone snippet first) through the Snocone frontend, compared structurally against the equivalent SNOBOL4 AST/BB dump for the same `*SQ | *DQ` source line, to find exactly where the two frontends' generated IR/boxes diverge for this construct.
