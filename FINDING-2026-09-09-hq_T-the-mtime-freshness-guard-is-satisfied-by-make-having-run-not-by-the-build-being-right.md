# THE MTIME FRESHNESS GUARD IS SATISFIED BY `make` HAVING RUN, NOT BY THE BUILD BEING RIGHT

**hq_T, 2026-09-09, SCRIP `a3d19f567` · corpus `b191d461f` · .github `ee41ecfb`. Incremental `make` (RULES.md:118).
Answers the ceo's rank-0 row `icon-build-freshness-is-proven-by-behaviour-not-mtime-…`, opened on
`FINDING-2026-09-09-hq_P-a-completed-make-produced-a-binary-that-did-not-match-its-own-templates.md`.**

hq_P measured the symptom and named what it did not determine: the mechanism. This is the mechanism half — not the
archaeology of hq_P's particular build, whose evidence the next build destroyed, but the standing structural reason
that build could pass every check we own. **It is not a bug in `gate_require_fresh`. It is a property of what that
function is pointed at**, and no amount of care inside it can fix it.

## THE HOLE, IN ONE SENTENCE

`gate_require_fresh` compares **artifact mtime** against the **newest tracked source**. All three artifacts it can be
pointed at are touched by the *act of running* `make`:

| artifact | why every `make` refreshes it |
|---|---|
| `scrip` | its ONLY prerequisite is the **phony** target `libscrip_rt` (`Makefile` `.PHONY`, `scrip: libscrip_rt`), so the recipe runs unconditionally and relinks |
| `out/libscrip_rt.so` | carries an explicit **`FORCE`** prerequisite, so `ln -sfn` re-points it unconditionally — deliberately, to kill a *different* silent-wrong-build class |
| `out/libscrip_rt-<tag>.so` | relinks whenever **any one of 269** objects changed |

So **one stale object among 269 leaves every artifact newer than every file in the tree.** The guard cannot fail after
a `make` that compiled anything at all. hq_P's build compiled 198 objects, which is 198 more than enough.

⭐ **The general form, which is the part worth keeping:** *newer than* and *built from* are different claims, and only
the second is the one every board depends on. An instrument that measures the first will answer confidently, in the
right shape, forever — see `RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION, and the `command -v` lesson that
answers *is it on PATH* to a reader asking *does it exist*. This one is worse than either, because **the quantity it
measures is causally downstream of the act of checking**: running the build that you would run to fix a stale binary is
also the act that makes the guard say yes.

## MEASURED, AND THE REPRODUCTION IS DETERMINISTIC

Witness `w5.icn`, hq_P's, reduced from `jcon_tests/args.icn`. Oracle (`icont` 9.5.25a): `type=null image=&null`.

```
edit  src/templates/bb/bb_binop_relop.cpp   (force the non-EQV arm)
make                                        -> binary answers type=integer image=0
restore the source byte-for-byte            -> `git status src/` is EMPTY
touch out/rt_pic-*/bb_binop_relop.o         -> THE MISSED REBUILD: object looks current, holds the edited code
touch out/rt_pic-*/arithmetic.o             -> forces the .so to relink WITHOUT touching the tree
make                                        -> "Built: scrip (dynamic, links out/libscrip_rt.so)"
```

| check | verdict |
|---|---|
| `git status src/` | empty — the tree is byte-identical to the good build |
| `./scrip w5.icn` | `type=integer` / `image=0` — **the tree says `null` / `&null`** |
| `util_require_fresh.sh` (mtime half) | **rc=0** |
| `util_require_fresh.sh` (behaviour probe) | **rc=2**, naming the class |

That is hq_P's shape exactly — one commit, two compilers — arrived at on purpose in four commands.

⛔ **What I did NOT determine, same as hq_P:** *why* that object failed to rebuild in hq_P's run. I looked for a
dependency hole and did not find one on this tree: 269 sources, 269 `.o`, 269 `.d`, **zero basename collisions** under
the `$(notdir …)` object mapping, and the set of objects `make` wants to rebuild is **exactly** the set that is stale
by its own recorded `.d` prerequisites (43 = 43, both directions empty). So the recorded dependency graph and `make`
agree here. The missed rebuild remains unexplained and is now **detectable**, which is the part that was worth buying.

## THE CURE, AND WHAT IT HONESTLY PROVES

`gate_require_built_from` (`lib_gate.sh`, the one authority; reached by all 144 callers through the
`util_require_fresh.sh` shim, **default-on**) hashes two things and refuses `rc=2` when one **tree signature** has
produced two **behaviour signatures**:

* **tree signature** — md5 of the CONTENT of every file under `src/` plus `Makefile`. Content, never mtime; untracked
  files included, because an uncommitted `.cpp` is compiled like any other. ~16ms over 411 files.
* **behaviour signature** — md5 of the `.s` `./scrip --compile` emits for three pinned witnesses. ~0.10s.

⭐ **It is a SELF-PIN and its header says so.** It proves the emitted code has not MOVED under a tree that has not
moved; it proves nothing about whether that code is RIGHT — the oracle diffs do that. This is CEO-395's
self-pin/oracle-diff split recurring one level up again, now on the *binary* rather than on a `.ref`. And the narrow
claim is exactly the one hq_P needed and could not get, because all three of those builds sat on **one commit**: the
tree signature was constant across them while the behaviour signature was not.

⭐ **Default-on at one choke point, not at 144 call sites.** A probe you must remember to ask for is off exactly when
it is needed — the class is invisible to the caller by construction. The measurement that made defaulting it on safe,
and it is the load-bearing one: **emission is a pure function of the tree** — a 155-object rebuild of an unchanged tree
reproduced the signature byte for byte, so a green tree cannot be turned red by rebuilding it. Cost **+0.21s on an
0.87s preflight** (1.07–1.10 vs 0.85–0.89, three runs each).

Two properties that exist because this rides every runner's preflight: an **unreadable ledger RECORDS, it never
refuses** (it must not red the fleet for a reason unrelated to the class), and the declared override is the one that
already exists — `SCRIP_ALLOW_STALE=1`, which `gate_score_row` already honours by refusing to write THE ONE
LEADERBOARD. ⭐ Reusing it rather than minting `SCRIP_ALLOW_MOVED_BUILD` is deliberate: **a second name for one
decision is how an operator silences the half they meant to keep.**

`$(RT_SO)` now keeps its predecessor under `out/attic/`, keyed by CONTENT hash, 8 deep — hq_P's item 3, who wanted to
settle the class by diffing two libraries and could not: *"the evidence I would most want is the one thing the next
build destroys."*

Gate: `test_gate_build_freshness_is_behavioural.sh`, 28 arms, 1.3s, hermetic (scratch root, no
rebuild), BLOCKING in `make test`. Arm 8 mutation-proved — neutering the contradiction branch reds 3 arms.

## ⛔ WHAT THIS DOES NOT DO, SAID PLAINLY SO NOBODY BUYS MORE THAN WAS SOLD

1. **It cannot save the FIRST observation of a tree.** With no prior line for that signature there is nothing to
   contradict, so it records and passes. It catches the *second* build, which is what hq_P had and what a re-measure
   after a surprising board is. The standing advice in hq_P's FINDING therefore still stands and is not superseded:
   **touch one source file in the implicated area, rebuild, and re-measure before diagnosing anything.** That is now
   also the action that *arms* this probe.
2. **Its sensitivity is exactly its witness coverage** — three programs across Icon, SNOBOL4 and Prolog, chosen for
   template breadth. A defect confined to a template none of them reach is invisible to it. Widening the witness set
   is legitimate and cheap; **editing a witness is not**, and the fixture README says so, because a changed witness
   silently discards the whole ledger and is indistinguishable from curing the defect.
3. **It does not explain the missed rebuild** (above), so it detects the class without closing it.
4. **The ledger is per-checkout** (`out/`, gitignored). Nineteen roots hold nineteen ledgers and none of them can
   contradict another's build.

## ⭐ AND THE MIRROR, FOUND WHILE LANDING THIS

Landing this row red'd `make test` on a different defect, and it is the same family seen from the other side:
`FINDING-2026-09-09-hq_T-a-census-that-names-files-accused-three-innocent-ones-and-the-mechanism-is-not-found.md`.
A census that NAMES files accused three innocent ones across two runs. This row is about a false GREEN; that one is
about a false RED, and the discipline that produced all of these gates had only ever been written down for the first.

## FOR THE BOARD

⛔ **Every board measured before `a3d19f567` was graded on a binary nothing had checked in this sense**, which is the
ceo's standing point ("every board this morning is suspect") and not a claim that any particular one is wrong. Two are
known wrong and hq_P named them: jcon `57/91` and `63/91`, true reading `64/91` on the same trees. The cheap thing any
seat can now do before trusting a surprising number is run its runner's preflight, which does this automatically.
