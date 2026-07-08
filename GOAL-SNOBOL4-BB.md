# GOAL — SNOBOL4 on the shared BB spine
AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude   OPENED: 2026-07-03 · SN4-PAT + RE-LIGHT folded in 2026-07-06 · BB-OWNED-ζ set TOP PRIORITY 2026-07-06 · MAJOR REDUCTION 2026-07-08 (Claude Sonnet 5) — completed rungs deleted per RULES.md handoff step 1; verbatim history in git log and old handoffs under `.github/archive/` if ever needed.

## ⛔ STANDING POINTER — read `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` BEFORE writing/editing ANY `x86_asm.h` encoder or `xa_*`/`bb_*` template
A new encoder is NOT exempt from that doc's R2/R7/R9/R10 for being new: ONE `x86(...)` concatenation, consumed via `bb_emit_x86`, never a hand-written `IF(MEDIUM_TEXT,...)+IF(MEDIUM_BINARY,...)` pair (the "forbidden shape"). Mirrored in `PLAN.md`'s BB-CODEGEN DESIGN SET (session-start step 7).

---

## ⚠ SESSION STATE (Claude, 2026-07-08, cont.) — α-DEF UNIFICATION **LANDED** ON BRANCH `alpha-def-unification-wip` (`8dc12d9e`); ZLS2 ARENA SCAFFOLD LANDED (`c1ff1b75`); BRANCH AT WATERMARK, READY TO MERGE PENDING LON REVIEW + PUSH (credential)
Root cause fixed as scoped: `emit_drive` 5th param carries `lbls[i]`; `DRIVE_FILL(nd,a,s,f,b)` sets `lbl_α/lbl_α_p` directly; `bb_fill_alpha` off the drive path. **PLUS eight def-less MEDIUM_BINARY arms the original sweep missed** (bcps_bin/bcps_bin_gen; bcws_slot/concat/int; byname/byname_gen/gvar_userproc) **and two TEXT-gated α hoists** (cell_choice, disj) — found via the m3-only unresolved-α signature (TEXT resolves labels by NAME, BINARY by OBJECT; that asymmetry is the diagnostic for any future straggler). Verified: m3 252/276, m4 251/9/16, DIVERGE=1 (1017); icon 12/12×2, prolog 5/5×3, polyglot 2/2×2. TMP-TRACE removed.

**ZLS2 ARENA (Lon directive this session — register/design decisions RESOLVED):** ONE register (r12), arena grows **DOWN**; α = `sub r12, K`, single-exit ω = `add r12, K` — down-growth makes BOTH constants the box's OWN emit-time frame size (up-growth needs the runtime predecessor's, unknowable at emit time). β needs no reload in pure LIFO (predecessor's pop lands r12 exactly on the resumed frame); bulk unwind (FENCE) reloads from a saved mark. ARBNO variable data = per-iteration mini-frames pushed below, no slide (v1 contiguous — body dies before append; v2 keeps rt_zcol). Six-register contract confirmed from `bb_create.cpp`: r12=ζ r13=subject r14=cursor-save r15=len-save rbx=GVA rbp=match-family scratch. **C-STACK (Lon's Eureka, analyzed): sound in the END STATE ONLY** — today the proc trampoline re-enters emitted code, so a suspended generator's live frames would sit below rsp after the trampoline pops = clobbered; under the 4/28 direct-jmp ucall convention Lon's no-interleave caveat holds by construction, rsp becomes the frame pointer, the `and rsp,-16` idioms delete, r12 AND rbp free up, and libgc scans the C stack for free. The discipline is backing-agnostic: built on r12 now, rename to rsp when the trampoline retires. (sbrk = the heap, not the stack.) **LANDED SCAFFOLD (dormant — `SCRIP_ZETA_PORT=2` + per-node grant both required):** `rt_zls2_init/lo` (`zeta_alloc.c`, mmap NORESERVE `ZC_ZLS2_MB=512`, GC-rooted once), `g_emit.op_zls2_bytes` (zeroed at every DRIVE_FILL), α-hook in `x86_deflabel`, `x86_zls2_free()` for template-placed true-exit frees (NEVER central — six-decoy-ω finding). NEXT: first consumer = ARBNO per-activation frame (save-slot-in-frame for the r12-repoint-vs-siblings dance), MALLOC+ASan proving per ZB-ACT-0 method, then trampoline retirement → rsp.

---

## ⭐⭐⭐ TOP PRIORITY RUNG: BB-OWNED-ζ — per-BB self-allocating memory (Lon pivot)

**THE IDEA:** a GC distinct from SIL mark/slide/adjust (§6, `GOAL-IR-IMMUTABLE-EMIT.md`), marked by BB entry/exit instead of heap-reachability tracing. α allocs + sets R12 + saves for β; β loads only (no alloc); γ untouched; the jump to ω out of a construct's TRUE exit is the free. A Byrd Box is pure-functional — one entry-family, one exit-family — so block liveness is a structural fact of control position, not something a tracer discovers. Start with `ZC_ALLOC_INFINITE` (proves wiring) before anything reclaims. Same rung as ZB-ACT-0/1/2 in `GOAL-IR-IMMUTABLE-EMIT.md`, merged here; ARBNO is the first construct (documented casualty of the old single static slot; `bb_match_arbno.cpp` already exists).

**⚠ ω is NOT uniformly "the death."** Verified directly against `bb_match_arbno.cpp`: it emits SIX `jmp "ω"` sites across six roles (v1 roles 0/1/2, v2 roles 3/4/5), and only TWO (role 2, role 5) are the construct's genuine irreversible exit — the other four reuse the `ω` port name for internal control flow (body-entry, refuse-and-defer). Hooking `port==OMEGA` universally at the central `x86_jmp` dispatch would free on the internal jumps too; under a bump/LIFO backing this is **silent corruption downstream**, not a crash at the bad instruction.

**STATUS OF THE CLASSIFICATION SIGNAL, `op_omega_is_death` (emit.cpp ~1514, field comment emit.h ~398):** computed per-node in `codegen_flat_chain_body`, intended to be true iff an ω-edge falls through to the chain's own outer `lbl_ω` (never resolved inside the local chain). **Session finding (Claude Sonnet 5, 2026-07-08, `SCRIP_OMEGA_DIAG` trace, verified not inferred): this does NOT correctly distinguish role 2's true death in at least one real case.** `IR_MATCH_HEAD` (the pattern statement's own fail-continuation target) can sit INSIDE the same `codegen_flat_chain_body` chain window as the ARBNO node whose ω targets it — so `omega_resolved=1` fires for role 2 too, giving `op_omega_is_death=0` for the one case that should read 1. The formula as written treats "target found among this chain's own nodes" as sufficient for "clean internal handoff," but landing on the chain's own fail-continuation node is not the same thing as landing on a fresh activation's α. **Not yet fixed — flagged, not patched on a hunch, per this project's own methodology.** The free-call this signal would gate (`x86_zeta_free_call`) stays disabled regardless (it frees r12 itself, wrong for ARBNO's carrier-based design) — this finding doesn't change that, it means the signal can't yet be trusted to drive any future central-hook free either.

**MITIGATION LANDED THIS SESSION (Claude Sonnet 5, 2026-07-08) — single-exit label, sidesteps the classifier instead of fixing it.** `bb_match_arbno.cpp` role 2 (v1 exhaust) now `def L(9)` immediately before its true-death `jmp "ω"` — an ordinary local integer label (auto-namespaced `.Lx<x86_uid>_9` per node, the existing `L(n)`/`x86_internal_name` mechanism, NOT a new port; RULES.md's FOUR-PORTS rule is untouched). Role 5 (v2 exhaust)'s existing `L(2)` def is now documented as the same kind of marker (was already there, undocumented). Gives anything auditing the emitted stream — disassembler, future central hook, a person — one unambiguous, greppable address for "this activation is provably dead," independent of the broken chain-membership check. Verified: `.Lx<uid>_9:` appears exactly once per ARBNO-exhaust node instance in compiled output, nowhere near roles 0/1. Zero regressions (crosscheck byte-identical to pre-change watermark below). Does NOT yet wire the central `x86_jmp` hook to consume this label — that's real design work (how does the hook, which only sees the port at dispatch time, learn a preceding local label was just defined?), not attempted.

**CONFIRMED WORKING, this session (Claude Sonnet 5, 2026-07-08), by direct trace not code-reading alone:** under `SCRIP_ZETA_SELFLOAD=4` (`ZC_SELFLOAD_ALLOC`), every ARBNO α-invocation gets exactly one alloc and exactly one free — either via role 2's own true-ω (`x86_arbno_role2_free`, when that activation individually backtracks to exhaustion) or via `IR_MATCH_RELEASE`'s `rt_zls_release_to`-from-mark backstop at `sJ` (when the activation succeeds and leaves via the pattern's success join instead of ARBNO's own ω). **This closes the previously-open "success-path leak"** (an ARBNO that never reaches its own ω was leaking its block) — closes it via the chain-walk itself (`rt_zls_release_to` walks `g_zls_cur` back to the mark, freeing everything above it) rather than needing a per-statement list, because the singly-linked alloc chain already IS that list. Verified via `SCRIP_ZLS_RELEASE_TRACE=1`/`SCRIP_ARBNO_STEP1_TRACE=1` paired event-by-event on hand-written v1 and v2 probes; repeated α-hits on backtrack-heavy probes are legitimate independent unanchored-retry activations (SPITBOL retrying the whole pattern at each cursor position), not a bug. Crosscheck run with the flag on: byte-identical fail-list to flag-off (mode-invariance gate satisfied).

**HONEST SCOPE, unchanged:** default-OFF (`ZC_SELFLOAD_OFF`), ARBNO-only, v1-only (phases 0/1/2; v2's phases 3/4/5 use the separate, already-working `rt_zcol_push` per-iteration COLLECTION mechanism, untouched by any of this). Extending beyond ARBNO to the other 20 `bb_match_*` templates, and turning this on by default, is real work still ahead — this session declined to add ARBNO-shaped alloc/free calls to a second template (`bb_match_arb.cpp`) directly inline, after determining that duplicates ARBNO's own already-disabled-for-good-reason central-hook approach rather than genuinely generalizing it (reverted; see git history if the false-start reasoning is ever needed).

**STEPS (unchanged from the ZB-ACT-0/1/2 ladder):**
1. Per-BB self-alloc, `ZC_ALLOC_INFINITE` — **substantially done for ARBNO v1** per the confirmation above; extending to other templates is what remains.
2. Real reclamation — flip backing to `BUMP_LIFO` (already the actual default per `zeta_choices.h`), prove under MALLOC+ASan first, confirm byte-identical to step 1.
3. Chain-coalesce optimizer pass — find chains of self-allocating BBs with single α-entry/single ω-exit, share ONE R12. Not started.

**r12 CANNOT be repointed by a per-construct self-alloc without breaking every sibling box** — confirmed from the implementation side: `FR(off)` is `[r12+off]` for the WHOLE function, shared by every box in it. STEP 1 as built carries the pointer via the runtime-side carrier instead (`rt_zls_arbno_step1_store/load`, one static per construct, deliberately NOT shared across constructs — e.g. ARBNO and a hypothetical ARB carrier must stay separate, since `ARBNO(ARB)` would otherwise have the inner alloc stomp the outer's still-pending pointer). Correct for sequential re-entry only, not yet nested/concurrent activations of the same node — explicitly future work.

---

<!-- ════════════ SNOBOL4 TEST-SUITE LADDER CRAWL — live head ════════════ -->

## ▶▶ CURRENT STATE — CRAWLING THE TEST SUITE

**CROSSCHECK WATERMARK (re-derived 2026-07-08, Claude Sonnet 5 — matches the recorded SCRIP `ebfc7009`/corpus `4f6f2943` watermark byte-for-byte, flag-on and flag-off):** `bash scripts/test_crosscheck_snobol4.sh` mode-3 **252/276 (24 FAIL)**, mode-4 **251/9/16 (9 FAIL, 16 SKIP)**, **DIVERGE=1** (a newly-exposed pre-existing mode-3/mode-4 disagreement on undefined-function-call handling, not a regression — see NEXT BRACKETS #2).

**DOCTRINE:** SNOBOL4 rides the same pipeline as Icon — `sno_parse_ast → lower_sno_stage2 → shared optimizer → ir_drive_slot_assign → the ONE language-blind emitter → mode-3/mode-4`. SCRIP follows SPITBOL semantics; oracle = `/home/claude/x64/bin/sbl -b`. Every statement: (1) build subject; (2) build pattern; (3) perform pattern; (4) build replacement; (5) perform replacement — pattern stages are now live (SN4-PAT family below).

**METHOD:** STATIC-FIRST → ONE STAB → THEN MONITOR. Read `.ref`, run both modes, reason from `.s`+IR+templates to the land mine; one targeted fix; verify both modes vs `.ref`. Escalate to the 2-way IPC sync-step monitor (bracket first-divergence↔last-agreeing, gdb spin-counter breakpoint, single-step to the land mine) only if the stab fails.

**NEXT BRACKETS (in order):**
1. **FENCE-in-ARBNO-body** (116/142/145/151) — both `sno_pat_deterministic` and `sno_pat_v2_ok` refuse the instant they see FENCE in an ARBNO body; confirmed intentional (FENCE was never scoped to cover ARBNO). Real design question: which fail-target does a sealed element inside iteration N point at — the statement's `fJ`, or iteration N's own local retry? Its own rung, not a quick stab. `151` is a deliberate negative discriminator (must keep passing).
2. **`1017_arg_local` DIVERGE** — the checked-in `.ref` was simply wrong (real oracle fails at assertion 1; `ARG`/`LOCAL` are unimplemented builtins). Regenerated `.ref` (corpus `4f6f2943`); mode-3 now matches it with zero code changes. Mode-4 does NOT match — produces a different hard-failure style for the same undefined-function call. Mechanism not yet understood (grepped source, found nothing — may be a baked `.rodata` string). Not a regression; mode-3/mode-4 always disagreed here, the stale `.ref` just hid it.
3. **062/063 (capture) — `SUBJECT PATTERN = REPL` splice.** Stages 4-5 of the 5-stage model have no implementation yet. Scoped, well-understood, not a wiring gap.
4. **word1/word3/cross/wordcount** — four distinct bugs (capture-into-OUTPUT-keyword; mid-chain-generator capture; wrong-output-undiagnosed; unimplemented "tree kind 31" expression form).
5. **1011_func_redefine, 1013_func_nreturn, 1015_opsyn** — each a new capability (DEFINE in expression position; NRETURN-result as lvalue; OPSYN-rebound operators through the lowerer), not a wiring gap. Each its own rung.
6. **213/082** — `indirect_name`/`keyword_stcount`, long-standing, not yet root-caused.
7. **124/143/140/141** — EVAL-adjacent/compound-pattern probes, not yet individually triaged.
8. **test_case/test_stack/test_string** (corpus include-library) — likely depend on OPSYN/splice landing first.

**FINDINGS PARKED (own rungs, not faked):** FINDING-A EAGER-ASSIGN (`.` assigns at subpattern-success even on eventual failure; the `rt_dcap_*` deferred-capture protocol is orphaned — wire at match entry/success/fail); FINDING-B SEQ-CHAIN-THROUGH-DETS (a deterministic element between the fail point and a left generator blocks resume; the SN4-PAT-BETA-CHAIN rung); FOLD BLOB TIER (`IR_REF_INVARIANT` — string tier landed, blob tier remains).

---

## ⛔ SN4-PAT — SNOBOL4 PATTERN MATCHING (the feature spine)

Non-pattern SNOBOL4 subset complete (literals, vars, keywords, `.NAME`, arith+concat, unary, `$`, subscript/DEREF, calls, gotos/labels, every assignment LHS form, DEFINE/DATA/OPSYN). Pattern matching genuinely needed new opcodes (SNOBOL's floating-needle-over-a-pattern model isn't Icon's anchored SCAN family) — a RECONSTRUCTION of a family amputated at `8de0fb46`, design recovered from git (parent `41b53078`).

**THE MODEL:** `IR_MATCH_*` (28, matchers, inline needle, γ=success/ω=failure wiring) + `IR_PATTERN_*` (STITCH boxes only — per-element pre-D7-era builders are ABANDONED, do not resurrect) + `IR_REF_INVARIANT` (folded-constant sealed blob for VARIANT-free subpatterns).

**LANDED (SN4-PAT-0 through SN4-PAT-DEFER-CALLOUT v1) — all rungs through the full ladder below are `[x]` complete, verified vs SPITBOL oracle, zero regressions at each step. Compressed to what a future session needs, not the forensic trail:**
- Enum family re-added (34 members), templates revived one at a time (LEN → LIT → ANY/NOTANY → SPAN → BREAK/BREAKX → TAB/RTAB retrofit → POS/RPOS/REM/ARB → CAT (node-free, edge-threading only, no template) → phase-0 capture SAVE → ALT → FENCE (node-free fail-retarget, not a β→ω box) → ARBNO v1 (deterministic body, 3-phase, no COLLECTION) → ARBNO v2 (generator body, per-iteration COLLECTION via `rt_zcol_push`) → EXPRESSION datatype (`*EXPR`/EVAL, DT_X) → DEFER-CALLOUT v1 (stored true-PATTERN values as AOT-compiled `bb_box_fn` blobs, DT_P).
- **Load-bearing findings to remember, not re-derive:** `_.x86_scratch_off` was read by five templates but written nowhere until SPAN's rung granted it in `ir_drive_slot_assign` — same landmine recurs for any new scratch-slot consumer, grant before wiring. `IR_lit` is an anonymous union (sval/ival/dval overlap) — never write two members on one node (silently zeroes the other, caused real bugs). The match-family `push rbx; mov rbx,rsp; and rsp,-16` C-call idiom poisons the GVA base if the callee re-enters emitted GVA-reading code — swept to `rbp` in touched templates, others inert only while their callees never re-enter emitted code. The emitter's flat chain-BFS worklist originally followed ω only for BINOP/CALL/SUBSCRIPT/generator-kind, missing ω-only backtrack targets (ALT RESTORE) — fixed to follow ω for the whole match-family opcode range.
- **`SN4-PAT-DEFER-CALLOUT` NEXT-SESSION BRACKETS still open, in order:** (1) fresh-frame WIP patch exists (`.github/WIP-sn4pat-defer-freshframe-2026-07-06.patch`) but introduces a DIVERGE=2 (word2/word4) — a real inter-mode lifetime issue, not landed, needs bracketing before landing; addendum suggests the "lifetime divergence" framing may be wrong (an `INPUT`-at-EOF failure-propagation hypothesis instead — re-check before assuming the patch's own diagnosis). (2) DT_P through user functions (063-066 fence_fn cluster) — a DEFINE'd function returning FENCE(...) needs DT_P to survive call/return. (3) β-resume across the blob boundary (074/W07 cursor cluster) — outer backtrack can't re-enter a returned blob's internal generator yet. (4) remaining stragglers: 1011/1013/1015/1017, 082/213, test_case/stack/string+word/cross.

**PARK-NEVER-DELETE (standing directive, Lon) — applies repo-wide, not just this file.** Park parsed-out language code out of the Makefile; never delete it (the `8f3e4b23` "kept intact on disk" precedent). `src/lower/lower_snobol4.gz5-parked-41b53078.c` holds the recovered pre-GZ#5 pattern lowerer (1402 lines) — any dead-code sweep must exempt `*.gz5-parked-*` files and the templates-on-disk inventory (23 `bb_match_*`, 5 `bb_pattern_*` + stubs — all API-current, kept intact by `8f3e4b23`).

---

## SNOBOL4 RE-LIGHT LADDER — SNOBOL4 on the post-GZ#5 spine

**SCOPE NOTE:** relocated here from being cross-referenced; the Icon-only hard rule elsewhere is Icon-climb-scoped and doesn't by itself govern this ladder — flagged, not silently resolved.

**Constraint (still binding): `IR_e` is FROZEN AGAINST ADDITIONS for this climb** (deleting unused ops is directed, not forbidden). One authorized carve-out already landed: `IR_KEYWORD` → `IR_KEYWORD_ICON`/`IR_KEYWORD_SNOBOL4` split (case-fold keyword sets genuinely differ, SNOBOL4 vs Icon — classify-by-name doctrine, not an accidental new-op need). If a rung seems to need a new opcode, the rung is wrong — find the existing-vocabulary lowering or park the program.

### Steps
- [x] RL-0 baseline · [x] RL-1 driver reroute onto the one emitter · [x] RL-2 assignment+OUTPUT re-lowered.
- [~] **RL-4 — statement control flow.** END-goto LANDED (`:(END)`/`:S(END)`/`:F(END)` resolve via a registered label pointing at the exit node). REMAINING: `:S()/:F()` forms branching on a pattern-match result — that's really RL-5/RL-6 territory now that the match family is live; re-check whether RL-4's own remaining scope has already been absorbed by SN4-PAT before treating it as separately open.
- [ ] **RL-3 — concat + arith.** Value concat, `IR_BINOP`/`IR_UNOP`/`IR_BINOP_TEST`/`IR_UNOP_TEST`, `IR_LIT_*`. Gate: `concat/`, `arith/`, `arith_new/` green. **Likely already subsumed by SN4-PAT/current crosscheck state — re-verify against the live watermark above before treating as the next rung; the RL ladder's own numbers predate SN4-PAT.**
- [ ] **RL-5 — primitive patterns onto the SCAN family.** Likely superseded by SN4-PAT's `IR_MATCH_*` family landing since this ladder was written — re-verify before working this rung directly; SN4-PAT's ladder above is almost certainly the current form of this work.
- [ ] **RL-6 — alternation, backtrack, capture.** Same caveat — check against SN4-PAT's ALT/FENCE/ARBNO/capture landings above first.
- [ ] **RL-7 — DEFINE + user functions.** Check against SN4-PAT-DEFER-CALLOUT's current state first.
- [ ] **RL-8 — indirection, aggregates, keywords.** `$X`, ARRAY/TABLE, `&`-keywords. Check current crosscheck data/keywords/strings category state before assuming this is still greenfield.
- [ ] **RL-9 — full-suite green + stale-section purge.** Crosscheck FAIL=0 both modes, DIVERGE=0; then delete anything in this file the ladder's progress has superseded.

**⚠ Whoever picks up RL-3/5/6/7/8 next: the numbers/gates as written predate SN4-PAT and may already be satisfied by it. Re-derive against the CURRENT STATE crosscheck watermark above before treating any of these as a fresh start — do not re-do work SN4-PAT already did under a different name.**

---

## ▶ MONITOR — 2-way IPC sync-step bug-finder: LANDED, reference only

All MON-RE-0 through MON-RE-6 steps are `[x]` DONE — the monitor is built, proven (semantic acceptance met on `/tmp/mdiv.sno`, an 8-step agreement trace), and is the standing bug-finding method referenced throughout this file and RULES.md. Mechanics: `g_monitor_bin` runtime flag (zero overhead when unset), LABEL/VALUE/CALL/RETURN taps emitted into the flattener (not walked at runtime), `scripts/test_monitor_3way_sync_step_auto.sh` / `test_monitor_2way_sync_step_bin.sh`. See RULES.md's own MONITOR-FIRST directive for usage. Companion offline tool: `harness/probe/probe.py` (`&STLIMIT`/`&DUMP=2` replay) — lower priority, needs mode-3/4 to honor those keywords first, neither does yet.

---

## ▶ DEMO-PAT — claws5 + treebank mode-4 PASS + benchmarked

**WHY:** claws5/treebank are pattern-heavy; SPITBOL interprets patterns (graph-walk + backtrack history stack), SCRIP compiles backtracking into four-port native control flow — a structural advantage already visible elsewhere (pattern_bt 0.77×, SCRIP beats SPITBOL). Proves the win on real corpus programs.

**GROUND TRUTH:** both demos hang in both modes (old "PASS" claims describe the now-deleted mode-1/2 interpreter). Root causes localized via minimal repros:
- **GAP-1 (root cause of the hang) — deferred-eval function calls as capture targets `(epsilon . *FN())` never execute.** Both demos build their entire data structure via these calls; they no-op, data stays empty, the pretty-printer spins forever over an empty structure. Fix needs: lower the deferred inner expr as a value-producing chain, run it at capture-commit, write the result. Runtime capture-write is currently name-only — needs a computed-name/run-chain variant.
- **GAP-2 — captures inside a repeated ARBNO body don't commit** (needs a per-iteration commit-ring: truncate-to-mark on β-reentry, flush at overall-match γ).
- **GAP-3 (lower priority, demos use stored patterns so it doesn't block them) — inline non-literal pattern in SCAN context still bombs.**
- **treebank additional gaps:** GAP-4 recursive deferred pattern eval (`*group` referencing its own def); GAP-5 BAL in built patterns; GAP-6 EVAL-built patterns spliced into a match; GAP-7 user DATA types.

**SEQUENCING:** claws5 first (GAP-1+2), treebank second (claws5 fixes + GAP-4..7). Gate: `test_crosscheck_snobol4.sh` byte-identical to HEAD + the named demo behavior.

### Phase A — claws5 — all still open
- [ ] DP-0 — oracle in hand (`x64` clone works for general programs; claws5/treebank need `-P`/`-f` this `sbl` build doesn't support — `claws5.ref` short-form remains the gate). Still need: `run_demo_mode4.sh` + `test_3way_demo_snobol4.sh` skeleton.
- [ ] DP-1 — deferred-call-in-capture execution (the GAP-1 fix; not a 1-liner, needs a new runtime capture-write variant accepting a computed name; needs the **nv set** ledger stamp, currently only requested).
- [ ] DP-2 — capture-commit inside ARBNO (the GAP-2 fix; D3 commit-ring).
- [ ] DP-3 — claws5 end-to-end, no hang, regenerate `.s` artifact.
- [ ] DP-4 — claws5 benchmark vs SPITBOL, record the honest number.

### Phase B — treebank — all still open
- [ ] DP-5 — user DATA types in mode-4 (M4-DATA: constructor + field selectors).
- [ ] DP-6 — BAL in built patterns.
- [ ] DP-7 — recursive deferred pattern eval `*group` (needs a recursion guard — progress-before-recursion, per manual Ch.8).
- [ ] DP-8 — EVAL-built patterns spliced into a match at runtime.
- [ ] DP-9 — treebank end-to-end + benchmark.

**Prereq reads:** `SNOBOL4-5STAGE-OWNED-BUILD.md` (D3/B7/B8/B9/B10 — DP-1/2/6/7/8 are those rungs, demo-sequenced), `ARCH-SNOBOL4.md` §Native pattern, `src/emitter/bb_regs.h`, `src/runtime/rt/bb_pat_build.cpp`, `src/emitter/emit_core.c` matcher dispatch.

---

## ▶ NRG — Native Register Codegen ("beat the interpreter on statements")

**THESIS:** SPITBOL is indirect-threaded code (not fetch-decode-execute) — SCRIP can't win by removing a dispatch loop that threading already removed. SCRIP currently loses on statements because it replaced threading's one-indirect-branch NEXT with a full PLT call per primitive. The only way to beat threaded code is specialization threading structurally can't do: keep a proven-typed value in a register, emit raw ops, no per-op tagged-descriptor load/re-check. (Patterns are the separate battleground SCRIP already wins — DEMO-PAT above; this rung is statements only.)

**Order A→E→B→C→D** (cheap CFG/dataflow cleanups first, de-risking the register allocator; B flips arith-class benchmarks; C/D kill the call cluster). Gate per sub-rung: crosscheck byte-identical + both-medium + regenerate touched `.s` + A/B wall-ms.

- [ ] **NRG-A — VN: local value-numbering / redundant-load elimination.** **VN-0** value-number repeated `[rbx+k*16]` loads + their tag-checks within a straight-line box chain. **VN-1** drop store-then-reload of the same frame slot and dead `IR_VAR` boxes.
- [ ] **NRG-B — REG: register residency + static type tracking (the deep win).** **REG-0** liveness + single-type-throughout analysis (reuse FZ invariance-proof + GVA DT_I guard). **REG-1** allocate a proven counter to a callee-saved reg across a loop, spill only at exit/escape edges. **REG-2** extend to function-body locals proven DT_I (fibonacci `N`, INC `N`). Gate needs the register value re-materializable at every β/ω edge + fallback.
- [ ] **NRG-C — INL: leaf-function inlining.** **INL-0** inlinability analysis in lower (≤N statements, non-recursive, statically resolved — the existing `__proc[]` table already proves the static-call set). **INL-1** splice the callee's four-port graph at the call site with param→arg substitution. `R=INC(R)` → `R=R+1` inline. Gate: byte-identical + recursion guard + A/B func_call/func_call_overhead.
- [ ] **NRG-D — PROTO: specialized call protocol** (non-inlinable/recursive calls). **PROTO-0** per-call-site block save/restore through known param/return cells resolved at preamble; no per-call loop, no fastpath re-check. Needs the **nv set** ledger stamp (currently only requested). Gate: byte-identical + A/B fibonacci (recursive)/roman.
- [ ] **NRG-E — BOPT: branch chaining** (scaffolded `src/opt/branchopt.c` `bopt_chain`, UNWIRED). **BOPT-0** map IR ports→Byrd ports first (read-only, a written port→field table, no code change). **BOPT-1** wire as a LOWER→EMITTER pass + cycle guard (honor the prior crash: γ-spine doubles as operand-recovery structure — rechain only edges proven not to shorten that walk). **BOPT-2** dead-BB drop + fall-through layout. **BOPT-3** copy propagation (collapse temp-forwarding chains the four-port templates emit — a temp that just forwards a child's value should have its consumer read the source directly; dead-temp elimination follows).

**Prior investigation (session 27): general BOPT in-place γ/ω mutation attempted, crashed (γ-spine is overloaded as operand-recovery structure), quantified low corpus-wide yield (34/1686 collapsible branches, 0% in hot loops) — CLOSED as a perf lever, `src/opt/branchopt.{c,h}` retained as a dead-end record, full writeup in `docs/BOPT-DESIGN.md`.**

---

## ▶ SCAN-GEMINI — every scan/match primitive gets its variable-operand twin

Each scan/match primitive currently folds a literal argument at compile time; the variable-argument case (`POS(N)` where N is a runtime value, not `POS(3)`) needs its own twin arm. `bb_match_span_var.cpp` is the reference twin already landed.

- [ ] **GEM-0 — make the variable-cset pattern REACH the per-primitive native boxes (the prerequisite everything else sits behind).** A non-literal `SUBJ ? PAT` currently bombs in the whole-statement scan box (`bb_scan_stmt.cpp`, "non-literal pattern needs native PB-RB graph") rather than reaching any per-primitive box — so none of the twins below can even be exercised via the common inline-match path until the non-literal case is routed into the native decomposed-graph builder instead of bombing. Same root as DEMO-PAT GAP-3. Multi-file pattern-engine work, budget a full session, MONITOR-first if a partial graph diverges.
- [ ] **GEM-1 — ANY_VAR twin.** New opcode + template mirroring `bb_match_span_var`: fetch cset by name at runtime, same single-char test.
- [ ] **GEM-2 — NOTANY_VAR twin.** As GEM-1, inverted test.
- [ ] **GEM-3 — BREAK_VAR twin.** As GEM-1, BREAK semantics (advance until a fetched-cset char).
- [ ] **GEM-4 — BREAKX_VAR twin.** As GEM-3 plus BREAKX's retry-extend semantics.
- [ ] **GEM-5 — POS_VAR/RPOS_VAR** (integer fetch + same compare, one new opcode pair or a name-driven arm).
- [ ] **GEM-6 — TAB_VAR/RTAB_VAR** (same shape).
- [ ] **GEM-7 — LEN_VAR** (same shape).
- [ ] **GEM-8 — scan-family variable arms in inline context** (`bb_scan_many`/`bb_scan_upto` gain the variable arm the way `bb_scan_any` already carries both; then relax `scan_pat_m3_native_safe`).
- [ ] **GEM-9 — completeness gate** (`test_gate_scan_gemini.sh`: every primitive has both a literal and variable box reachable, proven by compiling one of each).

**Prereq reads:** `bb_match_span_var.cpp`, `lower_snobol4.c` TT_SPAN/ANY/NOTANY/BREAK/BREAKX/POS/TAB/RTAB/LEN arms, `emit_bb.c:2560`/`:3035`, `emit_core.c:371-383`, `rt.c:98 rt_nv_cstr`, `bb_regs.h`. NOTE: overlaps SCAN-TABLE (below) — GEM is correctness, SCAN-TABLE is speed; do GEM first.

### SCAN-FOLD — the only active scan-class rung besides GEM
- [ ] SCAN-FOLD-0 — coverage audit (no code change): confirm every literal-arg primitive seals its constant with zero frame load/runtime eval. Deliverable: a table.
- [ ] SCAN-FOLD-1 — close any unfolded literal arm the audit finds.
- [ ] SCAN-FOLD-2 — NSPAN (nullable span, new primitive, not a folding step) — PARKED until requested.

### SCAN-TABLE — baked character-class classifier (PARKED, "for later")
- [ ] SCAN-TABLE-0 — pick form (256-byte table vs bitmap; lean 256-byte, char MUST be unsigned).
- [ ] SCAN-TABLE-1 — literal cset → baked RO table.
- [ ] SCAN-TABLE-2 — runtime cset → built-once table (the bulk of the real win; covers `BREAK(WORD) SPAN(WORD)` in wordcount/claws5/treebank).

### SCAN-UNROLL — inline-compare for tiny literal csets (PARKED, "for later")
- [ ] SCAN-UNROLL-0 — threshold + dispatch (≤~10 chars → unrolled compares, else table/variable path).
- [ ] SCAN-UNROLL-1 — emit the unrolled compares per primitive semantics.

---

## ▶ Other open perf/correctness rungs (found on full re-read, previously under-captured)

- [ ] **SAB — string self-append capacity** (string_concat 8.8×, string_manip 11.3× behind SPITBOL). `S = S X` currently mallocs+copies O(n) every iteration. Fix: detect the compile-time self-append pattern `V = V <expr>`, back V with a string-builder cell `(ptr,len,cap)` that doubles cap — amortized O(1) append. **SAB-0** detect the pattern in lower · **SAB-1** string-builder runtime type + emit arm · **SAB-2** (⛔ correctness-critical: must preserve copy-on-assign value semantics — any read/alias of V must see an immutable snapshot, or SPITBOL's value semantics break) · **SAB-3** gate + A/B.
- [ ] **EVR — EVAL/CODE arena reclaim** (eval_dynamic 176× behind SPITBOL). Diagnosed: every EVAL call re-parses+re-lowers+bump-allocates fresh RX code that's never reclaimed. Confirmed NOT an OOM in this sandbox (completes in ~88s; the bench-script "crash" was its own 30s timeout) but still a real per-call leak. Fix: snapshot the BB pool top before `eval_build_chain`, run, restore (mprotect RX→RW back), free the per-call AST/IR. Lowest priority (one benchmark) — but see BBGC below for the more general version of this same problem.
- [ ] **PEEP-0 — peephole window.** Kill redundant spill/restore round-trips, `mov reg,reg` identities, dead stores, already-live-value lea/mov. Operate on the structured op-list before flatten. **PEEP-1** sub-expression elimination (CSE) within a BB — reuse an already-computed value instead of recomputing (complements BOPT-3).
- [ ] **CFOLD-0 — literal-expression fold in lower** (feeds BOPT). Fold compile-time-literal arithmetic, literal relops used as predicates (lets BOPT delete the dead arm), literal string concat, `SIZE('abc')`. **CFOLD-1** wire into BOPT (a folded always-true/false relop becomes an unconditional edge → BOPT prunes the dead branch). ⛔ **gate constraint:** fold only when operands are literals AND the op is side-effect-free AND the result matches SPITBOL semantics exactly (integer width/overflow, number↔string coercion, the null-string-identity rule already fixed once in `str_concat_d`) — each folded form must be verified against the oracle individually, not just "looks obviously foldable."
- [ ] **FZ-5 — match-site direct reference** (follow-on to FZ-2/3/4, which are all landed). When the compiler proves a stored pattern variable is once-assigned-invariant, inline the sealed matcher head at the match site and skip the per-match `rt_defer_get_pat_fn` fetch — the real remaining hot-loop win for stored patterns. (Note: FZ-5a/5b under this name already landed per the SN4-PAT section above for the *inline* case — re-verify this item's exact remaining scope against that landing before starting; may be smaller than it looks or already done.)
- [ ] **GVA-4 — rbp GST hash path for runtime indirect refs** (optimization, not correctness — GVA-0's forwarding already guarantees correctness regardless). `$X` where X's runtime value names a GVA-backed variable: skip the full GST hash walk via a `gva_lookup_by_name`-style probe. Do only after GVA-0..3 are green and benchmarked (they are). Marginal impact expected (only helps indirect-ref-heavy code).
- [ ] **REC-COV — community-recognized corpora coverage.** Extend coverage into `corpus/programs/gimpel/` (145 `.sno`, no `.ref` yet) and `corpus/programs/snobol4/demo/` (18 `.sno`). Steps: honest runner + oracle-gen refs + triage table → gimpel → demo → promote counts to hard floors → re-ground any "Nx faster/slower" headline claims against the wider corpus, not just the 16-benchmark set.
- [ ] **BBGC — slide-compaction GC for the BB code arena.** ⬇ **LOW PRIORITY / EXPLORATORY — explicitly do NOT start ahead of GVA-4/REC-COV** (design-only spike, picked up only if the bump arena's lack of compaction becomes a real ceiling; the current LIFO-watermark EVR fix bounds but doesn't compact, so a long-running EVAL/CODE-heavy program could eventually exhaust it despite EVR). Vision: mark live BB blobs, sweep, slide survivors down to compact, re-stitch only the four ports. Viable because everything else baked into a sealed blob (register-relative state, RIP-relative-to-adjacent-RO, immediate constants, absolute-address runtime calls) needs zero fixup under a move — only the four ports (`rel32` call/jmp) do. Real hazard to solve: stored pointers to blob entry points held OUTSIDE the pool (EVAL cache, DT_C/DT_E descriptors, the label→code map, live return addresses on the C stack during an active BB frame) — mitigated by entry-table handle indirection + compacting only at a safepoint with no active BB frame. **BBGC-0** measure+baseline (build an EVAL/CODE stress program that actually exhausts the current bound) · **BBGC-1** root enumerator (read-only) · **BBGC-2** entry-table handle indirection · **BBGC-3** mark · **BBGC-4** safepoint discipline · **BBGC-5** sweep+slide-compact+re-stitch ports · **BBGC-6** trigger on overflow · **BBGC-7** gate (bounded-pool EVAL-heavy stress matches oracle, zero corpus regressions).

**Correction while re-reading (Claude Sonnet 5, 2026-07-08): OPSINGLE (delete `operand_aux`, one operand channel only) — this file's copy still lists it as open work, but it is ALREADY DONE.** PLAN.md's own IR-REDUCE row and a live grep both confirm `bb_operand_aux_set/get` has zero references outside `*-parked-*` files (exempt per PARK-NEVER-DELETE) — `IR_t.operands/n_operands` is the sole operand store, `SCRIP a3de01d2`. This file's own copy of the mandate was simply stale; do not re-attempt it.
- MON-RE-0..6 (the monitor): see its own section above, fully landed.
- FZ-4/FZ-5a/FZ-5b (pattern constant-folding + frozen-head inlining): landed, measured wins (string_pattern 1.13×, pattern_bt 2.81×), see `docs/` if the mechanism is ever needed again.
- DCR-1/2/3 (direct-call protocol): landed, func_call/fibonacci call-cluster cost roughly halved (still net-slower than SPITBOL on the call cluster specifically — see NRG above for why and what's next).
- RPF (relop GVA-parity) + table-get double-walk elimination: landed, moderate wins where relop/table-get dominate.
- KEYWORD-CONCAT bomb (`X = &UCASE &LCASE`): fixed, one-line root cause (nonleaf-flag gap in `sno_seq_flatten_ops`).
- Full three-way SCRIP/SPITBOL benchmark comparison: re-run several times across sessions: SCRIP is slower than SPITBOL on most benchmarks (the NRG rung above is the current plan to close this), competitive-or-faster specifically on pattern-heavy work.
