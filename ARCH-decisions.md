# ARCH-decisions.md — Design Decisions Log

Append-only. Each entry: date, decision, rationale, consequences, files affected.
Reference these IDs in commit messages: `D-001`, `D-002`, etc.

---

## D-001 — Compatibility Target: SPITBOL, not CSNOBOL4 (2026-03-24)

**Decision:** snobol4x targets **SPITBOL** as its primary compatibility reference,
not CSNOBOL4 2.3.3.

**Rationale:** CSNOBOL4 has a known FENCE semantic difference that makes it unsuitable
as the full compatibility target. SPITBOL is the production-grade, industrial-strength
SNOBOL4 implementation — it defines the language extensions, switches, and HOST()
behaviour that real programs depend on. CSNOBOL4 remains useful only as a monitor
participant and for isolated oracle checks.

**What this means in practice:**
- All SPITBOL language extensions are supported (HOST, LOAD, OPSYN, CLEAR, indirect
  function calls, extended arithmetic, etc.)
- Command-line switches match SPITBOL identically (`-b`, `-f`, `-P`, `-I`, etc.)
- `HOST()` function semantics match SPITBOL
- Runtime error messages match SPITBOL conventions
- CSNOBOL4 may still be used as an oracle participant in the monitor but is no longer
  authoritative when it diverges from SPITBOL

**Exception — datatype names (see D-002).**

**Files updated:** ARCH.md, MONITOR.md, PLAN.md, this file.

---

## D-002 — Datatype Names: UPPERCASE always (2026-03-24)

**Decision:** `DATATYPE()` always returns UPPERCASE names: `STRING`, `INTEGER`, `REAL`,
`PATTERN`, `CODE`, `ARRAY`, `TABLE`, `NAME`. No lowercase. Ever.

**Rationale:** SPITBOL returns lowercase (`pattern`, `string`, etc.). CSNOBOL4 returns
uppercase. We keep uppercase because:
1. The traditional SNOBOL4 spec uses uppercase datatype names.
2. `PATTERN` and `CODE` are canonical and widely documented in uppercase.
3. The beauty subsystem tests (and much SNOBOL4 literature) use uppercase.
4. Changing to lowercase would break existing SNOBOL4 programs that test `DATATYPE(x) = 'PATTERN'`.

**Monitor handling:** DATATYPE() return values are an **ignore-point** — differences
between snobol4x (uppercase) and SPITBOL (lowercase) are silently normalised.
See `tracepoints.conf` IGNORE rule `DATATYPE(*) [a-z]+|[A-Z]+`.

**Test suite:** All tests that check DATATYPE output are **case-insensitive** — they
pass regardless of case returned. See D-003.

**Files updated:** `src/runtime/snobol4/snobol4.c`, `test/` ref files, MONITOR.md tracepoints.conf.

---

## D-003 — Test Suite Case-Insensitivity for DATATYPE (2026-03-24)

**Decision:** All test `.ref` files and driver comparisons that involve `DATATYPE()`
output use **case-insensitive matching**. The test harness normalises DATATYPE strings
to uppercase before comparing.

**Rationale:** Follows from D-001 and D-002. When running the monitor with SPITBOL as
reference, SPITBOL emits lowercase datatype names. Rather than fork ref files for each
participant, we normalise once at comparison time. This also future-proofs tests against
any backend that happens to return lowercase.

**Implementation:** `run_beauty_subsystem.sh` and the monitor's `normalize_trace.py`
uppercase all `DATATYPE(...)` values before diff. Individual driver `.ref` files use
uppercase (our canonical form).

**Files updated:** `test/monitor/normalize_trace.py`, `test/beauty/run_beauty_subsystem.sh`.

---

## D-004 — .NAME Semantics: snobol4x Third Dialect (2026-03-24)

**Decision:** The `.NAME` (unary dot, name-of) operator has three known dialects.
snobol4x implements a **third kind** — distinct from both CSNOBOL4 and SPITBOL.

**Background — the three dialects:**

| Dialect | `.NAME` inside fn body | DIFFER(.NAME,'NAME') | IDENT(.NAME,'NAME') |
|---------|------------------------|----------------------|---------------------|
| CSNOBOL4 | Returns DT_S string `"NAME"` | Fails (identical strings) | Succeeds |
| SPITBOL  | Returns DT_S string `"name"` (lowercase) | Succeeds (differs) | Fails |
| **snobol4x** | Returns DT_N (name-type) with ptr to `"NAME"` | Succeeds (DT_N ≠ DT_S) | Fails |

**snobol4x behaviour:** `.NAME` emits a `DT_N` descriptor (type=9) pointing to the
name label. When passed to `IDENT`/`DIFFER`, `ident()` compares types first:
`DT_N ≠ DT_S → not identical → DIFFER succeeds, IDENT fails`. This matches SPITBOL's
observable behaviour (IsSpitbol passes, IsSnobol4 fails) even though the internal
representation differs.

**Why a third kind and not just "match SPITBOL":**
- The DT_N representation is structurally correct and consistent with the rest of
  the type system.
- It is observable only in edge cases (passing `.NAME` to IDENT/DIFFER directly).
- Programs that use `.NAME` for its intended purpose (indirect assignment, OPSYN, etc.)
  are unaffected.
- Changing to DT_S would require special-casing the emitter in ways that obscure the
  type semantics.

**Monitor handling:** `.NAME` value comparisons are an **ignore-point** when the
difference is CSNOBOL4 DT_S vs snobol4x DT_N. SPITBOL and snobol4x agree on
observable behaviour (DIFFER passes, IDENT fails), so the monitor's consensus rule
treats this as a known non-divergence.

**is.sno strategy:** The `is` driver tests the XOR property (exactly one of
IsSnobol4/IsSpitbol succeeds) rather than WHICH one. This is robust across all
three dialects.

**Files updated:** `src/backend/x64/emit_byrd_asm.c` (E_NAM DT_N emission preserved),
ARCH.md §Dialect Notes, this file.

---

## D-005 — Monitor Oracle: SPITBOL primary, CSNOBOL4 secondary (2026-03-24)

**Decision:** The 3-way monitor uses **SPITBOL as participant 0 (primary oracle)**
for consensus decisions. CSNOBOL4 remains a participant but is no longer authoritative
when it disagrees with SPITBOL.

**Previous state:** CSNOBOL4 was participant 0 (primary oracle). snobol4x targeted
CSNOBOL4 semantics.

**New consensus rules:**
- SPITBOL and snobol4x agree, CSNOBOL4 diverges → known CSNOBOL4 quirk; not our bug.
- SPITBOL and CSNOBOL4 agree, snobol4x diverges → our bug; fix snobol4x.
- SPITBOL and CSNOBOL4 disagree, snobol4x matches SPITBOL → correct; log CSNOBOL4 divergence.
- SPITBOL and CSNOBOL4 disagree, snobol4x matches neither → our bug; fix to match SPITBOL.
- DATATYPE case differences → ignore-point (D-002, D-003).
- .NAME type differences → ignore-point (D-004).

**Files updated:** MONITOR.md §Consensus Rules, `test/monitor/run_monitor_3way.sh`
(swap participant 0 from csn to spl), PLAN.md NOW table.

---

*DECISIONS.md = append-only L3 reference. No session state. No sprint content.*
*New decisions append below the last entry. Never edit existing entries.*
