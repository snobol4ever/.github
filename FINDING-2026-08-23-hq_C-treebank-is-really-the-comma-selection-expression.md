# FINDING: `demo_treebank` is not a treebank bug — it is `(A , B)` selection, and the failure edge pops a cell belonging to an expression that already SUCCEEDED

**Seat:** hq_C (Fable, s266) · **Date:** 2026-08-23 · **Row:** `vlist-expr-alternation` (re-briefed, assigned seat03) · **Witnesses:** corpus `718139e70` → `corpus/probe/vlist_select/`

## The claim

The last SNOBOL4 corpus red is **not** about treebanks, patterns, or deferred captures. It is the SPITBOL **selection expression** `(A , B)` — value of `A` if `A` succeeds, else value of `B` — and SCRIP's default lowering answers **null** when `A` fails.

## The chain, measured

| step | evidence |
|---|---|
| `treebank.sno` with its own `.input` | oracle `matched bytes=327`; scrip `** Error 235 … subscripted operand is not table or array` |
| the 235 fires inside the SECOND `ListAppend(stack, list())` | non-invasive `DBG()` helper trace (⛔ inline `OUTPUT=` instrumentation perturbs the program — it moved the error to 22; a helper function does not) |
| that is `ListInsert4`: `a = ARRAY('0:' (IDENT(a(x)) 0, size * 2 - 1))` | array-growth path, reached only on the second append |
| direct witness, no pattern machinery at all | `ListAppend` ×3: oracle `0:0 / 0:1 / 0:3`; scrip dies at the second with **Error 164** *prototype argument is not valid object* |
| **the 4-line root** | `x = 'nn'; OUTPUT = 'a=' (IDENT(x) 0, 5)` → oracle `a=5`; scrip prints **nothing at all** |

`ARRAY('0:' null)` is `ARRAY('0:')` — hence 164, and 235 one call later when the field is read back.

## Why the default is null

`lower_snobol4.c:727` — `if (!g_vlist_alt || t->n <= 1) return sx_lower(cx, first, γ, ω, res);` — the default path lowers **arm 1 only** and discards the rest. `SCRIP_VLIST_ALT` (default OFF) is the multi-arm lowering.

## ⭐ The two facts that turn this from an investigation into a fix

**1. `frame-rsp` is byte-correct.** `SCRIP_VLIST_ALT=1 SCRIP_ZETA_STORAGE=frame-rsp` matches `sbl -bf` on **every** rung (`z=5 direct=5 w=9 v=7`). The defect is specific to the default `cell-stack`. ⛔ **`cell-heap` is ALSO wrong now** — the in-tree comment at `lower_snobol4.c:719` claiming "frame-rsp / cell-heap (static offsets) were already right" is **stale**; measured s266, cell-heap loses the prefix exactly like cell-stack.

**2. The emitted asm names the mechanism, so the `zd_plan` theory can be skipped.** In the m4 text of the witness, arm-1's recede runs through **`n6_lit_string_β`** — which is the enclosing **concatenation's left operand**, *outside* the vlist — and that block does `add rsp,16; add rsp,16` before jumping to arm 2. **The arm-failure path pops a cell belonging to an expression that already succeeded.** That is precisely why `'direct='` disappears and the statement prints bare `5`.

`SCRIP_ZD_VLIST_OMEGA=1` (seat03's prototype) **does** fire — diffing the emitted `.s` shows it deletes exactly those two pops — and the answer is **still wrong**. So claiming arm 2 in `zd_plan` is **not sufficient**, and the in-tree comment naming zd_plan as "the actual rung" is at best half the story.

**The fix shape:** catch the arm-failure edge **at the vlist boundary** and restore the spine there, instead of letting recede propagate into the enclosing expression. Sound because the vlist's value rides the named `VLIST$n` variable, not a spine cell — so nothing in the abandoned arm is needed after the boundary.

## Instrument banked

`corpus/probe/vlist_select/` — **5 rungs + 2 passing controls**, all oracle-minted:

| rung | what it isolates | at HEAD |
|---|---|---|
| `c01_control_first_arm_succeeds` | select where arm 1 SUCCEEDS | ✅ PASS |
| `c02_control_no_select` | record-field array subscript, no select | ✅ PASS |
| `v01_select_min` | the 4-line root | ⛔ RED |
| `v02_select_concat_and_assign` | select inside a concat, and via assignment | ⛔ RED |
| `v03_array_proto_via_select` | `ARRAY('0:' select)` | ⛔ RED |
| `v04_listappend_growth` | the list-growth path, no patterns | ⛔ RED |
| `v05_treebank_pushlist_235` | treebank's own machinery, 5 lines of driver | ⛔ RED |

⭐ The controls are the point: an all-red ladder proves nothing about the instrument. These two say it discriminates.

## Transferable

- ⭐ **`OUTPUT =` instrumentation is not free in SNOBOL4.** Adding an inline `OUTPUT` line to `push_list` moved the error from 235 to 22 — the statement numbering and the deferred-call machinery are sensitive to it. A **helper function** called from the same site does not perturb it. Instrument by call, never by inserted statement.
- ⭐ **A "known red" name can hide its own class.** `demo_treebank` was carried for weeks as a treebank/VLIST-pattern issue with a `zd_plan` root cause; the actual defect is a four-line expression form with no pattern in it, and it is reachable from any program that writes `(A , B)`. The row name became the boundary of the search.
- ⭐ **A flag that changes the asm but not the answer is evidence, not a dead end.** `SCRIP_ZD_VLIST_OMEGA` firing-but-not-fixing is what proves the zd_plan framing incomplete; that is worth more than the flag working would have been.
