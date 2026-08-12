# GOAL-SN4-HOME-WIRES — r10/r11 wires, two glue kinds, shim deletion (HOME seat; master = GOAL-SN4-HOME.md)

## ⛔ TOOLING FIRST (s42) — `bash /home/claude/SCRIP/scripts/install_system_packages.sh` BEFORE ANY RUNG.
One authority, idempotent, prints whether `gdb` is live. **`gdb` is MANDATORY** — RULES.md MONITOR-FIRST step (2) *is* a gdb breakpoint with a spin/ignore counter. ⛔ **Never hand-run `apt-get install gdb`:** it pulls Recommends `libc-dbg` against a stale container apt index and 404s on a package gdb does not need — **that trap cost RBP-EARN seven sessions (s33–s39)**, each re-concluding "no gdb in this container" and passing it on. The script does `apt-get update` first and passes `--no-install-recommends`. Runtime `rt_*` symbols live in `out/libscrip_rt.so`: use `set breakpoint pending on` — "Function not defined" is dynamic linking, not a broken gdb. **Any tool genuinely missing ⇒ ADD IT TO THAT SCRIPT in the same push; never work around it silently.** If a prior cursor in this file claims gdb is unavailable, that claim is VOID — re-test.


**CHARTER:** rΓ=r10 · rΩ=r11 product-wide (Lon s12 verbatim: *"remove the stupid PROC shim around patterns and use proper PASS-THRU glue using R10 and R11"*), exactly TWO glue kinds (ONE-SHOT · PASS-THRU; FRAMED IS NOT A GLUE KIND — s29), RBP never written by glue. **Mechanism authority = LADDER WREG + LADDER PT inside `GOAL-RBP-EARN.md` (absorbed by reference, corrections here supersede).** RTCC's wire half (veneer preservation) is owned HERE per the s14 arbitration: safe config = RTCC-ON **and** wire capture/restore, neither alone.

## RUNGS
- [x] **W-0 · CLAIM SWEEP — ✅ CLOSED s36c (Lon answered W-0b same day; all three decisions executed at SCRIP `wreg_claim_whitelist.txt` + `test_gate_wreg_claim_binary.sh`).**
  - **(a) PRODUCT-WIDE (Lon verbatim: "R10 and R11 are product wide")** → the 30 SN4-unreachable RTX occurrences are DEBT, not licensable — ruling written into the whitelist header itself so no future entry can smuggle an unreachability justification. Debt tracked at **W-8** below.
  - **(b) delegated ("all your choice")** → executed: `x86_asm.h` licensed with pinned `occ=23`, split 9 RTCC-veneer = class (3) · 13 register-name tables = **new explicit class (5) "infrastructure"** (added to the header rather than widening (3) past its stated meaning) · 1 DC-stub scratch = temporary (3) tagged **DIES-WITH-W-5** (re-review that pin when W-5 lands).
  - **(c) recommendation accepted** → `scripts/test_gate_wreg_claim_binary.sh` BUILT and GREEN: gdb-dump-at-bb_seal + objdump per FINDING-2026-08-12j's method, 19-program set (this session's at-risk superset of the finding's 17), 27 slabs, 275 r10/r11 shape checks, every one matching the two licensed mechanisms (CLASS-D glue · RTCC veneer). `--quick` smoke mode exists. **Allowlist extension = FINDING-required event, says so in the script header.**
  - W-0a data half was already complete (RTX 223/223 · templates · raw-byte · x86_asm.h 23/23). Text-gate whitelist now reads `pinned occ=23 OK`, zero drift. `--strict` overall remains red only on W-3's not-yet-existing glue emitters — expected, not W-0's debt.
- [ ] **W-8 · THE 30 SN4-UNREACHABLE RTX OCCURRENCES — PRODUCT-WIDE DEBT (minted s36c from Lon's W-0b(a) ruling).** Census + per-occurrence classification already done (`FINDING-2026-08-12h`, the 30 "excused" rows — that word is now obsolete, they are queue). Work = reassign or veneer-cover each, per the same idiom families as the 193. Not urgent for SN4 floors (unreachable by definition) but blocks the day Icon/Prolog adopt wires; sequence after W-7/W-6 unless an Icon/Prolog wire ladder opens first, in which case it jumps.
- [x] **W-1 · ZCTX SCRATCH ERADICATION — DONE s33 (`26c84e72`).** Compressed at s36 handoff per RULES.md step 1 (was a 5-line entry); the one fact worth keeping: `g_zctx[66]` was dead exported BSS, deleted, and **HOME GATE line 4 is satisfied as a MEASURED side effect — `g_blob_ctx` and `rt_blob_ctx_ptr` both grep to 0.** Full history in `FINDING-2026-08-12b`.
- [ ] **W-2 · PUSH/POP GUARD UNIFICATION — ⛔⭐ RECOMMEND CLOSING OR RE-SCOPING (s36). THE RUNG HAS NO WORK LEFT AND NO WITNESSES. LON DECISION OWED.** Both halves of its premise are now falsified, by two separate sessions: (1) the named asymmetry is **structurally unreachable** — `lbl_res`'s address is taken at exactly ONE site, inside the `_blob_wire` branch itself, so nothing reaches the pop arm without having executed the push (s35, `FINDING-2026-08-12i`); the guards are textually different but semantically equivalent because `flat_pat`/`flat_jmp_entry`/`_wire_stub` are per-GRAPH-emission state that cannot change between the push and the res landing within one graph (re-verified s36 against the `sm_emit_t` struct + `emit_jmp_entry_clear`). (2) its named witnesses **D12/D13 are a different bug entirely** — an ARBNO template-dispatcher defect with nothing to do with r10/r11 push/pop (s36, `FINDING-2026-08-12k`). **So: no defect, no witness, and "unify two provably-equivalent predicates" is cosmetic tidying, not a correctness rung.** Three candidate dispositions, all cheap, none mine to pick: **(a)** close it as FALSIFIED with a one-line note that the guards are equivalent-by-construction; **(b)** keep it as a pure hygiene item, explicitly demoted below W-3/W-4/W-6 and stripped of its witnesses so no future session mistakes it for a live defect; **(c)** re-scope it to the thing the census actually found worth doing — the push/pop *emission* is raw string/byte literals inside `emit.cpp` (`:2721`/`:2724`/`:2688-90`), which is a live TEMPLATE-ONLY LAW violation in spirit even if grandfathered in practice; moving it into `bb_glue_*.cpp` behind `x86()` would be a real, gate-checkable rung. ⛔ **Whichever you pick, please strike D12/D13 from this rung's witness line** — they belong to the ARBNO owner (see cursor's ROUTING QUESTION).
  - **Line numbers, verified s36 (do not trust any cited in older prose):** push `emit.cpp:2721` TEXT / `:2724` BINARY, guard `_blob_wire` (defined `:2720`); reload `:2690` TEXT / `:2691-93` BINARY, guard `flat_pat` (`:2690`); `_wire_stub` (`:2717`); related `op_zgpop` (`:842`).
  - **CENSUS DONE** (s35): `bb_glue_flat.cpp` + `bb_glue_framed.cpp` read in full — **they contain NO r10/r11 push/pop at all.** `FINDING-2026-08-12i`.
- [ ] **W-3 · WREG MECHANISM, DORMANT.** Site glue `lea r10,[rip+site_γ]` · `lea r11,[rip+site_ω]` · `jmp <first interior box>`; exits `jmp r10`/`jmp r11`. Killswitched; default emission byte-identical to HEAD. r10/r11 are caller-saved ⇒ saves are TEMPLATE-EMITTED per-activation on the spine, never an implicit choke (s18 RSP-SAFETY + the stack-arg witness). **The emitter already exists and is dormant: `bb_glue_pass_wires_blob()` in `bb_glue_flat.cpp:154-159` (r10/r11 twin of `bb_glue_pass_wires`). Start there, not from scratch.**
- [ ] **W-4 · ARENA WIRE-PAIR SLOT (+16B) — THIS SEAT OWNS THE LAYOUT.** Blob-interior pending records capture {r10,r11} at push, restore at β, or it is `g_blob_ctx`'s single-cell defect in register clothing (the LAW). RBP/EARN-5 consumes this layout — one authority. ⛔ **The census named TWO shapes the layout must cover, not one — see the cursor's CARRY SHAPES block.**
- [ ] **W-5 · ⛔ THE FLIP — REQUIRES EARN-1 + EARN-3 LANDED (EARN-10 ordering).** PROC-shim deletion (PT-1..3), CLASS-D exit ceremony dies with it. The old WREG residual (19 SEGV + 7 HANG) was MISSING FRAMES, not glue defects — EXPECTED cured by EARN; measure by set, never assume. ⛔ **PREDICATE NOTE (2026-08-12): `frame_need_of` does not exist in `src/` under ANY spelling — it is a FORWARD REFERENCE to a symbol `GOAL-RBP-EARN.md` must create. This seat cannot unblock it by working harder; only the RBP seat can. Do not re-check it hopefully each session — check the EARN goal file's cursor instead.**
- [ ] **W-6 · RTCC RE-ENTRANT PRESERVATION + DEFAULT-ON REVALIDATION.** The veneer round-trips wires on leaf crossings only; fix the re-entrant case; then RTCC default-ON must hold the P0 floors with NO `SCRIP_RTCC=0` escape (kills the m4-130 class). Belt-and-suspenders: `-Wl,-z,now` for the r11 lazy-binding clobber. **Leaf half PROVEN SAFE (s35: 172 veneered, 0 bare match-time). Scope is re-entrant ONLY. Witnesses named: probes `140`/`141`.**
- [ ] **W-7 · ARBNO DISPATCHER SOUNDNESS — ROUTED TO THIS SEAT (Lon, s36 answers: "You own the dispatcher bug").** Witnesses: D12 (SEGV) · D13 (hang); X01 CONFIRMED RELATED s38 (same dispatcher gap, general form — see cursor). Root cause + full trace + blast radius: `FINDING-2026-08-12k-…`.
  - **⭐ INTERIM GUARD LANDED s38 (SCRIP `fc8b96b8b`, verified @`73c1ac33`-era tree + one rebase).** `op_arbno_body_defer_unsafe` (emit.h struct end + emit.cpp companion scan beside `op_arbno_body_k0` + per-node reset) ⇒ `bb_match_arbno()` declines with `x86_bomb` instead of the unsound plain-frameless fallback. **D12: SIGSEGV(139)→SIGABRT(134) named bomb. D13: hang(124)→134.** Floor-neutral, A/B-proven against a stashed baseline build (NOT assumed): probe/bb identical `159 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}`; crosscheck/patterns identical `PASS=77 FAIL=45` with a byte-identical failing-NAME set, only exit codes moved (145/165/183 139→134, 178/179 124→134). 16-passer set re-verified individually green.
  - **⛔ THE BOMB ARM MUST DEF ITS PAIR LABELS.** First version left 3–8 unresolved forward refs: the drive loop registers `β`(`PAIR(1)`, generic per-node pass emit.cpp ~2412) and `na_s`/`na_f`(`PAIR(2)`/`PAIR(3)`, `flat_drive_match_alt` ~1201) UNCONDITIONALLY before the template runs. Fixed by `x86_beta()` + `def PAIR(2)` + `def PAIR(3)` after the `ud2` (dead but resolved). **Generalizes to every n-ary template — see cursor scrutiny item 5.**
  - **NOT CLOSED — this is interim only.** It converts silent corruption into a loud refusal; it flips ZERO witnesses green. Real fix = anchor-relative ARBNO cell = **W-4 layout, which this seat cannot self-serve.**
  - **DISCRIMINATOR CONFIRMED (s36b, gdb at `lower_snobol4.c:1324`):** D12 builds 3× `DEFER(sval=LIST, pat_static=0)`; D09 (a passer) builds `DEFER(sval=P, pat_static=1)`. Bare `ITEM` in the pattern expression resolves through to the `*LIST` defer at lower time, so **the fix keys on the DEFER node's own `pat_static` — no extra indirection needed.**
  - **⛔ FIX CONSTRAINT (measured, not negotiable):** the 16-passer set {D09 D10 D11 G19 G20 H21 H24 H25 N12 N17 X02 X03 X04 X05 X06 X11} rides the same plain-frameless path with `k0=0` and must stay green BY SET. A blanket DEFER exclusion breaks all 16.
  - **⛔ FIX SHAPE, honestly stated:** neither existing arm is sound for a `pat_static=0` body — K16's re-homed static offsets assume no unmodeled suspend, plain-frameless assumes zero frontier motion. The correct home for the ARBNO cell in that class is an **anchor-relative slot** (FR/rbp per-activation, or the W-4 arena slot — one more reason W-4's layout decision is load-bearing). Interim option: decline with `x86_bomb` for `pat_static=0`-bearing bodies only — converts silent stack corruption into a loud compile-time refusal, flips 0 witnesses green, breaks 0 passers; a floor-neutral honesty patch, not a fix.
  - Reproduce: `SCRIP_ARBNO_DIAG=1 ./scrip --run <probe>` (arm verdict + k0) · gdb `start; break lower_snobol4.c:1324` + `printf`-commands for pat_static per node · `diff` vs `.ref` (never shell `[ ]` on multi-line output).

## GATES (every rung)
claim gate `--strict` green · probe + crosscheck BY SET vs P0 floors both modes, RTCC ON and OFF until W-6 seals · killswitch md5 discipline · FINDING + cursor move.

## ⭐⭐⭐ LIVE CURSOR — 2026-08-12 s39c (Claude Sonnet 5) — HANDOFF · W-3 STATUS CORRECTION: SCRIP_WREG KILLSWITCH IS DEAD CODE, NEW UNROOT-CAUSED CRASH FOUND IN THE SAME MECHANISM

### What this session did (continuation of s39a/s39b, same session, finally touched the actual charter)
With push and MON-CAP both credential-blocked, spent remaining budget checking this seat's own W-3 charter
instead of more ARBNO. Found the rung's own status line is WRONG. Full detail: `FINDING-2026-08-12r-…`.

**`bb_glue_pass_wires_blob()` is NOT dormant** — it has exactly one caller, `bb_match_defer.cpp:83`, called
UNCONDITIONALLY (no `IF(...)` guard). Every DEFER-pattern blob entry in the compiler has been emitting
r10/r11 wire glue, not the rcx/rdx fallback, at HEAD, right now. **`SCRIP_WREG`, the killswitch three
separate comments (and the goal file's own W-3 line: "Killswitched; default emission byte-identical to
HEAD") claim exists, is not implemented anywhere** — `grep -i WREG src/` finds only the comments; no
`getenv("SCRIP_WREG")` call exists. Empirically confirmed: `SCRIP_WREG=0` vs. unset produces byte-identical
compiled output. **This rung's status needs correcting before anyone reasons about it as "safe dormant
code."**

**While confirming this empirically, found a new, oracle-verified SIGSEGV** in exactly this mechanism:
`corpus/probe/bb/witness_wreg_s39/W01_stored_pattern_defer_len_capture.sno` — `P = LEN(*N) . X` (pattern
stored in a variable, deferred LEN, WITH capture) then `S ? P` crashes (exit 139); oracle says `=S`. Needs
BOTH the stored-pattern-variable indirection AND the capture — inlined or capture-free variants both pass;
not covered by existing D07/D08/D09 DEFER probes. gdb backtrace shows the fault PC 5 bytes past r10's value
and a suspiciously corrupted rsp — consistent with, but not proven to be, a wire-glue defect. **NOT
root-caused** — no source-level single-step trace done, only a post-mortem address backtrace.

**Zero SCRIP source changes.** corpus gains one new non-graded witness (`witness_wreg_s39/`, not wired into
`run_suite.sh`).

**WATERMARK: unchanged, same as s39a/b: 160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}** (this new
crash is a fresh construction, not a suite member, so it does not move the count).

### Why stopped here rather than fixing it
This crash, unlike X01, doesn't need MON-CAP (it's a straightforward SIGSEGV, plain gdb suffices) — the
real blocker is budget: a proper source-level hunt (breakpoint at the C++ template site, single-step
through JIT'd bytes without symbols) is slow and this session's budget mostly went to the X01 witness
construction earlier. More importantly, **this is a status-correcting discovery Lon should see before
anyone lands a fix or relies on "W-3 is dormant"** — surfacing it cleanly seemed like better use of the
remaining session than a rushed, possibly-wrong patch attempt on a newly-found bug in the seat's own
charter mechanism.

### Still open / still owed
- **W-3's real status is now: LIVE, UNCONTROLLED, CRASHING on at least one construction** — not "dormant,
  killswitched, safe." Recommend fixing the documentation/killswitch mismatch (Finding recommendation (a))
  regardless of whether the crash gets root-caused this cycle.
- **The new crash needs a real gdb hunt** — next session with budget for it should start there; no
  credential dependency, unlike everything else this seat has hit today.
- **W-4/W-6 — still completely untouched, six sessions running.**
- **Routing question (s38) — even more relevant now**: if this seat keeps finding real charter bugs the
  moment it looks at its own rungs (this session: one dead killswitch + one new crash, in under an hour of
  investigation), that's an argument FOR keeping it here, not against — worth flagging to Lon alongside the
  original routing question rather than assuming the s38 framing still holds unmodified.

## ⭐⭐⭐ LIVE CURSOR — 2026-08-12 s39b (Claude Sonnet 5) — HANDOFF · X01 DISCRIMINATOR NARROWED (7 ORACLE-VERIFIED WITNESSES), STILL NOT GDB-CONFIRMED, ZERO SCRIP EDITS

### What this session did (continuation of s39a, same session)
Built 7 hand-constructed `.sno` witnesses to test s39a's "purity" hypothesis for X01 against more than
n=1. Cloned the public `snobol4ever/x64` oracle (no credential needed) and verified every witness against
real SPITBOL output before touching SCRIP. Full detail: `FINDING-2026-08-12q-…`.

**s39a's "purity" hypothesis is FALSIFIED too** (not just the blanket-widening ones): a literal placed
OUTSIDE the outer ARBNO's own repeated arm does NOT rescue X01's shape, but a literal placed INSIDE that
arm (alongside the nested ARBNO, as a real co-member of the same repeated unit) DOES. Narrower discriminator
now supported by 7 constructed + 2 corpus witnesses: the outer arm needs a co-member that **consumes at
least one subject character on its own turn** — a null-string literal or explicit `LEN(0)` inside the arm
does NOT rescue it (ruled out with dedicated witnesses), so it's not "any co-member," specifically one that
advances the subject cursor. Minimal pair found: `ARBNO(ARBNO(LEN(1)))` (fails) vs.
`ARBNO(ARBNO(LEN(1)) 'x')` (passes) — same emitter trace (`framed=0 k0=0 sq=0 kk=16` both), opposite
outcome. **No currently-staged field distinguishes them.** Mechanism still not diagnosed — this is
narrowing, not a root cause, and RULES.md MONITOR-FIRST still applies (gdb/monitor tracing, not more
black-box probing, is the prescribed next step).

**Zero SCRIP source changes, same as s39a.** corpus gains a new non-graded witness directory
(`probe/bb/probes_x01_witness_s39/`, 7 `.sno` + 7 oracle `.ref` + README) — explicitly NOT wired into
`run_suite.sh`.

**WATERMARK: unchanged, same as s39a: 160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}.**

### Why stopped here (same reasoning as s39a, restated)
MON-CAP (csnobol4 build) requires `TOKEN_SEE_LON`, not available this session — three investigations in a
row now blocked on the same credential (s38's diagnosis, s39a's fix attempt, s39b's narrowing). Writing a
guard off an oracle-verified-but-mechanism-unconfirmed correlation would be a design call, and this seat has
now spent SIX consecutive sessions on ARBNO-dispatcher territory instead of its own charter — s38's routing
question (still unanswered) gets more urgent with each one, not less.

### Still open / still owed (carried, unchanged in substance from s39a)
- **W-3/W-4/W-6 — still untouched, six sessions running.**
- **MON-CAP — now blocking three investigations, all in this exact class.** Strongest-yet case for
  prioritizing it: X01W1-vs-X01W5 is a clean minimal pair, about as small as this bug class will get, ready
  to bisect the moment gdb/monitor tooling is available.
- **Five(+) questions for Lon from s38, still unanswered** — routing is now the most urgent one.

## ⭐⭐⭐ LIVE CURSOR — 2026-08-12 s39 (Claude Sonnet 5) — HANDOFF · X01 WIDENING FALSIFIED, ZERO SOURCE EDITS, WATERMARK UNCHANGED

### What this session did
Picked up s38's own "suggested next step" for X01 — widen W-7's guard from `op_arbno_body_defer_unsafe` to
the general `!op_arbno_body_k0` case — and **falsified it** before landing any code. Full detail:
`FINDING-2026-08-12p-…`. Short version: `k0=0` (and the more targeted `op_body_has_arbno`, which looked
like a better-fitting existing field) are BOTH `1`/set for 10 of the 16-probe pat_static=1 passer set
(G19 G20 H24 H25 X02 X03 X04 X05 X06 X11 — all genuinely contain nested ARBNO in their body, same as X01).
A blanket guard on either field breaks 10 currently-green probes to fix 1. **X01 is trace-identical to its
passing siblings on every field the emitter currently stages** (framed/k0/sq/kk/osv/body_has_arbno/
defer_unsafe all match X02's shape exactly) — there is no existing discriminator, narrow or wide, that
separates it. The actual distinguishing property (hypothesized, NOT validated beyond n=1): X01's outer body
span is PURELY the nested ARBNO, no bracketing K=0 members, unlike X02/X04/X06/G19 which wrap the inner
ARBNO in literal delimiters. No second positive witness exists in the suite to test this against.

**Zero source files changed.** One temporary diagnostic `fprintf` was added to `bb_match_arbno()` to
confirm `op_body_has_arbno`'s staged values, then reverted; `git diff` against SCRIP HEAD is empty,
confirmed after rebuild. Nothing to commit, nothing to push.

**WATERMARK: unchanged — re-measured, identical to s38: 160 pass · 1 xfail · 5 REGRESSION
{D12,D13,H31,X01,X10}.** (s38's own note: count is 159→160 from unrelated LOWER work, not this seat.)

**SCRIP `0bbf092b` — UNCHANGED. corpus `7814057e` — UNCHANGED (no regen ran; no codegen file touched).
.github this commit (the FINDING + this cursor move only).**

### Why this seat stopped rather than landing a narrower purity-check guard
A new scan field ("is the body span EXACTLY one IR_MATCH_ARBNO node, nothing else") is a plausible next
guard, parallel in shape to W-7's DEFER scan — but (1) it's unvalidated against more than one positive
witness and the 2-way sync-step monitor that RULES.md prescribes for exactly this wrong-answer-rc-0 class
is dark in this container (`csnobol4` not built, same MON-CAP gap s38 already flagged); (2) X01's real fix
is very likely the same W-4 layout work as W-7's real fix, so a second guard is doubly-interim; (3) this
would be a FIFTH consecutive session of this seat working ARBNO-dispatcher territory instead of its own
r10/r11 charter (W-3/W-4/W-6, still untouched) — s38's own scrutiny item 1 asked Lon to rule on whether that
routing should continue, and it's still unanswered. Landing another guard unilaterally pre-empts that
decision rather than waiting the one turn for it.

### Still open / still owed (unchanged from s38, carried)
- **W-3/W-4/W-6 — this seat's actual charter — still untouched, now FIVE sessions running.**
- **W-4 layout** — still the real blocker for W-7's DEFER case, X01, and 145/165/178/179/183 + demo board.
- **Five questions for Lon from s38, none answered yet** — routing (item 1, now more urgent), W-4 promotion,
  X01/general-guard scope (this session adds data: the "general `!k0` guard" half of Q3 is now answered —
  NO, falsified, see above — but "separate rung, narrower guard" is still open), W-2 disposition, MON-CAP.
- **MON-CAP / `csnobol4` build** — now blocked TWO investigations in a row (s38's diagnosis, this session's
  attempted fix). Recommend prioritizing this the next time a code-writing (not just diagnostic) session
  picks up X01 or any other wrong-answer-class probe.

## ⭐⭐⭐ LIVE CURSOR — 2026-08-12 s38 (Claude Sonnet 5) — HANDOFF · W-7 INTERIM GUARD LANDED, D12/D13 CONVERTED FROM SIGSEGV/HANG TO CLEAN BOMB, REAL FIX STILL BLOCKED ON W-4

### What this session did
Landed the interim, floor-neutral fix s37's cursor spec'd: `bb_match_arbno()` now declines with `x86_bomb(...)`
instead of silently emitting the plain-frameless arm when the body carries an `IR_MATCH_DEFER` with
`pat_static==0` (can transitively recurse, manual p.122's `*X` idiom — confirmed the exact SPITBOL manual
citation this session, Ch.9 "Recursive Patterns", the canonical `ITEM = SPAN(...) | *LIST` / `ARBNO(',' ITEM)`
list example is D12's own shape verbatim).

**New field `op_arbno_body_defer_unsafe`** (emit.h, true struct end; emit.cpp, same containment scan/span as
the pre-existing `op_arbno_body_k0`, added to the per-node reset block too). Consumed at the `bb_match_arbno()`
dispatch site in `bb_match_arbno.cpp`.

**One non-obvious complication, now fixed:** the first version of the bomb path aborted with 3-8 unresolved
forward references. Root cause: the drive loop (`emit.cpp` ~2412 generic per-node pass + ~1201
`flat_drive_match_alt`) pre-allocates `β`/`na_s`/`na_f` labels for EVERY `IR_MATCH_ARBNO` node UNCONDITIONALLY,
before the template runs, because sibling boxes structurally jump to them regardless of which arm gets picked.
Bombing out early left those dangling. Fix: the bomb path now still `def`s all three (`x86_beta()` +
`PAIR(2)`/`PAIR(3)`) as dead-but-resolved stubs after the `ud2` — unreachable but present, so
`bb_emit_end`'s forward-reference resolution succeeds.

### Measured (A/B, stashed baseline comparison — not just "looks right")
- **probe/bb: 159 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}** — IDENTICAL set to the pre-fix
  baseline. D12/D13 now exit 134 (clean SIGABRT + diagnostic message) instead of 139 (SIGSEGV) / hang.
- **16-probe pat_static=1 passer set individually re-verified green**: D09 D10 D11 G19 G20 H21 H24 H25 N12
  N17 X02 X03 X04 X05 X06 X11 — all still exact `.ref` matches. The guard never fires for them (confirmed by
  construction: `pat_static=1` for all of them, per the lower_snobol4.c stamp).
- **crosscheck/patterns (122 progs), full A/B**: baseline (git stash) PASS=77 FAIL=45; my build PASS=77
  FAIL=45 — **byte-identical failing-name set**, confirmed by diff. Only deltas are exit codes, all the same
  direction as D12/D13: `145_pat_left_assoc_via_arbno_fence` 139→134, `165_pat_arbno_defer_var_body` 139→134,
  `178_pat_recursive_star_list_zs2` 124→134, `179_pat_arbno_defer_recursive_list` 124→134,
  `183_pat_arbno_defer_recursive_carry` 139→134. Zero programs newly broken, zero newly fixed — purely a
  crash-quality improvement (silent corruption → named refusal) on programs already in the failing set.
- **Demo corpus regen** (`util_regen_demo_s_artifacts.sh`, mandatory per RULES.md step 4 since this touched
  `emit.cpp`/`x86_asm.h`-adjacent codegen): 12 `.s` artifacts changed in `corpus` (calculator-1/2 + variants,
  json-match + variants, treebank-array/list/match + variants) — the recursive-grammar demo family, exactly
  the class this guard targets. All were ALREADY in the documented 13/15-broken demo-board set (SIGSEGV);
  calculator-1/2 now present as clean named BOMB aborts (rc=134) instead of silent segfaults. Not a floor
  change (they were never in the 2/15 passing set) but a real diagnosability win, and every one of them is a
  live witness that W-4's real fix has a broad, not just probe-suite, payoff once it lands.

### W-7 status: NOT closed — interim only
The checkbox stays unchecked. What's landed converts a memory-corruption bug class into an honest,
loud, compile-time-style refusal — it does not make D12/D13/145/165/178/179/183 (or the calculator/json/
treebank demos) pass. **The real fix is still W-4-blocked**: route the `pat_static==0` body class to an arm
that homes the ARBNO cell at an anchor-relative (per-activation) slot rather than `[rsp+N]`. W-4 owns that
layout decision; this seat cannot self-serve it. X01 remains unexplained by this discriminator (its body has
no DEFER at all — nested `ARBNO(ARBNO(LEN(1)))` — confirmed a genuinely separate defect, not investigated
further this session; still unowned).

### Commits (push status deliberately NOT recorded here — `handoff_status.sh` is the only push truth, RULES STALE-ORIENTATION (a))
- SCRIP `1780cd1a` — the guard itself (emit.h + emit.cpp + bb_match_arbno.cpp).
- corpus `03298563` — regenerated demo `.s` artifacts, committed by the mandated regen script.

### Still open / still owed
- **W-4 layout** — now has FIVE more named live witnesses (145,165,178,179,183) beyond D12/D13, plus at least
  two demo drivers (calculator-1, calculator-2) that would very likely flip green once it lands (their
  ARBNO/DEFER shape is the exact target class — not verified end-to-end this session, since the arm doesn't
  exist yet, but worth checking first once W-4 is real).
- **X01 — ROOT CAUSE FOUND this session (read-only, no fix landed, no code touched — see below).**

### ⭐ X01 INVESTIGATION (this session — DIAGNOSIS ONLY, zero source edits)
`POS(0) ARBNO(ARBNO(LEN(1))) RPOS(0)` on `'abc'` should succeed (=S) per SPITBOL semantics; SCRIP prints =F.
Not a crash — silent wrong answer, rc=0. `SCRIP_ARBNO_DIAG=1` shows BOTH the outer and inner ARBNO taking the
`FRAMELESS` arm: outer is `framed=0 k0=0 sq=0` (declines K16 correctly — `sq=0` because its body contains a
nested `IR_MATCH_ARBNO`, one of the K16 prelude's own container-kind exclusions), inner is `framed=1 k0=1
sq=1` (pure `LEN(1)` body, legitimately k0-safe).

**The root cause is a DISPATCHER GAP, the same SHAPE as W-7's, but broader than the DEFER special case:**
`bb_match_arbno_frameless()`'s own design comment (line 92 of `bb_match_arbno.cpp`) states its soundness
precondition explicitly — *"Gated to the nested-K0 class (op_arbno_framed && op_arbno_body_k0): the frontier
never moves inside the activation, so the cell is [rsp+0]/[rsp+4] from EVERY site."* But `bb_match_arbno()`'s
dispatch (the function W-7 edited) calls `bb_match_arbno_frameless()` as the UNCONDITIONAL fallback — it
never actually checks `op_arbno_body_k0` before falling through. Confirmed via `zd_k()` (emit.cpp ~2005):
`IR_MATCH_ARBNO` is NOT in the K=0 exemption list, so `zd_k(nested ARBNO) == 16`, which is exactly why the
outer's containment scan correctly computes `k0=0` for a nested-ARBNO body — the mechanism is proven, just
not enforced at the dispatch site.

**This is the general form; W-7's `op_arbno_body_defer_unsafe` is ONE instance of it** (DEFER is one specific
K!=0 body member that can violate the frontier-static assumption; a nested ARBNO, which is unconditionally
K=16, is another). X01 is presumably surviving as wrong-answer rather than SIGSEGV/hang because the inner
ARBNO's own net-zero LIFO discipline on ITS success path happens to often restore rsp to the depth the outer
expects — the corruption is in the OUTER's DELTA0/yield-cursor bookkeeping (logic), not necessarily a stray
memory write, which is consistent with rc=0 + wrong output rather than a fault.

**Not fixed — deliberately, this session.** (1) Landing a second, wider dispatcher change in the same session
as W-7's narrow one would have made the two indistinguishable in any later bisect — the guard and the general
gate must be separately attributable. (2) The right general fix is almost
certainly the SAME W-4 arena-layout work the DEFER case needs (route any `k0=0` body — DEFER OR nested-ARBNO
OR any other K!=0 member — to an anchor-relative arm), which argues for generalizing
`op_arbno_body_defer_unsafe` into something like `op_arbno_body_frontier_unsafe` (`!op_arbno_body_k0` in the
general case, W-4-gated) rather than shipping a second narrow bomb-guard. That's a design call for whoever
picks up W-4, not a unilateral call from this seat mid-investigation. (3) Per RULES.md MONITOR-FIRST, the
2-way sync-step monitor (`test_monitor_2way_sync_step_bin.sh`) is DARK for this probe — `csnobol4` isn't
built in this container (`FAIL csnobol4 not built: /home/claude/csnobol4/snobol4`) — so this diagnosis is
static/gdb-adjacent reasoning from the templates + emit.cpp source and the diag trace, not a monitor-traced
bisection. Recommend MON-RE (reinstating the csnobol4 build) before anyone tries to land a fix here, per the
same standing law s35/s36 already flagged for the `dc_sib_bt` blind spot.

**Suggested next step for whoever owns this:** widen the dispatcher gate from `op_arbno_body_defer_unsafe`
to the general `!op_arbno_body_k0` case (a one-line change at the `bb_match_arbno()` ternary — the field
already exists), which would also catch X01 with the same bomb mechanism, OR treat it as a separate rung if
the general case needs different W-4 layout decisions than the DEFER-specific one. Either way this is a W-4
design question, not a mechanical fix this seat should make without that decision.

## ⛔⭐⭐⭐ SCRUTINY OF THIS LADDER — s38 (offered; three items need LON, and one of them is structural)

**s36 said "4 of 7 rungs' premises did not survive contact with the tree." s38's data says the deeper problem
is the SEAT BOUNDARY, and it has now cost three consecutive sessions of charter work.**

1. **⛔ THIS SEAT HAS NOT TOUCHED ITS OWN CHARTER IN FOUR SESSIONS.** W-3 (WREG mechanism), W-4 (arena wire-pair
   slot), W-6 (RTCC re-entrant) are the r10/r11 charter — the reason the seat exists. s35 did census, s36
   diagnosed an ARBNO bug, s37 verified that diagnosis, s38 fixed it and found a second ARBNO bug. **All four
   sessions were spent on ARBNO, which is not this seat's subject matter.** It got here honestly: W-2 named
   D12/D13 as witnesses (falsely — s36 proved they belong to ARBNO), and Lon's s36 answer then routed the
   dispatcher bug here explicitly. But the routing was made when the bug looked like one defect; s38 shows it
   is a defect CLASS whose real fix is W-4 layout work. **RECOMMENDATION: route ARBNO dispatcher soundness
   (W-7 residue + X01 + the general `!k0` gate) to the seat that owns the ARBNO templates — GOAL-SN4-ZETA-MECH
   or GOAL-SNOBOL4-BB — and point this seat at W-6 → W-3 → W-4.** If instead you want this seat to keep ARBNO,
   say so explicitly and I'd suggest renaming the seat, because "WIRES" no longer describes what it does.

2. **⛔ W-4 IS ON THE CRITICAL PATH FOR TWO SEATS AND IS UNSTARTED.** W-4 (arena wire-pair slot layout) is
   listed here as a wires rung, but it is now ALSO the blocker for every ARBNO `k0=0` fix (W-7 real fix, X01,
   the 145/165/178/179/183 witnesses, calculator-1/2 + json + treebank demos). That is a lot of the demo board
   — the plan's own "most legible progress meter", currently 2/15 — sitting behind ONE unstarted layout
   decision. **It is the highest-leverage unstarted item I can see in this file and probably deserves to be
   its own rung with a full runway rather than the 4th item on a seat that keeps getting pulled elsewhere.**

3. **W-5's predicate is still a forward reference** (`frame_need_of` absent from `src/` — re-verified s38 by
   grep, unchanged since s36). Not re-checked hopefully; recording the re-verification only.

4. **STALENESS TAGS — s36's suggestion (2) is worth adopting and this session is evidence.** s37 and s38 both
   re-derived the same `bb_match_arbno.cpp` line numbers because prose cited them untagged. Every rung naming
   a symbol/line/witness should carry `(verified @<hash>)`. Cheap, no tooling, makes rot visible.

5. **⚠ A METHOD NOTE WORTH GENERALIZING (earned the hard way this session).** The W-7 guard's first version
   compiled clean and bombed correctly — and produced 3–8 UNRESOLVED FORWARD REFERENCES, because the drive
   loop pre-registers `β`/`na_s`/`na_f` for every `IR_MATCH_ARBNO` BEFORE the template runs, so a template arm
   that returns early without `def`-ing them breaks label resolution graph-wide. **Any future rung that adds a
   declining/bombing arm to ANY n-ary template (ALTERNATE, FENCE1, SCAN_*, DISJUNCTION — they all go through
   `flat_drive_match_alt`) will hit this identically.** The rule: a bomb arm must still define every pair label
   its normal arm defines. Worth stating once in ARCH or GOAL-TEMPLATE-REVAMP-RULES rather than rediscovering.

### ⛔ QUESTIONS FOR LON (s38)
1. **ROUTING (the big one, item 1 above): does this seat keep ARBNO, or go back to r10/r11?** Four sessions
   of evidence say the current arrangement starves the charter. Either answer is workable; the ambiguity is
   what costs.
2. **W-4: promote to its own rung with a runway?** It now gates two seats and most of the broken demo board.
3. **X01 / the general `!op_arbno_body_k0` gate: widen W-7's guard, or separate rung?** One-line change if
   widened (field exists); the design question is whether the general case wants a different W-4 layout than
   the DEFER case. Not mine to decide unilaterally.
4. **W-2 disposition — FOURTH re-ask** (s35, s36, s37, s38). Three options written into the rung since s36.
5. **MON-CAP / `csnobol4` build — RE-ASK, and it is now blocking, not theoretical.** The 2-way sync-step
   monitor is DARK in this container (`FAIL csnobol4 not built: /home/claude/csnobol4/snobol4`), so X01 — a
   wrong-answer-rc-0 defect, exactly the class RULES.md says the monitor exists to catch — was diagnosed by
   source reading instead of the prescribed mechanical hunt. **Three of the five REGRESSION members are
   wrong-answer or hang rather than crash. Every "floor held BY SET" claim in this file is only as good as an
   instrument that cannot see that class.** Recommend a MON-RE rung: get `csnobol4` building in the container
   and add it to `install_system_packages.sh` (the same one-authority pattern that fixed the gdb trap).
- **W-2 disposition, MON-CAP/dc_sib_bt ownership, W-0b's now-resolved status** — carried unchanged from s36/s37,
  not touched this session; see those cursors below for full detail.
- **W-3/W-4/W-6 (this seat's own charter work)** — still untouched. Same observation s36 made: this seat keeps
  finding and fixing ARBNO-dispatcher-adjacent defects (routed here by Lon at s36) rather than touching its
  own r10/r11 wire charter. Worth a check-in on whether that routing should continue past W-7's interim state,
  now that the interim is landed and the remaining work (W-4 layout) is a different seat's decision.



### What this session did
Orient-only + code verification pass. No source files changed. Repos cloned fresh; binary built clean at HEAD. FINDING-2026-08-12k absorbed in full including its self-correction (zd_k DEFER clause is NOT the bug; the bug is the dispatcher never consulting op_arbno_body_k0). W-7 discriminator (pat_static) already confirmed by s36b's gdb check — this session verified the *dispatch code path itself* by reading the actual source rather than trusting the finding's simplified excerpt.

### Floor re-measured at HEAD (`SCRIP=7eac50a9`, `corpus=799133cc`, `.github=cd466e3d` pre-pull)
`bash corpus/probe/bb/run_suite.sh` → **159 pass · 1 xfail · 0 XPASS · 5 REGRESSION {D12, D13, H31, X01, X10}**. Regression set IDENTICAL to s36. Count moved 157→159 (LOWER's L-3b landing picked up 2 unrelated probes; nothing WIRES owns moved). This is the new watermark — the s36 "157" figure is stale.

### `bb_match_arbno()` dispatcher — source verified
`src/templates/bb_match_arbno.cpp` lines 207–222 (commit `5abdd0ae` "D-1 DELETE"):
```
return _.op_arbno_body_kk > 0
         ? bb_match_arbno_frameless_k()      // K16: requires _sq (no DEFER/ALTERNATE/…)
     : _.op_off < 0
         ? x86_alpha() + x86_bomb(...)
     : (_.op_sa < 0 || _.op_sb <= 0)
         ? x86_alpha() + x86_bomb(...)
         : bb_match_arbno_frameless();       // ← UNCONDITIONAL fallback, no k0 check
```
Confirmed: `op_arbno_body_k0` IS computed (emit.cpp:958, inside the `_chain` prelude) but feeds only into `bb_match_arbno_DELETED_ARMS()` — confirmed zero external callers by grep. The live entry never consults it. The finding's description is accurate; its simplified snippet matches the real code.

### K16 prelude `_sq` exclusion list — confirmed at emit.cpp:955
Nodes that set `_sq=0` and therefore decline K16, falling through to plain-frameless: `IR_MATCH_ALTERNATE`, `IR_MATCH_ARBNO`, `IR_MATCH_FENCE1`, **`IR_MATCH_DEFER`**, `IR_MATCH_VALUE`, `IR_CALL`, `IR_CALL_VALUE`, `IR_DISJUNCTION`, `IR_MATCH_ABORT`. D12's body (`',' ITEM` where ITEM contains `*LIST` → IR_MATCH_DEFER) sets `_sq=0`, `op_arbno_body_kk` stays 0, falls through. This is the exact mechanism.

### D12 reproduced live
`SCRIP_ARBNO_DIAG=1 ./scrip --run corpus/probe/bb/probes/D12.sno` → `[ARBNO-K16] framed=0 k0=0 sq=0 kk=16 osv=1 mb=-1 me=10 route=legacy` then `[ARBNO-ARM] FRAMELESS` then `Segmentation fault` (exit 139). Matches finding exactly. Note: the diagnostic prints `kk=16` reflecting the prelude's own scan before it declines; `route=legacy` means K16 was NOT selected; arm=FRAMELESS is the unconditional fallback. No contradiction.

### W-7 fix — where things stand, honestly
Two options, in order of increasing ambition:
- **Interim (floor-neutral, do-it-now):** In `bb_match_arbno()`, before the unconditional `bb_match_arbno_frameless()` call, check whether any node in the body span is `IR_MATCH_DEFER` with `pat_static==0` — if so, emit `x86_bomb("IR_MATCH_ARBNO: body contains suspend-capable DEFER — anchor-relative slot not yet implemented (W-4)")`. Flips 0 witnesses green, breaks 0 of the 16-passer set, converts silent stack corruption to a loud compile-time error. Honest, reversible, does not require W-4.
- **Real fix (requires W-4 layout decision):** Route the `pat_static==0` body class to an arm that homes the ARBNO cell at an rbp-relative (per-activation anchor) offset rather than `[rsp+N]`. W-4 owns the layout; this arm cannot be written soundly without it. The DELETED_ARMS's DT arm is a partial precedent (see the `FR(off+4)` per-activation cell it uses) but it's not a drop-in — the recursion-safe shape is different.

**Recommended next move for W-7:** land the interim x86_bomb guard first (safe, ~10 lines in `bb_match_arbno()`), re-run suite to confirm 16-passer set stays green and D12/D13 get a clean compile-time error instead of SIGSEGV/hang. Then open W-4 layout design. The body-node scan already exists inline in the K16 prelude (emit.cpp:955's `_sq` loop) — a compact version of it is the model for the bomb guard's own check.

### Still open / still owed
- **W-2 disposition (Lon):** three options written in the rung note; D12/D13 struck from its witness line (they are W-7's). No action taken this session.
- **MON-CAP / `dc_sib_bt`:** still unknown, still unowned.
- **W-5 predicate:** `frame_need_of` still grepping empty. Still FALSE. Still skip.
- **X01 / X10 relation to W-7:** X01 is `ARBNO(ARBNO(LEN(1)))` — no DEFER in the body, so the `pat_static` discriminator would NOT catch it. Possibly a sibling defect (nested ARBNO rather than recursive DEFER). Not traced this session; X10 is `TIMEOUT` on PAIRS negative-control probe. Both remain unowned.

## ⭐⭐⭐ LIVE CURSOR — 2026-08-12 s36 (Claude Sonnet 5) — HANDOFF · D12 ROOT CAUSE PINNED, NO FIX LANDED, W-2 RECOMMENDED FOR CLOSURE

### ⭐ s36b ADDENDUM — LON ANSWERED (same day, post-handoff); DISCRIMINATOR CONFIRMED
- **Q4 ANSWERED: THIS SEAT OWNS THE ARBNO DISPATCHER BUG** → minted as **W-7** (see RUNGS; full constraint set + confirmed discriminator recorded there). The 5-minute `pat_static` check is DONE: D12's DEFERs read `pat_static=0` ×3, D09's reads `1` — the fix's key exists exactly where predicted. Binary rebuilt at `9780591d` (a parallel session's `bb_glue_flat.cpp` landing) before measuring.
- **Q5 ANSWERED-UNKNOWN:** MON-CAP existence and `dc_sib_bt` ownership — Lon does not know. Both remain open product-wide; the wrong-answer-rc-0 blind spot stands unowned. Carried, not closed.
- **Q2 (W-0b) ANSWERED AND EXECUTED (s36c, same day):** (a) product-wide — 30 RTX occ are debt, minted **W-8**; (b) delegated — executed as 9=class(3) + 13=new class(5) + 1=temporary(3)/DIES-WITH-W-5, pinned occ=23, gate reads OK; (c) accepted — `test_gate_wreg_claim_binary.sh` built and GREEN (19 programs / 27 slabs / 275 shape-checks at `9780591d`). **W-0 IS CLOSED.** See the rung for the full record.
- **NEXT RUNG for this seat is now W-7** (owned, discriminator confirmed, constraint set measured), then W-6, then W-8. W-5 still blocked.

**NEXT RUNG: W-7 (owned, ready) → W-6 — NOT W-2 (falsified, see rung) and NOT W-5
(still blocked, `frame_need_of` re-checked s36, still absent from `src/`).**
**WATERMARK: unchanged — s35's by-set m3 floor stands, NOT re-measured this session (no code touched):
157 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}.**

**SCRIP `825ab0a4` — UNCHANGED, zero compiler bytes edited this session (diagnosis + one fix attempt
abandoned before landing). `.github` this commit. corpus `e7424687` untouched. x64 cloned for the monitor.
RULES.md step 4 (`.s` regen ×3) NOT APPLICABLE and deliberately not run — no codegen file was touched;
running it would have produced churn with no edit behind it.**

### What this session did
Traced **D12** (the 5-REGRESSION set's SIGSEGV) to a concrete root cause, mechanically, and then declined
to fix it because the measurement said the obvious fix was worse than the bug. Full detail:
`FINDING-2026-08-12k-…`. Short version:
- `bb_match_arbno()` (`bb_match_arbno.cpp:207`, the live dispatcher) has two arms: K16 (gated on a real
  "sequence-only" body check) and plain-frameless (**gated on nothing — it is the unconditional else**).
  Any body failing the K16 gate lands on plain-frameless without anyone verifying that arm's own stated
  precondition (`op_arbno_body_k0`, "the frontier never moves inside the activation"). For D12 that
  precondition is FALSE, and the arm's `[rsp+4]` yield-cursor write then stomps the high 32 bits of a live
  CLASS-D resume-record landing address when the nested `*LIST` suspends. gdb-confirmed: exact
  instruction, exact before/after stack values, twice.
- **Then the corpus said stop.** 19 probes ride that exact path with `k0=0`; **16 of them PASS today.**
  A blanket "decline on any DEFER in the body" fix breaks 16 to fix 3. The discriminator is finer —
  `pat_static` (lower-time, "transitively defer-free ⇒ cannot recurse") should separate D09's safe
  `*P`(`=LEN(1)`) from D12's recursive `*LIST`-via-`ITEM`, but I did not confirm it on the actual node
  before budget ran out. **Confirming `pat_static` on D12's ARBNO-body DEFER node is the smallest
  concrete next move and should take minutes.**

### ⛔⭐⭐ SCRUTINY OF THIS LADDER (offered, not applied — three of these need Lon)
**The pattern worth naming: 4 of 7 rungs' premises did not survive contact with the tree.** W-1's premise
was stale (work already done by another commit). W-2's asymmetry is unreachable AND its witnesses belong
to another bug. W-5's predicate is a forward reference to a symbol that has never existed. W-0 is blocked
on a decision, not on work. That is not four unrelated accidents — **this ladder was written against a
tree that has since moved, and it is now costing roughly one session per rung just to discover that.**
Concretely, I'd suggest:
1. **W-2 → close or re-scope** (three options written into the rung itself; my preference is (c), the
   TEMPLATE-ONLY-law re-scope, because it's the only one with a real gate behind it).
2. **Add a cheap staleness convention.** Every rung that names a symbol, a line number, or a witness could
   carry the commit hash it was verified against. Three sessions have now burned time re-deriving line
   numbers that drifted; a `(verified @<hash>)` tag makes rot visible instead of silent. Cheap, no tooling.
3. **The seat boundary is leaking, in both directions.** This seat has now found two defects that are
   almost certainly not its own (s35's `dc_sib_bt` silent-wrong-answer, s36's ARBNO dispatcher) and has
   one rung (W-5) it structurally cannot unblock. Meanwhile its own charter work (W-3/W-4/W-6) is
   untouched across three sessions. **If the goal is r10/r11 product-wide, the seat should probably be
   pointed at W-6 → W-3 → W-4 and told to route incidental finds out rather than trace them** — I traced
   D12 this session because W-2 named it as a witness, and that turned out to be a false lead by
   construction.

### ⛔ QUESTIONS FOR LON (several are re-asks — s35's went unanswered)
1. **W-0b policy** — still the only thing blocking W-0, now for a fourth session. One line into
   `wreg_claim_whitelist.txt` once decided. (a) clear r10/r11 where SN4 can't reach? (b) is `x86_asm.h`
   whitelist class (3) — noting the register-name-table 13 are a genuine widening, not a plain
   application? (c) sanction an objdump-based binary gate?
2. **W-2 disposition** — close as falsified, demote to hygiene, or re-scope to the emit.cpp raw-literal
   removal? (Options written into the rung.)
3. **ROUTING: who owns the ARBNO dispatcher bug?** It is a template/classifier defect
   (`bb_match_arbno.cpp` + the `_sq`/k0 scans in `emit.cpp`), not a wires defect. Smells like
   `GOAL-SN4-ZETA-MECH` or `GOAL-SNOBOL4-BB`. It is fully diagnosed and has a named next step — it just
   needs an owner who isn't this seat.
4. **RE-ASK from s35, still open: does MON-CAP exist?** And **who owns `dc_sib_bt`** (returns rc=0 and
   prints a silently wrong answer)? This session found the same blind spot from a second angle: X01 is in
   the 5-REGRESSION set as "wrong-output, rc=0" — a by-set floor that grades on pass/fail cannot see this
   class at all, and **three of the five REGRESSION members are now known to be wrong-answer or
   hang rather than crash.** Every "floor held BY SET" claim in this file is only as good as that
   instrument.
5. **Credential** — asked, still needed; see the BLOCKED note at the end of this handoff.

### DATA EARNED THIS SESSION (recorded so nobody re-derives it)
**The 19 probes that ride the unguarded plain-frameless arm with `op_arbno_body_k0=0`:**
PASS (16): D09 D10 D11 G19 G20 H21 H24 H25 N12 N17 X02 X03 X04 X05 X06 X11 ·
FAIL (3): D12 (SEGV 139) D13 (hang 124) X01 (wrong-output, rc=0).
Reproduce: `SCRIP_ARBNO_DIAG=1 ./scrip --run <probe>` for the arm verdict + `k0=`; `diff` against `.ref`
for truth. **Every one of the 16 passers references a NON-recursive deferred pattern (`*P` where
`P=LEN(1)`) or no DEFER at all; D12/D13 alone reference a self-recursive one.** That asymmetry is the fix's
discriminator and the reason a blanket fix is wrong.

**Possible same-class link, still unconfirmed:** s35's escalated `dc_sib_bt` silent-wrong-answer bug is
also a CLASS-D + recursive/deferred-pattern intersection. Live suspicion, not traced — and it is question
4 below, still unanswered from last session.

### INSTRUMENT RULES EARNED (offered for RULES.md; both cost me real time this session)
- **Run the codebase's own diagnostic before reading its source by hand.** I misdiagnosed this bug as a
  `zd_k()` arithmetic error and wrote it up that way; `SCRIP_ARBNO_DIAG=1` — which already existed —
  showed in one command that `zd_k`/`k0` were correct and the dispatcher simply never consulted them. The
  finding needed a full correction pass. Cost: ~an hour. (This is the s34 rule extended: not just "run the
  gate script before hand-rolling a census," but "run the diagnostic before hand-reading the logic.")
- **Never compare multi-line program output with a shell `[ "$a" == "$b" ]`.** Embedded newlines break the
  test and it reports FAIL for everything — I briefly believed all 19 probes were failing, which would
  have inverted the entire fix decision. Use `diff`. Cost: one wasted round, caught only because the
  result was implausible.
- **Before narrowing or widening any classifier, sweep the corpus for who currently rides the path you are
  about to close.** The blast-radius number (16 passers) is what turned a "cheap conservative fix" into a
  measured regression. It took ~5 minutes and changed the answer completely.

### SESSION-SETUP NOTES (small, real, cost false starts)
- `bb_seal` lives in `libscrip_rt.so`, **not** the `scrip` binary — `break bb_seal` before `start` does not
  resolve (gdb's "pending on future library load" prompt reads like success). `start` first, then `break`.
- `gdb` is not preinstalled here. `apt-get install -y --no-install-recommends gdb` works; plain
  `apt-get install -y gdb` pulls `libc6-dbg`, which 404s at this image's snapshot and aborts the install.
- HW watchpoints still don't work in this container (RULES.md is right); **software watchpoints on a FIXED
  address do work fine** and were the whole trace. Watch a fixed address, never an `$rsp`-relative
  expression — the latter silently re-evaluates as the stack moves and reports meaningless hits.
- The mode-3 RX slab is stable across runs in this container (`0x7ffff1600000`+, one page per sealed
  graph), so breakpoints on emitted-code addresses survive re-runs — that made the trace much cheaper than
  expected.

---

## ⭐⭐⭐ LIVE CURSOR — 2026-08-12 (Claude Sonnet 5, continuation session) — RAW-BYTE HALF OF W-0 CLOSED + ONE DEAD-CODE LANDING

**SCRIP `825ab0a4` (one commit ahead of the session-start `05e6b1ae` — the dead cursor-mirror deletion below;
the raw-byte sweep itself touched ZERO compiler bytes, read-only) · corpus untouched, clean (first background
clone attempt raced and left an EMPTY checkout — `git log -1` inside it showed "No commits yet"; `ls` alone
would have missed this. Flagging for any session that clones in the background: verify with `git log`, not
`ls`.) · x64 not cloned.**

**RULES.md step 4 (`.s` regen ×3) WAS RUN** (the second landing touched `x86_asm.h`): benchmark/feature/demo
regen scripts all report "same"/"no changes" — zero artifact bytes moved, confirming the deletion is
runtime-invisible as predicted. Two PRE-EXISTING unrelated gaps noted in passing (`coverage_sno_nodes.s`
EMIT-FAIL, `json.s` SKIP) — both reproduce identically with the edit absent, not caused by this session.
m3 floor NOT re-measured beyond the 17-program targeted re-run (identical before/after); s35's by-set floor
stands unless a later seat re-proves it: **157 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}**.

### ⭐⭐⭐ THE RAW-BYTE/BINARY-MEDIUM SWEEP IS DONE — SEE `FINDING-2026-08-12j-…` FOR FULL METHOD + RESULT

The s35 cursor's top-priority open item — objdump the ACTUAL mode-3 runtime slab, not source bytes — is now
done. Method: `break bb_seal(buf,size)` in gdb, dump `[buf,buf+size)` before the RW→RX mprotect, `objdump -D -b
binary -m i386:x86-64` the real bytes. Run across 17 programs (CLASS-D/DEFER/ARBNO-defer/PT-inline surface,
named in the finding) → 46 sealed graphs, ~174KB of genuine emitted code.

**Result: exactly two mechanisms, no third.** Every r10/r11-touching instruction shape found (14 distinct,
normalized) is either CLASS-D wire glue (the already-licensed `emit.cpp` occ=6) or RTCC veneer
(writeback/reload/call-stub in `x86_asm.h`, NOT yet whitelisted but ALREADY VISIBLE to the text-grep gate as
sweep debt — the binary form confirms it executes as the source says, it doesn't hide a new surface). The
raw-byte blind spot the s35 cursor worried was "the highest-risk code, concentrated" turned out — empirically
— to contain nothing the source-level census hadn't already named.

**One concrete catch from the trace, ✅ NOW LANDED (`825ab0a4`):** `x86_asm.h:232-234`'s
`x86_store_cursor_mirror()` (emitted `mov [r10], r14d`, unrelated to the wire pair — a match-cursor-mirror
base pointer) and its `XK_R10MIR` decode arm (`:1426`) were **dead code — zero live callers anywhere in
`src/`.** The one caller that could reach it, `xa_flat.cpp:249`, deliberately writes `"[r10 + 0]"` instead of
`"[r10]"` specifically to AVOID this parse arm — its own comment says so. Deleted this session (4-site edit:
function, enum entry, decode arm, dispatch arm). Proof: `test_gate_em_template_byte_identity.sh` PASS=4 FAIL=0
before AND after · the same 17-program mode-3 sweep re-run byte-for-byte identical stdout+rc before/after ·
`test_smoke_compile_hello_all_langs.sh` PASS=6 FAIL=0 · all three RULES.md-mandated `.s` regen scripts run
(benchmark/feature/demo) — every artifact reads "same"/"no changes" (one PRE-EXISTING unrelated EMIT-FAIL on
`coverage_sno_nodes.s` and one PRE-EXISTING unrelated SKIP on `json.s`, both reproduced identically with the
edit reverted, so neither is caused by this change). `wreg_claim` gate: `x86_asm.h` 25 occ/17 lines →
**23 occ/15 lines.** This was independent of the whitelist-policy decision (deleting dead code doesn't need
a licensing call) — the remaining 23 occurrences (RTCC veneer + register-name infrastructure) still await
that decision.

**W-0 IS NOW DATA-COMPLETE ON BOTH HALVES (RTX 223/223 done s34 + raw-byte done this session).** The ONLY
thing left to close W-0 is decision (1) from the s35 cursor below — the whitelist-policy question. There is no
more sweeping to do; re-running either census is explicitly NOT owed.

### ⛔⭐⭐⭐ FOR LON — THE MOST IMPORTANT THING I SAW ALL SESSION IS **NOT** IN THIS SEAT'S LADDER

**`dc_sib_bt.sno` returns rc=0 and prints the WRONG ANSWER, silently.** m3 output is `=S / X= / Y=C / Z=CD`;
oracle `.ref` is `=S / X=AB / Y=C / Z=ABCD`. Exit code 0. No crash, no diagnostic, no stderr. I hit this
incidentally while picking a CLASS-D witness and did **not** chase it (out of W-0's scope, and MONITOR-FIRST
says the monitor owns it, not me reading code).

**Why I am escalating it rather than filing it quietly:** this is the exact class HOME GATE line 5 already
names as a known blind spot — *"Monitor sees the classes it has been dark on: stdout-only divergence
(MON-CAP)"* — and the s33 BOARD conviction (`FINDING-2026-08-12c`) proved a dead mode can look alive for two
days because failing probes still print non-empty output. **A by-set floor that grades on pass/fail cannot see
this defect at all.** Every seat's "floor held BY SET" claim, including the ones in this file, is only as
honest as the instrument's ability to notice a wrong-but-exit-0 answer. If `dc_sib_bt` is silently wrong at
HEAD and the boards still read green, then the boards are measuring less than everyone believes.

Concretely, three things I cannot decide from this seat:
1. **Is `dc_sib_bt` a known member of the 5-REGRESSION set {D12,D13,H31,X01,X10}, or a SIXTH nobody has
   counted?** I could not tell from this file — the set is named by probe ID, `dc_*` are named witnesses. If
   it is uncounted, the floor number is wrong, not just imprecise.
2. **Who owns it?** It smells like RBP/EARN's CLASS-D territory (capture/backtrack losing `X`'s and `Z`'s
   spans looks like a pending-cell restore defect, not a register-scope defect) — but that is a guess from the
   output shape, which is exactly the kind of guess MONITOR-FIRST forbids acting on.
3. **Does MON-CAP exist yet?** HOME GATE line 5 lists it as owed. If it does not, this defect class is
   invisible product-wide and MON-CAP outranks several rungs currently ahead of it.

I would rather hand you one loud honest anomaly than a tidy report that steps over it.

### ⛔⭐⭐ INSTRUMENT GAP THAT SURVIVES THIS SESSION'S WORK (and why "W-0 data-complete" is not "W-0 safe")

I closed the *census*. I did **not** close the *instrument*. `test_gate_wreg_claim.sh` is still a text-regex
over source, and my finding demonstrates by construction that a raw-byte emission (`ef_b4(0x4C, 0x8B, …)`)
greps to zero. **So `--strict` can go green while binary-medium r10/r11 code drifts underneath it.** Today
that is fine — I verified the binary surface by hand and it is clean — but the verification is a *snapshot*,
not a *ratchet*, and the whole point of the pinned-`occ=` mechanism elsewhere in this gate is that snapshots
rot. Two honest options, both cheap, neither mine to choose:
- **(A)** Build `scripts/test_gate_wreg_claim_binary.sh` from the gdb-dump-and-objdump method in the finding
  (fixed program set → dump slabs → disassemble → assert every r10/r11 instruction matches an allowlisted
  shape). ~an hour of work; makes the guarantee permanent.
- **(B)** Accept the snapshot, and write into the whitelist header that the binary medium is verified by
  FINDING-2026-08-12j at hash `825ab0a4` and must be re-verified by hand whenever the CLASS-D exit region
  (`emit.cpp` ~2680-2900) or the RTCC veneer encoders change. Free, but it is a promise a human has to keep.
⚠ Do **not** solve this by adding byte patterns to the existing regex: `0x41`/`0x4C` are REX prefixes shared
with many registers, so a byte-level source grep is pure noise. The instrument for the binary half is a
disassembler over OUTPUT, never a matcher over SOURCE.

### SECONDARY OBSERVATIONS (smaller, recorded so they are not re-discovered)

- **The gate counts a diagnostic string as a register use.** `x86_asm.h:318`'s occurrence lives inside a
  `static_assert` *message*, not in emitted code. One of 23 — harmless to the total, but if `--strict` ever
  reads 1 and someone hunts it, this is where it will be. Comment-stripping does not strip string literals.
- **SESSION-SETUP HAZARD, cost me two false starts:** a backgrounded `git clone` that has not finished leaves
  a directory that `ls` shows as *present* and `git status` reports as *"No commits yet"* on an empty branch.
  Both `SCRIP` and `corpus` came up empty this way and I nearly worked against a phantom tree. **Verify clones
  with `git log -1`, never `ls`** — and prefer foreground clones. Worth a line in RULES.md session-setup if
  other seats are hitting it.
- **Method note that earned its keep:** my own 23-occurrence classification table was WRONG TWICE (summed to
  22, then 21) before a mechanical `awk | uniq -c` per-line recount fixed it. The sum-check caught what
  careful reading did not. Any future per-occurrence table in this seat should carry an explicit arithmetic
  check line — cheap, and it converts a silent miscount into a visible one.
- **W-5's unblock may be further out than this file implies.** I checked `.github` HEAD this session: the RBP
  seat's newest commit is an *s38 FIX PLAN for floor stabilization*, not EARN-1. `frame_need_of` still exists
  nowhere in `src/`. Do not schedule around W-5 landing soon.


### NEXT SEAT, IN ORDER

1. **⛔ FIRST, IF IT IS STILL UNANSWERED: W-0b (Lon's decision).** Nothing else in this ladder is cheaper, and
   until it is answered W-0 cannot close no matter how much work anyone does. If it IS answered, closing W-0
   is one whitelist line + `--strict`, ~10 minutes.
2. **Route the `dc_sib_bt` silent-wrong-answer** (see the FOR LON block above) to whoever owns MON-CAP / the
   floor instruments — BOARD by the seat table. Do not chase it from this seat; do not let it sit unrouted.
3. **W-6** — re-entrant `g_rtcc_block`. Leaf half PROVEN SAFE (s35: 172 veneered, 0 bare match-time), scope is
   re-entrant ONLY, witnesses named (`140`/`141`). **This is the largest genuinely-available piece of
   mechanism work in this seat** and it does not depend on W-0b or on the RBP seat. If you are a fresh seat
   with a full runway and W-0b is unanswered, start here, not at the top.
4. **W-3/W-4** — mechanism dormant but ALREADY WRITTEN (`bb_glue_pass_wires_blob` in `bb_glue_flat.cpp:154-159`);
   W-4's layout must cover BOTH carry shapes named in the s35 CARRY SHAPES block below, not just "crosses a call."
⛔ **Do NOT re-derive any census — RTX (223/223), templates, W-2's glue files, the raw-byte/binary medium
(46 slabs), and `x86_asm.h` (23/23) are ALL mapped.** What is missing is decisions, not data.
⛔ **W-5 stays blocked and this seat cannot unblock it** — `frame_need_of` is a forward reference the RBP seat
must create; re-checked this session, still absent from `src/` under every spelling. Check EARN's cursor, not
`src/`, and see the W-5 note in SECONDARY OBSERVATIONS above.

---

## ⭐ LIVE CURSOR — 2026-08-12 (Claude Sonnet 5) — RTX CENSUS COMPLETE + W-2 CENSUS COMPLETE + A GATE HOLE FOUND

**SCRIP `2913c6a4` (UNCHANGED — read-only session, ZERO compiler bytes) · corpus untouched · x64 not cloned.**
**No codegen touched ⇒ RULES.md step 4 (`.s` regen ×3) DOES NOT APPLY this session** — stated explicitly so
the next seat doesn't re-run it looking for skipped work. m3 floor NOT re-measured (nothing could have moved
it); s35's by-set floor stands: **157 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}**.

### ⛔⭐⭐⭐ NEW AND MOST IMPORTANT — THE CLAIM GATE IS BLIND TO THE BINARY MEDIUM, IN THE WIRE CODE ITSELF

`test_gate_wreg_claim.sh` matches TEXT spellings (`r10`, `[r10 + 8]`, `r10d`, …). **Every BINARY-medium
emission of r10/r11 is a raw byte tuple and greps to ZERO.** This is not hypothetical — it is live in the
CLASS-D blob wire path, i.e. exactly the code WREG is about. Four sites, all in `emit.cpp`, all invisible:

| Line | Bytes | Decodes to | TEXT twin (which the gate DOES count) |
|---|---|---|---|
| `:2689` | `4C 8B 54 24 08` | `mov r10,[rsp+8]` | `:2688` |
| `:2690` | `4C 8B 5C 24 10` | `mov r11,[rsp+16]` | `:2688` |
| `:2724` | `41 53` / `41 52` | `push r11` / `push r10` | `:2721` |
| `:2726` | `41 FF E2` | `jmp r10` | `:2722` |

**CONSEQUENCE:** the headline "222 template/emitter + 223 RTX = 445" is a FLOOR, not a total, and the
undercount is concentrated in the highest-risk code. The rung's own text already demanded this
("grep is insufficient — **objdump the emitted slab too**") and no session has done it. **This is now the
single most valuable unopened piece of W-0**, and it is cheap: `objdump -d` the emitted slab (or the
`.s` artifacts for the TEXT side) and decode, rather than growing the regex — a regex over C source can
never see a byte tuple that is assembled at runtime.
⚠ Do NOT "fix" this by adding byte patterns to the gate: `0x41` and `0x4C` are REX prefixes shared with
many other registers, so a byte-level source grep would be noise. The instrument for this half is a
DISASSEMBLER over output, not a matcher over source.

### ⭐⭐⭐ RTX HAND-ASM CENSUS: COMPLETE — 223/223, ALL 10 FILES

Full per-file tables + method: `FINDING-2026-08-12h-…` (8 addenda). Headlines:
- **193/223 (86.5%) SN4-reachable** — `rtx_match.S` 89 · `rtx_icnsub.S` 33 · `rtx_alloc.S` 20 ·
  `rtx_str.S` 19 · `rtx_icnvar.S` 13 · `rtx_arith.S` 9 · `rtx_icnnum.S` 11.
- **30/223 (13.5%) confirmed excused** — `rtx_plcall.S` 10 · `rtx_icnagg.S` 11 · `rtx_icnrel.S` 8.
- **6 idioms cover everything, no 7th:** momentary GOT accessor · GOT-indirect call/tail-call ·
  loop-carried pointer/scalar (capture-stack, hash-chain, field-scan) · longer-lived same-function carry ·
  local scalar (branchless sign / dispatch selector / index) · explicit stack-spilled preserver.
- **Σ/r13 question RESOLVED** (was flagged as s35's "sharpest next question"): not a contract conflict —
  `rt_match_ctx_restore`'s own header states the two-copy design (r13 = hot-path pin; GOT-global Σ/Σlen =
  C-readable mirror for slow paths and cross-TU C that cannot see a register pin). Close that item.
- ⭐ **METHOD RULE EARNED (fold into W-0's statement):** filenames, gate-ledger rung names ("RTX-N-ICN"),
  and a header's own measurement framing were EACH shown wrong at least once. **Three of five "icn"-named
  files were SN4-reachable.** The only trustworthy check is per-file: (1) find the symbol's caller in
  `src/templates/`, (2) identify the IR node kind that call site is gated on, (3) grep EVERY `lower_*.c`
  for who emits that kind, (4) check the optimizer for kind-rewrites. Cheap, mechanical, and it caught
  three errors that a name-based read would have shipped.

### ⭐⭐ W-2 CENSUS: COMPLETE — AND IT CHANGES THE RUNG'S PREMISE

`FINDING-2026-08-12i-…`. Both `bb_glue_*.cpp` read in full: **they contain no r10/r11 push/pop at all** —
the code is raw literals in `emit.cpp` (TEMPLATE-ONLY violation, pre-existing, and the whole CLASS-D/P/ZF
exit-glue region ~`:2680-2900` is written that way, not just this pair). The named asymmetry (pop guard
`flat_pat` broader than push guard `_blob_wire`) **traces as structurally unreachable**: `lbl_res`'s
address is taken at exactly one site, inside the `_blob_wire` branch itself, so the pop arm cannot be
entered without the push having run. **Grep-traced, NOT monitor-verified** — see the FINDING for exactly
what a live check would need.

### ⭐ CARRY SHAPES W-4's LAYOUT MUST COVER (named by the census; do not design against "crosses a call" alone)
1. **Carve/copy carry** — `rtx_str.S:165-207` (`str_concat_d`): r10=buf, r11=len live from just after ONE
   `rt_str_alloc` call through to `ret`, ~42 lines. Recurs in `rtx_match.S`'s `rt_cap_open` and
   `rt_match_replace`. A save-at-every-call-boundary scheme clobbers this.
2. **Explicit-frame preserver** — `rtx_plcall.S` cold growth arm: r10d spilled to `[rbp-24]` and restored
   around `call rt_pcall_grow`, via a frame slot rather than push/pop. A push/pop-shaped scanner misses it.

### ⛔⭐⭐⭐ FOR LON — FOUR DECISIONS, IN PRIORITY ORDER

1. **W-0 whitelist policy (open since s35, NOW WITH EXACT NUMBERS).** Does "product-wide" require clearing
   r10/r11 regardless of reachability? Data: 193/223 RTX occurrences are SN4-reachable and cannot be
   excused either way; only 30/223 are genuine licensing candidates. Plus `wreg_claim_whitelist.txt`'s
   header defines FOUR site-classes, all "code that legitimately OWNS the wires" — "unreachable for the
   graphs this gate protects" fits none, so licensing them is a real registry-policy edit, not a checkbox.
   **This is still the decision that unblocks the rest of W-0.**
2. **The raw-byte/binary-medium blind spot (NEW).** Is closing it W-0's job this rung, and is an
   objdump-based instrument sanctioned? It is the last unopened part of the rung's own charter text.
3. **W-2's two halves.** (a) Is the reachability argument enough to close the pop-guard question, or does
   MONITOR-FIRST require a runtime witness first? (b) Is migrating the raw-literal asm at `:2680-2900`
   into templates in scope for W-2, or a separately-tracked TEMPLATE-ONLY debt? The rung's charter says
   only "guard unification," so I did not assume the larger job.
4. **s35's process flag still stands and I could not verify it is resolved:** two live sessions shared this
   seat file on 2026-08-12 (the ONE INVARIANT break). Worth confirming how WIRES got re-fired.

### NEXT SEAT, IN ORDER
1. **Raw-byte/binary-medium sweep** (objdump the slab) — cheapest high-value item, closes W-0's last third.
2. **W-6** — re-entrant `g_rtcc_block` (leaf half already proven; witnesses `140`/`141` named).
3. **W-3/W-4** — mechanism is dormant but ALREADY WRITTEN (`bb_glue_pass_wires_blob`); W-4's layout must
   cover both carry shapes above.
4. **W-0 sweep proper** — blocked on decision (1) above, not on more data.
⛔ **Do NOT re-derive any census.** RTX (223/223), templates (s33/34/35), and W-2's glue files are all
mapped. What is missing is decisions and the raw-byte half.
⛔ **W-5 stays blocked and this seat cannot unblock it** — `frame_need_of` exists nowhere in `src/` under
any spelling; it is a forward reference `GOAL-RBP-EARN.md` must create. Check EARN's cursor, not `src/`.

---


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
3. **W-2** — [⛔ FALSIFIED s36 — historical text kept for provenance only; D12/D13 are an ARBNO dispatcher bug, not a guard bug] census `bb_glue_*.cpp` for asymmetric push/pop; ONE predicate both media; witness D12/D13 flipping green.
4. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block` (per-activation spine, not flat block).
5. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.
- **Do NOT re-derive the W-0 template census a fourth time.** Between FINDING-12f (structural), FINDING-12g (reachability), and FINDING-2026-08-11d (the ERAD ladder), the template surface is mapped. What is missing is RTX and a policy decision, not another count.

**UNBLOCKS: nothing new** (W-5 predicate still FALSE: `frame_need_of` grep still empty, re-checked s35).

---

## LIVE CURSOR — 2026-08-12 (Sonnet 5) — ⛔ SUPERSEDED by the TOP cursor (census finished 10/10, not 2/10). Retained per STALE-ORIENTATION (c) for provenance only; its counts are STALE BY DESIGN.

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

### NEXT SEAT, IN ORDER (supersedes the s35 list above for items 1-2) — RTX CENSUS 100% COMPLETE (223/223)
1. **W-0 register-reassignment design call for the 193 SN4-reachable RTX occurrences** — the RTX
   census is DONE (see the top-of-section marker above and `FINDING-2026-08-12h-…`'s final
   summary table). What's needed now is a replacement-register or preservation-mechanism decision
   per idiom, not another count.
2. **W-2** — [⛔ FALSIFIED s36 — historical, provenance only] census `bb_glue_*.cpp` for asymmetric
   push/pop; ONE predicate both media; witness D12/D13 flipping green.
3. **W-6** — nested-crossing witness with probe `140`/`141`; then fix re-entrant `g_rtcc_block`.
4. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout. **Account for two named
   risk shapes found during the census:** the "carve/copy carry" (`rtx_str.S`'s `str_concat_d`:
   r10/r11 carry a fresh buffer pointer + length across exactly one `rt_str_alloc` call, ~42
   lines, then die at `ret` — recurs in `rtx_match.S`'s `rt_cap_open`/`rt_match_replace`) and the
   "explicit-frame preserver across a call" (`rtx_plcall.S`'s cold growth arm, r10d spilled to
   `[rbp-24]` rather than pushed).
5. **⭐ W-0 whitelist-policy question (s35's OPEN QUESTION) — NOW ANSWERABLE WITH EXACT NUMBERS:**
   193/223 (86.5%) of RTX occurrences are SN4-reachable and cannot be excused either way the
   policy is decided; only 30/223 (13.5%) are genuine reachability-licensing candidates. This is
   the decision that unblocks the rest of W-0 (unchanged from s35's framing, now with real data).

⛔ W-5 REQUIRES (predicate): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND
`UNBLOCKS: WIRES W-5` on origin. Still FALSE, unchanged this session.

**UNBLOCKS: nothing new** (RTX census is a sub-item of W-0, not a rung boundary by itself, but it
is now a COMPLETE sub-item rather than a partial one).
**PROGRESS: RTX CENSUS 100% COMPLETE — 223 of 223 occurrences classified across all 10 RTX `.S`
files. See top-of-section marker and `FINDING-2026-08-12h-…` for full detail.**

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
`corpus/probe/bb/run_suite.sh` (NOTE: this is `corpus/probe/bb/`, NOT `SCRIP/scripts/` — the master's instrument map path is wrong): **159 pass · 1 xfail · 5 REGRESSION {D12, D13, H31, X01, X10} — NOT BASELINED (`XFAIL.run` = `fence_probe` only).** ⭐ Updated s37 (was 157 at s36; LOWER's L-3b added 2 unrelated probes). Any seat will see these 5; hold by SET, never count.

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
3. **W-2** — ⛔ SUPERSEDED s36: rung falsified (no defect, no witnesses — D12/D13 are an ARBNO bug). See the s36 cursor's rung note; disposition decision owed from Lon. Do NOT chase "D12/D13 flipping green" here.
4. **W-6** — nested-crossing witness with probe `140`/`141`; then fix the re-entrant `g_rtcc_block` case (per-activation spine, not flat block).
5. **W-3/W-4** — WREG mechanism (dormant, killswitched) + arena layout.

⛔ W-5 REQUIRES (predicate): `grep -rn "frame_need_of" /home/claude/SCRIP/src/` non-empty AND `UNBLOCKS: WIRES W-5` on origin. Currently FALSE — skip to W-6 or POOL.

**UNBLOCKS: WIRES W-6** (leaf half proven, scope narrowed to re-entrant case only).
