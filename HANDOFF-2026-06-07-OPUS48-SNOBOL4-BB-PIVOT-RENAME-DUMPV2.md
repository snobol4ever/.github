# HANDOFF 2026-06-07 OPUS48 — SNOBOL4-BB: PIVOT + bb_match RENAME + DUMP-V2/V2b

## Commits (SCRIP origin/main)
- `da96b66` PIVOT rename: bb_pat_* → bb_match_* (20 match-time templates)
- `d3907e8` DUMP-V2: --dump-bb line revamp (first cut — VETOED live)
- `8795a2c` DUMP-V2b: flat-linear correction (the veto applied)
- .github: this doc + GOAL-SNOBOL4-BB.md pivot section + watermark

## Lon PIVOT directives (this session, recorded in GOAL-SNOBOL4-BB.md ⭐ PIVOT section)
1. BB_INVARIANT/REF_INVARIANT: quit using COMPLETELY until further notice. Session reading (state for confirm): no NEW reliance; the existing baked chain breathes as a D4 shim only until builders cover each shape — corpus-non-decreasing HARD forces replace-then-remove. Rip-now-eat-the-red available on Lon's word.
2. Quit constant-folding; quit SNOBOL4 optimization in general.
3. BBs replace ALL old SM stack-machine functionality. Breadth over depth.
4. Rename bb_pat_* → bb_match_* — verified all 20 are match-time (dispatch from IR_PAT_* inside MATCH-driven chains; CAT/ALT are match-time control joins), executed `da96b66`. Fence glob now bb_match_* EXCLUDING head/retry/advance (head's lea-r10 mirror was always outside the family). Tracker entries swept; handoff docs untouched (history stays true). IR_PAT_* kind names NOT renamed (interp/shared namespace — separate question).

## Builder design (Claude under mandate — stated for veto, NOT yet vetoed; full text in goal file)
Hybrid: explicit IR kind per primitive × 7 family templates by operand class (nullary / unary_i / unary_s / unary_p / stitch / capture / defer). Slot-threaded RPN, stitch is its own box, instance record per D1, π=rbx. Invariant-off consequence: bb_match_* convert ONCE to [π+off] operand reads — no baked/instance twins. Staged D4-style.

## DT_P memory model (Lon, this session — thinking notes, inscribed in goal file; refine to D6 at builder landing)
DT_P = TEMPORARY value built by BB_PATTERN_*: "like strings, but of executable code." Build phase: UNSEALED, PAGE-SIZE segments, PATCHABLE LINKAGE for stitching. SEAL when `S ? P` executes — whole pattern sealed immediately before the match. Rationale: partial BB segments must not hold space when unreachable alone — collectable like strings. Interacts with D1/D5 + unstamped ledger.

## lower_sno.c census (Lon's contract CONFIRMED, 1095 lines)
0 `->α` / 0 `->β` field refs · 0 direct `->γ/->ω` pokes (all 9 via set_succ_fail) · 4 ir_operand_push · 30 node allocs (op set at birth) · 0 ring · 4 IR_EXEC (sanctioned SCAN sidecar) · 10 lower_unhandled loud-falls. Residue (data, not lower_sno style): SCAN still allocates sub-graphs (IR_alloc lower_sno.c:753); ARBNO inner via az sidecar punned in EXEC.counter (902-911).

## DUMP-V2b (the instrument; correction record)
First cut preserved S0's nested/indented pat:/subj: recursion — WRONG, Lon veto. Spec is FLAT LINEAR COLUMNAR: `[n] OP  γ=Nα  ω=Nβ  ops:[..] payload`, column 0, every slot 0..n-1 prints (NULL → `[n] ·`, the `continue` that dropped slots is dead), zero labels/indent. Sub-graphs print as SIBLING flat tables — stopgap until builder slots inline into the ONE linear sequence (then they vanish). Port letters render PORT-LAW convention (γ⇒target-α, ω⇒target-β) until IRD-4 IR_ref_t.sz — one-line swap, recorded in SNOBOL4-5STAGE-OWNED-BUILD.md DUMP-V2b rung. KNOWN RESIDUE: ARBNO-inner graphs undumped (az lower-internal — layering); dies with linear-builder lowering.

## roman.sno dump (Lon ask, this session)
corpus/crosscheck/keywords/100_roman_numeral.sno → 197-line flat dump. Instrument findings: 29 loud `[lower] UNHANDLED role=0 kind=47/46` falls (census-predicted missing arms; roman is M4-BEAUTY) + orphaned never-wired slots 58-63 (`γ=· ω=·` — GT/GE predicate, ASSIGN_CONCAT, SEQ, ASSIGN/BINOP shapes abandoned by the unhandled arms). csnobol4-suite/roman.sno parse-errors outright (pre-existing, not in gate corpus).

## JCON consult (Lon ask)
/tmp/jcon-master (proebsting/jcon, shallow — NOT committed). tran/ir.icn: `ir_chunk(label, insnList)` = labeled LINEAR instruction lists; every insn carries explicit `failLabel` + `lhs` fields (e.g. ir_Key) — validates the flat one-line-per-slot model and the γ/ω/ops columns. tran/dump.icn = generic record echo (-verbose). tran/gen_symbolic.icn = dump-as-a-BACKEND (one write per insn into an emit table keyed by label). tran/gen_dot.icn = ready graphviz generator — the crib for deferred V2-GUI (force-directed requirement).

## ⛔ AWAITING LON
1. Ledger stamps: **nv get/set** + **raw allocator** (both REQUESTED). Blocking `P = <pattern>` (DT_P into a variable, outliving the building statement's frame — 053 sits there). Anonymous in-statement patterns need NEITHER.
2. Builder taxonomy veto window (goal file ⭐ PIVOT section).
3. Invariant rip-now vs staged-replace confirm.

## Gates at close (all floors held, every commit)
smoke m4 7/7 HARD · pat-rung M4 18 PASS + 1 SKIP (053 pre-existing) · m4-only corpus 148/103/29 of 280 · beauty m4 1/17 · sno_pat_reg TIER1+TIER2 green · builds rc=0.

## NEXT
**BUILDERS RUNG 1** — bb_pattern_nullary + _unary_i/_unary_s for ANONYMOUS in-statement patterns over the ζ-arena (needs NO ledger stamps): new IR_PATTERN_* kinds appended in lower_sno, family templates per spec v2, dispatch cases appended, instance-driven MATCH beside the baked chain, probe-first vs sbl, statements route over as proven. Then _stitch (CAT/ALT, D2 equations). Concurrent-session courtesy: BB-FIXUP cursor at bb_term_inspect.cpp owns template hygiene; builders are NEW files (no overlap).

**Environment (fresh container):** install_system_packages.sh → build_scrip.sh → make libscrip_rt (MANDATORY before m4 work). SPITBOL oracle: clone snobol4ever/x64, bin/sbl -b.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
