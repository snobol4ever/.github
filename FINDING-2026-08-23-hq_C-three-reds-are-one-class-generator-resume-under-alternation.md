# FINDING: the front red, the json hang, and json-match-fence are ONE defect — a generator in an alternation arm is never resumed

**Seat:** hq_C · **Date:** 2026-08-23 (s264, FLEET mode, 4 workers) · **Tree:** SCRIP `1257d56c`, `make pristine` rc=0 · **Oracle:** `/home/resources/x64/bin/sbl -bf`

## Claim

`160_pat_alt_inner_gen_resume` (standing front red, both modes), the **json / json-match hang** (5-byte witness `[1,2]`, FINDING-2026-08-23-hq_C-json-hang-bisected-arbno-second-iteration.md), and almost certainly **json-match-fence DIFF** are **the same defect**, not three. Dispatching them to three seats would have put three seats in one file.

## The evidence — `corpus/probe/altgen/`, 7 rungs, refs minted from the oracle

All seven are the same program modulo the pattern, all matched against `[1,2]`:

| rung | pattern inside `'[' … ']'` | oracle | scrip m3 | |
|---|---|---|---|---|
| g01 | `*E ARBNO(',' *E)` | MATCHED | MATCHED | ✅ **control** |
| g02 | `( *E ARBNO(',' *E) )` | MATCHED | MATCHED | ✅ **control** |
| g03 | `( *E ARBNO(',' *E) \| ws )` | MATCHED | **FAILED** | ⛔ |
| g04 | `( *E ARBNO(',' *E) \| 'zzz' )` | MATCHED | **FAILED** | ⛔ |
| g05 | `( E ARBNO(',' E) \| ws )` | MATCHED | **FAILED** | ⛔ |
| g06 | `( *E ARB \| ws )` | MATCHED | **FAILED** | ⛔ |
| g07 | `( ARBNO(*E ',') *E \| ws )` | MATCHED | **FAILED** | ⛔ |

**What the ladder rules OUT, one ingredient per rung:** ARBNO specifically (g06 is plain `ARB`) · the deferred `*E` (g05 has none) · the second arm's content (g04 is a literal that cannot match) · the generator's position in the arm (g07 leads) · parenthesisation alone (g02 is the control that passes).

**What is left is the alternation wrapper itself.** The same generator that resumes correctly bare (g01) and parenthesised (g02) is **not resumed** once it is arm 1 of an alternation and the continuation after the alternation fails.

## That is exactly the checked-in front red

`corpus/crosscheck/patterns/160_pat_alt_inner_gen_resume.sno` is one line:

```
 'aXb' ? ('a' ARB . V | 'q') 'b'      :S(Y)F(N)
```

`ARB` inside arm 1; `'b'` is the continuation that must fail once so `ARB` extends over `X`. Identical shape to g06. The name written on that test — *alt inner gen resume* — has named the mechanism correctly the whole time.

## And it is why json hangs

`json.sno:255-256` is `jarray = '[' (epsilon . *parr()) ( *jelement ARBNO(',' *jelement) | ws )`; `:252-253` is the same shape for `jobject`. The generator is in arm 1 of an alternation. `[1]` passes because zero iterations never need a resume; `[1,2]` needs one and does not get it.

⭐ **The manifestation differs — wrong answer here, non-termination there — and the trigger is identical.** Treat the *wrong answer* as the primary instrument: g03–g07 answer in milliseconds and cannot hang a session, so they bisect and gdb far better than a 5s timeout ever will.

## Consequence for dispatch (FLEET s264)

One seat owns this class, and it is row `160-pat-alt-inner-gen-resume`. `json-alternate-af-spin` stays a **separate** row — seat04 gdb-verified that one as a stationary 2-instruction spin from FLAT-mode choice-record rsp drift, which is a distinct mechanism — but it must NOT be worked concurrently with 160, because a cure for the class may erase its symptom.

## Receipts

```bash
cd corpus/probe/altgen && for f in g0*.sno; do b=${f%.sno}; diff <(../../../SCRIP/scrip $f </dev/null 2>&1) $b.ref >/dev/null && echo "PASS $b" || echo "RED  $b"; done
```
Banked: corpus `4e6eab8bc`.
