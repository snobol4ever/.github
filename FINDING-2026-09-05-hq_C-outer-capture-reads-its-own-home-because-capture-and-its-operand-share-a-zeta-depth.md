# FINDING 2026-09-05 hq_C — the outer capture reads its own home slot because the capture node and its own operand sit at the same zeta depth

**Seat:** hq_C · **Mode:** QUARTET (Lon 2026-09-04 21:09, "HQs take the toughest") · **Tree:** SCRIP `a5085b19d`

## 1. The trigger is an alternation inside the captured group — nothing else

Two lines apart, and the failing one is the whole defect:

```
LIST = ",a"
LIST POS(0) "," (LEN(1) (BREAK(",") | REM)) . COMMON   ->  SCRIP COMMON=[]   ORACLE COMMON=[a]   ⛔
LIST POS(0) "," (LEN(1)  REM             ) . COMMON   ->  SCRIP COMMON=[a]  ORACLE COMMON=[a]   ✅
```

No pattern-valued variable, no function, no BAL, no includes. The row's earlier framing named a
pattern-valued variable as the ingredient; the narrowed witness above shows an **inline alternation** is
sufficient. The inner capture is always correct — only the outer one is lost.

## 2. The site, and what is NOT the bug

`src/templates/bb/bb_match_capture.cpp:30-31`:

```c
#define writehome() (_.op_zres ? ZRESD(0)   : FR(_.op_off))   /* the node's OWN result slot */
#define readhome()  (_.op_zres ? ZOPD(1, 0) : FR(_.op_off))   /* operand 1's slot           */
```

`ZRESD(w)` resolves the node's own result; `ZOPD(k,w)` the k-th operand's (`x86_asm.h:981,987`).

⛔ **The write/read asymmetry is BY DESIGN and is not the defect.** I assumed it was, and so does the
dispatch brief. The **passing** sibling is asymmetric — `write=[rsp#+0]`, `read=[rsp#+16]` — and correct. The
**failing** one is *symmetric*: both resolve to `[rsp#+0]`. The bug is the collapse, not the asymmetry.

⛔ **Second killed hypothesis:** "`op_zread[1]` is an unassigned sentinel defaulting to 0." Also false —
`op_zkind[1]=63` in *both* witnesses, so the producer is found and the offset is genuinely computed to zero.
⭐ Keep the near-miss anyway: `g_zd_read[]` initialises to **0** while `g_zd_kind[]` initialises to **-1**
(`emit.cpp:3267`), so **0 is simultaneously a legal offset and the default**. Nothing can range-check
`op_zread[k]` for "was this set" — only `op_zkind[k] != -1` answers that. It is not what bit here, but it is
a live sentinel-collides-with-a-legal-value trap sitting in a hot path.

## 3. ⭐ The arithmetic, measured

`emit.cpp:3271` computes `g_zd_read[_zj] = zd_out[i] - zd_out[_k] + _xh`. Instrumented on both arms:

```
good:  capture IR_MATCH_ASSIGN_COND zd_out=48   operand-1 producer IR_MATCH_ASSIGN_SAVE zd_out=32   xh=0  -> read=16  ✅
bad:   capture IR_MATCH_ASSIGN_COND zd_out=32   operand-1 producer IR_MATCH_ASSIGN_SAVE zd_out=32   xh=0  -> read= 0  ⛔
```

**With the alternation present, the capture node and its own operand's producer occupy the same zeta depth.**
The read offset is therefore 0, `readhome()` becomes byte-identical to `writehome()`, and the capture reads
back its own banked start cursor instead of the group's result — so `COMMON` is null. That is precisely the
"clobbered banked start cursor" the row was named for, now with the numbers rather than the symptom.

## 4. Where the cure is, and where it is not

The narrow remaining question: **why does the capture fail to advance past its `IR_MATCH_ASSIGN_SAVE` when
the captured group contains an alternation?** Start at `zd_k()` — `IR_MATCH_ASSIGN_COND` contributes **0**,
`IR_DISJUNCTION` with operands contributes **32** — and at how `zd_out` accumulates across disjunction arms.

⛔ **Do not cure this in `bb_match_capture.cpp` by making `readhome()` dodge the alias.** That treats the
symptom and leaves the depth wrong for every other `ZOPD` consumer — `bb_binop_arith`, `bb_binop_relop_val`,
`bb_match_break/any/notany` all read operands the same way.

## 5. Why this row matters beyond its own witness

Both remaining ERROR-246 stack overflows in the gimpel suite (`HYPHENAT_driver`, `LINE_driver`) trace to it:
`OR.sno` relies on the outer capture to set `COMMON`; `COMMON` comes back empty, the next statement consumes
the wrong text, and `OR/OR_EXTRACT` recurse forever. Traced live: at `ORX_5` the oracle has `COMMON=[a]
SUBLIST=[,]` while SCRIP has `COMMON=[] SUBLIST=[,a]`. ⭐ Note the failure mode — **a silently wrong capture
became an infinite recursion three statements later**, which is why this surfaced as a stack overflow and was
triaged as one for a long time.
