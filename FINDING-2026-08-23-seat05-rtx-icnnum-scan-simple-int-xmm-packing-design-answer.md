# FINDING — rtx-icnnum-icnsub-bail-invariant: the SCAN_SIMPLE_INT design answer (seat05, 2026-08-23)

**Row: `rtx-icnnum-icnsub-bail-invariant`. DONE-WHEN scope: SCAN_SIMPLE_INT only (`SCRIP/src/runtime/rtx/rtx_icnnum.S:39-90`).
`rtx_icnsub.S`'s 39 sites are NOT addressed here — out of scope for this row's grep-checked DONE-WHEN,
stays frozen under the same original ruling. ⛔ NO CODE CHANGE LANDED WITH THIS FINDING — design answer only,
per the row's own gate.**

## 0. THE BRIEF'S OWN EXCLUSION LIST IS STALE — VERIFY-YOURSELF FINDING #1

The row brief (seat13, explicitly unverified: *"did not isolate them"*) says: *"once bail-safety
(rdi/rsi/rdx/rcx) and blob pins (rbx/r12-r15) are excluded there are LITERALLY ZERO free GPRs."*
**`r12` is not a blob pin.** `ARCH-SNOBOL4-RTX.md` §2 (corrected s205), `ARCH-ICON-RTX.md` §2 (icnnum's
actual contract, "IDENTICAL TO ARCH-SNOBOL4-RTX §2"), and `rtx_abi.inc:16` (corrected s219, after the
header itself had contradicted the document "for FOURTEEN sessions") all independently say the same
thing: `ZC_FRAME_R12` was deleted outright, zero `#if` consumers, r12 is free. **`rtx_icnnum.S`'s own
header comment at line 29 ("Blob pins rbx r12-r15") is itself an instance of that fourteen-session rot** —
stale, uncorrected, inherited from before s205. This is not corrected here (see §5, scope) but must be
fixed by whichever rung lands a register change in this file.

This matters because it changes the register inventory from "4 non-excluded GPRs" (rax r8 r9 + one of
r10/r11) to potentially 5 (rax r8 r9 r12 + one of r10/r11) — the difference between the row being
unsolvable and half-solvable, as §3 shows.

## 1. GROUND TRUTH: WHAT SCAN_SIMPLE_INT ACTUALLY DOES (measured from source, not inferred)

```
#define SCAN_SIMPLE_INT(SRC, ACC, ACC32, PTR, CNT32, SGN8, SGN32, DIG, DIG32, SFX)
```
Both call sites (`rtx_icnnum.S:103,126`) bind identically:
`SRC=rdi/rsi(per-call) ACC=rax PTR=r11 CNT=r9d SGN=r10b/r10d DIG=r8/r8d`.

Per-value liveness, read directly from the macro body (`:40-90`):

| value | reg | live window | role |
|---|---|---|---|
| SRC | rdi/rsi | whole function | READ-ONLY pointer arg; never written by the macro. This is bail-safety, not a scratch value — excluded from "5 live values" framing below. |
| ACC | rax | whole loop, every digit iter | accumulator: `lea+add+add` every digit (`:68-70`) |
| PTR | r11 | **every iteration of THREE loops** (`.Lsp`, `.Ldig`, `.Lts`) | memory-address BASE register (`byte ptr [PTR]`, `:47,52,54,60,64`); `inc PTR` almost every iteration |
| CNT | r9d | every digit iter | digit counter, `inc`+`cmp` each iteration (`:72-73`); **read for the LAST time at `:77`**, never touched again |
| SGN | r10b/r10d | **write-once, read-once, both OUTSIDE the digit loop** | set at most once at sign detection (`:56`, only on `-`), tested once after trailing-space scan (`:87`) |
| DIG | r8/r8d | every digit iter | freshly loaded+validated every iteration (`:64-66`); **the byte 45/43 (sign) check does NOT touch DIG at all** |

**Critical observation the brief's "5 simultaneous" framing missed: SGN is not simultaneous with the other
four.** It has exactly two touch points, both structurally outside the hot loop, and — proven from the
code itself, not assumed — **DIG and CNT are both dead at those two touch points**:
- At the SGN-write site (`:56`, inside `.Lminus`, before `.Ldig` even starts): DIG has never been written
  this call (first `movzx DIG32,...` is the next instruction inside `.Ldig`, which unconditionally
  overwrites it before any read). DIG's incoming value is provably dead here.
- At the SGN-read site (`:87`, after `.Ltse` exits): CNT was last read at `:77` (`test CNT32,CNT32; jz
  .Lbail`) and never again. **Both call sites immediately re-clobber CNT/DIG right after the macro
  returns control** — `:104-105` (`mov r8,rax; xor r9d,r9d`) for S, and the fallthrough into
  `.Lother_int`/`.Lother_real` (`:128-129,133-134`, `movq r8,xmm1; movq r9,xmm2`) for O — so nothing
  downstream depends on DIG/CNT's post-macro value either. CNT is dead at `:87` by construction, not by
  assumption.

## 2. THE EXCLUSION SET, CORRECTED

Bail-safety (file header `:24-25`, "all four preserved for the bail path"): **rdi rsi rdx rcx** (SRC self/
other + `out`/`codes` args).
Blob pins (`ARCH-SNOBOL4-RTX.md`§2, `ARCH-ICON-RTX.md`§2, corrected): **rbx r13 r14 r15** — NOT r12.
Frame/stack: **rsp rbp**.
Ladder destination rule (`DISPATCH-R10-R11-ERADICATION.md`, "binding on every rung"): **NOT r8 (ANCHOR),
NOT r9 (GVA)** as a landing spot for evicted r10/r11 values — moot here since r8/r9 already hold DIG/CNT,
their pre-existing role, not a new claim.
Being eradicated: **r10 r11**.

13 of 16 GPRs excluded. Free: **rax r8 r9** (already ACC/DIG/CNT — their existing roles) **+ r12**
(genuinely unclaimed, per §0). That is the corrected inventory: **one spare GPR exists, not zero** — but
one spare GPR for two evicted values (PTR, SGN) is still short by one, so the question is whether either
value can leave the GPR file entirely.

## 3. THE VERDICT, SPLIT — r10 CLEARS, r11 DOES NOT (at zero rsp cost)

### r10 (SGN) → xmm0: **YES — concrete, zero rsp adjustment, demonstrated at instruction level**

xmm0 is free for the full duration of BOTH macro invocations: in the S-invocation (`:103`) nothing has
touched xmm0 yet (the DT_R branch that uses xmm0, `:116`, is a mutually exclusive earlier branch — self is
either DT_I/DT_R/DT_SNUL/DT_S, only one taken); in the O-invocation (`:126`) xmm1/xmm2 are live (holding
the S-result stash from `:119-120`) but xmm0 is untouched until `.Lint_to_real`/`.Lstore_real`, which are
both AFTER the O-scan completes. SysV: xmm0-15 are ALL caller-saved/volatile — zero save/restore burden,
unlike a GPR.

Concrete diff (macro body only, both call sites unchanged):
- Entry zeroing (`:45`, `xor SGN32,SGN32`) → `pxor xmm0, xmm0` — pure register clear, zero GPR touched.
- Write site (`:56`, `mov SGN8, 1`) → `mov DIG32, 1` then `movd xmm0, DIG32` — reuses DIG's register
  (r8/r8d) as a one-shot immediate carrier; safe because DIG32 is unconditionally overwritten by the very
  next executed instruction (`movzx DIG32, byte ptr [PTR]` at loop entry) on every path that reaches here.
- Read site (`:87`, `test SGN8,SGN8`) → `movd CNT32, xmm0` then `test CNT32, CNT32` — reuses CNT's
  register (r9/r9d) as the reload target; safe because CNT is dead at this point (§1) and both call sites
  re-clobber it unconditionally moments later regardless of which branch the macro took.

No rsp touch anywhere in this plan. No rdi/rsi/rdx/rcx touch. No blob-pin touch. `SGN8`/`SGN32` macro
parameters become dead and should be dropped when this lands (2 of 10 params, both call sites simplify
identically since xmm0 needs no per-invocation parameterization). **This is criterion (a), fully met.**

### r11 (PTR) → **NO xmm packing exists; the only GPR option costs a real (if small, uniform) rsp adjustment**

Three avenues examined, all fail the *zero* rsp-adjustment bar of criterion (a):

1. **xmm residency for PTR itself: hard ISA wall, not a design choice.** PTR is a memory-addressing BASE
   register (ModRM/SIB) dereferenced on every iteration of three separate loops (`:47,52,54,60,64`).
   x86-64 forbids xmm registers in a base/index field — full stop. Parking PTR in xmm between touches
   would need a GPR round-trip on literally every iteration of the hottest loop in the routine, and there
   is no register free to serve as that round-trip's temporary: ACC/DIG/CNT (the only 3 non-excluded GPRs,
   §2) are ALL simultaneously live at the exact instant PTR is dereferenced in `.Ldig` (`movzx
   DIG32,[PTR]` writes DIG in the same instruction that reads PTR; ACC and CNT hold state needed moments
   before/after in the same iteration) — none can be borrowed even transiently, unlike SGN's disjoint
   touch points.
2. **Evicting ACC/DIG/CNT to xmm instead, freeing a GPR slot for PTR:** technically conceivable (SSE2
   `paddq`/`pmuludq` could in principle carry the digit accumulation), but this is an algorithmic rewrite
   of the routine's core arithmetic, not a register rename — undemonstrated, untested, materially larger
   surface than the row asks for ("a concrete xmm/GPR assignment... demonstrated on the emitted asm of a
   witness" — I have not built or measured such a rewrite and will not claim it as proven safe).
3. **GPR reassignment PTR→r12:** r12 is unclaimed per §0/§2, so this is the natural candidate — **but r12
   is still plain SysV callee-saved despite not being an architectural pin, and the codebase already has a
   live, shipped instance of exactly this rule being followed: `rtx_match.S:800/883` —
   `push r12 /* r12 is FREE since ZR-RSP___-1 but still SysV callee-saved */` ... `pop r12` before return.
   `rtx_abi.inc:30-31` states the same rule explicitly: *"r12 being free does NOT exempt it from that rule
   [preserve on clobber] when a pinned graph is live above you — it is free, not scratch-by-fiat."*
   Using r12 for PTR therefore requires a `push r12` at entry and a matching `pop r12` at every exit —
   which, note, is NOT the fragile "multi-exit, variable-depth" bookkeeping the brief feared: this file
   funnels EVERY bail check (`:42,74,78,86`, both S and O invocations) through one single, unsuffixed
   `.Lbail:` label (`:152`), and rsp's displacement from a single entry-time push is constant across every
   loop depth — so the fix would be exactly 3 matching pops (2 `ret` sites `:144,151` + the one shared
   bail funnel `:152`), not N per-site unwinds. **This is real and bounded, but it is still an rsp
   adjustment**, so it fails criterion (a)'s literal bar as written, and it carries a second, unverified
   risk: `rtx_match.S:520` shows r12 ALSO carries a live, non-push/pop-guarded meaning in at least one
   other mechanism (`RTX_DCAP_TOP_VA`, seeded by the outer `rt_outer_call` thunk before entry, O-5 ZW-3) —
   whether `rt_coerce_num2_d` can ever be reached while that seed is live (i.e., numeric coercion invoked
   during an active match) is **not verified in this row** and would need checking before r12 is trusted
   here even WITH push/pop.
4. **Stack-slot spill for PTR** (the generic ladder fallback): same rsp-adjustment class as (3), and it is
   the specific thing the file's header names as the reason it chose xmm in the first place ("SCRATCH IS
   xmm, NOT THE STACK, precisely so that bail is a bare jmp valid at any point holds") — changing that is
   a soundness-invariant decision for Lon/HQ, not a register-packing exercise this row can settle
   unilaterally.

**Answer for PTR/r11 is (b): explicit NO to a zero-rsp-adjustment packing.** The specific value that
cannot be packed is PTR, for the specific reason that it is a hot-loop address-computation register with
zero free GPR to round-trip through and zero legal xmm addressing mode — and the best available fallback
(r12 with push/pop) is bounded and uniform (unlike the brief's fear) but still a real, non-zero rsp cost
plus one unverified cross-mechanism risk, so it is reported here as a costed option for HQ/Lon to rule on,
not blessed as a row-closing yes.

## 4. WHAT THIS UNBLOCKS

Per the row's own rule ("Only a YES earns an implementation rung"): **r10's half (SGN→xmm0) is clear to
implement** as its own follow-up rung — zero rsp cost, zero bail-safety/blob-pin impact, fully specified
in §3. `.github/ARCH-SNOBOL4-RTX.md`§2 must be amended in that same commit per
`DISPATCH-R10-R11-ERADICATION.md`'s per-rung DONE-WHEN #3, and `rtx_icnnum.S:29`'s stale "Blob pins rbx
r12-r15" header comment should be corrected in the same pass (§0). **r11's half (PTR) stays frozen** —
no implementation rung earned — pending an explicit Lon/HQ ruling on whether the bounded r12 push/pop
cost (§3.3, plus its unverified dcap-seed interaction) is acceptable, or whether the "bare jmp, scratch is
xmm not stack" invariant itself should be relaxed for this one register. This is the same disposition the
brief anticipated ("Only a YES earns an implementation rung") — it just now applies per-register rather
than to the row as a whole, which the brief's "5 simultaneous" framing did not distinguish.

## 5. SCOPE FENCE HONORED

Zero bytes of `rtx_icnnum.S` or `rtx_icnsub.S` changed by this FINDING. `rtx_icnsub.S`'s 39 sites across 5
arms are untouched and unanalyzed here — a separate design pass, not covered by this row's DONE-WHEN grep
target (`SCAN_SIMPLE_INT` is icnnum-only).
