# HANDOFF — 2026-06-10 — BB-FIXUP 39th attended run (Fable 5) — CV7 FINAL: ro_seal abolished from x86()

**Run shape:** Lon-DIRECTED bb_alt.cpp second redo, out-of-cursor; **cursor UNMOVED at `bb_assign_frame.cpp`**. Lon attending, context % each turn; opened ~25%, hand off at ~55%.

## The ruling (Lon, verbatim)
"Remove the invalid 'ro_seal_q' and 'ro_seal_str' instruction passed to x86 function. Make a CONVERSION specification that only VALID x86/x64 assembly instructions are ALLOWED as 1st parameter of x86 function."

This RESOLVES the 38th-run outstanding verdict "ro_seal_q/ro_seal_str CV7 directive-naming". **CV7 rewritten to its FINAL form** in GOAL-BB-FIXUP.md CONVERSIONS this commit.

## Landed — SCRIP 5647da8 (on origin)
- `ro_seal_q`/`ro_seal_str` dispatch mnemonics DELETED from `x86()` in x86_asm.h. Zero `x86("ro_seal` anywhere in src/.
- The RO seal decomposes to its real per-line assembly spellings:
  - quad seal: `x86("def", L(n)) + x86(".quad", val)`
  - string seal: `x86("def", L(n)) + x86(".quad", LS(n), lit) + x86("label", LS(n)) + x86(".string", lit)`
- NEW dispatch arms (medium switch inside x86_asm.h, per the ONE-MEDIUM rule):
  - `.quad` imm form: BINARY `x86_Lrec(u64le(xa.u))` / TEXT ` .quad N`
  - `.quad` (sym, str) form: BINARY bakes the lit POINTER `Lrec(u64le(ptr))` / TEXT prints the sym ` .quad .LxU_n_s`
  - `.string`: BINARY EMPTY (the string lives in process memory via the baked pointer) / TEXT ` .string "escaped"` via x86_asm_str_escape
- `LS(n)` helper added beside `x86_internal_name` (returns `.LxU_n` + `_s`).
- Call sites converted: `bb_alt.cpp` (both FOR-lambda arms — the directed redo), `bb_det_write.cpp` atom arm, `bb_det_is.cpp` rop + bop arms.

### Design calls stated for veto (none vetoed live)
1. `.quad`/`.string` qualify as valid assembly: they are the operation field VERBATIM in the emitted .s — same precedent as CV7's `ro_load_q → x86("mov", reg, ROQ(n))`.
2. `x86_ro_seal_q`/`x86_ro_seal_str` FREE FUNCTIONS remain inside x86_asm.h as byte-producers. 19 template files still call them directly — those are CV4 bypass hits converting to the CV7 decomposition at their ring stops (bb_scan_*, bb_var*, bb_gvar_assign*, bb_cell_*, bb_call, bb_lit_scalar, …).
3. Meta-forms `label`/`comment`/`def` stand as assembly SOURCE ELEMENTS (label-definition lines, comment lines), not invented op names — absent a further Lon ruling.

### Proof
- Normalized asm-diff EMPTY ×4 probes; LIVE coverage: alt int-seal (every write(1|2|3)), alt str-seal ×3 (every write("aa"|"bb")), det_write str-seal ×2 (write(hello)…write(X)).
- bb_det_is rop/bop arms driver-unreachable on probed shapes (const-folds; user-predicate `Z is X+Y` routes elsewhere — the `.S0` .rodata driver seal, see double-convention note) → string-identity by construction per the XK_SYM standard; the NEW encoder arms themselves are LIVE-covered via the other three sites in both media.
- Behavior A/B: m2/m3 identical ×8; m4-run ×3 — BOTH the pre-edit A .s and post-edit B .s assembled vs libscrip_rt and run: `1 2 3` / `aa bb` / `hello 42 foo`.
- Gates at floors every certification (×3: pre-push, post-a875c77 rebase, combined-head): icon m2 12/12 HARD m3=m4 10/12 · prolog m2 5/5 HARD m3=m4 5/5 · pat M4 19/0 (053 pre-existing) · prove_lower 68P rc=0 · purity 2 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 103 · sno_pat_reg HARD · hello-langs rebus ROW-DRIFT pre-existing (stash A/B identical — 38th-run flag stands).

## ⛔ Session-env note (EXTENDED — put in every fresh session)
`build_scrip.sh` does NOT build `out/libscrip_rt.so`. Icon/prolog m4 smokes read **0/12 and 0/5** until it exists. Fresh-session steps:
```bash
apt-get install -y libgc-dev
bash scripts/build_scrip.sh
make libscrip_rt
```

## Concurrents
- **a875c77** (icon-NL rung 3: scrip_ir.c + lower_icon_nl.c, template-neutral) absorbed mid-run via rebase; rebuilt, full battery re-certified, probes re-diffed EMPTY ×3 (8th-run precedent).
- ⛔⛔ **c3b1dbb (ICON-NL DEFAULT FLIP, idle-window)** — combined-head sanity FOUND A REGRESSION the flip's own gates missed: under NL=1 (the new default), `every write(1|2|3)` and `every write("aa"|"bb")` are **SILENT-EMPTY rc=0 in m2 AND m3**, and m4 emits ZERO seals, routing to the `rt_call_builtin` stack-removed ABORT — **bb_alt is driver-unreachable under lower_icon_nl** (alternation-in-every channel unwired). All three modes CORRECT under `SCRIP_NL=0`; my probe .s under NL=0 is byte-identical to the pre-edit baseline (diff 0 ×2) — **my work intact; the regression is c3b1dbb's. Owner: ICON-NL.** Gate-gap note for ICON-NL: the icon smoke set has no alternation-in-every shape, which is how the flip certified green.

## Lon verdicts outstanding
Standing 6: x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (owner PL-GZ) · m2 disj-backtrack silent-empty (owner PROLOG-BB) · IRD-2b IR_t.own ratify · ml comment-substring false-positive. Plus: counter-scope trio (lv/rp/nw vs sanctioned forms) · bb_arith dead-dispatch retirement · ceiling-ratify 2488 · **NEW: c3b1dbb alternation-in-every regression (owner ICON-NL)** · **NEW: TWO-CHUNK design question** (below). RESOLVED this run: ro_seal CV7 directive-naming.

## Two-chunk design discussion (Lon question; recommendation recorded, awaiting Lon's word)
Q: should `bb_*_str` return TWO strings — executable code vs data?
- Writable BB local storage is NEVER emitted (Lon's read confirmed): it is offsets baked into instructions; the r12 frame is allocated at runtime.
- RO seals are the only second-kind output; today they trail the box past the unconditional `jmp γ / def β / jmp ω` tail (the SEALED-adjacent FACT RULE). `[rip+disp32]` reaches ±2GB so adjacency is a mode-3 bb_pool RELOCATABILITY concern, not speed; side-by-side mildly costs L1i/L1d line sharing vs `.rodata`.
- DOUBLE CONVENTION exists today: driver-side `.section .rodata` `.S0:` seals (seen in prolog var-arith .s) vs box-adjacent `.Lx` seals.
- RECOMMENDATION: NO two-string template interface. If separation is wanted, the seam is the `.quad`/`.string`/seal-`def` arms accumulating into a second g_emit buffer, with emit_core owning PLACEMENT (per-box trailing for mode-3 blobs; pooled .rodata tail for mode-4). Zero template churn; CV9 parameterless single-return interface stays. Execute only on a concrete need (seal dedup, pool layout, or unifying the double convention).

## Next session
Cursor stop `bb_assign_frame.cpp` (TOTAL=66: bp=17 rp=27 hc=13 mt=1 sd=3 cl=4 ml=1) — the CV4/CV8/CV9/CV10 showcase per the 38th-run arrival note; its 17 x86_frame/reg bypass calls now also include x86_ro-class CV7 conversions where seals appear. SCRIP @ 5647da8 on origin (c3b1dbb above it, foreign, regression flagged) · .github @ this commit.
