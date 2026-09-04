# FINDING: `scrip --run`/`--dump-ast` with multiple positional source files silently honors only the first one

Discovered while working `dead-suite-path-consumer-sweep` (fixing `test_parser_snocone.sh`'s dead
`FIX="$S4E/corpus/tests/snocone/parser-fixtures"` default). Fixing the corpus path alone made every one
of 67 extracted fixtures fail with **empty output**, not a mix of real pass/fail -- the "non-empty is not
alive" false-signal class, one shared cause wearing 67 filenames, not 67 independent parser defects.

## The mechanism

`test_parser_snocone.sh` invokes the Snocone-self-hosted parser tool as 15 positional source files, on
the assumption that `scrip` concatenates them into one program:

```
scrip --run "$SD/global.sc" "$SD/case.sc" "$SD/assign.sc" ... "$SD/parser_snocone.sc" < fixture.sc
```

It does not. Confirmed by swapping order, not by reading driver source (ASM-DIFF-FIRST's minimal-repro
doctrine, applied to CLI behavior instead of codegen):

```
$ ./scrip --dump-ast bootstrap/global.sc bootstrap/parser_snocone.sc | wc -l
56
$ ./scrip --dump-ast bootstrap/global.sc | wc -l
56
```

`global.sc` first + `parser_snocone.sc` second produces **exactly** `global.sc`'s own statement count,
byte-for-byte the same as `global.sc` alone. `parser_snocone.sc`'s content -- including the driver code
at the bottom of the file (`Src = ''; while (Line = INPUT) Src = Src Line nl; if (Src ? Compiland) ... else
OUTPUT = 'Parse Error';`) -- never appears anywhere in the dump. Reversing the order confirms it
symmetrically: `parser_snocone.sc global.sc` dumps parser_snocone.sc's content (including its driver,
visible via the `else` branch's `OUTPUT = 'Parse Error'` assignment appearing in the AST) and `global.sc`
never appears. **Only the first positional source file is ever read; every subsequent one is silently
dropped**, with no warning on either stdout or stderr, exit 0.

This is why `--run`ning the full 15-file invocation returns exit 0 with completely empty stdout: with
`global.sc` first (as `test_parser_snocone.sh` orders them), only its top-level statements execute --
plain variable assignments, no output side effect -- so the program does nothing and exits cleanly. It
looks like a hang-free, crash-free, well-behaved run producing no output, which is a much quieter failure
mode than a crash would have been.

## Scope: isolated, not a tree-wide regression

`grep`ped `scripts/*.sh` for any other caller passing 3+ bare `.sc`/`.sno`/`.icn`/`.pl` positional
filenames to `scrip` on one invocation line: **zero hits**. `test_parser_snocone.sh` is the only consumer
of this composition technique anywhere in the tree. `src/driver/scrip.c`'s argument-parsing loop shows no
code path that accumulates multiple source files either (checked, not just absence-of-grep-hit). Whether
this ever worked -- an earlier driver version, since removed or never generalized -- or was never actually
exercised end-to-end since the script's 2026-05-19 authorship, was not traced; either is consistent with
what's measured here, and distinguishing them would require source-control archaeology on `scrip.c`
itself, which is out of scope for what was a "dead corpus path" row.

## What was and wasn't done about it

Fixed (this row's actual scope, both verified): the dead `FIX` corpus-path default (repointed to extract
the Snocone master's `parser` family, 67 entries, via `lib_master_extract.sh`) and a second, unrelated
pre-existing bug in the same file (`SCRIP="${SCRIP:-$HERE/scrip}"`, missing `../` -- resolves to
`scripts/scrip`, a dead symlink to a nonexistent `/home/claude/one4all/scrip`; every other caller in the
tree correctly uses `$HERE/../scrip`).

NOT fixed, and deliberately not attempted this pass (own dedicated investigation, matching how this same
row has repeatedly deferred `test_emit_diff_invariant_check.sh` and `test_crosscheck_x86_single_program.sh`
rather than rush a bigger shape onto a smaller fix's momentum): whatever the right composition mechanism
actually is. Two candidates, neither explored: (a) Snocone may have its own `INCLUDE`-style directive
meant for exactly this (SNOBOL4's `-INCLUDE` is real and documented elsewhere in this project; whether
Snocone inherits or has an equivalent was not checked), in which case `parser_snocone.sc` and its 14
sibling files should be joined at the SOURCE level into one file scrip is handed, not concatenated via the
shell command line; or (b) `scrip`'s driver could grow real multi-file-source support, if that is meant to
be a general capability rather than something this one script alone ever needed.

`test_parser_snocone.sh` itself now detects this class live (checked every run, not asserted once and
trusted forever) and REFUSES (rc=2) with the diagnosis when every failure in a run got empty output,
rather than printing a `PASS=0 FAIL=67`-shaped board that would read as 67 real parser defects. If the
underlying invocation is ever fixed, the script starts reporting real per-fixture results automatically,
with no separate code path to remember to remove.

## For whoever picks up `dead-suite-path-consumer-sweep` next

`test_parser_snocone.sh` is now off the fossil-path gate's list (was 7, is 6) and its corpus-path half is
genuinely fixed and verified. It should NOT be re-added to that row's remaining-scope list on that basis
-- the row's own charter is dead corpus PATHS, and that part is done. The multi-file-invocation question is
a different, standalone follow-up; no row exists for it yet as of this writing.
