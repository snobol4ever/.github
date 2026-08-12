# FINDING-2026-08-12o — MODE34: 5a root-caused and fixed; it was silently wrong in mode-3 too; the monitor cannot see 5b

**Session:** Claude Opus 5, GOAL-MODE34-IDENTICAL, following FINDING-2026-08-12n. Build green (`install_system_packages.sh`, `make -j4 scrip`, `make libscrip_rt`, gdb 15.1 present). SPITBOL oracle cloned (`/home/claude/x64`, public, no credential). Two SCRIP commits landed locally: `dbd85305` (the 5a fix) and `88b5f393` (census TSV). **Not pushed — no credential this session; see PUSH STATUS at the bottom.**

---

## 1. 5a ROOT-CAUSED AND FIXED — and it is NOT the bug the previous session named

FINDING-2026-08-12n filed 5a as a `_.nid` uniqueness problem ("either the same call node's TEXT emission is invoked twice somewhere in the mode-4 walk, or `_.nid` isn't actually unique across those three call nodes (e.g. an optimizer clone that didn't renumber)"). **The first disjunct is right and the second is wrong, and the distinction matters** — a session that went hunting for a nid-renumbering bug in the optimizer would have found nothing and burned the session, because `bb_node_id`'s dense hash table is provably collision-free.

**Measured, not inferred** (instrumented `bb_node_id` to log every call; then dumped `codegen_flat_chain_body`'s `nodes[]` array per chain):

- `bb_node_id` under `g_m4_dense_nid=1` is a pointer-keyed open-addressed table. Every distinct `IR_t*` gets a distinct id. The three `CHAR()` call nodes got ids 4, 7, 10 — correctly distinct. The colliding label came from **id 4 being emitted twice**, i.e. the SAME node walked twice, each time correctly minting the same name.
- The duplication is NOT between the DEFINE's two proc-table citizens as one might guess. `sno_build_call_stub`'s by-name stub graph (`IR_SAVE_RESTORE` role-3 WIRE-ADOPT → `IR_GOTO_DEFERRED`) walks **exactly 2 nodes** — clean, verified by `nodes[]` dump (`n=2`). It transfers by NAME at runtime through `rt_goto_transfer` and structurally reaches nothing.
- The duplication is between **`LBL__foo`'s own standalone `emit_chain` call** and **`main`'s own top-level `emit_chain` call**. `main`'s chain dumped `n=30`: 11 nodes of its own statements, then all 18 nodes of `foo`'s body, pulled in by `codegen_flat_chain_body`'s "pass 1: entry + enterable-chain roots" group-root pass (`zls_g_group_count`/`zls_g_group_anchor`, `gc=2`). That body was already fully emitted moments earlier as `proc_LBL__foo`.

**Mechanism, stated once so nobody re-derives it:** a plain DEFINE mints `LBL__<entry>` as a SHARED-GRAPH pseudo-proc — `proc_entry_node` = the label's anchor *inside main's own graph* (`lower_snobol4.c` ~2538, the `!g_sno_uses_code` arm; the SN4-FLAT-PROC O(n) design that replaced the old O(n²) re-lowering). It gets its own `emit_chain` and emits the body once, correctly. Separately, `zls_group_mark_anchor` registers EVERY labelled statement's anchor against main's graph (`lower_snobol4.c` ~2031), and main's own `emit_chain` pulls all of them in as orphan-proofing roots. The two mechanisms overlap completely for any label that is also a DEFINE entry.

**Fix (`dbd85305`, `src/emitter/emit.cpp`, +38/-1):** `emit_chain_mark_entry_emitted` / `emit_chain_entry_already_emitted` — a pointer set recording every node that has been the `entry` of a standalone `emit_chain` call; the group-root pass skips anchors already in it. Marked at the TOP of `emit_chain`, using the raw pre-entry-chase `entry` parameter, because that is the same pointer identity the ZLS registry stores (both derive from `bb_label_landing`/`anchor[i]`) — mark and lookup therefore compare by identical `IR_t*` with no chase-drift possible. Anchors with no dedicated proc are never marked and pull in exactly as before, so the pass keeps doing the orphan-proofing job it exists for.

## 2. ⭐ THE PART THAT CHANGES THE LADDER: 5a WAS CORRUPTING MODE-3 TOO, SILENTLY

This was not predicted by 12n and is the most consequential thing in this session.

The group-root pass's guard is `(!g_is_text || entry == g_emit_cfg->entry)`. **`g_is_text` is 0 in mode-3**, so the left disjunct short-circuits TRUE and the pass fires UNCONDITIONALLY on every mode-3 chain. Mode-3 therefore suffered the same double-walk — but a binary emitter has no assembler to reject a duplicate symbol, so instead of a loud `as` error it produced **silently wrong code**.

Measured on the 5b repro, same tree, only the 5a commit differing:

| | mode-3 | mode-4 |
|---|---|---|
| before `dbd85305` | empty string | `   hello` (untrimmed) |
| after `dbd85305` | `   hello` (untrimmed) | `   hello` (untrimmed) |
| SPITBOL oracle | `hello` | `hello` |

So 5a's fix moved mode-3 from one wrong answer to a *different* wrong answer that now AGREES with mode-4. **12n's "both modes wrong, differently — this rules out 'one mode is right, port the fix'" conclusion about 5b was itself an artifact of 5a**, and it is now retired: after the fix the two modes agree, and 5b is ONE bug, not two independent ones. That is a materially easier hunt than the one 12n handed off, and whoever takes 5b should start from the post-fix state, not 12n's description.

⚠ **Generalise this, because the class is bigger than this bug:** any defect whose loud arm is a mode-4 assembler/link error has a silent mode-3 twin wherever the emitter path is shared. A mode-4-only symptom is not evidence of a mode-4-only defect. This is the same lesson M34-6d recorded for harnesses, applied to defects.

## 3. Regression evidence (the gate this rung demands)

Full crosscheck (318) re-run before and after, same box, same build, `RT_OPT` default (no `-O2`, per O2-DIRECTED-ONLY):

**TOTAL=318 IDENTICAL=254 DIFFER=16 M3-MISS=46 M4-MISS=1 BOTH-FAIL=1** — before AND after, and the DIFFER and M3-MISS **program SETS diffed byte-identical**, not merely the counts (the s22b law: counts lie, diff the sets). Census committed as `SCRIP/docs/MODE34-PARITY-CENSUS-2026-08-12b.tsv` (`88b5f393`) — this also picks the convention 12n's open item 4 asked someone to pick.

Gates: `test_gate_emit_no_lang.sh` green. `test_gate_template_medium_invisible.sh --strict` baseline UNCHANGED at 12 (`bb_glue_flat.cpp` 4, `xa_flat.cpp` 8) — verified by stash/compare, pre-existing debt in files this session never touched.

**Honest read of the flat census: this fix resolved ZERO of the 16 DIFFER entries.** 12n hoped 5a "plausibly explains multiple DIFFER entries at once"; measured, it explains none of them in this corpus. `test_string` specifically was checked and is NOT a 5a case — it compiles fine both before and after, and its mode-4 binary SEGVs identically pre- and post-fix (verified against the pre-fix binary; not a regression I introduced). The fix is nonetheless real and load-bearing: it fixes a general shape (any statement calling the same by-name builtin 2+ times inside a DEFINE'd function), it is the reason mode-3 and mode-4 now agree on the 5b repro, and it removed a silent mode-3 miscompilation.

## 4. 5b: NOT root-caused. The monitor is blind to it, and that blocker is itself worth fixing.

Repro (unchanged from 12n; oracle-confirmed `hello` via `/home/claude/x64/bin/sbl -b`), now failing IDENTICALLY in both modes with `   hello`:
```snobol4
	DEFINE('foo(s)ws,r')                    :(foo_end)
foo	ws		=	' '
	s POS(0) (SPAN(ws) | '') REM . r	=
	foo		=	r				:(RETURN)
foo_end
	OUTPUT = foo('   hello')
END
```
Semantics re-grounded against the SPITBOL manual this session (Ch.6 + Ch.20): `POS(i)` is a zero-width cursor ASSERTION that never consumes and "waits for the cursor"; `SPAN(s)` matches one-or-more longest; the manual's own idiom for a nullable span is exactly `(SPAN(S) | '')`; `.` is CONDITIONAL assignment, deferred until the WHOLE match succeeds (unlike `$`, which is immediate — manual Ch.20 §3 names the two explicitly). So the expected behaviour is unambiguous and SCRIP is wrong, in both modes, identically.

**MONITOR-FIRST was attempted and is BLOCKED — do not read this as "the monitor was skipped".** `PARTICIPANTS="spl scr" test_monitor_3way_sync_step_auto.sh` reports DIVERGE at step 2, on the `LABEL stno` sync event, at statement 1 — i.e. before any pattern matching happens at all:

```
| 1 | 1 | LABEL stno=INT=1 | LABEL stno=INT=1 |
| >2| 1 | LABEL stno=INT=5 | LABEL stno=INT=6 |
```

Isolated with two control programs:
- `OUTPUT = 'hello'` + END → 3 steps, **full agreement, exit 0**. So stno numbering is NOT generically mismatched.
- A minimal `DEFINE('foo(s)') :(foo_end)` with no pattern matching at all → **same divergence shape**, SPITBOL 3 vs SCRIP 4.

So: SPITBOL and SCRIP disagree by a constant +1 on the goto-target statement number of a `DEFINE(...) :(label)` line — a statement-COUNTING CONVENTION difference (which lines count as statements around DEFINE/label-only lines), not a semantic defect. Output is correct in both control programs. But the controller treats it as a hard stop, so **the monitor can never reach 5b's actual divergence**, and every future DEFINE-bearing SNOBOL4 hunt is blocked the same way.

Per RULES.md ("If the monitor is ... blind to the divergence CLASS ... reinstating/extending it comes first"), the next 5b session's FIRST task is the monitor, not the pattern bug. Two options, cheapest first:
1. **Tolerate a constant stno offset** in `scripts/monitor/monitor_sync_bin.py`'s comparison: learn the per-participant offset at the first LABEL disagreement and compare offsets thereafter; a CHANGE in the offset is the real divergence. Cheap, local, and preserves the theorem.
2. **Reconcile the numbering** by finding which side counts the label-only line (`foo_end`) — more correct, more invasive, and arguably not worth it since the absolute numbers have no cross-engine meaning.

I did NOT do either, because doing it properly is a rung of its own and I would rather hand it off clean than half-land it.

## 5. Plan scrutiny — corrections folded into the goal file this session

- **M34-5's framing is too narrow.** It is written as "mode-3 coverage parity — fill missing BINARY arms" (M3-MISS). This session found a mode-3 defect that is not a missing arm at all but a shared-path bug whose mode-3 arm was silently wrong. M34-5 needs a second half: *shared-path defects whose mode-4 arm is loud and mode-3 arm is silent*.
- **The `entry == g_emit_cfg->entry` guard is vacuous and should be audited independently of this fix.** It is TRUE for every graph whose entry parameter equals its own `g->entry` — which is every single-node stub and every top-level chain. Whatever it was written to mean ("only for main's own chain"), it does not mean that. My fix routes around it rather than repairing it; someone should decide what it was FOR. Filed as a new M34-7c.
- **D1 remains unverified.** I did not get to the timing A/B. Still the cheapest open item on the board and still worth doing first by whoever picks this up cold — it costs one measurement and settles a wrong mental model that every reader of this file currently inherits.
- **12n's item 5 ("check whether the other DIFFER entries share 5a's or 5b's root cause") is now partly answered:** they do NOT share 5a's. The `*_pat_arbno_defer_*` / `*_pat_cap_*` cluster is untouched by it and remains the obvious candidate for one shared mechanism.

## PUSH STATUS
Computed, never typed — `scripts/handoff_status.sh` output is pasted in the handoff message. Two SCRIP commits (`dbd85305`, `88b5f393`) and this `.github` commit are LOCAL ONLY; `git push` failed with `could not read Username for 'https://github.com'`. Credential requested in-chat per RULES.md 6b. **This handoff is BLOCKED until that push succeeds.**
