# FINDING — 2026-08-10 — Claude Opus 5 — RTCC RC-5: THE ACCEPT THRESHOLD SITS AT THE NULL CENTER, THE GVA RAIL IS UNRESOLVABLE IN PRINCIPLE, AND THE ENCODING WIN IS EXACT (AND UNDERCOUNTED)

**Session:** s9 of GOAL-RTCC.md (Opus 5)
**SCRIP HEAD at open:** `c7e085fd` (clean, tree pristine; one commit past s8's `5b435458`)
**Class:** CONCURRENCY-SAFE — measurement + docs only. ZERO emitter bytes, zero source edits, no regen owed.
**Watermark re-proved at open:** claim-gate `--strict` PASS (collision class EMPTY) · fibonacci m3 `result: 832040` at RTCC=0 AND RTCC=1 · var_access m3 `result: 60000012` at RTCC=1.

---

## 0. WHAT I SET OUT TO DO, AND WHY IT COULD NOT BE DONE

The s6/s7/s8 cursor carries this debt verbatim:

> **RC-5-GVA rail (1.036x fibonacci / 1.028x var_access) NOT RE-PROVED on current HEAD** — s5 measured on `bcac52c4`, six commits before the concurrent AB-2/ICN-FR-5 landing. Re-prove with min-of-N instrument before claiming.

I opened this session to discharge that debt. **It cannot be discharged, and no future session can discharge it either** — not because the tree moved, but because the claimed effect is smaller than the instrument's resolution. The debt as written asks for a measurement the rail cannot make. This finding replaces it with one the rail *can* make.

---

## 1. THE GATE DEFECT — RC-5 ACCEPTS AT THE CENTER OF THE NULL DISTRIBUTION

Three binding statements, all currently live, are mutually inconsistent:

| source | statement |
|---|---|
| `GOAL-RTCC.md` RC-0(a) exit | *"an unchanged binary measures **1.00× ±noise**"* |
| `GOAL-RTCC.md` RC-5 accept | *"honest ratio, **revert if ≤1.00×**"* |
| `ARCH-SNOBOL4-RTX.md` rung 4 (RAIL) | *"**NO TWO-ARM NUMBER BELOW ~1.10× IS TRUSTWORTHY.**"* |
| `scripts/bench_min_of_n.sh:22,41` | `RATIO_FLOOR=1.10`, anything below prints **`~null`** |

RC-0(a) *defines* the no-effect distribution as centred on 1.00×. RC-5 then sets its accept threshold at **that same centre**. A rung with literally zero effect therefore passes RC-5 roughly half the time — the sign of the noise excursion decides, not the code.

⛔ **This is the same defect class this project already convicted once.** `ARCH-SNOBOL4-RTX.md` rung 0(f) records the killswitch md5 gate "**reports MOVER or IDENTICAL by coin flip**" against a non-deterministic program, and the correction was to stop grading a noisy quantity with a single-sample comparison. RC-5's threshold is that same shape, one level up: a noisy quantity graded against a threshold sitting inside its own noise band.

**The instrument already knows this and says so on every run** — `bench_min_of_n.sh` would print `~null(<1.10x)` next to both of s5's numbers. The rung's accept criterion and the rung's instrument disagree, and the accept criterion won because it is the one written in the goal file.

---

## 2. EMPIRICAL — THE NOISE BAND AT CURRENT HEAD SWALLOWS THE CLAIM

`fibonacci.sno`, mode 3, `SCRIP_RTCC=1`, **same binary, same flags, zero code change**, N=12 each:

| condition | min | med | max | spread | **max/min** |
|---|---|---|---|---|---|
| default (ASLR on — s5's condition, and `bench_min_of_n.sh`'s default) | 574 | 589 | 647 | 12.7% | **1.127×** |
| `setarch -R` (ASLR pinned) | 556 | 558 | 573 | 3.1% | **1.031×** |

Against a claimed RC-5-GVA effect of **1.036× / 1.028×**:

- Under **default** conditions an unchanged binary spans **1.127×** — **3.1× larger than the claimed effect.**
- Under **ASLR-pinned** conditions the range is **1.031×** — **essentially equal to the claimed effect.**
- ⭐ **THE MINIMUM ITSELF IS NOT STABLE ACROSS THE ONE VARIABLE THE HARNESS DOES NOT PIN BY DEFAULT.** min moved **574 → 556 (3.2%)** on an unchanged binary from address-space layout alone. `bench_min_of_n.sh`'s own rationale (lines 10–14) rests on min being *monotone-stable*; that argument holds **within** a fixed address layout and **fails across** ASLR draws. The estimator of record shifts by about the size of the effect it is being asked to grade.

⇒ **s5's 1.036× is not reproducible in principle at this precision, and re-running it would settle nothing.** This is NOT a criticism of s5: s5 followed the goal file exactly, hit `>1.00×`, and landed the rung as instructed. **The defect is in the threshold, not the session.**

⚠ **RC-0(a)'s own exit criterion is currently UNMET at HEAD and nobody noticed**, because nothing re-checks it: it requires an unchanged binary to measure `1.00× ±noise` across independent invocations, and an unchanged binary here reads **1.127×** by default. RC-0(a) is marked `[x]`. **Recommend `ASLR=off` become the DEFAULT in `bench_min_of_n.sh`, not an opt-in** — it is a 4× reduction in spread for free, and the current default is the arm that produced every unquotable number on this ladder.

---

## 3. THE CONSTRUCTIVE HALF — RC-5-GVA HAS A ZERO-VARIANCE INSTRUMENT NOBODY USED

The rung's *mechanism* claim is static encoding, and static encoding is **exactly countable with no noise at all**. Ground truth, `as --64` + `objdump`, verified by instruction address deltas (`0 → 8 → 0x10 → 0x18 → 0x1c → 0x20 → 0x24`):

| form | bytes | encoding |
|---|---|---|
| absolute `qword ptr [1879052288]` (killswitch OFF) | **8** | `48 8b 04 25 00 10 00 70` — REX.W + op + modrm + **SIB** + disp32 |
| `qword ptr [r9 + disp8]` (RC-5-GVA ON) | **4** | `49 8b 41 10` — REX.WB + op + modrm + disp8 |
| `qword ptr [r9 + disp32]` (offset ≥ 128) | **7** | `49 8b 81 00 10 00 00` |

⛔ **CORRECTION TO THE RECORD.** The s5 FINDING §"Key properties" states: *"7B `ABSQ` (absolute disp32 + REX prefix, SIB no-base) → 4B `[r9+disp8]` per access."* **The absolute form is 8 bytes, not 7** — the SIB byte is present *and* required (mod=00, r/m=100 with base=101 is the no-base disp32 form), and the count omitted it. **The saving is 8→4 = 4 bytes per in-range access, not 3.** The mechanism is **33% better than the rung claimed.**

Measured distribution at HEAD (`--compile`, `SCRIP_RTCC=1` vs `=0`):

| program | GVA accesses (ON) | disp8 | disp32 | **static saving** |
|---|---|---|---|---|
| roman | 106 | **106** | 0 | **424 B** |
| fibonacci | 116 | **116** | 0 | **464 B** |
| var_access | 54 | **54** | 0 | **216 B** |

⭐ **100% of GVA accesses are disp8 — zero disp32 anywhere.** The encoding win is therefore *maximal* (4 B each, never 1 B). s5 predicted this for roman's variables at offsets 0–40; it holds **universally** across all three programs. **That instruction class halves: 8 B → 4 B, a 50.0% reduction on the GVA access surface.**

⚠ **HONEST LIMIT — STATIC BYTES ARE NOT WALL TIME.** This instrument grades the **MECHANISM**, exactly and reproducibly. It does **NOT** establish a speedup: whether halving this class yields time depends on I-cache pressure and on those accesses being hot, neither of which a byte count can show. **Do not quote 50% as a speed number.** What it does establish is that RC-5-GVA is *not* a null rung — it does precisely and maximally what it claimed, by a margin larger than recorded — and it does so on a statistic that cannot drift, cannot be flaked by ASLR, and does not need a rebuild to re-prove.

⚠ Minor accounting note, stated rather than buried: OFF-arm absolute-form counts are **110 / 118 / 54** against ON-arm r9-form **106 / 116 / 54**. `var_access` matches exactly; roman and fibonacci carry a 4 and 2 residue. Either a few absolute operands are non-GVA, or a handful of GVA sites remain unconverted. **Not chased this session — flagged, not assumed.** A 4-site residue is a cheap, worthwhile probe for whoever opens the next RC-5 rung, and if they are unconverted sites they are free bytes.

---

## 4. WHAT SHOULD CHANGE (proposed — NOT applied this session)

1. **RC-5 accept threshold: `>1.00×` → `≥1.10× on the rail, OR a deterministic secondary instrument.`** A threshold at the null centre cannot grade anything.
2. **`bench_min_of_n.sh`: `ASLR` default `on` → `off`.** 12.7% → 3.1% spread for free. One-line change, scripts-only, concurrency-safe.
3. **Re-open RC-0(a).** Its exit criterion is unmet at HEAD under its own default conditions.
4. **Adopt static-encoding delta as RC-5's secondary instrument of record.** Cheap, exact, rebuild-free, and it grades the mechanism the rung actually implements.
5. **RC-5-GVA itself STANDS.** Do not revert. Its timing claim is unresolvable and should be struck from the cursor as a *number*; its mechanism is confirmed and larger than recorded.

---

## 5. WHAT I DID NOT DO, AND WHY

- **Did not open RC-6**, though the s8 cursor recommends it. RC-6 reclassifies a family NO-VENEER, which touches the registry and the `x86("call")` dispatch arm — **encoder surface, the NOT-CONCURRENCY-SAFE side of the line**, with nine seats live against one tree. **Lon routes that window; a seat does not take it.**
- **Did not edit `GOAL-RTCC.md`, `bench_min_of_n.sh`, or any source.** §4 is a proposal awaiting a ruling.
- **Did not commit or push.** Nothing is staged. Per RULES §6b the credential is asked for in-chat at session end; nothing here is pushable until §4 is ruled on.
- **Did not run the two-binary GVA A/B rebuild.** §2 establishes the result would be uninterpretable; spending two full rebuilds to produce an unquotable number is the exact waste this finding exists to prevent.

---

## 6. LAW PROPOSED FOR `GOAL-RTCC.md` LAWS & TRAPS

> **A THRESHOLD AT THE NULL CENTRE IS NOT A GATE (s9).** RC-0(a) defines the no-effect distribution as centred on 1.00×; any accept criterion of the form `>1.00×` therefore passes a zero-effect rung on a coin flip, and passed one for four sessions. An accept threshold must sit **outside** the measured noise band of its own instrument, or be replaced by an instrument with no noise band. Measured at HEAD: unchanged binary = **1.127×** default / **1.031×** ASLR-pinned, and the **min-of-N statistic itself moves 3.2% on ASLR alone**. Corollary: where a rung's mechanism is static (encoding, site count, byte width), **grade the mechanism — it has no noise band at all.**
