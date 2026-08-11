# FINDING 2026-08-11 (Claude Opus 5, s18) — WREG STEP 1 HAS NO VALID CHOKE: RSP-SAFETY AND A STACK-ARG WITNESS KILL THE BRACKET, SO THE WIRE SAVE BELONGS TO THE TEMPLATE

**Fingerprint:** SCRIP `5fbefd41` (UNTOUCHED — zero `src/` bytes changed this session) · corpus `5da04e78` · `.github` at session open `37e0273c`-lineage.
**Method:** source verification + site census + one byte-level witness. No code landed. No gate moved.

---

## 0. BASELINE RE-PROVED AT HEAD (the tree is in the documented state)

Built clean at `5fbefd41` (`-O0`, RT_OPT=0). Both documented anchors reproduce exactly:

| probe | result | matches file? |
|---|---|---|
| `treebank-match.sno < treebank.input` (327 B) m3 | **rc=139 SIGSEGV** | ✅ the FF-0 witness |
| `claws5-match.sno < CLAWS5inTASA.dat` m3 | **rc=0**, 20 B out | ✅ the defer-free survivor |

⛔ **BUILD TRAP FOR THE NEXT SEAT (cost this seat ~15 min):** a build killed mid-compile leaves a **ZERO-BYTE `.o`** that `make` then treats as up-to-date, and the failure surfaces as a *link* error in an unrelated symbol (`undefined reference to bb_lit_scalar[abi:cxx11]()`) — not as a compile error. `grep -c "error:"` reads **0** the whole time. Cure: `find out -name '*.o' -size 0 -delete` then rebuild. Do not chase the symbol. **Background builds do not survive between tool calls in this container** — `nohup make &` dies when the call returns; build in the FOREGROUND in chunks (make is incremental).

---

## 1. THE STEP-1 CHOKE: THREE CANDIDATES, ALL THREE WRONG

LADDER WREG-COMPLETE Step 1 (cursor CONSOLIDATED-2) reads: *"At the ONE choke `x86_align_enter/leave` (both media), push/pop {r10,r11} around every `call rt_*`."* s17 corrected this to *"the three `x86_rtcc_call*` / `x86_call_ro` funnels."* **Both are wrong, and so is the corrected third candidate.** Measured at HEAD:

| candidate | sites | verdict |
|---|---|---|
| `x86_align_enter/leave` | **78** (s17 said 37 — that was *pairs*) | ⛔ **emits NOTHING**: both early-return `std::string()` under the default `ZC_FRAME_RSP` (x86_asm.h:1863/1868). s17's claim (a) CONFIRMED at source. |
| `x86_rtcc_call` + `x86_rtcc_call_descr` + `x86_call_ro` | **4 + 6 + 11 = 21** | ⛔ **FEWER sites than the pair s17 rejected**, and they sit *below* the dispatch — they are the leaf helpers the dispatch arms delegate to. They miss the `XK_PORT`, `XK_REG` and TEXT-medium arms entirely. Not a choke. |
| `x86()` dispatch arms `"call"` / `"call_rt"` / `"call_bare"` (x86_asm.h:1632/1644/1653) | **350** `x86("call"…)` callers | ✅ **This IS the one choke** — and x86_asm.h:580 already says so verbatim: `x86_align_assert()` is *"prepended to EVERY emitted call form at the one \"call\" dispatch arm."* Proven universal-injection precedent. ⛔ **But see §2 — a push/pop bracket here is incorrect by construction.** |

⭐ **The "37 of 349" figure that framed s17's Problem 1 is two different units** (37 pairs vs 78 call sites vs 350 `x86("call")` callers). The conclusion s17 drew from it — *the align pair is not the choke* — is nonetheless **correct**, for the stronger reason in row 1: it emits nothing at all.

---

## 2. ⛔⭐⭐⭐ THE BRACKET IS NOT MIS-PLACED — IT IS WRONG AT EVERY IMPLICIT CHOKE. TWO INDEPENDENT PROOFS.

### (a) BYTE-LEVEL WITNESS: emitted calls pass arguments ON THE STACK

`src/templates/bb_arith.cpp:25-29` emits, in order:

```
lea  rax, [rip + <symbol>]
push rax                      <-- ARGUMENT, passed on the stack
call rt_arith
add  rsp, 8                   <-- caller cleanup
```

A bracket injected **at the dispatch arm** emits its `push r10; push r11` *between the argument push and the `call`*, burying the argument under 16 bytes. `rt_arith` then reads the saved r11 as its stack argument. **This is not a latent hazard — it breaks on the first call, and the killswitch the ladder specifies as `default ON` would have shipped it that way.** The dispatch arm cannot see arg setup; that is precisely what disqualifies it as a bracket site.

### (b) THE RSP-SAFETY LAW IS LIVE, AND IT APPLIES TO WREG FOR THE VENEER'S OWN REASON

x86_asm.h:300 — *"the veneer fires inside templates that may have live ζ cells on RSP. **NO push/pop allowed.**"* Verified LIVE in both media, not aspirational:
- **BINARY** `x86_rtcc_wb_bin`: zero push opcodes; uses the REX.W MOV-moffs-rax absolute encoding to avoid needing a base register.
- **TEXT** `x86_rtcc_wb_text` (:359): carries `/* RSP-SAFETY: no push/pop */` and stores RAX via a direct symbol reference.

⛔ **STALE COMMENT, DO NOT BE MISLED (it cost this seat a wrong turn):** the header block at x86_asm.h:281-282 still describes a writeback that *"push r11 … then pop [r11+64]"*. **No live implementation does this** — both media replaced it with push-free encodings. The prose survived the fix. It is not a counter-example to the law.

⭐ **The law is VENEER-SCOPED, NOT GLOBAL** — templates push around calls freely (`bb_arith.cpp:27` above; `bb_call_proc_staged.cpp:565` `push r12`; 54 `x86("push",…)` sites). **The distinguishing property is not "near a call," it is IMPLICIT vs EXPLICIT.** A template that pushes knows its own live rsp-relative state and compensates. A save injected by the dispatch is invisible to the template that owns the surrounding ζ cells, so it displaces flat refs the template already computed — the identical mechanism `x86_align_enter` documents in its own no-op comment: *"its own pushes are what displaced every flat ref inside it."*

**⇒ A WREG C-call wire save at an implicit choke is forbidden by the same live law, for the same reason, as the RTCC veneer.** s17 was right that Step 1 and the RSP-SAFETY LAW cannot both stand. The resolution is not a routing preference between them: **the law wins on mechanism, and the bracket has no site.**

---

## 3. THE PINCER — AND WHERE THE SAVE ACTUALLY BELONGS

Two constraints now close on the C-call wire save from opposite sides:

1. **No push at an implicit choke** (§2, RSP-SAFETY) — rules out the stack-pair bracket.
2. **No flat save area** — this file's own conviction at `rtcc.h:63` `g_rtcc_block[32]`: a flat cell cannot serve a LIFO discipline, so under a nested crossing the inner save destroys the outer γ. Rules out the veneer-style block.

⛔ **There is no third option AT A CHOKE.** Therefore the wire save is **not choke work at all**:

- **The template that owns the call emits it.** There, push/pop is legal (proven by 54 live sites), and the template knows its own carve, so the displacement is accounted rather than injected. This is also the only place that can distinguish a leaf `rt_*` crossing from a defer-eval crossing that may re-enter emitted code.
- **The discipline is per-activation on the FORTH spine** — WREG's own ONE LAW, already the stated cure at W-MAP items (2)/(3). Step 1 was the one facet that tried to satisfy it globally and implicitly; that is exactly the facet that cannot be.

⭐ **This RETIRES the "Lon routing call" the cursor has been blocked on since s14** (*exclude-wires vs depth-indexed block vs WREG-independent-of-RTCC*). It was posed as a choice between mechanisms at a choke. **Measurement removes the choke, so the question dissolves rather than resolves** — and the surviving answer is the one option s13c's reconciliation already named as the only nesting-correct one: WREG emits its own save, per-activation, on the spine.

---

## 4. WHAT THIS COSTS AND WHAT IT SAVES

**Costs:** Step 1 as written is not a rung — it is a no-op at candidate 1, a partial at candidate 2, and a corruption at candidate 3. It cannot be "greened." Steps 2/3/4 are **unaffected in substance** (they were always spine-record work); only Step 1's premise falls, and Step 3's g_zctx reader conversion inherits nothing from it.

**Saves:** the ladder's own note says Step 1's killswitch is *"default ON … safe pre-flip (registers are dead there today — brackets are semantically inert until wires go live)."* ⛔ **That safety argument is FALSE for the stack-arg class**: the bracket's *displacement* is live on arrival even when r10/r11 are dead, because it moves rsp under an argument that is already on the stack. A seat that trusted "semantically inert" would have landed default-ON breakage across every stack-arg call site in the product and then hunted it as a regression somewhere else entirely.

---

## 5. NEXT SEAT, IN ORDER

1. **Do NOT implement Step 1.** Re-specify it as: *the wire save is template-emitted, per-activation, on the spine* — i.e. fold it into W-MAP (2)/(3) and delete the "one choke" facet. This is a **cursor edit, not code**.
2. The FF-0 mechanism (blob γ/ω/res never restore rbp; the 2/15 set == the defer programs) is **untouched by this finding and still the live defect**. Nothing here contradicts CONSOLIDATED-2's root-cause chain.
3. FF-0b (the DIVERGE quartet at `930539c0`) remains unbisected and is still the cheapest unspent measurement on the board.
4. Regen ×3 still owed from s17 — **not** owed by this session (zero `src/` bytes changed).

⛔ **NOTHING WAS LANDED. NOTHING WAS RESTORED. The delete stays deleted, per the standing Lon directive.**
