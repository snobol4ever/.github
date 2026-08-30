# FINDING 2026-08-30 seat07 — `vsr3.icn`'s `id`-corruption crash is an 8-byte restore-RSP miscount in the generator-callee prologue, NOT a memory clobber. Likely the SAME root defect as root cause 1 (genqueen's depth-counter garbage).

## CONTEXT

Row `icon-n2-recursive-generator-per-activation-storage`. Current `## NEXT` (seat03, 2026-08-30) redirected
investigation away from the call-site region-LEA arithmetic (closed, three sessions confirmed it's real but
irrelevant to `id`'s corruption) toward `FN__walk`'s own prologue/suspend-resume machinery, naming the
`rbp=H+288` lead as the concrete next thing to chase. Recreated `vsr3.icn` (seat08's 15-line repro, embedded
verbatim in `FINDING-2026-08-29-seat08-geddump-error3-not-host-region-overlap-real-defect-in-call-site-plus16-constant.md`
— the file itself is not durably persisted anywhere in the repo/corpus, only inside that FINDING's markdown;
recommend someone add it to `corpus/` so it stops needing reconstruction every pass), compiled+linked to a
real mode-4 binary (`gcc -no-pie vsr3.s -lscrip_rt ... -o vsr3.bin`, same recipe as seat08/seat14), matched
the documented baseline exactly (unarmed rc=134 GENHOST bomb; armed `SCRIP_ICN_N2_SELFREC=1` rc=1 Error 3).

## THE `rbp=H+288` LEAD ITSELF IS EXONERATED — RE-DERIVED, NOT ASSUMED

Disassembled `FN__walk`'s prologue directly (`objdump -d -M intel`): `lea rbp,[rax+0x120]` (0x120=288),
confirming `align16(fb_walk)=288` holds on THIS witness too (previously only checked on a different one, per
this row's own standing "don't carry a number across witnesses" rule). `[rax+0x120]`=`[H+288]` is exactly
`[H+0]` once `rbp` is repointed, and it correctly holds the caller's saved `rbp` (`mov [rax+0x120],rbp` runs
*before* `rbp` is overwritten). This part of the prologue is legitimate frame-chain bookkeeping, not a bug.

## THE ACTUAL MECHANISM, DYNAMICALLY PROVEN, NOT INFERRED

**Step 1 — a hardware watchpoint on `id`'s own memory address never fires.** Broke at `n21_assign_α`
(`id := table()`'s write, confirmed at `[rsp+1440]`/`[rsp+1448]` matching this row's own prior citation),
captured the concrete address, set `watch *(long*)$id_addr`, continued to program exit. **The watchpoint
never triggers — the program runs to the Error-3 crash without that memory location ever being written
again.** `id`'s own storage is never clobbered. Everything downstream in this row's history that framed this
as "what corrupts `id`" was investigating the wrong verb.

**Step 2 — the crash is a stale-RSP read, not stale memory.** Broke at all four `lea rdx,[rsp+1440]` sites
(`n22`/`n27`/`n32`/`n56_var_ref_α` — the three `id["x"]:=N` RHS reads plus the actual `id[r.data]` read
inside the `every` loop). `n22`/`n27`/`n32` all fire at identical `rsp` (consistent, straight-line main
body, before any `walk` call). `n56` — the crash site — fires ONCE, at `rsp` **8 bytes higher** than the
other three. `*id_addr` read there is `0x7fff8f3fe040:0` — a stray stack address, not a table descriptor:
exactly what "Erroneous array or table reference" looks like when the read address is simply wrong.

**Step 3 — the 8 bytes traced to source.** `FN__walk`'s prologue (`emit.cpp:2887-2896`, the
`icn_gen_regime() && g_emit.flat_gen` arm) computes a "caller's pre-push rsp" checkpoint via
`lea rcx,[rsp+40]` → stored at `[H+312]`. The comment at `emit.cpp:2887` documents the INTENDED contract
explicitly: *"Entry stack (bcps_spine_gen_arm, armed): `[rsp+0]=gamma [rsp+8]=omega [rsp+16]=REGION
[rsp+24]=L7 [rsp+32]=pad`, caller pre-pad rsp0=`[rsp+40]`"* — five words, 40 bytes, by design.

`walk_γ` (the succeed/yield port, `walk_γ:` in the .s) jumps back to the call site's success continuation
(`.Lproc_gen_α_117_3` for this witness) **without ever touching `rsp` itself** — so whatever `rsp` was
throughout `walk`'s own execution is what the caller sees. `.Lproc_gen_α_117_3` then does
`mov rsp, qword ptr [rdx+24]` = `[H+312]` = the prologue's `entry_rsp+40` value.

**Directly measured the call site's actual push count** (break at `n51_proc_gen_α`'s first instruction and
at `FN__walk`'s first instruction, diff `$rsp`): **exactly 32 bytes (4 words), not 40.** Confirmed three
independent ways: static instruction count (4 `push`es: name/L7-slot value, region, the ω/γ continuation
pair), the dynamic rsp delta measurement, and the crash-site address delta itself all agree on exactly 8
bytes / one word.

**8 = 40 − 32.** The prologue's restore checkpoint overshoots the true caller rsp by exactly one word. Every
RSP-relative reference in `main` after the first successful suspend/resume — not just `id` — is silently
reading 8 bytes off from where it should. `id` is simply the first one whose garbage fails Icon's runtime
type-check loudly enough to surface as Error 3; a numeric or string local landing on plausible-looking
garbage might not error at all.

## PROBABLE UNIFICATION WITH ROOT CAUSE 1 (not proven, but the shapes match too well to ignore)

`emit.cpp:2893-2895` (gated on `icn_genframe2_selfrec() && icn_gen_is_selfrec(...)`) reads that SAME
"pad"/5th-word slot AGAIN, separately, banking it as the self-recursion depth into `[H+40]`. seat12's
already-documented root cause 1 (`FINDING-2026-08-29-seat12-n2-selfrec-depth-counter-reads-garbage...md`) is
"the self-recursion depth push is one 8-byte slot short of the shared callee prologue's expected layout,
causing the depth counter to read garbage." **That is the exact same missing 5th word, read from a
different angle.** If the call site is short one push, BOTH the depth-bank (root cause 1, garbage depth) and
the restore-rsp checkpoint (this FINDING, garbage `id`) are corrupted by the identical root defect — two
previously-separate-looking symptoms may be one bug, not two.

## WHAT I DID NOT PIN DOWN — genuinely open, not solved by guessing

`bb_call_proc_staged.cpp:725-738` (`bcps_spine_gen_arm`'s α/open path) has a conditional that SHOULD push a
real 5th word for exactly this shape: `icn_gen_regime() && icn_genframe2_selfrec() && icn_gen_is_selfrec("walk")`
is true for `walk`, and since `main` (the caller) is not itself `flat_gen`, the code should take the
"first (non-recursive) call... seed depth 0" branch (`x86_lea_id("rax",0) + push rax`) — a genuine 5th push.
**I could not cleanly confirm from static reading alone whether this branch is the source of the 4th push I
already found (mislabeled), or whether it fires at all and its push is simply absent from the compiled
output.** `x86_lea_id(dst, n)` loads the ADDRESS of a per-call-site auto-numbered local label (`x86_asm.h:596`),
not an integer value directly — and label-index 0 for this call site is ALSO where `x86_ro_seal_str(0, ...)`
(`bb_call_proc_staged.cpp:877`) defines the callee's name string ("walk"), used by the `rt_ab_undef_fn_stub`/
NRETURN-by-name error path. Whether these are the same push wearing two purposes, or the depth-seed branch is
silently not firing at all for this call shape, needs a cheap, decisive check (a getenv-gated stderr print at
line ~736, or a `gdb` break inside `bcps_spine_gen_arm`'s emission itself is not applicable — this needs a
COMPILE-TIME trace, e.g. a temporary `fprintf(stderr, ...)` in the template guarded by an existing debug env
var, or bisecting by hand-editing the conditional to always/never take that branch and diffing the `.s`)
before touching anything. **Did not attempt this compile-time trace or any fix — this row's own shared-code
discipline (full-rigor treatment before landing, this being `bcps_spine_gen_arm`'s general armed path, not a
witness-local shape) applies squarely, and I do not yet know which side (add a push at the call site, or
change the callee's `+40`/`+32` constant, or something in between) is the correct fix.**

## CROSS-WITNESS CONFIRMATION (cheap, static — not a full dynamic re-trace)

Compiled `geddump.icn` armed (`SCRIP_ICN_N2_SELFREC=1 --compile`) and diffed `FN__gedwalk`'s prologue against
`FN__walk`'s: **byte-for-byte identical shape**, including the same `lea rcx,[rsp+40]` → `[rax+312]`. This is
the shared `emit.cpp` template, not a `vsr3.icn`-specific artifact — the mechanism generalizes to geddump's
own Error-3, exactly as this row's `## NEXT` already speculated ("almost certainly shares this mechanism...
not independently re-verified"). Did not run a full gdb trace on `geddump.icn`/`geddump.dat` this pass (would
duplicate the `vsr3.icn` trace above with more setup cost for the same answer); the static prologue match is
sufficient to redirect confidence, not to close the loop.

## NEXT ACTOR

1. Resolve the open question above FIRST: does `bb_call_proc_staged.cpp`'s depth-seed/pad push (lines
   725-738) actually fire for a `main → walk(root)`-shaped call (self-recursive callee, non-self-recursive
   caller)? A getenv-gated stderr trace at that branch, or a scoped hand-edit-and-diff experiment, settles it
   in minutes — don't guess further from static reading, this row has already paid for that trap once
   (seat08's original `+16` analysis, later found to be on dead code for its own witness).
2. Once the missing/present-but-wrong-role push is located precisely: the fix is either (a) make the call
   site push a genuine 5th word unconditionally, or (b) make the callee's restore-checkpoint arithmetic match
   what the call site actually pushes — NOT both, and not guessed; whichever is chosen needs the standing
   full-rigor treatment (gdb end-to-end on the FIXED binary, `vsr3.icn` AND `geddump.icn`/`.dat`, full
   SNOBOL4/Icon/Raku/Prolog/Snocone/Rebus regression, since `bcps_spine_gen_arm`/`emit.cpp`'s `icn_gen_regime()`
   arm is shared by every Icon generator call, self-recursive or not).
3. If confirmed as the same defect as root cause 1 (seat12's depth-counter garbage), fixing this may close
   BOTH `genqueen`'s SIGSEGV and `vsr3.icn`/`geddump.icn`'s Error-3 in one landing — worth checking `genqueen`
   against whatever fix lands here rather than treating them as two separate follow-up items.
4. Mutual recursion (c) and the general design ruling: unchanged, not touched, not this FINDING's concern.

No source touched. No fix attempted.
