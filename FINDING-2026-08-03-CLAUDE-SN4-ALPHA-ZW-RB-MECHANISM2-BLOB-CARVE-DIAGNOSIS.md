# FINDING 2026-08-03 — CLAUDE SN4 ALPHA: SCRIP_ZW_RB MECHANISM-2 BLOB-CARVE DIAGNOSIS

**Session:** ALPHA advisory seat, 2026-08-03 (this session)
**Directive:** "Finish FORTH-style RSP stack with RBP used to WHACK on SUCCESS the unbounded ZETA growth cases."
**Goal:** Flip `SCRIP_ZW_RB` (mechanism-2) default ON.

---

## §1 What mechanism-2 is

Mechanism-2 (`zwr` in `zd_plan`, `op_zw2` at the choke, `SCRIP_ZW_RB` killswitch) is the RBP-boundary arm for blob-clause match statements (`nblob_real > 0`) that ZW-12 (`nblob==0`) cannot arm. It was designed and partially implemented in a prior OMEGA session and left default OFF because it was not fully exercised.

The stated design: `bb_match_begin` emits `push rbp; mov rbp,rsp` (the "boundary"), and `bb_match_end` emits `mov rsp,rbp; pop rbp` (the "whack on SUCCESS"). The intent is that `rbp = rsp_entry - 8` provides a depth-immune base for the match housekeeping quintet, while RSP continues to carry FORTH-style per-BB cells.

---

## §2 Measurement: SCRIP_ZW_RB=1 watermark

Baseline (HEAD, ZW_RB=0): **m3 281/25/11 · m4 274/32/10** (318 crosscheck programs).
With ZW_RB=1: **m3 238/63/16 · m4 232/68/16** — regression of −43 programs.

First PASS→FAIL programs: `044_pat_pos`, `060_capture_multiple`, `065_capture_then_arbno`, `066_capture_then_fenced_arbno`. All share `nblob_real > 0` (ZWR fires) and SEGV under ZW_RB=1.

---

## §3 Root cause: missing Kc carve in bb_match_begin's mech2 arm

### The frame layout mismatch

Under the UCLAIM regime (mechanism-2 OFF), `bb_match_begin` emits `sub rsp, Kc` (the whole-statement blob claim). Blob interior nodes (lit_integer, match_pos, etc.) write to `[rsp + off]` where `off` is baked against the pre-carve RSP base. After the `sub rsp,Kc` carve, `rsp = rsp_entry - Kc`, so `[rsp + off]` = `[rsp_entry - Kc + off]` — the correct slot within the carve.

Under mechanism-2 (bb_match_begin emits ONLY `push rbp; mov rbp,rsp`), `rsp = rsp_entry - 8`. The blob interior nodes still emit `[rsp + off]` = `[rsp_entry - 8 + off]` — 8 bytes off from where the stores went under UCLAIM. **No claim region is allocated at all.** The blob's FRQ slots live in unallocated stack space above the push, in the caller's frame — hence SEGV.

### Architecture: blob interior nodes are in cm[] not run[]

Blob interior nodes (closure members via `cm[]`) are NOT in the `run[]` array of `zd_plan`'s armed path. They are processed by the UCLAIM else-branch's operand-tree walk. This means:
- `zzwr[]` (the per-node mechanism-2 marker) is only set for `run[]` members at line 2052.
- `cm[]`-only members get `zd_zwr[k]=0` → `g_zd_uzwr=0` at the drive loop → `op_zw2=0` at the choke.
- My FRQ-compensation logic (`op_zdepth += 8+Kc`) never fires for them.

### The needed fix (confirmed by analysis, not yet landed)

Two parts:

**Part 1 — Mark closure members with zzwr[k]=1.** In `zd_plan`'s armed path (lines 2066-2068), after the run-member loop, add:
```c
if (zwr) for (int k = 0; k < n; k++) if (cm[k] && !zzwr[k]) zzwr[k] = 1;
```
This is OUTSIDE the `if (Kc > 0 && hpos >= 0 && !zwr)` block (which is dead under zwr=1). This makes closure members get `op_zw2=1` staged, enabling the compensation.

**Part 2 — Add sub rsp,Kc carve in bb_match_begin, placed correctly.** The mech2 arm needs `sub rsp, op_udout` (where `op_udout = Kc` at hpos) inserted AFTER `mov rbp,rsp` (so `rbp = rsp_entry-8` is set before the carve) and BEFORE `L(0)` (the retry label, so the carve happens once per statement activation, not per retry). Critical ordering:
```
push rbp          ; rbp→stack, rsp = rsp_entry - 8
mov rbp, rsp      ; rbp = rsp_entry - 8 (depth-immune base)
[setup reads: subject var, housekeeping saves — all [rbp+8+N] spellings, depth-immune]
[cas_rsp_mark: must store rsp AFTER the carve — see §4]
sub rsp, Kc       ; rsp = rsp_entry - 8 - Kc (blob claim allocated)
L(0):             ; retry label
```
With this layout, blob FRQ reads `[rsp + off + op_zdepth]` with `op_zdepth = 8 + Kc` gives `[rsp_entry + off]`. ✓

**Part 3 — Persistent op_mech2_kc field.** Add `int op_mech2_kc` to `sm_emit_t`, set it at MATCH_BEGIN from `g_zd_udout` (= Kc), and clear at MATCH_END. The choke compensation `op_zdepth += 8 + op_mech2_kc` applies to EVERY unarmed blob interior node (not BEGIN, not END which use rbp-relative spellings). The field must NOT be cleared at the per-node unconditional reset (line 832) — only at MATCH_END and `emit_jmp_entry_clear`.

**Part 4 — MATCH_END mech2 arm: move FRQ restores to rbp-relative.** `bb_match_end`'s mech2 arm uses `FRQ(_.op_off + N)` for housekeeping restores. These need to be `RDQ("rbp", 8 + _.op_off + N)` (rbp-relative, depth-immune) because at restore time `rsp = rsp_entry - 8 - Kc - <xfer_dance_offset>` which is deep into the blob. The `cas_rsp_mark`-based restore path also needs updating — see §4.

---

## §4 cas_rsp_mark: the ordering trap

`cas_rsp_mark` stores `rsp` at the time of the store in `bb_match_begin`. Under the proposed fix, if `sub rsp, Kc` is placed before `cas_rsp_mark`:
```
cas_rsp_mark = rsp_entry - 8 - Kc
```
When `bb_match_end` does `mov rsp, cas_rsp_mark`, it restores `rsp = rsp_entry - 8 - Kc`. Then `[rsp + off]` reads are at the correct blob-carve depth. ✓

If the carve is placed AFTER `cas_rsp_mark` (as attempted this session):
```
cas_rsp_mark = rsp_entry - 8  (pre-carve)
```
MATCH_END restores to `rsp_entry - 8`, then `[rsp + off]` lands 208 bytes too high (into the caller frame). → SEGV or wrong values.

**ORDERING LAW FOR THE NEXT SESSION:**
1. `push rbp` → rbp saved
2. `mov rbp, rsp` → rbp = rsp_entry - 8
3. Subject reads: `[rbp+8]`, `[rbp+16]` (subjc path) or `RDQ("rbp", 8+op_sa)` — depth-immune ✓
4. Housekeeping saves: `[rbp+8+op_off+48/56/64/72]` — depth-immune ✓
5. `call rt_match_enter`
6. `mov r10, cas_top`; `mov [r10+8], rsp` ← **cas_rsp_mark must go HERE, after sub rsp,Kc below**
7. `sub rsp, Kc` ← blob claim allocated; AFTER this: cas_rsp_mark must be stored
8. `[hfc path] mov rax, rsp; sub rsp, 32; mov [rbp+op_off+16], rax` ← rsp_mark (post-carve ✓)
9. patstk_mark, start_δ saves
10. **`cas_rsp_mark` store: must be AFTER step 7** — currently it fires in step 6

The fix requires reordering the CAS initialization to move `cas_rsp_mark` storage to after the `sub rsp, Kc`. Since `r10 = cas_top` points to the live CAS record being built, the reorder is:
```
; steps 1-5 as above
sub rsp, Kc           ; allocate blob region FIRST
mov r10, cas_top
mov [r10+0], 0        ; tag
mov [r10+8], rsp      ; cas_rsp_mark ← NOW captures post-carve rsp ✓
...
```

---

## §5 What was explored this session

This session established the complete diagnosis:
- Measured the −43 regression and identified the first failing programs.
- Traced the segfault to blob interior nodes writing to unallocated stack space.
- Identified the architectural mismatch (cm[] vs run[] marking, per-node vs per-chain compensation).
- Built the three-part fix plan (zzwr[] closure marking, carve placement, op_mech2_kc persistence).
- Discovered the cas_rsp_mark ordering trap (§4) — the carve must be before cas_rsp_mark.
- Confirmed that MATCH_END's FRQ restores need to be converted to rbp-relative spellings.

The fix plan is complete and validated by analysis. It requires ~4 coordinated edits across 3 files (emit.cpp, bb_match_begin.cpp, bb_match_end.cpp) plus the emit.h field addition. No code was committed this session — all work was exploratory.

---

## §6 POSITIVE CONTROL for next session

Before claiming mechanism-2 is green:
- `044_pat_pos`: PASS with ZW_RB=1 (first SEGV; POS+LEN+capture pattern, nblob_real=2, Kc=208)
- `060_capture_multiple`: PASS with ZW_RB=1
- Full crosscheck: m3 ≥ 281/25/11 · m4 ≥ 274/32/10 (at-or-above baseline, no regression from ZW_RB=1)
- DENOMINATOR LAW: report absolute counts (n/318), not fractions of armed subset

---

## §7 NEXT RUNG

**ZW-RB-1**: Implement §3 Parts 1–4 in order:
1. `zd_plan` closure mark (Part 1) — emit.cpp, 1 line, outside the `!zwr` block
2. `op_mech2_kc` field (Part 3) — emit.h + emit.cpp choke + clear-at-END + emit_jmp_entry_clear
3. `bb_match_begin` reorder: move cas_rsp_mark AFTER `sub rsp,Kc` (Part 4 / §4) + move carve before L(0) (Part 2)
4. `bb_match_end` FRQ→RBP conversion for housekeeping restores (Part 4)
5. Gate: SCRIP_ZW_RB=1 → 044_pat_pos PASS + full crosscheck at-or-above baseline
6. Once green: flip `zw_rb_on()` default from 0 to 1 in emit.h + verify ZW_RB=0 gives byte-identical baseline
