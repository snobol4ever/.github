# FINDING s122 (2026-08-16) — MILESTONE 1's `Parse Error` IS THE `probe/arbnostore` CLASS, AND FOUR INHERITED CLAIMS ARE STALE

**Seat:** Claude Opus 5, Lon in-chat ("using the IPC sync-step MONITOR, take us home"). **Measured at** SCRIP `ce0b6f93`, corpus `9c3aa509`, x64 oracle live. Build green (`scrip` + `out/libscrip_rt.so`), gdb 15.1 present.

This session ran a MONITOR-FIRST hunt to completion on the Milestone-1 blocker and stopped at the localization
per END-OF-CONTEXT LAW (mint the repro, route it, stop). **No code was changed.** Everything below is measured,
with the command that produced it.

---

## 1. ⭐ THE MILESTONE-1 BLOCKER IS NOW COMPOSED END-TO-END (R-2 called this "unlocalized")

`beauty.sno < beauty.sno`, m3, at HEAD: **rc=0, 10 lines / 278 bytes** against the oracle's 622 lines / 40971 bytes.
It clears the 7-line comment header, then emits `Parse Error` at the first non-comment line (`-INCLUDE 'global.inc'`).

The chain, each link measured:

| link | site | what |
|---|---|---|
| the failing match | `beauty.sno:614` | `main05  Src  POS(0) *Parse *Space RPOS(0)  :F(mainErr1)` |
| what `*Parse` derefs to | `beauty.sno:225` | `Parse = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop()` |
| the defect class | `corpus/probe/arbnostore/` | stored `ARBNO(<non-literal>)` takes its null match and never extends |

**`ARBNO(*Command)` stored in `Parse`, reached through `*Parse` — that is exactly `arbno_defer_stored_red`.**
Milestone 1 is therefore blocked on the arbnostore class and nothing else on this line. R-2's two "stacked
defects" reduce to one on the beauty path: the `probe/defval/` bare-deferred-value SIGSEGV is a *different*
line and does not gate `main05`.

**ORACLE HALF RE-CONFIRMED** at HEAD (s119's claim holds): `sbl -bf beauty.sno < beauty.sno` → rc=0,
622 lines, 40971 bytes, **byte-identical to the input file**. Fixed point is real and reproducible.
⛔ Note the flag: `-bf`, not `-b`. With plain `-b` the oracle **SIGSEGVs (rc=139)** after 34 lines — a
seat that copies the `-b` invocation from `RULES.md`/`REPO-SCRIP.md` will conclude the oracle is broken.

## 2. ⭐ THE MONITOR WORKS — ON THE WITNESS, VIA `spl scr`, NOT ON BEAUTY

`scripts/test_monitor_2way_spitbol_vs_run.sh /tmp/w/arbstar.sno` bracketed the bug on the first try:

```
| step | stno | spl              | scr              | source                                  |
|    7 |    4 | LABEL stno=INT=4 | LABEL stno=INT=4 | Src POS(0) *Pat RPOS(0)  :F(BAD)        |
|  > 8 |    4 | LABEL stno=INT=5 | LABEL stno=INT=6 | Src POS(0) *Pat RPOS(0)  :F(BAD)        |
```

Both engines enter statement 4; SPITBOL leaves to stno=5 (success), SCRIP leaves to stno=6 (`:F` arm).
Per the MONITOR-FIRST theorem the bug is inside statement 4's match. **This is the route around MON-CAP:**
the monitor is dark on `beauty.sno` but fully alive on a 7-line witness of the same class, and
`test_monitor_2way_sync_step_bin.sh` is not the only door — it hard-requires `csnobol4` (token-gated, absent),
while `test_monitor_2way_spitbol_vs_run.sh` uses the oracle we already clone and needs no credential.

## 3. ⛔ FOUR INHERITED CLAIMS ARE STALE — RE-MEASURE BEFORE INHERITING (VERIFY-INHERITED-BLOCKERS)

**(a) MON-CAP is no longer a SIGSEGV.** R-6 records `MONITOR_BIN=1` alone turning `scrip --run beauty.sno`
into **rc=139 SIGSEGV for any input including /dev/null**, with RIP on a stack address via `rt_outer_call`.
At HEAD that is **falsified**: the run is **rc=1, `** Error 22 in statement 0 / Undefined function called`**.
Trivial programs and DEFINE-in-`-INCLUDE` probes are clean under the monitor. The monitor is still dark for
beauty, but the failure mode has moved and the s119 gdb note no longer describes it.

**ROOT CAUSE NAMED (the thing to fix for MON-CAP):** `MONITOR_BIN` is **not behaviour-preserving**.
`src/driver/scrip.c:1608` and `:1756` read `int n_gva_m3 = getenv("MONITOR_BIN") ? 0 : gva_count();` — setting
the monitor variable forces **GVA off in m3**, which re-routes every call site into legacy arms. The templates
already narrate this in `bb_call_proc_staged.cpp:463/742` ("MONITOR_BIN forces n_gva_m3=0 … the site falls
HERE, to rt_proc_call_open with flat rcx/rdx wires"). So the monitor perturbs the program it is meant to
observe, and MONITOR-FIRST's premise (same program, observed) does not hold for any program whose failure
depends on the call path. There is **no standalone GVA killswitch**, so GVA-off cannot today be tested apart
from the taps. MON-CAP = decouple these two, then re-measure Error 22.

**(b) R-8's SIG11 rows are green.** The s105 census lists `&`→SIG11, `@`→SIG11, `~`→SIG11, rebind-twice→SIG11.
At HEAD `corpus/probe/opsyn/` runs **14 PASS / 5 FAIL**, and all four of those rows **PASS**:
`opsyn_bin_amp`, `opsyn_bin_at`, `opsyn_bin_tilde`, `opsyn_rebind_twice`. Still RED: `opsyn_bin_pct` (prints `0`),
`opsyn_bin_pound` (prints `0 0`) — the grammar-hard-wired-to-arithmetic silent-wrong-answer class R-8(a) names —
plus `d_unary`, `opsyn_builtin_target`, `opsyn_unary_target` (rc=1).
⭐ **Consequence for R-2:** `semantic.inc` does `OPSYN('&','reduce',2)` and beauty.sno:225 uses that `&` inside
the `Parse` pattern, so R-8 was correctly flagged "on the beauty path" — **but that half is no longer red.**
R-8 is not what is blocking Milestone 1. Do not open R-8 for beauty's sake.

**(c) `SCRIP_DEFER_RESUME=1` does not move beauty.** s121 landed the stored-pattern resume mechanism opt-in.
Run against the real target: `SCRIP_DEFER_RESUME=1 scrip --run beauty.sno < beauty.sno` → **byte-identical to
the default run** (10 lines, 278 bytes, same `Parse Error`). The mechanism does not cover
`ARBNO(*Var)`-inside-a-stored-blob. Negative result recorded so it is not re-tested.

**(d) `probe/arbnostore` reproduces exactly as s120 documented** — 4 RED / 4 GREEN at HEAD
(`arb_stored_red`, `arbno_defer_stored_red`, `arbno_var_stored_red`, `defer_star_arb_red` RED;
`arb_inline_green`, `arbno_lit_stored_green`, `arbno_var_inline_green`, `span_stored_green` GREEN).
Independently re-derived this session from beauty before that directory was opened, and the ladders agree —
so the s120 characterisation is sound and is **not** part of the retraction in (a)–(c).

## 4. TWO PROPERTIES OF THE DEFECT THAT NARROW THE FIX

**m3 ≡ m4.** The witness gives `Parse Error` in both modes (m4 via `--compile` + `gcc -no-pie`, runs clean).
This is **not** a mode gap — it is a shared LOWER/emitter defect, so R-6 does not gate it.

**Zero bombs.** `grep -ci bomb` on the emitted `.s` is **0**. Nothing declines; the emitter believes it
compiled this correctly. This is the **silent-wrong-answer** class, not a known `x86_bomb` decline — which is
why it survived to Milestone 1 while the loud ARBNO declines in R-4(a) were being counted.

**Ingredient isolation** (each row an independent program, oracle-anchored, `Src='ab'`):

| # | `Pat =` | matched as | verdict |
|---|---|---|---|
| A | `ARBNO(*Command)` | `*Pat` | **FAIL** — spl `MATCH`, scr `Parse Error`  ← the beauty shape |
| B | `ARBNO('a' \| 'b')` | `*Pat` | PASS — storage alone is fine |
| C | `ARBNO(*Command)` | inline, no `*Pat` | PASS — deferred element alone is fine |

**Neither ingredient is sufficient; the defect needs both.** And the iteration ladder shows it is not a
backtracking-only story: with `Src=''` the match **succeeds** (null arm live), with `Src='a'` — a single
element, no retry required — it already **fails**. The stored blob's deferred element never matches once.

## 5. WHERE THIS ROUTES

**R-4(b)** (`PAT$N` stored-pattern-blob class — "captures/ARBNO inside a separately-compiled pattern blob,
no enclosing MATCH_BEGIN in that graph, `op_*_frame_off==-1`"), which is marked LANDED s97 (`be18fcb6`).
The blob-as-own-activation landed; **the deferred element inside a stored ARBNO did not**. Treat R-4(b) as
having a named residual, with `arbno_defer_stored_red` as its gate and `beauty.sno` as its payoff.

**Next action for the seat that picks this up:** the bracket is already computed (statement 4 of
`probe/arbnostore/arbno_defer_stored_red.sno`), so start at MONITOR-FIRST step (2) — gdb with a spin/ignore
counter at the ARBNO element-match site inside the stored blob, and answer one question: on the first
iteration, why does the deferred element's match report failure. Compare against `arbno_lit_stored_green`,
whose only difference is that the element is a literal; an instruction identical in both is exonerated.

---

# ⭐⭐⭐ ADDENDUM — ROOT CAUSE FOUND WITHOUT gdb: **THE STORED-PATTERN BLOB'S β PORT IS A DEAD END**

The prescribed cheapest-discriminating-experiment (RULES: "a diff of their emitted asm") answered it outright.
Minimal pair, differing only in literal-vs-deferred element:

- `arbno_lit_stored_green.sno` — `C = ARBNO('a')` → **no blob at all.** The pattern is folded INLINE into `main`,
  ARBNO on ζ-SPINE (`n6_match_arbno_α: sub rsp,16`, slots `[rsp+0]/[rsp+4]`). 229 lines of asm. PASSES.
- `arbno_defer_stored_red.sno` — `C = ARBNO(*D)` → the deferred element forces a **separately-compiled blob**
  `FN__PAT$0`, ARBNO on the blob's own RBP activation (`[rbp-32]/[rbp-28]`). 461 lines. FAILS.

**So the literal case is green because it never becomes a blob.** The green sibling exonerates nothing in the
blob path — it does not exercise it. That is why this class survived every inline ARBNO gate.

## The emitted blob, four ports (`grep -n 'PAT\$0' /tmp/r.s`)

```
FN__PAT$0 / PAT$0_α_body:  push rbp; mov rbp,rsp; sub rsp,40
                           mov [rbp-8],r10   ; γ wire saved
                           mov [rbp-16],r11  ; ω wire saved
n0_match_arbno_α:          mov [rbp-32],r14d ; start cursor
                           mov [rbp-28],r14d;  jmp PAT$0_γ    ← NULL MATCH taken, go forward
n0_match_arbno_β:          jmp n1_match_defer_α               ← THE RETRY EDGE. never reached.
n0_match_arbno_af:         ... jmp PAT$0_ω                    ← interior exhaustion routes to ω ITSELF
PAT$0_res:                 mov r10,[rsp+8]; mov r11,[rsp+16]; mov rbp,[rsp+24]; add rsp,32
PAT$0_β:                   jmp PAT$0_ω                        ← ⛔ DEAD END
PAT$0_γ:                   ... push rbp; push r11; push r10; lea rax,[rip+PAT$0_res]; push rax
                           mov rbp,[rbp+0];  jmp r10
PAT$0_ω:                   mov rsp,rbp; pop rbp;  jmp r11
```

**The suspension machinery is already 90% built and correct.** γ pushes a genuine resume address
(`PAT$0_res`) so the caller *can* re-enter the blob, and `PAT$0_res` correctly restores r10/r11/rbp and
unwinds the 32-byte suspension record. Then it **falls through into `PAT$0_β`, which unconditionally
`jmp PAT$0_ω`** — reports total failure — while the ARBNO's own retry edge `n0_match_arbno_β` sits three
instructions away, unreachable. **The blob can be resumed; it just refuses to retry when it is.**

This explains every row of the ladder exactly:
- `Src=''` → the null match already satisfies `RPOS(0)`, no backtrack is ever requested → **MATCH** ✔
- `Src='a'` → outer `RPOS(0)` fails, backtracks into the blob, hits `PAT$0_β` → ω → **NOMATCH** ✔ (and this
  is why it fails at ONE element, with no retry required — it is not a backtracking-depth bug)
- literal element → never a blob → **PASS** ✔

## The fix shape (small, and safe by the blob's own construction)

`PAT$0_β` must route to the blob graph's interior last-choice-point (here `n0_match_arbno_β`), not to ω.
⭐ **ω remains correct as the exhaustion answer and needs no guard**, because the interior already routes its
own exhaustion out: `n0_match_arbno_af … jmp PAT$0_ω`. So β→interior cannot leak a hung match; a blob whose
interior has no choice point still reaches ω on its own.

**Start here:** `src/emitter/emit.cpp:2288` `blob_frame_scope()` — the file's own comment calls it *"R-4(b)
THE ONE AUTHORITY for 'this graph is a stored-pattern PAT$ blob activation'"* (used at `:2277`). The β-port
emission for blob-scope graphs is what stubs to ω. **ONE AUTHORITY law applies — fix it at the port
emission, do not special-case ARBNO**; `ARB`, `ARBNO(D)` and `defer_star_arb` are all RED for this one reason,
and all four should go green together.

**Gate for the fix:** `probe/arbnostore/` 8/8 (4 RED → GREEN, 4 GREEN unmoved) · `probe/dv/` and `probe/mrbp/`
unmoved · killswitch byte-identity is N/A (shape change) ⇒ md5 blast radius over crosscheck+patterns+probe,
BY SET, ZERO PASS→fail · then re-run `beauty.sno < beauty.sno` both modes: it should advance past line 8.
⛔ Milestone 1 needs the WHOLE 622-line fixed point — expect the next blocker behind this one, and re-measure
rather than assuming this is the last.
