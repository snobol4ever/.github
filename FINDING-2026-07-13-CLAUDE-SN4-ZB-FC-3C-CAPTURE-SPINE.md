# FINDING — ZB-FC-3c: the capture ring is STACK-INDEPENDENT, and SAVE's "capture stack" is a hand-rolled LIFO the FORTH spine already is

**Session:** s44 · 2026-07-13 · Claude
**Status:** RECON ONLY for 3c — zero capture code moved. (This session's LANDING was ALIGN-INV-2/RBP-FREE, a separate rung.)
**Rung:** `GOAL-SNOBOL4-BB.md` → ZB-FC-3c — CAPTURES (ASSIGN_SAVE/COND)

---

## Why this doc exists

The 3c rung carried an explicit standing order:

> ⛔ **UNVERIFIED, DO NOT ASSERT: nobody has read the commit-time walk — ONE GREP settles it, do it FIRST.**

and a stated **LOAD-BEARING INVARIANT**:

> the ring holds the **ABSOLUTE ADDRESS** of SAVE's δ-slot (§13 Tier C); once SAVE owns an rsp cell those are
> pointers INTO the stack — safe **precisely because** the ring is height-restored in the same LIFO order the
> cells pop, so a ring entry can never outlive its cell.

The grep was done. **The commit-walk claim is CONFIRMED. The load-bearing invariant is FALSE.** Both matter, in
opposite directions. This is the 8th consecutive session in which the PLAN, not the code, was the defective part.

---

## F1 — ✅ CONFIRMED: the commit walk IS linear left-to-right

`src/runtime/pattern_match.c:583` `rt_dcap_pump()`:

```c
while (c->i < g_rt_dcap_n) {
    int i = c->i;
    ...
    c->i = i + 1;
}
```

Strictly ascending from the scope base to the top. Commit order == record order == left-to-right.

⇒ **Lon's s42 ruling is verified by measurement, not assumed:** the LIFO push@α/pop@ω discipline ALREADY
produces the commit order. **No ordering machinery is needed and none should be built.**

Also confirmed and worth keeping: `g_rt_dcap_n` is re-read every iteration, so pends recorded by a *nested*
match (a `*VAR` proc body running its own match) are still swept by the outer pump. Any rewrite must preserve
that re-read.

Manual cross-check (Ch.6, read this session): conditional assignment *"occurs only if the pattern match is
successful"*, and *"may appear at any level of pattern nesting, and may include other conditional assignments
within its embrace."* The deferred-batch commit is oracle-correct BY THE MANUAL, and nesting is explicit —
so the LIFO spine must carry nesting, which it does natively.

---

## F2 — ⛔ REFUTED: the ring does NOT hold pointers into the ζ stack

`src/runtime/pattern_match.c:714` `rt_cap_open()`:

```c
long rt_cap_open(const char *varname, int saved_delta, int cur_delta, int is_imm)
{
    int len = cur_delta - saved_delta;
    const char *base = Σ ? Σ + saved_delta : NULL;          /* <-- pointer into the SUBJECT, not the frame */
    if (g_rt_dcap_active && !is_imm) { rt_dcap_record(varname, base, len); return 0; }
```

and the ring element:

```c
typedef struct { const char *varname; const char *base; int len; } rt_dcap_t;   /* pattern_match.c:539 */
```

The ring entry is **(varname, Σ+saved_delta, len)** — a pointer into the SUBJECT STRING plus an integer
length, both snapshotted AT RECORD TIME. `saved_delta` arrives BY VALUE as an `int` from the emitted box. The
ring never stores the address of SAVE's δ-slot and never dereferences the ζ frame.

⇒ **§13's Tier-C claim is wrong.** There is no dangling-pointer hazard to defend against, and the elaborate
"safe precisely because the ring is height-restored in the same LIFO order the cells pop" argument is
**unnecessary** — there is nothing to outlive.

⇒ **This DE-RISKS 3c substantially.** Moving SAVE's δ onto an rsp cell cannot corrupt the ring, under any
backtracking order. Delete the invariant from the rung rather than trying to preserve it.

*(Pre-existing, unrelated, NOT introduced here: `base` points into Σ, so any reallocation of the subject
during a match would invalidate ring entries. Out of scope; noted so it is not re-discovered as "3c broke it.")*

---

## F3 — THE ACTUAL PRIZE: SAVE's "capture stack" is a software LIFO simulating the stack rsp already is

`IR_MATCH_ASSIGN_SAVE`'s 16B zls grant (`zeta_storage.c:123`) is not scalar state — it is a **container**:

```
+0  (8B, ZK_PTR_GC)  capture.stack u32[] ([0]=cap, frames from [1]; box α-push/β-pop)
+8  (8B, RAW)        capture.stack gen(+8,4B) / sp(+12,4B)
```

and `pattern_match.c:675`:

```c
typedef struct { uint32_t *buf; uint32_t gen; uint32_t sp; } rt_cap_stk_t;
rt_cap_push(slot, delta): if (s->gen != g_cap_gen) { s->sp = 0; s->gen = g_cap_gen; }   /* lazy stale reset */
                          if (!s->buf) s->buf = rt_ws_alloc(17*4), s->buf[0] = 16;      /* first alloc      */
                          if (s->sp == s->buf[0]) { ...doubling growth via rt_ws_alloc... }
                          s->buf[1 + s->sp++] = (uint32_t)delta;                        /* α: PUSH          */
rt_cap_pop(slot):         s->sp--;                                                       /* β: POP           */
rt_cap_top(slot):         return s->buf[s->sp];                                          /* COND yield: TOP  */
```

**That is a per-box, heap-backed, growable LIFO stack of integer δs.** Its entire job is to let a SAVE box hold
one δ *per activation* so a generator re-entry between capture-open and capture-close finds the right span.

**The FORTH spine is a LIFO stack of fixed cells.** So:

| capture-stack machinery | FORTH-spine equivalent |
|---|---|
| `rt_cap_push` at α (grow array, `buf[1+sp++]=δ`) | `sub rsp,16` at α + store δ in own cell |
| `rt_cap_pop` at β (`sp--`) | **nothing** — β emits nothing; LIFO already put rsp at the frontier (FORTH law, S10c) |
| `rt_cap_top` at COND yield | read own cell |
| ω exit | `add rsp,16` at the ω hook — automatic |
| `gen` generation stamp + lazy `sp=0` reset | **DELETED** |
| `buf` + doubling growth + `rt_ws_alloc` | **DELETED** |

**The `gen` stamp is the tell.** Its own comment says it exists so that *"success-exited frames (never β-popped
— the γ-exit-live case) die at the next match instead of leaking across statement executions."* Under the FORTH
spine there IS no γ-exit-live leak: the ω hook pops the cell at **every** exit path (that is what S10b's
invert+pop+jmp synth is for). **The leak class the gen stamp compensates for cannot occur, so the compensation
dissolves.** This is the rung's predicted "mark/depth machinery dissolves" — arrived at for a *different and
correct* reason than the rung gave.

⇒ 3c is not "give SAVE a cell." 3c is **"delete the software stack, because the hardware one is already there."**

⇒ **AND IT IS A GC CUSTOMER.** `rt_cap_push` is a live `rt_ws_alloc` caller with doubling growth. Deleting it
removes an allocation site from the workspace — 3c therefore pays into TR/GC-W, and should be counted there.

---

## F4 — THE FENCE (the thing that makes 3c non-trivial, and the reason it is NOT a one-line fc_geom grant)

`fc_geom` (`zeta_storage.c:380`) is **node-local**: it sees an `IR_t *` and nothing else. But the FORTH cell
discipline is only sound where the S10c port invariant holds — and **ARBNO is still Tier-D heap flavor and moves
rsp per iteration between the body's γ and a later β.** ZB-FC-3b hit exactly this and **declined SEQ inside an
ARBNO body** (caught by `166_pat_arbno_cond_assign_commit` — note the name: it is *already a capture-in-ARBNO
test*).

⇒ A SAVE inside an ARBNO body **must decline** and keep the array path, until ZB-ITER lands.

⇒ Therefore 3c needs a **registrar with lowering context** — the `fc_seq_register` / `fc_alt_register` shape
(side table keyed by node pointer, PEERS RULE forbids IR_t fields) — **not** a one-line arm in `fc_geom`.
Budget accordingly; the "cheap grant" reading of this rung is wrong.

**Good news on coupling:** `lower_snobol4.c:1154` computes each ALT arm's exact footprint by calling `fc_geom`
itself, *before* the zero-cell whitelist switch at :1156-1159 (which currently lists
`IR_MATCH_ASSIGN_SAVE/_COND/_IMM`). So once SAVE is granted, **ALT's pad-to-max fp picks it up automatically**
and `fc_alt_fpmax` stays exact. No ALT edit is owed. VERIFY this on landing rather than trusting this line.

---

## LANDING PLAN (next session starts mechanical)

1. **`fc_save_register`** (zeta_storage.c, beside `fc_seq_*`/`fc_alt_*`): side table of SAVE nodes eligible for
   a cell. LOWER registers a SAVE iff it is **not inside an ARBNO body** (reuse ZB-FC-3b's own ARBNO fence
   predicate — do not re-invent it; find it, it is the thing that declined SEQ).
2. **`fc_geom`**: `IR_MATCH_ASSIGN_SAVE && fc_save_registered(nd)` → `*k = 16`.
3. **`bb_match_capture.cpp`**: under the grant — α stores δ into the own cell (drop the `rt_cap_push` call);
   COND-yield reads the own cell (drop `rt_cap_top`); β emits nothing. Ungranted SAVE keeps today's array path
   verbatim (**degrade, never die** — the ladder's standing rule).
4. **Gate**: crosscheck watermark-exact **both flavors** (default CSTACK **and** `SCRIP_ZETA_PORT=6`) × both
   media; sno 7/7 ×2; icon/prolog/raku unchanged; **`166_pat_arbno_cond_assign_commit` and 155–160 are the
   named capture tests — they are the bar**; `.s` regen (codegen touched).
5. **Only after 4 is green**: consider whether the array + `gen` + `rt_cap_push/pop/top` can be DELETED outright
   (they can only die when every SAVE is granted, i.e. after ZB-ITER lifts the ARBNO fence). Until then both
   paths coexist. **Count the removed `rt_ws_alloc` site into the TR/GC ledger when it finally goes.**

## Standing correction to the rung text

- DELETE the "ring holds the ABSOLUTE ADDRESS of SAVE's δ-slot" invariant — it is false (F2).
- KEEP the "commit walk is linear left-to-right" claim — it is true and now measured (F1).
- REWRITE the goal from "captures get a cell" to "the software capture stack dies into the spine" (F3).
- ADD the ARBNO fence + registrar requirement (F4) — this rung is NOT a one-line grant.
