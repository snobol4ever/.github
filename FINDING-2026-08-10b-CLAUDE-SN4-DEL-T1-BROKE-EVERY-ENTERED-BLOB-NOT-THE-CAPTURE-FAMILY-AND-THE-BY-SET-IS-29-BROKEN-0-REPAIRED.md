# FINDING 2026-08-10b (s10, Claude Opus 4.5) — DEL-T1 broke EVERY ENTERED blob, not "the capture/recursion family"; BY SET on crosscheck/patterns is 29 BROKEN / 0 REPAIRED

**Goal:** `GOAL-PASSTHRU-RBP-ERAD` · **Container:** fresh · **No code changed this session.** SCRIP/corpus trees untouched; only this file + the goal cursor.

## HASH CORRECTION (read before trusting the s9 cursor)

The s9 cursor names `9f1436b4` (D-1), `5e66bfa6` (D-2), `33062a20` (D-3). **None of those SHAs exist at origin.** They are pre-rebase hashes. The commits actually landed as:

| rung | real SHA | message |
|---|---|---|
| D-1 | `1af93e3a` | DEL-T1 D-1: DELETE the BLOB-GRANT frame establishment for PAT$ blobs |
| D-2 | `1f96143c` | DEL-T1 D-2: PASS-THRU glue for PAT$ blobs — rbp-free activation via g_blob_ctx |
| D-3 | `ef8a3052` | DEL-T1 D-3: separate ACTIVATION ESTABLISHMENT from the scan killswitch |

This is the s8 lesson recurring verbatim ("grep the commit MESSAGE, not the hash"). Session HEAD measured: SCRIP `c7e085fd`, corpus `9fb2e019`. Three parallel RTCC commits + one feature regen landed between D-3 and my open — **the RTCC seat is live**.

## WHAT WAS MEASURED (all same-container A/B, both arms built here)

Baseline reproduced s9 exactly: probe suite m3 **24 PASS / 12 FAIL**, fail set = 5 pre-existing (`ab_freturn`, `ab_nret_lvalue`, `ab_redefine`, `z4_arbno`, `z4_span`) + the 7 named casualties. RTCC landings did not perturb it.

### The inherited diagnosis is FALSIFIED

s9 records the frontier as "capture + recursion families" and prescribes attacking interior `op_flat_disp` for capture. Measured against a constructed minimal pair:

- `w_nocap` — the w_cap_stored program with **every capture operator removed** — **HANGS identically (rc=124)**. Capture is not the differentiator.
- The "passing" blob-bearing witness `pt_inline_1_full` passes because its match statement is `'VACUUM' ? VOWEL . N` — it matches on `VOWEL`, not `PAT`. Its 18 `proc_PAT` defs are **emitted but never entered**. It never exercised the blob path at all.

### Construct bisect, blob presence held constant (subject `'AY'`, `PAT = VOWEL <X>`)

| construct | blobs | HEAD `c7e085fd` | PRE-D-1 `930539c0` |
|---|---|---|---|
| `VOWEL 'Y'` | **0** (fully inlined) | ok | ok |
| `VOWEL LEN(1)` | 18 | **SEGV 139** | ok |
| `VOWEL ANY('Y')` | 18 | **SEGV 139** | ok |
| `VOWEL SPAN('Y')` | 18 | **HANG 124** | ok |
| `VOWEL BREAK('Z')` | 18 | **HANG 124** | ok (`no`, correct) |
| `VOWEL ARBNO('Y')` | 18 | **SEGV 139** | ok |
| `PAT` bare, no capture | 18 | **HANG 124** | ok |
| `PAT . N` | 18 | **HANG 124** | ok — **`AY`, the sbl answer** |

**Every blob-bearing program fails at HEAD. Every one of them was correct pre-D-1. The only survivor emits zero blobs.** The split into SEGV vs HANG tracks the construct, not the presence of capture.

⭐ **CONCLUSION (measured, not inferred): the D-2/D-3 pass-thru glue does not work for ANY blob entry.** The "6 repaired" in the s9 table were not repaired by working glue — they stopped *entering* blobs. `PT-4 PREREQ` was never discharged; DEL-T1 was executed ahead of its own stated prerequisite, which the goal file had already named ("PREREQ: ARBNO/SPAN/BREAK K-conversion inside blob context").

Note the last row: `PAT . N` returned **`AY`** pre-D-1 — oracle-correct, the exact answer s6 and s7 spent two sessions establishing and promoting to `corpus/probe/w_cap_stored.ref`. DEL-T1 regressed a previously oracle-green behaviour.

### BLAST RADIUS — `corpus/crosscheck/patterns` (122 programs), BY SET, both arms same container

| arm | PASS | FAIL | HANG |
|---|---|---|---|
| PRE-D-1 `930539c0` | **97** | 25 | 1 |
| HEAD `c7e085fd` | **68** | 54 | 6 |

**BY SET: 29 BROKEN, 0 REPAIRED.** Not a single program passes at HEAD that failed pre-D-1. Broken set is dominated by the stored-pattern/FENCE-via-var/JSON families (`114`, `115`, `119`, `124`, `126`, `127`, `129`, `130`, …).

### Killswitch state (both confirm s9's D-3 bisect)

`SCRIP_PAT_INLINE=0` and `SCRIP_SCAN_OFF=1` each leave the hangs unchanged — the scan machinery is exonerated, and PT-2's killswitch legitimately does not cover a deletion (goal file says so explicitly). **DEL-T1 has no killswitch; `git revert 1af93e3a` is the only undo, and D-2/D-3 sit on top of it.**

## WHAT THIS SESSION DID NOT DO (disclosed)

broad-336 NOT run (I ran the 122-program pattern crosscheck instead — narrower but the relevant family). **m4 NOT measured** — m3 only. Root cause not localized to an instruction: I convicted the *scope* of the breakage, not the specific defective displacement. No regen owed (no codegen touched). gdb unavailable in this container (attach-based localization was attempted and abandoned).

## ROUTING — LON'S CALL

The evidence changes the revert-vs-fix-forward question materially. Fix-forward was already attempted for a full session (s9) and produced 0 real repairs at 29-program cost.

1. **Revert `1af93e3a`+`1f96143c`+`ef8a3052`, land the PT-4 PREREQ first, then re-delete.** The prerequisite is the goal file's own text. Restores 29 programs immediately. Cost: your "I never want to see that code again" directive is un-discharged in the interim — the blob prologue comes back.
2. **Hold and fix forward**, accepting a 29-program hole in the pattern corpus while interior K-conversion is built under a broken tree.

⭐ Recommendation: **(1)**. The deletion is correct as a *destination*; it was landed before the interior could receive it, and the tree cannot presently prove any blob-entry work. The frame-emission code is deleted and captured in git — re-deleting after the prereq is cheap; measuring anything on a universally-broken blob path is not.

Unchanged routing debts: `bb_match_end.cpp` 12×r10 TIER-2 · `128` own rung · regen ×3 window (RTCC seat live) · ratchet reseed.
