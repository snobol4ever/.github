# FINDING 2026-08-10e — WREG-0 s14 (Claude Opus 5)
## The RTCC veneer that would preserve γ/ω is a FLAT GLOBAL CELL, so s13's "RTCC makes WREG viable" argument inverts under nesting — and nesting is the defining shape of the case WREG exists to serve

**Watermark:** SCRIP `353bafbd` (parent `802cf6bd` == s13b close; nothing moved under this seat) · corpus `bea31de0` UNTOUCHED · `.github` this commit.
**⛔ PUSH STATUS:** BLOCKED — no credential supplied this session. `353bafbd` + s13/s13b's four commits are all UNPUSHED. See the handoff line at the bottom.

---

## 1. THE INSTRUMENT WAS COUNTING LINES, NOT MENTIONS — SWEEP IS 506, NOT 416 (repaired, `353bafbd`)

`test_gate_wreg_claim.sh:78` is `n=$(strip_comments "$f" | grep -cE "$REGPAT")`. **`grep -c` counts matching LINES.** s13 published 234 + 182 = 416 under the label `mentions remaining`; those are line counts, and a line carrying both registers counts once — there are **10 such lines in `bb_call_fn.cpp` alone** (`lea rΓ` / `lea rΩ` pairs are the natural spelling, so the both-regs-one-line case is not rare, it is the *idiom the ladder itself specifies*).

Measured, comment-stripped, word-bounded:

| region | lines (s13's number) | TRUE occurrences | gap |
|---|---|---|---|
| templates + emitter | 234 | **283** | +21% |
| RTX hand-written asm | 182 | **223** | +23% |
| **TOTAL** | **416** | **506** | **+22%** |
| `bb_call_fn.cpp` | 82 | **97** | |
| `rtx_match.S` | 74 | **89** | |

**The sweep is 2.8× LADDER WREG's budgeted 178, not the 2.3× s13 computed.** The gate now prints both columns — LINES stays primary and comparable with every number s13 recorded, OCCURRENCES is the honest edit surface — and `--strict` fails on occurrences. `grep -o | wc -l` is SIGPIPE-safe by the same argument the s11 conviction makes for `grep -c`: `wc` reads to EOF and never closes the pipe early.

⭐ **This also dissolves s13's own internal 45-vs-82 discrepancy.** The cursor says *"size each file from the gate's stdout, not from the ladder's per-file text (bb_call_fn is 45, not 36)"* — but the gate's stdout says **82**. Neither is wrong: **45** is the *quoted-only* line count from the drift check (`grep -coE '"r1[01]"'`, also a line count), **82** is the *all-spellings* line count, **97** is the truth. Three instruments, three units, cited as commensurable. The instruction was right; it was aimed at a mislabelled unit.

---

## 2. ⛔⭐⭐ THE LOAD-BEARING FINDING — s13's STRONGEST PRO-WREG ARGUMENT IS THE HAZARD

s13's cursor offers an argument it says *"the ladder undersells"*:

> *"a scratch-tier RTCC claim is exactly what makes a register survive a C-RT crossing without the holder saving it, which is precisely what a blob's γ/ω need across every `rt_*` call. RTCC's veneer is not merely compatible with WREG; it is what makes register-carried wires viable at the runtime boundary."*

**The mechanism is real and I can see it in the emitted asm.** Compiling `corpus/probe/ab_defer_call.sno` (`--compile` writes asm to **stdout** — note for the next seat) under both arms and diffing isolates the veneer exactly:

```
>   mov qword ptr [rax + 56], r10          <- save  γ-slot at every crossing
>   mov qword ptr [rax + 64], r11          <- save  ω-slot
>   mov r10, qword ptr [r11 + 56]          <- restore, ×many
```

**But the save area is FLAT.** `rtcc.h:63` — `extern uint64_t g_rtcc_block[32];` · `rtcc.h:33` — `#define RTCC_SLOT_R10 7` (byte 56, matching the asm) · `rtcc_init.c:19` — `__attribute__((aligned(64))) uint64_t g_rtcc_block[32];`. **One slot per register, process-wide. No depth index. No stack. No per-activation discipline.** The header's own seeding comment calls the R9 case a *"BLOCK-CANONICAL EXCEPTION for constant globals"* — i.e. the block is designed for values that are constant or non-nested.

### The composition failure, by construction

```
outer blob:  r10 = γ_outer
  veneer saves γ_outer -> block[7];  call rt_X
    rt_X re-enters emitted code (deferred *F() mid-match)
      inner blob: r10 = γ_inner
      veneer saves γ_inner -> block[7]     <-- γ_outer DESTROYED
      inner returns: restores r10 = block[7] = γ_inner   (correct for inner)
  outer veneer restores r10 = block[7] = γ_inner          <-- WRONG
```

A flat cell cannot serve a LIFO discipline. **This is `g_blob_ctx`'s single-cell defect in register clothing** — the exact conviction this goal file already carries at `pattern_match.c:624`, and the exact objection LADDER WREG's own ONE LAW was written to pre-empt ("*a bare global pair IS g_blob_ctx's single-cell defect in register clothing*").

### Why the ONE LAW does not already cover this

WREG's ONE LAW makes pendings per-activation **on the spine** (*"every pending cell pushed INSIDE a blob captures {r10,r11} at push; its β-resume restores them"*) and argues soundness from spine pop-order. That argument is sound and I am not disputing it. **It does not reach the veneer**, which is a *different save area on a different discipline*: spine = per-activation LIFO, veneer = per-process flat. Composed, the second breaks the first. The ONE LAW's "per-activation-correct by construction" holds for blob-interior pendings and is silent on C-RT crossings.

### And nesting is not the exotic case — it is THE case

The witness that exposes this is not contrived; it is `ab_defer_call.sno`, whose own header reads *"function called MID-MATCH via deferred `*F()` — activation opens while the match registers are live."* That is the SPITBOL deferred-evaluation operator (manual p.86), and the manual is explicit that SPITBOL matches **exhaustively with no Quickscan heuristics**, so *"deferred expressions are not assumed to match at least one character, and recursive patterns always work properly"* (p.123). **The language guarantees the re-entrant shape.** A blob calling a DEFINE'd function mid-match, that function itself crossing into `rt_*`, is ordinary SPITBOL, and it is precisely the traffic WREG's wires exist to carry.

### ⛔ CONSEQUENCE FOR THE "ONE-LINE EDIT WREG-2 MUST NOT FORGET"

s13 flags a mandatory edit: extend `LIVE_CLAIMS` in `test_gate_rtcc_claimed_regs.sh` to `r10:GAMMA:WREG-2 r11:OMEGA:WREG-2`, because *"that second edit is what buys WREG the H2 veneer-writeback protection; skipping it re-runs the s6/s7 r9 story on r10."* **That protection is the flat cell.** Buying it as-specified buys the nesting hazard. The edit is not wrong to make, but it is **not sufficient and not safe alone** — recording it here so the next seat does not make it and believe the boundary is closed.

### The cheaper fix, offered as design input, NOT as a landed decision

If r10/r11 become **globally reserved wires** rather than scratch, the veneer should **exclude them from the block entirely** rather than save/restore them: a reserved register is invariant across the crossing *by convention*, any C-side clobber is a bug the claim gate exists to catch, and excluding them is strictly cheaper (2 fewer stores + 2 fewer loads per crossing — and the ab_defer_call arm shows **190 r10 mentions in one small program**) *and* removes the LIFO violation at the root. The alternative — making `g_rtcc_block` depth-indexed — is a real stack, i.e. the thing the FORTH spine already is, duplicated.

---

## 2b. ⛔⭐⭐⭐ RECONCILIATION WITH s13c — SAME MECHANISM, OPPOSITE CONCLUSIONS, AND COMPOSED THEY ARE WORSE THAN EITHER

**`23355182` (s13c) landed at 23:22:46, seven minutes before this seat's commit, and this seat did not see it while measuring** — a second STALE-ORIENTATION strike in one session, in the same container, after §5's warning was already drafted. Recorded against myself, not softened: **re-read HEAD immediately before committing, not only at open.**

s13c reached the SAME mechanism independently (`x86_rtcc_wb_bin` stores `[block+56]=r10` / `[block+64]=r11`; `x86_rtcc_rl_bin` restores the scratch tier) and drew the OPPOSITE conclusion — that the veneer is a *guarantee*, yielding two claims:
- **s13c COROLLARY:** *"the 182 RTX asm sites need NO sweep"* — sweep self-corrected 416 → 234.
- **s13c DECIDING FACT:** the hazard is that `g_rtcc_on = 0` by default, so at RTCC=OFF every `rt_*` call is bare and the wires die by plain SysV rules ⇒ *"WREG requires RTCC=ON as a CORRECTNESS precondition."*

**Both of us are partly right, and the union is the real picture:**

| | RTCC = OFF | RTCC = ON |
|---|---|---|
| **single (leaf) crossing** | wires clobbered — SysV scratch (**s13c**) | wires survive — veneer banks/reloads |
| **nested / re-entrant crossing** | wires clobbered (**s13c**) | **outer γ destroyed by the inner save (this seat)** |

⛔ **THERE IS NO RTCC SETTING AT WHICH THE VENEER IS A SOUND WIRE-SURVIVAL MECHANISM FOR THE DEFERRED-MID-MATCH SHAPE.** Confirmed by design intent, not inference: `x86_asm.h:299` documents the writeback as *"writeback all 9 GPRs to g_rtcc_block **WITHOUT touching RSP**"* — deliberately not stack-based — and `depth|stack|nest|reentr|push|save_area` returns **zero hits** across `rtcc.h` + `rtcc_init.c`. Flat by construction.

### Two corrections this forces on s13c, neither of them cosmetic

**(a) s13c's routing option (3) does not close the hole it is offered to close.** s13c presents three options and calls (3) *"RTCC goes default-ON as a WREG prerequisite"* the **cleanest**. It is not: flipping RTCC ON fixes the leaf column and leaves the nested cell unrepaired. Of s13c's three, only **(2)** — *"WREG-2 emits its own save/restore when RTCC is off"* — can be made nesting-correct, and **only if that save is per-activation on the FORTH spine (WREG's own ONE LAW) rather than in a flat block.** The honest reading is that (2) generalises: WREG needs a per-activation wire save **regardless of RTCC's setting**, and RTCC then becomes an optimisation for the leaf case rather than the survival mechanism. s13c's own aside — *"'NO SHIM is literal' quietly stops being literal"* — is the correct instinct, and it applies to all three options, not just (2).

**(b) s13c's RTX exemption is CONDITIONAL, and it fails precisely where it matters most.** The exemption argues that what `rtx_match.S` does to the pair inside a call is invisible to a caller that banked and reloaded. True for a **leaf** call. False when the callee re-enters emitted code that crosses again — and `rtx_match.S` **is the match runtime**, i.e. the one file where deferred `*F()` re-entry is not an edge case but the design. So the 182/223 RTX sites are **exempt for leaf crossings, not exempt for `rtx_match.S` (74 lines / 89 occ)** — the very file the Lon-directed bulletin already named *"the sharpest edge in the product"* on independent grounds. **Sweep arithmetic, honest:** 283 occ unconditionally + 223 occ conditionally-exempt, of which `rtx_match.S`'s 89 are not safely exempt at all.

⭐ **What survives from s13c untouched and is genuinely load-bearing:** the observation that WREG is specified **default-ON at WREG-2 on top of a default-OFF RTCC**, i.e. *"that combination ships wires with no survival mechanism."* That is correct, independent of everything above, and is the single most schedule-relevant fact either seat produced.

---

## 3. STATUS OF s13's ITEM (2) — `AB_TC_REG` PROBE: CHARACTERIZED, NOT CLEARED

s13 recorded the r10 collision at `bb_func_activate.cpp:25` as *"collided, not as broken and not as cleared."* Confirmed independently and **the dormancy is now source-verified rather than asserted**: `rtcc_init.c:20` `unsigned char g_rtcc_on = 0; /* default OFF — killswitch law */` · `rtcc.h:57` `RTCC_GLOBAL_R9_GVA 1` ⇒ `AB_TC_REG = (0 && 1) ? "r10" : "r9"` = **r9 in every default build**. Two seats, two routes, same verdict.

Behavioural probe, both arms, m3, `ab_defer_call` (a PASSING witness — chosen deliberately, since `ab_freturn` is one of the 5 known pre-existing probe failures and cannot discriminate): **RTCC=0 PASS · RTCC=1 PASS**, both byte-equal to `.ref`. So the collision is **not live today** — as expected, because nothing else claims r10 until WREG-1 lands.

⛔ **HONEST LIMIT OF THIS RESULT:** the hazard in §2 is derived **by construction from a measured mechanism** (flat block + save/restore at every crossing, both read from source and seen in emitted asm). It is **not** demonstrated by a failing program, and it cannot be until γ actually rides r10. **Recorded as a characterized hazard, not a measured failure** — the same standard s13 applied to itself.

**The probe that settles it, the day WREG-1 lands:** `ab_defer_call.sno` under `SCRIP_RTCC=1` with wires live, watching `block[7]` across the nested crossing — outer γ must survive the inner activation. If the veneer still saves r10, it will not.

---

## 4. NEXT SEAT

1. **Route the §2/§2b question before WREG-1 — and route it on BOTH seats' evidence, not either alone.** s13c's three options are the right frame; the correction is that (3) does not close the nested cell and (2) only closes it if the save is per-activation on the spine. Owner problem is real (GOAL-RTCC owns the veneer, this goal owns the wires), so this is **Lon's routing call**, not a seat's drive-by.
2. **Re-state LADDER WREG's sweep-cost line as 283 unconditional + 223 conditionally-exempt occurrences**, per-file in occurrences (`bb_call_fn` 97 · `rtx_match.S` 89, the latter NOT safely exempt). The ladder's 178, s13b's 416, and s13c's 234 are three different units and two different scopes; none is usable as written.
3. m4 column + broad-336 **still owed** from s8/s12b — untouched by this seat.
4. `128` and `151` own MONITOR-FIRST rungs — untouched.

## 5. ENVIRONMENT — ⛔ A CONCURRENT SEAT COMMITTED INTO THIS WORKING COPY MID-SESSION

Reflog, `.github`: clone at `37e0273c` 22:44:04 → `commit 47946ebb` **23:12:25** → `commit 9b18fe4d` **23:14:29**, none of them this seat's. **s13 and s13b ran in this same container and this same checkout**, and orientation performed at 22:44 was two commits stale by 23:14 — the goal file grew 366 → 400 lines *underneath a completed read*. 11-ENV's shared-container warning is not historical; it is current. **Re-check the cursor's own HEAD before trusting an orientation, not just at open.**

The seat left idle (no live `make`/`gcc`), tree clean, `scrip` + `out/libscrip_rt.so` built at 23:09 — which is the only reason this seat could measure without a rebuild collision.

⛔ **AND IT LEFT FOUR COMMITS UNPUSHED** (SCRIP `1d81b015` `802cf6bd`; `.github` `47946ebb` `9b18fe4d`), now five with `353bafbd`. This is the precise shape RULES.md convicts hardest — *"a pushed rung is never lost; an unpushed one routinely is (s9/s10 lost two sessions of RTCC work; s19–s26 stranded eight sessions and BUG-7 was re-derived from scratch)."* Credential was requested in-chat this session per RULES.md 6b and has not yet been supplied. **HANDOFF IS BLOCKED. No terminal doneness claim is made here, and `handoff_status.sh` has not been run because it would report BLOCKED and that is already known.**
