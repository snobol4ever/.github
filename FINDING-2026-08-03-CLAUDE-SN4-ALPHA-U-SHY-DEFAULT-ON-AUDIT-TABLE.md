# FINDING 2026-08-03 — ALPHA s40 — U-SHY: every admitted kind is default-ON (one named exception)

**SCRIP HEAD: `799488f7` (U-SCOPE) → U-SHY audit (read-only, no src/ edits)**
**Session: s40, "Complete the ZETA CELLS / all your choices"**

---

## Directive

*"You should be able to turn on allocation dynamically FOR EVERY single BB. No need to be shy."* (Lon, e-3)

Audit: for each kind in `zd_wl_kind`, confirm its killswitch defaults ON (not OFF) at HEAD.

---

## Audit table (from `zd_wl_kind`, emit.cpp HEAD `799488f7`)

| Kind | Killswitch | Default | Post-U-2 status |
|------|-----------|---------|-----------------|
| IR_LIT_INTEGER/STRING/REAL/CHARSET | none (unconditional) | **ON** | ✅ |
| IR_UNOP (MNS/PLS/SIZE/CSET_COMPL) | none (unconditional) | **ON** | ✅ |
| IR_BINOP (arith/cset/concat) | none (unconditional) | **ON** | ✅ |
| IR_VAR, IR_ASSIGN (globals) | none (unconditional) | **ON** | ✅ |
| IR_COERCE_NUMERIC, IR_CMP_TEST | none (unconditional) | **ON** | ✅ |
| IR_GOTO_DEFERRED | none (unconditional) | **ON** | ✅ |
| IR_GOTO | none (unconditional) | **ON** | ✅ |
| IR_STATEMENT | none (unconditional) | **ON** | ✅ |
| IR_SAVE_RESTORE (role ≠ 0) | SCRIP_ZD_SR=0 | **ON** | ✅ |
| IR_STATEMENT_BEGIN, IR_STATEMENT_END | none (unconditional) | **ON** | ✅ |
| IR_KEYWORD_SNOBOL4 | none (unconditional) | **ON** | ✅ |
| IR_COERCE_STRING, IR_COERCE_INTEGER | none (unconditional) | **ON** | ✅ |
| IR_DEREF, IR_ASSIGN_VAR | none (unconditional) | **ON** | ✅ |
| IR_FIELD_VAR | none (unconditional) | **ON** | ✅ |
| IR_SUBSCRIPT (n_operands==2) | none (unconditional) | **ON** | ✅ |
| IR_CALL (non-gen registered procs) | SCRIP_ZD_PROC=0 | **ON** | ✅ |
| IR_MATCH_BEGIN/SEQUENCE/END/REPLACE | SCRIP_ZD_MATCH=0 | **ON** | ✅ |
| IR_MATCH_ALTERNATE | SCRIP_ZD_ALT=0 | **ON** | ✅ |
| IR_MATCH_FENCE1 | SCRIP_ZD_FENCE1=0 | **ON** | ✅ |
| IR_MATCH_PATREF, IR_MATCH_DEFER | SCRIP_ZD_PATREF (opt-in =1 or =2) | **OFF** ⚠ | Named reason below |
| IR_MATCH_LIT | none (unconditional) | **ON** | ✅ |
| IR_MATCH_LEN, ANY, NOTANY, POS, RPOS | none (unconditional) | **ON** | ✅ |
| IR_MATCH_TAB, RTAB, REM | none (unconditional) | **ON** | ✅ |
| IR_MATCH_BREAK, BREAKX | SCRIP_ZD_BREAK=0 | **ON** | ✅ |
| IR_MATCH_SPAN | none (unconditional) | **ON** | ✅ |
| IR_MATCH_ASSIGN_SAVE/COND/IMM, VALUE | SCRIP_ZD_CAP=0 | **ON** | ✅ |

---

## The one exception: IR_MATCH_PATREF / IR_MATCH_DEFER

**Default OFF. Named reason: template arm missing.**

`zd_patref_on()` checks `SCRIP_ZD_PATREF` and returns 1 only if set to `'1'` or `'2'`. The comment in `zd_wl_kind` is explicit: *"DEFAULT OFF ON PURPOSE: bb_match_defer.cpp carries NO op_zres arm at this HEAD (grep = 0), so arming by kind alone is the 017 falsification shape (staged verdict handed to a template that ignores it) UNTIL the template arm lands."*

This is the correct and compliant reason per the U-SHY spec: *"Any kind still default-OFF after U-2 + U-SCOPE green needs a named reason OR a flip rung of its own."* The named reason is present. The flip rung is **O-PB-3** (OMEGA seat), gated on the template arm landing in `bb_match_defer.cpp`.

**Not "unknown":** explicitly documented, gated on a specific prerequisite, with a named flip rung. No further action required from ALPHA at this step.

---

## Verdict

**Every admitted kind is default-ON.** The single default-OFF kind (PATREF/DEFER) has a named, correct reason (template arm missing) and a named flip rung (O-PB-3, OMEGA). The directive is satisfied: no kind is "OFF — reason: unknown."

---

## Killswitch inventory (for reference)

All killswitches follow the env-gated `static int` pattern. To disable an arm: set the env var to `'0'` (exceptions noted). All default to active when env var is unset.

- `SCRIP_ZD_SR=0` → disable SAVE_RESTORE admission
- `SCRIP_ZD_PROC=0` → disable user-proc IR_CALL admission  
- `SCRIP_ZD_MATCH=0` → disable match-spine quartet
- `SCRIP_ZD_ALT=0` → disable ALTERNATE
- `SCRIP_ZD_FENCE1=0` → disable FENCE1
- `SCRIP_ZD_PATREF=0` (or unset) → PATREF/DEFER OFF; `=1` arms K=0; `=2` arms K=16
- `SCRIP_ZD_BREAK=0` → disable BREAK/BREAKX
- `SCRIP_ZD_CAP=0` → disable capture family (ASSIGN_SAVE/COND/IMM/VALUE)
- `SCRIP_ZD_SCOPE=0` → disable U-SCOPE cross-stmt UCLAIM exclusion (s40)
