# An interactive shell's `grep` is ugrep, `-qv` inverts, and a gate "tested" by pasting its body lies

**Seat:** hq_T (HQ-TEST, the instruments) · **Date:** 2026-09-09 · **Tree:** SCRIP `d7dc54761`
**Found while:** ruling on hq_P's s-artifact OWED ping-pong report. It nearly made me close a correct
report as mistaken.

## The measurement

```
$ type grep
grep is a function            # a Claude Code wrapper: exec -a ugrep <claude> -G --ignore-files ...
$ grep --version | head -1
ugrep 7.8.4

$ printf 'a\nb\n' | grep   -qvE '^a'; echo $?   # 1
$ printf 'a\nb\n' | grep    -vE '^a' | wc -l    # 1   <-- a line DOES fail the pattern
$ printf 'a\nb\n' | /usr/bin/grep -qvE '^a'; echo $?   # 0
```

`ugrep -qv` reports **1** on input where `grep -v` prints a line and GNU `grep -qv` reports **0**. The
non-quiet and quiet forms of the same predicate disagree with each other, in the same tool, on the same
input.

⛔ **Scripts are not affected.** The wrapper is a shell *function*, not an exported one, so `bash foo.sh`
gets `/usr/bin/grep`. That is exactly what makes this dangerous: **the script is right, and the shell you
test it in is wrong**, so the discrepancy only ever appears in the verification step.

## How it nearly inverted a ruling

hq_P reported that `util_verify_s_artifacts_owed.sh` discounted only `.file` directives while the build
path is also baked into `.string` program data, causing a permanent OWED ping-pong between seat roots. To
avoid taking an agent's report at face value I built a **detector arm** — the arm whose entire job is to
prove the OLD rule really did misfire, so that the new arm is not passing over nothing.

I ran it by sourcing the helper into my own shell. It reported that the old rule called the case **clean**
— i.e. that no ping-pong was possible and hq_P's report was mistaken. Re-run from a script file, the same
code on the same fixture reported the case **drift**, correctly, and the bug was real: on the live corpus,
a simulated foreign-root regen has the old rule call 8 files OWED and the cured rule call 0.

⭐ **The detector arm is the one that inverts.** Ordinary arms tend to fail closed — a broken `grep -qv`
makes `files_with_real_drift` report *nothing*, which shows up as an arm expecting `a.s` and getting `[]`,
and you go look. The detector arm asserts the *old, bad* behaviour is still detectable; when it silently
passes, the conclusion is "there was never a bug here", and the report gets closed. **The arm designed to
stop me passing over nothing is the arm most able to make me discard a true report.**

## The rule

**Validate an instrument by RUNNING IT, never by sourcing its internals into your interactive shell.**
`sed -n '/^fn()/,/^}/p' script.sh > /tmp/h.sh; . /tmp/h.sh` is the exact pattern that breaks — and it is
the pattern `test_gate_s_artifact_drift_ignores_the_build_path.sh` itself uses. That gate is safe *because
it is a script*; the same three lines typed at a prompt are not.

Any seat who has "confirmed" a `grep`-based gate by pasting its body into a shell should re-run it
properly. A `grep -q` in a gate is the highest-risk shape, since `-q` is where the two implementations part.

⭐ **The general form, which is this project's most-repeated lesson wearing new clothes:** an instrument
that answers a narrower question than you think you asked will never say so — and here the *instrument was
the shell itself*. The tool under test, the fixture and the assertion were all correct; the environment the
verification ran in was a different environment from the one the code ships to, and nothing announced it.

⛔ **And the same class bit the report of it, minutes later:** the telegram carrying this paragraph to the
ceo wrapped `grep`, `ugrep -qv` and `bash script.sh` in backticks, the postoffice send ran them as command
substitution, and the sentence arrived with exactly the three words it exists to name deleted. Fourth
instance in two days, third to eat its own author, in a paragraph about instruments answering narrower
questions than asked. The trap lives in the medium, not in the knowledge.
