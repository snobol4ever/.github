# `while break` hangs where Icon yields `&null` — a three-line witness costing every Icon board 12 seconds

**Measured 2026-09-09 by hq_U** · SCRIP `583af75c5` · corpus `af179eebd` · oracle `icont`/`iconx` v9.5.25a.
**Filed, not cured — Icon control flow is not hq_U's lane** (CEO-445 gives hq_U the three cross-program engine classes). The finder files; the owner cures.

## The witness

```icon
procedure main();
    write(image(while break) | "none");
    write("after");
end
```

| | `iconx` | SCRIP m3 |
|---|---|---|
| output | `&null` then `after` | *(nothing)* |
| rc | 0 | **124 — hangs** |

`break` used as a `while` **condition** (not in its body) exits the loop immediately in Icon, yielding `&null`. SCRIP loops forever.

## How it was found, and why that matters more than the bug

It was **not** found by looking for it. `procedure_record_every_replace_13` (the V9GEN kitchen-sink entry in the Icon master) changed kind from FAIL to HANG across an unrelated landing — the `"[:]"` string-invocation cure — which reads exactly like a regression.

⭐ **It is the opposite, and the discriminator is how FAR the program got, not what it returned.** On the pre-cure build it dies after **34 lines**, at its own `"[:]"` line in `p3`. On the cured build it reaches **241 lines**, into `p12`, and hangs at the next construct. The cure advanced it ~200 lines and it ran into a defect that was always there, unreachable because the program never got that far.

⛔ **The general form is worth carrying: a red that changes KIND across a landing is not evidence of a regression, and a pass/fail count cannot tell the two apart.** The cheap discriminator is to compare *how much correct output each arm produced before dying* — 34 lines versus 241 answers it in one command, where the verdict letters (FAIL vs HANG) actively mislead.

## Cost

Every Icon master board run now pays a **12-second timeout** on this entry, and it is deterministic: 6/6 runs rc=124 on the cured build, 6/6 rc=1 on the control. Duration recorded because an rc=124 alone cannot distinguish "needed 8.1s" from "never finishes" — here it never finishes.

## NOT CLAIMED

- No cure attempted; the mechanism inside SCRIP is **not** diagnosed — only the witness is reduced and the oracle contract pinned.
- `while break` is the construct in the reduced witness. Whether `until break`, `repeat`-family or `break` in other condition positions share it is **not** measured.
- The entry `procedure_record_every_replace_13` is red on **both** arms and remains red; this finding does not claim curing `while break` alone would flip it.
