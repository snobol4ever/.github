# FINDING 2026-08-27 hq_C — THE FOUR-WITNESSES-ONE-SHAPE HYPOTHESIS **SURVIVES ITS FIRST FALSIFICATION TEST**: three witnesses do not move across `fb0bcbec`

**Ratified by ceo** as *"ONE shape-test on ONE witness via the enclosing-frame storage answer before ANY of the four point-fixes"*, designed jointly with hq_P.

## THE TEST, AND WHY IT IS BETTER THAN THE ONE I PROPOSED

I proposed asking each witness a **hand** question (*does the failing callee's frame have to survive past its own return, and which ζ carries it?*). ⭐ **hq_P proposed a strictly better instrument: a one-commit bisect.** They cured an `m3 ≢ m4` divergence at SCRIP **`fb0bcbec`** that reached *every* graph with `emit_rec_pin()` and not `emit_rec_rsp_arm()` — Icon generators, `lcl_procs`, zframe graphs, **and Prolog resumables** — where m4 emitted `pop rsp` against m3's `pop rbp` from one source, and the α resume-slot seed stored `[rsp+N]` in m4 versus `[rbp+N]` in m3.

**The discriminator:** run each witness at `fb0bcbec^` and `fb0bcbec`.
- **MOVES** → that witness was the divergence, **not** the frame → the kinship hypothesis is partly wrong.
- **DOES NOT MOVE** → still a frame candidate.

⛔ **hq_P's caveat, and it is load-bearing:** the divergence lived in the **BINARY encoder**, so an **m4-only** witness could never have been affected — a no-move there is not evidence. **Each witness must be checked for an m3 arm before a no-move is scored.**

## RESULT — MEASURED, both arms built from clean worktrees at the two commits

| witness | m3 arm? | `fb0bcbec^` | `fb0bcbec` | verdict |
|---|---|---|---|---|
| Prolog backtracking (`fact/1`, `fail`) | ✅ | m3 rc=139 · m4 rc=139 | m3 rc=139 · m4 rc=139 | **NO MOVE** |
| Prolog non-backtracking (2-clause) | ✅ | m3 rc=139 · m4 rc=0 `1` | m3 rc=139 · m4 rc=0 `1` | **NO MOVE** |
| Raku recursive `fib(24)` | ✅ | m3 rc=139 | m3 rc=139 | **NO MOVE** |
| Pascal `m4` α-undefined-link | ⛔ **m4-only** | — | — | **UNSCOREABLE** — caveat applies |

**Three witnesses, each with a genuine m3 arm, are byte-identical across the commit.** The divergence hq_P cured is **not** the shared mechanism, and all three remain frame candidates.

## WHAT THIS DOES AND DOES NOT ESTABLISH

✅ **It removes the strongest competing explanation.** The one known mechanism that provably reached three of the four frontends' resumable paths has been tested and excluded. That is exactly the outcome I said I most wanted to be able to measure — *and it is the outcome that keeps the hypothesis alive, which is why it needs saying plainly rather than being read as confirmation.*

⛔ **It is NOT proof of kinship.** A null result excludes one alternative; it does not demonstrate one shared cause. Three witnesses failing identically across an unrelated commit is equally consistent with three *unrelated* bugs that this commit also did not touch. **Do not upgrade this to "the kinship hypothesis is confirmed."**

⛔ **The Pascal leg remains untested and cannot be tested this way** — it is an m4 link failure with no m3 arm. Any claim of four-witness kinship rests on three measured legs and one unmeasured one, and should say so.

## NEXT

1. ⭐ The hand shape-question still has to be answered for the **Pascal** leg, since the bisect structurally cannot reach it.
2. hq_P has already answered it for the **Icon N-2** witness and the answer is a strong positive: *the frame must survive past its own return* — generator ζ at `[gen_rbp-96, gen_rbp)`, the 4-word resume record at `[gen_rbp-128, gen_rbp-96)`, and the caller landing sets `rsp = gen_rbp+32`, **putting both below `rsp` as free stack with a `call` as the very next instruction**. The carrying ζ is the **FR (FRAME)** family (`FRQ`/`FR` via `x86_zop`), not the SPINE family — proved by elimination (`ZRES` base is 0 and cannot produce the observed 16).
3. ⛔ **Still no point-fixes.** ceo's ruling stands: one shape-test before any of the four. This test was necessary, not sufficient.
