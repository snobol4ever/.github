# ARCH-SN4-CONSTANTS — user-declared `&` constants: the durable design (Lon's Eurekas 1–3, 2026-08-19)

**Status home:** rung STATE lives in `GOAL-SNOBOL4-100.md` § SN4-CONSTANTS (+ FLAGSHIP/ORACLE-AMP subsections);
this file is the design of record they point at. **Evidence:** `FINDING-2026-08-19-s145-seeding-fix-beauty-advances-two-walls-named.md` (the blank-slate ground truth + oracle probe table) · `FINDING-2026-08-19-s145-B2-minted-arbno-capture-call-bracket.md` (the match-time deferred-call mechanics the optimizer tiers must respect).

## The three-tier `&` namespace (resolution order)
1. **Protected keywords** — constants already (`&ALPHABET &ARB &BAL &FENCE &ABORT &FAIL &REM &SUCCEED &UCASE &LCASE &STCOUNT &STNO …`), untouched.
2. **The closed unprotected list** — true keyword VARIABLES (`&ANCHOR &TRIM &STLIMIT &MAXLNGTH &FULLSCAN &DUMP &ERRLIMIT &CODE &CASE &FTRACE &TRACE &ABEND &COMPARE &PROFILE &ERRTEXT &ERRTYPE`), assignable per manual ch.16.
3. **Every other `&name` = USER CONSTANT** — one-time assignment, sealed forever. Bare `name` is a different cell (CN-2 canonicalizes the NV key to `"&Name"`; the pre-CN-2 lexer strip aliased `&W`≡`W`, measured).

## Semantics (HQ defaults under Lon's grant; veto any)
Second textual definition = compile error (CN-0 target; today runtime-only). Any dynamic write to a sealed cell = **error 341** (with name). Read with no definition anywhere = compile error (CN-0); read before the definition EXECUTES = **error 342** (with name). No bypass via `OPSYN`/`$('&X')`/aliasing — the seal lives on the CELL (`NV_t.is_const`, Lon's bit). Extension programs are oracle-fail by construction → pinned `.ref` lane.

## The guarantee (two layers)
(a) **The bit** — `is_const` on the NV cell (landed CN-2, SCRIP `a63c13d9`); a value-side DESCR tag bit remains open for optimizer trust-in-flow (decide against `GOAL-DESCR-TAG-ENCODING.md`). (b) **The page** — constants land in the KW-STATIC emitted block's sibling RO segment, `mprotect(PROT_READ)` after init: re-assignment FAULTS (CN-4; rides D-3's block — its brief carries the CONSTANTS-READY clause).

## CVA — the CONSTANT VARIABLE AREA (Lon's name, 2026-08-19 in-chat), beside GVA — the Global Variable Area
**The two-area model of record:** **GVA** (Global Variable Area — the existing `rt_gva_island`/`gva_register`/R9-slot machinery) holds WRITABLE globals only; **CVA** (Constant Variable Area) is its sealed sibling holding every constant DESCR + payload. Disjointness is already mechanically true at the collector: `src/optimizer/gva_collect.c:10` refuses `&`-names (`if (name[0] == '&') return 0;`) — verified by source at HQ, closing CN-2's open residue ("exclude &-names from GVA": nothing to do, it was never possible).

### The CVA design (Lon's optimization note (2026-08-19 in-chat, verbatim in substance: *"Have a separate GVA-like MMap'd arena for ALL CONSTANT DESCR, and have GVA for WRITABLE DESCR. Then you can SEAL the memory. But that causes problems if an EVAL(\"&new_constant = ...\") … I wasn't sure how you can guarantee assignment never happens a SECOND time at runtime unless you have a BIT in the DESCR which must be checked every time an assignment."*)
**The two guarantees are different things, and the design needs both:** the **BIT** (landed CN-2: `NV_t.is_const` on the CELL) refuses a second NAME→value binding — and costs nothing on the hot path, because `NV_SET_fn`'s fast path already segregates on `name[0] != '&'` before any seal logic can be reached; only `&`-name writes (rare, by construction one per constant) pay the check. The **ARENA** makes the bound VALUE physically immutable: a GVA-like mmap'd region (precedent: `rt_gva_island`, `rt.c`) holding every constant DESCR + payload (strings, staged pattern graphs), with **GVA proper reserved for WRITABLE globals only** — which also relieves GVA register-slot pressure (R9-tier slots are scarce; constants never needed write cells).
**The EVAL hole, and the answer:** `EVAL("&new = …")` mints constants at runtime, so a hard one-shot `mprotect(PROT_READ)` over the whole arena breaks. Recommended shape: **page-granular progressive sealing** — a bump allocator whose FILLED pages are sealed RO as the frontier crosses them; only the frontier page is ever writable, new runtime constants land there, reads never pay a protection flip. (Alternatives noted: unseal→append→reseal per mint, costlier but simpler; or CN-0 forbids runtime-minted constants — declined, EVAL-minting is legal.)
**Two homes, one semantics (mode split):** compile-time-known constants emit straight into the KW-STATIC block's sibling `.rodata` (zero runtime construction, mode-4) or the sealed arena (mode-3); runtime-minted (EVAL) constants always land in the arena. Payoffs beyond the seal: no GC scanning (immortal+immutable), no write barriers, co-located cache-friendly reads — the T1/T3 tiers get their storage story from this section. Status: DESIGN CANDIDATE for CN-4; the bit stays regardless (belt and braces — cell seal + value seal). Terminology of record everywhere from here on: **CVA / GVA**.

## Optimizer tiers
**T1** scalar constants → immediates/rodata, zero NV/GVA reads. **T2** constant PATTERNS → `pat_static` by DECLARATION: stage the graph at compile time; every `*&P` defer / stored-ARBNO resume on a declared-constant target bypasses the dynamic machinery (⛔ but NOT the match-time `. *Fn()` capture-call class — those side-effects fire per match by design; see the B2 FINDING). **T3** constant strings/tables → rodata, no GC scan, no write barriers.

## Parser-action COMPILER primitives (CN-5; Lon's final ruling 2026-08-19: "nPush/nPop FAMILY is a compiler primitive… CONSTANT forever… we'll eventually remove the *.inc file")
Builtin WINS always — sealed compiler names, user DEFINE of them = error. The family lowers at compile time to dedicated zero-width boxes (counter op + four-port backtrack undo); the runtime two-level encoding (`'' . *Fn()` deferred-call capture = the B2 thunk/record class) is never emitted for them. `semantic.inc`/`counter.inc` retire at end state; beauty_c rides the primitives. Precedence question CLOSED.

## Oracle amplification + the pristine-oracle law
Both oracles learn `&name` as plain variables (`sbl-x`, `csnobol4-x` — HQ board D-12/D-13) so converted programs keep LIVE oracle grading (single-assignment ⇒ observably identical). ⛔ Stock binaries are NEVER replaced; every `-x` proves full-classic-corpus byte-identity vs stock before anything trusts it.

## The flagship + isolation ladder
`corpus/programs/snobol4/demo/beauty_c/` — GENERATED (generator + WAVE list are the single source of truth). Fixed point: `beauty_c < beauty.sno ≡ beauty.sno`. Wave-1 = 52 pure grammar constants (62 pattern-shaped minus call-duals and DEFINE/OPSYN-tainted names — the `&reduce` reseal of run-1 is the measured teacher). Widening a wave moves one pattern between the constant and dynamic worlds = bisecting engine defects by construct.
