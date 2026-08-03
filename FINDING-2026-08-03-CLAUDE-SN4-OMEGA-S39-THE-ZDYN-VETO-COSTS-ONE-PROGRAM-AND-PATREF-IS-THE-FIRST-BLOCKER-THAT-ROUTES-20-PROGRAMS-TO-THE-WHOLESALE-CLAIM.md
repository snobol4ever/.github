# FINDING s39 (2026-08-03, OMEGA) — the zdyn veto's justification set is EMPTY except one program, PATREF is the first blocker for the whole pattern-statement class, and the FLAT glue already exists

**Parent:** SCRIP `c0c77585` (U-1a skeleton). **This session commits:** SCRIP `4e2ba87d` (ZD-PATREF measurement gate, default OFF, 318/318 byte-identical off).

**Lon directive this session (verbatim intent):** every BB allocates its own RESULT (if used) and LOCALS (if any) by one `sub rsp` instruction; operands index from RSP with sliding offsets, never RBP; walk until a genuine BRICK WALL, then add the RBP dance there and only there; STATEMENT / FUNCTION / ARBNO / FENCE1 are the known RBP constructs; no frame merely to call a constant-folded pattern; two glues (FLAT jump-there/back, FRAMED push-frame + jump-there/back + unframe); ONE traversal computing zeta offsets; no function-level scoping, statement-level only.

---

## 1. THE MODEL IS ALREADY LIVE FOR 100 OF 120 PROGRAMS — MEASURED, NOT ASSUMED

Census over `corpus/programs/snobol4/*.sno` + `csnobol4-suite/*.sno` (first 120):

| shape | count |
|---|---|
| pure per-BB carve (`sub rsp,16` per α, no `stmt_claim`) | **100** |
| wholesale UCLAIM (`sub rsp,<claim>` + N zero stores) | **20** |

The compliant witness is already the default emission:
```
n1_var_α:   sub rsp,16 / mov [rsp+0],rax / mov [rsp+8],rdx / jmp n2_...
n1_var_β:   add rsp,16 / jmp <pred>
```
That β shape is ALSO the UNWIND ruling's shape (box frees OWN K, rolls to pred) — **the per-BB allocation model and the unwind model are the same model.** They do not need reconciling.

`x86_alpha_carve(K)` (x86_asm.h:1708) is already the one-instruction `sub rsp,K`. `zls_build()` (`src/contracts/zeta_storage.c:403`) is already the ONE graph traversal accumulating offsets. `SCRIP_SLOT_ELIDE=0` is already the elide killswitch. **None of this needs building.**

## 2. THE 20 ARE NOT THE FUNCTION CLASS — THEY ARE THE PATTERN CLASS

15 of the 20 have **zero DEFINEs**:

```
8bit 400B · alt1 384B · any 256B · breakx 704B · collect2 160B · len 176B
match 160B · match2 160B · match3 176B · match4 176B · matchloop 176B
ops 1680B · repl 192B · uneval 176B · unsc 272B
  (with DEFINE: bal 160B · nqueens 1872B · roman 240B · sudoku 4944B)
```

`alt1.sno`, `any.sno`, `len.sno`, `match.sno` are plain top-level pattern statements with no procedure anywhere. **The standing prose blames jmp-entry / `LBL__` pseudo-procs. That is true of roman only and is NOT the common factor.** The common factor is pattern matching. This corrects the PLAYBOOK §0 non-compliant-witness attribution, which named ZD-4 + ZD-7 from the roman case alone and generalized from n=1.

## 3. `proc_LBL__ROMAN_α` IS ALREADY EMPTY — THE 240 BYTES ARE MATCH_BEGIN

Measured in the emitted `.s`:
```
proc_LBL__ROMAN_α:
proc_LBL__ROMAN_α_body:
n0_statement_begin_α:   jmp n1_var_α      <- zero instructions in the alpha
```
There is nothing to delete at the α. The 240B block is `n2_match_begin_α: sub rsp,240` + 30 `stmt_claim` zero stores — the UCLAIM wholesale arm (x86_asm.h:2053), not a procedure frame.

`IR_SAVE_RESTORE` **already exists as a real BB** (`n38_save_restore_α`). Its body is `call rt_flat_ret_snap@PLT` + `mov rcx,[rax+0]; mov rbp,[rax+24]; mov rsp,[rax+16]; jmp rcx`. The requested SAVE_RESTORE + CALL pair is present; the CALL half is a C call, which is the medium complaint, not an absence.

Residue that IS ceremony and can go once (2) is closed: `proc_LBL__ROMAN_res: add rsp,8; pop rbp` and the γ/ω `mov rsp,rbp; pop rbp; call exit@PLT` pair (the "blob γ that exits the process" already named in the s22u/s22v EXIT-CLASS ledger).

## 4. THE `zdyn` VETO'S JUSTIFICATION SET IS STALE — COST IS ONE PROGRAM

`SCRIP_ZD_DYNARM=7` (force DEFER + PATREF + FENCE1 all armed) vs bracket, full crosscheck-318 BY SET:

| | bracket | DYNARM=7 |
|---|---|---|
| m3 | 280P/35F/2T | 280P/35F/2T |
| m4 | 274P/40F/2T/1L | 273P/41F/2T/1L |

BY SET the entire delta is **two programs**:
- `066_pat_fence_fn_nested` PASS→FAIL (both modes) — the sole casualty
- `152_pat_json_keyvalue_renamed` m3 FAIL→**PASS** — a gain

The comment at `emit.cpp:1977` justifies the veto with flip set `{135,136,164,165,183}` + `{117}`. **All six now pass armed.** The intervening ZD/ZW work fixed them and nobody re-measured the veto that was protecting them. This is RULES rot-class (a) in a new costume: a decline whose evidence expired. **The veto is currently protecting exactly one program, and costing one other.**

⛔ Do NOT delete the veto on this finding alone — 066 is a real regression and must be hunted MONITOR-FIRST. But the rung is "fix 066, then delete the veto," not "design a nested-frame protocol first."

## 5. PATREF IS THE FIRST BLOCKER — AND IT IS ABSENT FROM `zd_wl_kind` ENTIRELY

`SCRIP_ZD_GAP=1` on alt1:
```
[ZD-GAP] r=3 op=IR_MATCH_PATREF(105) admit=0 nops=0 callee=-
```
Every other node in the run admits. `IR_MATCH_PATREF` / `IR_MATCH_DEFER` appear nowhere in `zd_wl_kind`'s ladder — they fall through to `return 0`. One unadmitted node at the head declines the whole run → wholesale claim.

**TWO GATES IN SERIES, and this was the session's trap:** `SCRIP_ZD_DYNARM` controls only the *statement-level quartet veto* (`zdyn`, emit.cpp:1977). The `[ZD-GAP] admit=0` is a *separate per-node capability gate* (`zd_wl_kind`). Opening either alone moves nothing. Measured: `SCRIP_ZD_PATREF=1` alone changed 1 of 9 programs; `SCRIP_ZD_DYNARM=7` alone changed 0 of 120 wholesale counts.

## 6. THE FLAT GLUE ALREADY EXISTS — `bb_glue_pass_wires`

`src/templates/bb_glue_flat.cpp`:
```
std::string bb_glue_pass_wires(int gid, int wid) {
    return x86_lea_id("rcx", gid) + x86_lea_id("rdx", wid) + x86_jmp_reg("rax");
}
```
Three instructions, **zero frame** — γ-wire in rcx, ω-wire in rdx, jump. Already consumed by `bb_call_value`, `bb_match_end` (×3), `bb_match_capture` (×2), and `bb_match_defer` (×2). **This IS Lon's GLUE #1 and it is proven in production.**

`bb_match_defer.cpp` already has the two-arm shape Lon described: fast arm (`rt_defer_get_pat_fn` → test → `bb_glue_pass_wires(4,5)`) = FLAT; slow arm (`L0` → `rt_defer_open` → `rt_proc_open_fn` → `bb_glue_pass_wires(7,8)`) = the FRAMED path, written in C. **GLUE #2 is the only one that needs building, and its job is to replace two C calls, not to invent a mechanism.**

## 7. WHAT LANDED: THE MEASUREMENT GATE (SCRIP `4e2ba87d`, DEFAULT OFF)

- `zd_patref_on()` — ONE gate helper feeding BOTH authorities (`zd_k` K verdict + `zd_wl_kind` admission). Two spellings of one gate is the s22k skew disease in miniature; the helper is why there is only one.
- `zd_k`: PATREF/DEFER → K=0 when armed (transfer boxes; they yield through scanner registers and capture side effects like MATCH_SEQUENCE/END, never a 16B spine cell; their `FRQ(op_off)` reads are zls-granted slot reads, not ZRES cell reads).
- `zd_wl_kind`: admission when armed.
- **GATE: 318/318 `.s` byte-identical with `SCRIP_ZD_PATREF` unset**, verified against the pre-edit binary directly (stash/build/compare), not inferred.

## 8. WHY IT IS DEFAULT OFF — THE MEASURED REASON, NOT CAUTION THEATRE

`bb_match_defer.cpp` has **no `op_zres` arm** (`grep -c op_zres` = 0). Arming by kind alone is the 017 falsification shape: a staged verdict handed to a template that ignores it. This is not speculative — it was MEASURED with both gates open:

| program | max carve, gates off → both on | stmt_claim stores |
|---|---|---|
| alt1 | 384 → 384 | 1 → **0** |
| nqueens | 1872 → 1872 | 6 → **2** |
| sudoku | 4944 → 4944 | 12 → **6** |
| any | 256 → **496** | 2 → 2 |
| len | 176 → **368** | 1 → 1 |
| roman | 240 → **416** | 4 → 4 |

Claims halve where the template can absorb the verdict and **inflate where it cannot**. The gate exists to measure that gap; closing it is the template arm, which is the next rung.


## 8b. ⛔ THE K-CHOICE HYPOTHESIS IS FALSIFIED — MEASURED A/B, DO NOT SPEND A RUNG ON IT

The obvious diagnosis of §8's inflation was: `emit.cpp` SPAN SHRINK (grep `SPAN SHRINK`) drops an armed member from the claim extent only when `zd_k(nd) > 0`, so a K=0 PATREF leaves its zls watermark slot inside the claim and inflates it. Under Lon's "have each BB allocate its LOCAL STORAGE needs, IF it has any" the fix looked like K=16 self-carve.

**A/B'd with `SCRIP_ZD_PATREF=2` (arm with K=16) vs `=1` (arm with K=0), both under `SCRIP_ZD_DYNARM=7`. THE TWO ARE BYTE-FOR-BYTE IDENTICAL on every program tested:**

```
prog        OFF        K=0        K=16       (max carve / stmt_claim stores)
any         256/2      496/2      496/2
len         176/1      368/1      368/1
roman       240/4      416/4      416/4
alt1        384/1      384/0      384/0
nqueens     1872/6     1872/2     1872/2
sudoku      4944/12    4944/6     4944/6
match/ops/breakx    unchanged in all three arms
```

**The K choice is NOT the lever. The inflation mechanism is UNIDENTIFIED and remains open.**

What the emitted `.s` does show (any.sno, statement 1) is that the RELOCATION half works correctly:
```
GATES OFF:  n1_keyword_snobol4_α: sub rsp,256   <- claim carved at statement head
            n2_match_begin_α:     (no carve)
GATES ON:   n1_keyword_snobol4_α: sub rsp,16    <- n1 SELF-CARVES, per-BB model working
            n2_match_begin_α:     sub rsp,256   <- claim relocates to the new declined head
```
So arming converts the head node to per-BB correctly and the claim moves to the first still-declined node. The defect is that in statement 2 the relocated claim is 496B where the original was 256B — it GREW on relocation. Candidate mechanisms NOT yet tested: (a) claim extent = `max_extent − claim_base` where the new base shifts the span rather than shrinking it; (b) `op_zdepth` compensation for the newly-armed prefix being added into the claim rather than netted out; (c) `zvo_resolve` owner-table base moving under the relocated head. **Bisect these before writing any template arm** — the s39 lesson is that the plausible-looking K fix was vacuous, and a template arm written against the wrong mechanism is the same wasted rung one level down.

## 9. NEXT RUNG (ordered, dependency-real)

1. **Hunt 066_pat_fence_fn_nested MONITOR-FIRST** under `SCRIP_ZD_DYNARM=7`. It is the sole thing the veto still buys.
2. **Bisect the §8b relocation-inflation mechanism FIRST** (a/b/c candidates named there) — the K hypothesis is already falsified; only then the **`bb_match_defer.cpp` op_zres arm** — the FLAT-glue fast arm needs its ZD spelling so an armed PATREF stops inflating the claim (§8's `any`/`len`/`roman` rows are the tripwire; they must go DOWN or stay flat, never up).
3. **Flip `SCRIP_ZD_PATREF` default ON** — own commit, own gate, per the s22h law.
4. **Delete the `zdyn` veto** once (1) is green.
5. **GLUE #2 (FRAMED)** — emitted `push rbp; mov rbp,rsp` + `bb_glue_pass_wires` + `mov rsp,rbp; pop rbp`, replacing the `rt_defer_open`/`rt_proc_open_fn` C pair on the slow arm. FLAT stays the default for constant-folded targets: a folded pattern is the same pattern folded or not, and gets no frame.

## 10. HONEST LIMITS OF THIS FINDING

- The 120-program census is `corpus/programs/`, not the crosscheck-318; the 20/120 ratio should not be quoted as a crosscheck watermark.
- The bracket measured here (m3 280P/35F/2T · m4 274P/40F/2T/1L) has a different F/T split from the s38 cursor record (m3 281/25F/11T). PASS counts agree; the F-vs-TIMEOUT split is container-speed sensitive. **BY SET comparison within this session is sound; cross-session T/F splits are not.**
- §4's "all six now pass armed" is measured at THIS head only. It is a statement about the veto's current justification, not a claim that the six are permanently fixed.
