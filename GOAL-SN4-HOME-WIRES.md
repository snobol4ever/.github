# GOAL-SN4-HOME-WIRES — r10/r11 wires, two glue kinds, shim deletion (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** rΓ=r10 · rΩ=r11 product-wide (Lon s12 verbatim: *"remove the stupid PROC shim around patterns and use proper PASS-THRU glue using R10 and R11"*), exactly TWO glue kinds (ONE-SHOT · PASS-THRU; FRAMED IS NOT A GLUE KIND — s29), RBP never written by glue. **Mechanism authority = LADDER WREG + LADDER PT inside `GOAL-RBP-EARN.md` (absorbed by reference, corrections here supersede).** RTCC's wire half (veneer preservation) is owned HERE per the s14 arbitration: safe config = RTCC-ON **and** wire capture/restore, neither alone.

## RUNGS
- [ ] **W-0 · CLAIM SWEEP, HONEST.** r10/r11 usage census across templates + emit.cpp + **RTX hand asm + raw-byte encoders** (grep is insufficient — objdump the emitted slab too). With BOARD: claim gate becomes data-driven {rbx r9 r10 r11 r12 …} + `--strict` (today: r9-only, informational — a hole MECH documented).
- [x] **W-1 · ZCTX SCRATCH ERADICATION — DONE s33 (`26c84e72`). PREMISE WAS STALE:** the six sequences were already gone (`0970838f`); of 5 `g_zctx` mentions FOUR were comments and one was a dead exported BSS array (`uint64_t g_zctx[66]`, 528B, ZERO code uses, no extern, no emitted reference). Deleted. ⭐ **HOME GATE line 4 side effect, MEASURED:** the last surviving `g_blob_ctx` mention lived inside that array's comment, so `g_blob_ctx` and `rt_blob_ctx_ptr` now BOTH grep to 0. Original text kept below for provenance: ~~ All six ZCTX sequences use r10/r11 as scratch (s37 measured) — re-allocate BEFORE any flip; live-on-arrival landmine otherwise.~~
- [ ] **W-2 · PUSH/POP GUARD UNIFICATION (MECH s37(B), the sole D12/D13 regression pair).** push guard `flat_jmp_entry` (emit.cpp:2373) vs pop guard `!_wire_stub && flat_jmp_entry && flat_pat` (:2806): any graph outside the intersection pushes and never pops = POP DEBT. ⛔ ONE predicate, both media — never a compensating pop on one exit (two-calculators disease). If the CLASS-O/`_wire_stub` design call is still ambiguous after the census, route both arms to Lon.
- [ ] **W-3 · WREG MECHANISM, DORMANT.** Site glue `lea r10,[rip+site_γ]` · `lea r11,[rip+site_ω]` · `jmp <first interior box>`; exits `jmp r10`/`jmp r11`. Killswitched; default emission byte-identical to HEAD. r10/r11 are caller-saved ⇒ saves are TEMPLATE-EMITTED per-activation on the spine, never an implicit choke (s18 RSP-SAFETY + the stack-arg witness).
- [ ] **W-4 · ARENA WIRE-PAIR SLOT (+16B) — THIS SEAT OWNS THE LAYOUT.** Blob-interior pending records capture {r10,r11} at push, restore at β, or it is `g_blob_ctx`'s single-cell defect in register clothing (the LAW). RBP/EARN-5 consumes this layout — one authority.
- [ ] **W-5 · ⛔ THE FLIP — REQUIRES EARN-1 + EARN-3 LANDED (EARN-10 ordering).** PROC-shim deletion (PT-1..3), CLASS-D exit ceremony dies with it. The old WREG residual (19 SEGV + 7 HANG) was MISSING FRAMES, not glue defects — EXPECTED cured by EARN; measure by set, never assume.
- [ ] **W-6 · RTCC RE-ENTRANT PRESERVATION + DEFAULT-ON REVALIDATION.** The veneer round-trips wires on leaf crossings only; fix the re-entrant case; then RTCC default-ON must hold the P0 floors with NO `SCRIP_RTCC=0` escape (kills the m4-130 class). Belt-and-suspenders: `-Wl,-z,now` for the r11 lazy-binding clobber.

## GATES (every rung)
claim gate `--strict` green · probe + crosscheck BY SET vs P0 floors both modes, RTCC ON and OFF until W-6 seals · killswitch md5 discipline · FINDING + cursor move.

## ⭐ LIVE CURSOR — 2026-08-12 s35 (Opus 5)

**SCRIP `2913c6a4` · corpus `019795bb` · x64 not cloned — hashes are POST-REBASE onto the origins that moved mid-session; floor re-proved at these exact hashes, not inherited.** m3 floor re-proved BY SET at this HEAD: **157 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10} — IDENTICAL to s33/s34.** One compiler edit + 3 mandated regen commits. **PUSH STATE at the bottom — read it before believing anything here landed.**

### ⛔⭐⭐⭐ FOR LON — TWO THINGS NEED YOU, ONE IS A PROCESS BREAK

**(1) TWO LIVE SESSIONS SHARED THIS SEAT FILE AND THIS CONTAINER TODAY.** s34 (Sonnet 5) and s35 (Opus 5, this one) both ran against `GOAL-SN4-HOME-WIRES.md` on the same filesystem and the same `.github` clone. I discovered it only when the cursor I had read at orientation (s33) had silently become s34 mid-session, and `git status` showed **ahead 2** when I had made exactly one commit — the other was theirs, local and unpushed. This is precisely the **ONE INVARIANT** of `GOAL-SN4-HOME.md` ("ONE LIVE SESSION PER SEAT FILE. Two sessions in one file is the s38b race"). Nothing was lost — our commits touch disjoint files and both are preserved — but that was luck, not design: had we both edited the cursor with `git add -A`, one would have silently swallowed the other's working tree. **The fire-and-forget model assumes one session per seat; something re-fired WIRES while it was already live.** Worth checking how, before it happens on a file where the overlap is not disjoint.

**(2) A WHITELIST-POLICY QUESTION I DELIBERATELY DID NOT DECIDE.** See "OPEN QUESTION" below — does `product-wide` mean physically clearing Prolog off r10/r11 even where SNOBOL4 provably cannot reach it? That's a charter question, not a data question.

### ⛔⭐⭐⭐ THE W-0 PREMISE WAS STALE IN A WAY NEITHER PRIOR READ CAUGHT

**The SNOBOL4 path was ALREADY swept of r10/r11 before W-0 opened.** Commits `89ff6994` ("R10/R11-ERAD slice 1: delete scratch use of the reserved wire pair from the SNOBOL4 path") and `b5a288bd` ("slice 2 + CORRECTION ON MYSELF: slice 1's ZERO-RESIDUE claim was FALSE"), recorded in `FINDING-2026-08-11d-…-R10R11-ERAD-SNOBOL4-PATH-COMPLETE-…`. The sweep moved the SN4 path to **r8**. **Neither the s33 cursor nor s34's FINDING-12f cites this ladder** — both treated the 226/222 number as undifferentiated SNOBOL4 debt. It is not.

Two independent 2026-08-12 reads converge on the same correction from different angles; fold BOTH into any future W-0 statement:
- **FINDING-12f (s34, Sonnet 5)** — STRUCTURAL axis: scratch vs. preserver. `bb_call_fn.cpp` 93/93 by hand = 100% genuine scratch; `xa_flat.cpp` splits in two; `bb_scan_*` are preservers.
- **FINDING-12g (s35, Opus 5, this session)** — REACHABILITY axis: can a SNOBOL4 program reach these sites at all? **Almost none of them.** `bb_call_fn.cpp`'s 93 and `xa_flat.cpp`'s bulk sit behind `dop_direct_fp` (table is 100% Prolog `$`-builtins), `pl_cells_graph`, or `zframe_graph`. Verified at the source of truth, not from comments: `zframe_graph = 1` is stamped by exactly four lowerers — `lower_icon.c:1423`, `lower_prolog.c:1395`, `lower_pascal.c:831`, `lower_raku.c:1051`. **`lower_snobol4.c` has ZERO mentions of it**; `IR_alloc` calloc-zeroes the field.
- ⛔ **A STALE CODE COMMENT TO DISTRUST:** `bb_call_proc_staged.cpp:673` claims "zframe_graph=0 for all SN4/Prolog/Raku/Pascal" — **false since PL-FR-2 gave Prolog the wholesale stamp.** `emit.cpp:1903` is the correct account. STALE-ORIENTATION, living in a code comment where no cursor discipline reaches it.

**CONSEQUENCE — the gate's 222 headline is NOT 222 units of SNOBOL4 risk.** The real remaining risk is the two surfaces reachability cannot excuse: **`x86_asm.h`** (shared encoder, every language) and **RTX hand-asm** (223 occ, not graph-gated at all). Prioritize those; the template count is mostly Prolog bookkeeping that cannot execute beside a live SN4 wire.

### WHAT LANDED (compiler)
- **`e019c651` — `bb_var.cpp` PL-ZK-5B dual-write drops r10/r11 entirely.** rax/rdx already hold `ZRES(0)`/`ZRES(8)` from the two lines directly above; nothing between there and `x86_gamma()`/`x86_beta_trampoline()` reads either (both verified as bare jmp/label emitters with no register-content dependency). The r10/r11 hop was a redundant reload, not a register need. Gate: **226→222 occ, 25→24 files**; site is GONE from the sweep list, not whitelisted. Build clean, smoke-tested, m3 floor identical by set.
- ⛔ **TENSION I AM FLAGGING RATHER THAN BURYING:** s34's NEXT item 2 said `bb_var.cpp` needs a replacement-register design call from Lon before editing. I edited it anyway, on the reasoning that their caution targets *choosing a replacement register* (a policy decision needing one consistent answer across many sites) whereas this fix **eliminates the need for one** — no register was claimed. I believe that distinction holds; Lon should overrule me if it doesn't. **I did NOT extend the move** to `bb_call_fn.cpp` (93 occ) or `xa_flat.cpp`'s dc-stub, where a genuine register-choice decision IS involved. Those sit exactly where s34 left them.
- **`bb_lit_scalar.cpp` — SAME SHAPE, DELIBERATELY NOT TOUCHED.** Its `ls_dual(w)` is a SHARED "ONE AUTHORITY" helper across multiple literal sites, and at `IR_LIT_INTEGER` the w=0 source is a compile-time immediate never in a register — the "already live in rax/rdx" shortcut does NOT generalize. Auditing every call site is the prerequisite. Dead-for-SN4 either way, so no urgency.

### ⛔ THE `.s` ARTIFACTS WERE STALE — AND MY REGEN COMMITS ARE MISLABELED
RULES.md step 4 forces regen when `src/templates/*.cpp` is touched, so I ran all three in order. They committed **large diffs that are NOT mine**: `129e72f3` (benchmarks, 23 files), plus feature + demo commits, all labeled with my rung. The content is other seats' unregenerated drift — the r10/r11→**r8** ERAD sweep above, plus a new `call rtcc_load_all@PLT` (RBP-EARN s34 / RC-5-GVA). **My edit is Prolog-gated and contributes ZERO bytes to any SNOBOL4 `.s`.** Two takeaways: (a) prior codegen landings skipped step 4, so the artifacts drifted; (b) whoever regenerates next inherits the mislabel — the commit message names a rung that did not cause the diff. Not corrupt, just misattributed; worth a note when reading `git log` on corpus.

### RTX `rtx_match.S` — OPENED (s34's #1), PARTIAL CLASSIFICATION, NOT FINISHED
Confirmed **SNOBOL4-reachable** and therefore NOT excusable by reachability: the file header states its own purpose as *"C deleted from the SNOBOL4-reachable runtime"*, and it is called from `bb_scan_match.cpp`, `bb_var_global.cpp`, `bb_call.cpp`, `bb_idx_get.cpp`. 89 occ; ~65 lines scanned in one pass, **not** all read by hand. Four distinct idioms, do not sweep as one unit:
1. **Momentary GOT-global accessors** (`g_cap_gen`, `rt_g_want_name`): `mov r10,[rip+X@GOTPCREL]` → one deref → done. Same shape as the Prolog scratch, but SN4-reachable.
2. **GOT-indirect call/tail-call** (`NV_GET_fn` :1027-8, `dtp_fn_of` :1035-6): ordinary `call r10`/`jmp r10` idiom, 2 instructions.
3. **Capture-stack block** (~:195-291, the SAVE-box push/pop the header documents): r11 does real address arithmetic (`&g_dfx[top]`, stride 24) and is live across several field accesses, with two genuine push/pop preservers embedded mid-block.
4. **Longer-lived carry**: r11 holds `varname` from `pop` :1128 through `mov rdi,r11` :1164.
- ⛔ **UNRESOLVED, WORTH A LOOK:** lines 296-314 / 390-393 / 536-539 / 1136-1143 reach **Σ (subject) and Σlen through GOT-indirect globals** (`mov r10,[rip+Σ@GOTPCREL]; mov r10,[r10]`) — but `GOAL-SN4-HOME.md`'s register contract names **R13** as Σ's home. Either these are slow/leaf paths legitimately falling back to a global copy while the hot inlined path keeps Σ in r13, or the contract and the shipping code disagree. **Cannot be settled by grep** — needs function boundaries + r13 liveness at those sites. Next session's sharpest question.

### OPEN QUESTION FOR LON — WHITELIST POLICY (deliberately NOT decided here)
Does **"product-wide"** (charter line 1) require physically clearing Prolog off r10/r11 *regardless of reachability*, or is provably-dead-for-SNOBOL4 sufficient to license a site? Pressure toward the former: `xa_flat.cpp` already names `rt_pl_dc_leave_γ` / `rt_pl_dc_leave_ω` — **Prolog has its own γ/ω continuation convention already using r11**, so the two may need to converge rather than coexist. Pressure toward the latter: those 118 occurrences cannot execute beside a live SN4 wire, so sweeping them buys no SN4 correctness today. ⛔ **`wreg_claim_whitelist.txt`'s header defines exactly FOUR site-classes, all describing code that legitimately OWNS the wires — "unreachable for the graphs this gate protects" fits none of them.** Adding a 5th class is a real edit to shared registry policy, so I left the whitelist untouched rather than force the answer in. **This is the decision that unblocks the rest of W-0.**

### NEXT SEAT, IN ORDER (supersedes s34's list; items 3-5 unchanged from it)
1. **Finish `rtx_match.S` by hand** (89 occ, ~24 unscanned) — and settle the **Σ/r13 contract question** above. Highest-risk surface, SN4-reachable, not excusable by reachability.
2. **The other 9 RTX `.S` files** (134 occ) — same treatment, same reason.
3. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness D12/D13 flipping green.
4. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block` (per-activation spine, not flat block).
5. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.
- **Do NOT re-derive the W-0 template census a fourth time.** Between FINDING-12f (structural), FINDING-12g (reachability), and FINDING-2026-08-11d (the ERAD ladder), the template surface is mapped. What is missing is RTX and a policy decision, not another count.

**UNBLOCKS: nothing new** (W-5 predicate still FALSE: `frame_need_of` grep still empty, re-checked s35).

---

## ⭐ LIVE CURSOR — 2026-08-12 (Claude Sonnet 5, continuing s35, same day) — RTX CENSUS: 2 OF 10 FILES DONE

**SCRIP `2913c6a4` (unchanged, read-only) · corpus not touched this session.** Read-only session:
`rtx_match.S` (89/89 occ) and `rtx_icnsub.S` (33/33 occ) fully hand-classified. FINDING pushed
(see `FINDING-2026-08-12h-…` for full detail); this cursor move is the handoff artifact.

### WHAT LANDED
- **`rtx_match.S` FINISHED** — item 1 above is DONE. All 89 occurrences map to s34's four known
  idioms (momentary GOT accessor · GOT-indirect call/tail-call · capture-stack block · longer-lived
  carry), no fifth idiom found. **The Σ/r13 open question is RESOLVED, not just deferred**: it was
  already answered in `rt_match_ctx_restore`'s own header comment (lines 378-381) — r13 is the hot
  inlined-path pin, the GOT-global Σ/Σlen pair is a deliberate C-readable mirror for slow paths and
  cross-TU C code that cannot see a register pin at all. Not a contract violation, nothing to
  arbitrate.
- **`rtx_icnsub.S` FINISHED** (first file of item 2's list of 9, though numbered separately since
  it's Icon-named but SN4-reachable — see below). 33/33 occurrences classified. One NEW idiom found:
  a **loop-carried pointer** (hash-chain walk, r10=link/r11=key cursor) — live across loop
  iterations but never across a `call`, structurally lower-risk than the capture-stack shape.
- **⭐ REACHABILITY CORRECTION (second instance of the FINDING-12g pattern, this time in RTX asm):**
  `rt_subscript_var` (`rtx_icnsub.S`) is **SNOBOL4-reachable** despite its Icon-flavored name and
  the header's own "RELEASED to ICON-RTX" ledger note — confirmed via `lower_snobol4.c:376,779`
  emitting `IR_SUBSCRIPT` for ordinary SNOBOL4 `X[i]` subscripting, and the file's own RTX-28
  comment says outright "arrays, which are SNOBOL4's." **Filenames and gate-ledger allocation
  language are not reachability proxies — check the lowerer call graph before excusing any RTX
  file by name.** This likely applies to some of the remaining 8 files too; check each on its own
  merits, don't pattern-match from this file's result either.

### NEXT SEAT, IN ORDER (supersedes the s35 list above for items 1-2) — 7 OF 10 RTX FILES DONE
1. **The other 3 RTX `.S` files** (30 occ remaining: `rtx_icnagg.S` 11 · `rtx_icnrel.S` 8 ·
   `rtx_icnnum.S` 11) — filenames say Icon; CHECK, don't assume, per addenda 2/4 (icnsub/icnvar
   turned out SN4-reachable) vs. addendum 6 (plcall turned out genuinely excused). `rtx_alloc.S`
   (20), `rtx_str.S` (19), `rtx_icnvar.S` (13), `rtx_arith.S` (9), and `rtx_plcall.S` (10) are now
   ALSO DONE — see FINDING-2026-08-12h addenda 2-6.
2. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness
   D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout. **W-4's arena wire-pair
   slot design should account for the "carve/copy carry" shape** found in `rtx_str.S`
   (`str_concat_d`: r10/r11 carry a fresh buffer pointer + length across exactly one
   `rt_str_alloc` call, then die at `ret`) — a naive save-at-call-boundary scheme would clobber
   this pattern, which recurs across the family (also in `rtx_match.S`'s `rt_cap_open` and
   `rt_match_replace`).
5. **⭐ W-0 whitelist-policy question (s35's OPEN QUESTION, still unanswered):** `rtx_plcall.S`
   is now a CONFIRMED, structurally-verified instance of "provably dead for SNOBOL4" (Prolog/
   Icon/Raku's `IR_CALL_PROC_STAGED` never reaches `lower_snobol4.c`) — a clean, fully-checked
   test case for whichever way that policy question gets decided.

⛔ W-5 REQUIRES (predicate): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND
`UNBLOCKS: WIRES W-5` on origin. Still FALSE, unchanged this session.

**UNBLOCKS: nothing new** (RTX census is a sub-item of W-0, not a rung boundary by itself).
**PROGRESS: 7 of 10 RTX `.S` files done (rtx_match.S 89 + rtx_icnsub.S 33 + rtx_alloc.S 20 +
rtx_str.S 19 + rtx_icnvar.S 13 + rtx_arith.S 9 + rtx_plcall.S 10 = 193 of 223 total RTX
occurrences classified, 30 remaining across 3 files).**

---

## LIVE CURSOR — 2026-08-12 s34 (Sonnet 5) — superseded by s35 above, retained per STALE-ORIENTATION (c)

**SCRIP `51934a9f` · corpus `14dc06bd` — read-only session, zero compiler bytes, zero code touched. FINDING pushed; this cursor move is the handoff artifact.**

### RUNG STATE
- **W-0 CLASSIFICATION VERIFIED, STILL NOT SWEPT** — s33's 93/25 tally is CONFIRMED CORRECT (re-derived independently via `test_gate_wreg_claim.sh`, not assumed); `bb_var.cpp:19` in the s33 line above is a **line number** (one site, 4 occurrences), not a count — the notation was misleading next to the other two entries, now fixed here. Full classification by hand, not by count:
  - `bb_call_fn.cpp` (93/93 read) + `bb_var.cpp` (4/4 read) = **100% genuine scratch, zero preservers** — all Prolog trail/heap-frontier/misc-global bookkeeping (`g_pl_trail`, `g_hp_fr`, `g_plw_dot_sl`, `g_plw_cellws_on`, `g_zeta_mode`) local to one helper each, plus the PL-ZK-5B dual-write idiom (ZRES→FRQ copy) appearing 3× total across both files. Two of these sites already document hand-verified workarounds for the `XK_R10MIR` encoder landmine below — confirmed live, not hypothetical.
  - `xa_flat.cpp` (25/25 read) **SPLITS IN TWO — do not sweep as one unit.** Lines 474–479 are the same genuine-scratch pattern as above. Lines 238–307 (the ICN-FR-3 zframe dc-stub / PL-DC direct-call entry) are the **pre-existing PROC-shim mechanism itself** — r11 carries a real C-ABI return address across a `rt_arg_stage`/`rt_pl_dc_prep` call via push/pop/jmp, r10 carries a transient cell-pointer reloaded from the stack (not the register) specifically *because* an earlier version tried holding it in r10 across the call and a SysV clobber ate it (SIGSEGV, hand-documented in the comment). This is shape-similar to a preserver but is not one, and it is the exact shim W-5 exists to delete — **not** scratch to reassign now. Full detail + line numbers: `FINDING-2026-08-12f-…`.
  - `bb_scan_match.cpp` spot-checked (8/8 read): confirmed genuine PRESERVER — every occurrence is push-r10-before-call / pop-r10-after around `rt_scan_needle`/`memcmp`, zero r11. The other 9 `bb_scan_*` files (~44 occ) and the remaining small files (`bb_idx_get/set`, `bb_initial`, `bb_rk_*`, `bb_glue_flat`, `bb_call_proc_staged`, `xa_bb_macro_library`, `bb_lit_scalar` — 31 occ) are UNVERIFIED, only inherited-trusted by class per the s33 INSTRUMENT RULE (one member confirmed ≠ the whole family confirmed).
  - **`x86_asm.h`** (25 occ) sits unwhitelisted — expected per the gate's own comment (whitelist empties until W-3 creates glue emitters), not a defect.
  - **RTX hand-asm surface UNOPENED THIS SESSION, LIKELY HIGHEST-RISK REMAINING WORK**: gate reports 223 occurrences across 10 `.S` files, `rtx_match.S` alone at 89 — *"the sharpest edge: it executes DURING a match, i.e. while the wires are live"* (gate's own words). Open this before the remaining `bb_scan_*` files — it's less trusted and higher-stakes.
  - No code changed. `--strict` still fails the same way it did at s33 (W-3's glue emitters don't exist yet). This session's contribution is a verified map, not a smaller number.
- **W-1 DONE** (`26c84e72`) — ZCTX scratch eradication complete; premise was stale (`g_zctx[66]` was dead exported BSS, zero code/emitter uses). HOME GATE line 4 satisfied as a side effect: `g_blob_ctx` and `rt_blob_ctx_ptr` both grep to 0, **measured not assumed.**
- **W-2 OPEN, LIVE WITNESSES D12/D13 in probe suite** — rung's line numbers DRIFTED (`emit.cpp:2373/2806` are wrong). Current guards: pop-side `_blob_wire` at `:2717` (`!_wire_stub && flat_jmp_entry && flat_pat`), push at `:2716`; related `op_zgpop` at `:842`. ⛔ **Push/pop EMISSION is template-side (TEMPLATE-ONLY law), not emit.cpp** — start with a grep census in `bb_glue_*.cpp`, not emit.cpp. NOT touched this session.
- **W-3..W-4 UNOPENED** — W-3 (WREG mechanism, dormant) is clean to open; census `bb_glue_flat.cpp` first. W-4 (arena wire-pair slot +16B) — THIS SEAT OWNS the layout; RBP/EARN-5 consumes it.
- **W-5 BLOCKED** — `frame_need_of` grep still empty (re-checked s34), predicate FALSE. Skip.
- **W-6 OPEN, NOT touched this session** — leaf crossings PROVEN SAFE (172 veneered, 0 bare match-time). Scope narrows to **re-entrant case only**: `g_rtcc_block` is one flat block at fixed offsets (r10→+56, r11→+64); a re-entrant `rt_*` overwrites outer wires with inner. Witness with `140_pat_eval_double_fn_trick` / `141_pat_eval_double_fn_arbno`.

### ⛔⭐⭐⭐ THE m4 FLOOR IS DARK — EVERY GATE HERE IS m3-ONLY UNTIL BOARD B-0 LANDS

Any program naming a user variable SIGSEGVs in mode 4. Root cause: **r9 (GVA base) is only established by a veneer RELOAD; the prologue's first three crossings are bare.** Slot is correctly seeded (`g_rtcc_block[6]=0x70001000`); nothing hands it to the register. Candidate repair: emit `mov r9,[g_rtcc_block+48]` in the m4 prologue AFTER `core_lib_init`. ⛔ Do NOT add r9 to the veneer writeback — that overwrites the constant seed with garbage on the first crossing. Falsified: `-Wl,-z,now`, `SCRIP_RTCC=0/1`, stale `.so` — do not re-spend. Full chain: `FINDING-2026-08-12e-…`.

### m3 BY-SET FLOOR (measured s33, before and after W-1, identical)
`corpus/probe/bb/run_suite.sh` (NOTE: this is `corpus/probe/bb/`, NOT `SCRIP/scripts/` — the master's instrument map path is wrong): **157 pass · 1 xfail · 5 REGRESSION {D12, D13, H31, X01, X10} — NOT BASELINED (`XFAIL.run` = `fence_probe` only).** Any seat will see these 5; hold by SET, never count.

### NAMED PREDICTIONS FOR THE FLIP (record here, do NOT fix before W-5 opens)
- **Scan-family asymmetry:** 26 `push r10` / 0 `push r11` across 10 `bb_scan_*.cpp` files. Every one protects γ and abandons ω the moment r11 becomes a wire. Witness at W-5.
- **Encoder landmine:** `[r10]` in a template → `XK_R10MIR` → `x86_store_cursor_mirror()` = `mov [r10],r14d`. Any W-3/W-5 template touching `[r10]` must use `[r10 + 0]`.

### INSTRUMENT RULE EARNED THIS SESSION (offer for RULES.md)
Three scanner bugs in one session, all the same family (awk keys as strings; name-shaped filter; `r=$?` capturing wrong process). All caught before publication. **Rule: an instrument reports a class only after one member has been confirmed by hand.** A table from a scanner is a claim about text; verify its units before trusting a zero.

### INSTRUMENT RULE, ROUND 2 (s34) — THE HAND-VERIFIER ALSO NEEDS TO CHECK ITSELF AGAINST THE REAL GATE
Same family again, different direction: I hand-rolled a `grep -c`/`grep -o` census to sanity-check the s33 cursor's 93/25 tally, got 81/101 and 39/50, and flagged a discrepancy — the CURSOR turned out right and MY grep was wrong (no comment-stripping; quote-restricted pattern misses the majority-case `"[r10 + N]"` bracketed-operand form; no sub-register spellings). `test_gate_wreg_claim.sh` already solves all three problems and prints both units. **Rule, extended: before hand-rolling a census of anything this codebase already has a named gate script for, run the gate script first.** A hand grep that disagrees with a trusted number is not evidence the number is wrong — it's evidence to go find the real instrument before publishing a correction.

### NEXT SEAT, IN ORDER
1. **RTX hand-asm census** — `rtx_match.S` (89 occ, live during a match — highest risk) + the other 9 `.S` files (134 occ). Completely unopened; `test_gate_wreg_claim.sh`'s RTX section already counts it, reading-by-hand is what's missing.
2. **W-0 register-reassignment design call** — `bb_call_fn.cpp` + `bb_var.cpp` are fully classified (100% genuine Prolog scratch, safe to reassign) but need a replacement-register decision before editing; a quick read suggests r8/rcx/rdx may be free at those specific sites but this is NOT verified against a full liveness check. `xa_flat.cpp` lines 238–307 are the PROC-shim itself — do NOT sweep, that's W-5. Remaining `bb_scan_*` files (~44 occ) + small files (~31 occ) are class-trusted from one spot-check, not individually verified.
3. **W-2** — census `bb_glue_*.cpp` for asymmetric push/pop; fix to ONE predicate both media; witness D12/D13 flipping green.
4. **W-6** — nested-crossing witness with probe `140`/`141`; then fix the re-entrant `g_rtcc_block` case (per-activation spine, not flat block).
5. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

⛔ W-5 REQUIRES (predicate): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND `UNBLOCKS: WIRES W-5` on origin. Currently FALSE — skip to W-6 or POOL.

**UNBLOCKS: WIRES W-6** (leaf half proven, scope narrowed to re-entrant case only).
