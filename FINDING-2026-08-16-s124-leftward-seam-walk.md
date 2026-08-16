# FINDING s124 — THE LEFTWARD SEAM WALK: THE SEAM WAS ALWAYS BUILT, THE ENTRY WAS REFUSED

**Seat:** Claude Opus 5, 2026-08-16, Lon in-chat *"using the IPC sync-step MONITOR, take us home"*.
**Measured at:** SCRIP `3e4f7537` → `1fbc0bcb`, corpus `039e1714` → `ca7ce3a0`, x64 oracle `5035571`.
**Binaries stamped:** `scrip` / `out/libscrip_rt.so` rebuilt in-seat before every verdict.

---

## 1. THE ONE-LINE DEFECT

```
GREEN (LEN(0) ARBNO(*C)):   PAT$0_β:   jmp  n1_match_arbno_β      ← enters the interior seam
RED   (ARBNO(*C) LEN(0)):   PAT$0_β:   jmp  PAT$0_ω               ← dead end, total failure
```

s122 NAMED this dead end. s123 LOCALIZED it to `emit.cpp` ~3105. s124 ROOT-CAUSED it:
**the interior seam was already built and correct; the dispatch simply refused to enter it.**

Measured interior wiring of the RED blob — a correct leftward walk, unreachable:

```
n1_match_len_β:     sub r14d, 0;   jmp  n0_match_arbno_β     ← self-undo, walks LEFT
n0_match_arbno_β:                  jmp  n2_match_defer_α     ← extends by one instance
```

Only the LEFTMOST element's β routes to `PAT$N_ω`. Entering at the right end therefore
walks the whole chain. Nothing needed building — only admitting.

`lower_snobol4.c:2531` had already published the right thing (`body_root` = the SEQ's
rightmost element) and its own comment already stated the law: *"a deterministic carrier's
β is a harmless fail-through, so this is uniform."* The EMITTER was the half that never
honoured it, admitting only `{ARB, ARBNO, BAL}`. A deterministic rightmost element fell to
the `lbl_ω` default. **A spelled-twice disease of the s68/s70 family, but split across the
lower/emit boundary: two halves of one law, one of them silently disagreeing.**

## 2. THE DISCRIMINATOR IS POSITION, NOT DEFERRAL

Three sessions chased the `*` operator. It was never the ingredient.

| pattern | rightmost element | pre-s124 |
|---|---|---|
| `ARBNO(*C)` | generator | GREEN |
| `LEN(0) ARBNO(*C)` | generator | GREEN |
| `LEN(0) LEN(0) ARBNO(*C)` | generator | GREEN |
| `ARBNO(*C) LEN(0)` | deterministic | **RED** |
| `LEN(0) ARBNO('a') LEN(0)` | deterministic | **RED** |

`LEN(0) ARBNO('a') LEN(0)` is RED with an **inline literal argument and no `*` anywhere**.
`LEN(0) ARBNO(*C) LEN(0)` is beauty's shape with `nPush()/nPop()` deleted and still RED —
**the function calls were never required either.** Both retired by a 7-line witness.

## 3. THE HYPOTHESIS THIS SEAT GOT WRONG, AND HOW IT WAS CAUGHT

s124 initially REFUSED `IR_MATCH_DEFER` as a carrier, by argument: its β is
`jmp qword ptr [rsp]`, a resume-THROUGH-RECORD rather than a self-undo, so entering it with
no live record must be a wild jump. That argument is **wrong**. The record IS live at seam
arrival, because the res stub restores `rsp` to exactly the frontier where the defer's own γ
left it. One build and one run refuted a paragraph of reasoning.

⛔ **The refusal is withdrawn and tier 3 is folded in.** Evidence bases differ and the
predicate says so: tier 2 (deterministic) is safe BY CONSTRUCTION — read the templates;
tier 3 (defer) is safe BY MEASUREMENT — zero movers over 318 programs.

## 4. ⛔ THE LAW EARNED — A TWO-READER KILLSWITCH FLIPS IN LOCKSTEP

`SCRIP_DEFER_RESUME` has **two readers**: `sn4_defer_resume()` in `emit.cpp` (half B, lands
the carrier) and `sno_defer_resume()` in `lower_snobol4.c` (half A, publishes it). Inverting
only half B measured **strictly worse than either uniform arm** (seam 1/4 → 0/4): half B
lands a carrier half A never published. That is s121's *"B without A is dead code"* failure
recurring at the DEFAULTS rather than at the landing. **s121's law binds defaults too.**
Before flipping any killswitch default, `grep -rn 'SCRIP_<NAME>' src/` and count the readers.

## 5. GATES (honest A/B, both compilers built in-seat)

| gate | result |
|---|---|
| killswitch OFF byte-identity | **318/318 crosscheck, ZERO diffs** — arm measured inert, not argued |
| default-flip blast radius | 318 programs, **54 changed bytes**, all pattern family |
| crosscheck new default vs measured ON arm | **IDENTICAL, row for row** |
| crosscheck new default vs old default | **ZERO row-level movers** ⇒ all 54 byte-movers are byte-level only |
| killswitch restore | `SEAM_WALK=0` → seam 1/4 (s123) · `DEFER_RESUME=0` → arbnostore 4/9 (pre-s121) |
| probe/seam | **1/4 → 4/4** at default, m3 ≡ m4 |
| probe/arbnostore | 8/9 unmoved (sole RED `arbno_defer_altarg_red` = R-4(a) by design) |
| regens ×3 | RUN AND COMMITTED — benchmark 5 · feature 6 · demo 18 files |

Absolute crosscheck numbers (297/20 m3) come from this seat's own runner over all 318
`corpus/crosscheck/**/*.sno` with a `.ref`; they are **not** comparable to s123's 305/12,
which used a different suite selection. Only the A/B delta within one runner is meaningful.
The 2 DIVERGE rows are present in every arm and are pre-existing.

## 6. ⛔ BEAUTY DID NOT MOVE — AND THE REASON IS NAMED

Beauty is byte-identical-failing at 10/622 lines in every arm measured this seat. The oracle
half stands re-verified: `sbl -bf beauty.sno < beauty.sno` → rc=0, 622 lines, md5
`6f1671c0757729992ae01a6bdf16f081` == the checked-in file.

```
beauty.sno:225   Parse = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop()
beauty.sno:614   Src POS(0) *Parse *Space RPOS(0)              :F(mainErr1)
```

The seam walk handles the `nPop()` tail. What it does **not** reach:

1. **`Command` is a large ALTERNATION** (`*Comment ~ … | *Control ~ … | *Stmt …`), so the
   deferred element inside the ARBNO is an ALT — s121's board-convicted depth class, still
   REFUSED, still the named next rung.
2. **The match site nests two blobs** (`*Parse *Space`), so the seam must walk ACROSS blob
   boundaries, not just within one.
3. `("'Parse'" & 'nTop()')` is a rebound-operator capture in the element list.

**Do not read "the seam walk is the rung that reaches beauty" (s123's prediction) as still
open — it has been done, and beauty needs the ALT-carrier depth story on top of it.**

## 7. NEXT RUNG

**ALT-CARRIER RESUME DEPTH** — admit `IR_DISJUNCTION` as a seam carrier with a depth story
that lands `res` with `rsp` at the ALT's own 32B arm record. s121's falsification (witness
`150`, jmp-through-0, rip=0 with LIVE wires) is the thing to beat; it is the last carrier
class refused. Then re-measure beauty, expecting item 2 above (cross-blob seam) behind it.

**Witnesses:** `corpus/probe/seam/` (4, all green — regression floor) and
`corpus/probe/arbnostore/arbno_defer_altarg_red` (R-4(a), the standing RED).
**Instrument:** `scripts/test_monitor_2way_spitbol_vs_run.sh` runs with NO credential and was
re-confirmed live this seat; `test_monitor_2way_sync_step_bin.sh` still hard-requires
token-gated `csnobol4` and cannot run in a fresh seat.
