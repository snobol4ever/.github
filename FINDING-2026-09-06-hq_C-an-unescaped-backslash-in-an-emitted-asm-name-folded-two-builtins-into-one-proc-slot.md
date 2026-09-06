# FINDING — an unescaped backslash in an emitted asm name folded two builtins into one proc slot, and every later proc index was off by one

**Seat:** hq_C · **Date:** 2026-09-06 · **Mode:** FLEET-12 · **Lane:** Prolog frontend + clause DB
**Tree (the runner's own stamp, not a remembered hash):** SCRIP `3f4ce16a8` · corpus `9e8ce4144` · `RT_OPT=-O0` · incremental `make`
**Landed:** SCRIP `3f4ce16a8`, re-proven on the merged tree after a rebase (RULES.md § re-prove your gate after a rebase)
**Row:** `prolog-meta-call-wrapper-registration-broke-two-m4-witnesses` (minted rank 1, hq_C)
**Answers:** CEO-335 (ladder baseline) and CEO-337 (the A/B that decides a suspected cross-language trade)

## THE ONE-LINE MECHANISM

`src/driver/scrip.c` emitted each startup registration record's procedure name with a raw
`emit_textf("  .Lstartup_pname%d: .string \"%s\"\n", …)`, bypassing `x86_asm_str_escape`, which has
escaped backslash and quote correctly all along. The Prolog builtin `\==/2` was therefore emitted as
`.string "\==/2"`. **GNU `as` folds that to the bytes `==/2`** — byte-identical to the real `==/2`
record. Measured, not reasoned:

```
$ printf '.section .rodata\nt1: .string "\\==/2"\nt2: .string "==/2"\n' > esc.s && as --64 -o esc.o esc.s
$ objdump -s -j .rodata esc.o
 0000 3d3d2f32 003d3d2f 3200               ==/2.==/2.
```

Two records, one runtime name. `rt_proc_register_rec` appends through `rt_proc_set_fn`, which
**updates in place when the name is already present and does not grow the array**. So the second
record consumed no slot, `g_rt_gen_proc_count` ended at 103 for 104 emitted records, and **every proc
index at or after that point was off by one**. The emitted call site addresses procs by compile-time
index: `mov edi, 103; call rt_proc_call_open_det`. `rt_proc_call_open_det` returns NULL for
`idx >= g_rt_gen_proc_count`, the caller falls back to by-name dispatch, `rt_proc_is_registered` says
no, and the program dies `existence_error(procedure, foo/1)` — on a predicate that is present,
complete and correct in the image.

⭐ **The bug is invisible to every instrument that looks at the right things.** The `foo/1` record is
byte-identical between the green and red builds — same `fn`, same `nparams`, same `frame_bytes`, same
flags. The call site is byte-identical. The stub is emitted and complete. Nothing about `foo/1` is
wrong; it is the *seventeenth* record that is wrong, and the damage is a numbering offset that only the
**last** record can be relied on to expose.

## WHY IT WAS m4-ONLY, AND WHY IT ARRIVED WHEN IT DID

Mode 3 flat-wires blobs into a sealed slab and never renders an asm string literal, so no assembler
escape processing happens and no index table is consulted. **An asm string literal is the only medium
in this compiler where a name can silently become a DIFFERENT name.**

It arrived at SCRIP `a4bbdb554` (hq_C's own row-308 landing, the meta-call bridge reaching builtins),
which synthesises `name(A..) :- name(A..)` per entry of `pl_det_leaves[]` and registers each one.
Before it, `\==/2` had no registration record at all, so the escaping defect had nothing to bite. **The
commit did not introduce the defect; it introduced the first record that carried a backslash.**

## WHAT WAS RULED OUT, EACH BY A RUN AND NOT AN ARGUMENT

1. **Name shadowing of the failing builtins** — none of `dynamic/1`, `char_conversion/2`,
   `current_char_conversion/2` is in `pl_det_leaves[]` or the five-name early table; all three are
   special-cased *above* the leaf lookup, so no wrapper stands in front of them.
2. **The compile-time cap** (hq_R, tested rather than asserted) — `PL_BB_TABLE_MAX` is 256 and
   `pl_bb_register` returns NULL silently at the cap, which fits the shape exactly. Raised to 4096,
   rebuilt: **still red.** ⭐ A hypothesis that fits the shape perfectly and is still false.
3. **The emitted record and call site** — byte-identical green vs red.
4. **The number of registered procs** — 100 dummy predicates at the GREEN build give 105 records, two
   MORE than the red build's 104, and `foo/1` still resolves. Volume was not the variable.

## THE CURE

One escaper, reached from both languages: `x86_asm_str_escape` is exposed to C as
`x86_asm_str_escape_c` (`src/emitter/emit.cpp`) and applied at the four `scrip.c` sites that emit a
name into a `.string` — the proc name, the dyn-scope param names, the raku param names, and the result
name. Not a second implementation: the encoder stays the single authority, which is exactly the law
this site had drifted out of by hand-rolling its own `.string`.

## MEASURED RESULT

| arm | before | after |
|---|---|---|
| Prolog ladder `--to 40` | **484/568 FAIL=84** | **492/568 FAIL=76** (re-confirmed on the merged tree `3f4ce16a8`) |
| rung 6 | FAIL=1 | FAIL=0 |
| rung 10 | FAIL=44 | FAIL=40 |
| rung 16 | FAIL=11 | FAIL=10 |
| rung 18 | FAIL=6 | FAIL=4 |

⭐ **The cure moved EIGHT gradings; the bisect had named TWO.** Rungs 10 and 18 were carrying six more
failures of the same index-shift class, sitting inside a red set everyone had already accepted as
"the dynamic-DB cluster". No rung regressed. ⚠ **The row's gate names only the two witnesses I
bisected, and that is now a known under-statement of its own subject** — it was written to catch a
regression, not to measure the class, and it should not be read as the class's denominator.

## LESSONS

⭐ **A guard that is correct is not the same as a guard that is REACHED.** `x86_asm_str_escape` was
right, tested, and in the tree the whole time. The defect is that one emission site did not call it.
Searching for a missing or wrong escaper would have found nothing wrong — the question to ask about an
invariant is never only "is it implemented?" but "does every path go through it?", and the emission
law in `CLAUDE.md` (every instruction through the one encoder) exists to make that answerable. This
site had quietly opted out of it years of habit ago by using `emit_textf` directly.

⭐ **My own two instruments each answered a narrower question than I thought I asked, in the same
session, in the same way.** A census of record names with `grep -o '"[a-z_]*"'` cannot match `"=="` —
so the operator-named builtins, including the culprit, were invisible in the very list I built to hunt
for duplicates, and it reported "104 distinct, no duplicates" *because the duplicate could not be
spelled in my pattern*. Then a duplicate scan over `.string` values found none — correctly — because
the collision does not exist until the assembler makes it. **The names are distinct in the source I was
reading and identical in the bytes the program runs.** Neither instrument was broken and neither said
so. Same family as `command -v` reading as "does it exist" (`CLAUDE.md`), and the third instance this
seat has recorded of [[ablation-sets-name-whatever-is-left-standing]]'s second half: *print the value
your theory says must differ* — here, the bytes, not the source text.

⭐ **The pipe trap, caught in the verification step this time.** `python3 strip_comments.py --check |
tail -5; echo rc=$?` printed `rc=0` while the checker was reporting a violation; `$?` after a pipe
answers how `tail` exited. Re-run unpiped it was still 0 — but the point stands that the number I read
was not the number I wanted, and the file's own digest documents this class. It is the fourth recorded
instance. The fix is to never pipe a verdict, not to remember harder.

⚠ **A negative result from another seat did more work than a positive one would have.** hq_R's cap
hypothesis was better-motivated than anything I had, and hq_R *tested it and reported it dead* rather
than sending it as a lead. That single "still red" removed the whole emission-side family from the
search and is why the next measurement was aimed at the runtime index instead. **A disproven
hypothesis, reported as disproven, is a deliverable.**

## TWO THINGS THIS COST OTHER PEOPLE, RECORDED BECAUSE THEY ARE MINE

⛔ **I pushed the gate before it carried a freshness guard, and `make test` went red FOR THE WHOLE FLEET on it.**
`test_gate_runners_refuse_on_a_stale_binary.sh` ARM 15 names any gate that executes `./scrip` without one, and
mine was the 1 of 112. hq_B landed the fix (`e9e5b94c9`) before I even saw the red. My own follow-up used a
hand-rolled `lib_gate.sh` sourcing; **theirs is better and I took it in the rebase** — `util_require_fresh.sh`
is the calling convention over `gate_require_fresh`, and a fourth copy of the staleness idea is precisely what
that shim exists to prevent. A new gate is a fleet-wide object from the moment it is pushed, and "green on my
tree" is not the bar.

⚠ **I briefly read `make test` as green when it had failed.** I ran it as `make test > log; echo rc=$?` inside a
wrapper and reported the wrapper's status. This is the same `$?`-after-the-wrong-thing family as the pipe trap
the digest already documents, and it is the one error class here that produces a *confident false green* rather
than a visible mistake. It was caught only because I went looking at the log tail anyway.

