# FINDING — a correction, not a cure: seat02's proposed fix location for the `&level` bug
# ("mirror bb_define_activate's enter_env/leave_env pair into bb_define_sr") is almost certainly NOT
# on the code path an ordinary plain-procedure call actually executes. The real call/return boundary
# for this witness is a SEPARATE, cross-language "PL-DC" direct-call trampoline in
# emit.cpp/xa_flat.cpp that bb_define.cpp never touches. Landing the originally-proposed fix would
# very likely have compiled cleanly, changed nothing for this witness, and looked like a fix.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`**, corroborating/correcting
`FINDING-2026-08-29-seat02-icon-level-keyword-not-tracked-for-non-generator-procedures.md` (cited by
`tests/icon/KEEP.md`'s `rung36_jcon_level` bullet as a "two-line-shaped fix").

**Not a cure — this is a characterization correction, same discipline as every other row here: verify
the emitted code before trusting a diagnosis, even a good one.** Nothing committed to SCRIP.

## 0. Why I looked

Picked `&level` as the most precisely-scoped Class-C lead from `tests/icon/KEEP.md` (hq_P's own
guidance this session: spend the next pass on Class C). Before touching `bb_define_sr` as seat02's
FINDING names, read it in full first — CLAUDE.md's own ASM-DIFF-FIRST rule, and seat02's own FINDING
flags an open question ("`bb_define_sr` was not read in full, only grepped for the two symbol names").

## 1. Bug reproduces exactly as documented

Minimal repro (seat02's own, from their FINDING):
```icon
procedure main(); write(&level); p(); write(&level); end
procedure p(); write(&level); end
```
Oracle: `1 2 1`. SCRIP m3 **and** m4: `1 1 1` (SCRIP HEAD `8a0f4f6f`, clean tree). Confirmed independently.

## 2. `bb_define_sr` is not the code path this witness executes

Read `bb_define.cpp` in full (640 lines, not grepped). `bb_define()` dispatches `IR_DEFINE`'s
`op_define_role` into `bb_define_bind` (role 6), `bb_define_activate` (role 7, generator-capable
procedures — the ONE place `rt_k_level` is touched), or `bb_define_sr` (everything else: roles
0/1/2/3/4/5/-1). `bb_define_sr` turns out to hold **four structurally distinct sub-mechanisms**
(SCC/CALL2BB inlined call-site optimization, an empty "wire-adopt" no-op, TINY/SIG shims with
independent γ/ω exit edges, and RETURN/FRETURN/NRETURN floaters) — none of which reference
`rt_k_level`, `kw_fnclevel`, or anything resembling `enter_env`/`leave_env`. Grepped to confirm: zero
hits for any of those names anywhere outside `bb_define_activate`.

**But `p()` in the minimal repro doesn't go through ANY of `bb_define_sr`'s roles at all.** Compiled the
witness (`--compile`) and read the emitted `.s` directly rather than assuming which role applies:

```
FN__p:                        <- the real function body
    sub    rsp, 128
    call   rt_icn_zframe_args_install
p_α_body: ... (keyword read, write() call) ...
p_γ:       add rsp,128 ; jmp [rsp]        <- success exit
p_ω:       add rsp,128 ; jmp [rsp+8]      <- failure exit
p_dcα:                         <- a SEPARATE trampoline, NOT part of FN__p's own body
    pop r12 ; push r12 ; push r12         (retaddr, duplicated)
    lea rcx,[.Lp_α_5_3] ; push rcx        (failure continuation)
    lea rcx,[.Lp_α_5_2] ; push rcx        (success continuation)
    jmp FN__p
```
`main`'s call site is `call p_dcα` — **not** a call into `FN__p` or into anything `bb_define.cpp`
emits. `p_dcα` converts the four-port (α/β/γ/ω) Byrd-box convention into an ordinary call/return shape
for plain call sites, by pushing two continuation addresses the callee's own `jmp [rsp]`/`jmp [rsp+8]`
exits read.

## 3. Where it's actually emitted, and why that raises the stakes rather than lowering them

`grep -rl "rt_icn_zframe_args_install"` (the prologue call in `FN__p`) and the `_dcα` label itself both
point outside `bb_define.cpp` entirely:
- `emit.cpp:3418`: `emit_label_initf(&lbl_dc, "%s_dcα", fam)` — where the trampoline's label is minted.
- `xa_flat.cpp:55` (`xa_flat_dc_stub_str`) — the trampoline's actual instruction sequence (the
  push/lea/jmp chain traced above), explicitly commented `"PL-DC direct-call entry"`.

⚠️ **"PL-DC" reads as Poly-Language Direct-Call, and the surrounding file is NOT Icon-only** —
`xa_flat.cpp` also carries substantial Snocone-specific commentary (`"CLASS-C chain epilogue... s272
snocone-returns-codegen"`) describing the *same* trampoline family serving a different frontend's
return convention. **This means a `&level`-style fix landed here cannot be a blind, unconditional
`rt_k_level` +1/-1** the way `bb_define_activate`'s is — `rt_k_level`/`&level` is an Icon-only concept,
and this call path is shared plumbing. Any real fix needs either an Icon-only guard at the right
emission point, or needs to land inside `FN__p`'s own body (prologue after
`rt_icn_zframe_args_install`, and each of its γ/ω exits) rather than in the shared `_dcα` adapter —
which is *also* more architecturally consistent with where `bb_define_activate` places its own
enter/leave bookkeeping (inside the callee, not at each caller's call site, so it fires no matter how
the callee is reached).

## 4. What this means for the "two-line fix" framing

**It probably isn't two lines, and it probably isn't in `bb_define_sr`.** Seat02's own FINDING was
honest about not having traced this ("two open questions... not chased here") — this session's
tracing answers one of them (does `bb_define_sr` even apply here — no) and opens a new one: which of
potentially several prologue/epilogue emission sites for `FN__p`-shaped bodies (this may not be the
only shape a "plain, ineligible-for-any-fast-path" Icon procedure compiles to) need the same treatment,
and whether the fix belongs at the callee's own boundary (robust to however it's invoked) or would need
duplicating across every call-adapter shape (`_dcα` and potentially others) if placed at the call site
instead.

## 5. Not attempted

No code touched (`git status --short` clean throughout). **Concrete next step for whoever continues:**
locate the OTHER prologue/epilogue emission for `FN__p`-shaped bodies (the code that emits `p_α_body`'s
`sub rsp,128`/`rt_icn_zframe_args_install` and the `p_γ`/`p_ω` `add rsp,...; jmp [...]` pairs — likely
in `emit.cpp` near the `flat_dc_body_p`/`zframe_graph` logic already found, not yet read in full), add
the `rt_k_level` +1 there right after frame setup and -1 at each of `p_γ`/`p_ω`, confirm it's Icon-only
by construction (check whether this emission path is reached for any non-Icon graph), then verify with
a broad Icon board plus SNOBOL4/Snocone control arms (this path is shared with at least Snocone) before
landing — same shared-node discipline as every high-blast-radius change on this project.

## 6. State

SCRIP `8a0f4f6f`, clean tree throughout. Mailing hq_P (this row's co-owner) and seat02 (original
FINDING's author, as a direct courtesy per this project's convention for corrections).
