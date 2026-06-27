# HANDOFF 2026-06-14 — Icon m3/m4: local-VAR slot aliasing + cset canonicalization (Claude)

**Goal:** GOAL-ICON-FULL-PASS — Icon `--run`/`--compile` up to full native coverage.
**Result:** m3/m4 **118 → 122 (+4)**, FAIL 29 → 25, zero regressions. m2 no longer exists
(the `--run` IR-graph interpreter was deleted in `a2440f4`; gates are native `--run`/`--compile` only).
**HEAD (SCRIP) = `9354db7`** (2 commits, rebased clean onto `6e87566`). HEAD (.github) = this file.

Both fixes are the SAFE class: lowering / native-binding only, no shared-dispatch or runtime-helper
change. Each was verified with an EXPLICIT full-suite FAIL-list diff (before vs after) showing ONLY the
intended rungs flipped — never a bare PASS-count delta, which can hide an EXCISE→FAIL.

---

## (1) `24b4266` — local IR_VAR reader aliases its varslot (+3)

**Symptom:** `every total := total + (1 to n)` → 5, not 15 (rung02_proc_locals, rung10_augop_break_repeat,
rung11_bang_augconcat_bang_concat — the accumulator pattern in all forms: `+:=`, `||:=`, `every x := x + g`).

**Root cause:** the descr flat-chain IR_VAR reader (`walk_bb_flat` case IR_VAR, emit_bb.c) allocated a
FRESH 16-byte copy slot (`op_off = bb_slot_alloc16(nd)`) and the `bb_var` template copied varslot→copy
ONCE. But that read is loop-hoisted (the VAR node sits above the loop in chain order), while IR_ASSIGN
keeps writing the REAL varslot each iteration. So BINOP always read the stale snapshot = the ORIGINAL
value. `0 + i` for the last `i` = 5, not the running sum.

Confirmed by reading the m4 asm for rung02_proc_locals: ASSIGN writes `[r12+48]` (the "total" varslot)
each iter, but BINOP reads `[r12+88]` (the VAR node's copy slot, written once before the loop).

**The rule it violated:** PER-BOX LOCAL STORAGE FACT RULE — *"a variable is ONE name-keyed frame slot
(`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers."* The private copy slot
was the bug; the law wants readers to read the varslot directly.

**Fix (one line, emit_bb.c `walk_bb_flat` IR_VAR local-var branch):**
```c
else { int voff = bb_varslot_peek(IR_LIT(nd).sval); g_emit.op_sa = voff;
       if (voff >= 0) { g_emit.op_off = voff; if (bb_slot_get(nd) < 0) bb_slot_register(nd, voff); }
       else g_emit.op_off = -1; }
```
Alias `op_off` to the varslot offset and register `nd → voff` so `bb_slot_get(nd)` (what consumers read)
returns the LIVE varslot. The `bb_var` template is UNTOUCHED — with `op_off == op_sa == voff` its
`mov rax,[r12+voff]; mov [r12+voff],rax` is a harmless self-copy. The `bb_slot_get(nd) < 0` guard makes a
double-walk (generator re-walk) idempotent.

**Safety reasoning (why aliasing doesn't break snapshots):** IR_ASSIGN already COPIES the RHS value INTO
the LHS varslot at assign time, so a value is committed to a slot at the moment of assignment. The only
scenario aliasing could change is a VAR read whose result is consumed AND the varslot mutates between read
and consume with no intervening copy — which is exactly the accumulator (and the fix is correct there).
Swap (`x:=:y`) reads varslots directly via `bb_varslot_peek` (flat_drive_swap), unaffected. Verified by
the full FAIL-diff: ONLY the 3 intended rungs flipped, both modes.

## (2) `9354db7` — cset literals canonicalized at lowering (+1)

**Symptom:** `"ac" == 'ca'` FAILed while `"ac" <<= 'ca'` PASSed on the SAME pair (rung37_str_relop missing
exactly the `ac=='ca'` line).

**Root cause:** `lower_icon.c:132` lowered BOTH `TT_QLIT` (string) and `TT_CSET` (cset) to the SAME
`IR_LIT_S` with the RAW `t->v.sval`. So `'ca'` became the literal string `"ca"` — cset identity lost, and
not even sorted. `==` (lexeq, ocomp.r) length-checks then `lexcmp("ac","ca") != Equal` → fail; `<<=`
(lexle) is pure `lexcmp Less` → "ac" < "ca" → pass. Per ocomp.r a cset coerces to its SORTED member string,
so `'ca'` → `"ac"` and both should pass.

**Fix (lower_icon.c):** csets are plain strings throughout the native path (there is NO cset type —
TT_CSET and TT_QLIT shared one `IR_LIT_S`), so canonicalize at lowering. Split the combined case and add a
static helper that sort+dedups the member bytes (iterate char codes 0..255, emit present ones = Icon
collating order):
```c
static const char * icn_cset_canon(const char * s) {
    if (!s) return s;
    unsigned char seen[256]; memset(seen, 0, sizeof seen);
    for (const unsigned char * p = (const unsigned char *) s; *p; p++) seen[*p] = 1;
    char buf[257]; int n = 0;
    for (int c = 0; c < 256; c++) if (seen[c]) buf[n++] = (char) c;
    buf[n] = 0; return lp_strdup(buf);
}
...
case TT_QLIT: { ... IR_LIT(nd).sval = t->v.sval; ... }
case TT_CSET: { ... IR_LIT(nd).sval = icn_cset_canon(t->v.sval); ... }
```
Sort+DEDUP is correct for set contexts too (`*'caa'` = 2, `upto('ca')` = `upto('ac')` — same character
set). Persisted via `lp_strdup` (the lower-common intern). `'ca'` → `"ac"`.

**This changed EVERY cset literal in the corpus** → the FAIL-diff was the safety net: ONLY rung37_str_relop
flipped FAIL→PASS, both modes, no cset-test regression. Helper max line = 200 (at the limit, OK);
lower_icon.c over-length-line count unchanged at 8 (all pre-existing, none mine).

**NOTE — separate bug, NOT fixed:** `image('ca')` / `image(x)` of a var still returns `&null` — the
builtin-call arg isn't marshalling the VAR's value (the arg DESCR is uninitialised). This is the same
class as rung29 `type(x)`/`image(x)` → null. Distinct from the slot aliasing fix here.

---

## Verification (full battery, run before each commit AND re-run after the rebase)

| Check | start | final |
|---|---|---|
| Icon m3 `--run` | 118 | **122** |
| Icon m4 `--compile` | 118 | **122** |
| Icon FAIL | 29 | **25** (pure FAIL→PASS ×4) |
| Icon EXCISED / XFAIL | 100 / 36 | 100 / 36 (unchanged) |
| Icon smoke (m3/m4) | 12/12 | 12/12 |
| Prolog smoke (m3/m4) | 5/5 | 5/5 |
| no-stack push/pop | 0 | 0 |
| FACT (seg_byte/SL_B/…) | 0 | 0 |
| lower_icon.c over-length lines | 8 | 8 (pre-existing) |

Files: `src/emitter/emit_bb.c` (+3/−1, IR_VAR branch), `src/lower/lower_icon.c` (+10, helper + case split).
Rebased onto `6e87566` (concurrent de-interp landing) and REBUILT + RE-GATED after rebase — all green.

---

## NEXT — the real-arith relop is genuinely its own session (fully traced this session)

**rung18 real_gt (`1.5 > 2.5`), mixed (`n < 2.5`)** bomb rc=134 `bb_binop_relop: shape mismatch`. Why:
- `rt_jct_relop` (by_name_dispatch.c:1229) has NO real/mixed numeric branch — junction, then int-int,
  then STRING strcmp of the real images (not Icon-numeric).
- The template's int-arm (`cmp rax,rcx` on `FRQ(sa+8)` int payloads) and the DESCR call-arm
  (`rt_jct_relop`) prepare operands INCOMPATIBLY: a VAR goes through `op_name1/2`+strtab in the int arm
  but DESCR slots (`FRQ(sa)`/`FRQ(sa+8)`) in the call arm; and `LIT_F` operands get NO slot
  (`op_sa`/`op_sb` < 0 → neither arm fires → bomb).
- Gate inconsistency: real_gt/mixed are ADMITTED (then bomb) while real_eq/real_lt/real_relop_goal are
  DECLINED (clean excise).

**Fix = 4 coordinated pieces (one session, SHARED binop area → gate the FULL suite + FAIL-diff + prolog/
snobol4 smokes):** (1) extend `rt_jct_relop` with a real/mixed branch (either operand `IS_REAL` → coerce
both to double, compare; keep int-int fast path) per oarith.r/ocomp.r; (2) in the relop operand setup
(emit_bb.c ~2895), for a numeric relop with a real/unslotted operand, slot BOTH operands as full 16-byte
DESCRs (LIT_F→{DT_R,bits}, LIT_I→{DT_I,val}, VAR→its varslot) + set a route flag; (3) add a template arm
(or extend the SLT..SNE call-arm key) routing BINOP_LT..NE through `rt_jct_relop` under that flag;
(4) make the gate admit real relops consistently. Same path also unblocks real-VAR arith
(`x:=1.5;write(x+y)`).

**Other targets seen, not started:** rung29 `type(x)`/`image(x)` of a var → null/&null (builtin-call arg
not marshalling the VAR value); generators/`suspend` (rung03), `limit` (rung14 rc=124), real to-by
(rung19), lists push/put/get/pull (rung22, 2 segfaults), sort (rung31, segfaults), user-proc recursion
depth-4096 (rung02_proc_fact), multi-gen CALL args (rung13 cross_arg — fresh-session per prior watermark).

**Canonical-source intel used:** `refs/icon-master/src/runtime/ocomp.r` (lexeq length-check + cset→string
coercion; numeric `==/>/<` semantics), `oarith.r` (numeric coercion protocol), `irgen.icn`
`ir_a_Every`/`ir_binary` (port topology). m2 oracle no longer exists; canonical is the only authority.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
