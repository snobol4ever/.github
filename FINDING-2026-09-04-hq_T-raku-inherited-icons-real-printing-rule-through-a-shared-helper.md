# FINDING — Raku silently inherited Icon's real-printing rule through a shared helper

**Date:** 2026-09-04 · **Measured and cured by:** hq_T · **Relocated into this file by:** hq_P
**Source:** the four `/* */` comments that stood above `rk_real_str()` in `src/runtime/by_name_dispatch.c`

## Why this file exists

⛔ **This content was written as source comments and is reproduced here VERBATIM because `src/` carries no
comments but the `/*---*/` separators** — `strip_comments.py --check` is a blocking arm of `make test`, and
those four lines were reddening it on origin/main for every seat. Deleting them to clear the gate would have
discarded a real shared-node explanation that exists nowhere else, which is the same prose-loss failure three
of us spent today ruling against in the SCORE.md write path. So the prose moved rather than died. The
attribution is hq_T's; hq_P only relocated it.

## The finding, verbatim as hq_T wrote it

> Raku prints the SHORTEST decimal that round-trips back to the same double; Icon prints 10 significant
> digits. They are different languages' rules and `rk_real_str` must not borrow Icon's.
>
> Measured 2026-09-04 (hq_T): `say sqrt(2)` printed `1.414213562` in both modes where Rakudo prints
> `1.4142135623730951` — the witness `ladder__/smoke__real_num_precision_not_truncated` (raku ALL entry
> `simple_program_37`) exists for exactly this and had gone red.
>
> CAUSE was a SHARED-NODE change graded on ONE frontend: `a15198201` re-derived `icon_real_str` to 10 sig
> figs empirically against `icont`, which is CORRECT FOR ICON, and this function delegated to it, so Raku
> silently inherited Icon's truncation. RULES.md SHARED-NODE VERDICT SCOPE names this exact shape.
>
> The cure adds Raku's own rule and leaves `icon_real_str` untouched, so Icon keeps the 10 sig figs it was
> just measured to need — branching on WHAT differs (the language's printing rule), never on a language name
> inside a shared helper.

## Why it is worth keeping

⭐ It is a **clean, correct** instance of the rule the project keeps paying to learn: a cure that is right for
the frontend it was measured on becomes a defect in every other frontend that shares the node. `a15198201`
was not careless — it measured `icon_real_str` against `icont` and got the right answer *for Icon*. The
defect was in the SCOPE of the verdict, not in the measurement.

⭐ The cure's shape is the reusable part, and it is the one `test_gate_emit_no_lang.sh` demands: the fix
branches on **what differs** — a language's real-printing rule — never on a language *name* inside a shared
helper. That is how a shared node grows a second behaviour without growing a `LANG_*` switch.

## A second-order note (hq_P)

⚠ These four lines were themselves a small instance of the same class they describe. A comment is the natural
place to explain a subtle cure to the next reader of that function — but `src/` has a repo-wide zero-comment
invariant, so the local, obviously-correct choice broke a global gate and reddened `make test` on origin for
every seat until someone graded a landing and noticed. The knowledge belonged in a FINDING from the start;
that is what FINDINGs are for, and a FINDING is greppable from anywhere while a source comment is only found
by whoever opens that file.
