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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-9-CONCAT `\|\|` string concat LANDED ✅ — corpus same-sweep 82→92 PASS (+10), 0 regressions (passlist-verified), SEGV 0, ABORT 146→133** (Opus 4.8, 2026-05-29). The single largest concrete ABORT cluster (`bb_binop: unsupported op ival=11`, 13 programs) is GONE. `s1\|\|s2` lowers to a tree-shape `BB_BINOP` op=ICN_BINOP_CONCAT (ival=11) — same shape as arith, driven by the op-agnostic `flat_drive_binop_tree`. Fix: (1) CONCAT arm in `bb_binop.cpp` (proven 32-byte arith layout, dead `movabs rdi,0` keeping γ/β/ω patch offsets {23,27,28}, calls `rt_icn_concat`); (2) new `rt_icn_concat` in `rt.c` routing through `icn_binop_apply` (the mode-2 oracle's CONCAT arm) so m2==m3 byte-identical by construction — distinct from the SNOBOL4 `rt_concat`/`CONCAT_fn` (different descriptor convention, cross-family). Newly passing: rung04_string_concat/chain/str_var, rung11_bang_augconcat_augconcat ×3, rung32_strretval ×4. Gates: FACT 0, canonical-5 byte-identical + zero-SM, smoke icon/prolog 5/5, broker 51/11. Deferred (→ IBB-9-4/5): generator-bearing concat (bang/alt/every) now RUNS but emits only the first generated value — needs generator re-pumping through the binop. **NEXT:** the ABORT residue is dominated by `bb_call: unsupported call shape` (Icon builtins — table/MAKELIST/set/list + string fns trim/reverse/repl/map/center/left/right/etc, write with non-int/non-str arg kinds); `every ival=2/3` (IBB-9-4/5); generator-proc dispatch; finish unop family (SIZE/RANDOM); BB_CASE; BB_AUGOP-in-every (rung10). [Prior: **IBB-9-6** user-proc dispatch 69→82 (`8d4c2c2f`); **IBB-9-UNOP** value-producing unary ops (`cc7995c4`); **IBB-9-2** while/until + swap + write(ALT) (`aeb83416`).] |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PLR-K-1 LANDED — atom-builtin MEDIUM_BINARY arms** (2026-05-29, Opus 4.8). `bb_builtin.cpp` only, FACT-clean (0/12). Ported the atom/string builtin family TEXT→BINARY so they run natively under `--run` instead of emitting asm strings AS raw bytes (double-jump-stub class — result var stayed `_`): CAT-D-1/3 atom_length/upcase/downcase(+string_ aliases, 6-scalar→rt_pl_atom_length/_upcase/_downcase); CAT-D-4/5 atom_string/string_to_atom(→rt_pl_atom_string_pair)+copy_term(→rt_pl_copy_term); CAT-D-2/3 atom_concat/string_concat (9 scalars, 6 reg+stack triplet, sub rsp,32); CAT-D-6 atom_chars/codes/string_chars/codes (Path A scalar→rt_pl_atom_chars_codes s1-on-stack; Path B list-literal BB_PL_STRUCT→emit_build_compound_term_bin into r8→rt_pl_atom_chars_codes_term, 8B scratch frame). Each a byte-twin of its TEXT arm but absolute `movabs` for in-process ptrs (atom sval direct, like the write arm). +8 extern-C helper decls. **GATE-2 33→43 (+10); mode-3 native rung 29→39 (+10).** Newly green rung12 ×5 (3-mode AGREE incl path-B `atom_chars(A,[w,o,r,l,d])`→world, `atom_codes`→hello) + ripple rung13/16/24/26. Gates: G1 5/5, G3 m2 104/107 byte-identical, G4 4/4, GATE-SWI 57/57, FACT 0/12, siblings 5/5/13, mode-4 TEXT untouched. **NEXT:** remaining TEXT-only arms — small first (type-test BB_PL_STRUCT compound `rt_pl_type_test_term`; char_type/2; numbervars/3), then format compound / retract / writeq; findall/3 last (own protocol, `nd->ival`=state ptr). [Prior: **PLR-J-5** native multi-clause/disjunction/recursive dispatch (one4all `0b77ba71`); PLR-J ladder J-0..J-5 COMPLETE.] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-ARB-CAT-BACKTRACK LANDED ✅** (Opus 4.8, 2026-05-29). **Native broad 252→255 (+3: 124_pat_regex_keyword_seal, word2, word3); mode-4 194 unchanged; zero regressions.** Corrected the prior session's WRONG "capture-registry" diagnosis — `'xx' ARB 'xx'` fails even with NO capture, so it's an ARB-backtracking bug. `flat_drive_cat` (`emit_bb.c`) multi-kid loop wired every kid's ω to the shared `right_ω → left_β` (= kid[0].β), so a failing trailing element skipped a *middle* generator's β (grow-retry). Fix (2 lines): `kid[i].ω → kid[i-1].β` (retry the immediately-preceding element). 2-kid already correct; only 3+ CATs with a non-last generator (ARB/SPAN/ARBNO) broke. word2 (`POS(0) LEN(4).WHEN TAB(6) ARB.WHO " :" TAB(24) REM.WHAT`) now byte-identical to `.ref` + SPITBOL oracle; capture works through the fix for free. Pure C label-pointer control flow (no byte-producing code). Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), broker 51/11, audit GATE OK, FACT 0, cross-lang 5/5/5/5. **NEXT: mode-2 (`--interp`) parity** — true mode-2 uses `bb_exec_pat` (lowered-graph oracle), where bare `ARB` lowers to a single-shot `BB_PAT_DEFER` that can't grow the embedded generator across the DEFER boundary; two-part fix documented in goal Open work (give DEFER `β=self` in lowering + resume the embedded `sub_bb` via `bb_exec_resume` on β). Then SPAN/ARBNO/FENCE BINARY-arm clusters; the m2-oracle bucket (1011/1013/1017). [Prior: **SBL-1016-EVAL-SLEN** native 251→252; **SBL-1010-ALIAS-ALTENTRY-FIX** 250→251; **SBL-BREAKX-2 + SBL-DATA-FN-SHADOW** 245→250; **SBL-NATIVE-FN-1** +2; **SBL-DEFER-NESTED** +20.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-NFA-1b DONE — NFA→isolated BB_NFA_* graph builder** ✅ (Opus 4.8, 2026-05-29, one4all `6b593da8`). `raku_nfa_to_bb(Raku_nfa*)→BB_graph_t*` state→node walk in `raku_nfa_bb.c` (zero `snobol4_pattern.c` contact): `nfa_kind_to_bb` 1:1 `Nfa_kind`→`BB_NFA_*`, one `BB_t`/state, γ=out1-node β=out2-node(SPLIT) ω=NULL, payload CHAR ival=char / CLASS sval=32-byte cset / CAP ival=group-idx, entry=start node, NULL on Phase-2 kinds. Verified standalone across L1-L15 (graph mirrors the NFA; ports/entry/payload correct). Pure graph construction, NO x86, dead-code-until-RK-NFA-4. Gates: m2 41/42, m3-native 41/42 (CRASH 0), m4 42/42, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1, FACT 0. **NEXT: RK-NFA-4** — NEW `bb_nfa_*.cpp` mode-4 templates (FACT-pure, four-port, opcode names from `Nfa_kind`) + `SM_BB_INVOKE` over the graph on `~~`; then **RK-NFA-5** mode-3 native via emitted templates (mode-3 already 41/42 CRASH 0 via the C matcher; this MOVES regex onto the isolated BB_NFA_* slab). [Prior: **RK-NFA-1e** (`0d94e255`) closed the whole mode-2/mode-4 regex cluster via the SM byname path, m2 35→41 m4 36→42 perfect.] |
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
