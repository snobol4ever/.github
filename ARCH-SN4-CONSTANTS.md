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

---

## T1 FOLD SEMANTICS — SPEC AMENDMENT (s151, HQ ruling)

T1 (`c3add39a`) folds a declared scalar `&Name` whose one-time assignment is a literal (TT_ILIT/FLIT/QLIT) into that literal at every read site. The fold is TEXTUAL, and that is the SPEC, not an approximation:

- A declared constant's read denotes its declared literal EVERYWHERE in the program, independent of statement execution order (the C worldview: the declaration is the truth, not the store that implements it — Lon's "CONSTANT GUARANTEED").
- **Error 342 narrows to:** (a) reads of UNDECLARED `&names` — live, witnessed (`cn_read_before.err_sno`); (b) reads of a declared constant NEVER assigned anywhere in the program — compile-time detectable; diagnostic owed when T1 meets such a program.
- **Documented and ACCEPTED:** on the degenerate class "read textually after the assignment but executed before it", `SCRIP_CONST_T1=0` raises 342 and `=1` yields the value — the arms diverge THERE ONLY, by spec. No dominance/flow analysis will be added to reconcile them.
- **OPEN (g-cn2), the EVAL boundary:** EVAL-compiled thunks lower at RUNTIME; T1's literal table is DRIVER-side. Until `cn_t1_eval.sno` proves both modes read the sealed cell correctly inside thunks, no fold in the runtime-compile path is the safe default — verify which way the landed code behaves, then witness it.

---

## CONST-GRAPH — EMIT-ONCE / LINK-MANY (the CN-13 design of record; Lon's Q3 s162 "keep a global offsets structure and deduce offsets WITHOUT inlining", re-ordered s166: "FULL graph traversal with whole graph ZETA SPINE calculated when NOT using constant folding and use a LINKED graph; i.e. the PASS-THRU GLUE which has less baggage than today")

This is the section CN-13's own ladder names as step 0. Written s166 from a full in-source verification pass; every mechanism claim below was read in the tree at SCRIP `e06cee8b`, not assumed.

### THE ECONOMICS, MEASURED (s166, witness `&Num = SPAN('0123456789')` at N sites, mode-4 `.s` line count, scaled N = 1·2·12·24 to isolate the MARGINAL cost)

| road | 1 site | 24 sites | **marginal per site** |
|---|---|---|---|
| constants OFF (`SCRIP_CONST_STATIC=0`) — dynamic defer + blob | 406 | 5121 | **205 lines** |
| **today's default** — CN-12 substitution (inline a copy per site) | 349 | 3477 | **136 lines** |
| CN-13 target — one shared graph + thin sites | 349 | ~470 | **~5 instructions** |

Scaling is exactly linear (485−349 = 136; (1845−485)/10 = 136; (3477−1845)/12 = 136), so the number is the cost of a WHOLE COPY OF THE GRAPH and nothing else. CN-12's substitution buys 34% over the dynamic road and then stops: the remaining 136 lines/site is duplication, which is precisely what a LINKED graph deletes. beauty's `&White` at 42 sites = **41 redundant copies ≈ 5,576 lines of emitted asm.**

### THE FOUR BLOCKERS A SEAT WOULD EXPECT — ALL FOUR ARE ALREADY CLEARED IN-TREE (verified s166, this is the section's real payload)

1. **"It needs a per-program directory: constant → {α label, ζ geometry}" — IT EXISTS, AND IT IS NOT A NEW GLOBAL.** `rt_proc_set_fn(pname, pfn)` records each proc graph's EMITTED ENTRY ADDRESS by name (`scrip.c` m3 proc loop), and `emit_patzeta_register(pname, frame_bytes, fp, uniform)` records its SUSPENSION/ζ FOOTPRINT by name, with `emit_patzeta_lookup()` already consumed at `emit.cpp` for the ARBNO-DT arm. `zls_graph_name()`/`zls_g_resume_by_name()` are the same shape for resume slots. ⛔ **This retires the NO-NEW-GLOBALS banner-ask that CN-13 as originally worded would have required** — the offsets structure Lon asked for is already built and already populated; the rung READS it, it does not mint it.
2. **"m3 can't jump to another graph statically" — EMIT ORDER ALREADY MAKES IT LEGAL.** In BOTH media the proc/PAT$ graphs emit BEFORE main (`scrip.c` m4 pre-main loop; m3 proc loop, whose `emit_chain` RETURNS the entry address as `bb_box_fn pfn`). So at the moment a site in main is emitted, its target's address is a known constant. The `jmp rax` in `bb_glue_pass_wires_blob` is therefore NOT a structural necessity — it is dynamic resolution the site no longer needs once the target is a DECLARATION. TEXT takes the symbol, BINARY takes the known in-process address: the **KW-D sanctioned divergence** (s165, `rt_anchor_g`/`x86_load_got` precedent), zero new encoders.
3. **"The callee side must be built" — IT IS BUILT.** `bb_glue_wire_γ()`/`bb_glue_wire_ω()` are already `jmp r10`/`jmp r11`, and R10/R11 are the reserved LIVE γ/ω wires by register contract. A shared graph already returns through exactly the wires a thin site would set.
4. **"The deterministic/resumable split needs a new predicate" — IT EXISTS.** `pat_static` (`sno_name_static` = eligibly-resolved AND transitively defer-free) is already the "cannot recurse, no suspension" stamp, and `emit.cpp`'s `zd_k` already bills `IR_MATCH_DEFER && pat_static` as **K=0, a transfer box entering through the FLAT glue with ZERO FRAME**. That is the leaf-only slice's admission test, already computed.

### WHAT THE RUNG ACTUALLY IS, THEN — AND WHY HALF OF IT IS A TRAP

With 1–4 cleared, the remaining work is ONE POLICY CHANGE plus its linkage: **a multi-site declared constant must stop being SUBSTITUTED and start being LINKED** — its graph registered once (the `sno_pat_collect`/`sno_pat_thunks_build` PAT$ road already emits exactly one graph per distinct stored pattern), its ζ-SPINE planned once by its own whole-graph traversal (`zdp_analyze` → `zzone_plan` → `zls_build`; RSP-relative FORTH makes the shared graph position-independent BY CONSTRUCTION, which is why the site needs no RBP activation and no offset arithmetic), and each site reduced to the bare pass-thru: set the two wires, jump the known α.
⛔ **DO NOT LAND THE LINKAGE HALF ALONE.** Making the defer site's target static WITHOUT the policy change is a VACUOUS rung: under the default arm a declared constant is substituted, so the defer site is never reached, and the new arm would be dead code measuring green. That is verbatim the s146/s147 "KW-2/KW-3 quietly redefined to index-plus-call and marked done" failure that cost five sessions, and the s165 lesson it produced: **a directive whose success metric is a count in the emitted asm needs a gate that counts the emitted asm.** That gate is `scripts/test_gate_const_graph.sh` (landed s166) and it exists BEFORE the code deliberately.

### LADDER (unchanged in shape from the s162 note, now with its blockers cleared)
(1) leaf-only slice — one SPAN constant, one shared graph, ≥2 sites; gate = marginal lines/site collapses, green both modes, killswitch off-arm byte-identical. (2) ALT-carrying constants — `cn_nest_alt_defer`'s defer count drops, output byte-identical; this is also what makes the s161 TOP-LEVEL-ONLY depth limit structurally obsolete rather than repaired. (3) recursion through the protocol (the `sno_kw_chase` cycle guard deletes — recursion becomes the graph linking to itself). (4) blob native-leaf for value builds.
**Boundary, restated so nobody oversells it:** a shared graph is still statement-regime boxes — the may-only-add-passes construct exclusions (FENCE/capture/BAL) bound its CONTENT exactly as they bound inline. CN-13 fixes duplication, nesting, recursion and the interpreter; the construct frontier advances on its own rungs.
**Convergence:** the linkage protocol ("enter emitted code with return wires") is the SAME mechanism B1's by-name→SNOBOL-defined trampoline needs — one build, two walls.

### ⛔⛔⛔ CORRECTION TO THIS SECTION, MEASURED THE SAME SESSION (s166) — THE "THIRD ROAD" IS DEAD CODE AT HEAD, AND THAT MAKES RUNG 1 BIGGER THAN THE PARAGRAPHS ABOVE IMPLY

The blocker analysis above stands; **its framing does not.** It reads as though `proc_PAT$N` — the emitted, shared, four-port pattern graph — is a LIVE road that CN-13 merely re-links. It is not. **Measured: of the 59 corpus programs whose COMMITTED `.s` artifact contains a `proc_PAT$` graph, ZERO still emit one at HEAD** (each recompiled with the live driver, rc=0, real output). Every one now either inlines or falls through to **`rt_defer_run_all` — the runtime blob INTERPRETER**. `word4.sno`, the program this section's protocol was read off, is one of the zero.

**What killed it, and it was not a bug:** PT-2's dead-blob suppression (`sno_fz_procname_is_dead` in `sno_pat_thunks_build`: *"blob suppression — all refs inlined, no `*name` consumers; proc_PAT graph is dead code"*) plus the successive widenings of the inline set (PT-1, PAT-INLINE-ARBNO, CN-12) between them consumed every reference. Each widening was individually correct and gated; together they retired the road without anyone deciding to.

**THREE CONSEQUENCES, IN ORDER OF WHAT THEY COST:**
1. **Rung 1 must REVIVE the graph road, not just re-link it.** The policy change is not "substitute → link", it is "substitute → *emit a graph at all* → link". Defeating the PT-2 suppression for a multi-site declared constant is step one of the rung, and the emitted-graph protocol (CLASS D suspension record, `proc_PAT$N_γ` pushing `{res,r10,r11,pad}`, `_res`/`_β` re-entry) must be re-proven, not assumed.
2. ⛔ **THE ROAD HAS ZERO LIVE COVERAGE, WHICH IS A RISK RATING, NOT A DETAIL.** No corpus program exercises `proc_PAT$` today, so no gate anywhere is testing that protocol — it has been bit-rotting unobserved through every rung since it went dark. Reviving it is reviving UNTESTED CODE, which is precisely the provenance of the B1c/B2c record-protocol crash classes already on this board. **Rung 1's first deliverable is therefore a witness that FORCES the road and proves it still works, before one line of linkage is written.**
3. **`.s` artifacts describing that road were stale, and this session found out how stale.** The regen owed for CN-14 rewrote **414 of 484 crosscheck artifacts (net −23,654 lines)** — CN-14's own measured blast was 24 of 527 programs, so **~390 were already lying before this session touched anything**, describing roads the compiler stopped taking sessions ago. `.s` = HONEST CURRENT OUTPUT is a rule that decays silently between regens; a road can die and its artifacts will keep testifying that it lives. **That is how this section came to be written from a stale file in the first place — and the ASM-DIFF-FIRST law's own instrument is the thing that must be regenerated before it is trusted.**

**REVISED LADDER FOR RUNG 1:** (0) mint a witness that FORCES a `proc_PAT$` graph at HEAD and prove the emitted-graph protocol green in both modes — this is a resurrection test, and if it fails, THAT is the rung and the linkage waits. (1) defeat PT-2 suppression for a declared constant with ≥2 sites. (2) thin static site (the 4-instruction glue; 13 of today's 17 site instructions are dynamic resolution, measured). (3) then the ALT/recursion rungs as written above.
