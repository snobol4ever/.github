# FINDING 2026-07-19 — R8 BLOCKER CLOSED (scan reg/global desync at generator suspend); + case-arm alternation, record-registry cap, stop() message; jtran ucode pipeline advances to a proc-body first-set blocker

Session (Lon: "get JCON self-hosting under SCRIP"). Base SCRIP `f7b198fa`, corpus `e6e2e2ef`, .github `7a65d854`.
Four fixes in tree this session, all VERIFIED with measured zero regression (fail-list byte-diff against a
same-sandbox baseline, twice). Board note: the documented 252/9/32 does NOT reproduce in this sandbox — unmodified
HEAD measures **241/20/32**, delta concentrated in real-arithmetic/math tests (real_add/mul/conv, sqrt, pow,
mathfunc, math_hello — environmental, likely libm/format drift) — all regression claims here are against the
MEASURED baseline (`/tmp/fails_base.txt` methodology: stash, rebuild, rerun, diff).

## FIX A — ICN-SCAN-SUSPEND-SYNC ★ closes the R8 blocker  [src/templates/bb_suspend.cpp, src/emitter/emit.cpp]
**Coexpr framing was a RED HERRING.** R15 (pure generator + scan + suspend, NO coexpr) loops `got: AA` with
`&pos` rolled back to 1 on every resume. gdb event trace (bp on rt_scan_enter/leave/reenter/sync_out/sync_in):
leave/reenter NEVER called; per cycle exactly `SYNC_OUT delta=0 -> pos:=1`. Mode-4 .s confirmed the mechanism:
inside a scan, pos/move/tab are REGISTER-family boxes advancing r14 (δ) only, never scan_pos; r13/r14/r15 are
shared live-through registers across proc calls; the CALLER-side call brackets (bb_call_proc_staged, per the
x86_asm.h world-boundary doctrine) treat the GLOBAL as authoritative — so the caller's value-out `sync_in`
clobbered the callee's advanced r14 from the stale global, and its β `sync_out` re-poisoned the global. Fix:
bb_suspend now PUBLISHES (`x86_scan_sync_out`) before the γ jump and REFRESHES (`x86_scan_sync_in_rr`) at the β
resume landing (self-gated on g_scan_regs_live), making the global authoritative at every boundary — correct for
both by-name and register-family callees. Second edit: `g_scan_regs_live` leaked across graphs when no IR_SCAN
leave box is emitted (this graph shape has none), emitting garbage sync brackets into non-scan procs (main's
startup publish with uninit r14); emit_chain now resets it per graph. VERIFIED: R8 (finding repro) → AA BB CC DD
then stop, m3 AND m4; R15 correct (pos 1→3→5→7); full discriminator ladder R9–R13 + instrumented r8p green.
Latent issues noted, NOT fixed: (1) rt_scan_leave/reenter are dead on the suspend path — the inner scan env leaks
to the caller during suspension (arguably correct Icon dynamic-state, but the scan_saved machinery is unused
there); (2) `fail` crossing a scan jumps straight to proc-ω bypassing rt_scan_leave (scan_depth leak, caps at 16);
(3) in-scan `&pos :=` writes r14 only (global catches up at next publish).

## FIX B — ICN-CASE-ALT: alternated case-arm selectors  [src/lower/lower_icon.c TT_CASE]
`case x of { a | b | c : ... }` matched ONLY the first alternative — for ALL types (`case 3 of {1|2|3:}` →
default). Canonical `ir_a_Case` (refs/jcon-master/tran/irgen.icn): the `===` comparison's failure port is the
clause expr's RESUME label. Fix: per-arm `cx->beta = ω` reset, capture kβ after key lowering, and
`lc_ω_to_β(idc, kβ)` when the key is resumable — mismatch resumes the selector generator (third instance of the
missing-resume-edge family, after `to` and `!`). **Residual divergence (documented in-code):** canonical also
routes clause-expr failure/EXHAUSTION to the NEXT clause; wiring key-fail→chain_next regressed multi-arm chains
(rung14_case_return_arm lock + 4× rung33_case — total case fallout, caught by the suite, reverted), so exhaustion
still exits via case-ω. Bites only when an alternated arm is FOLLOWED by more arms AND matches none of its
alternatives; jcon's parse paths match. Repros: /home/claude/t/r16 (plain record case ok), r17 (alternation), r19
(multi-arm ints). VERIFIED: r17/r19/rung14 (`side b a c`) green; suite byte-identical to baseline.

## FIX C — REC-REG-CAP: record/type registry 128 → 1024 + loud guard  [src/driver/driver_data.c]
jtran merge declares **415 records**; `SC_DAT_MAX_TYPES=128` silently dropped the tail at BOTH lower time (only
128 `record_register` calls emitted into the m4 prologue) and runtime. Symptom: `u_pnull()` (zero-field record,
gen_ucode.icn) → rt_call_arr → APPLY_fn → Error 5. Found via `SCRIP_DEBUG_APPLY=1`. Guard now prints
`[REC-REG-CAP] FATAL ... raise SC_DAT_MAX_TYPES` on saturation. Post-fix: 415 registrations in jtran.s, Error 5 gone.

## FIX D — stop() prints its args  [src/runtime/by_name_dispatch.c]
The by-name `stop` arm was bare `exit(0)`, swallowing every jcon error message (pipeline died silently rc=0).
Now writes args to stderr per canonical fmisc.r, still exits 0 this session (an rc 0→1 flip needs a
harness-impact audit first). This is what surfaced every parse error below.

## Pipeline progression (m4, hello_t.icn = plain 3-line Icon)
Build recipe verified end-to-end fresh: oplexgen/interfacegen standalone m4 → semicolonize → do_ops.icn (32
reserved_sym_tbl lines) + interface.icn; 17-module merge order per prior finding; SCRIP_BETA_ELIDE_OFF=1;
511,528 asm lines, 0 bombs, links 5.0MB. jtran CLI understood: colon-separated stages become a coexpr chain
(`create fn(c,args)`, `while @c`). Ladder: 2-stage preproc:stdout ✓ (4/4 lines); 3-stage yylex:stdout ✓ (12/12
tokens); **NEXTLINE dup/skip GONE** (line 1 once, line 2 present — FIX A did its job in situ); parse consumes
procedure main ( ) ; — through STRINGLIT after FIX B — parse:stdout terminates rc=0 (the earlier ~10M-empty-line
"parse spin" was an artifact of FIX B's intermediate regressed form, NOT a real blocker).

## OPEN BLOCKER — proc-body first-set rejects IDENT right after the header semicolon
4-stage ucode: `File hello_t.icn; Line 2 # Expecting ;` with **IDENT(write) current** and no further token pumps
(probe build: TOK[;] TOK[write] then the error — parse_nexpr never pulled `(`). Site bracket (parse.icn ~795-812):
after `parse_match_token(lex_SEMICOL)` (header, consumed ✓) → parse_locals → parse_do_initial → `while
member(do_proc_set, parse_tok_rec)` — the loop body never runs, so either member(do_proc_set, IDENT) is FALSE
(set construction incomplete — do_proc_set built from GENERATED do_ops/oplexgen machinery, same emission territory
as the prior bang-fix) or a `=== (a|b)` alternated comparison in parse_locals/do_initial misroutes (binop
right-operand resume — same missing-resume family). NEXT SESSION OPENER: probe `write(&errout,
image(member(do_proc_set, parse_tok_rec)))` + dump `*do_proc_set` and its construction site; if it's an every/!
emission gap in the GENERATED do_ops.icn, diff generated-vs-iconx-generated do_ops. ("Expecting ;" vs expected
"Expecting end" from match_token(lex_END) is unexplained — check parse_locals/do_initial internals first.)

## Repro pack (/home/claude/t/, dies with sandbox — all bodies in this doc or prior finding)
r8/r8p/r9–r13 (prior finding), r15 (pure scan+suspend), r16/r17/r19 (case), r18 (zero-field record).
jtran workdir /home/claude/jt: do_ops.icn+interface.icn generated, jtran + jtranp (probe: NEXTLINE in
lexer_probe.icn, TOK[..]/PUMP_FAIL at all three `@parse_tok` sites in parse_probe.icn).

## Board (this sandbox, measured)
Icon rungs 241/20/32, fail list BYTE-IDENTICAL to unmodified-HEAD baseline (verified twice: after FIX A, after
FIX B-revert). Icon smoke 14/14 ×2. Prolog 5/5 ×3. Hello matrix 6/6, drift 0. Gates: icn_no_stack OK,
one_reg_frame OK, semicolon OK; icn_scan gate FAILS AT BASELINE TOO (probes 23/5 identical pre/post; corpus
bucket N=0 + dead m2 floors — stale gate, pre-existing). SN4 smoke harness target missing from Makefile
(pre-existing, mode-1/2 era). Artifact regen ceremony run (benchmark/feature/demo + update_icon_bench_asm:
1 updated, 3 pre-existing compile-errs).
Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
