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

## Current state (2026-04-17, one4all HEAD f9995d0b — post Bug #1c fix)

SN-1..SN-5 DONE. BEAUTY SELF-HOSTS (all 18 driver×mode combos).
SN-6 IN PROGRESS: PASS=218/228. treebank-array/list/claws5 spun to parallel goals.
Smoke PASS=7. Broker PASS=49.

**This session (GOAL-LANG-SNOBOL4 — Bug #1c fixed; Bug #1d localized):**

### Bug #1c (`(PAT . *fn())` stored wrong value in target cell) — FIXED

Root cause located in `src/runtime/x86/snobol4_nmd.c`, `NAM_commit()`,
NAM_KIND_CALLCAP branch (previously lines 270–273).

The prior session's framing was slightly off: `(PAT . *fn())` does NOT pass
the matched text to `fn` as a function argument. Instead, `*fn()` is invoked
at match-time and returns a NAME descriptor (`DT_N`) whose `.ptr` points at
the cell that should receive the matched substring — the `.` operator then
conditionally assigns PAT's matched text via that NAME (SNOBOL4 `$`-style
indirection). The matched text was already captured correctly into the
NamEntry's `cc_substr`/`cc_slen` by `bb_callcap` (stmt_exec.c:612).

The bug: NAM_commit's callcap branch called the function to get the target
cell, then did `*cell = name_d` — storing the **NAME descriptor itself**
back into the cell instead of the matched text. The stale `slen`/`s` union
fields of that DT_N descriptor yielded a 1-byte fragment (commonly `\t`)
in every callcap target.

Fix: build a DT_S descriptor from `e->cc_substr` / `e->cc_slen` and write
that into the cell. Mirrors the already-correct `immediate` ($) path in
stmt_exec.c:605–607.

Verification:
- Minimal repro (one `constant = integer . *Push()` on `"12"`):
  before — `stk[1]="^I"` SIZE=1; after — `stk[1]="12"` SIZE=2 (matches SPITBOL)
- Three-push probe on `2+3`: all three pushes fire left-to-right with correct
  values (`"2"`, `"+"`, `"3"`) — byte-perfect against SPITBOL
- Smoke PASS=7, Broker PASS=49, SN-6 PASS=218/228 — no regressions

### Bug #1d (expr_eval top-level `*expr` / `*Binary()` handling) — localized, unfixed

Post-Bug-#1c, `expr_eval.sno` on input `2+3` now prints `PATTERN` instead of
the expected `5`. Pushes are verified correct in isolation, so the failure
is downstream — in either the top-level `expr` alternation (`*term addop
*expr . *Binary() | *term`) or in how `Binary` consumes the stack when
called via `. *Binary()`. The `"PATTERN"` output means `Pop()` is returning
a DT_P at least once, which is then fed to `EVAL(left ' ' op ' ' right)`
and round-trips to the literal string "PATTERN".

Hypothesis to test first: the forward-reference `*expr` inside `expr` (direct
recursion through an alt arm) is constructing a DT_P at pattern-build time
and that pattern value is leaking onto the stack as if it were the matched
text. Related to the same E_ALT / *varref value-ctx area touched earlier
this ladder.

### Prior in-ladder fixes (context)

Two earlier `--ir-run` fixes in `src/driver/interp.c` landed ahead of this
session (unchanged):
1. E_SEQ/E_CAT stale-acc on mode switch (pat_cat dropped DT=11)
2. E_ALT value-ctx: use `interp_eval_pat` for all alt arms

### Files touched this session

- `src/runtime/x86/snobol4_nmd.c` — NAM_commit NAM_KIND_CALLCAP branch
  now writes matched text (DT_S) into the target cell rather than the NAME
  descriptor.

### Next session (GOAL-LANG-SNOBOL4)

1. Diagnose Bug #1d. First reduce `expr_eval.sno` to the smallest input
   producing `PATTERN` output (already reduced to `2+3`). Instrument
   `Pop()` in-source to print `DATATYPE` of each value popped — identifies
   which push leaked a DT_P. Then walk back to the pattern construction:
   likely `src/driver/interp.c` `interp_eval_pat` on the `expr` alt
   containing `*expr`, or `bb_build` of `addop *expr . *Binary()`.
2. After Bug #1d fixes expr_eval: re-run full corpus, expect PASS=219/228.
3. SM-run `SIZE(INPUT)` EOF hang (fileinfo, word1, triplet, wordcount).
   `CHARS = CHARS + SIZE(INPUT) :F(DONE)` — EOF failure branch not
   propagated in SM-run. Investigate sm_lower.c keyword/arg lowering +
   failure threading.
4. Investigate beauty_XDump driver.
5. Add missing wordcount.sno and roman.sno to corpus/programs/snobol4/demo/.

### Remaining SN-6 failures (10 — unchanged count, expr_eval root-caused shift)

- fileinfo, word1: SM INPUT-as-arg EOF hang
- triplet: SM truncated output (same root)
- wordcount: SM wrong count + format
- expr_eval: Bug #1d — `*expr`/`*Binary()` leaks DT_P onto pattern stack
- beauty_XDump_driver: unknown
- demo_wordcount, demo_roman: .sno source MISSING
- demo_treebank: *group self-ref (pre-existing)
- demo_claws5: tracked in GOAL-SNO-CLAWS5.md
