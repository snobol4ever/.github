# FINDING s172 (local seat `/home/claude5`, Claude Opus 5, queue row `beauty-m3-zls` = M1-R3) — **WALL-2 IS DOWN. IT WAS NEVER A DIRTY QUAD: `EVAL` HANDS BACK A PATTERN THAT LIVES INSIDE THE CHAIN'S OWN JIT BLOB, AND THE RETAIN BUDGET FREED THAT BLOB THE MOMENT THE `EVAL` RETURNED. BEAUTY-m3 NOW ANSWERS BYTE-FOR-BYTE WHAT BEAUTY-m4 ANSWERS.**

**Front:** GOAL-SNOBOL4-100 · M1-R3 (WALL-2 of FINDING-2026-08-19-s170). Pristine build (`make pristine`) at SCRIP `924cf16a`, corpus `6d7da37f`, oracle `x64/bin/sbl -bf`. Landed: SCRIP `src/runtime/runtime_eval.c` (13 lines, runtime-only — no codegen, no template, no `.s`). Witness minted: `corpus/probe/b2c/b2c_eval_pat_release.{sno,ref}`.

## THE ANSWER IN ONE LINE
`eval_string_transient` ends with `if (mark < EVAL_RETAIN_BUDGET) eval_cache_put(s, fn); else bb_pool_release(mark);` — and `mark` is `bb_pool_mark()`, **the whole BB pool's frontier, the program's own compiled code included**. So the predicate never asked *"how much has EVAL retained?"*; it asked *"is this program's code smaller than 2MB?"* **Beauty's m3 blobs seal at `0x202000` = 2,105,344 bytes — 8,192 bytes past the 2MB budget** — so EVERY `EVAL` in beauty-m3 took the release arm, `bb_pool_release` mprotect'ed the blob back to RW and rewound `pool_top` over it, and the pattern that `semantic.inc:16` had just assigned (`shift = EVAL("p . thx . *Shift('" t "', thx)")`) was dangling before the statement finished. The first Shift/Reduce match jumped into it. **m4 escaped for one reason only: its code lives in the ELF, not in the pool, so `mark` stayed near 0 and the identical chains were RETAINED.** The mode asymmetry was an accounting artifact.

## THE SIGNATURE, RE-READ (and one correction to the s170 census)
`SCRIP_NO_SEGV_HANDLER=1 gdb` on `printf 'START\n' | ./scrip beauty.sno`:
```
rip 0x7fffee202000   rax 0x7fffee202000   rdx 0x7fffae06db10 (a DTP; [rdx+0] == 0x7fffee202000)
info proc mappings:  0x7fffee000000-0x7fffee202000 r-xp   <- the SEALED slab
                     0x7fffee202000-0x7ffff2000000 rw-p   <- the released/unused pool tail
```
The faulting pc is **exactly `pool_top`**: page-aligned because `bb_alloc` page-aligns every blob start, and unexecutable because `bb_pool_release` mprotect'ed it `PROT_READ|PROT_WRITE`. `rax == rip == [DTP+0]` says the jump was the DEFER site's blob entry through the DTP's fn field — a released blob pointer, not a garbage quad.
⛔ **`#1 zls_g_region (…) at zeta_storage.c:936` IS NOT A CALLER.** `zls_g_region` is an EMIT-TIME function; what gdb printed is the quad at `[rsp]` — a **stale return address left in the driver's dirty stack**, which the unwinder renders as frame #1. It is a fingerprint OF the dirty spine, not evidence that a dirty quad was READ. The s170 census (and the B2/B2c class note it inherited) read that frame as the defect; it was the corpse of an earlier emit-time call.

## THE PROOF — ONE VARIABLE, SAME BINARY
The fix makes the budget a killswitch (`SCRIP_EVAL_RETAIN=<bytes>`, default = retain always):
| run | `SCRIP_EVAL_RETAIN` | result |
|---|---|---|
| beauty m3 `START` | default (retain) | `Parse Error` + raw echo `START`, **rc=0** |
| beauty m3 `START` | `2097152` (historic 2MB cliff) | **SIGSEGV rc=139** — the wall, reproduced exactly |
| beauty m3 `      X = 1` | default | `Parse Error` + raw echo, rc=0 |
| beauty m3 `* c` | either | `* c` (comments bypass the parser, unchanged) |
| beauty **m4** `START` | either | `Parse Error` + raw echo — **m4 is untouched by the change** |
**m3 ≡ m4 on beauty's tiny input for the first time.** WALL-2 no longer exists; what remains on that input is WALL-1 in both modes (queue row 4 `b1c-m4-seam`, seat6) — beauty's grammar still matches no statement, but it now fails the SAME way in both modes instead of crashing in one.

## THE CLASS IN 7 LINES — `corpus/probe/b2c/b2c_eval_pat_release.sno` (oracle `match`)
```
	DEFINE('F()')	:(Fe)
F	F = 'x'	:(RETURN)
Fe	P = EVAL("*F()")
	'x' P	:S(Y)F(N)
Y	OUTPUT = 'match'	:(END)
N	OUTPUT = 'nomatch'
END
```
`./scrip` → `match` (default and at `=2097152`, because this program's pool mark is far below 2MB) · `SCRIP_EVAL_RETAIN=0 ./scrip` → **SIGSEGV, same signature** (rip = page-aligned `pool_top`, `rax == rip`). The env arm is what makes the class visible in a 7-line program instead of a 2MB one: beauty needed no env because **its own code size crossed the cliff**.

## THE FIX (SCRIP, runtime only)
`eval_retain_budget()` — house killswitch idiom, `SCRIP_EVAL_RETAIN=<bytes>`; unset ⇒ `~(size_t)0` ⇒ the chain is always cached and its blob kept for the life of the process, which is exactly what every program under 2MB already received. `=2097152` restores the historic cliff verbatim; `=0` releases every chain (the class on demand). The now-dead `EVAL_RETAIN_BUDGET` macro is deleted (ONE AUTHORITY). The early `if (!fn) bb_pool_release(mark)` **stays** — a chain that failed to build is referenced by nothing.
**Bounding, honestly stated:** retention is not free. A program EVAL'ing very many DISTINCT strings now grows the pool (one page-aligned blob per distinct string; `bb_pool_trim_last` already trims each 4MB reservation to its used pages) against the 64MB `BB_POOL_SIZE` reserve. At exhaustion `bb_alloc` returns NULL → `eval_build_chain` returns NULL → **the EVAL fails cleanly** instead of jumping into freed pages. That is a strictly better failure than the one this rung removes, and the killswitch restores the old economy for anyone who measures a need.

## BLAST RADIUS — MEASURED, BOTH ARMS, SAME BINARY
- `bash scripts/test_corpus_snobol4.sh`, default vs `SCRIP_EVAL_RETAIN=2097152`: **output byte-identical** (diff empty). m3 PASS=326 FAIL=11 · m4 PASS=322 FAIL=13 SKIP=2 (337 programs).
- `beauty_suite` m3, all 17 drivers, both arms: **17/17 PASS both** (matches the s171 census; m3 suite debt stays ZERO).
- By-set m3 board over **884 programs** (`crosscheck` + `probe` + `feat` + `smoke`), both arms, same binary: **787 PASS / 53 FAIL in BOTH arms — zero regressions, zero repairs, pass-sets identical.** The fail sets differ on exactly ONE row and only in crash FLAVOUR: `probe/m1/m1_arbno_capture_call_bracket` rc=132 (SIGILL) new vs rc=139 (SIGSEGV) old — the witness s169 already recorded as alternating SIG4/SIG11 in BOTH arms across runs, i.e. known noise on an already-red row, not a mover. ⛔ Run with one process per arm (⛔ a first attempt was VOID: a `&`-backgrounded board survived its tool call and a second copy appended to the same files, minting 130 phantom "repairs"; **backgrounded jobs in this container are not reliably dead, and two writers on one output file is a false board** — the RULES "counts do not transfer" law with a new face).
- `.s` blast radius: **structurally zero** — the change is in `src/runtime/runtime_eval.c`'s EVAL retention only; no emitter, template, `x86_asm.h`, or lowerer file is touched, and no emission path reads the budget.

## WHAT THIS DOES NOT CLAIM
1. **WALL-1 is untouched and still owns beauty** (row 4, seat6): both modes now say `Parse Error` on the first real statement. The 7-line witness above ALSO SEGVs in **m4** under every retention arm — that is the m4-seam class, not this one, and it is routed there.
2. **The B2c "dirty-quad carve-zeroing" hypothesis is falsified as the explanation of beauty's m3 wall.** The m3 dirty stack is real — it is what made the backtrace lie — but no dirty quad was read: the DTP field the DEFER site jumped through was written correctly, with the address of a blob that had been freed underneath it.
3. This says nothing about WALL-3 (`b1c-retreat`, row 5) or the two m4 suite reds of s171.
