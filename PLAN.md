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
| **ICON-BB** | `GOAL-ICON-BB.md` | **22 programs PASS mode 2, ZERO SM each** (Sonnet 4.6, 2026-05-28, one4all `936b8182`). Icon bypasses SM entirely: driver detects `is_icon && SCRIP_ICN_BB`, calls `bb_exec_once` directly. `--dump-sm` prints `count=0` for every Icon program. Ticked: IBB-1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 29, 30, 32 — all mode 2, all zero SM, all no code change beyond driver bypass + lower suppression. Includes full `test_icon.c` expression `every write(5 > ((1 to 2) * (3 to 4)))` → `3/4`, recursion `f(5)=15`, string scanning `"hello" ? { tab(2); tab(0) }`, tables, csets, find/upto. Known gap: IBB-23 suspend at top-level (pre-existing in legacy too, not a regression). Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 36, FACT 0. **NEXT: IBB-5** — mode-4 native, real x86 BB templates per `ARCH-x86.md`. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **FACT cleanup Steps 2+3 ✅** (Sonnet 4.6, 2026-05-28, one4all `88bacd2a`): `bb_emit_asm_result_pairs()` helper added to `emit_str.cpp`/`emit_str.h` — reconstructs (site, label, is_def) metadata from `xa_bb_emit_pair_*` arrays so templates need no `bin.*` access. All six combinator templates (`bb_pat_fence/alt/cat`, `bb_pl_seq/ite`, `bb_succeed`) stripped to pure byte production; wrappers swapped to `bb_emit_asm_result_pairs`. `flat_drive_fence` 0-children path updated (Option B) to always populate pairs — dead special case in template removed. FACT grep: **0 violations**. Gates: G1=5/5, G2=132/0, G3=**100/107** (+4: plus/3 ×3, ** integer power), G4=4/4. **NEXT:** WAM-CP-13, WAM-CP-6 (LCO trampoline refactor — see HANDOFF-2026-05-28-SONNET-PROLOG-BB-WAM-CP-6-ANALYSIS.md), WAM-CP-9 Steps B–D, or rung27 aggregate/nb_setval. |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. RK-GIVEN-MODE4 ✅. RK-HASH ✅. **RK-NAMED-CALL ✅** (Opus 4.7, 2026-05-28, one4all `c944db09`): template-pure restoration of Raku user-sub dispatch after LANG-IGNORANT-SM-TEMPLATES (`08e05f68`) ripped `rk_sub_lookup` from sm_calls.cpp/sm_jumps.cpp. New language-ignorant `SM_NAMED_CALL` opcode (a[0].s=name, a[1].i=nparams) emits `mov edi,nparams; call rt_frame_enter@PLT; call .Lsub_<name>; call rt_frame_leave@PLT`. `sm_label_str` MEDIUM_TEXT emits `.Lsub_<name>:` symbol when `a[0].s` non-empty (named labels emit symbols — opcode semantics, not language sniffing). `lower_fnc` for LANG_RAKU emits SM_NAMED_CALL when callee matches TT_SUB_DECL in proc_table. Templates contain ZERO `g_lang` refs. **GATE-RK4 17→22** (+rk_subs, +rk_combinator, +rk_interp, +rk_given, +rk_given18). GATE-RK 20 HOLD. Smokes raku/prolog/snobol4 HOLD. Icon (restored by MAIN-BOOT `80d0d5ee` in same session): smoke 5/5, broker 35, rungs 161 (rebased from `c944db09` — see ICON row). FACT RULE 0. GOAL file pruned 356→146 lines. Remaining 11 FAILs: regex/NFA (6, deferred), I/O (2), exceptions (1), junctions (1, blocked Q9-Q12), class (1). NEXT: I/O or exceptions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **Label arena landed ✅** (Opus 4.7, 2026-05-28, one4all `744ae342`): prerequisite for M3-NATIVE-4 combinator flat-wire retry. New `emit_label_alloc(fmt, ...)` in `emit_core.{h,c}` provides session-stable `bb_label_t *` (heap-backed, pool reset by `bb_emit_begin`); migrated all six flat drivers in `emit_bb.c` (`flat_drive_cat`/`_alt`/`_fence`/`_pl_seq`/`_pl_choice`/`_pl_alt`/`_pl_ite`) off stack-local `bb_label_t`/`alloca` arrays. Refined the prior session's dangling-label diagnosis: trace shows current AST/SM graphs survive only by leaf-self-definition of β (e.g. `bb_lit.cpp` site 109 has `is_def=true` for `lbl_β_p`); bug would surface under deeper combinator nesting (exactly what `patnd_to_bb_tree` would do). Plus `alloca` reuse across nested calls would silently corrupt label names. Arena closes both modes. Pure infrastructure — zero x86 bytes, FACT n/a. All gates byte-identical: G1=13/13 default+native, G2=36, G3=175/280, G4=237/280, native=165/280, rungs M2=19/M4=15, sister smokes prolog/raku/icon/rebus all green, FACT=0. **NEXT:** retry `patnd_to_bb_tree` (emit_sm.c-shaped graphs with `pat_set_children`) + extend `patnd_needs_xlate` to combinator roots; validate on 050_pat_alt_two/055_pat_concat_seq native ("dog"/"ab cd ef"). **Blocker:** audit_m3_native now FAIL (NOT my commit — surfaced after rebase against concurrent Prolog FACT-cleanup `88bacd2a` that stripped EP-walk byte production from six combinator templates `bb_pat_alt`/`bb_pat_cat`/`bb_pat_fence`/`bb_pl_seq`/`bb_pl_ite`/`bb_succeed` → FAKE-JMP STUB classification). Restore those six template arms via the FACT-correct inline-EP-walk pattern (recorded in 2026-05-28 SBL-EP-BINARY session log entry) BEFORE the broad-corpus combinator-flat-wire retry. Prior history on `5427e12e`: **SBL-EP-BINARY ✅** (`0e077eb5`) inline EP-walk in each template, **all BOMs eliminated ✅** (`4ce8c385`) deque-int scratch pattern. Beyond combinator flat-wire: SPAN/ARBNO/BREAKX/FENCE/POS/RPOS/TAB/RTAB cluster knockdown. |
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
