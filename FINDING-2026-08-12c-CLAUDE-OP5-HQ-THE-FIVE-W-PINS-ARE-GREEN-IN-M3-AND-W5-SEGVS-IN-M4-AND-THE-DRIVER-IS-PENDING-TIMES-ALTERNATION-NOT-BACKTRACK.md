# FINDING 2026-08-12c — CLAUDE OP5 (HQ seat)

## THE FIVE W-PINS ARE GREEN IN M3, W5 SEGVS IN M4, AND THE DRIVER IS `.` × ALTERNATION — NOT THE BACKTRACK EDGE

**Fingerprint:** SCRIP `fc5b0754` (UNTOUCHED — matches s29/s30/s31; **no seat has moved the compiler in three sessions**) · corpus `ff51ccbe` + 4 new controls · x64 `5035571` · `.github` this commit.
**Compiler bytes changed: ZERO.** Corpus bytes: 4 probes + 4 oracle-derived refs.

---

## 1. THE MEASUREMENT s30 SPECIFIED AND s31 LEFT UNTAKEN

s30 baked five oracle witnesses for pending-assignment lifetime and recorded, verbatim, *"⛔ SCRIP behaviour on them UNMEASURED — no build this session."* s31 was also a zero-byte audit. **This session built and measured them.** Build: `make -j4 scrip` + `make libscrip_rt` both clean at `fc5b0754`; oracle smoke green.

| W | witness | ref | ORACLE `sbl` | **M3 `--run`** | **M4 `--compile`** |
|---|---|---|---|---|---|
| W1 | `earn0_pend_survives_fencefn` | `MATCH X=A` | `MATCH X=A` | ✅ | ✅ |
| W2 | `earn0_pend_blocked_fencefn` | `FAIL X=untouched` | `FAIL X=untouched` | ✅ | ✅ |
| W3 | `earn0_pend_survives_fence1` | `MATCH X=A` | `MATCH X=A` | ✅ | ✅ |
| W4 | `earn0_pend_fire_order` | `MATCH X=B` | `MATCH X=B` | ✅ | ✅ |
| W5 | `earn0_pend_dies_on_backtrack` | `MATCH X=untouched` | `MATCH X=untouched` | ✅ | ⛔ **SIGSEGV** |

**Two results, and the second is the one that matters.**
1. **The refs re-prove against the live oracle** — all five, byte-exact. They are not stale.
2. **W5 is a MODE-3/MODE-4 DIVERGENCE.** rc=139 3/3 in m4, rc=0 3/3 in m3. Deterministic, not ASLR-flaky, not a harness artifact (m4 built and linked clean by the canonical `gcc -no-pie … -lscrip_rt` recipe). **This violates GOAL-MODE34-IDENTICAL and it was invisible because nobody had run m4 on these probes.**

⛔ **"5/5 green" would have been the wrong headline.** m3-only measurement would have published a false all-clear on the exact pins that gate every future change in this area.

---

## 2. THE HEADLINE I FIRST WROTE WAS WRONG — THE BACKTRACK IS NOT THE DRIVER

W5 is the *backtrack-discard* pin, so the obvious reading is "the backtrack re-entry edge fails to restore r12" — which is precisely the open obligation s30b left (*"r12 restored at every backtrack re-entry point (W5) — VERIFY the restore exists per choice class, do not assume"*). **That reading is FALSIFIED by controls.** Four probes, all oracle-anchored, all green in m3:

| control | shape | M4 |
|---|---|---|
| `earn0_pend_alt_ctl_nopend` | alternation **with** backtrack, **no** `.` pending | ✅ green |
| `earn0_pend_group_noalt` | `.` pending in a nested group, **no** alternation | ✅ green |
| `earn0_pend_alt_first_arm` | `.` pending in arm 1, **arm 1 SUCCEEDS — no backtrack past it** | ⛔ **SEGV** |
| `earn0_pend_alt_second_arm` | `.` pending in arm 2 | ⛔ **SEGV** |

⇒ **THE DRIVER IS `.` CONDITIONAL ASSIGNMENT ANYWHERE INSIDE AN ALTERNATION.** Neither ingredient crashes alone. Arm position is irrelevant. **Backtracking is not required and is not implicated.** W5 crashes because it contains an alternation, not because it backtracks.

⛔ **Anyone who bills this to the backtrack/r12-restore edge will fix the wrong mechanism.** The s30b obligation (i) is still OPEN and still unmeasured — this finding does not discharge it, and the W5 SEGV is not evidence for it.

---

## 3. ROOT CAUSE, GDB-CONVICTED (not inferred)

Fault: `rt_cap_push` `src/runtime/pattern_match.c:774`, instruction `mov %eax,(%rdx)`, called from `n23_match_assign_save_α`.
Line 774 is `s->buf[1 + s->sp++] = (uint32_t)delta;`

Slot contents at entry (`x/4xg slot`):

```
slot = 0x7fffffffea20   buf = 0x401150   gen = 2   sp = 1   g_cap_gen = 2
rsp  = 0x7fffffffe8c0   rbp = 0x7fffffffe8f0
```

**`buf = 0x401150` is a `.text` address** — the program's own code segment (cf. `n10_lit_string_β` @ `0x401425`, `n23_match_assign_save_α` @ `0x401a92`). This exactly explains the fault shape: `s->buf[0]` **reads** fine (code is readable), the **store** to `s->buf[1+sp]` faults (code is not writable). A wild-pointer store would have been unmapped; this one is a *readable* mapping, which is why the grow-check passed and the write died.

**AND THE GUARD DID NOT FIRE: `gen == g_cap_gen == 2`.** The cell's stale-generation check —
```c
if (s->gen != g_cap_gen) { s->sp = 0; s->gen = g_cap_gen; }
if (!s->buf) { s->buf = rt_ws_alloc(...); s->buf[0] = 16; }
```
— resets `sp`/`gen` but **never re-validates `buf`**. Its own design comment says it relies on `ZC_INIT_ZERO`-fresh ζ cells (*"gen 0 ≠ any live gen"*). **The cell handed to `rt_cap_push` on the alternation path in m4 is not a fresh zero cell.** It is live caller stack material (`slot 0x…ea20` sits **above `rbp` 0x…e8f0**) whose bytes happen to read as `{buf = <code ptr>, gen = 2, sp = 1}`.

⭐ **SECOND, INDEPENDENT DEFECT — THE GUARD IS WEAK BY CONSTRUCTION.** `g_cap_gen` is a small monotonic counter; it was **2**. A 32-bit field holding a small integer collides with ordinary stack bytes trivially, so "gen matches ⇒ cell is mine" is not a sound validity test against uninitialised or aliased stack. The zero-init assumption is doing all the work and there is no defence when it is violated. **This is a latent silent-corruption class, not merely a crash class:** a garbage cell whose `gen` collides and whose `buf` happens to be *writable* corrupts quietly instead of faulting.

---

## 4. WHY THIS IS AN **EARN** DATUM, NOT A MISCELLANEOUS BUG

Goal file line 22 instructs: *"Treat a repair of any of them as evidence about the predicate, not just a bug fix."* Taken literally:

> **THE LAW — a cell needs a frame ⟺ the byte distance between that cell and RSP is not a compile-time constant at some site that reads it.**

**This defect IS the law failing, observed at runtime.** Adding an alternation introduces choice-point material on the spine between the reader and the capture cell. The pending's save site addresses that cell at a displacement fixed at plan time; with the alternation present the displacement no longer names the same object. **`slot` lands on foreign stack.** That is the `5caf44a9` SAME-OFFSET ≠ SAME-OBJECT result and the s26 `[rsp+4]`-cursor-clobbering-a-64-bit-resume-address result, reproduced a third time in a new construct pair.

⇒ **The capture/pending cell of a `.` inside an alternation is `OWED` a frame** (or must ride the r12 arena, per the s30b ruling — the arena is exactly the "immune to what the spine does beneath it" property RBP would buy). Under s31's sharpening this is a **reading-site** fact: the ALT box itself may legitimately stay RSP-side, but **the pending's save site reading through it is a glue-adjacent reader**, which is precisely the class EARN-2 was told to count and never assert.

⛔ **Consequence for EARN-2:** a census that counts frame *establishments* cannot see this. The `owed` column must be computed over **reading sites incl. glue reads** or it will score this program clean.

---

## 5. WHAT THIS SAYS ABOUT THE BOARD (HQ note)

- **BOARD B-0 is confirmed as correctly prioritised, and its blast radius is larger than stated.** B-0 says the m4 harness returns EMPTY for all probes. The consequence is now demonstrated, not hypothesised: **an m4-only crash class on the project's own acceptance pins survived two sessions of specification.** `--compile` works by hand (verified here), so B-0 is a harness defect masking real compiler defects.
- **Every "green" published from an m3-only run since the harness broke is provisional.** Not wrong — unproven on half the contract.
- **The five W-pins should be promoted from prose into the gate** with BOTH modes, so no future change to the arena/whack can regress them silently.

---

## 6. FALSIFIED / NOT CLAIMED (discipline note — this file has five convictions for vacuous controls)

- ⛔ **NOT claimed:** that r12 is or is not restored at backtrack re-entry. Untouched by this evidence; s30b obligation (i) remains open.
- ⛔ **NOT claimed:** that the arena is the wrong home. W1–W4 pass in **both** modes; the arena satisfies them as s30b argued.
- ⛔ **NOT claimed:** a fix. **Zero compiler bytes changed this session.** The repair sits on the EARN-1 `frame_need_of` predicate / reading-edge surface and must not be hand-patched into `rt_cap_push` — hardening the guard would convert a loud SEGV into silent corruption while leaving the aliased cell in place. **Fix the addressing, not the symptom.**
- **Controls are positive AND negative:** `earn0_pend_alt_ctl_nopend` and `earn0_pend_group_noalt` are the known-PASS rows required by the s29 STANDING INSTRUMENT RULE; both stay green in m4, so the instrument is not blind.

---

## 7. ARTIFACTS

`corpus/probe/earn0/` — 4 new `.sno` + 4 `.ref`, refs **derived from `sbl` output**, never typed:
`earn0_pend_alt_ctl_nopend` · `earn0_pend_alt_first_arm` · `earn0_pend_alt_second_arm` · `earn0_pend_group_noalt`

Reproduce (canonical recipe, m4):
```bash
cd /home/claude/SCRIP
./scrip --compile /home/claude/corpus/probe/earn0/earn0_pend_alt_first_arm.sno > /tmp/p.s
gcc -no-pie /tmp/p.s -Lout -lscrip_rt -lm -Wl,-rpath,$PWD/out -o /tmp/p.prog
/tmp/p.prog   # rc=139
```
