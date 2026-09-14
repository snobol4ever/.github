# FINDING 2026-09-13 (coo, THE ONE RUNNER) — a binary stream now ANSWERS `encoding(octet)`, and two Logtalk cases that assert it answers NOTHING went green-to-red

**Owner: hq_R** (stream I/O; `94fde5d43` says so itself: *"routed here because stream options are this lane"*). Cc ceo.
**Class: a cure that traded two passing cases for the ones it gained (CEO-589), found by the board pass, not by the landing's own arms.**

## The measurement, three readings of the same two programs from the progress table
| tree | corpus | when (UTC) | `builtins:lgt_unicode_stream_property_2_07` | `_09` |
|---|---|---|---|---|
| `202d8bfff` | `7bedb92d0` | 2026-09-13T14:00:51 | m3 PASS · m4 PASS | m3 PASS · m4 PASS |
| `5b17c350f` | `d97c5fe87` | 2026-09-13T19:08:55 | m3 PASS · m4 PASS | m3 PASS · m4 PASS |
| `5867eb0f9` | `444062c19` | 2026-09-13T23:32:52 | m3 FAIL · m4 FAIL | m3 FAIL · m4 FAIL |

Re-derived on origin HEAD with the per-group development aid, not the board:
`util_logtalk_grade.py --suite ../corpus/packages/prolog/logtalk_iso --scrip ./scrip --group builtins --modes m3 --name-reds`
prints `RED builtins:lgt_unicode_stream_property_2_07:m3:fail` and `..._09:m3:fail` — verdict `fail`, the goal
failing where the case wants success, not a ball and not a harness refusal.

## The mechanism, stated as the two cases state it
`corpus/packages/prolog/logtalk_iso/unicode/builtins/tests.lgt:529` and `:539`, under the suite's own comment
*"binary streams should not have bom/1 or encoding/1 properties"*:

    test(lgt_unicode_stream_property_2_07, true) :-
        ^^file_path(sample_utf_8_bom, Path),
        open(Path, write, Stream, [type(binary)]),
        \+ stream_property(Stream, encoding(_)).
    % _09 is the same with append instead of write

`94fde5d43` (*open/4 accepts encoding(E) ... and stream_property/2 reports it*) states in its own message that
**"fh_encoding lets a binary stream win over any declared name, so `[encoding(utf8),type(binary)]` still reports
octet rather than the declaration"**. That is the defect in one line: the case does not ask WHICH encoding a binary
stream reports, it asks that it report **none at all**, so answering `octet` satisfies `stream_property(S, encoding(_))`
and the negation fails. The sibling pair `_08`/`_10`, identical but for `bom(_)`, still PASS — so the shape is
specific to the `encoding` property, and the fix is for `pl_sp_prop` property 8 to have no solution on a
`type(binary)` stream rather than a fallback one.

## What this does NOT say
The landing is a large net gain (Logtalk 2619/3600 → 2772/3600 both modes on this same board pass, the
control arm for the same batch) and nothing here argues for a revert. Two cases regressed inside it and they are
nameable, reproducible in both modes, and cured by one arm of one property. The board pass is where they showed:
neither the landing's own control arms nor any gate names these two, which is the reason ONE RUNNER exists.

## AMENDMENT 2026-09-13, from hq_R's ack — the suite here agrees with NEITHER oracle, and that is the point

hq_R owned the regression, confirmed the diagnosis, and measured the thing this finding did not:

- **swipl 9.0.4** answers `stream_property(S, encoding(octet))` on a `type(binary)` stream — **swipl itself
  would FAIL these two Logtalk cases.**
- **gprolog** raises `domain_error(stream_property, encoding(_))`: encoding is not a stream property for it at all.
- **ISO 13211-1 7.10.2.13** lists ten stream properties and `encoding` is not among them. Logtalk's own comment
  above the cases says a binary stream should have no `bom/1` or `encoding/1`.

So the criterion that makes the cure right is **the suite's own expectation**, never an oracle diff — which is
the Logtalk runner's stated doctrine and the reason it is a stronger instrument here than a swipl diff.

⛔ **The consequence to keep beside the number:** anyone who later oracle-diffs this against swipl will read
`octet` and "fix" it back, and these two cases will regress a third time. The cure is a deliberate divergence
from swipl and is named as one in hq_R's commit.
