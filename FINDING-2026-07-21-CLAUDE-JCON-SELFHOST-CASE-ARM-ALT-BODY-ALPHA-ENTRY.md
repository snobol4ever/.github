# FINDING: ICN-CASE-ALT-BODY — alternation as a `case` arm body entered at β (resume) not α (fresh)

**Date:** 2026-07-21
**Author:** Claude Opus 4.8
**Commit:** (ICN-CASE-ALT-BODY in SCRIP — one line in src/lower/lower_icon.c TT_CASE)
**Status:** CLOSED for the arm-body α-entry root cause. Icon rung gate 241/20/32 (at/above HEAD baseline,
zero regression). SELF-HOST BASE CASE RE-PROVEN at HEAD+fix with PRISTINE corpus source.

---

## Summary

Rebuilding the 17-module `jtran` from HEAD `3c96859c` (the parser-precedence commit) broke even
`hello, world`: the SCRIP-compiled `jtran` aborted while translating it with

```
Run-time error 500
offending value: record(ir_Label)
```

Root cause: **an alternation `A | B` used as the body of a `case ... of` arm was entered at the
alternation's β (resume) port instead of its α (fresh-start) port**, so the first alternand `A` was
skipped and only `B` ran. jtran's label-transfer emitters are built on exactly this shape.

This is the arm-**body** counterpart of the 2026-07-19 ICN-CASE-ALT-CLOSE fix, which only handled
resumable **selectors**. The precedence commit changed `|` *parsing* (and added +5 lines to lower for
the `?:=` desugar) but did **not** touch the TT_CASE arm-body wiring — so this was a latent lowering
defect newly reached on jtran's hot path once the parse fix let jtran's own source lower.

---

## Diagnosis (minimal-repro bracket)

The abort fired at `gen_bc.icn:84`, inside `bc_conditional_transfer_to`'s `"ir_Label"` arm:

```
case type(p) of {
    default: runerr(500, p);
    "ir_Label" : { put(s, j_goto_w(\bc_ir2bc_labels[p]) ) | runerr(500, p) };
    ...
```

The type dispatch was **correct** (it reached the `"ir_Label"` arm); the `\bc_ir2bc_labels[p]` lookup
was **non-null** (the label was present). Yet the `| runerr` right-hand side ran anyway. Rewriting the
arm body to an explicit `if lab := \...[p] then put(...) else {runerr}` made it work — proving the bug
was the alternation form, not the table/type logic.

Bracketing with minimal repros:

| shape | result |
|---|---|
| `A \| B` at statement top level (no case) | correct — `A` only |
| `A \| B` as `if`-then arm body | correct — `A` only |
| `A \| B` as `case` arm body | **BUG — `B` only** |
| `A \| B \| C` as `case` arm body | **BUG — `B` only** (lands on first resume point) |
| non-alternation `case` arm body | correct |

So the trigger is precisely: a **resumable arm body** (alternation / if / every) reached via a matched
`case` arm. It enters at the first β (the second alternand), never α.

Minimal:
```
case 1 of { 1: { write("A") | write("B") } };   # printed B, not A
```

---

## Mechanism

In `lower_icon.c` TT_CASE, the matched selector routes to the arm body via the `IDENTICAL` test node:

```
IR_t * be  = lower(cx, t->c[bi], NULL, ω, &bv);        // arm body entry (α, from icn_dj_α_entry)
IR_t * idc = build(cx, IR_CALL_BUILTIN, be, chain_next); // γ=be : match -> body ; ω=chain_next : miss
```

`lower_alt` returns a fresh α-entry, but the α-vs-β distinction is carried by the **edge tag** (`"α!"`
vs the default β-stamp). `build(...)` wires `idc.γ → be` with the *default* tag, so a match enters the
disjunction at β = resume = second alternand. The selector side already α-guards (lines 516/528); the
arm-body side did not.

---

## Fix

One line in `lower_icon.c` TT_CASE, right after the `IDENTICAL` node is built — α-force the arm-body
entry edge when the body is resumable, using the established force-writer idiom (same as the selector
side and `lower_every` at :1111):

```c
if (is_resumable(t->c[bi])) lc_γ_to_α(idc, be);
```

`lc_γ_to_α(nd, t)` sets `nd->γ.node = t` and stamps the edge `"α!"`, so the emitter enters the body
fresh. Gated on `is_resumable(t->c[bi])` so non-resumable bodies keep their (correct) default wiring.

---

## Verification

- Minimal repros: all corrected (`A|B`, `A|B|C`, if/plain unchanged).
- Icon smoke (`test_smoke_icon.sh`): 14/14 `--run` AND 14/14 `--compile` — zero regression.
- Full Icon rung gate (`test_icon_all_rungs.sh`): **PASS=241 FAIL=20 XFAIL=32** — at/above the HEAD
  baseline (240–241, env math-drift), zero regression. Remaining 20 are the documented pre-existing
  `rung36_jcon_*` / `rung37_*` clusters.
- `hello, world` self-hosts end-to-end (SCRIP-jtran → jlink → JVM) from **pristine, unmodified**
  `corpus/programs/icon/jcon-compiler` source — no workaround. `do_ops.icn`/`interface.icn` regenerate
  byte-identically (611 / 415 lines); `jtran.s` = 505,166 lines.

---

## NEXT (unchanged from prior cursor, now unblocked past the base case)

1. `to`-with-generator-limit: `1 to (2|4)` under-generates (root in `lower_to()`; needs the α-force
   GOTO trampoline like TT_SCAN at `lower_icon.c:623`). Gates `local`/`static` test programs.
2. True self-host: compile jtran's OWN modules through SCRIP-jtran, then byte-compare vs canonical.

## Toolchain build note

Full JVM self-host toolchain builds cold from `scripts/jcon_selfhost_build.sh` in a few minutes on a
single core (SCRIP `--compile` of the 17 modules is ~3s → 505,166 asm lines; `gcc -no-pie` ~2s). If the
repos live at `.../jcon/jcon-master` and `.../icon/icon-master` (not `.../jcon-master/jcon-master`),
override `JCONREPO`/`ICONREPO`. Needs a JDK (javac/jar) for `jcon.zip`; `apt-get update` first or the
openjdk fetch 404s.
