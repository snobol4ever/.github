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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-9-SIZE `*E` size unop LANDED ✅ — corpus same-sweep 92→93 PASS (+1), 0 regressions, SEGV 0** (Opus 4.8, 2026-05-29, one4all `254c93a6`). `*E` (BB_SIZE) routed to the stub `bb_limit` in mode-3 (emitted nothing → write trailer ABORTed); rerouted to `bb_unop` + new `rt_unop_size`, with `icn_size_value` extracted from the mode-2 BB_SIZE arm as the single source of truth both modes call (byte-identical by construction). `write(*s)` now works. **Prior: IBB-9-CONCAT `\|\|` string concat LANDED ✅ — corpus same-sweep 82→92 PASS (+10), 0 regressions (passlist-verified), SEGV 0, ABORT 146→133** (Opus 4.8, 2026-05-29). The single largest concrete ABORT cluster (`bb_binop: unsupported op ival=11`, 13 programs) is GONE. `s1\|\|s2` lowers to a tree-shape `BB_BINOP` op=ICN_BINOP_CONCAT (ival=11) — same shape as arith, driven by the op-agnostic `flat_drive_binop_tree`. Fix: (1) CONCAT arm in `bb_binop.cpp` (proven 32-byte arith layout, dead `movabs rdi,0` keeping γ/β/ω patch offsets {23,27,28}, calls `rt_icn_concat`); (2) new `rt_icn_concat` in `rt.c` routing through `icn_binop_apply` (the mode-2 oracle's CONCAT arm) so m2==m3 byte-identical by construction — distinct from the SNOBOL4 `rt_concat`/`CONCAT_fn` (different descriptor convention, cross-family). Newly passing: rung04_string_concat/chain/str_var, rung11_bang_augconcat_augconcat ×3, rung32_strretval ×4. Gates: FACT 0, canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 51/11. Deferred (→ IBB-9-4/5): generator-bearing concat (bang/alt/every) now RUNS but emits only the first generated value — needs generator re-pumping through the binop. **NEXT:** the ABORT residue is dominated by `bb_call: unsupported call shape` (Icon builtins — table/MAKELIST/set/list + string fns trim/reverse/repl/map/center/left/right/etc, write with non-int/non-str arg kinds); `every ival=2/3` (IBB-9-4/5); generator-proc dispatch; finish unop family (SIZE/RANDOM); BB_CASE; BB_AUGOP-in-every (rung10). [Prior: **IBB-9-6** user-proc dispatch 69→82 (`8d4c2c2f`); **IBB-9-UNOP** value-producing unary ops (`cc7995c4`); **IBB-9-2** while/until + swap + write(ALT) (`aeb83416`).] |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PLR-K-2 LANDED — char_type/2 mode-3 native + mode-4 emit** (2026-05-29, Opus 4.8). char_type/2 had a mode-2 oracle arm but NO emitter arm → fell to the double-jump stub in BOTH mode-3 (BINARY) and mode-4 (TEXT): boolean tests wrongly succeeded (`char_type('3',alpha)`→yes), extractor forms printed `_`. New `rt_pl_char_type` effect helper (`bb_exec.c`, transliterates the mode-2 oracle): boolean alpha/alnum/digit/space/upper/lower/punct/graph/csym/csymf/end_of_line/newline→1/0; extractors digit(V)/to_lower/to_upper/upper/lower/code→unify derived value into inner var under trail mark. MEDIUM_BINARY arm (mode-3): rdi=k0 rsi=i0 rdx=s0 rcx=ty r8=is_compound r9=ki, [rsp+0]=ii [rsp+8]=si (sub rsp,16), string ptrs absolute movabs. MEDIUM_TEXT arm (mode-4): byte-twin via @PLT + lea[rip+strtab]. **GATE-2 43→47 (+4); mode-3 native rung 39→43 (+4); mode-4 rung21 →5/5** (closes CAT-D char_type mode-4 gap). All 5 rung21 char_type 3-mode AGREE byte-identical (alpha→yes/no, digit_val→7, space_alnum→yes/yes/yes, to_upper_lower→A/z, upper_lower→a/B). Gates: G1 5/5, G3 m2 104/107 byte-identical, G4 4/4, FACT 0/12, siblings 5/5/13. **NEXT:** numbervars/3 (rung20); type-test BB_PL_STRUCT compound (`rt_pl_type_test_term`); writeq/write_canonical (rung22); format compound (rung19); retract (rung14); string_io (rung24); findall/3 last. [Prior: **PLR-K-1** atom-builtin BINARY arms (Gate-2 33→43); **PLR-J-5** native multi-clause/disjunction/recursive dispatch (one4all `0b77ba71`); PLR-J ladder COMPLETE.] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-ARB-CAT-BACKTRACK + SBL-CAP-OUTPUT-R10 LANDED ✅** (Opus 4.8, 2026-05-29). **Native broad 252→255 (+3: 124_pat_regex_keyword_seal, word2, word3); mode-4 194 unchanged; zero regressions; +1 native SEGV class eliminated.** (A) SBL-ARB-CAT-BACKTRACK: corrected the prior session's WRONG "capture-registry" diagnosis — `'xx' ARB 'xx'` fails even with NO capture, so it's an ARB-backtracking bug. `flat_drive_cat` (`emit_bb.c`) multi-kid loop wired every kid's ω to the shared `right_ω → left_β` (= kid[0].β), so a failing trailing element skipped a *middle* generator's β (grow-retry). Fix (2 lines): `kid[i].ω → kid[i-1].β`. 2-kid already correct; only 3+ CATs with a non-last generator (ARB/SPAN/ARBNO) broke. word2 byte-identical to `.ref` + oracle. (B) SBL-CAP-OUTPUT-R10 (`28a720f2`): `bb_capture.cpp` BINARY arm called `rt_cap_assign_cursor` without preserving `r10` (= &Δ, caller-saved); `NV_SET_fn(OUTPUT)`'s print path clobbers r10 → post-assign `[r10]` consumer SIGSEGVs. Fix: `push r10` twice (preserve + keep rsp 16-aligned) around the call. word1's SEGV → clean fail. Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), broker 57/5, audit GATE OK, FACT 0, cross-lang 5/5/5/5. **NEXT: (1) DEFERRED capture-commit** (word1: native + oracle both commit `.` immediately at each ARB backtrack step → OUTPUT prints intermediates; route through the capture-registry, commit once on full match). **(2) mode-2 (`--interp`) DEFER backtracking** (bare `ARB` → single-shot `BB_PAT_DEFER`; give DEFER β=self + resume embedded sub_bb via `bb_exec_resume`). Then SPAN/ARBNO/FENCE BINARY clusters; m2-oracle bucket (1011/1013/1017). [Prior: **SBL-1016-EVAL-SLEN** 251→252; **SBL-1010-ALIAS-ALTENTRY** 250→251; **SBL-BREAKX-2 + SBL-DATA-FN-SHADOW** 245→250; **SBL-NATIVE-FN-1** +2; **SBL-DEFER-NESTED** +20.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-NFA-4 SCAFFOLD LANDED — mode-4 BB_NFA_* emission begun** ✅ (Opus 4.8, 2026-05-29, one4all `ac1bc66b`). NEW `bb_nfa.cpp`: trivial passthrough templates `bb_nfa_eps`/`cap_open`/`cap_close` (pure `jmp γ`, clone of `bb_eps`); all 10 `BB_NFA_*` opcodes wired into `emit_core.c` dispatch (3→templates, 7 consuming/branching→`bb_stub` placeholder); prototypes + Makefile (RT_PIC_SRCS + explicit `bb_nfa.o` scrip rule). Dead-code-until-`~~`-rewiring — nothing builds a `BB_NFA_*` graph yet — zero regression. Gates: m2 41/42, m3-native 41/42 CRASH 0, m4 42/42, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0. **NEXT:** the 7 consuming/branching templates (pos/subject/slen register model + char/cset/backtrack + capture block) per the RK-NFA-4 DESIGN block in the goal file, then `~~`→`SM_BB_INVOKE` behind `RK_NFA_BB=1` — fresh full-budget session (byte-writing under FACT). [Prior: **RK-NFA-1b** (`6b593da8`) `raku_nfa_to_bb` graph builder; **RK-NFA-1e** (`0d94e255`) closed the mode-2/3/4 regex cluster via the byname path.] |
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
