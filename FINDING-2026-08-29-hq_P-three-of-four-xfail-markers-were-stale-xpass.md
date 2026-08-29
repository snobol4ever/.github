# FINDING — 3 of the 4 `.xfail` markers in `crosscheck/snocone` were STALE: the bugs were fixed and nobody promoted the markers

**hq_P · 2026-08-29 · SCRIP `5e2d01b7` · corpus `1716f2652` · row `corpus-crosscheck-probe-total-conversion`**

Converting `crosscheck/snocone` surfaced four documented `.xfail` sidecars. Each was re-verified individually by
running the source and diffing against its own `.ref`:

| witness | the marker's claim | measured |
|---|---|---|
| `rungA09/A09_anchor` | "`&ANCHOR` keyword not honoured by `?` operator in Snocone" | ✅ **matches `.ref`** — STALE |
| `assign_014_assign_indirect_dollar` | "indirect-assignment LHS (`$name = expr`) not in landed subset" | ✅ **matches `.ref`** — STALE |
| `assign_015_assign_indirect_var` | "indirect-assignment LHS (`$v = expr`) not in landed subset" | ✅ **matches `.ref`** — STALE |
| `hello_literals` | "alt-eval `E_VLIST` (e1,e2) expression, tree kind 22, not in landed subset" | ⛔ differs — **still valid** |

**75% of the documented expected-failures were lying.** Their features had landed; nobody went back and promoted
the markers. RULES already rules on this direction: *"XPASS is surfaced exactly as loudly as FAIL: the bug got
fixed and nobody promoted the marker, which is exactly as actionable as a fresh failure, just in the opposite
direction."* These never surfaced because **nothing was reading these sidecars** — `convert-blocks` consumes only a
`<family>.xfail` suite sidecar (`sidecar_xfail_path`, `:676`), not the per-source `.xfail` convention this tree
uses, so the markers sat unread beside their sources.

## Why it matters beyond three files

A stale XFAIL marker is **worse than no marker**: it is a standing, sourced-looking claim that a feature does not
work. Read at face value it steers work away from something already done, and it makes a green result look like an
anomaly to be explained rather than the truth. `A09_anchor`'s marker even names a mechanism
(*"emit_x64_snocone does not propagate kw_anchor to pattern match path"*) — precise, plausible, and false.

⛔ **Operational rule: never inherit an `.xfail` claim. Re-run the witness.** It costs one command and it was wrong
three times out of four here. ⭐ And the deeper point: a marker in a convention **nothing reads** cannot self-correct
— it can only rot. Either wire the convention into the tool that consumes the tree, or delete it.

The three stale markers went into the suites with their (now green) sources. `hello_literals` stays loose with its
marker, re-verified valid, pending the row's ruling on where red witnesses live.
