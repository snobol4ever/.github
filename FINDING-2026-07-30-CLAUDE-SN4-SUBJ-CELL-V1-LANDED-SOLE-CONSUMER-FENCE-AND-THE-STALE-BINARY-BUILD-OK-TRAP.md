# FINDING 2026-07-30 — SN4 SUBJECT-CELL v1 LANDED (rung (a)): the sole-consumer fence, and the stale-binary "BUILD OK" trap

**Session directive (Lon, verbatim intent):** every BB allocates its own RESULT (iff present and used) and LOCAL STORAGE (iff any) by ONE instruction (`sub rsp, K`); sliding offsets, operands indexed from RSP; **NO frame-relative addressing for operands — none**; RBP only for housekeeping (STATEMENT / FUNCTION / ARBNO / FENCE1).

## WHAT LANDED
The s21x-e measured frontier (first UNREGISTERED rejects across 316: LIT_STRING 157 · VAR 85 · LIT_INTEGER 29 — ordinary scalars in SUBJECT position) is now served: the subject producer chain registers into the ONE fc registry and **IR_MATCH_HEAD POPS the 16B subject DESCR from TOS** (`mov rdi,[rsp+0]; mov rsi,[rsp+8]; add rsp,16`) at the very top of α — replacing the `FRQ(op_sa)/FRQ(op_sa+8)` flat-slot operand read (emit.cpp drive promoted `op_sa = drive_value_slot(subj)`).

Four touch points, all env-gated `SCRIP_STMT_FRAME=1 && SCRIP_SUBJ_CELL=1` (the fc_call_ok two-env precedent — gate-off registration is ZERO):
1. **zeta_storage.c `zls_build` SUBJECT loop** — mirrors the IR_ASSIGN value-spine loop member for member (same leaves via `fc_vtree_scan`, same γ-adjacency fence `r->γ.node == h`, same d-simulation/wpop, same all-or-nothing capacity). fc_call arms cannot appear (the first zls_build loop zeroes `g_fcc_gfence` for every MATCH_HEAD-bearing graph). LIT_CHARSET subjects stay flat (runtime type-error path).
2. **emit.cpp MATCH_HEAD drive** — promotes `g_emit.op_subj_cell` from `fc_vread_fp(nd) >= 0` under ZC_FRAME_RSP + ZC_PORT_FORTH. fvr is node-keyed; sharing the ASSIGN registry cannot collide (line-866's consumer only ever sees IR_ASSIGN nodes).
3. **emit.cpp stmt-frame classifier** — HEAD is `fc_geom` 0 BY LAW (self-releasing 32B window, never summed), so its regime license is the fvr read registration — planner and classifier read ONE authority. γ is already always enqueued, so licensing the head extends the walk into the pattern body where every element faces the fc conjunct honestly.
4. **bb_match_head.cpp** — the `subjc()` pop arm at the TOP of α, **before any flat-spelled access**, so α's remaining depth equals the flat arm's exactly and `fc_leaf_walk`'s D=32+prefix math for every downstream pattern box is untouched. rdi/rsi survive to `rt_match_enter` (intervening saves touch only rcx/rax/r13/r14/r15/rbp; the non-RSP-frame rt_zls_mark arm cannot fire — promotion is gated ZC_FRAME_RSP). One `x86()` concat, both media by construction.

## LAW — THE SOLE-CONSUMER FENCE (the 062/063/cross/wordcount casualty class, measured then cured in-session)
First gate-ON run regressed exactly four programs, both modes: 062_capture_replacement, 063_capture_null_replace, cross, wordcount — **the replacement class**. Root cause is structural, not a bug in the arm: `sno_lower_match` pushes `subjval` into the SPLICE node too, and the splice reads the subject's FLAT slot post-match; under SUBJ_CELL the producer wrote the cell and the head popped it. The fence is pure dataflow, no kind naming: **registration requires the head to be subjval's ONLY operand consumer** (scan `g->all` for any other node holding subjval in `operands[]`; any hit declines). Replacement statements decline wholesale and stay flat-verbatim — degrade never die. Replacement subjects are lvalues with post-match readers; making THEM ride cells is the rung's named follow-up.

## WATERMARK (chunked crosscheck, 4×~79 shims — background jobs die between tool calls in this container, s126 fragility confirmed again)
- Session start, pre-edit: m3 311/4 · m4 311/2 SKIP=2 · DIVERGE=2 (140/141) — held vs s21x-i baseline.
- **Gate OFF, post-edit: m3 311/4 · m4 311/2 SKIP=2 · DIVERGE=2 — HELD EXACTLY, membership identical** {m3: test_case, 140, 141, 160 | m4: test_case, 160}.
- **Gate ON (both envs), with the fence: m3 311/4 · m4 311/2 SKIP=2 · DIVERGE=2 — IDENTICAL to gate-off, membership identical.**
- `.s` regen ×3 (benchmark / feature / demo): **zero changed artifacts** — default-path byte-identity proven corpus-wide (feature sweep's test_string EMIT-FAIL is the pre-existing s189 stale-tracked class).
- Non-vacuity: 19 `[rsp + 0]` cell reads in one two-match witness compile; pop shape verified at both head αs in m4 text; m3+m4 oracle-exact on literal-subject, VAR-subject, concat-tree-subject, and FAIL-path witnesses; `[FCS] decline SOLE-CONSUMER` verified firing on 062.

## TWO SELF-INFLICTED SPLICES (recorded so the shape is recognizable — both from editing off TRUNCATED views)
1. **emit.h mid-comment splice:** built `str_replace` old_str from a `cut -c1-200` view of the one-line `flat_stmt_frame` field; the match was a PREFIX of a longer line, so the insert landed inside the comment and strand-corrupted it. **Edit from the raw line, never a truncated render.**
2. **The dropped r13 save:** the pop-insertion new_str failed to re-include the unconditional `FRQ(op_off+48), r13` PATCTX save it had consumed — corrupting the fail-exit outer-Σ restore on BOTH arms. Witnesses slid through because single-level matches never read the restored Σ; the emitted asm diff caught it.

## ⛔ THE STALE-BINARY "BUILD OK" TRAP (the session's most reusable lesson)
`[ -x scrip ]` after `make` is NOT a build check: a failed make leaves the previous executable in place, so every "witness" between the first template edit and the repair ran the PRE-EDIT binary — including green results and a false vacuity reading. **Build success = `grep -c error <log>` == 0 (both `make scrip` AND `make libscrip_rt` — the rt_pic TUs recompile emitter headers), plus the binary mtime moving.** This is the s126 `.so`-mtime rule generalized to the driver.

## 📋 PARKED, PRE-EXISTING (repro banked, not this rung's dig)
`SCRIP_STMT_FRAME=1` alone (no SUBJ_CELL), PRISTINE-tree binary: `Z = 5 + 3; OUTPUT = Z; END` prints correct "8" then **SIGSEGV (rc=139) in m3**. Reproduces identically pre- and post-slice; gate-off clean. The crosscheck harness MASKS this class: it captures stdout with `|| true` and compares text only, so a post-output crash still counts PASS — the gate-on watermark cannot see it. MONITOR-FIRST when dug (RULES.md). Named: **STF-EXIT-SEGV**.

## NEXT
(1) Replacement-subject cells (retire the sole-consumer decline for the splice class — needs the splice to read the cell or a write-through ruling). (2) The armed-census sweep: with subjects registered the classifier walk now reaches pattern bodies; count new arms and the next reject kinds (RELEASE/COND are fc_geom-0 like HEAD — same fvr-license shape probably serves them). (3) STF-EXIT-SEGV (monitor-first). (4) A crosscheck harness arm that FAILS on nonzero exit status even when stdout matches, so post-output crashes stop hiding.
