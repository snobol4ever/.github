# FINDING 2026-09-01 seat01 — the last 861 relocations on x86_argroles are gone; and this rung was worth ~6 faults, not ~245

Row: `rtx-startup-touch-rewrites` (`## NEXT` item 2 — hq_P's named second rung on the same table).
SCRIP at landing: `bcb0ec1e` + this change. Build: `make pristine` (HQ-27), `RT_OPT=-O0` (NO -O2 BUILDS).
Dated TSV: `corpus/benchmarks/snobol4/perf-attribution-20260901T224010Z-seat01-argrole-blob.tsv`.

## WHAT LANDED

`x86_argroles` held 123 entries x 7 `const char *` (callee + role[6]) = **861 pointers**. A pointer to a
string literal cannot be a link-time constant in a PIC object — it must be written at load time — so all 861
were `R_X86_64_RELATIVE` relocations, and the table was pinned in `.data.rel.ro`: writable, and dirtied in
every process that loads the runtime.

The fields are now **16-bit offsets into one `x86_argrole_blob`** (244 distinct strings, 2,619 B; offset 0 is
the empty string). Every field is a genuine compile-time constant, so the table and the blob are both
`.rodata` — never written, shared between processes, demand-paged clean.

Consumer surface was two lines in `x86_asm.h` (`x86_argrole_find`, `x86_argnote`), both routed through a new
`x86_argrole_str()`. The `rr->role[slot] &&` NULL test dropped: no entry was ever NULL — all 861 are string
literals, and offset 0 yields `""` — so only the `[0]` emptiness test ever carried meaning.

## PROOF THE DATA IS UNCHANGED

⭐ Not a claim from the generator — a **compiled** comparison. A standalone program linked against the new
`x86_arg_roles.cpp` printed all 123x7 fields through `x86_argrole_str()`, diffed against the 861 strings
parsed out of the pointer table it replaces: **identical, zero lines of diff**. This catches C-level escaping
and literal-concatenation faults that a generator-side check cannot see.

## MEASUREMENT

Matched instrument: same box, same tree, `make pristine` BOTH arms, 5 runs/arm, `/usr/bin/time -v`, witness
`OUTPUT = 1` (the do-nothing RT-load floor). Metric is faults + MAXRSS, never wall clock — per hq_P's standing
direction for this lane, since relocation PROCESSING was already measured cheap and the cost is page-DIRTYING.

STRUCTURAL (exact readings of the linked `.so`, not sampled):

| | baseline | blob | delta |
|---|---|---|---|
| `R_X86_64_RELATIVE` | 6,037 | 5,176 | **−861 (−14.26%)** — exactly the predicted count |
| `.data.rel.ro` | 102,464 B | 95,552 B | **−6,912 B (−6.75%)**, writable → read-only |
| `.rodata` | 1,037,021 B | 1,038,749 B | +1,728 B (+0.17%) |

Net image −5,184 B, with 6,912 B moved from per-process-dirtied to shared-clean. `.rodata` grew by only the
table (1,722 B) and not the blob: the blob's strings deduplicated against literals already in the string pool.

RUNTIME (means of 5; arms separate cleanly — no run-range overlap on any row):

| | baseline | blob | delta |
|---|---|---|---|
| m3 minflt | 748.0 | 742.2 | −5.8 (−0.78%) |
| m3 maxrss | 9,348.0 kB | 9,092.0 kB | −256.0 kB (−2.74%) |
| m4 minflt | 755.8 | 751.2 | −4.6 (−0.61%) |
| m4 maxrss | 9,403.2 kB | 9,186.4 kB | −216.8 kB (−2.31%) |

⭐ REPRODUCED: the blob arm was built pristine TWICE, independently — m3 minflt 742.4 then 742.2, relocation
count identical at 5,176 both times. Reported rows are the final pristine tree's readings.

## VERIFICATION

- SNOBOL4 master suite: **m3 PASS=1677 FAIL=0 · m4 PASS=1677 FAIL=0 SKIP=0 · MISSING=0 · ✅ GATE OK**
- Icon smoke 14/14 both modes · Snocone 5/5 · Rebus 4/4 · Prolog 5/5 in all three modes, FAIL=0 throughout

⛔ **THE BOARD TOTAL IS 1677, NOT THE 893 THIS ROW'S BATON AND LEDGER BOTH STILL SAY.** The denominator moved
with the crosscheck/probe total conversion into the master suite; 893 is a pre-conversion number. Anyone
grading this row against 893 will think the corpus shrank or grew for the wrong reason. Read the printed
total — the standing law — and do not carry 893 forward.

⚠ **XPASS=2 in both modes, PRE-EXISTING, not attributable to this rung.** The board flags XPASS as loudly as
FAIL, correctly. It is not caused by this change: this change only appends `# role` comments to emitted asm
TEXT, while suite entries grade program stdout against `.ref`. It is the known standing pattern of XFAIL
markers going stale as SCRIP cures land — five separate corpus commits in recent history do exactly this
promotion (`c487af7c7`, `04177c4b3`, `6a8e86d89`, ...). Two markers are stale again and want promoting; that
is a corpus row, not this one, and it is recorded here so it is not lost.

## ⭐ THE FINDING THAT OUTLIVES THE RUNG: THE `## NEXT` BLOCK IS MIS-RANKED

The relocation win is exact and proportionally large — **14.26% of every relocation left in the runtime**. The
FAULT win is real but small: **~6 faults out of ~748**.

That is not a disappointment; it is arithmetic that was available BEFORE the rung and should have been in the
NEXT block. One copy of a 6,888-byte table spans under two pages, so removing its dirtying can only ever be
worth about two pages. The 150→1 collapse was worth ~245 faults because it removed **150 copies**, not because
this table is expensive. **The lever was never the table — it was the duplication.**

⛔ Consequence for whoever takes this row next. Sized honestly against the ~237-fault floor that target (1)
left behind:

| remaining target | status | honest size |
|---|---|---|
| NEXT #2, `role[]` blob (this rung) | **landed** | ~6 faults |
| NEXT #1, linker ordering | unstarted | ~23 faults (ceo's own re-size, QA line 47) |

**Linker ordering is now the largest remaining lever by roughly 4x, and the NEXT block ranks it FIRST while
ranking this one SECOND — the ordering was right, but the two were treated as comparable and they are not.**
It also carries real cost that should be budgeted, not discovered: GNU ld (no lld here) needs a linker-script
fragment, and the full 65-function list must be re-derived by executed-page symbol coverage — the FINDING it
came from names only the top 15.

⭐ And the general lesson for this lane, which is the reason this section exists: **a structural metric and a
cost metric can move by wildly different factors on the same change.** −14% of all relocations sounds like a
headline and buys ~0.8% of the faults. In this lane the graded metric is faults and RSS; a relocation count is
a mechanism, not a result, and should never be quoted as if it were the win.
