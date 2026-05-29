# HANDOFF — 2026-05-29 — Opus 4.8 — GOAL-RAKU-BB — RK-NFA regex onto the isolated BB_NFA_* family

**Author:** Claude (Opus 4.8) · with Lon Jones Cherryholmes
**Goal:** GOAL-RAKU-BB — Raku regex onto the ISOLATED `BB_NFA_*` family (NOT SNOBOL4's pattern opcodes).

## Session arc (five landings, all green, all pushed)

1. **RK-NFA-1e — regex on the SM dispatch path** (one4all `0d94e255`).
   `~~` lowered to `SM_CALL_FN raku_match` but the only handler was the legacy tree-walk
   `raku_try_call_builtin(tree_t*)`; the SM byname dispatcher (`sm_interp.c:1387` mode-2,
   `rt.c:1598` mode-4/3-via-rt_call) never knew the name → all 6 regex tests failed BOTH modes.
   Closed past option-A and lit the WHOLE cluster: (1) by-name twins `raku_match`/`_global`/
   `raku_subst`/`raku_nfa_compile`/`raku_re_capture`/`raku_named_capture` in
   `raku_builtins_byname.c`, all via the ISOLATED `raku_nfa_*` matcher; (2) capture name-collision
   fix — the lexer mapped BOTH `$*STDOUT`/`$*STDERR` (FH) and `$0`/`$1` (regex) to
   `VAR_CAPTURE→TT_CAPTURE→raku_capture`; split at the lexer: `$*STD*`→new `VAR_FH`→
   `TT_FH_CAPTURE`→`raku_capture` (FH, byte-identical), `$0`/`$1`→`VAR_CAPTURE`→`TT_CAPTURE`→new
   `raku_re_capture` (group slice); net-zero new grammar conflicts (still 30); (3) subst write-back —
   `lower_expr` emits `STORE_VAR`+re-`PUSH_VAR` after `raku_subst` when the LHS is a plain `TT_VAR`.
   **GATE-RK m2 35→41, m4 36→42.**

2. **Rename RK-PAT → RK-NFA** (one4all `a5e45c1e`, .github `4930a040`).
   Per Lon directive: the Raku regex ladder uses NFA-derived names, never PAT (PAT = SNOBOL4's
   pattern opcodes; PAT in Raku context signals opcode misuse). Renamed Raku-owned identifiers:
   `RK_PAT_BB`→`RK_NFA_BB` (env + local), `RK-PAT-*`→`RK-NFA-*`, `GATE-PAT-O`→`GATE-NFA-O`, stale
   `GOAL-RAKU-PAT-BB`→`GOAL-RAKU-BB`. Rephrased SNOBOL4 contrast prose to drop the literal token.
   SNOBOL4's OWN artifacts (`snobol4_pattern.c`, `BB_PAT_*`, `test_snobol4_pat_rung_suite.sh`) left
   untouched — correctly SNOBOL4-owned. Both files PAT-clean (no standalone PAT token in Raku context).

3. **RK-NFA-1b — `raku_nfa_to_bb` graph builder** (one4all `6b593da8`).
   State→node walk in `raku_nfa_bb.c`: `nfa_kind_to_bb` 1:1 `Nfa_kind`→`BB_NFA_*`, one `BB_t`/state,
   ports γ=out1-node (advance) / β=out2-node (SPLIT backtrack) / ω=NULL, payload CHAR ival=char /
   CLASS sval=32-byte cset / CAP ival=group-idx, entry=start node, NULL on Phase-2 kinds. Verified
   standalone across the full L1-L15 set (graph faithfully mirrors the NFA). Pure graph construction,
   no x86, dead-code-until-RK-NFA-4. The prereq for mode-4 template emission.

4. **Mode-3 gate added + stale claims corrected** (script: one4all `40ee1477`).
   Lon asked why only m2/m4 numbers showed. Created `scripts/test_raku_mode3_native.sh`
   (`SCRIP_M3_NATIVE=1 ./scrip --run`). Result: **mode-3 native 41/42, CRASH 0** — regex passes
   natively too. The prior "MODE3-DISPATCH-GAP / --run emits no output / CRASH 6" was STALE: that
   betrayal was retired. `scrip.c` 554-567 runs Raku `--run` via `sm_run_native` (no interp fallback,
   abort-on-failure); `sm_native.c` has ZERO `sm_interp_run` refs; `SM_CALL_FN`→`call rt_call`→
   `raku_try_call_builtin_by_name` — the dispatcher shared by all three modes. Mode-3 passes are
   genuine (rk_re34 emits real multi-line capture output). RK-NFA-5 reframed: MOVE regex onto the
   isolated `BB_NFA_*` slab (architectural), not a crash-fix.

5. **RK-NFA-4 SCAFFOLD** (one4all `ac1bc66b`).
   Begins mode-4 emission. NEW `bb_nfa.cpp`: trivial passthrough templates `bb_nfa_eps`/`cap_open`/
   `cap_close` (pure `jmp γ`, clone of `bb_eps`). All 10 `BB_NFA_*` opcodes wired into `emit_core.c`
   dispatch (3→templates, 7 consuming/branching CHAR/ANY/CLASS/SPLIT/BOL/EOL/ACCEPT→`bb_stub`
   placeholder). Prototypes in `bb_templates.h`; Makefile RT_PIC_SRCS **and** explicit `bb_nfa.o`
   scrip `-c` rule (BOTH mechanisms needed — `scrip` links `$(OBJ)/*.o`; missing the explicit rule
   was the link-fail gotcha I debugged). Dead-code-until-`~~`-rewiring; zero regression. Full
   byte-writing DESIGN block is in GOAL-RAKU-BB.md.

## Final gate snapshot (definitive, this handoff)

```
mode-2 (--interp):      41/42   (only rk_stdio39 — stderr→fd-1 fidelity non-bug)
mode-3 native (--run):  41/42   CRASH 0   (HONEST native, verified)
mode-4 (--compile x86): 42/42   PERFECT
smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5  HOLD
SNOBOL4 isolation (pattern-rung suite): M2 19/0  M4 18/1  (byte-identical — isolation proven)
FACT grep:   0
bison s/r conflicts: 30 (unchanged)
build: clean
```

## NEXT — RK-NFA-4 byte-writing (fresh full-budget session)

The remaining work is the 7 consuming/branching templates + capture block + `~~` rewiring — where
real x86 gets written under the FACT rule. The graph (`raku_nfa_to_bb`, RK-NFA-1b ✅) and the verdict/
capture/subst goldens (all 3 modes green via the C matcher) are ready as the oracle. Execute the
RK-NFA-4 DESIGN block in GOAL-RAKU-BB.md:
- 7 templates in `bb_nfa.cpp`: CHAR/ANY/CLASS (char/cset test→γ/ω, pos++), SPLIT (γ then β backtrack —
  model on `BB_ALT`'s counter-state slab), BOL/EOL (pos guards), ACCEPT (set match-end → graph-γ).
  Register model: pos/subject/slen in callee-saved regs set by the driver α; capture block via
  movabs (m3) / @PLT (m4), NOT a BB_t field (PEERS RULE); cset = 32-byte sval blob in rodata.
- Driver: leftmost-unanchored sweep (mirror `raku_nfa_bb_match`'s start-pos loop); `BB_PUMP` kind.
- `~~` rewiring: alternate lowering builds the graph via `raku_nfa_to_bb` + emits `SM_BB_INVOKE`
  (mirror `lower_raku_iterate_arr` + the `SM_BB_INVOKE` site in `lower_every`); gate behind
  `RK_NFA_BB=1`, flip default last.
- Isolation gate EVERY step: `scripts/test_snobol4_pat_rung_suite.sh` must stay M2 19/0 M4 18/1,
  FACT 0, GATE-RK4 not below 42/42, GATE-RK3 not below 41/42.

Alternative substantive next: **RK-BB-5.4c** (`zip`/`cross`) — needs a nested-tuple rep, own session.

## Heads
- one4all  `ac1bc66b`
- .github  `e333fa22`
- corpus   unchanged (`0f692c3`)
