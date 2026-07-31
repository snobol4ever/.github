# FINDING 2026-07-31 — ICON LOST 37 PROGRAMS TO A SNOBOL4 DEFAULT FLIP; `SCRIP_BB_ALLOC=0` RECOVERS 30 AT HEAD; AND MY OWN BISECT PREDICATE WAS READING `XFAIL`

Session: ICON-BB s203 (2026-07-31, Claude). Goal `GOAL-ICON-BB.md`. Lon directive: *"PIVOT!!! Climb the ladder to NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. See what SNOBOL4's sessions have been up to. Then do the same."*

No `src/` edit was made this session. Nothing committed. Everything below is measured on clean paired builds.

---

## ⭐⭐⭐ THE HEADLINE — ICON IS REGRESSED −37 AT HEAD, AND THE TRIGGER IS ONE TWO-LINE DEFAULT FLIP

| tree | Icon `--run` suite | note |
|---|---|---|
| `04d55ab6` (s202 watermark) | **252 / 11 / 30** | reproduces the cursor EXACTLY — the prose was true at its own commit |
| `417add3c` (HEAD), default | **215 / 48 / 30** | **−37** |
| `417add3c` (HEAD), `SCRIP_BB_ALLOC=0` | **245 / 18 / 30** | **+30 recovered by one env var** |

Both HEAD numbers reproduced on two independently clean-built trees (`rm -rf out scrip` each). This is NOT the STALE-ORIENTATION disease: the watermark was accurate when written. It is a genuine cross-language regression that went unmeasured because no Icon session ran for 177 commits.

## ⭐⭐ THE BISECT — CLOSED TO A SINGLE COMMIT, AND ITS PARENT IS THE SAME RUNG LANDED DORMANT

Predicate: rung01+rung02+rung03 combined FAIL count (21 programs; 0 at s202, 11 at HEAD). ~156 s/probe including a full clean rebuild of both halves.

- `6d0bbea9` **ZW-1 s21x-m** — universal per-BB carve landed **DORMANT** (`SCRIP_BB_ALLOC` opt-IN) → **FAIL=0 (GOOD)**
- `f52d5877` **ZW-1 s21x-m ACTIVATE** — *"ACTIVATE universal per-BB RSP allocation BY DEFAULT (Lon directive: all RSP activated, take the hit, walk the ladder)"* → **FAIL=10 (BAD)**

The diff is **two lines, both sense-flips of the same env var**, in `emit.cpp` and `emit.h`:
```
-  _ba = (e && *e == '1') ? 1 : 0;      /* opt-IN  */
+  _ba = (e && *e == '0') ? 0 : 1;      /* default-ON, killswitch SCRIP_BB_ALLOC=0 */
```
plus the reverted `emit_jmp_pin_rbp` arm (already retained in-tree as a law).

**"Take the hit" was a SNOBOL4 accounting.** That commit's own message records the armed watermark for SNOBOL4 (`m3 231/85`) and the ladder that would walk it back. Icon was never in the ledger, and the ladder that recovered SNOBOL4's cost was walked entirely through SNOBOL4-shaped rungs.

⭐ **THE RECOVERY IS NOT FREE AND MUST NOT BE FLIPPED BLIND.** `SCRIP_BB_ALLOC=0` recovers 30 of 37 for Icon, but the flip is load-bearing for the SNOBOL4 ζ ladder that has been built ON TOP of it for 65 commits since (ZTOS-1/2, GLUE-1..4, ZOP-1, ZD-2*, ZD-7/8, LP-1/2). **The default is not this session's to change** — SNOBOL4's watermark at HEAD (m3 276/41 · m4 276/40) is presumably measured WITH it on, and would have to be re-measured with it off before anyone touches the default. What the killswitch buys today is a **proven root cause and a per-language escape hatch**, not a landed fix.

⚠ **THE RESIDUAL 7 IS A SECOND, LATER EVENT** (245 ≠ 252) and is NOT explained by this commit. It lives somewhere in `#113..#177` and needs its own bisect with the same predicate. Do not attribute it here.

## ⛔⭐⭐ INSTRUMENT LAW EARNED THE HARD WAY — `grep -oE 'FAIL=[0-9]+' | tail -1` READS `XFAIL`

My first bisect predicate was:
```bash
grep -oE 'FAIL=[0-9]+' | tail -1 | tr -d 'FAIL='      # ⛔ BROKEN
```
The harness prints `PASS=215 FAIL=48 XFAIL=30`. `FAIL=[0-9]+` **also matches the tail of `XFAIL=30`**, and `tail -1` then selects that match. **Six consecutive probes returned FAIL=0 and I read all six as GOOD**, including HEAD itself — I was one step from publishing *"bisect clean, HEAD is fine, my build was the anomaly"*, which would have been exactly backwards and would have buried a −37 regression under a false exoneration of the very commit that caused it.

**What caught it:** running the FULL suite on the bisect worktree's own HEAD build and getting **215/48/30** — identical to the "anomalous" build I was about to blame. Two independent builds agreeing is what exposed the instrument. A single build would not have.

Corrected form anchors the left side of the pair:
```bash
grep -oE 'PASS=[0-9]+ FAIL=[0-9]+' | tail -1 | sed -E 's/.*FAIL=//'
```
**And it was PROVEN TO DISCRIMINATE at both ends before another probe was spent** (11 at HEAD, 0 at s202) — the step the first version never got.

⭐ **THIS IS THE REPO'S OWN LAW RECURRING A THIRD TIME.** s165: *"AN EMPTY COMPARISON MUST NEVER BE A PASS."* s22j: *"A NULL RESULT MEASURED ON A MIS-APPLIED CHANGE IS NOT A NULL RESULT."* Both were about an instrument that reported success by failing to look. **Generalized form, offered for RULES.md: A BISECT PREDICATE MUST BE PROVEN TO RETURN BAD AT THE KNOWN-BAD END AND GOOD AT THE KNOWN-GOOD END BEFORE THE FIRST REAL PROBE IS SPENT.** An all-GOOD or all-BAD bisect is the signature of a predicate that is not reading what it names — the cost is silent and the conclusion is confidently inverted.

## ⭐⭐ THE ζ FINDING THE REGRESSION DISPLACED — ICON IS NOT ON THE NON-POPPING LADDER AT ALL

Census, 295 Icon rung programs, `SCRIP_ZD_DIAG=1` at HEAD: **ARMED ZD NODES = 0. DECLINED RUNS = 271.** Gen-1 FC fires only **6 times in 140 programs**. Icon runs almost entirely on the **legacy whole-graph carve** — the corpse `GOAL-SNOBOL4-BB.md` THE MODEL says to delete. It never reaches Gen-2.

Two predicates in the language-blind emitter do it:

**(1) THE LOCALS CONJUNCT — `zd_wl_kind` (emit.cpp:1846).** `IR_VAR`/`IR_ASSIGN` arm only for globals. SNOBOL4 retired widening it as **"⛔ ZD-2h RETIRED AS VACUOUS BY CONSTRUCTION — DO NOT SPEND A RUNG WIDENING THIS LINE"** (`37d7c7ca`). That retirement is CORRECT FOR SNOBOL4 and its own comment names precisely why it cannot generalize: *"SNOBOL4 has no lexical locals… `graph_has_local` is an **ICON-era LEXICAL frame-slot concept**… and it has **no SNOBOL4 customers at all**."*

**MEASURED with SNOBOL4's own control probe `SCRIP_ZDLOCAL=1`** — the one their finding reports firing **0 times across 318 crosscheck programs**:

| corpus | local-arm hits |
|---|---|
| SNOBOL4 crosscheck (318 pgms, their measurement) | **0** |
| Icon rung corpus (295 pgms, this session) | **2258** (1613 `IR_VAR` + 645 `IR_ASSIGN`) |

⭐ **AND 1812 OF THE 2258 (80%) ARE ALREADY ON rbp-PINNED GRAPHS** (`pinned=1`) — exactly the pin gate the retired rung specified ("arm locals only where rbp is pinned so a varslot read is not displaced by ZD depth"). **Law 4's occasional C-style RBP is ALREADY ESTABLISHED for Icon's locals.** The depth-immune-base question ZD-2h found no node class to answer for has 2258 of them one language over.

**(2) `IR_CALL_BUILTIN_ICON`** — 68 first-blocker declines, simply absent from the whitelist.

**THE MACHINERY WORKS ON ICON THE MOMENT BOTH CLEAR.** Global arithmetic, no builtin call (`SCRIP_ZD_DIAG=1`, `armed=10 all_zd=1`):
```
i=0 IR_LIT_INTEGER    K=16 zout=16      i=5 IR_VAR            K=16 zout=64
i=1 IR_ASSIGN         K=0  zout=16      i=6 IR_COERCE_NUMERIC K=16 zout=80
i=2 IR_LIT_INTEGER    K=16 zout=32      i=7 IR_COERCE_NUMERIC K=16 zout=96
i=3 IR_ASSIGN         K=0  zout=32      i=8 IR_BINOP          K=16 zout=112
i=4 IR_VAR            K=16 zout=48      i=9 IR_ASSIGN         K=0  zout=112 gpop=112
```
Monotone spine, **ZERO intermediate pops**, ONE terminal release. The same program with `local` instead of `global`: `armed=0 all_zd=0 region=208` — carve live. **This is the directive's model already running on Icon, gated off by two lines.**

## ⭐ ICON'S BLOCKER CENSUS BARELY OVERLAPS SNOBOL4'S — THE GENERATOR FAMILY IS UNTOUCHED

First-blocker histogram, 271 declined runs:

| Icon first blocker | n | SNOBOL4 analog |
|---|---|---|
| `IR_CALL_BUILTIN_ICON` | 68 | none |
| `IR_ASSIGN` (the locals conjunct) | 65 | **vacuous — 0 customers** |
| `IR_CALL_PROC_STAGED` | 34 | Family A (`bb_call_proc_staged`) — the ONLY shared rung |
| **generator family:** `IR_DISJUNCTION` 30 · `IR_TO` 20 · `IR_REPALT` 5 · `IR_TO_BY` 4 · `IR_PROC_GEN` 4 · `IR_CALL_BUILTIN_GEN` 2 · `IR_CREATE` 1 · `IR_CONJUNCTION` 1 | **67** | **NONE — Icon-only, nobody has looked at it** |
| `IR_MAKE_LIST` 13 · `IR_SCAN_ENTER` 9 · `IR_KEYWORD_ICON` 6 | 28 | none |

⚠ **Per s22j's own instrument law — RANK BY BREAK SET, NOT BY DECLINE COUNT.** This histogram is a FRONTIER reading, not a backlog. The discriminating instrument is an Icon killswitch A/B set-diff (the `SCRIP_NOFC=1` shape), which **does not exist for Icon** and is a genuine prerequisite sub-rung.

## ⛔ THE STRUCTURAL LESSON — "SAFE FOR CODE" IS A MERGE CLAIM, NOT A SEMANTIC ONE

RULES.md's concurrency note (s47) sanctions 3–4 parallel sessions as *"safe for CODE (different files; git rebases cleanly; s47 measured zero divergence)."* **That measured claim is about MERGE, and it held — every one of the 177 commits rebased cleanly.** But the ζ ladder's edits live in `emit.cpp`, `emit.h`, `x86_asm.h` and the shared templates, which are **language-blind by the FACT RULE's own design** (no language identity past first dispatch). A SNOBOL4-shaped default flip in a language-blind file reaches every frontend, and git cannot see it.

⭐ **PROPOSED, LON'S CALL:** a per-language watermark re-prove is owed by any session that flips a DEFAULT in `src/emitter/` — not by any session that adds a gated arm. The distinction is cheap to state and greppable: an opt-in landing (`6d0bbea9`) is provably inert; the flip (`f52d5877`) is what carries cross-language risk, and it is exactly the shape that cost 37 programs here.

## REPRODUCTION

```bash
git -C /home/claude/SCRIP worktree add /home/claude/wt-s202 04d55ab6
cd /home/claude/wt-s202 && rm -rf out scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_icon_all_rungs.sh --scrip /home/claude/wt-s202/scrip | tail -1   # 252/11/30
# at HEAD:
bash scripts/test_icon_all_rungs.sh | tail -1                                      # 215/48/30
SCRIP_BB_ALLOC=0 bash scripts/test_icon_all_rungs.sh | tail -1                      # 245/18/30
```
All numbers RT_OPT=-O0 (no `-O2` was used or directed — O2-DIRECTED-ONLY rule).

## NEXT RUNGS, ORDERED

1. ⭐⭐⭐ **The residual 7** (`245` vs `252`) — second bisect, `#113..#177`, SAME corrected predicate, prove it discriminates first.
2. ⭐⭐ **Lon's call on the `SCRIP_BB_ALLOC` default** — needs a SNOBOL4 + Prolog watermark re-prove under `=0` before anyone touches it. Do NOT flip blind; 65 commits of ζ ladder sit on top of it.
3. ⭐ **Icon killswitch/break-set instrument** — the `SCRIP_NOFC=1` shape for Icon, so the census below can be ranked honestly rather than by count.
4. **ZD-2h widened for Icon under the pin gate** — the conjunct becomes *"global, OR local on a pinned graph"*: behaviorally named, so it stays inside the NO-LANGUAGE-IDENTITY FACT RULE. 2258 customers, 80% already pinned. ⛔ Requires Lon's release of the ⛔ on that line, since it is another goal's stated prohibition.
5. **`IR_CALL_BUILTIN_ICON`** — largest count; likely one template ZD arm.
6. **The generator family (67)** — the real Icon-shaped ζ question: four-port goal-directed evaluation on a non-popping FORTH spine. No SNOBOL4 precedent exists; `refs/jcon-master/tran/irgen.icn`'s 43 `ir_a_*` port topologies are the ground truth.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
