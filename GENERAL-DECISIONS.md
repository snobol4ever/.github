# GENERAL-DECISIONS.md — Design Decisions Log

Append-only. Each entry: date, decision, rationale, consequences, files affected.
Reference these IDs in commit messages: `D-001`, `D-002`, etc.

---

## D-001 — Compatibility Target: SPITBOL, not CSNOBOL4 (2026-03-24)

**Decision:** one4all targets **SPITBOL** as its primary compatibility reference,
not CSNOBOL4 2.3.3.

**Rationale:** CSNOBOL4 has a known FENCE semantic difference that makes it unsuitable
as the full compatibility target. SPITBOL is the production-grade, industrial-strength
SNOBOL4 implementation — it defines the language extensions, switches, and HOST()
behaviour that real programs depend on. CSNOBOL4 is SOURCE REFERENCE ONLY (v311.sil / snobol4.c for Silly SNOBOL4). Not installed, not executed as a test oracle. See D-005.

**What this means in practice:**
- All SPITBOL language extensions are supported (HOST, LOAD, OPSYN, CLEAR, indirect
  function calls, extended arithmetic, etc.)
- Command-line switches match SPITBOL identically (`-b`, `-f`, `-P`, `-I`, etc.)
- `HOST()` function semantics match SPITBOL
- Runtime error messages match SPITBOL conventions
- CSNOBOL4 is SOURCE REFERENCE ONLY — see D-005.

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
between one4all (uppercase) and SPITBOL (lowercase) are silently normalised.
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

## D-004 — .NAME Semantics: one4all Third Dialect (2026-03-24)

**Decision:** The `.NAME` (unary dot, name-of) operator has three known dialects.
one4all implements a **third kind** — distinct from both CSNOBOL4 and SPITBOL.

**Background — the three dialects:**

| Dialect | `.NAME` inside fn body | DIFFER(.NAME,'NAME') | IDENT(.NAME,'NAME') |
|---------|------------------------|----------------------|---------------------|
| CSNOBOL4 | Returns DT_S string `"NAME"` | Fails (identical strings) | Succeeds |
| SPITBOL  | Returns DT_S string `"name"` (lowercase) | Succeeds (differs) | Fails |
| **one4all** | Returns DT_N (name-type) with ptr to `"NAME"` | Succeeds (DT_N ≠ DT_S) | Fails |

**one4all behaviour:** `.NAME` emits a `DT_N` descriptor (type=9) pointing to the
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
difference is CSNOBOL4 DT_S vs one4all DT_N. SPITBOL and one4all agree on
observable behaviour (DIFFER passes, IDENT fails), so the monitor's consensus rule
treats this as a known non-divergence.

**is.sno strategy:** The `is` driver tests the XOR property (exactly one of
IsSnobol4/IsSpitbol succeeds) rather than WHICH one. This is robust across all
three dialects.

**Files updated:** `src/backend/x64/emit_byrd_asm.c` (E_NAM DT_N emission preserved),
ARCH.md §Dialect Notes, this file.

---

## D-005 — Oracle: SPITBOL x64 only. CSNOBOL4 = source reference only. (2026-03-24, amended 2026-04-09)

**Decision:** SPITBOL x64 (snobol4ever/x64, `/home/claude/x64/bin/sbl`) is the **sole execution
oracle** for all sessions. There is no secondary oracle. CSNOBOL4 is not built, not run,
not installed as a test tool.

**CSNOBOL4 role:** SOURCE REFERENCE ONLY. The `v311.sil` SIL source and the generated
`snobol4.c` are read as ground-truth C code for the Silly SNOBOL4 session. They are never
executed as an oracle. CSNOBOL4 lacks FENCE — any program using FENCE will produce wrong
answers under CSNOBOL4. A future milestone (M-CSNOBOL4-FENCE) will add FENCE to CSNOBOL4
using SPITBOL as the semantic guide — see PLAN.md component map.

**Consensus rule (2-party: SPITBOL vs one4all):**
- SPITBOL and one4all agree → correct.
- one4all diverges from SPITBOL → our bug; fix one4all.
- DATATYPE case differences → ignore-point (D-002, D-003).
- .NAME type differences → ignore-point (D-004).

**Files updated:** GENERAL-RULES.md, RULES.md, MONITOR.md, TESTING.md, GENERAL-OVERVIEW.md,
PLAN.md (M-CSNOBOL4-FENCE added).

---

*DECISIONS.md = append-only L3 reference. No session state. No sprint content.*
*New decisions append below the last entry. Never edit existing entries.*

---

## D-010 — E_SEQ vs E_CONCAT: juxtaposition is a runtime operation (2026-04-01)

**Status:** Known fragility — deferred refactor post M-DYN-S1.

**The issue:** SNOBOL4 juxtaposition is polymorphic at runtime:
- All operands coerce to string → `stmt_concat` (string concat)
- Any operand is `DT_P` → `pat_cat` (pattern sequence)

The parser cannot determine this at parse/IR-build time. A variable `P` holding
a pattern is syntactically identical to one holding a string.

**Current approach (fragile):**
Parser emits `E_SEQ` for all juxtaposition. Post-parse `fixup_val_tree` renames
`E_SEQ → E_CONCAT` in "known value contexts" (subject field always; replacement
field unless structural pattern markers like `E_CAPT_COND`/`E_ARB` are present).
`emit_x64.c` branches on the tag.

**Why it's fragile:** A variable `P` holding a DT_P value looks like a string variable
at parse time. `'' P ''` in the replacement field gets `E_CONCAT` → `stmt_concat`,
which will fail or produce wrong output if P is a PATTERN at runtime.

**What other frontends do:** Snocone uses `&&` (explicit sequence), Icon uses `||`
(explicit string concat) vs `&` (goal-directed sequence). Only SNOBOL4 has the
ambiguity — it's inherent to the language design.

**Correct fix:** Use `E_SEQ` everywhere for SNOBOL4 juxtaposition. Add a runtime
dispatcher `stmt_seq(DESCR_t left, DESCR_t right)` that checks types at runtime:
```c
if (left.v == DT_P || right.v == DT_P) return pat_cat(left, right);
return CONCAT_fn(left, right);
```
Remove `fixup_val_tree` from the SNOBOL4 frontend. Remove `E_CONCAT` as a distinct
node for SNOBOL4 (keep it for Icon/Snocone where it means explicit string concat).

**Deferred because:** M-DYN-S1 gate work (142/142) is the current priority. This
refactor touches the parser, emitter, and runtime simultaneously. Schedule for
a dedicated sprint after M-DYN-S1 fires.

**Short-term mitigation:** Remove `fixup_val_tree` call on `s->replacement` — that's
the most fragile site. Subject field is generally safe (value context is correct there).
