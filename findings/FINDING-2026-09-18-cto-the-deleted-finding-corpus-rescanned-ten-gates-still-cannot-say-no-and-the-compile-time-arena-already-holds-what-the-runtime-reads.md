# FINDING 2026-09-18 cto — the deleted FINDING corpus, rescanned: ten gates still cannot say no, and the compile-time arena already holds what the runtime reads

- **Seat:** cto · **Filed:** 2026-09-18 CDT · MODE EXECUTIVE
- **Trees:** SCRIP `ad42031a9` · corpus `0a9602642` · .github (this commit)
- ⛔ **LOCATION RULE (Lon, in-chat, 2026-09-18): every FINDING file lives in `.github/findings/`, NEVER in the `.github` root.** The 2231 recovered files in §0 all predate this rule and were written at the root; anything refiled from that corpus lands in `findings/`.
- **Occasion:** Lon, in-chat, 2026-09-18: *"You can use as many FINDING files as you want. I'll just delete them periodically. We should probably do a summarization when I delete. You could do that retroactively with all the ones I deleted if you would like."* then *"sure. scan those FINDING files and learn what you need."* This file is the scan's product, and the first FINDING filed since the ban lifted.

## §0 THE CORPUS, RECOVERED

**2231 distinct deleted `FINDING-*.md` paths, 22 MB, all recovered from `.github` history** into a scratch tree by walking `git log --diff-filter=D` and reading each blob at its deletion commit's parent. The two mass deletions are `f78d8b3fd` (826 files, 7.1 MB, Lon's 2026-09-04 word) and `c0d7427ee` (874 files, 6.1 MB, CEO-760); the rest are strays through 2026-09-16.

⭐ **NOTHING IS LOST — the deletions were of working-tree files, not of history.** Any one of them reads back with `git show <deletion-commit>^:<path>`. The cost of the sweeps was never the bytes; it was that **1926 distinct FINDING names are still cited by live docs, scripts and batons**, and a citation nobody can resolve is a prerequisite nobody can satisfy.

Ranked by citation count × measurement density, the top of the corpus is not evenly spread: two files (`FINDING-2026-08-22-seat16-rung-gate-false-green-audit` and `FINDING-2026-08-23-seat10-…-continued`) carry **90 citations between them**, and they are about the same thing — instruments that report success while measuring nothing.

## §1 ⛔ TEN GATES STILL CANNOT SAY NO, 26 DAYS AFTER THEY WERE NAMED

**This is a live re-measurement, not a quotation.** seat16 (2026-08-22) audited 105 of 120 scripts and found 31 CANNOT-SAY-NO; hq_P's V2-5 cured all 31 and pinned them in `scripts/test_gate_gates_can_say_no.sh`, which is still in the tree and still holds. seat10 (2026-08-23) then audited the scripts that pin never covered and named ~23 more. **That second list was never pinned.** Both files were deleted on 2026-09-16.

I re-ran seat10's list at HEAD using the ratchet's own injection verbatim — a scratch sibling root holding the gate script and nothing else, empty `src/`, empty `corpus/`, no `scrip` binary, `S4E_HOME`/`CORPUS`/`SCRIP` redirected into it:

```
examined 23: REFUSED=13 VACUOUS=10
still vacuous: test_gate_icn_one_reg_frame test_gate_port_functions test_gate_no_bb_bin_t
               test_gate_no_brokered test_gate_rbx_quarantine test_gate_ir_field_discipline
               test_gate_sm_dead test_gate_stage2_isolation test_gate_template_medium_invisible
               board_sno15_ident
```

Three inspected outputs, to show these are the real defect and not a harness artifact:

| script | what it printed after scanning NOTHING | rc |
|---|---|---|
| `test_gate_port_functions` | `string-port call-shape operands live: 0 (MUST be 0)` / `OK: all port operations route through the four port functions.` | 0 |
| `test_gate_ir_field_discipline` | `HARD TOTAL = 0` / `PASS (<= TARGET=119): discipline held — no NEW field overloading. Ratchet TARGET toward 0 as constructs convert.` | 0 |
| `board_sno15_ident` | `TRI-IDENTICAL 0/14 m3 bad=0 m4 bad=0 harness-fail=14` | 0 |

⛔ **`test_gate_ir_field_discipline` is the worst shape in the set and the reason a plain "vacuous" label undersells it.** It is a RATCHET, not a hard-zero gate. A missing scan does not merely look clean — **it looks like a huge win** (`0 <= 119`) — and the gate then *recommends tightening the target*. Acting on its own advice would entrench a false "target reached" permanently. `test_gate_sm_dead` has the identical shape against `MAX=1`.

⛔ **`board_sno15_ident` prints `harness-fail=14` — fourteen programs that did not run at all — and exits 0.** A board whose entire population failed to execute is indistinguishable, by exit code, from a clean board.

✅ **What HAS been cured since, measured the same way:** the HIGHEST-severity item in seat10's list, `test_gate_m1_self_host_fixed_point.sh` (the gate for the project's headline Milestone-1 byte-identical-fixed-point claim, which used to answer `M1 GATE: PASS` to a bogus `ARM` argument having compiled and run nothing) now returns **rc=2, `⛔ GATE UNPROVEN(2): unrecognized ARM 'bogus-arm' — expected m3, m4, or both`**, in both the wrapper and the `.github/probes/m1-bisect/` probe. `test_gate_baton_donewhen_runnable` also refuses (rc=2).

**The instruments lane is the coo's** (MODE line: THE INSTRUMENTS OFFICER). This is filed, not cured, and the coo is told; the ratchet that already exists is the obvious home — extending its pinned list is a smaller job than the original cure was, because the injection harness is already written.

## §2 ⛔ THE COMPILE-TIME ARENA ALREADY HOLDS SOMETHING THE RUNNING PROGRAM READS — AND THAT IS CORRECT, WHICH IS THE PROBLEM

This is the finding that changes work in flight, it sits in **`src/lower`, which is the cto's own directory under CEO-842**, and it comes out of a deleted file nobody can currently open: `FINDING-2026-09-13-hq_V-a-heap-block-whose-address-is-baked-as-an-immediate-into-mode-3-machine-code-can-never-be-reached-by-a-registered-slot.md`.

**hq_V's proof, recovered.** In mode 3 the emitter writes **the absolute address of a block as a 64-bit immediate inside the instruction stream it is assembling**. A slot is a memory location the collector can rewrite; **an operand embedded in emitted code is not a location the collector knows**, and registering it would mean the collector rewriting live machine code. hq_V measured the consequence directly by deleting the pinned branch of the forwarding loop: the SNOBOL4 `DATA('NODE(VAL,NXT)')` witness **SIGSEGVs in m3 and PASSES in m4**, because m4's `x86_load_ro` emits `lea dst, [rip + label]` against a fresh `.rodata` copy outside the heap while m3 emits `movabs dst, imm64` carrying the raw pointer. Their conclusion: that class must **LEAVE the collected heap, not become movable**.

**VERIFIED AT HEAD, `ad42031a9`, and the eviction has happened — under a different name:**

1. `lp_strdup` (`src/lower/lower_common.c:59`) — the lowerer's string interner, through which *every IR-side string reaches the runtime* — now allocates with **`ct_alloc`**, the compile-time arena.
2. `src/templates/bb/bb_call.cpp` still bakes those pointers as immediates at three sites, e.g. line 292: `x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t)IR_LIT(lf).sval, b1)`.
3. `src/templates/x86/x86_asm.h:135-138` confirms the medium split is live: under `MEDIUM_BINARY` this is `REX.W B8+r` — **`movabs` with the raw pointer as `imm64`** — and text otherwise.
4. The very next emitted instruction is `call_rt NV_GET_fn`, so **the running program dereferences that compile-time-arena pointer in `rdi`**. `rt_call_named_proc` (`rt.c:1805`) is the same shape for the by-name path.
5. `rt_pinned_alloc` / `rt_pinned_strdup` now have **zero hits tree-wide** — consistent with CEO-812's "no pinning in any form".

**So the design is right.** A process-lifetime, immutable, never-moved, never-collected arena block reached through an immutable immediate **needs no root, because nothing can ever invalidate the immediate**. This is precisely the `A_PROG` eviction hq_V prescribed, delivered as `ct_alloc`.

⛔ **But CEO-842's third clause, read literally, condemns it:** *"THE COMPILE-TIME ARENA MAY NOT HOLD ANYTHING THE RUNTIME CAN REACH -- that is the same evasion as malloc or a pin, one name further out, and it is reverted on sight."* The runtime demonstrably reaches `lp_strdup`'s strings. A seat enforcing that sentence on sight would revert the one arrangement that works and **reintroduce a measured SIGSEGV class** — and the file proving that is deleted.

⭐ **The predicate the rule wants is not reachability.** It is *"does the collector need to know about this block"*, and the three destinations do not currently name the class where the answer is no for a structural reason rather than a convenient one:

| class | reachable at runtime? | needs a root? | why |
|---|---|---|---|
| ordinary runtime data | yes | **yes** | it moves; a slot exists to rewrite |
| compiler-only, dead before the program runs | no | no | nothing reaches it |
| **lowerer-interned program-lifetime strings** | **yes** | **no — and CANNOT have one** | the only reference is an `imm64` inside emitted code; it never moves and is never freed |

**This is an ASK to the ceo, not a cure, and I have not edited the rule or the code.** Custody of RULES.md and MODE is the ceo's. The amendment I would propose is one sentence naming the third row by its test — *a block reachable only through an immediate baked into emitted code, in an arena that never moves and never frees, is not an evasion; it is the only correct home, and the collector is right not to know it* — plus a gate that holds the arrangement, since today nothing does.

## §3 THE GC COVERAGE BLIND SPOT, AND THE CORRECTION THAT SAVES IT

From `FINDING-2026-09-13-hq_V-the-master-corpus-does-not-exercise-the-collector-at-all-…` (deleted). Measured over every master entry with `SCRIP_ZETA_TELEM=1`, counting `[ZGC] regeneration` lines, at default settings:

```
icon ran=80  raku ran=80  snobol4 ran=80  prolog ran=80
entries_that_collect = 0 (0.0%) in all four
```

**320 entries, four frontends, zero collections.** Not a pacing artefact: forcing `LINE_MB=1` and `STRESS=100` on individual entries still yields 0; only `SCRIP_GC_STRESS=1` (collect on every allocation) makes one collect. The default GC line is 128 MB and master entries never approach 1 MB.

⛔ **The seat's own conclusion — "no board CAN red a collector defect" — is FALSE, and the file carries its own correction, which is the more useful half.** `corpus/packages/snobol4/csnobol4_suite/intval.sno` **calls `COLLECT` explicitly, twice**, and already reds on the coo's board. A program whose source says `COLLECT` drives the collector by hand: no pacing change, no environment variable, no 128 MB budget. ⭐ **`COLLECT` in the source is the cheapest collector-witness form there is** — one statement — and it is a better answer than the "add witnesses large enough to cross the GC line" the seat first proposed.

**What survives, stated correctly:** *for entries that merely allocate, the collector never runs at default settings, so board readings are not a function of collector behaviour.* Marking, rooting, slot fixup and the slide are invisible to every board the fleet publishes unless the program says `COLLECT`.

⛔ **And the reasoning error, preserved because it is the transferable part:** *"I measured collection frequency under default pacing and concluded about all board readings. I treated the collector as something only the runtime triggers, and forgot that the source language has a verb for it. A measurement over one triggering mechanism does not bound a behaviour with two."*

⛔ **The cost to a landing, which is why this matters under CEO-812.** The same seat had cleared a change with *"seven frontends, 2219 entries, 2219 identical, zero diff"*. But the changed predicates are read **only inside `gc_collect_ex`** — so if no entry collects, **the control arm never executed one line of the changed code.** It was real evidence of no collateral damage and **no evidence at all about the collector**. Under CEO-812 the four officers are rebuilding the collector now; **a corpus-wide control arm is not a collector verdict**, and any GC landing that cites one is citing the wrong number.

## §4 WHAT I TOOK FROM THE SCAN, AS THE CTO

1. **The recurring defect in this project is not in the compiler, it is in the instruments.** Two of my last three sittings turned on it: CTO-72's `fc_tables_reset` reset one counter of sixteen, and CTO-73's own row DONE-WHEN was vacuous through a backtick inside double quotes. §1 says the same thing at fleet scale, twice audited, and ten of the named scripts are still vacuous today.
2. **A ratchet that scans nothing is worse than a gate that scans nothing**, because its output reads as progress and invites tightening. Any new ratchet I write gets a coverage floor in the same commit.
3. **The three destinations of CEO-842 are two-and-a-half.** §2's class is real, is mine, and is already built correctly; what is missing is the words and a gate.
4. **A control arm is scoped to the code it actually executes.** §3's 2219-entry arm is the cautionary case.
5. **Deletion is safe; dangling citation is not.** 2231 files recovered intact, 1926 names still cited. The cure is to fold a file's measured claims into whatever cites it *before* deleting, which is the row minted alongside this file.

## §5 WHAT THIS FILE DOES NOT COVER

I read deeply into the top of the ranked corpus and the GC lineage. **2231 files were recovered; a small number were read in full.** The ranking (`citations × measurement density`) and the recovered tree are reproducible from the script shape in §0, and the untouched mass is dominated by per-suite census files whose numbers are superseded by the live progress DB. The clusters I did **not** mine and would take next: the `seat04` JSON/fence0 stack-leak pair, `seat03`'s vlist m4 SIGSEGV eval-indirect-call chain, and `hq_C`'s blob-frame-watermark family — all three are spine material in the cto's supervision area.
