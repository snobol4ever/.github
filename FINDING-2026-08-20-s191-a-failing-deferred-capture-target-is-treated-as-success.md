# FINDING s191 (HQ, beauty lane) — ⭐⭐⭐ A DEFERRED CALL IN CAPTURE-TARGET POSITION THAT **FAILS** IS TREATED AS SUCCESS, AND IT IS WHY BEAUTY MIS-CLASSIFIES EVERY TOKEN

**Date:** 2026-08-20 · SCRIP `008c2264` · corpus `+probe/dcap/` · pristine, RT_OPT `-O0` · oracle live `sbl -bf`.
**Lane:** HQ-owned beauty self-host (Lon: *"take over BEAUTY SELF HOST … Let's get it 100%"*). Second rung, immediately after the pre-chain-order cure moved the ladder 3/10 → 5/10.

## 1 · THE WITNESS — EIGHT LINES, WITH ITS OWN CONTROL

```
        DEFINE('chk(s)')                                   :(m)
chk     chk            =  .dummy
        s              'YES'                               :S(NRETURN)F(FRETURN)
m       'ABC'          POS(0) SPAN('ABC') $ tx $ *chk('NO') RPOS(0)   :S(Y)F(N)
```
`chk('NO')` cannot find `'YES'`, so it returns **`:F(FRETURN)`** — a failure.
**Oracle: `nomatch`. SCRIP: `matched`.** A false accept.

**Control (`dcap_freturn_target_ok_ctl`, GREEN):** the identical shape with `chk('YESSIR')`, which **succeeds** via `NRETURN` — both engines match. The control's greenness is what proves the defect is the failure path *only*, and it is the regression guard for any cure.

## 2 · WHY THIS IS BEAUTY'S PARSE WALL

Every one of beauty's token rules is a membership test written exactly this way (`beauty.sno:63-67`):
```
BuiltinVar = SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(BuiltinVars, TxInList)
Function   = SPAN(...) $ tx $ *match(Functions,   TxInList)
SpecialNm  = SPAN(...) $ tx $ *match(SpecialNms,  TxInList)
```
and `match()` (`match.inc`) is precisely `subject pattern :S(NRETURN)F(FRETURN)`. **With the failure ignored, the first guarded alternative always wins.**

Measured on the one-line input `L       X = 1`, with beauty's own tracing armed (`xTrace = 5`) so both engines narrate themselves:

| | oracle | SCRIP |
|---|---|---|
| token `X` | `Push(Id)` | **`Push(BuiltinVar)`** |
| token `1` | `Push(Integer)` | **`Push(BuiltinVar)`** |
| `match()` calls | **7** | **4** |

The three missing calls are the third list (`SpecialNms`): SCRIP never consults it, because the second test already "succeeded". Every downstream symptom — the `Shift`/`Reduce`/`PopCounter`/`TopCounter` chain and the eventual wild jump — is a consequence of parsing `X` as a builtin variable. **The crash was never the bug; a wrong answer four trace-lines earlier was.**

## 3 · MECHANISM

These targets are drained by `rt_dcap_pump` → `c_rt_dcap_end_ok_open`, and that function is called from **`bb_match_end.cpp`** — i.e. at MATCH_END, **after the match has already succeeded**. A failure discovered there has nothing left to retract. SPITBOL fires an immediate (`$`) assignment *during* the match, at the moment its element matches (manual p.87, the same citation s188 used for the `$`-commit rule), so a failing target fails the element **then**.

⛔ **A HAZARD FOR WHOEVER TAKES THE CURE, NAMED SO IT IS NOT DISCOVERED THE HARD WAY:** the pump's return value is **overloaded**. `rt_dcap_pump` returns `rc = 1` to signal a failed target, but `bb_match_end` tests the same register as the **FN-RET transfer protocol** (`test rax,rax; je L(2)`, and the non-zero path treats `rax` as a *transfer address*). A non-zero failure code and a transfer target are therefore indistinguishable at that site — so "just propagate rc" is not a one-liner, and a naive propagation can produce a jump to address 1.

## 4 · KILLSWITCH SWEEP — NO EXISTING ARM MOVES IT

`SCRIP_CAP_NAME_STRICT=0`, `SCRIP_PRE_ORDER=0`, `SCRIP_RTSEQ_RESUME=0` all leave the witness at `matched`. In particular **CAP-NAME-STRICT is not this**: it governs a target that resolves to a *value* rather than a name; here the target resolves fine and simply **fails**.

## 5 · METHOD NOTE — THE ABLATION THAT MADE IT VISIBLE

beauty's own trace variable `xTrace` is never assigned anywhere, so every `GT(xTrace, 4)` trace line silently fails. Setting `xTrace = 5` in a scratch copy turns beauty into a self-narrating parser — **and the ablation was validated by running the oracle on the same modified file** (it still prints the correct `L                 X              =  1`), so the instrumented program is a legitimate witness rather than a second bug. That one-line ablation is worth more than any trace tool built for the purpose, and it is why the divergence was located in minutes after three standalone reconstructions had failed.

Two witnesses at `corpus/probe/dcap/` (1 red, 1 green control), both live-oracle refed.
