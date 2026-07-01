# HANDOFF 2026-07-01 — Claude Sonnet 5 — IR dead-opcode cleanup + non-Icon lowerers back in the build

## Context
Session opened on `GOAL-IR-IMMUTABLE-EMIT.md` (named as focus, not opened/worked as a rung ladder this
session). Work instead came from a direct opcode-by-opcode audit — IR_FIELD/IR_FIELD_GET, IR_CONJ/IR_DISJ,
IR_NOT/IR_UNOP_TEST, IR_GOTO/IR_INDIRECT_GOTO — each answered by grepping construction sites (lowerers),
dispatch sites (`emit.cpp`), and template bodies rather than by inference from names. Two concrete actions
came out of that audit, both landed this session.

## Action 1 — deleted two confirmed-dead IR opcodes
`IR_GOTO` and `IR_INDIRECT_GOTO` removed from `IR.h` (enum), `scrip_ir.c` (name-table), and the stale
`emit_per_kind_audit.c` reference. Both were verified (construction-site + dispatch-site grep, whole
`src/` tree) to have zero build sites and zero emit cases — pure placeholders anchoring the JCON
correspondence table (`JCON-TO-SCRIP-IR-MAP.md`), never live. `scrip_ir.c`'s name-table uses designated
initializers (`[IR_X] = "..."`), so removal is position-independent; re-verified by syntax-compiling
`scrip_ir.c` after the edit (exit 0).

Per that same audit: `JCON-TO-SCRIP-IR-MAP.md` itself documents the correct current design — SCRIP's goto
is *structural* (every node's γ/ω edges + the boilerplate `jmp γ` every template already emits), matching
JCON's `ir_Goto`/`ir_IndirectGoto` is Cluster-1/Cluster-5 future work, not something either opcode did
today. Deleting the two placeholders doesn't remove functionality — nothing used them.

## Action 2 — lower_snobol4/prolog/raku/pascal.c back in the Makefile
Per Lon's direction. These four were out of the `scrip` binary recipe under the "Icon-only pivot"
(`lower_noicon_stubs.c`'s own header comment names it); their `.c` files remained on disk but referenced
IR opcodes that no longer exist in the current (post-collapse) `IR.h` — e.g. the SNOBOL4 lowerer's
`IR_GOTO_DYN`, which was never a real enum member, just a dangling identifier.

Fix, mechanical and compiler-verified at every step:
1. Per-file, iterate `gcc -fsyntax-only` → collect every `'IR_X' undeclared` error → sed-replace that
   token with `IR_OP_COUNT` (the array-sizing sentinel, guaranteed valid, greppable) → repeat until clean.
   Compiler chose the set, not eyeballing. Totals: `lower_snobol4.c` 171 tokens (was the entire
   `IR_MATCH_*`/`IR_PATTERN_*` family + old `IR_ASSIGN_*` specializations — 60 distinct phantom opcodes),
   `lower_prolog.c` 36 (16 distinct — `IR_UNIFY`/`IR_CUT`/`IR_DISJ`/`IR_ITE`/etc.), `lower_raku.c` 33
   (20 distinct — `IR_GATHER`/`IR_MAP`/`IR_CASE`/`IR_FIELD_GET`/etc.), `lower_pascal.c` 7 (6 distinct —
   `IR_IF`/`IR_ASSIGN_FRAME`/etc.). One manual follow-up: the collapse turned a 12-way `case` list in
   `lower_snobol4.c`'s `is_pat_consumer()` into 12 duplicate `case IR_OP_COUNT:` labels (compile error);
   deduped to one.
2. Makefile: added compile rules for the four reals to the `scrip` recipe (mirrors the existing
   `lower_icon.c` rule exactly; their `.o`s land in `$(OBJ)`, picked up by the recipe's `$(OBJ)/*.o`
   wildcard link — no other linkage change needed). Removed the `lower_noicon_stubs.c` compile *rule*
   from the recipe (would otherwise multiply-define `lower_snobol4`/`lower_sno_stage2`/
   `lower_pascal_stage2`/`lower_pl_stage2`/`lower_raku_stage2` against the reals). Confirmed the four
   reals cover all 7 symbols the stub provided, including `pl_dyn_mark`/`pl_dyn_is_marked` (both defined
   in `lower_prolog.c`).
   **Deliberately left `lower_noicon_stubs.c` in `RT_PIC_SRCS`** (the separate `libscrip_rt.so` source
   list) — different link target, no symbol overlap with the recipe change, no reason to touch it for
   this ask. If the reals should be in the runtime lib too, that's a separate decision + separate build
   verification.
3. Full fresh `make scrip`: exit 0, `Built: scrip`, zero compile errors, zero undefined-reference /
   multiple-definition link errors.
4. Icon regression check: `SCRIP_ICN_BB=1 ./scrip --run|--compile` smoke on a trivial program — both
   modes still produce correct output. No Icon regression from the swap.

## What this is NOT
The four lowerers **compile and link now; they do not work.** Every opcode they used to build is
`IR_OP_COUNT` — no emitter case exists for it, so any real SNOBOL4/Prolog/Raku/Pascal program run through
this binary will produce degenerate sentinel IR, not correct code. This reverses the *linkage* side of the
Icon-only pivot (the stub-abort is gone) but not its *semantic* consequence (nothing behind SNOBOL4/
Prolog/Raku/Pascal actually works) — build-green placeholder, not restored functionality. Milestone 1
(`beauty.sno` byte-identical to SPITBOL) predates this and was achieved under a different, non-Icon-only
Makefile configuration; it says nothing about the current (collapsed) opcode set and should not be assumed
to still hold without re-running it, which was out of scope this session.

## Open items for next session
- **Codegen-regen scripts (RULES.md step 4) not yet run.** Touching `lower_snobol4.c` is a listed trigger
  for `util_regen_benchmark_s_artifacts.sh`/`util_regen_feature_s_artifacts.sh`/
  `util_regen_demo_s_artifacts.sh`. Blast radius quantified before deciding whether to run: 16 SNOBOL4
  files in `corpus/benchmarks/snobol4/`, 153 in `SCRIP/test/snobol4/`, up to 850 demo programs corpus-wide.
  Given every SNOBOL4 pattern/match opcode is now sentinel, running these would very likely commit
  widespread bombing/garbage `.s` as the "honest current" snapshot per RULES.md's own no-pinned-golden
  philosophy — sanctioned, but large and repo-crossing (writes into `corpus`, not `SCRIP`), so held for
  explicit go-ahead rather than run inside this handoff. **Needs a `<rung>` tag too, and this session's
  work isn't rung-numbered — pick one before running.**
- `lower_snobol4.c`'s old `IR_GOTO_DYN` dangling reference is now folded into the general `IR_OP_COUNT`
  collapse (171-token count above includes it) — the specific bug flagged earlier this session no longer
  exists as a distinct issue.
- Real reimplementation of all four lowerers against the current (collapsed) `IR.h` is the actual next
  step if SNOBOL4/Prolog/Raku/Pascal support is being resumed — this session only made them not break the
  build, nothing more.
- `GOAL-IR-IMMUTABLE-EMIT.md` was never opened this session (deliberately — nothing here was one of its
  rungs). Worth a look next session to check whether either action here bears on its open rungs.

## Verification commands (rerunnable)
```bash
grep -rn "\bIR_GOTO\b\|\bIR_INDIRECT_GOTO\b" src/               # expect: empty
gcc -fsyntax-only -w -Isrc -Isrc/contracts src/contracts/scrip_ir.c   # expect: exit 0
for f in lower_snobol4 lower_prolog lower_raku lower_pascal; do
  gcc -fsyntax-only -w -Isrc -Isrc/include -Isrc/contracts -Isrc/lower \
    -Isrc/machine -Isrc/emitter -Isrc/runtime/core -Isrc/runtime -DDYN_ENGINE_LINKED src/lower/$f.c
done                                                              # expect: all exit 0
make scrip                                                        # expect: exit 0, Built: scrip
SCRIP_ICN_BB=1 ./scrip --run <trivial.icn>                        # expect: correct output
```

## Push status
Local commits only at time of writing — push pending credential (public clone needs none; push does).
This section is a placeholder; the FACT RULE in `RULES.md` is explicit that "pending push" is a BLOCKED
handoff, not a complete one, and that only `scripts/handoff_status.sh`'s verbatim stdout may claim
`HANDOFF COMPLETE`. Not claiming it here.
