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

## 7. ⚠ NOT DONE / OPEN

- **NO SPEED CLAIM.** Rail not run; RT_OPT=`-O0`. The s163 measurement lesson stands: this
  1-core container's sub-800ms windows swing 1.4-3.9×, so a rail number here would be noise. RTX-3
  is where real speed evidence was predicted to arrive (ARCH §6) — it needs a quiet measurement,
  and per the O2-DIRECTED-ONLY rule any `-O2` comparison build needs a Lon directive.
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
