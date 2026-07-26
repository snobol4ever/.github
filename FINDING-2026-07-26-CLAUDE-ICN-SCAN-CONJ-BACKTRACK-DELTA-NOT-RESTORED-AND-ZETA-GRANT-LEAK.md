# FINDING (2026-07-26) — JCON SELF-HOST BLOCKER: A FAILING CONJUNCTION AFTER A SUCCESSFUL `=` MATCH NEITHER RESTORES δ NOR RELEASES ITS ζ GRANT

**SCRIP `20aa255f` (no code changed) · RT_OPT=-O0 · oracle iconx 9.5.25a · oracle-jtran built via `icont -u -s`**

## THE HEADLINE

SCRIP-jtran (17 modules, 0 bombs, 5.12MB) **runs**, and is byte-identical to oracle-jtran through `preproc`
on JCON's own `irgen.icn` (1562 lines). It then dies in `yylex` on the file's FIRST field access. Root cause
is NOT the lexer and NOT `do_ops.icn` ordering — it is a **scan-backtracking defect in SCRIP**, reproduced in
6 lines of pure Icon with no jtran involved.

## THE MINIMAL REPRO (6 lines)

```icon
procedure main();
   local s;
   s := ".coord";
   s ? { if (="." & many(&digits)) then write("Y") else write("N") };
end
```

| engine | result |
|---|---|
| iconx 9.5.25a | `N` |
| SCRIP m3 | **SEGV** |
| SCRIP m4 | **SEGV** (mode-identical ⇒ LOWER or EMITTER, not a mode-specific runtime path) |

Companion repro, same root, no crash — shows the δ half directly:

```icon
   s ? { if (str <- ="." & str ||:= tab(many(&digits))) then write("NUM") else write("pos=", &pos) };
```
iconx `pos=1` · SCRIP **`pos=2`** (both modes).

## DISCRIMINATORS (each measured by removal — do not re-chase these)

| variant | verdict |
|---|---|
| `if ="." then write(&pos)` (match succeeds, no conjunction) | ✅ both `pos=2` |
| `if many(&digits) then Y else N` (bare failing scan in if/else) | ✅ both `N` |
| `if tab(many(&digits)) then Y else N` | ✅ both `N` |
| `(tab(many(&digits)) & write("Y")) | write("N")` (alternation, not if) | ✅ both `N` |
| `s[2:2]` zero-length substring · `tab(1)` no-op | ✅ both identical |
| **`if (="." & many(&digits)) then Y else N`** | ❌ **SEGV** |
| **`if (="." & tab(many(&digits))) then Y else N`** | ❌ **SEGV** |

So the trigger is precisely: **inside `?` scan, a CONJUNCTION whose LEFT operand is a SUCCEEDING `=` match
(which advances δ) and whose RIGHT operand FAILS.** Neither `if/else` alone, nor a failing scan alone, nor a
succeeding match alone is sufficient. `tab()` is not required. Zero-length allocation is not involved.

## THE MECHANISM — TWO SYMPTOMS, ONE ROOT

gdb on the m4 binary (`SCRIP_NO_SEGV_HANDLER=1`), at the fault:

```
#0  rt_substr (sigma=".coord", a=1, b=1) at gen_runtime.c:175
#1  xchain0_n12_α ()
rsp 0x7ffffbfff000   rbp 0x7ffffbfff050   r13 0x401210 (Σ subject, correct)   r14 0x1
```

1. **δ NOT RESTORED.** `r14` is the δ cursor (0-based, `&pos = δ+1`; ARCH-ICON register contract). At the
   failure edge it still reads **1**, i.e. `&pos=2` — still past the consumed `"."`. Canonical Icon backtracks
   the match and returns δ to 0 (`&pos=1`). This is the `pos=2` in the companion repro, seen in a register.
2. **ζ GRANT LEAKED.** `rsp` sits page-aligned ~64MB below its entry value. Under the build default
   `ZC_FRAME_RSP` + `ZC_PORT_FORTH`, port grants spend as `sub rsp,K` and must be released on BOTH return
   edges. The failure edge out of the conjunction never releases, so RSP walks down into the guard page.
   `rt_substr` is merely the first call to touch unmapped stack — **it is the victim, not the bug**
   (`rt_substr(1,1)`→len 0 is provably fine in isolation; `rt_str_alloc`'s documented contract `want=(n<0?0:n)+1`
   handles 0).

⚠ **DO NOT "fix" `rt_substr` or `rt_str_alloc`.** Both are correct. Hardening them converts the SEGV into the
silent wrong-`&pos` of the companion repro — strictly worse, because it hides the leak.

## WHY THIS IS THE SELF-HOST BLOCKER

`lexer.icn:135` is exactly this idiom — the real-literal lookahead:

```icon
if str <- ="." & str ||:= tab(many(&digits)) then { ... }   # special-cases ".123" as a real
```

For `p.coord`, `="."` consumes the dot, `many(&digits)` fails, and canonical Icon backtracks δ so the dot is
re-lexed as `lex_DOT` by `do_ops()` at line 148. SCRIP leaves δ past the dot, so the next token starts at
`coord`'s `c`, no operator arm matches, and the lexer reports `invalid character: "c"` (lexer.icn:170) —
which is precisely the error seen on `irgen.icn` line 29 (`\p.coord`, the file's first field access).
**Every Icon program using field access hits this.**

## PIPELINE STATE MEASURED THIS SESSION

| stage on JCON's `irgen.icn` | verdict |
|---|---|
| `preproc` | ✅ **byte-identical**, 1562 lines |
| `yylex` | ❌ blocked by the above |
| oracle-jtran full pipeline | ✅ 114 class files (needs `COEXPSIZE`, see below) |

**ORACLE INVOCATION GOTCHA (cost a false blocker this session):** oracle-jtran dies with Icon **runtime error
302 (memory violation)** on `irgen.icn` unless the co-expression region is enlarged. `jtran_main.icn:55` runs
every pipeline stage as `create fn(c,args)`, so deep recursion consumes the **co-expression** stack, not the
main stack. `jcon-master/bin/jcont:92-99` sets `BLKSIZE`/`STRSIZE`/**`COEXPSIZE`** and explicitly **unsets
`MSTKSIZE`**. Raising `MSTKSIZE` does nothing; raising `COEXPSIZE` is the fix. Working values:
`BLKSIZE=60000000 STRSIZE=20000000 COEXPSIZE=40000000`.

## SUPERSEDED: THE `hw.icn` "CONSTANT-POOL ORDERING" DIAGNOSIS IS STALE

`GOAL-JCON-IN-SCRIP.md`'s LIVE CURSOR (2026-07-23, `cf31d9d1`) says the last `hw.icn` gap is JVM
constant-pool ordering, `sc=973 vs or=983` bytes, and points at `bc_gen_ir_Succeed`/`Fail`/`ResumeValue`.
**Measured at `20aa255f`: both files are 995 bytes; `cmp` first differs at byte 826; all 57 differing bytes
lie in 826–950.** The constant pool precedes 826 entirely and is therefore **byte-identical** — that
diagnosis no longer holds and should not be chased.

The actual residue is benign: `0x3a` is JVM `astore`. Oracle stores slots **19,17,18**; SCRIP **18,19,17** —
same set, permuted. Source is `gen_bc.icn:1495 bc_initialize_tmps`, which emits `aconst_null; astore <slot>`
in `key(bc_tmp_table)` order.

## TABLE ITERATION ORDER — A SANCTIONED DIFFERENCE, NOT A DEFECT (recommendation)

SCRIP's `key(table)` order differs from canonical Icon's. 15-line repro (8 one-char keys):

```
iconx:  keyorder=@-*$!+%/
SCRIP:  keyorder=%$!-/+*@
```

Both deterministic. Canonical contract, if it is ever to be matched: `rmisc.r:175` — string hash is
`i=0; for first ≤10 chars { i += c & 0xFF; i *= 37 }; i += length` — walked by `rstruct.r:263 hgnext` in
slot-index order with chains sorted ascending by `hashnum`, over a segmented directory that only grows.

**Consequences measured, both benign:**
- `interface.icn` regenerates **byte-identical** (415 lines).
- `do_ops.icn` differs (611 lines both, 401 lines differing) — but the emitted trie **arm SETS are identical**
  when sorted, i.e. a **pure permutation**. `oplexgen.icn:229 optimize_tree` mutates its table *while*
  iterating it (canonical Icon explicitly leaves that implementation-defined), yet its `while \changes`
  fixpoint converges order-independently, so the final lexer is semantically equivalent. **`do_ops.icn` is
  NOT the yylex blocker** — falsified directly.

**RECOMMENDATION:** do not replicate Icon's hash. JCON targets the JVM, where these same tables are Java
HashMaps with a third order again, so `jjtran` permutes them too and JCON still self-hosts. Byte-identity of
`key()` order is a property JCON itself does not preserve. Declare order-permutation a sanctioned difference,
compare modulo it, and keep the hash contract above recorded in case a strict-identity gate is ever wanted.

## FIX / RE-TEST GATE

Start where the failure edge of a conjunction inside a scan is wired — the same `emit.cpp` neighbourhood as
the open nary-DISJUNCTION rung, and plausibly the same family as the FZ-E scan cluster. The fix must do BOTH:
restore δ (r14) and release the ζ grant on the failure edge.

1. `e2.icn` (6-line repro) → `N`, no SEGV, both modes
2. companion `<-` repro → `pos=1`
3. `v5.icn` (`zz := p.coord` through SCRIP-jtran) → class files produced
4. `SCRIP-jtran preproc irgen.icn : yylex : parse : ast2ir : bc_File` → 114 class files, diff vs oracle
   modulo the sanctioned `astore` permutation
5. `bash scripts/test_icon_all_rungs.sh` → must not regress 249/12/32
6. Re-check FZ-E cluster (`scan1`/`scan2`/`recogn`) — plausibly the same root

## ARTIFACTS

Repros in `corpus/programs/icon/repro/`: `scan_conj_backtrack_segv.icn` (e2),
`scan_conj_revassign_pos.icn` (companion), `keyorder.icn`. Build state: SCRIP-jtran `/home/claude/jt/jtran`;
oracle-jtran `/home/claude/jcon-oracle-src/tran/jtran`; icont/iconx `/home/claude/icon-oracle-src/bin/`.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus
