# FINDING 2026-08-11 — RTCC s16 (Opus 5): THE FIVE CONSTANTS ARE TWO CLASSES, AND GUARDING THREE OF THEM MANUFACTURES THE H2 SIGSEGV CLASS

**Rung:** RC-0 class (hygiene/correctness). **SCRIP** `565ecfa8` → `d6893783`. **corpus** → `a38e551f`.
**Emitted bytes: ZERO** (measured, see §4). Watermark re-proved at open AND close.

---

## 1. The standing instruction was wrong in kind for 3 of the 5

Carried since s12 and repeated in every cursor since: *"guard all five duplicated RTCC constants in ONE commit or none; one-sided guard strictly worse than none."*

The tree was found **in exactly the one-sided state** the instruction warns about — but the cure is **not** symmetry. Guarding the remaining three would have manufactured the very defect the guard exists to prevent.

| Constant | State at open | `-D` override | Class |
|---|---|---|---|
| `RTCC_GLOBAL_R8_ANCHOR` | guarded (s11) | **takes** | KNOB |
| `RTCC_GLOBAL_R9_GVA` | guarded (s11) | **takes** (1→0) | KNOB |
| `RTCC_SLOT_R8` | unguarded | silently ignored | **ABI** |
| `RTCC_SLOT_R9` | unguarded | silently ignored | **ABI** |
| `RTCC_GVA_REG` | unguarded | silently ignored | **ABI** |

Probe (`/tmp/probe_rtcc.c`, gcc `-w` as the tree builds): baseline `SLOT_R9=6 GVA_REG=r9 R9_GVA=1`; with `-DRTCC_SLOT_R9=7 -DRTCC_GLOBAL_R9_GVA=0 -DRTCC_GVA_REG='"r8"'` → `SLOT_R9=6 GVA_REG=r9 R9_GVA=0`. Without `-w`, gcc reports `"RTCC_SLOT_R9" redefined` / `"RTCC_GVA_REG" redefined` — **the tree-wide `-w` eats both**, which is the s11 mechanism that voided two graded rungs, still live on three constants.

## 2. Why guarding the ABI three is strictly harmful — PROVEN, not argued

`RTCC_SLOT_*` is only the **C half** of a two-sided ABI. The **asm half** is raw literals inside `x86_rtcc_wb_bin` / `x86_rtcc_rl_bin` / `x86_rtcc_wb_text`:

- `grep -rn "RTCC_SLOT_" src/templates/` → **zero real uses** (one comment mention at `x86_asm.h:307`).
- **12** raw slot literals in the wb/rl encoders; R9's offset `48` appears at `x86_asm.h:318`, `:334`, `:363`.

Demonstrated with a guarded copy of the header: with `#ifndef` added, `-DRTCC_SLOT_R9=7` **takes on the C side** (`rtcc_init` seeds `g_rtcc_block[7]`, `keywords.c` companion-writes there) while the encoders keep addressing `block+48` = `block[6]`. C and generated code then disagree about where `RT_GVA_VA` lives → every `[r9+k*16]` near-null → **the H2 SIGSEGV class documented above `x86_rtcc_wb_bin`**, produced by the guard meant to prevent a silent `-D`.

`RTCC_GVA_REG` carries the same coupling in the other direction: the reload encoders hardcode `mov r9,[r11+48]`, so renaming the register alone makes `GVARQ`'s 56 call sites address a register the veneer never seeds.

**LAW (new): KNOB ⇒ GUARD. ABI ⇒ SEAL.** A constant read by **both** halves is a knob — a `-D` reaches the emitted bytes and the flip is coherent by design. A constant read by **one** half, whose partner is a hardcoded literal, is ABI — guarding it converts *silently ignored* into *silently half-applied*, which is worse: the first yields two identical binaries (detectable as a null), the second yields a real but incoherent binary that looks like a successful experiment.

## 3. What landed

`static_assert` block in `x86_asm.h` immediately above the encoders, binding all **9** slot macros to the literals, `RTCC_GVA_REG` to `"r9"` (constexpr string compare), and the GPR tier width. Classification comments in `rtcc.h` marking the three as SEALED with the reason and pointing at the assertions. A drift is now a **BUILD ERROR**, never a silent miscompile.

**Positive controls — both fire (build exit=2):**
- `RTCC_SLOT_R9` 6→7 → `RTCC ABI drift: RTCC_SLOT_R9 ... this is the H2 SIGSEGV class`
- `RTCC_GVA_REG` r9→r8 → `RTCC_GVA_REG no longer names the register the reload encoders load`

Per s13's law, the seal is reported with the control that proves it can fail; an assertion block that has never been observed failing is indistinguishable from a comment.

## 4. Zero emitted bytes — measured, not assumed

Determinism checked first (2 runs, same binary, same hash). fibonacci mode-4 emission md5 **`3c63fed568a589b35eca7561dfb9cb42`** — identical on the sealed build and on a `git stash`ed rebuild of the same HEAD. `static_assert` emits nothing; this is the corroboration, not the argument.

**Watermark, open and close:** claim gate `--strict` **PASS** (COLLISION CLASS EMPTY, HAZARD SURFACE 19 — matches s12 exactly); fibonacci m3 `result: 832040` at `SCRIP_RTCC=0`, `=1`, and absent (the s13 default-ON flip confirmed live).

**No perf number is quoted.** Observed 344ms/383ms is 1.11×, inside this box's ~1.12× noise floor — s12's law forbids reading it, and RC-0(a)'s criterion is still unmet here.

## 5. ⛔ SECOND FINDING: the `.s` artifacts were stale by two commits, and the regen billed it to the wrong rung

RULES §4 owes a regen from any session touching `x86_asm.h`. s16 touched it **non-emittingly** and the regen produced **13,654 insertions / 2,200 deletions across 23 files** — which cannot be s16's, since s16's emission md5 is unchanged.

**Attribution, mechanical:** `roman.s` at `82c34a01` (last honest regen, RTX-FUNC-1+2) contains **0** occurrences of `g_rtcc_block`; at HEAD it contains **309**, and the added lines are dominated by veneer writeback/reload pairs (206 `mov r11`, 105 `mov r8`, 103 `mov r9`, 103 `mov r10`). **TRUE OWNER: SCRIP `c4cb8813` "RTCC DEFAULT-ON", pushed without the step-4 regen**; `565ecfa8` (ZCTX) sits in the same window.

The regen script's default message labelled the commit with *my* rung. Amended to name the true owner (`a38e551f`) so the next session does not read 13,654 lines as an RTCC s16 codegen change.

**LAW (new): A REGEN BILLS ITS DIFF TO WHOEVER RUNS IT, NOT TO WHOEVER CAUSED IT.** The regen is a *debt collector*: it sweeps every un-regenerated emission change since the last honest artifact into the running session's commit. Before accepting a regen diff, check it against your own rung's measured emission delta — if your rung is byte-neutral and the diff is not, the bytes are inherited and must be attributed by name. Same family as CRATER ATTRIBUTION (attribute by builds, not by argument).

## 6. Process notes

- **Heartbeat, one-directional (s15) — confirmed again.** No peer this session (only `/home/claude/.seat-RTCC-544`); canonical paths were unoccupied, and the two commits past the s15 cursor were ~40 min old and already on origin.
- **Path-pinning (s15h) acted on.** 192 script references expect `/home/claude/corpus`, 34 `/home/claude/SCRIP`. Trees were placed at the canonical paths **before** running any gate, so the claim gate graded the tree actually edited. A private clone would have graded whatever sat at the canonical path — or nothing.
- **A KILLED BUILD LEAVES 0-BYTE OBJECTS AND READS AS A BROKEN HEAD (new, s16).** A backgrounded `make` is reaped when the tool call returns; it left a **0-byte `bb_assign_global.o`**, and the next link failed with `undefined reference to bb_assign_global[abi:cxx11]()` — which looks exactly like a broken HEAD on a clean clone. `find out -name '*.o' -size 0 -delete` is the one-line cure. Diagnose a link failure on a fresh clone by checking object *sizes* before suspecting the tree.
