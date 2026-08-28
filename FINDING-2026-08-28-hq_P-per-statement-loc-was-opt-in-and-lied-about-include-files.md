# FINDING — per-statement `.loc` was opt-in (so it never fired), and where it did fire it lied about `-INCLUDE`

**Seat:** hq_P · **Date:** 2026-08-28 · **Row:** `perf-per-statement-loc-emission` (slice 2 of `perf-symbol-attribution-tooling`)
**Tree:** SCRIP `764752c6` · corpus `89620e682` · `RT_OPT=-O0` · pristine (HQ-27)
**Instrument:** `bash scripts/test_corpus_snobol4.sh` (the board command is part of the number — FACT RULE)

## What the row was

Lon's tooling order names per-statement attribution first: *"by making the symbols accessible by the perf
tools you can do per-statement, and per-BB or per-BB-type statistics for which statement or BB is hogging
the time."* Slices 1 + 3 landed at `476a8ae3` (family×port rollup, m3 perf-map). Slice 2 — DWARF
`.file`/`.loc` at statement boundaries so `perf report --sort srcline` and `perf annotate` work — did not.

## 1. The machinery already existed and had never once emitted anything

`fde80746` (2026-08-23) landed `x86("loc", …)`, `bb_line_of()`, and the `g_bb_src.line[]` column, all
correct — **behind `SCRIP_DWARF_LOC=1`, opt-IN.** So every profile taken in the five days since measured a
compiler that emits no line information, and the row minted today recorded "emitted `.s` carries ZERO
`.loc`" as a property of the compiler rather than of the flag's polarity.

⭐ **This is Instrument Law 1 exactly, in a second independent instance:** *a cure behind a default-OFF
flag is a deletion with a comment explaining what it used to do.* The file reads as if the feature
shipped. ⛔ **And the gate agreed with it** — `test_gate_emit_dwarf_loc.sh` asserted, as arm 3, that the
default build emits **no** `.file`/`.loc`, i.e. the gate's own success condition was that the feature stay
dark. A gate written at the same time as an opt-in cure will faithfully protect the opt-in.

**Cure:** default ON; `SCRIP_DWARF_LOC=0` is the killswitch and the control arm (clause 10 — both arms
boarded below). The polarity now has ONE spelling, `emit_dwarf_loc_on()`, used by both the per-node walk
and the two mode-4 preambles.

## 2. `.file` was declared once per `.loc` — 1,068 duplicate declarations on beauty

The op emitted `.file 1 "path"` immediately before every `.loc`. Half of all added lines were a repeated
declaration. Moved to the two mode-4 TEXT preambles in `scrip.c` — chosen because they are *structurally*
first (they run immediately after `emit_set_sink`, before any node is walked), not merely observed to come
first in one program. ⛔ `emit_set_sink` itself was rejected as the site: it has five call sites beyond
mode-4, and a `.file` emitted from there would fire in contexts nobody has audited.

## 3. ⭐ The part worth reading: `-INCLUDE` was being attributed to the main file

`snobol4.lex.c:703`'s `lineno` is a **monotonic counter over the post-include token stream**, so a
statement from an included file carries a number that indexes nothing in the file `.file` names.

**Measured on beauty** (618 lines, ten `-INCLUDE` directives), before the cure: **1,068 `.loc`, of which
599 pointed past the end of the file they named**, and the remaining include-derived rows landed on real
beauty.sno line numbers belonging to unrelated statements. ⛔ The second half is the dangerous half: a line
number past EOF is *visibly* bogus, while an in-range wrong line is **plausible**, and `perf annotate`
renders it as confidently as a true one.

⛔ **The existing gate could not see any of this: it graded `roman.sno`, which has no includes.** That is
Instrument Law 9 — *a cure named for a concept and graded on one spelling of it passes its own gate every
time.* The gate now carries its own generated `-INCLUDE` witness.

**Two obvious repairs were measured and both are wrong:**
- **Omit the `.loc` for included statements.** ⛔ DWARF `.loc` is *sticky* — instructions after a `.loc`
  belong to that line until the next one — so omission does not mean "unknown", it means "same as the
  previous statement". On beauty that would hand ~56% of the program to whichever main-file statement
  happened to be emitted last.
- **Emit `.loc 1 0 0`** (DWARF line 0 = "no source line"). ⛔ **gas silently DROPS it.** Measured: raw
  line table shows no row for the address, and `addr2line` reports the *previous* line. A directive the
  assembler discards is indistinguishable from the omission above.

**Cure:** file 1 is the main source, file 2 is `"<included>"`. The routing rides a fact `stmt_ast.c`
**already computed and threw away**: `stmt_src_slice()` returning NULL *is* "not in the main file" — it is
what produces the existing `<stmt N, line L: source not in main file (INCLUDE)>` comment. Recorded as an
`:incl` AST attribute and carried on the **sign** of the line already flowing to the `g_bb_src` side table.
⭐ No new global, no new parallel array, no signature change — the NO-NEW-GLOBALS rule names "parallel
array" explicitly, so widening the side table was deliberately avoided.

⛔ **A bound check alone was NOT enough, and the witness is what caught it.** My first cut routed on
`line <= stmt_src_nlines()`. An included statement whose stream line lands *inside* the main file's range
slipped through — in the 7-line witness, an include statement numbered 7 was emitted as `file 1 line 7`.
`stmt_src_slice`'s test is strictly stronger than a bound check (it also rejects a line whose text cannot
be a statement, or whose label does not match). **The predicate I could reconstruct at the emit site was
weaker than the one the compiler had already evaluated upstream** — the fix was to carry the real answer
forward, not to re-derive an approximation of it.

After the cure, beauty reads **178 file-1 rows (true line numbers) + 890 file-2 rows, and ZERO file-1
lines past EOF.**

## 4. ⛔⭐ An instrument lesson that cost the most time here: **mawk has no `\s`, GNU grep does**

Mid-session I measured beauty at **0 `.loc`** and spent a long stretch treating it as a compiler
regression — it was not. `awk '/^\s*\.loc/'` matches **nothing** under mawk (the only awk on this box),
while `grep -c '^\s*\.file'` in the *same* command block worked, because GNU grep supports `\s`. So the
two counters in one script disagreed, and the disagreement looked exactly like "the emitter stopped
emitting `.loc` but still emits `.file`" — a plausible, specific, entirely fictional bug. The file had
1,068 `.loc` the whole time.

⭐ **The transferable rule: a script that mixes `grep` and `awk` over the same text must not assume they
share a regex dialect.** Use POSIX classes (`[[:space:]]`) in `awk`, always. This is the same family as
RULES' clause 15 (ASCII regex over UTF-8 labels): **the instrument was wrong in a way that still printed a
plausible number.** ⛔ The tell was available and I did not read it for too long: *two counters over one
file disagreeing about the same file is an instrument fault before it is a subject fault.*

## 5. Inertness (the claim this row must not get wrong)

`.loc` moves no executable byte. `.text` **byte-identical** default-vs-killswitch on `pattern_bt`,
`porter`, `json`; stdout identical; **proven NON-VACUOUS** by a one-`nop` poison arm that the comparison
does catch. Independently corroborated by artifact regen: **41 benchmark/demo `.s` changed by +1,019
insertions and 0 deletions** — the emitted code is otherwise unchanged.

## Boards (pristine, `-O0`, SCRIP `764752c6` + corpus `89620e682`, re-run AFTER the rebase)

| arm | board |
|---|---|
| SNOBOL4 default (feature ON) | m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0 · MISSING=0 |
| SNOBOL4 `SCRIP_DWARF_LOC=0` | m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0 · MISSING=0 |

Shared-node scope (`emit.cpp` / `x86_asm.h` / `scrip.c` are reached by every frontend): icon smoke 14/14
m4, rebus 4/4, raku 724/724, polyglot 2/2, hello-matrix 6/6, `test_gate_emit_no_lang` OK,
`test_gate_template_medium_invisible` OK, `test_gate_emit_dwarf_loc` OK. Icon bench `.s` verified
byte-identical (8 sampled) and carry no `.loc` — only SNOBOL4's lowering populates the line table, which
is why prolog bench regen is `changed=0`. Prolog smoke **4/5**: `clause` fails **identically in both arms
and in m2**, which this change cannot reach — pre-existing, tracked by `prolog-multiclause-fail-backtrack-segv`.

⚠️ The first board pair was taken before `git pull --rebase` brought in 19 other-seat commits (one of them
touching `scrip.c`). Per the MEASURE-THEN-REBASE corollary that pair certified a tree that never existed on
origin; **both arms, all gates and all smokes above were re-run on the merged tree**, and the artifact
regen chain re-run and found already-current.

## ⛔ Routed, NOT cured here (outside this row)

`scripts/update_icon_bench_asm.sh CHECK=1` reports `total=0 new=0 updated=0 unchanged=0` and **exits 0** —
a clean success shape — while **37 Icon benchmark `.icn` sources with 20 committed `.s` artifacts** sit at
`corpus/benchmarks/icon/`. Its guard still matches the pre-re-grid path `*/corpus/icon`, which no longer
exists. This is Instrument Law 2 (*"measured and clean" must not share an output with "never ran"*) and the
same re-grid casualty class as the `util_regen_demo_s_artifacts.sh` 0/21 break RULES already records —
except the demo one is now **fixed** (21 sources found this session) and this one is not. It is harmless for
*this* change (Icon `.s` verified byte-identical by hand) but it would hide genuine Icon artifact drift from
every future session, silently. ⭐ Same shape as the two inert `lon` guards CLAUDE.md documents: **a guard
keyed on a name is not a guard, it is a coincidence.** Sent to `ceo`.

## Not claimed

No speed claim — this is attribution plumbing and it is inert by construction. Included statements resolve
to `<included>:<stream-line>`, an honest bucket, **not** a file `perf annotate` can open; giving each
include file its own `.file` number needs file identity threaded through the lexer and is not in this row.
Slice 3's m3 perf-map remains **per-graph, not per-box**.

## ⭐ ADDENDUM — RE-PROVEN ON THE FINAL TREE (same session, added openly rather than by silent edit)

After the FINDING body was written, a `pull --rebase` for a follow-up commit (the demo-regen path fix below)
moved the tree again. Both arms, the three gates and the Icon smoke were **re-run on the tree actually handed
off**: **SCRIP `e5ee4c78` · corpus `c9d235401`**, pristine, `RT_OPT=-O0`, `bash scripts/test_corpus_snobol4.sh`:

| arm | board |
|---|---|
| SNOBOL4 default (feature ON) | m3 PASS=1081 FAIL=0 · m4 PASS=1081 FAIL=0 SKIP=0 · MISSING=0 |
| SNOBOL4 `SCRIP_DWARF_LOC=0` | m3 PASS=1081 FAIL=0 · m4 PASS=1081 FAIL=0 SKIP=0 · MISSING=0 |

`test_gate_emit_dwarf_loc` rc=0 · `test_gate_emit_no_lang` rc=0 · `test_gate_template_medium_invisible` rc=0 ·
`test_smoke_icon` rc=0.

⛔⭐ **THE DENOMINATOR MOVED 893 → 1081 INSIDE ONE SESSION** — another seat grew the corpus between my two
board runs. Both readings are green and both are correct for their tree. This is the standing CLAUDE.md
warning paying off exactly as written: **`FAIL=0 / SKIP=0 / MISSING=0` is the invariant; the total is not.**
A seat matching a remembered 893 against today's 1081 would read legitimate corpus growth as 188 missing
programs and go hunting for a cure.

## ⛔ A DEFECT THIS ROW INTRODUCED, CAUGHT AND CURED THE SAME SESSION — COMMITTED ARTIFACTS WENT SEAT-ROOT-SPECIFIC

Because the compiler now emits `.file 1 "<path as given>"` (gcc's own behaviour, and correct — the compiler
echoes the path it was handed), **`util_regen_demo_s_artifacts.sh` baked `/home/claude_P/...` into 21 committed
demo `.s` artifacts**: it resolves its source with `find "$DEMO" …`, so it handed the compiler an absolute path.
⛔ **Every other seat root would have regenerated them straight back — a permanent churn war between
`/home/claude_P` and `/home/claude_C` over 21 files, with neither side wrong.** The benchmark regen was clean
throughout because it already passed a bare basename.

⭐ **What caught it is the part worth keeping: `handoff_status.sh`'s artifact WARN said "21 demo .s owed" while
the regen script itself said "already current" — and I chased the disagreement instead of trusting the
scarier-looking one or waving off the WARN-only banner.** Two instruments disagreeing about one tree is a fact
about the instruments, and it was true here in the same way it was true of the mawk/grep split in §4. The
script already `cd`s to `$DEMO`, so compiling `"${src#$DEMO/}"` is a one-token fix. Verified: 21 files
re-emitted (21 insertions, 21 deletions — one `.file` line each), **zero committed `.s` under `corpus/` carry an
absolute `/home/` path**, a second regen reports "already current", and roman/json/wordcount re-compile
byte-identical from `$DEMO`.
