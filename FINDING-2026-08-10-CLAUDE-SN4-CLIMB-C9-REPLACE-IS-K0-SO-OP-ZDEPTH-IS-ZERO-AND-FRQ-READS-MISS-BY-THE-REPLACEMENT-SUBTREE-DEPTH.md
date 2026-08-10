# FINDING 2026-08-10 — SN4 ζ-CLIMB C-9: IR_MATCH_REPLACE IS K=0, SO op_zdepth IS ZERO, AND EVERY FRQ READ AT THE SPLICE MISSES BY THE REPLACEMENT SUBTREE'S LIVE DEPTH

**Goal:** GOAL-SN4-ZETA-CLIMB, rung C-9 (REPLACEMENT + SPLICE). **Modes:** m3 ≡ m4 (identical wrong output — emission not m3 glue, METHOD §6).
**Opened at:** SCRIP `c7e085fd`, corpus `9fb2e019` (both AHEAD of the s34 cursor's `6ffa57fe`/`f46d3ebe`; capture family re-proved with ZERO drift).
**Status:** ⭐ **FIXED AND LANDED** — SCRIP `9b951391`. Diagnosis was completed first with ZERO source edits; the fix followed once Lon ruled the choice mine.

## MONITOR-FIRST BRACKET (RULES.md §1)

`PARTICIPANTS="spl scr" test_monitor_3way_sync_step_auto.sh 062_capture_replacement.sno`

```
DIVERGE step 4, stno=2, 062_capture_replacement.sno:3   X 'world' = 'there'
  last agree: step 3  LABEL stno=2
  spl: VALUE X = STRING(11)='hello there'
  scr: VALUE X = STRING(5) ='there'
```

`STRING(5)` is exactly the replacement's own length. The write is the replacement verbatim; no splice occurred.

## ROOT CAUSE (MEASURED)

`FRQ(off)` on the RSP/FORTH arm expands to `[rsp + off + op_zdepth]` (x86_asm.h; law stated verbatim in the emit.cpp:1915 comment — "on the RSP arm FRQ expands to `[rsp+varslot+op_zdepth]` which drifts as FORTH cells are carved").

- `zd_k()` (emit.cpp:2002) lists **`IR_MATCH_REPLACE` in the K=0 class** — the splice yields no own result cell, which is correct as a *cell* statement.
- The staging choke (emit.cpp:841) therefore sets `g_emit.op_zdepth = g_zd_k = 0`.
- But at the splice the **replacement expression's ζ-cells are still live on the spine**. `bb_match_replace` emits its four frame reads *after* the replacement subtree has already lowered RSP.

Consequence: `op_sa`, `op_sa+8`, `op_off`, `op_off+24` are each short by exactly the replacement subtree's live depth, and read stale stack.

The **selectivity is the fingerprint** and it is fully explained:

| arg | addressing | zdepth-sensitive? | result |
|---|---|---|---|
| `rdi` name | `ROQ(0)` → `[rip+…]` | no | ✅ correct |
| `r9` replacement | `ZOPQ(1,0)` raw-cell escape | **no** — "ZRES/ZOPQ use raw-cell escapes and ignore zdepth" (emit.cpp:841 comment) | ✅ correct |
| `rsi/rdx` subject | `FRQ(op_sa)`, `FRQ(op_sa+8)` | **yes** | ❌ stale |
| `ecx/r8` start,end | `FR(op_off)`, `FRQ(op_off+24)` | **yes** | ❌ stale |

## THE DEPTH IS NOT A CONSTANT — IT IS THE SUBTREE FOOTPRINT (gdb, measured)

Breakpoint on `rt_match_replace`, caller frame dumped, true values located by signature scan (subject DESCR `0x0000000b00000002` = DT_S slen=11; span = 4/7 for `'DEF'` in `'abc DEF ghi'`):

| probe | replacement | template emits | true location | delta |
|---|---|---|---|---|
| P1 | `'XY'` (literal, 1 cell) | sub_lo`+160` start`+48` end`+72` | `+176` `+64` `+88` | **+16** |
| P8 | `A '-' B` (concat, 5 cells) | sub_lo`+256` start`+80` end`+104` | `+336` `+160` `+184` | **+80** |

Delta is uniform across all four reads within a program and equals the replacement subtree's ζ footprint. Confirmed independently: true start`+160` and true end`+184` differ by exactly 24 — matching the template's `op_off` / `op_off+24` stride, so `op_off` itself is correct and only the base is displaced.

## FALSIFIED EN ROUTE (recorded so they are not re-derived)

1. **"Prefix dropped, suffix kept."** P1/P2/P3 show the suffix is dropped too. 062/063 only *looked* like a prefix bug because their suffixes are empty.
2. **"Splice arithmetic is wrong."** `c_rt_match_replace` (gen_runtime.c:150) is textbook-correct and matches the manual exactly: `nlen = start + rlen + (slen-end)`, three memcpys. The sink is innocent; the args are wrong.
3. **"Captures are broken."** Captures are CORRECT (`P4`: `Y=[DEF]` matches oracle). Stages 1–4 sound; only stage 5 addressing is wrong.
4. **"First-touch / one-shot bake"** (the FI8 lazy-init class, METHOD §6). 064 showed exactly 9 `slen=0` for exactly 9 replacement sites, which looked decisive — but P7 (same site executed 3×) read `slen=1 start=0 end=1` on pass 1 and zeros on passes 2–3. The values are *whatever garbage occupies the wrong addresses*, not a one-shot zero.
5. **"Replacement is healthy in 2.2M corpus calls."** The sweep counted `slen>0` in 2,245,935 calls — ALL of it was `test_case` **spinning in a runaway loop** (6.8M at a 20s timeout; it scales with wall clock). Excluding the hang there are ~13 genuine splice calls in all of crosscheck and essentially every one is wrong. `test_stack` PASSES with `slen=0` because its subject is legitimately null — `slen=0` is NOT a valid defect signal.
6. **"`op_off` aliases the head's save slots."** At head-RSP `[H+48]`=outer_Σ and `[H+72]`=cap_gen, which made `op_off+0/+24` look like a slot-allocation collision. It is not: once the zdepth displacement is applied the reads land on genuine start/end slots. `op_off` is correct.

## BLAST RADIUS

Every pattern-match-with-replacement statement on the FORTH spine. Crosscheck: 062, 063, 064_replace_multi_arm (9/9 sites), test_string (2/2). **`test_case`'s rc=124 timeout is very likely a CONSEQUENCE** — the subject is clobbered to the replacement, so loops of the `ALOOP SUBJ ? PAT = :S(ALOOP)` shape (manual Ch.6 p.73, the canonical delete-all-occurrences idiom) never converge. Worth re-checking after the fix before treating that hang as its own defect.

## MANUAL ANCHORS (SPITBOL v3.7, SCRIP FOLLOWS SPITBOL)

- Reference, "Pattern-match with replacement": *"If the pattern match succeeds, the replacement expression is evaluated and replaces the portion of the subject matched. Only the matched portion is replaced; characters adjacent to the matching substring are not disturbed."*
- Tutorial Ch.6 "Pattern Matching with Replacement": match → conditional assignments performed → replacement evaluated, converted to string, inserted. *"If the pattern matched the entire subject, replacement behaves like a simple assignment statement."* ⬅ **the degenerate case SCRIP currently produces unconditionally**, which is why the defect reads as "assignment" rather than "splice".

## FIX AS LANDED (SCRIP `9b951391`)

`g_zd_zunder` — staged in the drive loop for `IR_MATCH_REPLACE` ONLY (backward scan to `MATCH_END`, summing `zd_k` over armed run members: the run-local spelling of `zout(REPLACE) − zout(MATCH_END)`), consumed at the choke as an `op_zdepth` addend. Mirrors the `g_zd_ztail`/`IR_TO` precedent exactly — ONE staging site, ONE consumer, ONE authority. 3 insertions / 3 deletions in `emit.cpp`.

**⛔ CORRECTION TO THIS FINDING'S OWN FIRST DRAFT:** it offered option (B), an `op_wpop` fold on the CONST-WPOP precedent. **That is WRONG and must not be revived.** CONST-WPOP pops an *orphaned* cell on the **failure** edge (`je Lγ / add rsp,16 / jmp ω`). The replacement cells here are live on the **success** path — `r9` is a `lea` of `rv`'s own cell — so folding them before the call hands the sink freed stack. Compensating the reads (option A) is the only viable shape.

## GATE (full untruncated A/B, pristine HEAD `c7e085fd` vs fixed)

- crosscheck m3 **239/78 → 242/75**; EXACTLY 3 status changes, ALL fail→pass (`062_capture_replacement`, `063_capture_null_replace`, `064_replace_multi_arm`); **ZERO pass→fail**.
- 141-probe m3 **133/15/0/3R identical before and after** — neutral. m4 **132/16/0/3R**.
- Probes P1/P5/P7/P8 green in BOTH modes.
- ⚠️ **`D12`/`D13`/`H31` REGRESSIONS ARE INHERITED, NOT FROM THIS FIX** — proven by stash + pristine rebuild at HEAD: they fail without the change. They were green at the s34 watermark, so a parallel seat broke them between `6ffa57fe` and `c7e085fd`. **Someone should own these.**
- ⚠️ A first A/B appeared to show 3 pass→fail (`134/135/136` balanced-parens). That was an artifact of my sweep script truncating the failing list with `head -40` while FAIL was 75–78. Re-run untruncated: they fail in BOTH builds. **Recorded so the phantom is not chased.**

## RESIDUAL (NOT this defect)

- `test_case` rc=124 → **rc=134**: the runaway loop WAS a consequence — a clobbered subject made the canonical `ALOOP SUBJ ? PAT = :S(ALOOP)` delete-all idiom (manual Ch.6 p.73) non-convergent. It now terminates but still fails for a separate reason.
- `test_string` still fails — separate class.
- `061_capture_in_arbno`: `POS(N)` with a **variable** argument fails the match outright (not a splice defect at all).
- `065_capture_then_arbno`: pre-existing CRASH.

## WITNESSES FOR THE FIX GATE

`062` `063` `064_replace_multi_arm` `test_string` — plus probes preserved at `/home/claude/probe/`: `P1_mid_suffix` (mid-string, non-empty suffix), `P2_at_zero` (match at offset 0), `P3_longer_repl` (growing replacement), `P5_two_sites`, `P7_same_site_thrice` (same site 3×, proves it is not first-touch), `P8_concat_repl` (multi-cell replacement — **the delta-is-not-16 witness; any fix that hardcodes 16 passes P1 and fails P8**). Re-check `test_case` rc=124 after the fix.
