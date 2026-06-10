# HANDOFF 2026-06-10 — IR-REDESIGN lower rewrite: Raku UNPARK (value-ring pivot) + Pascal WHILE

Goal: **GOAL-IR-REDESIGN.md** ("lower rewrite"). The five NEW lowerers at `src/lower/nl/lower_*_nl.c`
are the deliverable. METHOD (strict): `--dump-bb` (OLD lower = oracle) vs `--dump-bb2` (NEW) →
normalized diff → fix FIRST divergence → `make scrip` → re-diff → COMMIT each green rung + guarded push.
NEVER read OLD lower source (lower.c / lower_program.c / lower_*_*.c); reproduce oracle BYTES only.

## State on origin (both verified clean, 0 ahead / 0 behind)
- **SCRIP `0ecd99c`** · **.github `d860a202`** (this doc adds one more .github commit).
- NOTE: a parallel emitter workstream (bb_alt / BB-FIXUP, e.g. `ddd60fe`, `89e64efe`) pushes
  concurrently — always `git fetch && git pull --rebase` before push. Integrated cleanly every time.

## Scores now (normalize=1, NEWFAIL=0 everywhere)
icon **6/8** · pascal **78/91** · snobol4 **147/153** · snocone **142/142 CLEAN** · prolog **0/7** ·
raku **1/29** (was 0). The written BASELINE/watermark in the goal file is STALE — trust the live
`bash scripts/scoreboard.sh LANG` (langs: icon snobol4 snocone prolog pascal raku).

## Landed this session (each a green rung, pushed)
**Pascal 44→78** (six rungs; earlier four were `141a617` nested-binop-result, `2263e33` frame-capture,
`151dbff` records/arrays as TT_IDX → arr_get/arr_set_pure, `db97f49` deref-set `p^:=v`):
- **`8ddfd2a` WHILE wiring** — (1) relop while-condition patches the BINOP RESULT γ (head node
  `all[cmark]`) not the leaf entry; (2) WHILE no longer builds its own back-edge CONJ on top of the one
  `lower_seq` emits — body lowered with γ=ω=cond_entry (loop back to condition), mirroring `lower_for`.
  Fixed double-CONJ + body-ω divergence. 74→78.

**Raku 0→1 — the UNPARK + value-ring pivot** (`0ecd99c`):
- Lon unparked Raku ("new plan"). Phase 5 only ever gated EXECUTION-TRUST on the frontend; the lowerer
  was always green-lit "the same way" — so standard graph-diff method applies, method unchanged.
- ROOT CAUSE of 0/29: skeleton `lower_raku` used the WRONG model (single `IR_PROG` + `ops:[]`).
  Oracle emits **per-proc VALUE-RING graphs** (BINOP `ival`=opcode, CALL `ival`=argcount with INVISIBLE
  args, γ-chaining) exactly like Icon/Pascal.
- PIVOT: added `lower_raku_enum` (finds TT_SUB_DECL; **name = c[0]->v.sval**, **stmts = c[1..n-1]** direct
  children — there is NO c[2] body block) + `lower_raku_proc` (value-ring `lower_rv` with res out-param) +
  an `is_raku` `--dump-bb2` dispatch block in `src/driver/scrip.c` mirroring icon/pascal. Fixed ω marker
  α→β (was a bug). Old `lower_raku` kept as the np<=0 fallback. **rk_arith MATCH.** Risk-free: raku was 0,
  all changes raku-scoped.
- VALUE-RING facts pinned: `say(EXPR)` → build `write` CALL first (γ=continuation, sval="write",
  ival=argcount), then EXPR value-ring with `EXPR.result.γ → CALL`; entry = EXPR.entry. Opcodes
  `+`0 `-`1 `*`2 `/`3 `%`4, relops LT5 LE6 GT7 GE8 EQ9 NE10, `~`(concat)=11. say/print → write/print.
  CALL allocated BEFORE its arg (lower index). `lower_rv` currently covers: literals, TT_VAR, binops,
  TT_SAY/PRINT, TT_FNC user calls, TT_STMT, TT_SEQ/PROGRAM. Everything else → SUCCEED (stub).

## OPEN — needs Lon ruling
- **RAKU MULTI-SUB ORACLE DEGENERACY.** `--dump-bb` emits only ONE proc graph for MULTI-sub programs
  (rk_subs 5 subs, rk_interp 2, rk_combinator 9 → all collapse to 1), a shared-node-array dedup artifact
  of the OLD path. NOT cleanly byte-matchable. Need a ruling like the oracle-crash SKIP list. The
  **SINGLE-sub** programs (oracle_procs=1=source_subs=1) are the matchable set (~17): rk_arith✓, rk_join,
  rk_control, rk_forloop, rk_gather, rk_range_for, rk_for_array{,_simple,_underscore}, rk_junctions/nest/
  prec, rk_re33/34/35/38, rk_reverse, rk_array_literal, rk_arrays, rk_strings, rk_str22, rk_map_grep_sort24.
- Carried: LAD-0b pointer-ival sed load-bearing; 7 OLD-lower oracle crashes in SKIP; `--dump-ast` segfaults
  on multi-proc pascal (works single-proc); LAD-0c (`--dump-bb2` dump-only, no execution validation);
  icon/pascal/prolog/raku `_nl.c` one-liners may exceed 200-char max (mechanical wrap, re-measure first).

## NEXT (resume immediately, cheapest-first, commit each rung)
**Raku** (~16 single-sub DIFFERs): extend `lower_rv` with `my $x=expr` (TT_ASSIGN/DECL value-ring — not
yet handled), for/while (TT_FOR_RANGE / TT_WHILE), string interpolation, junctions (TT_ALT), regex. Verify
each: `./scrip --dump-bb FILE </dev/null` vs `--dump-bb2` (helper `/tmp/dr.sh LANG` if regenerated; uses
strip `^; proc`+blank, norm `ival≥7digits→PTR`). CAUTION: **rk_join has an oracle ival QUIRK** (first
`join` ival=2 vs ival=4 for structurally identical calls) — OLD-path artifact, likely unmatchable, DEFER.
**Pascal** (13 DIFFER): cheapest arrparam (needs local-frame-only-if-has_children: locals are currently
ALWAYS frame via unconditional is_local, but a childless proc's locals should be plain VAR — oracle shows
VAR for sumvec's s/j), then arr2dtype2, read3, goto/case clusters, boolmix/boolchain, char3, sieve, ppp, pcom.
**Other**: icon 2 (queens/generators — suspend/IR_PROC_GEN, hardest), snobol4 5 (eval cluster + roman +
coverage), prolog 0/7 (full goal-directed rewrite like snocone; hello.pl cheapest).

## TERMINAL milestone (not yet safe)
"Install new lowers as default + remove OLD" — gated on large-portion MATCH **plus** execution-trust
(LAD-0c). NEW lowers are dump-only with zero execution validation; do NOT swap/delete yet.

## Env reminders
Build: `apt-get install -y libgc-dev` then `cd SCRIP && make scrip`. Use bash (process-substitution and
`(){}` functions FAIL under the bash_tool's sh — put helpers in `/tmp/*.sh` with `#!/usr/bin/env bash`).
Always `</dev/null` on scrip calls. Commit identity per RULES.md: `git config user.name "LCherryholmes"`,
email `lcherryh@yahoo.com` (set per-repo; .github needed it too). Tokenized remotes set for both repos.
