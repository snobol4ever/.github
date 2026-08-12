# FINDING — HOME-WIRES (Claude Sonnet 5) — W-3 crash ROOT-CAUSED: the DEFER blob's own rsp-relative spine
# depth (ZD-1 "OWN RESULT" cell, `[rsp# + N]`) collides with the OUTER graph's `zls2_mark` slot at `[rbp-56]`
# once the blob is entered; NOT a WREG r10/r11 register-clobber, and NOT the stfh() split-predicate class the
# comments warn about (both ruled out empirically). No source changed. Zero SCRIP edits.

**SCRIP `a037b637`, corpus `1dd3ff15`, .github this commit.**

## Continuation of
`FINDING-2026-08-12r` (s39c), which found the crash and stopped at "diagnosis-in-progress, not a root
cause." This session ran the prescribed gdb hunt (RULES.md MONITOR-FIRST step 2/3: breakpoint + spin
through the JIT'd code) to completion.

## Reproduce
```
/home/claude/x64/bin/sbl -b corpus/probe/bb/witness_wreg_s39/W01_stored_pattern_defer_len_capture.sno   # => =S
./scrip --run corpus/probe/bb/witness_wreg_s39/W01_stored_pattern_defer_len_capture.sno                 # SIGSEGV, exit 139
```

## Two hypotheses ruled out first (both cheap, both wrong — recorded so nobody re-checks them)

**(1) r10/r11 wire-register clobber.** Watched r10/r11 continuously from `rt_defer_get_pat_fn`'s return
through the crash. They are set once (`lea r10,[rip+γ]` / `lea r11,[rip+ω]`) and never touched again before
the fault. Not the mechanism.

**(2) `stfh()` split-predicate drift** (the exact failure class `bb_match_begin.cpp`'s and
`bb_match_end.cpp`'s own comments name and worry about — "A drift between these two lines is the split-ends
failure"). Instrumented both files' `stfh()` macros with an env-gated diagnostic
(`SCRIP_WIRES_STFH_DIAG=1`) printing every input (`flat_stmt_frame`, `oscap_l()`, `flat_deep_arrival`,
`flat_jmp_entry`, `flat_lcl_proc`, `zframe_graph`, `flat_pat`, `flat_gen`, `has_replace_l()`). All 16 BEGIN
calls and all 5 END calls for this program print identical values (`stfh()=true` throughout). The two files'
macro text is also byte-identical (diffed verbatim). Not a spelling drift, not a value drift. Instrumentation
was temporary — reverted, rebuilt, diffed clean against `/tmp/*.orig` backups before continuing.

## Root cause, gdb-confirmed step by step

**Crash instruction:** `mov -0x38(%rbp), %rsp` inside `n27_match_end`'s success-exit unwind — this is
`x86_zls2_release_to_call(HKM())` (`x86_asm.h:2088`, CSTACK arm: `x86_align_leave() + mov rsp,slot +
x86_align_enter()`), restoring `rsp` from the `zls2_mark` slot the head saved at MATCH_BEGIN α
(`bb_match_begin.cpp:70`, `HKM()` = `qword ptr [rbp + -56]`). The slot holds `0x7fff00000000` — a
suspiciously round, corrupted value — instead of a real stack address, so the restore hands execution a
garbage `rsp` and the very next `push %r14` faults.

**Traced the corruption with a software watchpoint on `[rbp-56]`** (`watch *(uint64_t*)($rbp-56)`, set right
after `rt_match_enter` returns so `$rbp` is known for this run):

1. **Write 1 (correct):** MATCH_BEGIN α, `mov [rbp-56], rsp` — plants the real rsp
   (`0x7fffffff9ad0`), 48 bytes above the live rsp at that point. Sane.
2. **Write 2 (the bug, first hit):** the very next watchpoint hit lands at `pc=0x7ffff1600009`, **inside the
   stored pattern's own compiled blob** (`proc_PAT$0`, specifically `n0_match_assign_save_α` — the
   `IR_MATCH_ASSIGN_SAVE` box backing the `. X` capture in `P = LEN(*N) . X`). The faulting write is
   `mov dword ptr [rsp + 64], r14d` — this box's ZD-1 "OWN RESULT" cell store (`ZRESD(0)`, which the ZD-1
   raw-marker convention resolves to `[rsp# + 0]`, driver-computed offset, printed here as the literal `64`
   after the box's own `sub rsp, 16` carve).
3. **Confirmed the aliasing arithmetically, not just observationally:** at the moment of write 2,
   `$rsp = 0x7fffffff9ac0`. `0x7fffffff9ac0 + 0x40 (=64) = 0x7fffffff9b00`. `$rbp - 56` at the same instant
   is `0x7fffffff9b38 - 56 = 0x7fffffff9b00`. **Identical address.** The box's own result-cell store and the
   outer graph's `zls2_mark` slot are the same eight bytes of stack memory.
4. Two further watchpoint hits (`NV_GET_fn`, `_var_init` — ordinary runtime C calls made later in the
   program) keep overwriting the same address with their own locals, which is expected once the slot is no
   longer "reserved" from the outer graph's point of view — it's just live stack below whatever the C ABI
   currently considers the frontier.

**Why the addresses coincide:** `proc_PAT$0` (the stored pattern, compiled once at `P = LEN(*N) . X` and
invoked later via DEFER) is flat-wired FORTH-style code sharing the *same* rsp spine as its caller — it is
entered via `jmp rax` (through the WREG glue), not `call`, and carves its own boxes' cells with
`sub rsp, N` directly on top of whatever rsp was live when the jump landed. The ZD-1 convention's
`[rsp# + N]` raw marker is resolved by the driver purely from the **blob's own internal carve depth** — it
has no way to know that the memory 64 bytes above its current rsp happens to be an address the *caller's*
bookkeeping (MATCH_BEGIN/MATCH_END's `zls2_mark`, itself living at a **fixed rbp-relative offset**,
`[rbp-56]`, chosen specifically because "64-byte zone the GLUE-O carve already reserves to clear the stfh
HKQ region") considers reserved and dead until MATCH_END reads it back. The two addressing schemes — the
outer graph's `[rbp+const]` and the blob's `[rsp+const]` — are each internally consistent, but nothing
enforces that they don't overlap once a `jmp`-entered blob's rsp lands close enough to the outer frame's rbp
that the blob's own local carves reach back up into the `zls2_mark`/HKQ zone.

## What this is — and is deliberately NOT claimed to be

**This is very likely NOT WREG(r10/r11)-specific.** `bb_match_defer.cpp`'s blob-entry glue call
(`bb_glue_pass_wires_blob`, line 83) has never had an rcx/rdx twin at this exact site to A/B against — the
`SCRIP_WREG` "killswitch" is dead code per `FINDING-2026-08-12r`, so there is no live alternate spelling to
test. But the corruption mechanism traced above — a jmp-entered blob's own `[rsp+N]` local cell landing on
the caller's `[rbp+const]` bookkeeping slot — depends only on the two graphs' relative stack depths at the
moment of entry, not on which registers carried the continuation addresses. Register choice (r10/r11 vs
rcx/rdx) does not change where `rsp` sits when the blob starts executing. **This finding does not prove
WREG is innocent** (nobody has run the depth arithmetic for the rcx/rdx-glued path, and it may differ if
the rcx/rdx trio's own calling convention pushes/pops differently before the jump) — it only establishes
that the r10/r11 register content itself is not where the bytes go wrong. Correctly scoping "is this a
WREG-charter bug or a pre-existing DEFER/blob depth-accounting bug that happens to live at WIRES' one call
site" is Lon's call, not concluded here.

## Fix shape (not implemented this session — see "why stopped" below)

The `zls2_mark` slot's home (`HKM()` = `[rbp-56]`, a fixed 8-byte cell) and the DEFER blob's own frame need
either: **(a)** the blob's spine-depth accounting to reserve/skip past the outer graph's HKQ/HKM zone when
entered via a jmp from inside a MATCH construct carrying that zone (a blob-entry-time depth offset,
analogous to how `x86_zclaim`/`op_fc_bytes` already carve K bytes for the anchored-capture case) — this is
the shape closest to "the existing machinery, widened," or **(b)** move `zls2_mark` off a fixed rbp-relative
offset entirely and onto the W-4 arena wire-pair-slot layout this seat already owns building (the goal
file's own W-4 rung note — "the census named TWO shapes the layout must cover" — may need to become THREE
once this is folded in), since an arena slot is immune to blob rsp-depth collisions by construction the same
way the register wires are. **(b) is very likely the more durable fix** — it converts a fixed-offset
collision hazard (any future blob carving anywhere near this depth reproduces the same bug) into a
depth-immune one, which is exactly the property WREG's own charter comment claims for r10/r11 ("Registers
are depth-immune BY NATURE and carry NO OFFSET").

## What this does NOT establish
- **Whether other DEFER/stored-pattern shapes hit the same collision at a different, non-crashing offset**
  (silently corrupting some OTHER dead-looking stack byte instead of the `zls2_mark` cell) — this witness is
  the one shape that happens to land exactly on `[rbp-56]`; a body with a different local-cell count could
  land somewhere that looks survivable but isn't (wrong number silently computed, not a crash). Not checked
  this session — would need a small sweep of stored-pattern DEFER witnesses with varying capture-body sizes.
- **Whether `stfh()`-false graphs (the `FRQ(_.op_off+16)` legacy-slack arm instead of `HKM()`) have an
  analogous collision** at their own fixed offset. Not checked — this witness is `stfh()=true` throughout.
- **The exact byte budget needed for a fix** — how many bytes of headroom the blob's carve needs before it's
  provably clear of the outer zone, for graphs of arbitrary DEFER-body complexity.

## Why this session stopped at root-cause rather than landing a fix
Same reasoning as s39c's stopping point, now with more evidence behind it: (1) the fix touches
frame/depth-accounting machinery (`zls2_mark`'s home, or the blob spine-depth driver) that oversteps this
finding's own scope — the W-4 arena layout is explicitly this seat's charter (`GOAL-SN4-HOME-WIRES.md` W-4:
"THIS SEAT OWNS THE LAYOUT") and folding zls2_mark into it is a real design decision, not a one-line patch;
(2) landing option (a) — widening blob-entry depth accounting — without checking whether it disturbs the
`SCRIP_OS_CAP`/anchored-capture machinery that already carves near this same zone risks a second, harder-to-
diagnose collision; (3) this genuinely changes W-3's and W-4's scope (W-4's layout note may need a third
shape) and W-6/RTCC's re-entrant scope (a jmp-entered blob revisiting its own carve on recursive DEFER use
is exactly the kind of re-entrant case W-6 is chartered to check) — a decision worth a clear write-up before
a fix lands under time pressure, not a unilateral same-session patch.

## What's committed
- `.github`: this finding + cursor update.
- **SCRIP: zero changes** (temporary `stfh()` diagnostic instrumentation added and fully reverted;
  `diff` against the pre-session tree is empty).
- **corpus: zero changes** (no new witnesses this session — reused s39c's `W01_stored_pattern_defer_len_capture.sno`).

## Recommended next steps (Lon's call)
- **(a)** Decide whether the fix belongs at W-3 (blob-entry depth accounting) or W-4 (fold zls2_mark into
  the arena layout) — this finding argues for W-4 but the decision affects two seats' scope.
- **(b)** Once decided, the fix itself is now well-scoped: either widen the blob-entry carve to skip past
  the outer HKQ/HKM zone, or relocate `zls2_mark` to a depth-immune arena slot.
- **(c)** After a fix lands, sweep for the "silent wrong-offset" variant named above — other DEFER/capture
  body shapes may collide with OTHER outer-graph slots (the anchored-capture δ region, the PATCTX quartet)
  without crashing, which is worse than a SIGSEGV because it produces a wrong answer instead of a loud
  failure.

## LIVE CURSOR — this session root-caused the W-3 crash (did not fix), did not touch SCRIP source, did not
move the watermark. Floor unchanged: **160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}** (this crash
is a new construction outside that suite, as before).
