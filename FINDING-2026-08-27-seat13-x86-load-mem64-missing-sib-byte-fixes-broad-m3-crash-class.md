# FINDING: `x86_load_mem64`'s BINARY encoding of `mov dst,[base]` omits the mandatory SIB byte whenever `base` is `rsp` or `r12` — a general x86 encoder bug (not Prolog-specific), FIXED and pushed, that resolves a broad class of mode-3 (`--run`) crashes across at least Prolog and SNOBOL4.

**Seat:** seat13 · **Date:** 2026-08-27 · **Task:** `prolog-sendmore-cryptarithm-segv` (postoffice) · **Fix:** SCRIP `12c0ee1c`, corpus `9dcbb35f9`.

## The bug

`src/templates/x86/x86_asm.h`, `x86_load_mem64()` (generic dispatcher for a bare `mov dst,[base]`, no displacement — reached from `x86()`'s operand matcher whenever `a.kind==XK_REG && b.kind==XK_MEMIND`, so it is shared across every frontend, not routed through any language-specific path):

```c
inline std::string x86_load_mem64(const char * dst, const char * basebr) {
    ...
    std::string code; code += (char)rex; code += (char)0x8B; code += (char)((0 << 6) | ((g & 7) << 3) | (m & 7));
    return MEDIUM_BINARY ? x86_Lrec(code) : (x86_rec("mov") + dst + ", qword ptr [" + rb + "]\n");
}
```

It emits REX + opcode `0x8B` + a ModRM byte and stops. x86-64 requires a SIB byte to immediately follow any ModRM with `mod=00, rm=100` — that combination is reserved to mean "SIB follows", regardless of what REX.B extends the base register to. `m & 7 == 4` is exactly `rsp` or `r12` as base, and this function never emits that SIB byte for that case. The result is a **one-byte-short encoding**: the CPU, executing the instruction stream, reads the *next* instruction's own first byte as the missing SIB byte, and everything from there on is misdecoded off-by-one until it eventually reads or jumps through an address built from garbage. It reproducibly manifests as `jmp` through a corrupted computed address, landing inside the (valid, mapped) RX slab at the wrong offset and executing whatever bytes happen to sit there — a classic "consumed-my-neighbor's-byte" signature, not a null-deref or stack-smash.

TEXT medium (mode-4, `--compile` → `as`+`gcc`) was **never** affected — it builds the mnemonic string instead of raw bytes, and GNU `as` encodes `[r12]`/`[rsp]` correctly regardless. Only BINARY medium (mode-3, the in-process JIT slab) hit this. `m3 ≡ m4 output` as a *design invariant* held for the emitted `.s`; it did not hold for the executed bytes, because this one encoder path only feeds BINARY.

**Fix** (additive, one line — cannot change encoding for any base register other than rsp/r12, so it cannot regress any currently-correct case):
```c
if ((m & 7) == 4) code += (char)0x24;
```

## Why this was hard to see from the trigger site

The first place I could reproduce it was Prolog's `IR_SUSPEND`/choicepoint `γ`-epilogue (`bb_suspend.cpp`'s `q$2F1_γ`-style exit), which does `lea r12,[rip+g_pl_zf_pending_cursor]; mov r12,[r12]` unconditionally on every successful return from a *called* (non-entry) predicate with a disjunction — 2+ clauses, or an if-then-else. That reads like a Prolog defect. It is not one: the same generic encoder path fires for **any** frontend's bare `[r12]`/`[rsp]` dereference; Prolog's ζ pending-cursor check is simply the first/most common caller of it that this session found. Root-caused via ASM-DIFF-FIRST per RULES.md: a two-clause `q(X):-X=1. q(X):-X=2.` witness crashes in m3, byte-identical `.s` runs clean in m4 (proves the bug is BINARY-encoder-specific, not a codegen/logic bug) — then gdb on the m3 slab (`ulimit -c unlimited`, `set breakpoint pending on`, break on the real runtime symbols since JIT'd code carries none) traced the exact fault to the byte immediately after a `movabs`-loaded global-address `lea` substitute, hand-decoded the raw bytes at the fault site (`4D 8B 24 4D 85 E4 0F 84 ...` — ModRM `0x24` correct, SIB should be `0x24`, is instead `0x4D`, which is literally the *next* instruction's own REX prefix byte being consumed as SIB), and traced it back to `x86_load_mem64` as the only call site building that exact byte shape.

## Measured impact

**Regression-verified before push:** full SNOBOL4 corpus 604/604 pass both modes (unchanged), Icon smoke 14/14 both modes (unchanged), Prolog smoke 4/5 unchanged (the one red, `clause`, is pre-existing and reproduces identically in mode-2 and mode-4, neither of which this patch touches). `corpus/benchmarks/snobol4/name_indirection.s` went from failing to emit at all to a real 926-line artifact — a second, independent confirmation this is a genuine cross-language encoder defect, not a Prolog-only one.

**Positive impact swept after the fact, against `FINDING-2026-08-27-seat14-prolog-second-entry-into-any-user-predicate-crashes-m3-m4.md`'s 19-kernel CRASH list** (`corpus/benchmarks/prolog/bench/*.pl`, `--run` only, post-fix, this session):
```
NOW PASS (rc=0), no longer crashing:  cal derive divide10 log10 ops8 times10          (6/19)
STILL CRASH, rc=139 (SIGSEGV):        crypt meta_qsort mu qsort queens queens_8
                                       queensn query sendmore                          (9/19)
STILL CRASH, rc=134 (SIGABRT):        nreverse nrev zebra                              (3/19)
STILL CRASH, rc=132 (SIGILL):         ham                                              (1/19)
```
Seat14's own 2-line minimal repro (`fib(20,F)` called twice; `fib/2` is itself 3-clause/disjunctive) now runs clean, printing `10946` both times — worth a note back to that finding and to the PZ-4 row, since it was framed as "not disjunction-specific" (their flat `bench__main, bench__main` no-choicepoint repro also crashed) but this fix alone clears their quoted repro. I have not re-isolated their flat-conjunction no-disjunction variant against the current tree; it may be a second, still-open trigger of the *same* class, or a distinct one — flagging rather than asserting.

## What's still open — and why I did not attempt it here

`sendmore.pl` itself (this task's actual target) still crashes post-fix, later and deeper than before (it now gets through many more nested predicate activations before failing — consistent with this fix having cleared the shallow, always-hit crash and exposed a second, deeper defect). I bisected a **separate, distinct** bug in the actual choicepoint-retry path (not the encoder — confirmed present identically in m3 *and* m4, so it's a logic/lowering bug, not a BINARY-medium issue):

Minimal witness: `digit(0). digit(1). main :- digit(X), X=\=0, write(X), nl.` — correct oracle answer `1`; SCRIP silently prints nothing and exits 0 (no crash, wrong answer) on this minimal case, and produces a genuine SIGSEGV on more elaborate cases like `sendmore.pl`. Traced with gdb (mode-4, real symbols) through the full resume sequence — `rt_pl_cp_pop3` → `rt_pl_zf_resume_set` → `rt_jmp_frame_lexprep2` all thread the popped trail mark correctly (verified byte-for-byte: captured `{v=3,i=0}`, correctly mirrored into the resumed frame at both the flag-check offset and the caller-declared `tm_off` offset) — but at the point `$unwind_nothrow` is actually invoked (to undo clause 0's binding before trying clause 1), its argument has been marshaled to `{v=3,i=1}`: the tag survives, the payload does not. `digit(1)` then tries to unify the still-bound-to-0 `X` against the literal `1`, correctly-but-wrongly fails, and that failure is what starves `sendmore.pl`'s search (and, at the scale of 8 nested choice-point variables instead of 1, evidently corrupts something badly enough to SIGSEGV rather than just misfire).

I stopped root-causing this one **on purpose, not from running out of leads** — `GOAL-PROLOG-100.md`'s `PZ-5` rung names this exact machinery (`g_pl_zf_pending_*`, `rt_pl_zf_resume_set/clear`, the lexprep2 override, `bb_call_proc_staged.cpp`'s fresh-frame re-open) as **"the pending-cursor machine"**, explicitly slated for wholesale deletion once PZ-4 (retained activation frames) lands, and the LIVE CURSOR (seat05, today) shows PZ-4 as an actively-worked, actively-owned row with its own task file and a fresh SIGILL witness of its own. Patching a value-marshal bug inside a mechanism that's already scheduled for full replacement would be throwaway work at best and duplicate/conflicting work at worst. Handing this off as evidence for that row instead: the exact repro above is a **third, independent** manifestation (encoder-clean, both-medium, non-disjunction-specific-in-trigger-shape-but-disjunction-specific-in-what-it-exercises) of the pending-cursor class, alongside seat05's omega-wire finding and seat07's lexprep-frame finding already cited on that cursor.

## Recommendation for this task's row

`prolog-sendmore-cryptarithm-segv`'s DONE-WHEN still fails (rc=139, not the crash it started as, but still not the oracle answer). The immediate crash this row was minted for is fixed and pushed. What remains is architecturally the PZ-4/PZ-5 gap, not a standalone SIGSEGV row — recommend re-scoping or closing this row with a pointer to the PZ ladder rather than continuing to chase it as an independent bug, per the task's own "if `-s1024m` fixes it... say so and re-title rather than curing it" precedent (same spirit: if the true cause is a keystone architectural gap, say so rather than force a local patch).
