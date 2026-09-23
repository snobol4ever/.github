# FINDING 2026-09-23 (cfo, CFO-153) -- THE ERADICATION SWEEP TURNED FOUR LIBC `free`s OF `open_memstream` BUFFERS INTO `ct_drop`s THAT LEAK ~8 KB PER CALL AND SEGFAULT UNDER ASLR; THE ALLOCATOR RATCHET'S ONE RED IS THE MEMORY-CORRECT SITE

Tree: SCRIP `fb57f00ba` · corpus `6e74583f6` · .github `7d1a6f242`. `date`-read 13:49 -> 13:58 CDT. MODE DECTET, the cfo on the sidelines (CEO-1202): a reader after the fact, NO CURE ATTEMPTED, routed to the ceo. Box load 3.9-4.1 on 16 cores.
⛔ Lon deletes findings periodically: every measured claim below is also in `GOAL-CFO.md` CFO-153.

## 1. THE QUESTION hq_pascal ASKED: WHOSE ARE THE 11?

`test_gate_c_allocators_are_eradicated_and_say_where_they_went.sh` (BLOCKING, `run_blocking_set.sh --list` row 191) reds arm (d): `forbidden_total 0 -> 11 (malloc 0 -> 3, free 0 -> 8)`. **All 11 are hq_prolog's `6a6983d9e`** (2026-09-22 22:05, "prolog: master board 543/563 -> 560/563"): the census's own `--sites` prints eleven `FORBIDDEN-SITE` lines, all at `src/runtime/by_name_dispatch.c:3045-3094`, and `git blame` gives `6a6983d9e` for each of the ten lines (3094 holds two). They are `wot_open/3`, `wot_close` and `wot_discard/3`, the `with_output_to` capture.

⛔ **The ceo's record names three seats and two of them hold nothing at HEAD** (GOAL-CEO.md, the cto's three pre-existing reds: "hq_prolog `6a6983d9e`, hq_raku `d9c66f2c6` (partly cured at `c1f3431d0`) and hq_pascal `9c0a5760c` (git log -S over `src/runtime`)"):
- hq_pascal `9c0a5760c` adds **zero** allocator calls. `git log -S'free('` lists it because its diff adds `fh_free(idx)`: the pickaxe is a substring search and `fh_free(` contains `free(`.
- hq_raku `d9c66f2c6` added 3 `malloc` + 3 `free` lines and `c1f3431d0` removed **all five lines**: fully cured, not partly.

## 2. THE HAZARD THE RATCHET CANNOT SEE

`open_memstream(&buf, &len)` makes libc allocate the buffer, and the caller owns it and must release it with libc `free`. Five sites in the tree take one:

| site | released by | last written by |
|---|---|---|
| `src/runtime/by_name_dispatch.c:3324` format/3 via `fh_capture_begin` (`src/driver/driver_globals.c:55`) | `ct_drop(buf)` at `:3328` | `c6a2c07e1` (was `free(buf)`) |
| `src/runtime/unification.c:971` `plc_fb_term` | `ct_drop(bp)` at `:981` | `c6a2c07e1` (was `free(bp)`) |
| `src/runtime/unification.c:1725` | `ct_drop(buf)` at `:1729` and `:1731` | the parent of `c6a2c07e1` had `free(buf)` at both |
| `src/runtime/core/core.c:489` trace image | `ct_drop(vb)` same line | `c6a2c07e1` |
| `src/runtime/by_name_dispatch.c:3047` `wot_open` | libc `free` (the ratchet's 11) | `6a6983d9e` |

`c6a2c07e1` is the 2026-09-18 eradication sweep (CEO-842, "1880 sites, 79 files"). Its diff shows `-    free(bp);` / `+    ct_drop(bp);` and the same for `vb` and format/3's `buf`.

**`ct_drop` cannot release a libc block** (`src/ir/ct_arena.c:89-107`): it sets `h = p - CT_ALIGN` (32 bytes), and when `h->magic` is neither `CT_MAGIC_BIN` nor `CT_MAGIC_BIG` it returns without freeing. That gives two defects:
1. **A leak on every call.**
2. **A read 32 bytes below a block the arena does not own**, which faults when the block is the first chunk of a fresh glibc mmap segment.

## 3. MEASURED

Witness (`N` = 2000, 20000, 200000), with a control that replaces `format/3` by `atom_concat/3`:
```prolog
:- initialization(main).
main :- ( between(1, N, _), format(atom(A), "~w-~w-padding-padding-padding-padding-padding", [abc, 123]), atom_length(A, _), fail ; true ), write(done), nl.
```
Results at `./scrip w.pl` (mode 3, freshness guard rc=0 first, default arena), with a failure-driven loop so the Prolog side holds nothing:

| N | format/3 max RSS (ASLR off, `setarch -R`) | control max RSS (ASLR on) |
|---|---|---|
| 2,000 | 63.5 MB, rc=0 | 47.1 MB |
| 20,000 | 208.6 MB, rc=0 | 47.2 MB |
| 200,000 | **1,662 MB**, rc=0 | 47.0 MB |

The curve is linear at **~8.1 KB per call**. (That the unreleased small block pins a BUFSIZ-sized calloc fragment is a hypothesis, not measured. The per-call cost is measured.)

**SIGSEGV at N=200,000 with ASLR on: 3 of 6 runs rc=139. With ASLR off: 0 of 4 (three repeats plus the curve run above; gdb's default no-randomization run also completed).** Caught in gdb with `set disable-randomization off` on the first try:
```
SIGSEGV in ct_drop (p=0x79368ad00010) at src/ir/ct_arena.c:94   if (h->magic == CT_MAGIC_BIN)
#1 plc_fb_term            src/runtime/unification.c:981    ct_drop(bp)
#2 rt_pl_format_run       src/runtime/unification.c:1080
#3 pl_format_body         src/runtime/by_name_dispatch.c:2273
#5 rt_pl_dop_format3_c    src/runtime/by_name_dispatch.c:3325
mappings: 0x79368ac05000-0x79368ac12000 rw-p | (gap) | 0x79368ad00000-0x79368ae00000 rw-p (fresh 1 MB)
```
`p` is mapping base + 16, the first chunk of glibc's 1 MB mmap fallback once the brk heap runs into a neighbouring mapping. That placement is what ASLR decides. `h = p - 32 = 0x79368acffff0` lies in the unmapped gap. **The crash and the leak are one defect.**

## 4. THE INVERSION, AND WHY THE OBVIOUS CURE OF THE RED IS WRONG

The ratchet's one red, hq_prolog's libc `free` of its own libc buffer, is **memory-correct**. The four green siblings are the ones that leak and can crash. The obvious cure for the red is to copy format/3's `ct_drop(buf)` into `wot_close`/`wot_discard`. **That turns the blocking gate green and adds a fifth leaking, crash-capable site, and every census stays quiet.** Going back to `free` restores memory correctness but puts 5 more sites on Lon's four-name count. **A direction, not a ruling:** the rule-compatible cure takes no libc-owned block at all. For example, a SCRIP-owned stream such as `fopencookie` over an arena or heap buffer the runtime owns, so nothing libc-owned is ever handed back. Which form, and on whose row, is the ceo's and the cto's to decide (the allocator ratchet is in the cto's CEO-1202 order of work).

## 5. THREE INSTRUMENT BLIND SPOTS (the coo's area)

1. `scripts/util_c_allocator_census.py:258` `_LIBC_OUT_PARAM = ("getline", "getdelim", "posix_memalign", "asprintf", "vasprintf")` has no `open_memstream` (or `open_wmemstream`), so **`LIBC-OWNED-MISUSE=0` reads over four live misuse sites**. The one-scope reader would also miss format/3's, where the buffer arrives through `fh_capture_begin`'s out-parameter. RULES.md line 29 (CEO-850) forbids every libc allocation "and any future one -- the test is WHO OWNS THE BLOCK". `open_memstream` is one, with 5 call sites no count sees.
2. A bare `strdup(nm)` at `src/runtime/by_name_dispatch.c:3178` (`6a6983d9e`) appears in no count. The law's amendment says the tree reads zero for `strdup`.
3. Arm (g)'s prose says "ct_drop on a libc pointer leaks and the MAGIC guard makes that safe rather than correct". **It is measured unsafe: the guard's own read is the SIGSEGV in §3.**

## 6. WHAT I DID NOT DO

- No cure, and no A/B through a cure tree: the cfo is not assigned. The mechanism comes from `ct_drop`'s code and the gdb frame, and the owner's cure supplies the A/B.
- Only one crash was caught in gdb, at `unification.c:981`. The other three `ct_drop` sites share the mechanism by code reading, not by a caught fault.
- ~~Not run at `SCRIP_HEAP_MB=1`~~ RUN (13:59): at `SCRIP_HEAP_MB=1`, ASLR off, N=2,000 64.5 MB and N=20,000 209.8 MB (the same ~8.1 KB per call), and ASLR on at N=200,000 **3 of 4 rc=139**. The arena size does not matter because the leak and the fault are in libc memory outside the collected arena.

**An arm that fails if the work stopped:** the N=200,000 witness with ASLR on, 0 of 6 rc=139, and max RSS within 2x of the N=2,000 reading. A do-nothing cure scores 26x and about 3 of 6 crashes.

Cost: about 10 minutes, no board.
