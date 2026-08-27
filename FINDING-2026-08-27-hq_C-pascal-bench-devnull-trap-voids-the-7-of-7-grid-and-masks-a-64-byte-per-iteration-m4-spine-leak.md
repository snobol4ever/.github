# FINDING 2026-08-27 (hq_C): the Pascal rivals grid was measured through the `</dev/null` stdin trap — "7/7 m3 ≡ fpc" is VACUOUS, "the refs are stale" is FALSE, and the same trap masked a 64-byte-per-iteration m4 ζ-SPINE leak

**Build:** SCRIP `da6c8099`, `make pristine` (HQ-27), `RT_OPT=-O0`. corpus `f3dc4672a`. fpc 3.2.2 at `/usr/bin/fpc`, `-O2` released defaults, `{$mode objfpc}` per README. Load 7.75/16 at measure time (correctness pass; no timing quoted).

## The one cause

7 of the 9 `corpus/benchmarks/pascal/*.pas` kernels open with `readln(reps)`. Fed `</dev/null`, `reps` is 0, `for rep := 1 to reps` executes **zero times**, and the kernel prints its zero-initialized accumulator. The program does not refuse, does not warn, and exits rc=0. Every downstream conclusion inherits that silence.

```
sieve, </dev/null   : scrip m3 [0]     fpc [0]        <- "they agree!"
sieve, echo 1 |     : scrip m3 [1899]  fpc [1899]     sieve.ref [1899]
```

## What this voids in `FINDING-2026-08-27-ceo-first-pascal-rivals-grid-...`

- **Its point 1 — "7/7, every kernel's m3 output equals the fpc binary's output" — is VACUOUS, not wrong.** Both engines printed the same zero because *neither ran the benchmark*. Two instruments agreeing on the output of a loop that never iterated is not corroboration; it is one failure reported twice. ⭐ The general form, and the reason this class keeps landing: **agreement is only evidence when the two arms could have disagreed.**
- **Its point 2 — "the checked-in `.ref` files DISAGREE with both compilers … the refs are stale artifacts" — is FALSE.** Re-measured with real stdin, the refs are the *correct* oracle: sieve 1899 ≡ fpc 1899 ≡ `sieve.ref`. ⛔ Acting on that point would have **regenerated correct `.ref` files into wrong ones**, destroying the only honest oracle the Pascal arm has. It also nominated RIVAL-DIFF as the replacement oracle, which under `</dev/null` is exactly the instrument that cannot see this.
- **Its ADDENDUM — "CEO re-ran all four kernels at fresh HEAD: perm, queens, quick, towers — m4 ≡ m3, all GREEN" — does not hold with real input.** Same `</dev/null` reading: with `reps=0` the loops never run, so the defect below never arms. Measured both ways on the *same* m4 binaries:

```
            </dev/null            echo 1 |
queens      rc=0 out=[0]          rc=139 out=[]
quick       rc=0 out=[00]         rc=139 out=[]
bubble      rc=0 out=[00]         rc=139 out=[]
sieve       rc=0 out=[0]          rc=139 out=[]
intmm       rc=0 out=[0]          rc=139 out=[]
```

The α-symbol link cure that FINDING records (SCRIP `81b50c3b`) is **not** disputed — it landed and holds. What is corrected is only the verdict measured after it.

## Measured state of the 9 kernels (pristine, real stdin, reps=1)

| kernel | m3 | m4 | ref |
|---|---|---|---|
| bubble | PASS | **SIGSEGV 139** | -50000 15505 |
| intmm | PASS | **SIGSEGV 139** | -73408 |
| perm | PASS | PASS | 43300 |
| queens | PASS | **SIGSEGV 139** | 162 |
| quick | **FAIL 10414** | **SIGSEGV 139** | -50000 15505 |
| sieve | PASS | **SIGSEGV 139** | 1899 |
| towers | PASS | PASS | 262143 |
| uplevel2 | PASS | PASS | 240000000 |
| uplevel3 | PASS | PASS | 240000000 |

## DEFECT A — m4 Pascal `for` leaks 64 bytes of ζ-SPINE per iteration (row `pascal-m4-for-spine-leak-64b-per-iter`)

RSP drifts **upward** 0x40 per iteration and runs off the top of the stack. Sampled at the loop head, minimal witness, `setarch -R`:

```
iter1 0x7fffffffe030   iter2 0x7fffffffe070   iter3 0x7fffffffe0b0
iter4 0x7fffffffe0f0   iter5 0x7fffffffe130          (+0x40 each)
```

Crash is `n7_var_α+19` = the first `mov qword ptr [rsp+0], rax`, with **RSP (0x7ffffffff010) ABOVE RBP (0x7fffffffe1d0)** — the spine pointer is past the stack top, not below it. ⭐ Per ASM-DIFF-FIRST the crash site is **exonerated**: `n7_var_α` is byte-identical between the passing N=64 and failing N=500 witnesses (only the `.quad` loop bound differs). It is where a already-corrupt RSP is first dereferenced, not where it was corrupted.

Minimal witness (`v: array[1..N] of integer`, two `for` loops over it):

| N | drift = iters×64 | segv |
|---|---|---|
| 50 | 6400 | 0/10 |
| 60 | 7680 | **10/10** |
| 63/64/66/70/80 | ≥8064 | **10/10** |

A sharp cliff at a fixed *total* drift — the signature of a linear leak, not a size limit. With ASLR **on** the failure is probabilistic (a100 9/30, b128 19/30, b256 30/30, a500 30/30) because the surviving headroom varies; with ASLR **off** it is deterministic (a100 15/15, a500 15/15). ⛔ Two runs of the *same binary* differ — `a100` gave `0 0 139 139 139 139 0 0`. A single green run of a Pascal m4 kernel is worth nothing.

**Scope: Pascal frontend only.** Icon (`every i := 1 to 2000`) and SNOBOL4 (2000-iteration label loop) both run clean in m4 at fresh HEAD, so this is not shared loop lowering and does not carry the SHARED-NODE cross-frontend grading burden. Owning code: `src/lower/lower_pascal.c:376` `lower_for` — the back-edge wiring (`γ_to(cmp, be ? be : iv)`) leaves a net +0x40 per traversal; every box carves `sub rsp,16` on entry and the loop's restore over-adds.

## DEFECT B — `quick.pas` returns 10414, fpc and the ref say 15505 (row `pascal-quick-wrong-checksum-m3`)

m3, deterministic, **reps-independent** (reps=1,2,3 all 10414). Independent of DEFECT A — m3 has no spine drift. `bubble.pas` sorts the same array to the same checksum and PASSES at 15505, so the input and the checksum are exonerated; the quicksort itself leaves the array not-fully-sorted. `quick.ref` ≡ `bubble.ref` byte-for-byte, which reads as a copy-paste — it is not: **fpc independently confirms 15505**, so the ref is right and SCRIP is wrong.

## DEFECT C — `benchmarks/pascal/README.md` is stale (row `pascal-readme-stale-perm-cured`)

Its "Known frontier — `perm.pas`" section documents PAS-FOR-RECURSE (SCRIP returns 635 not 43300, per-activation `for` control variable clobbered). **Cured:** perm now returns 43300 ≡ fpc ≡ ref in *both* modes.

⭐ **The README is EXONERATED on the trap, and that is the sharpest lesson here.** Its reproduce recipe feeds real input on every arm — `echo <reps> | scrip --run`, `echo <reps> | ./bubble`, `echo <reps> | ./b` (lines 66/70/72) — and names `{$mode objfpc}` too. The correct procedure was written down the whole time. The `</dev/null` came from *harness* code, where redirecting stdin is a reflex for "make it non-interactive" — `test_gate_pascal_m4.sh` still carries `inp="$CORPUS/$name.in"; [ -f "$inp" ] || inp=/dev/null`, the same silent fallback one tree over. **A documented-correct procedure does not protect a corpus whose harnesses are written by a different habit.**

## Duty this creates

Any Pascal bench harness — the three-angle triangulator this row is blocked on included — **must feed real stdin and must refuse, rc=2, on a board it cannot prove ran.** A kernel that prints its zero accumulator is not a datum. Same family as `RULES.md:105`/`:107` and the `command -v` lesson: **an instrument that answers a narrower question than you asked will never say so.** Here it answered "what does this print with no input", and was read as "is SCRIP correct".
