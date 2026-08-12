# FINDING — HOME-WIRES s39c (Claude Sonnet 5) — SCRIP_WREG killswitch is DEAD CODE (documented, never
# implemented); r10/r11 wire glue has been unconditionally live at the DEFER blob-entry site; NEW crash
# found in the same mechanism, oracle-confirmed, not yet root-caused

**SCRIP `0bbf092b`, corpus HEAD+witness commit, .github this commit. Zero SCRIP source edits. corpus gains
2 new files (1 `.sno` + `.ref` pair + README) under `probe/bb/witness_wreg_s39/`.**

## Why this session looked at W-3 at all
s39a/s39b spent the whole session on X01 (ARBNO dispatcher), which the cursor itself keeps flagging as NOT
this seat's charter. With push and MON-CAP both credential-blocked, used remaining budget to actually look
at W-3 (WREG mechanism) — the seat's own charter, six sessions untouched — specifically the claim in the
goal file: *"Killswitched; default emission byte-identical to HEAD"* and the dormant-function pointer:
*"The emitter already exists and is dormant: `bb_glue_pass_wires_blob()` in `bb_glue_flat.cpp:154-159`."*

## Finding 1 — `bb_glue_pass_wires_blob` is NOT dormant; it has one live, unconditional caller
`grep -rn bb_glue_pass_wires_blob src/` finds exactly one call site: `bb_match_defer.cpp:83`, called
directly with no `IF(...)` guard around it. This is the DEFER blob-entry glue — every `LEN(*N)`/deferred
pattern in the compiler goes through this path today, at HEAD, unconditionally emitting `lea r10,...` /
`lea r11,...` instead of the `rcx`/`rdx` spelling `bb_glue_pass_wires` (the non-WREG twin) uses.

## Finding 2 — `SCRIP_WREG`, the documented killswitch, does not exist in the source
Three separate comments claim it:
- `bb_glue_flat.cpp:158`: *"KILLSWITCH SCRIP_WREG: OFF reverts byte-identical to the rcx/rdx spelling above"*
- `bb_match_defer.cpp:83`: *"Under SCRIP_WREG=1 the wires ride r10/r11 ... under 0 this is the rcx/rdx trio"*
- `bb_templates.h:68`: *"Falls back to bb_glue_pass_wires verbatim when the switch is off."*

`grep -rn 'WREG' src/ -i` finds ONLY these three comments and the function/variable names themselves — no
`getenv("SCRIP_WREG")` anywhere. **Empirically confirmed, not just grep-inferred:** compiled the same
program with and without `SCRIP_WREG=0` in the environment (`--compile`, diffed the emitted asm) —
byte-identical output. The killswitch is aspirational documentation for a mechanism that was never wired
up. This directly contradicts the goal file's own W-3 status line ("default emission byte-identical to
HEAD") — the default emission is NOT byte-identical to a no-WREG HEAD; WREG's r10/r11 spelling has been the
ONLY spelling reachable at the DEFER blob-entry site since whenever this landed (not dated by this session
— `git log` archaeology not done, out of scope for a read-only investigation).

## Finding 3 — a genuine, previously unrecorded SIGSEGV in exactly this mechanism
While confirming Finding 1/2 empirically, constructed a probe to inspect the emitted glue and it crashed.
Oracle-verified minimal repro (`corpus/probe/bb/witness_wreg_s39/W01_stored_pattern_defer_len_capture.sno`):
```
        N = 2
        P = LEN(*N) . X
        S = 'ab'
        S ? P                                            :F(NO)
        OUTPUT = '=S'                                    :(EN)
NO      OUTPUT = '=F'
EN
END
```
`sbl -b` → `=S`. `scrip --run` → SIGSEGV (exit 139). **NOT covered by the existing D07/D08/D09 DEFER
probes** — checked each: D07 is the same `LEN(*N)` idiom but INLINED at the match site, not stored in a
variable first; D09 wraps `*P` in ARBNO, a different shape entirely. This probe's trigger needs BOTH: the
DEFER-bearing pattern stored in a variable before the match (`P = LEN(*N) . X` then `S ? P`, not
`S ? LEN(*N) . X` inline), AND a capture (`.`) on the LEN. Removing either condition (verified with two
sibling variants, not committed — see witness README) makes it pass.

**gdb backtrace (address-only, no debug symbols resolved the frame — see caveat below):**
```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff16017a9 in ?? ()
r10  0x7ffff16014a9
r11  0x7ffff16014ae
rax  0x0
rsp  0x7fff00000000      <- suspiciously round; looks corrupted, not a legitimate stack address
rbp  0x7fffffff9ba8      <- this one looks like a normal stack address, for comparison
```
The crashing PC is exactly 5 bytes past r10's value — consistent with a `jmp r10` having fired and
execution running a handful of bytes into whatever r10 actually pointed at before faulting. rsp's value is
corrupted to a suspiciously round address, which is a strong tell (real stack addresses in this container
are not round numbers) but NOT independently confirmed against a known-good rsp at the fault site — I did
not single-step from the JIT entry to pin the exact corrupting instruction. **This is diagnosis-in-progress,
not a root cause.**

## What this does NOT establish
- **Correlation, not proven causation, between Findings 1/2 and Finding 3.** The crash is IN the mechanism
  Finding 1/2 describes (confirmed: `n26_match_defer_α` in the disassembly matches `bb_match_defer.cpp`'s
  glue call), but whether it's specifically the r10/r11 wire spelling that's broken (vs. some unrelated
  defect in the stored-pattern-DEFER-with-capture path that happens to live at the same site) is NOT
  established. Since there is no working `SCRIP_WREG=0` fallback to A/B against, this can't be tested by
  toggling the killswitch — the killswitch doesn't exist.
- **Whether this is new or has been silently present since WREG's landing.** No `git log`/`git blame`
  archaeology done this session (read-only investigation budget went to reproduction + isolation, not
  history).
- **Root cause.** No source-level gdb trace (breakpoints on the actual C++ template functions, stepping
  through `bb_match_defer`/`bb_glue_pass_wires_blob`'s emitted bytes) was done — only a raw post-mortem
  backtrace on the already-crashed process. RULES.md's prescribed hunt (spin/ignore-counter breakpoint at
  the bracketed C site, single-step to the land mine) was NOT run; this finding is the "first divergent
  event" identification, not the fix.

## Why this session stopped here rather than fixing it
Same three-part reasoning as s39a/s39b: this is squarely W-3 territory (unlike ARBNO, actually IS this
seat's charter) but (1) landing a fix on an unconfirmed mechanism risks the same false-confidence trap as
the X01 sessions' first two hypotheses, both of which looked right and were falsified on the second check;
(2) a proper gdb hunt needs real budget for single-stepping through JIT'd code without symbols, which is
slow and this session already spent significant budget on the X01 witness construction; (3) most
importantly — **this is a correctness-relevant discovery about the seat's own charter status that Lon
should see before anyone lands a fix**, since it changes W-3's status from "dormant, safe to leave alone"
to "live, uncontrolled, and crashing on at least one construction." That's exactly the kind of fact a
handoff should surface rather than a session unilaterally patching around.

## What's committed
- `corpus`: `witness_wreg_s39/W01_stored_pattern_defer_len_capture.sno` + `.ref` (oracle) + README.
  NOT wired into `run_suite.sh` (would silently redefine "green" for this goal without sign-off).
- `.github`: this finding + cursor update.
- **SCRIP: zero changes.**

## Recommended next steps (Lon's call, not this seat's alone, per the reasoning above)
- **(a) Immediate, cheap, arguably overdue regardless of the crash:** either implement the documented
  `SCRIP_WREG` env-gate for real (so W-3's "killswitched" claim becomes true), or update the three comments
  + the goal file's W-3 description to stop claiming a killswitch exists. Leaving stale safety documentation
  in place is itself a hazard — the next session (or this one, next time) could reasonably try
  `SCRIP_WREG=0` as a debugging step and get silently ignored.
- **(b) The real fix needs a proper gdb hunt** on `W01_stored_pattern_defer_len_capture.sno` — breakpoint at
  `bb_match_defer`'s C++ template call site is available in this container (no MON-CAP/csnobol4 dependency;
  this is a crash, not a wrong-answer, so RULES.md's MONITOR-FIRST 2-way sync-step tooling isn't even needed
  — a plain gdb spin/ignore-counter breakpoint at the JIT'd code suffices, same as any other SIGSEGV hunt in
  this codebase).
- **(c) Once fixed, re-audit whether this crash class affects the non-DEFER PROC-shim WREG conversions** the
  s22v comment says are still queued (`bb_call_proc_staged` ×5, `bb_call_value`, `bb_match_capture`,
  `bb_match_end`) — if the DEFER site (the one WREG conversion that DID land) has a live bug, the queued
  conversions inherit the same risk surface until this is understood.

## LIVE CURSOR — this session did NOT touch SCRIP source, did not move the watermark
Floor unchanged: **160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}** (this crash is NOT in that set
— it's a new construction, not a suite member, so it doesn't move the count). New this session: a real,
previously unrecorded status finding about W-3 (dead killswitch) plus one oracle-verified crash witness in
the same mechanism, not yet root-caused.
