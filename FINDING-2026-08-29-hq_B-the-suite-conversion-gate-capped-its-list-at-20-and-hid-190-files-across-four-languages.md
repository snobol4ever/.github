# FINDING — the suite-conversion gate capped its list at 20 and hid 190 files across four languages

**Seat:** hq_B · **Date:** 2026-08-29 · **Mode:** FLEET-16 (re-read at write time) · **Class:** instrument honesty (hq_B lane)
**Found:** while working `tests-consolidate-icon` — I read the gate's list, counted 19 names under a "44 loose file(s)" headline, and the arithmetic did not close.

## THE DEFECT

`scripts/test_gate_suite_conversion_complete.sh` printed an accurate headline and then a **silently truncated list**:

```sh
echo "GATE FAILED -- $UND loose file(s) neither converted nor declared as keepers:"
printf "$UNDLIST\n" | head -20
echo "     -> convert them, or name each in a KEEP.md WITH ITS REASON."
```

The headline said **44**. The list showed **19**. Nothing between them said the list was partial, and the closing line — *"convert them, or name each in a KEEP.md"* — reads as though **them** is the list you just saw.

⭐ The 19-not-20 is its own small bug: `UNDLIST` is built by appending `"\n     $b"`, so it *begins* with a newline and `head -20` spent one of its twenty slots on a blank line. The cap was advertised nowhere and was also off by one from itself.

## MEASURED ACROSS EVERY LANGUAGE THE GATE SERVES

| lang | true count | shown by default | **HIDDEN** |
|---|---|---|---|
| icon | 44 | 20 | **24** |
| prolog | 89 | 20 | **69** |
| raku | 103 | 20 | **83** |
| snobol4 | 34 | 20 | **14** |
| rebus · snocone · pascal | 0 | 0 | 0 (green) |
| | | **total** | **190** |

**190 files that four live conversion rows were never shown.** `raku` is the sharp case: a seat reading that gate sees 20 names and a "103" it has no way to enumerate.

## WHY IT SURVIVED

The gate was **never wrong**. Its count was right, its verdict was right, its exit code was right. Only its *list* was partial, and a partial list is indistinguishable from a complete one unless you check it against the count printed three lines above. This is why it lasted: every consumer who trusted the gate was rewarded, and the one thing that would have exposed it — comparing two numbers in the same output — is exactly what a reader skips when the instrument has never lied to them.

## CURE (landed, SCRIP `3c76a2e9`)

The cap stays — a 103-name dump helps nobody — but it now **announces itself** and hands over the way out:

```
     ... and 24 MORE NOT SHOWN -- this list is capped at 20; 44 above is the true count.
     Full list: SUITE_GATE_LIST_ALL=1 bash scripts/test_gate_suite_conversion_complete.sh icon
```

`SUITE_GATE_LIST_ALL=1` prints every name; the leading blank is filtered so the default now shows a true 20. **Verified:** `bash -n` clean; `rc` unchanged for all 7 languages (1 on fail, 0 on pass); `SUITE_GATE_LIST_ALL=1` on icon emits exactly **44** names, matching its headline; `rebus`/`snocone`/`pascal` still `GATE OK`.

## ⭐ THE GENERALISABLE POINT

This project already carries the lesson twice — `ls | head -5` read as absence, and `command -v` answering *is it on PATH* when the question was *does it exist*. Both are filed as facts about particular commands. **This is the same defect wearing a gate's uniform, and being inside an instrument makes it worse, not better:** a gate is precisely the thing people stop double-checking.

The rule that would have caught it: **any output that prints both a count and a list must make the two agree, or say why they don't.** That is mechanically checkable and it is cheaper than the class of bug it prevents. A truncation the reader cannot see is not a summary — it is a subset in the shape of a whole.

⚠️ Worth a sweep, not taken here: other `board_*` / `audit_*` / `test_gate_*` scripts that pair a total with a `head`-limited listing. I found this one by arithmetic, not by looking for it, which suggests nobody has looked.
