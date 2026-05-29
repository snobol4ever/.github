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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PLR-J-3 LANDED — compound-term builder in raw bytes** (2026-05-29, one4all `bbf60667`). `bb_builtin.cpp` only, +180 lines, one template file, FACT 0/12. Added `emit_build_compound_term_bin` (MEDIUM_BINARY twin of the TEXT recursive `emit_build_compound_term`) + `functor/3`, `arg/3`, `=../2` compound-literal MEDIUM_BINARY arms. Was TEXT-only → in mode-3 native (`--run`) the asm strings emitted as raw bytes → `functor/arg/=..` produced garbage (rung09 printed `_ _ / _ / _`). Binary builder mirrors TEXT walker byte-for-byte: absolute `movabs` for interned-string + helper pointers (valid in-process for mode-3 native), `movabs rax,&helper; call rax` instead of RIP-rel `lea` + PLT; leaf→`rt_pl_node_to_term`, BB_PL_STRUCT→aligned slot frame + per-arg recurse + `rt_pl_compound_build_n`. Arms wire `_term` helper variants with standard `test/je ω/jmp γ/β→ω` bin-patch tail. **rung09 mode-3 native now byte-matches mode-2** (`foo 2`/`b`/`[foo,a,b]`); **GATE-2 crosscheck 10→11 PASS** (rung09 3-mode agreement, no swaps). Gates: GATE-1 5/5, GATE-3 m2 104/107 (byte-identical), GATE-4 4/4, FACT 0/12, siblings icon/raku/snobol4 5/5/13. Type-test BB_PL_STRUCT compound arg (`is_list([1,2,3])`) still honest-abort-guarded (wires a different helper `rt_pl_type_test_term`, untouched here; not corpus-blocking). **NEXT: PLR-J-2** (explicit per-node resume, replace β heuristic, transliterate irgen.icn `ir_a_Binop`/`ir_a_Mutual`/`ir_a_Call`; depends on PLR-J-0 `bounded` flag) or **PLR-J-4** (callee-block sweep + `bb_pl_call` binary call protocol — unblocks all multi-predicate programs, largest win for the 121 open mode-3 crosscheck failures). [Prior: **PLR-J-1** (`efbdd61c`) CAT-D-10 type-test BINARY arm; **PL-TRAIL-COND** tried+reverted (`40c17ecb`, CLOSED won't-fix — boxed GC has no heap reclamation); B3 sumto(1e7) O(1) heap (`0019cc7b`); print/1 mode-4 corpus 55/107 (`2fae45ec`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-BREAKX-2 + SBL-DATA-FN-SHADOW LANDED ✅** (Opus 4.8, 2026-05-29). **Native 245→250 (+5), zero regression** (smoke 13/13 ×2, rung M2=19/0 M4=18/1 [053 pre-existing], broker 44, cross-lang smokes icon/prolog/raku/snocone/snobol4 5/5/5/5/13, FACT 0, audit GATE OK). **(1) SBL-BREAKX-2** — `bb_pat_break.cpp` BREAKX (is_breakx, ival==1) MEDIUM_BINARY arm was a 2-jump stub with malformed sites `{1,2}` → patcher ate the 2nd `E9` → rel32 at output offset 19 vs empty label → `bb_emit_end` SIGABRT on every native BREAKX. Replaced with a real 302-byte α-scan + β-rescan blob (α: scan to first cset char, Δ+=z, jmp γ; β: recover z_orig=Δ−z arithmetically, z++ step-past, rescan to NEXT cset char → jmp γ/ω). Assembled+verified via `as`/objdump, transcribed FACT-pure. Native +2 (W05_breakx, word4 byte-exact incl mid-pattern REM+SPAN backtrack into β). **(2) SBL-DATA-FN-SHADOW** — native `rt_call` (rt.c) consulted the ungated cross-lang `icn_try_call_builtin_by_name` table (serves Raku/Icon `write`) BEFORE SNOBOL4 `INVOKE_fn`; Icon's `real()` builtin intercepted a SNOBOL4 `real(X)` on a `DATA('complex(real,imag)')` object (fails on DT_DATA) instead of the DATA accessor (`imag` worked — no Icon `imag`). Fix: exported `sno_fn_registered()` (case-sensitive `_func_buckets` presence) + gated the icn fallback behind `if(!sno_fn_registered(name))` so a user-DEFINE/DATA-registered SNOBOL4 fn shadows any cross-lang builtin; unregistered names unaffected. Native +3 (094_data_define_access, 811_size, match_driver — all byte-exact, same shadow class). **NEXT: 1010 SEGV bisected → 2 native-dispatch sub-bugs (OPSYN-alias recursion `OPSYN(.facto,'fact');facto(4)`; alt-entry `DEFINE('fact2(n)',.fact2_entry)`+recursion); plain recursion fine. Then 1016 eval SEGV, 1013/1011/1017 (oracle gaps too).** [Prior: **SBL-DEFER-NESTED ✅** native 223→243 (+20) — nested `*var` under combinator, three gaps (walk_bb_flat DEFER→FILL, patnd_to_bb_tree kid-traversal, rsp 16-byte align); **SBL-NATIVE-FN-1 ✅** NRETURN read-deref native +2; **SBL-TAB-RTAB-FIX/POS-RPOS-FLAG-FIX/SPAN-ARB-ESCAPE/POS-PATCH-OFFSET/ARBNO/M3-NATIVE-4/EP-BINARY/CAP**.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **RK-BB-5.0..5.3 (list/array Seq consumers + comma-list array initializer) COMPLETE** ✅ (Opus 4.8, 2026-05-29, one4all `36e41ed6`). **GATE-RK mode-2 28→33/40, GATE-RK4 mode-4 29→34/40.** FIVE commits, all pure value helpers in `raku_builtins_byname.c` (flatten SOH-array args into segments; no emitted x86, FACT-clean; reachable mode-2 `sm_interp` + mode-4 `rt_call`; byte-identical across modes). **(5.0 `a4bc02d4`)** `reverse(LIST/@arr)` eager-drain reorderer — `for reverse(...)` rides the existing `for CALL(...)→$v` materialization branch. **(5.1 `8b10f978`)** `unique` (dedup first-occurrence) + `sum` (INTVAL all-integral else REALVAL). **(5.2 `ed321adc`)** `join(SEP,LIST)` fold-to-string; composes with reverse. **(5.x `f9425b68`, test-only)** array-arg coverage — confirmed reverse/unique/sum/join all work on push-built `@arrays` (diagnostic: `@`-args were NEVER the gap). **(5.3 `36e41ed6`)** comma-list array initializer `my @a = e1,e2,...` — the REAL gap behind `my @a=1,2,3` parse errors. Two `raku.y` productions build `ASSIGN(@a, __rk_arr(...))`; lookahead `;`(single-expr) vs `,`(comma-list) is a clean LALR split → **net-zero new conflicts (still 30 s/r)**; parser regenerated via the `regenerate_parser_and_lexer_from_sources.sh` recipe (bison 3.8.2); new `__rk_arr` builtin packs args into an in-order SOH-array. Probes: rk_reverse, rk_unique_sum, rk_join, rk_seq_consumers_arr, rk_array_literal. Gates: smoke raku/icon/prolog/snobol4/snocone 5/5/5/13/5 HOLD, FACT 0, no regressions any commit. Handoff `HANDOFF-2026-05-29-OPUS48-RAKU-BB-5-SEQ-CONSUMERS.md`. **NEXT (RK-BB-5.4..N):** (a) `.method(N)` parsing (`@a.tail(2)`/`.head`/`.reverse`) — unblocks the method-form consumers the goal names; (b) parenthesized literal `my @a=(1,2,3)` (list-atom, conflict-prone); (c) `zip`/`cross` multi-Seq drivers (need nested-tuple rep). [Prior: **RK-BB-4c/4d** (`1652aeb9`) mode-4 junctions + precedence + nested mixed-flavor; **RK-BB-4** (`30e7c0a1`) mode-2 junctions; **M3-RK-NOINTERP-1a..1d**.] |
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
