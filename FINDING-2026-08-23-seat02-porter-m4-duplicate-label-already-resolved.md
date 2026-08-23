# FINDING — porter-m4-duplicate-label was already closed by `b7d88465` before this session started; independently verified and swept corpus-wide, zero code change needed

**Session:** 2026-08-23 seat02 (`/home/claude02`, Claude Sonnet 5), THE LOOP row `porter-m4-duplicate-label`, doorbelled by hq_C. Pristine per HQ-27 (`git pull --rebase` both repos, `make pristine`) before any verdict: SCRIP `a0859f7e` (corpus `1be5e617`, `.github` this commit). Watermark unchanged in SCRIP/corpus — no source touched.

## WHAT THE BRIEF ASKED

The baton (`/home/resources/postoffice/tasks/porter-m4-duplicate-label.task.md`, owner hq_C) and hq_C's doorbell both describe mode-4 emitting a duplicate local label for `demo/porter.sno` — `grep -c '\.Lx865_40'` = 2, `as` refusing with "symbol .Lx865_40 is already defined" — and direct that the CLASS be fixed (RULES.md NO-PER-OP-FILTER), not porter's specific node 865.

## THE ROW WAS ALREADY CLOSED

`git log --all --grep` over SCRIP surfaces `b7d88465` — **"alt-label-collision-cure: two internal-label range collisions + VLIST mechanism pinned"** — authored/committed `LCherryholmes <lcherryh@yahoo.com>`, pushed to `origin/main`, and an ancestor of both this session's HEAD (`a0859f7e`) and hq_C's own s264 baseline commit (`1257d56c` — `b7d88465` is `1257d56c~5`). Its message states the real root cause precisely:

`bb_match_alternate.cpp` entry stubs minted `.Lx<uid>_(21..19+N)` while sigma stubs minted `.Lx<uid>_(40..39+N)` for the same alternation node. The two series are only disjoint while `N < 21`; at exactly `N==21` the entry series' last label (`19+21=40`) lands on the sigma series' first (`40`) — a genuine range-arithmetic bug, not a node-specific one. Porter's stemmer has a 21-arm suffix alternation, so it hit the boundary. **Cure:** `alt_sigma_base(N) = max(40, 20+N)`, which keeps the two series disjoint for every `N`, not just 21 — satisfying NO-PER-OP-FILTER by construction (it's a formula over the shared mechanism, not an exception list). The same commit also caught and fixed a **second, independent** latent collision in `bb_call_proc_staged.cpp` (`stage_arg_inline`'s `L(20+2i)` landed `i==4` on `L29`, already claimed by `bcps_nret_consult` — any box staging 5+ inline args, not yet witnessed by any corpus program) by moving it to its own range (`SAI_L0=200`).

Confirmation this was real and not a misreading: two earlier commits (`dacd3852`/s116, `49fc7632`/board-SKIP4-naming) independently reproduced and named "duplicate .Lx865 local" / "a real duplicate-label compiler bug" against porter before the cure landed — the defect and the fix are both attested in history, not inferred.

## INDEPENDENT VERIFICATION THIS SESSION (before finding the commit)

1. **DONE-WHEN run verbatim** (compile porter.sno, `as` the output) — exits 0, both steps.
2. **Full crosscheck, both modes, against `porter.ref`** — byte-identical m3 (`--run`) and m4 (`--compile` → `gcc -c` → link) output.
3. **The `grep -c` "2" re-examined**: still reads 2 today, but it is one *definition* (`.Lx865_40:` at the line emitting the label) plus one *forward reference* (`lea rax,[rip+.Lx865_40]` two lines earlier) — never two definitions. `as` has nothing to refuse.
4. **Own corpus baseline** (own run of `test_corpus_snobol4.sh`, not copied from hq_C): m3 PASS=358 FAIL=2, m4 PASS=357 FAIL=2 SKIP=1, **360 total**. demo_porter names in neither the FAIL nor the SKIP list — matching hq_C's own s264 number (359-denominator version, since corrected by hq_C in-session to 360) and confirming the fix predates s264's measurement, not this session.
5. **The one live SKIP** (`132_pat_fence_eps_recur_shallow`) traced to completion: link-time `undefined reference to 'FN__makeP'` — a missing-symbol defect, unrelated to label minting. Not this row; not chased further; named here only so it isn't mistaken for the same class.
6. **Corpus-wide class sweep** (own script, `sweep_dup_labels.sh`): every non-`programs/lon/` `.sno` in corpus (1971 files) compiled to mode-4 `.s` (1806 succeeded; 165 hit unrelated pre-existing compiler aborts, not duplicate-label related) and assembled with `as`, grepping every stderr for "already defined". **Zero hits.** This is the strongest evidence available that the class — not just porter — is currently clean: it doesn't rely on any one program's structure happening to probe the fixed boundary.

## WHY THE ROW WAS STILL DOORBELLED

hq_C's own s264 QA note on the baton already flagged the SKIP-count as stale ("there is now exactly ONE m4 SKIP left ... NOT demo_porter, which the runner now reports differently") but the brief's `## NEXT` steps and hq_C's assignment message were written against the original (pre-`b7d88465`) bug report and never revised once the fix landed five commits earlier in the same lineage. Classic stale-baton pattern already named elsewhere in this project's own history (STALE-ORIENTATION, RULES.md).

## OUTCOME

No code change made — none was needed. Row computedly closed via `s4e_msg.sh done porter-m4-duplicate-label` (DONE-WHEN re-executed live, exited 0). Full receipts appended to the task baton's LEDGER. Recommend the baton be retired rather than redispatched; its `## NEXT` section is historical.
