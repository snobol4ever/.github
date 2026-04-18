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

- [ ] **SN-7** — beauty.sno self-host bootstrap: make beauty.sno parse and
  pretty-print itself correctly for the FIRST TIME under scrip --ir-run.
  This has never passed. Run beauty_${DRIVER}_driver.sno for all 6 drivers,
  diff each against SPITBOL oracle, drive to diff=0 for all 18 combos.
  Mirror of GOAL-NET-BEAUTY-SELF.md S-2 but for one4all x86 --ir-run.
  Gate: smoke PASS=7, broker PASS=49, all 18 beauty self-host combos diff=0.

```bash
bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
```

- [ ] **SN-19** — **Case folding belongs in the lexer, not the runtime.** Pivot.

  **Problem.** SNOBOL4's default mode is case-insensitive; case-sensitive is opt-in
  (CSNOBOL4 `-f`). The correct architecture is: in case-insensitive mode the lexer
  folds every identifier-ish token (variable names, function names, labels, keyword
  names) to a single canonical case (uppercase by convention) before it enters the
  token stream. Downstream — parser, IR, SM_Program, every runtime dispatch — sees
  only the canonical form and uses plain `strcmp`. In case-sensitive mode the lexer
  preserves spelling.

  **Current state is wrong.** The codebase carries mixed-case identifiers all the
  way through to runtime dispatch, and then every lookup site does its own
  `strcasecmp` / `toupper` band-aid. This is how the `differ(3+2,5)` vs `DIFFER(3+2,5)`
  divergence — working under `--ir-run`, failing under `--sm-run` with "Error 5:
  Undefined function or operation" — exists in the first place. Two dispatch paths,
  each doing (or forgetting to do) its own case normalization independently, will
  eventually disagree. The SN-18 broad-suite regression (218 → 172) is a symptom
  of this, not a bug in the bb_usercall ABI fix. Bisecting the three-file diff is
  the wrong response — the real fix is upstream.

  **Supersedes SN-18 bisect.** Do not bisect the SN-18 commit. Keep the SN-18 ABI fix
  (bb_usercall spec_t→DESCR_t) — that work is correct and restores 83% Porter
  accuracy. Fix SN-19 at the source, and expect the SN-18 regression to dissolve
  along with a long tail of other latent case-sensitivity bugs.

  **Plan:**
  1. Audit `src/frontend/snobol4/snobol4.l` — does it already have a fold branch?
     If yes, is it consistently applied to every identifier-emitting rule? If no,
     add `yytext` uppercase-fold for identifier tokens before building the token value.
  2. Confirm/add a scrip CLI flag for case-sensitive mode (mirror of CSNOBOL4 `-f`).
     Default = fold-to-upper (case-insensitive). Flag-on = preserve.
  3. Audit every runtime site that does `strcasecmp` or runtime `toupper` on
     identifier names — `snobol4.c` (APPLY_fn, _func_hash, fn_has_builtin, _ARG_
     and others), `stmt_exec.c`, `sm_interp.c` `INVOKE_fn`, `interp.c` E_FNC
     dispatch, label_lookup in `snobol4.c`. With folding done at lex time, these
     must become plain `strcmp` / plain hash. Every removed `toupper` is one more
     place the bug can never recur.
  4. The `.sno` source in corpus has mixed-case identifiers (per SPITBOL convention
     a program can write `Push()` and `push()` interchangeably in default mode).
     That convention continues to work because the lexer is folding; no corpus
     changes.
  5. Regenerate parser/lexer via
     `bash scripts/regenerate_parser_and_lexer_from_sources.sh` after any `.l` edit.
     Commit `.l` source AND generated files together (per RULES.md).
  6. Gate: smoke PASS=7, broker PASS=49, SN-6 broad suite back to 218+/228,
     Porter --ir-run stays at 83.46%, Porter --sm-run improves (no longer
     handicapped by bifurcated case handling), the minimal `differ(3+2,5)`
     repro passes under all modes.
  7. Case-sensitive mode validation: the double-function trick in RULES.md
     (`push_list` vs `Push_list`) must still work under the case-sensitive flag.
     Run a targeted test that uses the trick; it must behave correctly.

  **Key files to read first:**
  - `src/frontend/snobol4/snobol4.l` — lexer, the place to fix
  - `src/frontend/snobol4/snobol4.y` — confirm token value plumbing
  - `src/runtime/x86/snobol4.c` `_func_hash` / `APPLY_fn` / `fn_has_builtin`
  - `src/runtime/x86/sm_interp.c` `INVOKE_fn` call at SM_CALL
  - `src/driver/interp.c` E_FNC / E_VAR resolution

  **Minimal repro (must pass all three modes after the fix):**
  ```snobol4
                 &ANCHOR   = 0
                 &FULLSCAN = 1
                 differ(3 + 2, 5)   :F(NEQ)
                 OUTPUT    = 'equal'  :(END)
  NEQ            OUTPUT    = 'differ'
  END
  ```
  Expected output: `differ` under `--ir-run`, `--sm-run`, and `--jit-run`. Currently
  `--sm-run` emits `** Error 5 in statement 3 / Undefined function or operation`
  before the output because the lowercase `differ` reaches SM_CALL verbatim.

- [x] **SN-14** — Pattern primitives as typed EKind nodes. DONE.
- [x] **SN-15** — Verify all three modes still pass after SN-14. DONE.
- [x] **SN-16** — Porter (1980) stemmer demo (`corpus/programs/snobol4/demo/porter.sno`).
  Faithful translation of the CSCE-5200 Project 1 Python snobol4python PATTERN form; 95%+
  line-for-line correspondence. Oracle: tartarus.org/martin/PorterStemmer voc.txt + output.txt.
  Gate under SPITBOL: 23,531/23,531 = 100.0000% accuracy. DONE.

```bash
/home/claude/x64/bin/sbl -b /home/claude/corpus/programs/snobol4/demo/porter.sno \
    < /home/claude/corpus/programs/snobol4/demo/porter.input \
  | diff - /home/claude/corpus/programs/snobol4/demo/porter.ref | head
```

- [ ] **SN-17** — Porter stemmer under one4all — close the SPITBOL gap.

  **Current state (measured this session on one4all HEAD 770172e4):**

  | Mode             | Matches tartarus oracle | Accuracy |
  |------------------|-------------------------|----------|
  | SPITBOL `-b`     | 23,531 / 23,531         | 100.0000% |
  | one4all `--ir-run` | 12,796 / 23,531       |  54.38%   |
  | one4all `--sm-run` | 12,796 / 23,531       |  54.38%   |
  | one4all `--jit-run`| 12,796 / 23,531 *     |  54.38%   |

  `* --jit-run` additionally emits `sm_codegen: unimplemented opcode 11 (SM_PUSH_EXPR)`
  at sm-pc 997 and 1698 — known SN-10..SN-12 gap, not on this step's critical path.

  `--ir-run` and `--sm-run` produce byte-identical output to each other (`diff = 0`).

  **Symptom:** Only step 1a (plural stripping via `(epsilon . *s_empty())` and friends)
  appears to fire. Steps 1b, 1c, 2, 3, 4, 5a, 5b — all of which require a guard like
  `*g_m_gt_0()` preceding the commit-time action — silently do nothing. Example:

  ```
  input       tartarus   one4all
  abandoned   abandon    abandoned
  abate       abat       abate
  abbey       abbei      abbey          (step 1c: y->i fails to fire)
  ```

  **Root cause (already diagnosed in SN-6 Bug #1d):** one4all invokes `*fn()` at
  match-time; SPITBOL defers to commit-time (manual p.133–134). The Porter rules
  use the idiom `RTAB(n) $ stem 'suf' *guard() (epsilon . *action())` throughout.
  When the guard evaluates at match-time, the stem immediate-assignment `$` has
  fired, but on arms that later lose to another alt arm or fail outright, the
  `$` side effect leaks. More critically, the `(epsilon . *action())` never fires
  to set `target`, so the pipeline sees `target = 'UNSET'` and leaves the token
  alone — silent no-op.

  **Fix plan:** Resolve SN-6 Bug #1d (commit-time `*fn()` dispatch in NAM_commit,
  per GOAL-LANG-SNOBOL4 "Remaining 1+2*3 → 2 case" fix strategy). Expected
  outcome: porter accuracy under --ir-run and --sm-run jumps to match SPITBOL's
  100%. If any gap remains, bisect on the failing words (they will cluster by
  which Porter step the failing rule belongs to, which isolates the exact
  primitive still misbehaving).

  **Gate:**
  ```bash
  cd /home/claude/corpus/programs/snobol4/demo
  /home/claude/one4all/scrip --ir-run porter.sno < porter.input \
    | diff - porter.ref | wc -l            # expect 0
  /home/claude/one4all/scrip --sm-run porter.sno < porter.input \
    | diff - porter.ref | wc -l            # expect 0
  ```

  Expected numerics after fix: 23,531 / 23,531 under --ir-run and --sm-run.


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

## Current state (2026-04-18 — SN-19 session 5, architectural fix landed)

**HEAD:** one4all next-commit after `12b63f6f` (SN-19 session 4 landed);
session 5 resolves the `data_field_ptr` regression architecturally.

**Gates after this session:**
- Smoke PASS=7, broker PASS=49 — both green
- Broad suite **218/227** — held steady
- `differ(3+2,5)` minimal repro **PASSES all three modes**
- `data_field_ptr` now plain `strcmp` — no remaining `strcasecmp` on the
  DATA field-lookup hot path

### SN-19 — principle (sharpened this session)

Case folding is a **frontend concern**, not a shared-runtime concern. Each
language owns its own case policy:

| Frontend | Case policy | Where enforced |
|----------|-------------|----------------|
| SNOBOL4  | Default fold-to-upper (CSNOBOL4 `-f` reserved for future) | Lexer `snobol4.l` via `sno_fold_name`; SNOBOL4-originated runtime ingest (`_builtin_DATA`, `_DATA_`) pre-folds spec before calling shared runtime |
| Icon     | Case-sensitive | Verbatim — no folding anywhere |
| Raku     | Case-sensitive | Verbatim — no folding anywhere |

Shared runtime (`DEFDAT_fn`, `sc_dat_register`, `data_field_ptr`,
`DATCON_fn`, name-table ops) is **case-policy-neutral**: stores names
verbatim, compares with plain `strcmp`. Within a single language the ingest
side and the lookup side use the same case convention by construction, so
`strcmp` is correct for all three.

The earlier "fold in `DEFDAT_fn`" approach (session 3) was wrong — it
imposed SNOBOL4's fold-to-upper on Icon and Raku records, which only kept
working because `data_field_ptr` used `strcasecmp` as a safety net. Removing
that net exposed the architectural conflict (rk_class26 regression).

### SN-19 — session 5 additions

**Architectural correction (snobol4.c + interp.c):**

 32. `DEFDAT_fn` (snobol4.c ~2018) — reverted session-3 `sno_fold_name` on
     both typename (line 2032) and field name (line 2051). Now case-policy-
     neutral: stores names exactly as given. Comment documents the invariant.
 33. `sc_dat_register` (interp.c ~4644) — also case-policy-neutral (never
     had a fold before session 5's experiment; the experiment was reverted
     together with DEFDAT_fn's fold).
 34. `_builtin_DATA` (interp.c ~4767) — new SNOBOL4 ingest pre-fold. The
     `VARVAL_fn(args[0])` spec string is user-data crossing the SNOBOL4
     boundary; `sno_fold_name` applied here before handing to shared runtime.
     Matches the SN-19 principle's "lexer running again on deferred input".
 35. `_DATA_` (snobol4.c ~1176) — same pre-fold at SNOBOL4's other runtime
     DATA ingest point. Spec folded once before `DEFDAT_fn`; per-field
     `sno_fold_name` calls at ~1198 (typename) and ~1209 (field) retained
     because the typename drives `register_fn(uname, ...)` which itself
     must agree with downstream lexer-folded identifier lookups.
 36. `data_field_ptr` (interp.c ~417) — `strcasecmp` → `strcmp`. Now safe
     because every ingest path (SNOBOL4 `_builtin_DATA`/`_DATA_` pre-folds,
     Icon/Raku `E_RECORD` evaluation in `interp.c:3790` passes verbatim,
     `sc_dat_register` passes verbatim) matches its corresponding lookup
     path by construction.

No broad-suite regressions (218/227 held); rk_class26 restored to PASS.

### SN-19 — what's left (next session starts here)

**Stage-2 cleanup still to do:**
- `interp.c` keyword/control-flow compares against uppercase literals
  (~lines 620/670/754/755/760/765): `strcasecmp(target, "END"|"RETURN"|
  "FRETURN"|"NRETURN")`, `strcasecmp(kw_rtntype, "NRETURN")`,
  `strcasecmp(s->subject->sval, "ITEM")`. AST `sval` and `target` arrive
  canonical; these can be `strcmp`. Straightforward now that the
  architectural uncertainty is resolved.
- `interp.c` ~line 496 DATA field `strcasecmp(pnames[i], retname)` — now
  safe: SNOBOL4-side both canonical via `_parse_define_spec` + DEFDAT pre-
  fold through `_builtin_DATA`/`_DATA_`.
- `ufname` construction + uppercase fallback (~454–460, 541, 544) — defensive
  belt-and-suspenders; leave for case-sensitive mode work to validate.

**Case-sensitive mode validation still to do:**
- Confirm/add a scrip CLI flag for case-sensitive mode (mirror of CSNOBOL4
  `-f`). Default = fold-to-upper (case-insensitive). Flag-on = preserve.
  With the architectural fix landed, the CLI flag only needs to toggle
  `sno_fold_on` in the SNOBOL4 lexer and the two SNOBOL4 ingest pre-folds
  (`_builtin_DATA`, `_DATA_`) — everything else is already neutral.
- Double-function trick (`push_list` vs `Push_list`) must keep working
  under the flag.

**Gate for SN-19 completion:** smoke PASS=7, broker PASS=49, broad ≥218/227,
`differ` minimal repro all three modes all pass ✅ **ALL MET THIS SESSION**
plus the previously-blocking `data_field_ptr` band-aid resolved. Remaining
work is incremental stage-2 cleanup + CLI-flag ergonomics, not blockers.

### Porter accuracy — not remeasured this session

| Mode          | Matches         | Accuracy |
|---------------|-----------------|----------|
| SPITBOL (oracle) | 23,531 / 23,531 | 100.00% |
| scrip --ir-run  | 19,639 / 23,531 (pre-SN-19) | 83.46% |
| scrip --sm-run  | 14,269 / 23,531 (pre-SN-19) | 60.64% |
| scrip --jit-run | 12,796 / 23,531 (pre-SN-19) | 54.38% *(SM_PUSH_EXPR opcode unimplemented at pc 997/1698 — SN-10..SN-12 scope)* |

**SN-18 ABI fix kept** — `bb_usercall` returns `DESCR_t` (was `spec_t`); all
`extern spec_t bb_*` forward declarations across `stmt_exec.c` / `bb_build.c` /
`bb_flat.c` corrected to `DESCR_t`. Drove Porter 54% → 83% under --ir-run.
Do **not** revert.

**Open issues tracked elsewhere:**
- SN-6 remaining failures (same 9 as session 4): fileinfo/word1/triplet/wordcount
  (SM INPUT-EOF hang), expr_eval `1+2*3 → 2` (match-time vs commit-time
  `*fn()` dispatch), beauty_XDump_driver (unknown), demo_wordcount/demo_roman
  (source MISSING in corpus), demo_claws5 (see GOAL-SNO-CLAWS5.md)
- SN-17 Porter --ir-run gap to 100% — cluster of `feed`-class leaks from failed
  ALT arms; NAM rollback needs to cover NAM_KIND_CALLCAP entries
- SN-17 Porter --sm-run gap (60.64% vs --ir-run 83.46%) — SM lowering has its
  own issues around correctly-deferred usercall

