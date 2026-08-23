# FINDING 2026-08-23 seat01 — `free-r11` STEP 1: the remaining r11 (and r10) "scratch" in `bb_call_fn.cpp`/`xa_flat.cpp` was a live, default-on SEGFAULT — 100% of Prolog mode-3 was broken, not merely undocumented

**Row:** `free-r11` (`/home/resources/postoffice/tasks/free-r11.task.md`), locked by seat01. Continues the STEP 1 census two prior sessions (seat6, seat4/seat8) left open — seat6 measured real debt roughly double HQ's estimate and asked `q-free-r11` (still unanswered); seat8 twice found the row's DONE-marker did not match the code (`FINDING-2026-08-22-seat8-diag-regs-still-blocked-free-r11-closed-over-live-survivor.md`).

## 1. STARTING POINT — re-measured, not trusted

`git pull --rebase` on SCRIP/.github/corpus first (PULL-BEFORE-TRUST; local was 3/8/0 commits behind). Fresh `bash scripts/test_gate_wreg_claim.sh --strict` against current HEAD, not the 2026-08-22 docs:

| file | r10 | r11 | class per prior docs |
|---|---|---|---|
| `bb_call_fn.cpp` | 35 | 17 | "ordinary scratch... freely movable... no correctness risk today" |
| `xa_flat.cpp` | 0 | 1 | "Icon's own generator-suspend mechanism... out of scope" (for the ONE remaining site, this was wrong — see §3) |
| `bb_statement.cpp` | 1 (2 occ) | 0 | `diag-regs-stmt-and-bb` telemetry write itself — separate mechanism, correctly out of r11 scope |
| `emit.cpp` | — | 2 | licensed, pinned, rung E-5 (frameless-suspend cache) — untouched, see §6 |
| `x86_asm.h` | — | — | licensed but DRIFTED (pinned occ=16, live 23) — see §5 |

This is already far smaller than seat6's 248-occ/25-file estimate or seat8's 149-site/24-file measurement — most of that debt was cleared by intervening sessions (rung E-2 through E-6, `bb_define.cpp`'s r11 fully eradicated at `2e601a2e`) that this row's own prior briefs hadn't caught up to. The corrected number **is** the deliverable (HQ LAW 17) even before the rest of this FINDING.

## 2. THE BUG — not scratch, a register that was never set

Read `bb_call_fn.cpp` in full (596 lines). Every one of its remaining r10/r11 mentions lives inside the Prolog `$unify`/`$unify_lst`/`$trail_mark`/`$ix_g` inline fast-path helpers (`sink_trailpush`, `sink_tp_nc`, `sink_carve48`, `sink_carve48_take`, `sink_unify_lst_str`, `sink_trail_mark_str`, `sink_ix_g_str` — the "PL-SINK" family) and, in `xa_flat.cpp`, one Prolog zframe-epilogue arm (`PL-FR-4`). In every single site, the pattern is:

```
x86("lea", "r12", "[rip + __]", ..., "g_pl_trail")   // or g_hp_fr / g_plw_cellws_on / g_zeta_mode / g_plw_dot_sl / g_pl_zf_pending_cursor
x86("mov", "rdi", "[r10 + 0]")                        // or "eax","[r10 + N]" -- reads through r10/r11 instead of r12/rdi
```

**Nothing anywhere in the file, or in the rest of `src/`, ever writes a meaningful pointer into r10 or r11 at these points.** Exhaustive grep for every `mov`/`lea`/`pop` destination spelling of r10/r11 (including `r10d`/`r11d` sub-registers) across all of `src/` turns up exactly three setters, none of them this code: the licensed `diag-regs` telemetry write (`x86_asm.h:2013`, `r11 = _.nid`), the licensed `SCRIP_ZSM` diagnostic save/restore (`x86_asm.h:2061/2069`), and the RTCC self-restore idiom (`x86_asm.h:399-409`, which loads r10/r11 from a runtime-block slot that is documented as "currently always 0"). None of the three is what these Prolog sinks intended.

This reads as "harmless arbitrary scratch" for exactly as long as nothing else happens to leave a meaningful value in r10/r11 at that point in the box's straight-line code — which was true until this session, because r10/r11 sat genuinely idle there. It stopped being harmless the moment `diag-regs-stmt-and-bb` landed (`c951f257`, `53819b4a`, both dated **today**, 2026-08-23): `x86_diag_regs_on()` defaults **ON** (`SCRIP_DIAG_REGS` must be explicitly set to `0` to disable it), so every box's α/β port now writes `r11 = this box's BB node id` and the RTCC veneer now protects r10/r11 across every runtime call (i.e. actively preserves whatever garbage is there instead of letting an unrelated call clobber it away). The result: `corpus/programs/prolog/rung06_lists_lists.pl` — `append([a,b],[c,d],L), length(...), reverse(...)`, no edge cases — **SEGFAULTs on every run, both modes, on pristine `origin/main`, deterministically.**

```
$ ./scrip corpus/programs/prolog/rung06_lists_lists.pl < /dev/null   # pristine tree, 3 runs
Segmentation fault (139) / 139 / 139
```

The row's own brief named the exact precedent for this shape (`FINDING-2026-08-20-s194b`/`s194c`, the RTCC-bank/old-wire collision that cost Milestone 1 once) and its own blocking clause ("a half-freed register is the s194 collision") — this is that collision, live in production, not hypothetical.

## 3. `xa_flat.cpp` — same defect, one site, previously mis-filed

`ARCH-SNOBOL4-RTX.md` §2 excuses `xa_flat.cpp`'s r11 mentions wholesale as "Icon's own generator-suspend continuation... out of scope for both rows." That's correct for `rt_gen_save_wires`/`rt_gen_get_gamma_wire`/`rt_gen_get_omega_wire` (the `icn_zframe_gen` arm), but the ONE r11 site actually remaining today is a **different, Prolog-only** arm (`zframe_graph && !icn_zframe_gen`, tagged `PL-FR-4` — the same tag as one of the `bb_call_fn.cpp` sites, confirming common authorship/session): `lea r12,[rip+g_pl_zf_pending_cursor]` immediately followed by `mov r12,[r11]` — should be `mov r12,[r12]`. Identical defect, identical fix.

## 4. FIX AND VERIFICATION

**Fix:** `sed -i 's/\[r11/[rdi/g'` then, separately, `sed -i 's/\[r10/[r12/g'`, each scoped to `bb_call_fn.cpp` alone after manual per-site tracing confirmed every occurrence in the file was this exact pattern (verified individually, not assumed from the sed's success — see the register-threading trace in the session transcript: each block's `r12`/`rdi` value is fresh from an immediately-preceding `lea`/`mov`, no site reads a stale generation). `xa_flat.cpp` got one hand edit (`[r11]` → `[r12]`). Struct-offset assumptions for `g_pl_trail`/`g_hp_fr` (fields at +0/+24/+32) were cross-checked against the live definitions — `pl_trail_t = {pl_area_t area; int top;}`, `pl_area_t = {char*base; char*top; char*limit; size_t cap;}` in `src/parser/prolog/pl_cell.h` / `pl_area.h` — confirming offset 0=base, 24=cap, 32=top(count), not merely inferred from usage.

**Verification, by-file:**

| suite | pristine `origin/main` | +r11 fix only | +r10 fix (final) |
|---|---|---|---|
| Prolog mode-3 (`test_prolog_rung_suite.sh --mode run`, 164 progs) | **PASS=0 FAIL=164** | PASS=98 FAIL=66 | **PASS=101 FAIL=63** |
| SNOBOL4 corpus (`test_corpus_snobol4.sh`) | 359/1 (m3), 359/1 (m4) | 359/1, 359/1 | 359/1, 359/1 — **unchanged** |
| Icon smoke (`test_smoke_icon.sh`) | 14/14 both modes | 14/14 | 14/14 — **unchanged** |

Every PASS/FAIL delta at every stage was diffed by program name: **zero regressions anywhere, every change a clean FAIL→PASS.** SNOBOL4/Icon are untouched by construction — every edited line sits inside a Prolog-builtin-name-gated branch (`$unify`/`$unify_lst`/`$trail_mark`/`$ix_g`) or a `zframe_graph && !icn_zframe_gen` guard neither language's lowerer ever produces. `make pristine` EXIT=0 (this session's own final build). `test_gate_emit_no_lang.sh` and `test_gate_template_medium_invisible.sh` both green before and after.

**Mode-4 (`--compile`) is improved but not clean.** Pristine mode-4 was also 0/164 (same collision, compiled form). Post-fix, `rung06_lists_lists.pl` now compiles, links, and runs much further before crashing — see §6 for the different bug it now hits. The mode-4 suite total was not re-measured program-by-program after the r10 fix (mode-3 was prioritized as the primary native mode per the corpus scripts' own convention); a future session should re-run `--mode compile` for the full picture.

## 5. THE CENSUS TABLE, BEFORE/AFTER

Matching the task's own DONE-WHEN glob (`src/templates/*.cpp src/emitter/*.cpp`, r11 only):

| file | r11 before | r11 after | class |
|---|---|---|---|
| `bb_call_fn.cpp` | 17 | **0** | was mis-filed "scratch," was actually BUG — fixed |
| `xa_flat.cpp` | 1 | **0** | was mis-filed "Icon mechanism," was actually BUG — fixed |
| `emit.cpp` | 2 | 2 (unchanged) | genuine claim, licensed, rung E-5 — untouched, see §6 |
| all other `src/templates/*.cpp`, `src/emitter/*.cpp` | 0 | 0 | already clear (prior rungs) |
| **TOTAL** | **20** | **2** | |

r10 in `bb_call_fn.cpp` (a `free-r10` row concern, folded in here per `DISPATCH-R10-R11-ERADICATION.md`'s explicit "expect to merge, same files" authorization, since it was the literal same bug): 35 → **0**.

The task brief's own three-way CLASS split (dead wire / scratch / genuine claim) needed a fourth bucket that neither this brief nor `ARCH-SNOBOL4-RTX.md` had a name for: **register never set** — syntactically indistinguishable from scratch (a bare register mention with no wire semantics) but not movable by liveness review the way real scratch is, because there was no live value to preserve in the first place; the fix is "read the register that actually holds the address," not "pick a different free register."

## 6. TWO ITEMS FLAGGED, NOT FIXED, NOT THIS ROW'S SCOPE

1. **`emit.cpp`'s frameless jmp-entry pattern-blob suspend cache (2 r11 sites, `:2776`/`:3084` this session's line numbers) is untouched.** This is the one item every session since 2026-08-22 (seat3, seat4, seat8, this session) has independently flagged as a genuine architectural claim needing "real design/testing work, not a mechanical cleanup" — retargeting it to read `[rsp]` directly at the suspend point instead of caching in r10/r11 across an unenforced span of intervening box code. It is why this row's own mechanical DONE-WHEN command (`grep -q` zero) cannot pass and should not be weakened to pass — the prose criterion ("every remaining runtime use is named in the register contract as a deliberate claim") is satisfied; the literal-zero command is not, by design.
2. **A different, unrelated crash, newly reachable now that execution gets this far:** with both fixes applied, `rung06_lists_lists.pl` in mode-4 (and several deeper mode-3 rungs) SEGVs inside `pl_trail_unwind` (`pl_cell.h:81`) with a garbage `mark` (observed `-7936`), via `rt_pl_dop_unwind_nothrow → dop_unwind_nothrow → pl_trail_unwind`. The backtrace contains no r10/r11 register at all — confirmed by `gdb` register dump at the fault. This is a Prolog runtime/lowering correctness defect (something computes or threads the trail "mark" value incorrectly), unreachable before this fix simply because nothing got this far. Belongs to `GOAL-PROLOG-100.md`, not this row.
   ⛔ **THIS BUG IS ASLR/RUN-TO-RUN NON-DETERMINISTIC, MEASURED:** `rung06_lists_lists.pl` alone, run standalone 5× back to back on the identical post-rebase binary, gave 3 PASS / 2 SEGV. **The full 164-program suite is far more stable than that one witness suggests** — run twice in immediate succession it landed on the exact same **101/164** both times, with only `rung15_abolish_abolish_existing` and `rung15_abolish_abolish_then_query_fail` (one family) trading places (one PASS↔FAIL swap each, net zero). `101/164` is a solid number to cite, not a lucky draw — but treat any single standalone re-run of a borderline program as unreliable evidence on its own. This is the same instability class §7's `160_pat_alt_inner_gen_resume` names for SNOBOL4 (`ARCH-SNOBOL4-RTX.md` §7 step 3), now confirmed present in Prolog too, and it is a symptom of the `pl_trail_unwind` defect (or a sibling uninitialized-read in the same family), not of anything this row touched.

## 7. REGISTRY DRIFT FOUND (not caused, not re-pinned here)

`scripts/wreg_claim_registry.txt`'s `x86_asm.h` pin (`occ=16`) is stale against the live count (**23**, confirmed by `test_gate_wreg_claim.sh --strict` reporting `GATE: FAIL` / DRIFT) — both new occurrences trace to `c951f257` (the diag-regs write, `x86_asm.h:2013`) and `53819b4a` (RTCC-veneer protection of r10/r11, `:380-409`), both legitimate growth of the new claim landing after seat06's rung-E6 pin, not sweep debt. Separately, `bb_define.cpp`'s registry entry (`occ=4`, "ALL EIGHT non-rax caller-saved GPRs … r10 r11 …") no longer describes the code: the monitor-save site's actual push/pop set today is `{rdi×2, rsi, rdx, rcx, r8, r9, r12}` — zero r10/r11 — confirmed by direct read and by this session's own fresh grep (0 hits). `bb_define.cpp` was not touched this session; whoever last edited that site (after `2e601a2e`, uncommitted-message-visible) didn't update the registry prose. Neither drift blocked this row's own DONE-WHEN (`x86_asm.h` is a `.h`, outside the `*.cpp` glob; `bb_define.cpp`'s live count is already the correct 0) but both need re-pinning by whoever next owns the registry.

## 8. THE PRECONDITION GAP, FOR HQ

`DISPATCH-R10-R11-ERADICATION.md` states the new r10/r11 claim goes live only after eradication reaches true zero, gated by `WREG_CLAIM_LIVE` staying `0` until then. **That flag has no runtime effect.** The code that actually executes is gated by `SCRIP_DIAG_REGS` alone (`x86_asm.h:1925`, default ON), and it shipped default-ON in the same commits that wrote it, independent of `WREG_CLAIM_LIVE`'s state and independent of how much of the eradication ladder had landed. This is exactly how a stated, unanimous, twice-reaffirmed precondition ("free' is the precondition, not a policy... not negotiable") was violated without anyone deciding to violate it — the enforcement mechanism named in prose does not exist in code. Recommend HQ decide whether `SCRIP_DIAG_REGS` should default OFF until the ladder's remaining surface (RTX hand-asm, 297 occurrences across 11 `.S` files, entirely unaudited by this session) is swept, or whether some other structural gate is warranted. Not decided here — this is a flag for a ruling, not a unilateral change to a product-wide diagnostic default.

## 9. WHAT THIS SESSION DID AND DID NOT DO

- Fixed: `bb_call_fn.cpp` (17 r11 + 35 r10 sites), `xa_flat.cpp` (1 r11 site). Both files rebuilt, tested, `make pristine` clean.
- Amended `ARCH-SNOBOL4-RTX.md` §2 in the same-session commit (register-contract rungs amend the contract with the code, per RULES.md).
- Did NOT touch `emit.cpp` (rung E-5, deliberately deferred, see §6).
- Did NOT touch the RTX hand-asm `.S` files (225-297 occurrences, a separate, larger, unaudited rung set per `DISPATCH-R10-R11-ERADICATION.md`'s own A-1..A-4 rungs).
- Did NOT re-pin the `x86_asm.h`/`bb_define.cpp` registry drift (§7) — flagged with full cause, not fixed, since re-pinning without owning the surrounding rung risks masking future drift under a stale justification.
- Did NOT chase the `pl_trail_unwind` bug (§6.2) — confirmed unrelated to r10/r11 by direct backtrace inspection, flagged for `GOAL-PROLOG-100.md`.
- Did NOT flip `SCRIP_DIAG_REGS`'s default (§8) — flagged for an explicit HQ/Lon ruling, not a unilateral call.
