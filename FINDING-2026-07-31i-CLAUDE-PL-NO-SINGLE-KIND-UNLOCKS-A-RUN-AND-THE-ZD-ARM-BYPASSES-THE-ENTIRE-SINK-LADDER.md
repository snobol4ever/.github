# FINDING 2026-07-31i (s163) — PL: NO SINGLE KIND UNLOCKS A SINGLE RUN, AND THE ZD ARM BYPASSES THE ENTIRE PL-SINK LADDER

**Session:** s163 · **Baseline:** SCRIP `510c38fe` (clean at start) · **Build:** `-O0` throughout (Makefile default; no `-O1`/`-O2` used or sought)
**Lon directive (verbatim):** *"Climb the ladder to NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. Continue."*

---

## HEADLINE

Two measurements, each of which kills a queued rung *before* it was spent:

1. ⭐⭐ **NO SINGLE IR KIND UNLOCKS A SINGLE ZD RUN.** The minimum viable admission is a **PAIR**. The queued `NEXT (b)` — *"ZD-PL-1 `IR_VAR_REF` (41%)"* — would have written a template ZD arm, passed every gate, and moved the armed count by **exactly zero**.
2. ⭐⭐ **THE REAL BLOCKER IS NOT ADMISSION — IT IS THAT THE ZD ARM EARLY-RETURNS PAST THE ENTIRE PL-SINK LADDER.** Admitting `IR_CALL_BUILTIN_PROLOG` (which gates **100%** of runs, so nothing unlocks without it) routes every `$unify` / `$unify_lst` / `$trail_mark` / `$ix_g` through generic `rt_call_arr` by-name dispatch, discarding PL-SINK-1/2/4/8 and PL-REGAIN-5 — **and every correctness gate stays green**, because `rt_call_arr` is correct, only slow.

---

## (1) THE INSTRUMENT WAS WRONG: NODE FREQUENCY CANNOT RANK AN ALL-OR-NOTHING GATE

s162 ranked the gap by **node frequency** and named `IR_VAR_REF` the elephant (4168 nodes, 41%). But `zd_plan` is **all-or-nothing per run**: a run arms iff *every* node in it passes `zd_wl_kind`. The quantity that decides a rung is therefore **RUN-GATING** — in how many runs does this kind appear at all — not how many nodes it contributes.

Census re-run this session over the 185-program rung corpus (`corpus/programs/prolog/rung*.pl`), grouping each declined run's **full blocking SET** rather than its first blocker:

| Kind | Runs it blocks | % |
|---|---|---|
| `IR_CALL_BUILTIN_PROLOG` | **185** | **100%** |
| `IR_MOVE_LABEL` | 157 | 85% |
| `IR_VAR_REF` | 130 | 70% |
| `IR_VAR` | 93 | 50% |
| `IR_CALL_PROC_STAGED` | 91 | 49% |

**185 programs → 185 declined runs, exactly one per program.** Confirms gate A independently: only `main` reaches the run loop; every predicate graph early-returns on `flat_jmp_entry` before it.

### THE UNLOCK TABLE (a run unlocks iff its ENTIRE blocking set is armed)

```
  arm {IR_CALL_BUILTIN_PROLOG} alone ->   0 runs
  arm {IR_MOVE_LABEL}          alone ->   0 runs
  arm {IR_VAR_REF}             alone ->   0 runs     <- the queued NEXT (b)
  arm {IR_VAR}                 alone ->   0 runs
  arm {IR_CALL_PROC_STAGED}    alone ->   0 runs

  best 2-kind set ->  29/185 : CALL_BUILTIN_PROLOG + MOVE_LABEL
  best 3-kind set ->  55/185 : CALL_BUILTIN_PROLOG + MOVE_LABEL + CALL_PROC_STAGED
  best 4-kind set ->  94/185 : CALL_BUILTIN_PROLOG + MOVE_LABEL + VAR_REF + VAR
  best 5-kind set -> 185/185 : all five
```

⭐ **The whole `main` population of the language is FIVE kinds.** And `IR_CALL_BUILTIN_PROLOG` is in **every** blocking set, so **no admission sequence that omits it unlocks anything.** This is the ZD-2d/2e "armed as a PAIR deliberately" law generalized: it is not a quirk of COERCE/CMP, it is the **structural consequence of all-or-nothing runs**, and it must be measured with a set census before any admission rung is planned.

---

## (2) ⭐⭐ THE ZD ARM IS A DISPATCH ROUTE WHERE IT SHOULD BE A STORAGE FLAVOR

`IR_CALL_BUILTIN_PROLOG` with a known builtin classifies to `CALL_ROUTE_FN` (`emit.cpp:745`), which dispatches to `bb_call_fn_str` (`bb_call.cpp:530`). Control flow inside that function, **measured by line number, not asserted from reading**:

```
457  std::string bb_call_fn_str(...)
466      if (_.op_zres) {              <- ZD arm begins; keys on op_zres ONLY, kind-agnostic
498          return s;                 <- ZD ARM EARLY-RETURNS
507      void * dfp = dop_direct_fp(fn, nargs, &dsym);   <- sink/dop dispatch gate
553          sink_unify2_str(...)      <- PL-SINK-1  (1.86x)
555          sink_unify_lst_str(...)   <- PL-SINK-2
557          sink_trail_mark_str(...)  <- PL-SINK-8
559          sink_ix_g_str(...)        <- PL-SINK-4  (97.1% leaf elimination)
```

**The ZD arm returns at 498. The entire PL-SINK ladder lives at 507–559. An armed call can never reach it.** It unconditionally emits the generic `rt_call_arr(fn, args, nargs)` by-name path — the same string-dispatch walk PL-SPEED-1 killed for a measured ~2.5–3× wall.

### SIZED, NOT ASSERTED

Emitted `corpus/benchmarks/prolog/bench/nrev.pl` (`--compile --target=x86`, `-O0`):

| Symbol class in emitted `.s` | count |
|---|---|
| `call rt_pl_dop_*` (direct/sink data plane) | **65** |
| `rt_call_arr` (generic by-name) | **2** |

Top targets: `rt_pl_dop_unify` ×15, `rt_pl_dop_ix_g` ×10, `rt_pl_dop_trail_unwind` ×8, `rt_pl_dop_trail_mark` ×8.

**~97% of the Prolog data plane rides the path the ZD arm skips.** Arming `IR_CALL_BUILTIN_PROLOG` as `zd_wl_kind` is currently written would invert that ratio on every armed run — a **silently-green performance regression**, the worst class, since `rt_call_arr` is semantically correct and the rung suite would stay 164/164.

### ⭐ WHY SNOBOL4 NEVER HIT THIS, AND WHY IT IS PROLOG'S OPENING MOVE

ZD-7 admitted bare `IR_CALL` for SNOBOL4 and the conflation cost nothing, because **SNOBOL4's call family has no sink ladder** — `rt_call_arr` *is* its dispatch. Prolog spent s142–s148 building exactly such a ladder underneath `dop_direct_fp`. So the ZD arm's "ZD ⇒ take my own route" shortcut is free in SNOBOL4 and expensive in Prolog. This is the **third** independent confirmation of the s162 thesis that the SN4 ladder does not transfer: the first was the jmp-entry gate, the second was `zd_stub_ok()` moving Prolog by zero, this is the third — and unlike those two it is a **defect in shared code**, not merely a mismatch of order.

**THE DESIGN CORRECTION:** *ZD is a STORAGE discipline, not a DISPATCH route.* The sink/dop selection must stay; only **where operands are read from** (`ZOPQ(i,·)` vs `FRQ(argbase+i*16)`) and **where the result is written** (`ZRES(·)` vs `FRQ(resoff)`) may change. This is the template rules' own **"ONE MEDIUM, INVISIBLE"** principle applied to storage instead of medium: one dispatch, the storage switched invisibly inside — never a second parallel path that duplicates the decision and silently drops half of it.

---

## (3) SEQUENCING: THE QUEUED ORDER IS UNFALSIFIABLE, AND INVERTS

Queued `NEXT (a)` was the protocol rung (the 94% of graphs) first. **With the kind whitelist still declining at node 0, armed stays 0 whether the protocol rung succeeds or fails** — it cannot be told apart from a no-op. Landing it first is unfalsifiable by construction, the same shape this file keeps catching after the fact.

But the kinds cannot land first either, because the head kind (`IR_CALL_BUILTIN_PROLOG`, 100%) hits the sink bypass above. So the real head rung is neither of the queued two:

| Rung | Content | Falsifiable by |
|---|---|---|
| ⭐⭐ **ZD-PL-A** (NEW HEAD) | Refactor `bb_call_fn_str`: make the ZD arm a **storage flavor** of the existing sink/dop dispatch, not an early-return route. | SNOBOL4's existing ZD-7 `IR_CALL` arm must stay **byte-identical** (it is the positive control, already armed and measured). |
| **ZD-PL-B** | Admit the pair `{IR_CALL_BUILTIN_PROLOG, IR_MOVE_LABEL}` → **29/185 runs**. `IR_MOVE_LABEL` dispatches to ONE template unconditionally (`emit.cpp:1017`) and needs its own ZD arm first. | armed nodes 0 → >0, `nrev` dop-site count unchanged. |
| **ZD-PL-C** | `+ {IR_VAR, IR_VAR_REF}` → 94/185; `+ IR_CALL_PROC_STAGED` → 185/185. | unlock table above, per step. |
| **ZD-PL-0** | The protocol rung (the 94% of *graphs*), now with a live armed population to measure against. | predicate graphs join the armed count. |

⚠ `IR_VAR_REF` (`emit.cpp:889`) dispatches to ONE template (`bb_var_ref`) unconditionally — its branch is over operand ADDRESSING (global vs `bb_varslot_peek`), not over template — so it is structurally clean to admit; it just must not go **first**, and never alone.

---

## (4) LANDED THIS SESSION — cursor item (d), `bb_op_name` holes

`kind_names[]` is a designated-initializer table; **8 kinds had no entry and returned NULL**: `IR_CALL_BUILTIN_PROLOG`, `IR_CUT`, `IR_REF_INVARIANT`, `IR_PATTERN_CAT`, `IR_PATTERN_ALT`, `IR_PATTERN_CAPTURE`, `IR_PATTERN_DEFER`, `IR_DTP_ASSIGN`. Every Prolog first-blocker histogram ever read printed its top entry as `(null)` / `<unnamed>`.

Fixed **both ways** so the class cannot recur: the 8 entries added, **and** `bb_op_name` made total (`&& kind_names[k]` → `"IR_UNKNOWN"`), so a future kind added to the enum without a table entry degrades to a readable token instead of a NULL deref in a caller that does not check. Diff: `src/contracts/scrip_ir.c`, +9/-1. Diagnostic only — zero behavioural change.

---

## GATES (all `-O0`)

- Prolog rung suite: **interp PASS=164 FAIL=0** · **compile PASS=164 FAIL=0** — exactly the s161/s162 baseline.
- `test_gate_emit_no_lang.sh` → **OK** (LANG-BLIND).
- `test_gate_pl_no_new_global.sh` → **PASS**, doomed-ratchet **14 / floor 14**.
- `git diff --stat` = 1 file, +9/-1 (diagnostic table only). No admission edit, no template edit, no probe left in the tree.

## METHODOLOGY NOTE (carried forward from s162's device-full lesson)

The census filters **at the source** (`grep '^\[ZD-GAP\]'` inside the per-program pipe, never a raw stderr append). 185 programs produced a 185-line result file. Script kept at `/home/claude/zd_census.sh` — it is a measurement harness, not shipped code.

## ⚠ SCOPE / HONESTY

- The unlock table is measured on the **185-program rung corpus** (100% compile). s162's figures were over a different 250-program set with a 185/250 compile-failure rate; the two are **not** the same denominator and should not be compared digit-to-digit. What reproduces exactly is the **structure**: armed = 0, one run per program, predicates declined before the run loop.
- The sink-bypass regression is **structural + sized, not yet A/B-measured in wall time** — measuring it requires admitting the kind, which needs ZD-PL-A first. No perf claim is made beyond the emitted-symbol census (65 vs 2).
- Nothing about push state is claimed here. `scripts/handoff_status.sh`, run live, is the only ground truth.
