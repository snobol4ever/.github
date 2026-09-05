# FINDING seat03 2026-09-05 (FLEET-20, row icon-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect)

## 1. A CHECKED-IN REF WAS BACKWARDS, AND ITS OWN MARKER TEXT REPEATED THE ERROR WITH CONFIDENCE

`corpus/tests/icon/rung36_jcon_ck.expected` encoded scientific-notation exponents without a `+`
(`1.015599e14`). Its 2026-08-30 `.xfail` marker went further and stated the direction as a fact: "scientific-
notation output includes a stray '+' on the exponent (e+14 vs Icon's own e14)".

**Both were wrong.** Compiled and ran the upstream twin fresh against the real oracle
(`/home/resources/icon-master/bin/{icont,iconx}`, Icon Version 9.5.25a) twice, independently, with full
command tracing: real Icon prints `1.015599e+14`, WITH the `+`. SCRIP already matched it. The stored ref
was the thing that was wrong, most likely typed or cut incorrectly at some point before 2026-08-30, and a
confident-sounding marker sentence let that error survive at least one full re-classification pass without
being re-checked against a live oracle run. Re-cut the ref from a fresh oracle capture; verified
byte-identical afterward.

**The generalisable point, since this project already has several entries in this family (the `collate`
misattribution, the ICN4/Icon-denominator three-correct-counts case, `nargs`'/`struct`'s allocator-serial
non-reproducibility): a marker or ref that states a mechanism with confidence is not evidence of that
mechanism — it is evidence that someone believed it once.** The fix cost one fresh oracle run; trusting the
old marker would have cost whoever picks up `ck.icn` next an hour chasing a phantom SCRIP formatting bug in
the wrong direction.

## 2. AN ANNOUNCED MINT NEVER LANDED, AND A DEEPER ROOT CAUSE ALMOST WENT ORPHANED

`rung36_jcon_iobig.xfail` already routes to `icon-cset-keyword-element-generation-inside-a-coexpression-
segvs` (hq_B, minted 2026-09-04, ablated to an 8-line `suspend !&digits` inside a co-expression witness).

Today's `FINDING-2026-09-05-seat01-icon-relop-value-not-coerced-to-real-and-iobig-coexpression-thread-segv.md`
independently re-derived what is almost certainly the SAME defect straight from `iobig.icn`, to a
considerably deeper level (an exact gdb backtrace through `kw_cset_prime`'s lazy one-shot init, the precise
trigger — first-ever reference to a builtin keyword cset from a coexpression's own pthread — and three
ruled-out simpler explanations). That FINDING's text says *"Minting
`icon-arizona-class-coexpression-thread-first-malloc-segv`"* — but no such row exists in either
`QUEUE.tsv` or `QUEUE.done.tsv`. The mint was announced in prose and never executed (or did not land),
which would have left the deeper root cause reachable only by someone who happened to read that specific
FINDING file, while the row anyone would actually find by symptom (`iobig`'s own marker) still pointed at
the shallower 2026-09-04 ablation.

Cross-referenced the FINDING onto the existing row's LEDGER (not minting a duplicate) so the two converge
on one place. **Generalisable point: "minting" a row is a claim about a side effect, not a description of
intent — a FINDING that says it minted something is exactly as reliable as any other stated mechanism, and
checking that the row actually exists costs one `grep`.**

## 3. FOUR NEW DEFECTS, EACH A DIRECT EXTENSION OR SIBLING OF TODAY'S RELOP-COERCION LANDING

Ablating `arith.icn`'s and `ck.icn`'s residual STRICT-suite diffs (both otherwise explained by today's
`rt_relop_val_coerce` landing, SCRIP `53138c1e5`) surfaced that the fix's scope is narrower than the
symptom it was aimed at:

- **`icon-relop-value-coercion-does-not-cover-numeric-strings`** — the landed fix coerces a successful
  relop's result only when operand A carries the `DT_R` (real) tag; it does not cover numeric-STRING
  operands (`" 5 " >= " 5 "` should return integer `5`, SCRIP returns the untouched string `" 5 "`).
  Verified both directions on a two-line minimal repro.
- **`icon-real-builtin-does-not-recognize-radix-notation`** — `real("16rff")` etc. should parse
  (`255.0`) like `integer()` already does; SCRIP's `real()` fails outright. Explicitly NOT the same as the
  already-CLOSED `icon-arizona-class-radix-notation-wrong-value` (that cure touched `char()`/`chr()`/
  `integer()` only — read before assuming a match).
- **`icon-real-builtin-returns-inf-on-overflow-instead-of-failing`** — `real("3e500")` should fail like
  Icon's own conversion semantics; SCRIP returns the libc `inf` value instead.
- **`icon-jcon-misc-coexpr-activate-corrupted-target-pointer-segv`** — `misc.icn`'s marker was stale in
  the dangerous direction (claimed rc=1, actual rc=139 SEGV). gdb backtrace already in hand:
  `scrip_coexpr_activate` (`src/runtime/rt/rt_coexpr.c:184`) dereferences a `target` pointer
  (`0x100000002`) that looks like a wrong-slot argument rather than a valid pointer; caller frame
  unresolved.

All four rows carry a DONE-WHEN exercised this session and confirmed to currently read red (and, for the
misc row, confirmed to correctly REFUSE with `S4E_HOME` unset) — none were left as the placeholder-only
state a bare `mint` produces when no acceptance test is supplied inline.

## LEDGER (see the row's own baton for the full 21-marker account)

Population unchanged, `csv=0 allxfail=0 files=21` — none of the above reached a full PASS this session.
STRICT rung suite all 3 modes: `PASS=50 FAIL=7 BADEXIT=1 XFAIL=21 MISSING=2 TOTAL=79`; `strip_comments.py
--check` rc=0 (383 files). Zero SCRIP source changes this session (all changes are `corpus/tests/icon/
*.xfail` text plus one `.expected` re-cut); the board's own +1 PASS/-1 FAIL movement versus this session's
starting reading is explicitly NOT claimed here — it arrived via this session's own `git pull --rebase`
picking up concurrent fleet work before any of the above was measured.
