# ⛔⭐⭐⭐ GOAL-RBP-EARN — ADDING RBP AT ALL THE RIGHT SPOTS

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-12 s43 (Claude Sonnet 5) — **EARN-0b's OPEN QUESTION ANSWERED: THE `earn0_stored_varref` HANG IS NEITHER IN `rt_defer_step` NOR A GENERATOR-TERMINATION ISSUE. IT IS A CLOBBERED `r11` WIRE IN `bb_match_defer`'s BLOB-ENTRY GLUE. ROOT-CAUSED LIVE UNDER gdb, NOT YET FIXED. ZERO SRC BYTES CHANGED.**

**What happened:** picked up s42's exact next-step instruction (`set breakpoint pending on` → `break rt_defer_step` → watch return values). Built clean, confirmed the hang reproduces (`rc=124`) on both a minimal repro (`P = LEN(1)` / `Q = P LEN(2)` / `'abc' Q`) and the canonical `corpus/probe/earn0/earn0_stored_varref.sno`. **First finding: `rt_defer_open`/`rt_defer_close` are RTX asm veneers (`src/runtime/rtx/rtx_match.S`) over the C `c_rt_defer_open`/`c_rt_defer_close` I'd read from `pattern_match.c` — but `rt_defer_step` really is plain C, exactly as s42 said.** Breaking on `rt_defer_open`/`rt_defer_step` under `--run` (mode-3, JIT in-process) never fired — confirmed by attaching to the live hung process instead (`gdb -p $PID`) rather than trusting `run` to stop cleanly in batch mode. **The hang is NOT inside the defer runtime at all — those functions are called exactly once, successfully, on first entry, and never again.**

**Root cause, confirmed by repeated live breakpoint hits (not inferred from `.s` alone):** the infinite loop is a 2-instruction cycle entirely inside the JIT code for the OUTER pattern (`Q`'s own `proc_PAT$1`), not inside the deferred target (`P`'s `proc_PAT$0`) and not inside any runtime function:
```
proc_PAT$1_ω:   jmp   r11          ; r11 stale — loaded by n2_match_defer_α's OWN L(5), never restored
.Lx4_5:         add   rsp, 16
                jmp   proc_PAT$1_ω
```
Verified three independent ways under gdb: (1) set a live breakpoint at the observed `rip`, hit it repeatedly across `continue`s — `r10`/`r11`/`rax` bit-identical every hit, so it's a deterministic 2-instruction cycle, not chaotic corruption; (2) `stepi` through it and watched `rip` bounce between exactly those two addresses; (3) measured `rsp` across 8 breakpoint hits: +16 bytes per iteration exactly (one unbalanced `add rsp,0x10` per cycle) — it never SIGSEGVs and hangs forever because `add rsp,0x10` never dereferences memory, so a wildly out-of-range rsp is harmless to the loop itself.

**Mechanism, traced against source (`src/templates/bb_match_defer.cpp` + `src/templates/bb_glue_flat.cpp`):** `n2_match_defer_α` (the box for the stored-pattern-var reference `P` inside `Q`) calls `bb_glue_pass_wires_blob(4,5)` (`bb_glue_flat.cpp:162`) — `lea r10,[L(4)]; lea r11,[L(5)]; jmp rax` — to transfer into `P`'s resolved blob (`proc_PAT$0`), using `L(4)`/`L(5)` as **this node's own private** γ/ω continuation labels. `L(4)` correctly falls through into the REST of `Q`'s body (`n3_match_len_α`, matching `LEN(2)`) on `P`'s success. **But `Q`'s own shared failure port, `proc_PAT$1_ω`, is `jmp r11` — read from MANY sites throughout `Q`'s body** (six call sites in the minimal repro's `.s`, all assuming `r11` still holds `Q`'s true caller-supplied ω). `n2_match_defer_α` clobbers `r11` with its own local `L(5)` before the transfer and **never restores it on the success path** (the `L(4)` fallthrough does not reload `r11`). So when `n3_match_len` (matching `LEN(2)`) later fails inside `Q`'s body and does `jmp proc_PAT$1_ω`, it jumps into `n2_match_defer_α`'s own stale `L(5)` — which itself unconditionally ends in `jmp proc_PAT$1_ω` (`x86_omega()` at `bb_match_defer.cpp:98`) — a closed loop between those two labels that never reaches `Q`'s real caller.

**This reframes s39/s42's open question entirely.** It was never about whether `rt_defer_step` assumes generator termination — `rt_defer_step` is not in the loop. It is a **wire-lifetime bug in the pass-thru glue**: `bb_glue_pass_wires_blob`'s `r10`/`r11` loads are meant to be a **local, temporary re-purposing** of those registers for the duration of one blob transfer, but nothing in `bb_match_defer.cpp` restores the caller's original `r10`/`r11` before falling through past `L(4)` into the rest of the enclosing pattern's body — so any LATER failure inside that body, past the defer node, reads the wrong ω. This sits exactly on the goal's own named subject (the DEFER boundary) and is very plausibly the same class of bug EARN-10/EARN-11 (glue carries wires; `α`/`ω` establishes the frame) are meant to make impossible by construction — but note this is currently **WREG glue** (`SCRIP_WREG`-gated r10/r11 wire convention), not yet an EARN frame question per se; whether the eventual fix is "restore r10/r11 before falling through L(4)" (a glue fix, cheap) or "this is exactly why the box needs a frame" (an EARN fix, per the goal's own law) is the next call to make — **lean toward the glue fix first since EARN's law only mandates a frame when byte-distance-from-RSP goes unknown, and this bug is a plain register-save omission, not an addressing hazard.**

**NOT YET DONE:** the actual fix. **NEXT SEAT / continuation:** (a) confirm whether `L(4)`'s fallthrough is supposed to restore `r10`/`r11` to the values live at `n2_match_defer_α`'s own entry (i.e., save them before the `lea`s at `bb_glue_pass_wires_blob`, restore after `def L(4)`) — check whether `bb_glue_pass_wires` (the non-blob rcx/rdx sibling, used elsewhere) has this save/restore and `_blob` is missing it, or whether NEITHER has it and this is a product-wide latent bug that just happens to be invisible everywhere else because most callers don't have `Q`-style "more pattern after the defer, in the SAME enclosing pattern" shapes; (b) the minimal fix is almost certainly: push r10/r11 (or the caller's true γ/ω, which may already be sitting somewhere findable — e.g. on the spine from an outer glue) before the `lea` overwrite, pop/restore right after `def L(4)`; (c) verify board-clean (BY SET) on `crosscheck/patterns` + `probe/earn0/*` in both m3 and m4 before calling this fixed; (d) `earn0_varref_blob_hang` is recorded (s39 probe-ownership table) as "same class, shares MATCH_DEFER transfer" — check whether this same fix clears it too, or whether it's a structurally distinct site.

**WATERMARK: NOT RE-MEASURED, zero src bytes touched.** s39/s42's stands per the staleness law.

**Environment note for the next seat:** under `--run` (mode-3), `gdb -batch -x script.txt ./scrip` with a plain `break FN; run ...` in the script does NOT reliably stop at the breakpoint even though it resolves (confirmed via `start` + `info breakpoints` that the address is correct) — `run` alone in batch mode appears to race past it. **What works:** launch the program in the background, `sleep` briefly, find its real PID (`pgrep -f "^./scrip --run"` — NOT the `timeout` wrapper PID), then `gdb -p $PID -batch -ex "break *<live-rip>" -ex "continue" ...` — i.e., attach to the already-running process rather than trusting `gdb ... -ex run` to stop cleanly. Each `gdb -p PID -batch ...` invocation attaches and detaches once; to hit a breakpoint multiple times in sequence, chain multiple `-ex "continue"`/`-ex "printf ..."` pairs in ONE invocation (attaching fresh each time re-resolves ASLR but loses your place if the process already exited).

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-12 s42 (Opus 5) — **THE SEVEN-SESSION BLOCKER WAS A MISSING `apt-get update`. gdb IS INSTALLED, VERIFIED, AND IN THE SETUP SCRIPT. ZERO COMPILER BYTES.**

**What landed (SCRIP `scripts/install_system_packages.sh`):** `apt-get update` before any install (it was never there — every install in this project's history resolved against an apt index baked at image-build time), `gdb` added to the package set with `--no-install-recommends`, per-package install loop, and a closing liveness line that prints the gdb version or warns. Idempotent; re-run prints `SKIP all packages already installed` + `OK gdb 15.1 present`.

**⛔ ROOT CAUSE OF s33–s39, STATED ONCE SO IT IS NEVER RE-DERIVED:** `gdb` *Recommends* `libc-dbg`; bare `apt-get install gdb` installs Recommends by default; that package's indexed version had been superseded and deleted from the mirror ⇒ 404. **`libc6-dbg` is NOT a dependency of gdb** — s39 reported the symptom accurately and diagnosed the cause wrongly, and six sessions before it inherited the conclusion without re-testing. The fix is three seconds. **This is a MEASURED instance of the class this file already legislates against (SHELF LIFE / "re-run, never cite"): a tooling verdict was cited across seven sessions and never re-run.** Consider extending the CENSUS shelf-life law to environment facts, not just counts — Lon's call.

**VERIFIED, not assumed:** `gdb 15.1` runs against `./scrip`; `nm -D out/libscrip_rt.so` shows `rt_defer_open`/`rt_defer_step`/`rt_defer_close` all `T`; the minimal repro `P = LEN(1)` / `Q = P LEN(2)` / `'abc' Q` still hangs rc=124 at HEAD under the current build. ⛔ **NEXT TRAP, ALREADY HIT AND RECORDED:** `break rt_defer_step` before the program runs reports *"Function not defined"* — those symbols live in `out/libscrip_rt.so`, which is not loaded at gdb start. Use `set breakpoint pending on`. Dynamic linking, not a broken debugger.

**NEXT SEAT — s39's experiment is now runnable exactly as it was written**, and nothing about it has been superseded: `set breakpoint pending on` → `break rt_defer_step` → run the repro → `finish` across iterations and read the return value. The open question is unchanged: does `rt_defer_step` have a termination condition when the deferred target is a plain NON-generator (`LEN(1)`), or does it assume the target eventually reports "no more instances" the way a real generator does? If the latter, the fix is in `pattern_match.c:958-990`, not the lowerer. The fprintf fallback s39 proposed is no longer needed but remains valid.

**WATERMARK: NOT RE-MEASURED — zero compiler bytes touched this session**, so no number of mine is being claimed. s39's stands and is stale by the STALENESS LAW: re-run, do not transcribe.

**UNBLOCKS: EVERY SEAT** — MONITOR-FIRST step (2) is available product-wide for the first time in this stretch; any seat that recorded "no gdb in this container" should re-test before repeating it. **UNBLOCKS: RBP EARN-0b** — its method is a gdb watch and was unrunnable as written; caveats (B)/(C) in the rung still bind.

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-12 s39 (Claude Sonnet 5) — **s38's STEP 0 WAS STALE (the ASSIGN-elision no longer reproduces at HEAD). RE-DERIVED VIA MONITOR-FIRST: A REAL, DIFFERENT LOWERER DEFECT FOUND AND FIXED (`ca04abf2`, SCRIP). `earn0_stored_varref.sno` STILL HANGS — SECOND, UNLOCALIZED DEFECT REMAINS.**

**What happened:** opened s38's Step 0 (stored-pattern ASSIGN elision) and ran its exact reproduction commands. Neither arm showed the claimed elision — `ASSIGN var="P"` is present in the IR under both `SCRIP_PAT_INLINE` settings, at this HEAD. Per RULES.md MONITOR-FIRST, did not trust the stale writeup further; ran `test_monitor_2way_spitbol_vs_run.sh` on `earn0_stored_varref.sno` instead of continuing to read code from the old hypothesis.

**Real defect found and FIXED (`ca04abf2`, SCRIP):** `sno_seq_nary()` (`src/lower/lower_snobol4.c:1145`) wired every pattern-sequence element's backtrack (β) target to the **previous element's result node unconditionally** — correct for true generators (ARB/ARBNO/ALTERNATE, whose β genuinely advances retry state) but wrong for `IR_MATCH_DEFER`: `bb_match_defer` is a jmp-entry TRANSFER box into the deferred pattern's own code, not a generator with retained state. Re-entering it on a right-neighbour's failure just re-transfers into the target from scratch; when the target succeeds identically every time (e.g. `P = LEN(1)`), the composite loops forever with no progress. Minimal repro: `P = LEN(1)` / `Q = P LEN(2)` / `'abc' Q` hung (rc=124) at HEAD before the fix. `ir_is_generator_kind()` already existed and already classifies `IR_MATCH_DEFER` as generator-kind (correctly, for other consumers) — `sno_seq_nary`'s seam-fixup simply never consulted it. Fix excludes `IR_MATCH_DEFER` specifically from the `res[i-1]` resume wiring; every other generator kind is untouched.

**Verified board-clean (both boards re-checked this session, not just trusted from the commit message):** `board_patterns_set.sh` — crosscheck/patterns BY-SET diff REPAIRED=0 BROKEN=0, 76/122 both builds (3 already-failing recursive-defer programs 178/179/182 — the manual's own p.122 nested-list shape — shift SIG11→HANG, a diagnostic-signature change only, not a correctness regression). `board_earn0_set.sh` re-run fresh this session: byte-identical to the commit's claim — `earn0_stored_varref` FAIL-hang, `earn0_varref_cat_dropped` FAIL-silent, nothing else moved.

**⛔ NOT FIXED — `earn0_stored_varref.sno` and the minimal `Q = P LEN(2)` repro STILL HANG (rc=124) after the fix.** IR-level wiring is confirmed correct post-fix (`MATCH_LEN`'s ω now points at `FAIL`, not back at `MATCH_DEFER` — checked via `--dump-ir`). **CORRECTION TO THIS SEAT'S OWN EARLIER NOTE (caught before handoff, not by a peer):** an earlier pass through this cursor claimed the mode-4 `.s`'s `rt_proc_call_open`/`_epilogue_γ`/`_epilogue_ω` generator-drain loop (`.Lx4_2`/`.Lx4_7`/`.Lx4_8` in a minimal-repro `.s`) "only fires on DT_X-tagged values, not DT_P — not on this path," reasoning from `emit.cpp`'s prose comments rather than the emitted bytes. **Reading the actual `.s` for `Q = P LEN(2)` falsifies that: the loop IS reachable from the DT_P path.** `n2_match_defer_α`'s fast-cache check (`dtp_fn_of`, `.Lx4_9`/`.Lx4_10`) is a CACHE-MISS fallthrough to `.Lx4_0`'s cold path, which calls `rt_defer_open`, then loops at `.Lx4_2`: test the returned value, if non-zero `jmp` into it with `.Lx4_7`/`.Lx4_8` as return wires, `.Lx4_7` runs `rt_proc_call_epilogue_γ` + `rt_defer_step` then `jmp .Lx4_2` — an explicit backward edge. On first use in a freshly-built program the `dtp_fn_of` cache is necessarily cold, so THIS cold-path loop, not the fast one-shot path this seat inspected first, is the live mechanism for the hang. **Not yet determined:** whether `rt_defer_step`/`rt_proc_call_epilogue_γ` ever return a value that makes `.Lx4_2`'s test go to zero for a `MATCH_DEFER` target that is itself non-generator (`LEN(1)`) — if that termination condition assumes the deferred target is always generator-shaped (has a real "more instances?" answer), a plain `LEN(1)` reference may never satisfy it, which would be a second, genuinely distinct defect in `rt_defer_open`/`rt_defer_step` (`src/runtime/pattern_match.c:958-990`) rather than in the lowerer this rung already fixed. **Did not localize further this session: no gdb (`libc6-dbg` 404s in this container, `apt-get install gdb` fails), no strace/ltrace available** — reading `rt_defer_open`/`rt_defer_step`'s C source directly against the `.s` call sequence above is the next concrete step, not a repeat of the code read this seat already did (which was aimed at loop *existence*, not the termination predicate).

**NEXT SEAT:** Start at `src/runtime/pattern_match.c:958-990` (`rt_defer_open`/`rt_defer_step`/`rt_defer_close`) and read them AGAINST the `.Lx4_2`/`.Lx4_7`/`.Lx4_8` loop shape above (regen with `./scrip --compile /tmp/repro.s` on `P = LEN(1)` / `Q = P LEN(2)` / `'abc' Q` — or the corpus probe directly) — the open question is whether these functions have a termination condition for a deferred target that is a plain non-generator pattern, or whether they assume the target always eventually reports "no more instances" the way a real generator does. If the latter, the fix is in the runtime, not the lowerer. (a) get a working gdb in this container (try a different package source, or a static prebuilt binary) and breakpoint `rt_defer_step` with a spin/ignore counter per RULES.md's prescribed method to see actual return values across iterations; (b) failing that, a temporary fprintf in `rt_defer_step` (rebuild `libscrip_rt`) is cheap and would settle this in one run. `earn0_varref_cat_dropped.sno`'s default arm (PAT-INLINE path, PT-2 Defect B, `lower_snobol4.c:978-985`) is confirmed structurally separate — do not conflate the two when judging BY SET.

### ⛔⭐⭐⭐ s39 SCRUTINY OF THE PLAN — REQUESTED BY LON IN-CHAT. FOUR ITEMS, TWO NEEDING A RULING.

**⭐⭐⭐ (1) ✅ RESOLVED s42 — gdb IS AVAILABLE; THE BLOCKER WAS A STALE APT INDEX, NOT A BROKEN DEPENDENCY.** `bash scripts/install_system_packages.sh` now installs it (SCRIP, s42) and prints its version; `gdb 15.1` verified running against `./scrip` in this container, and the `Q = P LEN(2)` hang reproduced under it (rc=124). **ROOT CAUSE, so nobody re-derives it an eighth time:** the script never ran `apt-get update`, so every install resolved against an apt index baked at image-build time; and `gdb` *Recommends* `libc-dbg`, which bare apt installs by default, and whose indexed version had been superseded and deleted from the mirror. **`libc6-dbg` was never a dependency of gdb** — s39's diagnosis named the symptom, not the cause. Fix = `apt-get update` + `--no-install-recommends`, three seconds. ⛔ **Runtime `rt_*` symbols live in `out/libscrip_rt.so`, not in `scrip`** — a plain `break rt_defer_step` before the `.so` loads reports "Function not defined"; use `set breakpoint pending on`. That is dynamic linking, not a broken debugger, and it is the next trap on this exact hunt. **s39's NEXT-SEAT experiment is now RUNNABLE as written.** Original ask retained below for the record.
**(1-ORIG) THE TOOLING GAP IS THE REAL BLOCKER, AND IT IS UNOWNED — LON, THIS IS WHERE I MOST NEED HELP.** RULES.md's MONITOR-FIRST theorem specifies a THREE-step mechanical hunt: (1) monitor → first divergence; (2) **gdb breakpoint at the bracketed C site with a spin/ignore counter**; (3) single-step to the land mine. **Step (2) IS UNAVAILABLE IN THIS CONTAINER.** `apt-get install gdb` fails — `libc6-dbg 2.39-0ubuntu8.7` 404s on security.ubuntu.com. No `strace`, no `ltrace` either. So the prescribed method has a **broken middle rung**, and every seat that hits a runtime-level defect rediscovers this and then improvises. s39 got as far as reading emitted `.s` by hand and stopped exactly where step (2) would have started. ⇒ **CONCRETE ASK: add `gdb` to `scripts/install_system_packages.sh` (pinning or omitting the `libc6-dbg` dep, which is optional for breakpoint+register work), or bless an alternative step (2) in RULES.md — an instrumented `libscrip_rt` rebuild with fprintf at the suspect site is cheap and this container CAN do it.** Until one of those lands, every runtime-half bug in this file is bounded by hand-reading assembly, which is exactly the "reading code, guessing" that MONITOR-FIRST exists to forbid. **This single fix would do more for this goal's throughput than any rung below.**

**⭐⭐⭐ (2) ⛔ RULED s40 (Lon in-chat): option (c) TAKEN AND EXECUTED — see SCOPE section above.** Original ask retained for the record: s37's §7 question (a) split the defect ledger out, or (b) accept crash-triage as the prerequisite and re-title the ladder. **s39 is the SEVENTH consecutive session (s33–s39) spent entirely on crash triage. EARN-0 still blocked; EARN-1 never started; EARN-2 never opened.** ⛔ **s39 adds a NEW argument that favours (b) and that no prior session could make:** the defect this seat fixed sits **exactly on the EARN predicate's own frontier**. EARN Rule 1 (Lon, ruling (1) s28) names the owner as *"the operator who has a `*P` DEFER as an operand"* — and the seam-wiring bug was a control-flow defect on precisely that `MATCH_DEFER` boundary. **The defer transfer boundary is where BOTH the frame question AND the control-flow bugs live.** That is not a coincidence to triage away; it is evidence that the boundary is under-specified as a whole, and that "fix the crashes" and "derive the predicate" are the same work seen from two sides. ⇒ **This seat's recommendation is (b) with a scope note: re-title to name the defer boundary as the ladder's real subject, and keep the crash items that touch `MATCH_DEFER` HERE while routing the ones that do not (`treebank-array`, the duplicate-label class, BUILDFAIL-4) OUT to their owning goals.** That is a middle path s37 did not offer and it costs one editing pass.

**⭐⭐ (3) SCRUTINY OF THIS SEAT'S OWN FIX — A REVIEWER COULD REASONABLY REVERT IT, AND SHOULD BE TOLD SO PLAINLY.** `ca04abf2` is provably correct as graph shape (a backward β edge into a non-resumable transfer box is wrong by construction) and is board-clean (REPAIRED=0 BROKEN=0, 76/122 both builds). **But it delivers ZERO user-visible improvement today** — the probe it was aimed at still hangs — **and it makes three already-failing programs (178/179/182) fail SLOWER (SIG11→HANG), which costs real wall-clock on every corpus run that includes them.** The honest case FOR keeping it: IR correctness is a prerequisite for anyone reasoning about this area, and leaving a known-wrong edge in place to preserve a faster crash is trading correctness for convenience. The honest case AGAINST: under a strict may-only-add-passes reading it adds no passes and worsens test ergonomics, so it could wait for the runtime half and land as one coherent change. ⇒ **Lon's call. This seat kept it and states the tradeoff rather than burying it; do not read the green board as "this was free."**

**⭐⭐ (4) PROBE-OWNERSHIP TABLE — MEASURED s39, SO NOBODY DERIVES THE SPLIT A THIRD TIME.** The `earn0` board reports FAIL-hang / FAIL-silent with no attribution, so each arriving seat re-derives which defect owns which probe. s29 derived it, s37 partially re-derived it, s39 re-derived it again. Recorded here once:

| probe | m3 verdict | owning defect | status |
|---|---|---|---|
| `earn0_stored_varref` | FAIL-hang | seam-wiring (lowerer half **FIXED** `ca04abf2`) + **unlocalized runtime half** | runtime half OPEN — see cursor above |
| `earn0_varref_blob_hang` | FAIL-hang | same class as above (shares `MATCH_DEFER` transfer) | OPEN, not separately verified s39 |
| `earn0_varref_cat_dropped` | FAIL-silent | **PT-2 Defect B** (PAT-INLINE path; `Q = P P` lowers to plain `BINOP` concat, no patproc, no `MATCH_DEFER` at all) — `lower_snobol4.c:978-985` | OPEN, **structurally separate — do not conflate** |
| `earn0_varref_bare_dropped` | FAIL-silent | presumed PT-2 Defect B family | OPEN, unverified |
| `earn0_stored_capture` | FAIL-silent | s37 §3 folded this into EARN-0 (`$` capture inside stored pattern) | OPEN |
| `earn0_cap_after_bal` / `_varlen` | FAIL-silent | capture-after-variable-width; not investigated s39 | OPEN |
| `earn0_disc_arbno_star_fence_positive` | FAIL-silent | `ARBNO(*P)` + FENCE; manual p.122 recursion shape | OPEN |
| `l3_arb_pred` | FAIL-silent | L3 (LOWER seat) — not this goal | route out |

⛔ **Also measured s39 and worth pinning: `'MOUNTAIN' ? 'O' ARB . OUTPUT 'A'` — the SPITBOL manual's OWN canonical ARB-expansion example (p.64) — prints `NT` where the oracle prints `UNT`. This is PRE-EXISTING at HEAD (verified against a clean baseline build, NOT caused by `ca04abf2`) and is not on any board or probe list.** A wrong-answer on the manual's headline ARB example, invisible to every gate, is a bad thing to be carrying silently; it deserves a probe file at minimum.

**Frame iff the byte distance between a cell and RSP is not a compile-time constant at some site that reads it.**  
**PHASE: eradication COMPLETE (pattern blobs carry no RBP). All remaining work is ADDITIVE.**

**⛔⭐⭐⭐ DIRECTION CHANGE (Lon ruling s29): NO MORE ERAD — WE ARE DOING THE OPPOSITE.**
**EARN: every construct that needs a frame GETS one, IFF it needs one, derived from the predicate. Frames become MANY and TINY and the count RISES. Nothing is deleted for being a frame.**

**⛔ WHAT DIED IS THE *FRAME-DELETION PREMISE*, NOT THE MECHANISMS. ABSORBED INTO THIS GOAL AND STILL LIVE (Lon ruling s29):**
- **R10 / R11 AS THE WIRE REGISTERS — WE WILL DO THIS.** rΓ=r10 · rΩ=r11 carried in registers, product-wide convention. The old LADDER WREG below is the mechanism spec; it is ABSORBED here, not archived.
- **ONE-SHOT AND PASS-THRU GLUE — WE WILL DO THIS.** The old LADDER PT below is the sequence; ABSORBED, not archived.
- ⛔ **WHAT IS DEAD: the T1–T5 deletion-target lists, DEL-T's delete-first charter, and every "T-class → 0" / "census must show frames == 0" ratchet.** Those measured the wrong quantity. The ratchet is EARN-2's `unearned == 0 && owed == 0`.

**⛔⭐⭐⭐ ARCHITECTURAL RULING (Lon, s29) — RBP IS NOT PART OF THE GLUE.**
**There are exactly TWO glue kinds: ONE-SHOT and PASS-THRU. FRAMED IS NOT A GLUE KIND.** RBP establishment belongs to **`x86_alpha` / `x86_omega` (or the equivalent parameterized template form)**, keyed on the EARN predicate staged at plan time. Glue moves control and carries wires; α/ω establishes and releases the frame. **These are two separate concerns and must not be re-merged.** See THE EMISSION under EARN DESIGN OF RECORD.

**⛔⭐⭐⭐ PHASE STATE (Lon ruling s29): THE ERADICATION IS *COMPLETE*, NOT ABANDONED. FROM HERE THE WORK IS PURELY ADDITIVE.**
Lon, verbatim in substance: *"We are not going to have RBP around PATTERN BLOBS, so I suppose we already have eradicated all we need. From here we are adding RBP at ALL the RIGHT SPOTS."*
- **THE DELETE ALREADY LANDED.** `1af93e3a` (DEL-T1 D-1) removed BLOB-GRANT frame establishment for PAT$ blobs and is **live on main, unreverted** (bisect-confirmed; the "the delete was reverted" claim in older cursors is FALSE for mainline). **Pattern blobs have no RBP today.** That was the whole target. **T1/T2 are DISCHARGED BY EXECUTION.**
- ⇒ **NO RUNG BELOW MAY DELETE A FRAME AS ITS PURPOSE.** Deleting is over. Every remaining rung either ADDS a frame where the predicate says one is OWED, or moves WHO writes it (glue → α/ω).
- ⇒ **THE CENSUS IS NOW ASYMMETRIC AND `OWED` IS THE LIVE NUMBER.** `unearned` should already be at or near zero for the blob class — the deletion took it there. **The debt is `owed`: nodes the predicate says need a frame and have none.** A seat that opens EARN-2 expecting two comparable columns will mis-read the board.
- ⭐⭐⭐ **AND THIS EXPLAINS THE CURRENT DEFECT CLASS.** After eradication and before addition, the tree is in the state EARN predicts: **frames removed, frames not yet re-added, so every construct that NEEDS one is running without one.** s29's measured divergences are exactly that symptom — `ARBNO(*cmd)` cannot span `'aa'`; stored composites hang or SEGV; FENCE1 borrows a parent rbp it does not own. **These are not miscellaneous bugs to be triaged; they are the OWED column, observed at runtime.** Treat a repair of any of them as evidence about the predicate, not just a bug fix.

## ⛔⭐⭐⭐ SCOPE — SPLIT EXECUTED s40 (Lon in-chat: "Split it if you think it should… I'm with you on this")

**THIS FILE'S SUBJECT IS THE DEFER BOUNDARY:** the EARN frame predicate AND the `MATCH_DEFER` control-flow/runtime defects are one surface (EARN Rule 1 names the frame owner as the operator holding a cell across a `*P` defer; s39's fixed defect sat on exactly that boundary). **BILLS HERE:** EARN rungs, every `earn0_*` witness, defer-adjacent crashes (stored_varref runtime half, blob_hang, the fence_fn/*FN residual-11 cluster), PT-2 Defect B (stored-pattern semantics = EARN-0's own law). **ROUTED OUT s40, pointers landed in the receiving files:** `treebank-array` → `GOAL-MODE34-IDENTICAL.md` · duplicate-label class + BUILDFAIL-4 → `GOAL-SN4-HOME-BOARD.md`. **CURSOR HISTORY s14–s32 → `archive/ARCHIVE-RBP-EARN-CURSOR-HISTORY.md`** (nothing deleted; rulings therein remain binding). File: 1245→~700 lines.

**⭐⭐⭐ LIFTED FROM ARCHIVED CURSORS — STILL LIVE, DO NOT RE-DERIVE:**
- **RULING (a) s30, as STRUCK by s30b (both Lon in-chat, verbatim in archive):** pendings ride the **r12-topped mmap'd arena** — "Capture pending are in their own MMAP'd R12-topped arena. What is the problem there?" — stack-disciplined, match-scoped, NOT the heap the SPINE ruling avoids. Sub-arms (1)/(2) DEAD. **Arena still OWES, W-pinned: (i) VERIFY r12 restored at every backtrack re-entry class (W5) — do not assume; (ii) arena records GC-visible if holding DESCR refs (→ GOAL-SN4-HOME-RBX X-1); (iii) ONE-AUTHORITY reconciliation between the two capture arms (EARN-5's job, CAP-SYM s22m precedent).**
- **W1–W5 ORACLE PINS** = acceptance for ANY pending/capture change: the five `probe/earn0/earn0_pend_*` witnesses with baked refs (survive-FENCE-seal · blocked-on-fail · left-of-FENCE survives · chronological-last-wins · dies-on-backtrack). Two opposite lifetimes on one spine.
- **(b)/(c)/(d) of s30 remain OPEN** at zero cost (taxonomy label / legacy-ARBNO-arm sequencing / EARN-8 parked).
- **s29 OPEN QUEUE:** (1) re-grade `119/129/148/149` — s22's "4 REPAIRED" is **UNWITNESSED** (failure-asserting tests can't witness a repair whose failure mode is also failure); (2) discriminating `.ref` lines for the 10 unclearable success-shaped programs (corpus-only, cheap); (3) Defect B still has no default-arm reproducer — record one when A lands; (4) `earn0_disc_arbno_star_fence_positive` remains the best monitor target (terminating wrong-answer, proven separating control); (5) house-guards worth adopting: success-expecting controls are vacuous until arithmetic shown to separate · every BY-SET board carries a known-PASS control row, a run where it fails is VOID.

## ⚙️ CONCURRENT BY DEFAULT — AND THE REPOS MOVE UNDER YOU

**Many seats run this file's siblings at the same time. Edit any file, commit and push whenever a rung is buildable and green — mid-session, per rung. Never park work or decline an edit on concurrency grounds; stranding has cost this project far more than merging ever has.** Git merges; `git pull --rebase` and resolve normally.

**⛔ ASSUME ORIGIN MOVED SINCE YOU LAST LOOKED.** Another seat may have landed in your exact files while you were reading them.
- `git pull --rebase` before every push; **re-prove THIS file's gate/watermark after any rebase** — shared state moves under you and a watermark measured pre-rebase is void.
- `git log origin/main..HEAD` at orientation AND before handoff. **A clean `git status` is NOT a clean tree** — it hides local commits a peer seat left in a shared working copy.
- Place trees at canonical absolute paths (`/home/claude/{SCRIP,corpus,.github,x64}`) BEFORE running any gate: **many scripts grade a tree by absolute path.**
- Prefer **one clone per seat**; two seats in one working copy silently overwrite each other's uncommitted edits, and a global gitconfig scrambles attribution.
- Push **code repos before `.github`**, so no FINDING ever describes an unpushed tree.
- Push needs a credential — **ask Lon in chat and wait.** Never write push status into a doc.
- `bash scripts/handoff_status.sh` verbatim is the ONLY push truth. Not this file, not a commit message.

**Semantic collisions (two seats claiming one register) are caught MECHANICALLY by the claim gates, not by scheduling.** That is why no window is needed.

## DESIGN OF RECORD

- ⛔⭐⭐⭐ **SUPERSEDED s29 (Lon ruling): EXACTLY *TWO* GLUE KINDS — FRAMED IS NOT A GLUE KIND.** **ONE-SHOT** (`add rsp,K; jmp pred_β`) · **PASS-THRU** (transfer box adopts caller wires, ZERO frame). ⭐ **The wires are R10 (γ) and R11 (ω)** — the old rcx/rdx spelling is REPLACED, not paralleled, one product-wide convention (a per-kind split is the mixed regime ZW16 convicted). ⛔ **RBP establishment is NOT glue work.** It lives in **`x86_alpha`/`x86_omega`** (or the equivalent parameterized template form), keyed on the EARN predicate staged at plan time. **Glue moves control and carries wires; α/ω establishes and releases the frame. Two concerns, never re-merged.** *(Historical: this line formerly read "exactly three glue kinds … FRAMED (`bb_glue_framed_enter/leave`, THE ONLY RBP WRITER)" — kept for provenance because several rungs below still cite the three-kind form.)*
- **Licensed frame census** = **{STATEMENT · FUNCTION · MATCH_BEGIN · FENCE1}** (ARBNO-LON refinement, 08-06; FUNCTION = the AB activation frame, Lon verbatim confirm: the manual p.103 pushdown made literal).  **Every other RBP establishment in the product is a deletion target.**  ⛔⭐⭐⭐ **SUPERSEDED BY LADDER RBP-EARN (Lon ruling, s25, in-chat): THE LICENSE SET IS NO LONGER AN ENUMERATION — IT IS DERIVED FROM A PREDICATE.**  The four names above are now an OUTPUT to be re-checked, not an input; EARN-0 re-derives them and STATEMENT/FUNCTION are both expected to lose their licenses on the predicate.  Read LADDER RBP-EARN before treating any name in this line as settled.
- **The site side is already correct** (ZD-PATREF, emit.cpp:1935): `bb_match_defer` enters pattern blobs via `bb_glue_pass_wires`, K=0 transfer citizen.  The debt is **blob-side**: `emit_jmp_entry_for_patproc` (emit.cpp:2914/2925) routes every PAT$ blob onto BLOB-GRANT (emit.cpp:2362 — `sub rsp,kt` + wire adoption + **rbp pin**, kt=(48+jcon_value_region+15)&~15; claws5-match: 304) with the CLASS D exit protocol (γ {res,rbp} resume record, scanfail retry `mov rsp,rbp`, ω absolute unwind `lea rsp,[rbp+kt]`) and the legacy in-blob ARBNO per-iteration rbp rebase chain.
- **Statement-inline is the proof-of-possible**: the SAME constructs (ARBNO-LON frameless, ALT, SPAN/BREAK, captures) already run oracle-green in statement context under the licensed frames only.  An INVARIANT pattern's structure is compile-time known — its reference can therefore be pure wiring (pass-thru), its elements riding the statement regime, and the frame question evaporates for it.

## ⛔ HISTORICAL — THE CENSUS AS A DELETION LEDGER (the quantity below is the OLD one)

**⛔ This table counts FRAMES THAT EXIST, i.e. deletion progress. That question is CLOSED (see PHASE STATE at the top: the delete landed, blobs have no RBP). It is kept because EARN-2 must re-cut this exact instrument, and because the per-corpus shape is still the map of where frames live. ⛔ DO NOT open a rung against `frames == 0` — the live quantity is `owed`.**

## THE CENSUS (RE-MEASURED 2026-08-10 s7 at corpus `fa761d0` / SCRIP `23189c2` post-regen-×3; Σest **557** — s6's 618 and the 609 seed both OBSOLETE: demo MAIN 93→40 and bench MAIN 20→12 dropped via parallel frame-deletion landings between the s6 measurement and origin HEAD, direction consistent with the goal; instrument = `SCRIP/scripts/test_census_rbp_frames.sh`; `push rbp` inside PAT-BLOB regions includes CLASS D γ resume-record pushes — protocol shape, not establishment, dies with the blob; crosscheck/patterns regen cadence AUDITED s27: 122/122 census-unchanged vs live compiler — caveat lifted; expires on first frame-moving rung)

| corpus (.s) | files | blob-bearing | PAT$ blobs | est `mov rbp,rsp` PAT-BLOB / MAIN / PROC | push rbp PAT-BLOB / MAIN |
|---|---|---|---|---|---|
| programs/snobol4/demo | 28 | 17 | **101** | **130** / 40 / 12 | 113 / 19 |
| benchmarks/snobol4 | 23 | 6 | 8 | 2 / 12 / 3 | 8 / 7 |
| crosscheck/patterns | 122 | 57 | **130** | **93** / 265 / — | 139 / 178 |

Crosscheck-318 instruction baseline (STF-UNFLIP, measured then): **15,459 rbp instructions across 127 programs = the flat_pat/flat_gen WHOLE-GRAPH PIN debt** — "not a statement bracket — do not confuse the two."

## ⛔ DISCHARGED / HISTORICAL — THE DELETION-TARGET LIST

**⛔ T1 and T2 are DISCHARGED BY EXECUTION** (`1af93e3a` live on main; pattern blobs carry no RBP). **T3/T4/T5 are retired as deletion targets** — under EARN a frame is not debt; an UNEARNED one is, and `unearned` is already near zero for these classes. ⭐ **The KEEPERS list at the bottom is still useful, but inverted in meaning:** those constructs are no longer "licensed exceptions to deletion" — they are the first candidates to be re-checked against the predicate for whether they are OWED a frame. Read accordingly.

## THE DELETION-TARGET LIST (creators; keepers named so nobody re-litigates them)

- **T1 ⛔⭐ BLOB-GRANT frames on INVARIANT-pattern blobs** (Lon's named first target).  Dies with it: SCANBASE rbp reads (kt-32/kt-40), scanfail retry whack, CLASS D γ {res,rbp} record + `pop rbp` res stub + ω absolute unwind (emit.cpp:2742-2796), in-blob legacy ARBNO rbp rebasing.
- **T2** Same blobs reached via `*name` (the defer fast arm is the SOLE flat_pat entry — bare refs die at PT-1/2, star refs at PT-3).
- **T3** Invariant SEGMENT blobs referenced by variant stitch structures (PB) — same BLOB-GRANT frame.
- **T4** `flat_gen` whole-graph pin (generators; product-wide Icon/Prolog) — MECH M-2 routing; tracked here, executed where Lon routes.
- **T5** GLUE-O residual pins on `emit_rec_pin()` mains (the !rec_pin majority already suppressed — s26b census 464→252 push_rbp; remainder = data-reader mains; FB-STMT refinement path).
- **KEEPERS (licensed, never targets):** AB activation frames (`*_act_*`) · MATCH_BEGIN statement head · FENCE1 seal · STATEMENT bracket · Icon zframe/flat_lcl_proc (FUNCTION-class) · CLASS C ambient-rbp whack (a CONSUMER of the C frame, not a creator — the 1016_eval return-to-C mechanism, s22u falsification on record).

## ⛔⭐⭐⭐ EARN DESIGN OF RECORD — s28 CONSOLIDATED (Lon in-chat) — **SUPERSEDES: crossing row 3, s25's consequence (1), the two-class taxonomy, and this seat's own ruling-(2) gloss**

### THE LAW — UNCHANGED, AND NOW THE WHOLE DESIGN
> **A cell needs a frame ⟺ the byte distance between that cell and RSP is not a compile-time constant at some site that reads it.**

### ⭐⭐⭐ ARBNO — ONE FRAME AT α. THE CELL HANGS OFF RBP. β READS THROUGH IT.
**Lon, verbatim:** *"On ARBNO you would not setup another RBP at BETA, you would use RBP to access ARBNO's RESULT or LOCAL."* and *"If ARBNO need a LOCAL or RESULT it hang off of RBP. What else do you need. It can be a counter or delta cursor, whatever."*

- **ENTER once, at α.** β is the SAME activation — the frame is already live. β reaches ARBNO's cell at `[rbp+K]` and the anchor at `[rbp+ANCHOR]`. **`push rbp` at β would be a second establishment for one activation.**
- **ARBNO earns for OFFSET reasons** — identical mechanism to FENCE1's commit whack and to any operator holding a cell across `*P`. **It is not a special case and needs no special machinery.**
- **WHY THE OFFSET IS CONSTANT — the point everything else was obscuring:** a cell addressed off `rbp` is immune to whatever P does to the spine beneath it. **P's growth stops mattering entirely.** That is the whole reason the frame is the fix, and it is why the `[rsp+0]`/`[rsp+4]` cursor — whose offset assumed a frontier that moves — dies.
- ⛔ **CROSSING ROW 3 IS DELETED, NOT AMENDED.** *"ENTER at a port that is not α"* describes no crossing that exists. The crossing table is **THREE rows**: anchor drain (ABORT/FENCE-backup/total failure) · unanchored retry · heap-frame/generators (addressing, per s28 ruling (0)).
- ⛔ **s25's CONSEQUENCE (1) IS FALSIFIED.** It read *"ARBNO's counter dies — if ARBNO ENTERs per iteration, the frame chain IS the counter."* **There is no chain and the counter does not die** — it LIVES, in the frame, at a fixed offset, and Lon names it explicitly (*"a counter or delta cursor, whatever"*). What dies is the `[rsp+…]` **addressing** of it, not the datum.

### ⭐⭐ ONE HAZARD CLASS, NOT TWO (⛔ DERIVED BY THIS SEAT FROM RULING (2) — NOT A LON RULING; CORRECT IT IF WRONG)
The taxonomy split OPAQUE (unknown SIZE) from UNBOUNDED (unknown COUNT). **ARBNO was UNBOUNDED's only SNOBOL4 source, and it is not one** — it earns for offset, like everything else. The remaining named source, *"true recursion through a deferred self-reference"*, is `*P` — i.e. OPAQUE.
**And from the addressing side the split never bought anything:** a reader does not care whether the unknown bytes between it and rsp are one record of unknown size or N records of known size. **Unknown count is a SOURCE of unknown size, not a second kind of hazard, and the remedy is identical.**
⇒ **ONE CLASS: something of unknown size can sit between the cell and rsp.** Manual anchor unchanged (p.122 — only `*` defers). ⛔ **EARN-0's table keeps its verdicts; only the HAZARD column's two-way label collapses to one.** ⛔ Stack overflow on deep recursion remains oracle behaviour (p.123, `-s`) — a RESOURCE fact, never an addressing one, and it never selected a frame.

### ⭐⭐ THE EMISSION — HIDDEN IN α/ω, DYNAMICALLY SWITCHABLE (Lon's proposal, endorsed with one correction)
- **Gate on a value staged at plan time** by `frame_need_of` (EARN-1), read at the authority, never re-derived in the template — the `cap_anchor_of`/`op_cap_anchor` precedent (`emit.cpp:812`). Default-off makes EARN-1's *"emitted bytes byte-identical to HEAD"* gate trivially provable.
- ⛔⭐⭐⭐ **AMENDED s29 (Lon ruling): THE FRAME BELONGS TO `x86_alpha`/`x86_omega`, NOT TO GLUE.** α/ω is the parameterized template form that establishes and releases the frame, keyed on the staged `frame_need_of` value. **It is THE ONLY RBP WRITER** — that property transfers from `bb_glue_framed_*` to α/ω. ⛔ Whether α/ω calls a shared `_enter`/`_leave` primitive or inlines the dance is an IMPLEMENTATION choice; **what is non-negotiable is ONE authority for the bytes and ONE for the decision.** A second RBP writer anywhere — glue, template, or runtime — is the defect class this goal exists to prevent. ⭐ Because α/ω are language-agnostic, this lands product-wide: Icon `zframe`, Prolog, and `flat_gen` inherit the discipline free.
- **γ EMITS NOTHING.** That IS the LIFO theorem. The α/ω asymmetry — enter at α, leave only on the failure/exhaust edge — is CORRECT, not an oversight; say so in the code, because it reads as a missing bracket to anyone expecting symmetry.
- **TWO SITES ESCAPE α/ω and stay explicitly callable:** **FENCE1's LEAVE** (fires at a chosen PAIR *before* `fence_whack_commit`, not at ω — hardcoding leave-at-ω breaks an ordering already debugged once) and **the ANCHOR DRAINS** (ABORT, unanchored retry — they jump out from arbitrary depth). ⛔ ARBNO's β is **no longer** in this list.
- ⛔ **TRANSITION HAZARD:** between EARN-1 and EARN-7 the old pins are still live (MATCH_BEGIN HEAD-PIN, BLOB-GRANT). A strictly **per-node** staged gate avoids double establishment; EARN-7 deletes the old regime and only then may the gate go unconditional.
- ⭐ **SCOPE NOTE:** `x86_alpha`/`x86_omega` are language-agnostic, so this lands product-wide — Icon `zframe`, Prolog, T4 `flat_gen` inherit the discipline free. **Either a large win or a blast radius wider than EARN-4 scopes.** Decide deliberately.

### ⛔ THREE ERRORS BY THIS SEAT ON ONE POINT, RECORDED BECAUSE THEY WERE ALL THE SAME ERROR
(1) *"emit ENTER at β as well as α"* — inherited from crossing row 3 and repeated in the s28 ruling-(2) gloss. (2) *"a chain of carves below it"* — offered as the correction to (1). (3) Defending the UNBOUNDED class after its only member had dissolved. **All three invented per-instance structure that nothing requires.** The frame IS the fixed point; that is the entire mechanism. ⛔ **A seat reading ruling (2)'s "TWO instances" as two ESTABLISHMENTS will rebuild all three errors** — "two" was never about establishment.

### EARN-4, RESTATED UNDER THIS DESIGN
DELETE the `sub rsp,16` carve and every `[rsp+0]`/`[rsp+4]` cursor access. Rebuild as: **ONE frame at α; ARBNO's control datum (counter / delta cursor / result / local) at a fixed `[rbp+K]`; β reads through it; exhaustion read from the cell.** Whatever P leaves live beneath is P's own nodes' business, governed by the same law applied to them — **recursive application of one rule, not a second rule.** Gate unchanged: `arb1.sno` T1 **and** T2 oracle-green, N22–N33 + probe `181`, `board_patterns_set.sh` BY SET watching the BROKEN set.

## ⛔⭐⭐⭐ LON RULINGS — 2026-08-11 s28 (in-chat) — **THE CROSSING TABLE LOSES A ROW, FENCE1's EDGE WAS MISCLASSIFIED BY s27, AND ARBNO's "TWO" IS α AND β**

**⭐⭐⭐ RULING (0) — EARN-0b's HEAP-FRAME ROW IS CLOSED AS "GOOD ENOUGH", ON PRIOR ART.** Lon: *"We have ZETA FRAMES completely working LIFO in the past, so that proves a lot. I remember that ONLY CO-EXPRESSIONS were not LIFO, and they get their own thread."*
⇒ **THE FOURTH CROSSING NARROWS AND PARTLY DISSOLVES.** As written the row named three things — *resumable callables, generators, `flat_gen`*. Under this ruling they split:
- **CO-EXPRESSIONS LEAVE THE TABLE ENTIRELY.** Own thread ⇒ own stack ⇒ **LIFO holds per-stack, trivially.** A separate spine is not a non-LIFO spine. They were never a counterexample to the theorem; they were a second instance of it.
- **GENERATORS KEEP LIFO *ORDERING*** — a suspended generator's frame stays put and nothing is freed out of order; the consumer's frames simply sit above it. What they break is not the ordering but *"γ and β are free"*: the resumer must **address** a frame it did not create, so the base travels in the wire. That is the `{res,rbp}` record surviving **BY NEED**, exactly as the row already said — but for the addressing reason, **not** a lifetime reason.
⇒ **EARN-0b IS DISCHARGED FOR LADDER PURPOSES.** MON-RE on `c_rt_gen_spine_resume_enter` is no longer a blocker; it becomes generator-row hygiene whenever T4/`flat_gen` is actually worked. **Do not re-open EARN-0b to chase the dark instrument.**

**⭐⭐ RULING (1) — THE OWNER IS THE OPERATOR HOLDING A CELL ACROSS A `*P` DEFER.** Lon: *"The main problem is always the operator who has a *P DEFER as an operand."* **This is EARN Rule 1 restated by its author and it is the whole of EARN-5.** `*P` owns nothing; the frame belongs to whoever must read a cell after `*P` has run. Confirms the table's `DEFER`/`VALUE` = **NEVER (owns nothing)** rows and the `ASSIGN_SAVE` = **IFF-OPAQUE-SIBLING** row.

**⭐⭐ RULING (2) — ARBNO's "TWO INSTANCES" ARE THE TWO *ENTER SITES*, α AND β.** Lon: *"ARBNO always are the TWO instances needing RBP for offset reasons."* Read against crossing-table row 3 (*"ENTER at a port that is not α — ARBNO begins a NEW ACTIVATION at β — emit ENTER at β as well as α"*): ARBNO ENTERs at **α** (first instance) and again at **β** (every retry = a new activation). ⇒ ⛔ **SUPERSEDED s28 — SEE EARN DESIGN OF RECORD ABOVE: ONE ENTER AT α; β READS THROUGH THE LIVE FRAME. "Two" was never about establishment.** And per EARN consequence (1) the frame chain then **IS** the counter — which deletes the `[rsp+0]`/`[rsp+4]` cursor, i.e. **the exact machinery s26 convicted for the exhaustion SEGV** (32-bit cursor write landing on the upper half of a 64-bit resume slot). ⛔ If a seat reads "two" as "two frames total", the per-iteration chain is lost and with it the counter deletion.

**⛔⭐⭐⭐ RULING (3) + CORRECTION TO s27's TABLE — FENCE1's READING EDGE WAS WRONG, AND THE ERROR FLIPPED ITS JUSTIFICATION.** Lon: *"FENCE1 needs an RBP for WHACK on GAMMA reasons."*
**s27's table recorded FENCE1's edge as FAILURE. That is wrong.** The whack is `fence_whack_commit` — it fires on **COMMIT, i.e. P SUCCEEDED (γ)**, discarding P's alternatives by restoring the watermark (`bb_match_fence1.cpp:79/98-101`; the paired `framed_leave` runs *before* the whack). Under the s25 sharpening — **success-edge reads EARN, failure-edge reads do not** — s27 had FENCE1 on the *exempting* side of the rule and still reached the right verdict by the wrong route. **Corrected: FENCE1's read is on the SUCCESS edge and it earns for that reason.**
⭐ **THE ARGUMENT IS SELF-CONTAINED AND WORTH KEEPING:** the commit must restore a watermark whose distance from current rsp **is exactly P's growth — the unknown being measured.** You cannot address the watermark with the quantity it stores. Hence rbp. This holds whenever P's growth is not compile-time constant, which is EARN-6's condition unchanged.

**⛔ HYPOTHESIS RAISED AND FALSIFIED IN THE SAME BREATH — DO NOT INHERIT IT.** Answering ruling (3) I proposed a **THIRD hazard source**: alternation arms of unequal static depth would make a post-ALT exit depth runtime-variable even with zero OPAQUE/UNBOUNDED material, which would have pushed FENCE1 from IFF toward ALWAYS **and added a column to EARN-0's table.** **It is FALSE BY DESIGN.** `bb_match_alternate.cpp:13-14`: *"the ALT's own frontier and nodes after the ALT sit at the SAME static depth for every arm. No pad, no per-arm exact footprints, no uniform-depth stubs. 'Fixed offsets all the way down the graph.'"* ⇒ **ALT normalizes depth, so there is no third hazard class; the two-class taxonomy (OPAQUE · UNBOUNDED) is complete, and FENCE1 stays IFF-OPAQUE-SIBLING rather than ALWAYS.** Checked before it was written down, at a cost of one grep.

**⭐⭐ RULING (4) — ALTERNATE DOES NOT PAD, AND THE ZERO-FOOTPRINT PROPERTY IS A LIVE COUPLING TO EARN-4/5.** Lon asked whether ALT pads arms to fixed length (*"If so that is WRONG!"*). **It does not.** `ZB-FC-3a` pad-to-max was DELETED at s202 (`bb_match_alternate.cpp:9-14`). Uniform depth comes from arms carving **NOTHING**: every node inside a granted ALT's arms **declines its FORTH cell** (`fc_arm_member`, `zeta_storage.c`) and keeps a flat zls quad, so **an arm's rsp footprint is 0** and every arm yields at the ALT's own frontier. *"No pad, no per-arm exact footprints, no uniform-depth stubs."*

**⇒ ALT IS NOT A HAZARD TODAY, AND IF IT EVER BECOMES ONE IT STILL DOES NOT GET THE FRAME.** Lon, verbatim in substance: *"ONLY if ALTERNATE is an operand to another operator then that operator gets the RBP just like the others."* **Correct, and it is Rule 1 again:** unequal arm footprints would be an unknown-**SIZE** hazard — OPAQUE class, the same class as `*P` — and the hazard **owns nothing**. The operator holding a cell live across the ALT earns the frame. ALT's own row stays **NEVER** in both regimes: today because it produces no hazard, and in the hypothetical because a producer is never an owner.

**⛔⭐ THE COUPLING, FLAGGED BEFORE IT BITES:** zero-footprint arms are the **exact opposite** of EARN's Rule 3 (*"operands are RSP-relative, frames become MANY and TINY"*). The arms are flat precisely *because* they decline cells. **If EARN-4/EARN-5 gives arm-interior nodes per-activation cells — which recursion correctness may demand — the zero-footprint property DIES and ALT begins producing the OPAQUE hazard for real.** At that moment every operator reading a cell across an alternation earns a frame, and EARN-0's table gains rows it does not have today. ⇒ **Any rung that makes arm-interior nodes carve MUST re-run EARN-0's ALT row and the `$`/`.`-across-ALT rows in the same commit.** Not a defect today; a tripwire for the rung that changes it.

**NET EFFECT ON THE LADDER:** EARN-0b closed(0) · EARN-5's owner rule confirmed(1) · EARN-4 gains its emission shape — ENTER at α **and** β, chain-as-counter(2) · EARN-6's FENCE1 row keeps its verdict with a corrected justification(3) · the hazard taxonomy is confirmed COMPLETE at two classes. **Rulings (a)/ROOTSPINE remain OPEN — Lon: "Unsure."**

## ⛔⭐⭐⭐ FIX PLAN — s38 (Claude Sonnet 5, 2026-08-12) — STABILIZE THE FLOOR BEFORE TOUCHING THE EARN LADDER

**The problem in one sentence:** the EARN ladder cannot be honestly measured while the tree crashes on the very constructs the predicate must evaluate. Every seat arriving here spends its budget on crash triage rather than EARN, and leaves believing it made no progress. **This block turns that into a sequential fix plan with a done condition for each step.**

---

### ⛔ STEP 0 — **FALSIFIED s39. DO NOT RUN THE COMMANDS BELOW AS WRITTEN.**

**⛔⭐ s39 VERDICT: the defect described in this step does not exist at HEAD.** `SCRIP_PAT_INLINE=0 ./scrip --dump-ir earn0_stored_varref.sno | grep "ASSIGN var"` returns nothing in EITHER arm — not because the ASSIGN is elided, but because the grep pattern itself is wrong (the dump spells it `ASSIGN                 [3] var="P"`, so the anchor must be `'ASSIGN.*var="P"'`). With the corrected grep the ASSIGN is **PRESENT IN BOTH ARMS**. There is no elision to fix. The real defect behind `earn0_stored_varref` was re-derived MONITOR-FIRST and is recorded in the s39 LIVE CURSOR at the top of this file; a lowerer half is fixed (`ca04abf2`) and a runtime half remains open.

**⭐⭐⭐ THE GENERALIZABLE LESSON — THIS IS WHY THE STEP WENT STALE, AND IT WILL RECUR:** this step baked **expected outputs** into its instructions (*"expect: present (1 line). Without the flag: absent (0 lines). That is the defect."*). Under CONCURRENT-BY-DEFAULT the tree moves faster than prose can track, so a baked expectation is a **trap that looks like authority**: a seat runs it, sees the expectation fail, and cannot tell whether it found a new bug, the tree moved, or the instruction was always wrong. s39 lost a meaningful slice of budget to exactly that ambiguity before abandoning the step. ⇒ **RECOMMENDED FORMAT CHANGE for every future FIX PLAN in this file: state the QUESTION and the INSTRUMENT, never the expected answer.** *"Does the ASSIGN reach IR? Instrument: `--dump-ir | grep 'ASSIGN.*var=\"P\"'`, compare both `SCRIP_PAT_INLINE` arms"* stays true forever; *"expect 1 line / 0 lines"* rots in one session and actively misleads while it rots.

<details><summary>ORIGINAL s38 STEP 0 TEXT (retained for provenance only — commands are stale)</summary>

**What:** `P = LEN(1)` then `Q = P LEN(2)` then `'abc' Q` crashes or hangs. The assignment to `P` is never emitted into IR when the later use is via a stored-pattern blob path. Already convicted: it is in `lower_snobol4.c`, `SCRIP_PAT_INLINE` is the knob, the optimizer is exonerated.</details>

**Exact steps:**
```bash
# 1. Reproduce the conviction
SCRIP_PAT_INLINE=0 ./scrip --dump-ir /home/claude/corpus/probe/earn0/earn0_stored_varref.sno 2>&1 | grep "ASSIGN var"
# expect: present (1 line). Without the flag: absent (0 lines). That is the defect.

# 2. Find the decision site
grep -n "pat_inline\|PAT_INLINE\|pat_static\|SNO.MKPAT" src/lower/lower_snobol4.c | head -20
# The line that elides the ASSIGN when the consumer is a blob-path use is the one to fix.

# 3. Fix: the ASSIGN must be emitted regardless of how the RHS variable is consumed downstream.
#    Lower does not yet know whether the consumer will be a blob or a BINOP — that is decided
#    by the later statement, not the current one. The elision is premature.

# 4. Gate: run the earn0 probe suite
for f in /home/claude/corpus/probe/earn0/earn0_stored_*.sno \
          /home/claude/corpus/probe/earn0/earn0_varref_*.sno; do
  expected=$(cat "${f%.sno}.ref" 2>/dev/null)
  got=$(timeout 10 ./scrip --run "$f" < /dev/null 2>/dev/null)
  [ "$expected" = "$got" ] && echo "PASS $(basename $f)" || echo "FAIL $(basename $f)"
done

# 5. Done condition: every earn0_stored_* and earn0_varref_* probe exits 0 with oracle-matching output.
#    setarch $(uname -m) -R before each run to eliminate ASLR nondeterminism during testing.
```

**Files to touch:** `src/lower/lower_snobol4.c` only. If the fix requires touching `src/optimizer/`, re-examine — the optimizer is already exonerated, any optimizer-side fix is treating a symptom.

---

### STEP 1 — OWN THE RESIDUAL-11 m4-ONLY CRASHES IN crosscheck/patterns

**What:** 11 programs in `crosscheck/patterns` exit m4 SEGV while m3 is 0 — a MODE34-IDENTICAL violation. Named cluster: `063/064/065/066_pat_fence_fn_*`, `156_pat_cap_alt_abandon_pop`, `157_pat_cap_arb_alt_keep`, `141_pat_eval_double_fn_arbno`, `121_pat_calc_op_dispatch`, `064_replace_multi_arm`, `154_pat_construction_time_hoist`, + `treebank-array`. The hypothesis (s34) is that `*FN` inside a FENCE makes P's growth non-constant — the EARN predicate firing. **That is a name-cluster hypothesis, not a measurement.**

**Exact steps:**
```bash
# 1. Get the current list with fresh eyes
bash scripts/test_census_m3_m4_divergence.sh \
  /home/claude/corpus/crosscheck/patterns /tmp/residual11.tsv
awk -F'\t' '$3=="<SEGV>" && $4==0 {print $1}' /tmp/residual11.tsv

# 2. Pick the simplest failing program (shortest source, fewest constructs).
#    Diff its mode-3 vs mode-4 emitted assembly to find the first structural difference:
PROG=<chosen>
./scrip --compile /home/claude/corpus/crosscheck/patterns/$PROG.sno > /tmp/m4_$PROG.s
# mode-3 has no .s artifact — use --dump-ir as a proxy, or instrument with SCRIP_BLOB_MAP=1
# Compare the blob layout in m3 (binary) vs m4 (text) for the first differing construct.

# 3. MONITOR-FIRST: run the 2-way sync-step monitor against SPITBOL for the chosen program.
bash scripts/test_monitor_2way_sync_step_bin.sh \
  /home/claude/corpus/crosscheck/patterns/$PROG.sno
# First divergent trace event names the construct. The bug lives between that event
# and the previous agreeing one. That is the ONLY valid entry point — no code reading first.

# 4. Done condition: census returns PURE m4-only crash class = 0.
#    Run census twice back-to-back and diff — the instrument is byte-stable (measured s35).
```

**Do not assume the fence_fn_* hypothesis is correct.** Verify from the monitor trace before opening any template.

---

### STEP 2 — FIX treebank-array m4 SEGV

**What:** `corpus/programs/snobol4/demo/treebank-array.sno` exits m4 SEGV, m3 clean. Unmoved since at least s32. Separate from the r9/Site-A class (confirmed this session: the main_α fix did not touch it).

**Exact steps:**
```bash
# 1. Confirm it is still broken at current HEAD
setarch $(uname -m) -R \
  ./scrip --compile /home/claude/corpus/programs/snobol4/demo/treebank-array.sno \
  > /tmp/ta.s 2>/dev/null
gcc -no-pie /tmp/ta.s -Lout -lscrip_rt -lm -Wl,-rpath,$(pwd)/out -o /tmp/ta.prog
setarch $(uname -m) -R timeout 15 /tmp/ta.prog < /dev/null; echo "rc=$?"
# expect: rc=139

# 2. Diff its .s against the m3 blob layout via SCRIP_BLOB_MAP=1 --run
SCRIP_BLOB_MAP=1 setarch $(uname -m) -R \
  ./scrip --run /home/claude/corpus/programs/snobol4/demo/treebank-array.sno \
  < /dev/null > /dev/null 2>/tmp/ta_blobmap.txt
cat /tmp/ta_blobmap.txt | head -30

# 3. Nearest passing sibling: treebank-list runs clean in both modes.
#    diff the two programs' --dump-ir output to find the construct class that differs.
diff <(./scrip --dump-ir /home/claude/corpus/programs/snobol4/demo/treebank-list.sno 2>&1) \
     <(./scrip --dump-ir /home/claude/corpus/programs/snobol4/demo/treebank-array.sno 2>&1) \
  | head -40

# 4. MONITOR-FIRST: 2-way sync-step monitor on treebank-array.
bash scripts/test_monitor_2way_sync_step_bin.sh \
  /home/claude/corpus/programs/snobol4/demo/treebank-array.sno

# 5. Done condition: treebank-array exits 0, output matches .ref, both modes.
```

---

### STEP 3 — FIX THE DUPLICATE-LABEL AS-FAIL (porter.sno's .Lx generator)

**What:** `porter.sno` compiles to 93,370 lines of `.s` then fails assembly with 1 duplicate symbol (`.Lx3548_40`). The generator is `x86_internal_name()` in `x86_asm.h:736` — `".Lx" + _.x86_uid + "_" + n`. The expression-sno `.Lbynamefn` bug is **separate** and already owned by the BOARD seat (FINDING-2026-08-12h). Do not conflate them.

**Exact steps:**
```bash
# 1. Confirm porter's collision is the .Lx family, not .Lbynamefn
grep "already defined" /tmp/porter.aserr | head -5
# expect: .Lx#### lines, not .Lbynamefn lines

# 2. Find where g_m4_dense_nid interacts with g_flat_node_id
grep -rn "g_m4_dense_nid" src/ --include=*.c --include=*.cpp --include=*.h
# This flag is set to 1 at scrip.c:1335 immediately after g_flat_node_id=0.
# Read what it gates — if it remaps UIDs to a per-procedure compact range,
# two procedures with the same local node count will produce the same .Lx labels.

# 3. Hypothesis to test: does x86_begin() in TEXT mode branch on g_m4_dense_nid?
grep -n "dense_nid\|x86_begin" src/templates/x86_asm.h | head -20

# 4. If g_m4_dense_nid causes per-proc counter reset: fix by making x86_uid
#    draw from a global monotone counter in TEXT mode regardless of dense_nid.
#    The fix should be in x86_asm.h's x86_begin() or in whatever code g_m4_dense_nid gates.

# 5. Gate: porter.sno compiles and assembles without error.
cd /home/claude/corpus/programs/snobol4/demo
timeout 60 /home/claude/SCRIP/scrip --compile porter.sno > /tmp/porter2.s 2>/dev/null
gcc -c /tmp/porter2.s -o /tmp/porter2.o 2>/tmp/porter2.aserr \
  && echo "PASS: assembles clean" \
  || { echo "FAIL: $(wc -l < /tmp/porter2.aserr) errors"; head -5 /tmp/porter2.aserr; }

# 6. Done condition: zero assembler errors on porter.sno and expression.sno (with cwd=beauty_suite/).
#    Re-run demo regen afterward (util_regen_demo_s_artifacts.sh) and commit updated .s files.
```

**Note on expression.sno:** it has no `-I` flag in scrip's CLI — include resolution is CWD-relative. Compile as:
```bash
cd /home/claude/corpus/programs/snobol4/beauty_suite
/home/claude/SCRIP/scrip --compile \
  /home/claude/corpus/programs/snobol4/demo/expression.sno > /tmp/expression.s
```
Once porter's generator is fixed, retest expression — if it shares the same counter, one fix may close both.

---

### STEP 4 — ADD scrip.c TO THE REGEN TRIGGER LIST (4 PLACES)

**What:** `src/driver/scrip.c` calls `emit_textf()` directly and a one-line change there moves emitted bytes for every m4 SNOBOL4 program. The trigger list is currently missing it in all four places it appears.

**Exact steps:**
```bash
# Edit these four locations to add "src/driver/scrip.c" to the trigger list:
# 1. RULES.md step 4 line (currently: "emit.cpp, emit.h, src/templates/*.cpp, x86_asm.h, lower_snobol4.c")
# 2. scripts/util_regen_benchmark_s_artifacts.sh header comment
# 3. scripts/util_regen_feature_s_artifacts.sh header comment
# 4. scripts/util_regen_demo_s_artifacts.sh header comment
# No code changes — documentation only. Commit all four together.
```

**Longer-term:** four hand-synced copies of the same list is itself a defect vector. Consider a single `REGEN_TRIGGERS` variable sourced by all three scripts, with RULES.md pointing at it.

---

### STEP 5 — PRUNE THIS FILE AND RULE ON ITS SCOPE

**What:** 952 lines, 22 cursor entries where RULES says prune below the last ~3. Orientation cost is compounding — it consumed a significant fraction of the last two sessions before any work started.

**Exact steps:**
```bash
# 1. Prune: keep s35-s37 consolidated (this session's entry, line 132),
#    s34 (the r9 fix, still live context), and s33 (the build-order retraction,
#    needed to interpret s34). Archive everything below s33 into a comment or delete.
#    Target: <400 lines total, <=3 cursor entries visible.

# 2. Rule on scope (Lon): is crash-triage an explicit prerequisite spelled out here,
#    or does each crash item belong to its owning goal (SNOBOL4-BB, EARN, etc.)?
#    The file currently carries items it explicitly says "NOT ADOPTED BY GOAL-RBP-EARN"
#    for (EARN-0 stored-pattern) but then carries without that disclaimer for others
#    (residual-11, treebank-array, cap_imm_nret2). Consistency ruling needed.
```

---

### DONE CONDITION FOR THE WHOLE PLAN

```bash
# Run this after Steps 0-3 are complete. All lines should read PASS or AGREE:
bash scripts/test_census_m3_m4_divergence.sh \
  /home/claude/corpus/crosscheck/patterns /tmp/final_check.tsv
grep "DIVERGE=0\|PURE m4 CRASH CLASS = 0" /tmp/final_check.tsv || \
  awk -F'\t' '$3!==$4' /tmp/final_check.tsv

# And the earn0 probe suite:
for f in /home/claude/corpus/probe/earn0/earn0_stored_*.sno \
          /home/claude/corpus/probe/earn0/earn0_varref_*.sno; do
  setarch $(uname -m) -R timeout 10 /home/claude/SCRIP/scrip --run "$f" < /dev/null \
    > /tmp/got.txt 2>/dev/null
  diff -q "${f%.sno}.ref" /tmp/got.txt > /dev/null \
    && echo "PASS $(basename $f)" || echo "FAIL $(basename $f)"
done

# When both of the above are clean, EARN-0's predicate table can be hand-checked
# against a compiler that doesn't silently mangle what you're measuring.
# That is the entry condition for EARN-1.
```



**Fingerprint:** SCRIP `29fd4ad8` · corpus `3621fc4f` · `.github` this commit. Both builds ran AFTER `install_system_packages.sh` (verified, no exceptions). ⛔ **PUSH STATE AT WRITE TIME:** rebased onto moved origin (`.github` was 17 behind, SCRIP 7, corpus 4). **SCRIP and corpus rebased to ahead=0 — my regen commits were absorbed as identical (see §2); nothing to push there.** `.github` has 5 commits pending, credential requested in-chat per RULES 6b. `handoff_status.sh` is the only push truth — do not trust this line.

### 1. R-2 SETTLED — THE SITE-A GAP IS REAL, INDEPENDENT OF BUILD ORDER
Isolated `git worktree` at `52545cbf` (pre-fix, `grep -c rtcc_load_all` = 2) vs HEAD (post-fix, = 3), **both built after `install_system_packages.sh`**, identical corpus, identical unmodified census script. Only variable: the Site-A call.

| | AGREE | m4 SEGV | m4 HANG | PURE m4-only | m3 SEGV/HANG |
|---|---|---|---|---|---|
| HEAD (3 sites) | 111 | 39 | 5 | 10 | 28/6 |
| `52545cbf` (2 sites) | 68 | 82 | 4 | 52 | 28/6 |

m3 bit-identical across both (mode-3 never touches this bridge — an internal consistency check that nothing else drifted). Reproduces s34's own "(before)" numbers exactly. ⇒ **s33's retraction does not apply to Site A; removing that one call reproduces the entire gap. s34's fix is load-bearing.**

### 2. R-1 RULED YES (WITH EVIDENCE) — AND THE TRIGGER LIST HAS A STRUCTURAL HOLE
`src/driver/scrip.c` calls `emit_textf()` directly — it **is** an emission site, filed under `driver/` by directory convention only. One line there moved emitted bytes for every m4 SNOBOL4 program. Ran all three regens in RULES order: benchmark → corpus `af268e4d` (**23 files, 684+/661−**, genuinely stale); feature → SCRIP `29fd4ad8` (~40 files; one pre-existing `EMIT-FAIL` on `coverage/coverage_sno_nodes.s`, untouched by design, not new); demo → corpus `3621fc4f` (**20 files, 2336+/2316−**).

⛔ **PROPOSAL NEEDING A LON RULING:** add `src/driver/scrip.c` to the trigger list. **And note the list lives in FOUR places that must be hand-synced** — `RULES.md` step 4 plus each of the three regen scripts' header comments — and **all four are currently missing `scrip.c` identically.** That duplication is itself the defect vector; one source of truth would be better than four copies.

⭐⭐⭐ **DISCOVERED AT REBASE — MY REGEN COMMITS WERE ENTIRELY REDUNDANT AND GIT ABSORBED THEM.** A concurrent seat ran the same three regens and pushed first (`2913c6a4` feature, `019795bb` demo, `607481a2` benchmark). On `git pull --rebase` all THREE of my regen commits were **skipped as already-applied cherry-picks** — i.e. byte-identical output. **Two useful facts fall out:** (1) **regen is provably deterministic across seats and machines** — the scripts' idempotence claim is now measured, not asserted; (2) **two seats spent a session's regen budget on the same bytes.** Under CONCURRENT-BY-DEFAULT that will recur. Cheap mitigation for whoever cares: `git fetch && git log origin/main --oneline -5 -- '*.s'` before running regen ×3, and skip if a peer just did it.

### 3. R-3 CLOSED — IT IS NOT A NEW DEFECT
`cap_imm_nret2.sno` is `PAT1 = LEN(3) $ *STORE() 'X'` then `S PAT1` — a STORED pattern containing `$` capture. `probe/earn0/earn0_stored_capture.sno` is `Q = POS(0) LEN(1) $ V LEN(2) RPOS(0)` then `'abc' Q` — same shape, and its own file already records the identical symptom ("varies… 0/134/139"). **Isolated both arms to single-shot zero-loop reproducers: both crash on the FIRST match.** ⇒ corrects the standing assumption (s34's and mine) that this was iteration-dependent or specific to the `*STORE()` deferred arm. Neither is true. **Fold into EARN-0; it needs no standalone ownership.** ⛔ EARN-0 itself NOT advanced here — that thread is mid-bisection (stage-bisected to LOWER, `SCRIP_PAT_INLINE` implicated) and was deliberately not reopened.

### 4. NEW, UNOWNED: THE DEMO "BUILDFAIL 4" IS TWO UNRELATED PROBLEMS
- `claws5`, `json` — still AS-FAIL. Matches s34. Untouched.
- `expression`, `porter` — **were never r9 victims.** They are excluded from the demo regen set on SIZE grounds (Lon, 2026-07-26), whose comment states they "compile clean and assemble clean." **That is now FALSE:** `expression` → 346,857-line `.s`, **543 duplicate-symbol errors** (`.Lbynamefnzd####`); `porter` → 93,370-line `.s`, **1** (`.Lx3548_40`). Note `expression` needs cwd = `beauty_suite/` for include resolution — `scrip` has **no `-I` flag**.
- **TWO SEPARATE GENERATORS. ⛔ (a) IS NOT MINE — CONCURRENT SEAT GOT THERE FIRST AND WENT FURTHER.** **(a)** `.Lbynamefnzd####` (`expression`, 543 collisions): `bb_call.cpp:299,323` builds `".Lbynamefn" + _.nid`. **A BOARD seat independently found and filed this at `314fdb57` — `FINDING-2026-08-12h-…-ONE-DUPLICATE-LABEL-BUG-IS-BEHIND-ALL-SIX-M4-SKIPS.md`, which ties it to all six m4 SKIPs. Read theirs, not this line; my version claimed novelty it does not have.** ⭐ The convergence is itself evidence: two seats hit the same defect from unrelated directions within one day. **(b) STILL UNCLAIMED:** `.Lx3548_40` (`porter`, 1 collision) is a **DIFFERENT generator** — `x86_asm.h:736` `x86_internal_name()` = `".Lx" + _.x86_uid + "_" + n`, with `x86_uid` from global `g_flat_node_id` via `x86_begin()`. Their FINDING does not mention `.Lx`, `x86_internal_name`, `x86_uid`, `g_m4_dense_nid`, or `porter` (greped). `scrip.c:1334` resets the counter once, correctly scoped *before* the per-proc loop — but adjacent `g_m4_dense_nid = 1` (line 1335) is suggestively named for per-proc renumbering and **was not traced.** Next seat: `grep -rn g_m4_dense_nid` first; verify before fixing.
- `treebank-array` — **confirmed still m4 SEGV post-fix** (fresh binary, this session). Unmoved, separate from Site-A, unowned.

### 5. ⭐⭐⭐ METHODOLOGY — A SIXTH CONVICTION, AND IT IS THE *MIRROR* OF THE FIVE
This file convicts the vacuous-control class 5×: *"a control whose two arms predict the same output is not a control."* **I hit the inverse and nearly published it: two arms producing DIFFERENT symptoms are not necessarily two defects.** ARM A (plain `$ V`) showed heap-exhaustion abort; ARM B (`$ *STORE()`) showed SEGV; I read that as two mechanisms. **ASLR was the confound.** Under `setarch $(uname -m) -R` both are flatly `rc=139`, 5/5 and 5/5, with **identical crash register state** — `rbp` sane, `r9`/`r10`/`r11` sane, `rsp` = exactly `0x7fff00000000` (`0x7FFF << 32`, too structured to be organic drift; the write site was NOT traced).
⇒ **OPERATIONAL RULE, offered for adoption:** *before billing two symptoms to two causes, remove environmental nondeterminism and re-measure.* `setarch -R` is one cheap command and it collapsed a false 2-defect split into 1.

**⭐ INSTRUMENT STABILITY, MEASURED (not assumed):** `test_census_m3_m4_divergence.sh` run twice under identical conditions is **byte-identical** (122/122 rows). ⇒ the crosscheck corpus is NOT sampling the nondeterminism, so s34's numbers and §1's are sound. **But the `probe/earn0` witnesses ARE nondeterministic** (their own files say so). ⇒ **census = trust a single run; probe witness = do not.** Use `setarch -R` or N runs there.

### 6. ⛔ TWO SELF-INFLICTED ERRORS, BOTH CAUGHT AND REPAIRED THIS SESSION
1. **My s36 edit deleted s34's header line** (a `str_replace` that didn't re-append it), orphaning s34's body while `git status` stayed clean. Caught on a structure check before the next edit; repaired. **These headers are 300+ chars of bold/emoji and are fragile under `str_replace` — verify after every cursor edit with `grep -c '^## ⛔⭐⭐⭐ LIVE CURSOR\|^## ⭐⭐⭐ LIVE CURSOR'` (HEADERS ONLY = **22** at this commit; a bare `grep -c 'LIVE CURSOR'` returns 23 because this very sentence is a body mention — anchor the pattern or the canary lies to you).**
2. **My first s37 entry conflated `expression` and `porter` under one generator.** Falsified by checking porter's actual error string. Corrected in place — see §4, they are two.

### 7. ⛔⭐⭐⭐ SCRUTINY OF THE PLAN — THIS FILE HAS DRIFTED INTO BEING A DEFECT LEDGER, AND IT NEEDS A LON RULING
**The EARN ladder itself has barely moved in five sessions.** EARN-0 is partially discharged and blocked; EARN-1 not started; EARN-2 not opened. Meanwhile s33–s37 are almost entirely **crash triage**, and the biggest measured win of this whole stretch — §1's 42 repaired programs — **had nothing to do with the EARN predicate.** It was a missing register load on an entry bridge.

Look at what this file is now carrying without clear ownership: the residual-11 (attributed to "the EARN predicate firing" but explicitly flagged as *a hypothesis from a name cluster, not a measurement*), the BUILDFAIL-4, `treebank-array`, `cap_imm_nret2`, the duplicate-label class, R-3's stored-pattern bug. The file already applies the right discipline in one place — of EARN-0's stored-pattern defect it says *"⛔ NOT ADOPTED BY GOAL-RBP-EARN. Root-causing it does not bill it here."* — **but that discipline is not being applied consistently to anything else.**

⇒ **The cost is real and compounding:** each new seat spends its budget on triage while believing it is advancing EARN, and the file grows (952 lines, **22 cursor entries** where `RULES.md` STALE-ORIENTATION (c) says *prune below the last ~3*). Orientation alone is now expensive — it consumed a large fraction of this session's budget before any work started.

**LON: ONE OF THESE, PLEASE —**
- **(a)** Split the defect ledger out (`GOAL-SN4-CRASH-TRIAGE.md` or route each item to its owning goal), leaving this file for the EARN ladder proper; **or**
- **(b)** Accept that crash-triage IS the prerequisite — the tree cannot be measured for frame-need while it SEGVs — and **re-title the ladder to say so**, so seats stop mis-reading their own progress.
- **Either way: prune this file.** 19 of 22 cursor entries are below the retention line RULES already sets.

### 8. NEXT SEAT, IN ORDER
1. **Rulings first:** §2 (`scrip.c` on the trigger list, and the four-copy sync problem) and §7 (this file's scope). Both are cheap to decide and both compound if left open.
2. **EARN-0 continuation** — the real queue is that file's own §8: MONITOR-FIRST on `earn0_varref_cat_dropped`, **the silent-wrong-answer arm, not the loud crash/hang arms.** `setarch -R` (§5) may shorten the crash arm if taken.
3. **Duplicate-label class** (§4) — start at `grep -rn g_m4_dense_nid`, verify before fixing.
4. **`treebank-array`** m4 SEGV — unowned, unmoved.
5. s34's items 2 and 4 (residual-11 bisection; W-pins two-mode gate) — unchanged. **Residual-11's EARN attribution is still an unmeasured hypothesis; MONITOR-FIRST before billing it here.**
6. s29's queue beneath, unchanged. **s30b obligation (i) still OPEN.**

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-12 s35 (Claude Sonnet 5) — **R-2 CLOSED (677e8753 CONFIRMED ON main, NO REVERT). MATCH_SPAN's ZD ARM (346d1d6f, LANDED ONE DAY PRIOR) HAD TWO INDEPENDENT BUGS — eax CLOBBERED BY ITS OWN CALL, AND SUBJECT-EXHAUSTION WRONGLY ROUTED TO FAIL — FOUND VIA MONITOR-FIRST ON 063_pat_fence_fn_optional, FIXED, ZERO REGRESSIONS, BUT 063 ITSELF IS STILL BROKEN BY A SEPARATE BUG.**

**Fingerprint:** SCRIP `af207c9e` (+ regen `3be69bce`) · corpus `edc0986b` (+ regen `fc7bdefd`) · FINDING `FINDING-2026-08-12i-CLAUDE-SONNET5-RBP-EARN-MATCH-SPAN-ZD-ARM-EAX-CLOBBER-AND-EXHAUSTION-EXIT.md`. Full detail in the FINDING; summary below.

**ORIENTATION FIRST, NOT THE CURSOR TEXT.** Re-verified s34's three open rulings against the actual tree rather than trusting the cursor. **R-2 is settled**: `677e8753` (the `main_α` R9/GVA fix) is on `main`, unreverted (`git log --oneline 677e8753..HEAD -- src/driver/scrip.c` empty at the time), and BOARD independently hardened an instrument around it (`5a4a13f9`, `8729da2f`). R-1 (regen-trigger scope for `scrip.c`) and R-3 (`cap_imm_nret2` m3-only SEGV) remain OPEN, untouched this session.

**NEW INSTRUMENT:** `scripts/board_patterns_2mode.sh` — no prior script did a combined m3+m4 `.ref` census over `crosscheck/patterns` in one pass. Measured at HEAD before touching anything: **74/122 AGREE, 46 both-fail, 2 m4-only-fail, 0 m3-only-fail** — unchanged by this session's fix (see below).

**MONITOR-FIRST TRAIL:** picked `063_pat_fence_fn_optional` (small, on-goal: FENCE+capture) → `spl`/`scr` sync-step monitor (bridge pre-applied in cloned `x64`, worked immediately) → pinpointed `N` capturing `''` instead of `'123'` at `FENCE(SPAN(digits)|'') . N` → killswitches `SCRIP_FENCE_WHACK=0`/`SCRIP_U2=0`/`SCRIP_U2_FENCE=0` all INERT, **exonerating the RBP-frame/FENCE1 machinery** for this witness → stripped FENCE+alternation, bug reproduced with bare `SPAN(digits) . N` → IR dump showed the static-vs-dynamic-argument fork (`MATCH_SPAN []` zero-operand literal arm vs `MATCH_SPAN [16]` one-operand ZD arm) → temporary debug shim on `rt_sg_member` (fully reverted, verified via `nm`+`git diff` before commit) showed the ZD arm's needle ptr/len alternating correct/corrupted on every OTHER call, perfectly periodic.

**ROOT CAUSE, TWO BUGS, ONE ARM** (`bb_match_span.cpp`, `_.op_zres && _.op_sa >= 0`, landed `346d1d6f` 2026-08-11 — ONE DAY before this session, never previously exercised): (1) the loop held its scan position in `eax` across `call rt_sg_member`; the RTCC veneer's post-call reload restores only `{r8,r9,r10,r11}` (RC-4 "arg tier reload deferred", by design) so `eax` came back holding the call's OWN boolean return value, and `add eax,1; jmp L(0)` on that corrupted value destroyed position tracking after the first match — `rsi`/`edx` (needle ptr/len) held live across the call had identical zero protection. (2) reaching end-of-subject while every char matched so far routed to `omega` (FAIL) instead of `L(1)` (commit) — an all-member subject could never successfully SPAN to completion. Bug 2 was masked by bug 1 until fixed.

**FIX:** position moves to `FR(_.x86_scratch_off)` (memory, call-safe) across the loop; `rsi`/`edx` reloaded from the ζ-cell every iteration; `jge L(1)` not `jge omega` on exhaustion. `+18/-5`, isolated to one arm.

**MEASURED: crosscheck/patterns 74/46/2/0 UNCHANGED, before and after — zero regressions, zero whole-program repairs in this corpus.** The 7 patterns programs using `SPAN(var)` (`063-066`, `126`, `153`, `179`) all carry ADDITIONAL separate bugs still open. Two new oracle-baked witnesses: `probe/earn0/earn0_span_var_arg_hang.sno` (was rc=124, now `999`) and `earn0_span_var_arg_2char_wronganswer.sno` (was silent wrong `no digits`, now `99`). Regen ×3 run (benchmark: no change; feature: `wordcount.s` updated, auto-committed `3be69bce`; demo: same file, auto-committed `fc7bdefd`; `claws5`/`json` skip as assembler-rejected — matches s34's pre-existing BUILDFAIL note, unmoved, orthogonal).

**⛔ THIS IS NOT AN RBP/EARN FRAME BUG.** Killswitches for the frame machinery were inert on the originating witness. Filed under this goal because found via its own MONITOR-FIRST process on a FENCE witness, not because the fix belongs to the earning layer.

**⛔⭐⭐⭐ SCRUTINY OF THE PLAN — FOUR CORRECTIONS THIS SESSION EARNED THE RIGHT TO MAKE**

**(1) s34's RESIDUAL-11 → EARN ATTRIBUTION IS FALSIFIED FOR AT LEAST ONE MEMBER, AND THE NAME CLUSTER IS NOT A MECHANISM CLUSTER.** s34 wrote: *"`063/064/065/066_pat_fence_fn_*` … A `*FN` inside a FENCE makes P's growth non-constant — the EARN predicate firing, s28 RULING (3) verbatim"*, and correctly self-flagged it as *"HYPOTHESIS FROM A NAME CLUSTER, NOT A MEASUREMENT."* **It is now MEASURED, and the hypothesis is wrong for `063`.** `063_pat_fence_fn_optional.sno` contains **no function call at all** — its body is `X FENCE(SPAN(digits) | '') . N`. There is no `*FN`, so there is no deferred-growth hazard, so RULING (3) cannot be what fires. All three frame killswitches (`SCRIP_FENCE_WHACK=0`, `SCRIP_U2=0`, `SCRIP_U2_FENCE=0`) are **INERT** on it — the RBP/FENCE1 frame machinery is exonerated by measurement, not argument. ⇒ **`fence_fn` in a filename does not imply a function is present.** Any seat triaging the residual set by filename will re-derive this wrong attribution. Check the program text before billing a member to EARN.

**(2) ⛔⭐⭐⭐ A MEASUREMENT-DEFINITION HAZARD THAT COULD MAKE THE WHOLE BOARD READ HEALTHY WHEN IT IS NOT.** s34 reports `patterns` **AGREE 111** of 122 after its fix. This session's two-mode census reports **AGREE 74** of 122 at a later HEAD that *contains* that fix. The gap is too large to be drift, and the likely cause is definitional: **"m3 and m4 agree with EACH OTHER" is NOT "both match the oracle `.ref`."** Two modes agree perfectly on a *wrong* answer — and `063` is exactly such a program (m3 prints nothing, and pre-fix its whole class did too). The HOME GATE lists these as **two separate conditions** for good reason (line 1: *"oracle-green BY SET, BOTH modes, m3 ≡ m4 outputs byte-identical"* — a conjunction). ⇒ **Every published AGREE/DIVERGE number must state which relation it measures.** `scripts/board_patterns_2mode.sh` (new this session) scores strictly against `.ref` in both modes and prints the four disjoint buckets; s34's instrument may be scoring mode-vs-mode. **Reconcile before either number is quoted again** — this is cheap (run both at one hash) and it is a prerequisite for EARN-2, which is a *census*, i.e. exactly the kind of instrument this confusion silently corrupts.

**(3) ⭐⭐⭐ THE HIGHEST-VALUE UNCLAIMED LEAD: THE SIBLING ZD ARMS ARE PROBABLY CARRYING THE SAME DEFECT.** `346d1d6f` (O-7a) landed ZD arms for **all** cset-bearing linear match templates at once, one day before this session. This session found **two** bugs in the `MATCH_SPAN` one, both reachable by a five-line program. The siblings — `bb_match_any.cpp`, `bb_match_notany.cpp`, `bb_match_break.cpp`, `bb_match_breakx.cpp` — **all call the same `rt_sg_member`** and were landed by the same commit in the same shape. **A live smell was observed and NOT chased**: `BREAK(var)` on a subject that should match returned **empty output** in a 6-line probe (`ANY(var)` looked correct). ⇒ **Sweep the four siblings for the identical eax-clobber-across-call and the identical exhaustion-exit routing.** This is a small, bounded, high-yield rung — the diff shape is already written (see `af207c9e`) and each arm needs its own 5-line witness + oracle ref. Do this before opening anything larger.

**(4) THE VENEER'S PARTIAL RELOAD IS A LOADED GUN WITH NO GATE ON IT.** `x86_rtcc_call`'s reload restores **only** `{r8,r9,r10,r11}`; `rax/rcx/rdx/rsi/rdi` are deliberately NOT restored (RC-4 "arg tier reload deferred" — correct, so a caller can read the call's own return value). **Nothing mechanically prevents a template from holding a live value in the arg tier across `x86("call", …)`, and that is precisely the bug fixed this session.** The failure is silent, data-dependent, and — as measured here — can present as an infinite loop, a silent wrong answer, or a SIGSEGV depending on subject length. ⇒ **Proposed BOARD instrument (unclaimed):** a grep/AST check over `src/templates/*.cpp` for a register in the arg tier loaded before an `x86("call", …)` and read after it, without an intervening spill. Even a crude version would have caught this. Cheap, mechanical, and it guards a whole class rather than one instance — the same argument that justifies every other gate in this file.

**NEXT SEAT, IN ORDER:**
1. **Sibling ZD-arm sweep** (scrutiny item 3) — `ANY`/`NOTANY`/`BREAK`/`BREAKX`. Start with the `BREAK(var)` empty-output smell; it is already half-witnessed. Bounded, high yield, pattern already established by `af207c9e`.
2. **`063_pat_fence_fn_optional` IS STILL BROKEN** post-fix (m3 empty output, m4 SIG11) — a separate, now-unmasked bug, and per scrutiny item 1 it is **NOT** an EARN/frame defect. Re-run the `spl`/`scr` monitor fresh; the divergence should now sit past the SPAN capture, in the FENCE/alternation capture wiring. MONITOR-FIRST, do not read code first.
3. **Reconcile the two AGREE definitions** (scrutiny item 2) at one hash, before EARN-2 is opened or any patterns number is quoted again.
4. The other 5 `SPAN(var)` patterns programs (`064-066`, `126`, `153`) unexamined past this fix; `179` is ARBNO+defer and likely belongs to EARN-4 proper.
5. R-1 (regen-trigger scope for `scrip.c`) and R-3 (`cap_imm_nret2` m3-only SEGV, unowned) from s34 — still open, untouched this session.
6. **Proposed gate** from scrutiny item 4 — offer to BOARD; it is a ZERO-compiler-bytes item, collision-free by construction.

**⛔ SELF-CORRECTION, RECORDED BECAUSE THE RULE EXISTS FOR EXACTLY THIS:** an earlier draft of this very cursor entry ended with a line stating the repos' push status. **That violates STALE-ORIENTATION (a) — push status must NEVER be written into a doc; `handoff_status.sh` is the only push truth.** The line is removed. The rule is easy to break precisely when a session ends blocked and wants to leave a note about it; the note is the thing the rule forbids.

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-12 s34 (Opus 5) — **THE `main_α` BRIDGE NEVER ESTABLISHED R9. RC-5-GVA LANDED ITS MAIN-ENTRY LOAD ON `flat_α` ONLY. ONE LINE: `patterns` DIVERGE 54→11, 42 REPAIRED, 0 REGRESSIONS. THIS IS A *SOURCE* FACT AND IT DOES NOT CONFLICT WITH s33's RETRACTION.**

**Fingerprint:** SCRIP `d0d9515e` (= `52545cbf` + ONE line in `src/driver/scrip.c`) · corpus `c91d1adf` · FINDING `FINDING-2026-08-12e-…-AND-S33-D1-D2-ARE-BOTH-BY-DESIGN.md`. Build order: `install_system_packages.sh` ran BEFORE both builds; the A/B differs only by the one line.

**ROOT CAUSE — PROVEN FROM GIT, NOT FROM A BUILD.** `git show 52545cbf:src/driver/scrip.c | grep -c rtcc_load_all` ⇒ **exactly 2**: mode-4 `flat_α` (~1490) and mode-3 (~1651). The `main_α` bridge (~1278-1290) is `mov r12,[0x70000000]` · `xor esi,esi` · `jmp main_α` — **ZERO**. Every program routed through `main_α` emits `[r9+…]` GVA addressing (templates gate on `g_rtcc_on`, ON) with r9 never loaded ⇒ first write to any GVA-slotted variable faults. A 5-line probe emits 16 `r9` refs and no `rtcc_load_all`.

**⭐ RECONCILES WITH s33's RETRACTION — BOTH CAN BE TRUE, THEY NAME DIFFERENT SITES.** s33 retracts on the ground that a `scrip` built before `install_system_packages.sh` **omits** the call. That mechanism concerns a call that EXISTS in source (Site B). **It cannot explain Site A, where there is no call to omit.** ⇒ a bad build may drop Site B's call *in addition*; the Site A gap is unconditional. ⛔ **Do not read this cursor as contradicting the retraction, and do not read the retraction as closing this.**

**⭐ PLACEMENT IS LOAD-BEARING AND IS NOT SITE B's.** `rtcc_load_all` writes rax/rcx/rdx/rsi/rdi/r8/r9/r10/r11. It must sit AFTER the `is_prolog` warmup PLT calls (they clobber caller-saved r9) and BEFORE the `xor esi,esi` / `xor r14d` / `lea rcx,[.Lmain_zf_γ]` / `lea rdx,[.Lmain_zf_ω]` staging, which re-stages what load_all clobbers. The naive twin of Site B's placement destroys the ζ-frame γ/ω wires.

**MEASURED, ALL THREE CORPORA, FIXED BUILD.** `patterns` 122: AGREE **111**(68) · m4 SEGV **39**(82) · PURE **10**(52); per-program join 122/122 ⇒ **REPAIRED 42 · REGRESSED 0**; **m3 bit-identical** (28/6 both runs). `demo` 24: AGREE **19**(17) · PURE **1**(3) · **BUILDFAIL 4→4 UNMOVED** (`claws5` `expression` `json` `porter` — orthogonal to r9, still unowned; demo's true m4 SEGV is `treebank-array` alone). `benchmarks` 23 **(first measurement ever)**: AGREE **22** · PURE **0**. **Σ 169 · AGREE 152 · residual m4-only crash class = 11.**

**⛔ s33's D1/D2 REMAIN FALSIFIED AND MUST NOT BE "REPAIRED".** `rt_gva_island()` ends `return (DESCR_t *)RT_GVA_VA` — the island is **pinned at the constant**, so the dropped `rax` carried no information (D1). Slot 48 = `RTCC_SLOT_R9`(6)×8, seeded once and eternally by the `rtcc_init` constructor, labelled *"BLOCK-CANONICAL EXCEPTION for constant globals — no companion writes needed anywhere"*, `static_assert` at `x86_asm.h:319` pinning it ⇒ **a save-side write at 48 is not missing, it is forbidden** (D2).

**⭐⭐⭐ THE RESIDUAL 11 CLUSTER ON THIS GOAL'S OWN SUBJECT MATTER.** `063/064/065/066_pat_fence_fn_*` (**four**), `156_pat_cap_alt_abandon_pop`, `157_pat_cap_arb_alt_keep`, `141_pat_eval_double_fn_arbno`, `121_pat_calc_op_dispatch`, `064_replace_multi_arm`, `154_pat_construction_time_hoist`, + `treebank-array`. A `*FN` inside a FENCE makes P's growth non-constant — the EARN predicate firing, s28 RULING (3) verbatim. ⛔ **HYPOTHESIS FROM A NAME CLUSTER, NOT A MEASUREMENT — MONITOR-FIRST before billing it to EARN.**

**⛔ m3 IS NOT EXONERATED AND ONE PROGRAM DIVERGES THE OTHER WAY:** `benchmarks/snobol4:cap_imm_nret2` is **rc3=139, rc4=0** — m3 SEGVs where m4 is clean, and it is that corpus's entire DIVERGE.

**⛔ THREE OPEN RULINGS (Lon must decide before the next seat can proceed cleanly):**
- **(R-1) Regen ×3 scope:** `RULES.md` step 4 lists `emit.cpp / templates/*.cpp / x86_asm.h / lower_snobol4.c / runtime sinks` as regen triggers. `src/driver/scrip.c` is not on that list, yet this session's one-line change altered emitted bytes for **every** m4 SNOBOL4 program. Either `scrip.c` belongs on the list, or this class of change is legitimately exempt. **Ruling needed; regen NOT run.**
- **(R-2) s33 retraction vs. s34 finding:** s33 says the entire s32 m4 SEGV class was a phantom from a bad build (skipped `install_system_packages.sh`), with family H going 0-pass/31-REGRESSION → 30-pass/1-REGRESSION on a correct build. s34 shows the `main_α` gap exists **in source** at commit `52545cbf` (`grep -c rtcc_load_all` → exactly 2, none at Site A), independent of build order. Both can be true — a bad build additionally drops Site B's call — but the implication for whether s34's fix is load-bearing differs sharply. **Settle from evidence:** compile `52545cbf` correctly and check `crosscheck/patterns` against a probe in the pure-`main_α` family.
- **(R-3) `cap_imm_nret2`:** `benchmarks/snobol4`, **rc3=139, rc4=0** — m3 SEGVs, m4 clean. First measurement ever (benchmarks were the one unmeasured corpus). MODE34-IDENTICAL violation in the *reverse* direction. Unowned.

**NEXT SEAT, IN ORDER (after rulings):**
1. **Regen ×3 if R-1 says so** — or add `scrip.c` to the step-4 trigger list.
2. **Own the residual 11 m4-only crashes** — small enough to bisect per-program; MONITOR-FIRST; the `fence_fn_*` cluster is a hypothesis (EARN predicate, s28 RULING (3)), not a measurement.
3. **Own the BUILDFAIL 4** (`claws5`, `expression`, `json`, `porter` — demo only, orthogonal to r9, confirmed unmoved by this repair).
4. **W-pins into a two-mode gate** — now cheap: m4 half can pass; W5 was the last hold.
5. **EARN-2 re-cut over reading sites including base-register liveness** — a census over establishments *or* displacements scores the r9 class clean; acceptance unchanged (`earn0_pend_alt_first_arm` must score `owed`).
6. s29's queue beneath, unchanged. **s30b obligation (i) OPEN.**

**⛔⭐⭐⭐ CONCURRENCY CASUALTY — THIS SESSION'S COMMITS WERE WIPED ONCE AND RE-APPLIED.** A peer seat rewrote `.github` history (`8ce704c3` → `1f62ed25`) and reset SCRIP to `52545cbf`, discarding my committed-but-unpushed SCRIP fix and cursor edit; `git status` showed clean and the FINDING survived only as an untracked file. **Committed is not safe — only PUSHED is.** Both repos are UNPUSHED at handoff (no credential); s33's own work was likewise unpushed on my arrival. ⭐ Two vacuous instruments of my own died to printing a denominator: a `join` over never-created inputs reported "0 regressions" from an EMPTY set, and awk's default whitespace FS on a **TSV whose fields contain spaces** reported `42/44` as `25/78`. Every count needs a total beside it (86 − 42 = 44 ✓).

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-12 s33 (Opus 5) — **A `scrip` BUILT BEFORE `install_system_packages.sh` OMITS `call rtcc_load_all@PLT` AND MANUFACTURES A PHANTOM m4 SEGV CLASS. I PUBLISHED IT AS A ROOT CAUSE AND RETRACTED IT. ⭐⭐⭐ THE INHERITED 82/122 MAY BE THE SAME ARTIFACT — TEST IT BEFORE OPENING EARN-2.**

**Fingerprint:** SCRIP `52545cbf` · corpus `c91d1adf` · **ZERO compiler bytes this session, and my two demo scripts were rolled back unpushed.** FINDING `FINDING-2026-08-12d-CLAUDE-OP5-A-SCRIP-BUILT-BEFORE-INSTALL-SYSTEM-PACKAGES-…-SAME-ARTIFACT.md`.

**⛔ WHAT HAPPENED.** I skipped `scripts/install_system_packages.sh` at session start. `make scrip` exited **0** with a fully working compiler — `--run` green everywhere — but its mode-4 preamble is silently short one line: **`call rtcc_load_all@PLT`**, which establishes the RTCC set incl. **r9, the GVA base**. Every `mov [r9+0], rax` then wrote through garbage. I measured `163 / 161 m4 SEGV`, convicted the instruction in gdb, minimised it to a bare literal match, and proved causation by patching emitted text (5 programs, 4 families, `rc=139` → `rc=0` byte-matching m3 + `.ref`). **All observations real; conclusion wrong.** Settled by two mtimes: crashing `.s` emitted 14:09:50, `scrip` rebuilt 14:26:52, working `.s` 14:37:45 — `diff` = **exactly one line**. Emission is **fully deterministic** (5/5 md5, cwd-independent): not ASLR, not a claim gate — **two different compilers.**

**RE-MEASURED ON THE GOOD BUILD — `probe/bb` family H: m3 = `30 pass · 1 REGRESSION`, m4 = `30 pass · 1 REGRESSION`. IDENTICAL.** (Was `0 pass · 31 REGRESSION`.) **MODE34-IDENTICAL holds on this family.** ⛔ **Every other number I produced is VOID** — I re-ran only family H.

**⭐⭐⭐ THE LIVE HYPOTHESIS FOR THE NEXT SEAT (not a finding — I did not test it).** An under-built tree reproduces *exactly* the inherited shape: mass m4-only SEGV with m3 clean. s32's `patterns` `m4 SEGV=82 / PURE m4 CRASH=52` and `demo`'s unbilled `BUILDFAIL=4` are that shape. **SETTLE IT FIRST:** `bash scripts/install_system_packages.sh && rm -f scrip && make scrip && make libscrip_rt`, verify `./scrip --compile X.sno | grep -c rtcc_load_all` **≥ 1**, then re-run `test_census_m3_m4_divergence.sh` on `crosscheck/patterns`. **If the 82 collapses, then the `.`×alternation quartet, the `rt_cap_push`/`g_cap_gen`/`.text`-pointer conviction, and the "52 concealed crashes" that promoted B-0 to top-of-board are all the same artifact, and two sessions of EARN scoping need re-basing.** If it holds, it is real and this paragraph is void. ⛔ **Do not open EARN-2 until this is closed.**

**⭐ SURVIVES INDEPENDENT OF THE BUILD — B-0's PREMISE IS FALSE.** `run_suite.sh MODE=compile` does **not** return EMPTY: it prints verdicts, `want=`/`got=`, summary, `mode: compile` — on the bad build (correctly reporting 31 real crashes) *and* the good one (`30 pass · 1 REGRESSION`). **The harness works**; the inherited claim reads *program-output* emptiness as *instrument* failure. Reproduce B-0 before repairing it. ⭐ **`H31` is a genuine defect in BOTH modes** (`FENCE over ALT with capture`, `got=[]`, CRASH, **not in XFAIL**) — real, unrelated to the artifact, and a clean next target.

**⛔ THE HABIT THAT CAUGHT IT, RECORDED BECAUSE IT NEARLY DIDN'T.** Everything downstream of the bad build was self-consistent — gradient, gdb conviction, generalization, working patch — and I had **already committed** the FINDING and cursor. What broke it was validating a new instrument on **known answers**: it reported `m4 SEGV=0` on five programs I had already proven SEGV. I was one step from billing a sixth vacuous instrument; the instrument was fine and **the binaries had changed under me.**

**RECOMMEND (cheap, prevents recurrence):** make `./scrip --compile` output containing `rtcc_load_all` a **build gate**, and promote the package step in REPO-SCRIP.md from a documented line to a checked one. `make scrip` exiting 0 on an under-provisioned tree, with `--run` unaffected and only m4 emission short one call, is STALE-BINARY-BUILD-OK with a new face.

**NEXT SEAT, IN ORDER:** (1) settle the 82 (above); (2) then s32's order stands — W-pins into a two-mode gate, EARN-2 re-cut over reading sites, s29's queue; (3) `H31`. **s30b obligation (i) OPEN, untouched.**

**CONTAINER NOTES.** `gdb` absent and **not** installed by `install_system_packages.sh`; needs `apt-get update` first (bare install 404s on `libc6-dbg`). Background builds need **`setsid`**; plain `nohup … &` is killed between tool calls and silently truncated my first build.

## ⛔⭐⭐⭐ LADDER RBP-EARN — FRAME BY NEED (Lon ruling s25; SUPERSEDES the enumerated license set, s24b's ARBNO rung, and every "blobs get frames / blobs get no frames" premise in this file)

### THE LAW (one sentence, and everything else is a corollary)

> **A cell needs a frame ⟺ the byte distance between that cell and RSP is not a compile-time constant at some site that reads it.**

RSP-relative addressing works exactly when the compiler can count the bytes between the carve and every access.  So the question is never *"is this ARBNO?"* or *"is this a pattern blob?"* — it is **"what can sit on the spine in between, and do I know its size?"**

### THE TWO HAZARD CLASSES (the only two things that break compile-time distance)

- **OPAQUE — unknown SIZE.** A record of compile-time-unknown size may be live on the spine between the carve and the read.  Sources: the deferred/unevaluated expression operator `*E`, and variant (run-time-valued) pattern references.  ⛔ **NOT** an ordinary pattern-valued variable: pattern construction is BY VALUE, so `LIST` in `TEST = POS(0) LIST RPOS(0)` is fully known at build time.  Only `*` defers — which is exactly why the manual (p.122) *requires* the `*` for the recursive-list definition and calls it "a forward reference to a pattern not yet defined."  **This is the same cut as this file's invariant/variant split, re-derived from the addressing side.**
- **UNBOUNDED — unknown COUNT.** A compile-time-unknown number of uniform records.  Sources: **ARBNO** (p.121: `ARBNO(P)` behaves like `( "" | P | P P | P P P | … )` — every retry adds a live choice point, and each stays live because a later failure must peel back exactly one instance) and **true recursion** through a deferred self-reference.  ⛔ The count is unbounded **BY DESIGN and its overflow is oracle behaviour** (p.123: heavily recursive patterns and long subjects can overflow the stack; the remedy is `-s`, a bigger stack).  **No compile-time-sized array may stand in for it.**

### THE THREE RULES

1. **OWNERSHIP.** The frame belongs to the node holding a cell **live ACROSS** a hazard — **never to the hazard itself.**  `*P` owns nothing.  In `*P $ VAR` the frame is **`$`'s**, because `$` must save δ0 across its operand's execution and read it after; in `PRIMITIVE() $ VAR` that span is static and `$` is frameless.  ARBNO owns a frame **on its own account** — its control cell is live across its own unbounded retries — so **`ARBNO(LEN(1))` needs a frame exactly as much as `ARBNO(*P)` does.**  (Chicken-and-egg proof: at iteration N the cell sits at `base − N×R`; computing that needs N; N lives in the cell.  An anchor is not optional.)
2. **ANCHOR — no meta register.** Every frame reserves ONE fixed slot for the match anchor; frame-enter **copies the parent's** (two instructions); MATCH_BEGIN seeds it.  Any depth then reaches the match root in **ONE indirection — no walk, no register claim.**  Three properties a register does not buy: it costs nothing from a pool that is fully claimed (R12–R15/RBX spoken for, RTCC wants the caller-saved set); it is **per-activation by construction**, so a nested `*F()`'s inner MATCH_BEGIN cannot smash the outer — the exact `g_blob_ctx`/`g_rtcc_block` flat-cell defect this file has convicted twice; and it survives C crossings **without a veneer**, because it is memory the callee cannot name.  ⛔ A register is admitted ONLY on a measured hot path, never on principle.
3. **OPERANDS ARE RSP-RELATIVE, ALWAYS** (Lon: *"no RBP operand allocations"*).  A frame holds ONLY cells that span a hazard edge — a handful of slots each.  **Frames become MANY and TINY.**  The count RISES and that is the design working: "it is a pattern blob" is not a reason FOR a frame, and "it is constant-folded" is not a reason AGAINST one.

### ⭐⭐⭐ THE EARN PROTOCOL — set/unset/save/restore, and the crossings (derived s25 with Lon in-chat; ⛔ NOT YET MEASURED — see EARN-0b)

**THE INVARIANT.** *At every instruction boundary, `rbp` names the innermost live EARNED frame on the current control path, and `[rbp+ANCHOR]` names the enclosing MATCH_BEGIN frame.*

**TWO EMISSIONS, AT THE EARNING BOX ONLY.**  **ENTER** = `push rbp` · `mov rbp,rsp` · `sub rsp,K` · copy parent anchor into this frame's ANCHOR slot.  **LEAVE** = `mov rsp,rbp` · `pop rbp`.  **⭐ THE SAVE LOCATION IS THE FRAME CHAIN ITSELF** — `push rbp` puts the parent link on the spine, per activation, and that is the structural answer to the flat-cell defect class this file has convicted twice (`g_blob_ctx` at `pattern_match.c:624`, `g_rtcc_block` at `rtcc.h:63`): under EARN **there is no single cell to smash.**

**⭐⭐ γ AND β ARE FREE — THE LIFO THEOREM.**  Trace `A B C`, all earning.  A ENTERs (rbp=A) → γ forward emits NOTHING, and C runs with rbp=A because A's frame *is* the innermost live one.  B ENTERs (rbp=B, A's link at `[B+0]`) → C ENTERs (rbp=C) → C fails, LEAVEs → rbp=B **exactly**, and C's ω wires into B's β needing no rbp traffic **because the leave already restored it**.  B exhausts → LEAVE → rbp=A → A's β.  Correct at every port.  ⇒ **The CLASS D `{res,rbp}` resume record is not needed on this path** — not because it was wrong, but because it was paying for a frame that had not been earned.  Under EARN the LIFO discipline pays instead, for free.

**⛔ THE FOUR CROSSINGS WHERE IT IS *NOT* FREE (this is the whole cost of the protocol):**

| Crossing | Why LIFO fails | Mechanism | Cost |
|---|---|---|---|
| **ABORT · FENCE-backup · total failure** | jumps out from arbitrary depth | `mov rbp,[rbp+ANCHOR]`, then drain rsp to that base | 2 insns |
| **Unanchored retry** (scanfail → next start position) | same shape; re-attempts from the match root | same anchor drain, then re-enter α | 2 insns |
| **ENTER at a port that is not α** | ARBNO begins a NEW ACTIVATION at β | emit ENTER at β as well as α | same 4 |
| **Heap-frame activations** (resumable callables, generators, `flat_gen`) | the frame **OUTLIVES THE SPINE** — genuinely non-LIFO | here and ONLY here the base must travel in the wire: the `{res,rbp}` record SURVIVES, now BY NEED | as today |

**⭐⭐⭐ THE C BOUNDARY IS FREE, AND IT IS THE INVERSE OF WREG'S PROBLEM.**  `rbp` is **callee-saved** under SysV: every `rt_*` crossing preserves it with **no veneer, no claim gate, no sweep**.  r10/r11 are caller-saved — which is what forced the veneer, which is what turned out to be a flat cell (s14/s13c, both seats, reconciled).  **EARN's carrier has the property WREG's carrier lacks.**

**⭐⭐ SHARPENING THE PREDICATE (this changes EARN-0's table and cuts EARN-5's scope):**
> **A read earns a frame IFF hazardous material is still live on the spine AT THE READING EDGE.**  Failure edges unwind by construction; success edges do not.

So `$` **earns** (it reads δ0 on its operand's SUCCESS edge, with the operand's frames still alive), while **ALT does NOT** — its δ0 restore happens on the FAILURE edge, where LIFO has already returned rsp to ALT's own depth, so a static `[rsp+K]` is correct **even when the arms contain `*P`**.  ARBNO still earns: at its β its own unbounded stack of matched instances is live below it.  ⇒ EARN-0's table gets a column that can be filled MECHANICALLY: **which edge does the read happen on.**

**TWO CONSEQUENCES.**  (1) **ARBNO's counter dies** — if ARBNO ENTERs per iteration, the frame chain IS the counter and exhaustion is "reached my base frame": no `i`, no array, no sizing question.  That retires the last of s24b rather than replacing it.  (2) **Frames are themselves spine traffic**, so a statically-present frame is a known-size push and breaks nothing; only frames of UNKNOWN COUNT (ARBNO's) are hazards — **the predicate stays self-consistent under its own output.**

### THE RUNGS

- [ ] **EARN-0 · THE PREDICATE — ⛔ NOT CHEAP, NOT AN OPENER: GATED ON TWO COMPILER DEFECTS THIS GOAL OWNS (label corrected s42; the old header read "no code, cheap, opens any session" and that phrase, contradicted by note (C) 400 words below it inside this same bullet, is a live candidate for why s33–s39 each opened this rung and ended in crash triage — read (C) BEFORE planning a session around this).**  Produce IN THIS FILE a table: every `IR_MATCH_*` kind × {NEVER · IFF-OPAQUE-SIBLING · ALWAYS} with the manual citation for each non-obvious row.  Re-run the law over the four historical keepers and record the result including the two refusals (below).  Hand-check against three witnesses compiled at HEAD (`ARBNO(LEN(1))`, `*P $ VAR`, a fully constant-folded pattern) — the table must predict what the compiler already emits where the compiler is already correct.  **Deliverable is the table + the three rulings raised; ZERO src bytes.**  ⛔ **s27 PARTIAL DISCHARGE — READ BEFORE RUNNING THIS RUNG** (`FINDING-2026-08-11f`): (A) **The table EXISTS** — 32 kinds × HAZARD/READS-ACROSS/EDGE/VERDICT, in the FINDING; predicts-HEAD check passes (only 5 kinds may hold a frame; 24 of 29 match templates are already rbp-free). (B) **`BAL`, `CALLOUT`, `REPLACE` rows CLOSED in s27 §7** (BAL=NEVER/template read; CALLOUT=VACUOUS/no template; REPLACE=NEVER at HEAD). ✅ No open asm-verification rows remain. (C) **The hand-check STILL CANNOT BE COMPLETED for the STORED-pattern forms** — s29 STAGE-BISECTED the defect (LOWER, not optimizer; producer elision; TWO DEFECTS masking each other — see `FINDING-2026-08-12-CLAUDE-OP5-EARN-0-…`), but fixing either defect is NOT this goal's work. ⛔ **DO NOT attempt the stored-form hand-check until these are repaired — both defects are owned by this goal (Lon ruling s29).**  Key warning: `SCRIP_PAT_INLINE=0` surfaces a second defect (consumer path hangs); FIXING DEFECT A ALONE LOOKS LIKE A REGRESSION (silent rc=0 → rc=124). Judge BY SET. Existing witnesses + oracle-baked refs at `corpus/probe/earn0/`. (D) **EARN-1's two hazard inputs already exist** as `IR_t.pat_static` (OPAQUE) and the arbno frontier gate (UNBOUNDED) — consume them, do not re-derive; `emit_graph_has_deep_arrival` is the de-facto authority — reconcile with it. (E) **Ruling (a) is reframed as a DELETION** — both capture arms live, desynced before (s22m). ⛔ **s29 WARNING FOR EARN-1: do NOT consume `IR_t.pat_static` blindly.** On the BINOP arm the operand has been DROPPED before `pat_static` is evaluated; its closure runs over a non-existent node. Verify what it returns on `earn0_varref_cat_dropped` BEFORE wiring it into `frame_need_of()`. `emit_graph_has_deep_arrival` remains the de-facto authority.
- [ ] **EARN-0b · FALSIFY THE LIFO THEOREM BEFORE ANYONE BUILDS ON IT (no code, ~1 hour — ✅ NOW ACTUALLY RUNNABLE, s42: this rung's method is literally "gdb-watch whether `rbp` at β equals `rbp` at γ" and gdb is installed as of s42; note (B)'s broken-witness-class and (C)'s dark-instrument caveats still bind, so use the FUNCTION + `c_rt_defer_get_pat_fn` route (A) names).**  ⛔ **The EARN PROTOCOL above is DERIVED, NOT MEASURED** — the whole ladder rests on "γ and β are free", and this file's own history is seats trusting a derivation that a probe would have killed (s24's vacuous classifier, s23's dead board, s37's vacuous killswitch A/B).  Cheapest falsifier: ONE program with a framed box that suspends across a SECOND framed box, compiled at HEAD; gdb-watch whether `rbp` at β equals `rbp` at γ.  Also confirm the heap-frame row by the same method on a generator/resumable-callable witness — that row is the one predicted NOT to hold.  **Deliverable: theorem CONFIRMED or the crossing table grows a fifth row.  Either outcome is a pass; a seat that skips this and builds anyway is the failure.**  ⛔ **s26 PARTIAL DISCHARGE — READ BEFORE RUNNING THIS RUNG:** (A) LIFO CONFIRMED both directions on green SNOBOL4 witnesses (RSP instrument; `c_rt_defer_get_pat_fn` — CONFIRMED fires — is the breakpoint; ⛔ `c_rt_match_enter` is dark in m3: zero events, inline native, do not use). DOWN: nested `*F()`⊃`*G()` nests at exactly 16B/level. UP: `161_pat_defer_fn_nested_match` returns byte-identical rsp after FUNCTION+nested-match. (B) **The SNOBOL4 nested-framed-construct witness class is BROKEN at HEAD** (FENCE 6/13 WRONG, `066` silent empty output, `147`/`181` SEGV) — the experiment cannot be run on those witnesses; use FUNCTION + `c_rt_defer_get_pat_fn` as above. (C) **The heap-frame row (generators) has a DARK INSTRUMENT at HEAD**: `c_rt_gen_spine_resume_enter` fires ZERO times on the green `generators.icn`. ⛔ **SYMBOL PRESENCE IN `nm` IS NOT INSTRUMENT LIVENESS** — prove a symbol FIRES before planning a rung on it. MON-RE is the first work for the generator row; try `rt_call_value_resume_h` / `fc_tail_defer_susp_g` and confirm each fires before trusting. The heap-frame row remains **UNTESTED**.
- [ ] **EARN-1 · THE CLASSIFIER, ONE AUTHORITY, DORMANT.**  ONE function — `frame_need_of(IR_t*)` — computed at plan time and staged into `g_emit` (precedent: `cap_anchor_of` / `op_cap_anchor`, emit.cpp:812 — env read at the authority, template keys purely on the staged value so the ends cannot half-flip).  Its inputs are the two hazard classes **plus the READING-EDGE column** from the protocol sharpening (success-edge reads earn, failure-edge reads do not).  **NOTHING reads it yet.**  Gate: build green + emitted bytes **byte-identical** to HEAD across the probe suite (a dormant landing is what the killswitch law looks like when the replacement is from-scratch).  Also emit it as a diagnostic column so EARN-2 can consume it.
- [ ] **EARN-2 · THE CENSUS CHANGES UNITS — DO THIS BEFORE ANY DELETION.**  `scripts/test_census_rbp_frames.sh` today counts frames.  Re-cut it to count the TWO DEBTS: **UNEARNED** = an establishment whose owning node's classifier says NEVER (a frame nobody paid for), and **OWED** = a node the classifier says ALWAYS that has no frame (a need nobody served).  Both columns, per corpus, m3 and m4.  **From here on the ratchet is `unearned == 0 && owed == 0`, not `frames == 0`.** ⛔⭐ **s29 PHASE NOTE: THE TWO COLUMNS ARE NOT SYMMETRIC AT HEAD.** The eradication already ran, so `unearned` starts at or near ZERO for the blob class and `owed` starts LARGE. **`owed` is the working number and the one that will drive every remaining rung.** Expect the frame count to RISE monotonically from here — that is the goal succeeding, not regressing.  ⛔ Landing this after a deletion would measure the deletion with the instrument the deletion invalidated (the REAPED-BUILD-FAKED / dead-board class, twice on record in this file).
- [ ] **EARN-3 · ANCHOR PROPAGATION (mechanism only — establishes NO new frames).**  Fixed slot in every frame; enter copies parent; MATCH_BEGIN seeds.  Witness: a 3-level nested `*F()` where the innermost reads the outermost match root and prints it.  Gate: probe + xc318 BY SET ≥ floors, both modes.  **This rung is what makes every later rung cheap; it lands alone.**
- [ ] **EARN-4 · ARBNO FROM SCRATCH (full runway; ONE isolated commit for the delete).**  DELETE the current ARBNO frame/cursor machinery outright — the `sub rsp,16` carve, every `[rsp+0]`/`[rsp+4]` cursor access, the in-blob per-iteration rbp rebase chain — and rebuild: **one frame per activation on the spine**, control cell at a fixed offset in it, exhaustion by the frame chain, growth against the real stack limit.  ⛔ `git revert` of that commit is the only undo (killswitch law does not cover deletions).  ⛔ Templates touched ⇒ **ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md are mandatory first reads** (RULES, non-negotiable).  Gate: `arb1.sno` T1 **and** T2 (the exhaustion path that SEGVs at HEAD) both oracle-green; N22–N33 + probe `181`; ⭐ **`earn0_disc_arbno_star_fence_positive`** (s29 polarity-inverted witness — oracle MATCHES, HEAD FAILS; the ARBNO×FENCE×`*cmd` family's first non-vacuous positive test; proven-separating control `earn0_disc_arbno_star_fence_poisoned` beside it); `board_patterns_set.sh` diff BY SET — **watch the BROKEN set, not the net count.**  Read `bb_match_arbno.cpp` (439 lines) cold before choosing the record shape.
- [ ] **EARN-5 · THE ACROSS-HAZARD OWNERS.**  `$` (immediate) and `.` (conditional) and any construct saving δ0 across an operand that contains an OPAQUE node.  Frameless where the span is static — that is the majority and it is where the win is.  Gate: the capture families (`w_cap_*`, `mv_*_cap`) BY NAME, both modes.
- [ ] **EARN-6 · MATCH_BEGIN AND FENCE GO CONDITIONAL.**  MATCH_BEGIN establishes **iff** its pattern contains an OPAQUE or UNBOUNDED node; a fully constant-folded match is frameless top to bottom.  FENCE establishes **iff** a backup can arrive from opaque-or-unbounded depth — bare `FENCE 'x'` in a static pattern is frameless (p.125: backup through FENCE fails the match; failing cleanly means restoring a spine whose depth you must be able to name).  ⛔ `FENCE(P)` is a DIFFERENT construct (p.127 — scopes the block to alternatives *within* P); classify both rows separately in EARN-0.
- [ ] **EARN-7 · RESIDUE SWEEP OF THE OLD REGIME (⛔ s29: SCOPE REDUCED — THE MAIN DELETE ALREADY LANDED).**  ⛔ **This rung is NO LONGER "delete the frames"** — `1af93e3a` did that and blobs carry no RBP. What remains is **dead protocol scaffolding around an absence**:   `emit_jmp_pin_rbp` / `emit_rec_pin` / `emit_heap_fb_adopt` blob-class pinning, BLOB-GRANT's rbp pin, the CLASS D `{res,rbp}` record and its `pop rbp` res stub, the ω absolute unwind `lea rsp,[rbp+kt]`, the scanfail `mov rsp,rbp` whack.  **After this rung a frame exists IFF the classifier asked for one** — graph class stops being a frame input entirely.  Census must show UNEARNED → 0 with OWED staying 0.
- [ ] **EARN-8 · STATEMENT AND FUNCTION RE-EXAMINED (Lon ruling required — see below).**  Both fail the predicate on inspection; both are load-bearing elsewhere.  Do not touch either before EARN-7 is sealed and the ruling is in.
- [ ] **EARN-10 · GLUE IS TWO KINDS AND CARRIES R10/R11 (ABSORBED from LADDER WREG + LADDER PT, Lon ruling s29).**  Exactly **ONE-SHOT** and **PASS-THRU**; **FRAMED is deleted as a glue kind** — its frame emission moves to `x86_alpha`/`x86_omega` under EARN-1's staged predicate.  Wires ride **rΓ=r10 · rΩ=r11** in BOTH kinds, one product-wide convention (per-kind split = the mixed regime ZW16 convicted).  Site glue = `lea r10,γ` · `lea r11,ω` · `jmp` target; blob exits = `jmp r10` / `jmp r11`.  ⛔ **ORDERING: this rung REQUIRES EARN-1 landed and EARN-3's anchor**, because pass-thru with zero frame is only correct once the constructs that NEED a frame have earned one — the old WREG ladder's residual 19 SIGSEGV + 7 HANG were exactly the constructs EARN gives frames to.  ⭐ **That reframes the old ladder's blocker: it was not a glue defect, it was a MISSING FRAME.**  Existing mechanism spec + claim gate + 234-site sweep census: LADDER WREG below (ABSORBED, read it).  ⛔ r10/r11 are SysV CALLER-saved — the save is TEMPLATE-EMITTED per-activation on the spine, never at an implicit choke (s18: RSP-SAFETY LAW + the stack-arg witness `bb_arith.cpp:25-29`).  ⛔ Templates touched ⇒ ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md mandatory first reads.
- [ ] **EARN-11 · THE α/ω PARAMETERIZED FRAME FORM (the ruling made real).**  `x86_alpha`/`x86_omega` become the **SOLE RBP WRITER** product-wide, parameterized on the staged `frame_need_of` value; `bb_glue_framed_enter/_leave` loses its RBP-writer status and either becomes α/ω's callee or is deleted.  **γ EMITS NOTHING — that IS the LIFO theorem.**  The α/ω asymmetry (enter at α, leave only on the failure/exhaust edge) is CORRECT — say so in the code, because it reads as a missing bracket to anyone expecting symmetry.  **TWO SITES STAY EXPLICITLY CALLABLE:** FENCE1's LEAVE (fires at a chosen PAIR before `fence_whack_commit`) and the ANCHOR DRAINS (ABORT, unanchored retry).  ⭐ Language-agnostic ⇒ lands product-wide (Icon `zframe`, Prolog, `flat_gen`) — **either a large win or a blast radius wider than EARN-4; decide deliberately.**  Gate: default-off staged value ⇒ emitted bytes byte-identical to HEAD; then per-node arming only (⛔ TRANSITION HAZARD: old pins still live until EARN-7).
- [ ] **EARN-9 · SEAL.**  Standing gate `unearned == 0 && owed == 0`; regen ×3 (stacks with the regen already owed from s24); cursor move; FINDING.

### THE TWO REFUSALS THE LAW PRODUCES (stated up front so nobody reads them as regressions)

- **STATEMENT fails the predicate.**  MATCH_END unwinds the whole match, so at statement resume RSP is back at statement-entry depth — **statically known.**  STATEMENT's license was always derivative: it was licensed because the match unwind was not trustworthy (**FF-0's conviction: blob γ/ω/res never restore RBP**).  Fix the unwind and STATEMENT is frameless.
- **FUNCTION fails it too, on the same reading of its own citation.**  Manual p.104: on call, existing values of locals and dummy args are **saved on a pushdown stack** and restored on return — that is pure LIFO spine traffic, a SAVE/RESTORE need, **not an addressing need**.  A frame is how it is implemented today, not what the semantics demand.

### ⛔ THREE RULINGS ONLY LON CAN MAKE (raised at EARN-0; (a) is the schedule-relevant one)

- **(a) CAPTURE PENDINGS: SPINE OR HEAP?** ⛔⭐ **RULED s30 (Lon in-chat): SPINE — "attempt SPINE and avoid HEAP at all costs." See the s30 cursor: oracle pins W1–W5, the whack×pending collision, three spine sub-arms.** Original question kept for provenance: Conditional assignment `.` fires at overall match success (p.102 `… REM . *CAPITALS[STATE]`), so its δ0 is live across the entire remaining pattern.  On the spine, **every `.` in any pattern containing any `*P` gets a frame** and the count explodes.  In a heap-allocated pending list, `.` never needs a frame at all.  **This single choice moves more frames than ARBNO does.**  Not yet costed — `bb_match_capture.cpp` (230 lines) unread.
- **(b) EARN-8's delicensing of STATEMENT and FUNCTION** — FUNCTION is the AB activation frame and reaches GOAL-SNOBOL4-RTX and LADDER AB; this is a cross-goal call, not a drive-by.
- **(c) COLLISION ROUTING.**  EARN-4/EARN-7 land in the exact frames **GOAL-SN4-ZETA-MECH** owns the stack-work cursor for, and EARN-2's anchor decision touches **GOAL-RTCC**'s register pool argument.  Coordinate or accept the collision explicitly — do not let a fresh seat discover it mid-fix-loop.

### ⭐ STANDING INSTRUMENT RULE (s29, three convictions same session)

> **Before trusting any A/B or BY-SET board: state what the DEFECTIVE arm would print and confirm it DIFFERS from the correct arm FOR THE CLASS UNDER TEST.** If the arms coincide at the defect site — because both produce the same wrong answer, or because the test asserts a failure that any failure (including total pattern loss) satisfies — the instrument is dark on that class. Three instances s29: (1) vacuous controls on success-expecting subjects; (2) a census blind to vacuous passes (both arms agree by definition); (3) four failure-asserting tests that pass whether the seal works or not. **Supplement with any instrument that can see the mechanism** (`--dump-ir`, poisoned control with PROVEN-OPPOSITE oracle answer, or direct asm diff).

> ⭐ **Corollary:** every BY-SET board must carry a known-PASS control row. A run in which the control fails is measuring the harness and is VOID.

> ⭐ **Corollary:** a test that asserts FAILURE is blind to every defect whose failure mode is also failure.

**RUNWAY:** EARN-0/1/2 are cheap and can open any session.  **EARN-4 and EARN-7 are full-runway only** — the fix loop is the cost center and a half-landed frame regime at end-of-context is a broken tree by construction (this file's standing law).

## ⭐⭐⭐ ABSORBED INTO RBP-EARN — ONE-SHOT AND PASS-THRU GLUE IS LIVE WORK (Lon ruling s29)

**⛔ NOT ARCHIVED. ONE-SHOT and PASS-THRU glue WILL be executed.** ⛔ **What is dead in the rungs below: the T1/T2 deletion targets, the "T-class establishments → 0" seals, and PT-6's ratchet.** Those measured frames-as-debt. Under EARN a frame is not debt — an UNEARNED one is. ⭐ **What is live: the glue protocol itself** — pass-thru adopting caller wires with zero frame, one-shot's `add rsp,K; jmp pred_β`, and the site/blob linkage. ⛔ **RBP is NOT part of this glue** — see the architectural ruling at the top of this file.

## ⛔⭐⭐⭐ LADDER PT — incremental sequence to FLAT PASS-THRU (every rung: killswitch + BY SET gates m3+m4 on the probe suite + xc318 + watermark floors ≥ current + regen ×3 when lower/emitter touched + corpus witnesses with SPITBOL refs)

- [x] DONE — PT-0 (d8bd4ba8)
- [x] DONE — PT-1 (d8bd4ba8)
- [x] DONE — PT-2
- [x] DONE — PT-3
- [ ] **PT-4 · SURVIVING-BLOB PASS-THRU PROTOCOL** ⬅ **s11: THIS IS NOW THE GATE ON EVERYTHING. The DEL-T1 delete was reverted (`c4ef2176`) after its fix-forward was measured net-negative; the blob needs a depth-immune base that is NEITHER rbp NOR rsp before any re-delete.** — blobs still required (stitch segments T3, dynamic refs): α becomes PASS-THRU + a box-own linkage CELL on the spine ({γ, ω, δ0, scanflag} — law-1 "a box a few bytes of its own", NOT a frame, NO pin); interiors admitted to the per-box mechanism (**PL-ZK-5 admission precedent**: a `pat_cells`-class lifts zd_plan's jmp-entry self-decline + the `!flat_pat` guard at emit.cpp:2346); CLASS D record {res,rbp}→{res,pad}; scanfail loses `mov rsp,rbp` (the FORTH fail-chain restores entry depth BY CONSTRUCTION); ω absolute unwind dies.  **PREREQ**: ARBNO/SPAN/BREAK K-conversion inside blob context — COORDINATE WITH MECH, single authority; Lon routes whether this executes here or re-homes.  ⛔ CARVE-ERAD conviction stands (emit.cpp:2914): never cut the region under unconverted readers.
- [ ] **PT-5 · flat_gen PIN census tracking + GLUE-O residual re-measure** — execution likely MECH; this file keeps the product-wide count honest.
- [ ] **PT-6 · PHYSICAL DELETION + RATCHET SEAL** — BLOB-GRANT arm, CLASS D exit spellings, kt region math deleted (label and code same slice); final census: **T-class establishments → 0, keepers unchanged**; the ratchet becomes a standing gate.
- [ ] **PT-7 · g_zctx DELETE — LON'S MECHANISM (s11 in-chat, supersedes the wait-for-full-M-1b form): "storing what you needed as BB locals to the BB_DEFER BB box. There are no GLOBALS needed."**  Two-part conversion, then delete: **(a) SITE STATE → BB_DEFER LOCALS** — linkage {γ, ω, base, scanflag, δ0} become the defer box's OWN locals in the LICENSED statement frame (per-activation + depth-immune by the license; allocated by the normal layout pass, so no aliasing by construction; templates touched ⇒ ARCH-ICON + TEMPLATE-RULES read first, NON-NEGOTIABLE).  **(b) INVARIANT INTERIOR REFS → INLINE** (the s8 enclosure-inlining rung executed): a shared blob's reference to an invariant target folds into the blob body, so NO code inside shared blobs ever needs to find caller state — the circularity (shared code cannot know a caller's slot offset) is dissolved by removing the interior defer, not by answering it.  Then `g_zctx` + every push/pop DELETED, one isolated commit.  **EXIT GATE:** `grep -r g_zctx src/` == 0 · probe+xc BY SET ≥ **32/5 · 82/40** floors BOTH modes · census zero globals AND zero T-class frames.  **RESIDUE:** true recursion only (`dc_recur` class — shared code re-entering itself; manual p.123's stack) stays with MECH M-1b, now the WHOLE of its scope here.  Full-runway seat required — the fix loop is the cost center.
- [ ] **PT-7-ORIG-BRIDGE-FORM (superseded by LON'S MECHANISM above; kept as design record): g_zctx DELETE (Lon commitment, s11-Fable in-chat: "Is this global going to be removed in the future when other things are fixed?" — YES, and this rung is the binding form)** — `g_zctx` is a BRIDGE, not architecture: it exists ONLY because interior depth is not yet restored by construction, so re-entering code cannot find its own carve.  **GATE-IN:** M-1b / interior K-conversion complete — every match-family box's fail/exit path restores entry rsp (the FORTH drain law), `op_flat_disp` valid inside blob context.  **CONVERSION:** every g_zctx consumer (α/β push, γ/ω pop, scanhit/scanfail reads) becomes rsp + emit-time constant; the CLASS-D record's [+8] payload becomes {res,pad} exactly as PT-4's spec already writes; then DELETE the symbol and every push/pop emission, label and code same slice, ONE isolated commit (`git revert` = undo).  **EXIT GATE:** `grep -r g_zctx src/` == 0 · probe+xc BY SET ≥ the `9eb9b4f3` floors (**32/5 · 82/40**) in BOTH modes · census: zero globals AND zero T-class frames — the first state of the product with neither.  Expected side effect: `dc_recur` flips green under the same discipline.

## ⭐⭐⭐ ABSORBED INTO RBP-EARN — LADDER WREG IS LIVE WORK (Lon ruling s29: "We will do R10 and R11")

**⛔ NOT ARCHIVED. The r10/r11 wire mechanism is the DESIGN OF RECORD's wire spelling and WILL be executed.** Read the rungs below for the mechanism, the claim gate, and the sweep census. ⛔ **BUT: every rung below that frames its purpose as "delete the frame" or "T-class → 0" is reversed by EARN.** The wires are carried because glue must move control without a frame — **not** because frames are being eradicated. ⛔ **AND THE `bb_glue_framed_enter` REFERENCES BELOW ARE SUPERSEDED** — RBP now belongs to `x86_alpha`/`x86_omega`.

## ⛔⭐⭐⭐ LADDER WREG — TWO GLOBAL WIRE REGISTERS (rΓ=r10 · rΩ=r11) as dynamic γ/ω for PASS-THRU + ONE-SHOT glue (Lon design s12 in-chat: "TWO GLOBAL REGISTERS as dynamic OMEGA and GAMMA… Is this a Eureka moment!!!" · pick confirmed: "R10 and R11. Perfect. DO the full design.") — SUPERSEDES the NEXT ordering below: WREG-0 first

**PRINCIPLE.** A blob is missing exactly two facts: γ and ω. Deliver them in two reserved registers. Registers dissolve 11-CODE's LAW ("a depth-immune base that is NEITHER rbp NOR rsp") by stepping outside it — depth-immune by nature, and NO OFFSETS, so PT-7's shared-code slot-offset circularity stops existing rather than being solved. The blob needs ZERO receiving code: "NO SHIM" is literal.

### ASSIGNMENT (LOCKED, s12 census evidence)
**rΓ = r10 · rΩ = r11.** Grounds: (1) the ONLY caller-saved pair that is never a SysV argument register — rdi/rsi (549 template uses) and rcx/rdx are args 1–4 of every `rt_*` call, ABI-mandated loads that can never be renamed, disqualified categorically (rcx/rdx additionally falsified: 110 interior uses measured in claws5-match PAT$0); (2) both unowned — REGISTER-LAYOUT's retirement notice says r10/BBREG_DATA is OUT, r11 has no role; r9 is TAKEN (RTCC GVA base), r8 is SCANBASE-entangled; (3) RTCC veneers bracket every `rt_*@PLT` crossing, which also neutralizes the lazy-binding resolver's r11 clobber (belt-and-suspenders: `-Wl,-z,now`). **Fallback if WREG-0 finds an unrenameable r10 use (none can exist by ABI; raw-byte encoders are the only risk): r8+r11, paying the SCANBASE entanglement.** Sweep cost measured: 178 discretionary-scratch renames — bb_call_fn 36 (LIVE mid-match via defers, not theoretical) · xa_flat 21 · bb_match_end 12 (already a TIER-2 routing item — the claim forces a wanted cleanup) · bb_scan_match 8 · bb_func_activate 7 · bb_call_proc_staged 7 · rest small.

### CONVENTION — ONE AUTHORITY (ZW16 mixed-regime conviction binds)
Wires ride r10/r11 in **ALL THREE glue kinds**, one product-wide convention — a per-kind split is exactly the mixed regime ZW16 convicted. FRAMED (`bb_glue_framed_enter`) BANKS the pair into its licensed frame at enter (it has a frame; it may). PASS-THRU and ONE-SHOT carry them live. `bb_glue_pass_wires`' rcx/rdx spelling is REPLACED, not paralleled.

### SPELLINGS (both media; TEXT shown, BIN via the same x86() encoders)
- **Site glue, compile-time-known invariant target:** `lea r10,[rip+site_γ]` · `lea r11,[rip+site_ω]` · `jmp n<first>_…_α` (direct rel32 into the blob's FIRST interior box — no proc_PAT$N_α label exists).
- **Site glue, runtime-resolved defer (`*name` fast arm):** same two `lea`s · fn ptr from the proc table into rax · `jmp rax`. Same wires, same zero-shim.
- **Blob exits:** success = `jmp r10` · fail-after-drain = `jmp r11`. NO unwind — there is no carve to dispose of; `op_zgpop` at the statement remains SOLE release authority.
- **Interior unchanged:** ζ cells (`sub rsp,16`) are box-own bytes, licensed, untouched.

### ⛔ THE ONE LAW — WIRES JOIN MATCH STATE (falsification-hardened: a bare global pair IS g_blob_ctx's single-cell defect in register clothing, `pattern_match.c:624` conviction)
**Rule: every pending cell pushed INSIDE a blob captures {r10,r11} at push; its β-resume restores them before any blob code runs.** Statement-inline cells pay NOTHING. Soundness in one line: the drain pops cells in spine order, so when control crosses from blob B's pendings down into blob A's, A's topmost captured cell restores A's wires before A executes — per-activation-correct by construction; success side is trivially correct (r10 live at the success instant); `dc_recur` inherits the discipline (M-1b save-by-value, single-field form ×2). Cost: +16B and 2 stores per blob-interior pending push, 2 restores per β. s23K's "match state = 4 registers + frame" becomes 6.

### SCAN RECAST — the retry loop is the SITE's ω, not the blob's protocol
The shim's SCANBASE fills (r8→kt−32, r14d→kt−40) fed the in-blob scanfail retry (`mov rsp,rbp` whack + re-attempt). Under WREG the blob knows NOTHING about retry: **an unanchored site chooses ω = its own retry-advance stub**, which reads/writes the attempt cursor in the STATEMENT frame's own slots (licensed, depth-immune, the site's own layout — no shared-code offset problem) and re-runs the glue with the advanced start. Anchored sites choose ω = statement-fail. scanhit's "publish the winning start" head-slot write-back is already statement-side and stays. **The entire in-blob scanhit/scanfail protocol dies with the carve, in the same slice.**

### REGISTRATION + RESUME (same slice as the shim delete)
- `rt_proc_set_fn("PAT$N", …)` registers the FIRST-BOX address (the α label is gone). `rt_proc_set_frame_bytes` → 0, with a consumer audit (who reads frame_bytes for PAT procs?). `set_jmpentry` stays 1.
- **Resume-slot pair dies for PAT blobs:** the `lea rax,[rip+ω]; mov [rbp+240],rax` store AND its `jmp [rbp+240]` readers — armed on PAT$ blobs only via the `g_resumable_callable_active` leak (emit.cpp:2443/3060, 11-CODE's second route). Fix the LEAK in this slice; the wires make the slot redundant for this family. **Witnesses: `dc_nest_bt` · `dc_sib_bt`** (the deep-arrival programs FABLE measured breaking under naive de-arm — they must ride the wires now; if they don't, the deep-arrival class is FRAMED-licensed, not WREG — decide by measurement, record which).

### KILLSWITCH (one switch, five surfaces)
`SCRIP_WREG=0` reverts BYTE-IDENTICAL to legacy: rcx/rdx pass_wires + α shim + carve + zctx push/pop + CLASS-D exits + resume store + registration address. ON is default at WREG-2 landing (PT-1 precedent). The switch gates site glue, shim emission, exit shape, registration, and cell capture TOGETHER — α-with-no-push ⇒ exits-with-no-pop is one mechanism and must flip as one.

### RUNGS
- [~] **WREG-0 · CLAIM + SWEEP (any seat, no behavior change)** — ⬅ **PART-DONE s13 (SCRIP `1d81b015`). GATE + CENSUS LANDED; THE SWEEP ITSELF IS NOT STARTED.**
  - ✅ **Gate `test_gate_wreg_claim.sh` + `scripts/wreg_claim_whitelist.txt` landed** — informational by default, `--strict` hard-fails; matches EVERY spelling (`\br1[01][dwb]?\b`) and through macros, comments stripped. Whitelist EMPTY BY DESIGN (nothing is licensed until WREG-1 creates the glue emitters).
  - ✅ **Exit criterion's no-change half VERIFIED at `1d81b015`, same container:** probe m3 **33/5/1**, fail set `{ab_freturn ab_nret_lvalue ab_redefine dc_recur z4_arbno}` · xc/patterns m3 **82/40** — BOTH reproduce s12b **BY SET**, not merely by count. Full xc fail set now recorded in the s13 cursor below (s12b published counts only; a count is not a set).
  - ⛔ **CENSUS CORRECTED — the design's 178 is raw, not the surface:** 178 raw quoted = **159 code + 19 comment-only**; TRUE surface **234 across 29 files** (all spellings, code only). The 75 delta is bracketed operands + `r10d/r11b`. Per-file, size from the gate not from this file's text: the design's bb_call_fn 36 measures **45**.
  - ⛔⭐ **"BOTH UNOWNED" IS FALSIFIED — r10 IS ALREADY CLAIMED.** `bb_func_activate.cpp:25-26` `AB_TC_REG{,_D}` = `"r10"/"r10d"` when `g_rtcc_on && RTCC_GLOBAL_R9_GVA`, taken by the s8 RTCC-safety fix *because* r10 was then "scratch-tier claimed with NO global assigned" — the very property WREG retires. **DORMANT by default** (`g_rtcc_on = 0`, env `SCRIP_RTCC`); live only at `SCRIP_RTCC=1`. **Unprobed — route, do not guess:** the only remaining safe target is r8, which this ladder flags SCANBASE-entangled, and RULES forbids acquittal by code-reading as firmly as conviction. Full provenance: `FINDING-2026-08-10d-CLAUDE-OP5-WREG-0-*`.
  - ⬜ **STILL OWED:** the **234-site** sweep (templates/emitter only — the 182 RTX asm sites are EXEMPT: the veneer banks the pair, see the DECIDING FACT in the cursor) · raw-byte producer eyeball (`x86_asm.h` internals, `ef_b3` in xa_flat — greps cannot see encoded bytes) · `--strict` green · the manifest (surviving invariant blobs post-PT-2b + witnesses + sbl refs; `sbl` was NOT cloned/built this seat).
- [~] **WREG-1 · SITE GLUE + REGISTRATION** — ⬅ **PART-DONE s15 (SCRIP `1e26e27d`). Killswitch `SCRIP_WREG` BORN (default OFF, md5-byte-identical revert proven). `bb_glue_pass_wires_blob` = `lea r10,γ · lea r11,ω · jmp rax`, NO new encoder needed in either medium. `bb_match_defer` fast arm converted. ⛔ STILL OWED: the OTHER blob entry paths — PT-2's "sole flat_pat entry" premise is FALSIFIED (3 more entries measured in `dc_sib_bt` asm); per-caller blob-vs-proc target census REQUIRED before flip. Registration (`rt_proc_set_fn` first-box address, `frame_bytes`→0) NOT started.**
- [ ] **WREG-1-ORIG (superseded scope note): SITE GLUE + REGISTRATION (full-runway seat, killswitch born here)** — `bb_match_defer` fast arm (emit.cpp:1935) + `emit_jmp_entry_for_patproc` (2914/2925) retarget to first-box label; two `lea`s; runtime-defer `jmp rax` variant; startup registration address + frame_bytes 0. Both media. Both switch arms build and run.
- [~] **WREG-2 · SHIM + CLASS-D + RESUME DELETE** — ⬅ **SUBSTANTIALLY DONE (s19, discharged into this bullet by s20 per s19 CORRECTION 1). LANDED: blob α shim SUPPRESSED (no carve, no `g_zctx` push, no wire stores) + CLASS D exits = `jmp r10`/`jmp r11` (`emit.cpp:2373`/`:2812`/`:2832`). Cumulative s19 ON 64→74 PASS, broken-vs-OFF 36→26, OFF arm md5-byte-identical across every rebuild. ⛔ STILL NOT FLIPPABLE — the residual 26 is 19 SIGSEGV (⇒ WREG-3) + 7 HANG (⇒ WREG-4), s20 measured. The historical s15 text follows for provenance only:** **PART-DONE s15, GATED RED. Under the switch: blob α shim (carve + wire stores + SCANBASE fills + 6-instr `g_zctx` push) SUPPRESSED; CLASS D exits = `jmp r10`/`jmp r11`. ⛔ ON ARM IS 21/17 (vs 33/5 OFF) BECAUSE THREE READER CLASSES SURVIVE THE CUT — `scanhit` + `scanfail` (⇒ WREG-4) and `proc_PAT$N_res`/β + the `[rbp+32]` resume leak (⇒ WREG-3). ⭐ THEREFORE: WREG-4 IS A PREREQUISITE OF WREG-2, NOT A FOLLOW-UP — re-order the ladder. Do NOT flip default-ON until (1) entry census, (2) WREG-4, (3) WREG-3 land.**
- [ ] **WREG-2-ORIG (superseded scope note): SHIM + CLASS-D + RESUME DELETE (same seat/slice as WREG-1)** — blob_act region: carve, wire stores, SCANBASE fills, zctx 6-instr push, resume store — GONE under the switch; exits `jmp r10`/`jmp r11`; zctx pop + γ record + ω absolute unwind — GONE; scanhit/scanfail blocks — GONE (retry is now WREG-4's site stub); `g_resumable_callable_active` leak FIXED. Deliverable: **claws5-match.s regen carries ZERO `proc_PAT$` α labels and ZERO `g_zctx` references** — the exact mess Lon pointed at, gone from the artifact.
- [~] **WREG-3 · SUSPENSION CAPTURE — SLICE 1 LANDED s19 (`afed618`), W-MAP (3) PROPER STILL OWED.** Slice 1 suppressed the resume-slot store + β frame-slot dispatch under the switch (they were corrupting the ADOPTED INVOKER's frame at `[rbp+144]` — the carve that used to contain that offset is gone); ON 68→74, broken 32→26, 6 repaired 0 broken, `rbp+144` refs 7→0. ⛔ **NOT a resume path:** a backtrack into a suspended blob still transfers to FAIL. **W-MAP (3) proper = γ pushes `{res,r10,r11}` (24B→32B aligned) at the deep frontier; `res` restores the pair and falls to β.** ⛔ **`res` MUST NOT take r10/r11 as scratch — it does today (`proc_PAT$N_res` re-pushes `g_zctx` using exactly that pair), DORMANT only because γ is a bare `jmp r10`; W-MAP (3) is the edit that ARMS it.** ⭐ **s20 sizing: expected blast radius is the 19 SIGSEGV members, NOT all 26** — the 7 HANG members are WREG-4's. Original rung text: **(MECH single-authority zone; Lon routes the seat)** — contract from this file: which cells (blob-interior pendings ONLY), layout delta (+16B pair slot), capture at push, restore at β before any blob code. Mechanics (cell allocation, ARBNO iteration interaction, K-conversion residue) are MECH's; the PT-4 PREREQ note (ARBNO/SPAN/BREAK K-conversion in blob context, COORDINATE WITH MECH) still binds interiors.
- [~] **WREG-4 · STATEMENT-SIDE RETRY STUB — SLICE 1 LANDED s19 (`3434697`), REMAINING HALF NOW SIZED BY s20.** Slice 1 cut the scan blocks' null-ctx dereference (the α shim was `g_zctx.cur`'s SOLE WRITER, so both scan blocks opened on a null base; gdb-convicted at `cmpq $0x1,0x8(%rdx)` with `rdx=0`). ON 64→68. ⭐ **s20: the remaining half's blast radius is the 7 HANG members `114 · 130 · 137 · 138 · 144 · 147 · 150` (rc=124, a retry loop that never advances) — NOT the whole residual.** ⛔ **AND RE-DERIVE THE ANCHORED PREDICATE FIRST:** `emit.cpp:2735`'s "anchored patterns are COMPLETE under this arm" is FALSIFIED — `114` is `POS(0)`/`RPOS(0)`-anchored both ends and hangs; p.204 step 6 is about advancing a scan START and this loop advances no start. ⛔ gdb is DARK on this class (never reaches a fault; ASLR falsified as the cause via `setarch -R`) — use a bounded-iteration probe or the 2-way monitor watching cursor advance. Original rung text: unanchored-site ω spelling: attempt-cursor slot in the statement frame, advance+relaunch stub, anchored sites skip. Head-slot write-back audited end-to-end. (Site-emitter work; may land inside WREG-1/2's slice if runway allows.)
- [ ] **WREG-5 · GATE** — probe + xc + broad-336, m3 AND m4, BY SET, same container both arms, BOTH switch states. Floors (≥, s12b measured): probe 33/5 m3 · 33/4 m4 · xc 82/40 m3 · 78/44 m4 · broad 270/66 · 262/68/6. Witness set: pt_inline_1{,_hand,_full} · w_cap_* · dc_nest_bt · dc_sib_bt · dc_recur · `151_pat_arbno_inline_fence_backtrack` (the reverse-MODE34 SEGV — must not regress FURTHER; repairing it is not this rung's burden). Census: T1/T2 establishments → 0, keepers {STATEMENT·FUNCTION·MATCH_BEGIN·FENCE1} unchanged. regen ×3. sbl oracle on every witness.
- [ ] **WREG-6 · SEAL** — ratchet reseeds at the honest census (s12 baseline Σest ≈ 263, xc measured fresh not from stale artifacts); killswitch label + code DELETED same slice once green BOTH media BOTH modes; if these blobs were g_zctx's last consumers, `grep -r g_zctx src/` == 0 discharges PT-7's exit gate in the same commit.

**OPUS WALK NOTES (binding house law, restated so a fresh seat needn't rediscover it):** push per-rung mid-session, never park (RULES ¶1) · MONITOR-FIRST on ANY oracle divergence — never read-and-guess · ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md BEFORE any template/encoder edit, non-negotiable · BY SET always, absolute counts do not transfer across containers (s7 law) · same container both arms · namespace /tmp evidence per seat (11-ENV clobber) · `/home/claude/s12_run.sh` exists (seat-namespaced, ENV-TRAP-(a)-correct runner; promote to scripts/ at will) · a deletion landed at end-of-context is a broken tree by construction — WREG-1/2 want a FRESH seat.

**Relationship:** supersedes PT-4's spine linkage CELL for the wire half (registers replace the cell); dissolves PT-4's depth problem for exits; makes PT-7's `g_zctx` DELETE reachable (these blobs are its remaining consumers); the DEL-T1 re-delete rides WREG-2; WREG-3 is M-1b's shape and `dc_recur` is expected to flip green under it.

**UNRESOLVED BY DESIGN (named so nobody mistakes silence for a decision):** (a) MECH owns cell mechanics and ARBNO-iteration/K-conversion interaction; (b) deep-arrival (`flat_deep_arrival`) blobs — WREG wires or FRAMED license: decided by the dc_nest_bt/dc_sib_bt measurement in WREG-2, recorded either way; (c) frame_bytes consumer audit outcome.

