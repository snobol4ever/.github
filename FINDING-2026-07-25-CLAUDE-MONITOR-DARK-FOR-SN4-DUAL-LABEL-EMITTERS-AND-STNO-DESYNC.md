# FINDING 2026-07-25 (Claude) — THE 2-WAY SYNC-STEP MONITOR IS DARK FOR SNOBOL4 `spl` vs `scr`: IT FALSE-POSITIVES ON A 3-LINE HELLO-WORLD

**Why this matters more than the bug that found it:** `RULES.md`'s FIRST ABSOLUTE RULE is MONITOR-FIRST
BUG-FINDING — *"the bug is NOT hunted by reading code, guessing, or scattering print statements"* — and it
names the escape clause: *"If the monitor is dark for the mode under test, REINSTATING IT (the MON-RE rung) is
the prerequisite and comes first — a working monitor is worth more than any single bug fix."*
**It is dark. Every SNOBOL4 divergence hunt is currently running without its mandated primary tool.**

---

## 1. THE PROOF (falsification test, not an impression)

```bash
printf '\tOUTPUT = 1\n\tOUTPUT = 2\nEND\n' > triv.sno
PARTICIPANTS="spl scr" bash scripts/test_monitor_3way_sync_step_auto.sh triv.sno
```
Both engines print exactly `1\n2\n`. The monitor nevertheless reports:

```
[ctrl] DIVERGE step 2
| step | stno | spl              | scr              |
| 1    | 1    | LABEL stno=INT=1 | LABEL stno=INT=1 |
|>2    | 1    | LABEL stno=INT=2 | LABEL stno=INT=3 |
```

Same result on `claws5-match.sno` (byte-identical under both modes — verified independently this session):
`spl LABEL stno=INT=2` vs `scr LABEL stno=INT=8`. And on `claws5.sno` (which DOES have a real bug) the
monitor diverges at **step 2 on statement 1**, an unrelated statement, long before the actual fault — so it
brackets nothing.

⇒ **The monitor cannot presently distinguish "identical" from "divergent" for SNOBOL4.** Its output on any
`spl`/`scr` pair must be treated as UNINFORMATIVE until MON-RE lands. It is not merely noisy — it reports
DIVERGE on provably identical programs, which is the failure mode that silently sends a session to the wrong
statement. (`monitor_sync_bin.py`'s own comments are emphatic that this must not happen: *"a LABEL divergence
IS the divergence … do not filter LABELs out of the comparison"* — correct policy, but it presumes the two
LABEL streams are comparable, and they are not.)

## 2. ROOT CAUSE — TWO INDEPENDENT, UNSYNCHRONIZED `LABEL` EMITTERS ON THE SCRIP SIDE

`grep -rn mon_emit_label_bin src/` finds **two** producers:

1. **Emitted-code tap** — `src/emitter/emit.cpp:925`, fired **only on `IR_GOTO`**, guarded by
   `MONITOR_BIN` + `g_emit.op_stno > 0`, emitting via `emit_mon_label_tap` (`src/templates/bb_succeed.cpp:18`).
   `op_stno` is set at `emit.cpp:797` from `IR_LIT(nd).ival` — a field that is **overloaded** (the very next
   line reuses the same `ival` as `op_ival`), so it is a trustworthy statement number **only on GOTO nodes**.
2. **Driver-side AST walk** — `src/driver/driver_call.c:161`, one call per `TT_STMT` reading a `:stno`
   attribute, and `continue`-ing (emitting NOTHING) for `TT_CHOICE`/`TT_UNIFY`/`TT_CLAUSE` subjects.

SPITBOL emits a LABEL at **every statement entry**. Neither SCRIP producer matches that contract, and with two
of them live the stream is order-dependent.

**Measured corroboration:** `MONITOR_BIN=1 scrip --compile triv.sno` emits **exactly two taps, `stno` 1 and 2 —
CORRECT**, matching SPITBOL. But the monitor runs `scrip --run` (mode 3 — see
`test_monitor_3way_sync_step_auto.sh:190`) and mode 3 yields `1, 3`. **So the two modes do not agree on the
monitor wire either — a MODE34-IDENTICAL violation in the instrumentation itself**, with mode 4 being the
correct one. Note `--dump-ast triv.sno` shows **no `:stno` attributes at all**, so the driver-side producer
would read 0; the observed `3` comes from neither producer cleanly, which is itself diagnostic.

## 3. THE SANCTIONED FALLBACK IS ALSO ABSENT

`RULES.md` offers: *"The offline alternative when no barrier is wanted is the harness `probe.py`
(`&STLIMIT`+`&DUMP=2` frame replay, bisect-divergence) — same bracket theorem, replay instead of live wire."*
**`probe.py` does not exist anywhere in the tree** (`find / -name probe.py` returns only unrelated urllib3
files). So the documented Plan B is unavailable too. Either restore it or strike it from RULES.md — a rule
pointing at a non-existent tool is worse than no rule.

## 4. WHAT WAS DONE INSTEAD (and why it was legitimate)

The claws5 hunt proceeded by **input bisection to a minimal deterministic repro** — which satisfies the same
BRACKET THEOREM the monitor exists to provide (narrow the interval until the fault is isolated to one
statement/one token), then gdb. It found the failing ordinal exactly and excluded five candidate mechanisms.
See `FINDING-2026-07-25-CLAUDE-SN4-CAPTURE-START-ZEROED-AT-20TH-ARBNO-ITERATION.md`.
**This is a substitute, not a replacement:** bisection needs a program whose input can be shrunk, which is
luck. The monitor works on any divergence. MON-RE remains owed.

## 5. PROPOSED MON-RE LADDER (not started)

- **MON-RE-1** Rule the LABEL contract explicitly: *one LABEL per executed statement, stno = SPITBOL's
  counting* (comment lines `*` skipped, `-` directives skipped, all other lines including blanks increment —
  the rule `scripts/monitor/build_stno_map.py` already encodes). Write it into the monitor design doc.
- **MON-RE-2** Collapse to ONE producer honoring that contract. The `IR_GOTO`-only tap cannot (statements not
  lowering to a GOTO emit nothing); a statement-entry emission point is required. Delete or gate the
  `driver_call.c` producer so two streams cannot interleave.
- **MON-RE-3** Prove mode-3 ≡ mode-4 on the wire (this is MODE34-IDENTICAL applied to instrumentation).
- **MON-RE-4** **Falsification gate — the piece whose absence let this rot silently:** a test asserting the
  monitor reports NO divergence on a set of programs known byte-identical (`triv.sno`, `claws5-match.sno`).
  A monitor that cannot pass a hello-world must fail its own gate loudly. Add to the Session Setup gate list.
- **MON-RE-5** Restore `probe.py` or strike the reference from RULES.md.

## 6. HONEST LIMITATION

Root cause is established for the *structure* of the defect (two producers, GOTO-only tap, mode-3/mode-4
wire disagreement). The exact provenance of mode 3's `stno=3` on `triv.sno` was **not** run to ground — that
is MON-RE-2's first measurement, not a settled fact here. No monitor code was changed this session.
