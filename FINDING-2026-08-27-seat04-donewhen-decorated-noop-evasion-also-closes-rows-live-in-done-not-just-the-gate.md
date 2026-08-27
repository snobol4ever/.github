# FINDING — seat04: the decorated-no-op DONE-WHEN hole lived in `done` itself, not only in the auditor gate — and the vacuity-probe skip that hq_C and hq_P already flagged today is the exact opening it uses to actually close a row

**Seat:** seat04 · **Date:** 2026-08-27 · **Repo/commits:** SCRIP `0ab06791` (pushed) · **Mode at time of writing:** FLEET-12
**Row:** `donewhen-decorated-noop-evasion` (rank 1, locked via `s4e_msg.sh next`)
**Related, same day:** `FINDING-2026-08-27-hq_C-the-done-certifier-had-three-ways-to-not-grade-and-two-were-environment-dependent.md` (the vacuity probe's `*/*|*'$'*` skip, characterized as "real but currently unreachable... nearly every live criterion contains `/` or `$`"); `FINDING-2026-08-27-hq_P-defect-c-done-when-was-vacuous-and-valgrind-alone-does-not-catch-it.md` §4 ("that skip is the same hole flagged to hq_C earlier today... their non-vacuity has to be established by hand").

## Claim

Both of today's findings above treat the vacuity probe's skip-on-`/`-or-`$` as leaving criteria **unautomatable** — something a human has to establish by hand. **Measured, it is worse than unautomatable: for a decorated no-op, the fallback that is supposed to cover the gap has the identical hole the probe was built to catch, so the row closes automatically, with no human in the loop at all.** Reproduced live in an isolated scratch postoffice — no risk to the real one.

## 1. The row's own assignment: the AUDITOR gate had the hole first

`test_gate_baton_donewhen_runnable.sh`'s no-op check was `tr -d '[:space:]'` then an exact-string match against `true|:|exit0|/bin/true`. seat10 proved live (2026-08-23) that `exit 0 # nothing to verify`, `: ok, done`, and `echo done` all report "runnable" — a trailing comment or a decorative argument survives whitespace-stripping, and `echo`/`true`/`:`/`exit` all resolve as real commands so the first-word-resolves check doesn't catch them either.

Fixed: a quote-aware comment stripper (`#` starts a comment only outside quoting and at word-start — real shell semantics, implemented in `awk`, never executing `$dw`) plus a "simple command" check (no `;|&`` ` ``/`$(` — sequencing is out of scope, see §4). `true`/`:`/`/bin/true` are refused with any trailing arguments (they ignore them by POSIX definition); bare `echo` is refused outright (cannot fail short of a write error); `exit 0`/`exit0` match after whitespace normalization; `printf`/`return` are WARNed, not blocked — verified empirically that `printf` can genuinely fail (bad format spec) and `return` outside a function already fails on its own (`bash -c "return 0"` → rc=2), so neither is an unconditional no-op.

**Verified, real postoffice, 279 batons, before vs. after — byte-identical:** same 24 pre-existing UNCLOSEABLE rows, same reasons (`NO DONE-WHEN`/`PROSE`/`first word not a command`), zero new catches, zero lost catches. Scratch postoffice: all three seat10 witnesses now caught (`examined 12: runnable=9 UNCLOSEABLE=3`), positive controls (bare `true`, real prose) still caught.

## 2. ⛔⭐ THE ESCALATION: the identical blocklist shape lives in `done` itself, and there it is not merely an unaudited gap — it is a working false-accept

`s4e_msg.sh done` has its own, independent no-op check (a second, hand-rolled copy of the same `tr -d '[:space:]'` exact-match idea, slightly wider: also `/usr/bin/true`, empty string, `"#"*`). It shares the exact same hole. **Two layers make this look safer than it is, and both have a gap at the same seam:**

1. The exact-match blocklist — same decorated-no-op hole as §1.
2. The **vacuity probe** (run the criterion in an empty scratch dir; refuse if it still exits 0) — a real, independent defense, but it **skips itself** whenever `dw` contains `/` or `$` (`case "$dw" in */*|*'$'*) : ;;`), exactly the condition hq_C and hq_P both flagged today from the other direction (their own criteria legitimately name paths).

For seat10's three original witnesses — none contains `/` or `$` — the probe **does** run and independently catches all three (confirmed live, scratch postoffice, pre-fix binary: all three REFUSED, claim unchanged). That is real, working defense-in-depth, and it is why the hole did not surface as a `done` incident on its own before today.

**But decorate the same no-op with a path or a variable reference — both completely natural things to put in an explanatory comment — and the probe skips itself, leaving only the broken blocklist standing. Measured on the pre-fix binary, scratch postoffice:**

| DONE-WHEN | vacuity probe | blocklist | result |
|---|---|---|---|
| `: ok, done # see /path/to/notes` | **skipped** (contains `/`) | miss (decorated) | **rc=0 — ROW CLOSED, `DONE` appended** |
| `exit 0 # nothing to verify, cf $HOME` | **skipped** (contains `$`) | miss (decorated) | **rc=0 — ROW CLOSED, `DONE` appended** |

Both closed a live scratch row end to end — `verifying DONE-WHEN (γ): ...` / `✅ DONE-WHEN exited 0 — completion is COMPUTED, not claimed.` / `done <topic>` — with zero human review and zero automated catch at any layer. This is the same shape hq_C named for the earlier three defects ("the criterion did not examine the tree, and nothing said so") but reached by a different path than any of hq_C's three or hq_P's valgrind-blindness case.

## 3. Fix and verification

Same technique as §1 (comment-strip + simple-command + args-tolerant true/:/`/bin/true`/`echo` refusal), added as `s4e_strip_donewhen_comment` plus a check block placed **before** the vacuity probe in `done`'s DONE-WHEN branch, so it does not depend on or interact with the probe's own skip condition — it is a separate line of defense at the seam the probe already declines to cover, not a change to the probe.

**Scratch postoffice, post-fix, 10 witnesses in one run:**
- 6 no-op shapes (3 original + 2 bypass + `/bin/true because reasons`) — all `⛔ REFUSED ... is a decorated shell no-op`, claims unchanged.
- `test -d /tmp` (real, passing) — closes normally, claim gets `DONE`, unaffected.
- `test -d /this/path/does/not/exist` (real, legitimately failing) — refused via the **normal execution-failure path** (`NOT DONE — the task DONE-WHEN exited 1`), confirming the new check does not misfire on genuine commands.
- bare `true`, bare `:` — still caught, by the **original**, untouched blocklist arm (message reads "is a shell no-op", not "decorated" — the two checks coexist without interfering).

`bash -n` clean on the edited file; `s4e_msg.sh check` and `next` re-run against the real postoffice afterward, unaffected (inbox read correctly, this row's held claim still resumes correctly). No other call site of the same `tr -d '[:space:]'` pattern exists in `s4e_msg.sh` (`grep -n` confirms one occurrence, now paired with the companion check).

## 4. Known limit, stated rather than hidden

Neither fix attempts to trace exit-status propagation through a compound command (`;`/`|`/`&&`/`||`/command substitution) — a DONE-WHEN like `true && exit 1` is left to the existing parse/first-word/vacuity checks, unchanged. This is a deliberate scope boundary, not an oversight: the witnesses proven live today are all bare, single-command decorations (a trailing comment or a literal argument), and chasing exit-status semantics through arbitrary shell chains is a materially larger, more error-prone undertaking than the hole actually being closed. If a chained-no-op witness is ever reproduced live the way seat10's and this session's were, it should get its own row rather than be assumed covered here.

## Receipts

- SCRIP `0ab06791` (pushed) — both fixes, `test_gate_baton_donewhen_runnable.sh` and `scripts/s4e_msg.sh`.
- Real-postoffice before/after diff of the gate: 278→279 batons across a `git pull --rebase`, 24 UNCLOSEABLE rows byte-identical by name and reason both times.
- Scratch-postoffice reproductions (this session, not committed anywhere — ephemeral by design): the two live-close witnesses in §2, the 10-witness post-fix suite in §3.
