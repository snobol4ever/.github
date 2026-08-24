# FINDING — the Icon rung board's 14 crash-class failures are ZERO new defects: they decompose exactly into RTX-29 (table-int-subscript, blocked pending ruling) and the suspend/no-activation-frame class (icon-n2, FREE)

**Seat:** seat09 · **Session:** s272(cont) · **Date:** 2026-08-24 · **Row:** `icon-regression-232-to-169`, DONE-WHEN item (b)
**Tree:** SCRIP HEAD at time of triage `97fbaf30` (post `e8fc3bdc`/`f5dd74af`), corpus HEAD unchanged this session, RT_OPT `-O0`, `make pristine` before every arm.

## Context

hq_C's `FINDING-2026-08-24-hq_C-icon-232-to-169-is-two-instruments-not-one-regression.md` (same day) resolved the headline "232→169 regression" as an instrument mismatch and cured the dominant `rc=1` wall (SCRIP `e8fc3bdc`, +74 programs). What survived is the crash class: **13 SIGSEGV + 1 SIGABRT**, named there as "the highest-value programs on the Icon board" and left for triage. This FINDING is that triage.

## Method

1. Fresh `make pristine`, ran `test_icon_rung_suite.sh` in both `--mode compile` and `--mode interp` to get the current crash-name list (mode divergence noted below — not investigated further, out of scope for this row).
2. For each crashing program, checked source for `table(`/`suspend`/`create`/`@` occurrences as a cheap first-pass hint — **this hint turned out to be unreliable and is not the classification basis; see the correction below.**
3. Built a **throwaway diagnostic probe**: in a scratch worktree off current HEAD, applied the exact stand-down pattern RTX-26 already carries in production (`jmp .Lsub_bail` as the first instruction after `.Lsub_table_int:` in `src/runtime/rtx/rtx_icnsub.S`), mirroring the mitigation `audit-rtx29-icon-table-int-chain-walk-post-s262` is already holding pending a Lon/HQ ruling. **Not landed, not committed — probe only**, exactly analogous to a same-tree control arm: it answers "does this specific defect explain this specific crash," nothing more.
4. Ran the full crash-name list against the probe binary and recorded before/after exit codes. A crash that **stops** under the probe is attributable to RTX-29; a crash that **survives** is not.

⭐ **The static grep hint was wrong on at least one witness** (`rung36_jcon_genqueen`: 0 `table(` occurrences, 2 `suspend`/`create`/`@` occurrences — looked suspend-shaped) **and the probe overruled it** (crash cured by the RTX-29 stand-down, so it is table-class, not suspend-class, despite never calling `table()` by that literal token — it likely reaches a table via a builtin or an implicit structure). Only the empirical probe result is trustworthy; the grep was triage-routing only, never the verdict.

## Result: 14 crash instances, 2 root causes, 0 new defects

| program | mode(s) seen crashing | probe verdict | root cause |
|---|---|---|---|
| `rung36_jcon_table` | compile, interp | **cured (rc→0)** | RTX-29 |
| `rung36_jcon_random` | compile, interp | **cured (rc→0)** | RTX-29 |
| `rung36_jcon_fncs1` | compile, interp | **cured (rc→1)** | RTX-29 |
| `rung36_jcon_mindfa` | compile, interp | **cured (rc→1)** | RTX-29 |
| `rung36_jcon_recogn` | compile, interp | **cured (rc→1)** | RTX-29 |
| `rung36_jcon_genqueen` | compile only | **cured (rc→1)** | RTX-29 |
| `rung03_suspend_gen` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) |
| `rung03_suspend_gen_compose` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) |
| `rung03_suspend_gen_filter` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) |
| `rung03_suspend_return` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) |
| `rung36_jcon_cxprimes` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) |
| `rung36_jcon_scan2` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) |
| `rung37_subscript_genproc` | compile, interp | unaffected (139) | suspend/no-frame (icon-n2) — source's own header comment names this exact mechanism ("ICN-IDX-GEN-ENTRY", "the tgrlink class") |
| `rung36_jcon_var` | interp only (SIGABRT, rc=134) | unaffected (134, still aborts) | suspend/no-frame (icon-n2) — 1 `suspend` occurrence; SIGABRT rather than SIGSEGV is very likely the stack-protector (`-fstack-protector-strong` is a build flag) catching the same frame-corruption mechanism before it turns into a wild jump, not a distinct defect |

**6 of 14 → RTX-29. 8 of 14 → the suspend/no-activation-frame class.** Every single crash traces to a defect someone had already found, root-caused, and named before this triage started:

- **RTX-29** — `audit-rtx29-icon-table-int-chain-walk-post-s262` (seat08, live-confirmed, holding claim, **BLOCKED pending Lon/HQ ruling** on whether to apply RTX-26's own stand-down precedent). Do not re-diagnose; do not duplicate. This triage is independent *corroborating* evidence (6 real corpus witnesses on top of seat08's hand-built repro) but changes nothing about that row's own disposition or its explicit "awaiting direction" state.
- **suspend/no-activation-frame** — `icon-n2-generator-activation-frames` (rank 0 in QUEUE order per hq_P's `FINDING-2026-08-24-hq_P-icon-bench-0-of-8-is-one-defect-suspend-procedures-get-no-activation-frame.md`: a procedure containing `suspend` is emitted with no activation frame at all, so frame-relative writes land on the caller's pushed {γ,ω} port pair, and the eventual `ret`/port-jump reads a small integer as a code address). Row is **FREE** (stood down under a fleet-size cap, not cancelled) — its hard prerequisite (ZOPQ operand routing) is already landed (seat13, SCRIP `73f1a3c7`), and hq_P's own four-line witness (`procedure gen(); suspend 1; end`) reproduces the identical signature every one of these 8 programs shows.

## Minor note, not chased here

`rung36_jcon_genqueen` crashes in `--mode compile` (m4) but not `--mode interp` (m3) on this tree; `rung36_jcon_var` is the reverse (SIGABRT in interp, not observed in compile). CLAUDE.md names `m3 ≡ m4 output` a design invariant; this pair is a small, live divergence in *which* programs crash per mode. Both are still members of the two classes above either way (confirmed each against the probe independently), so it does not change this triage's conclusion, but it is worth a name for whoever next audits mode parity.

## What this closes and what it does not

Satisfies `icon-regression-232-to-169` DONE-WHEN (b) — "the 13 SIGSEGV + 1 SIGABRT programs are triaged and either cured or minted as named crash rows" — via **triage + routing to two rows that already exist**, not via minting duplicates and not via curing them in this session. Curing either class is real, separately-scoped work (RTX-29 is blocked on a ruling; icon-n2 is a real activation-frame codegen feature) and is deliberately not attempted here — this row's own DONE-WHEN item (b) asks for triage, not for landing both cures inline.

## Related

- [[FINDING-2026-08-24-hq_C-icon-232-to-169-is-two-instruments-not-one-regression]] — the instrument-split resolution this triage continues.
- [[FINDING-2026-08-24-hq_P-icon-bench-0-of-8-is-one-defect-suspend-procedures-get-no-activation-frame]] — the suspend/no-frame mechanism, root-caused.
- `audit-rtx29-icon-table-int-chain-walk-post-s262` (task baton) — the table-int mechanism, live-confirmed, blocked.
- `icon-n2-generator-activation-frames` (QUEUE rank 0, FREE) — the natural next row for whoever picks up the 8-program half of this board.
