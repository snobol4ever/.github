# GOAL-ICON-FULL-PASS.md — Icon: m3/m4 → 283/283

## ▶▶▶ RUNG #1 — FIRST, ALWAYS: GET `corpus/benchmarks/icon/*.icn` PROGRAMS WORKING ◀◀◀

**This is the TOP priority of this goal. Do it FIRST, before any other rung below.** (Lon directive 2026-06-23.)

**State (2026-06-23):** **9/13 benchmarks parse AND compile to assembling `.s`** — concord deal ipxref micsum post queens shuffle tgrlink version. Sources are semicolonized (SCRIP Icon requires explicit `;`; NO newline processing — see the SEMICOLON-REQUIRED FACT RULE + PRISON gate). `link`/`invocable` now parse (BENCH-0 landed). `version` is SMX-clean (has `.s`).

**THE ONE BLOCKER for the 8 compiling-but-excising benchmarks: the `scan` box has no mode-3/4 native arm.** Landing it flips concord deal ipxref micsum post queens shuffle tgrlink from SMX-excise to clean `.s` AT ONCE. Canonical: `refs/icon-master/src/runtime/fstranl.r` (`any bal find many match upto`) + `fscan.r` (`move pos tab`); ICN-SCAN ladder in GOAL-ICON-BB.md; register contract = SNOBOL4 Σ(R13)/δ(R14)/Δ(R15).

**4 still parse-blocked on real expression-grammar gaps (NOT semicolons):** geddump (`return` in expr position), micro (`create` as expr), options (`if-then-else` as assignment RHS), rsg (parenthesized comma-expr `(=\"<\",tab(...))` in subscript).

**Next concrete steps, in order:** (1) the `scan` box for modes 3/4 → 8 benchmarks to clean `.s`; (2) BENCH-1 link resolution (fold linked `.icn` into program — `icon_compile` has `filename`; libs options/post/shuffle are in `corpus/benchmarks/icon/`); (3) the 4 grammar gaps; (4) `.expected` oracles + headline `BENCH-Q`/`BENCH-C` diffs. Gate every step with `bash scripts/test_icon_rung_suite.sh` (no regress) + `bash scripts/test_gate_icn_semicolon_required.sh`.

---

## ▶▶ CURRENT PRIORITY — JCON/ICON BENCHMARKS (BENCH ladder) ◀◀

**Goal:** all canonical JCON/Icon benchmarks running natively (m3 `--run` AND m4 `--compile`), stdout == oracle, within timeout.  
**Oracles:** `corpus/programs/icon/rung36_jcon_*.expected` (link-free; queens/concord/genqueen present; deal/ipxref/rsg still need oracle — see BENCH-ORACLE).  
**Benchmark sources:** `corpus/benchmarks/icon/*.icn` (merged icon-master + jcon-master into single folder — queens, concord, deal, ipxref, rsg, micro, micsum, version, …). NOT `programs/icon/` (that is the rung *test* suite).  
**Side-by-side `.s` artifacts:** every benchmark `.icn` in `corpus/benchmarks/icon/` that compiles cleanly carries a sibling `.s` (current GAS emitter output), committed next to its source as an emitter-regression snapshot. Maintained ONLY by `SCRIP/scripts/update_icon_bench_asm.sh` (default corpus `benchmarks/icon/`, glob `*.icn`); never hand-edited. Run it on every Icon-emitter handoff and commit the corpus delta alongside the SCRIP commit. Procedure: `.github/PROC-ICON-BENCH-ASM.md`. Baseline `dd0d0a2`: maintained=3 (`micro micsum version`); the rest CERR/EXCISED until their native arms land, then auto-acquire a `.s`.

### BENCH rung ladder

- [ ] **BENCH-ORACLE** — link-free `.icn` + `.expected` for deal/ipxref/rsg. deal+rsg nondeterministic (`&random`) → seed-pin or XFAIL. ipxref deterministic → build/capture or hand-author.
- [x] **BENCH-0** — `link`/`invocable` parse → `TT_LINK`/`TT_INVOCABLE` AST (parser production landed this session). `--dump-ast` no longer errors on `link`/`invocable` lines. Resolution (fold linked `.icn` into program) is BENCH-1, still open.
- [ ] **BENCH-1** — library resolution: resolve linked name to `.icn` on IPL search path; parse+lower into same program.
- [ ] **BENCH-2** — `&time` keyword (elapsed-ms int; strip timing lines in diff harness).
- [x] **BENCH-F1.5** — flat-chain UNOP-assign value-flow (`x := \expr`, `x := /expr`) — LANDED `a18778b`.
- [x] **BENCH-F1** — `IR_IDX_SET` scaffolding landed `04197ed`, gated to clean EXCISE. Global path verified working (Opus probe). Gate off once F3 done (no benchmark is blocked solely on F1).
- [x] **BENCH-F2** — `IR_RASGN` (`<-`) full scaffolding landed `a54ebef`, gated to clean EXCISE. **Remaining gap:** rhs-var slot collides with dest-var slot inside conjunction chain — `bb_varslot_peek(rhs)` returns dest's slot offset instead of rhs's. Fix: trace flat-chain varslot allocation for `(y<-x) & write(y)`. Repro: `x:=5; y:=1; (y<-x) & write(y)` → `5`.
- [ ] **BENCH-F3** — generator operand inside relop / chained comparison (`0 = (r:=1 to 3)`, queens full chain). `bb_binop_gen` β re-pump. Coordinate with rung13 cross_arg.
- [ ] **BENCH-F4** — recursive proc + generator driver (`every q(1)`, q calling q(c+1) under backtracking). Depends on rung02 recursion fix.
- [ ] **BENCH-Q** — `rung36_jcon_queens` m3+m4 == `.expected`. First headline benchmark.
- [ ] **BENCH-C** — `rung36_jcon_concord` (tables + sort + scan + read + find). Clear `.xfail`.
- [ ] **BENCH-D/R** — deal/rsg (blocked on BENCH-ORACLE seed-pin).
- [ ] **BENCH-I** — ipxref (heaviest; after concord).
- [ ] **BENCH-X** — tgrlink/geddump/micro/micsum (optional extras).

### BENCH gate (per step)
```bash
cd /home/claude/SCRIP && make && make libscrip_rt
C=/home/claude/corpus/programs/icon; T=rung36_jcon_queens
IN=/dev/null; [ -f "$C/$T.stdin" ] && IN="$C/$T.stdin"
# m3: timeout 30 ./scrip --run $C/$T.icn < "$IN" > /tmp/b_m3.out 2>/tmp/b_m3.err
# grep -q '\[SMX\]' /tmp/b_m3.err && echo EXCISED || diff /tmp/b_m3.out $C/$T.expected && echo "m3 ✅"
# m4: ./scrip --compile --target=x86 $C/$T.icn > /tmp/b.s && as /tmp/b.s -o /tmp/b.o
#     && gcc -no-pie /tmp/b.o -Lout -lscrip_rt -Wl,-rpath,out -lgc -lm -o /tmp/b.bin
#     && LD_LIBRARY_PATH=out timeout 30 /tmp/b.bin < "$IN" > /tmp/b_m4.out
#     && diff /tmp/b_m4.out $C/$T.expected && echo "m4 ✅"
bash scripts/test_icon_rung_suite.sh --mode run     | tail -1   # must not regress
bash scripts/test_icon_rung_suite.sh --mode compile | tail -1
```

---

**Status:** m3/m4 **144/283** · FAIL 14 · XFAIL 36 · EXCISED 89 · HEAD(SCRIP)=`e928643`.  
m2 `--run` is deleted (GOAL-DE-INTERP); suite reports phantom m2 FAILs — **ignore m2, gate on m3/m4 only**.  
**Always diff FAIL names AND EXCISED names vs baseline in BOTH modes** — a net +PASS can mask an EXCISE→FAIL.

---

## Open 18 FAILs (m3 == m4)

| Group | Tests | Root cause |
|-------|-------|-----------|
| `bb_call` FATAL (rc=134) | `rung08_find{,_gen}`, `rung22_push_put_*`, `rung30_seq`, `rung32_strret_every`, `rung37_proc_lookup` | `builtin_is_generator()` excludes find/seq/push/put from `rt_builtin_is_known` → `CALL_ROUTE_FATAL`. Fix: extend classifier to route generators+mutators through `CALL_ROUTE_BYNAME`. |
| Recursion overflow (rc=134) | `rung02_proc_fact` | `rt_call_proc_descr` hits 4096-frame limit. |
| `suspend…do` generator (rc=124) | `rung03_suspend_gen{,_compose,_filter}` | IR_SUSPEND/EVERY interaction with flat chain incomplete. |
| `limit \` (rc=124) | `rung14_limit_{large,to,zero}` | `flat_drive_limit` has no counter — unbounded generation. Canonical: `ir_a_Limitation` (irgen.icn:113). |

| cross-arg alternation (wrong output) | `rung13_alt_alt_cross_arg{,_sideeffect}` | `every write(1\|2,":",3\|4)` — multi-gen CALL args; `is_deep` ag-ring stale on carry. |

---

## BB / Byrd-Box discipline

**ALL temporaries and local allocation storage in BB templates must use `DESCR_t` (16-byte frame slots).** No raw int/pointer spills to the frame — every slot is a full `DESCR_t` claimed with `bb_slot_claim(16)`, addressed as `FRQ(slot)` (low 8) + `FRQ(slot+8)` (high 8). This ensures DESCR_t-clean frame layout and will support cross-language BB interfacing. Exception: SNOBOL4 pattern-match BBs use sub-16 `x86_scratch_off` for internal counters — those are a separate discipline and not touched here.

**`DESCR_t` layout:** `{DTYPE_t(4)+slen(4) | int64/ptr(8)}` — passed/returned as **rdi:rsi** (args) / **rax:rdx** (return). The high 8 bytes are INTEGER-class even when holding a `double`.

---

## Session setup
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
make && make libscrip_rt
bash scripts/test_smoke_icon.sh      # m3 12/12 · m4 12/12 (m2 line phantom)
bash scripts/test_smoke_prolog.sh    # m3 5/5 · m4 5/5
```

## Gate after every step
```bash
make && make libscrip_rt
bash scripts/test_icon_rung_suite.sh
bash scripts/test_gate_bb_one_box.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_gate_icn_no_stack.sh; bash scripts/test_gate_icn_one_reg_frame.sh  # == 0
bash scripts/test_gate_icn_semicolon_required.sh  # Icon requires ';'; no newline processing (PRISON)
```

## Canonical sources
- Port topology: `corpus/programs/icon/jcon-ref/irgen.icn`
- Runtime: `corpus/programs/icon/` (ocomp.r / fstranl.r / oarith.r / oref.r / oasgn.r / ovalue.r)
- `<-` canonical: `oasgn.r` rasgn `operator{0,1+}`; irgen.icn:472 `ir_a_Binop` op `"<-"`, `ir_rval`→`&null` arg 1
- `limit \`: irgen.icn:113 `ir_a_Limitation`

## Key intel
- `icn_ring_to_tree` returns NULL when chain has IR_BINOP/IR_LIT_I → falls to `descr_flat_chain_build`.
- `--dump-bb` does NOT show `operand_aux`. Chain-node indices (`xchainN_nK_*`) are CHAIN positions, not graph node ids.
- Gate: `graph_native_emittable_mode` (scrip.c, permissive-by-default). To EXCISE a kind, reject it there.
- m3 binary tolerates dup labels (last-wins); m4 `as` rejects them (rc=1). Always assemble `.s` standalone.
- Globals route through NV dictionary (all modes). Locals keep frame slots.
- RT = value (takes/returns DESCR_t, no ports). BOX = ports (marshals args, calls RT, wires α/β/γ/ω). No duplicated logic.

---

## Watermark

**2026-06-23 (Claude) — Benchmark corpus unblocked: semicolonized sources + `link` parsing + return-terminator fix. 9/13 benchmarks now parse and compile to assembling `.s` (was 3).** Three pieces, all rule-compliant (compiler does ZERO newline processing):
(1) **ICON SEMICOLON-REQUIRED FACT RULE + PRISON** authored — `scripts/test_gate_icn_semicolon_required.sh` (3 locks: no insertion machinery; `TK_SEMICOL` minted only from literal `;`; behavioral canary — newline-separated bare statements MUST parse-error, semicolon-separated MUST parse). Adversarially verified: a disguised insertion that evades both grep locks is still caught by the behavioral canary. FACT RULE in GOAL-ICON-BB.md; terse line in RULES.md; wired into Session-Setup + per-rung gate lists here and in GOAL-ICON-BB.md.
(2) **`link`/`invocable` parsing (BENCH-0)** — `TT_LINK`/`TT_INVOCABLE` added to `src/contracts/ast.h`; top-level parse production in `src/parser/icon/icon_parse.c`. The 6 benchmarks that died at `link` now parse it.
(3) **`return`-terminator parser gap** — bare/value `return` before `}`/`end` was rejected at both `return` parse sites; both now accept those terminators with optional `;`. (Genuine grammar fix, suite-neutral.)
**Benchmark sources semicolonized** (corpus `benchmarks/icon/*.icn`, all 13) — verified byte-identical to prior HEAD MODULO the added `;` (no content altered). The disallowed semicolon-adding TOOL was NOT committed (months-old disallowance; semicolons are hand-added and checked in).
**Status:** 9/13 parse-clean + compile to assembling `.s` (concord deal ipxref micsum post queens shuffle tgrlink version); `version` SMX-clean (has `.s`); the other 8 excise on ONE feature — **`scan`** (string-scanning box, no mode-3/4 native arm). 4 still parse-blocked on real expression-grammar gaps (NOT semicolons): geddump (return-in-expr), micro (`create` expr), options (`if` as assign RHS), rsg (paren comma-expr in subscript). **Rung suite UNCHANGED 144/283 — zero regression.** icon smoke 12/12 m3+m4, prolog 5/5, prison green. **KEY LEVER: the `scan` box for modes 3/4 flips 8 benchmarks from SMX-excise to clean `.s` at once.** HEAD(SCRIP) pending push.


**2026-06-23 (Claude) — `.s` artifact maintenance repointed to the real benchmark corpus.** `update_icon_bench_asm.sh` defaulted to `programs/icon/` (the rung *test* suite) glob `rung36_jcon_*.icn` — WRONG. The benchmark sources are `corpus/benchmarks/icon/*.icn` (queens/concord/deal/ipxref/rsg/micro/micsum/version/…), which had ZERO `.s`. Fixed: script default → `benchmarks/icon`, glob `*.icn` (SCRIP `97e4d9d`); generated `.s` for the 3 that compile today — `micro micsum version` (corpus `a88c6ad8`); GOAL+PROC docs corrected (.github `22a81433`). The other 10 CERR/EXCISE pending native arms (F2 `<-`, F1 subscript-assign, link resolution) and auto-acquire a `.s` the moment they compile. NO codegen touched; suite unchanged 144/283; `CHECK=1` clean (zero drift).

**2026-06-22 (Claude) — Corpus benchmarks/icon + benchmarks/jcon merged into single benchmarks/icon/ folder** (37bc1bc5, corpus). jcon-only files moved in (geddump/tgrlink/version); concord.dat jcon superset used; rsg.dat icon-master (1000-poem) retained. README-ICON-JCON.md updated.

**2026-06-22 (Claude) — BENCH-F2 `<-` scaffolding landed, gated (a54ebef).** IR_RASGN + lower_icon case + bb_rasgn.cpp + flat_drive_rasgn + dispatch. Remaining gap: rhs-var slot collides with dest-var slot in conjunction — `bb_varslot_peek(rhs)` returns dest's offset. No regression: m3/m4 140/140, gates green.

**2026-06-22 (Claude) — BENCH-F1.5 UNOP-assign value-flow (a18778b).** m3/m4 138→140. `x:=\expr`/`x:=/expr` now emit natively. Two-line fix: (1) `rhs_kind_ok` admits IR_UNOP; (2) `codegen_flat_chain_body` pre-registers all locally-assigned varslots before walk. Root cause: BFS ω-edge enqueue dequeued var-read before its producing assign; pre-registration decouples read-resolution from walk order.

**2026-06-22 (Claude) — BENCH-F1 IR_IDX_SET scaffolding (04197ed), gated.** `subscript_set` rt helper exists; bb_idx_set template + flat_drive_idx_set + dispatch built. Gated to clean EXCISE. Global path verified working (gate-off probe). Local path excises on unrelated reason. Leave gate as-is until a benchmark is otherwise green and only idx_set remains.

**2026-06-19 (Claude) — BENCH ladder authored.** queens blockers verified: IR_IDX_SET (list-element assign) + IR_RASGN (`<-`) + generator-in-relop. Oracle correction: `*.std` files are NOT stdout — real oracle is `rung36_jcon_*.expected`.

**Earlier landings (see git log):** local-VAR builtin-call arg marshal (5f54227, +5); real-POW (fe80ecf, +1); real-arith binops+relops (c26f89f, +5); IR_CASE native (176ecda, +5); IR_SWAP `:=:` native; bb_every four-port; local IR_VAR varslot alias (9354db7, +4); deterministic builtins + subscript s[i] + global-VAR reads (1fcd8c5, +17); Jcc opcode fix (521ab64, +6); real constant-fold; pow constant-fold.

**2026-06-22 (Claude Sonnet 4.6) — Dead interp eradication + real TO/BY native (`e928643`).** gen.h stripped to BinopKind-only; 34 dead gen_bb_*(void*,int) externs deleted from emit_bb.c; gen_runtime.h/c + resolution.h dead bb_node_t decls removed. Real TO/BY: flat_drive_to sets op_num_real, claims 16B counter slot; bb_to.cpp real branch via rt_jct_relop/rt_num_arith (loop label L(10) avoids collision with RO seals L(0)/L(1)). IR_RASGN lvalue pre-registration fixed. Suite 142→144.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
