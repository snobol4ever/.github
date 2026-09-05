# FINDING 2026-09-05 hq_T — ARBNO's null-body guard recedes to the body's ENTRY, not the body's TAIL

**Seat:** hq_T (HQ-TEST) · **Row:** `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries` · **Mode:** FLEET-16
**Trees graded:** SCRIP `04824a14b` + this fix · corpus `a6e836ea6` + this promotion · .github `2e188b98`
**Build:** incremental `make`, `RT_OPT=-O0` (read from `Makefile:43`, not typed). Box clock 2026-09-05 ~10:30–11:10 CDT.

## 1. The defect, in one sentence

`bb_match_arbno_frame`'s **null-body guard** — "the body matched without moving the cursor, so do not start
another instance" — recedes to `PAIR(1)`, which is the ARBNO body's **ENTRY** node's β. The body is a
**chain**, so the only β that means "give me your next solution" is its **LAST** node's β. `PAIR(4)`, which
the emitter already computes for exactly this purpose, is that node.

Two consequences, and the second is why it crashes rather than merely answers wrong:

1. **Wrong box.** Entering the entry box's β asks the *first* member of the chain to re-decide, skipping
   every solution the members to its right still had.
2. **Wrong `rsp`.** At the guard, the body's own frames are stacked above the ARBNO's. `n7_match_alternate_β`
   reads its resume address from `[rsp+8]` *of its own frame*; arriving there with the tail node's frame on
   top makes `[rsp+8]` an unwritten slot of a different box. The observed value is 0, so the box jumps to 0.

Measured, both modes, minimal witness `'aaa' ARBNO(('' | 'x') ARB) RPOS(0)`:

```
Program received signal SIGSEGV.   rip 0x0   rsp 0x7fffffbf93b0   (m3 and m4 identical)
```

## 2. The cure

`src/templates/bb/bb_match_arbno.cpp`, one operand:

```c
- + x86("je",  PAIR(1))
+ + x86("je",  sn4_arbno_tailbeta() ? PAIR(4) : PAIR(1))
```

⭐ **The fix is not a new idea; it is the arm ten lines below, applied to the arm ten lines above.** The
exhaust arm of the *same box* already reads
`x86("jne", sn4_arbno_tailbeta() ? PAIR(4) : PAIR(1))`. Both arms recede into the body, so they must name
the body's β the same way; when `tailbeta` landed only one of the two was converted. **A box whose two
recede paths disagree about where its body's β lives has one of them wrong, and a grep for the flag finds
only the converted one** — the unconverted arm looks like ordinary code, not like a straggler.

`PAIR(4)` is not new machinery. `flat_drive_match_alt` (`emit.cpp:1421`) already builds it for ARBNO by
scanning the body index range **backwards** for the last node whose `γ.node` is the ARBNO — i.e. it already
knows how to find the body's tail. It was computed and then consulted by one arm of two.

## 3. Blast radius — measured over the whole master, not sampled

⛔ **A copied `scrip` is not a baseline, and I proved that the hard way** (same trap hq_C retracted a
measurement for at 2026-09-05T01:33Z). `scrip` is a ~40 KB *driver*; the emitter and every `bb_*` template
live in `out/libscrip_rt.so`, and the driver carries `DT_RUNPATH=/home/claude_T/SCRIP/out` **absolute**. So
`cp scrip base/scrip` produces a byte-identical file that loads the *current* library. My first corpus-wide
asm diff reported `IDENTICAL=1817 CHANGED=0` — a comparison of the patched build against itself, and the
"0 changed" reads exactly like a clean bill of health.
⭐ **The tell was available and I did not look for it:** `md5sum base/scrip patched/scrip` is one line and
would have printed the same hash twice. **When a differential measurement returns "no difference at all",
the first hypothesis is that both arms are the same arm.**
The cure is `LD_LIBRARY_PATH=<dir>/out` — `DT_RUNPATH` (unlike `DT_RPATH`) is searched *after*
`LD_LIBRARY_PATH`, verified by running the witness under each and getting rc=139 vs rc=0.

Redone correctly, over all **1859** master entries, base library vs patched library:

| | count |
|---|---|
| emitted `.s` **byte-identical** (exonerated) | **1744** |
| emitted `.s` **changed** | **73** |
| `--compile` fails identically on both | 42 |
| `--compile` rc diverged | **0** |

The 73 changed entries were then RUN on both libraries, both modes, against their own `.ref`:

```
arbno_arb_rpos_replace_branch_1   base m3=FAIL m4=FAIL  ->  patched m3=PASS m4=PASS
arbno_arb_rpos_replace_branch_2   base m3=FAIL m4=FAIL  ->  patched m3=PASS m4=PASS
(the other 71: verdict unchanged, base == patched)
```

**Two cures, zero regressions, and the 1744 byte-identical entries cannot regress by construction.**

Stability of the two cures (this family is ASLR-sensitive — see the row's 2026-09-04 ledger):
`ASLR on 10/10 both modes` · `setarch -R 3/3 both modes`, each.

## 4. The witness family this closes, and the one it does not

The 18 entries of this class split by ingredient. The cured mechanism is **M3: `ARBNO(<ALT with a
null-matching arm> <null-matching generator>)` + a forcing tail.** Ablation (each line one ingredient,
all graded m3+m4+oracle under `setarch -R`):

```
'aaa' ARBNO(('' | 'x') ARB) RPOS(0)     SEGV  <- the witness
'aaa' ARBNO(('' | 'x') ARB)             green <- drop the forcing tail
'aaa' (('' | 'x') ARB) RPOS(0)          green <- drop the outer ARBNO
'aaa' ARBNO('' ARB) RPOS(0)             green <- drop the ALT
'aaa' ARBNO(('a' | 'x') ARB) RPOS(0)    green <- ALT arm no longer matches null
'aaa' ARBNO(('' | 'x') LEN(1)) RPOS(0)  green <- tail node cannot match null
'aaa' ARBNO(('' | 'x') BAL) RPOS(0)     green <- ditto (BAL cannot match null)
''    ARBNO(('' | 'x') ARB) RPOS(0)     green <- empty subject
'aaa' ARBNO(('x' | '') ARB) RPOS(0)     SEGV  <- arm ORDER is NOT an ingredient
'aaa' ARBNO(('' | 'x') ARBNO('q')) RPOS(0) SEGV <- any null-matching generator, not just ARB
```

⛔ **Arm order is not an ingredient, and the recorded reason said it was.** `ALL.xfail` for
`arbno_arb_rpos_replace_branch_1` reads *"an ALT whose **FIRST** arm matches the NULL string"*; `('x' | '')`
crashes identically. The reason was written from one witness and generalised one word too far.

**Still open after this fix: 16 of the 18.** They are NOT this mechanism — the remaining population is
FENCE-with-capture (`fence_arb_*`, `fence_capture_*`, `fence_rpos_rem`, `fence_span_rpos`) and
ARBNO-over-**deferred** bodies (`ARBNO(*G0)`), which reach different emitter arms. Re-censused on this
build under `setarch -R`, both modes, all 18: see §6.

## 5. ⛔⭐ `grep` IS BLIND TO `corpus/tests/snobol4/ALL.ref` — IT HAS A NUL BYTE

This nearly shipped a torn master, and it is the most reusable thing in this document.

`ALL.ref` contains **exactly one** NUL byte, at offset 919, inside a legitimate expected output (`a\0b`,
a `CHAR(0)` witness). GNU grep classifies the whole file as binary from that one byte and then:

```
grep -c 'arbno_arb_rpos' ALL.ref   -> rc=1, NO OUTPUT     (reads as "this name is not in the file")
grep -a -c 'arbno_arb_rpos' ALL.ref -> rc=0, "1"           (the truth)
```

I ran the first form, got nothing, and concluded **"ALL.ref carries no banners for this master"** — so I
promoted the two markers in `ALL.sno` and `ALL.xfail` only. `read_suite` then refused, naming the exact
torn seq, which is precisely the failure `lib_master_extract.sh`'s INTERIM PROMOTION PROTOCOL exists to
catch and which tore the suite for every seat on the box for ~40 minutes on 2026-09-01.

⭐ **The instrument was right and my question was wrong** — the same family as `command -v icont`. `grep`
answers *"does this text appear in a file I am willing to treat as text"*, and it never says which half of
that it failed on. **Use `grep -a` on anything under `corpus/tests/*/ALL.*`**, and treat a bare `rc=1` with
no output on a file you have not proven textual as *unmeasured*, never as *absent*.
⭐ The protocol's own defence held exactly as written: **the promotion was proven by running `read_suite`
on the result, and that is what caught it — before the commit, not after.**

## 6. Fresh census of the class on this build (`setarch -R`, both modes, oracle rc=0 for all 18)

```
ENTRY                                      M3            M4
arbno_arb_rpos_replace_branch_1            PASS          PASS      <- CURED, promoted
arbno_arb_rpos_replace_branch_2            PASS          PASS      <- CURED, promoted
fence_capture_imm_capture_replace_branch_1 DIFF rc=139   PASS      (m3 only; hq_T 2026-09-04 cured m4)
fence_rpos_rem_replace_branch_1            DIFF rc=139   DIFF rc=139
arbno_fence_rpos_replace_branch_1          DIFF rc=139   DIFF rc=139
fence_span_rpos_replace_branch_1           DIFF rc=139   DIFF rc=139
arbno_fence_pos_replace_branch_2           DIFF rc=139   DIFF rc=132
arbno_fence_tab_replace_branch_1           DIFF rc=124   DIFF rc=139
arbno_bal_tab_replace_branch_1             DIFF rc=124   DIFF rc=139
fence_arb_span_replace_branch_1            DIFF rc=139   DIFF rc=139
fence_arb_tab_replace_branch_1             DIFF rc=139   DIFF rc=132
fence_arb_tab_replace_branch_2             DIFF rc=139   DIFF rc=132
arbno_fence_bal_replace_branch_3           DIFF rc=0     DIFF rc=0
arbno_fence_bal_replace_branch_1           DIFF rc=0     DIFF rc=0
arbno_span_break_replace_branch_1          DIFF rc=124   DIFF rc=124
arbno_span_tab_replace_branch_1            DIFF rc=139   DIFF rc=139
arbno_fence_bal_replace_branch_2           DIFF rc=1     DIFF rc=1
arbno_fence_span_replace_branch_2          DIFF rc=124   DIFF rc=124
```

⚠️⭐ **THE rc COLUMN IN THAT TABLE IS LOAD-DEPENDENT AND I MEASURED BOTH READINGS.** Taken again while a full
board was running on the same box (load ~15 on 16 cores), eleven of these entries read **rc=124** where the
table says **rc=139**: the 8 s per-program bound fires before the crash does. Nothing about the entries changed
— the *instrument* changed. **A crash and a timeout are the same observation at different box loads unless the
bound is far above the measurement**, which is the general form of this digest's own `timeout 30s` lesson.
Grade this family on a quiet box, or at a bound an order of magnitude above the run, and record which.

⛔ Several recorded reasons in `ALL.xfail` still claim a **1:1 mode breach** ("m3 answers, m4 SEGVs" for
`fence_rpos_rem_replace_branch_1`; "m3 SEGVs, m4 answers" for `fence_span_rpos_replace_branch_1`). **Both
now crash in both modes.** That is drift in the reasons, not in this fix — the entries were already red both
modes before this change (they are among the 1744 byte-identical). Recorded here so the next seat does not
re-derive a breach that no longer exists; consistent with seat12's 2026-09-04 finding that 6 of 19 reasons
were stale.

## 7. DONE-WHEN

`n` (fuzz/`fz_` reasons remaining in `ALL.xfail`): **18 -> 16.** Still RED; the row stays open.
