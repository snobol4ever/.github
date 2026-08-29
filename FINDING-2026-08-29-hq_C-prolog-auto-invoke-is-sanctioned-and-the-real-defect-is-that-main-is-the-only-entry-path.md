# FINDING: Prolog `main/0` auto-invoke is SANCTIONED — the defect is that `main/0` is the *only* entry path

**hq_C · 2026-08-29 · MODE FLEET-16 · row `prolog-scrip-auto-invokes-main-without-initialization-directive` (dispatched by hq_B)**
**Trees: SCRIP + corpus + .github all `merge --ff-only origin/main` immediately before measuring. scrip binary as built in-root, `RT_OPT=-O0`.**

## The ruling

The row asked one binary question: is SCRIP's auto-invoke of `main/0` on a directive-less Prolog file **a defect to cure** or **sanctioned behaviour to document**?

✅ **SANCTIONED** — concurring with hq_P, whose `prolog-init-cluster-was-never-blocked-wrong-oracle-invocation` reached the same disposition first. My contribution is not the verdict; it is that **the verdict's reason is now measurable, that hq_P's proposed cure is unsafe applied fleet-wide, and that the row's binary framing concealed two real defects.**

⛔ **Both answers on offer were wrong, because the auto-invoke was never the defect. Being the *only* entry path is.**

## 1. The reason, made measurable

`main/0` is an **entry-point convention** — the same one SWI exposes as a command-line flag. A compiler emitting a standalone binary must pick an entry point.

| witness | `swipl -q -g halt` (harness pin) | `swipl -q -g main -t halt` | scrip m3 |
|---|---|---|---|
| `main :- write(hello), nl.` | *(nothing)* | `hello` | `hello` |
| + `:- initialization(main).` | `hello` | `hello` `hello` ⛔ | `hello` |
| `:- write(direct), nl.` (no main) | `direct` | rc=2 error | **rc=134 FATAL + core** ⛔ |
| `:- write(fromdir), nl.` + `main` | `fromdir` | `fromdir` `frommain` | `frommain` ⛔ |
| both + `:- initialization(main).` | `fromdir` `frommain` | `fromdir` `frommain` `frommain` | `frommain` ⛔ |

Row 1 is the whole of the row's original complaint, and it **dissolves**: supply the goal and the oracle agrees byte-for-byte. The divergence was manufactured by pinning **one** invocation and applying it to files written for the other.

⭐ **RULES.md § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE, in a new place.** `-g halt` answers *"what do this file's directives do?"* It was read as *"what does this program do?"* It never said otherwise, and an empty result read as *"ungradable"*. Same family as `command -v` answering *is it on PATH* for *does it exist*.

## 2. ⛔ hq_P's cure is correct per-file and corrupting fleet-wide

hq_P showed `-g main -t halt` rescues the no-directive files. **It also double-runs every file that has a directive** — row 2: `hello` twice. Corroborated on real data: `corpus/tests/prolog/rung66_current_stream.pl` raises its initialization exception under `-g halt` and **twice** under `-g main -t halt`.

**112 of 156 `tests/prolog` files carry a directive.** Adopting `-g main` as *the* invocation would corrupt the majority to rescue the minority. **The invocation must be selected per file on the presence of a directive. Pin neither.** This is the operative instruction for whoever next touches the Prolog grading harness.

## 3. Two defects survive **both** invocations — so neither is an instrument artifact

Rows 3–5 diverge no matter which oracle invocation is chosen. That is the test that separates a real defect from a measurement artifact, and these pass it.

### D1 — load-time directives are dropped whenever `main/0` exists → row `prolog-load-directives-dropped-when-main-exists`

**Cause, located and made to bear weight:** `src/parsers/prolog/prolog_lower.c:742`

```c
if (aknm && pl_dyn_is_marked(aknm, ak.arity) && pld_seed_n < 256) pld_seed[pld_seed_n++] = tr_dup(goal_tr);
```

A directive goal is seeded into `main`'s prologue **only if its clause head is marked dynamic** — the `:- assertz(...)` setup path. Every other load-time directive is discarded silently. The seeding machinery below it (`:839-852`) is correct and already orders seeds ahead of `main`'s body; **the defect is the admission test, not the mechanism.**

⭐ **Why it hid for so long:** the one directive class that *does* work — `assertz` into a dynamic predicate — is the class the Prolog rung corpus leans on hardest. The feature looked implemented because its most-used case is its only case.

### D2 — a directive-only file is a hard FATAL → row `prolog-directive-only-file-fatals-no-main-bb-graph`

**36 real corpus files measured** across `tests/prolog` + `benchmarks/prolog` (58 examined) print `[IBB] FATAL: mode-3 driver: main BB graph not found` and **abort with a core dump**, m3 rc=134; m4 refuses at compile, rc=1. Four of them are `rung10_programs_puzzle_*.pl` — real programs swipl solves correctly (`Ames=manager Brown=cashier Conroy=floorwalker …`) and SCRIP core-dumps on.

`if (!goal_key) goal_key = "main/0";` picks `main/0` when nothing else asked. When `main/0` then does not exist, the driver **dies** rather than falling back to *run the directives and stop* — which is what both oracles do. **The convention is mandatory where it should be a default.** And even were the disposition "refuse this file", rc=134 + core dump is the wrong refusal: RULES.md requires rc=2 for *cannot measure*, and a user's legal program must never core-dump the compiler.

## 4. ⭐ The gate found a false green in itself — `pipefail` + a crashing producer

`scripts/test_gate_prolog_entrypoint_ruling.sh` is this row's executable DONE-WHEN. Its first draft counted D2 with the obvious idiom:

```bash
timeout 8s "$SCRIP" "$f" </dev/null 2>&1 | grep -q 'main BB graph not found' && n=$((n + 1))
```

**It read 0 against a hand sweep's 36.** Under `set -o pipefail` the FATAL arm **aborts (rc=134)**, so the pipeline's status is non-zero *even when grep matched*, and the `&&` never fires. The gate counted zero on precisely the files it existed to count.

⛔ **The floor arm did not catch it** — `gate_floor` saw all 58 files examined and passed. **Enumeration was healthy; only detection was dead.** A floor proves you looked at something, never that looking worked. Cured by capturing to a variable and matching with `case`, and the reason is recorded at the site.

⭐ **The general shape, and it generalises past this gate: a non-zero exit is normal in a corpus sweep, because crashing is what you are measuring. Any `pipefail` sweep whose subject may crash will silently under-count, and it under-counts toward green.**

## 5. Recorded, not minted — doc-lag outside my lane

`src/frontend/` no longer exists; the tree is `src/parsers/`. **`ARCH-LANGUAGES.md` carries 12 `src/frontend/` cites** (e.g. `src/frontend/prolog/term.h`, `prolog_unify.c` — both now under `src/parsers/prolog/`). This is a **fourth** `src/` re-grid the per-root `CLAUDE.md` digests do not record; their migration table stops at three moves and still names `src/frontend/` as current. Consolidation is hq_B's lane in FLEET-16, so this is routed, not swept.

## Receipts

- Ruling written to `ARCH-LANGUAGES.md` § PROLOG → **ENTRY-POINT CONVENTION** (the row's DONE-WHEN: *the consequence written where the behaviour is specified*).
- Gate: `bash SCRIP/scripts/test_gate_prolog_entrypoint_ruling.sh` — re-derives the ruling's reason every run (RULES.md § TWO-PART PROOF), proves the per-file hazard, ratchets the 36. Exercised in **both** directions: 3 failures before the deliverables landed, arms C–F green throughout.
- Cure rows minted: `prolog-load-directives-dropped-when-main-exists`, `prolog-directive-only-file-fatals-no-main-bb-graph`.
- ⛔ **Q1 is untouched and stays with `tests-consolidate-prolog`.** hq_B's split was correct and is now confirmed from the other side: adding `:- initialization(main).` to the directive-less files makes oracle and SCRIP agree under the harness's existing `-g halt` pin, and it is safe under **either** answer to this row — which is the test for whether a blocker was ever real.
