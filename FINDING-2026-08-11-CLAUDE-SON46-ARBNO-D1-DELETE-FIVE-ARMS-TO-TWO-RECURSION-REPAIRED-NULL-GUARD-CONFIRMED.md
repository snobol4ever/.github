# FINDING 2026-08-11 (Claude Sonnet 4.6) — ARBNO D-1 DELETE: FIVE ARMS TO TWO; RECURSION-THROUGH-ARBNO REPAIRED; NULL GUARD CONFIRMED BY MEASUREMENT

**HEAD at close:** SCRIP `57e40a2f` · corpus `5da04e78` · `.github` this commit.
**Zero src/ bytes changed in .github or corpus this session.**

---

## 1. THE QUESTION LON ASKED

"ARBNO is WIRING ONLY. Get rid of all that nonsense. Tell me one good reason why ARBNO needs to do ANYTHING whatsoever."

**Answer, measured not argued:** ARBNO needs exactly ONE BB local — 16 bytes, two dwords. It needs nothing else. The 422-line / five-arm / six-killswitch template was the mess; the correct design was already sitting in the `bb_match_arbno_frameless` arm, unused by most cases.

---

## 2. THE ONE GOOD REASON (from corpus/probe/bb/test_sno_arbno_csl1a.c)

The seed poses it as an open question and answers it by running two arms:

| CELLSZ | result |
|---|---|
| 0 — body allocates nothing | `ARBNO_ω reached with Δ=3  (correct: 0)` ❌ |
| 1 — body claims 1 byte | `ARBNO_ω reached with Δ=0` ✅ |

**The ZETA frontier displacement IS the committed-instance counter.** When the body claims zero per instance, the frontier never moves, the retract finds `ζ == base` on the first try, and jumps straight to ω — three committed instances never unwound, cursor escapes corrupted.

ARBNO's ONE BB local stores DELTA0 (the entry cursor snapshot). The retract cascade compares `r14d` (current cursor) against `[rsp+0]` (DELTA0). That comparison is the counter: it is zero when the cursor has walked all the way back. zd_k(ARBNO)=16 is THE ONE AUTHORITY; the frameless_k arm bills `kk+16` per instance so a K0 body still advances by ARBNO's own cell.

---

## 3. WHAT THE LIVE FRAMELESS ARM ACTUALLY DOES

```
α:   sub  rsp,16          ONE 16B cell — the sole BB local
     mov  [rsp+0], r14d   +0 = DELTA0 (entry cursor snapshot)
     mov  [rsp+4], r14d   +4 = yield  (last committed cursor)
     γ                    shy: succeed on null immediately

β:   jmp body_α           WIRING — pure transfer

(2): cmp  r14d,[rsp+4]    COMPARE 1: did cursor advance?
     je   body_β          no advance → stop extending
     mov  [rsp+4], r14d   record new yield
     γ

(3): cmp  r14d,[rsp+0]    COMPARE 2: back at entry?
     jne  body_β          no → retreat further
     add  rsp,16          release the cell
     ω                    final failure
```

**No increment. No decrement. No counter. No count at +8.** Two cursor comparisons. That's it.

COMPARE 1 is also the null-body guard: a body that matches null leaves r14d == [rsp+4], je fires, extension stops. Confirmed by measurement:

```
'x' ? POS(0) ARBNO('') RPOS(0)      → =F   rc=0  (correct, no hang)
'x' ? POS(0) ARBNO(LEN(0)) RPOS(0)  → =F   rc=0  (correct, no hang)
```

The manual has no null-body prohibition (error #61 is type-only: "ARBNO argument is not pattern"). The protection is COMPARE 1's progress test, not a guard.

---

## 4. D-0 MANIFEST — ARM TRAFFIC BEFORE DELETE

Instrument added: `arbno_arm_diag()` on `SCRIP_ARBNO_DIAG=1` channel, names the template arm at emit time.

| probe | arm (before) | result |
|---|---|---|
| n24 `ARBNO('ab')` | TAIL | =S |
| n27 `ARBNO(',' SPAN('ab'))` | FRAMELESS_K | =S |
| n28 `ARBNO(',' 'ab')` | TAIL | =S |
| n32 `ARBNO('AA'\|'BB'\|'CC')` | TAIL | =S |
| n32b (failure subject) | TAIL | =F |
| min2 `L='x'\|'('ARBNO(*L)')'`, depth 1 | NARY-CHAIN | =S |
| **min1 depth 2** | **NARY-CHAIN** | **💥 SEGV** |
| **nest** manual p.122 example | **NARY-CHAIN** | **💥 SEGV** |
| iso_nest inner | FRAMELESS | =S |
| iso_defer | NARY-CHAIN | =S |

Correlation: NARY-CHAIN → crash/wrong on depth≥2 recursion-through-ARBNO; FRAMELESS_K → always correct. The legacy TAIL arm passed accidentally.

---

## 5. D-1 DELETE — WHAT WAS REMOVED

`bb_match_arbno()` dispatch: five arms → two.

**Removed:** TAIL (`fc_tail` carry-the-tail, 48B root records, chainheads, view repointing, saved-rbp, counter dance at `+8`, exhaust pointers) · DT (`ps-3 defer-tail`, blob-owned frames, zero linkage) · NARY-CHAIN (48B per-activation root record, linked frame chain — the broken arm).

**Kept:** `bb_match_arbno_frameless_k` (kk>0 bodies) · `bb_match_arbno_frameless` (K0 bodies) · two bomb guards.

`emit.cpp`: carry-the-tail claim gated to dead branch (`if (!_k16r && 0 && _tailc)`); `zls_arbno_geom` is now sole geometry authority.

Deleted bodies preserved behind unreferenced `bb_match_arbno_DELETED_ARMS()` for `git revert` safety per D-1 charter. Physical excision + dead killswitch removal is next seat.

---

## 6. POST-DELETE MEASUREMENT

| probe | before | after |
|---|---|---|
| min1 `'((x))'` recursion-through-ARBNO | 💥 SEGV | ✅ =S |
| nest manual p.122 canonical | 💥 SEGV | ✅ =S |
| n24 / n27 / n28 / n32 / min2 / iso_defer / iso_rec | ✅ | ✅ |
| **n32b** alternation body, failure subject | =F | ⚠️ no output |
| **iso_nest** `ARBNO(ARBNO('ab'))` | =S | ⚠️ =F |

Repaired 2 (the crashes). Broke 2 (the previously-routed-around classes, now visible).

---

## 7. THE TWO REGRESSIONS — WHAT THEY ARE

**n32b (no output, rc=0):** `POS(0) ARBNO('AA'|'BB'|'CC') RPOS(0)` on subject `'AABBB'` (should =F). Neither S() nor F() fires — the failure-edge escape exits the statement without reaching either goto. Alternation body, `sq=0` gate — this class was declined by the K16 prelude and routed to legacy; it is now on the frameless arm for the first time. 2-way monitor is the next move; reading code is not.

**iso_nest (=F instead of =S):** `ARBNO(ARBNO('ab'))` on `'abab'`. The outer ARBNO's committed-instance retract interacts with the inner's frontier in a way that doesn't compose. Also previously declined (`_fr=1` gate) and now on frameless for the first time.

Both are newly visible debt, not regressions against a previously correct state.

---

## 8. SPITBOL MANUAL READINGS THIS SESSION

- Ch. 7 p. 86: deferred evaluation `*name` — fetches current value at match time, not construction time. Valid args: ANY BREAK BREAKX LEN NOTANY POS RPOS RTAB SPAN TAB, or lifted one level (`*EQ(I,4)`).
- Ch. 9 p. 121-123: ARBNO — shy, retried on backtrack, each retry supplies one more instance. `ARBNO(P) ≡ ("" | P | P P | ...)`. Recursive patterns via `*LIST` forward reference.
- Ch. 9 p. 125-127: FENCE — blocks backtracking past it; as first component anchors unanchored match. `FENCE(P)` makes P's alternatives invisible to backtracking from outside P.
- Error table: #61 "ARBNO argument is not pattern" — type check only, no null-body prohibition.

---

## 9. NEXT SEAT — IN ORDER

1. **Physical excision** — delete `bb_match_arbno_DELETED_ARMS()` body + dead killswitches (`arbno_rootspine`, `arbno_fprpop`, `arbno_lon`) + dead tail/DT staging in emit.cpp. One commit.
2. **n32b diagnosis** — 2-way monitor on `n32b`; first divergent event names the fix. Do NOT read code first.
3. **iso_nest diagnosis** — same instrument after n32b is green.
4. **Broad-336 + m4** — both still owed, untouched this session.
5. **D-3 GATE** — `test_census_rbp_frames.sh`, T5 establishments → 0, keepers unchanged.
