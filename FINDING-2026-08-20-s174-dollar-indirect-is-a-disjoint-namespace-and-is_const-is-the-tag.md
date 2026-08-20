# FINDING s174 — the `$()` ruling LANDED: `is_const` was already the namespace tag, so the two namespaces split with no key mangling and 0 `.s` movers

**Seat:** seat2 (`/home/claude2`, Claude Opus 5, CN front) · **Queue row:** `cn-oracle-rulings`
**Unblocked by:** HQ-61, verbatim: *"your probe governs — ORACLE-FAITHFUL CONFIRMED. `$('&X')` routes to the ordinary-variable namespace, wholly disjoint from keyword space, BOTH halves; drop 341-on-indirect-write; the ARCH-SN4-CONSTANTS `$()` clause goes VACUOUS and your FINDING says so with the probe receipts. Lon's desk delegation was 'use SPITBOL as Oracle, details matter not' — a probe that falsifies a ruling's premise supersedes the ruling's letter."*
**Predecessor:** `FINDING-2026-08-19-s173-eval-fails-not-aborts-and-the-dollar-indirect-premise-is-falsified.md` — the falsification receipts and both costings. That FINDING's §2 ("BLOCKED ON HQ") is CLOSED by this one.
**Baseline:** SCRIP `bd183811` · corpus `09542e6f` · oracle `x64/bin/sbl -b` (live; every receipt below is a run).

## Verdict in one line

**Ruling (4) is DELIVERED — option (i), the faithful arm. `SEAT-CN-3` item 4 is CLOSED, both halves.** The implementation is smaller than either costing predicted, because the tag the split needs **already existed**: `NV_t.is_const` was already exactly the set of keyword-space cells.

## 1. The oracle receipt the s173 sibling could not produce — EVERY store, not just the first

s173 proved DISJOINTNESS. It could not see the **seal**, because `cn_indirect_is_ordinary_var.sno` writes each indirect cell exactly ONCE and SCRIP's seal only bites on the SECOND write. Minted this session on live sbl, `probe/cn/cn_indirect_rewrite.{sno,ref}` (**`.ref` is the oracle's verbatim stdout**):

| probe | oracle | what it proves |
|---|---|---|
| `$('&ZED') = 1/2/3` | `1`, `2`, `3` | three successive indirect writes ALL accepted — no seal of any kind |
| `DATATYPE($('&ZED'))` | `INTEGER` | the cell is an ordinary typed variable, not a keyword |
| `$('&ANCHOR') = 'X1'` then `'X2'` | indirect `X2`, **direct `&ANCHOR` still `1`** | two writes, keyword untouched throughout |
| `N = '&ZED'` then `$N` | `3` | reached through an ordinary computed name — same cell |

**This is the receipt that decides the mechanism.** Under the pre-ruling regime SCRIP's second indirect write raised 341, and no witness on the board could see it.

## 2. `is_const` WAS ALREADY THE NAMESPACE TAG — the mechanism, and why not a mangled key

The obvious implementation is to give keyword space a mangled key (`"&\x01N"`, `"&&N"`). **It is the wrong one, and provably so from this project's own corpus:** `$()` names variables with ARBITRARY strings — `beauty.sno:104` is literally `$'$' = *White '$' *White` — so *every* mangled key is a string some program can type, and the disjointness would be a convention rather than a property.

The right one costs nothing. `NV_SET_fn` sealed on the leading `'&'` and **nothing else in the tree sets the bit**, so `is_const == 1` was *already* precisely "this entry is a tier-3 keyword-space cell". Promote it from seal to **namespace tag** and the split is a filter:

- **`_nv_ordinary(e)`** = `!(e->is_const && _nv_kwsplit())` — one predicate, applied in `NV_GET_fn`, `NV_SET_fn`, `NV_EXISTS_fn`, `NV_PTR_fn`, `NV_bind_gva`: the five ORDINARY walkers.
- **`NV_KW_GET_fn` / `NV_KW_SET_fn`** — the complement, and the ONLY minter of sealed cells left in the file. `rt_keyword_read_snobol4`'s two tier-3 arms and `rt_keyword_write_snobol4`'s one now call these. The one-time-assignment seal is unchanged in force AND in wording; it merely stopped being a property of a leading `'&'` in an ordinary store and became a property of the namespace the store came from — which is exactly what the oracle measures (`$('&NEVERSET') = 99` silent; `&C = "one"` then `&C = "two"` still **341**).
- **Two entries may now share a name in one bucket chain.** That IS the two cells.

**⛔ THE ONE NON-OBVIOUS EDIT, AND IT IS A SILENT-WRONG-ANSWER TRAP:** `NV_CONST_ASSIGNED_fn` returned `e->is_const` **of the first name match**. The bucket chain PREPENDS, so the moment an indirect write to `"&N"` lands in front of the constant, the 342 predicate would answer "never assigned" for a constant that *was* assigned — a wrong diagnostic on correct code, reachable only after this ruling and invisible to every witness that does not write both cells. It is now a keyword-space scan (`name match && is_const`), identical for every pre-ruling program.

Killswitch **`SCRIP_KWSPACE_SPLIT=0`** restores the pre-ruling regime exactly: every guard is written as `is_const && _nv_kwsplit()` and every seal as `'&' && !_nv_kwsplit()`, and both `NV_KW_*` accessors delegate verbatim to their ordinary twins on the OFF arm — so the revert is the old call, not an approximation of it.

## 3. The second pinned gate event fired — as designed, and this is now twice in a row

s153 minted `cn_indirect_seal.sno` as a RULING REQUEST that pinned the THEN-current table (`indirect=42`, 341 on the indirect write) and said out loud it existed so the ruling would be VISIBLE rather than silent. **The gate went red on the first run after the flip.** Rewritten to the ruled table, and its header now carries the falsified premise it used to assert:

```
direct=42        indirect=[]       write=[99]      rewrite=[100]
direct-after=42  undeclared=[]     reached-end
```

**⛔ `cn_indirect_seal.ref` is ORACLE-LAW-DERIVED, not an oracle run, and the file says so** — `&USER_DECLARED_CONSTANTS` is oracle-fail by construction (251), so that exact program cannot run on sbl. The LAW it applies is oracle-run byte-for-byte in its two siblings. The three are meant to be read together, and the header says that too.

This is the same mechanism that retired `cn_t1_eval_undecl.err_sno` last session. **Two deliberate pins, two rulings, two red gates on the first run: the convention is earning its keep and should keep being used for anything a ruling might move.**

## 4. Measurements — A/B'd against ORIGIN HEAD `bd183811` (s149 standing law)

| instrument | baseline `bd183811` | this seat | verdict |
|---|---|---|---|
| SNOBOL4 crosscheck m3 | PASS=308 FAIL=9 | PASS=308 FAIL=9 | **identical, same 9 names** |
| SNOBOL4 crosscheck m4 | PASS=306 FAIL=10 SKIP=1 | PASS=306 FAIL=10 SKIP=1 | **identical, same 10 names** |
| DIVERGE (m3 vs m4) | 1 (`141_pat_eval_double_fn_arbno`) | 1 (same) | **identical** |
| CN-4 / UDC gate | 32 PASS 0 FAIL | **40 PASS 0 FAIL** | 8 assertions added |
| CN-13 const-graph gate | green | green | unchanged |
| SNOBOL4 smoke m3/m4 | 6/1, 6/1 | 6/1, 6/1 | identical (`define` PRE-EXISTING, proven so s173) |
| Icon smoke m3/m4 · Icon crosscheck | 14/14, 0 FAIL · 4/4 | 14/14, 0 FAIL · 4/4 | identical |
| Prolog smoke | 3 PASS 2 FAIL | 3 PASS 2 FAIL | identical |
| Prolog crosscheck ×2 each arm | 112/2/75 · 112/1/76 | 111/3/75 · 111/1/77 | **one name differs, and it is a coin flip — see below** |
| `.s` md5 sweep | — | **0 movers / 527 comparable (529 rows)** | codegen byte-identical; **no artifact regen owed** |
| new/changed witnesses | — | 2 witnesses, **m3+m4 green, 0 DIVERGE** | |

**⛔ THE PUSH REBASED ONTO seat1's s183 RT-CARRIER, SO THE VERDICT WAS RE-TAKEN AT THE REBASED HEAD `ffbc1425` — AND WITH THE ONE CONTROL THAT SETTLES ATTRIBUTION.** The crosscheck moved under me: m3 308/9 → **312/5**, m4 306/10/1 → **308/8/1**, DIVERGE 1 → **3** (`expr_eval`, `140_pat_eval_double_fn_trick`, `141_pat_eval_double_fn_arbno` — m3 now passes the first two while m4 still fails them). That is entirely upstream's: running the SAME binary with `SCRIP_KWSPACE_SPLIT=0` reads **312/5, 308/8/1, DIVERGE 3, identical name-for-name in every row**, so this ruling contributes exactly ZERO rows at the new HEAD in either arm. CN-4 gate 40/0 and the smokes are unchanged there too. **A same-binary killswitch A/B is the only control that can separate your rows from a concurrent seat's, and a rebase is exactly when you need it.** (141's count at the rebased HEAD: 20 serial reps, m3 20/20 PASS, m4 20/20 FAIL — still deterministic here.)

**Revert probe (the gate is not vacuous):** `SCRIP_KWSPACE_SPLIT=0` takes the CN-4 gate to **8 FAIL** — both witnesses × both media × both the `.ref` and the stderr-SILENT assertion.

**⛔ THE `.s` A/B WAS RUN THE HONEST WAY, AND IT HAD TO BE.** `nm` on `scrip` finds neither new symbol, which invites the conclusion that a runtime-only edit cannot move codegen — but the `scrip` binary's md5 DOES change (`3efc9203` → `b89974b3`), because `core.c` is linked into the compiler too. The claim was therefore measured, not reasoned: stash → rebuild → sweep → `diff` → pop. **0 movers.** A seat that trusted `nm` here would have skipped the only instrument that can answer the question.

**⛔ THE PROLOG −1 REPEATED TWICE AND WAS STILL NOISE — s173's "UNTIL IT REPEATS" RULE IS NOT ENOUGH, AND HERE IS THE PROGRAM.** Both baseline runs read PASS=112 and both post-change runs read PASS=111, so the delta survived the s173 test. Diffing the PASS-NAME SETS (not the counts) named it in one step: **`rung13_assertz_assertz_unify`**, with every other name identical and each arm's set stable across its two runs. Run directly, that program **SIGSEGVs NONDETERMINISTICALLY IN BOTH KILLSWITCH ARMS** — **6/30 crashes with the split ON, 9/30 with `SCRIP_KWSPACE_SPLIT=0`, which is the exact pre-ruling code path** — and its "PASS" is vacuous anyway: `test_crosscheck_prolog.sh` compares `--run` against `--run`, both of which print NOTHING here against an `.expected` of `two`, so the suite grades a crash-vs-no-crash coin flip. Not this ruling's, not ridden, and now a NAMED find instead of a band. **THE TRANSFERABLE RULE: when a suite delta repeats, diff the NAME SETS before believing the count — and control with the killswitch OFF arm, which is the only same-binary control there is.**

**⛔ DoD-1 REPETITION COUNT (HQ-61's note, seat1's `b7e10d3c` nondeterminism find):** the DIVERGE row above names `141_pat_eval_double_fn_arbno`, so it carries its count. **20 serial reps at this tree, both media: m3 PASS 20/20, m4 FAIL 20/20 — the DIVERGE reproduced 20/20, deterministic HERE.** Both suite readings (baseline and post-change, 1 suite run each) name it. Load-sensitivity was seat1's observation at a different SHA on a different seat; this seat did not reproduce it, and says so rather than repeating the claim.

## 5. What did NOT move, and is still owed

1. **The four s173 divergences are untouched and still upstream of everything** — undefined function answers 5 at top level / nothing inside a fragment where the oracle answers 22 · integer division by zero never raises · the 342-vs-251 split on the default arm · `&ERRTEXT`/`&ERRTYPE` not oracle-verbatim for the compile half.
2. **`$('&pos')` / `$('&subject')` still reach Icon's shared-runtime cells**, because `NV_GET_fn`/`NV_SET_fn` intercept those two names ABOVE the table. It is the same shared-cascade leak class as CN-11, not the constants seal, and the oracle has no counterpart to diff — named here, deliberately not ridden, and it does not touch any assertion above.
3. **`corpus/programs/prolog/rung13_assertz_assertz_unify.pl` SIGSEGVs nondeterministically (6/30 and 9/30 above) and prints nothing where `.expected` says `two`** — a silent wrong answer wearing a flaky-suite costume, pre-existing in both arms, worth its own row.
4. `SEAT-CN-3` items 2 (LEN/POS-family int args through declared constants) and 3 (WAVE-2 `beauty_c` literals) remain untouched.

## 6. Doc of record

`ARCH-SN4-CONSTANTS.md` §Semantics: the `$()` clause was already struck as factually wrong at s173; its "**UDC ARMED STILL DIVERGES … OPEN RULING**" paragraph is replaced by the HQ-61 ruling, the mechanism, the killswitch, and the two witness names. **The `$()` clause is VACUOUS: there was never a bypass to seal, because the seal lives on the cell and `$()` addresses a different one.**
