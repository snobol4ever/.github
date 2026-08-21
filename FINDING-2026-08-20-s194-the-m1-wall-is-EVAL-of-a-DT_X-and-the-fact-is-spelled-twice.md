# FINDING — 2026-08-20 s194 (HQ, Fable 5, beauty lane hands-on) — ⭐⭐⭐ THE M1 WALL IS `EVAL` OF A `DT_X`, AND THE FACT IS SPELLED TWICE WITH THE TWO SPELLINGS DISAGREEING

**Measured at SCRIP `40a5b01a` / corpus `bec0c597` / .github `21b7504a`, pristine (`make pristine` EXIT=0, RT_OPT `-O0`), oracle `x64/bin/sbl -bf` verified alive first.**

## 1. THE LADDER READING, AND THE FIRST CORRECTION

`board_beauty_m1.sh --modes m3` at pristine HEAD: **m3 5/10, first red at 40** — identical to the s191 cursor, so nothing regressed and nothing advanced. `--bisect` then named **M3 FIRST FAILING LINE = 26**, which is:

```
                  &FULLSCAN      =  1
```

⛔ **HQ'S FIRST READING OF THAT LINE WAS WRONG AND ITS OWN CONTROL KILLED IT.** `&FULLSCAN` is a pattern-matching mode keyword and the obvious story — *"SCRIP's fullscan path is broken"* — is false. The ordinary control `X = 1` fed to beauty SEGVs identically. Line 26 is simply **the first real statement in beauty.sno**; lines 1–25 are comments, blanks and `-INCLUDE`s. The keyword is a coincidence of position, not an ingredient.

**The floor, measured** (each fed to beauty on stdin; oracle rc=0 on all six):

| input | SCRIP m3 | note |
|---|---|---|
| `` (empty) | **PASS** | |
| `END` | **PASS** | |
| `* hi` + `END` | **PASS** | class A (crash-on-completion) is CURED |
| `X` + `END` (bare label) | **PASS** | |
| `X =` + `END` (null RHS) | **PASS** | ⭐ **nothing to EVAL** |
| `X = 1` + `END` | **rc=139** | |
| `OUTPUT = 1` + `END` | **rc=139** | |
| `X 5` + `END` (match) | **rc=139** | |
| `:(L)` + `END` (goto) | **rc=139** | |
| `L X = 1` + `END` | **rc=139** | |
| `X = "s"` + `END` | **rc=139** | |

⭐ **The discriminator is not assignment, not match, not goto: it is whether the statement carries an EXPRESSION.** `X =` with an empty right-hand side is the one statement shape that survives, and it is the one with nothing to evaluate.

## 2. THE CRASH CHAIN, WITH GDB RECEIPTS

`CSN_NO_SEGV_HANDLER=1 gdb --args ./scrip beauty.sno < (X = 1)`:

```
#9 rt_call_arr(fn="EVAL", nargs=1)                by_name_dispatch.c:4657
#8 rt_call_arr_impl(fn="EVAL", nargs=1)           by_name_dispatch.c:4704
#7 try_call_builtin_by_name(fn="EVAL", nargs=1)   by_name_dispatch.c:6932
#6 rt_call_named_proc(name="EXPR$207F7", args=0x0, nargs=0)   rt/rt.c:2002
#0 rtccb()                     rip=0x7ffff4943880  rax=0x0  rcx=0x3
```

Measured at the breakpoint, **not inferred**:

```
name=EXPR$207F7   jmp_entry=1   dyn_scope=1   is_generator=0   fn=0x7fffee210000
rt_dyn_alpha_fn("EXPR$207F7", 0)  =  0x0        <<< NO SEALED α CELL
rt_proc_find("EXPR$207F7")        =  0x7fffae047130   <<< the proc DOES exist
```

**The chain, five steps:**
1. beauty's `semantic.inc` builds every grammar rule through `EVAL`; each statement carrying an expression reaches `EVAL` with an **unevaluated-expression descriptor (`DT_X`)** naming a runtime-minted thunk `EXPR$207F7`.
2. `by_name_dispatch.c:6932` routes that `DT_X` to `rt_call_named_proc(name, NULL, 0)`.
3. `rt_proc_find` succeeds and `dyn_scope` is set, so the C-lex early return at `rt.c:1999` is not taken.
4. The sealed-α arm at `rt.c:2000` declines — **twice over**: its own `!strchr(name,'$')` guard refuses synthetic names, *and* `rt_dyn_alpha_fn` answers **NULL** anyway (measured above), because a fragment thunk carries **no `<name>_α` staging label by construction** — `runtime_eval.c:202` states this and `SCRIP_SEAL_DIAG` measures it (`alpha$EXPR$0F1 MISS`), so the seal at `runtime_eval.c:251` seals nothing.
5. Control falls to `rt.c:2002` `rt_proc_enter((void *)p->fn)`, where `p->fn` is the **GENERIC ENTRY THUNK** — and the s117 comment sitting on the line directly above describes precisely this outcome: *"the wrong protocol for an emitted body, so rt_proc_enter's wire jmp lands wild."* It lands in `rtccb` with `rax=0`.

## 3. ⭐⭐⭐ THE DEFECT IS ONE AUTHORITY SHORT — `DT_X` IS HANDLED TWO WAYS

This is the s68/s70 **spelled-twice** disease on a live road:

| site | handling of a `DT_X` | outcome |
|---|---|---|
| `pattern_match.c:1001` (and `:994`, `:993`) | `rt_proc_call_open(val.s, 0)` — the **slim fn-pointer road** | **works** |
| `by_name_dispatch.c:6932` (EVAL builtin) | `rt_call_named_proc(val.s, NULL, 0)` — the **C by-name road** | **wild jump** |

The runtime already *knows* the right answer for a `$`-marked fragment thunk and applies it in three places; the EVAL builtin is the one caller that never got the ruling. `runtime_eval.c:202` records the same ruling for the emitted side — `bb_call_proc_staged`'s TINY arms consult `g_rt_fragment_emit` and **REFUSE**, falling to "the slim/legacy call = the rt fn-pointer machinery main programs already use for every thunk call." **The C by-name road is the only consumer that still enters through the generic thunk.**

## 4. ⛔ A CURE FALSIFIED BY TEST — RECORDED SO THE NEXT SEAT DOES NOT SPEND A SESSION ON IT

The obvious one-line fix is to send synthetic names down `rt_proc_call_c_lex` instead of `rt_proc_enter`. **It is INERT and this was measured, not reasoned**: patched behind `SCRIP_SYNTH_CLEX`, rebuilt, all six red witnesses **byte-identical armed vs off-arm (rc=139 both)**. Cause: `rt_proc_call_c_lex` opens with

```c
if (p->jmp_entry) { (void)rt_proc_call_prologue_lex(p, nargs, wn); return rt_proc_enter((void *)p->fn); }
```

and **`jmp_entry=1` for this proc** (measured, §2) — so the "safe" road funnels back to the identical instruction. The patch was reverted; the tree carries none of it. ⛔ **Any cure routed through a road that can reach `rt_proc_enter(p->fn)` for a `jmp_entry=1` proc is the same no-op wearing a different name.**

## 5. ⭐ THE ROAD IS THE WALL — PRICED BY ABLATION, AND THE NEXT WALL IS NAMED

Diagnostic only (`SCRIP_EVAL_DTX_STUB=1`, three lines, reverted after measuring): make the `DT_X` arm answer `FAILDESCR` instead of jumping. Nothing else changed.

| | baseline | ablated |
|---|---|---|
| m3 rungs green | 5/10 | **6/10** |
| first red | line **26** | line **52** |
| failure mode | **SEGV 139** | clean rc=1 |

⛔ **THIS IS NOT A CORRECTNESS RESULT AND MUST NOT BE READ AS ONE.** The ablation makes `EVAL` answer *failure*, which is semantically wrong; its greens prove only that **the crash — not a wrong answer — is what stops beauty at line 26**. A correct cure must reach the same-or-better ladder **without** the semantic hole.

⭐ **THE NEXT WALL, NOW NAMED AND FREE:** line **52**, `DQ = '"' BREAK('"' nl) '"'` — a pattern-valued assignment. It is dispatchable the moment the EVAL road lands, and it does not have to wait for it.

## 6. WHAT A CORRECT CURE HAS TO DO

`rt_proc_call_open_slim` returns `(long)p->fn` — *"nonzero == admitted AND the transfer target"* — i.e. it **admits and hands back a target the emitted caller jumps to**; it is not a complete call. So the cure is not a one-line substitution: the C by-name road needs the slim **transfer + epilogue** protocol (`rt_proc_call_epilogue_slim_γ` and siblings) that emitted call sites already speak, applied on the `$`-marked-thunk arm. That is one rung, and it belongs to whoever owns `runtime_eval.c` / `by_name_dispatch.c`.

**Sibling to audit in the same rung:** `rt_call_proc_descr` (`rt.c:908`) ends `return rt_proc_enter(rt_dyn_alpha_fn(name, (void *)p->fn));` — the **same fallback to the same generic thunk**, and it is the road `claws5-m4-sig11` (queue row 23) already convicted for m4. One class, two callers.

## 7. RELATED RECORD

- `FINDING-2026-08-20-s193-the-m4-image-was-never-told-where-the-alpha-face-lives.md` — seat4's `apply-snodef-m4`: the same α-cell class for **DEFINE'd** functions in **m4**. This finding is its runtime-fragment twin in **m3**.
- Queue row 23 `claws5-m4-sig11` — `alpha$<FN>` sealed only by `m3_seal_entry_cells`, m4 image has zero cells.
- `runtime_eval.c:202` (`g_rt_fragment_emit`) and `:251` (`bb_ab_seal_entry_cells`) — the emitted side's ruling, already correct.
- RULES.md ASM-DIFF-FIRST: step 2 (diff the `.s`) **does not apply here and that is worth saying** — the binary is identical across the passing and failing cases; only the *input* differs. When one program crashes on one input and not another, the asm diff has nothing to compare and gdb is the correct second step, not the third.

## 8. ROUTED

`GOAL-SNOBOL4-100.md` LIVE CURSOR (s194 HQ beauty lane) · `GOAL-SCRIP-HQ.md` cursor + queue row `m1-eval-dtx-byname` (rank 0) · `QUEUE.tsv` in lockstep (TWO-CHANNEL LAW).
