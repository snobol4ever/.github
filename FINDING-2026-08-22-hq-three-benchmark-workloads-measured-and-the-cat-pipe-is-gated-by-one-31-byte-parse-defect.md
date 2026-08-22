# FINDING — the three benchmark workloads, measured; and the beauty cat-pipe is gated by ONE 31-byte parse defect

**Session:** 2026-08-22 HQ (`/home/claude`, Claude Opus 5), background discovery agent under HQ LAW 13 as amended. **RT_OPT=-O0.** Oracle `x64/bin/sbl -bf`. Every program run individually `timeout`-wrapped; a hang is recorded as a RESULT, never waited on. `corpus/programs/lon/` excluded by construction.

## A — `corpus/benchmarks/`

176 programs across 4 language dirs; SNOBOL4 is 30 `.sno` (15 top-level kernels + 15 under `demo/`) with 30 `.ref`.

| set | m3 | m4 |
|---|---|---|
| 15 top-level kernels | **15 GREEN** | **15 GREEN** |
| 15 `demo/` | 11 GREEN · 1 FAIL · 3 HANG | 10 GREEN · 2 FAIL · 2 HANG · 1 ASM-ERR |

Non-green: `calculator-2` wrong both modes (`check: -207319` vs `160475`) · `json`, `json-match` HANG both · `json-match-fence` m3 HANG / m4 same wrong value · **`porter` m4 will not assemble — duplicate symbol `.Lx865_40` at `.s:4854`** (m3 green). All wrong-output rows are byte-identical m3 vs m4, so **m3 ≡ m4 holds**.

**Runner:** `test_bench_snobol4_timed.sh` is sound — fixed-ms budget, ns resolution, and it DOES time the oracle (`ENGINES="sbl m3 m4"`, flags from `lib_oracle_flags.sh` → `-bf`). ⛔ But all three runners iterate only `$B/*.sno`: **the 15 `demo/` benchmarks have no runner at all** and no rows in `NOISE-FLOOR.tsv` (60 rows, top-level only). 6 scripts still call bare `sbl -b`.

## B — `corpus/programs/snobol4/demo/` (24 `.sno`)

**m3 18 GREEN / 2 wrong / 2 error / 2 HANG · m4 17 GREEN / 2 wrong / 2 error / 2 HANG / 1 ASM-ERR.**

- **Claim CONFIRMED:** `demo_treebank` is deliberate — `TT_VLIST` has no case in `lower_snobol4.c`, the array never grows, every subscript lands on a null base. Measured `Error 235`, mechanism matches the s194 ruling exactly.
- **Claim CONFIRMED, independently reproduced:** `{"a":1}` and `[1]` → rc 0 correct; `[1,2]` and `{"a":1,"b":2}` → **rc 124 HANG**, while `sbl -bf` answers both instantly. ⛔ `json.input` (the pinned-ref input) *contains a comma*, so that pinned-green row cannot pass today.
- ⛔ **`expression` has NO VALID JUDGE:** SCRIP reports 15 parse errors, and **the oracle itself SIGSEGVs under `-bf`**. A fourth oracle defect, after the `TIME()` mismatch (s253), layout bias (s250), and the 23.47% dead instrumentation in `sbl` (FINDING same day).

## C — the beauty CAT-PIPE: the mechanism works

1. **Input is plain stdin** via the bare `INPUT` keyword (`beauty.sno:604`/`609`), accumulating into `Src`. The `-l131072` in `ReadWrite.inc:9` belongs to a named-**file** reader that is **defined and never called** — it does not gate the stdin path.
2. **1,934 files / 1,526,170 bytes (1.49 MB)** of concatenable SNOBOL4 source exist excluding `programs/lon/`.
3. **`&MAXLNGTH` does NOT cap the feed** — `main01` resets `Src` per statement, so 524288 bounds one statement + continuations, not the file. Verified at 1.41 MB.
4. ⭐ **`cat` IS well-defined — TESTED, not assumed.** 3 crosscheck files (483 B): scrip == oracle byte-identical. **`beauty.sno` doubled (81,942 B): scrip == oracle AND output == input — the doubled self-source is still a fixed point.** Baseline reconfirmed: 40971 B, md5 `6f1671c0757729992ae01a6bdf16f081`.

**⛔ THE GATE IS FAIL-STOP ON ONE PARSE DEFECT.** `mainErr1 ... :(END)` ends the run at the first unparseable statement, and the oracle has **zero** parse errors across the whole feed. Two SCRIP-only blockers:

- ⭐ **31-byte witness:** `        a = 'aa' ; b = 'bb' ; d = 'dd'` + `END` → SCRIP `Parse Error`; oracle beautifies all three. **Two semicolons pass, three fail** — a repetition/resume defect, not a semicolon defect. **42 corpus files carry it.**
- Excluding those 42 (1.41 MB, 1,892 files): SCRIP reaches **742 KB out in 11.4 s at 572 MB RSS**, then halts on `1 # 1 :S(BAD)F(OK)`.

## Verdicts and the single highest-value fix each

- **A — NEEDS-WORK.** Kernels clean 15/15 both modes; the `demo/` family has no runner and 5 reds. Fix: **the `.Lx865_40` duplicate-label emitter bug** — the only program that cannot be built at all, and a label collision is a SCALE defect that will bite CAT-PIPE at m4.
- **B — NEEDS-WORK.** Fix: **the json ARBNO-comma hang** — one defect clears 3 rows here and 3 in A, **6 of the 11 total reds**.
- **C — NEEDS-WORK, not blocked.** Mechanism, oracle-identity and scale all check out. Fix: **the 3-semicolon parse defect**, the first fail-stop, gating 42 files.
