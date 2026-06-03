# HANDOFF 2026-06-03 — Claude Opus 4.8 — ICON-BB: ICN-SCAN ladder authored (planning session)

**Goal:** GOAL-ICON-BB.md — Lon directive: a RUNG implementing BBs for EVERY Icon string-scanning
operation, ONE STEP per BB, on the SNOBOL4 register layout.
**SCRIP HEAD:** `d46b943` (local == origin/main, clean — NO code commits this session).
**.github HEAD:** this commit (ladder landed earlier at `b411947b`).

---

## One-line summary

The **ICN-SCAN LADDER** is written into GOAL-ICON-BB.md: 16 gated steps (ICN-SCAN-0 … ICN-SCAN-FENCE),
one stackless BB per scanning operation — the full canonical set from `fstranl.r`
(any/bal/find/many/match/upto) + `fscan.r` (move/pos/tab) + `?:=` scan-assign + `=s` sugar — each step
carrying its IR kind, port topology, frame slots, probe, and the per-step gate. ARCH-ICON.md gained the
matching "String scanning — the ICN-SCAN BB family" architecture section. No SCRIP code was touched.

## What this session did

1. **Full orientation** (PLAN/RULES/GOAL-ICON-BB/GOAL-ICN-GLOBAL-NV, last three Icon handoffs, canonical
   `irgen.icn` + `fstranl.r` + `fscan.r` read in full; icon-master/jcon-master extracted to `SCRIP/refs/`).
2. **Inventory answers for Lon** (BB→RT call grid; scan-site map; scan-op→BB grid) — these surfaced that
   the scanning functions had NO native boxes and routed to the `rt_call_builtin` ABORT STUB.
3. **Authored the ICN-SCAN LADDER** (.github `b411947b`) + ARCH-ICON.md section + watermark/priority
   updates (this commit). Grounding gathered first: `bb_pat_any.cpp` (the Σ/δ/Δ + `lea rdi,[rip+cset]`;
   `call strchr` idiom to copy), available `x86_ro_seal_str/_q` + `x86_frame_load/store(64)` helpers,
   the Proebsting paper (uploaded; now cited §4.1–4.5, Fig 1/2).

## The ladder (one step per box — full text in GOAL-ICON-BB.md)

- ICN-SCAN-0 `bb_gen_scan` registerize (Σ=r13/δ=r14/Δ=r15 on ENTER, ledger carries triple, δ↔scan_pos sync)
- ICN-SCAN-1 `bb_keyword` register arms (&pos = δ+1 inline; &subject from Σ/Δ)
- ICN-SCAN-2 nine IR kinds (IR_SCAN_*) + lowerer name-map + m2 delegate arms + emit_core stubs → all EXCISE
  (sanctioned fallback if m2 byte-identity resists: name→template map in the EMIT driver only)
- ICN-SCAN-3..6 `bb_scan_pos` / `bb_scan_any` / `bb_scan_match` / `bb_scan_many` — function{0,1},
  positions returned, δ untouched
- ICN-SCAN-7..8 `bb_scan_tab` / `bb_scan_move` — {0,1+}, write δ, RESTORE on β (fscan.r "reverses");
  tab's operand may be a sibling SCAN_* slot (`tab(upto(c))` is wave-1)
- ICN-SCAN-9..11 `bb_scan_upto` / `bb_scan_find` / `bb_scan_bal` — function{*} generators, frame cursor
  (+ bal cnt), β re-pump via the generator-β chain edge (`b48f0cd` mechanism)
- ICN-SCAN-12 `=s` lowerer sugar → SCAN_TAB(SCAN_MATCH) (no box)
- ICN-SCAN-13 `?:=` — `bb_gen_scan` LEAVE-γ assign arm per jcon `ir_a_Scan` "?:="
- ICN-SCAN-FENCE `scripts/test_gate_icn_scan.sh` + corpus scan-bucket sweep

**Contracts in the rung header:** register layout = SNOBOL4 verbatim (R12=ζ, R13=Σ, R14=δ, R15=Δ, RBX=NV
hash, RO `[rip+disp]`, results to own 16-byte frame slot); semantic invariant (only tab/move write δ);
wave-1 precise gating (literal args, default window, everything else EXCISEs `[SMX]`); per-step gate
(probe m2==m3==m4 · m2 corpus 130 HARD byte-identical · smoke 12/12 · kind off `icn_kind_native_stub` only
when its box lands · all FACT gates · commit per RULES).

## Gates

None re-run — no code changed. Baseline stands at `d46b943`/`eca2dcb` numbers (m2 corpus 130 HARD, Icon
smoke m2 12/12, m3/m4 corpus ~12–19 PASS with the scan/global additions, FAIL bucket per the GN-6 notes).

## NEXT (the first build step)

**ICN-SCAN-0.** Read `fscan.r` + `bb_gen_scan.cpp` + `rt_icn_scan_enter/leave` (gen_runtime.c:59–89)
first; make ENTER return/load the Σ/δ/Δ triple, push the prior triple on the ledger, restore on LEAVE,
and define the δ↔`scan_pos` sync contract at every emitted `rt_*` boundary. Gate: rung05 scan_subject +
scan_concat_subject m2==m3==m4 unchanged, smoke 12/12 HARD.

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git   /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git  /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
# canonical sources: unzip uploaded icon-master.zip / jcon-master.zip into refs/
bash scripts/test_smoke_icon.sh
bash scripts/test_icon_rung_suite.sh
# then: GOAL-ICON-BB.md → ICN-SCAN LADDER → ICN-SCAN-0
```
