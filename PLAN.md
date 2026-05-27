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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1b ✅. LFJ-1c ✅ (`5cd9003d`). **LFJ-2..LFJ-7 ✅** (`0b3b331d`, Opus 4.7, 2026-05-27). **LFJ-8 ✅** (`3d8aae8c`, Opus 4.7, 2026-05-27): `ir_a_Every` → `lower_icn_new_Every`. TT_EVERY flipped. 1:1 transcription of legacy_EVERY (which already encodes JCON's flat-wire gen topology). Preserves AG-pure 8.1 literal-bound gating + 8.2 TT_TO/TT_TO_BY dynamic-bound routing. Gates: 5/5 · 198 · 25 · 5/5. FACT RULE clean. Next: **LFJ-9** — transcribe `ir_a_Compound` + `ir_a_ProcBody`. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..8 ✅ (Opus 4.7, one4all `710ee0b0`). CAT-D-7 write(compound) mode-4 via 100% template emission (`d2ce06fc`, 3 new rt_pl_write_int/float/cstr one-liners + recursive emit_write_term in bb_builtin.cpp). CAT-D-8 BB_PL_ITE wrapper for mode-4 if-then-else (`710ee0b0`, new bb_pl_ite.cpp template + flat_drive_pl_ite driver + state struct + mode-2 exec case + lower wrapper). GATE-1 5/5, GATE-3 88→89/107 (+1), GATE-4 4/4 held, GATE-2 --mode run 11→15/107 (+4), mode-4 rung suite 11→15/107 (+4). FACT RULE clean. NEXT: fix ==/2 mode-4 (always-succeeds bug, independent of ITE, would unlock more rungs), CAT-A-3 (BB_PL_CALL + BB_CHOICE β-resume; needs Lon directive), CAT-D-6 (atom_chars/atom_codes — list cons-cell construction). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`). RK-BB-3.0+3d infra ✅ (`fcac4ab3`). RK-BB-3.0a ✅ (`ba481112`). RK-BB-3.0b ✅ (2026-05-27, Opus 4.7, one4all `7a60d30e`) — GAP 2 mutators: lower.c lower_fnc (push/pop) + TT_ARR_SET prepend SM_PUSH_LIT_S vname; sm_interp.c + rt.c mutating dispatch branches peel args[0].s as vname → raku_try_mutating_builtin_by_name. Cumulative 3.0a+3.0b: GATE-RK 8→10 (+rk_str22, +rk_arrays), GATE-RK4 9→11 (+rk_str22, +rk_arrays), all smokes hold, broker hold, FACT RULE clean. NEXT: RK-BB-3a (BB_ITERATE polymorphism for `for @arr -> $v` — runtime substrate now complete; needs bb_iterate.cpp + bb_exec.c BB_ITERATE polymorphic on \x01-string DT_S vs Icon-char DT_S). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-DCG-DEFER-M4 ✅ + widened ✅ (Opus 4.7, this session, one4all `26913b08`): `stmt_exec.c` DT_P wiring via `patnd_needs_xlate` gate — translator path for ARBNO-bearing trees and single-atom PATND roots. + SBL-ARBNO-COUNTER-RESET ✅. Gates: M2 rung 18 (was 16), mode-2 broad 218/280 (was 210, +8), mode-4 broad 175/280 (was 174, +1 net via Qize_driver + W02_seq_basic + W02_seq_nested). NEXT: SBL-G-2 (re-freeze GATE-PK) or extend translator gate to XCAT/XOR composites (carefully). |
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
