# FINDING — seat09: RTX-29 stand-down (`3fce9831`) did not cure 3 of its 6 assigned crash programs — `jcon_mindfa` and `jcon_recogn` still SIGSEGV both modes, `jcon_genqueen` still SIGSEGV in compile mode, and the two verified backtraces are NOT the RTX-29 mechanism

**Date:** 2026-08-24 · **Seat:** seat09 (FLEET-12) · **Row:** `icon-regression-232-to-169` (rank 0) · **Build:** `make pristine` EXIT=0, RT_OPT=-O0 (default, no `-O2`) · **Tree:** SCRIP `ab9c087c` (fresh pull, clean).

## 0. Verdict, up front

`audit-rtx29-icon-table-int-chain-walk-post-s262` is closed DONE (seat08's claim, commit `3fce9831`, `.github` `35059811`), and this task's own LEDGER records all 6 of its assigned programs (`jcon_table`, `jcon_random`, `jcon_fncs1`, `jcon_mindfa`, `jcon_recogn`, `jcon_genqueen`) as routed to that class. **A fresh full-corpus run at HEAD shows 3 of those 6 still crash: `jcon_mindfa` (SIGSEGV, both `interp` and `compile`), `jcon_recogn` (SIGSEGV, both modes), `jcon_genqueen` (SIGSEGV, `compile` mode only — `rc=1` in interp).** `3fce9831`'s own verification used an Icon *smoke* run (14/14) and a narrow 5-line table-int repro, not the 293-program rung suite — the smoke set does not include any of these three programs, so the regression to the smoke set is real but did not exercise this gap. **Root cause is NOT re-diagnosed here for `jcon_genqueen`** (not re-run under gdb this session — time-boxed, see §4) but IS established for the other two, and it is two DIFFERENT mechanisms, NEITHER of which is RTX-29's `.Lsub_table_int`/`.Lsub_hash_init` chain-walk:

## 1. `jcon_mindfa` — corrupt string descriptor reaches the table-hash C path, `aggregates.c`

Clean, fully symbolicated backtrace (`gdb -batch`, `CSN_NO_SEGV_HANDLER=1 SCRIP_NO_SEGV_HANDLER=1`, `--run` i.e. m3):

```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff41777e7 in _tbl_h_str (k=0x7fffffbf83d0) at src/runtime/aggregates.c:211
211	    while (m >= 8u) { h = (h ^ *(const unsigned long long *)p) * 0xFF51AFD7ED558CCDull; p += 8; m -= 8u; }
#0  _tbl_h_str (k=0x7fffffbf83d0) at src/runtime/aggregates.c:211
        p = 0x7ffff7f0fffa ""   n = 4294967295   m = 4293049599   h = 5711972849520236552
#1  _tbl_hval (k=0x7fffffbf83d0) at src/runtime/aggregates.c:267
#2  _tbl_hkey (k=...) at src/runtime/aggregates.c:280
#3  table_set_descr_d (tbl=0x7fff8afffb00, k=..., val=...) at src/runtime/aggregates.c:421
#4  0x00007ffff4130904 in rt_assign_var () at src/runtime/rtx/rtx_icnvar.S:184
#5  0x00000000004506f0 in ?? ()   <- JIT'd m3 blob, no symbols, expected
```

`n = 4294967295` (`0xFFFFFFFF`) is a sentinel-shaped length reaching a string-hash loop that reads 8 bytes at a time off `p` — this is a **table SET with a string key whose descriptor's length field is garbage**, crashing inside the C hash helper, not inside any RTX-29 asm. `table_set_descr_d` is the general table-insert path (reached here from `rt_assign_var`, i.e. an ordinary `t[k] := v` assignment with `k` a string) — a different function from `rt_subscript_var`/`.Lsub_table_int`, which is a table-READ path RTX-29 patched. This is an insert-path defect with a corrupt-length string descriptor, unrelated to RTX-29's integer-subscript chain-walk.

## 2. `jcon_recogn` — jump into non-code, dead unwind

```
Program received signal SIGSEGV, Segmentation fault.
0x00007fffffbf9295 in ?? ()
#0  0x00007fffffbf9295 in ?? ()
#1  0x0000000000000000 in ?? ()
```

`0x00007fffffbf9295` is a **stack address**, not a code address — RIP landed in stack memory (frame pointer chain dead one frame later). This is consistent with a corrupted return address or an indirect jump/call through a bad pointer, not a data-only OOB read like RTX-29's or `jcon_mindfa`'s. No further diagnosis attempted this session (would need a hardware watchpoint on the corrupted return slot, which this container does not support per RULES.md — the ASM-DIFF-FIRST minimal-repro route is the next seat's correct starting point, not gdb-first).

## 3. `jcon_genqueen` — NOT re-diagnosed this session

Confirmed still `rc=139` in `--mode compile` (`rung36_jcon_genqueen`, `test_icon_rung_suite.sh --mode compile`), `rc=1` in `--mode interp` — this asymmetry was already flagged as a live `m3 ≡ m4` parity gap in this task's own prior LEDGER entry ("minor, not chased"). Not gdb'd this session; carrying the existing flag forward rather than re-deriving it.

## 4. Why this wasn't caught at RTX-29's own closure, and why I stopped here

`3fce9831`'s commit message grades "Icon smoke 14/14 both modes (unchanged)" plus a hand-written 5-line repro — neither includes `jcon_mindfa`/`jcon_recogn`/`jcon_genqueen`. The stand-down is a correct, narrowly-targeted fix for the mechanism it names (verified: the 5-line repro is 0/5 crashes post-patch) — it was never claimed to cover the full rung corpus, but this task's own LEDGER (mine, previous session) routed all 6 named programs to that row as one class, and that classification is now shown to be too coarse: at least 2 of the 6 (mindfa, recogn) crash via mechanisms RTX-29's patch never touches. **This FINDING does not fix any of the three** — diagnosing and curing two new, unrelated crash mechanisms is a properly-scoped row of its own, not a same-session extension of a triage task. Minted as `rtx29-standdown-residual-crashes-mindfa-recogn-genqueen` (rank 0); message sent to hq_C (RTX-29's closing authority) flagging the gap.

## 5. Fresh full-corpus numbers, HEAD `ab9c087c`, post-pull, `make pristine` clean

| instrument | PASS | FAIL | BADEXIT | XFAIL | TOTAL |
|---|---|---|---|---|---|
| `test_icon_rung_suite.sh --mode interp` | 245 | 18 | — | 30 | 293 |
| `test_icon_rung_suite.sh --mode compile` | 243 | 20 | — | 30 | 293 |
| `test_icon_all_rungs.sh` (`--run`) | 246 | 16 | 1 | 30 | 293 |
| SNOBOL4 `test_corpus_snobol4.sh` | 365/365 both modes, FAIL=0 SKIP=0 | | | | |

No code changed this session; this FINDING and the newly-minted row are the only new artifacts.
