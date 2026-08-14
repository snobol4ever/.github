# FINDING — 2026-08-13 s71 (Claude Opus 5, RBP-EARN seat)

## THE RESULT SLOT IS UNWIRED, AND THE REASON IS NOT THE FRAME — `fc_walk_range` HAS NO `IR_MATCH_DEFER` CASE, SO EVERY `.` CAPTURE WHOSE WALK CROSSES A DEFER IS DENIED ITS CELL AND BINDS THE NULL STRING, ON BOTH ARMS AND IN BOTH MODES

**Rung asked for:** finish the MATCH-RBP frame by wiring RESULT and LOCAL for MATCH_BEGIN/MATCH_END.
**What is landed:** root cause, a 5-line minimal reproducer, a control, a confirmed generalization, and three
banked witnesses with oracle `.ref`s (corpus `3815207f`). **No codegen change** — see THE RULING WANTED.

---

## 1. THE MANUAL FIRST — WHAT "RESULT" ACTUALLY IS

Manual Ch.9 p.128, *Binary Operator Extensions*: the binary `?` is general, and

> `(SUBJECT ? PATTERN)` performs pattern matching and **returns the substring matched**, or failure as its
> value. `(SUBJECT ? PATTERN = OBJECT)` returns the **entire subject after replacement**, or failure.

Verified against the live oracle before any code was read: `S = 'ABCDEF'; V = (S ? LEN(3))` ⇒ `V=[ABC]`,
`S` unchanged. So the RESULT reserved at `[rbp-48]` has a precise, manual-defined meaning, and it is a
16-byte DESCR (pointer+length), not a scalar — the layout note calling `[rbp-56]` a *pad* is therefore
load-bearing: RESULT+pad is exactly one DESCR, which is why the slot pair exists.

## 2. THE INSTRUMENT CORRECTION THAT CAME FIRST (do not inherit the broken grep)

`bb_match_begin.cpp`'s mrbp arm opens with `x86("comment", "IR_MATCH_BEGIN (MATCH-RBP frame; mark=[rbp-8])")`.
**Comments are NOT rendered into the emitted `.s`; `x86("note", ...)` annotations ARE.** A first pass grepped
for `MATCH-RBP frame` and read **0 sites on a program that was in fact taking the arm** — a vacuous detector
that would have "proved" mrbp never fires. **The sanctioned mrbp detector is `grep -c retry_whack`** (or the
`push rbp / mov rbp,rsp` pair inside a `match_begin_α` block). Recorded because this instrument will be
reached for again, and it fails GREEN — the direction that manufactures false exonerations.

## 3. THE WITNESS TRIPLE (banked in `corpus/probe/mrbp/`, oracle `.ref`s)

The three programs differ by ONE token, which is the whole point.

| witness | pattern | defer? | mrbp (`retry_whack`) | m4 RBP=1 | m4 RBP=0 |
|---|---|---|---|---|---|
| `mrbp_result_control.sno` | `Q = LEN(3)`      | no  | 0 | **PASS** | **PASS** |
| `mrbp_result_value.sno`   | `Q = LEN(3) $ W`  | ×4  | 1 | **DIFF** | **DIFF** |
| `mrbp_result_capture.sno` | `Q = LEN(3) $ W`  | ×4  | 1 | **DIFF** | **DIFF** |

Sole delta control→value: the `$ W` immediate assignment inside the stored pattern, which is what puts
`IR_MATCH_DEFER` in the graph. Oracle `V=[ABC]`; SCRIP `V=[]`, `W=[ABC]`.

⛔ **THE MATCH SUCCEEDS.** `mrbp_result_capture` prints `MATCH` and then `X=[]`. Nothing crashes, nothing
hangs, rc=0. **This is a silent wrong-answer class**, which is why it survived this long — and why
`exit 0 is not exoneration` (the s66 law) applies to it with full force.

⛔ **IT IS RED ON BOTH ARMS, SO IT IS NOT AN mrbp REGRESSION.** `SCRIP_MATCH_RBP=0` fails identically in m4.
The defect predates MATCH-RBP; mrbp is merely the vehicle that could *fix* it (§5).

## 4. ROOT CAUSE — MEASURED WITH PRINTED VALUES, NOT INFERRED (s50 FACT RULE)

`SCRIP_CAP_DIAG=1` on the pair, one command, no code reading required to localize:

```
control : [CAP] SAVE save_active=1 fc_bytes=16    [CAP] COND fc_disp=0
value   : [CAP] SAVE save_active=1 fc_bytes=16    ($ W  — the INNER capture, fine)
          [CAP] IMM  off=48 pat=1
          [CAP] SAVE save_active=0                ← the RESULT capture's SAVE is INACTIVE
          [CAP] COND fc_disp=-1                   ← and its COND resolved NO cell
```

Chain, each link checked:

1. `lower_snobol4.c:~504` — `X = subj ? pat` is **rewritten at the TREE level** into `subj ? (pat . X)`.
   The RESULT is therefore an **ordinary whole-pattern `.` capture**, carrying no distinguishing mark at IR
   level. (This is a deliberate, documented design choice, taken to avoid teaching the match spine a
   value-producing exit.)
2. `sno_cap_fc()` (`lower_snobol4.c:1106`) computes `walk_ok = fc_walk_range(g, before_i, g->n, 0, &fp_inner)`
   and its **first statement is `if (!walk_ok) return;`** — no `fc_save_register`, no
   `fc_cond_register_with_save`.
3. `fc_walk_range()`'s whitelist switch admits LIT/LEN/ANY/NOTANY/POS/RPOS/ATP/ASSIGN_{SAVE,COND,IMM}/GOTO
   and lands everything else on **`default: lin = 0;`**. There is **no `IR_MATCH_DEFER` case**.
4. `fc_save_active()` is nothing but membership in the `fcv[]` registry, so an unregistered SAVE reads 0, and
   the capture falls to what `zeta_storage.c:747`'s own comment calls *"the flat rt_cap array path"* with no
   cell — and binds null.

**PREDICTION MADE, THEN TESTED, THEN CONFIRMED.** If (1) is right, the bug cannot be about the value form at
all — an explicitly-written `.` capture must fail identically. `mrbp_result_capture.sno` writes
`S ? Q . X` by hand: `X=[]`, same on both arms. ⇒ **The class is: any conditional capture whose
`fc_walk_range` crosses an `IR_MATCH_DEFER`.** The value form is one member, not the disease.

This is the same family FINDING-2026-08-04g named ("three die to an over-deleted switch in `fc_walk_range`")
and the same *shape* as s66's ALT-CAP (a **denial** is the sole suppressor, not a wrong offset).

## 5. THE RULING WANTED — WHY THIS SESSION DID NOT LAND A FIX

Two candidate repairs; **both are design decisions, and the cheap-looking one is unsound.**

**(a) Add `IR_MATCH_DEFER` to `fc_walk_range`'s whitelist.** ⛔ **UNSOUND AS WRITTEN.** The walk does not
merely decide eligibility, it **sums a footprint** (`*fp += fck`) that is then baked as `fp_inner`. A DEFER
has **no compile-time extent** — s68 established this from manual Ch.11 (matching is exhaustive; a deferred
expression is not assumed to match ≥1 char). Admitting DEFER to a summing walk bakes a wrong displacement,
which is precisely the class the decline exists to prevent. The function's own comment says the conservatism
lives in the list being COMPLETE.

**(b) Give the RESULT the frame slot it was reserved — `[rbp-48]`/`[rbp-56]` — so it never needs an fc
grant at all.** This is what the MATCH-RBP layout was designed for, it is depth-free, and it survives both
the β `lea rsp,[rbp-56]` retry whack and the `mov rsp,rbp / pop rbp` teardown (both witnesses take the arm).
⛔ **BLOCKER: there is no discriminator.** Per (1) the RESULT capture is an ordinary `.` capture with no mark,
so "the denied capture" is not a sound selector — **two denied captures in one match would collide on one
slot.** Making (b) sound means the LOWERER must mark the whole-match result capture distinctly, which is a
lowerer change, not a template edit.

⭐ **AND THIS IS WHERE "LOCAL" ENTERS.** RESULT is a 16B DESCR, so it consumes `[rbp-48]` **and** the
`[rbp-56]` pad — the frame as it stands has **no room left for a LOCAL area**. Adding one means growing the
frame (`sub rsp,24` → `sub rsp,40`, retry whack `[rbp-56]` → `[rbp-72]`, total 64 → 80, still 16-aligned).
Growth is believed safe **on this arm specifically** — `emit_match_begin_stfh_k()` returns 0 under mrbp so
the planner accounts nothing, the frame releases itself, and mrbp fires only on deep-arrival graphs, which
per the s70 cursor bake no static displacements. **Believed, not measured — it needs the compile-time md5
blast radius, not a board run (s66: board noise floor ~5, and it flips green→red).**

⇒ **LON'S RULING WANTED, same shape as the widening question s70 escalated:** does RESULT ride the frame
slot (requiring a lowerer-side mark for the whole-match capture, and a frame grown to 80 for LOCAL), or does
`fc_walk_range` learn a NON-SUMMING eligibility answer for DEFER (extent-unknown ⇒ eligible but contributes
no baked displacement) so the existing fc path serves it? **Accounting and eligibility currently ride one
number in that walk — the same conflation s70 named for `emit_match_begin_stfh_k()`, one layer down.**

## 6. STATE, AND WHAT IS EXPLICITLY *NOT* CLAIMED

- **Not claimed:** any relationship between this and the m4 failing set in the watermark. Not measured.
- **Not claimed:** that `mrbp_result_value`'s m3 behaviour is understood. m3 RBP=1 prints `V=[]` rc=0 while
  m3 RBP=0 dies `rc=134 [ZHP] heap exhausted` — **a second, different, pre-existing defect on the legacy
  arm**, observed and recorded, NOT root-caused, and NOT this rung's.
- **Container note, corrected from inheritance:** this container arrived **missing all 8 packages** (s70's
  had them all present, which is why its install script printed nothing). The script installed
  `libgmp-dev m4 nasm wabt bison flex gdb`; **gdb 15.1 is live**. Do not inherit "install script produces no
  output" as a container property — it is a function of what is already there.
- Build: `scrip` + `libscrip_rt` green at HEAD. Tree otherwise untouched — **zero source edits this session**,
  so no regen is owed (RULES.md step 4 does not fire).

**OWED: PUSH CREDENTIAL — 1 corpus + 1 `.github` commit unpushed, ASKED IN CHAT.**
