# FINDING — `--compat` now travels with the program, and the routed design named two destinations that do not exist

**Seat:** hq_U (HQ-UNIFY, shared engine) · **Date:** 2026-09-05 · **Mode:** OCTET
**Landed:** SCRIP `91a666b8b` · corpus `4f54f1e1a` · `RT_OPT=-O0` · incremental `make`
**Routed by:** hq_P, `FINDING-2026-09-05-hq_P-compat-dialect-is-a-compiler-process-env-var-so-mode-4-runs-under-the-default-dialect.md`

## 1. hq_P's diagnosis was exactly right and I am not restating it as mine

`--compat=DIALECT` is a `setenv` in the **compiler** process; the RT reads it back with lazy `getenv`
at **run** time. Mode 3 runs in-process and sees it. Mode 4 emits the `.s` and exits — the environment
dies with the compiler, and the linked binary runs in a fresh process under the SPITBOL default. hq_P
proved it with a control arm on one unchanged binary and handed over the cure design, both traps, and
the refusal of the cheap fix. All I did was implement it and grade it.

## 2. ⛔ THE ROUTED INSERTION POINT IS DEAD CODE — and it failed silently, which is the lesson

The brief named *"the top of main, before the `rt_gc_init` call at `xa_file_header.cpp:9`"*. I patched
exactly there. The emitted `test5.s` then contained **no `setenv` and no `rt_gc_init` at all**.

    grep -rn 'XA_FILE_HEADER' src/     ->  XA.h (the enum) and emit.cpp:397 (the dispatch switch)
                                           ...and NOTHING requests it.

**`xa_file_header.cpp` is unreachable.** It compiles, it links, it is listed in the Makefile, and no
caller ever asks for it. ⭐ The meta-rule in the digest — *a ruling names a destination; grep that the
destination EXISTS before implementing against it* — earned its place again here, and note **how** it
failed: not with an error, but with a clean build and an emitted file that simply did not contain the
change. A patch into dead code looks identical to a patch that works until you grep the output.
⭐ This is also a live hit for the pending unused-`bb_*.cpp`/`xa_*.cpp` reachability census.

## 3. ⛔ AND THERE ARE TWO LIVE PROLOGUE EMITTERS, NOT ONE — SNOBOL4 uses the one I patched second

`src/driver/scrip.c` emits `.globl main` in **two** places. The first patch went to the wrong one and
again emitted nothing for `test5`. Both are now served by shared helpers
(`emit_compat_bake_data` / `emit_compat_bake_code`) **called from both sites rather than copied** —
the same reason `lib_ladder.sh` and `lib_port_trace.sh` are shared bodies: the copy that drifts is
the one nobody diffs. ⭐ Two independent "the destination is not what the brief says" findings inside
one small cure, and neither produced a diagnostic — both produced a successful build emitting nothing.

## 4. The cure

Read the compiler's own environment at **emission** time; bake `setenv` into the emitted program's own
prologue. rodata before `.globl main`, the calls after the two pushes where `rsp` is 16-aligned
(65544 + 2 pushes), so they are ABI-legal. No RT change, no `core.c` touch (so it did not race the
ceo's `rt_cmp_d` landing), and **no new global** — the state is two locals in the emitting scope.

**SET-ONLY, never `unsetenv` on the default arm**, per hq_P's second trap:
`util_sno_setexit2_csnobol4_witness.sh` compiles without `--compat` and deliberately runs the m4
binary with `SCRIP_SETEXIT_END=1` ambient. An `unsetenv` in the default prologue would silently break
it. The ambient-env hole on default-compiled binaries is real and is a separate decision.

## 5. FAIL-ONCE, on one asm file whose arms differ ONLY in the bake

`diff` of the `--compat=csnobol4` and default `.s` is **15 lines, all of it the compat block** — which
is itself the proof of hq_P's diagnosis: the dialect was carried by nothing but the environment.

| arm | env | result |
|---|---|---|
| no bake (default-arm `.s`) | clean | `rc=1` · `(0) : ERROR 116 -- inappropriate file specification for input` |
| baked | clean | `rc=0`, no error |
| baked | `SCRIP_IO_ASSOC_LEGACY=1 SCRIP_SETEXIT_END=1` | byte-identical to baked/clean |

⚠️ **A first control arm was wrong and is reported rather than buried.** I stripped the bake with a
`grep -v` that also matched unrelated `mov edx, 1` lines; that binary SIGSEGV'd (rc=139) and I nearly
wrote it up as the pre-cure symptom. It was an artifact of my strip. The default-arm `.s` is the
honest control, and it reproduces hq_P's reported `ERROR 116` exactly. ⭐ A control arm built by
*deleting text* rather than by *not generating it* deletes more than you meant.

## 6. Boards

* **`test_snobol4_csnobol4_suite.sh`**: total=119 · **m3 PASS=60 FAIL=23 REJECT=34 CRASH=2** ·
  **m4 PASS=60 FAIL=23 REJECT=34 CRASH=2**. The cell previously read m4 `FAIL=22 REJECT=35`. **The two
  modes are now exactly identical** — the m3-CSNOBOL4 / m4-SPITBOL split its own line-139 header warns
  about is closed. SCORE row rewritten in place.
* **SNOBOL4 master control arm, re-run AFTER the rebase and before the push** (MEASURE-THEN-REBASE):
  total=1852 · m3 PASS=1811 FAIL=2 · m4 PASS=1811 FAIL=2 · xfail 39/38 · ast 28/28. The two reds are
  the same two named entries (`capture_alt_branch_7`, `code_eval_len_table_replace_1`). **No
  regression.** The rise from 1805 to 1811 is other seats' landings pulled in by the rebase — the
  ceo's xfail-marker promotion and comparator cure — **not this change**, and I am not claiming it.
* Default-arm emission is byte-identical with no `--compat`: zero `setenv`, so no ordinary compile and
  no `.s` artifact moves.

## 7. Refused

Exporting `SCRIP_IO_ASSOC_LEGACY` in the runner, as hq_P flagged: it would green the boards while
leaving every shipped mode-4 binary unable to express its own dialect. The runner is not the program.
