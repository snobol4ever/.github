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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-9-2 while/until (relop conds) + swap `:=:` + write(ALT) any-type fix ✅ — corpus same-sweep 56→62 PASS (+6), 0 regressions, SEGV 0** (Opus 4.8, 2026-05-29, one4all `aeb83416`; baseline RE-MEASURED on live `c7529bad` = 56 PASS, not the doc's 216 which used an older corpus snapshot). Landed: (1) `flat_drive_while` (emit_bb.c) — JCON `ir_a_While` topology, gate reuses `bb_if` LAST_OK bytes via `emit_core` BB_WHILE/BB_UNTIL→`bb_if`, loop exits via `lbl_γ` (the γ-successor; exiting via ω drops the next stmt — bug caught by build+run), gate fires only for relop conds with var/literal/pure-arith operands (`icn_while_operand_simple`), non-relop/generator conds stay on the degenerate path; assignment-as-rvalue `(i:=i+1)>N` fixed generally in `flat_drive_binop_tree` (re-push stored value via `bb_var`). (2) new template `bb_swap.cpp` + `flat_drive_swap` (x:=:y, two BB_VAR). (3) `bb_call.cpp` `arg_is_any` += BB_ALT (string/real alts were printed as pointer garbage by int-write). Gains: rung35_while, rung09_until_gen, rung09_repeat_break, rung15_swap_basic, rung15_swap_str, rung13_alt_every_write. Gates: FACT 0, smoke icon/prolog 5/5, broker 44/11, zero-SM holds. Prior: **IBB-9-1 `every x := 1 to N do B` (static-TO assign)** (one4all `e8f66866`). JCON-grounded (read `jcon/tran/irgen.icn`): `ir_a_Every` treats `every x:=GEN do B` as `every (x:=GEN) do B`; since `:=` ∈ `ir_binary`'s funcs set, `ir_binary:438` routes `expr.resume→right.resume` — the assign is transparent to resume, forwarding into the generator. SCRIP transcription: `lower_icn_new_Every_ag` intercepts TT_EVERY whose c[0] is TT_ASSIGN over a static literal TT_TO (BB_TO α==β==NULL) + plain TT_VAR lhs; interposes a BB_ASSIGN store node (ival=1, β=gen for mode-2 null guard) on the ival=1 topology (gen.γ=store, store.γ=body, body.γ=gen, body.ω=gen, gen.ω=bb). `flat_drive_every` ival=1 detects the store and emits gen→store→body→gen_β; store's β routed to a dead `store_ω` stub (NOT gen_β — would self-jump gen_β into an infinite loop, the bug found+fixed this session). TT_TO_BY excluded (keeps operand boxes, needs separate generator wiring). Newly passing: every_do_hello, block_body_nested_block, range_to. Gates: FACT 0, smoke icon/prolog 5/5, broker 42/11, zero-SM holds, no regressions. **A FULL JCON-GROUNDED ROADMAP IS NOW IN THE GOAL FILE (rung IBB-9, steps 9-1..9-8), each citing the exact `ir_a_*` procedure to transcribe.** **NEXT:** the cheap "mode-2 works, just wire mode-3" wins are now exhausted; the remaining tail is real rungs. Biggest lever by far: **user-proc dispatch (IBB-9-6, ~158 of 169 aborts are `bb_call: unsupported call shape`)** — mode-2 is a working oracle; mode-3 needs native proc emission + a calling convention + frames + `BB_RETURN`. Then the **scanning subsystem (~11 FAILs: `s ? expr` with tab/move/match/any/many/upto)** — mode-3 scan templates are TODO-stubbed. Smaller: `||` lconcat (rung13 nested), reals (rung18), `case` (BB_CASE flat driver; rung33), unary null-tests (need relop-as-rvalue), loop `break`/`next` (unwired in mode-3), and the mode-2 `every`-ival=3 rebind bug (rung35_every_do_block — m3 is already CORRECT; m2 prints `2 2 2` vs correct `2 4 6`). Deferred refactor **IBB-9-RELOP-PORTS** (retire the flag+`BB_IF` router; relop routes via own γ/ω). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PLR-J-2 LANDED — explicit per-node resume predicate** (2026-05-29, Opus 4.8, one4all `751c5f10`). `lower_pl.c` only, +~24 lines, lower-time only, byte-identical, no emitter/FACT change. Replaced the inline `(t==BB_PL_CALL||t==BB_CHOICE||t==BB_PL_ALT)` resumable tests in `lower_pl_new_Conj` (`gβ[]` wiring) and `lower_pl_clause_body` (body backtrack chain) with one named predicate `pl_node_is_resumable(BB_t*)`, transliterating JCON irgen.icn F2/F3 (redo edge wired by name, not a runtime nearest-resumable-predecessor scan). Dual of PLR-J-0's `pl_goal_is_bounded`: bounded goal → β dead → non-resumable; unbounded (user call / choice / disjunction) → resumable → conjunction threads a redo edge in. BYTE-IDENTICAL to the structural test it replaces for every node kind emitted today (BB_PL_ITE stays non-resumable to the SEQ). Closes PL-LOWER-REVAMP gap (2). Redo edge verified: `pick(1..3). main:-pick(X),X>=2,write(X),nl.` → `2`; backtrack-all → `2`/`3`. Gates byte-identical: GATE-1 5/5, GATE-2 11/121, GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57, FACT 0, siblings 5/5/13. **NEXT: PLR-J-4** (callee-block sweep in `SM_BB_PL_INVOKE` BINARY arm + `bb_pl_call.cpp` MEDIUM_BINARY call protocol in lockstep — binary arm still a double-jump stub; unblocks all multi-predicate programs, largest win for the 121 open mode-3 crosscheck failures; split 4a port-protocol / 4b callee-sweep+drop-guard if needed) or PLR-J-5 (BB_CHOICE as ir_a_Alt + gprolog retry/trust ordering; depends on J-2 ✅ + J-4). [Prior: **PLR-J-0** (`e2d99c3d`) `bounded` determinacy classifier; **PLR-J-3** (`bbf60667`) compound-term builder in raw bytes, GATE-2 crosscheck 10→11; **PLR-J-1** (`efbdd61c`) CAT-D-10 type-test BINARY arm.] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-1010-ALIAS-ALTENTRY-FIX LANDED ✅** (Opus 4.8, 2026-05-29). **Native 250→251 (+1), zero regression.** Both bisected 1010 sub-bugs (OPSYN-alias recursion `OPSYN(.facto,'fact');facto(4)` AND alternate entry point `DEFINE('fact2(n)',.fact2_entry)`+recursion) shared ONE root cause and ONE +13-line fix in `interp_hooks.c::_usercall_hook`. Not frame-setup — a name-resolution infinite loop: the early `FNCEX_fn` guard bounced to `APPLY_fn` whenever `sm_label_pc_lookup(name)<0` (testing only the DIRECT name); an alias (body under entry `fact`) and alt-entry fn (body under `fact2_entry`) have no same-name SM label → bounce → `fn==NULL` → `g_user_call_hook`→`_usercall_hook`→∞→stack-overflow SEGV. Block-1 below already resolves both via `FUNC_ENTRY_fn` but the early guard never reached it. Fix: try uppercase-name + `FUNC_ENTRY_fn` PCs before bouncing; only reach `APPLY_fn` for genuine C builtins. 1010_func_recursion 4/4 byte-exact; FAIL-diff = exactly 1010 newly green. Gates: smoke 13/13 ×2, rung M2=19/0 M4=18/1 (053 pre-existing), mode-2 251 unchanged, broker 49/11 (identical before/after), cross-lang 5/5/5/5, FACT 0, audit GATE OK. **NEXT: 1016 eval SEGV, 1013 NRETURN-lvalue, 1011 redefine, 1017 arg_local; then SPAN/ARBNO/FENCE BINARY-arm clusters; then flip default to native.** [Prior: **SBL-BREAKX-2 + SBL-DATA-FN-SHADOW** native 245→250; **SBL-NATIVE-FN-1** NRETURN read-deref +2; **SBL-DEFER-NESTED** +20; **SBL-TAB-RTAB-FIX/POS-RPOS-FLAG-FIX/SPAN-ARB-ESCAPE/POS-PATCH-OFFSET/ARBNO/M3-NATIVE-4/EP-BINARY/CAP**.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-BB-5.4a + 5.4b COMPLETE** ✅ (Opus 4.8, 2026-05-29, one4all `56a30122`). **GATE-RK mode-2 33→35/42, GATE-RK4 mode-4 34→36/42.** THREE commits, green/regression-free. **5.4a `.method` list-method forms** (`dbb3d15f` postfix + `91bfae91` for-form): `.reverse`/`.unique`/`.sum`/`.elems`/`.head(N)`/`.tail(N)` routed from `TT_METHCALL` (after class static-resolution miss) + `TT_FIELD` (bare) to the list-context value helpers via the `raku_is_listmeth` whitelist, ahead of the class `raku_mcall`/`FIELD_GET` fallbacks; new `head`/`tail` value builtins (trailing arg=N, bare N=1); `for`-CALL materialise guard widened (`raku_methform_listmeth`) so `for @a.reverse -> $x` iterates. Pure value helpers, FACT-clean, byte-identical m2/m4; class methods/fields untouched. **5.4b parenthesized array literal `my @a=(1,2,3)`** (`56a30122`): two initializer-only `raku.y` productions mirroring 5.3 bare comma-list → **NET-ZERO new conflicts (still 30)**; single-paren `(7)` stays scalar; general-atom form added +2 and was reverted. New probes `rk_listmeth`, `rk_paren_array`. Gates: smoke raku/icon/prolog/snobol4/snocone 5/5/5/13/5 HOLD, FACT 0. Handoff `HANDOFF-2026-05-29-OPUS48-RAKU-BB-5-4-METHODS-AND-PAREN.md`. **NEXT (RK-BB-5.4c):** `zip`/`cross` multi-Seq drivers — each output element is itself a list → needs a nested-tuple rep (STX-within-SOH) understood by `for`/`say`/`.elems`; NOT a pure value helper, broad blast radius, recommend fresh session. Or the deferred regex cluster (GOAL-RAKU-PAT-BB). [Prior: **RK-BB-5.0..5.3** (`36e41ed6`) reverse/unique/sum/join consumers + comma-list array init; **4c/4d** mode-4 junctions + precedence + nesting; **M3-RK-NOINTERP-1a..1d**.] |
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
