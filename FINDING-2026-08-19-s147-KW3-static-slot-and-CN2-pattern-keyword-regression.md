# FINDING 2026-08-19 s147 — KW-3 STATIC KEYWORD SLOT LANDED, AND THE ARMED GATE'S "6/10" WAS ALREADY 4/10 ON ARRIVAL

**Seat:** web (Claude Opus 5), continuing HQ dispatch D-3 KW-STATIC.
**Repos:** SCRIP `a63c13d9` → `306858fe` (+ pin commit) · corpus `9e1b3f16` → (+ witness) · `.github` (cursor + this file).
**Parent:** `GOAL-SNOBOL4-100.md` LIVE CURSOR s147. Predecessor: `FINDING-2026-08-19-s146-KW1-census-keyword-truth-table.md`.

---

## 1. KW-3 — THE KEYWORD IS NOW A STATIC IN THE EMITTED ASM

`bb_keyword_snobol4` resolves `&KW` to its canonical block index **at emit time** (`rt_kw_index` — the keyword is a
source literal, so its index is a compile-time fact), seals that index as a static quad (`x86_ro_seal_q`), and the box
loads it rip-relative (`x86_ro_load_q`) and calls the O(1) accessor `rt_kw_read_idx`:

```
n2_keyword_snobol4_α:   sub   rsp, 16
                        mov   rdi, qword ptr [rip + .Lx127_0]
                        call  rt_kw_read_idx@PLT
                        ...
.Lx127_0:               .quad 0        <- &ANCHOR, statically present in the program
```

This retires the read cost the KW-1 census measured — a pointer to the keyword's **NAME STRING**, plus two case-folds
and a ~60-arm `strcmp` cascade — in favour of one rip-relative load and an array index.

**Laws held.** BOTH-MEDIUM and TEMPLATE-ONLY: the seal/load pair is the already-sanctioned medium-invisible encoder
couple (`bb_call_proc_staged.cpp:239` names it as such), so the template contains zero raw-byte producers and zero
`MEDIUM_*`. ONE AUTHORITY: `kwb_read`/`kwb_write` were split into entry-keyed bodies (`kwb_read_ent`/`kwb_write_ent`)
that **both** the by-name and the by-index paths execute, so the fast path cannot answer differently from the slow one —
the s68/s70 spelled-twice law applied to KW-3's own seam. `rt_kw_read_idx` calls `kwb_init_once()` itself precisely
because it bypasses the finder; omitting it would have left lazy seeding to whichever by-name read ran first, which is
the "initial value depends on access order" defect class KW-1 measured.

### ⛔ DELIBERATE SCOPE CALL — CELLS DID **NOT** MOVE (needs Lon's ruling)

The rung as written said "emit the block into the program's `.data` and bind it via `rt_kw_bind()`". **The per-keyword
SLOT is emitted static; the CELLS stay in the runtime**, and that divergence is deliberate. The KW-2 design homes each
keyword *at the cell its consumer already reads* — that is the whole reason `&TRIM = 1` started working, because the
write finally landed in the cell core.c's input path actually tests. Relocating cells into program `.data` would put a
keyword's storage somewhere other than where its consumer reads it, **re-creating the exact spelled-twice disease KW-2
had just cured**. `rt_kw_bind()` is untouched and remains the relocation seam if Lon wants the full block moved; the
by-index contract is bounds-tested so such a rebind fails loudly rather than reading a neighbour's cell.

---

## 2. THE INHERITED REGRESSION — AND HOW IT WAS CAUGHT

The s146 cursor records the armed gate at **6/10**. This seat measured **4/10**.

**The instinct to treat that as one's own breakage is what must be resisted.** Instead: a pristine baseline tree was
built from unmodified HEAD and measured — **also 4/10, with an identical failing set**. The loss therefore predated
this work, and the two lost rows (`kw_datatypes` m3+m4) were attributable to a commit that landed *after* KW-2.

### Root cause

`SN4-CONSTANTS` **CN-2** re-keyed the tier-3 keyword read from the bare name to a canonical `"&Name"`:

```c
{ char kb[128]; const char *ck = sval; if (sval[0] != '&') { ...prepend '&'... }
  if (!NV_EXISTS_fn(ck)) { ...core_runtime_error(342, ...); return NULVCL; }
  return NV_GET_fn(ck); }
```

The lexer strips `&`, so the pre-CN-2 tail was `NV_GET_fn("ARB")` — the **bare `ARB` variable holding the primitive
pattern**. CN-2's canonicalisation severed that bridge: `&ARB` now looked up `"&ARB"`, which no program ever assigns, so
it fell into the user-constant tier and raised **error 342 ON READ**. The whole family went with it:
`&ARB &BAL &REM &FAIL &FENCE &ABORT &SUCCEED`.

### Why this is unambiguously wrong

SPITBOL manual **Ch.16, p.187–188** enumerates each of these as a *protected keyword* — read-only repositories of
fundamental system patterns — verbatim: *"&ARB — The primitive pattern ARB."* The manual further explains they exist
"only for historic reasons," because SPITBOL forbids altering `ARB`/`BAL` at all. A keyword the manual names can never
be an "unknown `&name`". KW-2's own design note had explicitly relied on these **falling through** the block ("pattern
keywords are deliberately NOT in the block and reach their PATTERN value via the bare-name variable table").

### Fix

The family is resolved to its bare-name primitive pattern **ahead of** the CN-2 tier-3 arm. Runtime-only; zero codegen
blast radius. Armed gate **4/10 → 6/10**, restoring the s146 watermark.

---

## 3. THE CLASS LESSON — A RECORDED WATERMARK IS A CLAIM, NOT A MEASUREMENT

s146's own hard-won lesson was *"a small witness gate does not substitute for the by-set A/B"*. s147 adds its sibling:

> **⛔ Rebuild the pristine baseline and MEASURE it before attributing a red row to your own rung.**

Had this seat trusted the recorded 6/10, the only available conclusion was "KW-3 broke two rows", and the next move
would have been to bisect a correct rung looking for a defect that was never in it. Had it trusted its *own* 4/10 as
the true baseline, the CN-2 regression would have been silently laundered into the new watermark and inherited forever.
**Two numbers disagreed; the resolution was to build the third.**

---

## 4. THE STANDING PIN — WHY THIS CLASS WENT SILENT, AND WHY IT NOW CANNOT

The regression survived because **nothing pinned the behaviour**. `kw_datatypes.sno` caught the `DATATYPE` symptom, but
it is scored only on the KW-STATIC gate's armed arm and the loss was read as a KW-STATIC shortfall rather than a
correctness regression in a different subsystem.

Minted: `corpus/probe/kw/kw_pattern_family.{sno,ref}`, oracle-minted, **proven in both directions** — it FAILS on the
pristine pre-fix baseline and PASSES on the fixed build. It exercises `&ARB` and `&REM` as real pattern operands
(behaviour beyond `DATATYPE`) and pins the remaining five at the READ.

**Scope note discovered while minting it:** `&BAL`, `&FAIL`, `&FENCE`, `&SUCCEED` and `&ABORT` **cannot currently be
used as pattern operands at all** — SCRIP's lowerer rejects them outright (*"pattern shape outside the SN4-PAT
subset"*). That is a separate and larger gap on the road to 100%, recorded here and deliberately kept out of this
witness so the pin measures the regression rather than an unimplemented feature. Promote those five to real matches
when the pattern subset widens.

**It is run as a STANDING PIN, outside the KW-STATIC score.** The fix lives outside the killswitch, so the row passes
on *both* arms — and a row identical on both arms measures nothing about *arming*. Scoring it would have inflated the
legacy arm from 0/10 to 2/12 with a result the killswitch does not control. This mirrors, in the opposite direction,
the reasoning already applied to `kw_unset_datatype`. The gate now prints the pin separately and **exits non-zero if it
breaks**, independent of the score.

---

## 5. A LYING INSTRUMENT — `ab_board_sweep.sh --mode 4`

`scripts/ab_board_sweep.sh --mode 4` reports **PASS=0 DIVERGE=317 on every arm**, including pristine HEAD. It is not a
result. Mode 4 runs `scrip --compile`, whose stdout is **assembly text**, and diffs it against the program's expected
**runtime output** — a comparison that is structurally incapable of passing.

It remains valid as an *invariance* check (both arms identical ⇒ no behavioural movement), and was used as such here.
**It must never be recorded as a score.** This is the s33 "non-empty is not alive" false-signal shape wearing different
clothes: a full, plausible, entirely meaningless table. Flagged in the s147 cursor.

---

## 6. EVIDENCE

| check | result |
|---|---|
| killswitch byte-identity, default arm | **529/529, ZERO movers** — measured twice (after KW-3, and again after the fix) |
| regens ×3 (`benchmark`/`feature`/`demo`) | **zero changed bytes** — independent confirmation of the sweep |
| KW-STATIC gate, armed | **4/10 → 6/10** (s146 watermark restored); re-proven after rebase |
| KW-STATIC gate, legacy | 0/10 (unchanged; expected — the block is off) |
| standing pin `kw_pattern_family` | **OK m3 + m4** on fixed build; **BROKEN on pristine baseline** (bidirectional proof) |
| by-set A/B, crosscheck 318, m3 | base↔fix **0 movers** · base-ARMED↔fix-ARMED **0 movers** · default↔armed **0 movers** |
| `082_keyword_stcount` (s146's regression witness) | PASS on both arms |
| BOTH-MEDIUM / raw-byte greps | 0 in `bb_keyword_snobol4.cpp`; medium-invisible offenders unchanged (`bb_glue_flat`, `xa_flat` — pre-existing WIP) |

---

## 7. NEXT SEAT

**KW-3b (write half).** `rt_kw_write_idx` is **landed and ready** as the runtime half. Writes still route through the
`SNO$KWSET` by-name builtin — there is no write template at all. Retarget the two lowering call sites,
`lower_snobol4.c:586` and `:2327`, and give `&KW =` a real template on the same sealed-index shape as the read.
BOTH-MEDIUM, TEMPLATE-ONLY.

Then **KW-4**: delete the gated bare-name family, the `kw_*` statics, the `SCRIP_SEED_NAMES` ALPHABET bridge, and
`bb_match_advance`/`IR_MATCH_ADVANCE`.

⚠ Re-run the **by-set A/B**, not just the witness gate — s146's `&STNO` rewind was invisible to the witness gate.
⚠ Flipping the killswitch default to ON remains its own gated step: Class B changes `&TRIM`/`&FULLSCAN` behaviour for
every program, and the 802-row A/B is the evidence required.

**Still red, both routed, neither takeable here:** `kw_protected_write` needs the `&ERRLIMIT` → statement-failure
mechanism SCRIP does not have at all (KW-5/ERRLIMIT rung). `kw_bare_shadow` is HQ's **B1** — an unset variable yields a
NULL-tagged descriptor where the oracle gives the null string. Manual **p.24** is the authority and is verbatim:
*"SPITBOL guarantees that a new variable's initial value is the null string."* DATATYPE is innocent.
