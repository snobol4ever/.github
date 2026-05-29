# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`).

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself.

### Milestone 3 ⏳
All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md`. Find goal in table below.
3. Read `RULES.md` in full.
4. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
6. **If MODE3-EMIT or MODE4-EMIT — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.**
7. Open Goal file. Open that repo's REPO file.
8. Run Goal file's `## Session Setup` scripts.
9. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-9-6 user-proc dispatch LANDED ✅ — corpus same-sweep 69→82 PASS (+13), 0 regressions (worktree-verified), SEGV 0, ABORT 0** (Opus 4.8, 2026-05-29, one4all `8d4c2c2f`). The `bb_call: unsupported call shape` ABORT cluster (~158 aborts) is GONE. JCON `ir_a_Call`/`ir_a_Return` in the flat-slab model: a user proc compiles to a `bb_build_flat` slab that leaves its return value on the vstack; new `rt_icn_call_proc` (rt.c) binds params as named vars (Icon BB mode-3 uses NV not frame slots), invokes the slab (built LAZILY on first call so unreached unsupported procs don't abort), reads the result by vstack depth-delta, restores bindings (recursion-correct). Landed: (1) Icon proc registry + lazy builder in `rt.c`/`rt.h`; (2) new `bb_return.cpp` template (value-on-vstack → `jmp γ`; bare return pushes null), wired `bb_templates.h`/`emit_core.c`/Makefile; (3) `emit_bb.c` `flat_drive_return` (routes to slab-level exit `flat_succ_p`, not next stmt — a return exits the proc) + `flat_drive_call_userproc` + `BB_BINOP_GEN` non-streaming collapse (`n*fact(n-1)` → plain binop, matching the mode-2 oracle which finds neither operand streams); (4) `bb_call.cpp` userproc arm + `write(proc())` via any-write trailer; (5) `scrip.c` driver registers all proc entries + lazy builder before main. Newly passing: rung02_proc_add_proc/fact, rung03_suspend_fail/return, rung09_loops_repeat_counter/until_while, rung21_global_initial_×3, rung25_global_×4. Gates: FACT 0, smoke icon/prolog 5/5, broker 51/11, zero-SM holds. Edge cases byte-identical: 0-arg, nested, recursion, early/bare return. Deferred: generator procs (`suspend` → odometer); rung02_proc_locals (blocked on `every ival=2`, IBB-9-4). Prior: **IBB-9-UNOP** value-producing unary ops (one4all `cc7995c4`); **IBB-9-2 while/until + swap + write(ALT)** (`aeb83416`). **NEXT:** scanning subsystem (~11 FAILs); `every ival=2/3` (IBB-9-4/5); generator-proc dispatch; finish unop family (SIZE/RANDOM); `||` lconcat; BB_CASE; BB_AUGOP-in-every (rung10). Deferred refactor **IBB-9-RELOP-PORTS**. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PLR-J-5 LANDED — native multi-clause/disjunction/recursive dispatch** (2026-05-29, Opus 4.8, one4all `0b77ba71`). Ported the MEDIUM_TEXT `BB_CHOICE` dispatcher AND the `BB_PL_ALT` disjunction arm to MEDIUM_BINARY (raw bytes via `bb_bin_t`; every `@PLT`→`movabs rax,&fn; call rax` for in-process mode-3 native), wired BB_PL_STRUCT operands in the BINARY unify arm through PLR-J-3's `emit_build_compound_term_bin` (was honest-abort-guarded; uses the TEXT arm's 16-byte scratch-slot alignment so rsp stays 16-aligned across a compound-R build's internal `call rt_pl_compound_build_n`), and removed the multi-clause guard in `SM_BB_PL_INVOKE`. Cross-block label identity (template dispatcher ↔ driver-emitted clause bodies) via `emit_label_intern` of `cbody[i]`/`cpre[i]`/`exit_γ` in `flat_drive_pl_choice`/`_alt` (mirrors PLR-J-4 linkage; behaviorally identical in TEXT/mode-2). **DISCOVERY: `bb_pl_alt.cpp` BINARY was ALSO a double-jump stub and was the actual first blocker** — `( G ; true )` mains route through ALT, not BB_CHOICE; both arms ported in lockstep. **Multi-clause/recursive/disjunctive predicates now run natively in mode-3** (3-mode AGREE: `pick/1`→`1/2/3`, recursive `member/2`→`a/b/c`, `color/1`→`red/green/blue`). 5 files +225/-45. **GATE-2 crosscheck 11 → 33 PASS (+22)** — the ladder's bulk-unblock. Gates: GATE-1 5/5, GATE-3 m2 104/107 (byte-identical), GATE-4 4/4, GATE-SWI 57/57, FACT 0/12, siblings 5/5/13; mode-3 native rung suite 29/107 (remaining = unported builtin BINARY arms). **PLR-J ladder J-0..J-5 COMPLETE.** Two findings (NOT introduced/NOT fixed): `rung05_backtrack.ref` has a literal `-e ` echo artifact (lone ORACLE_MISS; all 3 modes correctly print `a/b/c`); mode-2 `--interp` loops on cut-in-disjunction-with-fail (pre-existing at parent `8d096733`; mode-3 native gives the CORRECT single answer). **NEXT:** unported builtin BINARY arms (findall/3, format-compound, char_type/2, numbervars/3, writeq — the mode-3 rung-suite 78 fails), or orthogonal mode-2 cut-in-disjunction loop, or orthogonal mode-3 nested-`is` (`R is 3*10+4`→`6`). [Prior: **PLR-J-4** (`8d096733`) callee-block sweep + `bb_pl_call` BINARY; **PLR-J-2** (`751c5f10`) explicit per-node resume; **PLR-J-0** (`e2d99c3d`) bounded classifier; **PLR-J-3** (`bbf60667`) compound-term builder; **PLR-J-1** (`efbdd61c`) type-test BINARY arm.] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-1016-EVAL-SLEN LANDED ✅** (Opus 4.8, 2026-05-29). **Native 251→252 (+1, this session total +2 with SBL-1010); zero regression.** `*expr` (deferred/unevaluated expr, EVAL target) lowers to `SM_PUSH_EXPRESSION entry_pc` → `DT_E` descriptor read by `EXPVAL_fn`: slen==1 → `sm_eval_subexpr(entry_pc)` (SM-PC path); slen==2 → `call *i` (thunk, for mode-4 where the subexpr is a real `lea`-emitted code addr). The mode-3 native MEDIUM_BINARY arm of `sm_push_expression_str` (`sm_expr_incr.cpp`) wrongly set `mov esi,2` (slen=2) while `rdi`=`movabs <entry_pc>` (a raw SM PC, e.g. 5) → `EXPVAL_fn` did `call *5` → SIGSEGV. Mode-2 builds slen=1. Fix: BINARY arm `u32le(2u)`→`u32le(1u)` (one immediate) → `{slen=1, i=entry_pc}` like mode-2; MACRO/TEXT arms (mode-4 thunk) untouched. 1016_eval 3/3 byte-exact (concat/var-ref/failing-expr); FAIL-diff = exactly 1016 newly green. Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-2 oracle 252 unchanged, broker 51/11, cross-lang 5/5/5/5, FACT 0, audit GATE OK. Also triaged **1011/1013/1017 as m2 oracle gaps** (fail BOTH modes — DEFINE-redefine / NRETURN-lvalue / ARG-local — fix the oracle first, native parity follows for free). **NEXT: SPAN/ARBNO/FENCE BINARY-arm clusters (~24 native fails); the m2-oracle bucket (1011/1013/1017 + 044/045/etc); then flip default to native.** [Prior: **SBL-1010-ALIAS-ALTENTRY-FIX** native 250→251 (`_usercall_hook` alias/alt-entry resolution); **SBL-BREAKX-2 + SBL-DATA-FN-SHADOW** 245→250; **SBL-NATIVE-FN-1** +2; **SBL-DEFER-NESTED** +20.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-NFA-1b DONE — NFA→isolated BB_NFA_* graph builder** ✅ (Opus 4.8, 2026-05-29, one4all `6b593da8`). `raku_nfa_to_bb(Raku_nfa*)→BB_graph_t*` state→node walk in `raku_nfa_bb.c` (zero `snobol4_pattern.c` contact): `nfa_kind_to_bb` 1:1 `Nfa_kind`→`BB_NFA_*`, one `BB_t`/state, γ=out1-node β=out2-node(SPLIT) ω=NULL, payload CHAR ival=char / CLASS sval=32-byte cset / CAP ival=group-idx, entry=start node, NULL on Phase-2 kinds. Verified standalone across L1-L15 (graph mirrors the NFA; ports/entry/payload correct). Pure graph construction, NO x86, dead-code-until-RK-NFA-4. Gates unchanged: m2 41/42, m4 42/42, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0. **NEXT: RK-NFA-4** — NEW `bb_nfa_*.cpp` mode-4 templates (FACT-pure, four-port, opcode names from `Nfa_kind`) + `SM_BB_INVOKE` over the graph on `~~`; then **RK-NFA-5** mode-3 native (closes 6 CRASHes). [Prior: **RK-NFA-1e** (`0d94e255`) closed the whole mode-2/mode-4 regex cluster via the SM byname path, m2 35→41 m4 36→42 perfect.] |
| **PP-PURE** | `GOAL-PURE-TEMPLATES.md` | PP-PURE-2 — xa_bb_ptr_slot side-effect fix + SM locals. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **Mode-4 SN4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | M4SN-5 or M4SN-6. 250/280 ✅. |
| **PST Parent** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | Stage 2 PST-LR-0 bulk rename. |
| **PST SNOBOL4** | `GOAL-PST-SNOBOL4.md` | SN4-SC-6 smoke blocked by EC-3* regression. |
| **PST Snocone** | `GOAL-PST-SNOCONE.md` | MIRROR-GAP-SC-SC-5: XDSAR in bb_build_brokered. |
| **PST Raku** | `GOAL-PST-RAKU.md` | PRF-14-6 OPEN — leaf-pushers misuse shift. |
| **SN4 JVM** | `GOAL-SN4-JVM-EMIT.md` | SJ4-JVM-4 done. Beauty.sno halts at Parse Error. smoke 13/13. |
| **SN4 .NET** | `GOAL-SN4-NET-EMIT.md` | SN4-NET-5d — SM_PAT_* wiring. smoke_net 9/9, broker 23/49. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed; IEP-5/6/7/9 blocked on CHUNKS. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2 — delete bb_node_t path. |
| **Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | SCT-1f or SCT-BEAUTY-SC-PARSE. |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| corpus | `REPO-corpus.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles AST to SM_Program. INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
