# FINDING 2026-07-26g — CLAUDE — RK: `**@r` (SLURPY_LOL) IS BLOCKED ON THE FLAT REPRESENTATION, NOT A CHEAP FOLLOW-ON — AND TWO `rest_kind` CLAMPS WOULD HAVE MADE IT SILENTLY PASS

**Session:** orientation + one falsification rung. **No code landed.** **Scope:** `GOAL-RAKU-BB.md` LIVE CURSOR s2026-07-26c, NEXT RUNG item (a).

---

## HEADLINE

The s2026-07-26c cursor names `**@r` (SLURPY_LOL, non-flattening) as the cheapest next rung: *"needs one more lexer rule (`"**@"`) and a THIRD `rest_kind` value (`REST_NESTED`) … the plumbing this session built takes it directly, no redesign."*

**The plumbing claim is CORRECT. The rung is still BLOCKED.** The blocker is not plumbing — it is that the current aggregate representation **cannot express the distinction the feature exists to make**. `**@r` belongs on the RK-AGG ladder (real aggregates), not in the cheap-follow-on list.

⚠ The estimate was not careless: it asked *"what code must change?"* and answered correctly. The unasked question was *"can the representation hold the answer?"* That question is the finding.

---

## THE PROOF (measured, not argued)

Canonical first, per CONSULT CANONICAL SOURCES. `Actions.nqp:9623` selects among three slurpy list-builders:

```
:name(%info<pos_onearg> ?? 'from-slurpy-onearg' !! %info<pos_lol> ?? 'from-slurpy' !! 'from-slurpy-flat')
```

`List.rakumod`: `from-slurpy` (:193) vs `from-slurpy-flat` (:271). The **only** difference is that `-flat` carries the Iterable→`.flat.Slip` conversion (:287-291). So `*@` flattens Iterable arguments; `**@` preserves them as single elements. The distinction is **observable only when an argument is itself an aggregate** — for all-scalar calls the two are identical by definition.

SCRIP's flat aggregate is a `SOH`(`\x01`)-joined string. `rt_make_flat_agg` (`by_name_dispatch.c:1643`) splits every argument on `SOH` and rejoins on `SOH`, **with no escape mechanism**. A non-flattening variant would skip the split and join directly.

Isolated reduction of both policies (`/tmp/sohproof.c`, faithful to :1643), on the one input that distinguishes them — `f(1, (2,3))`, i.e. `args = ["1", "2"SOH"3"]`:

```
*@     len= 5 bytes=1[SOH]2[SOH]3
**@    len= 5 bytes=1[SOH]2[SOH]3
IDENTICAL: YES - representation cannot distinguish
```

**Byte-identical.** `[1, (2,3)]` and `[1,2,3]` have the same encoding. Therefore no `rest_kind` value, however plumbed, can make `**@r` behave differently from `*@r` on the current representation. Implementing it would ship a **silent wrong answer** — the exact shape the s2026-07-26c cursor itself warns about in the m4-replay-trap note.

---

## TWO LATENT CLAMPS THAT WOULD HAVE HIDDEN IT

Had the rung been attempted as specified, it would have compiled, linked, run, and **passed a naive smoke** — because a third `rest_kind` value is silently destroyed twice before it reaches the binder:

1. **`src/runtime/rt/rt.c:554`** — `g_rt_gen_procs[i].rest_kind = kind ? 1 : 0;`
   A hard clamp to `{0,1}`. `rt_proc_set_rest_kind(name, 2)` stores **1**.
2. **`src/runtime/rt/rt.c:609`** — `p->rest_kind ? rt_make_flat_agg(...) : rt_make_list(...)`
   A truthiness ternary, not a switch. Clamps independently of (1); fixing only (1) still yields flat.

Both are correct code for a two-valued fact and become wrong the instant the fact grows a third value. Neither is a bug **today**. Both must be widened *in the same edit* that introduces any third `rest_kind`, or the new value is unobservable.

⚠ **The dangerous ordering:** because all-scalar calls are identical under both policies, the obvious first smoke — `f(1,2,3)` with `**@r` → `.elems` 3 — **passes under the clamp**. Green smokes would have been read as a landed rung. The only smoke that discriminates is one whose argument is itself an aggregate, which is precisely the case the representation cannot encode.

---

## WHAT THIS MEANS FOR THE LADDER

- **`**@r` moves out of the cheap-follow-on list and onto RK-AGG.** Its true prerequisite is `RK-AGG-a`/`RK-AGG-b` (descriptor Array + nesting) — already on the ladder as "retire the `\x01` string encoding". Once an aggregate is a descriptor rather than a joined string, `**@` is genuinely the small rung the cursor described, and the two clamps above become its whole plumbing cost.
- **The cursor's items (b) and (c) are unaffected** by this finding. (b) `*%h` (SLURPY_NAMED) depends on the named-arg envelope, not on nesting. (c) `multi` + slurpy is a mangling/arity question, also independent.
- **Recommended next rung:** (b) or (c), or — if the aim is to unblock the largest set of DEFERRED tails at once — `RK-AGG-a`, which this finding adds a second independent motive for.

---

## VERIFIED BASELINE (measured live this session, at HEAD `92e926cf`, clean worktree)

Built `-O0` per the O0-DEV FACT RULE (`RT_OPT ?= -O0` confirmed intact at `Makefile:33`/`:309`; **no `-O1`/`-O2` was passed anywhere**). `scrip` 201s, `libscrip_rt.so` fresh (mtime moved — the s126 stale-artifact check). Suites driven from the clean worktree, whose runner resolves `SCRIP="${HERE}/../scrip"` to that worktree's own binary — **not** the dirty tree described below.

| Suite | m3 `--run` | m4 `--compile` | rc |
|---|---|---|---|
| Raku `test_smoke_raku.sh` | **695 PASS / 0 FAIL / 0 DECLINED** | **695 PASS / 0 FAIL / 0 DECLINED** | 0 |
| Icon `test_smoke_icon.sh` | 14 / 0 | 14 / 0 | 0 |
| SNOBOL4 `test_smoke_snobol4.sh` | 7 / 0 | 7 / 0 | 0 |

**Two things this establishes.** (1) The s2026-07-26c cursor's `695/0` claim is **TRUE and still holds** — an instance where the prose matched ground truth, worth recording since the STALE-ORIENTATION rule exists because it often does not. (2) The ZB-VAL commits that landed on top of `e9a95691` (through `92e926cf`) **did not regress Raku or its peers** — the cross-language concurrency model held.

⚠ Note the existing `slurpy_flattens_array_arg` / `slurpy_flattens_two_arrays` smokes are green. Those lock in `*@`'s **flattening**, which is exactly the behavior this finding shows `**@` cannot be distinguished from. They are correct and should stay; they simply cannot be adapted into a `**@` test.

---

## LIMITATIONS — DO NOT OVERSELL

- ~~No build was run and no suite was executed this session.~~ **DISCHARGED — the watermark WAS verified live later in the same session; see VERIFIED BASELINE below.** The *semantic* claim of this finding still rests on canonical source, on reading the SCRIP sources at `92e926cf`, and on an isolated C reduction of `rt_make_flat_agg` — **the suite run neither confirms nor refutes it**, because no `**@r` smoke exists to run. The two are independent: the baseline is green AND the rung is blocked.
- The reduction reproduces `rt_make_flat_agg`'s split/rejoin faithfully but is not the function itself; it shares no code with the runtime.
- The claim is about the **current** representation only. It says nothing about whether RK-AGG's descriptor Array should carry nesting a particular way.

---

## ⚠ UNEXPLAINED SESSION-INFRASTRUCTURE ANOMALY (recorded, not diagnosed)

A **fresh** `git clone` of SCRIP produced a **dirty working tree**. Measured:

- Clone completed **00:14:00** (reflog: single `clone:` entry; `.git/HEAD` and control file `src/lower/lower_icon.c` both mtime 00:14:00).
- Four files were written **00:25:57 – 00:27:18**, twelve minutes later: `src/contracts/rk_opname.h`, `src/parser/raku/raku.y`, `src/lower/lower_raku.c`, `src/runtime/by_name_dispatch.c`.
- No stash. No hooks. No clean/smudge filters. Worktree is on local `/dev/vda` — the only fuse mounts are `/mnt/user-data/*`, so nothing external syncs into it. No user process was running at inspection time (00:29:59).
- Every command this session ran before the discovery was read-only (`view`/`grep`/`sed`/`git log`) plus one `mkdir`/`ln -s` under `refs/`.

The diff is **coherent, competent, uncommitted work implementing cursor item (c)** (`multi` + slurpy): it introduces `RK_SLURPY_MARK`/`RK_SLURPY_TYPE` in `rk_opname.h`, teaches `rk_multi_mangle` to map the marker to a `Slurpy` type rather than mangling its raw bytes, and widens `__multi_call` to filter variable-arity candidates. **It is not this session's work and its origin is not established.**

**Actions taken — deliberately conservative:** the diff was preserved verbatim to `PRESERVED-uncommitted-raku-multi-slurpy.patch`; the working tree was **left untouched** (not committed, not reverted, not stashed); all investigation for this finding was done in a **separate clean worktree at `92e926cf`** so authorship cannot be conflated. **No claim is made about who wrote it or how it arrived.** Lon should decide its disposition — it looks like work worth keeping.
