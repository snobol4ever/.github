# FINDING 2026-09-12 hq_P — DEFINE's entry label is resolved STATICALLY (last textual DEFINE wins), not at the DEFINE that executes

**Row:** `snobol4-snoflake-three-sigsegv-crashes-bypass-the-error-246-stack-overflow-guard`
**Tree measured:** SCRIP `4bcd6bd21` (cure landed; measured at `9104f01e6` + cure), corpus `ada938d3d`, .github `b3a4a1b2`. Build: incremental `make`, `RT_OPT=-O0`.

## The claim

`DEFINE(proto, entry)` rebinds an already-defined function's ENTRY POINT at runtime — Gimpel's standard
re-DEFINE idiom. SCRIP resolved that entry label at COMPILE time with **last-textual-DEFINE-wins**, so a
function re-DEFINE'd to a different entry re-entered at its ORIGINAL entry. Where the idiom guards a
self-call (`COPYL`), that is unbounded recursion: the row's reported "stack overflow / SIGSEGV" was never a
stack-guard defect at all — the guard was reporting a real infinite recursion correctly.

## The witness (12 lines, minted here)

```
	DEFINE('G(L)T')
	                                :(GEND)
G	OUTPUT = 'at-G'
	DEFINE('G(L)', 'G_1')
	G = G(L)
	DEFINE('G(L)T')                 :(RETURN)
G_1	OUTPUT = 'at-G1'
	G = 'done'                      :(RETURN)
GEND
	OUTPUT = G('x')
	OUTPUT = 'second call:'
	OUTPUT = G('y')
END
```

`sbl -bf`: `at-G / at-G1 / done / second call: / at-G / at-G1 / done`.
SCRIP before the cure: `at-G` forever, then ERROR 246. Both modes.

## Root cause, two sites

1. **`src/driver/scrip.c` (dentry table).** For each DEFINE bind node the builder walked to the CALL STUB's
   baked `IR_GOTO_DEFERRED` label and used THAT as the entry — the last-wins static winner — instead of the
   bind node's OWN entry operand (`ir_define_bind_entry()`). `bb_define.cpp:438`'s own comment says the seal
   exists so "a call reads the binding in force when it runs rather than a baked winner"; the table feeding
   it handed it the baked winner. Cured by preferring the bind node's own operand.
2. **The table was built in the TEXT region only**, so m3 never had it. Factored into one helper
   `sn4_dentry_table_build()` called from both main-graph regions.

## The both-medium half (the part worth keeping)

With (1) and (2) fixed, m4 went byte-exact but **m3 did not**. Cause: the M4-BODY-SEAL emits
`x86("lea", "r9", "[rip + __]", _fn, blbl)` → `x86_load_ro`, which in TEXT emits the symbolic label but in
**BINARY bakes the numeric `_fn` queried at COMPILE time** — the default entry. So the seal that exists to
unpin the baked winner silently re-pinned it in one medium. ⭐ The instrument lesson: a template that takes
`(pointer, label)` is only both-medium-correct when the pointer and the label denote the SAME thing; here the
label was per-DEFINE and the pointer was per-FUNCTION, and nothing in the type system says so.
Cured by resolving BY NAME at runtime (`rt_define_bind_body(fname, entry)` → `rt_entry_resolve`), which is
identical in both media because no address is baked at all.

## Measured result (row DONE-WHEN, 8 witnesses x 2 modes)

Before: 8 of 8 witnesses red in at least one mode. After: **6 of 8 green in BOTH modes**
(`infix-to-polish`, `wang-theorem-prover`, `word-ending-analysis`, `gimpel-conversions`,
`gimpel-sorting-functions`, `gimpel-tree-pattern`). The 3 raw SIGSEGVs were already gone on this tree
before the cure; the ERROR 246s were this defect.

## Two residual reds, both a DIFFERENT defect — NOT this one

- `gimpel-linked-list-functions`: now reaches statement 28 and raises **ERROR 235** (subscripted operand is
  not table or array). Gimpel's idiom re-DEFINEs the LOCALS LIST too (`COPYL(L)T` → `COPYL(L)`), so the inner
  activation must NOT shadow `T`. SCRIP bakes one frame layout per function from the last-wins DEFINE, so the
  recursive call saves/nulls `T`. **The entry label is now dynamic; the formals/locals list still is not.**
  That is the next row in this family, and it needs per-DEFINE activation shims (role 4/5 machinery exists).
- `gimpel-snobol-statement-reader`: **ERROR 038** goto undefined label. Unrelated to DEFINE entry binding.

## A separate defect found while ablating (NOT cured here, no row yet)

SCRIP's DEFINE is purely compile-time: a DEFINE that never EXECUTES still makes the function callable.
```
	                                :(SKIP)
	DEFINE('F(X)')
SKIP	OUTPUT = 'before'
	OUTPUT = F(1)
F	F = 'yes'                       :(RETURN)
END
```
`sbl -bf` raises **ERROR 022 undefined function called**; SCRIP prints `yes`. Same root shape (DEFINE treated
as a declaration, not a statement). The narrower witness `b.sno` — a call made BEFORE the entry-DEFINE
executes — still takes the later DEFINE's entry for the same reason, and is left red deliberately rather than
papered over.

## Instrument defect cured in passing (the row's own DONE-WHEN)

The DONE-WHEN's m4 arm ran `--compile f.sno -o f.bin` and then EXECUTED `f.bin`. `--compile` emits ASSEMBLY
TEXT, so every m4 arm died `Permission denied` (rc=126) and reported "diverges from the oracle" — a goalpost
no cure could ever reach, reading as 8 compiler reds. ⭐ It is the same shape seat02 cured in this file's own
LEDGER one pass earlier (missing `SNO_LIB`), in the same DONE-WHEN, and it survived that pass because the
arm's failure LOOKED like the defect under study. Fixed to assemble+link exactly as
`test_snoflake_suite.sh:compile_m4()` does. With the arm fixed, 8 of the 10 reported reds were the
instrument, not the compiler.

## Control arm (CEO-611: no cure that trades one program for another)

`make test` on the cured tree: **164 arms, 151 green, 10 red, 3 refused**. The SAME 13 non-green arms are
red/refused with **identical rc** on the stashed pre-cure tree — so none of them is this change. Every
SNOBOL4, Icon and Prolog semantic gate and the SNOBOL4 corpus board are green on both arms. No master or
package board was run here (ONE RUNNER, ONE BOARD — the coo's).

Gate `test_gate_sno_define_entry_label_rebinds_at_runtime.sh` is wired into `make test` and
`scripts/gate_wiring.tsv`, proven **FAIL-ONCE** on the pre-cure tree (RED in BOTH media) and **PASS-ONCE**
after. ⭐ The m4 arm is not decorative: two thirds of this cure passed m4 byte-exact while m3 still looped,
so a TEXT-only check would have certified a half-cure.

Landed at SCRIP `4bcd6bd21`.
