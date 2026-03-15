# FRONTEND-PROLOG.md — Tiny-Prolog Frontend (L3)

Tiny-Prolog is a planned frontend for SNOBOL4-tiny only.
Prolog unification maps to the Byrd Box model: the four ports α/β/γ/ω
correspond to proceed/recede/succeed/fail in Prolog's SLD resolution.

*Session state → TINY.md.*

---

## Status: Planned (post-M-BOOTSTRAP)

No sprints active. Reference material only.

## Why Prolog fits the Byrd Box model

Prolog's execution: try a clause (α), on failure try next clause (β),
on success return binding (γ), on total failure propagate up (ω).
The four-port model describes SLD resolution exactly.
Byrd himself developed the box model for Prolog debugging — SNOBOL4ever
uses the same model for SNOBOL4 patterns. The symmetry is intentional.
