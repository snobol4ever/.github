# FINDING 2026-07-14 s58b — ZS-2 JMP-TOPOLOGY DESIGN (CORRECTED) + R12-FREE LADDER

AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
GOAL: GOAL-SNOBOL4-BB.md RUNG ZS-2. Base: SCRIP cb193af5 (encoder vocab added; one past 05449bbe).

## RULINGS OF RECORD (Lon, s58)
1. RSP IS THE ζ BASE — "it just slides." Cells push/pop; emitter tracks static depth; dynamic-depth constructs anchor via saved-rsp headers (s52 ARBNO chain is the reference).
2. "DEFER BBs should not jump via a C function call to its destination; the x86 asm should just JMP to the alpha of the BB." — final design §5-CORRECTED below.
3. R12-FREE LADDER: ZS-2 → PROC-CONV → SLOT-MIGRATE → FLIP.
4. r12 afterlife: OPEN (ZH base vs general pool — non-blocking).

## §5-CORRECTED — THE DESIGN (Lon ruling s58; supersedes §5-ORIG)
- blob_α is a KNOWN LABEL at emit time (`<prefix>_α` from the pat_flat chain).
- After fn→rax (get_pat_fn or FZ-5b inlined): `jmp rax` DIRECTLY to blob_α. No C function call.
- Blob's own α self-allocates on rsp (`sub rsp,K`). FORTH cells pushed in body.
- γ retains cells, jmps to outer γ continuation (known label, baked at emit).
- ω: `add rsp,K`, jmp to outer ω continuation.
- β re-entry: direct `jmp blob_β` from outer chain's backtrack edge. blob_β = known label.
- NO header cells, NO stored-edge-pointer cells, NO trampoline. The complexity in §5-ORIG came from treating edge targets as runtime values; they are LABELS BAKED AT COMPILE TIME.
- ENCODER VOCABULARY (now in tree, cb193af5): x86_lea_id (lea reg,[rip+L(n)]) · x86_jmp_reg (FF/4 reg) · x86_jmp_mem (FF/4 mem, SIB-correct for rsp/r12).
- DELETE from bb_match_defer.cpp: rt_zls_alloc (:43) · rt_fn_frame_bytes (:41) · both rt_zls_release (:54/:121) + their extern decls. grep-clean = storage completion.
- zeta_storage.c:111: two fields → one 16B ZK_RAW pad row this rung.

## T2 ROOT CAUSE (static-slot clobber — derivation, not a guess)
zeta_storage.c:111 grants two 8B fields in the STATIC flat frame (one grant per box, whole-program). Recursive *LIST re-enters the same box at depth 2, overwrites depth 1's live fn/frame pointers. β reloads the clobbered slot → call rcx → PC in stack region. Jmp-entry + self-allocation makes the clobber unrepresentable.

## PARALLEL SESSION NOTE (s58a, Claude Sonnet 4.6 — do NOT re-derive)
That session measured the identical root cause on the FLAT DEFER rsp attempt (5.5M ZLS1 allocs→0, pattern_bt correct) and observed the nested-DEFER SEGV (4 regressions: 124/130/139/150). Their FINDING-2026-07-14-CLAUDE-ZS-RSP-DEFER-GAMMA-BETA-LIFETIME.md has the measured recipe. Read it first; this doc adds Lon's ruling and the encoder vocab. The two sessions converged on identical diagnosis.

## R12-FREE LADDER
1. ZS-2 — this rung (jmp-entry DEFER).
2. PROC-CONV — rt.c:549/878/892/980 + :591/:608 family; icon/prolog/raku smokes join gate.
3. SLOT-MIGRATE — flat FR() frame dissolves into per-box FORTH cells on stream; ZS-0 gate = scoreboard.
4. FLIP — -DZC_FRAME=RSP; kill one literal "r12" template site; 151 FR() sites need zero edits; gate on default-build byte-identical + RSP crosscheck number reported honestly.
