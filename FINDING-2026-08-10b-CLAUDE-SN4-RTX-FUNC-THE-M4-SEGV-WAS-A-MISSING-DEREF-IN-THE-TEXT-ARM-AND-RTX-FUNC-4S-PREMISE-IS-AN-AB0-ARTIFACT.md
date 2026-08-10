# FINDING 2026-08-10b (Claude, Opus seat) — SN4 RTX-FUNC: the m4 AB=1 SEGV was a MISSING DEREF in the TEXT arm of the `fn_cell` transfer; RTX-FUNC-4's premise is an AB=0 ARTIFACT; the AB deficit is TWO NAMED PROGRAMS and both are one aliasing defect

**SCRIP HEAD at open:** `930539c0` (`799f2e76` + feature regen). **Watermark re-proved at open and close.**

---

## 1. ⭐⭐ THE TOP BLOCKER IS DOWN — m4 AB=1 SEGV FIXED, ROOT CAUSE IS A BOTH-MEDIUM ASYMMETRY

`bb_call_proc_staged.cpp:271-272` and `:468-469` carry a `MEDIUM_BINARY ? … : …` ternary whose two arms **were not the same program**:

```
BINARY : movabs rax,&cell            + mov rax,[rax] + jmp rax    <- 3 insns, HAS the deref
TEXT   : mov rax,[rip+cell@GOTPCREL] +                 jmp rax    <- 2 insns, DEREF MISSING
```

`@GOTPCREL` yields the symbol's **ADDRESS**. The call site needs its **CONTENTS**. So in TEXT the emitted code jumped **to `fn_cell$FN` itself — a `.data` symbol** — instead of through it. The documented contract is `jmp [fn_cell$FN]`, memory-indirect (`bb_call_proc_staged.cpp:236`, `:446`; `bb_func_activate.cpp:37-38`); TEXT had silently lost the indirection.

**FIX:** add the missing `x86("mov","rax",RDQ("rax",0))` to the TEXT arm at both sites. Template-only. **`x86_asm.h` UNTOUCHED.**

**ACCEPTANCE (m4, `SCRIP_AB=1`, was rc=139 at every one):** `func_call` rc=0 ORACLE-EXACT · `func_call_overhead` rc=0 ORACLE-EXACT · `fibonacci` rc=0 ORACLE-EXACT.

⭐ **HOW IT WAS FOUND, AND WHY NO CODE-READING WAS NEEDED.** There is no gdb in this container (cursor was right). The core dump was parsed directly for `NT_PRSTATUS` (`/home/claude/coreinfo.py`, ~30 lines of struct unpacking): **`RIP == RAX == 0x4050d0`**, and `nm -n` put `0x4050d0` at **`d fn_cell$INC`** — a data symbol. The diagnosis was complete before any template was opened. ⭐ **A core file is a register set; "no gdb" is not "no crash PC."** Recommend this as standing technique — it is cheaper than the monitor for the SEGV class, which the monitor is structurally blind to.

## 2. ⛔ A SECOND, INDEPENDENT BOTH-MEDIUM DEFECT — FIXED, BUT IT WAS **NOT** THE SEGV

Both monitor taps in `bb_func_activate.cpp` (`:172` CALL tap, `:311` RETURN tap) baked `&g_monitor_bin` with `x86("movabs", ...)` — an **ASLR'd address from the `scrip` COMPILER's own process** (`0x7F0391348D8C` observed). Correct in BINARY (same process); garbage in a separate m4 binary.

**FIX:** the already-existing `x86_load_got("rax","g_monitor_bin",&g_monitor_bin)`. Its BINARY arm is **byte-identical** to `x86_movabs_r64` (same REX computation, same `0xB8|(m&7)`, same `u64le`, same `x86_Lrec` wrap) ⇒ m3 emission cannot move by one byte. `readelf -sW` + `--dyn-syms` confirm `g_monitor_bin` is **GLOBAL / DEFAULT / in the `.so` dynamic table** ⇒ exported ⇒ preemptible ⇒ `@GOTPCREL` is the correct TEXT form per ARCH §7 0(c)'s original three checks.

⛔⛔ **MY OWN HYPOTHESIS WAS FALSIFIED AND I ALMOST MIS-CREDITED THE FIX.** Fixing this produced a correct-looking emission (`mov rax, qword ptr [rip + g_monitor_bin@GOTPCREL]`) and **the SEGV persisted unchanged**. Had the rung stopped at "emission is now right," a real defect would have been closed on a green artifact while the blocker stood. ⭐ **Emission correctness is not execution correctness; in m4 they are separated by a whole process boundary — which is the entire reason this ladder keeps mandating the m4 arm.**

## 3. ⛔⭐⭐ RTX-FUNC-4'S PREMISE IS FALSE, AND ITS GATE IS STRUCTURALLY UNSATISFIABLE

The rung states: *"`func_call.sno` m4 `.s` still shows `call rt_arg_stage` + `call rt_proc_call_open_slim` — the SCC probe returns 0 for INC in m4, so the AB-3b arm never fires in TEXT mode."*

**MEASURED at HEAD, on FRESHLY EMITTED artifacts (not the committed `.s`):**

| arm | `rt_arg_stage` | `rt_proc_call_open_slim` |
|---|---|---|
| m4 **AB=1** `func_call` | **0** | **0** |
| m4 **AB=1** `fibonacci` | **0** | **0** |
| m4 **AB=0** `func_call` | 1 | 1 |
| **committed `func_call.s`** | 1 | 1 |

⇒ **The AB-3b arm fires correctly in TEXT mode. There is no SCC probe defect. The seat read an artifact and mis-attributed it.**

⭐⭐ **THE MECHANISM, WHICH GENERALISES:** `SCRIP_AB` defaults **OFF** (`lower_snobol4.c:2054`, opt-in since RTX-FUNC-0). The `.s` regen scripts run the compiler at its **default**. Therefore **every committed `.s` artifact in this tree describes the AB=0 legacy arm**, and the rung's GATE — *"regenerated `.s` artifacts show zero `rt_arg_stage`"* — **cannot be satisfied by any compiler behaviour whatsoever** while AB defaults off. This is the SECOND RTX-FUNC rung to inherit a gate whose mechanism it does not have (after RTX-FUNC-1/-2's `SCRIP_RTX_CALL` kill-switch, which has no CALL arm). ⛔ **Same root cause both times: the gate was written for a different rung's machinery.** ⇒ **RTX-FUNC-4 is DISCHARGED WITH CORRECTION — its substantive goal was already met before the rung was written.**

⚠ **CONSEQUENCE FOR EVERY FUTURE SEAT: `.s` artifacts are AB=0 EVIDENCE ONLY.** They are still HONEST CURRENT output (RULES step 4) — of the default arm. No AB-path claim may cite them, in either direction.

## 4. ⭐⭐ THE AB PATH'S ENTIRE CORRECTNESS DEFICIT IS **TWO PROGRAMS**, AND THEY ARE ONE DEFECT

First both-modes crosscheck ever run on the AB arm (previously impossible — m4 AB=1 SEGV'd):

| arm | m3 | m4 | DIVERGE |
|---|---|---|---|
| **AB=0** (default) | **282 / 35 / 0** | **276 / 40 / 1 SKIP** | **5** |
| **AB=1** | 280 / 37 / 0 | 274 / 41 / 2 SKIP | 6 |

**AB=0 numbers are IDENTICAL to the recorded watermark at `799f2e76`+port ⇒ zero regression from this seat.**
⚠ **AND THE AB=0 SWEEP IS NOT EVIDENCE FOR THIS PORT** — it is structurally blind to every line changed here (ARCH §7 2b: citing an unmoved battery as a gate is a FALSE CLAIM). The AB=1 sweep is this rung's real gate.

**AB=1 deficit, enumerated — the SAME TWO in BOTH modes: `1011_func_redefine` · `test_math`.** Same set in m3 and m4 ⇒ **SEMANTIC defect, not a medium defect.** AB=1 also **FIXES** one m4 program (`097_define_capture_return_d2probe`) — that is the whole DIVERGE 5→6 delta.

## 5. ⭐⭐ ROOT CAUSE OF `test_math`: THE FUNCTION NAME ALIASED TO A FORMAL — WITNESS MINTED

`corpus/lib/math.sno` uses the standard SPITBOL Ch.8 accumulator idiom throughout: `DEFINE('max(max,x)')`, `min(min,x)`, `abs(abs)`, `sign(sign)`, `gcd(gcd,b)r` — **formal slot 0 carries the FUNCTION'S OWN NAME**, so the result variable and formal 0 are the same name. (`lcm(a,b)g`, the one prototype with a distinct first formal, is NOT in the broken set.)

**MINIMAL REPRO + ORACLE:**

```
DEFINE('mx(mx,x)')          :(mx_end)
mx   mx = LT(mx,x) x        :(RETURN)
mx_end
```

| call | SPITBOL | AB=0 | **AB=1** |
|---|---|---|---|
| `mx(3,7)` (guard TAKEN) | 7 | 7 | 7 ✅ |
| `mx(9,2)` (guard NOT taken) | **9** | **9** | **2** ⛔ = formal 1's actual |
| `m3(9,2,5)`, 3 formals, never assigned | **9** | **9** | **null** ⛔ |
| `nn(a,x)` NON-aliased control | null | null | null ✅ |

⇒ **the AB result read takes the WRONG GVA SLOT when the function name aliases a formal, and the error SCALES WITH `nformals`** (2 formals → formal 1's actual; 3 formals → off the end → null). The non-aliased control is correct in every arm.

⛔⭐ **THE DISCRIMINATOR IS THE FAILING GUARD, AND THE OBVIOUS PROBE IS VACUOUS BY SYMMETRY.** `mx(3,7)` succeeds under **every** arm, because when the guarded assignment is TAKEN the result and formal 1 hold the *same value*. Only a call whose guard FAILS separates them. A seat probing this with the natural "does max work?" test gets GREEN and concludes the AB path is clean. (Same class as ARCH §7 2b-0 / the s217 vacuous-probe lesson, arrived at from the opposite direction.)

✅ **WITNESS MINTED (slice-9 recipe): `corpus/probe/ab_name_alias.sno` + SPITBOL-generated `.ref`. Two-sided at mint: AB=0 ORACLE-EXACT, AB=1 DIVERGES.** This is the regression canary for the fix; it did not exist before and the defect had no falsifier.

⚠ **NOT FIXED THIS SEAT — deliberately.** The remaining budget could not have gated a lowering/slot-mapping change (watermark re-prove + AB=1 sweep + regen). Convicting it to a named mechanism with a two-sided witness is the complete unit of work; a half-gated fix is not.

## 6. ⚠ SMALLER CORRECTIONS OF RECORD

- ⛔ **`5416ed56` DOES NOT EXIST IN THIS REPO.** The cursor cites it four times as the RTX-FUNC-1/-2 hash of record. The landing is **`799f2e76`** (verbatim-matching message, ancestor of HEAD). **Third stale-hash incident in this file** after `165e6ba` and the s8 watermark rebase. ⭐ A hash minted pre-rebase and written into prose rots exactly like a symbol name or a line number.
- ✅ **`.s` regen ×3 RUN: benchmark / feature / demo all report ZERO CHANGED ARTIFACTS.** Not a skipped debt — a **computed proof** that default-arm emission is byte-identical, which is the expected and correct result for an AB-arm-only edit.
- ✅ **`pattern` smoke FAIL (6/7 both modes) EXONERATED STRUCTURALLY, WITHOUT A REBUILD CONTROL.** The program (`S='abc'; S 'b' = 'X'`) emits **zero** `fn_cell`, **zero** `g_monitor_bin`, **zero** `_act_α` ⇒ incapable of reaching either edit. Its own defect (yields `X`, want `aXc` — replacement clobbers the whole subject) is a live MATCH-family bug, pre-existing, unrelated.
- ⚠ **ALL 7 SYMBOLS RTX-FUNC-4 NAMES ROUND-TRIP** in the tree (step 0b clean) — no phantoms this time. The rung was wrong about behaviour, not about names.
- ⛔ **CONCURRENCY:** this seat edited `bb_func_activate.cpp` AND `bb_call_proc_staged.cpp`. The former is marked NOT-CONCURRENCY-SAFE and cost a concurrent seat a stash on 2026-08-10. Routing was requested in-chat before commit.

## 7. OWED NEXT

1. ⭐⭐ **FIX THE NAME-ALIAS SLOT READ** — `corpus/probe/ab_name_alias.sno` is the two-sided gate, already minted. This plus `1011_func_redefine` is the whole gap to AB default-on.
2. **`1011_func_redefine`** — AB=1 produces NO OUTPUT AT ALL (not a wrong value). Separate symptom from §5; not yet characterised; DEFINE re-execution flipping `fn_cell` is the obvious first suspect and is untested.
3. **RTX-FUNC-5 MEASURE** — now runnable in BOTH media for the first time. ⛔ **NO SPEED NUMBER IS QUOTED IN THIS FINDING.** The three-arm rail (`bench_rtx_3arm.sh`) was not run; ARCH §7 step 4's min-of-N rail defect is still open and nothing below ~1.10× is trustworthy. Prior seats' 1.17×/1.16× stand unchallenged and un-re-measured here.
4. Give RTX-FUNC a real `SCRIP_RTX_CALL` template arm, or amend the EVERY-RUNG kill-switch clause to name the AB arm as the kill-switch for TEMPLATE rungs (owed since s_this+3; now owed twice).
5. `x86()` family-wide fall-through bomb + real `"leave"` encoder + `sub`-to-memory arm — all still need the `x86_asm.h` seat (Lon routes).
6. `roman.sno` live-across-call defect — untouched this seat.
