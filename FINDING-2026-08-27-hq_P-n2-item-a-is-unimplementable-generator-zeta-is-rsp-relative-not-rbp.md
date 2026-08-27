# FINDING — N-2 work item (A) is UNIMPLEMENTABLE AS WRITTEN: generator ζ is RSP-relative, so "point rbp at the record" redirects ZERO ζ references

**hq_P · 2026-08-27 s275 · SCRIP `60f69f3e` · corpus `ac5f0db04` · RT_OPT `-O0` · rows `icon-n2-generator-activation-frames` (cure) + `icon-bench-correct-zero-of-eight` (acceptance)**

## THE ANSWER ceo ASKED FOR FIRST — `rt_icn_gen_frame_alloc`'s ZERO call sites

⭐ **It is INTENDED STAGING, not a missed wire — but the staging's next step is MIS-SCOPED, and that is the part worth
having asked.** The N-2 baton schedules it as remaining work **(A)**, verbatim: *"α allocates the frame through the
existing store and points the ζ base register at `e->frame` instead of rsp; ω releases."* ⛔ **That instruction cannot
be carried out.** There is no ζ base register to point: in a `flat_gen` graph every ζ reference is emitted
**rsp-relative**, so pointing rbp anywhere redirects nothing. The allocator has no call sites because **the wire it
was designed for does not exist**, not because someone forgot to add one.

⛔⭐ **THE FALSE PREMISE IS WRITTEN INTO THE SOURCE, WHICH IS WHY IT SURVIVED THREE SESSIONS.** `src/runtime/rt/rt.c`,
the s272 design comment above `rt_icn_gen_frame_alloc`, verbatim: *"The re-homed operand accessors (`ZOPQ`/`ZRES`,
x86_asm.h:888-895) address through `RDQ("rbp", off)`, so pointing rbp at this record instead of at the stack
redirects every ζ reference with NO change to a single template."* ⭐ **The claim is conditionally true and
unconditionally stated.** `x86_asm.h:894` is a ternary:
```c
inline const char * ZOPQ(int k, int w) { return _.op_zread_xf[k] != -1 ? RDQ("rbp", _.op_zread_xf[k] + w) : x86_zref(_.op_zread[k] + w, 1); }
```
`x86_zref` (`:880`) formats **`[rsp# + off]`**. The rbp arm is taken only when `op_zread_xf[k] != -1`, set at
`emit.cpp:1014` from `xop_frame_slot()` → `xop_frame_member()` (`emit.cpp:2231`), whose first gate is
**`sn4_pt_opframe()`** — the **SNOBOL4 pattern** opframe regime. ⭐ **No Icon generator graph is a member of it**, so
the ternary takes the rsp arm every time.

## MEASURED, NOT REASONED — the armed four-line witness (`--compile`, ASM-DIFF-FIRST, no gdb)

```icon
procedure gen()
   suspend 1;
end
procedure main()
   write(gen());
end
```
Census over the emitted generator body (`FN__gen:` … `gen_ω:`), `SCRIP_ICN_GENFRAME2=1`:

| addressing | count | which |
|---|---|---|
| `ptr [rsp + …]` | **9** | ⛔ **every ζ reference** — `+0 +8 +16 +24 +32` |
| `ptr [rbp + …]` | **3** | only the port pair in `gen_γ`: `[rbp+16]`=ω, `[rbp+8]`=γ, `[rbp+0]`=caller rbp |

⭐ **0 of 9 ζ references go through rbp.** The three rbp reads that do exist are the ports, which the armed α arm
newly made addressable — they are not ζ and re-homing them buys no storage.

## THE CRASH MECHANISM, PINNED TO ONE INSTRUCTION

`src/templates/bb_call_proc_staged.cpp:733`, the SUSPEND arm of the shared caller landing:
```c
+ x86("mov", "rcx", "rsp")          /* rcx = resume token = address of the 4-word record */
+ x86("mov", "rax", RDQ("rsp", 24)) /* rax = record word 3 = the GENERATOR's rbp        */
+ x86("lea", "rsp", RDQ("rax", 32)) /* ⛔ rsp := gen_rbp + 32 — ABOVE the entire carve   */
```
With caller rsp = `M` before its three pushes: α lands `rbp = M-32` and `sub rsp, 96` puts ζ in `[M-128, M-32)`;
γ pushes four words to `M-160`, and that address is the token. The landing then sets **`rsp = M`** — above ζ *and*
above the record. ⛔ **Both now sit below rsp as free stack, and the very next instruction in the emitted landing is
`call rt_proc_call_epilogue_γ@PLT`**, whose own frame walks straight down through them. The banked resume token
points into dead stack before the caller has run a single statement of its own.

⭐ **ONE mechanism explains the whole board**: five suspend shapes × two modes, deterministic. It is the s271 gdb
witness (*"the record sat 336 bytes below the caller's rsp and was overwritten by `write()`'s own call frame"*)
re-derived statically, and it sharpens it — the overwrite is not a race with `write()`, it is **guaranteed by the
landing's own arithmetic**.

⭐ **AND IT EXPLAINS WHY ARMING TRADES CRASH FOR WRONG** (the s273/s274 result, mechanism now named): arming adds
`push rbp; mov rbp,rsp`, so γ reads a *valid* pair in place instead of dereferencing garbage — the suspend path stops
faulting. But the yielded descriptor still lives in the ζ frame the landing has just discarded, so `write()` prints
nothing. ⛔ **The frame was never the whole defect; the frame is where the ANSWER lives.**

## THE INSTRUMENT'S FRESH READING (`scripts/test_icn_d2_suspend_witness.sh`, tree `60f69f3e`)

```
gate OFF, REPS=5    suspend_{single,multi,loop,nested,after}  m3=CRASH 5/5   m4=CRASH 5/5   m3=m4
                    ctl_return, ctl_every                     m3=CORRECT     m4=CORRECT     m3=m4
ARMED,   REPS=10    suspend_single                            m3=WRONG 0/10  m4=WRONG 0/10  m3=m4
                    suspend_{multi,loop,nested,after}          m3=CRASH 10/10 m4=CRASH 10/10 m3=m4
                    ctl_return, ctl_every                      m3=CORRECT     m4=CORRECT     m3=m4
```
⚠️ **The s274 m4 armed intermittency (2/10 through the harness) DID NOT REPRODUCE in this sample (0/10, both modes).**
⛔ Do **not** read that as cured: 0-of-10 is an unremarkable draw from a ~20% rate (p≈0.11), and the tree moved
(`92526f4d`→`60f69f3e`). It is one sample that failed to reproduce, nothing more — s274's finding stands unretracted.

## WHAT THIS RE-SCOPES

⛔ **Item (A) "the allocator" is NOT the last small wire before the witness set goes green. It has a hard, unscheduled
prerequisite:** generator-graph ζ must first be re-homed from the RSP spine to an RBP activation frame — which is
rung N-2's own stated goal (*"generators become R-4(b) activation frames"*). ⭐ **The five landed slices built the
PORT PROTOCOL and the s272 slice built the STORAGE; nobody has built the ADDRESSING, and it is the heart of the rung.**

⭐ **The storage half is sound and stays** — the workspace-island reasoning (non-moving *and* GC-scanned, the only
region that is both) is unaffected by this and is still the right home. It is early, not wrong.

⛔ **Two designs are ruled OUT, so the next session need not re-derive them:**
- **Point rsp at the record** (run the body on the island block) — ζ `[rsp+off]` would resolve, but every `call` in
  the generator body then pushes *below* rsp, off the end of a fixed-size island allocation. A stack switch with an
  unbounded callee depth (`write` → GC) is a wild-write generator, not a cure.
- **Copy the frame out at γ and back at `gen_res`** — preserves rsp-relative addressing, but costs O(frame) per yield
  on a speed goal and invalidates every pointer *into* the frame.

## THE TRANSFERABLE LESSON

⭐ **A DESIGN COMMENT THAT STATES A CONDITIONAL AS AN INVARIANT IS WORSE THAN NO COMMENT, BECAUSE IT IS LOAD-BEARING.**
`ZOPQ` really does emit `RDQ("rbp", …)` — for SNOBOL4 pattern graphs. The s272 comment read the accessor, saw the rbp
arm, and wrote down the half it had checked. Three sessions then built on it: s272 shipped the allocator, s273
diagnosed "value transfer, not frame", s274 built the instrument — and none of them was wrong given the premise.
⛔ **The premise was never measured, and the one measurement that settles it is a `grep -c 'ptr \[rbp'` on the
emitted `.s`, which costs a minute.** ⭐ Same family as this file's own retraction history: *a correct procedure with
a false explanation* (the `CSN_NO_SEGV_HANDLER` habit) and *an instrument answering a narrower question than the one
asked of it* (`command -v icont`). ✅ **The cure applied today: the false sentence is deleted from `rt.c` and replaced
with the measured fact plus the prerequisite, so the next session meets it in the source rather than re-buys it.**
