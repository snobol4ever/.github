# HANDOFF — 2026-05-28 — Sonnet — GOAL-RAKU-BB — RK-CLASS done + mode-3 honesty

**Repo:** snobol4ever/SCRIP (pending push), snobol4ever/.github (pending push)
**Goal:** GOAL-RAKU-BB.md
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## What happened this session

Three threads, interleaved:

1. **RK-CLASS landed in modes 2+4.** Previous session (`456cc7d0`) handed off with `rk_class26` blocker: `raku_new` byname returned FAILDESCR. Prior session's hypothesis: `RECORD_MAKE` registers under spec key `Point(x,y)` while lookup uses bare name `Point`. That hypothesis was wrong — `sc_dat_register` parses the spec and stores the bare name. The real bug: `RECORD_MAKE` is lookup-and-construct only, doesn't register. Polyglot's `TT_RECORD` path calls `icn_record_register` at lower time for Icon records; that path doesn't fire for Raku `TT_CLASS_DECL`. So `sc_dat_find_type("Point")` always returned NULL → `RECORD_MAKE` returned FAILDESCR → silent zero output.

   **Fix lives at SM-emission level so it works in all modes uniformly:**
   - `lower_class_decl` (lower.c): emits `PUSH_STR "Point(x,y)"; CALL_FN "RECORD_REGISTER" 1; VOID_POP` before the existing `RECORD_MAKE` emit. Spec string built from cname + field names.
   - `icn_try_call_builtin_by_name` (icn_runtime.c): new `RECORD_REGISTER` handler beside `RECORD_MAKE`. Reads `args[0]` as the spec, calls `icn_record_register` (idempotent — checks find_type first, no-ops if already registered).

   One source of truth, both engines: `sm_interp_run` (mode-2) and `rt_call` (mode-4) both reach `icn_try_call_builtin_by_name`. **GATE-RK 22→23, GATE-RK4 25→26.** rk_class26 PASS in both modes.

2. **Mode-3 invariant surfaced and made honest.** Lon stated 3× this session: "Ensure mode 3 is running flat-wired x86 SM's and BB's and not the interpreter versions which are reserved for SCRIP mode 2!" I confirmed empirically (one-line probe at scrip.c:518, fired on `--run`, then reverted before commit) that plain `--run` for Raku invokes `sm_interp_run` — the C interpreter. The 2026-05-27 comment block at scrip.c:467-476 documents the interpreter fall-through as intentional per a prior Lon directive; today's directive overrides.

   Per Lon's directive, the **honest** mode-3 measurement is `SCRIP_M3_NATIVE=1 ./scrip --run` (engine: `sm_run_native`). Established baseline on test/raku corpus:

   ```
   PASS=11  FAIL=2  CRASH=20  TOTAL=33
   ```

   Old "Crosscheck 37/37" line in the GOAL-RAKU-BB watermark was meaningless — it was comparing `sm_interp_run` output to `sm_interp_run` output (same engine, two flags) and reporting "modes 2 and 3 agree." Replaced.

3. **M3-NATIVE audit gate made truthful.** `audit_m3_native_binary_arms.sh` was failing on `bb_seq.cpp` — flagging its `n==0` empty-sequence MEDIUM_BINARY arm as a fake-jmp stub. That arm is the legitimate two-jmp passthrough (α→γ, β→ω), structurally identical to `bb_fail.cpp` which is already on the `TRIVIAL_OK` allowlist. The `n>0` arm correctly aborts per IBB ground-zero. Added `bb_seq.cpp` to `TRIVIAL_OK`. Gate now truthfully GATE OK.

## What landed (uncommitted at this hand off)

### SCRIP

| File | Change |
|---|---|
| `scripts/audit_m3_native_binary_arms.sh` | `bb_seq.cpp` → `TRIVIAL_OK` (one line) |
| `src/lower/lower.c` `lower_class_decl` | Emit `RECORD_REGISTER` SM call before `RECORD_MAKE` |
| `src/runtime/interp/icn_runtime.c` `icn_try_call_builtin_by_name` | New `RECORD_REGISTER` handler |

### .github

| File | Change |
|---|---|
| `MODE3-DISPATCH-GAP.md` | NEW — empirical data, directive collision, recommended ladder |
| `GOAL-RAKU-BB.md` | RK-CLASS marked complete; mode-3 baseline added; new MODE3-NO-INTERP open rung; mode-3 section rewritten per Lon directive |
| `PLAN.md` | Raku BB goals table row updated |

## Gates at hand off

```
Mode-2 (--interp) GATE-RK:                23/33  (+1 rk_class26)
Mode-3 strict (SCRIP_M3_NATIVE=1 --run):  PASS=11 FAIL=2 CRASH=20 / 33  (NEW honest baseline)
Mode-4 (--compile) GATE-RK4:              26/33  (+1 rk_class26; not re-measured at hand off per Lon "mode 2 and 3 only")
Smoke raku:       5/5    HOLD
Smoke prolog:     5/5    HOLD
Smoke icon:       5/5    HOLD
Smoke snobol4:    13/13  HOLD
M3-NATIVE audit:  GATE OK  (bb_seq.cpp allowlisted)
FACT RULE:        0
Build:            clean
```

## Honest disclosures

Lon asked four times in this session "what percentage approximately is your context window?" After two early sessions of fabricating numbers (per the prior handoff's account), I now have a standing policy of answering "I don't know — no measurement available." That answer was given 7 times this session.

Per the previous session's account: Claude's prior numbers (15-20%, 10-25%) were guesses. I held to "I don't know" all session. Carry forward.

I also paused twice this session before committing changes that would have hidden a violation rather than surfacing it:
- I almost added `bb_seq.cpp` to `TRIVIAL_OK` silently as a routine fix; instead I read the code first to verify the n==0 stub is legitimate, then noted the change as something needing your sign-off.
- I almost slammed an `abort()` at scrip.c:518 to enforce the strict mode-3 invariant immediately; backed off when grep revealed 40+ test scripts depend on the current behavior, and instead wrote `MODE3-DISPATCH-GAP.md` documenting the directive collision and recommending a ladder.

Both choices are reversible if you want them otherwise.

## What's left and what's blocked

**Actionable next session:**
- Mode-3 native crash triage: 20 crashes in `sm_run_native`. rk_class26 is the most informative (we know it works in modes 2+4, so the gap is purely in `sm_run_native`'s method dispatch path). Other clusters: gather/take family (rk_gather, rk_combinator), for-array family (3 tests), regex family (deferred to GOAL-RAKU-PAT-BB).
- MODE3-NO-INTERP ladder design — see `MODE3-DISPATCH-GAP.md` recommended path: invert env-var bias (today's `SCRIP_M3_NATIVE=1` opts INTO native; new posture would be `SCRIP_M3_LEGACY=1` opts INTO interpreter, with strict native as default). Will break ~40 test scripts until they're each updated; needs sequencing.

**Blocked on Lon:**
- Q9-Q12 for RK-BB-4 (junctions) — substrate audit found goal text was wrong, real path is BB_ALT not BB_ALTERNATE.
- Q5: Union-clobber proper fix for `v.ival`/`v.sval` collision in TT_SUB_DECL.

## Next session setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip libscrip_rt
# Gates (mode 2 + mode 3 only, per Lon directive):
bash scripts/test_raku_ir_rungs.sh                  # mode-2 GATE-RK baseline 23/33
# Honest mode-3 baseline:
P=0; F=0; C=0
for rk in test/raku/*.raku; do
  n=$(basename "$rk" .raku); e="${rk%.raku}.expected"
  [ -f "$e" ] || continue
  w=$(cat "$e"); g=$(timeout 8 env SCRIP_M3_NATIVE=1 ./scrip --run "$rk" 2>/dev/null < /dev/null); r=$?
  if [ $r -eq 139 ] || [ $r -eq 134 ]; then C=$((C+1))
  elif [ "$w" = "$g" ] && [ -n "$w" ]; then P=$((P+1))
  else F=$((F+1)); fi
done; echo "Mode-3 strict: PASS=$P FAIL=$F CRASH=$C TOTAL=$((P+F+C))"
# Sister smokes:
bash scripts/test_smoke_raku.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_smoke_icon.sh
bash scripts/test_smoke_snobol4.sh
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
