# FINDING s78 — the S-2 casualty is EVERY MATCH INSIDE A DEFINE, not ARBNO; and FUNCTION RBP was absorbing the MATCH-BRACKET leak, not only the statement goto leak

**Seat:** Claude Opus 5, RBP-EARN. **HEAD:** SCRIP `996673d7` (S-1 + S-2 landed). **Status:** root cause MEASURED, fix NOT written.

## 1. The probe's own name is wrong, and that misled two seats including me

`zb_act_arbno_in_define` is the sole PASS→red mover of S-2 (FUNCTION-linkage RBP removal). Its name asserts ARBNO. **ARBNO is irrelevant.** Three-variant bisect, built and run against the live sbl oracle:

| variant | shape | result |
|---|---|---|
| `v_a` | ARBNO, **no** capture, in DEFINE | **SIGSEGV** |
| `v_b` | capture (`LEN(3) . V`), **no** ARBNO, in DEFINE | **SIGSEGV** |
| `v_c` | ARBNO **+** capture, **no DEFINE** (top level) | **PASS** (`aaa`) |

⇒ the discriminator is **MATCH ∩ DEFINE**. Neither ARBNO nor capture is load-bearing; DEFINE is.

## 2. Two suspects acquitted by experiment, not by reading

- **ARBNO ζ-FRAME exonerated:** identical SIGSEGV under `SCRIP_ARBNO_RBP=1` AND `=0`.
- **mrbp (ζ-STANDING match frame) exonerated:** identical SIGSEGV under `SCRIP_MATCH_RBP=1` AND `=0`, on both `v_a` and `v_b`.

Both were my own leading hypotheses. Both are dead. Recording them so the next seat does not re-spend them.

## 3. ROOT CAUSE, read off the emitted `.s` (`v_b`, the minimal case)

The match statement `M S POS(0) LEN(3) . V RPOS(0) :S(Y)` carves:
- `n13_var_α: sub rsp,16` — the subject producer
- `n14_match_begin_α: ... sub rsp,32` then `sub rsp,32` — **64 bytes of in-bracket match storage**

and its success exit emits **`n21_statement_end_α: add rsp,16; jmp n26_statement_begin_α`** — releasing the 16 pre-match producer ONLY. **The 64 is never released on that path.** The later `:(RETURN)` statements are each individually correct (`add rsp,16; jmp RETURN`, K=16 = their own one cell), but they run with the match's 64 still live, so the RSP-only RETURN floater (`pop rcx; add rsp,8; jmp rcx`) pops garbage and jumps to it.

**THE UNDER-RELEASE IS DELIBERATE AND DOCUMENTED.** `emit.cpp:2181` computes STATEMENT_END's gpop as `zdh_match + emit_match_begin_stfh_k()` — pre-match producers plus the stfh carve — explicitly *instead of* `_wzdepth` (the full depth including in-bracket cells), on the stated ground that *"cas_rsp_mark restore collapses all in-bracket cells."* That premise is sound **only if the match bracket's own mark-restore actually fires on the taken path**. It did not need to be true before, because the FUNCTION frame's `mov rsp,rbp` at RETURN discarded the residue wholesale.

## 4. What this means for the ladder

s77(12) said FUNCTION RBP "is currently ABSORBING the statement leak BY DESIGN." **It was absorbing MORE than that.** S-1 fixed the statement goto-out leak (measured, +10 programs). This finding shows a SECOND absorbed leak at the MATCH BRACKET level, and it is exactly the population S-3 was already scheduled to fix: **the match must whack to its own MARK at its own exits** (s75/s76's law: "every exit that DISCARDS suspended frames = loop-whack to its MARK"; mrbp named as "the one non-conformist whole-frame single-owner whack" that must convert).

⇒ **S-3 is not merely the next rung, it is the rung that closes the S-2 board.** With it, the RSP-only board should read 147 and the old RBP board becomes deletable text.

⛔ **DO NOT "fix" this by restoring the full `_wzdepth` at STATEMENT_END.** Two authorities would then release the same bytes (the bracket restore on paths where it does fire, plus the statement) — a double release, which is the mirror defect. The release belongs to ONE authority, and by the frame law that authority is the match bracket's own exit.

## 5. Reproducers (in this file, not banked as corpus witnesses — cheap to re-cut)

`v_a` / `v_b` / `v_c` above; 6 lines each, DEFINE + one match + `:(RETURN)`. `v_b` is the minimal crash and needs no ARBNO at all.
