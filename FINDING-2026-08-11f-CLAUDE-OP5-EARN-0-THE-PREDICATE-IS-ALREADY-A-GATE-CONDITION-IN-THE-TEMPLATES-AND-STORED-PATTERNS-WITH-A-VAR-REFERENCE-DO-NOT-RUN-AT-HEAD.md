# FINDING 2026-08-11f (s27, Opus 5) — EARN-0: THE PREDICATE IS ALREADY A GATE CONDITION IN THE TEMPLATES, AND STORED PATTERNS WITH A VAR-REFERENCE DO NOT RUN AT HEAD

**Fingerprint:** SCRIP `fc5b0754` UNTOUCHED (zero src bytes) · corpus `6c601c19` + `probe/earn0/` NEW + `probe/arb1.ref` VERIFIED · `.github` this commit.
**Rung:** EARN-0 (the classification table). **Instrument:** SPITBOL oracle `x64/bin/sbl -b` (cloned this session) vs `scrip --run` (m3), built green at HEAD (`make scrip` rc=0, `make libscrip_rt` rc=0, zero `error:`).

---

## 1. ⭐⭐⭐ THE EARN PREDICATE IS NOT A NEW IDEA IN THIS TREE — IT IS ALREADY WRITTEN, AS A GATE CONDITION, IN THE TEMPLATES

EARN's law is *"a cell needs a frame ⟺ the byte distance between that cell and RSP is not a compile-time constant at some site that reads it."* Three independent sites already encode exactly that, as live arming conditions:

- **`bb_match_arbno.cpp:92`** — the `[rsp+0]`/`[rsp+4]` cursor is gated to the nested-K0 class `(op_arbno_framed && op_arbno_body_k0)` because **"the frontier never moves inside the activation, so the cell is `[rsp+0]`/`[rsp+4]` from EVERY site."** That is the UNBOUNDED hazard, named as the reason for a gate. The gate is the law; the law was already load-bearing.
- **`IR_t.pat_static` (`IR.h:226`)** — set at the lowerer's DEFER build site: 1 iff the target's **transitive closure over spine-position VAR references contains ZERO `TT_DEFER`**, with the manual citation inline (*"p.122: only `*` recurses"*). **This is EARN's OPAQUE test, already computed, under another name.** EARN-1's `frame_need_of()` should CONSUME this, not re-derive it.
- **`bb_match_capture.cpp:44`** — the δ home resolves per graph class, and the comment states the per-activation principle verbatim: *"pinned graphs resolve `[rbp+off]` = depth-immune, per-activation by the frame itself … X/Y/Z are three nodes = three slots, recursive same-node activations live in distinct blob frames."*

⇒ **EARN-1 is smaller than the ladder assumes.** The classifier's two hazard inputs already exist as `pat_static` (OPAQUE) and the arbno frontier gate (UNBOUNDED). What does not exist is the **READING-EDGE** column and ONE authority that unifies them.

## 2. ⭐⭐ FENCE1 AND ARBNO ALREADY COLLIDE OVER RBP, AND EARN PREDICTS THE SUPPRESSION BECOMES DEAD CODE

`bb_match_fence1.cpp:22` — FENCE1 takes its OWN independent RBP frame (U-2 STRUCTURAL, `bb_glue_framed_enter/leave`), **suppressed when `op_ival == 2` (FENCE1-in-ARBNO-body)** because *"ARBNO owns rbp in its own frame dance; a nested push-rbp/pop-rbp corrupts it (MEASURED: `142_pat_arbno_fence_arbno` hang)."*

ARBNO does not own a frame — it **borrows the parent's rbp as an element view register** (`zv()` returns `"rbp"`, `bb_match_arbno.cpp:15`, save/restore via slot `op_off+32`). The collision is therefore between a *real* frame (FENCE1's) and a *borrowed* one (ARBNO's), which is not a LIFO discipline at all.

⭐ **FALSIFIABLE EARN PREDICTION, cheap, and it is a DELETION:** once EARN-4 gives ARBNO its own per-activation frame, nested push/pop can no longer corrupt anything, so **the `op_ival != 2` suppression becomes dead code and `142_pat_arbno_fence_arbno` must stay green with it removed.** If it does not, EARN-4's frame is not per-activation and the rung is not done. Record this as EARN-4's second gate line.

## 3. ⭐ ARBNO's ROOT-SPINE SCAFFOLD IS EARN-4's DESIGN, ALREADY IN THE TREE, DEFAULT-OFF AND MEASURED INSUFFICIENT — WITH ITS MISSING HALF NAMED

`bb_match_arbno.cpp:45`, `SCRIP_ARBNO_ROOTSPINE` (default **0**): `=1` puts the chain-arm ROOT header in a **48B α-carved SPINE record, "per-activation BY CONSTRUCTION"** — EARN's protocol exactly. Its own comment records why it is off: *"MEASURED INSUFFICIENT ALONE"* — every yield exit terminates the view chain at `root-op_off` instead of the statement frame, so downstream FR readers leak a view as rbp (claws5-match SEGV'd under default 1). And it names the missing half: *"The COMPLETE arm additionally restores true rbp from `[root+32]` at every γ exit AND re-derives the view at as/af entry."*

Its diagnosis is the **third recorded instance of this goal's flat-cell defect class**: *"DEL-T1 (`1af93e3a`) deleted that contract for blob interiors, so every nested activation of the same node shared ONE statement-frame header — `pattern_match.c:624`'s single-cell defect in frame clothing."*

⇒ EARN-4 should **start from `ROOTSPINE=1` plus the named second half**, not from scratch. ⛔ This does not contradict Lon's *"I would not use any of the previous code"* — the ruling is about the *old regime* (BLOB-GRANT pins, CLASS D records); ROOTSPINE is a dormant scaffold OF the new one. Raise it, do not assume it.

## 4. ⛔⭐⭐⭐ MEASURED DIVERGENCE: A STORED PATTERN THAT REFERENCES A PATTERN-VALUED VARIABLE DOES NOT RUN AT HEAD

EARN-0 requires hand-checking the table against witnesses compiled at HEAD. The check found the compiler is **not correct on the case EARN's law calls the SIMPLEST POSSIBLE ONE.**

By the manual (p.122), pattern construction is **BY VALUE** — only `*` defers — so `P` inside `Q` is fully known at build time and carries NEITHER hazard. EARN predicts **zero frames anywhere** in these programs. Measured (m3, `timeout 20s`, oracle-baked refs, `corpus/probe/earn0/`):

| witness | pattern | oracle | scrip m3 | rc |
|---|---|---|---|---|
| `earn0_inline_control` | `'abc' POS(0) P $ V LEN(2) RPOS(0)` (INLINE) | `MATCH V=[a]` | `MATCH V=[a]` | 0 **PASS** |
| `earn0_stored_varref` | `Q = POS(0) P LEN(2) RPOS(0)` ; `'abc' Q` | `MATCH` | *(nothing)* | **124 HANG** |
| `earn0_stored_capture` | `Q = POS(0) LEN(1) $ V LEN(2) RPOS(0)` ; `'abc' Q` | `MATCH V=[a]` | *(nothing)* | **0, SILENT EMPTY** |

**The control is the whole point:** the inline form is CHARACTER-IDENTICAL in pattern and is correct. The discriminator is **storing the composite in a variable and matching against it** — a class boundary, not a flake.

⛔ **HONEST LIMITS, stated so nobody inherits more than was measured:**
- **Not all stored patterns break.** `P = POS(0) ARBNO(LEN(1)) RPOS(0)` and `P = POS(0) 'ab' LEN(1) RPOS(0)`, both stored then matched, are **oracle-green**. The trigger is narrower than "stored composite."
- **Shape-sensitive.** `earn0_stored_capture` printed `MATCH V=[]` (wrong bind, ran to completion) with an *unused* `P = LEN(1)` line present, and prints nothing without it. Same file, one dead line, different failure mode — the address-sensitive class already on record in this file.
- **⛔ CORRECTION ON MYSELF, CAUGHT BY THE POST-REBASE RE-PROVE (RULES §concurrent).** My table above records `earn0_stored_capture` as "rc=0, SILENT EMPTY" as though that were its stable signature. **It is not.** Re-run against the same untouched binary (`fc5b0754`, SCRIP did not move in the rebase) it returned **rc=134 SIGABRT (`Aborted`)**. And `earn0_stored_varref` measured **rc=124 HANG** here but produced **`Segmentation fault`** on an identical earlier invocation. **BOTH stored witnesses are NONDETERMINISTIC across {silent-empty rc=0, SIGABRT 134, SIGSEGV 139, HANG 124} on a fixed binary.** ⛔ **Do not treat any single rc as the signature, do not bisect on one, and do not read a changed rc as a repair** — this is the arms-identical-control-is-invalid trap already on record in this file (`FINDING-2026-08-10-...-AB0-IS-NONDETERMINISTIC-ON-RECURSION`). The stable, reportable fact is the **PASS/FAIL split against the oracle ref**, which reproduced identically on every run: control PASS, both stored forms FAIL.
- **The silent-empty CLASS is pre-existing and already named** by s26 (`066_pat_fence_fn_nested`, "exit 0 is NOT exoneration"). ⭐ **What is new is a 6-line reproducer with NO FENCE, NO defer, NO ARBNO in it, plus a passing inline control** — i.e. the class is not FENCE-specific and is much cheaper to hunt than the witnesses s26 had.
- ⛔ **NOT ROOT-CAUSED.** Per RULES MONITOR-FIRST this is where the 2-way sync-step monitor takes over. **I did not run it** — the divergence is reported, not diagnosed. Do not read section 4 as a mechanism.
- ⛔ **NOT ADOPTED BY THIS GOAL.** Like s26's FENCE set, this is pre-existing debt EARN-0's hand-check SURFACED. It needs an owner. RBP-EARN should not silently absorb it.

## 5. RULING (a) IS NOT A GREENFIELD CHOICE — BOTH ARMS ARE ALREADY LIVE, AND THEY HAVE DESYNCED BEFORE

The ladder raises ruling (a) as *"CAPTURE PENDINGS: SPINE OR HEAP?"* with `bb_match_capture.cpp` (230 lines) marked **unread**. It is now read. Both mechanisms **already exist and are selected per-node**:

- **Spine/frame arm** — δ in the SAVE node's own ZLS slot via `caphome()`/`FR(op_off)`, keyed on `sfc()` = `x86_fc_on() && (!cap_sym() || op_fc_base >= 0)`.
- **Heap/array arm** — the `rt_cap` software array + pend-park CAS machinery.

⛔ And the failure mode of having both is on record at `bb_match_capture.cpp:29` (s22m): `op_fc_bytes` **has two writers meaning different things**, so a SAVE armed by the ZD spine took the cell arm while its COND partner read the array — *"Producer wrote one place, consumer read another: capture start came back 0, so every capture preceded by a matched element swallowed the preceding characters."*

⇒ **Reframe ruling (a) for Lon:** it is not "which should we build," it is **"which of the two live mechanisms do we delete."** That is cheaper than the ladder assumes and it retires a defect class rather than trading frame counts. Note also that COND/IMM are already **ZERO-CELL** (`:22-24`) — they read a delta the SAVE node owns — so under EARN the frame belongs to **SAVE**, which is Rule 1 ("the frame belongs to the node holding a cell live ACROSS a hazard, never to the hazard itself") landing on a node that already exists. `IR_MATCH_ASSIGN_SAVE` is the ownership site.

## 6. DEBT DISCHARGED: `arb1.ref` IS NOW ORACLE-VERIFIED

s26 flagged `corpus/probe/arb1.ref` as **transcribed** from `181`'s ref, "not independently regenerated — rebake with `sbl -b` when x64 is present." x64 is present. Fresh bake is **byte-identical** to the transcription (`T1 MATCH` / `T2 NOMATCH`). The provenance caveat in the file header can now be read as settled. HEAD behaviour re-confirmed unchanged: `T1 MATCH` then **rc=139 SIGSEGV** on T2.

---

## EARN-0 CLASSIFICATION TABLE — FIRST CUT (32 `IR_MATCH_*` kinds; `NEVER` · `IFF-OPAQUE-SIBLING` · `ALWAYS`)

Columns: **HAZARD** = does this kind INTRODUCE a hazard. **READS-ACROSS** = does it hold a cell live across one. **EDGE** = which edge the read happens on (the s25 sharpening: success-edge reads earn, failure-edge reads do not). **VERDICT** = frame need.

| kind | HAZARD introduced | READS-ACROSS | EDGE | VERDICT | basis |
|---|---|---|---|---|---|
| `LIT` `ANY` `NOTANY` `LEN` `POS` `RPOS` `TAB` `RTAB` `REM` `SPAN` `BREAK` `BREAKX` | none | no | — | **NEVER** | primitives; cursor delta is a compile-time constant from the carve. 12 kinds, and all 12 are rbp-free in the templates at HEAD ✅ |
| `SPAN_VAR` | none (value arg) | no | — | **NEVER** | argument is by value; deferral would be a `DEFER` node, not this one |
| `ARB` | none | no | — | **NEVER** | single retry point, bounded by subject length; distance stays static |
| `BAL` | none¹ | no | — | **NEVER** ¹ | ¹ manual p.128 BAL recurses over bracket nesting — **UNVERIFIED, flag for EARN-6** |
| **`ARBNO`** | **UNBOUNDED** (p.121 `("" \| P \| PP \| PPP \| …)`) | its own control cell, across its own retries | success (β) | **ALWAYS** | Rule 1 chicken-and-egg; `ARBNO(LEN(1))` earns as much as `ARBNO(*P)` |
| **`DEFER`** | **OPAQUE** (p.122 only `*` defers) | nothing of its own | — | **NEVER (owns nothing)** | `*P` is the hazard, never the owner — Rule 1 verbatim |
| **`VALUE`** | **OPAQUE** (variant ref) | nothing of its own | — | **NEVER (owns nothing)** | structural clone of DEFER per `IR.h:142` |
| `ALTERNATE` | none | δ0, to reset the cursor per arm | **FAILURE** | **NEVER** ⭐ | the s25 sharpening's headline refusal: LIFO has already returned rsp to ALT's own depth, so `[rsp+K]` is correct **even when the arms contain `*P`** |
| **`ASSIGN_SAVE`** | none | δ0, across whatever follows | **SUCCESS** | **IFF-OPAQUE-SIBLING** | the real owner for both captures (§5); already has its own slot |
| `ASSIGN_IMM` (`$`) | none | reads SAVE's δ | success | **NEVER (zero-cell)** | `bb_match_capture.cpp:22-24`; p.87 fires per-subpattern |
| `ASSIGN_COND` (`.`) | none | reads SAVE's δ | success (whole match) | **NEVER (zero-cell)** · ⛔ **ruling (a)** | p.93: assignment "occurs only after the pattern match is complete" — span is the whole remaining pattern |
| `FENCE1` | none | its own floor, across P | failure | **IFF-OPAQUE-SIBLING** | p.125 bare FENCE aborts on backup; has a real frame today (U-2) + the ARBNO suppression of §2 |
| `ATP` (`@`) | none | cursor | success | **NEVER** | writes a position, spans nothing |
| `ABORT` | none | — | — | **NEVER** | crossing 1 (anchor drain), not a frame |
| `CALLOUT` | ⛔ **UNCLASSIFIED** | ? | ? | ⛔ **OPEN** | arbitrary user code mid-match; treat as OPAQUE until measured |
| `MATCH_BEGIN` | none | the match root | both | **IFF-OPAQUE-SIBLING** | EARN-6; seeds the ANCHOR slot |
| `MATCH_END` | none | unwinds | — | **NEVER** | its unwind is why STATEMENT is refused (the file's own refusal #1) |
| `REPLACE` | none | splice span | success | **IFF-OPAQUE-SIBLING** | α-only; ⛔ see the s25 splice defect, unverified here |
| `RETRY` `ADVANCE` | none | — | — | **NEVER** | crossing 2 (unanchored retry) |
| `CAT` | none | — | — | **NEVER** | concatenation node, no state |

**Predicts-HEAD check:** the table says only `ARBNO`, `ASSIGN_SAVE`, `FENCE1`, `MATCH_BEGIN`, `REPLACE` can ever hold a frame. At HEAD exactly **8 of 29** match templates mention rbp, and **24 of 29 are already rbp-free** — the 21 `NEVER` rows are confirmed frameless by the compiler today. ✅ Table is consistent with HEAD wherever HEAD is correct.
⛔ **Three rows are NOT hand-checked against emitted asm** (`BAL`, `CALLOUT`, `REPLACE`) and **the three witnesses could not complete the check for the stored-pattern forms** — see §4. EARN-0 is therefore **PARTIALLY DISCHARGED. Do not mark it done.**

---

## NEXT SEAT, IN ORDER

1. ⛔ **Lon: ruling (a) reframed (§5) — which of the two LIVE capture mechanisms is deleted.** Cheaper than the ladder assumed; retires the s22m desync class.
2. ⛔ **Lon: does §3 (`ROOTSPINE=1` + its named missing half) count as "previous code" under the s25 from-scratch ruling?** This changes EARN-4's cost materially.
3. **Owner for §4** (stored-pattern-with-var-reference). Then MONITOR-FIRST on `earn0_stored_varref.sno` — 6 lines, sub-second, passing inline control beside it. **This is the cheapest live divergence witness in the goal today.**
4. Finish EARN-0: `BAL`, `CALLOUT`, `REPLACE` rows against emitted asm.
5. **EARN-2 before ANY deletion** (unchanged).

**Inherited debts unchanged by this session:** regen ×3 still owed from s24 (this session changed **zero** src bytes, so it adds none) · ζ-MECH watermark re-baseline + H31/X01/X10 bisect · off-path r10/r11 residue · `board_demos_zeta.sh` m4 arm wrong as written · the heap-frame row of EARN-0b still UNTESTED with a DARK instrument (MON-RE first — untouched here).

**ENV (adds to s26's list):** `gdb` still absent. `nproc`=1. `setsid` confirmed necessary and sufficient for a detached build (`make scrip` + `make libscrip_rt`, ~2.5 min, rc=0 both). `x64` oracle clones clean in ~30s (57M) and `sbl -b` runs witnesses directly — **there is no reason for a seat to work without the oracle.**

---

## 7. EARN-0's THREE OPEN ROWS, CLOSED (s27 continuation)

- **`CALLOUT` — VACUOUS ROW. Zero producers, no template.** `IR_MATCH_CALLOUT` occurs in exactly four places tree-wide: the enum (`IR.h`), the name table (`scrip_ir.c`), `emit_per_kind_audit.c`, and TWO conservative bail lists in `emit.cpp` (`emit_graph_has_deep_arrival` :2881 and the FB-STMT bail :2891). **No lowerer constructs one and `bb_match_callout.cpp` does not exist.** The deep-arrival comment even labels it *"CALLOUT conservative"* — listed out of caution, never measured. ⇒ **The row is vacuous and the two bail entries are dead weight that can never fire.** Referral: `GOAL-DEAD-CODE-SWEEP.md`.
- **`BAL` — NEVER, CONFIRMED BY TEMPLATE READ.** `bb_match_bal.cpp` is 50 lines, entirely `FR(x86_scratch_off{,+4,+8})`, **zero rbp**. Semantics (p.124) need a paren-DEPTH COUNTER, a fixed-size scalar — not a stack of live records — and like ARB its retries REPLACE one choice point rather than accumulating instances that must be peeled back. That is the ARBNO contrast in one line: **ARBNO earns because its instances stay live; BAL and ARB do not because theirs do not.**
- **`REPLACE` — NEVER at HEAD (revised down from IFF-OPAQUE-SIBLING).** Built at `lower_snobol4.c:1802` as the statement splice. Witness `S 'world' = 'there'` is **oracle-green**, and `bb_match_replace.cpp` carries ONE rbp mention (the s193 head/release/replace save-restore bracket, which the emit.cpp census itself calls *"save/restore-of-caller-value, value-neutral without a seed"*). ⛔ The s25 splice defect (`FINDING-2026-08-10f`) is a SPAN-arithmetic bug, not a frame need; it does not lift this row.

### ⭐ INDEPENDENT HEAD-SIDE CONFIRMATION OF THE TABLE'S HEADLINE REFUSAL
`emit.cpp:2881`'s comment records that **`ALTERNATE`, `SEQUENCE`, `ARB`, `RETRY`, `RELEASE` were DROPPED from the rbp-reader set in s193**, measured, with the crosscheck watermark as tripwire. That is the s25 sharpening's marquee claim — **ALT does not earn** — already proven at HEAD by a different seat for different reasons. The table's `NEVER` rows are not a prediction; four of them are a re-derivation. ⇒ **`emit_graph_has_deep_arrival` IS a de-facto `frame_need_of` and EARN-1 should reconcile with it rather than mint a second authority** (this file's own ONE-AUTHORITY law).

## 8. ⛔⭐⭐⭐ CAPTURE AFTER A VARIABLE-LENGTH PRIMITIVE BINDS THE WRONG SUBSTRING — CONVICTED BY PREDICTION

Closing the `BAL` row surfaced a second live divergence, and it is **broader than BAL**.

**MECHANISM:** for `<varlen-primitive> . R`, the capture's δ0 is the primitive's **`consumed` counter**, not the match START. Binding is `[n, p+n)` where p = start, n = consumed. Correct is `[p, p+n)`.

| witness | p | n | oracle | scrip | predicted |
|---|---|---|---|---|---|
| `BAL . R` on `AB+(14-2)*C` | 0 | 1 | `A` | *(null)* | `[1,1)` = null ✅ |
| `ANY BAL . R ANY` on `AB+(14-2)*C` | 3 | 6 | `(14-2)` | `-2)` | `[6,9)` ✅ |
| `ANY('+') BAL . R 'e'` on `ab+(cd)ef` | 3 | 4 | `(cd)` | `cd)` | `[4,7)` ⭐ **stated in advance** |
| `ANY('+') ARB . R 'g'` on `abcd+efg` | 5 | 2 | `ef` | `cd+ef` | `[2,7)` ⭐ **stated in advance** |

**BAL ITSELF IS CORRECT.** Measured with `@` (cursor read, capture-free): `cursor_after_BAL` agrees with the oracle on both subjects. Only the capture is wrong.

⛔ **CORRECTION ON MYSELF — I NEARLY SHIPPED A VACUOUS CONTROL, AND IT WOULD HAVE MIS-SCOPED THE DEFECT.** My first ARB control (`ANY('+-*/') ARB . R ANY('+-*/')`) AGREED with the oracle, and I read that as "ARB is fine, BAL is special." **It was vacuous: p=3 and n=3 were EQUAL, so `[p,p+n)` and `[n,p+n)` are the same string and the control could not discriminate.** Re-run with p=5, n=2 it FAILS exactly as predicted. This is the vacuous-A/B class already convicted three times in this goal (s24's classifier, s37's killswitch, s23's dead board); it caught me too, one measurement after I invoked the rule against s26. **A control whose two arms predict the same output is not a control — check the arithmetic separates BEFORE trusting a green arm.**

**BLAST RADIUS (candidate, unverified):** the 9 templates writing `FR(x86_scratch_off)` as a consumed counter — `arb bal break breakx rem rtab span span_var tab`. **WHY THE CORPUS IS BLIND:** every PASSING capture test (`058`/`059`/`060`) binds after fixed-length `LEN`, which has no consumed counter. The one failing capture test, `061`, is the **variable-ARG** class (`FINDING-2026-08-10d`) — adjacent, distinct, separately owned; I do **not** claim it.

⛔ **NOT ROOT-CAUSED IN SOURCE.** Convicted by arithmetic on four witnesses, not stepped. MONITOR-FIRST owns the next step. ⛔ **NOT ADOPTED BY THIS GOAL** — like §4, it needs an owner. Witnesses: `corpus/probe/earn0/earn0_cap_after_{varlen,bal}.sno`, oracle-baked.

⭐ **WHY IT MATTERS TO EARN ANYWAY:** ruling (a) asks where capture pendings live. **This is a δ0-SOURCING defect in the mechanism the ruling would consolidate onto.** Whichever arm survives, δ0 must come from the SAVE node's own slot — which is precisely EARN Rule 1 putting the frame on `IR_MATCH_ASSIGN_SAVE`. The bug is an argument FOR the reframing in §5, not an obstacle to it.

---

## 9. ⭐⭐ THE CENSUS INSTRUMENT IS EXONERATED FOR EARN-2 — AUDITED, NOT ASSUMED (s27 continuation)

EARN-2 ("the census changes units") rests entirely on `scripts/test_census_rbp_frames.sh`, and s26's hardest lesson was **prove an instrument before planning a rung on it**. Two facts looked like they collided:

- The census **reads committed `.s` artifacts**, not the live compiler (`:23-27`), and its own header concedes they are honest *"only at the regen cadence."*
- **Regen ×3 has been owed and unpaid since s24**, and this file's census table already carries the caveat *"crosscheck/patterns regen cadence STILL unaudited — indicative only."*

**MEASURED, not assumed.** The artifacts ARE byte-stale, and the staleness is exactly the documented debt: `038_pat_literal` diffs 28 lines, all of the shape `mov r10, r12` → `mov r8, r12` — the R10R11-ERAD landing. **But that change is REGISTER SUBSTITUTION, which cannot move an rbp establishment.**

**FULL AUDIT of `crosscheck/patterns`** (every `.s`-bearing program recompiled at HEAD `fc5b0754` and compared on the census quantity `mov rbp,rsp` + `push rbp`):

| programs with `.s` | compile-failed | census UNCHANGED | census MOVED |
|---|---|---|---|
| **122** | **0** | **122** | **0** |

⇒ **The census's own quantity is EXACT at HEAD over this corpus even though the artifacts are byte-stale, and the "indicative only" caveat can be lifted for `crosscheck/patterns`.** EARN-2 may proceed on this instrument. ⭐ This is the first instrument check in this goal since s26 to come back **LIVE rather than DARK** — s26's `c_rt_match_enter` and `c_rt_gen_spine_resume_enter` were both dark.

⛔ **THE EXONERATION IS CONDITIONAL AND EXPIRES ON THE FIRST FRAME-MOVING RUNG.** It holds only because the outstanding debt is register-substitution, orthogonal to rbp. **EARN-4 and EARN-7 move frames BY DESIGN**, so the instant either lands, these artifacts are wrong for the census and regen ×3 becomes a HARD PREREQUISITE, not a hygiene item. Re-run this audit after any codegen landing; it is 122 compiles and costs ~2 minutes.
⛔ **NOT DISCHARGED:** regen ×3 itself is still owed. This section shows only that the debt does not contaminate *this* measurement. Scope: `crosscheck/patterns` only — `demo` and `benchmarks` were not audited.
⭐ **Free liveness datum:** 122/122 compiled clean in m4 (`--compile`), so the mode-4 asm path is healthy across the pattern corpus at HEAD.
