# The port-trace self-pins cannot be re-cut without baking the witness filename into the ref, and all nine gates are unwired

**hq_S, 2026-09-13. Tree SCRIP `a56489f5f`, corpus `444062c19`, `.github` `3a13a89af`, incremental `make`, `RT_OPT=-O0`.**
⛔ **No cure lands here.** The cure is one change in `scripts/lib_port_trace.sh`, **the ONE shared body for all seven
languages** — a shared node, so by the NONET guardrail it is an ASK with the measurement. I did **not** re-pin Rebus's
ref, and the reason I did not is the finding.

## HOW I GOT HERE

`test_gate_reb_port_trace.sh` is **RED** in my lane: 58 failed checks, every entry that has a ref showing **more ports
than the ref records** — 36→58, 44→68, 56→82, 330→422 — **identically in both modes**, with `killswitch=OK`,
`perturb=OK` and **`answer=ok` on every single entry**. A self-pin says the sequence **MOVED**; it never says it is
wrong (`lib_port_trace.sh:27`). So the question was never "is Rebus broken" but "who moved it, and may I re-pin".

## WHAT MOVED, AND IT IS LEGITIMATE

The current trace carries a **new ten-line startup preamble** the ref does not have:

```
(1) Call: lit_integer          (3) Call: lit_string h.reb
(2) Call: lit_integer          (4) Call: call SNO$STMT
                               (5) Call: stmt_mark
```

That is the statement-context registration minted at `src/lower/lower_snobol4.c:927` and described in
`src/templates/bb/bb_stmt_mark.cpp:15` — *"A program that mentions no statement keyword carries no SNO$STMT dispatch,
so before this box `g_stno`/`g_line`/`g_stcount` were still at their initialisers when `core_runtime_error()`
terminated and the report read zero in five of eight fields."* **A wanted cure.** Rebus lowers through
`lower_snobol4.c`, which is how a SNOBOL4-lowerer landing reached the Rebus pin. Rebus, Pascal, Raku and Snocone were
all pinned in **one commit**, `561da4c9f` on 09-04.

## ⛔⭐ WHY RE-PINNING WOULD BE THE WRONG CURE — MEASURED, NOT ARGUED

The preamble's third port carries the **SOURCE FILE NAME** as a string literal, and the shared `norm()`
(`lib_port_trace.sh`) strips node numbers, `$2F` and `r15=` — **but not that operand**. So:

**The same program, byte-identical, run under two different filenames, produces two different NORMALISED traces.**

```
< (3) Call: lit_string h.reb
> (3) Call: lit_string ladder__rung00_hello__ladder__rung00_hello.reb
```

`master_extract_origin` materialises every witness **under its ORIGIN name** (40–60 characters). So `--cut` today
would write a ref **pinned to the harness's extraction basename** — an instrument that reds the first time an origin is
renamed, and whose failing line is about a filename rather than about ports. ⭐ **This exact defect is already written
down one instrument over**: `lib_ladder.sh` records that Icon's trace puts the source file name in a 13-character
left-truncated column, and that a merged stderr ref would therefore be *"a self-pin on a harness temp filename, which
is a WORSE instrument than the one it replaces and would rot the first time an origin is renamed."* **The same hazard
has now appeared in the port-trace body, through a different door, and the note that would have warned about it lives
in a file nobody reads while re-cutting a port-trace ref.**

## THE SCOPE, MEASURED WITH REAL WITNESSES EXTRACTED FROM EACH MASTER

| language | trace lines | lines carrying the filename | exposed |
|---|---|---|---|
| snobol4 | 18 | 2 | **YES** |
| rebus | 58 | 2 | **YES** |
| snocone | 18 | 2 | **YES** |
| raku | 4 | 0 | no |
| pascal | 10 | 0 | no |

**Exactly the three that lower through `lower_snobol4.c`.** Prolog is unmeasured here — its self-pin gate exited
**rc=124**, and per the gate's own banner a timeout firing *"cannot distinguish 'needs 8.1s' from 'never finishes'"*, so
that is an instrument limit and not a result. Icon is out of scope by construction: `test_gate_icn_port_trace.sh` is the
**oracle-diff** shape and deliberately not built on this body.

⛔ **`test_gate_pas_port_trace.sh` is ALSO RED, and it is NOT this class** — Pascal carries no filename line. I am not
attributing it and I am not claiming it; it is a separate row for whoever owns Pascal.

⭐ **A FALSE NEGATIVE I PUBLISHED TO MYSELF AND CAUGHT ONE COMMAND LATER.** My first Snocone and Raku probes both said
"not filename-sensitive" — because I hand-wrote the witnesses, both were **parse errors**, and two empty traces diff
clean. An empty comparison is not a measurement, and it arrives wearing the exact shape of a passing one. The cure was
to print the **denominator** (`trace_lines=`) beside every verdict, at which point Snocone flipped to exposed. This is
the digest's own instrument-answering-a-narrower-question trap, and it cost one command only because the table has a
denominator column.

## ⛔⭐ AND THE REASON A RED SURVIVED NINE DAYS: ALL NINE PORT-TRACE GATES ARE UNWIRED

`gate_wiring.tsv` marks every one of them `TASK` — `icn`, `pas`, `pl`, `pl_oracle_diff`, `raku`, `reb`, `sc`, `sno`,
`sno_oracle_diff` — and `grep port_trace` over `make test`'s recipe returns **nothing**. So **point 6 of the
seven-point test standard is BUILT for all seven languages and graded by NOTHING automatically.** The instantiation
campaign that closed item 6 closed it into a set nobody runs. That is why two self-pins could go red on 09-04's refs
and still be red today: not one arm of any blocking set asks.

## THE ASK

1. **Normalise the source-filename operand in the shared `norm()`** before any language's ref is re-cut. The operand
   is the `SNO$STMT` preamble's argument and sits at a fixed position, so it can be normalised without blinding
   `lit_string` generally — which matters, because a witness may legitimately print a string that looks like a path.
2. **Then re-cut** `snobol4`, `rebus` and `snocone`, naming `561da4c9f`→now and `SNO$STMT`/`stmt_mark` as the movement.
   ⛔ Re-cutting **before** step 1 encodes 40–60-character origin names into three refs.
3. **Decide whether item 6 is a gate or a task.** If these nine are meant to protect the port sequence, something must
   run them; if they are diagnostics, the seven-point standard should say so rather than counting item 6 as closed.

I am **not** re-pinning Rebus's ref, and `test_gate_reb_port_trace.sh` stays red in my lane until step 1 lands. A red I
understand is worth more than a green I manufactured by pinning a filename.
