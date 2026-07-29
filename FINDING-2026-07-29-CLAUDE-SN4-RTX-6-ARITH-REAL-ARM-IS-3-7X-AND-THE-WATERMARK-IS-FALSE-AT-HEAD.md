# FINDING — s210 (2026-07-29) — RTX-6 ARITH: `rt_add`/`rt_sub`/`rt_mul` ported. The real-real arm is **3.710×**. And the ladder's watermark is **FALSE AT HEAD**.

**Ladder:** SN4-RTX · **Rung:** RTX-6 (ARITH) · **Gate:** `SCRIP_RTX_ARITH` · **RT_OPT=`-O0`**
**Symbols:** `rt_add` `rt_sub` `rt_mul` (SN4-exclusive; C bodies → `c_rt_*` same commit)
**Templates touched: ZERO.** `x86_asm.h` untouched. ⇒ no `.s` regen owed, concurrency-safe vs the ζ ladder.

---

## 1. THE PORT

Two fast arms in `src/runtime/rtx/rtx_arith.S`, everything else tail-jumps to the untouched C body
with args in place.

| path | asm insns (incl. the 2-insn gate C never pays) | C insns |
|---|---:|---:|
| int-int | **10** | ~30 + stack-protector canary |
| real-real | **13** | 124-insn function containing a **`setjmp` call** + an `rt_num_arith_impl` call |

**WHY BYPASSING `setjmp` ON THE REAL ARM IS SOUND — argued, not assumed.** The C entry
(`arithmetic.c` `RT_BINOP_ENTRY`) arms a `setjmp` so a `core_runtime_error` deep inside can longjmp
out as FAILDESCR. For two `DT_R` operands that path is provably unreachable for ADD/SUB/MUL:
`to_real` (`core/core.c:2010`) returns `v.r` directly for `DT_R` without calling anything, `csop`
is 0, both `IS_REAL_fn` are 1 so `anyf` is 1, and the switch arm is a bare `REALVAL(ld op rd)` — no
zero test, no `fmod`, no `pow`, no error call. **DIV/MOD/POW are deliberately NOT ported** for
exactly this reason. The `g_core_errjmp_n` increment/decrement pair is restored before return, so
skipping it is not observable.

---

## 2. ⭐ THE HEADLINE — AND MY OWN PRE-STATED BAND WAS FALSIFIED

Pre-stated before writing any asm (s187/s204 rule): `arith_mixed` **1.40×–2.20×**, int-only
**1.05×–1.35×**. **The real number is 3.710×. I UNDER-predicted by more than a factor of 1.7** — I
underestimated what `setjmp` plus an `-O0` callee frame costs per call. Recording this because the
ladder's pre-stating rule exists to make predictions falsifiable in BOTH directions, and every prior
instance in this file has been an over-prediction.

3-arm interleaved harness (`bench_rtx_3arm.sh`), r=4, round 1 discarded, RT_OPT=`-O0`:

| program | shape | **ON/PRISTINE** | ON/OFF (legacy 2-arm) | OFF/PRISTINE (gate tax) |
|---|---|---|---|---|
| `arith_mixed` | 80,000,001 calls, 50/50 int/real | **3.710×** | 3.931× | 0.944× |
| `arith_int` (new) | 100,000,000 calls, 100% int | **1.107×** | 1.397× | **0.793×** |

Raw samples (the harness prints them so an intra-arm spread cannot hide behind a median):
`arith_mixed` ON `576 534 562` vs PRISTINE `2085 2115 1985` — **non-overlapping by a wide margin**;
worst intra-arm spread 1.079× against a 3.710× gap, so the arm-stability precondition passes.

**The split is mechanistic, not mysterious:** the real arm deletes an entire `setjmp` + impl frame
(huge); the int arm only sheds `-O0` frame ceremony, because the C entry *already* had an inline
int-int fast arm (modest). The disassembly predicts exactly this ratio shape.

### ⭐⭐ `arith_int` IS THE STRONGEST CONFIRMATION OF s209's THESIS YET
Legacy two-arm reads **1.397×** where the honest answer is **1.107×**, because OFF/PRISTINE is
**0.793×** — a 100M-call family pays the gate compare + taken branch + PLT hop on *every* call. s209
measured the tax at 1.002×/0.905× and correctly refused to generalize it; here it is **21%**. ⇒ the
tax is not a constant to subtract, it scales with call count, and on a hot family it is enormous.

---

## 3. ⛔⛔ THE WATERMARK IS FALSE AT HEAD — AND IT IS NOT MINE

**Recorded across the whole ladder:** m3 314/1 · m4 309/4 · DIVERGE=3.
**MEASURED THIS SESSION at HEAD (`b17e263a`):** **m3 268/47 · m4 267/46 · DIVERGE=2.**

**PROVEN NOT MINE, three ways identical:** gate ON, gate OFF, and a **genuinely pristine `.so` built
with the port stashed out** all produce 268/47 · 267/46 · DIVERGE=2, byte-for-byte the same counts.

**THE FAILURES ARE REAL — I CHECKED, AND I WAS WRONG TWICE ON THE WAY.**
- First guess: environment/layout gap. **Wrong.**
- Second guess: missing `.ref` files — six sampled programs showed `REF-MISSING`. **Wrong, and the
  error is instructive:** my `find` matched SCRIP's `test/snobol4/**` copies, but the crosscheck
  reads `$CORPUS/crosscheck` (`test_crosscheck_snobol4.sh:61`). The real corpus has 316 `.sno` and
  504 `.ref` — the refs were there all along. **A program can exist twice in this tree, and the copy
  you grep is not necessarily the copy the gate runs.**
- Ground truth: `patterns/047_pat_rtab` **segfaults (rc=139)**; `strings/word1` **segfaults when fed
  its real `.input`**. Genuine crashes.

⛔ **I DO NOT ASSERT A CULPRIT.** Having been wrong twice in one diagnosis, naming a cause on the
third guess is exactly the s209 mistake (a mechanically plausible story built on one number).
What is established: the number, that it is not the RTX ladder's, and that it is a real crash class.
The obvious suspect is the parallel ζ ladder — **that is a hypothesis, not a finding.** RULES'
MONITOR-FIRST rule owns the next step, and s208 already logged three benchmark segfaults
(`roman` · `pattern_bt` · `string_pattern`) that nobody chased; this looks like the same class,
now 46 programs wide.

**CONSEQUENCE FOR THE LADDER, STATED PLAINLY: every rung since the watermark drifted has gated
"no regression" against a baseline that does not exist.** The concurrency contract named this exact
risk — *"THE WATERMARK ITSELF IS SHARED STATE… re-prove at session start"* — and this session proves
the risk is now realised, not theoretical. **A three-way ON/OFF/PRISTINE identity (what I did here)
is the substitute that still works when the absolute baseline is untrustworthy: it is a
DIFFERENTIAL claim and it survives a broken watermark.** Recommend every ladder adopt it until the
baseline is restored.

⚠ **PROTOCOL DEVIATION, MINE:** I ported BEFORE re-proving the watermark, contrary to §7. The
three-way identity recovered the no-regression claim, but only by luck of the port being clean — had
it not been, I could not have separated my breakage from the inherited breakage. **Re-prove first.**

---

## 4. ⭐ s206's ARITH CENSUS IS STALE AND ITS CONCLUSION IS INVERTED

RTX-6's own rung text says an int-int port *"grades a guaranteed 1.000×"* on `arith_mixed`, resting
on s206's interposer census: **100% DT_R+DT_R**.

**Measured at HEAD (`scripts/util_rtx_arith_census.c`, committed this session):**

| program | `rt_add` calls | at 2× bound | real-real | int-int |
|---|---:|---:|---|---|
| `arith_mixed` | 80,000,001 | 160,000,001 (**exact 1:1**, +1 preserved) | 50% | 50% |
| `arith_loop` | 1,000,000 | — | 0% | 100% |

**s207's own collapse-to-one-call pushed the integer loop counter into the runtime**, doubling the
call count and creating a 40M-call int-int population that could not have existed when s206 measured.
⇒ **NINTH PHANTOM SHAPE — THE STALE CENSUS: a measurement that was true, was recorded correctly, and
was invalidated by a LATER rung on the SAME ladder.** RTX-7's decay (s208) required an *unrelated*
rung to succeed; this one is self-inflicted, one rung apart, and therefore likelier to recur.
**A census has a shelf life. Re-run it, do not cite it.**

Both benchmark headers are now stale prose: `arith_mixed.sno`'s own comment asserts *"arith_loop
calls rt_num_arith ZERO times… SCRIP's emitter inlines integer arithmetic."* It calls `rt_add` a
million times.

---

## 5. ⚠ `arith_loop` CANNOT FALSIFY THE INT ARM — A FIXED POINT THAT ABSORBS THE ERROR

The falsification build (int arm corrupted to `a.i + b.i + 1`, real arm `addsd`→`subsd`) produced:

| program | broken asm, gate ON | gate OFF |
|---|---|---|
| `arith_mixed` | `-30000001` ⭐ caught | `60000001` ✅ |
| `arith_loop` | **`1000000` — UNCHANGED** ⛔ | `1000000` |
| direct probe `2+3` / `2.5+1.25` | `6` / `1.25` ⭐ caught | `5` / `3.75` ✅ |

`arith_loop` is `N = N + 1` under `LT(N, 1000000)`: corrupt the add and N simply steps by 2 and
**still lands exactly on the bound**. The output is a fixed point that absorbs the corruption.
⇒ **It looks like an ARITH gate and is worth nothing as one.** Same class as §7 step 2b's unmoved
battery, but nastier: the battery here is *on-family and hot* (1M calls) and still proves nothing.
**A falsification target must be OUTPUT-SENSITIVE to the corrupted value, not merely reach it.**
The new `arith_int.sno` inherits this defect by design (same shape) — it is a TIMING benchmark only;
falsify on `arith_mixed` or the direct probe.

---

## 6. GATES

✅ Falsification **two-sided on BOTH arms** (broken asm: ON wrong / OFF correct; restored: correct)
✅ RTX unit **21/21 misc · 36/36 alloc · 8426/0 STR**
✅ Prolog crosscheck **189/0** at gate ON *and* OFF · Icon **4/0** at gate ON *and* OFF (shared
   `arithmetic.c` — mandatory, and these DO move under the probe for arithmetic-reaching programs)
✅ SNOBOL4 crosscheck **identical across ON / OFF / PRISTINE** (268/47 · 267/46 · DIVERGE=2)
⛔ Absolute watermark **NOT met** — see §3; it is unmeetable at HEAD by any build, including pristine.
⚠ NOT RUN: Milestone-1 beauty oracle md5 (needs the x64 clone; unreproduced since RTX-3 for a
   recorded reason).

---

## 7. WHAT THE NEXT SESSION SHOULD DO

1. **The watermark, via the MONITOR, per RULES — not by guesswork.** It blocks every ladder's
   absolute gate. 46 programs, at least one clean segv repro (`047_pat_rtab`, no `.input` needed).
2. **Do NOT port DIV/MOD/POW** into these arms without the zero-test/`fmod`/`pow` work; the soundness
   argument in §1 explicitly does not cover them.
3. `rt_num_arith` itself (`OUT:SN4-RTX:s205`) remains unported and is Prolog's arithmetic path
   (`by_name_dispatch.c`) — a separate 0(d) is owed before touching it.
4. The real-real SSE arm generalises: `rt_cmp_d` already has an int arm and could take a `ucomisd`
   real arm by the same argument, inside the same gate, with no `x86_asm.h` change.

---

## 8. ADDENDUM — ONE ALTERNATIVE EXPLANATION RULED OUT (still no culprit named)

Before leaving the watermark to the next session, the cheapest competing hypothesis was tested:
**were the 46 extra failures simply NEW tests, added ahead of the feature they exercise?** If so
there is no regression at all and the recorded watermark was merely taken on a smaller suite.

**RULED OUT.** The failing programs are OLD:

| program | added |
|---|---|
| `crosscheck/strings/word1.sno` | `ff2af249` 2026-03-11 |
| `crosscheck/control/expr_eval.sno` | `ce148ba7` 2026-03-11 |
| `crosscheck/patterns/047_pat_rtab.sno` | `3d321764` 2026-03-13 |
| `crosscheck/patterns/120_pat_calc_add.sno` | `b794c7c2` 2026-04-29 |

All predate the 314/1 watermark's own sessions by months. ⇒ **these are long-standing tests that
used to pass and now segfault. It is a REGRESSION.**

⛔ **STILL NO CULPRIT ASSERTED.** This narrows the question, it does not answer it. What is now
established: (i) the failures are real crashes, (ii) they are not the RTX ladder's, (iii) they are
not corpus growth. The next session inherits a well-posed bisect: the suite passed at the watermark's
recording and fails at `b17e263a`, with `crosscheck/patterns/047_pat_rtab.sno` as a clean segv repro
needing no `.input`. **Per RULES, the monitor owns that hunt, not a reading of the diff.**
