> **SUPERSEDED 2026-07-06 (Claude Sonnet 5), same day.** Both items below are now LANDED, not parked:
> the fresh-frame patch is committed (SCRIP `920861ec`), and the INPUT-EOF bug this finding bracketed
> is independently root-caused and fixed (SCRIP `3cf0cc89`) — see `GOAL-SNOBOL4-BB.md` BRACKET 1 for the
> current, authoritative writeup (including why the fix needed a second part in `emit.cpp` beyond the
> `bb_var_global.cpp` guard this document's author didn't reach). Kept here verbatim as the historical
> record of the diagnostic session that bracketed the bug via gdb breakpoint hit-counting — the method
> and the evidence chain below are still accurate and worth reading; only the "not yet fixed" framing
> is stale.

# FINDING 2026-07-06 — SN4-PAT defer-freshframe: +9 recursive-grammar patterns, word-family INPUT-loop hang isolated

## Summary
Landed the WIP `bb_match_defer.cpp` fresh-frame patch (deferred `*PAT` / pattern-valued-variable
match `X ? PAT` now allocates a fresh 64 KB ζ frame per evaluation via `rt_zls_alloc` instead of the
shared persistent `rt_frame()`). This is a **net +9 pattern tests** on the SNOBOL4 crosscheck, clean in
BOTH modes. It also exposed a pre-existing hard-word-family issue as a mode-3/mode-4 DIVERGE (2 tests).

## Measured crosscheck delta (scripts/test_crosscheck_snobol4.sh)
| Mode        | Baseline (rt_frame) | After patch |
|-------------|---------------------|-------------|
| `--run`     | 230 pass / 46 fail  | **241 / 35** |
| `--compile` | 230 pass / 20 fail / 26 skip | **239 / 11 / 26** |
| DIVERGE     | 0                   | **2** (word2, word4) |

**The +9 (clean both modes):** 115, 120, 126, 127, 131, 138, 139, 146, 152 — the calc / JSON /
boolean-expr recursive-grammar patterns that recurse through a deferred pattern variable and therefore
need a distinct frame per nesting level (the shared `rt_frame()` clobbered the parent's cursor-save
slots on re-entry). Confirmed passing in `--run` and `--compile`.

## Two edits in this session (both in src/templates/bb_match_defer.cpp)
1. **The WIP patch** (`.github/WIP-sn4pat-defer-freshframe-2026-07-06.patch`, applied cleanly):
   `rt_frame()` → `rt_zls_alloc(65536)` for the deferred-pattern call frame, with an unconditional
   `rt_zls_release()` after the call.
2. **Release-on-failure correction** (this session): the WIP released the fresh frame UNCONDITIONALLY,
   including on the SUCCESS path. That contradicts the rt.c generator convention (rt.c:434/444 release
   `if (IS_FAIL(result))` only) — a successful match's frame must stay live because the pattern box can
   be re-entered on BACKTRACK and its captures/cursor-saves referenced. Restructured to release only on
   the failure branch (`cmp eax,1; je L1` success skips release and → γ; failure → release → ω). Uses a
   second box-local label `L1` (verified: `.Lx<uid>_<n>` is per-box unique, `X86_INTERNAL_BASE+n`;
   L0/L1 coexist safely). **Behaviour-neutral on the current suite** (241/35, 239/11 unchanged) but
   removes a latent backtrack-path corruption; kept on correctness grounds.

## THE REMAINING BUG (word2/word4 DIVERGE) — precisely bracketed, needs gdb/monitor
`X ? PAT` where PAT is a pattern-valued variable, matched in an **INPUT loop**, prints CORRECT output
then **hangs** (non-termination at the INPUT/EOF boundary → `:F(END)` never fires → infinite LOOP).
mode-3 captures the correct pre-hang stdout (harness `|| true` swallows the timeout) so it scores as a
false PASS; mode-4 fails outright → the two disagree → DIVERGE.

**Minimal deterministic repro (6 lines), hangs under `--run`:**
```
	PAT = LEN(1) . C
LOOP	LINE = INPUT		:F(END)
	LINE ? PAT		:F(LOOP)
	OUTPUT = C		:(LOOP)
END
```
run as: `printf 'a\nb\nc\n' | ./scrip --run repro.sno`  → prints a b c, then exit 124 (timeout).

**Established facts (bracket):**
- Triggered by the fresh ALLOC, not the release: reverting to release-on-failure did NOT fix it; the
  passing recursive cases (e.g. 120) that do NOT loop over INPUT exit 0 cleanly.
- Baseline `rt_frame()` (persistent shared frame) does NOT hang — so this is a fresh-frame side effect.
- Three mechanistic hypotheses (frame release corruption; r12 dangling; captures-in-frame) were each
  falsified by inspection — REGISTER-LAYOUT.md confirms the pattern fn's own glob preamble is
  `push r12; mov r12, rdi`, so r12 IS preserved by the callee; r13/r14/r15 (subject base / cursor /
  length) are the likelier clobber suspects across the deferred call, but NOT yet confirmed.

**Why it stopped here:** per RULES.md MONITOR-FIRST, a divergence must be found with the sync-step
monitor (or the gdb spin-counter bracket), NOT by guessing. This sandbox has **no gdb** and the monitor
oracles (`/home/claude/x64/bin/sbl`, `/home/claude/csnobol4/snobol4`) are **not built**. Standing up
one of those is the prerequisite for the fix and is the correct next step — do NOT hand-patch the
codegen further without it.

## NEXT STEP (mechanical, once tooling is up)
1. Build an oracle (`scripts/build_spitbol_oracle.sh` or clone `x64` for the prebuilt `sbl`) + the
   monitor IPC libs, OR `apt-get install gdb`.
2. On the 6-line repro: monitor → first divergence, or gdb break on the INPUT sink + the deferred-match
   return, spin-count to the EOF iteration, single-step to the instruction that leaves the loop-control
   / EOF verdict reading the wrong r13/r14/r15 (or frame slot). Prime suspect: subject-model registers
   (r13/r14/r15) not restored across the deferred `call rcx`. If confirmed, save/restore r13/r14/r15
   (or the outer cursor) around the call in bb_match_defer.cpp — analogous to the r12 preamble.
3. Re-run crosscheck: DIVERGE must return to 0 with the +9 preserved; word2/word4 should then pass both
   modes (cracking into the known-hard word family: cross, word1-4, wordcount).

## Everything else still red (unchanged, NOT regressions) — the SN4-PAT roadmap
The other 33 `--run` fails are pending architecture the lowerer FATALs on by design, not bugs:
- **Runtime (variable) charset args** for SPAN/ANY/BREAK (fence_fn 063-066): `SPAN('0..9')` lowers,
  `SPAN(digits)` FATALs "outside the SN4-PAT subset". Needs the IR_MATCH_* runtime-charset family.
- **v3 generator nesting** (116, 142, 145, 151): "nested ARBNO / FENCE inside … are v3".
- **EVAL/CODE** (140, 141): "EVAL and CODE are outside the landed subset".
- **OPSYN / redefine / NRETURN / arg-local** (1011, 1013, 1015, 1017); **indirection** (213);
  **&STCOUNT** (082); capture edge cases (059, 062, 063, W07_capt_*); expr_eval + 3 library tests.

## Build/verify
- `make scrip` + `make libscrip_rt` both green (X86-only, modes 3/4).
- Change surface this session: `src/templates/bb_match_defer.cpp` only (+15 / −3).
- Prereqs installed in sandbox: libgc-dev, flex, m4, nasm, libgmp-dev.

---

## UPDATE (gdb session): word2/word4 divergence root-caused — it is a PRE-EXISTING INPUT-EOF bug, NOT caused by the defer-freshframe patch

Installed gdb and traced the word2/word4 hang to a **separate, pre-existing codegen bug** that the defer-freshframe patch merely UNMASKED. The patch itself is clean.

### Evidence chain
1. gdb breakpoint hit-count on the real INPUT sink `core.c:2701 input_read()` (getline on stdin;
   returns FAILDESCR at EOF): the 6-line defer repro hits it **47,332 times** (timeout-capped) →
   the loop SPINS on INPUT; after EOF, `LINE = INPUT :F(END)` does **not** branch to END.
   (Note: INPUT does NOT route through the `read` builtin at by_name_dispatch.c:2988 — 0 hits there.)
2. Read the emitted `.s` for the repro: the INPUT read box (`IR_VAR` → `call NV_GET_fn` for name
   "INPUT") does `call NV_GET_fn; mov [slots]; jmp <next>` — an **unconditional** forward jump, with
   **no `cmp eax,99; je <β-chain>` FAILDESCR check**. Contrast the SNO$MKPAT call box in the same
   graph, which correctly guards with `cmp eax, 99 ; je <fail>`. The INPUT read is missing its fail
   guard, so EOF (FAILDESCR=99) is stored into LINE and execution falls through instead of taking :F.
3. **Proof it is independent of the defer patch:** a plain INPUT loop with NO deferred match —
   `LOOP LINE = INPUT :F(END) / OUTPUT = LINE :(LOOP) / END` — printed **2,789,260 lines in 4 s**
   under `--run` (spinning on blank FAILDESCR output). Its emitted INPUT read box is byte-identical to
   the repro's: no fail guard.

### Why the defer-freshframe patch changed word2/word4 from FAIL→DIVERGE (not a regression)
With the OLD shared `rt_frame()`, the deferred pattern proc ran with `r12 = g_main_frame` and wrote its
capture slot `[r12+16]` and its FAIL-exit `[r12+0]=99` — the SAME frame slots `main` uses (the emitted
`main` body writes the pattern value to `[r12+16]`; see `.s`). That slot corruption made word2/word4
produce WRONG output but terminate (they were plain FAILs). The fresh-frame patch gives the proc its own
frame, so `main`'s slots are no longer clobbered → the match is now CORRECT → which then reaches the
pre-existing INPUT-EOF spin. Hence FAIL(wrong-output, terminating) → DIVERGE(correct-output, hangs).
The +9 recursive-grammar wins come from the same fix (fresh frame per nesting level).

### The real fix for the word/cross family (SEPARATE work, precisely located)
Teach the INPUT read (and any input-associated / fail-capable keyword variable) to emit a FAILDESCR
guard after the value read: `cmp eax, 99 ; je <box β-chain>` — i.e. mark the `IR_VAR` read of INPUT
(and TERMINATE/etc. where applicable) as fail-capable so the box graph wires its β (fail) edge to the
statement's :F target, exactly as `rt_call_arr`/SNO$MKPAT boxes already do. This spans IR generation +
box α-emission (the generic `IR_VAR` path in the lowerer does not currently distinguish fail-capable
reads — `grep -n INPUT src/lower/lower_snobol4.c` is empty). This is NOT a defer-template change and
should be done and validated under the monitor as its own change. Expected payoff: the entire
`cross / word1 / word2 / word3 / word4 / wordcount` cluster (all INPUT-to-EOF loops), and any other
INPUT-loop tests, become terminating; word2/word4 DIVERGE returns to 0.

**[2026-07-06, later session, Claude Sonnet 5]: this prediction was half right.** The whole cluster now
*terminates* (no more hangs), and word2/word4 do fully PASS both modes (DIVERGE→0) — but word1, word3,
cross, and wordcount hit FOUR SEPARATE, DISTINCT bugs of their own once the hang stopped masking them
(capture-into-`OUTPUT`, a mid-chain-generator capture shape, an undiagnosed wrong-output, and an
unrelated lowerer FATAL respectively). The actual fix landed was also NOT `by_name_dispatch.c` — INPUT's
read never routes through that file at all (confirmed by the 0-hits note above); the real fix was in the
generic `IR_VAR` path exactly as this document predicted, in `bb_var_global.cpp` + `emit.cpp`'s chain-BFS
ω-discovery (the latter step wasn't anticipated here). See `GOAL-SNOBOL4-BB.md` BRACKET 1 for the full
writeup and the four newly-surfaced bugs.

### Net state of THIS session's change
`src/templates/bb_match_defer.cpp` only (+15/−3): fresh 64K frame per deferred eval + release-on-failure.
Crosscheck: `--run` 241/35, `--compile` 239/11/26, DIVERGE 2 (word2, word4 — the unmasked INPUT-EOF bug).
No regressions to the failure set; +9 recursive-grammar patterns fixed in BOTH modes.
