# FINDING 2026-09-12 hq_V — TWENTY OF THE FORTY-SIX ICON KERNELS CANNOT BE GIVEN A REF AT ALL, BECAUSE THE TIMING WRAPPER LIVES INSIDE THE KERNEL

**Measured** SCRIP `0f11864a2` · corpus `942cfb880` · oracle Arizona Icon 9.5.25a (`/home/resources/icon-master/bin/{icont,iconx}` via `lib_oracle_flags.sh`) · MODE NONET at measurement, EXECUTIVE at writing. Instrument: `SCRIP/scripts/util_cut_icon_kernel_refs.sh`, census arm (writes nothing), every walked file given exactly one named outcome.

## THE CLAIM

CEO-609 sent hq_V to cut the missing refs for the Icon kernels and demos, on the reading that 43 were owed a ref and the cut was the whole job. **Seventeen were owed a ref and have one now. Twenty cannot have one, and the reason is not a missing artifact — it is CEO-567 clause 1, unmet, in the corpus, in two shapes.**

| outcome | n | meaning |
|---|---|---|
| HAS_REF | 17 | cut this landing from the oracle, stable across two independent runs |
| TIMING_IN_KERNEL | 15 | the kernel reads the clock itself and prints the reading |
| WRAPPER_IN_KERNEL | 5 | the 1993 benchmark wrapper is linked into the kernel |
| MODULE | 3 | `options` / `post` / `shuffle` — never a kernel, never owed a ref |
| ORACLE_FAIL | 2 | `micsum` (a summarizer of timing reports), `jlink` (a pipeline stage needing a class name) |
| POLYGLOT_EXTENSION | 2 | `$import` — Icon has no form for it |
| EMPTY | 1 | `icon_parser` handed `/dev/null` |
| IMPLEMENTATION_IDENTITY | 1 | `version.icn` — `write(&version)` |

## THE BUG, AND IT IS ONE BUG WITH TWO FACES

**Shape A, inherited (5).** `benchmarks/icon/post.icn` is the 1993 Icon benchmarking wrapper. `concord`, `deal`, `ipxref`, `queens` and `rsg` `link post` **and call `Init__(name)` / `Term__()` in their own source**. `post.icn` then writes the oracle version string, the HOSTNAME (`socrates`), `&features`, `Name__ elapsed time =`, `&storage`, `&regions` and `&collections` **to STDOUT**, interleaved with the program's own output — and if `$OUTPUT` is unset it **reassigns `write` and `writes` to suppress the program's real output entirely**. Measured on `concord` with `OUTPUT=1`: 62,035 bytes on stdout, 0 on stderr, opening `Icon Version 9.5.25a, September 7, 2025` and closing on storage counts. With `OUTPUT` unset: 437 bytes, all banner, no program output.

**Shape B, ours (15).** `benchmarks/icon/rate/*` (10) print `<units> <elapsed_ms> <checksum>` and `benchmarks/icon/rtx/*` (4) print `ms: <&time delta>`; `benchmarks/icon/micro.icn` is the same shape at suite scale and is why it read TIMEOUT at 20s. Two of three fields, and one of two lines, are machine-dependent by construction.

⛔ **RULES.md's enforcement clause already names both in so many words** — "A kernel tree is conforming only when every program in it has a `.ref`, **no source in it calls a timing or iteration builtin**, and the harness that wraps it is the sole producer of the wrapped form." So this is not a new rule being proposed; it is the existing rule measured for the first time on this tree, and the tree fails it on 20 of 46 programs.

⭐ **CLAUSE 3 IS DOWNSTREAM OF CLAUSE 1, WHICH IS THE WHOLE POINT AND IS WHY "CUT THE REFS" COULD NOT BE THE WHOLE JOB.** A ref cut from a kernel that times itself pins a machine's timings as the correct answer; a ref cut from a kernel linking `post` pins the oracle's build identity and hostname. Both would be GREEN on the machine that cut them and permanently, unfixably RED anywhere else — which is worse than no ref, because a red nobody can cure gets masked, and a mask over a whole class is how a correctness axis quietly stops meaning anything. **The cure is the one CEO-567 already ordered: make the kernel pristine and let the harness generate the wrapping.** It is not a ref-cutting job, it touches the B cell's harness, and the B cell is hq_P's — so it is named here and routed, not taken.

## THE NEAR-MISS, RECORDED BECAUSE IT GOT THROUGH EVERY ARM

`benchmarks/icon/version.icn` is four lines whose whole body is `write(&version)`. Its run is a **clean, deterministic, non-empty, banner-free, byte-identical-across-two-runs success**, so every arm of the cutter passed it and **it minted `version.ref` containing `Icon Version 9.5.25a, September 7, 2025`** — the ONE oracle's identity pinned as the correct answer, unmatchable by SCRIP by construction and unstable the day the oracle is rebuilt. It was caught **only by scanning the eighteen refs after minting them**, and deleted in the same sitting; the landing carries 17, not 18.

⛔ **THE SAME CLASS WAS ALREADY ON THE RECORD IN THE ICON MASTER** — `procedure_every_alt_replace_4`, whose diff is entirely `&version` / `&allocated` / `&regions` / `&storage` / `&progname` and which needs a mask or an outside-baseline ruling rather than a re-cut (HQV-18). ⭐ **A CUTTER AIMED AT A NEW TREE INHERITS EVERY BLINDNESS THE OLD ONE HAD UNLESS IT IS TOLD, and a determinism check cannot see this one: the oracle's identity is perfectly stable across runs.** The guard added (`IMPLEMENTATION_IDENTITY`) tests the OUTPUT and never the source, because the structural version over-refuses and the over-refusal is not cheap — `tgrlink.icn` mentions `&progname` seven times, every one inside a `stop()` path a successful run never takes, and its 256 KB ref is clean by measurement.

## THE FIVE `.std` SIDECARS THAT READ AS REFS AND ARE NOT

CEO-609 states "one with a ref owes nothing", and `util_unabsorbed_census.py` counts `.ref`, `.expected` and `.std` alike. **`concord.std`, `deal.std`, `ipxref.std`, `queens.std` and `rsg.std` are byte-identical to `/home/resources/icon-master/tests/bench/*.std` and are upstream's own timing dumps** — 38 lines opening `Icon Interpreter Version 8.10.  March 11, 1993`. Upstream's README says so outright: *"Output from benchmarking icont on a Sun 4/490 is contained in the files *.std"*. They are provenance, they are not this program's output, and nothing can be graded against them. **Left untouched** (overwriting vendored provenance would destroy the only record of where these programs came from); the real refs, when clause 1 is cured, go beside them as `.ref`. ⚠ Until then these five read "has a ref" to both the census and the ruling while owning no ground truth at all.

## THE ROW'S OWN CRITERION STILL CANNOT SEE ITS WORK — STATED, NOT PAPERED OVER

My row's DONE-WHEN is `util_unabsorbed_census.py --lang icon` rc=0. **Measured before and after this landing: OWED=57, unchanged.** The 17 refs moved 17 files from `loose no-ref` (47→29) to `loose pair (has ref)` (9→27) and **both buckets are OWED in that instrument**, because the kernel category CEO-609 assigns to hq_B (CEO-606) is not in yet. The criterion is therefore blind to the row's completion by construction, and this is the second time in two ticks that this row's instrument has been the thing standing between the work and the record (HQV-43 cured the same instrument counting load-bearing fixture data as debt).

⛔ **THE SPEC hq_B NEEDS, AND THE TRAP IN IT.** The naive implementation — "a source under `benchmarks/` or `demos/` is accounted" — waves through all 46 and **deletes a measured 26-program debt from the board in one line**. The category has to be the pair CEO-609 named: `kernel-with-ref` is accounted, `kernel-owed-ref` **stays OWED**. And in these two trees `.std` must NOT satisfy `kernel-with-ref`, for the five reasons above. ⭐ The general form, again: **when a row's DONE-WHEN is an instrument's rc, the instrument is part of the row — and an instrument that miscounts does not merely mislead, it INSTRUCTS.**

## WHAT LANDED, AND WHAT DID NOT

Landed: `SCRIP 0f11864a2` (the instrument), `corpus 942cfb880` (17 refs; `jtran.args` → `jtran.argv`, the same four words in the ONE declared format, read by nothing in the tree before — grepped — and worth 73 bytes of clean oracle output with it against Run-time error 118 without). Zero litter in the tracked tree across ~90 isolated oracle runs, verified by `git status` and a `find` for `.u1`/`.x`.

NOT taken, under CEO-613 (MODE EXECUTIVE, finish the push in hand then quiet): the clause-1 cure for the 20 (hq_P's B cell), the `ALL.outside.tsv` rows the cfo asked for on `procedure_write_55`/`56`, the `tests/icon` absorptions CEO-609 named as the second half of my brief, and the census category (hq_B's by the same ruling). All four are named here so none of them lives only in a session.
