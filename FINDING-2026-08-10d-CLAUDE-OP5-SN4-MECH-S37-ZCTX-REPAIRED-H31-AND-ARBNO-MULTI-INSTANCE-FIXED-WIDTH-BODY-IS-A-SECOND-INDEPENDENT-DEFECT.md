# FINDING 2026-08-10d — MECH s37 (Opus 5): ZCTX REPAIRED H31; THE RE-ENTRANCY DISCRIMINATOR SURVIVES FALSIFICATION WITH NEGATIVE CONTROLS ON EVERY NEIGHBOURING AXIS; AND ARBNO WITH A FIXED-WIDTH BODY IS A SECOND, INDEPENDENT DEFECT THE PROBE SUITE CANNOT SEE

**Session:** orientation + watermark re-prove + mechanical ablation. **NO CODE WRITTEN.** Oracle-anchored throughout (`/home/claude/x64/bin/sbl -b`).
**HEAD at measure:** SCRIP `bce9a4b0` · corpus `bea31de0` · `.github` `37e0273c`. Fresh container, 1 CPU, 3 GB, `-O0` (O2-DIRECTED-ONLY observed).

---

## 1. WATERMARK PROVED AT OPEN — H31 IS REPAIRED, THE CURSOR IS 13 COMMITS STALE

| Mode | pass | xfail | XPASS | REGRESSION |
|------|------|-------|-------|------------|
| m3 `--run` | **134** | 15 | 0 | **2** — D12, D13 |
| m4 `--compile` | **133** | 16 | 0 | **2** — D12, D13 |

s36 recorded m3 133/15/0/**3** · m4 132/16/0/**3** over set D12·D13·**H31** at `a5533659`. **+1 pass each mode; the regression set shrank 3 → 2 BY SET; H31 is GREEN in both modes.**

The repair is `0970838f` (ZCTX BASE STACK, Fable s11) — `g_blob_ctx` deleted, replaced by `g_zctx[66]` = `[0]`depth · `[1]`current base · `[2+i]`spill. **`GOAL-SN4-ZETA-MECH.md` does not record this**: s36 was still the newest cursor entry and it prescribes M-1b GLOBAL-EXECUTE as if the global were still live. `grep -rn 'g_blob_ctx\|rt_blob_ctx_ptr' src/` == 0 except inside the g_zctx comment. **M-1b Steps 1–3 are substantially DONE; what survives of M-1b is the residue named in §2, not the census.**

⚠ The landed shape is a *stack*, not the zero-global design s36d ruled for. It is closer, not identical, and its own comment defers overflow policy to M-1b. Lon should rule whether the base stack satisfies the s36d ruling or is an intermediate.

## 2. D12/D13 — THE DISCRIMINATOR SURVIVES FALSIFICATION, AND OVERFLOW IS FALSIFIED

Both SEGV (exit 139), both modes. Ablation, every row oracle-checked:

| # | shape | result |
|---|-------|--------|
| a | construct the recursive patterns, never match | PASS |
| b | top-level `*LIST` defer, ITEM non-recursive | PASS |
| c | recursive ITEM, top level uses `LIST` **directly** (no `*`) | **SEGV** |
| d | recursive ITEM + top-level defer, **ARBNO removed** | PASS |
| e | plain `*Q` (non-recursive) inside an ARBNO body | PASS |
| h | blob that owns an ARBNO, activated inside an ARBNO body, **no self-recursion** | PASS |

**It is not defer, not ARBNO, not nesting, not blob-in-blob, and not the top-level `*`.** Every one of those has a passing negative control. The discriminator is **a blob activation beginning while an activation of THAT SAME blob is still live on the spine.** ARBNO's only role is generating the backtracking pressure that forces the recursive alternative to be tried while the outer activation is still open — (d) has identical recursion and never crashes because it never backtracks into it.

**⛔ ZCTX DEPTH OVERFLOW IS FALSIFIED.** A depth-graded series of D12 (subjects `(12,78)` · `(12,(34),78)` · `(12,(3,45,(6)),78)` · `(12,(3,(4,(5))),78)`) crashes at **every** depth including 1. Capacity 64 is never approached. The residue is push/pop ASYMMETRY on a failure exit — an activation entered but drained by a route that does not pop, desynchronising `[0]`/`[1]` so the outer activation re-bases off a foreign or stale base — **not exhaustion**. Next seat: gdb the pop arms (`emit.cpp` CLASS-D γ ≈2808 / ω ≈2827) against the α push ≈2375; the crash is gdb-reachable per RULES §1.

## 3. ⭐ NEW, INDEPENDENT DEFECT — ARBNO CANNOT SUPPLY ≥2 INSTANCES OF A FIXED-WIDTH BODY

Found incidentally while building controls. **Not a blob program, no defer, no recursion, no pattern object.** Both modes.

```
        SUBJ = 'abab'
        SUBJ ? POS(0) ARBNO('ab') RPOS(0)               :F(NO)
        OUTPUT = '=S'                                   :(EN)
NO      OUTPUT = '=F'
EN
END
```
oracle `=S` · SCRIP **SEGV**.

**Instance-count boundary is exact:**

| instances ARBNO must supply | oracle | m3 |
|---|---|---|
| 0 — `ARBNO('ab')` on `''` | =S | =S |
| 1 — `ARBNO('ab')` on `'ab'` | =S | =S |
| **2** — `ARBNO('ab')` on `'abab'` | =S | **SEGV** |
| **3** — `ARBNO('ab')` on `'ababab'` | =S | **SEGV** |
| **3** — `ARBNO('a')` on `'aaa'` | =S | **SEGV** |

**Body-kind discriminator** (`'ab,ab' ? POS(0) X ARBNO(',' Y) RPOS(0)`, oracle `=S` throughout):

| X / Y | m3 |
|---|---|
| SPAN / SPAN | **=S correct** |
| literal / literal | =F |
| LEN / LEN | =F |
| literal / LEN | =F |
| LEN / literal | =F |

**SPAN is the only body kind that works.** Note the two symptoms: the bare form CRASHES, the concatenated form returns a SILENT WRONG ANSWER (`=F` for a matching subject) — the exact class RULES §1 calls the monitor blind to, and OPS-2 MON-CAP's whole justification.

**⛔ WHY THE SUITE IS DARK TO THIS: every ARBNO probe in `corpus/probe/bb/probes/` uses a SPAN body** (X07 `ITEM ARBNO(',' ITEM)` with `ITEM = SPAN('0123456789')` is the manual p.121 shape and PASSES). The 141-probe gate can be fully green while a core SNOBOL4 primitive is broken for literal and LEN bodies. **This is a suite-coverage hole, not just a bug.** Mint the five rows above as probes before fixing anything.

**KILLSWITCHES EXONERATE THE CONSTANT-WIDTH PATH.** A/B on the failing case: `SCRIP_ARBNO_K16` 0/1, `SCRIP_ARBNO_LATCH` 0/1, `SCRIP_ARBNO_FRAMELESS` 0/1, `SCRIP_ZPOP_FOLD_OFF` 0/1 — **all four byte-identical `=F` both settings.** The K-conversion arms are NOT the owner. (Side observation: `SCRIP_OPT=0` produces empty output on the same program — the emergency arm is itself broken here. Nothing may depend on it per FACT RULE, but it is not a usable bisect instrument on this class.)

## 4. ROUTING

1. **ARBNO fixed-width body ranks above D12/D13.** It is a core primitive, silent in one form, invisible to the gate, and independent of the whole blob/ζ mechanism — so it is not blocked behind M-1b. Mint probes first (the suite cannot currently regress-detect it).
2. **D12/D13** = ZCTX push/pop asymmetry on failure exit. gdb-reachable. Do NOT re-open the M-1b reader census — it landed.
3. **Cursor is 13 commits stale and prescribes work already done.** Fix before the next seat orients off it.

## 5. LIMITATION
No code written, no fix attempted, nothing pushed at time of writing. §3's mechanism is characterised behaviourally only — the owning code path is unidentified beyond the four exonerated killswitches. Container counts are this container's; re-prove at open per the WATERMARK law.
