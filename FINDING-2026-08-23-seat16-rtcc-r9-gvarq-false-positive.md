# FINDING-2026-08-23-seat16-rtcc-r9-gvarq-false-positive

FROM seat16, RE rtcc-r9-gvarq-collision-bb-define (hq_C task assignment, this session)

## Scope

hq_C's brief (confirmed at HEAD, ranked 0): `test_gate_rtcc_claimed_regs.sh --strict` reports
`bb_define.cpp — clobbers r9 AND reads GVARQ [UNCLEARED]`, GATE: FAIL. Same defect *class* as the s6/s7
fibonacci SIGSEGV (r9 = RT_GVA_VA claimed by RC-5-GVA; a template that clobbers it and then reads
`GVARQ()` before it's restored corrupts the base for whatever global read follows). Task: establish
LIVE defect vs false positive by probe (RULES.md forbids conviction *or* acquittal by code-reading),
cure or clear, and make the gate enforce by default.

**Step 4 (make `--strict` the default arm) was already done** by commit `e88e77db` ("V2-5 gate honesty:
31 gates that could not say no now refuse an empty tree"), part of the 65 commits this seat pulled at
session start — see "Incidental: version skew" below. The gate's own usage docstring (lines 31-33) still
read the old, pre-V2-5 default and was never updated to match; fixed in this session as a two-line diff.

## Verdict: FALSE POSITIVE. Cleared in the registry, nothing to fix.

`bb_define.cpp` has exactly two live r9-write sites today (grep against the gate's own `wpat`/`rpat`
regex, `strip_comments`'d, matching what the gate actually scans):

**Site 1 — `bb_define_bind()` role 6, line 283: `lea r9, [rip+<entry-label>]` (or `x86_load_got("r9",…)`)
before `call rt_define_site`.** This call is auto-veneered: the generic `x86("call", sym, ptr)` dispatch
(x86_asm.h:1512, `a.kind==XK_SYM && xb.tag==2`) routes through `x86_rtcc_call`, and `rt_define_site` is
not in `x86_rtcc_clob_raw`'s whitelist so it gets the conservative `RTCC_C_ALL` clobber mask. The
mechanism that makes this safe is in `x86_rtcc_wb_bin`/`x86_rtcc_rl_bin` (x86_asm.h:375-393): the
writeback **unconditionally skips r9** (`(m & RTCC_C_R9) && !RTCC_GLOBAL_R9_GVA` — false, since
`RTCC_GLOBAL_R9_GVA` is `#define`d `1`), so the canonical `rtccb+48` seed is never overwritten with the
clobbered entry-label value; the reload **unconditionally restores r9** from that same, never-corrupted
seed (no `RTCC_GLOBAL_R9_GVA` guard on the reload side) right after the call returns. `bb_define_bind()`
itself has **zero** `GVARQ(` references anywhere in the function (confirmed by reading it in full), so H1
cannot occur regardless of the window's contents.

Confirmed empirically, not just by source-reading — probe `corpus/probe/rtcc/rtcc_define_r9_selfheal.sno`
(`DEFINE('ADD(A,B)')`, called with a GVA-claimed global argument so `bb_define_bind`'s call sites are live),
compiled with `--compile` (default settings, no env overrides):
```
lea   r9, [rip + n3_statement_begin_α]
mov   qword ptr [rip + rtccb+40], r8      ; wb: r8, r10, r11 written -- NOT r9
mov   qword ptr [rip + rtccb+56], r10
mov   qword ptr [rip + rtccb+64], r11
call  rt_define_site@PLT
mov   r8,  qword ptr [rip + rtccb+40]     ; rl: r8, r9, r10, r11 ALL reloaded, r9 included
mov   r9,  qword ptr [rip + rtccb+48]
mov   r10, qword ptr [rip + rtccb+56]
mov   r11, qword ptr [rip + rtccb+64]
```
(a second, identical wb/rl pair follows immediately for the M4-ALPHA-SEAL call to `bb_ab_seal_alpha`).
By the time the emitted code reaches its first `[r9+off]` access (the save-set spill in the following
activation body), r9 has already been restored — twice, redundantly. Mode-3 and mode-4 both execute this
witness correctly (`ADD(GV,5)` with `GV=10` → `15`, then `GV` re-read unmutated → `10`), though
correctness was never in question — the gate flags a register hazard, not wrong output.

**Site 2 — `bb_define_activate()` role 7, lines 139/144: `push r9` … `call mon_emit_call_bin` … `pop r9`.**
This is the *legacy* AB (activation-block) mechanism. `lower_snobol4.c` (~line 1959) gates the entire
path behind `getenv("SCRIP_AB")=="1"`; unset by default, so `g->ab_nodes[]` is never populated,
`bb_ab_emit_nodes()`/`bb_define_activate()` never fires, and this code is **dead under every default
build** — confirmed by `grep -rl mon_emit_call_bin corpus/` returning zero hits across the entire
regenerated corpus (hundreds of programs). This is exactly why the gate still lists `bb_define.cpp` in
the HAZARD SURFACE: the *text* contains the write; the *path* is unreachable without an explicit opt-in.

Compiled the same probe with `SCRIP_AB=1 ./scrip --compile`, forcing this path live:
```
push  rdi / rsi / rdx / rcx / r8 / r9 / r12 / rdi
mov   rdi, qword ptr [rip + .Lx62_0]
mov   qword ptr [rip + rtccb+40], r8      ; wb: skips r9, same as site 1
mov   qword ptr [rip + rtccb+56], r10
mov   qword ptr [rip + rtccb+64], r11
call  mon_emit_call_bin@PLT
mov   r8,  qword ptr [rip + rtccb+40]     ; rl: restores r9 too (redundant w/ the manual pop below)
mov   r9,  qword ptr [rip + rtccb+48]
mov   r10, qword ptr [rip + rtccb+56]
mov   r11, qword ptr [rip + rtccb+64]
pop   rdi / r12 / r9 / r8 / rcx / rdx / rsi / rdi
```
Zero `[r9+off]` access falls between the `push r9` and `pop r9` — H1 impossible by direct inspection of
the actual window. The enclosed call is *also* auto-veneered (same generic dispatch as site 1), so H2 is
impossible for the identical skip-writeback/unconditional-reload reason. Two independent layers of
restoration (manual pop + automatic veneer reload) agree.

**Action taken:** registered `bb_define.cpp` in `scripts/rtcc_claimed_reg_registry.txt` citing both probe
invocations and both `.s` excerpts above (registry format requires a named probe — code-reading alone is
not a clearance per the registry's own header). `test_gate_rtcc_claimed_regs.sh --strict` now: `GATE:
PASS (strict)`, exit 0. Re-verified after a `make pristine` rebuild (HQ-27); no source/template/emitter
file was touched, so this is a documentation+registry-only change — zero codegen risk. Ran the broad
SNOBOL4 corpus (`test_corpus_snobol4.sh`) post-rebuild as an extra sanity check though nothing in scope
could plausibly regress it: 358/359 both modes, the one failure (`demo_treebank`) pre-existing and
already tracked (`FINDING-2026-08-20-s192-...`, unrelated to this change).

## Secondary, out-of-scope observation — filed, not fixed

Compiling the probe under `SCRIP_AB=1 --compile` (default medium, TEXT) produces an `.s` that **fails to
assemble**: `bb_define_activate()`'s tail (line ~150) emits `x86("jmp_fn", blbl, ptr)`, and `jmp_fn` has
no TEXT-medium encoder — the literal text `jmp_fn FN__ADD` lands in the `.s` file, which is not valid
GNU-as syntax (`gcc -c` errors: "no such instruction"). This violates **BOTH-MEDIUM MANDATORY**
(CLAUDE.md) for the legacy AB path specifically. Not fixed here: (a) unrelated to the r9/GVARQ collision
this task was scoped to, (b) the path is opt-in-only and dead by default (see site 2 above), (c) mode-3
(BINARY) executes this same witness correctly under `SCRIP_AB=1`, so the defect is TEXT-medium-only and
narrow. Flagged to hq via `s4e_msg.sh ask` for queue triage — not minting a QUEUE.tsv row myself.

## Incidental: version skew at session start (process finding, not a code defect)

This seat's `SCRIP` clone was **65 commits behind origin** at session start (0 ahead, clean tree — pure
fast-forward, pulled without incident). Consequence while stale: `s4e_msg.sh next` parsed the *current*
`QUEUE.tsv` (v1, converted to the V2-2 rank/topic/owner/state index schema by hq_C) under the *old*
rank/topic/brief/step column assumptions, silently locking `name-lookup-strcmp` (an unrelated row) and
printing a meaningless `brief: unassigned` / `first: FREE` — an artifact of the schema mismatch, not a
deliberate pick. Zero work occurred on that row; released it (`claims.released.seat16-stale-picker-s263/`,
reason recorded in the claim file itself, matching hq_C's own precedent for this kind of release) and
claimed the actually-assigned row through the corrected, post-pull script instead. Also found and archived:
hq_C had assigned-then-released this same row at 01:26/01:49 UTC citing Lon's in-chat "no FLEET, just 2
HQ.s, duo" ruling (s258) — but the live `fleet` view at session time showed all 16 seats plus both HQs
holding open rows, so treated that release as time-scoped to a window this seat wasn't running in, not a
standing instruction, and proceeded on hq_C's (later, still-live) direct task assignment. Surfacing this
for HQ to reconcile — whether "duo" is still the intended operating mode is a fleet-wide question, not
a seat-local one.
