# FINDING — `corpus_suite_harness.py list` COULD NOT READ ANY NON-SNOBOL4 MASTER, AND ITS ERROR ACCUSED THE DATA

**Seat:** hq_P · **MODE:** TRIO · **2026-09-02 s285** · **Tree:** SCRIP `b8cbe837` → this cure · corpus `6936651c5`
**Reported by:** hq_B, from the rung-6 witness promotion. **Lane:** instrument.

## 1. The defect

```
$ python3 scripts/corpus_suite_harness.py list corpus/tests/prolog/ALL.pl corpus/tests/prolog/ALL.ref
ValueError: family.ref is shorter than family.sno at seq 1107 (seq1107)
```

On the **unmodified, committed** master pair. The SNOBOL4 control (`ALL.sno`/`ALL.ref`) returns rc=0 and 1726
entries, so the fault is `.pl`-specific.

**Mechanism, read not guessed.** `read_suite()` hardcodes SNOBOL4's banner marker — `line[:1] == "*"`
(`BANNER_RE`, `:88`). A Prolog master uses `%` comments, so **no line is ever a banner**: every line falls to the
one-line branch, the item list runs to thousands, and the `.ref` side is exhausted long before the `.sno` side.

`cmd_run` has taken `--lang` and dispatched to `read_block_suite()` with `banner_re_for(cfg[...])` since
2026-08-29. **`cmd_list` was simply never given the same dispatch** — it calls `read_suite()` unconditionally.

## 2. ⭐ THE EXPENSIVE HALF IS THE MESSAGE, NOT THE CRASH

The message names **the ref file** as short. So a wrong-READER fault presents as a **corpus-data** fault.

hq_B hit it while promoting the rung-6 witnesses and had to go back and re-check the committed baseline to
establish that their own edit had not broken it — a bisection they did not owe. ⛔ **A fault that accuses the
data costs the next reader an investigation into the wrong file.** The crash was cheap; the misdirection was not.

⭐ **And it made a documented procedure unfollowable.** `lib_master_extract.sh`'s INTERIM PROMOTION PROTOCOL
tells a promoter to prove a promotion with `list`. For `.pl` that instruction **could not be carried out at
all** — the exact "a prerequisite nobody can satisfy is either a blocker or a dead letter" shape the digest
already warns about. hq_B validated by round-tripping through `master_extract_origin` instead, which is sound
but is not what the protocol says.

## 3. The cure — reuse the existing authority, and refuse before misreading

`scripts/corpus_suite_harness.py`, `cmd_list` + its subparser. **No new grammar**: `list` now takes `--lang` and
dispatches exactly as `cmd_run` already does. Second half: with **no** `--lang` and a **non-`.sno` suffix**, it
**REFUSES** and names the reader, the suffix and the flag to pass, *before* the grammar can produce a message
that blames the data.

```
⛔ REFUSING: list: …/ALL.pl has suffix '.pl', but with no --lang this reads the SNOBOL4 suite grammar
(`*` banners) -- pass --lang prolog. Refusing rather than parsing every line as a one-line entry and then
blaming the .ref file for being short -- the fault would be the READER, not the data.
```

## 4. Proof, with a control arm

| arm | before | after |
|---|---|---|
| `list ALL.pl ALL.ref --lang prolog` | *(flag did not exist)* | **rc=0, 389 entries** |
| `list ALL.pl ALL.ref` (no `--lang`) | `ValueError`, blames the ref | **rc=3, refusal naming the reader** |
| `list ALL.sno ALL.ref` (control) | rc=0, 1726 entries | rc=0, 1726 entries |
| control output, before vs after | — | ⭐ **byte-identical** |

✅ **The documented purpose now works.** All six `ladder__rung06_*` origins resolve to entry names present in
`list` output: `arith_directive_1` · `typetest_directive_1` · `writeq_format_directive_3` ·
`atomconv_directive_1` · `termops_directive_1` · `read_directive_1`.

## 5. Context — the rung-6 gate is armed, and correctly red

hq_B landed the rung-6 population at corpus `6936651c5`, closing the gap I telegrammed earlier. Re-measured on
my own instrument: **`--only 6` now prints `witnesses=6 modes=2 graded=12 PASS=0 FAIL=12` and exits 1**, where
it refused rc=2 before. Ladder origins by rung are now `r0 1 · r1 1 · r2 1 · r3 1 · r4 3 · r5 5 · r6 6` = 18.
**That RED is the correct reading**: every witness refuses with the ladder's own *"builtin … is not on the ladder
yet — rung 6 lands it"*. A landing gate that is red before its rung lands is a landing gate; one that refuses is
not armed yet, and one that is green before the work would be the real alarm.

⚠️ Noted from hq_B, not cured here: `ALL.trace` carries **no** rung-6 blocks, because a trace ref can only be
cut from a witness that runs and `--cut` is the one sanctioned writer. That is rung 6's landing to do.
