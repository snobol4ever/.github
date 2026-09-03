# FINDING 2026-09-03 seat07 — `*&subject` read 0 inside an active scan (word0's `slen` clobbered by a
# bare qword tag store in the in-register fast path); a CONCURRENT-EDIT COLLISION with seat02's own,
# independent `&level` entry-side fix, found and reconciled before push. Icon master board: only 2 reds
# remain on the whole 534-entry suite (1 XFAIL-by-design + 1 unfixable-by-construction &progname line).
# One stale XFAIL marker (`rung36_jcon_kwds`) promoted, answering seat02's open ask to hq_B.

**seat07 · 2026-09-03 · freelance session (Lon direct: "pick either Icon or Prolog to perfect")**

## 0. Scope note on how this session picked its lane, and the collision that followed from it

MODE was FLEET-8 with seat07's queue row locked to a Raku test-runner task. Lon, in this session
directly, overrode that assignment in-chat ("pick either Icon or Prolog to perfect"). Per CLAUDE.md's
own loop protocol, this was recorded via `s4e_msg.sh send hq override-icon-not-raku` before starting;
the Raku row was left untouched for the Fleet. Freelancing outside the normal FLEET-8 dispatch is
precisely why §1 happened: seat02 held a properly dispatched row
(`icon-jcon-suite-39-non-pass-censused-by-class-and-cured`) touching the exact same defect this session
found independently, and nothing in either session's own view could have shown the collision coming —
see §1 for the full account, kept in full because it is the more generally useful part of this FINDING.

## 1. Concurrent-edit collision: two independent, equally-valid fixes for the same defect, reconciled

### 1a. What this session found, independently, before seeing seat02's work
Reading the same prior art seat02 also read (`FINDING-2026-08-30-seat01-icon-level-exact-fix-sites-
located-implementation-ready.md`), this session landed the SAME missing entry-side `&level` increment
in `emit.cpp`'s `flat_lcl_proc` branch, via the SAME mechanism (`bb_emit_x86()` of an `x86(...)`-DSL
block mirroring `bb_define.cpp`'s `enter_env` verbatim — proven medium-complete by `_lseed`'s own
existing dual-arm emission a few lines up, so no raw-byte BINARY arm was needed, exactly the concern
the original FINDING left open). First build read a constant +1 at every nesting depth (verified with a
3-deep probe: 2,3,4 where 1,2,3 was expected, ruling out doubling and pointing at one additive
constant). This session's diagnosis: the READ side, not the write side — `keywords.c`'s `&level`
dispatch returned raw `rt_k_level` with no `-1`, unlike `kw_fnclevel`'s own formula for the same shared
counter. Fix: `keywords.c:345`, `INTVAL(rt_k_level)` → `INTVAL(rt_k_level - 1)`. Verified byte-identical
against the real oracle `rung36_jcon_level.expected` in both modes, full battery green (Icon smoke,
master board 377→379, SNOBOL4 control arm 1679/1679 unmoved, `emit_no_lang` gate, `strip_comments`).

### 1b. Discovered on rebase: seat02 landed an equally-valid, DIFFERENT fix for the identical symptom
`git pull --rebase` (routine, mid-session, per the project's "push freely" convention) brought in SCRIP
`0376cf07` (seat02, same day, ~same hour): the SAME entry-side increment block, landed the SAME way
(`bb_emit_x86`, mirrors the same `bb_define.cpp` reference), but resolving the OFF-BY-ONE on the WRITE
side instead — changing `rt_k_level`'s C-global initial value from `1` to `0` (`rt.c:392`), reasoning
that `main`'s own activation should go through the same entry-side bookkeeping as every other Icon
procedure, so the old `1` baseline double-counted it. Both fixes are internally consistent and both
were independently verified against the SNOBOL4 control arm as non-regressing.

The rebase applied CLEANLY — no textual conflict — because seat02's insertion point and this session's
insertion point were textually disjoint (theirs inside the `if(g_is_text){}else{}` block via a
`_level_incr` variable emitted from both arms; this session's was a separate block appended AFTER that
block, same branch). **A clean git apply is not evidence of semantic compatibility.** With both landed,
`rt_k_level` gets incremented TWICE per entry (once by each mechanism) against ONE decrement per exit
(seat01's already-landed exit side, untouched by both), so the counter drifts +1 net per call — this
session's OWN keyword-read fix then silently compensated for exactly the wrong half of it, producing a
value that was right for main() alone by coincidence-of-arithmetic and wrong the moment a full board run
exercised the multi-entry cases: **`board_icon_master.sh` read `378` (not the pre-rebase-verified `379`)
immediately after the SECOND rebase pulled `0376cf07` in — a REGRESSION, caught by re-running the gate
after the rebase (per CLAUDE.md's own "re-prove your gate" rule) rather than trusting the earlier,
now-void measurement.**

### 1c. Reconciliation, and why this session's redundant half was the one removed
Kept seat02's landed fix (already on `main`, properly dispatched, and the lower-diff-churn side to keep
now that it exists) and reverted BOTH of this session's now-redundant/now-wrong pieces: the duplicate
`emit.cpp` entry-side block (removed entirely — seat02's `_level_incr` already does the job) and the
`keywords.c` `-1` adjustment (reverted to the original raw `INTVAL(rt_k_level)` — with seat02's
init-value fix in place, the raw read is already correct, and this session's `-1` on top of it would
have under-counted by one). Re-verified from a pristine rebuild: all three of this session's own
witnesses (`rung36_jcon_level.expected`, `procedure_scan_write_1.ref`, `procedure_alt_fail_replace_1.ref`)
byte-identical again in both modes; Icon smoke 14/14; Icon master board back to `379`/`381` run-graded
(matching the pre-collision measurement exactly — the collision cost a rebuild-and-recheck cycle, not a
wrong number in the end); SNOBOL4 control arm re-run clean a third time.

**The generalizable lesson**, worth keeping past this one incident: a queue row lock (this session had
none — it was freelancing) is not the only collision surface in a many-seat environment: two sessions
reading the SAME prior-art FINDING can independently, correctly, and un-conflictingly land two DIFFERENT
fixes for the SAME root cause, and a clean rebase will not say so. The only thing that caught it here was
re-running the actual gate after every rebase rather than trusting a pre-rebase measurement — exactly
the rule CLAUDE.md already states, now with a concrete instance behind it.

## 2. `*&subject` reads 0 inside an active scan — independent of §1, unaffected by the collision

### 2a. Symptom, narrowed by direct probing rather than assumption
The board's third original red, `procedure_scan_write_1`, showed `*&subject` (SIZE of the scan subject
keyword) as 0 where 4 was expected, inside a `? { }` scan block, while `&subject` alone (no `*`) printed
the correct string value in the SAME statement. A first hypothesis ("scan-specific") was falsified by a
minimal probe: `*&subject` outside any scan is ALSO 0, but that is CORRECT there (no scan active, subject
is legitimately empty) — the real, reproducible defect is `*&subject` (and even `t := &subject;
write(*t)`, an assigned COPY) both reading 0 while INSIDE an active scan where `&subject`'s VALUE is
demonstrably correct (`value=abcd` printed correctly from the same scope).

### 2b. Root cause — read from `descr.h`'s actual layout, not guessed
`DESCR_t` packs `{uint8_t v; uint8_t mod_op; uint16_t src_node; uint32_t slen;}` into ONE 8-byte word
(word0), with the pointer/union as a separate word1. `bb_keyword_icon.cpp`'s `g_scan_regs_live` fast path
for `&subject` (used specifically when inside an active scan, where the subject lives in registers
r13=ptr/r15=len per the box's own comment) built word0 with a single `x86("mov", ZRES(0), (long)DT_S)` —
a bare qword store of the compile-time tag constant, which zeroes `slen` (and `mod_op`/`src_node`) along
with it, since all four fields share that one qword. `write(&subject)` prints correctly because printing
walks the pointer directly; only the SIZE read (`*`) touches `slen`. The `call rt_keyword_subject`
fallback arm (used when NOT in an active in-register scan) returns a properly-packed `struct DESCR_t` via
the C ABI and was never wrong — confirmed with `*&progname` before diagnosing further — so this is
scan-register-path-specific, not a general "size of a string keyword" defect.

### 2c. Fix — reused an existing sibling helper, no new addressing primitive, no `shl`/`or`-immediate
`ZRESD(w)`/`FR(off)` (the dword-sized siblings of `ZRES(w)`/`FRQ(off)`, already defined in `x86_asm.h`
next to the qword versions this box already used) let word0 be built as two dword stores instead of one
clobbering qword store: `ZRESD(0) = DT_S` (tag, correctly scoped to 4 bytes now) and `ZRESD(4) = r15d`
(the live length, into `slen`'s actual byte range). Applied to both of this box's arms (the `_.op_zres`
ZRES form and the frame FRQ/FR form) — both had the identical bug. `or`-with-an-immediate is not even
implemented in this encoder (checked before assuming it as an option); the two-dword-store form needed
no new primitive and matches this exact FR/FRQ ↔ ZRESD/ZRES pairing convention already used pervasively
elsewhere in the file.

### 2d. Verification
`procedure_scan_write_1` oracle-identical both modes; the standalone `subj_probe3.icn` probe
(value/size/assigned-size) all correct; `test_gate_emit_no_lang.sh` OK (neither this fix nor §1's
now-reverted attempt introduced a language identifier into `emit.cpp`/templates); `strip_comments.py
--check` clean on the touched file (the `x86("comment", ...)` calls are assembly-comment STRING
ARGUMENTS emitted into the generated `.s`, not C source comments — a different thing from what that gate
polices); SNOBOL4 control arm unaffected (`bb_keyword_icon.cpp` is Icon-gated by `kw` string match, lower
shared-surface risk than §1's `emit.cpp`, but re-run anyway).

## 3. What is NOT a defect — `procedure_every_alt_replace_4`'s residual `&progname` line

The board's ONLY remaining real FAIL (after §1 landed via seat02, §2 landed here, and — per a fresh
census this session ran, see §5 — the other four reds the original ceo census named
[`procedure_record_limit_replace_1`, `procedure_record_every_replace_2`, `procedure_scan_while_1`, and
`procedure_alt_fail_replace_1`'s own cset/type-image line] were ALREADY resolved by other concurrent work
by the time this session measured, not touched here) is `&progname`: expected `rung36_jcon_kwds` (the
file's ORIGINAL name before absorption into the `ALL.icn` master suite), actual
`procedure_every_alt_replace_4` (the absorbed entry's auto-generated name). `&progname` correctly returns
the CURRENT running program's actual name — correct compiler behavior; the mismatch is a structural
consequence of the master-suite absorption renaming the file, not a bug reachable by any compiler
change. Confirmed independently: `rung36_jcon_kwds` graded as its own block-suite entry inside
`corpus/tests/icon/rung36_all.icn` (a DIFFERENT suite, where the entry keeps its own name) now passes
FULLY in both modes — see §4.

## 4. Rider: one stale XFAIL marker promoted — this answers seat02's own open ask

seat02's FINDING (`FINDING-2026-09-03-seat02-icon-jcon-suite-census-and-level-cure.md`) measured the
STRICT rung suite (`test_icon_rung_suite.sh`, same underlying `corpus/tests/icon/` files, a three-mode
view) moving `264/6/1/27` → `266/4/1/26/1(XPASS)` of 298 after their `&level` cure, and explicitly left
the XPASS witness unidentified, asking hq_B to find and promote it. This session's OWN full-suite run
(`test_icon_all_rungs.sh`, the mode-2 category view over the SAME files) surfaced the same signal —
`rung36_all: xpass=1` — and named it directly: `SUITE_LIST_ALL=1 corpus_suite_harness.py run
rung36_all.icn rung36_all.ref` prints `XPASS(marker stale, promote it) ... rung36_jcon_kwds` in both
modes. Per this project's established convention (script comment: "seat15, xpass-promotion-xfail-
hygiene, 2026-08-29") the stale ` XFAIL` marker token was removed from BOTH mirrored banner lines
(`corpus/tests/icon/rung36_all.icn:1038` and the matching banner inside `rung36_all.ref` — the harness
refuses on a banner mismatch between the two files, which is how the second copy was found rather than
missed). Re-verified: `rung36_all` board now reads `m3_pass=42 ... xfail=0 xpass=0 · m4_pass=42 ...
xfail=0 xpass=0` (was `pass=41 xfail=0 xpass=1`).

## 5. Numbers, named on every axis (RULES.md convention), measured AFTER the §1 reconciliation

Icon master board (`board_icon_master.sh`, `corpus/tests/icon/ALL.icn`, RT_OPT=-O0, pristine build,
`--modes m3,m4 --by-modes-column`, m3=`--run` m4=`--compile`, both graded independently, no SPITBOL
oracle involved — these are Icon-suite refs):
- Before this session (SCRIP `1bcfba40`, the fresh pull this session started from): ast-graded 153/153;
  run-graded m3 PASS=377 m4 PASS=377 / 381 (three FAILs at that point: `procedure_scan_write_1`,
  `procedure_alt_fail_replace_1`, `procedure_every_alt_replace_4` — the other three reds the ceo's
  original census had named were ALREADY resolved between that census and this session's start).
- After seat02's `&level` fix landed (pulled via rebase) + this session's §2 `*&subject` fix, both
  reconciled per §1c: ast-graded 153/153 PASS (unchanged); run-graded m3 PASS=379 m4 PASS=379 / 381.
- Combined: 532/534 — the 2 remaining: 1 XFAIL (by design) + 1 FAIL that is §3's unfixable-by-
  construction `&progname` artifact, not a compiler defect.
- Floor re-pinned in `board_icon_master.sh`: `ICON_MASTER_M3_PASS_FLOOR`/`_M4_PASS_FLOOR` 377 → 379.

SNOBOL4 control arm (`test_corpus_snobol4.sh`, RT_OPT=-O0, pristine, both modes, master block total=1726
m3/m4 xfail=70 xpass=0): PASS=1679 FAIL=0 both modes, GATE OK — re-run three times across this session
(after §2 alone, after the §1 collision was discovered, and again after the §1c reconciliation), since
`emit.cpp`'s `flat_lcl_proc` branch is shared cross-language surface and a rebase had moved the tree
each time.

## 6. State

Files touched by this session's SURVIVING changes: `SCRIP/src/templates/bb/bb_keyword_icon.cpp` (§2),
`SCRIP/scripts/board_icon_master.sh` (floor re-pin), `corpus/tests/icon/rung36_all.icn` +
`corpus/tests/icon/rung36_all.ref` (§4). `SCRIP/src/emitter/emit.cpp` and `SCRIP/src/runtime/keywords.c`
were touched and then reverted back to seat02's landed state (§1c) — net zero diff on those two files
relative to seat02's `0376cf07`. Row `icon-level-keyword-not-tracked`: closed by seat02's `0376cf07`, not
by this session — this FINDING's §1 documents the collision and independent confirmation, not a second
closure. `icon-scan-subj-cglobal-retirement`'s sibling `*&subject`-size defect: cured here as a rider to
this session's board investigation, not that row's own stated scope (that row is presumably about the
`scan_subj` C-global's retirement, a different concern; this fix is in the register FAST PATH, not the
global-fallback path the row likely targets — read that row before assuming this FINDING closes it).
`tests-consolidate-icon` (hq_B, was `PARKED-AWAITING:icon-level-keyword-not-tracked`): its park condition
is cleared by seat02's fix, flagged here for hq_B's own attention, not landed by this session.
