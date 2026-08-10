# FINDING 2026-08-10 — RTX-FUNC-11: THE 17 BEAUTY DRIVERS ARE **ONE** DEFECT IN **ONE INCLUDE**, AND THE FAULT IS A SCALE-THRESHOLDED, ADDRESS-LAYOUT-SENSITIVE MEMORY FAULT — NOT A DEFINE/AB DEFECT

**Seat:** Claude Opus (fresh clone seat, same container as the clean-clone seat that minted RTX-FUNC-11).
**Fingerprint:** SCRIP `bce9a4b` (binary md5 `63d023df309a`, mtime 23:05:23, **verified unmoved across every measurement below**) · corpus `bea31de` · `.github` `1050194`. `RT_OPT=-O0`, AB=0 (default), mode 3 unless stated.
**Status:** NOT root-caused. MONITOR-FIRST was **not** discharged — see §6. This finding is reduction + fault characterisation only.

---

## 1. CONFIRMED INDEPENDENTLY
17/17 `beauty_suite/*_driver.sno` → `rc=139` (SIGSEGV), zero stdout. Reproduces the clean-clone seat's claim exactly.

## 2. THE COMPILER IS CLEAN — THIS IS A RUNTIME FAULT
`scrip --compile fence_driver.sno` → **rc=0**, 2,318,398 bytes of asm. The front-end does not fault.

## 3. BOTH MODES FAULT — NOT MODE-3-SPECIFIC
That asm, assembled+linked by the project's own recipe (`gcc -no-pie … -lscrip_rt`) and run: **rc=139**. ⇒ the defect is in emitted code or `libscrip_rt`, i.e. the surface **shared** by m3 and m4. Any hypothesis that is m3-only is excluded.

## 4. ⭐ THE REDUCTION — 17 DEFECTS COLLAPSE TO 1
- A two-line program — `-INCLUDE 'global.sno'` + `END`, **no driver body at all** — segfaults.
- The driver body **with the `-INCLUDE` removed** runs `rc=0` and its output is **byte-identical to `fence_driver.ref`**. FENCE semantics are correct; the driver is innocent.
- **17/17 drivers include `global.sno`.** ⇒ this is ONE defect reached 17 ways, and the "13 of 17 are FAILs in the broad sweep" arithmetic should not be read as 13 independent bugs.

## 5. ⭐ `global.sno` CONTAINS **ZERO** `DEFINE(` — THE AB/ACTIVATION-BLOCK WORK IS EXONERATED
The entire recent RTX-FUNC ladder is DEFINE/activation-block machinery. The crashing include has no DEFINE at all. **RTX-FUNC-11 is not downstream of RTX-FUNC-0..10 and must not be sequenced as if it were.**

### The crashing shape (`global.sno` tail, lines 157–163)
```
    UTF_Array = SORT(UTF)
    i = 0
G1  i = i + 1
    $UTF_Array[i, 2] = UTF_Array[i, 1]  :S(G1)
    UTF_Array =
    i =
```
A TABLE of N entries → `SORT` → array; loop with **indirect assignment** (`$`) creating one variable per entry, terminating on **array-subscript failure**; then the array variable is nulled. Prefix-truncation of `global.sno` is monotonic (lines 20…161 all clean, 162 and 163 crash) and line 162 is `UTF_Array =` — but see §7: the small-scale standalone form of this shape does **not** crash, so the tipping line is necessary, not sufficient.

## 6. ⭐⭐ THE SCALE LAW — AND WHY N=1 IS A COIN FLIP HERE
Holding head+tail fixed and varying only the number of `UTF[...]` table entries, **N=8 per point**, ASLR on:

| entries | clean | SEGV |
|---|---|---|
| 64  | 8 | 0 |
| 88  | 8 | 0 |
| 104 | **4** | **4** |
| 112 | 0 | 8 |
| 125 | 0 | 8 |

⛔ **A single-run binary search over this range reports a false sharp threshold.** Mine did: it returned "103 clean / 104 crash", and n=104 then passed twice on re-run. **This is the `160_pat_alt_inner_gen_resume` class (ARCH §7 step 3) arriving in the RTX-FUNC-11 axis** — any threshold, bisect verdict, or fix-confirmation taken at N=1 anywhere in 88 < N < 112 is luck, not evidence. Bisect for regression-vs-debt **must** use a workload at N≥112, where the fault is 8/8 deterministic.

## 7. FAULT CLASS: ADDRESS-LAYOUT SENSITIVE ⇒ MEMORY CORRUPTION
Disabling ASLR (`setarch -R`) **does not fix anything — it changes the signal**:

| workload | ASLR ON | ASLR OFF |
|---|---|---|
| 17 drivers | 17 SEGV, 0 clean | **5 SEGV + 12 SIGBUS**, 0 clean |
| reduced n=125 | 8 SEGV, 0 clean | **8 SIGBUS**, 0 clean |

Zero clean runs in every arm. A fault whose *signal* moves with address-space layout while its *incidence* does not is an out-of-bounds / wild-pointer write, not a logic error — consistent with the probabilistic zone at n≈104 and with the small standalone form (§5) being too small to reach the corrupted region.

## 8. ⛔ SELF-FALSIFICATION, RECORDED
I first reported "ASLR off ⇒ 12 of 17 drivers run" and "reduced case 0/8 crashes with ASLR off". **Both were false, and the cause was my own probe:** it tested `[ $? -eq 139 ]` only, so **SIGBUS (135) scored as a pass**. Caught by diffing actual stdout against `.ref` — a "passing" driver had produced *no output at all*. Every count above is re-measured with a full exit-code census (`0` / `139` / `135`).
⭐ Same genus as the s_this+5b `grep -c "fn_cell\$"` end-of-line-anchor census: **a probe that can only see one failure mode will report every other failure mode as success.** Prefer an *output* check over an *exit-code* check whenever a reference output exists.

## 9. NOT DONE — HONESTLY
- **MONITOR-FIRST NOT DISCHARGED.** `test_monitor_2way_sync_step_bin.sh` runs `PARTICIPANTS="csn spl"` — **CSNOBOL4 vs SPITBOL, neither of which is SCRIP**, and *neither oracle is present in this container* (`/home/claude/x64` not cloned; CSNOBOL4 not built). For a SCRIP fault the participants must be `spl scr` or `csn scr`. **The monitor is DARK here ⇒ ARCH §7's MON-RE clause binds: stand the oracle up before the next hunt.**
- **Regression-vs-debt UNSETTLED.** No cause is named because none was measured.
- **`gdb` backtrace not taken** (deliberate: MONITOR-FIRST ordering).

## 10. ⭐ BISECT IS NOW UNBLOCKED (was a repeat blocker)
SCRIP cloned at depth 1 (**1** commit). `git fetch --unshallow` → **3148** commits. `GOAL-PASSTHRU-RBP-ERAD.md` records depth-1 blocking s6's bisect and PASSTHRU s12's; it is now fixed in this tree. **407 commits since 2026-08-01** bracket the recent churn.
⚠ **Environment fact, cost one probe:** a backgrounded build (`nohup make … &`) is **reaped when its tool call returns** — empty process table, log frozen mid-command, zero errors. Bisect builds must run in the **foreground** of a single call. A worktree at `03cecd87` exists at `/home/claude/wt-probe` (unbuilt) so the shared tree is never checked out from under a concurrent seat.

## 11. FOR LON
1. **Sequence RTX-FUNC-11 independently of the RTX-FUNC ladder** — §5 shows it is not a DEFINE defect.
2. **Stand up an oracle** (`git clone https://github.com/snobol4ever/x64`) — without it the prescribed monitor cannot run at all, for this rung or any other.
3. **Bisect at N≥112 entries only** (§6), 407-commit range, foreground builds.
4. Hygiene, unchanged from the prior seat: two dangling tracked symlinks + absent `demo/inc`.

**`handoff_status.sh` is the push truth — NOT this block.** Nothing in this finding is committed or pushed.
