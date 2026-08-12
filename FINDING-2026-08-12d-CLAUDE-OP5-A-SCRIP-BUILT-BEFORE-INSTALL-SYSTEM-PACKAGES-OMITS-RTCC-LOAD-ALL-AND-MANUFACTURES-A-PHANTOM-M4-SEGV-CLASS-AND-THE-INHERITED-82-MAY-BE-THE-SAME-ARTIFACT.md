# FINDING 2026-08-12d — CLAUDE-OP5 — **A `scrip` BUILT BEFORE `install_system_packages.sh` SILENTLY OMITS `call rtcc_load_all@PLT` AND MANUFACTURES A WHOLE-CORPUS PHANTOM m4 SEGV CLASS. I PUBLISHED THAT PHANTOM AS A ROOT CAUSE AND RETRACTED IT. THE INHERITED 82/122 MAY BE THE SAME ARTIFACT.**

**Fingerprint:** SCRIP `52545cbf` (= s32's `fc5b0754` + census script only; **zero compiler bytes, mine included**) · corpus `c91d1adf` · `.github` `ede9f243`.

---

## ⛔⭐⭐⭐ THE HEADLINE IS A RETRACTION OF MY OWN WORK — READ IT BEFORE THE EVIDENCE

I built the tree **without running `scripts/install_system_packages.sh`** (REPO-SCRIP.md session-start line 1; I skipped it knowingly and said so). `make scrip` succeeded, **zero errors**, and produced a working compiler — `--run` green across the board. But that binary **silently omits one line from the mode-4 preamble: `call rtcc_load_all@PLT`.** That call establishes the RTCC register set including **r9, the GVA base**. Without it every `mov [r9+0], rax` GVA-slot write dereferences garbage.

**Result: an apparently catastrophic, apparently well-evidenced mode-4 crash class that does not exist.** I measured it at `163 programs / 161 m4 SEGV / BUILDFAIL=0`, convicted the faulting instruction in gdb, isolated it to a bare-literal minimal reproducer, and **proved causation end-to-end** by patching emitted text (establish r9 + add the missing veneer save) and watching five programs across four families flip from `rc=139` to `rc=0` byte-matching m3 and their pinned `.ref`. **Every one of those observations was real. The conclusion drawn from them was wrong.**

## WHAT ACTUALLY SETTLED IT — TWO mtimes

```
scrip mtime  2026-08-12 14:26:52      <- rebuilt (by the package step I ran late)
c2.s  mtime  2026-08-12 14:09:50      <- CRASHING emission: BEFORE the rebuild
e1.s  mtime  2026-08-12 14:37:45      <- WORKING  emission: AFTER  the rebuild
```
Same source, same flags, same cwd. `diff` between the two emissions is **exactly one line**: `+ call rtcc_load_all@PLT`. Emission itself is **fully deterministic** (5/5 identical md5, cwd-independent) — so this was never nondeterminism, never ASLR, never a claim-gate oscillation. It was **two different compilers**, and I had been reading one binary's output as the other's.

**RE-MEASURED ON THE PROPERLY BUILT TREE, `probe/bb` family H:**

| mode | result |
|---|---|
| `--run` (m3) | `30 pass · 0 xfail · 0 XPASS · 1 REGRESSION` |
| `--compile` (m4) | `30 pass · 0 xfail · 0 XPASS · 1 REGRESSION` |

**Identical. MODE34-IDENTICAL holds on this family.** The prior reading was `0 pass · 31 REGRESSION`.

## ⛔ HOW I ALMOST SHIPPED IT, AND THE ONE HABIT THAT CAUGHT IT

Everything downstream of the bad build was internally consistent, which is what made it dangerous: a control gradient (`c1_out` green, every pattern-matching program SEGV), a gdb conviction, a generalization test across two synthetic controls and two pinned-`.ref` probes, and a text-level patch that repaired all five. **I had written and committed a FINDING and a cursor entry declaring the class root-caused.**

What broke it was **validating an instrument on knowns before trusting it**: a new predictor script reported `m4 SEGV = 0` on five programs I had *already proven* SEGV. I had been about to bill that as a sixth vacuous instrument — but the instrument was fine and the *binaries had changed underneath me*. ⇒ **The vacuous-control habit this goal file mandates did not just catch a bad instrument; it caught a bad premise.** Had I skipped the known-answer check, the retraction would have shipped as a discovery.

**⛔ SECOND-ORDER TRAP, NAMED:** `make scrip` **exits 0 and yields a fully functional compiler** on a tree missing its build dependencies. There is no warning, no degraded-mode banner, and `--run` is completely unaffected — **only mode-4 emission is silently short one call.** This is the STALE-BINARY-BUILD-OK class with a new face: not a stale binary, but a *legitimately fresh binary built from an under-provisioned environment*.

## ⭐⭐⭐ WHAT SURVIVES — AND ONE LIVE HYPOTHESIS ABOUT THE INHERITED NUMBERS

**(1) BOARD B-0's PREMISE IS STILL FALSE, INDEPENDENT OF THE BUILD.** `run_suite.sh MODE=compile` does **not** return EMPTY. It prints full verdicts, `want=`/`got=`, a summary line and `mode: compile` — on both the bad build (correctly reporting 31 real crashes) and the good build (`30 pass · 1 REGRESSION`). **The harness works.** The inherited "the harness is the defect / `--compile` works by hand" reads a *program-output* emptiness as an *instrument* failure. ⇒ **do not send a seat to repair a working instrument.** ⛔ Caveat, stated plainly: the s32 seat may have observed a genuinely different failure I never reproduced. Reproduce B-0 before closing it.

**(2) ⭐⭐⭐ THE INHERITED m4 SEGV CLASS ITSELF IS NOW SUSPECT — AND THE TEST IS CHEAP.** s32's `crosscheck/patterns` reads `m4 SEGV=82 / PURE m4 CRASH=52`, and the `demo` corpus reads `BUILDFAIL=4`, a class "absent from patterns" and unbilled. **A tree built without the package step reproduces exactly this shape: mass m4-only SEGVs with m3 clean.** I raise this as a HYPOTHESIS, not a finding — I have not re-run `crosscheck/patterns` on the good build. **SETTLING EXPERIMENT (do this before opening EARN-2):**
```bash
bash scripts/install_system_packages.sh && rm -f scrip && make scrip && make libscrip_rt
./scrip --compile <any .sno> | grep -c rtcc_load_all      # MUST be >= 1
bash scripts/test_census_m3_m4_divergence.sh /home/claude/corpus/crosscheck/patterns
```
If the 82 collapses, then **s32's `.`×alternation quartet, the `rt_cap_push` / `g_cap_gen` / `.text`-pointer conviction, and the "52 concealed crashes" that promoted B-0 to top-of-board are all built on the same artifact** — and the two sessions of EARN work scoped from them need re-basing. If the 82 holds, it is real and this paragraph is void. **Either way the grep above should become a build gate: one line, and it makes this entire failure mode unmissable.**

**(3) `H31` IS A GENUINE DEFECT IN BOTH MODES.** `FENCE over ALT with capture: JSON key-value` (renamed from 152), `got=[]`, CRASH, **not in XFAIL**, on the good build, in m3 *and* m4. Untouched by any of the above and unrelated to the artifact.

## ⛔ NOT PROVEN / DO NOT INHERIT

- **Nothing about r9 is a compiler defect.** D1/D2 as I wrote them describe *the under-built binary's* output. On a correct build the preamble calls `rtcc_load_all` and the veneer question does not arise in the form I posed it. **The two scripts I wrote to demonstrate it have been deleted and their commits rolled back** (never pushed).
- **I did not re-run `crosscheck/patterns`, `benchmarks/snobol4`, or the full 163-program probe census on the good build.** Only family H, both modes. Every other number I produced this session came from the bad build and is **VOID**.
- s30b obligation (i) remains **OPEN** and untouched.

## RECOMMENDATION

Add to REPO-SCRIP.md's Session Start and to the build gate: **`./scrip --compile` output must contain `rtcc_load_all`**. And promote the package step from a documented line to a *checked* one — it is currently the difference between a real compiler and one that manufactures a 160-program crash class without saying a word.

**Container notes (unchanged, still useful):** `gdb` is absent and is **not** installed by `install_system_packages.sh`; needs `apt-get update && apt-get install -y gdb` (bare install 404s on `libc6-dbg`). Background builds need **`setsid`** — plain `nohup … &` is killed between tool calls and silently truncated my first build.
