# FINDING — s216 (2026-07-29): A port passed every step-0 check including a clean 0(d), and was still vacuous. The instrument was landed; the asm was not.

**Session goal as named by Lon:** "Replace SCRIP's C runtime with ASM code. Continue."
**Outcome:** ZERO symbols converted. One additive script, one contract amendment, two struck symbol names. The negative result is the deliverable and it is not a consolation prize — it names a gap in the checklist that has now cost the ladder two sessions (s213's reverted batch, and this one).

---

## 1. What was built, and why it is reverted

`rt_cap_push` (`pattern_match.c:747`) was ported to `src/runtime/rtx/rtx_match.S` behind the existing `SCRIP_RTX_MATCH` gate, C body renamed `c_rt_cap_push`:

- 11-instruction hot path, zero calls, `g_cap_gen` read via `@GOTPCREL` (exported — the s214 rule)
- **BAIL-BEFORE-MUTATE** honored on both cold arms (first-use `buf == NULL`; buffer-full grow), each reached with zero stores retired, because the C fallback re-executes the whole body from scratch
- Built clean; output **byte-identical to pre-port C under gate ON and under gate OFF**

It is **reverted** (`git checkout`, tree 0 modified, verified by **grep AND md5** per s212's interrupted-revert lesson). Reason: **it never executed.**

| measurement (`json.sno` + `twitter.json`, m3, gate ON) | value |
|---|---|
| `rt_cap_push` entries | **57,578** |
| bailed to `c_rt_cap_push` | **57,578** |
| **commits handled by asm** | **0** |
| `rt_ws_alloc` calls | **67,583** |

`rt_ws_alloc` exceeding the push count proves the shape: the ζ capture slot arrives `ZC_INIT_ZERO`-fresh, so **allocation is the common case, not the edge**. The arm I ported is the arm this tree never takes. ARCH §7 forbids landing an RTX family without two-sided falsification, and this port **cannot be falsified on any workload in the tree** — so it must not land.

---

## 2. ⭐⭐ The finding: step 0(d) passed in full and was insufficient

0(d) (minted s188) requires the symbol be executed in the window the rung will move, measured at two counts, with the count proven to scale. `rt_cap_push` satisfied **every** clause:

- **57,578 dynamic calls** — not a static count, measured with an `LD_PRELOAD` interposer
- **hottest unported symbol in its family** on the ladder's own designated defer workload
- **scaling proven EXACTLY 2.00×** on a structurally-doubled input, across all 17 measured symbols
- re-measured, not cited (s210's rule)

All true. The port was still vacuous.

**Cause: 0(d) counts entries to a SYMBOL. A gated RTX port is a symbol with ARMS, and the asm covers only the arm the author chose.** So 0(d) can pass in full while the ported arm is dead.

**The bitter part: s215 minted exactly this lesson one level up** — *"a call count cannot name an arm"* — for choosing among `rt_defer_open`'s four arms. I read it, applied it to arm SELECTION, and then walked into the identical error one level down, where the count is dynamic, correct, scaling, and *still* does not license the port. **A lesson recorded as being about one decision does not automatically transfer to the decision beside it.**

⇒ **ARCH §7 step 0 is now SIX checks. (f) is the arm check.**

---

## 3. ⭐⭐ Landed instead: `scripts/util_rtx_arm_census.sh`

Turns the lesson into a mechanical pre-flight check instead of prose:

- counts `sym` and `c_sym` and prints **`COMMITS = entries − bailed`** = calls the asm handled end to end
- **`COMMITS == 0` ⇒ do not write the asm**; run it BEFORE the port, on the workload the rung will be graded on
- **symbol list DERIVED FROM THE TREE every run** (`RTX_FUNC` names ∩ the `.so` dynamic table) — never hand-maintained, because a checked-in symbol list is precisely the phantom/doc-rot class this ladder has already paid for six times
- signature-agnostic: the thunk is `inc qword ptr [rip+cnt]` + `jmp qword ptr [rip+real]`, which clobbers **only EFLAGS** and never an argument register, so it forwards any signature without knowing it

**VALIDATED TWO-SIDED AT MINT** (the discipline RTX-0b applied to its harness): `str_concat_d` **500,000 commits gate-ON → 0 commits / 500,003 bails gate-OFF**, while same-run `rt_str_alloc` (different family) held steady — negative and positive control in one run.

It immediately produced a second result nobody asked for: **`rt_gcheap_alloc` is VACUOUS on `pattern_bt`** (1 entry, 1 bail, 0 commits). A live, landed RTX-2 family with nothing to grade on that program.

---

## 4. Symbol-name corrections (struck in this commit, per ARCH §7 step 0)

The RTX-8 rung read `match_enter/variant/value/replace`. After step 0 it is **2 real, 1 phantom, 1 truncation** — both failure modes in one rung line:

| rung name | verdict |
|---|---|
| `rt_match_enter` | REAL — `builtins/gen_runtime.c:127`, 42 static sites |
| `rt_match_variant` | ⛔ **PHANTOM** — declaration-only `rt/rt.h:30`, zero definitions, zero call sites |
| `rt_match_value` | ⛔ **TRUNCATION** — tree spells TWO symbols: `rt_match_value_get_pat_fn`, `rt_match_value_open` (`pattern_match.c:1010/1016`) |
| `rt_match_replace` | REAL — `gen_runtime.c:151`, 12 static sites |

Also: `rt_match_capture` and `rt_scan_splice_empty` are live definitions with **ZERO static call sites** in the benchmark+demo `.s` artifacts — ungradeable on today's corpus.

---

## 5. Corroborations and corrections of the record

- **s215's numbers reproduce EXACTLY** under an independently written instrument: `rt_defer_open`/`close` **402,121**, `rt_defer_get_pat_fn` **29,573**.
- **`rt_defer_step` re-confirmed at ZERO dynamic calls** against **432 static call sites** — the widest static/dynamic gap in the family.
- ⛔ **`rt_call_arr` is NOT setup-only.** s188 measured it flat across N on `claws5-match`; on `json.sno` it takes **96,861 calls scaling 2.00×**. That claim is **workload-scoped, not general**, and should not be quoted as a property of the symbol.
- ⛔ **`rt_cap_push` takes ZERO calls in ALL 20 `corpus/benchmarks/snobol4/` programs**, reachable only from the `json.sno` demo. RTX-12 board blindness, one family further along.

---

## 6. ✅ RTX-0f is effectively solved — scale the INPUT, not the grammar

Wrapping N copies of `twitter.json` as `[doc,doc,…]` scales **every** match symbol **exactly 2.00× per doubling**. Self-timed `match_ms`: 1×=**282** · 3×=**870** · 4×=**1172** against `MIN_MS=800` ⇒ **4× is a gradeable window**, which retro-qualifies s215's ungraded slice. This is the "cheapest credible shape" RTX-0f itself nominated.

⚠ **Two caveats, both load-bearing:**
1. 6× read **1323 ms** where ~1750 was expected — **sublinear**. Do not quote a ratio off single runs; the benchmark still owes repeated interleaved rounds.
2. **Naive `cat a a` does NOT work.** It makes malformed JSON; the parse aborts and counts come back *lower*. It briefly faked an exact-1.00× reading that I misread as "these symbols are construction-phase" — **falsified by a tiny-input control** (`rt_cap_push` = 7 on 8 bytes vs 57,578 on 631 KB). A wrong-but-self-consistent scaling reading is available to anyone who scales an input without validating it.

---

## 7. ⭐ Method lesson: a silent value-probe is ambiguous; a `ud2` is not

The falsification probe (corrupt the stored capture delta) came back **silent** — readable two ways: "asm did not run" *or* "this value never reaches the output." A **`ud2` planted on the commit path settled it in ONE run by not firing** under gate ON.

⇒ **Prefer a HARD probe (crash/trap) over a value probe whenever a silent result would be readable two ways.** s204 and s213 both burned time on silent probes; this is the cheap disambiguator.

---

## 8. Instrument defects — mine, and all caught from the object rather than by assumption

1. File-scope `__asm__` emitted the thunks into **`.bss`** (no `.text` directive): `nm` printed `B` where `T` was required. Caught by checking the object, not by trusting that the code "looked right."
2. **Exported counters in a `.so` cannot take direct `[rip+sym]`** — `R_X86_64_PC32` link failure. This is **ARCH §7 step 0(c) biting my own tool**; fixed with `visibility("hidden")`, which is the same resolution the contract prescribes for runtime globals.
3. The interposer's constructor runs in **two processes**; only the second has `libscrip_rt.so` loaded, and the first's destructor was overwriting the census with zeros. Fixed by arming on `dlopen(..., RTLD_NOLOAD)`.
4. **`json.sno` writes `match_ms` to stderr**, which faked a stdout diff until the redirection was corrected — a self-inflicted false divergence.

---

## 9. Next rung — pre-measured, and the arm check still owed

**Target `pattern_bt.sno`, not json.** Measured entries, gate ON:

| symbol | entries | note |
|---|---|---|
| `rt_match_enter` | **500,001** | `gen_runtime.c:127` |
| `rt_match_ctx_restore` | **500,001** | `gen_runtime.c:145` |
| `rt_dcap_end_ok_open` / `close` | **500,001** each | `pattern_match.c:696/717` |
| `rt_ws_alloc` | **192** | ⇒ **NOT allocation-bound**, unlike the cap family |

23× hotter than json, and `pattern_bt` is a real benchmark with a `.ref`, so the existing harness can grade it.

⛔ **These are ENTRY counts. They do not name an arm. Run `util_rtx_arm_census.sh` on the chosen symbol before writing a line of asm** — that is the whole point of this session.
⚠ Note the file: `rt_match_enter`/`rt_match_ctx_restore` live in `builtins/gen_runtime.c`, **not** `pattern_match.c`.

## 10. Not run, and not claimed

Full crosscheck both modes · smokes · beauty · 15-demo board · unit batteries. **No asm landed, so no watermark moved.** Code delivered: one additive script (zero codegen impact ⇒ no `.s` regen owed) plus doc corrections. `handoff_status.sh` is the push truth.
