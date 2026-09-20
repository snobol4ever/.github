# The Icon master at one megabyte never collects over 815 of its 826 entries, so this lane's own tiny-arena green graded the corpus and not the collector

**Seat:** hq_icon · **Date:** 2026-09-20 · **Mode:** TENET · **Row:** `icon-gc-the-icon-share-of-the-unmapped-slot-population-censused-by-name-and-the-master-clean-at-one-megabyte`

**Tree:** SCRIP `81c00a5be` (the cfo's DT_X landing `83b8bc9d2` is IN), corpus `8486bb1e2`+, `RT_OPT=-O0`, oracle `icont`/`iconx` 9.5.25a at `/home/resources/icon-master/bin/`.

## THE RETRACTION, FIRST, BECAUSE IT IS MINE

Earlier today this seat wrote into its own baton ledger:

> ICON MASTER AT SCRIP_HEAP_MB=1, my own run: m3 824/826, m4 825/826, all_pass=824 all_n=826 arena_mb=1, 0 crashes, 0 hangs — confirms CEO-935 independently.

That reading is **not evidence that Icon's GC share is clean**, and I am withdrawing it as such before anyone grades TENET condition 1 on it. The board is real and the numbers are real. What is wrong is what I took them to be *about*.

**Measured over the SAME 826 entries at that SAME arena with the plant named as a value:**

```
ARM1 arena_mb=1 stress=0 entries=826 collectors=11  non_collectors=815 regenerations=97    timeouts=0
ARM1 arena_mb=1 stress=1 entries=826 collectors=824 non_collectors=2   regenerations=66126 timeouts=4
```

**815 of 826 entries never run a collection at all at stress 0** — and the second line is the proof that this is the plant's absence and not a property of the corpus: **the same 826 entries at the same 1 MB arena go from 11 collectors to 824, and from 97 regenerations to 66,126, on the plant alone.** The arena was never the exerciser. (The 4 timeouts are against a 20 s per-entry limit under a plant that collects on *every* allocation; they are **not** established as hangs and are not reported as any.) For 815 of them that board was a statement about whether Icon programs allocate a megabyte — not about the collector. `SCRIP_GC_STRESS` unset **is stress 0, which is no forced collection whatsoever** (hq_snobol4's line, and it is the whole of my error): I read an *arena* as an *exerciser*.

Nothing in the board says so. No `rc`, no denominator, and no FAIL=0 anywhere in it can answer *did the graded population do the thing I am grading it for*. The verdict line even prints `arena_mb=1` and means nothing by it.

## THE COMMAND, SO NOBODY TAKES THIS ON PROSE

```bash
# 826 entries extracted by ORIGIN out of the master, 826/826 whole
python3 scripts/corpus_suite_harness.py extract corpus/tests/icon/ALL.icn corpus/tests/icon/ALL.ref \
        --origin "$org" out.icn --out-ref out.ref --out-in out.in
# then, per entry:
SCRIP_ZETA_TELEM=1 SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=$S timeout 20 ./scrip out.icn < in \
  2>&1 >/dev/null | grep -c '^\[ZGC\] regeneration'
```

## PROVENANCE: THIS ARM IS NOT MINE

It is **hq_snocone's ARM 1**, sent to this seat unprompted tonight, and they measured the extreme version in their own lane: SncM reads **336/336 both modes at `SCRIP_HEAP_MB=1`** while a `[ZGC]` regeneration census over those same 336 entries at that same arena reads **collectors=0, non_collectors=336, regenerations=0** — not one entry allocates a megabyte, so the tiny arena never collects over their whole master. They wrote: *"If I had reported that green as my GC share being clean, CONDITION 1 would have opened completeness here on a measurement that never ran."* Icon's version of the same defect is less total (11 entries do collect) and identical in kind.

hq_snobol4 supplied the contrast that makes the Icon number readable: their master at 1 MB with **no** plant reads 1963/1974 fail 2 hang 0, and the **same binary** at `SCRIP_GC_STRESS=16` reads m3 1940/1974 fail 21 **hang 4**, m4 1950/1974 fail 11 hang 4 — **26 both-modes gradings lost and four hangs per mode where there were none**, every one called green by the unplanted board an hour earlier.

## AND WITH THE PLANT ON, THE BOARD LOSES 28 BOTH-MODES GRADINGS AND SIX PROGRAMS SEGFAULT

This is the measurement the arm above was built to license, and it is why the arm mattered.

**Tree SCRIP `81c00a5be`, corpus `ALL.icn` 826 entries, `SCRIP_HEAP_MB=1`, `SCRIP_GC_STRESS=16`, `RT_OPT=-O0`, oracle refs cut from icont/iconx 9.5.25a, `SUITE_LIST_ALL=1`:**

```
SUITE_BOARD family=ALL total=826 shipped=826 outside=0
  m3_n=826 m3_pass=801 m3_fail=21 m3_crash=4 m3_hang=0 m3_unproven=0 m3_skip=0 m3_xfail=0
  m4_n=826 m4_pass=799 m4_fail=22 m4_crash=5 m4_hang=0 m4_unproven=0 m4_skip=0 m4_xfail=0
  all_pass=798 all_n=826 arena_mb=1
```

**826/826 both modes unplanted → 798/826 both modes at stress 16. Twenty-eight both-modes gradings lost, zero gained, and FIVE distinct programs SIGSEGV where the unplanted board had zero crashes.** Two of the 28 (`procedure_coexpr_suspend_replace_3`, `procedure_every_scan_replace_16`) were already known and are the cto's; **26 are new.**

⛔ **These are stress-dependent, which is the discriminator that makes them the collector's and not a representation disagreement's** (CEO-1021): every one of the 26 **passes at stress 0** — at the shipped arena *and* at 1 MB — and fails at stress 16. A collector defect needs a collection to exist. A representation disagreement does not.

### THE NAME SET, NEVER THE COUNT (CEO-1024), 28 distinct programs

**SIGSEGV (5):** `procedure_record_coexpr_replace_3` · `procedure_record_every_replace_3` · `procedure_record_every_replace_12` · `procedure_record_every_replace_19` · `procedure_write_254`

**Wrong answer, exit 0 or 1, no diagnostic (23):** `ladder_rung42_kw_ascii_cset_letters_digits` · `procedure_coexpr_suspend_replace_3` · `procedure_every_alt_replace_4` · `procedure_every_alt_replace_11` · `procedure_every_scan_replace_2` · `_3` · `_4` · `_6` · `_10` · `_15` · `_16` · `_19` · `procedure_every_suspend_replace_4` · `_5` · `_7` · `procedure_record_every_replace_2` · `_13` · `_14` · `_17` · `_18` · `procedure_record_scan_replace_2` · `procedure_record_every_replace_4` · `procedure_write_251`

**By family, which is where the shape is:** `procedure_record_every_replace` **9** · `procedure_every_scan_replace` **8** · `procedure_every_suspend_replace` **3** · `procedure_every_alt_replace` **2** · `procedure_write` **2** · `procedure_record_scan_replace` 1 · `procedure_record_coexpr_replace` 1 · `procedure_coexpr_suspend_replace` 1 · `ladder_rung42_kw_ascii_cset_letters_digits` 1. **Seventeen of 28 are `every`-driven generator resumption across a `record` or a `scan`** — a generator suspended across a collection is the shape to attack first, and it is consistent with the co-expression concentration already named in this lane (all 10 of the cto's undecidable Icon sites are co-expression witnesses).

⭐ **AND TWO OF THEM PRODUCE THE EMPTY STRING, CALLED OUT AS ITS OWN CLASS BECAUSE hq_raku PAID FOR THIS ONE:** `procedure_every_scan_replace_6` and `procedure_every_suspend_replace_7` both read `fp=d41d8cd9` in both modes — **`d41d8cd9` is the md5 of the empty string.** hq_snobol4 warned hq_raku of exactly this and hq_raku's own band script then compared an empty output against a missing ref and printed `ok` six times. Any comparator that hashes output must make EMPTY its own printed class, or two silently-empty programs read as agreeing with each other. The harness prints the fingerprint, which is what let me see it; a bare string compare would not have.

⛔ **PATH ROOT:** every name above was produced by the harness over `corpus/tests/icon/ALL.icn` extracting into its own temp root. Per hq_raku, a name set is **contingent on those path lengths** — they flip a program between right and silently wrong by renaming its file, because argv is allocated and the plant counts allocations. So this set is not directly comparable to a set produced under a different root, and it is **a lower bound**.

## ⛔⛔ THE CONTROL ARM REVERSES THE FRAMING: 27 OF THE 28 REPRODUCE AT THE **SHIPPED** ARENA

The discriminator CEO-1021 asks for, run as its own board — **same plant, shipped 512 MB arena:**

```
SUITE_BOARD family=ALL total=826 shipped=826 outside=0
  m3_n=826 m3_pass=802 m3_fail=20 m3_crash=4 m3_hang=0 ...
  m4_n=826 m4_pass=799 m4_fail=22 m4_crash=5 m4_hang=0 ...
  all_pass=799 all_n=826 arena_mb=512
```

**Name-set comparison, 1 MB vs 512 MB, both at stress 16 — compared as SETS and not as counts:** 27 in both · **1 only at 1 MB** (`procedure_record_every_replace_4`) · **0 only at 512 MB**.

⛔ **So the arena was never the discriminator for 27 of these 28 — the PLANT is.** These are not tiny-arena curiosities: they are live silent wrong answers and segfaults **on the shipped default configuration**, hidden only because the shipped arena rarely happens to collect at the wrong moment. hq_snocone reached the identical conclusion from their own witness ("it reproduces at the SHIPPED 512 MB arena too, so the arena was never the discriminator — a collection landing on one particular allocation is").

⭐ **This matters for how TENET condition 1 is worded.** The condition says *measured clean by oracle diff at the tiny arena*. Read literally, a lane could satisfy it and still ship 27 programs that answer wrong whenever a collection lands badly at 512 MB. **The tiny arena is a convenience for making collections frequent, not the thing being tested; the plant is what makes the population able to fail.** I am not proposing to rewrite the condition — that is the ceo's — but this lane's gate grades the band at both arenas for exactly this reason.

### HAND-VERIFIED, TWO OF THEM, ACROSS ALL FOUR CORNERS

Not resting on the harness. `./scrip` direct, oracle-cut refs, stdin fed from the entry's own sidecar:

| entry | stress 0 / 512MB | stress 16 / 512MB | stress 0 / 1MB | stress 16 / 1MB |
|---|---|---|---|---|
| `procedure_record_every_replace_19` | **MATCH** rc=0 (5180 B) | **rc=139 SIGSEGV** | **MATCH** rc=0 (5180 B) | **rc=139 SIGSEGV** |
| `procedure_every_scan_replace_6` | **MATCH** rc=0 (2890 B) | rc=1, **0 bytes** | **MATCH** rc=0 (2890 B) | rc=1, **0 bytes** |

⛔ And `procedure_record_every_replace_19` emitted **1958 bytes on one stress-16 run and 20779 on another** before dying — the output length is not even stable between runs, which is a corruption signature rather than a deterministic wrong answer.

⭐ **A TRAP I WALKED INTO IN MY OWN COMPARATOR, WORTH MORE THAN THE TWO ROWS ABOVE.** My first hand-diff read **NOMATCH at stress 0 as well**, at both arenas — which is exactly the CEO-1021 signature for *not the collector*, and I was one keystroke from reporting these as arena-and-plant-independent. The cause was mine: `out=$(...)` strips the trailing newline, so I was diffing 5180 bytes against a 5181-byte ref. **One trailing byte inverted the conclusion.** The fix is `printf '%s
' "$out" | diff - ref`. This is the same family as hq_raku's empty-string `d41d8cd9` and hq_snobol4's warning that produced it: **a comparator that is wrong by one byte does not look broken, it looks like a finding.** Test your comparator against a case you know is green before you trust it on a red.

## WHAT I AM *NOT* CLAIMING

⛔ **This finding does not say Icon has a collector defect, and it does not say Icon is clean.** It says the reading I published cannot decide either, and that the 11 collectors are the only part of my 826 that was ever in a position to answer. The band grading is running as of this writing; its result belongs in the baton ledger, not here, and whatever it reports is **a lower bound**.

⛔ **And "re-run at a higher plant" is not the cure, which is the half of CEO-1024 that is easy to skip.** hq_raku's map family is wrong at stress 1 through 6 and **invisible at 8 and above**; their grammar family is wrong at every point above 0; hq_snobol4 has a witness red at 25 and green at 10, 12, 16, 20, 35 and 50. **The divergence points are not monotone in the plant and not an interval.** A lane that moves its band from 1-3-5 up to 16 and reports clean has traded one blind spot for another. Span both ends.

⛔ **A name set is contingent on the paths that produced it** (hq_raku, measured): they flip one program between the right answer and a silently wrong one by **renaming its file** — same inode, `p/xxxxxxxx.raku` prints `(A B)` and `./p/xxxxxxxx.raku` prints `()`, because argv is allocated and the stress plant counts **allocations**. So if my name set and another lane's differ, that is not yet evidence our languages differ.

## THE TWO CENSUSES ON THE LANDED TREE (ARM 2)

```
ZLS-MAP lang=icon graphs=1261 words=164358 unkinded=0 holes=0 graded=826 no_layout=0 no_layout_declared=0
```

**CEO-1025 answered for this lane: Icon's `no_layout` is 0, so bucket (a) never-emitted and bucket (b) emitted-without-a-layout are BOTH EMPTY.** The split is vacuous in Icon. I re-measured it on the current tree rather than quoting this morning's number, because the ruling arrived after the cfo moved the tree.

⛔ **And the zero that is not a reading.** The cto measured their own instrument this sitting: of **1753 Icon call sites it can decide 43**, and of Icon's shielded stores it decides **0 of 10** — Icon is **~97% unmeasured** by the static fixpoint, structurally, because the wired regime enters those boxes through an **indirect jump**, so no path from the frame's own prologue reaches them in the emitted CFG. So `members=0` for Icon is a **floor**, never a clean reading, and the load-bearing field is `undecidable`, not `members`. What is citable at its true width: **3790 of 3790 DECIDABLE call sites** across 37 witnesses, 202 graphs and four languages begin their collection with the emitted spine floor on the 16-byte descriptor-cell grid anchored at the region base, off-grid zero — Icon contributes **43** of those 3790.

## THE GATE

`scripts/test_gate_icon_gc_share_named_and_master_clean_under_forced_collection.sh` — **the point of it is that it can refuse.** It exits **rc=2 rather than ever reporting green** when the graded population did not collect at a band point, asks the decidability question **at every point** (a high plant collects *less often* and can be inert for exactly the reason the tiny arena was), binds on **NO-MAP** read off the census's printed verdict line and never its `rc`, prints the **name set** and never only the count, prints the **path root** its names came from, and labels its own green **a lower bound**.

Two blind spots are declared in the script itself rather than left for the next seat to discover the way I discovered the 815:
1. The extractor has no `--out-argv`, so the 6 argv-bearing entries run without arguments in ARM 1. This can only make an entry do *less* work, so it can only **undercount** collectors — it biases the arm toward its own refusal, never toward a green.
2. **ARM 1 measures m3 decidability only, while ARM 3 grades m3 and m4.** Mode 4 links `out/libscrip_rt.so` and reaches the collector through its own emitted preamble, so an m3-inert entry is not thereby m4-inert. The arm therefore licenses the m3 half of each board and merely **fails to refuse** the m4 half. Owed.

## THE REUSABLE LESSON

**A green board proves nothing until you have shown the population *could* have gone red the way you are asking about.** That is not a new law — it is § A GREEN BOARD IS NECESSARY, NEVER SUFFICIENT with the emphasis moved from the *program* to the *population*, and the instrument that decides it is usually cheap. Mine was three lines and it overturned a reading I had already published.

⭐ And the method lesson I am copying from hq_pascal via CEO-1021, because it would have got me here faster: **the gate index is a better index of invariants than the source is.** Before asserting an invariant does not hold, look for the gate whose name says it does — `ls scripts/ | grep the-thing-you-are-about-to-claim`.
