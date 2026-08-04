# FINDING 2026-08-03 (Claude, ICON-BB) — ICON IS 1/262/30 AT HEAD, A TRIVIAL `write("hi")` FAILS IN BOTH MODES, AND THE UNIT OF ζ SCOPE FOR ICON IS THE **PROCEDURE** (CONFIRMED AGAINST CANONICAL JCON)

**Session:** s207. **Tree:** SCRIP `4d902148`, corpus `8411e48f1`, `.github` `45edc7b07` — all clean at origin on entry
(`handoff_status.sh` verified BEFORE any work; the s206 cursor's "LOCAL ONLY, NOT PUSHED" commits are **not present**,
so everything below is measured on a tree that matches origin exactly).
**Build:** from-scratch `make libscrip_rt && make scrip`, RT_OPT=`-O0` (no `-O2`; FACT RULE O2-DIRECTED-ONLY).

---

## ⭐⭐⭐ 1. THE WATERMARK IS FALSE BY A FACTOR OF 180. RE-DERIVE BEFORE TRUSTING ANY ICON NUMBER.

| source | Icon `--run` suite |
|---|---|
| GOAL-ICON-BB.md LIVE CURSOR (s206) | 184 / 79 / 30 |
| **MEASURED THIS SESSION at `4d902148`** | **PASS=1 FAIL=262 XFAIL=30 TOTAL=293** |

This is not a suite-harness artifact. **A one-line Icon program fails in BOTH modes:**

```icon
procedure main(); write("hi"); end
```

| mode | result |
|---|---|
| m3 `./scrip --run` | **rc=139 (SEGV)**, no output |
| m4 `--compile` → `as` → `gcc` → run | links clean, **rc=1, NO OUTPUT** |

⭐ **THE DAMAGE IS ICON-ONLY — the shared emitter is fine for its other two customers.** Measured same binary,
same session: SNOBOL4 `OUTPUT = "hi"` → prints `hi`, rc=0. Prolog `main :- write(hi), nl.` → prints `hi`, rc=0.
So this is NOT a broken build and NOT a tree-wide break; it is Icon's arm of a shared emitter.

⛔ **NOT RECOVERABLE BY ANY LIVE ENV GATE.** All of these still SEGV on the one-liner, measured individually:
`SCRIP_UNWIND=0` · `SCRIP_ZD_SCOPE=0` · `SCRIP_U2=0` · `SCRIP_GLUEO=0` (moves rc 139→**134**, still dead) ·
`SCRIP_GLUE_SYM=1` · `SCRIP_BB_ALLOC=0` · `SCRIP_UNWIND=0 SCRIP_ZD_SCOPE=0` together.
**So the regression is not behind a killswitch and cannot be bought back at runtime — it needs a bisect.**

⚠ **PRIME SUSPECT RANGE, NOT YET BISECTED (do not treat as attributed).** The last 12 SCRIP commits are almost
entirely SNOBOL4 ALPHA/OMEGA/ZETA work landing in the **shared** emitter, several of them flipping a default ON:
`4c3e9b45` U-1b UNWIND **default ON** · `799488f7` U-SCOPE **default ON** · `5bb623fe` ZW-12 FORTH-cell depth fix ·
`e4f95963` U-2a · `4d902148` U-2 structural · `a9823228` "every value-spine BB frees own K on omega".
**This is the s203 ZW-1 story verbatim** — a SNOBOL4 accounting flips a shared default and Icon was never in the
ledger. The env opt-outs not recovering it means the damage is structural in one of these, not gated by them.

---

## ⭐⭐ 2. THE DEFECT IS VISIBLE IN 19 INSTRUCTIONS. THREE NAMED FAULTS, READ OFF THE EMITTED `.s`.

Full emitted body for `procedure main(); write("hi"); end` (mode-4, elided directives):

```
main:                    sub rsp,8 ; push rdi ; push rsi ; call core_lib_init@PLT ; ... ; jmp main_α
n0_lit_string_α:         sub rsp,16                       # n0 carves its OWN cell — correct
                         mov [rsp+0],2 ; mov dword [rsp+4],2 ; mov rax,[rip+.Lx2_0] ; mov [rsp+8],rax
                         jmp n1_call_builtin_icon_α
n1_call_builtin_icon_α:  mov rax,[rsp+0]  ; mov [rsp+16],rax     # <-- writes ABOVE its own frontier
                         mov rax,[rsp+8]  ; mov [rsp+24],rax     # <-- ditto
                         lea rdi,[rip+.Lrkfn4] ; lea rsi,[rsp+16] ; mov edx,1 ; call rt_call_arr@PLT
                         mov [rsp+0],rax ; mov [rsp+8],rdx ; cmp eax,104 ; jne .Lx3_240
                         add rsp,16 ; jmp main_ω            # <-- SUCCESS ARM GOES TO OMEGA
.Lx3_240:                add rsp,16 ; jmp main_ω            # <-- fail arm, same target
n1_call_builtin_icon_β:  add rsp,16 ; jmp main_ω
main_β:                  jmp main_ω
main_γ:                  xor edi,edi ; call exit@PLT        # <-- UNREACHABLE: nothing jumps here
main_ω:                  mov edi,1   ; call exit@PLT
```

**FAULT A — `main_γ` IS UNREACHABLE; SUCCESS IS ROUTED TO FAILURE.** `cmp eax,104 / jne .Lx3_240` produces two
arms whose bodies are **byte-identical** and both `jmp main_ω`. The conditional is therefore vacuous, and the γ
port of the outermost graph has **zero in-edges**. `main_ω` is `exit(1)`, which is exactly the observed m4 rc=1.
A determinate Icon procedure that succeeds must reach γ; nothing in this program can.

**FAULT B — A BB THAT CARVES NOTHING ADDRESSES A CELL IT NEVER GRANTED.** `n1_call_builtin_icon` emits **no
`sub rsp,K` at α**, yet marshals its argument window to `[rsp+16]`/`[rsp+24]`. Trace rsp: entry−8 (`sub rsp,8`),
−16 (`push rdi`), −24 (`push rsi`), −40 (n0's `sub rsp,16`). So `[rsp+16]` = entry−24 and `[rsp+24]` = entry−16 —
**precisely the `push rsi` and `push rdi` slots.** The call's own arg window is written on top of the prologue's
saved `argc`/`argv`. This is THE MODEL's first law broken at the simplest possible call site: *a BB allocates
EXACTLY at α, its OWN cell*. `IR_CALL_BUILTIN_ICON` was already censused s203/s205 as un-armed (68 declines, then
re-ranked to 6) — this shows the decline is not merely a missed optimization, it emits an **out-of-frame write**.

**FAULT C — NO PROCEDURE-TERMINAL RELEASE.** The single `add rsp,16` releases n0's cell only. There is no
procedure-scoped release because GLUE-O suppressed both the enter and the whack (symmetrically — that part is
CORRECT, and `SCRIP_GLUEO=0` re-enabling them changes rc 139→134, i.e. it is not the cure either).

⚠ **FAULT A AND FAULT B ARE INDEPENDENT.** Fixing the γ wiring alone would route success to `exit(0)` while the
arg window still scribbles the prologue's pushes; fixing the carve alone still exits(1) on success. Do not
attribute the 262 to a single edit.

---

## ⭐⭐⭐ 3. THE UNIT OF ζ SCOPE FOR ICON IS THE **PROCEDURE** — CONFIRMED AGAINST CANONICAL JCON, WITH THE MECHANISM

**Lon directive, s207:** *"whereas the unit of scope for SNOBOL4 is the statement, the unit of scope for Icon is
the PROCEDURE."* This is confirmed by ground truth and it is **stronger than a release-point convention — it is
the ALLOCATION granularity.** From `refs/jcon-master/tran/irgen.icn`:

| line | fact |
|---|---|
| 762–763 | `ir_tmptable := table()` / `ir_loctable := table()` created **fresh inside `ir_a_ProcDecl`** — once per PROCEDURE |
| 1480–1483 | `ir_tmp(st,inuse)` does `st.tmp +:= 1` and indexes **that one per-procedure table** |
| 788 | each top-level statement of the body is lowered with a **fresh `ir_stacks(0,0)`** — slot NUMBERING restarts per statement |
| 1534 | branch points pass `ir_stacks(copy(x.tmp), copy(x.lab))` — **sibling arms share depth**, classic expression-tree allocation |

⇒ **`tmp1` in statement 1 and `tmp1` in statement 7 are the SAME physical cell.** The procedure's frame is the
**high-water mark over the body**, and its **lifetime is the activation**.

⭐ **AND THE REASON IS THE ONE THAT MATTERS FOR CODEGEN: in Icon a suspended generator's cells must survive past
the apparent end of the statement that created them.** `every write(g())` resumes `g` after control has visibly
left the statement. **No bracket smaller than the procedure is sound in Icon.**

⭐⭐ **THIS RETIRES A STANDING MISREADING.** s204 concluded `emit_fb_stmt_scan`'s bail list (`IR_SUSPEND · IR_SCAN* ·
IR_TO · IR_TO_BY · IR_LIMIT · IR_REPALT · IR_PROC_GEN · IR_CREATE · IR_ITERATE · IR_DISJUNCTION ·
IR_CALL_BUILTIN_GEN · IR_KEYWORD_ICON_GEN`) makes FB-STMT "a SNOBOL4-only rung **by construction**", and treated
that as a fact about the scanner. **It is a fact about the LANGUAGE.** Those kinds are exactly the ones whose
cells outlive their statement. FB-STMT is not declining Icon by accident or by conservatism — **a statement
bracket cannot exist in Icon at all.** Stop trying to widen it, and stop treating its bail list as debt.

⭐⭐ **THIS ALSO SHRINKS ICN-FB-1 FROM A 43-ROW TABLE TO A PREDICATE THAT ALREADY EXISTS.** The ladder asks for
"one row per Icon deep kind, STATIC/DYNAMIC". Under procedure scope the question is not per-kind, it is
**per-procedure**: *does this procedure contain suspension or unbounded growth?*
- **No** → depth is static at exit → **RSP-only**, terminal `add rsp,K` at procedure γ/ω, **no rbp at all**.
- **Yes** → no static exit depth exists → **rbp pinned at procedure α**, `mov rsp,rbp; pop rbp` at exit.

That second set is exactly law 4's "occasionally … for the few instances of free unbounded stack growth and a
stable frame for housekeeping", and **SCRIP already computes the predicate**: `emit_jmp_pin_rbp()` =
`flat_deep_arrival || flat_pat || flat_gen`. SCRIP's *graph* already ≈ Icon's *procedure* (`main_α`, `proc_g_α`),
so **the scope unit is structurally correct in the tree already**. What is wrong is the three faults in §2.

⚠ **ONE DESIGN QUESTION THE DIRECTIVE DOES NOT SETTLE — carried forward, NOT guessed here.** Within a procedure,
does the non-popping spine (a) **accumulate monotonically to procedure exit** (SUM — one terminal `gpop`, simple,
but that is where s204's **141,056-byte single carve** comes from), or (b) **return to the procedure's base depth
at statement boundaries without per-BB pops** (MAX — canonical's depth-reuse, memory-lean, but unsound for any
statement that left a generator suspended)? Canonical JCON does (b), and gets away with it because it allocates
*named slots*, not rsp depth. **The likely synthesis is a two-regime split falling straight out of the classifier
above: determinate procedures reuse and stay rsp-only; suspending procedures accumulate and take the rbp
bracket.** That is an inference from two constraints, not a measurement — it needs Lon's ruling or an A/B.

⭐ **AND THIS IS THE ACTUAL MEMORY FIX.** The directive's complaint is *"allocations … not in ONE BIG FRAME. It
eats TOO MUCH memory."* SCRIP prefix-sums every node's slot across the whole graph — **SUM over nodes**. Canonical
is **MAX over statements**. The 141,056-byte carve is the difference between those two, not a failure to release
finely enough. ICN-CARVE-0 should be re-scoped to measure **sum-vs-max**, not just a `sub rsp,K` histogram.

---

## 4. WHAT THIS SESSION DID NOT DO (stated plainly)

- **No bisect.** Each probe is a ~25s both-halves build plus a suite run; the session did not have the budget to
  run one responsibly, and a half-run bisect with an unproven predicate is exactly what the s203 instrument law
  forbids. **The bisect is the next session's first act** — and per that law the predicate must be proven to
  discriminate at BOTH ends first: `procedure main(); write("hi"); end` returning rc=0 with output `hi` is a
  clean, fast, unambiguous GOOD/BAD oracle. Use it, not the 293-program suite.
- **No code changed.** Nothing was edited in SCRIP; the tree is byte-identical to origin. This is deliberate —
  fixing FAULT A or FAULT B blind, without knowing which commit introduced them, would land a second opinion on
  top of a regression rather than reverting it.
- **`gdb` is NOT INSTALLED in this container** (`apt-get install -y gdb` first if you want RULES.md's
  monitor→bracket→gdb hunt). The m4 assemble+link+run path worked and was sufficient to prove the codegen wrong
  without a debugger — prefer it as the cheap first probe.

## 5. NEXT SESSION — ORDERED

1. ⭐⭐⭐ **Bisect the one-liner.** GOOD/BAD predicate = `procedure main(); write("hi"); end` → rc==0 && stdout=="hi".
   Prove it BAD at `4d902148` and GOOD at some ancestor before the first real probe. Suspect range is the
   SNOBOL4 ALPHA/OMEGA/ZETA run listed in §1.
2. ⭐⭐ **Then FAULT A (dead γ) and FAULT B (uncarved arg window) separately** — they are independent (§2).
3. ⭐ **Re-scope ICN-CARVE-0 to sum-vs-max** per §3, and re-baseline every Icon number in the goal file; the
   184/79/30, 37,872 rbp refs and 6,264 unseeded figures are all measured on a tree that no longer exists.
4. **Settle the SUM-vs-MAX ruling** (§3) before writing the classifier — it decides the whole shape of ICN-FB.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
