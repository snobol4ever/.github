# FINDING-2026-07-29 — SN4 ARITH INLINE LANDED (1.146× arith_int), AND THE TENTH PHANTOM SHAPE: THE WRONG TEMPLATE ARM

**s212, Claude + Lon.** Rung AI-3 of `DESIGN-SN4-ARITH-INLINE-AND-DT-BITS.md`.
**Directive:** Lon, s212 — *"Make it where the actual arithmetic instruction is INLINE within the template …
make the number of instructions for these INLINE BB's as small as possible."* This is the "later" promised by
the **s207 directive** (*"for now all these should be ONE CALL into the runtime. We'll optimize the inline
later."*) — the inline work was DEFERRED BY DIRECTION, and this rung un-defers it.

---

## 1. WHAT LANDED

`src/templates/bb_binop_arith.cpp` — inline int-int ADD/SUB/MUL on **both** arms (fc value-spine and
`op_off` slot), with s207's per-op `call rt_add`/`rt_sub`/`rt_mul` **demoted to a cold fallback at `L(0)`**.
Non-int operands, DT_DATA overloads, reals, DIV/MOD/POW and the `setjmp` ceremony all still route to the
existing C — **unchanged semantics, only a fast path added in front.**

⭐ **NOT WRITTEN FRESH — RECOVERED FROM `d61d7cba^` (the s207 collapse) AND THEN REPAIRED.** The deleted code
was already reviewed and shipped; rewriting it would have re-litigated solved problems. Two defects it
carried were fixed in the recovery:

| Defect in the pre-s207 code | Fix |
|---|---|
| Probes `DT_DATA` **before** `DT_I` — 6 wasted hot-path instructions | Test `DT_I` first; DT_DATA handled by the cold `rt_*` call, whose C body already does the overload probe. **Sound because the guards are mutually exclusive** (`DT_I=6`, `DT_DATA=100`) — the same reordering argument `rtx_arith.S`'s own header uses for `rt_cmp_d`. |
| Reloads both tags a second time (`rspd(16)`/`rspd(0)` twice) | Load once, branch immediately |

**Instruction counts (hot path, MEASURED by reading `scrip --compile` output, not estimated):**

| Arm | pre-s207 | today (s207 call) | **this rung** |
|---|---|---|---|
| fc value-spine | 18 | 9 + call/ret + 9 in asm | **12** |
| `op_off` slot | 17 | 9 + call/ret + 9 in asm | **11** |
| `op_off`, immediate-folded (`N = N + 1`) | — | same | **8** |

⭐ **ZERO `x86_asm.h` CHANGES — THE RTX-11/12 CONCURRENCY COLLISION NEVER HAD TO BE OPENED.**
`DESIGN-SN4-ARITH-INLINE-AND-DT-BITS.md` §1.4 listed five missing encoders and declared the rung blocked on
Lon serializing `x86_asm.h` against the parallel sessions. **That estimate was made from the design, not from
the tree, and it was wrong.** `GVA_LD` in `bb_binop_gvar_arith.cpp` already emits inline int arithmetic with a
tag guard and a call fallback — every encoder needed (`mov r32,m32` · `cmp r32,imm` · `jne L(n)` · `def L(n)`
· `add`/`sub`/`imul` r64,r64 · `mov m64,imm`) was already live. **Same class as the phantom-symbol defects,
inverted: a capability declared missing that was present.** ⇒ **grep the templates for a working precedent
BEFORE declaring an encoder gap**, exactly as step 0(e) says to grep `.S` before declaring a symbol dead.

⚠ The immediate-fold machinery (`op_imm_a_ok`/`op_imm_b_ok`, `emit.cpp:1198-1206`) was **never removed** by
s207 — only its consumption in the template was. It came back for free.

---

## 2. THE BOARD — MEASURED, RT_OPT=`-O0`, interleaved, round 1 discarded (hugepage warmup)

Arms swapped by `LD_LIBRARY_PATH` per ARCH §7 step 4. ⭐ **`scrip` is BYTE-IDENTICAL between arms**
(`md5 f1987887…` both) — the templates live in `libscrip_rt.so`, so one binary runs both arms and nothing is
relinked between them. Swap proven **in both directions** by re-emitting and confirming the box reverts.

| Benchmark | PRISTINE | THIS RUNG | ratio | pre-stated band | verdict |
|---|---|---|---|---|---|
| `arith_int` (100M int-int) | ~1280 ms | ~1117 ms | **1.146×** | 1.15–1.45× | ⛔ **BELOW my own floor — a MISS, reported as one** |
| `arith_mixed` | ~608 ms | ~574 ms | 1.060× | 1.05–1.25× | ⚠ **below ARCH §7's ~1.10× trust threshold ⇒ LEAD, NOT A FINDING** |
| `arith_str` | 475 ms | 465 ms | 1.02× | 0.98–1.05× | ✅ in band — string path correctly unmoved |
| `arith_loop` | 13 ms | — | — | — | ⛔ UNGRADEABLE by construction (its own header says so) |

`arith_int` arms are **non-overlapping**: PRISTINE 1270–1306, THIS RUNG 1093–1153. `arith_mixed` arms are
non-overlapping but barely (594–620 vs 561–589), which is exactly why the ~1.10× rule exists.

⛔ **THE PREDICTION MISSED LOW AND THAT IS RECORDED, NOT ROUNDED.** I pre-stated 1.15–1.45× for `arith_int`
and measured **1.146×**. It is 0.004 under the floor. Reporting it as "≈1.15, in band" would be the exact
dishonesty this ladder's pre-stated-band discipline exists to prevent — s210's under-prediction is the
precedent that this cuts both ways.

⭐ **THE INSTRUMENT IS FAR BETTER THAN THE LADDER ASSUMES.** `arith_int` at 100M iterations reproduces to
**0.3%** (1270/1272/1274 on three consecutive pristine runs). The ±3% null floor and the s209 harness
instability are properties of the SHORT benchmarks, not of this box. **A benchmark sized to ~1.3 s makes a
1.05× effect measurable here.** `arith_int.sno` was written s2xx precisely because `arith_loop`'s 13 ms window
is ungradeable — that judgement is now vindicated with numbers.

---

## 3. ⭐⭐ THE TENTH PHANTOM SHAPE: **THE WRONG TEMPLATE ARM** — COST ONE BUILD, WOULD HAVE COST A SESSION

**The first implementation modified the `op_off` slot arm. `arith_int` never reaches it.**

`N = N + 1` compiles through `vfcb()` — the **value-spine (fc)** arm — reading the top two FORTH cells at
`[rsp+16]/[rsp+24]` and `[rsp+0]/[rsp+8]`. The `op_off` arm was not emitted at all. The build was clean, the
gate was green, the answer was correct, and **the emitted code was byte-identical to pristine.**

⛔ **STEP 0(d) WAS DISCHARGED AND WAS STILL INSUFFICIENT.** s210's census measured `rt_add` at 100,000,000
calls in `arith_int` — true, current, and re-confirmed. The runtime symbol *is* hot. **But 0(d) proves a
SYMBOL executes; it says nothing about WHICH TEMPLATE ARM EMITS the call site.** A template has multiple
mutually-exclusive arms selected by port mode (`vfcb()`), slot availability (`op_off >= 0`), operand class
(`op_num_real`) and literal folding — and editing the wrong one is invisible to every check in §7 step 0.

**This is the family one level BELOW where the checklist currently looks.** The recorded shapes are about
*symbols* (dead, invented, misspelled, already-asm, bypassed, stale-census). This one is about *emission
sites*: the symbol is right, the family is right, the file is right, **the arm is wrong.**

⇒ **PROPOSED ADDITION TO ARCH §7 STEP 0 — (f) PROVE THE ARM YOU ARE EDITING IS THE ARM THAT EMITS:**
> Before editing any multi-arm template, run `scrip --compile <the benchmark this rung will be graded on>`
> and **read the emitted box**. Confirm the instruction sequence matches the arm you intend to change. Ten
> seconds, no build. ⚠ **Comments are NOT emitted in TEXT mode** — do not grep for the template's
> `x86("comment", …)` string as the discriminator (I tried; it silently finds nothing and reads as "the arm
> didn't fire" even when it did). Discriminate on the **operand spelling**: `qword ptr [rsp + 16]` = fc cells,
> `FRQ(op_sa)` = slot frame.

⚠ Note the near-miss: the cold path legitimately still contains `call rt_add`, so **"is there still a call to
rt_add?" is also not a discriminator.** Both of the two obvious checks fail silently here.

---

## 4. FALSIFICATION — TWO-SIDED, OUTPUT-SENSITIVE, AIMED AT THE ARITHMETIC

Corrupted the inline `add`→`sub` on both arms and rebuilt (`RC=0`). `arith_int` then **loops forever**
(`timeout` exit **124**) where the correct build finishes in 1.1 s — `N = N - 1` never reaches its bound.
**The arm demonstrably executes and demonstrably produces the answers.**

⛔ **The corrupted crosscheck could NOT be counted: corruption turns many programs into infinite loops and
the suite does not terminate.** The mover count is therefore UNMEASURED; the infinite-loop probe is the
falsification of record. **Stated as a gap, not papered over.** ⚠ s210's warning that `arith_loop` is a fixed
point which absorbs corruption is why the probe was aimed at an **output-sensitive, terminating** program.

⚠ **The revert was interrupted mid-command and DID NOT APPLY** — verified afterward by grep (`sub`-for-ADD
still 2, `add`-for-ADD 0) and re-reverted by explicit line-number `sed`. **The build artifact carried the
corruption for one cycle.** ⇒ **after any falsification probe, re-grep the source AND rebuild AND re-run the
gate before believing any subsequent number.** All §2 numbers above were re-taken on the restored build.

---

## 5. GATES

| Gate | Result |
|---|---|
| SNOBOL4 crosscheck m3 | **277 PASS / 38 FAIL** — fail-set **byte-identical to PRISTINE, zero movers** |
| SNOBOL4 crosscheck m4 | **275 PASS / 38 FAIL / 2 SKIP** — **identical, zero movers** |
| DIVERGE | 3 (`124_pat_regex_keyword_seal`, `141_pat_eval_double_fn_arbno`, `W06_tab`) — **identical** |
| Icon / Prolog / Snocone | logs **BYTE-IDENTICAL** across arms (4/0 · 189/0 · 7/1) |
| Correctness | `arith_int` 100000000 · `arith_str` checksum `-1000000.` (oracle-exact) |

⛔ **THE OTHER THREE BATTERIES ARE NO-REGRESSION EVIDENCE ONLY, NOT COVERAGE EVIDENCE** — ARCH §7 2b, whose
s165 measurement is that Icon 4/0, Prolog 189/0 and Snocone 8/0 stay unmoved under a *deliberately broken*
arith build. Citing them as a gate on this rung would be the FALSE CLAIM that rule names. ⭐ They ARE the
right instrument for trap 4 (beneficiary notification — the emitter is language-agnostic by FACT RULE, so
`bb_binop_arith` serves every frontend that lowers `IR_BINOP_ARITH`).

⚠ **THE ABSOLUTE WATERMARK DISAGREED FOR THE THIRD SESSION RUNNING: recorded 314/1 · s210 measured 268/47 ·
s212 measures 277/38.** Three sessions, three numbers, on a suite whose size also disagrees (295 vs 315 vs
316 `.sno` found). **The DIFFERENTIAL (same fail-set both arms) is the only instrument that survived, and it
is what this rung is graded on.** ⭐ Do not attempt to reconcile the absolutes until the TAB/RTAB bisect
closes — `047_pat_rtab` is in the fail-set on BOTH arms here, confirming s211's regression is still live and
untouched by this rung.

⛔ **NOT RUN, OWED:** smokes 7/7×2 · beauty · 15-demo board identity · `.s` regen ×3 (**templates changed ⇒
emitted bytes changed ⇒ this IS owed**) · `test_gate_template_medium_invisible.sh --strict`.

---

## 6. OPEN / NEXT

- [ ] **`.s` REGEN ×3** — owed by construction (RULES step 4). Not done this session.
- [ ] Remaining gates in §5.
- [ ] **DIV/MOD inline** — deliberately excluded. s207's commit message records that it *"removes unguarded
      idiv (SIGFPE on zero divisor)"*; re-adding inline `idiv` without an explicit zero test would re-open
      exactly that defect in 5 committed artifacts. Needs the zero test + `INT64_MIN / -1` test, local.
- [ ] **The `or`-computes-the-result-tag identity is NOT yet taken** (design §1.2). It saves one more
      instruction and is free in the *current* numbering, but it needs the both-numeric guarantee to be sound,
      so it belongs with the hoist (route A) — not with this rung.
- [ ] **Route A (hoist) vs B (`DT_t` renumber)** — still open. This rung is the shared prerequisite for
      neither; it stands alone. §3 of the design doc has the decision table. **Route B remains blocked on the
      TAB/RTAB bisect** (tree-wide `.s` regen cannot be graded against a false watermark).
- [ ] `DESIGN-SN4-ARITH-INLINE-AND-DT-BITS.md` §1.4's encoder-gap claim should be **struck** — see §1 above.

**PUSH STATE: NOT ASSERTED HERE.** Per RULES STALE-ORIENTATION (a), a push-status banner in a committed doc
is structurally incapable of being true. `scripts/handoff_status.sh` is the only ground truth.
