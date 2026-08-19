# FINDING s148 — `&USER_DECLARED_CONSTANTS` lands; two pre-existing defects, one of them in the INSTRUMENT

**Seat:** web (Claude Opus 5), 2026-08-19. **Repos:** SCRIP `d68ec482` · corpus `8c00356b` · `.github` this file.
**Rungs:** CN-4 (runtime, LIVE) · CN-4b (lowering, wired-inert) · CN-5 (seal==2, correct-unreachable).
**Gate:** `scripts/test_gate_udc.sh` — 12/12. **Witnesses:** `corpus/probe/cn/cn_udc_{declare,reopen}.sno` + `cn_udc_closed.err_sno` + `cn_clear_unseal.err_sno`.

---

## ⭐⭐⭐ CN-4 — THE NAMESPACE BECOMES A DECLARATION (live, measured)

CN-2 left the tier-3 `&Name` namespace unconditionally open. That is a silent divergence: the stock oracle answers **error 251 — "keyword operand is not name of defined keyword"** for every undefined `&name` (measured this seat; manual App. D p.278). `&USER_DECLARED_CONSTANTS` turns the extension into something the program *declares*.

- **Tier-2 by construction** — it is the one `&name` that must be answerable *before* the tier-3 arm exists, since it decides whether that arm exists at all.
- **Cell = `kwb_own[7]`**, the free slot in the array Lon's 2026-08-19 grant already covers ⇒ **CN-4 adds NO new global anywhere.**
- **Born 1** = namespace open = pre-CN-4 behaviour verbatim ⇒ default arm byte-identical. Flipping the born value to 0 is its own gated step, exactly as KW-2's default flip is.
- **Closed ⇒ 251 on BOTH read and write.** Gating only the read would let a program create sealed cells it could never read back — the worst of both regimes.
- **Placed ABOVE the tier-3 fallthrough.** Below it, `&USER_DECLARED_CONSTANTS = 0` would be captured as a sealed constant by the very namespace it is closing, and could never be re-opened (341 on the second write).
- **Answered in the unarmed path too**, since the block sits behind `SCRIP_KW_STATIC` (default OFF) while the declaration must be readable in every arm. Both paths store to the same cell.

⛔ **It is not an oracle keyword.** `sbl` 251s `&USER_DECLARED_CONSTANTS` itself, so every program using the feature is ORACLE_FAIL **by construction** and can only ever be `.ref`-pinned, never sbl-diffed. Inherent to a namespace-opening extension.

## ⭐⭐ CN-4b — ONE AUTHORITY, TWO INPUTS (no new global; the grant was DECLINED)

Lon granted "all your choices," which included permission for a new lowering flag. **It was not taken, because the flag was the wrong shape.** The env killswitch `SCRIP_CONST_STATIC` and the program's `&USER_DECLARED_CONSTANTS = 0` are not two facts needing two homes — they are two *inputs* to one fact ("is the declared-constants feature active for this compilation?"). Spelled-twice disease (s68/s70) is one fact with two homes; **one home with two inputs is ONE AUTHORITY done right.** The pre-scan reports the declaration through `sno_const_feature(1)`, which forces the `_cs` static that already existed; `_cs` remains a single function-local static.

Only a **literal 0** counts — a runtime value cannot be evaluated at lower time, and a missed compile-time close costs optimisation, never correctness (the runtime 251 gate still fires). `strcasecmp`, because the runtime read path lower-cases before comparing and the two halves must agree on which statement is the declaration.

## ⛔ CN-5 — CORRECT, AND UNREACHABLE BY ONE LINE

`seal==2` (s142 defer-site entry-cell) needs write-once so that *"once DT_P appears the fn can never change."* `sno_seal_pat` proves that by **inference**; a declared constant carries it **in the language** (CN-2's `is_const` + error 341, enforced at the cell not the spelling, so OPSYN/indirect/FIELD aliasing cannot bypass it). That is the CN-4 thesis applied to `seal`.

**BLOCKER, NAMED SO NO SEAT RE-DERIVES IT:** `src/optimizer/gva_collect.c:10` — `gva_name_eligible()` returns 0 for any `name[0]=='&'`. So `op_gva_k` is permanently −1 at a constant's defer site and `bb_match_defer.cpp:44`'s cell arm (`vslot<0 && dw_cell() && g_gva_active && op_gva_k>=0 && op_seal==2`) can never fire.

⛔ **NOT TAKEN, and not a one-liner in consequence** — admitting `&` to the GVA plane moves every constant into the register-allocation plane and collides with RTCC. Exactly CN-3b's shape of blocker: the missing arm is trivial to write and expensive to *justify*.

## ⛔⭐ THE OPTIMISATIONS ARE STAGED, NOT CASHED — AND A FALSE POSITIVE IS RECORDED

Isolation test (same source, `SCRIP_CONST_STATIC=1` vs `0`): **byte-identical**. CN-4b and CN-5 are wired and consulted but **inert at emit**, confirming s147's finding that every `pat_static` consumer is default-OFF, `PATV$`-gated, or unreached for these shapes. All three `.s` regens reported **zero changed artifacts**, independently.

⚠ **A "CN-4b REACHES emit" reading was produced mid-session and was FALSE** — it came from the extra source statement changing the file, not from `pat_static`. Recorded so the next seat does not trust it. **The isolation A/B (same source, killswitch flipped) is the only sound form; comparing two different sources is not an A/B.**

## ⛔⭐⭐ DEFECT 1 — `CLEAR()` SILENTLY UN-SEALS A CONSTANT (pre-existing CN-2)

Witness `corpus/probe/cn/cn_clear_unseal.err_sno`. `NV_CLEAR_fn` (`core.c:2378`) walks every bucket and nulls `e->val` **without consulting `e->is_const`**:

- `DATATYPE` goes `PATTERN` → `NULL`;
- **error 342 does NOT fire** on the later read, because the *entry* still exists so `NV_EXISTS_fn` stays true — the silent null the CN design says *"would defeat GUARANTEED"*;
- **error 341 then forbids restoring it**: permanently null **and** permanently unwritable.

Not introduced by CN-4/CN-5 and not fixed by them. It is the measured reason **CN-5 retains the `g_sno_fz_unsafe` guard** when stamping `seal==2` — the fz poison is exactly the EVAL/CODE/CLEAR reachability guard, so gating on it makes the cache sound without a second analysis. **CN-5 is correct whether or not this is fixed, and gets strictly better when it is.**

## ⛔⭐⭐⭐ DEFECT 2 — THE MD5 BLAST-RADIUS INSTRUMENT HAS A NOISE FLOOR, AND MOST OF IT IS CORPSES

Every codegen rung in this goal is validated against a corpus md5 sweep. **Measured this seat: 7 of 510 programs differ run-to-run under a FIXED `.so`.** Two distinct classes, and `setarch -R` — the s147 prescription — tames **neither**:

| class | programs | evidence |
|---|---|---|
| **timing** (rc=0, prints `TIME()` deltas) | `demo/calculator-1.sno`, `demo/calculator-2.sno` | 3 `TIME(` refs each; `match_ms=` flips 0↔1 |
| **corpses** (already dead, output varies as they die) | `128_pat_recursive_grammar_right_rec`, `160_pat_alt_inner_gen_resume`, `216_indirect_goto_computed`, `cf_goto_computed`, `null` | rc=139 / 139 / 139 / 132 / 134; **zero** `TIME(` refs |

**A dead program still emits bytes, and unstable bytes masquerade as blast radius.** This is the s33 *"non-empty is not alive"* false-signal class resurfaced **inside the instrument** — the same disease PLAN.md step 1b warns about for the missing oracle, now one level up. s147's "0 differing over 1295" and this seat's own first "508/510" were both measured on this noisy instrument; the numbers were right, the confidence was luck.

⭐ **FIX IS CHEAP AND SHOULD LAND BEFORE THE NEXT CODEGEN RUNG:** record `rc` beside the md5 and compare only `rc==0` programs (or compare rc first, and report an rc change as its own class). Five of the seven vanish immediately; the two timing programs want a `TIME()`-scrub or exclusion.

---

## NEXT SEAT — PICK UP EXACTLY HERE

1. **Instrument first.** Add `rc` to the sweep. Everything below is validated with it.
2. **CN-6 = the CLEAR defect.** Make `NV_CLEAR_fn` skip `is_const` entries, or decide (semantics call) that CLEAR legitimately un-seals and 342 must then fire again — which requires distinguishing "entry exists" from "entry has been assigned", i.e. `NV_EXISTS_fn` is the wrong predicate at `keywords.c:355`.
3. **CN-5 stays parked** until someone prices `&` in the GVA plane against RTCC. Do not admit it casually.
4. **The T2 ruling is still open** and is now cheaper: `&USER_DECLARED_CONSTANTS = 1` can be read as the program electing option (a) for itself, which would retire the language-wide semantics call. Wired but deliberately not assumed.
