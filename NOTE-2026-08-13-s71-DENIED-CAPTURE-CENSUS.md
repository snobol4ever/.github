# NOTE — 2026-08-13 s71 — DENIED-CAPTURE CENSUS (compile-time, 476 programs scanned)

Companion measurement to `FINDING-2026-08-13j`. Purpose: convert "I have one witness" into "here is the
size of the class", so the ruling that finding asks for is made against a number instead of an anecdote.

## METHOD — compile-time only, deliberately

Each program compiled once with `SCRIP_CAP_DIAG=1`; stderr counted. **No program was run.** This is the
s66 discipline: the board's noise floor is ~5 and it flips programs green→red, so a runtime board cannot
size a class this size. A capture is **DENIED** when `sno_cap_fc()` declined to register it, which shows up
as `SAVE … save_active=0` and/or `COND … fc_disp=-1`.

Scan root: `corpus/probe` + `corpus/programs/snobol4` = **476 programs**, of which **201 emit any `[CAP]`
site at all** (the rest carry no captures and are outside the question).

## NUMBERS

| quantity | value |
|---|---|
| programs emitting captures | **201** |
| total `[CAP]` sites | **1966** |
| programs with ≥1 DENIED capture | **69** (34.3% of 201) |
| denied `SAVE` sites (`save_active=0`) | **289** |
| denied `COND` sites (`fc_disp=-1`) | **303** |
| of the 69, ALSO carrying ≥1 `IR_MATCH_DEFER` | **41** |

Heaviest members of the 41 (denied-COND count):

```
 57  programs/snobol4/demo/porter.sno
 29  programs/snobol4/demo/beauty/beauty.sno
 27  programs/snobol4/beauty_suite/omega_driver.sno
 24  programs/snobol4/beauty_suite/XDump_driver.sno
 22  programs/snobol4/beauty_suite/Qize_driver.sno
 22  programs/snobol4/beauty_suite/Qize.sno
 13  programs/snobol4/demo/json.sno
  6  programs/snobol4/demo/calculator-1.sno
```

## ⛔ WHAT IS **NOT** CLAIMED — read this before spending the number

1. **A DENIAL IS NOT AUTOMATICALLY A WRONG ANSWER.** A denied capture falls to the flat `rt_cap` path.
   `FINDING-2026-08-13j`'s witness shows that path binding NULL *when the walk crossed a defer*; whether it
   is also wrong for every other denial cause is **NOT MEASURED**. 69 and 303 are therefore an **upper
   bound on the surface**, not a defect count.
2. **THE 41 ARE CO-OCCURRENCE, NOT CAUSATION.** A program can hold a denied capture for a reason that has
   nothing to do with its defer (an ungranted ALT arm and ARBNO interiors are both known deniers). Nothing
   here attributes a specific denial to a specific defer. **Per-site attribution was not run.**
3. **THE OVERLAP WITH THE WATERMARK'S FAILING SET IS NAMED, NOT ASSERTED.** `porter`, `json`,
   `calculator-1` and `beauty.sno` appear both here and in the m4 failing set the watermark records.
   **Causation NOT measured, NOT asserted** — this is exactly the discipline s70 applied to its own 28-set,
   and the same restraint applies. It is a cheap next probe, not a result.
4. ⛔ **`beauty.sno` CANNOT BE SCORED FROM THIS HARNESS ANYWAY** (s66): the oracle itself dies on it in this
   container (`ERROR 217 duplicate label`, then SIGSEGV), so any PASS/DIFF reasoning about the Milestone-1
   program is void until that is resolved. Its 29 denied CONDs are a **compile-time** fact and stand on
   their own; no runtime verdict is implied.

## THE CHEAPEST NEXT PROBE (for whoever holds the ruling)

Per-site attribution: re-run the census with the walk's bail kind printed beside each declined pair, so the
303 split into *defer-caused* / *ALT-caused* / *ARBNO-caused* / other. That converts an upper bound into a
work queue, and it is a diagnostic print inside `sno_cap_fc`, not a codegen change — byte-inert, gateable
by the existing `DIAG=1 == DIAG=0` md5 check.

---

## ADDENDUM (same session) — THE 41 NARROWED TO 15, AND THE DENIER SET IS NAMED

The 41 above were flagged as **co-occurrence**. They can be narrowed toward attribution **without any
compiler change**, using only the emitted `.s`, because `fc_walk_range`'s whitelist denies on
`default:` — so the deniers present in a program are exactly its **non-admitted kinds**.

Admitted by the walk: `LIT LEN ANY NOTANY POS RPOS ATP ASSIGN_{SAVE,COND,IMM} GOTO`, the `fc_geom` set
`SPAN TAB RTAB BREAK BREAKX BAL REM ARB`, and a **granted** `ALTERNATE`.

**Step 1 — exclude the two other known deniers.** Of the 41, **15** contain **no ARBNO and no ALTERNATE**.

```
probe/bb/probes/D05.sno        probe/dc_nest_bt.sno       probe/mv_valheld_cap.sno
probe/bb/probes/D06.sno        probe/dc_sib_bt.sno        probe/os1_runtime_k.sno
probe/w_cap_ay.sno             probe/w_cap_group.sno      probe/w_cap_novowel.sno
probe/w_cap_stored.sno         probe/mrbp/mrbp_result_value.sno
                               probe/mrbp/mrbp_result_capture.sno   (+3 more)
```

⭐ The two witnesses banked by `FINDING-2026-08-13j` appear in this list on their own merits — a
**self-consistency check on the classifier**, not an input to it.

**Step 2 — enumerate every non-admitted kind actually present across those 15.** Result:

> **`defer` and `value` — nothing else.**

⇒ **THE DENIER SET FOR THESE 15 IS EXACTLY `{IR_MATCH_DEFER, IR_MATCH_VALUE}`.** This is no longer
co-occurrence: within this subset there is no other kind that *can* reach `default:`.

## ⭐ WHAT THIS CHANGES FOR THE RULING

`IR_MATCH_VALUE` is `IR_MATCH_DEFER`'s sibling — same template family (`bb_match_value.cpp` is
structurally `bb_match_defer` with the name-based acquisition replaced by an operand-slot read), and
**both share the property that makes the whitelist fix unsound: no compile-time extent.** Both are also
already in `emit_graph_has_deep_arrival`'s list.

⇒ **Any eligibility answer must cover BOTH kinds, not DEFER alone.** A fix that admits only DEFER would
leave the `value` half of this subset still binding null, and would look green on whichever witness
happened to use `$` rather than a pattern-valued operand.

⛔ STILL NOT CLAIMED: that all 15 produce wrong output. Only the two banked witnesses have been run
against the oracle. The other 13 are a **candidate queue with a named cause**, which is what a work
queue should be — not a defect count.
