# HANDOFF — 2026-06-13 — BB-FIXUP 73rd run (Opus 4.8) — bb_call.cpp write-family de-walk (entered the FIX-3 monster)

## TL;DR
One pin-free ring stop landed, byte-identical, on the cursor file (the FIX-3 monster):
- `bb_call.cpp` **324 → 309** (−15) — **SCRIP `242e1d0`** (rebased from `b52b9ff`).
- This is **FIX-3-i's EMIT-BLIND goal** (de-walk the write family) achieved via a **CV10 prep-relocation**, NOT the ladder's lower-split (which is unsound here — see finding below).

GRAND 1192 → 1177 (mine) → **1163** (concurrent `9480185` −14). 75 dirty / 53 clean. All floors green pre+post, re-certified on combined head. **No LADDER rungs closed; cursor STAYS `bb_call.cpp`** (FIX-3-iii pins the bulk).

## State
- SCRIP HEAD **`242e1d0`** (verified on origin). Clean tree.
- `.github` — 73rd-run watermark in `GOAL-BB-FIXUP-A-to-Z.md` + this doc.
- `# CURSOR: bb_call.cpp` (unchanged — FIX-3-iii blocked).
- Workspace: SCRIP + corpus + x64 all cloned at `/home/claude/`. Clone all three every session that runs C2 probes / corpus gates.

## Session open
SCRIP @ `a6e0a18`; `git pull --rebase` → `d2d307c`, absorbing 2 concurrents off the 72nd-run close (neither touches bb_call): `966bb35` (POWER_fn int**non-neg-int → INTEGER, 027 parity) · `d2d307c` (&-keyword reads via rt_keyword_read in M3/M4). Full baseline battery GREEN; GRAND 1192 / 76 dirty / 52 clean confirmed (ceiling intact — the 2 concurrents were runtime/emit, not template violations).

## The stop — bb_call.cpp 324→309 (SCRIP 242e1d0)
3-file edit: `bb_call.cpp` + `emit_bb.c` + `emit_globals.h`.

**What it does:** relocates the write-family dispatch decision out of the `bb_call` template (CV10 — templates must not inspect the IR graph) into `emit_bb.c` prep, delivered via a new `int op_write_route` field in `sm_emit_t`.

**⛔ DESIGN FINDING (stated, vetoable — this CORRECTS FIX-3-i's recipe):**
The ladder's FIX-3-i says "lower_icon.c emits the shape-kind (slotted-value→WRITE_SLOT…)". That is **unsound for the live arm.** The write_slot discriminator is `bb_slot_get(a0) >= 0` — an **emit-time** fact: the write arg's frame slot is allocated when the arg's own box emits (or by `flat_drive_call_intexpr`) during emit, *not* at lowering. LOWER cannot soundly predict it. The correct, sanctioned mechanism is the **CV10 prep-relocation** (the 38th/40th-run class note: "a `bb_prepare` relocation, not a LOWER split"). So FIX-3-i's de-walk goal is met without any enum/lower-split.

**Implementation:**
- `emit_globals.h`: `int op_write_route;` added to `sm_emit_t` (beside `op_call_fp`).
- `emit_bb.c`: `static int bb_call_write_route(IR_t *nd)` (placed before `walk_bb_flat`) transcribes the `bb_call.cpp` 554-580 routing **order-exactly**:
  - `0` = not a peeled write (not `write` / not nargs==1, OR write that falls through) → normal dispatch
  - `1` = SLOT (`g_descr_flat_chain && bb_slot_get(a0)>=0`)
  - `2`/`3` = BINOP concat / int (`is_write_intexpr && a0∈{BINOP,TO,TO_BY}`, concat iff `BINOP && ival==BINOP_CONCAT`)
  - `4` = LEGACY (`is_write_intexpr`, other shapes — the bomb)
  - `5` = STRLIT-empty (`a0==IR_LIT_S` no-slot — returns `std::string()`)
  - called at the **top** of `case IR_CALL` (`g_emit.op_write_route = bb_call_write_route(nd);`). Timing is byte-identical: the slotted arg box emits before the write box, so its slot already exists by the time write's prep runs; the non-descr binop/legacy route needs no slot.
- `bb_call.cpp`: the `is_write_strlit`/`is_write_intexpr`/`arg_is_any`/`arg_is_ro_binop` derivation + the `bb_slot_get` slot fast-path (old 554-580) are **replaced by a `switch (_.op_write_route)`**; `is_userproc`/`is_builtin` are inlined into `if` conditions (their `&& !is_write_*` exclusions are now moot — write nargs==1 returns early via the route; multi-arg write / `writes` / non-write fall through to userproc/builtin/FATAL unchanged). **The dval arms (542-549) and rk_bool (550-553) are UNTOUCHED** (FIX-3-iii).

**Empirical de-risk (no source change — compile probes):** probed every write-arg shape →
- `write(int/str/binop/concat/float/1 to 3)` nargs==1 → **all** `rt_write_any_nl` (SLOT route 1)
- `write()` / `write(1,2)` / `writes("x")` → `rt_call_arr` (bb_call_fn, route 0)
So `bb_call_write_binop` (`rt_write_int_nl`/`rt_write_strz_nl`) and `bb_call_write_legacy` (explicit bomb) are **corpus-DEAD**; their only callers are inside `bb_call.cpp`. Those arms are byte-identical **by construction only** (not corpus-exercisable) — flagged.

**C2 proof:** git-stash baseline vs new, `--compile --target=x86`, normalized (`bbN_`/`.LcallN`/`.SN`/`.LpbN`/`.LxN`) A/B diff **EXACTLY EMPTY ×10 probes** (6 SLOT shapes + multi/writes/none + a builtin-call route-0). Behavior **m2=m3=m4 parity** across all. bb_call.cpp counters: `nw 20→11`, `lv 92→85`, `rp 67→68` (+1 = the explicit switch arms; within-file, TOTAL still dropped 15).

## Gate floors (held pre+post, re-certified on combined head 242e1d0)
sno m4 7/7 HARD · pat M2 19 M4 19/0 · icon m2 12/12 HARD m3=m4 10/2 · prolog 5/5 ×3 (the GZ-ONLY pivot held) · prove_lower 0P+0F rc=0 VACUOUS · purity 1 (bb_call_write_slot) · bin_t 0 · vstack 3 · handencoded 0 · med_inv 75 · sno_pat_reg HARD · emit_blind 0.

## Concurrent absorbed
`9480185` "Prolog: GZ-ONLY pivot — delete flat+rich/heap-env fallback path; +movq xmm,r64 encoder" raced the push (−132 lines `emit_bb.c`, +9 `x86_asm.h`, −233 `scrip.c`). Rebased clean (it edits a different `emit_bb.c` region — Prolog codegen — not `bb_call_write_route`); rebuilt + full battery re-certified. Attribution: my −15 (bb_call) + its −14 + 1 file dirty→clean = GRAND 1192→1163.

## FIX-3 plan, refined (source-grounded — read before next bb_call work)
**`bb_call.cpp` CANNOT reach rc=0 without FIX-3-iii (PINNED).** Proven via the audit breakdown: the bulk — `lv 85 / rp 68 / bp 51 / ef 26 / mt 25` — is the `marshal_*` / `arith_opnd_*` / `byname` / `userproc` / `staged` machinery serving the **dval==2/3 mass**. Genuine cross-subsystem blocker → cursor STAYS per SOP.

- **FIX-3-i (write de-walk): DONE this run.** The enum-split half (`IR_CALL_WRITE_SLOT`/`WRITE_EXPR`) is now **redundant churn** — the EMIT-BLIND goal is met via the prep-relocation. Do **not** also add those IR kinds.
- **FIX-3-ii (DEFINE carve, dval==5): next pin-free increment, but more entangled than advertised.** The ladder calls it "SMALL; 2 readers," but `dval==5` is woven into the **shared `dval==2||3||5` compound predicates** (`emit_bb.c:3270` + `bb_call.cpp:108/137/166/347`). Peeling it means touching those shared sites (update them to also match `IR_CALL_DEFINE`, not remove dval logic). Still pin-free, but it is a **full IR-kind split** (lower_sno DEFINE branch → `IR_CALL_DEFINE`; IR.h + scrip_ir.c; emit_core dispatch; emit_bb prep `case` + the 2+ readers; delete the dval==5 arm; prove rt_proc_define live via the smoke `define`). Not started this run (LAW-7 budget).
- **FIX-7d stands:** no mechanical 7c passes (pe/mt hygiene) on the bb_call family — "churn-against-pending-split." Advance ONLY via the FIX-3 structural splits.

## Open PINs (need Lon's word)
1. **FIX-3-iii** — dval==2/3 channel: how `IR_CALL_GEN_SCAN` (Icon scan builtins) peels off `IR_CALL_PROC_STAGED`/`NAMED_PROC` so the native fast-path keys on a KIND, not `dval==3 + sval`. Co-owned with IRD/ICN. PIN before touching the dval channel (the OPERATION-section three-revert lesson).
2. **LANGUAGE-BLIND audit category** (carried from 71st/72nd). Adding it to `audit_bb_fixup_file.sh` retroactively flips ~7 behind-cursor files dirty (incl bb_call) → cursor-reset cascade. Options: (a) extend the byte-neutral strip to siblings, (b) add the audit category + accept the reset, (c) defer to FIX-FENCE. DEFERRED to Lon's explicit word.

## Standing verdicts (carried, none new)
m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop box ungated (ICON/lowering) · rank rp-patch ratify · ceiling-ratify 1163.

## NEXT SESSION
Cursor **stays `bb_call.cpp`**. With full budget either: land **FIX-3-ii** (DEFINE carve — the IR-kind split touching the shared `dval∈{2,3,5}` predicates), OR take Lon's **FIX-3-iii** pin to start the dval==2/3 mass (the real bulk). Clone SCRIP + corpus + x64; baseline battery GREEN before first edit. SCRIP @ `242e1d0` · `.github` @ this commit.
