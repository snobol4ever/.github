# `match_begin` β is ALREADY at Lon's design bar — and the 18.18% that justified the row was a 144-sample artifact

**Seat:** hq_P · **Date:** 2026-08-28 · **Mode:** FLEET-8 (`MODE` computed) · **Row:** `perf-match-begin-beta-cure` (Lon-entry, burn-down)
**SHARED AXES:** `perf cycles:u @999Hz` · `PERF_BIN=/usr/lib/linux-tools-6.8.0-138/perf` · mode 4 · `RT_OPT=-O0` · SCRIP `71175348` · corpus `3a01209c7`
**BASIS:** porter **fixed-work** bench — `bench_wrap.sh --mode=iter --n=30` (`kernel=PORTER`, `check=139812`), stdin `porter.dat` (190,138 B), 4.63 s, ~4,700 samples/run, **5 independent runs**.
**TSV:** `corpus/benchmarks/snobol4/perf-attribution-20260828T134902Z-hq_P-match-begin-beta.tsv`

## 1. The lever was measured on 144 samples, and it does not survive re-measurement

The row was minted on slice 1's read: `match_begin` = **24.84%** of cycles, **18.18% on β**. Lon's design steer was built on that ("MATCH_BEGIN is almost 25%"). ⭐ **My own caveat at mint said re-rank before sizing any claim. Re-ranked:**

| | slice 1 (single pass, 0.14 s) | **this row (fixed-work, 4.63 s, 5 runs)** | |
|---|---:|---:|---|
| `match_begin` TOTAL | 24.84% | **9.33%** (8.95–9.55) | **2.66x overstated** |
| `match_begin` β | 18.18% | **7.15%** (6.94–7.29) | **2.54x overstated** |

⛔ **THE SLICE-1 PROFILE CONTAINED 144 SAMPLES IN TOTAL** (`perf script | wc -l`), for the whole program. `match_begin` β at ~10% of it is **~14 samples**. Poisson alone puts ±26% at 1σ on 14 counts, before any scheduler noise from seven other fleet seats. **`18.18%` is four significant figures resting on about fourteen samples.**

**Demonstrated, not argued** — same binary, same input, 5 runs each, single-pass basis: β read **2.42, 5.74, 6.41, 10.37, 4.77**. A 4.3x spread. I first read that spread as a *basis* effect (two different `porter.sno` + two different `porter.input` exist, see §5) and was wrong: the distributions overlap almost entirely. **It was noise, and I nearly reported it as a finding.**

⭐ **The ranking survives even though the size does not:** `match_begin` is still the **top BB family** (next is `match_defer` at 4.23%). The row's target is real; its size was not.

## 2. The β RECEDE port is ALREADY what Lon asked for

Lon's design bar, verbatim in substance: *"all it needs is a few register manipulations to save/restore the pattern context and should be straight assembly code."* The row asked what the β points buy — *RTCC save/restore? dfx frame? rt calls? redundant context reload per backtrack step?*

⛔ **ANSWER: NONE OF THOSE. STATIC, DETERMINISTIC, WHOLE-PROGRAM:**

| port | bodies | **`call` insns** | **push/pop** | median size |
|---|---:|---:|---:|---:|
| `match_begin_β` | 13 | **0** | **0** | **9 insns** |
| `match_begin_af` | 13 | 13 | 13 | 15 insns |
| `match_begin_α` | 13 | 13 | 65 | 27 insns |

**β is nine instructions with zero calls and zero frame traffic** — it already *is* "a few register manipulations, straight assembly." Sampled opcode mix inside β agrees: `mov` 55.8% · `cmp` 26.1% · `lea` 17.5% · all branches 0.5%.

⭐ **The ceremony Lon describes exists — in α and `af`, not β.** `rt_match_ctx_restore@PLT` is called from **`af`**, and α carries 65 push/pop. **A cure aimed at β has nothing to remove.**

The whole β body, verbatim — the unanchored-retry loop:
```
n2844_match_begin_β:  mov  r11, 1778
.Lmain_α_5012_13:     lea  rsp, [rbp + -56]          # retry_whack
                      add  dword ptr [rbp + -40], 1  # start_δ
                      mov  eax, dword ptr [rbp + -40]
                      cmp  eax, r15d;  jg  .Lmain_β_5012_1
                      mov  rcx, qword ptr [rip + rt_anchor_g@GOTPCREL]
                      mov  rax, qword ptr [rcx]
                      cmp  rax, 0;     jne .Lmain_β_5012_1
                                       jmp .Lmain_α_5012_0
```
⛔ **A HYPOTHESIS OF MINE THAT THE MEASUREMENT KILLED, recorded so nobody re-derives it:** the `rt_anchor_g` reload through the GOT looks like textbook removable ceremony — an invariant global re-loaded every retry, 4 of ~10 instructions. **It costs 0.00%.** The `jg` above it exits the loop in the common case, so the anchor path is rarely reached. I was about to hoist it. ⭐ **Hoisting it would have been a real code change, a plausible story, and zero measured gain.**

⭐ **So the cost is not ceremony PER retry — it is the NUMBER of retries.** The lever, if one exists, is algorithmic (first-character discrimination, a skip loop, anchoring), **not** the instruction-shape cure the row was minted to perform.

## 3. The actual top lever on a throughput basis is GC + allocation

Non-BB symbols are **74.10%** of this profile (BB boxes are 25.49%):

| symbol | share |
|---|---:|
| `NV_SET_fn` | 10.49% |
| `gc_collect_ex` | 7.95% |
| `rt_cap_open` | 7.95% |
| `__strcmp_evex` | 7.72% |
| `rt_gcheap_carve` | 5.93% |
| `c_rt_gcheap_alloc` | 4.88% |

⭐ **`gc_collect_ex` + `rt_gcheap_carve` + `c_rt_gcheap_alloc` = 18.76%** — twice `match_begin`'s entire 9.33%, and larger than every BB box combined on the β port. ⛔ **It is invisible on the single-pass basis by construction**: one pass over 20k words barely fills the heap, so GC scarcely runs. The instrument that ranked `match_begin` #1 could not have seen the bigger lever.

⚠️ Whole-program branch-miss rate is **0.78%** (51,525,694 / 6,642,860,683). Not the story either.

## 4. Callgrind cannot attribute to BB boxes at all

I reached for the deterministic instrument first (campaign rule prefers Ir at fixed work on this shared box). **It cannot name a single box.** Emitted BB labels are `NOTYPE LOCAL`, **size 0** — the `.s` contains **zero** `.type`/`.size` directives — and valgrind ignores zero-sized symbols, reporting `???:0x…`. perf resolves them only because it uses nearest-preceding-symbol.

⛔ **So per-box attribution is currently possible ONLY with the sampling instrument, which is exactly the one that needs a long run to be trustworthy.** Emitting `.type`/`.size` for box labels would make the deterministic instrument work and remove the sampling-error problem at its root. **Routing this, not doing it — it is an emitter change and belongs in its own row.**

## 5. Two different programs are both called "porter"

`corpus/demo/snobol4/porter/porter.input` (190,138 B) is **byte-identical** to `corpus/benchmarks/snobol4/demo/porter.dat` (md5 `ffca0f6c…`), while `corpus/benchmarks/snobol4/demo/porter.input` is a **different** 1,763 B file — **and the two `porter.sno` differ too** (437 vs 417 lines; the benchmark copy adds the `PORTER(N)` kernel and the `*BENCH` marker).

⛔ **"porter on porter.input" therefore names two different measurements**, and the 1.7 KB one runs so briefly that its profile is **99.43% `do_lookup_x`** — dynamic-linker startup, not the program. Any perf number labelled only "porter" is under-specified.

## The class

Same shape as the other instrument errors this session, from a third direction: **`perf` faithfully reported the share of the samples it took; that was read as the share of the work.** The instrument was not broken — the question it answers ("of 144 samples, how many landed here") is narrower than the one it was used for ("what fraction of the work is this"), and it had no way to say so.

⛔ **Operational rule: a profile must state its SAMPLE COUNT next to any share it reports, and a share built on fewer than ~1,000 samples is a hypothesis, not a measurement.** `util_perf_bb_rollup.sh` already prints COVERAGE for exactly this reason; it should print sample count too, and refuse below a floor. **That is a cure I own and am routing to my own tooling row rather than smuggling into this one.**

## Ledger

- ⛔ **The β instruction-shape cure this row was minted to perform SHOULD NOT BE CUT.** β has nothing to strip. Re-aiming needs Lon/ceo, since the row carries Lon's own steer — **routed, not decided here.**
- ✅ First step (attribution inside the port) is **DONE**; question answered with a static, deterministic result rather than a sampled one.
- ⭐ Candidates for re-aim, ranked by measured size: **GC+alloc 18.76%** · `NV_SET_fn` 10.49% · α/`af` context save-restore (where the ceremony actually is) · retry-COUNT reduction for `match_begin`.
