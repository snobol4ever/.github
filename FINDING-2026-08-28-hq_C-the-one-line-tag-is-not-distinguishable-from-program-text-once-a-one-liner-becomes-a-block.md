# FINDING 2026-08-28 (hq_C) — The suite format's `;* <name>` tag is indistinguishable from program text once a one-liner is promoted to a block. Two defects fixed, a third rowed.

seat02 reported (`convert-cli-reexecutes-existing-entries-corrupts-eval`) that `convert` reprocesses every entry already in the target family and reproducibly corrupted an unrelated already-green one-liner, `ev_fn_beauty_shape`, into a bogus block — twice, with a race ruled out. They declined to guess at a root cause. **Reproduced and root-caused: three independent defects, not one.** Two are fixed (SCRIP `b25fe5e7`); the third is rowed.

## First, the good news: the tool never silently corrupted anything

`convert`'s on-disk re-validation refused every bad merge loudly — *"⛔ ON-DISK RE-VALIDATION FAILED for 8 entries — DO NOT delete originals."* The recipe was unusable, not dangerous. ⭐ **That check is the only reason this was a bug report instead of a corrupted permanent corpus**, and it is why the row that inherits the remainder carries a banner forbidding its relaxation: a check you would have to weaken to let your fix through is the fix being wrong.

## Defect 1 — read-back duplication: 21 entries written, 22 read back

The format's two shapes are distinguished by a sentinel: a format-(A) one-liner **ends with a mandatory `;* <name>` tag**, and `_is_entry_start()` uses that to know where a format-(B) block's body stops. Its docstring states the assumption plainly:

> A block's own body lines are raw, unjoined original statement text and **do not end this way in practice**

⭐ **"In practice" is doing all the work, and re-conversion is what breaks it.** Promote an already-converted one-liner to a block — exactly what merging into an existing suite does — and the promoted line carries its own tag into the block body. `_is_entry_start()` fires on it, so the block gets an **empty body**, and the very same line is then re-read as a one-line entry. The entry comes back **twice**.

Measured on `probe/eval`: 21 entries written, **22 read back**, `ev_fn_beauty_shape` duplicated. That is seat02's "bogus block" precisely — the block is bogus because it is *empty*.

**Fixed:** the line immediately after a banner is consumed unconditionally. A block always has at least one body line, so this is safe for every suite, interleaved ones included.

## Defect 2 — `convert` was not idempotent

`convert_one()` computed `one_line = joined + f";* {name}"` over statements parsed from the original text. When that text was *already* a one-liner, `parse_statements()` kept the existing tag as a trailing comment statement and `join_one_line()` preserved it — so a second tag was appended: `;* ev_fn_literal;* ev_fn_literal`. **Every re-conversion adds another.** Measured: **17 of 21 entries doubled their tag in a single pass.**

**Fixed:** strip our own sentinel before processing, only when the file is a single line whose trailing tag names that same entry — our writer's output, never a hand-authored witness's real last statement.

## Defect 3 — an XFAIL entry does not survive extract → re-convert (ROWED, not fixed)

With 1 and 2 fixed, `probe/eval` re-converts to 21-in/21-out with zero doubled tags, and re-validation **still** refuses. The signature:

```
ev_code_end_label_ctl: orig={m3: CRASH rc=-11, m4: CRASH rc=-11}   suite={m3: PASS, m4: PASS}
```

⭐ **Note the direction — it is the opposite of corruption.** The extracted standalone file *crashes*, correctly, because it is an XFAIL witness; the same entry *passes* inside the suite. The loss is in `extract`, not `convert`. Row `suite-harness-xfail-extract-round-trip`.

⛔ **A trap left in that row's banner, because it cost me time:** several entries report divergence while their verdicts *print identically* (`PASS/PASS` vs `PASS/PASS`). Not a display bug — `behaviorally_equal()` compares **output text** for a PASS and `Verdict.__repr__` omits it. I read the identical reprs as evidence of a comparison bug before checking what the comparison actually reads.

## Bonus defect found while fixing: `write_suite` could emit an unreadable file

A block ends only at the next banner or EOF, so **any one-liner written after a block is swallowed into that block's body.** `write_suite` emitted entries in arbitrary order, so this was live — `probe/eval` survived only because its two blocks happened to be appended last. **Existing suites were correct by accident of ordering, not by invariant.** Now: blocks are emitted last, and `write_suite` asserts the file round-trips rather than writing one that cannot be read back.

## ⭐ The lesson — an in-band sentinel is a bet that your data will never look like your syntax

The format marks entries with a comment the target language already permits anywhere. That is fine while the tag only ever appears where the writer put it, and it fails the moment the writer's own output becomes the reader's input. **Every layer here was individually reasonable**: a mandatory tag, a reader that uses it to find block ends, a converter that appends it. The defect lives in the *composition*, which is why no single function looks wrong under review and why re-conversion — not conversion — is what exposed it.

This is the same shape as the `.xfail` reason-channel gap recorded on `corpus-crosscheck-probe-total-conversion`: **metadata about an entry placed in-band, inside the entry.** The row's own instruction there was to key it as a sidecar exactly like `.in`, and it was right for exactly this reason. ⛔ **The general rule this corpus should adopt: entry metadata belongs in a parallel file keyed by name, never in the entry's own text.** `.in` got this right; the `;* <name>` tag did not, and it took a re-conversion to find out.

**Verification:** `probe/eval` 21-in/21-out, zero doubled tags. Existing suites unchanged (eval 21, opsyn 22, passthru 183, fuzz 54, all FAIL=0). Blocking set green: `test_corpus_snobol4.sh` m3 PASS=1298 FAIL=0 · m4 PASS=1298 FAIL=0 SKIP=0 MISSING=0; `test_gate_emit_no_lang` rc=0; `test_gate_template_medium_invisible` rc=0.
