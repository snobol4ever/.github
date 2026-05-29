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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-8b STRING RELOPS IN IF-COND ✅ (partial) — corpus same-sweep 22→28 (+6), SEGV 0** (Opus 4.8, 2026-05-29, one4all `0e926c16`). Three pieces: (1) `bb_binop.cpp` AG-pure relop/strrel apply arm — `rt_acomp`(numeric)/`rt_lcomp`(string) + unconditional `jmp γ`; both ports of an AG-pure relop reach the BB_IF router, per the mode-2 oracle. (2) NEW `bb_if.cpp` router — `rt_pop_void; rt_last_ok; test eax,eax; jz ω(else); jmp γ(then)`; registered in emit_core dispatch + bb_templates.h + Makefile. (3) `flat_drive_seq` rewritten from γ-only linear walker into a **node-keyed CFG emitter** (BFS follows γ always, ω ONLY for BB_IF so operand children aren't double-emitted; non-IF nodes keep outer lbl_ω as baseline — resolving ω generally SEGV'd by mis-wiring operands that tree-shape drivers walk inline; one stable arena label per node, emitted once). AG-pure BB_BINOP routes to FILL; added `case BB_IF`. BB_SEQ is Icon-exclusive (only lower_icn.c builds it) → zero cross-family impact. **The original IBB-8 `flat_drive_if`/`pBB->cond` plan was unworkable (BB_IF has no back-pointer to the cond chain; PEERS RULE forbids adding one) and was superseded by the CFG-seq approach.** Newly passing: rung12_strrelop_size_{slt,sge,sne}, rung37_strrelop_hello, rung07_control_seq, canonical if_expr crosscheck. Gates: FACT 0, smoke icon 5/5, prolog 5/5, broker 39/14, zero-SM holds, no regressions. Handoff `HANDOFF-2026-05-29-OPUS48-ICON-BB-IBB8B-STRING-RELOPS.md`. **NEXT (IBB-8c):** numeric/real relops blocked on **BB_LIT_F vstack-push** — `bb_lit_scalar.cpp` BB_LIT_F path is a pass-through stub that never pushes the real (mirror the BB_LIT_I arm with a DT_R DESCR_t push); unblocks rung18_real_relop_*. Then block-body if (rung35_block_body_if_*) nested-block flattening, every-E-do-body (~4), write(BB_CALL), user-proc dispatch. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **M3-PL-NOINTERP-1a..1e — native `--run` LIVE, mode-3 0→10 PASS** (Opus 4.8, 2026-05-29, one4all `b408b086`). Implemented the native MEDIUM_BINARY Prolog program entry so `--run` runs instead of aborting, and fixed a family of latent `movabs rax,0; call rax` (call-to-null) stubs in BB template binary arms that segfaulted the moment native execution reached them. **(1a) `sm_bb_switch.cpp` SM_BB_PL_INVOKE BINARY arm** — was the abort stub; now env-push (`mov edi,64; call pl_bb_env_push`) + `walk_bb_flat` + γ/ω tail in raw bytes via the proven SM_BB_INVOKE scratch-buffer recipe (save emit state → scratch buf → walk → bb_emit_end resolves patches → restore → return bytes). Guards multi-predicate programs (callee-block loop DEFERRED) with honest `g_sm_native_unsupported` abort. **(1a fix) `bb_builtin.cpp` write** — `call 0` → load atom into rdi, call `rt_pl_write_atom` (or `rt_pl_write_var`). **(1b) `bb_unify.cpp`** two `call 0` → `rt_pl_node_to_term`/`rt_pl_unify_terms` (scalar unify native); compound (BB_PL_STRUCT) operands honest-abort-guarded (emit_build_compound_term is TEXT-only, port deferred). **(1c) `bb_arith.cpp`** full 7-arg `rt_pl_arith` port; **`bb_pl_cut`**→rt_pl_cut_set, **`bb_pl_var`**→rt_pl_var_push, **`bb_atom`**→rt_pl_atom_push (also fixed rcx→rdi reg bug). **(1d) NEW `is/2` BINARY arm** (binary `L op R` + unary `op(L)`) calling `rt_pl_is` — was TEXT-only, emitting asm-as-bytes in native → var left unbound (`_`). **(1e) NEW comparison BINARY arm** (12 ops `< > =:= == @< ...`) calling `rt_pl_arith_cmp`/`rt_pl_term_cmp` — was TEXT-only → native comparisons always falsely succeeded (`5<3` printed `true`). **Net: mode-3 native crosscheck 0→10 PASS** (hello, arith, rung01, rung04, rung23_arith_ext_{bitwise,max_min,power,sign,truncate}); all 3-mode agreement, no degenerate matches. Gates: GATE-3 m2 104/107, GATE-SWI m2 57/57, siblings icon/raku/snobol4 5/5/13, FACT 0; all emitted bytes inside `*_templates/`. **NEXT (multi-session): the 122 remaining need (a) the DEFERRED callee-block loop in PL_INVOKE (unblocks every multi-predicate program at once — port the TEXT `pl_emit_callee_block_body` sweep to bytes), (b) compound-term builder in raw bytes (port `emit_build_compound_term`, unblocks rung03 + compound unify/functor/univ), (c) BB_PL_CHOICE/backtracking BINARY arms, (d) DCG.** Prior stands: B3 sumto(1e7) O(1) heap (`0019cc7b`), print/1 mode-4 corpus 55/107 (`2fae45ec`). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-DEFER-NESTED LANDED ✅** (Opus 4.8, 2026-05-29). Nested `*var` (XDSAR→BB_PAT_DEFER) under a combinator now matches under `sm_run_native`. **Native 223→243 (+20) and m2 223→243 (+20)** measured against the live sibling base one4all 30e7c0a1 (a Raku commit had regressed SNOBOL4 m2 from 252→223 via shared bb_exec.c/coerce; this defer fix recovered to 243 — residual 243<252 is the sibling's, flagged for cross-goal review). Zero mode-2/3 regression introduced by this commit (empty FAIL-line diff). smoke 13/13 ×2, rung M2=19, FACT=0, audit GATE OK. Root cause was three gaps, all fixed: (1) `walk_bb_flat` had **no `case BB_PAT_DEFER`** → fell to `default` (define β; jmp ω; jmp ω), never FILLing the template → DEFER became a zero-width no-op (false matches); (2) the BROKERED branch of `exec_stmt` built defer trees with the γ-chain `patnd_to_bb_graph`, but the flat driver traverses **kids** not γ pointers → POS→DEFER collapsed to bare POS; (3) the `bb_pat_defer.cpp` MEDIUM_BINARY arm was empty, and once filled a single `push r10` before `call rt_defer_match` mis-aligned rsp → SIGSEGV when the deref ran a sub-pattern. Fixes: add `walk_bb_flat` DEFER→FILL; XDSAR into `patnd_is_simple_atom`; **surgical** `defer_combinator` gate routes only defer-bearing combinator roots through `patnd_to_bb_tree` (legacy-cast trees untouched); BINARY arm with `and rsp,-16` 16-byte alignment around the call. Newly native: 056/070-073/108/110-112/115/128/132-138/144/147 + fence/arbno-over-defer (068/117/143/150 no longer SIGSEGV). **Mode-4 deferred per Lon (not gated this session);** `bb_pat_defer.cpp` TEXT arm still needs the same alignment fix when mode-4 resumes. Handoff `HANDOFF-2026-05-29-OPUS48-SBL-DEFER-NESTED-LANDED.md` (landed) / `HANDOFF-2026-05-29-OPUS48-SBL-SPAN-VERIFIED-DEFER-NESTED-XDSAR.md` (isolation). [Prior: **SBL-TAB-RTAB-FIX ✅** (`0ae0e7c2`) native +3; **SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`) native +25; plus SBL-BOMB/SPAN-ARB-ESCAPE, POS-PATCH-OFFSET, ARBNO child-gate, M3-NATIVE-4 flat-wire, EP-BINARY, bb_capture.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-BB-4 MODE-2 JUNCTIONS COMPLETE + mode-2 gather + ACOMP** ✅ (Opus 4.8, 2026-05-29, one4all `30e7c0a1`). **GATE-RK mode-2 23→26/33** (+rk_gather, +rk_given18, +rk_junctions). FOUR pieces. **(1) RK-M2-GATHER** — `bb_exec.c` `BB_SEQ` gains a Raku-gather multi-yield driver (gated `lang==RKU && α==BB_SUSPEND`): yields one `take` per (re)entry using `bb->counter` as the resume cursor (reset by `bb_exec_once`, preserved by `bb_exec_resume`); mirrors mode-3 `bb_seq_gather_binary`. rk_gather mode-2 FAIL→PASS. **(2) RK-M2-ACOMP** — `sm_interp.c` `SM_ACOMP` coerces `DT_S` operands via `to_real` (mirrors `SM_ADD`); previously non-`DT_I`/`DT_R` operands compared as 0, so `given` on a `for`-loop var (array element = string) missed every `when` arm. rk_given18 FAIL→PASS. Shared path; zero regression (before/after stash on SNOBOL4 crosscheck, broad broker 6/6). **(3) RK-BB-4a** (constructors) — `lower.c` intercepts Raku `any/all/one/none` → `__rk_jct_*` builders (per-language lowering, dup-name skip); `raku_builtins_byname.c` packs a tagged-string junction VALUE (`ETX+flavor+SOH` members, Q12) + `rk_junction_collapse` (recursive, per-flavor any=OR/all=AND/one=exactly-one/none=NONE); `sm_interp.c` `SM_ACOMP`/`SM_LCOMP` junction guard (`s[0]==0x03`, inert for normal values). **(4) RK-BB-4b** (infix) — `raku.l` single-char `\|`/`&`; `raku.y` `mk_junction` builds `any()`/`all()` `TT_FNC` (same lowering as 4a), same-flavor chains flatten at parse time (sidesteps nested-`\x01` leak); parser/lexer regenerated, zero grammar conflicts. **Full `rk_junctions` probe PASS mode-2.** Q9-Q12 answered (Q9 reuse-unless-divergent, Q10 BB_ALT, Q11 substrate-first, Q12 tagged-string); BB_ALT substrate proven (mode-2 complete engine + mode-4 binary slab real, not stub). Gates: GATE-RK m2 26/33, GATE-RK4 m4 26/33 HOLD, GATE-RK3 26/33 HOLD (no native code touched), smoke raku/prolog/icon/snobol4 5/5/5/13, FACT 0, build clean. Handoff `HANDOFF-2026-05-29-OPUS48-RAKU-BB-JUNCTIONS-MODE2.md`. **NEXT: RK-BB-4c** — mode-3/4 junctions (emit `rt_junction_collapse` @PLT/movabs at `SM_ACOMP`/`SM_LCOMP` template sites to flip `rk_junctions` mode-4 green; or Q11 substrate-first via `BB_ALT` binary slab). Then RK-BB-4d edges (mixed-flavor nesting rep, precedence, var round-trip) or deferred regex cluster (GOAL-RAKU-PAT-BB). `rk_stdio39` mode-2 FAIL is a test-fidelity issue (`$*STDERR→fd2` correct; expected encodes fd1) — Lon's call. [Prior: **M3-RK-NOINTERP-1d ✅** (`a894af4a`) rk_gather mode-3 native CRASH→PASS; **1c** (`8d3a8cdf`); **1b** (`48ca4e21`); **1a** (`55d03444`); **3** (`c3476078`).] |
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
