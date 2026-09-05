# FINDING — a deferred pattern's live depth is a RUN-TIME VALUE, so no static offset can reach past it

**Seat:** hq_C · **Date:** 2026-09-05 · **Row:** `snobol4-outer-capture-inside-a-function-over-callers-local-pattern-variables`
**Tree:** SCRIP `2243452ad` (pushed; graded as `0891a406d` rebased onto `94f894b80`, re-proved after the rebase) · corpus `911c49b77` · .github `cdff151c` · `RT_OPT=-O0` · incremental `make`

## The claim

An outer conditional-assignment capture whose banked start cursor is separated from its commit by an
`IR_MATCH_DEFER` read the wrong stack slot — silently empty in the `LEN(1)` shape, and the loud
`rt_dcap_pump: CORRUPT CAPTURE ENTRY refused` in the `BAL` shape. The cure is one token in
`src/emitter/emit.cpp`: the capture-nesting hazard scan must treat **every** defer as a hazard.

## What was already known, and what was wrong about it

The row's baton recorded a sweep of the `_xh` hop constant for `IR_MATCH_DEFER` and concluded:

> No constant is correct — 16 and 0 each fix a disjoint half. That is not a tuning problem, it is a
> statement about the emitted code: `bb_match_defer` leaves a DIFFERENT number of live bytes on
> different exit paths into the capture.

The observation was right and the **inference was too weak**, which is why it proposed two cures that
cannot work: "make the two exit paths uniform" and "model `_xh` per predecessor edge". Both assume the
number is statically knowable once you look hard enough at the emitted block.

⭐ **It is not knowable at all.** The deferred pattern is selected by a *variable's value* at run time,
entered with `jmp rax`, and its own retained γ frame stays live by Byrd-box design so that β can
backtrack into it. The live depth at the consumer is therefore a property of whatever pattern the
variable happened to hold.

**The decisive witness — ONE compiled capture node, two run-time values:**

```
	DEFINE("F(LIST,K)SEIZE,ANC,COMMON,IC")
	OUTPUT = F(",ABLE,ACTOR",1)
	OUTPUT = F(",ABLE,ACTOR",2)	:(END)
F	ANC = POS(0) ","
	SEIZE = REM
	EQ(K,1)	:S(GO)
	SEIZE = BREAK(",") | REM
GO	LIST  ANC  (BAL . IC  SEIZE) . COMMON	:F(FRETURN)
	F = "K=" K " COMMON=[" COMMON "] IC=[" IC "]"	:(RETURN)
END
```

gdb on the m4 binary, breaking at the single `n65_match_assign_cond_α`:

```
  bank@0x7ffffffedf20   CAPTURE rsp=0x7ffffffede70   NEEDED_OFFSET=176   (emitted reads 48)
  bank@0x7ffffffedf20   CAPTURE rsp=0x7ffffffede40   NEEDED_OFFSET=224   (emitted reads 48)
```

Same instruction, same program, two different correct answers. **No static number and no per-predecessor
model can satisfy both.** That kills cure shapes 1 and 2 as a class, not as a tuning failure.

## The actual mechanism

`frame_need_of()` → the `SCRIP_CAP_NEST` scan in `emit.cpp` decides whether a capture's banked cursor is
addressed rsp-relative (`ZRESD`/`ZOPD`, offset computed at the `_xh` hop) or frame-relative (`CFC(0)`,
rbp-based and immune to rsp drift). Its guard read:

```c
if (_m && (_m->op == IR_MATCH_ARBNO || (_m->op == IR_MATCH_DEFER && !_m->pat_static) || _m->op == IR_MATCH_VALUE)) h = 1;
```

`SCRIP_CAP_NEST_DIAG=1` on the failing witness prints the exempted node directly:

```
[CAPNEST] nd=0x8262760 save=0x82627b0 cfg_n=80 si=49 ci=48 ext=55
[CAPNEST]   scan[54] op=70 pat_static=1        <- IR_MATCH_DEFER, exempted
```

⛔ **The same question was already answered the other way, three hundred lines up.** `earn_hazard_in()`:

```c
if (nd->op == IR_MATCH_DEFER) { const char * _e = getenv("SCRIP_DEFER_HAZ_STATIC"); if (_e && _e[0] == '1' && nd->pat_static) return 0; return 1; }
```

A defer is a hazard **unconditionally**; the `pat_static` exemption is behind a **default-off** env var.
The CAP_NEST scan hard-coded the exemption that its own neighbour deliberately keeps switched off.
`SCRIP_EARN_DIAG=1` shows both verdicts on one tree: `[EARN] op=70 need=1 haz=1` for the defer itself,
`[EARN] op=61 need=0 haz=0` for the capture that steps over it.

⭐ **`pat_static` is not a claim about the emitted frame.** It means "this name is bound to one constant,
defer-free pattern" — a fact about the pattern's *shape*, read as a fact about its *stack cost*. It is
not even reliable on its own terms: in the witness above `SEIZE` is assigned two different patterns and
`pat_static` still reports **1**.

## The cure

```diff
-if (_m && (_m->op == IR_MATCH_ARBNO || (_m->op == IR_MATCH_DEFER && !_m->pat_static) || _m->op == IR_MATCH_VALUE)) h = 1;
+if (_m && (_m->op == IR_MATCH_ARBNO || _m->op == IR_MATCH_DEFER || _m->op == IR_MATCH_VALUE)) h = 1;
```

The capture moves to the frame cell, exactly as the ARBNO and FENCE hazards already do:

```
before:  n39_match_assign_save_α:   mov dword ptr [rsp + 0],   r14d      n44: mov eax, dword ptr [rsp + 48]
after:   n39_match_assign_save_α:   mov dword ptr [rbp + -64], r14d      n44: mov eax, dword ptr [rbp + -64]
```

It is surgical: the **inner** capture in the same statement does not cross the defer and keeps its
`[rsp + 16]` read. Zero `x86_bomb` in the emitted output — the neighbouring
`op_cap_frame_off == -1` bomb arm is not reached by any graded entry.

## Grading — all on the merged tree, A/B with the one token as the only difference

| arm | m3 | m4 |
|---|---|---|
| DONE-WHEN, cure reverted | RED `rt_dcap_pump` refusal | RED `rt_dcap_pump` refusal |
| DONE-WHEN, cure applied | `COMMON=[ABLE] IC=[A]` ✅ | `COMMON=[ABLE] IC=[A]` ✅ |

- **SNOBOL4 master (re-measured AFTER the 10:34 CDT oracle swap, md5 bc694a0cc699):** m3 PASS=1801 FAIL=0 · m4 PASS=1801 FAIL=0 SKIP=0 · ast 28/28 · MISSING=0 · ✅ GATE OK
- **Baseline master, same tree, cure reverted:** m3 1801/0 · m4 1801/0 · xfail 50/49 · xpass 3/4 — **identical**
- **Icon master board:** m3 599 / m4 599 vs floor 596, watermarks held (754 entries)
- **Snocone smoke:** 5/5 · **`strip_comments.py --check`:** clean · **`make test`:** rc=0
- Predecessor row `snobol4-outer-capture-over-a-group-containing-a-pattern-valued-variable` DONE-WHEN: still green

⭐ **The master board is a no-op arm, and saying so is the point.** The cure changes no master entry in
either direction. Its causal evidence is the witness A/B and the gimpel cell, never the totals.

## Population actually freed — re-measured, not inherited

`corpus/packages/snobol4/gimpel`, m3, same tree, one token apart:

```
baseline   pass=72  err246=9  wrong=46
cured      pass=73  err246=6  wrong=48
```

- **`ORVISUAL_driver` newly PASSES.** Nothing that passed before stopped passing.
- **Three programs left the ERROR-246 class**; two of them land as wrong answers rather than passes.
- **`OR_driver`** goes from unbounded recursion to **terminating**, 3 wrong lines of 9 — real movement,
  not a pass. Its residue is a different defect.
- ⛔ **`HYPHENAT_driver` and `LINE_driver` are UNCHANGED — still ERROR 246.** The row's own GOAL named
  them as what this defect burns. That attribution is **refuted for these two**, exactly as the
  predecessor row's headline attribution was refuted before it.

⭐ **Twice now on this row's lineage, a cure has been correctly measured, honestly graded, and delivered
a different population than the one that justified it.** The DONE-WHEN grades the witness; it never
grades the claim. Re-measure every unblock.

## For the next actor

- The same `!pat_static` exemption appears at `emit.cpp:2258` (`if (m->op == IR_MATCH_DEFER && !m->pat_static) return 1;`)
  and, inverted, at `:2170`; the ARBNO body-defer-unsafe scan at `:1180` carries it too. **I did not touch
  them** — no witness, so no change. They are the obvious place to look when the next defer-crossing
  consumer misreads its operand, and the argument above (a defer's depth is a run-time value) applies to
  each of them unaltered.
- `g_zd_read[]` is initialised to **0** while `g_zd_kind[]` is initialised to **-1**, so a computed read
  offset of 0 is indistinguishable from "never set". Only `op_zkind[k] != -1` answers that question.
