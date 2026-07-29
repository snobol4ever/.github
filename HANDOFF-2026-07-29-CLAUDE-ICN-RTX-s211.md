# HANDOFF-2026-07-29-CLAUDE-ICN-RTX-s211 — RTX-6-ICN LANDED AT 1.783×, AND THE RUNG WAS WON BY READING THE EMITTING TEMPLATE INSTEAD OF THE C FILE

**Session:** s211-ICN · **Ladder:** `GOAL-ICON-RTX.md` · **Landed:** SCRIP `eb81508d` · corpus `90559c6c` · `.github` `10da9696`
**Gates at close, all re-derived fresh on the REBASED tree:** Icon **252/11/30** · SNOBOL4 **m3 280/54 · m4 276/50/8** ·
Prolog **185/0/0** — each identical gate ON and OFF. Session baseline `.so` md5 `9a83beff3e8ab0586df34f83c0f660cd`.

⛔ **PUSH STATE IS NOT ASSERTED HERE — `scripts/handoff_status.sh` is the only truth** (RULES.md s47(a)).
At the moment it was last run it reported all three repos unpushed; **no credential was available.**

---

## ▶ WHAT LANDED

1. **RTX-6-ICN — `rt_coerce_num2_d` in asm** (gate `SCRIP_RTX_ICNNUM`, **eighth family gate = shared
   state**), with the `static` callee `rt_parse_num_d` **ABSORBED, not exposed**.
   **ON/PRISTINE 1.783×**, 3-arm interleaved, round 1 discarded: ON 861ms (841-922) · PRISTINE 1535ms
   (1523-1583) · OFF 1580ms. Spreads 1.04-1.10× against a 1.783× gap; **ON and PRISTINE do not
   overlap.** Kill-switch tax 0.972×. `RT_OPT=-O0`. PRISTINE `.so` verified **byte-identical to the
   session baseline**, so the honest arm is provably the untouched runtime.
   ⛔ **SCOPE: this is an ISOLATION benchmark.** The allocation-mixed variant was **REFUSED by the
   harness**; its 1.188× is recorded as **not-a-result** and is not claimed anywhere.
2. **RTX-0b-ICN first half** — self-timed scalable Icon benchmarks in `corpus/benchmarks/icon/rtx/`.
3. **Ledger, cursor, FINDING, and the mandatory shared-runtime notification** to SN4-RTX + Prolog.

---

## ⭐⭐ THE TRANSFERABLE CONTENT — STEP 0(g) HAS A SECOND HALF

**The arm a callee takes is decided by the CALLER TEMPLATE'S INLINE GUARD, and the guard is written to
skim off the CHEAP cases — so the callee is left holding the EXPENSIVE one.**

`bb_coerce_numeric.cpp:18-31` inlines DT_I+DT_I and DT_R and reaches γ **without calling anything**;
the emitted `call rt_coerce_num2_d@PLT` sits only on the arm that guard REJECTS. Measured: pure-integer
arithmetic enters the symbol **0 times**; string→numeric enters it **60,000 times / 120,000 parse
entries**, live arms **STR_INT + DT_I**, **STR_REAL / SNUL / FAIL all ZERO**.
⇒ `rt_parse_num_d`'s two textually-first arms are **unreachable from Icon**, and porting them — the
obvious reading of both the C source and s210's own handoff — **would have measured ~0.** That is
RTX-1-ICN's exact error one rung over.

**RULE (proposed for `ARCH-ICON-RTX.md` §8):** *before choosing an arm, read the EMITTING TEMPLATE and
grep it for an inline `cmp`/`je` over the descriptor tag. If the template guards the call, port the arm
the guard REJECTS.* Cost: one grep.

⭐ **AND IT DISCRIMINATES — I RAN IT ON THE NEXT RUNG BEFORE CLOSING.** `bb_binop_relop.cpp` has **NO
inline tag guard**: zero `cmp DT_*`/`je` before any call, and `rt_jct_relop` is called **unconditionally
at five sites**. ⇒ **RTX-6b is in the OPPOSITE REGIME from RTX-6** — no guard means the callee's own
dispatch is the whole story and **0(g) as originally written (s209b) applies unmodified**, so the
textually-first arms may genuinely be live there. **Do not carry RTX-6's conclusion across.**

---

## ▶ NEXT SESSION — DO THESE IN ORDER

1. **Push** (needs a credential), then satisfy the s202 ancestry check
   `git rev-list --count origin/main..HEAD == 0` and only then leave RTX-6-ICN's `[x]` standing.
2. **`bash scripts/test_icon_all_rungs.sh` — expect 252/11/30.** Re-derive, never hand-copy.
3. **Step 0(h)** — `grep -l "Rung:.*<RUNG>" FINDING-*.md` before opening anything.
4. **RTX-6b-ICN** (`rt_binop_overload` 141 + `rt_jct_relop` 163). The 0(g)-second-half recon is DONE and
   recorded above: **no guard ⇒ measure the callee's internal arms directly.** ⚠ `rt_cmp_d` is already
   asm under the ARITH gate ⇒ **ISOLATION ARM REQUIRED** (s204: a family gate's error has no known sign
   and no known bound). ⚠ `rt_num_arith` is SN4-RTX's.
5. **Benchmark with `scripts/bench_rtx_3arm.sh` and an `&time` self-timed program.** Author it from
   `corpus/benchmarks/icon/rtx/bench_icnnum_isolate.icn` — **hoist allocation OUT of the timed loop**,
   or the harness will refuse to grade it (see §Allocator below).

---

## ⚠ THREE THINGS I WOULD NOT WANT INHERITED SILENTLY

1. **PROTOCOL DEVIATION.** `RTX-CLAIMS.md` requires the check-out **pushed before the work**. Without a
   credential the claim was **committed** ahead of the port (`4c952538` precedes `eb81508d`) but not
   pushed ahead of it. The ordering is honest in the history; **the protective property — another
   session seeing the claim before spending itself — was NOT obtained.** An empty correcting commit was
   added because `4c952538`'s own message wrongly says "pushed".
2. **A PARALLEL SESSION PUSHED MID-FLIGHT AND THE REBASE WAS CLEAN.** The Z4/ζ ladder landed
   `57a7b598` (templates + `x86_asm.h` + `.s` artifacts). **Zero file overlap** with this ladder
   (`rt.c`, `rtx_*.S`, `Makefile`) — the three-way concurrency contract working exactly as §7 specifies.
   Icon re-derives **252/11/30 on the combined tree.** ⚠ The rebase **changed my commit hash**, so
   `56b8752d` → `eb81508d` was re-pointed across three docs; a hash written into prose before a rebase
   is the stale-reference class RULES.md s47 names.
3. **THE ALLOCATOR WAS THE BIMODALITY, NOT THE BOX.** The first benchmark's arms were bimodal
   (PRISTINE 1180 1684 1153 1672 1301) and the s209 precondition correctly refused it. **More rounds
   cannot fix it — the spread is multiplicative.** Hoisting the per-iteration `string(i)` allocation out
   of the loop took spreads **1.57× → 1.04×**. ⇒ **suspect the allocator in the window before suspecting
   the box.** This partially retro-qualifies s209's "25% spread inside a single arm" attribution.

---

## ⛔ STILL LON'S, UNTOUCHED BY THIS SESSION

- **RTX-0-RULING(a)** symbol ownership · **RTX-0-RULING(b)** SCAN destination — **still blocks
  RTX-2-ICN**, since the recommended `rt_substr` is in that family.
- **`rt_subscript_var`** — Icon's #1 exported run-phase symbol (315k), checked out to SN4-RTX.
- **Your open item #1 (dynamic-count allocation): this session is a FIFTH falsification of static
  ranking, and a new kind.** `rt_coerce_num2_d`'s 209 static sites are real AND its 240k dynamic count
  is real, **yet its two textually-first arms are unreachable.** Static counts cannot see arm liveness
  even when the dynamic count is correct. ⇒ **dynamic-count allocation as you proposed, PLUS
  arm-liveness as a rung PRECONDITION rather than a rung step.**
- **RTX-0b second half** — `scrip --run p.icn -n8` ⇒ `cannot open '-n8'`; **mode 3 does not forward
  argv.** N is edited into the source.

---

## FILES

**SCRIP** (`eb81508d`): new `src/runtime/rtx/rtx_icnnum.S` · `src/runtime/rt/rt.c` (`rt_coerce_num2_d`
→ `c_rt_coerce_num2_d`; `rt_parse_num_d` untouched and still `static`) · `src/runtime/rtx/rtx_init.c`
(gate) · `Makefile` (`RT_PIC_SRCS`). **Zero templates, zero `x86_asm.h` ⇒ no `.s` regen owed.**
**corpus** (`90559c6c`): `benchmarks/icon/rtx/` — two self-timed programs + README.
**.github** (`10da9696`): the FINDING · `GOAL-ICON-RTX.md` cursor + RTX-6 closed + RTX-6b minted ·
`RTX-CLAIMS.md` rows + message board.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
