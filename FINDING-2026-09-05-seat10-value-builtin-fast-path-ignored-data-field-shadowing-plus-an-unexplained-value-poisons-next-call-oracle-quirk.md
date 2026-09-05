# FINDING — the `VALUE` builtin's fast dispatch path ignored `DATA()` field-shadowing (fixed), and a separate, still-unexplained "VALUE() poisons the next library-style call" oracle quirk (open)

**Seat:** seat10 · **Date:** 2026-09-05 · **Mode:** FLEET-20 (hq_P lane, SNOBOL4)
**Row:** `snobol4-testpgms-test1-traps-29-runtime-errors-under-spitbol-scrip-traps-3` (STEP A)
**Tree:** SCRIP (this session's commit, see LEDGER) · corpus unchanged · oracle `/home/resources/x64/bin/sbl -bf`, cross-checked against `/home/resources/spitbol-bench-oracle/sbl -bf`

## 1. FIXED: `VALUE(x)` ignored `DATA()`-based field shadowing when reached via the fast BID dispatch

`test1.spt`'s "TEST MULTIPLE USE OF FIELD FUNCTION NAME" section does
`DATA('CLUNK(VALUE,LSON)')`, which makes `VALUE` a field accessor of `CLUNK`. Real SPITBOL then
raises **041 "FIELD function argument is wrong datatype"** for any subsequent `VALUE(x)` call
whose argument is not a `CLUNK` instance — including a plain string argument. SCRIP silently
returned empty instead (statement `!LE(4,10)`'s slot in the file, ERRTYPE 41, was simply absent).

Root cause, found via ASM-diff (`--compile`) + grep, not guesswork: SNOBOL4 calls compile to
`rt_call_arr_bl` → `rt_call_arr_impl` → `try_call_builtin_by_name_bl`
(`src/runtime/by_name_dispatch.c:4286`, ~1900 lines). That function has a fast **known-builtin-ID
jump table** (`switch(_bid)`) that, for `BID_VALUE`, went straight to `NV_GET_fn` (the original
by-name variable lookup) with **no check that "VALUE" had been re-registered as a field name**.
A *different*, narrower check earlier in the same function (line ~4288) *does* handle the case
where the call argument is already a matching-type `DT_DATA` instance — which is why
`VALUE(a_clunk_instance)` already worked before this fix — but nothing covered the "argument is
NOT already the right DATA type" case, which is exactly when SPITBOL's 041 applies.

Two-part fix, verified against the oracle on isolated witnesses:
1. `src/driver/driver_data.c`, `c_dat_field_get`: when no field matched and no `rt_str_method`
   (Raku) fallback applied, if `fname` **is** a registered field name of *some* type
   (`rt_dat_field_of_any`), raise `core_runtime_error(41, "field function argument is wrong datatype")`
   instead of silently returning `FAILDESCR`. Only the getter — the setter (`dat_field_set`) is
   confirmed to NOT raise 41 in real SPITBOL even for a wrong-type target
   (`LSON(some_node) = 'X'` gives `SET OK` in both oracle and SCRIP; do not "symmetrize" this).
2. `src/runtime/by_name_dispatch.c`, the `BID_VALUE` case (~line 6001): before falling to
   `NV_GET_fn`, check `rt_dat_field_of_any("VALUE")`; if true, dispatch through `dat_field_get`
   instead (which now correctly raises 41 for a mismatched argument via fix #1, and still returns
   the right field value for a matching-type argument, unchanged).

Verified: isolated witnesses `VALUE(a_clunk_instance)` (still 'A', unchanged),
`VALUE('a_plain_string')` after `DATA('CLUNK(VALUE,LSON)')` (now 041, matching oracle exactly, both
`/home/resources/x64/bin/sbl` and the independent `spitbol-bench-oracle` clean build), and the
*exact* real-file shape `VALUE('B')` where `B` holds a `NODE` (not `CLUNK`) instance (now 041,
matching). Full SNOBOL4 corpus regression run before pushing (see LEDGER for the exact command and
result) — check there before trusting this is still clean.

⛔ **CROSS-LANGUAGE RISK, same shape as the `!`/`/`/`%`/`#`/`|` fix before it**: `by_name_dispatch.c`
is shared by SNOBOL4/Icon/Prolog. The new `rt_dat_field_of_any` check only fires for a 1-arg call
whose name is a genuinely-registered field of *some* `DATA()`/record type — for any other name,
`c_dat_field_get`'s existing `rt_str_method` fallback (Raku string methods) is tried *first* and
unchanged, so this should not touch Raku method dispatch. Icon's own record field syntax
(`record.field`) lowers to a dedicated `IR_FIELD_GET` node (`src/lower/lower_icon.c:440`) and never
reaches this string-keyed path at all, so it is unaffected structurally, not just by luck — but it
was not re-verified against the Icon corpus this session; do that before calling this fully closed
(the SNOBOL4 corpus run is the only regression evidence on file so far).

⛔ **NOT A CLASS FIX.** Per RULES.md's own escape clause ("fix the class or leave it visibly red with
a named witness"): `BID_VALUE` is the *only* case in that ~100-entry jump table that got this
treatment. Any other `BID_*` name that also happens to be `DATA()`-able as a field (nothing stops a
program writing `DATA('FOO(SIZE,TRIM)')`) almost certainly has the identical bug — untested, not
fixed, left as a named gap for whoever scopes the real class fix. The right shape is probably a
*single* guard placed once, generically, for every `BID_*` arm that has a same-named field-shadowing
possibility, not ~100 individual edits — that is a job for its own row, not a smuggled-in patch here.

## 2. NOT FIXED, characterized precisely: `VALUE()` appears to "poison" the very next not-yet-warm dispatch, and separately SCRIP hoists literal `DATA()` specs to compile time while the oracle evaluates them at their normal runtime position

This is what remains of the original STEP A mystery ("statement 137 is ERRTYPE 22 in the oracle,
never mentioned as a `VALUE`/`DATA` issue by the prior ledger entries, which assumed it was
`!LT(4,5)`"). **The prior ledger's raw-line→statement mapping was wrong** — re-derived mechanically
(Python, honoring `;`-separated multi-statement lines and `.`-continuation lines, which the earlier
"skip `*`/blank/`-EJECT`" description did not account for): statement 137 is raw line 198,
`DATA('CLUNK(VALUE,LSON)')` itself — **not** `!LT(4,5)` (that is actually statement 144). Statement
139 (not 140) is `VALUE('B')` at raw line 200. Whoever resumes this row should re-derive the mapping
fresh rather than trust either version, ideally with a real `&STNO` trace of the compiled program
rather than a static script (semicolons are handled here but there may be other cases missed, e.g. a
`;` inside a quoted string containing a literal semicolon, which this script's naive quote-tracking
does handle but has not been independently cross-checked statement-by-statement against the oracle's
own `&LASTNO`).

Given that corrected mapping, the oracle's ERRTYPE 22 at statement 137 is on the **`DATA('CLUNK(VALUE,LSON)')` statement itself**, not on any use of a comparison predicate. Isolated, minimal, reproducible on **both** independent oracle builds (`x64/bin/sbl` and `spitbol-bench-oracle`, ruling out an x64-fork-specific instrumentation artifact):

```
&ERRLIMIT = 1000
SETEXIT(.ERRH)
DATA('NODE(VAL,LSON,RSON)')
B = NODE()
TEST = DIFFER(VALUE('B'),B)     ; <-- first-ever VALUE() call in the program, succeeds normally here
DATA('CLUNK(VALUE,LSON)')        ; <-- oracle: CAUGHT ERRTYPE=22 here.  SCRIP (post-fix #1 above): no error here at all.
OUTPUT = 'AFTER DATA CALLS'
:(DONE)
ERRH    OUTPUT = 'CAUGHT ERRTYPE=' &ERRTYPE
        SETEXIT(.ERRH) :(CONTINUE)
DONE    OUTPUT = 'DONE'
END
```

Further isolation, ruling out `DATA`/`CLUNK` involvement specifically: a **bare** `VALUE(name)` call
(no `DATA()` anywhere in the program, `name` a plain assigned variable) followed by a call to **any**
not-yet-referenced comparison predicate (`LT`, or `LE` if tried first instead — order-independent,
whichever is referenced *first* after the `VALUE()` call takes the hit) also raises ERRTYPE 22 on
that first reference, one-shot only — the *second* reference to the same predicate in the same run
evaluates completely normally. An ordinary, definitely-core builtin (`TRIM`) referenced right after
`VALUE()`, with nothing else touched first, does **not** show this effect in the one case tried.
Minimal witnesses (not yet committed to corpus):

```
&ERRLIMIT = 1000
SETEXIT(.ERRH)
B = 5
TEST = DIFFER(VALUE('B'),B) STARS
OUTPUT = 'LT(4,5)=' LT(4,5)      ; oracle: CAUGHT ERRTYPE=22 here (both builds).  SCRIP: no error, LT(4,5) evaluates normally.
OUTPUT = 'AFTER'
:(DONE)
ERRH    OUTPUT = 'CAUGHT ERRTYPE=' &ERRTYPE
DONE    OUTPUT = 'DONE'
END
```

Swapping `LE` in for the first post-`VALUE()` reference instead of `LT` reproduces the identical
one-shot 22 on `LE` instead — so this is not specific to `LT`, it is whichever not-yet-touched
comparison-family name is referenced *first* after a `VALUE()` call anywhere earlier in execution.
**Working hypothesis, not confirmed** (no SPITBOL source available to verify against): `LT`/`LE`/
`GT`/`GE`/`EQ`/`NE` (and perhaps others) are not true core primitives in the reference SPITBOL
implementation but are lazily resolved on first reference from some internal table, and `VALUE()`'s
own by-name lookup mechanism has a side effect that causes exactly the *next* such lazy resolution
to report "undefined" once, after which it resolves normally for the rest of the run. This is a
real, reproducible property of **both** available oracle builds (so almost certainly genuine
upstream SPITBOL behavior, not an x64-fork-specific instrumentation defect of the kind already on
file for the `TRACE`/ERROR-199 class) — but replicating SPITBOL's exact internal mechanism in SCRIP
without its source is a much deeper undertaking than this row's scope. Recommend this become its own
row, owned by whoever is best placed to either find/build a from-source SPITBOL to read, or to
accept it as a documented, permanently-open oracle-fidelity gap.

**Separately and only loosely related:** re-running the `DATA/CLUNK` witness above with `DATA`
appearing *before* the `VALUE()` call in **source order** but where the file is compiled by SCRIP —
SCRIP still applies the `CLUNK` field-shadowing to `VALUE('B')` calls that, in the oracle, execute
*before* the `DATA('CLUNK...')` **runtime** statement has been reached. That is: SCRIP appears to
register a **literal-argument** `DATA(...)` call's fields at compile time (`record_register` is
called directly from `src/lower/lower_snobol4.c:2427` for any `DATA('...')` call whose argument is
a compile-time string literal), globally, for the whole program, regardless of where that statement
falls in the runtime control flow — while the oracle clearly treats `DATA()` as an ordinary runtime
statement whose effect only exists after it actually executes. This is a genuine, structural
divergence (confirmed by: `probe_value_then_data.spt`-style test where `VALUE('B')` — called
*before* the `DATA('CLUNK...')` statement executes — is already treated as CLUNK-shadowed by SCRIP,
raising 041, where the real oracle still treats it as the plain builtin at that point in the
control flow, only shadowed after the `DATA` statement executes and hitting the *separate* ERRTYPE
22 quirk above at that point instead). Not fixed here: this is a compile-time-hoisting design choice
in `lower_snobol4.c` that most likely exists for a real reason (forward references / recursive
type definitions?) and deserves its own investigation into whether it can be made
order-respecting without breaking whatever it was built for, rather than a quick patch under this
row.

## Net effect on this row's DONE-WHEN

Before this session: SCRIP raised **no error at all** at either of the two divergent statements
(missing both entirely, not just wrong-typed). After: the second one (`VALUE('B')`, formerly
mis-numbered "140", actually statement 139) is now **byte-exact** against the oracle. The first
(`DATA('CLUNK(...)')` itself, formerly mis-numbered "137", actually statement 137 — the mechanical
count agrees with the old number here by pure coincidence) now raises *something* (041) where it
previously raised nothing, but the oracle's own ERRTYPE there is 22, for the separate, unresolved
reason above — so this one line stays red. `m3` line count moved from 93 to 95 (of the real 140);
the DONE-WHEN is still RED overall, correctly (STEP B's TRACE-line divergence is untouched and was
never in this row's scope for today). See LEDGER for exact before/after diffs and the corpus
regression command run before push.
