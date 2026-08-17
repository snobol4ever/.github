# FINDING s129 — A FRAMED BLOB'S LEAF SUSPENSION CELL OVERSHOOTS INTO THE CALLER'S STANDING FRAME AND SHREDS THE CAS MARK (DEFAULT ARM, NO KILLSWITCH)

**Measured** 2026-08-16 s129 (Claude Opus 5, Lon in-chat *"using the IPC sync-step MONITOR, take us home"*).
SCRIP `2e18a2f3`, corpus `5a08cd99` (clone HEADs, unmodified — **NO CODE CHANGED THIS SESSION**; localization only, END-OF-CONTEXT LAW).
Witnesses: `corpus/probe/clobarm/` (5 programs + `.ref` from live `x64/bin/sbl -b`, README carries the matrix).

---

## 1. THE HEADLINE

**`corpus/probe/clobarm/clob_altarm_arm2direct_red.sno` — 9 lines, DEFAULT build, no env var — is rc=139.**

```
        t = ('zz' . K | SPAN('abcdefghijklmnopqrstuvwxyz') . I)
        s = 'iffoo'
        s POS(0) t RPOS(0)                                    :S(YES)F(NO)
YES     OUTPUT = 'id=' I                                      :(END)
NO      OUTPUT = 'parse fail'
END
```

Oracle `id=iffoo`. SCRIP m3 **and** m4 SIGSEGV. This is not a killswitch arm, not an opt-in slice,
and not a backtracking-depth bug: **arm 1 fails outright, so arm 2 runs on the first forward pass
with no backtrack and no choice record in play.**

⛔ **`SCRIP_CHOICE_RBP` (s128) IS EXONERATED AS THE CAUSE.** It is byte-identical at the faulting
instruction and changes only whether the instruction is REACHED. Earlier in this same session I
had provisionally attributed the crash to the s128 slice (the first two probes only fail under
`=1`); `clob_altarm_arm2direct_red` was minted specifically to discriminate, and it falsified that
attribution. Recorded here so the next seat does not inherit the wrong suspect.

## 2. THE MECHANISM (gdb-measured, not argued)

`n2_match_span_α`'s leaf suspension cell is, **byte-identical in both arms**:

```asm
.Lx12_240:              mov              dword ptr [rsp + 164], r14d
```

At the moment it executes (default build, `clob_altarm_arm2direct_red`):

| quantity | value |
|---|---|
| `blob_rbp` (`PAT$0` activation) | `0x7fffffffe8b8` |
| `blob_frame_bytes()` | 56 |
| `rsp` at the write | `0x7fffffffe850` = `blob_rbp-104` (56 frame + 32 ALT record + 16 assign_save) |
| **cell target `rsp+164`** | **`0x7fffffffe8f4` = `blob_rbp+60` = `standing_rbp-4`** |
| `standing_rbp` (`IR_MATCH_BEGIN`) | `0x7fffffffe8f8`; `[standing_rbp-8]` = CAS MARK (`push r12`) |

The dword store lands on the **upper half** of the mark qword:

```
[standing_rbp-8]:  0x00007ffff29ff030   ->   0x00000000f29ff030
```

Caught with a **software** watchpoint (`set can-use-hw-watchpoints 0; watch -l`) — see §5.
The truncated mark then flows `n38_match_end_α` → `rt_match_end_all` → `c_rt_dcap_end_ok_open`
→ `rt_dcap_pump` (`src/runtime/pattern_match.c:691`), which walks the pending-capture arena from a
wild base. SIGSEGV at `mov 0x10(%rax),%rax`.

**The disagreement is CROSS-BLOB.** The callee prices its leaf cell into caller territory at
`blob_entry+52` (the s127 "leaf cells live at offsets the CALLER's carve reserved" design), while
the caller — the `IR_MATCH_BEGIN` standing frame — carves 56 bytes for its OWN five slots
(mark/Σ/δ/Δ/start_δ) and reserves nothing above them for a callee. Nobody owns `blob_entry+52`,
so the callee's cell and the caller's mark alias.

## 3. THE CLASS, NAMED PRECISELY

**`blob_frame_bytes() > 0` (via registry demand) with zd static pricing still ACTIVE.**

- **Wire-clobber blobs escape** — dynamic-box graphs decline zd static pricing wholesale (the zdyn
  veto; `emit.cpp:2341` states this as the reason clobber blobs tolerate a frame at all).
- **Zero-demand blobs escape** — `blob_frame_bytes()==0`, no frame, legacy shape (and the s127
  retraction proved framing them by shape is what breaks 120/131/165/181/182).
- **Registry-demand-framed, non-clobber blobs are the hole**, and they are exactly the shape the
  s128 admission gate ADMITS (`count>0 ∧ !clobber`).

This is the same work item the s128 cursor named as a prerequisite — *"the zd cross-blob pricing
must learn `blob_frame_bytes` first"* — but it is **not merely a prerequisite for widening the
choice-record slice. It is a live default-arm corruption reachable from a 9-line program.**

## 4. WHAT IS EXONERATED (do not re-suspect these)

- **The ALT template.** Full gdb trace of `r12` (capture-pending arena TOP) across a blob backtrack:
  `α 030 → arm1 success 048 → β 048 → arm1 cond_β sub r12,24 → 030 → af 030 (cursor restored to 0)
  → arm2 success 048`. Cursor and arena discipline are **correct end to end**; arm 2 does run and
  does match. `assign_cond_β: sub r12,24` is present and identical in blob and inline.
- **The choice record's field set.** I hypothesised the 32B record was missing an `r12` field and
  that `[cro+24]` should carry it. The trace above **falsifies** that: the discard already happens
  in the arm's own `cond_β`, which `[cro+8]` correctly routes to. `[cro+24]` being free is real but
  is not this bug.
- **"Stale pending capture / last-write-wins".** `clob_altarm_samevar_red` (both arms capture the
  same variable) still SEGVs — falsified.
- **`rbp` at match end.** Measured correct (`0x7fffffffe8f8`, same standing frame at begin and end).
  The `mark=0xf29ff030 <cannot access>` in the raw backtrace is the *corrupted value*, not a
  misdecoded frame — confirmed by reading `[rbp-8]` directly.

## 5. REPRODUCTION

```bash
cd /home/claude/corpus/probe/clobarm
/home/claude/SCRIP/scrip --run clob_altarm_arm2direct_red.sno < /dev/null ; echo rc=$?   # 139

# m4 too (m3 ≡ m4, not a mode gap)
/home/claude/SCRIP/scrip --compile clob_altarm_arm2direct_red.sno < /dev/null > d.s
gcc -no-pie -o d d.s -L/home/claude/SCRIP/out -lscrip_rt
LD_LIBRARY_PATH=/home/claude/SCRIP/out ./d ; echo rc=$?                                  # 139

# catch the writer (HW watchpoints do NOT work in this container; SOFTWARE ones DO)
gdb -q ./d
  break n35_match_pos_α
  run
  set can-use-hw-watchpoints 0
  watch -l *(unsigned long*)($rbp-8)
  continue        # stops in n2_match_span_α, old 0x7ffff29ff030 -> new 0xf29ff030
```

⛔ **VERIFY-INHERITED-BLOCKERS, discharged:** RULES.md says *"HW watchpoints DO NOT WORK in this
container — use hit-counts"*. That is true of **hardware** watchpoints only. `set
can-use-hw-watchpoints 0` + `watch -l` (software) works fine and found this writer in one shot on
a program this size. Recommend RULES.md gain the qualifier; the hit-count discipline stays correct
for long-running programs where software watchpoints are too slow.

## 6. WHY THIS MATTERS FOR MILESTONE 1

`beauty.sno`'s `Command` is an ALT with capture-carving arms reached through a pattern variable —
the shape of this whole probe directory. Beauty's blob is additionally **wire-clobber**-framed
(hence zd-vetoed, hence not corrupted by THIS instruction), so this finding is **NOT yet claimed as
beauty's blocker** — that remains the `Command` non-leaf resume story. But the two rungs share one
prerequisite, and it is now measured rather than predicted: **cross-blob zd pricing and
`blob_frame_bytes()` must be reconciled before either can move.** Doing it as corruption repair
also buys the s128 widening for free.

## 7. NEXT RUNG (routed, not started — END-OF-CONTEXT LAW)

1. **Reconcile the two owners of `blob_entry+N`.** Start at `src/contracts/zeta_storage.c`
   (`zd_plan`/`zvo_resolve`) + the emit.cpp staging, and at `blob_frame_bytes()`
   (`emit.cpp:2338`). Either the callee prices its leaf cells BELOW its own frontier, or the
   caller's carve reserves the callee's priced window — **ONE AUTHORITY, not both** (s68/s70
   spelled-twice disease).
2. **Gate on `probe/clobarm/` 5/5** (4 red→green, `trueinline` stays green) **before** anything else,
   plus the standing pristine manifest 361/361, crosscheck m3 A/B, and the s127 five named movers
   120/131/165/181/182 (that retraction is what proves the ORDER: pricing first, framing second).
3. Only then revisit the s128 admission widening for the clobber-arm class.

⛔ **DO NOT** attempt this by widening `blob_choice_rbp_scan` — the fault is upstream of the choice
record entirely and fires with no choice record in play.
