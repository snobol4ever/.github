# FINDING — the SNOBOL4 master carries a 27-entry CSNOBOL4-dialect probe family, and the harness cannot say so

**Seat:** hq_P · **Date:** 2026-09-05 · **Found while:** diagnosing the inherited row `snobol4-unknown-keyword-assignment-not-detected`
**Tree:** SCRIP `2aff59c4c` · corpus `48d053e21` · measured by execution, m3, `sbl -bf` as the oracle

## What the row looked like, and what it actually is

The row reads: *assigning to an undefined `&KEYWORD` raises no error in SCRIP — silently accepted*. True, and both
oracles raise. But the premise that follows from it — *add the missing detection* — is **wrong**:

⭐ **The detection already exists and already uses SPITBOL's own number and text.** `keywords.c:447` and `:512` raise
`core_runtime_error(251, "keyword operand is not name of defined keyword: <name>")`. Both are gated on
`!rt_udc_on()`, and `rt_udc_on()` is `kwb_own[7] != 0` — the keyword **`&USER_DECLARED_CONSTANTS`**, whose
initialiser (`keywords.c:123`, `kwb_own[8] = {0,0,0,0,0,0,0,1}`) **defaults it to 1**.

Proven by execution, not by reading: adding `&USER_DECLARED_CONSTANTS = 0` to the witness makes SCRIP print `251`
and the full SPITBOL text immediately.

So the defect is **a CSNOBOL4 extension enabled by default under a SPITBOL authority** — the same shape as the END
trap ruled on 2026-09-04 (RULING R1), whose answer was: default OFF, `--compat=csnobol4` adds it back.

## ⛔ Why that answer cannot simply be applied here

**The cost, censused over 1838 of 1859 master entries:** 20 entries assign to an undefined keyword. Two sampled and
run against the oracle:

| entry | its `.ref` | `sbl -bf` says | grades today |
|---|---|---|---|
| `keyword_1` | `amp=hi bare=bare` | `ERROR 251 -- keyword operand is not name of defined keyword` | **PASS** |
| `arbno_span_pos_branch_10` | `match` | `ERROR 251 -- …` | **PASS** |

⭐ **Their refs do not encode SPITBOL — they encode the extension as expected behaviour, and that is deliberate.**
`ALL.csv` puts every one of them in family **`probe_cn`** (27 entries) with origins `cn_namespace_split`,
`cn_const_chain`, `cn_defer_const`, `cn_t1_scalar_fold`, and — literally — **`cn_udc_reopen`**. `cn` is CSNOBOL4.
This is a CSNOBOL4 conformance probe set, correct for its dialect. Nobody made a mistake; the master is carrying
two dialects.

**The blocker:** `corpus_suite_harness.py` has **no `--compat` support and no per-entry dialect mechanism** (zero
grep hits; the `ALL.csv` `modes` column reads `UNKNOWN` for 1797 of 1859 rows). So "default OFF + compat switch" is
**unimplementable as a landing today**: the switch exists in the compiler and the suite cannot reach it. Flipping
the default without that reds ~20 currently-green entries.

## ⚠️ The part that outlives both rows, and why this is a FINDING and not just a ledger line

The announcement basis is **100% of the INDUSTRY STANDARD**. At least 27 SNOBOL4 master entries are graded against
**CSNOBOL4-only behaviour**, and the master records that fact **only in an origin string** — not in anything the
runner reads.

⛔ **A two-dialect suite with an implicit dialect reports green for entries graded against a contract the headline
does not claim.** That is fine if the dialect is explicit and per-entry; it is not fine while it is implicit and the
default is SPITBOL. This is a corpus-provenance and scoping question for ceo/hq_T, not a compiler defect — routed
as an `ask`, not filed as a row.

## Correction to guidance I issued earlier today

⛔ I told two seats that `core_err_msgs[]` **is** the Griswold/CSNOBOL4 table, so new errors should take CSNOBOL4
numbers (7 for unknown keyword, 3 for subscript). **Withdrawn — measured and too strong.**
`core_runtime_error(code,msg)` consults the table **only** when `msg` is NULL and `1<=code<=39`; the tree carries
22 low-code and 20 high-code call sites, and low codes pass explicit messages too (`core.c:603` raises code `1`
with `"… is not numeric"`). The convention is **mixed**; there is no single rule to appeal to.

⭐ **The rule that replaces it, and it would have saved all three rows I touched today:** **before inventing an
error code, grep for the oracle's own message text.** Unknown keyword (`251`), subscripted operand (`235`), and
unary-not-numeric (`1` with explicit text) all **already existed in the tree**. Not one needed a new code.
**I ruled from the error TABLE when the answer was in the CALL SITES.**

## Sibling row, same shape, narrower than written

`snobol4-subscript-undeclared-operand-not-detected` is also already implemented: `pattern_match.c:1299`
(`c_rt_subscript_var_container_only`) raises `kwb_error(235, "subscripted operand is not table or array")`, and as
an **rvalue** (`A = 5; OUTPUT = A<1>`) SCRIP already prints `235` **byte-identical to `sbl -bf`**. The defect is
confined to the **assignment (lvalue)** path, which routes to the plain `c_rt_subscript_var` (`:1250`) — that
variant returns `FAILDESCR` silently. It is a variant-selection question, not missing detection.
⭐ **Use the rvalue arm as the control when curing it:** it is already correct, so a change that reds it has overreached.
