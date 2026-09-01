# FINDING 2026-09-01 seat03 — the port-exit gate's OK_CALL arm asserted "DESCR-returning" without checking, and hid half the violation population

Row: `port-exit-value-contract-untagged-rax-forges-dt-fail`. Measured on a `make pristine` build at
SCRIP `14f384ed` (cure landed as **`b4e78819`**, hash read back from `origin/main`, not assumed),
corpus `e2f3496fd`, .github `e16b232e`, `RT_OPT=-O0`.

## THE DEFECT, IN THE INSTRUMENT RATHER THAN THE COMPILER

`port_exit_value_contract_scan.py` classified **every** `call` reaching a promotion site as safe:

```python
if CALL.match(ist):
    return ("OK_CALL","rax:rdx from a DESCR-returning call: %s" % ist[:60], n)
```

The verdict string states *"a DESCR-returning call"* — a cause the code never tested. Any `call` at all
satisfied it. This is `RULES.md`'s own instrument-law shape: **a signal reachable by two causes that names
only one**, and it sat inside the gate built to kill exactly that disease elsewhere.

## THE MEASUREMENT

Across the row's own six witness programs, all 10 `OK_CALL` transfers resolve to just three callees, and
their return types were read from source rather than inferred:

| callee | declared | returns `DESCR_t`? | count |
|---|---|---|---|
| `rt_relop_overload` | `int rt_relop_overload(DESCR_t, DESCR_t, int, DESCR_t *out)` — `arithmetic.c:58` | **no** — DESCR goes out through `*out` | 5 |
| `rt_jct_relop` | `int c_rt_jct_relop(DESCR_t, DESCR_t, int)` — `by_name_dispatch.c:4951` | **no** | 4 |
| `rt_assign_var` | `DESCR_t rt_assign_var(DESCR_t, DESCR_t)` — `core.h:425` | yes | 1 |

**9 of 10 were misclassified. RAW was 9; the true count is 18 — exactly half.**

## ⛔ WHY THIS WAS WORTH STOPPING FOR, RATHER THAN CURING THE 9 AND MOVING ON

The row's DONE-WHEN requires the gate GREEN. Curing the 9 `RAW` sites would have turned it green **with 9
contract violations still standing** — the precise *"fix the two known instances and leave a fourth
waiting"* outcome seat09 named and the DONE-WHEN was written to prevent. A cure built against 9 would have
been built against half its population, and the gate would have certified it.

## ⛔⛔ AND TWO OF THE HIDDEN SITES ARE GENUINELY FORGEABLE, NOT MERELY UNNORMALIZED

`rsg.icn:1195` (`-> define_γ`) and `:7401` (`-> source_γ`) arrive with the return of **`rt_scan_sync_in`**,
declared `uint64_t rt_scan_sync_in(void)` and returning `(uint64_t)(int64_t)(scan_pos - 1)`
(`gen_runtime.c:111`) — a raw scan position. **Scan position 105 gives low byte 104 = `DT_FAIL`.** That is a
live, data-dependent forged failure on the row's own axis, and the old gate reported both sites as OK.

The Pascal-witness pair is unnormalized but not currently forgeable, and saying so is part of the result:
`rt_relop_overload` returns only 0/1/2, so it cannot reach 104. It still breaks the contract — and note
`DT_SNUL = 0x00` and `DT_S = 0x02` are **valid tags** (`descr.h`), so `quick.s:1341` promotes `rax=0` as a
well-formed null-string DESCR with stale garbage in rdx: a silent wrong *value* rather than a spurious fail.

## THE REPAIR

The call arm is now an allow-list **derived from `src/` on every gate run**, never hand-maintained — a hand
list is only as correct as its last edit, and this gate exists so a cure need not depend on a census staying
complete. It is fail-closed: the scanner REFUSES (rc=2) when the list is missing, unreadable, or empty,
because a zero-symbol list would reclassify every call as a violation and read as a catastrophe.

**Proven in all three states before being quoted, both directions per RULES.md's TWO-PART PROOF:**
- **CAN SAY NO** — `FAIL(1) = 18` on the default witness set (was 9).
- **CAN SAY YES** — `PASS(0)`, rc=0, over 22 exits on `deal.icn` + `queens.icn`. (The half everyone skips.)
- **CANNOT-MEASURE** — `rc=2` on each of the three refusal arms: no flag, empty file, unreadable file.

## STATE OF THE ROW, PLAINLY

- The gate is **redder than before, and that is the correct direction** — the count was wrong, not the tree.
- **No cure attempted, and no codegen touched**: `x86_asm.h` and every template are untouched, so the
  shared-node control arms (SNOBOL4 blocking set, Icon pinned watermark) are not engaged and no `.s`
  artifacts are owed. The `zd_plan` precedent — cure Pascal, regress SNOBOL4, revert — is not in play here.
- **The cure is still open, and ruling (c) still stands.** What changed is its population (18, not 9) and
  its shape: the ruled generation-time check needs to know whether rax holds a tagged DESCR at a transfer,
  and `x86_port_hook` today tracks no register state at all — it carries per-box `_.op_*` fields and emits
  strings. Whoever builds it should price that in, and note `CLAUDE.md`'s ⛔ NO NEW GLOBAL VARIABLES rule
  before adding emitter state to carry it.
- **The promotion site the cure must touch is named, since the baton did not name it:**
  `src/templates/xa/xa_flat.cpp` — the `zf_pas_nest_graph()` epilogue-γ arm and the ICN-FR-2 zframe
  epilogue-γ arm, both of which emit `mov rdi, rax` / `mov rsi, rdx`.
