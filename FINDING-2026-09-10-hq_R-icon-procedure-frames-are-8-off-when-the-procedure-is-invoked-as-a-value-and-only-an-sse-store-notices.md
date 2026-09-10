# FINDING 2026-09-10 hq_R — an Icon procedure frame is 8-off when the procedure is invoked as a VALUE, and only an SSE store ever notices

**Tree:** SCRIP `b9f9bc465` · corpus `47349890c` · `RT_OPT=-O0` · incremental `make`.
**Found from:** IPL run-tier board 87/89 both modes (`test_icon_ipl_suite.sh`, hq_R). RUN_FAIL is **zero**; the entire remaining IPL run-tier gap is two crashes, `diffu` and `diffn`, SIGSEGV in BOTH modes. They are ONE class.
**Owner:** this is hq_U's misaligned-SSE-store #GP class (MODE lane cut; hq_B's `.github 936228e1`), not hq_R's. Routed, not cured.

## THE FAULT IS AN ALIGNMENT #GP, NOT A BAD POINTER
The crash looks like a wild write and is not one. `si_addr` is **0x0** and the faulting instruction is

    movaps %xmm0,-0xc0(%rbp)        with rbp = 0x7ffffffe8de8  ->  target 0x7ffffffe8d28

`0x7ffffffe8d28 % 16 == 8`, so `movaps` raises **#GP on a misaligned operand**. The buffer it was told to fill (`rt_pinned_alloc(64)`, `by_name_dispatch.c:5283`) is perfectly valid and sits inside a mapped `rw-` region — I checked, because the pointer *looked* wild. The stack is nowhere near exhausted either (`rsp` 43 KB above the guard, 8 MB limit). **Three plausible causes were ruled out by measurement before the real one was found**, and each would have produced a confident wrong FINDING.

## THE MEASUREMENT THAT NAMES IT
`by_name_dispatch.c` already carries an `SCRIP_CALLARR_TRACE` hook — somebody has stood here before. Over one `diffu` run, 49 runtime calls:

| `rsp % 16` at `rt_call_arr_bl` | calls |
|---|---|
| 0 (correct) | **45** |
| 8 (misaligned) | **4** |

The four are not random: they are **all three `===` calls and the single `string` call**, and nothing else. The crash is simply the first misaligned call whose callee happens to reach an aligned SSE store.

## THE SAME PROLOGUE IS CORRECT ONE WAY AND BROKEN THE OTHER
Every Icon procedure frame in this program subtracts a multiple of 16:

    FN__zot          sub rsp,336     FN__diffread  sub rsp,1248     FN__groupfactor  sub rsp,528

A frame size ≡ 0 mod 16 **preserves** whatever alignment it was entered with. So the prologue is not the defect; the ENTRY is. Measured at the two entries in the same run:

    FN__diffread     entry rsp % 16 = 0   ->  calls from this frame are correctly aligned
    FN__groupfactor  entry rsp % 16 = 8   ->  EVERY call from this frame is 8-off

`diffread` is called by name and statically. `groupfactor` is invoked as a **procedure VALUE** — `dif()` does `/group := groupfactor` and then `gf := group(...)` — and `===` reaches its callee the same way (`diffu.icn` declares `invocable all`). ⭐ **Two entry conventions wearing one spelling**: the callee cannot tell how it was reached, so a frame that is correct under a direct call is 8-off forever under the value call, and every call it makes inherits that.

`string(m)` is the FIRST statement of `groupfactor`, which is why this particular program dies immediately rather than somewhere subtle.

## THE PATCH THAT IS ALREADY THERE IS THE TELL
`FN__groupfactor`'s prologue contains

    push rax / push rdx / push rbx / mov rbx, rsp / and rsp, -16    <-- then the &trace call

An explicit realignment **wrapped around the tracer call only**. That is the earlier cure for this same class applied at the one site where it had been observed to bite. It works, and it left every other call in the same frame exposed. ⛔ **A local realignment at the site that crashed treats the symptom's address as the defect's address.** The frame was misaligned before the tracer and stayed misaligned after it; `string` is the same bug two years of call sites later.

## WHY IT HID
A misaligned stack is invisible until a callee spills an SSE register with an ALIGNED store. Most of the runtime never does, so 45 of 49 calls were misaligned-or-not with no observable difference, and the four that were misaligned needed the *callee's* codegen to care. ⭐ **The symptom is a property of the CALLEE's instruction selection, not of the defect** — which is why this reads as a rare, program-specific crash and is actually a systematic ABI break on one entry path.

## REPRO
    cd corpus/packages/icon/ipl/progs
    scrip diffu.icn -- diffu.in1 diffu.in2        # SIGSEGV 139, m3 and m4 alike
`diffn` is byte-for-byte the same failure at the same instruction. Both match their icont-cut `.std` under the real oracle. Row `flip-ipl-diffu` (hq_R) carries a DONE-WHEN proven red in both modes.
