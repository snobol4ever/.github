# FINDING — err248-system-fn-redefine: DEFINE/OPSYN now refuse system-function names, and the
first implementation caught a cross-language false-positive before it shipped

**seat07 (`/home/claude07`, Claude Sonnet 5), 2026-08-23, task `err248-system-fn-redefine` (hq_C
assignment, LINKS: `FINDING-2026-08-22-seat07-ir-ident-differ-inline.md`, q-system-fn-protection).**

## Goal and oracle-first measurement

SCRIP silently accepted `DEFINE`/`OPSYN` redefinition of any system function; real SPITBOL raises
**ERROR 248 "attempted redefinition of system function"** and dies. Per the task's own methodology,
the oracle was measured FIRST (`x64/bin/sbl -bf`, six probes) before any code was written:
- `DEFINE('SIZE(X)')` and `OPSYN('SIZE','TRIM',0)` → fatal ERROR 248, 1 statement executed.
- `OPSYN('MYALIAS','TRIM',0)` (non-system target) → succeeds normally, ordinary alias.
- `&ERRLIMIT=5` before the OPSYN attempt → **non-fatal**: `&ERRTYPE`=248, `&ERRTEXT`="attempted
  redefinition of system function" (no trailing period), execution continues. This is the mechanism
  that makes the defect byte-diffable at all against two structurally different error-dump formats.
- `OPSYN('=','TRIM',1)` (operator-kind form, `type≠0`) → succeeds, no 248. Confirmed protection is
  scoped to the plain name/function-synonym form (`kind==0`) only; operator redefinition is a
  separate, always-legal SPITBOL mechanism and was deliberately left untouched.

## The fix has two independent halves, because DEFINE and OPSYN are structurally unlike each other

**OPSYN** (`src/runtime/pattern_match.c:439`, `opsyn()`) is an ordinary runtime function shared by
both call sites (`_OPSYN_` in core.c and `by_name_dispatch.c:6935`). One added line, gated on
`kind==0`, calls the existing `kwb_error(248, ...)` helper before `register_fn_alias` — this
automatically inherits `&ERRLIMIT`/`&ERRTYPE`/`&ERRTEXT` semantics for free, since it is the same
mechanism the file's own pre-existing 152/153/156 checks already use.

**DEFINE is not a runtime call in the common case.** `src/lower/lower_snobol4.c`'s whole-program
prescan (`~2385-2418`) recognizes every compile-time-literal `DEFINE(...)` and **hoists it out of the
statement stream entirely** (`is_def[i]=1; ... continue;`) before `sno_build_graph` ever runs — the
function becomes callable from program start, and the DEFINE statement itself never becomes part of
the runtime control-flow graph. Confirmed by direct measurement: my first implementation (below) only
patched `_DEFINE_` (`core.c:2806`, the runtime C function `register_fn("DEFINE", ...)` wraps) and a
literal `DEFINE('SIZE(X)')` sailed through unprotected — `_DEFINE_` turned out to be reachable **only**
for a genuinely non-literal prototype, and SCRIP does not even support that yet (`FATAL lower_snobol4
(GZ#5 subset): DEFINE with a non-literal prototype string is outside the landed subset`). So the real
fix for the common case had to go in the prescan itself: both hoisting branches (the `TT_DEFINE` AST
form and the `sno_stmt_define`-recognized fallback) now check the parsed name and, if protected, print
`SCRIP: ERROR 248 -- attempted redefinition of system function: <name>` and `exit(1)` instead of
registering. **This is a compile-time refusal, not a byte-identical reproduction of SPITBOL's runtime
error dump** — DEFINE's pre-existing hoisting architecture has no notion of "the DEFINE statement
executing" at a point where `&ERRLIMIT` could even be consulted (prescan runs before any keyword has a
runtime value), and rearchitecting that is well outside this row's scope. What changed is real: the
redefinition is refused instead of silently accepted, which was the actual measured defect. Flagged
below as a follow-on for whoever wants full runtime fidelity there.

## ⛔ A real bug, caught before commit: the first version used the wrong registry

The first implementation checked names against `builtin_ids.h`'s `bid_of()`/`g_bid_tab` — the
perfect-hash table the emitter uses for fast by-name call dispatch. That table is **shared across every
language SCRIP compiles** (SNOBOL4, Icon, Pascal, Raku all in one namespace) and contains lowercase
entries that are Icon's builtins, not SNOBOL4's — `match`, `max`, `min`, `abs`, `sqrt`, `any`, `tab`,
and dozens more. Running the full corpus after the first build turned up exactly this: **4 new
failures** (`test_math`, `match_driver`, `omega_driver`, `semantic_driver`) that had nothing to do with
system functions — they were ordinary SNOBOL4 programs defining their own lowercase functions/locals
named `max` and `match`, now wrongly refused because those strings happen to occupy `g_bid_tab` slots
for Icon's `max()`/`match()`. This is exactly the class of regression RULES.md's NAME-16 rule makes
more likely going forward (new SNOBOL4 code is now encouraged to use short, lowercase, descriptive
names), not less.

**Fix: a new, SNOBOL4-only closed table**, `src/runtime/snobol4_system_fns.h` (95 entries,
`sn4_is_system_fn(name)`), mechanically derived from every `register_fn("NAME", ...)` call in
`core.c` — not hand-picked — filtered by one objective rule: uppercase-only, `MON_`-prefix excluded.
The exclusion removes two classes of non-user-facing internal registration that share the same table
for unrelated reasons: arithmetic-dispatch helpers (`add`, `sub`, `mul`, `neg`, `nPush`, `nPop`, `c`,
`n`, `t`, `v`, `__num_pos`, `DIVIDE_fn`, `POWER_fn` — lowercase or `_fn`-suffixed, never real SPITBOL
keywords) and the monitor IPC bridge (`MON_OPEN`, `MON_PUT_*_VALUE`, etc.). All three sites (`core.c`,
`pattern_match.c`, `lower_snobol4.c`) now include this header instead of `builtin_ids.h`. Re-ran the
full corpus after the swap: the 4 false positives are gone, `test_math`/`match_driver` produce their
real output again, and the err248 witness (below) is unaffected.

## Verification

- **DONE-WHEN** (task's own criterion, corrected path — see note): `SCRIP/scrip
  corpus/crosscheck/functions/err248_system_fn_redefine.sno` vs `/home/resources/x64/bin/sbl -bf` on
  the same file — **byte-identical, both m3 (`--run`) and m4 (`--compile`)**. New witness (checked in
  with its oracle-derived `.ref`) exercises 4 different protected names via `&ERRLIMIT`-caught OPSYN
  (SIZE, TRIM, DATATYPE, IDENT), a non-system OPSYN alias (negative control), an operator-kind OPSYN
  (negative control for the `kind==0` scope boundary), and a benign DEFINE (negative control that
  DEFINE still works normally). Literal-DEFINE-triggers-248 is deliberately **not** in the byte-diffed
  witness — see the DEFINE-hoisting discussion above; including it would make the whole file's
  compilation abort before any of the other, genuinely comparable output is produced.
- ⛔ **The task brief's DONE-WHEN names a relative `x64/bin/sbl`, which does not exist under this
  seat root.** `scripts/lib_oracle_flags.sh` documents that the old `${S4E_HOME}/x64/...` fallback was
  deliberately deleted ("a fallback does not just TOLERATE a per-root clone"); the only correct path is
  the absolute `/home/resources/x64/bin/sbl`. Ran the corrected command directly — passes. Not treating
  this as a blocker (a brief whose path is stale is still a brief); flagging so the next seat that
  copies this DONE-WHEN verbatim doesn't lose time to it.
- **SNOBOL4 corpus** (`test_corpus_snobol4.sh`, pristine build): m3 PASS=359 FAIL=1, m4 PASS=359
  FAIL=1 SKIP=0 (360 total) — the one failure, `demo_treebank` ("Pattern match failed"), is
  pre-existing and unrelated (already named as a known baseline failure in
  `FINDING-2026-08-22-seat07-ir-ident-differ-inline.md`, written before this session; confirmed here
  again by direct re-run, no ERROR 248 involved).
- **SNOBOL4 smoke**: 7/7 both modes (mode-4 HARD GATE).
- **Gate**: `test_gate_emit_no_lang.sh` OK (unaffected — the new table lives in `src/runtime/`, never
  reached by `src/emitter`/`src/templates`).
- **No new global variable**: `g_sn4_system_fns[]` is `static const` — immutable compile-time data,
  the same pattern `builtin_ids.h`'s own `g_bid_tab` already uses in this codebase. Every other
  identifier touched is a local or an existing accessor.

## Not done / follow-ons

- **DEFINE's protected-name refusal is a compile-time fatal, not a catchable runtime ERROR 248.**
  Full parity (respecting `&ERRLIMIT`, statement counting, `:F()` branching) would require literal
  DEFINE to stop being hoisted out of the control-flow graph — a real rung of its own, not a corollary
  of this one. `_DEFINE_` (`core.c`) is patched and correct for when that rung lands (or for whenever
  dynamic-prototype DEFINE is implemented — today it isn't: `FATAL ... DEFINE with a non-literal
  prototype string is outside the landed subset`).
- **`corpus/crosscheck/functions/err248_system_fn_redefine.sno` has no `.s`/`.j`/`.il`/`.wat` sibling
  yet** — this session ran the full mandated regen chain
  (`util_regen_{benchmark,feature,demo,programs,prolog_bench,crosscheck}_s_artifacts.sh`) since
  `lower_snobol4.c` was touched; see that chain's own commit for what it swept.
