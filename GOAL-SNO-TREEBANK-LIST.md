# GOAL-SNO-TREEBANK-LIST.md — demo_treebank-list PASS

**Repo:** one4all
**Parallel:** This goal runs in its own session simultaneously with GOAL-SNO-TREEBANK-ARRAY
and GOAL-SNO-CLAWS5. All three sessions share main — pull --rebase before every push.
Fixes to shared files (interp.c, bb_boxes.c, stmt_exec.c) benefit all sessions immediately.

**Done when:** `demo_treebank-list` passes in `test_interp_broad_corpus_and_beauty.sh`;
output matches `corpus/programs/snobol4/demo/treebank-list.ref` under `--ir-run`.

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
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Program

```
corpus/programs/snobol4/demo/treebank-list.sno
Input:  corpus/programs/snobol4/demo/VBGinTASA.dat
Ref:    corpus/programs/snobol4/demo/treebank-list.ref
Oracle: CSNOBOL4 -bf -P 500k  (double-function trick; SPITBOL -f is broken)
```

Run to test:
```bash
DEMO=/home/claude/corpus/programs/snobol4/demo
timeout 30 /home/claude/one4all/scrip --ir-run $DEMO/treebank-list.sno \
    < $DEMO/VBGinTASA.dat 2>/dev/null | diff - $DEMO/treebank-list.ref
```

---

## Known state (2026-04-17)

**BAL is implemented** — `bb_bal` in `bb_boxes.c`, `XBAL` wired in `stmt_exec.c`.
This fix is already on main; pull it at session start.

**Blocker 1: case-sensitive label dispatch (same as GOAL-SNO-TREEBANK-ARRAY).**
treebank-list.sno uses `push_list`/`Push_list`, `init_list`/`Init_list`.
`label_lookup()` in `src/driver/interp.c` line 148 uses `strcasecmp`.
Fix: `strcmp`. GOAL-SNO-TREEBANK-ARRAY may land this fix first — pull before
starting work and check if it is already done.

**Blocker 2: CSNOBOL4 reports Error 16 (overflow) with default stack.**
treebank-list.sno builds deeply recursive list structures. CSNOBOL4 needs
`-P 500k` to run it without overflow. scrip has no pattern-stack size limit of
this kind, so this should not be a blocker for scrip — but watch for deep
recursion in the interpreter (call stack depth in `call_user_function`).

Current symptom (scrip): `''` — empty output. Program runs but produces no output,
likely because push/pop mis-dispatch (same root as treebank-array).

---

## Steps

- [ ] **TL-1** — Confirm `label_lookup` fix is on main (may be landed by
  GOAL-SNO-TREEBANK-ARRAY session). If not, apply it: change `strcasecmp` to
  `strcmp` in `label_lookup` in `src/driver/interp.c`. Rebuild. Run smoke + broker.

- [ ] **TL-2** — Run treebank-list under scrip --ir-run. Diff against ref.
  Fix any divergences. Watch for interpreter stack overflow on deep list recursion;
  if hit, raise `DVAR_MAX_DEPTH` in `interp.c` or investigate the recursion path.
  Gate: diff clean; smoke PASS=7; broker PASS=49;
  `test_interp_broad_corpus_and_beauty` PASS improves.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | `label_lookup`, `DVAR_MAX_DEPTH` recursion cap |
| `src/runtime/x86/bb_boxes.c` | `bb_bal` (already implemented) |
| `corpus/programs/snobol4/demo/treebank-list.sno` | Program under test |
| `corpus/programs/snobol4/demo/treebank-list.ref` | Expected output |

---

## Invariants

- CSNOBOL4 `-bf -P 500k` is oracle (SPITBOL `-f` broken).
- Never patch corpus source. Fix the runtime.
- Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- Pull --rebase before every push (parallel sessions active).

---

## Current state (2026-04-17, one4all HEAD — post-BAL commit)

TL-1 next. BAL on main. label_lookup fix pending (may arrive from treebank-array session).

---

## Session 2026-04-17 progress

**TL-1 DONE.**
- `label_lookup` in `src/driver/interp.c:148`: `strcasecmp` → `strcmp`.
- Smoke PASS=7, Broker PASS=49. Committed on main.

**TL-2 IN PROGRESS — root cause re-diagnosed; prior hypothesis disproved.**

Prior session hypothesized the remaining bug was in a `bb_callcap`/`CC_γ_core` path for
`epsilon . *fn(vs)` that was still prepending matched text as args[0]. **That hypothesis
is wrong.** All four user-call dispatch sites (`bb_usercall`, `bb_callcap` `$`-immediate,
`flush_pending_callcaps`, `NAM_commit`) were instrumented with TL_TRACE env-gated stderr
prints and none of them fire for the failing case. The bug is upstream.

**Minimal 22-line reproducer:** `/home/claude/tl_repro.sno` (attached below in full so
next session can recreate quickly — NOT checked into corpus since rule says no
speculative test files; recreate locally).

```snobol4
               &ANCHOR        =  0
               &FULLSCAN      =  1
               DEFINE('push_list(v)')
               DEFINE('Push_list(vs)')                      :(push_list_end)
push_list      OUTPUT         =  'push_list called with v="' v '"'
               push_list      =  .dummy                     :(NRETURN)
Push_list      OUTPUT         =  'Push_list called with vs="' vs '"'
               Push_list      =  EVAL("epsilon . *push_list(" vs ")")  :(RETURN)
push_list_end
               word           =  NOTANY('( )') BREAK('( )')
               pat            =  '(' (word . tag) Push_list('tag') ')'
               '(NP)'  pat                                  :F(nomatch)
               OUTPUT         =  'MATCH'                    :(END)
nomatch        OUTPUT         =  'NOMATCH'
END
```

Oracle (CSNOBOL4 -bf) output:
```
Push_list called with vs="tag"
push_list called with v="NP"
MATCH
```

scrip output (same program):
```
push_list called with v=""
MATCH
```

**Smoking gun from TL_TRACE instrumentation on `call_user_function`:**
```
[cuf] fname="Push_list" nargs=1 a0={v=1 s="tag"}
push_list called with v=""
MATCH
```

`Push_list` IS entered with `fname="Push_list"` and `args[0]="tag"` — the entry is
correct. But the `OUTPUT = 'Push_list called with vs="..."'` line inside its body
**never fires**. Instead, lowercase `push_list`'s body executes (its OUTPUT fires with
`v=""` because `v` is unset in the `Push_list` frame — only `vs` is set).

**Strong inferred root cause (needs one final trace to confirm):** every `FUNC_*_fn`
metadata accessor in `src/runtime/x86/snobol4.c` lines 2826-2877 uses `strcasecmp`:
`FNCEX_fn` (2831), `FUNC_NPARAMS_fn` (2841), `FUNC_NLOCALS_fn` (2849),
`FUNC_PARAM_fn` (2857), `FUNC_LOCAL_fn` (2866), `FUNC_ENTRY_fn` (2875). In a
case-sensitive program with both `push_list` and `Push_list` DEFINEd, `_func_hash`
puts them in the same bucket and `strcasecmp` returns the first entry that matches
case-insensitively. Then `call_user_function` at `src/driver/interp.c:548` does:
```c
const char *entry = FUNC_ENTRY_fn(fname);   // returns push_list's entry, not Push_list's
STMT_t *body = entry ? label_lookup(entry) : NULL;   // now labels case-sensitive — jumps to push_list body
```
TL-1 fixed `label_lookup` to be case-sensitive, but the function-registry lookup
that *feeds* the entry name into `label_lookup` is still case-insensitive. So we
jump to the wrong body with `vs="tag"` in NV, and `push_list`'s body reads `v`
(unset → `""`).

**Next session TL-2:**
1. Confirm hypothesis: add a one-line trace at `src/driver/interp.c:548-551`
   printing `fname`, `entry` from `FUNC_ENTRY_fn(fname)`, and which of the three
   fallbacks (`entry`, `fname`, `ufname`) actually resolved the body. Expected:
   for `fname="Push_list"`, `FUNC_ENTRY_fn` returns `"push_list"` (lowercase),
   body is found via that entry, lowercase `push_list` body runs.
2. Apply symmetric TL-1 fix to the function registry: change `strcasecmp` → `strcmp`
   in all six accessors in `src/runtime/x86/snobol4.c` (lines 2831, 2841, 2849, 2857,
   2866, 2875). This is the natural completion of TL-1.
3. Rebuild. Rerun the 22-line reproducer — expect oracle-matching output.
4. Rerun full treebank-list diff. If clean: done. If not, continue from there.
5. Smoke PASS=7, Broker PASS=49 must still hold. `strcasecmp` → `strcmp` on
   function registry may break case-insensitive callers elsewhere — watch broker
   and the full broad_corpus run for regressions.

**Risk note:** Changing `strcasecmp` → `strcmp` in `FNCEX_fn` in particular is
risky. `FNCEX_fn` is called in many places (grep shows ~15 sites) and some callers
may pass an uppercased name. Safest patch may be narrower: fix only `FUNC_ENTRY_fn`
plus the `FUNC_NPARAMS_fn`/`FUNC_PARAM_fn`/`FUNC_NLOCALS_fn`/`FUNC_LOCAL_fn` four
— the ones that matter for dispatching to the correct body's parameter frame.
Leave `FNCEX_fn` case-insensitive and see if broker still passes. If yes, that's
the right scope. If treebank still fails, widen.

**State:** instrumentation reverted; tree clean; no commits made this session
beyond the doc update you're reading. SPITBOL + CSNOBOL4 both built locally.
