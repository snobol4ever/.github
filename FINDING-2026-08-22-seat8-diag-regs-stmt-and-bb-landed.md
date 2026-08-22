# FINDING — seat8: `diag-regs-stmt-and-bb` LANDED — r10/r11 live crash telemetry, both media, killswitch proven inert

**Date:** 2026-08-22 · **Seat:** seat8 (`/home/claude08`, Claude Sonnet 5) · **Topic:** `diag-regs-stmt-and-bb`, task 3 of 3 in Lon's telemetry ladder (`free-r10` → `free-r11` → this row) · **Status:** DONE.

## 1. Unblocked, then landed

This row's own earlier cursor (same seat, prior session) found it correctly blocked: `free-r10`/`free-r11` claimed DONE while two live r10/r11 survivors still existed, contradicting the DONE-WHEN. HQ's s256 ruling (`FINDING-2026-08-22-s256-hq-free-r10-and-free-r11-had-an-inverted-done-when-...md`) diagnosed the DONE-WHEN itself as inverted — "free" means legal scratch with documented dedicated exceptions, not zero textual mentions — and declared both rows DONE, unblocking this one. Full design, the collision analysis, killswitch proof, the mode-3 dense-nid bug found and fixed, and the honesty-clause measurements are all in `ARCH-SNOBOL4-RTX.md` §2 (the CLAIMED bullet) — this FINDING is the discoverable pointer and handoff summary, not a duplicate of that writeup.

## 2. What landed (SCRIP `c5e97682`)

- **r10 = SNOBOL4 statement number**, written in `bb_statement()` right after `x86_alpha()` — one template body, shared by `IR_STATEMENT_BEGIN`/`IR_STATEMENT`/`IR_STATEMENT_END`, no per-op filter.
- **r11 = BB node id**, written centrally in `x86_port_hook()` for `(X86H_DEF or X86H_DEF_PAIR) at (ALPHA or BETA)` — the one ancestor every box's port-definition already routes through (ordinary boxes via `x86_alpha()`/`x86_beta()`, looping boxes' beta-redefinition via `x86_deflabel_pair()`), so every box family in every language gets it uniformly.
- Both are a single existing `x86("mov", reg, imm)` call. Zero new `x86_asm.h` encoders, zero new globals (`_.op_stno`/`_.nid` were already staged `g_emit` fields).
- **Killswitch `SCRIP_DIAG_REGS=0`** (default on), measured byte-identical to the pre-row tree across 322 `corpus/crosscheck` programs, re-confirmed after two rebases through concurrent sessions' work.
- **Suppressed** inside the `wire-suspend-cache-clobber` survivor's own live span (`emit.cpp:2744`/`:3052`) via `emit_diag_regs_suppress()`, which recomputes that site's own existing condition — no new state, and this row does not touch that survivor's own open rung.

## 3. A real bug this row's own DONE-WHEN caught, that no existing gate could see

`bb_node_id()`'s dense sequential numbering (`g_m4_dense_nid`) was enabled only on the mode-4 driver path. Mode-3 (`--run`) silently used the non-dense `(uintptr_t)nd % 100000u` fallback — r11 read as noise (24736) instead of the box's real id (7) under `--run`, while mode-4 was already correct. **Invisible to `test_corpus_snobol4.sh`'s full both-modes run** (a write-only diagnostic register changes no program output) — only reading the register directly, which the DONE-WHEN's crash-witness requirement forces, surfaced it. Fixed on the mode-3 SNOBOL4/Icon/Raku/Prolog dispatch too, gated behind the same killswitch via a C-linkage `x86_diag_regs_on_c()` twin (the established `x86_zdp_on`/`x86_zdp_on_c` pattern). Re-verified both media post-fix via genuine SIGSEGV + core-dump witnesses read from fresh gdb sessions.

## 4. Honesty clause (measured, not assumed)

Both registers read "the last statement/box **entered**," never a guarantee of "the statement/box that **faulted**." Measured on the checked-in witness (`corpus/probe/diag_regs_witness.{sno,ref}`, a `BREAK('D')` match): `n6_match_begin`'s `call rt_match_enter@PLT` clobbers r10 as ordinary scratch inside that call, in both media identically, while r11 — refreshed once per box rather than once per statement — survives to a correct reading whenever the fault lands in the currently-executing box's own straight-line code with no RTX call intervening since that box's own alpha/beta write. This is not a defect to fix; it is the honest shape of "free scratch register" telemetry, and it is why the writeup calls this a complement to (not a replacement for) the DWARF-loc/box-symbols row and the §9 DESCR provenance stamp.

## 5. Verification, final numbers (post both rebases, on the pushed tree)

- SNOBOL4 corpus: m3 PASS=357 FAIL=2 · m4 PASS=355 FAIL=2 SKIP=2 (359 total; +2 vs this session's own opening baseline of 355/2·353/2/2skip — two new `ident_call1`/`ident_call2` benchmarks landed concurrently and both pass). Same two pre-existing fails throughout (`160_pat_alt_inner_gen_resume`, `demo_treebank`), same two skips.
- Icon 14/14, Prolog 3/5, Snocone 4/5, Raku 705/724 — all identical to pre-row baseline (independently re-confirmed via a stash A/B, not assumed).
- `test_gate_template_medium_invisible.sh`: unchanged, 0 in `bb_*.cpp` (the pre-existing 8-site `xa_flat.cpp` Icon WIP debt untouched). `test_gate_emit_no_lang.sh`: OK.
- Beauty M1 mode-4 fixed point (622-line self-host) still holds; mode-3's pre-existing, already-known divergence starting at line 10 (an `-INCLUDE` gap, confirmed pre-existing via the same stash A/B) is unaffected — not this row's defect, not chased here.
- `make pristine` EXIT=0, re-proven after two separate rebases (each pulling in real concurrent codegen work — `bb_define.cpp` r11/ω eradication and the RTCC call-stub r10 retarget — that this row's own killswitch and suppression logic had to, and did, coexist with cleanly).

## 6. Concurrent collisions handled, not just noted

Two other rows landed mid-session and both touched code this row's own writeup discusses: `rung E-4` (`bb_define.cpp`, moved the DEFINE-shim's ω half off r11 onto rax) and `rung-E6-x86-asm-h` (retargeted the RTCC call-stub off r10 entirely). Neither required a code change here — this row's hook lives in `x86_port_hook()`/`bb_statement()`, structurally independent of both — but both required rebasing through real `.s`-artifact merge conflicts (resolved by regenerating from the compiler post-rebase, per RULES.md: `.s` is honest current output, never a merge target) and one prose conflict each in `ARCH-SNOBOL4-RTX.md` (resolved by keeping the newer content and correcting one now-stale sentence of this row's own writeup that referenced `bb_define.cpp`'s pre-eradication r11 use).

## 7. Not touched, correctly out of scope

`wire-suspend-cache-clobber` and `wreg-gate-retire` (both split out by the s256 ruling as their own rungs) — this row suppresses around the former, does not fix it.

**Routed:** this FINDING · `ARCH-SNOBOL4-RTX.md` §2 (the CLAIMED bullet, already landed) · `GOAL-SNOBOL4-100.md` LIVE CURSOR (below) · `QUEUE.tsv` row `diag-regs-stmt-and-bb` → DONE.
