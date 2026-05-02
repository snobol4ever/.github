# GOAL-SNOCONE-IN-SNOCONE — Snocone Compiler Written in Snocone

**Repo:** one4all + corpus
**Done when:** the Snocone compiler — frontend (lex + parse), IR, lowering — is
written in Snocone itself, compiles its own source through scrip, and the
resulting compiler reproduces its own output. Stage 1 output equals Stage 2
output. The Snocone compiler writes itself.

This is the **second major bootstrap moment**, following Milestone 1
(SNOBOL4 beauty self-host, Session #57, 2026-04-28). Where Milestone 1
proved that scrip's SNOBOL4 frontend is faithful enough to host
beauty.sno byte-for-byte, this goal proves that Snocone is expressive
and complete enough to host its own compiler. It pairs naturally with
Milestone 2 of the THREE-MILESTONE AUTHORSHIP AGREEMENT.

---

## Status

**Empty.** Goal opened 2026-05-02 #19 by Lon. Detailed step plan to be
written in subsequent sessions. This file is the placeholder so the
goal exists in `PLAN.md` and can be claimed by an active session.

---

## Open rungs

- [ ] **SS-1** — Write the step plan. Decide which slice of the Snocone
  compiler ports first (lexer? parser? IR lowering? code emit?), decide
  which scrip backend hosts the Stage 1 binary, decide the byte-equality
  gate that closes the loop.

---

## Invariants (placeholder — confirm with Lon when SS-1 lands)

- Commit identity: LCherryholmes / lcherryh@yahoo.com.
- The Snocone source of the compiler lives somewhere under
  `corpus/programs/snocone/` (canonical destination TBD in SS-1).
- The compiler MUST be runnable under scrip without C glue —
  pure Snocone end-to-end is the bootstrap proof.
- No "patch the runtime to make this corpus file work" — same rule
  as RULES.md elsewhere.

---

## Notes

- The current Snocone compiler frontend lives at
  `one4all/src/frontend/snocone/` and is written in C (bison/flex
  grammar plus hand-written IR lowering). That stays as the Stage 0
  bootstrap host.
- Andrew's SNOCONE (1981) at `/tmp/snocone_andrew/` (when present)
  is a useful precedent — his Snocone compiler is itself written in
  SNOBOL4 and emits SNOBOL4. We are doing one step further: Snocone
  emitting its own IR and walking through scrip's IR runner.
