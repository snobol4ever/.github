# FINDING 2026-08-10d (Claude Opus 5) — WREG-0: the design's "both unowned" premise is STALE (r10 was re-taken by AB_TC_REG), and the 178-site census is 159 code + 19 comments over a 234-site TRUE surface

**Goal:** `GOAL-PASSTHRU-RBP-ERAD.md` · LADDER WREG · rung **WREG-0** (claim + sweep + gate).
**Watermark:** SCRIP `bce9a4b0` at open (== s12-close cursor, nothing moved under this seat) → **`802cf6bd`** at this finding. corpus `bea31de0` untouched. Container-fresh clone, unshallowed.
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

## 2b. ⛔⭐⭐ THE RTX ASM SURFACE — 182 MORE SITES THE CENSUS NEVER SAW, AND THE SHARPEST EDGE IN THE PRODUCT

After the census above was taken, this seat's own parent commit turned out to carry a directive that changes the number. `.github` `37e0273c` (CROSS-GOAL BULLETIN, Lon-directed, cross-posted to all five concurrent seats) says to the SNOBOL4-RTX seat, verbatim:

> *"Any RTX asm that clobbers r10 or r11 silently breaks EVERY pattern blob in flight — the wires are live across the entire match, and a corrupted rΓ/rΩ is a wild jump, not a wrong answer. RTX may run concurrently IFF its asm either PRESERVES the pair or sits behind an RTCC veneer.* ⛔ *WREG-0's claim gate must sweep RTX asm sources, not just `src/templates/` — raw-byte and hand-written asm do not grep as `"r10"`."*

Gate extended (SCRIP `802cf6bd`) and measured:

| region | mentions | files | in the design's 178 census? |
|---|---|---|---|
| `src/templates/` + `src/emitter/` | **234** | 29 | partially (as 178 raw / 159 code) |
| `src/runtime/rtx/*.S` hand-written asm | **182** | 10 | **NO — entirely invisible to it** |
| **TRUE TOTAL** | **416** | **39** | — |

**The sweep is ~2.3× the size the ladder budgets for.** Per-file head of the RTX burn-down: `rtx_match.S` **74** · `rtx_icnsub.S` 25 · `rtx_alloc.S` 18 · `rtx_str.S` 17.

⭐ **`rtx_match.S` at 74 is the single sharpest edge in the product for WREG**, and the reason is structural rather than statistical: it is the MATCH runtime, so it executes *during* a match — precisely the interval in which γ/ω are live in r10/r11. Every other region can at worst corrupt a value; this one corrupts a jump target. The bulletin's phrase is exact.

The two burn-downs are reported SEPARATELY by the gate and folded together only in the `--strict` verdict, because a template rename and a hand-written-asm rename are different work needing different proofs — the template arm goes through `x86()` encoders under the TEMPLATE-RULES, while `.S` files are outside that discipline entirely.

**Consequence for the ladder's own routing:** LADDER WREG lists RTX nowhere in its sweep cost (*"178 discretionary-scratch renames measured: bb_call_fn 36 · xa_flat 21 · bb_match_end 12 · bb_scan_match 8 · bb_func_activate 7 · bb_call_proc_staged 7 · rest small"*). The bulletin routes it, but the ladder was never updated to match. **[SUPERSEDED BY §2c — the veneer already banks the pair, so the RTX arm needs neither owner nor sweep.]** ~~The RTX arm needs an owner named before WREG-1 lands~~, since by the bulletin's own logic an unswept `rtx_match.S` does not degrade WREG gracefully — it makes it unsafe from the first blob that calls into the match runtime.

## 2c. ⛔⭐⭐⭐ THE DECIDING FACT — **WREG HAS A HARD CORRECTNESS DEPENDENCY ON RTCC=ON, AND RTCC IS DEFAULT OFF.** (And the corollary: the 182 RTX sites need NO sweep.)

Chasing §2b's blocker to its root produced the single most consequential fact of this seat. Read `x86_asm.h`:

**`x86_rtcc_wb_bin` (the pre-call half) saves the pair:**
`mov [rax+56], r10` (R10 slot 7) · `mov [rax+64], r11` (R11 slot 8).
**`x86_rtcc_rl_bin` (the post-call half) restores exactly the scratch tier** — its own header: *"RC-4 PARTIAL RELOAD: only the SCRATCH TIER {R8, R9, R10, R11} is restored from the block"* — `mov r10,[r11+56]` · `mov r11,[r11+64]`.

**So the save/restore of γ/ω across a C-RT crossing ALREADY EXISTS, is committed, and is the default RC-4 behaviour whenever RTCC is on.** It is precisely the mechanism WREG needs, built for another purpose and already paid for.

⭐ **COROLLARY — §2b's 182-site RTX blocker DISSOLVES.** Whatever `rtx_match.S` does to r10/r11 *inside* the call is invisible to the caller: the wires were banked before the call and reloaded after. The bulletin's escape clause — *"RTX may run concurrently IFF its asm either PRESERVES the pair or sits behind an RTCC veneer"* — is satisfied by the **second** disjunct, structurally, for free. **The RTX arm needs no owner and no sweep; the sweep is 234, not 416.** (Self-correction of this seat's own §2b conclusion, made three tool-calls later. The 182 sites are real; the *inference that they must be swept* was wrong.)
Note the veneer even clobbers r10 itself for its own indirect-call stub (`movabs r10, ptr; call r10`, justified in-comment as *"R10 already written-back, free as indirect-call scratch"*) — and that is still WREG-safe, because the reload follows. Save → clobber → call → restore is net-preserving.

⛔ **BUT THE GUARANTEE IS ENTIRELY CONDITIONAL, AND THE CONDITION IS OFF BY DEFAULT.** The veneer's first line is a killswitch:
```c
inline std::string x86_rtcc_call(const char *sym, uint64_t ptr) {
    if (!g_rtcc_on) return x86_call_ro(sym, ptr);   /* KILLSWITCH: gate OFF → byte-identical to pre-RTCC */
```
With `g_rtcc_on == 0` — **the default** (`rtcc_init.c:20`, *"default OFF — killswitch law"*) — every `rt_*` call is a **bare call with no writeback and no reload**, so r10/r11 are clobbered per plain SysV caller-saved rules by *any* runtime call a blob makes.

**Therefore: at RTCC=OFF, γ/ω in r10/r11 do not survive a single `rt_*` call, and by the bulletin's own standard the failure mode is not a wrong answer but a wild jump.** LADDER WREG lists the veneer as *ground #3* for the register pick — a supporting argument. It is not a supporting argument. **It is a precondition.** The ladder nowhere states that WREG requires RTCC=ON, and the two killswitches currently default in opposite directions: WREG is specified to land **default-ON at WREG-2** (*"ON is default at WREG-2 landing (PT-1 precedent)"*) on top of an RTCC that is **default-OFF**. Landing that combination ships wires with no survival mechanism.

**THE ROUTING QUESTION THIS FORCES (Lon only — it is a strategy call, not an implementation detail).** Three ways out, and they are not equivalent:
1. **WREG default-OFF until RTCC goes default-ON** — safe, but WREG delivers nothing until the RTCC seat finishes, and PT-1's default-ON precedent is broken.
2. **WREG-2 emits its own unconditional save/restore around `rt_*` crossings when RTCC is off** — self-sufficient, but it re-implements the veneer and the ladder's *"NO SHIM is literal"* claim quietly stops being literal.
3. **RTCC goes default-ON as a WREG prerequisite** — cleanest and matches *"this ladder is the payoff of the RTCC investment"* (bulletin), but it makes a five-seat scheduling dependency explicit and hands WREG's schedule to the RTCC seat.

**RESIDUAL HAZARD — CENSUSED AND CLEAN.** `x86("call_bare")` is *"intentionally veneer-free"* in **both** gate states, so any use outside an explicit `rtcc_wb`/`rtcc_rl` bracket would be an unprotected crossing even at RTCC=ON. Measured: **12 uses across 8 templates, and every file's `call_bare` count equals its `rtcc_wb` count equals its `rtcc_rl` count** (`bb_assign_global` 1/1/1 · `bb_binop_arith` 3/3/3 · `bb_binop_concat_slot` 1/1/1 · `bb_binop_gvar_arith_slot` 1/1/1 · `bb_call` 2/2/2 · `bb_call_fn` 1/1/1 · `bb_call_proc_staged` 2/2/2 · `bb_match_begin` 1/1/1). **No unbracketed `call_bare` exists.** Per-file count equality is not per-site pairing, so this is a clean *screen*, not a proof — but it is clean, and it says the residual hazard class is presently empty.

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
