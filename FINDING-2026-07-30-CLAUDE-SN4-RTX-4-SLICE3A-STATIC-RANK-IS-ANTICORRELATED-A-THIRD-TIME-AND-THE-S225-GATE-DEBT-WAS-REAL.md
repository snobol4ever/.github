# FINDING — SN4-RTX-4 SLICE 3A: `rt_flat_wire_adopt` LANDED, THE STATIC RANK WAS ANTI-CORRELATED A THIRD TIME, AND THE s225 GATE DEBT WAS REAL

**Session:** s226 (2026-07-30) · Claude · `GOAL-SNOBOL4-RTX.md`
**Contract:** `ARCH-SNOBOL4-RTX.md` §7 · RT_OPT=`-O0` · zero templates touched ⇒ **no `.s` regen owed** (verified, not inherited)

---

## 0. THE RESULT THAT OUTRANKS THE PORT

**A STATIC CALL-SITE RANK PUT THIS SYMBOL 16th OF 46. STEP 0(d) PUT IT 4th OF 20, AT 23,743,053 ENTRIES.**
This is the **third** consecutive time the ladder has been shown that static site count measures the EMITTER'S REACH and not execution — s188 (`rt_call_arr`, 232 sites / cold), s225 (`rt_defer_step`, 434 sites / **zero** dynamic entries), and now s226 in the **opposite direction**: a symbol that the static census RANKS TOO LOW.

⭐⭐ **THE PRIOR TWO CASES WERE FALSE POSITIVES; THIS ONE IS A FALSE NEGATIVE, AND IT IS THE MORE DANGEROUS SHAPE.** A false positive costs a wasted rung and announces itself (the port lands, the probe does not fire, s213's batch gets reverted). A false negative is SILENT: the symbol simply never appears near the top of a queue, no session ever looks at it, and nothing in the tree ever says so. `rt_flat_wire_adopt` has **6 static sites** — below `rt_call_arr` (99), `NV_SET_fn` (43), and every one of the five `rt_proc_set_*` (16 each), all of which are colder than it. ⇒ **RULE: THE 0(d) CENSUS IS NOT A FILTER APPLIED TO A STATIC SHORTLIST. It must be run over the WHOLE still-C surface, or the symbols it would have promoted are never candidates in the first place.**

---

## 1. THE s225 GATE DEBT WAS REAL AND IS NOW DISCHARGED

The s225 LIVE CURSOR's correction banner was **correct**: the kill-switch sweep it claimed had passed was never run. Re-run this session from a clean clone at `origin/main`:

| gate | result |
|---|---|
| `test_gate_rtx_killswitch_sets.sh MATCH <crosscheck> 4 both` | **GATE PASS** — 317 progs · m3 IDENTICAL=316 QUARANTINE=1 **MOVER=0** · m4 IDENTICAL=313 QUARANTINE=1 **MOVER=0** SKIP=3 |
| `test_rtx_unit.sh` | ALL PASS — 21 + 36 + **8426** checks, 0 mismatches |
| `test_gate_rtx_store_width.sh` | PASS — 16 GOT-tainted stores checked |

⇒ **RTX-8 SLICE 10 IS NOW GATE-COMPLETE.** The correction did its job: the debt was named in the file, a later session read it and paid it. That is the STALE-ORIENTATION rule working as designed, and it is worth recording that the mechanism succeeded, not only that the original claim failed.

⭐ **NEW DATUM ON THE `160` QUARANTINE (the ladder's open "characterise at N≫4" rung).** Across the two sweeps this session, `160_pat_alt_inner_gen_resume` produced a **3-element union**: `{5d701824, 6a68d667, d7772c55}`. MATCH-sweep m4 saw all three in the ON arm alone. **Instability is present with the gate OFF in every sweep** ⇒ it is C-side by the gate's own argument and blocks no port. ⚠ Still NOT characterised — a union across runs is a LOWER BOUND on the set, not the set.

---

## 2. THE PORT

`rt_flat_wire_adopt` — the **write** side of the wire quad that `rt_flat_ret_snap` (asm since slice 3) **reads**. Same two globals, same struct, same stride, same `call` family gate. Landed in `rtx_call.S`; C renamed `c_rt_flat_wire_adopt` in the SAME commit.

**MEASURED, BOTH FROM THE OBJECT (never estimated):** asm **20 instructions** vs C **41**. The `-O0` C body's waste is confirmed empirically rather than asserted: a full `rbp` frame on a strict leaf, all FOUR pointer args spilled to `[rbp-N]` and reloaded, `g_pcall_top` loaded **twice**, `g_pcall_wires` loaded **twice**, and the `w` pointer spilled to `[rbp-0x8]` and **reloaded before every one of the five stores**.

**STEP 0 DISCHARGED IN FULL:**
- 0(a) live definition — `rt.c:1051`.
- 0(b) spelling round-trips byte-identically against the tree; the sibling `rt_flat_wire_adopt_isle` (5 args, r12 variant) is a **SEPARATE symbol and was deliberately NOT touched** — verified `grep -c` = 1 after the rename.
- 0(c) **RUN ON THE OBJECT FILE, NOT THE `.so`**: `g_pcall`/`g_pcall_top`/`g_pcall_wires` are `GLOBAL HIDDEN` in `rt.o` and **absent from the `.so` dynamic table** ⇒ `[rip+sym]` direct, **`@GOTPCREL` NOT owed**. Confirmed in the emitted object: `mov eax, DWORD PTR [rip+0x46f219] # g_pcall_top`. **ZERO visibility promotions needed** — the sibling port had already paid that cost.
- 0(d) **23,743,053 entries** corpus-wide; **exactly 10,000,000 on `func_call` and `func_call_overhead` = the loop count**, i.e. 1:1 with SNOBOL4 procedure calls. Manual Ch.8: every `DEFINE`'d function reaches `RETURN`/`FRETURN`/`NRETURN` exactly once per activation, so "once per call" is a property of the LANGUAGE, not of the benchmark.
- 0(f) **10,000,000 entries / 0 BAILED / 10,000,000 COMMITS on `func_call`** — 100% asm, **no cold arm exists**. Contrast s224 slice 9 (1 entry ⇒ 0 commits) and s225's retarget: this is the shape those slices wished for.

**FALSIFICATION — TWO-SIDED, PROBE SIZED FROM THE COMMIT COUNT PER §7 step 2b-0:** `ud2` planted **after the guards, on the commit path** (not at entry — an entry-sited probe would not distinguish guard-return from commit). Gate ON ⇒ **rc=132 SIGILL**. **SAME BUILD**, `SCRIP_RTX_CALL=0` ⇒ **rc=0, `result: 10000000` correct.** Revert verified **THREE ways**: `grep ud2` = 0 · src md5 OK · `.so` md5 **BIT-IDENTICAL** to pristine `f89f3d2b070ce4acb3fcfc03d193dd1c`.

**GATES AT THE RE-PROVEN WATERMARK:** session-start re-prove **m3 312/4/0 · m4 312/2/2 · DIVERGE=2**, fail sets `{test_case,140,141,160}`/`{test_case,160}` — **HELD EXACTLY after the port**, 24 s. `test_gate_rtx_killswitch_sets.sh CALL <crosscheck> 4 both` ⇒ **GATE PASS**, 317 progs, m3 316/1/**0** · m4 313/1/**0**/SKIP 3. Unit ALL PASS. Store-width PASS.

⛔ **NO SPEED NUMBER IS CLAIMED.** The rail still refuses every window on this machine (s224 hugepage bimodality) and that rung is still open and still outranks every port. This is an **ERADICATION** slice serving RTX-12; the 3-arm rail was deliberately NOT run rather than run and spun.

⚠ **COVERAGE CARRIES ITS POPULATION (s224 rule):** the 0(d)/0(f) numbers above are the **21-program SNOBOL4 BENCHMARK battery**, measured on ALL 21, of which **6** have non-zero entries (`func_call`, `func_call_overhead`, `fibonacci`, `mixed_workload`, `roman`, `indirect_dispatch`).

⭐⭐ **THE REGRESSION BASE IS ENUMERATED, NOT ASSUMED — AND IT IS THE FIRST HEALTHY ONE IN FOUR SLICES.** 317 crosscheck programs compiled and grepped ⇒ **27 can statically REACH the symbol**; the arm census was then run on **ALL TWENTY-SEVEN** (never a sample — that is the s224 mistake):

**23 of 27 COMMIT ≥1 · 0 of 27 BAILED ONCE · 412 total commits · 4 reach-but-never-execute** (`expr_eval`, `140`, `141`, `1017_arg_local`).
Top carriers: `088_define_recursive_fib` **204** · `212_gc_args_in_flight` 80 · `test_stack` 25 · `1010_func_recursion` 15 · `test_string` 14 · `test_math` 12 · `204_gc_recursive_frames` 11 · `test_case` 11.

⭐ **NOT ONE PROGRAM SHOWS THE `entries − 1 = commits` LAZY-ARM SHAPE** that hollowed out slice 9 (where 5 of 7 reaching programs had 1 entry ⇒ 0 commits, and the gate's entire power rested on `test_case`, which fails its own oracle, plus `test_string`, which does not link in m4). Here `test_case` is **1 of 23 committing programs, not the sole carrier**, and both it and `test_string` could be removed from the base without the base collapsing. ⇒ **the byte-identity gate has real power over this asm**, which is a claim slice 9 could not honestly make. The suite-wide `IDENTICAL=316` remains **no-regression evidence and NOT a claim that 316 programs exercised the asm** — 27 did, 23 of them committing.

⚠⚠ **AND THE COVERAGE INSTRUMENT ITSELF PRODUCED A FALSE ZERO BEFORE IT PRODUCED THIS NUMBER — RECORDED BECAUSE IT WOULD HAVE BEEN PUBLISHABLE.** The first sweep invoked `scrip --compile <p> -o /tmp/cov.s` and reported **`TOTAL=317 REACH=0`**. `--compile` writes to **STDOUT and takes no `-o`**: every one of the 317 invocations returned rc=1 and wrote nothing, and `grep` on a nonexistent file dutifully matched nothing. **A clean, plausible, universal zero produced entirely by a bad flag.** It was caught only by re-running the instrument against `func_call.sno` — a program already PROVEN to reach the symbol by two independent measurements — and getting 0 where 1 was mandatory. ⇒ **RULE: A COVERAGE INSTRUMENT MUST BE SHOWN TO RETURN A POSITIVE ON A KNOWN-POSITIVE BEFORE ANY ZERO IT REPORTS IS BELIEVED.** Same family as the s220 `util_rtx_count_syms.sh` rc=139 note ("a zero from this tool must NOT be read as never called") and as §0's false-negative class: **the tool that silently reports nothing is more dangerous than the tool that crashes.**

---

## 3. THE LOCKSTEP TRIO — AND WHY TWO OF ITS MEMBERS ARE **NOT** ASM RUNGS

Three still-C symbols fire in near-exact lockstep across the benchmark battery:

| symbol | static sites | static rank | **dynamic entries** |
|---|---|---|---|
| `rt_flat_wire_adopt` | 6 | 16 | **23,743,053** |
| `rt_goto_transfer` | 6 | 17 | **23,743,053** |
| `rt_proc_call_open_slim` | 13 | 11 | **23,742,553** |

The 500 delta is fully accounted for: `indirect_dispatch` routes through the non-slim `rt_proc_call_open` (500 calls) instead.

⭐⭐ **BUT THE OTHER TWO MUST NOT BE TAKEN AS ASM PORTS, AND SAYING SO IS THE POINT OF THIS SECTION.** Reading their C bodies (§7 step 1, before writing any asm):
- `rt_goto_transfer` (`runtime_eval.c:276`) resolves its target through `rt_label_get_fn`, which is a **LINEAR `strcmp` SCAN over `g_lbl_tab`** — plus an `snprintf` into a 256-byte buffer and a second lookup on the `LBL__` miss path. At 23.7M calls the cost is the SCAN, not the call ceremony.
- `rt_proc_call_open_slim` (`rt.c:1150`) opens with `rt_proc_find(name)` (name lookup) and carries a `strcmp` loop over `np` formals.

⇒ **THESE ARE ALGORITHMIC RUNGS (lookup structure), NOT INSTRUCTION-COUNT RUNGS.** A faithful transliteration to asm inherits the scan and wins only `-O0` ceremony on top of an O(n) body — the s188 `try_call_builtin_by_name` lesson exactly ("an asm port inherits that algorithm"). The tree already carries a documented landmine on this shape: `FINDING-2026-07-18-CLAUDE-PL-SPEED1-DOLLAR-GATE-80M-STRCMP-POINTER-CACHE-LANDMINE.md`. **Scope with Lon before any code; it is plausibly the largest single lever on this battery and it is not an RTX-phase-1 rung.**

---

## 4. RTX-7's DOWNGRADE PREMISE IS MEASURED ON A NON-REPRESENTATIVE SAMPLE

RTX-7 was downgraded s208 with: *"`NV_GET_fn` = ZERO calls in var_access · func_call · string_manip · table_access · fibonacci · indirect_dispatch · op_dispatch"* and bounded at a **0.58% UPPER BOUND**, concluding *"a perfect port wins less than the ±3% null floor."*

**THOSE SEVEN ZEROS REPRODUCE EXACTLY THIS SESSION.** `NV_SET_fn` takes 25–26 entries (startup only) on every one of them. **But it is the #1 executed still-C symbol overall at 24,700,581 entries**, and the volume lives in programs s208 did not sample:

`string_pattern` **10,000,026** · `pattern_bt_deep` **8,000,028** · `eval_dynamic`/`eval_fixed` **2,000,026** each · `roman` 1,200,038 · `mixed_workload` 1,000,046 · `pattern_bt` 500,028.

s208 DID name EVAL as the live window. What the sample missed is the **PATTERN family** — 18M of the 24.7M. ⇒ **The 0.58% ceiling is a property of s208's seven programs, not of the symbol.** This is the s224 "population in the same sentence" defect one more time, and it is the SAME SHAPE as §0: a correct measurement on an unrepresentative set, published as a general conclusion. ⛔ **Do not re-quote the 0.58% bound without naming its battery. RTX-7's speed premise needs re-measuring on the pattern/EVAL programs before it is called a null.** ⚠ `NV_SET_fn` remains DB-1's write-barrier choke point — coordinate per the concurrency contract.

---

## 5. THE FULL BENCHMARK SURFACE, AS MEASURED (the queue for "convert everything the benchmarks use")

The 21 SNOBOL4 benchmarks call **46 distinct runtime symbols** / 871 static sites. **24 are already asm (486 sites, 55%).** Of the 20 still-C runtime symbols (`main_α` and `proc_startup` are compiler-emitted PROGRAM symbols, not runtime — struck from the queue):

**HOT:** `NV_SET_fn` 24.70M · `rt_flat_wire_adopt` 23.74M **[LANDED THIS SESSION]** · `rt_goto_transfer` 23.74M · `rt_proc_call_open_slim` 23.74M · `rt_call_arr` 12.46M
**WARM:** `rt_div` 81,405 (arith_mixed only)
**STARTUP-ONLY (16–32 calls total):** `rt_proc_call_open` · `rt_proc_set_frame_bytes` · `rt_proc_set_jmpentry` · `rt_proc_set_dyn_scope` · `core_lib_init` · `rt_gva_island` · `gva_register` · `rt_proc_set_fn` · `rt_proc_register` · `rt_proc_set_zstatic` — **exactly 21 for the three `*_init`/`gva_*` symbols = one per program.** Porting these buys ZERO time; they are RTX-12 eradication only.
⛔ **ZERO ENTRIES ON ALL 21 — UNFALSIFIABLE, DO NOT PORT (Lon directive s213 / step 0(d)):** `rt_proc_set_nparams` · `rt_arg_stage` · `dtp_fn_of` · `rt_defer_step` (confirms the s225 strike on a second battery).

⚠ **`rt_arg_stage` is named as a port target inside RTX-4 SLICE 3's own rung text and is ZERO here** — same class as the names struck at s204/s213. It needs a minted workload before anyone writes asm for it.

⭐ **`rt_call_arr` — s188 AND the retarget are BOTH right, and the population is the whole story.** 4–6 calls on most benchmarks (agreeing with s188's cold verdict on the rail demos) but **10,000,004 on `string_manip`**, 1,000,004 on each `eval_*`, 400,008 on `roman`. **This reproduces RTX-4 SLICE 3's retargeting numbers TO THE DIGIT** ("string_manip (10.0M) · eval_fixed (1.0M) · roman (400K)") ⇒ the instrument is confirmed against an independent prior measurement, and that rung's gating choice was correct as written.

---

## 6. NEXT RUNG

1. ⭐⭐ **The rail's min-of-N / hugepage-pinning mode** — unchanged from s224/s225, still blocks EVERY speed claim on this machine, still outranks any port.
2. ⭐⭐ **The `rt_goto_transfer` / `rt_proc_call_open_slim` LOOKUP rung** (§3) — 23.7M × linear `strcmp` scan. Lon's routing; algorithmic, not phase-1 RTX.
3. ⭐ **Re-measure RTX-7 on the pattern/EVAL battery** (§4) before its 0.58% ceiling is quoted again.
4. Run the whole-surface 0(d) census for **Icon and Prolog** the way §0's rule now demands — both ladders have been ranking off static counts.
5. `DESCR_t.slen` SNOBOL4 half · `util_regen_feature_s_artifacts.sh` missing `SNO_LIB` · characterise `160` at N≫4 (§1 gives a 3-element lower bound).

`handoff_status.sh` is the push truth — **NOT this document.**
