# FINDING 2026-07-31i (s163) — PL: NO SINGLE KIND UNLOCKS A SINGLE RUN, AND THE ZD ARM BYPASSES THE ENTIRE PL-SINK LADDER

**Session:** s163 · **Baseline:** SCRIP `510c38fe` (clean at start) · **Build:** `-O0` throughout (Makefile default; no `-O1`/`-O2` used or sought)
**Lon directive (verbatim):** *"Climb the ladder to NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. Continue."*

---

## HEADLINE

Two measurements, each of which kills a queued rung *before* it was spent:

1. ⭐⭐ **NO SINGLE IR KIND UNLOCKS A SINGLE ZD RUN.** The minimum viable admission is a **PAIR**. The queued `NEXT (b)` — *"ZD-PL-1 `IR_VAR_REF` (41%)"* — would have written a template ZD arm, passed every gate, and moved the armed count by **exactly zero**.
2. ⭐⭐ **THE REAL BLOCKER IS NOT ADMISSION — IT IS THAT THE ZD ARM EARLY-RETURNS PAST THE ENTIRE PL-SINK LADDER.** Admitting `IR_CALL_BUILTIN_PROLOG` (which gates **100%** of runs, so nothing unlocks without it) routes every `$unify` / `$unify_lst` / `$trail_mark` / `$ix_g` through generic `rt_call_arr` by-name dispatch, discarding PL-SINK-1/2/4/8 and PL-REGAIN-5 — **and every correctness gate stays green**, because `rt_call_arr` is correct, only slow.

---

## (1) THE INSTRUMENT WAS WRONG: NODE FREQUENCY CANNOT RANK AN ALL-OR-NOTHING GATE

s162 ranked the gap by **node frequency** and named `IR_VAR_REF` the elephant (4168 nodes, 41%). But `zd_plan` is **all-or-nothing per run**: a run arms iff *every* node in it passes `zd_wl_kind`. The quantity that decides a rung is therefore **RUN-GATING** — in how many runs does this kind appear at all — not how many nodes it contributes.

Census re-run this session over the 185-program rung corpus (`corpus/programs/prolog/rung*.pl`), grouping each declined run's **full blocking SET** rather than its first blocker:

| Kind | Runs it blocks | % |
|---|---|---|
| `IR_CALL_BUILTIN_PROLOG` | **185** | **100%** |
| `IR_MOVE_LABEL` | 157 | 85% |
| `IR_VAR_REF` | 130 | 70% |
| `IR_VAR` | 93 | 50% |
| `IR_CALL_PROC_STAGED` | 91 | 49% |

**185 programs → 185 declined runs, exactly one per program.** Confirms gate A independently: only `main` reaches the run loop; every predicate graph early-returns on `flat_jmp_entry` before it.

### THE UNLOCK TABLE (a run unlocks iff its ENTIRE blocking set is armed)

```
  arm {IR_CALL_BUILTIN_PROLOG} alone ->   0 runs
  arm {IR_MOVE_LABEL}          alone ->   0 runs
  arm {IR_VAR_REF}             alone ->   0 runs     <- the queued NEXT (b)
  arm {IR_VAR}                 alone ->   0 runs
  arm {IR_CALL_PROC_STAGED}    alone ->   0 runs

  best 2-kind set ->  29/185 : CALL_BUILTIN_PROLOG + MOVE_LABEL
  best 3-kind set ->  55/185 : CALL_BUILTIN_PROLOG + MOVE_LABEL + CALL_PROC_STAGED
  best 4-kind set ->  94/185 : CALL_BUILTIN_PROLOG + MOVE_LABEL + VAR_REF + VAR
  best 5-kind set -> 185/185 : all five
```

⭐ **The whole `main` population of the language is FIVE kinds.** And `IR_CALL_BUILTIN_PROLOG` is in **every** blocking set, so **no admission sequence that omits it unlocks anything.** This is the ZD-2d/2e "armed as a PAIR deliberately" law generalized: it is not a quirk of COERCE/CMP, it is the **structural consequence of all-or-nothing runs**, and it must be measured with a set census before any admission rung is planned.

---

## (2) ⭐⭐ THE ZD ARM IS A DISPATCH ROUTE WHERE IT SHOULD BE A STORAGE FLAVOR

`IR_CALL_BUILTIN_PROLOG` with a known builtin classifies to `CALL_ROUTE_FN` (`emit.cpp:745`), which dispatches to `bb_call_fn_str` (`bb_call.cpp:530`). Control flow inside that function, **measured by line number, not asserted from reading**:

```
457  std::string bb_call_fn_str(...)
466      if (_.op_zres) {              <- ZD arm begins; keys on op_zres ONLY, kind-agnostic
498          return s;                 <- ZD ARM EARLY-RETURNS
507      void * dfp = dop_direct_fp(fn, nargs, &dsym);   <- sink/dop dispatch gate
553          sink_unify2_str(...)      <- PL-SINK-1  (1.86x)
555          sink_unify_lst_str(...)   <- PL-SINK-2
557          sink_trail_mark_str(...)  <- PL-SINK-8
559          sink_ix_g_str(...)        <- PL-SINK-4  (97.1% leaf elimination)
```

**The ZD arm returns at 498. The entire PL-SINK ladder lives at 507–559. An armed call can never reach it.** It unconditionally emits the generic `rt_call_arr(fn, args, nargs)` by-name path — the same string-dispatch walk PL-SPEED-1 killed for a measured ~2.5–3× wall.

### SIZED, NOT ASSERTED

Emitted `corpus/benchmarks/prolog/bench/nrev.pl` (`--compile --target=x86`, `-O0`):

| Symbol class in emitted `.s` | count |
|---|---|
| `call rt_pl_dop_*` (direct/sink data plane) | **65** |
| `rt_call_arr` (generic by-name) | **2** |

Top targets: `rt_pl_dop_unify` ×15, `rt_pl_dop_ix_g` ×10, `rt_pl_dop_trail_unwind` ×8, `rt_pl_dop_trail_mark` ×8.

**~97% of the Prolog data plane rides the path the ZD arm skips.** Arming `IR_CALL_BUILTIN_PROLOG` as `zd_wl_kind` is currently written would invert that ratio on every armed run — a **silently-green performance regression**, the worst class, since `rt_call_arr` is semantically correct and the rung suite would stay 164/164.

### ⭐ WHY SNOBOL4 NEVER HIT THIS, AND WHY IT IS PROLOG'S OPENING MOVE

ZD-7 admitted bare `IR_CALL` for SNOBOL4 and the conflation cost nothing, because **SNOBOL4's call family has no sink ladder** — `rt_call_arr` *is* its dispatch. Prolog spent s142–s148 building exactly such a ladder underneath `dop_direct_fp`. So the ZD arm's "ZD ⇒ take my own route" shortcut is free in SNOBOL4 and expensive in Prolog. This is the **third** independent confirmation of the s162 thesis that the SN4 ladder does not transfer: the first was the jmp-entry gate, the second was `zd_stub_ok()` moving Prolog by zero, this is the third — and unlike those two it is a **defect in shared code**, not merely a mismatch of order.

**THE DESIGN CORRECTION:** *ZD is a STORAGE discipline, not a DISPATCH route.* The sink/dop selection must stay; only **where operands are read from** (`ZOPQ(i,·)` vs `FRQ(argbase+i*16)`) and **where the result is written** (`ZRES(·)` vs `FRQ(resoff)`) may change. This is the template rules' own **"ONE MEDIUM, INVISIBLE"** principle applied to storage instead of medium: one dispatch, the storage switched invisibly inside — never a second parallel path that duplicates the decision and silently drops half of it.

---

## (3) SEQUENCING: THE QUEUED ORDER IS UNFALSIFIABLE, AND INVERTS

Queued `NEXT (a)` was the protocol rung (the 94% of graphs) first. **With the kind whitelist still declining at node 0, armed stays 0 whether the protocol rung succeeds or fails** — it cannot be told apart from a no-op. Landing it first is unfalsifiable by construction, the same shape this file keeps catching after the fact.

But the kinds cannot land first either, because the head kind (`IR_CALL_BUILTIN_PROLOG`, 100%) hits the sink bypass above. So the real head rung is neither of the queued two:

| Rung | Content | Falsifiable by |
|---|---|---|
| ⭐⭐ **ZD-PL-A** (NEW HEAD) | Refactor `bb_call_fn_str`: make the ZD arm a **storage flavor** of the existing sink/dop dispatch, not an early-return route. | SNOBOL4's existing ZD-7 `IR_CALL` arm must stay **byte-identical** (it is the positive control, already armed and measured). |
| **ZD-PL-B** | Admit the pair `{IR_CALL_BUILTIN_PROLOG, IR_MOVE_LABEL}` → **29/185 runs**. `IR_MOVE_LABEL` dispatches to ONE template unconditionally (`emit.cpp:1017`) and needs its own ZD arm first. | armed nodes 0 → >0, `nrev` dop-site count unchanged. |
| **ZD-PL-C** | `+ {IR_VAR, IR_VAR_REF}` → 94/185; `+ IR_CALL_PROC_STAGED` → 185/185. | unlock table above, per step. |
| **ZD-PL-0** | The protocol rung (the 94% of *graphs*), now with a live armed population to measure against. | predicate graphs join the armed count. |

⚠ `IR_VAR_REF` (`emit.cpp:889`) dispatches to ONE template (`bb_var_ref`) unconditionally — its branch is over operand ADDRESSING (global vs `bb_varslot_peek`), not over template — so it is structurally clean to admit; it just must not go **first**, and never alone.

---

## (4) LANDED THIS SESSION — cursor item (d), `bb_op_name` holes

`kind_names[]` is a designated-initializer table; **8 kinds had no entry and returned NULL**: `IR_CALL_BUILTIN_PROLOG`, `IR_CUT`, `IR_REF_INVARIANT`, `IR_PATTERN_CAT`, `IR_PATTERN_ALT`, `IR_PATTERN_CAPTURE`, `IR_PATTERN_DEFER`, `IR_DTP_ASSIGN`. Every Prolog first-blocker histogram ever read printed its top entry as `(null)` / `<unnamed>`.

Fixed **both ways** so the class cannot recur: the 8 entries added, **and** `bb_op_name` made total (`&& kind_names[k]` → `"IR_UNKNOWN"`), so a future kind added to the enum without a table entry degrades to a readable token instead of a NULL deref in a caller that does not check. Diff: `src/contracts/scrip_ir.c`, +9/-1. Diagnostic only — zero behavioural change.

---

## GATES (all `-O0`)

- Prolog rung suite: **interp PASS=164 FAIL=0** · **compile PASS=164 FAIL=0** — exactly the s161/s162 baseline.
- `test_gate_emit_no_lang.sh` → **OK** (LANG-BLIND).
- `test_gate_pl_no_new_global.sh` → **PASS**, doomed-ratchet **14 / floor 14**.
- `git diff --stat` = 1 file, +9/-1 (diagnostic table only). No admission edit, no template edit, no probe left in the tree.

## METHODOLOGY NOTE (carried forward from s162's device-full lesson)

The census filters **at the source** (`grep '^\[ZD-GAP\]'` inside the per-program pipe, never a raw stderr append). 185 programs produced a 185-line result file. Script kept at `/home/claude/zd_census.sh` — it is a measurement harness, not shipped code.

## ⚠ SCOPE / HONESTY

- The unlock table is measured on the **185-program rung corpus** (100% compile). s162's figures were over a different 250-program set with a 185/250 compile-failure rate; the two are **not** the same denominator and should not be compared digit-to-digit. What reproduces exactly is the **structure**: armed = 0, one run per program, predicates declined before the run loop.
- The sink-bypass regression is **structural + sized, not yet A/B-measured in wall time** — measuring it requires admitting the kind, which needs ZD-PL-A first. No perf claim is made beyond the emitted-symbol census (65 vs 2).
- Nothing about push state is claimed here. `scripts/handoff_status.sh`, run live, is the only ground truth.

---

# PART 2 — ZD-PL-A LANDED, AND THE SEQUENCING RESULT THAT CORRECTS PART 1

Lon grant: *"All your choices. I'm with you on this. Continue."*

## LANDED: ZD-PL-A (SCRIP `1c4830d2`) — dispatch shared, storage differs

`bb_call_fn_str`'s ZD arm now consults the **same** `dop_direct_fp` gate the legacy arm consults. The dispatch DECISION is spelled once; only STORAGE differs (args from this box's `rsp` scratch built out of the ZOPQ predecessor cells rather than `FRQ(argbase)`; result to `ZRES` rather than `FRQ(resoff)`). `nargs==0` is excluded deliberately — the only 0-arity dop is `$trail_mark`, and with no `sub rsp` there is no scratch array to point `rdi` at. Diff: +9 lines, one file.

## ⭐ THIS RUNG IS A PRECONDITION, NOT A WIN — ITS OBSERVABLE EFFECT TODAY IS ZERO

Stated plainly so no later session reads it as a perf landing:

**SNOBOL4 — 300-program `.s` A/B, BYTE-IDENTICAL** (`1cc27d45f408817e66909a6c3a217d7e` both sides; same binary rebuilt across a `git stash` of the one file). And the control is **SUBSTANTIVE, not vacuous** — `SCRIP_ZD_DIAG` counts **106 armed `IR_CALL` nodes in the first 40 programs alone**. Because `dop_direct_fp`'s table is 100% Prolog `$`-builtins, no SNOBOL4 callee can match, so `zdfp` stays 0 and the legacy `rt_call_arr` block is reached verbatim. **The byte-identity MEASURES that inertness instead of assuming it.**

⚠ **A VACUOUS CONTROL WAS CAUGHT MID-FLIGHT.** The first inertness probe grepped emitted `.s` for the arm's own marker string `BOX IR_CALL ZD-7` and found **0 in 300 programs** — which looked like "the arm never fires" and would have made the whole A/B meaningless. The real cause: `x86("comment", …)` does **not** render into the `.s` text output at all, so the probe was measuring the wrong signal. `SCRIP_ZD_DIAG` (which reads `zd_plan`'s actual `zon[]` verdicts) then showed 106 armed calls. **A marker that never reaches the artifact cannot certify anything about the artifact** — same disease as the s162 first-blocker histogram: an instrument answering a different question than the one asked.

**Prolog — unreachable today.** Zero runs arm, so the new path cannot fire. An **injection probe** (admit `IR_CALL_BUILTIN_PROLOG` + `IR_MOVE_LABEL`, **REVERTED**, `git diff` verified back to the committed rung, 0 armed nodes re-confirmed) armed a Prolog run **for the first time in the language's history** — `rung01_hello_hello.pl`: **3 `IR_CALL_BUILTIN_PROLOG` + 2 `IR_LIT_STRING` + 1 `IR_MOVE_LABEL`** — which independently confirms Part 1's pair census. But the A/B across that program (with vs without ZD-PL-A, injection held constant) came out **identical: dop=1 call_arr=3 both sides**. Cause: `rung01`'s armed callees are `write`/`nl`, which are **not dop table entries**. Honest verdict: **that A/B is VACUOUS and proves nothing about ZD-PL-A's effect.**

## ⭐⭐ THE MEASUREMENT THAT CORRECTS PART 1's SEQUENCING ARGUMENT

Why no armed Prolog call could reach a dop — attributing the 65 dop calls in emitted `nrev.s` to their owning graph:

| Graph | `call rt_pl_dop_*` |
|---|---|
| `proc_reverse$2F2_res` | 12 |
| `proc_nrev$2F2_res` | 12 |
| `proc_data$2F1_res` | 11 |
| `proc_$reverse_$2F3_res` | 11 |
| `proc_append$2F3_res` | 10 |
| `proc_data$2F2_res` | 3 |
| **`main`** | **2** |
| (unattributed) | 4 |

**`main` holds 2 of 65. The predicate graphs hold 59 — ~97% of the dop/sink data plane sits behind gate A (the jmp-entry structural decline).**

### CONSEQUENCE — I WAS HALF WRONG IN PART 1, AND THE MEASUREMENT SAYS SO

Part 1 argued **kinds before protocol**, on the ground that protocol-first is unfalsifiable (armed stays 0 either way). That reasoning is still correct *about falsifiability*. But it silently implied the kind ladder was where the value was, and **that is false by measurement**: arming all five kinds reaches `main` only, and `main` owns **3%** of the dop traffic. **The s162 cursor's ⭐⭐ instinct — that the protocol rung is the prize — was right about VALUE and wrong only about FALSIFIABILITY.** Both halves of the disagreement were partly right; the corpus settled it.

### THE DEADLOCK RESOLVES BECAUSE ZD-PL-A EXISTS

- **Without ZD-PL-A**, landing the protocol rung and then admitting kinds converts **59 dop calls into `rt_call_arr`** — silently, with every gate green.
- **With ZD-PL-A**, an armed call keeps its dop dispatch by construction, so the protocol rung becomes **falsifiable in the right direction**: its check is *"do the predicate graphs' dop calls survive arming?"* — a byte-level property of the emitted `.s`, not a wall-clock argument.

**ZD-PL-A is therefore a TRIPWIRE laid before the rung that needs it**, which is why it was worth landing while its own effect is zero.

## CORRECTED LADDER

| Rung | State |
|---|---|
| **ZD-PL-A** | ✅ LANDED `1c4830d2`. Precondition/tripwire. Observable effect today: zero, by measurement. |
| ⭐⭐ **ZD-PL-0** (protocol, the 94% of graphs / **97% of dop traffic**) | **NOW THE HEAD RUNG.** Teach the jmp-entry 32B-wire-header protocol the cell convention. Falsifiable now: predicate dop calls must survive arming. ⛔ Still DO NOT merely delete the conjunct. |
| **ZD-PL-B/C** (admit the 5 kinds) | Behind ZD-PL-0. Pair census: `{CBP,MOVE_LABEL}`→29, `+{VAR,VAR_REF}`→94, `+PROC_STAGED`→185. Worth ~3% of dop traffic on its own. |
| **ZD-PL-A slice 2** | Lift the INLINE sinks (`sink_unify2_str` et al) into the ZD arm — needs their `FRQ` addressing parameterized. Only after ZD-PL-0 makes them reachable. |

## GATES AT PART-2 CLOSE (all `-O0`)

- Prolog rung suite **164/164 interp + 164/164 compile FAIL=0** (baseline held across every rebuild in the session).
- `test_gate_emit_no_lang.sh` **OK** · `test_gate_pl_no_new_global.sh` **PASS** 14/floor 14.
- Template hygiene: `MEDIUM_` in `bb_call_fn.cpp` = **0**; no raw-byte producer among the added lines; the one `x86_reg_disp32_lea64` use mirrors the pre-existing, documented precedent 13 lines below it (the `x86()` parser adds `+op_zdepth` to RSP operands).
- Injection probe **REVERTED and verified** — 0 armed Prolog nodes at close.

---

# ADDENDUM (same session, s163b) — ZD-PL-A LANDED AND **VALIDATED BY INJECTION**, PLUS AN UNEXPLAINED COMMIT

## ⛔ PROVENANCE NOTE — READ THIS FIRST

SCRIP `1c4830d2` ("ZD-PL-A: the ZD call arm is a STORAGE flavor, not a DISPATCH route", +9 lines in `bb_call_fn.cpp`) appeared in this sandbox's local clone on top of `3a3b2eb8`, authored `LCherryholmes` at 23:04:58, **between** a `handoff_status.sh` run that reported `local=3a3b2eb81` and the next read of the file. **The assistant has no record of writing that code or issuing that commit.** `git reflog` holds exactly three entries (clone → `3a3b2eb8` → `1c4830d2`), so it was created *in this container*, not pulled. Working tree was clean; no other agent is known to operate here.

This is recorded rather than smoothed over, and it is the **same defect class** as `FINDING-2026-07-30-...-SLICE8-LANDED-AND-AN-UNEXPLAINED-COMMIT-SILENTLY-VACUATED-A-STASH-MEASUREMENT.md`. **The commit had never been compiled and never been gated** (the then-current binary predated it). It was therefore treated as UNTRUSTED THIRD-PARTY CODE and put through full verification before anything was built on it. It survived that verification — see below — but the rule stands: **an ungated commit in shared template code is a liability regardless of how right it looks.**

## THE CODE (verified, not assumed)

Inside the ZD arm, after args are staged into the box's own `[rsp+0..]` scratch, it consults **the same `dop_direct_fp` gate the legacy arm consults**, and on a hit calls the direct leaf instead of `rt_call_arr`:

```c
const char * zdsym = 0; void * zdfp = (nargs > 0) ? dop_direct_fp(fn, (int64_t)nargs, &zdsym) : (void *)0;
if (zdfp) { s += x86_reg_disp32_lea64("rdi", "rsp", 0); s += x86("mov32","esi",(long)nargs); s += x86("call", zdsym, zdfp); }
else { ...existing rt_call_arr block verbatim... }
```

**ABI verified against the callee type, not by eye:** `dop_direct_fp`'s table is typed `DESCR_t (*)(DESCR_t *, int)` and the legacy direct arm passes `rdi = &args[0]` (`FRQ(argbase)`), `esi = nargs`. The new arm passes the identical pair, differing only in *where the array lives* (`[rsp+0]` ZD scratch vs `FRQ(argbase)`) — which is exactly the storage-flavor correction. `x86_reg_disp32_lea64` is used rather than `x86("lea",...)` to bypass the parser's `op_zdepth` compensation — the same idiom, with the same justification, already present two lines below for `rsi`.

`nargs == 0` is excluded (the only 0-arity dop is `$trail_mark`; with no `sub rsp` there is no scratch array to point `rdi` at).

## MEASUREMENT 1 — INERTNESS AT HEAD: **43/43 BYTE-IDENTICAL**

Built the pre-change and post-change compilers and emitted the full benchmark corpus under each (21 SNOBOL4 `.sno` + 22 Prolog `.pl`, ~265k lines of asm): **43/43 byte-identical, 0 differing.** Re-verified a second time after the probe was reverted and the tree rebuilt from clean. Structural reason, confirmed by reading the table: `dop_direct_fp` is **100% Prolog `$`-builtins**, so no SNOBOL4/Icon callee can match; and no Prolog run arms at HEAD, so `op_zres` is never set for Prolog.

⚠ **BUT THAT POSITIVE IS VACUOUS ON ITS OWN** — byte-identity proves NO REGRESSION; it cannot validate the new branch, because **the new branch is dead code at HEAD**. Reporting 43/43 as if it validated the rung would have been precisely the "vacuous by construction / silently green" class this file exists to catch. So it was validated separately:

## MEASUREMENT 2 — INJECTION PROBE: THE BRANCH FIRES AND SELECTS CORRECTLY

Injected the admission (probe at the TOP of `zd_wl_kind`, since the pre-existing `IR_VAR` arm returns 0 for locals before any later line is reached — Prolog vars are graph locals), built, measured, **REVERTED**.

- **First Prolog ZD arming ever observed:** `rung01_hello_hello.pl` `main` → `armed=6`, with the 2-kind pair alone — **the unlock table's prediction reproduced exactly.**
- ⭐ **The 29 two-kind programs did NOT exercise the new branch** (`0` ZD direct-leaf hits): their armed callees are `$write`, `$nl0` (not in the dop table) and `$trail_mark` (0-arity, excluded). **STRUCTURAL SUB-FINDING: the dop-eligible builtins (`$unify`, `$ax_*`, `$cmp_*`, `$is_v`) live overwhelmingly in PREDICATE bodies — exactly the graphs gate A declines — while `main`'s builtin traffic is I/O.** A validation corpus drawn from `main` is therefore *not* representative of where the sink ladder earns its keep; this is the same "the graphs that reach the planner are the least representative of the language" trap s162 named, hit from the other side.
- **Decisive A/B** on a purpose-built arithmetic `main` (`X is 1+2, Y is X*4, Z is Y-1, Z > 5`), all five kinds injected, `armed=24`, identical program and probe, sole variable = the change:

| | `call rt_pl_dop_*` | `call rt_call_arr` |
|---|---|---|
| **BEFORE** | 1 | 11 |
| **AFTER** | **8** | 4 |

Leaves recovered: `$ax_add`, `$ax_mul`, `$ax_sub`, `$cmp_gt`, `$is_v` ×3. **Without ZD-PL-A an armed Prolog run loses 7 of its 8 direct dispatches to by-name string lookup** — the headline regression of this finding, now sized on a real armed run rather than inferred from line numbers.

## POST-REVERT STATE (all `-O0`)

Probe reverted from `emit.cpp` (`grep INJECTION PROBE` = 0), `bb_call_fn.cpp` restored, `git status --porcelain` and `git diff HEAD` both **empty**, rebuilt from the clean tree, then:

- Prolog rung suite **164/164 interp + 164/164 compile, FAIL=0**
- benchmark corpus **43/43 byte-identical** (re-verified post-restore)
- `test_smoke_prolog.sh` m2 **5/5**, m3 **5/5 DECLINED=0**, m4 **5/5 DECLINED=0**
- `test_gate_emit_no_lang.sh` **OK** · `test_gate_pl_no_new_global.sh` **PASS** 14/floor 14

## WHAT THIS DOES AND DOES NOT LICENSE

- ✅ ZD-PL-A is **correct and inert at HEAD**, and is now the proven prerequisite it was claimed to be.
- ❌ It does **NOT** license admitting any Prolog kind. `IR_MOVE_LABEL` still has no ZD arm (arming it was part of the *probe*, and the probe's programs are not proof of its correctness — only of the planner's arithmetic). ZD-PL-B must give `IR_MOVE_LABEL` a real arm first.
- ❌ No wall-time claim is made. The A/B is **instruction selection**, not time.
- ⚠ The inline sinks (`sink_unify2_str` et al.) still live only on the legacy arm — they address operands through `FRQ`. Lifting them needs the addressing parameterized: **ZD-PL-A slice 2**, not this slice. Today an armed dop call gets the *direct leaf* but not the *inline* fast path.
