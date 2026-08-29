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

---

## AMENDMENT (same day) — I TOOK THE SWEEP. THREE MORE GATES, AND THE WORST HID 1583 LINES

The body above closed with *"worth a sweep, not taken here… I found this by arithmetic, not by looking for it, which suggests nobody has looked."* I looked. Searched `test_gate_*` / `board_*` / `audit_*` for a `head -N` (N≥5) applied to a **listing**, in a script that admits truncation **nowhere**. Most of the tree's 234 `head -N` uses are legitimate samples and were left alone. Three were this defect:

| gate | count it prints | list cap | hidden today |
|---|---|---|---|
| **`test_gate_no_lang_names.sh`** | `$N` = **1623** | 40 | **1583 — LIVE** |
| `test_gate_zdp_on_null.sh` | `total/movers/self-nondeterministic` | 20 & 40 | latent |
| `test_gate_s130_blast.sh` | `TOTAL=$n MOVERS=$d` | 40 | latent |

All three now name their cap and print the full-list command. **`GATE_LIST_ALL=1` is the fleet-wide spelling**; `test_gate_suite_conversion_complete.sh` accepts it alongside its original `SUITE_GATE_LIST_ALL`. Landed SCRIP `53add566`.

### ⚠️ AND AN HONESTY CORRECTION ON MY OWN HEADLINE NUMBER

**1583 is not 1583 people were misled by.** `test_gate_no_lang_names.sh` is **wired nowhere** — `grep -rln` finds it referenced only by itself and by GOAL/FINDING prose. It is the dormant **structural** LI-FENCE gate for the unfinished language-independent de-name rung (`GOAL-RUNTIME-RENAME.md`, `GOAL-RUNTIME-REORG.md`), and it is a *different file* from the blocking-set behavioural gate `test_gate_emit_no_lang.sh`, which is in the Makefile and passes `rc=0`. So the 1583 were hidden from **whoever next picks up that rename rung**, not from a live gate anyone runs today.

That distinction matters and I nearly shipped without it: "a gate hiding 1583 violations" and "a dormant gate that will hide 1583 violations from the next person to run it" are different claims, and only the second is true. The fix is worth the same either way — a rung is picked up by someone eventually, and they would have started from a 40-line view of a 1623-line problem.

### THE SHAPE, NOW THAT THERE ARE FOUR

Four instances, all independently written, none by a careless author:

- a count and a list, in the same output, disagreeing;
- the count always right, the list always a prefix;
- **no instance printed anything false** — each merely printed *less* than it counted;
- and in every case the closing instruction (*"convert them"*, *"add them to the ALLOW list"*) refers to a **them** the reader believes they can see.

⭐ That last point is the real mechanism and it is worth stating separately: **a truncated list plus an imperative naming it turns a display bug into a scoping bug.** The reader does not merely see less — they form a plan sized to what they saw. Every one of these gates told someone to go fix a set, and showed them a prefix of it.

**The rule this argues for, unchanged and now four-witnessed:** any output that prints both a count and a list must make the two agree, or say why they do not. It is one line per site and mechanically checkable.
