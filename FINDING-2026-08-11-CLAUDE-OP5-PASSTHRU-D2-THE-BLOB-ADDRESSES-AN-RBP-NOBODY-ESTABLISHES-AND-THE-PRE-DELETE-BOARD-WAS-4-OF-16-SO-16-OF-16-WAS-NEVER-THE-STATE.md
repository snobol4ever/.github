# FINDING 2026-08-11 — CLAUDE-OP5 — PASSTHRU D-2: THE BLOB ADDRESSES AN RBP NOBODY ESTABLISHES, THE ARBNO COLLISION IS AT ONE LITERAL OFFSET, AND THE PRE-DELETE BOARD WAS 4/16 WITH ZERO SEGVS — SO 16/16 WAS NEVER THE STATE AND WREG STEP 1 AS WRITTEN IS VACUOUS

**Seat:** Opus 5, 2026-08-11. **Fingerprint at open:** SCRIP `69e5f380` · corpus `5da04e78` · `.github` `6afbe373`.
**Landed:** SCRIP `c25b8e00` (D-2 record protocol off the spine) + `5fbefd41` (debt-sizing probe). Both killswitch-gated, both OFF byte-identical to `69e5f380` by md5 over the calculator-1 artifact.

---

## 1. ⛔ WREG-COMPLETE STEP 1 AS WRITTEN IS VACUOUS AND ITS CHOKE IS THE WRONG ONE

The cursor directs: *"At the ONE choke `x86_align_enter/leave` (both media), push/pop {r10,r11} around every `call rt_*`."* Three measured corrections, any one of which sinks it as written:

1. **Both functions early-return EMPTY under the default `ZC_FRAME_RSP` regime** (`x86_asm.h:1863`/`1868` — *"under the RSP default both halves are a no-op"*). A bracket added inside them emits **nothing** in the shipping configuration. Step 1 as specified is a null.
2. **They are not the choke.** `x86_align_enter()` appears at **37** sites; `x86("call", …)` appears at **349**. The real C-call funnels are `x86_rtcc_call` (void/int/ptr), `x86_rtcc_call_descr` (DESCR_t), and `x86_call_ro` (bare) — which are *already* the RTCC veneer chokes, i.e. the same three the s13/s13b/s14 veneer argument is about.
3. **The bracket is forbidden at that choke by a standing law.** `x86_asm.h:300`: *"RSP-SAFETY LAW: the veneer fires inside templates that may have live ζ cells on RSP. **NO push/pop allowed**."* This is in direct conflict with s15f's corrected routing, which named the stack-pair `push r10/r11 · call · pop` as *the only live candidate* after retracting option (c). **The file currently holds both positions and they cannot both stand.** Not resolved here — it is a Lon routing call, and it straddles GOAL-RTCC exactly as s14 said.

⭐ Consequence for the ladder: Steps 2–4 are unaffected in principle, but **Step 1 must be re-specified against the rtcc_call chokes before a seat spends on it**, and the RSP-SAFETY conflict answered first.

---

## 2. ⭐⭐⭐ THE D-2 DEFECT, ROOT-CAUSED TO THE BYTE — AND THE COLLISION IS AT ONE LITERAL OFFSET

**Mechanism (artifact, not inference).** DEL-T1 dropped `flat_pat` from `emit_jmp_pin_rbp()`, so a PAT$ blob's prologue establishes **no rbp**. Measured at HEAD, `proc_PAT$0_α` is `sub rsp,144` + wire/δ saves + the g_zctx cell push — carrying neither `push rbp` nor the heap-adopt `mov rbp,rdi`. But `lower_snobol4.c:2408` and `:2631` set `resumable_callable = 1` on **every** patproc and RT recipe graph, so `emit_heap_fb_adopt()` keeps `emit_rec_pin()` true and the blob still **addresses through an rbp nobody established**. Exactly **four** refs per blob:

| ref | site | authority |
|---|---|---|
| `mov [rbp+80], rax` (resume-slot store, α) | emit.cpp record site | `emit_rec_fb()` |
| `jmp qword ptr [rbp+80]` (β dispatch) | emit.cpp record site | `emit_rec_fb()` |
| `mov [rbp+48], r14d` (capture δ save) | `FR()` | `x86_fb_pinned()` |
| `mov eax, [rbp+48]` (capture δ read) | `FR()` | `x86_fb_pinned()` |

**⛔ THE COLLISION IS LITERAL, NOT ANALOGICAL.** The enclosing ARBNO emits `mov qword ptr [rbp + 80], rsp` — it stores its own frontier pointer at **the same offset off the same register** the blob writes its resume continuation to. "Leaks the ARBNO view into the invoker" is not a metaphor for aliasing: it is one address, written by two owners. Under a MATCH_BEGIN statement head this is survivable (claws5 passes — it is defer-free); inside an ARBNO body it is the casualty set.

**THE GEOMETRY THAT MAKES THE CURE FREE (measured invariant, every blob):** carve `kt`; activation cell `C = base+kt-40` (γ wire `C+16`, ω `C+24`, own-base `C+32` — proved by ω's `lea rsp,[C+40]` absolute unwind); **resume slot at `base+kt-64` == `C-24`**. kt 144/128/176 → slot 80/64/112, cell 104/88/136 — difference **−24 in all three**.

**Landed (`c25b8e00`):** α stores off **rsp** (that site is the chain head, before any interior carve, where rsp *is* the flat base — so only the base register moves, the offset is untouched); β dispatches off **the cell pointer in rax**, which `res` has just popped, because rsp at β is the DEEP frontier (non-popping spine), not the flat base. Registers + stack only, **zero globals added** (RULING 3). `emit_rec_rsp_arm()` (emit.h) is the **ONE AUTHORITY** — all four refs read it, so store and load cannot pick different base registers (the s158 land mine this file convicts repeatedly). Scope is exactly the orphaned class (`flat_pat && !emit_jmp_pin_rbp()`); genuine heap-fb activations (gen-proc, Prolog resumable) are untouched, because there the frame really is in rbp and `pop rsp` of a heap base is the 44-test backtrack SIGSEGV.

**Verified:** all four orphaned rbp refs inside the blob → **0**. `SCRIP_REC_RSP=0` byte-identical.

**⛔ NECESSARY, NOT SUFFICIENT — stated plainly so nobody reads this as the repair.** Board unchanged at 1/16.

---

## 3. ⭐⭐⭐ THE SURVIVING CLOBBERER IS ON T1'S OWN KILL LIST AND WAS NEVER REMOVED

Pre-delete prologue (`930539c0`) vs HEAD, same program, same blob:

```
PRE:   sub rsp,144 · mov [rsp+120],rcx · mov [rsp+128],rdx · mov [rsp+136],RBP · mov RBP,rsp · ...
HEAD:  sub rsp,144 · mov [rsp+120],rcx · mov [rsp+128],rdx · mov [rsp+136],RSP · <g_zctx cell push>
```

D-1 removed **both** the caller-rbp **save** and the frame **establishment**. But the **in-blob top-level ARBNO still rebases rbp** (`mov rbp,rsp`, `lea rbp,[rax-88]`) — which is item one on T1's own "Dies with it" list (*"in-blob legacy ARBNO rbp rebasing"*) and **was never deleted**. Previously the blob's save/restore contained that clobber; now it **escapes into the invoker**. The ARBNO-LON frameless arm that would retire it is default-ON but **gated to the nested-K0 class** (`op_arbno_framed && op_arbno_body_k0`); a *top-level* ARBNO inside a blob is not nested, so it takes the legacy chain arm. Widening that gate is ζ-MECH's cursor, which is exactly the collision the ROUTING note at the foot of this goal file already predicted.

---

## 4. ⭐⭐⭐ THE NUMBER NOBODY HAD: THE PRE-DELETE BOARD, AND WHAT IT RETIRES

Built `930539c0` in a worktree and ran the same 16-program board, same container, same refs:

| tree | m3 PASS | failure shape |
|---|---|---|
| `930539c0` (pre-DEL-T1) | **4 / 16** | **zero SEGVs** — every failure a DIFF |
| HEAD + `c25b8e00` | **1 / 16** | mostly rc139 SEGV |
| HEAD + `SCRIP_PROBE_PATPIN=1` | **1 / 16** | most SEGVs revert to DIFF |

**Three things this retires:**
- ⛔ **"16/16" was NEVER the state.** The board was 4/16 before the delete. The DIFF set is **older, separate debt** and must stop being billed to DEL-T1. Any future "restore the demos" framing that assumes a green pre-state is measuring against a tree that never existed.
- ⭐ **The delete owns the CRASH class, and only that.** Re-pinning alone (probe ON) converts most SEGVs back to DIFFs and recovers **zero** passes. So the pin is the crash-class owner; correctness is owned elsewhere. **The debt is two defects, not one, and paying the pin half will look like progress on the crash census while moving the board by nothing.**
- ⭐ The regression is `4 → 1`, i.e. **3 programs**, not the "7-PROGRAM DEMO REGRESSION" this file records. That figure is stale or scoped to a different set.

**Bisect (automated, predicate = calculator-1 m3 vs .ref):** good `930539c0` → bad `c25b8e00`; walked to `36997bc8` bad → `942ef1b1` bad → `1f5824a7` bad → `1f96143c` bad, with `1af93e3a` (D-1) **unbuildable standalone (skip)**. First buildable bad = **`1f96143c` (DEL-T1 D-2)**. So the correctness break traces to the DEL-T1 pair itself, compounded by the 36 commits since — **not** to an independent later defect. That is consistent with this file's own story and closes the question of whether something else snuck in.

---

## 5. NEXT SEAT, IN ORDER

1. **Lon routes the Step-1 conflict** (§1): `x86_align_enter/leave` is a no-op and not the choke; the real chokes forbid push/pop by standing law, which contradicts s15f's only-live-candidate. Re-specify Step 1 or answer the RSP-SAFETY law.
2. **The ARBNO rbp rebasing is the live clobberer** (§3). Either widen the frameless arm past the nested-K0 gate, or make the ARBNO self-preserving. This is ζ-MECH's zone — coordinate, do not drive-by.
3. **Stop chasing the DIFF set as DEL-T1 debt** (§4). It predates the delete. Size it on its own before spending a seat.
4. **The tree is ASLR-flaky on these programs** — calculator-1 reported DIFF and rc139 on consecutive identical invocations. Any single-run board number is unreliable; take best-of-N or the failure will oscillate under you, as the M4 oscillation notes already warn.
5. m4 column untouched this seat (m3 only). Regen ×3 not run — this session changed emitter code, so **regen is owed** before any artifact comparison is trusted.

**HONEST LIMITS:** MONITOR-FIRST was not used — the shipped `SCRIP_FB_DIVERGE` instrument plus disassembly carried the diagnosis, and FF-0 was already documented CLOSED WITH MECHANISM, so re-deriving it was declined deliberately. The `[rax-24]` β dispatch is proved correct for the res→β path (rax is the cell, just popped); **β predecessors other than res were NOT enumerated** — if one exists, that dispatch reads a stale rax and it will present as a wild jump. That audit is owed before `SCRIP_REC_RSP` is treated as settled.
