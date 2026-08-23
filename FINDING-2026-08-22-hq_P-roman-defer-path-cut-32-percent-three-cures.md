# FINDING — ROMAN'S DEFER PATH CUT 32.4%, THREE CURES, ALL LANDED AND PUSHED

**Seat:** hq_P · **2026-08-22 s260** · **Class:** MEASURED + CURED · **RT_OPT=`-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer`**
**Instrument:** callgrind Ir at FIXED WORK (`echo 2000 | ./roman`), mode-4 native binary.
**⛔ OUTPUT VERIFIED ON EVERY ARM BEFORE ANY NUMBER WAS BELIEVED: `check: 1102`.** The rig REFUSES to print an Ir number when the output is anything else.

## ⛔ WHY THIS SEAT CURED INSTEAD OF BRIEFING

**Lon, in-chat s260: "Target ROMAN. Run in a loop. Find the biggest bottleneck, then fix. Rinse, repeat."** That
overrides MEASURE-FREELY-CURE-NEVER for this row, per THE LOOP clause 6. Routed to `GOAL-HQ-PERFORM.md` § LON
OVERRIDE s260 the moment it landed. Scope is the ROMAN speed row on this seat, not a general repeal.

## The result

| arm | Ir @ N=2000 | Ir/iter | Δ | check |
|---|---|---|---|---|
| session baseline `f4657712` | 80,371,475 | 40,186 | — | 1102 ✓ |
| + FAIL-strcmp guard | 77,638,799 | 38,819 | −3.40% | 1102 ✓ |
| + one resolution not two | 62,788,744 | 31,394 | −19.1% | 1102 ✓ |
| + drop the unobservable dfx frame | **54,315,629** | **27,157** | **−13.5%** | 1102 ✓ |
| **cumulative** | | | **−32.4%** | |

⭐ The baseline reproduces this seat's own s259 measurement to **36 Ir in 80.4M (0.00004%)** — the rail is exact.

## The three cures

1. **`strcmp(varname,"FAIL")` on every deferred execution** — a full libc call to recognise one reserved name,
   2.96% of the program. `strcmp(v,"FAIL")==0` implies `v[0]=='F'`, so a first-char guard cannot change an answer.
2. ⭐ **TWO name resolutions per deferred node, not one.** The emitted box called `rt_defer_get_pat_dtp` and then,
   on the not-a-pattern fall-through, `rt_defer_run_all` — and **both opened by resolving the same baked literal
   through the global name table**, back to back, with only a `test` and a `jz` between them. callgrind named the
   pair exactly: `rt_defer_nv_read'rt_defer_get_pat_dtp` **594,060 Ir** and `rt_defer_nv_read'rt_defer_run_all`
   **594,060 Ir** — *identical counts*. `rt_defer_probe_run` resolves once and returns both answers **in registers**
   (rax=fn, rdx=dtp-or-cursor), so RULES.md's NO-NEW-GLOBALS rule is met by construction, not by grant.
3. ⭐ **A dfx frame pushed and popped with nothing in between.** `rt_defer_run_all` pushed a `g_dfx` frame, stored
   the value, and had `c_rt_defer_close` pop it straight back off — no call out, no emitted code, no assembly in
   the gap. Pure ceremony, and not cheap: `rt_dfx_push` 3.78% plus the pop, the 24-byte struct copy and the
   top-of-stack check. Also: a **one-byte** compare was calling `__strncmp_avx2` (1.70%).

⛔ **THREE CASES DELIBERATELY KEEP THE OLD TWO-CALL PAIR**, because for them the second read is not redundant:
`*`-prefixed names (get_pat_dtp PUSHES to `g_spk`, run_all POPS — producer/consumer, not repeat), `DT_X` (resolving
calls a procedure that may itself assign the variable), and a `DT_P` whose `fn` has not materialised.

## ⭐ THE CONTROL, and why it is the load-bearing part

`SCRIP_DEFER_MERGE=0` on the **same binary** returns the merged entry to the original two-call pair:

| | ON | OFF |
|---|---|---|
| after cure 2 | 62,788,744 | 81,444,908 |
| after cure 3 | **54,315,629** | **82,157,813** |

Both OFF arms print `check: 1102`. **A broken program is fast** — hq_C's s259 warning — so the killswitch is what
distinguishes *work removed* from *work skipped*. Corpus at `-O2` on every arm: **m3 355/359, m4 354/359 + 2 SKIP**,
fail-set byte-identical to the recorded baseline (`160_pat_alt_inner_gen_resume`, `demo_treebank`, and the two
`-O2`-only reds `161_pat_defer_fn_nested_match` and `demo_porter`). `test_gate_emit_no_lang` and
`test_gate_template_medium_invisible` both green.

## ⛔ TWO CORRECTIONS I OWE THE RECORD

1. **I diagnosed the wrong root cause first.** Seeing `T` excluded from the GVA fast path, I concluded
   `graph_has_local` was over-conservative because SNOBOL4 locals are dynamically scoped — and the emitted
   `ROMAN_α` prologue does confirm that (`mov rax,[r9+32] # T` … `mov [r9+32],0` … restore). **But the deferred
   name is not `T`.** `.S1` resolves to **`"PATV$0"`**, a compiler-generated marshalling variable that
   `gva_collect_graph` (`emit.cpp:3329`) skips by design. The GVA arm is unreachable here for a different and
   legitimate reason. The measured redundancy that the cures actually address never depended on that reading.
2. **`-Bsymbolic-functions` is not the win it looks like.** The runtime is a PIC shared library, so intra-library
   calls go through the PLT. Relinking the same objects with `-Wl,-Bsymbolic-functions`: 62,071,844 vs 62,788,716
   = **−1.14% only**. PLT cost is indirect-branch and cache, which **Ir does not measure**. Dropped, not adopted.

## ⭐ THE NEXT ROW, NAMED AND SIZED

`NV_GET_fn'rt_defer_nv_read` **14.85%** + `__strcmp_avx2'NV_GET_fn` **4.37%** = **19.2%** — the ONE remaining
by-name resolution per deferred execution, 140,381 calls at ~74 Ir each. This is the FINDING-s259 "narrow
direction": resolve the deferred name to its `NV_t*` **once** and follow a pointer, SPITBOL's `vrblk` discipline.
`core.c`'s own memo comment already establishes the soundness (workspace blocks never move or free; `NV_SET_fn`
reuses rather than shadows) and the two hazards (stack-buffer pointer keys; shadowing, cured by `g_nv_memo_gen`).
⭐ **A per-site slot already exists — `g_sno_defer_cells[4096]`** — currently allocated only when `ci >= 0`, which
requires a GVA-eligible name and so never fires for a `PATV$` site. Extending `ci` to merged sites would give this
cure a home **without a new global**.
