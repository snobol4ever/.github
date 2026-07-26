# FINDING-2026-07-26-CLAUDE-PL-ISO-9-VARIABLE-NAMING-FAMILY-AND-TRACKER-VS-PROSE-MISMATCH.md

## RUNG: GOAL-PROLOG-BB.md LADDER A → PL-ISO-9

**LANDED:** `get_print_stream/1`, `name_singleton_vars/1`, `name_query_vars/2`, `bind_variables/2`.
Tracker (`PROLOG-ISO-TRACKER.md`, regenerated live): DONE 135→139, core-open 103→99, UNASSIGNED
unchanged at 0. `pretty.pl` 5/5, `print.pl` 3/3 — both now fully closed.

## (1) THE TRACKER'S PL-ISO-9 AND THE GOAL FILE'S PL-ISO-9 PROSE WERE TWO DIFFERENT SCOPES

Before touching code, I re-ran `audit_prolog_iso_coverage.sh` live (it had never been pointed at a
populated `refs/gprolog-master` in this session's sandbox before) and diffed its output against the
committed tracker — zero diff, so the committed tracker was already ground-truth-current. Its own
`RUNG` map assigns `write.pl`→PL-ISO-9 and `format.pl`→PL-ISO-9 alongside `pretty.pl`/`print.pl`, but
`write.pl` and `format.pl` were ALREADY 12/12 and 2/2 DONE — only 4 rows across `pretty.pl`/`print.pl`
were actually open under that name. The goal file's PL-ISO-9 prose ("format directives `~p ~q ~e ~f
~g ~r ~c ~s ~t~| ~+`; write_term/2 options; print_message") describes real, still-open work, but none
of it corresponds to a `set_bip_name` row the audit script can see — those are *option atoms* and
*format directive characters*, not top-level exported predicates, so the mechanical tracker is
structurally blind to them. **Marking PL-ISO-9 `[x]` would have been exactly the stale-doc failure
class RULES.md names ("a document asserting a fact nothing checks and nobody updates")** — so the
goal file line is `[~]` (partial): the tracker-visible predicate set is closed, the prose-only
directive/option work is not, and the cursor says so explicitly rather than rounding up.

## (2) DESIGN SOURCE — READ THE REAL SOURCE, NOT JUST THE MANUAL PROSE

All four predicates were designed directly against `refs/gprolog-master/src/BipsPl/pretty.pl` +
`print.pl` and `refs/gprolog-master/doc/pl-bips.tex` (canonical per RULES.md CONSULT CANONICAL
SOURCES). `get_print_stream/1` is not separately specified anywhere beyond "the stream `print/1` and
portray write to" — gprolog's own `print.pl` never sets a distinct print-stream global, so it reduces
to current-output; verified this by diffing the returned stream term against `current_output/1`'s
(`==` succeeds — same underlying handle).

`name_singleton_vars/1` and `name_query_vars/2` both bind to `'$VARNAME'(Name)`, sharing the exact
distinct-unbound-var-walk shape as the already-landed `numbervars/1,3` (`pl_numbervars_walk`, this
file) — refactored into a reusable `pl_distinct_vars_walk` (dedup by pointer identity, occurrence
COUNTED not just deduped, since singleton detection needs the count). `bind_variables/2` is the
general form numbervars/3 is defined in terms of (per the manual: `numbervars(Term,From,Next)` ≡
`bind_variables(Term,[from(From),next(Next)])`) — implemented the full option parser
(`numbervars`/`namevars`/`from/1`/`next/1`/`exclude/1`).

## (3) BUG CAUGHT BEFORE COMMIT — `[]` IS `DT_S`, NOT `DT_A`, IN THIS CELL MODEL

First draft checked `(int)d->v == DT_A && (int)d->i == nil_id` to detect the empty list and used
`pl_make_atom(nil_id)` to build one. **Every test failed silently** (goal just failed, no crash, no
error — the worst kind of bug to catch) because SCRIP's Prolog cell model represents short atoms,
including `[]`, as inline `DT_S` string cells (`v=DT_S, s="[]"`), not always as interned `DT_A` ids —
confirmed by grep against the working sibling `rt_pl_term_variables_cell` (line 683, this file),
which already builds nil as `nil.v = DT_S; nil.s = "[]"` and by two other general-atom call sites
(`by_name_dispatch.c:571,1404`) that explicitly check BOTH tags for exactly this reason. Fixed by
adding `pl_atom_text()` (returns the C string for either `DT_S` or `DT_A`, else NULL) and
`pl_is_nil()`/`pl_nil_cell()` built on it; every atom-identity check in all four functions (list nil,
option-name atoms, the `=`  functor check, the `Name` atom in `Name=Var` pairs) now goes through this
helper instead of assuming one tag. **RULE FOR NEXT SESSION touching `pl_cell_t` atoms directly:
never compare `d->v == DT_A` alone — an atom is `DT_A` OR `DT_S` depending on how it entered the
cell, and code that only checks one tag will silently reject half its valid inputs.**

## (4) GPROLOG 1.4.5's OWN `bind_variables/2` CONTRADICTS ITS OWN MANUAL — DID NOT COPY THE BUG

The manual (`pl-bips.tex`) documents `next(Next)` as an OUTPUT: "when `bind_variables/2` succeeds,
`Next` is unified with the last integer N used + 1." The real gprolog 1.4.5 source
(`pretty.pl:148-150`) calls `'$check_nonvar'(Next), integer(Next)` on it — i.e. the shipped
implementation actually REQUIRES `Next` bound going in, and then does nothing further with it
(verified live: `bind_variables(foo(X,Y,X),[from(5),next(N)])` with `N` unbound throws
`instantiation_error` in real gprolog 1.4.5; with `N` pre-bound to any integer it just fails). Lon
directed KEEPING the documented (ISO/manual) semantics rather than bug-compatibility — implemented
`next(Next)` as: accepts UNBOUND (binds it to the computed next-N on success, per the manual) or a
pre-bound integer (accepted, not currently cross-checked against anything, matching the manual's
silence on that case) — never throws instantiation_error on a fresh `Next`. Verified live:
`bind_variables(foo(X,Y,X),[from(5),next(N)])` → `N=7` in SCRIP, matching the doc's arithmetic
exactly. **This is a deliberate, documented divergence from gprolog 1.4.5's shipped behavior — noted
here so a future cross-check session doesn't "fix" it back to the buggy form.**

## (5) SECOND REAL DIVERGENCE FOUND AND FIXED — `from(NotAnInteger)` ERROR SHAPE

Initial cut threw `type_error(integer, Value)` when `from/1`'s argument wasn't an integer. Live
gprolog 1.4.5 throws `domain_error(var_binding_option, from(Value))` instead — traced to the real
control flow: `'$get_bind_variables_options2'(from(From)) :- '$check_nonvar'(From), integer(From), ...`
is one clause among several; when `integer(From)` fails, THE WHOLE CLAUSE FAILS (not an exception),
so Prolog backtracks into the catchall `'$get_bind_variables_options2'(X) :- '$pl_err_domain'
(var_binding_option, X)` — the ENTIRE malformed option term becomes the domain-error culprit, not
just its argument. Fixed to match: `from(bad)` → `domain_error(var_binding_option, from(bad))`,
verified byte-identical to gprolog 1.4.5 (module the universal `_G0` vs `bind_variables/2` context arg
cosmetic difference every other ISO error in this runtime already carries).

## (6) VERIFICATION — BYTE-IDENTICAL VS GPROLOG 1.4.5 ON EVERY CHECKED CASE

`apt-get install --no-install-recommends gprolog` (1.4.5, matches the tracker's own oracle version) —
first attempt with the doc package pulled unrelated GUI deps into a broken mirror; `--no-install-
recommends` avoided it cleanly.

- `name_singleton_vars`: `foo(X,Y,X)` → `foo('$VARNAME'('_'),...)` at the singleton `Y` slot only,
  non-singleton `X` slots untouched — **byte-identical** `write_canonical` output vs gprolog (mod
  cosmetic fresh-var naming `_G0` vs `_38`).
- `name_query_vars`: `['X'=X,'Y'=Y,foo=bar]` → binds `X`,`Y` to `'$VARNAME'('X')`/`'$VARNAME'('Y')`,
  `Rest = ['.'(foo=bar,[])]` (the non-`Name=Var` element passed through) — **byte-identical**.
- `get_print_stream`: same stream as `current_output/1` (`==` succeeds); `stream_property(_,alias(_))`
  gives `no_alias` in SCRIP vs gprolog's `top_level_output` — confirmed this is a PRE-EXISTING gap
  shared identically by `current_output/1` (untouched by this session, same `no_alias` result), not
  something this rung introduces or owns.
- `bind_variables`: `from(5)` on 2 distinct vars → `'$VAR'(5)`/`'$VAR'(6)`, `next` unifies to 7;
  `namevars` → `'$VARNAME'('A')`/`'$VARNAME'('B')`; default (`[]`) → `numbervars` behavior starting
  at 0; `exclude(['$VAR'(0)])` skips 0, starts at 1 — **all four byte-identical to gprolog 1.4.5**.
  Three ISO error shapes (`domain_error` bad option, `type_error(list,_)` non-list options,
  `domain_error(var_binding_option, from(bad))`) — **byte-identical** (mod the `_G0` context cosmetic).

## (7) KNOWN GAP SURFACED, NOT FIXED THIS RUNG — THE WRITER HAS NO `$VAR`/`$VARNAME` HOOK

`grep -rn "VAR\|VARNAME" src/runtime/*.c` restricted to writer logic: zero hits. `write/1` on a
numbervars'd or bind_variables'd term prints the raw `'$VAR'(N)` compound instead of a letter (`A`,
`B`, ...) the way gprolog's `write/1`/`print/1` do — only `write_canonical` (which deliberately never
special-cases anything) was used for verification in this FINDING for exactly that reason. This is
PRE-EXISTING (the already-DONE `numbervars/1,3` has carried the identical gap silently since it
landed) and is out of scope for PL-ISO-9's admission test (the tracker checks predicate existence +
correct C-level behavior, not writer integration) — but it is precisely a `write_term/2` numbervars-
option item, i.e. the next natural slice of this same rung's still-open prose half. Flagged in the
goal file cursor; not fixed here to keep this rung's diff to the variable-naming family only.

## GATES (all green, `-O0`, no `-O2` directive this session)

- `test_prolog_rung_suite.sh`: **164/164 × 3 modes** (interp/run/compile).
- `test_smoke_prolog.sh`: **5/5/5** (m2/m3/m4).
- `test_gate_pl_no_new_global.sh`: PASS, ratchet 14/floor 14 **UNMOVED** (no new globals — only
  `static` file-local helpers added).
- `test_gate_pl_no_value_stack.sh`: PASS.
- `audit_prolog_iso_coverage.sh`: DONE 135→139, core-open 103→99, UNASSIGNED unchanged at 0.

## WATERMARK

SCRIP `src/runtime/unification.c` (5 new functions: `rt_pl_get_print_stream_cell`,
`pl_distinct_vars_walk`, `pl_atom_text`, `pl_is_nil`, `pl_nil_cell`, `rt_pl_name_singleton_vars_cell`,
`rt_pl_name_query_vars_cell`, `pl_namevars_letters`, `rt_pl_bind_variables_cell`) + `by_name_dispatch.c`
(4 dispatch arms, 4 det-builtin table rows, 1 `pl_builtin_is_known` line). corpus: none touched.
.github: this FINDING + `PROLOG-ISO-TRACKER.md` regenerated + `GOAL-PROLOG-BB.md` PL-ISO-9 line
corrected to `[~]` with the tracker-vs-prose split spelled out.

BANKED (carried, none resolved this session): NO-LCO deep-recursion segfault + cumulative exhaustion;
nested-`\+` binding leak; retractall/1 gaps; compiled-path silent-fail on undefined predicates; the
writer's missing `$VAR`/`$VARNAME` hook (new banked item, §7 above).
