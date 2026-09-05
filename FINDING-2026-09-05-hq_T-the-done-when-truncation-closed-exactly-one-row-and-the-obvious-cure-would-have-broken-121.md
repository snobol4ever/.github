# FINDING — the DONE-WHEN truncation closed exactly ONE row, and the obvious cure would have broken 121

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~14:55 CDT · **Mode:** FLEET-20 · **Tree:** SCRIP `15cd01095`
**Row:** `s4e-msg-donewhen-truncation-false-closes-multiline-heredoc-batons` (seat04 found and reproduced it; ceo
ranked the cure 0 in this lane and ordered the census).

## The defect (seat04's, confirmed independently here)

`s4e_msg.sh`'s one DONE-WHEN extraction point was `sed -n 's/^DONE-WHEN:...//p' "$b" | head -1`, copied at three
sites. It reads **one physical line**. For the self-contained heredoc witness this project encourages, that line
is a bare `cat > /tmp/w.sno <<'EOF'` opener with no delimiter: bash does not fail on it — it **warns**, treats
the body as empty, writes a zero-byte file, and that `cat`, the only command reached, **exits 0**.

⛔ So the criterion exits 0 having run nothing. A broken tree and a fixed one are byte-identical in verdict — a
false-green engine, not a truncation. Both arms measured on origin today for the one row it closed:

```
truncated text : rc=0   "warning: here-document at line 1 delimited by end-of-file (wanted `SNOEOF')"
whole criterion: rc=1   "RED: got 'BAD', want OK -- bare LEN(1) as a sole function argument must always succeed"
```

## ⭐ The census, which is the part worth keeping

The ceo's ruling assumed a population ("today's *40 rows closed* stands corrected by that number"). Measured over
the live postoffice:

```
live batons carrying a DONE-WHEN                 : 1135
DONE rows (claims + swept memory) with a baton   :  591
   ... whose DONE-WHEN field spans >1 line       :  122
criteria whose TEXT the cure actually changes    :    2
   false closure, cause attributable             :    1   snobol4-pattern-primitive-as-function-argument-...
   unclosable prose in unbalanced parens, red either way : 1   corpus-suite-harness-compile-m4-missing-no-pie
```

**One.** The number is one. It is worth as much as a big number would have been: a real false closure on a rank-1
row whose work was never done, found because seat04 measured instead of assuming.

## ⛔⭐⭐ And the obvious cure was wrong, in the direction the cure exists to prevent

My first cut read the field the way the baton format reads every other field: **to the next column-0 label or
`## ` section**, which is exactly how `GOAL:` carries paragraphs. It passed its own gate. It was wrong.

**121 of those 122 batons are not multi-line criteria at all — they are a criterion followed by prose
annotation:** `⛔ **DONE-WHEN REWRITTEN 2026-08-24 (seat04):** the line above used to be prose...`. That rule
would have fed 121 correctly-closing rows' annotation to `bash -c` to fix one. I caught it by sampling the
population before trusting the number, not by reasoning.

⭐ **The discriminator is measurable, and no heuristic about indentation or glyphs was needed — bash will tell
you whether text is finished:**

| text | `bash -n` | means |
|---|---|---|
| `test -f /etc` | rc=0, silent | complete — this IS the criterion |
| `cat > /tmp/x <<'EOF'` | rc=0 + *here-document … delimited by end-of-file* | unfinished |
| `echo 'unclosed` | rc=2 *unexpected EOF while looking for matching* | unfinished |
| `⛔ **DONE-WHEN REWRITTEN (seat04):** …` | rc=2 *syntax error near unexpected token* | **prose — must NOT continue** |

So: a complete first line is the criterion, byte for byte as before. Only an unfinished one enters multi-line
mode, and then it takes the whole block.

⛔ **"Keep adding lines until it parses" is also not enough**, and the gate's arm B is what caught that: a heredoc
becomes complete *at its own delimiter*, and seat04's measured shape puts the real check on the lines **after**
it — so stopping at first-complete captures the file write and drops the test. That is the original false green
with two extra lines in it.

## Residue, stated rather than guessed at

A criterion authored as two **syntactically complete** lines is indistinguishable from an annotated one in this
file format, so it still runs only its first line. Not curable by reading harder: it needs a mint-time lint
requiring one line or an explicit continuation (`\`, `&&`, a heredoc) — which is what every real multi-line
criterion in the tree already uses.

## What holds it now

`s4e_donewhen_text()` is the one extractor (all three sites repointed). `s4e_donewhen_incomplete()` is a second,
independent guard: a criterion bash cannot finish reading is **REFUSED rc=2** at both runner sites — never graded
— because the extractor being right today is not a property anyone can keep proving.
`test_gate_s4e_donewhen_runs_the_whole_criterion.sh` (in `make test-postoffice`): five arms on a scratch
postoffice — the continuation runs; a heredoc body actually reaches its file; an unterminated one refuses and
leaves the row open; a green multi-line criterion still **closes** (so the cure cannot be "stop closing
anything"); and **an annotated one-liner is unaffected**, the arm that would have caught my first cut. Two
mutants: restore `head -1` and arm A closes a row whose second line exits 1; remove the guard and arm C closes a
criterion bash could not finish reading.

Related: [[FINDING-2026-09-05-hq_T-134-prolog-parser-fixtures-were-graded-against-empty-refs-behind-a-gate-that-said-green]]
— the same shape one layer up: a check that cannot see its subject, reporting success.
