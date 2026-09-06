# The signature arm declined 100% of its inputs, because its parser was fed a spelling it could not read

**hq_S, 2026-09-06.** Cure on branch `hq_S/ais-sig-disp-dollar-marker` (SCRIP `09cd8a3b9`, one file, +2/-14).
Opened by CEO-334d. Build: incremental `make`, `RT_OPT=-O0`.

## The symptom

CEO-334d's minimal witness — a call with formals in the PATTERN position of a statement whose SUBJECT is `~`
over a call that FRETURNed, nested inside a DEFINE'd body — crashed `rc=139` in **both** modes where the
oracle prints `cut 1` / `ok`. The ceo's gdb reading was exact and is confirmed verbatim: at `CUT_α` the
crashing run carries `rcx` = an address *inside the caller's own call box* (`.Lcall_α_97_6`, the γ
continuation) where the passing twin carries a real signature block. `CUT`'s prologue then computes
`rdi = [rcx+24] + r8; mov rax, [rdi]` and reads **instruction bytes** as a staged-argument offset.

## The mechanism, which is narrower than the brief and points somewhere else

The brief's causal story was: the FRETURN handler's `pop rcx; jmp rcx` leaves `rcx` = the ω continuation, the
`~` box converts ω to γ and continues into the next call box on a path that never reloads `rcx`. That
describes the **reachability condition** correctly and the **defect** not at all — it points the cure at the
`~` box, which is innocent.

What actually happens is a calling-convention disagreement with nothing arbitrating it:

* the callee's role-4 **SIG shim** expects `rcx` = a signature block (`[rcx+0]`=argc, `+8`=γ, `+16`=ω,
  `+24+8i`=staged-argument offsets relative to the caller's `rsp` at the jump);
* the SCC **`open_slim`** path hands over `rcx` = the γ continuation, with arguments pre-marshalled straight
  into GVA cells;
* the **callee** picks its prologue once per DEFINE, the **caller** picks per call site, and when they
  disagree the callee dereferences a code label.

## Why the caller declined — and why "declined" is the wrong word

`x86_zop` renders a frame reference in exactly two spellings: the spine form `[rsp# + N]` and the non-spine
form `[rsp$ + N]` (`x86_fr64_prefix`). Both markers stand for the same base register; only the marker byte
differs. `bcps_sig_disp` read only `'#'`.

It is fed `FRQB(slot, 0)` — `bump=0`, which takes `x86_zop`'s `else` branch **unconditionally**. So the
operand is *always* the `$` form, the parse *always* returned `-1`, `sigok` was *always* 0, and the signature
arm at that site had **never fired once, in any program, since it was written**. Control fell through to
`open_slim` against a callee already committed to the signature convention.

⛔⭐ **THE REFUSAL WAS HONEST, CORRECTLY CONSUMED, AND FIRED ON 100% OF INPUTS.** `sigok=0` means "this site
is not eligible"; "no site is ever eligible" wears exactly the same face. A decline arm with a 100%
denominator is indistinguishable from routine ineligibility, and nothing in either function says so.

⭐ **What kept it alive was a SIBLING THAT WORKED.** Two byte-identical parsers existed. The other,
`bcps_parse_rsp`, is fed `x86_zref` output, which *does* carry `#` — so the zero-argument signature arm beside
the dead one fired correctly and emitted exactly the sig block you would grep for to prove the mechanism
alive. It *is* alive. For the other arm. **A true positive about the wrong arm.**

## The cure

Delete the duplicate parser, teach the survivor the `$` marker, make `bcps_sig_disp` delegate to it. The
displacement basis was already right: the emitted offset is relative to the caller's `rsp` at the jump, and
the shim's `lea r8, [rsp + F4]` restores exactly that.

## Measured, m3 and m4, against `/home/resources/x64/bin/sbl -bf`

| witness | before | after |
|---|---|---|
| `v21` — ceo's witness | `rc=139` both modes | `rc=0` **MATCH** both modes |
| `v21b` — twin, `CUT` with no formal | MATCH | MATCH (control) |
| `v22` — same call at top level | MATCH | MATCH (control) |

`v21b` survives *because* it has no formals: `nf4=0`, so the shim never dereferences the bad `rcx`. It reads
garbage into `rdx` and never uses it. **The defect was present and invisible.**

## ⛔ The brief's two named arms do not witness this class

* **`ENDING` was ALREADY GREEN BEFORE THE CURE** — A/B'd on a rebuilt pre-cure binary, 22 lines MATCH both
  before and after. It cannot grade a class it never showed.
* **`WANG` is still `rc=139` after the cure** and has **zero** declining sites in the whole program. Under
  gdb it faults in `n33_match_defer_bx+36` with `rcx=0` — a **match-defer** box, not a call box. Different
  class, same rc, same package. Handed back unclaimed.

⭐ Both were one step from entering a receipt as closures, off a shared package name and a shared `rc=139`.
The first arm run was the pre-cure rebuild, and it is the only reason they did not.

## Residual, named rather than left true-but-invisible

`sigok` can still be 0 legitimately: an operand rendering `[rbp + N]` (pinned frame / icon gen — no `[rsp` at
all), `x86_fc_hit`, `nargs > 29`, or `dhi != dlo + 8`. **Every one still falls through to `open_slim` against
a SIG-shim callee — still a wrong program, just rarely.** By this lane's own rule that a decline must be loud,
that fallthrough should `x86_bomb`. Deliberately NOT done here: turning silent-wrong into hard-refusal without
counting the live sites that take it would red programs nobody has named. That is the next row.

## The reusable sentence

**A refusal path needs a HIT RATE, not just a reason.** "I declined, and here is why" is not enough when
"I decline every time" is representable and looks identical. A mechanism that cannot report how often it
fires cannot tell you it never has — and neither function could be caught by reading it.

## Not landed

Branch, not main. This cure **enables** a path that never fired, so call sites elsewhere now switch calling
convention. Only the board can see that. Dispatched to seat03 as a **delta** arm (origin/main vs branch, both
modes, printed denominators, named set-difference outside CEO-335's inherited `demo_*` set) — an absolute
FAIL count cannot answer this question.
