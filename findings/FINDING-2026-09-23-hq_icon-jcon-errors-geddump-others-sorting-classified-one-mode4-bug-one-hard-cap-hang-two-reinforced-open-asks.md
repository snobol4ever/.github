# FINDING 2026-09-23 hq_icon — the four remaining Jcon reds (errors, geddump, others, sorting), classified

**Seat** hq_icon · **Mode** DECTET · **Context** continuing the Jcon-to-91 row after SCRIP 9c0011d92 (proc-operator
fix) moved the board 76->78/82 by curing `args`/`coerce`. This sitting examined the remaining four.

## `others` and `sorting` — reinforcing evidence for already-open asks, no new ask sent

- `others.icn`: SIGSEGV, `SCRIP_GC_BIRTH_LEDGER` names `kind=215/HB_WSB, size=8208, allocated by rt_wsb_alloc
  from rt_wsb_realloc` — the IDENTICAL (kind, allocator, caller) triple as `every_scan_replace_2`,
  `every_suspend_replace_9`, `record_every_replace_13/17` (cfo's open kind-215 ask, icon-master-under-stress-5 row).
- `sorting.icn`: SIGSEGV, birth signature `kind=213/HB_DINST, allocated by DATCON_fn from rt_make_list` — the
  IDENTICAL triple as `record_coexpr_replace_3`/`record_every_replace_12` (cto's open kind-213 ask, same row).

Neither needs a new telegram; both are witnesses of open classes, folded into the GC-stress task's ledger.

## `errors.icn` — NEW, mode-4-ONLY: a procedure's return value comes back as repeated poison bytes through a `|` alternation

`(2 % "a") | monitor(&line)` — `2 % "a"` raises error 102 under `&error:=1`(-trapped), the `|` alternation falls
through to `monitor(&line)`, which prints `&error`/`&errornumber`/`&errortext`/`&errorvalue` (ALL FOUR CORRECT,
byte-identical to icont, ruling out a keyword-rooting gap — confirmed independently with a minimal witness
forcing 2000 `list(50)` allocations plus `SCRIP_GC_STRESS=5` between the error and the read: still matches) and
`return`s `line` (142, a plain integer). `write(name, image(that alternation's value))` is where it breaks:

- **mode 3 (`--run`)**: matches `icont` byte-for-byte, 5/5 reruns, deterministic PASS.
- **mode 4 (`--compile`)**: deterministic FAIL, 5/5 reruns — `image()` of the alternation's value prints a run of
  ~700 repeated single bytes (`cat -v`: `M-[M-[M-[...`, a poison/uninitialized-memory pattern) instead of `142`.
  Every other line of this 480-line, error-heavy program matches; this is the ONLY divergent line.

Clean at `SCRIP_HEAP_MB=64`/`collections=0` (confirmed), broken at the shipped default arena — collector-related,
but the shape (a plain INTEGER return value reading back as a long poisoned-memory run, not a corrupted string
pointer) does not match this session's other findings (kind=215/213/205 unrooted results, or the DT_E/PROCVAL_SLEN
gap already cured). This smells like a MODE-4-SPECIFIC frame/register convention for a procedure's return value
crossing a `|` alternation under a live collection, not a missing root on a named global slot — exactly the
"reaches the frame/spine" shape the icon-master-under-stress-5 row's own NEXT block says to hand to cto rather
than guess at (CEO-942's split). NOT attempting a cure: this is the same territory as the trace-tap poll placement
this seat got wrong earlier today, and it needs a debugger/ASM-diff session on the m3-vs-m4 divergence, which
RULES.md's own debugging order (ASM-DIFF-FIRST) prescribes and this seat has not yet run.

## `geddump.icn` — reinforces the not-yet-routed hard-cap+collector hang class

HANGS (rc=124, 20s timeout) at the shipped default arena feeding its real `.dat` input; clean (rc=0, matches
`.std`) at `SCRIP_HEAP_MB=64`/`collections=0`. Same shape as `every_suspend_replace_10` from the icon-master row
(SIGABRT-clean-exhaustion at default settings, HANG instead of abort under added pressure) -- a second witness for
a class that row already named as "not yet routed to anyone." Folding both into that row's ledger; still nobody's
open ask.

## ROUTING

`others`/`sorting`: no action, already asked (cfo kind-215, cto kind-213). `errors`: NEW, needs ASM-diff between
m3 and m4 emission for a procedure-return-through-alternation before anyone should touch it — flagged to cto
(frame/spine) rather than attempted blind. `geddump`: reinforces an unrouted hard-cap/collector-hang class from
the icon-master row; still needs a home, tentatively cfo (collector/allocator) given the shape (a real capacity
case that should abort cleanly and instead spins).

## REPRO

```
cd SCRIP
SCRIP_GC_EXERCISE=1 ./scrip ../corpus/packages/icon/jcon_tests/others.icn < /dev/null   # SIGSEGV, kind=215
SCRIP_GC_EXERCISE=1 ./scrip ../corpus/packages/icon/jcon_tests/sorting.icn < /dev/null  # SIGSEGV, kind=213
./scrip --compile -o /tmp/e.s ../corpus/packages/icon/jcon_tests/errors.icn && gcc -no-pie -o /tmp/e /tmp/e.s -Lout -lscrip_rt -Wl,-rpath,$PWD/out -lm -lpthread && /tmp/e < /dev/null | diff - ../corpus/packages/icon/jcon_tests/errors.std   # one line, poisoned bytes for "142"
timeout 20 ./scrip ../corpus/packages/icon/jcon_tests/geddump.icn < ../corpus/packages/icon/jcon_tests/geddump.dat  # rc=124 hang; SCRIP_HEAP_MB=64 -> rc=0, matches
```
