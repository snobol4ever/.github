# FINDING 2026-08-02f — OMEGA O-1 (ZW-5 slice 2): the statement box is a TRAILER, not a bracket; slice 1's dispatch case was in the wrong dispatcher; and lighting the rung is BLOCKED ON ALPHA

**Session:** s23p, first OMEGA front session. **Parent:** SCRIP `bed9244` (ZW-5 slice 1). **Landed:** mint + driver case + template correction, DORMANT behind `SCRIP_ZW5=1` (opt-IN, see §4 for why the polarity is inverted from the rung text).

---

## 1. OPEN BRACKET (reproven before any edit, per contract §5)

| runner | m3 | m4 |
|---|---|---|
| crosscheck 318, TIMEOUT=8 | **280** PASS / 36 FAIL / 1 TIMEOUT / 1 NOREF | **266** PASS / 48 FAIL / 1 TIMEOUT / 2 LERR / 1 NOREF |

PASS counts reproduce the s23o record EXACTLY (280 · 266) and the LERR pair is present. The fail/timeout split moved (36/1 vs the recorded 27/10) — the container-speed shift RULES predicts, which is why the record is compared BY SET. Pass sets saved.

**Census at `bed9244` (HEAD-stamped, not cited from the goal file's stale figures):** stmt_claim-bearing programs **193** / **377** sites · fused-terminal proxy (`add rsp` adjacent to `jmp main_γ/ω`) **1,064** · rbp-bearing programs **317/318** · claim histogram still carries the 2944–4720 monsters (ZD/ALPHA territory).

## 2. ⭐⭐⭐ THE SHAPE CORRECTION: TRAILER, NOT BRACKET (measured, one line of `x86_asm.h`)

The rung text, the slice-1 template comment, and the `IR.h` kind comment all describe IR_STATEMENT as a BRACKET with an "α→body wire" — a box that opens at α, hands off to the body, and collects the body's return at γ. **That shape is not expressible in this template system, and the proof is two adjacent inlines:**

- `x86_asm.h:544` — `x86_alpha()` → `x86_deflabel(X86P_ALPHA)` — **DEFINES a label**
- `x86_asm.h:547` — `x86_gamma()` → `x86_jmp(X86P_GAMMA)` — **IS A JMP**

So the slice-1 body `def α · <bomb> · jmp γ · def β; jmp ω` has exactly ONE entry and no site control can return INTO. A bracket needs two entries; this box has one.

**The correct shape is the statement's SUCCESS TRAILER:** the body's success wire enters α, falls through to `jmp γ`, and the release rides that jmp's ONE `X86H_JMP` γ hook arm. The box's own γ carries the statement's real continuation (`sT`), so nothing about control flow changes — **the ONLY delta is the release's HOME**, which is precisely WHACK CONTRACT clause 4 (BB_END_STATEMENT is `op_zgpop`'s home; the 5,923 fused pops are its absence). Everything the bracket reading promised, the trailer reading delivers with strictly less machinery and no child-handoff mechanism at all. **The slice-1 bomb is therefore DELETED, not replaced.**

## 3. ⭐⭐ THE MINT IS ONE EDIT, AND THE PLANNER MIGRATES THE STAGING FOR FREE

`lower_snobol4.c:1850-1851` is the ONE derivation point every statement form threads its continuations through — `sT`/`fT` are already resolved there (goto field, computed goto, or fallthrough `next`). One edit reaches every form without touching a single statement arm.

**The staging migration (rung step 4) needs no staging code at all.** Once the box is on the γ spine, `zd_plan`'s run chase (`cur = zd_chase(cur->γ)`) walks INTO it, so the box becomes the run's last member. The last operator's γ target is then IN the run at `k > r` ⇒ `gin=1` ⇒ `zgpop[last_op] = 0` automatically, and the box's own γ leaves the run ⇒ `gin=0` ⇒ `zgpop[box] = zd + kc = K_total`. **The planner does the migration by construction** — which is exactly what "op_zgpop's home BY STAGING" was always supposed to mean, and it honors ZERO-HAND-COUNTED-POPS without a single hand-summed figure.

**FAIL EDGE UNCHANGED IN SLICE 2, and this is not laziness:** the admission gate is "all fail edges arrive at depth 0," and a depth-0 arrival needs no release. Checked before assuming — the wire port selector in `.sz` carries α (`0xce 0xb1`), β (`0xce 0xb2`) and the σ marker read at `emit.cpp:2285`; **there is NO ω-ARRIVAL convention.** Routing fail edges into the box is not a skipped wiring detail, it IS slice 3's per-depth stub ladder, which lands atomically with its planner (s22h).

## 4. ⛔⛔ THE RUNG CANNOT BE LIT BY OMEGA — CROSS-FRONT DEPENDENCY ON ALPHA

**`IR_STATEMENT` is in `zd_k` (slice 0) but is NOT in `zd_wl_kind`.** Under the all-or-nothing run gate a minted box is a first-blocker that declines its ENTIRE statement — every statement in every program falls to the UCLAIM arm.

MEASURED on the playbook's own compliant witness (`probe1.sno`), `SCRIP_ZW5=1` vs off:

| | claims | stmt_claim | m3 result |
|---|---|---|---|
| gate OFF | 5×`sub rsp,16` + 1×48 | 0 | `5` |
| gate ON | 128 / 64 / 48 | **3** | `5` |

and on a 59-program crosscheck sample, m3 **55/59 pass gate-OFF → 51/59 gate-ON, 4 lost with segv.** The model-compliant per-box cells collapse into exactly the legacy claim block Lon keeps seeing. Semantics survive on the witness (both print 5) but the regime is the wrong one and four programs die.

`zd_wl_kind` is **ALPHA's file region** (contract item 1, ADMISSION CLUSTER) and item 9's semantic wall forbids OMEGA changing an admission verdict. **So the whitelist entry is a CROSS-FRONT REQUEST, filed in the OMEGA cursor per contract item 2 — not an edit made here.** This dependency is named nowhere in the O-1 rung text; it is the reason the killswitch ships as `SCRIP_ZW5=1` opt-IN rather than the rung's `=0`-reverts polarity. **Flip the polarity in the same commit that proves the lit rung green at the merged head.**

## 5. ⭐⭐ THE CASE SLICE 1 REPORTED AS LIVE WAS IN THE WRONG DISPATCHER (found by running, not reading)

`SCRIP_ZW5=1` aborted the compile on the FIRST minted box: `FATAL emit_drive: IR op=124 has no template in the universal driver` — **while `case IR_STATEMENT:` plainly exists at `emit.cpp:1000`.** The contradiction resolves via the message's own footnote: there are TWO dispatchers. Slice 1 added the case to `walk_bb_node_inner`'s switch (879–1067, the m4 text walker); `emit_drive` (1214+) is a second switch whose unhandled ops fall to `drive_unowned`. **Added here, shape copied verbatim from `IR_SUCCEED`/`IR_CUT` — which IS the trailer contract** (`jmp γ` + β trampoline to ω).

⛔ **LATENT SECOND SPELLING, flagged not fixed:** `walk_bb_node_inner`'s case does `g_emit.op_zgpop = (int)nd->ival`. That is a second release authority beside the staging choke (the s22k disease that has caused a silent stack skew every time it existed). It is inert ONLY because lower never stamps `ival`. **The new `emit_drive` case deliberately does NOT set `op_zgpop`** — the choke supplies it from the planner. Reconcile `walk_bb_node_inner` to the planner in the lighting commit; do not carry the second spelling forward.

## 6. GATE (dormant landing)

**318/318 `--compile` byte-identical to parent `bed9244` with the gate off**, re-proven AFTER all three edits (md5 manifest diff = 0 differing files). Build green, zero `error:` in the log, `-O0` throughout (no `-O2` directive in session). Crosscheck/bench BY SET re-run is NOT owed for a byte-identical dormant landing and is owed in full at the lighting commit.

## 7. NEXT (for whoever takes O-1 to lit)

1. ALPHA lands `IR_STATEMENT` in `zd_wl_kind` (+ `zd_nops` → 0) — the cross-front request.
2. Reconcile `walk_bb_node_inner`'s `op_zgpop = nd->ival` to the planner (§5).
3. Add the depth-0 admission gate to the mint (today it mints for EVERY statement — that is why 4 sample programs segv; the gate is the cure and is cheap once the whitelist makes the armed regime observable).
4. Flip `SCRIP_ZW5` polarity to `=0`-reverts, full §3 gate set, census proxy pre/post on the 1,064.
