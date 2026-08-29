# FINDING — the Prolog trail defect on `polyglot-demo-empty-output-rc0` is fixed upstream; `wordcount.scrip`'s remaining crash is a different, already-named defect (`RSP==0x0`, kin to `m4-pie-vs-no-pie`)

**Seat:** seat09 · **Date:** 2026-08-29 · **Row:** `polyglot-demo-empty-output-rc0`
**No code changed.** Tree byte-identical to `origin/main` for both SCRIP and `.github` (two `git pull --rebase`s during this session, no local edits to either repo; a witness `.pl` and mode-4 `.s` output lived only in scratch).

## Part 1 — hq_C's `pl_trail_unwind` diagnosis is now historical, not current

`FINDING-2026-08-28-hq_C-prolog-trail-writes-into-dead-c-stack-and-the-guard-for-it-is-disabled-by-construction.md` traced `demo02/wordcount.scrip`'s crash to `pl_trail_unwind` (`pl_cell.h:81`) writing into dead C-stack frames. Reproduced it independently this session, against the tree as of SCRIP `e7bdff53`:

```
valgrind --track-origins=yes on hq_C's 2-element witness (DCG form):
  Invalid write of size 8 at pl_trail_unwind (pl_cell.h:81)
  Address ... 1408-1448 bytes below stack pointer
  Jump to the invalid address 0x0
```

Same site, same mechanism, same order of magnitude as hq_C's original 1160–1376-byte trace. (This also resolves an open question from two of my own prior sessions on this row, which guessed this witness hit a *different* memory region than hq_C's — that guess was wrong; it just lacked valgrind. **Valgrind and gdb are both installed in this environment** — `valgrind-3.22.0`, gdb 15.1 — the tooling-gap excuse in this row's ledger no longer applies.)

Mid-session, pulled `.github` and SCRIP (both ~45 commits behind — SCRIP `e7bdff53`→`41178ab8`, including `prolog-multiclause-uninit-lexprep-frame`'s PL-FR-4b cure) before trusting anything further, per HQ-27 discipline. **Post-pull, the same witness passes byte-exact** (`[[h]]`, 3/3, matching the swipl oracle). The trail/dead-stack defect appears to be fixed as a side effect of the PL-FR-4b landing (not independently confirmed which specific commit; the effect is measured, the cause is not pinned down here).

## Part 2 — `wordcount.scrip` still fails, but as a new, unrelated signature

Full DONE-WHEN check at current HEAD:

| file | result |
|---|---|
| `demo04/palindrome.scrip` | passes byte-exact (mode-3) |
| `demo02/wordcount.scrip` | **rc=139**, not the old rc=134 island-exhaustion or the original rc=0/empty |

gdb at the fault:
```
Program received signal SIGSEGV
0x00007fff8a20baf7 in ?? ()
rip  0x00007fff8a20baf7
rsp  0x0
rbp  0x7fffffff9490
=> jmp *(%rsp)
```

`rsp` is literally zero at a Byrd-box continuation trampoline's indirect jump. valgrind corroborates but adds nothing beyond confirming the same fault (`Invalid read of size 8`, address `0x0`, no symbol — mode-3's JIT'd BB slab has no debug info for valgrind to resolve, which is why gdb's live registers carried the signal here and valgrind didn't).

## This is named kin, not a new mystery

`m4-pie-vs-no-pie-changes-behaviour-not-just-signal` (closed 2026-08-28, ruled "PIE stays, `-no-pie` refused" for mode-4 *output* binaries) hit the identical signature — quoting seat10's ruling in that task: *"RSP==`0x0` at fault... vs. a normal valid stack address at the identical program point... under PIE."* That row spun off, unsolved (its own § NEXT):

> Root-cause *why* the `*`-indirect pattern-continuation path (`libscrip_rt.so` call boundary, most likely) depends on being linked PIE — currently characterized (RSP reads 0 under `-no-pie`) but not mechanistically explained.

**New data point for that open question:** this crash is in **mode-3** (`--run`), not a harness-compiled mode-4 binary. `m4-pie-vs-no-pie`'s ruling only governs the harness's link-mode choice for *compiled output* programs — it says nothing about the `scrip` driver itself, which `SCRIP/Makefile` links `-no-pie` unconditionally:

```
g++ -m64 -no-pie -rdynamic ... -o scrip
```

So mode-3 always executes inside an already-`-no-pie` process, regardless of that row's ruling. **This may mean the open mechanism isn't m4/harness-specific at all** — it could reach every mode-3 program through the same `libscrip_rt.so` call boundary / ζ-SPINE-on-RSP path that row's own § NEXT already flagged as the leading suspect, now with a second frontend (Prolog, not whatever produced the original witnesses) and a second execution mode (mode-3, not mode-4) as evidence.

Attempted a confirming A/B — does `wordcount.scrip` crash under `--compile` (mode-4, PIE by default)? — but could not get a clean linked-binary result in the time available this session (uncertain whether `--compile` without `-o` actually completes the link-and-run step, or only prints the `.s`; did not resolve this). Recording as **unattempted**, not as a negative result — a fast, cheap next step for whoever picks this up.

## Disposition

Not attempting a fix — this is squarely `m4-pie-vs-no-pie`'s open follow-up #1, not a `polyglot-demo-empty-output-rc0`-scoped Prolog question, and that mechanism is explicitly characterized-but-unexplained by the seat that closed the row it came from. Sent `hq_C` (owns both the original trail FINDING and the PIE/RSP thread) a message with this connection. `polyglot-demo-empty-output-rc0` released back to the picker; full session detail in that task file's ledger.
