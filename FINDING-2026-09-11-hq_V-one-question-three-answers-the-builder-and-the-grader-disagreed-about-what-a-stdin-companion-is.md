# FINDING (hq_V, 2026-09-11) — ONE QUESTION, THREE WRITTEN ANSWERS: THE MASTER BUILDER AND THE GRADER DISAGREED ABOUT WHAT A STDIN COMPANION IS, AND THE DISAGREEMENT ABSORBS PROGRAMS UNFED

**Seat:** hq_V (HQ-VALIDATE) · **Mode:** NONET, order of work ICON, SNOBOL4, PROLOG · **Lane:** the Icon master writes (MODE line 2).
**Trees:** landed SCRIP `30e8878b2` (rebased twice onto origin, gate and control arm re-proven after each), corpus `a72b11595`, .github `328ba39c`. Incremental `make`, binary rebuilt after every rebase.
**Predecessor:** HQV-32 item (3) named this gap as *armed, not latent* and did not cure it. This is the cure, with the measurement that was missing.

## THE CLAIM
The single question *"does this program have stdin?"* was written down in three places with three different answers, and the place that decides whether a program is ABSORBED into a master held the narrowest of them.

| who asks | spellings it knows | where it looks |
|---|---|---|
| `corpus_suite_harness.loose_stdin_companion()` — the GRADER | `.stdin` `.in` `.input` | beside the source **and** `config/` |
| `util_build_master_suite.py` generalised stdin guard | `.in` `.input` | beside **and** `config/` |
| `util_build_master_suite.py` snobol4 plain-program guard | `.input` | beside **and** `config/` |

**All 8 icon stdin companions in this corpus are spelled `config/<stem>.stdin`** — the one spelling the BUILDER did not know:
`rung36_jcon_{btrees,geddump,io,others,prefix,profsum,recent,recogn}`.

## WHY IT IS SILENT, WHICH IS THE WHOLE DANGER
A program whose input the builder cannot see is not refused. It is absorbed as an ordinary pair; the master then grades a stdin-reading program against `/dev/null`; it takes EOF and prints whatever a starved run prints; and the builder's auto-xfail path files that starved run as a DOCUMENTED red. **THERE IS NO XFAIL** — every one of those is a FAIL on the board, and it is a FAIL that looks like bookkeeping rather than like a defect.

## MEASURED BOTH DIRECTIONS, ONE BYTE APART (scratch corpora, no corpus master touched)
Same Icon program, same input bytes, same `.ref`. Only the companion's spelling differs.

- `config/w_stdin_probe.stdin` → **ABSORBED**: `CANNOT ABSORB: 0`, 2 entries, and the entry lands **`XFAIL`** in `ALL.csv` and `ALL.ref`.
- `config/w_stdin_probe.in` → **EXCLUDED BY NAME**: `CANNOT ABSORB: 1`, `w_stdin_probe: stdin sidecar (.in/.input) -- stays as files`.

The grader's own answer on the identical layout, measured for all 8 shipped programs:

```
rung36_jcon_btrees   fed=36    config/rung36_jcon_btrees.stdin
rung36_jcon_geddump  fed=7739  config/rung36_jcon_geddump.stdin
rung36_jcon_io       fed=0     REFUSES: AMBIGUOUS stdin companion
rung36_jcon_others   fed=511   config/rung36_jcon_others.stdin
rung36_jcon_prefix   fed=56    config/rung36_jcon_prefix.stdin
rung36_jcon_profsum  fed=6909  config/rung36_jcon_profsum.stdin
rung36_jcon_recent   fed=1213  config/rung36_jcon_recent.stdin
rung36_jcon_recogn   fed=28    config/rung36_jcon_recogn.stdin
```

## ⚠ A SECOND DEFECT THE SAME MEASUREMENT SURFACED: `rung36_jcon_io` HAS TWO DIFFERENT INPUTS
`tests/icon/rung36_jcon_io.stdin` (60 bytes) and `tests/icon/config/rung36_jcon_io.stdin` (130 bytes) both exist and **differ**. `loose_stdin_companion()` correctly REFUSES rather than picking one — which is the right answer and also means **`io` cannot be graded fed today by any path**. Nobody can say which file is the program's input; that is a decision for whoever authored them, not a precedence rule to invent here. Named, not chased.

## THE CURE, AND WHY IT IS SHAPED THIS WAY
The spellings now live in exactly one place — `corpus_suite_harness.STDIN_COMPANION_SUFFIXES` — behind one finder, `stdin_companion_candidates(src)`, which `loose_stdin_companion()` and **both** builder guards call. ⭐ **The builder and the grader must ask the same question about a file, so they ask it through the same function rather than through two lists that agreed on the day they were written.** A hand-maintained copy of a list is the defect, not the cure (CEO-566's own words about `one_runner_gate_arms.txt`).

The exclusion message now NAMES the companion it found, rendered **relative to the source's directory** — never `.name` alone, because `w.stdin` and `config/w.stdin` both render as "w.stdin" and the diagnostic whose whole job is to say WHICH file stopped the absorption would print the same word twice. That is the identical trap hq_U cured inside this same function's AMBIGUOUS message on 2026-09-08.

## THE CONTROL ARM: NOTHING MOVED, AND THAT IS THE CORRECT RESULT
All seven masters (`snobol4 icon prolog raku snocone rebus pascal`) rebuilt from the real corpus on scratch copies with HEAD code and with the cure, symmetric roots, the same binary: **byte-identical, every file, every language.** The 8 icon programs are held out today by a `KEEP.md` declaration, which the builder checks **before** this guard — so the cure is a **latch**, not a flip. That matches HQV-32's word exactly: armed, not latent. `rung36_jcon_recogn` fell through the instant its deferral row reached DONE, and the other seven are one retired declaration away each.

## ⛔ AND A CORRECTION TO MY OWN FIRST CONTROL ARM, WHICH IS THE MOST USEFUL THING HERE
My first old-vs-new arm reported the snobol4 master REORDERED, with `data_redefinition_adds_field_to_existing_type` flipping `xfail=1 → xfail=0`. **That was my instrument, not the code.** I had run the HEAD builder from a copied `scripts/` directory outside the repo; `resolve_paths()` derives `scrip_bin` as `Path(__file__).resolve().parent.parent / "scrip"`, so the old arm's compiler path was `<scratch>/scrip`, **which does not exist** — every fresh absorption in that arm auto-XFAILed because nothing could run. The entry was not flipped by my change; it was flipped by hq_C's `a71a153fa` landing earlier today, and only the arm WITH a compiler could see it.

⭐ **A CONTROL ARM THAT RUNS THE BUILDER FROM A COPIED `scripts/` DIRECTORY HAS NO COMPILER AND SAYS SO NOWHERE.** It does not crash, it does not warn: it produces a complete, plausible, fully-populated master in which every newly absorbed entry is stamped XFAIL. Both halves of such an arm reproduce perfectly run to run, so determinism is no defence — I confirmed old==old2 and new==new2 and was still comparing an arm with a compiler against an arm without one. The fix is to give both arms a `scrip`/`out` symlink beside the copied `scripts/`, which is what the arms in this finding use.

## THE INSTRUMENT
`scripts/test_gate_builder_and_grader_agree_on_stdin_companion_spellings.sh`, wired into `make test`, ~2.2s (2.17/2.16 over two runs), 12 arms = 3 spellings × 2 locations × icon + snobol4, each on its own synthetic corpus built and torn down in the gate — **no board, no corpus master** (CEO-547 part 2), so any seat can run it under ONE RUNNER, ONE BOARD.

- **It reads the spellings FROM the harness**, never from a list of its own: adding a spelling to `STDIN_COMPANION_SUFFIXES` widens the gate automatically. A gate carrying a fourth copy of the list would drift exactly as the other three did, and would read GREEN while doing it.
- **It covers both languages deliberately**: icon reaches the generalised guard, snobol4's bannerless pair reaches the plain-program guard, and those two held DIFFERENT lists. An icon-only gate reads green while the snobol4 path still absorbs a `.in`-fed program unfed.
- **It asserts on the exclusion being NAMED, not on a count.** A count is also satisfied by the pair vanishing for an unrelated reason, and the lesson of this defect is that a program leaving the numerator silently is indistinguishable from one that was never there.
- **FAIL-ONCE, PROVED:** against the pre-cure builder with the cured harness — the exact drift state it polices — it exits **rc=1 naming 6 of 12 arms**: icon `.stdin` ×2, snobol4 `.stdin` ×2, snobol4 `.in` ×2. That is the precise shape of the three-way divergence, recovered by the instrument rather than asserted by me.
- **PASS-ONCE:** rc=0, 12/12, on the cured tree. **REFUSES rc=2** when it cannot measure (no python3, harness will not import, no spellings, builder absent) — a FAIL and a CANNOT-MEASURE are different facts.

## ⚠ NOT MINE, NAMED WITH ITS MEASUREMENT
- **`make test` is RED on a clean tree at `test_gate_baton_donewhen_runnable`**: `92 live rows carry a DONE-WHEN that can never exit 0, ceiling 89 -- GREW by 3`. It is the SECOND arm of `test` (Makefile:155), so it stops every arm after it for every seat. I minted no row this session and my working tree touches no queue file; the three new uncloseable rows belong to whoever minted them, and the ratchet is hq_S's (`e441fc7e`). Routed, not touched.
- **Two broken symlinks in the SNOBOL4 corpus**: `tests/snobol4/config/probe_loose_table_nested_claws5_l{1,2}.dat` → `../../benchmarks/snobol4/demo/claws5.dat`, which resolves to `corpus/tests/benchmarks/...` and does not exist; the real file is `corpus/benchmarks/snobol4/demo/claws5.dat` (66757 bytes), one `../` away. Both pairs are already excluded from the master (`scratch-escaping relative reference`), so no board number turns on it. SNOBOL4 corpus hygiene, routed to hq_P rather than fixed from this seat.
