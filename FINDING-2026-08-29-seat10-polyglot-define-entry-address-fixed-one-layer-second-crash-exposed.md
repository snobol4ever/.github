# FINDING — seat10: polyglot DEFINE entry-address bug ROOT-CAUSED TO ITS EXACT SOURCE LINE AND FIXED — cures the documented RIP=0x0 crash, does NOT fully cure the row, a second layer is now exposed

**Date:** 2026-08-29 · **Seat:** seat10 (`/home/claude10`) · **Topic:** queue row `m3-passes-m4-fails-three-polyglot-demos` ("bug 2" in that row's own numbering, `polyglot-define-entry-address-wrong-in-merged-program`)
**Landed:** SCRIP `205f54b3` · **Status:** ONE LAYER FIXED, VERIFIED SAFE, ROW NOT DONE. Do not read this as closing the row — read §4 first.

## 0. Why this row could not be trusted at face value this session

Independently re-ran this row's own literal DONE-WHEN command fresh (pristine build, current HEAD) before touching anything: **it returns `OK`, and that is a false positive**, exactly as seat15's last session flagged. `demo04`/`demo09` no longer show the `m3 PASS && m4 FAIL` pattern the check looks for because an unrelated, separately-landed commit (`9ac81161`, `polyglot-main-selector-ignores-main-mod-registry`) exposed mode-3 to the same underlying defect — both demos now **crash in both modes** (confirmed via a full fresh gate run: `m3 PASS=3 FAIL=7`, `m4 PASS=3 FAIL=7`, `demo04`/`demo09` both `CRASH(sig=11)` in both arms). A demo failing both modes has had its witness destroyed, not cured — this row's own DONE-WHEN cannot currently distinguish "fixed" from "broken differently," and I am not calling `done`.

Also repaired, found stale again in the process: `scripts/test_gate_polyglot_demos.sh`'s `DEMO_DIR` (`corpus/scrip/` → `corpus/demo/scrip/`, a Lon-ordered move, `corpus` commit `23e65c0e`, that landed hours after seat15 had already fixed the identical drift the OTHER direction). This path has now round-tripped `demo/scrip → scrip → demo/scrip` within about a day; the gate's own comment now records the full history so nobody "fixes" it back blind a third time.

## 1. Root cause, localized to the exact instruction (ASM-DIFF-FIRST, per RULES)

Used hq_P's own documented minimal repro (SNOBOL4 `check(s)` `DEFINE` idiom + demo04's actual Prolog `main`, no Icon — reproduces the exact bug, per this row's LEDGER). Compiled it and `assign_driver.sno` (the standalone, working sibling) to mode-4 `.s` and compared the `DEFINE`-registration block directly:

```
repro2.s:3673:   lea  r9, [rip + n206_statement_begin_α]     <- WRONG: check_end's next call site
repro2.s:3683:   lea  rsi, [rip + check_α]                    <- CORRECT, 10 lines later, same function
```

Both instructions live in `bb_define_bind()` (`src/templates/bb/bb_define.cpp`). The first feeds `rt_define_site`'s `fn` argument (the address later read back by `bb_call_route_classify`/`rt_proc_call_open_slim` when something calls `check` through the registry); the second feeds `bb_ab_seal_alpha`'s own, independent "M4-ALPHA-SEAL" registration.

**Why they disagree:** the first computes its label from `g_emit.lbl_t0`, populated upstream in `emit.cpp` per `IR_DEFINE` role — several roles set it to "the label of the node that follows this one in program order" (`IR_LIT(nd->operands[1]).sval` for role 4, or via `sr3_gamma_label`-adjacent machinery for others). That equals the DEFINE'd proc's own entry **only when the body is textually the very next statement and node numbering is undisturbed** — true for every single-language SNOBOL4 program (confirmed: standalone builds emit the identical "next-statement-label" pattern and it is harmless there, because standalone's own call sites never read the registry — they emit a static `lea rax,[rip+check_α]; jmp rax` directly, bypassing `p->fn` entirely; this matches seat01's and seat15's own established finding, now confirmed at the source-line level rather than inferred from behavior). Polyglot merging renumbers nodes into one flat cross-language space, and node N+1 is no longer reliably "the next line of THIS section" — it can be the first call site instead, which is exactly what happened here (`n206_statement_begin` is `OUTPUT = check('racecar')`, the line immediately after `check_end`).

The second instruction (`bb_ab_seal_alpha`'s call, `bb_define.cpp:291`) has never shown this bug because it does not consult `lbl_t0` at all — it builds the label directly: `std::string(fname) + "_\xce\xb1"`. That pattern is unconditionally correct by construction, for every role, every language shape, standalone or merged.

## 2. Fix

`src/templates/bb/bb_define.cpp`, `bb_define_bind()`: the `rt_define_site` registration's label now uses the same direct construction, gated behind `SCRIP_DEFINE_FN_DIRECT_ALPHA` (default ON; `=0` reverts to the old `lbl_t0`-sourced value) per the INSTRUMENT LAWS' killswitch-polarity rule. Surgical: only replaces the label used in the branch that was already trusting `lbl_t0` non-null; the `lbl_t0 == NULL` stub-fallback path (`"rt_ab_undef_fn_stub"`, the `x86_load_got` arm) is untouched, and the branch condition deciding `lea` vs `load_got` is untouched.

## 3. Verified safe — measured, not assumed

`IR_DEFINE` is SNOBOL4-exclusive (`grep -l IR_DEFINE src/lower/lower_*.c` → only `lower_snobol4.c`; no `lower_snocone.c` exists at all, so Snocone shares SNOBOL4's lowerer and this code path too — checked, not assumed).

| witness | before | after |
|---|---|---|
| minimal repro (SNOBOL4+Prolog, no Icon), m3 | SIGSEGV, `RIP=0x0` (gdb-confirmed: jump through a null pointer, matching seat03's own historical finding exactly) | SIGSEGV, different site (§4) — the `RIP=0x0` crash is gone |
| minimal repro, m4 | SIGSEGV | SIGSEGV, same different-site shape as m3 |
| `assign_driver.sno` (the exact witness that disproved seat15's Option-1 attempt), m3+m4 | 7/7 PASS | 7/7 PASS, unchanged |
| full SNOBOL4 corpus gate (`test_corpus_snobol4.sh`), pristine build | — | **m3 PASS=1381 FAIL=0 · m4 PASS=1371 FAIL=0 SKIP=10 — zero regressions** |
| Snocone smoke | — | 5/5 PASS |

The corpus result is cleaner than Bug 1's own landed profile (which flipped `demo03`/`demo08` PASS→FAIL and was landed anyway, per hq_C's ruling that a false green is worse than a named regression) — this fix has no measured regression anywhere tested.

## 4. What is NOT fixed — read this before assuming the row is close to done

With the address now correct, the minimal repro and `demo04`/`demo09` **still crash, in both modes** — a different, previously-masked defect is now the sole visible cause. gdb on the m4 binary: crash inside `n204_define_bx` itself (the DEFINE statement's own registration/seal code), `RIP` a real code address (not null) this time, but the caller's own return address on the stack reads back as `0x0` — consistent with stack corruption or a calling-convention mismatch somewhere in the register-save/restore sequence around the `rt_define_site`/`bb_ab_seal_alpha` calls, not yet localized further. **Not chased this session** — this is squarely the next layer, same shape as every prior "fix one bug, surface the next" cycle on this row (Bug 1 → Bug 2 was the identical pattern).

This is also consistent with, and does not contradict, seat03's separate finding that `bb_call_route_classify` routes `check`'s call sites through `rt_proc_call_open_slim` (a name/cell-based dynamic dispatcher) instead of the static `check_α` trampoline, and that the two calling conventions are incompatible (`r9`-relative frame access vs. `pcells`/`NV_SET_fn` binding). Fixing the registered *address* does not fix *which dispatcher reaches it* — both defects can be, and evidently are, simultaneously real. Whoever picks this up next should not assume address-correctness alone reaches a passing state; the routing/calling-convention question seat03 raised (routed to hq_C, topic `polyglot-callroute-dynscope-vs-frame`, still unanswered as of this session — checked hq_C's inbox directly) is very likely still the governing blocker even with this fix in place.

## 5. For the next actor

- Do not re-derive §1's root cause — it is now nailed to the exact source line and instruction, with a byte-level before/after diff.
- The next concrete step is localizing §4's new crash: gdb with a breakpoint on `n204_define_bx`'s entry, single-step through the seal/registration sequence, and check the stack/return-address integrity at each `call` (`rt_define_site`, `bb_ab_seal_alpha`) — the corrupted frame #1 (`0x0`) suggests the return address itself is being clobbered, which would point at the `x86_scan_sync_out()`/`x86_scan_sync_in_rr()` register-save dance around those calls rather than at the calls themselves.
- `SCRIP_DEFINE_FN_DIRECT_ALPHA=0` reverts this fix instantly for A/B testing without a revert commit, if a future finding suggests it is implicated in the new crash (checked this session: the seal logic's own code, which the new crash sits inside, is byte-for-byte unchanged by this fix — but confirm rather than trust that reasoning if the new crash resists localization).
- Mailed hq_C (topic `polyglot-callroute-dynscope-vs-frame`, as an addendum to seat03/seat15's existing thread) with this finding, per this row's established practice of keeping the routed scope question current rather than opening a new one.
