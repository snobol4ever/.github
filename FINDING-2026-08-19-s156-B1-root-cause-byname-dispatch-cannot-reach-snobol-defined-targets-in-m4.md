# FINDING 2026-08-19 s156 (HQ) — B1 ROOT-CAUSED: m4's BY-NAME DISPATCH CANNOT REACH SNOBOL-DEFINED TARGETS. BEAUTY'S "Parse Error" IS TOTAL, AND THE OPSYN-GRAMMAR THEORY IS DEAD.

## THE WITNESS (minted: `corpus/probe/b1/b1_opsyn_binary_snodef.sno`, 7 lines)
    DEFINE('RED(A,B)') ... RED = A '+' B ... OPSYN('&', 'RED', 2) ... X = 'l' & 'r' ... OUTPUT = X
- **oracle (sbl)**: `l+r` · **m3**: `l+r` · **m4**: EMPTY, rc=0 — silent statement failure.

## THE MECHANISM — the code names its own gap
`core.c core_call_registered_fn` (the s10 OPSYN operator dispatch): *"Returns 0 when the name is
absent or carries no C fn (**SNOBOL-defined synonym targets are a follow-on**)."* The follow-on was
never built. The m4 emission routes the OPSYN'd operator through a by-name site carrying the literal
`"&"` (`.Lbynamefnzd23` in the witness .s); the chain finds no C fn behind the alias and returns 0 →
the statement fails silently. m3's in-process route resolves the DEFINE'd target; m4's cannot.

## WHY THIS IS B1 — measured, all guard-independent (identical at SCRIP_DEFER_BETA_GUARD=0)
- beauty's grammar engine IS OPSYN dispatch: `OPSYN('~','shift',2)` + `OPSYN('&','reduce',2)`
  (semantic.inc:7-8). Every rule evaluation nulls out, so the parse tables never act.
- The wall is TOTAL: beauty m4 Parse-Errors on its FIRST input line — the bare label `START` —
  and on `X = 1` fed as the whole input. Not statement-class-specific. Not the compile-side
  grammar (SCRIP compiles beauty's `&`-expressions fine — 12.8MB .s, runs clean since B2b).
- FALSIFIED: "SCRIP lacks binary OPSYN support" (candidate #1 since s145) — parsing and m3
  dispatch are green; the gap is ONLY the m4 by-name → SNOBOL-defined-target hop.

## THE SAME MISSING MECHANISM, SECOND WITNESS
`benchmarks/snobol4/indirect_dispatch.xfail` (seat, 2026-06-20): `$FN(X)` with FN='ADD1' — oracle
errors (022), **m4 produces EMPTY output**. Indirect by-name calls to SNOBOL-defined functions and
OPSYN'd operator aliases to SNOBOL-defined functions are one dispatch chain. One fix, two cures
(and the xfail's disposition should be re-graded after it).

## FIX DIRECTION (next slice, HQ-owned — beauty-critical path)
The follow-on the s10 comment promises: when the by-name chain finds the alias target is a
SNOBOL-DEFINED function, trampoline into generated code (the machinery exists for defers/thunks:
rt_proc_call_open_fnret / CALL2BB / EXPR$ collect). Gate with the standard ladder + this witness
pair (opsyn witness green m4, xfail re-graded) + beauty m4 statement-count movement.

---

## ADDENDUM (s162, HQ) — THE B1 FAMILY BOTTOMS OUT AT B1c: THE FAIL-RETREAT. EVERYTHING ELSE IS NOW GREEN AND WITNESSED.

**Falsified this slice (each with a witness now in `probe/b1/`):**
- B1d (dyn-scope theory): EVAL inside a DEFINE'd fn reading dyn-scoped formals — WORKS both modes (`b1c_eval_fn_pattern_retreat` prints `CB: ty cap=AB` oracle-true before the crash). ⚠ TRAP FOR FUTURE GRADERS: the m4 binary's stdout is BLOCK-BUFFERED when piped — a SEGV swallows correct output already printed; grade under `stdbuf -o0` before concluding "crashed before X".
- Pattern-VALUED formals through EVAL (`b1c_patvalued_formal_retreat`: `'A'|'B'` passed as `p`, fragment matches arm 2, `cap=B` oracle-true). The ladder A–H: scalar EVAL in fn ✓, formal-reading EVAL ✓, pattern-build ✓, deferred-call build ✓ (main+fn) ✓, thx-arg ✓, pattern-formal ✓ — ALL green m4.

**B1c, measured (gdb on the witness m4):** after the deferred call returns and the match FAILS, the retreat cascade dies at `rip=0x1`: `[rsp] = {0x1, 0x40207d}` where 0x40207d is an address INSIDE `n53_lit_string`'s box — the cascade consumed an ordinary SPINE VALUE CELL (a literal's 16B descriptor pair) as a resume record. Not the zero-cell class (B2a/B2b's guard passes non-zero garbage); the cascade has walked PAST the record region. Both modes, guard-independent. The B2 FINDING's §FIX-CAMPAIGN successor: the fragment-blob ↔ main-match record protocol misaligns by (at least) one quad somewhere in the crossing.

**Beauty consequence:** every grammar-BUILD layer is proven; B1c stands between the built grammar and any parse that must retreat (shift-reduce retreats constitutively). Beauty-m4's CLEAN Parse Error (no SEGV) is still unexplained-in-detail (its EVALs may fail on a construct the ladder misses, or its match dies pre-record) — but B1c is prerequisite either way. NEXT: record-layout census across the fragment/main crossing, then the B1c fix, then re-measure beauty + the un-swallowed B1b/B1c witnesses.

---

## ADDENDUM (s163, HQ) — B1c NARROWED TO ITS 10-LINE KERNEL: THE CROSS-MEDIUM PATTERN SEAM. AND THE GRAMMAR IS FULLY EXONERATED — ALL 36 RULE DATATYPES ORACLE-IDENTICAL.

**Lon asked: does beauty run at all on small programs?** Answer built stepwise, with two invocation traps caught en route:
- ⛔ ORACLE-INVOCATION LAW: beauty REQUIRES `sbl -bf` (`-f` case-sensitive; RULES.md SN-30) — bare `-b` folds `Shift`/`shift` into duplicate labels and produces garbage that LOOKS like corpus corruption. `util_run_beauty_oracle.sh` is the sanctioned runner.
- ⛔ `X = 1` in column 1 is a LABEL declaration — the oracle Parse-Errors it too. Tiny-input probes must be INDENTED.
- **Instrumented beauty (scratch copy, DT probes + xTrace=9): every one of the 36 grammar rules builds ORACLE-IDENTICAL datatypes in m4.** T4+D-18 fully cured the build layer. On `      X = 1` the oracle's machine runs (`PushCounter() → Shift(Id, X) …`); m4 prints Parse Error with ZERO deferred calls fired.
- **Witness ladder I–N**: direct pattern-value match ✓ · runtime concat of main-built values ✓ · deferred `*VAR` of a concat ✓ · fn-RETURNED pattern value in concat (L) ✓ · ARBNO(*VAR) wrap (N) ✓ — all green both engines. **M KILLS: `("" . D1 *PC()) F` where `F = EVAL("'x' . D2 *PC()")` — main-built ⊕ fragment-built CONCAT.** The walk runs the main half (first `PC ran` prints), crosses the seam into the fragment-built object, SEGVs. Oracle: `PC ran / PC ran / match`. `probe/b1/b1c_cross_medium_concat_seam.{sno,ref}`.
- **Beauty's manifestation is the same seam**: every rule concatenates main-built values (`nPush()`, literals) with EVAL-built values (`shift`/`reduce` results) — Parse's FIRST element walk hits a seam immediately; beauty's composite fails CLEAN (F-path, hence "Parse Error" not SEGV) while witness M's shape crashes — same underlying handoff, two failure faces (the vH/evd retreat crash `rip=0x1` is this family's third face).

**B1c fix target (next slice):** the runtime pattern-object walk at the main↔fragment blob boundary — where the composite's node handoff loses the record protocol. Entry points: rt pattern-object rep (pattern_match.c concat of DT_P values), the blob-enter machinery for fragment-built sub-patterns (PB-1s PATV$/MKPAT class), and the vH death anatomy ([rsp]={1, mid-lit-box addr} = walked past records into spine values).
