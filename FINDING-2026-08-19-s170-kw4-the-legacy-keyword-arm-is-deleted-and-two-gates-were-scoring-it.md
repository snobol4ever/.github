# FINDING s170 — KW-4: the `SCRIP_KW_STATIC=0` legacy keyword arm is DELETED, and two gates had been scoring the arm that no longer existed

**Seat:** local `/home/claude2`, Claude Opus 5, queue row `kw-4-legacy` (rank 14) · brief = GOAL-SNOBOL4-100 s166 SEAT-KW-3 **item 1 ONLY**.
**Landed:** SCRIP `bf87289d` (rebased onto the concurrent `97ad2912`). Baseline for the delta: `97ad2912`, its own parent.
**Watermark:** `make pristine` on BOTH trees, driver and `out/libscrip_rt.so` from one build each, RT_OPT `-O0`, oracle `x64` cloned and proven alive.

## 1. What was deleted

The arm had been unreachable-by-default since KW-6 flipped the switch ON (s161) and **oracle-WRONG in eight places** since the s165 census — bare unset `MAXLNGTH` read 524288 and `TRACE/STCOUNT/STNO/ANCHOR/TRIM/FULLSCAN/ERRLIMIT` read 0, where an ordinary unset variable must read NULL (Ch.16 p.187: keyword names *"are set apart from other variables by the unary operator ampersand"*). This is a **correctness deletion**, exactly as the s165 cursor reframed it.

| site | deleted |
|---|---|
| `core.c` `NV_GET_fn` | 14 bare-name read hijacks + the `goto`/label that skipped them |
| `core.c` `NV_SET_fn` | 11 bare-name write hijacks + the `goto`/label that skipped them |
| `core.c` | `core_seed_names()` + `SCRIP_SEED_NAMES`: the bare-`ALPHABET` bridge and the 30-line `tab/ht/nl/lf/cr/ff/vt/bs/nul/epsilon/...` NV pre-seeding block (the s144 `nl`/`lf` class) |
| `keywords.c` | **`rt_kw_static_on()` — the getenv itself**, and every guard it fed: the block is now THE arm at both the read and the write door, seeding is unconditional (KW-5b), `rt_kw_direct_sym` keeps only its own `SCRIP_KW_DIRECT` test |
| `keywords.c` | 10 post-block cascade arms the block always claims first — read `alphabet`/`errtext`/`user_declared_constants`; write `anchor`/`trim`/`maxlngth`/`trace`/`dump`/`{fullscan,stlimit,abend,code}`/`user_declared_constants` |
| `core.c`, `keywords.c` | the duplicate cells that lost their last reader with the hijacks: **`kw_stno`** and **`g_trim`** |
| `lower_snobol4.c` + both `bb_keyword_*` templates | the *"armed AND named"* conjunct collapses to *"named"* — which is what `sno_kw_static_slot`'s ONE AUTHORITY comment already promised |
| `templates/` + `IR.h` + `scrip_ir.c` | **`bb_match_advance.cpp` / `IR_MATCH_ADVANCE`** (dead, and the last template reference to `kw_anchor`) |

**The cascade arms were dead BY CONSTRUCTION, not by luck:** `kwb_read_ent` and `kwb_write_ent` return nonzero for **every** entry they find (`if (!e) return 0` is their only zero exit), so once the block query is unconditional, every arm below it naming a block keyword is unreachable. Verified in the source first, then measured anyway.

`IR_MATCH_ADVANCE` was the upper sentinel of the `IR_MATCH_LIT … IR_MATCH_ADVANCE` range in three places (`optimizer.c:35`, `emit.cpp:2230`, `emit.cpp:3484`). They re-anchor on **`IR_MATCH_RETRY`**, the surviving top of the match family — behaviour-identical because no node ever carried the deleted op. ⛔ The enum deletion renumbers everything below it, which is an ABI change across `.o` files: this is why every verdict here is from `make pristine`, never an incremental link (the Makefile's own s157 warning, and the HQ-27 contamination class).

## 2. The verdict — measured on a pristine pair, my commit against its own parent

- **`.s` blast radius: 0 movers / 527 comparable** (529 swept). Also 0 against the pre-rebase baseline `b7e10d3c`.
- **0 behavioural movers / 320 programs** — every `corpus/probe/*` family + demos, m3, output-diffed binary-to-binary against the baseline build. ⭐ **This is the load-bearing measurement, not the `.s` sweep:** the deletion is almost entirely *runtime C*, which `.s` byte-identity cannot see at all. A killswitch-byte-identity claim that only sweeps `.s` would be vacuous for a change of this shape.
- **crosscheck identical row-for-row** to the parent: m3 308 PASS / 9 FAIL · m4 306 PASS / 10 FAIL / 1 SKIP.
- **kw_direct 10/10 GREEN · kw_static 26/26 GREEN · UDC 23/23 · smoke 6/1.**
- **regens ×3** (benchmark/feature/demo): *"no changes"* on all three — an independent confirmation of the 0-mover result.
- **ratchets unmoved, measured on both trees:** raw producers 291, BOTH-MEDIUM 29 (at ceiling, not grown), `ir_field_discipline` PASS.

**The smoke `define` row is pre-existing and its pin is what is wrong.** The baseline worktree scores identically 6/1, **and the live oracle also prints nothing** for that exact program — so SCRIP ≡ oracle and the smoke script's pinned `"42"` is the outlier. Routed, not fixed here.

## 3. ⛔ TWO GATES WERE VACUOUS THE MOMENT THE SWITCH DIED — AND ONE HAD BEEN INFLATING ITS SCORE

`test_gate_udc.sh` looped `for arm in 0 1` and `test_gate_kw_static.sh` printed an `ARM=LEGACY` epilogue — both over a switch the binary no longer reads. The udc loop was running **the same binary path twice and counting it as two passes**: its advertised **27/27 was really 23/23**. Both are fixed here; `--legacy` now BLOCKS with a message instead of silently grading the default arm as if it were the legacy one. A gate that scores a deleted arm is the s68 vacuous-gate class, and it is worth saying plainly that this one was *born* vacuous by outliving its switch, not written badly.

**The killswitch-byte-identity baseline moves to `SCRIP_KW_DIRECT`**, as the s165 cursor proposed: measured 0/529 byte-identical, and unlike `SCRIP_KW_STATIC` it **isolates precisely** (s149: 47/527 movers, 47 of 47 `&`-referencing, zero false positives).

## 4. ⛔ THE s165 "SIX DUPLICATE CELLS" COUNT IS WRONG — FOUR OF THEM HAVE LIVE NON-HIJACK READERS

KW-4 deletes **two** of the six (`kw_stno`, `g_trim`). The other four survive because something *other than* the bare-name hijack still touches them — so they are not hygiene debt, they are **live split-brains** on the default arm, and each is its own rung:

| cell | block-canonical cell for the `&` form | what still touches the orphan |
|---|---|---|
| `kw_anchor` | `g_anchor` | `ASGNIC_fn` (write) · `sync_monitor` save/restore · `rt_scan_lit` (read) |
| `kw_maxlngth` | `g_maxlngth` | `ASGNIC_fn` only — **write-only, nothing reads it** |
| `kw_trace` | `g_trace` | `core.c:464` trace gate (read) · `core.c:1688` (write) |
| `kw_stcount` | `g_stcount` | `core.c:508/528` error-message text (read) — and **nothing increments it**, `rt_stmt_enter` bumps `g_stcount`, so error messages carry a stale 0 |

⭐ **`rt_scan_lit` is itself dead**: `bb_scan_stmt` is declared in `bb_templates.h` but **never called from `emit.cpp`**, and `rt_scan_lit` appears in **zero** committed `.s` artifacts. It is the same shape as `bb_match_advance` — a dead template keeping a duplicate cell alive. Retiring it is what unblocks `kw_anchor`.

**Not repaired here, deliberately.** Every one of these is reachable on the **default** arm, so repointing them is a *behaviour change* that would forfeit the 0-mover proof this deletion rests on, and mix two rungs in one commit. They are named, measured, and routed — the deletion stays provably neutral.

## 5. ⛔⛔ ESCALATION, NOT MINE: A NEW m3≢m4 DIVERGE LANDED IN THE SEVEN CONCURRENT COMMITS — DoD-1 VIOLATION

Measured on **both** trees, so the attribution is not an inference:

| tree | m3 | m4 | DIVERGE |
|---|---|---|---|
| `b7e10d3c` (my session baseline) | 307P/10F | 306P/10F/1S | **0** |
| `97ad2912` (parent, WITHOUT my commit) | 308P/9F | 306P/10F/1S | **1** — `141_pat_eval_double_fn_arbno` |
| `bf87289d` (HEAD, WITH my commit) | 308P/9F | 306P/10F/1S | **1** — same row, identical |

The window is `b7e10d3c..97ad2912` (7 commits), and **one killswitch convicts it with zero builds**:

- m3 default → `out=e`, **correct, matches the `.ref`**
- m3 `SCRIP_B1C_PARITY=0` → **dumps core**
- m4 default → **dumps core** · m4 `SCRIP_B1C_PARITY=0` → **dumps core** (the switch is inert in m4)

⇒ `c6245f60` *"B1c: FLIP SCRIP_B1C_PARITY DEFAULT ON"* is **mode-3-only**. It genuinely repaired m3 (its own "9 movers, every one crash→better" is real and the m3 row went 307→308) but left m4 crashing, which **converts a both-modes-fail row into an m3-pass/m4-crash DIVERGE** — a `GOAL-MODE34-IDENTICAL` / DoD-1 violation. A fix that lands in one medium only does not read as a regression on either mode's own PASS count, which is exactly why the crosscheck grades DIVERGE as a separate column. **Owner: the B1c seat. Repro is the corpus row itself, no new witness needed.**

## 6. Transferable lesson

**A killswitch outlives its arm, and the gates that grade it keep scoring for years.** `SCRIP_KW_STATIC` defaulted ARMED at s161; from that moment its `=0` arm was dead code carrying eight wrong answers, `test_gate_udc.sh` was inflating 23 to 27, and `test_gate_kw_static.sh` was printing an arm label for a branch nothing took. Nothing went red — a retired switch fails silent by construction. **When a killswitch flips default, the same commit should schedule the arm's deletion AND the gates that name it**, or the gate becomes a monument to a branch that no longer exists.
