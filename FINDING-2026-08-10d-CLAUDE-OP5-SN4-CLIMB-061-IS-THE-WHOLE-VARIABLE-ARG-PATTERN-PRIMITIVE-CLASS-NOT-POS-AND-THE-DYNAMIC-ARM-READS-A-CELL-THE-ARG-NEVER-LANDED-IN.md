# FINDING 2026-08-10d (CLAUDE OP5, SN4 ζ-CLIMB s39) — 061 IS THE WHOLE VARIABLE-ARG PATTERN-PRIMITIVE CLASS, NOT POS; AND THE DYNAMIC ARM READS A CELL THE ARGUMENT NEVER LANDED IN

**Session scope:** orientation + C-9 residual entry at `061` per s38's NEXT. **ZERO code changed.** Trees at open == trees at close.
**Tips measured:** SCRIP `bce9a4b` · corpus `bea31de` · .github `37e0273` (HEAD had moved past s38's close `66322b3c`; see OPEN ITEM 1).
**Build:** foreground-launched under `setsid` with an exit-code sentinel, exit 0, 0 `error:`, binary mtime 23:07 **predating** every measurement (METHOD 8).

---

## 1. HEADLINE — THE CURSOR'S CHARACTERIZATION IS TOO NARROW BY A WHOLE FAMILY

s38's NEXT reads *"061 variable-arg POS"*. Measured: **it is not POS, and it is not `061`.** Every pattern primitive tested fails
when its argument is a **variable** and passes when the argument is a **literal**. `061` is one witness of a family defect.

| Probe | Shape | Oracle | m3 | m4 |
|---|---|---|---|---|
| `q1_pos_lit` | `POS(0) 'a' . V` **literal** | `a` | ✅ | ✅ |
| `r6_lit_in_var_shape` | `POS(1) 'a'` **literal, non-zero** | `OK` | ✅ | ✅ |
| `q2_pos_var_once` | `POS(N)` N written **once** | `a` | ❌ NOMATCH | ❌ NOMATCH |
| `q3_pos_var_twice` | `POS(N)` N written **twice** | `a` | ❌ NOMATCH | ❌ NOMATCH |
| `q4_pos_var_loop_nocap` | 061 loop, **no capture** | `HIT0 HIT1 HIT2` | ❌ empty | ❌ empty |
| `q6_len_var` | `LEN(N) . V`, N=2 | `ab` | ❌ NOMATCH | ❌ empty |
| `r3_tab_var` | `TAB(N) . V`, N=2 | `OK[ab]` | ❌ NOMATCH | ❌ NOMATCH |
| `r4_anchor_posvar` | `POS(N)` N=0, **&ANCHOR=1** | `OK` | ❌ NOMATCH | ❌ NOMATCH |
| `r5_expr_arg` | `POS(N + 0)` | `OK` | ❌ NOMATCH | ❌ NOMATCH |
| `q7_061_verbatim` | corpus `061` | `a a a` | ❌ empty | ❌ empty |

**POS, LEN, and TAB are all affected.** This is consistent with C-3 being green: C-3 is *STATIC* patterns, i.e. literal arguments only.
⇒ The fix has **one owner and one choke**, not four. Do not open per-primitive rungs.

## 2. FOUR HYPOTHESES KILLED BEFORE ANY CODE WAS READ (cheapest-discriminating-experiment protocol, RULES §1)

1. **NOT capture.** `q4` has no `. V` and fails identically. The probe's name (`061_capture_in_arbno`) is misleading twice over — it contains **no ARBNO and no capture is required** to reproduce.
2. **NOT the loop / not ARBNO.** `q2` is a single-shot three-line match and fails.
3. **NOT the write-count/seal split.** `q2` (`sno_fz_wrcount==1`) and `q3` (`wrcount==2`) behave **identically**. The seal=2 vs seal=0 lead that D05/D06 cost sessions on **does not govern this class** — do not inherit it here.
4. **NOT a broken variable read.** `r2` proves the variable is healthy at that point: `DUPL('x',N)` → `xx` and `OUTPUT = N` → `2`, both oracle-correct in both modes. Non-pattern functions take variable arguments fine. The defect is specific to **pattern-primitive argument marshalling.**

## 3. THE MECHANISM, MEASURED AGAINST EMITTED ASM (not inferred from reading the emitter)

`src/templates/bb_match_pos.cpp:9` documents two arms verbatim: *"static arm reads `op_sb` constant, dynamic arm reads `ZOPQ(0,8)` (integer value of predecessor cell)."* The emission confirms it — nearest passing sibling vs failing probe, same shape:

```
LITERAL r6 (PASSES)                 VARIABLE r4 (FAILS)
n8_match_pos_α:                     n18_match_pos_α:
    mov  rax, 1        <- static        mov  rax, qword ptr [rsp + 8]   <- dynamic ZOPQ(0,8)
    cmp  r14d, eax                      cmp  r14d, eax
    je   <success>                      jne  <fail>
```

**The load is the whole delta.** `cmp r14d, eax` compares only the **low 32 bits**, so a cell correctly holding `N=0` would
succeed at cursor 0. `r4` sets `N=0`, is **anchored** (scan-retry removed from the picture), and still fails ⇒
**`[rsp+8]` does not hold the argument.** The dynamic arm is reading a cell the argument never landed in.

**Corroborating evidence (sharpened in §8 — read that, it supersedes the wording here):** `LEN(N=0)` succeeds in `r1`'s flat shape but fails in `s1`'s loop shape. In `r4`'s emission
`rsp` is reset from `[r12-16]` and decremented (`sub rsp, 32`, the match-frame carve) between argument evaluation
(`n16_coerce_integer`) and the read — the shape in which a base-relative read goes stale.

⚠️ **This is a lead, not a conviction, and it is deliberately left unconvicted.** It is the same *class* as C-9's splice defect
(`FRQ` reads short by the replacement subtree depth, fixed s35 via the `g_zd_zunder` addend at the choke) — but the goal file's own
anti-pattern §2 warns that "the offset is wrong by N bytes" theories have been falsified twice. **Next seat: bracket it with the
MONITOR first** (this class is a value divergence with live trace events, so unlike the 3R crash class the monitor is *not* dark),
then confirm which cell `n16_coerce_integer` actually writes before touching any offset.

## 4. SECOND, SEPARATE LAND MINE — `IR_MATCH_POS` HARD-ABORTS ON THE UNEVALUATED `*N` FORM (rc=134)

`q5_pos_star_stored` — the manual p.143 #11 shape, a **stored** pattern `P = POS(*N) 'a' . V` — does not fail, it **aborts**:

```
FATAL emit_drive: IR op=88 has no template in the universal driver.
```
**op 88 = `IR_MATCH_POS`** (index confirmed against the ordered enum in `src/contracts/IR.h`, 127 ops).
m3 rc=**134**; m4 does not even link (`<BUILDFAIL>`). Per the sink's own note, POS *has* a case (literals work), so what fired is a
**guard inside that case** declining the deferred-argument form — the backtrace line, not the message, names it.

⚠️ **Do not assume this is `test_case`.** s35 recorded `test_case` at rc=134 and I initially suspected a shared cause; measured at
`bce9a4b`, `test_case` **hangs (rc=124 under `timeout 8`)** and emits no op=88 abort. Different signature. Unresolved — see OPEN ITEM 2.

## 5. ORACLE / SEMANTICS ANCHORS (SCRIP FOLLOWS SPITBOL, METHOD 7)

- Oracle reproduces `061`'s committed `.ref` byte-for-byte (`a a a`) — the reference is trustworthy.
- **`061` is legal SNOBOL4 and the `*` operator is NOT required in it.** Manual p.143 #11 scopes `*` to patterns **stored in a variable**; used directly in a match statement, `POS(N)` re-evaluates per execution. Oracle-confirmed both ways: `q7` (bare `POS(N)` in-statement) and `q5` (`POS(*N)` stored) both yield `a a a`.
- **TAB-binds-subject (p.143 #10) is still unprobed** and remains on C-9's list. Manual text, for whoever takes it: `TAB`/`BREAK` bind every character they pass over, so `S ? TAB(49) LEN(1) = '*'` replaces the **first 50 characters**, not the 50th; the sanctioned forms are `POS(49) LEN(1) = '*'` or `TAB(49) . FRONT LEN(1) = FRONT '*'`. This is a direct spec for the splice span: **the replaced span is the full extent bound by the match, not the trailing sub-pattern.**

## 6. OPEN ITEMS / WHAT THIS SESSION DID NOT DO (stated plainly, not padded)

1. **NO WATERMARK WAS RE-PROVED.** The 141-probe suite was **not run**. s38's m3 133/15xf/0/3R was measured at `66322b3c`; this session's tip is `bce9a4b`, so the watermark at this tip is **unknown**. It is NOT claimed to be unchanged. First task for the next seat if a number is needed.
2. `test_case` rc=124 hang at `bce9a4b` vs s35's recorded rc=134 — signature moved, undiagnosed. `test_string` exits rc=0 at this tip (output not diffed against ref); s35 recorded it failing. Both need a clean re-measure before being trusted either way.
3. **MONITOR-FIRST was not executed** for the class in §3. The discriminating-experiment stage (RULES §1's explicit precondition, "before reading any code") was completed and is what §1–§3 rest on; the monitor bracketing is the next instrument, not a skipped one.
4. Container: **no `sudo`** ⇒ `gdb` and `nasm` are unavailable this session. The gdb spin-counter half of RULES §1 cannot be run until that is resolved.
5. Evidence namespaced per seat at `/tmp/climb_s39/` (probes + oracle refs + `lit.s`/`var.s`).

## 7. RECOMMENDED NEXT RUNG

Enter at the **choke, not the primitive**: one fix at the dynamic-arm argument read should clear POS + LEN + TAB together, and
`061` is then a regression witness rather than a rung. Acceptance set: `q1 q2 q3 q4 q6 q7 r3 r4 r5 r6` green both modes plus
`s1`/`s2` sweeps returning identity (`0->0 … 5->5`). The `*N` abort (§4) is a **separate** rung — an unimplemented guard arm,
not an offset — and should not be folded into the same commit.

---

# §8 — SAME-SESSION ADDENDUM: MONITOR BRACKET OBTAINED, MECHANISM PROVEN VALUE-INDEPENDENT, AND ONE OF MY OWN CLAIMS CORRECTED

## 8.1 MONITOR-FIRST EXECUTED — AND THE MONITOR IS **NOT** DARK FOR THIS CLASS (§3's assertion is now earned, not assumed)

`PARTICIPANTS="spl scr" test_monitor_3way_sync_step_auto.sh` on the anchored `POS(N)` probe. ⚠️ Note for the next seat: the
`2way..._bin.sh` entry point runs **csn vs spl — two oracles**, and cannot see SCRIP at all; the 3-way harness with an explicit
`PARTICIPANTS` pair is the one that brackets SCRIP.

```
| step | stno | spl                          | scr                          | source                        |
| 5    | 3    | @3 VALUE N = INT=0           | @3 VALUE N = INT=0           | N = 0                         |
| 6    | 4    | LABEL stno=INT=4             | LABEL stno=INT=4             | X POS(N) 'a'  :F(NOMATCH)     |
| >7   | 4    | LABEL stno=INT=5             | LABEL stno=INT=7             | (fall-through vs :F branch)   |
```

Bracket = **inside statement 4's execution**, between last-agree (step 6) and first-diverge (step 7). Independently of §2.4,
step 5 shows **both engines agreeing `N = INT=0`** immediately before the match ⇒ the variable is correct on entry; the loss is
strictly inside the match. This is the RULES §1 precondition, discharged.

## 8.2 THE ARGUMENT PROVABLY NEVER REACHES THE PRIMITIVE (value-independence, identical shape)

Three programs differing **only** in the assigned constant:

| N | oracle | m3 |
|---|--------|----|
| 0 | `OK[]`   | **NOMATCH** |
| 1 | `OK[a]`  | `OK[]` |
| 2 | `OK[ab]` | `OK[]` |

m3 **does not track N**: `N=1` and `N=2` both match **zero** characters, and `N=0` — which for `LEN(0)` can never fail — fails.
The effective argument is uncorrelated with the source argument. Combined with §2.4 (the variable itself is correct) and 8.1
(both engines agree on `N` at entry), this closes the question: **the dynamic arm reads a slot unrelated to the argument.**

## 8.3 THE INTERVENING CARVES, IN EMISSION ORDER (var.s)

```
172:  sub  rsp, 16
175:  mov  qword ptr [rsp + 0], rax   # result      <- argument descriptor written here
177:  jmp  n16_coerce_integer_α
184:  sub  rsp, 16                                  <- coerce box carves its own 16B
213:  sub  rsp, 32                                  <- match frame carve
215:  mov  dword ptr [rsp + 0], 0     # start_δ
      mov  rax, qword ptr [rsp + 8]                 <- ZOPQ(0,8), read off the MOVED rsp
```
At read time `[rsp+8]` sits **inside the match frame** (between `start_δ` at `+0` and `rsp_mark` at `+16`) — an unwritten slot
holding leftovers. Descriptor layout corroborates that `+8` is the right *half* (type/len at `+0`/`+4`, value at `+8`), so the
half is right and the **base** is wrong: the fixed `+8` does not account for the carves interposed since the write.

## 8.4 ⛔ CORRECTION TO MY OWN §3 — THE DISPLACEMENT IS STRUCTURAL, NOT PADDING-SENSITIVE

§3 called context-dependence "the fingerprint." **Partly wrong, and I am correcting it before anyone builds on it.** Four probes
with an identical match statement and 0/1/2 extra preceding assignments (`t1_min` `t2_prepad` `t3_exprarg` `t4_two_pad`) fail
**uniformly**. The displacement comes from the *interposed carve depth* (coerce + match frame), which is a property of the
construct, not of what preceded it. The r1-vs-s1 difference is a difference of **shape**, not of padding. A next seat testing
"add a statement and watch it move" would get a null result and might wrongly acquit the offset theory.

## 8.5 ⛔ DO NOT HARDCODE THE DELTA — s35's TRAP APPLIES HERE VERBATIM

The carve depths visible above are 16 + 32 in *this* shape. **Do not turn that into a constant.** s35 recorded, for the
structurally identical C-9 splice defect: *"THE DELTA IS NOT A CONSTANT: +16 for a literal replacement, +80 for `A '-' B` — the
subtree's ζ footprint. Any fix hardcoding 16 passes the literal case and FAILS concat."* The same failure mode is available here:
a richer argument expression (`POS(N + 0)`, a function call) carves more. The correct shape is s35's — **stage the depth at the
planner and consume it at the choke as an addend** (`g_zd_zunder`/`g_zd_ztail` precedent), computed from the planner's own carve
accounting, never from a number read off one emission.

**STATUS: still a lead, not a conviction.** What is now PROVEN: the argument never arrives (8.2), the loss is inside the match
statement (8.1), and the read is base-relative across two interposed carves (8.3). What is NOT proven: that correcting the base
is sufficient. Confirm which cell the planner *believes* it wrote before editing any offset.
