# SNOBOL4-plus — Directory

> **New Claude session? Read this file first. Then jump directly to what you need.**
> Everything lives in `PLAN.md`. This file tells you where.

---

## 1. Session Start (every session, in order)

| What | Where |
|------|-------|
| Clone all six repos | `PLAN.md` § Session Start — Clone All Repos |
| Build CSNOBOL4 + SPITBOL oracles | `PLAN.md` § Session Start — Build Oracles |
| Git identity + token decode | `PLAN.md` § Git Identity |
| Current work — what's next | `PLAN.md` § Outstanding Items (P1/P2/P3) |

---

## 2. What This Org Is

| What | Where |
|------|-------|
| Mission + people | `PLAN.md` § What This Organization Is |
| All repos at a glance | `PLAN.md` § Repository Index |
| Setup history | `PLAN.md` § Organization Setup Log |

---

## 3. Per-Repo Plans (read the one you're working in)

| Repo | Where |
|------|-------|
| **SNOBOL4-jvm** — Clojure, full SNOBOL4→JVM | `PLAN.md` § SNOBOL4-jvm — Full Plan |
| **SNOBOL4-dotnet** — C#, full SNOBOL4→MSIL | `PLAN.md` § SNOBOL4-dotnet — Full Plan |
| **SNOBOL4-tiny** — native compiler, Byrd Box | `PLAN.md` § SNOBOL4-tiny — Full Plan |
| **Snocone** — C-like sugar front-end (both targets) | `PLAN.md` § Snocone Front-End Plan |
| **SNOBOL4-python** — pattern library, PyPI | `PLAN.md` § SNOBOL4-python — Plan |
| **SNOBOL4-csharp** — pattern library, C# | `PLAN.md` § SNOBOL4-csharp — Plan |
| **SNOBOL4-corpus** — shared programs + benchmarks | `PLAN.md` § SNOBOL4-corpus — Plan |

---

## 4. Protocols (reference when needed)

| What | Where |
|------|-------|
| Commit + push every change | `PLAN.md` § Standing Instruction — Small Increments |
| Save state mid-session | `PLAN.md` § Directive: SNAPSHOT |
| End of session cleanly | `PLAN.md` § Directive: HANDOFF |
| Something broke, exit fast | `PLAN.md` § Directive: EMERGENCY HANDOFF |
| How to declare a snapshot | `PLAN.md` § Snapshot Protocol |
| How to write a handoff prompt | `PLAN.md` § Handoff Protocol |

---

## 5. Key Design References

| What | Where |
|------|-------|
| Byrd Box α/β/γ/ω model | `SNOBOL4-tiny/doc/DESIGN.md` |
| Bootstrap strategy (seed→self-hosting) | `SNOBOL4-tiny/doc/BOOTSTRAP.md` |
| Architecture decisions (resolved) | `SNOBOL4-tiny/doc/DECISIONS.md` |
| Snocone semantic rules + label gen | `PLAN.md` § Key Semantic Rules (from Koenig spec) |
| JVM design decisions (immutable) | `PLAN.md` § Design Decisions (Immutable) — SNOBOL4-jvm |
| JVM tradeoff prompt (read before every JVM decision) | `PLAN.md` § Tradeoff Prompt — SNOBOL4-jvm |
| Dotnet token type reference | `PLAN.md` § Token.Type Reference — SNOBOL4-dotnet |

---

## 6. Current Baselines (update at every handoff)

| Repo | Tests | Last commit |
|------|-------|-------------|
| SNOBOL4-dotnet | 1,607 / 0 | `63bd297` |
| SNOBOL4-jvm | 1,896 / 4,120 assertions / 0 | `9cf0af3` |
| SNOBOL4-tiny | Sprint 0–1 done, Sprint 2 next | `74c66f7` |

---

## 7. What To Do Next (update at every handoff)

**SNOBOL4-tiny**: Sprint 2 — CAT node.
Write `test/sprint2/cat_pos_lit_rpos.c` by hand, confirm compile+run,
then drive from `emit_c.py` and diff. First auto-generated test.

**SNOBOL4-jvm / dotnet**: Snocone Step 3 — `if/else` → label/goto pairs (both targets).

**Org**: Jeffrey needs to accept GitHub org invitation → promote to Owner.
