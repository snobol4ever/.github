# FINDING s183 — THE M1 WALL IS DOWN: the JIT road spelled the resume surface a SECOND time and got it wrong

**Session:** 2026-08-20 s183 · HQ (Fable 5, max effort) · SCRIP `10d0bdbb` (merge of HQ's cut with seat1 `943e404a`)
**Parent:** `FINDING-2026-08-20-s182-beauty-m1-one-empty-line.md` (+ its three addenda) — s182 root-caused this wall and reduced it to a 5-line witness; s183 fixed it.
**Queue row:** `m1-fncat-beta` (rank 1, THE M1 rung) — **DONE**, by two seats independently.

---

## 1. THE DEFECT, IN ONE SENTENCE

`sno_pat_tree_graph_rt` — the **runtime/JIT** pattern-graph builder — published `gp->all[before_pat]` **raw** as the blob's resume surface. For a multi-element SEQ that node is a **leading argument-less `IR_GOTO` relay** (a nested-nary scaffolding sentinel); `optimizer/branch_chain.c:59` then chased the relay through to the **`IR_SUCCEED` terminator**, which is not even in the emitted node set — so `emit.cpp`'s β dispatch found no resume target and defaulted to `lbl_ω`. The blob **conceded wholesale** instead of re-entering its left element.

That is exactly s182's sentence — *"a runtime-composed pattern has no β path from its right element back into its left"* — with the mechanism named.

## 2. WHY IT ONLY BIT THE COMPOSED ROAD

`P = mk() ''` — a concat whose elements are **function-call results** — is **not** a `PAT$` blob. The lowerer cannot know statically that `mk()` returns a pattern, so the concat is built at runtime: `pat_cat` → `TT_SEQ` recipe → `dtp_fn_of` JIT → **`sno_pat_tree_graph_rt`**. The statically-lowered twin `P = A ''` goes through `sno_pat_thunks_build` instead, which has carried the correct computation since s121.

**This is beauty's `Parse` verbatim.** Beauty's grammar assignments are all build-time calls composing pattern values (`X4 = nInc() *Expr5 FENCE(*White *X4 | epsilon)`).

## 3. MEASURED, NOT ARGUED

`SCRIP_RESUME_WHY=1`, the s182 instrument, answers directly:

| road | witness | `body_root_op` | tier | in_nodes |
|---|---|---|---|---|
| static (`sno_pat_thunks_build`) | `ptw_min_varcat` | **72 = `IR_MATCH_LIT`** | 2 | 1 |
| JIT (`sno_pat_tree_graph_rt`) | `ptw_min_fncat_arbno` | **116 = `IR_SUCCEED`** | **0** | **0** |

ZSM port census (`SCRIP_ZSM_ALL=1 SCRIP_ZSM_CENSUS=1`, op numbers mapped through `IR.h`) — **this is the queue row's stated gate**:

| witness | `IR_MATCH_ARBNO` | `IR_MATCH_DEFER` |
|---|---|---|
| `ptw_min_varcat` (passing twin) | α=1 **β=2** γ=3 | α=2 **β=4 γ=6** |
| `ptw_min_fncat_arbno` **before** | α=1 γ=1 — **never β** | α=2 β=1 γ=2 **ω=1** |
| `ptw_min_fncat_arbno` **after** | α=1 **β=2** γ=3 | α=2 **β=4 γ=6** |

After the cure the JIT'd blob's port profile is **identical to the statically-lowered twin's**, which is the strongest available statement that the two roads now agree.

## 4. THE CURE IS A DELETION, NOT A NEW RULE

Two sites each spelled *"which node is this blob's published resume surface"* — the s68/s70 **spelled-twice disease**. The JIT copy was missing **every** law the static one had earned: the nary `out_rtail` carrier capture (s121 half B1), the FENCE-RESUME tier-1 narrowing (s182), the right-sealed refusal, and the leading-GOTO-relay skip.

Both roads now call **ONE AUTHORITY** each, extracted verbatim from the static site:
- `sno_pat_carrier_build()` — build the body and capture the rightmost element's carrier.
- `sno_pat_publish_body_root()` — decide and publish `body_root`.

Killswitch `SCRIP_RTSEQ_RESUME=0` restores the two pre-rung lines verbatim. No new globals.

## 5. ⭐ TWO-SEAT CONVERGENCE — AND WHY THE MERGE KEPT WHAT IT KEPT

seat1 (`943e404a`, "RTSEQ-RESUME") and HQ found this **independently** and landed within minutes. Same root cause, same witness, two different cuts. The merge (`10d0bdbb`) kept:
- **seat1's killswitch name** `SCRIP_RTSEQ_RESUME` — it landed first and its FINDING cites it. One knob, not two.
- **seat1's `[RTGRAPH]` diagnostic** — widened to answer for **both** roads, not just the JIT one. *A diagnostic that answers for one of two callers is how the second spelling stayed invisible.*
- **HQ's extraction** over seat1's copy-paste, for one concrete reason and not on style: the copy-paste cut **omitted the s182 FENCE-RESUME arm**, so a *fenced* composed pattern kept publishing the broken raw carrier — and beauty's own `Command = nInc() FENCE(3-arm ALT)` is exactly that shape. A third copy of the fact would have re-armed the defect on the next law added to the static road.

## 6. RECEIPTS

- **Movers:** `ptw_min_fncat_arbno` nomatch→**match**; `ptw_min_compose` nomatch→**match** — the s181 cursor's *"THE one remaining beauty road"*, cured by the same one wire. Controls `ptw_min_varcat` + `ptw_min_fncat_inline` unchanged.
- **Corpus fail-set BIT-IDENTICAL** armed vs off-arm, and again after the merge: **m3 332/5 · m4 325/11** — the s182 watermark exactly.
- **Pass-thru combo board: m3 119/120 · m4 111/120** (s182 read 108/112 and 100/112). The one m3 red is the named residue `ptw_min_opsyn_evalpat`, red in **both** arms.
- **7-mover fence class** 114/119/129/130/148/149/150 **GREEN in both arms**.
- **beauty_suite m3 17/17** — unchanged.
- **ZERO `.s` MOVERS** pre-edit vs post-edit (10-witness md5 including `beauty.sno`). The static-road extraction is byte-identical **by measurement**; the JIT road is runtime-only and emits no `.s` at all.

## 7. ⛔ BEAUTY: THE WALL MOVED. **M1 IS NOT EARNED.**

On `m1_min.in` (one newline), with the oracle wanting the **identity** (`\n` in, `\n` out):

| arm | result |
|---|---|
| `SCRIP_RTSEQ_RESUME=0` (pre-rung) | `Parse Error` |
| shipped default (armed) | **SIGSEGV, rc=139, stable 3/3, empty stdout** |

The descent now gets past the composed-pattern concede and dies downstream. **This is forward progress, not a regression** (the off-arm answer was never right either), and it is **not** M1.

**Measured about the new wall:**
- `rip=0x7ffff7ffd000` — inside ld.so **data**, i.e. a **wild jump**, not a call into bad code.
- `rsp=0x7fffffff8890` against a `[stack]` of `0x7ffffff13000`–`0x7ffffffff000` — the stack is **shallow**. **NOT stack exhaustion**, and not runaway recursion.
- **No existing killswitch moves it.** Swept 12 at `=0`: FENCE_RESUME, CAP_SEAMTIER, BLOB_CASMARK, PT_OPFRAME, PT_FRAME, B1C_LAND, DEFER_XPAT, CHOICE_RBP, CODE_THUNKS, SPAN_FRAME, FENCE0_WHACK, PB_ARGORDER — all still SIGSEGV.
- A 4-rung ablation ladder of composed patterns (`mk()` + FENCE, + self-recursion `*X` inside `X`, + FENCE'd self-recursion, + two-level composition) is **all green vs the oracle** (checked in as controls, corpus `probe/passthru/ptw_min_cw_*`).

### ⛔ HQ SELF-CORRECTION, KEPT VISIBLE — "A FRESH CLASS" WAS WRONG
HQ first wrote this crash up as **a fresh class**, reasoning from its own killswitch sweep (12 knobs, none moves it). **seat1 identified it correctly and HQ did not:** the backtrace signature — `_rtld_global` then `#1 0x0` — is the **identical signature `FINDING-…-s182` addendum 1 already recorded** for the `Parse = *Command` / `*Label nl` override witnesses, i.e. **a wild jump through a corrupted continuation** (ARCH-PASSTHRU law 0a/2), the **pass-thru continuation defect**. The two facts are not in conflict and both stand: *no existing killswitch moves it* is a measurement; *it is not a new class* is an identification against a record HQ failed to check. The identification is the load-bearing one, because **witnesses for this class already exist** — so the successor rung is *"work the known witnesses"*, **not** *"mint a new ladder"*, and HQ's first draft of that rung would have sent a seat to re-mint witnesses already on disk. seat1's cursor and `FINDING-2026-08-20-s183-the-jit-road-published-a-scaffolding-goto-as-its-resume-carrier.md` are the authority on this point.

### ⛔⛔ INSTRUMENT WARNING, THE MOST IMPORTANT LINE IN THIS FILE
**`SCRIP_ZSM_ALL=1` DOES NOT SURVIVE THIS ARM.** Under it beauty prints `Parse Error` — *the pre-rung answer* — while the shipped build SIGSEGVs stably. The ZSM instrument is therefore **grading a different program** on this witness, exactly the class RULES.md already names for `MONITOR_BIN`. **The ZSM ring, the ZSM census and `util_autobug.sh` (which exports `SCRIP_ZSM_ALL=1`) MUST NOT be used to trace or grade the beauty crash** until the perturbation is root-caused. This extends the s179 note (*"residual perturbation on fwctx ctl remains under investigation"*) from a loose end to a **blocking instrument defect on the M1 lane**, and it retires the automatic bug finder for this specific hunt.

## 8. THE NEXT RUNG (dispatch-ready)

**`m1-composed-wild-jump`** — ONE deliverable: root-cause the **pass-thru continuation defect** now that beauty reaches it.
- **⛔ START FROM THE WITNESSES THAT ALREADY EXIST**, per the self-correction above: the **s182 `Parse = *Command` / `*Label nl` override witnesses** carry this exact signature, and seat1's cursor states beauty's SIGSEGV and those two are **provably one target** — with a 1-byte input and a 2-frame backtrace. Do **not** start by minting a ladder; the four `ptw_min_cw_*` controls are checked in only to say what does *not* reproduce it.
- **Also owed here, and CLOSED by this merge — verify, don't redo:** seat1's cursor lists "the **fenced** RT publication this rung deliberately left alone (JIT road still publishes the stale first-allocated node)" as owed work. HQ's extraction gave the JIT road the s182 fence arm, so it is already closed at `10d0bdbb`; confirm with `SCRIP_RESUME_WHY=1` (`[RTGRAPH]` now prints for both roads) rather than re-implementing it.
- **⛔ Do NOT use ZSM/autobug** (§7). ASM-DIFF-FIRST: mint the repro, diff `--compile` `.s` against the nearest green ladder sibling, gdb last — and note the backtrace is destroyed by the wild jump, so breakpoint the β dispatch with a hit count instead of reading `bt`.
- **DONE-WHEN:** a standalone witness reproduces `rc=139` at shipped default and is green under `SCRIP_RTSEQ_RESUME=0`; root cause named; fix only if killswitch-clean with corpus fail-set identical; FINDING.

**Sibling rung, now unblocked and worth its own seat: `zsm-all-perturbation`** — root-cause why `SCRIP_ZSM_ALL=1` changes beauty's answer. DONE-WHEN: beauty's shipped-default answer is bit-identical with and without `SCRIP_ZSM_ALL=1`, or the perturbing mechanism is named and the instrument is fenced off in its own header.
