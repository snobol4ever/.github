# FINDING s145/B2 — THE BEAUTY CRASH IS MINTED: CAPTURE-INTO-DEFERRED-CALL BRACKETS AROUND AN ARBNO KILL
# BOTH MODES. 12-LINE WITNESS, NO BEAUTY, NO INCLUDES, LIVE-ORACLE GREEN.

**Session:** 2026-08-19 s145 HQ (Fable 5). Witness `corpus/probe/m1/m1_arbno_capture_call_bracket.{sno,ref}`.

## THE WITNESS (oracle: `nomatch`; SCRIP m3 SIGILL rc=132; SCRIP m4 SIGSEGV rc=139)
```
	DEFINE('PC()')	:(PCe)
PC	PC = .d	:(NRETURN)
PCe	nP = '' . *PC()
	C = 'x'
	P = nP ARBNO(*C) nP
	Src = 'START'
	Src POS(0) P RPOS(0)	:S(Y)F(N)
```
The shape is beauty's `Parse = nPush() ARBNO(*Command) … nPop()` distilled: `nPush()` returns
`epsilon . *PushCounter()` (semantic.inc:20) — a null-width match whose CAPTURE TARGET is a DEFERRED CALL
(NRETURN-name; the side effect fires at MATCH time). Two such brackets around a deferred-body ARBNO in an
anchored match that must fail-and-backtrack ⇒ control transfers into non-code.

## HOW IT WAS REACHED (the trace chain, each step measured)
1. ζ-SM (`SCRIP_ZSM=1`) reads **silent to the death** — zero port violations; not a frame-discipline breach
   the SM can see. (s141's zero-violations reading was honest.)
2. gdb at the fault: **si_addr == RIP == `0x7fffee203000` == the RX slab's exact end** (`r-xp` boundary);
   preceding bytes all `00` — execution SLID THROUGH never-written zeros off the mapping. Stack carries blob
   resume-record-shaped cells + a REAL return into `zls_g_region+28` (libscrip_rt).
3. That frame is real, not noise: mode-3 compiles thunks in-process. ⛔ CORRECTS FINDING-…-two-walls-named §5
   ("bt unreliable / beauty does no runtime compile") — beauty DOES reach runtime compilation: my "no EVAL"
   grep had silently run in the wrong cwd (ENOENT ≠ absence; the same cwd class as the sweep-tool slip).
   `semantic.inc` EVALs at build; the `*PushCounter()`-class THUNKS fire at match time.
4. Five-level ablation of beauty itself (all with input = one line `START`): *Parse replaced ⇒ clean · root
   `nPush() nPop()` (no ARBNO) ⇒ clean · root with `ARBNO(*Command)` ⇒ SEGV regardless of the reduce-`&` term ·
   `Command = nInc()` ALONE still crashes · **bare `ARBNO(*Command)` root (brackets removed) ⇒ CLEAN for every
   Command body.** The brackets, not the body.
5. Standalone reconstruction from semantic.inc's mechanics ⇒ the witness above, first try.

## ⛔ CORRECTIONS TO THE STANDING RECORD
- **"B2 is m3-only" is WRONG.** The witness kills BOTH modes. In beauty, m4 stops earlier: its `*Parse` match
  FAILS CLEANLY (wall B1 → `Parse Error`, exit 0) before the crash path arms; m3's match reaches the crash.
  The walls are SEQUENTIAL (B1 masks B2 in m4), not mode-parallel.
- The `zls_g_region` frame was evidence, not noise (item 3).

## ALSO IN THIS SESSION-SLICE
CN-2 behavior A/B verdict (6 suites × 2 arms, 913 rows/arm): 3 movers — the new cn witness RC1→PASS
(intended), `dc_nest_bt` and `leafsib_break` red→red signal shuffles. **Zero green→red: the &-seal and
canonical &-keys are corpus-safe.**

## NEXT (HQ)
Fix design for the bracket class: the `'' . *Fn()` thunk's match-time activation + the ARBNO retreat crossing
its record — route through the s121–s127 defer/resume machinery laws (the admitted af edge vs an
activation-pushing capture-call record; the witness's m4 `.s` is now the ASM-DIFF-FIRST substrate — diff
against the bracket-free sibling). This is squarely the ζ/defer territory Lon assigned to HQ.

## ⭐⭐⭐⭐⭐ MECHANISM CONFIRMED AT INSTRUCTION LEVEL (HQ, same day, post-ownership ruling)
**Killswitch bisect:** default rc=132 · `SCRIP_ARBNO_TAILBETA=0` rc=132 (**the s145 tail-beta rung is exonerated**) · **`SCRIP_DEFER_RESUME=0` rc=0 `nomatch`** · **`SCRIP_SEAM_WALK=0` rc=0 `nomatch`** — B2 is armed by the s121/s124 resume pair, and both cured arms are oracle-correct on the witness.
**ASM-DIFF (witness vs bracket-free sibling, mode-4 text):** the witness's statement graph carries the brackets as `match_defer` nodes whose **β labels are `jmp qword ptr [rsp]`** — the CLASS-D record resume — and the retreat edges from the failing right side (`RPOS` fail, ARBNO σ/af) β-target exactly those labels. But `'' . *PC()` **completes deterministically without suspending** (ε-match, call fires, capture lands, success) — no suspension record is ever pushed — so at retreat time `[rsp]` holds unrelated stack data: m3 slides into slab zeros (SIGILL/SEGV at the RX edge), m4 jumps through junk (SIGSEGV). s121's own gate text predicted the class ("a deterministic carrier's β fail-throughs home"); the statement-graph wiring assumed record-entry is always valid — false for completed-unsuspended defers.
**FIX DESIGN (HQ, to land next slice with full gates):** THE RECORD CELL MUST ALWAYS CARRY A VALID CONTINUATION — bb_match_defer's completion path arms its own record slot with the FAIL-THROUGH continuation (its ω/fail glue) whenever it exits WITHOUT publishing a suspension; the suspension path keeps writing the resume stub as today. Then `jmp [rsp]` is correct in every state, no admission-gate re-narrowing needed, and the s121 arbnostore repairs are untouched (they enter genuinely-suspended records). Killswitch + byte-identity + 529 sweep + arbnostore 10/10 + beauty both modes = the gate set. Alternative rejected: re-narrowing the SEQ-RESUME-GATE at lower time cannot see whether a blob will suspend (runtime fact) — it would re-break the repaired arbnostore class or under-fix this one.

## ⭐⭐⭐⭐⭐ THE CURE, PROVEN BY HAND-PATCH (HQ, same day) — AND THE OWNER, NARROWED TO ONE SEAM
**One instruction fixes the witness:** rerouting the arbno-af ω fall-through (`jmp n9_match_defer_β`) through a stub
that does `add rsp, 16` first makes the witness run ORACLE-PERFECT (`nomatch`, rc=0). The depth delta is exactly
one 16-byte cell.
**Owner accounting (read off the witness .s):** the leaked 16 is the RIGHT bracket's (n11's) **generic-emitter
α-carve** (`sub rsp,16` at `n11_match_defer_α` — NOT emitted by bb_match_defer.cpp; it is the ζ-carve from the
generic per-node staging). n11's γ pushed the 16-byte {L(6)-stub, cursor} record; RPOS failed; n11's β
record-resume ran L(6), which frees ONLY the record (`add rsp,8; pop rax`) and ω-exits **with the α-carve still
on the spine**; the arbno's af then enters the LEFT bracket's `jmp [rsp+0]` 16 bytes short of its record. The
blob-side twin stub (`.Lx13_6`) frees all 32 (8+8+16) — the statement-side L(6) is the one that under-frees.
**THE FIX (next HQ slice, scoped):** the defer's exhaust/ω path must free what its α carved (THE MODEL: "ω
self-frees on failure") — land it at the L(6) stubs (both `sn4_alt_carrier()` arms) as the carve-release,
gated by whether the generic staging carved for this node (the zd_k/op-carve fact must be read from ONE
authority, not re-derived in the template), killswitch, default per Lon's blanket grant. ⛔ The naive
alternative — popping at the arbno-af edge — is WRONG by construction: the delta is a property of the
LEAKING NODE's exit, not of the af edge (depth-clean bodies would be over-popped; arbnostore 10/10 rides
those edges).
**Gate set at landing:** witness green BOTH modes · arbnostore 10/10 · cn 5/5 · KW armed 6/10 · 529 sweep both
arms · patterns+crosscheck behavior A/B · **beauty m3 re-run** (if the leak is beauty's B2, m3 stops crashing
and joins m4 at wall B1 — one front left).

## ⛔⭐⭐⭐⭐⭐ MECHANISM CORRECTED — THE REAL DEFECT IS THE SHARED-BLOB HARDWIRED β LANDING (HQ, supersedes the "L(6) under-frees" hypothesis above)
Deeper read of the witness .s exonerates the stubs: n11's L(6) frees all 32; n12's fast path is carve-neutral;
the blob's CLASS-D record is `{res-stub@+0, r10@+8, r11@+16, rbp@+24}` (the WIRE-ORDER discipline, ascending)
and `PAT$1_res` restores wires+frame and pops 32 — balanced. **The defect: `PAT$1_β` then executes
`jmp n11_match_defer_β` — a SINGLE HARDWIRED SITE LANDING — while the stored pattern nP is SHARED by TWO defer
sites (n9 and n11).** An n9-origin retreat (`af → n9β → jmp [rsp] → PAT$1_res`) restores n9's OWN wires from
its record, then gets thrown at n11's β anyway; n11β re-executes `jmp [rsp]` at consumed-record depth →
garbage → the slab-zero slide / m4 junk jump. The earlier +16 hand-patch cured the WITNESS by accident of
layout, not by principle — do not land it.
**THE FIX (exact):** the post-`PAT$1_res` continuation must ride the RESTORED WIRES (or a site cell carried in
the record), never a hardwired site label — the emitter's blob-β landing selection (the s121 half-B2 dispatch
region, emit.cpp ~3257 + the PAT$ β publication) must emit the return-through-r11/r10 form (or per-site res
stubs) for MULTI-SITE blobs. Single-site blobs are unaffected, which is why arbnostore (single-site witnesses)
stayed green through s121–s125. **This also makes B2 a WIRE-ORDER citizen: the record layout was right; the
landing violated the protocol. D-14's canary would have caught this class (wires restored ≠ site entered).**
**Beauty tie-in:** beauty's brackets are nPush()/nPop() — TWO DIFFERENT stored patterns, each single-site… but
its grammar re-uses stored patterns at many sites (*&Space at two sites in beauty_c, `*Space` twice in classic
main05/611) — the multi-site class is exactly beauty-shaped.

## ⛔⭐⭐⭐⭐ FIX CAMPAIGN, SLICE 1 — TWO SHAPES FALSIFIED, THE CONFOUND NAMED, THE DESIGN NARROWED (HQ, end of s145)
**The confound first (it voids part of HQ-23):** every HEAD-based measurement in this hunt after s148 was
CONFOUNDED BY KW-3b — re-baselined at the green parent `bc0eeff4`: witness rc=132 and **arbnostore 10/10**
there, while at HEAD arbnostore reads **0/10** and every capture-call probe hits a NEW `SNO$MKPAT: compiled
pattern blob '' not registered` wall. ⛔ **KW-3b's blast radius therefore includes the ENTIRE stored-pattern
class (arbnostore 10→0) and a pattern-registration corruption (empty blob names) — the D-3 repair brief is
now URGENT and its gate set must include arbnostore 10/10 + the MKPAT wall's disappearance.**
**Live trace (m4 + symbols, the decisive instrument):** the retreat cascade is `stmt-β → PAT$1_res →
n11β → [rsp]=PAT$0_res (the INNER thunk blob's record — consumed correctly) → … → n9β → [rsp] = 0x0 →
jmp 0 = the SIGSEGV`. All labels/depths measured, not inferred.
**Falsified shape #1 (blanket zero-guard → node-ω):** generalizing the s153 zero-guard to every record-resume
β cures the jump-through-zero BUT its zero-arm exits via `x86_omega()` at the CURRENT (arbitrary) depth —
measured on the CLEAN base: arbnostore 10/10 → 8/10, and the witness still dumps core via another path.
Reverted. The s153 arm works only because its `zrelease` is that class's exact depth correction.
**Falsified shape #2 (the +16 af pop):** already voided above — accident of layout.
**THE NARROWED DESIGN (next slice, on the clean base):** the zero-cell continuation must be DEPTH-IMMUNE —
the match's ABSOLUTE unwind (the `mov rsp,rbp`-family fail tail owned by MATCH_BEGIN/ζ-STANDING), not the
node's ω; and the residual crash path on the witness (still core-dumping with the β guarded) must be traced
with the same m4-symbol-gdb workflow before any further emission change. Work happens on a `bc0eeff4`-based
branch until the D-3 repair restores a clean HEAD.

## ⭐⭐⭐⭐⭐ THE FIX DESIGN, COMPLETE (end of s145 slice 2 — ready to implement, no open questions)
The depth-immune continuation EXISTS in every emitted match already: `match_begin_β` opens with
`lea rsp, [rbp + -56]` — the retry_whack, an ABSOLUTE rsp restore off ζ-STANDING — then runs the
bump/retry/fail logic. The zero-arm must land exactly there. Mechanism (all existing machinery, zero RTX
changes, zero frame relayout):
1. **bb_match_begin** registers ONE ζ-STANDING slot via the s86/s87 unified frame-slot registry
   (`frame_slot_scan` / the `capture_frame_slot()` idiom) — the MATCH-β CONTINUATION SLOT — and at α stores
   its own β address into it (`def L(k)` placed at the β entry + `x86_lea_id("rax", k)` + `mov [rbp-slot], rax`;
   both idioms already exist in the template layer).
2. **bb_match_defer's record-resume β** becomes the s153-shaped guard, generalized: `mov rax,[rsp+0];
   test; jne resume; mov rax,[rbp-slot]; jmp rax` — zero ⇒ jump to the match's β THROUGH ζ-STANDING (rbp is
   pinned for the match's life, so this is depth-immune where the falsified node-ω arm was not).
3. Killswitch `SCRIP_DEFER_BETA_GUARD` (default ON per Lon's autonomy grant), `=0` = raw `jmp [rsp]`
   byte-identical.
**Gate set:** witness green BOTH modes (expect `nomatch` — no MKPAT wall on the clean base) · arbnostore
10/10 (the falsified arm's 2 losses must NOT recur — the whack replaces the depth-wrong ω) · cn + kw armed ·
529 both arms · patterns+crosscheck A/B · **beauty m3** (join m4 at B1 = the payoff) · regens ×3.
**Residual to trace during implementation:** the guarded witness still core-dumped once on the clean base —
re-trace with m4 symbols AFTER the whack-arm lands (the ω-at-depth arm may itself have caused the residual).
Work on branch `hq-b2` (based `bc0eeff4`) until the D-3 KW-3b repair restores a clean main.

---

## ADDENDUM 5 — s150 (HQ): THE PRISTINE RE-GATE AND THE LANDING (2026-08-19)

B2a is ON MAIN: `d9f5cf24` (rebased onto `6d0fd9c3`; the two commits between the branch base and the landed tip touch ZERO src/ files, so the gated driver sources are the landed ones byte-for-byte). Every arm measured from `rm -rf /tmp/si_objs out && make` per HQ-27's PRISTINE-BUILD-BEFORE-VERDICT law.

- **G1 (guard=0 identity)**: 0 movers / 527 comparable (rc-recording sweep, s149 instrument). The killswitch is honest.
- **G2 (guard ON — the default)**: blast radius 375/527 .s movers — the expected every-match-frame class (half A stores the continuation cell in EVERY match frame carve).
- **G2 behavior (all ON)**: arbnostore 10/10·10/10 · cn 8/8·8/8 · m1 family 47/53 m3 · 46/53 m4 — row-for-row identical to the pristine-main baseline; kw `--armed` 10/14 with exactly the two routed reds; udc 12/12; oracle arbno witnesses 16/16 both modes; demo-dir outputs byte-identical OFF vs ON; beauty m3 SEGV in BOTH arms with byte-identical 259-byte output.

The witness `m1_arbno_capture_call_bracket` still reads SIG4 m3 / SIG11 m4 in BOTH arms: **B2a alone cures nothing measured and harms nothing measured** — consistent with, and only with, the B2b mechanism (the guard's escape path is correct only under ζ-STANDING rbp; under blob/defer ACTIVATION rbp, [rbp-48] is not the continuation and the escape jumps through garbage — the measured rip=0x100000002 class — the same crash the unguarded `jmp 0` gave). B2b is the remaining wall: frame-chain continuation copy vs layout-aware slot, FRAME-LAYOUT CENSUS FIRST (`scripts/test_census_rbp_frames.sh`), then re-run the witness and beauty m3.

---

## ADDENDUM 6 — s155 (HQ): B2b LANDED (`a075a0b1`) — THE MBC CELL. THE m4 WITNESS IS GREEN FOR THE FIRST TIME, AND beauty-m4 RUNS CLEAN TO B1.

**Anatomy (gdb, pristine tip, guard ON):** the β-site trace read n55β (standing rbp, live record, pass-through) → n11β (ζ-FRAME activation rbp `0xe068`, live record, pass-through) → **n9β (same activation rbp, ZERO record → guard FIRED → `jmp [rbp-48]` = a libscrip_rt DATA address → executed .so bytes until a stray RET hit rip=0)**. The standing frame's own [rbp-48] held exactly the published L13 (disassembles as the retry_whack) — half A works; the ESCAPE's rbp assumption was the whole defect.

**Falsified en route:** (1) CAS-mark equality discriminator — r12 is the arena CURSOR and advances past the saved mark mid-match (measured: r12=…060 vs mark=…030). (2) Every frame-chain scheme — ζ-FRAME carves 40 bytes ([rbp-48] is not a slot there; writing it at the prologue is clobbered by the first push), ARBNO-FRAME has rbp-at-bottom geometry with caller-rbp at [rbp+24], and a child cannot know its parent's class.

**The fix (half C):** `rtccb[31]` = RTCC_MBC_QUAD (claimed in rtcc.h §RC-6) — the innermost LIVE mrbp match's L13. MATCH_BEGIN α saves the outer value into the [rbp-48] borrow and publishes its own; restores at BOTH match exits — begin's L(1) fail tail (abort-class escapes route through it per bb_match_fence1's E-1 note) and `mend_bank_cursors()` (runs after x86_alpha() on every real MATCH_END arm; restore-before-bank in one authority). Guard escape: load MBC → test → je raw-resume → `jmp rax`; pass-through stays FLAGS-only (TOUCH-NOTHING held); MBC==0 falls through raw (legacy `SCRIP_MATCH_RBP=0` world — a GLOBAL env, so mixed-arm builds cannot exist). Same killswitch, all sites.

**Measured (pristine ladder):** TRUE G1 identity `b2b@0 ≡ main@0`: **0 movers / 527** (worktree-built baseline). Blast ON: 375/527 — the every-match-program class, expected (halfA reshape + escape + end restore). Probe board 54 rows: m3 48/54 · m4 48/54 — zero green→red; m4's +1 IS the witness (`SIG11 → "nomatch" rc=0`). Oracle arbno 16 rows green, kw --armed = exactly the two routed reds, udc 12/12. **beauty m4: SEGV-era → rc=0 clean run** emitting the full 7-line header then `Parse Error` + `START` — B1 verbatim, now beauty-m4's ONLY wall.

**⛔ BASELINE-ARM LAW (minted here, cost one false alarm):** once a killswitch ships ON in main, an identity gate must compare SAME ARMS — `branch@0` vs `main@0`, never `branch@0` vs `main@default`. The first sweep read 375 "movers" that were merely B2a's own ON-arm on the main side; three distinct md5s per program (main@ON ≠ branch@0 ≠ branch@ON) is the telltale.

**The m3 twin (NEXT, B2c candidate):** witness/beauty m3 crash at BOTH arms incl. guard=0 — pre-existing, and the crash SIGNAL drifts across trees (SIG4 → SIGSEGV), which fits the hypothesis: m3 runs on the driver's DIRTY stack, so never-written spine quads are NOT zero — the zero-test is powerless there (an m4-ism: fresh stack pages read 0). Candidate fix: CARVE-ZEROING — each defer α's reserved record quads explicitly zeroed at carve, making "virgin == 0" deterministic in BOTH media. Gated, priced (hot-path stores per defer α), then the guard covers m3 too.
