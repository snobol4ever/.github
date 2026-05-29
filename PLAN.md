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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-9-1 `every x := 1 to N do B` (static-TO assign) ✅ — corpus same-sweep 213→216 (+3), SEGV 0** (Opus 4.8, 2026-05-29, one4all `e8f66866`). JCON-grounded (read `jcon/tran/irgen.icn`): `ir_a_Every` treats `every x:=GEN do B` as `every (x:=GEN) do B`; since `:=` ∈ `ir_binary`'s funcs set, `ir_binary:438` routes `expr.resume→right.resume` — the assign is transparent to resume, forwarding into the generator. SCRIP transcription: `lower_icn_new_Every_ag` intercepts TT_EVERY whose c[0] is TT_ASSIGN over a static literal TT_TO (BB_TO α==β==NULL) + plain TT_VAR lhs; interposes a BB_ASSIGN store node (ival=1, β=gen for mode-2 null guard) on the ival=1 topology (gen.γ=store, store.γ=body, body.γ=gen, body.ω=gen, gen.ω=bb). `flat_drive_every` ival=1 detects the store and emits gen→store→body→gen_β; store's β routed to a dead `store_ω` stub (NOT gen_β — would self-jump gen_β into an infinite loop, the bug found+fixed this session). TT_TO_BY excluded (keeps operand boxes, needs separate generator wiring). Newly passing: every_do_hello, block_body_nested_block, range_to. Gates: FACT 0, smoke icon/prolog 5/5, broker 42/11, zero-SM holds, no regressions. **A FULL JCON-GROUNDED ROADMAP IS NOW IN THE GOAL FILE (rung IBB-9, steps 9-1..9-8), each citing the exact `ir_a_*` procedure to transcribe.** **NEXT (IBB-9-2):** `while C do B` — cond-result routing fix. `flat_drive_while` (emit_bb.c:1029) is JCON-faithful (body.success/failure → `expr.START`, the every-vs-while difference) BUT the relop cond does not gate: `i:=5; while i<=3 do write(i)` loops in m3, prints nothing-but-99 in m2. **CONFIRMED this session (Opus 4.8):** the while-cond relop is a **TREE-SHAPE BB_BINOP** (α/β NON-NULL, `ival`=relop opcode), NOT AG-pure — detect by opcode, not by α==β==NULL. **REGRESSION TRAP:** a router must fire ONLY for relop conds; an unconditional router regressed 26 read-loop programs (`while line:=read() do…`) — assign/generator conds route truth via their own γ/ω and set no LAST_OK. Inspect `flat_drive_binop_tree` (emit_bb.c:805) first: does a tree-shape relop set LAST_OK+jmp γ (→ reuse bb_if router) or route via γ/ω (→ just wire cond.ω)? Gate against the 216 baseline. Parser note: the `do {block}` "expected ; got while" is just missing stmt separators (newline-as-separator gap), not a BB blocker. Then until (9-3), every ival=2/3 (9-4/5; 9-5 also needs a mode-2 ival=3 x-rebind fix), user-proc dispatch (9-6, `ir_a_Call`), write(BB_CALL) (9-7), DEFERRED computed-goto resume (9-8). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **M3-PL-NOINTERP-1a..1e — native `--run` LIVE, mode-3 0→10 PASS** (Opus 4.8, 2026-05-29, one4all `b408b086`). Implemented the native MEDIUM_BINARY Prolog program entry so `--run` runs instead of aborting, and fixed a family of latent `movabs rax,0; call rax` (call-to-null) stubs in BB template binary arms that segfaulted the moment native execution reached them. **(1a) `sm_bb_switch.cpp` SM_BB_PL_INVOKE BINARY arm** — was the abort stub; now env-push (`mov edi,64; call pl_bb_env_push`) + `walk_bb_flat` + γ/ω tail in raw bytes via the proven SM_BB_INVOKE scratch-buffer recipe (save emit state → scratch buf → walk → bb_emit_end resolves patches → restore → return bytes). Guards multi-predicate programs (callee-block loop DEFERRED) with honest `g_sm_native_unsupported` abort. **(1a fix) `bb_builtin.cpp` write** — `call 0` → load atom into rdi, call `rt_pl_write_atom` (or `rt_pl_write_var`). **(1b) `bb_unify.cpp`** two `call 0` → `rt_pl_node_to_term`/`rt_pl_unify_terms` (scalar unify native); compound (BB_PL_STRUCT) operands honest-abort-guarded (emit_build_compound_term is TEXT-only, port deferred). **(1c) `bb_arith.cpp`** full 7-arg `rt_pl_arith` port; **`bb_pl_cut`**→rt_pl_cut_set, **`bb_pl_var`**→rt_pl_var_push, **`bb_atom`**→rt_pl_atom_push (also fixed rcx→rdi reg bug). **(1d) NEW `is/2` BINARY arm** (binary `L op R` + unary `op(L)`) calling `rt_pl_is` — was TEXT-only, emitting asm-as-bytes in native → var left unbound (`_`). **(1e) NEW comparison BINARY arm** (12 ops `< > =:= == @< ...`) calling `rt_pl_arith_cmp`/`rt_pl_term_cmp` — was TEXT-only → native comparisons always falsely succeeded (`5<3` printed `true`). **Net: mode-3 native crosscheck 0→10 PASS** (hello, arith, rung01, rung04, rung23_arith_ext_{bitwise,max_min,power,sign,truncate}); all 3-mode agreement, no degenerate matches. Gates: GATE-3 m2 104/107, GATE-SWI m2 57/57, siblings icon/raku/snobol4 5/5/13, FACT 0; all emitted bytes inside `*_templates/`. **NEXT (multi-session): the 122 remaining need (a) the DEFERRED callee-block loop in PL_INVOKE (unblocks every multi-predicate program at once — port the TEXT `pl_emit_callee_block_body` sweep to bytes), (b) compound-term builder in raw bytes (port `emit_build_compound_term`, unblocks rung03 + compound unify/functor/univ), (c) BB_PL_CHOICE/backtracking BINARY arms, (d) DCG.** These are now sequenced as the JCON/ICON-derived rung ladder **PLR-J-0..5** (GOAL-PROLOG-BB.md → PL-LOWER-REVAMP; study `doc/JCON-ICON-STUDY-2026-05-29-OPUS.md`); recommended first landing **PLR-J-1** (type-test builtin BINARY arm — smallest, corroborated by rung09). Prior stands: B3 sumto(1e7) O(1) heap (`0019cc7b`), print/1 mode-4 corpus 55/107 (`2fae45ec`). |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-DEFER-NESTED LANDED ✅** (Opus 4.8, 2026-05-29). Nested `*var` (XDSAR→BB_PAT_DEFER) under a combinator now matches under `sm_run_native`. **Native 223→243 (+20) and m2 223→243 (+20)** measured against the live sibling base one4all 30e7c0a1 (a Raku commit had regressed SNOBOL4 m2 from 252→223 via shared bb_exec.c/coerce; this defer fix recovered to 243 — residual 243<252 is the sibling's, flagged for cross-goal review). Zero mode-2/3 regression introduced by this commit (empty FAIL-line diff). smoke 13/13 ×2, rung M2=19, FACT=0, audit GATE OK. Root cause was three gaps, all fixed: (1) `walk_bb_flat` had **no `case BB_PAT_DEFER`** → fell to `default` (define β; jmp ω; jmp ω), never FILLing the template → DEFER became a zero-width no-op (false matches); (2) the BROKERED branch of `exec_stmt` built defer trees with the γ-chain `patnd_to_bb_graph`, but the flat driver traverses **kids** not γ pointers → POS→DEFER collapsed to bare POS; (3) the `bb_pat_defer.cpp` MEDIUM_BINARY arm was empty, and once filled a single `push r10` before `call rt_defer_match` mis-aligned rsp → SIGSEGV when the deref ran a sub-pattern. Fixes: add `walk_bb_flat` DEFER→FILL; XDSAR into `patnd_is_simple_atom`; **surgical** `defer_combinator` gate routes only defer-bearing combinator roots through `patnd_to_bb_tree` (legacy-cast trees untouched); BINARY arm with `and rsp,-16` 16-byte alignment around the call. Newly native: 056/070-073/108/110-112/115/128/132-138/144/147 + fence/arbno-over-defer (068/117/143/150 no longer SIGSEGV). **Mode-4 deferred per Lon (not gated this session);** `bb_pat_defer.cpp` TEXT arm still needs the same alignment fix when mode-4 resumes. Handoff `HANDOFF-2026-05-29-OPUS48-SBL-DEFER-NESTED-LANDED.md` (landed) / `HANDOFF-2026-05-29-OPUS48-SBL-SPAN-VERIFIED-DEFER-NESTED-XDSAR.md` (isolation). [Prior: **SBL-TAB-RTAB-FIX ✅** (`0ae0e7c2`) native +3; **SBL-POS-RPOS-FLAG-FIX ✅** (`dbdec9bb`) native +25; plus SBL-BOMB/SPAN-ARB-ESCAPE, POS-PATCH-OFFSET, ARBNO child-gate, M3-NATIVE-4 flat-wire, EP-BINARY, bb_capture.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-BB-4c (mode-4 junctions) + RK-BB-4d (precedence + nested mixed-flavor) COMPLETE** ✅ (Opus 4.8, 2026-05-29, one4all `1652aeb9`). **GATE-RK mode-2 26→28/35, GATE-RK4 mode-4 26→29/35.** THREE commits. **(RK-BB-4c `216f22cd`)** junction collapse added to shared `rt_acomp`/`rt_lcomp` (`rt.c`), mirroring the mode-2 `SM_ACOMP`/`SM_LCOMP` interpreter cases — FACT-clean (the x86 templates already emit `mov edi,<op>; call rt_acomp`/`rt_lcomp`, so the work lives in those runtime helpers, no template byte change). Operand `rk_junction_is()`→`rk_junction_collapse(scalar,jct,op,numeric)` (1 acomp/0 lcomp); scalar+`LAST_OK=1` on hit else FAIL. `rk_junctions` mode-4 GREEN. Mode-3 junctions correct too (same helpers) but DORMANT — Raku `--run` emits no output for any program (pre-existing MODE3-DISPATCH-GAP), lights up free when that closes. **(RK-BB-4d precedence `0a5352e3`)** new `jct_expr` grammar tier in `raku.y` makes infix `|`/`&` bind TIGHTER than comparison (real Raku); `$x==1|2|5`→`$x==any(1,2,5)`. Comparison productions take `jct_expr` operands; `%left '|' '&'` moved above comparison; `%type <node> jct_expr`; parser+lexer regenerated, NET-ZERO new conflicts (baseline already 30 s/r). **(RK-BB-4d nesting `1652aeb9`)** the predicted SOH-leak pinned + fixed: `rk_junction_collapse` member scan stopped at the first SOH, truncating a nested junction (which CONTAINS SOHs) to zero members and leaking its members outward — broke ONLY a flavor wrapping a different-flavor multi-member inner (`50&(50|60)` missed; `10|(50&60)` hit). Fix: self-delimiting EOT(`\x04`) terminator — builder appends `\x04`; scanner stops scalars at SOH-or-EOT and depth-skips nested `\x03…\x04` spans, recursing on the opaque span (arbitrary depth). Probes `rk_junction_prec` + `rk_junction_nest` added (both modes green). Zero regression: smoke raku/icon/prolog/snobol4/snocone 5/5/5/13/5; crosschecks stash/rebuild baseline-identical (SNOBOL4 5/1, Icon 3/1, Prolog 0/132, Raku 36/1); FACT 0; build clean. Handoff `HANDOFF-2026-05-29-OPUS48-RAKU-BB-4C-4D-JUNCTIONS-MODE4-NEST.md`. **NEXT: RK-BB-5** — `reverse`/`tail`/`from-loop` Seq consumers, `zip`/`cross` multi-Seq drivers; or RK-BB-4c mode-3 once MODE3-DISPATCH-GAP closes; or deferred regex cluster (GOAL-RAKU-PAT-BB). Sliver: `^`(one) infix not lexed (only `one(...)` constructor). [Prior: **RK-BB-4 mode-2 junctions** (`30e7c0a1`) RK-M2-GATHER + RK-M2-ACOMP + 4a constructors + 4b infix; **M3-RK-NOINTERP-1d** (`a894af4a`); **1c** (`8d3a8cdf`); **1b** (`48ca4e21`); **1a** (`55d03444`).] |
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
