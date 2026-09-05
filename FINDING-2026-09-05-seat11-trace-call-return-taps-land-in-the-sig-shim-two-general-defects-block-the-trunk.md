# FINDING 2026-09-05 seat11 — CALL/RETURN trace taps landed in the SIG shim (bb_define_sr); two pre-existing, general (non-TRACE) defects block trace_trunk.sno's last DONE-WHEN arm

**Seat:** seat11 (hq_P lane) · **Mode:** FLEET-20 · **Tree:** SCRIP this commit
**Task:** `snobol4-trace-types-v-l-c-r-k-a-print-spitbols-banner-in-both-modes`

## 1. Where CALL/RETURN actually needed to be wired (corrected from the prior sitting's own note)

The prior seat11 sitting concluded F's real prologue lives in `src/emitter/emit.cpp`'s
`codegen_flat_chain_body` / `xa_flat_chain_prologue_str` (`src/templates/xa/xa_flat.cpp`) — the
"CLASS-C" mechanism. **That mechanism is never reached for a plain `DEFINE`'d, tiny-shim-eligible
proc.** I built and landed hooks there first, rebuilt, and measured **zero** occurrences of
`rt_trace_call_hook`/`rt_trace_return_hook` in the compiled `.s` for `trace_trunk.sno` — proving
`xa_flat_class_c_pred()` is false on this path — then reverted that change entirely (it would have sat
dormant, unverified, in a shared hot path used by other languages/constructs; `git checkout` confirms
it is gone).

The real reached path is **`bb_define_sr()`, role 4, the `fnsig()` branch** in
`src/templates/bb/bb_define.cpp` ("IR_DEFINE role 4: SIG s66 per-DEFINE shim") — confirmed by reading
the compiled `.s` directly (ASM-DIFF-FIRST) and matching every instruction back to this function's own
`x86(...)` chain line by line: the `F_α:` label (`x86_def_ext(emit_label_intern(la.c_str()))`), the
`sub rsp,64` frame carve, the save-and-zero of the extra/result slot, the `cmp rdx,i`/swap-by-map
formal marshal — all of it is this shim, not CLASS-C.

## 2. What's landed and verified correct

Two taps added to `bb_define_sr()`'s fnsig branch, register-save list and `g_trace` gate copied
verbatim from this same file's own `bb_define_activate()` taps (including `r9`, which
`RTCC_GLOBAL_R9_GVA` pins as the GVA table base for the whole function — a plain C hook function is
free to clobber any caller-saved register unless saved/restored around the call):

- **CALL tap**, inserted right after the formal-marshal `FOR` loop, before the `jmp` into the body —
  fires once every formal is in its GVA home, mirroring where `bb_define_activate`'s own tap fires
  relative to its marshal-in.
- **RETURN tap**, gamma-only, inserted right after `rax:rdx` are loaded with the definitive return
  value (the pre-existing nreturn-after-indirect-assign-wrong-value reload), before the `jmp` back to
  the caller. Omega/FRETURN is deliberately left unaddressed — no witness in this row exercises it.

**Measured correct** (`trace_trunk.sno`, both modes, byte-diffed against the swapped oracle):
- CALL fires exactly once, tag `tagF`, name spelled `F` (bare, matching real SPITBOL's non-dotted
  concatenation spelling — confirmed byte-identical to oracle), value blank (F is unset at call time —
  correct), **`lastno=12` — byte-identical to oracle.**
- RETURN fires exactly once, tag `tagR`, **`lastno=5` — byte-identical to oracle.**
- `&TRACE` reads `0` inside both callback invocations and is correctly restored after each — no
  regression to the already-landed accounting.

This proves the tap *placement*, the *register discipline*, the *tag propagation*, and the *depth/stno
plumbing* (`g_stno` read directly by `rt_trace_call_hook`/`rt_trace_return_hook`, unchanged from the
prior sitting) are all correct. The two remaining diffs are NOT in this code — see below.

## 3. Blocker A — `&LASTNO` (`g_stno`) is not restored across ANY call/return boundary (general, pre-existing, TRACE-independent)

Minimal trace-free repro (no `DEFINE`/`TRACE` interaction beyond a single ordinary call):

```
	DEFINE('G(Y)')	:(START)
G	G = Y	:(RETURN)
START	N = G(9)
	OUTPUT = 'lastno=' &LASTNO
END
```

- Oracle (`/home/resources/x64/bin/sbl -bf`): `lastno=3`
- SCRIP (m3): `lastno=2`

Real SPITBOL restores the caller's `g_stno` once a called procedure returns, so a statement *resuming*
after a nested call reports itself, not the callee's last statement. SCRIP's `rt_stmt_enter` (writes
`g_lastno = g_stno; g_stno = stno`, `src/runtime/keywords.c:455`) only fires at a **textual** statement
boundary — nothing saves/restores `g_stno` at a **call** boundary in any of the calling conventions
(confirmed absent from `bb_define_sr`; I did not exhaustively check the other ~4 calling-convention
shims in `bb_call_proc_staged.cpp`, `bb_define.cpp`'s `bb_define_activate`/`bb_define_bind`, or
`xa_flat.cpp`'s CLASS-C, but the defect is in the same *family* of code by construction — a call/return
boundary — not in any TRACE-specific site).

This is why `trace_trunk.sno`'s **`N`'s own (pre-existing, already-landed) VALUE trace** — fired
*after* `N = F(2)` completes, no code of mine on that path — reports `lastno=4` (leaked from *TF's own*
last-executed statement, since TF itself now also runs and calls `rt_stmt_enter`) instead of oracle's
`lastno=12`. Before my CALL/RETURN taps existed at all (hooks never firing), the same line already read
`lastno=5` (leaked from *F's own* statement) instead of `12` — proving the leak predates and is
independent of this row's work.

**Not fixed here**: the fix belongs at the call/return boundary shared by every calling convention, not
in the TRACE dispatch — a shared-node class per FLEET-20's own rule ("cure only fixture-, xfail- or
instrument-level reds yourself; a shared-node class goes to hq_U with the witness"), and touching it
blind under one sitting risks every other calling convention's own board.

## 4. Blocker B — a currently-returning `DEFINE`'d proc's own name reads blank via external by-name (`$NAME`) lookup

Oracle's RETURN line: `tf tagR F = 2 lastno=5 trace=0`. SCRIP's: `tf tagR F =  lastno=5 trace=0` — the
`$NAME` dereference (TF's own body, `NAMEVAL(rt_ws_strdup_c("F"))` created in `rt_trace_event`,
`src/runtime/core/core.c`) reads blank instead of `2`.

This is **not** the `retval` argument I plumbed through `rt_trace_return_hook` — `rt_trace_event`'s
registered-callback branch never reads its `value` parameter at all (only the default-banner branch
does), so my RETURN tap's rax:rdx-preservation work, while correct and necessary for the two untraced
default-banner witnesses (`M`, `P`), is simply inert here. The blank value is `NAMEVAL`'s own by-name
resolution of the string `"F"` at the moment TF's body executes.

I could not pin the exact mechanism in the time this sitting had. Ruled out: this is not a
`RTCC_GLOBAL_R9_GVA`-vs-absolute-addressing split — `bb_var_global.cpp`/`bb_assign_global.cpp` (plain
global reads/writes, which is how `N`/`M`/`P` are compiled) **also** respect
`RTCC_GLOBAL_R9_GVA`, and `N`'s own by-name read (the exact same `NAMEVAL(strdup(name))` path, same
callback, different name) reads correctly (`N = 2`) — so `r9`-relative and by-name resolution do land
on the same memory for an ordinary variable. `F` is different only in being the name of the procedure
*currently in the middle of returning* at the moment the lookup happens, which suggests `gva_index_of`
(or whatever `NAMEVAL`'s deref ultimately calls) may resolve a `DEFINE`'d proc's own name to a
different slot than `bb_define_sr`'s `rgx` (`rt_proc_result_name_get`-derived) while that proc is
active — a symbol-resolution question, not a fixture bug, and out of scope for this row to chase
further blind.

## 5. DONE-WHEN status

`trace_bogus_type.sno` (ERROR 199) and `trace_undefined_function.sno` (ERROR 198): **still PASS, both
modes** — unaffected by this sitting's change (re-verified after landing).

`trace_trunk.sno`: **still RED, both modes** — but the diff surface has shrunk to exactly the two
general defects above; the CALL/RETURN mechanism itself (registration, dispatch, tag, depth, stno-at-
the-instant-of-the-event, `&TRACE` save/zero/restore) is now verified correct. The DONE-WHEN stays
whole per standing ceo ruling (CEO-286) — not weakened to make the row closable.
