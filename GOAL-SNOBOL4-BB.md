<!-- ════════════ TOP PRIORITY RUNG (Lon, 2026-07-06 session cont.) ════════════ -->

## ⭐⭐⭐ TOP PRIORITY RUNG: BB-OWNED-ζ — per-BB self-allocating memory, THE BB-SPECIFIC GC (Lon pivot, this session)

**THE IDEA (Lon, verbatim-in-spirit):** a new kind of GC, distinct from the SIL mark/slide/adjust family (§6 in
`GOAL-IR-IMMUTABLE-EMIT.md`), marked by BB entry/exit instead of heap-reachability tracing. **α does the ALLOC + SET
R12 + saves it for β to load. β LOADS that saved R12 (no alloc). γ has nothing special. The jump to ω out of a
construct's TRUE exit is a FREE.** Start with `ZC_ALLOC_INFINITE` (a bump arena that never frees) to prove the
wiring is correct before anything reclaims. Three steps: (1) per-BB self-alloc under INFINITE (correctness only,
nothing freed yet); (2) flip the backing to something that actually slides/adjusts the already-marked blocks (real
reclamation); (3) an optimizer pass finds CHAINS of these BBs with a single α-entry / single ω-exit and coalesces
them onto ONE shared R12, so the per-BB grain is the CORRECTNESS baseline and the chain-coalesce is the SPEED
optimization layered on top, not a redesign. **This is the ⭐ZB-ACT-0 / ZB-ACT-1 / ZB-ACT-2 ladder already sitting
in `GOAL-IR-IMMUTABLE-EMIT.md` (§ZB-ACT, Lon's "EUREKA times ten," 2026-07-06) — same idea, independently arrived
at twice same-day, now merged into ONE rung, with ARBNO as the first construct because it's the documented casualty
(re-entrant iteration clobbering its one static slot) and because its `bb_match_arbno.cpp` template already exists
to test against.**

**⚠ THE PART OF THIS IDEA ALREADY TRIED AND FOUND WRONG, SAME-DAY, VERIFIED IN LIVE CODE (do not re-derive this the
hard way — read it once here):** "ω = free, uniformly, for every jump to the ω port" is NOT structurally sound.
α and β get a clean zero-edit central hook because every node has EXACTLY ONE α-define and ONE β-define — that's a
structural property of the port model. **ω does NOT have this property in every template.** Verified by direct
read of `src/templates/bb_match_arbno.cpp` this session: it emits SIX literal `jmp "ω"` sites across its six roles
(v1: G/K/F: roles 0/1/2; v2 per-iteration-COLLECTION body: G/K/F: roles 3/4/5), and only TWO of the six (role 2's
line 70, role 5's line 133) are the construct's genuine "this activation is dead forever" exit. The other four
(role 0 line 54, role 1 line 64, role 3 line 95, role 4 line 111) reuse the literal ω port name for internal
control flow — role 0/3's ω actually means "enter the body" (a forward/success-shaped jump wearing the ω name);
role 1/4's ω means "refuse this zero-advance extension, hand off to the exhaust role" (which IS role 2/5's true
exit, reached via alias). Hooking `port==OMEGA` universally at the central jump-dispatch site (`x86_jmp`,
`x86_asm.h:238`) would fire a FREE on the four internal jumps too. Under a bump/LIFO backing, `rt_zls_release`
(`zeta_alloc.c:74`) snaps the bump pointer back WITHOUT checking it's actually the topmost live frame — so a wrong
free here is **silent corruption three statements downstream**, not a crash at the bad instruction. That's the
trap: the bug doesn't announce itself where it happens.

**THE REWIRE QUESTION Lon asked THIS SESSION, ANSWERED (read `bb_match_arbno.cpp` first, don't assume):** *can the
ω's be made unique instead of construct-aware-hunting the true one?* **Answer: looks mechanically cheap FOR THIS
TEMPLATE, not yet proven for the other 20.** The six sites fall into a legible repeating two-per-role-family
pattern (generator role's ω = "enter body", body-success role's ω = "refuse, defer to exhaust", exhaust role's ω =
true death) — nothing about the CONTROL FLOW needs to change, only which string names the jump/label pair at each
site. Renaming role 0/3's exit to e.g. `ω_arbno_enter_body`, role 1/4's to `ω_arbno_refuse`, and reserving bare `ω`
for role 2/5 looks like a pure find-and-relabel inside one template — the jump TARGETS don't move. **The catch:**
this is one template out of the 21-member `bb_match_*` family (`abort/advance/any/arb/arbno/atp/break/breakx/
capture/defer/fence/head/len/notany/pos/rem/retry/rtab/span/span_var/tab`); if unique-naming turns out to fight
some OTHER template's structure (a generator role whose "enter body" jump can't cleanly get a distinct label, or a
template where the true exit ISN'T reachable via a clean alias the way role 2 aliases role 1's refusal here), the
convention has to be decided once and applied uniformly, not re-invented per template. This is worth discovering
by actually building ARBNO's slice first, not by auditing all 21 up front — **the rewire is STEP 1 to actually
attempt, not a fallback**; construct-aware ω-hunting per the ORIGINAL corrected model (below) is the fallback if
renaming fights a given template.

**THE METHOD — MALLOC+ASan BEFORE BUMP, either way this resolves (Lon directive, corrected model, already in
`GOAL-IR-IMMUTABLE-EMIT.md` §ZB-ACT):** whichever way the ω question resolves for a given template, prove the
wiring under `-DZC_ALLOC=ZC_ALLOC_MALLOC` + ASan FIRST — a real malloc per α, a real free per the chosen ω site(s),
so a wrong free is caught INSTANTLY and LOUDLY as a stack-traced use-after-free/mismatched-free, not a silent
bump-pointer snap. Only once ASan-clean, flip to `ZC_ALLOC_BUMP_LIFO` (or start at `ZC_ALLOC_BUMP_INFINITE` per
Lon's ask — pure-wiring isolation, nothing ever frees, so any surviving bug is layout, never lifetime) and confirm
BYTE-IDENTICAL behavior across backings — the MODE-INVARIANCE GATE: an allocator/grain change may alter bytes and
speed, NEVER behavior; the crosscheck fail-set must stay byte-identical m3/m4/backing-to-backing.

**STEPS (three, per Lon — matches ZB-ACT-0/1/2 exactly):**
1. **STEP 1 — per-BB self-alloc, correctness only, `ZC_ALLOC_INFINITE` backing.** Instrument ARBNO's α/β/ω per the
   port model above (α=alloc+set+save R12, β=load-only, γ=untouched). Try the unique-ω-naming rewire first; fall
   back to construct-aware true-ω wiring (role 2 v1 / role 5 v2 specifically) if renaming fights the template.
   Nothing frees yet — INFINITE never releases. Acceptance: ARBNO repro matches oracle both modes; the OLD
   clobber-on-re-entry bug (documented casualty — re-entrant iteration reusing its one static whole-program slot)
   is GONE; crosscheck fail-set byte-identical to pre-rung (this is additive, default-off until wired live).
2. **STEP 2 — real reclamation.** Flip backing to something that actually slides/adjusts the marked-dead blocks
   (BUMP_LIFO first, per the existing ZC_ALLOC axis — mark/release, LIFO discipline; the eventual BB-specific
   slide/adjust GC is the longer-term target per the BB-SPECIFIC-GC EUREKA below). Prove under MALLOC+ASan first
   per THE METHOD above, THEN flip to the real backing and confirm byte-identical to STEP 1's INFINITE run
   (mode-invariance gate — proves reclamation introduced no lifetime bug, doesn't just look fast).
3. **STEP 3 — chain-coalesce optimization.** An optimizer pass finds chains of these self-allocating BBs with a
   single α-entry / single ω-exit (no internal branch back out) and coalesces them onto ONE shared R12 — the BB
   "owns" its memory individually as the correctness baseline; the chain-share is a LATER optimization on top, not
   a prerequisite. This is exactly ZB-ACT-2's "procedure grain on the emitted side" generalized to any coalescible
   chain, not just procedure boundaries.

**THE BB-SPECIFIC-GC EUREKA this rung is actually chasing (why Lon called it top priority):** a Byrd Box is
pure-functional with exactly one entry-family and one exit-family ⇒ block liveness is a STRUCTURAL fact of control
position, not a heap-reachability question a tracer has to discover. The ω port (the TRUE one) IS the death — you
never trace to find out a ζ-block is dead, you just reached the instruction that means it's dead. So the "collector"
degenerates to an ASSERTION that the stack discipline held (a flag set at α, cleared at true-ω), not a mark-and-
sweep — structurally simpler than the SIL mark/slide/adjust family precisely because the BB structure pre-answers
the liveness question that general GC has to compute. **If alloc is one bump on entry and free is a flag/pointer-
snap on exit, and R12 can be shared across a coalesced chain as the final optimization — yes, this looks like a
genuinely speedy design, PROVIDED the true-ω question is answered correctly per construct (or the unique-naming
rewire pans out).** That "provided" is exactly what STEP 1 proves before anything else in this rung is trusted.

**Prereq reads before touching code:** `GOAL-IR-IMMUTABLE-EMIT.md` §ZB-ACT in full (the ⭐⭐ZB-PORTS /
⭐ZB-ACT-0 / ZB-ACT-1 / ZB-ACT-2 rungs — ZB-PORTS may already be landed or in-flight this session per that file's
watermark journal, check its own top-of-section CURRENT-PRIORITY banner before assuming step order), plus
`ARCH-ZETA-LOCAL-STORAGE.md` (the ζ design doc of record) and `src/contracts/zeta_choices.h` (the `ZC_ALLOC` /
`ZC_SELFLOAD` axes — already built, this rung is about who calls them and where, not building allocation).
**Do NOT duplicate the ζ history into this file** — this rung is the SNOBOL4/ARBNO-facing entry point and pointer;
the full design, the choice-space (granularity × backing), and the six-model ζ history stay in the GZ#5 file per
the existing PLAN.md split.

### SESSION LOG — first STEP-1 slice attempted, real progress + one real structural gap found (same session)

**What actually got built and is sitting in the tree right now, all gated behind `ZC_SELFLOAD_ALLOC` (=4, new
enum value, added this session to `zeta_choices.h`) and fully inert by default — confirmed byte-identical
252/276·251/9/16·DIVERGE=1 crosscheck vs. pre-rung baseline with the mode off:**
- `emit.h`: new `int op_omega_is_death` field on the shared emit context.
- `emit.cpp`: `op_omega_is_death` computed ONCE, correctly, per node, at the exact point the flattening loop
  (`codegen_flat_chain_body`) already resolves `omega_resolved`/`otgt` for that node's ω-edge — true iff the edge
  falls all the way through to the chain's own outer `lbl_ω` and isn't a disguised `IR_SUCCEED` fallthrough. This
  field is SOUND and reusable — it is NOT currently read by anything (see below) but costs nothing left in place.
- `x86_asm.h`: `x86_selfload_mode()` (env-override reader, mirrors `x86_port_mode()`'s `SCRIP_ZETA_PORT` pattern —
  new var `SCRIP_ZETA_SELFLOAD`) and `x86_zeta_free_call()` (alignment-safe `call rt_zls_release(r12)`, forward-
  declared before `x86_jmp` / defined after `x86()` because `x86()` itself calls `x86_jmp` — ordering constraint,
  now documented in-file). **`x86_zeta_free_call()` is currently UNUSED** — see the r12-vs-carrier finding below.
- `zeta_alloc.c`/`.h`: two new accessors, `rt_zls_arbno_step1_store(void*)` / `rt_zls_arbno_step1_load(void)`,
  backed by ONE static pointer (`g_zls_arbno_step1_carrier`). Explicitly scoped in the source comment as
  sequential-reentry-only, not nested/concurrent — see below, this limit is now CONFIRMED hit in practice, not
  just theorized.
- `bb_match_arbno.cpp`: role 0's α now calls `rt_zls_alloc(4096)` then `rt_zls_arbno_step1_store` (gated); role
  2's true exit now calls `rt_zls_arbno_step1_load` then frees it (gated). r12 is deliberately NEVER repointed by
  either call — confirmed necessary (see below).

**Two real, verified findings from actually building this, both worth carrying forward precisely:**

1. **The "six jmp ω sites" from the earlier same-session framing were NOT six competing guesses about one
   ambiguous exit.** Traced through `lower_snobol4.c`'s `sno_ω_to`/`lc_ω_to_β`: the wiring layer ALREADY decides,
   per-edge, at IR-construction time (not emit time), whether an ω-edge lands at a target's α (clean handoff) or
   its β (an aliased re-entry — e.g. role 0's ω aliases into role 2's β BECAUSE role 2 reads role 0's OWN shared
   zls slot one instruction before role 2's true exit). The Proebsting paper's port-as-attribute framing
   initially suggested "these should have unique local labels" (a labeling fix) — traced further, that was ALSO
   not quite it: the construction is already correct, it just needed reading `op_omega_is_death` (computed from
   the SAME `omega_resolved`/`otgt` values `emit.cpp` already has) rather than guessing from `op_phase`
   (overloaded across ≥3 unrelated IR node kinds — verified, NOT a safe discriminator alone). `op_omega_is_death`
   IS the right, precise, per-node signal. **Confirmed exactly right for role 2/5 specifically** (verified via
   `sno_ω_to(F, fail)` landing outside the local chain, on the pattern's own fail continuation).

2. **r12 cannot be repointed by a per-construct self-alloc without breaking every sibling box.** `FR(off)` is
   LITERALLY `[r12+off]` (`x86_asm.h`) — r12 is ONE register for the WHOLE emitted function, shared by every box
   in it, not scoped to one construct's activation. `x86_zeta_free_call()`'s original design (free "r12 itself")
   assumed r12 WAS the allocated block — wrong; STEP 1 as actually built carries the pointer via the runtime-side
   single carrier instead, r12 untouched. **This confirms, concretely, the design doc's own "open sub-question"
   (§ZB-ACT-0, "the cheat's first correct form is per-SCOPE... NOT literally per-individual-box") is correct** —
   this session hit the exact wall that sub-question predicted, from the implementation side, independently.

**THE GAP — bigger than expected, found via PRECISE per-call tracing (a temporary `SCRIP_ARBNO_STEP1_TRACE=1`
env-gated fprintf pair in `rt_zls_arbno_step1_store/load`, NOT the generic `[ZLS]` telemetry counters, which
mix in unrelated pre-existing `zls` consumers — `bb_match_defer.cpp` also calls `rt_zls_alloc`/`release` and an
early reading of the shared counters this session WRONGLY attributed their movement to this rung's own code;
correct that mistake if it resurfaces in a later session's memory of this log):**

**A successful ARBNO match — one that never needs to backtrack to its own role-2 exhaustion — currently LEAKS its
allocated block.** Traced why: role 0's γ (null-yield) and role 1's γ (extend-succeeded) BOTH target `succ`
(`lower_snobol4.c` line ~628/630) — the REST OF THE PATTERN, not anything in ARBNO's own role family. There is no
γ-side death point local to ARBNO at all. The actual "this activation can never be resumed again" moment on the
SUCCESS side is `sJ` — a plain `IR_GOTO`, built ONCE PER STATEMENT (`lower_snobol4.c` line ~888,
`sno_lower_match`'s caller), representing the WHOLE PATTERN-MATCH STATEMENT's own final, irreversible success.
Confirmed via trace: a 2-line test where line 1 succeeds cleanly and line 2 backtracks to true exhaustion showed
STORE/STORE/LOAD — line 1's block never freed, line 2's correctly freed. Output matched the oracle both lines;
this is a resource leak, not a correctness bug, but it is real and it is not a small addendum to STEP 1 — it's a
DIFFERENT SHAPE of problem: `sJ` is shared across the ENTIRE pattern tree for one statement, potentially several
ARBNOs (nested or sequential) deep, so "free the one thing in the single global carrier" cannot generalize to it —
a single scalar carrier cannot represent N simultaneously-live, independently-freeable activations, which is
exactly what a compound pattern with more than one still-live generator requires. **NEXT SESSION SHOULD START
HERE, not by re-deriving the above:** the real fix needs a per-match-statement carrier shaped like a stack/list
(pushed at each generator role's own alloc, drained at `sJ`), and — importantly — must NOT double-free anything
whose OWN construct already reached its own true-ω first (a compound pattern where one alternative's ARBNO
exhausts internally while a DIFFERENT alternative is what ultimately succeeds). This needs real design thought,
not a quick patch; do not attempt a second single-carrier variant as a shortcut, that is the same mistake at a
different scope. Marking `sJ` as special requires a flag set at CONSTRUCTION time in `sno_lower_match`
(mirroring how `op_omega_is_death` was correctly solved by reading construction-time knowledge rather than
inferring from a generic node-kind check) — `IR_GOTO`'s generic node kind alone does NOT distinguish a
pattern-statement's `sJ` from any other ordinary goto in the program; hooking `IR_GOTO` broadly would be wildly
overbroad (every statement in every language this spine supports emits `IR_GOTO`s for ordinary sequencing).

**CONFIRMED THIS SESSION (Lon's closing question, checked against the actual construction rather than assumed):**
`sJ` really is created EXACTLY ONCE per statement (`lower_snobol4.c` line ~888) and threaded as a single fixed
value through the ENTIRE recursive descent — `sno_lower_match` → `sno_pat_node`'s recursion (every `succ` at
every level of the pattern tree, arbitrarily nested, eventually bottoms out at this same node; verified by
tracing role 0/role 1's γ targets up through the recursion, not merely asserted). So Lon's simplification is
EXACTLY right and does not need hedging: **the fix is one loop, at one shared point (`sJ`), over "every generator-
kind box that got a fresh alloc during this statement" — not a per-construct or per-nesting-level search.** This
also resolves the double-free worry cleanly, for free: role 2's own true-exit (`sno_ω_to(F, fail)`) routes to
`fJ` — the statement's FAILURE join, a structurally different node from `sJ`. An ARBNO that already died via its
own ω never reaches `sJ` at all, so the success-side sweep only ever sees activations still pending precisely
because they took the success branch — no overlap, no guard needed against double-freeing something role-2
already freed. **The shape of the actual fix, precisely:** a per-STATEMENT (not per-node, not global) carrier —
a small fixed-size array or a stack, pushed once per generator-role alloc (role 0's α, and whatever the
analogous entry point is for any other self-allocating construct once this generalizes past ARBNO), reset at the
START of each statement's lowering (so it can't leak across statements the way the current single global
carrier structurally cannot help but do), and drained — walked, each entry freed via the existing
`rt_zls_release` — at `sJ`'s own emission point specifically, which needs the same construction-time flagging
`op_omega_is_death` already demonstrates the right pattern for (a flag set where `sJ` is BUILT in
`sno_lower_match`, not inferred later from `IR_GOTO`'s generic kind). **The generalization Lon is pointing at —
"at the end of each statement AND at the end of each pattern match AND at the end of an EVAL" — is the same
mechanism at three altitudes: `sJ` already covers "end of statement" and "end of pattern match" (they are THE
SAME NODE for a plain match statement, confirmed above); EVAL will need its own analogous outermost join once it
lands, but EVAL is currently a hard FATAL in this subset (`lower_snobol4.c` line ~1178, "EVAL and CODE are not
remotely possible yet") — there is no existing join to point at for it today, so that third altitude is
future-verified, not yet checkable, and should not be assumed identical to the other two without re-deriving it
against EVAL's actual lowering once EVAL is landed.**

---

<!-- ════════════ SNOBOL4 TEST-SUITE LADDER CRAWL — live head (2026-07-06) ════════════ -->

# GOAL — SNOBOL4 on the shared BB spine
AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude   OPENED: 2026-07-03 · SN4-PAT + RE-LIGHT folded in 2026-07-06 · BB-OWNED-ζ set TOP PRIORITY 2026-07-06

## ▶▶ CURRENT STATE — READY TO CRAWL THE TEST SUITE (2026-07-06)

**WHAT MOVED HERE (Lon directive, 2026-07-06):** the full `SN4-PAT` pattern-reconstruction ladder (SN4-PAT-0 … SN4-PAT-DEFER-CALLOUT) and the SNOBOL4 subset RE-LIGHT ladder (RL-0 … RL-9), lifted out of `GOAL-IR-IMMUTABLE-EMIT.md` (Ground Zero #5). That file keeps the language-blind spine (emitter-reads-IR rules, TMP-ERADICATE, the ζ/ZLS storage design, the Icon rungs); THIS file is now the sole home of SNOBOL4 feature work and the test-suite climb. **The ζ infrastructure SNOBOL4 rides (the bump ζ-stack, per-iteration COLLECTIONS, `rt_zcol_push`, GC-6) still lives in the GZ#5 file — reference it, do not copy it.** The GZ#5 chronological watermark journal (SN4-PAT sessions included, interleaved with Icon/ζ/GC) also stays there as the whole-project log; the per-rung LANDED records that matter for SNOBOL4 travel with the ladders below.

**CROSSCHECK WATERMARK (SCRIP `ebfc7009`, corpus `4f6f2943`, committed LOCAL/UNPUSHED — credential pending; RE-DERIVE at session start — never trust this line):** `bash scripts/test_crosscheck_snobol4.sh` mode-3 **252/276 (24 FAIL)**, mode-4 **251/9/16 (9 FAIL, 16 SKIP)**, **DIVERGE=1** (see below — a newly-exposed pre-existing bug, not a regression from this session's code changes).

**DOCTRINE:** SNOBOL4 rides the SAME pipeline as Icon — sno_parse_ast → lower_sno_stage2 (`src/lower/lower_snobol4.c`) → shared optimizer → ir_drive_slot_assign → the ONE language-blind emitter → mode-3 (`--run`) / mode-4 (`--compile`). SCRIP FOLLOWS SPITBOL SEMANTICS; oracle = `/home/claude/x64/bin/sbl -b`. Every statement lowers on the 5-STAGE MODEL: (1) build subject; (2) build pattern; (3) perform pattern; (4) build replacement; (5) perform replacement. Pattern stages are now LIVE (the SN4-PAT family below), no longer lower-time fatals.

**THE METHOD (Lon directive, lightened 2026-06-27 now the monitor is proven): STATIC-FIRST → ONE STAB → THEN MONITOR.** Per failing program: (1) read its `.ref`, run `--run`/`--compile`, read the divergent output, reason from the generated `.s` + the IR + the BB templates straight to the land mine; (2) ONE targeted fix, rebuild; (3) VERIFY both modes vs `.ref` (ground truth — no live oracle needed). If the stab fails or the bug resists static reasoning, ESCALATE to the 2-way IPC sync-step monitor: bracket first-divergence ↔ last-agreeing event, pin a gdb spin/ignore-counter breakpoint at that bracket, single-step to the land mine (the instruction that writes the wrong value), fix, re-verify. The monitor is the heavy instrument reserved for hard bugs — NOT built or run until a stab has failed. Regression gate = the `.ref`-based crosscheck.

**BRACKET 2 — ✅ CLOSED, BUT BOTH PRIOR-SESSION HYPOTHESES WERE WRONG (Claude Sonnet 5, 2026-07-06, later session).** The previous NEXT BRACKETS #1/#2 guessed these were reentrancy/call-path problems. Neither was — both were small, mechanical, pre-existing gaps, found by actually running each `.sno` and reading the FATAL rather than trusting the old speculation. **Fix the assumption before fixing the bug.**
- **063-066 (fence_fn cluster) — NOT about DT_P/function-call reentrancy.** None of these four tests contain a `DEFINE` at all. Root cause: `sno_cset_fold` (the compile-time charset-argument folder for `ANY`/`SPAN`/etc.) only recognized `TT_QLIT` and `&LCASE`/`&UCASE`, so `SPAN(digits)` (a plain named variable holding a literal, the common `digits='0123456789'` idiom) and `ANY(&UCASE &LCASE)` (string concat via juxtaposition) both failed to fold, making `sno_pat_supported` reject `FENCE(SPAN(digits)|'')` as "outside the subset" even though FENCE(ALT) itself was already fully landed. Fix: `sno_cset_fold` now also resolves (a) a `TT_VAR` name when a whole-program scan finds EXACTLY ONE write to that name anywhere (main body + all DEFINE bodies + pattern-capture targets + `TT_SWAP`) and it's a plain literal assignment — a sound single-static-assignment check, not order-dependent, so it's safe regardless of GOTO control flow; (b) `TT_SEQ`/`TT_CAT` string concatenation of two foldable pieces. New code: `sno_cconst_*` family in `lower_snobol4.c` (built once per compile in `lower_sno_stage2`, right after `st[]` assembles). SCRIP `cea84ba4`.
- **074/W07 cursor cluster — NOT about β-resume across a blob boundary.** `@NAME` (cursor-position capture, `TT_CAPT_CURSOR`) and `$NAME` (immediate-value capture, `TT_CAPT_IMMED_ASGN`) were simply never wired into the lowerer at all — `sno_pat_supported`/`sno_pat_node` had no case for either. Both had COMPLETE runtime+template support already sitting on disk, unused: `bb_match_atp.cpp`/`rt_at_cursor` (for `@`) existed since the pre-purge parked file (`lower_snobol4.gz5-parked-41b53078.c`) referenced `TT_CAPT_CURSOR`; `bb_match_capture.cpp` already implemented BOTH `op_phase==1` (COND, `.`) and `op_phase==2` (IMM, `$`) — only phase 2's emit-side DRIVE/dispatch/op_sval wiring was missing, `IR_MATCH_ASSIGN_IMM` existed in `IR.h` but had zero references in `emit.cpp`. Fixes: SCRIP `b55ae5ea` (ATP: Makefile + emit.cpp op_sval-fill/DRIVE/dispatch + lower_snobol4.c support/node cases) and `6e6d6d18` (IMM: same three emit.cpp sites + lower_snobol4.c `TT_CAPT_IMMED_ASGN` case, structurally identical to the existing `TT_CAPT_COND_ASGN` case). **Lesson for next session: when a bracket's stated root cause doesn't match what the FATAL actually says, trust the FATAL — these two hypotheses were plausible-sounding and both wrong.**
- **Verification (all four landings above):** each oracle-pinned individually (063/064/065/066/074/W07_capt_cur/W07_capt_imm/059_capture_dollar_deferred — the last cleared for free by the `$` fix — all m3==oracle), full crosscheck re-run after every commit (241→245→247→250, DIVERGE=0 throughout), icon smoke 12/12×2 unaffected at every step (this file's changes are 100% inside `lower_snobol4.c`/`emit.cpp`/`Makefile`, language-blind-emitter rules respected — no template touched a byte-producing path, only DRIVE staging + dispatch wiring for opcodes Icon never emits).

**NEW FINDING — FENCE cannot appear inside an ARBNO body today, BY DESIGN, not oversight (investigated, not fixed, this session).** `116_pat_arbno_of_fence_inline`, `142_pat_arbno_fence_arbno`, `145_pat_left_assoc_via_arbno_fence`, `151_pat_arbno_inline_fence_backtrack` all use `ARBNO(FENCE(...))` or a body containing FENCE. Both `sno_pat_deterministic` AND `sno_pat_v2_ok` explicitly `return 0` the instant they see `sno_is_fence(t)` — so an ARBNO body containing FENCE fails BOTH disjuncts of the `sno_pat_supported` ARBNO gate (`sno_pat_deterministic(body) || (sno_pat_v2_ok(body) && sno_pat_v2_tail_gen(body))`) unconditionally, regardless of what else is in the body. This is confirmed intentional — SN4-PAT-3i's own landing note says "FENCE was never scoped to cover [ARBNO]." **151 is a deliberate NEGATIVE DISCRIMINATOR** (its own comment: establishes that a previously-found leak — FENCE-via-`*var` retrying past its seal — requires the `*var` indirection, NOT inline FENCE; any future fix "must keep this passing"). Wiring FENCE into ARBNO bodies means teaching the per-iteration COLLECTION body-wiring how FENCE's fail-retarget (`cx->pat_fail` seal) composes with the ARBNO iteration/generator machinery — a real design question (which fail-target does a sealed element inside iteration N point at: the statement's `fJ`, or iteration N's own local retry?), not a missing switch-case. **Do not attempt this as a quick stab; it is its own rung.** `132_pat_fence_eps_recur_shallow` is unrelated (see below) despite sharing the FENCE-in-recursive-pattern theme.
**NEW FINDING — 132 is a separate, narrow, unrelated bug.** `DEFINE('makeP()')` fatals with "DEFINE entry label not found among statement labels: makeP" — but `makeP` is a decoy, never called (the test is really exercising a self-referential stored pattern, `P = LEN(1) FENCE(*P | eps)`). DEFINE-registration currently fatals eagerly on a missing entry label even for a function nothing invokes; it should probably only fatal at call time, or accept a DEFINE with no discoverable body when the function is provably uncalled. Independent of the FENCE-in-ARBNO question above — a much smaller fix, untouched this session, good next-session starting point.

**NEXT BRACKETS (in order, re-derived from a fresh crosscheck this session — do not trust the old list above this line, it named the wrong root causes):**
1. **132_pat_fence_eps_recur_shallow — ✅ CLOSED this session (SCRIP `ebfc7009`).** Was a compile-time-eager DEFINE entry-label check: `lower_sno_stage2` built a callee graph for EVERY DEFINE unconditionally and fatal'd if the entry label matched no statement — but SPITBOL only resolves an entry at call time, so a program that DEFINEs a function and never calls it (this test's decoy `DEFINE('makeP()')`, the real content is a self-referential stored pattern `P = LEN(1) FENCE(*P | eps)`) must still run. Fix: skip registering the `proc_table` entry instead of fataling (`stage2_proc_grow` indices are name-keyed elsewhere, not positionally tied to `defs[]`, so skipping one is safe). Oracle-verified, zero regressions, icon+prolog smoke unaffected.
2. **⚠ NEW FINDING — the checked-in `.ref` for `1017_arg_local` was simply WRONG, not a SCRIP bug, and fixing it exposed a real mode-3/mode-4 inconsistency (investigated, NOT fixed, this session).** The old `.ref` said `PASS 1017_arg_local (8/8)`; the REAL SPITBOL x64 oracle (checked with BOTH `-b` and `-bf`, identical either way — not a case-folding artifact) actually fails at the first assertion: `FAIL 1017/001: ARG(.jlab,1) = A` (`ARG`/`LOCAL` are simply unimplemented builtins in SCRIP — confirmed zero references anywhere in `by_name_dispatch.c` — and apparently real SPITBOL's own `ARG`/`.label`-as-name interaction doesn't do what this test's author assumed either, since the checked-in expectation never matched even the real oracle). **SCRIP mode-3 already produces the corrected `.ref`'s output byte-for-byte with ZERO code changes** — regenerated the `.ref` via the documented procedure (corpus `4f6f2943`). **But mode-4 (`--compile`) does NOT match** — it produces an `Error 5 ... Undefined function or operation` style hard failure instead of the graceful fallback mode-3 uses for the same undefined-function call, which is why DIVERGE went 0→1. Grepped `src/runtime/`, `src/driver/` for the literal message and found NOTHING — the mechanism is not understood yet, so nothing was touched rather than guess-fix a runtime error path used by (presumably) every language's undefined-function call, not just SNOBOL4's. **This is NOT a regression from anything landed this session — mode-3 and mode-4 always disagreed on this exact program; the stale `.ref` simply made both look equally "wrong" so the disagreement never surfaced as a DIVERGE before.** Next session: find where mode-4's undefined-function path diverges from mode-3's (grep binary/library strings if source grep keeps failing; it may be baked in as a `.rodata` string rather than a C string literal Claude's grep pattern matched) before touching it.
3. **FENCE-in-ARBNO-body** (116/142/145/151) — real design work, see the finding above; do this as its own focused rung, verify 151 (the discriminator) still gives the SEALED/GOOD answer, not just that it compiles.
4. **062/063 (capture) — `SUBJECT PATTERN = REPL` splice.** Explicitly out of scope per the existing FATAL ("match-only for now"): stages 4-5 of the 5-stage model (build replacement + splice it into the subject) have no implementation at all yet. Real, scoped, well-understood new feature — not a wiring gap.
5. **word1/word3/cross/wordcount** — the four distinct bugs from the previous session's bracket-1 fix (still unfixed, still distinct: word1 = capture-into-OUTPUT-keyword; word3 = mid-chain-generator capture; cross = wrong output, exit 1, undiagnosed past that; wordcount = "expression form not in the landed subset: tree kind 31", an unrelated parse/lower gap).
6. **1011_func_redefine, 1013_func_nreturn, 1015_opsyn** — each a genuinely new capability, NOT wiring gaps: 1011 needs DEFINE callable in expression position (currently statement-level-literal only); 1013 needs a function call result usable as an assignment lvalue (NRETURN-returned name); 1015 needs OPSYN-rebound operator symbols routed through the lowerer's operator dispatch. Each is its own rung.
7. **213/082** — `indirect_name`/`keyword_stcount`; long-standing pre-existing baseline items per earlier sessions, not yet root-caused this session.
8. **124/143 ("regex")/140/141** — `EVAL`-adjacent and compound-pattern corpus probes, not yet individually triaged this session.
9. **test_case/test_stack/test_string** (corpus `lib/case.sno`/`stack.sno`/`string.sno`, include-library) — likely depend on some of the above (OPSYN, splice) landing first; re-check after 4 and 6.

**FINDINGS PARKED (do not fake — own rungs):** FINDING-A EAGER-ASSIGN (`.` assigns at subpattern-success; a failing match still mutates the target — the `rt_dcap_*` deferred-capture protocol is orphaned, never called — wire it at match entry/success/fail); FINDING-B SEQ-CHAIN-THROUGH-DETS (a deterministic element between the fail point and a left generator blocks resume — the le_tail trick sees only the rightmost leaf; the SN4-PAT-BETA-CHAIN rung); FOLD BLOB TIER (`IR_REF_INVARIANT` folded-constant sealed blobs — string tier landed, blob tier remains).

<!-- ════════════ SN4-PAT LADDER — moved verbatim from GOAL-IR-IMMUTABLE-EMIT.md, 2026-07-06 ════════════ -->

## ⛔ SN4-PAT — SNOBOL4 PATTERN MATCHING, RECONSTRUCT THE AMPUTATED IR FAMILY (Lon, 2026-07-04; was #1 priority in GOAL-IR-IMMUTABLE-EMIT.md, relocated here 2026-07-06 — this is now the SNOBOL4 feature spine and the top of the test-suite crawl)
**THE RUNG NAME IS `SN4-PAT`.** The non-pattern SNOBOL4 subset is already complete on the live spine (literals,
vars, keywords, `.NAME`, arith+concat, unary, `$`, subscript/`DEREF`, calls, gotos/labels, every assignment LHS
form, DEFINE/DATA/OPSYN). **The wall is pattern matching** (`lower_snobol4.c:257` — any `:pat` field or `TT_SCAN`
subject `sno_fatal`s). Pattern matching genuinely needs new opcodes — the existing Icon SCAN family is anchored
control-flow, not SNOBOL's first-class floating-needle-over-a-DT_P-pattern model — so this is NOT an
"existing-IRs" job. **It IS a RECONSTRUCTION**: the full pattern IR family existed and was amputated wholesale,
and the design is recoverable from git.

**PROVENANCE (all in `git log`):**
- `8de0fb46` GZ#5 ENUM-AMPUTATION — removed 119 non-Icon members incl. the 53-opcode pattern family (design
  survives at parent `41b53078`).
- `2e5a5a3e` — matcher family was `IR_PAT_*`, renamed `IR_MATCH_*` to mirror `bb_match_*`.
- `18133720` FZ-3 — pattern CONSTANT FOLDING: an all-constant (VARIANT-free) subpattern → sealed
  `IR_REF_INVARIANT` RO blob, built once not per-match. **This is the "IR_INVARIANT" Lon means.**
- `547de08d` / BB-REVAMP-TRACKER — the 21 `bb_match_*` templates (abort/advance/any/arb/arbno/atp/break/
  breakx/capture/defer/fence/head/len/notany/pos/rem/retry/rtab/span/span_var/tab).

**THE MODEL (SPITBOL, two families + one ref — re-added to `IR_e` this session, build stays green):**
- `IR_MATCH_*` (28) = MATCHERS: the inline needle. `lower_pat_node` (recover from `41b53078:lower_snobol4.c`,
  ~200 lines) compiles a pattern tree into one node per element, wired by γ(success)/ω(failure); `IR_MATCH_ALT`
  = backtrack tree, `IR_MATCH_CAT` = concatenation thread, `IR_MATCH_ASSIGN_IMM/_COND` = `$`/`.`. Used for
  direct `SUBJECT PAT [= REPL]`.
- `IR_PATTERN_*` = STITCH boxes ONLY. The per-element builders (LIT/ANY/SPAN/LEN/…) are the ABANDONED pre-D7
  era — do NOT resurrect them. The real design (D7 PIVOT `d7ba0fd9` → `52fce031` `rt_pattern_build` +
  `rt_pattern_stitch_cat`/`_alt`; B3 STITCH-ALT `7a12aedd`; B6 STITCH-CAT `409f62a9`/`a59f38b8`; FZ-3
  `18133720` + FZ-4 `6141434` folding): every VARIANT-free subpattern is constant-folded into a sealed
  `IR_REF_INVARIANT` blob; only VARIANT parts are stitched at the reference site via `IR_PATTERN_CAT`/`_ALT`
  stitch boxes; `IR_PATTERN_CAPTURE` is passthrough (FZ-4); `IR_PATTERN_DEFER` = `*EXPR`; `IR_DTP_ASSIGN` =
  stored-pattern `.`/`$` (DTP frag, `src/include/dtp.h`). **[HISTORY CORRECTED 2026-07-04, case-fixed grep:
  `rt_pattern_stitch_*`/`rt_pattern_build` were superseded PRE-parent by the freeze+blob design — do NOT
  resurrect them; the parent snapshot is the final authoritative form, and `sno_freeze_pat_graph_entry` lives
  in the parent's `lower_snobol4.c`, RECOVERED to disk — see FOLD + the PARK-NEVER-DELETE directive below.]**
- `IR_REF_INVARIANT` (1) = the folded-constant sealed blob that VARIANT stitching references.

**LADDER (incremental, keep build green each rung; land one matcher end-to-end at a time):**
- [x] **SN4-PAT-0 ENUM** — re-add the family to `IR_e` before `IR_OP_COUNT` (additive; `-w` build so no
  exhaustiveness break; inert until lowered). LANDED 2026-07-04, `make scrip` green. **[CORRECTED same day
  (Lon): the initial re-add faithfully copied the parent snapshot's 24 per-element `IR_PATTERN_*` builders —
  but those were the ABANDONED pre-D7 era (a grep-alternation bug hid the stitch history). Dropped to the
  stitch-era five: `IR_PATTERN_CAT`/`_ALT` (stitch boxes), `_CAPTURE` (passthrough), `_DEFER`, + re-added
  `IR_DTP_ASSIGN`. Family is now 34 members (28 `IR_MATCH_*` + `IR_REF_INVARIANT` + 5). Rebuilt green.]**
- [x] **SN4-PAT-1 TEMPLATE-REVIVE (LEN first)** — LANDED 2026-07-04, build green. `bb_match_len.cpp` back in the
  Makefile (source list + compile rule); it compiles against today's headers with **ZERO drift** (BB-FIXUP
  `547de08d` had kept it current — no `IR_node_alloc`/`bb_build_flat` reconciliation needed after all).
  `bb_match_len()` declared in `bb_templates.h`; `case IR_MATCH_LEN` added to `emit.cpp` dispatch (beside
  `IR_TO`, line ~724). Inert until SN4-PAT-2 emits the node, so Icon + existing SNOBOL4 subset unchanged.
  NOTE for SN4-PAT-2: the template reads `_.op_ival` (the LEN count) and emits the anchored δ+n≤Δ advance with
  γ/ω ports — it assumes it sits inside a floating harness, so SN4-PAT-2 must also supply the retry-at-each-
  start-position loop (that's what `IR_MATCH_HEAD`/`IR_MATCH_RETRY`/`IR_MATCH_ADVANCE` are for) unless the
  program is `&ANCHOR`-mode.
- [x] **SN4-PAT-2 LOWER-LEN** — LANDED 2026-07-04 (this session). `L LEN(3) . X` → `abc` m3==m4==oracle; bare
  `L LEN(3) :S/F` matched/nomatch both paths both modes; conditional-capture semantics oracle-pinned (X untouched
  on failure); corpus m3 115→117, m4 FAIL set byte-identical to pre-session baseline (stash-verified). DESIGN
  (Lon directive, this session): the 3-box HEAD/RETRY/ADVANCE harness was REPLACED mid-rung by ONE generator box —
  `IR_MATCH_HEAD` is generator-kind (`ir_query.c`), α = `rt_match_enter` (stateless DESCR→{ptr,len} mirroring
  `rt_scan_enter`, sets Σ/Σlen for capture) + start=0 + r14d=start + jmp γ; β = start+=1, bounds vs Δ, `g_anchor`
  gate, loop — the unanchored retry IS the Byrd resume, `bb_to.cpp` shape. Pattern-fail edges β-stamp via local
  `sno_ω_to` (lower_icon.c precedent); `fJ` chain-reachability comes free from the stock generator-kind ω rule
  (the 3-box BFS special-case was reverted). `bb_match_retry.cpp`/`bb_match_advance.cpp` restored to pre-session
  bytes, unwired, DEAD under this design. Capture = `IR_MATCH_ASSIGN_COND` → `bb_match_capture` phase-1 COND arm
  (op_off = head's start slot, operands=[pat-entry, harness-box]); op_sval whitelist in `walk_bb_node` preamble
  grew the op. NOTE for SN4-PAT-3..N: single-element capture equates pattern-start with attempt-start; multi-
  element CAT needs the phase-0 SAVE arm + its own saved-δ slot. `= REPL` splice still bombs (deferred, wall text
  updated at the old `:257` site).
- [x] **SN4-PAT-3a LIT** — LANDED 2026-07-04 (this session). `bb_match_lit.cpp` written fresh (never existed;
  `IR_MATCH_LIT` had no template — do not confuse with the orphaned pre-family `bb_lit.cpp`, unwired, park-
  candidate). memcmp-based, β rewinds δ by n (adopted from `bb_lit.cpp`'s pattern — needed once CAT chains
  backtrack through a matched LIT). Oracle-pinned: anchored/floating/absent/capture, empty lit, overlong,
  tail-boundary, capture-untouched-on-fail — m3==m4==oracle all paths.
- [x] **SN4-PAT-3b ANY/NOTANY** — LANDED 2026-07-04. Templates pre-existed on disk, unwired; wiring exposed a
  live bug on first-ever execution: the single-char fast path emitted `x86("cmp","sil",imm)` — the `x86()`
  dispatch has no 8-bit-register case, so it silently returned empty (no bomb) rather than failing loud,
  leaving the branch testing stale flags from the bounds check. Fixed: `sil`→`esi` (movzx already zero-
  extends). **Any other unwired template calling `x86()` with an unencodable form has the same latent bug —
  the dispatch declining silently instead of bombing is an emitter-wide footgun, not scoped to this rung.**
  Literal-charset-arg subset only (the parked file's `dval=1.0` var-arg tag is the DIVISION-RULE flag pattern,
  not carried over).
- [x] **SN4-PAT-3c SPAN** — LANDED 2026-07-04. **Real finding:** `_.x86_scratch_off` (read by `bb_match_span`/
  `_arb`/`_arbno`/`_break`/`_breakx`) is declared in `sm_emit_t` and read by five templates but was **written
  nowhere in the codebase** — permanently 0 via static zero-init, a live TMP-ERADICATE violation (any value
  legitimately at frame slot 0 gets silently clobbered) that was invisible only because nothing reading it had
  ever been dispatched. Fixed at LOWER: granted `IR_MATCH_SPAN` a slot in `ir_drive_slot_assign`
  (`nd->tmp = base+k*16; k+=1;`, mirrors the `IR_MATCH_HEAD` grant one line above it), then
  `g_emit.x86_scratch_off = drive_value_slot(nd)` in the DRIVE dispatch — zero emitter-side allocation, per
  rule. Verified the grant does real work (not just satisfies the FATAL-if-ungranted check) with a slot-
  collision probe: two globals alive across the SPAN scratch write, sum checked post-match against oracle.
  **⚠ CARRY FORWARD — BREAK/BREAKX (next in tracker order) read this SAME unwritten field. Grant it in
  `ir_drive_slot_assign` (same one-line pattern) BEFORE wiring their dispatch cases, or this exact landmine
  reappears.** ARB/ARBNO inherit the identical defect when their turn comes later in the ladder.
- [x] **SN4-PAT-3d BREAK/BREAKX** — LANDED 2026-07-04. Applied the SPAN lesson up front instead of rediscovering
  it: both templates read the same never-written `_.x86_scratch_off` (BREAKX uses both `+0`/`+4`, same as SPAN
  — one 16B slot covers it), so both got the `ir_drive_slot_assign` grant (`k+=1` each, same pattern) BEFORE
  their dispatch cases went live — first build was clean, no FATAL. Literal-charset-only subset (matches
  ANY/NOTANY/SPAN precedent). Oracle-pinned: BREAK head/absent/empty/zero-length-at-cursor, BREAKX head/zero-
  length-retry/absent, all m3==m4==oracle. **Two-matcher collision probe** (BREAK + BREAKX both live in one
  graph, two globals alive across both scratch writes, non-colliding sum) confirms independent per-node slots
  — the grant generalizes correctly when multiple scratch-using matchers coexist, not just one at a time.
  **⚠ CARRY FORWARD — ARB (later in tracker order) reads this SAME field. Grant it before wiring.**
- [x] **SN4-PAT-3e TAB/RTAB** — LANDED 2026-07-04. Separate opcodes (`IR_MATCH_TAB`/`IR_MATCH_RTAB`), int-literal
  arg baked directly into `IR_LIT(nd).ival` at LOWER (no operand node, no `ir_operand_push` — same as LEN;
  confirmed neither is in `ir_node_produces_value()`, so no `nd->tmp` grant applies or is needed; emitter reads
  the constant via the generic `op_ival` preamble and bakes it as an x86 immediate, never a memory load). No
  scratch slot required (unlike SPAN/BREAK/BREAKX). **Bug caught before it hit the corpus:** `bb_match_tab.cpp`
  enforced the forward-only constraint (`current_cursor > n → fail`) but had **no upper-bound check against
  `r15d` (Δ)** at all — `TAB(99)` on a 10-char subject incorrectly matched, jumping the cursor to 99 (past the
  subject end). Found by direct comparison against `bb_match_len.cpp` (the correct sibling doing an analogous
  bounds check via addition) rather than the full monitor harness — justified here because the divergence was
  already bracketed to one un-composed statement in a template authored this same session, not inherited logic;
  fix verified empirically against oracle both pre/post, including fencepost cases (`n==Δ` succeeds, `n==Δ+1`
  fails, `n==0` succeeds) since bounds-check fixes are exactly where off-by-one errors hide. Fix: added
  `cmp r15d, n; jl ω` before the existing forward check. **`bb_match_rtab.cpp` was NOT touched** — its overlong
  case (`RTAB(99)` on a 10-char subject) already failed correctly, but by accident: `Δ-n` underflows to a
  negative signed value when `n > Δ`, and any non-negative cursor position compares "greater than" a negative
  target under signed `jg`, so it fails for an incidental reason rather than an explicit check. Left alone
  since it isn't broken and isn't this rung's scope — flagged here in case a future rung's fencepost probe
  finds a case where the accident doesn't hold (e.g. `n` chosen so `Δ-n` wraps positive again at extreme
  magnitudes — not exercised, not ruled out).
- [x] **SN4-PAT-3f TAB/RTAB TWO-MODE RETROFIT** — LANDED 2026-07-04 (Lon-directed proof-of-concept). **The gap:**
  every SN4-PAT-3 matcher (LEN through RTAB) gated the AST shape at LOWER time (`t->c[0]->t == TT_ILIT`) and
  `sno_fatal`'d on anything else — meaning none could accept a variable/computed argument, which is arguably
  the *more* common real-world SNOBOL4 shape (`TAB(I)` far more common than `TAB(3)`). **The correct precedent,
  already live in this codebase:** `IR_SCAN_TAB`/`_MOVE`/`_POS` (Icon) do zero shape-checking at LOWER — the
  argument is lowered as an ordinary expression (in fact `IR_SCAN_TAB` isn't even a dedicated lowering arm; it's
  a generic `IR_CALL` whose opcode gets *retagged* post-hoc by `icn_retag_scan_body` purely from the builtin
  name) — and the EMITTER's DRIVE case is the ONLY place that folds: `a0->op == IR_LIT_INTEGER` → bake immediate
  (`op_sb`); else → read the operand's already-registered runtime slot via `bb_slot_get` (`op_sa`, sign as the
  discriminant). **Retrofit applied to TAB/RTAB, mirroring this exactly:**
  - `sno_pat_node`'s signature changed from `(IR_graph_t * g, ...)` to `(scx_t * cx, ...)` (deriving `g = cx->g`
    locally) — needed so pattern arms can reach `sx_lower`, the general recursive expression lowerer. Both call
    sites (the one recursive self-call, the one external call from `sno_lower_match`) updated. **This signature
    is now available to every future pattern arm that needs a general argument — the plumbing cost was paid
    once.**
  - `TT_TAB`/`TT_RTAB` LOWER arm: dropped the `TT_ILIT` gate entirely (matching the retag precedent's zero-
    special-casing) — now unconditionally `sx_lower`s the argument, wires it via `ir_operand_push`, returns the
    argument's own entry chain (not the TAB node) since the argument must execute first.
  - `sno_pat_supported`: TAB/RTAB relaxed from `t->c[0]->t==TT_ILIT` to "any argument present" — shape no
    longer LOWER's concern.
  - Emitter DRIVE case: rewritten to inspect `nd->operands[0]`, branch on `a0->op == IR_LIT_INTEGER` exactly
    like `IR_SCAN_TAB`, using `op_sa`/`op_sb` (replacing the old generic `op_ival` read, which is meaningless
    once the constant may live on a *different* node than `nd`).
  - Both templates: replaced the direct `(long)(int)_.op_ival` immediate with
    `IF(_.op_sa>=0, mov rax,FRQ(op_sa+8)) / IF(_.op_sa<0, mov rax,(long)op_sb)`, then unchanged bounds-check
    logic against `eax` instead of a baked constant.
  **Proof, not just passing tests:** dumped the actual `.s` output — `TAB(3)` emits `mov rax, 3` (immediate,
  zero memory access, byte-for-byte the old fast path); `TAB(N)` emits `mov rax, qword ptr [r12+104]` (genuine
  runtime load). Same opcode, same template, provably different code shape depending on what the argument
  turned out to be — not merely "tests pass," the mechanism is visibly correct. Oracle-verified: literal (all
  prior pins re-confirmed unchanged), bare variable (`TAB(N)`/`RTAB(R)`, including runtime-value overlong-
  bounds cases), and a genuine computed expression (`TAB(N+1)`, an `IR_BINOP` operand — proves "any expression,"
  not just "also accepts a variable"). Full corpus regression clean (m3/m4 counts and FAIL set unchanged —
  no existing corpus program yet exercises variable-argument TAB/RTAB, so this is net-new capability, not a
  fix to a previously-failing case).
  **⚠ DECISION PENDING (Lon) — retrofit the remaining 7 (LEN, LIT, ANY, NOTANY, SPAN, BREAK, BREAKX)?** LEN is
  the same int-arg shape as TAB (should be a quick mirror). LIT/ANY/NOTANY/SPAN/BREAK/BREAKX are all
  string/charset-arg shape — a DIFFERENT retrofit (fold check becomes `a0->op==IR_LIT_STRING`, general path
  reads a string descriptor's pointer+length instead of one int) — and SPAN/BREAK/BREAKX additionally still
  carry the scratch-slot grant from SN4-PAT-3c/3d, which needs to keep working alongside the new operand-based
  charset. Not yet started; the plumbing (`sno_pat_node`'s `cx` signature) is in place for whoever picks this
  up.
- [x] **SN4-PAT-3g POS/RPOS/REM/ARB** — LANDED 2026-07-04. POS/RPOS = one opcode (`IR_MATCH_POS`) + `"r"` sval
  marker per parked design (existing-IRs-only constraint), built TWO-MODE FROM BIRTH (TAB recipe: operand +
  emitter fold; `RPOS(N)` variable-arg oracle-proven). REM/ARB take scratch grants; REM gained α-save/β-restore
  (its consumption Δ−entry isn't recomputable, unlike LIT's fixed n); ARB added to `ir_is_generator_kind`
  (its β IS extend-and-retry) and its β exhaust path fixed to restore entry cursor (box invariant). **Parser
  fact learned:** bare `REM`/`ARB` (no parens) arrive as `TT_VAR "REM"` — the parked TT_VAR name-dispatch arm
  is load-bearing; restored for REM/ARB only (FENCE/ABORT/BAL names fatal until their rungs). **Ops note:** a
  vanished-on-rebuild fatal traced to a suspected stale link — `make ... | tail -1` hides whether the edited
  TU actually recompiled; force `rm` the .o when in doubt. All 13 session pins re-verified byte-identical;
  corpus unchanged (138/137) — single-element POS/REM/ARB are rare in corpus; the unlock arrives with CAT.
- [x] **SN4-PAT-3h CAT + phase-0 capture SAVE** — LANDED 2026-07-04 (this session). **CAT is NODE-FREE in the
  live single-HEAD design** — the parked `IR_MATCH_CAT` was a subgraph SUCCEED-sink; here pattern success
  threads straight to `sJ`, so concatenation is pure edge-threading with no node and no template (`bb_match_cat.cpp`
  stays UNWIRED — do not add it). `case TT_SEQ` in `sno_pat_node`: lower right-first `(succ,fail)`, then left with
  `succ = right-entry`; return left-entry. Deterministic elements' ω already point at `fail` (=head=retry-position,
  correct SNOBOL4 — SPAN/BREAK/LEN never back off); the ONLY resumable leaf today is ARB (generator-kind), so if the
  left tail `ir_is_generator_kind`, re-point right's tail-ω at it via `sno_ω_to` (β-aware) — the rc/lc tail nodes are
  recovered by the parked `g->all[before]` first-allocated-is-rightmost-leaf trick. `sno_pat_supported` relaxed to
  admit `TT_SEQ` recursively.
  **phase-0 capture SAVE (the SN4-PAT-2 multi-element note, now resolved):** a capture spans `[inner-start, current)`,
  NOT `[attempt-start, current)` — so `TAB(3) LEN(2) . V` on `abcdef` must yield `de`, not `abcde`. Added additive enum
  `IR_MATCH_ASSIGN_SAVE` (right after `_COND`): a phase-0 node placed at the capture's OPEN that does `mov FR(off),r14d`
  into its OWN δ-slot; the phase-1 COND reads that slot (`operands[1] = save`, so `op_off = drive_value_slot(save)`).
  Wiring per rung: enum (`IR.h`) · δ-slot grant in `ir_drive_slot_assign` (`k+=1`, HEAD one-liner precedent, `scrip_ir.c`) ·
  DRIVE case `op_off=own slot, op_phase=0` + dispatch case → `bb_match_capture()` + op_sval whitelist add (all `emit.cpp`) ·
  the template's phase-0 arm was MISSING `jmp γ` (never exercised pre-session) — added (`bb_match_capture.cpp`) · LOWER
  `TT_CAPT_COND_ASGN` rewritten to emit SAVE→inner→COND and return the SAVE as the capture entry. Single-element captures
  still pass (SAVE just records the attempt-start = old behavior).
  **RESULTS (oracle=`sbl -b`, m3=`--run`, m4=`--compile`+gcc; all m3==m4==oracle):** crosscheck patterns 8→13
  (044 pos, 045 rpos, 046 tab, 047 rtab, 048 rem, 049 arb, 055 concat_seq now green — the deterministic-concat +
  multi-capture set); capture rung 2→4 (060 multiple, 061 in_arbno); mode-3 ladder total 86→93; ZERO regressions on the
  8 already-green rungs (hello/output/assign/concat/arith_new/control_new/functions/data). NOT YET regenerated: the
  `.s` artifacts (handoff step 4 — capture codegen changed, so `util_regen_{benchmark,feature,demo}_s_artifacts.sh` owe a
  commit) — a follow-up must run them.
- [x] **SN4-PAT-3h ALT** — LANDED 2026-07-04 (this session). Phased `IR_MATCH_ALTERNATE` (mirrors the capture
  phases): phase-0 SAVE records the ALT-entry cursor into a scratch slot (grant in `ir_drive_slot_assign`,
  `k+=1`); phase-1 RESTORE reloads it before each subsequent alternative so a failed cursor-advancing
  alternative can't leave the next one mid-input. Alternatives chain via ω: `alt[i].fail → RESTORE_{i+1} →
  alt[i+1]`, last → outer fail, each `alt.succ → succ`. `sno_pat_node` `case TT_ALT`: flatten the left-assoc
  spine L-to-R, build `save = IR_MATCH_ALTERNATE` (n_operands==0 ⇒ phase 0), loop i=na-1..1 lowering alt i and
  minting a RESTORE (n_operands==1, operand=save ⇒ phase 1, `op_off = drive_value_slot(save)`), then alt 0 with
  `fail = RESTORE_1`; `lc_γ_to(save, e0)`; return save. Template `bb_match_alt.cpp` rewritten (was bare
  `x86_pair_loop`) as the two-phase `mov FR(off),r14d`/`mov r14d,FR(off)` + `jmp γ`, wired in the Makefile;
  DRIVE + dispatch in `emit.cpp`; gate relaxed for `TT_ALT`.
  **EMITTER FINDING (carry forward — bit ALT, will bite FENCE/ARBNO too):** the flat chain-BFS worklist
  (`emit.cpp` ~1350–1392, TWO passes) enqueued every node's γ but followed ω ONLY for BINOP/CALL/SUBSCRIPT/
  generator-kind — so an **ω-only backtrack target** (the ALT RESTORE, reached only via a preceding
  alternative's ω) was never discovered, never emitted, and its ω silently defaulted to `main_ω` (whole graph
  collapsed to one alternative). Root fix: **the match family's ω is a genuine control edge** (next alternative /
  fail handler), so both BFS passes now follow ω for `op ∈ [IR_MATCH_LIT, IR_MATCH_ASSIGN_SAVE]`. Behavior-neutral
  for every prior test (their ω targets — HEAD, next element — were already discovered; the enqueue dedups), only
  `.s` node-numbering shifts (never a gate). Any future SN4-PAT node that is reached ONLY via ω (FENCE seal-back,
  ARBNO retry) is now discoverable for free.
  **RESULTS (m3==m4==oracle):** crosscheck patterns 13→15 (050 alt_two, 051 alt_three), mode-3 ladder 93→95, ZERO
  regressions (8 green rungs full; capture/strings/keywords unchanged; m4 spot-checked on the green rungs).
  **053 alt_commit still fails** — it is `P = ('a'|'b'|'c'); X P`, a STORED-pattern reference (`X P`), i.e.
  DEFER/stored-pattern territory (a later rung), NOT pure ALT. NOT YET regenerated: the ALT `.s` feature
  artifacts (handoff step 4 owes another `util_regen_feature_s_artifacts.sh` run — codegen changed again).
- [x] **SN4-PAT-3i FENCE** — LANDED 2026-07-05 (Claude Sonnet 5). Bare `FENCE` and the `FENCE(P)`
  atomic-group form now lower in the single-HEAD model. FINDING THAT SHAPED IT: every deterministic
  matcher fails straight to `head` (the retry-at-next-anchor box; ω=`fJ`) — there is no left-to-right
  backtrack chain among deterministic elements — so FENCE cannot be a `β→ω` box (a later element's
  failure never reaches it). FENCE is instead node-free (the landed-CAT precedent, zero new IR/template/
  Makefile touch) and works as a **fail-retarget**: in a pattern sequence, a fence SEALS — every element
  to its right fails to the statement-level `cx->pat_fail` (=`fJ`, new `scx_t` field) instead of `head`,
  cutting off both anchor-retry and left-generator resume, exactly the manual's semantics (forward = null
  match, no effect; backtrack into it = whole match fails). `FENCE(P)` additionally lowers `P` with the
  pre-seal fail (so `P` retries normally on forward-fail) — the seal only blocks re-entry after `P`
  succeeds. `lower_snobol4.c` only (+59/-15): `sno_is_fence`/`sno_seq_has_fence` helpers; `TT_FENCE` +
  `TT_VAR "FENCE"` leaf arms; `TT_SEQ` flattens the left-assoc spine and retargets per-element fail past
  the first fence (fence-free sequences keep the untouched 2-way CAT path byte-for-byte); `sno_pat_supported`
  child-aware for `FENCE(P)`. VERIFIED vs SPITBOL x64 oracle: 058/059/060/067/069/100-104/107 all m3==oracle
  (one bug caught+fixed pre-measurement: standalone `FENCE(P)` was matching null and dropping `P`). Crosscheck
  both modes 154→168 (+14), DIVERGE=0, mode-4 FAIL back to the 3 parked (082/099/213); non-pattern FAIL set
  byte-identical to baseline (zero regressions); patterns 15→29; Icon smoke 12/12×2. Artifact regen
  (feature/benchmark/demo) = 0 changed — fence tests live in the crosscheck corpus, compiled on-the-fly,
  no committed `.s`. Remaining pattern fails are ARBNO, `*VAR` deferred-eval, and pattern-as-value/via-var
  (105/106 need the last one) — FENCE was never scoped to cover them.
  **NEXT: ABORT/BAL, then ASSIGN_IMM (`$`)/DEFER — pattern-as-value (STITCH) is the other
  large lever whenever Lon wants that path instead.**
- [x] **SN4-PAT-ARBNO (ZB-5 deterministic-body v1)** — LANDED 2026-07-05. `ARBNO(P)` for a DETERMINISTIC body
  P lowers in the single-HEAD model with **NO per-iteration COLLECTION and NO stack** — the key finding:
  backtracking through deterministic iterations cannot yield a new alternative, so the first extension-failure
  IS total exhaustion; only three 4-byte cursors are needed (entry δ / last-yield δ / cur_before), packed in
  ONE 16B `ZK_RAW` zls slot. **Three phases share `IR_MATCH_ARBNO`, discriminated by `IR_LIT(nd).ival` staged
  into `g_emit.op_phase` at drive time** (the ALT-precedent proof that op_phase survives the walk; op_ival would
  be DRIVE_FILL-clobbered): **G** (phase 0, generator-kind, 0 operands, FIRST-allocated so TT_SEQ's tail rule
  finds the β surface) — α saves entry+yield=δ, `jmp γ` (the null yield, SPITBOL shortest-first); β restores
  δ=yield (right neighbour may have consumed cursor before failing), records cur_before, `jmp ω` — **G.ω is
  REPURPOSED as the body-entry edge** via `lc_ω_to(G, body_entry)`, the construct's real fail exit lives on F.
  **K** (phase 1, operand[0]=G) — body-success landing: `δ==cur_before → jmp ω(=F)` (the 4/28 zero-advance
  guard), else yield=δ, `jmp γ` (yield one more). **F** (phase 2, operand[0]=G) — exhaust: δ=entry,
  `jmp ω`(outer fail); its template `def β` ALIAS lands both body-fail edges (bodies stamp fail β-wards via
  `sno_ω_to` + `IR_MATCH_ARBNO` is now generator-kind). **Files:** `ir_query.c` (ARBNO → generator-kind);
  `zeta_storage.c` (grant row: phase-0 node only, `n_operands==0` guard, one 16B ZK_RAW — **audit=0 justified:
  template `bb_match_arbno.cpp` authored AND reads the field the same commit, the landed audit-0 rule**);
  `lower_snobol4.c` (`sno_pat_deterministic` recursive gate rejecting ALT/ARB/ARBNO/FENCE bodies;
  `sno_contains_arbno` capture gate; `TT_ARBNO` arm building G/F/K; `sno_pat_supported` ARBNO + capture arms);
  `bb_match_arbno.cpp` (REWRITTEN in place — the dormant `bb_child_lbl`-era template had the P5 cursor-restore
  bug; new three-phase body); `emit.cpp` (dispatch arm + DRIVE staging own-slot-via-operand[0]); `Makefile`
  (both the `RT_PIC_SRCS` list and the `scrip:` compile rule). **VERIFIED vs SPITBOL x64 oracle** (probe set
  `/tmp/arbno_probe.sno` + no-capture `Q1..Q11`): extension, zero-occ, shortest-first, null-body no-loop,
  multi-element body (ANY ANY), SPAN body, LEN(2) body, unanchored head-retry, **cursor-restore (`ABABAC` POS(0)
  ARBNO('AB') 'AC' RPOS(0)** — the β-must-restore case), and BOTH forced-FAIL cases (`AAX`, odd-length under
  RPOS) — **m3==m4==oracle on all**. Crosscheck both modes **168→171** (+3), **DIVERGE=0**, m4 FAIL back to the
  3 parked {082,099,213}, signal-abort set 26==26 vs HEAD (zero new crashes); the 3 emit gates PASS; icon smoke
  12/12×2. Artifact regen (feature/benchmark/demo) run at handoff — ARBNO tests compile on-the-fly in the
  crosscheck corpus, no committed `.s`. **v2 (generator body) LANDED 2026-07-05 — see
  SN4-PAT-ARBNO-2 below (per-iteration COLLECTION + the ALT-RESUME prerequisite); the counterexample
  `'AAAB' POS(0) ARBNO('AAA'|'AA') 'AB' RPOS(0)` now == oracle both modes.
  **FINDING — CAPTURE-OVER-GENERATOR IS PRE-EXISTING-BROKEN (ARB shares it):** `ARBNO(P) . V X` (a `.`-capture
  whose span wraps a generator) mis-compiles — the phase-1 COND between the generator and its right neighbour X
  severs the β-resume chain (X's fail reaches `head`/retry, NEVER the generator's β), so the generator never
  extends. **PROVEN pre-existing at clean HEAD:** `ARB . V 'B'` on `'AAAB'` returns `[]` not `[AAA]` with ZERO
  of my changes applied. Gated for now: `sno_contains_arbno` makes a capture whose span contains ARBNO
  UNSUPPORTED (052_pat_arbno → SKIP, honest capability boundary; ARB-capture left exactly as baseline, untouched).
- [x] **SN4-PAT-CAPTURE-STACK (Lon directive 2026-07-05) — LANDED 2026-07-05 (Fable). Capture-over-generator
  un-gated: frames on a per-box STACK, `++` on α / `--` on β, exactly as directed.** SAVE's 16B zls slot is now
  `{+0 buf: GC_MALLOC_ATOMIC u32[] ([0]=cap, frames from [1]) — ZK_PTR_GC, so dead buffers collect free; +8 gen;
  +12 sp}`; `rt_cap_push/pop/top` in `pattern_match.c`; `rt_match_enter` bumps a per-match generation and a
  stale-gen slot lazily resets sp=0 — that kills the γ-exit-live success-leak per match AND validates
  ZC_INIT_ZERO-fresh ζ frames (v2 COLLECTION moves this reset into the iteration machinery when it lands).
  LOWER rewiring: COND stays first-allocated (TT_SEQ tail trick finds it); SAVE minted BEFORE the inner so the
  inner lowers with fail=SAVE — every inner exhaust pops before failing leftward (β-aware, so a left generator
  still resumes); COND.ω = the backtrack-IN edge → inner-tail's β when the inner is a generator, else SAVE.β;
  `IR_MATCH_ASSIGN_COND`+`_SAVE` added to `ir_is_generator_kind` so all re-points land β-wards. **NEW HELPER
  `sno_resume_ω_to`** (both TT_SEQ re-point sites): a capture-COND's ω is its inward resume edge — clobbering it
  severs the capture's own chain; re-points chain through `operands[1]` (SAVE's ω) instead. Proven by
  `(ARB . V) (ARB . W) 'Z'` on 'AABZ' → `[][AAB]` == oracle (without it, W's generator is skipped). Gate
  `sno_contains_arbno` DELETED (single user). **Oracle-proven fixes:** `ARB . V 'B'`/'AAAB' `[]`→`[AAA]`;
  mid-pattern variant `fail`→`[AAA]`; 052_pat_arbno SKIP→PASS both modes; capture-inside-ARBNO-body
  `ARBNO('a' . V)` → `[a]`; nested `(LEN(1).A LEN(2).B).C` → `a/bc/abc`. **Corpus:** m3 172 pass (was 171;
  FAIL 90→89 = exactly 052), m4 172 pass / 3 FAIL {082,099,213} / 86 skip, DIVERGE=0; a controlled HEAD-vs-rung
  compile-skip diff proves the m4 delta == {052} exactly, nothing regressed in — the prior watermark's m4
  168/90 was stale by 3 environmental skips (FAIL sets byte-identical + the m3 delta rules out runtime flips ⇒
  HEAD-today m4 = 171/3/87). Icon smoke 12/12×2; emit gates ×3 + sno_pat_reg PASS; feature `.s` regen
  auto-committed (18 capture-bearing pattern tests — helper-push α, real β pop labels, inner-fail→SAVE.β all
  visible). `1017_arg_local` --compile SIGABRT is pre-existing (in both skip sets). **Accepted v1 limit:** when
  a seq re-point chains through a capture, the pop on that path is elided (SAVE.α re-pushes on resume; bounded
  per match by the gen-reset; top-reads stay correct).
  **FINDING A — EAGER-ASSIGN (pre-existing, pinned):** the dcap deferred-capture protocol
  (`rt_dcap_begin/end_ok/end_fail`, pattern_match.c) is ORPHANED — declared at emit.cpp:395, never called — so
  `.` assigns at subpattern-success; a FAILING match still mutates the target (probe: `V='old'; 'ZQ' ? 'Z' . V
  'NOPE'` → oracle `V=old`, SCRIP `V=Z`). No crosscheck test distinguishes (064 tests no capture despite the
  name). Own rung: wire dcap begin/end at the match entry + success/fail exits.
  **FINDING B — SEQ-CHAIN-THROUGH-DETS (pre-existing, improved here, residual pinned):** a deterministic
  element between the fail point and a left generator blocks the resume — the le_tail trick sees only the
  rightmost leaf, so in `(ARB . V) 'B' 'C'` a 'C' failure retries the anchor instead of extending ARB. Probe
  'ABQABC': oracle `[ABQA]`, SCRIP `[QA]` (HEAD gave `[]` — this rung improved it; the residual is the det-tail
  chain). Own rung: SN4-PAT-BETA-CHAIN — β pass-through on deterministic matchers or a leftward β-surface scan
  in TT_SEQ.
- [~] **SN4-PAT-FOLD** — STRING TIER LANDED 2026-07-05 (chat session, Opus 4.8, SCRIP `1d205f46` code + `25c170ee` .s); BLOB TIER remains.
  **WHAT LANDED (string-valued stored patterns):** a bare variable in pattern position (`subject pat`) now lowers to
  `IR_MATCH_DEFER` instead of bombing at the wall. KEY SEMANTIC FINDING (oracle-pinned): `'foo' 'bar'` is STRING
  CONCATENATION → the string `"foobar"` (`DATATYPE`=STRING), NOT a pattern — only `|`/true-pattern-ops build a
  PATTERN value. So `pat='foo' 'bar'; subject pat` needs NO blob: `rt_defer_match`'s DT_S path matches the stored
  string literally. Six sites: `sno_pat_supported` accepts bare TT_VAR; `sno_pat_node` TT_VAR→`IR_MATCH_DEFER`
  (op_sval=name, op_ival=0); emit.cpp op_sval-list + template-dispatch(`bb_match_defer`) + DRIVE_FILL populate-case
  + both ω-queue range checks (DEFER is enum-outside LIT..ASSIGN_SAVE → folded explicitly); Makefile gained
  `bb_match_defer.cpp` (was libscrip_rt-only → mode-3 link error). **MEASURED: crosscheck m3 187→189, m4 187→189,
  DIVERGE=0** (W02_seq_basic + W02_seq_nested newly PASS oracle-exact; ZERO regression). GC-stressed (SCRIP_GC_STRESS=1)
  BYTE-IDENTICAL (189/87); both emit gates green; Icon crosscheck 4/0 (DEFER is SNOBOL4-only, Icon codegen untouched).
  Pattern-VALUED stored vars (W03 alternation, DT_P) now COMPILE and clean-FAIL (bomb→fail; `rt_defer_get_pat_fn`
  returns NULL) — the honest degrade until the blob tier.
  **BLOB TIER REMAINS (the real seal-blob rung):** `IR_REF_INVARIANT` is in the enum but has NO emit arm (grep
  emit.cpp = 0); `xa_pattern_blobs()` is a shell gated on `xa_pat_blob_invariant_n`; the parked freeze functions
  (`sno_freeze_pat_ir`/`_graph_entry`, parent `lower_snobol4.gz5-parked-41b53078.c:689-738`) are INCOMPLETE —
  `sno_freeze_kids_attach` builds the CAT/ALT kids array then `(void)(zk)` DISCARDS it, so a verbatim port drops
  children. So the blob tier is a RECONSTRUCTION not a port: (1) build the `IR_REF_INVARIANT` emit arm that seals a
  constant pattern subgraph into an invocable blob + registers it; (2) `TT_ASSIGN` hook: pattern-valued RHS → seal +
  store a DT_P handle (the value `rt_defer_get_pat_fn` fetches: `val.v==DT_P && val.p`); (3) the match already invokes
  it via `bb_match_defer`'s DT_P branch (`call rt_frame; call the fn`). Oracle-pin W03 outward. `bb_pat_build.cpp`
  parked; `src/include/dtp.h` on disk; `rt_pattern_stitch_*`/`rt_pattern_build` SUPERSEDED — do NOT resurrect.
- [x] **SN4-PAT-ARBNO-2 (ZB-5 v2: generator bodies via per-iteration COLLECTION) — LANDED 2026-07-05 (Claude Fable 5).**
  `ARBNO(P|Q)` and friends re-choose FINISHED iterations; 054_pat_arbno_alt FAIL→PASS both modes; the on-record
  counterexample `'AAAB' POS(0) ARBNO('AAA'|'AA') 'AB' RPOS(0)` == oracle both modes (iteration 1 re-chosen
  'AAA'→'AA' after iteration 2 exhausts).  **LOAD-BEARING DISCOVERY — ALT WAS NEVER RESUMABLE:** `IR_MATCH_ALTERNATE`
  was absent from `ir_is_generator_kind` and its template had NO β arm — once an alternative succeeded there was no
  path to the next, so `('a'|'ab') 'c'` on 'abc' FAILED vs oracle at clean HEAD (collections alone could not have
  fixed 054).  **ALT-RESUME (the prerequisite piece, landed first and independently probed):** slot repartitioned
  `{+0 cursor save (4B RAW), +8 resume continuation (8B ZK_PTR_CODE)}`; TT_ALT rewired to UNIFORM JOIN boxes —
  alternative i's success lands J_{i+1}.α (MARK: `lea rax,[rip+L0]` = its OWN reload arm, store to [slot+8], jmp
  ω=outer-succ) and its failure lands J_{i+1}.β/L0 (reload cursor, jmp γ=alternative i+1; β-wards free via
  sno_ω_to once ALTERNATE is generator-kind); the trailing T=J_n is the SAME box with γ=outer-fail (resume exhaust
  restores the entry cursor then fails leftward, β-aware); SAVE.β = `jmp qword [slot+8]` — the resume-in REPLAYS
  exactly where forward-failure of the succeeded alternative would have gone, so deterministic pass-through costs
  nothing and [slot+8] is always written before any possible resume.  NEW ENCODER (template-only rule honored):
  `x86_lea_rip_id` — `lea r64,[rip+L(n)]`, REX.W 8D /5 + the SAME J-record rel32 fixup as jmp/jcc (rel32 is the
  instruction's last 4 bytes in both).  Oracle-probed 6/6 both modes incl. 3-way deep dispatch, capture-over-
  resumed-ALT (V='ab'), unanchored+exhaust-restore.  **ARBNO v2 (roles 3/4/5 ADDITIVE beside v1's 0/1/2 — v1
  byte-untouched):** owner quad 32B `{entry,yield,i,cap | ptr ZK_PTR_GC | pad}`; element = 16B header
  `{prev_rZ, cur_before}` + the body subgraph's CONTIGUOUS slot window; G.β pushes a ZEROED element
  (`rt_zcol_push`, pattern_match.c, dual-built) and REPOINTS rZ=elem+16-min_off so body boxes' [r12+off] become
  per-iteration (header readable at [r12+min_off-16/-8]); K reads header, restores rZ, i++/yield (zero-advance
  way → F.α = resume THIS element's body β for its next way — oracle-pinned BOTH null-alternative orders); F.β
  (body-fail) restores rZ, i==0→exhaust else i--, resume element i via F.γ stamped β-wards at the body's
  first-allocated (rightmost) leaf.  RELOAD LAW held: elem recomputed from (ptr,i) at every owner port.  Geometry:
  G brackets the body with operands[0/1]=first/last body node BY ALLOCATION (optimizer audit: branch_chain only,
  no reorder/compact ⇒ index window exact, grants contiguous); zls_build post-pass computes {min_off,span} per
  owner → `zls_arbno_geom()` → DRIVE stages op_sa/op_sb.  SAFETY AUDIT that shaped the scope: every SNOBOL4 var
  is `global_register`'d ⇒ IR_VAR → bb_var_global (NV/GVA, r12-free) ⇒ NO vslot reads under repointed rZ.
  `rt_zcol_push` = realloc ×2-growth + the zeta_alloc GC_add_roots trick (capture-buf GC ptrs INSIDE elements stay
  collector-visible; roots move with the block; fresh-index memset = the fresh-iteration rule, POP never zeroes);
  ptr/cap PERSIST across anchor retries/statement re-executions (2001-iteration loop torture == oracle both modes,
  no growth).  **NAMING RULING (Lon 2026-07-05): "phase" is a MISNOMER — `op_phase`/template arms are a box-ROLE
  discriminator; concept stands (capture/ALT/ARBNO all use it), rename is a future housekeeping rung.**
  **GATES (sno_pat_v2_ok + sno_pat_v2_tail_gen, honest v3 boundary):** body's RIGHTMOST leaf must be ALT/ARB/
  capture (a deterministic tail exposes no β — chaining THROUGH it is the Finding-B pass-through rung, e.g.
  `ARBNO(ARB 'X')` refused); nested ARBNO refused (element prev_rZ into a realloc-MOVABLE outer collection = the
  RELOAD-LAW escape); FENCE-in-body refused (seal jumps to fJ with rZ still repointed); generator INSIDE an
  alternative refused (the ALT mark records the NEXT alternative — an inner generator's remaining ways would be
  skipped on resume; same residual applies to plain nested ALT outside ARBNO, strictly-better-than-HEAD but
  documented).  **KNOWN v1 LIFETIME RESIDUAL:** MALLOC-arm collections leak at FRAME DEATH (proc returns) — reuse
  within a frame prevents loop growth; retire via the §5f per-activation release list or GC-4; D7 (ZC_COL_MALLOC)
  honored but Lon may want to re-rule toward GC given elements now hold GC pointers.  **EVIDENCE:** ALT probes 6/6
  + ARBNO probes 10/10 (counterexample, deep re-choose 'AAAAAB', both zero-advance orders, capture-over-v2
  W='abab', two-ALT body, total-exhaust) m3==m4==oracle; full crosscheck m3 189→190, m4 189→190 / FAIL(m4) five
  BYTE-IDENTICAL to HEAD {082,099,213,057,W02} / SKIP 82→81, DIVERGE=0 — stash-verified full-corpus fail-set diff
  == exactly {054} both modes (NOTE: the ZB-5-era "3 parked m4 fails" baseline was stale — 057/W02 were already
  m4-FAIL at actual HEAD `1d205f46`); GC_STRESS=1 green on all probe sets; icon smoke 12/12×2; gates
  no_ir_mutation/no_lang/no_slot_alloc/byte_identity/no_handencoded/sno_pat_reg/ir_field_discipline ALL PASS;
  benchmark regen EMIT-FAILs (eval_dynamic etc.) stash-proven pre-existing, corpus-side (benchmark+demo)
  artifacts 0-changed; feature `.s` (SCRIP-side, `test/snobol4/**/*.s`) DID change for ALT/ARBNO-bearing
  tests — correctly, codegen changed there — committed separately by the regen script (an earlier draft of
  this entry wrongly said "0 changed" across the board).  **POST-PUSH REBASE:** origin/main had moved past
  this session's `1d205f46` baseline (a concurrent session landed `7c818c9d` IR_t.tmp ERADICATE + `974c0031`
  Prolog GZ#6) by the time of handoff; `git pull --rebase` hit one real conflict in `emit.cpp` (both sessions
  added an extern near `drive_value_slot` — resolved by dropping this session's now-redundant `zls_off`
  extern and keeping the new `zls_arbno_geom` one), all other files auto-merged clean. Full crosscheck +
  Icon smoke + all 7 gates RE-RUN post-rebase: byte-identical to the pre-rebase numbers above — the merge
  changed nothing behaviorally. SCRIP `dba13602`.
  FILES: x86_asm.h (+encoder, +lea dispatch arm), ir_query.c (+ALTERNATE), bb_match_alternate.cpp (rewritten),
  bb_match_arbno.cpp (+roles 3/4/5), lower_snobol4.c (TT_ALT rewire, TT_ARBNO v2 branch, v2 gates, supported
  relax), zeta_storage.{c,h} (ALTERNATE fields, ARBNO ival-keyed rows, geometry post-pass + export),
  emit.cpp (ARBNO DRIVE + extern), pattern_match.c (+rt_zcol_push).  NEXT: Finding-B det-tail pass-through
  (un-gates `ARBNO(P det-tail)`), nested-ARBNO (needs stable element addressing or GC-4), or the FOLD blob tier.

**⛔⛔ STANDING DIRECTIVE (Lon, restated 2026-07-04) — PARK, NEVER DELETE, parked-language code.**
Park out of the Makefile (the `8f3e4b23` "kept intact on disk" precedent); deletion of parked code is a
directive violation even inside a "reset" commit. **The violation on record:** GZ#5 followed the rule for the
118 templates but DELETED the SNOBOL4 pattern lower wholesale — the parent's `lower_snobol4.c` (1402 lines:
`lower_pat_node`, `sno_freeze_pat_graph_entry`, the match-statement driver, the generator-kind classifier)
was replaced by the 451-line non-pattern rebuild with no on-disk copy kept. **RECOVERED this session** to
`src/lower/lower_snobol4.gz5-parked-41b53078.c` (parked, NOT in the Makefile; build unaffected, verified
green). Emit-side needed no recovery: at the parent, matchers had no per-op dispatch caller (generic
`bb_build_flat` blob path only) — today's arms are written fresh in `emit.cpp`, one line per kind
(SN4-PAT-1's `IR_MATCH_LEN` is the precedent). **Any dead-code sweep (incl. GOAL-DEAD-CODE-SWEEP) must
exempt `*.gz5-parked-*` files and everything in the WIRING INVENTORY above.** SN4-PAT-2..N port FROM the
parked file INTO the live tree.

**WIRING INVENTORY (src scan 2026-07-04 — what exists on disk for re-wiring):**
- **Parser (live):** `src/parser/snobol4/` (`snobol4.l`/`.y` + generated) — full grammar incl. pattern syntax.
- **Lower:** `lower_snobol4.c`/`.h` (live, non-pattern subset complete; `:257` is the wall), `tree_to_sno.c`.
- **Runtime (live in build):** `pattern_match.c` (cset_resolve, `pat_*` atoms, `rt_cap_assign_cursor`,
  `rt_at_cursor`, `rt_defer_match`, `rt_assign_var`; `pat_cat`/`pat_alt` are B0 BOMBs — superseded by stitch),
  `pat_pool.c`, `by_name_dispatch.c`, `xa_pattern_blobs.cpp`, `src/include/dtp.h`.
- **Runtime (parked, not in Makefile):** `bb_pat_build.cpp` (mints `IR_MATCH_*` blob-builders; exempt per
  GOAL-SNOBOL4-BB session-31 note).
- **Templates on disk (kept intact by `8f3e4b23`, API-current per BB-FIXUP):** 23 `bb_match_*` (abort advance
  alt any arb arbno atp break breakx capture cat defer fence head len notany pos rem retry rtab span span_var
  tab — `len` re-wired SN4-PAT-1), 5 `bb_pattern_*` (break capture cat len lit — cat/capture are post-FZ-4
  passthroughs; `lit`/`len`/`break` are abandoned-era, audit before wiring) + `bb_pattern_stub.cpp`,
  `bb_keyword_snobol4.cpp`, `bb_scan_match.cpp`.
- **Dormant backends (X86-ONLY era):** JVM/`SnoPat.java`, .NET/`SnoRt_patterns.il`, JS/`sno_engine.js`,
  WASM/`sno_runtime.wat` — reference semantics only, not wiring targets.
- **Tools:** `src/tools/tmatch_proto.c` (matcher prototype harness).
- [x] **SN4-PAT-EXPR (EXPRESSION datatype + `*EXPR` + EVAL + pattern auto-eval) — LANDED 2026-07-06 (Claude Fable 5).**
  `A = *(X Y Z)` / `EVAL(A)` / `S ? *P` / bare stored-expression-in-pattern all m3==m4==oracle. **DESIGN:** each `*expr`
  carves an anonymous zero-arg dyn-scope proc graph (`EXPR$N`, DEFINE precedent: sJ/fJ→SUCCEED/FAIL, IR_ASSIGN to own
  result_name; live-bound collector loop after the defs loop handles nested `*`), registered via the EXISTING generic
  proc_table→rt_proc_set_fn pipeline both modes — zero new emit machinery; value = `IR_CALL "SNO$MKEXPR"(name-lit)` →
  new **DT_X=15** DESCR (DATATYPE→EXPRESSION); **EVAL** by-name arm: DT_X → `rt_call_named_proc` (FAILDESCR
  propagates failure — `*LT(1,0)` eval-fail oracle-pinned), numerics pass through, **EVAL(<string>) stays a loud
  runtime-compilation wall** (140 moved SKIP→honest FAIL). Pattern context: `rt_defer_match` fetches → DT_X
  auto-invokes → DT_I/DT_R results coerce to string → literal match; inline `*(expr)` in pattern carves too, flagged
  by a `*` NAME PREFIX (printable, GAS-safe, illegal as SNOBOL identifier). `FAIL` reserved-primitive arm added
  (057 DIVERGE→0). **LOAD-BEARING FINDING 1 — IR_lit is an ANONYMOUS UNION (sval/ival/dval overlap): the FOLD arm's
  `sval=nm; ival=0;` ZEROED sval, so IR_MATCH_DEFER matched EMPTY since FOLD landed; its green tests were
  wrong-success coincidences (W02_seq_fail_propagate + 056 empty-capture were this).** Never write two IR_lit members
  on one node. **FINDING 2 — the match-family C-call idiom `push rbx; mov rbx,rsp; and rsp,-16` POISONS the GVA base:
  any callee that re-enters emitted GVA-reading code (blob invocation!) segfaults on `[rbx+k*16]`.** bb_match_defer
  switched to rbp (zero template hits repo-wide); **CARRY FORWARD: bb_match_{capture,arbno,alternate,...}/bb_subject
  share the rbx dance — inert only while their callees never re-enter emitted code; sweep before Rung-B DT_P blobs.**
  Plus a stale-rdi/esi reload in the L0 arm (caller-saved args were dead after the rt_defer_get_pat_fn call).
  **MEASURED: crosscheck m3 190→195, m4 190→195, DIVERGE=0; m4 FAIL {082,099,213,057,W02}→{082,140,213}
  (099/W02/056/057 cured); icon smoke 12/12×2; no-lang + no-IR-mutation gates PASS. `.s` regen owed at handoff
  (defer-template codegen changed).** Files: descr.h (+DT_X), lower_snobol4.c (collector, TT_DEFER value+pattern
  arms, EVAL wall lifted, expr-graph builder), by_name_dispatch.c (EVAL/SNO$MKEXPR/DATATYPE-uppercase+EXPRESSION),
  pattern_match.c (defer invoke/coerce/FAIL), bb_match_defer.cpp (rbp + reload).
- [~] **SN4-PAT-DEFER-CALLOUT — v1 LANDED 2026-07-06 (Claude Fable 5, SCRIP `6e701b9c` + rbx-sweep `6983b386`). Crosscheck m3 195→230, m4 195→230, DIVERGE=0.** Stored true-PATTERN values are AOT-compiled `bb_box_fn` blobs; **DT_P.p = the compiled code address** (Lon: "DT_P builds a bb_box_fn. We are code."). THE DESIGN (the FZ resurrection on the live spine — zero runtime pattern construction, zero new emit machinery): a pattern-valued RHS (`pat='a'|'b'`, `cmd=FENCE(...)`, `W=SPAN(&LCASE)`) carves its own graph via the LIVE `sno_pat_node` (ONE matcher compiler, inline+stored) with SUCCEED/FAIL terminals and NO head (blob = anchored fragment; the CALLER's head retries), registered as proc `PAT$N` through the EXPR$N pipeline — both modes compile+register it for free. **The invocation ABI matched by construction:** the `g_frame_active` epilogue already returns eax=1/99 at γ/ω, `bb_match_defer` already checks `cmp eax,1`, and Σ/δ/Δ (r13/r14/r15) ride the C call — the subgraph's own β-rewind restores δ on blob failure. Assignment lowers to `IR_CALL "SNO$MKPAT"(name)` → DT_P from `rt_proc_get_fn` (one-time code-address fetch at statement position, MKEXPR precedent). Match site was already live. Files: rt.c (+rt_proc_get_fn), by_name_dispatch.c (SNO$MKPAT), lower_snobol4.c (g_sno_pats registry, sno_is_pattern_rhs, sno_pat_collect, assignment hook, post-loop blob builder, **sno_cset_fold** compile-time &LCASE/&UCASE folding in ANY/NOTANY/SPAN/BREAK/BREAKX + gate). Oracle-pinned: W03 bare-ALT-var, 108/068 FENCE-via-*var incl. SEAL semantics (one-shot blob boundary = FENCE semantics naturally — why the fence cluster fell wholesale), 105, 071 two-derefs-with-captures. m4 FAIL 3→19 is PROGRESSION (SKIP 78→27; every new m4 fail also fails m3 identically, DIVERGE=0). PREREQ LANDED same session: **rbx-poison sweep** (`6983b386`) — bb_match_{capture,arbno}+bb_subject alignment scratch rbx→rbp, byte-identical proven. Gates: icon 12/12×2, polyglot 2/2×2, no_ir_mutation+no_lang PASS; artifact regen run (corpus `c83d1b5a` + SCRIP feature .s ×25).
  **NEXT-SESSION BRACKETS (in order):** (1) **FRESH-FRAME WIP, DIVERGE BRACKETED** — `.github/WIP-sn4pat-defer-freshframe-2026-07-06.patch` (40 lines, bb_match_defer: rt_frame→rt_zls_alloc(64K)/rt_zls_release per invocation, LIFO both continuations). MEASURED m3 241/m4 239 (+11/+9; recursive-grammar cluster 115/120/126/131/138/139 all PASS m3) **but DIVERGE=2 (word2, word4): fresh frames cured them in m3, NOT m4** — a real inter-mode lifetime divergence, monitor/bracket it before landing (the shared-static-rt_frame v1 is what's committed; nested `*var` blobs clobber its slots, which is exactly what the patch fixes). (2) **DT_P through user functions** (063-066 fence_fn cluster): a DEFINE'd function returning FENCE(...) — DT_P must survive the call/return path + defer must accept call-result patterns. (3) **β-resume ACROSS the blob boundary** (074/W07 cursor cluster): outer backtrack cannot re-enter a returned blob's internal generator — the resumable-β protocol proper (entry=1 β-dispatch exists in the prologue; needs per-invocation state survival, gates on (1)). (4) remaining non-pattern stragglers: 1011/1013/1015/1017, 082/213, test_case/stack/string + word/cross (include-library, partly gated on (1)). **ADDENDUM 2026-07-06 (later session, Claude Sonnet 4.6):** bracket (1)'s "lifetime divergence" framing is probably WRONG — see the STILL OPEN note on the top-of-file ladder entry above for the corrected `INPUT`-at-EOF failure-propagation hypothesis, repro, and the two known-good FAILDESCR sites to model the fix on. No fix landed; patch remains uncommitted/reverted from the SCRIP working tree.

<!-- ════════════ SNOBOL4 RE-LIGHT LADDER — moved verbatim from GOAL-IR-IMMUTABLE-EMIT.md, 2026-07-06 ════════════ -->

## SNOBOL4 RE-LIGHT LADDER — SNOBOL4 on the post-GZ#5 spine (RELOCATED here from GOAL-SNOBOL4-BB.md, Lon directive 2026-07-04)

**RELOCATION NOTE (2026-07-04).** This is the SNOBOL4-subset re-light ladder (RL-0…RL-9). It was moved here from GOAL-SNOBOL4-BB.md because that file is titled *"SNOBOL4 on the shared BB spine (GZ#5 rebuild)"* — it IS Ground Zero #5 work, and THIS file is the GZ#5 home. The move consolidates the live SNOBOL4 climb with the rest of GZ#5 rather than cross-referencing it.
- **SCOPE FLAG for Lon (NOT silently resolved):** the ICON-ONLY HARD RULE at the top of this file is Icon-climb-scoped — it constrains which `lower_*.c` and which tests the *Icon* rungs may touch. It does not, by itself, govern this relocated SNOBOL4 ladder, so the two now coexist. If you want one unified scope, reconcile that hard rule (e.g. re-title it "Icon-climb scope" or add an explicit SNOBOL4-climb carve-out). Flagged here rather than changed on my own initiative.
- GOAL-SNOBOL4-BB.md **retains** all SNOBOL4-specific detail (monitor RUNG-0/1/2, DEMO-PAT, NRG, PERF-GVA, fail maps); ONLY the RL ladder moved. A breadcrumb there points back here.
- The ladder assumes GOAL-SNOBOL4-BB.md's **"ONE EMITTER FOR ALL LANGUAGES"** FACT RULE (Lon, 2026-07-03; mirrored in RULES.md) — referenced below as "the ONE-EMITTER FACT RULE".
- PLAN.md's SNOBOL4-BB row still points at GOAL-SNOBOL4-BB.md (left as-is per RULES.md "do not edit PLAN.md goals table on routine handoff"); update it to point here if/when you want.

### THE RE-LIGHT LADDER — SNOBOL4 on the post-GZ#5 spine (Lon pivot 2026-07-03, session 31)
**Ground truth (session 31, live-run — NOT inferred):** crosscheck `--run PASS=5 FAIL=256`, `--compile SKIP=261` (every compile aborts in the gvar_* GROUND-ZERO stubs; the 5 "passes" are vacuous — aborted runs with empty stdout matching empty/whitespace refs; TRUE BASELINE = 0). The RUNG-1 fail-set numbers below (PASS 159/179, FAIL 76, DIVERGE 22) are PRE-RESET and STALE — do not chase them. `lower_snobol4.c` compiles but is GUTTED: node kinds mass-replaced with the `IR_OP_COUNT` sentinel (`--dump-ir` shows them as `IR_UNKNOWN`); REM/ARB/FENCE/ABORT/BAL, TT_NUL, seq/def-call minting — all placeholders.
**Constraint (Lon directives 2026-07-03): NO NEW IR — `IR_e` is FROZEN AGAINST ADDITIONS for this entire first climb; deleting UNUSED ops is DIRECTED, not forbidden.** **[CARVE-OUT 2026-07-04, Lon-authorized: the `IR_KEYWORD` → `IR_KEYWORD_ICON`/`IR_KEYWORD_SNOBOL4` split IS permitted against this freeze (enum +1). Rationale: as the emitter loses its language global (LANG-eradication), a single name-dispatched keyword BB over one case-fold `kw_read` table cannot distinguish `&LCASE`(SNOBOL4) from `&lcase`(Icon) — the two keyword SETS are different and the distinction must live in the opcode. This is the classify-by-name doctrine, not a rung that "needs" a new op by accident. Do NOT re-merge these to "restore" the freeze.]** The never-minted sweep landed same day: full 63-op audit (mint-count per op across lower/parser/driver/runtime/optimizer/machine) found EXACTLY THREE never-minted ops — `IR_CALL_BYNAME`, `IR_CALL_USERPROC`, `IR_CALL_GVAR_USERPROC` — all three DELETED (enum members, scrip_ir.c name rows + case-list, emit.cpp case-lists, proc_collect.c case-list, bb_call.cpp staged-predicate) → **enum now 60 ops + sentinel; the GVAR name left the IR enum by deletion, no rename needed** (by-name call routing lives at emit time in `bb_call_route_classify`'s `CALL_ROUTE_*` over `IR_CALL`, where it belongs). Kind numbers shifted −3 past the CALL block — symbolic names are the anchor (RL-1's recorded "op=29" is pre-shift). Deletion gates: build ×2 green, Icon smoke 12/12 ×2, Icon corpus 209/44/36 exact, crosscheck counts unchanged, kind-residue grep = 0 repo-wide. The vocabulary that implements all of Icon is the vocabulary; it covers a large portion of SNOBOL4. The known delta is addressing (GST(NV)+GVA vs GVA-only, per the ONE-EMITTER FACT RULE), not opcodes. If a rung appears to need a new opcode, the rung is wrong — find the existing-vocabulary lowering or park the program and note it here.
**Method:** STATIC-FIRST → ONE STAB → THEN MONITOR (unchanged). Rung supply = `test_crosscheck_snobol4.sh` (261 programs, category dirs under `corpus/crosscheck/`). Every rung gated on: both modes, `.ref` byte-match, DIVERGE=0, zero regression of previously-green categories.
**SESSION 31 CLOSE (2026-07-03) — ▶ NEXT SESSION START AT RL-2.** Landed: emit_chain consolidation (the ONE-EMITTER FACT RULE), RL-0/RL-1, unused-IR sweep (enum 60). RL-2 opening moves in order: (1) `scrip.c:609` — route SNOBOL4 through `ir_drive_slot_assign` (TMP-ERADICATE grants) instead of legacy `ir_tmp_slot_assign`; (2) mode-4 SNOBOL4 branch: replace the `gva_collect_graph` stub call with zero-collect (GST(NV)-first — n_gva=0, names ride NV) or a real collector — Lon's call; (3) re-lower assignment+OUTPUT in `lower_snobol4.c` onto `IR_ASSIGN`/NV (DT_N NAMEVAL association prints), replacing the IR_OP_COUNT placeholders. Gate: `hello/`, `output/`, `assign/` green both modes, zero Icon regression (209/44/36 anchor).
### Steps
- [x] **RL-0 — baseline recorded.**
- [x] **RL-1 — driver reroute onto the one emitter.** `scrip.c:609/612` now routes SNOBOL4 through `ir_drive_slot_assign` (was legacy `ir_tmp_slot_assign`). Dormant-arm template files are KEPT (may be reused later) — future re-light happens by LOWERING onto live kinds, never by resurrecting per-language emitter paths.
- [x] **RL-2 — re-lower assignment + OUTPUT.** `hello/` 4/4, `assign/` 8/8, `output/` 7/8 (the one fail, `&ALPHABET` keyword read, belongs to RL-8).
- [ ] **RL-3 — concat + arith.** Value concat, `IR_BINOP`/`IR_UNOP`/`IR_BINOP_TEST`/`IR_UNOP_TEST`, `IR_LIT_*`. Gate: `concat/`, `arith/`, `arith_new/` green.
- [~] **RL-4 — statement control flow.** END-GOTO LANDED (2026-07-04, this session, `src/lower/lower_snobol4.c` +1 line, local/unpushed): `:(END)`/`:S(END)`/`:F(END)` now resolve — `END` (SNOBOL4's reserved terminator, so no user label can collide) is registered as a label pointing at the program-exit `IR_SUCCEED` node (`bb_label_registry_add(lp_strdup("END"), exitnd)` after the label-registry loop). Was: `sno_resolve_label("END")` failed because END is the `:end` terminal, never registered. **MEASURED +24 both modes** (crosscheck mode-3 41→65, mode-4 40→64, DIVERGE=0; Icon smoke 12/12 ×2 unchanged) — END-goto is a pervasive exit idiom, so it was the SOLE remaining blocker for ~24 otherwise-in-subset programs. REMAINING for RL-4: the `:S()/:F()` forms that branch on a **pattern-match** result (`X 'lit' :S(L)F(L)`, e.g. control_new 033/034/035) — those need the IR_MATCH_* family and are really RL-5. Non-pattern control flow is now green.
- [ ] **RL-5 — primitive patterns onto the SCAN family.** Candidate mapping (verify per-rung vs SPITBOL semantics, manual Ch. 4/6): literal→`IR_SCAN_MATCH`, ANY/NOTANY→`IR_SCAN_ANY`, SPAN/BREAK→`IR_SCAN_MANY`/`IR_SCAN_UPTO`, LEN→`IR_SCAN_MOVE`, POS/RPOS→`IR_SCAN_POS`, TAB/RTAB→`IR_SCAN_TAB`, BAL→`IR_SCAN_BAL`, find-forms→`IR_SCAN_FIND`, all inside `IR_SCAN_ENTER`/`IR_SCAN`. Gate: `patterns/` subset without alternation/capture.
- [ ] **RL-6 — alternation, backtrack, capture.** Four-port ω-wiring (`IR_REPALT`, β re-entry), `.`/`$` capture. Gate: remaining `patterns/`, `capture/`.
- [ ] **RL-7 — DEFINE + user functions.** `IR_CALL_BYNAME`/`IR_CALL_USERPROC`/`IR_RETURN` (+FRETURN/NRETURN semantics on ω/γ). Gate: `functions/` green.
- [ ] **RL-8 — indirection, aggregates, keywords.** `$X` (NV by computed name), ARRAY/TABLE via `IR_SUBSCRIPT`/`IR_MAKE_LIST`/`IR_FIELD_*`, `&`-keywords via `IR_KEYWORD`. Gate: `data/`, `keywords/`, `strings/`, `library/`.
- [ ] **RL-9 — full-suite green + stale-section purge.** Crosscheck FAIL=0 both modes, DIVERGE=0; then (Lon approval) delete the superseded pre-reset sections below.

### SNOBOL4 RE-LIGHT — WATERMARK 2026-07-04 (re-derived baseline + END-goto landing; Claude Opus 4.8)
**Re-derived HEAD `0831f2a5` baseline (the session-31 "TRUE BASELINE=0" is long stale — much landed via SNOBOL4-GZ#5-rung-1).** Full `test_crosscheck_snobol4.sh` at HEAD: **mode-3 41/261, mode-4 40/261 (SKIP 221 = `--compile` aborts on the same feature gaps; mode-4 tracks mode-3, DIVERGE=0)**. Per-category mode-3 (the rung supply, biggest first): patterns 1/92 · strings 4/17 · keywords 0/12 · rung9 0/10 · rung10 0/9 · functions 0/8 · rung8/rung11/capture 0/7 · data 0/6 · rung4/rungW05/rungW07 0/5 · control_new 3/7 · arith 0/2 · output 7/8 · GREEN: hello 4/4, concat 6/6, assign 8/8, arith_new 8/8.
**Landed 2026-07-04 (END-goto, on origin `a1a3b404`):** END-goto (RL-4 slice) → mode-3 65/261, mode-4 64/261. One line in `lower_snobol4.c`; zero new IR; zero emitter touch.
**Landed 2026-07-04 (STRING-BUILTIN REGISTRATION, this session — blocker-map item 4):** `SUBSTR`/`REVERSE`/`LPAD`/`RPAD`/`INTEGER` were bombing `bb_call: unsupported call shape` purely because they were absent from `rt_builtin_is_known`'s `known[]` (so `bb_call_route_classify` fell to CALL_ROUTE_FATAL). All five already had runtime impls (`SUBSTR_fn`/`REVERS_fn`/`lpad_fn`/`rpad_fn` in `string_builtins.c`); the emitter's CALL_ROUTE_FN path (`bb_call_fn_str`) is fully generic (marshals args, calls `rt_call_arr(name, args, nargs)` — passes the name as a runtime string, stays language-blind). FIX = two pure additions, no new IR, runtime-only: (1) five names → `known[]`; (2) five dispatch arms in `try_call_builtin_by_name` calling the existing `*_fn` (INTEGER is a SPITBOL predicate → NULVCL success / FAILDESCR fail, mirroring IDENT/DIFFER; 2-arg LPAD/RPAD/SUBSTR defaults handled). **MEASURED: crosscheck mode-3 65→76, mode-4 64→75, DIVERGE=0** (strings 4→9, rung8 3→6, rung9 7→8 by category sweep — the builtins are cross-category; every other category byte-identical, zero regression). Both modes verified oracle-exact on all five; Icon smoke 12/12 ×2 held (emitter/templates untouched, so mutation + no-lang gates unaffected). **HANDOFF: codegen output changed for SNOBOL4 programs calling these (they now emit `call rt_call_arr` instead of aborting), so run the `util_regen_*_s_artifacts.sh` set before commit per RULES.md step 4.**
**Landed 2026-07-04 (KEYWORD-READ + DATATYPE, this session — blocker-map item 2 partial):** `lower_snobol4.c` bombed `tree kind 6` (= `TT_KEYWORD`) on every keyword read. FIX = three localized changes, no new IR, no emitter/template touch: (1) `case TT_KEYWORD` in `sx_lower` → `IR_KEYWORD` (mirrors Icon's `lc_key`; the emitter's `bb_keyword` generic tail already calls `rt_keyword_read`); (2) `rt_keyword_read` now case-folds the keyword id before `kw_read` — SNOBOL4 keyword tokens are UPPERCASE `&`-stripped (`(TT_KEYWORD ALPHABET)` per `--dump-ast`) while `kw_read`'s keys are all lowercase (Icon-style); folding unifies both frontends, Icon unaffected; (3) `&alphabet` aliased to the 256-char `&cset` in `kw_read` (SPITBOL's name for the full set). Also registered `DATATYPE` = the existing lowercase `type` builtin (identical lowercase output; one `known[]` entry + widened the `type` arm condition). **MEASURED: crosscheck mode-3 76→83, mode-4 75→82, DIVERGE=0** (keywords 6→8, output 7→8, rung8 6→7, rung9 8→9, strings 9→11; every other category byte-identical, zero regression). 097_keyword_alphabet (`SIZE(&ALPHABET/&UCASE/&LCASE)`=256/26/26) + 081_builtin_datatype both modes oracle-exact; Icon smoke 12/12 ×2 held. **ONE mode-4 FAIL (082_keyword_stcount): NOT a regression** — it advanced from compile-abort (SKIP) to compiling-but-wrong; it uses `&STNO`, which has no runtime statement-counter (kw_read → FAILDESCR → NV null), so it fails both modes identically (hence DIVERGE=0). Was already failing mode-3 before this change. A real `&STNO`/`&STCOUNT` counter is a future rung.
**Blocker map ahead (existing-IR, ranked by leverage):** (1) **PATTERNS = RL-5/6, 91 programs** — the mega-lever and the whole point of SNOBOL4; `lower_snobol4.c` currently bombs any `:pat`/TT_SCAN subject LOUD (`sno_fatal` at the `if (pat || subj==TT_SCAN)` guard, line ~157). Maps onto the EXISTING Icon SCAN family (IR_SCAN_MATCH/ANY/MANY/UPTO/MOVE/POS/TAB/BAL/FIND) per the RL-5 candidate table — no new IR. This is the next real rung; it is large (multi-session). (2) **Keyword read/assign** (`&ALPHABET` read, `&TRIM =`/`&ANCHOR =` assign) — blocks output/006, arith's fileinfo+triplet (both die on `&TRIM = 1`), keywords 0/12; note `&ANCHOR` also changes pattern semantics so it couples to RL-5. (3) **DEFINE + call/return** (RL-7) — functions 0/8, expr_eval. (4) string builtins SUBSTR/REVERSE/LPAD/RPAD (SPITBOL extensions — `bb_call: unsupported call shape`; check runtime actually implements them before registering by-name).

**Landed 2026-07-04 (DEFINE + AGGREGATES + KEYWORD-ASSIGN + INCLUDES, this session — blocker-map items 2/3 + user-fn ladder, on SCRIP `9146f606`):** mode-3 **115/261**, mode-4 **114/116 non-skip** (DIVERGE=0; the two m4-only fails are pre-existing 082_keyword_stcount &STNO and 213_indirect_name NRETURN-read). Icon smoke 12/12 ×2 held; polyglot/emit gates untouched-green. Landed in four rungs over EXISTING IR only (enum still frozen at 62 ops; zero new opcodes):
- **DEFINE (user functions, functions 8/8 + rung10 1010/1012/1014/1018):** dynamic scoping is a per-proc behavioral property `dyn_scope` (is_generator precedent) + a `result_name` plumb for alt-entry/alias result cells. Function bodies carve as SEPARATE IR graphs over the full statement list (entry = anchor of the entry-label stmt); RETURN→graph `IR_SUCCEED`, FRETURN→`IR_FAIL`, NRETURN aliased to RETURN. Runtime path already existed (`rt_call_named_proc`, rt.c): added `result_name` to `rt_proc_t`+`ProcEntry`, `rt_proc_set_result_name`, both dyn call paths use `rname=result_name?:name` for the save-push + result read; resolve_cells binds rcell to rname. `DEFINE` entry arg accepts `.label` (TT_NAME) as well as `'label'` (TT_QLIT). scrip.c registers result_name after all three set_generator sites (mode-3 driver loop + mode-4 startup asm `.Lstartup_prn%d` + `rt_proc_set_result_name@PLT`). **Shadowed-name idiom** `DEFINE('max(max,x)')` (parameter name == function name): the result-cell save-push is SKIPPED when a param already shadows rname, so the param's binding is what the body reads/writes and what the caller receives — fixes the whole math.sno family.
- **AGGREGATES/RECORDS/INDIRECTION (data 6/6, rung11 7/7, rung2 210/211/212, rung9 910):** `by_name_dispatch.c` known[] += ARRAY TABLE ITEM PROTOTYPE CONVERT DATA APPLY OPSYN VALUE SNO$KWSET; arms after SNO$NAME. ARRAY via `sno_array_from_proto` (recursive nested 1-D ARBLKs, `'lo:hi'`/`'n'` comma-split dims, init arg, proto stashed in new `ARBLK_t.proto`). ITEM = chained `rt_subscript_var`+`rt_deref`. CONVERT INTEGER/REAL/STRING. DATA guarded `dat_register`. APPLY (DT_N name→registered proc via g_call_args+rt_call_proc_descr, else recursive builtin). VALUE (DT_N deref / NV_GET by name). **EARLY instance-field guard at dispatcher head** (nargs==1 && DT_DATA && fn is a field of the instance's own DATBLK → dat_field_get) beats Icon `real()`/`type()` cast-shadowing — keyed on `args[0].u->type` (DATBLK_t), NOT the DatType registry (that cast was the segfault). `lower_snobol4.c`: TT_IDX rvalue arm (chained IR_SUBSCRIPT + final IR_DEREF), `sx_subscript_lv` helper (+fwd decl), assignment-subject arms for TT_IDX / `ITEM(...)=` / record-field `f(obj)=` (IR_FIELD_VAR + IR_ASSIGN_VAR), TT_NAME generalized to subscript-lv NAMETRAP (no deref), TT_INDIRECT special-cases a TT_NAME inner (direct IR_DEREF, no SNO$NAME wrap → `$.a<2>`). `sno_prescan_expr` recursive walker in the pre-scan loop: DATA literal → `dat_register`; OPSYN(alias,old) → old∈defs ? clone the def with `result_name`=orig fname : `rt_builtin_synonym_add`. DATATYPE returns the instance's own type name for DT_DATA when no gen_type tag.
- **KEYWORD-ASSIGN (arith/fileinfo, arith/triplet, keywords 098/099):** `&KW = v` subject (TT_KEYWORD) lowers to `IR_CALL "SNO$KWSET"(kwname-literal, v)` — SNO$NAME precedent, zero new IR. keywords.c gained writeable storage (`g_anchor`/`g_trim`/`g_maxlngth` + existing error/trace/dump/random) with read arms for anchor/trim/maxlngth/fullscan/stlimit, and `rt_keyword_write_snobol4` (lowercases, coerces to long, routes to the global or falls back NV_SET). (&ANCHOR/&TRIM are STORED and round-trip; their pattern/I-O *semantics* land with IR_MATCH_*.)
- **INCLUDES (library test_case/math/stack/string — math+stack now PASS; case+string park on the pattern wall as expected):** driver include seeding was resolving the source dir from the *relative* argv path so the ancestor-`/lib` walk missed — fixed to `realpath()` the input first, split `SNO_LIB` on `:` (multi-root), and `strdup` the dir strings (they were stack-buffer pointers handed to the lexer's `inc_dirs[]`, a latent lifetime bug).
- **EMITTER (touched — regression-gated, artifacts regenerated):** the flat spine's per-node γ/ω target resolution now CHASES through `IR_GOTO` runs (the label-registry landing for RETURN/etc. is a GOTO node, so a raw pointer-match missed it and the fail/return edge fell to the proc-ω fail exit — this is why a conditional `f = PRED(...) val :(RETURN)` that failed the predicate returned FAILDESCR instead of the prior value), and an unresolved ω whose target is `IR_SUCCEED` now maps to the success port. Proven pure: Icon `.s` bench artifacts + smoke unchanged in shape, IR-mutation + no-lang gates still HARD-zero.

PARKED (existing-IR, with reasons — do NOT fake): 1011 runtime redefinition (static last-wins can't do mid-program re-DEFINE of a live binding); 1013+213 NRETURN by-name lvalue/read; 1015 operator-OPSYN (TT_OPSYN kind 23 needs parser operator machinery); 1016 EVAL (TT_DEFER kind 8 — impossible under the frozen enum per directive); 1017 ARG/LOCAL (would pass ONLY by uppercasing param names — SPITBOL case-fold vs SCRIP case-sensitivity, declined); 082 &STNO statement counter; END-inside-function terminating the whole program (currently returns).

**NEXT LEVER = PATTERNS (RL-5/6, ~91 programs + capture 7 + rungW* 26 + strings cross/word1-4/wordcount + control_new-3):** the one-shot IR_MATCH_* family. Dormant `bb_match_*.cpp` templates exist on disk (NOT in the Makefile). This is the mega-lever gating the largest single block of the corpus and the honest end of the existing-IR ladder.

<!-- ════════════ ORIGINAL GOAL-SNOBOL4-BB CONTENT BELOW (GZ#5 REBUILD + PRE-GZ5 ARCHIVE) ════════════ -->

<!-- ════════════ GZ#5 REBUILD (2026-07-03) — THIS SECTION SUPERSEDES THE PRE-GZ5 LADDER BELOW ════════════ -->

# GOAL — SNOBOL4 on the shared BB spine (GZ#5 rebuild)
AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude   OPENED: 2026-07-03

DOCTRINE: SNOBOL4 rides the SAME pipeline as Icon — sno_parse_ast → lower_sno_stage2 (src/lower/lower_snobol4.c) → shared optimizer → ir_drive_slot_assign → the ONE language-blind emitter → mode-3 (--run) / mode-4 (--compile). SCRIP FOLLOWS SPITBOL SEMANTICS; the oracle is /home/claude/x64/bin/sbl -b. Every statement lowers on the 5-STAGE MODEL: (1) build subject — can fail; (2) build pattern — can fail; (3) perform pattern; (4) build replacement — can fail; (5) perform (substring) replacement — rarely fails. Stages 2/3/5-pattern are LOUD LOWER-TIME FATALS until the IR_MATCH_* family exists ("soon" per Lon 2026-07-03).

## RUNG 1 — statement core (LANDED 2026-07-03)
WATERMARK: probes p1/t2/t5/p2/p4 = 5/5 PASS in m3 AND m4, byte-exact vs the SPITBOL oracle (hello; unconditional goto; unset-var and empty-string arith; the classic uninitialized LT counting loop; the ladder: SIZE TRIM DUPL REPLACE REMDR IDENT DIFFER LGT, $-indirection read AND write, unary minus, S/F gotos, INPUT association). Icon smoke stayed 12/12 ×2 (HARD gate).
WHAT LOWERS: NAME = expr and $expr = expr (5-stage skeleton, pattern stages fatal); eval-only statements; :S/:F/unconditional GOTOs — per-statement anchor + S/F junction IR_GOTOs, pass-1 anchors feeding the shared bb_label registry; END; literals ILIT/FLIT/QLIT/NUL; concat (TT_SEQ → BINOP code 11); + - * / **; unary ±; TT_FNC → IR_CALL byname; $e rvalue = SNO$NAME call → IR_DEREF (NAMEVAL DT_N slen==0 → NV_GET_fn, so INPUT association is free); OUTPUT/TERMINAL/keyword associations via NV_SET_fn.
ZERO NEW IRs. The one pre-authorized IR (GSM/NV vs GLA) proved UNNECESSARY: every sno variable is global_register()'d and GVA never activates for sno, so IR_VAR/IR_ASSIGN land on the existing NV_GET_fn/NV_SET_fn arms of bb_var_global/bb_assign_global. The Icon-proven IR vocabulary carried the whole subset.
RUNTIME ADDITIONS (language-blind, src/runtime/by_name_dispatch.c): uppercase arms IDENT DIFFER TRIM DUPL REPLACE REMDR + SNO$NAME (NAMEVAL mint; fails on null name); all added to known[] — the ONE list bb_call_route_classify checks. _SNOCOERCE macro: SPITBOL null-string→INTEGER-0 for the numeric predicates (EQ NE LT LE GT GE) and DUPL/REMDR.
SHARED FIXES LANDED WITH THIS RUNG (all-language wins): (1) rt_num_arith (src/runtime/arithmetic.c) normalizes empty DT_S/DT_SNUL operands → INTVAL(0) — was pointer-arithmetic UB; (2) bb_binop_arith raw-int arm now TYPE-DISPATCHES — non-DT_I operand or rt_binop_overload miss routes to a rt_num_arith slow arm (labels L2/L3) instead of raw payload adds (UB for EVERY language); DT_I fast path byte-identical; (3) bb_label_landing() implemented in lower_common.c (was declared in lower.h, defined nowhere).
DRIVER: is_sno_bb (pure-.sno programs) joins the modern spine beside is_icon/is_raku at all six gates (dump-ir slot-assign; both mode arms; optimizer + slot-assign loops). g_gva_active stays 0 for sno — NV arms by construction.
KNOWN SUBSET WALLS (loud lower-time fatals, by design): pattern statements (:pat attr or TT_SCAN subject); DEFINE; EVAL/CODE (the lower_snobol4() runtime-eval entry aborts); indirect/computed gotos :($X); assignment subjects other than NAME / $expr.

## RUNG 2 — DEFINE (NEXT; Lon: "DEFINE can be done")
STEPS: (1) at lower time parse the DEFINE("F(A,B)L1,L2") literal: fname, formals, locals, entry label (defaults to fname); (2) statement-graph call/return protocol: calls to F enter the label anchor with a recursion-safe return-linkage stack; RETURN/FRETURN/NRETURN become registered labels whose junctions pop the linkage — FRETURN signals ω, NRETURN returns by-name; (3) NV save/restore = SNOBOL4 dynamic scoping: on call push NV cells of formals+locals+fname, bind args by value; on RETURN the result is NV(fname), then restore — runtime helpers rt_sno_call_save/restore are name-list ops, language-blind; (4) probe: recursive factorial vs oracle, m3+m4; runtime (non-literal) DEFINE stays fatal until EVAL exists.

## RUNG 3 — builtin ladder
Sweep the SPITBOL builtin surface vs oracle, one probe file per family, m3+m4 diffed: CONVERT, DATATYPE, REVERSE/LPAD/RPAD, ARRAY/TABLE/ITEM/PROTOTYPE, DATE/TIME parity, &keyword read/write matrix, arithmetic edges (real division, ** precedence).

## RUNG 4 — IR_MATCH_* wake — ✅ SUPERSEDED / DONE (see the SN4-PAT ladder above)
**RECONCILED 2026-07-06:** this rung's PROPOSAL ("introduce the IR_MATCH_* opcode family 1:1 with the hibernating templates") is exactly what the relocated **SN4-PAT ladder above** executed and landed (SN4-PAT-0 re-added the family to `IR_e` with Lon's permission; SN4-PAT-1…DEFER-CALLOUT wired LEN/LIT/ANY/NOTANY/SPAN/BREAK/BREAKX/TAB/RTAB/POS/RPOS/REM/ARB/CAT/ALT/FENCE/ARBNO/capture/DEFER end-to-end, both modes, oracle-pinned). The original proposal text is retained below as the historical plan the ladder carried out; do NOT treat it as open work.
Hibernating template stock already on the menu: bb_match_{abort,advance,alt,any,arb,arbno,atp,break,breakx,capture,cat,defer,fence,head,len,notany,pos,rem,retry,rtab,span,span_var,tab} + bb_pattern_{break,capture,cat,len,lit,stub} + bb_scan_stmt + bb_subject + bb_scan_splice_empty. PROPOSAL: introduce the IR_MATCH_* opcode family 1:1 with these boxes; stage-2 lowers pattern BUILD to a pattern-graph value; stage-3 PERFORM = scan-enter driving match boxes with the cursor in the Σ/δ/Δ discipline; stage-5 replacement splice via the splice box. Byrd four-port α/β/γ/ω throughout; the emitter stays language-blind — one dispatch case per new IR KIND, never per language. The pre-GZ5 ladder below is the ARCHIVE of how these boxes once ran; mine it, do not resurrect it wholesale.

## FAIL MAP (hard-won; do not relearn)
- polyglot_lang_mask(icon program) carries a stray LANG_SNO bit → any REAL lower_sno_stage2 must exact-mask guard (landed: returns 0 unless mask is exactly sno). This is why the old no-op stub was silently "safe". Root-cause the mask computation someday.
- Goto fields are TT_GOTO_S/TT_GOTO_F/TT_GOTO_U NODES (child[0] = TT_QLIT label, or an expr for indirect), NOT ":go*" string attrs — the ast printer's ":goS L" rendering is a convenience lie.
- NV_GET miss returns NULVCL (DT_SNUL, s=NULL). Anything arithmetic must take the typed slow arm; never trust raw payload reads.
- mode-4 tests MUST rebuild out/libscrip_rt.so after runtime edits — a stale .so silently runs old semantics.
- scripts/test_gate_bb_one_box.sh fails on bb_binop_gvar_arith_slot.cpp and bb_binop_concat_slot.cpp (0 extern "C" bb_* entries) — PRE-EXISTING before this session, untouched by it.

<!-- ════════════ PRE-GZ5 ARCHIVE BELOW (SM-era pattern ladder; superseded 2026-07-03) ════════════ -->

<!-- GOAL-SNOBOL4-BB · SCRIP native pattern-match ladder for modes 3/4 (--run/--compile) -->

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ▶▶▶▶▶  TOP PRIORITY — SEEN FIRST, DONE FIRST — MONITORED LADDER CLIMB  ◀◀◀◀◀  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

**THIS SECTION IS THE WHOLE JOB. Everything below it (DEMO-PAT, NRG, GVA, PERF-CALL, …) is a SOURCE OF FAILING PROGRAMS to feed THIS ladder — not a separate track.** The method (Lon directive 2026-06-27 — **lightened from strict MONITOR-FIRST now that the monitor is proven**): **STATIC-FIRST → ONE STAB → THEN MONITOR.** For each failing program: (1) **STATIC ANALYSIS** — read the program's `.ref`, run SCRIP `--run`/`--compile`, read the divergent output, then reason from the generated `.s` + the IR + the BB templates straight to the land mine. (2) **ONE STAB** — make a single targeted fix and rebuild. (3) **VERIFY against the program's `.ref`** — both `--run` AND `--compile` must match it; the `.ref` is ground truth, **no live oracle needed**. If the stab FAILS or the bug resists static reasoning, **ESCALATE** to the 2-way IPC sync-step monitor: bracket between the first divergent trace event and the previous (last-agreeing) event, pin a gdb spin/ignore-counter breakpoint at that bracket, and walk C-step-by-step until the LAND MINE (the instruction that writes the wrong value) is under the cursor — fix, re-verify. The monitor is the **heavy instrument reserved for hard-to-find bugs**; it (and the x64 SPITBOL oracle + the extra monitor build targets it needs) is **NOT built or run until a stab has failed**. NO scattershot prints. The regression gate stays the `.ref`-based crosscheck (fast, not the monitor). Documented prior art (monitor escalation): `GOAL-MONITOR-REINSTATE.md`, `MONITOR-BINARY-DESIGN.md`, `GOAL-TWO-STEP-HUNT.md`, and the gdb-hit-count diagnoses in `GOAL-LANG-SNOBOL4.md` / `GOAL-CSN-FENCE-FIX.md` / `GOAL-PROLOG-BB.md` and `archive/ARCHIVE-LANG-SNOBOL4-HISTORY.md`.

## ⛔ FACT RULE — SCRIP SNOBOL4 IS CASE-SENSITIVE; ALL RESERVED NAMES MUST BE UPPERCASE (Lon directive, 2026-06-26)
**SCRIP SNOBOL4 operates in case-sensitive mode ONLY. This is non-negotiable and permanent.**
- All reserved/builtin symbols MUST be UPPERCASE in SCRIP source: `DEFINE`, `OUTPUT`, `INPUT`, `END`, `RETURN`, `FRETURN`, `NRETURN`, `EQ`, `NE`, `LT`, `LE`, `GT`, `GE`, `LGT`, `IDENT`, `DIFFER`, `INTEGER`, `REAL`, `SIZE`, `TRIM`, `DUPL`, `REVERSE`, `REPLACE`, `SPAN`, `BREAK`, `ANY`, `NOTANY`, `LEN`, `POS`, `RPOS`, `TAB`, `RTAB`, `ARB`, `ARBNO`, `REM`, `FAIL`, `SUCCEED`, `FENCE`, `ABORT`, `BAL`, `OPSYN`, `EVAL`, `CODE`, `APPLY`, `ARRAY`, `TABLE`, `DATA`, `ITEM`, `CONVERT`, `CHAR`, `LPAD`, `RPAD`, `SUBSTR`, `SORT`, `COLLECT`, `COPY`, `DATE`, `TIME`, `PROTOTYPE`, `ARG`, `LOCAL`, `FIELD`, and all keywords (`&LCASE`, `&UCASE`, `&ALPHABET`, `&ANCHOR`, `&TRIM`, etc.).
- **SPITBOL oracle must ALWAYS be invoked with `-bf` flag** (binary, no case-folding): `/home/claude/x64/bin/sbl -bf file.sno`. Never invoke without `-bf` as it will silently fold case and produce misleading oracle results.
- The crosscheck corpus (`corpus/crosscheck/`) and all reference test programs already use uppercase. If a test program has lowercase builtins, it is a bug in the test program, not a SCRIP limitation.
- This rule was established because the SCRIP parser is case-preserving (`intern = strdup`, no folding) and the runtime registers all builtins in `_func_buckets` under their uppercase names (`"DEFINE"`, `"EQ"`, etc.). A lowercase call `define(...)` will never find the builtin and will silently fail with Error 5.



## ⛔ FACT RULE — ONE EMITTER FOR ALL LANGUAGES; THERE IS NO SNOBOL4 ENTRY POINT IN EMIT (Lon directive, 2026-07-03)
**ONE emitter serves ALL languages, both mediums, both modes (the all-languages extension of GOAL-MODE34-IDENTICAL.md's one-emitter-across-modes rule and the concurrency discipline's "edit only your own language's arms, never a peer's").** Per-language variation lives in LOWERING and in per-IR-kind dispatch arms/box templates INSIDE the one emitter — NEVER in a parallel emitter or a per-language entry.
- The one emitter entry is **`emit_chain`** (`src/emitter/emit.cpp`): `bb_box_fn emit_chain(IR_t *entry, FILE *out, const char *prefix)` — `out==NULL` → BINARY (returns the sealed box fn), `out!=NULL` → TEXT (non-NULL on success); the proc `.globl` line lives with the driver's other asm scaffolding. **CONSOLIDATED (Lon directive 2026-07-03, session 31):** the four `descr_flat_chain_build*` variants (whose `pnames/np` params were already dead) and the five `gvar_flat_chain_build*`/`bb_build_flat`/`codegen_flat_build` GROUND-ZERO stubs are DELETED; every call site rides `emit_chain` (scrip.c mode-3+4 main+proc for ALL languages, `runtime_eval.c` EVAL/CODE rail, `emit.h`); internal helpers renamed `emit_*` (`emit_chain_operand_refs`, `emit_chain_arity`, `emit_binop_opnd_slot`); grep `descr_flat|gvar_flat|bb_build_flat|codegen_flat_build` = 0 in build files (`bb_pat_build.cpp` exempt — parked, not in Makefile, mints dead `IR_MATCH_*` kinds).
- Addressing is an ARM, not an emitter: SNOBOL4 rides GST(NV) by-name (`NV_GET_fn`/`NV_SET_fn`; DT_N NAMEVAL is the association-honoring arm — OUTPUT/INPUT) alongside GVA slots where names resolve statically, vs Icon's GVA-only (`[rbx+k*16]`). Same emitter, different arm.

## THE RE-LIGHT LADDER — RELOCATED (Lon directive 2026-07-04)

**MOVED to `GOAL-IR-IMMUTABLE-EMIT.md`** — the GZ#5 home file. This file's own title is *"SNOBOL4 on the shared BB spine (GZ#5 rebuild)"*, so the RL-0…RL-9 subset climb belongs there with the rest of Ground Zero #5. The live SNOBOL4 re-light ladder (RL-0…RL-9, the NO-NEW-IR constraint, the session-31 close + RL-2 opening moves) now lives in GOAL-IR-IMMUTABLE-EMIT.md → "SNOBOL4 RE-LIGHT LADDER". This file retains the SNOBOL4-specific detail below: the monitor climb (RUNG-0/1/2), DEMO-PAT, NRG, PERF-GVA, and the fail maps. Any "THE RE-LIGHT LADDER above" reference elsewhere in this file now means that relocated ladder.

## THE LADDER (do strictly in this order)

- **RUNG 0 — GET THE MONITOR LIT FOR MODES 3/4.** The monitor is currently DARK for native modes (the per-statement taps lived only in the deleted mode-2 path). Until it emits `LABEL/VALUE/CALL/RETURN` per statement from `--run`/`--compile`, no climb is possible. This is the **MON-RE rung immediately below** (MON-RE-1 … MON-RE-6). Reinstating it is the prerequisite to every subsequent rung and therefore comes FIRST. Acceptance: `PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run bash scripts/test_monitor_3way_sync_step_auto.sh /tmp/mdiv.sno` reports the first divergence at the `$nm = vl` statement (a real semantic divergence), with matching LABEL/VALUE granularity up to that point.
- **RUNG 1 — CLIMB THE CROSSCHECK FAIL SET.** Walk `test_crosscheck_snobol4.sh`'s FAIL set one program at a time, **STATIC-FIRST**: read its `.ref` + the divergent SCRIP output + the generated `.s`, take ONE targeted stab, rebuild, and verify `--run`/`--compile` against the `.ref`. Escalate to the monitor (bracket → gdb spin-break → land mine) ONLY if the stab fails. Each fix drops the fail count by one; the next program's divergence is the next sub-rung. The fail set is the rung supply.
- **RUNG 2 — CLIMB THE DEMO HANGS (claws5, treebank).** Same loop on the pattern-heavy demos (the DEMO-PAT material below): monitor localizes the hang to the first statement where SCRIP's wire diverges from the oracle (GAP-1's deferred-call-in-capture will surface as the trace event where the side-effect counter fails to advance), bracket it, walk to the land mine in the lower/emit/runtime path, fix. The GAP-1…GAP-7 diagnosis below is the MAP of expected land mines, not a substitute for the monitor finding them.
- **RUNG 3+ — anything else that diverges** (NRG correctness regressions, new feature gaps) climbs the same ladder.

**Build + monitor invocation (every session):**
```bash
apt-get install -y libgc-dev && cd /home/claude/SCRIP && make && make libscrip_rt
git clone https://github.com/snobol4ever/x64 /home/claude/x64   # SPITBOL oracle (spl)
# 2-way monitor (the bug finder):
PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run bash scripts/test_monitor_3way_sync_step_auto.sh <file.sno>  # SCRIP under test
# then gdb at the bracket with a spin counter:
#   break <file>:<line>;  ignore <bp> <N-1>   (stop on the first DIVERGENT iteration)
#   step / next / finish  until the land-mine instruction is under the cursor
```

---

<!-- GOAL-MONITOR-REINSTATE · IPC sync-step binary monitor, re-homed onto native modes 3/4 -->

# RUNG 0 DETAIL — GOAL-MONITOR-REINSTATE.md — reinstate the binary sync-step IPC monitor

## ▶▶▶ NEXT SESSION — START HERE

**Why this goal exists.** The binary sync-step IPC monitor (controller `scripts/monitor/monitor_sync_bin.py`, harness `scripts/test_monitor_3way_sync_step_auto.sh`, wire format `scripts/monitor/monitor_wire.h`) compares SCRIP against SPITBOL **event-by-event over a synchronous binary wire** and reports the FIRST divergence with a source-line table. It made bug-finding near-instant. It went dark when **mode-2 (`--run`) was deleted**: the per-statement trace taps (`mon_emit_label_bin`, the VALUE/CALL/RETURN emitters) are called ONLY from `src/driver/driver_call.c` → `exec_stmt`, the dead mode-2 SM-interpreter path. Modes 3 (`--run`) / 4 (`--compile`) are native x86 and never call them per-statement, so SCRIP's wire stream leads straight to `END` while SPITBOL leads with `LABEL stno=1`.

**GROUND TRUTH (session, verified by live run — NOT inferred):**
- Framework WORKS: with the harness defaulting to `--run`, a 2-way `PARTICIPANTS="spl scr"` run connects both participants, steps the barrier, and prints a DIVERGE table. The controller, FIFO barrier, byte-compare, and first-divergence reporter are all intact.
- SCRIP-side binary protocol is INTACT in `src/runtime/core/core.c`: `mon_send_bin`, streaming `MWK_NAME_DEF` intern, `MWK_VALUE/CALL/RETURN/LABEL/END`, the go-pipe barrier (`MONITOR_READY_PIPE`/`MONITOR_GO_PIPE`), and the LOAD-able `_b_MON_PUT_*` builtins. Verified: scrip emits 27 wire bytes when env vars are set.
- SPITBOL `/home/claude/x64/bin/sbl` has the bridge compiled in (`MONITOR_READY_PIPE` present in the binary); x64 carries `monitor_ipc_spitbol.so` + `osint/monitor_ipc_runtime.c`.
- The CURRENT divergence on any program is the instrumentation-granularity gap (SPITBOL `LABEL stno=1` vs SCRIP `END`), NOT a semantic bug. Fixing that gap = this goal.
- `mon_emit_label_bin` is reachable ONLY from `driver_call.c:161` (mode-2). The IR does NOT carry a statement number (`lower_snobol4.c` drops `:stno`; the AST attr is read at `driver_call.c:153`). The IR node struct (`src/contracts/IR.h`) has `ival`/`dval`/`counter`/`state` per-opcode fields but no dedicated stno slot.

**ACCEPTANCE (the whole goal):** `PARTICIPANTS="spl scr" SCRIP_RUN_FLAG=--run bash scripts/test_monitor_3way_sync_step_auto.sh /tmp/mdiv.sno` reports the FIRST divergence at the `$nm = vl` statement — SPITBOL `a`=`hello`(STRING) vs SCRIP `a`=``(NULL) — a SEMANTIC divergence, with matching LABEL/VALUE granularity up to that point. (`/tmp/mdiv.sno`: a DEFINE'd `setit(nm,vl)` whose body is `$nm = vl`, called as `setit("a","hello")`, then `OUTPUT = "a=" a`.)

---

## ▶ RUNG: MON-RE — re-home the sync-step taps onto modes 3/4

Each step gated on `make scrip` rc=0 (never a broken commit) + the named behavioral check. The taps are `MONITOR_BIN`-guarded (read env once at startup into a global; zero emission + zero overhead when unset → crosscheck/bench unaffected). Template-only / four-Greek-port / both-medium per RULES.md. Regenerate benchmark/feature/demo `.s` only after MON-RE-3 (the first codegen-touching step) and confirm they are byte-identical with `MONITOR_BIN` unset (the guard makes the default path unchanged).

### Steps
- [x] **MON-RE-0 — harness default mode.** `scripts/test_monitor_3way_sync_step_auto.sh`: scrip participant defaulted `--run` (deleted) → `--run`. DONE this session. (Still TODO sub-fix: the `${MONITOR_PM:+...}` `bin/sh` Bad-substitution — force `#!/usr/bin/env bash` invocation / guard the expansion.)
- [x] **MON-RE-1 — `g_monitor_bin` startup flag (runtime-only, behavior-neutral).** DONE (SCRIP `4686e00`, 2026-06-26). `g_monitor_bin` global in `core.c`; behavior byte-identical.
- [x] **MON-RE-2 — carry stno into IR.** DONE (SCRIP `4686e00`, 2026-06-26). `IR_exec_t stno` sidecar in `IR.h`; `--dump-ir` shows stno on statement-entry nodes.
- [x] **MON-RE-3 — LABEL tap in the native statement-entry box.** DONE (SCRIP c8db891, 2026-06-26). The tap is emitted in the FLATTENER (codegen_gvar_flat_chain_body in emit_bb.c), NOT the bb_succeed leaf — the flattener COALESCES IR_SUCCEED nodes (gvar_chain_resolve_stmt skips them) so bb_succeed() never fires in modes 3/4. Mechanism: a parallel nstno[] array tracks each work-box stno, populated during BFS by gvar_chain_skip_stno() (returns the stno of the IR_SUCCEED skipped past); when g_monitor_bin && nstno[i]!=0 the per-node loop calls extern-C bridge emit_mon_label_tap(stno) (bb_succeed.cpp) emitting mov rdi,stno; call mon_emit_label_bin. EMIT-TIME GATED on g_monitor_bin: the compiler core_lib_init() runs before emit in BOTH modes 3+4, so the tap is emitted ONLY when MONITOR_BIN set at compile time -> .s byte-identical with monitor off (verified arith_loop/mixed_workload/table_access md5 identical HEAD-scrip vs MON-RE-3-scrip). Gate MET: crosscheck --compile PASS=170 FAIL=85 / --run PASS=149 FAIL=112 / DIVERGE 21 — fail set BYTE-IDENTICAL to pristine HEAD (same script on /tmp/scrip_HEAD gave identical numbers+lists; zero regressions). 2-way spl-scr monitor on /tmp/mdiv.sno now ADVANCES: steps 1+2 AGREE (LABEL stno=1 DEFINE, LABEL stno=3 MAIN), step 3 DIVERGES with the bug BRACKETED — SPITBOL @3 CALL setit (enters the call) vs SCRIP LABEL stno=2 (falls through to proc-body label WITHOUT the CALL frame). .s artifacts brought current (pre-existing drift, NOT MON-RE-3 — default-path output proven identical to HEAD).
- [x] **MON-RE-4 — VALUE tap on global store.** DONE (SCRIP a136452, 2026-06-26). Added mon_emit_value_bin(name, DESCR_t) to core.c (after mon_emit_label_bin): skips kw_trace/comm_var guards, goes straight to mon_send_bin(MWK_VALUE,...) with type/payload dispatch. Wired into rt_gvar_assign_str/int/var/descr in rt.c — each calls mon_emit_value_bin(name, d) after NV_SET_fn, gated on g_monitor_bin. Runtime-only change: .s byte-identical (verified md5). Gate MET: crosscheck PASS=170/85 FAIL-set IDENTICAL to HEAD. 2-way spl-scr monitor on /tmp/simple_assign.sno: steps 1+2 AGREE (LABEL stno=1, VALUE X=STRING(5)=hello); step 3 diverges on protocol ordering (SPITBOL advances to LABEL stno=2 before SCRIP sends second VALUE) — this is expected MON-RE-4 granularity; the VALUE wire event is confirmed on both sides at step 2. mon_emit_value_bin NOT yet wired to GVA inline-store path ([rbx+k*16] direct writes bypass rt_gvar_assign_*); that tap belongs in MON-RE-4b or the NRG rung when GVA inline stores are instrumented. NOTE: rt_gvar_assign_var changed to materialize DESCR_t before NV_SET_fn so the value is available for the tap.
- [x] **MON-RE-5 — CALL/RETURN taps on function boundaries.** DONE (SCRIP `93990cc`, 2026-06-26). Added `mon_emit_call_bin(fname)` / `mon_emit_return_bin(fname, retval)` to `rt.c` (declared in `core.h`): these temporarily raise `kw_ftrace=1` to bypass `comm_call`/`comm_return`'s ftrace gate, emit the MWK_CALL/MWK_RETURN event, then restore `kw_ftrace`. Wired into `rt_call_named_proc`, `rt_call_proc_direct`, `rt_call_named_proc_sl` — all gated on `g_monitor_bin`. Gate: crosscheck `--run PASS=149 FAIL=112`, `--compile PASS=170 FAIL=85`, byte-identical to HEAD.
- [x] **MON-RE-6 — ACCEPTANCE.** DONE (SCRIP `d813b92`, 2026-06-26). 2-way `spl scr` on `/tmp/mdiv.sno` steps 1-8 now AGREE: LABEL 1, LABEL 2, LABEL 4, CALL setit, LABEL 3, VALUE a=STRING(5)=hello, RETURN setit, LABEL 5. Step 9 diverges on END-label only (SPITBOL LABEL stno=6 vs SCRIP END — benign, END not lowered to IR stno). **Semantic acceptance MET: `$nm = vl` semantic divergence (the original target bug) is GONE.** Root causes fixed this session: (1) `gvar_chain_skip_stno` took first stno in chain instead of last → fixed to collect ALL stnos via `gvar_chain_collect_stnos()`; per-node `nstno_extra[8]` array, runtime dedup prevents duplicate LABEL taps across flat bodies; (2) `$nm = vl` (TT_INDIRECT + TT_VAR repl) returned NULL from `lower_stmt_body` → proc body γ chained to next main stmt → setit executed MAIN IR_CALL instead of its own body; fixed by adding `IR_INDIRECT_ASSIGN_VAR` lowering + BB template `bb_indirect_assign_var.cpp` + runtime `rt_indirect_assign_var()` (NV_GET val_name, NV_SET target, VALUE tap); (3) `comm_call/comm_return` fprintf suppressed when `g_monitor_bin` set (monitor tap raises kw_ftrace=1 only for wire-send). Gate: crosscheck --run PASS=149 FAIL=112 / --compile PASS=170 FAIL=85 byte-identical to HEAD.

**Prereq reads (PLAN.md step 7 — touches codegen + per-statement emission):** `MONITOR-BINARY-DESIGN.md` (binary wire spec), `ARCH-SCRIP.md` §Execution modes + §Isolation invariants (no SM/BB walk at runtime — the taps are EMITTED calls, not graph walks, so they comply), `ARCH-x86.md` §Flat-BB-ABI, `src/emitter/bb_regs.h`, `src/runtime/core/core.c` (the `mon_send_bin` family + `MONITOR_READY_PIPE` block), `src/driver/driver_call.c:150-165` (the mode-2 reference tap), `scripts/monitor/monitor_wire.h` (record layout), `scripts/monitor/monitor_sync_bin.py` (the controller).

**Companion tool (harness repo):** `harness/probe/probe.py` (`&STLIMIT`+`&DUMP=2` frame replay, bisect-divergence) is the OFFLINE alternative — it needs scrip mode-3/4 to honor `&STLIMIT` (count+abort) and `&DUMP=2` (var-table dump), NEITHER of which mode-3 currently does (verified). Lower priority than MON-RE because it requires more new native code than re-homing existing taps; tracked here for when MON-RE lands and a no-barrier replay is wanted.


---

# ⛔ SUPERSEDED (pre-GZ#5 reset — numbers stale; live climb = THE RE-LIGHT LADDER above) — was: NEXT SESSION — START HERE (session 30)

**MON-RE-6 LANDED (SCRIP `d813b92`, session 29, 2026-06-26).** 2-way monitor spl vs scr on `/tmp/mdiv.sno` now agrees through 8 steps: LABEL 1/2/4, CALL setit, LABEL 3, VALUE a=hello, RETURN setit, LABEL 5. Semantic acceptance met. Root causes fixed: (1) stno-chain collection (gvar_chain_collect_stnos — ALL stnos per chain, runtime dedup); (2) `$nm = vl` was NULL-returning from lower_stmt_body → proc body executed MAIN body's IR_CALL instead of indirect assign; fixed via IR_INDIRECT_ASSIGN_VAR lowering + BB template + runtime + VALUE tap; (3) comm_call/comm_return fprintf suppressed under g_monitor_bin. Remaining gap: END-label (step 9: SPITBOL LABEL stno=6 vs SCRIP END) — benign, END not in IR stno chain.

**▶ NEXT MOVE: RUNG 1 — climb the crosscheck fail set STATIC-FIRST (read .ref + .s, one stab, verify vs .ref; monitor only on a failed stab). 410-413 (arith in call-arg) CLOSED (SCRIP `795eaef`). 310/311/312 (concat in call-arg) CLOSED (SCRIP `bc18352`) — value-concat `'a' 'b'` as a call arg lowers to an IR_SEQ node (dval=1.0, two sub-arg-blocks) that hit `flat_drive_gvar_seq_passthrough` (no-op) → varslot garbage; fixed via new `rt_concat_parts_d` (DESCR-returning concat) + IR_SEQ exclusion in `gvar_drive_call_arg_slots` + IR_SEQ concat arm in `marshal_call_arg` (flatten→parts-on-frame→call→store); also gave `gvar_seq_flatten` IR_LIT_F support and strdup'd numeric parts (strtab interns by pointer + dumps lazily, so reused static bufs corrupted earlier refs: `X=1 2;Y=3 4`→`34`/`34`). Crosscheck set-level diff: m4 FAIL 79→76 (only the 3 leave, none enter), DIVERGE 22 unchanged, run 156→159, compile 176→179, zero regressions. Next lower-risk sub-rungs: 210-213 (indirect `$X` ref/assign), 091-095 (array/table create/access). Lon pivot 2026-06-27.**

---

## ▶ PRIORITY RUNG (session 29, PRIORITY 1): DEMO-PAT — claws5 + treebank mode-4 PASS + benchmarked

**WHY (Lon):** claws5 and treebank are PATTERN-HEAVY. SPITBOL *interprets* patterns (graph-walk + backtrack history stack, manual Ch.18 "Pattern-match algorithm" — a pushdown stack remembers alternatives, cursor pops on fail). SCRIP *compiles* the backtracking into four-port native control flow (the γ/ω/β edges ARE baked jumps; no history stack at runtime). That is SCRIP's structural advantage — already visible (pattern_bt 0.77×, SCRIP beats SPITBOL). Landing these two demos + benchmarking them proves the home-field win on real corpus programs.

**GROUND-TRUTH DIAGNOSIS (session 29, scrip built + RUN — NOT inferred; oracle NOT in scope, no x64 token).** Both demos HANG in BOTH modes (mode-3 `--run` and mode-4 `--compile` share the pattern codegen; both exit 124 timeout, zero output). The OLD `GOAL-SNO-CLAWS5.md`/`GOAL-SNO-TREEBANK-*.md` "PASS" claims are STALE — they describe the now-DELETED `--run` mode (modes 1/2, `src/driver/interp.c`, C Byrd boxes `bb_seq`/`bb_bal`); that interpreter is gone. Minimal repros (`/tmp/rep/t1`–`t9`, recreate from this list) localize the gaps:
- **t4/t5/t7/t9 = MATCH OK, NO HANG:** stored ARBNO + alternation + POS/RPOS + variable csets (SPAN/NOTANY/BREAK/ANY of DIGITS/UCASE) + `' '` separator all match correctly on real claws lines. **The pattern STRUCTURE works. The match itself does NOT hang.**
- **GAP-1 (ROOT CAUSE of the hang) — deferred-eval function calls as capture targets `(epsilon . *FN())` NEVER EXECUTE.** t6/t8/t9: the side-effect counter stays 0 — `*new_sent()`/`*add_tok()` silently no-op. Both demos build their ENTIRE data structure (`mem` table / parse stack) via these calls. They don't fire → data stays empty → the downstream pretty-printer (`pp_mem`'s `pm_cnt_loop`: `ns=ns+1; ssk[ns,1] :S(pm_cnt_loop)` over `SORT(empty)`) spins forever → THE HANG. Fix GAP-1 and the hang dissolves because the data populates.
- **GAP-2 — captures (`.`) inside an ARBNO repeated body don't COMMIT.** t7: `wrd`/`tag` come back EMPTY after a matching ARBNO. Independent of GAP-1. (D3 commit-ring must truncate-to-mark on ARBNO β-reentry and flush at overall-match γ.)
- **GAP-3 (related, lower priority — demos use STORED patterns so it doesn't block them) — inline non-literal pattern in SCAN context bombs:** t1/t2 → `BOMB bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted)`. Same family; fix opportunistically.
- **treebank ADDITIONAL gaps (beyond claws5):** GAP-4 recursive deferred pattern eval `*group` (a pattern var referenced via `*` inside its own def — recursive descent); GAP-5 `BAL` in built patterns; GAP-6 EVAL-built patterns (`Push_list = EVAL('epsilon . *push_list(' vs ')')` — runtime-constructed pattern spliced into the match); GAP-7 user `DATA` types (`DATA('list(head,tail)')`, M4-DATA).

**SEQUENCING:** claws5 FIRST (needs only GAP-1 + GAP-2). treebank SECOND (claws5 fixes + GAP-4..7). Each step gated on `test_crosscheck_snobol4.sh` byte-identical to HEAD (zero regressions) + the named repro/demo behavior.

### Phase A — claws5 (GAP-1 + GAP-2)
- [ ] **DP-0 — oracle + mode-4 demo harness + bench skeleton.** ✅ ORACLE IN HAND (session 29): `x64` SPITBOL cloned PUBLIC, no token (`git clone https://github.com/snobol4ever/x64`; `x64/bin/sbl -b` works for general programs — verified hello + arith). ⛔ BUT `sbl` does NOT run claws5/treebank: this `sbl` build rejects the `-P` memory flag they need AND `sbl -f` is broken on them (old goal note). **claws5/treebank oracle = SPITBOL** (`sbl -b`) on programs it accepts; `claws5.ref` (SHORT 95-line ref, sentences 1–4) remains the acceptance gate. Still TODO: `scripts/run_demo_mode4.sh` (crosscheck recipe `--compile→gcc -c→gcc -lscrip_rt -lgc -lm→run`, already prototyped at `/tmp/m4run.sh`) + `scripts/test_3way_demo_snobol4.sh` skeleton. No codegen change.
- [ ] **DP-1 — deferred-call-in-capture EXECUTION (the root-cause fix).** **EXACT DIAGNOSIS (session 29, AST-confirmed via `--dump-ast`): `(epsilon . *FN())` parses to `(TT_CAPT_COND_ASGN <pat> (TT_DEFER (TT_FNC FN)))` — the capture target `c[1]` is a `TT_DEFER` node, NOT a `TT_VAR`. BOTH lowering paths take the target as a STATIC string and DROP the deferred expr:**
  - inline scan path — `lower_snobol4.c:308` (`case TT_CAPT_COND_ASGN`): `vn = c[1]->v.sval` → `IR_LIT(nd).sval = vn`.
  - stored/freeze path (the one claws5 hits — `claws = …; src claws`) — `lower_snobol4.c:~576` (`sno_build_leaf_ir`, `IR_PATTERN_CAPTURE`): `IR_LIT(cap).sval = c[1]->v.sval`.
  When `c[1]` is `TT_DEFER`, `->v.sval` is `""`, so FN is never lowered/evaluated → side effect lost (t6/t8/t9: counter stays 0). The runtime write `rt_cap_assign_cursor(varname,sδ,cδ,is_imm)` (`bb_match_capture.cpp`) only accepts a BAKED name — **so this is NOT a 1-liner.**
  **FIX (both paths + runtime):** when `c[1]->t == TT_DEFER`, (a) lower its inner expr (`c[1]->c[0]`, the `TT_FNC`/expr) as a value-producing chain via the stamped EVAL/`run_code_chain`/`dyn-goto` rail; (b) at capture-commit (overall-match γ for `.`; submatch for `$`), RUN that chain (fires FN's side effects), take its return as the assignment NAME; (c) write the matched substring to that name. Add a runtime capture-write variant that accepts a computed name (or runs the deferred chain) — current `rt_cap_assign_cursor` is name-only. ⛔ needs **nv set** ledger STAMP (REQUESTED) for step (c). NOTE: in claws5/treebank the returned name is throwaway `dummy` (value=null) — the POINT is FN's side effect — so step (c) is harmless-but-required; the essential behavior is (a)+(b) EVALUATE the deferred target. Gate: t6/t8/t9 counters increment (`new_sent#`/`add_tok#` > 0); no crosscheck regression.
- [ ] **DP-2 — capture-commit inside ARBNO.** `.` captures in the ARBNO repeated body commit on overall success (D3 ring: SAVE records {ring-mark, δ} per iteration; WRITE appends {nv-ref, sδ, eδ} at element-γ; β-retreat truncates to mark; CAPTURE_COMMIT flushes at match-γ). Gate: t7 returns non-empty `wrd`/`tag`; no regression.
- [ ] **DP-3 — claws5 end-to-end.** mode-4 output byte-matches the DP-0 oracle ref on `claws5.input` (small), then full `CLAWS5inTASA.dat` (989 lines → 5622-line ref); NO hang (terminates < TIMEOUT). Regenerate `claws5.s` artifact (real codegen, no bomb stub). Gate: crosscheck byte-identical; claws5 diff=0.
- [ ] **DP-4 — claws5 BENCHMARK (the home-field proof).** Run claws5 mode-4 vs SPITBOL (`sbl -b`) via `test_3way_demo_snobol4.sh`; record wall-ms ratio in this goal. EXPECTATION: pattern-heavy → SCRIP competitive-or-faster (the four-port-compiles-the-backtracking thesis). Record the honest number whatever it is.

### Phase B — treebank (claws5 fixes + GAP-4..7)
- [ ] **DP-5 — user DATA types in mode-4 (M4-DATA).** `DATA('list(head,tail)')` constructor + field selectors `head(x)`/`tail(x)` + `list(a,b)`. Gate: a `list` round-trips; treebank's `stk = list(frame_id, stk)` / `head(stk)` / `tail(stk)` work.
- [ ] **DP-6 — BAL in built patterns.** The B7 BAL sub-rung: balanced-paren scan (depth counter in per-box scratch, per-char ()-balance in α, regenerating). Gate: `('(' BAL ')') . item` extracts a balanced group; `spat` in treebank matches one s-expression.
- [ ] **DP-7 — recursive deferred pattern eval `*group`.** A pattern variable referenced via `*` inside its own definition: deferred DT_P fetch + real β re-entry into the embedded sub-graph (B10 + S3 instance re-entry). ⛔ recursion guard (manual Ch.8: a pattern recursing without consuming subject overflows — match real `icont`/sbl semantics: progress before recursion). Gate: nested s-expression `((a b) c)` parses to correct depth.
- [ ] **DP-8 — EVAL-built patterns.** `Push_list = EVAL('epsilon . *push_list(' vs ')')` — runtime CODE/EVAL produces a DT_P that is spliced into the enclosing pattern at match time. Reuses the stamped EVAL rail + DP-1 deferred-call-in-capture. Gate: `Push_list('tag')`/`Pop_list()`/`Push_item('wrd')` fire during the match; stack builds.
- [ ] **DP-9 — treebank end-to-end + BENCHMARK.** mode-4 byte-matches oracle on `treebank.input` (regenerate ref against live oracle per DP-0); regenerate `treebank-array.s`; add to `test_3way_demo_snobol4.sh`; record wall-ms ratio. Gate: crosscheck byte-identical; treebank diff=0; bench number recorded.

**Prereq reads (PLAN.md step 7 — touches per-box pattern state):** `SNOBOL4-5STAGE-OWNED-BUILD.md` (D3 capture-commit ring, B7 BAL, B8 capture-in-built, B9 ARBNO, B10 DEFER-IN-BUILD — DP-1/2/6/7/8 ARE those rungs, re-sequenced demo-first); ARCH-SNOBOL4.md §Native pattern; `src/emitter/bb_regs.h`; `src/runtime/rt/bb_pat_build.cpp`; `src/emitter/emit_core.c` matcher dispatch; the permission ledger in SNOBOL4-5STAGE (DP-1 needs **nv set** STAMPED — currently REQUESTED).

---

## ▶ PRIORITY RUNG (session 29, PRIORITY 2): NRG — Native Register Codegen ("beat the interpreter on statements")

**THESIS (the reframing that makes "true compiler beats interpreter" tractable).** SPITBOL is NOT a fetch-decode-execute interpreter — for statements it is an **indirect-threaded-code VM** (manual history ch.: "compiling to an intermediate language of indirectly threaded code … a highly optimized run-time system then interprets the thread"). Threaded dispatch ≈ ONE indirect branch per op (`*next++`); no decode, no central loop; primitives are hand-tuned assembly. So SCRIP CANNOT win by "removing the dispatch loop" — threading already removed it. SCRIP currently LOSES on statements (15/16 benchmarks) because it replaced the cheap threaded NEXT (one indirect branch) with an EXPENSIVE PLT **call** per primitive (full System V convention) — *worse than threading*. NRG-A merely restores PARITY (inline → no call boundary). The ONLY way to BEAT threaded code is the one thing a threaded VM structurally cannot do: **specialize to the program** — keep a proven-typed value in a register and emit raw machine ops, with NO per-op tagged-descriptor load/store and NO per-op type re-check. (Patterns are the OTHER battleground and SCRIP already wins there — see DEMO-PAT; this rung is statements only.)

**EVIDENCE (assembly-traced, session 29).** `arith_loop.s` one iteration of `N=N+1; N=LT(N,1e6) N`: `N` is loaded from `[rbx+16/24]` and its `DT_I` tag re-checked (`cmp edx,6`) **twice** (LT box `bb13` + arith box `bb14`), plus a dead store-then-reload of slot 80 and a slot-96 round-trip — ~25 instrs where a register-resident DT_I counter needs **3** (`cmp r14,1e6; jge done; add r14,1`). `func_call.s` INC body (`INC=N+1`): **three** PLT calls — `call NV_GET_fn` (fetch N, result DEAD/unused), `call rt_gvar_get_int` (fetch N AGAIN), `call rt_gvar_assign_int` (store) — to add 1. Plus `rt_call_proc_direct`'s ~15-op save/restore protocol per call. SPITBOL threads all of this with values in registers and locals at known offsets.

**Each sub-rung independent; gate = `test_crosscheck_snobol4.sh` byte-identical (PASS=171 FAIL=84, fail SET unchanged, every stdout identical) + both-medium (mode-3==mode-4) + regenerate benchmark/feature/demo `.s` + A/B wall-ms on its target. Template-only / four-Greek-port / ledger-gated per RULES.** Order A → E → B → C → D (cheap CFG/dataflow cleanups first; they de-risk the register allocator by removing the redundancy that would confuse it; B is the lever that flips arith-class benchmarks; C/D kill the call cluster).

### NRG-A — VN: local value-numbering / redundant-load elimination (do FIRST — cheapest, broad)
- [ ] **VN-0** — within a straight-line (non-β-reentrant) box chain, value-number `[rbx+k*16]` loads + their `DT_I` tag-checks; a second identical load reuses the register. Kills arith_loop's 2nd N-load + 2nd tag-check, INC's dead `NV_GET_fn`.
- [ ] **VN-1** — drop store-then-reload of the same frame slot (`mov [r12+s],rax; … mov rax,[r12+s]`) and dead `IR_VAR` boxes whose slot is never read.
- [ ] **VN-gate** — byte-identical crosscheck; A/B arith_loop, op_dispatch, func_call.

### NRG-B — REG: register residency + static type tracking (the DEEPEST win — the only thing threading can't do)
- [ ] **REG-0** — liveness + "single-type-throughout" analysis: mark a scalar DT_I throughout a loop/body when assigned only by arithmetic, no EVAL/CODE/indirect-assign/I/O-assoc to it (reuse FZ invariance-proof + GVA DT_I guard).
- [ ] **REG-1** — allocate the proven counter to a callee-saved reg across the loop; emit `add/cmp/jcc` directly; spill to `[rbx+k*16]` only at loop exit + escape edges (spill is already-stamped GVA territory — NO new ledger). Target: arith_loop inner loop → 3 instrs.
- [ ] **REG-2** — extend to function-body locals proven DT_I (fibonacci `N`, INC `N`).
- [ ] **REG-gate** — ⛔ register value re-materializable at every β/ω edge + fallback; verify vs `sbl -b` arith_loop/fibonacci/mixed_workload. A/B arith_loop, fibonacci.

### NRG-C — INL: leaf-function inlining (eliminates the call protocol for tiny procs)
- [ ] **INL-0** — inlinability analysis in lower (≤N stmts, non-recursive, statically resolved — DCR-2 `__proc[]` already proves the static-call set).
- [ ] **INL-1** — splice callee four-port graph at the call site, param→arg substitution, return var → local temp. `R=INC(R)` → `R=R+1` inline.
- [ ] **INL-gate** — byte-identical; recursion guard; A/B func_call, func_call_overhead.

### NRG-D — PROTO: specialized call protocol (for non-inlinable/recursive calls)
- [ ] **PROTO-0** — emit per-call-site block save/restore through the known param/return cells (cells resolved at preamble à la DCR-2); no per-call loop, no fastpath re-check. ⛔ needs **nv set** ledger STAMP (currently REQUESTED).
- [ ] **PROTO-gate** — byte-identical; A/B fibonacci (recursive), roman.

### NRG-E — BOPT: branch chaining (scaffolded `src/opt/branchopt.c` `bopt_chain` — UNWIRED; Makefile compiles but does not link it)
- [ ] **BOPT-1** — wire `bopt_chain` as a LOWER→EMITTER pass + cycle guard (generator self-loops / `to.code` back-edges must not collapse). ⛔ honor the prior crash: γ-spine doubles as operand-recovery; rechain ONLY edges proven not to shorten an operand-recovery walk (gate on the deterministic chains VN proved safe).
- [ ] **BOPT-2** — dead-BB drop + fall-through layout (common path takes no branch).
- [ ] **BOPT-gate** — byte-identical; emitted-jump-count delta + A/B across all 16.

**Prereq reads:** the uploaded Proebsting four-port paper (§4 templates, §5/Figs 1–2 optimization — **persist to repo `docs/`**); ARCH-x86.md §Flat-BB-ABI + §Boxes-are-stackless; `src/lower/lower_snobol4.c`; `src/emitter/emit_bb.c` (FILL/port machinery + flattener); `src/emitter/BB_templates/x86_asm.h`.
---

## ▶ RUNG: SCAN-CLASS — specialize the cset-matching scanners (fold → table → unroll)

**GROUND TRUTH (session, emitter-verified — NOT inferred).** The literal-vs-variable dispatch and RIP-relative constant-folding ALREADY EXIST for these primitives:
- `lower_snobol4.c:522` routes SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB down a LITERAL arm (arg ∈ {QLIT,ILIT,CSET}) vs a VARIABLE arm.
- POS/RPOS literal integers are ALREADY folded to immediates: `bb_match_pos.cpp:17` `cmp r14d,<imm>`; RPOS `sub ecx,<imm>; cmp r14d,ecx`; `bb_scan_pos.cpp:15` `cmp64 r14,<imm>`.
- ANY/SPAN/BREAK literal csets are ALREADY sealed RIP-relative: `bb_scan_any/many/upto` literal arms emit `ROQ(0)` + `.string`. They still `strchr` the sealed string per subject char — the inner-loop cost SCAN-TABLE/SCAN-UNROLL attack.
- NSPAN does NOT exist in `src/` (no token/IR/template) — a NEW primitive, not a folding task.

So constant-folding-into-RIP is largely DONE. Remaining: (1) a coverage AUDIT; (2) the inner-loop algorithm (table/unroll), PARKED below per Lon (2026-06-27); (3) **the VARIABLE-operand TWIN of each primitive — the SCAN-GEMINI rung below (Lon directive 2026-06-27: "every BB here should have a gemini").**

---

## ▶ RUNG: SCAN-GEMINI — every scan/match primitive gets its variable-operand TWIN (Lon 2026-06-27)

**THE GAP (session 30, RUN-confirmed — NOT inferred).** Each scanner primitive currently has a LITERAL box (operand folded: integer→immediate `cmp`, cset→`.string` sealed RIP-relative reached via `ROQ(n)`/`lea [rip+__]`). Its VARIABLE twin (operand is a `TT_VAR`/`TT_KEYWORD` resolved at runtime) is MISSING for all but SPAN — and even SPAN's twin (`IR_MATCH_SPAN_VAR` + `bb_match_span_var.cpp`) is UNREACHED in the common capture case. **Live proof:** `S ? SPAN(DIGS) . M`, `ANY(CS) . M`, `NOTANY(CS) . M`, `BREAK(CS) . M` (CS/DIGS a variable) ALL bomb `libscrip_rt: BOMB — bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted)`; oracle (`sbl -bf`) returns `123`/`1`/`a`/`abc` respectively.

**THE MECHANISM (emitter-traced).** Lowering ALREADY tags the variable case (`lower_snobol4.c` TT_SPAN/ANY/NOTANY/BREAK/BREAKX/POS/RPOS/TAB/RTAB/LEN arms): variable arg → `IR_LIT(nd).sval = <VARNAME>` + a marker (`dval=1.0`/`2.0`, or SPAN's `ival=1`); literal arg → `sval = <cset string>` or `ival = <int>`. Then `scan_pat_m3_native_safe()` (`emit_bb.c:2560`) returns 0 (forces the STORED/`bb_match_*` family instead of inline `bb_scan_*`) precisely when the marker is set (`dval!=0.0` for POS/LEN/TAB/RTAB/ANY/NOTANY/BREAK/BREAKX; `ival==1` for SPAN). In the match family ONLY SPAN has a `_VAR` opcode+template; the other seven fall through to their LITERAL template, which bakes the variable's NAME string as if it were the cset (cset prims) or reads a stale `ival` (int prims) → wrong result or the PB-RB bomb. **The fix is the missing twin per primitive + the routing that reaches it.**

**THE REFERENCE TWIN (the one that exists — mirror it).** `bb_match_span_var.cpp`: `lea rdi,[rip+VARNAME]` → `call rt_nv_cstr` (fetch the variable's cset string by name at runtime; `rt.c:98`) → store the `char*` to a claimed scratch slot (`bb_slot_claim(16)`) → the SAME inner `strchr` loop the literal SPAN uses, but `rdi` reloaded from the slot each char. FILL wiring at `emit_bb.c:3040` (`IR_MATCH_SPAN_VAR`: `op_name1 = sval(varname)`, `op_name2 = "bb_spanv"`, claim scratch). **Every cset twin is this shape; every int twin is the same minus the cset loop (fetch int via a numeric NV getter, then the primitive's `cmp`).**

### Sequencing (cset twins first — they unblock the pattern-heavy demos; SPAN reachability first since its template already exists)
- [ ] **GEM-0 — make the variable-cset pattern REACH the per-primitive native boxes (the prerequisite the twins sit behind).** **GROUND TRUTH (session 30, RUN-traced):** `SPAN(DIGS) . M` etc. bomb in `bb_scan_stmt.cpp:39` (`bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted)`), NOT in any per-primitive box. `bb_scan_stmt` is the WHOLE-STATEMENT scan box: it has a fully-literal fast path (`op_scan_pat_lit` set → one `call rt_scan_lit` with the whole pattern baked as a string) and bombs otherwise. A variable cset makes the pattern non-bakeable → `op_scan_pat_lit==NULL` → bomb. **So the pattern is NEVER decomposed into the per-primitive native match boxes where `bb_match_span_var` (and the GEM-1.. twins) live.** Therefore GEM-0 is the DECOMPOSITION/BUILD step, not a one-line op promotion: a non-literal `SUBJ ? PAT` must route to the native PB-RB built-graph path (the builder-BBs-that-build-BBs → generic `BB_MATCH` box, per ARCH-SNOBOL4.md "Native pattern architecture — modes 3 & 4") so the pattern's primitive boxes (`IR_MATCH_SPAN_VAR`, etc.) are actually emitted and run. This is the SAME root as DEMO-PAT GAP-3 ("inline non-literal pattern in SCAN context bombs"). `IR_MATCH_SPAN_VAR` being referenced-but-never-assigned in `src/` is the symptom: nothing builds the decomposed graph that would carry it. **Sub-steps:** (a) confirm/locate the native PB-RB build entry the literal path bypasses; (b) route `bb_scan_stmt`'s non-literal-pattern case into it instead of bombing; (c) ensure the marked-variable primitive (`ival==1`/`dval!=0`, `sval=varname`) lands as its `_VAR` box in the built graph. Gate: `/tmp/spanvar.sno` (`SPAN(DIGS) . M` → `123`) passes both modes; crosscheck fail set ⊆ HEAD (zero regressions); `.s` regenerated. ⛔ This is multi-file pattern-engine work (shares surface with DEMO-PAT DP-3/GAP-3) — budget a full session; do it MONITOR-first if a partial graph diverges.
- [ ] **GEM-1 — ANY_VAR twin.** New `IR_MATCH_ANY_VAR` opcode (IR.h) + `bb_match_any_var.cpp` (mirror span_var: `rt_nv_cstr` fetch → slot → ANY's single-char `strchr` test, success on match). Lowering: TT_ANY variable arm emits `IR_MATCH_ANY_VAR` (or normalize promotes `IR_MATCH_ANY` w/ `dval!=0`). FILL arm in `emit_bb.c` (claim scratch, `op_name1=varname`). Dispatch in `emit_core.c`. Gate: `ANY(CS) . M` → `1`; crosscheck ⊆ HEAD; both-medium (mode-3==mode-4); `.s` regen.
- [ ] **GEM-2 — NOTANY_VAR twin.** As GEM-1, inverted test (success when the char is NOT in the fetched cset). Gate: `NOTANY(CS) . M` → `a`; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-3 — BREAK_VAR twin.** As GEM-1, BREAK semantics (advance cursor until a char IN the fetched cset; cursor stops before it). `bb_match_break`'s literal loop, cset reloaded from slot. Gate: `BREAK(CS) . M` → `abc`; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-4 — BREAKX_VAR twin.** As GEM-3 plus BREAKX's retry-extend semantics (the two `strchr` sites in `bb_match_breakx.cpp`, both cset-reloaded). Gate: a BREAKX-of-variable program matches oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-5 — POS_VAR / RPOS_VAR twins (integer).** `bb_match_pos` currently folds `op_ival`; the variable case (`POS(N)`/`RPOS(N)`, `dval=2.0`/`1.0`, `sval=varname`) needs an int-NV fetch (`rt_gvar_get_int(varname)` → register) then the SAME `cmp r14d,reg` (POS) / `mov ecx,r15d; sub ecx,reg; cmp r14d,ecx` (RPOS). One new opcode pair or a `op_name`-driven arm inside `bb_match_pos`. Gate: `POS(N)`/`RPOS(N)` with variable N match oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-6 — TAB_VAR / RTAB_VAR twins (integer).** As GEM-5 for `bb_match_tab`/`bb_match_rtab` (the `cmp`/`mov32 r14d` and the RTAB `sub` use a fetched register instead of `op_ival`). Gate: `TAB(N)`/`RTAB(N)` variable match oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-7 — LEN_VAR twin (integer).** `bb_match_len` variable-N twin (fetch int, `cmp`/advance by register). Gate: `LEN(N)` variable matches oracle; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-8 — scan-family variable arms (inline-context twins).** `bb_scan_many` (SPAN), `bb_scan_upto` (BREAK), `bb_scan_tab` already-slot — add the `var cset`/`var int` arm to each inline scanner the way `bb_scan_any` already carries BOTH arms (literal via `ROQ`, variable via `FRQ(op_sa+8)`/`rt_nv_cstr`), so a marked-variable primitive in an inline (non-stored) `S ? ... = ...` context need not be forced into the stored family by `scan_pat_m3_native_safe`. Then RELAX `scan_pat_m3_native_safe` to allow the now-handled variable inline shapes. Gate: a variable-cset inline replace (`S ? SPAN(var) = X`) matches oracle in both modes; crosscheck ⊆ HEAD; both-medium; `.s` regen.
- [ ] **GEM-9 — GEMINI completeness gate (audit + prison).** Grep proof every primitive has BOTH a literal box and a variable box reachable: a script `test_gate_scan_gemini.sh` that compiles one literal + one variable program per primitive and asserts (a) neither bombs, (b) both match `sbl -bf`. Wire into the SNOBOL4 gate. This is the rung's completion test.

**Prereq reads (PLAN.md step 7 — per-box pattern state + per-statement emission):** `bb_match_span_var.cpp` (the reference twin), `lower_snobol4.c` TT_SPAN/ANY/NOTANY/BREAK/BREAKX/POS/TAB/RTAB/LEN arms (the literal-vs-variable tagging), `emit_bb.c:2560` `scan_pat_m3_native_safe` + `:3035` the FILL switch, `emit_core.c:371-383` the dispatch, `rt.c:98` `rt_nv_cstr`, `bb_regs.h`. NOTE: GEM overlaps SCAN-TABLE-2 (runtime-cset table) — the table is the FAST inner loop; GEM is the CORRECT one. Do GEM first (correctness), table later (speed); the table then drops into each `_var` twin's loop.

### SCAN-FOLD — audit + close constant-folding coverage (the only ACTIVE scan-class rung)
- [ ] **SCAN-FOLD-0 — coverage audit (no code change).** For ANY/NOTANY/SPAN/BREAK/BREAKX (× `bb_scan_*` inline AND `bb_match_*` stored/native families) and POS/RPOS/LEN/TAB/RTAB: confirm the literal arm seals its constant RIP-relative (cset via ROQ/.string) or immediate (integer via `cmp imm`), with NO frame load / NO runtime arg-eval on the literal path. Deliverable: table {primitive × family → folded? Y/N/site}.
- [ ] **SCAN-FOLD-1 — close any unfolded literal arm.** Any primitive the audit marks N (literal arg still frame-loaded) → seal RIP-relative/immediate like its siblings. Gate: crosscheck byte-identical; both-medium; regenerate only the closed primitive's `.s`.
- [ ] **SCAN-FOLD-2 — NSPAN (decision, not auto).** NSPAN (nullable span, ≥0) is unimplemented; adding it is a NEW primitive (parser token + lower + `bb_*nspan`, ≥0 loop-exit vs SPAN's ≥1), its own rung — NOT a folding step. PARK until Lon requests.

### SCAN-TABLE — baked character-class classifier (PARKED — Lon: "for later")
Replace the per-char `strchr(cset,ch)` (PLT call + O(cset-len) scan) in `bb_scan_any/many/upto/bal` (+ `bb_match_*` cset loops) with a baked classifier reached RIP-relative — the real inner-loop win.
- [ ] **SCAN-TABLE-0 — pick form.** 256-byte 0/1 table (`movzx eax,[r13+rcx]; cmp byte [rip+tbl+rax],0`) vs 32-byte bitmap (`bt`). Lean: 256-byte table for streamers (single indexed load). ⛔ char UNSIGNED (movzx 0–255) — bytes ≥128 (&ALPHABET) misclassify otherwise.
- [ ] **SCAN-TABLE-1 — literal cset → bake table into RO data, sealed adjacent, RIP-relative.** Build the 256-entry table at emit time from the literal cset; emit in the sealed RO region; rewrite the literal arm's inner loop to the indexed test. Add the x86 form to x86_asm.h (both-medium). Gate: crosscheck byte-identical; A/B SPAN/BREAK on string_pattern/pattern_bt; `.s` regenerated.
- [ ] **SCAN-TABLE-2 — runtime cset → built-once table (SPITBOL parity; bulk of the win).** Represent a cset VALUE as a 256-entry table built once when its string materializes, memoized on the descriptor; the variable arm's loop uses it. Covers `BREAK(WORD) SPAN(WORD)` (wordcount/claws5/treebank). ⛔ rebuild on cset reassignment. Gate: crosscheck byte-identical; A/B wordcount.

### SCAN-UNROLL — inline-compare / unrolled small literal csets (PARKED — Lon: "for later")
Tiny literal csets (≤~10 chars): skip the table, emit direct `cmp al,cN; je` chains (`SPAN(' ')`/`BREAK(',')`/`ANY('+-')` → one compare). Faster than the table load for the common short-cset case.
- [ ] **SCAN-UNROLL-0 — threshold + dispatch.** Choose N (≤10); literal cset len ≤N → unrolled-compare arm, else → SCAN-TABLE arm, else (variable) → table/strchr. 1-char fast path first (highest frequency).
- [ ] **SCAN-UNROLL-1 — emit unrolled compares per the primitive's loop semantics** (ANY = OR-of-compares→match; NOTANY = none-match→match; SPAN/BREAK = loop-exit condition). Both-medium. Gate: crosscheck byte-identical; A/B on a single-char-cset-heavy program.

**Sequencing (Lon).** SCAN-FOLD (audit) is small — folding is already in place. SCAN-TABLE-2 (runtime-cset table) holds the bulk of the inner-loop win; SCAN-TABLE-1 + SCAN-UNROLL cover the literal cases. All gated A/B (the win is MEASURED, not assumed); template-only / four-Greek-port / both-medium; `.s` regenerated per touched primitive.


---

**RPF + TABLE-WALK-FIX LANDED (SCRIP `8ef7412`, session 27, 2026-06-25).** Two PERF-CALL wins; gate PASS=171 FAIL=84 SKIP=6 (zero regressions, fail set byte-identical to HEAD), both-medium clean, all results match .ref. Artifacts regenerated (benchmark/feature/demo .s).

(1) **RPF — relop GVA-parity** (`bb_call.cpp`): `arith_opnd_a/b` gained a `gk_lb` param (default=-1, all existing callers unchanged → byte-identical output). `bb_call_relop_inline_str` passes `gk_lb=0/2` + calls `x86_begin()`. When the operand is a GVA global (k≥0): emits `mov rdx,[rbx+k*16]; cmp edx,DT_I; jne slow; mov reg,[rbx+k*16+8]`; falls through to existing `call rt_gvar_get_int` on miss. Same DT_I-guarded pattern as `bb_binop_gvar_arith.cpp`. Fibonacci GVA-guard count unchanged (frame param, correctly untouched). **A/B (best-of-3, mode-4 native, SCRIP-vs-SCRIP):** op_dispatch 248→19ms (13.1×), arith_loop 121→13ms (9.3×), var_access 1478→238ms (6.2×), func_call 5206→4157ms (1.25×), pattern_bt 328→264ms (1.24×), table_access 3244→2758ms (1.18×). Moderate wins where the relop is not dominant; zero effect where operand is a frame param.

(2) **Table get double-walk elimination** (`aggregates.c` + `core.h` + `pattern_match.c`): added `table_get_found(tbl,key,*found)` — one chain walk, explicit found flag. `subscript_get` DT_T: was `table_has()+table_get()` (2 walks); now `table_get_found()` (1 walk). Same dflt/NULVCL branches. table_access 2758→2410ms (1.14× this change; **3244→2410 = 1.35× combined** with RPF). result: 250500 correct.

**SPITBOL re-grounding NOT done this session** — `x64` oracle token not in scope. The SCRIP-vs-SCRIP speedups are solid. Honest inference: op_dispatch/arith_loop/var_access likely flip to faster-than-SPITBOL (prior ratios were 2.29×/2.90×/1.05×; the RPF drop is ~13×/9×/6×), but that needs oracle confirmation. SPITBOL re-grounding is the first task of the next session that has the `x64` token.

**▶ NEXT MOVE (session 28): DCR-2 — codegen-side proc resolution (the named open rung in the DCR ladder).** Replace the per-call `lea rdi,name; call rt_call_named_proc` with a baked proc index/cells resolved at preamble (`__proc[]` table, GVA-analogous), so the call site does `mov rdi,[rip+__proc+k*8]; call rt_call_proc_direct` — eliminates even the cache lookup. `emit_bb.c` IR_CALL arm + `lower_snobol4.c` (mark statically-resolvable `IR_CALL`s; keep by-name fallback for `$FN`/OPSYN/runtime-DEFINE). Gate: crosscheck byte-identical; further `func_call`/`fibonacci` delta. See DCR-2 step below.

**OPT rung status (session 27 investigation):** BOPT-1 (in-place γ/ω mutation) attempted, built, wired, crashed (`flat_drive_assign FATAL` — γ-spine is overloaded as operand-recovery structure; in-place edge mutation shortens the spine the operand-recovery walks). Quantified: 34/1686=2% collapsible branches corpus-wide, 0% in hot loops; 793 dead beta-resume stubs (size/build-time, not runtime). Safe forwarder chaining already done by `gvar_chain_resolve_stmt`. Copy-prop: 23 instances corpus-wide (~1/benchmark). **OPT rung is CLOSED as a perf lever.** `src/opt/branchopt.{c,h}` retained as dead-end record. Full analysis in `docs/BOPT-DESIGN.md`.

**KEYWORD-CONCAT BOMB FIXED (SCRIP `c6d8c28`).** `X = &UCASE &LCASE` (and any concat with a `TT_KEYWORD` operand) no longer bombs `bb_gvar_assign_concat: no parts (not flattenable)`. Root cause: `sno_seq_flatten_ops` did not flag `TT_KEYWORD` as `nonleaf`, so keyword operands fell through the foldable-leaf path (which accepts only `TT_QLIT`) and dropped into the unimplemented `IR_SEQ` runtime-concat path with zero `op_parts`. Fix: one line — add `t->t == TT_KEYWORD` to the `nonleaf` trigger, routing keyword operands through the already-proven `sno_concat_chain` binary-chain path (`IR_BINOP_CONCAT`). Gate: crosscheck PASS=171 FAIL=84, fail set byte-identical to pristine HEAD (zero regressions). `wordcount.s` feature artifact updated (was bomb stub, now real codegen). 5 new demo `.s` committed (arithmetic/counter/hello/pattern_test/porter — previously never generated). Note: `wordcount` closes the codegen bomb but still **hangs** in its inner match-replace loop (`NEXTW LINE ? WPAT =`) because `WPAT = BREAK(WORD) SPAN(WORD)` with runtime-computed `WORD` cset hits the same deep pattern-engine gap as `word1`–`word4`/treebank/claws5 (crosscheck fail set, broader pattern-engine work). Benchmark timing confirmed across all 16 benchmarks: PASS=15/16 (eval_dynamic = documented OOM, correct at low N). Mode-4 native vs mode-3: arith_loop 113ms/862ms (7.6×), op_dispatch 233ms/2008ms (8.6×), table_access 3153ms/7088ms (2.2×).

**▶ NEXT MOVE (session 25): DCR-2 — codegen-side resolution (drop by-name proc call entirely). See DCR-2 step below.**

**THREE-WAY COMPARISON — RE-GROUNDED post-DCR (session 27, 2026-06-25; DCR-3).** All 16 benchmarks run SCRIP mode-4 (AOT native) vs SPITBOL (`sbl -b`). Reproducible: `scripts/test_3way_snobol4.sh` (wall-clock ratio). **Correctness: 14/14 result-bearing benchmarks byte-identical across SCRIP and SPITBOL** (`arith_loop` and `indirect_dispatch` emit no `result:` line, so they are correctness-`?` not graded). `indirect_dispatch` remains the one known DIVERGENCE (`R = $FN(X)`, `FN='ADD1'`): SPITBOL ERRORS ("undefined function called"), SCRIP returns blank `R` — the divergence is in ERROR behavior, not a printed result, so no engine emits a comparable `result:` line; nothing gates it. **Performance (wall-ms ratio = SCRIP/SPITBOL): SCRIP is SLOWER than SPITBOL on 15/16, ≈parity or faster on 1.** Re-grounded ratios: arith_loop 2.90×, op_dispatch 2.29×, string_concat 10.01×, eval_fixed 8.16×, mixed_workload 12.11×, table_access 10.86×, roman 21.80×, **fibonacci 10.50× (was 23.1× — DCR HALVED it)**, string_pattern 10.35×, string_manip 17.22×, **func_call_overhead 6.62× (was 13.3×)**, **func_call 6.65× (was 14.2×)**, eval_dynamic 165.47×. var_access 1.05× (≈parity; was 0.77× faster — slipped to parity, measurement-sensitive at `-O0` gcc of the native `.s`). **Faster than SPITBOL on 1:** pattern_bt 0.77× (FZ path). **DCR EFFECT (the headline of this re-grounding):** the function-call cluster — the whole point of the DCR ladder — dropped from ~14–23× to ~6.6–10.5×: func_call 14.2×→6.65× and func_call_overhead 13.3×→6.62× (cell-cache + memoized cells, both ~2.6×), fibonacci 23.1×→10.50× (~2.2×). The A/B numbers (DCR-1 func_call 2.61×, fibonacci 2.07×) are confirmed at the whole-benchmark level. **roman barely moved (22.7×→21.80×)** — honest: roman's per-call cost is dominated by the pattern-match + `REPLACE`, not the call save/restore protocol DCR optimized, so the protocol win is a small slice of roman's work. **The "10×" headline is STILL inverted for general workloads — DCR narrowed the call cluster by ~2× but did not close it.** Root cause unchanged (assembly-traced): native control flow but a runtime PLT call per SNOBOL primitive that SPITBOL inlines/threads. eval_dynamic COMPLETES in ~72s (NOT OOM; the bench-script "CRASH" is its 30s timeout). The remaining PERF-CALL sub-rungs (AXS done; SAB, table-probe) inline the next primitives.

**FZ-5b LANDED (SCRIP `6141434`).** Match sites referencing a once-assigned invariant pattern variable now bake the sealed matcher head directly (RIPSEAL lea) and skip the per-match `rt_defer_get_pat_fn` fetch — the hot-loop win for string_pattern/pattern_bt (500k× fetch eliminated). Three pieces: (1) FZ-5a: `fz_inlinable_head()` once-assigned-invariant analysis in `lower_snobol4.c` — conservative proof (assigns==1 AND frozen head recorded AND no indirect-assign/EVAL/CODE/CONVERT in program); behavior-neutral foundation. (2) FZ-5b: `flat_drive` IR_MATCH_DEFER case in `emit_bb.c` stages `child_cache_get`/`child_cache_get_lbl` when `fz_inlinable_head` hits; `bb_match_defer.cpp` branches on `bb_child_fn`/`bb_child_lbl` presence — inline path bakes frozen head, fetch path unchanged. Reuses RIPSEAL lea (both-medium clean). Cross-language safe (NULL for non-SNOBOL4). Gate MET: crosscheck PASS=171 FAIL=84 SKIP=6, fail set byte-identical to baseline (zero regressions). `.s` artifacts updated: string_pattern/pattern_bt/mixed_workload benchmarks now show inline marker + zero `rt_defer_get_pat_fn` calls. FZ-5b timing MEASURED (session 24, A/B = inline-on vs forced-fetch baseline, 5-trial min self-ms): string_pattern 8557→7590ms (**1.13×**), pattern_bt 1125→401ms (**2.81×**). Spread is the mechanism working — pattern_bt is one match/iter so killing the per-match `rt_defer_get_pat_fn` dominates; string_pattern also runs the INNER concat/replace loop so the fetch is a smaller slice. Verified live in codegen: 0 `rt_defer_get_pat_fn` calls, old per-shape builders absent, both outputs byte-match `.ref`.

**FZ-4 (Option B) LANDED (SCRIP `6141434`).** Bare invariant captures (`PAT = BREAK(',') . W`) now freeze to `IR_REF_INVARIANT` — the general `sno_freeze_pat_graph_entry` path — retiring `bb_build_break_capture_blob`. Full deletion set: `bb_build_break_capture_blob`, `bb_build_break_cap_lit_blob`, `sno_break_cap_lit_graph`, `sno_freeze_break_cap_lit_bin`, `sno_freeze_break_cap_lit_text` (all removed from `bb_pat_build.cpp`). `bb_pattern_cat.cpp` / `bb_pattern_capture.cpp` reduced to passthrough-only (Raku keeps passthrough; SNOBOL4 pat_via_dtp builder arm removed). `emit_core.c` dead pat_via_dtp BREAK.VAR-LIT extraction collapsed to stub. Key correction vs goal-file premise: `bb_build_break_capture_blob` was NOT dead before this rung — bare buildable captures still routed through it; FZ-4 Option B REDIRECTED that path to freeze rather than simply deleting a dead function. Gate MET: crosscheck byte-identical, build clean.

**▶ NEXT MOVE: FZ-5b timing + GVA-4 or OPSINGLE — Lon decides.**


## ▶ PRIORITY RUNG (do FIRST, session 27): OPT — IR/codegen optimizer passes (Lon pivot, Proebsting four-port)

**PIVOT (Lon, 2026-06-25):** stop hand-inlining individual hot primitives (RPF relop-prefetch and SAB self-append are HELD). Beat SPITBOL *on its own terms* by adding the GENERAL optimizer passes that Proebsting's four-port paper — "Simple Translation of Goal-Directed Evaluation" (uploaded `8_Simple_Translation_of_Goal_Directed_Evaluation.pdf`; **add to repo `docs/` for persistence**) — explicitly prescribes. SCRIP's emitter IS that four-port scheme: every operator template emits `.start/.resume/.fail/.succeed` chunks wired by gotos; in the generated `.s` these are the Greek `α`(start)/`β`(resume)/`ω`(fail)/`γ`(succeed) labels and the `snoch0_n<k>_<port>` BB labels. The paper (§5, Fig 1→Fig 2) states the naive expansion "suffers from generating many simple copies and many branches to branches," and that "propagating copies and eliminating branches to branches (by branch chaining and reordering the code)" yields code that "closely resembles … two generic `for` loops." This is a per-`.s` win on EVERY generated function — the structural complement to the PERF-CALL ladder (which attacks per-primitive call cost; OPT attacks the wiring overhead between primitives).

**EVIDENCE (assembly-traced, session 27).** `arith_loop.s` / `op_dispatch.s` are saturated with jump-to-jump chains the four-port wiring creates by construction: e.g. `snoch0_n10_β: jmp snoch0_n13_α`, the pair `jmp snoch0_n14_α … snoch0_n11_β: jmp snoch0_n10_α`, and EVERY template tail is `jmp γ; β: jmp ω`. The ports are explicit IR edges (`nd->γ.node`, `nd->ω.node`, the `EMIT_PAIR_FILL(nd, lbl_γ, lbl_ω, lbl_β)` machinery in `emit_bb.c`), so they can be re-wired at the IR level BEFORE template expansion — collapsing each chain to ONE jump rather than peephole-patching the emitted text. Three passes, independent, in pipeline order:

### BOPT — Branch optimizer (IR→IR, NEW stage AFTER lower, BEFORE emitter)
The primary/immediate pass. Re-wire the four-port edges so a port targeting an unconditional-goto BB points directly at that goto's ultimate target (Byrd chaining), then drop the emptied BBs.
- [ ] **BOPT-0 — map IR ports → Byrd ports.** Confirm which IR field is which port (`α`=start, `β`=resume, `ω`=fail, `γ`=succeed) and how `flat_drive`/`EMIT_PAIR_FILL` realize them. Read ARCH-x86.md §Flat-BB-ABI + §Boxes-are-stackless, `emit_bb.c` FILL machinery, the flattener (`x86_uid`/`g_flat_node_id` in `x86_asm.h`). Deliverable: a written port→field table; no code change.
- [ ] **BOPT-1 — transitive goto-chaining.** New `src/opt/branchopt.c` (or a `src/lower/` post-pass) over the lowered graph: for each port edge whose target BB is body-empty except `jmp X`, redirect the edge to X. Union-find / pointer-chase with a **cycle guard** — `to.code` back-edges and generator self-loops must NOT collapse into an infinite redirect. This is the "branches to branches → one jump" core.
- [ ] **BOPT-2 — dead-BB + fall-through elimination.** After rechaining: drop BBs with no predecessors; merge `A: … jmp B` into `B` when A is B's sole predecessor and B can follow A (eliminate `goto next`). Layout reorder (paper's "reordering the code") = lay succeed-chains out as straight-line fall-through so the common path has no taken branch.
- [ ] **BOPT-3 — copy propagation.** Collapse the `t<node>.value ← child.value` temp-forwarding chains the four-port templates emit (uminus/plus/relop each allocate a temp that often just forwards a child's value; cf. paper Fig 2 propagating `to1.I` directly instead of materializing `to1.value`). Propagate so the consumer reads the source temp; dead-temp elimination follows.
- [ ] **BOPT-gate.** ⛔ pure CFG/copy rewriting — semantics MUST be preserved. `test_crosscheck_snobol4.sh` result byte-identical (PASS=171 FAIL=84, fail SET unchanged, every program's stdout byte-identical). Both-medium (mode-3 == mode-4). Regenerate + commit ALL benchmark/feature/demo `.s` (they WILL change — fewer jumps; that IS the win). A/B: emitted-jump-count + wall-ms delta on arith_loop, op_dispatch, fibonacci (executed-branch reduction → a speedup that helps all 16 benchmarks, unlike a single-primitive inline).

### PEEP — Peephole / common-subexpression (post-emitter, "maybe after the emitter")
Window pass over the emitter's pre-flatten op-list (PREFERRED — structured, not regex-on-text) or the text `.s` (fallback). Cleans residue BOPT cannot see at IR level.
- [ ] **PEEP-0 — peephole window.** Kill redundant `mov A,rax; mov rax,A` spill/restore round-trips (e.g. the relop operand spill in `bb_call_relop_inline_str`), `mov reg,reg` identities, dead stores (`mov X,_; mov X,_`), and `lea`/`mov` of an already-live value. Operate on the structured op-list before flatten.
- [ ] **PEEP-1 — sub-expression elimination (CSE).** Within a BB, reuse an already-computed value instead of recomputing it (same global loaded twice; same index recomputed). This is the "SUB-EXPRESSION OPTIMIZER" half; complements BOPT-3.
- [ ] **PEEP-gate.** Crosscheck result byte-identical; both-medium; regenerate `.s`; A/B timing.

### CFOLD — General constant folding (ALL expressions, not just patterns)
Today only invariant PATTERNS fold (PB-FZ). Extend folding to every expression kind.
- [ ] **CFOLD-0 — literal-expression fold in lower (or a fold pass feeding BOPT).** Fold compile-time-literal arithmetic (`2 + 3 → 5`), literal relops used as predicates (`LT(5,10)` → always-succeed null `""`; `GE(2,9)` → always-fail — which lets BOPT delete the dead arm), literal string concat (`'a' 'b' → 'ab'`), `SIZE('abc') → 3`.
- [ ] **CFOLD-1 — wire into BOPT.** A folded always-true/false relop becomes an unconditional edge → BOPT prunes the dead branch; fewer ops reach the emitter (smaller `.s`, fewer jumps).
- [ ] **CFOLD-gate.** ⛔ correctness: fold ONLY when operands are literals AND the op is side-effect-free AND the result matches SPITBOL semantics (integer width/overflow, number↔string coercion, the null-string-identity rule from the `str_concat_d` fix). Crosscheck byte-identical; each folded form verified against `sbl -b`.

**Prereq reads:** the uploaded paper (four-port templates §4; example + optimization §5 / Figs 1–2); ARCH-x86.md §Flat-BB-ABI + §Boxes-are-stackless; ARCH-SNOBOL4.md §Native pattern architecture; `src/lower/lower_snobol4.c` (LOWER output = the graph BOPT consumes); `src/emitter/emit_bb.c` (FILL / port machinery + flattener); `src/emitter/BB_templates/x86_asm.h` (label/flatten primitives). **PLAN.md staging:** BOPT is a NEW pipeline stage between LOWER and EMITTER — register it in the driver between those two phases (the first genuinely new stage in the pipeline; PEEP hangs off the emitter, CFOLD off lower).


## ▶ PRIORITY RUNG (session 24): PERF-CALL — inline the per-primitive runtime calls

**Mandate.** The three-way comparison proves SCRIP mode-4 loses to SPITBOL on 14/16 benchmarks because every SNOBOL primitive (var get/set, operator dispatch, string concat, function call, subscript, EVAL) is a runtime PLT call. SPITBOL inlines/threads them. This ladder inlines the most-executed primitives, ranked by MEASURED cost. Each sub-rung is gated on `test_crosscheck_snobol4.sh` staying byte-identical to HEAD (zero regressions) plus a timing delta on its target benchmark(s). Sub-rungs are independent; do DCR first (biggest cluster: func_call 14×, fibonacci 23×, roman 23×).

### DCR — Direct Call protocol (the function-call cluster)

**Diagnosis (assembly + source traced, session 24).** Per call to a trivial `INC(N)`, `rt_call_named_proc` (`src/runtime/rt/rt.c:375`) runs the SNOBOL dynamic-scoping protocol as **~7 GST hash ops BY STRING NAME**: `rt_name_save_push` does `NV_GET_fn("N")`+`NV_SET_fn("N")` to save/install the param, same pair for the return-var `INC`, then `NV_GET_fn("INC")` to fetch the return, then `rt_name_restore` does two `NV_SET_fn` restores. With one proc the `strcmp` scan over `g_rt_gen_procs` is nanoseconds — the per-call HASHING is the 14×. SPITBOL saves through compile-time-known slots, no hashing.

**Fix.** Cache `name_ptr → {rt_proc_t*, ret_cell, param_cells[]}` (each cell from `NV_PTR_fn`, **proven stable**: GST entries are GC-malloc'd + chained, never moved; GVA cells live in static `__gva`; gva_register is preamble-only so cells are fixed before any call). Do save/restore via direct `*cell` ops — zero hashing after warmup. The `name` pointer is a stable `.rodata` address per call site, so a direct-mapped cache keyed by `(uintptr_t)name` is sound (collisions just re-resolve).

**⛔ HAZARD — `NV_GET_fn`/`NV_SET_fn` are NOT pure cell access (traced `core.c`).** They branch on special names with side effects a raw `*cell` would SKIP: INPUT reads stdin, OUTPUT/TERMINAL write, I/O-channel-associated vars write to files, keyword vars set `kw_*`, protected-pattern vars error. Guards (all three MANDATORY):
- (a) **Keyword fallback (free):** `NV_PTR_fn` already returns NULL for INPUT/OUTPUT/STLIMIT/ANCHOR/TRIM/… — so a NULL cell means "don't cache, fall back to by-name `NV_GET/SET`." Correct automatically.
- (b) **Protected-pattern bypass:** skip the whole fast path when `g_protected_pat_vars_armed` (`core.c:6`, cheap global).
- (c) **I/O-association disable-hook:** add a global `g_call_fastpath_off` flipped permanently true at the I/O-association sites (`core.c` ~788/2725/2753, where `_io_chan[i].varname =` is set). Once any var is I/O-associated, all calls use the correct slow path. Rare — every benchmark + most corpus never associate I/O, so the fast path applies broadly.

#### STEPS
- [x] **DCR-1 — cell-cache + cell-based save/restore (RUNTIME-ONLY, no codegen change).** ✅ DONE (session 24, SCRIP `4b663b0`). A/B: func_call 17174ms→6582ms (2.61×), fibonacci 4821ms→2324ms (2.07×).
- [x] **DCR-2a — proc-lookup cache (runtime-only).** ✅ DONE (session 25, SCRIP `3b30fbb`). Behavior-neutral; O(1) for multi-proc.
- [x] **DCR-2-cells — memoize param/return cells on rt_proc_t (runtime-only).** ✅ DONE (session 25, SCRIP `d9dc34b`). A/B func_call: ~6588ms→~6435ms (~2.5%). Cumulative: 17174ms→6435ms (~2.67×). In `rt.c`: change the `g_name_save` entry to carry `(DESCR_t *cell /*or NULL*/, const char *name, DESCR_t old)`. Add the `name_ptr→cell` cache (direct-mapped, ~2048, key compare; miss → `NV_PTR_fn`, fill). `rt_name_save_push`: resolve cell via cache; if non-NULL save `(cell, *cell)` + `*cell = arg`; else fall back to `NV_GET/SET` by name (store NULL cell + name). `rt_name_restore`: per entry `*cell = old` when cell non-NULL else `NV_SET_fn(name, old)`. In `rt_call_named_proc` (and `_sl`): return fetch via cached cell when non-NULL else `NV_GET_fn(name)`; add guards (b)+(c) to gate the cache. Both call entries benefit. **Gate:** `make libscrip_rt` (so rebuild only — this is runtime); `test_crosscheck_snobol4.sh` byte-identical to HEAD (the keyword/I/O programs in the corpus PROVE the guards); A/B `func_call`/`fibonacci` timing vs HEAD.
- [x] **DCR-2 — codegen-side resolution (drop the by-name call entirely).** ✅ DONE (session 28, 2026-06-25, SCRIP `a5ed5be`). `src/driver/scrip.c` only — activates dormant scaffolding: `proc_collect_reset/graph` over main+proc bodies, emit `__proc_names`/`__proc` bss table, `rt_proc_table_fill` in preamble, `g_proc_direct_active=1`. Call sites: `lea rdi,name; call rt_call_named_proc` → `mov rdi,[rip+__proc+k*8]; call rt_call_proc_direct`. Fallback by-name kept for `$FN`/OPSYN/runtime-DEFINE. Gate: crosscheck PASS=171 FAIL=84, fail set byte-identical (zero regressions). Both-medium clean. A/B: func_call 5208→5138ms (~1.3%), fibonacci 2040→1987ms (~2.6%) — honest small win; DCR-1/2a/2-cells already made by-name O(1); residual cost is save/restore protocol.
- [x] **DCR-3 — gate + re-ground.** ✅ DONE (session 27, 2026-06-25). `.s` confirmed byte-identical (DCR was runtime-only, idempotent regen, corpus tree clean). Re-run via `scripts/test_3way_snobol4.sh` (SCRIP/SPITBOL, wall-clock ratio). Func-call rows updated in the THREE-WAY block above: func_call 14.2×→6.65×, func_call_overhead 13.3×→6.62×, fibonacci 23.1×→10.50× (DCR ~2.2× win confirmed at benchmark level); roman 22.7×→21.80× (unchanged — pattern/REPLACE-bound, not call-bound). 14/14 result-bearing benchmarks MATCH. **The whole DCR ladder (DCR-1/2a/2-cells) is now CLOSED and re-grounded.**

### AXS — Array subscript inline (table_access 8.8×, mixed_workload 5.7×)
`subscript_get`/`subscript_set` are per-access PLT calls. For `ARRAY(...)` (NOT hashed `TABLE`) with an integer index, inline a bounds-check + direct `[base + idx*16]` load/store, exactly the shape GVA uses for scalars. Tables stay on the runtime hash path.
- [x] **AXS-0** — detect array-with-int-index access in `lower_snobol4.c` (distinct from table). ✅ DONE (session 26) — IR_IDX operand box already handles this shape; no lower-side change needed.
- [x] **AXS-1** — emit inline bounds-check + `[base+idx*16]` arm. ✅ DONE (session 26, SCRIP `e3d0ff8`). Read + write. Encoder fix (`x86_load_indexed8` REX.B/X/R) bundled.
- [x] **AXS-2** — gate: crosscheck byte-identical; out-of-range semantics match (delegate to slow path — correct by construction). ✅ DONE (session 26). PASS=171 FAIL=84, fail set byte-identical. Both-medium clean. **Note:** `table_access`/`mixed_workload` use TABLE not ARRAY — AXS DT_A guard correctly bypasses; those benchmarks need a separate table-probe inline rung.

### SAB — String self-append capacity (string_concat 8.8×, string_manip 11.3×)
`S = S X` calls `str_concat_d` → `libgc` malloc + O(n) copy every iteration = O(n²) copies + an allocation storm (the source comment confirms O(n²)). SPITBOL is O(n²) too but its per-op alloc/copy is far cheaper. Detect the compile-time self-append pattern `V = V <expr>` and back `V` with a string-builder cell tracking `(ptr,len,cap)` that doubles `cap` → amortized O(1) append (no malloc/copy while `len<cap`).
- [ ] **SAB-0** — detect self-append `V = V <expr>` in `lower_snobol4.c`.
- [ ] **SAB-1** — string-builder runtime type + emit arm.
- [ ] **SAB-2** — **⛔ correctness: preserve copy-on-assign value semantics** — any read/alias of `V` must see an immutable snapshot (else SPITBOL's value semantics break); handle `SIZE`, aliasing, GC rooting.
- [ ] **SAB-3** — gate: crosscheck byte-identical; A/B string_concat/string_manip timing.

### EVR — EVAL/CODE arena reclaim (eval_dynamic 176×)
Already diagnosed in the EVAL-OOM block below: per-EVAL re-parse + re-lower + a bump-allocated mprotect-RX code page that is NEVER reclaimed (self 1.5s vs 87.7s wall = sealing/syscall time). **CORRECTION:** eval_dynamic COMPLETES correctly in this sandbox (87.7s) — it is NOT an OOM here; the bench-script CRASH was the 30s timeout. Fix = the parked RECLAIM variant: snapshot `bb_pool` top before `eval_build_chain`, run, restore (mprotect RX→RW back), free the per-call AST/IR. Cross-ref the EVAL-OOM diagnosis. Lowest priority (one benchmark).

---



**GVA-0/1/2 LANDED (SCRIP `ef7594d`). GVA-3a/3b + str_concat_d fix LANDED (SCRIP `9222a33`). GVA-3a string-coercion fix LANDED (SCRIP `1d2c976`, rebased onto `fe2d39e`).**

Session 16 (2026-06-24): arith_loop ~870ms → ~141ms (~6×). Hot loop now branch-only: LT(N,1000000) emits cmp+jcc (GVA-3b), N=N+1 emits mov [rbx+k*16+8]+add (GVA-3a). Zero crosscheck regressions (87 fails, byte-identical set to pristine).

**CORRECTION (session 17, 2026-06-24): the session-16 line above originally claimed "Bench OK=14/16, FAIL=0" — that was WRONG. GVA-3a shipped a correctness regression: its inline-arith direct cell read `mov rax,[rbx+k*16+8]` takes the raw value field assuming DT_I, but for a DT_S/DT_R operand that field is a char*/double-bits, not an integer. So `T<IDX> = WORD + 0` (WORD a pattern capture) stored a pointer, and mixed_workload returned nondeterministic garbage instead of 550 — real state was OK=13 FAIL=1 CRASH=2. The pre-GVA path used rt_gvar_get_int (which coerces via strtoll); GVA-3a dropped that. Integer counters are always DT_I so arith_loop/fibonacci were unaffected, which is why it slipped through. The relop (GVA-3b) was already correct — it calls rt_gvar_get_int for named globals. FIX (`bb_binop_gvar_arith.cpp`, arms 2 both-names + 3 one-name): inline type-tag guard — `cmp edx,DT_I` on the cell type, fast raw read when DT_I (hot path stays call-free, branch predicts), else fall to rt_gvar_get_int slow path that coerces. arith_loop/fibonacci timings unchanged; bench now GENUINELY OK=14/16, FAIL=0, CRASH=2 (the 2 = pre-existing EVAL OOM eval_dynamic/eval_fixed, unchanged). Crosscheck still 87 fails byte-identical (zero regressions, verified before and after rebasing onto PB-NBODIES-32). All 16 benchmark + feature + demo .s artifacts regenerated side-by-side (idempotent on the combined tree).**

**EVAL OOM — DIAGNOSED (session 17, not fixed; deep + deferred).** eval_fixed (1M× `EVAL('X + 1')`) and eval_dynamic (1M× `EVAL('N + ' N)`) are the only two non-green benches (bench OK=14/16; these are CRASH, OOM-killed, NOT timeout — eval_fixed dies at ~3s). EVAL itself is CORRECT (small counts return the right value); the failure is a ~75KB/call memory leak (measured: 80MB@1k iters → 2.2GB@30k → OOM@150k, linear). Path: `EVAL_fn` (pattern_match.c) → `CONVE_fn` → `eval_build_chain` (runtime_eval.c) runs EVERY call: it re-parses the string, `lower_snobol4`s it, and `gvar_flat_chain_build` emits fresh machine code into the BB pool. The BB pool (`src/machine/bb_pool.c`) is a fixed mmap arena with a BUMP allocator (`bb_alloc` advances `pool_top`, never reclaims; `bb_pool_init` early-returns once `pool_base` set). So every EVAL bump-allocates new sealed (mprotect RX) code pages that are never freed; the per-call AST/IR (`ast_stmt_new`/`strdup`/lowered graph `g`) also leak. FIX OPTIONS for next session: (a) string→DT_E-chain CACHE — builds once, reuses; fixes eval_fixed fully (and makes it fast) but NOT eval_dynamic (1M distinct strings → cache grows + still bump-allocates per new string); (b) RECLAIM per run — snapshot `pool_top` before `eval_build_chain`, run the chain, restore `pool_top` (needs mprotect RX→RW back before reuse) + free AST/IR — fixes BOTH but is the deeper change (watch: chain must not be referenced after reset; GC interactions). Note the new cross-repo DIRECTIVE (`.github` `d26f002a`): BB-local collections use dynamic realloc-2x (cap-bumps retired) — a cache added here must follow that.

**str_concat_d correctness fix (SCRIP `9222a33`):** SPITBOL null-string-identity: `"" N` preserves N's type. Pristine returned STRING after `LT(N,5) N`; oracle expects INTEGER. GVA-3a removed the accidental `strtoll` mask that hid the bug. Fixed: `IS_NULL_fn` early-return in `str_concat_d`.

**▶ NEXT MOVE: PB-FZ** (constant-fold invariant patterns — see PRIORITY RUNG below). Then GVA-4 (indirect `$X` fast path via rbp-based GST hash index). Alternatively OPSINGLE or REC-COV — Lon decides.

---

## ▶ PRIORITY RUNG: PB-FZ — ALWAYS constant-fold invariant patterns (Lon pivot, 2026-06-24)

**PIVOT (Lon):** NO command-line switch between constant-folding and build-from-scratch. ALWAYS freeze every invariant pattern subtree at COMPILE time. `bb_pat_build.cpp` survives ONLY as the STITCH path for the case where an INVARIANT and a structurally-VARIANT pattern are combined. This promotes ARCH-SNOBOL4.md's "ALL-INVARIANT BLOB FREEZE" optimization to the ONLY path and deletes the baseline instance-wiring.

**VARIANCE TAXONOMY (the trigger is STRUCTURAL variance, not operand variance):**
- INVARIANT (→ FREEZE to one sealed `bb_box_fn` blob): literal-operand primitives (`POS(0)`, `SPAN('0-9')`, `LEN(3)`, `"abc"`), invariant combinators (SEQ/ALT/ARBNO/`.`/`$` of invariants), and `*E` (deferred-eval box has FIXED code → its graph is static; `ARBNO(*var)` is INVARIANT). **CORRECTION to ARCH-SNOBOL4.md: it lumps `*E` with the structural variants — wrong; `*E` is a fixed box doing a dynamic sub-call, so it FREEZES.**
- OPERAND-variant (→ FREEZE structure, box reads operand LATE from a slot; NO build, NO stitch): `POS(X)`, `SPAN(cvar)`, `LEN(N)`. `POS(0)` and `POS(X)` are the SAME `BB_MATCH_POS` unary matcher fed by different operand-source boxes (baked-immediate vs `[ζ+off]`/`[rbx+k·16]` load); the operand-source is polymorphic across same-arg-type matchers (one int-source feeds POS/RPOS/LEN/TAB/RTAB; one string-source feeds SPAN/BREAK/BREAKX/ANY/NOTANY). So `POS(START_LINE) SPAN(CHARS) RPOS(FINISH_LINE)` freezes WHOLE to one blob, late operand reads, ZERO runtime stitch. **GUARDRAIL:** late read is sound ONLY for IMMEDIATE matches (construct+match same statement); a STORED operand-variant pattern must SNAPSHOT operands into per-instance slots at construction (else post-construction mutation diverges from SPITBOL, which freezes operand values at the `P = …` assignment).
- STRUCTURAL-variant (→ the ONLY case needing `bb_pat_build` STITCH): a pattern-valued variable used as a sub-pattern (`var_pattern`, no `*`), `$NAME` indirect resolving to a pattern, a function call returning a pattern. These splice a runtime box-graph into the enclosing combinator.

**THE STITCH SET IS CLOSED** (SPITBOL pattern algebra — manual Ch.6 "Pattern operations" + ARBNO + immediate-assign). Exactly five combinators, so exactly these stitch boxes, and ONLY when an operand is structurally variant:
1. `STITCH_SEQ` — Subsequent (concatenation `P Q`), n-ary (assoc-flatten).
2. `STITCH_ALT` — Alternate (alternation `P | Q`), n-ary.
3. ARBNO-stitch — `ARBNO(P)` loop wrapper (variant body; `ARBNO(*P)` freezes).
4. CAPTURE-stitch `.` — conditional assignment `P . NAME` (capture-on-overall-success wrapper).
5. CAPTURE-stitch `$` — immediate assignment `P $ NAME` (capture-on-submatch wrapper).
Precedence (manual): `.`/`$` > blank(SEQ) > `|`(ALT) — fixes the stitch-tree shape. `@NAME`, `*E`, and all primitive functions are LEAVES, never combinators.

**BENCHMARK INVENTORY (verified this session — build clean, bench OK=15 FAIL=0 CRASH=1, only eval_dynamic = known throughput timeout). All three pattern benchmarks are FULLY INVARIANT → the STITCH boxes are NOT exercised by the bench corpus (they are for the wider crosscheck corpus). The bench is a pure FREEZE exercise, split immediate-vs-stored:**
- **roman** (immediate: `N RPOS(1) LEN(1).T =` and `'…' T BREAK(',').T`): ALREADY inline-frozen — emits `IR_MATCH_RPOS`/`LEN`/`CAPTURE` boxes inline; bare `T` is `IR_MATCH_DEFER` (dynamic fetch, correct). **DONE — no work.** Result-sensitive, passes .ref.
- **string_pattern** (stored: `PAT = BREAK(',').WORD ','`): built ONCE via per-shape fused runtime builder `bb_build_break_cap_lit_blob` (`src/runtime/rt/bb_pat_build.cpp:88`), matched 500k× via DEFER. Correct (result-sensitive, passes .ref). FZ replaces the fused builder with a frozen blob.
- **pattern_bt** (stored: `PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd').W`): **stored ALT-pattern build is UNIMPLEMENTED in mode-4** — pattern literals are ABSENT from the `.s`, PAT is a no-op stub. "OK" is a FALSE PASS: result is the loop counter `N`, and a null PAT matches the null string every iteration → 500000 regardless. FZ IMPLEMENTS it. (Add a result-sensitive check — output `W` — so the freeze is actually validated.)

**SEAM (verified):** stored pattern `PAT = <invariant>` lowers (`src/lower/lower_snobol4.c`) to `IR_PATTERN_CAT` + `pat_via_dtp`; `src/emitter/BB_templates/bb_pattern_cat.cpp` emits a C-call to the per-shape `bb_build_break_cap_lit_blob`. Per-shape fused builders don't scale (no `alt4_span_cap` builder ⇒ pattern_bt stub). **`IR_REF_INVARIANT` is ALREADY a reserved opcode (`src/contracts/IR.h:174`, "REFINV" in `prove_lower.c`) but UNWIRED in the emitter — it exists for exactly this.** The immediate matchers (`bb_match_*()` dispatched in `src/emitter/emit_core.c`) ARE the frozen boxes to reuse. **FZ = redirect the existing immediate-matcher emission into a standalone sealed blob under a label + store its head as a `DT_P` via `IR_REF_INVARIANT`, replacing the `pat_via_dtp` build-call.** Match site keeps its DEFER fetch (FZ-2/3); inlining the sealed head to skip per-match DEFER is the FZ-5 perf step.

### STEPS
- [x] **FZ-2 — `IR_REF_INVARIANT` store + DEFER fetch.** ✅ LANDED (session 20, SCRIP `c3b6a83`). `PAT = BREAK(',') . W ','` lowers to a sealed matcher blob + `IR_REF_INVARIANT` storing the head as DT_P (no `bb_build_break_cap_lit_blob`). Gate MET: mode-3 AND mode-4 output == `string_pattern.ref`; builder call absent from `string_pattern.s`. See prior START-HERE header for the six pieces.
- [x] **FZ-3 — ALT-of-literals freeze.** ✅ LANDED (session 21, SCRIP `973df9e`). `PAT = ('aaa'|'bbb'|'ccc'|'ddd') SPAN('abcd').W` constant-folds to one sealed `IR_REF_INVARIANT` blob; pattern_bt mode-3 AND mode-4 output `result: 500000` + `W: ccccddddaaaa` (W hand-computed; oracle confirm pending token). Added `sno_freeze_pat_ir()` — general recursive kids-channel matcher-graph builder for invariant patterns — replacing the narrow FZ-2 per-shape constructor. Key insight: `flat_drive_cat/alt` read arms from the **kids channel** (`bb_match_kids_state_t`), not the γ/ω spine; must build in kids-channel form. `sno_has_pat()` guard prevents value-concat expressions (e.g. `42 ' items'`) from entering the freeze path. pattern_bt.sno+.ref updated (W output added). `string_pattern.s` byte-identical. Bench OK=15 FAIL=0 CRASH=1 (eval_dynamic OOM pre-existing). Crosscheck PASS=171 FAIL=84 vs pristine 168/87 — zero new failures, +3 fixed (132/133/134_pat_fence_eps_recur also freeze via the new general path).
- [x] **FZ-4 — retire dead fused builders.** Remove now-unused per-shape builders in `bb_pat_build.cpp` (keep ONLY the structural-variance STITCH path). Gate: `test_crosscheck_snobol4.sh` byte-identical (zero regressions).
- [ ] **FZ-5 (follow-on perf) — match-site direct reference.** When the compiler proves PAT holds a once-assigned invariant pattern (assigned, never reassigned), inline the sealed head at the match site and skip the per-match `rt_defer_get_pat_fn` (runs 500k× in string_pattern/pattern_bt) — the actual hot-loop win, turning stored into roman's inlined form.

**Prereq reads (PLAN.md step 7 — touches per-box state):** ARCH-SNOBOL4.md §"Native pattern architecture" + §"ALL-INVARIANT BLOB FREEZE", ARCH-x86.md §Boxes-are-stackless + §Flat-BB-ABI, `src/emitter/bb_regs.h`, `src/emitter/BB_templates/bb_pattern_cat.cpp`, `src/runtime/rt/bb_pat_build.cpp`, `src/emitter/emit_core.c` (matcher dispatch).

---

**Build:** `apt-get install -y libgc-dev && make && make libscrip_rt`. Oracle: `git clone …/x64 /home/claude/x64; sbl -b`. Tri-probe: `scrip --compile p.sno > p.s; gcc -no-pie -x assembler p.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs `sbl -b`. Bench/crosscheck gates: `scripts/test_bench_snobol4_modes.sh`, `scripts/test_crosscheck_snobol4.sh`.

---

## Prior context (session 13 — literal-subject native scan, now history)

roman's scan 2 (`'0,1I,…,9IX,' T BREAK(',') . T`) declined native because `flat_drive_scan_stmt` gated on a *named* subject only. Four-layer fix landed: `emit_bb.c` gate accepts `op_scan_subj_lit`; `flat_drive_scan_native` attaches an `IR_LIT_S` operand to `IR_SUBJECT`; `bb_subject.cpp` lit arm fixed (`mov→lea`, `bb_subj_litlbl()`, `rt_subject_load_lit`); `pattern_match.c` `rt_subject_load_lit` sets ζ-slot AND `Σ`/`Σlen`. Roman's earlier `MCXI` (recursive re-descent) symptom was resolved by the turn-1 local-var fix above. Roman reproduction:
```snobol4
    &TRIM = 1
    DEFINE('ROMAN(N)T')                   :(RE)
ROMAN N RPOS(1) LEN(1) . T =              :F(RETURN)
    '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' T BREAK(',') . T :F(FRETURN)
    ROMAN = REPLACE(ROMAN(N), 'IVXLCDM', 'XLCDM**') T :S(RETURN)F(FRETURN)
RE  R = ROMAN('176')
    OUTPUT = 'RESULT=' R
END
```

**Design note (carried):** the `walk_bb_node` preamble clobbering `op_a_sval` from `operands[0]` is the ambient-`g_emit` class flagged in session 12; the general cure (port-field reset / FILL-only / debug gen-counter assert) is still unbuilt.

---

# Open rungs (not yet started)

## PERF-GVA — Global Variable Array: eliminate GST hash lookup on hot path

### Naming

| Abbrev | Full name | What it is | Register | Access |
|--------|-----------|------------|----------|--------|
| **GST** | Global Symbol Table | Hash dictionary: name→DESCR_t. Runtime/dynamic. Currently called NV. | `rbp` (BBREG_HASH) | by name string |
| **GVA** | Global Variable Array | Flat `DESCR_t[N]` for compile-time-known globals. Static `.data`. | `rbx` (BBREG_BASE) | by integer index k |
| **LVA** | Local Variable Array | Per-call-frame `DESCR_t` slots for procedure locals/params. Already exists as ζ-frame. | `r12` (BBREG_ZETA) | by byte offset |

**The problem:** every global variable read is `call NV_GET_fn@PLT` (hash walk + string compare). Every write is `call rt_gvar_assign_*@PLT`. For `arith_loop` at 1M iterations that is ~14 PLT+hash calls per iteration. SPITBOL bakes variable addresses into code at compile time — zero calls per access.

**The fix:** at compile time, assign each program-global variable name an integer index k. Emit a flat `DESCR_t __gva[N]` array in the program's `.data` section. At preamble, call `gva_register(names, __gva, N)` which (a) populates `__gva[k]` = current GST value (null for new vars), (b) sets `GST_t.is_gva=1` and `GST_t.cell=&__gva[k]` so existing `NV_GET_fn`/`NV_SET_fn` paths transparently read/write through the GVA cell, (c) returns `__gva` base. Preamble stores that base in `rbx`. Templates then access `[rbx + k*16]` — two `mov` instructions, zero calls.

**GC safety:** `__gva` lives in `.data` (static storage, not GC heap). `DESCR_t.s` string payloads are still GC-managed heap pointers written into the cell — BDW scans `.data` as a root, so strings in GVA cells are reachable and not collected. The cell address itself never moves.

**GST forwarding invariant:** after `gva_register`, every GVA-backed variable in GST has `is_gva=1` and `cell→__gva[k]`. `NV_GET_fn` returns `*cell`; `NV_SET_fn` writes `*cell`. Dynamic paths (indirect refs `$X`, EVAL) that resolve to a GVA-backed name still work correctly at the cost of one extra pointer dereference — no correctness regression.

---

### GVA-0 — Infrastructure: GST forwarding flag + gva_register runtime  ✅ DONE (local, unpushed)

**GVA-0a — `GST_t` (rename from `NV_t`) gains `is_gva` + `cell`:**
In `src/runtime/core/core.c` (binary; edit via patch or sed):
```c
typedef struct _VarEntry {
    char              *name;
    DESCR_t            val;    /* live value when is_gva==0 */
    DESCR_t           *cell;   /* points into __gva when is_gva==1 */
    int                is_gva;
    struct _VarEntry  *next;
} GST_t;   /* was NV_t */
```
`NV_GET_fn`: `if (e->is_gva) return *e->cell;` before returning `e->val`.
`NV_SET_fn`: `if (e->is_gva) { *e->cell = val; return val; }` before writing `e->val`.
`NV_PTR_fn`: `if (e->is_gva) return e->cell;`
**Rename `NV_t` → `GST_t` throughout `core.c`.** Public API names `NV_GET_fn`/`NV_SET_fn`/`NV_PTR_fn`/`NV_CLEAR_fn` keep their names for now (rename is a separate rung, not required for correctness).

**GVA-0b — `gva_register` in `src/runtime/rt/rt.c` + `rt.h`:**
```c
/* Register N compile-time globals. Returns cells base (stored in rbx by preamble). */
DESCR_t *gva_register(const char **names, DESCR_t *cells, int n);
```
Implementation: for k in 0..n-1: find-or-create GST entry for `names[k]`; copy existing `e->val` into `cells[k]`; set `e->is_gva=1`, `e->cell=&cells[k]`.
**Exclude** names where `NV_PTR_fn` returns NULL (INPUT, OUTPUT, PUNCH, keyword `&`-prefix vars) — these stay GST-only, no GVA slot.

**GVA-0c — emitter: GVA name collection in `emit_bb.c`:**
New pass before any box emission: walk all IR nodes, collect distinct `op_sval` names for `IR_VAR`, `IR_ASSIGN`, `IR_BINOP_GVAR_ARITH`, `IR_BINOP_GVAR_ARITH_SLOT` that are non-keyword, non-`&`-prefix, non-INPUT/OUTPUT. Assign each a slot index k (stored in a new `int g_gva_slots[]` parallel to a `const char *g_gva_names[]` table, max 1024 entries). Store per-name GVA index in a lookup table `gva_index_of(name) → k` used by all templates.

**GVA-0d — emitter: emit `__gva` array + preamble call in `xa_flat.cpp` / `xa_prologue.cpp`:**
In TEXT mode, after `.section .data` banner:
```asm
  .align 16
__gva:
  .space N*16, 0
__gva_names:
  .quad .Lgvan0, .Lgvan1, ...   /* N name pointers */
  .section .rodata
.Lgvan0: .string "VARNAME0"
...
  .section .text
```
In preamble (before first user BB):
```asm
  lea rdi, [rip + __gva_names]
  lea rsi, [rip + __gva]
  mov edx, N
  call gva_register@PLT
  mov rbx, rax              /* rbx = __gva base for lifetime of program */
```
Also `push rbx` / `pop rbx` around any call that may clobber it per ABI — but since `rbx` is callee-saved in SysV ABI, callees preserve it automatically. No push/pop needed around `call` instructions in templates.

**GVA-0e — update `bb_regs.h` comment block** to document `rbx=GVA base` and `rbp=GST hash base` with new names.

**Gate GVA-0:** compile `arith_loop.sno` → verify `__gva` in `.s`; link and run → output identical to oracle; `gva_register` called once; `NV_GET_fn("N")` returns value through `e->cell`.

---

### GVA-1 — Direct load: IR_VAR global read → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** In `bb_var.cpp` (and `bb_var_global.cpp` if separate), when `gva_index_of(_.op_sval) >= 0` (name has a GVA slot), replace `call NV_GET_fn` with inline load.

Add to `emit_globals.h` `sm_emit_t`:
```c
int op_gva_k;   /* GVA slot index for this node, -1 if GST-only */
```
Populated in `emit_bb.c` `walk_bb_node` preamble alongside existing `op_sval` fill.

Add to `x86_asm.h`:
```c
inline const char *GVAQ(int k, int hi) {
    static char b[8][40]; static int i; i=(i+1)&7;
    snprintf(b[i],40,"qword ptr [rbx + %d]", k*16+hi);
    return b[i];
}
```

`bb_var.cpp` new first arm (checked before existing `g_gvar_flat_chain` arm):
```cpp
(_.op_gva_k >= 0) ?
  x86("comment", "IR_VAR gva")
+ x86("label",   _.lbl_α)
+ x86("mov",     "rax", GVAQ(_.op_gva_k, 0))
+ x86("mov",     "rdx", GVAQ(_.op_gva_k, 8))
+ x86("mov",     FRQ(_.op_off),     "rax")
+ x86("mov",     FRQ(_.op_off + 8), "rdx")
+ x86("jmp",     "γ")
+ x86("def",     "β")
+ x86("jmp",     "ω") :
```

**Gate GVA-1:** `grep "call NV_GET_fn" arith_loop.s` == 0; full `test_crosscheck_snobol4.sh` oracle-identical.

---

### GVA-2 — Direct store: IR_ASSIGN global write → `[rbx + k*16]`  ✅ DONE (local, unpushed)

**Mandate:** Replace `call rt_gvar_assign_int` / `call rt_gvar_assign_descr` / `call rt_gvar_assign_var` / `call rt_gvar_assign_lit_i` / `call rt_gvar_assign_lit_s` with inline stores when the destination name has a GVA slot.

Integer literal store (`N = 5`), DT_I=6:
```asm
mov dword ptr [rbx + k*16],     6
mov dword ptr [rbx + k*16 + 4], 0
mov qword ptr [rbx + k*16 + 8], IMM
```

DESCR_t from frame slot (result already split lo=rax hi=rdx):
```asm
mov qword ptr [rbx + k*16],     rax
mov qword ptr [rbx + k*16 + 8], rdx
```

Steps:
- GVA-2a: `bb_gvar_assign.cpp` — integer and descr paths
- GVA-2b: `bb_gvar_assign_lit_i.cpp`, `bb_gvar_assign_lit_s.cpp`
- GVA-2c: `bb_gvar_assign_var.cpp` — var→var copy through GVA
- GVA-2d: `bb_gvar_assign_call.cpp`, `bb_gvar_assign_concat.cpp`

**Gate GVA-2:** `grep "call rt_gvar_assign" arith_loop.s` == 0; crosscheck suite green.

---

### GVA-3 — Fused integer arithmetic + relop  ✅ DONE (session 16, SCRIP `9222a33`)

**Mandate:** `N = N + 1` where both operands and destination are GVA-backed integer vars emits zero calls. Detect in `bb_binop_gvar_arith.cpp` when `op_parts` names all have GVA slots.

`N = N + 1` (add, immediate RHS):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]   /* N.i */
add rax, 1
mov dword ptr [rbx + kN*16],     6      /* DT_I */
mov dword ptr [rbx + kN*16 + 4], 0
mov qword ptr [rbx + kN*16 + 8], rax
```

`LT(N, 1000000) N` (relop predicate, GVA int vs immediate):
```asm
mov rax, qword ptr [rbx + kN*16 + 8]
cmp rax, 1000000
jge β_port
/* success fall-through: value = N.i already in rax */
```

Steps:
- GVA-3a: `bb_binop_gvar_arith.cpp` fused path for GVA+GVA and GVA+IMM
- GVA-3b: new `bb_gvar_relop.cpp` for `LT`/`GT`/`LE`/`GE`/`EQ`/`NE` on GVA int operands — emits `cmp` + conditional jump, replaces `call rt_call_arr@PLT`

**Gate GVA-3:** `arith_loop.s` hot loop body (label `LOOP` to next label) contains zero `call` instructions; `fibonacci.s` same; timing run shows ≥5× improvement over baseline on `arith_loop`.

---

### GVA-4 — rbp GST hash path for runtime indirect refs (optimization, not correctness)

**Mandate:** `$X` where X's runtime string value names a GVA-backed variable: use `rbp`-based hash index to skip full GST walk.

New runtime helper `gva_lookup_by_name(const char *name) → int k` (returns -1 if not GVA-backed). Emitted in `.data` beside `__gva`:
```asm
__gst_idx:
  .space GVA_HASH_SIZE*4, 0xff   /* uint32_t[GVA_HASH_SIZE], sentinel=0xffffffff */
```
Preamble fills `__gst_idx` with (hash(name) → k) entries after `gva_register`.

Template for indirect read, fast path:
```asm
/* name string ptr in rdi */
call gva_hash_probe@PLT     /* (rbp, rdi) → k or -1 */
test eax, eax
js   .gst_slow
mov  rdx, qword ptr [rbx + rax*16 + 8]
mov  eax, dword ptr [rbx + rax*16]
jmp  γ
.gst_slow:
call NV_GET_fn@PLT
```

This is an optimization rung — correctness is guaranteed by GVA-0b's `is_gva` forwarding regardless of this rung. Do GVA-4 only after GVA-0 through GVA-3 are green and benchmarked.

**Gate GVA-4:** indirect-ref crosscheck programs (`014_assign_indirect_dollar`, `015_assign_indirect_var`) oracle-identical; `arith_loop` timing unchanged (no indirect refs in that benchmark).

---

### Expected performance impact

| Rung | Calls eliminated per `arith_loop` iteration | Estimated speedup |
|------|---------------------------------------------|-------------------|
| GVA-1 | 2 × `NV_GET_fn` | ~2× |
| GVA-2 | 2 × `rt_gvar_assign_*` | +1.5× |
| GVA-3 | `binop_apply` + both assign calls | closes to ~10× baseline |
| GVA-4 | partial `NV_GET_fn` for indirect | marginal on arith |

---

## OPSINGLE — delete operand_aux, one channel only

**Mandate:** exactly ONE operand channel: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`).

Writers still aux-only (add `ir_operand_push`, keep aux until readers flipped): `lower_snobol4.c` CALL args, `lower_icon.c:134,137,315`, `lower_raku.c:210`, `lower_pascal.c:147,162,177,340`, `lower_prolog.c:140`.

Readers to flip (`bb_operand_aux_get` → `nd->operands[]`): `BB_templates/bb_call.cpp:98`; `emit_bb.c:350,411,438,846,1072,1492,1818,2489,2957(DELETE bridge shim),3035,3240,3335,3398,3458`; `driver/scrip.c:102,245,1931`; `contracts/scrip_ir.c:355`.

Delete last (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all call sites.

**Gate:** `grep operand_aux src/` (excl attic) == 0 AND all language gates green.

## REC-COV — community-recognized corpora

**Mandate:** extend coverage into community corpora. PB-GREEN stays session-first.

Inventory (pass-rates unmeasured — RC-0's job):
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/snobol4/demo/` — 18 `.sno`

Steps: RC-0 honest runner + oracle-gen refs + triage table → RC-1 gimpel → RC-2 demo → RC-3 promote counts to hard floors → RC-4 re-ground "10×" claim.

---

## BBGC — slide-compaction garbage collector for the BB code arena  ⬇ LOW PRIORITY / EXPLORATORY (Lon 2026-06-24)

**Status: design-only spike. Do NOT start ahead of GVA-4 / OPSINGLE / REC-COV.** Picked up only when the `bb_pool` bump arena's lack of compaction becomes a real ceiling (the EVAL leak fix landed a LIFO watermark — `bb_pool_mark`/`bb_pool_release` — and a 2MB retention budget, which BOUNDS but does not COMPACT: cached/retained chains pin non-top regions, so pure-LIFO leaves holes a long-running EVAL/CODE-heavy program eventually exhausts).

**Vision (Lon):** treat `bb_pool` as a GC heap of *code*. When it fills, mark live BB blobs, sweep the unreferenced, and **slide the survivors down to compact**, re-stitching ONLY the four ports (α β γ ω) and touching nothing else inside a blob body.

**Why this is viable — relocatability taxonomy (grounded in `x86_asm.h` binary encoder + `bb_regs.h`, verified 2026-06-24).** Setting the 4 ports aside, here is everything baked into a sealed blob and its behavior under a slide:
1. **Register-relative state** (`[r12+off]` ζ, `rbx` GVA, `rbp` GST, `r13/r14/r15` Σ/δ/Δ) — encodes NO code/data address → **zero fixup**. This register-centric ABI is the whole reason compaction is tractable.
2. **RIP-relative to adjacent sealed RO** (`lea reg,[rip+disp32]` to interned name/lit bytes) — disp32 = target−rip_next → **invariant IFF the RO tail moves with its blob as one indivisible unit**. ⇒ relocation unit = blob + adjacent RO, never split.
3. **Immediate data constants** (`movabs reg,<int|float-bits>`) — values, not addresses → **position-independent**.
4. **Runtime-function calls** — binary encoder ALREADY emits `movabs rax,&fn ; call rax` (`x86_asm.h:196`, abs addr) NOT `call rel32`. The runtime never moves, so the absolute target is invariant under caller movement → **zero fixup**. (Ports, by contrast, are `0xE8 rel32` / `XK_PORT` — relative, the one thing that breaks.)
5. **The four ports** — `call/jmp rel32` between boxes → break on move → **re-stitch (recompute rel32)**. Exactly the scoped work; nothing else in the body needs it.
6. **⚠ THE REAL HAZARD — stored pointers to blob ENTRY points held OUTSIDE the pool.** A moving collector must fix these: (a) the EVAL cache (`runtime_eval.c` `g_eval_cache[].fn`); (b) DT_C/DT_E descriptors on the SNOBOL heap (`code()`/`CONVE_fn` stash `d.ptr=blob_addr` into first-class values a user var can hold — `:<C>` direct-goto, `CONVERT(s,'CODE')`, retained `*expr`); (c) the runtime label→code map; (d) **live return addresses on the native C stack** pointing INTO a blob if GC can fire while a BB frame is active (the precise-moving-GC-of-JIT-code problem).

**Two design decisions that make "touch nothing else" literally true:**
- **Entry-table handle indirection.** Hand out a stable handle (index into a per-pool entry-table the collector owns) instead of a raw blob-entry address; cache/descriptors/direct-gotos store the handle, the table holds the live address, relocation updates ONLY the table. Bounds category-6 fixups to one table.
- **Compact only at a safepoint with no active BB frame** (between top-level statements / after an EVAL/CODE returns — easy to guarantee since those run synchronously to completion and the pool is touched only between statements). Eliminates category-6(d) entirely, avoiding return-address rewriting.

### STEPS
- [ ] **BBGC-0 — measure + baseline.** Add `bb_pool` occupancy/hole stats; build an EVAL/CODE-heavy stress program that pins retained chains AND keeps allocating (forces holes the 2MB-budget LIFO can't reclaim). Confirm the failure mode (NULL from `bb_alloc` while total live < pool) and document why LIFO watermark alone is insufficient. NO behavior change.
- [ ] **BBGC-1 — root enumerator.** Enumerate all live BB entry-point references: `g_eval_cache`, DT_C/DT_E descriptors reachable from GST (BDW already roots the SNOBOL heap — walk code-typed cells), the runtime label→code map, direct-goto code values. Output a `(holder, entry_addr)` root list. Read-only; no relocation yet.
- [ ] **BBGC-2 — entry-table handle indirection.** Replace raw entry addresses handed to cache/descriptors/direct-goto with handles into a collector-owned per-pool entry-table; the table holds the current address. Floor: EVAL/CODE crosscheck byte-identical (one extra deref on the slow path only).
- [ ] **BBGC-3 — mark.** From roots, mark reachable blobs; follow inter-blob refs (ports + entry-table) transitively. Verify mark set ⊇ everything the stress program calls.
- [ ] **BBGC-4 — safepoint discipline.** Define + assert the compact safepoint (no active BB frame on the C stack). Confirm EVAL/CODE return BEFORE any compaction trigger. (Closes category-6(d).)
- [ ] **BBGC-5 — sweep + slide-compact.** Slide live blobs (blob + adjacent RO, one unit) down to remove holes; update the entry-table; re-stitch the 4 ports per moved box (recompute rel32). Add a verifier that asserts NO code-internal absolute pointer exists outside the covered categories (1/3/4 must need nothing). 
- [ ] **BBGC-6 — trigger.** On `bb_alloc` overflow, run compaction (at a safepoint) and retry instead of returning NULL.
- [ ] **BBGC-7 — gate.** EVAL-heavy stress (e.g. 1M distinct EVALs) runs with BOUNDED pool, output == SPITBOL oracle, compaction firing ≥N times; full `test_crosscheck_snobol4.sh` byte-identical (zero regressions); bench unaffected.

**Prereq reads when picked up (per PLAN.md step 7 — this touches per-box state + relocation):** `ARCH-x86.md` §Boxes-are-stackless + §Flat-BB-ABI, `ARCH-ICON.md` §register-contract, `REGISTER-LAYOUT.md`, `src/emitter/bb_regs.h`, `src/emitter/XA_templates/xa_flat.cpp`, `src/machine/bb_pool.c` (the new `bb_pool_mark`/`bb_pool_release`).

---

# Completed / superseded (summary only)

Sessions 1–12 built the full SNOBOL4-BB ladder bottom-up:
- **DDS-0** (session ~8): deleted all `bb_*_proto[]` byte arrays, `DTP_t` head, `rt_dtp_run`. Ground-zero rebuild.
- **TR-1** (`7d6a9c9`): `sno_leaf_buildable` extended for `TT_CAPT_COND_ASGN`; capture patterns routed to builder, not orphaned.
- **TR-LEN** (`75f97e5`): `bb_build_len_blob` allocates `IR_MATCH_LEN` (matcher), not `IR_PATTERN_LEN` (builder). `r1`→`W=CD`.
- **Rename** (`2e5a5a3`): `IR_PAT_*` → `IR_MATCH_*` throughout.
- **TR-BREAK** (`15bda9d`): `bb_pattern_break.cpp` + `bb_build_break_blob`. First ζ-slot box; proves frame mechanism end-to-end.
- **TR-CAPTURE** (`1e962ed`): `bb_build_break_capture_blob`; `PAT=BREAK(',') . W`→`W=alpha`.
- **TR-CAT** (`5d6e7cd`): `bb_build_break_cap_lit_blob`; `PAT=BREAK(',') . W ','`→`W=alpha`.
- **splice fix** (`9ea1251`): `bb_scan_splice_empty` stripped of stale port scaffolding; string_pattern + mixed_workload GREEN.
- **literal-subject scan** (`f3f7cdb`, session 13): gate + `IR_LIT_S` operand + `bb_subj_litlbl` + `rt_subject_load_lit`. Last bomb removed.

Architecture constants (do not re-derive):
- `walk_bb_node` preamble (emit_core.c:328–333) overwrites `op_sval`/`op_ival`/`op_a_sval`/etc. from node+operands every emission — never rely on ambient values set before `FILL`.
- `rt_cap_assign_cursor` reads global `Σ` (set by `rt_subject_load_nv` and now `rt_subject_load_lit`).
- `flat_drive_cat_arms` reads the kids channel (`IR_EXEC(cat).counter`), NOT `operands[]`; a CAT with `nkids==0` emits empty.
- `bb_build_flat` entry CAT with nkids==0 emits empty — kids channel is mandatory.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.

---
## SESSION ADDENDUM — 2026-06-27 (RUNG 1: unary-minus — bugs #1 + #2 FIXED, 411 CLOSED; PIVOT to STATIC-FIRST ladder-walking)

### Canonical scripts (USE THESE — stop hand-running make/apt/git-clone)
- Setup (once/session): `bash scripts/install_system_packages.sh` (apt deps incl libgc-dev); then `bash scripts/build_scrip.sh` (builds ./scrip) and `make libscrip_rt` (out/libscrip_rt.so).
- Oracle (ONLY when escalating to the monitor — do NOT clone by default): `git clone https://github.com/snobol4ever/x64 /home/claude/x64` -> /home/claude/x64/bin/sbl (invoke with `-bf`).
- Monitor (ESCALATION ONLY — reach for it after a static stab has failed): `PARTICIPANTS="spl scr" MONITOR_TIMEOUT=15 bash scripts/test_monitor_3way_sync_step_auto.sh <file.sno>` (spl=oracle, scr=SCRIP; binary IPC over ready/go FIFOs; runs .sno UNMODIFIED). ALWAYS wrap: `timeout 90 ... | head -120`. Only ctrl.out (divergence table) persists.
- Crosscheck (regression gate — the `.ref`-based FAST path, run for EVERY fix; NOT the monitor): `bash scripts/test_crosscheck_snobol4.sh` (~136s; CORPUS=/home/claude/corpus). Redirect to file, grep the PASS=/FAIL= summary. **Verified clean-tree baseline (2026-06-27): --run PASS=152 FAIL=109; --compile PASS=172 FAIL=83 SKIP=6; DIVERGE=22.** (The older 150/111 · 170/85 numbers were stale.)
- Artifact regen (after ANY codegen fix): `bash scripts/util_regen_{benchmark,feature,demo}_s_artifacts.sh`; commit only changed .s.
- Session-close verify: `bash scripts/handoff_status.sh` (auto-discovers ALL repos under /home/claude with origin; prints CHAT SESSION COMPLETE only when every repo is clean+pushed). TWO repos to push every session: SCRIP (code) + .github (this doc).

### Monitor event-type capture — RESOLVED (2026-06-27 session 2)
All FOUR sync-step event types now fire AND agree byte-for-byte end-to-end under the `spl scr` monitor (--run): LABEL, VALUE, CALL (fn-enter), RETURN (fn-return). Five comment-free repros reach END with exit 0 (full agreement): /tmp/{mdiv2,counter,concat,v_types,calls}.sno (calls.sno exercises nested OUTER→INNER calls + a real FRETURN). Fixes landed (all monitor instrumentation emit-time/runtime gated on g_monitor_bin; .s byte-identical with MONITOR_BIN unset; crosscheck unchanged --run 150/111, --compile 170/85/6, DIVERGE 22 — zero regression):
- VALUE was the broken type. The MON-RE-4 taps had been LOST from rt_gvar_assign_{str,int,descr,var} (only rt_indirect_assign_var still had one). RESTORED a tap after NV_SET_fn in all four (rt.c) + added one to rt_gvar_assign_concat_parts (pattern_match.c:~571) so normal concat-assign `MSG=A B` emits VALUE. Central skip-guard added to mon_emit_value_bin (core.c): `if (!name||!name[0]||name[0]=='_'||name[0]=='&'||NV_PTR_fn(name)==NULL) return;` — NV_PTR_fn returns NULL for exactly INPUT/OUTPUT/keyword sys-vars, so OUTPUT/INPUT stores correctly emit NO VALUE (matches SPITBOL) while every normal scalar/var/concat store does. NOTE: only --run was needed (it routes ALL stores through rt_gvar_assign_*); --compile uses inline [rbx+k*16] GVA stores that bypass the runtime — NOT instrumented (the monitor runs --run). If a future rung monitors native --compile output, the GVA inline-store templates (bb_gvar_assign.cpp `_.op_gva_k>=0` arms, bb_binop_gvar_arith.cpp) still need emit-time VALUE taps.
- FRETURN was mislabeled as RETURN: kw_rtntype was never written (init "" → comm_return always emitted the "RETURN" default). FIXED mon_emit_return_bin (rt.c) to set kw_rtntype = IS_FAIL_fn(retval) ? "FRETURN" : "RETURN" (save/emit/restore around comm_return). The caller's `result = IS_FAIL_fn(fret) ? FAILDESCR : ...` makes IS_FAIL detection exact (a successful RETURN never yields FAILDESCR).
- Bare-goto / trailing-empty LABEL gap: SCRIP coalesces statements whose only content is a transfer (`:(L)`) or an empty trailing label into γ-edges, so trailing stnos that lead to program-end had no work-box and were dropped (SPITBOL emits a LABEL on EVERY statement entry). FIXED in the flattener (codegen_gvar_flat_chain_body, emit_bb.c): per-box ntail_extra[]/ntail_cnt[] capture the γ-chain trailing stnos when γ resolves to a non-real end node; in the emit loop, when g_monitor_bin && that box's γ targets lbl_γ, its γ is redirected to a tiny per-box tap-trampoline that emits the trailing LABEL taps then `jmp lbl_γ`. Per-EDGE (NOT a shared join) so it is correct for branchy programs where two gotos hit the same end-label — CRITICAL: the trampoline does NOT use the emitted_stnos dedup (each runtime edge takes exactly one path, so the same trailing stno legitimately appears on multiple edges; deduping dropped the LABEL on the not-emitted-first path — this was the calls.sno WAS_S/WAS_F→MEND bug).
- END-statement LABEL: SPITBOL emits a final LABEL for the END line (stno = highest source stno + 1) before terminating; SCRIP never lowered END. FIXED: g_mon_max_stno (core.c) tracks the highest stno passed to emit_mon_label_tap (bb_succeed.cpp) at emit time; mon_at_exit (core.c) now emits LABEL(g_mon_max_stno+1) with a proper ack handshake (inline writev, NOT mon_emit_label_bin — avoids the exit-on-'S' re-entrancy during atexit) immediately before the END record. Works for --run (emit + run share the process); harmless for --compile (guard g_mon_max_stno>0).
Separate monitor nit (STILL OPEN, not addressed): SPITBOL counts comment lines toward stno; SCRIP does not (spl = scr+1 on commented programs). Use comment-free repros until normalized.

### 411_arith_unary — monitor bracket
DIFFER(-5, 0-5) at stmt 1: spl FAILs the DIFFER (-5 == 0-5) -> jumps e001 -> PASS; scr SUCCEEDs the DIFFER -> falls through -> FAIL.

BUG #1 — FIXED (SCRIP commit 7d86f7b). lower_snobol4.c lower_expr binop branch had NO arity guard; unary TT_MNS/TT_PLS (expr_unary, n=1) share the binop token type, so it read a non-existent c[1] and lowered -5 as "5 - null" = 5. Fix: `if (lc_is_binop(t->t) && t->n >= 2)` diverts unary to the IR_UNOP branch. Verified: -5 now negates in codegen (mov 5; neg); full crosscheck unchanged (no regression). Observably neutral until BUG #2 lands.

BUG #2 — FIXED ✅ (2026-06-27, static-first, ONE stab — uncommitted in working tree pending session-close push). After #1, `-5` computes correctly but a unop feeding a CALL ARG was emitted as `IR_UNOP_GVAR_SLOT` (bb_unop_gvar_slot.cpp) writing a BARE 8-byte int at `[slot+0]`, while `marshal_call_arg`'s producer-box path (bb_call.cpp) copied `[slot+0]/[slot+8]` as a 16-byte descriptor -> arg0 = `{value, GARBAGE}` vs the binary path's correct `{DT_I=6, value}`. (DESCR_t = {DTYPE_t v @+0, value @+8}; DT_I=6.) The `.s` showed it directly: arg0 `{-5, garbage}`, arg1 `{6,-5}` -> DIFFER saw them differ -> wrong success. **Fix landed = Option (a)** (mirror how binary arith already works): (1) `emit_bb.c gvar_drive_call_arg_slots` — exclude `IR_UNOP` (TT_MNS/TT_PLS) from slot pre-computation (parallel to the existing binary-arith exclusion), so it falls through to inline marshaling; (2) `bb_call.cpp marshal_call_arg` — added an inline-unop arm (after the inline-binop arm) that materializes the operand via `arith_opnd_a`, `neg` for TT_MNS, and boxes `{6, rax}` (plus `#include "ast.h"`). **Assertion 002** (`DIFFER(+'4', 4)`): `+'4'` was marshaled as a bare `LIT_S {DT_S,"4"}` (unary plus dropped) -> string "4" ≠ integer 4 -> wrong. Per the SPITBOL manual (unary +/- coerce a string operand to a number; leading sign must be followed by ≥1 digit; null/blank -> integer 0), the inline-unop arm was extended to **compile-time coerce a numeric string literal** to `{6, ±value}`. Real-form strings (`'4.5'`) deliberately fall through — float follow-up. **VERIFIED:** `411_arith_unary` prints `PASS 411_arith_unary (2/2)` in BOTH `--run` and `--compile`->bin, matching `.ref`. **Regression gate (set-level diff, clean vs fix tree, BOTH modes):** 411 moves FAIL->PASS in m3 AND m4; **zero regressions** in either; DIVERGE flat at 22 (clean 152/172 -> fix 153/173). 411 is CLOSED.

### RUNG 1 arithmetic cluster — DONE ✅ (2026-06-27, static-first)
410/411/412/413 all PASS both modes. Set-diff vs clean tree: **+4 m3, +4 m4, zero regressions, DIVERGE flat 22** (clean 152/172 -> 156/176). All fixes live in `bb_call.cpp marshal_call_arg` (the call-arg value-producing path that the assign-form boxes never covered) + the `emit_bb.c` call-arg pre-compute exclusion:
- **411 unary -/+**: exclude `IR_UNOP(TT_MNS/TT_PLS)` from pre-compute; inline-unop arm materializes operand, `neg` for TT_MNS, boxes `{6,rax}`. String operand coerced to int (`lits_int_val`, SNOBOL rule); `IR_LIT_F` operand folded to `{7,±bits}`.
- **410 POW + string coerce**: exclude `BINOP_POW`; inline arm calls `POWER_fn`->boxes `{rax,rdx}`. Binary string-operand coercion via `lits_int_val` in `arith_opnd_a/b` + `arith_kind_ok` (covers 410/006-009).
- **412/413 real + mixed**: float/mixed-LITERAL arith arm routes through `rt_num_arith(a,b,op)` (runtime does real/promotion), boxes `{rax,rdx}`. Covers real +,-,*,/, real**int, int+real promotion.
- Float follow-up (NOT a rung yet): only LITERAL float operands are routed; a real-valued VAR in call-arg arithmetic (e.g. `RV ** 2`) still takes the int-only inline path. Surfaces only if a future test needs it.

### Next RUNG 1 supply (static-first each)
m4 FAIL set still holds: pattern tests (052-152 `pat_*` — the DEMO-PAT/GEM surface, heavier), 091-095 array/table/data, 100_roman_numeral, 210-213 indirect, 310-312 concat, 1010-1017 func, 1110-1115 array/table, 811/W0x/word*. Lower-risk next stabs: **310-312 concat, 210-213 indirect, 091-095 array/table**.

**310 concat — DIAGNOSED, NOT yet fixed (2026-06-27, probe only).** `DIFFER('a' 'b', 'ab')` fails assert 001. Statement concat works (`OUTPUT = 'a' 'b'` -> `ab`); the gap is CALL-ARG-only. In the `.s`, the sibling literal `'ab'` (arg1) is correctly pre-computed + producer-boxed from a slot, but `'a' 'b'` (arg0) emits NO compute box and is marshaled via `marshal_call_arg`'s **varslot FALLBACK** (`bb_call.cpp` ~478-487): `voff = bb_varslot(IR_LIT(lf).sval)` treats the string `"ab"` as a VARIABLE NAME and copies garbage from that stale slot. So either (a) `'a' 'b'` folds to `IR_LIT_S "ab"` but the LIT_S marshal arm is bypassed (arg falls through to the var-fallback), or (b) the `BINOP_CONCAT` is dropped because it is neither excluded-then-inline-marshaled (like arith) nor producer-boxed (like its sibling). NEXT SESSION: confirm arg0's actual IR op via the arg subgraph (top-spine `--dump-ir` hides it); fix = make the marshal fallback box an `IR_LIT_S` as `{DT_S, strptr}` (NOT `bb_varslot`), and/or add `BINOP_CONCAT` to the `gvar_drive_call_arg_slots` pre-compute path so a concat arg is boxed like any other producer. This is the same call-arg-marshal family as the arith cluster but in the string/concat dimension.

---

## ▶ RUNG: IDX-SET-SLOTS — array/table store+read `A<k> = v` / `OUTPUT = A<k>` ✅ CLOSED (Claude 2026-06-27, local-unpushed)

**LANDED (verified): `--run` 159→164, `--compile` 179→184; DIVERGE 22 (unchanged); ZERO regressions (precise set-diff). Fixed: 091, 092, 093, 1111, 1113.** Smokes SNOBOL4 7/7, Icon 12/12, Prolog 5/5 (shared-file edits cross-checked). Three distinct root causes, all found static-first (IR dump + `.s` + one probe), no monitor:

1. **Literal operands got no frame slot** (`A<1>=7` bombed `bb_idx_set: needs base/key/value operand slots`). `walk_bb_flat`'s LIT slot-allocation (emit_bb.c ~2850) is gated on `g_descr_flat_chain`, which is **0** in the `codegen_flat_build` path (NOT the `descr_flat_chain_build_text` path — the scrip.c:2986 `dfc=1` wrapper covers only the latter). Fix: `flat_drive_idx_set` forces `g_descr_flat_chain=1` ONLY around literal-kind operand walks (new `idx_operand_is_lit` predicate, emit_bb.c) so a literal key/value gets a real 16-byte DESCR slot, while IR_VAR operands stay on their existing path (forcing it globally broke the base IR_VAR's slot — confirmed by probe).
2. **TT_QLIT + TT_FLIT lowering gap** (091 `A<1>='first'`, 093 `T['name']='Alice'`, 1110 `a<2>=4.5` all dropped to no-ops). Extended FOUR lowering arms in `lower_snobol4.c`: the store arm (~1092), the read-RHS arm (~1002), and `lower_expr`'s TT_IDX arm (~144, for subscript-as-call-arg) all now accept key/value ∈ {ILIT,VAR,QLIT,FLIT} building IR_LIT_S / IR_LIT_F boxes. The read template `bb_idx_get.cpp` got a new IR_LIT_S key arm (skip the DT_A array fast path — string keys only index tables — build `{DT_S, sealed-ptr}` via op_name2/op_parts_lbl[1], call subscript_get).
3. **Bare-int arith value wrote a malformed DESCR** (092 `A<I>=I*I` segfaulted). A non-descr GVA arith binop (`arith_emits_descr`==0) writes a raw i64 to slot+0, but IR_IDX_SET expects a full `{DT_I,val}` DESCR; copying slot+0/slot+8 put the int in the tag word → malformed element → segfault on later read. Fix: driver computes `op_num_real = (val_box->op != IR_BINOP || arith_emits_descr(val_box))`; `bb_idx_set.cpp` promotes a bare-int slot to `{DT_I,[slot+0]}` in BOTH the fast-path element write and the slow-path subscript_set call (IF(_.op_num_real) guards).

**BONUS (same call-arg work): narrowed the TT_FNC orphan-punt** (lower_snobol4.c ~1119). Previously ANY function-call statement with a TT_IDX arg was punted to an orphan (ignoring :S/:F). Now only UNSUPPORTED shapes (TT_INDIRECT/TT_OPSYN, or a TT_IDX that is not base=VAR key∈{ILIT,VAR,QLIT}) orphan; a supported subscript arg flows through normal call lowering (the marshal path already handles IR_IDX args via lower_expr). This is what made `DIFFER(a<n>, v)` work and unblocked 1111/1113.

**Files:** `src/lower/lower_snobol4.c`, `src/emitter/emit_bb.c`, `src/emitter/BB_templates/bb_idx_get.cpp`, `src/emitter/BB_templates/bb_idx_set.cpp`.

---

## ▶ RUNG: SIZE-INT ✅ CLOSED (Claude 2026-06-27, local-unpushed) — SIZE of an integer

**LANDED: 811_size FIXED (both modes 3/3). `--run` 164→165, `--compile` 184→185, DIVERGE 22, zero regressions.** `SIZE(12)` returned 0 instead of 2. Root: the `SIZE` builtin (`by_name_dispatch.c` try_call_builtin_by_name ~2701, AND the rt.c rt_size_d sink) special-cased `IS_INT_fn||IS_REAL_fn → INTVAL(0)`. SPITBOL coerces a number to its decimal string and counts chars (`SIZE(12)`=2, `SIZE(345)`=3). Fix: integer arm now `strlen(VARVAL_fn(v))`; real arm left at 0 (no test coverage — conservative). Only the by_name_dispatch.c arm needed editing for the tested call path (`IR_CALL SIZE` → marshaled args → `rt_call_arr` → `try_call_builtin_by_name`); rt_size_d's int fallback (line 669) was already correct via VARVAL_fn.

**⛔ CRITICAL BUILD LESSON (cost ~30min this session — record so it is never repeated): a runtime file compiled into BOTH `scrip` (the static object link) AND `libscrip_rt.so` requires rebuilding BOTH targets after an edit.** `--run` (mode-3, in-process) calls the copy STATICALLY LINKED INTO `scrip`; `--compile`+link (mode-4) calls the `.so`. Editing `by_name_dispatch.c` / `rt.c` / `core.c` / any RT_PIC_SRCS file and running ONLY `make libscrip_rt` leaves `--run` executing the STALE embedded copy — the fix silently does nothing in mode-3 and a probe placed in the source "never fires". ALWAYS `make -j4 scrip && make libscrip_rt` after a runtime-file edit. (This is the runtime-file analogue of the EMIT-DECOUPLE dual-list trap.)

---

## ▶ RUNG: INDIRECT-REF — `$` indirect reference as rvalue (210/211/212/213, diagnosed 2026-06-27 Claude, NOT started)

**ROOT CAUSE (RUN+AST-confirmed, all 4 share it).** The `$` indirect-reference operator works only as an assignment TARGET (`lower_snobol4.c` ~1069 `$'lit'=v`≡`lit=v`, ~1073 `$V='lit'`, ~1079 `$V=W`). As an **rvalue it is completely unsupported**: (1) `lower_expr` and the call-arg lowerer `sno_arg_lower` (`lower_snobol4.c:104`, reached via `sno_arg_block`/`lc_arg_block`/`lc_call_argblks` at ~108/111) have **NO `TT_INDIRECT` arm**; (2) worse, the TT_FNC orphan trigger at **`lower_snobol4.c:1141`** marks ANY call with a `TT_INDIRECT` arg as `complex_arg` → the WHOLE call is orphaned (no γ/ω, `:S`/`:F` ignored, chains to nxt). So `DIFFER($'bal', bal) :F(e001)` never runs and falls straight to the FAIL line. (All four stop at their first `$`-rvalue assertion: 210/001, 211/002, 212/001, 213/001.)

**AST SHAPES (from `--dump-ast`).** `$'bal'`=`(INDIRECT (QLIT "bal"))` · `$.bal`=`(INDIRECT (NAME (VAR bal)))` · `$.a<2>`=`(INDIRECT (NAME (IDX (VAR a)(ILIT 2))))` · `$X`=`(INDIRECT (VAR X))` · `$NM` (NM=.A, holds DT_N)=`(INDIRECT (VAR NM))`.

**THE KEY SIMPLIFICATION — name-deref cancels at compile time.** `$(NAME(lvalue))` ≡ that lvalue (the `.` makes a name, `$` immediately derefs it back): so `$.bal`≡`bal`≡`IR_VAR('bal')` and `$.a<2>`≡`a<2>`≡`IR_IDX(a,2)`. And `$(QLIT s)`≡`IR_VAR(s)`. These are PURE COMPILE-TIME rewrites needing no runtime helper and **flip 210 + 211 + 212** (211/001 `$'qq'='x'` already passes via the assign-target path; 211/002 `$'_no_such_var_'` rvalue→`IR_VAR('_no_such_var_')`→null→`DIFFER(null)` fails→`:F` taken).

**THE RUNTIME RESIDUE — `$VAR` (213 only).** `$(VAR x)` can NOT be resolved at compile time — x's *value* is the name (a string like `'A'`, OR a DT_N nameval as in `NM=.A`). Needs a runtime indirect-read helper: fetch x's value; if string→`NV_GET(string)`, if DT_N→follow the name to its cell. 213 also needs `$X = 99` as an **lvalue with a runtime (VAR) name** (the existing assign arms only handle `$'lit'`/`$V='lit'`/`$V=W` where the target name is literal or the value side is simple — `$X=99` where X holds the name needs the runtime-name assign path; check whether ~1079 already covers it). 213/005 NRETURN-of-`.var` is a separate concern (verify independently).

**FIX PLAN (do compile-time trio first — clean, no runtime change):**
1. **Add `TT_INDIRECT` arm to `sno_arg_lower` (~104) AND `lower_expr` (~131 switch):** `$(QLIT s)`→`IR_VAR(s)`; `$(NAME(VAR v))`→`IR_VAR(v)`; `$(NAME(IDX(VAR,key)))`→`IR_IDX(base,key)` (reuse the IR_IDX operand shape from the `case TT_IDX` arm ~144); `$(VAR x)`→leave for step 3 (runtime).
2. **Narrow the orphan trigger `lower_snobol4.c:1141`:** only orphan when the indirect is the UNSUPPORTED shape — i.e. drop `a->t == TT_INDIRECT` from the blanket `complex_arg` set for the compile-time shapes (QLIT / NAME-wrapped), so a supported indirect arg flows through normal call lowering (which now marshals it via the step-1 `sno_arg_lower` arm). Gate carefully — this is the same orphan-narrowing pattern the TT_IDX call-arg work used (HANDOFF note "narrowed the TT_FNC orphan-punt"). Verify no regression in programs that currently rely on indirect-arg orphaning.
3. **(213, separate sub-step) runtime `$VAR` rvalue + lvalue:** add the runtime indirect-read helper (string-name → NV_GET; DT_N → deref) and an IR rvalue box for `$(VAR x)`; confirm/extend the `$X=value` runtime-name assign arm. Likely its own session.

**Gate:** per program `--run` AND `--compile` match `.ref`; crosscheck fail set ⊆ HEAD (esp. watch the orphan-narrowing for regressions); both-medium; `.s` regen (lowering changed). Compile-time trio (210/211/212) is the clean first landing; 213 is the runtime follow-on.

**Prereq reads:** `lower_snobol4.c` ~104 (`sno_arg_lower`), ~131-158 (`lower_expr` switch + the `TT_IDX` arm to mirror), ~1069-1082 (the existing indirect-ASSIGN arms), ~1137-1145 (the TT_FNC orphan trigger). Runtime indirect helpers: grep `NV_GET_fn`/`IR_INDIRECT_ASSIGN_*`/DT_N handling in `rt.c`/`core.c`. SPITBOL Ch.7 "indirect reference".

---

## ▶ RUNG: ARRAY-SEMANTICS — remaining array/table/DATA cluster (diagnosed 2026-06-27, NOT started)

**SUPPLY + first-failing-assertion (RUN-confirmed):**
- **1110_array_1d** — ✅ CLOSED (Claude 2026-06-27, local-unpushed). 9/9 both modes; crosscheck `--run` 165→166, `--compile` 185→186, DIVERGE 22, zero regressions (fail set == baseline minus 1110, proven by `comm`). OOB-high/zero array refs now FAIL and are caught by `:F`. **Two-part fix as diagnosed:** (a) `lower_snobol4.c` `case TT_IDX` (bare-subject switch, was `return NULL`) now builds an `IR_IDX` wired `γ=γ_tgt`(success)/`ω=ω_tgt`(failure) for the supported shape (base=VAR, key∈{ILIT,VAR,QLIT}); unsupported shapes stay orphan. Because a goto-less stmt sets `ω_tgt=nxt` (caller line 1247, SPITBOL `-FAIL` semantics), a goto-less bare subscript still falls through to the next stmt whether OOB or not — no regression. (b) `bb_idx_get.cpp` slow path: `subscript_get` already returns `FAILDESCR`(`.v=DT_FAIL=99`) for `DT_A` OOB (via `array_get`), while `DT_T` miss returns `NULVCL`(DT_SNUL, success — tables never OOB). Added `cmp eax,DT_FAIL; je ω` after the slow-path `call subscript_get` (the diagnosis's "found/OOB out-flag" was unnecessary — the descriptor tag already carries the signal; `.v` is the first 4 bytes → `eax`, same as the existing `cmp eax,DT_A` fast-path guard). `je ω` is an established four-port idiom (bb_scan_any/bb_binop_relop). (001/002/008/009 PASS now — null-init, real store, string store all work.)
- **1112_array_multi** — stops at **003: custom lower bound** `d = ARRAY('-1:1,2'); d<-1,1> = 0`. 2D (`c<1,2>`) WORKS now (001/002 pass), but a NEGATIVE index / custom-lower-bound prototype does not. Multi-subscript `<i,j>` and `<i,j,k,l>` lowering + the bounds math for non-1 lower bounds.
- **1114_item** — stops at **001: `ITEM(aaa, 1) = 5`**. ITEM as an ASSIGNMENT TARGET (and ITEM read). ITEM is the programmatic-subscript builtin (equivalent to `<>`); needs a lowering that maps `ITEM(a, i...) = v` to the same IR_IDX_SET and `ITEM(a, i...)` to IR_IDX, plus N-ary subscript support (4D in the test).
- **1115_data_basic + 095_data_field_set** — ✅ CLOSED (Claude 2026-06-27, local-unpushed). Both 6/6 / full-ref both modes; crosscheck `--run` 166→168, `--compile` 186→188, DIVERGE 22, zero regressions (set-diff: only these two left the fail set). **Diagnosis was understated — the real bug:** field-accessor-as-assignment-target (`fld(obj) = value`, e.g. `val(a) = 'new'`) was *entirely* unimplemented — `lower_snobol4.c`'s has_eq block had no `TT_FNC`-subject arm, so it hit the `subj != VAR/KEYWORD → return NULL` guard and the whole assignment was DROPPED (silent no-op). (1115's assertion 004 `lson(b)=a` was a FALSE PASS: the set no-op'd but the verify `rson(lson(b))` failed on the null arg, which made DIFFER fail and took `:F` anyway; 006's direct reread returned the stale construction value, failing honestly.) **Fix (lowering only, no template/runtime change):** added a has_eq arm — `fld(obj) = value` (subj=TT_FNC, n==1, arg=VAR, value∈{ILIT,VAR,QLIT,FLIT}) lowers to `IR_IDX_SET(base=obj, key=LIT_S(fld-name), value)`, exactly mirroring the `a<'k'>=v` string-key write. `subscript_set`'s existing DT_DATA string-key arm (`pattern_match.c` ~229: scans `blk->fields[]`, writes `arr.u->fields[i]`) does the work; the accessor READ (`dat_field_get`) sees it because both touch the same `arr.u->fields[]`. Reused the whole IR_IDX_SET path → both-medium for free. Non-accessor `f(x)=v` (no valid SNOBOL4 meaning) → subscript_set on a non-DATA returns 0 = harmless no-op, no regression. (095 came along free — same construct.)

**Method:** static-first per program; the OOB-fail (1110) and ITEM (1114) are the two cleanest next stabs. Multi-dim/custom-bound (1112) and DATA-mutate (1115) are deeper. Gate per program: `--run` AND `--compile` match `.ref`; crosscheck fail set ⊆ HEAD; both-medium; `.s` regen if codegen changed.

**Prereq reads:** `bb_idx_get.cpp` / `bb_idx_set.cpp` (the read/store templates), `flat_drive_idx_get`/`flat_drive_idx_set` (emit_bb.c ~1671/1695), `lower_snobol4.c` ~144/1002/1092/1171 (the four IDX lowering sites), `aggregates.c` `subscript_get`/`subscript_set` (runtime array/table), ARCH-x86.md §Flat-BB-ABI.

---

## SESSION ADDENDUM — 2026-06-27 (RUNG 1: INDIRECT-REF compile-time trio 210/211/212 CLOSED)

**Crosscheck baseline entering this session (post prior session's local-unpushed landings now confirmed pushed):** `--run PASS=168 FAIL=93` · `--compile PASS=188 FAIL=67 SKIP=6` · `DIVERGE=22`.

**NOTE — 310/311/312 concat stale note:** the goal addendum "310 concat — diagnosed, not yet fixed" was stale. 310/311/312 pass clean in both modes at session open. One less item in the rung-1 supply.

### INDIRECT-REF compile-time trio — CLOSED ✅ (Sonnet 2026-06-27, SCRIP `63c666ba`)

**Programs:** 210_indirect_ref (2 assertions), 211_indirect_assign (2 assertions), 212_indirect_array (1 assertion). All PASS both `--run` and `--compile` vs `.ref`. **Gate:** `--run` 168→**171**, `--compile` 188→**191** (+3 each); DIVERGE 22→**22** (list byte-identical); **zero regressions** (precise m4 set-diff: only 210/211/212 leave the fail set; DIVERGE list unchanged rules out any m3-only regression). `.s` artifacts regenerated (3 feature tests updated; benchmark/demo unchanged — no affected programs).

**Root cause (both problems):**
1. **Orphan trigger** (`lower_snobol4.c:1141`): `TT_INDIRECT` unconditionally set `complex_arg=1` → the whole containing DIFFER call was orphaned (no γ/ω, `:S`/`:F` ignored, fell through regardless of result). So `DIFFER($'bal', bal) :F(e001)` never ran and never jumped.
2. **No rvalue arm for `TT_INDIRECT`** in `lower_expr`: `is_sno_unop` listed `TT_INDIRECT` so it would have routed to `IR_UNOP`, which has no indirect-semantics implementation; but the orphan trigger fired first so this was never reached.

**Fix (pure lowering, one file, 22 lines, no template/runtime change):**
- Added `sno_indirect_resolvable(a)` predicate: true for `$'lit'`, `$.var`, `$.arr<k>` (the three compile-time-cancellable shapes per SPITBOL Ch. 7 — *"alternate use of indirection and name operators cancel one another"*). False for `$VAR` (runtime, 213 — untouched).
- Added `lower_expr` arm (before `is_sno_unop`): `$'lit'`→`IR_VAR(lit)`, `$.var`→`IR_VAR(var)`, `$.arr<k>`→recurse `lower_expr(g)` (emits `IR_IDX` via the existing `case TT_IDX` arm).
- Narrowed orphan trigger: only `TT_OPSYN` and non-resolvable `TT_INDIRECT` orphan; resolvable shapes flow through `sno_call_channels` → `sno_arg_lower` → `lower_expr` → the new arm.

**Next rung-1 supply (static-first each):** 213 (runtime `$VAR` rvalue — needs runtime indirect-read helper; goal file has full diagnosis); array cluster: 1112 (multi-dim/custom-bounds `ARRAY('-1:1,2')`), 1114 (ITEM as assignment target); func cluster: 1010/1011/1013/1014 (recursion, redefine, NRETURN, FRETURN).
