# FINDING 2026-07-27b — THE FC BASELINE WAS 99.1% BY-DESIGN; AND "WHAT IS CONVERTED" IS NOT READABLE FROM `fc_geom`

SCRIP commits: `a885f492` (ZLS-CALL-BASE) · `2603dc46` (FC-AUDIT discriminate) · `537e2638` (FC-108 closed).
Gates at every step: mode-3 crosscheck **314/1 with the fail SET identical to a rebuilt pre-change baseline**
(counts alone were not accepted as proof); FC gate green; codegen byte-identity proven by md5 where claimed.

## 1. A BASE-CONVENTION HAZARD CLASS — THREE INSTANCES, ONE SHAPE

Every instance is the same error: **a SHIFTED base combined with an UNSHIFTED size/formula.**
`zls_grant_locals` is handed `off = node_base + 16`; `zls_off()` returns `e->loff` (the shifted locals base for
the `zls_locals_shifted` family); `zls_node_bytes()` measures from `e->off` (the RESULT base). Mixing them is
silent — nothing crashes, no wrong address is emitted, a map is simply wrong.

- **(a) call arms (FIXED, `a885f492`).** All three arms in `zls_grant_locals` computed field offsets in
  node-base terms while receiving a locals base, so every registered call field sat one quad high; two arms
  additionally used `off * j` — a base MULTIPLIED by an arg index. The s92 repair had named that typo but
  fixed only the `PROC_GEN`/`CALL_VALUE` arm's SHAPE, keeping its node-base formula. Emitter truth
  (`bb_call.cpp`, plain and by-name-gen alike): `argbase = resoff+16`, arg j at `argbase+16*j`, extra quad at
  `resoff+16*(1+nargs)`. MEASURED on `REPLACE(S,'lo','LO')`: argv registered `+0/+48/+96` — a phantom DESCR
  landing on ANOTHER node's result quad at +0 — against the emitter's `+48/+64/+80`. Corrupted the FIELD MAP
  only (the emitter computes argv addresses itself): scope `lo_off/hi_off`, `zls_node_bytes`, the GC kind map.
- **(b) `op_own_ci` / C_i (FIXED, `537e2638`).** `zls_off() + zls_node_bytes()` = `loff + bytes` overstated
  every shifted node's end by exactly the shift. `IR_MATCH_BREAK` (result@63792 + cnt/cur@63808, true end
  63824) reported `ci=63840` — 16 bytes INTO the next node. Now `zls_result_off() + zls_node_bytes()`.
- **(c) the `zls_elide_ok`→IR_CALL rung premise (FALSIFIED, not landed).** The cursor's rung asserted
  "234 dead, **zero locals**". `IR_CALL` is NOT zero-locals: the default arm grants `1 + n_operands` argv
  quads, and `zls_grant_elide`'s elide path returns BEFORE `zls_grant_locals`, so admitting it would drop
  every argv registration. Salvage = a per-instance predicate (`n_operands == 0`, excluding tab/move and
  staged-gen), which is a signature change, not a whitelist edit.

**SWEEP (this session):** the remaining surface is narrow and clean. `zls_off()` returning the shifted base is
the INTENDED contract for the shifted family; the bug arises only when combined with a size measured from the
result base, and `zls_node_bytes` has exactly ONE consumer outside `zeta_storage.c` (now fixed). The region
math inside `zeta_storage.c` uses `e->off` consistently. **HARDENING RECOMMENDED, NOT DONE:** export
`zls_node_end(nd)` = `e->off + bytes` so the composition cannot be performed wrongly by a caller.

## 2. THE FC GATE WAS MEASURING CORRECT BEHAVIOUR — 13,006 → 108 → 0

`x86_fc_hit` counted ANY granted box whose offset left its window. That conflates three events:

| class | meaning | verdict |
|---|---|---|
| OWN + full-cell | box with an `fc_geom` cell addressing its OWN field outside it | **the defect** |
| OWN + window-only | `IR_MATCH_HEAD` — `op_fc_wbytes` is a DOCUMENTED partial window | by design |
| CROSS | the offset belongs to ANOTHER node | normal emitter behaviour |

HEAD is the crux: `cursor`/`zeta_mark`/`zls2_mark` are cell-resident at +0/+8/+16, while `head.end`,
`head.dcap_mark`, `head.incoming_rbp` are marked *"FLAT on both paths — post-unwind lifetime"* and are read by
RELEASE/REPLACE **after the cell dies**. Those accesses MUST land on rbp. Counting them made the gate's own
zero-assert architecturally unreachable — the ratchet was pinned to a floor nobody had identified. **Same
class as s184's discovery that the gate was scoring wall-clock patience as data.**

MEASURED on `demo/expression.sno` (11,662 of the old 13,006): OWN/full-cell **108** · OWN/HEAD **6,936** ·
CROSS **4,618**. The residual 108 then ALSO proved to be an artifact — 2 `IR_MATCH_BREAK` boxes whose reads at
+20/+24 land in the NEXT node's result quad (neighbour reads; every consumer reads its operand's slot), scored
OWN only because of hazard (b). **True corpus residue = 0.** `FC_BASELINE` 13006 → 0.

⚠ **ZERO DOES NOT MEAN CONVERTED.** It means no granted box addresses its own field outside its cell. This is
written into the gate header so a later session cannot misread it.

## 3. COVERAGE IS NOT READABLE FROM `fc_geom` — AT LEAST SIX MECHANISMS

The correction that matters most for the widening ladder. A per-kind conversion status requires consulting ALL
of these, not `fc_geom`'s whitelist:

1. **`fc_geom` cell grant** — ARB/SPAN/TAB/RTAB/BREAK/BREAKX/BAL/REM, ALTERNATE (`fc_alt_fpmax>=0`),
   ASSIGN_SAVE (`fc_save_active`), LIT_*/VAR (`fc_vlit_active`), Icon SCAN_TAB/MOVE/MATCH.
2. **Zero-cell BY LAW** — no box-private RW scratch, so a zero cell IS the FORTH form: SN4 LEN/ANY/NOTANY/
   POS/RPOS; Icon ANY/MANY/POS. Nothing to convert.
3. **Zero-cell BY RETIREMENT** — `IR_MATCH_SEQUENCE` via `fc_seq_active` (ZB-FC-3b): *seq_i/delta retired, the
   LIFO stack position IS the element index.* **SEQUENCE IS ALREADY CONVERTED.**
4. **Partial window** — `op_fc_wbytes` (HEAD): rebases FR/FRQ without arming the α-sub/ω-add hook.
5. **Cross-box cell read** — `op_fc_disp = fc_cond_fp(nd)` (ASSIGN_COND / ASSIGN_IMM): converted as READERS of
   SAVE's cell, owning none themselves.
6. **Tail participation** — `op_tail` (ARBNO tail-granted statements), `op_defer_leaf_susp` (DEFER).

**CONSEQUENCE — A PRIOR LIST IN THIS SESSION WAS WRONG.** A census counting fields in the FLAT-frame map
(`--dump-zeta`) ranked HEAD 570 / CALL 405 / SEQUENCE 66 / DEFER 64 / FENCE1 32 / ARBNO 30 / VALUE 6 and
proposed SEQUENCE→DEFER→FENCE1→VALUE as a cheap "Tier 1". That census cannot see mechanisms 2–6, and SEQUENCE,
DEFER, FENCE1, ARBNO, ASSIGN_COND and ASSIGN_IMM all engage FORTH machinery in their emit arms already.
**Do not order a widening ladder from the flat-frame field census.** Build the status per kind from the six
mechanisms first; that map does not exist yet and is the real prerequisite rung.

## 4. NEXT

- Build the per-kind conversion-status map from all six mechanisms (prerequisite to any widening ladder).
- `IR_CALL` (405 flat local fields) is the largest genuinely uncommitted kind — audit its argv cross-box
  contract now that the field map is correct.
- `IR_MATCH_HEAD` (570) needs the RELEASE/REPLACE post-unwind lifetime resolved before any widening.
- Export `zls_node_end()` (hazard-class hardening, §1).
- `expression.sno` emits **4.47M lines of asm** and terminates; `beauty.sno` does not terminate. Same order of
  pathology, possibly one cause — worth pairing with the s184 beauty investigation.
- Corpus path defect corroborated: `test_crosscheck_snobol4.sh` sets `INC=$CORPUS/programs/snobol4/demo/inc`,
  which does not exist (`beauty_suite/` is real) — the same stale path s184 found in `REPO-corpus.md`, live in
  the gate script's `SNO_LIB` seed.
