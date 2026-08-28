# FINDING 2026-08-28 (seat03) — `icn-recogn-genqueen-suspend-shape`: fresh re-measurement (signatures moved since 08-27) plus a much smaller synthetic reproduction than the existing 30-line witness

## Context
Row `icn-recogn-genqueen-suspend-shape`, un-parked by Lon 2026-08-28. STEP 1 of its own `## NEXT`
asks to re-measure both witnesses at HEAD before any cure work, since hq_P is mid-flight on
`icon-n2-generator-activation-frames` (104 commits since their lock per this row's own text) and "the
class may have moved." It has. This is that re-measurement plus bounded, non-blocking diagnosis
(STEP 2's own allowance) — **no frame-protocol code touched**, per this row's explicit instruction to
coordinate with hq_P's lane first.

## Fresh measurement — both still red, but the failure SIGNATURES changed since seat08's 08-27 note

| witness | 08-27 (seat08) | 2026-08-28 (this session, fresh pull+`make pristine`) |
|---|---|---|
| `jcon_recogn` | crash (unspecified detail) | `rc=139` SIGSEGV, both modes, unchanged in shape |
| `jcon_recogn` + `SCRIP_ICN_GENFRAME2=1` | "byte-identical crash" (seat08) | **now `rc=124` (times out)** — no longer byte-identical to the no-flag crash |
| `jcon_genqueen` | m3 hang `rc=124`, m4 SIGSEGV | **now `rc=1` both modes**: `scrip: runtime error: ERROR 246 -- stack overflow (unbounded or too-deep recursion exhausted the call stack)` — a controlled detection, not a raw hang/crash |
| `jcon_genqueen` + `SCRIP_ICN_GENFRAME2=1` | (not tested at the time) | `rc=124` (times out) |

Genqueen's shift from "silent hang / SIGSEGV" to "cleanly-detected stack overflow" is consistent with
the recently-landed unconditional stack-guard (`src/runtime/rt/rt_stack_overflow.c`, per root
`CLAUDE.md`) now catching what used to run away silently — it does not mean the underlying generator-
frame issue is fixed, only that its failure is now diagnosed instead of silent.

## A much smaller reproduction than the existing 30-line witness

`rung36_jcon_recogn.icn` is a textbook mutually-recursive CFG recognizer (`s()`/`t()`, alternation,
backtracking via `suspend`). Bisecting the *input* first: **even the simplest possible accepting
input, a single `"c"` (matching `<s> ::= c` directly, zero recursion), crashes** — with a *different*
signal (`SIGBUS`, `rc=135`) than every other input tested (`SIGSEGV`, `rc=139`), which by itself
suggests address-dependent memory corruption rather than one fixed faulting instruction.

Bisecting the *program shape* next, all of the following crash identically (`SIGSEGV`, `rc=139`),
including the most minimal:
```icon
procedure main(); write(s()); end
procedure s(); suspend "c"; end
```
No recursion, no mutual recursion, no alternation, no parameter indirection, no `?`-scan, no `&`
conjunction — a single user-defined procedure containing nothing but one `suspend` statement, called
once and its result passed straight to `write()`. Also crashes identically when the same minimal `s()`
is invoked via an `if`-condition, via `every`, or via a parameter (`goal := s; ...; goal()`), and when
combined with `&` conjunction or a `?`-string-scan in isolation or together (all combinations tested;
none avoid the crash). **This is not "a sixth backtracking shape icon-n2's five witnesses miss" — the
minimal case has no backtracking, no recursion, and no alternation at all.**

gdb on the crash (ptrace, no env var, per RULES.md MONITOR-FIRST): `SIGSEGV` at `rip=0x0000000000006361`
— an implausibly low address, unmapped, no symbol. `rsp`/`rbp` both look like ordinary, plausible stack
addresses. This is the classic signature of a corrupted resume/return address being jumped to (a
generator's saved resume point overwritten with something that is not a real code address), not a
straightforward null-pointer dereference.

**With `SCRIP_ICN_GENFRAME2=1` armed, the minimal case's failure mode changes but does not resolve**:
`write(s())` now exits `rc=0` with **empty output** instead of crashing — `write()` silently produced
nothing where `"c"` was expected. Neither arm is correct; the flag changes *how* this breaks, not
*whether*. The slightly more complex synthetic case (parameter-indirection + `&` conjunction + `?`-scan,
i.e. closer to `recogn`'s actual shape) still crashes identically with the flag armed.

## Broader signal, reported neutrally — not chased further, may simply reflect active WIP

`grep -l suspend` over all `rung36_*.icn` finds 12 files. Of those, several currently `FAIL` (not the
already-tracked `XFAIL`) with suspend-adjacent symptoms: `jcon_cxprimes` (`rc=139`, crash),
`jcon_level` (`rc=1`), `jcon_scan2` (`rc=139`, crash, and its `want`/`got` diff shows fewer backtrack
iterations produced than expected — consistent with a generator/backtrack accounting issue, not
independently diagnosed here). Whether these are new fallout from `icon-n2`'s in-flight work, pre-
existing and simply outside anyone's tracked scope yet, or unrelated, is **not established by this
finding** — flagged for hq_P's own situational awareness, not asserted as fact, and explicitly not
folded into this row's scope (this row is recogn+genqueen only).

## What was NOT done (deliberately, per this row's own instruction)
- No frame-protocol code touched. `icon-n2-generator-activation-frames` is hq_P's active, fast-moving
  lane (104 commits since lock) — this row's own text asks to coordinate before touching it, which this
  finding is.
- No attempt to fix `jcon_recogn`/`jcon_genqueen` directly.
- No further chase of `cxprimes`/`level`/`scan2` — out of this row's named scope.

## Recommendation
Given even the maximally-minimal single-`suspend` case crashes (and changes shape under
`SCRIP_ICN_GENFRAME2=1` rather than resolving), this looks entangled with the in-flight `icon-n2` work
rather than cleanly separable "sixth shape" work a fresh seat can safely add a witness for right now.
Asked hq_P (`s4e_msg.sh ask icn-recogn-genqueen-minimal-repro-plus-fresh-measurement`) whether this
minimal case is already understood/mid-fix on their branch, or whether it's new information. Row left
`PARKED-AWAITING` a reply rather than attempting the frame-protocol fix unilaterally mid-flight.
