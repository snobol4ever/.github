# FINDING 2026-08-11 (Opus 5, MECH s38) — THE ARBNO DEFECT IS THE **LEGACY ROUTE**, NOT THE BODY WIDTH; AND s37's KILLSWITCH EXONERATION WAS **VACUOUS BY CONSTRUCTION**

**HEAD at open/close:** SCRIP `565ecfa8` · corpus `0affc04e`. No compiler code changed this session (one experiment made, measured, reverted — §5).

**WATERMARK, re-proved at open AND close, BY SET:** m3 **137/22/0/2** · m4 **135/24/0/2** (`SCRIP_RTCC=0`; see §6). REGRESSION set = **D12 · D13 only**, identical open to close. Raw counts differ from the s37 cursor's `134/15` / `133/16` because the suite grew 151 → 161 probes at corpus `0affc04e`; the **set** is what matches, which is the comparison RULES mandates.

---

## 1. THE HEADLINE

s37's cursor states the top-rank defect as:

> *"ARBNO CANNOT SUPPLY ≥2 INSTANCES OF A FIXED-WIDTH BODY … Body-kind: SPAN is the ONLY kind that works."*

The observation is real but the **naming is wrong, and the wrong name hides the owner.** Measured, with the compiler's own `SCRIP_ARBNO_DIAG=1` routing diagnostic:

| probe | body | `k0` | `sq` | `kk` | route | result |
|---|---|---|---|---|---|---|
| N27 | `',' SPAN('ab')` | 0 | 1 | 16 | **FRAMELESS_K** | ✅ `=S` |
| N28 | `',' 'ab'` | 1 | 1 | 0 | legacy | ❌ `=F` |
| N24 | `'ab'` (bare) | 1 | 1 | 0 | legacy | 💥 SEGV |
| N33 | `',' ANY('abc')` | 1 | 1 | 0 | legacy | ❌ `=F` |
| N32 | `'AA'|'BB'|'CC'` | 1 | **0** | 0 | legacy | 💥 SEGV |

**Correlation is 1.000 with zero exceptions across every probe swept this session: every specimen that routes `FRAMELESS_K` is correct; every specimen that routes `legacy` is wrong or crashes.**

**THE DEFECT IS THEREFORE:** the **legacy (`fc_tail` CARRY-THE-TAIL) ARBNO arm is broken**; the ARB-LON-K16 `FRAMELESS_K` arm is correct. Body kind is **not** the defect axis — it is merely the *input* to the routing gate at `emit.cpp:955`:

```
if (_sq && !_k0 && _kk > 0 && !_fr && !_osv) { _k16r = 1; ... }
```

SPAN carries `zd_k != 0`, so a SPAN body satisfies `!_k0 && _kk>0` and routes to the good arm. Literal / `LEN` / `ANY` carry `zd_k == 0` ⇒ `_k0=1` ⇒ declined. An ALTERNATE in the body span sets `_sq=0` ⇒ declined by a **different clause**. "Fixed width" is a coincidence of which leaves happen to carve; it is not the discriminator and does not predict N32.

**Consequences of the renaming (each actionable, none visible under the old name):**
- **ALTERNATION bodies are in the defect class.** The manual's own p.122 example — `PAIRS = POS(0) ARBNO('AA' | 'BB' | 'CC') RPOS(0)` on `'CCBBAAAACC'` — **SEGVs**. A documented tutorial pattern, failing, with no probe covering it until this session (§4).
- **The instance-count boundary is route-dependent, not "≥2".** On the legacy route the *concatenated* form fails at **≥1** instance (`L1`: `POS(0) LEN(1) ARBNO(',' LEN(1)) RPOS(0)` on `'a,b'` → `=F`), while the *bare* form survives 1 and dies at 2. On the K16 route instance count is **irrelevant** — a SPAN-tailed body was measured green at 0, 1, 2, 3 and 4 instances. s37's "0 PASS · 1 PASS · 2+ SEGV" generalised one shape's boundary to the construct.
- Fixing "ARBNO" means **fixing or retiring the legacy arm**, not teaching leaves to carve.

## 2. ⛔ s37's KILLSWITCH EXONERATION WAS VACUOUS — THE INFERENCE, NOT JUST THE RESULT

s37 recorded:

> *"Four killswitches EXONERATED (byte-identical both settings): `SCRIP_ARBNO_K16`, `_LATCH`, `_FRAMELESS`, `SCRIP_ZPOP_FOLD_OFF` — the K-conversion arms are not the owner."*

Measured this session (md5 of the full mode-4 emission):

| probe | default | `SCRIP_ARBNO_K16=0` | |
|---|---|---|---|
| N24 (failing) | `e1af30f380e5` | `e1af30f380e5` | identical |
| N28 (failing) | `77b5d891eb3f` | `77b5d891eb3f` | identical |
| **N27 (passing)** | `bf5cc8323bc7` | **`fc049c8c4a09`** | **DIFFERS** |

And behaviourally: `SCRIP_ARBNO_K16=0` flips **N27 from `=S` to `=F`** — the killswitch *manufactures* the defect on a healthy specimen. `SCRIP_ARBNO_FRAMELESS=0` does the same.

**The killswitch is live. It was measured on specimens that were already in its OFF state.** `SCRIP_ARBNO_K16` can only move a graph *off* the K16 arm; N24/N28 were never on it (`k0=1`), so byte-identity was **guaranteed a priori** and carried no information. The bytes were correctly observed; the inference drawn from them — *"therefore the K-conversion arms are not the owner"* — is invalid, and it pointed the next session away from the arm that **is** the owner.

**METHOD RULE (proposed, this ladder's idiom):** a killswitch A/B is **VACUOUS unless the specimen is demonstrably ON the arm the switch disables.** Prove residency first — `SCRIP_ARBNO_DIAG=1` prints `route=` and settles it in one run — then A/B. A null result on a specimen of unproven residency is not evidence; it is the absence of an experiment. This is the same shape as the FINDING-07-30 "vacuous by symmetry" and "vacuous by volume" convictions: the probe ran, and could not have moved.

## 3. WHY THE SUITE WAS DARK, AND WHY IT STILL WAS AFTER N22–N31

s37 correctly diagnosed the coverage hole (*"every ARBNO probe uses a SPAN body"*) and a seat minted **N22–N31** at corpus `0affc04e`, covering instance counts and four literal/LEN body-kind permutations. That closed the `k0` entrance.

It did **not** close the `sq` entrance: **every one of N22–N31 reaches the legacy arm via `k0=1`.** No probe in the suite drove `_sq=0`, so the alternation route — a second, independent entrance to the same broken arm, and the one the manual documents — remained invisible. Two probes minted this session (§4) close it.

## 4. MINTED THIS SESSION (corpus, with goldens and baseline in the same commit)

- **`N32`** — body kind ALTERNATION, the manual p.122 `PAIRS` pattern verbatim. Enters legacy via `sq=0`. Oracle `=S`; SCRIP **SEGV** both modes.
- **`N33`** — body kind `ANY`, a width-1 leaf with `zd_k == 0`. Enters via `k0=1`, and differs from the passing control N27 **only** in leaf kind, making it the tightest available control pair.

Both goldens generated by `mkrefs.sh` from `sbl -b`; `mkrefs.sh --verify` reports **163 current / 0 drifted**. Both listed in `XFAIL.run` + `XFAIL.compile` in the same commit per the suite's own rule. `SUITE.md` N-family row updated (31 → 33) and now names which entrance each row exercises.

## 5. EXPERIMENT RUN, MEASURED, REVERTED — WIDENING THE GATE TO `kk == 0` DOES NOT WORK

The obvious repair — since the arm's own comment claims it *"widens ARBNO-LON past body-K0"* while its gate literally requires `!_k0` — is to admit `kk == 0` sequence bodies to the K16 arm. Implemented behind a default-off `SCRIP_ARBNO_K16_WIDE`, built clean, measured:

- **N28: `=F` → abort.** Strictly worse; the wrong answer became a crash.
- **N24: SEGV → SEGV.** No movement.

**Reverted; tree is clean and behaviour restored (re-verified after rebuild).** The K16 arm's σ-junction re-homing addresses the previous cell at a **one-level-in static offset equal to `kk`**; at `kk == 0` that offset collapses onto the current cell and the commit/retract arithmetic degenerates. The arm is not accidentally gated on `kk>0` — it is **structurally dependent** on it.

⛔ **DO NOT RETRY THE ONE-LINE GATE WIDENING.** A K0 body needs the arm to carve a body cell **on the body's behalf** (a 16B stride the body itself never allocates) so the σ junction has a non-degenerate stride — that is a real design rung with a layout delta, not a predicate edit. No default-off killswitch was left behind: a known-broken switch is exactly the M-5 debt this ladder exists to delete.

## 6. INCIDENTAL, BUT LOAD-BEARING FOR EVERY SEAT

- **⛔ The s37 cursor's headline hash `7aa32a3d` DOES NOT EXIST IN ORIGIN** (`git cat-file -t` → *not a valid object name*). The landed commit is **`565ecfa8`**, which the s37 addendum (A) names correctly — so the two halves of one cursor disagree, and the headline is the wrong one. Cursor corrected. This is STALE-ORIENTATION (b) with a live hash: a session trusting the headline would rebase against a commit that was never pushed.
- **s37 addendum (C) reconfirmed:** m4 without `SCRIP_RTCC=0` is unusable (130+ regressions) until WREG lands. Every measurement in this FINDING carries `SCRIP_RTCC=0`.
- `SCRIP_ARBNO_DIAG=1` is an excellent, already-built instrument that the cursor does not mention. It prints `framed / k0 / sq / kk / osv / route` per ARBNO site and answers "which arm is this graph on?" in one run. **Any future ARBNO killswitch A/B should open with it** (§2).

## 7. WHAT THIS DOES AND DOES NOT UNBLOCK

Unchanged: **D12/D13 remain the only REGRESSION set**, and their owner is still the **push/pop guard asymmetry routed to Lon in s37 addendum (B)** — untouched here, still awaiting the ruling on which guard to align. This session deliberately did not bolt a compensating pop onto one exit.

The ARBNO class is now **named, bounded, instrumented and covered**, and its repair is a scoped design rung (§5) rather than a hunt. It remains independent of the ζ mechanism and **not blocked behind M-1b**.

## 8. NEXT ENTRY POINT

1. **Route to Lon (two rulings now pending, both cheap to answer):** (a) the s37(B) push/pop guard alignment for D12/D13 — unchanged; (b) **the legacy ARBNO arm: repair, or retire by teaching the K16 arm to carve a body cell for K0 bodies?** §5 shows the predicate edit is not viable, so this is a layout decision, and it is the whole ARBNO class.
2. **Do not re-derive §1 or §2.** The route table and the vacuity proof are measured and reproducible in one command each.
3. If the ruling is *retire*, the rung is: K16 arm carves a 16B body-stride cell when `kk == 0`, σ junction reads it at the uniform offset, gate becomes `_sq && !_fr && !_osv` — measured against N22–N33 as the ready-made witness set, then the `sq=0` alternation entrance as a separate, later rung (path-dependent bodies are genuinely harder and N32 is its witness).

## 9. s38b ADDENDUM (same session, at handoff) — A CONCURRENT SEAT, THE FIX IT LANDED, AND ITS VERIFICATION

**§4's "another seat" was literally true but under-described, and one inference above is corrected here.** Corpus `0affc04e` (N22–N31) was NOT in origin at s38's clone — it appeared in the LOCAL working copy at 00:30, ten minutes after clone, followed at 01:00–01:01 by SCRIP `7dfb803a`+`560c63e4` and corpus `e707f815`+`091d45cc`+`d24999fa`. **A concurrent seat shares this container's persistent filesystem and committed into the SAME working copies**; authorship shows this seat's identity only because s38 set `git config --global` at session start. s38 briefly read this as fabrication — wrong headline, right instinct: the commits track the s37 cursor's own next-entry list in house idiom and follow regen ×3.

**THE TWO-CALCULATORS FIX (`7dfb803a`) IS VERIFIED, independently, from a fresh rebuild at handoff:** raw (XFAIL=/dev/null) m3 = **160 pass, fails {D12, D13, fence_probe}**; raw m4 (`SCRIP_RTCC=0`) = **159 pass, fails {A06, D12, D13, fence_probe}**. The pruned baselines in `e707f815` are **exactly truthful**; gate both modes = REGRESSION **{D12, D13} only**. **NEW WATERMARK: m3 160/1/0/2 · m4 159/2/0/2.** The fix retires the N02-FIX β pop (ZD-5b const-wpop already owns the right-spine release; the double-pop displaced every header read by 16 — its comment explains §1's m3/m4 asymmetry precisely). `SCRIP_ARBNO_FPRPOP=1` restores the double-pop for same-build bisect. **This answers §8 ruling (b) de facto: REPAIR the legacy arm — Lon should RATIFY.** §5's ⛔ (do not retry the K16 gate widening) stands; the working repair was in the legacy arm itself, outside §5's analysis.

**⛔ SEAT-ISOLATION HAZARD, for RULES:** two seats raced one working copy; one seat's uncommitted baseline edits were silently overwritten by the other's commit, and attribution was scrambled by a shared global gitconfig. Proposed rule: **one clone per seat** (or serialize seats), and at orientation ALWAYS run `git log origin/main..HEAD` — a clean `git status` is NOT proof of a clean tree.
