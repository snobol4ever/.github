# FINDING 2026-07-25 (s164) — SN4 RTX-3 STRINGS: THE PHANTOM FAMILY IS A CLASS, NOT AN INCIDENT; AND `rt_sxt_note` IS THE TRAP THAT PASSES EVERY TEST

**Rung:** RTX-3 STRINGS. **Status:** LANDED, default ON, gate `SCRIP_RTX_STR`.
**Watermark:** re-proven at session start AND after landing — m3 314/1 · m4 309/4 · DIVERGE=3.

---

## 1. THE RUNG NAMED DEAD SYMBOLS. AGAIN. STEP 0 CAUGHT IT IN TWO MINUTES.

RTX-3 as written named `str_concat_d` + **`rt_concat`** + **`rt_lcomp`/`rt_acomp`** + `rt_coerce_str_d`
+ SIZE/TRIM/DUPL/REPLACE. Three of those are phantoms:

| symbol | definition | call sites |
|---|---|---|
| `rt_concat` | NONE — declaration only, `rt/rt.h:69` | 0 |
| `rt_lcomp`  | NONE — declaration only, `rt/rt.h:81` | 0 |
| `rt_acomp`  | NONE — declaration only, `rt/rt.h:80` | 0 |

Whole-tree grep across `*.c/*.h/*.cpp/*.s/*.S`: each appears exactly ONCE, in its own prototype.
They are vestigial declarations of a value-stack-era API that was never written or was deleted
without its header.

**This is the SECOND occurrence in two rungs** (RTX-2: `blk_alloc`/`blk_free`), and the two have
different causes — RTX-2's came from an inventory script sweeping dead artifacts, this one from
prose in the ladder naming an API that never existed. **The common factor is not the script; it is
that a rung's symbol list was written from a DOCUMENT rather than from the tree.** ARCH §7 step 0
(added by RTX-2) is therefore not an RTX-2 postmortem detail — it is a permanent, load-bearing
step, and it paid for itself immediately. It cost two minutes and saved a rung.

⭐ **RULE PROPOSED:** the every-rung protocol's step 0 should ALSO require striking the dead names
out of the ladder text in the same commit that discovers them, so the next session cannot re-read
the same phantom list. RTX-2 corrected ARCH §5 but left the RTX-3 rung line untouched — which is
exactly why this session met the same wall.

**LIVE STR SURFACE** (fixed inventory script, 26 live `.intel_syntax` artifacts):
`str_concat_d` **152 — #2 overall, behind only `rt_call_arr` 232** · `memcmp` 106 (libc, stays) ·
`rt_gvar_assign_str` 44 + `rt_gvar_assign_concat_parts` 9 (NV family — RTX-7, not here) ·
`rt_coerce_str_d` 2 static (indirect reach only, ARCH §5 caveat (a)). **STR is `str_concat_d`.**

---

## 2. WHAT LANDED

`src/runtime/rtx/rtx_str.S` — `str_concat_d`, TWO-PLAIN-STRINGS FAST PATH ONLY.

**GUARD** (all must hold, else `jmp c_str_concat_d` with rdi/rsi/rdx/rcx untouched):
both operands `DT_S` · both `slen` nonzero and != `0xFFFFFFFF` · both payload pointers non-null ·
`g_gc_pending == 0` · SXT token does not own the left operand.

Under exactly that guard the C body provably reduces to carve/copy/copy/NUL/re-arm/return, and
**all ten helper calls are ELIMINATED, not skipped**: `rt_gc_point_arr`, `descr_to_str`×2,
`VARVAL_fn`×2, `rt_sxt_match`, `memcpy`×2, `rt_sxt_note`. Copies use an exact-bounds overlapping
memcpy (1-3 / 4-7 / 8-15 / 16-32 GPR+SSE, `rep movsb` above 32) — no overshoot, so no dependency
on carve rounding.

**NOT PORTED, C keeps sole ownership:** pattern concat (`pat_cat`) · FAIL propagation · the
NULL-operand identity · list concat (`DT_DATA`) · all coercions · CSET operands · unknown-length
strings · the SXT extend-in-place path with its GVA alias scan · any pending collection.

---

## 3. THREE TRAPS THAT WOULD EACH HAVE BEEN A SILENT CORRUPTION

**(a) `slen == 0` DOES NOT MEAN EMPTY.** `core.h descr_slen`: for `DT_S`, `slen == 0` means
*length unknown — call `strlen`*. `slen == 0xFFFFFFFF` means *this is a CSET*. **A CSET carries
tag `DT_S`.** A guard of "tag is `DT_S`, use `slen` as the length" is wrong twice over. Excluded
both, explicitly.

**(b) THE MANUAL'S NULL RULE IS TYPE-PRESERVING.** v3.7 Concatenation p.22: *if either operand is
the null string, the other is returned unchanged — it is NOT coerced to string.* The manual's own
example is `(20 - 17) ''` yielding the **integer** 3, not `'3'`. Requiring nonzero `slen` on both
sides routes every null case to C, preserving the type. A fast path keyed only on tags would have
silently stringified integers at the edge of every null concat.

**(c) ⭐⭐ `rt_sxt_note` CANNOT BE INLINED UNCONDITIONALLY — AND GETTING THIS WRONG PASSES EVERY
CORRECTNESS TEST.** The obvious reading is "we just carved this block at the frontier, so arm the
token." False: `c_rt_str_alloc` can satisfy a request from the fill window or a recycled block, and
in those cases C *declines* to arm. Arming anyway would hand a stale ownership token to the next
concat, which would then extend a buffer it does not own — corrupting live aliases, per the very
invariant the manual states (*"the two strings remain unchanged"*). The inverse error is worse in a
quieter way: **failing to arm when C would arm breaks NO test at all** — every result stays
byte-correct — while turning every `S = S CH` append loop in the corpus from O(n) back to O(n²).
A pure-correctness gate cannot see it. The port therefore reproduces the note's title checks
faithfully (`HBF_TTL` set, `type == DT_S`, `h + h->size == g_hp_top`), and the differential battery
probes the token through the exported `rt_sxt_match()` on every one of its 8404 cases.

---

## 4. GC SAFETY — WHY HOLDING RAW `a.s`/`b.s` ACROSS THE CARVE IS SOUND

`rt_gc_point_arr` is `if (!g_gc_pending) return;` and nothing else, so the C body's shielded
collection point costs ONE compare here. The load-bearing fact is the second one: **the allocator
never collects.** `gc_heap.c` only *sets* `g_gc_pending` (lines 212/217); collection runs
exclusively at explicit gc_points. So no descriptor can move between the guard and the return, and
the raw payload pointers held across `rt_str_alloc` cannot dangle — the same property the C body
already relies on. A pending collection routes to C.

---

## 5. C-SIDE CHANGE (minimal, follows the `g_hp_fr` precedent exactly)

`gc_heap.c`: the three SXT statics promoted into a **hidden** `g_sxt_fr` cell
(`owner@0 len@8 gva_n@16 off@20`) with four `_Static_assert` offset anchors, so a layout error fails
the BUILD. The `off` flag moved out of function-static into that cell using RTX-2's `zfull`
convention: **-1 = unresolved ⇒ jump to C so C resolves the `getenv`**, 1 = SXT disabled (token
cannot match, fast path safe), 0 = enabled (test the token). Hidden visibility means direct
`lea [rip+sym]` — no GOT hop, unlike `g_hp_fr`, which is exported only because the emitter bakes its
address into `sink_carve48`.

---

## 6. GATES — ALL GREEN

- **Differential 8404 cases, 0 mismatches** (every memcpy size class × both operands; every guard
  boundary — slen0/CSET/null-ptr/SNUL/int/real/FAIL/embedded-NUL/aliased operands; append loops).
  Full RTX battery 8461 with RTX-1's 21 and RTX-2's 36.
- **⭐ FALSIFICATION, BOTH SIDES** (the proof that matters): asm return tag deliberately broken to
  `DT_R` → gate ON = **8359/8404 mismatches**, gate OFF = **0**. The asm really executes; the switch
  really switches. Reverted and re-gated.
- Smokes SNOBOL4 7/7 × 2 modes. **Icon 14/14 × 2 · Prolog 5/5 × 3** — mandatory here, not optional,
  because `gc_heap.c` is shared by every language.
- Full crosscheck at watermark, both gates: m3 314/1 · m4 309/4 · DIVERGE=3 (same three
  `21{4,5,6}_indirect_goto`).
- **Kill-switch md5 ON == OFF = `0cc898346d1ad83e1b89d87a7342147a` — identical to the hash RTX-2
  recorded**, so crosscheck output is unchanged across two consecutive RTX landings.
- 15-demo board ON == OFF (`ea3eafd5...`), 13/15 TRI-IDENTICAL, m3 bad=0, m4 bad=2 (known state).
- beauty self-application ON == OFF (`1c75f97d...`).
- **`.s` regen NOT owed and PROVEN so**: `util_regen_benchmark_s_artifacts.sh` → *"No changes —
  benchmark .s artifacts already current."* Phase-1 touches zero templates by construction, and the
  emitter still emits `call str_concat_d`; only the C body's name moved.

---

## 7. MEASUREMENT — ISOLATED SYMBOL A/B (`rtx_str_bench.c`), **RT_OPT=-O0 BOTH ARMS**

A whole-program rail is unreadable here and was not attempted as evidence: s163 measured this
container's sub-800ms windows swinging 1.4-3.9×, and the concat-heaviest corpus benchmark
(`string_concat.sno`) completes in ~20ms, an order of magnitude below anything resolvable. A
SINGLE SYMBOL can be measured, because the iteration count is ours to choose. Each case runs in
its OWN PROCESS (heap fill cannot accumulate across cases — the first attempt without this showed
gate-ON times climbing 111→318→752 ns as the heap filled while gate-OFF stayed flat, which is the
confound, not a result), 40000 iterations × 9 reps, MINIMUM reported (on a shared 1-core box the
minimum is the least-contaminated estimator; noise only adds).

| case | asm ON | C OFF | ratio |
|---|---|---|---|
| tiny 3+3 | **10.64** | 76.51 | **7.2×** |
| small 8+8 | **13.74** | 84.04 | **6.1×** |
| token 12+7 | **12.81** | 81.74 | **6.4×** |
| mid 24+24 | **19.80** | 84.79 | **4.3×** |
| big 64+64 | **33.77** | 100.30 | **3.0×** |

Reproduced on a confirmation pass (tiny 10.64/79.37, big 38.17/102.34). Short operands — the
common SNOBOL4 shape, tokens and single characters — gain most, which is the expected shape: the
eliminated cost is ~10 fixed call overheads, so it dominates when the copy itself is small.

⛔ **THE CAVEAT THAT MUST TRAVEL WITH THESE NUMBERS, PER O2-DIRECTED-ONLY: BOTH ARMS ARE `-O0`.**
That is the SHIPPED configuration, so "the runtime as it ships got 6× faster at this symbol" is a
fair statement. **It is NOT "hand-written asm beats optimized C by 6×", and it must never be quoted
that way.** A large and unmeasured share of the gap is `-O0` refusing to inline the `static inline`
descriptor helpers (`IS_FAIL_fn`, `IS_NULL_fn`, `descr_slen`, `IS_STR_fn`), so the C arm pays real
call overhead for predicates that `-O2` would fold to a compare. **The asm-vs-optimized-C question
is OPEN and cannot be answered without a directed `-O2` runtime build** (RULES: O2-DIRECTED-ONLY —
needs a Lon directive in-session, and per s126 must run detached+polled with tree/artifact state
checks before and after).

**NO PROGRAM-LEVEL CLAIM IS MADE.** The symbol is 6× faster; what fraction of any real program is
this symbol has not been measured here, and `str_concat_d`'s 152 static sites rank the CALL
BOUNDARY, not dynamic weight (ARCH §5 caveat (a)). A program-level number needs a workload that
runs long enough to resolve — the claws5/json family from the s161 anatomy, not this benchmark.

- **MILESTONE-1 BEAUTY ORACLE md5 (`abfd19a7...`) STILL NOT REPRODUCED** — and now with a reason,
  which is more than RTX-2 could say. The x64 oracle IS cloned this session, but
  `sbl -b beauty.sno` from the demo directory dies with `ERROR 217 duplicate label` at line 568 and
  then segfaults, and `beauty.sno` reads its subject from **stdin** (with `< /dev/null` it exits 0
  with zero output). **The canonical Milestone-1 invocation is recorded NOWHERE in the goal file's
  Session Setup, RULES, or PLAN** — only the resulting md5 is. That is a documentation gap worth
  closing: a milestone whose reproduction command is unwritten cannot be re-proven by any later
  session. SCRIP-side ON==OFF identity WAS proven; the oracle comparison was not.
- `str_repeat_d` (same file, same family) not ported — far fewer sites; fold into a later slice.
- The carve is reached by `call rt_str_alloc` rather than inlined, deliberately: inlining would mint
  a FOURTH copy of the carve fast path (`rtx_alloc.S` + `sink_carve48` already must agree). If
  measurement nominates that call, slice 2 inlines it via a shared macro with a byte-identity proof
  on `rtx_alloc.o`.

## 8. ⚠ STILL OPEN

- **MILESTONE-1 BEAUTY ORACLE md5 (`abfd19a7...`) NOT REPRODUCED** — now with a diagnosis, which is
  more than RTX-2 could offer. x64 IS cloned this session, but `sbl -b beauty.sno` from the demo
  directory dies `ERROR 217 duplicate label` at line 568 then segfaults, and `beauty.sno` reads its
  subject from **stdin** (`< /dev/null` ⇒ exit 0, zero output; `< beauty.sno` ⇒ 278 bytes of real
  beautifier output). **The canonical invocation is recorded NOWHERE** — not Session Setup, not
  RULES, not PLAN; only the md5 survives. A milestone whose reproduction command is unwritten cannot
  be re-proven by any later session, and this one is the project's Milestone 1. Recommend the
  invocation be written into the goal file's Session Setup block next time someone knows it.
  SCRIP-side ON==OFF identity WAS proven (`1c75f97d...`); the ORACLE comparison was not.
- **`-O2` COMPARISON UNANSWERED** — see §7. This is the single most useful next measurement for the
  whole RTX programme, because it tells us how much of every future rung's win is real asm advantage
  versus `-O0` overhead we could have deleted with a compiler flag. It needs a Lon directive.
- `str_repeat_d` + SIZE/TRIM/DUPL/REPLACE builtins not ported (same family, far fewer sites).
- The carve is reached by `call rt_str_alloc` rather than inlined, deliberately: inlining mints a
  FOURTH copy of the carve fast path (`rtx_alloc.S` + `sink_carve48` already must agree). Given §7's
  numbers the remaining call is now a visible fraction of the fast path, so slice 2 (shared macro +
  byte-identity proof on `rtx_alloc.o`) is worth costing.
- Session numbering collided: a parallel Icon session also used **s164** (`1bed74b4`). Harmless here
  (different goal files, clean rebase) but the numbering is not collision-free across parallel chats.
