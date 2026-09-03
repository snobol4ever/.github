# FINDING: Pascal gets a smoke floor gate and a construct ladder (rungs 0-9); building them found two new defects

**Who/when:** seat10, 2026-09-03, FLEET-16, row `pascal-smoke-floor-gate-and-construct-ladder-from-rung-0`
(GOAL-TEST-SUITE-CONSISTENCY.md — Lon's "make testing consistent across all 7 languages" initiative).

## What was built

**`test_smoke_pascal.sh`** — 9 witnesses (writeln, for-loop, while-loop, procedure, recursive function,
array, record, set, files-via-stdin), HARD zero-FAIL both modes, shape copied from `test_smoke_icon.sh`.
Every expected value is the literal captured stdout of `fpc -Miso` on that exact witness — none hand-typed.
One hand-transcription error (a single missing space in a right-justified integer field) was caught by
running the finished script end-to-end before landing it, not assumed correct from the source construction
alone — the fix was to stop hand-typing padded literals entirely and compute them (`printf '%11s' N`).

**`test_pascal_ladder.sh`** — mechanically identical to `test_prolog_ladder.sh` / `test_raku_ladder.sh`
(`--to N` / `--only N` / `--list`, both modes, `lib_master_extract.sh` origin-keyed extraction, REFUSE rc=2
discipline). hq_B's own template was not on origin when this row was picked up (grepped `SCRIP/scripts/` for
`*ladder*template*` — nothing; same finding seat11 already made for the Raku sibling row) — built directly
from the proven shape per the row's own doorbell-mail fallback instruction ("build the language's witnesses
first"). 10 rungs landed: hello, var/assign, arithmetic, if/while, for/repeat, procedure+function, arrays,
records, sets, strings — one construct per rung. Every `.ref` oracle-cut from `fpc -Miso`.

**Verified, not assumed:** `--to 5` PASS 12/12 (the row's own DONE-WHEN floor), `--to 9` PASS 18/20, `--only 0`
alone, `--to N --only N` correctly REFUSEs rc=2, a missing master correctly REFUSEs rc=2, and — matching
seat11's own discipline on the Raku ladder — a corrupt-then-restore proof (hand-broke rung00's `.ref`,
confirmed both modes FAIL, restored, confirmed both modes PASS again) that the instrument catches real
breakage rather than passing by construction.

## Two new defects found while building these (both minted, neither routed around silently)

1. **`rung09_strings` is honestly RED.** ISO 7185's actual string mechanism is `packed array[1..N] of char`
   (`-Miso` rejects Delphi's `string` type outright — confirmed directly, `Error: Identifier not found
   "string"`, before writing the witness). `a := 'foo'; writeln(a)` works; `if a = 'foo' then ...`
   (packed-array-of-char equality) hits SCRIP's "Run-time error 102 / numeric expected" — the same class as
   the already-minted `pascal-fpc-class-runtime-102-numeric-expected`. Isolated precisely (assignment +
   writeln alone passes; only the `=` comparison breaks) before landing the rung, not guessed. Left red
   deliberately — a construct SCRIP does not yet support is exactly what a ladder rung is for.

2. **`set of char` membership is always false — new, minted as `pascal-char-set-membership-always-false`.**
   Found while building the smoke gate's `set_membership` witness: a char-range-for-loop-counting-vowels
   witness diverged from the oracle (SCRIP printed 0, oracle expected 5). Isolated to a 4-line minimal repro:
   `vowels := ['a','e']; if 'a' in vowels then writeln('yes') else writeln('no')` prints `no` (should be
   `yes`). Ruled out char-range for-loops generally (`for c:='a' to 'e' do writeln(c)` prints correctly) and
   ruled out sets generally (`set of 0..9` with integer membership checks — the ladder's own rung08 — passes
   both modes). The smoke gate's own `set_membership` witness was swapped to a small integer set with direct
   `if N in s` checks (matching rung08's proven-safe shape) rather than landing a known-red witness inside a
   floor gate that must never regress — a floor gate stays on proven ground, it does not chase every edge
   found while building it.

**A third, uncharacterized observation, NOT minted:** a larger integer set (`0..20`, 8 elements) combined
with a for-loop accumulator (`for i:=0 to 20 do if i in primes then n:=n+1`) also diverged from the oracle
(8 expected, 6 got) in one construction tried while designing the smoke witness — distinct from both defects
above (int set, not char set; has an accumulator loop, unlike rung08's direct checks). Not isolated further
and not rowed — flagged here so it is not silently lost, but a floor/ladder-building session does not owe a
full investigation of every shape tried and discarded.

## Master suite grew 149 → 159

Fresh `corpus_suite_harness.py run` on the grown master: `total=159 m3_pass=152 m3_fail=6 m3_crash=1` (both
modes identical). The only NEW non-pass is `ladder__rung09_strings` (deliberately red, see above); the other
6 are pre-existing and untouched by this row: `program_procedure_nested_1` (the `deep5` self-diagnosing bomb,
never in any row's scope) and the 5-entry array/packed-comparison regression seat09 is already tracking
separately (`q-pascal-array-packed-regression-post-fleet12-icon-commits`).

## Row disposition

DONE-WHEN met: `test_smoke_pascal.sh` exists and passes, `test_pascal_ladder.sh --to 5` passes, 10
`ladder__rung*` entries in the CSV. `SCORE.md` and `GOAL-TEST-SUITE-CONSISTENCY.md`'s Pascal inventory row
both updated same session. Row's own `## NEXT` names rungs 10+ (pointers/`new`, files as a construct in its
own right, nested procedures + uplevel, `case`, `with`) as real remaining work, same as the Raku sibling row
stayed open past its own rung 9.
