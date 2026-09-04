# FINDING — arithmetic errors silently bypassed `core_runtime_error`: two cures landed, one deeper emitter bug still open

**Date:** 2026-09-03 (~23:00-00:30 CDT, crossing into 09-04 UTC) · **Seat:** seat03 (FLEET-8, hq_P lane) · **Row:** `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect`

## Headline

Root-caused the `setexit-not-invoked-under-errlimit-survival` class (FINDING-2026-09-03-seat08 §4.1):
it was never actually a SETEXIT/ERRLIMIT logic bug. `rt_div`/`rt_mod` (the compiled fast-path used by
every ordinary `/`/`MOD` in expression code, `src/runtime/arithmetic.c:243-244`) silently returned
`FAILDESCR` on a zero divisor instead of calling `core_runtime_error` at all — so the entire
SETEXIT/ERRLIMIT machinery in `core_runtime_error` was **dead code for arithmetic errors**, never
reached, regardless of whether it was itself correct. Only `DIVIDE_fn` (the separate by-name/OPSYN
dispatch path) called it correctly. **Two real cures landed** (see LEDGER on the row's task file,
commits below); **a third, separate, deeper bug was exposed and root-caused but NOT fixed** — an
error-only-reachable label's compiled code body can be silently dropped from emission while its
registration-table entry survives, producing a dangling symbol.

## 1. THE ARITHMETIC BYPASS (cured)

`src/runtime/arithmetic.c:243-244`, the `RT_BINOP_ENTRY`-generated `rt_div`/`rt_mod`:
```c
RT_BINOP_ENTRY(rt_div, BINOP_DIV, if (b.i == 0) return FAILDESCR; ...)
RT_BINOP_ENTRY(rt_mod, BINOP_MOD, if (b.i == 0) return FAILDESCR; ...)
```
On a zero divisor this just fails the statement silently (like an ordinary pattern-match failure) —
never touching `core_runtime_error`, `&ERRLIMIT`, `&ERRTEXT`, or any armed `SETEXIT` handler. Verified
against the **correctness oracle** (`/home/resources/x64/bin/sbl -bf`) on a bare `D=0; X=1/D` with no
`&ERRLIMIT`/`SETEXIT` at all: real SPITBOL prints `ERROR 014 -- division caused integer overflow` and
aborts before the next statement. SCRIP silently continued. Cured by calling
`core_runtime_error(2, "division caused integer overflow")` (exact oracle wording, needed because
`keyword_replace_2`'s own `.ref` reads `&ERRTEXT` after the trap) on the zero-divisor path, matching
the pattern `DIVIDE_fn` already used. `rt_mod` gets the same call with `NULL` (generic message; no
witness in this class exercises MOD, so no oracle-verified text was fabricated for it — worth checking
if a MOD-by-zero witness is ever minted).

Left alone, deliberately: `rt_num_arith`/`rt_num_arith_impl` (`arithmetic.c:207-264`), which duplicate
the same silent-FAILDESCR pattern for **compile-time constant folding** (`src/optimizer/const_fold.c`).
That's correct behavior there — `X = 4.0 / 0.0` as a literal must NOT abort the compiler, it must defer
to normal runtime evaluation, which then raises the error if that statement ever actually executes.
`rt_num_arith_impl` is shared between the folder and the real-number/mixed-type runtime path (`rt_div`'s
own fallthrough when not both `DT_I`), so real-valued division/modulo-by-zero **at runtime still
silently fails** — same architectural gap, not fixed this sitting because untangling "am I folding or
executing" needs its own careful design, and no witness in this class needs it (all four use integer
division specifically to dodge the compile-time fold — see `keyword_replace_2`'s own header comment).
`src/runtime/by_name_dispatch.c:4115` (`bn_remdr`, the `REMDR()` builtin) has the identical
silent-FAILDESCR-on-zero pattern too, a third independent instance — not touched, just noted.

## 2. A HIDDEN SECOND BUG THE FIRST FIX WAS MASKING (cured)

Fixing §1 alone **broke a currently-passing, non-xfail test**: `keyword_branch_2`
(`&ERRLIMIT=10; X=1/D :F(NEXT)`, no `SETEXIT` anywhere, expects `CONTINUED`). `core_runtime_error`
(`src/runtime/core/core.c:2060`) had a transfer branch for "SETEXIT armed AND `&ERRLIMIT` nonzero" but
**no branch at all** for "`&ERRLIMIT` nonzero, no SETEXIT armed" — that case fell through to the
unconditional abort. This is exactly FINDING-2026-09-03-seat08 §4.2
(`errlimit-not-invoked-under-errlimit-survival` / `errlimit-alone-does-not-survive-undefined-function`,
witness `keyword_replace_branch_9`), but it turns out to not be a narrow, exotic case — an
already-green corpus test depends on it. Added the missing branch: `&ERRLIMIT != 0` alone now
decrements the budget, publishes `&ERRTEXT`/`&ERRTYPE`, and **returns normally** (letting the caller's
`FAILDESCR` take the statement's own `:F()`/fallthrough path), rather than falling to the
print-and-abort fallback. This is error-code-agnostic (lives in `core_runtime_error` itself, not in
`rt_div`), so it also cured `keyword_replace_branch_9` (`undefined function called`, a different error
code entirely) for free — that entry is promoted too, not just the arithmetic ones. Note there is
ALSO a second, older, parallel implementation of nearly this same idea (`kwb_error()` in
`src/runtime/keywords.c:209-214`, used by some keyword-access error sites, not by `core_runtime_error`)
— the two are not unified; a future session normalizing error-survival logic should know both exist.

Both fixes verified: `keyword_branch_2`, `keyword_replace_1`, `keyword_replace_branch_9` all byte-match
their oracle `.ref`; bare `plain_divzero` (no ERRLIMIT) still correctly hard-aborts; full
`test_corpus_snobol4.sh` control run shows no other regressions (see task LEDGER for the exact board).

## 3. STILL OPEN — a compiled label can be silently dropped from emission (NOT fixed, root-caused)

`keyword_replace_2`, `keyword_replace_branch_10`, `keyword_replace_branch_11` (3 of the class's 4
witnesses) remain broken even with §1+§2 landed. Root cause, via ASM-DIFF-FIRST (`--compile` on a
minimal working/failing pair):

- **Minimal pair**: `keyword_replace_1` (7 statements, works) vs `keyword_replace_2` (8 statements,
  fails) — identical `SETEXIT(.H) / &ERRLIMIT=10 / D=0 / X=1/D` prefix; `keyword_replace_2` has one
  extra statement (`OUTPUT="AFTER"`) between the erroring statement and the unconditional `:(END)`.
- In `keyword_replace_1`'s compiled `.s`, `LBL__H:` is emitted as a real code label (defined) AND
  registered in the startup proc table.
- In `keyword_replace_2`'s compiled `.s`, the startup proc table STILL emits `.quad LBL__H` (a
  reference), but **`LBL__H:` itself is never defined anywhere in the file** — the label's entire
  compiled box chain is missing, even though a data literal it would have used (`"HANDLER "`) survives
  in `.rodata` (proving the string pool and the code-emission walk are on different, independently-gated
  paths). `H` is reachable ONLY dynamically (via `SETEXIT(.H)`, a NAME value, never a static
  `:(H)`/`:S(H)`/`:F(H)` control-flow edge) in BOTH programs equally, so "unreachable by static
  analysis" alone can't be the differentiator — something about the extra intervening statement (or
  something correlated with it) changes whether the emission walk keeps the label.
- Confirmed this is not cosmetic: `gcc keyword_replace_2.s -lscrip_rt ...` **fails to link**
  (`undefined reference to 'LBL__H'`) — this is the actual mechanism behind FINDING-2026-09-03-seat08's
  own note "m4 refuses to compile this shape at all" for branch_10/branch_11, now precisely located
  rather than just observed as a symptom.
- Mode 3 (`--run`) fails the same way at runtime (`rt_label_get_fn`/`rt_proc_get_fn("LBL__H")` finds
  nothing), consistent with BOTH-MEDIUM correctness expectations — whatever drops the label in TEXT
  emission almost certainly drops the equivalent binary blob too.
- Secondary effect of landing §2 without §3: `rt_goto_transfer("H")`'s failure now recurses into
  `core_runtime_error(38, "transfer to undefined label: H")`, which itself gets silently absorbed by
  the new §2 branch (`&ERRLIMIT` is still nonzero at that point) and returns normally instead of
  crashing — so `keyword_replace_2`/branch_10/branch_11 now fail **silently** (exit 0, no output)
  rather than with the loud "Error 38" abort they produced with only §1 landed. Not a regression in
  PASS/FAIL terms (still correctly xfail either way, still diverges from `.ref`), but worth knowing so
  the next investigator isn't surprised by the changed symptom. `rt_goto_transfer`'s callers
  (`core_runtime_error`'s transfer branch, and separately `bb_goto_deferred.cpp`'s codegen use for
  ordinary indirect gotos) never check whether the transfer actually found its target before falling
  through to `exit(0)` — a real gap, but fixing it means changing `rt_goto_transfer`'s signature, which
  ripples into codegen call sites; scoped out of this sitting along with the label-drop bug itself
  since it's downstream of the same root cause and touches a different subsystem (emitter/codegen,
  not runtime) than §1/§2.

**Not root-caused further this sitting** — needs an emitter/box-emission-walk investigation (likely
around `emit.cpp`'s label-chain reachability/emission decision, or `bb_glue_flat.cpp`/
`bb_glue_framed.cpp`), which is a different subsystem than the runtime-library fixes above and was
judged bigger than one sitting. Suggested first step for whoever picks this up: bisect the "extra
statement" variable directly — take `keyword_replace_1` (works) and add statements one at a time
between the error and `:(END)` until `LBL__H:` disappears from `--compile` output, to find the exact
trigger rather than guessing from the two existing witnesses alone.

## Landed

- SCRIP: `arithmetic.c` (rt_div/rt_mod call `core_runtime_error`), `core.c` (errlimit-alone survival
  branch in `core_runtime_error`). Commit hash: see task LEDGER (pushed same session).
- corpus: `keyword_replace_1` and `keyword_replace_branch_9` promoted out of
  ALL.sno/ALL.ref/ALL.xfail/ALL.csv (all four homes, INTERIM PROMOTION PROTOCOL followed — `list`
  clean, all three bypass arms PASS for both). `keyword_replace_2`, `keyword_replace_branch_10`,
  `keyword_replace_branch_11` remain xfail, reason text unchanged (still accurate — "handler never
  fires" is still true, now for the newly-precise reason in §3 above rather than the original "never
  even attempted" reason; not rewritten this sitting since the observable symptom for a reader of
  ALL.xfail — divergence from `.ref` — hasn't changed, only the internal mechanism, which lives here
  instead).

## For hq_P

Filing this as a class row candidate: `snobol4-error-only-label-dropped-from-compiled-emission`
(or hq_P's preferred name) — blocks full resolution of 3 witnesses in the row's own class, plus
probably a wider category (ANY label reachable only via `SETEXIT`/similar dynamic-name use, not just
these 3). Not minted by seat03 (fleet seats don't mint); routing per protocol.
