# FINDING — `test_gate_pl_port_trace.sh` misreports GATE UNPROVEN(2) on any witness that refuses at compile time, not a broken tracer

**seat09, 2026-09-06, FLEET-12. Measured while working row `prolog-rung-15-stream-character-and-byte-io-complete-iso-8-11-to-8-13`
(hq_C, rung15), running that baton's own DONE-WHEN arm 3.**

## What happened

`bash scripts/test_gate_pl_port_trace.sh --to 15` (tree SCRIP `af8712f3d` corpus `db275702f` .github `f6830947e`):

```
GATE UNPROVEN(2) [test_gate_pl_port_trace]: ladder__rung10_global_vars_b_setval_getval m3: SCRIP_PL_TRACE=1 produced ZERO trace lines -- the instrument is not firing, this is not 'no ports'
```

rc=2, no timeout involved (completed well inside an 8s window). This fires at **rung10**, not rung15 — the
gate iterates origins in ascending rung order and `exit 2`s at the first bad one, so rung15's own 7 still-red
stream forms (see `FINDING-2026-09-05-seat08-...`) are never even reached by `--to 15`. This row's DONE-WHEN
arm 3 cannot pass today for a reason that has nothing to do with rung15.

## Repro (minimal, standalone, no gate involved)

```
$ cat w.pl
:- initialization(main).
main :- b_setval(flag10a, on), b_getval(flag10a, V), write(V), nl.

$ ./scrip w.pl </dev/null;                      echo rc=$?
scrip: prolog: builtin b_getval is not on the ladder yet -- rung 10 lands it (...)
rc=2
$ SCRIP_PL_TRACE=1 ./scrip w.pl </dev/null;     echo rc=$?
scrip: prolog: builtin b_getval is not on the ladder yet -- rung 10 lands it (...)
rc=2
```

Identical stderr, identical rc=2, in both cases — `SCRIP_PL_TRACE=1` changes nothing about this program's
behavior. (First pass at this repro piped through `head` and misread `$?` as the pipeline's last stage —
caught and re-measured without a pipe before writing this down; flagging it only so nobody re-treads that
specific hole.)

## Root cause (read, not guessed — `src/lower/lower_prolog.c`)

`pl_refuse()` (line ~68-72) is unconditional:

```c
static void pl_refuse(const char * what, const char * detail, int rung) {
    fprintf(stderr, "scrip: prolog: %s%s%s is not on the ladder yet -- rung %d lands it (...)\n", ...);
    exit(2);
}
```

`b_setval`/`b_getval` are named in `pl_rung10_builtins[]` (line 188) but — unlike `nb_setval`/`nb_getval`,
which have a real lowering case at line 889 (`pl_db_leaf2("$nb_setval", ...)`) — have no lowering case of
their own, so a call falls through to this refuse path **during lowering**, i.e. before any IR/BB graph
exists for the program at all. mode-3 never jumps into a box graph, so `SCRIP_PL_TRACE` correctly has zero
`Call:`/`Exit:`/`Redo:`/`Fail:`/`Exception:` lines to emit — there is no hidden tracer to "not fire."

This is not `b_setval`-specific: `corpus/tests/prolog/config/LADDER.tsv`'s own rung10 `global_vars` row
already documents `b_setval_getval`, `b_setval_trails_on_backtrack`, `prolog_flag_read` and
`prolog_flag_set` as pre-existing REFUSE-class reds (rc=2, "hq_C's cure", dated 2026-09-04/05, unrelated to
this finding). Standalone-checked two more refuse-class witnesses for contrast: `retract_erase_first_match_1`
(a *different* refuse message, `lower_prolog.c` dynamic-predicate path) and rung15's own `stream_property`
(the *same* `pl_refuse` call site, just a different `rung` argument, per seat08's finding) — **both** also
print their refuse message unchanged and keep rc=2 under `SCRIP_PL_TRACE=1`, with (necessarily) zero trace
lines either way. So this is the general shape of every still-unlanded, refuse-class ladder witness, not one
form.

## The gate's actual logic (`scripts/lib_port_trace.sh:109-130`)

Per witness per mode, the gate:
1. runs untraced (`r30`) and traced (`r31`), and already computes `pert3`/`pert4` = whether rc and stdout
   are IDENTICAL between the two runs (lines 117-124) — for a compile-time refuse this is trivially `OK`,
   since both runs hit the same `exit(2)` before there is anything trace-sensitive to diverge on;
2. **then, unconditionally, regardless of `pert3`/`pert4` or rc** (line 129-130):
   ```sh
   [ "$total" -gt 0 ] || { echo "GATE UNPROVEN(2) ...: $PORT_TRACE_ENV=1 produced ZERO trace lines -- the instrument is not firing, this is not 'no ports'"; exit 2; }
   ```
   treats zero normalized trace lines as ALWAYS meaning "the instrument is broken." That is true for a
   witness that runs to completion (or fails mid-graph) with no ports touched — the gate's comment is right
   about *that* case — but false for a witness that never entered a box graph in the first place, which
   `pert3`/`pert4` (already computed, one loop earlier, and already `OK` here) is exactly the signal that
   would tell the two cases apart.

## Scope and impact

- Blocks `test_gate_pl_port_trace.sh --to N` for **every** N ≥ 10 today, unconditionally, at the first
  refuse-class witness in rung order (currently rung10's `global_vars_b_setval_getval`) — masking whatever
  rungs 11-15+ would otherwise report, trace-wise. `--only 15` was not separately checked this session but
  is expected to hit the identical class the moment it reaches any of rung15's 7 still-red forms (confirmed
  standalone above for `stream_property`).
- This is a defect in the shared trace-diffing library (`lib_port_trace.sh`), not in rung10's or rung15's
  own box/builtin code, and not something introduced this session.
- Not mine to cure: I hold rung15 (hq_C), not the port-trace instrument itself, and `lib_port_trace.sh` is
  used across every language's port-trace gate (per `FINDING-2026-09-03-hq_T-all-seven-languages-already-
  emit-byrd-port-traces-only-the-flag-is-named-prolog.md`) — plausibly hq_T's (instruments) lane rather
  than hq_C's, but I'm not ruling on that; asked hq_C to route it (`q-prolog-rung-15-stream-character-and-
  byte-io-complete-iso-8-11-to-8-13`).

## Fix shape (not attempted here)

The ingredients the gate needs are already computed one loop earlier and just not consulted at line 130:
skip (or downgrade to informational) the zero-trace-lines UNPROVEN when `pert3`/`pert4` is `OK` **and** the
untraced rc is non-zero (a stable, trace-independent non-zero exit — i.e. "consistently refused before
producing ports," not "instrument silent while the program ran"). A witness that produces zero trace lines
at rc=0 would still, correctly, UNPROVEN.
