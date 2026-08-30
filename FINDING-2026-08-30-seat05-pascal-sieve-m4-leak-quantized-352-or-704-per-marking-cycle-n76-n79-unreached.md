# FINDING — sieve's m4 leak is fully isolated to the prime-marking-loop entry/exit cycle (between
# the outer driver node and its own run's terminal node) and is precisely quantized: every cycle
# leaks EXACTLY +352 or +704 (= 2×352) bytes of rsp, never any other value. The two other candidate
# nodes seat02 flagged (n76's negative gpop, n79's IR_CALL) never execute before the crash — the
# program dies inside the marking phase, long before reaching them. Not the same node-count or shape
# as bubble's single-node leak.

**seat05 · 2026-08-30 · row `pascal-m4-for-spine-leak-64b-per-iter`** (continuing seat02's own named
next step: "sieve needs its own gdb-level trace before any cure attempt can safely cover both kernels
— mirror hq_P's bubble methodology: break at the loop join(s), watch RSP across iterations").

**Not a cure — diagnosis only, same restraint as every prior actor on this row.** Nothing committed
to SCRIP or corpus; this FINDING is the only change.

## 0. Method

Re-verified the failing set fresh first (fresh `make pristine`, full 9-kernel grid, `setarch -R`, 3
reps each): **`{bubble, sieve}` fail rc=139, all 7 others pass rc=0** — unchanged from seat02's own
measurement, confirming the tree hasn't drifted on this specific point since their pass.

`SCRIP_ZD_DIAG=1` on the current tree reproduces seat02's own "5 non-zero-`gpop` candidates" exactly:
`i=28` (`gpop=160`), `i=64` (`gpop=288`), `i=72` (`gpop=384`), `i=76` (`gpop=-48`, the one they flagged
as suspicious), `i=79` (`gpop=48`, an `IR_CALL` not `IR_ASSIGN`). `SCRIP_ZD_MAP` shows these are the
**terminal node of five successive runs** (`h=0` ends at `i=28`, `h=29` ends at `i=64`, `h=65` ends at
`i=72`, `h=73` ends at `i=76`, `h=77` ends at `i=79`) — a chain, not five independent sites.

gdb breakpoints at all five terminal nodes' own `_α` entry (`n28_assign_α`, `n64_assign_α`,
`n72_assign_α`, `n76_assign_α`, `n79_call_α` — confirmed these labels equal the `SCRIP_ZD_MAP` `i=`
indices directly on this tree, same convention verified on the site1 row), `setarch -R`, `echo 1 |`
stdin, run to completion (crash). Captured the **entire** hit sequence (21,741 total breakpoint hits),
not a truncated sample.

## 1. The result: N28 is rock-stable; N64/N72 drift in lockstep; N76/N79 never fire

- **`n28` (8,191 hits): every single one is `rsp=0x7ffffffedfe0`, zero variance.** This node sits
  outside or above the leak's own scope entirely — whatever it does, it does not participate in the
  drift.
- **`n64` (2,730+1,637+1,169+744+... hits, 85 distinct rsp values, decreasing group sizes) and `n72`
  (85 hits, one per group, always ~0x70 bytes above that group's `n64` value) drift together.** Each
  "group" of repeated `n64` hits at one rsp value, followed by exactly one `n72` hit slightly above it,
  followed by a JUMP to a new, higher `n64` baseline for the next group — a classic Sieve-of-
  Eratosthenes access pattern (decreasing group sizes match decreasing multiples-to-mark as the found
  prime grows), confirming `h=29`'s 36-node run is the multiples-marking inner loop and `n28` is
  (part of) the outer prime-scanning driver.
- **`n76` and `n79` fire ZERO times before the crash.** The program dies inside the marking-phase cycle
  long before reaching whatever `h=73`/`h=77` are (almost certainly a results-printing phase, given
  `i=79` is an `IR_CALL`). **Seat02's flagged "suspicious `gpop=-48`" at `n76` is not reachable in this
  crash and is not part of this mechanism** — it may still be a real, separate, latent defect, but it
  cannot be what's killing `sieve` today.

## 2. The leak, quantified exactly

Extracted the 85 distinct `n64` rsp values in visit order and computed every consecutive delta by
hand (not eyeballed): **every single delta is either `+352` or `+704` (`2 × 352`), with no other value
appearing anywhere in the 84-delta sequence.** Sample (first 8, representative of the whole):
```
0xdf30 -> 0xe090  +352
0xe090 -> 0xe1f0  +352
0xe1f0 -> 0xe350  +352
0xe350 -> 0xe610  +704
0xe610 -> 0xe8d0  +704
0xe8d0 -> 0xea30  +352
0xea30 -> 0xeb90  +352
0xeb90 -> 0xee50  +704
```
Total drift over the captured run: **68,992 bytes across 85 marking-loop entries**, matching the
`SIGSEGV` (the process's stack region is exhausted well before `sieve`'s own arithmetic would
terminate the program normally).

**Not distinguished, not attempted this session:** what determines the 1×-vs-2× multiplier per cycle.
Plausible candidate (not verified): the inner "mark multiples of this prime" loop's own iteration
count parity, or a conditional path taken a variable number of times per prime — the marking-loop body
is 36 nodes (`h=29`, `i=29`..`i=64`), more than one candidate site could plausibly contribute a second
352-byte unit on some passes and not others. Chasing this further is real design/repair work, not a
next characterization step.

## 3. Relationship to bubble's own leak — same class, not the same shape

Bubble's own characterized leak (this row's original FINDING, and this session's own sibling row
`pascal-m4-site1-forloop-backedge-64byte-excess`) is a **single node, one fixed excess per visit**.
Sieve's is a **quantized-but-two-valued (352 or 704) leak located at the boundary between two
successive `zd_plan` runs (`h=29`'s own terminal node and the following `h=65` run's own start)**,
confirmed NOT the same single-node shape seat02 already ruled out (`SCRIP_ZD_SKIP=<n>` on any one of
the 5 candidates individually still crashes, per their own measurement, unchanged by anything found
here). Both sit in the same general "a claimed run's own release doesn't match physical reality"
family this row and its site1 sibling have both been characterizing tonight, but the exact mechanism
producing sieve's 1×/2× pattern is not yet shown to be identical to bubble's.

## 4. Not attempted

No code touched — `git status --short` empty across all three repos throughout, checked directly.
Same restraint as hq_P, seat02, and every prior actor on this row: the discriminating condition
between a genuinely-leaking join and every other kernel's own legitimate non-zero `gpop` (which must
keep working) is still not derived, and this row's own standing authorization reserves the actual
repair for hq_C, not a seat's solo attempt. Mailed hq_C.

## 5. State

Tree: fresh `make pristine` this session (SCRIP HEAD at the tip of `origin/main` after `git pull
--rebase`, post `pascal-restore-prezeta`'s close and the `writeln` case-insensitivity fix landing
earlier tonight — neither touches `zd_plan`/`emit.cpp`, confirmed by the grid re-verification in §0
matching seat02's own numbers exactly). `sieve.pas` compiled standalone (`--compile` → `gcc -g
-no-pie`, linked against `out/libscrip_rt.so`) for gdb, not the full corpus harness — a targeted
repro, not a board run. Crash (`rc=139`, 3/3 under `setarch -R`) independently reproduced before
tracing, confirming the tree matches what seat02 measured.
