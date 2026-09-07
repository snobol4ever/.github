# FINDING — the generator-host region is a CONTAINER two orders of magnitude smaller than its CONTENTS, and no size-keyed cap can see it

**Seat:** hq_B (HQ-BEAUTIFY) · **Date:** 2026-09-06 · **Row:** `icon-generator-host-carve-sums-the-whole-component-and-reserves-66mb-on-jtran-main` (rank 0)
**Tree:** SCRIP `fb2939930`, binary built 20:38 CDT, incremental `make` (RULES.md § THE PRISTINE BUILD IS LOOSENED)
**Instrument:** `icn_gen_host_layout_audit()` in `src/templates/x86/x86_asm.h`, wired at both host-prologue arms of `src/emitter/emit.cpp`; gate `scripts/test_gate_icn_genhost_layout_consistent.sh`

## The claim

A generator callee's region is carved by its **caller** and sized `icn_gen_host_slice()`. The callee, compiled as
a host in its own right, lays out its own callee area with `icn_gen_host_reserve()`. **These are the same walk
seeded differently** — the caller's `visited` set already carries the caller's ancestors, so the caller's walk
cuts a cycle EARLY and hands over a small container, while the callee's own walk cuts it late and lays out a
large one. Container and contents are sized by two different rules, and the callee's generator call sites then
address storage past the end of the region it was given.

⛔ **That is a silent wild write, not a stack overflow.** The program compiles, links, runs, exits 0, and
corrupts whatever lies above its region. It becomes visible only when the recursion goes deep enough to reach
the shortfall — which is why three of the four programs this instrument names **match the `icont` oracle today**.

## The measurement

`SCRIP_N2_OFFSET_SELFTEST=1` on `corpus/demos/icon/jcon/jtran.icn`, 42 generator hosts:

| host | call sites | reserves |
|---|---|---|
| `main` | 6 | 66,454,176 |
| `proc_ir` | 36 | 66,092,304 |
| `proc_ir_a_ProcDecl`, `proc_ast2ir`, `proc_ir_unary_coexp`, +12 more | 1 each | ~66,10x,xxx |
| `proc_ir_a_Binop` | 5 | **246,530,256** |
| `proc_ir_a_Case` | 4 | 244,801,216 |
| `proc_ir_a_Sectionop` | 3 | 190,599,888 |

`ir` hands each of its 36 sites an average **1,836,000-byte** slice. The callee that lands in it, `ir_a_Binop`,
lays out **246,530,256 bytes** for its own callee area. **Container 1.8 MB, contents 246 MB — 134×.**

## Why the structure forces it

`irgen.icn` is **one SCC of ~41 mutually recursive GENERATORS with no ordinary proc on the cycle**.
`procedure ir(p, st, inuse, target, bounded, rval)` (irgen.icn:1358) is a generator whose whole body is
`case type(p) of { "a_Binop": suspend ir_a_Binop(...) ... }` — 40+ suspend sites — and `ir_a_Binop`
(irgen.icn:474) suspends `ir(p.left, ...)` and `ir(p.right, ...)` straight back. **The cycle's depth is the AST
depth: unbounded and data-dependent.** No static per-call-site sum can be right, and the cycle cut that keeps it
finite (`N2_SELFREC_SLOTS - 1` × the cycle's frame sum) is what makes the caller's answer and the callee's
answer disagree.

## ⭐ The reusable half: a SIZE-keyed cap is blind to this, and a CONSISTENCY-keyed one is not

My 2026-09-06 census withdrew the ceo-authorised size-keyed refusal because the carve distribution is
**bimodal** — every Icon demo/benchmark program carves exactly 65,544 except jtran (66 MB), icon_parser
(33 MB) and icon_recognizer (20 MB), with nothing in between — so any threshold that catches jtran also reds
two programs that match the oracle. That finding stands. **What it could not see is the actual defect.**

Census of all 46 `.icn` under `corpus/demos/icon` + `corpus/benchmarks/icon`: **39 clean · 3 do not compile ·
4 fire**, 117 inconsistent call sites.

    geddump.icn           1 site   host=proc_gedwalk callee=gedwalk    CONTAINER=21,824     CONTENTS=22,176
    icon_parser.icn      13 sites  host=proc_p_expr  callee=p_expr     CONTAINER=133,920    CONTENTS=5,396,032
    icon_recognizer.icn  23 sites  host=proc_r_block callee=r_stmt     CONTAINER=20,252,416 CONTENTS=20,290,096
    jtran.icn            80 sites  host=proc_ir_a_Binop callee=ir      CONTAINER=61,513,504 CONTENTS=66,092,304

⛔ **`geddump.icn` carves 65,544 bytes — the same number as every clean program in the corpus — and is still
laying out an inconsistent region.** It is invisible to the bimodal census, invisible to any threshold, and
green against the oracle. `icon_parser` is short by 5.26 MB on a single self-recursive site (40×) and also
green. **The general form: when a defect is a relationship between two computed quantities, no cap on either
quantity alone can detect it — and the quantity that is easy to measure is the one that will be capped.**

## What is built, and what it is not

`icn_gen_host_layout_audit()` is a **default-on loud diagnostic**, not a refusal. `SCRIP_ICN_GENHOST_LAYOUT_STRICT=1`
makes the compiler refuse `rc=2` at the offending host; `SCRIP_ICN_GENHOST_AUDIT=0` turns it off. **The emitted
`.s` is byte-identical with the audit on and off** — proven on jtran, one binary, one env var, the technique
from `FINDING-2026-09-06-hq_B-an-env-selectable-ceiling-turns-a-byte-identity-control-arm-into-a-one-command-diff-on-one-binary.md`.
It is REPORTED-not-blocking as a ramp because arming it today reds three programs that are green against the
oracle — the same call the xfail census and `board_packages.sh` took.

⛔ **This is the FLOOR (ceo-372 clause 2), not the cure.** The cure is per-activation, per-path carving on the
stack (Lon 2026-09-06: *"No activations on the heap"*), held by the cto as an SCC depth table. **When it lands
this audit reads zero on all 46 — that is the arm that proves it**, and it is a stronger arm than any carve
number, because it grades the layout's internal agreement rather than its size.

## ⛔ The witness the cure must not break

Two SCC entries can be **live at once in one activation**, and they must not share a slot. Minimal witness,
oracle-checked, **green in both modes today**:

    procedure g(n)
        if n <= 0 then fail;
        suspend n;
        suspend h(n - 1);
    end
    procedure h(n)
        suspend g(n);
    end
    procedure main()
        every i := g(3) do every j := g(3) do write(i, " ", j);
    end

`main` is not in the SCC `{g,h}` and has TWO call sites into it; the outer `every i := g(3)` stays suspended
holding its frame while the inner `every j := g(3)` runs. `iconx` prints 9 lines; SCRIP matches in m3 and in the
linked m4 binary. **It is green today precisely because each call site gets its own slice** — the property a
single depth-indexed table removes. A slot computed as a compile-time constant offset from the caller's own
region gives both sites the same slot.

Two more, measured the same way on origin `2a1e4cdfa` + the audit, both **MATCH iconx today** and are the
red-on-a-single-table / green-on-per-site-slices pair the stack cure's DONE-WHEN wants:

- **Member fan-out** (the cto's own shape — a member with two simultaneously live member children):
  `suspend h(n - 1) + h(n - 2)` inside `g`, `every write(g(4))` → iconx `4 5 5`, SCRIP `4 5 5`.
- **`create` across a host statement boundary** (the arm for a cursor reset at statement end):
  `e := create g(3); write(@e); x := g(2); write(x); every write(@e)` → iconx `3 2 2`, SCRIP `3 2 2`.
  The co-expression's SCC entry is live across the host's `x := g(2)` statement; it stays green under a
  statement-boundary reset only if the co-expression's table lives in its snapshot copy, not the host's.

⛔ **The audit is only as good as the pair it compares.** It reads CONTAINER from `icn_gen_host_slice` and
CONTENTS from `icn_gen_host_reserve_walk`. A cure that replaces the sizing walk must re-point both sides at
the new functions, or the audit fires on the old arithmetic and its zero says nothing about the new layout.
