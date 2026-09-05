# FINDING 2026-09-05 (hq_P) — the BENCHMARK oracle cannot case-fold names; the defect is DORMANT because every bench caller passes `-bf`

**Status:** MEASURED, dormant. Documentation cured (comment-only, SCRIP `d03a9dbb2`). Oracle source NOT repaired — that is not a SCRIP change.
**Trigger:** hq_B message `correction-both-oracles-are-broken-and-your-bench-arm-cannot-case-fold`, correcting their own earlier attribution. Their witness: `.github` `cdff151c`.
**Tree:** SCRIP `b66d462df` → `d03a9dbb2` · corpus `911c49b77` · .github `9ccd3a3d`.

## The claim, re-measured on the BENCH face by execution

hq_B established that the two SPITBOL builds differ in more than LOAD support. The whole translator diff is
three lines in `asm.sbl` `g_flc`: stock folds UPPER→lower; our x64 fork flipped it to lower→UPPER (fork commit
`e68dfeb`, *"SN-30g … UPPERCASE canonical case"*). `flc` has **four** call sites wanting **opposite** directions
— `flstg` (the `&CASE` name folder) needs lower→UPPER, while `trace` and the `cnc` control-card scanner fold
then compare against lowercase constants and need upper→lower. So each build is correct at some sites and
broken at the others.

Witness `ABC = 5` / `OUTPUT = 'got=[' abc ']'`, both binaries, this root:

| binary | `-b` | `-bf` | reading |
|---|---|---|---|
| `/home/resources/x64/bin/sbl` | `got=[5]` | `got=[]` | folds by default; `-f` turns it off — **s189 holds here** |
| `/home/resources/spitbol-bench-oracle/sbl` | `got=[]` | `got=[]` | **folding is OFF whatever you pass; `-f` is a no-op** |

⭐ **So the s189 sentence carried at the top of `lib_oracle_flags.sh` — "SPITBOL CASE-FOLDS names by default …
and `-f` turns folding OFF" — is a property of `x64`, not of "SPITBOL".** It remains the right *mandate*; it is
the wrong *explanation* for the bench face, and a seat reasoning from it about the bench binary reasons wrongly.

## The half that is hq_P's: is any perf number affected? NO — swept, not assumed

All 17 `sbl_clean_bin` callers take the language arm from `sbl_lang_flags` **verbatim** (`-bf`). Under `-bf`
**both** binaries have folding off, so they agree, and the folding defect never executes. **`NOISE-FLOOR`
provenance is intact on this axis** — both bakers (`bake_noise_floor_snobol4_{timed,fixed}.sh`) invoke
`"$SBL" $(sbl_lang_flags)`. The two non-users of the accessor are not exposure either:
`bench_triangulate_snobol4.sh` calls `sbl_clean_bin` as a **precondition guard only** and delegates timing to
two callers that do use it, and `test_gate_oracle_bf_capable.sh` is the capability gate itself.

⛔ **What would wake it:** any bench invocation that drops `-f`. That silently changes *which language* the
oracle runs, **on one binary and not the other**, so the two faces stop being comparable and nothing in the exit
code says so. ⛔ **`sbl_bf_capable()` cannot catch this** — it proves `-bf` is ACCEPTED, never that `-f` DOES
ANYTHING. That is the gap worth remembering: a capability probe that passes vacuously on a broken build.

## ⛔ One LIVE bare `-b`, and it is NOT in the perf lane — routed to hq_C

`scripts/test_rsp_descent_sweep.sh:38` runs the **correctness** oracle with bare `-b`:

    ORA=$(cd "$SWEEP_CORPUS" && timeout 30 "$SWEEP_ORACLE" -b "$src" </dev/null 2>/dev/null)

`SWEEP_ORACLE` resolves to `/home/resources/x64/bin/sbl` (`:20`), the face that **does** fold — so this grades
case-sensitive SCRIP against a case-folding SPITBOL. That is the exact s189 class the authority file exists to
retire, and it also hand-assembles the oracle path, which `lib_oracle_flags.sh` forbids by name. A wrong ANSWER
is `hq_C`'s lane; routed, not cured here.

## Pre-existing red, not mine to cure

`test_gate_oracle_bf_capable.sh` is **RED (rc=1)** in this root, on `⛔ STRAY private clone: /home/claude04/x64`
(dated Aug 24, 12 days old — another seat's root; Lon s261 "no root have x64"). **Control arm run:** the gate
returns rc=1 with the *pre-edit* library restored as well, so the red predates this work and the edit is neutral.
Reaching into another seat's root is the FLEET-mode error, so this is reported, not touched.

## Cure applied

Comment-only, SCRIP `d03a9dbb2`, proven mechanically: **zero non-comment lines added, zero lines removed,
function set byte-identical**, `bash -n` clean, all three accessors smoke-tested. Records the second divergence
axis beside `sbl_clean_bin` and points at it from the header, so the "they differ only in LOAD" reading cannot
be re-derived from this file. The real repair is **11 dispatch constants** in the oracle's `asm.sbl` (hq_B has
it designed — point the broken sites at the already-correct `ch_u*`: `ch_ua=65 ch_ui=73 ch_un=78 ch_uv=86`),
an oracle-source change under `/home/resources`, deliberately out of scope for a SCRIP commit.
