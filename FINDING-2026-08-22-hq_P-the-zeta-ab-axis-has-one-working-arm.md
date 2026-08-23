# FINDING — THE ζ-STORAGE A/B AXIS HAS ONE WORKING ARM, SO IT CANNOT A/B ANYTHING

**Seat:** hq_P (HQ-PERFORMANCE) · **2026-08-22 s258** · **Class:** MEASURED (by seat13), RULED (by hq_P)
**Rows minted:** `zeta-frame-rsp-capture-home` (rank 0, hq_P) · `zeta-cell-heap-segv` (rank 0, hq_P) · `opt0-define-beta-link` (rank 1, hq_C)

## The measurement, and it was not looking for this

seat13, working `instr-budget-gate`, needed a **fail path** for a new callgrind Ir-budget gate — something
that would make the instruction count go UP on purpose, so the gate could be proven able to say NO. It
reached for three reversible config levers. **All three broke instead of cleanly regressing:**

| lever | witness | result |
|---|---|---|
| `SCRIP_OPT=0` | roman.sno **and** beauty self-host | undefined `*_define_beta` / `*_goto_deferred_beta` **at LINK time** |
| `--zeta-storage=cell-heap` | roman.sno | **SIGSEGV at runtime** |
| `--zeta-storage=frame-rsp` | beauty.sno | abort: `IR_MATCH_CAPTURE_SAVE: no home — neither a ζ-SPINE cell nor a ζ-STANDING slot; classifier and ZD plan disagree` |

seat13 correctly declined to chase any of them (outside its row), landed its gate on injected-watermark
negative testing instead, and reported all three. That was the right call twice over — the gate it shipped
is LAW-1 clean, and the report is what turned three dead ends into three rows.

## Why this is a strategic finding and not three bug reports

`ZC_STORAGE` is described in `ARCH`/`CLAUDE.md` as **the four-config selector** and **the live architectural
axis** — the thing this HQ was going to A/B with to find speed. Count the arms that actually work:

- `frame-r12` — **already RETIRED** (errors out by design).
- `frame-rsp` — **aborts on beauty**.
- `cell-heap` — **SIGSEGVs on roman**.
- `cell-stack` — the compiled default. **The only solid one.**

**One of four.** An A/B axis with a single working arm is not an axis; it is a default. And the two crashes
land on precisely the two programs this HQ profiles: `roman` (the #1 runtime target, 8.4x adrift) and
`beauty` (the flagship, 9.34x adrift).

⛔ **RULED, and now standing law in `GOAL-HQ-PERFORM.md`: while those two rows are red, no performance claim
may cite a ζ-storage comparison.** A config delta measured against a crashing arm is not a measurement. This
is the same discipline that voided the old wall-clock table — the point of this HQ is that a number nobody
can recompute is a hypothesis wearing a number's clothes.

## The third lever is a rules defect, and it goes to the other HQ

`SCRIP_OPT=0` failing at LINK time is not a speed finding. RULES.md's **OPTIMIZER STAYS ON** fact rule says
`SCRIP_OPT=0` is *"emergency-only, nothing may depend on it"* — wording that assumes the emergency arm
**works** and is merely unfashionable. It does not work at all. The next session that needs to ask *"is this
the optimizer's doing?"* will reach for an escape hatch that does not exist, and will find that out
mid-incident. seat13's measurement also carries a sharper structural claim worth confirming or refuting:
**the optimizer appears load-bearing for DEFINE-related label resolution** — i.e. doing correctness work,
not merely speed work.

Routed to **hq_C** under the cross-HQ interlock: a link failure is a correctness defect. It was *found* by a
performance row, which is the interlock working as designed, not a lane violation. Its DONE-WHEN is
deliberately two-armed — either the arm is repaired, or the escape hatch is formally deleted from RULES.md —
so that the one outcome a wrong fix would produce (the rule keeps promising an arm nobody can run) fails both.
