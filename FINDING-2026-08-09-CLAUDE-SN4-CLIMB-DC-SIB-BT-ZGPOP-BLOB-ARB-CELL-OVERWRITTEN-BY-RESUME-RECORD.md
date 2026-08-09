# FINDING-2026-08-09-CLAUDE-SN4-CLIMB-DC-SIB-BT — ZGPOP-BLOB: ARB ζ-CELL OVERWRITTEN BY RESUME RECORD ON CLASS D BLOB γ

**Session:** s34 (Sonnet 4.6) · **Goal:** GOAL-SN4-ZETA-CLIMB C-7 (dc_sib_bt open item)
**SCRIP fix commit:** `24b54c50` · **Corpus commit:** `f8f7513a`
**Watermark post-fix:** m3 136/15/0/0 · m4 135/16/0/0 (0 regression)

---

## PROBE

`corpus/probe/dc_sib_bt.sno` — defer-β re-yield, sibling ARBNO capture:

```snobol4
        P = ARB
        Q = LEN(1)
        'ABCD' ? ((*P $ X) (*Q $ Y) 'D') $ Z       :F(NO)
        OUTPUT = '=S'                               :(EN)
NO      OUTPUT = '=F'
EN      OUTPUT = 'X=' X
        OUTPUT = 'Y=' Y
        OUTPUT = 'Z=' Z
END
```

Expected: `=S / X=AB / Y=C / Z=ABCD`. Pre-fix: SIGSEGV rc=139.

---

## MONITOR-FIRST RESULT (spl vs scr, RULES.md §1)

```
| step | stno | spl                         | scr                         |
| ---- | ---- | --------------------------- | --------------------------- |
| 7    | 3    | @3 VALUE Y = STRING(1)='A'  | @3 VALUE Y = STRING(1)='A'  | ← last agree
| 8    | 3    | @3 VALUE X = STRING(1)='A'  | @3 VALUE X = STRING(0)=''   | ← DIVERGE
```

First diverge: after `Y='A'` fires (ARB=0 chars, Q=LEN(1) matched 'A') and `'D'` fails, the chain backtracks. Oracle re-extends ARB to 1 char and reports `X='A'`; SCRIP reports `X=''` then crashes.

---

## ROOT CAUSE

### Setup

`(*P $ X)` lowers to `SAVE → DEFER(P) → IMM(X) → …`. DEFER uses the **GVA fast path** (GVA cell hit → `bb_glue_pass_wires(4,5)` = `lea rcx,L(4); lea rdx,L(5); jmp rax`) to enter the `proc_PAT$0` blob (which wraps ARB). The blob uses the **CLASS D γ protocol** (emit.cpp:2773):

> "γ SUSPENDS the activation (frame + interior state retained for β re-entry): 16B resume record {res-landing, rbp} pushed at the **deep frontier** — the invoker's β edge `jmp qword [rsp]` reads the landing word, the res stub restores rbp and falls into the chain's resume dispatch."

The design: blob γ pushes `{proc_PAT$0_res, blob_rbp}` at the **ζ-cell depth** (ARB's cell still carved at `[rsp]`). DEFER's outer β (`jmp qword [rsp]`) reads `proc_PAT$0_res`, jumps there, `add rsp,8; pop rbp` consumes the record, leaving rsp at the ARB-cell level, then falls through to `proc_PAT$0_β: jmp [rbp+32]` which re-enters ARB's β.

### The bug

`zd_plan` runs for blob graphs (CARVE-DATA-ERAD deleted the jmp-entry veto, emit.cpp:2013). For ARB (`zd_k=16`), it computes `zd_gp[arb]=16` (statement-terminal γ release). The ZGPOP-STF choke at emit.cpp:841:

```c
g_emit.op_zgpop = g_emit.flat_stmt_frame ? 0 : g_zd_gpop;
```

In a blob (`flat_stmt_frame=0`), `op_zgpop = g_zd_gpop = 16`. The γ hook in x86_asm.h:2263 then emits `add rsp, 16` before `jmp proc_PAT$0_scanhit`.

This fires ARB's γ-free **before** the blob's `proc_PAT$0_γ` pushes the resume record. Result:

```
rsp before ARB α:    rsp_blob − 0    (blob base)
ARB α:               sub rsp,16  →  rsp_blob − 16  (ARB cell at [rsp])
ARB γ:               add rsp,16  →  rsp_blob       ← ⚠ SPURIOUS FREE
proc_PAT$0_scanhit → proc_PAT$0_γ:
  push rbp            rsp_blob − 8   (blob rbp)
  push res_addr       rsp_blob − 16  (resume record at [rsp])
  jmp L(4)
```

Resume record lands at `rsp_blob − 16` — same address where the ARB cell was, now overwritten. DEFER's β fires: `jmp [rsp]` → `proc_PAT$0_res` → `add rsp,8; pop rbp` → rsp = `rsp_blob`. Falls to `proc_PAT$0_β: jmp [rbp+32]` → `n0_match_arb_β`. ARB's β reads:

```asm
add dword ptr [rsp + 0], 1    ← [rsp_blob + 0]: blob frame header, not ARB counter
mov eax, dword ptr [rsp + 4]  ← [rsp_blob + 4]: blob frame header, not start cursor
```

ARB reads garbage as its extension counter and start cursor. r14 gets a wrong value. `rt_cap_open(X, saved_delta=0, cur_delta=wrong, is_imm=1)` fires → X='' (or crashes trying). rc=139 (SIGSEGV).

---

## FIX

**Location:** emit.cpp:841 — the ZGPOP-STF choke, the ONE authority for `op_zgpop`.

**Change (one conjunct added):**
```c
// Before:
g_emit.op_zgpop = g_emit.flat_stmt_frame ? 0 : g_zd_gpop;

// After:
g_emit.op_zgpop = (g_emit.flat_stmt_frame || (g_emit.flat_jmp_entry && g_emit.flat_pat)) ? 0 : g_zd_gpop;
```

**Reasoning:** CLASS D blobs (`flat_jmp_entry && flat_pat`) must retain all ζ-cells across γ so the resume record pushes at the true deep frontier. The blob ω unwinds absolutely (`lea rsp,[rbp+kt]`) — no γ-free is needed or safe. The ZGPOP-STF precedent (`flat_stmt_frame ? 0`) is the same mechanism for the same reason: a different authority already handles cleanup, so the hand-counted pop is dead weight that corrupts the protocol.

---

## COLLATERAL

`zleak_matchbegin_stfh` was an XPASS in both modes at session open (parallel session fix had already landed). Retired from XFAIL in the same corpus commit per RULES.md §4.

---

## PROOF THAT EXISTING GREEN TESTS ARE UNAFFECTED

The `add rsp, K` suppression on blob γ is safe because:
1. Blob ω: `lea rsp,[rbp+kt]` — absolute unwind from ANY arrival depth. The K release on ω still fires (via `x86_add("rsp", op_wpop)` or the blob's own ω arm); `op_zgpop` controls only γ.
2. ARB ω (blob exhausted): restores r14 to start cursor from `FR(scratch+4)` = `[rbp+scratch+4]` (rbp-relative, depth-immune), then blob ω fires absolute unwind. No rsp arithmetic needed.
3. All other passing probes that use DEFER fast-path blobs either (a) never trigger DEFER's outer β (blob's first γ is the only one; right siblings all succeed) or (b) use the DEFER slow path (rt_defer_open/step/close) which manages blob lifetime separately.
