# FINDING — an oracle's refusal is evidence about THE FILE YOU HANDED IT, never about the program upstream shipped

**hq_P, 2026-09-10.** Measured with `/home/resources/icon-master/bin/icont` (Icon v9.5.25a) against
`/home/resources/jcon-master` and `/home/resources/icon-master/ipl`. Trees: SCRIP `db870418b`, corpus `47349890c`,
`.github` `b6caf38a`. Raised by ceo **CEO-487**, which measured two of the four; the other two are this sitting's.

## The claim

Four Icon package programs were ruled `ORACLE_REFUSES` — *a ruling, meaning nobody owes work* — on a real, correctly
quoted icont refusal. **All four refusals were icont refusing OUR OWN FILE.** Each differs from its upstream original
**only by the semicolons our 826-file Icon conversion appended**, upstream compiles `rc=0` under the same icont, and
in every case the **vendored `.std` already matches Arizona icont output byte-for-byte**, so no ref re-cut is owed
either. All four move to `UNGRADED` / `NEEDS_VENDORED_SOURCE` and return to the graded denominator when the source is
re-vendored.

| program | recorded refusal | upstream under the same icont | ours vs upstream | `.std` vs icont |
|---|---|---|---|---|
| `jcon_tests/geddump` | `Line 139 # ";": invalid declaration` | compiles `rc=0`, runs `rc=0` | semicolons only (0 residual lines) | **matches byte-for-byte** |
| `jcon_tests/htprep` | `Line 257 # ";": missing then` (+266, 286) | compiles `rc=0`, runs `rc=0` | semicolons only (0 residual lines) | **matches byte-for-byte** |
| `jcon_tests/prepro` | `Line 10 # $undef: too many arguments` | compiles `rc=0`, runs `rc=0` | semicolons only (17 in `.icn`, 2 in `.dat`) | **matches byte-for-byte** |
| `ipl/progs/qei` | `Line 185 # ";": extraneous arguments on $else/$endif` | compiles `rc=0` | semicolons + whitespace only | not run (compile-class row) |

`prepro` is the one CEO-487 ruled the other way — *"prepro stays OUTSIDE: icont refuses the upstream too ($undef with
an argument is a jcon preprocessor extension)"*. It does not. `$undef ghi` with one argument is ordinary Arizona Icon.
A bare staged copy of the upstream fails `"prepro.dat": cannot open` — **the staging, not the preprocessor**; with the
shipped `prepro.dat` companion beside it, upstream compiles `rc=0` and runs clean. **Proven by repair:** strip only the
19 semicolons our conversion put on `$` directive lines and our own file compiles `rc=0`, runs `rc=0`, and its output
matches the vendored `prepro.std` exactly.

`qei` is **hq_P's own row from 2026-09-09**, and it is the sharper half: it had already been re-measured once that
morning and *confirmed*. **A re-measurement that repeats the original question can only ever confirm.** The control
that breaks the tie is a *different* question — `diff ours upstream` — and it had never been asked.

## The shape

**An oracle's refusal is evidence about the file you handed it. It is evidence about the program upstream shipped only
if somebody checked that they are the same file.** The two have opposite owners: one is a closed ruling, the other is
work owed, and the refusal text is identical.

The discriminator is one command, it costs nothing, and **the `tpp1`–`tpp5` rows in this very package already carried
it**: *"byte-identical to arizona_tests/general/tppN.icn, and upstream ... does not compile standalone either — NOT our
vendoring edit."* That sentence is the whole difference. (Its first half has since gone stale — our conversion touched
those fragments too, re-measured and corrected here — while the half the ruling rests on holds.)

`lib_inventory.sh`'s own tie-break names why this was expensive rather than merely wrong: *a wrong `UNGRADABLE` removes
a program from the debt permanently and silently — nobody re-reads a closed ruling.* These four sat closed with a
one-`sed`-wide repair behind them, inside the announcement window, in the one language Lon put every seat on.

## What landed

- `corpus/packages/icon/jcon_tests/OUTSIDE_ARIZONA_BASELINE.tsv` — three rows re-classed and re-reasoned; header gains
  **THE CONTROL ARM**, which states the standing rule: **no `ORACLE_REFUSES` row may be written in any Icon package
  without an upstream control in its reason column.**
- `jcon_tests/UNGRADABLE.tsv` → `jcon_tests/UNGRADED.tsv` for the three; `tpp1`–`tpp5` control sentences corrected
  (class untouched — they are `$include` fragments with no `main` either way).
- `ipl/UNGRADABLE.tsv` → `ipl/UNGRADED.tsv` for `qei`; the *"it stays put"* line in the 91-row note corrected in place.
- Swept: `ORACLE_REFUSES` rows keyed on a semicolon anywhere under `corpus/packages/icon` are exactly these four.

## What is owed, and by whom

**hq_B holds the repair class** (ceo CEO-487, on Lon's order). The DONE-WHEN for each of the four is measured and
sharp: `icont -s` compiles it `rc=0`, and its run matches the **already-correct shipped `.std`**. hq_P re-boards the
jcon and ipl suites when the repair lands. **10 files under `corpus/packages/icon` carry a semicolon on a
preprocessor-directive line** (`geodat`, `qei`, `htprep`, `prepro`, `tpp`, `tpp1`–`tpp5`) — a starting census for the
class, not its boundary: `geddump`'s semicolon is in a declaration and `htprep`'s three are inside an `if` condition
and two parenthesised continuations, so a directive-line grep alone under-reports it.
