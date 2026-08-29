# FINDING 2026-08-29 (seat01) — N-2 item 3's flat_gen carve half landed; a stale inbox ruling and a live predicate-drift catch

## What landed
SCRIP `9ac7e59c` (rebased to `06d4852f`): `src/emitter/emit.cpp`'s `flat_gen` prologue arm now calls
`icn_gen_host_reserve()` and grows its own carve for its generator callees, exactly mirroring step 2b's
`flat_lcl_proc` arm — the `flat_gen` half of hq_P's LEDGER-s282 ruling ("(b), not (a)") for N-2 item 3. Full
verification ledger: `tasks/icon-n2-generator-activation-frames.task.md` § LEDGER-seat01-2026-08-29 (this file
is the reusable lessons, not a duplicate of that receipt).

## Lesson 1 — an inbox message is a doorbell, not a ruling of record; it can go stale without ever being retracted
seat01's inbox held a real, well-reasoned message from hq_P ruling option **(a)** on a fork seat01 had routed for
a decision (scope N-2 step 3 to `flat_lcl_proc`-hosted call sites only). Nothing about the message looked stale —
it named a measured fact, classified the three yield programs by host kind, and gave explicit landing guidance.
**It was superseded anyway.** The task baton's own append log carries a *later* entry (file-mtime ~45 minutes
after the inbox message, same day) headed "RULED: OPTION (a) IS UNSOUND — NOT 'SMALLER', UNSOUND", with a
constructed counter-example the (a) ruling did not have when it was written: a generator reached from *both* a
`flat_lcl_proc` host and a `flat_gen` host. Under (a), that generator's one shared prologue would be redirected to
consume a reserved region its `flat_gen`-hosted call site never supplies — not "unchanged, not worse" but a wild
`rbp` write on a call path that is *correct today*. hq_P reversed to **(b)** and never re-sent the inbox.

Nothing was misconfigured. `s4e_msg.sh`'s own design says exactly this can happen (RULES.md § THE MAIL CHANNEL:
mail delivery is "one turn of latency, not immediacy" — mid-turn messages sit unread until the recipient's next
prompt boundary), and ARCH-FLEET-CEO.md is explicit that **the baton, not the inbox, is the record** ("QA rides
the baton, newest first — inbox is only the doorbell"). The inbox told seat01 a ruling had happened; it did not
promise that ruling was still current. **Enforcement for the next reader:** when a routed fork's answer is sitting
in your inbox, cross-check the task baton's own append log before acting — especially on a rank-0, "measured and
reversed same-day" row like this one. A timestamp comparison (inbox message mtime vs. task-file mtime) settles it
in seconds and is worth doing every time, not just when something feels off.

## Lesson 2 — extending a carve and updating the predicate that classifies it are one deliverable, not two, and the gap between them is invisible without a selftest
`icn_gen_host_reserved()` exists specifically to answer "did *this* host actually reserve," classified by which
arm of `emit.cpp`'s three-arm prologue chain a graph took. Extending the `flat_gen` arm's carve without updating
this predicate in the same edit produces a *specific*, silent wrong answer: the predicate keeps reporting "no"
for a host that now genuinely reserves, so `icn_gen_host_reserve_offset()` keeps refusing exactly the call sites
the carve extension exists to serve. This is not a hypothetical — it happened here, live, in this sitting: after
landing the carve extension alone and rebuilding, `SCRIP_N2_OFFSET_SELFTEST=1` on a fresh `outer()`/`inner()`
witness read `host=proc_outer expect_off=0 got_off=-1 MISMATCH` before anything was pushed. The fix (`icn_gen_host_
reserved()`'s `flat_gen` arm returning `1`, not `0`) and the carve extension landed together, in one commit,
because shipping either half alone leaves a known-wrong predicate in the tree.

**Enforcement:** any change to which hosts a compile-time reservation mechanism covers must be re-verified against
every consumer of the classifying predicate in the same sitting — `SCRIP_N2_OFFSET_SELFTEST=1` plus
`test_icn_n2_host_reserved_agrees.sh` did this cheaply here (one build, one witness compile). This is the same
"predicate mirrors an else-if chain in another translation unit with no compiler check that it still does" class
`icn_gen_host_reserved()`'s own comment already warns about — this FINDING is a second, live instance of it firing
exactly as designed, one session after the first.

## Not a new finding, flagged for the next reader anyway
`util_verify_s_artifacts_owed.sh` (disposable clone, real corpus untouched) reports 83 owed `.s` artifacts + 3
CERR this session did not cause: the drift spans SNOBOL4 and Prolog benchmarks this Icon-`flat_gen`-only-gated
change cannot reach, and the 3 CERR names (`options`/`post`/`shuffle`) are the exact three RULES.md's own prior
measurement ("FIRST MEASUREMENT AT HEAD", § Handoff sequence step 4) already named as a standing, out-of-scope
backlog. Reproduced here only so the next session doesn't re-discover it from zero and mistake it for something
this commit broke.

## Still open
Step 3's harder half — the 4th pushed stack word as the host→generator pointer channel, generator-α's consumption
of that pointer instead of self-carving, the landing's `+32`→`+40` change and its retire-arm mirror, and the
per-callee partition of `icn_gen_host_reserve()`'s SUM — is unchanged in substance since LEDGER-s282 and was not
attempted here, matching this row's own established precedent that it "wants its own sitting with REPS-raised D2
verification, not a rushed extension."
