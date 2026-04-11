## SWI-Prolog Benchmark Suite — Prolog JVM Backend

**Suite:** [github.com/SWI-Prolog/bench](https://github.com/SWI-Prolog/bench) (31 programs)  
**Milestone:** M-PJ-BENCH-BASELINE (PJ-84a, commit `a79906e`)  
**Status: 31/31 ✅**

> JVM wall-clock times include JVM startup (~100ms cold). The suite is designed
> for iteration-count scaling; single-pass times are shown for compile-and-run
> correctness validation only — not performance comparison.

| # | Benchmark | Status | JVM (cold) | Notes |
|---|-----------|:------:|:----------:|-------|
| 1 | `tak` | ✅ | 112ms | |
| 2 | `nreverse` | ✅ | 159ms | |
| 3 | `qsort` | ✅ | 119ms | |
| 4 | `flatten` | ✅ | 132ms | was VerifyError (`nonvar/1` stack fix) |
| 5 | `crypt` | ✅ | 153ms | |
| 6 | `derive` | ✅ | 152ms | |
| 7 | `fast_mu` | ✅ | 135ms | |
| 8 | `log10` | ✅ | 171ms | |
| 9 | `meta_qsort` | ✅ | 119ms | was VerifyError (`nonvar/1` stack fix) |
| 10 | `mu` | ✅ | 138ms | |
| 11 | `nand` | ✅ | 182ms | |
| 12 | `ops8` | ✅ | 150ms | |
| 13 | `poly_10` | ✅ | 178ms | was COMPILE_FAIL (`:- op` dynamic table) |
| 14 | `prover` | ✅ | 174ms | was COMPILE_FAIL (`:- op` dynamic table) |
| 15 | `query` | ✅ | 159ms | |
| 16 | `reducer` | ✅ | 133ms | was VerifyError (`atomic/1` stack fix) |
| 17 | `sendmore` | ✅ | 151ms | |
| 18 | `serialise` | ✅ | 153ms | |
| 19 | `simple_analyzer` | ✅ | 166ms | was VerifyError (`atomic/1`+`nonvar/1`) |
| 20 | `times10` | ✅ | 130ms | |
| 21 | `divide10` | ✅ | 157ms | |
| 22 | `unify` | ✅ | 168ms | was VerifyError (`nonvar/1` stack fix) |
| 23 | `zebra` | ✅ | 129ms | |
| 24 | `sieve` | ✅ | 126ms | was Jasmin error (NAF nesting fix) |
| 25 | `fib` | ✅ | 119ms | was COMPILE_FAIL (`:- table` directive) |
| 26 | `boyer` | ✅ | 130ms | was VerifyError (`atomic/1` stack fix) |
| 27 | `browse` | ✅ | 121ms | was VerifyError (`nonvar/1` stack fix) |
| 28 | `chat_parser` | ✅ | 205ms | was Jasmin error (14-arg desc overflow) |
| 29 | `perfect` | ✅ | 164ms | |
| 30 | `queens_8` | ✅ | 115ms | |
| 31 | `eval` | ✅ | 174ms | |

### Bugs fixed to reach 31/31

| Bug | Symptom | Root cause | Fix |
|-----|---------|-----------|-----|
| `atomic/1` VerifyError | `Inconsistent stack height 0 != 1` | `dup`+`ifne a_ok` left tag-ref on stack at join; fall-through had depth 0 | `pop` at `a_ok`; explicit `goto lbl_γ` for float path |
| `nonvar/1` VerifyError | `Inconsistent stack height 1 != 0` | `dup`+`ifnull nfail` left ref on stack at `nfail` | `pop` before `goto lbl_ω` at `nfail` |
| NAF nesting | Jasmin syntax error mid-method | Inner `\+` wrote helper `.method` block into outer helper's byte stream | Per-helper `tmpfile()`, chained onto `pj_helper_buf` for deferred flush |
| Descriptor overflow | Jasmin truncated `invokestatic` | `argpart[256]` / `desc[512]` overflow at 14 args (14×18=252 bytes) | Widened to `argpart[1024]` / `desc[2048]` |
| `:- table` parse error | Parse error on `table foo/2` | `table` not in fx-1150 prefix-op list | Added `table`/`enable_tabling` to parser prefix list + emitter skip list |
| User-defined operators | Parse error on `x less_than y`, `P # Q`, `P & Q` | `:- op(P,T,N)` directives not applied at parse time | Dynamic `user_ops[]` table; `find_binop()` extended; op/3 processed immediately in `parse_clause` |
