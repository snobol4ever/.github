# FINDING — SIX OPEN SNOBOL4-LANE BUGS, PRECISELY DIAGNOSED, NOT CURED (hq_snobol4, 2026-09-23)

Written before session end so this diagnostic work does not die with the seat (RULES.md: "an unwritten
measurement dies with the seat"). Landed fixes from tonight (heap_kb declarations, `ASM_driver`'s GC-root,
`T<>` subscript, `test_snoflake_suite.sh` ordering, SETEXIT-over-EVAL priority) are already committed and
pushed and are not repeated here — this finding is the residue: six real, reproduced, unfixed bugs, each with
enough evidence that the next seat starts from a witness, not from zero.

Tree at time of writing: SCRIP `a22f9c6ed`, corpus `00de9e950`.

## 1. ARBNO-in-alternation backtracking search terminates one level too early (SNOBOL4 master)

Witnesses: `arbno_span_any_branch_2`, `arbno_span_break_replace_branch_2` (tests/snobol4/ALL.csv); also
explains `ATN`'s FAIL in packages/snobol4/aisnobol (confirmed same shape: `ARBNO` nested inside a multi-arm
`|`).

```
        $'blank'        =  SPAN(' ')
        jarray         =  '[' ( *jelement ARBNO(',' *jelement) | $'blank' ) ']'
        jelement       =  ANY('0123456789')
        json           =  POS(0) jarray RPOS(0)
        src = '[1,2]'
        src json  :F(BAD)
        OUTPUT = 'MATCH'  :(END)
BAD     OUTPUT = 'FAIL'
END
```
Expected `MATCH`, actual `FAIL`. `src='[1]'` matches.

**Mechanism (confirmed via gdb):** pattern *definitions* compile through the runtime first-class-pattern JIT
path (`dtp_fn_of` → `dtp_rcp_tree` → `bb_compile_pat_tree_sz`, src/runtime/pattern_match.c). `dtp_rcp_tree`'s
`TT_ARBNO` case rewrites `ARBNO(X)` into a self-recursive alternation `('' | SEQ(X, DEFER(*ARB$N)))`. This is
why the pattern ends up with TWO simultaneous frame-resident `IR_MATCH_ALTERNATE` nodes (the user's outer `|`
plus this rewrite). For input `[1,2]` the backtrack search tries cursor=1 (fails on `,`), cursor=2 (fails on
`2`), then gives up — cursor=3, which finds `]` and would succeed, is never tried.

**Ruled out, with evidence** (do not re-walk these): frame-slot/layout allocation math in emit.cpp
(`sn4_blob_choice_scan`, `choice_frame_candidate`, `choice_frame_slot`, `frame_slot_scan`, `blob_layout_slot`,
`blob_frame_bytes`) — proven correct even for two simultaneous alternates via a byte-identical-layout,
opposite-outcome minimal pair; `op_alt_cell` in bb_match_alternate.cpp — dead code whenever the per-node
offset is truthy; `rt_defer_merge_on`/`rt_defer_probe_run` — no-ops for `*`-prefixed names; register
clobbering in bb_match_lit.cpp — only touches eax/edx/ecx/rcx; `sno_seq_nary`'s σ/φ port-chaining
(lower_snobol4.c ~1531-1548) — instrumented, the catch-all fallback never fires in either the passing or
failing case.

**A real, separate bug was found and discarded while chasing this** — see §2 below, it is not this bug but is
entangled with it in the same file.

Next step, not yet tried: hardware watchpoint on `$rsp` (not a register-value watch) armed right before the
failing recursive `DEFER(*ARB$0)` call in a `--compile` mode-4 build (stable addresses), single-stepping the
full failing retry sequence to see definitively whether a push is left unmatched, or whether the "next
alternative" pointer read from the `[rbp-0x38]`-style retry-jump-table slot is simply wrong.

## 2. Unrooted compile-time string baked into JIT code (real bug, fix causes a regression, NOT landed)

Found while investigating §1. `dtp_rcp_tree`/`rcp_of` (src/runtime/pattern_match.c, lines ~65 and ~97)
allocate the `ARB$N`/`OPQ$N` self-reference name strings via `rt_heap_strdup_c` (GC heap) into an ephemeral
compiler-only AST node, then bake the raw address into JIT-compiled machine code. Nothing roots it afterward;
a collection between compile and use can reclaim it, and DEFER then silently resolves to garbage/empty.

**Confirmed real** via direct A/B: before the fix, `ARB$0`'s self-reference read back empty (`fn=NULL`);
after switching both allocations to `ct_strdup` (the established compile-time-arena allocator, already used
pervasively across the codebase for exactly this purpose — grep confirms), it correctly reads `"ARB$0"` and
resolves the right function pointer.

**Do not land this fix as-is.** Applying it alone flips master-board xfail entry `user_function_arbno_rpos_1`
from a terminating wrong-answer (already red, harmless) into an infinite HANG — confirmed via
stash/rebuild/rebuild-back A/B to prove causation. Root cause of the regression not found: a second DEFER call
site (site index 4 in `rt_defer_probe_run` order) also reads empty with `{fn=NULL, aux=3}` (a "simple literal
value, zero-width match" fast-path return, not the failure sentinel `aux=-2`) — unknown whether this is a
second instance of the same unrooted-string bug (e.g. a third `rt_heap_strdup_c` site in pattern_match.c not
yet found, or a lifetime/reuse issue in `ct_arena`'s compile-time arena between JIT compilations) or an
unrelated, intentionally-empty match. **This must be resolved before the `ct_strdup` fix can land safely.**

## 3. ARC_driver — stack-smash in a hand-written asm calling-convention trampoline

`corpus/packages/snobol4/gimpel/ARC_driver.sno`, mode-3: several correct outputs print (arc-trig values,
numerically right), then `*** stack smashing detected ***`, rc=134. gdb: the canary trips inside
`core_apply_runtime_proc` (core.c:3820-3827) when calling `ASIN` — but that function's own bounds
(`g_call_args[k]`, `k<64`) are fine. The real call path for a `dyn_scope` "tiny" procedure like `ASIN` goes
through `rt_call_proc_descr()` → `rt_tiny_record_enter()`, hand-assembled x86-64 in src/runtime/rt/rt.c
(~828-929) computing a dynamically-sized stack frame (`~24*nargs+47` bytes, 16-aligned) to marshal arguments
and a two-continuation (γ/ω) record. Several correct calls succeed before the canary trips, suggesting
cumulative drift across repeated calls rather than a single-call arithmetic error. Hand-checked the
`nargs=1` frame-size arithmetic — no obvious off-by-one found by inspection.

Confirmed NOT related to the SETEXIT/EVAL fix landed tonight (identical crash before/after that fix). Possibly
related to a `math_exp.sbl` crash in spitbol_x64_tests (see §6) — both are calling-convention/stack-frame
trampolines in the same file family, unconfirmed.

Next step: a dedicated watchpoint-based gdb session tracking live register/stack state across the repeated
`rt_tiny_record_enter` calls, not a static read — the drift is cumulative, so a single-call trace won't show
it.

## 4. REDEFINE_driver — OPSYN semantics defect (cto's reduction, refutes the original hypothesis)

`corpus/packages/snobol4/gimpel/REDEFINE_driver.sno`: we print `new[]` / empty where oracle prints
`new[original(x)]` / `original(x)`.

**cto's measured 8-line reduction** (sbl prints `new[orig(x)]` then `orig(y)`; SCRIP hits ERROR 246 stack
overflow):
```
DEFINE('F(S)')                    :(E1)
F       F = 'orig(' S ')'         :(RETURN)
F2      F = 'new[' G(S) ']'       :(RETURN)
E1      OPSYN('G','F')
        DEFINE('F(S)','F2')
        OUTPUT = F('x')
        OUTPUT = G('y')
END
```
With a null third argument (`N = IDENT(NULL); OPSYN('G','F',N)`), SCRIP instead prints `new[]` — the driver's
exact symptom.

**Oracle rule (sbl agrees):** `OPSYN(new, old)` copies `old`'s definition AT THE TIME OF THE CALL; a later
`DEFINE` of `old` must not retroactively change what the alias resolves to. SCRIP's alias keeps tracking the
live, redefined `old`, so it either infinite-recurses (stack overflow, 2-arg form) or resolves to nothing
(null-3rd-arg form).

**Two sites cto named, not yet fixed:** the compile-time two-literal-argument path,
src/lower/lower_snobol4.c:2714, copies the def entry but the call still resolves the redefined name at call
time rather than the snapshot; the runtime path, `opsyn()` in src/runtime/pattern_match.c:500 calling
`register_fn_alias()` in src/runtime/core/core.c:3818, copies the `FNCBLK` fields but the null-third-arg form
comes back null instead of the snapshot.

**Confirmed collector-invariant** (cto, measured at `SCRIP_HEAP_MB=512`, at 1, at `SCRIP_GC_STRESS=0`, mode 4
compile+link+run — identical every time): not a GC bug, genuinely SNOBOL4-lane, not cto's/collector's to fix.
The originally-suspected cause (`prescan_defines()` eager top-level DEFINE prescan) is refuted — it only
matches literal `DEFINE(...)` at top level, not the bare-variable-argument form used here.

**ADDENDUM (hq_snobol4, 2026-09-23), read-only trace, no dynamic verification done (SCRIP busy with an
unrelated bisect this sitting) — both named sites look individually correct by static reading; the bug is
apparently somewhere neither site's own logic accounts for.** `sno_prescan_expr`'s OPSYN handling
(`lower_snobol4.c` ~2714-2718) does a genuine VALUE COPY of `defs[fo]` into a NEW, independent array slot
for the new name at the point the prescan visits the `OPSYN` call — for the reduction in this section, that
visit happens (in both source order and actual runtime order, they coincide here) BEFORE the later
`DEFINE('F(S)','F2')` statement updates F's own slot, so the copy correctly captures F's ORIGINAL state.
Likewise the runtime path — `register_fn_alias()` (`core.c:3776`) allocates a genuinely NEW `FNCBLK_t` and
copies `spec`/`entry_label`/`fn`/`nparams`/`params`/`nlocals`/`locals` BY VALUE from `old_entry` (a pointer
copy of the STRING pointer, not a shared mutable field) — and the later `DEFINE_fn_entry()` (`core.c:3712`)
mutates F's *own* `FNCBLK_t.entry_label` field in place, which cannot retroactively change a VALUE ALREADY
COPIED into a separate struct. Two leads for whoever picks this back up, neither followed: (1) `entry_label`
is a LABEL-NAME STRING that gets **re-resolved fresh on every call** via `rt_entry_resolve()` (see
`core_define_entry_label`, `core.c:3739`, and its callers in `rt.c:608/979/1019`) — if it were ever
re-resolving the *function* name "F" instead of a fixed *label* target, that would explain live-tracking,
but by-value the copied string reads "F" (the label), which behavior-wise should be label-stable regardless
of DEFINE; not directly verified whether `rt_entry_resolve` treats it that way in practice. (2) The
`SCRIP_DEFINE_FOLD` compile-time optimization noted in passing in `bb_goto_deferred.cpp` ("DEFINE-FOLD
s55 ONE-SHOT: jmp the function's alpha, no chain, no reserve") wires a call STATICALLY when the compiler
believes a name has exactly one definition — G, having exactly one `defs[]` entry (the OPSYN-copied one),
may qualify for this fold even though its *aliased* target (F) does not; not checked whether this fold
applies to G's call site or whether it resolves to the wrong thing if it does. Next attempt: gdb/`--dump-ir`
on the 8-line reduction to see what `defs[]`'s G-entry and `_func_buckets`'s G-FNCBLK actually contain at
the point `G('y')` is called, rather than re-deriving from source reading alone.

## 5. IMAGE_driver — function-frame codegen defect (cto's reduction)

**cto's measured 6-line reduction** (sbl prints `ABCD` then `DONE`; SCRIP segfaults both modes, every arena):
```
DEFINE('IM(S)T')                              :(E)
IM      IM = S
IM1     IM BREAK('_') . T ('_' | 'Q') = T     :S(IM1)F(RETURN)
E       OUTPUT = IM('AB_C_D')
        OUTPUT = 'DONE'
END
```
gdb: `rip` becomes a DESCR-tagged word (`0x100000002`-shaped), not a wild pointer — the return path itself is
overwritten. The stack beside it holds `IM`'s γ and ω continuations.

**Three required ingredients, each confirmed necessary** (cto): the same REPLACE at top level passes; the same
alternation as a match-only (no REPLACE) inside the function passes; the same REPLACE with `LEN(1)` instead of
the `('_' | 'Q')` alternation passes; moving the subject to a local `U` instead of the result variable still
crashes. So: **an ALTERNATION inside a REPLACEMENT inside a DEFINEd function corrupts the function's own
return path.** Confirmed collector-invariant, same basis as §4 — not a GC bug.

## 6. SIR / TEST — infinite loop; CODE()/EVAL() fragments don't reconnect to real program-level control flow

`corpus/packages/snobol4/aisnobol/SIR.sno` and `TEST.sno`, both modes: genuine infinite loop (9000+ identical
lines in ~5s), both `-INCLUDE "SPITCORE.sno"`. The repeating text is `LISTARG`'s type-mismatch error, meaning
its fatal-error handler `TDUMP` never actually stops the program.

**Traced mechanism:** `TDUMP` is `DEXTERN`'d — dynamically loaded from `spitlib.spt` via `CODE()` on first
use. It ends in an unconditional `:(END)`, meant to terminate the whole program per SPITBOL's EVAL/CODE
semantics ("as if spliced into the main program"). It doesn't: `bb_label_registry_add(lp_strdup("END"),
endnd)` (src/lower/lower_snobol4.c:2276) registers "END" against `endnd = exitnd`, the exit node **of the
specific compilation call in progress** — for a fragment compiled via `code_at()` (used by both `CODE()` and
`EVAL()`), that's the fragment's own local exit ("return to caller"), not real termination.
`sno_goto_target()` (line 969) exempts "END" from the fragment-mode label-nulling every other label gets
(`sno_label_reserved` includes END), so it resolves to this fragment-local exit. Control unwinds back through
`LOADEX` → `DEXTERN` → the `TDUMP(...)` call site inside `LISTARG`, falls through to whatever comes next, and
eventually loops back into SIR/TEST's own main loop, which retries the same failing operation forever.

**Corroborating, unconfirmed lead:** `src/runtime/runtime_eval.c`'s `rt_goto_resolve_x` (line ~464) has a
matching suspicious special case: `if (!strcmp(name, "END")) return NULL;` — returns NULL without setting the
`undef` error flag, silently relying on an unconfirmed caller-side special case for "END". This may be the
SAME underlying gap as the SETEXIT/EVAL bug fixed tonight (a22f9c6ed) seen from the runtime side rather than
the lowering side — that fix only addressed SETEXIT's error-trap priority, not this goto-to-END-from-a-
fragment case; not verified whether the landed fix has any bearing here.

Two plausible fix points, neither attempted: `lower_snobol4.c`'s fragment-mode END registration should resolve
"END" inside a `code_at()` fragment to the REAL program exit, not the fragment's local one; or
`runtime_eval.c`'s END resolution needs a real re-resolution path instead of a silent NULL. Either risks
regressing other CODE()/EVAL() users across the corpus if changed without full-suite verification — not
attempted for lack of remaining budget in the pass that found it.

## Also noted, not reduced further

- **spitbol_x64_tests `math_chop`**: not a crash — 34 of 1232 checked values differ from the oracle in the
  *last displayed digit* of large-exponent doubles (e.g. `...582931e+91` vs oracle's `...582932e+91`) — a
  double-to-decimal rounding edge case in the number formatter, `chop()`/`trunc()` themselves are correct.
  Formatter function not located.
- **spitbol_x64_tests `math_exp` crash**: enters its SETEXIT trap correctly (even before tonight's SETEXIT fix,
  in this call shape) but then corrupts state — `&ERRTEXT` reads back an unrelated later error's text, then
  segfaults. Plausibly a stack-unwinding mismatch between a mid-function `:(RETURN)` and `rt_chain_enter`'s own
  trampoline bookkeeping — same risk class as §3, unconfirmed shared cause.
- **spitbol_x64_tests `gcbuster`, `host`, `module`, `save`, `sv`, `math_atan` (m4 COMPILE_FAIL)**: not
  investigated at all this session.
- **A real language-conformance gap** (ceo, CEO-1187 telegram, unrelated to tonight's other work): `DEFINE('f()')`
  placed textually after a call to `f()` runs in SCRIP where SPITBOL raises ERROR 022 (undefined function),
  both modes — SCRIP is too permissive about forward-referenced-then-later-defined functions. Not reduced,
  not located in source.

## Ownership note

§1–2 (emit.cpp / pattern_match.c) and §4–5 (REDEFINE_driver / IMAGE_driver, cto-confirmed collector-invariant)
are SNOBOL4-lane, hq_snobol4's under DECTET line 2. §3 and the `math_exp` connection are shared runtime
(rt.c/runtime_eval.c) but narrowly SNOBOL4-triggered so far — land or ask per RULES.md at the time. §6 touches
`lower_snobol4.c` (SNOBOL4-only) and possibly `runtime_eval.c` (shared) — verify which side the real fix
belongs on before landing.
