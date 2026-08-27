# FINDING seat09 — Icon `tab`/`move`'s β-restore block is correctly emitted and permanently unreachable: a dead-code defect wearing a state-management costume, root-caused during icon-n3's STEP-1 contamination hunt

**Front:** queue row `icon-n3-scan-one-depth-authority`, hq_P's 2026-08-27(b) STEP 1 requirement (root-cause the jcon_scan
cross-contamination symptom, ASM-DIFF-FIRST, before ruling on scan_subj's scope). Routed as its own FINDING per hq_P's
2026-08-27(b) ruling: *"THE FINDING IS BETTER THAN THIS RUNG'S OWN HYPOTHESIS AND SHOULD BE ROUTED AS ONE... the shape
recurs and this is the cleanest witness of it we have."* ⛔ **Diagnosis only — the fix is NOT landed**; tracked as NEXT
item 6 in `icon-n3-scan-one-depth-authority.task.md`. Do not read this FINDING as a closed row.

**Build:** SCRIP `89c8c654` (the two unrelated fixes landed that same session — `:=:` result-operand swap, cset
`image()` escaping — are not this finding's subject; see that commit's own message for those). Verified against the
real Icon oracle at `/home/resources/icon-master` (`bin/icont` + `bin/iconx`, confirmed present and runnable).

## 1. The symptom looked like state corruption. It was a missing jump.

`&subject:="abcdefghij"; every write(tab(1 to 4));` on SCRIP prints `b,c,d,e` where real Icon prints `a,ab,abc,abcd`
(oracle-confirmed). Three sessions' worth of scan-cursor hypotheses (the 7 falsified attempts at `835f4131`, all
do-not-retry) treated this as a corrupted-cursor question — wrong `scan_subj`/`scan_pos`, wrong nesting save/restore,
wrong GC root. **All of them interrogated the STATE. Nobody asked whether the restore code ever RAN.**

It doesn't. `--compile` ASM-diffing the emitted `.s` for both a bare and a `?`-scoped variant of the witness shows
`bb_scan_tab.cpp`'s β-block — the `mov r14,[saved-slot]` restore-on-resume code, structurally correct, α/γ/β/ω-complete
— has **zero incoming jumps** in either variant. The box is wired to succeed (γ) and to concede (ω), but nothing ever
transfers control back to its own β on resume. The restore instruction is not wrong. It is unreachable.

## 2. Root cause: `lower_call()` grants "resume my own box" wiring to generators by name, and `tab`/`move` aren't on the list

`src/lower/lower_icon.c`, `lower_call()` ~line 167:
```
cx->beta = (icn_proc_is_generator(name) || gb) ? call : (...)
```
`find`/`upto`/`bal` (`gb`, built with `IR_CALL_BUILTIN_GEN` at line 148) and user-defined generator procs
(`icn_proc_is_generator`) get `cx->beta = call` — wire the box's own β as the resume target. `tab`/`move`
(`is_cursor_mover`, computed one line above this condition and already used elsewhere in the same function for
scope-narrowing) are **not** included, so they fall through to the argument-chaining branch and their own β is never
a jump target from anywhere. The retyping pass at ~line 297 that later relabels the node's op (to
`IR_CALL_BUILTIN_ICON` or `IR_SCAN_TAB`) runs AFTER β/ω wiring is already finished, so both the generic by-name call
path and the specialized scan path inherit the identical gap — it is one bug, not two.

## 3. Why the obvious one-line fix is wrong, and why that's informative rather than a dead end

Adding `is_cursor_mover` to the line-167 condition does not fix this — it hangs. Confirmed by execution (90MB of
repeated output before kill). The reason generalizes: `cx->beta = call` only lands on a node's **β** port if
`ir_is_generator_kind(call->op)` recognizes that node's op-kind (`lower_icon.c:18-21`: recognized → `lc_ω_to_β`,
unrecognized → `lc_ω_to`, i.e. **α**, fresh re-entry). `IR_CALL_BUILTIN_GEN` (what `gb` builtins get, line 148) is in
`ir_is_generator_kind`'s switch (`src/optimizer/ir_query.c:17-39`); plain `IR_CALL`/`IR_CALL_BUILTIN_ICON`/
`IR_SCAN_TAB` (what `tab`/`move` get) are not. So the naive fix routes the "resume" jump to `tab`'s **α** — a fresh
re-invocation with stale/unadvanced arguments, forever. ASM-diff before/after the naive fix shows exactly this:
`n6_call_builtin_icon_β: jmp n5_call_α` (wrong port, right box) versus the unfixed `jmp n4_to_β` — i.e. once the jump
exists at all, it already lands on the correct BOX, just the wrong PORT on it. That localizes the real fix to op-kind
recognition, not wiring intent, and rules out a large class of alternative explanations (wrong box entirely, scan_subj
involvement) in one measurement.

Two real fixes follow from this, neither attempted: (a) give `tab`/`move` their own IR op-kind, added to
`ir_is_generator_kind`'s switch, with its own emission route rather than inheriting `gb`'s `CALL_ROUTE_BYNAME_GEN`
(untested for `tab`/`move`'s actual by-name + `rt_scan_sync_out/in` calling convention); (b) make
`ir_is_generator_kind` name-aware (touches ~15 call sites across 5 files: `lower_icon.c`, `lower_raku.c`,
`lower_snobol4.c`, `lower_prolog.c`, `emit.cpp`). The naive fix was reverted, not pushed — `git show 89c8c654` is
clean of it.

## 4. The generalizable lesson

**A block that is correctly emitted, reads correctly on inspection, and would pass any review that does not check
reachability is not evidence the mechanism it implements is correct.** This is the same *family* as
`FINDING-2026-08-19-s172-the-last-three-medium-guards-were-a-store-in-the-wrong-file.md`'s lesson (state duplicated
because it lived in the wrong place) but is not that lesson — this is a **graph-wiring** defect, not a **storage**
defect: the code is in the right place and asks the right question, but nothing routes to it. Where a state-costume
defect hides behind "is the value right?", a wiring-costume defect hides behind "does this code look right?" — the
tell in both cases is the same discipline: ASM-diff-first, and specifically check what jumps to a block, not just
what the block does when reached.

## 5. What this does and does not close

**Confirms:** the substring-length symptom (`tab(1 to N)` losing its first yield and over-advancing) is fully
explained by this one wiring gap, independent of `scan_subj`/`scan_pos`/GC roots/`x86_scan_sync_out-in`/
`g_scan_regs_live` — the computed basis for hq_P's STEP-2 scope split (scan_subj retirement is now its own row,
`icon-scan-subj-cglobal-retirement.task.md`, not gated on this fix).

**Does NOT confirm:** whether the SAME mechanism explains the OTHER jcon_scan symptom — one `write()` printing a
different, earlier `write()`'s literal text. That is plausible (a stale r14 feeding `rt_substr`'s offset/length could
read an adjacent buffer and look exactly like this) but not independently isolated with its own minimized repro.
Tracked as `icon-n3-scan-one-depth-authority.task.md` NEXT item 5 — hq_P's explicit STEP 2, still open.

**Does NOT close:** the actual fix. Two candidates identified in §3, neither landed. Tracked as NEXT item 6 in the
same task file.
