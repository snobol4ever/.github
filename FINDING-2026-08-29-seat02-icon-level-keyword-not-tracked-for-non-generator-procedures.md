# FINDING — `&level` is only maintained by the generator-role procedure prologue/epilogue (`bb_define_activate`); the standard role (`bb_define_sr`) never touches `rt_k_level`, so calling/returning from an ordinary (non-`suspend`) procedure never moves `&level`

**seat02 · 2026-08-29 · row `tests-consolidate-icon`, characterizing `rung36_jcon_level.icn`**

## The bug

`src/runtime/keywords.c:357` reads `&level` straight from the global `rt_k_level`. Three call sites
exist for maintaining that counter:

1. `src/runtime/rtx/rtx_icngen.s` — the generator-spine trio (`rt_gen_spine_resume_enter` ++,
   `rt_gen_spine_pass_γ`/`rt_gen_spine_pass_ω` --), wired only into the suspend/resume path
   (`bb_call_proc_staged.cpp`/`bb_call_value.cpp`).
2. `src/templates/bb/bb_define.cpp:100-107` and `:185-193` — inline `enter_env`/`leave_env` code that
   also increments on entry / decrements on exit, but this block lives **only inside
   `bb_define_activate()`** (line 54), the procedure-definition role used for generator-capable
   (`suspend`-containing) procedures.
3. Nothing else. `bb_define_sr()` (line 380, the **standard** role used for ordinary procedures) and
   `bb_define_bind()` (line 267) contain **zero** references to `rt_k_level` or `kw_fnclevel` —
   confirmed by grepping each function's own line range in isolation.

So a call into any procedure that does **not** contain `suspend` never touches `rt_k_level` at all,
in either direction. Icon's canonical semantics (cited in `rtx_icngen.s`'s own header,
`refs/icon-master/src/runtime/invoke.r:210`) increments `k_level` on **every** procedure invocation,
generator or not — SCRIP only implements the generator half.

## Evidence

Witness: `corpus/tests/icon/rung36_jcon_level.icn` (`#SRC: JCON`):

```icon
procedure main(); write(&level); foo(3); write(&level); every bar(3); write(&level); end
procedure foo(n); write(&level); if n ~= 0 then foo(n-1); write(&level); end
procedure bar(n); write(&level); suspend 1 to n do write(&level); write(&level); end
```

`.expected`: `1 2 3 4 5 5 4 3 2 1 2 2 2 2 2 1` (one value per line) — matches Icon's real semantics: each
`foo` call/return moves the level by one (2,3,4,5,5,4,3,2), each `bar` call moves it once to 2 and
stays there through every `suspend`/resume (generator activation isn't popped until it actually
returns).

`./scrip --run` actually prints: `1 1 1 1 1 1 1 1 1 1 2` then crashes (see below) — **every one of
`foo`'s 8 calls reads back the unchanged initial level**, because `foo` compiles through
`bb_define_sr`. `bar`'s first read correctly shows `2` because `bar` (containing `suspend`) compiles
through `bb_define_activate`, which does carry the +1/-1 pair.

Minimal repro isolating this from anything generator-related — no `suspend` anywhere:

```icon
procedure main(); write(&level); p(); write(&level); end
procedure p(); write(&level); end
```

Expected (Arizona semantics): `1 2 1`. SCRIP prints `1 1 1`.

## Corroborating measurement already on record

`RTX-CLAIMS.md:180`'s own falsification note for `rt_gen_spine_resume_enter` — breaking it
(`add 1000` instead of `inc`) moved the graded corpus board by exactly **one** program (`252 → 251`).
That is independent confirmation that `&level`'s correctness is exercised by essentially **one**
corpus program total (this witness), which is exactly why the standard-role gap above has never
tripped a gate.

## A second, unrelated defect surfaced while isolating this one

While minimizing `bar`'s crash (the `** Error 1 ... Illegal data type` after the eleventh line above),
found it reproduces with **no `&level` involved at all**:

- `suspend 1 to n` (generator expression, no `do`, no `every`, called as `write(bar(3))` or via
  `every bar(3)`) → `Illegal data type`, deterministic.
- `suspend n` (plain scalar, no `do`) consumed as a value — `write(bar(3))` where `bar(n)` is just
  `suspend n` — does not error, but **prints raw garbage bytes instead of `3`**.
- `suspend n do write("side")` consumed the same way — same garbage, and the do-clause's own
  `"side"` output never appears.

This matches, rather than adds to, the already-open rank-0 row `icon-n2-generator-activation-frames`
(owner `ceo`) — specifically its own tracked item **"(2) close the value path (`emit.cpp:3168` →
`bb_call_proc_staged.cpp:720` carries the four-word record but not the result descriptor)"**. Not
filed as a separate FINDING; mailed `ceo` directly (`icon-n2-suspend-value-path-corroboration`) with
these three minimal, `&level`-free repros as additional witnesses, same precedent as seat08's
`cxprimes`/`scan2` corroboration in this same KEEP.md.

## Disposition this session

Not fixed — out of this row's lane (`tests-consolidate-icon` characterizes, it does not fix runtime
bugs; same discipline already applied here to `proto`, `scan1`, `kwds`/`subjpos`, etc.).
`rung36_jcon_level.icn` stays loose, not entered in `KEEP.md` as a permanent keeper (it is a bug, not
a design exclusion) — `tests/icon/KEEP.md`'s `level` bullet updated with this characterization,
written as a bare stem (no `.icn` suffix) so the suite-conversion gate's basename-substring "declared"
check does not silently mark it as settled (per `FINDING-2026-08-29-seat14-keepmd-gate-substring-
false-positive.md`'s finding on exactly this gate, and this task's own established convention for the
other 14 open rung36 files). Mailed `hq_C` (`icon-level-keyword-standard-role-gap`) — this is a
narrow, precisely-located codegen gap independent of the value-path defect above.

## Not attempted

The fix itself: mirroring `bb_define_activate`'s `enter_env`/`leave_env` `rt_k_level` +1/-1 pair into
`bb_define_sr` (and confirming whether `bb_define_bind` needs the same treatment for co-expressions).
Two open questions worth settling before landing it, not chased here: (1) whether `kw_fnclevel` (set
alongside `rt_k_level` in the activate role, read nowhere `&level` itself reads) needs the same
mirroring or is dead weight; (2) whether the standard role's fast-path exit(s) — `bb_define_sr` was
not read in full, only grepped for the two symbol names — have more than one return edge that would
each need the decrement, the way `bb_define_activate`'s `leave_env` fast-path (`:166-193`) sits beside
a slower `L(7)` arm that was not traced.
