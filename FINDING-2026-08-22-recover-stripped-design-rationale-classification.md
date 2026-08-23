# FINDING — classification of the 6,919 comments stripped by `e25a5daf`, chosen home for recovered rationale, and the flagship relocation

**Session:** 2026-08-23 seat05 (`/home/claude05`, Claude Sonnet 5), THE LOOP row `recover-stripped-design-rationale` (rank 0, `FREE`, `s4e_msg.sh next`). Filename is dated 2026-08-22 because that is the literal path the row's `DONE-WHEN` requires (`.github/FINDING-2026-08-22-recover-stripped-design-rationale-classification.md`) — it was minted 2026-08-22 by hq_C's QUEUE.tsv→baton conversion; this FINDING was actually written 2026-08-23.

## 0. WHY THIS ROW EXISTS

`e25a5daf` ("GOAL-STYLE-200COL REACTIVATION 4", 2026-08-20 23:01:56 -0500) stripped comments fleet-wide to enforce RULES.md's C style (200-char lines, zero blank lines, exactly one comment form — the 200-char separator). Verified directly (`git diff --shortstat e25a5daf^ e25a5daf`): **162 files changed, 3,058 insertions(+), 8,294 deletions(-)** — matches the brief's cited numbers exactly. File-extension breakdown: 73 `.cpp`, 54 `.c`, 34 `.h`, 1 `.sh`.

The style rule itself is correct and not in question — this row does not propose reverting it. The problem is narrower and concrete: some of what was stripped was not decoration, it was the only surviving record of *why* — a measurement, a witness program name, a ruling, a warning against a specific mistake already made once. `seat04` needed exactly one such comment this week (why `blob_choice_rbp_scan` excludes FENCE) and it was one `git show e25a5daf^` away from being unrecoverable-by-search.

## 1. METHODOLOGY

Manually classifying 6,919 comments was out of scope for one row (row-factory instruction in the brief). Built a heuristic extractor+classifier instead (`/tmp/.../scratchpad/rationale/classify.py`, not checked in — session-scratch, reproducible from this description):

1. For every changed `.c`/`.cpp`/`.h` file (161 of 162; the 1 `.sh` file excluded), pull the OLD and NEW blobs via `git show e25a5daf^:<path>` / `git show e25a5daf:<path>`.
2. Extract every `/* ... */` and `// ...` span from each blob via regex scan (not a full C tokenizer — good enough for this codebase's style, not immune to a `/*`-looking sequence inside a string literal).
3. Whitespace-normalize and diff OLD's comment multiset against NEW's (count-aware, so a comment appearing twice in OLD and once in NEW counts one occurrence as stripped) → the **stripped set**, 6,165 spans. This undercounts the brief's 6,919 by ~11%; the gap is most likely comments that were reworded rather than deleted outright (textually different in NEW, so not "identical-and-still-present," but also not counted as a distinct stripped span by this exact-match diff) or extraction edge cases in deeply nested inline block comments. Treat 6,165 as the classified population, not a claim that it equals 6,919 exactly.
4. Classify each stripped span **DECORATION** vs **RATIONALE** by a keyword+structure heuristic:
   - `RATIONALE` if it matches ≥2 signal patterns from a ~30-term list (measured, witness, regression, cure(s), SEGV, crash, bug, defect, bisect, FINDING, ruling, DO NOT, ⛔, ⭐, a session tag `sNNN`, a percentage, `rc=NNN`, FACT RULE, CONVICT/RETRACT/REFUSE/ADMIT, corpus/program-name patterns, etc.), or 1 signal in a span ≥90 chars, or contains this codebase's terse **design-tag idiom** (`PL-FR-4`, `RK-ZC-5`, `ZD-2m`, `ICN-PROC-FRAME`, `TINY-SITE`, `Z4-7`, ...) in a span ≥50 chars — added after sampling showed the keyword list alone was missing this codebase's dominant terse-rationale style (a comment explaining a *why* via a named design decision, with none of the war-story keywords: e.g. *"PL-FR-4 ZFRAME RESUME: set pending-resume globals before re-calling rt_proc_call_open_det; xa_flat epilogue-γ picks them up while callee frame is live."* scored 0 on keywords alone — a decoration comment does not invent a tag, so the tag itself is evidence).
   - `DECORATION` otherwise (includes every regenerated separator line, which shows up as "stripped" because the OLD separators varied in length/character and the NEW ones are uniform 200-char — these are pure noise in the classification, not lost rationale).
5. Validated by hand: random 12-file sample (seed 42), eyeballed both buckets twice (once before the design-tag fix, once after) — see §2 for what the fix caught and what it still misses.

## 2. COUNTS, AND THEIR HONEST LIMITS

```
TOTAL stripped comment spans classified: 6,165
  DECORATION: 3,406  (55.2%)
  RATIONALE:  2,759  (44.8%)
files with >=1 stripped comment: 152 of 161
```

**This is a lower bound on RATIONALE, not a precise count.** Manual sampling after the fix still found misses — e.g. a design-tagged span with a lowercase letter immediately after the tag's hyphen (`ZD-2m`) initially fell through the original tag regex (fixed, case-insensitive suffix now); shorter design-tag spans under the 50-char floor are still bucketed DECORATION by construction, and some of those are real (terse) rationale. The DECORATION bucket's dominant member by volume is the regenerated 200-char separator (pure noise, correctly classified) — the heuristic's *precision* on DECORATION is good; its *recall* on RATIONALE is what's approximate. Anyone doing a remaining cluster (§5) should treat a DECORATION verdict as "probably safe to skip," not "definitely skip," and spot-check a sample before trusting the bucket wholesale — same rule this project applies to every other measured-not-guessed number.

Per-file ranking (RATIONALE count, top 10 of 152) — this is what drove cluster prioritization in §4–§5:

| rank | file | RATIONALE | DECORATION |
|---|---|---|---|
| 1 | `src/emitter/emit.cpp` | 647 | 262 |
| 2 | `src/templates/x86_asm.h` | 253 | 295 |
| 3 | `src/lower/lower_snobol4.c` | 232 | 169 |
| 4 | `src/contracts/zeta_storage.c` | 132 | 73 |
| 5 | `src/emitter/emit.h` | 119 | 21 |
| 6 | `src/runtime/rt/rt.c` | 106 | 233 |
| 7 | `src/driver/scrip.c` | 105 | 73 |
| 8 | `src/templates/bb_call_proc_staged.cpp` | 81 | 60 |
| 9 | `src/templates/bb_define.cpp` | 75 | 113 |
| 10 | `src/templates/xa_flat.cpp` | 59 | 74 |

## 3. THE HOME — DECIDED AND WHY

The brief offered four candidate homes: an ARCH file, a FINDING, a per-function design note, an indexed appendix. Decision, matching this project's own existing conventions rather than inventing a fifth:

- **Large, coherent, multi-session rationale clusters** (a subsystem's worth of interlocking `sNNN`-tagged decisions that reference each other, like the ALT-carrier-depth story below) → **a new `ARCH-*.md` file**, this project's existing convention for living subsystem design documentation (`ARCH-ICON.md`, `ARCH-FLEET-CEO.md` already exist and are already first-reads in `CLAUDE.md`'s session-start protocol for their subsystems). This is a better fit than `FINDING-*` for content that spans many original sessions' worth of accumulated decisions, since the `FINDING-YYYY-MM-DD` naming convention implies a single point-in-time discovery, not an evolving narrative — the recovered content is closer to "this is how the subsystem works and why" than "here is what I found today."
- **A single isolated decision/measurement not part of a larger narrative** → a `FINDING-*.md` (this project's existing point-in-time evidence format) is the better fit and is what future per-cluster relocations not large enough for their own ARCH file should use.
- **Discoverability across both** → a new lightweight **indexed appendix**, `.github/RATIONALE-INDEX.md`: one line per relocated symbol/function name, pointing at whichever doc holds its rationale. This directly answers the failure mode named in the brief (seat04 was "one git show away" from the answer) — the index makes it one `grep` on the *symbol name* away, without needing to already know a recovery doc exists or guess which one.

## 4. FLAGSHIP RELOCATION — THE SEAT04 CLUSTER

Relocated to **`.github/ARCH-PATTERN-CHOICE-CARRIER.md`**: the ALT/DEFER/ARBNO choice-carrier depth-safety story spanning `sn4_alt_carrier`, `sn4_blob_choice_scan`, `resume_carrier_ok` (the exact function+comment seat04 needed — reproduced there verbatim, including the *"lf=0 and fn=1 on BOTH cures ... the choice-node COUNT alone does"* sentence and the three witness program names), `blob_choice_rbp_scan`, `sn4_choice_rbp_off`, `blob_frame_bytes`, and the `zeta_depth.c`/`.h` ZDP lattice (`zdp_tier`) that a s136 comment describes as unifying the earlier ad-hoc estimators.

This is not just a comment dump — it is organized as a narrative (problem → s121→s189 historical arc → per-function verbatim rationale → warnings) because the source comments themselves are written that way, cross-referencing prior rungs by session tag. One finding surfaced only by doing this relocation properly (reading `resume_carrier_ok`'s cluster as a whole, not each comment in isolation) is new information, not just recovery: **the s136 ZDP lattice's own header claims it "replaces" the s121–s131 estimators, but `git grep zdp_tier(` at the commit this was written against shows `zdp_tier` called only from within `zeta_depth.c` itself — `emit.cpp` still calls the old estimators directly.** So the unification the s136 rationale describes as done is not the live path today; both systems coexist, and a future session should re-verify before assuming either one is authoritative. That fact would have been invisible without reconstructing the cluster.

Indexed in `.github/RATIONALE-INDEX.md` under all six symbol names above.

## 5. REMAINING CLUSTERS — QUEUED, NOT RELOCATED (row-factory, per the brief: do not try to relocate all 6,919)

One queue row minted per remaining top-ranked file (see §2 table, ranks 1 remainder through 8), each a `FREE` `QUEUE.tsv` row with its own task baton under `/home/resources/postoffice/tasks/`, same instructions as this row (classify sub-clusters, pick the highest-value one, relocate it, prove the home, spin off further rows if the file is still too big for one sitting):

- `rationale-emit-cpp-remainder` — `src/emitter/emit.cpp`, the ~600 RATIONALE-classified spans NOT already covered by `ARCH-PATTERN-CHOICE-CARRIER.md` (this file alone is larger than every other file's total; it will need more than one follow-up row)
- `rationale-x86-asm-h` — `src/templates/x86_asm.h` (the sole `x86(...)` encoder — RULES.md `Emission discipline`; its rationale is likely encoder-design-invariant material, worth an ARCH file of its own)
- `rationale-lower-snobol4-c` — `src/lower/lower_snobol4.c`
- `rationale-zeta-storage-c` — `src/contracts/zeta_storage.c`
- `rationale-emit-h` — `src/emitter/emit.h`
- `rationale-rt-c` — `src/runtime/rt/rt.c`
- `rationale-scrip-c` — `src/driver/scrip.c`
- `rationale-bb-call-proc-staged` — `src/templates/bb_call_proc_staged.cpp`

## 6. OUTCOME

- `.github/ARCH-PATTERN-CHOICE-CARRIER.md` — flagship relocation (§4).
- `.github/RATIONALE-INDEX.md` — the indexed appendix (§3), seeded with the 6 relocated symbols and the 8 remaining-cluster rows.
- This FINDING — classification methodology, counts (§2), home decision (§3).
- 8 new `QUEUE.tsv` rows + task batons for the remaining clusters (§5).
- No source code changed; no comments restored into any `.c`/`.cpp`/`.h` file — RULES.md's style rule is respected throughout.
