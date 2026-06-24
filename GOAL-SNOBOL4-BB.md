<!-- GOAL-SNOBOL4-BB · SCRIP native pattern-match ladder for modes 3/4 (--run/--compile) -->

# ▶▶▶ NEXT SESSION — START HERE (handoff 2026-06-23m, session 13 · Claude Opus 4.8)

**State:** SCRIP `b3245a2` (PUSHED), corpus `351df26d` (PUSHED), .github THIS commit (PUSHED). Clean. **Bench BOMB 0, GREEN=12, DIFF=4** (eval_dynamic/eval_fixed/indirect_dispatch pre-existing; roman wrong result — concat double-walk fixed, local-var framing still pending).

**What landed (session 13) — literal-subject native scan, 4 files +54/−5:**
roman's scan 2 (`'0,1I,…,9IX,' T BREAK(',') . T`) declined native because `flat_drive_scan_stmt` gate keyed on a *named* subject only. Four-layer fix:
1. `emit_bb.c` gate: accept `op_scan_subj_lit` in addition to `IR_LIT(pBB).sval`.
2. `flat_drive_scan_native`: for a literal subject, attach an `IR_LIT_S` operand to the `IR_SUBJECT` node — `walk_bb_node` preamble (emit_core.c:332) unconditionally overwrites `op_a_sval` from `operands[0]`, so the literal must ride there.
3. `bb_subject.cpp` lit arm: fixed latent label bug (`lea [rip+??]`), `mov→lea`, added `bb_subj_litlbl()` helper, route through new `rt_subject_load_lit`.
4. `pattern_match.c` `rt_subject_load_lit`: sets ζ-slot AND global `Σ`/`Σlen` — `rt_cap_assign_cursor` reads `Σ` for capture base; the NV arm set it, the lit arm didn't.
Plus: `Σ`/`Σlen` save/restore around `p->fn(fb,0)` in both `rt_call_named_proc` variants (rt.c) — mirrors runtime_eval.c precedent; correct but not proven load-bearing for roman.

**Verified:** literal-subject match+capture correct (oracle-match on `'hello' LEN(2) . T`, `T=6`→`VI`, `T=1`→`I`, scan1 `RPOS(1) LEN(1) . T =`→`T=6 N=177`). Zero regression: PB-GREEN 6 green, 8 benches byte-identical `.s`.

**▶ NEXT MOVE — roman's recursive control-flow bug.** Roman no longer bombs but prints `MCXI` not `MDCCLXXVI`. Trace (with per-level `OUTPUT`, using `'176'`): each digit extraction and table lookup is correct (6→VI, 7→VII, 1→I) but the recursion **re-descends after the base case** — oracle 3 calls (6,7,1)→`CLXXVI`; ours (6,7,1,1,7,1,1)→`CXI`. This is a return-path/backtrack-re-entry bug, not a capture bug. The `Σ` save/restore did NOT fix it → corruption is elsewhere. Reproduce with:
```snobol4
    &TRIM = 1
    DEFINE('ROMAN(N)T')                   :(RE)
ROMAN N RPOS(1) LEN(1) . T =              :F(RETURN)
    OUTPUT = 'digit T=' T ' rest N=' N
    '0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' T BREAK(',') . T :F(FRETURN)
    OUTPUT = '  roman T=' T
    ROMAN = REPLACE(ROMAN(N), 'IVXLCDM', 'XLCDM**') T :S(RETURN)F(FRETURN)
RE  R = ROMAN('176')
    OUTPUT = 'RESULT=' R
END
```

**Design note (carried):** the `walk_bb_node` preamble clobbering `op_a_sval` is the same ambient-`g_emit` class the session-12 design candidate flagged. The fix sidestepped it (carry value as operand so preamble produces it). The general cure — port-field reset / FILL-only / debug gen-counter assert — is still unbuilt.

**Build:** `apt-get install -y libgc-dev && make && make libscrip_rt`. Oracle: `git clone …/x64 /home/claude/x64; sbl -b`. Tri-probe: `scrip --compile p.sno > p.s; gcc -no-pie -x assembler p.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs `sbl -b`. Benches: `corpus/benchmarks/snobol4/*.sno`.

---

# Open rungs (not yet started)

## OPSINGLE — delete operand_aux, one channel only

**Mandate:** exactly ONE operand channel: `nd->operands[]`. Delete `operand_aux` (`bb_operand_aux_set`/`bb_operand_aux_get`).

Writers still aux-only (add `ir_operand_push`, keep aux until readers flipped): `lower_snobol4.c` CALL args, `lower_icon.c:134,137,315`, `lower_raku.c:210`, `lower_pascal.c:147,162,177,340`, `lower_prolog.c:140`.

Readers to flip (`bb_operand_aux_get` → `nd->operands[]`): `BB_templates/bb_call.cpp:98`; `emit_bb.c:350,411,438,846,1072,1492,1818,2489,2957(DELETE bridge shim),3035,3240,3335,3398,3458`; `driver/scrip.c:102,245,1931`; `contracts/scrip_ir.c:355`.

Delete last (all readers flipped + all language gates green): `bb_operand_aux_set`, `bb_operand_aux_get`, struct fields, all call sites.

**Gate:** `grep operand_aux src/` (excl attic) == 0 AND all language gates green.

## REC-COV — community-recognized corpora

**Mandate:** extend coverage into community corpora. PB-GREEN stays session-first.

Inventory (pass-rates unmeasured — RC-0's job):
- `corpus/programs/gimpel/` — 145 `.sno` (no `.ref`)
- `corpus/programs/csnobol4-suite/` — 124 `.sno` WITH `.ref` ← start here
- `corpus/programs/snobol4/demo/` — 18 `.sno`

Steps: RC-0 honest runner + oracle-gen refs + triage table → RC-1 csnobol4-suite → RC-2 gimpel → RC-3 demo → RC-4 promote counts to hard floors → RC-5 re-ground "10×" claim.

---

# Completed / superseded (summary only)

Sessions 1–12 built the full SNOBOL4-BB ladder bottom-up:
- **DDS-0** (session ~8): deleted all `bb_*_proto[]` byte arrays, `DTP_t` head, `rt_dtp_run`. Ground-zero rebuild.
- **TR-1** (`7d6a9c9`): `sno_leaf_buildable` extended for `TT_CAPT_COND_ASGN`; capture patterns routed to builder, not orphaned.
- **TR-LEN** (`75f97e5`): `bb_build_len_blob` allocates `IR_MATCH_LEN` (matcher), not `IR_PATTERN_LEN` (builder). `r1`→`W=CD`.
- **Rename** (`2e5a5a3`): `IR_PAT_*` → `IR_MATCH_*` throughout.
- **TR-BREAK** (`15bda9d`): `bb_pattern_break.cpp` + `bb_build_break_blob`. First ζ-slot box; proves frame mechanism end-to-end.
- **TR-CAPTURE** (`1e962ed`): `bb_build_break_capture_blob`; `PAT=BREAK(',') . W`→`W=alpha`.
- **TR-CAT** (`5d6e7cd`): `bb_build_break_cap_lit_blob`; `PAT=BREAK(',') . W ','`→`W=alpha`.
- **splice fix** (`9ea1251`): `bb_scan_splice_empty` stripped of stale port scaffolding; string_pattern + mixed_workload GREEN.
- **literal-subject scan** (`f3f7cdb`, session 13): gate + `IR_LIT_S` operand + `bb_subj_litlbl` + `rt_subject_load_lit`. Last bomb removed.

Architecture constants (do not re-derive):
- `walk_bb_node` preamble (emit_core.c:328–333) overwrites `op_sval`/`op_ival`/`op_a_sval`/etc. from node+operands every emission — never rely on ambient values set before `FILL`.
- `rt_cap_assign_cursor` reads global `Σ` (set by `rt_subject_load_nv` and now `rt_subject_load_lit`).
- `flat_drive_cat_arms` reads the kids channel (`IR_EXEC(cat).counter`), NOT `operands[]`; a CAT with `nkids==0` emits empty.
- `bb_build_flat` entry CAT with nkids==0 emits empty — kids channel is mandatory.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**

