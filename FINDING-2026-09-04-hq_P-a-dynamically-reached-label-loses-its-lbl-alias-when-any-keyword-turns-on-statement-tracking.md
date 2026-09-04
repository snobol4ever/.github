# FINDING — a dynamically-reached label loses its `LBL__` alias when any keyword turns on statement tracking

**Date:** 2026-09-04 · **Seat:** hq_P (QUARTET) · **Row:** `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect`
**Landed:** SCRIP `e86a9708e` · corpus `8e34e5788` · supersedes the OPEN §3 of
`FINDING-2026-09-03-seat03-arithmetic-errors-bypassed-core-runtime-error-two-cures-landed-one-emitter-bug-open.md`

## Headline

seat03 left this class root-caused-but-open with a named minimal pair and a named suspect. **Both were wrong,
and the way they were wrong is the transferable part.** The suspect was "something about the extra intervening
statement"; the actual trigger is the single keyword `&LASTNO`. The minimal pair was not minimal — it differed
in *two* places at once, and the difference everyone was looking at was the inert one.

One token in `src/emitter/emit.cpp` cures it. The SNOBOL4 master goes **1696 → 1698, FAIL=0 in both modes**.

## 1. The pair was not minimal, and that is why the hypothesis survived

seat03's pair was `keyword_replace_1` (works) vs `keyword_replace_2` (fails), described as "identical prefix;
`keyword_replace_2` has one extra statement (`OUTPUT = "AFTER"`)". The prefixes are indeed identical — but the
**handler bodies also differ**, and that second difference was never listed:

```
keyword_replace_1   H  OUTPUT = "PREV=[" SETEXIT("") "]"
keyword_replace_2   H  OUTPUT = "HANDLER " &ERRTEXT " S" &LASTNO
```

A 2×2 over the two variables settles it in four compiles — `LBL__H:` defined or not:

| | handler uses `SETEXIT` | handler uses `&LASTNO` |
|---|---|---|
| **no** intervening statement | DEFINED | ⛔ DROPPED |
| **with** intervening statement | DEFINED | ⛔ DROPPED |

The intervening statement is **inert in both directions**. A nine-variant sweep over handler bodies then names
the trigger exactly: `OUTPUT = "X"`, `"A" "B"`, `&ERRTEXT`, `SETEXIT("")`, `SIZE("ab")`, `D`, `Q = 1` all keep
the label; **only `&LASTNO` drops it.** Not keywords in general — `&ERRTEXT` is fine. Not function calls.

⭐ **The lesson: a pair with two differences is not a witness, it is a coincidence with a story attached.**
Ablate to a pair that differs in exactly one place, or run the matrix. seat03's own handoff had already warned
that a characterization is "a strong prior, not a proof" — this is that warning collecting on itself.

## 2. Mechanism

`&LASTNO` sets `g_sno_uses_stmtkw`, which makes `lower_snobol4.c` prepend a per-statement `SNO$STMT` hook —
`IR_LIT_INTEGER`, `IR_LIT_INTEGER`, `IR_CALL` — **between the label anchor and the statement body**:

```
without &LASTNO:   anchor(IR_GOTO) -> sbeg(IR_STATEMENT_BEGIN) -> body
with    &LASTNO:   anchor(IR_GOTO) -> num(IR_LIT_INTEGER) -> lnn -> hook(SNO$STMT) -> sbeg -> body
```

The label's proc-table alias is bound in `src/driver/scrip.c` by walking the anchor forward past
`IR_SUCCEED`/`IR_FAIL`/`IR_GOTO` to the first real box. That walk does not know about hooks, so the alias lands
on `num` (`IR_LIT_INTEGER`, op 49) instead of `sbeg` (`IR_STATEMENT_BEGIN`, op 116). Measured directly:

```
h_setexit (works)   [LBLDIAG] alias LBL__H -> node op=116 ... APPLIED
h_lastno  (fails)   [LBLDIAG] alias LBL__H -> node op=49  ... never APPLIED
```

`num` is then never emitted. `codegen_flat_chain_body` uses a **statement-seeded** walk whenever the graph holds
any `IR_STATEMENT_BEGIN`: it seeds `entry`, then every `IR_STATEMENT_BEGIN` in graph order. For a label reached
only *dynamically* — `SETEXIT(.H)` passes a NAME, never a static `:(H)`/`:S(H)`/`:F(H)` edge — nothing reaches
the hook, because the hook sits **upstream** of the `IR_STATEMENT_BEGIN` that the seeding does find. The body is
emitted (seeded as a statement); the anchor prologue is not; the alias silently never applies.

The seeding that would have covered it — the group anchors, which are exactly the label landings
(`zls_group_mark_anchor`, `lower_snobol4.c:2042`) — was gated `!_stmt_seed`, on the reasoning that statement
seeding already covers everything. **True of the statement BODIES, false of the anchor PROLOGUE.**

⛔ **The failure is silent by construction, and asymmetrically so:** the proc table still emits `.quad LBL__H`
from the same `proc_entry_node`, so the *reference* survives while the *definition* vanishes. m4 dies at `ld`
(`undefined reference to LBL__H`); m3 dies at `rt_label_get_fn`. Nothing in the emitter notices that it wrote a
reference to a symbol it declined to define.

## 3. The cure, and why it is this one rather than the other one

```diff
-      if (g_emit_cfg && entry_is_own_graph_root && !_stmt_seed) { int _gc = zls_g_group_count(g_emit_cfg); ...
+      if (g_emit_cfg && entry_is_own_graph_root) { int _gc = zls_g_group_count(g_emit_cfg); ...
```

The obvious alternative — teach the alias walk to skip the hook chain too, so the alias lands on the
`IR_STATEMENT_BEGIN` that *is* emitted — **links, and reports the wrong answer.** `rt_stmt_enter` does
`g_lastno = g_stno`, so a handler entered *through* its own hook reads `&LASTNO` = the statement that erred.
Aliasing past the hook would skip that and report the previous statement. The oracle refs grade exactly this
distinction (`keyword_replace_2.ref` ends `S4`), so the two cures are separated by the witness, not by taste.

**Blast radius: SNOBOL4/Snocone only.** `lower_snobol4.c` is the sole caller of `zls_group_mark_anchor`, so
`zls_g_group_count()` is 0 for every other frontend and the ungated loop body does not execute — the
SHARED-NODE VERDICT SCOPE obligation is discharged by construction, not by hope.

## 4. Board

Incremental `make`, `RT_OPT=-O0`. SNOBOL4 master, 1736 entries, SCRIP `e86a9708e` / corpus `8e34e5788`:

```
mode-3 (--run):     PASS=1698 FAIL=0
mode-4 (--compile): PASS=1698 FAIL=0 SKIP=0   MISSING=0
master: xfail=61  xpass=0
```

Two entries promoted (both XPASS after the cure, an XPASS left standing being its own defect):

- `keyword_replace_2` — was blocked exactly on this label drop.
- `keyword_replace_3` — **not in seat03's list of three.** Its own banner had predicted it: *"RED BY DESIGN
  beyond the trap rung … This row is what will notice when that is cured."* It noticed. A witness written to
  detect a future cure did its job years-of-sessions later, which is an argument for writing them that way.

## 5. Still open — `:(CONTINUE)` is unimplemented (a DIFFERENT defect, not this one)

`keyword_replace_branch_10` and `_11` were the other two of seat03's three. They **advance past the label drop**
— `LBL__H`, `LBL__S5`, `LBL__S7` all define and link now — and stop on something else entirely:
`transfer to undefined label: CONTINUE`. `:(CONTINUE)` is SPITBOL's resume-transfer out of a `SETEXIT` handler
(resume the interrupted statement's own success/failure continuation); SCRIP treats `CONTINUE` as an ordinary
label and raises Error 38. That needs the error-return continuation captured at the trap — a separate class row,
not a tail of this one. Refs, for whoever takes it: `branch_10` → `HANDLER S4 / MID / AFTER` (trap is one-shot);
`branch_11` → `HANDLER S4 / MID / HANDLER S6 / AFTER` (handler re-arms).

## 6. An instrument lesson that cost a torn suite, and is worth more than the bug

**`corpus/tests/snobol4/ALL.ref` contains one NUL byte, so `grep` silently switches to binary mode and prints
nothing** — including for `grep -c`. Two greps for the entry banners came back empty and were read as *"ALL.ref
carries no banners"*, contradicting the INTERIM PROMOTION PROTOCOL's own text, which says a marker lives in
ALL.sno **and ALL.ref** and ALL.xfail. The first promotion pass therefore touched three homes and left ALL.ref
torn.

⭐ Three things are worth keeping from that:

1. **This is the `command -v` class again** (an oracle probe that answers a narrower question than the one you
   meant, silently, with a well-formed empty answer). It is now the third recorded instance in this project, in
   a third instrument. The shape recurs faster than any individual cure for it.
2. **Documented fact was overridden by an unverified empty grep.** The protocol said four homes; the grep said
   two; the grep won because it looked like measurement. It was measurement — of the wrong file mode.
3. **The protocol's own guard caught it immediately and loudly** — `read_suite` raised
   `family.ref banner mismatch at seq 1685` rather than degrading — which is exactly why it demands the proof be
   run *on the result*, in the same commit. A cheaper habit would have shipped an unreadable master to every seat
   on the box, which is precisely the 40-minute outage of 2026-09-01 that caused the protocol to exist.

✅ Use `grep -a` on `ALL.ref`, or read it in Python. Both promotions are proven in-commit: `read_suite` rc=0 /
1736 entries, and `util_census_optimizer_bypass --only` clean on all three arms (default · `SCRIP_OPT` ·
`SCRIP_ZD`) for both entries.
