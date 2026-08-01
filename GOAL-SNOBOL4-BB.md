# GOAL-SNOBOL4-BB — SNOBOL4 → native x86 Byrd-Box codegen

Frontend: SNOBOL4 → shared IR → BB emitter (mode-3 `--run` / mode-4 `--compile`). Protocol: RULES.md; template/encoder work requires ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md FIRST. Watermark is SHARED STATE — re-prove at session start AND close. History pruned 2026-07-30; full text in FINDING docs + git (pre-shrink = `.github` `2f3fd45a`).

---

## ⛔⭐⭐ THE MODEL

**THERE IS NO GRAPH FRAME.** Every BB: **allocates at α** (`sub rsp,K`, *its own* K) · **reads/writes only its own cell** · **releases at γ/ω** · **jumps**. No pre-allocation, no whole-graph carve, no prefix-summed prologue.

⭐ **THE ONE REFINEMENT (law 4):** value spine rides RSP FORTH-style; housekeeping that must survive an unwind (ARBNO/FENCE1/CALL) rides a depth-immune RBP. `flat_stmt_frame` default is OFF (`SCRIP_STMT_FRAME=1` = opt-in); `op_zgpop` is the SOLE statement-terminal release authority.

**THE WHOLE-GRAPH CARVE IS A CORPSE.** `flat_frame_bytes` is debt; so are ~1054 `FR`/`FRQ`/`FRQB` reader sites across ~109 templates. **The job is to delete their customers until there are none, then delete the carve.**

### ⛔⭐⭐ CARVE-ERAD (head rung)

⭐ **THE ~1054 READER SITES NEED ZERO EDITS.** They resolve through `x86_asm.h:373 x86_frame_off()`. ⛔ Hand-converting 109 files is WRONG. **MANIFEST:** `flat_frame_bytes` 31 sites · `op_flat_disp` 24 · carve emission 7 · `x86_frame_off` 1 line. **ORDER:** (1) per-BB address authority complete FIRST; (2) drop `op_flat_disp` from `x86_frame_off`, delete its 24 sites; (3) delete `flat_frame_bytes` + 7 carve sites. ⚠ DO NOT cut sites before (1) covers their readers. ✅ Step (1) mechanism is `op_zread[k] = δ_out(consumer) − δ_out(producer)` staged by `zd_plan` — not a running-sum depth.

### ⛔ THE FAILURE MODES
- Treating the frame as infrastructure. It is a corpse.
- Clamping the carve while readers still address into it. Tautological — the reds name unconverted boxes.
- Misreading law 4's RBP constructs as licensing a graph frame.

### ✅ THE ONLY DISCRIMINATING TEST
Convert one box's readers to its own cell; watch the carve requirement DROP. Progress = monotone decrease of the declined-statement census.

---

## ⛔⭐⭐ LIVE CURSOR — s22x (2026-08-01)

Directive: s22w NEXT items 1+3 under Lon grant "All your choices. I'm with you on this." — GLUE formalization + match-family FORTH-cell conversion.

⭐⭐⭐ **TWO LANDINGS, ZERO BROKEN BY SET, BOTH MODES.**

**(1) GLUE-SYM — SCRIP `8aceaaef`.** All 10 hand-rolled pass-through wire trios (`lea rcx,<γ>; lea rdx,<ω>; jmp rax`) → `bb_glue_pass_wires(gid,wid)`, ONE spelling tree-wide: bb_call_proc_staged ×5 · bb_call_value (+ missing bb_templates.h include) · bb_match_capture · bb_match_release · bb_match_defer L7 · **bb_match_value (the backlog's unlisted 6th member)**. Dormant legacy zr-anchor IF-arms hoisted above the glue (lea rcx/rdx touch neither rsp nor zr). PROVEN: `.s` byte-identical **0/318**, crosscheck IDENTICAL BY SET both modes. Glue taxonomy now symmetric: `flat/framed_enter+leave` (storage) · `outer_γ/ω` (CLASS O) · `wire_γ/ω` (CLASS P one-shot) · `pass_wires` (pass-through). Grid item FOUR stays dynamic per s22v Ch.9 ruling.

**(2) CAS-MARKER-CARRY — SCRIP `b016019d`. The match unwind is DEPTH-FREE.** The head's tag-0 sentinel (24B, 16 unused) now carries the rsp mark (+8) and patstk snapshot (+16); tail RELEASE, general RELEASE (RSP+rfc arm), and the head fail exit recover both off the marker they already scan to — the second variable-depth reach the original CAS-MARKER note promised deleted, is deleted. **ROOT CAUSE (041 class, gdb + static audit):** `op_fc_disp` counts fc_geom grants but NOT the ZW-1 alpha carves the non-popping γ spine leaves live — release entered 32 deep of its spellings, `[rsp+16]` read the assign_save leaf cell (dword cursor 0 under 0x7fff residue), one-mov unwind loaded rsp=0x7fff00000000, push SEGV. Backtrack path was immune (leaf βs pop); ONLY the success path exposed it. Fixed +3 (041_pat_span, 042_pat_break, 047_pat_rtab — the linear head→leaf→capture→release shapes). Non-default regimes byte-preserved (marker arms gated `ZC_FRAME_RSP && rfc()`).

**WATERMARK:** open m3 217/99/1 · m4 214/101/1 → close **m3 220/96/1 · m4 217/98/1** · DIVERGE 3 {170, 1016, test_stack} unchanged.

**REMAINING-FAIL DECOMPOSITION (fresh, s22x close):** (a) **arbno/alt capture-start** — 052/054/065-class, rc=0 wrong capture (V='' where oracle 'aaa'), PRE-EXISTING (rc unchanged across s22x), the dcap start-clobber family; (b) **stored-pattern rt_cap_push SEGV** — 053-class, `P = ('a'|'b'|'c'); X P . V` crashes INSIDE rt_cap_push (C side, rsp sane) from n19_match_assign_save under the DT_P match_value path — the s22 localized stored-pattern class; (c) fence-via-var family (~15 programs); (d) DIVERGE 3 carried.

**Instrument note (my own misattribution this session):** general-arm `RSP(fc_disp+8)` with fc_disp=0 and tail-arm `RSP(fc_disp+0)` with fc_disp=8 emit IDENTICAL bytes — verify which ARM fired from the template conditions, never from the emitted shape.

**Residue flagged, not converted:** release's dval≠0 arm (end-cursor stash) still speaks `fc_disp`-relative spellings — same disease class, convert when a dval witness fails on it.

**NEXT — ORDERED:**
1. ⭐⭐ **Arbno/alt capture-start** (052/054/065): dcap start recorded per-iteration or clobbered — monitor-bracket the first divergent capture event.
2. ⭐⭐ **Stored-pattern rt_cap_push SEGV** (053): C-side fault, gdb bt into rt_cap_push internals.
3. **ZD-5a admission proper** (IR_MATCH_HEAD into zd_wl_kind + zd_k/zd_nops) — the marker made the unwind depth-free, so admission no longer needs the disp model for the release.
4. Glue backlog residue: need-FOUR emitted glue behind label-redefinition gate + role-0 emitted one-shot open — carried.
5. Proc-shape admission (OUTPUT-in-body × zero-locals) + DYNAMIC BOX · FENCE whack-at-checkpoint · JOIN-POINT RULE · TREEBANK Pop_list — carried.

---

## ⛔⭐⭐ PRIOR CURSOR — s22w (2026-08-01)

Directive: "NON-POPPING FORTH-style RSP ZETA stack, C-style RBP occasionally only when absolutely necessary; allocate on ALPHA, free on OMEGA, WHACK-FREE at completion / FENCE checkpoint / known sync point; dynamic glue for one-shot and pass-through access to completed one-entry-one-exit BB graphs."

⭐⭐⭐ **DEFINE-FAMILY ARG DELIVERY FIXED + FORMALS/SAVE-SET SPLIT. +15 m3 / +14 m4, ZERO BROKEN. SCRIP `0522b634` (ARGREAD) + `42f4e9f7` (NPSPLIT).**

**WATERMARK:** open m3 202/113/2 · m4 200/114/2 → close **m3 217/99/1 · m4 214/101/1** · DIVERGE 3 {170_pat_abort_kills_match, 1016_eval, test_stack(m3 output-correct rc=139, m4 FAIL)}.

**ARGREAD mechanism:** templates emit flat coordinates, not addresses — every `[rsp+N]` is re-parsed at x86_asm.h:1208/1209 and re-resolved through `x86_frame_off` at encode time. `FRQ(128)` resolved correctly (zvo_resolve 128→112). `FRQB(slot,bump)` pre-added the bump into the flat coordinate (128+32=160), so the UCLAIM owner table was asked about a fictitious offset, declined, and the read landed one DESCR cell high — every slim-installed formal arrived as garbage (083 m3 `Illegal data type`). Fix: x86_zop's rsp arm now resolves via `x86_frame_off` FIRST, adds the bump, spells raw `[rsp# + N]` so nothing re-resolves. Both FRQB consumers fixed (bb_call_proc_staged slim install + bb_save_restore role-0 twin). ⭐ **s22t "UCLAIM dark" is CORRECTED: the resolver is live** — only the claim-emission hook (x86_asm.h:1935) was under suspicion, and the s22w addendum proves that too is live (staged K=128/192 == emitted `sub rsp,128/192`, claim+release both end-to-end). **UCLAIM is fully live at HEAD. ZD debt is PURELY the match-family FRQ migration.**

**NPSPLIT:** `nparams` keeps full-name-set meaning everywhere (save/restore span, pname bound, pad loop, consistency check). New `nformals` (ProcEntry + sno_def_t + rt_proc_t appended-last — rtx_call.S offsets pinned by _Static_asserts) is consulted only at arg boundaries: bb_scc_probe admission, open_slim nargs guard, classic-prologue excess clamp (manual Ch.8: evaluated then IGNORED), dc eligibility. 0 = unsplit registrant → fallback to nparams, byte-identical. All 6 direct driver sites + both emitted m4 startup arms register it. Sweep IDENTICAL BY SET vs ARGREAD arm — no corpus excess-arg witnesses; np7 probe is the evidence (`swap('hello','world','XX')` against `(a,b)tmp`: conflated arm binds `tmp='XX'`, split arm prints `tmp[] / world hello` manual-exact, m3=m4).

**Side sightings (not credited to this rung):** (a) test_stack m3 output-correct-rc=139 exit-path residual — joins DIVERGE. (b) Proc-shape entry/dispatch admission failure (7 witnesses, 6 acquittals — NEXT 4 bisect 3/4 done): body never enters on `OUTPUT=A` shape probes; 085 (result-arith body) passes, np7 (OUTPUT-in-body + locals) passes. Surviving suspects: OUTPUT-target-in-body × zero-locals admission path.

**Instrument note:** container shell is DASH — `[ "$a" == "$b" ]` with multiline strings silently mis-verdicts; wrap in `bash -c` and compare with `diff`.

**NEXT — ORDERED:**
1. ⭐⭐⭐ **Pattern-blob ZD family** — match family still speaks FRQ/op_flat_disp; with ARGREAD proving the encode-time resolution chain end-to-end, convert match-family readers onto zvo/ZD and the arming exclusion list retires itself.
2. ~~UCLAIM claim-hook bisect~~ **CLOSED by s22w addendum — no code change needed.**
3. **Glue backlog conversion** (bb_call_proc_staged ×5, bb_call_value, bb_match_capture, bb_match_release, bb_match_defer L7 arm) + need-FOUR emitted glue behind label-redefinition gate + role-0 emitted one-shot open.
4. **Proc-shape admission** (OUTPUT-in-body × zero-locals, 7 witnesses / 6 acquittals) — two probes close it.
5. DYNAMIC BOX · FENCE whack-at-checkpoint · JOIN-POINT RULE · TREEBANK Pop_list — carried.

---

## ⛔⭐⭐ PRIOR CURSOR — s22v (2026-08-01)

⭐⭐⭐ **EXIT-CLASS LEDGER LANDED. IDENTICAL BY SET, BOTH MODES (m3 205/112 · m4 203/113/1 · DIV 2 {170,1016}), ZERO FIXED ZERO BROKEN.**

**Three exit classes** (the ledger comment at emit.cpp's shared-γ/ω site is the authority): **CLASS O** outer one-shot — α pins rbp, γ/ω whack at completion (`bb_glue_outer_γ/ω`). **CLASS C** chain-entered (LBL__/EVAL/CODE, `rt_chain_enter` citizens) — rt_chain_enter never touches rbp; the whack unwinds to the ambient C frame pointer (why RBPPAIR broke 1016_eval). **CLASS P** wire-entered DEFINE stub blobs — `bb_glue_wire_γ/ω`: snap the pcall record, restore rsp/rbp from it, jmp home through the port's wire.

**Four-glue grid:** (ONE) MAIN→initial graph: one-shot static, COMPLETE. (TWO) BB_DEFER→pattern blob: pass-through, `bb_glue_pass_wires(gid,wid)` MINTED + canonical consumer converted. (THREE) call site→SAVE_RESTORE/CALL_FUNC graph: one-shot dynamic, `bb_glue_wire_γ/ω` LANDED. (FOUR) two-block SHIM→function body: pass-through THROUGH REGISTRY (`rt_goto_transfer`) — **MUST STAY DYNAMIC** (SPITBOL Ch.9: CODE labels override same-name main labels at runtime).

**Pass-through conversion backlog (hand-rolled trios, convert on touch):** bb_call_proc_staged ×5 · bb_call_value · bb_match_capture · bb_match_release · bb_match_defer L7 arm.

**RBPPAIR FALSIFIED — DO NOT RETRY.** The obvious cure (mirror the α guard at γ/ω) was implemented, proven present (positive control: ROMAN loses `mov rsp,rbp; pop rbp` while main keeps it), then measured: m4 IDENTICAL BY SET, m3 breaks `1016_eval`. The reason: `rt_chain_enter` pins rbp for jmp-entry citizens the emitter's α guard excludes — a second, unledgered pin authority. The exit-class ledger is the correct fix.

**Instrument note:** A/B artifact is `out/libscrip_rt.so` NOT `scrip` — snapshotting the executable gives two binaries with identical md5 both loading current templates (vacuous A/B). Snapshot `.so`, select with `LD_LIBRARY_PATH`. `make` silently no-ops after `git checkout` of one template — touch the TU and re-verify.

---

## ⛔⭐⭐ PRIOR CURSOR — s22u (2026-08-01)

⭐⭐⭐ **WIREREG: DEFINE RETURN WIRES WERE CALLER STACK GARBAGE — CARVE-ERAD CASUALTY. m3 +5 · m4 +5 · ZERO BROKEN. SCRIP `2edd3497`.**

The role-3 IR_SAVE_RESTORE wire-adopt box read `[rsp+kt-24]`/`[rsp+kt-16]` for the γ/ω wires — bytes written by `xa_flat`'s jmp-entry prologue, which CARVE-KILL (s22o) deleted. With no writer, every DEFINE'd function returned through a wild jmp (roman: rc=139, ZERO output, γ wire = `0x7ffff4dba3d8`). **The wires never needed storage:** both call paths already do `lea rcx,<γ>; lea rdx,<ω>; jmp rax`, and wire-adopt is the FIRST box of the stub blob, so rcx/rdx are still live. Fix = read the registers directly. Marshal order load-bearing: rdi←rcx, rsi←rdx BEFORE the rdx/rcx overwrites.

Fixed (3/3 bare exec, both modes): `084_define_loop_call 1010_func_recursion 1013_func_nreturn 1014_func_freturn 213_indirect_name`.

---

## ⛔⭐⭐ PRIOR CURSOR — s22t (2026-08-01)

⭐⭐⭐ **UCLAIM MECHANISM LANDED AND COMMITTED — statement-extent claim at declined run head's α + owner-table resolver in `x86_frame_off`. COMMITTED AS VERIFIED NO-OP (4-arm crosscheck IDENTICAL BY SET). First task of s22u: one fprintf at choke apply vs hook to find what dropped `op_uclaim`.**

⭐⭐⭐ **MECHANISM PROVEN END-TO-END BEFORE IT WENT DARK (pre-operand-closure build):** `sub rsp,144` (claim), subject DESCR at resolved `[rsp+128/136]`, head quartet at `[rsp+64..88]`, `add rsp,144` on all three exits — claim and release balanced. Two designs falsified en route: (a) per-node claims (re-carve leak per backtrack retry); (b) γ-chase-only membership (blob OPERAND nodes kept ghost spellings, crashing after correct output). Landed cure = OPERAND CLOSURE: membership = γ-chase run + transitive operands.

**Instrument law:** `setarch -R` AND canonical runner grandchild-env both cushion the s22r envp-corruption class — use static census (ghost writes in .s) and fixed-invocation A/B, never pass counts. Numeric watermarks don't transfer across harnesses.

---

## ⛔⭐⭐ PRIOR CURSOR — s22s (2026-08-01)

⭐⭐⭐ **THE 15-PROGRAM CARVE-ERAD PAYOFF IS A GATE COMPOSITION. WATERMARK IDENTICAL-BY-SET AT OPEN AND CLOSE: m3 204/113 · m4 188/128/1 · DIVERGE 16.**

The 15 programs are ALL pattern statements. The mechanism is already written: `bb_match_head` pops the subject DESCR from TOS (`op_subj_cell`) and `bb_match_release` carries the ONE-MOV UNWIND (`mov rsp, RSP(op_fc_disp+8)`) — both gated on `fc_vread_fp(head) >= 0`, whose walk never runs because `subj_on` conjoins two default-off envs.

**Bare decouple FALSIFIED:** `subj_on` default-on arms the CONSUMER while the PRODUCER VAR keeps flat stores — ~52 pattern programs broken both modes, reverted. Producer-side gate UNLOCATED (suspect layout-freeze ordering). This is the ZTOS reader-frontier law: arming a reader whose producer still speaks flat displaces the READER by its own pop.

---

## ⛔⭐⭐ PRIOR CURSOR — s22r (2026-08-01)

⭐⭐⭐ **NON-POPPING ZETA SPINE IS THE DEFAULT. m3 199/118 → 204/113 · m4 186/130/1 → 188/128/1, BREAKING ZERO. SCRIP `f6ee055` (NOFC-ONE) + `259b9cd` (NOFC-DEFAULT-ON).**

`SCRIP_NOFC` was two edits in one: the value-spine half (fc_geom vlit grant suppression) is a VERIFIED NO-OP — the value spine is fully ZD-armed, zero unarmed nodes left. **100% of NOFC's delta is the ZW-1 universal-carve suppression.** Killswitch now `SCRIP_NOFC=0`.

⭐⭐⭐ **CARVE-ERAD payoff sized: `SCRIP_M4_HEADROOM=65536` — one `sub rsp,N` in main moves envp out of reach WITHOUT converting a reader. m4 188/128/1 → 203/113/1 (+15, ZERO broken), DIVERGE 16→1 (sole survivor 1016_eval). The TRUE correctness figure is BELOW 203 — passing programs under the pad are CUSHIONED, not correct.**

Multi-authority collapse: `zc_nofc()` is now ONE site tree-wide (was 4 template-local getenv copies); flipping `zc_nofc` alone would have rearmed the producer/consumer asymmetry s22l diagnosed. PROVEN TRANSPARENT (all four fail sets diff IDENTICAL) then flipped.

**Instrument law: NEVER report a SCRIP timing delta from one run. Three runs minimum, report the spread.**

---

## ⛔⭐⭐ PRIOR CURSOR — s22q (2026-08-01)

⭐⭐⭐ **m3 ONE-SHOT BRIDGE PARITY FIX. m3 73/244 → 199/118 (+126, ZERO regressions). DIVERGE 125 → 13. SCRIP `150e903e`.**

m4 used `jmp main_α` (rsp ≡ 0 mod 16 at α); m3 used `call *%rax` (pushes 8 more) → α arrived rsp ≡ 8 mod 16 → SIGSEGV in the first C routine using `movaps`. **Fix = ONE CONSTANT:** `rt_outer_call`'s adjuster is 16, not 8.

**Localization method:** break on the C sink the graph calls, read `rsp % 16` at entry in BOTH modes. m3 = 8 → SIGSEGV; m4 = 0 → passes. The C-side `core_lib_init` calls in the same m3 process measured 0 — that separates "graph is skewed" from "runtime is broken."

**m3 IS CUSHIONED, NOT CORRECT** — m3 headroom ~20KB (deep C driver frames absorb stray writes), m4 headroom 344B (jmps from main, then argv, then envp). DIVERGE was partly measuring HEADROOM.

⭐ **ENVP CORRUPTION CLASS:** `__environ[0]` = `0x3` (a DESCR type tag written by `[rsp+568]` against 344B headroom). The ~1054 unarmed readers are NOT merely reading a dead region — they are WRITING THROUGH LIVE PROCESS STATE. **DO NOT RE-CARVE** — convert the readers.

**Static triage:** max `[rsp+N]` in .s vs 344B threshold — ~76 of m4's 130 failures share ONE authority; ~54 are different problems. Monotone progress metric: watch the >344 bucket empty.

**DO NOT re-carve with a big `sub rsp,K` cushion in main.** That is the whole-graph carve re-entering through the driver's door.

---

## ⛔⭐⭐ PRIOR CURSOR — s22p (2026-08-01)

⭐⭐ **ONE-SHOT BRIDGE + NON-POPPING WHACK. m4 64/252 → 186/130 (+122). SCRIP `05d250bd`.**

Three atomic changes: (1) `jmp main_α` (not call/ret); (2) outermost box owns its γ/ω as glue — whack + exit; (3) `bb_glue_outer_whack()` gated by `bb_glue_framed_enter()`. DIVERGE 15→125 expected (m4 changed exit path; m3 still returns eax to C).

**The epilogue was emitting the γ/ω port landings** — deleting it dropped m4 to 0 PASS/317 SKIP. Deleting `xa_flat_epilogue_str` (270 lines) + wrapper + dispatch + decl + enum, zero refs tree-wide.

---

## ⛔⭐⭐ PRIOR CURSOR — s22n (2026-08-01)

⛔⛔ **EMERGENCY HANDOFF — FLAT PROLOGUE EMITTER DELETED. m3 276/41 → 77/240 · m4 276/40 → 5/311/1. CORPUS RED BY DESIGN. SCRIP `983f24d3` + `ba46bb5e`.**

Lon directive ×3: DELETE `xa_flat_prologue_str`. 311 m4 failures is ONE missing authority. Revert = `git revert ba46bb5e 983f24d3`.

**The function was ONE authority for THREE entry shapes:** (1) jmp-entry carve — `sub rsp,K` + wire header + rbp pin + zero-fill (the corpse); (2) `GEN_RESUMABLE` heap-frame adopt (generator β-resume); (3) `STMT_FRAME` 8B parity pad (the design-of-record per-BB shape). Deleting the function took (3) out with (1). **RE-LAND IS STMT_FRAME ALONE AS ITS OWN FUNCTION, NOT A REVERT.**

**Instrument law: delete C functions by BRACE-MATCHING, never line regex.**

---

## HISTORY INDEX (one-liners; full text = FINDING docs + git)

- **s22m** (08-01) CLAWS5 + JSON oracle-match. Treebank root cause bracketed: H11 Pop_list rsp rose +104 (mod16=8), SIGSEGV glibc movaps. gdb available (`apt-get update && apt-get install -y gdb`).
- **s22l** (07-31) NOFC symmetric, +33 programs (ALL pat_*), m3 276/41 → 308/9. `SCRIP_NOFC` still off by default. ZD-SR (IR_SAVE_RESTORE roles 1/2/3 admitted, transparent). Attribution correction: the 33-program win is the CARVE SUPPRESSION, not the non-popping consumer read. Instrument law: run under `setarch -R`; ASLR is ±2 noise on every m4 figure.
- **s22k** (07-31) K authority collapsed to one site (was three). ZD-9 define-stub admission (`g_flat_frame_floor > 0` discriminator). Watermark m3 276/41 · m4 276/40 · DIV=3.
- **s22j** (07-31) ALT pair-defs were beta entries — every alternation segvd. `X86H_DEF_PAIR` new site code; `op_pair_rejoin` flag. m3 232/85 → 241/76, ZERO regressions.
- **s22i** (07-31) ZD-7 Slice 2 (IR_CALL builtin family). IR_CALL decline census 519→58. SIZE('hello')→5 ✅.
- **s22h** (07-31) ZD-7 Slice 2 engineering: PROC_STAGED exclusion mandatory (measured); planner changes require template arm atomically; `lea rsi` encoder gap identified.
- **s22g** (07-31) ZD-7 Slice 1 engineering: TAG-SAFE callee accessor; full callee partition; IR_CALL runs are not single-node; naive ZD arm −63 m3 (FRQ adds depth, wrong address).
- **s22f** (07-31) NON-POPPING RUNG OPENED. Five pops are Gen-1 FC, not STF consumers. Gate = ZD-7 (IR_CALL). FC census 163 firings / 29 programs; NOFC=1 breaks 20 (call-bearing statements). STF arming widen is the WRONG gate.
- **s22e** (07-31) LP-2 landed (RPO walk + zd_plan above xa_dispatch). `flat_all_zd` exact. Instrument trap: committed `.s` artifacts for claws5/json are ASSEMBLER-REJECTED at HEAD and will not regen until codegen defect fixed.
- **s22d** (07-31) LP-1 landed (BFS pre-prologue verdict). arithmetic.sno carve 248→8. Zero crosscheck programs fire.
- **s22b** (07-31) STF-UNFLIP (`flat_stmt_frame` default ON→OFF, SCRIP_STMT_FRAME=1 opt-in) + WPOP-1 (`!op_zres` guard at binop/unop sites). Crosscheck EXACT both ends, fail sets IDENTICAL BY SET both modes. **The fail edge was over-freeing by 32; the carve was absorbing it.** Carve deletion will EXPOSE every over-free it currently swallows.
- **s22a** (07-31) RPO-FILL v2 (post-order + per-root reversal; preorder trap: wholesale reversal loses `entry`) + ZGPOP-STF (zeroed at planner choke, not emission site). STF-armed 31/318. Consumer pops NOT deleted (serve the ~287 unarmed graphs). `add rsp,ΣK` FORBIDDEN — the seed's own annotation: "ZERO hand-counted pops."
- **s21x-z** (07-31) Four findings, zero commits. STF-FLIP is ceremony (HKQ never fires, 0/317). ZD-5a-PRE vacuous (cannot reach match-bearing graphs). Consumer pops violate port discipline. `.s` scramble is BFS fill.
- **s21x-y** (07-31) Value spine fully closed. ZD-2m IR_FIELD_VAR (last value-spine blocker). STF-FLIP (flat_stmt_frame OFF→ON). Watermark m3 232/85 · m4 229/86/2 · DIV=1 — held EXACT through s22b, s22c, s22r, s22u, s22v. Census 100% protocol: CALL 519 · MATCH_HEAD 247 · SAVE_RESTORE 18 · GOTO_DEFERRED 6.
- **s21x-x through s21x-v** (07-31) ZD-2 verdict widening complete (all value-spine kinds). ZD-1 landed (RSP FORTH per-BB stack, default-ON). ZD-2h retired (SNOBOL4 has no lexical locals). Carve debt re-derived live: 1054 sites / 109 templates, UNMOVED — ZD arms are additive, legacy arm survives beside each.
- **s21x-r** (07-30) STF defect was process-scope flag (ZLEAK-1/2). Armed set (31) and m4 regression set (41) DISJOINT. Declined-graph sweep 285→0: ALL-OR-NOTHING per graph now holds corpus-wide. Law: NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME.
- **s21x-q through s21x-e** (07-29/30) ζ-cell spelling sweep closed. ZTOS-1/2 sliding offsets. GLUE-3/4 wired. ZREL-1/2. LEN-GHOST fix. CALL2BB slices 1/2/3 landed. GOTO-ERAD survey. ZD whitelist widening beginning.
- **s186** (07-27) SN4-RTX split to its own file. Shrink-pass lesson: 8 live rungs deleted by prior prune, recovered from `950e6a9f`.

---

## ⛔ LON DIRECTIVE — s21x-c (2026-07-29): DESIGN OF RECORD

1. Every BB allocates its own storage: ONE `sub rsp,K`.
2. Sliding offsets, RSP-indexed; emitter tracks live depth at compile time.
3. RSP-only until a genuine brick wall, then RBP dance.
4. **Four RBP constructs: STATEMENT · FUNCTION · ARBNO · FENCE1.** Law 7: DEFINE's FUNCTION = IR_CALL's frame dance only.
5. Named anti-pattern (roman): `sub rsp,1344` whole-graph carve. WRONG.
6. DEFINE, constant-folded, emits exactly TWO BBs: IR_SAVE_RESTORE + IR_CALL.
7. **SCOPE LAW: statement level ONLY. No function-level processing.**

**DYNAMIC BOX GLUE (s21x-f):** any BB graph (one entrance, four ports) invokable by a DYNAMIC BOX. (A) DYNAMIC-FLAT: α `jmp [entry_cell]`, β `jmp [resume_record]`, γ/ω = supplied wires; zero frame. (B) DYNAMIC-FRAMED: + RBP/RSP dance. First customer: IR_MATCH_PATREF.

---

## ⛔ LAWS & TRAPS (binding; DO NOT RETRY marked experiments)

- **ζ GATE IS "ZERO MID-BODY CELL", NOT "ZERO RSP":** residual raw-rsp sites are classified NOT-ζ. Four legitimate classes: GLUE · C-ABI ALIGN · CSTACK SWAP ARM · PROLOGUE.
- **NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME:** `static int on = getenv(...)` inside a function taking `IR_graph_t*` is the defect signature. Cost 41 m4 programs.
- **DECLINED-GRAPH SWEEP before any default-flip:** every `live=0` graph must be byte-identical between regimes. Non-vacuous: check armed graphs still differ.
- **CENSUS UNITS:** always state the env with an armed count.
- **SUSPENDED-CELL (s21x-l):** no rsp cell may suspend across γ above an ARBNO/DEFER extent.
- **RESULT-IS-THE-CELL (s21x-k):** consumer overwrites the source cell IN PLACE, net-zero.
- **SOLE-CONSUMER FENCE (s21x-j):** subject registration requires IR_MATCH_HEAD be subjval's ONLY operand consumer.
- **UNION-TAG (s21x-g):** IR_t sval/ival/dval are ONE union — normalize at single dispatch point; never include IR_SAVE_RESTORE in op_sval promotion whitelist.
- **NODE-EXACT HANDOFF (s21x-g):** emission order is not a contract; key by CALL NODE POINTER.
- **STUB DISCRIMINATOR (s21x-h):** DEFINE-stub key = `g_flat_frame_floor > 0`.
- **DEFER-DEEP LOAD-BEARING (s197):** do NOT drop IR_MATCH_DEFER from deep-arrival until recursive-defer programs pass.
- **s206 DO-NOT-RETRY:** `x86_fc_cells()=(FORTH||HEAP)` predicate flip → wild jumps.
- **SCAN-RETRY = 5th rbp member (s196):** `&ANCHOR` is a runtime keyword; no static classifier retires the pin.
- **STALE-BINARY TRAP (s21x-j):** `[ -x scrip ]` is not a build check. Grep both make logs for `error:`.
- **op_flat_disp RIDES EMISSION ORDER** — any layout change must prove per-chain disp locality first.
- **CENSUS SHELF LIFE:** re-run, never cite. HEAD-STAMP every measurement.
- **COMPARE m4, NEVER m3:** `test_string`/`213_gc_exhaustion_churn` are harness-only flakes on m3. Diff fail sets BY SET, never by count.
- **RBPPAIR DO-NOT-RETRY:** mirrors the α guard at γ/ω, proven present, breaks `1016_eval`. The second pin authority is `rt_chain_enter` (CLASS C graphs).

---

## ⛔ PENDING LON RULINGS
- **FOUR-modes confirmation** — `ZC_STORAGE_{FRAME_R12,FRAME_RSP,CELL_STACK,CELL_HEAP}`.
- **Replacement-splice ruling (s21x-j):** splice reads the cell, or write-through — retires sole-consumer fence for replacement class.
- **SRC-ORDER-LAYOUT ruling A/B/C.**
- **RBP-SHED-7:** ⛔ blocked.

---

## LADDERS

### ⭐⭐ LADDER ZD

**CENSUS (s21x-y, re-run after every rung): 790 declined, first-blocker ranked — `IR_CALL` 519 · `IR_MATCH_HEAD` 247 · `IR_SAVE_RESTORE` 18 · `IR_GOTO_DEFERRED` 6. 100% PROTOCOL — value spine has no remaining members.** ⚠ Clearing a cheap blocker PROMOTES the expensive one behind it; a decline count is a frontier reading, NEVER a backlog.

- ✅ **ZD-2 COMPLETE** — all value-spine kinds ride the cells (LIT · VAR/ASSIGN-global · UNOP · BINOP · COERCE · CMP_TEST · KEYWORD_SNOBOL4 · SUBSCRIPT · DEREF · ASSIGN_VAR · FIELD_VAR). Declines 1060→790.
- [ ] **ZD-2c** `bb_binop_relop` — zero first-blockers today; arm when a widened statement declines on it. (`IR_FIELD_GET`, `BINOP_XREP`: vacuous by construction — Icon/Raku-only, zero SNOBOL4 customers.)
- [ ] **ZD-2g** UNOP closure (NULL/NONNULL/NULLTEST_VAR) — never first-blocks today.
- [ ] **ZD-3** Legacy arm retirement — per kind fully covered by ZD arm, delete vfc/vfcu/vfcb/vfcc + the `op_fc_disp` registration.
- [ ] **ZD-4** Lift the jmp-entry decline — `SCRIP_ZD_JMPENTRY=1` hatch; diff 1019's fragment .s on/off; fix; delete gate.
- [ ] **ZD-5 MATCH FAMILY (247) — the 85/86-red target.**
  - [ ] **5a-PRE** Ledger the STFH-48: `bb_match_head:32` emits `IF(stfh(), x86_zclaim(48))` but `zw_carve_k` returns 0 for IR_MATCH_HEAD → second unledgered allocation authority. Enumerate non-HKQ `[rsp+off]` refs first.
  - [ ] **5a** Linear-match bridgehead (head → LEN/POS/RPOS/SPAN/ANY/NOTANY/REM/TAB/RTAB → release; no alt/arbno/fence/defer/capture).
  - [ ] **5b** Planner extension for branching runs (alt, arbno cycles, defer). ⛔ The ONE genuinely design-tier item.
  - [ ] **5c** Per-template conversions, smallest-first.
- [ ] **ZD-7** `IR_CALL` (519) + `IR_SAVE_RESTORE` (18) — the protocol rung, law 4's other genuine RBP citizen.
- [ ] **ZD-6** Standalone: 130/131 clean-HEAD segv · DIV member W04_arbno_basic · bb_op_name entries for ops 14/73–77.

### GOTO-ERAD
- [ ] GE-0 census; GE-1 monitor-tap relocation (prerequisite); GE-2 survivor unprotection; GE-3 SNOBOL4 lower-side; GE-4..7 per-language; GE-8 emitter sweep; GE-9 enum deletion + gate.

### RBP-SHED (order 3→1→2→4→5)
- [ ] SHED-3 REC-PIN-OWN: move stale-emission globals to per-graph g_emit mirror at emit_chain choke.
- [ ] SHED-1 NPARAMS: retire `g_flat_outer_nparams>=1` pin conjunct for depth-static graphs.
- [ ] SHED-2 ABORT-REBALANCE: route ABORT through statement fail exit.
- [ ] SHED-4 HOOK-ENCODE: scanhit/scanfail hooks through x86().
- [ ] SHED-5 ALIGN-DANCE-DELETE: retire transient push-rbp alignment window.

### ✅ FB-STMT RE-ARM — CLOSED s22c (DEFAULT-ON, SCRIP `bdd6c23b`). Ceremony unchanged · data refs −44% · IDENTICAL BY SET both modes. Residue: pat/gen blob class excluded by construction at emit.cpp:2650 — extension shares surface with ZD-5.

### SRC-ORDER-LAYOUT (s21x-b): statement layout order scrambled (BFS fill). Awaiting ruling A/B/C. Gates: watermark, census, .s regen ×5.

### CARRIED OPEN: MARKER-CAPTURE · r9 park-address anchor · arm-quad OVERLAY · fc_cond FIRST-WINS · SYM-VIS-M3 JIT map · Icon generator-scan FORTH cells.

---

## ↗ MOVED OUT / SUPERSEDED
- **SN4-RTX** → `GOAL-SNOBOL4-RTX.md`. RTX-11/12 NOT concurrency-safe.
- **ZHEAP / CELL ladder** — superseded by s21x-c design of record. ZC_PORT_HEAP rbx α-carve stays dormant-ratified (HZ-1).

---

## ⛔⭐ WATERMARK OF RECORD (s22x close)

| runner | m3 | m4 | DIVERGE |
|---|---|---|---|
| **crosscheck 318, TIMEOUT=8** | **220/96/1** | **217/98/1** | **3 {170, 1016, test_stack}** |

Harness: `/tmp/xc.sh` (lean resumable 2-arm runner from .github, bare container exec). Prior record s22w: 217/99/1 · 214/101/1 · DIV=3 — REPROVEN at s22x open before any edit; s22x +3/+3 (GLUE-SYM proven byte-identical 0/318; CAS-MARKER-CARRY did the +3).
