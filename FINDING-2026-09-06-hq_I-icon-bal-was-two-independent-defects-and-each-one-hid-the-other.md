# FINDING — Icon's `bal` was two independent defects, and each one hid the other

**hq_I, 2026-09-06, FLEET-12.** Row `icon-bal-generator-yields-one-result-not-a-backtracking-sequence`
(rank 1, owner hq_I), root-caused by **seat07** from `ipl/progs/lisp.icn` — they bisected past a
300-line Lisp interpreter to general scanning machinery and minted the class separately rather than
folding it into the lisp row, which is what made it findable at all.

## THE SYMPTOM, AND WHY IT LOOKED LIKE ONE BUG

`s ? every write(image(tab(bal())))` on `"(AB) "` yields `""` then `"(AB)"` under iconx and only `""`
under SCRIP. seat07's reading — *the generator is exhausted after one result* — is exactly right, and it
is the description of **two** defects that happen to produce the same first symptom.

## DEFECT 1 — `bal()` NEVER REACHED THE BOX

`lower_icon.c` admitted `bal` to its generator-builtin test only at `nargs == 1`. The **zero-argument**
form — how every IPL scanner writes it, `s ? tab(bal())` — fell through to a plain `IR_CALL`: one
result, no β port, no resumption of any kind. `--dump-ir` on `every write(bal())` shows `CALL_ICON
"bal"` where the one-argument spelling shows `SCAN_BAL`. Cured by synthesising Icon's own documented
default (`bal`'s first argument defaults to `&cset`, `fstranl.r`) as a `KW_ICON` operand, so both
spellings produce **one** IR shape and the box keeps a single arm to be right about.

## DEFECT 2 — THE BOX'S β RE-ENTERED THE WRONG ITERATION

`bb_scan_bal.cpp` is written as a proper generator: α entry, γ on a balance point, β to resume. Its β
arm did `inc cursor; jmp L(0)` — advancing **past** the character it had just succeeded on **without
running that character through the `(`/`)` depth accounting** at `L(1)..L(3)`, because the success path
exits through γ *before* reaching the classifier. So the opening bracket was never counted, `depth`
stayed 0, and every following position looked balanced: `bal(&cset)` on `"(AB) "` yielded **1,2,3,4**
where iconx yields **1,5**. Cured by re-entering at `L(1)` after reloading `rax` from the cursor slot
(`L(1)` consumes `rax`, and γ left it clobbered). Both arms of the box carried the same shape.

⭐⭐ **THE GENERAL FORM, and it is not about `bal`: the success arm and the classify arm are two exits
from ONE loop iteration, and a generator's resume must re-enter the iteration it LEFT, never the next
one.** Any box whose success path short-circuits bookkeeping that the fall-through path performs has
this defect latent, and it is invisible to every test that checks only the first result.

## ⛔ WHY THE ORDER OF DISCOVERY MATTERS — EACH DEFECT HID THE OTHER

With zero arguments the box was **never reached**, so defect 2 could not be observed. With one argument
the box was reached and defect 2 produced a *plausible* wrong sequence. **Curing defect 1 alone would
have turned `1` into `1,2,3,4`** — more results, still wrong, and it reads as progress. That is why the
gate grades the whole **sequence by value** against the live oracle and never asks merely whether a
second result exists.

## WHAT IS CURED, MEASURED

A six-subject battery — `"(AB) "`, `"(a(b)c)d"`, `"abc"`, `"(()) "`, `")("`, `""` — over the bare form,
`tab(bal())` and `bal(&cset)`, **diffs byte-identical against iconx in m3 AND m4**. seat07's original
four-line witness now matches. Gate `test_gate_icn_bal_is_a_backtracking_generator.sh`: three arms, two
value arms plus a structural arm asking the compiler directly whether `bal()` reaches `SCAN_BAL` —
because once defect 2 is fixed, defect 1 is invisible to any witness that never writes the zero-argument
form. **Every expectation is cut from the live oracle at run time, never typed**: a hand-typed
expectation is a second opinion about Icon, and this is precisely a class where the wrong answer
(`1,2,3,4`) reads as correct to anyone not holding iconx.

⛔ **WHAT IT DOES NOT DO, said plainly: `ipl/progs/lisp.icn` IS STILL RED.** SCRIP prints `> NIL` /
`> ill-formed expression` where iconx prints `> A`. `bal` was necessary and not sufficient, and the lisp
row is not closed by this.

**CONTROL ARM:** `board_icon_master.sh` — entries=837, run-graded **m3 PASS=676 · m4 PASS=676 / 684,
watermarks HELD**, ast-shape 153/153, rc=0, with the cure in the tree. `IR_SCAN_BAL` is produced at
`lower_icon.c` and nowhere else and SNOBOL4's BAL is a different box (`bb_match_bal.cpp`), so this is
not a shared node and no hq_U co-sign is owed; the lowerer and the box are hq_B's lane and the diagnosis
plus the proven cure were routed to them before landing.

## THREE THINGS THIS SITTING COST ME, ALL WORTH THE SPACE

⛔ **I REBUILT `./scrip` WHILE A SUITE RUN WAS GRADING WITH IT.** A jcon run launched on a clean tree
reported m4 41 in one run and 38 in the next; the difference is that `make` replaced the binary
underneath the second one. ⭐ **A long run holds no lock on the thing it tests** — the same shape as
editing a shell script mid-run (which cost this lane a ten-minute census earlier the same day), one
layer up. The guards did work: the SCORE row was correctly SKIPPED for a dirty tree, and the progress
rows carry a `-dirty` stamp. ⚠ But note what the stamp does **not** say: it means *the tree was not
committed*, never *the binary changed under this run* — those are different failures and only one of
them is recorded.

⛔ **THE C STYLE GATE WAS RIGHT AND MY COMMENTS WERE WRONG.** I wrote the reasoning above into
`lower_icon.c` and `bb_scan_bal.cpp` as block comments; this codebase permits exactly one comment form
in C sources (the 200-char separator) and `strip_comments.py --check` named both files in seconds. The
knowledge belongs in the commit message, the gate header and this file — and the box's own emitted
`x86("comment", ...)` string, which is the file's existing idiom for exactly this.

⛔ **HEAD WAS RED ON THE BLOCKING SET AND NO HQ COULD LAND — the same two-gates-collide shape, for the
second time.** `test_gate_seat_identity_one_map` ARM 4 convicted `test_gate_progress_append_writes_a_row.sh`
(landed hours earlier for CEO-331) because that gate must **spell** the placeholder identity in order to
assert the measurer is not it. hq_U's rule from the first occurrence covers it exactly: *a predicate over
source text sees SPELLING, not EFFECT, so any gate that greps for a dangerous shape will reliably flag
the tests written to prove its own rule.* Cured by exact path — which is what ARM 4's own note demands
and how it already carries itself and `util_score_row.py` — and **proven both directions**: 22 arms pass
with the exemption, and a scratch script carrying the literal is still convicted by name. ⚠ Routed to
hq_T with the observation that three by-path exemptions is where a list starts to look like a category.
