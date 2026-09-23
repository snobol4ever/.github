# FINDING 2026-09-22 hq_icon — `proc("<op>", n)` procedure values hold a heap string the collector never visits

**Seat** hq_icon · **Mode** DECTET · **Trigger** ceo's CEO-1151 ask (re-run Jcon, name the still-red class) plus
the Icon master's `SCRIP_GC_STRESS=5` row (task `icon-master-under-scrip-gc-stress-5-...`, step (4)/write_253).

## THE DEFECT, TWO INDEPENDENT WITNESSES

`f := proc("~===", 2)` (or any operator-symbol string proc() resolves via the `op1`/`op2` tables,
`src/runtime/by_name_dispatch.c:6810-6817`) returns `DESCR_t{v=DT_E, slen=PROCVAL_SLEN, s=rt_heap_strdup_c(pname)}`
— an ordinary heap allocation (`HB_WSB`-class) holding the operator's name, reached ONLY through this DT_E's
`.s` field. Calling `f` later re-derives the operator by reading `.s` back out. Nothing roots that string across
a later collection: a subsequent allocation moves/reclaims the block, the next dereference of `.s` reads
garbage, and the runtime reports it as `error 106: procedure or integer expected` with the offending value
rendered as literal garbage bytes (`in {P<48 raw bytes>&null} from line N`) — the garbage IS the corrupted
`.s` pointer being printed, not a second bug.

- **corpus/tests/icon/ALL.icn `procedure_write_253`** (Icon master, `SCRIP_GC_STRESS=5`): `f := proc("~===",2);
  write("A:", image(f(1)))` — PASSES with plain `./scrip` (no output diff from `icont`), FAILS under
  `SCRIP_GC_STRESS=5` with the exact `error 106`/garbage-image shape above, zero stdout (icont: `A:&null B:2
  C:&null D:&null E:7`, all five lines).
- **corpus/packages/icon/jcon_tests/args.icn** (named in ceo's CEO-1151 regression report): FAILS at the
  **shipped default arena**, not only under forced stress — `SCRIP_GC_EXERCISE=1` names `collections=2` on the
  failing run. Forcing `SCRIP_HEAP_MB=64` (measured `collections=0` in the same report line) makes it PASS,
  byte-identical to `args.std`. Same `error 106`/garbage-image shape, confirmed by inspecting `args.icn:23`
  (a `proc(<operator string>, n)` call site of the same shape as `write_253`'s).

Two unrelated corpora, two unrelated programs, the identical failure signature, and a clean run at
`collections=0` that breaks the instant a real collection runs — this is not two coincidences.

## WHY IT IS NOT A `proc()` SEMANTIC BUG

Without any stress/pressure, `procedure_write_253` matches `icont` exactly on this tree (verified by direct
`./scrip` run, no env overrides) — `proc()`'s operator-table lookup and the `~===`-with-one-arg evaluation
(`by_name_dispatch.c:5439-5461`, defaulting the missing operand to `NULVCL`) are both correct. The defect is
purely in **survival of the returned procval across a collection**, not in what `proc()` builds.

## ROUTING

Not mine to cure — collector-shared (`by_name_dispatch.c`'s DT_E/`PROCVAL_SLEN` producers plus whatever typed
visitor walks a `DT_E` block; `rt_heap_strdup_c`'s result at `by_name_dispatch.c:6811`/`6817` is handed back as
a bare `.s` pointer with no root taken before the caller's next allocation). This is the same SHAPE as the
already-open `kind=215`/`rt_wsb_alloc` finding
(`FINDING-2026-09-21-hq_icon-two-master-suite-crashes-...-kind-215-never-visited.md`) but a DIFFERENT DESCR
tag (`DT_E`/`PROCVAL_SLEN`, not a plain `HB_WSB` value slot) — worth checking together, since a fix keyed only
on `DT_S`/`DT_SNUL` string slots would miss this one. Sent to cfo (collector lane).

## REPRO

```
cd SCRIP && python3 scripts/corpus_suite_harness.py extract ../corpus/tests/icon/ALL.icn ../corpus/tests/icon/ALL.ref \
    procedure_write_253 /tmp/w253.icn --out-ref /tmp/w253.ref
SCRIP_GC_STRESS=5 ./scrip /tmp/w253.icn < /dev/null   # error 106, garbage image; plain ./scrip matches icont

SCRIP_GC_EXERCISE=1 ./scrip corpus/packages/icon/jcon_tests/args.icn < /dev/null   # error 106 at shipped arena, collections=2
SCRIP_HEAP_MB=64 SCRIP_GC_EXERCISE=1 ./scrip corpus/packages/icon/jcon_tests/args.icn < /dev/null   # PASS, collections=0
```
