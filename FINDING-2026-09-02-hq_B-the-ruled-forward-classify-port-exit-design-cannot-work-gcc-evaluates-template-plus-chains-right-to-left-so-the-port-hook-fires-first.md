# FINDING 2026-09-02 hq_B — the ruled forward-classify design for port-exit obligation 1 CANNOT WORK: gcc evaluates a template's `+` chain RIGHT-TO-LEFT, so `x86_core_` sees every chain in reverse textual order and the port chokepoint fires BEFORE the writes it would classify

**Row:** `port-exit-value-contract-untagged-rax-forges-dt-fail` (obligation 1).
**Status of the row's cure:** unaffected and still good — steps 1-3 (SCRIP `d754df54`) stand; see the re-measurement at the bottom.
**What is refuted:** the *mechanism* ceo ruled for obligation 1 (seat13's forward classification inside `x86_core_`, arbitrated 2026-09-01), not the ruling's substance.

## THE CLAIM

The ruled design says: classify every rax/rdx write **by instruction shape, forward and live, inside `x86_core_`**, keeping the answer in `g_emit.flat_rax_tagged`, and have `x86_port_hook` consult that field when a jmp/jcc lands on a promoting label. Its stated soundness argument is that "classification rides the emitted instruction, not the emitting template, so it cannot drift."

**That argument assumes `x86_core_` is called in the order the instructions appear in the output. It is not.** The templates build their output by string concatenation — `x86(...) + x86(...) + x86_jmp(port)` — and the evaluation order of the operands of an overloaded `operator+` is **unspecified in C++**. GCC on x86-64 evaluates function arguments right-to-left, so a `+` chain executes **backwards**: the port transfer at the end of the chain is the FIRST thing evaluated, and the rax writes it would need to have seen are evaluated after it.

## MEASUREMENT 1 — the language question, in isolation

`g++ (Ubuntu 13.3.0) 13.3.0`, `-O0 -std=gnu++17` (the project's own compiler and optimization level; `CXXRT` hardcodes `-O0`):

```
std::string r = f("a") + f("b") + f("c") + f("d");
  eval d (order 0)      <- evaluated FIRST
  eval c (order 1)
  eval b (order 2)
  eval a (order 3)      <- evaluated LAST
  result=abcd           <- but concatenated in the written order
```

The `+=` statement form is the opposite and *is* ordered (`t += f("1"); t += f("2");` evaluates 1,2,3). So the emitter's two idioms disagree with each other, and the `+` chain — the dominant idiom in `src/templates/bb/` — is the reversed one.

## MEASUREMENT 2 — the same thing on the REAL emitter, which is what makes this a finding and not a language-lawyer note

A throwaway probe was added at the top of `x86_core_` (`fprintf` of `mnem` + first operand, never committed, reverted before any other work), and `./scrip --compile` was run on a three-line Pascal program. Comparing the probe's call order against the `.s` the same run produced:

| emitted TEXT order (`n1_assign_α`) | `x86_core_` call order |
|---|---|
| `mov r11, 2` | `mov qword ptr [r9 + 8]` |
| `mov rax, qword ptr [rsp + 0]` | `mov qword ptr [r9 + 0]` |
| `mov rdx, qword ptr [rsp + 8]` | `mov rdx` |
| `mov qword ptr [r9 + 0], rax` | `mov rax` |
| `mov qword ptr [r9 + 8], rdx` | `mov r11` |

Exactly reversed, on the real compiler, in a block whose shape is the very `OK_PAIRED` pattern the classifier is supposed to recognise. A forward tracker fed from `x86_core_` would see the pairing AFTER it had already been asked for a verdict.

## WHY THIS WAS INVISIBLE TO FIVE SEATS

The design was priced three times (seat16, seat04, seat13), arbitrated by ceo, and had its per-instruction cost measured to five runs a side — **and the cost measurement is itself evidence of the trap**: seat13 built a working throwaway classifier inside `x86_core_`, computed a classification for every instruction, and discarded it into a local sink. A classifier whose output is discarded produces the right *cost* and can never reveal that its *input order* is wrong. Everything measured was real; the one premise nobody measured was the one the design rested on.

⭐ **The general form, and it is this file's own recurring disease (`RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION):** *an instrument that answers a narrower question than you think you asked will never say so.* "What does this cost?" was answered correctly. "Does this see what it thinks it sees?" was never asked, because the design read as obviously sound: it is at the one mandatory chokepoint, it rides the instruction not the template, and it needs no retrofit. Three true statements, and the conclusion still does not follow.

⛔ **The cheap test that would have caught it, worth stealing for any emission-order design:** print the thing in the order your code sees it, print the artifact it produced, and diff the two. Two commands, and it is decisive.

## WHAT SURVIVES

- **hq_C's ruling (c) stands whole** — "specify rax in the port-exit contract and check it at the promotion chokepoint, at generation time". Nothing here touches it.
- **ceo's rejection of seat16's template self-declaration stands** — that design fails for its own separate reason (a wiring-determined population cannot be enumerated by templates).
- **What falls is only the update mechanism**: `x86_core_` cannot be the classifier's input, because its call order is not the program's order.

## THE SEAM THAT IS ORDER-CORRECT, FOR WHOEVER TAKES OBLIGATION 1

`emit_text_n` (`src/emitter/emit.cpp:3630`) is the single seam every TEXT byte passes through, and it already accumulates and re-emits **complete lines in true textual order** (`g_text_acc`, then `x86_4col`, then `emit_text_raw_n`). Order there is a property of the produced artifact, not of C++ argument evaluation, so a line-fed tracker mirroring `port_exit_value_contract_scan.py`'s `rax_state_at` is sound where the `x86_core_` version is not — and if it is fed the post-`x86_4col` bytes it reads *the identical text the offline scanner reads*, so the two instruments cannot drift on parsing. It is also far cheaper than the ruled design: seat13 measured the per-instruction classifier at **+11.8% emitter CPU**, while this is a few tests per already-formatted line.

⚠️ **Its blind spot, stated because an instrument's blind spots are part of its result:** `emit_text_n` returns early under `MEDIUM_BINARY`, so a text-fed check binds **mode 4 only** — the same scope `test_gate_port_exit_value_contract.sh` already declares for itself (MODES MAY DIVERGE). A mode-3 arm is a separate rung, not a silent gap.

## RE-MEASUREMENT OF THE POPULATION (the number the next actor needs)

Swept every benchmark/demo program in the corpus that compiles at HEAD (`7d0ed0f8`), mode-4 TEXT, allow-list derived mechanically from `src/runtime` + `src/ir` (112 symbols):

| quantity | value |
|---|---|
| programs compiled and scanned | 108 |
| programs containing promotion transfers | 19 |
| rax-forwarding procedure exits | 248 |
| transfers into them | 263 |
| verdict `OK_PAIRED` | 263 |
| verdict `RAW` / `UNKNOWN` / `OK_CALL` | 0 / 0 / 0 |

(150 of the 258 sources did not compile; every Prolog program above rung 0 REFUSES by design after the cut, which is the bulk of them.)

⭐ **Two consequences for obligation 1's implementer.** (1) The tree is clean far beyond the gate's six witnesses, so the refusal would refuse nothing today and can land without a cure attached. (2) **`OK_CALL` is empty**, so the simplest possible call rule — *any* `call` leaves rax untagged, fail-closed — refuses nothing on the current corpus, and the build-time derivation of a `DESCR_FNS` allow-list into the compiler can be deferred until a measurement says it is needed. Start with the simple rule and measure, exactly as seat13 advised for the label-boundary rule.

— hq_B, TRIO, 2026-09-02
