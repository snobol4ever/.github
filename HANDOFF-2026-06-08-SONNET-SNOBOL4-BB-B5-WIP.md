# HANDOFF — SNOBOL4-BB — B-ladder B5 WIP (Sonnet, 2026-06-08)

## TL;DR
- **Foundation recovered & verified.** Local `main` rebased onto **live** `origin/main = 4f2ae74` + cherry-picked **B4** (`706a5af`). B0–B4 GREEN: smoke 7/7, pat-rung 19/19 no-SKIP, corpus 154/280, beauty 1/17, fence OK.
- **B5 (`bb_pattern_unary_s`) wired + compiling, but RUNTIME-UNVERIFIED.** Committed `0642c99` on top of B4.
- **Nothing pushed to `main`.** Both commits live on branch **`snobol4-bladder-b5-wip`** (pushed to origin) — `main` is untouched and safe.
- **First action next session: run the B5 builder probe vs `sbl`, then the full gate battery.** Do NOT merge B5 to main until green.

## Repo-state history this session (important)
At clone time `origin/main = 6b4ff36` (Pascal PB-26 line) was missing B2/B3/B4. **A concurrent session moved `origin/main` to `4f2ae74` mid-session** (PB-27 + IRD-3c recovery `1d3b397` + FIX-7b), which **already restored B2 + B3** (`bb_pattern_lit/alt/stub`, `bb_dtp_assign`) — pat-rung is 19/19 on live `origin/main`. Only **B4 was still missing** from origin.

A full-branch merge of `snobol4-bladder-b2-b3-b4-restore` was dry-run and **rejected**: conflicts ONLY in the 3 Pascal grammar files (`pascal.y` + `.tab.c/.tab.h`, PB-26 vs older PB-24/25); the entire SNOBOL4 frontier merges clean. Chose the **cherry-pick** route instead (sidesteps Pascal entirely). Re-applied B4 (`8d796f8`) onto live `origin/main`; only conflict was the design-doc ladder-ticks (resolved to the accurate B2/B3/B4-ticked state).

## Git topology (as of handoff)
```
origin/main = 4f2ae74   PB-27   (LIVE, moving — concurrent session active; B2+B3 present, B4 NOT)
   └─ 706a5af  B4: UNARY_I protos (cherry-pick of 8d796f8; VERIFIED green)
        └─ 0642c99  B5 WIP UNVERIFIED: bb_pattern_unary_s
   → both on branch  snobol4-bladder-b5-wip  (pushed to origin)
```
B4's original commit is also safe at `8d796f8` on `snobol4-bladder-b2-b3-b4-restore`.

## B5 design (implemented in `0642c99`)
`src/emitter/BB_templates/bb_pattern_unary_s.cpp` — D6 builder, **precise parallel of B4's `bb_pattern_unary_i.cpp`**.
- **Universal layout HELD:** +0 cset_ptr · +8 saved-δ scratch · +16 out_γ · +24 out_ω · **β@+32** (so B6's `base = ω_site−24, β = ω_site+8` derivation stays valid).
- Operand at +0 is a **cset pointer** (null-terminated strtab string), filled exactly like `bb_pattern_lit`'s lit-ptr (`x86("lea","rcx","[rip + __]",us_addr(),us_label())` + `ins2 mov [rax],rcx`). Pool-cursor load uses `ins2 mov rax, qword ptr [rip + g_pat_pool_cur]` (B3 finding — the `[rip+__]` form emits `lea`, wrong for a value load).
- Matching = **inline call-free membership scan** (`us_scan_one`: loop cset bytes to NUL; no `strchr`, per call-free-proto rule). Leaves +8 free as the doc promised.
- **β one-shot → out_ω** for ANY/NOTANY/SPAN/BREAK. **BREAKX β re-generates** (restore saved-δ@+8, skip past the break char, rescan to next; out_ω only when no further break char).
- Entire proto body in `ins1`/`ins2` passthrough (mode-4 TEXT-only) — sidesteps the B2 silent-drop trap on `[r13+rax]` / `byte ptr` operand shapes.

### α/β semantics per primitive (per SPITBOL + sbl probes)
- **ANY**: δ<Δ ∧ subject[δ]∈cset → δ++, →γ; else →fail. β→ω.
- **NOTANY**: δ<Δ ∧ subject[δ]∉cset → δ++, →γ; else →fail. β→ω.
- **SPAN**: scan run of cset chars from δ; if ≥1 matched → δ=end, →γ; 0 matched → fail. β→ω.
- **BREAK**: scan run of NON-cset chars; stop before first cset char → δ=that pos, →γ; reach Δ with no break char → **fail** (standard SPITBOL). β→ω.
- **BREAKX**: like BREAK for α (save stop pos→+8); β skips past break char, rescans for next.

### Wiring touchpoints (all done in `0642c99`)
1. `emit_core.c` — 5 `bb_pattern_stub(...B5)` → `bb_pattern_unary_s()`.
2. `bb_templates.h` — `void bb_pattern_unary_s(void);`.
3. `Makefile` — source list + compile rule (link globs `$(OBJ)/*.o`).
4. `lower_sno.c` — `sno_pattern_buildable` extended (TT_SPAN/ANY/NOTANY/BREAK/BREAKX with TT_QLIT arg); `lower_pattern_build` cset arm → IR_PATTERN_* with `IR_LIT(n).sval`.
5. `emit_bb.c` — `walk_bb_flat` FILL ×5 (`op_kind` + `op_sval` + `bb_slot_alloc24`); `descr_chain_arity` ×5 → 0.

Build fix applied: `usl` widened from `const char *` to `const std::string &` (was passing `usl(p + "ml")`).

## SBL oracle targets (LOCKED — verify against these)
| pattern | subject | expect |
|---|---|---|
| `SPAN('ab')` | `aabbcc` | `aabb` |
| `ANY('abc')` | `cab` | `c` |
| `NOTANY('ab')` | `Xab` | `X` |
| `BREAK('X')` | `abcXdef` | `abc` |

NOTE: `BREAK('Q')` on a subject with no `Q` — probe was ambiguous (null-match vs match-fail indistinguishable in the probe). B5 implements **fail** (standard SPITBOL). Pin this against the corpus BREAK tests.

## EXACT NEXT STEPS
1. `git checkout snobol4-bladder-b5-wip` (or pull it), `bash scripts/build_scrip.sh && make libscrip_rt`.
2. **Run the B5 builder probe vs sbl** — builder path is `P = SPAN('ab'); 'aabbcc' ? P . X; OUTPUT = X` (pattern assigned to a var → routes through `lower_pattern_build` via `lower_sno.c:1105`). Use the `run_m4` recipe from `scripts/test_smoke_snobol4.sh` lines 18–22: `scrip --compile --target=x86 → as → gcc -no-pie -lscrip_rt → run`. Diff all five primitives against the table above.
3. If any mismatch: **objdump-verify the new operand shapes** (B2 silent-drop discipline) — though all are `ins2` passthrough so `as` already sees them verbatim; suspect logic (scan bounds, δ math) before encoding.
4. Full m4 battery: smoke 7/7, pat-rung 19/19 no-SKIP, corpus **≥154 non-decreasing**, beauty 1/17, fence HARD.
5. On GREEN: tick B5 in `SNOBOL4-5STAGE-OWNED-BUILD.md`; then integrate to `main`.

## Integration / merge guidance
- **B4 (`706a5af`) is verified-green and ready to merge to `main`.** The concurrent session may land its own B4 first — if so, drop this one (pull --rebase will conflict on the two B4s; `git rebase --skip` the B4 commit and keep only B5).
- **B5 merges to `main` only after step 4 is green.**
- Merge via `git pull --rebase origin main` then push (code repos first per RULES.md). `origin/main` is actively moving — re-fetch immediately before any push.

## Stale watermark (deferred — NOT touched, to avoid racing .github)
`GOAL-SNOBOL4-BB.md` watermark says `main=90f89bf` (stale; live `origin/main` is `4f2ae74`). Left untouched here because the concurrent session is actively editing shared `.github`. Fix it in whichever commit lands the B-ladder foundation on `main`.

## Open ladder (after B5)
B6 STITCH-CAT · B7 NULLARY · B8 CAPTURE · B9 ARBNO+FENCE(P) · B10 DEFER-IN-BUILD (*V/*E, true downstream-retreat re-entry) · B11 SEAL-FLIP. Open m4 bug clusters: M4-FENCE, M4-DATA, M4-DEFINE, M4-BUILTIN, M4-BEAUTY, M4-STARVAR.

— Sonnet, co-dev. GATES: MODE-4 ONLY (never --interp/--run).
