# FINDING — WS-CLASS WIDENING + AGG-PRECISE LANDED; the in-flight-aggregate root window found and closed (s92, 2026-07-17, Claude)

**SCRIP commits: `6a186dd0` (widening) · `41c9b685` (AGG-PRECISE + window fix).** Directive: "Complete RBX topped GC."

## 1. WS-CLASS WIDENING (core.c) — the s38-certified family, flipped by VALUE not by census
40 calls → `rt_ws_strdup_c`/`rt_ws_alloc_c`: the **VARVAL_fn coercion family (19 sites — every DT_I/DT_R snprintf-strdup, DATATYPE names, NAMEVAL strings)**, `_LCASE_`/`_UCASE_`, `_DATE_`'s buf, GETVAR/keyword/FNCEX/ARG/LOCAL/INPUT STRVAL immediates, `scan_subj`. The s38 "75 strdup sites" certification was for the IMMORTAL destination (in-edges irrelevant); for COLLECTABLE the in-edge audit is the work: DESCR STRVAL/NAMEVAL (precise walk marks DT_S and DT_N slen==0), statics (census scan, ws_only honors WSC), stack/ζ (conservative), ws-struct payloads (immortal-WS transitive fixpoint). 255 VARVAL_fn callers grep-proven free of struct/array stores. **NOT flipped, by the churn-value rule:** startup keyword chars, bin_names (pointer-bearing + rt_ws_realloc'd), NV/FNCBLK/DATBLK/DATINST registries, trace/io varnames — permanently live or pointer-bearing; flipping buys mark cost, zero reclaim. **A/B (stash, 300-iter coercion churn, STRESS=3): immortal ws +1/iteration unbounded → CONSTANT 620; window 64B → 28,736B.**

## 2. AGG-PRECISE — VCELL/TBPAIR/TBBLK collectable via TYPED classes
`HB_AGGV/AGGP/AGGT` (206–208), `rt_agg_alloc(kind,n)`; 15 VCELL sites (finding s91 undercounted at 1) + TBPAIR + TBBLK flipped; keys → `_c`. Precise marks: DT_N slen==2 marks vc + vc->key and **honors vc->tbl** (SPITBOL name semantics: a held `T<k>` NAME keeps the OLD table alive across `T` reassignment — manual ch.7); shared `gc_visit_tbblk` marks the TBBLK, every pair, every key, visits key_descr/val/dflt. Pinned-when-marked, never slid (raw cellp/lvalue pointers can't adjust); dead → reclaimed. ws_only conservative filter honors the class range (interior-capable gc_blk_of ⇒ stack-held `&vc->sv` lvalues pin).
**First-cut lesson:** with TBBLK still immortal, the WS-payload fixpoint scanned DEAD tables' buckets and resurrected their pairs (probe: agg=2122 pinned across 100 dead tables). Dead containers must leave the scan set ⇒ TBBLK flipped too ⇒ agg=23 (one live table + in-flight).

## 3. ⚠ THE DEFECT THE SLICE EXPOSED — and its general fix
`203_gc_table_string_keys` (STRESS=25, m4 only) failed NEW: gdb raw bucket dump at the failing read showed **10/15 pairs, one surviving pair's key overwritten by churn bytes** while `gc_visit_tbblk` ran every collect (43 bp hits). Mechanism: collects fire only at `rt_gc_point` sites; the point inside the string path (rt.c:105) lands **mid-statement between `rt_subscript_var`/pair-alloc and linkage**. Flavor-2 conservatively **PINS** the in-flight aggregate block seen on the stack but **never recursed it** — so vc->key and unlinked pairs died despite the pin. Invisible for the immortal lifetime of these cells; the flip exposed it. m3 masked by its root layout.
**FIX (zero codegen):** the typed titles let the existing fixpoint give conservatively-pinned aggregates their PRECISE visit — AGGV marks key, walks tbl backref, visits key_d/sv/cellp; AGGP marks key, visits descrs; AGGT runs gc_visit_tbblk. Any aggregate the stack can see now behaves as if reached through the descr graph; every alloc-to-link window is closed by construction. 203 EXACT again under STRESS=25 m4.

## 4. MEASURED (STRESS=3, telemetry)
100 transient tables × 21 entries, collect #2222: parent **17,697 blocks pinned immortal, window 48B** → s92 **678 pinned, window 1,284,800B**; `agg=24` = exactly one live table + in-flight; agg-dead reclaimed each cycle. String-churn probe unregressed (ws=620 constant).

## 5. Gates — ALL AT WATERMARK (s92 numbers; parallel sessions had improved the s91 line)
crosscheck EXACT m3 305/2 · m4 304/2/1 · DIVERGE=1 (1017_arg_local, identical) · smokes sno 7/7×2 · icon 14/0×2 · prolog 4/1×2 · gc-stress plain 15/15×2, STRESS=25 fail-set exactly pre-existing {204 m3+m4, 212 m4, 214}; retention tier remains the documented O(n²) harness wall. Runtime-only diff ⇒ `.s` regen n/a (s89/s91 precedent).

## Open
- **ARBLK/DATINST** immortal — same typed-class recipe applies (mind ARBLK's separate `a->data` allocation and cellp stability into it).
- rt_ws audit vs TR-5 census (remaining files); window-first re-try; ZH-RETIRE; ruling (C) rc=134; gen-proc consult — unchanged.
