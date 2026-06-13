# HANDOFF 2026-06-13 · Sonnet 4.6 · SNOBOL4-BB M3-CONCAT-MULTIPART

**SCRIP HEAD:** eb98b8e
**.github HEAD:** (this commit)

---

## What this session did

Fixed **M3-CONCAT-MULTIPART** (pat-rung 055). M3 pat-rung was 18/19; now **19/19**, full
m2/m3/m4 three-mode parity on the pattern rung suite.

---

## The bug

`OUTPUT = A ' ' B ' ' C` (and the single-part lit_s concat) gave empty output in M3 (BINARY/JIT),
correct in M2 and M4. The destination-variable-name pointer baked into the `lea rdi` BINARY arm of
`bb_gvar_assign_concat.cpp` was wrong in BOTH arms:

- **lit_s arm** used `_.op_sval`. But `op_sval` is **NULL** for `IR_ASSIGN_CONCAT` — `emit_bb.c:483`
  only sets it for `IR_DET_WRITE` / `IR_BUILTIN`. BINARY mode baked `movabs rdi, 0` → null dst name →
  `rt_gvar_assign_str` no-op.
- **multi-part arm** used `_.bb_ls`. That is `g_emit.bb_ls_buf` — a scratch buffer holding the *label
  name* (e.g. `.Ss_abcd`) produced by `bb_intern_into`, not the variable name. BINARY baked the address
  of the scratch char array → `rt_gvar_assign_concat_parts` got a garbled dst.

TEXT mode was always correct because it reads `_.bb_ls` as a **label** (the `lea rdi, [rip + .Ss_…]`
assembler reference), which resolves to the sealed string — the label and the pointer are two different
things, and only the pointer was wrong.

## The fix (2 lines)

Both arms' `lea rdi` ptr arg → `(IR_LIT(_.node).sval ? IR_LIT(_.node).sval : "")`. `_.node` is the
`IR_ASSIGN_CONCAT` node; `IR_LIT(_.node).sval` is the destination variable name, a permanent IR
allocation (same source `emit_bb.c:985` uses to set `bb_ls` for the TEXT label). `bb_ls` (TEXT label arg,
3rd parameter) unchanged.

```
-        + x86("lea",  "rdi", "[rip + __]", (uint64_t)(uintptr_t)(_.op_sval           ? _.op_sval           : ""), _.bb_ls)
+        + x86("lea",  "rdi", "[rip + __]", (uint64_t)(uintptr_t)(IR_LIT(_.node).sval ? IR_LIT(_.node).sval : ""), _.bb_ls)
...
-         + x86("lea",  "rdi", "[rip + __]", (uint64_t)(uintptr_t)_.bb_ls, _.bb_ls)
+         + x86("lea",  "rdi", "[rip + __]", (uint64_t)(uintptr_t)(IR_LIT(_.node).sval ? IR_LIT(_.node).sval : ""), _.bb_ls)
```

## Verification

- **M4 TEXT byte-identical** pre/post fix (proved via `git stash` + `diff` of `--compile` output). The
  change only touches the BINARY `movabs` immediate; TEXT reads the label arg, which did not change.
- **055** now prints `ab cd ef` in M2, M3, and M4 (matches sbl oracle).

## Gates at eb98b8e

- smoke: **7/7/7 HARD** ✓
- pat-rung: **m2 19/19 · m3 19/19 · m4 19/19 no-SKIP** ✓ (m3 was 18/19)
- fence (test_gate_sno_pat_reg): **HARD** ✓ (TIER 1 + TIER 2 both 0)
- no_bb_bin_t: **0** ✓
- broad m4-only corpus THIS CONTAINER: M2=172 · M3=**152** (was 144 pre-fix, **+8**) · M4=148

## Container-sensitivity note

The watermark's "155/280 floor" was from a different container. On the pre-fix stashed tree in *this*
container the baseline was M3=144 / M4=148; the fix moves M3 to 152 with M4 unchanged. Treat the
*delta within one container* as the regression signal, not the absolute number (per goal file's
hard-won-facts note). The line-23 inventory figure (155/280) is intentionally left untouched — M4 did
not move, so editing it would falsely imply change.

## Next session

Per MODE 4 BUG LADDER priority, next open rung is **M4-SMOKE-REGRESS** (m3 concat + m4 define fail with
`< /dev/null` — bisect the `bb_unify.cpp` duplicate-label `.Lx2_0` from 14ae014) or the **M4-FENCE**
cluster (061/062/064/066/100/101/103/108/110/112 — FENCE matches null L→R, fails on retreat, SPITBOL
p.204). The fence corpus fails (066/067/069) are still visible in the broad m4 run.
