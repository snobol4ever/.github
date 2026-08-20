# FINDING s184 (seat7, row `span-frame-flip`) — THE TDump_driver BLOCKER IS ROOT-CAUSED: THE ARMED CARVE MOVES `rsp` FOR THE WHOLE GRAPH AND NOT ONE FLAT ζ-SPINE OPERAND OFFSET IS REBASED

**Status:** ROOT CAUSE NAMED + MINIMAL WITNESS + CONTROL. Flip still HELD (HQ-61 option (1)); the fix is **not** landed — see §6, the obvious fix is measured WRONG.
**Tree:** SCRIP `ffbc1425` (pristine, RT_OPT `-O0`) · corpus `e2dcb1ee` · witnesses `corpus/probe/leafwide/`.

## 1. What HQ-61 asked for
> flip stays HELD until TDump_driver is root-caused … the operand-slot flat read inside an arm resolves to caller territory … TDump spurious-FAIL and these may be one family: arm-interior leaf state vs the backtrack path.

HQ's sentence is **exactly right and it is the whole defect**. It is not a backtrack-path defect and not leaf state — it is an **operand** defect, and the α path is already wrong before any backtracking happens.

## 2. Reproduced at HEAD (the blocker is live)
`corpus/programs/snobol4/beauty_suite/TDump_driver.sno`, m3, `ulimit -s unlimited`, 10 runs per arm:

| arm | PASS | FAIL |
|---|---|---|
| `SCRIP_SPAN_FRAME=0` | 10 | 0 |
| `SCRIP_SPAN_FRAME=1` | 4 | 6 |

⭐ **THE WRONG ANSWER IS NOT GARBAGE, IT IS A COHERENT SECOND ANSWER** — and that is what makes it findable:
```
expected  (Name)                     got  ("Name")
expected  (BinOp (Name) (Name))      got  ("BinOp" ("Name") ("Name"))
```
A value that should render as a bare identifier comes out **quoted**. That names the site with no tracing at all — `TDump.sno:54-55` (and its twin `:34-35`):
```
TLump0    t(x)  POS(0) ANY(&UCASE &LCASE)
+               (SPAN( digits &UCASE '_' &LCASE) | epsilon) RPOS(0)   :F(TLump1)
TLump1    t = '"' t(x) '"'
```
The pattern asks *"is `t(x)` a bare identifier?"*; on **F** it quotes. So the armed arm makes that match **spuriously fail**. That is the `(SPAN|epsilon)`-on-an-ALT-arm shape the s173 sweep named, and the "silent wrong answer" is simply the program's own `F` branch being taken.

## 3. The mechanism (ASM-DIFF-FIRST; gdb never needed)
Passing sibling = the same program at `SCRIP_SPAN_FRAME=0`. The whole two-arm `.s` diff on TDump_driver is **64 lines at two sites**, and on the minimal witness it is **32 lines**. In both cases the diff contains **only three things**: the carve, the retry_whack, and the leaf cell re-home.

```
push rbp; mov rbp,rsp; push r12/r13/r14/r15      ->  rsp = rbp-32
OFF     sub rsp, 24                              ->  rsp = rbp-56
ARMED   sub rsp, 40                              ->  rsp = rbp-72     <- carve grew 16
OFF     .Lx6323_13: lea rsp,[rbp-56]  # retry_whack
ARMED   .Lx6323_13: lea rsp,[rbp-72]  # retry_whack
OFF     leaf cell = [rsp + 0]
ARMED   leaf cell = [rbp - 80]                                        <- re-homed, as designed
```
So far, all intended. **The defect is what did NOT change.** Inside that same SPAN box, both arms emit *byte-identical*:
```
mov  rsi, qword ptr [rsp + 120]      # coerce_string    <- the SPAN's charset operand
mov  edx, dword ptr [rsp + 116]
```
`rsp` under those two instructions differs by exactly **16** between the arms (OFF `rbp-72`, ARMED `rbp-88`, each after the box's own `sub rsp,16`). The offset `120` was planned for the OFF-arm depth and is **never rebased** when the carve grows.

**Therefore the armed SPAN reads its charset descriptor 16 bytes past its slot — in caller territory.** Wrong charset ⇒ SPAN matches nothing ⇒ the `| epsilon` arm wins ⇒ `RPOS(0)` fails ⇒ the `F` branch quotes. Silent, because every step is a legal match outcome.

This explains **every** observed property: silent (a legal `F`), nondeterministic (whatever sits at `rbp+32` varies), `ulimit -s unlimited`-sensitive (stack placement decides it), both media (pure codegen offset), and arm-interior (the ALT arm is the only place the re-home happens).

## 4. THE TWO AUTHORITIES (this is the spelled-twice disease, third instance)
- **A — the carve:** `emit_match_begin_frame_extra()` (emit.cpp:2533) → staged `op_frame_extra` → `bb_match_begin.cpp` prologue. Returns `16 * count`; a `leaf_frame_member()` node is a candidate under `SCRIP_SPAN_FRAME`, so the count — and `rsp` for the entire statement graph — moves.
- **B — the flat operand offsets:** the ζ-depth planner (`zd_plan`/ZOPQ staging), which emits `[rsp+120]`. **B has no knowledge of A.** Nothing in `src/` reads `emit_match_begin_frame_extra` except the prologue template.

At the OFF arm `extra == 0` for these graphs, so A and B agree *by accident of zero*. Arming makes `extra` non-zero and the two disagree by exactly `extra`.

## 5. MINIMAL WITNESS + CONTROL (`corpus/probe/leafwide/`, oracle `sbl -b`)
```
leafwide_span_dyncs_alt.sno   DEFAULT 12/12 PASS   ARMED 1/12 PASS      <- the defect
ctl_span_constcs_alt.sno      DEFAULT 12/12 PASS   ARMED 12/12 PASS     <- the control
```
Both are 7 statements, self-contained, no `-INCLUDE`. They differ in **one ingredient**:

⭐ **THE INGREDIENT IS NOT THE ALT ARM AND NOT THE LEAF RE-HOME — IT IS WHETHER THE BOX MAKES A FLAT `[rsp+N]` SPINE OPERAND READ.**
The control writes its charset inline, so it **constant-folds to a static IP-relative table** (`lea rdi,[rip+.C1]`) and the SPAN box makes **zero** flat operand reads — `grep -c 'rsp +'` inside the box is 0. The control is still re-homed (`[rsp+4]`→`[rbp-76]`) and still carves 16 more, and it is **green in both arms**. The witness uses `SPAN(*CS)`, which cannot fold, so the charset is spine-staged and read at `[rsp+120]`.

⛔ **THIS IS WHY THE s173 LADDER MISSED IT AND WHY IT WILL BITE ANY SEAT THAT TRANSCRIBES beauty BY HAND.** A hand-written transcription of `TDump.sno:54` folds its charset and is green; TDump's own `digits` arrives from an `-INCLUDE`d runtime global and does not fold. Four build-up witnesses (`DEFINE` activation, function-call subject, top-level call subject, verbatim shape) were all green before the ingredient was identified. **Transcribing the shape is not transcribing the program.**

## 6. ⛔ THE OBVIOUS FIX IS MEASURED WRONG — DO NOT LAND IT
The carve bills one slot per candidate while `frame_slot_scan` — the numbering authority — advances by the claim width:
```c
frame_slot_scan:                 k += zdp_scratch_cell(m) ? 2 : 1;   /* two-slot claim, 44b8b82c */
emit_match_begin_frame_extra:    count++;  return 16 * count;        /* private re-walk, one slot */
```
That is a *second*, real inconsistency (the leaf is handed index 1 = `rbp-80` inside a frame carved only to `rbp-72`), and the comment above the carve already **promises** it calls the scan — it does not, it re-walks. **But making the carve bill the claim width MAKES THE PROGRAM STRICTLY WORSE:** built and measured, `sub rsp,40`→`56`, and TDump_driver goes **12/12 FAIL, deterministically** (from 6/10). Reverted.

⭐ **That failed experiment is the proof of §3**, and it is why it is recorded rather than discarded: widening the carve moved `rsp` by a further 16 and the flat operand offsets *again* did not follow, taking the read from 16-bytes-stale to 32-bytes-stale and turning a nondeterministic wrong answer into a deterministic one. **The carve is not independently adjustable.** Any fix must make B follow A — rebase the flat ζ-SPINE operand offsets by `op_frame_extra` for every node inside that MATCH_BEGIN's scope — or make A not move `rsp` at all. Fixing A alone is a regression.

## 7. Consequence for the arming verdict (HQ-61's re-sweep ask)
⛔ **THE RE-SWEEP CANNOT DECIDE THE FLIP, AND RUNNING IT FIRST WOULD MISLEAD.** The armed arm is now known **broken by construction** for any statement graph where `emit_match_begin_frame_extra() > 0` meets a flat spine operand read in a re-homed box. A mover count taken before the fix measures which programs *happen* to have a foldable charset — an accident of constant-folding, not a safety property, and one that shifts with any optimizer change. The sweep belongs **after** B is made to follow A. The s173 30/527 number is stale for this reason as well as HQ's.

## 8. Not this defect, kept so it is not re-derived
`probe/leafwide/ctl_spanvar_alt_inline` (HQ's second witness) is **RED IN BOTH ARMS**, m3 and m4 — `nomatch` where the oracle says `match:aabb`. It is arm-independent and therefore **not** a flip blocker and **not** this class; its pattern-variable twin `leafwide_spanvar_alt` is green in both arms. It wants its own row.

## 9. Files
`corpus/probe/leafwide/{leafwide_span_dyncs_alt,ctl_span_constcs_alt}.{sno,ref}` (corpus `e2dcb1ee`).
Repro: `cd corpus/probe/leafwide && SCRIP_SPAN_FRAME=1 scrip --run leafwide_span_dyncs_alt.sno </dev/null` — expect `bare`, get `quoted` ~11/12.
