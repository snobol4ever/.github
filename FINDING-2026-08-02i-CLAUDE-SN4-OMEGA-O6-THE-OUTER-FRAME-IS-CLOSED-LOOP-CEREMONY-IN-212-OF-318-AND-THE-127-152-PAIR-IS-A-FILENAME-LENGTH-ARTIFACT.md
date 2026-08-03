# FINDING 2026-08-02h — [OMEGA] O-6 / ZW-6 CLASS O: the outer frame is CLOSED-LOOP ceremony in 212 of 318, and the 127/152 pair is a FILENAME-LENGTH artifact

**Session s26a (Opus). Parent SCRIP `1e0ba4ae` (SHED-3). Rung: O-6 · ZW-6 CLASS O glue relocation, slice 1 (GLUE-O).**
**Landed OPT-IN, default OFF: `SCRIP_GLUEO=1`. Diag: `SCRIP_GLUEO_DIAG=1`.**

---

## 1. THE CLAIM, AND WHY IT IS THIS FILE'S OWN LAW

`bb_glue_framed.cpp`'s header closes the framed flavor to law 4's FOUR RBP CONSTRUCTS — STATEMENT, FUNCTION,
ARBNO, FENCE1 — and says in so many words: *"Everything else is depth-static and belongs to the flat twin."*
STF-UNFLIP (s22b, Lon) then took STATEMENT **back out** of that set: *"it never licensed one bracket per
statement"*, and the statement release became `op_zgpop` = `add rsp,K`. `flat_stmt_frame` has shipped default
OFF ever since.

**Consequence nobody had drawn:** an ordinary legacy main graph with `flat_stmt_frame=0` qualifies for NONE of
the four constructs and was being handed a framed enter anyway, by the CLASS O outer glue. The frame is
established, restored, and never read.

## 2. MEASURED AT HEAD (318-program crosscheck `.s` corpus, not inherited)

| metric | value |
|---|---|
| programs bearing rbp | **317 / 318** |
| ...containing ANY `[rbp+N]` DATA reference | **105** |
| ...**CLOSED LOOP** (rbp established, restored, never read) | **212** |
| CLASS O `mov rsp,rbp; pop rbp` at `main_γ/ω` | **634** |
| ...immediately followed by `call exit@PLT` (never returns) | **634 / 634** |

The witness is the playbook's own compliant probe (`A=2 / B=3 / OUTPUT=A+B`, zero matches, zero calls,
zero ARBNO/FENCE): 6 rbp mentions, **0** data refs. The statement release `add rsp,32` already returns rsp to
base; `main_γ` then does `mov rsp,rbp; pop rbp` and calls `exit@PLT`.

## 3. THE PREDICATE IS NOT A NEW CLASSIFIER

Suppression fires on `g_glue_entered && !emit_rec_pin()`. `emit_rec_pin()` is the EXISTING union
(`emit_jmp_pin_rbp || emit_heap_fb_adopt`) that `x86_fb_pinned()` consults to decide whether a data ref NAMES
rbp — so `!emit_rec_pin()` is precisely *"no reader of this frame can exist."* ZETA-FB-1's divergence gate
(emit.cpp, grep `ZETA-FB-1`) already proves every input is FINAL for the graph before the enter site, so the
value at the enter and at the γ/ω whack cannot disagree.

**ONE AUTHORITY (the GLUE-SYM law):** the decision is taken in the same statement that computes
`g_glue_entered` and recorded in `g_glue_o_sup`, which `bb_glue_outer_whack()` reads. Enter and whack cannot
drift into the *"omitting (1) while keeping (3) loads the CRT caller's rbp into rsp"* shape the file's header
names.

## 4. ALIGNMENT IS NEUTRAL BY CONSTRUCTION **AND** BY PRIOR MEASUREMENT

Enter consumes `push rbp` (8) + pad `((K+8+15)&~15)-8` = 8 at K=0 → **exactly 16 bytes**. Dropping enter AND
leave together therefore shifts rsp by **0 mod 16**. EXIT-ALIGN (s22q) independently measured the post-leave
call site at `rsp ≡ 0 (mod 16)` — the parity both `call exit@PLT` (mode 4) and `ret` (mode 3) require. The
alignment hazard that made this rung look risky is closed on both arms.

## 5. GATES

| gate | result |
|---|---|
| Byte-identity, killswitch **OFF**, 318 programs | **318/318 identical** to parent `1e0ba4ae` |
| Regen ×4 (benchmark / feature / demo / crosscheck) | **zero changes** in all four (483 emitted, 0 changed) |
| Crosscheck BY SET, **length-matched** A/B (`SCRIP_GLUEO=0` vs `=1`) | **zero real regressions**, both modes |
| Bench board, both arms | **18/21 EXACT HOLD**, identical fail set `{eval_dynamic, eval_fixed, roman}` |

### RBP census, OFF → ON
| metric | OFF | ON | Δ |
|---|---|---|---|
| programs bearing rbp | 317 | **132** | −185 |
| total rbp instructions | 11 636 | 10 364 | −1 272 |
| `push rbp` | 464 | 252 | **−212** (= the closed-loop population, exactly) |
| glue whacks `mov rsp,rbp` | 953 | 529 | **−424** (= 2 per suppressed graph, γ+ω) |
| programs with `[rbp+N]` data refs | 105 | **105** | **0 — not one reader disturbed** |

The −212 / −424 land on the predicted population to the digit. The unchanged 105 is the safety witness.

## 6. ⭐ THE 127/152 PAIR IS A FILENAME-LENGTH ARTIFACT — AND IT NEARLY BOUGHT ME A FALSE WIN

The first A/B (no env var on the OFF arm) showed `152_pat_json_keyvalue_renamed` **newly PASSING** under
GLUE-O and no regressions — i.e. a free win. It is not one. Re-run **length-matched** (`SCRIP_GLUEO=0` vs
`SCRIP_GLUEO=1`, equal string length per the playbook's §5 ZD-4 warning), the result is **+152 / −127**: a
swap, net zero.

**`127_pat_json_keyvalue` and `152_pat_json_keyvalue_renamed` are the SAME PROGRAM under two filenames.** The
name is longer, argv is longer, initial rsp shifts, and the s23i placement class flips. This is the documented
env-pad instrument in its purest possible form — two byte-identical programs whose only difference is the
length of their own name, exactly one passing at a time.

⛔ **RULE FOR THE NEXT SESSION:** the playbook says hold env LENGTH equal across A/B arms. That is not
pedantry about env vars — **the corpus contains a pair that discriminates on FILENAME length**, so any
comparison that changes the process's initial stack in any way (env, argv, cwd) can mint or destroy a pass in
this pair. Report `{127,152}` as ONE bistable citizen, never as two results. GLUE-O did **not** cure it and was
never going to: it is a placement-class citizen, a different rung.

## 7. WHAT THIS TRADES (say it plainly)

The frame is today a **safety net**: `mov rsp,rbp` silently rebalances a spine that leaked. Suppressing it
converts a latent leak from invisible into a crash. **That is the point** — an unbalanced non-popping spine is
a defect and the net is what has been hiding it — but it is also why this ships OPT-IN. `bb_glue_flat.cpp`
serves Icon and Prolog too, so the default flip needs all three watermarks re-proven and is its own commit
(contract §6; the s203 ZW-1 lesson that an opt-OUT flip of a SHARED default cost Icon 30 programs).

That the corpus is BY-SET clean with 212 nets removed is positive evidence the spine is already balanced for
that population — the fused-terminal census independently reads **0**.

## 8. LEDGER CORRECTION — THE s25a CURSOR'S PUSH BANNER WAS FALSE

The OMEGA cursor carried **"⛔ MERGE GATE BLOCKED … Cannot push per §3."** All five s25a commits are on origin,
rebased: `2f8f9df7` (A-5) · `1c28155e` (O-3) · `dd45e5cf` (O-4) — and **two further rungs landed after it**,
`346d1d6f` (O-7a) and `1e0ba4ae` (SHED-3). The cursor also still named O-4 as head, routing an honest
orientation to an already-done rung and costing this session its first measurement pass to detect.

This is RULES.md FACT RULE (a) — *NEVER WRITE PUSH STATUS INTO A DOC* — recurring for the twelfth recorded
time. The banner is a claim about an event occurring AFTER the text is frozen into the commit; it is
structurally incapable of being true, and nobody edits a committed session-state block afterward. The recorded
hashes were also PRE-rebase, so they matched nothing on origin. **`scripts/handoff_status.sh` is the only
ground truth on push state.** Banner voided s26a.

## 9. NEXT

O-6 slice 2 = the **default flip**, gated on re-proving Icon + Prolog + SNOBOL4 watermarks (own commit).
Then the residue this rung does not touch: `old_rbp` ceremony (256 sites) dies with ZW-1's arm; `cap_gen`
(1 080 mentions / 175 programs) dies with **O-5 / ZW-3**, whose premise is re-confirmed at HEAD — **r12 is
still 0 mentions, 0/318 programs**, so its first commit is wiring + canary exactly as the playbook scopes it.

---

## 10. ADDENDUM (s26a close) — MERGE GATE AT `3473ecc8`, AND THE ZW5 FLIP IS A 1-FOR-2 TRADE

Twin commits arrived mid-session: ALPHA's A-7 ZD-5b bridgehead (LEN/ANY/NOTANY/POS/RPOS/TAB/RTAB/REM/SPAN)
and OBSERVER `542776a5`, which flipped `SCRIP_ZW5` to default OFF and recorded *"Full 318x2+bench owed next
session."* Rebuilt and re-ran the full §3 set at the merged head.

**GLUE-O is unaffected:** A/B **BY SET IDENTICAL both modes** (m3 281/26/10, m4 272/34/10/1L — zero newly
failing AND zero newly passing), bench **18/21 EXACT HOLD** both arms, census unchanged (317→132, `push rbp`
464→252, whacks 953→529, `[rbp+N]` programs 105→105, fused-terminal 0). The finding is therefore **robust to
Lon's ZW5 ruling**: the CLASS O outer glue frame is a different citizen from the ZW-5 statement box, which is
why the ruling and this rung do not collide.

**The owed measurement, discharged.** Re-bracketing open (`1e0ba4ae`) → merged head on the DEFAULT arm:

| mode | fixed by the merge | broken by the merge |
|---|---|---|
| m3 | `067_pat_fence_fn_vs_kw`, `127_pat_json_keyvalue` (bistable, §6) | — |
| m4 | — | `164_pat_arbno_nested`, `173_pat_fence_kw_blocks_backup` |

**ATTRIBUTED BY DIRECT A/B, NOT INFERRED:** both m4 losses return to PASS under `SCRIP_ZW5=1` at this same
head. They belong to the FLIP — not to ALPHA's ZD-5b admissions, and not to GLUE-O.

⭐ Worth Lon's eye: `164_pat_arbno_nested` was O-2's own cited witness (*"m4 … zero P→F, 164 passes"*) and
`173` was s25a's LIT-admission gain; the flip surrenders both. The cure it buys (`067`) was a HANG; the two it
costs are wrong-output. Whether that is the trade wanted is a ruling, not a measurement. **Not reverted** —
`SCRIP_ZW5`'s default is Lon's ruling in the OBSERVER seat, not OMEGA's to undo. Recorded here so the next
session inherits the number instead of the impression.
