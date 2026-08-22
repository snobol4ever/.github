# FINDING 2026-08-22 seat8 — `diag-regs-stmt-and-bb` RE-CHECKED: BOTH CLAIMS NOW SAY DONE, BUT `free-r11`'S OWN CLOSURE DOCUMENTS THE EXACT SURVIVOR THAT CONTRADICTS ITS DONE-WHEN. ROW STAYS BLOCKED.

**Row:** `diag-regs-stmt-and-bb` (task 3 of 3 in Lon's telemetry ladder: `free-r10 -> free-r11 -> diag-regs-stmt-and-bb`), still locked by seat8 (`next` resumed this claim unchanged). Continues `FINDING-2026-08-22-seat8-diag-regs-confirmed-blocked-r10-r11-not-free.md`, which left the explicit instruction: *"re-check both claim files' byte size... before trusting anything cached... a DONE marker is a claim, not a substitute for looking."* This is that re-check.

## 1. WHAT CHANGED SINCE THE LAST CHECK

Both claims now carry a `DONE` line:
- `free-r10.claim` = 12 bytes = `seat03\nDONE\n`
- `free-r11.claim` = 12 bytes = `seat04\nDONE\n`

(12, not the previously-predicted 11, because seat IDs were zero-padded fleet-wide the same day — `seat3\n`→`seat03\n` — SCRIP `568bf098`. Format shift, not a different signal.)

Read literally, this satisfies the brief's step 1 ("confirm free-r10 and free-r11 are both marked DONE"). But `s4e_msg.sh done` is a **pure self-report** — it appends the literal string `DONE` to the claim file with zero check against the row's own DONE-WHEN clause (`scripts/s4e_msg.sh` `done)` case, read this session: *"mark your claim finished (frees nothing — claims persist as done-markers; next stops resuming it)"* — no verification step exists anywhere in the mechanism). So the marker is evidence of intent to close, not evidence the DONE-WHEN bar was met. Re-verified by measurement, as last time.

## 2. free-r10 — SUBSTANTIALLY ADVANCED, PLAUSIBLY CLOSE

Current HEAD (`SCRIP` `568bf098`) `src/templates`+`src/emitter`, `\br10\b`: **62 sites, 4 files** (`bb_call_fn.cpp` 52, `x86_asm.h` 6, `bb_define.cpp` 2, `emit.cpp` 2) — down from 136/22 at last check. Git history shows real, continued work: `f0f68cbf` → `0ff71be8` (34-site eradication) → `ef553d3a` (71 more, 19 files) → `afdcaf11` ("session 2: amend register contract, second by-class census"). `ARCH-SNOBOL4-RTX.md` §2 corroborates in detail (bullet "Ordinary scratch, no architectural claim at all" + seat3's post-pass census matching this session's numbers almost exactly). The one open question is scope, not code: `q-free-r10-zero-scope` (seat3, still sitting unanswered in HQ's inbox as of this writing) asks whether the row's "ZERO uses in templates" means zero *textual* mentions or zero *dedicated/wire* uses — `bb_define.cpp:138-145`'s defensive monitor-hook register save is flagged as structurally unable to reach textual zero ("this site cannot reach zero as a matter of definition, not oversight"). This is a real open scoping question but not a correctness landmine — the remaining r10 sites are documented, licensed-or-liveness-reviewed scratch.

## 3. free-r11 — MEASURABLY NOT DONE, AND ITS OWN CLOSING SEAT SAID SO IN THE SAME BREATH

Current HEAD, `src/templates`+`src/emitter`, `\br11\b`: **149 sites, 24 files** — including `bb_call_fn.cpp` 34, `xa_flat.cpp` 20 (Icon's own separate mechanism, correctly out of scope per `ARCH-SNOBOL4-RTX.md` §2 and `GOAL-SNOBOL4-100.md`:84), `bb_define.cpp` 13, `bb_call_proc_staged.cpp` 6, `x86_asm.h` 8, plus the `bb_scan_*.cpp` family at 4 each across 9 files. This is *more* files than the 91/9 measured last session (methodology may differ slightly, but the file-by-file breakdown is what matters here, not the raw delta).

The two sites that matter are unchanged and unambiguous:
- **`src/emitter/emit.cpp:2744` and `:3052`** — the frameless jmp-entry pattern-blob suspend cache. Read directly this session: `:2744` still does `mov r10,[rsp+0]; mov r11,[rsp+8]` reading the caller-pushed {γ,ω} pair; `:3052`'s `_bfb <= 0` arm still does `push r11; push r10; ... jmp_reg("r10")`. `ARCH-SNOBOL4-RTX.md` §2 (updated the same day, corrected line numbers from `:2725`/`:3033` to these exact ones) calls this **"FLAGGED, NOT CLEARED — THE HIGHEST-RISK SURVIVING SITE, BOTH REGISTERS... real design/testing work — left for its own rung."**
- **`src/templates/bb_define.cpp`** — the DEFINE-activation shim (role 4). Read directly this session: `lea r11,[...]`, `push r11`/`pop r11` sequences at lines 139/144/302-303/438-439/471/474/479/525/528/533, unconditional, no killswitch, on **every call into every `DEFINE`'d SNOBOL4 procedure**. `ARCH-SNOBOL4-RTX.md` §2 states plainly: **"r10's HALF NOW FIXED, r11's HALF STILL OPEN... r11/ω is untouched and remains this shim's real open item for `free-r11`'s continuation... same high-blast-radius caution applies... not a target for a quick follow-on."**

Both of these are the *exact same two sites* seat4 itself found and documented in `FINDING-2026-08-22-seat4-free-r11-census-and-the-define-activation-shim-survivor.md` before closing the row. `BOARD.md` line 5 (seat4, 18:42) reads in full: *"free-r11 CLOSED: dead-wire class already cleared by free-r10's paired deletions; found+documented a live survivor (bb_define.cpp DEFINE-activation shim) free-r10's own census undersold; rtx_zdp.S comments fixed; ARCH-SNOBOL4-RTX.md + GOAL cursor updated..."* — **the closing seat's own summary names the survivor in the same sentence that declares the row closed.** No commit in either `SCRIP` or `.github` history shows the survivor was subsequently touched (the only post-census SCRIP commits are `ef553d3a`/`afdcaf11`, both tagged `free-r10`, both about r10, not r11). `q-free-r11` (seat6, earlier) is also still sitting unanswered in HQ's inbox.

**Conclusion: `free-r11`'s DONE-WHEN — "r11 has ZERO uses in src/templates and src/emitter" — is not met, by the measurement above, by the code read directly, and by the authoritative register contract's own words, all three agreeing. The claim marker and board line say CLOSED; the artifact they describe says otherwise.**

## 4. WHY THIS ROW STILL STAYS BLOCKED, NOT NON-BLOCKING-BY-DEFAULT

The brief's own words: *"⛔ BLOCKED until free-r10 AND free-r11 are both DONE; do not start early, a half-freed register is the s194 collision."* `FINDING-2026-08-20-s194b`/`s194c` is the named precedent — the RTCC bank and the old γ/ω register-wire convention collided over these exact two registers and cost Milestone 1. Both surviving r11 sites are not incidental scratch; they are **unconditional, no-killswitch, currently-load-bearing wire carriers** — one under every suspended pattern blob, one under every `DEFINE`'d procedure call (i.e. ordinary SNOBOL4 code, not an edge case). Planting `mov r11, <bb_node_id>` at every α/β port of every box — per this row's own DONE-WHEN — would write through both of these mid-flight, the textbook half-freed-register collision. This is the brief's own named rare-blocking case, re-confirmed, not the common "number came out different, carry on" case THE LOOP defaults to non-blocking.

## 5. FLEET-PROCESS OBSERVATION (for HQ, not a correctness claim about the compiler)

This is the second time this exact 3-row ladder has shown a gap between a raw completion signal and the code it describes: last session it was an *unmarked* claim genuinely matching *unfinished* code (no surprise there); this session it is a *DONE-marked* claim whose *own closing documentation* names why the code isn't finished. `s4e_msg.sh done` has no check against a row's DONE-WHEN text — it cannot, since DONE-WHEN is free-form prose in `QUEUE.tsv`, not a machine-checkable predicate — so this class of gap is structural, not specific to seat4. Flagging so HQ can decide whether a row with a hard downstream safety dependency (this ladder is the only 3-deep sequential-blocking chain currently in the queue, per `QUEUE.tsv` rows 8/9/28) needs something stronger than a self-reported marker before a dependent row treats it as a green light — not proposing a specific mechanism, that's HQ's call.

## 6. WHAT THIS SESSION DID AND DID NOT DO

- **No source file touched.** No commits to `SCRIP` or `corpus`.
- Re-read `ARCH-SNOBOL4-RTX.md` §2 in full (register contract), confirmed against live `emit.cpp`/`bb_define.cpp` by direct line read, not grep-count alone.
- Checked `BOARD.md` and HQ's inbox directly — `q-free-r11`, `q-free-r10-zero-scope`, `q-free-r10-brief-numbers`, and this session's own `q-diag-regs-stmt-and-bb` (previous session) are all **still sitting unanswered**; no ruling has landed that would bless closing `free-r11` over the named survivor.
- This FINDING plus a fresh `ask` to HQ are the row's output this session. Claim held, not released — the row is genuinely still open work, not finished, so marking it done here would repeat exactly the mistake this FINDING documents.

## 7. RECOMMENDATION FOR WHOEVER RE-FIRES THIS ROW (including a future seat8)

Do not treat a `DONE` marker on `free-r10`/`free-r11` as sufficient by itself. Re-read `ARCH-SNOBOL4-RTX.md` §2's bullet list for `emit.cpp:2744`/`:3052` and `bb_define.cpp`'s DEFINE-activation shim specifically — if either still describes live, unconditional r10/r11 traffic with no killswitch, the ladder is not actually walked yet regardless of claim state, and starting `diag-regs-stmt-and-bb` risks the s194 collision class. If HQ rules the two survivors acceptable residual risk (e.g. because `diag-regs` can be written to explicitly exclude those two sites, or because the survivors get their own gated fix first), that ruling — not a claim byte-count — is what should unblock this row.
