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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1b ✅. **LFJ-1c** ✅ (`5cd9003d`: empty `lower_icn_new.{c,h}` created in `src/lower/`; Makefile sources list + per-file compile rule wired; `lower_icn_new.o` builds (no symbols) and links cleanly). Substrate complete — table substrate + transcription target file pair both in place. Next: **LFJ-2** — transcribe `ir_a_NoOp` from `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn` into `lower_icn_new_NoOp`; flip the matching slot in `lower_kind_table` (likely TT_NUL or whichever AST kind Icon's NoOp maps to per LOWER-IRGEN-MAPPING.md). Gates: smoke 5/5, broker 24, rungs 198, smoke_prolog 5/5. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..5 ✅ (Opus 4.7, one4all `bb8bb529`). CAT-D-2 atom_concat/3 (`ecb3b229`, new rt_pl_atom_concat 9-arg helper, 3 stack args under 32B aligned frame). CAT-D-3 string_length/upper/lower/concat aliased onto CAT-D-1/D-2 helpers (ZERO new rt). CAT-D-4 atom_string/2 + string_to_atom/2 bidirectional (`52a78efb`, new rt_pl_atom_string_pair). CAT-D-5 copy_term/2 (`bb8bb529`, new rt_pl_copy_term). GATE-2 --mode run 5/107 → 11/107 (+6). GATE-1 5/5, GATE-3 88/19, GATE-4 4/4 all held. FACT RULE clean. NEXT: CAT-A-3 (BB_PL_CALL + BB_CHOICE β-resume; needs Lon directive on design), CAT-D-6 (atom_chars/atom_codes), or fix pre-existing mode-4 write(compound) + ITE-with-==/2 gaps (would lift many rungs). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`: rk_gather PASSES mode-4 — 9/30). RK-BB-3 substrate audit done (2026-05-27, Opus 4.7, one4all `d4cbefaf`) — 6 gaps verified, scope decomposed into 3a/3b/3c/3d; gating on Lon Q6/Q7/Q8 (polymorphic BB_ITERATE, FIELD_GET_fn in template, eager vs lazy `my @x = map`). New probe test/raku/rk_for_array_simple.raku added (mode-4 9/31, mode-2 8/31). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-DCG-DEFER-M4 PARTIAL ✅ (`954236f5`): `patnd_to_bb_graph` translator + bb_exec.c BB_PAT_DEFER DT_P wiring; rung suite M2 15→16. NEXT: stmt_exec.c DT_P wiring (parallel scan loop on bb_exec_pat bypassing bb_broker) + SBL-ARBNO-COUNTER-RESET (kind-aware bb_reset preserving aux-ptr counters for ARBNO/PROC_GEN/PL_SEQ/CHOICE) together unlock the +15 broad-corpus uplift (070-074, 105-117). |
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
