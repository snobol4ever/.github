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

---

# ADDENDUM (same seat, same build) — RTX-FUNC-11 REDUCED: **THE DEFECT IS `-INCLUDE`-SPECIFIC. IDENTICAL BYTES RUN INLINE AND SEGFAULT WHEN INCLUDED.**

⭐⭐ **THE HEADLINE, AND IT IS A CLEAN PATH-SWAP — RULES.md's prescribed cheapest discriminating experiment, "made to swap paths where possible":**

```
17 lines pasted INLINE into one file  ->  runs, prints "alive"
the SAME 17 BYTES via -INCLUDE        ->  Segmentation fault
```

Reduction ladder from `fence_driver.sno` (21 lines) — every step measured, none inferred:
1. Driver **minus** its `-INCLUDE` line ⇒ runs and is **ORACLE-EXACT** against `fence_driver.ref`. **The driver body is not implicated at all.**
2. `-INCLUDE 'global.sno'` + a single `OUTPUT` ⇒ SEGV. The include is the whole defect.
3. Prefix scan of `global.sno` (163 lines): first crashing prefix = **line 161**, `$UTF_Array[i, 2] = UTF_Array[i, 1] :S(G1)` — preceded by `UTF_Array = SORT(UTF)`.
4. Suffix scan: smallest crashing region = **lines 145–161 (17 lines)** — 12 `UTF[...]` entries + `SORT` + the indirect-assignment loop.
5. **Inline-vs-include on those exact 17 lines ⇒ the swap above.**

## WHAT IS EXONERATED (each killed by measurement, not argument)
- **`-INCLUDE` in general** — a 3-line include of `X = 42` works.
- **Source size** — 23,447 bytes of comment padding in the included file: **ok**.
- **Value size / runtime data size** — 12 values of `DUPL('X',40)` built at runtime: **ok**.
- **Key length** — 12 × 4-char *literal* keys (`'abc1'`): **ok**.
- **High/non-ASCII bytes** — ASCII `CHAR(65) CHAR(66) CHAR(67)` keys crash exactly as the UTF-8 ones do.
- **Concatenation as such** — 12 × `'a' 'b' 'c1'` concatenated *literals*: **ok**.
- **Entry count as such** — 20 entries with short literal keys: **ok**.
- **`SORT`, the `$` indirect assignment, the out-of-range loop exit, standalone** — none crash in isolation, at any size I tried, without `-INCLUDE`.

## ⛔ WHAT I COULD **NOT** ISOLATE — RECORDED AS A CONTRADICTION, NOT SMOOTHED INTO A MODEL
The trigger tracks something that scales with **`CHAR()` calls in the included file**, and it is threshold-like:

| included file | total `CHAR()` calls | result |
|---|---|---|
| 12 entries × 2 `CHAR` | 24 | ok |
| 6 entries × 4 `CHAR` | 24 | ok |
| 12 entries × 3 `CHAR` | 36 | ok |
| 40 entries × 1 `CHAR` | 40 | **SEGV** |
| 24 entries × 2 `CHAR` | 48 | **SEGV** |
| 48 entries × 1 `CHAR` | 48 | **SEGV** |
| 12 entries × 4 `CHAR` | 48 | **SEGV** |
| **11 REAL entries × 4 `CHAR`** | **44** | **ok** ⛔ |

⛔ **The last row contradicts the scalar model** (44 > 40, yet ok). The real entries differ from the generated ones in value length and key distribution, so a second variable is in play. **I am not naming a mechanism.** A "total CHAR() calls > ~36" story fits seven rows and is falsified by the eighth; publishing it as *the* rule would hand the next seat a model that breaks on the very program that started this. ⭐ *This is the s223/s217 lesson in a new axis: a probe that fits most of the data is not a conviction.*

## HOW TO REPRODUCE IN ~10 SECONDS (no corpus needed)
```bash
cd /tmp && mkdir -p r && cd r
: > inc_body.sno
n=1; while [ $n -le 48 ]; do printf "    UTF[CHAR(%s)] = 'v%s'\n" $((40+n)) $n >> inc_body.sno; n=$((n+1)); done
printf '    UTF_Array = SORT(UTF)\n    i = 0\nG1  i = i + 1\n    $UTF_Array[i, 2] = UTF_Array[i, 1]  :S(G1)\n' >> inc_body.sno
printf -- "-INCLUDE 'inc_body.sno'\n\tOUTPUT = 'alive'\nEND\n" > p.sno
scrip --run p.sno                      # -> Segmentation fault
cat inc_body.sno > inline.sno; printf "\tOUTPUT = 'alive'\nEND\n" >> inline.sno
scrip --run inline.sno                 # -> alive        (SAME BYTES, no -INCLUDE)
```

## FOR THE NEXT SEAT
- ⛔ **Still not root-caused, still MONITOR-FIRST.** The inline arm is a **perfect control**: same source bytes, same runtime work, one path crashes. Run the 2-way monitor with the inline arm as the agreeing reference and take the first divergent event.
- **Not minted into `corpus/probe/` this seat** — a `.ref` needs the SPITBOL oracle (`/home/claude/x64`), which I did not clone. Recipe above is complete; minting is a 5-minute rung for whoever has the oracle up.
- **Coverage blind spot, worth a rung of its own:** `crosscheck/` contains **zero live `-INCLUDE` directives**, so the 269-program passing suite is *structurally incapable* of catching any `-INCLUDE` defect. The 17 beauty drivers are the only `-INCLUDE` coverage in the graded set, and all 17 are red. **The gate cannot see this class.**
