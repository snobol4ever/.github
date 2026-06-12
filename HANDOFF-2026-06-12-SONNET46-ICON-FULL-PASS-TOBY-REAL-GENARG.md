# HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-TOBY-REAL-GENARG.md

**Session:** 2026-06-12 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — goal file purge + real to-by fix + gen-in-call-arg diagnosis
**HEAD (SCRIP):** `3e08aaa`
**m2:** 198/247 (was 195 at session start)

---

## Work Done

### 1. Goal file purge/compress (committed `67da8832` in .github)

GOAL-ICON-BB.md: updated current-priority banner, compressed BB-hygiene ladder (HY-0…7g ALL DONE), rung ladder, Premise, CONSULT CANONICAL, Session Setup, watermark. Removed 2026-06-06 stale BUG-1..6 session history.

GOAL-ICON-FULL-PASS.md: updated status to m2=195, removed resolved STANDING FINDING (NL β-chain RESOLVED 2026-06-10), deleted completed β-CHAIN-REST step, compressed FULL-18-resid, fixed stale `lower_icon_nl.c` references, added FULL-11 next-in-every entry.

---

### 2. IR_TO_BY real-step fix (+2 m2, committed `3e08aaa` in SCRIP)

**Bug:** `every write(1.0 to 2.0 by 0.5)` produced `0` instead of `1.0 1.5 2.0`.

**Root cause:** `lower_to` sets `IR_LIT(to).sval = "ar"` (ag+real) when the step is a real constant and operands are lowered as nodes (ops[0]=LIT_F=1.0, ops[1]=LIT_F=2.0). In `IR_interp.c IR_TO_BY`, the ag-real path requires `!Lc && !Hc` — but Lc/Hc ARE set from ops[], so the ag path is skipped. The non-ag path then checks `is_real = (sval[0]=='r')` — but sval="ar" has sval[0]='a', so `is_real=false` and the integer path runs, reading LIT_F value via `IS_INT_fn` which returns false → counter=0. Hence output is 0.

**Fix:** `is_real = (sval && (sval[0]=='r' || (sval[0]=='a' && sval[1]=='r')))` — detects both "r" (non-ag real) and "ar" (ag+real with ops).

**Verified:** `every write(1.0 to 2.0 by 0.5)` → `1.0 1.5 2.0`. rung19 pos+neg both PASS. No regressions.

---

### 3. FULL-18-resid: generator-in-user-proc-call-arg (DIAGNOSED, not fixed)

**Bug:** `every write(tag("a"|"b"|"c"))` outputs only `[a]`. `every write(s[1 to 3])` outputs only `a`.

**Root cause (confirmed by `--dump-bb`):** The ALT/TO generator in the call arg completely disappears from the BB graph. For `tag("a"|"b"|"c")`, the graph shows only `CALL tag ival=1` with no ALT nodes wired in. For `every write("a"|"b"|"c")` (which works), the ALT is present in the flat chain.

**Mechanism:** In `lower_icon.c` `lower_call` line 82:
```c
cx->beta = icn_call_allow_gen(name) ? call : ω;
```
`icn_call_allow_gen` returns true only for `find`, `upto`, and user-defined generator procs. For `tag` (not a generator proc) and `[]` (subscript builtin), it returns false → `cx->beta = ω`. When the arg subtree is lowered (e.g., ALT for "a"|"b"|"c"), it receives `ω` as its fail-chain, and `last_gen` from the ALT is not propagated back as the CALL's generator source. The ALT nodes end up with γ/ω pointing to `ω` (EVERY resume), never reachable from the flat trampoline chain.

**Fix direction:** In `lower_call`, detect whether any arg contains a generator (check `cx->last_gen` after lowering each arg). If so, wire the call's `cx->beta = call` so the generator stays in the flat chain and is resumable. The `g_icn_postfix_resume` flag at line 94 is the existing gate for write/writes chaining — the same mechanism needs to activate for all calls with generator args.

**Do NOT:** Loosen the `c9ec94c` / `g_icn_postfix_resume` gate blindly — it guards write-chaining tests that are already green.

**Affected rungs:** rung16 `s[1 to 3]` (+1), rung32 `tag("a"|"b"|"c")` (+1), likely many rung36/37 tests that use generators inside user proc args.

---

## Investigation: FULL-11 next-in-every (CLOSED, NOT a bug)

Initial hypothesis (from NEXT.γ=4α in dump) was that NEXT should point to generator β not α. Investigation showed the primes test (`rung36_jcon_primes`) **already passes correctly** at m2=198 — the "27 appearing" was from a flawed manual test. The flat trampoline preserves TO state=1 correctly when NEXT fires and resumes TO. FULL-11 is closed.

---

## State Invariants (all hold at HEAD 3e08aaa)

- m2 icon smoke 12/12 HARD ✅
- m3 icon smoke 10/12 (2 pre-existing: proc_zeroarg, proc_recursion) ✅
- m4 icon smoke 10/12 (same 2) ✅
- Prolog m2 5/5 HARD ✅
- one-box gate PASS ✅
- No value stack, no C byrd-box functions, no bb_bin_t ✅

---

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
