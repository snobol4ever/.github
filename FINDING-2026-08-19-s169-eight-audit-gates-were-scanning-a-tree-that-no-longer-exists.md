# FINDING s169 — EIGHT GATES/AUDITS WERE SCANNING A TREE THAT NO LONGER EXISTS, AND THREE OF THEM PRINTED GREEN WHILE DOING IT

**Seat:** local `/home/claude1` (seat1), Claude Opus 5. **Picked up:** postoffice QUEUE.tsv row 1
`gates-dead-paths` (HQ-48 ruling on seat3's `q-fz-out-of-lane` catch).
**SCRIP** `25d8970c` → this commit · **.github** this commit.

## 1. THE CLASS IS BIGGER THAN THE BRIEF, AND THE ROOT CAUSE IS A BLIND SED

The brief said **6 gate scripts grep dead `src/emitter/BB_templates/`**. The true count is **8 scripts**,
and `BB_templates` was only one of four dead spellings. `src/emitter/` today holds exactly four files
(`emit.cpp`, `emit.h`, `emit_str.cpp`, `sil_macros.h`); `BB_templates/`, `SM_templates/` and
`XA_templates/` are all gone, and the 169 template files live flat in `src/templates/`.

The mechanism is visible in the wreckage. Two scripts read:

```
for f in src/templates/*.cpp src/emitter/SM_templates/*.cpp src/templates/*.cpp; do
```

That is a **blind search-and-replace** from the src reorg: it rewrote `BB_templates` → `templates` and
`XA_templates` → `templates` (collapsing two distinct dirs onto **one, listed twice**) and left
`SM_templates` untouched because no target existed. So the same reorg produced **both** failure modes at
once — **double-counting** where it succeeded, **dead scans** where it didn't. Neither was ever noticed,
because a doubled count and a zero count both look like a number.

## 2. THE CENSUS — WHAT THE FIXED SCRIPTS ACTUALLY REPORT (RATCHET BASELINE)

Every "before" below is measured on `25d8970c`, every "after" on this commit.

| script | BEFORE (dead path) | AFTER (real tree) |
|---|---|---|
| `test_gate_emit_no_ir_mutation.sh` | `PASS`, templates unscanned | `PASS` — **honest**: 3 emitter + 169 template files, 0 sites |
| `test_gate_em_template_matrix.py/.sh` | `rc=2` "template dirs not found" | `rc=2` **VACUOUS, declared** (see §3) |
| `util_three_section_audit.sh` | **`AUDIT GREEN`, 0 files** | **`AUDIT RED`** — 146 audited, 3 OK, **137 missing** |
| `audit_multi_emit_helpers.py` | **`0 helpers across 0 files`** | **227 helpers across 144 files** |
| `util_template_purity_audit.sh` | `8 side-effects` (**doubled**) | **4** — bb_call, bb_call_write_slot, bb_define, bb_match_replace |
| `audit_m3_native_binary_arms.sh` | 327 rows (every file **twice**) | 165 rows, `GATE OK` |
| `util_emit_inventory.sh` | 0 symbols, 0 per-TU | `emit.cpp`=91 fprintf/fputs/fwrite |
| `audit_concurrency_invariants.sh` | 4× "not found" | live (see §4) |

**Three of these printed a passing verdict while scanning nothing** — `util_three_section_audit.sh`
("AUDIT GREEN: all x86 blocks have three sections", 0 files harvested), `audit_multi_emit_helpers.py`
("0 helpers across 0 files", empty glob), and the templates half of the IRM-0 gate. This is the s33
**"non-empty is not alive"** false-signal class, in its purest form: the output was well-formed,
plausible, and completely uninformed.

## 3. TWO CHECKS ARE NOT MIS-PATHED, THEY ARE ARCHITECTURALLY DEAD — HQ DECISION OWED

Repointing exposed that two contracts no longer exist anywhere in the codebase. **Neither was silently
"fixed"**; both now declare themselves.

**(a) `test_gate_em_template_matrix.py` — the EC-UNI 5-column matrix.** It required every template fn to
carry an `IS_<BE>` arm for X86/JVM/JS/NET/WASM. Measured: **zero `IS_X86`, `IS_JVM`, `IS_JS`, `IS_NET`,
`IS_WASM` tokens exist in `src/templates/`** — none, of any kind. Its `SIG_RE` also matches only
`void|int|long` signatures while the real templates return `std::string`/`DESCR_t`, so it extracts **0
functions from 145 files**. RULES.md **X86-ONLY** superseded this contract. The gate now hard-exits `rc=2`
with a VACUOUS banner rather than printing `PASS` over an empty set.

**(b) `util_three_section_audit.sh` demands what RULES.md forbids.** It fails any template whose
`PLATFORM_X86` block lacks `MEDIUM_MACRO_DEF` + `MEDIUM_BINARY` + `MEDIUM_TEXT` sections. RULES.md
**NO MEDIUM_\* IN TEMPLATES** requires *zero* `MEDIUM_*` in `bb_*.cpp`. **The 137 "MISSING" are
compliance, not debt** — this audit must be RETIRED, never satisfied. Left red and loud, not deleted.

## 4. THE PURITY RATCHET WAS 2× TOO LOOSE, AND THE DOUBLING HID ITSELF

`audit_concurrency_invariants.sh` gates template purity against `PURITY_BASELINE=8`. The audit it consumes
was printing **8** only because it scanned `src/templates` twice; the true count is **4**. The doubled
number **exactly matched the stale ceiling**, so the ratchet never fired and the defect concealed itself —
four real new violations could have landed silently. Re-based **8 → 4**.

Its other three dead refs are fixed or declared: `src/lower/lower.c` (split into per-language lowerers —
and the `lower_(value|pattern|goal)` role-dispatcher shape it scans for exists in **none** of the 7, so
check (a) now says VACUOUS out loud); `src/emitter/emit_core.c` → `emit.cpp`; and check (d), which
byte-compares FACT RULE blocks across `GOAL-{SNOBOL4,ICON,PROLOG}-BB.md` — **all three consolidated away,
and the blocks did not survive into the `-100` files** (grep == 0 in all three). (d) is unrunnable, not
mis-pathed; repointing only moves the failure. Gated behind `CONCURRENCY_SKIP_D=1` with the reason inline.
**HQ decision owed: restore the blocks or retire the check.**

### The emitter dup-label check: a corrected path turned it into a FALSE RED, twice

Worth recording because it is the trap this whole class sets. `emit_core.c` → `emit.cpp` made check (b)
runnable — and it immediately flagged **~120 IR kinds** as duplicated. False: `emit.cpp` now holds **26
switches**, and a kind legitimately appears once per switch (`IR_ACTIVATE` in `walk_bb_node_inner` *and*
`emit_drive`). The flat `grep | sort | uniq -d` had no scoping. Rewritten to a brace-depth stack. That
flagged **one** survivor, `IR_MATCH_LIT` — also false: one-line switches (`switch (o) { case ...: }`) leaked
their labels into the enclosing scope. Fixed by normalising `{`, `}` and `case IR_X` onto their own lines.
Then a string-literal stripper — added for safety — **swallowed a real `}`** (emit.cpp contains the char
literal `'"'`, exactly one), unbalancing 1349/1348 and silently blinding the check again. Dropped the
stripper; added a **brace-balance assertion** so the scoper says so instead of passing.

**Proven live, not assumed:** clean on real `emit.cpp`; injected a duplicate `case IR_MATCH_LIT` into the
same switch → `VIOLATION: emit.cpp: case IR_ label duplicated WITHIN a single switch`. A gate nobody has
watched fail is a gate nobody should believe.

## 5. THE BOTH-MEDIUM RATCHET: THE NUMBER AND THE COMMAND DISAGREED

RULES.md carried `29` as a typed known-red ratchet, beside the command
`grep -rn 'MEDIUM_' src/templates/bb_*.cpp`. **That command yields 38.** The counts:

| method | count |
|---|---|
| `grep -rn 'MEDIUM_'` — the documented command | **38** |
| raw occurrences (`-o`) | 41 |
| comment-stripped lines / occurrences | 31 / 33 |
| **guard sites: `if (MEDIUM_` 19 + `IF(MEDIUM_` 10** | **29** ← seat3's census |

29 is the **guard-site** count, and guard sites are what the rule forbids ("any function gating output on
`MEDIUM_TEXT`/`MEDIUM_BINARY` is a violation"). The documented command counts every mention. A seat running
RULES.md literally tomorrow reads a **9-site regression that never happened** — and the ratchet's whole
purpose is to make that reading trustworthy.

**Fixed by computing it, never typing it** (the `handoff_status.sh` discipline applied to a ratchet):
`scripts/test_gate_template_medium_invisible.sh` now prints the guard-site count and **fails if it exceeds
29** (`MEDIUM_RATCHET` overrides; it also announces when the count *drops* so the gain gets locked in).
Negative-tested at ceiling 28 → `RATCHET FAIL`, `rc=1`. RULES.md line 19 now points at the computed gate.

**Ratchet baselines recorded, all of which MAY NOT GROW:** MEDIUM_\* guard sites **29** · template purity
side-effects **4** · three-section missing **137** (retire, do not satisfy) · multi-emit helper candidates
**227/144**.

## 6. THE LESSON THIS CLASS TEACHES

A gate whose path dies does not fail — **it passes**, and it keeps passing for as long as nobody checks
what it read. Every one of these eight kept its exit code and its confident wording while its subject
vanished underneath it. The cheapest defence is the one now in three of them: **a scan that matches zero
files must say VACUOUS, never OK.** Emptiness has to be loud, because silence is indistinguishable from
success.

Grep-based gates should also be **negative-tested when written** — two of the repairs above were themselves
wrong on first measurement, and only an injected violation caught it.

## 7. FOR HQ — NEXT ROWS THIS CENSUS EARNS

1. **`medium-retire` (row 10) is unblocked** — its census is §5: 29 guard sites, and the per-file punch list
   is **29 guard sites across 9 files**: `bb_glue_flat` 8, `bb_define` 5, `bb_call_write_slot` 4,
   `bb_call_proc_staged` 4, `bb_scan_stmt` 3, `bb_call_bool` 2, and `bb_mapgrep`/`bb_key_gen`/`bb_gather` 1
   each. (Note this differs from the `grep -c 'MEDIUM_'` line-count spread, which touches 12 files — one
   more reason the ratchet had to be pinned to a single command.)
2. **Retire-or-respec decisions owed** (§3, §4): `test_gate_em_template_matrix.py` (5-column matrix vs
   X86-ONLY) · `util_three_section_audit.sh` (demands what RULES.md forbids) · concurrency check (a)
   (lower role-dispatchers gone) · check (d) (FACT RULE blocks lost in the `-100` consolidation).
3. **RULES.md still names retired goal files** — the ICON semicolon FACT RULE cites `GOAL-ICON-BB.md`,
   which no longer exists. Same class, doc side; not touched from this lane.
4. **`ec_uni_9a_collapse.py` deliberately left dead.** It is a retired one-shot that **rewrites** template
   files; repointing it at `src/templates/` would arm a dormant mutator against the live tree for no gain.

## 8. HANDOFF

Row 1 `gates-dead-paths` DONE-WHEN met: 8 scripts scan the real tree (brief said 6), census above is the
ratchet baseline, ratchet is computed and negative-tested. No compiler source touched — **scripts and docs
only**, so no `.s` regen debt (RULES.md step 4) is incurred by this rung.
