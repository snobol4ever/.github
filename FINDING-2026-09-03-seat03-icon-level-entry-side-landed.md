# FINDING — icon &level: ENTRY-SIDE landed (SCRIP pending commit), closing the two-part cure
# started at `41730a7f`. Root cause of the "off by a constant +1" first attempt: rt_k_level's own
# static initializer already counts the root graph (Icon main) as level 1, and the new entry-side
# code ran for main's own frame too, double-counting it. Fixed by teaching lower_icon.c to flag
# main's graph as root_graph (mirroring lower_prolog.c's only other use of that field) and gating
# the new entry-side increment on it, exactly as the codebase already gates PL's own root-graph
# special cases in xa_flat.cpp.

**seat03 · 2026-09-03 · row `icon-master-six-run-graded-reds-cured`**

## 0. Context

Assigned row's task file names `procedure_every_alt_replace_4` and `procedure_alt_fail_replace_1`
as two of "the six run-graded reds" on the Icon master board, both failing on their `&level` output
line. Both trace to the same standing gap: `FINDING-2026-08-29-seat02-icon-level-keyword-not-tracked-
for-non-generator-procedures.md` through `FINDING-2026-08-30-seat01-icon-level-half-cure-...md` had
already landed the EXIT-side (decrement) half of this cure at SCRIP `41730a7f`, explicitly leaving the
ENTRY-side (increment) unimplemented pending raw-byte BINARY-arm verification. This session lands that
second half.

## 1. Where the entry-side lives, and why it needed two files, not one

The `bb_define.cpp`-side enter_env/leave_env pair (`bb_define_activate`, generator-role procedures)
was always complete. The gap is a SEPARATE prologue: ordinary (non-suspend) Icon procedures compile
through `emit.cpp`'s `flat_lcl_proc` branch (`codegen_flat_chain_body`, ~line 2927), which builds its
`sub rsp,N` / `call rt_icn_zframe_args_install@PLT` prologue via raw TEXT-snprintf and raw-byte BINARY
writers (`ef_b1`/`ef_b2`/`bb_emit_u64`), NOT the `x86(...)` DSL — exactly the reason the prior FINDING
declined to land it by hand. This session's addition does not touch that raw-byte block at all: it
appends a SEPARATE, pure-`x86()`-DSL statement immediately after it (still inside the same
`codegen_flat_chain_body` function, still gated identically), so BOTH media stay byte-consistent by
construction — no `as`-verified raw bytes needed, sidestepping the prior blocker entirely rather than
resolving it by hand-encoding.

```cpp
if (_iws && _use_zframe_install && !(g_emit_cfg && g_emit_cfg->root_graph)) {
    extern int * const rt_k_level_p;
    extern int64_t kw_fnclevel;
    bb_emit_x86(x86("comment", "...")
             + x86("mov", "rax", "[rip@got + __]", &rt_k_level_p, "rt_k_level_p")
             + x86("mov", "rax", RDQ("rax", 0))
             + x86("add", RDD("rax", 0), (long)1)
             + x86("mov", "ecx", RDD("rax", 0))
             + x86("movsxd", "rcx", "ecx")
             + x86("sub", "rcx", (long)1)
             + x86("mov", "rax", "[rip@got + __]", &kw_fnclevel, "kw_fnclevel")
             + x86("mov", RDQ("rax", 0), "rcx"));
}
```
The instruction sequence is `bb_define_activate`'s own `enter_env` (`bb_define.cpp:94-101`) copied
verbatim — same registers, same formula (`kw_fnclevel := new_level - 1`) — placed after the
`rt_icn_zframe_args_install` call so it never disturbs the rdi/esi/edx arg-marshaling above it; rax/rcx
are dead at that point (the body proper begins at `lbl_α_body`, which reads the freshly-carved frame,
not these registers).

## 2. The regression the FIRST attempt produced, and the actual root cause

Built with only the `_iws && _use_zframe_install` gate (mirroring the already-landed exit side's own
condition, minus root_graph). Minimal repro (seat02's own, from the original FINDING):
```icon
procedure main(); write(&level); p(); write(&level); end
procedure p(); write(&level); end
```
Expected `1 2 1`. **Got `2 3 2` — every value shifted by a constant +1, both m3 and m4.** Not a crash,
not a partial fix: a clean, deterministic, wrong-by-one-constant answer, which is its own tell (a
genuine per-call miscount would not stay a *constant* offset across a call and a return).

`rt_k_level`'s own static initializer (`rt.c:392`, `int rt_k_level = 1`) already counts Icon `main`'s
own implicit level — every OTHER caller of `rt_k_level++`/`--` in `rt.c` (the C-side runtime helper
call paths: apply, eval, co-expression activation, etc.) brackets a NESTED call, never `main`'s own
entry. `main()` itself never received a matching increment anywhere before this session — its "level
1" was baked into the initializer. Since `main` is an ordinary `icn_cells_graph` + `flat_lcl_proc`
procedure exactly like any other Icon procedure written by a user, the new entry-side code ran on
`main`'s own prologue too, incrementing `main`'s already-correct level 1 to 2 before its own first
`write(&level)` executed. The exit-side decrement, already landed and unguarded, was firing on main's
own return all along, invisibly — nothing reads `&level` after `main` returns, so the missing symmetry
was never observable until this session's own entry-side half made it observable from the other end.

## 3. The fix, and why `root_graph` rather than a name check

`g_emit_cfg->root_graph` (`IR.h:239`) exists in the codebase already, but before this session it had
exactly ONE setter: `lower_prolog.c:690`, `top->root_graph = 1` for Prolog's own synthetic top-level
goal graph — grepped and confirmed (`grep -rn "root_graph\s*=" src/`), so for every Icon graph including
`main` it read 0 always, and the first attempt's guard (`!root_graph`) was silently a no-op. Rather
than detect "is this main" by string-comparing the graph's own name at the EMIT site (which would
either violate NO-LANGUAGE-IDENTITY-PAST-LOWER if done language-blind-incorrectly, or need an
Icon-specific carve-out in shared cross-language code — this `flat_lcl_proc` prologue is confirmed
shared with Snocone per the prior FINDING), the fix teaches Icon's OWN lowerer to set the SAME
language-blind flag Prolog already established, at LOWER time where language identity is legitimately
still known:

`lower_icon.c`, `lower_icon_proc()`'s main return path:
```c
if (pd->v.sval && !strcmp(pd->v.sval, "main")) g->root_graph = 1;
```
`emit.cpp`'s existing `!(g_emit_cfg && g_emit_cfg->root_graph)` guard then needed no further change —
it now correctly reads true only for the graph the driver actually enters, cross-language, matching
the SAME idiom the PL epilogue in `xa_flat.cpp:424` already reads for its own analogous purpose
(`_plretain = !(... root_graph)`, "THE ROOT GRAPH NEVER RETAINS — it is entered from the driver").

## 4. Verified, both media, both the minimal and the full generator-inclusive witness

Minimal repro, m3 AND m4: `1 2 1` (was `2 3 2` pre-fix, `1 1 1` before ANY of this session's or the
prior session's work). Fuller witness (seat02's own, exercising the ALREADY-landed generator/suspend
path through `bar()` in the same program, to confirm no interaction with `bb_define_activate`'s
independent enter/leave pair):
```
procedure main(); write(&level); foo(3); write(&level); every bar(3); write(&level); end
procedure foo(n); write(&level); if n ~= 0 then foo(n-1); write(&level); end
procedure bar(n); write(&level); suspend 1 to n do write(&level); write(&level); end
```
m3: `1 2 3 4 5 5 4 3 2 1 2 2 2 2 2 1` — **byte-identical to Arizona's documented semantics**, matching
the ORIGINAL FINDING's own `.expected` line exactly. Both task witnesses now match their `.ref`
exactly on their `&level` lines: `procedure_alt_fail_replace_1` is a full byte-identical match;
`procedure_every_alt_replace_4` matches on `&level` and now differs ONLY on an unrelated,
pre-existing `&progname` line — see the companion FINDING on the census/instrument artifacts for why
that line is not a compiler defect and not closable by any code change.

## 5. Deliberately NOT done: the exit-side's own symmetric root_graph guard

The already-landed exit-side decrement (`xa_flat_zframe_epilogue_{γ,ω}_str()`) still fires
unconditionally on `main`'s own return, including for `main` — asymmetric with the new entry-side
guard. Left alone deliberately: (a) nothing reads `&level` after `main` returns in normal execution,
so this is not an observable defect against any known witness; (b) that exact code already regressed
once from an unrelated register-clobber bug (the `41730a7f` FINDING's own section 1), so it is not
reopened without a witness that actually needs the change — matching this project's own
TWO-PART-PROOF law (derive a fix from a stated cause, and only when something needs it).

## 6. Witness minted

`corpus/tests/icon/icon_level_keyword.icn` / `.ref` — the fuller repro above, oracle-independent
(verified by direct semantic derivation matching Arizona's own documented `&level` behavior, cited in
`rtx_icngen.s`'s own header per the original FINDING).

## 7. State

SCRIP tree dirty with this change plus the `*&subject` fix (companion FINDING); build verified on a
non-pristine incremental rebuild before this write-up, full `make pristine` + STRICT watermark +
SNOBOL4 control arm run separately before push (see task LEDGER for the numbers).
