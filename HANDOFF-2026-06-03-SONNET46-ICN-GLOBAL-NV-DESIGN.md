# HANDOFF-2026-06-03-SONNET46-ICN-GLOBAL-NV-DESIGN.md

## Session summary

Design + scoping session. No code written. One new goal file created and pushed.

---

## What was accomplished

### Conceptual work — cross-language BB wiring via shared NV dictionary

Extended discussion across the full session on the architecture of cross-language Goal-Directed Evaluation using Byrd Boxes (Proebsting paper reviewed). Key conclusions:

**The four ports are the universal protocol.** Every BB — regardless of which language produced it — exposes the same four ports (α start, β resume, γ succeed, ω fail) and speaks DESCR_t. The language that built a BB is invisible to anything wired to its ports. Direct cross-language BB wiring is already possible with zero extra machinery.

**Variable model audit across all six languages:**
- SNOBOL4 / Snocone / Rebus — pure global NV dictionary already. Locals saved/restored via shadow mechanism.
- Icon — globals currently use integer frame slots (`g_bb_varslot`), locals use frame slots. This is a compiler optimization inherited from icont, NOT a semantic requirement.
- Raku — OUR-scope = package stash (equivalent to NV dict), MY-scope = lexical slots, $* dynamic = shadow walk.
- Prolog — WAM X/Y registers + trail for logic variables. `nb_setval`/`nb_getval` = non-backtrackable globals equivalent to NV. Logic variables stay Prolog-internal; ground values freely cross the NV boundary.

**Key insight:** Icon globals do NOT need frame slots. A dictionary works fine — and is already what every other language uses. Only locals need slots (or a local shadow dict). The slot mechanism was an optimization for icont's integer-index model; in SCRIP it buys nothing and costs cross-language sharing.

**After the rung:** Icon globals join SNOBOL4/Snocone/Rebus in the shared NV namespace. A variable written by an Icon BB can be read by a SNOBOL4 BB with zero dispatch, directly wired through the same `bb_var_global` template.

---

## New goal file created

**`GOAL-ICN-GLOBAL-NV.md`** — committed to `.github` HEAD `a2d0f983`.

Six steps + FENCE:

| Step | What |
|------|------|
| GN-1 | Collect global names into per-graph set at lower time |
| GN-2 | Tag `IR_VAR` nodes: `state=1` for globals, `state=0` for locals |
| GN-3 | New `bb_var_global` template: x86 call to `NV_GET_fn` |
| GN-4 | `IR_ASSIGN` lhs-global routes to `NV_SET_fn` |
| GN-5 | Cross-language probe: Icon sets, SNOBOL4 reads (or v.v.), m2 |
| GN-6 | Full Icon corpus sweep: m2 PASS ≥ 127 |
| GN-FENCE | Grep: no global names appear as `[reg+off]` frame slots |

---

## Baselines (2026-06-03, SCRIP HEAD `85677cb`)

- Build: GREEN (`make -j4 scrip` rc=0)
- `test_icon_all_rungs.sh`: **m2 PASS=127 FAIL=120 XFAIL=36 TOTAL=283** — this is the gate for GN-6
- `test_per_kind_diff.sh`: GONE=1115 (audit tool unlinked in this environment — not a regression, environment limitation; run from a full SCRIP build with audit tool linked)
- `test_smoke_icon.sh`: m2 0/12, m3 0/12, m4 0/12 (GZ-10 work in progress; not the gate for this rung)

---

## Repos state

| Repo | HEAD |
|------|------|
| `.github` | `a2d0f983` |
| `SCRIP` | `85677cb` |
| `corpus` | (unchanged this session) |

---

## Next session entry point

Read `GOAL-ICN-GLOBAL-NV.md`. Run Session Setup. Start at **GN-1**: add `icn_is_global(name)` to the lower context by scanning `TT_GLOBAL` nodes before lowering procedure bodies. Zero behavior change — pure bookkeeping. Gate: build green, `test_icon_all_rungs.sh` m2 still 127 PASS.

The parser already marks global declarations as `TT_GLOBAL` nodes (`icon_parse.c:776`). The lowerer already handles them (`lower.c:914`) as no-ops (`IR_SUCCEED`). GN-1 just needs to intercept those nodes to extract the name list before the no-op path fires.
