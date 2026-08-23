# FINDING — the benchmark corpus was a HARNESS, not a set of programs; and a `.ref` minted against the wrong oracle arm agrees with the bug forever

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Session:** s265 · **Date:** 2026-08-23
**Trees:** SCRIP `a0ebc660` · corpus `90dbbb895` · both pushed
**Gates, pristine, merged tree:** corpus m3 **359/360**, m4 **359/360 SKIP=0** (only `demo_treebank`, seat03's deliberate red) · `test_gate_emit_no_lang.sh` rc=0 · `test_gate_template_medium_invisible.sh` rc=0

## THE ORDER

**Lon, in-chat, verbatim in substance:** *"We have a problem because the system does NOT have the stand alone program and has all that WRAPPER actually in the SOURCE CODE. And there is NO REF files. So REVAMP the benchmark harness to have the `*.sno` file look like and BE the REAL program application that can be run stand alone, and you can make temporary versions you build on the fly with WHATEVER WRAPPERs you need."*

Then, second: *"Do not use the HUGE files for the REF files. Use the INPUT versions which are small for that reason."*

Then, third: *"Tell HQ-PERFORM that now he can run the app and time wall clock and perf values, and enjoy a TIME based or an ITERATION based benchmark harness. Yeah baby. We should have three options I would think."*

## WHAT WAS ACTUALLY WRONG — MEASURED, NOT ASSUMED

Every one of the **33** programs under `corpus/benchmarks/snobol4/` **was the wrapper**. `arith_loop.sno` in full, before:

```
        ZCHK = 1000
        ZBUD = 500
        ZFLR = 20
        DEFINE('ZBODY(ZKN)')                            :(ZBODY_END)
ZBODY   A = 0
...
ZBODY_END
-INCLUDE 'harness.inc'
```

No `END` of its own. Not runnable standalone — it needs `harness.inc` on the include path to even parse. No real output. And its `.ref` was one line, `check: 1000`, which is not the program's answer but the **harness's phase-1 census**.

Two programs — `ident_call1`, `ident_call2` — had **no `.ref` at all**, and both the scorecard and `test_bench_snobol4_timed.sh` scored them by skipping the comparison. They read as passing because nothing was compared.

⛔ **The demo family was worse, and this is the part worth recording.** `benchmarks/snobol4/demo/` holds a Porter stemmer, a JSON deserializer, a CLAWS5 tagger, two calculators — real applications, with real standalone twins sitting in `corpus/programs/snobol4/demo/`. Their benchmark forks carry this comment, which describes the damage exactly:

> *"Every OUTPUT in the original driver is accumulated into the check value instead of printed, so the check witnesses every value computed, not merely that the match succeeded."*

A 163 KB oracle-gradeable answer had been replaced by one integer. The intent was sound — make the census witness the work — but the cost was the program.

## THE SHAPE NOW

`corpus/benchmarks/snobol4/**/*.sno` is a **standalone application**: its own `END`, its own real output, no `-INCLUDE`, runs under `scrip p.sno`, `sbl -bf p.sno` and csnobol4 with no include path and no harness on disk. `roman.sno` prints Roman numerals. `porter.sno` prints stems. `.ref` is that output, minted from the oracle.

One SNOBOL4 **comment** line splits the file and carries the metadata — inert to every engine, so the program stays standalone:

```
*BENCH kernel=<FN> check=<N> bud=<ms> flr=<ms> [batch=<K>]
```

Above it: the SETUP section (declarations, pattern library, the kernel function). Below it: the MAIN section — the application's own driver and its `END`.

`scripts/bench_wrap.sh` builds the timed twin **on the fly**: SETUP verbatim + the contract variables + a one-line `ZBODY` shim calling the kernel + the body of `harness.inc` **inlined**. Inlined, not included — the twin then has no include-path dependency at all and runs from any directory under either engine, which is what lets it live in a `mktemp` dir.

### THREE OPTIONS, AS RULED

| | how | what it is for |
|---|---|---|
| 1 · **STANDALONE** | don't call the wrapper. `/usr/bin/time -v ./scrip roman.sno`, `perf stat`, `callgrind` | time the real application from outside — and it is **graded while you time it**, because it now has a real `.ref` |
| 2 · **TIME-BASED** | `bench_wrap.sh p.sno` | fix the ms budget, count iterations. Byte-identical harness; `iters:`/`ns:`/`ms:` keep their exact spelling, every existing parser unchanged |
| 3 · **ITERATION-BASED** | `bench_wrap.sh p.sno --mode=iter --n=N` | exactly N iterations, no wall-clock deadline anywhere — the callgrind/cachegrind arm |

⭐ **MODE 3 WAS UNREACHABLE FOR EVERY DATA-DRIVEN BENCHMARK AND NOBODY HAD SAID SO.** The old fixed-work gate was `fixed_n = INPUT` — a stdin read. But `porter`/`json`/`claws5`/`calculator`/`treebank` read their **corpus** from stdin, so that gate could never see a count for them: they were time-based-only, silently, by construction. `bench_wrap.sh --mode=iter` **bakes** `fixed_n` into the generated program instead, which makes instruction-counting reachable for the whole corpus — including the two rows hq_P is actively profiling. hq_P reports having hit the same wall independently and hand-built the same workaround; their published claws5/json figures are already fixed-work and stand, but must be re-baselined on `bench_wrap.sh` before the two sets are mixed.

### THE REFS

`scripts/util_mint_bench_refs.sh` mints every `.ref` from `sbl -bf` and verifies m3 **and** m4 against it. Per Lon's second order, stdin for a ref run is `<prog>.input` → `<family>.input` → `/dev/null` — **never** the big `<family>.dat`, which stays what the timed arm feeds. So `porter.ref` is 1.4 KB, not 163 KB. **Correctness is graded on the small input; throughput is measured on the large one.**

**33 programs · 31 PASS m3 and m4 · 2 fail**, and the 2 are `json-match` / `json-match-fence` TIMEOUT — the already-open `json-match-capture-free-hang` row from the s264 cursor, pre-existing and unrelated to this work.

## ⛔ THE CORRECTNESS DEFECT THIS UNCOVERED — `DATATYPE()` FOLDED PROGRAMMER-DEFINED TYPE NAMES

Minting `json.ref` from the oracle turned `json` red, which is how the defect surfaced. Minimal witness:

```
        DATA('jobj(otab,okeys,onum)')
        DATA('MiXeD(a)')
        OUTPUT = DATATYPE(jobj(1,2,3))
        OUTPUT = DATATYPE(MiXeD(9))
END
```

| | `jobj` | `MiXeD` |
|---|---|---|
| `sbl -bf` (**the law**) | `jobj` | `MiXeD` |
| `sbl -b` (folding — the arm s189 outlawed) | `JOBJ` | `MIXED` |
| SCRIP, before | ⛔ `JOBJ` | ⛔ `MIXED` |
| SCRIP, after | ✅ `jobj` | ✅ `MiXeD` |

**Root cause, `src/runtime/by_name_dispatch.c:5202`.** `bn_type_datatype` spells the built-in type names lowercase internally (`"integer"`, `"table"`, `"array"`, `"string"`…) and upper-cases **the whole result** on the way out. Correct for every built-in. Wrong for the one case where the string did not come from that internal table but from the user's own `DATA` prototype, which must be returned exactly as declared. The fold also ran the name through a `static char ub[32]`, silently truncating any type name past 31 characters.

Cured at the single site by marking whether the name was programmer-declared and returning it verbatim in that case — not by a per-call-site filter, and not by touching the built-in path. m3 and m4 are both byte-identical to the oracle now.

## ⭐⭐ THE TRANSFERABLE LESSON — A `.ref` MINTED AGAINST THE WRONG ORACLE ARM AGREES WITH THE BUG FOREVER

`corpus/programs/snobol4/demo/json.ref` pinned `root=JOBJ`. That ref was minted against `sbl -b` — folding ON — before s189 ruled `-bf` the only correct arm. So for as long as it existed, the pin **agreed with SCRIP's bug**, the demo suite graded green, and the defect was invisible to every instrument aimed at it. It was not found by grading; it was found by **re-deriving the pin from the correct authority and diffing**.

⛔ **Any pin older than s189 is suspect by construction.** A corpus-wide sweep for refs whose spelling can only have come from the folding arm is worth a row. hq_P has recorded the same rung independently, and has recorded — against their own interest — that the two values were printed side by side in their own session-start transcript and not compared: *"printing two things is not diffing them."*

## FILES

- `SCRIP/scripts/bench_wrap.sh` — NEW. The wrapper generator. Refuses by name with rc=2 on: no marker · two markers · non-integer attribute · a kernel with no `DEFINE` · **a SETUP goto crossing the marker into MAIN** (the twin is built from SETUP alone, so such a branch would be a dangling transfer visible only when timing).
- `SCRIP/scripts/util_mint_bench_refs.sh` — NEW. Mint from the oracle, verify m3+m4, small input.
- `SCRIP/src/runtime/by_name_dispatch.c` — the DATATYPE cure.
- `SCRIP/scripts/test_bench_snobol4_timed.sh`, `bake_noise_floor_snobol4_{timed,fixed}.sh` — wrap on the fly; gate on the `*BENCH` marker. ⛔ The old gate asked *"does it include harness.inc"*, which after the revamp is false for **every** program — held unchanged, the entire suite would have reported UNGRADED rather than failing loudly. That is the invisible-skip class again, and it is why the new gate fails loudly by name.
- `SCRIP/scripts/scorecard_snobol4.sh` — `benchmarks` suite drops `norm=ms`. Those programs no longer print measurement lines; a filter with nothing to filter is a blindfold nobody is wearing. Suite scores **18/18 m3, 18/18 m4, 100.0%** on real program output (it was 17/17 on `check:` lines).
- `corpus/benchmarks/snobol4/harness.inc` — now the wrapper TEMPLATE, still valid as an include. Gained one line: a baked `fixed_n` wins over the stdin gate.
- `corpus/benchmarks/snobol4/**/*.sno` + `*.ref` — 33 programs converted, 33 refs minted.
- `corpus/benchmarks/snobol4/demo/*.input` — NEW. The small inputs.
- `corpus/programs/snobol4/demo/json.ref` — re-minted from `sbl -bf`.

## WHAT IS STILL OPEN

- `json-match` / `json-match-fence` TIMEOUT — the existing `json-match-capture-free-hang` row. Untouched here.
- The pre-s189 ref sweep described above — **unminted, needs a row.**
- The 15 `benchmarks/snobol4/demo/` programs are graded by `util_mint_bench_refs.sh` but are **not** in the scorecard, whose `benchmarks` suite is `-maxdepth 1`. Adding them changes the denominator and the weights, and ⛔ **the weights are Lon's knob** — not moved without a ruling.
