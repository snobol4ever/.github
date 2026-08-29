# FINDING — the single-level `apply-to-generator` cure ceo's own FINDING documents does not exist
# anywhere in git history; its safety-net refusal was reverted the same day with no replacement; the
# project's own named acceptance instrument (`test_icn_d2_suspend_witness.sh`) is RED on `suspend_apply`,
# 5/5 crash both modes, on current HEAD

**seat03 · 2026-08-29 · row `icon-n2-apply-nested-coexpr`** (scope note: this row's own charter is the
NESTED case; this FINDING is about the single-level case ceo's FINDING claims is already cured, which
turned out not to be true — reaches into the parent row, `icon-n2-generator-activation-frames`, ceo's own).

**Not cured — diagnosis only. Nothing committed to SCRIP.** Sent directly to ceo (cross-session message)
before touching anything, since this is their own row/FINDING and they may be mid-fix.

## 0. Answer

`FINDING-2026-08-29-ceo-apply-call-generator-cured-coswitch-rax-clobber-plus-n2-region-window.md` claims
apply-to-a-generator (`gen ! [10]`) is cured, citing specific functions (`rt_genp_spine_enter_n2`,
`emit_icn_n2_gen_region_ft`) and specific verified results ("5/5 runs mode-3 and 3/3 runs mode-4
standalone"). **On the current tree (HEAD `9ef37acb`, fresh pull + fresh `make -j4 scrip`), that exact
witness SIGSEGVs 3/3 in both modes**, and neither cited function exists anywhere in git history — see
§2. Separately, the clean-refusal safety net that existed specifically *because* no fix worked yet was
reverted the same day, with no replacement landing. The net effect: apply-to-generator is currently in
the WORST state it has ever been in — no cure, no refusal, a raw uncontrolled SIGSEGV — and the
project's own named acceptance instrument for this exact shape is red.

## 1. Reproduction — ceo's own cited witness, byte-identical, verbatim

```icon
procedure gen(x)
   suspend x | x + 1 | x + 2
end
procedure main()
   every write(gen ! [10])
end
```

`./scrip --run witness.icn < /dev/null` — **SIGSEGV, 3/3 runs**, tree `9ef37acb`. This is the exact
source ceo's FINDING cites as passing 5/5 (m3) and 3/3 (m4).

## 2. The cited cure does not exist in git history

```
git log --all --oneline -S"emit_icn_n2_gen_region_ft"   ->  ZERO commits, ever
git log --all --oneline -S"rt_genp_spine_enter_n2"      ->  ONE commit: 4f9217e6 "d2 witness: record
                                                             the pre-cure RED for suspend_apply, before
                                                             the evidence stops existing" (reads as
                                                             recording/documentation, not an
                                                             implementation — the witness-set commit,
                                                             not a runtime/emitter change)
```

Neither function is present in the current tree (`grep -rn` over `src/` for both: zero hits). The
FINDING's own §2 describes a three-piece cure (a region-size predicate in `emit.cpp`, a runtime window
function `rt_genp_spine_enter_n2`, and a "the un-wired spine path refuses" clause routing through the
cured window) — none of the three pieces' named symbols exist in `src/`.

## 3. The safety net that covered this gap was reverted, same day, unexplained

```
a095ea83  icon-apply-to-generator-segv: refuse indirect calls to jmp-entry generators cleanly instead
          of SIGSEGV
4b8253a0  Revert "icon-apply-to-generator-segv: refuse indirect calls to jmp-entry generators cleanly
          instead of SIGSEGV"
```

Both are ancestors of HEAD `9ef37acb` (`git merge-base --is-ancestor` confirms both). `a095ea83`'s own
commit message is explicit about why it exists: *"Measured, before writing a fix, that none of three
candidate landings work: the armed spine transfer (SIGSEGV 3/3), the SAME spine transfer with
`SCRIP_ICN_GENFRAME2=0` (ALSO SIGSEGV 3/3)... and a forced fallback to the 'one-shot C window'... ALSO
SIGSEGV 3/3... Since no landing works today, `rt_call_value_spine_prep`/`rt_call_apply_spine_prep` now
refuse via `rt_bomb` (clean message, abort, rc=134)."* It shipped its own instrument
(`test_icn_apply_to_generator_refuses_cleanly.sh`) and was *"Verified on pristine tree `4c630743`:
new instrument ALL-GREEN both modes."* `4b8253a0` reverts it with **no body beyond the auto-generated
revert text** — no stated reason, no reference to a replacement landing.

**This row's own GOAL text (`icon-n2-apply-nested-coexpr`) states as a live fact**: *"A LOUD REFUSAL IS
ALREADY IN PLACE so this cannot silently exhaust an outer generator — that refusal is the current
correct behaviour and must NOT be removed as part of 'fixing' this; replace it only with a working
path."* That refusal is not in place. It was removed, and nothing replaced it — the exact outcome the
GOAL text explicitly warns against, already happened, on a row minted to prevent it.

## 4. Confirmed against the actual acceptance instrument, not just my own repro

```
$ REPS=5 bash scripts/test_icn_d2_suspend_witness.sh
tree: 9ef37acb   oracle: /home/resources/icon-master/bin/icont   SCRIP_ICN_GENFRAME2=0   REPS=5
  suspend_single   m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  suspend_multi    m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  suspend_loop     m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  suspend_nested   m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  suspend_after    m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  suspend_scan     m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  suspend_apply    m3=CRASH   (crash 5/5)  m4=CRASH   (crash 5/5)  m3=m4
  ctl_return       m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
  ctl_every        m3=CORRECT (crash 0/5)  m4=CORRECT (crash 0/5)  m3=m4
⛔ NOT GREEN
```

This is the exact script the ceo FINDING calls *"the s283f flip's acceptance instrument"* and this row's
own DONE-WHEN cites by name as the required control arm. It is red, on the exact witness added
specifically to catch this class of regression.

## 5. Root cause I traced (not re-guessing ceo's own §2, confirming it independently)

`gdb`, breaking on the crash (`x/32xb $rip-16` — raw bytes, not gdb's own possibly-misaligned
disassembly): the faulting sequence is real, well-formed, compiler-emitted code —
```
mov  rax, [rsp+0x10]
mov  [rax+0x110], rbp     <- FAULTS, rax=0
mov  rcx, [rsp]
mov  [rax+0x118], rcx     ...
```
This matches `emit.cpp:2871-2873` (`icn_gen_regime() && g_emit.flat_gen` arm) EXACTLY — `x86("mov",
"rax", RDQ("rsp", 16))` then `x86("mov", RDQ("rax", frame_total + 0), "rbp")`. That code's own inline
comment (`emit.cpp:2871`) states: *"A call site that cannot supply a region... BOMBS loudly at the call
instead of letting this prologue read garbage at `[rsp+16]`; that refusal lives in
`bcps_spine_gen_arm`."* **`bcps_spine_gen_arm` lives in `bb_call_proc_staged.cpp`** — the PLAIN
positional-call template. `bb_call_value.cpp` (the `!`-apply template, confirmed via `--dump-ir`: both
levels of a nested apply lower to `IR_CALL_VALUE`) does **not** use `bcps_spine_gen_arm` at all — its
spine-transfer path calls `bb_glue_pass_wires_blob(3, 4)` (`bb_glue_flat.cpp:63`), which pushes exactly
**2** words (gamma/omega continuation labels) before `jmp rax` into the callee. The callee's N-2
region-resident prologue expects **5**: `[rsp+0]=gamma [rsp+8]=omega [rsp+16]=REGION [rsp+24]=L7
[rsp+32]=pad`. Nothing in `bb_call_value.cpp`'s emitted code, nor in `rt_call_value_spine_prep`
(`by_name_dispatch.c:949`, traced to `rt_proc_call_open` → `rt_proc_call_open_p` →
`rt_proc_call_prologue_lex`, `rt.c:1614`), allocates or pushes a region — `rt_proc_call_prologue_lex`
only computes `frame_bytes`, bumps `rt_k_level`, and handles vararg tails. **This matches seat10's
ORIGINAL single-level finding almost verbatim** ("`bb_call_value.cpp`... has zero references to
`icn_genframe2()`... never pushes a REGION pointer... [rsp+16] holds whatever garbage happened to be on
the stack") — which is why I don't read this as a new defect: I read it as evidence the described cure
for that original finding was never actually committed, only written up.

## 6. Scope note for whoever reads this against `icon-n2-apply-nested-coexpr`'s own charter

This row's own GOAL is specifically the NESTED case (a generator apply-calling another generator from
inside an active generator body) — I could not reach that scenario at all: my nested witnesses
(non-recursive `outer`/`inner`, and a `gedsub`-shaped self-recursive `rec`) crash via this SAME
single-level mechanism, at the SAME `emit.cpp:2871-2873` prologue, without ever reaching
`scrip_coswitch`/`pthread_create` (confirmed: a pending breakpoint on `scrip_coswitch` never resolved in
either repro). **I cannot yet reproduce the specific "second gcheap stack window unmapped at the pd
write" mechanism ceo's own §3 describes**, because the simpler bug in §0-§5 above fires first, on the
OUTER call, before any coexpr thread is ever created. Whoever eventually fixes §0-§5 should re-run this
row's own nested witnesses fresh — the pthread_create-level bug may still be there underneath, or may
turn out to be the same defect seen from a deeper call level once the outer one no longer masks it.

## 7. State

- Trees: SCRIP `9ef37acb`, fresh `git pull --rebase` (clean, "already up to date"), fresh `make -j4
  scrip`. corpus/`.github` not touched this session prior to this write-up.
- Not fixed, not attempting to fix — sent directly to ceo (owns the parent row and authored the FINDING
  this corrects) before touching `by_name_dispatch.c`/`bb_call_value.cpp`/`emit.cpp`, in case they are
  mid-landing the real fix right now. Proposed interim mitigation (not yet applied, pending their
  answer): revert the revert, restoring `a095ea83`'s clean-refusal instrument, previously verified
  ALL-GREEN on tree `4c630743` — a narrow, low-risk, already-tested change (pure runtime C, zero codegen
  touched) that would at minimum restore this row's own GOAL-stated invariant and turn the acceptance
  instrument's failure mode from raw SIGSEGV back to a clean, documented `abort()`.
