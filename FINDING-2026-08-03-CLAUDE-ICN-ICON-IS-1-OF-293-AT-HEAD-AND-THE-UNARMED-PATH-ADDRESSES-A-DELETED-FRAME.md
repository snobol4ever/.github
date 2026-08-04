# FINDING s207 (2026-08-03) — ICON IS 1/293 AT HEAD; THE UNARMED PATH ADDRESSES A FRAME CARVE-KILL DELETED; AND "ARM EVERYTHING" IS MEASURED INERT

**Session:** s207 · **Tree:** SCRIP `4d902148` (clean, == origin, verified `handoff_status.sh`) · **RT_OPT=-O0**

---

## 1. THE WATERMARK IS NOT 184/79/30. IT IS 1/262/30.

Re-derived fresh from `scripts/test_icon_all_rungs.sh`, corrected predicate (`grep -c '^PASS'`, anchored —
the s203 instrument law, because `FAIL=` also matches `XFAIL=`):

| tree | Icon `--run` suite |
|---|---|
| s206 cursor CLAIMS (`dda156eb`) | 184 / 79 / 30 |
| **HEAD `4d902148` MEASURED** | **1 / 262 / 30** |

`procedure main(); write("hello"); end` **SEGVs (rc=139)**. This is not a harness artifact — it reproduces
by hand in mode 3. `--compile` (mode 4) exits 0 and emits an assemblable `.s`, so the defect is in the
emitted code, not the compiler driver.

⛔ **NO KILLSWITCH RECOVERS IT.** Measured, all rc=139 unless noted:
`SCRIP_GLUEO=0` (rc=134, stack smashing) · `SCRIP_GLUE_SYM=1` · `SCRIP_BB_ALLOC=0` · `SCRIP_STMT_FRAME=1` ·
`SCRIP_UNWIND=0` · `SCRIP_U2=0` · `SCRIP_ZD_SCOPE=0` · `SCRIP_ZD_ENDJMP=0` · `SCRIP_ZD_DYNARM=7`.
This is a hard regression, not an env-gated regime.

## 2. ⭐⭐⭐ SNOBOL4 IS FINE. THIS IS THE s203 ZW-1 LESSON, VERBATIM, ONE YEAR LATER.

` OUTPUT = "hello"` under the SAME binary prints `hello`, rc=0.

The commits between the s206 watermark and HEAD are **concurrent SNOBOL4-BB ALPHA/OMEGA session work on the
SHARED emitter** — `4c3e9b45 [ALPHA] U-1b default ON`, `4d902148 [OMEGA] U-2`, `5bb623fe [ZETA] ZW-12`,
`799488f7 [ALPHA] U-SCOPE default ON`, `9c08c263 [HQ] ENDJMP`. At least one is an **opt-OUT flip of a shared
default**, which is precisely what `GOAL-ICON-BB.md`'s own s203 entry names as having cost Icon 30 programs
while the ledger recorded a SNOBOL4 accounting. The gates quoted in those commit messages are SNOBOL4
crosscheck sets (318 programs, m3/m4 by-set identical). **Icon was not in the ledger again.**

⇒ **PROCESS RUNG, not a code rung:** any commit touching `src/emitter/` or `src/templates/` must carry an
Icon watermark line, or the shared-emitter default must stay opt-IN. The s203 lesson was written down and
the identical failure recurred, which is the RULES.md test for promoting a lesson to a FACT RULE.

## 3. ROOT CAUSE — READ STRAIGHT OFF THE EMITTED `.s`, NOT INFERRED

`scrip --compile /tmp/h.icn` for `write("hello")`:

```
main:                    sub rsp, 8 ; push rdi ; push rsi ; call core_lib_init@PLT
main_α: main_α_body:                      <-- NO push rbp / mov rbp,rsp   (GLUE-O suppressed, correctly)
n0_lit_string_α:         sub rsp, 16      <-- SELF-ALLOCATES. writes [rsp+0]/[rsp+8]. THE FORTH SPINE WORKS.
n1_call_builtin_icon_α:                   <-- NO sub rsp AT ALL
                         mov [rsp+16], rax        <-- writes ABOVE its own frontier
                         mov [rsp+24], rax
                         lea rsi, [rsp+16]        <-- hands the runtime a pointer into that region
                         call rt_call_arr@PLT
main_γ:                  xor edi,edi ; call exit@PLT     <-- no whack (symmetric with no enter: correct)
```

**THE ARITHMETIC.** Let `R` = the return-address slot at `main:` entry. `sub rsp,8` → `R-8`;
`push rdi` → `R-16`; `push rsi` → `R-24`; `n0: sub rsp,16` → `R-40`.
Therefore at `n1`: `[rsp+16]` = `R-24` and `[rsp+24]` = `R-16` — **exactly the pushed `rsi` and `rdi`
save slots.** The call box scribbles its argument window over the caller's saved registers and then passes
`rt_call_arr` a pointer into them. That is the SEGV.

**WHY.** `n0` (a value producer) is ZD-armed and self-allocates. `n1` (`IR_CALL_BUILTIN_ICON`) is **absent
from `zd_wl_kind`** — the capability registry — so it declines; ZD arming is all-or-nothing per run
(s205: partial arming needs a region convex under BOTH operand and consumer edges), so the node falls back
to its **legacy flat-frame offsets**. Those offsets are displacements into the whole-graph carve that
**CARVE-KILL (`ef9a7d2c`/`1ba33ea6`) deleted**. The frame is gone; the offsets still name it.

⇒ This is the DIRECTIVE'S OWN DIAGNOSIS, confirmed in machine code: *"Each BB should allocate its own
storage… There is NO FRAME RELATIVE addressing anymore for operands."* `n0` obeys. `n1` does not, and
cannot, until its template grows a ZD arm.

## 4. ⭐⭐ "TURN ON ALLOCATION FOR EVERY SINGLE BB" IS MEASURED **EXACTLY INERT** AT THIS HEAD

The inherited prohibition (s205: default-admitting scores 238→130/133/30) was measured against a **working
unarmed path**. The unarmed path is now broken, so the trade-off plausibly inverted. **Tested rather than
assumed:**

| arm | Icon suite | `write("hello")` |
|---|---|---|
| default | **1 / 262 / 30** | rc=139 SEGV |
| `SCRIP_ZD_TOTAL=1` | **1 / 262 / 30** | **rc=0, PRINTS NOTHING** |
| `SCRIP_ZD_TOTAL=1 SCRIP_ZD_NOGRAPH=1` | — | rc=0, prints nothing |

**EXACTLY INERT on the suite, and on the repro it converts a LOUD crash into a SILENT WRONG ANSWER** — the
failure mode `bb_glue_flat.cpp`'s own header calls the one thing this subsystem keeps re-learning
(*"a storage decision which quietly does nothing produces plausible code and a wrong answer"*).

⇒ **The blanket flip is NOT the lever, and this is now a fresh number rather than an inherited one.**
s205's conclusion survives at this head for a NEW reason: arming a kind whose template has no ZD arm makes
`zd_wl_kind` LIE — the node arms, nobody writes the cell, the consumer reads an unwritten slot.
**THE UNIT OF WORK REMAINS ONE TEMPLATE ARM, ONE KIND AT A TIME.**

## 5. NEXT RUNGS — ORDERED

1. ⭐⭐⭐ **`IR_CALL_BUILTIN_ICON` ZD ARM** (`bb_call.cpp`). It is the FIRST node in the simplest possible
   Icon program and it is unarmed; nothing downstream can be measured until it lands. Its arg window must
   come from its own α carve (`ZOPQ`/`ZRES`), not from flat offsets.
   ⛔ **FULL-BUDGET RUNG — DO NOT HALF-LAND.** This changes an emitted call's argument shape, so it is
   BOTH-MEDIUM MANDATORY (`bb_call.cpp` + the `x86()` encoders), and this file's own BID-AT-LOWER ruling
   applies verbatim: *half-landing it is worse than not starting.*
2. ⭐⭐ **Bisect `dda156eb`..`4d902148` for the Icon break** with a predicate proven to discriminate at BOTH
   ends first (s203 instrument law). GOOD anchor candidate = `dda156eb`; BAD = HEAD. Predicate =
   `write("hello")` prints `hello` && rc==0. ~40 commits, each ~25 s build.
   ⚠ The break may be MULTIPLE independent events; do not assume one.
3. ⭐ **The process rung in §2** — Icon watermark required on shared-emitter commits, or default stays opt-IN.
4. Only then: the ICN-FB / ICN-CARVE ladder as written. **Every number in that ladder was measured on a tree
   where Icon ran; all of them need re-derivation.**

## 6. INSTRUMENT NOTES

- `refs/jcon-master` + `refs/icon-master` do NOT exist in a fresh SCRIP clone (`.gitignore:85`). Satisfied
  s207 by cloning `proebsting/jcon` and the Arizona Icon source and symlinking. **`proebsting/jcon` is the
  correct upstream** — record it, every session has re-derived this.
- `test_icon_all_rungs.sh` needs corpus at `/home/claude/corpus` or it SKIPs silently; symlinked s207.
- The suite prints its own summary line as the last line; use it, or `grep -c '^PASS'` anchored.

## 7. CANONICAL-SOURCE READ (per CONSULT CANONICAL SOURCES)

`refs/jcon-master/tran/irgen.icn`, `ir_a_Return` / `ir_a_Fail` / `ir_a_Suspend` / `ir_a_ProcCode`:
at the IR level JCON emits `ir_Succeed` / `ir_Fail` for BOTH a callee return and a program exit — **the IR
draws no callee/outermost distinction at all.** That distinction is entirely a backend concern, which
confirms s206's diagnosis (`bb_glue_outer_γ/ω` needing a callee flavor) is aimed at the right layer, and
confirms it is NOT a lowering defect. `ir_a_ProcCode` routes both body success and body failure to
`ir_Fail` — a procedure that runs off its end FAILS, it does not return null.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
