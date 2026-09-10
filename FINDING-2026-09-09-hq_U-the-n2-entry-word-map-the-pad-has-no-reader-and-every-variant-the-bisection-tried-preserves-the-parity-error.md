# The N-2 entry-word map: the "pad" has no reader, and every variant the bisection tried preserves the same parity error

**Written 2026-09-09 by hq_U** · SCRIP `df41c4250` · row CEO-481 (N-2, routed to hq_U ahead of the `&error` class). **MAP AND ANALYSIS ONLY — NO CODE TOUCHED, no build, tree clean.** Built from the sources plus the cto's bisection table; the empirical arm is named at the bottom and is **not** run.

## The map, with every writer named

Two sites hand a generator callee its entry frame and they are hand-written twins of each other:

| word | compiled site (`bb_call_proc_staged.cpp:689`, `bcps_spine_gen_arm`) | runtime twin (`rt.c:1068`, `rt_genp_spine_enter_n2`) |
|---|---|---|
| `[rsp+0]` | γ | γ |
| `[rsp+8]` | ω | ω |
| `[rsp+16]` | REGION — **`emit.cpp:2955` calls this `unused` under N-3** | REGION (`%rsi`, passed as 0 by the only caller, `rt.c:1109`) |
| `[rsp+24]` | L7 | L7 |
| `[rsp+32]` | **"pad"** | **"pad"** |
| `[rsp+40]` | N-2 ABI word (`icn_gen_regime()` only) | N-2 ABI word |
| ANCHOR | `[rsp+48]` | `[rsp+48]` |

⛔ **The two sites are two hand-written copies of one ABI, and the tree says so in its own words** — `rt.c`'s comment exists because `b49fd7a4` grew the compiled site by one word and *did not* grow the twin. That is the same class as the seat-identity map and the `PROCVAL_SLEN` copy in `rtx_icncall.s`: one contract, two hand-written copies, no gate comparing them.

## ⛔ THE SLOT AT `[rsp+32]` HAS NO READER, AND THE FILE CONTRADICTS ITSELF ABOUT WHOSE WORD IT IS

`bb_call_proc_staged.cpp:689` ends with: *"…would keep the region at +16 and silently move the pad, **which is the slot the selfrec depth is read from at [entry rsp+32]**."*

**`selfrec` occurs exactly once in the entire tree — in that sentence.** `grep -rniE 'selfrec|self_rec|self-recur' src/` returns one line, the comment itself. There is no writer and no reader of a "selfrec depth" anywhere.

And twenty-nine lines later, the *same file* gives the same two words a different owner — `bb_call_proc_staged.cpp:718`: *"the PL-CALL-ALIGN pad+L7 push just above … is **this call site's OWN transient bookkeeping, not a retained callee frame**."* The push's own annotation agrees with `:718` and not with `:689`: **PL-CALL-ALIGN — "pad the lone L(7) push to a 16B unit"**, introduced because one bare 8B push left rsp 8-mod-16.

⭐ **So the word is an ALIGNMENT pad by the account of the code that emits it, and a DATA slot by one clause of one comment that names a reader which does not exist.** Both cannot be true, and only one of them has a `grep` behind it. This is the *correct-procedure-false-explanation* shape from RULES.md, in its most expensive form: the false half is the half that tells the next seat what the word is FOR.

## ⭐ WHY EVERY VARIANT IN THE BISECTION CRASHED — A PARITY ARGUMENT, OFFERED AS A PREDICTION

The cto measured that dropping the pad makes the parity gate 2/2 green and the tracer witness exit 0, **and crashes `parse` and `patchu` in both modes under every combination tried** — prologue anchor `lea rcx,[rsp+48]` left or moved to `40`, runtime twin reserve `16` or `8`; `chkhtml` reverts to its old FAIL at 48 and crashes at 40.

Read against the map, **every one of those knobs moves memory by 8, and none of them restores the 8 bytes the pad removal took off the compiled path**:

- dropping the pad removes **8** bytes from the callee's entry frame, so the body runs at the opposite 16-byte parity;
- the ANCHOR `48 → 40` constant changes **where ANCHOR points**, not the body's rsp parity;
- the runtime twin's `16 → 8` reserve changes parity **on the twin's path only** (`rt_genp_entry_c`, the by-name / procedure-value generator door), not on the compiled `bcps_spine_gen_arm` path.

⭐ **That predicts the table exactly, including its two odd rows:** a whole-program crash wherever the compiled generator path is reached, `chkhtml` merely reverting to its prior FAIL where it is not, and the parity gate and tracer witness going *green* because they exercise the arm the removal genuinely fixes. It also predicts the symptom shape both existing comments already record for this exact error — **"SIGSEGV in the first `movaps` a callee reaches"**, with no SCRIP frame in the backtrace.

⛔ **This is a PREDICTION, not a measurement, and the distinction is the point** — it comes from reading two comments and an arithmetic, and the last seat to trust a comment about this slot is why the row exists. It is cheap to falsify, and falsifying it is the next arm: **remove the pad AND remove or add a second 8-byte word on the compiled path** (or move it across the call, which is what the cto and the ceo independently concluded), then re-run `parse`, `patchu` and `chkhtml`. If the parity argument is right, one 16-byte-preserving edit turns the whole table green at once; if it is wrong, the crash survives a parity-neutral edit and the slot really is read as data — at which point **the reader must be produced by name**, not asserted.

## The arms this row owes (CEO-481, restated so they are runnable)

parity gate · the tracer witness · `parse`, `patchu`, `chkhtml` through `util_ipl_grade_programs.sh` · Icon master per-entry identity · SNOBOL4 FAIL=0.

## NOT CLAIMED

- **No code touched, nothing built, nothing measured by me.** The map's rows are read off the two emitting sites; the contradiction and the absent reader are `grep` results and are reproducible in one command each.
- I have **not** confirmed which of the two doors `parse`, `patchu` and `chkhtml` each take, and the parity argument depends on it — that is the first thing to check and it is one `--compile` plus a grep for the call site, not a guess.
- `emit.cpp:2955` calling `[rsp+16]` **`unused`** while both twins call it `REGION` is a **third** disagreement about this frame that I have not resolved and am not folding into the parity argument.
