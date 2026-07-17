# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ▶ LIVE CURSOR (updated every handoff — RULES.md STALE-ORIENTATION rule)
- **✅✅✅ NCB-1d LANDED (2026-07-17 s90, Lon "Switch all Icon templates to RSP/RBP FORTH ζ, sharing the C runtime stack; look at what SNOBOL4 has done") — det LEXICAL procs join the jmp-entry regime; the proc trampoline is retired for them; Icon 205→237, Raku 209→283/283-PERFECT, SN4 +2.** The s84-era "return-value + base-case" bug was the CALL-REGIME/SELF-ALLOC MISMATCH: bcps' lex arm kept the caller-made-frame window (`rt_frame_prep`+`call rax`) while the callee body self-allocated under RSP and ignored rdi — args never arrived (fact's n = zeroed DESCR → `n=0` type-fails → ~128×64KB runaway → SIGSEGV) and γ hardcoded `eax=1` losing the [rbp+0/8] result.  **THE FIX (uncommitted in this tree, 6 source files):** (1) `emit.h` `flat_lex` + (2) `emit.cpp emit_jmp_entry_for_proc` now ADMITS det lex real procs (`gram__*` scan-protocol boxes and generators still declined; LBL__ arms with flat_lex=0), (3) `xa_flat.cpp` jmp-entry prologue BOTH mediums gains a flat_lex tail `call rt_jmp_frame_lexprep(fb=rsp, kt−32)` (new rt.c strict leaf: NULVCL fill + `rt_frame_bind_args` from staged `g_call_args`; no-op on non-lex pcall top) and the DET γ/ω epilogues BOTH mediums converted rsp-relative → **DEPTH-IMMUNE rbp-absolute** (result+wires via pinned rbp, `lea rsp,[rbp+kt]`, reads-before-motion — the line-429 "seal cut arriving DEEP" tripwire class; Icon `return` from generator/scan depth IS that arrival), (4) `bb_call_proc_staged` det-arm guard widened `is_dyn && RSP` → `RSP` (every det named call takes the wire; legacy arms now non-RSP-only), (5) **REGIME RECORD** `rt_proc_t.jmp_entry` (+setter; registered beside `rt_proc_set_generator` in the three in-process driver sites AND printed into the m4 `proc_startup` — m4's runtime table never had is_generator, so the compile-time truth is embedded), consulted by ALL FIVE C transfer windows: `rt_proc_call_c_lex`, `rt_call_proc_descr` (first-class `$b()`/blocks — the blk_calls_sub stack-jump crash), and `rt_proc_call_gen_h`'s new det arm (value calls `every (!plist)()` — rung37_proc_lookup crash; one-shot via `rt_proc_enter`, hout=0).  **MEASURED (all fresh this session, SCRIP src on `496e62f4`+edits, corpus `f69dd89f`+10 icon-bench .s):** Icon harness **237/20/32** (was 205/52/32 at measured HEAD; honest sweep CLEAN 200→**236** (stratum 2), FAIL 52→**20**, zero regressions by comm-diff), icon smoke **m3 14/14** m4 12/14 (was 12/10), **Raku smoke 283/283 BOTH modes** (HEAD measured 209/74 — the regime coherence fixed all 74: blocks, methods, multis, grammars, param typechecks), SN4 crosscheck **m3 305/2** (HEAD 303/4 — depth-immune epilogue fixed `test_case` + `140_pat_eval_double_fn_trick`, the EVAL-deep-arrival class), m4 295/11 unchanged, **DIVERGE 12→10** same residual names, SN4 smoke 7/7×2, prolog smoke 3/5 = PRE-EXISTING at HEAD (cursor's 5/5 was s84-era; not this slice), 3 Icon gates + emit_no_lang green, strict-medium residue xa_flat 96→**100** (the 4 raw-arm adds, s84-precedent style — the xa_flat revamp remains the WIP owner).  Residual 20 FAIL classified: 3× rung03_suspend_* + genqueen/level/fncs1 (GENERATOR procs = slice 2), jcon scan/scan1/scan2 + rung08×3-DIRTY + scan_alt-DIRTY (FZ-E scan family), htprep/prepro (FZ-D parse), var (FZ-B1), kwds/mindfa/recogn/string rc=0 wrong-output quad, args/coerce/endetab/mffsol. `rung36_jcon_parse` FAIL→DIRTY (27B correct then rc139 mid-flight, rcx=0 wire signature — gen/scan intersection); `rung36_jcon_meander` is ADDRESS-UNSTABLE across relinks (full-output+rc139 on one build, empty+rc0 on the next) — count NOT-fixed, flag for slice 2.  Repros `/tmp/{onecall,fact0,fact3}.icn` + `blk.raku`/`gram.raku`; sweep `/tmp/icon_m3_honest.sh` (now mirrors harness `.stdin` handling).
  **STRATUM 2 (same session, FZ-E root fix): `xaf_anchor_leave_*` was reading the graph anchor `mov rsp,[rsp+off]` — the U5 zr→rsp seal made it depth-valid only at 0; Icon's retained scan-suspension cells arrive DEEP (sa2 bracket: `"eb" ? (="e"||="b")` alone crashed rsp→heap→jmp 0), and SN4 mode-4 seal-cuts were the SAME class.  Fix = frame-base read (`x86_fb()`/`48 8B A5`) under RSP, enter unchanged (prologue IS depth 0).  Plus the lower_alt fresh-entry GOTO trampoline (lower_icon.c:16's generic β-promotion was landing alternation fail-cascades on generator-arm βs).  POST-BATTERY: Icon honest CLEAN **236** DIRTY **1** (`proto` rc1) FAIL 20 zero-regression; icon smoke **14/14 BOTH modes**; rung08 trio + scan_alt crash → CLEAN/rc0; **SN4 m4 295→304, DIVERGE 12→1** (the whole pat_fence/abort family was this anchor bug; residuals m3 {expr_eval,141}, m4 {expr_eval,1017}, DIV {1017} — strict subsets), m3 305/2 held, Raku 283/283 held, prolog 3/5 held.  `rung36_jcon_meander` is **ASLR-UNSTABLE** (full-output+rc0 vs empty+rc0 across execs — NOT counted fixed; sweep counts wobble ±1 on it).  Scan residuals now VALUE-level: scan_alt/scan1 NOMATCH-rc0, scan/scan2 rc139 deeper in the family.
- **⚠ HARNESS DEFECT (still open):** `test_icon_all_rungs.sh` grades stdout only (2>/dev/null, exit code discarded) — an exit-code check must be added so crash-on-exit regressions cannot hide (this is exactly what masked the 0-clean state as 205 green). Same blind spot in the SNOBOL4 crosscheck.  Interim: `/tmp/icon_m3_honest.sh` (mirrors harness incl. `.stdin`, adds exit-code CLEAN/DIRTY split).
- **HEAD rung:** ZERO-FAILURE MANDATE — live headline **237/20/32** (s90, NCB-1d landed; see top bullet). R12-era 242/15/32 (`b404fb95`) remains the pre-RSP reference. FAIL-ZERO (15) + XFAIL-ZERO (32) ladders below. Re-derive counts fresh, never from prose.
- **GROUND TRUTH — R12 baseline (SCRIP `b404fb95`, corpus `78915257`, documented, NOT re-run this session):** **242 PASS / 15 FAIL / 32 XFAIL / 289 TOTAL** (mode-3). Fail set (15): `rung36_jcon_{args,coerce,endetab,fncs1,htprep,kwds,mffsol,mindfa,prepro,recogn,scan,scan1,scan2,string,var}`. This is the clean pre-RSP-flip baseline and the base the DISJUNCTION refactor should build from.
- **⭐ NEW DIRECTIVE (Lon, 2026-07-17): co-expressions and generator PROCEDURES are slated to get their OWN stack PER INSTANCE.** The single RSP/RBP ζ FORTH stack is the per-sequence frame for straight-line/backtracking boxes; a `create`/`@` co-expression and a suspending generator procedure each need an independent activation stack per live instance (so multiple suspended generators / co-expressions coexist without clobbering one another's ζ). This is the natural home for the s65 "side-stack island for suspending PAT$ blobs" idea generalized to Icon co-expr + generator-proc instances. NOW = SLICE 2 (s90): with det lex procs landed on jmp-entry, the generator-proc conversion is the next rung — per-instance activation stacks (ZH heap routing exists: rt_proc_call_gen_h/resume_frame_h; the det arm inside gen_h shows the seam). The 3 rung03_suspend_* + genqueen/level/fncs1 fails are its acceptance set. Relates to `ARCH-ICON.md` §Co-expressions (pthread+semaphore model already landed for `create`/`@`) — per-instance stack is the ζ-allocation half of that.
- **XFAIL-ZERO progress this session:** 3 stale markers deleted (corpus commit `78915257`): `level` (every/suspend exhaustion was fixed upstream), `random` (LCG now matches), `subjpos` (was KNOWN HANG — now runs in 28ms, byte-identical). All three verified m3+m4 stable across repeated runs before deletion.
- **FZ-B1 `var` DIAGNOSIS CORRECTED this session:** NOT a pointer-hole (DT_N / NAMETRAP already exists — slen=0 NV-dict, slen=1 direct cell ptr, slen=2 VCELL; rt_deref + IS_NAMETRAP_fn wired). Actual gaps: (1) lower_lvalue_var in lower_icon.c has no case for variable(...) as lvalue target → TT_ASSIGN mints nameless placeholder → emitter abort; (2) rt_icon_variable(name) needs a per-proc runtime name→frame-offset table for locals (one narrow reflection-scoped table; globals → NV dict slen=0; keywords → closed setter table). NEXT: Lon call on name-table form (sealed RO blob vs startup-built).
- **FZ-E SCAN FAMILY root cause (recogn/scan/scan1/scan2/string) CORRECTED this session:** NOT generator-in-call-arg. Minimal repro: "eb" ? { (="a") | (="e" || ="b") } returns &null, should return "eb". Root cause: emitter wires SCAN_MATCH fail-edge to arm-B beta label (resume, mid-flight) instead of alpha label (fresh start). In asm: SCAN_MATCH "a" omega -> xchain0_n5_beta (element-index=2) not xchain0_n5_alpha (index=0, save delta). Land mine in emit.cpp ~L887-904 / IR_SCAN_SEQUENCE case L1101 — the fail-edge alpha/beta classifier. recogn 4th input "eb" (t()‖="b" path) is this bug, not generator-in-arg.
- **NOTE (refs, 2026-07-17):** uploaded zips did NOT arrive this session; `refs/` set up from GitHub canonical upstreams per RULES.md fallback — `refs/icon-master` → `github.com/gtownsend/icon` (master; Arizona Icon v9, 45 `src/runtime/*.r`), `refs/jcon-master` → `github.com/proebsting/jcon` (master; `tran/irgen.icn` present). Both verified against RULES.md's `ls` check. ICN-RESUME-THROUGH-SCAN LANDED 483a6215.
- **⭐ NEW DIRECTIVE (Lon, this session): ERADICATE IR_MOVE_LABEL from Icon — make IR_DISJUNCTION a nary self-state box (mirror IR_MATCH_ALTERNATE / IR_SCAN_ALTERNATE). Full design in `FINDING-2026-07-15-CLAUDE-ICON-MOVE-LABEL-ERADICATION-VIA-BB-SELF-STATE.md`. Key facts measured: (a) Icon's `|` lowers to IR_DISJUNCTION + per-arm IR_MOVE_LABEL (lower_icon.c:820); IR_IF similarly uses IR_INDIRECT_GOTO + two IR_MOVE_LABELs (lower_icon.c:835–848). (b) ARBNO is SNOBOL4-only — Icon does NOT produce it. (c) Icon's top-level `|` (IR_DISJUNCTION) and `1 to N` (IR_TO) both SURVIVE the RSP-frame default flip at HEAD; the 38-test regression (242→204) is from the scan-family and complex reflection paths under the new RSP frame — caused by `f7de3863` (R12-ERAD s65) flipping the default BEFORE the Icon RSP migration was complete. (d) Icon `|` lowers to IR_DISJUNCTION (NOT IR_MATCH_ALTERNATE; Icon's lower_alt is Icon-owned in lower_icon.c:820). SNOBOL4's `|` produces IR_MATCH_ALTERNATE — different kinds. (e) The 38-test HEAD regression is the R12-ERAD session's to recover (out of Icon lane); work from `b404fb95` for a clean 242-baseline signal. NEXT RUNG: implement the DISJUNCTION nary refactor per the FINDING (start at §3, option B for value routing — per-arm result copy dispatched by alt_i).**

## ▶▶ ZERO-FAILURE MANDATE (Lon directive, 2026-07-15): "We have no expected failures." END STATE = 289/0/0 — every FAIL fixed AND every `.xfail` marker DELETED (source fixed or SCRIP fixed). The two ladders below are the whole job. Re-derive counts from a fresh `test_icon_all_rungs.sh --corpus <path>` run, never from prose (this session already caught the cursor claiming 239/15 when ground truth was 238/16 — the `rung13` regression).

### ▶ RUNG: FAIL-ZERO — drive the live FAILs to 0 (20 as of s90 — re-derive fresh; cluster membership below is 2026-07-15-era, several since fixed by NCB-1d)
Grouped by ROOT CAUSE, not alphabetically — one fix clears a whole cluster. Attack clusters top-down (crashes before wrong-output: a crash blocks everything downstream of it). Each step: MONITOR/`--dump-ir` to bracket → fix at the land mine → confirm m3 AND m4 → re-run suite, confirm the test flips and nothing else breaks.

**Cluster A — `x86_parse` bracket-operand abort — ✅ FIXED (SCRIP, root cause found).** ROOT CAUSE (not what the first note guessed — the multi-gen `every` was a red herring): `x86(mnem, xa, xb, …)` at `x86_asm.h:1057` eagerly runs `x86_parse` on its first TWO args BEFORE checking the mnemonic — so a DATA-directive payload (`.string`/`comment`/diagnostic) whose text contains `[...]` (e.g. the Icon string value `"[x]"`) was parsed as a memory operand, and the base-not-a-register arm `abort()`ed before the `.string` handler at 1067 could safely escape it. Minimal repro was just `write("[x]");` — any bracket-bearing string literal, no `every` needed. FIX: the abort at ~1038 replaced with the benign `XK_SYM` fallthrough the function already uses at line 1049 (unrecognized bracket → treat as symbol, let real instruction handlers fail loudly downstream if they truly get a bad operand). Data payloads now pass through untouched. Verified: 238→239 PASS, zero regressions, all Icon gates green, m3+m4.
- [x] **FZ-A1** — `rung13_alt_alt_cross_arg_sideeffect` — **PASS** (the regression; fully green now).
- [→] **FZ-A2** — `rung36_jcon_kwds` — crash GONE but had a SECOND failure behind it → now WRONG-OUTPUT (1609B). Reclassified to Cluster E (monitor for first divergence; keyword-read gaps `&ascii`/`&lcase`/`&cset` suspected per prior watermarks).
- [→] **FZ-A3** — `rung36_jcon_scan1` — crash GONE, now WRONG-OUTPUT (385B). Reclassified to Cluster E.

**Cluster B — emit-time IR aborts (2 distinct bugs, 2 tests).**
- [ ] **FZ-B1** — `rung36_jcon_var` — `emit_drive IR_ASSIGN guard: nameless 2-operand assign` — assign-through-lvalue-producer (`!x`/`?x` element-variable, or `s[i:j]` section as assignment TARGET). LOWER's TT_ASSIGN terminal arm mints a placeholder instead of a real target; fix in `lower_icon.c` TT_ASSIGN (not a missing template — the abort message says so).
- [ ] **FZ-B2** — `rung36_jcon_scan` — `bb_call marshal: IR_VAR arg names a local with no LOWER-granted varslot (TE-4)` — grant the varslot in `ir_drive_slot_assign` per the BOMB message's own pointer.

**Cluster C — SEGV rc=139 (3 tests, need minimal-repro bisection each).** Run under `CSN_NO_SEGV_HANDLER=1`/`SCRIP_NO_SEGV_HANDLER` for a clean backtrace, then MONITOR→bracket→gdb-hit-count per RULES.md.
- [ ] **FZ-C1** — `rung36_jcon_endetab`
- [ ] **FZ-C2** — `rung36_jcon_fncs1`
- [ ] **FZ-C3** — `rung36_jcon_scan2`

**Cluster D — PARSE errors (ONE symptom, 2 tests): `function call: expected ) (got ;)`.** htprep line 160, prepro line 39. Icon front-end rejects some legal call syntax (likely a `;`-in-arg or nested-call form). Diagnose in `src/parser/icon/`; decide source-fix vs parser-fix (parser-fix strongly preferred — the .icn is canonical JCON).
- [ ] **FZ-D1** — `rung36_jcon_htprep` (parse error line 160)
- [ ] **FZ-D2** — `rung36_jcon_prepro` (parse error line 39)

**Cluster E — WRONG-OUTPUT, ran clean (6 tests, monitor each for first divergence).** These reach the oracle-diff mechanically — MONITOR-FIRST is the exact tool. Bracket the first divergent event, fix at the land mine.
- [ ] **FZ-E1** — `rung36_jcon_args` (out=2989B; wrong content)
- [ ] **FZ-E2** — `rung36_jcon_coerce` (out=1550B; ⚠ under `--compile`/naked `--run` this can emit ~241MB on one line — ALWAYS cap `| head -c`; the harness is safe because it captures to a var)
- [ ] **FZ-E3** — `rung36_jcon_mffsol` (out=92B)
- [ ] **FZ-E4** — `rung36_jcon_mindfa` (out=2220B)
- [ ] **FZ-E5** — `rung36_jcon_recogn` (out=0B — produces nothing; generator-in-call-arg suppression suspected)
- [ ] **FZ-E6** — `rung36_jcon_string` (out=2744B)

### ▶ RUNG: XFAIL-ZERO — sift every `.xfail` marker; fix source OR fix SCRIP; DELETE the marker (35 tests)
END STATE: zero `.xfail` files in `corpus/programs/icon/`. Per test: (1) remove `.xfail`, run it, read the real failure; (2) decide — is the `.icn`/`.expected` wrong (fix SOURCE) or is SCRIP missing/wrong (fix SCRIP)? Prefer fixing SCRIP: the `rung36_jcon_*` programs are canonical JCON and the `.expected` is graded against the real iconx/JCON oracle. Source-fix is legitimate only for a genuinely-broken test artifact. NOTE: `.xfail` files are NEVER run by the harness, so some may ALREADY pass — check each before assuming work is needed (a free win = delete marker, confirm PASS). Markers carrying a stated reason are triaged first (known root cause); the 24 empty markers need a fresh run to classify.

**Known-reason markers (11) — root cause already recorded:**
- [x] **XZ-1** `subjpos` — DONE (s4): was KNOWN HANG; now runs 28ms, byte-identical m3+m4. Marker deleted corpus `78915257`.
- [x] **XZ-2** `random` — DONE (s4): now passes m3+m4 byte-identical. Marker deleted corpus `78915257`.
- [ ] **XZ-3** `radix` — bignum: radix literals > 64 bits need arbitrary-precision ints (not implemented). Ties to lgint.
- [ ] **XZ-4** `lgint` — large-integer / bignum arithmetic (empty marker but name + radix note imply the same bignum gap).
- [ ] **XZ-5** `ck` — generative argument to `tab` (`tab(span-1|0)`) unsupported; `Image()` needs generator-in-arg; "deeper issues" noted.
- [x] **XZ-6** `level` — DONE (s4): passes m3+m4 byte-identical (upstream fix landed). Marker deleted corpus `78915257`.
- [ ] **XZ-7** `profsum` — `next` inside `line ? {}` doesn't restart enclosing `while`; next/break propagation through scan body.
- [ ] **XZ-8** (reserved — refold if another reasoned marker surfaces on fresh read)
- [ ] **XZ-9** (reserved)
- [ ] **XZ-10** (reserved)
- [ ] **XZ-11** (reserved)

**Empty markers (24) — classify on a fresh run, then fix or delete.** Batch by first-failure signature after un-quarantining; expect them to fold into the same clusters as FAIL-ZERO (bignum, generator-in-arg, scan control-flow, io). List: `arith btrees case checkfpx collate cxprimes diffwrds errkwds errors evalx every fncs geddump gener image io iobig large misc nargs others prefix recent sets sieve sorting struct toby`.
- [ ] **XZ-E-BIGNUM** — the arithmetic/number cluster (`arith`, `checkfpx`, `cxprimes`, `radix`✓, `lgint`✓) — likely all one bignum/real gap.
- [ ] **XZ-E-STRUCT** — `btrees`, `sets`, `sorting`, `struct`, `sieve`, `collate` — list/set/table/sort builtins.
- [ ] **XZ-E-GEN** — `every`, `gener`, `evalx`, `nargs` — generator/argument semantics.
- [ ] **XZ-E-IO** — `io`, `iobig`, `image`, `errors`, `errkwds`, `others`, `recent`, `misc`, `case`, `diffwrds`, `prefix`, `large`, `fncs`, `geddump` — classify individually; io + image + error-keyword families.

## ⌚ WATERMARK 2026-07-17 s90 (Claude Fable 5 · SCRIP src `496e62f4` + 6-file NCB-1d edits UNCOMMITTED · corpus `f69dd89f` + 10 icon-bench .s uncommitted) — NCB-1d landed: det lexical procs join jmp-entry; Icon 237/20/32; Raku 283/283 both modes; SN4 m3 305/2 DIVERGE 10

**Scope:** NCB-1d implementation session per Lon's "RSP/RBP FORTH ζ for ALL, sharing the C runtime stack; look at what SNOBOL4 has done."  Root-caused the s84 proc bug to the call-regime/self-alloc mismatch; converted det lexical procs to the SN4 jmp-entry protocol (admission + lexprep prologue tail + depth-immune rbp-absolute det epilogues + site guard widening + the `rt_proc_t.jmp_entry` regime record consulted by all five C transfer windows; `gram__*` scan-protocol boxes name-declined).  All numbers fresh-measured with stash-A/B attribution: Icon harness 205→**237**/20/32, honest sweep CLEAN 200→**236** (zero regressions by comm-diff), icon smoke **14/14 BOTH modes**, Raku **283/283 both modes** (HEAD measured 209/74 — all 74 pre-existing failures fixed), SN4 crosscheck m3 303/4→**305/2** (`test_case`+`140` = EVAL deep-arrival class the old rsp-relative epilogue comment predicted), m4 295→**304** DIVERGE 12→**1** (stratum-2 anchor fix cleared the pat_fence/abort family), SN4 smoke 7/7×2, prolog 3/5 (pre-existing at HEAD, attributed by stash), gates green except strict-medium WIP residue xa_flat 96→100 (4 raw-arm adds, s84 precedent).  Artifacts regenerated (feature/bench/demo committed by their utils; 10 icon-bench .s pending the source commit).

## ⌚ WATERMARK 2026-07-17 (Claude Opus 4.8 · SCRIP `11e36fae` s83 · corpus `78915257`) — RSP/RBP ζ measurement across full suites; refs from GitHub; per-instance-stack directive noted

**Scope:** Measurement + orientation session, no code committed. Built scrip + libscrip_rt at HEAD `11e36fae` (RSP/RBP FORTH-style ζ is the default for ALL zeta allocations here). Ran BOTH full Icon suites: **mode-3 `--run` = 205/52/32/289; mode-4 `--compile` = 195/62/32/289** by the stdout-only harness (Lon ask: "how much of Icon is still running using RSP/RBP for ALL ζ allocations"). Delta vs the documented R12 baseline (242/15/32 at `b404fb95`, NOT re-run this session) = **−37 mode-3**. **🚨 But an exit-code-aware re-sweep found the 205 is a stdout-only illusion: CLEAN (stdout ok + exit 0) = 0/289; all 205 "passes" print correct output then abort rc=134 (`*** stack smashing detected ***`) — the RSP/RBP ζ FORTH stack overruns the native C-stack canary. Under RSP-for-ALL-ζ, ZERO Icon programs exit cleanly.** The stdout-only grading (harness L92/97) masked a total-corruption regression; an exit-code check is a needed harness fix. The ~18-commit REG-7 RBP-consumer-flip series since the s65 flip (`f7de3863`) recovered only +1 for Icon — that work was SNOBOL4/shared, not Icon. Frame invariants hold under RSP (`no_stack`=0, `one_reg_frame`=0, semicolon prison green); mode-4 smoke red at 10/14. mode-4 FAILs ⊃ mode-3 FAILs + 10 compile-path-only casualties (scan/string-builtin/IO). Regressed population = basic proc/suspend/loop/global/record/strretval/case rungs (`rung02/03/09/13/21/24/25/32/33/37`) — consistent with FINDING §8 (RSP migration incomplete for Icon's scan-family + generator/reflection paths). Set up `refs/` from GitHub canonical upstreams (zips did not arrive): `gtownsend/icon` + `proebsting/jcon`. **Noted new Lon directive:** co-expressions + generator procedures get their OWN stack PER INSTANCE (ζ-allocation half of the co-expr model). **No SCRIP/corpus code changed; main tree untouched.** **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8

## ⌚ WATERMARK 2026-07-15 s5 (Claude Sonnet 4.6 · SCRIP `b404fb95` · corpus `78915257`) — orientation + IR_MOVE_LABEL eradication directive

**Scope:** Pure orientation + analysis session. No code committed to SCRIP or corpus. Established refs/ symlinks from uploaded zips. Confirmed clean baseline 242/15/32 at `b404fb95` (re-derived fresh). Measured and proven: (1) HEAD `96fb698c` is **204/53/32** — 38-test regression from `f7de3863` RSP-frame default flip, **not Icon's bug to fix** (R12-ERAD session owns recovery). (2) Icon's `|` top-level alternation uses IR_DISJUNCTION + IR_MOVE_LABEL (lower_icon.c:820); IR_IF uses IR_INDIRECT_GOTO + two IR_MOVE_LABELs — both are the "label indirection instead of self-state" anti-pattern. (3) ARBNO is SNOBOL4-only; Icon does not produce it. (4) Icon `|` lowering is Icon-owned (`lower_alt`, `lower_icon.c:820`) producing IR_DISJUNCTION — different from SNOBOL4's IR_MATCH_ALTERNATE. (5) Lon directive: eradicate IR_MOVE_LABEL from Icon; reshape IR_DISJUNCTION into nary self-state form mirroring IR_MATCH_ALTERNATE / IR_SCAN_ALTERNATE; make the BB hold its own state variables. Design captured in `FINDING-2026-07-15-CLAUDE-ICON-MOVE-LABEL-ERADICATION-VIA-BB-SELF-STATE.md`. **No code changes. SCRIP main tree green and untouched.** **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 s4 (Claude Sonnet 4.6 · SCRIP `b404fb95` · corpus `78915257`) — 3 xfail markers deleted; FZ-B1 and FZ-E root causes corrected

**Scope:** ZERO-FAILURE MANDATE session. **XFAIL-ZERO: 35→32** — deleted stale markers for `level`/`random`/`subjpos` (all now pass m3+m4 byte-identical, confirmed stable). FAIL count held at 15 (no regressions). **FZ-B1 `var` diagnosis corrected:** DT_N/NAMETRAP already exists; real gaps are (a) no lvalue-of-variable() lowering case in lower_icon.c and (b) per-proc runtime name→frame-offset table for locals needed by rt_icon_variable(). Full diagnosis in LIVE CURSOR. **FZ-E scan-family root cause found:** disjunction fail-edge wired to arm-B β instead of α in emit.cpp IR_SCAN_SEQUENCE case (~L887-904, L1101); minimal repro isolated. recogn/scan/scan1/scan2/string share this root cause — NOT generator-in-call-arg as previously noted. All Icon gates green (smoke 14/14 m3+m4, semicolon prison, no_stack, one_reg). **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 s3 (Claude Sonnet 4.6 · SCRIP `b24c63c7` · corpus unchanged) — orientation only; 239/15/35 independently verified; refs/ symlinks established from uploaded zips

**Scope:** Pure orientation session. No code changes. Built scrip from HEAD `b24c63c7` (6 commits ahead of s2 cursor — all Raku/Pascal, zero Icon). Independently re-ran full Icon suite: **239/15/35 confirmed byte-identical to cursor**. All 4 Icon gates green, smoke 14/14 m3+m4. Set up `refs/jcon-master` + `refs/icon-master` symlinks from user-uploaded zip archives (RULES.md CONSULT CANONICAL SOURCES setup). Read `ir_a_Scan` from canonical `irgen.icn` as first look at Cluster B/scan territory. Next session: begin FAIL-ZERO work at first open rung (FZ-B1 or FZ-B2 per Lon direction). **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 s2 (Claude Sonnet 4.6 · SCRIP `50249fd5` · corpus unchanged) — control-in-value fix landed; cluster diagnoses corrected; 239/15/35 maintained

**Scope:** Full session-setup baseline confirmed (239/15/35 byte-identical to cursor). Investigated all 15 FAILs; corrected cluster descriptions — every cursor claim was measured against a minimal repro, not trusted from prose. **LANDED `50249fd5` — control-in-value fix:** `while`/`until`/`repeat`/`every` were setting `*res` to a control `IR_GOTO` and routing loop-exit to γ (success). Icon semantics: these produce no value and fail as expressions. Fixed all four in `lower_icon.c`: route exit to ω, `*res = NULL`. Safe for statement context (succ==fail in `lower_proc_body`). `image(while write(move(1)))` now correctly reaches `| "none"`. `scan` advanced past its TE-4 bomb. **Verified:** 239/15/35 zero-regression, all 4 Icon gates PASS, smoke 14/14 m3+m4, Prolog 5/5, m4 compiles. **Diagnoses:** FZ-B1 `var` blocked on pointer-hole arch (Lon). FZ-B2 `scan` new blocker: bare scan functions outside `s ? …` read uninit Σ/δ/Δ. FZ-D1/D2 `htprep`/`prepro`: Icon preprocessor (unbuilt). FZ-E cluster: generator-argument-to-procedure, distinct second root cause. **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6

## ⌚ WATERMARK 2026-07-15 (Claude Opus 4.8 · SCRIP `e18b038a` · corpus unchanged) — ZERO-FAILURE MANDATE opened; FZ-A1 landed (238→239/15/35); goal file pruned

**Scope:** fresh full Icon suite run corrected the cursor (claimed 239/15, reality was 238/16 — `rung13_alt_alt_cross_arg_sideeffect` regression, HEAD newer than s5). Authored FAIL-ZERO (16 steps, 5 clusters) + XFAIL-ZERO (35 markers) ladders. **FZ-A1 LANDED (SCRIP `c822995a`→`e18b038a`):** `x86_parse` eager pre-parse (`x86_asm.h:1057`) aborted on bracket-bearing string literals (`.string`/comment payloads containing `[...]`, e.g. `write("[x]")`); abort replaced with the benign `XK_SYM` fallthrough the fn already uses. rung13 PASS; kwds/scan1 crash lifted → wrong-output (Cluster E). Zero regressions, all Icon gates green, m3+m4. Then pruned this goal file (watermarks → last 3; stale scan-design cursor bullets removed).

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)
No language-specific logic in any BB/XA template: templates dispatch on IR shape + representation flags only. FORBIDDEN inside `src/emitter/{BB,XA}_templates/`: `IR_LANG_*`/`LANG_*`/`is_<lang>` guards, language-named template fns/files/dispatch arms, hardcoded language-builtin names. Per-language behavior lives in the runtime (by-name dispatch) or in LOWER (different IR shape → its own BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md`; fix ladder LB-* in GOAL-PASCAL-BB.md. COMPLETION TEST: the audit's Tier-1 grep over both template dirs == 0.

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
"duplicate the byte-producing code into each template file" clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--run` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--run`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

> **⚠️ `wire_seq`/`wire_alt` (lower.c)** were strictly generalized 2026-05-31 (fail-chain walks past bounded
> elements; alt arms lower right-to-left), re-proven non-regressive for Icon — relevant only if you edit them.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog's goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static'd into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer's. This is what makes concurrent sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | (retired) | RW box-locals → `[r12+off]` (ζ frame); RO → `[rip+disp]`. r10 RETIRED (R10-OUT) |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**DUAL ROLE — R13/R14/R15 ALSO CARRY THE PROLOG TRAIL (RATIFIED Lon 2026-06-13).** Prolog has no subject string, so the subject trio Σ/δ/Δ is idle and instead carries the TRAIL — Prolog's one main attraction (its single shared binding-undo spine) — in the SAME base/cursor/end shape, casing preserved (UPPER = fixed, lower = moving):

| Reg | subject (SNOBOL4/Icon) | Prolog TRAIL — `Trail{stack;top;capacity}` |
|-----|------------------------|---------------------------------------------|
| **R13 = Σ** (UPPER, fixed) | subject BASE ptr | trail `stack` — base of the `Term*` array |
| **R14 = δ** (lower, moving) | CURSOR | trail `top` — the mark; "push" = ++, "unwind" = set back |
| **R15 = Δ** (UPPER, fixed) | subject LENGTH/END | trail `capacity` — the fixed bound |

The physical registers are SHARED — never live in two languages at once. A cross-language BB jump save/restores the trio (DEFERRED — its own later rung; not yet wired). The trail in registers replaces the `g_resolve_trail` symbol load with pure register traffic. **RBP stays RESERVED** (its brokered-frame role is dead under NO C BYRD-BOX; held for a future use TBD — Lon). This DUAL-ROLE addition is byte-identical across all three GOAL files; the subject rows above remain each file's own.

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).


## ⛔⛔ GROUND ZERO 3 — STACKLESS (Reset 2026-05-30) ⛔⛔

Values live in flat per-box slots at emit-time offsets; consumer reads producer's slots directly. Unbounded backtrack = per-box arena indexed by depth, never push/pop. Inter-box transitions are `jmp rel32`. **References:** `test_icon.c` (flat goto target) · `test_sno_1/2/3.c`.

**GATE:** `grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c | grep -v _pl_ | wc -l` == 0.

### ⛔ ALWAYS TEST BOTH NATIVE MODES (m2/--run DELETED)

Every test runs `--run`/`--compile` on the SAME source. Done = m3+m4 PASS or LOUDLY EXCISE. HARNESS: `scripts/test_icon_rung_suite.sh [--rung R] [--mode all|run|compile]`. Stubbed kind → `[SMX] EXCISED` (exit 0). m4 needs `make libscrip_rt` + gcc.

### Rung ladder

- [x] **ICN-STORAGE** — GST-1/2 + GVA-1/2 + LVA-1 LANDED (globals `[rbx+k*16]` mode-4; locals locked ζ-frame, gate `test_gate_icn_local_no_nv.sh`). Open remainder: **GVA-M3** (mode-3 in-process globals still NV; optional) → `GOAL-ICN-GVA-M3.md`. Analysis: `ICON-AUDIT-2026-06-24.md` §C. Unblocks `initial`/`static` (the `.bss __gva` arena is their persistent-writable-static region).
- [ ] **GZ-DEFER** — EVAL / CODE / `*P` deferred patterns.
- [ ] **GZ-11+** — `not`/`size`/`nonnull` `bb_unop` · relop remainder · generator-operand binops (Fig-1) · `rt_call_builtin` · lists/tables/records/csets/sort.

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

---

## Premise

Icon IS a Byrd-Box port-graph; every construct is a box; no SM, no value stack. Modes 3/4: `push r12; mov r12,rdi; jmp .Lroot_α`; boxes in `bb_pool`/linked binary; transitions are `jmp rel32` — no call/ret/dispatch/broker/walker/push-pop. Target shape: `test_icon.c` (flat goto, named slots, three-column LABEL/ACTION/GOTO).

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes for an Icon program.** Completion: `./scrip --dump-sm prog.icn` → `; SM_sequence_t  count=0`.

## ⛔ ICON SEMICOLON-REQUIRED — NO NEWLINE PROCESSING, EVER (FACT RULE — Icon, Lon directive 2026-06-23)

**SCRIP Icon REQUIRES an explicit `;` between bare statements. The Icon front-end does ABSOLUTELY NO
newline processing — a newline is plain whitespace and NEVER becomes a statement separator.** The
canonical `icont` "optional semicolon" mechanism (newline → `;` insertion when the previous token is an
Ender and the next is a Beginner — `refs/icon-master/src/common/tokens.txt`, `src/h/lexdef.h`) is
**FORBIDDEN in this codebase.** SCRIP is its own dialect: statements are `;`-terminated, full stop. A
program with bare statements separated only by newlines is a PARSE ERROR, by design, and that is correct.

**WHY THIS RULE EXISTS IN ITS PRISON FORM.** A session ADDED newline-to-`;` insertion to the Icon lexer
(the Beginner/Ender table + newline-crossing `TK_SEMICOL` synthesis) — exactly the thing forbidden here —
to make canonical newline-style benchmark sources parse. It was reverted byte-for-byte, but a plain rule
("Icon requires semicolons") did not prevent it. The rule now has STRUCTURAL + BEHAVIORAL ENFORCEMENT so
it cannot recur. Canonical newline-style sources are adapted by ADDING `;` to the SOURCE (a corpus matter),
NEVER by teaching the compiler newline processing. KEEPING A BENCHMARK PARSING IS NOT A LICENSE to insert
newline handling — when a benchmark and this rule conflict, the **rule wins**: the source gets semicolons.

**FORBIDDEN inside `src/parser/icon/`:** any Beginner/Ender token classification used for separator
insertion (`tok_is_beginner`/`tok_is_ender`/`Beginner`/`Ender` flags), any newline-crossing detection that
synthesizes a separator (`prev_line` comparison driving a `TK_SEMICOL`), any one-token buffering whose
purpose is to inject a separator (`have_pending` + synthetic `TK_SEMICOL`), and minting `TK_SEMICOL` from
anything other than the literal `;` character. The lexer treats `'\n'` as whitespace (the `isspace` path in
`skip_ws`) and emits `TK_SEMICOL` ONLY from `case ';'`.

**ENFORCEMENT — THE PRISON (`scripts/test_gate_icn_semicolon_required.sh`), three independent locks, ALL
must hold:** LOCK 1 (negative grep, comments stripped) — zero newline-insertion machinery in
`src/parser/icon/*.c|*.h`. LOCK 2 (mint-site) — exactly ONE `make_tok(TK_SEMICOL,...)` site in
`icon_lex.c` (the `';'` case). LOCK 3 (behavioral canary, identifier-name-independent) — a two-bare-
statement program separated by a NEWLINE MUST be rejected with a parse error, and the same program with an
explicit `;` MUST parse. Reintroducing insertion must defeat all three; LOCK 3 pins the actual behavior so
a rename cannot evade it. **COMPLETION TEST:** (a) `scripts/test_gate_icn_semicolon_required.sh` exits 0;
(b) it is in the Session-Setup gate list; (c) the newline canary parse-errors and the semicolon canary
parses; (d) `src/parser/icon/icon_lex.c` mints `TK_SEMICOL` only from the literal `;`.

## ⛔ CONSULT CANONICAL SOURCES (JCON + Icon)

Every port-topology / resume-wiring / builtin-semantics question: read canonical FIRST — `refs/jcon-master/tran/irgen.icn` and `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `ocomp.r`, `fscan.r`). The m2 oracle is a transcription; canonical wins. Extract uploaded zips into `refs/` at session start if absent.

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
./scrip --compile /tmp/rung_NN.icn  > out_m4.s

bash scripts/test_icon_rung_suite.sh --rung rungNN
make libscrip_rt

bash scripts/test_gate_icn_no_stack.sh
bash scripts/test_gate_icn_one_reg_frame.sh
bash scripts/test_gate_icn_semicolon_required.sh
bash scripts/test_gate_icn_local_no_nv.sh
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_prolog.sh
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.
- Reintroduce the value stack for Icon in any form.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh                   # m3 12/12 · m4 12/12
bash scripts/test_smoke_prolog.sh                 # PASS=5
bash scripts/test_gate_icn_semicolon_required.sh  # PASS (PRISON)
```

---

## Watermark

**2026-07-01 measured (this sandbox, SCRIP `6a509382`, local):** `test_icon_all_rungs.sh` PASS=190 FAIL=63 XFAIL=36 /289 · icon smoke 12/12 m3+m4 · no_stack 0 · one_reg 0 · semicolon prison green · local_no_nv PASS · `audit_jcon_wholesale.sh` 64/66. Older per-session tallies (a different harness era) and the 2026-06-2x session logs were DELETED 2026-07-01 per RULES.md "DELETE completed steps" — full narratives in git + `.github/HANDOFF-*.md`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c`

## Session-close / push protocol
See RULES.md — the computed-status FACT RULE (`scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim) and the companion rule forbidding the word "HANDOFF" in assistant-authored prose at close. The two rule bodies formerly duplicated here were deleted 2026-07-01; RULES.md is the single home.
