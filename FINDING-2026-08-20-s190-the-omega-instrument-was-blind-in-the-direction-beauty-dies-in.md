# FINDING s190 (seat3, `/home/claude3`, Claude Opus 5) — queue row `beauty-return-pair-shift`

## ⭐⭐⭐ THE HEADLINE: THE COMPUTED GOTO RAN ITS TARGET **NESTED**, AND `:(RETURN)` CANNOT RETURN FROM A NESTED CHAIN. **FIXED — `216_indirect_goto_computed` IS GREEN IN BOTH MODES, AND beauty NOW PRINTS ITS CORRECT OUTPUT BEFORE DYING OF SOMETHING ELSE.**

`IR_GOTO_DEFERRED`'s fallback arm called `rt_goto_transfer`, which ends in `rt_chain_enter` — a **CALL** that runs the transferee as a **nested one-shot activation** (five callee-save pushes, chain-scoped wires `rcx`/`rdx` aimed at its own landing). That is correct for an EVAL/CODE fragment that *terminates*. It is wrong for a computed goto into a labelled statement that ends in `:(RETURN)` — and **per the manual (v3.7 p.130) `RETURN` is a reserved LABEL reached by a goto, not a statement**, so "goto into code that returns" is the *ordinary* SNOBOL4 idiom, not an exotic one. The transferee therefore reached the shared `RETURN` floater ≈720 bytes **below** the activation's frontier, where the `{γ,ω}` pair its `DEFINE` α pushed is not, and the depth-exact `pop rcx` read C save-set data — `rip=_rtld_global`.

**That signature is already written down in the very file that causes it.** `bb_goto_deferred.cpp` line 32 records it for the *sibling* arm s111 lifted: *"RUNS the body NESTED inside a C frame … the site's {gamma,omega} pair went unconsumed and was re-read as save-set data (rip=_rtld_global)"*. This is that same fix for the **computed-name half** — the *"sealed-cell resolution / owed slice-2"* the same note planned and left owed.

## ⛔⛔ CORRECTED IN PLACE (same session, kept visible per STALE-ORIENTATION rather than silently rewritten)

My first write-up of this finding said **"IR_STATEMENT_END double-releases 96 bytes at depth 0."** **That is false and I falsified it myself.** I trusted the ring's `depth` column; `g_zsm_rsp0` is ONE cell re-based by every nested graph, and the last `ORIGIN` before the crash belonged to a *different* graph (`op=59 IR_MATCH_ASSIGN_IMM`, st=961) — the file's own documented KNOWN LIMIT. Read from raw rsp only, **every release on the failure road is arithmetically exact**: the frontier is stable at `0x…8860` across st=956/961/963/969, `MATCH_BEGIN`'s ω returns to it, and `STATEMENT_END`'s 96 is exactly the six cells its statement carved (6 × 16, `0x…8800`→`0x…8860`). **rsp was correct at the `pop rcx` all along.** A seat who saw the first version must be able to see it retracted; the `zd-statement-end-double-release` row I asked for on that reading is withdrawn.

## THE CURE — ARM 1'S SHAPE, NOT A NEW ONE (SCRIP `b12cb82e`)

The s55 DEFINE-FOLD arm already does the right thing for a *constant* label: `jmp [rip@cell + LBL__<name>]`, *"wires ride r10/r11, no chain, no reserve"*. The computed-name arm now does the same, with the address resolved at runtime instead of baked:

```
α · align_enter · load name · call rt_goto_resolve · align_leave
  · test rax,rax · jz L1                      ; NULL (the END sentinel) falls through to γ
  · add rsp, op_zgpop                          ; the statement-terminal release — see below
  · jmp rax                                    ; transfer AT THE FRONTIER, wires in r10/r11
L1: γ
```

`rt_goto_resolve` is `rt_goto_transfer`'s lookup half **split out verbatim** — same order, same diagnostics, same `exit(1)` on an undefined label. `rt_goto_transfer` is now literally resolve-then-enter, so every pre-existing caller is byte-unchanged. Killswitch `SCRIP_GOTO_TAIL=0` restores the prior emission exactly.

### ⛔ TWO HALVES, AND THE SECOND WAS ONLY VISIBLE ONCE THE FIRST LANDED

Tail-jumping at the **site's** depth still died — `rip=rcx=0x0000000800000002`, a **string DESCR tagword** (tag 2, len 8), the same class `bb_match_replace.cpp:37` records ("*loaded a statement cell descr tagword 0x300000002 and jumped into it*"). Reason: the site is **mid-statement**. beauty's dispatch has three live operand cells (the constructed name) standing between the goto box and the activation frontier. **A normal goto never meets this** — it rides `statement_end: add rsp,K; jmp <label>`, so the terminal release happens *first* and the jump leaves from the frontier. A deferred goto transfers from *inside* the statement and must perform that release itself. `op_zgpop` is exactly that release, already staged by the planner; this arm jumps away and never reaches `x86_gamma()`, the only other consumer, so emitting it here **moves** it rather than duplicating it.

### ⛔ THE RTCC VENEER IS LOAD-BEARING HERE

`x86("call", …)` banks `r10`/`r11` into `rtccb` and restores them across the resolver (`g_rtcc_on` defaults ON). That is what keeps the wires alive. `x86("call_bare", …)` would silently drop them — the inverse of the s184 trap recorded in `x86_zsm_ev`.

## THE WITNESS, AND WHY beauty IS THE PROGRAM THAT SHOWS IT

Bisecting the **input** rather than the program: empty file **rc=0** · `* comment` **rc=0, correct identity** · `head -5` **rc=0** · one empty line / one space / `\tX = 1` / `END` / `head -10` all **rc=139, zero bytes emitted**. beauty's **comment road was green and its non-comment road SEGV'd before one byte**, because the non-comment road is the dispatch:

```
beauty.sno:247   DIFFER(t)   :S($('pp_' t))F(RETURN)     ; and :466 for ss_
```

Every `pp_<t>` target sits **inside `pp`'s own body** (`DEFINE('pp(x)c,i,n,s,t,v')` at :240) and exits `:S(RETURN)`. That is a computed goto into a function body followed by a return — precisely the shape that had no correct road.

**After the fix:** beauty < one empty line **prints its correct identity line**, then a diagnosed `Error 121 — len argument is negative or too large`. All 8 `m1_lad_*` rungs move **rc=139 → rc=1**.

## RECEIPTS (`make pristine`, RT_OPT `-O0`, re-proved at merged HEAD SCRIP `b12cb82e` after two other seats' commits landed beneath)

| | m3 | m4 |
|---|---|---|
| **default (arm ON)** | **PASS=333 FAIL=4** | **PASS=326 FAIL=10 SKIP=1** |
| `SCRIP_GOTO_TAIL=0` | PASS=332 FAIL=5 | PASS=325 FAIL=11 SKIP=1 |

**The ONLY mover is `216_indirect_goto_computed` — the test literally named for this construct — green in BOTH modes. ZERO new reds across 337 programs × 2 modes**, fail-sets diffed by name. Crosscheck agrees: 216 leaves both fail lists, DIVERGE set identical (`expr_eval`, `140/141_pat_eval_double_fn_*`). Medium gate green (0 sites, ceiling 0). RULES step-4 regen: all five scripts **changed=0**. `board_beauty_m1.sh --modes m3`: **3/10 green, first red still at 10 — NOT claimed moved**; what changed is the failure *class*, not the rung.

## ⛔ WHAT THE BRIEF GOT WRONG — BOTH CLAIMS, MEASURED

**(1) "The `{gamma,omega}` pair is not missing, it is SHIFTED … a REAL scrip continuation ONE SLOT BELOW (`0x41bd68`)."** `readelf -S scrip` puts `0x41bd68` at the **exact base of `.fini_array`** — static data in the compiler's own image. Its partner `0x7ffff7ffd000` is ld.so's rw data page. **Neither is a `_γ`/`_ω` label; neither is in any executable mapping.** The pair was not shifted — it was never *at* that depth, because the body was running nested. (Nor was it startup garbage: at `main` entry those slots read `0x0`. I checked, and that hypothesis of mine was wrong too.)

**(2) "Prime suspect: the conceded match's omega unwind leaks slots; law 0b omega-balance."** A full `SCRIP_ZSM_ALL` census — **26,063 port events, 36 IR kinds** — reports **ZERO** `RSP LEAK`, **ZERO** ω `IMBALANCE`. Only 8 γ· skews, all the documented benign whack-owner shape. **And the ω arm could not have found this anyway:** its release test is literally `if (rsp < e->rsp_a)` — *under*-release only. Over-release was invisible **by construction**. `SCRIP_ZSM_OVERPOP=1` (landed SCRIP `2cf31532`, armed-only, report-only) surfaces **1094** previously-invisible over-releases. ⛔ **In fairness to the record: that knob did NOT find this bug.** It is a real gap closed, not the instrument that cracked the case — what cracked it was reading raw rsp and following `IR_GOTO_DEFERRED` into the template.

**Also exonerated by A/B:** `SCRIP_WIRE_PAIR_FRAME=0` and `=1` are both rc=139 — `bcps_wire_pair_consumed` is not involved.

## ⛔ NAMED, NOT FIXED — THE NEXT WALL IS NOW REACHABLE

`Error 121 — len argument is negative or too large` on every ladder rung. It was unreachable before (the process died first), so it is **newly exposed, not newly caused** — the `SCRIP_GOTO_TAIL=0` arm reproduces the old SIGSEGV at the same input, which is the control that proves it.

## SUGGESTED ROWS (asked, not worked)

1. **`beauty-error-121-len`** — the newly-reachable wall. beauty prints its correct identity line and then trips `Error 121` in statement 0; this is now the M1 blocker and the first-red-at-10 mover.
2. **`goto-tail-wires-audit`** — the tail arm jumps without setting `rcx`/`rdx`, which is right for a transferee that leaves via `:(RETURN)`. A transferee that instead *falls off its end* exits via chain-scoped wires this arm does not supply. No corpus witness fails today; the class deserves a witness before it finds one.
3. **`zsm-overpop-triage`** — 1094 over-releases are now visible and most are legitimate whack-owners. A predicate separating those from real double-releases turns the knob from a candidate list into a verdict.
