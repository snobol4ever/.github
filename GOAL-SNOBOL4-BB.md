# GOAL-SNOBOL4-BB — SNOBOL4 → native x86 Byrd-Box codegen

Frontend: SNOBOL4 → shared IR → BB emitter (mode-3 `--run` / mode-4 `--compile`). Protocol: RULES.md; template/encoder work requires ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md FIRST. Watermark is SHARED STATE — re-prove at session start AND close. History pruned 2026-07-30; full text in FINDING docs + git (pre-shrink = `.github` `2f3fd45a`).

---

## ⭐⭐⭐ LIVE CURSOR — s23d (2026-08-01) — ON-3 ARG-NOTE CLOSED + ON-0 RE-PROVEN + ⭐⭐⭐ ON-5 LANDED (the claim is finally zeroed end to end)

**Directive (Lon, this session):** *"Finish annotations. Continue."* then *"All your choices. I'm with you on this."* — the OBJ-NOTE ladder, my pick of rung. Took **ON-3 continuation** (the 189 `call rt_*` argument loads, the biggest opaque family left), then **ON-0**.

**LANDED (SCRIP `154a3fa8`, templates + two scripts):**
- **`x86_argnote()`** (x86_asm.h, hooked at `x86_4col`'s return) — argument loads now read `mov rdi, [rsp+96]  # slot`, the callee's OWN parameter name. ⭐ **189 sites, ZERO template edits.**
- ⭐⭐⭐ **THE CHOKE POINT IS TEMPORAL, NOT STRUCTURAL — the generalization of s23c's lesson.** The role CANNOT be known when the mov is emitted: the callee is unnamed until the `call` several instructions later, and the `+` chains evaluate in UNSPECIFIED ORDER, so no stateful lookahead is legal. But `bb_emit_x86` hands `emit_text_n` the WHOLE template body in ONE call, so when `x86_4col` runs, loads and `call` are both present — one backward walk names all of them. **When a fact is unknowable at emit time, ask which LATER PASS already sees it.** Reach for this whenever the blocker is "the templates evaluate in unspecified order."
- **`x86_arg_roles.h` GENERATED** (`scripts/gen_callee_arg_roles.py`) from the REAL runtime prototypes — no term invented. SysV slot arithmetic: `DESCR_t` = **TWO** slots (verified empirically, `a`→rdi:rsi / `b`→rdx:rcx), both halves naming the one object; floats skip GPRs; >16B by-value return takes slot 0 as hidden `sret`.
- ⛔ **THE RTX ASM PORTS ARE NOT C-ABI** — `rt_sg_scan.S` says so outright ("LEAN CUSTOM CONVENTION — NOT the C ABI"). C-derived roles would be WRONG for that family; theirs come from their own `.S` banner contract. **Any future register→meaning tooling must special-case them.**
- **124/143 tabled; 19 REFUSED rather than guessed** (`rax` = indirect call; `rt_make_list`/`rt_proc_value`/`rt_section_var` = CONFLICTING declarations; rest = no reachable prototype).
- **Two generator bugs caught before landing:** `return foo(a,b);` parsed as a declaration (would have invented roles from LOCAL VARIABLES); and no conflict detection (would have taken whichever declaration `os.walk` reached first — order-dependent, unreproducible names).

**PROOF — behaviour-neutral BY MEASUREMENT, not merely by construction:**
- roman.s **CODE IDENTICAL modulo comments** (strip-and-diff); 3614 → 3614 lines; notes 977 → 1165.
- ⭐ The **PRE-CHANGE `.s` was assembled and run** — output identical to post-change. **M4 == M3** identical.
- Gate sweep **931 programs: 0 stray `#@`, 0 notes on jump lines** (the GOTO column stays the jumps'). `scripts/test_gate_argnote_sweep.sh` added.
- mode-3 untouched by construction: `x86_4col` returns early for BINARY *before* `x86_argnote` runs.

**⭐⭐ ON-0 WATERMARK RE-PROVEN — `m3 279/27/11 · m4 266/39/10/2L`** (xc.sh, all 318, foreground chunks). **m4 EXACT vs carried s23a**; LERR set = the named 2L pair. The single m3 delta (280/10→279/11) is **`213_gc_exhaustion_churn`**, the harness-only m3 flake the LAWS name by name; m4's TIMEOUT set is the same list minus exactly it. **BY SET, never by count.**

**⛔⭐ TWO TRAPS RECORDED — full write-up in `FINDING-2026-08-01-CLAUDE-SN4-ARG-NOTE-RODE-THE-4COL-CHOKE-POINT-AND-MY-SWEEP-MISCOUNTED-266-PHANTOM-FAILS.md`:**
1. **A `find . -name '*.sno'` SWEEP IS NOT A WATERMARK.** Mine read `emit-fail=266/931` and I nearly handed it off as a regression. ~120 were a **CWD artifact** (relative includes), 67 CRLF, 21 §2 below, 6 the known LOWER subset. The gate now prints `emit-decline` with the warning inline so it cannot be misread.
2. **`hello.sno` IS MALFORMED, NOT A PARSER DEFECT.** `OUTPUT` sits in COLUMN 1, which the SPITBOL manual (p.37/p.45) makes a **LABEL**, leaving body `= 'HELLO WORLD'` with no subject. Oracle-anchored both ways: corpus file → `sbl -b` **SEGFAULTS**; one leading tab → prints `HELLO WORLD`. **SCRIP's rejection is CORRECT. DO NOT "fix" the parser to accept these ~21 files.**

**⭐⭐⭐ ON-5 LANDED (SCRIP `efc11e5f`) — CLAIM-ZERO now spells its destination RAW via `x86_zref` (`[rsp# + N]`).** Plain `RDQ("rsp",N)` text was RE-RESOLVED at encode time by `x86_frame_off`→`zvo_resolve` against the UCLAIM owner table, which rebased raw claim offsets as if they were FLAT and collapsed the upper ones onto the lower cells — the ARGREAD hazard at x86_asm.h:874, same remedy.
- ⚠ **WORSE THAN s23c RECORDED.** s23c had ONE witness at 30 stores/26 distinct. Re-taking the census across roman's 12 runs: the defect **SCALES WITH CLAIM SIZE** — (30,26) max 200 on a 240B claim (top 32 BYTES never written), plus **(62,40)** and **(78,56)**, 22 collapsed cells each. **SIX OF TWELVE runs collapsed.** AFTER: every run total==distinct and monotone; collapsed-runs **6 → 0**.
- **GATE 1 WATERMARK BRACKET — `m3 279/27/11 · m4 266/39/10/2L`, IDENTICAL to the pre-fix s23d baseline, and diffed BY SET across all 318: ZERO verdicts moved in either mode.** Equal counts alone would not show this; the set diff is what rules out a fixed/broken swap.
- **GATE 3 WITNESSES:** 066 + 053 PASS both modes. 165/183 remain m4 SEGV — consistent with s22z/s23a having already proven 165 **claim-zero-INDEPENDENT** by killswitch; this fix never claimed them.
- **GATE 4 ARTIFACT REGEN ×4 DONE** (the regen s23c deliberately deferred to this rung): crosscheck 482 · demo 20 · benchmark 21 · feature. **Insertions == deletions in every one** (55712/55712, 28141/28141, 4640/4640) — pure in-line destination changes, ZERO line drift, because the store COUNT was always right and only the destinations were wrong. emit-fail held at **15**, as-fail at the named **2L** pair.
- ⚠ Unlike ON-3 this **DOES change emitted code, in BOTH modes** — the raw spelling bypasses re-resolution for BINARY too, which is correct: both media carried the defect.

**NEXT — ORDERED:**
1. ⭐⭐ **ON-1 operand-kind plumbing** — root-caused s23c, still NOT landed; claim-zero discharges only 26/30 cells (top 32 bytes never written). It changes emitted code and **ON-0 above is now a FRESH bracket** to land it against.
2. ⭐ **ON-3 remainder** — `[rbp+N]` statement-region slots, then match_*/pat_*/defer housekeeping. **The argument-load family is CLOSED.**
4. **ON-4 srccomment echo repair** — Lon's original complaint, still untouched.
5. ⛔ **PENDING LON RULING:** the ~21 column-1 corpus files — repair (add leading blank) or mark `.xfail`?

---

## ⛔⭐⭐ PRIOR CURSOR — s23c (2026-08-01) — ON-3: the self-cell has a name, and the annotation found a real bug

**Directive (Lon, this session):** *"Work on annotating the generated S code"* then *"All your choices. I'm with you on this."* — i.e. the OBJ-NOTE ladder, my pick of rung. Took **ON-3** (housekeeping-term sweep); **ON-1/ON-2 remain blocked on the shared-params ruling**, unchanged.

**LANDED (SCRIP `816b1cf6` ON-3 batch 1 + `afbcab9b` ON-2 interim, templates only):**
- **`ZRESN()`** (x86_asm.h, beside ZRES/ZOPQ) — the box's OWN result cell named with the same lowercase spelling its `n<uid>_<kind>` label uses. ⭐ **Universal with ZERO per-template plumbing**: `op_node_kind` is staged at emit.cpp's SINGLE dispatch point (`:861`) for EVERY node. This is the ON-3 analogue of CARVE-ERAD's "the ~1054 reader sites need zero edits" — find the choke point, don't hand-edit 100 files.
- ⚠ **ROTATING buffer, deliberately**: `bb_kind_name`'s own buffer is a SINGLE static (unlike RDQ/ABSQ/ROQ which already rotate). Two differing kind names alive in one `+` chain would collapse onto the last writer. `ZRESN()` copies into an 8-slot rotor. NULL-safe (the `"note"` arm renders empty on a null name).
- **41 sites / 15 templates**, scripted per the s23b GVA pattern: 24 ZRES DESCR-pair stores · 3 `lea` address-of-out-param (coerce_integer/numeric/string) · 10 `bb_lit_scalar` DESCR-construction stores (DESCR layout confirmed against `contracts/descr.h` — 16B, v+slen at 0, value at 8, so both halves name ONE object) · 4 `bb_var_global` result stores, whose **GVA arm takes `gva_name()` not `ZRESN()`** (the variable's own name beats "var", matching what s23b established for the GVA reads two lines above).
- **CLAIM-ZERO pass named `stmt_claim`** (x86_asm.h:1951) — the single largest opaque class in the `.s`.
- **`ZOPAN()` — ON-2 INTERIM (`afbcab9b`), 25 sites / 12 templates.** The ladder's sanctioned no-ruling path: operand-a ONLY, via the `op_a_node_kind` emit.cpp:867 already stages at the single dispatch point. A `ZOPQ(0,·)`/`ZOPD(0,·)` read now names the box whose cell it consumes — roman.s consumer reads carry `# var` / `# binop` / `# coerce_numeric` where they read bare `[rsp+N]` before. Guarded on the `-1` no-operand sentinel (`bb_kind_name` would otherwise spell `op-1`). ⛔ **Operands b..n still need the `op_zkind[]` ruling — ON-1 is NOT unblocked by this.**

**PROOF — behavior-neutral BY MEASUREMENT, not merely by construction:**
- roman.s **CODE IDENTICAL modulo comments** vs pre-session baseline (strip-and-diff). Not one instruction moved.
- line count **3614 → 3614** across BOTH batches; notes **270 → 776 → 802**. Gate sweep re-run after each batch: 262 programs, 0 stray `#@`, 0 notes on jump lines, 46792 notes at close.
- **M3 == M4** on 12 pattern programs, zero diverge.
- Gate sweep **262 programs**: 0 stray `#@`, 0 notes on jump lines, 42230 notes. as-fail = **2** == the named pre-existing 2L pair (1017_arg_local, library/test_string). emit-fail = **1** (coverage_sno_nodes) = pre-existing LOWER SN4-PAT subset limit, **fails identically in mode-3** (verified, not assumed).
- mode-3 untouched by construction (notes are BINARY-empty).

**⭐⭐⭐ THE RUNG PAID FOR ITSELF: ON-5 IS ROOT-CAUSED AND IT IS NOT COSMETIC.** Full write-up in `FINDING-2026-08-01-CLAUDE-SN4-ON5-IS-NOT-DUPLICATE-ZEROING-...md`. Summary: naming the zero pass showed both runs are the SAME producer; hook instrumentation showed it fires ONCE per statement head; the offset census showed **30 stores / 26 distinct** per claimed statement — 4 cells written twice AND **4 cells (the TOP 32 BYTES of the claim) NEVER written**. Cause: the loop spells plain `RDQ("rsp",_zi)`, which `x86_frame_off` re-resolves through `zvo_resolve` — **the ARGREAD hazard documented at x86_asm.h:874, 1077 lines above the offending loop**. CLAIM-ZERO therefore only partially discharges the `rt_cap_push` zero-fresh contract it was landed (s23a) to guarantee, and the unzeroed window is at the TOP of the claim where a PIN-REBASE-relocated cap slot is most likely to land. Fix spec = the `[rsp#]` raw escape, one line. ⛔ **NOT LANDED — it changes emitted code and needs a watermark bracket.**

**WATERMARK: NOT re-proven this session** (annotation rung is provably code-identical; budget went to the ON-5 root-cause instead). Carried unchanged = s23a close **m3 280/27/10 · m4 266/39/10/2L**. ⚠ **This is now TWO sessions stale (s23b also carried it). ON-0 is overdue and should bracket the ON-5 fix.**

**Artifacts NOT regenerated s23c** — deliberate: the four regen scripts would rewrite every `.s` with pure note-tail deltas, and the ON-5 fix (next rung) will rewrite them again with REAL deltas. Regen once, after ON-5 lands.

**NEXT — ORDERED:**
1. ⭐⭐⭐ **ON-5 fix + ON-0 watermark bracket** (they go together — see the FINDING's gate list). Re-test 066/165/183/053 and the PIN-REBASE 7 against a claim-zero that actually zeroes the whole claim; s23a's killswitch exoneration of 165 was against a mechanism covering only 26/30 of its range.
2. ⭐⭐ **ON-1 operand-kind plumbing** — still needs the Lon ruling on `op_zkind[]` in the shared params struct. Interim operand-a-only path via `_.op_a_node_kind` remains available without a ruling.
3. ⭐ **ON-3 continuation** — with self-cells and operand-a done, the biggest remaining opaque family is the **189 `call rt_*` sites' argument loads** (`mov rdi/rsi/rdx, …` before the call); literal role terms per callee. Then `[rbp+N]` statement-region slots.
4. **ON-4 srccomment echo repair** — Lon's original readability complaint, still untouched.

---

## ⛔⭐⭐ PRIOR CURSOR — s23b (2026-08-01) — OBJ-NOTE: object references name themselves in the GOTO column

**Directive (Lon, verbatim, this session — a PIVOT off CARVE-ERAD):** *"What I need is a comment at the end of most x86/x64 instructions with one term, the name of the object being referenced. … In every case where some object is being referenced, I want to see it's name sharing the 4th column as the GOTO (JMP, JE, etc...) column. Do not put comments on lines that are a jump instruction since it takes the space of the fourth column."* Context: the `.s` files were unreadable (srccomment echoes out-of-order + duplicated; GVA accesses bare absolute addresses) so Lon could not direct deletions.

**LANDED (SCRIP, one commit + regen commits):**
- **x86_asm.h OBJ-NOTE mechanism:** `x86("note", name)` → in-band `#@name` marker line, folded by `x86_4col` onto the NEXT instruction line at the GOTO column (col 89, display-width-correct for Greek); jump lines NEVER take it (drop-on-jump); BINARY = empty string by construction; STATELESS across the templates' unspecified-evaluation-order `+` chains (the marker travels in the string, not a global); idempotent under the sink's second 4col pass (fold guarded on existing `#`); markers unmatched at chunk end re-emit so the sink pass (marker+instruction adjacent in one string) completes cross-call folds.
- **Name sources:** `gva_name(k)` (pre-existing gva_collect.c registry, now extern"C" to templates beside ABSQ) · `bb_kind_name(op)` exported (emit.cpp wrapper over flat_label_kind, same lowercase spelling as the `n<uid>_<kind>` labels) ready for the operand-BB case.
- **Wired:** all 34 `ABSQ(RT_GVA_VA…)` GVA sites (7 templates, scripted uniform insertion) + `bb_var_ref` address-of-GVA immediate + `bb_match_head` housekeeping ×11 (`outer_Σ/δ/Δ`, `cap_gen`, `old_rbp`, `stmt_base`, `cas_top`, `cas_rsp_mark`, `cas_patstk`). roman.s = 266 notes; the opaque `[1879052304]` pair is parameter N's GVA slot, now self-naming.
- **PROOF:** annotated .s assembles/links/runs; **M4 == M3 byte-identical** (roman + green GVA/capture probe `HELLO ABC`); zero stray `#@` markers; mode-3 untouched by construction (notes are BINARY-empty; 4col untouched for BINARY).

**WATERMARK: NOT re-proven this session** (Lon-directed pivot + handoff on a tight budget); carried = s23a close **m3 280/27/10 · m4 266/39/10/2L**. Behavior-neutrality evidence: regen sweep emit-fail=15 == s22z's 15 pre-existing; as-fail=2 == the watermark's 2L class (1017_arg_local + library/test_string, both named pre-existing); M4==M3 spot-proofs above. Next session MUST re-prove per protocol.

**Artifacts regenerated s23b under rung "OBJ-NOTE":** bench (21 files) + feature (SCRIP) + demo (19 files, corpus `ce100cbb`) + crosscheck (357 files) — all pure in-line annotation or note-tail deltas, deterministic on rerun (changed=0 verify pass).

**NEXT — ORDERED (formalized as ⭐⭐ LADDER OBJ-NOTE under ## LADDERS — executable steps ON-0…ON-5 + the usage doc; route follow-on sessions THERE):**
1. ⭐⭐ **Operand-BB reads (directive case 2):** `ZOPQ(k,·)` consumers need per-operand kind names — either `op_zkind[]` in the emit params struct (emit.cpp plumbing, SHARED STRUCT — needs Lon ruling) or operand-a-only via existing `_.op_a_node_kind` now. `bb_kind_name()` is ready either way.
2. ⭐ **Housekeeping-term sweep** across the remaining ~100 templates — mechanical, idiom proven (`x86("note","term") +` prefix).
3. **Duplicate frame-zeroing in n1_var** ([rsp+0..24] zeroed twice at α) — observed s23b, unchased.
4. **srccomment statement echoes out-of-order + duplicated** — the original readability complaint; carried.

---

## ⛔⭐⭐ PRIOR CURSOR — s23a (2026-08-01) — CARVE-DATA-ERAD: the whole-graph DATA is GONE

**Directives (Lon, verbatim, this session):** the s22w standing order (NON-POPPING FORTH RSP ζ, RBP only when absolutely necessary), then: *"How about just delete the whole-graph carve function? … I do not want ONE piece of code calling it EVER AGAIN."* and *"Alternatively delete the ENTIRE data structure that stores the whole-graph data. Either one will do, delete the CODE or the DATA, your choice. But it is GONE NOW!"* — **the watermark drop below is pre-accepted by these words; this section is the sign-off record.**

**LANDED (SCRIP commits):**
- `24ee32a8` **PIN-REBASE + CLAIM-ZERO** — the m4-SEGV-six root. x86_frame_off pinned-statement arm: under HEAD-PIN the pinned rbp IS the statement claim base → claimed flat offs rebase (off−umin), ZERO depth terms, gated `op_stmt_pin>0`; bb_match_head `hoff()` resolves pin save + staged op_stmt_pin together. CLAIM-ZERO: UCLAIM hook zeroes the claim at the run head (ZC_INIT_ZERO's first live class; rt_cap_push contract). Killswitch `SCRIP_CLAIM_ZERO=0`. Root evidence in commit (software watchpoint → rt_cap_push dword store zeroing environ[0] hi-half through [stale_rbp+0x190]; claim [256,432) K=176 vs quartet 320..344 / cap 384). **Software watchpoints WORK in this container** (066 recipe in transcript) — the HW-watchpoint ban stands, this is the substitute.
- `e3677e73` **CARVE-DATA-ERAD** — op_flat_disp producer DELETED (field permanently 0; fc_leaf_disp caller-less); zd_plan jmp-entry whole-graph veto + SCRIP_ZD_NOGRAPH gate DELETED (blob statements claim unconditionally).

**WATERMARK:** open = s22z close **m3 284/23/10/1 · m4 278/28/10/1+LERR1** (fresh open-baseline attempt was killed by the environment — nohup/background jobs DIE between tool calls; run xc.sh in FOREGROUND CHUNKS of 80, it is resumable). Mid (post-fix): 285/275, attribution EXACT vs stashed pre-edit build (`/tmp/s22z_bin`). **CLOSE (post-deletion): m3 280/27/10 · m4 266/39/10/2L.**

**DELETION PRICE (fix-forward punch list, all attributed by set-diff):**
1. ⭐⭐⭐ **op_flat_disp class** {061_capture_in_arbno TMO, 063/064/065_pat_fence_fn_*, 153/154} both-modes — fc_geom granted-cell INTRA-CLAIM compensation rode the deleted term. FIX SPEC: carry the granted prefix in zvo_resolve's dout terms — the ⛔ step-2 "narrowing" relocated INTO the claim authority. This is the head rung.
2. ⭐⭐ **PIN-REBASE debt** 7 m4 {056,162,164,173,W02_seq_basic/fail_propagate/nested} — bisected to the rebase (claim-zero exonerated via killswitch). LEAD: cut-site restores resolve through the CUT box's op_uhead/op_udout while hoff staged through the HEAD's — per-node owner-resolution mismatch, sequence/arbno shapes.
3. ⭐⭐ **NOGRAPH set** {1017_arg_local m4 LERR, 135/136_pat_balanced_parens m4}; win held: 1012_func_locals m3 FIXED; test_case TMO→FAIL (now diagnosable).
4. **m4-six residue** 161 (wrong output rc=0, monitor-first) · 165/183 (rc=139): 165 proven claim-zero-INDEPENDENT; main_γ epilogue rbp=0, zero output — defer-replay `dtp_fn_of`→`jmp rax` runtime chain suspected of repinning rbp without restoring the match pin (slab-level gdb needed).
5. **JANITORIAL (delete-the-code half):** dead `+op_flat_disp` terms (24-site manifest), fc_leaf_disp body, zd_stub_ok, the `_ng` remnant in zd_plan, then the **blob kt grant** once blob claims prove out. `zw_carve_k` is the per-BB REVIVAL candidate — despite the name it is NOT old code.
6. Carried: arbno-star-var 070-075 · FENCE whack-at-mark (130/150) · ZD-5a admission · glue backlog · JOIN-POINT · TREEBANK Pop_list.

**s22z NEXT list is SUPERSEDED by the above** (item 1 partially resolved: 066/122/179 green + 053/121; remainder folded into 2/4).

---

## ⛔⭐⭐ THE MODEL

**THERE IS NO GRAPH FRAME.** Every BB: **allocates at α** (`sub rsp,K`, *its own* K) · **reads/writes only its own cell** · **releases at γ/ω** · **jumps**. No pre-allocation, no whole-graph carve, no prefix-summed prologue.

⭐ **THE ONE REFINEMENT (law 4):** value spine rides RSP FORTH-style; housekeeping that must survive an unwind (ARBNO/FENCE1/CALL) rides a depth-immune RBP. `flat_stmt_frame` default is OFF (`SCRIP_STMT_FRAME=1` = opt-in); `op_zgpop` is the SOLE statement-terminal release authority.

**THE WHOLE-GRAPH CARVE IS A CORPSE.** `flat_frame_bytes` is debt; so are ~1054 `FR`/`FRQ`/`FRQB` reader sites across ~109 templates. **The job is to delete their customers until there are none, then delete the carve.**

### ⛔⭐⭐ CARVE-ERAD (head rung)

⭐ **THE ~1054 READER SITES NEED ZERO EDITS.** They resolve through `x86_asm.h:373 x86_frame_off()`. ⛔ Hand-converting 109 files is WRONG. **MANIFEST:** `flat_frame_bytes` 31 sites · `op_flat_disp` 24 · carve emission 7 · `x86_frame_off` 1 line. **ORDER:** (1) per-BB address authority complete FIRST; (2) drop `op_flat_disp` from `x86_frame_off`, delete its 24 sites; (3) delete `flat_frame_bytes` + 7 carve sites. ⚠ DO NOT cut sites before (1) covers their readers. ✅ Step (1) mechanism is `op_zread[k] = δ_out(consumer) − δ_out(producer)` staged by `zd_plan` — not a running-sum depth.

### ⛔ THE FAILURE MODES
- Treating the frame as infrastructure. It is a corpse.
- Clamping the carve while readers still address into it. Tautological — the reds name unconverted boxes.
- Misreading law 4's RBP constructs as licensing a graph frame.

### ✅ THE ONLY DISCRIMINATING TEST
Convert one box's readers to its own cell; watch the carve requirement DROP. Progress = monotone decrease of the declined-statement census.

---

## ⛔⭐⭐ LIVE CURSOR — s22z (2026-08-01)

Directive: s22y NEXT item 1 under Lon grant "All your choices. I'm with you on this." — blob/fence subject arming, decline retirement.

⭐⭐⭐ **FOUR LANDINGS, ZERO BROKEN BY SET. m3 233→284 (+51) · m4 229→278 (+49) — the largest single-session gain of the campaign.** The fence family (062-150), star-var/defer families, and grammar core collapsed into the pass column.

**THE CAUSAL CHAIN, each link measured:** (1) **BLOB-GRANT** (emit.cpp α, gated `scan_live && flat_jmp_entry`): CARVE-KILL had deleted the xa_flat jmp-entry seed and nothing replaced it for PAT$ blobs — no frame, no wire adopt, SCANBASE scribbling into the invoker's spine, rcx/rdx wires dropped. Re-landed verbatim (ef9a7d2c~1): `sub rsp,kt` + wires [kt-24]/[kt-16] + caller-rbp [kt-8] + pin, both media. (2) **CLASS D** at the exit-class ledger — the fourth citizen (`!wire_stub && flat_jmp_entry && flat_pat`): γ suspends (ZS-2 record {res-landing, rbp}, jmp γ-wire), ω unwinds absolutely (`lea rsp,[rbp+kt]`, jmp ω-wire); retires the CLASS O `exit(0)` disease on pattern blobs (1ba33ea6~1 spellings; BINARY lea rides `bb_emit_patch_rel32`, backward-resolve proven). 105/108 flipped PASS both modes on (1)+(2) alone. (3) **DECLINE RETIRED** (zeta_storage.c, killswitch `SCRIP_SUBJ_DYN=0`): the s22y casualties were BLOB defects wearing subject-arming's clothes, and the declined fence passes were VACUOUS (fail-branch refs — 061's own ref is the f-branch). (4) **HEAD-PIN + CUT-RESTORE** (`SCRIP_HEAD_PIN=0`): post-CARVE-KILL the law-4 statement slots `[rbp+N]` resolved against main's pin (m4: dead CRT territory, survived by LUCK) / rt_chain_enter's ambient frame (m3: LIVE — 061 armed = statement re-execution loop, gdb-sampled). The match CONSTRUCT now establishes its own base — `rbp := region base` at head α after the subject pop (rsp==base by the PATCTX invariant), old rbp saved rsp-relatively into op_off+40 — licensed by STF-UNFLIP's own words (construct housekeeping that survives an unwind; NOT a statement bracket). The restore rides the SOLE RELEASE AUTHORITY: `op_stmt_pin` (= the slot's region offset, staged at bb_match_head template top, retired at the next `bb_src_of` statement head in the drive walk) prepends `mov rbp,[rbp+off]` at zgpop cuts and `op_wterm`-discriminated wpop cuts (planner-terminal only — a mid-statement trampoline-ΣK restore would corrupt the live pin); head/release +40 tail restores gated off under the pin, since the direct af/β fail cuts bypass those tails entirely (the 061 slab witness: `add rsp,0xe0; jmp NO` with rbp left on the region → chain-γ whack against region base → wild ret → tail loop).

**FALSIFIED SPELLINGS, kept so nobody re-derives them:** (a) pin-slot at fixed region [rbp+8] — unsafe, SLOT-ELIDE can move a whitelisted run-head's locals to offset 0; the head's op_off+40 is the reserved slot (HEAD is elide-EXCLUDED). (b) op_stmt_pin cleared at uclaim staging — SEGV'd every armed program: unclaimed statements (bare `NO OUTPUT=...`) never stage one, the stale pin rode into THEIR cuts; lifetime authority is the bb_src_of statement head. (c) Exit-tail restores kept alongside cut restores — order conflict: tail restores old rbp, cut's `[rbp+off]` then reads the OLD frame.

**Instrument notes (gdb, hard-won):** batch-mode `break SYM` set BEFORE `run` on .so symbols silently never binds — every no-hit conclusion drawn that way this session was WRONG (cost: one full false root-cause). Bind after `start`/attach, or trace. `ni` at the `call *%rax` into the slab swallows the entire slab execution. The working recipe: `tbreak rt_outer_call; run; x/520i $rdi` = full static slab listing, no stepping; loop-PC sampling via repeated attach/`x/1i $rip`/detach.

**WATERMARK:** open m3 233/74/10/1 · m4 229/77/10/1 (REPROVEN at s22z open) → close **m3 284/23/10/1 · m4 278/28/10/1+LERR1**, ZERO regressions by set. DIVERGE 4→10: 164/170 RESOLVED; test_stack/1016 carried; NEW m4-only SEGV six {066,122,161,165,179,183} + m3-only {053(m4 now green!),127}. Residual shared core: 068/069, 070-075 (arbno-star-var), 121/126/131/140/141/143/145 (grammar), 160/180/181, 1012/1019. Artifacts regenerated s22z (bench+feature+demo+crosscheck, corpus committed; 15 pre-existing emit-fails noted in rg4 log).

**NEXT — ORDERED:**
1. ⭐⭐⭐ **m4-only SEGV six** (066 witness, rc=139): matches under DEFINE'd functions / defer replay — the TEXT-medium twins of paths m3's BINARY just proved green. Prime suspects: a TEXT-only defect in the three new emission sites (BLOB-GRANT text, CLASS D γ/ω text, cut-restore text) or proc-graph (floor>0) interaction with HEAD-PIN. Small, clean bracket.
2. ⭐⭐ **arbno-star-var shared core** (070-075): both-modes, the next family.
3. **053 m3 rt_cap_push SEGV** — carried (m4 side resolved this session).
4. **FENCE whack-at-mark refinement**: fence1 `as` whacks `mov rsp,rbp` (region base) — over-discards pre-fence element cells; correct target is the α mark cell; witnesses 130/150. Carried until after (1).
5. ZD-5a admission · glue backlog · JOIN-POINT RULE · TREEBANK Pop_list — carried. One-off anomaly: m3 stderr `BENCH exec=1641307ms` on an instant run (timer artifact, unchased).

---

## ⛔⭐⭐ PRIOR CURSOR — s22y (2026-08-01)

Directive (s22y): s22x NEXT item 1 under Lon grant "All your choices. I'm with you on this." — SUBJECT-CELL rung.

⭐⭐⭐ **SUBJECT-CELL LANDED DEFAULT-ON. m3 220→233 · m4 217→229, ZERO BROKEN BY SET, BOTH MODES.**

**THE PRODUCER-SIDE GATE IS LOCATED AND NAMED:** `zeta_storage.c` fc_geom vlit line's `!zc_nofc()` term (landed s22l to retire the ASSIGN-pair producer half) — it took the SUBJECT producer with it after s22r's NOFC default-flip, while the head's `fc_vread_fp` promotion carries no NOFC term. Consumer-armed/producer-flat, the exact s22s displacement. **Fix = fvs[] subject-membership table; the grant line becomes `(!zc_nofc() || fc_subj_member(nd))`.** Gate decoupled to ONE env (`SCRIP_SUBJ_CELL`, STMT_FRAME conjunct dropped — it rode the dead s21x STF-default era), then DEFAULT-FLIPPED (killswitch `=0`) on the s22r proof shape: strictly-better-by-set. Gate-off `.s` byte-identical (proven on 052); armed delta is surgical (producer `sub rsp,16` + rebased `[rsp+0/8]` writes via the fc_hit mechanism, ZERO template edits; head TOS pop replaces the corpse `[fb+op_sa]` read). Binop-tree subject branch now requires `!zc_nofc()` so it can never arm consumer-only. Fixed: the whole 052/054/065/W04 ARBNO family + 151/158/162/163/166/167 (+164 m3).

**DECLINE SET (measured, degrade never die):** graphs bearing IR_MATCH_DEFER / IR_MATCH_PATREF / IR_MATCH_FENCE1 stay flat-verbatim. Casualties that forced it: (a) **117/142 both-modes** — blob re-entry class: the *cmd / stored-eps blob's deep-repoint (`mov rbp,rsp; add rbp,-248` — a STATIC depth-model constant) and wire glue predate the subject grant; m3 died at ARBNO iteration 2 (rip=0x1000, rbp=0x100001 = DESCR-shaped restore, r15=Δ=3 proving the subject itself arrived correct), m4 silent-exit rc=0 with rt_match_ctx_restore NEVER called, frame chain into statement-1's slab region. (b) **061/107 m3-only** — inline-FENCE fail-path: OUTPUT CORRECT then hang (rc=124 at 20s) — the m3 exit-path scan spins at a 16-sensitive boundary. Blob/fence arming is the named follow-on; its first audit is the deep-repoint constant + the exit-scan termination predicate.

**Instrument notes:** (1) rt_defer_open/step breakpoints never fire on 117 — the defer rides the compiled-blob arm; do not bracket stored-pattern bugs at the rt_defer surface. (2) The 2-way monitor is DARK for this build (scr emits zero trace events) — MON-RE is prerequisite before monitor-first applies here. (3) `grep -l "\*"` on .sno matches comment lines — worthless as a defer detector.

**WATERMARK:** open m3 220/97/1 · m4 217/100/1 (REPROVEN at s22y open) → close **m3 233/84/1 · m4 229/88/1** · DIVERGE 4 {test_stack, 164_pat_arbno_nested (m3-fixed, m4 pre-existing fail), 170, 1016}.

**NEXT — ORDERED:**
1. ⭐⭐⭐ **Blob/fence subject arming** (retire the decline set): audit the deep-repoint `rbp=rsp−K` static model + wire-glue depth assumptions against the +16 grant; the m3 exit-scan spin (061 witness, output-correct-then-hang) is the cheap first bracket.
2. ⭐⭐ **Stored-pattern rt_cap_push SEGV** (053) — carried, C-side, gdb bt into rt_cap_push.
3. **ZD-5a admission proper** — carried.
4. Glue backlog residue + proc-shape admission + DYNAMIC BOX · FENCE whack-at-checkpoint · JOIN-POINT RULE · TREEBANK Pop_list — carried.
5. `.s` artifact regen NOT run this session (judgment call: `zeta_storage.c` is contracts, not on the RULES codegen file list, and the default flip changes armed-program `.s` broadly — next codegen session should regen).

---

## ⛔⭐⭐ PRIOR CURSOR — s22x (2026-08-01)

Directive: s22w NEXT items 1+3 under Lon grant "All your choices. I'm with you on this." — GLUE formalization + match-family FORTH-cell conversion.

⭐⭐⭐ **TWO LANDINGS, ZERO BROKEN BY SET, BOTH MODES.**

**(1) GLUE-SYM — SCRIP `8aceaaef`.** All 10 hand-rolled pass-through wire trios (`lea rcx,<γ>; lea rdx,<ω>; jmp rax`) → `bb_glue_pass_wires(gid,wid)`, ONE spelling tree-wide: bb_call_proc_staged ×5 · bb_call_value (+ missing bb_templates.h include) · bb_match_capture · bb_match_release · bb_match_defer L7 · **bb_match_value (the backlog's unlisted 6th member)**. Dormant legacy zr-anchor IF-arms hoisted above the glue (lea rcx/rdx touch neither rsp nor zr). PROVEN: `.s` byte-identical **0/318**, crosscheck IDENTICAL BY SET both modes. Glue taxonomy now symmetric: `flat/framed_enter+leave` (storage) · `outer_γ/ω` (CLASS O) · `wire_γ/ω` (CLASS P one-shot) · `pass_wires` (pass-through). Grid item FOUR stays dynamic per s22v Ch.9 ruling.

**(2) CAS-MARKER-CARRY — SCRIP `b016019d`. The match unwind is DEPTH-FREE.** The head's tag-0 sentinel (24B, 16 unused) now carries the rsp mark (+8) and patstk snapshot (+16); tail RELEASE, general RELEASE (RSP+rfc arm), and the head fail exit recover both off the marker they already scan to — the second variable-depth reach the original CAS-MARKER note promised deleted, is deleted. **ROOT CAUSE (041 class, gdb + static audit):** `op_fc_disp` counts fc_geom grants but NOT the ZW-1 alpha carves the non-popping γ spine leaves live — release entered 32 deep of its spellings, `[rsp+16]` read the assign_save leaf cell (dword cursor 0 under 0x7fff residue), one-mov unwind loaded rsp=0x7fff00000000, push SEGV. Backtrack path was immune (leaf βs pop); ONLY the success path exposed it. Fixed +3 (041_pat_span, 042_pat_break, 047_pat_rtab — the linear head→leaf→capture→release shapes). Non-default regimes byte-preserved (marker arms gated `ZC_FRAME_RSP && rfc()`).

**WATERMARK:** open m3 217/99/1 · m4 214/101/1 → close **m3 220/96/1 · m4 217/98/1** · DIVERGE 3 {170, 1016, test_stack} unchanged.

**REMAINING-FAIL DECOMPOSITION (fresh, s22x close; (a) CORRECTED by event trace — see FINDING-2026-08-01-CLAUDE-SN4-ARBNO-CLASS-IS-SUBJECT-DELIVERY-NOT-CAPTURE):** (a) **SUBJECT-DELIVERY class** — 052/054/065-family, rc=0 wrong output. THREE suspects acquitted by breakpoint event trace (capture append/retract balanced-and-correct topology · arbno re-yield through n12 · rpos semantics exact); the tell was **r15=0 at the rpos check** — the head's legacy `!subjc()` flat-slot subject read handed rt_match_enter garbage (rdi=0x401125, a code address), so the whole match ran honestly against an EMPTY subject and V='' is the truthful 0-rep capture. Fix surface = the s22s SUBJECT-CELL rung (subjc TOS pop; consumer arm exists in bb_match_head, PRODUCER-side gate still unlocated); (b) **stored-pattern rt_cap_push SEGV** — 053-class, C-side fault, rsp sane; (c) fence-via-var family (~15); (d) DIVERGE 3 carried.

**Instrument note (my own misattribution this session):** general-arm `RSP(fc_disp+8)` with fc_disp=0 and tail-arm `RSP(fc_disp+0)` with fc_disp=8 emit IDENTICAL bytes — verify which ARM fired from the template conditions, never from the emitted shape.

**Residue flagged, not converted:** release's dval≠0 arm (end-cursor stash) still speaks `fc_disp`-relative spellings — same disease class, convert when a dval witness fails on it.

**NEXT — ORDERED:**
1. ⭐⭐⭐ **SUBJECT-CELL rung** (the 052-class unlock, s22s carried): locate the producer-side gate that keeps the subject VAR on flat stores while `subj_on` arms the head's TOS pop; arm producer+consumer ATOMICALLY (the s22s bare-decouple falsification: consumer-only arming displaced ~52 pattern programs). The consumer arm already exists in bb_match_head (`subjc()`); the event-trace ladder in the FINDING doc is the verification instrument.
2. ⭐⭐ **Stored-pattern rt_cap_push SEGV** (053): C-side fault, gdb bt into rt_cap_push internals.
3. **ZD-5a admission proper** (IR_MATCH_HEAD into zd_wl_kind + zd_k/zd_nops) — the marker made the unwind depth-free, so admission no longer needs the disp model for the release.
4. Glue backlog residue: need-FOUR emitted glue behind label-redefinition gate + role-0 emitted one-shot open — carried.
5. Proc-shape admission (OUTPUT-in-body × zero-locals) + DYNAMIC BOX · FENCE whack-at-checkpoint · JOIN-POINT RULE · TREEBANK Pop_list — carried.

---

## ⛔⭐⭐ PRIOR CURSOR — s22w (2026-08-01)

Directive: "NON-POPPING FORTH-style RSP ZETA stack, C-style RBP occasionally only when absolutely necessary; allocate on ALPHA, free on OMEGA, WHACK-FREE at completion / FENCE checkpoint / known sync point; dynamic glue for one-shot and pass-through access to completed one-entry-one-exit BB graphs."

⭐⭐⭐ **DEFINE-FAMILY ARG DELIVERY FIXED + FORMALS/SAVE-SET SPLIT. +15 m3 / +14 m4, ZERO BROKEN. SCRIP `0522b634` (ARGREAD) + `42f4e9f7` (NPSPLIT).**

**WATERMARK:** open m3 202/113/2 · m4 200/114/2 → close **m3 217/99/1 · m4 214/101/1** · DIVERGE 3 {170_pat_abort_kills_match, 1016_eval, test_stack(m3 output-correct rc=139, m4 FAIL)}.

**ARGREAD mechanism:** templates emit flat coordinates, not addresses — every `[rsp+N]` is re-parsed at x86_asm.h:1208/1209 and re-resolved through `x86_frame_off` at encode time. `FRQ(128)` resolved correctly (zvo_resolve 128→112). `FRQB(slot,bump)` pre-added the bump into the flat coordinate (128+32=160), so the UCLAIM owner table was asked about a fictitious offset, declined, and the read landed one DESCR cell high — every slim-installed formal arrived as garbage (083 m3 `Illegal data type`). Fix: x86_zop's rsp arm now resolves via `x86_frame_off` FIRST, adds the bump, spells raw `[rsp# + N]` so nothing re-resolves. Both FRQB consumers fixed (bb_call_proc_staged slim install + bb_save_restore role-0 twin). ⭐ **s22t "UCLAIM dark" is CORRECTED: the resolver is live** — only the claim-emission hook (x86_asm.h:1935) was under suspicion, and the s22w addendum proves that too is live (staged K=128/192 == emitted `sub rsp,128/192`, claim+release both end-to-end). **UCLAIM is fully live at HEAD. ZD debt is PURELY the match-family FRQ migration.**

**NPSPLIT:** `nparams` keeps full-name-set meaning everywhere (save/restore span, pname bound, pad loop, consistency check). New `nformals` (ProcEntry + sno_def_t + rt_proc_t appended-last — rtx_call.S offsets pinned by _Static_asserts) is consulted only at arg boundaries: bb_scc_probe admission, open_slim nargs guard, classic-prologue excess clamp (manual Ch.8: evaluated then IGNORED), dc eligibility. 0 = unsplit registrant → fallback to nparams, byte-identical. All 6 direct driver sites + both emitted m4 startup arms register it. Sweep IDENTICAL BY SET vs ARGREAD arm — no corpus excess-arg witnesses; np7 probe is the evidence (`swap('hello','world','XX')` against `(a,b)tmp`: conflated arm binds `tmp='XX'`, split arm prints `tmp[] / world hello` manual-exact, m3=m4).

**Side sightings (not credited to this rung):** (a) test_stack m3 output-correct-rc=139 exit-path residual — joins DIVERGE. (b) Proc-shape entry/dispatch admission failure (7 witnesses, 6 acquittals — NEXT 4 bisect 3/4 done): body never enters on `OUTPUT=A` shape probes; 085 (result-arith body) passes, np7 (OUTPUT-in-body + locals) passes. Surviving suspects: OUTPUT-target-in-body × zero-locals admission path.

**Instrument note:** container shell is DASH — `[ "$a" == "$b" ]` with multiline strings silently mis-verdicts; wrap in `bash -c` and compare with `diff`.

**NEXT — ORDERED:**
1. ⭐⭐⭐ **Pattern-blob ZD family** — match family still speaks FRQ/op_flat_disp; with ARGREAD proving the encode-time resolution chain end-to-end, convert match-family readers onto zvo/ZD and the arming exclusion list retires itself.
2. ~~UCLAIM claim-hook bisect~~ **CLOSED by s22w addendum — no code change needed.**
3. **Glue backlog conversion** (bb_call_proc_staged ×5, bb_call_value, bb_match_capture, bb_match_release, bb_match_defer L7 arm) + need-FOUR emitted glue behind label-redefinition gate + role-0 emitted one-shot open.
4. **Proc-shape admission** (OUTPUT-in-body × zero-locals, 7 witnesses / 6 acquittals) — two probes close it.
5. DYNAMIC BOX · FENCE whack-at-checkpoint · JOIN-POINT RULE · TREEBANK Pop_list — carried.

---

## ⛔⭐⭐ PRIOR CURSOR — s22v (2026-08-01)

⭐⭐⭐ **EXIT-CLASS LEDGER LANDED. IDENTICAL BY SET, BOTH MODES (m3 205/112 · m4 203/113/1 · DIV 2 {170,1016}), ZERO FIXED ZERO BROKEN.**

**Three exit classes** (the ledger comment at emit.cpp's shared-γ/ω site is the authority): **CLASS O** outer one-shot — α pins rbp, γ/ω whack at completion (`bb_glue_outer_γ/ω`). **CLASS C** chain-entered (LBL__/EVAL/CODE, `rt_chain_enter` citizens) — rt_chain_enter never touches rbp; the whack unwinds to the ambient C frame pointer (why RBPPAIR broke 1016_eval). **CLASS P** wire-entered DEFINE stub blobs — `bb_glue_wire_γ/ω`: snap the pcall record, restore rsp/rbp from it, jmp home through the port's wire.

**Four-glue grid:** (ONE) MAIN→initial graph: one-shot static, COMPLETE. (TWO) BB_DEFER→pattern blob: pass-through, `bb_glue_pass_wires(gid,wid)` MINTED + canonical consumer converted. (THREE) call site→SAVE_RESTORE/CALL_FUNC graph: one-shot dynamic, `bb_glue_wire_γ/ω` LANDED. (FOUR) two-block SHIM→function body: pass-through THROUGH REGISTRY (`rt_goto_transfer`) — **MUST STAY DYNAMIC** (SPITBOL Ch.9: CODE labels override same-name main labels at runtime).

**Pass-through conversion backlog (hand-rolled trios, convert on touch):** bb_call_proc_staged ×5 · bb_call_value · bb_match_capture · bb_match_release · bb_match_defer L7 arm.

**RBPPAIR FALSIFIED — DO NOT RETRY.** The obvious cure (mirror the α guard at γ/ω) was implemented, proven present (positive control: ROMAN loses `mov rsp,rbp; pop rbp` while main keeps it), then measured: m4 IDENTICAL BY SET, m3 breaks `1016_eval`. The reason: `rt_chain_enter` pins rbp for jmp-entry citizens the emitter's α guard excludes — a second, unledgered pin authority. The exit-class ledger is the correct fix.

**Instrument note:** A/B artifact is `out/libscrip_rt.so` NOT `scrip` — snapshotting the executable gives two binaries with identical md5 both loading current templates (vacuous A/B). Snapshot `.so`, select with `LD_LIBRARY_PATH`. `make` silently no-ops after `git checkout` of one template — touch the TU and re-verify.

---

## ⛔⭐⭐ PRIOR CURSOR — s22u (2026-08-01)

⭐⭐⭐ **WIREREG: DEFINE RETURN WIRES WERE CALLER STACK GARBAGE — CARVE-ERAD CASUALTY. m3 +5 · m4 +5 · ZERO BROKEN. SCRIP `2edd3497`.**

The role-3 IR_SAVE_RESTORE wire-adopt box read `[rsp+kt-24]`/`[rsp+kt-16]` for the γ/ω wires — bytes written by `xa_flat`'s jmp-entry prologue, which CARVE-KILL (s22o) deleted. With no writer, every DEFINE'd function returned through a wild jmp (roman: rc=139, ZERO output, γ wire = `0x7ffff4dba3d8`). **The wires never needed storage:** both call paths already do `lea rcx,<γ>; lea rdx,<ω>; jmp rax`, and wire-adopt is the FIRST box of the stub blob, so rcx/rdx are still live. Fix = read the registers directly. Marshal order load-bearing: rdi←rcx, rsi←rdx BEFORE the rdx/rcx overwrites.

Fixed (3/3 bare exec, both modes): `084_define_loop_call 1010_func_recursion 1013_func_nreturn 1014_func_freturn 213_indirect_name`.

---

## ⛔⭐⭐ PRIOR CURSOR — s22t (2026-08-01)

⭐⭐⭐ **UCLAIM MECHANISM LANDED AND COMMITTED — statement-extent claim at declined run head's α + owner-table resolver in `x86_frame_off`. COMMITTED AS VERIFIED NO-OP (4-arm crosscheck IDENTICAL BY SET). First task of s22u: one fprintf at choke apply vs hook to find what dropped `op_uclaim`.**

⭐⭐⭐ **MECHANISM PROVEN END-TO-END BEFORE IT WENT DARK (pre-operand-closure build):** `sub rsp,144` (claim), subject DESCR at resolved `[rsp+128/136]`, head quartet at `[rsp+64..88]`, `add rsp,144` on all three exits — claim and release balanced. Two designs falsified en route: (a) per-node claims (re-carve leak per backtrack retry); (b) γ-chase-only membership (blob OPERAND nodes kept ghost spellings, crashing after correct output). Landed cure = OPERAND CLOSURE: membership = γ-chase run + transitive operands.

**Instrument law:** `setarch -R` AND canonical runner grandchild-env both cushion the s22r envp-corruption class — use static census (ghost writes in .s) and fixed-invocation A/B, never pass counts. Numeric watermarks don't transfer across harnesses.

---

## ⛔⭐⭐ PRIOR CURSOR — s22s (2026-08-01)

⭐⭐⭐ **THE 15-PROGRAM CARVE-ERAD PAYOFF IS A GATE COMPOSITION. WATERMARK IDENTICAL-BY-SET AT OPEN AND CLOSE: m3 204/113 · m4 188/128/1 · DIVERGE 16.**

The 15 programs are ALL pattern statements. The mechanism is already written: `bb_match_head` pops the subject DESCR from TOS (`op_subj_cell`) and `bb_match_release` carries the ONE-MOV UNWIND (`mov rsp, RSP(op_fc_disp+8)`) — both gated on `fc_vread_fp(head) >= 0`, whose walk never runs because `subj_on` conjoins two default-off envs.

**Bare decouple FALSIFIED:** `subj_on` default-on arms the CONSUMER while the PRODUCER VAR keeps flat stores — ~52 pattern programs broken both modes, reverted. Producer-side gate UNLOCATED (suspect layout-freeze ordering). This is the ZTOS reader-frontier law: arming a reader whose producer still speaks flat displaces the READER by its own pop.

---

## ⛔⭐⭐ PRIOR CURSOR — s22r (2026-08-01)

⭐⭐⭐ **NON-POPPING ZETA SPINE IS THE DEFAULT. m3 199/118 → 204/113 · m4 186/130/1 → 188/128/1, BREAKING ZERO. SCRIP `f6ee055` (NOFC-ONE) + `259b9cd` (NOFC-DEFAULT-ON).**

`SCRIP_NOFC` was two edits in one: the value-spine half (fc_geom vlit grant suppression) is a VERIFIED NO-OP — the value spine is fully ZD-armed, zero unarmed nodes left. **100% of NOFC's delta is the ZW-1 universal-carve suppression.** Killswitch now `SCRIP_NOFC=0`.

⭐⭐⭐ **CARVE-ERAD payoff sized: `SCRIP_M4_HEADROOM=65536` — one `sub rsp,N` in main moves envp out of reach WITHOUT converting a reader. m4 188/128/1 → 203/113/1 (+15, ZERO broken), DIVERGE 16→1 (sole survivor 1016_eval). The TRUE correctness figure is BELOW 203 — passing programs under the pad are CUSHIONED, not correct.**

Multi-authority collapse: `zc_nofc()` is now ONE site tree-wide (was 4 template-local getenv copies); flipping `zc_nofc` alone would have rearmed the producer/consumer asymmetry s22l diagnosed. PROVEN TRANSPARENT (all four fail sets diff IDENTICAL) then flipped.

**Instrument law: NEVER report a SCRIP timing delta from one run. Three runs minimum, report the spread.**

---

## ⛔⭐⭐ PRIOR CURSOR — s22q (2026-08-01)

⭐⭐⭐ **m3 ONE-SHOT BRIDGE PARITY FIX. m3 73/244 → 199/118 (+126, ZERO regressions). DIVERGE 125 → 13. SCRIP `150e903e`.**

m4 used `jmp main_α` (rsp ≡ 0 mod 16 at α); m3 used `call *%rax` (pushes 8 more) → α arrived rsp ≡ 8 mod 16 → SIGSEGV in the first C routine using `movaps`. **Fix = ONE CONSTANT:** `rt_outer_call`'s adjuster is 16, not 8.

**Localization method:** break on the C sink the graph calls, read `rsp % 16` at entry in BOTH modes. m3 = 8 → SIGSEGV; m4 = 0 → passes. The C-side `core_lib_init` calls in the same m3 process measured 0 — that separates "graph is skewed" from "runtime is broken."

**m3 IS CUSHIONED, NOT CORRECT** — m3 headroom ~20KB (deep C driver frames absorb stray writes), m4 headroom 344B (jmps from main, then argv, then envp). DIVERGE was partly measuring HEADROOM.

⭐ **ENVP CORRUPTION CLASS:** `__environ[0]` = `0x3` (a DESCR type tag written by `[rsp+568]` against 344B headroom). The ~1054 unarmed readers are NOT merely reading a dead region — they are WRITING THROUGH LIVE PROCESS STATE. **DO NOT RE-CARVE** — convert the readers.

**Static triage:** max `[rsp+N]` in .s vs 344B threshold — ~76 of m4's 130 failures share ONE authority; ~54 are different problems. Monotone progress metric: watch the >344 bucket empty.

**DO NOT re-carve with a big `sub rsp,K` cushion in main.** That is the whole-graph carve re-entering through the driver's door.

---

## ⛔⭐⭐ PRIOR CURSOR — s22p (2026-08-01)

⭐⭐ **ONE-SHOT BRIDGE + NON-POPPING WHACK. m4 64/252 → 186/130 (+122). SCRIP `05d250bd`.**

Three atomic changes: (1) `jmp main_α` (not call/ret); (2) outermost box owns its γ/ω as glue — whack + exit; (3) `bb_glue_outer_whack()` gated by `bb_glue_framed_enter()`. DIVERGE 15→125 expected (m4 changed exit path; m3 still returns eax to C).

**The epilogue was emitting the γ/ω port landings** — deleting it dropped m4 to 0 PASS/317 SKIP. Deleting `xa_flat_epilogue_str` (270 lines) + wrapper + dispatch + decl + enum, zero refs tree-wide.

---

## ⛔⭐⭐ PRIOR CURSOR — s22n (2026-08-01)

⛔⛔ **EMERGENCY HANDOFF — FLAT PROLOGUE EMITTER DELETED. m3 276/41 → 77/240 · m4 276/40 → 5/311/1. CORPUS RED BY DESIGN. SCRIP `983f24d3` + `ba46bb5e`.**

Lon directive ×3: DELETE `xa_flat_prologue_str`. 311 m4 failures is ONE missing authority. Revert = `git revert ba46bb5e 983f24d3`.

**The function was ONE authority for THREE entry shapes:** (1) jmp-entry carve — `sub rsp,K` + wire header + rbp pin + zero-fill (the corpse); (2) `GEN_RESUMABLE` heap-frame adopt (generator β-resume); (3) `STMT_FRAME` 8B parity pad (the design-of-record per-BB shape). Deleting the function took (3) out with (1). **RE-LAND IS STMT_FRAME ALONE AS ITS OWN FUNCTION, NOT A REVERT.**

**Instrument law: delete C functions by BRACE-MATCHING, never line regex.**

---

## HISTORY INDEX (one-liners; full text = FINDING docs + git)

- **s22m** (08-01) CLAWS5 + JSON oracle-match. Treebank root cause bracketed: H11 Pop_list rsp rose +104 (mod16=8), SIGSEGV glibc movaps. gdb available (`apt-get update && apt-get install -y gdb`).
- **s22l** (07-31) NOFC symmetric, +33 programs (ALL pat_*), m3 276/41 → 308/9. `SCRIP_NOFC` still off by default. ZD-SR (IR_SAVE_RESTORE roles 1/2/3 admitted, transparent). Attribution correction: the 33-program win is the CARVE SUPPRESSION, not the non-popping consumer read. Instrument law: run under `setarch -R`; ASLR is ±2 noise on every m4 figure.
- **s22k** (07-31) K authority collapsed to one site (was three). ZD-9 define-stub admission (`g_flat_frame_floor > 0` discriminator). Watermark m3 276/41 · m4 276/40 · DIV=3.
- **s22j** (07-31) ALT pair-defs were beta entries — every alternation segvd. `X86H_DEF_PAIR` new site code; `op_pair_rejoin` flag. m3 232/85 → 241/76, ZERO regressions.
- **s22i** (07-31) ZD-7 Slice 2 (IR_CALL builtin family). IR_CALL decline census 519→58. SIZE('hello')→5 ✅.
- **s22h** (07-31) ZD-7 Slice 2 engineering: PROC_STAGED exclusion mandatory (measured); planner changes require template arm atomically; `lea rsi` encoder gap identified.
- **s22g** (07-31) ZD-7 Slice 1 engineering: TAG-SAFE callee accessor; full callee partition; IR_CALL runs are not single-node; naive ZD arm −63 m3 (FRQ adds depth, wrong address).
- **s22f** (07-31) NON-POPPING RUNG OPENED. Five pops are Gen-1 FC, not STF consumers. Gate = ZD-7 (IR_CALL). FC census 163 firings / 29 programs; NOFC=1 breaks 20 (call-bearing statements). STF arming widen is the WRONG gate.
- **s22e** (07-31) LP-2 landed (RPO walk + zd_plan above xa_dispatch). `flat_all_zd` exact. Instrument trap: committed `.s` artifacts for claws5/json are ASSEMBLER-REJECTED at HEAD and will not regen until codegen defect fixed.
- **s22d** (07-31) LP-1 landed (BFS pre-prologue verdict). arithmetic.sno carve 248→8. Zero crosscheck programs fire.
- **s22b** (07-31) STF-UNFLIP (`flat_stmt_frame` default ON→OFF, SCRIP_STMT_FRAME=1 opt-in) + WPOP-1 (`!op_zres` guard at binop/unop sites). Crosscheck EXACT both ends, fail sets IDENTICAL BY SET both modes. **The fail edge was over-freeing by 32; the carve was absorbing it.** Carve deletion will EXPOSE every over-free it currently swallows.
- **s22a** (07-31) RPO-FILL v2 (post-order + per-root reversal; preorder trap: wholesale reversal loses `entry`) + ZGPOP-STF (zeroed at planner choke, not emission site). STF-armed 31/318. Consumer pops NOT deleted (serve the ~287 unarmed graphs). `add rsp,ΣK` FORBIDDEN — the seed's own annotation: "ZERO hand-counted pops."
- **s21x-z** (07-31) Four findings, zero commits. STF-FLIP is ceremony (HKQ never fires, 0/317). ZD-5a-PRE vacuous (cannot reach match-bearing graphs). Consumer pops violate port discipline. `.s` scramble is BFS fill.
- **s21x-y** (07-31) Value spine fully closed. ZD-2m IR_FIELD_VAR (last value-spine blocker). STF-FLIP (flat_stmt_frame OFF→ON). Watermark m3 232/85 · m4 229/86/2 · DIV=1 — held EXACT through s22b, s22c, s22r, s22u, s22v. Census 100% protocol: CALL 519 · MATCH_HEAD 247 · SAVE_RESTORE 18 · GOTO_DEFERRED 6.
- **s21x-x through s21x-v** (07-31) ZD-2 verdict widening complete (all value-spine kinds). ZD-1 landed (RSP FORTH per-BB stack, default-ON). ZD-2h retired (SNOBOL4 has no lexical locals). Carve debt re-derived live: 1054 sites / 109 templates, UNMOVED — ZD arms are additive, legacy arm survives beside each.
- **s21x-r** (07-30) STF defect was process-scope flag (ZLEAK-1/2). Armed set (31) and m4 regression set (41) DISJOINT. Declined-graph sweep 285→0: ALL-OR-NOTHING per graph now holds corpus-wide. Law: NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME.
- **s21x-q through s21x-e** (07-29/30) ζ-cell spelling sweep closed. ZTOS-1/2 sliding offsets. GLUE-3/4 wired. ZREL-1/2. LEN-GHOST fix. CALL2BB slices 1/2/3 landed. GOTO-ERAD survey. ZD whitelist widening beginning.
- **s186** (07-27) SN4-RTX split to its own file. Shrink-pass lesson: 8 live rungs deleted by prior prune, recovered from `950e6a9f`.

---

## ⛔ LON DIRECTIVE — s21x-c (2026-07-29): DESIGN OF RECORD

1. Every BB allocates its own storage: ONE `sub rsp,K`.
2. Sliding offsets, RSP-indexed; emitter tracks live depth at compile time.
3. RSP-only until a genuine brick wall, then RBP dance.
4. **Four RBP constructs: STATEMENT · FUNCTION · ARBNO · FENCE1.** Law 7: DEFINE's FUNCTION = IR_CALL's frame dance only.
5. Named anti-pattern (roman): `sub rsp,1344` whole-graph carve. WRONG.
6. DEFINE, constant-folded, emits exactly TWO BBs: IR_SAVE_RESTORE + IR_CALL.
7. **SCOPE LAW: statement level ONLY. No function-level processing.**

**DYNAMIC BOX GLUE (s21x-f):** any BB graph (one entrance, four ports) invokable by a DYNAMIC BOX. (A) DYNAMIC-FLAT: α `jmp [entry_cell]`, β `jmp [resume_record]`, γ/ω = supplied wires; zero frame. (B) DYNAMIC-FRAMED: + RBP/RSP dance. First customer: IR_MATCH_PATREF.

---

## ⛔ LAWS & TRAPS (binding; DO NOT RETRY marked experiments)

- **ζ GATE IS "ZERO MID-BODY CELL", NOT "ZERO RSP":** residual raw-rsp sites are classified NOT-ζ. Four legitimate classes: GLUE · C-ABI ALIGN · CSTACK SWAP ARM · PROLOGUE.
- **NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME:** `static int on = getenv(...)` inside a function taking `IR_graph_t*` is the defect signature. Cost 41 m4 programs.
- **DECLINED-GRAPH SWEEP before any default-flip:** every `live=0` graph must be byte-identical between regimes. Non-vacuous: check armed graphs still differ.
- **CENSUS UNITS:** always state the env with an armed count.
- **SUSPENDED-CELL (s21x-l):** no rsp cell may suspend across γ above an ARBNO/DEFER extent.
- **RESULT-IS-THE-CELL (s21x-k):** consumer overwrites the source cell IN PLACE, net-zero.
- **SOLE-CONSUMER FENCE (s21x-j):** subject registration requires IR_MATCH_HEAD be subjval's ONLY operand consumer.
- **UNION-TAG (s21x-g):** IR_t sval/ival/dval are ONE union — normalize at single dispatch point; never include IR_SAVE_RESTORE in op_sval promotion whitelist.
- **NODE-EXACT HANDOFF (s21x-g):** emission order is not a contract; key by CALL NODE POINTER.
- **STUB DISCRIMINATOR (s21x-h):** DEFINE-stub key = `g_flat_frame_floor > 0`.
- **DEFER-DEEP LOAD-BEARING (s197):** do NOT drop IR_MATCH_DEFER from deep-arrival until recursive-defer programs pass.
- **s206 DO-NOT-RETRY:** `x86_fc_cells()=(FORTH||HEAP)` predicate flip → wild jumps.
- **SCAN-RETRY = 5th rbp member (s196):** `&ANCHOR` is a runtime keyword; no static classifier retires the pin.
- **STALE-BINARY TRAP (s21x-j):** `[ -x scrip ]` is not a build check. Grep both make logs for `error:`.
- **op_flat_disp RIDES EMISSION ORDER** — any layout change must prove per-chain disp locality first.
- **CENSUS SHELF LIFE:** re-run, never cite. HEAD-STAMP every measurement.
- **COMPARE m4, NEVER m3:** `test_string`/`213_gc_exhaustion_churn` are harness-only flakes on m3. Diff fail sets BY SET, never by count.
- **RBPPAIR DO-NOT-RETRY:** mirrors the α guard at γ/ω, proven present, breaks `1016_eval`. The second pin authority is `rt_chain_enter` (CLASS C graphs).

---

## ⛔ PENDING LON RULINGS
- **FOUR-modes confirmation** — `ZC_STORAGE_{FRAME_R12,FRAME_RSP,CELL_STACK,CELL_HEAP}`.
- **Replacement-splice ruling (s21x-j):** splice reads the cell, or write-through — retires sole-consumer fence for replacement class.
- **SRC-ORDER-LAYOUT ruling A/B/C.**
- **RBP-SHED-7:** ⛔ blocked.

---

## LADDERS

### ⭐⭐ LADDER OBJ-NOTE — one-term object names in the GOTO column (mechanism landed s23b, SCRIP `eb0c08a8`; Lon directive 2026-08-01)

**HOW TO USE THE SYSTEM (read before any step):**
- **The idiom:** prefix the instruction's `x86(...)` call with `x86("note", <name>) + ` inside the same `+` chain. The note renders `# <name>` at the GOTO column (col 89) on the NEXT instruction line. Jump lines (`j*`) silently DROP it — Lon: never comment a jump, the GOTO column is theirs. BINARY medium = empty string, so mode-3 bytes are untouched BY CONSTRUCTION — no mode-identity risk from any note you add.
- **Name sources:** `gva_name(k)` — GVA slot → variable name (gva_collect.c registry, extern"C"'d in x86_asm.h beside ABSQ) · `bb_kind_name(op)` — IR op → lowercase kind, the same spelling the `n<uid>_<kind>` labels use (exported from emit.cpp) · string literals for housekeeping terms (`"old_rbp"`, `"cas_top"`, …; bb_match_head's 11 are the reference vocabulary).
- **Mechanics (do NOT re-derive):** the note is an in-band `#@name` marker line folded by `x86_4col`; stateless across the templates' unspecified-evaluation-order `+` chains (it travels in the string, never a global); idempotent under the sink's second 4col pass; markers unmatched at chunk end re-emit so the sink completes cross-call folds. Implementation lives ONLY in x86_asm.h (`"note"` arm in `x86_core_` + the fold in `x86_4col`).
- **Verify recipe per step:** `scrip --compile probe.sno` → notes at col 89, ZERO on `j*` lines, `grep -c '^#@'` == 0 stray markers; assemble+link (`gcc -no-pie X.s -LSCRIP/out -lscrip_rt -Wl,-rpath,…/SCRIP/out`), run, diff vs `--run` output (**M4 == M3**); then the four regen scripts (`util_regen_{benchmark,feature,demo,crosscheck}_s_artifacts.sh "<step>"`) — equal insert/delete counts = pure in-line annotation; emit-fail must hold at 15 and as-fail at the 2L pair unless the watermark itself moved.

**STEPS:**
- [x] **ON-0 WATERMARK REPROVE — DONE s23d: `m3 279/27/11 · m4 266/39/10/2L`.** m4 EXACT vs carried s23a; LERR = the named 2L pair; the lone m3 delta is `213_gc_exhaustion_churn`, the LAWS-named harness-only m3 flake. BY SET, never by count. ⭐ This is a FRESH bracket — ON-5 should land against it.
- [ ] **ON-1 operand-kind plumbing** (⛔ STILL needs Lon ruling — the s23c `ZOPAN()` interim covers operand-a ONLY and does NOT discharge this step — shared params struct): add `op_zkind[]` beside `op_zread[]` in the emit params, populated where `op_zread` is staged with each operand producer's IR op; templates then speak `x86("note", bb_kind_name(_.op_zkind[k])) +` before each `ZOPQ(k,·)` read. Interim without the ruling: operand-a only via existing `_.op_a_node_kind`.
- [~] **ON-2 operand-read sweep — OPERAND-A DONE s23c (`afbcab9b`, 25 sites/12 templates via `ZOPAN()`); operands b..n await ON-1.** scripted insertion (the s23b pattern — python regex per file, see `eb0c08a8`'s 34-site GVA pass) across the `ZOPQ(`/operand-FRQ consumer sites; verify recipe per batch.
- [~] **ON-3 housekeeping-term sweep — BATCH 1 LANDED s23c (`816b1cf6`); ARGUMENT-LOAD FAMILY CLOSED s23d (`154a3fa8`)**: the SELF-CELL class is done via `ZRESN()` (41 sites/15 templates) + the CLAIM-ZERO pass named `stmt_claim`. ⭐ THE LESSON: `op_node_kind` at emit.cpp:861 is a CHOKE POINT — one accessor named every box's own result cell tree-wide, no per-template plumbing. Look for the choke point before batching by family. ⭐ ARG-NOTE (s23d) closed the **189 `call rt_*` argument loads** via a TEMPORAL choke point — `x86_argnote` walks BACKWARD from each `call` in the 4col pass, where `bb_emit_x86`'s whole-body handoff has already made loads and callee visible together; roles GENERATED from real prototypes, RTX asm ports read from their own non-C-ABI banner contract. REMAINING: `[rbp+N]` statement-region slots, then the match_*/pat_*/defer housekeeping. bb_match_head stays the reference embodiment.
- [ ] **ON-4 srccomment echo repair:** the statement source echoes are OUT OF ORDER + DUPLICATED (Lon's original complaint) — root the echo emission order in emit.cpp's BFS layout vs source stno order; one echo per statement, source order.
- [x] **ON-5 — LANDED s23d (`efc11e5f`); census 6/12 runs collapsed → 0, watermark unmoved BY SET, regen ×4 done. Original s23c analysis below.** ⛔ The s23b framing ("find the two producers, delete one") is FALSIFIED: there is ONE producer, it fires ONCE per statement head, and the defect is a **misresolution**, not a duplicate. Census per claimed statement = **30 stores / 26 distinct**: 4 cells written twice AND **4 cells (top 32 BYTES of the claim) NEVER written**. Cause: `RDQ("rsp",_zi)` spells plain `[rsp+N]`, re-resolved by `x86_frame_off`→`zvo_resolve` — the ARGREAD hazard already documented at x86_asm.h:874. CLAIM-ZERO thus only partially discharges the `rt_cap_push` zero-fresh contract it was landed for. Fix = the `[rsp#]` raw escape, one line. **Changes emitted code → land it WITH the ON-0 watermark bracket.** Full write-up + gate list: `FINDING-2026-08-01-CLAUDE-SN4-ON5-IS-NOT-DUPLICATE-ZEROING-...md`.

### ⭐⭐ LADDER ZD

**CENSUS (s21x-y, re-run after every rung): 790 declined, first-blocker ranked — `IR_CALL` 519 · `IR_MATCH_HEAD` 247 · `IR_SAVE_RESTORE` 18 · `IR_GOTO_DEFERRED` 6. 100% PROTOCOL — value spine has no remaining members.** ⚠ Clearing a cheap blocker PROMOTES the expensive one behind it; a decline count is a frontier reading, NEVER a backlog.

- ✅ **ZD-2 COMPLETE** — all value-spine kinds ride the cells (LIT · VAR/ASSIGN-global · UNOP · BINOP · COERCE · CMP_TEST · KEYWORD_SNOBOL4 · SUBSCRIPT · DEREF · ASSIGN_VAR · FIELD_VAR). Declines 1060→790.
- [ ] **ZD-2c** `bb_binop_relop` — zero first-blockers today; arm when a widened statement declines on it. (`IR_FIELD_GET`, `BINOP_XREP`: vacuous by construction — Icon/Raku-only, zero SNOBOL4 customers.)
- [ ] **ZD-2g** UNOP closure (NULL/NONNULL/NULLTEST_VAR) — never first-blocks today.
- [ ] **ZD-3** Legacy arm retirement — per kind fully covered by ZD arm, delete vfc/vfcu/vfcb/vfcc + the `op_fc_disp` registration.
- [ ] **ZD-4** Lift the jmp-entry decline — `SCRIP_ZD_JMPENTRY=1` hatch; diff 1019's fragment .s on/off; fix; delete gate.
- [ ] **ZD-5 MATCH FAMILY (247) — the 85/86-red target.**
  - [ ] **5a-PRE** Ledger the STFH-48: `bb_match_head:32` emits `IF(stfh(), x86_zclaim(48))` but `zw_carve_k` returns 0 for IR_MATCH_HEAD → second unledgered allocation authority. Enumerate non-HKQ `[rsp+off]` refs first.
  - [ ] **5a** Linear-match bridgehead (head → LEN/POS/RPOS/SPAN/ANY/NOTANY/REM/TAB/RTAB → release; no alt/arbno/fence/defer/capture).
  - [ ] **5b** Planner extension for branching runs (alt, arbno cycles, defer). ⛔ The ONE genuinely design-tier item.
  - [ ] **5c** Per-template conversions, smallest-first.
- [ ] **ZD-7** `IR_CALL` (519) + `IR_SAVE_RESTORE` (18) — the protocol rung, law 4's other genuine RBP citizen.
- [ ] **ZD-6** Standalone: 130/131 clean-HEAD segv · DIV member W04_arbno_basic · bb_op_name entries for ops 14/73–77.

### GOTO-ERAD
- [ ] GE-0 census; GE-1 monitor-tap relocation (prerequisite); GE-2 survivor unprotection; GE-3 SNOBOL4 lower-side; GE-4..7 per-language; GE-8 emitter sweep; GE-9 enum deletion + gate.

### RBP-SHED (order 3→1→2→4→5)
- [ ] SHED-3 REC-PIN-OWN: move stale-emission globals to per-graph g_emit mirror at emit_chain choke.
- [ ] SHED-1 NPARAMS: retire `g_flat_outer_nparams>=1` pin conjunct for depth-static graphs.
- [ ] SHED-2 ABORT-REBALANCE: route ABORT through statement fail exit.
- [ ] SHED-4 HOOK-ENCODE: scanhit/scanfail hooks through x86().
- [ ] SHED-5 ALIGN-DANCE-DELETE: retire transient push-rbp alignment window.

### ✅ FB-STMT RE-ARM — CLOSED s22c (DEFAULT-ON, SCRIP `bdd6c23b`). Ceremony unchanged · data refs −44% · IDENTICAL BY SET both modes. Residue: pat/gen blob class excluded by construction at emit.cpp:2650 — extension shares surface with ZD-5.

### SRC-ORDER-LAYOUT (s21x-b): statement layout order scrambled (BFS fill). Awaiting ruling A/B/C. Gates: watermark, census, .s regen ×5.

### CARRIED OPEN: MARKER-CAPTURE · r9 park-address anchor · arm-quad OVERLAY · fc_cond FIRST-WINS · SYM-VIS-M3 JIT map · Icon generator-scan FORTH cells.

---

## ↗ MOVED OUT / SUPERSEDED
- **SN4-RTX** → `GOAL-SNOBOL4-RTX.md`. RTX-11/12 NOT concurrency-safe.
- **ZHEAP / CELL ladder** — superseded by s21x-c design of record. ZC_PORT_HEAP rbx α-carve stays dormant-ratified (HZ-1).

---

## ⛔⭐ WATERMARK OF RECORD (s22y close)

| runner | m3 | m4 | DIVERGE |
|---|---|---|---|
| **crosscheck 318, TIMEOUT=8** | **233/84/1** | **229/88/1** | **4 {test_stack, 164, 170, 1016}** |

Harness: `/tmp/xc.sh` (lean resumable 2-arm runner from .github, bare container exec). Prior record s22x: 220/96/1 · 217/98/1 · DIV=3 — REPROVEN at s22y open before any edit (fail/timeout split shifts with container speed; pass sets and diverge set exact); s22y +13/+12 (SUBJECT-CELL default-on; 164 joins DIVERGE as m3-fixed over a pre-existing m4 fail).
