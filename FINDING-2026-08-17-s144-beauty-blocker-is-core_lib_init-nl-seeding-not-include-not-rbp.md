# FINDING s144 — THE REAL BEAUTY-SELF-HOST BLOCKER IS `core_lib_init` SILENTLY PRE-SEEDING `nl`/`lf`/etc. AS
# GLOBAL NAMES. NOT `-INCLUDE`. NOT AN RBP/ζ-FRAME DEFECT.

**Session:** 2026-08-17 s144 (Claude Sonnet 5). Investigation only this session — root cause fully isolated and
confirmed via gdb, no fix landed. SCRIP HEAD unchanged (`84faa529`).

---

## ⛔ THE HEADLINE

The s142/s143 finding's diagnosis — "beauty stops at `-INCLUDE` because SCRIP tries to really open the `.inc`
files" — is **WRONG** and is retracted here. The `.inc` files are present on disk (`global.inc` etc. sit right
beside `beauty.sno` in `corpus/programs/snobol4/demo/beauty/`); real `-INCLUDE` directives in beauty.sno's own
header compile and execute correctly in both SCRIP and the oracle. `Parse Error` is not a SCRIP compiler
diagnostic — it is **beauty.sno's own program output**, emitted by its `mainErr1` label when its self-hosted
`*Parse` grammar (beauty is a hand-rolled shift-reduce parser generator, not a naive pattern) fails to
recognize a line of its own source fed back to it as subject text.

**The actual root cause:** `src/runtime/core/core.c`'s `core_lib_init()` — called unconditionally as the very
first statement of `main()`, before `rt_gva_island`/`gva_register`/anything program-specific — pre-populates
the global SNOBOL4 name table with hardcoded values for a family of plain (non-`&`-prefixed) names:
```c
NV_SET_fn("tab", ...) NV_SET_fn("ht", ...) NV_SET_fn("nl", "\n") NV_SET_fn("lf", "\n")
NV_SET_fn("cr", ...)  NV_SET_fn("ff", ...) NV_SET_fn("vt", ...)  NV_SET_fn("bs", ...)
NV_SET_fn("nul", ...) NV_SET_fn("epsilon", pat_epsilon()) NV_SET_fn("fSlash", ...)
NV_SET_fn("bSlash", ...) NV_SET_fn("semicolon", ...) NV_SET_fn("UCASE", ...) NV_SET_fn("LCASE", ...)
NV_SET_fn("digits", "0123456789")
```
None of these plain names are SPITBOL builtins per the manual (only `&`-prefixed keywords and `&ALPHABET`
itself are real builtins). Real SPITBOL requires a program to build these conveniences itself — which is
EXACTLY what beauty.sno's `global.inc` does, by hand, via `&ALPHABET POS(n) LEN(1) . name` matches (10 lines,
`corpus/programs/snobol4/demo/beauty/global.inc:2-13`). Because SCRIP's `core_lib_init` has already written a
real newline into `nl` before beauty.sno's own `global.inc` code ever runs, and because beauty's `Label`/`Stmt`/
`Comment`/`Control` grammar all key off `nl` via `BREAK(... nl ...)`, the ENTIRE grammar is desynced against
what it was written and oracle-tuned against (`nl` == the empty string in real SPITBOL, because the oracle
provides no such convenience seeding).

## HOW THIS WAS ISOLATED (ASM-DIFF-FIRST discipline, ~20 progressively smaller repros)

1. Fed beauty.sno only the single line `START\n` as subject (bypassing the `-INCLUDE` red herring entirely):
   oracle echoes `START` (beautifies correctly); SCRIP prints `Parse Error`.
2. Localized to `Label = BREAK(' ' tab nl ';') ~ 'Label'` and `Src = 'START' nl`: `SIZE(Src)` = 6 in SCRIP
   (5 + a real newline byte) vs 5 in the oracle (`nl` evaluated to the EMPTY string in the oracle).
3. Isolated `nl`'s value directly: `SIZE(nl)` = 1 in SCRIP, 0 in the oracle, straight after `-INCLUDE
   'global.inc'` — before `global.inc`'s own `&ALPHABET POS(10) LEN(1) . nl` line even runs.
4. Chased a false lead: believed this was `-INCLUDE`-specific (identical statement inline vs via `-INCLUDE`
   gave different results). This was a confound — separately discovered that statements AFTER the first one
   in a fall-through-reached `-INCLUDE`d file do not execute in EITHER engine (a genuine, oracle-and-SCRIP-
   shared quirk, NOT investigated further, NOT the bug — noted for whoever next touches `-INCLUDE` semantics).
5. **Minimal repro with NO `-INCLUDE` at all**, gdb-confirmed dead code:
   ```
   OUTPUT = 'before'                              :(SKIPIT)
   &ALPHABET POS(10) LEN(1) . nl
   SKIPIT  OUTPUT = 'nl=[' nl '] size=' SIZE(nl)
   END
   ```
   SCRIP: `nl` ends up a 1-char newline. Oracle: `nl` stays empty. Set a gdb breakpoint on
   `rt_keyword_read_snobol4` (the only function the dead match statement could reach that touches `&ALPHABET`)
   — **never hit**; program runs start-to-finish without the breakpoint firing. The dead statement is
   genuinely never executed; `nl`'s corrupted value predates it entirely.
6. Bisected which POS() values reproduce this with the SAME dead-code shape: only `POS(10)` — every other
   tested position (5, 65, 100, 200) correctly leaves the capture target empty. Then bisected which VARIABLE
   NAMES reproduce it holding POS(10) fixed: only `nl` (and by inspection of the source, presumably `lf`,
   `tab`, `ht`, `cr`, `ff`, `vt`, `bs`, `nul`, `epsilon`, `fSlash`, `bSlash`, `semicolon`, `digits`, `UCASE`,
   `LCASE` — the exact `core_lib_init` seeding list, not yet each individually re-verified this session).
   A control name (`zzzvar`) at POS(10) correctly stayed empty — proving this is a NAME-TABLE collision, not
   a POS/LEN emitter defect.
7. `grep -rn '"nl"\|"lf"'` across `src/` landed on `core.c`'s `core_lib_init()`, confirmed by reading it and
   cross-referencing against the compiled assembly's `main:` prologue (`call core_lib_init@PLT` is the first
   instruction, ahead of `rt_gva_island`/`gva_register`/`rtcc_load_all`).

## ⛔ RESIDUE — NOT YET CLOSED THIS SESSION

- **The exact mechanism by which `core_lib_init`'s `NV_SET_fn("nl", ...)` reaches the GVA-cached register slot
  (`[r9+0]` in the compiled program) has not been traced instruction-by-instruction.** `NV_SET_fn` writes into
  the name-value table; `gva_register`/`NV_bind_gva` (called AFTER `core_lib_init` in `main`'s prologue) binds
  a GVA register slot to that same name. The likely mechanism: `NV_bind_gva("nl", &cell)` copies the ALREADY-
  SEEDED table value into the fresh cell at bind time (rather than the cell starting genuinely zeroed and the
  table lookup being lazy) — this would explain everything observed but was not confirmed by reading
  `NV_bind_gva`'s definition (grep found only its ONE call site in `gva_register`; the definition itself is
  presumably a macro or in a header not yet located).
- **Full enumeration of affected names not completed.** Strongly suspected (by direct inspection of the
  `core_lib_init` seeding block) but not each individually gdb/oracle-diffed this session: `lf`, `tab`, `ht`,
  `cr`, `ff`, `vt`, `bs`, `nul`, `epsilon`, `fSlash`, `bSlash`, `semicolon`, `digits`, `UCASE`, `LCASE`. Also
  unconfirmed: whether `ARB`/`BAL`/`FENCE`/`ABORT`/`FAIL`/`REM` (registered as PATTERN VALUES in the same
  function, immediately after this block) are legitimate — the manual DOES list these as real `&`-prefixed
  keyword constants (`&ARB`, `&BAL`, `&FENCE`, `&ABORT`, `&FAIL`, `&REM`, confirmed p.desc in this session's
  manual reading) but `core_lib_init` registers them WITHOUT the `&` (as `NV_SET_fn("ARB", ...)` not
  `NV_SET_fn("&ARB", ...)` — needs checking whether that's a second, separate collision class or intentional
  plumbing for the `&`-stripping done in `rt_keyword_read`/`rt_keyword_read_snobol4`).
- **No fix attempted.** The two live candidate directions: (a) delete/gate this seeding entirely — it has no
  basis in the manual and actively conflicts with any program that uses these common short names for its own
  purposes (beauty.sno is exactly such a program, and this is idiomatic SNOBOL4, not an edge case); (b) if this
  seeding was added deliberately for some other reason (a prior session's convenience shim, possibly to help
  some OTHER corpus program that expects it — not checked this session), a scorecard/corpus sweep is needed
  BEFORE deleting it, to confirm nothing else in the 1396-program corpus depends on the pre-seeded names.
  ⛔ Do not delete blind — grep the corpus for bare (non-`&`) references to `nl`/`lf`/`tab`/`ht`/`cr`/`ff`/`vt`/
  `bs`/`nul`/`epsilon`/`fSlash`/`bSlash`/`semicolon`/`digits`/`UCASE`/`LCASE` as FIRST-USE-BEFORE-ASSIGNMENT
  sites first; a program relying on the SCRIP-only convenience (if any exist) would regress silently.

## WITNESS MINTED

`corpus/probe/m1/m1_alphabet_unreached_capture.sno` + `.ref` (oracle-verified, `nl` stays empty). Confirms the
defect independent of `-INCLUDE`, independent of `&ALPHABET`'s runtime value, independent of control flow —
purely a name-table pre-seeding vs. real-SPITBOL-blank-slate mismatch.

## NEXT SEAT — pick up exactly here

**(a) Trace `NV_bind_gva`'s definition** (only one call site found, in `gva_register`, `rt.c:515`; definition
not yet located — check for a macro, or a different file/header via its declaration) to confirm whether GVA
bind-time copies the pre-seeded table value into the register cell (this session's leading hypothesis) or
something else.
**(b) Corpus sweep BEFORE any fix**: grep all of `corpus/` for bare references to each of the ~16 seeded names,
to establish whether ANY existing green corpus program depends on the convenience seeding (if so, the fix needs
a compat path, not a blind delete).
**(c) Decide and land the fix** — most likely deleting the `core_lib_init` seeding block for the plain-name
family (keeping `ARB`/`BAL`/`FENCE`/`ABORT`/`FAIL`/`REM`/`SUCCEED` pattern-value registration, which likely IS
correct/needed machinery for `&ARB` etc. to resolve through `rt_keyword_read`'s "not a hardcoded keyword, fall
through to NV_GET_fn" path — needs (a) resolved first to know if deletion here breaks that fallback).
**(d) Re-run beauty self-host** after the fix — same witness (`beauty.sno < beauty.sno`), expect it to progress
well past line 10 for the first time this milestone.
**(e) Re-run the s141/s142/s143 ζ-SM false-positive gate** (5 witnesses) to confirm this fix is orthogonal to
the ζ-frame class and doesn't perturb it — expected zero interaction since this defect is pure name-table
initialization order, nowhere near RBP/RSP frame management.

## MEASURED

Minimal repro reproduced deterministically 5/5 in earlier session-internal reruns. gdb-confirmed dead-code
non-execution (breakpoint on `rt_keyword_read_snobol4` never hit). POS-value bracketing: 1/5 tested positions
(10) affected. Name bracketing: `nl` affected, `zzzvar`/`chv`/`v5`/`v65`/`v100`/`v200` not affected — consistent
with a name-table collision, not a pattern-matching or POS/LEN emitter defect. No SCRIP source changed this
session (investigation only). `handoff_status.sh` not run — nothing to push from SCRIP/corpus beyond the new
probe witness pair; `.github` has this finding doc, not yet committed/pushed pending credential.
