# FINDING 2026-08-30 hq_B — 26 of the last 400 commits carry the forbidden harness trailers

**Tree:** SCRIP `544e8fd6` · corpus `04177c4b` · measured 2026-08-30, seat `hq_B`.

## The rule and the measurement

`CLAUDE.md` § Commits and handoff is explicit:

> Commit identity is `LCherryholmes <lcherryh@yahoo.com>` as **author AND committer**, and messages carry
> **no** `Co-Authored-By:` / `🤖 Generated with` / session-URL trailers — **this deliberately overrides the
> harness default.**

Measured across the last 200 commits of each repo:

```
SCRIP   17 / 200   carry Co-Authored-By and/or Claude-Session
corpus   9 / 200
        26 / 400   = 6.5%
```

They are spread across many seats and many subjects — icon codegen, the define purge, the demos rename,
the builder dedupe, the XFAIL re-land. **This is not one seat and it is not one session.**

## ⭐ The mechanism is that it is a DEFAULT, and defaults do not announce themselves

The rule's own wording names the cause: it *"deliberately overrides the harness default."* A rule that
overrides a default has to be actively re-applied by every session that ever commits — and nothing rejects
a commit that carries the trailers. No hook fires, no gate goes red, `handoff_status.sh` does not look.
The commit lands, is pushed, and is indistinguishable from a compliant one unless somebody reads the body.

That is the same shape as everything else found in this tree today, one layer over: **the failure mode is
silence.** A deleted guard turns nothing red; a vacuous gate prints PASS; a partial resolver returns
`None`; and a forbidden trailer is simply appended by a tool that was never told not to.

⚠️ **And it is self-reinforcing in a way the other instances are not:** every fresh session starts from the
harness default, so the population grows with seat turnover rather than with carelessness. Six months of
this is a history where the trailer is the norm and the rule is the exception, at which point the rule is
the thing that looks wrong.

## Cure — a hook, not a reminder

This is exactly the class the project has already cured three times by moving a duty out of a seat's good
intentions and into the harness (the Stop-hook banner, the inbox check, the pristine default). The
equivalent here is a `commit-msg` hook that rejects a message containing `Co-Authored-By:`,
`Claude-Session:` or `Generated with`, naming the rule.

⛔ **A reminder in `CLAUDE.md` will not do it, and the evidence is that the reminder is already there** —
in bold, with its own rationale, in the file every seat loads at session start. 26 commits landed anyway.

⚠️ Not landed by me: a `commit-msg` hook is fleet-wide infrastructure and would start rejecting commits for
every seat at once. Routed to ceo. The historical 26 are not worth rewriting — history rewriting is
forbidden and the trailers are noise, not error.

## Scope note

The identity half of the rule is **clean**: every one of the 400 commits sampled has
`LCherryholmes <lcherryh@yahoo.com>` as author and committer. Only the trailer half leaks.
