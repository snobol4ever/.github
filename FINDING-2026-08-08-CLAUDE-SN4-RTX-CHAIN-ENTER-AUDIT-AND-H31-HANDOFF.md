# FINDING-2026-08-08-CLAUDE-SN4-RTX-CHAIN-ENTER-AUDIT-AND-H31-HANDOFF.md

## Session: s_this (2026-08-08) — RTX cursor item (3) + item (1)

### Item (3): `rt_chain_enter` calls at runtime_eval.c:303/308/312/379/412 — CLASS C skip audit

**Question:** Do any of the five direct `rt_chain_enter` calls suffer the same CLASS C bypass that
`eval_chain_enter_only` had (where `bb_glue_outer_γ`'s `mov rsp,rbp; pop rbp; ret` unwinds through
the callee's frame and lands in the caller, skipping the post-call `NV_GET_fn(EVAL_TMP)` read)?

**Answer: NO. None of the five sites suffer the CLASS C bypass. No code change needed.**

**Analysis by site:**

- **Line 379** (`EXPVAL_fn`, DT_E slen==3): already has correct `NV_GET_fn(EVAL_TMP)` save/read/restore
  sandwich around the `rt_chain_enter` call. This was the site the EVAL-RETURN-FIX targeted. ✅ Already correct.

- **Line 412** (`EXPVAL_fn`, DT_C slen==3): executes a `CODE()` object (statement block, not EVAL expression).
  Returns `NULVCL` unconditionally. Caller does not read `EVAL_TMP` after — there is no value to skip.
  Not the CLASS C shape.

- **Lines 303, 308, 312** (`rt_goto_transfer`): GOTO semantics — fire-and-forget transfer to a labeled code
  block via `:(LABEL)`. `rt_chain_enter` is its own self-contained frame (5 pushes, shared landing at `1:`,
  pops, ret). The caller has no post-call `NV_GET_fn` read to skip; `rt_goto_transfer` is void and callers
  discard its return.

**Root cause recap:** The CLASS C issue was structural to `eval_chain_enter_only`: that function's own
`rbp`-based frame was what `bb_glue_outer_γ` (`mov rsp,rbp; pop rbp; ret`) unwound through, landing
PAST the post-call `NV_GET_fn(EVAL_TMP)` in `eval_string_transient`. `rt_chain_enter` itself returns
normally to its own `1:` epilogue — it is not a CLASS C exit point. The five sites use plain `rt_chain_enter`,
which does not create this bypass.

**Verdict:** Item (3) discharged. No regression, no code change.

---

### Item (1): Hand `152_pat_json_keyvalue_renamed` + one-line probe to ζ/ON ladder (s238 directive)

**Action taken:** Created `corpus/probe/bb/probes/H31.sno` + `H31.ref` from `152_pat_json_keyvalue_renamed`.

- Named H31 (extends H-family; last was H30; H = FENCE-class probes)
- Tests `FENCE(str | num | bool)` with conditional-assign capture (`.KVAL`, `.NVAL`)
- SPITBOL oracle: `k=age s= n=42 b=` — FENCE-protected conditional-assign committed
- SCRIP current (HEAD `2ba70058`): rc=139 SIGSEGV, NVAL not captured — same root as X01–X11
- Added to `XFAIL.run` and `XFAIL.compile` as known open defect
- Corpus committed: `09fc07bc`

**Class:** FENCE(ALT) with capture — the first H-family probe exercising both FENCE1-over-ALT structure
AND conditional-assign (.KVAL/.NVAL/.BVAL/.SVAL). Prior H-probes test structural pass/fail without capture.
H31 is the minimal real-world witness (JSON key-value parser) for the MECH H-class ladder's next entry point.

---

### Watermarks re-proved at HEAD `2ba70058`

**RTX watermark (test_crosscheck_snobol4.sh, setarch -R, N=1):**
- m3 **260/57/0** · m4 **240/76/1 SKIP** · DIVERGE **19** ← exact match to cursor. Zero regression.

**ZETA-MECH watermark (corpus/probe/bb/run_suite.sh, setarch -R):**
- m3 **29/112/0** (29 pass · 1 xfail · 112R) — crater baseline confirmed
- m4 **114/25/0** (114 pass · 3 xfail · 25R) — crater baseline confirmed
- (Crater = UCLAIM physical deletion landing; H31 adds one xfail to each baseline)


---

### Post-rebase addendum: CAPGEN-ERAD (parallel seat `83ff2b1d`) cleared H31's SIGSEGV

After rebasing onto `372d4b60`, H31 behavior changed:
- **Before rebase:** rc=139 SIGSEGV — `g_cap_gen` save/restore in MATCH_BEGIN/END caused crash
- **After CAPGEN-ERAD:** rc=0, wrong output — `k=age s= n="age":42 b=` vs oracle `k=age s= n=42 b=`

NVAL now receives the entire remaining subject `"age":42` instead of just `42`. The FENCE(str|num|bool) alternation selection fails: `str` arm attempts `'"' BREAK('"') . SVAL '"'` and loses, but FENCE is not correctly routing the cursor to the `num` arm at the right subject position — the `.NVAL` conditional-assign fires on the wrong slice.

**For MECH H-class:** H31 is now a clean wrong-output failure, not a crash. Monitor-first protocol is directly applicable (no SIGSEGV handler interference). The behavioral failure is the FENCE-over-ALT cursor-position / capture routing bug, distinct from the old crash. H31 remains xfail in both modes.

Watermark post-rebase (`372d4b60`): RTX m3 **265/52/0** · m4 **253/63/1** · DIVERGE **11** · MECH m3 **124/17/0** · m4 **123/16/0**.
