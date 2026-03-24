> Org renamed SNOBOL4-plus → snobol4ever, repos renamed March 2026. Historical entries use old names.

# SESSIONS_ARCHIVE.md — Append-only session log

**Format:** One `## SessionID — Description ✅/❌ (date)` block per session.
Oldest sessions pruned for context economy. Full git history is the permanent record.

---

## IJ-6 — Icon JVM — 2026-03-24

**HEAD in:** `e590c4f` IJ-5 | **HEAD out:** `a3d4a55` IJ-6

**Fix 1 ✅** `ij_emit_proc`: `lconst_0/lstore N` preamble for all `ij_nlocals` slots before `suspend_id` dispatch → `Register pair 2/3 wrong type` dead.
**Fix 2 ✅** `ij_emit_suspend` body γ: route through `icn_N_bdone: pop2; goto ports.γ` drain — body assignments leave long on stack.
**Fix 2b ✅** `ij_emit_suspend` body ω: `strncpy(bp.ω, ports.γ)` — failure path has empty stack, must NOT go through pop2.
**Fix 3 ✅** `ij_emit_proc` stmt chain: each stmt γ → `icn_sN_sdrain: pop2; goto next_a` — prevents stale long entering next stmt's α.

**All VerifyErrors dead. Class loads and exits 0.**

**Remaining for IJ-7:** no-output bug — `icn_upto()` returns `icn_failed=1` immediately. Debug: `javap -c icn_upto`, check `i := 1` stores to slot 2, `1 <= 4` compares lload 2 vs lload 0. Verify `sdrain` routes to while-condition α, not `icn_upto_done`.

---

## PJ-8 — Prolog JVM — 2026-03-24

**HEAD:** `d36f0ed` snobol4x main

**Fixed:** rung02 infinite loop. Root cause: `base[nclauses]` uninitialized in `pj_emit_choice()`.

**Fix:** `base[nclauses] = base[nclauses-1] + 1`. Omega guard emitted only when last clause has no body user-calls.

**Corpus:** rung01 ✅ rung02 ✅ rung03 ✅ rung04 ✅ rung05 ✅ rung06 ❌

**rung06:** `append/3` compound head `[H|R]` — `pj_emit_unify_expr` for `E_COMPOUND` mishandles fresh output vars in head unification.

**Next:** PJ-9 — diagnose rung06, then M-PJ-LISTS.

---

## PJ-7 — Prolog JVM — 2026-03-24

**HEAD:** `c6a8bda` · **Branch:** `main`

**Completed:** M-PJ-BACKTRACK ✅ — rung05 `member/2` outputs `a\nb\nc\n` correctly.

**Fix:** γ formula changed from `base[ci] + sub_cs_out + 1` to `base[ci] + init_cs + 1`. Greek naming throughout `prolog_emit_jvm.c`; Jasmin labels use ASCII spellings.

**Corpus:** rung01 ✅ rung02 ❌ (pre-existing) rung03 ✅ rung04 ✅ rung05 ✅

---

## B-276 — M-BEAUTY-OMEGA ✅ — 2026-03-24

Binary `E_ATP` in value context emitted wrong OPSYN dispatch. Fixed `expr_has_pattern_fn` + `expr_is_pattern_expr`. 106/106 ✅.

**Commits:** snobol4x `151a99b` · .github `468c507`

---

## N-248 — M-T2-NET ✅ M-T2-FULL ✅ — 2026-03-22

`net-t2` branch. 110/110 ALL PASS. CLR stack-frame isolation makes NET T2-correct by construction.

**Commit:** `425921a`

---

*(Entries before N-248 pruned 2026-03-24. Full history in git log.)*
