# FRONTEND-ICON.md — Tiny-ICON Frontend (L3)

Tiny-ICON is a planned frontend for snobol4x only.
SNOBOL4 and Icon share a bloodline — Griswold invented both.
The Byrd Box IR is the bridge: same four ports (α/β/γ/ω), new Icon frontend
feeding the same TINY pipeline. Goal-directed generators map directly to Byrd boxes.

*Session state → TINY.md. Backend targets → BACKEND-C.md / BACKEND-X64.md.*

---

## Status: Planned (post-M-BOOTSTRAP)

No sprints active. Reference material only.

## Why Icon fits the Byrd Box model

Icon's goal-directed evaluation: expressions suspend and resume like generators.
This maps exactly to α (proceed) / β (resume) / γ (succeed) / ω (fail).
JCON (Townsend + Proebsting, 1999) proved this: Icon → JVM via Byrd Box IR.
See MISC.md §JCON for architecture reference.

## Reference

- JCON source: https://github.com/proebsting/jcon
- JCON paper: https://www2.cs.arizona.edu/icon/jcon/impl.pdf
- Key files to study: `tran/ir.icn` (IR vocab), `tran/irgen.icn` (AST→IR), `tran/gen_bc.icn` (IR→JVM)
