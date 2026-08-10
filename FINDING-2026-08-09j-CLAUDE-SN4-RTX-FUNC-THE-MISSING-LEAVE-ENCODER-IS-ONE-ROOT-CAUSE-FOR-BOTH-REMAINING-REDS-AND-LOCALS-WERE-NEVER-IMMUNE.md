# FINDING 2026-08-09j — RTX-FUNC: the missing `leave` encoder is ONE root cause for BOTH remaining REDs, and locals were never immune

**Seat:** GOAL-SNOBOL4-RTX (RTX-FUNC). **Tree:** SCRIP HEAD `45de80bf` at open. **Mode:** m3 unless stated. **RT_OPT:** `-O0`.

---

## 1. The defect, in one line

`bb_func_activate.cpp:248` called **`x86("leave")`**. There is **no `"leave"` arm in `x86_asm.h`'s dispatch** (`grep -n '"leave"' src/templates/x86_asm.h` → **zero matches**; the only hits tree-wide are `x86_align_leave` and prose). The call emitted **NOTHING, in BOTH media**. The AB callee frame was therefore **never torn down**.

Proof it was silent, not merely wrong: the emitted TEXT for a DEFINE program contains **no `leave` instruction at all** — `grep -n "leave" probe.s` returns only `call rt_ab_leave_env@PLT` lines. Exactly **one** template call site used the mnemonic, so nothing else in the tree could have masked it.

## 2. It is the root cause of BOTH open REDs — they were never two bugs

| cursor item | mechanism |
|---|---|
| **REMAINING #1 — live-nested recursion** | β jumps to the caller's landing with `rsp` still ~one frame (144 B for nsave=3) BELOW the caller's block base, inside the dead callee frame. The landing's `[rsp+0]`/`[rsp+16]` restores then read frame residue instead of the caller's save block. |
| **REMAINING #2 — per-call leak** | one whole activation frame leaks per call. Measured: AB=1 SEGVs between **121,250 and 124,531** calls (bisected) vs **2,000,000 clean at AB=0** — a leak of order one frame per call. |
| **m4 AB=1 runtime SEGV** (the cursor's "blocked oracle", called a PREREQUISITE) | same missing teardown; the TEXT arm was never unwinding either. |

⭐ The cursor treated #1 and #2 as separate and speculated they "may share this root". **They do — and the shared root is neither of the mechanisms proposed.**

## 3. TWO INHERITED CLAIMS FALSIFIED

- ⛔ **"Locals are never affected" — FALSE.** `r_probe` (formal `N`, local `L`, result `T`) at AB=1 printed `post-call N=z L=z T=z`. The local is corrupted identically to the formal. The caller's **statement literal `'final '` was destroyed too** (`OUTPUT = 'final ' S(1)` printed `zz`). ⇒ the damage is not save-set-shaped at all; it is *everything the caller held live across the call*. The cursor built its "use this asymmetry to re-recognise the class fast" heuristic on this claim — **the heuristic is void.**
- ⛔ **The `±16` falsification of the rsp claim was INSUFFICIENT, and the discarded claim was the CORRECT one.** The prior seat shifted the landing read one slot (`16*i` → `16*i+16`), saw no change, and struck "rsp at the landing ≠ block base — DO NOT RE-RUN IT". A one-slot probe **cannot discriminate a 144-byte base error**: both reads land in the same wrong region and return the same residue. ⭐ **A probe must span the magnitude of the error it is meant to exclude.** This cost the ladder a seat and sent the next hypothesis (BOTH-MEDIUM miscoding of `x86_rsp_load64` with `"rcx"`) after an encoder that was already proven correct at source.

## 4. The experiment ladder that got there (cheapest-first, no gdb needed)

1. `r_two` — **two formals**. AB=1 → `z/z/z`, not `z/z/1`. **Kills the off-by-one class**: every formal resolves to the same source, so the error is a wholesale base error, not an index error.
2. `r_probe` — formal + **local** + result. → locals corrupted (§3), and the enclosing statement's literal destroyed ⇒ scope is wider than the save set.
3. Read the emitted TEXT: caller-side spill/install order and **both landings are CORRECT** (block slot 0 = N, slot 1 = L, restored before `add rsp,48`); α's spill offsets and β's restore loop are correct; GVA cells distinct (no aliasing). ⇒ **emission is right, so the frame is wrong.**
4. `grep '"leave"' x86_asm.h` → zero. Confirmed against the emitted `.s`.
5. **Quantified** the prediction: leak ≈ one frame/call; bisected the SEGV threshold; AB=0 control clean at 2M.

⚠ Note the false trails this ladder retired by measurement, not argument: red-zone smashing (α **does** `sub rsp,152`), save-slot/RES0 layout collision (member k at `-0x70-16k`, clear of `-0x58/-0x60`), GVA cell aliasing (cells distinct), and β-restore off-by-one.

## 5. Fix (SCRIP, this commit)

`x86("leave")` → `x86("mov","rsp","rbp") + x86("pop","rbp")`. Same effect; neither encoder touches flags (nor does `leave`); both are proven in-tree (`x86_srf_floater` :1966, `bb_glue_framed` :37).

⛔ **Deliberately NOT an `x86_asm.h` edit.** Adding a real 1-byte `"leave"` encoder is the better long-term form and is the RULES-preferred shape ("Missing instruction ⇒ ADD the encoder"), but `x86_asm.h` is **NOT-CONCURRENCY-SAFE** — **Lon routes that seat.** The pair keeps the repair inside the template this seat holds. **When that seat is routed, add the encoder and collapse the pair.**

## 6. Results — AB=1, m3, all oracle-exact vs `/home/claude/x64/bin/sbl`

`r_plain` `z` · `r_keepn` `z1` · `r_two` `z/1/m` · `r_probe` both lines · `recur2` **6** (was *Illegal data type*) · `fibonacci` **832040** (was *Illegal data type*). Leak: **2,000,000 calls clean** (was SEGV ~122k).

**Speed — min-of-N, in-program ms, `RT_OPT=-O0`:**

| bench | AB=0 | AB=1 | SPITBOL | AB=1 vs SPITBOL | directive baseline |
|---|---|---|---|---|---|
| `func_call` | 1441 | **1104** | 1166 | **1.06×** | 0.49× |
| `func_call_overhead` | 1457 | **1136** | 1172 | **1.03×** | 0.52× |
| `fibonacci` | 396 | **294** | 207 | **0.70×** | 0.37× |

Two of three are **past SPITBOL parity**, clearing the Lon directive's ≥0.80× falsifiable acceptance. `fibonacci` roughly doubled but still trails — consistent with the two surviving C crossings (`rt_ab_enter_env`/`rt_ab_leave_env`) costing per activation and therefore scaling with recursion depth. **That is exactly RTX-FUNC-1/-2, which are now unblocked.**

⚠ **These are NOT rail numbers.** `bench_rtx_3arm.sh` still lacks the min-of-N mode that the ladder says blocks every speed claim on this machine. Min-of-N in-program ms, one container, no pristine arm. **Treat as indicative until railed.**

## 7. Honest gate state — what is NOT proven

- **Default arm untouched BY CONSTRUCTION:** at `SCRIP_AB=0` the AB tail emits **zero** occurrences (`grep -c 'S_act_'` → 0). Every edit is inside the AB β tail.
- **`.s` regen ×3:** expected **zero-diff for THIS edit** (invisible at default), but the carried debt since `8172e54` is **still owed and NOT discharged here**.
- **NOT RUN:** full crosscheck at watermark; watermark re-prove; kill-switch CALL gate N≥4; m4 AB=1 end-to-end.
- 9 DEFINE-bearing corpus programs mismatch their `.ref` — **identically in both arms**, and they are `-INCLUDE`/input-driven demos run with `</dev/null`. Harness artifact, not a regression; not further characterised.
- `beauty.sno` was **NOT graded** — it needs its `-INCLUDE` harness; the ad-hoc run produced empty output and that is a harness failure, not a gate result. **Not quoted as a pass or a fail.**

## 8. Stale pointer of record

The live cursor cites SCRIP **`165e6ba`**, which **does not exist in this repo** (`git cat-file -t` → *Not a valid object name*). HEAD `45de80bf` carries a verbatim-matching message ⇒ pre-rebase hash drift, not a divergent tree. Same STALE-ORIENTATION class the RULES name.
