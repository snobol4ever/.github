# FINDING 2026-07-30 — PL ZETA-FB-3: THE SECOND PROLOGUE ARM IS NAMED, THE DUPLICATION WAS **SEVEN COPIES NOT ONE SITE**, AND THE NEW GATE IS FALSIFIED IN BOTH DIRECTIONS

**Session:** s161 in the `GOAL-PROLOG-BB.md` sequence (s158 → s159 → s160 → s161). ⚠ NOTE ON NUMBERING: the tree-wide counter is far ahead — `s221-PL` is the first session of the NEW sibling file `GOAL-PROLOG-RTX.md` (2026-07-30). Two Prolog goal files now run concurrently; this one is the ζ/BB ladder. Their session numbers are not comparable and neither is wrong.
**Ladder:** `ZETA-FB` — closes the item s160's cursor listed as NEXT (a).
**SCRIP baseline:** `b1ca896e` at session start (the HEAD s221-PL measured on) → **rebased mid-session onto `931d4e00`; shipped SHA `8e7ebd56`.** Origin advanced under this session and `emit.cpp` was among the files the incoming commits touched, so **every gate was re-measured after the rebase — see §5b.** The §5 table is the pre-rebase measurement; §5b is what certifies the shipped commit.
**RT_OPT:** `-O0` throughout, both builds. No `-O1`/`-O2` used or sought (O2-DIRECTED-ONLY); `grep -cE '\-O[12]'` on each build log = 0.

---

## 0. WHAT THIS SESSION DID

**DID:** named the second rbp-establishing prologue arm (`emit_heap_fb_adopt()`), routed **seven** re-derivation sites through it, made `emit_rec_pin()` the disjunction of two *named* arms, and added a gate that fires when a copy comes back — falsified by injection in both directions.
**DID NOT:** widen any predicate. One genuine semantic question surfaced (§4) and is left OPEN and measurable rather than silently resolved, because blind widening of exactly this shape is what s158 measured as a regression.

---

## 1. ⭐⭐ THE SUBSTRATE HAD MOVED UNDER THE CURSOR — CHECK FIRST, AGAIN

s160's cursor item (6) recorded this lesson and it applied to s160 itself. At `b1ca896e` there is now an **FB-STMT layer** that did not exist when s160 wrote its NEXT list: `x86_fb_data()` (`x86_asm.h:364`), `g_emit.flat_fb_refine` (`emit.h:597`), `emit_fb_stmt_scan`, `op_fb_rbp`, `flat_stmt_frame` — landed by a parallel session under the Lon directive *"Change every RBP to RSP that can be. I want only the housekeeping data indexed by RBP"* (2026-07-29).

**Consequence for this rung: none — but only by luck of layering.** FB-STMT refines **DATA SPELLING** only; it explicitly leaves ceremony, record protocol and epilogues reading `emit_jmp_pin_rbp`/`emit_rec_pin` untouched. The arm this session names is a **PROLOGUE** arm, so the two changes are orthogonal. Had FB-STMT touched the prologue, s160's NEXT (a) would have needed re-scoping before a single edit. **The check cost two greps; skipping it was never worth it.**

## 2. ⭐⭐ THE SHAPE WAS WORSE THAN THE CURSOR SAID: SEVEN COPIES, AND ONE OF THEM WASN'T IN xa_flat AT ALL

s160's NEXT (a) named a single site: *"`xa_flat.cpp:281`'s adopt arm and `emit_jmp_pin_rbp` STILL gate on different expressions … route 281 through a named predicate."* Measured, the raw disjunction `g_gen_proc_active || g_resumable_callable_active` appeared in **code** at seven places:

| # | Site | Role |
|---|---|---|
| 1 | `xa_flat.cpp:281` | heap-frame adopt prologue, **BINARY** |
| 2 | `xa_flat.cpp:401` | adopt prologue, **TEXT** twin |
| 3 | `xa_flat.cpp:411` | adopt prologue, TEXT |
| 4 | `xa_flat.cpp:418` | adopt prologue, TEXT |
| 5 | `xa_flat.cpp:525` | adopt **epilogue**, BINARY |
| 6 | `xa_flat.cpp:641` | adopt epilogue, TEXT |
| 7 | **`emit.cpp:2256`** | **β frame-slot dispatch** — NOT in `xa_flat` |

Plus an eighth spelling inside `emit_rec_pin()` itself, and five now-dead `extern int` declaration lines supporting the six `xa_flat` copies.

**Site 7 was hiding in plain sight and the tree said so.** `emit_rec_pin`'s own provenance comment reads *"the beta dispatch below ALREADY gates on this pair"* — the comment names the duplicate, and the duplicate outlived the comment. A cursor written from the code it just edited sees the sites it touched; it does not see the sites that describe themselves in prose two functions away. **A grep for the CONDITION, not for the site, is what found it.** Generalization: when closing a duplication seam, enumerate by grepping the duplicated *expression* across the whole tree, never by trusting the site list in the cursor that opened it.

## 3. THE CHANGE

`emit.h`, beside the two existing predicates:

```c
static inline int emit_heap_fb_adopt(void) { extern int g_gen_proc_active; extern int g_resumable_callable_active; return g_gen_proc_active || g_resumable_callable_active; }
static inline int emit_rec_pin(void)       { return emit_jmp_pin_rbp() || emit_heap_fb_adopt(); }
```

Two prologue shapes establish rbp as the frame base, and now each has a name:
- **arm 1 — SEED.** `xa_flat`'s jmp-entry hdr saves the caller rbp and seeds `rbp = rsp` at the activation's flat base. Gate: `emit_jmp_pin_rbp()`.
- **arm 2 — ADOPT.** `push rbp; mov rbp,rdi` — the frame arrives *already allocated on the heap* and is adopted; **no rsp frame is carved at all**, because the activation must survive β-resume and cannot live on a stack that unwinds. Gate: `emit_heap_fb_adopt()`.

`emit_rec_pin()` is now literally "arm 1 fired OR arm 2 fired" — the union written **once**, as the disjunction of the two producers, instead of one arm named and the other respelled. `x86_fb_pinned()` continues to read `emit_rec_pin()` (ZETA-FB-2, unchanged), so the base the prologue **ESTABLISHES**, the base a data ref **NAMES**, and the base the record protocol **NAMES** are one decision with one spelling.

**Naming discipline:** `heap_fb_adopt` describes *what the arm does to the frame base* — no language token, no `is_<language>`, so NO-LANGUAGE-SENTINEL and NO-LANGUAGE-IDENTITY-GLOBALS hold. `test_gate_emit_no_lang.sh` OK.

**Byte-neutral by construction, then measured** (§5) — identical boolean, one name.

## 4. ⚠ OPEN AND DELIBERATELY NOT CLOSED: THE β DISPATCH GUARDS NARROW AND SPELLS WIDE

Site 7 is:

```c
if (g_suspend_resume_slot >= 0 && emit_heap_fb_adopt()) {   /* body spells emit_rec_fb() / emit_rec_fb_num() */
```

The **guard** is the narrow adopt-only arm; the **body** names `emit_rec_fb()`, the wide union. **Sound today**, because adopt ⟹ `emit_rec_pin()`, so whenever this arm is taken the register the body names is right.

But the asymmetry has a reachable consequence: a graph that is `emit_jmp_pin_rbp()` (deep-arrival / pat / gen) but **not** adopt, carrying `g_suspend_resume_slot >= 0`, takes the **ELSE** arm — the label-scan resume path — by construction. Whether it *should* is a real question about the suspend protocol, not a typo.

**NOT RESOLVED HERE, ON PURPOSE.** No test fails, the suite is 164/164, the tripwire reports zero divergence, and widening a frame-base predicate blind is precisely what s158 measured as a **107/164 FAIL + SIGSEGV** regression. Per s160's own rule, the fix is not an argument, it is an instrument: this needs **a gate that fires when a `pin && !adopt && slot>=0` graph exists** before anyone touches the guard. If that class is empty in the corpus, the question is academic and the guard is fine as-is; if it is non-empty, the two arms need a measured decision. **Recorded as the next ζ-FB item, with the instrument named first.**

## 5. GATES — ALL GREEN, FULL-CLEAN `-O0`

| Gate | Result |
|---|---|
| `.s` byte-identity vs pre-change baseline | **184 / 184 identical** |
| Prolog rung suite `--mode interp` | **164 / 164** PASS, FAIL=0 |
| Prolog rung suite `--mode compile` | **164 / 164** PASS, FAIL=0 |
| `test_smoke_icon.sh` | 14/14 m3 · 14/14 m4 |
| `test_smoke_compile_hello_all_langs.sh` | PASS=6 FAIL=0 **ROWS_DRIFT=0** |
| `test_gate_fb_predicate_tripwire.sh` (s160) | 1911 programs / **0** divergences |
| `test_gate_emit_no_lang.sh` | OK |
| `test_gate_pl_no_new_global.sh` | PASS · doomed-ratchet **14 / floor 14** |
| `test_gate_fb_adopt_one_predicate.sh` (**NEW**) | PASS · one definition, zero re-derivations |
| `test_gate_template_medium_invisible.sh --strict` | FAIL `xa_flat.cpp(108)` — **PRE-EXISTING, COUNT UNCHANGED** (§7) |

**Byte-identity methodology, stated so it can be attacked.** 250 programs across three frontends (Prolog `programs/prolog`, Icon, SNOBOL4 `crosscheck`). Each was compiled **twice by the same binary first** and any program whose two `.s` differ was excluded as self-unstable — the banked uninitialised-`.string` class is a false-positive source for every byte-identity sweep, so it must be screened *out* rather than argued around. Screen result: **stable=184, self-unstable=0, no-compile=66**. The 184 md5s were captured before the edit and re-captured after **both** build stages; all 184 matched each time.
⚠ **LIMITATION, DO NOT OVERREAD:** `unary_not.sno` — the specific banked self-unstable program — **is not in this 250-program set**, so "self-unstable=0" is scoped to what was swept and is **not** a refutation of the banked defect. The 66 no-compile programs are unexamined here; they are excluded from the identity claim, not asserted healthy.

## 5b. ⭐⭐ THE TREE MOVED **DURING** THE SESSION — EVERY GATE IN §5 WAS RE-MEASURED AFTER REBASE

`handoff_status.sh` reported origin ahead on **all three** repos at session close: parallel sessions had pushed mid-flight. SCRIP origin had advanced `b1ca896e` → `b38e31d8` → `931d4e00` (RTX-24-ICN, four SN4 s21x-e commits, RTX-16-ICN, and **`931d4e00` PL-RTX RTX-1-PL SLICE 0** from the sibling Prolog file).

**`src/emitter/emit.cpp` IS AMONG THE FILES THOSE SESSIONS CHANGED** — one of the three this rung edits. The rebase applied cleanly (final SHA **`8e7ebd56`** on parent `931d4e00`), but a clean rebase certifies nothing about behaviour: **§5's numbers were measured on a tree that no longer existed.** This is s159's convergence lesson pointed at this session — *each session measured only its own half; the combination was never measured.*

**RE-MEASURED ON THE REBASED TREE, full-clean `-O0`, all green:** rung suite **164/164 interp + 164/164 compile** · icon smoke 14/14 m3 + 14/14 m4 · all-lang hello ROWS_DRIFT=0 · new adopt gate PASS · `emit_no_lang` OK · `pl_no_new_global` PASS (14/floor 14) · medium-invisible `--strict` `xa_flat.cpp(108)` **still 108, unchanged**.

**Byte-neutrality re-proven by DIRECT A/B against the parent commit, on the rebased tree** — the stale-baseline comparison in §5 could no longer support the claim, so it was replaced rather than reasserted: `git revert --no-commit HEAD` → rebuild → snapshot → `git reset --hard` → rebuild → snapshot. **70 / 70 byte-identical.**
⚠ **SCOPE, STATED PLAINLY:** the rebased A/B used a **70-program** subset (the first 70 of the screened-stable list), not the full 184, to stay inside the session's time budget. The 184/184 figure in §5 stands for the pre-rebase tree; the 70/70 figure is the one that certifies the **shipped** commit. Anyone wanting 184/184 on `8e7ebd56` should re-run the sweep with the full list — the method is in §5 and the harness is throwaway (`/tmp`, not committed).



`scripts/test_gate_fb_adopt_one_predicate.sh` asserts the adopt condition appears in **code** exactly once — in `emit_heap_fb_adopt()`'s body. Comment prose is exempt (provenance comments legitimately quote the old spelling; `x86_asm.h:362` does). The individual globals are **not** banned — the driver sets them and the divergence instrument reads them for reporting; only the **re-derived predicate** is.

This gate exists because of `GOAL-PROLOG-BB.md`'s own closing note: *an invariant that nothing checks and nobody updates is the defect, not the documentation.* Seven copies is what happens when the invariant lives in prose. Removing them without a gate just resets the counter.

**Falsified both ways — a gate that has only ever passed is not known to work.** This is s160's lesson applied to a new instrument: its Injection A *reported 0 hits and was nearly read as success* because the probe never entered the class.
- **Injection A** — re-inline the raw pair at `xa_flat.cpp:281` → **FAIL rc=1**, offender named at the correct line.
- **Injection B** — rename the predicate out of existence → **FAIL rc=1** on the "predicate is GONE" arm.
- Clean tree → **PASS rc=0**.

**A defect in my own gate, found by the injection and fixed:** Injection A first reported the offender at **line 239** for a fault at **line 281**. Cause: comment-stripping with `s{/\*.*?\*/}{}gs` **deletes the newlines inside multi-line comments**, so every reported line number is a post-strip number. An offender report that misdirects the next session to the wrong line is worse than no line number. Fixed by preserving the comment's newlines: `s{/\*(.*?)\*/}{my $c=$1; $c =~ s/[^\n]//g; $c}gse`.
⚠ **THE SAME BUG IS LIVE IN A SIBLING GATE:** `test_gate_template_medium_invisible.sh:11` uses the identical newline-eating strip. It happens not to matter *there* (see §7), but any future gate copied from it inherits a silent line-number lie. **Do not copy that line; copy the corrected one.**

## 7. `xa_flat.cpp(108)` IS A **COUNT**, NOT A LINE NUMBER — AND s160'S 106 IS STALE, NOT WRONG

Three sessions have now carried `medium-invisible --strict FAIL xa_flat.cpp(106)` as a pre-existing WIP baseline. **The parenthesised number is the per-file COUNT of raw-byte producers, not a source line** — this session briefly mis-read it as a line number while chasing §6's real line-number bug, and checking took one command.

Measured this session by `git stash` A/B on the identical tree state: **baseline 108, post-change 108 — unchanged.** So s160's `106` is not an error; the count moved 106 → 108 under the parallel FB-STMT landing. The figure is **owned by XA-FLAT-CONVERT**, is not this rung's to fix, and is confirmed here only as *not moved by this rung*.
**RULE THIS SUGGESTS:** a WIP baseline number carried across sessions must say **what it counts**. `xa_flat.cpp(108)` invites exactly the misreading above; `xa_flat.cpp: 108 producers` does not.

## 8. WATERMARK

- **SCRIP:** `src/emitter/emit.h` (new predicate + `emit_rec_pin` rewritten) · `src/emitter/emit.cpp` (β dispatch routed) · `src/templates/xa_flat.cpp` (6 sites routed, 5 dead extern lines removed) · `scripts/test_gate_fb_adopt_one_predicate.sh` (new)
- **corpus:** `<none>`
- **.github:** this finding + the `GOAL-PROLOG-BB.md` LIVE CURSOR

Per RULES.md (a) — **NEVER WRITE PUSH STATUS INTO A DOC** — this finding makes no claim about whether the above reached origin. `scripts/handoff_status.sh`, run live, is the only ground truth on that. s160's own cursor carried a parenthesised push-state claim; this one does not, deliberately.

## 9. BANKED (carried, unchanged by this session)

`unary_not.sno` uninitialised-`.string` non-determinism (a false-positive source for every `.s` identity sweep — screened around in §5, not fixed) · engine-wide silent-fail on undefined predicates · int/float standard-order conflation (two-oracle) · lexer escape three-site/two-behaviour · NO-LCO segfault · nested-`\+` binding leak · `retractall/1` gaps.

## 10. NEXT

1. **ζ-FB-4 — the §4 instrument, before the §4 edit.** Add a probe that reports any graph with `emit_jmp_pin_rbp() && !emit_heap_fb_adopt() && g_suspend_resume_slot >= 0`. Empty ⇒ §4 is academic, say so and close it. Non-empty ⇒ the β guard's narrow/wide asymmetry is a real decision needing measurement. **The probe must be falsified by injection before its zero is believed** (s160's near-miss, §6).
2. **PROLOGUE-ARM PARITY AUDIT.** Arms 1 and 2 are now both named, but nothing checks that a graph cannot satisfy *both* (seed and adopt), which would mean two prologues establishing rbp differently in one activation. Probably excluded by construction; **currently unmeasured**, and "probably" is what §2 was.
3. Then LADDER A features or the PL-SPEED ladder (SINK-5/6/7/9) — ζ storage blocks neither. ⚠ SINK-6 and SINK-7 premises were falsified s147; **re-measure before starting**. Also note `GOAL-PROLOG-RTX.md`'s s221-PL finding argues the SINK ladder makes the RTX ladder vacuous for Prolog by construction — read it before opening perf work, the two ladders now overlap.
