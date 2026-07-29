# FINDING-2026-07-29-CLAUDE-ICN-RTX-0D-STATIC-RANK-IS-WRONG-AND-THE-TOP-THREE-ARE-COLD

**Session:** s203-ICN · **Rung:** RTX-0d-ICN (step 0(d), the relevance check) · **Landed:** measurement
only, no asm. **Gate:** `util_rtx_claims.sh` GREEN (0 fatal, 0 warn), falsification two-sided.

---

## ⭐⭐ THE FINDING

**Icon's static call-site ranking is not merely imprecise — its top three entries execute ZERO times on
the measured board, and the hottest unported C symbol sits at static rank 20.**

Measured with an LD_PRELOAD counting interposer over mode-4 linked binaries, **validated against a
positive control before any number was read** (s201 discipline), at **two loop counts with scaling
confirmed** (s188 step 0(d)):

| symbol | static sites | static rank | **queens N=6** | **queens N=8** | **deal** | scales? | state |
|---|---:|---:|---:|---:|---:|---|---|
| `rt_call_arr` | 2157 | **1** | 134 | 1,822 | 126 | **YES ~13.6×** | C, unported |
| `rt_arg_stage` | 897 | **2** | **0** | **0** | **0** | — | C, unported |
| `rt_write_any_nl` | 566 | **3** | **0** | **0** | **0** | — | C, unported |
| `rt_call_proc_descr` | 542 | **4** | **0** | **0** | **0** | — | C, unported |
| `rt_proc_set_fn` | 361 | 5 | 10 | 10 | 12 | **NO — flat** | C, unported |
| `rt_deref` | 193 | 17 | 4,372 | **69,490** | 617 | YES ~15.9× | ✅ already asm |
| `to_int` | 286 | 6 | 2,465 | **37,588** | 102 | YES ~15.2× | ✅ already asm |
| **`rt_assign_var`** | **147** | **20** | 1,119 | **15,871** | 110 | **YES ~14.2×** | **C, UNPORTED** |
| `rt_list_bang_at` | 110 | 26 | 28 | — | 10 | — | C, unported |
| `str_concat_d` | 112 | 25 | 2 | — | 23 | — | ✅ already asm |

**⭐ THE HEADLINE: `rt_assign_var` IS THE HOTTEST UNPORTED C SYMBOL ON ICON'S BOARD.** 15,871 calls at
N=8 — **8.7× `rt_call_arr`'s 1,822** — from **static rank 20**. Nothing in the static inventory
predicted it. It scales cleanly (14.2× against the workload's ~14×), so it is genuinely in the window.

**⭐ AND THE TWO SYMBOLS ABOVE IT ARE ALREADY ASSEMBLY.** `rt_deref` (69,490) and `to_int` (37,588)
dominate the dynamic board and are both already ported (`rt_asm_helpers.S`, LEAF gate). ⇒ **the prior
work already captured Icon's top two, and nobody knew it, because no Icon ladder had ever measured
dynamically.** ICON-RTX inherits a bigger head start than `ARCH-ICON-RTX.md` §0 credited it with.

---

## ⛔ WHAT THIS SETTLES — `rt_call_arr` ARBITRATION, CLOSED

The ledger blocked `rt_call_arr` on Lon because the allocation rule gave it to ICON-RTX 3.7:1 while
SN4-RTX had it open as RTX-4 SLICE 3. **The measurement dissolves the conflict rather than resolving it,
exactly as the ledger predicted it might.**

- It is **NOT s188 repeating.** For SNOBOL4, `rt_call_arr` was flat 8 across N=1→64 — setup-only. **For
  Icon it SCALES 13.6×.** It is genuinely executed in the window. The two languages reach it differently.
- **But it is not the elephant either.** 1,822 against `rt_assign_var`'s 15,871 and `rt_deref`'s 69,490.
- ⇒ **RULING: ICON-RTX DROPS ITS CLAIM. `rt_call_arr` stays with SN4-RTX.** It is not worth an
  arbitration, it is not Icon's best target, and SN4-RTX's own re-targeting analysis (fusion with
  `try_call_builtin_by_name`) applies unchanged. ICON-RTX is recorded as beneficiary.

---

## ⛔ WHAT THIS SETTLES — THE LADDER'S PHASE-1 ORDER, REWRITTEN

RTX-1-ICN as written led with the **proc-setup family** (`rt_proc_set_fn` &c., 361+210+210+209+202
static). **Measured: `rt_proc_set_fn` is 10 at N=6 and 10 at N=8 — FLAT.** That is the `rt_call_arr`
signature from s188, verbatim: per-procedure setup is executed once per procedure, not once per call, so
it is **setup-only and outside any timed window.** ⇒ **RTX-1-ICN's target is falsified before it was
written.** Re-ordered:

1. **`rt_assign_var`** (15,871, scales) — new RTX-1-ICN.
2. **`rt_call_arr`** — SN4-RTX's, ICON benefits.
3. `rt_list_bang_at` / the AGG cluster — measure first, counts are low here but the board is narrow.
4. Everything else pending a wider board.

---

## ⚠⚠ THE LIMITS OF THIS MEASUREMENT — SAY THEM PLAINLY

**TWO PROGRAMS. BOTH ALGORITHMIC.** `queens` and `deal` are backtracking/list workloads. They are **not
a board**, they are a probe. Specifically:

- **`rt_write_any_nl` = 0 while both programs visibly produce output.** That is *unexplained*, not
  evidence of coldness — Icon's write path evidently reaches a symbol not in the interposer's 15. ⛔ **Do
  not record `rt_write_any_nl` as cold on this data.** Resolve the write path first.
- **`rt_scan_enter` / `rt_scan_leave` / `rt_substr` = 0** — but **neither program scans.** This says
  nothing about the SCAN family. **A board with no string scanning cannot rule on Icon's scanning
  runtime.** The instrument is blind here, in exactly the way s188's rail was blind to AGG/ARITH.
- **The interposer covers 15 symbols.** Icon's live surface is **90**. The true #1 may not be in the list.
- `micro` produced no report (needs stdin or exits early) — not chased.

⇒ **RTX-0b-ICN (the famset) is now the blocking prerequisite, not a convenience.** It owes: a scanning
program, an I/O-heavy program, a procedure-call-heavy program, and an interposer widened to the full 90.

---

## ⭐ METHOD NOTES PAID FOR IN THIS SESSION

**(1) THE INTERPOSER HIT ARCH §7 STEP 0(c) WHILE BEING BUILT FOR IT.** First link failed:
`R_X86_64_PC32 against cnt_rt_call_arr can not be used when making a shared object`. Cause is exactly the
rule the checklist states — an exported symbol is **preemptible** and needs GOT indirection; a
visibility-**hidden** one binds `[rip+sym]` direct. Fixed by marking the counters hidden. **The
instrument for the rule broke on the rule.**

**(2) TRAMPOLINES, NOT C WRAPPERS — DELIBERATE.** These functions return `DESCR_t` in **rdx:rax**. A C
wrapper needs a prototype, and a wrong one **silently corrupts the descriptor pair instead of failing to
compile.** The interposer increments and tail-jumps in asm, preserving flags via `lahf`/`seto`/`sahf`, so
it is signature-agnostic **by construction** and cannot perturb the value contract.

**(3) ⚠ HARNESS TRAP, COST ONE FALSE READING: `LD_PRELOAD` + `timeout`.** Running
`LD_PRELOAD=x.so timeout 60 ./prog` loads the interposer into **`timeout`'s** process first, where every
`dlsym(RTLD_NEXT, …)` fails and prints `unresolved`. The first read of `deal`/`micro` looked like a
total link failure and was **not**. **Never wrap a preloaded run in another binary.**

---

## GATE STATE AT WRITING

`scripts/util_rtx_claims.sh`: **fatal 0 · warnings 0 · GREEN.** Falsification two-sided and **escalated
once**: the first double-claim probe was **SILENT** (CHECK 1 recorded only the first `OUT:` per row).
Per s204 — *a silent probe is a question, not an answer* — it was escalated rather than recorded as a
pass; the gap was real and is fixed. Both double-claim shapes (same row, different rows) now go RED and
revert clean. **The gate has been shown it can see a defect; that is why its green means anything.**

⛔ **NO SPEED CLAIM IS MADE ANYWHERE IN THIS FINDING.** No port landed. Every number above is a **call
count**, not a time.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
