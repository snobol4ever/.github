# FINDING (2026-07-27, s169) — SCRIP-jtran output was NON-DETERMINISTIC; root cause = address-keyed structure hash. FIXED, 17/17 byte-reproducible.

**SCRIP `e63a8b6a` + 1 runtime fix · Icon suite 250/11/32 UNCHANGED (measured post-fix) · RT_OPT=-O0**
**Oracle: Arizona Icon 9.5.25a semantics read from uploaded source. NO JAVA USED (Lon directive 2026-07-21).**

---

## HEADLINE

s168 reported "JCON self-host 17/17 class-count parity, byte-identity open (key() ordering)". **The byte-identity
blocker is worse than an ordering mismatch: SCRIP-jtran did not agree with ITSELF.** Same binary, same input,
same flags produced **different bytes and different file sizes on every run**. No prior doc names this.

Root-caused to ONE line and fixed. Post-fix all 17 modules are byte-reproducible run-to-run.

| | pre | post |
|---|---|---|
| Modules byte-reproducible across 2 runs | 0/17 | **17/17** |
| Class counts (total) | 513 | 513 (unchanged) |
| Icon suite | 250/11/32 | 250/11/32 (unchanged) |

⚠ **REPRODUCIBLE ≠ ORACLE-IDENTICAL.** This makes SCRIP self-consistent. It does NOT match `iconx`'s ordering
(SCRIP uses 256-bucket djb2 string keys; canonical Icon uses `13255*id>>10` into a split-chain hash — different
bucket structure entirely). Determinism is the PREREQUISITE for byte-identity work, not the achievement of it.

---

## ROOT CAUSE — `tbl_key_str` keyed structures by RAW POINTER ADDRESS

`src/runtime/aggregates.c`, the table-key derivation:

```c
default:      snprintf(buf, bufn, "\001p%p", kd.ptr); return buf;
```

Every non-scalar key — list, set, table, record — was keyed by `%p`, its heap address. Addresses move run to
run (allocator/GC/ASLR state), so the djb2 bucket differs, so `key()` iteration order differs, so every
downstream artifact differs.

**MEASURED, NOT INFERRED.** Minimal repro (`/tmp/keyorder2.icn`), 4 runs, record-keyed and list-keyed tables:

```
record-keys: 8 5 4 7 2 1 3 6      list-keys: 2 3 4 6 7 5 1 8
record-keys: 4 5 8 7 2 1 3 6      list-keys: 2 1 8 7 5 3 6 4
record-keys: 1 3 6 8 5 4 7 2      list-keys: 7 5 1 8 2 3 4 6
record-keys: 8 5 4 7 6 3 2 1      list-keys: 8 3 5 2 7 4 6 1
```

String-keyed tables were ALWAYS stable (content-hashed) — which is exactly why this hid for so long: the suite
and most corpus programs key tables by string.

### How it surfaced in the bytecode

Bracketed by hexdump of the smallest divergent class (`p_l$lexer$lex_error.class`, 1643 vs 1648 bytes, first
divergence at byte 1217 — i.e. header and most of the constant pool AGREE):

```
run1: ... 3a 21 ... 3a 22 ... 3a 1e ... 3a 20     code_len 0x189 (393)
run2: ... 3a 20 ... 3a 1e ... 3a 22 ... 3a 21     code_len 0x18e (398)
```

`3a` = JVM `astore`. Identical instruction sequence, **same SET of local-variable slots, different assignment
ORDER**, and the method code length moves with it. jtran allocates local slots by walking a table keyed by AST
records — so hash order IS slot order IS emitted bytecode.

### Canonical Icon does NOT do this

`refs/icon-master/src/runtime/rmisc.r` L254-272 — the hash of a list/set/table/record is **its `id`**, hashed
like an integer:

```c
case T_List:   i = (13255 * BlkLoc(*dp)->list.id) >> 10;   break;
case T_Set:    i = (13255 * BlkLoc(*dp)->set.id) >> 10;    break;
case T_Table:  i = (13255 * BlkLoc(*dp)->table.id) >> 10;  break;
case T_Record: i = (13255 * BlkLoc(*dp)->record.id) >> 10; break;
```

and `ralc.r` assigns those ids from monotonic serial counters at allocation:
`list_ser++` (L284) · `set_ser++` (L244) · `table_ser++` (L240) · `recid++` (L349) · `coexp_ser++` (L137).
Allocation ORDER is deterministic for a deterministic program, so `iconx` reproduces byte-for-byte. **Address
is never used as a hash input anywhere in canonical Icon.**

⭐ **SCRIP ALREADY HAD HALF OF THIS AND WASN'T USING IT.** `DATINST_t` (core.h) already carries `long id`, and
`core.c` already stamps it `u->id = t->serial_next++` — a per-record-type serial, exactly canonical. It was
simply never consulted by `tbl_key_str`, which fell through to `%p`.

### Fix (`src/runtime/core/core.h`, `src/runtime/aggregates.c`, +2 outlier files)

- Added `long id` to `ARBLK_t` and `TBBLK_t`; added `g_agg_list_ser` / `g_agg_table_ser` monotonic counters and
  the accessors `rt_agg_serial_list()` / `rt_agg_serial_table()`.
- Stamped the id at **all five** allocation sites — `array_new`, `array_new2d`, `table_new` in aggregates.c,
  plus three that bypass `array_new`: `pattern_match.c` (×2) and `by_name_dispatch.c` (×1). Missing any one of
  those would have left an uninitialised id, which is worse than the address (garbage, not merely unstable).
- `tbl_key_str` now emits `\001d<typename>#<id>` (record), `\001l<id>` (list), `\001t<id>`/`\001S<id>`
  (table/set). Type name is included for records because SCRIP's key doubles as the EQUALITY key (`strcmp`),
  and canonical record ids are per-type so they collide across types.
- `%p` fallback retained for the still-unconverted types (cset, coexpr, proc). **Known residual, see below.**

### Verification (all measured post-fix)

- Repro: 5/5 runs identical for both record- and list-keyed tables; string-key order unchanged.
- **Full 17-module self-host run TWICE, per-module md5: 17/17 identical.** Class counts unchanged (513).
- Icon suite re-run: **PASS=250 FAIL=11 XFAIL=32** — matches the `GOAL-ICON-BB.md` baseline exactly.
- jtran was REGENERATED (not just relinked) because the fix changes `ARBLK_t`/`TBBLK_t` struct layout.
  `scrip --compile` 17 mods = 511,495 asm lines, 0 bombs.

### Residual (NOT fixed here, named so it is not lost)

`%p` still keys **cset, co-expression, and proc** descriptors. Canonical Icon hashes csets by their bits
(`rmisc.r` L244-252), procs by name string (L274-276), coexprs by `coexp_ser` id. Any program keying a table
by a cset or co-expression is STILL non-deterministic. Not exercised by jtran, so unmeasured — do not assume
it is harmless.

---

## SECOND DEFECT — rc=139 SEGV on 5 of 17 modules (diagnosed, NOT fixed)

`preprocessor`, `lexer`, `irgen`, `gen_bc`, `bytecode` exit **139 (SIGSEGV)** — while emitting COMPLETE,
oracle-count-matching, byte-reproducible output. s168's "17/17 parity" did not catch it because class-count
grading discards the exit code — **the harness blind spot RULES.md already warns about, recurring a layer
down. An exit code discarded is a failure graded as a pass.**

**NOT the s168 1 MB coexpr ceiling** — that fix is present and honored (`g_coexp_stksize = 67108864` confirmed
live in gdb at the moment of the crash).

gdb, thread 2 (a co-expression thread; main thread blocked on futex):
```
rt_gc_point_arr (arr=0x7fff92c000f0, n=2, r0=0x0) at gc_heap.c:383
 <- c_str_concat_d (string_ops.c:19)  <- n67248_binop_α   [frames beyond = 0x3 garbage]
=> 0x7ffff4a49fe0 <rt_gc_point_arr+19>:  mov %rdx,-0x28(%rbp)
RSP = 0x7fff92bffff0   RBP = 0x7fff92c00020
```
Faulting write `0x7fff92bffff8` is immediately below the page boundary `0x7fff92c00000` = **guard-page hit**.

⭐ **THE DISCRIMINATOR — MORE STACK DOES NOT MOVE THE CRASH ADDRESS.** At 8 MB and at 64 MB, RSP at fault is
byte-identical (`0x7fff92bffff0`) and the emitted output is byte-identical (49,343 bytes). This is NOT an
undersized stack. Under `ZC_COEXPR_STACK_GCHEAP=1` the stack is carved from the **bump allocator at a fixed
arena base**, so `lo` and the guard page land at the SAME address regardless of requested size — only the top
moves. (256 MB is WORSE — 0 classes; the gcheap carve fails outright.)

### ⛔ MECHANISM CORRECTED — IT IS NOT RECURSION. IT IS A ζ-GRANT LEAK. (measured, supersedes first draft)

An earlier draft of this finding said "runaway recursion." **That is FALSIFIED — do not cite it.** Measured by
dumping 400 KB of raw stack at the fault (`dump binary memory`) and histogramming it:

```
stack words dumped : 50,000      nonzero: 49,996
words in ANY code range (exe 0x400000-0x800000, so 0x7ffff4-f6): 3
```

**THREE return addresses in 400 KB.** A deep call chain would show tens of thousands. The stack is not frames —
it is bulk DATA. Autocorrelation gives a perfect 16-byte period (2,977 matches / 3,000 at stride 2 words):

```
+0064  0x0000000000000001   <- DESCR_t.v = DT_S
+0072  0x00007fff9664c220   <- string pointer, IDENTICAL every period
... repeating to the guard page
```

8 MB / 16 B ≈ **524,288 identical string descriptors**. `x/s` on that pointer: **`"\t\f "`** — the sorted
materialization of the cset `' \t\f'` (0x09, 0x0c, 0x20). Exactly three characters, so it is `lexer.icn`
**L248 `tab(many(' \t\f'))`**, NOT L72's four-character `' \t\f\r'`.

So the mechanism is a **re-succeeding loop whose per-iteration ζ grant is never released** — under the
`ZC_PORT_FORTH` default a grant spends as `sub rsp,K`, so each iteration marches RSP down 16 bytes until it
walks off the bottom of the window into the guard page. More stack only buys more iterations, which is exactly
why the fault address never moves. This is the `ARCH-ICON` ζ/FORTH carve discipline failing to give back on β.

**Related prior art (this is the same family, now with a concrete cset and site):**
`FINDING-2026-07-26-CLAUDE-ICN-SCAN-CONJ-BACKTRACK-DELTA-NOT-RESTORED-AND-ZETA-GRANT-LEAK.md` (the grant leak)
and `FINDING-2026-07-26-CLAUDE-ICN-SCAN-MATCH-BETA-RESUCCEEDS-INFINITE-BETA-LOOP-BLOCKS-JCON-SELFHOST.md`
(the β re-succeed). ⚠ The *linkage* to those two is still INFERRED; the stack evidence above is MEASURED.

### ⚠ NOT YET ISOLATED — two repros that DO NOT reproduce it (do not re-try these)

Both run CORRECTLY under `scrip --run`, so the defect needs more context than `tab(many(cset))` alone:
1. straight-line — `s ? { tab(many(' \t\f')); ... }` → correct, pos=4, terminates.
2. forced backtrack into tab's β — `s ? { tab(many(' \t\f')) & ="ZZZ" }` under both `if` and `every`
   → correctly takes ELSE / yields nothing / terminates.

The live case additionally sits **inside a co-expression** and inside `yylex`'s generator/`suspend` structure.
The next rung is to add the coexpr + suspend wrapper to repro 2, one ingredient at a time, in the s164
by-removal style — each ingredient's necessity measured, not assumed.

---

## SUGGESTED NEXT RUNGS

1. **Bracket the runaway.** Instrument a depth counter in the emitted-box prologue for the coexpr thread and
   dump the repeating box-id cycle; that names the β edge directly instead of inferring it.
2. **Grade the exit code.** Any JCON self-host harness must fail a module on rc != 0. A parity table that
   cannot see a SIGSEGV is not a parity table.
3. **Close the `%p` residual** (cset / coexpr / proc) against `rmisc.r` L244-276.
4. Only then attack byte-identity vs the oracle — it is now a well-posed question, which it was not before.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
