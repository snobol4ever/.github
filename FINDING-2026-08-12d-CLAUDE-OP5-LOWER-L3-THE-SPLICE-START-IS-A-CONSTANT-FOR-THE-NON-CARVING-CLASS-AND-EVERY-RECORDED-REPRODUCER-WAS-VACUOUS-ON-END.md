# FINDING 2026-08-12d (s34, Opus 5) — LOWER L-3: THE SPLICE `start` IS A **CONSTANT** FOR THE NON-CARVING CLASS, AND EVERY RECORDED REPRODUCER WAS **VACUOUS ON `end`**

**Fingerprint:** SCRIP `900060c7` — **ZERO src bytes, zero script bytes** · corpus `7045b2ea` + `probe/l3/` (12 probes, oracle-baked refs) · `.github` this commit. **Measurement only.**
**Seat/rung:** GOAL-SN4-HOME-LOWER, L-3 (C-9 residuals). L-0 was landed by s33 and is NOT re-opened.
**Instrument:** `SCRIP_REPL_TRACE=1` — the C-boundary trace already committed in `gen_runtime.c:c_rt_match_replace`, printing the arriving `(slen, start, end)`. **No rebuild, no gdb, no code-reading.** This is s41's own measurement point, reused.
**Build honesty:** `scrip` relinked at HEAD; `make libscrip_rt` → *"Nothing to be done"*; the only commits since the last compiler-byte commit `fc5b0754` touch `scripts/` only. Oracle `x64/bin/sbl -b`, run from the corpus root (s40 CWD rule).
**Floor:** the earn0 board re-RUN at this HEAD reproduces s33's floor **BY SET exactly** (12 PASS / 5 FAIL-silent / 2 FAIL-hang / 1 FLAKY; all four controls green).

---

## 0. THE ONE-LINE RESULT

**The splice defect is THREE classes, not s41's two, and the third one is not a displacement error at all:** for `ARB` / `SPAN` / `BREAK` / `REM` the splice receives `start` = **a hard constant 3** and `end` = **`slen`** — i.e. no match information whatsoever. **No displacement, constant or linear, can repair a constant.** It went unrecorded because every reproducer anyone ever wrote had the match ending at the subject's last character, which makes `end == slen` a **vacuous pass**.

## 1. THE THREE CLASSES, MEASURED AT THE C BOUNDARY

Subject/pattern varied; `want` is the oracle's replacement span.

| class | members | `start` arriving | `end` arriving |
|---|---|---|---|
| **fixed-length** | `LEN(n)`, string literals | **CORRECT** ✅ | **CORRECT** ✅ |
| **carving** | `TAB`, `RTAB` | cursor **at the carve site** = `match_start + Σ(preceding consumed)` | **CORRECT** ✅ (s41's `op_zpat` genuinely works) |
| **non-carving var-length** | `ARB`, `SPAN`, `BREAK`, `REM` | **constant `3`** | **`slen`** |
| **zero-width** | `POS`, `RPOS` | `0` | `1` (s41's `[0,1)` collapse, reproduced) |

⭐ **`LEN` is genuinely clean, NOT vacuously clean** — verified with a *non-terminal* match (`ANY('+') LEN(2) 'g'` in an 18-char subject, match `[10,14)`): arrives `10,14`, oracle-identical. s41's "LEN folds its constant and carves nothing" claim **stands**.

## 2. THE TWO LINEAR SERIES (the derivation, not a guess)

**Series T — carving class.** `LEN(k) TAB(6) LEN(1)` on `ABCDEFGHIJ`; `want start = 0` for every k.

| k | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| arrived `start` | 0 | 1 | 2 | 3 |

Slope exactly **+1 in k**. ⇒ `start` names the cursor **where the carving primitive began**, not the match start. Confirmed independently at non-terminal end by `LEN(2) TAB(14)` → arrives `2,14`, want `0,14`.

**Series S — non-carving class.** `LEN(k) SPAN('ef') 'g'` on `abcd+efg`; `want start` varies 5→2.

| k | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| want `start` | 5 | 4 | 3 | 2 |
| arrived `start` | 3 | 3 | 3 | 3 |

**Flat.** The read is not tracking position. Constant `3` held across **4 subjects** (lengths 6, 8, 10, 18), **4 primitives** (ARB/SPAN/BREAK/REM), **4 prefix lengths**, match positions 2/4/5/6/10, matched-lengths 2 and 3, and with/without a suffix.

## 3. ⛔⭐⭐⭐ THE VACUOUS-`end` TRAP — WHY THIS SURVIVED THREE SESSIONS

s41's reproducer set was `S = 'ABCDEFGHIJ'` + one pattern + `= '*'`, and it covered TAB/RTAB/POS/RPOS/LEN. **The ARB/SPAN/BREAK/REM family was never in it.** When this session first added them, `end` looked **correct** for all four — because each probe's suffix (`'g'`) was the subject's last character, so `end == slen` and the two hypotheses predicted the same number. Only when the match was pushed away from the subject end (`XXXXXXXXXX+efgYYYY`) did `end` reveal itself as `slen`.

⇒ **NEW OPERATIONAL RULE, offered for the goal's anti-vacuity ledger:**
> **A splice witness whose match reaches the end of the subject cannot discriminate `end` from `slen`.** Every splice probe must leave characters to the RIGHT of the match.

This is the **sixth** conviction of the vacuous-control class in this goal (s23 dead board · s24 classifier · s27 ARB control · s37 killswitch A/B · FINDING-2026-08-12 §3 · this). FINDING-2026-08-12 §3 gave the tell as *"a success-expecting witness."* That tell does **not** fire here — these witnesses expect a specific string, not success. The `end`/`slen` collision is a **second, independent tell**, which is why the stated rule did not catch it. `probe/l3/l3_spl_VACUOUS_terminal_trap.sno` is retained **on purpose** as the documented member.

## 4. FALSIFICATIONS — MINE, STATED IN ADVANCE, RECORDED SO NOBODY RE-WALKS THEM

1. **"The ARB/BAL capture defect is retry-extension"** (manual Ch.18 p.207–8: ARB and BAL have implicit alternatives, `ARB ≡ LEN(0)|LEN(1)|…`). Predicted `BREAKX` and `ARBNO` capture must also fail. **MEASURED: both PASS. DEAD.**
2. **"Non-carving `start` = `end − primitive_start`"** (fitted to the constant-3 observation). Predicted `LEN(1) SPAN('ef')` → `start 2`; `ANY('+') SPAN('e') 'fg'` → `start 5`. **MEASURED: 3 and 3. DEAD.**
3. **"`start` is a signed displacement of the match start"** (the shape s41's residual board implies). Falsified by Series S being **flat** — a displacement of any sign or slope must move when `want` moves.

## 5. CORRECTIONS TO THE RECORD

- **s41's residual board (FINDING-2026-08-10f) names TWO open components** — POS/RPOS anchor, and "the `start` term needs its own displacement." **A third exists and is larger:** the non-carving class receives `(3, slen)`. s41's wording assumed a displacement; the arithmetic says otherwise. s41 also could not consult the SPITBOL manual (its `/mnt/user-data/uploads/` was empty — stated in its own last section); the manual was available this session.
- **⛔ The s33 LOWER cursor's ordering claim is FALSIFIED.** It put L-3 ahead of L-1 because `cap_after_bal`/`cap_after_varlen` were "L-3's named mechanism verbatim." **Capture and splice are two defects:** BREAK/SPAN/REM/TAB/RTAB **capture correctly** and **splice incorrectly**. One shared `start` authority cannot produce that split. Fixing the splice will not clear those two rows. *(L-3 remains the right next rung — 9/12 red — but on its own merits, not that one.)*
- **`earn0_cap_after_varlen.sno`'s stated blast radius is over-broad by seven.** Its comment names nine candidate templates (`arb bal break breakx rem rtab span span_var tab`). **Measured: only ARB and BAL fail capture.** SPAN, BREAK, REM, TAB, RTAB, BREAKX, ARBNO all capture correctly.
- **The `[n, p+n)` capture formula SURVIVES and gains a third witness.** Predicted in advance that `'abcdefg' ? ARB . R 'g'` binds **null** (p=0, n=6 ⇒ `[6,6)`). Measured: null. This also kills the "after a variable-length primitive" framing — ARB is *first* here, with no predecessor at all.

## 6. THE BOARD — `corpus/probe/l3/` (12 probes, oracle-baked refs)

Run with the **existing** generic runner, no new script:
```bash
EARN0=/home/claude/corpus/probe/l3 REPEAT=2 bash scripts/board_earn0_set.sh m3
```
**m3 at `900060c7`: 3 PASS / 9 FAIL-silent.** PASS = `len_nonterm` · `len_pure` · `lit_len` (the three fixed-length controls, all green). FAIL = `tab_nonterm` · `tab_linear3` · `rtab_nonterm` · `span_nonterm` · `arb_nonterm` · `break_nonterm` · `rem_nonterm` · `pos` · `VACUOUS_terminal_trap`.

⭐ **These are landed deliberately, in `probe/l3/` and NOT `probe/bb/`** — `probe/bb` is the universal per-rung gate where red rows register as REGRESSION (s41 left its reproducers in `/tmp` for exactly this reason, **and they were lost**, which is why this ground was re-walked). `probe/l3/` is boarded BY SET by a runner that already reports red rows, the same contract as `probe/earn0/`.

## 7. NEXT SEAT, IN ORDER

1. **The non-carving class is the prize, not the `start` displacement.** `(3, slen)` is a read of cells nobody wrote for this shape — the same disease as POS/RPOS's `(0,1)`. Locate the writer, not an offset. ⛔ Do **not** spend a rung on "a third displacement": Series S is flat and kills that whole family of fixes.
2. **`TAB`/`RTAB` `start` IS a genuine displacement** (Series T, slope +1) and is separable — it is the only component s41's framing describes correctly.
3. **`bal` is its own row:** it is the one shape wrong on **both** `start` (+1) and `end` (+1), and the only capture-failing member that also splices wrong. Do not fold it into either class without its own witness.
4. **Then L-1 (Defect A)** — and honour its ⛔: fixing A alone RAISES the hang count. A seat that reverts on that signal reverts a correct fix.

**Debts unchanged:** m4 arm UNMEASURED for both boards (BOARD B-0 still owns the m4 harness) · regen ×3 not owed — **zero codegen bytes this session**.

**ENV note:** a detached build needs `setsid`, not `nohup` — a `nohup` background build died between tool calls after the package install, and `/tmp/build.log` was an **inherited artifact of the previous session in this container**, which briefly read as live progress. Check log mtimes before trusting a build log you did not watch start.
