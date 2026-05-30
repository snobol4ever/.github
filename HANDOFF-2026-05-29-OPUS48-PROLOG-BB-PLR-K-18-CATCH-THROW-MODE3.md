# HANDOFF 2026-05-29 — Opus 4.8 — PROLOG-BB: PLR-K-18 catch/3 + throw/1 mode-3 native

**Goal:** GOAL-PROLOG-BB.md — close the rung28 catch/throw gap in mode-3 native (`--run`).
catch/throw were mode-2 only (WAM-CP-10); mode-3 aborted at emit time.

## State at handoff

- one4all HEAD `9eed4fa1` (parent `a062f28b`), tree clean.
- .github HEAD: this handoff + GOAL-PROLOG-BB.md watermark update.
- corpus untouched (no `.ref`/`.s` changes — mode-3 now MATCHES the existing refs).

## What landed (one4all `9eed4fa1`)

Four files, all Prolog-specific:

- `src/lower/bb_exec.c` (+2 helpers after `rt_pl_findall`):
  - `rt_pl_catch(void *zc_ptr)` — transliterates the mode-2 `BB_PL_CATCH` executor:
    push Pl_CatchFrame, `setjmp`, run `goal_g` via `bb_exec_once`; on `longjmp` from
    throw restore `g_pl_env` (load-bearing — inner callee env is current at longjmp
    time), unwind trail to frame mark, unify Catcher with the exception, run `rec_g`;
    rethrow via `pl_throw_term` if Catcher does not match.
  - `rt_pl_throw(void *alpha_ptr)` — mirrors the mode-2 `BB_BUILTIN "throw"` arm:
    materialize ball from the α term subtree via `pl_node_to_term`, `pl_throw_term`
    longjmps (no return on match).
- `src/lower/bb_exec.h` — two decls.
- `src/emitter/BB_templates/bb_pl_catch.cpp` — MEDIUM_BINARY arm:
  `sub rsp,16` / `movabs rdi,zc_ptr` / `movabs rax,&rt_pl_catch; call rax` /
  `add rsp,16` / `test eax,eax` / `je ω | jmp γ | β: jmp ω`. (Was `bomb_bytes`.)
- `src/emitter/BB_templates/bb_pl_builtin.cpp` — throw MEDIUM_BINARY arm:
  `movabs rdi,&α` / `movabs rax,&rt_pl_throw; call rax` / `jmp ω | β: jmp ω`.
  (Was falling through the BB_BUILTIN default stub.)

## Root cause (the reusable finding)

A predicate body emitted as a **callee block** (`pl_emit_callee_block_body` →
`walk_bb_flat` → `FILL`) supplies its `.Lplpb%d_β` redo label via `g_emit.lbl_β_p`,
and the block's `<blbl>_redo:` site does `jmp .Lplpb%d_β`. The body's BINARY template
MUST define β (`bin.is_def=true` on the `_.lbl_β_p` entry) or the final program emit
closes with `bb_emit_end: unresolved forward reference label='.Lplpb%d_β'`.

Two arms omitted the β-define:
1. The BB_BUILTIN **default** BINARY stub (`return bytes("\xE9")+u32le(0)+bytes("\xE9")+u32le(0)`
   with bin left `{}`). throw had no specific arm → hit this.
2. The catch BINARY arm I first wrote used the findall-style `{ω,γ,ω}` bin with all
   `is_def=false` → never defined its β.

Both omissions are **invisible** when the node is NOT a callee-block entry (β is defined
by the surrounding INVOKE entry path, e.g. `.Lplent0_β`), and **fatal** when it is:
`foo :- throw(X)` (throw is foo's whole body) and `inner :- catch(...)` (catch is
inner's whole body). The working reference pattern is the `nl` arm's `{γ,β,γ}` with
`is_def={false,true,false}`.

Diagnosis path: `[CATCH-TMPL]` + `[THROW-ARM]` stderr traces (since removed) showed the
template firing twice — once for `main`'s catch (`.Lplent0_β`, resolved) and once for
`inner`'s catch (`.Lplpb1_β`, unresolved). Isolation minimised the corpus `rethrow.pl`
to: throw-in-sub-pred alone triggers it (ball type irrelevant); a catch whose own
catcher matches does NOT (no rethrow, body resolves); rethrow (inner catcher mismatch)
+ catch-as-callee-block-entry is the exact trigger.

## Alignment note

Both arms `sub rsp,16`. `rt_pl_catch` → `setjmp` → glibc, and `rt_pl_throw` →
`pl_node_to_term`/`pl_throw_term`, are SSE-alignment-sensitive (movaps spill faults on
8-mod-16 rsp). Same class as the PLR-K-10 findall `__vsnprintf_internal` SIGSEGV.

## Gates (stash/pop verified)

| Gate | Baseline (`a062f28b`) | After (`9eed4fa1`) | Δ |
|---|---|---|---|
| GATE-1 smoke | 5/5 | 5/5 | = |
| GATE-2 crosscheck | 98/38 | **103/33** | **+5** ✅ |
| GATE-3 mode-2 (--interp) | 108/111 | 108/111 | = |
| GATE-3 mode-3 (--run) | 94/111 | **99/111** | **+5** ✅ |
| GATE-4 mode-4 minimal | 4/4 | 4/4 | = |
| GATE-SWI plunit | 57/57 | 57/57 | = |
| FACT arm1 / arm2 | 0 / 12 | 0 / 12 | = |
| icon / raku / snobol4 / snocone | 5/5/13/5 | 5/5/13/5 | = |

The crosscheck ±5 was confirmed by `git stash` → rebuild → re-run (98) → `stash pop` →
rebuild → re-run (103): exactly the 5 rung28 cases moved FAIL→PASS, nothing else.

rung28 mode-3 individually: rethrow, throw_catch_compound, throw_catch_atom,
catch_atom_match, no_throw all PASS (each diffed against its `.ref`).

## NEXT

- Remaining mode-3 crosscheck gaps are the documented boundaries:
  rung14 retract (5) + rung15 abolish (4) = the **PL-RT-ASSERTZ** mutable-clause-store
  boundary (the BB_CHOICE dispatcher bakes clause count as a compile-time constant);
  rung27 succ_or_zero (1, corpus `.pl` gap); rung30 DCG (2, separate).
- **Mode-4 (compile) catch/throw** is still the WAM-CP-13 gap: `bb_pl_catch.cpp`
  MEDIUM_TEXT is an α/β→ω fail-through stub, and `bb_pl_builtin.cpp` has no throw
  MEDIUM_TEXT arm. A correct mode-4 catch needs the goal/recovery sub-graphs emitted as
  nested functions + an r12 catch-barrier (the BINARY arm here can't carry over: the
  zc_ptr / α pointers are compile-time-only, dead in the emitted separate process).

## Commit identity

```
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Verification

```
cd /home/claude/one4all && git log origin/main --oneline -1
# 9eed4fa1 PLR-K-18: catch/3 + throw/1 mode-3 native MEDIUM_BINARY arms
```
