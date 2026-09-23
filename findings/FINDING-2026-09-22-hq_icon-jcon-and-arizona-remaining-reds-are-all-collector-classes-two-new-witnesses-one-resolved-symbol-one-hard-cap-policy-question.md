# FINDING 2026-09-22 hq_icon — Jcon (78/82) and Arizona (81/88): every remaining red sorts into an
already-open collector class, one previously-unresolved symbol gets named, and a hard-cap policy
question is raised

**Seat** hq_icon · **Mode** DECTET · **Ask** Lon, direct in-chat: "Get Jcon and Zona test suites to 100%."
**Tree** SCRIP `a4bf5637e` (post-pull, includes the by_name_dispatch.c fix that already moved Arizona
76→81/88 by curing args/coerce/coexpr/tracer/transmit), corpus `df634e34d`, RT_OPT `-O0`.

## THE MEASUREMENT FIRST

Fresh incremental build, both suites re-run this sitting via their sanctioned runners (`test_icon_jcon_suite.sh`,
`test_icon_arizona_suite.sh`), boards auto-published to SCORE.md/SUITES.tsv by the runner itself:

- **Jcon 78/82**, union of reds 4: `errors` `geddump` `others` `sorting`
- **Arizona 81/88**, union of reds 7: `errors` `gc2` `ilib` `mega` `others` `sorting` `spellnum`

Every one of these 9 distinct programs (some names collide across the two suites but are different files)
sorts into one of three already-tracked GC-collector classes, plus one new capacity-policy question. NONE
is a safe, self-contained Icon-lane fix — every one either reaches the frame/spine or the collector's typed
visitors (the shared infrastructure the four officers are chunk-dividing per CEO-1107/1108), or is a hard
heap-cap capacity question (CEO-1101, Lon's explicit "do not extend it" order). Per TENET (HQs measure,
officers cure) and this same row's own standing instruction, none of these were attempted blind.

## kind=215/HB_WSB — cfo's open ask, two new witnesses

- `arizona/spellnum.icn`: SIGSEGV, birth `kind=215/HB_WSB size=48, rt_wsb_alloc`, caller unresolved (symbol
  at `+0xd41ae`), direct call site not through `rt_wsb_realloc`.
- `arizona/others.icn`: SIGSEGV, birth `kind=215/HB_WSB size=8208, rt_wsb_alloc from rt_wsb_realloc` —
  BYTE-IDENTICAL signature to `jcon/others.icn` (same size, same allocator/caller pair).

Both fold into cfo's standing kind-215 ask (the `icon-master-under-scrip-gc-stress-5-...` row's ledger).
No new telegram needed — reinforcement only.

## kind=213/HB_DINST — cto's open ask, one new witness

- `arizona/sorting.icn`: SIGSEGV (m3 only; m4 passes — asymmetric), birth `kind=213/HB_DINST size=48,
  DATCON_fn from rt_make_list` — identical signature to `jcon/sorting.icn` and to the row's own
  `record_coexpr_replace_3`/`record_every_replace_12` witnesses. Reinforcement only, no new telegram.

## kind=2 — THE PREVIOUSLY-UNRESOLVED SYMBOL, NOW NAMED

Today's earlier ledger entry on the GC-stress row named `every_suspend_replace_7` as "kind=2 (UNRESOLVED
NAME, not in the typed-kind table), allocated by c_rt_str_alloc, caller symbol also unresolved... worth its
own ask once someone can resolve the symbol."

`arizona/ilib.icn` SIGSEGVs with the SAME kind=2 signature, and this run's stack DOES resolve the caller:

```
[ZGC-BIRTH]   block #61173, kind=2/HB_?, size=1360, allocated by c_rt_str_alloc (.../libscrip_rt.so+0x962fb)
              from rt_substr (.../libscrip_rt.so+0x4ddb57), born at arena+257376, +672 into it
```

`rt_substr` (`src/runtime/builtins/gen_runtime.c:193`, registered `GC_RET_DESCR` in
`src/templates/x86/gc_allocating_table.inc:1577`) is called from exactly three Byrd-box templates:
`bb_scan_move.cpp`, `bb_scan_tab.cpp`, `bb_scan_alternate.cpp` — the pattern-scan boxes, i.e. squarely
**cto's chunk A ("scan spine", 24 sites)**, not a new class. This resolves the previously-unnameable
`every_suspend_replace_7` symbol and gives cto a second, independent witness in a different corpus. Telegram
sent to cto with both witnesses and the resolved symbol.

## `errors.icn` — CONFIRMED the SAME bug in both suites, still unrouted for a cure

`jcon/errors.icn` and `arizona/errors.icn` both FAIL only in mode-4, both on the exact same construct:
`image((2 % "a") | monitor(&line))` — `monitor` returns a plain integer (the current source line), which
prints as ~700 bytes of repeated poison instead of the number. Diffed the two suites' `errors.icn` sources:
byte-identical line. One bug, two suite entries — curing it clears both.

Attempted to shrink the repro past what the 09-22 21:51 finding already established (that finding flagged
this as needing an ASM-diff/debugger session and explicitly did not attempt a cure). Built two minimal
witnesses this sitting:

```icon
# gc_errors_alt.icn: every i := 1 to 3000 do s := list(50); write(image((2 % "a") | monitor(&line)))
# gc_errors_direct.icn: same but write(image(monitor(&line))), no alternation
```

Both PASS cleanly in m4, with and without `SCRIP_GC_STRESS=5`, with and without `SCRIP_HEAP_KB=64` (tiny
arena). Neither raw allocation volume nor forced stress alone reproduces it — the real file's `main()` sets
`&error := -1` once and runs procedures `p1`..`p6` first (dozens of prior trapped-error expressions each
doing real work) before reaching the failing line, so whatever collector state or object graph the bug needs
is built up over that longer run, not by bulk allocation alone. NEGATIVE RESULT, but it narrows the search:
this is not "any DESCR return value crossing any collection" (that would have shown in the minimal witness);
something about the specific preceding call sequence matters. Still flagged to cto (frame/spine, per CEO-942's
split) rather than guessed at further blind — reinforcing, not superseding, the 09-22 21:51 finding's routing.

## NEW: the hard heap-cap (CEO-1101, 4096 KB) genuinely blocks three entries, and this is a policy question

- `arizona/mega.icn`: aborts at the shipped default (SIGABRT, `[ZHP] HARD CAP REACHED`, COLLECTIONS RUN 74 —
  a real capacity case per the abort message's own three-way classification, not zero collections). Clean
  and byte-identical to oracle at `SCRIP_HEAP_MB=64`.
- `jcon/geddump.icn`: HANGS (rc=124) at the shipped default feeding its real `.dat` input; clean (rc=0,
  matches `.std`) at `SCRIP_HEAP_MB=64`. (Already named in the 09-22 21:51 finding as an unrouted hang class;
  this sitting confirms the SAME 64 MB threshold clears it, same shape as `mega`.)
- `arizona/gc2.icn`: wrong output, but NOT a rooting bug — it directly prints `&collections` (the built-in
  collection-count keyword) after each of 8 explicit `collect()` calls. SCRIP's count runs a constant +1
  ahead of iconx's at every line (2 vs 1, 3 vs 2, ... 6 vs 5): one extra SPONTANEOUS collection happens
  before/during the program's own first `collect()`, an inherent consequence of the 4 MB cap forcing GC
  pressure iconx's much larger default heap never sees. This is not fixable without either matching iconx's
  heap size (defeats the cap) or artificially suppressing an automatic collection near the cap (dangerous).

None of these three are ROOTING bugs — no ZGC-STALE trap, no stale pointer. They are what the cap's own abort
message calls "a live set that genuinely does not fit the window this run named," and `gc2` is a keyword
whose value is definitionally a function of collection cadence. Neither `board_icon_master.sh` nor either
package-suite runner (`test_icon_jcon_suite.sh`, `test_icon_arizona_suite.sh`) sets `SCRIP_HEAP_MB` — all
grade at the bare 4 MB shipped cap. Raised as an ASK to ceo, not attempted as a fix: does 100% on these three
package-suite entries require a larger DECLARED arena for package-suite grading (the same kind of explicit
choice board_icon_master's own SCORE.md row appears to name as `arena_mb=512`, though neither runner script
actually sets that env var — worth checking where that number comes from), or are these three expected to
stay ungradable/excluded under the hard-cap policy? This is Lon's tradeoff to make, not mine.

## ROUTING

cfo: reinforcement only (kind-215, two new witnesses, no new telegram needed — folded into the ledger).
cto: telegram sent — kind-213 new witness (arizona/sorting) plus the RESOLVED kind-2/`rt_substr` symbol
(arizona/ilib, scan-spine chunk) plus reinforcement of the errors.icn frame/spine flag.
ceo: telegram sent — the hard-cap policy question (mega/geddump/gc2), needs Lon's call, not a code fix.

## REPRO

```
cd SCRIP
SCRIP_GC_BIRTH_LEDGER=65536 ./scrip --run ../corpus/packages/icon/arizona_tests/general/ilib.icn < /dev/null      # SIGSEGV, kind=2, rt_substr
SCRIP_GC_BIRTH_LEDGER=65536 ./scrip --run ../corpus/packages/icon/arizona_tests/general/spellnum.icn < /dev/null  # SIGSEGV, kind=215
SCRIP_GC_BIRTH_LEDGER=65536 ./scrip --run ../corpus/packages/icon/arizona_tests/general/others.icn < ../corpus/packages/icon/arizona_tests/general/others.dat   # SIGSEGV, kind=215
SCRIP_GC_BIRTH_LEDGER=65536 ./scrip --run ../corpus/packages/icon/arizona_tests/general/sorting.icn < /dev/null   # SIGSEGV, kind=213
SCRIP_HEAP_MB=64 ./scrip --run ../corpus/packages/icon/arizona_tests/general/mega.icn < /dev/null   # rc=0, matches .std; default arena aborts (hard cap)
SCRIP_HEAP_MB=64 ./scrip --run ../corpus/packages/icon/jcon_tests/geddump.icn < ../corpus/packages/icon/jcon_tests/geddump.dat   # rc=0, matches .std; default arena hangs
./scrip --run ../corpus/packages/icon/arizona_tests/general/gc2.icn < /dev/null   # &collections runs +1 vs oracle, every line, from the first
```
