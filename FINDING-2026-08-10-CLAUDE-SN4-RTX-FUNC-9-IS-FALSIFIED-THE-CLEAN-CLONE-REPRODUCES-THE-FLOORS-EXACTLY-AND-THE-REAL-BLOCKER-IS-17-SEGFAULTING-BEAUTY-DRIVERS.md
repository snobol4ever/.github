# FINDING 2026-08-10 (Claude Opus, fresh seat) — RTX-FUNC-9 IS FALSIFIED: A CLEAN THREE-REPO CLONE REPRODUCES THE RECORDED FLOORS **EXACTLY**, THE DANGLING SYMLINK IS A RED HERRING, AND THE REAL DEFECT IN THAT NEIGHBOURHOOD IS **17 SEGFAULTING BEAUTY DRIVERS**

**Seat:** fresh container, clean three-repo clone, nothing inherited.
**Fingerprint:** SCRIP `bce9a4b` · corpus `bea31de` · `.github` `37e0273` (all 2026-08-10).
**Build:** one coherent moment — `scrip` and `out/libscrip_rt.so` both mtime **23:05**. `RT_OPT=-O0` (O2-DIRECTED-ONLY: no `-O2` directed this session).
**Arm:** `SCRIP_AB` defaults **OFF** (`lower_snobol4.c:2056`) ⇒ every number below is the **AB=0 / LEGACY** arm — the same arm RTX-FUNC-9's `253/64` cites.

---

## 1. THE RUNG'S PREMISE, AND WHY IT IS FALSE

RTX-FUNC-9 reads: *"the `snobol4corpus` DANGLING SYMLINK blocks absolute watermark comparison … A fresh three-repo clone measures AB=0 m3 253/64 against a recorded 282/35 — so **no seat working from a clean clone can quote or re-prove the watermark**."*

**I am a seat working from a clean clone, and I re-proved the watermark exactly.**

| suite | my clean-clone measurement | recorded |
|---|---|---|
| broad-336 m3 | **270 / 66** | **270 / 66** (s12b MEASURED FLOORS, this goal file line 9) |
| broad-336 m4 | **262 / 68 / 6** | **262 / 68 / 6** (same) |
| crosscheck-317 m3 | 269 / 48 | 253/64 *and* 282/35 both cited |
| crosscheck-317 m4 | 262 / 54 / 1 | — |

The broad-336 floors reproduce **byte-for-byte from a clean clone with the dangling symlink still in place.** That single fact refutes the rung's central claim.

### FOUR INDEPENDENT DISPROOFS OF THE SYMLINK MECHANISM
1. ⭐ **THE DENOMINATOR IS INVARIANT.** `253+64 = 282+35 = 269+48 = **317**`. Three measurements, three different splits, **one denominator**. A missing corpus subtree changes the DENOMINATOR; these numbers cannot have been produced by absent programs. *This is free arithmetic available on the face of the rung text itself — it needed no container to spot.*
2. **Zero graded programs reference it.** `grep -rl "snobol4corpus\|lon/inc" crosscheck/` → **0**.
3. **`crosscheck/` has zero live `-INCLUDE` directives** — it is self-contained by construction, exactly as `REPO-corpus.md` states. There is no path by which an absent include dir could reach it.
4. **The graded set is complete in a clean clone:** 318 `.sno` in `crosscheck/`, exactly **1** without a sibling `.ref` ⇒ 317 graded. Matches the ARCH §7 note's shape (recorded there as 316/315; the suite has since grown by two).

**⇒ RTX-FUNC-9 should be STRUCK, not scheduled.** Vendoring the corpus or writing a fetch script would have cost a rung and fixed nothing about watermark reproducibility.

### WHAT I DID **NOT** ESTABLISH
- **Why another seat measured `253/64`.** Unknown. Candidates: a different SCRIP HEAD, an incomplete toolchain (this container shipped **without `bison`/`flex`/`nasm`** — `install_system_packages.sh` was required), or uncommitted tree edits. Not retroactively determinable. **I claim only that the symlink is not the cause.**
- **Why `282/35` differs from my `269/48`** — see §3, which is the live suspect but is NOT convicted.
- **Anything about Milestone 1.** `demo/beauty/beauty.sno` is graded by a DIFFERENT runner; the broad sweep's `BEAUTY` var points at `beauty_suite/`, not at it. I never located its input file (it reads **stdin**; `</dev/null` correctly yields empty output, md5 `d41d8cd9…` = empty string). ⛔ **An earlier reading of mine — "beauty.sno emits nothing ⇒ Milestone 1 broken" — was WRONG and is recorded here so nobody inherits it.** Empty output from a stdin filter fed `/dev/null` is the CORRECT result, not a regression.

---

## 2. THREE BROKEN PATHS DO EXIST — ALL COSMETIC TO THE WATERMARK, ONE UNDOCUMENTED

| path | kind | target | status |
|---|---|---|---|
| `corpus/snobol4corpus` | tracked symlink (mode 120000) | `/home/claude/snobol4corpus` | **dangling** — in none of the three repos |
| `corpus/programs/lon/sno/inc` | tracked symlink (mode 120000) | `../inc` ⇒ `programs/lon/inc` | **dangling** — target absent; ⭐ **UNDOCUMENTED ANYWHERE UNTIL NOW** |
| `corpus/programs/snobol4/demo/inc` | plain directory | — | **ABSENT**, yet it is the runner's `INC`/`SNO_LIB` value (`test_broad_corpus_snobol4.sh:15`) |

The third is the interesting one: **every program in the broad sweep is invoked with `SNO_LIB` pointing at a directory that does not exist.** It is nevertheless NOT the cause of the driver failures — see §3, where it is explicitly falsified. Worth repairing as hygiene (`REPO-corpus.md` advertises `demo/inc/` as the `-INCLUDE` home), not as a blocker.

---

## 3. THE REAL DEFECT NEXT DOOR: **ALL 17 `beauty_suite/*_driver.sno` SEGFAULT IN MODE 3**

13 of them show as `FAIL` in the broad sweep. Measured directly:

```
drivers graded:                       17
PASS with runner's INC (missing dir):  0
PASS with INC = drivers' own dir:      0
produced NO output (crash/empty):     17     ← "Segmentation fault" on stderr
```

**Three environment hypotheses raised and KILLED by measurement, in order:**
- ❌ `SNO_LIB` → missing `demo/inc`. Falsified: pointing `SNO_LIB` at the drivers' own directory changes nothing. The included `.sno` files (`global.sno`, `ReadWrite.sno`, `counter.sno`, `semantic.sno`) are all **present** beside the drivers.
- ❌ CWD. Falsified: segfaults identically from the corpus root — which is what SCRIP HEAD `bce9a4b` ("compile from the CORPUS root so `-include` resolves") made the natural suspect.
- ❌ `SNO_LIB=corpus/lib`. Falsified: same segfault.

⛔ **ARITHMETIC COINCIDENCE, RECORDED SO IT IS NOT MISTAKEN FOR EVIDENCE.** `282−269 = 13` and `48−35 = 13` — exactly the 13 drivers failing in the sweep. The fit is perfect and **I could not make it mean anything**: the drivers fail in every environment arm I could construct, so "the recorded 282/35 is a run where these 13 passed" remains an untested story about a DIFFERENT commit, not a mechanism. *A perfect numerical fit is a hypothesis generator, never a conviction* — the same trap as citing an unmoved battery as a gate (ARCH §7 step 2b).

⛔ **NOT ROOT-CAUSED, DELIBERATELY.** RULES.md MONITOR-FIRST binds: a divergence is found with the 2-way IPC sync-step monitor, never by reading code or guessing. **I did not run the monitor** and therefore name no cause. Next seat: `scripts/test_monitor_2way_sync_step_bin.sh programs/snobol4/beauty_suite/fence_driver.sno`.

**Open and unanswered: is this a REGRESSION?** These are Gimpel-suite beauty drivers; a whole-suite segfault is not the shape of long-standing debt. Cheapest discriminator is a bisect on SCRIP HEAD, not a code read.

---

## 4. PROPOSED LADDER EDITS (Lon accepts or rejects)

1. **STRIKE RTX-FUNC-9.** Premise falsified four ways. ⭐ Per ARCH §7 step 0's own instruction — *"strike the dead names out of the ladder rung text in the SAME commit that discovers them"* — this finding and the rung edit ship together. RTX-2 corrected the table but left the RTX-3 rung intact, and the next session walked into the same wall; this is that lesson applied to a rung's **CAUSE** rather than its **SYMBOLS**.
2. **MINT `RTX-FUNC-11: THE 17 BEAUTY DRIVERS SEGFAULT IN m3.`** MONITOR-FIRST from `fence_driver.sno`. Establish regression-vs-debt by bisect before any code is read.
3. **HYGIENE (not a rung):** delete the two dangling tracked symlinks; either create `demo/inc/` or point the runner's `INC` at a path that exists.
4. **CORRECT THE FLOORS' PROVENANCE NOTE.** The s12b floors are reproducible from a clean clone — say so beside them, so the next seat does not re-derive this.

---

## 5. THE TRANSFERABLE LESSON

RTX-2's phantoms were DEAD names. RTX-3's were INVENTED names. RTX-4's were LIVE names RECORDED WRONG. **RTX-9's rung had good names and a WRONG CAUSE** — a mechanism inferred from a coincidence (a dangling symlink was visible; the watermark did not match; the first was assumed to explain the second) and never tested against the arithmetic sitting in the rung's own sentence.

⭐ **The family resemblance is exact: a rung written from a DOCUMENT — or from an INFERENCE — rather than from the TREE.** ARCH §7 step 0 already demands that symbols round-trip against the tree. **This finding argues the same discipline is owed to a rung's stated CAUSE:** before scheduling work against a mechanism, run the cheapest experiment that could disprove it. Here that experiment was adding two numbers.
