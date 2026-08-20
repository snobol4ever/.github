# FINDING s182 — THE M1 WALL IS ONE EMPTY LINE, AND THE MECHANISM IS β-RETREAT INTO A DEFERRED PATTERN

**Seat:** HQ (Fable 5, max effort), 2026-08-20. **Tree:** SCRIP `26587504` + this session's two edits, corpus `9fd581f1`, pristine build at RT_OPT=-O0.
**Lon's order this session:** *"stop when you have a concrete simple example, a reproducer, and SHOW ME."* This file is that record.

## ⭐ THE HEADLINE — M1 REDUCES TO A ONE-BYTE INPUT
`beauty.sno` fed a file containing **a single newline** answers `Parse Error`. The oracle beautifies it correctly.
```
printf '\n' > m1_min.in                       # corpus/programs/snobol4/demo/beauty/m1_min.in (checked in)
scrip beauty.sno < m1_min.in                  # -> Parse Error          (WRONG)
x64/bin/sbl -bf beauty.sno < m1_min.in        # -> (blank line)         (RIGHT)
```
This supersedes every prior spelling of the wall ("the FIRST Shift/Reduce parse", s170). **Only `*`/`-` comment lines survive** — and only because `main01` short-circuits them (`Line POS(0) ANY('*-')`) before the parser is ever entered. Every other input class fails: empty line, bare label `START`, `X = 1`, `:(END)`, `END`.

## THE MECHANISM, MEASURED SIDE BY SIDE (not inferred)
Probe inserted at `beauty.sno` `main05`, both engines, same file, input `        X = 1`:
| probe | SCRIP | ORACLE |
|---|---|---|
| `SIZE(Src)` | 14 | 14 |
| `Src POS(0) (*Parse $ pcon)` → `SIZE(pcon)` | **0** | **0** ← both agree |
| `Src POS(0) *Parse RPOS(0)` | **FAILED** | **OK** |
Both engines agree the FIRST match of `*Parse` is zero-length. The oracle then **backs into `*Parse` and retries** until an alternative consumes all 14 characters. **SCRIP never re-enters.** The failing statement is `main05`:
```
Src  POS(0) *Parse *Space RPOS(0)   :F(mainErr1)
```
β-retreat into a deferred pattern value is dead on this road. **This is ARCH-PASSTHRU law 0/0a/0b territory exactly** — the crossing back into a suspended graph.

## TWO SEGVs IN BEAUTY CONTEXT (harder signal than the wrong answer — NEW WITNESSES)
Override `Parse` in otherwise-unmodified beauty, input = one newline:
| override | SCRIP | ORACLE |
|---|---|---|
| `Parse = *Command` | **SIGSEGV** | ok |
| `Parse = ARBNO(*Command)` | **SIGSEGV** | ok |
| `Parse = *Label nl` | **SIGSEGV** | ok |
| `Parse = *Stmt (nl \| ';')` | ok | ok |
| `Parse = *White nl` | Parse Error | Parse Error (both — legitimate) |
gdb on the `*Label nl` arm: `SIGSEGV in _rtld_global`, then `#1 0x0000000000000000 in ?? ()`. **The return address itself is garbage** — a wild jump through a corrupted continuation, i.e. the pass-thru class, not a data bug. `Label = BREAK(' ' tab nl ';') ~ 'Label'`, and `~` is `OPSYN('~','shift',2)` where `shift = EVAL("p . thx . *Shift('" t "', thx)")`.

## ⛔ AN ELEGANT HYPOTHESIS, FALSIFIED BY TEST — RECORDED SO NOBODY RE-DERIVES IT
**Hypothesis:** beauty is killed by the whole-program fz poison. `semantic.inc`/`assign.inc`/`ShiftReduce.inc`/`omega.inc` all call `EVAL`, which sets `g_sno_fz_unsafe` (`lower_snobol4.c:1001`), which unseals EVERY name (`sno_seal_pat`, `:968`), so no grammar pattern folds statically.
**Test:** `SCRIP_FZ_FORCE=1` (diagnostic added this session at the `sno_seal_pat` guard; zero new state, getenv read at the guard) forces the poison off.
**Result: beauty is UNCHANGED in both arms — `Parse Error` at `SCRIP_FZ_FORCE=0` and at `=1`, on both inputs.** ⛔ **THE POISON IS NOT BEAUTY'S BLOCKER.** beauty's grammar patterns are *genuinely* built at runtime by `EVAL` inside `shift`/`reduce`; there is no static road for them to fall off. The defect is squarely the runtime pattern road losing β-retreat.
⚠️ `SCRIP_FZ_FORCE` is **DIAGNOSTIC ONLY, NEVER A FIX** — it is unsound by construction (the poison exists because a runtime fragment can rewrite any name). The sound cure for the same programs is the DECLARATION road (`sno_const_pat`, which never consults the poison).

## THE POISON IS STILL A REAL AND SEPARATE DEFECT (3 NEW ORACLE-REFED WITNESSES)
Independent of beauty, the poison produces **silent wrong answers** on the runtime-composed road, and `FN__PAT$1` emission is a **1:1 predictor**:
| trigger (added to an otherwise-passing program) | `FN__PAT$N` emitted | verdict |
|---|---|---|
| nothing (control) | 1 | PASS |
| `EVAL` / `CLEAR` / `CONVERT` / `$('ZZ') = 1` anywhere | **0** | **nomatch (oracle: match)** |
| indirect *read* `Z = $('ZZ')`; a second write to `P2` | 1 | PASS |
Witnesses landed in `corpus/probe/passthru/`: **`ptw_min_poison_eval`**, **`ptw_min_compose_nocap`**, control **`ptw_min_compose_ctl`** (the asm-diff pair — one line apart; `FN__PAT$1:` + `PAT$1_res:` present in the control, ABSENT in the twin; 727 vs 547 lines).
**`ptw_min_compose` SIMPLIFIED:** the s180 cursor recorded this class as "ARBNO-value **+ capture-value** β-retreat". **The capture is NOT an ingredient** — removing it keeps the failure (`ptw_min_compose_nocap`). Measured ingredient set: whole-program poison · ARBNO pattern-value in a variable · an empty-string value in a variable · runtime composition of TWO variables · the defer. `POS(0)`/`RPOS(0)` are OBSERVABILITY, not cause (without them a zero-iteration ARBNO succeeds spuriously and hides the bug).

## THE CONSTANT-DECLARATION ROAD — CN-3c HAS LANDED, AND A DOWNSTREAM GAP REMAINS
Lon's `&USER_DEFINED_CONSTANTS` lever is the sound cure for the poison class (`sno_const_pat` never consults it). **Measured state:**
- ⛔ **DOC ROT, CORRECTED HERE:** `lower_snobol4.c:987` and `:1901` still say the `sno_pat_supported` `TT_KEYWORD` arm is missing and is "the ONLY blocker" (s148 wording). **That arm LANDED with CN-12** and is present today. HQ's first pass this session believed those comments; they must be rewritten in place.
- **`TT_FNC` returns 1** — calls in pattern position (`nPush()`, `shift`) do NOT block registration either.
- **AND YET the composed-constant road still fails**, so the remaining gap is DOWNSTREAM of registration and is currently unidentified. Witnesses landed in `corpus/probe/cn/` (refs SCRIP-pinned to the semantic truth the plain control establishes — `&` forms are ORACLE_FAIL by construction, error 251):
  | witness | form | verdict |
  |---|---|---|
  | `cn_const_compose_ctl` | `A=..; B=..; P2 = A B` | PASS |
  | `cn_const_compose_leaf` | `&A=..; &B=..; P2 = &A &B` | **RED** |
  | `cn_const_compose_all` | `&A=..; &B=..; &P2 = &A &B` | **RED** |
  Constants built **inline** (`&P2 = ARBNO('a') ''`) work. Constants composed **from other constant references** do not — which is precisely the "traverse down the references and inline at compile time" half of Lon's brief.
- **A HANG:** `&P2 = &A &B` with a capture on the defer (`(*&P2 $ got)`) does not answer at all — `rc=124` at an 8s cap.

## LON'S QUESTION, ANSWERED (in-chat s182): *"were you trying to process the EVAL during constant folding via nPush/nInc/nDec/nPop and Shift/Reduce?"*
**No.** `SCRIP_FZ_FORCE` only disables the poison GUARD on the table `sno_seal_pat` already holds. It does not evaluate `EVAL` at compile time and folds nothing through the semantic functions. **Whether it SHOULD is the open design question**, and beauty's own `semantic.inc` header argues yes: *"these functions are called while building the parser patterns, **not during pattern matching**."* Their arguments at every call site are constants (`'Label'`, `1`, `7`), so `shift(BREAK(...),'Label')` is compile-time determinable in principle. Doing it = partial evaluation of the semantic layer. **NOT ATTEMPTED, NOT COSTED — it is a ruling for Lon, not a rung HQ may mint alone.**

## RECEIPTS (pristine, RT_OPT=-O0)
- **corpus m3 331/6 · m4 325/11 — EXACT match to the s181 watermark. Zero regressions.**
- passthru combo board **m3 108/112 · m4 100/112** (was 107/109 over 109 rows: +3 rows landed, +1 pass, +2 honest new reds per law 0d).
- **META SCORE 69.4** (13 suites, 1729 rows, `test-results/scorecard-s182-meta`; s179 read 69.0, s91 baseline 38.0).
- Both session edits are default-arm inert: the `SCRIP_FZ_FORCE` guard short-circuits identically when unset; the scorecard change is report-side only.

## INSTRUMENT REPAIR (the scorecard was DEAD and reporting nothing)
`scorecard_snobol4.sh report` hard-called **`gawk`, which is not installed on this box** — every report since the last gawk-bearing environment printed a header, an error line, and NO SUITE ROWS AND NO META. Fixed: `${AWK:-awk}` + the one gawk-ism (`PROCINFO["sorted_in"]`) replaced by a portable explicit top-3 max scan. **Also documented a live footgun:** every `run` truncates `<out>/results.tsv` first, so two `--suites` runs sharing one `--out` is NOT a union — the second wipes the first and `report` then scores a partial denominator that LOOKS like a whole board. HQ hit this exact trap this session before catching it.

## NEXT, IN ORDER (HQ's read)
1. **The β-retreat-into-defer road** — the M1 blocker. `Parse = *Command` SEGV on a one-byte input is the sharpest handle ever held on it; asm-diff its passing sibling `Parse = *Stmt (nl | ';')`.
2. **Lon's ruling** on partial-evaluating the semantic layer (above) — it decides whether the `&PATTERNS` conversion of beauty (queue row 36) can help at all, since beauty's patterns are EVAL-built.
3. The downstream composed-constant gap (`cn_const_compose_*`).
4. Rewrite the two stale s148 comments in place (DOC RULE).
