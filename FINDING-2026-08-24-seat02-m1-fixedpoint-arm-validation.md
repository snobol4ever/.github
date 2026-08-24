# FINDING — m1-fixedpoint-arm-validation: bogus ARM argument now correctly rejected, UNPROVEN(2)

**Session:** 2026-08-24 seat02, THE LOOP row `m1-fixedpoint-arm-validation` (minted 2026-08-23 by seat10 during `rung-gate-false-green-audit`, full diagnosis in `FINDING-2026-08-23-seat10-rung-gate-false-green-audit-continued.md`). Snapshot: SCRIP `411bd9de`, corpus `35b7d034`, `.github` `340cc840`.

## THE DEFECT (as proven by seat10, reconfirmed here before fixing)

`.github/probes/m1-bisect/check_m1_fixedpoint.sh` and its wrapper `SCRIP/scripts/test_gate_m1_self_host_fixed_point.sh` accepted any `$1` silently. The probe sets `rc=0` unconditionally, then runs two independent `case "$ARM" in m3|both) ...;; esac` / `case "$ARM" in m4|both) ...;; esac` blocks — neither matches an out-of-contract value, both are skipped entirely, `rc` never changes, and the script reports "M1 FIXED POINT HOLDS" / "M1 GATE: PASS" at exit 0 having compiled and run nothing. This is the gate for the project's headline Milestone-1 claim (beauty self-host is a byte-identical fixed point), so a silent-pass-on-garbage-input gap here is the same false-green class the sibling `rung-gate-false-green-audit` row exists to police, but on the single highest-stakes gate in the project.

**Before (reconfirmed, unmodified tree, same command seat10 used):**
```
$ bash .github/probes/m1-bisect/check_m1_fixedpoint.sh not-a-real-arm
  M1 FIXED POINT HOLDS (not-a-real-arm)
$ echo $?
0
```

## THE FIX

One line added to each script, placed before any state (`rc`) is touched or work begins, following the project's existing `lib_gate.sh` `UNPROVEN(2)` convention (`GATE UNPROVEN(2) [...]: ...`, `exit 2` — a gate that could not examine what was asked of it, not a verdict on the fixed point itself):

- `.github/probes/m1-bisect/check_m1_fixedpoint.sh`, inserted immediately before the `exp=...; rc=0` line:
  ```sh
  case "$ARM" in m3|m4|both) ;; *) echo "⛔ GATE UNPROVEN(2): unrecognized ARM '$ARM' — expected m3, m4, or both"; exit 2;; esac
  ```
- `SCRIP/scripts/test_gate_m1_self_host_fixed_point.sh`, inserted immediately after `ARM="${1:-both}"`, before the probe is invoked — so a bad `$1` is rejected at the wrapper level too, not solely relying on the probe:
  ```sh
  case "$ARM" in m3|m4|both) ;; *) echo "⛔ GATE UNPROVEN(2): unrecognized ARM '$ARM' — expected m3, m4, or both"; exit 2;; esac
  ```

Each is a 1-line diff (`git diff --stat`: 1 file changed, 1 insertion(+), in each repo). No change to the fixed-point check itself, the compile/run arms, or the report formatting.

## AFTER — DONE-WHEN and both entry points

```
$ bash .github/probes/m1-bisect/check_m1_fixedpoint.sh not-a-real-arm; echo rc=$?
⛔ GATE UNPROVEN(2): unrecognized ARM 'not-a-real-arm' — expected m3, m4, or both
rc=2

$ bash SCRIP/scripts/test_gate_m1_self_host_fixed_point.sh bogus-arm; echo rc=$?
⛔ GATE UNPROVEN(2): unrecognized ARM 'bogus-arm' — expected m3, m4, or both
rc=2
```

DONE-WHEN (`bash .github/probes/m1-bisect/check_m1_fixedpoint.sh not-a-real-arm; test $? -ne 0`) passes.

## REGRESSION CHECK — all legitimate arms still run real work and report the true fixed point

Ran all three legitimate arms through both the probe directly and the wrapper (`RT_OPT=-O0`, per the project's NO-`-O2`-EVER rule; `libscrip_rt-f65f143e2f.so`):

| arm | probe direct | wrapper | md5 |
|---|---|---|---|
| `m3` | FIXED POINT, 40971 bytes, rc=0 | M1 GATE: PASS, rc=0 | `6f1671c0757729992ae01a6bdf16f081` |
| `m4` | FIXED POINT, 40971 bytes, rc=0 | M1 GATE: PASS, rc=0 | `6f1671c0757729992ae01a6bdf16f081` |
| `both` | both arms FIXED POINT, rc=0 | M1 GATE: PASS, rc=0 | `6f1671c0757729992ae01a6bdf16f081` |
| (no arg, defaults to `both`) | — | M1 GATE: PASS, rc=0 | `6f1671c0757729992ae01a6bdf16f081` |

All four md5s match each other and match the value independently recorded in `FINDING-2026-08-23-seat02-sweep-free-rows-are-real-89-classified.md`'s `sn4-m1-r0-bisect` closure — the milestone genuinely holds; this row only closed a hole in the gate that certifies it, and did not touch (or need to touch) the certification logic itself.

## STATUS

All 5 `## NEXT` steps from the task file complete. Row is closeable; DONE-WHEN verified passing, both changed files committed. Not retiring the claim by hand-typed verdict — `s4e_msg.sh done` will re-run the DONE-WHEN itself per LAW 1 before certifying.
