# FINDING — 2026-08-20 s194b (HQ, Fable 5, beauty lane, solo per Lon) — ⭐⭐⭐ THE M1 WALL BOTTOMS OUT: A WIRE-ENTRY BLOB IS ENTERED FROM C WITH **RTCC BANK RESIDUE IN ITS ω WIRE**, AND IT JUMPS INTO `rtccb`

**Supersedes nothing; EXTENDS `FINDING-2026-08-20-s194-the-m1-wall-is-EVAL-of-a-DT_X-and-the-fact-is-spelled-twice.md` by four levels.** Measured at SCRIP `ebbc1c89`, pristine (`make pristine` EXIT=0, RT_OPT `-O0`), oracle `sbl -bf` verified alive first. Instruments used, in order: Lon's automatic bug finder → the 2-way IPC monitor → the ZSM ring → seat3's `SCRIP_ZSM_OVERPOP` census → `SCRIP_SEAL_DIAG` → gdb disassembly.

## 1. ⛔ THE FINDER REPORTED "NO DIVERGENCE" AND IT WAS A FALSE NEGATIVE — FIX THIS FIRST

`util_autobug.sh` on beauty printed **“NO DIVERGENCE — the two engines agreed to END. Nothing to bracket.”** That is false. Run directly, the monitor says:

```
[ctrl] PARTIAL EOF step 1908: ['scr'] done, others still running
  spl: still emitting @168 VALUE tx = STRING(1)='X'
  scr: EOF
timeout: the monitored command dumped core
```

The scrip child **SIGSEGV'd**; the finder read a dead child as agreement. ⛔ **This is the “non-empty is not alive” class arriving in the bug finder itself** — the same shape as the absent-oracle all-FAIL table. A tool that cannot run must say *could not run*, never *nothing to bracket*. Row `autobug-dead-child-false-agree` minted.

**THE REAL BRACKET: last agreement = step 1907, first divergence = step 1908**, with SPITBOL sitting on `tx = 'X'` — beauty's **token variable**, mid token-classification.

## 2. THE ZSM RING AT THE CRASH, AND ITS GREEN TWIN

`op=15` is **`IR_CALL_VALUE`**.

**🔴 RED (`X = 1`) — final two events, then the ring ends:**
```
α· op=15 node=97120  rsp=0x7fffffff65f0  depth=80
ω· op=15 node=97120  rsp=0x7fffffff6640  depth=0     <- 80 bytes released; ζ-SPINE collapsed
```
**🟢 GREEN (`X =`, null RHS — nothing to EVAL) — same box:**
```
α· op=15 node=68848  rsp=0x7fffffff9370  depth=-1616
ω· op=15 node=68848  rsp=0x7fffffff9380  depth=-1632  <- 16 bytes, one slot
β· op=17 node=68928  …                               <- unwind continues correctly
```
⛔ **EXONERATED, and worth recording so nobody re-chases it:** the eye-catching `α op=25 (IR_CUT) node=24672` answered by a *different* node's γ appears **identically in the green ring**. An event present in both arms is not evidence.

## 3. ⭐ THE DISCRIMINATOR, FROM seat3's OVER-RELEASE CENSUS

`SCRIP_ZSM_OVERPOP=1` (seat3, s193 — built precisely because the ω arm only ever tested UNDER-release). ⛔ **The count is a trap: GREEN has MORE over-release events than RED (1628 vs 1305)**, and the instrument says so itself (“a CANDIDATE, not a verdict”). What matters is the *shape set*. Grouped by `(op, bytes)` across both runs, **exactly one shape exists in red and in no green run**:

```
op=15 | 80        red_count = 1        <- IR_CALL_VALUE released 80 bytes MORE than its α carved
```

**Causally closed by ablation** (`SCRIP_EVAL_DTX_STUB=1`, diagnostic, reverted): same binary, same input, one flag — `op=15|80` **ABSENT** and `rc=0`; default, **PRESENT** and `rc=139`.

## 4. ⭐⭐⭐ 345 UNSEALED THUNKS — THE α FACE IS NEVER EMITTED FOR FRAGMENT THUNKS

`SCRIP_SEAL_DIAG=1` on the red run:

```
345 seal MISSES:   259 × EXPR$n_α      86 × PAT$n_α
[SEAL] MISS lbl=EXPR$0_α cell=alpha$EXPR$0
```

`bb_ab_seal_entry_cells` looks up a label literally named `<pname>_α`; a proc chain's entry α is emitted generically as `bb<N>_α`, and the α face is a **TINY record-contract entry shape** that “exists only where the TINY shim is admitted.” EXPR$/PAT$ thunks have no DEFINE site and no shim, so **every one of beauty's 345 thunks is unsealed** and `rt_dyn_alpha_fn` answers NULL for all of them.

## 5. ⛔⛔⛔ THE BOTTOM: A WIRE-ENTRY BLOB ENTERED WITH RTCC BANK RESIDUE IN ω

`p->fn` for `EXPR$207F7` — `jmp_entry=1 dyn_scope=1`:
```asm
jmp    +5
sub    $0x10,%rsp
lea    0xf(%rip),%rcx          ; rcx = &record   {nargs=0, γ=0x…37, ω=0x…37}
movabs $0x7ffff55410a8,%rax    ; g_ab_fn_cells + 1032   (FILLED — 0x7fffee040014)
mov    (%rax),%rax
jmp    *%rax
```
The cell is **not** empty, so the first jump is real. The body it reaches is a **wire-entry blob**:
```asm
sub    $0x30,%rsp
mov    0x880(%r9),%rax         ; reads through r9  = ζ base
movq   $0x0,0x880(%r9)         ; WRITES through r9
mov    %r10,0x10(%rsp)         ; consumes r10 = γ wire
```
It requires the **VM register plane** — r9 (ζ base) and r10/r11 (γ/ω wires). `rt_proc_enter` establishes none of them. At the fault:

```
rip 0x7ffff49448c0 <rtccb>     rax 0x0     rcx 0x3
r9  0x70001000                 r10 0x7ffff4128468
r11 0x7ffff49448c0             <<< r11 == rtccb == rip
```

⭐⭐⭐ **The ω wire held the address of `rtccb` — the RTCC global register bank — and the blob jumped it.** The blob did exactly what it was built to do; it was handed C-side residue as its ports. This is the *"stale rcx/rdx wire delivery"* class named at `scrip.c:86`, and it is the **same global `rtccb` wire bank the HQ-70 audit already convicted** (*"a machine whose wires bank in a global cannot be observed safely — the strongest argument on file for PF-2"*).

## 6. THE CHAIN, END TO END

1. `ShiftReduce.inc:22/24` — `t = EVAL(t)` `:F(NRETURN)` where `t` holds an **EXPRESSION**. (`semantic.inc:16` built it with `EVAL("…")`, the **string** road, which works.) Manual v3.7 p.85-86: *an EXPRESSION is evaluated only when referenced*.
2. → `pattern_match.c:1179` `rt_dtx_drain` (gated by `SCRIP_DEFER_XSTAR`, the s188 Class-B cure) **or** `by_name_dispatch.c:6932` (the EVAL builtin). **Two entrances, one dead end.**
3. → `rt_call_proc_descr` / `rt_call_named_proc` → sealed-α arm declines (**α cell unsealed — §4**).
4. → `rt_proc_enter(p->fn)` = the generic entry thunk.
5. → thunk builds its record, jumps through a filled `g_ab_fn_cells` slot into a **wire-entry blob**.
6. → blob consumes r9/r10/r11; the C road set none; **r11 = &rtccb**.
7. → blob jumps ω → `rtccb` → SIGSEGV, `rax=0`. ZSM records it as `op=15` ω releasing 80 bytes.

## 7. ⛔ THREE CURES FALSIFIED BY TEST — DO NOT RE-SPEND THEM

1. **Route synthetic names to `rt_proc_call_c_lex`** — **INERT**, 6 witnesses byte-identical armed vs off-arm. `c_lex` opens `if (p->jmp_entry) return rt_proc_enter(p->fn)` and `jmp_entry=1` here.
2. **Swap the EVAL arm to the sibling `rt_call_proc_descr`** — **still SEGV**. `rt.c:908` has the same fallback to the same generic thunk. Both C by-name roads funnel to one instruction.
3. **`MONITOR_BIN=1` alone (GVA off)** — **still SEGV**, and it makes the *green control* SEGV too. The monitor's agreement came from the child dying, not from GVA.

**KILLSWITCH SWEEP, 18 arms** (`DYN_ALPHA`, `BYNAME_ALPHA`, `CODE_THUNKS`, `SLIM_PAIR`, `AB`, `M4_ALPHA_SEAL`, `GOTO_TAIL`, `SPAN_FRAME`, `CONST_NEST`, `PRE_ORDER`, `FENCE_RTAIL`, `SUB_AGG`, `ALT_TAIL`, `FENCE0_WHACK`, `FENCE_IGNORE`, `OPT`): **only two move it**, and both trade the crash for a wrong answer, not for a cure —
- `SCRIP_DEFER_XSTAR=0` → rc=0, `Parse Error` (the **pre-s188 wall** returns: the drain is *needed*, it merely crashes on unsealed thunks)
- `SCRIP_RTSEQ_RESUME=0` → rc=0, `Parse Error`
- `SCRIP_OPT=0` → rc=**134** (different failure; not a road out)

## 8. WHAT A CORRECT CURE MUST DO

Give the C by-name road a **wire-entry trampoline** that establishes r9 + r10/r11 before transferring, the way emitted call sites do — *or* emit an `_α` TINY face for EXPR$/PAT$ thunks so the existing `rt_tiny_record_enter` road becomes available (which would close all 345 at once). ⛔ **`EVAL` must keep a failure channel** — `ShiftReduce.inc` writes `:F(NRETURN)`, so a cure that cannot fail is wrong. ⛔ This sits on the **RTCC/PF-2 axis**: while the wires bank in a global, any C→blob transfer is entering with residue.

## 9. WITNESSES CHECKED IN (`corpus/probe/m1eval/`, live-oracle refs)

- **`m1e_eval_chained_defer_red.sno`** — ⭐ a **new standalone oracle-differential defect found on the way**, 3 lines, no crash: `a = *(1 + 2)` · `b = *a` · `OUTPUT = EVAL(b)` → oracle **`EXPRESSION`**, SCRIP **empty**. A *chained* defer (a thunk returning an EXPRESSION) — `rt_dtx_drain`'s own territory, silently wrong. Checked in RED per law 0d.
- `m1e_eval_defer1_ctl.sno` · `m1e_eval_selfassign_ctl.sno` — GREEN controls (one defer level; self-assignment). Both oracle-identical.
- `beauty_assign_red.in` / `beauty_nullrhs_ctl.in` — the 2-line beauty inputs; the red/green pair that isolates “statement carries an expression”.

## 10. ⛔ M1 IS NOT EARNED AND IS NOT CLAIMED

Ladder unchanged at pristine HEAD: **m3 5/10, first red line 26**. Nothing landed in SCRIP or corpus except the witnesses above; every experiment in this finding was reverted and both trees are clean.

## 11. ROUTED

`GOAL-SNOBOL4-100.md` LIVE CURSOR (s194b) · `GOAL-SCRIP-HQ.md` cursor · rows `m1-eval-dtx-byname` (rank 0, re-briefed to this depth), `m1e-chained-defer-eval`, `autobug-dead-child-false-agree` · `QUEUE.tsv` in lockstep.
