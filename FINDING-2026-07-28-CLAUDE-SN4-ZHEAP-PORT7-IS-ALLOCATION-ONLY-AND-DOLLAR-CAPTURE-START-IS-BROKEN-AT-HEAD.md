# FINDING 2026-07-28 (s205) — `ZC_PORT_HEAP` IS THE ALLOCATION HALF ONLY, MEASURED; AND `$` CAPTURE START IS BROKEN AT HEAD IN THE DEFAULT PORT

**Rung:** `GOAL-SNOBOL4-BB.md` RUNG ZHEAP (s205 pivot — ζ locals → GC heap, ζ results → mmap value stack).
**Build:** SCRIP HEAD, `make scrip`, **RT_OPT = `-O0`** (Makefile default; no `-O2` directed this session, per O2-DIRECTED-ONLY).
**Oracle:** `/home/claude/x64/bin/sbl -b`.

## 1. THE FUNNEL IS ALREADY PARAMETERIZED — `ZHEAP-0` IS NOT NET-NEW

`src/contracts/zeta_choices.h` carries an EIGHT-flavor ζ port axis, `ZC_PORT_{PLAIN,INSTRUMENTED,ALLOC,INLINE,CSTACK,OWNED,FORTH,HEAP}` = 0..7, read in the encoder as `x86_port_mode()` and switched INVISIBLY INSIDE `x86()` — already the discipline `ZHEAP-0` specifies. Compiled default is `ZC_PORT_FORTH` (6).
**Recommendation stands: `ZHEAP-0` = "select and default flavor 7", NOT "add a `SCRIP_ZMODE` switch."** A second orthogonal axis would create a 2×8 regime matrix, which is what the NO-INTERLEAVE law exists to prevent.

### 1a. GAP — THE HEAP FLAVOR HAS NO CLI SELECTOR
`src/driver/scrip.c:442` parses `--zeta-port=` by NAME against a closed list: `plain, instrumented, alloc, inline, cstack, forth`. **`heap` (7) and `owned` (5) are missing** — `--zeta-port=heap` is rejected outright. The arm is reachable ONLY through the env path, `rt_zeta_port_mode()` in `zeta_alloc.c:267`, which is a raw `atoi` of `SCRIP_ZETA_PORT`. **`SCRIP_ZETA_PORT=7` works; the documented flag does not.** One-line fix, but it is why the arm looks unreachable.

## 2. THE α-CARVE ALREADY EXISTS — `ZHEAP-2` IS LARGELY WRITTEN

`src/templates/x86_asm.h:1836–1848`, gated `site==X86H_DEF && port==X86P_ALPHA && hk>0 && x86_port_mode()==ZC_PORT_HEAP`:
`mov rax,rbx` · `add rbx,hk` · `cmp rbx,ABSQ(RT_WS_LIMIT)` · `ja` → aligned `call rt_zh_bump_slow` → `mov rbx,ABSQ(RT_WS_TOP)`.
The outer seed `mov rbx,[RT_WS_TOP]` is emitted too (`xa_flat.cpp:398`, REG-4b). **"GENERALIZE `sink_carve48`" is superseded — the carve is not merely generalizable, it is WRITTEN and both-medium.**
Delta: coded as `ja L(60); jmp L(61)` (jump-over), NOT the predicted-not-taken fall-through the rung's prose specifies. Cosmetic; the rung and the code disagree.

## 3. ⭐ THE MEASUREMENT — PORT 7 IS ALLOCATION-ONLY, AND THE SPLIT IS PERFECTLY CLEAN

Six programs, each run under the oracle and under `SCRIP_ZETA_PORT` 6 and 7. `DIFF` = ran, output ≠ oracle. `SEGV` = 139.

| program | construct | ORACLE | PORT6 (FORTH, default) | PORT7 (HEAP) |
|---|---|---|---|---|
| `a_noPat` | assignment only, no match | `HI` | OK | OK |
| `b_lit` | `'ABC' 'B'` literal match | `YES` | OK | OK |
| `e_at` | `'FIX' @OUTPUT 'B'` | `0 1 2 3 DONE` | OK | OK |
| `c_lenCap` | `'ABCDEF' LEN(3) . X` | `ABC` | OK | **SEGV** |
| `d_dollar` | `'ABCDEFG' 'A' ARB $ OUTPUT 'E'` | `⟨null⟩ B BC BCD DONE` | **DIFF** | **SEGV** |
| `f_arbno` | `POS(0) ARBNO('a') RPOS(0)` | `YES` | OK | **SEGV** |

**THE SPLIT IS EXACTLY "DOES THIS BOX CARVE ζ".** Boxes with no ζ locals (no match; bare literal; `@`, which the manual p.65–66 says *"behaves like the null string — it doesn't consume subject characters or interfere with the match in any way"*) run correctly under HEAP. **EVERY box that actually carves — capture (`.`), immediate assignment + generator (`$`/ARB), ARBNO — segfaults.**

**THIS CONFIRMS THE PORT'S OWN ADMISSION, MEASURED RATHER THAN READ:** *"SLICE A IS THE ALLOCATION HALF ONLY: the box receives its ζ base in rax, but FR/FRQ frame plumbing under heap residence (`x86_zr` for escapee classes) is HZ-1's census slice."* The bump happens; the box then addresses its locals through FR/FRQ, which still resolve **rsp-relative** (`x86_fr32_prefix()` is hardcoded rsp — s196 already recorded this, against ARCH-ICON.md's stale `[rbp+off]` prose). Storage at rbx, addressing at rsp ⇒ every carving box dereferences garbage.

### CONSEQUENCE FOR THE RUNG — THE SCOPE IS ONE THING, NOT NINE
`A-1`'s *"addressing form unchanged"* is the entire remaining cost of clause (1). The first work item is precisely: **make FR/FRQ resolve against the ζ base register under heap residence.** The six-program table above is a ready-made oracle-checkable tripwire — three SEGVs must become OK without moving the three OKs.

## 4. 🔴 INDEPENDENT PRE-EXISTING DEFECT — `$` CAPTURE START CURSOR IS WRONG AT HEAD, IN THE DEFAULT PORT

`d_dollar` DIFFs under **port 6, the shipping default** — nothing to do with ZHEAP.

```
ORACLE (sbl -b):   ⟨null⟩   B      BC     BCD     → starts all 1, ends 1,2,3,4
SCRIP  (port 6):   A        AB     ABC    ABCD    → starts all 0, ends 1,2,3,4
```

**Yield COUNT is right (4). END cursors are right (1,2,3,4). Every START is 0 instead of 1** — i.e. the capture's start is the SCAN start, not the ARB element's own start, so each yield is one character too long on the left.
This is the s195 capture-extent class (*"COND's FR read of the SAVE slot landed on head's rsp-snapshot cell"*) and the s202 **MARKER-CAPTURE** rung is its named fix (*"SAVE.α pushes pend-stack MARK entry CARRYING start cursor (r12, depth-immune; frame slot dies)"*).

**⚠ WHY THIS MATTERS TO ZHEAP SPECIFICALLY:** `$` write-through surviving a failed match is the load-bearing premise of `ZHEAP-7` (manual p.87, verified). **The natural gate witness for that premise is ALREADY RED at HEAD**, so it cannot validate ZHEAP-7 until MARKER-CAPTURE lands.
**USE `e_at` INSTEAD.** `@` cursor assignment carries the identical property — manual p.65–66: *"Cursor assignment is performed whenever the pattern match encounters the operator, including retries. It occurs even if the pattern ultimately fails"* — and it is **GREEN at HEAD in both ports**, making it the only currently-usable write-through-survives-failure witness. Its oracle output is the manual's own worked example.

## 5. NEXT
1. **FR/FRQ heap-residence addressing** — the one blocker; tripwire = the six-program table.
2. `--zeta-port=heap` CLI selector (one line, `scrip.c:442`).
3. Decide the ω contract: `ZC_PORT_HEAP` says the region is *"never collected, never slid"*; `ZHEAP-5`/`7` require MARK/ADJUST/SLIDE. Harvest the carve, do not inherit the lifecycle claim.
4. MARKER-CAPTURE (unblocks the `$` witness, and is independently a HEAD defect in the default port).

**Not run this session:** full watermark under port 7 (blocked — 3 of 6 minimal patterns SEGV, so a corpus sweep would report noise, not signal); allocation-rate measurement on `pattern_bt`/`string_pattern` (the "failure is an allocation-rate event" consequence).
