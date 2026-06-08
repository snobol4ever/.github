# HANDOFF — SNOBOL4-BB — B5 UNARY_S LANDED ON MAIN (Opus 4.8, 2026-06-08, attended)

## TL;DR
- **B5 verified vs sbl and LANDED ON MAIN.** `origin/main = 26cec68`. B0–B5 all on main.
- **The ORIGIN-REWRITE INCIDENT is RESOLVED** — the prior session's `snobol4-bladder-b5-wip` branch was rebased onto live `origin/main` **conflict-free** and fast-forwarded in. **No force-push of main, no history rewrite.**
- **Gates GREEN on the landed tree:** smoke 7/7 · pat-rung 19/19 no-SKIP · corpus **155**/280 (floor 154, +1) · beauty 1/17 · fence HARD.
- **NEXT: B6 STITCH-CAT** (`P = 'a' LEN(2)` — nearest-left-resume β wiring).

## What landed
`src/emitter/BB_templates/bb_pattern_unary_s.cpp` (B5 builder, was committed WIP-UNVERIFIED by the prior Sonnet session, now **runtime-verified**). The full B-ladder foundation (B4 `bb_pattern_unary_i.cpp` + B5 `bb_pattern_unary_s.cpp` + verification) moved from the holding-pen branch onto `main`.

Commits now on `main` (linear, on top of `642bec7`):
```
26cec68  B5 VERIFIED: bb_pattern_unary_s green vs sbl oracle
d432c0b  B5 WIP (bb_pattern_unary_s wired)
7296218  B4: UNARY_I protos
642bec7  (prior origin/main — Pascal session 31)
```

## How the merge was done (record, in case it matters for the workflow ruling)
1. `snobol4-bladder-b5-wip` base was `4f2ae74` (PB-27); origin/main had advanced +4 (`642bec7`): a Pascal handoff, Prolog M34-3 + parity-gate, and **FIX-7b on `bb_scan_pos.cpp`**.
2. Compared file sets: **fully disjoint** — the B-ladder touches `bb_pattern_unary_{i,s}.cpp`, `bb_match_atp.cpp`, `bb_templates.h`, `emit_bb.c`, `emit_core.c`, `lower_sno.c`, `Makefile`, design-doc; origin's 4 commits touch `HANDOFF.md`, `BB-REVAMP-TRACKER.md`, `bb_scan_pos.cpp`, `scripts/test_gate_pl_m34_parity.sh`, a handoff `.md`. **No overlap, no pascal.y** (PB-26/27 already in the shared base `4f2ae74`).
3. `git rebase origin/main` on the branch → **clean, zero conflicts**. Inherited origin's FIX-7b `bb_scan_pos.cpp`.
4. **Rebuilt + re-ran the full battery on the rebased tree** (mandatory — the tree changed under FIX-7b/M34-3). All green.
5. `git checkout main; git merge --ff-only snobol4-bladder-b5-wip` → pure fast-forward; `git push origin main` (normal push — origin/main was still `642bec7`, so it FF'd; **never `--force` on main**).
6. Feature branch force-synced to the landed tip (`--force-with-lease`, feature branch only) so it isn't left divergent-stale.

## B5 verification detail (so no session re-derives it)
**Builder route requires a NAMED-VARIABLE subject.** `S = '…'; P = SPAN('ab'); S ? P . X` routes the *scan* through `flat_drive_scan_native`, which consumes the built DT_P via the B3 defer shim. A **literal** subject (`'aabbcc' ? P`) routes through the `rt_scan` general arm → the still-standing BOMB `bb_scan: TEXT(mode-4) non-literal pattern needs native PB-RB graph (pending)`. **That BOMB is S1 SUBJECT-EVERYWHERE's job, NOT a B5 bug.** ⚠️ The prior B5 handoff's stated probe path (`'aabbcc' ? P`) would have hit this BOMB — it was never run. Use named-var subjects to probe builders until S1 lands.

Probes (all vs `/home/claude/x64/bin/sbl -b`, named-var subject):
| pattern | subject | scrip = sbl |
|---|---|---|
| SPAN('ab') | aabbcc | `aabb` ✓ |
| ANY('abc') | cab | `c` ✓ |
| NOTANY('ab') | Xab | `X` ✓ |
| BREAK('X') | abcXdef | `abc` ✓ |
| BREAKX('X') | abcXdef | `abc` ✓ |
| BREAK('X') | abc (no X) | fail ✓ (BREAK fails at Δ w/ no break char — standard SPITBOL, p.214) |
| SPAN('z') | abc | fail ✓ |
| ANY('z') | abc | fail ✓ |

Probe scripts left at `/tmp/b5probe2.sh` (named-var battery) and `/tmp/b5iso.sh` (fail-path isolation). The corpus runner is the durable gate.

## Two divergences — ISOLATED, DEFERRED, not B5 regressions
1. **Capture inside a built DT_P corrupts BREAK's fail-path.** `P = BREAK('X') . X; S ? P :F(NO)` on a no-X subject: scrip succeeds-null (`matched[]`) where sbl fails. Remove the `. X` and BREAK fails correctly. → **B8** (capture-in-built-pattern) territory; capture inside DT_P is unbuilt. Statement-level capture on a *successful* single-primitive match already works (the success probes above carry `. X`).
2. **BREAKX β-regen needs a subsequent.** `BREAKX('X') . A 'Xc' . B` can't be exercised in the builder route until a literal subsequent can be stitched into the DT_P → **B6** STITCH-CAT. BREAKX's α (match-to-first-break-char) is verified; its β re-generation will be testable once B6 lands a downstream element to force the rematch.

## B5 design (as landed) — for B6's sake
`bb_pattern_unary_s.cpp`, precise parallel of B4's `bb_pattern_unary_i.cpp`. **Universal slot layout HELD** (so B6's `base = ω_site−24, β = ω_site+8` derivation is family-wide valid): `+0 cset_ptr · +8 saved-δ scratch (BREAKX β) · +16 out_γ · +24 out_ω · β@+32`. cset_ptr is a NUL-terminated strtab string filled exactly like `bb_pattern_lit`'s lit-ptr; pool-cursor load uses `ins2 mov rax, qword ptr [rip + g_pat_pool_cur]` (the B3 finding — `[rip+__]` emits `lea`, wrong for a value load). Matching is an inline call-free membership scan (no `strchr`, per the call-free-proto rule). Whole proto body in `ins1`/`ins2` passthrough (mode-4 TEXT-only), sidestepping the B2 `[r13+rax]`/`byte ptr` silent-drop trap. **β: one-shot → out_ω for ANY/NOTANY/SPAN/BREAK; BREAKX β re-generates** (restore +8, skip past break char, rescan; ω only when no further break char). ⛔ SCRATCH LANDMINE (B9): +8 is per-INSTANCE single-slot — ARBNO re-entering one instance needs per-activation save.

## NEXT — B6 STITCH-CAT
Per `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` (B0–B5 ✅, B6–B11 + B-CONV open) and D2:
- **`P = 'a' LEN(2)`** etc. — runtime `wire_seq`: patch a.γ_dangle → b.head; b.head.ω_inst → a's nearest-left-resume (one layer down, exactly `lower.c:57-63`).
- The unary_s/unary_i slot layout is built to support this (`β = ω_site + 8`).
- Unblocks the BREAKX-regen and capture-fail probes above once paired with B8.
- Probe-first vs sbl, one rung = one commit, m4 gates only, corpus non-decreasing HARD.

## Carried asks for Lon (unchanged from prior sessions)
- **Ring serialization / force-push prevention** workflow ruling — the IRD agent requested the same (`ee7042b7`). This session avoided a fourth incident by FF-only + disjoint-set verification, but the prevention mechanism is still Lon's call.
- **Ledger stamps:** nv get/set REMAINDER + raw allocator still REQUESTED (`SNOBOL4-5STAGE-OWNED-BUILD.md` permission ledger). RWX-staging veto (W^X flip = B11) still open.

## Session Setup reminder
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64   # sbl oracle
```
Gates (MODE-4 ONLY; never --interp/--run; never the all-modes runners):
```bash
bash scripts/test_smoke_snobol4.sh                               # 7/7 HARD
bash scripts/test_snobol4_pat_rung_suite.sh                      # 19/19 no-SKIP
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh  # 155 floor
bash scripts/test_gate_em_beauty_subsystems_mode4.sh             # 1/17 floor
bash scripts/test_gate_sno_pat_reg.sh                            # static fence HARD
```

— Opus 4.8, co-dev. GATES: MODE-4 ONLY.
