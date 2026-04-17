# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=47
```

---

## Architecture reminder

```
.sno → sno_parse() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()   tree-walk
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol

⛔ Step 1 (`scrip-monitor --monitor`) runs EVERY iteration, unconditionally.
⛔ Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 — ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 — only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 — only if Step 1 shows problem: OUTPUT probe → fix → rebuild → repeat
# Rebuild: make scrip && make scrip-monitor CSN_A=...
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

---

## Rung ladder

### Phase 1 — IR-run  ✅ DONE (SN-1..SN-5)
### Phase 2 — SM-run  (SN-7..SN-9, gated on SN-6)
### Phase 3 — JIT-run (SN-10..SN-12, gated on SN-9)

- [x] **SN-1** — beauty omega driver all three modes. DONE.
- [x] **SN-2** — beauty gen driver all three modes. DONE.
- [x] **SN-3** — beauty tdump driver all three modes. DONE.
- [x] **SN-4** — beauty alpha/beta/gamma drivers all three modes. DONE.
- [x] **SN-5** — beauty.sno self-hosts; all 18 driver×mode combos PASS. DONE.
- [ ] **SN-6** — Full corpus: run test_interp_broad_corpus_and_beauty.sh. IN PROGRESS: PASS=215/228.

```bash
bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
```

- [x] **SN-14** — Pattern primitives as typed EKind nodes. DONE.
- [x] **SN-15** — Verify all three modes still pass after SN-14. DONE.

*(treebank-array, treebank-list, claws5 promoted to independent parallel goals:
GOAL-SNO-TREEBANK-ARRAY.md, GOAL-SNO-TREEBANK-LIST.md, GOAL-SNO-CLAWS5.md)*

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/snobol4.y` | Bison grammar |
| `src/frontend/snobol4/snobol4.l` | Flex lexer |
| `src/driver/interp.c` | --ir-run tree-walk |
| `src/runtime/x86/sm_lower.c` | IR → SM |
| `src/runtime/x86/sm_interp.c` | SM interpreter |
| `src/runtime/x86/sm_codegen.c` | x86 JIT |
| `src/runtime/x86/bb_boxes.c` | SNOBOL4 pattern boxes |
| `src/runtime/x86/snobol4_pattern.c` | subscript, OPSYN, array helpers |
| `src/runtime/x86/snobol4.c` | ARRAY/TABLE/CONVERT builtins, array_get/set |
| `corpus/programs/snobol4/beauty/` | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=47 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-17, one4all HEAD — post-IR-eval-pat-ctx fixes)

SN-1..SN-5 DONE. BEAUTY SELF-HOSTS (all 18 driver×mode combos).
SN-6 IN PROGRESS: PASS=218/228. treebank-array/list/claws5 spun to parallel goals.
Smoke PASS=7. Broker PASS=49.

**This session (GOAL-LANG-SNOBOL4 — expr_eval.sno drill-down):**

Focus: `test/snobol4/control/expr_eval.sno` — a recursive-descent arithmetic
calculator built entirely from SNOBOL4 patterns with `*fn()` side-effects.
SPITBOL oracle confirmed: `1+2*3→7, (1+2)*3→9, 2.5e1+0.5→25.5, -3+10→7, 4*5+6→26`.

Landed two `--ir-run` fixes in `src/driver/interp.c`:

1. **E_SEQ/E_CAT stale-acc on mode switch.** In the value-ctx handler, when
   a pattern operand arrives mid-concat, the code re-evaluated the current
   child in pat ctx but left the accumulator pointing at frozen DT_E values
   from prior children. In `expr = *term integer`, `*term` produced
   DT_E(E_VAR) via interp_eval's value-ctx E_DEFER path, then when `integer`
   (DT_P) arrived, `pat_cat(acc, nxt)` hit DT_E with a ptr that had been
   flattened to NULL during descriptor copy — emitting
   `pat_cat: left is not a pattern (DT=11) — dropping` and silently
   producing wrong patterns. Fix: on mode switch, re-accumulate
   children[0..i-1] via `interp_eval_pat` before continuing.

2. **E_ALT value-ctx.** E_ALT used `interp_eval` on arms, so `*term` alone
   on an alt arm became DT_E → silently coerced by `var_as_pattern` to
   `pat_lit("term")` (a literal 4-char match for the word "term"). Fix:
   use `interp_eval_pat` for all arms — pattern alternation is inherently
   a pattern op.

Gates post-fix: Smoke PASS=7, Broker PASS=49. No regressions.

**SN-6 remaining `expr_eval` failure is now a different bug (Bug #1c).**
Isolated minimal: `constant = integer . *Push()` matching `"12"` calls
`Push` with `\t` (a tab character) instead of `"12"`. SPITBOL calls Push
with `"12"` correctly. This is the `XCALLCAP+RPOS(0)` cursor-threading
issue already flagged in prior session notes.

**Next session (GOAL-LANG-SNOBOL4):**
1. Fix XCALLCAP matched-text capture for `. *fn()` — look at
   `stmt_exec.c:942` (XCALLCAP match-time handler). The matched substring
   is not being passed as the function argument; a cursor/offset byte (tab)
   is reaching the function instead.
2. Re-run `expr_eval.sno` full input; expect `7 / 9 / 25.5 / 7 / 26`.
3. Fix SM-run SIZE(INPUT) EOF hang — affects fileinfo, word1, triplet, wordcount.
   `CHARS = CHARS + SIZE(INPUT) :F(DONE)` — EOF failure branch not propagated in SM-run.
   Investigate sm_lower.c keyword/arg lowering + failure threading.
4. Investigate beauty_XDump driver.
5. Add missing wordcount.sno and roman.sno to corpus/programs/snobol4/demo/.

**Remaining SN-6 failures (10):**
- fileinfo, word1: SM INPUT-as-arg EOF hang
- triplet: SM truncated output (same root)
- wordcount: SM wrong count + format
- expr_eval: XCALLCAP passes wrong matched text (Bug #1c — narrowed this session)
- beauty_XDump_driver: unknown
- demo_wordcount, demo_roman: .sno source MISSING
- demo_treebank: *group self-ref (pre-existing)
- demo_claws5: tracked in GOAL-SNO-CLAWS5.md
