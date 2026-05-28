# HANDOFF — ICON-BB Step 9 — Claude Sonnet 4.6 — 2026-05-27

## What was done

**Step 9: AG-pure N-ary applies — BB_LCONCAT, BB_SECTION, BB_IDX, BB_IDX_SET**

Also in this session: LFJ-15b was completed first (see HANDOFF-2026-05-27-SONNET-ICON-BB-LFJ-15b.md).

### Lower side — _ag variants (lower_icn.c)

| Function | Kind | Chain |
|----------|------|-------|
| `lower_icn_new_Lconcat_ag` | BB_LCONCAT | lhs→rhs→apply; apply reads peek(1/0) |
| `lower_icn_new_Sectionop_ag` | BB_SECTION | base→i1→i2→apply; apply reads peek(2/1/0) |
| `lower_icn_new_Idx_ag` | BB_IDX | base→idx→apply; apply reads peek(1/0) |

`lower_icn_expr_threaded_b` early-exits for TT_LCONCAT, TT_SECTION/PLUS/MINUS, TT_IDX.

### Executor side — AG-pure branches (bb_exec.c)

All gated on `nd->α == NULL && nd->β == NULL` (scrubbed by _ag):

- **BB_LCONCAT**: peek(1)=lhs, peek(0)=rhs → `icn_lconcat_d`
- **BB_SECTION**: peek(2)=base, peek(1)=i1, peek(0)=i2 → `subscript_get2` (PLUS/MINUS transform inline)
- **BB_IDX**: peek(1)=base, peek(0)=idx → `subscript_get`
- **BB_IDX_SET**: peek(2)=base, peek(1)=idx, peek(0)=rhs → `subscript_set`

### Note on BB_IDX_SET lower side

`lower_icn_new_Idx_ag` covers TT_IDX (subscript read). TT_IDX_SET (subscript write with 3 operands: base/idx/rhs) still uses Family-2 (BB_CALL deep-thread) path in `_threaded_b` — the executor AG-pure branch was added for it but the lower side _ag wasn't needed since it goes through the sidecar path. This is fine for Step 9; Step 10 will clean it up.

## Gates

```
smoke_icon 5/5  ·  icon_all_rungs 198/268  ·  smoke_prolog 5/5  ·  broker 30/52  ·  FACT RULE 0
```

## Commits

- `6a631124` — LFJ-15b: AG-pure consolidation (all _threaded_b intercepts retired)
- `1dfe9631` — Step 9: AG-pure N-ary applies

## What's next

**Step 10** — Sidecar cleanup: delete `bb_operand_aux_set/get` calls from Icon lower path.

Remaining sidecar users in Icon path:
- `lower_icn.c:1908` — Family 1 (BB_ASSIGN, `bb_operand_aux_set`)
- `lower_icn.c:1939` — Family 2 (BB_CALL non-generator, `bb_operand_aux_set`)
- `bb_exec.c:845` — BB_ASSIGN apply reads sidecar
- `bb_exec.c:922` — BB_CALL reads sidecar for deep-thread path

Step 10 replaces these with ring reads (peek) — the chain walker already pushes every node's value to the ring, so the apply box can read peek(0) for the last arg without a sidecar. BB_CALL with multiple args needs peek(N-1..0). Family 1 (BB_ASSIGN) needs peek(0)=rhs. The odometer path (generator args) is a separate concern and stays on its current path.
