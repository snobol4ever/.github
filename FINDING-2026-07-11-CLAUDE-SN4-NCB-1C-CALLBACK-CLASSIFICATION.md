# FINDING 2026-07-11 — NCB-1c: THE CALLBACK CLASS, CLASSIFIED

AUTHORS: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
GOAL: `GOAL-SNOBOL4-BB.md` PHASE 1 → RUNG NCB-1c. Base: SCRIP `4e84e986` (NCB-1b landed).
STATUS: **CLASSIFICATION ONLY — NO CODE MOVED.** The rung mandates a written (a)/(b) verdict for every site
before anything is touched. This is that document.

---

## THE LEDGER AS THE GATE SEES IT (`scripts/test_gate_no_c_to_bb.sh`, run at this HEAD)

7 groups / 13 sites. **The gate counts TRANSFERS (the `p->fn(fb,entry)` inside rt.c), not CALLERS.** NCB-1c
moves CALLERS. A transfer site disappears only when its trampoline loses its LAST caller. Keep this distinction
or the rung will be graded against the wrong number (see §5).

---

## 1. THE MATCHER — 3 sites, `src/runtime/pattern_match.c`

Each sits **directly under exactly one emitted box** (verified: these leaves have no other caller in the tree).
That is the HOIST precondition, and all three meet it. They differ only in TRANSFER MULTIPLICITY.

| # | Site | Box (sole caller) | Construct | Transfers per invocation | Verdict |
|---|------|-------------------|-----------|--------------------------|---------|
| **M1** | `rt_defer_match` :745 + :753 | `bb_match_defer.cpp:56` | `*X` deferred eval; DT_X EXPRESSION referenced in a match | **up to 2, sequential** | **(a) HOIST** |
| **M2** | `rt_cap_assign_cursor` :668 | `bb_match_capture.cpp:57` | capture target is a computed name `*VAR` (`rt_g_want_name=1`) | **≤ 1** | **(a) HOIST — do FIRST** |
| **M3** | `rt_dcap_flush_from` :584 (via `rt_dcap_end_ok`) | `bb_match_release.cpp:24` | `.` conditional-assignment commit at match success | **0..N — a PUMP** | **(a) HOIST — do LAST** |

**MANUAL (the semantics arbiter, read for this rung):**
- *Unevaluated Expressions* (p.85–86): `*N` is fetched **at every match-time reference**, not once — "when NPAT is
  used in a pattern match, the deferred evaluation operator fetches the then current value of N." So M1's transfer
  fires on **every** arrival at that box, including every backtrack retry. It is a hot edge, not a one-shot.
- *Expression datatype* (reference section): `E = *(LEN(K) POS(M))` compiles to a call-and-nothing-more; the calls
  happen **only when E is referenced in a pattern match (or EVAL'd)**, and the pattern structure is built *then*.
  ⇒ M1's `val.v == DT_X` arm (:753) is that rule, and the evaluation may **build patterns, call user functions
  with side effects, and re-enter the matcher** (recursive `*group`, DP-7).
- *Conditional assignment* (Ch.6): performed **only when the entire match succeeds** — which is exactly why M3's
  transfers are a deferred batch at RELEASE rather than N scattered calls.

⇒ **These are NESTED EVALUATIONS, not tail calls.** The hoisted box must tolerate re-entry. It does: after the
hoist the transfer is an ordinary BB→BB call, and a nested match is just a deeper box graph. This is the
argument that the hoist is SAFE, and it is the reason the C-trampoline (which forces a C frame to sit under the
re-entry) is actively harmful here rather than merely inelegant.

**SHAPE (all three; the NCB-1b `bcps_det_arm` REUSED VERBATIM — F5 stands, zero new encoders):**
```
M2 (the proof):   rt_cap_open(name,…) -> entry|0      ; sets rt_g_want_name inside the leaf
                  [entry ? NCB-1b arm : skip]
                  rt_cap_finish(nm, base, len)         ; clears want_name, does the assign
M1 (2-round):     loop { rt_defer_open(varname,ival) -> {entry|0, val} ; entry ? arm : break }
                  rt_defer_apply(val, cur_delta) -> int
M3 (the pump):    while ((i = rt_dcap_flush_next()) >= 0) { entry = rt_dcap_open(i); arm; rt_dcap_resolve(i, nm) }
```
`rt_g_want_name` is a global set/cleared **around** the transfer today — it must move INSIDE the open/finish
leaves, or the emitted window will straddle it. This is the one way to get M2 quietly wrong.

**ORDER: M2 → M1 → M3.** M2 is one transfer with no loop: it proves the arm inside a matcher box for the cost
of the smallest diff. M3 puts an emitted *loop* in `bb_match_release` and must not be attempted first.

---

## 2. BY-NAME DISPATCH — SNOBOL4-reachable, `src/runtime/by_name_dispatch.c`

The dispatcher's contract today is `int handled; *out = value`. Four sites are **already in TAIL POSITION**:

| # | Site | Construct | Shape | Verdict |
|---|------|-----------|-------|---------|
| **B1** | :1327 | by-name proc call (`wname`) | `*out = rt_call_proc_descr(…); return 1;` | **(a) HOIST** |
| **B2** | :2008 | indirect/computed proc (`newproc`) | same | **(a) HOIST** |
| **B3** | :2121 | indirect/computed proc (`tproc`) | same | **(a) HOIST** |
| **B4** | :4725 | **`APPLY`** | same | **(a) HOIST** |

**ONE protocol change buys all four:** the dispatcher's return becomes 3-way —
`HANDLED` · `NOT_MINE` · `NEEDS_TRANSFER{name, nargs}` — and the emitted by-name box performs the transfer with
the NCB-1b arm, storing the result where `*out` went. Cheapest family in the whole rung: the C side is already
tail-shaped, so no C control flow has to survive across the transfer.

| # | Site | Construct | Verdict |
|---|------|-----------|---------|
| **B5** | :4707 | `EVAL(E)` where `E` is DT_X (manual EVAL rule 2: an unevaluated expression is evaluated with current values) | **(a) HOIST — but OWNED BY NCB-3.** Its invoke IS what NCB-3 moves. Do not cut it twice. |
| **B6** | :750, :764, :772, :2782, :2785 | generator α/β riders (`rt_proc_call_gen_h`, `rt_proc_resume_frame_h`) | **OWNED BY NCB-2** (as the goal file already says) |

**⚠ FINDING (design constraint on B1–B4, else NCB-2 re-cuts this function):** B6 rides the SAME dispatcher.
The 3-way verdict enum must therefore carry a **GENERATOR transfer** case (entry + activation slot) from day
one, not just the deterministic one. Design it once, in NCB-1c, and NCB-2 fills in the arm.

---

## 3. THE RAKU OO DISPATCHER — **4 sites the rung did not know about**

The rung lumped "by_name_dispatch.c APPLY/`$`-indirect/DT_X ×10". Four of those are **not SNOBOL4-reachable at
all** — they are the Raku OO method dispatcher, and they are **inside C loops**, not in tail position:

| # | Site | What it is | Why it is not a tail call |
|---|------|-----------|---------------------------|
| **R1** | :537 `invoke_method_proc` | method-proc fallback (no proc-table entry) | returns the value, but reached only via the OO path |
| **R2** | :544 | native-fn method | same |
| **R3** | :563 | **`__TWEAK` ancestor-chain pump** | inside a `for` loop walking the class chain; **result discarded** |
| **R4** | :591 | named-argument method call | inside the named-arg binding loop; result discarded |

**VERDICT: (b) SANCTION — NAMED, WITH A REASON AND AN OWNER.**
> *"Raku OO method dispatch. The transfer sits inside a C-driven ancestor/named-arg walk whose results are
> discarded; the 3-way NEEDS_TRANSFER protocol does not fit a mid-loop discarded call. Hoisting these means the
> OO dispatcher itself becomes an emitted pump — a `GOAL-RAKU-BB.md` design question, not a SNOBOL4 one."*

Re-assign to GOAL-RAKU-BB. **Do not let it balloon this rung** (the rung's own standing instruction).

---

## 4. THE DRIVER HOOK — `src/driver/driver_hooks.c`

| # | Site | Construct | Verdict |
|---|------|-----------|---------|
| **D1** | :72, :73 | `_usercall_hook` — try `FNCEX` name; **on FAIL retry the `FUNC_ENTRY` alias** | **(a) HOIST — RIDES B1–B4** |

Installed as `g_user_call_hook` (scrip.c:605); invoked from `core.c:2582/:2587` on the by-name call path — i.e.
**reached from an emitted box through the same channel as B1–B4**, so it joins the same 3-way protocol.
Its "call; if FAIL, call the alias" is the **same 2-round open-loop as M1**. One primitive, two customers.

---

## 5. ⛔ THE EXPECTATION CORRECTION — "V1/V3 die, ledger drops" IS ONLY HALF TRUE

F7 predicted V1/V3 die and V4 keeps only its generator sites. Verified against the live tree:

- **V1 `rt_call_named_proc` — M1, M2, M3, D1 are its LAST FOUR CALLERS.** NCB-1b already took its template
  callers. All four land ⇒ its transfer (rt.c:861) goes ⇒ **group V1 dies. 7 → 6.**
- **V4 `rt_call_proc_descr` CANNOT DIE THIS RUNG.** Even with B1–B4 hoisted, **R1–R4 (Raku) keep calling it**, so
  rt.c:532 stays lit. V4 survives with its Raku callers + its generator sites. **NCB-2's advertised "4 → 1" is
  therefore unreachable while the OO dispatcher is C-driven** — that is a real dependency between GOAL-SNOBOL4-BB
  and GOAL-RAKU-BB, and it was not previously recorded anywhere.
- **V2 `rt_call_proc_direct` is DEAD CODE** (F7, re-confirmed: zero callers). Deleting it is a free 6 → 5, but it
  is a DELETE ⇒ **Lon's call** under PARK-NEVER-DELETE. Not taken unilaterally.
- **V3 `rt_call_named_proc_sl`** is template-only ⇒ NCB-1d, unchanged.

**HONEST GATE FOR NCB-1c: 7 → 6 groups** (V1 only), *plus* the four Raku sites moved from "unclassified residue"
to "named sanction." Any claim of 7 → 4 from this rung is false.

---

## 6. LANDING ORDER (proposed; no code moved yet)

1. **M2** — smallest diff, proves the NCB-1b arm inside a matcher box. Gate: crosscheck watermark-identical.
2. **B1–B4 + D1** — one 3-way dispatcher protocol (with the NCB-2 generator case designed in), five call sites.
3. **M1** — the 2-round open-loop (shares D1's primitive).
4. **M3** — the emitted pump in `bb_match_release`.
5. Re-run gate: expect **V1 gone, 7 → 6**. Regen `.s` artifacts (RULES step 4 — every step above touches codegen).

Each step: full crosscheck both modes, watermark-identical (m3 284/7, m4 283/7/1, DIVERGE=1/1017), sno 7/7 ×2,
icon 12/12 ×2, prolog 5/5 ×2. **No step is done while it leaves a red it did not have before.**

---

## 7. LANDED — M2 (SCRIP `13f71c66`, artifacts `d6ccf22a` + corpus)

`rt_cap_assign_cursor` → `rt_cap_open` (fbytes|0) + `rt_cap_finish` (epilogue + assign); the COND/IMM arm of
`bb_match_capture` carries the NCB-1b window verbatim. Zero new encoders (F5 holds again). Watermark identical
both modes, failing set identical, sno/icon/prolog smokes green ×2. `rt_g_want_name` subtlety: `rt_nret_fix`
RESTORES the snapshot at epilogue, so finish must clear it after — the old code's trailing `= 0` was load-bearing.

**FINDING — THE `*` CAPTURE BRANCH HAS ZERO LIVE COVERAGE AND A PRE-EXISTING BOMB (SZ-3-class):**
No crosscheck test reaches `rt_cap_open`'s `*` arm (138's `*expr` is a deferred PATTERN = M1's site; 140/141
fail upstream in LOWER). A minimal probe from the manual's own NRETURN idiom (p.133 `SUBJECT ? PATTERN . STORE()`):
```
        DEFINE('STORE()')                :(MAIN)
STORE   STORE = .DUMMY                   :(NRETURN)
MAIN    'ABCDE' ? LEN(3) . *STORE()
        OUTPUT = DUMMY
END
```
Oracle: `ABC`. SCRIP m3: `[IDX] BOMB rt_assign_var: lvalue is not a variable (dtype=0)` — **IDENTICALLY pre- and
post-M2** (verified by stash/rebuild/run). The pseudo-proc `EXPR$n` chain does not propagate the NRETURN by-name
result to its own result cell — exactly SZ-3's "capture-write is name-only, needs a run-chain variant."
**This probe is a smaller SZ-3 reproducer than test 140** (no EVAL, no TABLE): whoever lands SZ-3, start here.

---

## 8. LANDED — M1 (SCRIP `0d3eca75`, corpus `f3abb166`)

`rt_defer_match` → `rt_defer_open` / `rt_defer_step` / `rt_defer_close`; `bb_match_defer`'s value path carries the
NCB-1b window **in a loop** (`open → [sub rsp → rt_frame_prep → call rax → step]* → close`). Round discipline is
the old body exactly: one `*`-triggered call, at most one DT_X-triggered call (`dtx_used`) — a second DT_X result
is stored, not re-called, and falls out of close as -1, as before. State on a LIFO: per the manual, a deferred
expression may itself run a match, so the box re-enters itself.

⚠ **This box ALREADY had an x86 BB→BB bridge** — the `call rcx` blob path (compiled-pattern DEFER). Only the
*value* path was still routed through C. M1 makes the two paths symmetric.

**WATERMARK UP: m3 285/7, m4 284/7/1** (was 284/283) — the +1 is the new test, not a fixed red.

---

## 9. ⛔⛔ CRITICAL FINDING — AN EMITTED BB→BB TRANSFER DOES NOT PRESERVE r13/r14/r15

**An `xa_flat` callee pushes only its frame register (plus an optional display reg). It therefore does NOT honor
the SysV callee-saved contract for r13/r14/r15.** The matcher keeps its **cursor in r14d** and scratch in r15d
(77 and 16 template uses respectively). So any emitted transfer made **while a matcher cursor is live** must save
those registers ITSELF.

**The C trampoline hid this by accident.** `rt_call_named_proc` is a C function; whether the caller's r14 survived
depended on whether GCC happened to allocate r14 in that function (if it did, GCC's own push/pop restored it
across `p->fn`). Nothing in the design guaranteed it.

**ABLATION-PROVEN, and it is a WRONG ANSWER, not a crash.** With the save removed:
```
'AABZ' ? 'A' *F() 'Z'      (F's body runs a nested match)   →   SCRIP: fail2      ORACLE: match2
```
**…and the FULL 292-test crosscheck passes anyway.** The corpus could not see it. New test
`corpus/crosscheck/patterns/161_pat_defer_fn_nested_match.sno` (oracle-minted `.ref`) closes the hole.

**BINDING ON EVERY REMAINING NCB RUNG:**
- **M3** (the `bb_match_release` pump) — same exposure, same save.
- **NCB-2's generator α/β arms** — a generator resumed from inside a pattern has the cursor live. **Same save, or
  the same silent wrong answer.**
- **NCB-1b's `bcps_det_arm` is SAFE ONLY BY ACCIDENT** — a statement-level proc call has no live matcher cursor.
  The moment a det call site is reached with r14 live (SZ-3's `*inner()` in a capture), it acquires this bug.
- The real fix is a *convention*, not four copies of three pushes: either (i) `xa_flat` preserves r13/r14/r15 like
  a well-behaved SysV callee, or (ii) an explicit "BB→BB transfer clobbers the matcher regs" rule with ONE
  encoder-level dance (`x86_xfer_enter()` / `x86_xfer_leave()`) that every arm calls. **Proposed for Lon: (ii)
  first (cheap, greppable), (i) as the ZB-OWN/NCB-5 end state.** Recorded, not taken unilaterally.

---

## 10. LANDED — M3 + THE `x86_xfer_*` ENCODER (SCRIP `ad7dc2c0`)

`rt_dcap_flush_from` → `rt_dcap_end_ok_open` / `rt_dcap_step` / `rt_dcap_end_ok_close`; `bb_match_release` PUMPS
the 0..N computed-name commits. Flush cursor on a LIFO — the old C loop was re-entrant *through its C locals*
(a `*VAR` proc body may run its own match and commit its own pends); a static cursor would have corrupted that
silently. `g_rt_dcap_n` re-read every iteration, exactly as the old for-loop did.

**`x86_xfer_enter()` / `x86_xfer_leave()` landed in `x86_asm.h`** (beside the align dance): the r13/r14/r15 save
is now ONE greppable encoder pair instead of copy-pasted pushes. `bb_match_defer` refactored onto it. **NCB-2's
generator arms must use it** — a generator resumed inside a pattern has the cursor live.

### ✅ THE MATCHER IS NOW FREE OF C→BB PATHWAYS
All four `pattern_match.c` callers of `rt_call_named_proc` are gone (M1 ×2, M2, M3). `grep` leaves exactly the
three survivors this classification predicted in §5: `by_name_dispatch.c:4707` (EVAL DT_X → **NCB-3**) and
`driver_hooks.c:72/73` (**D1**). V1 dies when those go — not before. The prediction held.

### ⛔ FINDING — `x86_zls2_release_to_call` RESETS `rsp`; AN XFER WINDOW MUST OPEN *AFTER* IT
It does not merely call: it emits `mov rsp, [frame+off]` (the statement's zeta mark), closing and re-opening the
align dance around itself. Pushes taken BEFORE it are abandoned by that reset, and the matching pops then read
garbage off the zeta region — **mode-4 segfault, mode-3 silent corruption** (m4 went 284 → 167/124 before the
cause was found). Cost of learning it: one full crosscheck. **Any template splicing an xfer window into a box
that also releases zeta must order them: release first, save second.** Generalization for NCB-2/ZB-OWN: an rsp
reset and a C-stack save are the same resource — never interleave them; the encoder pair does not and cannot
know what a sibling helper did to rsp.
