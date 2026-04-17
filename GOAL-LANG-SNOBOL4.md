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

## Current state (2026-04-17, one4all HEAD f4c8b833 — post Bug #1c + Bug #1d partial)

SN-1..SN-5 DONE. BEAUTY SELF-HOSTS (all 18 driver×mode combos).
SN-6 IN PROGRESS: PASS=218/228. treebank-array/list/claws5 spun to parallel goals.
Smoke PASS=7. Broker PASS=49.

**This session (GOAL-LANG-SNOBOL4 — Bug #1c fixed; Bug #1d partial):**

### Bug #1c (`(PAT . *fn())` stored wrong value in target cell) — FIXED

Root cause in `src/runtime/x86/snobol4_nmd.c`, `NAM_commit()`,
NAM_KIND_CALLCAP branch.

Semantic clarification first: `(PAT . *fn())` does NOT pass the matched
text to `fn` as a function argument. Instead, `*fn()` is invoked at
match-time and returns a NAME descriptor (`DT_N`) whose `.ptr` points at
the cell that should receive the matched substring — the `.` operator
then conditionally assigns PAT's matched text via that NAME (SNOBOL4
`$`-style indirection). The matched text is captured into the
NamEntry's `cc_substr`/`cc_slen` by `bb_callcap` (stmt_exec.c:612).

The bug: NAM_commit's callcap branch called the function to get the
target cell, then did `*cell = name_d` — storing the **NAME descriptor
itself** back into the cell instead of the matched text. The stale
`slen`/`s` union fields of that DT_N descriptor yielded a 1-byte
fragment (commonly `\t`) in every callcap target.

Fix: build a DT_S descriptor from `e->cc_substr` / `e->cc_slen` and
write that into the cell. Mirrors the already-correct `immediate`
(`$`) path in stmt_exec.c:605–607.

one4all commit: f9995d0b

### Bug #1d (absence of intra-match NAM rollback on backtrack) — PARTIAL

The NAM frame accumulates (.) captures and *fn() callcaps during a
pattern scan, all flushed in left-to-right order at NAM_commit. Before
this change there was no intra-match rollback: when a combinator
backtracked (e.g. bb_alt trying arm 2 after arm 1 failed), every (.)
entry the failed arm had appended survived into the next arm and
eventually fired at top-level NAM_commit.

Minimal repro: `expr = constant addop *expr | constant` against `2+3`.
Before: stk = [2,+,3,3]. After: stk = [2,+,3] (matches SPITBOL).

Fix landed (commit f4c8b833):
- `src/runtime/x86/snobol4.h` — prototypes for `NAM_mark` /
  `NAM_rollback_to`.
- `src/runtime/x86/snobol4_nmd.c` — both implemented. `NAM_mark()`
  returns the current frame tail as an opaque handle; `NAM_rollback_to
  (mark)` trims the list back to that mark (NULL mark → empty frame).
- `src/runtime/x86/bb_boxes.c` — `alt_t` gained `nam_mark`. bb_alt
  checkpoints on `ALT_α` and rolls back on `child_α_ω` so a failed
  arm's (.)/callcap entries do not leak into the next arm. β
  semantics unchanged.

Verification
- Minimal repro now correct (see above)
- `expr_eval.sno`: was 0/5 lines correct, now **4/5 correct**
  (9, 25.5, 7, 26). Remaining: `1+2*3 → 2` (should be 7).
- Smoke PASS=7, Broker PASS=49, SN-6 PASS=218/228 — no regressions
- Cross-pollinates to Icon, Prolog, Raku, Snocone, Rebus (all use bb_alt)

### Remaining `1+2*3 → 2` case — diagnosed, not yet fixed

Same absence-of-rollback pattern, but at the **bb_seq** level.

In outer `expr = *term addop *expr . *Binary() | *term`, matching
`1+2*3`: outer arm1's `*term` matches `1`; `addop` matches `+`;
`*expr` on `2*3` recurses. Inner `*expr`'s arm1 is `*term addop *expr
. *Binary()`. Its `*term` matches `2*3` fully (queueing pushes
[2,*,3] and an inner Binary callcap), but then the SEQ's next child
`addop` fails (no input left). bb_seq then calls `left.fn(...,β)` to
β-retry the left child (*term) — BUT the NAM entries left already
appended during its α (the [2,*,3, inner-Binary-cc] quartet) are not
rolled back, and any entries left's β attempt may add just stack on
top. Bad state then bubbles up to the outer NAM_commit walk.

At commit time, stk sees one extra entry between inner and outer
Binary, so inner Binary computes `(+ · 2 · 6)` instead of `(1 + 6)`,
EVAL parses as garbage, FAIL, top pop yields the leftover "2".

Fix strategy for bb_seq (NOT in this commit — β semantics need care):
- Add `void *pre_left_mark, *pre_right_mark` to `seq_t`.
- On `SEQ_α`: `pre_left_mark = NAM_mark()`.
- After `left_γ` (left just succeeded): `pre_right_mark = NAM_mark()`.
- On `right_ω` before calling `left.β`: `NAM_rollback_to
  (pre_right_mark)` — drop right's attempted entries; keep left's α
  entries while its β is attempted (they are valid up to the moment
  of β). On left.β success, new left_γ runs and pre_right_mark will
  be reset before right.α — so left's α entries that will be
  superseded by the β result need to go too. Cleanest: on `right_ω`
  rollback to `pre_left_mark` (drop both left-α and right-α entries)
  before calling `left.β`. Validate no regression in C5 sessions, as
  this is the hottest pattern primitive.
- On `left_ω` / `SEQ_ω`: parent box handles the outer rollback (bb_alt
  already does). If bb_seq is the top box, the statement-level
  NAM_discard covers it.

### Files touched this session

- `src/runtime/x86/snobol4_nmd.c` — NAM_commit NAM_KIND_CALLCAP fix
  (Bug #1c) and new `NAM_mark`/`NAM_rollback_to` helpers.
- `src/runtime/x86/snobol4.h` — prototypes for the new helpers.
- `src/runtime/x86/bb_boxes.c` — `bb_alt` takes a NAM checkpoint and
  rolls back on arm failure.

### Prior in-ladder fixes (context — landed before this session)

Two `--ir-run` fixes in `src/driver/interp.c`:
1. E_SEQ/E_CAT stale-acc on mode switch (pat_cat dropped DT=11)
2. E_ALT value-ctx: use `interp_eval_pat` for all alt arms

### Next session (GOAL-LANG-SNOBOL4)

1. Finish Bug #1d by extending NAM rollback into `bb_seq` (strategy
   above). Minimal repro: `1+2*3` against full `expr_eval.sno`
   expected `7` scrip gives `2`. After this fix, expect expr_eval
   5/5 and SN-6 PASS=219/228.
2. Audit other backtracking boxes — `bb_arbno`, `bb_pos_alt`,
   `bb_deferred_var` — for the same rollback gap. Each should take
   a mark on α and roll back when its α-trial fails (parent may also
   roll back, but local rollback is the clean pattern).
3. SM-run `SIZE(INPUT)` EOF hang (fileinfo, word1, triplet, wordcount).
   `CHARS = CHARS + SIZE(INPUT) :F(DONE)` — EOF failure branch not
   propagated in SM-run. Investigate sm_lower.c keyword/arg lowering
   + failure threading.
4. Investigate beauty_XDump driver.
5. Add missing wordcount.sno and roman.sno to
   corpus/programs/snobol4/demo/.

### Remaining SN-6 failures (10 — count unchanged; expr_eval now 4/5)

- fileinfo, word1: SM INPUT-as-arg EOF hang
- triplet: SM truncated output (same root)
- wordcount: SM wrong count + format
- expr_eval: Bug #1d remainder — bb_seq rollback missing (4/5 of
  input now passes; only `1+2*3` still wrong)
- beauty_XDump_driver: unknown
- demo_wordcount, demo_roman: .sno source MISSING
- demo_treebank: *group self-ref (pre-existing)
- demo_claws5: tracked in GOAL-SNO-CLAWS5.md
