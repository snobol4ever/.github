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
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ-0..LFJ-1b ✅. LFJ-1c ✅ (`5cd9003d`). **LFJ-2..LFJ-7 ✅** (`0b3b331d`, Opus 4.7, 2026-05-27). **LFJ-8 ✅** (`3d8aae8c`). **LFJ-9 ✅** (`80b9130e`): `ir_a_Compound`/`ir_a_ProcBody` documented non-emission. **LFJ-10 ✅** (`5c5bc669`): TT_FNC→Call, TT_FIELD→Field, TT_SECTION/PLUS/MINUS→Sectionop. **LFJ-11 ✅** (`8b6e513b`, Opus 4.7, 2026-05-27): TT_ALTERNATE→Alt, TT_SEQ→Conjunction, TT_NOT→Not. **LFJ-12 ✅** (`9b8fec0c`, Opus 4.7, 2026-05-27): TT_WHILE→While, TT_UNTIL→Until, TT_REPEAT→Repeat, TT_LIMIT→Limitation. Gates: 5/5 · 198 · 5/5 · 26/51. FACT RULE clean. **11 of 15 LFJ rungs complete** (73%). Next: **LFJ-13** — transcribe `ir_a_Scan`, `ir_a_Case`, `ir_a_Return`, `ir_a_Suspend`, `ir_a_Break`, `ir_a_Next`. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | CAT-D-1..9b ✅. CAT-D-6 ✅ (`b60ebfa4`, Sonnet 4.7, 2026-05-27): atom_chars/atom_codes/string_chars/string_codes mode-4 via two-path template (scalar a1 → rt_pl_atom_chars_codes; literal cons-cell a1 → rt_pl_atom_chars_codes_term + emit_build_compound_term). Plus rt_pl_write_var TERM_COMPOUND → pl_write fix. Mode-3 rung 19→21 (+2: rung12_atom_chars, rung12_atom_codes). Mode-4 rung 19→21 (+2 same). CAT-D-10 ✅ (`060aad55`, Sonnet 4.7, 2026-05-27): 11 type-test builtins (var/nonvar/atom/atomic/number/integer/float/compound/callable/is_list/ground) — fixed silent always-succeeds bug. Mode-2/3/4 byte-identical across full scalar + compound battery. No rung-count delta (type tests live inside ITEs whose branches still depend on unimplemented builtins). Gates: GATE-1 5/5, GATE-2 54/132, mode-2 89/107, mode-3 21/107, mode-4 minimal 4/4, mode-4 rung 21/107. FACT RULE 0. NEXT: CAT-A-3 (BB_PL_CALL + BB_CHOICE β-resume — needs Lon directive on design), CAT-D-11 (sort/2 + msort/2 — RT helper does term-array build + insertion-sort via pl_term_compare + dedup + cons-list build + unify; ZERO port logic in RT, template owns γ/ω as in CAT-D-1..10), CAT-D-12 (functor/3 + arg/3 + =../2 — unblocks rung09). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1 ✅. RK-BB-2 ✅ (`d08237e0`). RK-BB-3.0+3d ✅ (`fcac4ab3`). RK-BB-3.0a ✅ (`ba481112`). RK-BB-3.0b ✅ (`7a60d30e`). **RK-BB-3a partial ✅** (`706e2828`, 2026-05-27, Opus 4.7) — lower.c `lower_raku_iterate_arr` + `lower_every` pattern-match on `TT_EVERY(TT_ITERATE(TT_VAR,sval),body)` builds 1-node BB graph (BB_ITERATE, sval=arr_vname, cfg->lang=BB_LANG_RKU). bb_exec.c BB_ITERATE sval-polymorphic: Raku path NV_GET_fn → \x01-segment scan → yield substring → γ; counter-byte-offset advances past separator; re-fetch each call (source ≠ yield slot). bb_iterate.cpp Raku MEDIUM_TEXT arm authored — 100% template emission: .data slots (name + counter quad), inline x86 (α resets counter, β falls through, load via NV_GET_fn@PLT, inline \x01 scan, yield via rt_push_str@PLT, jmp γ). **Mode-2 + Mode-3 GREEN (+2 each: rk_for_array_simple, rk_for_array); mode-4 emits cleanly but loop bails on slen=0 — NV_GET_fn returns NULVCL even after pushes populate. Isolated asm test confirms instruction sequence correct.** GATE-RK mode-2: 10→12, mode-3: 10→12 (same code path), GATE-RK4 11/31 HOLD, smokes hold, broker 198 HOLD, FACT RULE 0. NEXT: RK-BB-3a-mode4-debug (slen=0 root cause — likely section-switch fall-through or label scope; objdump triage). Then RK-BB-3b/c (lazy map/grep). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | SBL-MODE3-REACTIVATE ✅ (Opus 4.7, continued 12, one4all `380b4683`). **SBL-MODE-PURITY-1 ✅** (Opus 4.7, continued 13, one4all `24df0702`): removed L327 LIVE→brokered fallback in stmt_exec.c exec_stmt. Architectural rule (Lon): modes do NOT silently fall back between themselves — `--run` (LIVE) builds patterns via `bb_build_flat`; `--interp` (BROKERED) via `bb_build_brokered`. Cross-mode fallback corrupts the test signal. Probe showed zero L327 hits under current corpus, so the fix is mechanically safe; all five gates hold (13/13, 26, 175/280, 218/280, M2=18 M4=15). NEXT: SBL-MODE-PURITY-2 (mode-gate L309/L311/L367/L377 literal-coercion paths — currently all four call `bb_build_brokered` unconditionally regardless of g_bb_mode). Hold SBL-ANY-2 (BINARY arm fill) until all SBL-MODE-PURITY sub-steps land. |
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
