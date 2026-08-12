# FINDING-2026-08-12j — HOME-RBX X-3: the residence gap is measured (36/122 vs 76/122), and DIFF — not crash — dominates

**Seat:** RBX · **Rung:** X-3 (inline bump-alloc / port promotion, opened this session per s34's
own recommendation to decouple it from X-2) · **Session:** Sonnet 5, s35 · **Zero code changed.**
Build order confirmed correct (`install_system_packages.sh` → `make scrip` → `make libscrip_rt`) before
any measurement, per the s33 cross-seat note about phantom SEGVs from stale builds.

## Own-HEAD baseline (control), corpus/SCRIP at this session's pulled HEAD

| instrument | m3 result | vs s33 recorded floor |
|---|---|---|
| probe/bb | 159 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10} | matches by set (+2 pass, other seats' landings) |
| probe/bb (m4, compile) | 157 pass · 2 xfail · 6 REGRESSION {D12,D13,H31,X01,**X05**,X10} | **X05** is new — not in m3's set, not previously named anywhere in this file. Filed, not chased (out of X-3 scope). |
| crosscheck/patterns | 76/122 (28 SIG11, 12 DIFF, 6 HANG) | identical by set |
| crosscheck/gc | 15/15 | identical |
| crosscheck/capture | 8/9 (1 DIFF = `061_capture_in_arbno`, pre-existing) | identical |

m4 liveness re-confirmed (`MODE=compile bash probe/bb/run_suite.sh X12` → PASS) before trusting any m4
number, per the staleness law.

## X-3's actual question: what does "port promotion" cost, concretely?

§ A of the contract already states REG-4b (the rbx bump frontier) is built and corpus-exercised, but
dormant on the default port (`ZC_PORT_FORTH`, port 6) — HEAP is port 7, reachable only via
`--zeta-port=heap` / `SCRIP_ZETA_PORT=7`. § A also predicts the shape of the gap: "the fc *consumers*
stay FORTH-gated… the block is allocated-but-unread… making the locals actually RESIDE in the block is
the X-3 slice-2 work, and it is the part that has never run." This session measured that gap instead of
assuming its size.

### Census — the blast radius named
```
grep -rn ZC_PORT_FORTH src/emitter/ src/templates/ src/runtime/   → 26 sites, 8 files
grep -rn ZC_PORT_HEAP  src/emitter/ src/templates/ src/runtime/   →  5 sites, 3 files
```
Files carrying a `ZC_PORT_FORTH` gate: `emit.cpp`, `emit.h`, `bb_match_begin.cpp`, `x86_asm.h`,
`bb_match_end.cpp`, `bb_match_capture.cpp`, `bb_call_proc_staged.cpp`, `zeta_alloc.c`. Representative
gated consumers, all keying `x86_port_mode() == ZC_PORT_FORTH`: `x86_fc_on`, `x86_fc_hit` (the granted-
window capture-cell read), `fc_alt_active`, `fc_seq_on`, the `op_subj_cell` FORTH-cell producer/consumer
registry, and the ARBNO K16 frameless-arm routing prelude in `emit.cpp`. None of these have a HEAP arm —
under HEAP mode today they silently fall through to whatever their `else` does (typically the legacy
rbp-relative path), which is exactly the mechanism that turns into wrong-but-not-crashing output below.
**~5:1 blast radius, not a flip of a default.**

### Empirical gap — SCRIP_ZETA_PORT=7 against the same three crosscheck sets, same binary, same corpus
(`x86_port_mode()` and the runtime's `rt_zeta_port_mode()` are the same reader — `emit.cpp:453` —
so the env var swaps port at both emit-time and run-time for m3 in one process; m4 self-selects via the
baked `rt_zeta_port_set_mode@PLT` call when the port was overridden, per `emit.cpp:1260/1470`.)

| set | FORTH (own-HEAD) | HEAP | delta |
|---|---|---|---|
| hello + assign (16 files, quick spot-check, not part of the table above) | 16/16 | **16/16** | none — the frontier arithmetic itself is correct |
| crosscheck/patterns | 76/122 (28 SIG11, 12 DIFF, 6 HANG) | **36/122** (23 SIG11, **48 DIFF**, 15 HANG) | **−40 programs**; DIFF nearly quadruples |
| crosscheck/gc | 15/15 | **13/15** (2 SIG11: `206_gc_pattern_capture`, `209_gc_big_strings`) | −2 |
| crosscheck/capture | 8/9 (1 pre-existing DIFF) | **6/9** (2 new SIG11: `060_capture_multiple`, `065_capture_then_arbno`, `066_capture_then_fenced_arbno` — three named, two SIG11 one already-DIFF) | −2 net (3 named regressions, 1 was already broken) |

**The failure-mode shift is the finding, not just the count.** Under FORTH the patterns failures are
mostly crash-class (28 SIG11 vs 12 DIFF). Under HEAP the dominant mode inverts to DIFF (48 of 122) — the
program runs to completion and prints something, just the wrong thing. This is exactly what "allocated-
but-unread" predicts: the frontier bump happens, the block exists, but a FORTH-gated consumer reads the
*old* (rbp-relative or FORTH-cell) address instead of the heap-resident one, so the data silently comes
from the wrong place rather than faulting. **A silent-wrong-answer class is worse to leave live than a
crash class** — it is the SPITBOL-semantics violation the whole HOME GATE is measuring against, and it
would corrupt output rather than announce itself.

### Named next experiment (MONITOR-FIRST, not a re-sweep)
`041_pat_span` and `042_pat_break` — pass clean under FORTH, SIG11 under HEAP, both in the same tiny
`crosscheck/patterns` numeric-tail cluster as `038`–`046` (all quick, all already isolated as
pass/fail pairs by this session's diff). These are the cheapest FORTH-vs-HEAP divergence pair on
record: same source, same oracle, one env var different. Next rung should point the 2-way sync-step
monitor at one of these (SPAN/BREAK against a HEAP-armed binary) rather than reading `x86_fc_hit`/
`fc_alt_active` cold — RULES' own law: convict the FIRST DIVERGENT trace event, don't guess from source.

## What this does NOT do
Doesn't touch codegen, doesn't add a HEAP arm anywhere, doesn't move the default port. Zero `.s`
regen triggered (no compiler bytes touched — build hash unchanged across this whole session).

## FILED OUTWARD
- **→ whoever owns probe/bb m4:** `X05` is a new m4-only regression name, not previously seen in the
  RBX cursor's recorded sets. Not chased here — flagging so it isn't silently absorbed into "the known
  five."
- **→ this seat, next rung:** the MONITOR-FIRST pair above (`041_pat_span` FORTH-vs-HEAP) is the
  concrete X-3 slice-2 entry point — cheaper and more decisive than reading `x86_fc_hit` cold.

**UNBLOCKS: RBX X-3 slice-2** (the monitor-pointed consumer fix); does not touch X-2 (still Lon/BOARD's
seating call, untouched this session).
