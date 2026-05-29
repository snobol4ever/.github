# HANDOFF — Prolog BB — PLR-K-7/8/9: number_string, atom_number, format, term_to_atom, term_string

**Author:** Claude Opus 4.8 · **Date:** 2026-05-29
**Goal:** `GOAL-PROLOG-BB.md`
**one4all HEAD at handoff:** `8be5f202`
**corpus HEAD at handoff:** `5354a66`
**.github HEAD at handoff:** (this commit)

---

## Session arc

Three PLR-K rungs landed, each closing a double-jump-stub gap where a builtin had a mode-2
oracle arm but missing or incomplete emitter arms, so mode-3 native (`--run`) and/or mode-4
emit (`--compile --target=x86`) produced `_` or empty output. **GATE-2 crosscheck 61 → 70
PASS (+9 this session); mode-4 corpus 55 → 67.** All other gates byte-identical throughout;
mode-2 (the correctness reference) never touched except for additive effect helpers.

Each rung verified the actual 3-mode state of its corpus rung BEFORE coding (not trusting the
watermark), built the effect helper as a faithful transliteration of the mode-2 oracle, added
the MEDIUM_BINARY (mode-3) and/or MEDIUM_TEXT (mode-4) arm, and re-ran the full gate suite.

---

## What landed (in order)

### PLR-K-7 — number_string/2 + atom_number/2 (one4all `fa30091f` → rebased `5a55ac7b`)

Both recognized in `lower_pl.c` and handled by the mode-2 oracle, but had **NO emitter arm at
all** (neither TEXT nor BINARY) → mode-3 native AND mode-4 emit both printed `_ _`.

- New effect helper `rt_pl_number_string_pair(num_first, k0,i0,s0, k1,i1,s1)` (`bb_exec.c`, after
  `rt_pl_atom_string_pair`). `num_first=1` for number_string (arg0=num arg1=text); `=0` for
  atom_number (arg0=text arg1=num). Number arg bound → render text and unify into text arg; text
  arg bound → parse (`strtol` int else `strtod` float) and unify the number. Decl in `bb_exec.h`.
- MEDIUM_BINARY arm (mode-3): 7 scalars — `num_first` prepended shifts the SysV layout vs the
  6-scalar atom_string arm: rdi=num_first esi=k0 rdx=i0 rcx=s0 r8d=k1 r9=i1, `[rsp+0]=s1`,
  `sub rsp,16`, `movabs` absolute pointers. MEDIUM_TEXT arm (mode-4): byte-twin via `@PLT`.

GATE-2 61 → 62 (+1, rung24_string_io_number_string); rung24 string_io 4/5 → 5/5. atom_number
verified 3-mode AGREE (no corpus rung). corpus `.s` regenerated (`e422738`).

### PLR-K-8 — format/1 + format/2 MEDIUM_BINARY arm (one4all `e0ce19ef` → rebased `123878af`)

`format` was MEDIUM_TEXT-only → mode-3 native emitted the asm strings as raw bytes → format
produced EMPTY output (all 5 rung19 printed nothing at rc 0). Ported both paths of the TEXT arm
to raw bytes (`bb_pl_builtin.cpp` only):
- Path A (scalar/absent args1): `rt_pl_format(arity,k0,i0,s0, k1,i1,s1)` — 7 scalars, s1 on the
  stack at `[rsp+0]`. format/1 lands here.
- Path B (compound args1, e.g. `[world]` / `[foo,bar,99]`): build args-list Term* via
  `emit_build_compound_term_bin` into r8, call `rt_pl_format_term(arity,k0,i0,s0, args*)`.

`sub rsp,16`; `movabs` absolute pointers; std bin-patch tail. Added extern decls for
`rt_pl_format`/`rt_pl_format_term` (the TEXT arm referenced them only by `@PLT` string).

GATE-2 62 → 67 (+5) — all 5 rung19 (format1_nl, format2_a/d/i/w) now 3-mode AGREE. Path B
verified with multi-element `[foo,bar,99]`→`foo-bar-99`. No corpus `.s` regen needed (mode-3
only; TEXT arm already existed and was unchanged).

### PLR-K-9 — term_to_atom/2 + term_string/2 + BB_ARITH TEXT-walker fix (one4all `0da0b083` → rebased `8be5f202`)

Both had NO emitter arm → mode-3 native + mode-4 emit printed `_`.

- New effect helper `rt_pl_term_to_atom_term(t0, k1,i1,s1)` (`bb_exec.c`) — forward-only,
  mirrors the oracle: render arg0's term via `pl_term_to_string` (operator-notation writer),
  intern the atom, unify into the text arg. The arm builds arg0's Term* via
  `emit_build_compound_term[_bin]` and passes the pointer (writeq/numbervars `_term` idiom).
  Decl in `bb_exec.h`. MEDIUM_BINARY + MEDIUM_TEXT arms.

- **ALIGNMENT FINDING (reusable):** `rt_pl_term_to_atom_term` → `pl_term_to_string` →
  `open_memstream` is SSE-alignment-sensitive and SIGSEGVs if rsp is not 16-aligned at the call.
  The numbervars/writeq `_term` arms use `sub rsp,8` (their helpers do no alignment-sensitive
  glibc work, so the off-by-8 was tolerated); this arm needs `sub rsp,16` (both BINARY + TEXT).
  Found via gdb backtrace into `open_memstream`. **Note for any future native helper calling
  glibc stdio / memstream / printf-family: use `sub rsp,16`, not `sub rsp,8`.**

- **BB_ARITH TEXT-WALKER FIX:** `emit_build_compound_term` (the MEDIUM_TEXT walker) had NO
  BB_ARITH branch → fell to the `unhandled kind` comment → an operator literal like `1+2`
  produced no term-build code (rax garbage) and rendered EMPTY in mode-4. The MEDIUM_BINARY twin
  already had the branch (PLR-K-4); added the matching branch to the TEXT walker (functor=sval,
  operands on α/β, arity 0→atom/1→f(a)/2→f(a,b)). Benefits any mode-4 arm feeding an operator
  term through the TEXT walker (functor/arg/=../write_canonical with operator literals).

GATE-2 67 → 70 (+3) — rung25 term_string/term_to_atom/term_to_atom_arith now all 3-mode AGREE.
mode-4 corpus 64 → 67 (+3). corpus `.s` regenerated (`5354a66`).

---

## Verified state at handoff (final gate run, all green)

| Gate | Result |
|---|---|
| FACT arm1 (templated-bytes-outside-templates) | 0 |
| FACT arm2 (bytes() outside bomb_bytes/bb_emit_asm_result) | 12 (baseline) |
| GATE-1 smoke | 5/5 |
| GATE-2 crosscheck (mode-3 native, 3-mode agree) | **70 PASS / 66 / 1 ORACLE_MISS** |
| GATE-3 rung suite (mode-2 interp) | 108/111 |
| GATE-4 mode-4 minimal | 4/4 |
| GATE-SWI plunit (mode-2) | 57/57 (100%) |
| mode-4 full corpus | 67/111 |
| siblings icon / raku / snobol4 | 5/5 / 5/5 / 13/13 |
| Build | green |

GATE-3 m2 3 FAILs are pre-existing (rung15 then_reassert, rung27 aggregate/bagof/setof,
rung30 dcg_pushback_rest). The lone GATE-2 ORACLE_MISS is the pre-existing `-e ` artifact in
`rung05_backtrack_backtrack.ref` (all 3 modes correctly print `a\nb\nc`).

---

## NEXT

The cheap mode-3/4 builtin-arm gaps in the GOAL `NEXT` pointer are now mostly closed
(number_string, atom_number, format, term_to_atom, term_string, char_type, numbervars, writeq,
write_canonical, print, type-test compound all 3-mode or mode-3-native). Remaining:

1. **findall/3** — the last and hardest. Its `nd->ival` carries a `bb_pl_findall_state_t*`, NOT
   an arity int, so it does NOT fit the uniform builtin-arm shape used by every rung above. Needs
   a dedicated mode-3/4 path: emit the goal sub-graph inline (collect solutions by driving the BB
   subgraph and snapshotting bindings) or route specially. This is its own protocol; budget a full
   rung for it. (rung11 is the corpus target.)

2. **retract/1 + retractall/1 + assertz/asserta** — the PL-RT-ASSERTZ mutable-clause-store
   boundary (see PLR-K-6 honest-abort note in the GOAL file). The native BB_CHOICE dispatcher
   bakes the clause count as a compile-time constant, so runtime clause mutation is invisible to
   the emitted enumerator. Needs a runtime-mutable clause store the native dispatcher consults —
   a multi-session substrate, not a template arm. abolish/1 (rung15) sits on the same boundary.

3. **PL-INDEX-L2-1** (optional, dispatch-speed only) — Level-2 hash bucketing for first-arg
   indexing. Byte-identical mode-2 output; worth doing only if a many-fact benchmark motivates it
   (assessed low priority by the prior Sonnet session). No heap-reclamation precondition (unlike
   the closed PL-TRAIL-COND).

Develop and verify against mode-2 (the correctness reference) throughout. Each new arm: verify
the actual 3-mode state of the target rung FIRST, transliterate the oracle into an effect helper,
add BINARY (mode-3) + TEXT (mode-4) arms, re-run the full gate suite, regenerate corpus `.s` if
mode-4 emit changed.

---

## Lessons for next session

1. **Verify the rung's real 3-mode state before coding.** Every rung this session had a
   different actual gap than the one-line watermark NEXT implied (rung24 was 4/5 not 0/5; format
   was empty-output not `_`; term_to_atom needed a TEXT-walker fix nobody had flagged). The gate
   run is the truth; the NEXT pointer is a hint.

2. **`open_memstream` / glibc stdio is alignment-sensitive.** A native helper that calls into
   glibc printf/stdio/memstream MUST be entered with rsp 16-aligned at the call. `sub rsp,8` is
   only safe for helpers that themselves do no SSE-touching glibc work. When a new `_term` helper
   segfaults inside libc, suspect alignment first; gdb backtrace into the libc frame confirms it.

3. **TEXT and BINARY compound-term walkers can drift.** `emit_build_compound_term` (TEXT) and
   `emit_build_compound_term_bin` (BINARY) are supposed to be twins, but the BB_ARITH branch was
   added only to the BINARY twin in PLR-K-4. When adding a mode-4 arm that feeds a new node kind
   through the TEXT walker, check the walker actually handles it (the `unhandled kind` comment is
   silent — it emits no code and leaves rax garbage rather than failing loudly).

4. **Concurrent pushes are frequent.** one4all moved under me on all three pushes (SNOBOL4 BREAK/
   POS, Icon IBB-10/11, Raku RK-NFA). `git pull --rebase` was always clean (orthogonal work), but
   the rebase REWRITES the commit hash — re-confirm the watermark hash matches origin AFTER the
   push, and if it changed, land a clean corrective commit rather than amending pushed history
   (amending + rebasing a pushed commit creates a conflict against the remote copy).
