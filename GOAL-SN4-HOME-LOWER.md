# GOAL-SN4-HOME-LOWER — front-half correctness: LOWER + splice (HOME seat; master = GOAL-SN4-HOME.md)

## ⛔ TOOLING FIRST — `bash /home/claude/SCRIP/scripts/install_system_packages.sh` BEFORE ANY RUNG
One authority, idempotent, prints whether `gdb` is live. **`gdb` is MANDATORY** (MONITOR-FIRST step 2 *is* a gdb breakpoint with a spin/ignore counter). ⛔ **Never hand-run `apt-get install gdb`** — bare apt pulls Recommends `libc-dbg` against a stale index and 404s on a package gdb doesn't need; **that trap cost RBP-EARN seven sessions (s33–s39)**, each re-concluding "no gdb in this container." The script does `apt-get update` first and passes `--no-install-recommends`. A prior cursor claiming gdb is unavailable is VOID — re-test.

**gdb on this tree (s45, measured):** `emit.cpp` compiles into `out/libscrip_rt.so`, NOT into `scrip`. Consequences: (a) `--args` needs the **absolute** path `/home/claude/SCRIP/scrip` or gdb reports "No such file or directory"; (b) `break emit.cpp:NNNN` fails with "No source file named emit.cpp" until the `.so` is loaded — `set breakpoint pending on` does NOT fix this; **use `start` first, then set the breakpoint, then `continue`**; (c) conditional breakpoints on the drive loop work and are the right isolation tool (`break emit.cpp:2702 if i == 13`).

**CHARTER:** every SNOBOL4 wrong-answer whose owner is `lower_snobol4.c`, the ZD depth-staging arithmetic, or the replace/splice arithmetic. **ZERO emitter frame-arm bytes** — that surface is the RBP seat's; this partition is what makes P1 four-way concurrent.

**LAWS THAT BIND HARDEST HERE:** MONITOR-FIRST · never guess an offset, instrument it · every board carries a known-PASS control row · judge BY SET vs BOARD's P0 floors, never by count.

## RUNGS
- [ ] **L-1 · DEFECT A — PRODUCER ELISION (LOWER; convicted by knob `SCRIP_PAT_INLINE=0`).** Why is a use inside a stored composite not an inlining site, and why is the producer elided before that is known? Fix in LOWER. ⛔ **FIXING A ALONE LOOKS LIKE A REGRESSION** — silent rc=0 passes become rc=124 hangs as the mask comes off. **EXPECT the hang count to RISE**; a seat that reverts on that signal reverts a correct fix. Judge BY SET. `SCRIP_PAT_INLINE=0` is a diagnostic discriminator ONLY. *(The "measured s29 §2b" citation this rung carried is a dangling pointer — no s29 section survives. Treat the rise-in-hangs prediction as INHERITED-UNVERIFIED and re-measure rather than assume.)*
- [ ] **L-2 · DEFECT B — THE CONSUMER HANG A WAS MASKING.** Mint the default-arm witness FIRST (unreachable until A lands); then MONITOR-FIRST. Inherited hypothesis: match-time, inside one statement, plausibly unbounded allocation (`[ZHP] heap exhausted` sibling arm) — **plausible, NOT established**; cross-check with HOME-RBX X-4.
- [ ] **L-5 · `test_string` SECOND COMPONENT.** Capture also wrong (`r=[   hello]`) — NOT the splice signature; alternation-arm / post-SPAN cursor suspect, unconvicted. Own witness, own conviction.
- [ ] **L-6 · `fc_walk_range` SECOND-INSTANCE AUDIT (promoted from s43's next-rung list; unstarted).** L-3b's defect #2 was one arm of `fc_walk_range` (`lower_snobol4.c` ~1093) contributing 0 to `fp` for kinds `zd_k` actually carves 16 for. Only the arm with a witness was fixed. The same `switch` has `break`-with-no-`fp` for `IR_MATCH_LIT/LEN/ANY/NOTANY/POS/RPOS/ATP/ASSIGN_SAVE/ASSIGN_COND/ASSIGN_IMM/GOTO`. The `MATCH_*` ones were verified genuinely K=0 — **but `IR_MATCH_ASSIGN_SAVE` is K=16 in `zd_k`** (its own comment says so). Likely live second instance. **Cheap probe:** mint an l3-style witness with a capture (`SPAN('e') . V`) inside a splice statement; see whether the writer/reader miss reproduces.

## ⛔ CLOSED — DO NOT RE-DERIVE, DO NOT RE-SPEND (carried forward from deleted rungs L-0/L-3/L-3b/L-4)
- **L-4/061 is CLOSED (SCRIP `6d804efd`).** `emit.cpp:2725`'s `g_zd_read[_zj] = zd_out[i] - zd_out[_k]` was blind to `IR_MATCH_BEGIN`'s runtime carve (`sub rsp,32` at `bb_match_begin.cpp:77`). Fix: backward-scan from consumer to producer, add 32 for every qualifying run-local `MATCH_BEGIN` crossed (gated by the identical predicate `bb_match_begin.cpp`'s own `hfc()` uses: `fc_head_fp()>=0||fc_tail_head()` under `ZC_FRAME_RSP`+`ZC_PORT_FORTH`), summed across every head found (not just nearest — nested-head arm is UNVERIFIED, no nesting witness exists yet). ⛔ **CORRECTS s45's hand-derived deficit (48=32+16):** that number came from the stale `zd_ud`/`zdh` comment's formula (fields confirmed absent from the tree). The real, gdb-measured deficit is **32 flat**. GATE (own-HEAD A/B, stash-based, all four arms clean): `crosscheck/capture` 8/9→9/9 (061 only, zero collateral) · `crosscheck/patterns` 61/78 both arms byte-identical · `probe/bb` 160-pass, same pre-existing 5-member regression set unmoved · l3 board 14/14 both arms · `test_string` (L-5's own witness) confirmed byte-identical both arms via a true pre-fix worktree build — **L-5 remains genuinely untouched, not incidentally fixed.** Oracle/m3/m4 three-way byte-identical on 061. ⛔ **PROVENANCE:** this diff was found already sitting uncommitted in the working tree at session orientation — no git author, no matching cursor entry. Not derived fresh this session; independently verified via the black-box A/B above before landing. Recorded plainly per the s43 provenance precedent.
- **L-3b is CLOSED; l3 board 13/13 m3.** Two independent defects, both fixed: **(1)** `x86_zop()` regime-2 spelled an already-resolved address as plain `[rsp + N]`, byte-identical to the regime-4 prefix, so `x86_parse` reclassified it and ran `x86_frame_off()` a second time — fix was to spell the `[rsp# + N]` raw escape (SCRIP `3d223c12`). **(2)** `fc_walk_range` contributed 0 to `fp` for `IR_LIT_INTEGER/STRING/REAL`, which `zd_k` universally carves K=16 for — two authorities for one carve decision, the `s22k` spelled-twice class; ONE LINE (SCRIP `93fbe1e2`).
- ⛔ **FALSIFIED, do not inherit:** "POS/RPOS is a third independent defect" (it flipped PASS on defect #2's one-line fix — the slot was right, the *depth the reader assumed* was wrong, which a slot-level check cannot see). Also falsified: "no displacement of any sign can fix it, find the WRITER" — the writer was never missing, and a *principled* displacement was exactly the fix.
- ⛔ **FALSIFIED (s44):** "L-4/061 is the same defect as the ASSIGN_SAVE gap" — `SCRIP_CAP_DIAG` shows that arm sound for this witness and never even reached. Do not re-spend on it for 061 without new evidence. *(Note: this does NOT retire L-6, which is about a different `fc_walk_range` arm on a different witness class.)*
- ⛔ **FALSIFIED (s45):** s43's "L-4 is very likely the same defect as #2, re-measure, it may already be fixed" — re-measured at HEAD across s44 and s45; still broken, and s45 root-caused it to a genuinely separate site (`emit.cpp:2702` ZD staging, not `fc_walk_range`).

## GATES (every rung)
crosscheck/patterns + probe BY SET vs P0 floors, both modes · monitor divergence must MOVE PAST the fix · regen ×3 iff codegen touched (splice arithmetic counts) · FINDING per land mine · cursor move per handoff.

## BOARDS — RUN THEM, NEVER TRANSCRIBE THEM (STALENESS LAW)
```bash
EARN0=/home/claude/corpus/probe/l3     bash scripts/board_earn0_set.sh m3   # the l3 board (13 rows + control)
EARN0=/home/claude/corpus/probe/earn0  bash scripts/board_earn0_set.sh m3   # the earn0 witness floor (L-0)
```
`REPEAT=n` reports a row whose verdict is not constant as **FLAKY** rather than as whichever arm came up first; `earn0_stored_capture` is the known flaky member and a single-shot board misleads by design. *(The hand-pasted shell loop this file used to carry is DELETED — s40 PLAN SCRUTINY item 2, finally actioned s45. The script is generic and takes `EARN0=<dir>`.)*

⛔ **THE m4 COLUMN OF `board_earn0_set.sh` LIES — DO NOT READ IT AS EVIDENCE.** It diffs `--compile`'s stdout (assembly text) against a `.ref` of expected program output; it never assembles, links, or runs, so m4 reads all-FAIL including known-good controls. Fix is ~10 lines: borrow `compile_mode4()` from `scripts/test_broad_corpus_snobol4.sh:30` (`--compile > p.s` · `gcc -c` · `gcc -no-pie … -lscrip_rt` · run). Diagnosed s43, re-confirmed and hand-verified s44. BOARD owns instruments; see STANDING ASKS.

⛔ **AN ORACLE-LESS BOARD PRINTS A PLAUSIBLE ALL-FAIL TABLE.** `x64` is not in the standard three-repo clone a LOWER seat is given. Predicted s40, measured s43, hit again s44, hit again s45 — **four sessions.** `git clone https://github.com/snobol4ever/x64 /home/claude/x64` at orientation, every time. The complementary guard (`[ -x "$SBL" ] || { echo "ORACLE MISSING"; exit 2; }` inside the board scripts) is BOARD's to land and is **still open**.

## LAND MINES
- `x86("comment", …)` → always empty string (`x86_asm.h:1590`). Use `fprintf(stderr,…)`. To correlate a template to emitted bytes, use `--compile`: every node is labelled `n<N>_<kind>_α:`.
- `FR`/`FRQ`/`x86_zop`/`x86_zref` → shared static rotating buffer `b[16][48]`. Capture to `std::string` immediately.
- ⛔ **`[rsp# + N]` in the `.s` does NOT tell you which accessor family produced it.** `ZOPQ(k,w)` and `FRQ(off)` are byte-identical in spelling whenever the staged offset coincides — this cost s44 a wrong mechanism attribution. Check `g_emit.op_zres` at the staging site; do not infer the arm from the emitted text. `SCRIP_ZOP_DIAG` only instruments `x86_zop()`, so its **silence is not evidence** the read went elsewhere.
- `--dump-zeta` is a different coordinate system from the template's `op_off` arithmetic. Do not compare without proving the base.
- Two `case IR_MATCH_END:` exist (~984 `walk_bb_node_inner`, ~1326 `emit_drive`). Sequential, not rival.
- **A rung that says "see X" must name a file or a section a `grep` can find.** The cursor-prune convention guarantees session-number pointers rot; cite `FINDING-*.md` filenames. (s44 lost time to a "see s39b" pointing at a section that never existed.)
- **Witness references get a corpus-relative path, not a bare number.** There are two `061`s: `crosscheck/capture/061_capture_in_arbno.sno` (L-4's) and `crosscheck/patterns/061_pat_fence_fn_seal.sno`.

## ⛔⭐ STANDING ASKS FOR LON (consolidated s40+s43+s44; none actioned yet)
1. **THE ONE INVARIANT (one live session per seat file) HAS NO MECHANICAL ENFORCEMENT — FIVE RECORDED VIOLATIONS** (s34, s35, s38b, s40, s43). Cost is real and now documented from *both* sides: at s42/s43 two seats independently paid for the same root-cause hunt, and commits appeared in trees whose authors never issued them. **Proposed fix, small:** each session writes `SEAT-LIVE-<SEAT>.json` (pid, container, ISO start, heartbeat) at orientation and refuses to start if one exists with a heartbeat < 30 min old; `handoff_status.sh` deletes it. Seconded by s43 and s44. **s44 and s45 both saw ZERO provenance anomalies** — the invariant does hold unenforced sometimes, so judge the guard against a real base rate, but five incidents is the case for it.
2. **The `board_earn0_set.sh` m4 arm.** Diagnosis complete, patch trivial (above). BOARD owns instruments per COLLISION PINS, so LOWER has not landed it. **Say the word and it's a five-minute rung here.**
3. **The `.s` regen scripts print "Committed." even when the commit FAILED** on a missing git identity, leaving staged-but-uncommitted files invisible at handoff. Two cheap fixes: set `git config --local` identity for **corpus** and **`.github`** in the session-start blocks (only SCRIP's is documented), and have the regen scripts check the commit exit status before claiming success.

---
## ⭐ LIVE CURSOR — 2026-08-13 (Claude Sonnet 5). **L-4/061 CLOSED — but the fix was NOT authored this session; it was found already uncommitted in the tree, provenance unknown, and independently verified before landing.**

**Orientation found the working tree dirty.** A fresh three-repo clone (+ x64, which PLAN.md's own step 1b flags as routinely forgotten) should never show `git status` changes. `emit.cpp` had one modified, uncommitted hunk at line ~2725: `git blame` returned "Not Committed Yet." `git diff` showed it was exactly the generalized fix s45's cursor described wanting (backward-scan-and-sum, mirroring `g_zd_zunder`'s pattern for `IR_MATCH_REPLACE`) — already written, already correcting s45's own hand-derived arithmetic in its comment, already citing gdb verification on "a real linked mode-4 binary." No corresponding `.github` cursor entry exists anywhere for it.

**Did not assume either "already fixed, nothing to do" or "trust it blindly."** Ran the full black-box A/B myself, stash-based, before touching anything: baseline (`git stash`, rebuild) reproduces s44/s45's claim exactly — `061` empty output, rc=0. Fixed arm matches oracle (`x64/bin/sbl`, path corrected — it's under `bin/`, an earlier misread on my part, not a real doc/reality gap) and scrip m3/m4, byte-identical `a\na\na`. Four gates run both arms: `crosscheck/capture` (the fix's true target, 9 tests) is the only mover, 8/9→9/9; `crosscheck/patterns` (78 w/ `.ref`), `probe/bb` (166), and the l3 board (14) are all byte-identical by set between arms — zero collateral, including the 5 long-documented pre-existing `probe/bb` regressions (`D12 D13 H31 X01 X10`), unmoved. Also ran the RULES.md step-4 regen (benchmark/feature/demo `.s` artifacts) since codegen was touched — blast radius is large (this is "the ONE authority for every ZD-armed cross-head read in the tree," exactly as its own comment warns), so I separately confirmed the sanctioned demo board (`board_sno15_ident.sh`) is still 2/15 TRI-IDENTICAL (unchanged from the long-documented floor) and that `test_string` — L-5's own open witness — is byte-identical against a true pre-fix worktree build. **L-5 is not incidentally fixed; it remains a separate, still-open defect**, consistent with L-4 and L-5 being tracked as distinct.

**Committed locally (SCRIP `6d804efd`), not pushed** — credential not yet supplied this session. `.github` cursor moved in the same session so the fix can't strand the way inherited-uncommitted work usually does. Full mechanism + gate table in the CLOSED section above; not restating here.

**NOT DONE:** push (any repo) · nested-`MATCH_BEGIN` witness (the `_xh` summing-across-every-head arm is UNVERIFIED, flagged inherited-unverified in the fix's own comment — I did not manufacture a nesting witness to test it) · L-1/L-2/L-6, untouched · `test_case` (crosscheck/library) observed FAILing this session, not investigated — outside L-4's scope, noted only so it isn't rediscovered as new.

**UNBLOCKS:** nothing outside this seat.

---
## ⭐ LIVE CURSOR — 2026-08-12 s45 (Claude Opus 5). **L-4/061 ROOT CAUSE FOUND AND GDB-CONFIRMED. NOT FIXED — the deficit's exact size and origin are established; the general compensation formula is not. NO COMPILER CODE CHANGED.**

**Setup:** standard three-repo clone + hand-cloned `x64` (the four-session oracle trap, again). `install_system_packages.sh` clean, gdb 15.1 live. Built clean at SCRIP `0bbf092b` / corpus `7814057e` — both match s44's recorded HEADs, so no rebase surprises. Set `git config --local` identity in SCRIP, corpus, **and `.github`** (the last is undocumented and blocked my first commit).

**MONITOR re-run fresh** (`PARTICIPANTS="spl scr"`, not transcribed): divergence unchanged from s44. At `X POS(N) 'a' . V` (stmt 3) SPITBOL matches and captures `V='a'`; SCRIP branches straight to the fail label (`LABEL stno=INT=7` = `DONE`). SCRIP m3: empty output, rc=0. Oracle: `a\na\na`.

### ⛔ CORRECTION TO s44's MECHANISM CLAIM (mine to correct; the symptom half was right)
s44 traced the read to `bb_match_pos.cpp`'s `FRQ(_.op_sa+8)` arm, "regime-3/4, not the already-fixed regime-2 path." **That attribution is WRONG.** gdb at the staging site shows `g_emit.op_zres == 1` for this node (`op_sa=192`), so `bb_match_pos.cpp` takes its **`ZOPQ(0,8)` arm** — the ZD/FORTH-cell path — not `FRQ`. The two spellings are **byte-identical** here (both `[rsp#+8]`), which is exactly why the disassembly misled. `SCRIP_ZOP_DIAG` printed nothing for this node not because the read went elsewhere but because that diagnostic only instruments `x86_zop()` and never fires on `x86_zref`. **A silent absence was read as a positive result.** Land mine recorded above.

### ROOT CAUSE (gdb, live process, not hand-derived from `.s` text)
`emit.cpp:2702` is the ONE site staging `g_zd_read[k]`, and it computes the naive `zd_out[i] - zd_out[_k]`. `zd_out` is a **static, pre-drive** tally with no visibility into `IR_MATCH_BEGIN`'s **runtime** carve (`sub rsp,32`, emitted later, per-match). So a ZD-armed node whose operand is produced *before* `MATCH_BEGIN` and consumed *inside* the match misses every runtime carve in between — MATCH_BEGIN's own Kc **and** every un-popped predecessor cell (the non-popping-run design keeps them live).

Measured:
- `zd_out[IR_COERCE_INTEGER(N)] == zd_out[IR_MATCH_BEGIN] == zd_out[IR_MATCH_POS] == 48` — all three identical, which *is* the proof `zd_out` cannot see the carve.
- `g_zd_read[0]` stages `0` ⇒ `ZOPQ(0,8)` spells `[rsp#+8]`.
- Traced through the emitted `.s`: `coerce_integer` writes `N`'s value at `[rsp+24]` relative to its own post-carve rsp; falls through to `match_begin` **without popping**; `match_begin` carves 32 more; the same physical cell is therefore at `[rsp+56]` under the rsp `match_pos` reads.
- **Correct 56 · emitted 8 · deficit exactly 48 = 32 (MATCH_BEGIN) + 16 (un-popped coerce_integer).**
- `fc_head_fp(MATCH_BEGIN)` returns **16**, not 32 or 48 — it counts a fixed-cell WINDOW, not the runtime carve. ⛔ **Not the drop-in fix term; do not assume it is.**

The site's own inline comment ("ZD-5b-LEN cross-head correction") already names this class for `IR_MATCH_LEN` and states the corrected formula in terms of `zd_ud[]`/`zdh` — **`grep` finds those identifiers nowhere in the tree.** Written down, never implemented. `IR_MATCH_POS` shares `LEN`'s staging path (`zd_nops`'s `n_operands` arm, `emit.cpp:2030`) and inherits the identical gap.

### NEXT RUNG (L-4) — the fix, and why a constant is wrong
⛔ **A hardcoded +48 would be wrong.** The deficit is `MATCH_BEGIN`'s actual runtime Kc plus the summed `zd_k()` of every un-popped node between producer and consumer — it varies per witness (32 here; the stale LEN comment cites 256 for its own). **The pattern to adapt already exists and is proven:** `g_zd_zunder` (`emit.cpp:2697`) does exactly this backward-scan-and-sum for `IR_MATCH_REPLACE`. Generalize it at the 2702 staging loop: when the producer is found *before* the run-local `MATCH_BEGIN` and the consumer *after* it, add the backward-scan sum to the naive difference. Verify 061 resolves to 56, then **re-run the full l3 board + broad SNOBOL4 corpus + Icon + Prolog** — 2702 is the ONE authority for every ZD-armed cross-head read in the tree, so a fix here widens far past this witness, for better or worse. Judge BY SET; expect the LEN witness the stale comment describes to flip too.

### Still open, untouched by this session
`corpus/probe/earn0/l4_span_varg_hang.sno` (SPAN(V)) passes m3 clean but **segfaults m4** (rc=139) — a real BOTH-MEDIUM violation, found s44 by hand-running the correct mode-4 sequence. Not monitor-bracketed, not gdb'd. Own witness; may or may not share L-4's root cause. Note the discriminator: SPAN(V)'s dynamic arm is *not* broken the way POS(N)'s is in m3.

### GATES status
No compiler code touched ⇒ no regen, no artifact commits. l3 board not re-run (nothing landed to move it). Diagnosis only; promote to `FINDING-*.md` when the fix lands.

**UNBLOCKS:** nothing outside this seat — L-4's fix touches only `emit.cpp:2702`'s staging loop (depth staging, not frame-arm emission; inside LOWER's charter). The next seat gets a formula shape, not a fresh hunt.

---
## ⭐ LIVE CURSOR — 2026-08-12 s44 (Claude Sonnet 5). **L-3b RE-CONFIRMED FRESH (14/14 incl. control). L-4 measured, not fixed. NO CODE CHANGED.**

Hit the oracle-less trap s43 predicted; fixed the same way (hand-cloned `x64`) and **added `x64` to `PLAN.md`'s session-start clone block** (setup instructions, not the goals table). s43's "PUSH BLOCKED / local only" note resolved benignly — the commits were on `origin`; the note was stale, not evidence of another writer. Zero provenance anomalies this session.

**l3 board re-run fresh: 14/14 PASS m3 at HEAD** — independently reconfirms L-3b.

**L-4:** monitor pinpointed the first divergence at `POS(N)` itself (SPITBOL matches and continues; SCRIP fails) — the match predicate on the dynamic argument is wrong, **not** the capture. `SCRIP_CAP_DIAG` shows the SAVE node resolves `save_active=1 fc_bytes=16`, correctly counted via `fc_geom`'s early grant, so s43's ASSIGN_SAVE hypothesis is falsified for this witness. ⛔ **I retracted, same session, a specific "32-byte offset drift" I had computed by hand from raw `.s` text** — that arithmetic assumed zero depth compensation between producer and consumer, which is false. The symptom was solid; the mechanism was not established. *(s45 note: the retraction was correct, and s45's own mechanism differs again — see the correction block above.)*

**Also found (s44):** the witness **changed failure class** — every prior cursor calls L-4 a hang (`rc=124`); at this HEAD `061` is a silent empty-output `rc=0`, and `l4_span_varg_hang` (named for the hang!) doesn't hang either. That moves the class from the hard-to-instrument bucket (monitor is dark on hangs — no second trace to align) into the easy one. **A seat inheriting "L-4 = the hang class" reaches for the wrong instrument.**

---
---
*History below s44 pruned this session per STALE-ORIENTATION (c) ("newest at top; prune below the last ~3"). Deleted records: s33/s33b, s34–s43 cursors (s43's own broad-336 numbers: m3 264, m4 257, zero new failures either direction — superseded by this session's narrower but cleaner per-suite A/B), the resolved TWO-SEATS alarm, and completed rungs L-0/L-3/L-3b. s43's own provenance episode (two seats independently landing the same fix, both write-ups honest) is the direct precedent this session's L-4 provenance note follows. Everything load-bearing was lifted into the ⛔ CLOSED, LAND MINES, BOARDS, and STANDING ASKS sections above. Full history: `git log GOAL-SN4-HOME-LOWER.md`.*
