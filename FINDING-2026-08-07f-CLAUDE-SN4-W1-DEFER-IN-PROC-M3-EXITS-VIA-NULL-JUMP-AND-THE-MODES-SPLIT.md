# FINDING 2026-08-07f (Fable) — SN4 W-1: a value/defer pattern element inside an INVOKED proc detonates mode-3 at final exit via a NULL jump, and the modes split

HEAD: SCRIP `f2751777` (unchanged) · corpus at the 07e suite-repair commit → this commit adds probe **X12**. Entry point: the 07e armed-roman rc=139; the shrink below shows the underlying defect is a **DEFAULT-regime** bug the armed regime merely exposes earlier.

## THE WITNESS (now probe corpus/probe/bb/probes/X12.sno; XFAIL.run, m4 NOT xfailed)

```
	DEFINE('R(U)')	:(R_END)
R	'145' U	:F(FRETURN)
	R = 'OK'	:(RETURN)
R_END
	OUTPUT = R(4)
	OUTPUT = 'AFTER'
END
```
m3: prints `OK` and `AFTER` **correctly**, then rc=139. m4: rc=0, correct. **MODES ARE NOT 1:1 ON THIS CLASS.**

## SHRINK LADDER (all m3 default; oracle correct throughout)

| witness | proc body | result |
|---|---|---|
| v1 | `N RPOS(1) LEN(1) . U =` + recursion | **PASS** |
| w1_b | + `REPLACE(R(N),…)` recursion, no ref stmt | **PASS** |
| w1_g | `'ABC' 'B'` literal-only match | **PASS** |
| w1_h | `N RPOS(1) LEN(1) . U` no-replacement capture | **PASS** |
| w1_i | `'0,1I,2II,' BREAK(',') . U` (no ref element) | **PASS** |
| w1_j / w1_k | `'145' U` / `'145' *U` — bare ref/defer element | **rc=139** |
| w1_e / w1_f | ref/defer + BREAK + capture | rc=139 (after CORRECT output) |
| w1_c / w1_d | stmt-1 before the ref stmt | rc=139 (output degrades to EMPTY) |

The crashing ingredient is precisely **one variable-valued pattern element (plain ref → PB IR_MATCH_VALUE path, or `*U` → IR_MATCH_DEFER path) inside a DEFINE'd, INVOKED proc**. Both operators identically — this is NOT a PB-1s regression; it is the shared value/defer invoke machinery in proc graphs, mode-3 only. Toplevel copies of the same statements are green across the 141-probe suite.

## THE DAMAGE IS SILENT AND DETONATES AT EXIT

w1_o/w1_p: the proc returns, **subsequent toplevel statements execute correctly** (`AFTER` prints), 1 or 3 calls alike — then the process dies at final exit. `SCRIP_NO_SEGV_HANDLER=1` backtrace: **frame #0 = 0x0000000000000000** — generated code jumped through a NULL slot; caller frames are stack garbage. Mechanism bracket (monitor-grade, mechanical): last-agreeing event = final statement's correct completion; first divergence = exit-glue control transfer. HYPOTHESIS (labeled as such, one gdb session from proof): an orphaned continuation/resume slot from the value/defer element's proc-graph run — the CLASS D suspension record (emit.cpp:2720 family: 16B `{res-landing, rbp}` pushed at the deep frontier, consumed by a `jmp qword [rsp]`-shaped β edge) or the PS-1b m3-only `rt_proc_set_zstatic` twin (driver:1554) — survives the proc whack and is read as the exit continuation. m4's separate-binary exit path never reads the slot, hence the split.

## RELATION TO KNOWN CLASSES
- **07e armed roman rc=139**: roman's stmt-2 carries exactly this element inside ROMAN(); the armed regime shifts stack geometry so the stale slot kills mid-run (144/345 lines) instead of at exit. Same family, earlier landing.
- **Full roman at default rc=0-but-wrong-output**: same proc/ref shape yet exits alive with degraded values — consistent with the stale slot holding a survivable-but-wrong value under roman's deeper call texture. UNVERIFIED unification; the wrong-output bug keeps its own W-1 line until the monitor says otherwise.
- **161_pat_defer_fn_nested_match / ZW-13 seal**: adjacent (defer re-entrancy) but that class is armed-only; X12 is default-regime.

## GDB SESSION DATA (07f addendum, bounded per TIME-BOXED rule)
- The NULL jump originates from the **static in-binary emitted region** (~0x418d68 neighborhood appears as the stale caller frame — the SEG_CODE slab class, not the mmap'd pat_pool), narrowing the site to the m3 static-slab exit glue.
- **The crash point MOVES under gdb** (env/argv length shifts it) — the 127/152-class absolute-sensitivity signature. This is strong mechanism evidence: the consumed slot is addressed absolutely/at a skewed depth, exactly the class W-3's frames are predicted to make impossible. Any A/B on this bug MUST control env length (`setarch -R`, fixed argv).
- One run showed a single anomalous `output_str` hit in the crasher that the clean twin never makes (both assign only literals to OUTPUT); non-reproducible under the shifted env — logged as a lead, not a fact.

## NEXT MECHANICAL STEP (W-1, MONITOR-FIRST toolchain)
gdb spin-counter at the CLASS D resume-record push + at the proc RETURN whack on X12; watch the 16B record's slot across the whack; the land-mine is whichever reader consumes it post-release. Fix directions, in preference order: consume-on-success (pop the record at γ when the blob completes forward), or park the record off-stack (claim slot, not push).

## GATES THIS COMMIT
141-probe m3: X12 enters as xfail — suite 138/4/0/0 (no regression; the defect was always there, now it is VISIBLE). m4: X12 PASSES (123→124/18/0/0). SCRIP untouched.
