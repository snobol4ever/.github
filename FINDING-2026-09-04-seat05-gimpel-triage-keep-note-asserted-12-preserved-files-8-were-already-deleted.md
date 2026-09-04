# FINDING — `gimpel_triage_KEEP.md` asserts 12 files "preserved byte-identical"; 8 of the 12 (all real witnesses) were already deleted 49 minutes earlier

**Session:** 2026-09-04, seat05 · lane hq_C, while looking for the "eight censused mode-pair classes" referenced for `snobol4-gimpel-suite-126-to-100-percent-by-class`.

## 1. THE CLAIM, AND WHAT IS ACTUALLY ON DISK

`corpus/tests/snobol4/config/gimpel_triage_KEEP.md` (hq_B, committed 2026-08-29) states, verbatim: *"Moved here from `corpus/probe/gimpel_triage/` by hq_B, 2026-08-29 ... 12 files, all preserved byte-identical (`git mv`, zero content changes)"*, and lists 12 declared keepers by name.

Measured 2026-09-04 (`ls corpus/tests/snobol4/gimpel_triage_class*`): **only 4 of the 12 exist.**

| declared keeper | present? |
|---|---|
| `class1_dup_label_driver` | **MISSING** |
| `class1_dup_label_shared` | present |
| `class2_rc1_compile_fail_dexp` | **MISSING** |
| `class3_diff_span_self_rebind` | **MISSING** |
| `class4_rc1_rc1_copyl` | **MISSING** |
| `class5_sig11_seq_driver` | **MISSING** |
| `class5_sig11_seq_module` | present |
| `class6_rc1_sig11_once` | **MISSING** |
| `class7_sig6_compile_fail_ip` | **MISSING** |
| `class8_sig6_perm_driver` | **MISSING** |
| `class8_sig6_perm_module` | present |
| `class8_sig6_perm_swap` | present |

The 4 survivors are exactly the four **`.ref`-less include helpers** — i.e. the least useful quarter of the set. Every actual **driver** (the file you run to see the bug) and every **`.ref`** oracle pin is gone.

## 2. THE MECHANISM — A DELETION LANDED 49 MINUTES BEFORE THE NOTE THAT ASSERTS PRESERVATION

`git log --diff-filter=D --all -- '*gimpel_triage*'` in `corpus/` finds exactly one deleting commit:

- **`dcdf7140`, 2026-08-29 18:19:57 -0500** — a "Master board" cutover commit. `git show --stat` on it lists a pure deletion (no rename pairing, no corresponding add) of all 8 driver+`.ref` pairs at the then-current path `tests/snobol4/gimpel_triage/class{1,2,3,4,5,6,7,8}_*.{sno,ref}`, alongside an unrelated `tests/snobol4/probe/gimpel.{sno,ref}` pair — consistent with an automated sweep of `.ref`-paired "probe-shaped" files being retired in favor of the new master-block scheme, which had no `-INCLUDE`/multi-file awareness (see `gimpel_triage_KEEP.md` §1) and evidently no awareness that these particular pairs were mid-move to their standalone-keeper home either.
- `gimpel_triage_KEEP.md` was committed the same day, and its own prose situates it as the record of a `git mv` that "preserved byte-identical" — but 8 of the 12 files it names were already gone from the tree by the time that commit landed. The note was written by reading the **intent** of the move, not by re-measuring the tree after it.

Net effect: the 4 survivors got flattened to their current names in a later same-day pass (mtimes read 19:09, after the 18:19:57 deletion) simply because they carry no `.ref` and were invisible to whatever selection criterion the cutover swept on — not because anyone decided to keep them and drop the other 8.

## 3. WHY THIS IS THE SHAPE THIS ORG KEEPS PAYING FOR

Same class as THE INSTRUMENT LAWS' "a zero in a summary is an assertion, not an absence" and this file's own CLAUDE.md's "trust `ls` over this file, always": a document whose entire purpose is to assert *"these files are preserved, here to stay, standalone"* is exactly the kind of claim that must be checked by listing, not trusted by reading — and it is precisely the load-bearing kind of claim (a census, a cure row, a class row) that people build on without re-verifying. Concretely, hq_C's 2026-09-04 mail described "the eight censused mode-pair classes" as available witnesses to hand out — they are not re-runnable; the 8-day-old `FINDING-2026-08-27-seat10-gimpel-triage-eight-symptom-classes-ranked.md` is the only place their content still fully exists (as prose + inline `.sno`/status tables), not the tree.

## 4. WHAT THE KEEP NOTE WOULD HAVE HAD TO DO TO BE TRUE (the reusable part)

A preservation claim is only checkable if it gives a reader a one-line way to re-verify it later, after the tree has moved again. Concretely, for any future "moved/kept, byte-identical" note:

1. **State the count as a command, not a number in prose** — e.g. `ls <dir>/<family>_* | wc -l` alongside the claimed count, so a reader (or a gate) can re-run it instead of trusting the sentence.
2. **Pin a checksum per file, not just "byte-identical" as an adjective** — `git mv` really does preserve content byte-for-byte for whatever it actually moves, but that guarantee says nothing about a *different, later* commit deleting the result. A `sha256sum` list committed beside the note turns "preserved" into something `diff`-able forever, independent of what git history says happened.
3. **Write the note *after* the last commit it depends on, and re-list the directory at that moment** — this note's actual defect was sequencing: it described a `git mv` accurately, then a second, unrelated commit invalidated 2/3 of it 49 minutes earlier in wall-clock terms (the note-writing session most likely hadn't re-pulled/re-listed between the two). The fix is procedural, not textual: **the last action before committing a preservation claim is the listing that would falsify it.**

## 5. NOT IN SCOPE HERE

Reconstructing the 8 missing witnesses is not attempted in this FINDING. `class1` (`-INCLUDE` diamond duplicate-label) is confirmed independently already cured (hq_C, SCRIP `9273f6329`) so it needs no reconstruction. The recursion class (`class4`/`class8`, `COPYL`/`PERM`) and the two "outside the landed subset" refusals (`class2`/`class7`, `DEXP`/the unary-`~` witness) still reproduce against current HEAD when run directly from the real `corpus/packages/snobol4/gimpel/` source (not the deleted probe copies) — see this session's other work on `snobol4-gimpel-class-sig11-both-modes` for a related, freshly-verified census.

## Consumers

Zero scripts read `gimpel_triage_KEEP.md` or the surviving 4 files (confirmed by the KEEP note itself, §Consumers, still accurate). This FINDING changes no code and deletes nothing further.
