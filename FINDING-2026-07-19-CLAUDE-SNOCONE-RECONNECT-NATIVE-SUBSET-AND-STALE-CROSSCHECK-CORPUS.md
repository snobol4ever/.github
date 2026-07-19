# FINDING 2026-07-19 (Claude Opus 4.8) — Snocone reconnect: the native subset boundary is the frontier, and the on-disk crosscheck corpus had rotted to pre-language-tightening syntax

**Context.** Session re-plugged into Snocone after a long gap ("entirely new world"). Everything below is MEASURED from a clean build of HEAD (SCRIP `762aafc5`), not read from prose. The April-2026 `GOAL-SNOCONE-IR-BB.md` is fully superseded: its whole premise (a mode-2 IR-graph *interpreter* runs the beauty subsystems) is gone, because modes 1/2 are deleted. Snocone now lives entirely on the native Byrd-Box path — mode-3 `--run` (flat-wired x86 BB blobs in a sealed slab) and mode-4 `--compile` (standalone x86-64 asm). Snocone shares `lower_snobol4` with SNOBOL4.

## Ground truth (built from HEAD)
- `make scrip` builds clean; needs no flex/bison (generated `.tab.{c,h}`/`.lex.c` are checked in), no libgc (`-lm -lpthread` only). `nasm` is needed ONLY by the mode-4 assemble/link harness, not by the compiler build.
- **Snocone smoke `test_smoke_snocone.sh`: 5/5 PASS** — scalar assign, arithmetic, `function`, `if/else`, `while` all lower to native code and run.
- **The native lowering covers a SUBSET (SCO-CF-2 / GZ#5).** It handles scalar `TT_VAR = expr`, arithmetic, and structured control flow. Everything outside emits a LOUD `FATAL lower_snobol4 (GZ#5 subset)` by design (never a silent wrong answer). Measured constructs OUTSIDE the landed subset:
  - **Pattern match** `subject ? pattern` — expression tree kind 48. (`IR_MATCH_*` family pending.)
  - **Indirect / computed-target assignment LHS** — `$'x' = e`, `$v = e`. The guard message: "TT_ASSIGN lhs form outside the SCO-CF-2 subset (TT_VAR only)."
  - **Alt-eval `E_VLIST`** — `(e1, e2, ...)` in value position — expression tree kind 22.
  - EVAL of a pure-arithmetic string (`EVAL("2 + 3")`) already works; the FATAL banner lists EVAL/CODE as pending for the general (pattern) case.
- **Mode-3 / mode-4 parity confirmed** on the crosscheck corpus: mode-4 `--compile` codegen = 17 clean / 3 subset-FATAL, matching mode-3 `--run` = 17 PASS-vs-oracle / 3 XFAIL. The subset boundary is mode-independent (it is in the shared lowering), as expected.

## The real regression-floor bug: `corpus/crosscheck/snocone` had rotted (fixed this session)
The 20-file on-disk corpus was authored before the language tightened. 19 of 20 files used **`#` as a comment prefix** (in current Snocone `#` is an undefined-OPSYN *binary operator*, priority 7 — NOT a comment; comments are `//` and `/* */`) and **omitted the trailing `;`** (now a hard statement terminator — a newline is whitespace, not a terminator). So "16-of-20 FAIL" was pure syntax rot, not a code regression. It rotted unnoticed because the maintainers' live gates (`test_smoke_snocone.sh`, the inline heredocs in `test_crosscheck_snocone.sh`) use correct syntax and never touch these on-disk files.

**Fix applied:** migrated the 19 files (`#`→`//`, added `;` terminators; no inline `#`, no col-1 continuations, so the transform was safe and idempotent on the one already-modern file `hello_literals.sc`). Result mode-3 `--run` vs oracle: **4 → 17 PASS**. The remaining 3 are genuine frontier gaps, now marked `.xfail` with reasons (the sc-corpus-rung harness honors `.xfail`):
- `assign_014_assign_indirect_dollar.xfail` — indirect-assign LHS `$'x' = e`
- `assign_015_assign_indirect_var.xfail` — indirect-assign LHS `$v = e`
- `hello_literals.xfail` — alt-eval `E_VLIST` `('', '')`

## Secondary stale artifacts found (so the next session does not trip on them)
1. **`scripts/test_crosscheck_sc_corpus_rung.sh` uses DEAD CLI flags.** It invokes `scrip -sc -x86`; the current driver has no `-sc` (it reads `-sc` as a filename → `cannot open '-sc'`). Current mode-4 is `scrip --compile FILE` (asm to stdout, links `libscrip_rt.so`). It also computes `TINY="$SCRIPT_DIR/../.."` — correct only if the script lives at `test/crosscheck/` (per its own header) but the copy in `scripts/` overshoots the repo root by one level. (Worked around this session with symlinks at the overshot root purely to reach the nasm stage; the flag rot is the blocker, not the path.)
2. **`test_beauty_snocone_all_modes.sh` / the `beauty_*` cases in `test_crosscheck_snocone.sh` FATAL wholesale** (0/42/3): they exercise the beauty subsystems (tree, arith-with-helpers, trace, match, strings, ShiftReduce…), which are pattern-matching-heavy and therefore land squarely on the native frontier above. These are interpreter-era expectations; they cannot pass until the `IR_MATCH_*` ladder lands. Empty output = the FATAL going to stderr while stdout is silent (parse/lower refusal), not a hang.
3. **`GOAL-SNOCONE-IR-BB.md` is archaeology** — delete/retire when convenient; its `stmt_exec`/`execute_program` IR-interpreter path no longer exists.

## Where "full Snocone" (Path B) starts
Extend the `lower_snobol4` native subset, in this order of leverage:
1. **Indirect / computed-target assignment LHS** (`$name = e`) — smallest, unblocks 2 corpus files immediately and is a prerequisite shape for pattern capture targets.
2. **Alt-eval `E_VLIST`** (`(e1, e2, …)`) — eager left-to-right short-circuit; unblocks `hello_literals` and is pervasive in the parser library.
3. **`IR_MATCH_*` family** (`subject ? pattern`, then `? pattern = repl`) — the big one; unblocks every beauty subsystem. This is the GZ#5 ladder in `GOAL-IR-IMMUTABLE-EMIT.md` / `GOAL-SNOBOL4-BB.md`; the RULES.md BB-CODEGEN design-set reading + monitor-first bug-finding apply before any codegen edit.

## Files touched this session
- `corpus/crosscheck/snocone/*.sc` — 19 migrated to current syntax.
- `corpus/crosscheck/snocone/{assign_014_assign_indirect_dollar,assign_015_assign_indirect_var,hello_literals}.xfail` — new markers.
- this FINDING.

No source (`src/`) changes; the compiler was not modified.
