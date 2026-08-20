# FINDING s182 — THE M1 WALL IS ONE EMPTY LINE, AND THE MECHANISM IS β-RETREAT INTO A DEFERRED PATTERN

**Seat:** HQ (Fable 5, max effort), 2026-08-20. **Tree:** SCRIP `26587504` + this session's two edits, corpus `9fd581f1`, pristine build at RT_OPT=-O0.
**Lon's order this session:** *"stop when you have a concrete simple example, a reproducer, and SHOW ME."* This file is that record.

## ⭐ THE HEADLINE — M1 REDUCES TO A ONE-BYTE INPUT
`beauty.sno` fed a file containing **a single newline** answers `Parse Error`. The oracle beautifies it correctly.
```
printf '\n' > m1_min.in                       # corpus/programs/snobol4/demo/beauty/m1_min.in (checked in)
scrip beauty.sno < m1_min.in                  # -> Parse Error          (WRONG)
x64/bin/sbl -bf beauty.sno < m1_min.in        # -> (blank line)         (RIGHT)
```
This supersedes every prior spelling of the wall ("the FIRST Shift/Reduce parse", s170). **Only `*`/`-` comment lines survive** — and only because `main01` short-circuits them (`Line POS(0) ANY('*-')`) before the parser is ever entered. Every other input class fails: empty line, bare label `START`, `X = 1`, `:(END)`, `END`.

## THE MECHANISM, MEASURED SIDE BY SIDE (not inferred)
Probe inserted at `beauty.sno` `main05`, both engines, same file, input `        X = 1`:
| probe | SCRIP | ORACLE |
|---|---|---|
| `SIZE(Src)` | 14 | 14 |
| `Src POS(0) (*Parse $ pcon)` → `SIZE(pcon)` | **0** | **0** ← both agree |
| `Src POS(0) *Parse RPOS(0)` | **FAILED** | **OK** |
Both engines agree the FIRST match of `*Parse` is zero-length. The oracle then **backs into `*Parse` and retries** until an alternative consumes all 14 characters. **SCRIP never re-enters.** The failing statement is `main05`:
```
Src  POS(0) *Parse *Space RPOS(0)   :F(mainErr1)
```
β-retreat into a deferred pattern value is dead on this road. **This is ARCH-PASSTHRU law 0/0a/0b territory exactly** — the crossing back into a suspended graph.

## TWO SEGVs IN BEAUTY CONTEXT (harder signal than the wrong answer — NEW WITNESSES)
Override `Parse` in otherwise-unmodified beauty, input = one newline:
| override | SCRIP | ORACLE |
|---|---|---|
| `Parse = *Command` | **SIGSEGV** | ok |
| `Parse = ARBNO(*Command)` | **SIGSEGV** | ok |
| `Parse = *Label nl` | **SIGSEGV** | ok |
| `Parse = *Stmt (nl \| ';')` | ok | ok |
| `Parse = *White nl` | Parse Error | Parse Error (both — legitimate) |
gdb on the `*Label nl` arm: `SIGSEGV in _rtld_global`, then `#1 0x0000000000000000 in ?? ()`. **The return address itself is garbage** — a wild jump through a corrupted continuation, i.e. the pass-thru class, not a data bug. `Label = BREAK(' ' tab nl ';') ~ 'Label'`, and `~` is `OPSYN('~','shift',2)` where `shift = EVAL("p . thx . *Shift('" t "', thx)")`.

## ⛔ AN ELEGANT HYPOTHESIS, FALSIFIED BY TEST — RECORDED SO NOBODY RE-DERIVES IT
**Hypothesis:** beauty is killed by the whole-program fz poison. `semantic.inc`/`assign.inc`/`ShiftReduce.inc`/`omega.inc` all call `EVAL`, which sets `g_sno_fz_unsafe` (`lower_snobol4.c:1001`), which unseals EVERY name (`sno_seal_pat`, `:968`), so no grammar pattern folds statically.
**Test:** `SCRIP_FZ_FORCE=1` (diagnostic added this session at the `sno_seal_pat` guard; zero new state, getenv read at the guard) forces the poison off.
**Result: beauty is UNCHANGED in both arms — `Parse Error` at `SCRIP_FZ_FORCE=0` and at `=1`, on both inputs.** ⛔ **THE POISON IS NOT BEAUTY'S BLOCKER.** beauty's grammar patterns are *genuinely* built at runtime by `EVAL` inside `shift`/`reduce`; there is no static road for them to fall off. The defect is squarely the runtime pattern road losing β-retreat.
⚠️ `SCRIP_FZ_FORCE` is **DIAGNOSTIC ONLY, NEVER A FIX** — it is unsound by construction (the poison exists because a runtime fragment can rewrite any name). The sound cure for the same programs is the DECLARATION road (`sno_const_pat`, which never consults the poison).

## THE POISON IS STILL A REAL AND SEPARATE DEFECT (3 NEW ORACLE-REFED WITNESSES)
Independent of beauty, the poison produces **silent wrong answers** on the runtime-composed road, and `FN__PAT$1` emission is a **1:1 predictor**:
| trigger (added to an otherwise-passing program) | `FN__PAT$N` emitted | verdict |
|---|---|---|
| nothing (control) | 1 | PASS |
| `EVAL` / `CLEAR` / `CONVERT` / `$('ZZ') = 1` anywhere | **0** | **nomatch (oracle: match)** |
| indirect *read* `Z = $('ZZ')`; a second write to `P2` | 1 | PASS |
Witnesses landed in `corpus/probe/passthru/`: **`ptw_min_poison_eval`**, **`ptw_min_compose_nocap`**, control **`ptw_min_compose_ctl`** (the asm-diff pair — one line apart; `FN__PAT$1:` + `PAT$1_res:` present in the control, ABSENT in the twin; 727 vs 547 lines).
**`ptw_min_compose` SIMPLIFIED:** the s180 cursor recorded this class as "ARBNO-value **+ capture-value** β-retreat". **The capture is NOT an ingredient** — removing it keeps the failure (`ptw_min_compose_nocap`). Measured ingredient set: whole-program poison · ARBNO pattern-value in a variable · an empty-string value in a variable · runtime composition of TWO variables · the defer. `POS(0)`/`RPOS(0)` are OBSERVABILITY, not cause (without them a zero-iteration ARBNO succeeds spuriously and hides the bug).

## THE CONSTANT-DECLARATION ROAD — CN-3c HAS LANDED, AND A DOWNSTREAM GAP REMAINS
Lon's `&USER_DEFINED_CONSTANTS` lever is the sound cure for the poison class (`sno_const_pat` never consults it). **Measured state:**
- ⛔ **DOC ROT, CORRECTED HERE:** `lower_snobol4.c:987` and `:1901` still say the `sno_pat_supported` `TT_KEYWORD` arm is missing and is "the ONLY blocker" (s148 wording). **That arm LANDED with CN-12** and is present today. HQ's first pass this session believed those comments; they must be rewritten in place.
- **`TT_FNC` returns 1** — calls in pattern position (`nPush()`, `shift`) do NOT block registration either.
- **AND YET the composed-constant road still fails**, so the remaining gap is DOWNSTREAM of registration and is currently unidentified. Witnesses landed in `corpus/probe/cn/` (refs SCRIP-pinned to the semantic truth the plain control establishes — `&` forms are ORACLE_FAIL by construction, error 251):
  | witness | form | verdict |
  |---|---|---|
  | `cn_const_compose_ctl` | `A=..; B=..; P2 = A B` | PASS |
  | `cn_const_compose_leaf` | `&A=..; &B=..; P2 = &A &B` | **RED** |
  | `cn_const_compose_all` | `&A=..; &B=..; &P2 = &A &B` | **RED** |
  Constants built **inline** (`&P2 = ARBNO('a') ''`) work. Constants composed **from other constant references** do not — which is precisely the "traverse down the references and inline at compile time" half of Lon's brief.
- **A HANG:** `&P2 = &A &B` with a capture on the defer (`(*&P2 $ got)`) does not answer at all — `rc=124` at an 8s cap.

## LON'S QUESTION, ANSWERED (in-chat s182): *"were you trying to process the EVAL during constant folding via nPush/nInc/nDec/nPop and Shift/Reduce?"*
**No.** `SCRIP_FZ_FORCE` only disables the poison GUARD on the table `sno_seal_pat` already holds. It does not evaluate `EVAL` at compile time and folds nothing through the semantic functions. **Whether it SHOULD is the open design question**, and beauty's own `semantic.inc` header argues yes: *"these functions are called while building the parser patterns, **not during pattern matching**."* Their arguments at every call site are constants (`'Label'`, `1`, `7`), so `shift(BREAK(...),'Label')` is compile-time determinable in principle. Doing it = partial evaluation of the semantic layer. **NOT ATTEMPTED, NOT COSTED — it is a ruling for Lon, not a rung HQ may mint alone.**

## RECEIPTS (pristine, RT_OPT=-O0)
- **corpus m3 331/6 · m4 325/11 — EXACT match to the s181 watermark. Zero regressions.**
- passthru combo board **m3 108/112 · m4 100/112** (was 107/109 over 109 rows: +3 rows landed, +1 pass, +2 honest new reds per law 0d).
- **META SCORE 69.4** (13 suites, 1729 rows, `test-results/scorecard-s182-meta`; s179 read 69.0, s91 baseline 38.0).
- Both session edits are default-arm inert: the `SCRIP_FZ_FORCE` guard short-circuits identically when unset; the scorecard change is report-side only.

## INSTRUMENT REPAIR (the scorecard was DEAD and reporting nothing)
`scorecard_snobol4.sh report` hard-called **`gawk`, which is not installed on this box** — every report since the last gawk-bearing environment printed a header, an error line, and NO SUITE ROWS AND NO META. Fixed: `${AWK:-awk}` + the one gawk-ism (`PROCINFO["sorted_in"]`) replaced by a portable explicit top-3 max scan. **Also documented a live footgun:** every `run` truncates `<out>/results.tsv` first, so two `--suites` runs sharing one `--out` is NOT a union — the second wipes the first and `report` then scores a partial denominator that LOOKS like a whole board. HQ hit this exact trap this session before catching it.

## NEXT, IN ORDER (HQ's read)
1. **The β-retreat-into-defer road** — the M1 blocker. `Parse = *Command` SEGV on a one-byte input is the sharpest handle ever held on it; asm-diff its passing sibling `Parse = *Stmt (nl | ';')`.
2. **Lon's ruling** on partial-evaluating the semantic layer (above) — it decides whether the `&PATTERNS` conversion of beauty (queue row 36) can help at all, since beauty's patterns are EVAL-built.
3. The downstream composed-constant gap (`cn_const_compose_*`).
4. Rewrite the two stale s148 comments in place (DOC RULE).

---

# ADDENDUM — THE MONITOR SESSION (Lon's call, s182 later the same day)

**Lon, in-chat, twice: *"the IPC 2-way monitor with SCRIP<->SPITBOL help to find first divergence"* and *"For beauty.sno being so large, consider running the IPC 2-way monitor to isolate the first divergence which is directly after the FIRST bug."* HE WAS RIGHT AND THE ABLATION LANE WAS NOT GOING TO GET THERE.** Instrument audited first per ARCH-PASSTHRU (clean on a known-good witness, exact on a known-bad one) before any verdict was read from it.

## ⭐ LANDED: PB-ARGORDER (SCRIP `be455630`) — A CORPUS MOVER THE MONITOR FOUND
FIRST DIVERGENCE of a 1499-step beauty run, `case.inc:23` — **nowhere near the parser the ablation lane was digging in**:
```
icase = icase (upr(letter) | lwr(letter))          oracle: CALL upr        scrip: CALL lwr
```
**DEFECT:** the `PAT-ARG-BIND`/`PB-1s` pre-arg loop (`lower_snobol4.c:~2303`) **PREPENDED** each argument to its evaluation chain, so N pre-args evaluated **RIGHT-TO-LEFT** while `pre[]` is harvested left-to-right. SPITBOL evaluates expression operands **left to right** (manual v3.7 Ch.7). The CONCAT twin was already correct (`sx_binop` chains forward) — that asymmetry is what convicted this loop rather than the `TT_ALT` arm.
**RECEIPTS:** corpus **m3 331/6 → 332/5**, fail-set diff is ONE line — **`demo_treebank` FAIL→PASS, a pure cure, zero new fails**; m4 325/11 unchanged. `SCRIP_PB_ARGORDER=0` reverts. Witness `probe/cn/cn_alt_eval_order.sno`. Zero new globals.
**MONITOR RECEIPT:** with the cure in, the first divergence **MOVES 1499 → 1568**, landing on `main05` itself: oracle `CALL PushCounter` (enters `Parse`) vs scrip `LABEL stno=1083` (jumps straight to `mainErr1`).

## ⭐⭐ THE M1 WALL IS NOW FOUR LINES
A 3-stage probe at `main05` on the one-newline input puts the split **precisely at `RPOS(0)`**: `*Parse` alone OK on both · `*Parse *Space` OK on both · `*Parse *Space RPOS(0)` **scrip FAILS, oracle succeeds**. `RPOS(0)` is what forces the newline to be consumed, which requires **retrying and extending `ARBNO(*Command)`**. Reduced to standalone witnesses in `corpus/probe/passthru/`:
| witness | form | verdict |
|---|---|---|
| `ptw_min_arbno_fence_defer` | `P = ARBNO(FENCE(*C))`, matched via `*P` + `RPOS(0)` | **RED** (oracle match / scrip nomatch) |
| `ptw_min_arbno_fence_lit` | `P = ARBNO(FENCE('a'))` — no defer inside | **RED** |
| `ptw_min_arbno_fence_inline` | same ARBNO(FENCE()) written INLINE | PASS |
| `ptw_min_arbno_nofence` | `ARBNO(*C)` — no FENCE | PASS |
**A STORED `ARBNO(FENCE(X))` REACHED THROUGH A DEFER LOSES ITS RETRY.** The two controls isolate it exactly: inline is fine, and ARBNO without the fence is fine. This is beauty's own shape — `Parse = nPush() ARBNO(*Command) …` where `Command = nInc() FENCE(3-arm ALT)`.
**MANUAL AUTHORITY (v3.7 Ch.9, read this session at Lon's instruction):** *"If a subsequent pattern component fails to match, SPITBOL backs up, and asks ARBNO to try again. Each time ARBNO is retried, it supplies another instance of its argument pattern"* — `ARBNO(P)` ≡ `( "" | P | P P | … )`. And decisively: *"pattern matching is done exhaustively and no heuristics are applied. In particular, **deferred expressions are not assumed to match at least one character**"* — the heuristics *"often produce malfunctioning patterns when deferred evaluation is used within a pattern."* SPITBOL is ALWAYS fullscan.

## ⭐⭐⭐ THE AUTOMATIC BUG FINDER — LON'S DESIGN, BUILT AND AUDITED (`scripts/util_autobug.sh`, SCRIP `85bc4b99`)
**Lon's technique, verbatim in substance:** *"2-way monitor reports event of FIRST DIVERGENCE. The previous event then is event of the LAST AGREEMENT. The BUG is between [them] … INSTRUMENT the BB at that LAST AGREEMENT BB to fire TRACE ON … and TRACE OFF when it arrives at the FIRST DIVERGENCE BB. This trace has the BUG in it and should be REASONABLY LIMITED in size. An AUTOMATIC BUG FINDER!!!"*
**THE BRACKET NEEDS NO COUNTER AND NO NEW RUNTIME STATE** — the monitor already closes the window on both sides: it sync-steps the engines and KILLS the scrip child the instant the controller answers `S` (`mon_send_bin`'s ack arm), i.e. **at the first divergence**. The process therefore dies inside the bug's own statement, the already-registered `SCRIP_ZSM` atexit reporter runs, and the ZSM four-port ring (last `ZSM_TRACE=64` ports, execution order) **is** the bounded trace. TRACE-ON becomes "64 ports ago" instead of a counter. Runtime half = one getenv-gated call to the existing `zsm_dump()` inside the existing atexit hook.
**IT PAID ON ITS AUDIT RUN**, naming two things in `ptw_min_arbno_fence_defer`'s window:
1. **`depth` GOES NEGATIVE** at an `ω·` (node 18784: RSP restored ABOVE its activation value, `depth=-16`). A negative carve depth is structurally impossible, **nothing currently treats it as fatal**, and it is exactly the RSP-relative-to-activation-time comparison Lon specified for the ZSM (ARCH-PASSTHRU INSTRUMENTS, "owed").
2. **The ARBNO retry FIRES BUT NEVER EXTENDS** — from that point node 18352 cycles `β→γ→α·→β→γ→α·→β→ω`, no progress, then concedes. That is the `nomatch`.
⛔ Monitor-safety is in the tool's header: a `MONITOR_BIN` verdict is a verdict on a DIFFERENT program. **The tool LOCATES; it never GRADES** — every bracket is confirmed on a plain build and minted as a standalone witness before being cited.

## ALSO MEASURED THIS SESSION
- **`&FULLSCAN = 0` conformance gap:** the oracle refuses it (`ERROR 274 — value assigned to keyword fullscan is zero`, manual: *"may only be set to a non-zero value"*); **SCRIP accepts it and reports `fullscan=0`**. Reads of `&FULLSCAN` agree (1) on both. Cheap, well-defined, not M1-blocking.
- **The manual's own arithmetic parser (Ch.9 "Parsing and Translation") PASSES on SCRIP** — all five cases byte-identical to the oracle including nested parens and unary minus, and it still passes when converted to beauty's EVAL-built OPSYN idiom AND to beauty's double-capture argument-bearing deferred call (`p . thx . *Shift(t,thx)`). **This is Lon's CALCULATOR X example verbatim** (`primary = constant . *push() | "(" *exp ")"` — the `'(' *X ')'` at the very bottom of his brief). It is now the strongest PASSING control we have one structural step from beauty.

## NEXT
1. `ptw_min_arbno_fence_defer` — 4 lines, deterministic, and it IS M1. Make ZSM `depth < 0` FATAL first; it is a free invariant that convicts this class at the moment of damage.
2. Confirm the finder's two named symptoms on a PLAIN build (monitor-safety).
3. `&FULLSCAN=0` → ERROR 274.

## ⭐⭐⭐ THE FINDER PROVED THE WITNESS IS THE WALL (not by argument — by matching traces)
Ran `util_autobug.sh` on BOTH the 4-line witness and real beauty (one-newline input). **The two bug windows carry the SAME SIGNATURE:**
| | `ptw_min_arbno_fence_defer` (4 lines) | `beauty.sno` (622 lines + 16 includes) |
|---|---|---|
| bracket | DIVERGE step 6, stmt 3 | DIVERGE step 1568, `main05` (`@1080 CALL PushCounter` vs `LABEL stno=1083`) |
| first negative depth | `ω· node=18784` → **depth=−16** | `ω· node=94000` → **depth=−16** |
| then | `β→γ→α·→β` no-progress cycle on node 18352 | `β→γ→α·→β` no-progress cycle on node 93488 |
| ends | `ω` concede (depth −96) | `ω` concede (depth −720) |
**Same first-negative value (−16), same no-progress retry cycle, same concede.** This is the evidence that the 4-line witness IS M1 — previously an argument from shape, now a measured trace-signature match. Work the 4 lines, not the 622.
**FIRST ACTION (free, and it convicts at the moment of damage): make ZSM `depth < 0` FATAL.** A negative carve depth means RSP was restored ABOVE its activation value; it is structurally impossible in a correct machine, it is the RSP-relative-to-activation comparison ARCH-PASSTHRU already lists as owed, and today nothing reports it.

---

# ADDENDUM 2 — FENCE-RESUME LANDED (SCRIP `3bbba198`): THE ARBNO(FENCE()) RETRY CLASS IS CURED

**Found by Lon's IPC/ZSM method end to end**, each step handing the next its target:
1. **Monitor bracket** → first divergence at `main05` (`CALL PushCounter` vs `LABEL stno=1083`).
2. **ZSM ring** → the ARBNO's β *fires* but never *extends* (`β→γ→α·→β→γ→α·→β→ω`, rsp unchanged throughout).
3. **asm-diff** → `PAT$0_β: jmp PAT$0_ω` — the blob conceding wholesale.
4. **A getenv-gated `RESUME-GATE` probe** → `body_root=(nil)` for the fenced twin vs a live tier-1 carrier for the passing control. That printed the root cause outright.

**THE DEFECT — TWO WHOLESALE SHAPE REFUSALS, BELT AND SUSPENDERS, both asking "is there a FENCE1 *anywhere* in this blob":**
- **the BUILDER** (`lower_snobol4.c:2624`): `pfenced = sno_pat_contains_fence(pat)` published `body_root = NULL` for the WHOLE graph — no resume surface at all;
- **the BELT** (`emit.cpp:3341`): `_f1` refused the resume arm on the same anywhere-test.
With no resume surface the β-dispatch emitted `PAT$N_β: jmp PAT$N_ω`, so **ARBNO conceded WITHOUT EXTENDING**. ⛔ This is precisely what law 0d forbids ("no admission filter, no shape refusal").

**THE MANUAL IS THE AUTHORITY** (v3.7 Ch.9/18): FENCE *"fails if the scanner has to **back up through** it"* — but ARBNO's β does not back through anything; it **extends forward** with one more instance at the current cursor (`ARBNO(P)` ≡ `( "" | P | P P | … )`). Two different motions, and an anywhere-scan cannot tell them apart.

**NARROWED, NOT DELETED** — the refusal owns a named 7-mover class. The carrier is published only when the first real body node is itself a **tier-1 generator** by `zdp_seam_tier`, the ONE lattice authority for "this box's β EXTENDS". Every other fenced shape keeps the old NULL exactly, and the fence template's own β still concedes if reached, so cut semantics are untouched.

**RECEIPTS:** `ptw_min_arbno_fence_{defer,lit}` **nomatch → match** (oracle-identical) · both controls unchanged (inline; ARBNO-without-fence) · **the 7-mover class 114/119/129/130/148/149/150 ALL GREEN** · corpus **m3 332/5 · m4 325/11 with the fail-set IDENTICAL to pre-fix** · `SCRIP_FENCE_RESUME=0` reverts both halves.

⛔ **BEAUTY IS STILL `Parse Error`** on every input class. This cured a real, named, oracle-differential class and did **not** finish M1. The loop continues: re-run `util_autobug.sh` for the next divergence.
⛔ **AND A CORRECTION TO ADDENDUM 1, KEPT VISIBLE:** it named `depth < 0` as "structurally impossible" and proposed making it FATAL. **That was wrong.** `runtime_init.c:112` documents the ZSM origin datum as ONE cell, so a nested activation's ORIGIN overwrites its caller's and the caller's later ports read against the callee's datum — Lon's own s136 ruling: *"I know RSP changes into a function but just ignore all that"*, noise "bounded to post-call ports and READ AS NOISE". The negative depth is an instrument artefact, not the wound. The load-bearing half of that trace was always the second symptom: **the retry that fires but never extends.**
