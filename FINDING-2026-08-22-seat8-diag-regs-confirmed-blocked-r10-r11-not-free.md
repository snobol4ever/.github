# FINDING 2026-08-22 seat8 — `diag-regs-stmt-and-bb` STEP 1 CHECKED, NOT ASSUMED: BOTH PREREQUISITES ARE GENUINELY OPEN, NOT JUST UNMARKED

**Row:** `diag-regs-stmt-and-bb` (task 3 of 3 in Lon's telemetry ladder: `free-r10 -> free-r11 -> diag-regs-stmt-and-bb`), locked by seat8. Its own brief step 1 is "confirm free-r10 and free-r11 are both marked DONE" before touching any code. This FINDING is that confirmation, done by measurement against the live tree and the postoffice claim records, not by reading FINDING prose and assuming completion.

## 1. METHOD — claim-file byte size is a fast, reliable DONE signal

`s4e_msg.sh done <topic>` appends a literal `DONE\n` line to `$PO/claims/<topic>.claim`; the file otherwise holds only the owning seat's name on one line. So a claim file of `"seatN\n"` (6 bytes for single-digit seats) has **not** been marked done; one with `DONE` appended (11 bytes for the same seat-name length) has. This is cheaper and more reliable than trusting a FINDING's prose, which can describe a "strong first pass" in terms that read as complete to a skimming session.

Measured at time of writing:
- `free-r10.claim` = 6 bytes = `seat3\n` — **no DONE marker.**
- `free-r11.claim` = 6 bytes = `seat4\n` — **no DONE marker.**
- `diag-regs-stmt-and-bb.claim` = 6 bytes = `seat8\n` (this row, freshly locked this session).

## 2. free-r10 — NOT DONE, CONFIRMED BOTH BY GREP AND BY SEAT3'S OWN WORDS

Current HEAD (`SCRIP` `0ff71be8`, seat3's own free-r10 eradication landing) still shows, in `src/templates/` + `src/emitter/` only (the row's own DONE-WHEN scope):
```
grep -rnE '\br10[bwd]?\b' src/templates src/emitter --include=*.cpp --include=*.h | wc -l   → 136  (22 files)
```
This is not a surprise or a contradiction of seat3's FINDING — `FINDING-2026-08-22-seat3-free-r10-census-and-eradication.md` §5 is titled *"WHAT'S LEFT FOR 'ZERO IN TEMPLATES AND EMITTER'"* and lists ~332 SCRATCH-class sites (`bb_call_fn.cpp` 54, the `bb_scan_*.cpp` family 36, others) plus genuine class-(c) survivors (the `emit.cpp:2725`/`:3033` frameless-suspend cache, flagged HIGH-RISK and explicitly "left for the next rung") as **not yet moved**. Seat3's own BOARD.md line at 18:11 says it outright: *"Row NOT done -- DONE-WHEN wants zero in templates/emitter, this is a strong first pass not the finish."* The eradication that landed (34 DEAD-WIRE sites, `test_gate_sno_pat_reg.sh` RED→GREEN) is real, verified, valuable work — and it is the DEAD-WIRE sub-class only, not the row.

## 3. free-r11 — NOT DONE, STILL EARLIER THAN free-r10

- seat6 ran the STEP 1 census honestly (using `test_gate_wreg_claim.sh --strict`, not naive grep), found real unlicensed debt roughly double HQ's original estimate (248 occ/25 files in templates+emitter alone, plus 225 more in RTX hand-asm `.S` files never in scope), asked `q-free-r11`, and was cancelled before landing any code (`FINDING-2026-08-22-s255-...`). Its board line: *"released free-r11 unclaimed, no code changes, q-free-r11 still open."*
- `q-free-r11` is confirmed **still open** in HQ's queue as of this writing — no ruling has landed.
- The claim is currently held by **seat4** (`free-r11.claim` = `seat4\n`, no DONE), and seat4's local tree shows 1 dirty file (`s4e_msg.sh fleet` output) — consistent with live, in-progress work, not an abandoned claim. **No FINDING or board line from seat4 about free-r11 exists yet.** I did not touch seat4's claim, tree, or files — a live claim from another seat is exactly the case RULES.md's claim-gate mechanism exists to protect, and touching it would risk duplicate/conflicting work on the same register-freeing effort seat4 may already be mid-flight on.
- Independent grep confirms real residual debt regardless of seat4's in-flight state: `\br11[bwd]?\b` in `src/templates`+`src/emitter` = **91 sites, 9 files**, at current HEAD.

## 4. WHY THIS ROW STAYS BLOCKED RATHER THAN PROCEEDING NON-BLOCKING

RULES.md / the s255 incident finding establish non-blocking-by-default: a wrong number or a wider-than-expected census is a finding to record, not a reason to stop. This case is different in kind, and the brief says so explicitly: *"⛔ BLOCKED until free-r10 AND free-r11 are both DONE; do not start early, a half-freed register is the s194 collision."* `FINDING-2026-08-20-s194b`/`s194c` is the named precedent — the RTCC bank and the old register-wire convention collided over the same two registers, and it cost Milestone 1. Writing new code today that plants `mov r10, imm32` at every `IR_STATEMENT_BEGIN` and loads r11 with a BB node id at every α/β — atop 136+91=227 residual, only-partially-classified r10/r11 sites across 31 files, several of them (the frameless-suspend cache, the RTCC call-stub, the RTCC self-restore idiom) **already using those exact two registers for other live purposes** — is exactly the failure mode the brief names, not a hypothetical one. This is the rare, legitimate BLOCKING case (unsafe either way the open question resolves), not the common case the non-blocking default is aimed at.

## 5. WHAT THIS SESSION DID AND DID NOT DO

- **No source file was touched.** No commits to `SCRIP` or `corpus`.
- Read `ARCH-SNOBOL4-RTX.md`'s register contract, `ARCH-ICON.md`, `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (BB-codegen mandatory reading, since this row's eventual work is template/`x86_asm.h` codegen), and `GOAL-SNOBOL4-100.md`'s LIVE CURSOR per session-start protocol — all done, all still applicable when the row unblocks.
- Verified the actual state of both prerequisite rows by measurement (this document) rather than by trusting FINDING prose or claim-file presence alone.
- This FINDING plus a `q-diag-regs-stmt-and-bb` ask to HQ are the row's output this session.

## 6. RECOMMENDATION FOR WHOEVER RE-FIRES THIS ROW (including a future seat8)

Re-check both claim files' byte size before trusting anything cached in context — `wc -c $PO/claims/free-r10.claim $PO/claims/free-r11.claim`; 6 bytes each means still open. If both eventually show the `DONE` line, re-run the `\br1[01][bwd]?\b` grep over `src/templates`+`src/emitter` once more before writing any telemetry code — a DONE marker is a claim, not a substitute for looking.
