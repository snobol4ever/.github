# FINDING — a trampoline with an odd push count entered generated code eight bytes off, and the symptom landed in glibc

**ceo, 2026-09-14. SCRIP `744f9e4ae` (cure + gate), measured on `e87ef5153`. Row `snobol4-generated-code-enters-the-c-runtime-with-the-stack-misaligned-by-eight` (open; this cures one half of it).**

## What was wrong

`rt_proc_enter_named` pushes **six** registers — `rsi` plus the five callee-saved — where its sibling `rt_proc_enter` pushes **five**, and nothing compensated for the parity flip. Generated code entered through it therefore ran with RSP 8 bytes off the convention every other entry sets, and so did every C frame it went on to call.

The compensation was not missing for want of knowing: **`rt_proc_enter_frag` does the same six pushes and then `subq $8, %rsp`, with a matching `addq $8, %rsp` in both exit paths.** One trampoline of three had the fix; the one beside it did not.

## Why it survived, which is the part worth keeping

**A misaligned stack is not an error.** It runs. Hundreds of calls return correct answers on it. It faults only when some callee happens to use a 16-byte aligned SSE store — here glibc's `vsnprintf` doing `movaps %xmm0,-0xc0(%rbp)`, reached through a `DATA()` buildplan hook that has nothing to do with the defect. So the symptom lands arbitrarily far from the cause, in another project's library, and reads as a SNOBOL4 semantic bug.

## The measurement, and the two ways I got it wrong first

⛔ **`rsp` at a gdb breakpoint is not evidence.** `break <function>` lands *after* the prologue, so the value is not comparable between sites, and my first two passes at this concluded things that were not true — including one census that flagged a healthy program as misaligned. **Frame CFAs are the right instrument**: they are unwound from real CFI and must be `0 mod 16`.

On AI SNOBOL's `SIR`, before the cure:

| | calls into the runtime | aligned | misaligned |
|---|---|---|---|
| before | 2438 | 2298 | **140** |
| after | 21536 | 21536 | **0** |
| `TEST` after | 45955 | 45955 | **0** |

The trace names the transition exactly: the last aligned call is `APPLY` at statement 498, and every call after it is off by 8. A healthy program never flips.

## The gate, and its own two defects

`test_gate_runtime_trampolines_enter_generated_code_16_byte_aligned.sh`, wired into `make preflight`, holds the whole family statically: a trampoline is entered by a `CALL`, so RSP ≡ 8 (mod 16); after N pushes and S subtracted bytes the requirement is **8 − 8N − S ≡ 0 (mod 16)**. Fail-once proven by removing the cure.

Two things it got wrong on its first runs, both now fixed and both worth stating because they are the ordinary failure modes of a census:

1. **A false red.** It flagged `rt_tiny_record_enter` — six pushes, no immediate compensation. That trampoline sizes its frame from a register (`leaq 56(%rdx),%rcx; subq %rcx,%rsp`) and restores RSP from RBP, so its parity is a runtime value the gate *cannot* compute. It now prints such trampolines as **NOT STATICALLY DECIDABLE by name**, holds them to the RBP-restore property instead, and never counts them green.
2. **A silent omission.** It missed `rt_outer_call` entirely, because that block writes `.globl` and `.type` inside one string literal and the pattern wanted a line of its own. A census that cannot say how many it did not see reports seven of eight as "all of them".

## Control arms (shared runtime)

Icon master **826/826** both modes · SNOBOL4 master **1968/1980**, crash=0, the three standing reds unchanged and each proven red without this patch · Prolog master **542/563** (541 at the last published pass) · `make preflight` 49 arms, 0 red.

## What is not cured

`SIR` now runs to **rc=0** and its output differs from the oracle (36 lines against 80, missing the `I UNDERSTAND.` lines) — a diff, not a crash. `TEST` still SIGSEGVs **with zero misaligned calls**, at a jump into `libscrip_rt.so` with a garbage return stack. That is a second defect; the row stays open naming it rather than closing on the half that is cured.
