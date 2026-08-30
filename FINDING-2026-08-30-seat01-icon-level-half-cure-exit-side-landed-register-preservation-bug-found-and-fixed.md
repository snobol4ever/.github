# FINDING — icon &level: exit-side HALF-CURE landed (SCRIP `41730a7f`), per hq_P's own three
# conditions for this row. Also: a first attempt at this exact, small, DSL-only change caused a real
# regression (Icon rung board FAIL 8→32) that a naive board-count check would have looked "close
# enough" to miss — caught only by exact-list diffing, not counts. Root cause confirmed via
# asm-diff + direct trace: a register-preservation bug, not a logic bug in the level arithmetic
# itself. Fixed, re-verified with an exact-list diff against a clean baseline, landed.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`**

## 0. Context — what hq_P authorized and why this exists

Prior FINDING (`icon-level-exact-fix-sites-located-implementation-ready`) located both real emission
sites for `&level` tracking precisely but landed neither, given the entry side's raw-byte BINARY arm.
hq_P's reply (`level-sites-located-land-it-carefully`) set three conditions, the middle one explicitly
inviting this: *"the exit side you found is already Icon-scoped and is the cheaper, safer half —
landing it alone first is legitimate and I would prefer it, so long as the commit says plainly that it
is half the cure and the board is expected to move by zero."*

## 1. First attempt: a real regression, not a false alarm

Implemented the exit-side decrement (mirroring `bb_define_activate`'s `leave_env` pair) in
`xa_flat_zframe_epilogue_γ_str()`/`_ω_str()`. Built, ran the full battery per this project's own
standard (not a spot check): `make pristine`, Icon smoke, Icon rung suite board (all 3 modes), SNOBOL4
control arm.

**Result: Icon smoke dropped 14/14 → 12/14 (both modes), rung board FAIL 8 → 32.** Not "moves by zero"
— a real, measured regression. Reverted immediately (`git checkout`), rebuilt, confirmed smoke back to
14/14. Nothing broken was pushed.

## 2. Diagnosis — ASM-DIFF-FIRST, not a second guess

Isolated to the smallest failing witness already in this project's own smoke suite:
`procedure fact(n); if n<=1 then return 1; else return n*fact(n-1); end` — expects `120`, silently
printed nothing (`rc=0`, no crash) with the broken change.

1. **Confirmed the insertion was clean**: diffed the emitted `.s` for `fact.icn` between the clean and
   broken builds. The ONLY difference was my own 9 intended instructions — nothing else in the file
   moved, no label/offset corruption. This ruled out an emitter side-effect and narrowed the search to
   the 9 instructions' own runtime semantics.
2. **Read `bb_glue_wire_γ()`'s actual definition** rather than trusting its neighboring comment: it is
   `x86_jmp_mem("rsp", 0)` — a bare `jmp qword ptr [rsp+0]`. Doesn't explain the bug by itself.
3. **Read the actual call site** in `fact.s`: the recursive call is `call fact_dcα`, landing back at a
   site whose very next instruction is `cmp al, 104; je fact_ω` — a live check of `AL` for the `DT_FAIL`
   sentinel. `fact_dcα`'s own success-landing trampoline does a bare `jmp r12` with **no fresh success
   tag written** — whatever is in `AL` at the jump-back point is exactly what the caller reads.
4. **Root cause, confirmed not guessed**: my decrement sequence's own scratch usage ends with
   `rax = &kw_fnclevel` (a GOT-relative pointer, essentially arbitrary low byte) — clobbering the
   result's own success/fail tag that the marshal step (`mov rdi,rax; mov rsi,rdx`, which runs BEFORE
   my block) had already captured into `rdi:rsi` but left `rax` itself unprotected. Every call site
   whose landing reads `AL` (not just `rdi:rsi`) got a corrupted verdict.

## 3. Fix, and why it's confirmed not just plausible

`push rax` immediately after the marshal, `pop rax` immediately before the unwind (`add rsp, kt`) —
brackets the entire decrement block, which only needs `rax`/`rcx` as internal scratch and never needs
the ORIGINAL `rax` value for its own purposes. Applied to both γ and ω arms (ω doesn't marshal a result
first, so the push goes at the very top of its own block instead).

**Verified with the SAME rigor that caught the bug — an exact-list diff, not a count comparison**:
`bash test_icon_rung_suite.sh --mode interp | grep '^FAIL ' > with_fix.txt`, then `git stash` (clean
baseline), rebuild, same command → `clean.txt`, then `git stash pop`. **`diff clean.txt with_fix.txt` is
EMPTY** — byte-identical FAIL populations. (An earlier count-only check read `FAIL=8` vs `FAIL=10` and
looked like a small regression; that was comparing against a STALE remembered number, not a fresh
baseline — the list diff is what actually settles it, and it settles it at zero.) `fact(5)` now
correctly prints `120` again. The still-incomplete witness (`rung36_jcon_level`'s own minimal repro)
reads `1 1 0` — not yet correct (expected: needs the entry-side increment too), but not a new symptom
either — matches the documented half-cure exactly.

Full battery: `make pristine`; Icon smoke 14/14 both modes; Icon rung board FAIL list byte-identical to
a fresh clean rebuild; SNOBOL4 corpus control arm 1519/1519 both modes FAIL=0 MISSING=0 GATE OK.

## 4. The generalizable lesson, worth keeping past this one bug

**A clean, DSL-built (non-raw-byte) instruction sequence can still silently break unrelated call sites
if it doesn't preserve a register the CALLER depends on, and nothing near the insertion point says so.**
This is a different hazard than hq_P's own raw-byte caution (BOTH-MEDIUM MANDATORY, TEXT/BINARY
divergence) — here TEXT and BINARY agreed perfectly (confirmed by the asm-diff), and the bug was still
real. The four-port Byrd-box convention signals success/failure through a REGISTER VALUE at the jump
target, not always through the jump target's address alone — `bb_glue_wire_γ()`'s own comment
("NON-CONSUMING jmp") describes what happens to the STACK, not what the CALLER reads from registers, and
nothing forced noticing that distinction before landing. The check that caught it — comparing the
EXACT FAIL list against a freshly-built baseline, not a remembered count — is the same discipline RULES.md
already names for other instrument classes; this is that lesson's instance in a live register-clobber,
not a queue state or a gate script.

## 5. Not done

Entry-side increment (`emit.cpp`'s `flat_lcl_proc` prologue, raw-byte BINARY arm) — unchanged from the
prior FINDING, still needs `as`-verified bytes or a new `x86_asm.h` encoder per hq_P's condition 1.
`&level` itself is still wrong end-to-end until that lands.

## 6. State

SCRIP `41730a7f`. `git status --short` clean. Mailing hq_P.
