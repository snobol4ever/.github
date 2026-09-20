# FINDING 2026-09-20 hq_raku — a trailing `;` dropped every Raku sub's return value, and rung 07's own witness could never have caught it

**Seat:** hq_raku · **MODE:** SEPTET · **Row:** `raku-the-six-benchmark-graphs-with-no-frame-layout-are-cured-one-construct-family-at-a-time`
(rank 2, claimed), reached from the rank-0 GC row `raku-the-31-no-layout-graphs-…`.
**Oracle:** `/home/resources/rakudo-local/bin/raku` v2026.05. **Tree:** SCRIP `51199e79a` (this cure), corpus `8486bb1e2` (the two witnesses). **`RT_OPT` = `-O0`.**

## The defect

`sub_body` builds the implicit return from **one** arm, `'{' stmt_list expr '}'` — a final expression carrying
**no semicolon**. Write the semicolon and `expr ';'` folds the expression into `stmt_list` instead, where nothing
carries its value out of the sub. `method_body` has the same shape.

Measured against the oracle, both modes:

| final statement of the sub body | rakudo v2026.05 | SCRIP before | SCRIP after |
|---|---|---|---|
| `7;`                  | 7 | *(empty)* | 7 |
| `"s";`                | s | *(empty)* | s |
| `$k;`                 | 2 | *(empty)* | 2 |
| `$k + 1;`             | 3 | **1**     | 3 |
| `$k <= 0 ?? 9 !! 7;`  | 7 | *(empty)* | 7 |
| `$k.Str;`             | 2 | *(empty)* | 2 |
| `(7);`                | 7 | *(empty)* | 7 |
| `7` *(no semicolon)*  | 7 | 7         | 7 |

⛔ **`$k + 1;` returned 1, not empty.** The sub handed back a **stale return register**, not a missing value —
which is why this never read as one defect. An empty answer looks like an unimplemented feature; a plausible
number looks like an arithmetic bug somewhere else. Same value class the cto's rule (b) is written against,
except that it was already in the tree rather than about to be landed by a parse cure.

## Why no witness caught it

`corpus/tests/raku/ALL.raku` has carried `ladder__rung07_subs_implicit_return` since the rung was cut:

```raku
sub double($x) { $x * 2 }
say double(5);
```

**No semicolon.** The rung that exists to grade the implicit return graded only the shape that works. The
defective shape is the *more idiomatic* of the two and appears in five of the six no-frame-layout benchmarks.

⭐ This is the same lesson this seat filed on 2026-09-20 about the statement-prefix/phaser family, recurring
one rung over and reaching the opposite conclusion about which shape was missing: **a construct family graded
only on its own witnesses is graded on the shapes someone thought to write down.** Filing it as a fact about
phasers was not enough to catch it here; the reusable form is the sentence, not the family.

## The cure

`rk_tail_value()` in `src/parsers/raku/raku.y` wraps a body's final statement in `TT_RETURN`, called from
`sub_body`'s and `method_body`'s `'{' stmt_list '}'` arm.

Two placement facts that cost measurement and would cost the next reader a reverted landing:

1. **It runs BEFORE `rk_phasers_place`, never after.** That function's own `tail_ret` arm already lifts a
   trailing `TT_RETURN` aside and re-appends it after the phasers. Wrap afterwards and you wrap whatever
   phaser rank sorted last — a `LEAVE`/`KEEP` body — instead of the value.
2. **The statement set is a DENYLIST, not an allowlist of value kinds.** An unrecognised node kind is left
   alone and keeps today's behaviour, rather than being silently handed a value it never had. `TT_IF` as a
   final statement is *deliberately* on the denylist: rakudo returns the taken branch's value and we do not,
   and that is a second cure with its own witness, named here and not smuggled in under this one.

## Verdict, base vs head on one tree

* RakM development pass, same tree, `--lang raku --modes m3,m4`, arena 512 MB:
  **base 839/927 → head 841/929, both modes.** m3_fail 38 and m4_fail 25 **unchanged**; +2 gained, 0 lost —
  exactly the two new witnesses. The cure is board-neutral on every pre-existing entry.
* Witnesses proven **red on the base binary** (`1` for 3; empty for 7) and green on the cure, m3 and m4.
* `make preflight` 56 arms 0 red · `test_smoke_raku.sh` 10/10 both modes ·
  `test_gate_parser_generated_files_in_sync.sh` GATE GREEN · bison conflicts unchanged.
* **No shared node.** `raku.y` is reached by one frontend, so SHARED-NODE VERDICT SCOPE does not bind;
  `rk_tail_value`/`rk_tail_is_statement` are statics in that file.

Two witnesses minted through the sanctioned path (`util_add_ladder_witness.py --lang raku`, refs cut by the
oracle, never by us): `ladder__rung07_subs_implicit_return_trailing_semicolon` and
`…_bare_literal_tail`. Denominator 927 → 929.

## Named, not cured

* **`TT_IF`/loop as a final statement** still yields no value (denylist above). Own witness, own row.
* **`run_raku_via_x86_backend.sh` cannot run.** It sets `SCRIP="$(cd "$HERE/.." && pwd)"` and then
  `SCRIP="${SCRIP:-$ROOT/scrip}"` — the variable is already set, so `:-` never fires and `SCRIP` stays the
  **tree root directory**. `[ -x "$SCRIP" ]`, the guard that exists to say *scrip not built*, **passes on a
  directory** (`-x` means searchable, not runnable), so the script reports `FAIL scrip emit failed:` with an
  empty error file. The Prolog twin it claims to mirror has the correct `ROOT` line; the Raku copy dropped it.
  ⭐ Two of this digest's own lessons at once: a guard answering a narrower question than the reader thinks,
  and a copy that carries its donor's *claim* of equivalence after diverging in the one line that matters.
  ✅ **CURED the same sitting, SCRIP `9d3479b42`**: `ROOT` holds the tree, `SCRIP` holds the binary, and the
  guard is `-f` AND `-x`. Proven by grading both witnesses through the script in m4 — 3 and 7, where it had
  printed only its own failure banner. ⛔ **Any raku m4 red read through that script before `9d3479b42` is a
  false red and must be re-measured.**

## Sequel, same sitting — why this had to land FIRST

Five of the six no-frame-layout raku benchmarks end a sub body with a semicolon. Curing their **parse** without
curing this would have made them compile and print a plausible wrong answer silently — the cto's standing rule (b)
exactly. With this in, the `:=` scalar bind landed as SCRIP `d6ccadc69` and the row's own instrument moved:
**raku `no_layout` 9 → 7, `graded` 918 → 922**, `unkinded=0 holes=0` unchanged.

⭐ **The two graphs it freed were ONE construct, and the row's own GOAL had them as two.** That GOAL names
`benchmark_rc-man-or-boy-test` as *a self-referential closure binding* and `benchmark_point_class_add2` as
*NQP internals* — both are the `:=` bind (`my $B := { … }`, and `my Point $self := nqp::create(self)`, the typed
arm). **A per-file construct list written from the failing line is a guess about the family**; re-derive the
construct from the parse error before trusting it.

⭐⭐ **And the test rule (b) actually needs, which this sitting produced:** ask whether lowering the new construct
**INHERITS** a wrong answer or **INTRODUCES** one, and decide it by running the `=` spelling of the same program.
`my @x = (1,2,3)` is already correct against rakudo, so lowering `my @x := (1,2,3)` to an assign would *introduce*
a wrong answer — refused by name. `my $a = (1,2,3)` is already wrong, so the scalar arm only *inherits* one — landed.
One command per arm, and it replaces an argument about taste with a measurement.


⛔⛔ **CORRECTION, SAME SITTING, BEFORE ANYONE CITES THE ABSOLUTE: 839/927 → 841/929 WAS A DEVELOPMENT PASS ON A COPY OF THE MASTER WITHOUT ITS COMPANIONS, AND ITS ABSOLUTE IS WRONG BY TWELVE PROGRAMS.** The copy carried only `ALL.raku`, `ALL.ref` and `ALL.csv`; the master also ships `ALL.wantrc`, `ALL.argv.bare` and `config/`, which the harness resolves BY PATH beside the suite. Without them, entries needing argv get none and entries with a non-zero declared rc are graded as plain failures. **The real board over the corpus path reads `853/929` both modes** (m3 FAIL=26 · m4 FAIL=14, m4 skip=12), against the previously published `851/927` at `fadeab33f` — so on comparable real-board terms the landing is **+2 pass, +2 denominator, 0 lost**, which is the two new witnesses and nothing else. ⭐ **THE DELTA SURVIVES AND THE ABSOLUTE DOES NOT**: base and head were run on the identical incomplete copy, so the comparison is sound and every number read off it as a level is not. A dev-pass absolute must never be published, and `test_gate_master_companions_resolve.sh` is the gate that exists for exactly this.
