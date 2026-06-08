# HANDOFF — 2026-06-08 24th attended run (Opus 4.8) — FIX-7b XK_REGDISP/ro dispatch half

**Result:** FIX-7b COMPLETE. SCRIP @ **2ec1175** (local==origin). `.github` this commit. Cursor UNMOVED (`bb_aggregate_nb.cpp`, LAP 3 start — 7b touched no ring file). FIX-7 rung STAYS OPEN (7c/7d remain).

## What landed (x86_asm.h ONLY + tracker note)
The 22nd run landed the label/comment half (11a3062 + 050f07d). This run landed the remaining XK_REGDISP/ro half:

1. **`XK_REGDISP` operand** — added to the operand enum, plus two `x86_parse` cases:
   - general `qword ptr [reg+disp]`, placed AFTER the `qword ptr [r12 + `/`qword ptr [rsp + ` specializations (so XK_FR64/XK_RSP64 keep their early-return paths);
   - bare `[reg+disp]` (the lea text form), placed AFTER the memidx8 `*8]` case and BEFORE the generic XK_MEMIND catch.
   - Both guarded on `x86_is_reg(base) && a numeric disp ending in ']'` → existing XK_MEMIND / XK_MEMIDX8 / XK_R13RCX / XK_RIPSEAL parses are byte-untouched.
2. **`x86()` dispatch** for the reg_disp32 family via the existing mnemonics:
   - `mov`: `XK_REGDISP+XK_REG → x86_reg_disp32_store64`, `XK_REGDISP+XK_IMM → x86_reg_disp32_store_imm64`, `XK_REG+XK_REGDISP → x86_reg_disp32_load64`;
   - `lea`: `XK_REG+XK_REGDISP → x86_reg_disp32_lea64` (placed BEFORE the generic `XK_REG/XK_REG` lea catch).
3. **`ro_load_q` + `ro_seal_str` dedicated mnemonics** — the sealed-slot index `n` can't round-trip through an operand string (`ro_load_q` emits Lrec+Jrec RIP-load; `ro_seal_str` emits Drec + 8-byte payload), so they take `n` directly: `x86("ro_load_q", reg, n)`, `x86("ro_seal_str", n, lit)`.

## ⛔ Scope finding (changes the 7c picture)
The headline "227 bypass calls" splits as frame_* 115 / reg_disp32_* 71 / ro_* 41. **frame_* is ALREADY dispatched via XK_FR64** (mov dispatch lines 547/548/551 → `x86_frame_store64`/`mov_imm64`/`load64`). So frame_* is pure **7c call-site conversion**, not a 7b dispatch gap. 7b's actual additive surface was the **6 dispatch entries** above. ~221 call-site conversions (frame_* 115 / reg_disp32_* 71 / ro_* ~35) are 7c work.

## Byte-proof (the "do NOT land unexercised" mandate)
Standalone harness compiled against the REAL `x86_asm.h` (define `g_medium`/`g_emit`/`g_flat_node_id` + `u32le`/`u64le`; toggle `g_medium`), comparing every new `x86(...)` form against its existing helper byte-for-byte, BOTH media (TEXT + BINARY), sweep = 14 legal bases (low3≠4, i.e. not rsp/r12) × 13 displacements (0, disp8 boundary ±127/128/−129, disp32 65536, …) × 10 dst/src regs (incl. r8+ for REX.R/B) × 8 immediates + the ro slot/literal matrix → **checks=13960 fails=0**. The forms are byte-identical to the (already-verified) helpers by construction; the probe verifies the parse+dispatch wiring across the range.

**Recipe note for 7c / future encoder work:** `scrip` statically embeds the template objects (`g++ ... /tmp/si_objs/*.o -o scrip`), and `make` has NO header-dependency tracking — so after editing `x86_asm.h` a **forced rebuild** (`make -B scrip` + `rm out/libscrip_rt.so && make libscrip_rt`) is required for a meaningful gate run. A plain `make scrip` / `make libscrip_rt` will report "nothing to be done" and silently test stale objects.

## Gates (green at floors, identical to baseline — additive + behavior-neutral)
smoke m4 7/7 HARD · pat M4 19/0 · prove_lower 68 PASS + 3 inherited FAIL rc=0 (law-5 trio) · purity 2-floor (bb_call_write_slot, bb_every) · bin_t 0 · handencoded 0 · vstack 3 · sno_pat_reg HARD · icon crosscheck 4/4 (modes 2+3 HARD) · pl crosscheck 4/4.

## Concurrent absorbed
**IRD-3 TO e8c9d49** (IR_interp.c + lower.c — mode-2 consumer reads operands[], guard decoupled from slot-emptiness) landed mid-push; my commit rebased CLEAN (zero file overlap). Per the 8th-run precedent, rebuilt + re-ran the HARD gates on the combined head 2ec1175 — all green, e8c9d49 regressed nothing. First push also hit an auth miss (the clone lacked the token in the remote URL); fixed with `git remote set-url origin https://TOKEN@github.com/snobol4ever/SCRIP`.

## Next-session order (GOAL FIX-7, unchanged)
FIX-4 (gvar 3c capture) → FIX-3 (=bb_call LANGUAGE-BLIND ONE-IR-ONE-LOGIC split; bb_return op_sa-relocation is the landed model; FIX-7 counters as acceptance gates) → 7c SWEEP LAP 3 from `bb_aggregate_nb` (now ALSO converts the ~221 reg_disp32/frame/ro bypass call-sites to `x86()` forms, asm-diff per stop).

## Outstanding verdicts (6, unchanged)
x86_movimm uint32-truncation (bb_call_fn) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (owner PL-GZ) · m2 disj-backtrack silent-empty (owner PROLOG-BB) · IRD-2b IR_t.own DEVIATION ratification · ml comment-substring false-positive (harden regex vs reword — FOR LON).
