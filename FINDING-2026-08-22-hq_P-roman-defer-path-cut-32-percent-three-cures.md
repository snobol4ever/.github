# FINDING — ROMAN'S DEFER PATH CUT 32.4%, THREE CURES, ALL LANDED AND PUSHED

**Seat:** hq_P · **2026-08-22 s260** · **Class:** MEASURED + CURED · **RT_OPT=`-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`**
**Instrument:** callgrind Ir at FIXED WORK (`echo 2000 | ./roman`), mode-4 native binary.
**⛔ OUTPUT VERIFIED ON EVERY ARM BEFORE ANY NUMBER WAS BELIEVED: `check: 1102`.** The rig REFUSES to print an Ir number when the output is anything else.

## ⛔ WHY THIS SEAT CURED INSTEAD OF BRIEFING

**Lon, in-chat s260: "Target ROMAN. Run in a loop. Find the biggest bottleneck, then fix. Rinse, repeat."** That
overrides MEASURE-FREELY-CURE-NEVER for this row, per THE LOOP clause 6. Routed to `GOAL-HQ-PERFORM.md` § LON
OVERRIDE s260 the moment it landed. Scope is the ROMAN speed row on this seat, not a general repeal.

## The result

| arm | Ir @ N=2000 | Ir/iter | Δ | check |
|---|---|---|---|---|
| session baseline `f4657712` | 80,371,475 | 40,186 | — | 1102 ✓ |
| + FAIL-strcmp guard | 77,638,799 | 38,819 | −3.40% | 1102 ✓ |
| + one resolution not two | 62,788,744 | 31,394 | −19.1% | 1102 ✓ |
| + drop the unobservable dfx frame | **54,315,629** | **27,157** | **−13.5%** | 1102 ✓ |
| **cumulative** | | | **−32.4%** | |

⭐ The baseline reproduces this seat's own s259 measurement to **36 Ir in 80.4M (0.00004%)** — the rail is exact.

## The three cures

1. **`strcmp(varname,"FAIL")` on every deferred execution** — a full libc call to recognise one reserved name,
   2.96% of the program. `strcmp(v,"FAIL")==0` implies `v[0]=='F'`, so a first-char guard cannot change an answer.
2. ⭐ **TWO name resolutions per deferred node, not one.** The emitted box called `rt_defer_get_pat_dtp` and then,
   on the not-a-pattern fall-through, `rt_defer_run_all` — and **both opened by resolving the same baked literal
   through the global name table**, back to back, with only a `test` and a `jz` between them. callgrind named the
   pair exactly: `rt_defer_nv_read'rt_defer_get_pat_dtp` **594,060 Ir** and `rt_defer_nv_read'rt_defer_run_all`
   **594,060 Ir** — *identical counts*. `rt_defer_probe_run` resolves once and returns both answers **in registers**
   (rax=fn, rdx=dtp-or-cursor), so RULES.md's NO-NEW-GLOBALS rule is met by construction, not by grant.
3. ⭐ **A dfx frame pushed and popped with nothing in between.** `rt_defer_run_all` pushed a `g_dfx` frame, stored
   the value, and had `c_rt_defer_close` pop it straight back off — no call out, no emitted code, no assembly in
   the gap. Pure ceremony, and not cheap: `rt_dfx_push` 3.78% plus the pop, the 24-byte struct copy and the
   top-of-stack check. Also: a **one-byte** compare was calling `__strncmp_avx2` (1.70%).

⛔ **THREE CASES DELIBERATELY KEEP THE OLD TWO-CALL PAIR**, because for them the second read is not redundant:
`*`-prefixed names (get_pat_dtp PUSHES to `g_spk`, run_all POPS — producer/consumer, not repeat), `DT_X` (resolving
calls a procedure that may itself assign the variable), and a `DT_P` whose `fn` has not materialised.

## ⭐ THE CONTROL, and why it is the load-bearing part

`SCRIP_DEFER_MERGE=0` on the **same binary** returns the merged entry to the original two-call pair:

| | ON | OFF |
|---|---|---|
| after cure 2 | 62,788,744 | 81,444,908 |
| after cure 3 | **54,315,629** | **82,157,813** |

Both OFF arms print `check: 1102`. **A broken program is fast** — hq_C's s259 warning — so the killswitch is what
distinguishes *work removed* from *work skipped*. Corpus at `-O2` on every arm: **m3 355/359, m4 354/359 + 2 SKIP**,
fail-set byte-identical to the recorded baseline (`160_pat_alt_inner_gen_resume`, `demo_treebank`, and the two
`-O2`-only reds `161_pat_defer_fn_nested_match` and `demo_porter`). `test_gate_emit_no_lang` and
`test_gate_template_medium_invisible` both green.

## ⛔ TWO CORRECTIONS I OWE THE RECORD

1. **I diagnosed the wrong root cause first.** Seeing `T` excluded from the GVA fast path, I concluded
   `graph_has_local` was over-conservative because SNOBOL4 locals are dynamically scoped — and the emitted
   `ROMAN_α` prologue does confirm that (`mov rax,[r9+32] # T` … `mov [r9+32],0` … restore). **But the deferred
   name is not `T`.** `.S1` resolves to **`"PATV$0"`**, a compiler-generated marshalling variable that
   `gva_collect_graph` (`emit.cpp:3329`) skips by design. The GVA arm is unreachable here for a different and
   legitimate reason. The measured redundancy that the cures actually address never depended on that reading.
2. **`-Bsymbolic-functions` is not the win it looks like.** The runtime is a PIC shared library, so intra-library
   calls go through the PLT. Relinking the same objects with `-Wl,-Bsymbolic-functions`: 62,071,844 vs 62,788,716
   = **−1.14% only**. PLT cost is indirect-branch and cache, which **Ir does not measure**. Dropped, not adopted.

## ⭐ THE NEXT ROW, NAMED AND SIZED

`NV_GET_fn'rt_defer_nv_read` **14.85%** + `__strcmp_avx2'NV_GET_fn` **4.37%** = **19.2%** — the ONE remaining
by-name resolution per deferred execution, 140,381 calls at ~74 Ir each. This is the FINDING-s259 "narrow
direction": resolve the deferred name to its `NV_t*` **once** and follow a pointer, SPITBOL's `vrblk` discipline.
`core.c`'s own memo comment already establishes the soundness (workspace blocks never move or free; `NV_SET_fn`
reuses rather than shadows) and the two hazards (stack-buffer pointer keys; shadowing, cured by `g_nv_memo_gen`).
⭐ **A per-site slot already exists — `g_sno_defer_cells[4096]`** — currently allocated only when `ci >= 0`, which
requires a GVA-eligible name and so never fires for a `PATV$` site. Extending `ci` to merged sites would give this
cure a home **without a new global**.


---

# ⭐⭐⭐ s261 CONTINUATION — ROMAN IS NOW −56.3%, SIX CURES, AND THE DEFER PATH MAKES NO CALL AT ALL

Lon s261: *"So keep on slicing those times... Keep squeing."* Two more cures landed on top of the three above.

| arm | Ir @ N=2000 | Ir/iter | Δ | check |
|---|---|---|---|---|
| session baseline `f4657712` | 80,371,475 | 40,186 | — | 1102 ✓ |
| `97ef3c3a` FAIL-strcmp guard | 77,638,799 | 38,819 | −3.40% | 1102 ✓ |
| `454b5190` one resolution, not two | 62,788,744 | 31,394 | −19.1% | 1102 ✓ |
| `f8081604` drop the unobservable dfx frame | 54,315,629 | 27,157 | −13.5% | 1102 ✓ |
| `a16598a2` ⭐ SPITBOL's vrblk discipline — cache the cell | 47,143,490 | 23,571 | −13.2% | 1102 ✓ |
| `84aaef7e` ⭐⭐ inline the read into emitted code, no call | **35,130,646** | **17,565** | **−26.7%** | 1102 ✓ |
| **cumulative** | | | **−56.3%** | |

**vs the clean benchmark oracle (7,966 Ir/iter, recorded s258): 6.58x → 2.21x.**

## The last two cures, and why the second one is the shape that matters

**Cure 4 — stop looking the name up.** `NV_GET_fn` + its `strcmp` was 19.2%, and callgrind's *line* annotation
showed the lookup was not the cost — the **ceremony** was: prologue 1,214,530 Ir, a non-inlined `_var_init()`
call 462,184 Ir to test one flag, memo index 770,115, memo key/generation check 1,271,736, validation strcmp
2,376,240. You cannot make a lookup cheap enough. `NV_PTR_fn` already returns the stable cell — core.c's own memo
comment carries the proof — so each site caches a **self-validating (key, cell) pair**: a slot collision misses
and re-resolves, it can never hand one site another's cell. **`NV_GET_fn` disappeared from the profile entirely.**

**Cure 5 — stop making the call.** What was left was the *wrapper*: an `xfer_enter/leave` push-pop of r13/r14/r15,
an `rtccb` save/restore of r8/r9, a PLT call and a branch chain — **~120 Ir to "read a cell and compare one
byte."** The emitted box now does the common case in ~18 instructions with no call. ⛔ It **cannot answer
differently, only sooner**: every other case — cold slot, shared slot, non-string, multi-character, a pattern, an
unevaluated expression — falls through to the *unchanged* call.

⭐ **THE REGISTER MAP WAS VERIFIED, NOT ASSUMED, AND THAT IS THE METHOD POINT.** Earlier the same day this seat
asserted a register/name mapping in this same box and was wrong (the deferred name is `PATV$0`, not `T`). So the
claim was sourced from emitted code that *provably* scans the subject: `bb_match_break` emits
`movsxd rcx, r14d / cmp ecx, r15d / movzx esi, byte ptr [r13+rcx]`, fixing **r13 = subject, r14d = cursor,
r15d = length**. The inline arm reuses that exact idiom rather than a second guess.

## ⛔ Controls, and one that would have been fake

Every arm is killswitch-controlled: `SCRIP_DEFER_MERGE=0` (runtime) and `SCRIP_DEFER_INLINE=0`. **`DEFER_INLINE`
is an EMIT-time switch**, so toggling it on an already-baked binary does nothing — the OFF arm was **re-compiled**
(48,166,519 Ir, check 1102). A control that cannot actually disable the thing it controls is not a control.

## ⛔ A latent hazard this seat introduced and then closed

The cell-pair cache lives in the upper half of the existing `g_sno_defer_cells`; the DTP cache allocates from the
bottom with a bound of 4096. **A program with enough DTP sites would have written a DTP into a word read back as a
cell address.** Bound tightened to 2048. Named because it was mine and it was live for two commits.

## ⛔ demo_calculator_1 — a NEW corpus red, and it is NOT from this work

Sent to hq_C as a wrong answer under their standing order, with the bisect that rules this seat out: identical
failure with `SCRIP_DEFER_INLINE=0`, with `SCRIP_DEFER_INLINE=0 SCRIP_DEFER_MERGE=0`, and with this seat's entire
working tree **stashed** and rebuilt at HEAD `3970f54a`. ⛔⛔ **MY SUSPECT WAS WRONG AND IS CLEARED — DO NOT REVERT `53819b4a`.** hq_C adjudicated it
(`FINDING-2026-08-23-hq_C-calculator-1-is-an-O2-split-53819b4a-cleared.md`) and the argument is decisive: the
**scrip compiler is hardcoded `-O0` and does not honour `RT_OPT`** (Makefile:86), so emitted code is *identical*
across both arms — a codegen commit cannot cause a failure that flips on **runtime** opt level with codegen held
constant. `-O0` gives `check: 103002` clean; `-O2` gives the refusal stream. It is an **RT_OPT split**, and since
every corpus number in this FINDING is `-O2`, `demo_calculator_1` is a **known `-O2`-only red** alongside
`161_pat_defer_fn_nested_match` and `demo_porter` — *not* a regression from this work.

⭐ **THE METHOD ERROR WAS MINE AND IT IS THE PART WORTH KEEPING.** I said the red "appeared on the first run after
the rebase" and named the codegen commit I noticed in that pull. **The pull carried TWO relevant commits** — and
the second (`53c1323a`) was hq_C's *guard*, the code that **prints** the refusal. Before it, that path did a silent
out-of-bounds memcpy. So my own evidence was equally consistent with a **pre-existing latent defect that a new
guard made AUDIBLE**, and I never considered that reading. Correlation with a pull is not causation by the commit
you happened to notice in it — PRESENCE IS NOT PROOF, aimed at a changelog instead of a gate.

The **+795,000 Ir (+1.7%)** cost of `53819b4a` stands on its own as a *performance* observation and is untouched
by the clearing — it is simply not also a wrong answer.

⛔ **LON OVERRIDE, s261, verbatim via hq_C: *"Do NOT fix -O2 bug for BEAUTY. Do not care. Next."*** Nobody is to
spend time curing this. It is diagnosed and parked deliberately.
