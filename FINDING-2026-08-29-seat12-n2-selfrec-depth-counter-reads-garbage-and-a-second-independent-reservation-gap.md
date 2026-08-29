# FINDING — the bounded self-recursion fix's depth counter reads garbage off the stack (missing push), plus a second, independent under-reservation bug when a self-recursive generator also calls a sibling generator

Row: `icon-n2-recursive-generator-per-activation-storage`. Origin: seat05's 2026-08-29 characterization that `rung36_jcon_genqueen` SIGSEGVs wild under `SCRIP_ICN_N2_SELFREC=1` (`rip=0x3, rsp=0xffffffffffffffde`) instead of hitting the fix's own loud N=64 refusal, hypothesized as specific to `solvequeen`'s conjunction shape (`suspend placequeen(c) & solvequeen(c+1)`) versus `gedwalk`'s plain alternation. This FINDING does the gdb/instrumentation trace seat05's own `## NEXT` named as the concrete next step, per the row's ASM-DIFF-FIRST discipline (build → diff constants → gdb).

**Reproduced exactly**: `SCRIP_ICN_N2_SELFREC=1 ./scrip --run tests/icon/rung36_jcon_genqueen.icn < /dev/null` under gdb — `rip=0x3, rsp=0xffffffffffffffde`, byte-identical to seat05's own cited numbers. Two independent, precisely-located defects found, neither actually specific to conjunctions.

## Root cause 1 (the immediate trigger): the self-recursion depth push is one 8-byte slot short of what the shared callee prologue reads

`src/templates/bb/bb_call_proc_staged.cpp`, both sub-branches of the self-recursion depth-passing block (~line 750-762):
```cpp
: x86("mov", "rax", RDQ("rbp", 40)) + x86("add", "rax", 1L) + ... + x86("push", "rax")   // recursive call: ONE push
: x86_lea_id("rax", 0) + x86("push", "rax")                                              // first call: ONE push
```
Both emit exactly **one** 8-byte `push` to carry the depth value. Compare the sibling, non-selfrec branch two lines below (the one this code is explicitly modeled on — its own comment says "same 8 bytes, same rsp math as the PL-CALL-ALIGN pad below"):
```cpp
: x86("sub", "rsp", 8L) + ... + x86_lea_id("rax", 7) + x86("push", "rax")   // TWO 8-byte slots: pad (sub) + L7 (push)
```
The shared callee prologue that reads this value back (`src/emitter/emit.cpp` ~line 2877-2879) unconditionally reads it from a **fixed offset, `[rsp+32]`**, which is only correct under the standard 5-slot/40-byte layout the file's own comment documents (`emit.cpp` ~line 2871: `[rsp+0]=gamma [rsp+8]=omega [rsp+16]=REGION [rsp+24]=L7 [rsp+32]=pad`) — a layout that assumes **two** slots (pad+L7) were pushed before the three that follow (region + two continuation labels). The selfrec branches push only **one** slot there, so everything after it (region, then two label pushes) lands one slot closer to `rsp+0` than the callee expects, and `[rsp+32]` reads **past** the top of what was actually pushed — stale/uninitialized stack memory, not the depth value (which is really sitting at `[rsp+24]` from the callee's perspective).

**Verified directly** (gdb, `/tmp/genqueen.bin`, breakpoints at the prologue-complete instruction `0x402546` and the depth-read instruction `0x402b6f`):
```
[ENTRY depth=0] rbp=0x7ffffffe5f98  H+40 just-banked=0            <- correct (first call, hardcoded 0)
[depth-read for self-call, depth=0] H+40=0                        <- read back correctly
[ENTRY depth=1] rbp=0x7ffffffe6198  H+40 just-banked=4213421       <- GARBAGE (expected 1)
[depth-read for self-call, depth=1] H+40=4213421                  <- read back, still garbage
libscrip_rt: BOMB — N-2 bounded self-recursion: depth exceeds ... N2_SELFREC_SLOTS
```
Depth 0 happens to read back correctly (memory above the caller's own fresh stack activity is apparently zero there); depth 1's banked value is already garbage. Under the compiled mode-4 binary the garbage happens to be ≥64, so the fix's own loud bound check fires — a false-positive refusal, not the real bound. Under mode-3 (`--run`), a **different** garbage value sits in the analogous memory (a different execution harness, different residual stack contents), evidently one that reads as small enough to pass the check, letting execution continue with a corrupted depth and eventually crash wild — reproducing the exact `rip=0x3`/`rsp=0xffffffffffffffde` signature.

⛔ **This is unconditional on the callee's identity, not specific to `genqueen` or to conjunctions.** The pushed-slot-count defect is purely a property of `bb_call_proc_staged.cpp`'s own emission for *any* call site targeting a self-recursive generator — it does not branch on what control construct (`|`, `&`, plain statement) contains the call. `gedwalk`'s own extensively-verified 24432-call trace almost certainly has the identical garbage-read defect; it was not caught because that verification checked **region addresses** (which never depend on the depth value — see root cause 2's derivation below for why) and the fixed bound (64), not the **banked depth value itself** against its expected sequence. It is plausible (not verified this pass — geddump.icn's own current run hits an unrelated, likely pre-existing, `gedload`-side obstacle before gedwalk recurses meaningfully; see "Also observed" below) that gedwalk's garbage happened to stay under 64 for that one input, the same "worked by accident, not by correctness" shape this row's own leafsib/clobarm/ab findings have repeatedly surfaced elsewhere in this codebase.

## Root cause 2 (independent, still real even if root cause 1 is fixed): the reservation formula gives a self-recursive generator's *sibling* callee only one slot, not N

`solvequeen` calls two generators from its own body: itself (`solvequeen(c+1)`) and `placequeen(c)`, a **separate, non-recursive** generator. `icn_gen_host_slice`'s self-recursion branch (`src/templates/x86/x86_asm.h` ~line 935) reserves `(N2_SELFREC_SLOTS-1)` copies of **solvequeen's own** per-activation size only:
```cpp
if (icn_genframe2_selfrec() && i == nvisited - 1) { *out_bytes = (N2_SELFREC_SLOTS - 1) * (((fb + 15) & ~15) + 48); return 1; }
```
`placequeen`'s own slice is summed **once**, elsewhere in the same walk (as an ordinary sibling call node), never multiplied by N. But at runtime, the call-site address for `placequeen` is a **fixed compile-time offset from the current activation's own `rbp`** (`bb_call_proc_staged.cpp` ~line 776, `lea rcx,[rbp + n2_base + n2_off]`) — and `rbp` itself advances by one `solvequeen`-slot-size (512 bytes, confirmed below) at every recursion level. So **every** recursive activation of `solvequeen` computes its own, distinct `placequeen` region at `rbp_D + 32304`, but only **one** 864-byte `placequeen` slot was ever reserved for the whole chain, appended once after the 63-deep self-recursion table.

**Verified numerically** (compiled constants, cross-checked against gdb-observed addresses, `n=6` board):
- `solvequeen`'s own registered frame size: `frame_total = 0x1d0 = 464` (the `lea rbp,[rax+0x1d0]` in its prologue) → per-slot size `align16(464)+48 = 512`.
- `placequeen`'s own frame size: `frame_total = 0x330 = 816` → its own slot `816+48 = 864`.
- Self-call region offset (`n2_off`) = `0` (scanned first in `solvequeen`'s own body); `placequeen`'s offset = `0x7e30 = 32304 = 48 + 63*512` — exactly `(N-1)` self-rec slots, confirming the table size and scan order both measured correctly.
- `main`'s carve: `sub rsp, 0x8640 = 34368` = `736 (main's own frame_total+16, RSP-relative branch) + 512 (solvequeen's own base slot) + 32256 (63-slot self-rec table) + 864 (placequeen's one slot)` — exact match, confirming the *reservation* arithmetic is internally consistent (this is **not** an off-by-one in the size formula itself).
- `rbp` genuinely advances by exactly 512 bytes per recursion level (`rbp_1 - rbp_0 = 0x7ffffffe6198 - 0x7ffffffe5f98 = 512`, gdb-measured) — the region hand-off geometry is correct and depth-independent by construction (each activation's own prologue adds its own `frame_total` on top of the fixed `rbp+48` its caller computed, which is what makes the whole chain self-similar).
- `placequeen`'s computed region offset from the top of the reserved window: depth 0 → `33512` (fine, window is `34368`), depth 1 → `34024` (344 bytes of margin left), **depth 2 → projected `34536`, 168 bytes past the end of the entire reservation.** `solvequeen`'s actual recursion depth for a 6x6 board reaches ~7 (bounded by column count, per seat05's own read of the source) — well past where this drifts out of bounds.

**Why gedwalk doesn't hit this**: `gedwalk` (`suspend r | gedwalk(!r.sub)`) calls no *other* generator from its own body — `!r.sub` is an apply-generator consumed as an argument expression (`bb_call_value.cpp`'s territory, a separate, already-filed gap: `icon-apply-to-generator-segv-bb-call-value-has-no-n2-awareness`), not a second peer generator call through this mechanism. With no sibling generator call to under-reserve, root cause 2 has nothing to bite on for `gedwalk` specifically — it is a real gap only when a self-recursive generator's own body *also* directly calls a different, non-recursive generator, `genqueen`'s exact shape.

## Neither root cause is a storage-*location* design question

Both are implementation bugs in the already-agreed design (per-activation storage nested in the enclosing caller's carve), not new instances of the open "where does per-activation storage for *general* recursion live" question this row's GOAL routes to Lon/hq. Root cause 1 is a narrow, mechanical fix (match the selfrec branches' push count to the already-existing 5-slot contract). Root cause 2 needs an actual decision — multiplying every sibling-generator slice by N unconditionally would over-reserve for the common case (a self-recursive generator with several non-recursive generator calls, most of which are typically not live simultaneously across all N depths); a more precise formula needs the row's own careful, gdb-verified treatment before landing, matching this row's existing standard for touching this file. **Not fixed here** — consistent with every prior session's discipline on this exact code (`icn_gen_host_slice`/`icn_gen_host_reserve`/`bb_call_proc_staged.cpp`'s N-2 region hand-off), and with `SCRIP_ICN_N2_SELFREC` being default-OFF and independently armed, so this changes nothing about any currently-graded board.

## Also observed, not chased down (flagging, not claiming)

`geddump.icn`'s own end-to-end run (the row's actual DONE-WHEN target), armed, against its real `.dat` input: **does not reach the crash class above at all.** Unarmed, it refuses `[GENHOST] host=proc_gedload ... recursive/cyclic (unsupported)` — consistent and expected, since `gedload` calls `gedsub` (the file's *other* directly-self-recursive generator, per this row's own baton) and the unarmed cycle-refusal is working as designed. Armed (`SCRIP_ICN_N2_SELFREC=1`), it instead hits `** Error 3 -- Erroneous array or table reference`, rc=1 — a plain Icon semantic error, not a crash, and it happens very early (before gedwalk itself appears to recurse meaningfully, from a one-call gdb trace). This resembles (title match, not confirmed identical) `FINDING-2026-08-29-seat15-n2-armed-generator-value-as-table-subscript-collapses.md`'s class of bug, but that finding's own text explicitly excludes `geddump` ("geddump/tgrlink are unchanged -- both still hit the documented forward-reference refusal") and cites a different symptom (silent collapse, not a hard error) against a different program (`concord`) and a different genhost site (`proc_event`, not `proc_gedload`) — so this is not a confirmed duplicate, just a plausible relative. **Not investigated further this pass** (out of budget for this sitting, and orthogonal to the two root causes above, which is what this row's own baton asked for). Whoever continues `geddump.icn` specifically should re-run the real oracle first (`icont`/`iconx`, confirmed here: rc=0, 12568 lines, matching this row's own previously-cited count) and treat this Error-3 as its own, separate small investigation before assuming either root cause above is the thing standing between `geddump` and green.

## Reproduction

```
SCRIP_ICN_N2_SELFREC=1 ./scrip --compile -o /tmp/genqueen.s corpus/tests/icon/rung36_jcon_genqueen.icn < /dev/null
as -g -o /tmp/genqueen.o /tmp/genqueen.s && gcc -no-pie -g -o /tmp/genqueen.bin /tmp/genqueen.o SCRIP/out/libscrip_rt.so -Wl,-rpath,SCRIP/out
# mode 4: hits the loud (but FALSE -- garbage-triggered) N2_SELFREC_SLOTS bomb after 2 activations
# mode 3: SCRIP_ICN_N2_SELFREC=1 ./scrip --run corpus/tests/icon/rung36_jcon_genqueen.icn < /dev/null  ->  SIGSEGV rip=0x3 rsp=0xffffffffffffffde
```
