# FINDING 2026-08-08 — AB-0 CENSUS: THE MONITOR TAPS LIVE INSIDE THE C AB-3 DELETES, AND THE ACTIVATION-FRAME ABI IS FOUR FIELDS SHORT

**Session:** 2026-08-08c (Fable). **Rung:** LADDER AB / AB-0 (census + ABI freeze + witnesses). **Code paths changed:** NONE (census rung).
**Repos touched:** corpus (10 witnesses + 8 oracle refs), .github (this FINDING + ladder ABI correction).
**Grounding:** SCRIP `28ef6caf`, corpus `ba057fc4`, artifacts as regen'd at `c1b0ace1`. Oracle: `/home/claude/x64/bin/sbl -b`.

## 1. THE EMISSION PICTURE AT HEAD (what the ladder was opened on)

The DEFINE statement emits an EMPTY statement begin/end skeleton (`demo/roman.s:227` — `n12_statement_begin_α → n13_statement_end_α → n14`). Nothing else. Every mechanism the DEFINE should own is replicated PER CALL SITE (`roman.s n29_call_α:553`, and again at n32/n107/n186/n188/n191…):

`rt_arg_stage` (one C call per arg) · 48B save carve in the CALLER's spine · six movs saving ROMAN/N/UNITS · **`rt_proc_call_open_slim` = a STRING-KEYED `rt_proc_find(name)` on EVERY invocation** · `rt_proc_open_fn` · `lea` the γ/ω wire pair · `jmp rax` · **TWO full inline restore landings** (~12 movs each, `.Lx88_6` γ / `.Lx88_7` ω) · `rt_proc_call_epilogue_slim_γ/ω`.

FIVE C crossings on the hot path of a call SPITBOL makes with zero — the RTX "hot C surface is calls SPITBOL never makes" class, in the call family.

RETURN/FRETURN are IR_SAVE_RESTORE roles 1/2 (`lower_snobol4.c` `sno_build_graph`, `!result_name` arm) emitting `n37/n38_save_restore_α` (`roman.s:742/749`): `call rt_flat_ret_snap` → C peek of the pcall wire record → `mov rcx,[rax+GW|WW]; mov rbp,[rax+24]; mov rsp,[rax+16]; jmp rcx`. NRETURN = `SNO$NRET` builtin + role-1 landing (`lower_snobol4.c:1940/1944`). Entry stub = `sno_build_call_stub` role-3 WIRE-ADOPT (`:1904`). `SCRIP_CALL2BB` (s21x per-SITE two-BB shape) exists default-OFF at `lower_snobol4.c:198` + `emit.cpp:2944/2993`; the ZD-SR note at `emit.cpp:1902` declines role 0 EXPLICITLY because of its CALL2BB arg-window preamble. LADDER AB SUPERSEDES CALL2BB: ownership moves per-SITE → per-DEFINE.

**Wire record offsets read off the emitted code (`rt_flat_wires_t`):** `+0` γ wire · `+8` ω wire · `+16` rsp · `+24` rbp. Confirmed by role-1 reading `[rax+0]` and role-2 reading `[rax+8]`.

**Template emission homes (census by count):** `bb_call_proc_staged.cpp` (13 `rt_proc_open_fn`, 11 `rt_arg_stage`, 5 `open_slim`, 6+6 `epilogue_slim_γ/ω`) · `bb_save_restore.cpp` (4 `open_slim`, 2 `flat_ret_snap`) · `bb_glue_flat.cpp` (3 `flat_ret_snap`) · `xa_flat.cpp` (8 `rt_arg_stage`, `flat_ret_snap`, `rt_lcl_proc_args_install`, `rt_jmp_frame_lexprep`). **⚠ SCOPE WIDENING: `bb_match_capture.cpp` (3), `bb_match_end.cpp` (2), `bb_match_defer.cpp` (2) also call `rt_proc_open_fn`** — the match family enters the proc machinery directly for mid-match calls. These are AB customers; AB-3 must not slim the call site and leave the match-side entries on a different protocol.

## 2. ⛔ THE LADDER-ORDERING FINDING — THE MONITOR TAPS ARE INSIDE THE DELETED C

`mon_emit_call_bin` / `mon_emit_return_bin` (`rt.c:987/992` → `comm_call`/`comm_return`, `core.c:485/504` → `mon_send_bin(MWK_CALL|MWK_RETURN,…)`) are invoked from **exactly the three functions AB-3 removes from the emitted path**:

- `rt_proc_call_open_slim` `rt.c:1238` → `mon_emit_call_bin(p->name)`
- `c_rt_proc_call_epilogue_slim_γ` `rt.c:1251` → `mon_emit_return_bin(c.p->name, result)`
- `c_rt_proc_call_epilogue_slim_ω` `rt.c:1263` → same

Slimming the call site therefore **BLINDS `MWK_CALL`/`MWK_RETURN` in the 2-way/3-way sync-step monitor** — the instrument RULES.md makes mandatory for every divergence hunt, on the very ladder most likely to produce one. Under the MONITOR-FIRST law ("if the monitor is dark for the mode under test, reinstating it comes first") this is a HARD PREREQUISITE, not a cleanup item.

**RESOLUTION (cheap, and it belongs in AB-2, not a separate MON-RE rung):** relocate the taps into the α/β blocks. The per-function block makes the fname a COMPILE-TIME CONSTANT (that is the structural gift of per-DEFINE ownership — the legacy path had to look the name up because the site was generic), so the tap is `lea rdi,[rip+fname_ro]; call mon_emit_call_bin` under a `cmp qword [g_monitor_bin],0; je` guard: TWO instructions on the hot path when the monitor is off, and the event stream is byte-identical when it is on. β additionally sets the discriminator string ('RETURN'/'FRETURN'/'NRETURN') that `comm_return` reads out of `kw_rtntype` — which the β already writes per the design. **AB-2 acceptance gains: monitor event stream on a call witness IDENTICAL pre/post, by diff, both modes.** No separate MON-RE rung needed — but AB-3 MUST NOT land before this.

## 3. ⛔ THE ABI IS FOUR FIELDS SHORT — CORRECTIONS TO THE LADDER'S FRAME

The design of record listed: caller rbp · prev anchor · β addr · γ wire · ω wire · entry rsp · arity/nsave meta · save-set DESCRs. Reading what the legacy C actually saves shows FOUR MORE fields are load-bearing. Frame must additionally carry:

1. **`Σ` (subject base) and `Σlen`** — `open_slim:1233` saves them; both epilogues restore them. A call opened MID-MATCH (deferred `*F()`, capture-with-function) must not lose the enclosing match's subject. **Also open for AB-1:** `driver_call.c:387` (the full path) saves **Σ, Δ, Ω, Σlen** while the slim path saves only Σ/Σlen. Whether the slim path's omission of Δ/Ω is safe-by-construction (the match frame owns the cursor) or a latent defect is UNRESOLVED — AB-1 must decide deliberately and record which, not inherit the asymmetry silently.
2. **`wn` (`rt_g_want_name`)** — captured at open (`:1225`), consumed by `rt_nret_fix(result, wn)` at both epilogues. It is CALLER state (does this context want a NAME or a VALUE) and must be per-activation.
3. **value-trail mark (`vtmark = rt_value_trail_mark()`)** — with `rt_value_trail_tidy_dead_window(vtmark, fb, frame_top)` at both epilogues. GC correctness, not bookkeeping. In the native block the window bounds are exactly the RBP frame (cleaner than the C `__builtin_frame_address(0)+16` form it replaces).
4. **`rt_k_level`** — `++` at open, `--` at both epilogues.

Plus two behaviours the block's α must reproduce that the design credited to the site: **missing formals nulled** for `k = nargs..np` (`:1226`) and **the result cell nulled unless a formal shadows it** (`:1227-1228`).

**`rt_nret_fix` (`rt.c:654`) CONFIRMS the design's NRETURN clause:** if the callee returned by name and the caller did not want a name, the NAME IS DEREFERENCED — and in the emitted order that deref runs AFTER the inline restore movs (`roman.s .Lx88_6` restores, `add rsp,48`, THEN `call …epilogue_slim_γ`). Restore-then-deref is the live semantics; the ladder's "NRETURN name deref is CALLER-side POST-restore" is correct and now oracle-confirmed (§4).

## 4. WITNESS SET — 10 PROGRAMS, ORACLE-BACKED (`corpus/probe/ab_*.sno`, 8 `.ref`)

| Witness | Oracle | What it pins |
|---|---|---|
| `ab_recurse` | `720` / `3628800` | Per-activation save cells. `TMP` is read AFTER the recursive call returns; any STATIC save cell yields wrong products. THE recursion gate. |
| `ab_nret_restore` | `A=written` | **NRETURN name = the CELL, and the caller's store lands POST-restore.** Callee returns `.A` (a formal); A is restored to 'outer' on return; the caller's assign then writes 'written' INTO the restored A. Confirms §3's ordering. |
| `ab_nret_lvalue` | `DUMMY=43` / `DUMMY=AB` | NRETURN as assignment target AND as a pattern capture target (manual p.133). |
| `ab_freturn` | `got=ABC` / failed / `X=` | FRETURN exits the ω wire = statement failure, no value assigned. |
| `ab_argcount` | `[x|]` `[x|y]` `[|]` | Missing args → null, extras ignored (p.212). Arity is compile-time under a literal prototype. |
| `ab_redefine` | `first` / `second-via-alt-entry` | fn_cell REPOINT on re-DEFINE **and** `DEFINE(s,name)` alternate entry (p.219) in one program. Kills any "bind once, jump direct always" shortcut. |
| `ab_goto_out` | see below | **The anchor witness.** |
| `ab_defer_call` | `match OK cnt=1` / `second OK R=C cnt=2` | Call opened MID-MATCH via deferred `*MK()`; match survives and continues, twice. The Σ/Σlen (and Δ/Ω) question of §3.1 is gated HERE. |
| `ab_undef_call` | **ERROR 022 — undefined function called** | The fn_cell init-stub's error. NO `.ref` (dump carries memory stats — not byte-gateable; assert the code, not the text). |

**`ab_goto_out` is the strongest structural result of this rung.** Goto OUT of a function body, then `:(RETURN)` from outside it:
```
in OUT P=arg
at OUTSIDE P=arg LOC=inner-loc     <- activation still PENDING: formals/locals NOT yet restored, outside the body
now returning from outside
after call (not reached)           <- the RETURN LANDED BACK AT THE ORIGINAL CALL SITE
FIN
```
The activation is pending outside the body's lexical extent, and a RETURN from anywhere still finds it and resumes the caller. **This is precisely what the ACT-ANCHOR design predicts and what any lexically-scoped or statically-paired return would get wrong.** It also independently justifies the ladder's "GOTO-OUT-OF-BODY leaves the frame pending — do not 'fix' it" trap: the pending frame is the SEMANTICS. Ruling for AB-2: the floaters resolve the target through the anchor ONLY; the body's lexical extent must never gate the return path.

## 5. NET EFFECT ON THE LADDER

- AB-0 CLOSED. ABI corrected (§3) — the `contracts/` header AB-1 freezes must carry Σ/Σlen(/Δ/Ω verdict), wn, vtmark, k_level, plus the wire quad at the legacy offsets {0,8,16,24} so the dual-arm of AB-2 can read either home.
- **AB-2 absorbs the monitor-tap relocation and gains a monitor-stream-identity gate; AB-3 is BLOCKED behind it.** No separate MON-RE rung.
- AB-1 gains the Δ/Ω deliberate decision + the two α behaviours (null missing formals, null result cell unless shadowed).
- AB-3 gains a scope item: the `bb_match_*` `rt_proc_open_fn` entries (§1) must move onto the block protocol in the same slice as the call sites, or mid-match calls run a second protocol against the same activation stack.
- Positive control for AB-3's "prove the arm fired": the per-call `rt_proc_find` string lookup count on the witness set must go to 0 (POSITIVE-CONTROL LAW: hand-verify one known-good/known-bad before quoting the number).
