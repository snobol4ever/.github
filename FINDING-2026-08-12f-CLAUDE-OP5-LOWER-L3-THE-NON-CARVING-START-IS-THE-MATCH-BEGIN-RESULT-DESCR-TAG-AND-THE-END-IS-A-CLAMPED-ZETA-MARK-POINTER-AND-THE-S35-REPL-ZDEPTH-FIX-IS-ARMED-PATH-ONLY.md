# FINDING 2026-08-12f — CLAUDE-OP5 — LOWER L-3 — **THE NON-CARVING `start` IS THE MATCH_BEGIN RESULT-DESCR TYPE TAG (`DT_I`=3) AND THE `end` IS A CLAMPED `zeta_mark` GC POINTER. THE READ IS AIMED 16 BYTES LOW. THE WRITER WAS NEVER MISSING — s35's C-9 REPL-ZDEPTH CORRECTION IS ARMED-PATH-ONLY.**

**Fingerprint:** SCRIP `51934a9f` · corpus `14dc06bd` · `.github` `4a292e25`. Tree built AFTER `scripts/install_system_packages.sh` (packages were genuinely absent — see 2026-08-12d; building first would have reproduced the phantom m4 class). ZERO compiler bytes changed this session.

---

## 1. THE HEADLINE

L-3's third class ("non-carving var-length": `ARB` `SPAN` `BREAK` `REM`) does **not** suffer a displaced cursor. `IR_MATCH_REPLACE`'s reach-back to the match's `start`/`end` pair resolves **exactly 16 bytes below** the intended cells. At that wrong address sit, by the ZLS layout table:

| what replace INTENDED to read | what it ACTUALLY reads (−16) |
|---|---|
| ZLS **+48** `head.cursor` (the live anchor) | ZLS **+32** `result` DESCR of `IR_MATCH_BEGIN` — first dword = the DESCR **type tag** |
| ZLS **+72** `head.end` (stashed by `IR_MATCH_END`) | ZLS **+56** `head.zeta_mark` — a **GC pointer** |

`DT_I = 0x03` (`src/contracts/descr.h:49`). **That is the constant `3`.** It is flat across Series S because a type tag has no relationship to cursor position — which is exactly why "no displacement of any sign or slope can fix it" read true from the outside.

The `end` term is a pointer, i.e. astronomically greater than `slen`, and `c_rt_match_replace` clamps it: `if (end > slen) end = slen;`. **`end` is therefore reported as `slen` for every member of the class, always.**

## 2. THE WRITER IS FINE — THIS IS A READER DEFECT (corrects the s34 cursor's framing)

s34's cursor said: *"`(3, slen)` is a read of cells nobody wrote for this shape … find the writer, not an offset."* The first half is exactly right, the instruction was the right one to follow, and following it landed here. But the conclusion needs correcting for the next seat:

- **`IR_MATCH_BEGIN` DOES write `head.cursor` (+48) and `IR_MATCH_END` DOES write `head.end` (+72), correctly, in both the passing and failing shapes.** Verified in emitted asm: both siblings carry an identical `mov dword ptr [rsp+0], 0  # start_δ` / `add dword ptr [rsp+0], 1  # start_δ` pair from `bb_match_begin.cpp:72,78`.
- The defect is that **the READER's effective address is short by the replacement subtree's spine footprint.**
- ⛔ So "find the writer" is now DISCHARGED and the answer is "there was never a missing writer." Do not spend another session hunting one.

## 3. THE MECHANISM IS ALREADY NAMED IN-TREE — AND ITS FIX IS INCOMPLETE BY GUARD

`src/emitter/emit.cpp:841` carries the s35 **C-9 REPL-ZDEPTH** comment, which describes this defect verbatim:

> *"With zdepth=0 all four frame reads (`op_sa`, `op_sa+8`, `op_off`, `op_off+24` — subject lo/hi and match start/end) were short by exactly the subtree footprint and read stale stack: MEASURED +16 for a literal replacement, +80 for `A '-' B`, i.e. NOT a constant but the subtree's own zeta depth."*

That correction is set **inside `if (g_zd_arm) { … }`** (`g_zd_arm = zd_on[i] && …`, emit.cpp:2656). Shapes whose replace node does not arm the ZD path never receive it. **That is why L-3's rung text — "mechanism named, fix incomplete" — was literally true: the mechanism was found and repaired on one path only.**

⛔ **THE GATE WITNESS IS ALREADY WRITTEN DOWN, HONOUR IT:** the same comment states *"any fix hardcoding 16 passes the literal case and FAILS the concat case,"* gate witness **`P8_concat_repl`**. The correct term is the planner's under-cells quantity (`g_zd_wpop`, the same value line 842 hands to `op_wpop`), **never the literal 16 my probes happen to show.** Every probe on the l3 board uses a single-literal replacement, so this board **cannot by itself falsify a hardcoded 16** — it is structurally vacuous on that distinction. Any candidate fix must be judged on `P8_concat_repl` as well.

## 4. THE MEASUREMENT (m3, at my own HEAD — re-run, not transcribed)

Board reproduced row-for-row at `51934a9f` (recorded at `900060c7`): **3 PASS / 9 FAIL-silent**, the 3 PASS being the fixed-length controls. `EARN0=/home/claude/corpus/probe/l3 REPEAT=2 bash scripts/board_earn0_set.sh m3`.

`SCRIP_REPL_TRACE=1`, subject `'XXXXXXXXXX+efgYYYY'` (slen 18), true match `[10,14)`:

| probe | start | end | verdict |
|---|---|---|---|
| `len_nonterm` (control) | **10** ✅ | **14** ✅ | PASS |
| `span_nonterm` | **3** | 18 (=slen) | FAIL |
| `rem_nonterm` | **3** | 17 (=slen) | FAIL |
| `tab_nonterm` | 2 | 14 ✅ | FAIL (carving class) |

**THE MINIMAL PAIR:** `len_nonterm` and `span_nonterm` differ by exactly one token (`LEN(2)` vs `SPAN('ef')`), match the identical extent, expect identical output, and emit an identical `sub rsp,16` replacement-literal push with an identical `op_sa`. Only the start/end base differs — by exactly 16.

**BOARD-WIDE SPLIT (all 12 probes, `mov ecx, dword ptr [rsp+N]` at the replace site):**

| start_off | members | result |
|---|---|---|
| **64** (= ZLS+48, correct) | `len_nonterm` `len_pure` `lit_len` `pos` | the ONLY 3 PASSes are here |
| **48** (= ZLS+32, the tag) | `arb` `break` `rem` `rtab` `span` `tab_nonterm` `tab_linear3` `VACUOUS_terminal_trap` | **8 of 8 FAIL** |

Perfect correlation, no exceptions.

## 5. TWO INSTRUMENT DEFECTS THIS EXPOSED

- ⛔ **THE `SCRIP_REPL_TRACE` PRINT IS POST-CLAMP.** `gen_runtime.c:161` sits *after* `if (end > slen) end = slen;`. A traced `end == slen` is therefore **indistinguishable from `end > slen`, including from a raw pointer.** Every recorded "`end` arrives as `slen`" observation in this goal is really "`end` arrived as ≥ slen." This is why the class looked like a semantic end-of-subject (vacuous-witness) problem rather than the garbage read it is. **Moving that fprintf above the clamp is a one-line, zero-risk instrument upgrade and should precede the next measurement.**
- **`l3_spl_pos` reads the CORRECT slot (64) and still fails** ⇒ POS/RPOS is genuinely a separate defect, not a member of this class. This independently confirms the s34 four-class table by a mechanism the table did not use.

## 6. MY OWN HYPOTHESIS THAT DIED (recorded per anti-pattern §2 — the fourth to die on this rung)

I first convicted the **PATCTX register-save block**: the `.s` annotations show `mov qword ptr [rsp+48], r13  # outer_Σ` and `[rsp+72], rax  # cap_gen` at MATCH_BEGIN, matching SPAN's read offsets 48/72 exactly. I nearly published "replace is reading the saved outer Σ/Δ registers."

**It is false.** Those stores are in a *different rsp regime* — rsp moves repeatedly between MATCH_BEGIN and the replace site (`sub rsp,32`, `mov rsp,[r12-16]`, `add rsp,16`, `sub rsp,8/16`, and the `sub rsp,16` literal push). Static displacement equality across a moving FORTH spine is meaningless. In ZLS terms `sigma_save` is at **+96**, not +48. The `--dump-zeta` layout table is the authority and it killed the conviction.

⛔ **RULE EARNED (seventh conviction in this goal): on the RSP spine, never compare two `[rsp+N]` displacements taken at different program points without first proving rsp is unchanged between them.** The `.s` `#` annotations are per-site labels, NOT a frame map; `--dump-zeta` is the frame map.

## 7. NEXT SEAT, IN ORDER

1. **Move the `SCRIP_REPL_TRACE` fprintf above the clamp** (instrument first — it is currently lying about `end` on every failing row).
2. Determine why the replace node declines the ZD arm in var-length pattern graphs (`zd_on[i]` at emit.cpp:2656) — that is the single guard separating the 64-group from the 48-group.
3. Apply the subtree-footprint correction on the unarmed path using **`g_zd_wpop`, never a literal 16**; judge on `P8_concat_repl` (concat replacement, +80) as well as the l3 board, which is vacuous on that distinction.
4. `TAB`/`RTAB` remain their own row: `tab_nonterm` reads at 48 like the class, but its `end` arrives CORRECT (14) while the class's is clamped — so TAB is plausibly this same 16-byte defect on `start` only. Re-measure TAB the moment the 16 is fixed before spending anything on s41's Series-T displacement theory; the displacement framing may fall out entirely.
5. `bal` still owns its row (wrong on both terms, and the only capture-failing member that also splices wrong).

**UNBLOCKS:** LOWER L-3 (root cause CLOSED to a named guard and a named correct term; "find the writer" discharged as a non-existent target) · LOWER L-4/L-5 unaffected. **m3 only — the m4 arm of this board is UNMEASURED, not green; BOARD B-0 still owns it.**
