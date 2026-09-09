# FINDING 2026-09-08 hq_P — `DEFINE` is applied at COMPILE time, so a later redefinition retroactively changes earlier calls

## Claim

In SNOBOL4 `DEFINE` is an **executable statement**: a call before it sees the old definition, a call
after it sees the new one. SCRIP resolves every `DEFINE` of a given name at **compile** time into one
slot of a single table, so **the last `DEFINE` in program order wins for the whole program** —
including calls that execute before it.

## The witness (8 lines, both modes)

```
        DEFINE('F(S)')                          :(e)
F       F  =  'first'                           :(RETURN)
G       F  =  'second'                          :(RETURN)
e       OUTPUT  =  F('x')
        DEFINE('F(S)', 'G')
        OUTPUT  =  F('x')
END
```

| | line 4 | line 6 |
|---|---|---|
| `sbl -bf` | `first` | `second` |
| SCRIP m3 | **`second`** | `second` |

## Mechanism — located, not guessed

`src/lower/lower_snobol4.c` keeps one compile-time table `defs[]` keyed by function name, with **one
slot per name**. Three sites collect into it and all three overwrite:

- `:2539` `if (fo >= 0) defs[fo] = d;`
- `:2723` `if (found >= 0) { defs[found] = d; def_body[found] = body; }`
- `:2745` `if (found >= 0) defs[found] = d;`

`--dump-ir` on the witness confirms the consequence exactly: both call sites lower to `CALL "F"`
(dispatch is correctly **by name**), two `IR_DEFINE` bind nodes are emitted in the right places —
and there is only **one `; proc F`**, built from the surviving table slot. The runtime has one body
to reach, so the name-dispatch has nothing to choose between.

## Arms that did NOT fix it — record so nobody re-runs them

| hypothesis | test | result |
|---|---|---|
| the first `DEFINE` omits its entry, so the bind attaches no entry operand (`sno_bind_attach_entry`, `:982`, returns early when `entry` is empty) | write `DEFINE('F(S)','F')` explicitly | **no change** — still `second second` |
| the per-entry-label proc machinery exists but is gated on `g_sno_uses_code` (`:2785`, emits a `LBL__<lbl>` proc per label) | force that path on with a `CODE()` call in the witness | **no change** — still `second second` |
| label binding is wrong generally | `DEFINE('F(S)')` with a second unrelated label, and with a non-prefix label name | **correct in both** — not a label-resolution bug |
| dotted identifiers (`MYF.`) mis-lex | `DEFINE('F.(S)')` and call `F.('x')` | **correct** — periods are part of identifiers as they should be |

So the cure is not a missing operand or a gate: **a proc must exist per distinct entry, and `IR_DEFINE`
must re-point the name→proc binding at run time.** That is structural work in the SNOBOL4 lowerer.

## Blast radius — 4 gimpel reds, and the idiom is the reason

The affected programs are not exotic. They use the standard SNOBOL4 **self-redefining one-shot**: a
function whose first call redefines it so later calls take a different entry, often redefining itself
back on failure. A compile-time one-slot table cannot represent it by construction.

| program | shape | board today |
|---|---|---|
| `gimpel/REDEFINE_driver` | `REDEFINE()` swaps a function and preserves the old under `NAME.` | RED m3=RC1 m4=RC1 |
| `gimpel/COPYL` | `DEFINE('COPYL(L)T')` ×2 + `DEFINE('COPYL(L)','COPYL_1')` | RED m3=RC1 m4=RC1 |
| `gimpel/PERM` | `DEFINE('PERM(A)','PERM_INIT')` ×2 + a 3-arg redefinition | RED m3=SIG6 m4=SIG6 |
| `gimpel/PERMS` | `DEFINE('PERMS(S)…','PERMS_INIT')` ×2 + a plain redefinition | RED m3=RC1 m4=COMPILE_FAIL |
| `snoflake_suite/syntactic-recognizer` | `DEFINE('F…')` ×2 | not separately graded |

⛔ The RC1/SIG6/COMPILE_FAIL spread is **one defect wearing four symptoms** — calling the wrong body
with the wrong formal list crashes in whatever way that body happens to crash.

## ⛔⭐ The part that matters most: two correct witnesses exist and NOTHING GRADES THEM

`corpus/tests/snobol4/` contains `define_redef_three_way.sno` and `define_redef_alt_entry.sno`, with
**correct `.ref` files** (`one/two/three` and `first/second-via-alt-entry`). Both are RED today —
SCRIP prints `three three three` and `second second`.

**Neither appears in `ALL.csv`, `ALL.xfail`, or `ALL.excluded.txt`.** They are not passing, not
expected-failing, and not excluded — **they are simply not in the master suite at all**, so the board
never runs them. The SNOBOL4 master reads `1894/1894 FAIL=0` tonight with this defect live and its
own witnesses sitting unused beside it.

⭐ That is the sharpest instrument lesson here, and it is a different shape from the ones this project
has catalogued: not a test that cannot fail, and not a stale denominator — **a correct, failing test
that no denominator contains.** An `xfail` at least appears in a census. This is invisible to every
count we keep, because every count starts from `ALL.csv`.

⛔ I did **not** add them to the master. Two known-reds would take the blocking arm from `FAIL=0` to
`FAIL=2` for every seat, 34 hours before the announcement; whether they enter before or after the
cure is a `ceo` call, not a seat's.

## Routing

Structural lowerer work → the **cto**'s NONET lane (the hardest engine bug). Not cured here.

⚠️ Control-arm warning for whoever takes it, per the corrected SHARED-NODE law (CEO-405): the cure
changes how **user-function dispatch** binds, and the carriers of that state are the proc table and
`IR_DEFINE`, which Icon and Prolog procedures also reach. The lowerer census names SNOBOL4 only; the
wider answer is owed.

## Provenance

SCRIP `13c3cf588`, corpus `00eb70759`, `RT_OPT=-O0`, oracle `/home/resources/x64/bin/sbl -bf`.
Surfaced walking hq_P's NONET Q-Z gimpel slice from `REDEFINE_driver`.
