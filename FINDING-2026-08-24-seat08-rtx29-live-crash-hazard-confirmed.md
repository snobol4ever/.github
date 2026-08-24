# FINDING — seat08: RTX-29 (`.Lsub_table_int`) is a CONFIRMED LIVE SIGSEGV, not a latent hazard — 5-line Icon repro, 8/8 reproductions

**Date:** 2026-08-24 · **Seat:** seat08 (FLEET-8) · **Row:** `audit-rtx29-icon-table-int-chain-walk-post-s262` (rank 0) · **Build:** `make pristine` EXIT=0, RT_OPT=-O0 (default; no `-O2` anywhere, s262/s266 FACT RULE) · **Tree:** SCRIP `57d507d9` (clean pull, no local changes at time of this FINDING).

## 0. Verdict, up front

**Branch 3 of the row's own decision tree: NONZERO HITS ON THE DANGEROUS DEREFERENCE ITSELF.** This is not the historical-traffic-only case the row was minted to check for — it is a **present-day, trivially-reachable, deterministic SIGSEGV** in `rt_subscript_var` (`src/runtime/rtx/rtx_icnsub.S`), reachable from ordinary Icon source using nothing but the language's own `table()`/`t[i]` syntax on a plain local variable. Per this row's own NEXT block: *"escalate to Lon/HQ immediately... before doing anything else... rather than fixing blind."* This FINDING is that escalation. **No runtime code has been changed.**

## 1. The minimal repro

```icon
procedure main()
    local t, i;
    t := table(0);
    every i := 1 to 5 do
        t[i] := i;
    every i := 1 to 5 do
        write(t[i]);
end
```

Run: `./scrip repro.icn < /dev/null` → prints `1`, `2`, `3`, then **SIGSEGV, rc=139, core dumped.**

Bisected by hand: N=1..4 keys run clean (rc=1, unrelated to this defect — see §5); **N=5 crashes 8/8 reruns**; N=6..9, N=10, N=20, N=30, N=50, N=500 all crash too (checked N=1..10, 20, 30, 50, 500). N=5 is the smallest witness found and is stable, not ASLR-flaky, across 8 consecutive runs.

## 2. Crash site and root cause, from a live gdb trace

```
Program received signal SIGSEGV, Segmentation fault.
rt_subscript_var () at src/runtime/rtx/rtx_icnsub.S:396
396         mov     r11, [r10 + TBPAIR_KEY]
r10            0x8b68              35688
r11            0x0                 0
x/gx $r10  ->  Cannot access memory at address 0x8b68
```

Line 396 is inside the hash-then-chain-walk block RTX-29 re-enters via `jmp .Lsub_hash_init` (line 815) — the exact PRE-s262 mechanism this row's GOAL flagged: `r10` is loaded a few lines earlier as `tb->buckets[hash & 0xFF]` (a **hardcoded 256-way mask**), then blindly dereferenced as a `TBPAIR_t*` chain node (`mov r11, [r10 + TBPAIR_KEY]`, `TBPAIR_KEY` offset 0). Under the live s262 table layout (`core.h:130-170`) `TBBLK_t.buckets` is sized to a **dynamic per-table `nbuck`** (nowhere near 256 for a 5-entry table) and holds `TBBUCK_t **` — pointers to `{unsigned len,cap; TBPAIR_t ent[];}` dense-array headers, not chain nodes. Indexing 256 slots into an array sized for a handful of buckets reads **past the real array, into unrelated heap objects** the bump allocator (`rt_agg_alloc`) happened to place nearby.

`0x8b68` is not arbitrary garbage — it is recognizable: `mov qword ptr [rax+VCELL_SV], DT_FAIL | (MOD_OP_RT_SUBSCRIPT_VAR<<8)` (this same file, line 431, `.Lsub_hit`'s own VCELL-stamping code) bakes exactly this bit pattern into every VCELL's `.sv` field, confirmed present verbatim in the built binary's disassembly (`out/libscrip_rt.so`, `331857: mov QWORD PTR [rax+0x28],0x8b68`). The out-of-bounds bucket read is landing on a **stale VCELL from an earlier subscript operation in the same run** (i=1..4 each mint one via `rt_agg_alloc`'s bump allocator) and misreading its stamped tag word as a live chain-node pointer. Small `N` (1-4) apparently doesn't yet lay out a VCELL at the exact wrong-hash offset this witness hits; `N=5` does, reliably, in this environment.

This is precisely the hazard mechanism the row's GOAL predicted ("reading a bucket header's packed struct... and dereferencing it is a near-certain SIGSEGV") — measured now, not inferred.

## 3. Reachability entry conditions (confirmed via source read + gdb, cross-checked two independent ways)

`.Lsub_table_int` fires when: subscript tag == `DT_I`, base tag == `DT_N` (a VARREF, `slen==1`, non-null ptr — i.e. a **plain identifier**, not an already-dereferenced value), and `rt_deref(base)` yields `DT_T` (a table). This is exactly what `t[i]` on a `local t` compiles to — no exotic construction needed. RTX-31 (the sibling arm added earlier today for SNOBOL4's already-deref'd `T[I]` shape) does **not** cover this: its own header says *"RTX-29 stays as-is; this is a new, additional arm, not a replacement"* — Icon's own `t[i]` on a bare variable still routes through RTX-29, confirmed live in this FINDING.

Three breakpoint offsets from `rt_subscript_var`, derived two independent ways (static objdump byte-matching against the `.S` source's `#define`d constants, AND gdb's own DWARF line-table resolution once the shared library is loaded) — both methods agreed exactly:

| label | offset | gdb-resolved source line |
|---|---|---|
| `.Lsub_table_int` entry | `+0x574` | `rtx_icnsub.S:784` |
| `.Lsub_chain` entry | `+0x24c` | `rtx_icnsub.S:394` |
| `.Lsub_cmp` (the dangerous `movzx ecx,[r11]`) | `+0x264` | `rtx_icnsub.S:401` |

Positive control (single key, `t[1]:=99; write(t[1])`): `.Lsub_table_int` and `.Lsub_chain` each hit 2 times, `.Lsub_cmp`/crash 0 times (that run's wrong-hash slot happened to land on a zeroed/unallocated region — a lucky miss, not a proof of safety). 500-key stress control: 8 hits on entry/chain then SIGSEGV on the 9th, at the same line-396 site as the minimal N=5 repro. This confirms the earlier "lucky zero" was luck, not immunity — a wrong-hash slot landing on non-null adjacent heap content is the norm once more than a handful of keys exist, not the exception.

## 4. Scope / what has NOT been done

- **No fix applied.** Per the row's own branch-3 instruction, this is escalate-first, not fix-blind. `git status` on SCRIP shows no modified tracked files from this session (only untracked scratch files under `/tmp`, not the repo).
- The row's FIRST STEP also asked for a full sweep of the real Icon corpus/benchmarks/smoke suite for hit counts — that is still in progress separately (this FINDING did not wait on it, per "escalate immediately... before doing anything else"); its results will be appended to the task file's LEDGER when done, corpus-sweep permitting.
- `N=1..4`'s `rc=1` (instead of `rc=0`) on an otherwise fully-correct run (`1`,`2`,`3`,`4` printed correctly) was observed in passing and is **not chased here** — it doesn't match this defect's signature (no SIGSEGV, correct output) and may be pre-existing/unrelated `main()`-return-value behavior. Noting it so it isn't lost, not diagnosing it.
- The unrelated `corpus/icon/samples/generators.icn` SIGSEGV found earlier in the same sweep (coexpression/string-slice related, zero tables in that program) was already routed separately: `s4e_msg.sh send hq_C icn-generators-sigsegv-unrelated-to-rtx29`.

## 5. Recommendation (not actioned — Lon/HQ's call per the row's own branch-3 text)

RTX-26's own precedent (`.Lsub_table:`, line 351-363, already stood down with a hard `jmp .Lsub_bail`, dead code kept below for reference, s262) is sitting right above RTX-29 in the same file and is the obvious mechanical fix — RTX-29 falling through to that same dead machinery is the entire defect. The row's text already anticipated this exact outcome: *"Standing it down is very likely the right answer either way; only live, nonzero, dangerous traffic changes that [calculus]"* — this FINDING is that live, nonzero, dangerous traffic. This seat is holding off on applying it only because the row's branch-3 instruction says escalate-and-repro first, not because the fix is unclear.

## 6. Repro file

Saved at `/tmp/claude-1000/-home-claude08/dd97d012-f281-4386-a20c-2b1a8ea75af9/scratchpad/mincheck5.icn` (scratch, not committed — reproduced inline in §1 above, five lines, no dependencies).

## 7. RESOLUTION (seat08, same day, 2026-08-24, after Lon/HQ ruling)

**hq_C ruled (s272): apply the stand-down.** Exactly §5's recommendation — mirror RTX-26's own s262 precedent, verbatim in shape: a hard `jmp .Lsub_bail` as the first live instruction after `.Lsub_table_int:`, old itoa+chain-walk body kept below, dead, for reference. Do not attempt to make the arm correct against the current table layout; the C fallback this bails to is already the correct, already-existing behavior (same ruling as RTX-26). Graded on all three frontends with a same-tree control arm per the shared-node verdict scope rule, since the machinery this arm falls into is the same shared dead code RTX-26 already stood down.

**Safety of the jump, verified before applying (not assumed):** both `.Lsub_table` (RTX-26) and `.Lsub_table_int` (RTX-29) are reached at the identical `sub rsp, 88` frame depth from the one shared dispatch prologue (`rtx_icnsub.S:212-230`, `.Lsub_table` at line 224, `.Lsub_table_int` at line 230, no stack adjustment between them) — the bail restores `[rsp+0..24]` as the caller's original pre-`rt_deref` arguments and tail-jumps to `c_rt_subscript_var`, which is exactly as valid from either label.

**Measured, control vs. treatment, same rebased tree (`git stash`, not two separate pulls — the rebase-baseline corollary's "same tree plus the one change" satisfied structurally), pristine `-O0` builds, repeated three times end-to-end as the fleet pushed concurrently underneath this row:**

| check | before (control) | after (treatment) |
|---|---|---|
| 5-line repro (§1), 3-5 reruns each build | SIGSEGV, rc=139, 3/3 | clean, rc=0, correct output `1 2 3 4 5`, 0/5 crashes (5/5 runs) |
| SNOBOL4 corpus (`test_corpus_snobol4.sh`) | PASS=338 FAIL=0 both modes | PASS=338 FAIL=0 both modes — **identical** |
| Icon smoke (`test_smoke_icon.sh`) | 14/14 both modes | 14/14 both modes — **identical** |
| Prolog smoke (`test_smoke_prolog.sh`) | 3/5, fails={clause,recursion} all 3 modes | 3/5, same fail-set all 3 modes — **identical** |

SNOBOL4 confirms zero regression at 338/338 rather than the row's originally-expected 362/362 — traced to a pre-existing, unrelated demo-corpus path fossil that shrinks the script's own denominator by 22, identically on the control arm too, so provably not this defect or this fix. Not a new finding: `test_corpus_snobol4.sh`'s own header shows hq_C's s272 audit already mid-fixing exactly this class of stale nested-path fossil the same session (seat04's sibling `INC` fix, `9960787d`, landed the same day); no message sent, would be noise atop an already-in-progress cleanup.

**Landed:** SCRIP `3fce9831` (source fix), corpus `5ae0f05a` (regenerated `.s` artifacts — the runtime-sink regen chain's diffs traced entirely to concurrent seats' already-origin template commits catching up to current compiler output, never to this change, which is structurally invisible to any caller's emitted bytes). Full receipts, LEDGER, and the rewritten `DONE-WHEN` are in the task file (`audit-rtx29-icon-table-int-chain-walk-post-s262.task.md`).

**§4's noted-but-not-chased `rc=1` on an otherwise-correct run:** independently fixed the same session by another seat's unrelated commit (`e8fc3bdc`, "a failing main is NORMAL termination and exits 0, not 1") — confirmed in passing during this row's final re-verification pass (post-fix repro now exits `rc=0`, was `rc=1` on earlier builds this same session, before that commit landed). Coincidental timing, not caused by or dependent on this row's fix.
