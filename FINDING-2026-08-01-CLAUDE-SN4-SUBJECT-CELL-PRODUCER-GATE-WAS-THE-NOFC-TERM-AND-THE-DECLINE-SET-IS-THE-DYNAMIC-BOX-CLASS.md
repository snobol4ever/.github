# FINDING 2026-08-01 (s22y) — SN4 SUBJECT-CELL: the producer gate was the NOFC term, and the decline set is the dynamic-box class

**Session:** s22y, Lon grant "All your choices. I'm with you on this." · SCRIP `6a0a58d2` · .github cursor `34eb1ca9`
**Watermark:** m3 220/97/1 · m4 217/100/1 (reproven at open) → **m3 233/84/1 · m4 229/88/1 · DIV 4 {test_stack, 164, 170, 1016}** — ZERO broken by set, both modes.

## 1. The s22s "producer-side gate UNLOCATED" is one term on one line

`zeta_storage.c` fc_geom's vlit grant read `fc_vlit_active(nd) && !zc_nofc()`. The `!zc_nofc()` term landed s22l to retire the ASSIGN-pair producer half (correct: ZD serves those consumers). The SUBJECT-CELL rung shares the same fvl registry, but its consumer — IR_MATCH_HEAD, ZD's 247-strong first-blocker — cannot be ZD-served. After s22r flipped NOFC default-on, every subject producer lost its grant while the head's promotion (`fc_vread_fp`, no NOFC term) armed unconditionally: consumer-armed/producer-flat, the exact displacement the s22s bare decouple measured and the s22x event trace saw as rdi=0x401125 (the head's flat read landing in the carve corpse — in 052, producer wrote `[rsp+288]` inside its own carve = rbp−16 while the head read `[rbp+288]`, 304 bytes away above the pin).

**Fix (zero template edits):** `fvs[]` membership table populated beside the direct-pair registration; the grant line becomes `(!zc_nofc() || fc_subj_member(nd))`. The fc_hit rebase does the rest — the granted producer's `FRQ` spellings become `[rsp+0/8]` TOS writes over its own `sub rsp,16`, and the head's existing subjc arm pops them at α top before any flat access, so downstream D=32+prefix math is untouched (verified: armed-vs-flat `.s` diff is exactly the producer/head pair, 15 lines, nothing else — checked FULL, not head-truncated). The binop-tree subject branch now requires `!zc_nofc()` so it can never again arm consumer-only. Gate decoupled to ONE env (`SCRIP_SUBJ_CELL`; the STMT_FRAME conjunct rode the dead s21x STF-default era), proven zero-delta off, then DEFAULT-FLIPPED (killswitch `=0`) on the s22r proof shape.

## 2. The decline set, and the two casualty classes that forced it

Registration declines any graph bearing **IR_MATCH_DEFER / IR_MATCH_PATREF / IR_MATCH_FENCE1** (degrade never die). Measured casualties of arming them:

**(a) Blob re-entry class — 117 (*cmd defer) / 142 (stored-eps PATREF), BOTH modes.** m3: SEGV at ARBNO iteration 2, rip=0x1000, rbp=0x100001 (DESCR-shaped restore garbage) with r15=Δ=3 — the subject itself arrived CORRECT; the kill is downstream, in the stored-pattern blob's geometry. m4: silent rc=0 with `rt_match_ctx_restore` NEVER called (neither match exit ran); m3 frame chain points into statement-1's slab region (the FENCE blob built there, re-entered at match time). Named suspects for the follow-on: the ARBNO deep repoint `mov rbp,rsp; add rbp,-248` — a STATIC depth-model constant — and the blob wire glue, both of which predate the subject grant.

**(b) Inline-FENCE m3 exit-scan spin — 061/107, m3 only.** Output CORRECT AND COMPLETE, then hang (rc=124 at 20s): the m3 exit path spins after the last write, at a 16-sensitive boundary. m4 same bytes exits clean — the boundary comparison passes in m4's stack geometry and spins in m3's. **Repro recipe (the spin does not exist at HEAD):** remove IR_MATCH_FENCE1 from the decline scan, rebuild, `scrip --run 061_pat_fence_fn_seal.sno` — output appears, process never exits. First bracket for the follow-on: attach to the hang and sample rip (ptrace attach works in this container once the process exists; note /proc/sys/kernel/yama is absent here).

At HEAD-default, 061 runs 21ms rc=0 correct — the decline is doing its job.

## 3. Instrument notes (paid for this session)

- `rt_defer_open/step` breakpoints NEVER fire on 117 — the `*cmd` defer rides the compiled-blob arm, not the C stored-pattern machinery. Do not bracket stored-pattern bugs at the rt_defer surface.
- The 2-way monitor is DARK for this build (scr side emits zero trace events; controller reads PARTIAL EOF at step 2 regardless of where the program actually dies). MON-RE is prerequisite before monitor-first applies to this class.
- `grep -l '\*'` over `.sno` matches the `*` comment convention — worthless as a defer detector; read the statements.
- A `.s` regime diff piped through `head` is not a diff — the 117 audit was only trustworthy after `diff | wc -l` proved the hunk count.
- Deep-arrival graphs REPOINT rbp to the statement claim base; `[rbp+K]` ledgers done against the graph pin are wrong there. The repoint is the `mov rbp,rsp; add rbp,-K` pair, and K is emitter-static — the first thing the blob-arming rung must audit against the +16 grant.

## 4. Handoff state at write time

SCRIP `6a0a58d2` and .github (cursor `34eb1ca9` + this doc) are LOCAL, 1+ ahead of origin; push attempted and failed (no credential in container: "could not read Username"). Handoff is BLOCKED pending credential per RULES — this doc is written before the push so the push carries it.
