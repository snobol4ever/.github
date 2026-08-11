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

---

# ADDENDUM — s16b: THE ARG-TIER RULING, TAKEN (VETOABLE), AND A GC GAP THAT BLOCKS IT

Lon in-chat: *"All your choices."* Per the s13b precedent the ⛔LON rulings below are **taken by me and are VETOABLE**.

## 7. RULING (vetoable): MINT RC-8, do NOT re-open RC-4

s14 asked: *re-open RC-4 as `[~]` with reload carry, or mint an explicit rung for arg tier + XMM?* **Mint RC-8.** Reasons: (a) RC-4's closure was correct **for what it claimed** — it landed the writeback and the scratch-tier reload, and explicitly deferred the arg-tier reload in a comment; re-opening a correctly-closed rung to carry someone else's scope is how a ledger stops meaning anything; (b) the arg tier and XMM now carry a **prerequisite defect** (§9) that did not exist in RC-4's frame, so the work is genuinely new; (c) s14 declined to re-open another seat's closed rung and that instinct was right.

**RC-8 shape (ordered — the order is the ruling):** RC-8a GC coverage (§9) — *blocking, must land first* · RC-8b decide the arg tier: claim it (add the reload) **or** stop paying for it (drop the 5 dead stores), see §8 · RC-8c XMM8–15: either stage them or **amend the charter** to say 9 GPRs, because at HEAD there is no rung behind the XMM claim at all.

## 8. THE ARG TIER IS PAID FOR AND NEVER COLLECTED — 5 OF THE VENEER'S 14 INSTRUCTIONS

s14's *"arg tier reload orphaned"* is right in substance but the precise fact is sharper and changes the arithmetic. **`rtcc_load_all` is not orphaned** — it has exactly two call sites, `src/driver/scrip.c:1490` (mode-4, emits `call rtcc_load_all@PLT`) and `:1651` (mode-3, direct call), and **both are the process-entry crossing**. It reads the block **once per process, before any generated code has run**. The per-crossing reload (`x86_rtcc_rl_bin`/`rl_text`, verified identical) restores only `{r8, r9, r10, r11}`.

Therefore `rax rcx rdx rsi rdi` are **stored on every crossing and reloaded by nothing**: **5 of the 14 instructions per crossing are pure cost at HEAD.**

**This reframes RC-6.** s13b's static instrument is `crossings_removed × 14`, whose payoff sits behind per-family RTX *eradication* (s13b: eligible set = 1 symbol of 54). But `crossings × 5` is available **with no eradication at all**, on the same noise-free static instrument. Against s11's measured crossing counts: **fibonacci 9,423,879 × 5 = 47,119,395 instructions; roman defer trio 6,600,066 × 5 = 33,000,330.** That is the same order as RC-6's headline prize, unblocked.

⛔ **NOT COSTED, AND I DID NOT IMPLEMENT IT.** `x86_rtcc_wb_bin` uses the RAX store + `movabs rax, block` as its RSP-safe way to obtain a base register, so dropping the arg-tier stores is not a 5-line deletion: it needs a base-register story (RAX is caller-saved and dead before a `rt_*` call, but "dead" must be **probed**, not assumed — vararg callees read AL), and it interacts with §9. **Estimating this and building it are different rungs; I did the first only.** RC-8b is where it belongs.

## 9. ⛔ NEW DEFECT — THE BLOCK IS NEVER SCANNED BY THE GC

`rtcc_gc_register` calls `rt_gc_root_pin_add` **only**. In `gc_heap.c` these are not the same thing:
- line 625 — pinned roots go to `rt_gc_pin_ptr(p)`: pins the **pointer value** `p`
- line 626 — ranges go to `gc_cons_scan(lo,hi)`: **scans the memory**

Every other block registration in the tree does **both** (`zeta_heap.c:161`, `rt_coexpr.c:74`). RTCC does only the first, so **the block's 32 slots are scanned by nothing**, and `rtcc_init.c`'s *"at any GC point all claimed-register values sit in the block; registering it is sufficient — no per-register pin needed"* is **false**: the premise holds, the conclusion does not.

**LATENT at HEAD** — r8 is an integer (`&ANCHOR` value), r9 is the mmap'd GVA island, r10/r11 are code addresses; no claimed register can hold a heap DESCR. **LIVE the instant the arg tier is claimed**, because RAX:RDX carry `DESCR_t` returns: a heap object reachable only from a claimed register would be invisible to the collector. Use-after-free.

⛔ **CONSEQUENCE: RC-7 MUST NOT FOLD.** Its DoD line 1 would certify a veneer that protects 3 of 17 registers and whose canonical block is outside the GC's reach. And **RC-8a blocks RC-8b**: claiming the arg tier before fixing coverage converts a latent gap into a live use-after-free.

Note the composition: §8 says unclaimed slots are written for no reason; §9 says claimed slots are unscanned. Both are the same principle — **the block should contain exactly the claimed set, no more and no less** — and RC-8a/RC-8b should be designed against that sentence rather than separately.

## 10. WHAT LANDED (s16b): `scripts/test_gate_rtcc_block_coverage.sh`

The census as one command. Reproduces the inherited numbers **independently**: veneer 9+5 = **14** instructions/crossing (s13b), ROUND-TRIP `r8 r10 r11` = **3** (s14), plus RELOAD-ONLY `r9` (correct by H2) and WRITEBACK-ONLY `rax rcx rdx rsi rdi`.

**It is SELF-ARMING, not permanently red** — a gate that is red at HEAD gets ignored or blocks commits. It WARNS while the GC gap is latent and turns **FAIL automatically** the moment an arg-tier register joins ROUND-TRIP. No future session has to remember §9; the tripwire arms itself.

Positive controls: simulated arg-tier claim → GC tripwire fires `USE-AFTER-FREE`; the BOTH-MEDIUM check fired independently because the simulated claim touched TEXT only — the realistic shape of a half-claim.

**Two instrument defects found and fixed BEFORE any number was trusted:** (a) v1 parsed the BINARY encoder's **comments** for register identity — grading documentation, not code, the s13b class exactly; fixed by parsing the TEXT encoders (real asm strings) and cross-checking BINARY structurally by instruction count. (b) v1 miscounted the `RTCC_GLOBAL_R9_GVA`-guarded store in both mediums, crediting `r9` as written-back when HEAD skips it, and raising a **false** BOTH-MEDIUM alarm — the s11 class. Reported because a gate's first census is exactly where the s11/s13b traps live.

## 11. NEW LAWS

- **KNOB ⇒ GUARD, ABI ⇒ SEAL** (§2). Guarding a constant whose partner is a hardcoded literal converts *silently ignored* into *silently half-applied*. The first yields two identical binaries — detectable as a null. The second yields a real but incoherent binary that **looks like a successful experiment**. That is strictly worse, and it inverts s12's "one-sided guard is worse than none": the correct completion is not to guard the rest, it is to classify them.
- **A REGEN BILLS ITS DIFF TO WHOEVER RUNS IT, NOT WHOEVER CAUSED IT** (§5). Check any regen diff against your own rung's measured emission delta; if your rung is byte-neutral and the diff is not, the bytes are inherited and must be attributed by name.
- **A COVERAGE CLAIM IS NOT A COVERAGE MECHANISM** (§9). "Registering the block is sufficient" was true of the *premise* (values do sit in the block) and false of the *mechanism* (`pin_add` never scans). When a comment asserts sufficiency, find the function that does the work and read it — sufficiency claims are where BLOCK-CANONICAL-style laws rot.
- **PREFER A SELF-ARMING GATE TO A RED ONE** (§10). A gate that is red at HEAD is either ignored or blocks every commit. Encode the condition that makes the defect *live* and let the gate arm itself; the analysis then survives without anyone remembering it.
- **A KILLED BACKGROUND BUILD READS AS A BROKEN HEAD** (§6). A backgrounded `make` is reaped when the tool call returns, leaving 0-byte objects; the next link failed `undefined reference to bb_assign_global[abi:cxx11]()` on a **clean clone at origin HEAD**. Check object sizes (`find out -name '*.o' -size 0`) before suspecting the tree.

## 12. s16c — RC-8b's "RAX IS DEAD" PREMISE IS **NOT** RETIRED (partial probe, reported as a null)

§8 named the blocker for dropping the arg-tier stores: `wb_bin` uses the RAX store + `movabs rax,block` as its RSP-safe base-register story, so the deletion needs RAX to be genuinely dead before a veneered call — **probed, not assumed** (vararg callees read AL).

**Attempted and NOT completed.** Two censuses, both returned zero, and per s13's law a zero is not a measurement until a non-zero is named beside it. Controls:

- **Vararg census — CONTROL PASSED, reading stands but is NARROW.** Zero variadic `rt_*` declarations; the same regex finds **20** variadic declarations across `src/` (`sno_error(int,const char*,...)`, `rebus_error`, `mremap`), so the instrument works. ⇒ *no `rt_*` callee reads AL*. **But this does not clear the premise**: variadic non-`rt_*` symbols exist and I did not establish whether any is veneered.
- **Veneered-symbol census — CONTROL FAILED, MY INSTRUMENT WAS WRONG.** I grepped `x86_rtcc_call("sym")` and read 0 veneered symbols. The veneer is not invoked that way: templates emit **`x86("rtcc_wb")` (12 sites) and `x86("rtcc_rl")` (12 sites)** around the call, so the callee symbol is *not* an argument to the veneer at all. Same class as s13b's `.globl` census and s11's `LD_AUDIT` complement — **a census over this tree must use the tree's own spelling.**

⇒ **RC-8b stays blocked on this probe**, and the correct instrument is now named: walk the **12 `x86("rtcc_wb")` template sites** and identify the call each brackets, rather than searching for a symbol-parameterised veneer that does not exist. Recorded so the next session inherits the instrument and not the false zero.

**LAW (reinforced, third occurrence this session): CHECK A ZERO AGAINST A NON-ZERO FROM THE SAME INSTRUMENT.** It caught a bad instrument here (veneered-symbol census), validated a good one (vararg census), and earlier caught the gate's comment-parsing defect. Cost per check: one grep.
