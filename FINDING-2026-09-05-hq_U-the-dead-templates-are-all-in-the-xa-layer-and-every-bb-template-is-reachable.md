# FINDING — STEP 0 and the reachability census: every `bb_*` template is reachable, and the dead code is a 12-file block in the XA layer

**Seat:** hq_U (HQ-UNIFY) · **Date:** 2026-09-05 · **Mode:** OCTET · **Row:** `bb-fixup-az-cleanup` (rank 1, claimed)
**Tree:** SCRIP `bba73d438` · corpus `67271a687` · `.github` `ef8c6e25` · `RT_OPT=-O0`

## 1. STEP 0 — the fresh scan, which is the only target list

    bash scripts/audit_bb_fixup_rank.sh
    FILES: 151 total / 65 dirty / 86 clean
    GRAND TOTAL violations: 1467
    GATE FAIL(1) [audit_bb_fixup_rank]: 65 template file(s) need fixup (examined 151)

⚠️ The ceo's STEP 0 at 13:28 today read **1446**; it is **1467** now. The ring is dirtying faster than
it is being cleaned, on the same day, and the row has not been worked in between. Descending order:
`bb_call_proc_staged` 397 · `bb_define` 219 · `bb_call` 205 · `xa_flat` 184 · `bb_match_arbno` 76
(STRUCT-BLOCKED, excluded) · `bb_call_fn` 30 · `bb_match_end` 27 · `bb_match_defer` 26 · then a long tail.

## 2. ⛔ THE ROW'S WORKING HYPOTHESIS IS WRONG, AND MEASURING IT WAS THE POINT

The row was minted with a lead: *"first read by symbol: 7 stems unreferenced outside their file, glue/main
certainly reached by other names — a lead, not a verdict."* Graded properly, **that lead does not survive**:

| layer | files | verdict |
|---|---|---|
| `src/templates/bb/` | **134** | **134 reachable. ZERO dead.** |
| dispatched IR opcodes | **122 distinct** | **122 produced by a lowerer/parser. ZERO never-produced.** |
| `src/templates/xa/` | 17 | **12 entirely unreachable** |

**The dead code is not scattered through `bb_*`. It is a contiguous block in the XA layer**, and a
census that had gone looking file-by-file through 134 `bb_*` templates would have found nothing and
concluded the tree was clean.

## 3. THE DISCRIMINATOR — and why `nm` and grep both say "reachable"

The ceo's instruction was to grade by what reaches the emitted `.s`, not by `nm`. Here is the mechanism
that makes the cheaper instruments lie, stated so it is reusable:

    void xa_dispatch(XA_op_t op) { switch (op) { case XA_FILE_HEADER: xa_file_header(); return; ... } }

`xa_file_header` **is** referenced — by its own `case` line. `nm` finds the symbol; grep finds a caller;
the linker keeps it; the Makefile lists it; the build is clean. Every static instrument reports it live.

    grep -rn '\bxa_dispatch\b' src/   ->  THREE call sites, all with literal opcodes:
        emit.cpp:459   xa_dispatch(XA_STRTAB_RODATA)
        emit.cpp:509   xa_dispatch(XA_CSETTAB_RODATA)
        emit.cpp:3479  xa_dispatch(XA_FLAT_DATA_SECTION)

**The switch has 27 arms and exactly 3 can ever be selected.** ⭐ **The right question is not "is this
symbol referenced" but "is its OPCODE ever PRODUCED"** — a grep that returns *producers*, not one that
returns *mentions*. hq_P stated the rule after their routed design named a dead destination: *a routed
design must name its destination by a grep that returns callers, not by a file and line the author read.*
This is that rule turned into a census.

⭐ And the confirming instrument is emission, exactly as the ceo said: I patched `xa_file_header.cpp`
earlier today for the `--compat` cure, built cleanly, and the emitted `.s` contained **not one byte** of
the change. **A patch into dead code is byte-for-byte indistinguishable from a working one at every stage
before emission.**

## 4. The 12 unreachable XA files — 243 lines total

`xa_bb_macro_library` (58) · `xa_bb_ptr_slot` (19) · `xa_cap_fixup` (22) · `xa_epilogue` (10) ·
`xa_exec_stmt_blob` (7) · `xa_expression_registry` (20) · `xa_file_header` (24, holds both
`xa_file_header` and `xa_file_footer`) · `xa_js_label_register` (16) · `xa_macro_library` (22, both
open/close) · `xa_pattern_blobs` (14) · `xa_prologue` (10) · `xa_wasm_main` (21, both open/close).

Three further entry points are unreachable *inside* otherwise-live `xa_flat.cpp`: `rt_pl_choice_open`,
`rt_pl_quad_seed`, `xa_entry_dispatch`.

Live and dispatched: `xa_strtab_rodata`, `xa_csettab_rodata`, `xa_flat_data_section`. The rest of
`xa_flat.cpp` is live by direct call, not through the dispatcher.

## 5. ⛔⛔ UNREACHABLE IS NOT DELETABLE — do not run the row's delete step over this list

The row says *"each unreachable template deleted in its own named commit."* **That must not be applied
mechanically to the list above.** Lon ruled 2026-08-28 that porting to JVM, .NET, JavaScript and
WebAssembly **IS the plan**; the digest's own note is that *a GOAL file full of unbuilt port design is
unbuilt, not abandoned*. At least `xa_wasm_main` (open/close) and `xa_js_label_register` are scaffolding
for exactly those targets — `--target=` accepts `x86|jvm|js|wasm` and the non-x86 arms stub out **today**.
Deleting them converts "not built yet" into "was deleted", silently, in a commit that would read as
hygiene.

⭐ **The general form, and it is the finding I would keep if I could keep only one: DEAD CODE AND UNBUILT
CODE ARE BYTE-IDENTICAL TO EVERY REACHABILITY INSTRUMENT.** Both are unreferenced; both compile; both
emit nothing. The difference is not in the tree, it is in a ruling — and no census can see it. So the
census's honest output is a list plus a **classification question for Lon or the ceo**, never a delete
list. I am not deleting any of the twelve, and the row's second half should be re-scoped to say so.

**Recommended split for the twelve:** (a) *port scaffolding, KEEP* — `xa_wasm_main`,
`xa_js_label_register`; (b) *needs a ruling* — `xa_macro_library`, `xa_prologue`, `xa_epilogue`,
`xa_bb_macro_library`, `xa_exec_stmt_blob` (these read as retired mode-1/2 machinery, and modes 1 and 2
are deleted, but "reads as" is not a measurement); (c) *safe to retire on the ceo's word* —
`xa_file_header`/`xa_file_footer`, whose only claim to life was the dispatch arm and which I have proven
emits nothing.

## 6. What is NOT done

The A–Z cleaning itself. STEP 0 is recorded and the census is complete; **no template was cleaned this
window and no file was deleted.** The next actor takes `bb_define.cpp` (219) as the largest eligible
target — `bb_call_proc_staged` (397) is the `bb_call` family the row excludes as FIX-3-gated, and hq_C
has a PARKED-ENGINE-OWED row (rung-12 WAM `switch_on_term`) landing in its clause-dispatch chunk.
