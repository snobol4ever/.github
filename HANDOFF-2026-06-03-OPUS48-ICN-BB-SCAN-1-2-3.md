# HANDOFF 2026-06-03 (Opus 4.8) — ICN-SCAN-1 + ICN-SCAN-2 + ICN-SCAN-3

**SCRIP HEAD: `d629a36`** (three gated rungs: `d82003b` → `5091102` → `d629a36`, each individually
gated/committed/pushed, clean rebases onto orthogonal Pascal/Prolog/SNOBOL4 peers, post-rebase re-verified).
**Full detail = the three rung entries + Watermark in `GOAL-ICON-BB.md` (single source of truth).**

## Landed

1. **ICN-SCAN-1 (`d82003b`)** — `bb_keyword` register arms inside a native scan body: `&pos`=`{DT_I,r14+1}`,
   `&subject`=`{DT_S,0,r13}`, zero rt calls; new `g_icn_scan_regs_live` (emit_bb.c) with SAVE/RESTORE around the
   body subchain (nesting-safe); rt_icn_keyword_* fallback outside scans; m2 untouched.
2. **ICN-SCAN-2 (`5091102`)** — nine `IR_SCAN_*` kinds (IR_e END, renumber-free) + dump names; nine LOUD
   `x86_bomb` stubs `bb_scan_*.cpp` (own files, Makefile src+rules); emit_core one case per kind after IR_ALT.
   **SANCTIONED FALLBACK taken** (oracle IR_CALL arm — arg-subgraph eval, susp_gen_cache, suspend-buf, gen-arg
   odometer — resists cheap delegation): name→template routing lives INSIDE emit_core's IR_CALL case gated on
   `g_icn_scan_regs_live` (the `&`-prefix→bb_keyword precedent); lowerer + m2 STRUCTURALLY untouched. All nine
   kinds on `icn_kind_native_stub` (inert belt; the LIVE gating lever = `icn_scan_subgraph_safe` name set).
3. **ICN-SCAN-3 (`d629a36`)** — `bb_scan_pos` real: α `cmp64 r14,(n-1)` (fscan.r: succeed iff &pos==n, δ
   untouched) → `{DT_I,n}`→slot→γ; β→ω. Driver arm (emit_bb.c IR_CALL flat-chain, operand-slot promotion):
   digs literal n from `counter` blks[0] IR_LIT_I → `op_sb`; `op_off=bb_slot_alloc16(nd)` (consumer reads
   producer slot — empirically: args live in counter SUBGRAPHS, the call chains arity-0 before its consumer).
   `pos` admitted to safe set; IR_SCAN_POS off the stub list. **ENCODER FIX:** `x86_cmp_imm64` lacked REX.B for
   r8+ — BINARY `cmp64 r14,imm` encoded `cmp rsi,imm` → silent m3 scan failure while m4 (gas text) was right;
   only prior user rcx ⇒ byte-identical fix.

## Gates (held at EVERY rung)

corpus ALL THREE columns byte-identical set-diff (SCAN-1 via stash/rebuild/compare): **m2 129 HARD / m3 13
PASS+152 EXC / m4 20 PASS+91 EXC — zero PASS-set drift any mode any rung**. Smokes Icon m2 12/12 HARD · Prolog
5/5 · broker 32. Structural all green: bb_bin_t=0 · no-handencoded `--strict` · g_vstack=0 · no-stack 10≤127 ·
one-reg-frame 0≤21 · prove_lower2 · FACT=0 · new templates 0 raw-byte producers. Probes: SCAN-0/1 set all
m2==m3==m4; SCAN-3 `"abc" ? write(pos(1))`→`1` / `pos(2)`→fail **m3==m4 per canonical fscan.r**.

## ⚠ Discoveries (queued, NOT fixed — each is its own re-baseline rung)

- **m2 oracle gap (PRE-EXISTING, verified at stashed baseline):** icon-flavor by-name block
  (~`by_name_dispatch.c:2617`) has any/many/upto/tab/move/match/find but **NO `pos` arm**; generic pos (:621)
  unreached on the scan path ⇒ `write(pos(1))` empty in m2 (if/conj forms too; `write(match("a"))` works ⇒
  pos-specific). Fix flips FAIL→PASS ⇒ SUITE-HONESTY-style re-baseline rung.
- **Second oracle divergence, same block:** its `match` MOVES `scan_pos`; canonical fstranl.r `match` does NOT
  move &pos.
- PER-STEP GATE's `probe m2==m3==m4` clause is BLOCKED for pos/any-class probes until that oracle rung lands —
  gate on m2 BYTE-IDENTITY + m3==m4-vs-canonical meanwhile (as SCAN-3 did).

## NEXT = ICN-SCAN-4 (`bb_scan_any.cpp`)

Copy `bb_pat_any`'s strchr cset test; value contract: `INTVAL(δ+2)`→slot, δ untouched (fstranl.r `any(c)`
{0,1}); β→ω. Generalize the SCAN-3 driver arm from the single `pos` name to the name→kind table; dig the cset
literal the same counter-blks way, seal RO via `x86_ro_seal_str`; admit `any` to the safe set + IR_SCAN_ANY off
the stub list when the box lands. Session setup unchanged (GOAL-ICON-BB.md `## Session Setup`); extract the
uploaded icon/jcon zips into `SCRIP/refs/` if absent (CONSULT-CANONICAL-SOURCES).
