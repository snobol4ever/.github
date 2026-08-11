# FINDING 2026-08-11 (Claude Opus 5, s18b) — FF-0b SETTLED BY BUILD-AND-RUN: THE "DIVERGE QUARTET" SPLITS IN HALF, THE BLAST-RADIUS TABLE IS STALE, AND FF-3's ≥9/15 FLOOR IS UNREACHABLE BY FF-1/FF-2

**Fingerprint:** SCRIP `5fbefd41` (mainline, restored; **zero `src/` bytes changed all session**) vs `930539c0` (last-good parent of DEL-T1 D-1 `1af93e3a`) · corpus `5da04e78`.
**Method:** two real builds, both self-checked, m3, best-of-3 per program, board recipe verbatim (`-CASE 0` + tab `&TRIM = 0` temp-prepend, `sbl -b -d512m -i64m`, `ulimit -s unlimited`). Instruments committed: `ff0b_quartet.sh`, `board_m3.sh`.

⭐ **BUILD SELF-CHECK (do this before trusting any A/B):** at `930539c0` the FF-0 witness `treebank-match < treebank.input` returns **rc=0** where HEAD gives **rc=139**. The rebuild is therefore genuinely a different compiler, and the bisect's GOOD end is independently re-proved. Without this check an incremental build that silently did nothing looks exactly like a clean result.

---

## 1. ⛔⭐⭐⭐ THE QUARTET IS NOT ONE SET. IT SPLITS BY FAMILY.

FF-0b asked: is the never-bisected calculator DIVERGE quartet the DEL-T1 culprit, or a second defect? **Both — one family each.**

| program | @`930539c0` (pre-delete) | @`5fbefd41` (HEAD) | owner |
|---|---|---|---|
| `calculator-1-match` | **IDENT** | DIVERGE | ⇒ **DEL-T1. FF recovers it.** |
| `calculator-1-match-fence` | **IDENT** | RC=139 | ⇒ **DEL-T1. FF recovers it.** |
| `calculator-2-match` | **DIVERGE** | RC=139 | ⛔ **OLDER DEFECT. FF cannot.** |
| `calculator-2-match-fence` | **DIVERGE** | RC=139 | ⛔ **OLDER DEFECT. FF cannot.** |

All eight cells stable **3/3** — no oscillation observed in either build. The s17 ASLR-flakiness warning is real but did **not** fire on this set today; still take best-of-N, but a 3/3 result here is not luck.

⭐ The calc-2 pair carries **two stacked defects**: an older wrongness that already diverged pre-delete, plus DEL-T1 converting that divergence into a crash. Repairing FF moves them from SEGV back to DIVERGE — **which will look like a partial win and is not one.** Anyone grading calc-2 by "no longer crashes" will bank a false pass.

---

## 2. ⛔ THE BLAST-RADIUS TABLE IS STALE — 3 OF ITS 4 "DIVERGE" ROWS ARE NOW SEGV

The cursor's blast-radius line records *"DIVERGE both modes: calculator-1-match/-fence · calculator-2-match/-fence."* Measured at HEAD, 3/3 each: **only `calculator-1-match` still diverges; the other three SIGSEGV.** The DIVERGE-vs-SEGV split that FF-0b was framed around no longer describes the board. **Re-measure before reasoning from that table.**

---

## 3. THE PRE-REGRESSION BOARD, MEASURED (m3, `930539c0`) — WHAT FF CAN AND CANNOT REACH

| program | @`930539c0` m3 | reachable by FF? |
|---|---|---|
| `claws5-match` · `claws5-match-fence` | IDENT | already green at HEAD (the defer-free survivors) |
| `treebank-match` · `treebank-match-fence` | IDENT | ✅ **FF's to recover** |
| `calculator-1` · `calculator-1-match` · `calculator-1-match-fence` | IDENT | ✅ **FF's to recover** |
| `claws5` (base) | ⛔ **RC=139** | ❌ **SEGV BEFORE THE DELETE — not DEL-T1's, and not on the cursor's SEGV list at all** |
| `treebank-list` · `treebank-array` | ⛔ DIVERGE | ❌ older debt |
| `calculator-2` (base) · `calculator-2-match` · `calculator-2-match-fence` | ⛔ DIVERGE | ❌ older debt |
| `json-match` · `json-match-fence` | ⏱ **m3 exceeds 110 s** (oracle completes; scrip does not) | ❔ unresolved — see §4 |

**Pre-delete IDENT = 7 of 13 resolved** (json pair unresolved). **FF's entire recoverable set is 5 programs**: the treebank-match pair and the calculator-1 triple.

⛔ **THEREFORE FF-3's GATE (`board ≥ 9/15 both modes`) IS UNREACHABLE BY FF-1/FF-2 ALONE.** Even a perfect FF lands at 7 (+json). The remaining six — `claws5` base, `treebank-list`, `treebank-array`, and the whole `calculator-2` family — were **already broken at the delete's parent** and are untouched by anything in this goal. The s17 scrutiny amendment predicted exactly this shape (*"⇒ second defect, own rung, and FF-3's floor becomes SEGV-class-only"*); it is now measured, and it is worse than that amendment assumed, because the pre-existing set is **six programs, not the calc quartet's two**.

⭐ **This also finally explains the "was 9/15" figure without anyone having to be wrong:** 7 resolved IDENT + the json pair = 9, iff json was IDENT pre-delete. That is consistent, unverified, and the one measurement that would close it.

---

## 4. `json` IS NOT A CRASH PROGRAM PRE-DELETE — IT IS A SLOW ONE

At `930539c0`, `json-match` m3 **exceeds 110 s** while the sbl oracle finishes inside it (620 KB `twitter.json`). It does not SEGV there. At HEAD the cursor records rc=139. So json's HEAD crash is plausibly DEL-T1's, but its **pre-delete state was never IDENT-verified by anyone** — the board's 300 s default TMO hides the cost, and every board number that included json bought it with wall clock nobody itemised. ⛔ **Do not bank json in either direction without a timed run.** A cheaper witness than 620 KB is owed, exactly as the 327 B treebank input was minted for FF-0.

---

## 5. WHAT THIS MEANS FOR "GET THE DEMOS WORKING"

Of the four named families, **FF repairs at most one and a half**:

- **CALCULATOR** — the `-1` triple returns; the `-2` triple does **not** (older defect, own rung).
- **TREEBANK** — the `-match` pair returns; `-list` and `-array` do **not** (older defect).
- **CLAWS5** — `-match`/`-match-fence` are already green; the **base program SEGVs pre-delete** and is nobody's tracked debt today.
- **JSON** — unresolved; needs a timed pre-delete run and a smaller input first.

**Sequencing this implies:** FF is still correct and still worth landing, but it is **not the demo-repair rung** it is being read as. The demo board needs a second, independent ladder for the pre-existing set, and that ladder should be sized off §3's table rather than off any board delta, because a board delta cannot distinguish "FF fixed it" from "it was never FF's."

---

## 6. NEXT SEAT, IN ORDER

1. **Do not grade FF against ≥9/15.** Re-cut FF-3's gate to its true reachable set: `treebank-match`, `treebank-match-fence`, `calculator-1`, `calculator-1-match`, `calculator-1-match-fence` — **5 programs, BY NAME, not by count.**
2. **Mint the pre-existing-defect rung** for `claws5` (base), `treebank-list`, `treebank-array`, `calculator-2` family. `claws5` base is the surprise and probably the cheapest entry — the `-match` variants beside it are green, giving a same-family passing sibling to diff against (the RULES sibling-exoneration method, free here).
3. **Time `json` pre-delete** with a reduced input; settle the 9th slot.
4. Everything in the s18 cursor above (WREG Step 1 retirement) stands unchanged; this finding is orthogonal to it.

⛔ **NOTHING LANDED. NOTHING RESTORED.** SCRIP restored to mainline `5fbefd41`, tree clean; **the built binaries in the container are from `930539c0` — rebuild before trusting any run.**
