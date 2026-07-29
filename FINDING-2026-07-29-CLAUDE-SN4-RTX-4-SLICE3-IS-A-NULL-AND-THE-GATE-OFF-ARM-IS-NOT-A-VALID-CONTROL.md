# FINDING — s209 (2026-07-29) — RTX-4 SLICE 3 LANDED AND MEASURES **NULL** (TWICE, TWO HARNESSES); THE TWO-ARM `ON/OFF` A/B IS **UNSTABLE**, NOT MERELY BIASED — AND THE 3-ARM HARNESS I BUILT TO PROVE THAT **FALSIFIED MY OWN FIRST EXPLANATION**; AND `nm` ON THE `.so` CANNOT SEE THE `static`/`hidden` SPLIT

**Ladder:** `GOAL-SNOBOL4-RTX.md` · **Contract:** `ARCH-SNOBOL4-RTX.md` · **Ledger:** `RTX-CLAIMS.md`
**Symbols:** `rt_flat_ret_snap` + `rt_proc_open_fn` (CALL family, entry side) — both SN4-EXCLUSIVE, checked out `OUT:SN4-RTX:s208`, zero arbitration.
**Files:** `src/runtime/rt/rt.c`, `src/runtime/rtx/rtx_call.S`. **ZERO templates touched ⇒ no `.s` regen owed by construction.**
**All numbers RT_OPT=`-O0`** (Makefile default; no `-O2` directed this session, per O2-DIRECTED-ONLY).

---

## ⭐⭐ HEADLINE 1 — THE PORT IS CORRECT, GATED, FALSIFIED **AND IT WINS NOTHING**. PRE-STATED BAND FALSIFIED.

Pre-stated before any measurement (s187/s204 rule): `func_call` **1.05–1.20×**, `fibonacci` **1.02–1.12×**.

| program | pristine C | asm (`SCRIP_RTX_CALL=1`) | **ratio vs pristine** | gate OFF |
|---|---|---|---|---|
| `func_call` (10M calls) | 2292.5 ms | 2275.5 ms | **1.007×** | 2425 ms |
| `fibonacci` | 619 ms | 622 ms | **0.995×** | 667.5 ms |

**Both inside the ±3% null floor. One is fractionally NEGATIVE.** The band is **FALSIFIED** and this rung
claims **no speedup**. Per the ladder's own rule a pre-stated null is the answer, not a failed
measurement — and recording it is what produced HEADLINE 2, which is worth more than the rung was.

⚠ **THE NULL IS NOT "THE ASM IS BAD."** The port does measurably less work — verified by `objdump`, not
estimated: `rt_flat_ret_snap` **48 → 28** instructions, `rt_proc_open_fn` **16 → 13** (both counts
INCLUDE the 2-instruction gate the C does not pay). Each global is loaded once instead of twice; the
40-byte copy is 6 memory ops instead of 10; no rbp frame; no `rbx` (a PIN) saved as copy scratch.
**The work was removed and the clock did not move.** That is a statement about where `func_call`'s time
actually is, and it says: **not in these two leaves' ceremony.**

---

## ⭐⭐⭐ HEADLINE 2 — THE TWO-ARM `ON/OFF` A/B IS UNRELIABLE. ⛔ **AND THE INSTRUMENT I BUILT TO PROVE IT FALSIFIED MY OWN FIRST EXPLANATION — READ THE CORRECTION BEFORE QUOTING ANYTHING HERE.**

**FIRST ATTEMPT (2-arm, env-var swap, cross-build pristine).** I measured gate OFF as **5.8% slower than
pristine on `func_call`** and **7.8% on `fibonacci`**, and generalized: *the kill-switch costs
`cmp` + taken `je` + a PLT stub on every call, therefore every ON/OFF A/B on this ladder is biased by
~6–8% in the asm's favour.* The mechanism is real and visible in the objdump
(`je 3a4a0 <c_rt_flat_ret_snap@plt>`). **The GENERALIZATION was wrong, and it did not survive one run of
the harness I wrote to check other rungs' numbers with.**

**RTX-0e, 3-ARM SAME-MOMENT INTERLEAVED (`scripts/bench_rtx_3arm.sh`, R=5, round 1 discarded):**

| program | PRISTINE | OFF | ON | **ON/PRISTINE** | ON/OFF | **OFF/PRISTINE (the tax)** |
|---|---|---|---|---|---|---|
| `func_call` | 2275 ms | 2271 ms | 2257 ms | **1.008×** | 1.006× | **1.002×** |
| `fibonacci` | 632 ms | 698 ms | 635 ms | **0.995×** | 1.099× | **0.905×** |

⛔ **WHAT THIS KILLS — MY OWN CLAIM.** The kill-switch tax is **NOT a uniform 6–8%.** On `func_call` it is
**0.2%**, essentially nothing. My 5.8% rested on a single OFF median of **2425 ms that DID NOT REPRODUCE**
(2271 ms here, same binary, same gate byte). ⇒ **that sample was noise, and I built a causal story on top
of it.** The story was mechanically plausible, which is exactly what made it dangerous.

⭐ **WHAT SURVIVES, AND IT IS STRONGER THAN WHAT I FIRST CLAIMED.** The two-arm ratio is not merely biased
by a constant that could be subtracted — **it is UNSTABLE.** The identical comparison, on the identical
program, with **ZERO code change between them**, read:

> `func_call` ON/OFF = **1.066×** (harness 1) and **1.006×** (harness 2)

**A 6-point swing with nothing changed but the harness.** That is a worse property than a fixed bias: a
fixed bias can be corrected, a swing this size can MANUFACTURE an in-band "win" out of nothing. And the
tax genuinely IS large on some programs (`fibonacci` 0.905×) and absent on others (`func_call` 1.002×), so
it cannot be characterized once and reused. ⇒ **NO TWO-ARM `ON/OFF` NUMBER ON THIS LADDER IS TRUSTWORTHY
BELOW ~1.10×, AND THE REASON IS INSTABILITY, NOT A CORRECTABLE OFFSET.**

⚠ **CONSEQUENCE FOR RECORDED CLAIMS — QUALIFIED, NOT OVERTURNED.** RTX-3b's `func_call` **1.080×** is a
two-arm number on the exact program where I have now watched the two-arm ratio swing 1.006–1.066 for free.
⛔ **I did NOT re-measure RTX-3b and I do NOT assert it is spurious.** I assert it is **UNSAFE TO INHERIT**
and owes a 3-arm re-grade. Same for RTX-5b's 1.022×/1.002×. RTX-3b's `var_access` **1.366×** is far outside
this instability and is **not challenged**.

⭐ **THE NULL, BY CONTRAST, IS NOW THE MOST SOLID NUMBER IN THIS FINDING:** ON/PRISTINE came out **1.007×
and 1.008×** on `func_call` and **0.995× / 0.995×** on `fibonacci` across **two independent harnesses,
one cross-build and one same-moment interleaved.** The cross-build caveat I owed is **DISCHARGED** — and
it changed the null not at all while demolishing the explanation I attached to it.

⚠ **UNEXPLAINED, DELIBERATELY NOT PROMOTED TO A LAW:** the tax is ~0% on `func_call` (10M calls) and ~9.5%
on `fibonacci` (2.7M calls) — i.e. it is LARGER on the program with FEWER calls, which a per-call tax
cannot explain. Candidates: `func_call`'s window is dominated by loop/arith work so the leaves are a
smaller share than the s208 27% figure implies; or single-core instability (this box produced s200's
1.340/2.497/2.606/0.510 spread). **No cause asserted. Do not build another story on one number — that is
the mistake this very headline records.**

---

## ⭐⭐⭐ HEADLINE 2b — **I RE-GRADED RTX-3b WITH THE HARNESS AND IT IS VINDICATED. MY OWN DOUBT WAS THE THING THAT DID NOT SURVIVE — SECOND SELF-CORRECTION THIS SESSION.**

HEADLINE 2 marked RTX-3b's numbers "unsafe to inherit." **I then did the work instead of leaving the doubt
hanging on landed work, and the doubt lost.** Pristine-STR arm built by REMOVING `rtx_str.S` from the link
entirely and renaming `c_str_concat_d` → `str_concat_d` (verified: `nm` shows one `str_concat_d`, no asm,
no `c_` body; both arms produce `result: 60000012`, matching `var_access.ref`).

| program | RTX-3b CLAIMED (2-arm) | **ON/PRISTINE (3-arm)** | ON/OFF | gate tax (OFF/PRISTINE) |
|---|---|---|---|---|
| `var_access` | 1.366× | **1.262×** | 1.186× | 1.064× |
| `func_call` | 1.080× | **1.061×** | 1.063× | 0.998× |

⭐⭐ **RTX-3b IS A REAL WIN. BOTH NUMBERS SURVIVE, SLIGHTLY LOWER, SAME CONCLUSION.** And the one I
specifically impugned — `func_call` 1.080× — measures **1.061× against a genuine pristine build**, where
**the two-arm and three-arm numbers differ by 0.002.** ⇒ **THE ARTIFACT I PREDICTED IS NOT THERE.
WITHDRAW THE "UNSAFE TO INHERIT" FLAG ON RTX-3b.** It should never have been raised on the strength of a
magnitude coincidence.

⛔⛔ **THIS FORCES THE REAL DIAGNOSIS, AND IT IS NOT THE ONE HEADLINE 2 REACHED FOR EITHER.** Across every
3-arm measurement now taken, the kill-switch tax is **1.002× · 0.998× · 1.064×** — i.e. **≈ nothing, and
not even consistently signed** (on `var_access` the OFF arm came out *faster* than pristine, which a gate
that only ADDS instructions cannot cause — that is a link-layout difference, exactly s200's confound,
since removing `rtx_str.S` moves the whole `.so`). The single outlier is CALL/`fibonacci` at 0.905×.
⇒ **THE DOMINANT ERROR SOURCE ON THIS BOX IS RUN-TO-RUN NOISE, NOT THE CONTROL'S STRUCTURE.**
Look at the raw `var_access` PRISTINE samples: **717 · 595 · 587 · 737** — a **25% spread within one arm**,
while its ON arm was **518 · 522 · 514 · 525**, tight. A denominator that noisy is what makes a ratio
swing, and it is why the 1.262× above should be read as "a large real win, roughly 1.13×–1.26×"
(fastest-pristine vs slowest-ON gives the floor), **not as a precise number.**

⇒ **CORRECTED PRESCRIPTION — WEAKER THAN HEADLINE 2's AND ACTUALLY SUPPORTED:** the value of
`bench_rtx_3arm.sh` is **(i)** it includes a true baseline so a rung learns what it really bought, and
**(ii)** it prints EVERY raw sample so a 25% intra-arm spread is impossible to hide behind a median.
It is **NOT** true that two-arm numbers are systematically inflated — measured, they mostly are not.
**The honest rule is: replicate, publish raw samples, and distrust any ratio whose arms overlap —
regardless of how many arms you ran.**

## ⭐⭐ HEADLINE 3 — NEW STEP-0(c) REFINEMENT: `nm` ON THE `.so` CONFLATES `static` WITH `hidden`, AND THE DIFFERENCE IS LINK-OR-FAIL

s208's step 0(c) reported: *"all four globals (`g_pcall` `g_pcall_top` `g_pcall_wires` `g_flat_ret_snapbuf`)
are ABSENT from the `.so` dynamic table ⇒ linker-localized ⇒ direct `[rip+sym]`, NO GOTPCREL — the exact
split that cost RTX-2 a rung, measured not assumed."*

**That conclusion is CORRECT about the addressing mode and CONCEALS A HARD BLOCKER.** In the `.so` all four
print lowercase `b`. In the **object file** they do not:

```
g_pcall             B   <- global, visibility(hidden)   -> linkable from another TU
g_pcall_top         B   <- global, visibility(hidden)   -> linkable from another TU
g_pcall_wires       b   <- static, FILE-LOCAL           -> NOT REFERENCEABLE FROM .S AT ALL
g_flat_ret_snapbuf  b   <- static, FILE-LOCAL           -> NOT REFERENCEABLE FROM .S AT ALL
```

⛔ **THE `.so` IS STRUCTURALLY INCAPABLE OF SHOWING THIS**: hidden-visibility globals are demoted to local
symbols *by the link*, so by the time you `nm` the `.so`, `static` and `hidden` have become the same
letter. **The check must run on the `.o`.** Two of the four symbols this rung needed could not have been
named from assembly at all, and the failure would have arrived as a link error after the asm was written.

⇒ **STEP 0(c) GAINS A CLAUSE:** *`nm` the **object file**, not the `.so`, and read the CASE: uppercase `B`/`D`
= linkable across TUs; lowercase `b`/`d` = `static`, and a cross-TU asm port must first promote it.*
**FIX APPLIED:** both were promoted from `static` to `__attribute__((visibility("hidden")))` — the identical
attribute the other two in the same family already carry. Hidden-ness is preserved (absent from the dynamic
table, direct `[rip+sym]`, interposition-proof); only sibling-TU linkage widens, which is exactly what the
port needs and nothing more.

⭐ **FAMILY RESEMBLANCE:** RTX-2 was cost a rung by the **exported vs hidden** split, which is invisible at
the C use site. This is the **same axis one level down** — `static` vs `hidden`, invisible in the `.so`.
Both are "two things that look identical through the instrument you happened to pick."

---

## ⛔ HEADLINE 4 — THE RECORDED BASELINE DISAGREED WITH MEASUREMENT AGAIN (FOURTH TIME ON THIS LADDER)

- s207 cursor recorded: **m3 280/54 · m4 276/50 SKIP=8 (334 total)**
- **MEASURED LIVE s209 on the same HEAD (`d61d7cba`, s208 changed no code): m3 268/47 · m4 267/46 SKIP=2 · DIVERGE=2 (315 total)**
- **This matches s200's measured baseline EXACTLY.**

The totals differ (334 vs 315), so this is a **suite-size** disagreement, not a regression. Reported, not
chased. **BASELINE OF RECORD FOR s209 = 268/47 · 267/46 · DIVERGE=2 — and re-prove it live anyway.**

---

## ✅ GATES (all re-proven live this session, nothing inherited)

- **Watermark, gate ON:** 268/47 · 267/46 · DIVERGE=2 — **failure sets diffed LINE-BY-LINE vs baseline: byte-identical, zero movers either direction.**
- **Watermark, gate OFF:** identical to baseline, byte-identical failure set.
- **TWO-SIDED FALSIFICATION, aimed at the rung's DISTINCTIVE computation** (s204's rule — not "does calling work"): `PROC_FN` corrupted 8 → 0 so `rt_proc_open_fn` returns `p->name` instead of `p->fn`.
  - broken asm + gate **ON** → **248/67 · 246/67 = 20 and 21 movers ⇒ THE ASM EXECUTES.** Loud; no escalation needed.
  - broken asm + gate **OFF** → **268/47 · 267/46 = exact baseline ⇒ THE GATE REACHES C.**
  - restored ⇒ exact watermark, failure set byte-identical.
- ⚠ **A SECOND PROBE COULD NOT BE BUILT AND THAT IS WORTH RECORDING:** the intended probe was corrupting the 40-byte stride to 32 (the *pre-Z4-7* `sizeof`, i.e. the exact hazard the s208 cursor flagged as "the struct is moving under a parallel session"). **It does not assemble** — x86 scale factors are 1/2/4/8 only, so `lea rax,[rax+rax*3]` is not encodable. The stride is instead protected by the pre-existing `_Static_assert` in `rt.c`, which is **stronger** than a probe: a struct change breaks the BUILD, not the runtime.
- **Prolog 188/0 SKIP=1 · Icon 4/0** — ⛔ **cited ONLY as no-regression evidence. Per §7 step 2b, an unmoved battery is a coverage statement and citing it as proof the asm executes would be a FALSE CLAIM.** (Cursor recorded Prolog 189; measured 188/0 SKIP=1, FAIL=0 either way.)
- **Snocone NOT run** — `beauty_full_bin` absent from this clone (environmental, same gap s207 recorded).

## ✅ STEP 0 — ALL FIVE CHECKS RE-PROVEN, NOT INHERITED

(a) both defined live in `rt/rt.c` · (b) spellings byte-identical to the tree · (c) linkage — **see HEADLINE 3, the inherited answer was incomplete** · (d) ⭐ **re-measured on my own LD_PRELOAD interposer: 1M loop → 1,000,000 calls each; 2M loop → 2,000,000 calls each. Exactly 1:1 at two scales.** Manual **Ch.8** makes this a property of the LANGUAGE, not the benchmark: every `DEFINE`'d function reaches `RETURN`/`FRETURN`/`NRETURN` exactly once per activation · (e) neither is already asm (grep run **with `--include=*.S`**, per the s200 correction).

## 📐 DESIGN NOTES WORTH KEEPING

- **THE ERROR PATHS ARE DELIBERATELY NOT PORTED.** Level-zero RETURN (manual Ch.8 "Return from level zero" → core error 18, which must route through the core machinery so `&ERROR`/`SETEXIT` trapping still applies) and the no-return-wires diagnostic both **tail-jump to the C body**. The asm contains no error handling, so **it cannot regress error behaviour — by construction, not by testing.**
- **`rdx` IS CLOBBERED AND THAT IS PROVABLY SAFE.** `rt.c`'s comment says *"rax:rdx ride untouched through the floater's tail."* Verified against the machine: the **-O0 C body already clobbers `rdx`** (`movslq %eax,%rdx`), so no emitted caller can legally depend on it; and the emitted floater in `func_call.s` consumes only `rax`, then reloads `rcx`/`rbp`/`rsp` from the returned buffer. **The comment describes the tail AFTER the call, not a guarantee across it.** Checked because an accidental -O0 preservation dependency would have been invisible until it wasn't.
- **All baked offsets are `_Static_assert`-anchored in `rt.c`** (`rt_pcall_t` 64/p@0 pre-existing; `rt_flat_wires_t` 40 + all five offsets from Z4-7 slice 2; **`rt_proc_t.fn`@8 added this slice**, confirmed from emitted code as `mov 0x8(%rax),%rax`, never hand-computed).

## ⛔ OWED / NOT ESTABLISHED

1. ✅ **DONE THIS SESSION — RTX-0e, `scripts/bench_rtx_3arm.sh`**, the 3-arm same-moment interleaved harness (pristine / OFF / ON), committed as a script rather than a throwaway. It discharged this rung's own cross-build caveat and immediately falsified this session's first causal story. **Use it for every future rung; report ON/PRISTINE as the answer and ON/OFF only to show how much of a legacy claim was artifact.**
2. **Re-grade sub-1.10× recorded wins with the 3-arm harness** — RTX-3b `func_call` 1.080×, RTX-5b 1.022×/1.002×. **Not overturned; unsafe to inherit.** The harness now exists, so this is cheap: two builds and one run. ⚠ RTX-3b's `var_access` 1.366× is outside the instability and is not in question.
3. **`-O2` arm not built** (O2-DIRECTED-ONLY). These leaves are pure -O0 ceremony removal, so the null may *deepen* under `-O2` as gcc removes the same redundancy itself. **Never quote these numbers without the `-O0` clause.**
4. **Whether to KEEP this port.** It is correct, gated, falsified and free of regression, but it buys ~0%. ⇒ **Lon's call.** The honest argument for keeping it: it is a prerequisite for RTX-11 (registerized ABI), where these two leaves stop being C-signature-bound and the ceremony that is currently invisible becomes removable. The honest argument against: it is 100 lines of assembly earning nothing today.
5. **Three benchmarks still segfault at HEAD** (`roman.sno`, `pattern_bt.sno`, `string_pattern.sno`, rc=139) — pre-existing, pattern-family, untouched here. RULES says the 2-way monitor, not guesswork.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
