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
