# FINDING 2026-07-25 (s160) — CSET LITERALIZATION OF THE FIFTEEN: THE FOLD ALREADY FIRED ON 3 OF 5, AND THE 2 IT MISSED WERE MISSED FOR A NAMED REASON (CAPTURE-ASSIGNED VAR DEFEATS `sno_cconst_lookup`) — SIZE WIN, NOT TIME WIN

**Session:** s160 · **Goal:** GOAL-SNOBOL4-BB.md, cursor item NEXT-(1) (`&LCASE`/`&UCASE` rewrite of the workhorses)
**Scope:** corpus only. **NO `src/` CHANGE.** No `.s` regen owed (RULES handoff step 4 does not fire — codegen untouched).
**Directive:** Lon — *"Use concatenation of literals, &LCASE, and &UCASE only for arguments to ANY, NOTANY, SPAN, BREAK, and BREAKX. NO VARIABLES."*

---

## 1. WHAT LANDED

All **15** working-set demos now pass cset arguments as literals / `&LCASE` / `&UCASE` / `CHAR(n)` only. **Zero variables** reach
`ANY` / `NOTANY` / `SPAN` / `BREAK` / `BREAKX` anywhere in the working set.

Ten of the fifteen (`*-match`, `*-match-fence`) were **already** literal — untouched. Five carried variables:

| Program | Before | After |
|---|---|---|
| `claws5` | `SPAN(DIGITS)`, `ANY(UCASE)`, `SPAN(DIGITS UCASE)` | `SPAN('0123456789')`, `ANY(&UCASE)`, `SPAN('0123456789' &UCASE)` |
| `treebank-list` | `SPAN(' ' nl)`, `NOTANY('( )' nl)`, `BREAK('( )' nl)` | …`CHAR(10)` in place of `nl` |
| `treebank-array` | same three | same |
| `calculator-1` | `ANY(LCASE)`, `SPAN(DIGITS)` | `ANY(&LCASE)`, `SPAN('0123456789')` |
| `calculator-2` | `ANY(LCASE)`, `SPAN(DIGITS)` | `ANY(&LCASE)`, `SPAN('0123456789')` |

**`&DIGITS` deliberately NOT used** — it is not a standard SPITBOL keyword (s159 ruling); digits stay the literal `'0123456789'`
so the rewrite compiles identically under `sbl` and SCRIP.

**`CHAR(10)` is the newline form** — a newline cannot be written as a quoted literal in SNOBOL4 source. It is in
`sno_cset_fold`'s coverage (`CHAR(n)`-int arm) and is exactly what the already-literal sibling `treebank-match.sno`
uses for the same two patterns, so it is the established idiom here, not an invention.

**MANUAL BASIS (SPITBOL v3.7, Ch.16 Protected Keywords, p.188):** `&LCASE` is the string of 26 lower-case alphabetic
characters in ascending order; `&UCASE` the 26 upper-case. Both are **PROTECTED** — the program cannot assign them, which is
precisely what makes folding them sound under the s159 ruling that the *variable* fold is not. `&ALPHABET` (p.187) is the
256 ASCII characters in ascending order and `CHAR(i)` (Ch.19, p.217) converts an integer ordinal to a character string,
so the corpus idiom `&ALPHABET POS(10) LEN(1) . nl` ≡ `CHAR(10)` exactly.

---

## 2. THE GATE — ORACLE EQUIVALENCE, 5/5 IDENTICAL

`sbl(original)` vs `sbl(rewritten)`, s107 recipe verbatim (temp-prepend `-CASE 0` + tab `&TRIM = 0`, `-b -d512m -i64m`,
`-s256m` for treebank), full corpus inputs:

| Program | rc orig | rc new | output bytes | verdict |
|---|---|---|---|---|
| claws5 | 0 | 0 | 155,589 | **IDENTICAL** |
| treebank-list | 0 | 0 | 281,686 | **IDENTICAL** |
| treebank-array | 0 | 0 | 281,844 | **IDENTICAL** |
| calculator-1 | 0 | 0 | 5,885 | **IDENTICAL** |
| calculator-2 | 0 | 0 | 5,878 | **IDENTICAL** |

A rewrite that changes behaviour is a bug, not a speedup. It does not change behaviour.

---

## 3. ⭐ THE NEW FACT — WHY TWO OF FIVE ACTUALLY MOVED

s159 diffed `--compile` output for `claws5` and `calculator-2` and found **byte-identical**, concluding the literal rewrite
buys nothing but insurance. That conclusion is **correct for those two and now confirmed for a third**, and **wrong as a
generalization** — because s159 never tested the treebank pair:

| Program | orig `.s` | new `.s` | delta |
|---|---|---|---|
| claws5 | 149,023 | 149,023 | **identical** — fold already fired |
| calculator-1 | 149,714 | 149,714 | **identical** — fold already fired |
| calculator-2 | 150,015 | 150,015 | **identical** — fold already fired |
| **treebank-list** | 221,179 | **217,474** | **−3,705 B** |
| **treebank-array** | 253,315 | **249,568** | **−3,747 B** |

**THE MECHANISM, NAMED:** `sno_cconst_lookup` admits a variable on `total==1 && clean==1` — assigned exactly once, cleanly.
`DIGITS = '0123456789'` and `LCASE = &LCASE` are clean simple assignments, so they folded all along. **`nl` is assigned by a
PATTERN CAPTURE** — `&ALPHABET POS(10) LEN(1) . nl` — which is not a clean simple assignment, so `cconst_lookup` refused it
and **the treebank csets were being constructed at RUNTIME on every build**.

**WHAT THE FOLD REMOVED (treebank-list, normalized asm diff):** 6 × `IR_VAR` (the runtime reads of `nl`), 19 α entries +
17 β resumes (**whole Byrd boxes**), 131 instructions net (6,713 → 6,582). This is a genuine constant-BB collapse:
runtime cset construction became sealed compile-time constants.

---

## 4. ⛔ BUT IT IS A SIZE WIN, NOT A TIME WIN — MEASURED, NOT ASSUMED

Same-moment interleaved A/B, `treebank-array` mode-3, input amplified 4× (400,620 B in / 1,127,346 B out),
**identity=OK verified for BOTH variants against `sbl` at that size before timing**, RT_OPT=`-O0`:

```
orig (var nl) ms: 16356 15488 18663   median 16356
new  (folded) ms: 16399 15928 16560   median 16399
A/B new vs orig: 0.997x  (-0.3%)
```

**−0.3% against a 15.5–18.7 s spread is noise.** The 19 removed boxes run during **pattern CONSTRUCTION**, which happens
once at `delim`/`word` definition — **not in the per-token match loop**. Removing one-time setup work cannot move a
token-bound workload.

⇒ **RULE (same family as s157's "name the LINE, not the store"): a fold that removes CONSTRUCTION-path boxes must justify
itself on SIZE or on CONSTRUCTION-heavy workloads — never quote it as a match-loop speedup.** The lever for the slow demos
remains frame accumulation / backtracking cost (s157), untouched by this.

---

## 5. CORRECTNESS BASELINE — REPRODUCED EXACTLY, NO REGRESSION

Tri-identity on the 5 rewritten programs (sbl vs m3 vs m4), fresh `-O0` build (`scrip` + `libscrip_rt.so`):

| Program | M3 | M4 | note |
|---|---|---|---|
| claws5 | DIVERGE | IDENT | MODE34-VIOLATION (pre-existing, s158 ordinal-20 capture bug) |
| treebank-list | IDENT | DIVERGE | MODE34-VIOLATION (pre-existing) |
| treebank-array | IDENT | DIVERGE | MODE34-VIOLATION (pre-existing) |
| calculator-1 | IDENT | IDENT | |
| calculator-2 | IDENT | IDENT | |

**Identical to the s158/s159 board.** The rewrite introduces no divergence and fixes none — those three are separate,
already-documented defects. The other ten demos are **byte-unchanged sources**, so their status is unchanged by construction.

---

## 6. WHY THIS IS WORTH HAVING EVEN AT ZERO SPEED

Per the s159 ruling, the VAR arm of the cset fold is **dangerous**: indirect assignment (`$('DIG' 'ITS')`), immediate
assignment in a pattern, later fragments, and `CODE()` run-time compilation can all write a name after the analysis decided
it was constant. Every one of the fifteen demos now folds through **protected keywords and literals only** — forms the
program provably cannot rewrite. The working set no longer depends on the unsound arm at all.

**⇒ THE UNBLOCKED RUNG:** removing (or gating) the `VAR`-via-`cconst` arm of `sno_cset_fold` is now testable against this
working set without losing any fold that the demos actually rely on. That is a `src/` change with full-crosscheck blast
radius and is NOT done here — it is proposed, with the corpus prerequisite now satisfied.

---

## 7. ARTIFACTS

- Corpus: 5 `.sno` files edited in `corpus/programs/snobol4/demo/`. Nothing else touched.
- Gate script (session-local, not committed unless directed): oracle equivalence A/B, `sbl(orig)` vs `sbl(new)`.
- Pristine originals preserved at `/home/claude/base/` for the duration of the session.
- RT_OPT=`-O0` throughout. No `-O1`/`-O2` anywhere (RULES O2-DIRECTED-ONLY).
- `handoff_status.sh` is the push truth — not this document. **No push status is asserted here** (RULES stale-orientation rule (a)).
