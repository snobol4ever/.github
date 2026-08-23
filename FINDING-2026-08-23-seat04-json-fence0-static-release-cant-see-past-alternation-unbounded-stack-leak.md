# FINDING — seat04: bare `FENCE` never releases backtrack state when it follows an ALTERNATE/ARBNO, and citm_catalog.json exhausts the C stack because of it — ROOT-CAUSED, synthetic witness minted, NOT FIXED (needs a shared-allocator change, out of this row's scope)

**Date:** 2026-08-23 · **Seat:** seat04 (`/home/claude04`) · **Found while working:** THE LOOP queue row `json-alternate-af-spin` — building the row's own DONE-WHEN (`json.sno < citm_catalog.json`) surfaced this as a **third, independent** blocker, on top of the row's own af-spin and the (now-fixed, see below) jstring-escape bug.
**Status:** ROOT-CAUSED, gdb-verified to the exact instruction and the exact missing release. **NOT FIXED.** A safe fix requires extending the shared frame-slot allocator (`frame_slot_is_candidate`/`blob_frame_bytes`) that also backs `blob_choice_rbp_scan` — the very mechanism `json-alternate-af-spin`'s own HARD CONSTRAINT says must not be casually touched. This needs its own dedicated, fully-verified session, not a same-row patch.
**Relationship to sibling rows:** independent of `json-alternate-af-spin` (the comma-spin) and independent of `jstring-escape-dcap-pump-segv` (fixed today, SCRIP `2037a02f`, seat09) — all three happen to gate the same DONE-WHEN (`json.sno` on `citm_catalog.json`) but are three different mechanisms. Do not merge fixes across them.

---

## 1. Symptom

With today's fixes in place (`SCRIP` HEAD `2037a02f`, which cures both the af-spin's *visible* hang — see §7 below — and the jstring-escape corruption), `citm_catalog.json` (1,727,204 bytes, the row's own DONE-WHEN target) still fails:

```
R="$PWD"; cd "$R/corpus/programs/snobol4/demo"
timeout 60 "$R/SCRIP/scrip" json.sno < citm_catalog.json > /tmp/citm.got 2>&1
# → Segmentation fault, rc=139, wall time ~1.2s (NOT a timeout — this is fast and deterministic)
```

Not a hang, not slow — a fast, deterministic SIGSEGV. `[ -s /tmp/citm.got ]` is true (the crash writes `input bytes=1727204` before dying) but the exit code fails the row's `&&`-chained DONE-WHEN regardless.

## 2. Isolated: it's the `performances` section, and it's a C-stack overflow

Bisecting `citm_catalog.json` by top-level key (each of the 11 keys fed to `json.sno` alone): only `performances` (243 items, 499KB) crashes; the other 10 keys (`events` 184 members, `seatCategoryNames` 64 members, etc.) all pass clean. Bisecting `performances` by item count: a sharp, one-item cliff, not a gradual slowdown — the exact count moved between two same-session rebuilds here (233-pass/234-crash before an unrelated activation-frame allocation fix landed mid-session, 223-pass/224-crash after it — see §6's caveat), which is itself useful evidence: the threshold tracks total retained-and-unreleased bytes, and any change to per-node stack cost shifts it, consistent with §3's mechanism and inconsistent with any theory involving a fixed, unrelated resource limit.

`gdb run` + `bt` on the crash:
```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff416716f in c_rt_defer_close (cur_delta=<error reading variable: Cannot access memory at address 0x7ffffbffef9c>)
    at src/runtime/pattern_match.c:925
925	{
RSP=0x7ffffbffef90
#0  c_rt_defer_close (...) at pattern_match.c:925
#1  rt_patv_defer_run_all (hv=0x7fffae83b100, i=1, fb="PAT$6$V1", cur_delta=1513103) at pattern_match.c:986
#2  0x00007fffee013127 in ?? ()      <- unwinder gives up: JIT'd box-threaded code, no CFI
...
```
`RSP=0x7ffffbffef90` is **inside the guard page below `[stack]`** — `/proc/<pid>/maps` shows `[stack]` starting at `0x7ffffbfff000`; the crashing write lands `0x70`–`0x10` bytes *below* that boundary depending on which exact callee's prologue happens to be the one that finally overruns it (I measured this at three slightly different function entries — `patv_slot`, `rt_dfx_push`, `c_rt_defer_close` — across otherwise-identical repeated runs of the same input; they're all in the same small cluster of deferred-pattern-value helpers in `pattern_match.c`, and which one is "last" is immaterial to the mechanism). **This is a genuine stack-pointer exhaustion**, not a wild-pointer crash: `g_dfx_top=1`, `g_dcf_top=0`, `g_cas_used=393216` of an 8MB island at the time of the crash (checked via gdb `print`) — none of the C-side bookkeeping arrays are anywhere near their own bounds-checked limits (those `abort()` cleanly with `rt_cas: ... overflow` if hit; this crash is not that). The exhaustion is real x86 `rsp`.

**What does NOT reproduce it, ruling out the obvious hypotheses (all tested against the standalone `json.sno` binary, `--compile`+`gcc -g` linked against `libscrip_rt.so`):**
| shape | tested up to | result |
|---|---|---|
| flat array of integers, `[0,1,2,...]` | 50,000 elements | clean |
| linearly nested arrays, `[[[...[1]...]]]` | 2,000 levels deep | clean |
| flat array of 1-member objects, `[{"a":1},...]` | 1,600 objects | clean |
| array of objects each with a nested 2-elem array | 3,200 objects | clean |
| **synthetic replica of a real `performances[i]` record** (9 members; `prices`: 2 items; `seatCategories`: 4 items × `areas`: 10 items each — matched to the real file's measured average branching, `performances[:234]` = 33,176 total JSON nodes, 3.69 seatCategories/perf, 9.58 areas/seatCategory) | **224 records** (committed threshold, HEAD `2037a02f`) | **rc=139, SIGSEGV** — same order of magnitude as the real data's own threshold |

So it isn't array *length*, isn't nesting *depth*, and isn't object *count* in isolation — it's the accumulated cost of many **container-typed** (object/array) nodes whose own bodies exercise real ARBNO iteration (2+ members/elements), stacked across the whole document. Neither pure width nor pure depth alone gets there in the ranges tested; the real branching factor (moderate depth × moderate fan-out at each level, repeated a couple hundred times) does. **A fully synthetic, self-contained, oracle-independent witness is committed** at `corpus/probe/json_fence0_leak/` (see §6) — no dependency on `citm_catalog.json`'s actual content.

## 3. Root cause: `FENCE`'s static stack-release computation gives up silently when the fence is preceded by an ALTERNATE/ARBNO, and bills 0

`jarray`/`jobject` both end with a bare, zero-argument `FENCE` (`json.sno`): `'[' (... | ws) ']' (epsilon . *earr()) FENCE`. This compiles to `IR_MATCH_FENCE0`, `src/templates/bb_match_fence0.cpp`:
```c
int rel = _.op_fence0_release;
... + x86_alpha() + IF(rel > 0, x86("add", "rsp", rel)) + x86_gamma() + x86_beta() + x86_omega();
```
`rel` — the number of bytes to whack off `rsp` on success, releasing whatever backtrack state accumulated since some earlier point — is a **compile-time constant**, computed once by `fence0_release_bytes()` (`src/emitter/emit.cpp:713-734`). That function walks *backward* from the FENCE node along the box graph's `γ` (success) chain (`zd_chase`, which only follows `IR_GOTO` — it has no notion of a loop-back or a multi-arm join), accumulating `zd_k(m)` for each simple, statically-sized predecessor (`SPAN`/`BREAK`/`TAB`/etc.), and **explicitly `break`s the moment it meets `IR_MATCH_ALTERNATE`, `IR_MATCH_ARBNO`, `IR_MATCH_FENCE1`, `IR_MATCH_DEFER`, `IR_MATCH_VALUE`, `IR_CALL`, `IR_CALL_VALUE`, `IR_DISJUNCTION`, or `IR_MATCH_ABORT`** — i.e. any predecessor whose own stack footprint is data-dependent rather than a fixed constant.

For `jarray`/`jobject`, the FENCE's immediate predecessor chain is `']' ← (elements ARBNO(...) | ws) [IR_MATCH_ALTERNATE]` — so the walk should stop at the alternation and bill whatever it's already accumulated (near-zero, since only the closing-bracket literal sits between). **But it doesn't even get that far.** Confirmed with the function's own built-in diagnostic (`SCRIP_FZ_DIAG=1`) on the crashing witness:
```
[FZ-DIAG] fence 0x2b39a410 not on any MATCH_BEGIN forward chain -- bill 0
```
**Every one of json.sno's four bare-FENCE sites hits this exact branch, always.** The *first* loop in `fence0_release_bytes` — which tries to locate the fence node at all, by chasing `γ` forward from every `IR_MATCH_BEGIN` in the compilation unit — never reaches it. `zd_chase`'s "follow the single `γ` pointer" traversal is built for a straight-line peephole scan; it cannot represent an `IR_MATCH_ALTERNATE`'s join (multiple arms converging on one continuation) or an `IR_MATCH_ARBNO`'s loop-back, so a FENCE reachable only *through* one of those structures is invisible to it. The function's fallback for "can't find it" and "found it but hit a dynamic predecessor" is the **same value: 0**, silently — `bb_match_fence0.cpp`'s own comment even documents this as intentional ("nothing releasable here"), which is the right conservative default *for a genuinely-zero case* and the wrong one for an *unprovable* case.

**Net effect: the trailing FENCE on every `jarray`/`jobject` emits zero release code.** It performs its logical job (preventing SNOBOL4-level backtracking past this point) but does nothing to the physical stack. Every array/object's own multi-element ARBNO iteration — and the transient trial-and-error of `jvalue`'s 7-arm alternation tried for every element inside it — leaves real, uncollected `sub rsp,N` state behind on every commit, and because the enclosing FENCE never whacks it, that state survives for the **entire remaining duration of the top-level match**, accumulating across every sibling array/object in the document. `performances[i]`'s own nested `prices`/`seatCategories`/`areas` arrays each contribute their own uncollected slice; multiplied across the whole array, the accumulation walks `rsp` off the bottom of the stack.

This is why no corpus witness caught it before: every existing test program is too small (in total element count across its *whole* document, not depth or single-array width) to accumulate enough leaked stack to hit an 8MB-64MB ceiling. `citm_catalog.json` is the first realistic, large, genuinely bushy (moderate depth × moderate branching, repeated hundreds of times) document this compiler has ever been asked to fully process.

## 4. Why this is NOT a quick fix, and why I did not attempt one

The obvious repair — give bare `FENCE` the same dynamic mark-at-α/restore-at-commit mechanism `IR_MATCH_FENCE1` (the one-argument `FENCE(X)` form) already has (`fence_mark_save`/`fence_release` in `bb_match_fence1.cpp`, using a per-node RBP-relative frame slot, `_.op_fence_frame_off`/`fence_frame_slot()`) — cannot be copy-pasted, because **`FENCE0` currently has no frame slot to write into, and getting one is not a local change:**

- `fence_frame_slot()`/`fence_frame_candidate()` (`emit.cpp:2358`, `:736`) are hard-coded to `nd->op == IR_MATCH_FENCE1` and use that node's `operands[0]/[1]` (the bounded sub-pattern the one-argument form has and the zero-argument form does not) — they cannot be reused as-is.
- The actual slot allocator, `frame_slot_scan()` (`emit.cpp:2229`), assigns indices by iterating `frame_slot_is_candidate()` (`emit.cpp:2218`) over every node in the blob. **`frame_slot_is_candidate` does not list `IR_MATCH_FENCE0` at all** — only `IR_MATCH_ARBNO`, `IR_MATCH_ASSIGN_SAVE`, `IR_MATCH_FENCE1`, and the generic leaf/xop checks. (`frame_need_of()`, a *different* function used for a *different* purpose — deciding whether a `MATCH_ASSIGN_*` capture needs activation-frame routing, the exact classifier seat09 extended today for the jdec fix — separately claims `IR_MATCH_FENCE0` needs 1 slot, but that claim is never consumed anywhere; it is dead budget, not a working reservation.)
- Adding `IR_MATCH_FENCE0` to `frame_slot_is_candidate` changes **`blob_frame_bytes()`'s total** for every blob containing a bare FENCE — and `blob_frame_bytes()` is the same function `sn4_choice_rbp_off()` (`emit.cpp:2342`) calls to decide `json-alternate-af-spin`'s own RBP-vs-FLAT choice-record placement. Touching this allocator is touching the exact shared mechanism that row's own HARD CONSTRAINT (§3 of its task baton: "the two ALT admissions answer DIFFERENT QUESTIONS and MUST NOT BE MERGED") warns against entangling casually, and it is used by dozens of other node kinds project-wide (`arbno_frame_slot`, `leaf_frame_slot`, every `MATCH_ASSIGN_*` capture, `blob_choice_rbp_scan` itself). A change here needs the full verification ladder (`make pristine`, `test_corpus_snobol4.sh`, `test_broad_corpus_snobol4.sh`, `test_crosscheck_snobol4.sh`, `board_beauty_m1.sh` both modes) before it can be trusted, exactly as `json-alternate-af-spin`'s own three prior sessions concluded about the sibling choice-record work.

I judged implementing this blind, in the same session that found it, to be the wrong trade — this is a shared, actively-tuned, wide-blast-radius allocator, and a rushed change risks exactly the "cures the crash, produces a silent wrong answer or a new regression elsewhere in the corpus" outcome `json-alternate-af-spin`'s own session-3 `SCRIP_CHOICE_RBP_FENCE` experiment already demonstrated is a real risk in this exact neighborhood of the code (§12 of that row's FINDING: the tempting fix cured the hang but returned `NOMATCH` where the oracle says `MATCH`).

## 5. Suggested fix direction, for whoever takes this

**Give every bare `FENCE0` a mark-at-α/restore-at-commit slot unconditionally**, rather than trying to make the static backward-walk smarter. This sidesteps `zd_chase`'s inability to traverse ALTERNATE/ARBNO entirely — no need to prove a static byte count, ever — at the cost of 2 `mov`s instead of 1 `add` per FENCE hit even in the simple cases that could have used the cheap static path. Given this project's `O0-ALWAYS`/"no `-O2` ever" performance posture, that trade looks clearly worth it for a correctness-and-boundedness guarantee. Concretely:
1. Extend `frame_slot_is_candidate()` to admit `IR_MATCH_FENCE0` (mirroring the `IR_MATCH_FENCE1` line right above it).
2. Add a `fence0_frame_slot()` parallel to `fence_frame_slot()`, without the `nd->op == IR_MATCH_FENCE1`/operand-range gating (a bare FENCE has no operand range — the candidate check for it is closer to "is `nd` itself an `IR_MATCH_FENCE0`", unconditionally, given it's always paying for the slot now).
3. Wire `g_emit.op_off` (or a new `op_fence0_frame_off`, matching FENCE1's naming) into the `case IR_MATCH_FENCE0:` switch arm in `emit_ir_node`.
4. In `bb_match_fence0.cpp`, replace the static `IF(rel>0, add rsp,rel)` with FENCE1's `fence_mark_save`/`fence_release` shape (mark at α, restore at commit) — gate behind a killswitch (e.g. `SCRIP_FENCE0_DYNAMIC`, default OFF at first, matching the project's established pattern for this exact class of change) so it is A/B-measurable against the current byte-identical baseline before flipping the default.
5. **Verify byte-identical `.s` output with the killswitch off**, then full corpus + `board_beauty_m1.sh` both modes + this FINDING's own two witnesses (§6) with the killswitch on, before considering a default flip.

This is real, scoped, implementable work — but it is a dedicated-session undertaking (shared allocator, wide blast radius, needs the full gate ladder), not a same-sitting patch, which is why it is being handed off rather than attempted here.

## 6. Witnesses committed

`corpus/probe/json_fence0_leak/`:
- `synth_perf224.json` (322,337 bytes) — fully synthetic, no dependency on `citm_catalog.json`'s content. An array of 224 records, each shaped like a real `performances[i]` (9 members; 2 `prices` sub-objects; 4 `seatCategories`, each with 10 `areas`). `scrip corpus/programs/snobol4/demo/json.sno < corpus/probe/json_fence0_leak/synth_perf224.json` → SIGSEGV (rc=139) at HEAD `2037a02f`.
- `gen_synth_perf.py` — the generator (`python3 gen_synth_perf.py <N>`), so the exact shape is auditable/reproducible and adjustable without hand-editing 300KB+ of JSON. ⛔ **The crash threshold is NOT a stable constant** — it moved from 233-pass/234-crash to 223-pass/224-crash within this same session, purely from an unrelated activation-frame allocation change (`2037a02f`) shifting per-record stack cost. Re-bisect with this generator (binary search on `N`) before trusting a specific threshold against a different HEAD; do not assume 224 stays the boundary.
- `synth_perf223.json` (320,898 bytes, same generator, N=223) — the one-below-threshold control at today's HEAD: clean exit, `rc=0`, confirming the cliff is sharp and this is the right minimal pair for a future regression test once the real fix lands. (No `.ref` minted — SPITBOL correctly parses both; the interesting fact here is SCRIP's *crash*, not a wrong-answer diff, so there is nothing to XFAIL against yet. Once §5's fix lands, promote `synth_perf224.json` into a real corpus row with a mint from `sbl -bf`, after re-confirming the threshold at whatever HEAD lands the fix.)

## 7. Housekeeping: what this session also confirmed about the row's OWN mechanism (af-spin), so the two are not conflated

Per this row's own task baton, I re-verified `json-alternate-af-spin`'s status before chasing this new lead, since a same-day, unrelated commit (`3a644af1`, hq_P, "ARRAY(n) no longer round-trips through text") had — per its own author's explicit "I cannot explain the mechanism, not taking credit" flag — stopped the original hang from reproducing. **Measured, not assumed: this is a SYMPTOM CHANGE, not a fix.** `n241_match_alternate`'s choice record (renamed by box numbering shift but structurally the same box the original FINDING analyzed) is still `[rsp+...]`-addressed (FLAT mode) in today's `json.s`; gdb on a fresh `-g` mode-4 build of `json.sno` + `[1,2]` shows `rsp` still drifting ~1,168 bytes across ARBNO re-entry into this alternation's ports, matching the original mechanism exactly. A 102-input fuzz sweep (trailing/leading/doubled commas, truncation, random malformed fragments) found no reproducible hang against current HEAD, including cases that force a genuine backtrack through `n241_match_alternate_af` (confirmed via breakpoint — `af` IS reached for some inputs and does NOT spin). **Best-supported explanation, not fully proven:** the ARRAY(n) fix changed workspace/heap allocation timing enough that the stale garbage value the original mechanism reads from the drifted stack slot no longer happens to be a self-referencing jump target — the underlying defect is unchanged and could plausibly resurface under different allocation conditions (a different `SCRIP_GC_STRESS` arm, a different malloc layout, a grammar shape elsewhere in the corpus that exercises the same "alternation choice record re-entered after an ARBNO that ran through a nested alternation" shape). **Recommend the row stay open with this status — LATENT, not CURED** — full detail filed as a session addendum to the row's own primary FINDING rather than repeated here.
