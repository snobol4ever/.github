# HANDOFF — PLG-9g (partial): Prolog mode-4 `writeq`/`write_canonical` + `atomic_list_concat` TEXT arms

**Author:** Claude Opus 4.8 · **Date:** 2026-06-01 · **SCRIP HEAD (pre-commit):** `86c265e` (PLG-9f)
**Goal:** GOAL-PROLOG-BB.md (PLG-9 mode-4 ladder)
**Directive (Lon):** "Your choice. Continue." — climb the mode-4 ladder; pick the most tractable EXCISED closures.

## What landed

**Four builtin functors crossed onto mode-4 native x86, un-EXCISING 7 rungs (GATE-3 m4 69→76, 0 FAIL).**
Each is the missing `@PLT` MEDIUM_TEXT twin of a builtin that already had a working MEDIUM_BINARY arm — the
gap was purely that a standalone `.s` (mode-4 compile-to-file) cannot splice the raw-byte BINARY arm, so the
rich gate (`pl_rich_node_emittable`) EXCISED these families with a loud-fall, not a miscompile.

| Functor(s) | Rungs un-EXCISED | BINARY arm mirrored | Runtime helper (@PLT) |
|---|---|---|---|
| `writeq/1`, `write_canonical/1` | rung22 ×4 | PLR-K-4 | `rt_pl_writeq_term_ptr` / `rt_pl_write_canonical_term_ptr` |
| `atomic_list_concat/2,3`, `concat_atom/2` | rung26 ×3 | PLR-K-14 | `rt_pl_atomic_list_concat_term` |

```prolog
:- initialization(main).
main :- writeq('hello world'), nl, writeq(foo), nl.        % rung22 -> 'hello world' / foo
main :- write_canonical(1+2), nl.                          % rung22 -> +(1,2)  (op form suppressed)
main :- atomic_list_concat([hello, beautiful, world], ' ', A), write(A), nl.  % rung26 -> hello beautiful world
```
All three modes agree (m2/m3 byte-identical 111/111; m4 now PASS).

## Mechanism (additive, Prolog-arm-only, FACT-clean: 0 bytes outside templates)

Both arms follow the proven PLG-9a/b TEXT idiom — **no value stack, no name-table round-trip**:
build the argument Term* with `emit_build_compound_term` (the TEXT post-order walker; reads atom args from
sealed `.rodata` via `[rip + .Sn]`), leave it in `rax`, then call the runtime helper `@PLT`. The result
unifies into the result-variable's slot, which lives in `g_resolve_env` — the **process-global per-activation
home** that the subsequent `write(A)` reads directly. This is the same binding-survival pattern PLG-9f
established (the consumer reads the producer's slot directly; the binding is not threaded through any stack).

- **writeq/write_canonical** (`bb_builtin.cpp`, MEDIUM_TEXT, after the `write`/`writeln`/`print` arm):
  `sub rsp,8` → `emit_build_compound_term(α)` → `mov rdi,rax` → `call rt_pl_{writeq,write_canonical}_term_ptr@PLT`
  → `add rsp,8` → γ; β→γ (write-family never fails). The two writers delegate to the mode-2 oracle's
  `pl_writeq` / `pl_write_canonical`, so quoting decisions are already ISO-correct.
- **atomic_list_concat/concat_atom** (`bb_builtin.cpp`, MEDIUM_TEXT, after the writeq arm):
  `sub rsp,16` → `emit_build_compound_term(a0-list)` → `mov rdi,rax`; then the 8-scalar SysV pack —
  `esi`=arity, `edx`=ksep, `rcx`=isep, `r8`=ssep(`lea [rip+.Sn]` or 0), `r9d`=kres, `[rsp+0]`=ires,
  `[rsp+8]`=sres(`lea`/0) → `call rt_pl_atomic_list_concat_term@PLT` → `add rsp,16` → `test eax` → je ω / jmp γ;
  β→ω. arity 2: result is `a1`, sep triple zeroed; arity 3: sep is `a1`, result is `a2`.
- **Gate** (`scrip.c` `pl_rich_node_emittable`): admits `writeq`/`write_canonical` (`nd->α != NULL`) and
  `atomic_list_concat`/`concat_atom` (`nd->α && (ival==2||ival==3)`). The two summary comments updated to move
  these out of the STAY-EXCISED list.

## Canonical grounding (per RULES.md — read Prolog sources for the constructs touched)

- gprolog `src/BipsPl/write_c.c`: `Pl_Writeq_1` sets `WRITE_NUMBER_VARS | WRITE_NAME_VARS | WRITE_QUOTED`;
  `Pl_Write_Canonical_1` sets `WRITE_IGNORE_OP | WRITE_QUOTED` (operator notation suppressed → `1+2` prints as
  the functional form `+(1,2)`, matching the rung26 `.expected`).
- gprolog `src/EnginePl/atom.c` (`Pl_Create_Atom` property scan): `needs_quote` true for non-identifier /
  non-graphic atoms with special chars — `'hello world'` quotes (space → needs_scan), `foo` does not
  (identifier), `'Hello'` quotes (leading uppercase ⇒ not a small-letter identifier). Matches rung22 `.expected`.

## Gates (all green, no regression)

| Gate | Before (86c265e) | After |
|---|---|---|
| GATE-1 smoke m2/m3/m4 | 5/5/5 | 5/5/5 |
| GATE-3 rung m2 | 111/111 | 111/111 (byte-identical) |
| GATE-3 rung m3 | 111/111 | 111/111 (byte-identical) |
| **GATE-3 rung m4** | 69 / 0 FAIL / 42 EXCISED | **76 / 0 FAIL / 35 EXCISED (+7)** |
| FACT grep / g_vstack | 0 / 0 | 0 / 0 |
| template purity | baseline (7 pre-existing) | unchanged; `bb_builtin.cpp` NOT flagged |
| prove_lower2 | PASS | PASS (no lower2 case touched) |
| Icon smoke (sibling) | 12/12/12 | 12/12/12 |
| SNOBOL4 smoke (sibling) | 12 PASS / 7 FAIL | 12 PASS / 7 FAIL (stash-and-compare proven identical) |

Sibling neutrality for SNOBOL4 (whose m3/m4 sit at the pre-existing `SBL-RING-REMOVE` abort) was proven by
**stash-and-compare**: at clean `86c265e` the SNOBOL4 smoke was `12 PASS / 7 FAIL`, byte-identical with my two
files applied. I touched no SNOBOL `bb_pat_*` arm and no Icon arm; the edits are inside the Prolog `cx.lang`
arms / Prolog functor branches only.

## Findings for the next engineer

- **The "BINARY-arm-exists-just-needs-`@PLT`-TEXT" closures are now EXHAUSTED.** writeq/write_canonical (PLR-K-4)
  and atomic_list_concat (PLR-K-14) were the last builtins with a proven BINARY arm but no TEXT twin. The 35
  remaining EXCISED rungs all need a real runtime substrate, not a mechanical arm-mirror:
  - **dynamic-DB** (retract/retractall/abolish/assertz/asserta — rung13-15): needs the `bb_*.cpp` emit-template
    for the mutable clause store. This is the **WAM-CP-13** deliverable (owns the PLG-9g dynamic-DB emit).
  - **catch/throw** (rung28): needs the catch-barrier through templates — also WAM-CP-13.
  - **findall** (rung11): the compile-time `bb_findall_state_t*` heap pointer is dead in the separate mode-4
    process (honest-abort stub today). Needs the PLG-10 deferred-frame-array analogue.
  - **numbervars** (rung20) + **copy_term** (rung26): the mode-4 **var-identity** gap — each reference to a term
    like `f(X,Y,X)` builds a FRESH Term* from IR, so intra-term var-sharing and numbervars' mutation do not
    survive to the consumer. Needs a per-activation term-identity substrate.
  - **float arith** (rung29): `rt_pl_arith`/`rt_pl_is` are integer-(`long`)-only. Needs the `rt_pl_arith_d` →
    `double` + `rt_pl_is_d` → `TERM_FLOAT` path plus float rendering in `emit_write_term` / the write helpers
    (today `IR_LIT_F` leaves a `# not yet rendered inline` marker). Self-contained, no CP work — likely the
    best next standalone rung. (NOTE: rung29 `float_conversion` — truncate/ceiling/floor/round — returns
    INTEGER results from float inputs, so it may fall out partly from a float-input-aware `rt_pl_arith` even
    before full float-result support; worth checking which of the 4 rung29 cases need true float results.)
- **`emit_build_compound_term` (TEXT) and `_bin` (BINARY) are byte-twins** and both reach `rt_pl_node_to_term` /
  `rt_pl_compound_build_n`. When adding any future builtin TEXT arm, mirror the BINARY arm's argument shape
  exactly (γ-chain vs α/β operand layout differs per lower convention — see lower_pl.c) and reuse the TEXT
  builder; do not hand-roll term construction.

## Files

`src/emitter/BB_templates/bb_builtin.cpp` (+66: two MEDIUM_TEXT arms), `src/driver/scrip.c` (+28/−9: gate admits
4 functors + summary-comment refresh) — SCRIP. `GOAL-PROLOG-BB.md` watermark (PLG-9g-partial completed item +
open-item rewrite + gate table) — .github.
