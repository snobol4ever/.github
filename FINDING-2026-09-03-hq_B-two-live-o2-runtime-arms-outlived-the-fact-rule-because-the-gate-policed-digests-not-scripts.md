# FINDING — two live `-O2` runtime arms outlived the FACT RULE, because the gate policed digests, not `scripts/`

**Seat:** hq_B · **Date:** 2026-09-03 · **Row:** `jcon-selfhost-build-carries-a-live-o2-runtime-arm-contradicting-the-s262-fact-rule`
**Cure:** SCRIP — deletes both arms, adds `scripts/test_gate_no_o2_arm_in_scripts.sh`

## WHAT WAS TRUE

Lon's s262 FACT RULE is absolute: **NO `-O2` BUILDS, EVER** (`RULES.md` § FACT RULES; `Makefile:34` carries
`RT_OPT ?= -O0` verbatim). `test_gate_digest_matches_rules.sh` enforces it — **over the per-root `CLAUDE.md`
digests**. So it polices where the rule is *written down* and never where it is *executed*, and two live
executable arms sat in `scripts/` while every digest read clean:

1. `jcon_selfhost_build.sh` — `PERF=1` → `RTOPT='-O2 …'`, with a header sentence asserting the opposite of the
   rule: *"RULES: -O2 only for performance work"*. Routed by hq_P, assigned to hq_B. **Deleted.**
2. `build_o2_working_snobol4.sh` — **not previously reported by anyone.** Its entire purpose is
   `make libscrip_rt RT_OPT="$O2"` with `O2='-O2 …'`: a full `-O2` runtime plus a hybrid tag. **Deleted.**

⭐ **A rule enforced only against its own statement is a rule about documents.** The digest gate was working
perfectly and was never the wrong tool — it answers *"does the digest say the right thing"*, which was read as
*"is the rule obeyed"*. Same family as `command -v icont` answering *is it on PATH* and being read as *does it
exist* (`CLAUDE.md`, the oracle-path lesson): **the instrument was correct and the question was narrower than
the one everybody thought they had asked.**

## WHY DELETING THE SECOND ONE LOSES NOTHING

`build_o2_working_snobol4.sh` documented a real defect class, so this is worth stating rather than assuming:

- its backing row **`161-o2-red` is RETIRED** (`QUEUE.tsv:21`) — no live work depended on it;
- **nothing references it** outside `GOAL-HQ-COMPLETE.md:1024`;
- and that line already carries the **confirmed root cause**, in more detail than the script did:
  `rt.c` compiled at *any* optimisation allocates the BLOB-PIN registers (`rbx · r13 Σ · r14 δ · r15 Δ`,
  pinned by `rtx_abi.inc`) and breaks the pinned ABI. `r13` is necessary in every cure. **At `-O0` gcc never
  allocates them, so the pins survive by accident — which is exactly why `-O0` works and `-O1` does not.**

The script's own header called itself *"a WORKAROUND, NOT A FIX"* that *"HIDES the undefined behaviour rather
than removing it"*. It was written before the FACT RULE existed. The knowledge is in the GOAL file; the
executable violation was the only thing the file still added, and `git` keeps it recoverable regardless.

## THE GATE, AND WHY IT IS NARROWER THAN THE ROW ASKED FOR

⛔ **The row specified: grep every `scripts/*.sh` for a non-comment line carrying `-O2`. That spec is wrong,
and shipping it literally would have been worse than shipping nothing.** Measured: **26 of the scripts match**,
and the overwhelming majority are legitimate and must stay —

| shape | why it must stay |
|---|---|
| `gcc -O2 -o tools/bench_rusage` (11 scripts) | the **measurement harness itself**. Building the stopwatch at `-O0` adds the stopwatch's own cost to every benchmark number. |
| `fpc -O2` | the **rival at its released default** — the entire basis of a fair two-number three-angle comparison. |
| `build_monitor_ipc_sync_library.sh` | a separate IPC helper `.so`, not `libscrip_rt`. |

The FACT RULE governs **SCRIP's runtime optimisation level**, not every compiler invocation a script makes. So
the gate refuses exactly that: an `-O2` reaching `RT_OPT=` / `RTOPT=`. ⭐ **A gate broader than its rule gets
disabled by the first person it blocks for a good reason, and then it guards nothing** — and a gate that would
force the benchmark stopwatch to `-O0` would silently corrupt every perf number in the tree, which is a worse
outcome than the violation it was written to catch.

## ⭐ THE DETECTOR'S OWN FIRST CUT WAS WRONG IN BOTH DIRECTIONS AT ONCE

Worth recording because it nearly shipped. The first regex matched `-O2` near `RT_OPT` and:

- **flagged two lines of `test_gate_digest_matches_rules.sh`** — that gate's own *search patterns* for this very
  violation. A detector, reported as an offender.
- **missed `build_o2_working_snobol4.sh`**, whose arm reads `RT_OPT="$O2"` with `-O2` assigned to `$O2` eleven
  lines earlier. One level of variable indirection was all it took.

**A pattern that reports the detector and spares the offender is worse than no gate**, because it produces a
red that a reader learns to dismiss. The shipped gate skips lines whose first non-blank character is a quote (a
string *argument* — a grep pattern or a documented example — is never a command), then does two stages:
variables assigned a literal `-O2`, then `RT_OPT`/`RTOPT` set to a literal `-O2` **or to one of those
variables**. Proven all three ways, per the ceo's fail-once-and-pass-once ruling:

| arm | result |
|---|---|
| the original `jcon` `PERF=1` shape, alone in a fixture | **rc=1**, names `file:line` |
| legitimate `gcc -O2` bench wrapper + `fpc -O2` rival beside an `-O0` runtime | **rc=0** |
| gate whose `../scripts` does not exist | **rc=2 REFUSED** — never skip-as-success |

## CONTROL ARMS — SCRIP `dec0d7e2` + this change, corpus `2482cbf3`, RT_OPT=-O0, incremental

Documentation repointed in the same landing: `GOAL-PASCAL-100.md:56,58` told readers to run
`PERF=1 bash scripts/jcon_selfhost_build.sh`, which no longer exists.
