# ARCH-PASSTHRU — THE ONE CROSSING LAW BETWEEN BB GRAPHS (Lon 2026-08-20 in-chat, PRIORITY ONE)

**Lon, verbatim in substance:** *"Get a reliable way to go between BB's. Each BB graph has TWO continuations. Moving between them should be simply a matter of switching these TWO and switching back as they move. … You have EVERY SINGLE BB have a RESULT, so that you are forced to put it somewhere, because when it is needed that will be a problem caught ahead of time. Now some BB results are in REGISTERS."*

## THE LAW
1. **TWO CONTINUATIONS, ONE DISCIPLINE.** Every BB graph's external contract is the pair {γ-continuation, ω-continuation} riding the r10/r11 wires. EVERY crossing between graphs = bank the caller's pair, install the callee-relative pair, run; the callee's γ/ω restore the banked pair. Nothing else may carry cross-graph linkage: no pushed landing pads, no flat depth assumptions leaking across the seam, no per-road glue.
2. **THE PAIR IS ACTIVATION STATE, NOT A CALL ARTIFACT.** Graphs suspend (γ) and are re-entered (β). Whatever holds the suspension holds the banked pair, and β re-entry reinstalls it — "switching back as they move" holds in BOTH directions. Existence proof already in-tree: the PAT$ blob head (`blob_frame_bytes`: saved rbp @+0, γ wire r10 @−8, ω wire r11 @−16).
3a. **⛔ THE RESULT LAW, STABILIZATION FORM (Lon 2026-08-20 in-chat, amending 3): EVERY BB ALLOCATES A RESULT SLOT — uniformly, register-resident results included — TEMPORARY UNTIL STABILIZED.** The point is the calculation: uniform allocation makes slot number = box index and carve = n_boxes × granule, so the offset math has NO per-box cases and NO candidacy — the registry's candidate scans (the last admission machinery) go dead. A register result may stay CACHED in its register; the cell exists regardless, so a consumer can never find no home ("caught ahead of time"). Frame bloat is accepted scaffolding; after the pass-thru ladder stabilizes, cells un-allocate box-by-box, each with its own measurement — never wholesale, never by filter.
3. **⛔ THE RESULT LAW (Lon 2026-08-20).** EVERY BB has a RESULT and a DECLARED HOME for it (a register or a cell named by the lattice) — declared at compile time, uniformly, so a consumer can never discover a missing result at runtime. The s174 operand-slot flat read (needle read resolving to caller territory inside an ALT arm) is the conviction: a result whose home was an assumption. Register-resident results are fine — the law is that the home is DECLARED, not that it is memory. Enforcement joins the ZDP lattice (the one per-box ζ-semantics authority, `zeta_depth.c`) and the ZDP/ZSM/canary instruments check declared-vs-actual.

## THE FOUR PROTOCOLS IN THE TREE TODAY (the disease, measured)
1. **Blob crossing** — CONFORMANT (banks the pair in its head; the model).
2. **Pushed-pair landing** (`bb_call_proc_staged` slim/legacy: `[rsp+0]=γ [rsp+8]=ω`) — B1c's root cause (s168), R1b's sibling (fragment thunk landing, s173).
3. **DTP record road** (DEFER β = `jmp qword ptr [rsp]`) — record-held continuation.
4. **TINY shim** — third call shape with its own admission/exits.
Every M1 wall on the 2026-08 board is a mismatch between these. The cure is ONE law, proven bottom-up — not eight seats curing faces.

## THE LADDER — NINE CLASSES (Lon 2026-08-20 in-chat, SUPERSEDES the first 5-level sketch; every class exercised through BOTH `*PATTERN_var` AND `PATTERN_func()` — "the whole problem derives from those two")
| class | boxes | state character |
|---|---|---|
| **(0)** | POS · RPOS · LITERAL · LEN · ANY · NOTANY | ZERO-local; result = r14d; β reverses arithmetically or is a pure predicate |
| **(1)** | TAB · RTAB · REM · BREAK · SPAN | one 4–8B cell today, ALL of it the entry-cursor β-restore (+ SPAN's loop counter); semantic minimum ~0 once the β convention is fixed (see RESULT GRID note) |
| **(2)** | ARB · BAL · BREAKX | GENUINE retry state — extending-β generators (BREAKX reclassified here from the leaf family: its β re-enters, unlike BREAK) |
| **(3)** | ALT · ARBNO | choice/iteration records (32B rsp record · 16B registry slot per activation) |
| **(4)** | CAPTURE (SAVE/COND/IMM) | the RESULT-law hot case: result lands in a VARIABLE's cell, not a register |
| **(5)** | FENCE0 · FENCE1 | cut semantics across graphs (0B · 16B watermark) |
| **(6)** | EVAL | runtime fragment compile + crossing (the B1c/retain-budget territory) |
| **(7)** | CODE | runtime statement-graph compile + crossing |
| **(8)** | MEGA | ARBNO/DEFER/EVAL/CODE stacked combinations — the beauty grammar shape |
Witness home: `corpus/probe/passthru/pt<class>_*`; every class × {var-road, func-road} × 1–3 layers × BOTH directions (γ forward, β retreat back through every seam). Gate: the class's whole witness family oracle-identical BOTH modes before the next class opens.

## THE RESULT GRID (measured at HEAD 2026-08-20, HQ; the RESULT-law baseline)
r13 = subject base · r15d = subject length · **r14d = cursor delta, THE result register of the matcher family** · r10/r11 = the two continuations.
POS/RPOS/LIT/LEN/ANY/NOTANY: 0 locals, result r14d. TAB/RTAB/REM/BREAK: 4B = entry-cursor β-restore ONLY. SPAN(lit): 8B (loop ctr + entry). SPAN(*expr): 16B (needle {ptr,len} pair — ABI forces the fill call's out-params into memory). BREAKX 8B / ARB 8B / BAL 12B: genuine retry state. ARBNO 16B slot; ALT 32B rsp record; CAPTURE 16B slot (result → variable cell); FENCE0 0; FENCE1 16B watermark; DEFER = the crossing state itself (DTP + resume + banked pair).
**⛔ THE β CONVENTION DECISION (class-1's rung must fix it):** today the machine mixes two β disciplines — relative boxes REVERSE r14 arithmetically, absolute movers RESTORE from their cell. A non-restoring TAB β chaining into a reversing LIT β reverses from the wrong value. Class-1's zero-local form requires the ONE law: every β re-derives r14 from its own knowledge, absolutely — then the four 4B cells vanish and class 1 collapses into class 0.

## STATUS
- 2026-08-20 HQ (Fable): file minted; L1 witness family + HEAD baseline census this session (see GOAL-SNOBOL4-100 cursor + FINDING when pushed). Delegation suspended — HQ executes.
