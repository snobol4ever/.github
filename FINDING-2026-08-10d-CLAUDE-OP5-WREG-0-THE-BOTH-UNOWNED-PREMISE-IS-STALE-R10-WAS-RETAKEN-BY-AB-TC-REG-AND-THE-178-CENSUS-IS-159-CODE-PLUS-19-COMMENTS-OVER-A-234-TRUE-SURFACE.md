# FINDING 2026-08-10d (Claude Opus 5) — WREG-0: the design's "both unowned" premise is STALE (r10 was re-taken by AB_TC_REG), and the 178-site census is 159 code + 19 comments over a 234-site TRUE surface

**Goal:** `GOAL-PASSTHRU-RBP-ERAD.md` · LADDER WREG · rung **WREG-0** (claim + sweep + gate).
**Watermark:** SCRIP `bce9a4b0` at open (== s12-close cursor, nothing moved under this seat) → **`1d81b015`** at this finding. corpus `bea31de0` untouched. Container-fresh clone, unshallowed.
**Charter served:** Lon, s12/s13 in-chat — *"Eradicate PROC linkage to pattern BLOBS and use proper GLUE using R10 and R11 for GAMMA and OMEGA."*
**Status: NOT a code rung.** One gate landed (informational, zero behavior change). The sweep itself is NOT done and is explicitly NOT claimed.

---

## 1. ⛔⭐ THE DESIGN'S REGISTER-PICK GROUND #2 IS FALSIFIED AT HEAD — r10 IS NOT UNOWNED

LADDER WREG justifies `rΓ=r10 · rΩ=r11` on three grounds, of which the second reads: *"both unowned — REGISTER-LAYOUT's retirement notice says r10/BBREG_DATA is OUT, r11 has no role."*

**That is true of the retirement notice and false of HEAD.** `src/templates/bb_func_activate.cpp:25-26`:

```c
#define AB_TC_REG   ((g_rtcc_on && RTCC_GLOBAL_R9_GVA) ? "r10"  : "r9")
#define AB_TC_REG_D ((g_rtcc_on && RTCC_GLOBAL_R9_GVA) ? "r10d" : "r9d")
```

Used at `:216` (`movzx AB_TC_REG, cl` — the AB RETURN/NRETURN/FRETURN type code) and compared at `:222` and `:347`.

**Provenance, from the fix's own comment at `:216` (verbatim, and the sentence that matters is the third):** *"RTCC-SAFE (s8): r10 when the GVA claim is live -- r9 = RT_GVA_VA under RTCC_GLOBAL_R9_GVA and the veneer writeback would store this type code into the canonical GVA slot, killing [r9+k\*16] process-wide (proven: AB=1 RTCC=1 fibonacci SIGSEGV). **r10 is scratch-tier claimed with NO global assigned, so it keeps the author's survives-the-C-call property.** RTCC OFF -> r9, byte-identical."*

So r10 was freed by the retirement notice and **re-taken afterwards by the s8 RTCC-safety fix — which selected it *because* it was claimed-but-unassigned.** WREG assigns a global to r10 and thereby **retires the exact property that fix depends on.** The design read the notice; it did not read HEAD. This is stale-by-one-landing, not wrong-at-writing — but it is load-bearing for a register pick that the ladder calls LOCKED.

### Reachability — the de-escalation, stated as precisely as the hazard
`src/runtime/rtx/rtcc_init.c:20` — `unsigned char g_rtcc_on = 0;` (*"default OFF — killswitch law"*), set only from `getenv("SCRIP_RTCC")`. **The r10 arm is therefore DORMANT in every default build; the collision is live only under `SCRIP_RTCC=1`.** WREG is not blocked on this today. It IS blocked on it the day RTCC goes default-ON, and GOAL-RTCC's charter ("claim all 9 caller-saved GPRs as VM globals") points straight at that day.

### Why this is a routing item and NOT a drive-by fix
The obvious repair — move `AB_TC_REG` off r10 — needs a register that (a) survives the C call under RTCC, (b) has no global assigned, (c) is not r9/GVA, (d) is not r10/r11 once WREG lands. In the caller-saved pool that leaves **r8**, which the ladder itself flags as *"SCANBASE-entangled"*. Whether AB activation and SCANBASE liveness actually overlap is exactly the question a DEFINE'd function called from inside a match answers — and **RULES.md forbids acquittal by code-reading as firmly as conviction.** The `rtcc_claimed_reg_whitelist.txt` header says the same thing in its own words: *"A line here without a named probe is not a clearance."* So this wants a probe, i.e. a rung. It is recorded, not guessed.

## 2. THE CENSUS — the design's 178 reproduces EXACTLY, and is not the sweep surface

Measured at `bce9a4b0` over `src/templates/` + `src/emitter/`:

| measure | count | what it is |
|---|---|---|
| raw quoted `"r10"`/`"r11"` | **178** | reproduces the design's number to the digit (105 + 73) |
| same, comments stripped | **159** | the design's figure includes **19 comment-only mentions** |
| **ALL spellings, code only** | **234** across **29 files** | the TRUE sweep surface |

The **75-site delta** is the tail a `"r10"`-shaped grep cannot see: bracketed memory operands (`[r10 + 8]`, 191 raw) and sub-register spellings (`r10d`/`r11d`/`r10b`/`r11b`, 9 sites). **That blind spot is not academic — it is the mechanism by which the one pre-existing r10 claim in the product (§1, spelled `r10d` behind a macro) hid from the design's census.** Per-file burn-down is the gate's stdout; the head of it is `bb_call_fn` 82 · `xa_flat` 23 · `x86_asm.h` 16 · `bb_match_end` 12 · `bb_call_proc_staged` 12.

⚠️ The per-file *quoted* counts also disagree with the design's published split (design: bb_call_fn 36 · xa_flat 21 · bb_match_end 12 · bb_scan_match 8 · bb_func_activate 7 · bb_call_proc_staged 7; measured: 45 · 22 · 12 · 8 · 7 · 7). bb_call_fn is the one real divergence (36 → 45). Not chased this seat; flagged so the sweeping seat sizes bb_call_fn from the gate, not from the ladder text.

## 3. LANDED — `scripts/test_gate_wreg_claim.sh` + `scripts/wreg_claim_whitelist.txt` (SCRIP `1d81b015`)

WREG-0's named gate. **Informational by default (exit 0), `--strict` hard-fails** — so it blocks nobody before WREG-1/2 land, exactly as `test_gate_rtcc_claimed_regs.sh` does for its own class.

**Two gates, two invariants, both wanted — stated in the gate header so nobody merges them:**
- `test_gate_rtcc_claimed_regs.sh` = **COLLISION** class: who writes a live-claimed register *while also reading through GVARQ*.
- `test_gate_wreg_claim.sh` = **SCOPE** class: who *mentions* r10/r11 at all, outside the sites licensed to own the wires.
A file can pass the first and fail the second: **r10-as-scratch is harmless to GVA and fatal to γ.**

Whitelist is **EMPTY BY DESIGN** at creation — at WREG-0 every mention is sweep debt, `x86_asm.h` included; its encoder internals become licensed entry (3) the moment a wire spelling actually needs them. Adding a line before its rung lands would hide debt rather than license ownership.

Carried forward from the RTCC gate's hard-won trap, because it silently inverts results: **never `| grep -q` under `pipefail`** — `grep -q` closes the pipe, upstream `sed|perl` takes SIGPIPE(141), pipefail propagates, and *a match reads as a miss*. Every count in the new gate uses `grep -c`.

## 4. ⛔ THE ONE-LINE EDIT THAT WREG-2 MUST NOT FORGET

`test_gate_rtcc_claimed_regs.sh` carries `LIVE_CLAIMS="r9:RT_GVA_VA:RC-5-GVA"` and its own instruction: *"Add a register to LIVE_CLAIMS the moment RC-5 assigns a global to it — that one edit is what buys the next assignment this protection."*

**At WREG-2, when site glue actually carries the wires, that line must become `r9:RT_GVA_VA:RC-5-GVA r10:GAMMA:WREG-2 r11:OMEGA:WREG-2`, and `WREG_CLAIM_LIVE=1` must flip in the new gate.** Both edits are recorded in the new gate's STATUS TIERS block. Skipping them re-runs the s6/s7 r9 story on r10 — with the H2 veneer-writeback hazard intact, i.e. a clobber that survives the template and destroys γ process-wide.

## 5. ⭐ THE SYNERGY THE DESIGN UNDERSELLS (recorded because it changes how WREG-2 should be argued)

The ladder mentions RTCC only defensively (*"veneers bracket every rt_\* crossing, which also neutralizes the lazy-binding resolver's r11 clobber"*). The stronger statement is available and comes from the s8 fix's own reasoning in §1: **a scratch-tier RTCC claim is precisely what makes a register survive a C-RT crossing without the holder saving it.** That is the property WREG needs from r10/r11 — a blob's γ/ω must outlive every `rt_*` call it makes. So RTCC's veneer is not merely compatible with WREG; **it is the mechanism that makes register-carried wires viable across the runtime boundary at all.** The s8 fix already proved the property works, on r10, by measurement (the fibonacci SIGSEGV it cured). WREG inherits a tested mechanism rather than betting on an untested one.

## 6. WHAT THIS SEAT DID NOT DO — named so nobody reads silence as completion

- **The sweep is NOT started.** 234 sites stand. Each rename needs a liveness argument at its site, and the free caller-saved pool is genuinely tight (§1) — this is why the ladder's word "discretionary" in *"178 discretionary-scratch renames"* is carrying more weight than it looks like it is.
- **No suites run.** WREG-0's exit criterion (probe + xc m3 BY SET unchanged vs s12b: probe 33/5/1 · xc 82/40) is **UNVERIFIED**. The s7/s8 floors remain owed on top.
- **No manifest.** WREG-0's *"every surviving invariant blob post-PT-2b + witnesses + sbl refs, committed"* is NOT produced. The `sbl` oracle was not cloned or built this seat.
- **WREG-1/2 not attempted, deliberately.** The ladder says they want a FRESH full-runway seat and that *"a deletion landed at end-of-context is a broken tree by construction."* Attempting the PROC-shim eradication on the back half of a seat that had already spent its front half on orientation and census would have produced exactly that.

**LIMITATION on §1:** the falsification is source-level and provenance-level (the fix's own comment names its dependency), plus one measured environment fact (`g_rtcc_on = 0` default). It is NOT a probe. Nobody should record AB_TC_REG as *cleared* or as *broken* on the strength of this file — it is recorded as **collided and unprobed**, which is a different and smaller claim.
