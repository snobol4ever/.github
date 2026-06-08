# HANDOFF 2026-06-08 OPUS48 — IR-REDESIGN: IRD-4b sub-task 1 (t→op rename)

**State:** SCRIP `aae8686` (the substantive t→op rename) — SCRIP origin/main has since advanced to
`cd52558` (concurrent BB-FIXUP audit-counter hardening *for* this rename; NOT an IR change, sits on
top of mine). `.github` origin = this commit. Both trees CLEAN, pushed. Canonical state lives in the
GOAL-IR-REDESIGN.md watermark (single source of truth); this file is the session narrative.

## What landed — `aae8686` (one commit, fully gated)

IRD-4b **sub-task 1**: the IR_t kind field renamed `IR_e t` → `IR_e op`, behavior-preserving, across
every consumer that reads or writes it:
- `contracts/IR.h` — the struct field itself.
- Pure IR consumers (quote/comment-aware whole-file pass): `interp/IR_interp.c`, all `emitter/**`
  (`BB_templates/*.cpp`, `emit_bb.c`, `emit_core.c`), `contracts/scrip_ir.c` (allocator sets the
  kind at one site + the graph dumper).
- AST→IR producers, IR-side accesses only (line-targeted): `lower/lower_program.c`,
  `lower/lower_value.c`, `driver/scrip.c` (the pl_gz synth region), `parser/raku/raku_nfa_bb.c`.
- `runtime/unification.c` (one `nd->op` in the term builder).
- The **separately-compiled harnesses** `tools/prove_lower.c` (8 sites) + `tools/emit_per_kind_audit.c`
  (3 `->t` + 3 `.t`). ⚠ These are NOT built by `make`/`make libscrip_rt` — only by their own scripts.
  The main build did not flag them; the **gate** (prove_lower) did. Any future IR_t field change MUST
  remember these two.

**`tree_t` (AST) `->t` was deliberately left untouched** (lower/ keeps 198, scrip.c keeps 1).
Disambiguation method: rename the struct field, then let the compiler flag every broken access — it
flags ONLY IR_t accesses, never tree_t or string literals. For the mixed files (scrip.c,
lower_program.c) the fix was line-targeted with a verified invariant: on every edited line, the
textual `->t` count equalled the compiler-flagged count, proving no line mixed IR_t and tree_t (the
single scrip.c `tree_t->t` line and one lower_value mixed case were correctly excluded). Helper
scripts used: `/tmp/rename_t_to_op.py` (quote/comment-aware whole-file) and `/tmp/fix_lines.py`
(line-targeted) — both ephemeral, trivially reconstructable.

## Gate — PASSED

Clean rebuild of both targets, 0 errors. `grep '->t' == 0` in the pure consumers
(interp/emitter/scrip_ir). All 5 interp sweeps (sno153/icn9/pl8/sco191/pas5) + 5 smokes
byte-identical (wall-clock lines ignored; raku+rebus are pre-existing FAIL). prove_lower **PASS=68
rc=0** byte-identical (col-7 ptr-masked). Changeset = clean **761/761** insertions/deletions, 35
files — a pure rename, no logic drift. **IR_t is now `{op, γ, ω, operands, n_operands, idx, own}`.**

## NEXT — IRD-4b sub-task 2: γ/ω CARRIER FLIP (do FRESH + ATOMIC)

⚠ **No safe partial.** Changing the γ/ω field type breaks every deref at once, so it is
all-or-nothing through to a green build + byte-identical gate + commit. Do NOT start near a context
limit.

1. Change `IR_t.γ`/`IR_t.ω` from `IR_t*` to `IR_ref_t{node, sz[4]}`.
2. Interp/emitter follow `ref.node` and dispatch on `ref.sz[1]` (0xB1=`α` fresh / 0xB2=`β` resume).
3. `iref()` carrier helper already exists — update it.
4. **DO NOT change γ/ω semantics.** Every current target is fresh-entry, so set `sz="α"` UNIFORMLY
   first (behavior-preserving). β-targeting wires (conjunction right-ω→left-β, body→expr-β, etc. per
   JCON `irgen.icn`) are a SEPARATE later semantic step.

Then **IRD-5**: sizeof fence already 64→48 (member count 7, target met); ADD an IR_t struct-shape
section to `ARCH-IR.md` — best done AFTER the carrier flip so γ/ω's type is documented correctly
(ARCH-IR.md currently documents only tree_t/AST + the SM/broker model and the conceptual four PORTS).

## Notes for the next session

- **Cold start:** `apt-get install -y libgc-dev`; clone SCRIP latest main; `make && make
  libscrip_rt && bash scripts/bake_ird3_baseline.sh <outdir>` to re-establish the baseline (the
  `/tmp` ones do not survive a new container). Gate = the PASS criteria above.
- `bash_tool` runs `/bin/sh` (dash) — wrap process substitution in `bash -c`. Mask prove_lower col-7
  with `awk '{if(NF>=7)$7="PTR";print}'`.
- **COORDINATE with BB-FIXUP** — `emit_bb.c` is shared. The pre-push GUARD (assert
  `origin/main == HEAD~1`, else rebase, never `--force`) held this session: rebased cleanly onto
  concurrent FIXUP commits `793a613`/`ed50f54`/`97b5f5e` (disjoint files; their `bb_fail.cpp` has
  zero IR_t refs), and `cd52558` then landed on top of the rename. Push code repos first, `.github`
  last.
- **`src/parser/icon/icon_lex_test.c` is DEAD/unbuilt and already-broken independent of this work** —
  its 37 "member t" errors are about `IcnToken`, not `IR_t`. Out of scope; latent cleanup only.
