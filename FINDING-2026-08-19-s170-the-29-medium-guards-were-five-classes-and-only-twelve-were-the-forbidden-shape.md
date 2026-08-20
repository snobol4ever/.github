# FINDING s170 — THE 29 BOTH-MEDIUM GUARDS WERE FIVE CLASSES, ONLY TWELVE WERE THE FORBIDDEN SHAPE, AND THE MEDIUM BRANCH HAD BEEN SPLITTING THE PORT SEAM

**Seat:** local `/home/claude1` (seat1), Claude Opus 5. **Picked up:** postoffice QUEUE.tsv row 13
`medium-retire`. **SCRIP** `bcd3984e` + `256103fc` · **.github** this commit.
Census prerequisite: `FINDING-2026-08-19-s169-eight-audit-gates-...` §5/§7.

## 1. A RATCHET COUNTED ONE NUMBER; THE NUMBER WAS FIVE DIFFERENT PROBLEMS

RULES.md carried `29` as a single known-red debt, and s169 made it computed. Retiring it exposed that
the 29 were never one thing. Measured, per site:

| class | n | what it actually was |
|---|---|---|
| **dead by construction** | 4 | `bb_key_gen`'s `MEDIUM_MACRO_DEF` arm; `bb_call_bool`'s two arms sitting 9 lines **below an unconditional return** |
| **tautology** | 2 | `bb_call_proc_staged`'s `if (MEDIUM_BINARY \|\| MEDIUM_TEXT)` |
| **redundant wrapper** | 2 | `bb_gather`/`bb_mapgrep` wrapping `x86("directive",…)` in `IF(MEDIUM_TEXT,…)` |
| **THE FORBIDDEN SHAPE** | 12 | `bb_glue_flat` 8 + `bb_call_write_slot` 4 — one instruction written twice |
| **not an output gate at all** | 5 | `bb_define` C-side live-image state (3) + its emission twin (1) + diagnostics (1 file, 3 sites) |

**Only 12 of 29 were the violation the FACT RULE names.** A single number had been standing in for
dead code, tautologies, redundancy, the real defect, and a class the rule does not even cover.

## 2. THE KEYSTONE FACT NOBODY HAD WRITTEN DOWN: `BB_MEDIUM_MACRO_DEF` IS ASSIGNED NOWHERE

`grep -rn 'BB_MEDIUM_MACRO_DEF' src/` returns exactly two hits — the enumerator's own declaration and
the `MEDIUM_MACRO_DEF` macro. **Nothing ever assigns it.** `g_medium` takes `BB_MEDIUM_BINARY` (emit.cpp
:23/:198) or `BB_MEDIUM_TEXT` (:207, driver :1236/:1409) and nothing else, which is the expected
residue of modes 1 and 2 being DELETED.

Two consequences did most of this row's work:

1. Every `MEDIUM_MACRO_DEF` guard is **unreachable**, so R1 ("no `MEDIUM_MACRO_DEF` arm") is satisfied
   by deletion, never by conversion.
2. **`MEDIUM_TEXT` and `MEDIUM_BINARY` are exact complements.** That is what makes
   `if (MEDIUM_BINARY || MEDIUM_TEXT)` a *provable* tautology rather than a plausible one — and it is
   why 8 of the 29 fell with no argument, no encoder, and no risk.

This belongs in RULES.md beside the rule: a seat converting these needs to know the predicate is
two-valued before it can collapse anything safely.

## 3. THE ENCODERS WERE ALREADY MEDIUM-INVISIBLE; THE TEMPLATES WERE SPELLING AROUND THEM

Not one of the 12 forbidden-shape sites needed a new instruction. Every one collapsed onto machinery
that **already switched internally**, which is the whole point of R2 and exactly what had been
forgotten at the call sites:

- `x86("directive", …)` returns `std::string()` in BINARY (`x86_asm.h:1753`). `bb_gather`/`bb_mapgrep`
  wrapped it in `IF(MEDIUM_TEXT,…)` anyway — medium-complete, guarded a second time.
- `x86("mov", reg, FRQ(off))` **dispatches straight to `x86_frame_load64`** (`x86_asm.h:1885`).
  `bb_call_write_slot`'s two arms were emitting the same instruction through two spellings of one
  function.
- `bb_glue_flat`'s two `_chain` arms were **character-for-character the same expression** under
  `MEDIUM_TEXT` and under `MEDIUM_BINARY`.

⛔ **One trap worth naming.** The `!_chain` pair unified on `x86("call_bare", sym, ptr)`, **not** the
more obvious `x86("call", sym, ptr)`. `x86("call", sym, ptr)` routes through `x86_rtcc_call`, and
`g_rtcc_on` **defaults ON** — so the obvious spelling would have wrapped an RTCC veneer around a call
that had none, moving bytes in **both** media while looking like a pure cleanup. `call_bare` is
`x86_call_ro` verbatim, which is what both arms already were.

## 4. THE MEDIUM BRANCH WAS NOT ONLY DUPLICATING INSTRUCTIONS — IT WAS DESYNCHRONISING THE PORT SEAM

This is the part with teeth, and it is why the class is worth more than its line count.

`x86_deflabel(port)` is not a label printer. It carries `x86_port_hook(X86H_DEF, port)` +
`x86_zdp_probe_at(port)` + `x86_zdp_rbp_at(port)` — Lon's every-port probe seam (s136), whose stated
design property is that hooking there "reaches EVERY α and EVERY β of EVERY box in BOTH media with
ZERO template edits". `x86_asm.h` says outright that the string forms `x86("def","α")` / `x86("jmp","ω")`
are **RETIRED and abort at emit time**.

`bb_call_write_slot`'s TEXT arm hand-spelled its ports as raw `x86("label", _.lbl_β)` — **twice in a
row**, a duplicate definition `as` would reject. So that box's TEXT medium sat **outside the port-hook
seam entirely**: canary, ZDP probe and ZLS2 flavor reached it in BINARY and silently did not in TEXT.
A medium-branched template does not just risk two instruction streams; it risks **two different
instrumentation coverages**, and the instrument that goes missing is the one you would use to find the
resulting bug.

**Censused, and the good news is that it is bounded.** 21 raw `x86("label",…)` sites across 17 template
files, but **18 are `LS(n)` box-local scratch labels — legitimate**. Exactly **3 were ports**: the 2 in
`bb_call_write_slot` (retired here; TEXT now enters the seam) and 1 in `bcps_txt_gen_arm`, which lives
inside the frozen dead arm of §5. **No live instance of the class remains on this tree.**

## 5. WHAT DID NOT RETIRE, AND WHY EACH ONE IS A RULED FLOOR RATHER THAN SKIPPED DEBT

**29 → 3.** Every residual has a named owner; none was left because it was hard.

**(a) `bb_call_proc_staged`, 2 sites — RETIRED (HQ green-light on Lon's delegated desk; rung 3, own commit).** `bcps_bin_gen_arm` /
`bcps_txt_gen_arm` are the forbidden shape at *function* granularity **and have already diverged** —
the TEXT arm carries `rtcc_wb`/`rtcc_rl` + `call_bare`, the BINARY arm carries neither. Exactly the
drift the FACT RULE's WHY predicts. They are also **unreachable at every runnable configuration**
(`x86_zc_frame() != ZC_FRAME_RSP`; `ZC_FRAME_ISLE` needs the retired `frame-r12` selector,
`ZC_FRAME_DEAD5` `#error`s). Deleting them is part of the 17-arm `!= ZC_FRAME_RSP` question RULES
reserves to Lon. HQ first froze them on exactly that ground — *dead + forbidden does not un-reserve it* —
then green-lit **these two only**, as their own attributable commit; the other 15 arms stay reserved. Deleting
them also removed the **third and last** raw-port-label site of §4, so that class now has no instance at all,
live or dead. **29 → 3.**

**(b) `bb_define` 103 / 488, 2 sites — ruled OUT OF SCOPE.** These gate **C-side state, not output**:
allocating and storing the live `g_ab_fn_cells` pointer that exists only for the in-process m3 image
(m4 resolves the same cell as a linker symbol). RULES bans gating *output* on `MEDIUM_*`; these emit
nothing. The honest cure — let the ONE allocator return NULL when there is no live image — requires
hoisting `bb_ab_cell_addr` + `g_ab_fn_cells` out of a template file, which HQ minted as its own row
(`ab-cell-hoist`).

**(c) `bb_define` 427, 1 site — THE FLOOR IS 3, ONE ABOVE HQ's FIRST ARITHMETIC.** Declared, not forced. HQ left this to me
as "emission", and it is; but its own `RTX-FUNC-0 BIND-NEUTRALIZE` comment records why it cannot be
made medium-invisible **in place**: in BINARY the sealed `lea` bakes `ptr=0` as a movabs immediate with
**no forward-patch**, so emitting its three TEXT bind instructions there would write 0 over the address
the C-store already placed — historically measured as *"cell probe good, then jmp 0 at first call"*.
Those instructions exist in TEXT **because the C-store is BINARY's bind**. 427 is therefore the
*emission half* of (b), and retires with `ab-cell-hoist` or not at all.

## 6. WHAT DID RETIRE THAT NEEDED A NEW ENCODER — ONE, AND R7 SAYS SO

`bb_define:222` was the R10 **intentional divergence** (live address vs link-time symbol) sitting in
the wrong place. BINARY jumped the registered proc's address (`x86_jmpfn`), TEXT jumped the label gas
resolves (`x86_jmp_lblptr`). **The divergence was never the violation; its LOCATION was.** R7's rule is
that a missing shape means *add the encoder*, so `x86("jmp_fn", label, fp)` + `x86_jmp_fn_body` now take
**both** coordinates and the encoder picks the one its medium can resolve — precisely the contract the
sealed `[rip + __]` 5-arg forms already hold for RO loads. The template is medium-free; zero movers.

`bb_scan_stmt`'s 3 sites (HQ-affirmed) were the medium choosing nothing but **diagnostic wording**:
TEXT split a decline three ways by which operand was non-literal, BINARY lumped all three under
"pattern". Rewritten to say *what* differs — the LANG-sentinel cure applied to the medium axis — so m3
gains subject/replacement precision it never had. No corpus program reaches those bombs; zero movers.

## 7. PER-MEDIUM BYTE-IDENTITY — MEASURED, CUMULATIVE, AGAINST A PRISTINE BASELINE

| medium | instrument | denominator | movers |
|---|---|---|---|
| TEXT (m4 `.s`) | `util_s_md5_sweep.sh` | 529 programs, **comparable(rc=0)=527** | **0** |
| BINARY (m3 run) | `util_out_sweep.sh` | **572 programs** | **0** |

Both diffs are against the **same pristine `make pristine` baseline**, re-run after each of the two
rungs, so the claim is cumulative rather than per-rung. RULES step-4 regen chain: **"No changes"** on
every corpus — the independent confirmation that codegen did not move. Gate
`test_gate_template_medium_invisible.sh` green at ceiling 5. Icon smoke 14/14. SNOBOL4 6/1 and Prolog
3/5 are **byte-for-byte identical to the baseline binary's** — both reds pre-existing (the SNOBOL4 one
is queue row `smoke-define`), neither caused nor cured here.

## 7b. ⛔ THE BINARY SWEEP PRODUCED A MOVER THAT WAS NOT MINE — AND IT LOOKED LIKE A CURE

Recorded because the next seat to run a byte-identity A/B on this corpus will hit it.

After rung 3, `util_out_sweep` reported **1 changed row**:
`crosscheck/patterns/141_pat_eval_double_fn_arbno.sno` moved from `RUN_RC_139` to a real md5 — which
reads exactly like *"deleting the dead generator arms fixed a segfault."* A tempting thing to publish.

It is a **pre-existing intermittent crash**. Proof, in the order it was taken: re-running the sweep on
the **unmodified baseline binary** reproduces the *identical* one-row flip (same md5, `027851e5…`), and
HEAD against that second baseline capture is **0 movers**. 40 direct runs — 20 per arm — are `rc=0`
with byte-identical output.

**This is a NEW instance of the s148/s150 false-mover class, and `util_out_sweep.sh`'s two existing
cures do not cover it.** Its header documents both: `rc!=0` is labelled `RUN_RC_<rc>` and never hashed
(so a dead run cannot manufacture a hash), and elapsed-time fields are normalised (so parallel load
cannot). An **intermittent crash defeats both at once** — the same program lands in the stable RC label
on one run and a legitimate md5 on the next, so it reads as a mover *in either direction*, and the very
mechanism that makes crashes stable-looking is what disguises it.

**The cheap defence, and it is the one this rung used:** before believing a single mover, re-run the
sweep **on the control arm**. A difference that reproduces against an unmodified binary is the
instrument talking, not the change.

## 8. THE LESSON

s169's lesson was that a gate whose path dies keeps passing. This row's is the sibling: **a ratchet
that counts one number teaches the next seat that it is looking at one problem.** 17 of these 29 sites
were dead, tautological, or redundant — they cost nothing to remove and had been carried for
sessions as if they were the same debt as the 12 real ones. Meanwhile the genuinely dangerous property
of the class — that a medium branch silently splits *instrumentation* coverage, not just instruction
streams — was invisible in the count entirely, because coverage is not a number a grep returns.

Count the classes, not the sites. And when a rule's ratchet is retired, the retiring seat is the one
best placed to say what the number was actually made of.
