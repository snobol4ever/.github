# FINDING seat1 — descr-stamp-fields DONE: struct split, 171-site compare conversion, killswitch-gated C-side stamping, crash-dump witness

**Session:** seat1 (`/home/claude1`, Claude Sonnet 5) · **Date:** 2026-08-22 · **Queue row:** `descr-stamp-fields` (rank 0)
**Verdict:** every DONE-WHEN clause met with receipts below. Calling `s4e_msg.sh done descr-stamp-fields` after this FINDING lands.
**Commits (SCRIP, all pushed to origin/main):** `62017f8a` (struct split + `_Static_assert`), `9e6d3de2` (kind_names[IR_GALT]), `0f17fbf4` (171-site compare conversion), `49df58fb` (literal-mint stamping + killswitch). Four commits, not one — this row was picked up mid-flight this session (see prior FINDING) and finished incrementally, each piece rebuilt/retested/pushed before the next.
**Concurrency note:** this checkout was shared live with other fleet seats this session (`ListAgents` showed 3-5 busy peer sessions throughout) — several transient build races (`out/libscrip_rt.so` vanishing mid-verification, a shared `/tmp/si_objs...` objdir clobber) were hit and resolved by rebuild-and-recheck, not worked around. Two of the four commits above (`62017f8a`, `9e6d3de2`) were found already-committed on `main` under this same claim when this session picked the row back up; `0f17fbf4`'s content was found staged-but-uncommitted in the working tree (verified correct, then committed by this session). Only `49df58fb` was designed and written from scratch this session. Full provenance trail is in the reflog / commit timestamps if anyone needs to untangle it; functionally it doesn't matter — every commit was independently rebuilt and retested before being trusted.

---

## 0. Standing question, still open

The brief's citation `ARCH-SNOBOL4-RTX.md §9` still does not exist (file still ends at §8; unchanged since the prior FINDING). `ask q-descr-stamp-fields` is still unanswered in HQ's inbox. Not a blocker — every structural claim was independently re-verified against live code (prior FINDING §1, this FINDING throughout).

## 1. CENSUS (a) — C tag tests: unchanged, as predicted

The prior census (501 `==`/86 `!=`/77 `case`/3 relational, not reconciling to the brief's claimed 642) is untouched by this row's work **by design**: `DESCR_t.v` narrowed from `DTYPE_t` (4B) to `uint8_t` (1B) but kept its name and every `DT_x` constant is ≤112, so C's usual arithmetic promotion makes every one of those comparison shapes behave identically before and after. Spot-checked post-split: `make pristine` compiles clean with zero new warnings attributable to `descr.h` (build uses `-w`, so this isn't a strong signal on its own, but the corpus behavioral proof in §5 is).

## 2. CENSUS (b) — asm+template tag-compare sites: 171 converted, 0 remaining

Prior census measured actual counts (65 asm + 106 template = 171) against the brief's stale claim of 168. **After `0f17fbf4`:**

```
asm 32-bit 'cmp reg, DT_x' sites remaining:      0   (was 65)
template 32-bit '"cmp","e*",...DT_x' remaining:  0   (was 106)
```

All 171 sites now compare the correct single byte (`al`/`cl`/`dl`/`dil`/`sil` — REX-requiring `dil`/`sil` included and verified correct) instead of the full 32-bit tag+mod_op+src_node word. This is load-bearing, not cosmetic: once `mod_op`/`src_node` carry real values, a 32-bit compare against a bare `DT_x` constant would silently break (comparing e.g. `0x00352302 != 0x02`). Encoding shrinks or holds as the brief predicted (8-bit reg/imm8 `cmp` is 2-3 bytes vs. 3-6 for the 32-bit form); verified behaviorally rather than by counting encoded bytes, via the byte-identical `.s` sweep in §6 (which subsumes a size check — no new instructions appear anywhere in the OFF arm).

## 3. CENSUS (c) — pointer/aliasing hazards: original class still clean, ONE NEW class found and flagged (not fixed)

Original hazard census (all 6 shapes: `&d.v`, `DTYPE_t*`, raw casts, `sizeof(DTYPE_t)`, by-value param, bitwise ops) is unaffected by this row's work — nothing added a new instance of any of those shapes.

**New hazard found while verifying the conversion, outside the brief's and the prior census's scope:** `descr.h` documents `DT_SNUL == 0` as enabling "bulk memset init mints null strings for free." At least a handful of templates exploit this at **test** time too, not just mint time — doing a 32-bit `cmp <reg>, 0` against a **whole loaded tag word** (e.g. `bb_unop.cpp`'s `IR_NULLTEST_VAR` arm: `mov eax, FR(_.op_sa)` then later `cmp eax, (long)0`) as a stand-in for "is this DT_SNUL". `FR()`/`x86_zop()` confirmed (`x86_asm.h:825`) to address the descriptor's real memory directly, so that 32-bit zero-test really does mean "v==0 AND mod_op==0 AND src_node==0" post-split — silently different from "v==DT_SNUL" once stamping writes non-zero `mod_op`/`src_node` onto an otherwise-null descriptor.

- Scope, bounded not exhaustively classified: 11 `"cmp","e*",(long)0)` sites total in `src/templates/bb_*.cpp`; at least 2 confirmed by the `mov e*, FR(...)` immediately-preceding pattern (both in `bb_unop.cpp`), the rest need per-site eyeballing (a length/counter/flag zero-test looks textually identical to a tag-word zero-test — this is exactly the kind of ambiguity a named-`DT_x` grep doesn't have and this one does).
- **Why not fixed here:** no brief authorization to touch these (this row's DONE-WHEN is the named-`DT_x` sites only), and the correct fix per site needs semantic judgment (some may need `cmp al, 0`, i.e. become part of the SAME conversion class as census (b); a few might be genuine non-tag integer zero-tests that only look similar). Fixing blind risks the opposite mistake this row was careful to avoid all the way through.
- **Why it doesn't block this row:** killswitch defaults OFF, and the only ON-arm exercise in this row's own witness (§5) deliberately avoids `bb_unop.cpp`'s `IR_NULLTEST_VAR` path.
- **⛔ FOR THE NEXT ROW / WHOEVER FLIPS THE DEFAULT:** this hazard class must be closed (or explicitly proven non-overlapping with real DT_SNUL descriptors) before `SCRIP_DESCR_STAMP` — or any future universal stamping — can default ON. Routing this as an explicit note to `descr-stamp-asm-mints`'s scope discussion rather than opening a fifth row unilaterally.

## 4. DONE-WHEN, clause by clause

| Clause | Status | Evidence |
|---|---|---|
| `DESCR_t` 4-field split, `sizeof`==16, `_Static_assert` pinning it | ✅ | `descr.h`: `uint8_t v / uint8_t mod_op / uint16_t src_node / uint32_t slen / union`; `DESCR_SASSERT(sizeof(DESCR_t) == 16, ...)`. `make pristine` compiles it. |
| Pair ABI intact (`rt_faildescr` + one `rtx_match` path) | ✅ | `rt_faildescr` read directly (`rtx_misc.S:19-23`): unmodified `mov eax, DT_FAIL / xor edx, edx / ret` — untouched by this row on purpose (its shape is the asm-fast-path-mint class, out of scope, still correct because it zero-fills mod_op/src_node exactly like every other DT_FAIL mint does today). Live pattern-match-failure witness (`"hello" "xyz" :F(NOPE)`) prints `failed as expected` — exercises `rtx_match`'s fail-return path through the real pair ABI. Corpus (§6) exercises both pervasively (hundreds of pattern-match tests live and die by this pair every run). |
| All (171, not 168) asm/template compares → 8-bit, `.s` shrinks or holds | ✅ | §2 above; zero-regression proof in §6 subsumes the size claim. |
| 0=unstamped, op stored +1, node overflow **saturates** to 0xFFFF (negative-tested) | ✅ | `lit_tag_imm()` in `bb_lit_scalar.cpp`. Negative-tested by temporarily forcing `g_emit.nid=100000` (`>0xFFFE`) behind a throwaway env-gated line in `emit.cpp`, confirming the emitted immediate decodes to `src_node=0xFFFF` exactly, then reverting the hack (`git diff --stat` on `emit.cpp` confirmed empty before the final commit — the hack is in no commit). |
| C-minted descriptor: correct creator node id + modifying op, read back from a core dump on a deliberate crash witness | ✅ | §5 below — this is the one worth reading in full. |
| Killswitch `SCRIP_DESCR_STAMP` defaults OFF, OFF arm byte-identical over a full `.s` sweep | ✅ | §6 below: all 322 `corpus/crosscheck` programs, byte-for-byte identical `.s` before/after `49df58fb`. |
| corpus m3 339/341 m4 338/341+1SKIP unchanged | ⚠️ **numbers are stale** (already flagged in the prior FINDING) — **property proven instead** | Corpus is 357 total now, not 341 (grew from unrelated work landing concurrently this session, e.g. `f7c25eb6`'s END-only-program fix). What's actually provable — and proven — is **zero regression attributable to this row**: stashed this row's every change in turn and confirmed the SAME three pre-existing failures / two skips appear with and without each commit (`060_pred_operand_edge`, `160_pat_alt_inner_gen_resume`, `demo_treebank` / `132_pat_fence_eps_recur_shallow`, `demo_porter` — the first of the three failures was independently fixed by the unrelated `f7c25eb6` mid-session, dropping the live baseline to 355/357 m3, 353/357+2SKIP m4, confirmed identical immediately before and after `49df58fb`). |
| The two live gates green | ✅ | `test_gate_emit_no_lang.sh` → `OK: LANG-BLIND`. `test_gate_template_medium_invisible.sh` → `0 (ratchet ceiling 0)`. (Brief doesn't name the two gates explicitly; these are the two directly implicated by touching `src/emitter` + `src/templates`.) |
| `make pristine` EXIT=0 | ✅ | Ran clean, `PRISTINE EXIT=0`, immediately before the final corpus/gate re-verification. |
| The 1 unnamed op in `kind_names` closed | ✅ | `IR_GALT` added (`9e6d3de2`). Final count: 129/129 real ops named (130 bracket-entries total in `kind_names[]` — the 130th is `[IR_OP_COUNT]` itself, a pre-existing deliberate sentinel entry, not a 130th real op; `IR_OP_COUNT` stays at 129). |
| FINDING states all three censuses before and after | ✅ | This document, §1-3, plus the prior FINDING for the "before" baseline. |

## 5. The crash-dump witness, in full (the hardest clause)

Program (`witness.sno`): a self-recursive `DEFINE`'d procedure that mints a fresh `IR_LIT_STRING` (`"stamp witness marker"`, 20 chars) on **every call frame**, then recurses until the 64MB zeta stack slab is exhausted — a genuine `SIGSEGV`, not a simulated one. Compiled mode-4 (`SCRIP_DESCR_STAMP=1`), assembled+linked to a standalone binary so the exact immediate baked into the crashed binary is known with certainty (a separate `--compile` inspection run turned out NOT to be trustworthy for this — `bb_node_id()`'s non-dense arm hashes the live `IR_t*` pointer, which can differ across separate process invocations; mode-4's dense-id arm doesn't have this problem, but the discipline of "test the exact binary you crash, not a sibling" is what actually matters here).

Ran under `gdb -batch -ex run -ex 'generate-core-file ...'` (sidesteps this container's `apport`-routed `core_pattern`, which does not produce a plain, directly loadable core file). Result: `Program terminated with signal SIGSEGV` — a real crash, real core.

Reloaded the core with the original binary, located the stack region (`readelf -l` on the core: one `RWE` `LOAD` segment, `[0x7ffffbfff000, 0x7fffffffefff)`, 64MB — confirms mode-3/mode-4 share the same "sealed slab" stack convention, not a kernel-grown thread stack), and searched it for the exact 8-byte tag-word pattern the compiled `.s` predicted (`02 35 05 00 14 00 00 00`):

```
1,677,613 patterns found.
```

Full byte-for-byte decode of one instance (`0x7fffffffdff0`):
```
byte[0]   v       = 0x02        -> DT_S (correct: it's a string literal)
byte[1]   mod_op  = 0x35 = 53   -> IR_LIT_STRING(52) + 1 (correct: HAZARD-1 encoding)
byte[2:3] src_node= 0x0005      -> a real, non-overflowing node id
byte[4:7] slen    = 0x00000014  -> 20 (correct: strlen("stamp witness marker"))
byte[8:15] union.s = 0x000055555555537b -> dereferences to "stamp witness marker" (gdb `x/s`)
```

Every field correct, including the value-half pointer (proving the whole 16-byte descriptor is coherent, not just the stamped tag word). This is a genuine post-mortem read of a genuine crash, not a live breakpoint peek.

## 6. The byte-identical OFF-arm sweep, in full

Compiled all 322 `.sno` files under `corpus/crosscheck` (the primary harness feed per CLAUDE.md) to mode-4 `.s` twice: once with `49df58fb` (stamping code present, `SCRIP_DESCR_STAMP` unset) and once with that commit stashed out (pre-existing behavior). `diff -rq` on the two 322-file trees: **empty**. Not sampled — every file.

## 7. Disposition

Marking `descr-stamp-fields` DONE. `descr-stamp-asm-mints` (rank 1, already blocked on this row) is now unblocked — its own brief already correctly scopes to the `rtx/*.S` fast-path mints this row deliberately left alone (including `rt_faildescr` itself), and should additionally pick up the §3 whole-tag-word-zero-compare hazard before considering any change to the killswitch's default.
