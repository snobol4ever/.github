# FINDING 2026-08-24 seat05 — json-arbno-inloop-stack-accrual was an undersized DCAP island, not a missing release mechanism

**Row:** `json-arbno-inloop-stack-accrual` (postoffice task baton, hq_P-owned, SNOBOL4 #1 rank). **Fix landed:** SCRIP `0d4a5fbf`.

## Summary

The task's own GOAL text proposed two cure directions: (a) release-at-ARBNO-commit for the r12/DCAP deferred-capture arena, mirroring the already-cured rsp/CAS fence0 leak, or (b) grammar-level in-loop fence placement. A prior session (2026-08-23) tried (a) — mirroring the blob retiring-exit's r12 restore (`emit.cpp:3183`) into `bb_match_fence0.cpp`'s dynamic-release arm — and it **eliminated the SIGSEGV but produced silently wrong output** (`root=STRING`, every census counter 0), then was reverted.

This session re-read the DCAP pump/replay design from scratch (`rt_dcap_pump`/`c_rt_dcap_end_ok_open`/`rt_match_end_all` in `pattern_match.c`, the slice-8 design comment in `rtx_match.S`, and the `head.dcap_mark` field comment in `zeta_storage.c`) rather than re-attempting a release mechanism, and concluded (a) is unsound by construction:

- `g_dcap_top` (r12) is a pure bump allocator for deferred pattern captures (`IR_MATCH_DEFER`, e.g. SNOBOL4 `. var` conditional value assignment).
- `rt_dcap_pump` only ever replays a **fixed `[mark, top)` window** opened by `c_rt_dcap_end_ok_open`, called from exactly one template: `bb_match_end.cpp` (`IR_MATCH_END`, the `?` operator's own success terminus). `rtx_match.S`'s slice-8 comment states this explicitly: "a nested match's entries (pushed above our top) are swept by its own open/close and never by ours."
- `zeta_storage.c`'s `head.dcap_mark` field comment confirms r12 is already correctly truncated on **both** exits of a match (`"α saves live-r12 pend top = this match's MARK; ω/RELEASE truncate r12 from it"`) — but only at that match's *own* boundary, not at every FENCE inside it.
- A bare `FENCE` (`IR_MATCH_FENCE0`) commits a *sub*-match — it forbids backtracking into what it fenced, but it is not the enclosing `?` match's own END. Rewinding r12 there discards deferred-capture bytes the eventual top-level pump has not read yet (and, worse, lets a *later* iteration's writes silently overwrite the rewound region before that pump ever runs) — exactly the failure the prior session measured. Early release at FENCE is only sound if paired with an early *pump* of that same span, which is a materially bigger, riskier change (and interacts with the "deferred until overall match success" transactional guarantee — SPITBOL manual v3.7 p.62's conditional-assignment rule) than this row needs.

For `json.sno`, the whole file is parsed by **one** top-level `?` match (the grammar composes `jvalue`/`jobject`/`jarray` as stored-pattern indirection, not as separate nested `?` statements), so the DCAP window never closes until the entire file is consumed. Peak r12 usage is therefore bounded — by input size × capture density — not literally unbounded, and not fixable by an earlier release point without breaking the replay-window invariant above.

## The actual bug: `RT_DCAP_ISLAND_BYTES` was 4MB with no bounds check anywhere on the write path

`pattern_match.c:612` (`#define RT_DCAP_ISLAND_BYTES (4u << 20)`) is passed to `rt_slab_region`, which rounds up through `rt_slab.c`'s fixed klass table (64KB/1MB/16MB) — so the *actual* allocation was already 16MB by accident, not the nominal 4MB, and nothing tracks or checks that ceiling on the append side (unlike the sibling `RT_CAS_ISLAND_BYTES` arena, which does: `pattern_match.c:590`, `"raise RT_CAS_ISLAND_BYTES"`). Once writes exceed the malloc'd chunk, behavior is undefined — measured previously (2026-08-23 gdb) as a SIGSEGV inside a `MATCH_DEFER` chain (`mov qword ptr [r12+8],rsi`).

Measured density: ~8.4 bytes of r12 growth per input byte (2026-08-23 gdb, N=1200 synthetic: 14.5MB growth / 1,726,800 input bytes). `json.sno`'s own `INPUT(.INPUT, 9, '[-f0 -r4194304]')` hard-caps every possible subject at 4,194,304 bytes regardless of what's piped in, so the worst-case DCAP demand *for this program, for any input* is bounded at ≈4,194,304 × 8.4 ≈ 34MB — this is not an unbounded leak, it's an undersized fixed buffer for a legitimately bounded requirement.

## The fix

One line, `src/runtime/pattern_match.c`: `RT_DCAP_ISLAND_BYTES` 4MB → 64MB (`(size_t)64u << 20`, matching the `RT_PL_CELLWS_ISLAND_BYTES` precedent exactly — same magnitude, same idiom, comfortable headroom over the derived 34MB worst case for this program and more for others). No codegen touched — pure runtime constant, zero emitted-`.s` impact (spot-checked m3≡m4 byte-identical on the witness below).

**Not done, flagged as a follow-up, not blocking this row:** the DCAP write path (generated assembly, not one C function — unlike CAS's `rt_cas_carve`) has no bounds check at all, so a future workload that legitimately exceeds 64MB will still fail as an unexplained SIGSEGV/heap corruption rather than a clean `abort()` with a "raise RT_DCAP_ISLAND_BYTES" message. Adding one means touching the deferred-capture append site in generated code (`bb_match_defer.cpp`-adjacent codegen), which is out of scope for this row's DONE-WHEN and carries its own codegen risk; a candidate follow-up row, not attempted here.

## Receipts (SCRIP HEAD `447faf10` + this commit `0d4a5fbf`, RT_OPT=-O0, `make pristine`)

Full detail and exact commands in the task baton's LEDGER (`json-arbno-inloop-stack-accrual`). Headline: same-tree paired A/B on the N=1500 synthetic witness (`corpus/probe/json_fence0_leak/gen_synth_perf.py 1500`, 2,158,501 bytes) — re-confirmed the crash on *today's* pulled tree before crediting the fix (REBASE-BASELINE COROLLARY: the original 2026-08-23 crash measurement predates today's pull) — `rc=139` SIGSEGV without the change, `rc=0` with it, correct proportional census (objects/arrays/integers/nulls per record exactly match the independent N=2900 run). N=2900 (largest N under json.sno's own 4MiB INPUT cap) is a clean, non-truncated SUCCESS. The task's literal DONE-WHEN (N=4000, which truncates at the INPUT cap) passes (`rc=0`) and is not vacuous — the truncated 4.19MB subject is larger than the N=1500 witness that crashed pre-fix. Broad corpus unregressed: `test_corpus_snobol4.sh` m3 362/362, m4 362/362 SKIP=0. Standard/variant json witnesses (`json.input`, `json-match.sno`, `json-match-fence.sno`) byte-identical to their `.ref`. m3≡m4 byte-identical on the N=1500 witness.

## Links

- Task baton: `/home/resources/postoffice/tasks/json-arbno-inloop-stack-accrual.task.md`
- Commit: SCRIP `0d4a5fbf`
- Prior/related: `FINDING-2026-08-23-seat04-json-fence0-static-release-cant-see-past-alternation-unbounded-stack-leak.md` (the sibling, already-cured rsp/CAS leak this row was explicitly distinguished from) · GOAL-SNOBOL4-100.md line 98 (cross-reference, not updated by this session — task-baton is now this row's authoritative record per ARCH-FLEET-CEO.md).
