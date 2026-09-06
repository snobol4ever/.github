# FINDING 2026-09-06 hq_T — ARBNO's null-body guard baseline is never rolled back when the exhaust arm recedes, so a null shallower instance passes the guard forever

**Seat:** hq_T (HQ-TEST) · **Row:** `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries` · **MODE:** OCTET
**Tree graded:** SCRIP `b6d2ae3f7` + this change, corpus `8fdad5458` + the promotion · **Build:** incremental `make`, `RT_OPT=-O0`
**Cured:** `arbno_fence_bal_replace_branch_2` (master seq 1888, origin `probe_fuzz__fz_segv_03`), both modes. **DONE-WHEN n: 11 → 10.**

## 1. The entry, and the reason that had rotted

```
G0 = BAL RPOS(3)
G1 = (BREAK(' ') | '')
P  = (FENCE((BREAKX('ab')) $ v0) *G0 | ARBNO(*G1))
'a b c' *P RPOS(0)      :S(OK)F(NO)      oracle: match
```

The xfail reason (rewritten 2026-09-06) called this "rc=1 in BOTH modes — NO CRASH AT ALL … a plain wrong answer,
the cheapest possible ablation target". **rc=1 was right and "wrong answer" was wrong.** Measured here:
`ERROR 246 -- stack overflow (unbounded or too-deep recursion exhausted the call stack)`, both modes, deterministic
under `setarch -R`. ⭐ A clean runtime-error exit and a wrong answer are the same `rc=1` to any grader that reads only
the code, and this reason was written from an rc alone. **An rc is not a verdict; the first line of output is.**

## 2. The witness reduces to one line with none of the named ingredients

Eight ablations of the fuzz witness, then eight more. Everything the entry's NAME advertises — FENCE, BAL, the
capture, BREAKX, the outer defer, the alternation between the two arms — is **irrelevant**:

```
'a b c' ARBNO((BREAK(' ') | '')) RPOS(0)      :S(OK)F(NO)      oracle: match, SCRIP: ERROR 246
```

Three ingredients, each proven necessary by a one-ingredient green sibling:
* a first arm that **can succeed and later match null** — `('x' | '')` is GREEN, `(SPAN('abc') | '')` and
  `(BREAK(' ') | LEN(0))` are RED, so it is the null-after-progress behaviour, not the node kind;
* the **null arm last** — `('' | BREAK(' '))` is GREEN;
* a **forcing tail** — dropping `RPOS(0)` is GREEN.

⛔ Do not read the family names as the ingredient list. This entry is filed under `arbno_fence_bal` and contains no
FENCE-, BAL- or capture-dependent defect at all.

## 3. The mechanism — measured in gdb, not argued

`bb_match_arbno_frame` keeps **one** cell, `AFC(4)`, as the null-body guard's baseline: the cursor at the end of the
last accepted instance. `γ_as` fires the guard on `cursor == AFC(4)` and otherwise advances it. The exhaust arm
(`ω_af`) recedes into the body on `cursor != AFC(0)` — **dropping one instance** — and does **not** roll `AFC(4)` back.

After a recede, the guard therefore grades a **shallower** instance against a **deeper** instance's cursor. In the
witness the shallower instance re-matches null at cursor 0 while `AFC(4)` still reads 1, so `0 != 1`, the guard does
not fire, ARBNO accepts a null instance, the tail fails, and `β` re-enters the body at its **α** — the exact state the
machine was in one cycle earlier.

Breakpoint on the body's α, printing `rsp` and the cursor:

```
hit  0  rsp=0x7ffffffee000  cursor=0        hit  1  rsp=0x7ffffffedfe0  cursor=1
hit  2  rsp=0x7ffffffedfe0  cursor=0        hit  3  rsp=0x7ffffffedfc0  cursor=1
...  cursor oscillates 0/1 forever; rsp falls 0x20 every two hits
```

**It is a non-terminating loop that also leaks**, one 32-byte alternate activation per cycle — which is why the
symptom is a stack overflow rather than a hang, and why this entry was originally filed as a SEGV witness.

## 4. The cure

`src/templates/bb/bb_match_arbno.cpp`, `bb_match_arbno_frame`'s exhaust arm only: before receding, roll the guard
baseline back to ARBNO's own start (`eax` already holds `AFC(0)`). Receding to instance *k−1* makes ARBNO's start the
correct baseline whenever *k−1* is the first instance, which is the case the witness and every entry in the master
actually reaches; it is strictly closer to correct than a baseline belonging to an instance that no longer exists.

⛔ **Named rather than implied: this is not the fully general fix.** The exactly-correct baseline is the *start cursor
of the instance being re-entered*, which lives in the **body's** frame, not ARBNO's — with one cell ARBNO cannot grade
an instance it receded into at depth ≥ 2. `bb_match_arbno_frameless_k` already has the right shape (a 16-byte cell
**pushed per instance** and **popped before its recede**, `L(3)`), but it is reachable only for an rsp-neutral body
(`_sq` in `emit.cpp`) — precisely because ARBNO cannot interleave rsp pushes with a body that pushes its own frame.
A general cure needs a guard stack ARBNO owns; the 16-byte `arbno_frame_slot` has no room for one. **That is the next
ground on this mechanism, and it is a design change, not an edit.**

## 5. Blast radius — measured over every entry, not sampled

**SNOBOL4 master, all 1890 entries**, emitted `.s` byte-diffed between a genuine base build and the patched build:

| SAME (exonerated by construction) | CHANGED | compile-fail on both | rc diverged | total |
|---|---|---|---|---|
| 1742 | 112 | 36 | **0** | 1890 |

All **112** changed entries then run in **both modes on both builds** against their own refs:
**exactly 1 verdict changed — `arbno_fence_bal_replace_branch_2`, FAIL→PASS in m3 AND m4 — and 111 unchanged.**
Base 92/224 → patched 94/224 over that set; the +2 is that one entry's two modes. **Zero regressions.**

**Rebus master, 772 entries: SAME=181, CHANGED=0.** `IR_MATCH_ARBNO` is emitted by `lower_snobol4.c` **only**
(measured: `grep -rl IR_MATCH_ARBNO src/lower src/parsers` returns that one file), so byte-identity is the
SHARED-NODE VERDICT SCOPE discharge for the frontends that reach the shared lowerer.

Stability of the cured entry: **10/10 ASLR-on and 3/3 `setarch -R`, both modes.**

⛔ **A copied `./scrip` is not a baseline** — the driver is ~240 KB and the emitter lives in `out/libscrip_rt.so` with an
absolute `DT_RUNPATH`. Both libraries were built separately, proven distinct by `md5sum`, selected with
`LD_LIBRARY_PATH` (searched **before** RUNPATH), and **the selection was proven on the witness before any diff was
trusted**: base rc=1 ERROR 246, patched rc=0 `match`.

## 6. Two instrument results worth more than the cure

⛔⭐ **`test_gate_raku_paren_call_passes_its_arguments.sh` IS RACING AND IT IS BLOCKING `make test` FOR EVERYONE.**
It is arm 2 of 60, so its red stops the other 58 arms — including the SNOBOL4 board — from running at all. First
reading said base PASS / patched FAIL, which reads exactly like a regression from this change. Repeating it four
times per build on a box at load ~15 of 16 cores:

| run | base | patched |
|---|---|---|
| 0 | PASS(0) | FAIL(1) |
| 1 | FAIL(2) | FAIL(3) |
| 2 | PASS(0) | PASS(0) |
| 3 | FAIL(1) | FAIL(4) |

**The violation count varies run to run on an unchanged build, and the base build fails 2 of 4.** The failures are
`BUILDFAIL` on the scratch binary — the build race hq_B and I already diagnosed, not a verdict on any tree.
⭐ **A single base/patched split that agrees with your hypothesis is not evidence until the base arm is repeated**;
one reading of a racing instrument would have had me revert a correct cure.

⛔ **`make test` runs 60 recipe arms, not the 35 the digest claims** (four values in four days). Read the recipe.

## 7. Also corrected

* All eleven ARBNO killswitches (`SCRIP_ARBNO_{TAILBETA,FRAMELESS,ALTSIB,K16,SEAL_OMEGA,REENTRY,LATCH,PEEK,ROOTSPINE,FPRPOP}`,
  `SCRIP_OPT=0`) are **inert** on this witness — the defect is base design, behind no flag. Nobody need re-probe them.
* `SCRIP_RESUME_WHY=1` prints **identical** output for the red witness and its green sibling here. It names the
  resume-carrier family; this is not that family, and the instrument correctly said nothing.
* `s4e_msg.sh done` answered "not your claim" for a row with **no claim file at all**, naming the wrong defect and
  sending the reader to look for an owner who does not exist (ceo CEO-362, hq_C's bus finding). Split into two
  diagnostics, both arms proven live.
