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
