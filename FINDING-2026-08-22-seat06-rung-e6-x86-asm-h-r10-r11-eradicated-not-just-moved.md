# FINDING seat06 — RUNG E-6 (`x86_asm.h`) LANDED: r10/r11's GENUINE RUNTIME USES ARE ELIMINATED, NOT RETARGETED; 16 SURVIVORS ARE TWO DOCUMENTED, UNAVOIDABLE CLASSES

**Session:** seat06 (`/home/claude06`, Claude Sonnet 5) · **Date:** 2026-08-22 · dispatched directly by HQ mid-session (`RE rung-E6-x86-asm-h`), per `.github/DISPATCH-R10-R11-ERADICATION.md`
**Tree:** SCRIP (pre-edit `b007a116`) → this session's commit, pristine-built and gated at each step · `.github` amended in the same commit set per RULES.md
**Scope:** `src/templates/x86_asm.h` ONLY, as dispatched. No other file's r10/r11 debt was touched.

---

## 1. HEADLINE

x86_asm.h had **22 occurrences** of r10/r11 (10 r10 + 12 r11, 14 lines) before this session. **16 remain** (8+8, 8 lines) — but the reduction understates the work: **6 of the 6 eliminated occurrences were real runtime register uses, fully deleted (not moved to another register)**, because the call-stub mechanism that needed r10 in the first place was itself redesigned to need no dedicated scratch register at all. The 16 survivors are not scratch debt — they are two structurally-necessary classes (infrastructure vocabulary, and register-content-agnostic diagnostic save/restore), documented and registered per the same precedent `bb_define.cpp` already established for E-4.

## 2. WHAT WAS RETARGETED, AND WHY EACH ONE IS SAFE

All four sites below share one safety argument: **the register they now use is never a live SysV argument or a value the caller expects to survive a call**, and every one is verified against real call sites, not assumed.

| site | before | after | why safe |
|---|---|---|---|
| `x86_rtcc_call`/`x86_rtcc_call_descr`/`x86_rtcc_call_descr_ops` BINARY call-stub | `movabs r10,ptr; call r10` (self-inflicted clobber — `m \|= RTCC_C_R10` existed only to protect against this) | `movabs rax,ptr; call rax` (byte-identical to the ALREADY-SHIPPED `x86_call_ro`, i.e. an existing, proven pattern, not a new one) | rax is never a SysV argument register and is dead-by-convention immediately before any non-variadic call; the veneer's own `wb`/`rl` sequences that also touch rax do so either strictly BEFORE (writeback) or strictly AFTER (reload) this point, never overlapping it |
| `x86_call_dc` (DEFINE-shim call-through-cell, `DIES-WITH-W-5` tagged) | `movabs r11,slot; call [r11]` | `movabs rax,slot; call [rax]` | verified against both real call sites (`bb_call_proc_staged.cpp:366,581`): the immediately preceding code loads only the call's actual arguments into `detN_argreg[i]`, never rax |
| `x86_rtcc_rl_bin`'s OWN temp base pointer for R8(ANCHOR)/R9(GVA) reload | `movabs r11,block` then `[r11+40]`/`[r11+48]` — **UNCONDITIONAL, every RTCC call needing ANCHOR/GVA protection paid this, regardless of the R10/R11 conditionals** | `movabs rcx,block` then `[rcx+40]`/`[rcx+48]` | rax/rdx hold the just-returned call result at this exact point (cannot reuse); r8/r9 are the reload destinations themselves (cannot be their own base without extra care this rewrite avoids needing); rcx is dead post-call by pure SysV convention and untouched by the `cap` step that follows in the `_descr` variants |
| `rtcc_anchor_cmp`'s `!RTCC_GLOBAL_R8_ANCHOR` binary arm | `movabs r11,anchor_addr; mov r8,[r11]; cmp rax,0` | `movabs rcx,anchor_addr; mov r8,[rcx]; cmp rax,0` | **dead code** — `RTCC_GLOBAL_R8_ANCHOR` is `#define`d `1` unconditionally (`rtcc.h:24`), so this arm never executes today; fixed anyway for completeness since it is a genuine (if inert) r11 site the gate's own textual regex cannot see (raw bytes, no "r11" string literal — a blind spot shared with every other BINARY-only hand-encoded site in this file). Zero behavior change; not chasing the pre-existing `mov r8,...`/`cmp rax,...` register mismatch in that dead arm — out of scope, not a register-eradication question. |

**Deleted outright, not merely made conditional-false:** `RTCC_C_R10`/`RTCC_C_R11` `#define`s, `x86_rtcc_wire_bank()`, `x86_rtcc_nowire()`, and every R10/R11 conditional branch in `x86_rtcc_wb_bin`/`rl_bin`/`wb_text`/`rl_text` (8 lines). `x86_rtcc_clob`'s table literalizes its four R10-tagged entries (`rt_cap_match_begin`, `rt_cap_pop`, `rt_cap_top`, `rt_match_ctx_restore` → `0`; `rt_cmp_d` → `RTCC_C_R8|RTCC_C_R9`) to their **already-effective** value — `x86_rtcc_nowire()` was unconditionally stripping the R10 bit by default even before this session (confirmed by hand-tracing `x86_rtcc_nowire(m) = m & (~(R10|R11) | wire_bank())` with `wire_bank()=0` under the default, unset `SCRIP_RTCC_BANK_WIRES`), so this is a **provable no-op**, not a behavior change disguised as cleanup. A `static_assert` message illustrating the reload address (`x86_asm.h:334`) was updated from `[r11+48]` to `[rcx+48]` to stay factually accurate against the new code, not merely reworded to dodge the grep.

## 3. THE 16 SURVIVORS — TWO CLASSES, NEITHER A REGISTER USE

**(5) Infrastructure, 12 occ** (`x86_rnum()` decoder :47-48,:58 · `regs[]`/r10d,r11d/r10b,r11b encode tables :1194-1196): the encoder's own generic register-name↔number vocabulary. Cannot reach zero without breaking the encoder's ability to ever emit an instruction naming r10/r11 by string — needed both by any not-yet-swept caller elsewhere in the tree during the rest of this ladder, **and by `diag-regs-stmt-and-bb` itself**, which will need exactly this vocabulary to emit its own r10=STMT/r11=BBID writes once that rung lands. This is the same class Lon delegated at s36c under the OLD (now-retired) WREG claim; the reasoning — a lookup table is not a register *use* — is claim-agnostic and re-affirmed here under the new one.

**(6) NEW — diagnostic register-content-agnostic save/restore, 4 occ** (`x86_zsm_ev` :2001,:2009, gated `SCRIP_ZSM`, default off): pushes every potentially-live GPR including r10/r11 before a diagnostic probe call (`rt_zdp_ev`) and pops them in exact reverse order. It never assigns r10/r11 any meaning — it transparently *preserves* whatever the caller already had, which is exactly the property the future r10=STMT/r11=BBID claim needs from anything running alongside it. This generalizes `bb_define.cpp:138-145`'s pre-existing single-instance monitor-save pair (E-4's license) into a named class, since x86_asm.h turned out to hold a second, independent instance of the identical shape.

`grep -rEc '\br1[01][dwb]?\b' src/templates/x86_asm.h` = 16, both classes fully accounted for, zero unexplained. Both classes are documented in `scripts/wreg_claim_registry.txt` (pin `occ=16`, matching the live count exactly) and in `ARCH-SNOBOL4-RTX.md` §2 (amended same commit, per RULES.md).

## 4. emit.cpp REGISTRY TASK (bookkeeping only — file untouched, out of E-6's scope)

HQ's dispatch also asked to "re-point its registry at r10=STMT/r11=BBID and re-pin the drifted counts (emit.cpp pinned occ=6, now 16)." Fresh measurement: `grep -rEc '\br1[01][dwb]?\b' src/emitter/emit.cpp` = **7**, matching the CURRENT pin exactly — **zero drift**, not 16. Per HQ LAW 17 this correction is reported, not silently absorbed. The registry entry's justification was re-pointed at the current r10=STMT/r11=BBID framing (additively — the existing accurate prose was not rewritten), without touching `emit.cpp`'s own code, which stays E-5's territory.

## 5. REGRESSION — AND A METHODOLOGY CORRECTION ALONG THE WAY

⛔ **My own first-pass baseline was misleading, and I am flagging my own number rather than letting it stand.** Pre-edit, one crosscheck run read `m3 320/323 · m4 319/323+1skip`, with three failures: the already-documented-nondeterministic `160_pat_alt_inner_gen_resume`, plus `184_pat_cond_assign_defer_double_fire` and `185_pat_cond_assign_defer_seq_minimal`. Post-edit, both consistently read `322/323` (only `160` failing). Before writing that up as "my fix improved two tests," I checked whether it was real: **`.s` (TEXT/mode-4) output is proven byte-identical before/after this change** (`util_regen_crosscheck_s_artifacts.sh`: 490 programs, `changed=0`; this edit only touches BINARY-medium bytes and dead code — TEXT mode's call sequence was always `call sym@PLT`, never touching r10 in the first place). Since m4's PASS count could not possibly change from provably-unchanged `.s` bytes, I reverted (`git stash`), rebuilt the **unmodified** tree, and re-ran: it *also* reads `322/323`, 184/185 passing. **`184`/`185` are flaky, unrelated to this change** — my original baseline simply drew their failing state on that one run. Confirmed stable at `322/323` across three total runs post-edit and one pre-edit-tree control run. **Net regression verdict: exactly neutral** — this change neither breaks nor fixes anything in the crosscheck suite; the only standing failure is the pre-existing, separately-documented `160` non-determinism.

Gates: `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh` unaffected (8 pre-existing `xa_flat.cpp` sites, not this rung's) · `test_gate_wreg_claim.sh` shows `x86_asm.h` and `emit.cpp` both cleanly pinned, zero drift (the overall `--strict` gate still fails on the OTHER ~13 unfinished rungs' files — expected, not mine to clear) · `test_gate_wreg_claim_binary.sh` clean (`r10/r11-shape-checks=0`). `make pristine` EXIT=0, verified fresh at every rebuild this session.

## 6. NOT DONE, NAMED RATHER THAN SILENTLY SKIPPED

- **Beauty self-host was NOT used as a gate for this rung** — its mode-3 fixed point is independently, currently broken on a pristine tree unrelated to this change (see `FINDING-2026-08-22-seat06-beauty-m3-self-host-currently-diffs-from-oracle-not-fixed-point.md`, flagged separately, not chased here).
- **`rtcc_anchor_cmp`'s pre-existing `mov r8,[...]` / `cmp rax,0` register mismatch** (§2 table, last row) is left exactly as found — it predates this session, the arm is unreachable, and "is this dead branch's own logic correct" is a different question than register eradication.
- Only `x86_asm.h` was touched. The other 13 rungs in `DISPATCH-R10-R11-ERADICATION.md` (E-1 through E-5, A-1 through A-4, plus the still-blocked `diag-regs-stmt-and-bb`) are unaffected and unclaimed by this session.

## 7. FILES CHANGED

`src/templates/x86_asm.h` (net −20 lines: −61/+41) · `scripts/wreg_claim_registry.txt` (+19/−2, documentation only) · `.github/ARCH-SNOBOL4-RTX.md` (amended §2, same commit set, per RULES.md's register-contract rule).
