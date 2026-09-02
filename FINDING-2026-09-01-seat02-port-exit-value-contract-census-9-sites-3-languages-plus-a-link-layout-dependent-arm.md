# FINDING 2026-09-01 seat02 — port-exit value contract: the census, 9 live sites across 3 languages, and a NEW link-layout-dependent arm

> ⛔⛔ **CORRECTION, SAME DAY, BY seat03 — THE NUMBER IN THIS FILE'S TITLE IS WRONG. THE POPULATION IS 18, NOT 9.**
> My scanner's `OK_CALL` arm returned "rax:rdx from a DESCR-returning call" for **every** `call` reaching a
> promotion site — **a cause it never tested**. Measured by seat03: 9 of those 10 call `rt_relop_overload`
> (`arithmetic.c:58`) or `rt_jct_relop` (`by_name_dispatch.c:4951`), both of which return `int` and pass the
> DESCR out through `*out`; only `rt_assign_var` genuinely returns `DESCR_t`. Gate re-run after their fix:
> **RAW=18, OK_CALL=1.** ⭐ It mattered beyond bookkeeping — **curing "the 9" would have turned the gate GREEN
> with 9 real violations still standing**, the exact outcome this row's DONE-WHEN exists to prevent.
> ⛔ **And two of the hidden sites are FORGEABLE, which this file's "no data-dependent arm outside Pascal"
> reading understated:** `rsg.icn:1195` and `:7401` arrive with `rt_scan_sync_in`'s return (`uint64_t`,
> `scan_pos - 1`) — **scan position 105 gives low byte 104 = `DT_FAIL`.**
> **Authoritative account: `.github/FINDING-2026-09-01-seat03-port-exit-gate-ok-call-arm-asserted-descr-returning-without-checking-and-hid-half-the-population.md`; fix landed SCRIP `b4e78819`.**
> ⭐ The census AXIS below is sound and seat03 confirms it; only the call arm was not. This is the twelfth
> batch's clause landing on my own instrument: **the gap between the predicate you state and the predicate
> your script implements is invisible in the output** — my verdict string asserted the check, and the code
> never did it. Left in place, corrected here rather than rewritten, because the whole point is that it read
> as a measured result.

Row: `port-exit-value-contract-untagged-rax-forges-dt-fail` (rank 0, owner `hq_P`, class-triaged by `hq_C` from seat09's Pascal root-cause).
Mode at execution: **FLEET-8** (read from `/home/resources/postoffice/MODE`, not assumed). Tree: SCRIP `8eac17da`, corpus `90582d05`, .github `3a80d743`.
Deliverable per the baton's `## NEXT`: **the census, not a fix.** No cure was attempted — deliberately, per the brief and per the `pascal-m4-site1-forloop-backedge-64byte-excess` cure-then-revert precedent.

## 1. The contract, restated from measurement (not inherited)

`DESCR_t.v` is `uint8_t` (`src/ir/descr.h`), so the emitted `cmp al, 104` **is** the whole tag test — there is no wider check available to strengthen instead. `DT_FAIL = 0x68 = 104`.
A procedure-level success exit forwards rax:rdx as the return `DESCR_t`; confirmed by reading the emitted label, not by inference:

```
qsort_γ:            mov rdi, rax     ← rax IS the returned tag half
                    mov rsi, rdx     ← rdx IS the returned payload half
                    ... ; jmp rcx
```

So every transfer reaching such an exit must arrive with a real `DESCR_t` in rax:rdx.

## 2. The census — the axis, chosen before knowing where the defect lives

⭐ The brief warned that this fleet has been bitten four times by the census **axis**, not the effort. The tempting axis here is "grep the relop templates". I took two axes and they disagree usefully:

**(a) Source axis, `src/templates/bb/` — 573 port-exit transfer sites.** Classified by what last wrote rax: `DESCR_CALL` 260, `UNKNOWN` (join point) 137, `OTHER` 121, `DESCR_HALF` 38, **`RAW_PAYLOAD` 17 across 12 files** (known site `bb_binop_relop.cpp:37` among them — positive control passed).

⛔ **But the source axis over-reports, and reading the sites is what showed why.** I spot-verified `bb_var.cpp`, `bb_enter_init.cpp`, `bb_suspend.cpp`: they are all the same **benign shape** — rax used as scratch in a two-word DESCR copy or a payload test. **Every one of those 17 is CORRECT under the assumption that a port is control-flow-only.** They are not 17 bugs.

**(b) Emitted axis, mode-4 TEXT over 52 compiled programs — this is the real population.** 235 rax-forwarding procedure exits, 274 transfers into them: `OK_PAIRED` 173, `UNKNOWN` 47, **`RAW` 35**, `OK_CALL` 19. Nine programs across **three languages** carry a RAW transfer into a procedure exit:

| program | RAW / transfers |
|---|---|
| `prolog_recognizer.pl` | 21 / 23 |
| `family.pl` | 3 / 3 |
| `tgrlink.icn` | 3 / 11 |
| `queens.pas` | 2 / 3 |
| `perm.pas` | 2 / 7 |
| `quick.pas` (seat09's witness) | 1 / 4 |
| `fbench.pas`, `uplevel2.pas`, `uplevel3.pas` | 1 each |

## 3. ⭐ THE CLASS STATEMENT, and it is not "17 buggy templates"

**The port-exit ABI does not specify rax at all.** Templates treat rax as scratch — correctly, and it is the normal, right thing to do. Procedure-exit wiring then silently promotes rax from scratch to the DESCR return register. **Two different contracts on one label, and nothing checks which is in force.**
That is why a per-site patch list is the wrong cure: the population being patched is not wrong, and the defect re-arms the moment a new template uses rax as scratch. It is `RULES.md` § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE, sitting in the calling convention itself.

## 4. ⛔⛔ A NEW ARM THE WITNESS DID NOT SHOW: link-layout-dependent, not data-dependent

`prolog_recognizer.pl` line 360, verified by reading both ends:

```
n18_move_label_α:   mov r11, 19
                    lea rax, [rip + n20_call_prolog_α]   ← a CODE ADDRESS in the tag register
                    mov qword ptr [rsp + 16], rax        ← rax was scratch for a frame store
                    jmp nInc$2F0_γ
nInc$2F0_γ:         mov rdi, rax / mov rsi, rdx / ... ; jmp rcx   ← forwards it as the return DESCR
```

seat09's Pascal arm forges `DT_FAIL` when **user data** happens to have low byte 104. This arm forges it when **the linker** happens to place a label at an address whose low byte is `0x68` — roughly 1-in-256 per site, decided at link time and stable until unrelated code moves. Its signature is therefore *"the program broke after an unrelated change"*, which is materially harder to attribute than a data-dependent wrong answer, and it is concentrated in **Prolog** — the language FLEET-8 is currently working (`prolog-term-to-descr-eradication`). Flagged to hq_C on that ground.

## 5. The gate — `scripts/test_gate_port_exit_value_contract.sh` (+ `port_exit_value_contract_scan.py`)

Generation-time by design, per the row's own DONE-WHEN: the defect is data-dependent, so a runtime assert only ever fires on the inputs that already broke. The gate compiles witnesses to mode-4 TEXT, finds every `<proc>_γ:` that opens `mov rdi, rax`, and for each transfer into one walks backward (across fall-through boundaries) to the defining write of rax. OK iff rax:rdx came from a **paired** `[K]`/`[K+8]` load or a DESCR-returning `call`.

⭐ **PROVEN IN ALL THREE STATES before being quoted** (INSTRUMENT LAWS clause 1 — an instrument nobody has watched fail is not an instrument):
- **FAIL(1)** — 9 violations named with file, line, target label and reason, over 18 exits (default witness set).
- **PASS(0)** — 0 violations over **165** exits on clean Icon witnesses, so it is not stuck-red.
- **UNPROVEN(2)** — `gate_require_exec` (unbuilt scrip), no-witnesses, all-witnesses-fail-to-compile, and a `gate_floor` on exits examined: **"measured and clean" and "never ran" never share an output.**
- Census instrument controlled separately: neutralizing the known load dropped RAW 17→15 (it fed two transfers); injecting a synthetic one raised it to 16. It moves in both directions with the right magnitude.

⛔ **Blind spots, stated because they are part of the result:** the backward walk is dataflow-lite, not a full CFG — a block entered by a jump from elsewhere may carry a different rax. A definite raw load found this way is a TRUE positive; an `OK` verdict is only as strong as the fall-through assumption, so `OK` is reported, never certified. The 47 `UNKNOWN` are **not** proven safe — the row's own axis is "not *provably* a `DESCR_t`", and UNKNOWN is by definition unproven. It reads mode-4 TEXT and **binds mode 4 only** (MODES MAY DIVERGE).

## 6. Status against DONE-WHEN, plainly

DONE-WHEN is **NOT met and this row is not closable yet**: the gate now exists (its `[ -f ... ]` precondition is satisfied) but it is **RED at 9 sites**, because the defect is live and uncured. That is the honest state, and the gate was deliberately not weakened to green. The SNOBOL4 control-arm board was **not** run this session — no codegen was touched, so there is nothing yet for it to control; it becomes mandatory the moment a cure is attempted.

## 7. The sentinel question — asked, non-blocking, and the census adds a third option

Routed to `hq_C` as `q-port-exit-sentinel-contract-ruling`. The brief offers (a) every port exit normalizes — defence in depth, still forgeable by the next unnormalized path — or (b) the sentinel moves out of the data value space — structural, larger blast radius.
⭐ The census points at a **(c)** the brief does not list: **specify rax in the port-exit contract and check it at the one chokepoint.** `x86_jmp` / `x86_jcc` in `x86_asm.h` is the single place every port transfer passes; it already holds the concrete target label via `x86_portname(port)` and already carries an `x86_port_hook(X86H_JMP, port)` extension point. That makes the check generation-time, and — per hq_P's standing decision rule — **its correctness does not depend on this census being complete**, which no per-site patch list can claim.
