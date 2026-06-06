# HANDOFF 2026-06-06 OPUS48 — SNOBOL4-BB: BROK-2 + BROK-3 (ARBNO wired+shy; brokered mode eradicated)

**Session:** GOAL-SNOBOL4-BB ("here we go" named SNOBOL4-BB; brief wrong-goal detour into BB-FIXUP was reverted uncommitted before any push). Two rungs closed. SCRIP origin/main contains `7f3b5d0` (BROK-2) and `71a0625` (BROK-3); .github `ec975b39` carries the goal state; this doc follows. Watermarks in GOAL-SNOBOL4-BB.md are the single source of truth; this doc is the narrative + the time-costing facts.

## BROK-2 — ARBNO wired-child conversion + SHY (SCRIP `7f3b5d0`)

SPITBOL manual read FIRST (pp.121-122, 212; 137/250 are summary/efficiency only): ARBNO is SHY — null match first, each retry supplies ONE more instance, alternation legal inside the argument, `ARBNO(PAT)` ≡ `("" | PAT | PAT PAT | …)`.

- `emit_globals.h` + `flat_wired`; `codegen_flat_body(nd, prefix, text_externalise, wired)` — only the IR_PAT_ARBNO pre-build site passes wired=1 (CALLOUT/REF_INVARIANT stay call-convention).
- `xa_flat.cpp` wired TEXT arms: prologue = banner only (no `push r12`/`mov r12,rdi`/`lea r10`); epilogue = `jmp <base>_wγ` / `<ω>: jmp <base>_wω` (no eax=1/99 protocol, no FAILDESCR `[r12+0/4/8]` write — the LATENT note is RETIRED for ARBNO children, no pop/ret). `<base>` = `flat_lbl_α` minus the 3-byte `_α` suffix; same derivation lives in `bb_pat_arbno.cpp` from `bb_child_lbl` — ONE naming protocol, two ends.
- `bb_pat_arbno.cpp` regenerated SPEC v2 shy: α saves cursor to ζ-slot + `jmp γ`; β stores extension point (prev ζ-slot) + `jmp child_α`; `_wγ` carries the null-instance termination guard (`cmp r14d, prev; je exhaust` — a null instance adds nothing to the alternation equivalence); `_wω` restores saved + `jmp ω`. push/pop r10, the `.data` section, and the 256-byte depth stack DELETED.
- **Empirical oracle proof:** `'aaa' ARBNO('a') . V` unanchored → sbl `[]`, wired-m4 `[]`, m2 `[aaa]`. m4 is now sbl-faithful; m2 is not (flag below). GATE-3 rose 137-138 → **143/280** (shy now ref-matches the sbl-derived `.ref` corpus).

## BROK-3 — brokered-mode eradication (SCRIP `71a0625`)

Scope-first grep proved `bb_build_brokered` CALLER-FREE (BROK-0 probes had already proven the path dead; BROK-1/2 converted the holdouts). Deleting it removed the only `EMIT_BINARY_BROKERED` setter, the only `brokered=1` codegen call, and the hand-emitted brokered prologue bytes (`0x55 0x48 0x89 0xE5`). Cascade (−51/+29 net incl. fence): enum member + both case arms (emit_core); `g_bb_brokered` global + per-mode assignments; `BB_BROKERED`/`BB_WIRED` macros (zero consumers); `g_emit.flat_brokered` + its 8 pop-rbp ternaries (xa_flat.cpp); `brokered` param dropped from `codegen_flat_body`; tools/emit_per_kind_audit.c OR-clauses. Fence `scripts/test_gate_no_brokered.sh` AUTHORED (comment-stripped refs == 0 HARD), added to Session Setup.

## ⚠ FLAGS FOR LON

1. **M2-ARBNO-SHY** — the mode-2 oracle ARBNO (`IR_interp.c:3811`) is GREEDY (matches max instances at α, pops on retry) and diverges from sbl on unanchored capture (`[aaa]` vs `[]`). Harmless to today's gates (anchored patterns converge), but the shy m2 rewrite is its OWN rung — broad m2 counts can move. Needs your go.
2. **`bb_box_fn` typedef SURVIVES `(void*, int entry)`** — rt.c:480/529/595 invoke `p->fn(fb, 0)` (C α-entry into DEFINE blobs); the ladder's "if no survivor" clause applies. Dropping the typedef requires first converting those rt_proc entries to jmp-threading. Do NOT delete the typedef without that.
3. Pre-existing, untouched: `test_gate_em_template_matrix.sh` fails "template dirs not found" (env path, not in this goal's battery); `test/emit_baseline/-asm/patterns/052/054*.s` snapshots are now stale vs wired output (no gate consumes them; regen via `util_g8_session_emit_fix.sh` if wanted).

## Facts that cost time to learn (do not re-derive)

- `Δ` is ONE BSS cell in libscrip_rt.so (nm-verified) — every blob's `lea r10,[rip+Δ]` loads the same address, so wired children inherit parent r10 safely and ARBNO's push/pop pair was protecting siblings from a redundant reload. REG-RO TIER2 r10 count dropped ~24→~22.
- The wired-child contract (settled, REC-2 unblocked): no prologue; child keeps parent's r12/r13/r14/r15/r10; γ/ω are `jmp <base>_wγ`/`_wω` stubs; child ω leaves r14d at entry value (pattern leaves only advance on γ); child β re-enters the last-succeeded arm's β — that β entry is the hook for closing the FIDELITY GAP (deep re-entry of a matched instance's alternatives, e.g. `ARBNO('ab'|'a') 'b'` on `'ab'` — still open, no gate exercises).
- m3 never reaches the ARBNO TEXT arm: BINARY arm still bombs → rt_scan fallback; REC-2 (BINARY arm) should be built ON the wired contract, x86() in-band records.
- sbl one-liner method settles semantics disputes in seconds: `/home/claude/x64/bin/sbl -b file.sno` vs `--interp` vs compiled m4 — cheaper than arguing from the manual alone.
- Broad-gate counts this env (2026-06-06): GATE-3 143/280, GATE-4 162/280, M3-native broad 162/280. Full GATE-3 stash-baseline run exceeds the container's single-command time limit — budget two commands or rely on mechanistic attribution.
- ARCH-x86.md's EMIT_BINARY_BROKERED / dispatched-BB / `--bb-brokered` sections are now HISTORICAL (doc not edited this session).

## Gates at close (merged tree, after rebases over concurrent `e65893f` Icon, `6e6e29a` Pascal — zero file overlap)

build rc=0 · smoke 19/19 (m2 7/7 HARD) · M3-native 19/19 · rung M2=18/M4=18 (053 pre-existing) · broker 32 · prove_lower2 PASS · GATE-3 143/280 · GATE-4 162/280 · no_bb_bin_t 0 · REG-FENCE TIER1=0 · no-brokered 0 · no_vstack g_vstack=0 · purity floor 2 (no growth) · em_template_byte_identity 4/4.

## NEXT

**REG-RO** (frontier #1: READ-ONLY locals → `[rip+disp]`, per-box byte-map re-derivation, as+objdump verify). Then the FIDELITY GAP β-re-entry rung when a gate exists. **M2-ARBNO-SHY awaits Lon's go.**
