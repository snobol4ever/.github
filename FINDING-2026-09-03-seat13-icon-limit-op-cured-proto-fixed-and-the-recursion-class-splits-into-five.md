# FINDING 2026-09-03 seat13: FLEET-16's three assigned Arizona classes — one cured (proto fixed, evalx's
residual re-scoped), one censused into a five-way split with a live safety regression flagged, one
censused into four independent SIGSEGV causes with follow-up rows minted for each

**Rows:** `icon-arizona-class-generator-forward-reference-reservation` (kept RUNNING, blocked as designed),
`icon-arizona-class-unresolved-forward-reference-emit` (CURED), `icon-arizona-class-silent-segv-no-diagnostic`
(census complete, split into 4 rows). Dispatched FLEET-16, ceo, 2026-09-03 ~16:15 CDT. **Ask target:** hq_P.

**Tree:** SCRIP `3a37313a0` · corpus `39f1c505c` · .github `7eb62e4c`, RT_OPT=-O0, `make` incremental (per
Lon's 2026-09-03 ~15:58 pristine-loosening ruling — `make pristine` reserved for ceo audits/release points/
stale-binary refusals; this session's verdict runs on an incremental rebuild, per that ruling).

## 1. `icon-arizona-class-unresolved-forward-reference-emit` — CURED

Minimal repro bisected from `proto.icn` (44 statements in one procedure → 1): a bare `x \ i;` — Icon's `\`
LIMIT operator applied to a **non-generator** operand (a plain variable) — aborts `bb_emit_end: 1
unresolved forward reference(s)` identically to the full witness. Root cause: `\` does not require its
operand to be a real generator, but every Byrd box emits all four ports unconditionally regardless of
runtime reachability, and `IR_LIMIT`'s beta port (`bb_limit.cpp`, `x86_jmp_tgt(X86T_TGT0)`) unconditionally
jumps to whatever `emit.cpp`'s chain-walk found in `g_limit_gen_beta` — the generator operand's own
resume-beta label — without checking whether that operand kind ever actually *places* such a label.
A plain `IR_VAR` doesn't (nothing ever resumes into a bare variable), so the label is referenced but never
defined. The identical hazard for `IR_SUSPEND`'s do-body, three lines above in the same function, is
already correctly guarded (`ir_is_generator_kind(...) || IR_CALL || IR_CALL_PROC_STAGED`); `IR_LIMIT` had
simply never been given the same guard. Fix: one line, `src/emitter/emit.cpp` (chain-walk driver, ~line
3192), mirroring the SUSPEND guard exactly — verified SCRIP `3a37313a0`, pushed.

**Verified:** minimal repros correct; `proto.icn` byte-identical to `.std` (was empty); Arizona suite board
m3/m4 `44/45 → 45/44` (both modes, +1 PASS); STRICT rung suite **unchanged** `PASS=266 FAIL=4 BADEXIT=1
XFAIL=26 XPASS=1 TOTAL=298` all three modes (this session's own re-measurement — the dispatch message's
cited `264/6/1/27` is stale, superseded by `0376cf07`'s `&level` cure before this session started); Icon
smoke `14/14` both modes; `IR_LIMIT` confirmed Icon-exclusive (`grep` across `src/lower/`, `src/parsers/`
— sole producer `lower_icon.c`), zero cross-language risk. `git diff --stat`: exactly
`src/emitter/emit.cpp | 2 +-`.

`evalx.icn` no longer hits this class's abort at all — confirming the cure, not merely masking it — but
now fails later, at `FATAL emit_drive: IR op=121 has no template in the universal driver` (`IR_SWAP`,
Icon's general `x :=: y` on non-trivial lvalues; the plain-variable fast path `IR_SWAP_VAR` *is*
implemented). Real, separate, non-trivial feature gap — minted as
`icon-swap-op-general-lvalue-no-emitter-template` (rank 2) rather than folded in or rushed. This row's own
DONE-WHEN is re-cut to certify what its name promises (the unresolved-forward-reference class, gone on
both witnesses) rather than full `.std` match on `evalx`, which was never this class's fact once peeled
back one layer.

## 2. `icon-arizona-class-generator-forward-reference-reservation` — NOT cured, correctly (blocked on its
own named prerequisite), but the 5 witnesses are now classified and one combination is flagged DANGEROUS

Per this row's own GOAL text it cannot close before `[[icon-n2-recursive-generator-per-activation-storage]]`
lands, and that design row's own LIVE CURSOR history (GOAL-ICON-100.md) last moved 2026-08-29 — still open.
What this session adds is a real census, using gdb plus the codebase's own existing (default-OFF)
`SCRIP_ICN_N2_SELFREC` diagnostic flag as an experimental probe (not landed, not proposed as a fix):

| Witness | Recursion shape | With flag OFF (today's default) | With flag ON |
|---|---|---|---|
| `btrees` | direct self (`walk`, `leaves`) | `rt_bomb()` abort, rc=134 | **rc=0, byte-identical to `.std`** |
| `collate` | direct self (`proc_perm`) | `rt_bomb()` abort, rc=134 | rc=0 but WRONG (cset byte-order bug, unrelated 2nd defect) |
| `recogn` | mutual, 2-cycle (`s`↔`t`) | `rt_bomb()` abort, rc=134 | unchanged — flag's cycle check only catches immediate self-calls |
| `genqueen` | mutual, 2-cycle (`solvequeen`↔`placequeen`) | `rt_bomb()` abort, rc=134 (clean, gdb-confirmed) | **⛔ raw SIGSEGV, rc=139** |
| `pdco` | `create`/co-expression (`Call`/`Allpar`/`Extract`) | raw SIGSEGV, rc=139 (never reaches the BOMB guard at all) | unchanged |

The `genqueen` row is the one worth a banner: **enabling the existing self-recursion flag turns a safe,
loud, diagnosable refusal into an unsafe crash**, on a recursion shape (mutual, not self) the flag was
never built to help — its own `i == nvisited-1` cycle check should mean genqueen's specific host is
refused identically either way, so something ELSE in the program's memory layout shifts when the flag
flips. Not root-caused further this session; flagged rather than quietly worked around, because the
alternative reading ("the flag looks free to flip since it doesn't seem to change genqueen") is
demonstrably false and would be a live safety regression if anyone shipped it on that reading. `pdco` is
flagged as possibly not belonging to this class's mechanism at all: `create`/co-expression activation is a
structurally separate call path from `bb_call_proc_staged.cpp`'s generator-call BOMB check, with no
equivalent guard — QA question routed to hq_P.

## 3. `icon-arizona-class-silent-segv-no-diagnostic` — census complete, confirmed NOT one root cause, split
into 4 rows

gdb `run`+`bt` (ASM-DIFF-FIRST step 3 — these are unconditional crashes, no breakpoint/hit-count needed)
on all 4 witnesses, plus one bisection (`others`, which turned out to hide two independent crashes):

- **`gc2`** — SIGSEGV inside `snprintf`, `rt_fire_buildplan_tweak` (`by_name_dispatch.c:618`, formatting
  `"%s__TWEAK"`) ← `dat_construct` (`driver_data.c:374`) ← a `"nonterm"` constructor dispatch. →
  `icon-arizona-segv-buildplan-tweak-nonterm-gc2`.
- **`iobig`** — SIGSEGV inside `kw_cset_reg`←`kw_cset_prime`←`rt_icn_cset_register` (`keywords.c:59/72/82`,
  registering `&lcase`), backtrace showing thread/semaphore frames (`__new_sem_wait_slow64`, a function
  literally named `β`) interleaved with what should be single-threaded cset priming — untested hypothesis
  that this interacts with co-expressions moving onto real pthread stacks this week. →
  `icon-arizona-segv-cset-register-coexpr-iobig`.
- **`tracer`** — SIGSEGV *inside* `snprintf(ibuf, 32, "%lld", arr.i)` itself at `pattern_match.c:238`
  (`subscript_get`'s integer→string coercion for subscripting, e.g. `n[1]`) ← `c_rt_subscript_var`
  (`:1282`). A 32-byte local buffer faulting on `%lld` is not a plausible logic bug in this function —
  working hypothesis is a stack-alignment/corruption issue at the JIT-compiled caller's ABI boundary,
  not this callee. → `icon-arizona-segv-int-subscript-snprintf-tracer-others`.
- **`others`** — bisected (`spellw`/`sieve`/`wordcnt` → individual `spellw(n)` arguments) to **two
  independent crashes in one file**: (a) `spellw(n)` for small `n` (1,2,5,10 reproduce; 13,20 do not)
  SIGSEGVs in raw `__strlen_evex` with `rdi=0x1` — an integer's raw bits reaching `strlen` as a `char*` —
  traced to `spell()`'s `find(n)` call with `n` still a plain, uncoerced integer. → minted separately as
  `icon-arizona-segv-find-uncoerced-integer-arg-others`. (b) `spellw(25)` (the `n<=99` branch, via `n[1]`)
  hits the identical `subscript_get`/`pattern_match.c:238` site as `tracer` — folded into that same row
  above rather than re-minted, since it may share the root cause (not proven, both call sites could
  independently corrupt the stack in different ways and coincidentally land in the same callee).

Net: at least 3, arguably 4, unrelated defects behind 4 identical-looking SIGSEGVs — exactly the "signal
reachable by two causes" shape RULES.md warns about, now with names and gdb evidence instead of a shared
census bucket. None root-caused to a fix yet; each new row carries its own witness, backtrace and working
hypothesis so the next picker-up starts past the census step (INHERITED-CLAIM LAW still applies — re-run
the repro fresh before trusting any of this).

## Everything landing in this push
SCRIP: one-line `emit.cpp` fix (§1). corpus: unchanged (no corpus edits this session). .github: this
FINDING, the three original task batons rewritten in place (LEDGER/NEXT/QA per baton-one-next-block-gate),
5 new task files minted (`icon-swap-op-general-lvalue-no-emitter-template`, and the four
`icon-arizona-segv-*` rows), `QUEUE.tsv` rows for same (via `s4e_msg.sh mint`), `SCORE.md`'s Icon rows for
`test_icon_arizona_suite.sh` and `test_icon_rung_suite.sh` rewritten in place with this tree per Lon's
2026-09-03 leader-board ruling.

## QA open to hq_P (this seat's ask target)
1. Should `pdco` move out of `icon-arizona-class-generator-forward-reference-reservation` into its own row
   (co-expression activation has no GENHOST-equivalent guard at all)?
2. Is extending `icn_gen_host_reserve_walk`'s cycle detector from "immediate self-call only" to "any
   revisit, reserve for the whole cycle" the intended shape for mutual recursion, or does the N-2 design
   already plan something else for N-cycles?
3. The `genqueen` SELFREC-flag regression (safe abort → raw SIGSEGV) — worth its own investigation before
   the next session that touches `SCRIP_ICN_N2_SELFREC` or the N-2 design row treats the flag as
   low-risk/free to experiment with.

Not blocking — this seat proceeds to its next assigned/picked row either way, per "finish every part that
doesn't depend on the answer first."
