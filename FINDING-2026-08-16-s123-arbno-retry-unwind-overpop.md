# FINDING s123 — THE β-ROUTING FIX IS CORRECT; ITS FOUR BREAKERS ARE AN **ARBNO RETRY-UNWIND OVER-POP**, NOT A SEAL FAILURE

**Measured 2026-08-16 s123 (Claude Opus 5, Lon in-chat "using the MONITOR, take us home").**
**Binary stamped: SCRIP `ce0b6f93`, `scrip` mtime 2026-08-16 21:40:56** (no parallel rebuild during this seat — re-checked at close).
Corpus `9c3aa509`. Oracle `x64` @ `5035571`. gdb 15.1 present and used.

---

## 0. One-paragraph summary

`SCRIP_DEFER_RESUME=1` is the s121 arm that routes a stored-pattern blob's β to its interior
leaf generator instead of to ω. It takes **`probe/arbnostore` from 4 RED to 8/8 GREEN** — R-4(b)'s
stated gate — and its crosscheck cost is **+2 / −4 by set**. s121 attributed the four breakers to
FENCE seals ("seal==1 defers may NEVER be β-targeted"). **That attribution is FALSIFIED here.**
A newly minted FENCE-free witness with the identical control shape crashes identically. The four
breakers are one generic defect: **`n<K>_match_arbno_af` routes to the defer's β to "back out the
previous instance", but that defer's activation frame was already unwound by the fast-path return,
so the whack double-pops and the AF loop walks up the entire frame chain, one caller frame per lap,
until it pops a zero and dereferences `[0-32]`.**

---

## 1. What the MONITOR gave (RULES.md MONITOR-FIRST, step 1)

`bash scripts/test_monitor_2way_spitbol_vs_run.sh corpus/probe/arbnostore/arbno_defer_stored_red.sno`
— the spl↔scr participant pair, **no credential needed** (s122's route confirmed live):

| step | spl | scr |
|---|---|---|
| 5 (last agree) | LABEL stno=3 | LABEL stno=3 |
| **> 6 DIVERGE** | LABEL stno=**4** (`OK`) | LABEL stno=**5** (`NO`) |

Bug is inside statement 3, `'aaa' POS(0) C RPOS(0)`. Independent confirmation of s122 on a
freshly built binary rather than an inherited claim.

Incidental, NOT chased, worth one line for whoever needs it: step 4 shows
`spl VALUE C = UNKNOWN` vs `scr VALUE C = PATTERN` — a monitor value-rendering difference on the
PATTERN datatype, not a divergence in behaviour.

## 2. The dead-end port, re-measured at HEAD (s122's finding, independently reproduced)

```
PAT$0_γ:   push {rbp,r11,r10,→PAT$0_res}    ← suspension machinery WORKS
PAT$0_res: restore r10/r11/rbp; add rsp,32  ← resume WORKS
PAT$0_β:   jmp PAT$0_ω                      ← DEAD END
n0_match_arbno_β: jmp n1_match_defer_α      ← the real retry, 3 insns away, unreachable
```

**THE ONE LINE THAT SPELLS IT** (this is the fact s122 routed toward and did not reach —
record it so nobody greps for it again): `src/emitter/emit.cpp` ~**3105**, the chain's β dispatch:

```c
bb_label_t *resume_tgt = &lbl_ω;                                     /* ← the dead end */
for (i) if (nodes[i]->op == IR_SUSPEND)                resume_tgt = betas[i];   /* Prolog/Icon */
if (body_root) for (i) if (nodes[i]==body_root && op==IR_DISJUNCTION)      resume_tgt = lbls[i];
if (body_root) for (i) if (nodes[i]==body_root && op==IR_CALL_BUILTIN_GEN) resume_tgt = betas[i];
/* [SCRIP_DEFER_RESUME=1 only] leaf-generator arm, declined if any IR_MATCH_FENCE1 node: */
if (_dres && flat_pat && body_root) if (!_f1)
    for (i) if (nodes[i]==body_root && op in {ARBNO,ARB,BAL})               resume_tgt = betas[i];
emit_jmp_label(resume_tgt, JMP_JMP);
```

For a SNOBOL4 blob at default **no arm fires**, so β falls to ω. That is the entire dead end.

## 3. Measurements (this seat, live binary)

**`probe/arbnostore` (5-run verdicts, m3):** default **4 RED / 4 GREEN**; `SCRIP_DEFER_RESUME=1`
**8/8 GREEN**. The R-4(b) gate is met by code already in the tree.

**Crosscheck A/B, DIVERGE 0 in BOTH arms:**

| arm | m3 | m4 |
|---|---|---|
| `SCRIP_DEFER_RESUME=0` | PASS=299 FAIL=18 | PASS=298 FAIL=18 SKIP=1 |
| `SCRIP_DEFER_RESUME=1` | PASS=297 FAIL=20 | PASS=296 FAIL=20 SKIP=1 |

**By set — the only honest reading:**
- **FIXED (+2):** `139_pat_calc_paren_deep`, `143_pat_regex_quantified_class`
- **BROKEN (−4):** `119_pat_arbno_of_fence_via_var_via_outer`, `129_pat_arbno_star_var_fence_with_alts`,
  `148_pat_arbno_star_var_fence_short`, `149_pat_arbno_star_var_fence_outer_pre_match`

s121's decision to ship default-OFF is **re-validated**. What is overturned is the *reason*.

## 4. ⛔⛔ RETRACTION — "seal==1 defers may NEVER be β-targeted" IS NOT THE MECHANISM

All four breakers are spelled `..._fence_...`, which made the seal the obvious suspect and made
R-4(h) (FENCE0→BB) look like the prerequisite. **The discriminating control was never run. It is
run here.**

**NEW WITNESS: `corpus/probe/arbnostore/arbno_defer_altarg_red.sno`** — the same control shape with
**no FENCE anywhere**:

```
        cmd   = ('a' | 'ab')
        outer = ARBNO(*cmd)
        s     = 'ab'
        s POS(0) *outer RPOS(0)      :S(BAD)F(GOOD)
```

| arm | result |
|---|---|
| oracle `sbl -b` | `match` |
| SCRIP default | `nomatch` — **silent wrong answer** (the beauty class) |
| SCRIP `SCRIP_DEFER_RESUME=1` | **rc=139 SIGSEGV — identical crash to all four fence witnesses** |

**FENCE is incidental.** The four breakers are fence-shaped only because those are the witnesses
that happened to exist in the suite. Do NOT spend a rung widening the seal decline to see FENCE0
metadata — that was this seat's own first hypothesis and it is wrong.

## 5. The mechanism, from gdb (RULES.md steps 2–3)

`w148` built m4, `SCRIP_NO_SEGV_HANDLER=1`, breakpoints on every port of the ARBNO blob:

```
GAMMA    rbp=e8e8  r14=0      suspend, shy null match
RES      → ARBNO_B rbp=e8e8   β routes into the ARBNO  ✓
DEFER_A  rbp=e8b8  r14=0      fresh instance of *cmd
ARBNO_AS rbp=e8e8  r14=1      cmd matched 'a', cursor 1  ✓
GAMMA / RES / ARBNO_B / DEFER_A  r14=1   second retry: fresh cmd at cursor 1 → FAILS
ARBNO_AF rbp=e8e8  → DEFER_B pops → rbp=e938   ← CALLER's frame
ARBNO_AF rbp=e938  → DEFER_B pops → rbp=ea00
ARBNO_AF rbp=ea00  → DEFER_B pops → rbp=ea60
ARBNO_AF rbp=ea60  → DEFER_B pops → rbp=0
ARBNO_AF rbp=0     → mov -0x20(%rbp),%eax → SIGSEGV
```

Faulting instruction `n9_match_arbno_af`: `mov -0x20(%rbp),%eax` with **rbp=0**.

**The defect:** the failing fresh instance already returned through the fast-path glue
`pop rbp; jmp n<K>_match_arbno_af`, which restored rbp to the blob frame. `af` then reads its
start-cursor slot, sees `cursor != start`, and concludes "an instance is still placed, back it
out" → `jne n<K+1>_match_defer_β`. But `defer_β` is written as *unwind MY OWN activation*
(`mov rsp,rbp; pop rbp`), and that activation is already gone — so it eats the **blob's** saved
caller-rbp. Each lap climbs one more frame. This is latent at default because β never routes into
the ARBNO at all.

## 6. What the fix actually is — and the clean split it produces

Backing out instance-by-instance only exists to reach a **previous instance's internal choice
points**. Two cases, and they part company cleanly:

- **Sealed argument (119/129/148/149):** `FENCE(P)` makes alternatives inside P invisible on backup
  (manual p.127; p.204 restates it for the bare primitive). The previous instance therefore has
  **no** reachable alternatives, so ARBNO must simply report exhaustion: **`af` should go straight
  to ω, never to `defer_β`.** ARBNO grows monotonically on retry (manual p.121: `"" | PAT | PAT PAT
  | …`) and never shrinks, so nothing is lost. **This is fixable at the port emission now, and it is
  the whole −4.**
- **Unsealed argument (`arbno_defer_altarg_red`):** the oracle's `match` genuinely requires
  re-entering the placed instance and taking its second alternative. That state is not retained
  today — every instance returns fully unwound. This needs **per-instance retained choice points =
  R-4(a), the dynamic-K ARBNO ACTIVATION FRAME**, exactly as the goal file already scopes it. This
  probe is the witness R-4(a) never had.

**So the ordering flips:** R-4(h) (FENCE0→BB) is **not** the prerequisite for landing the β route.
The `af`→ω-under-seal correction is, and it is smaller.

## 7. NEXT RUNG (precise, gated)

1. In the ARBNO af emission, when the ARBNO's body element is a right-sealed defer (`op_seal == 1`),
   emit the exhaust edge to **ω** rather than `jne <defer_β>`. Start from `src/templates/bb_match_arbno.cpp`
   (note: the `_TAIL` element-scheme arm at ~:163 is a DIFFERENT template from the simple
   `α/β/as/af` shape these witnesses emit — confirm which arm emits your witness by asm diff first).
2. Re-run the A/B. **Expected: −4 → 0, so the arm goes +2 net and `SCRIP_DEFER_RESUME` can default ON**
   (killswitch INVERTED, not deleted, per R-7).
3. GATES: `probe/arbnostore` 8/8 (now 9 files with the new witness — expect `arbno_defer_altarg_red`
   to stay RED until R-4(a); mark it so, do not let it block) · crosscheck ≥ 301/16 m3 with DIVERGE 0 ·
   `dv/` + `mrbp/` unmoved · md5 blast radius BY SET (shape change ⇒ killswitch byte-identity N/A) ·
   then re-measure beauty both modes.
4. ⛔ **Beauty will still not move on this rung alone, and the structural reason is now known:**
   `Parse = nPush() ARBNO(*Command) (…) nPop()` has `body_root` = the SEQ chain, **not** a bare
   generator, so the `nodes[i] == body_root` test can never fire for beauty **however the carrier set
   is widened**. Beauty needs the **leftward seam walk** — route β to the *rightmost interior choice
   point*, which is just Ch.18 step 6 ("pop the stack to get a previous alternative") stated
   generically instead of per-shape. That is the rung after this one.

## 8. Operational notes earned this seat

- `test_monitor_2way_spitbol_vs_run.sh` needs **no credential** and works today. `..._sync_step_bin.sh`
  still hard-requires token-gated `csnobol4`.
- **gdb 15.1 IS present** after `install_system_packages.sh`. Hit-counted breakpoints with `commands`
  blocks printing `$rbp/$rsp/$r14` at each port is the cheapest possible instrument for this class —
  the whole frame-chain walk fell out of one 20-line gdb script. HW watchpoints still unavailable.
- The container went intermittently unresponsive mid-session (commands failing, then `echo` working,
  then failing again) and recovered with the build intact. Re-`stat` the binary after any such gap
  before trusting a verdict.
