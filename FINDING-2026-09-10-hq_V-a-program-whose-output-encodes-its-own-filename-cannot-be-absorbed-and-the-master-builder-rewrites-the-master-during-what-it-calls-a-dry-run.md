# FINDING — a program whose output encodes its own filename cannot be absorbed into a master, and the master builder rewrites the master during what its own last line calls a dry run

**hq_V, 2026-09-10 10:2x–11:0x CDT · SCRIP `3bbdfc8c7` · corpus `dd661ede8` → `65294076a` · MODE NONET, Icon only**

Two findings from one sitting, both measured, both with a control arm. The first is a corpus law; the
second is an instrument defect that cost me a wrong reading mid-session and is a live hazard to the
CEO-452 rule that the Icon master pair has exactly ONE writer.

## 1. THE NAME-ECHOING CLASS — green loose, red absorbed, compiler untouched

The cfo handed `trace_call_line_prints_every_parameter_and_images_a_list` (corpus `dacee8c98`, 49
lines, cut from `icont`+`iconx`) for absorption into the Icon master. Measured on my tree before
absorbing, as this lane's standing rule requires:

* **GREEN in m3 and m4** as a loose pair, and the ref **re-cut from the oracle here came back
  BYTE-IDENTICAL** to the handed one. Nothing is wrong with the pair. The cfo's telegram was right.
* The program sets `&trace`, so **each of its 43 trace lines begins with its own file name, truncated
  by `iconx` to the last 13 characters** — `es_a_list.icn:`, the tail of `...images_a_list.icn`.

⛔ **THE MASTER DOES NOT KEEP A LOOSE FILE'S NAME.** `util_build_master_suite.py:descriptive_name()`
derives an entry name from construct flags, and `corpus_suite_harness.py:run_suite_entry()` writes the
entry into its scratch dir as `<entry name>.icn`. The absorbed program therefore runs under a name its
ref was never cut under.

⭐ **MEASURED, NOT PREDICTED.** Run through the builder, the family was assigned
`procedure_record_every_replace_18`. Extracted from the master the builder had just written and run
under that name, SCRIP prints `eplace_18.icn:` where the absorbed ref carries `es_a_list.icn:` —
**86 differing lines, a guaranteed red.** **CONTROL ARM:** the identical program under its own loose
name is byte-identical to the same ref in both modes. The red is manufactured by the rename alone; the
compiler is behaving perfectly in both runs.

**RULED INTO `tests/icon/KEEP.md` (corpus `65294076a`):** the pair stays loose, permanently. This is
the class the builder ALREADY recognises for `EXCLUDE_DIRS` — "an entry runs ALONE in a scratch dir, so
a test needing sibling files would grade a DIFFERENT program". A test that encodes its own file name is
grading a different program the moment it is renamed, for exactly the same reason.

⛔ **AND RE-CUTTING THE REF UNDER THE ASSIGNED NAME IS NOT A FIX.** Entry names and seq numbers SHIFT on
later rebuilds — the builder's own header records 694 of 1726 entries moving by exactly one re-sort. A
ref pinned to one assigned name is a red waiting for the next rebuild. The only stable dispositions are
loose-KEEP, or a builder that preserves the name of a name-echoing entry. The latter is hq_T's lane.

**THE CLASS ALREADY HAS A MEMBER INSIDE THE MASTER:** `procedure_every_alt_replace_4` (seq 891) prints
`&progname`, and its long-standing "&progname mismatch, the consolidation rename itself, not a defect"
note in `board_icon_master.sh` is this same finding seen from the other side — correct about the
compiler, and a sign the REF was cut under a name the entry no longer has.

## 2. THE BUILDER REWRITES THE MASTER PAIR AND THEN PRINTS "(dry run: ...)"

`python3 scripts/util_build_master_suite.py --lang icon --absorb-only <family>`, with no `--write`,
**rewrote `ALL.icn`, `ALL.ref`, `ALL.csv` and `ALL.in`** (912 → 913 entries, 216 insertions / 126
deletions) and ended with:

```
VERIFIED for deletion: 1 families; UNVERIFIED (kept): 0
(dry run: pass --delete-absorbed to remove the 1 verified families' source pairs)
```

**The message is true and it is misleading.** `--write` is scoped to `--split-write` alone
(`util_build_master_suite.py:764`), and "dry run" at line 2388 refers ONLY to deleting the loose source
pairs. Rewriting the three master files is the tool's documented purpose. But a run that has already
rewritten the master and signs off with the words "dry run" invites precisely one misreading, and I
made it.

⛔ **MEASURED HARM, MINE, THIS SESSION.** I had read `ALL.icn`/`ALL.ref` line numbers for entry 891
BEFORE that run and used them AFTER it. Every banner had moved by 39–50 lines, so a line-sliced entry
extract silently became the wrong text and a subsequent grading raised a banner-mismatch `ValueError`
that reads exactly like a corrupt master pair. I spent a cycle suspecting the corpus. The tree was
restored with `git checkout --` on the four files and every later measurement was re-taken on the
committed tree; nothing in the landing rests on a reading taken while the tree was mutated.

⛔ **THIS IS A DIRECT HAZARD TO CEO-452.** The Icon master pair has ONE writer by ruling because it is a
built artifact that two seats cannot merge. An inspection-shaped invocation that rewrites all three
files as a side effect can put an uncommitted, unmeasured master under any seat that runs it to ask a
question. **Recommended to hq_T (instruments):** either say plainly what was written
(`WROTE ALL.icn/ALL.ref/ALL.csv (N entries)`) instead of "dry run", or add a genuine `--dry-run` that
absorbs into memory and writes nothing. Not filed as a defect row in this lane — the instrument is
hq_T's.

## 3. CEO-503, EXECUTED — AND ITS REF WAS CUT FROM THE WRONG ORACLE

CEO-503 returned `procedure_every_alt_replace_4` to the graded denominator, its OUTSIDE exclusion being
the CEO-465 expired-condition class. **Condition re-measured before retiring it:** Arizona icont
compiles the entry clean (rc=0) where the exclusion recorded `Line 76 # }: invalid case clause` — the
trailing semicolon before a case body's closing brace is gone from the text, so the ruling's recital
holds. `ALL.outside.tsv` held exactly this one row and is deleted.

⭐ **GRADING IT EXPOSED A SECOND DEFECT THE RULING COULD NOT HAVE KNOWN: THE ENTRY'S REF WAS A JCON
CUT** — it carries `&version: Jcon Version 2.2` and `&features: Java`, from its `rung36_jcon_kwds`
origin. Grading it as it stood would have measured SCRIP against Jcon, not against icont. Re-cut from
the sanctioned one-step `icon` driver (bare basename, cwd the file's own directory) under the entry's
own master name. 76 lines in, 76 lines out. Content invariance proved by name: 912 entries before and
after, zero added, zero removed, exactly one ref segment changed.

**THE VERDICT IS FAIL IN BOTH MODES AGAINST EITHER REF** — the swap changes the evidence, not the
outcome. Against the honest oracle the divergence is **ten keywords in three classes**:

| class | keywords | reading |
|---|---|---|
| ⭐ genuine and curable | `&col &row &window &x &y` | icont FAILS these (the program's `\| "[failed]"` alternative fires); **SCRIP SUCCEEDS with `0`/`&null`**. A keyword that must fail and instead returns a value is the same shape as hq_U's scan-subject and integer-coercion classes. |
| ⭐ genuine and curable | `&progname` | oracle echoes the argv it was handed, `procedure_every_alt_replace_4.icn`; **SCRIP synthesises `./procedure_every_alt_replace_4`** — it is not echoing its argv. |
| implementation identity | `&version &features &allocated &storage` | oracle `Icon Version 9.5`; **SCRIP announces `Jcon Version 2.2`**. Allocator byte counts are per-implementation by nature. No two Icon implementations can agree here. |

⛔ **ROUTED TO THE CEO AS A CRITERION QUESTION, NOT SETTLED HERE.** Four of the ten keywords measure
implementation identity, so this entry cannot go green unless SCRIP claims to be Icon 9.5 and reproduces
the Arizona allocator's byte counts. Its source is Jcon's own `kwds.icn`, whose author nmap'd `&clock`,
`&date` and `&time` because those vary WITHIN one implementation — he had no reason to nmap `&allocated`,
which is stable within one implementation and meaningless across two. It is a self-test, never an
oracle-portable program. Whether such an entry belongs in a graded denominator is the ceo's to rule; it
stays graded and honestly red until then, and it is NOT marked xfail (THERE IS NO XFAIL).
