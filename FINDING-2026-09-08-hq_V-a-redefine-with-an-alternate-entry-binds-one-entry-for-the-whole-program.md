# FINDING 2026-09-08 hq_V — a runtime `DEFINE` with an alternate entry point binds ONE entry for the whole program

**Seat** hq_V · **Mode** NONET · **Tree** SCRIP `c707c9762` (clean) · **Oracle** `sbl -bf`
**Status** ⛔ **NOT CURED.** Diagnosis is exact and three cure attempts are measured dead ends, named below so
nobody spends the window re-walking them. Row `snobol4-gimpel-recursive-list-functions-overflow-the-call-stack-where-spitbol-completes`.

## The claim, measured

`DEFINE` is an **executable statement**: each execution binds the function's entry point. We bind once,
at compile time, and the **last `DEFINE` in program text wins for every call in the program**.

```
	DEFINE('F(X)')                  :(FEND)
F	OUTPUT = 'A ' X                 :(RETURN)
F1	OUTPUT = 'B ' X                 :(RETURN)
FEND
	F('one')
	DEFINE('F(X)', 'F1')
	F('two')
	DEFINE('F(X)', 'F')
	F('three')
END
```

| | `sbl -bf` | SCRIP m3 **and** m4 |
|---|---|---|
| `F('one')` | `A one` | `A one` |
| `F('two')` | `B two` | **`A two`** |
| `F('three')` | `A three` | `A three` |

With only the first two `DEFINE`s the reading is `B one` / `B two` — i.e. the **last** binding, applied
retroactively to a call that ran before it. Both modes fail identically, so this is not a mode split.

## Where it is lost — the dentry table binds by NAME, never by the DEFINE's own entry

`src/driver/scrip.c` (~line 1418) builds `bbg->dentry_*`, the table `emit.cpp:1260` reads to set
`g_emit.lbl_t0` — "this DEFINE's entry" — for each bind node. For every `ir_define_is_bind` node it looks
the function up in `s2->proc_table` **by name** and takes that one proc's entry. It never consults the
entry the lowerer attached to the bind node: `sno_bind_attach_entry` (`lower_snobol4.c`) pushes the entry
as an `IR_LIT_NAME` operand with `pat_static = 1`, and `sno_parse_define` defaults `d->entry` to the
function name, so **every bind node already carries its own correct entry** and the driver ignores it.

Emitted assembly confirms it — all three sites load the same activation:

```
lea r9, [rip + F_α]   ;  call rt_define_site@PLT      (x3, identical)
```

⭐ **The mechanism designed for exactly this problem exists and is dormant.** `bb_define.cpp` carries
`M4-BODY-SEAL (term 3): body_cell$<FN> <- &LBL__<this DEFINE's entry>, so a call reads the binding in force
when it runs rather than a baked winner`, and the activation really does read `body_cell$F`. In the witness
above **no store to `body_cell$F` is emitted at all**, because the seal is gated on `_.lbl_t0`, which is
NULL for the reason above. The runtime half is fine too: `rt_define_site` already rebinds `p->fn` and sets
`p->redefined`.

## Three measured dead ends — do not re-walk these

1. **`SCRIP_NO_TINY=1`** (disable the direct-call tiny shim): reading unchanged. The direct-call fast path
   is **not** what bakes the winner.
2. **Ungating the M4-BODY-SEAL** from `bb_tiny_shim_ok` in `bb_define.cpp`: reading unchanged, because
   `_.lbl_t0` is NULL regardless of the gate. ⛔ Note both this and any change that makes
   `bb_tiny_shim_ok` return *false* SUPPRESS the very seal the cure needs — the predicate guards it.
3. **Resolving the bind's own entry operand** through the `LBL__<entry>` `proc_table` search, mirroring the
   `IR_GOTO_DEFERRED` arm a few lines below in the same loop: reading unchanged, and `r9` still loads
   `F_α`, so the lookup did not resolve. **That is the next question:** whether `LBL__F1` is absent from
   `proc_table` for a label that is only a DEFINE entry and never a branch target, or whether the entry
   operand does not survive to the driver.

All three were reverted; the tree named above is clean and the witness above still reproduces on it.

## Why it matters beyond one fixture

Two snoflake reds reach `ERROR 246 -- stack overflow` through this. `COPYL.INC` (Gimpel) is the pattern
in the wild: it re-`DEFINE`s **itself** with an alternate entry to get a memo table set up once —
`DEFINE('COPYL(L)', 'COPYL_1')` — then calls itself and restores the original binding on return. With one
entry baked for the whole program that re-entry trick cannot work.

⛔ **`gimpel-conversions` is NOT this bug and needs its own diagnosis** — `SPELL.INC` recursion was my first
suspicion and it is **wrong**: in-place pattern replacement is measured CORRECT (`N RTAB(3) . M =` gives
`N=976 M=1`, matching the oracle, as does `P LEN(1) . Q =`). Its overflow is still unexplained.
