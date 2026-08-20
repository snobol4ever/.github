# FINDING s172 (seat3, Opus 5, queue row `pt-group-defer`) — PT-3: THE `*group` DEFER ROUND TRIP COLLAPSES TO LOADS. THREE C CALLS PER DEREFERENCE BECOME ~12 INSTRUCTIONS, AND THE SKIP IS **PROVABLE FROM `dtp_fn_of`'s OWN BODY**, NOT MERELY PLAUSIBLE — 1.41×/1.63× ON treebank AT `RT_OPT=-O0`, ZERO ARM-CAUSED MOVERS IN 1034 PROGRAMS

**Front:** GOAL-SNOBOL4-100 · PT (pattern-perf trace) · rung **PT-3**. Queue row 12 `pt-group-defer`. DONE-WHEN: *"killswitch rung landed, corpus green, measured delta in a FINDING labeled RT_OPT level."* All three met.
**Trees:** SCRIP `982f7b46` (this commit, pushed) · corpus `74fe5ff4` · .github (this commit). Every number on a `make pristine` build — driver AND `out/libscrip_rt.so` from one commit.
**⛔ RT_OPT = `-O0` ON EVERY NUMBER IN THIS FILE.** See §6; the label is not decoration, it is the caveat.

## 1. THE TARGET WAS NAMED FOR ME, AND THE ENTRY POINT WAS EXACT
FINDING s168 (PT-0/1/2) ranked the histogram and named the top: the `*group` deferred dereference is **59.4 % of all treebank-match cycles** — `rt:patv_slot` 19.9 % + `rt:rt_patv_defer_get_pat_dtp` 15.2 % + `match_defer_α` 14.1 % + `rt:dtp_fn_of` 10.2 % — and the emitted `$V` slot arm pays a **three-call C round trip per dereference**:

`rt_patv_defer_get_pat_dtp(hv,i,fb)` → `patv_slot(hv,i,fb,0)` → `dtp_fn_of(v.p)`

…after which the *template* re-loads `fn` from `[dtp+0]` by hand, two instructions later.

## 2. ⭐ WHAT MAKES THE SKIP PROVABLE RATHER THAN PLAUSIBLE — THE WHOLE RUNG RESTS ON FOUR LINES
`dtp_fn_of` is, in its entirety:
```c
void *dtp_fn_of(void *headv) { DTP_t *h = headv; if (!h) return 0;
    if (!h->fn && h->rcp) { /* lazy-compile the recipe into h->fn */ }
    return h->fn; }
```
So **once `fn` is materialized, `dtp_fn_of` is a PURE function returning `[dtp+0]`** — and `[dtp+0]` is the exact word the existing cold arm already re-loads for itself. On the steady-state arm (a `*group` compiled once and dereferenced millions of times) **all three calls are provably redundant**, and the box can answer from loads alone. This is not "probably equivalent"; it is the callee's own body.

## 3. THE ARM
Template-only, both media, **no new global** — the same function-static `getenv` cache idiom as `fence0_whack_on`/`rspd`. Reproduce `patv_slot`'s snap arm inline (`h=[rbp-24]`, `snap=[h+32]`, `nsnap=[h+40]` — the offsets `DTP_t`'s own definition publishes *for asm consumers*), take the DT_P/payload test in the **GVA arm's already-verified spelling** (`mov rax,qword[..]` / `cmp eax,DT_P` / `mov rdx,qword[..+8]`), then `fn=[rdx+0]`; non-null ⇒ done, **zero calls**.

**Every** other case — no DTP, no snap, index past `nsnap`, not DT_P, null payload, fn not yet compiled — falls through to the **UNCHANGED** cold path. The arm cannot answer differently, only sooner.

It lives **template-side, not in `emit.cpp`**, and that is a deliberate contrast with FZ-3 earlier this same session: FZ-3 *had* to sit emitter-side because it changed the spine depth the ζ planner models. This arm **carves nothing** — it adds instructions, never bytes of spine — so the planner has no question to ask and an armed template can never meet a disarmed planner.

## 4. MEASURED — INTERLEAVED, DISJOINT WINDOWS, IDENTITY-GATED
Protocol inherited from `bench_pt0_3way.sh` (s143/s141/s168): interleaved **same-moment** samples (one iteration times both arms back to back), odd sample count, median of sorted, **identity gate first**, ratios are the deliverable. Two separate script runs would NOT be interleaved — that is precisely the s143 trap (*"identical bytes measured 51 ms and 71 ms minutes apart"*), so an arm-vs-arm harness was written rather than running the 3-way twice.

| workload | medium | OFF median | ON median | ratio | windows |
|---|---|---|---|---|---|
| `treebank-match` | m4 prebuilt | 100 ms | **71 ms** | **1.41×** | DISJOINT [96,103] vs [65,75] |
| `treebank-match-fence` | m4 prebuilt | 98 ms | **60 ms** | **1.63×** | DISJOINT [93,103] vs [58,68] |
| `treebank-match` | **m3 (BINARY)** | 117 ms | **96 ms** | 1.22× | window INCLUDES scrip's own compile |

`reps=200`, samples 11/9/9, `RT_OPT=-O0`, mode 4 arms are **prebuilt binaries** so scrip's compile is outside the timed window. The m4 windows do not overlap at all, so this is not a noise-floor artifact.

**⭐ THE m3 ROW IS THE BOTH-MEDIUM PROOF, AND IT IS NOT DECORATIVE.** "Zero movers in mode 3" is exactly what an arm that **emits nothing in BINARY** would also produce — a real BOTH-MEDIUM violation would have been invisible to the correctness sweep. Timing m3 separates the two: the arm is **live in BINARY**, saving ~21 ms against m4's ~29 ms, the same absolute work diluted by the compile constant the harness header already documents.

## 5. CORRECTNESS — 1034 PROGRAMS, BOTH MEDIA, **ZERO ARM-CAUSED MOVERS**
- **Reach: 112 of 1019 comparable programs** emit the collapse — including **`beauty.sno` and `beauty_c.sno`** (the M1 self-host target), all 8 `beauty_suite` drivers, every `calculator`/`json`/`treebank` match program, and 23 `crosscheck/patterns`. This is not a one-program micro-optimization.
- **m3 behavioural A/B: 4 apparent movers / 1034 — ALL FOUR DISPROVEN** by the hold-the-arm-fixed control (10 runs, env untouched): `leafsib_tab`, `calculator-1`, `json`, `cf_goto_computed`. The last is doubly exonerated: its `.s` is **byte-identical between arms**, so the arm emits nothing for it at all, yet it still flips 132↔139 on its own.
- **Oracle-grading the 112 touched programs at the ARMED arm: PASS 74, ARM-CAUSED FAIL 0**, 37 already-red-or-no-ref. ⛔ The one program the sweep initially flagged as an arm-caused divergence — `demo/json.sno` — is a **FALSE POSITIVE** produced by the exact hazard this seat documented hours earlier: held at a fixed arm it flips between two outputs in **both** arms (6/4 ON, 9/1 OFF) and matches its `.ref` in neither. Had the control not been run, this FINDING would have reported a regression that does not exist.
- **Disarmed = byte-identical.** At default OFF the emitted `.s` is IDENTICAL to the tracked artifacts for `treebank-match`, `treebank-match-fence`, `claws5-match`; demo and crosscheck regens both report `changed=0`.
- **Gates:** LANG-BLIND green · BOTH-MEDIUM ratchet 3/3, delta 0 (this file adds zero `MEDIUM_`) · the FZ gate from this session's earlier rung still GREEN.

## 6. ⛔⛔ THE DOMINANT CAVEAT: THIS IS AN `-O0` NUMBER, AND THE RUNG IS THE KIND `-O0` FLATTERS MOST
The collapse deletes **calls to small leaf functions**, which is precisely the cost `-O0` prices highest and `-O2` is most likely to erase — at `-O2` the C compiler may inline `patv_slot` straight into `rt_patv_defer_get_pat_dtp` and recover much of this **on the disarmed arm**. s168 §7 already warned that the 52.4/45.3 cycle split is RT_OPT-sensitive for exactly this reason ("small leaf fns at -O0").

**The `-O2` arm is UNMEASURED, deliberately: O2-DIRECTED-ONLY binds and Lon has not directed `-O2` this session.** So: **treat 1.41×/1.63× as an UPPER BOUND, not as the shipping number.** What is *not* RT_OPT-sensitive is the instruction count — three call/ret pairs plus two redundant materializations of the same word, gone on the hot arm — and that survives any optimizer setting.

**⭐ THE ONE ASK FOR LON / HQ:** direct an `-O2` A/B of this arm. It is the difference between a real 1.4× on the M1 critical path and an artifact of the development build, and no seat can answer it without the direction.

## 7. WHAT THIS SEAT DID **NOT** DO
- **Did not flip the default.** The rung ships DISARMED per the standard ladder; the A/B is the case, and the flip is a separate attributable decision (the FZ-3 precedent from this same session).
- **Two intended workloads could not be mounted and are reported, not dropped:** `calculator-2-match` and `json-match` have no single-line `subject ? pattern :F(label)` for the inherited tape transform to rewrite. That is a **harness** limitation, not a result — no claim is made about them either way. Widening `mktape` is a clean follow-on.
- **Did not touch `patv_slot`/`dtp_fn_of` themselves.** The C side is untouched; a future rung could delete the now-cold double read there, but that is runtime work and this row is the emitted arm.
