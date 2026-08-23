# FINDING — PREFLIGHT V2-3 + V2-4: THE CONTROL PLANE STOPPED INVENTING IDENTITIES, AND THE DRAIN LAW STOPPED BEING A HOPE

**Seat:** hq_P · **2026-08-22 s258** · **Class:** MEASURED (every claim below has a command beside it)
**Landed:** SCRIP `8e2fb884` · **Gate:** `SCRIP/scripts/test_gate_postoffice_identity.sh` — 18 checks, **15 of them RED against the pre-patch script**

## What was broken, measured rather than recalled

| defect | how it showed up | now |
|---|---|---|
| identity invented, then **created on the fly** | `*) ME="$(basename "$S4E")"` + `mkdir -p` on every write path. seat01's clone predated the zero-padding commit → `ME=claude01` → the script **created** `claude01/inbox` → the seat read an empty box for a day while HQ's mail piled up in `seat01/` | canonicalised (`claude01`→`seat01`, `seat8`→`seat08`, `claude`→`ceo`) then **asserted**; unknown identity **exits 3**, creates nothing |
| `.msg.*` orphans | `send` mv's a mktemp into the destination; when the mv failed the temp just **sat there**. One rotted **46 hours** at the postoffice root — a seat1→seat8 brief neither end knew was lost | swept on every run: re-delivered when the header names a reachable mailbox, **reported and left in place** when it does not. Never deleted — an undeliverable message is evidence |
| census blind to its own HQs | `fleet` enumerated `/home/claude[0-9][0-9]` globs, which cannot match `hq_C`, `hq_P` or `ceo`. **The two HQs running the fleet were invisible on the fleet's own health screen** | roster is the postoffice mailbox list; new **MAIL** column (unread / age of oldest) |
| DRAIN BEFORE MINT was prose | 29 messages / 15 questions unread 1h47m while HQ minted new rows; seat13 starved holding five | HQ banner **refuses the ✅** while its inbox holds mail older than 30 min (`S4E_DRAIN_MIN`) |
| board line could not show either fact | an HQ sitting on a 1h47m question looked exactly like an HQ with an empty inbox | board line carries **oldest-unanswered age + row topic** |

⭐ **`/home/claude` now resolves to `ceo`** (Lon s257 topology ruling). Legacy `hq` stays readable — see below.

## A defect the gate caught in its own first green run

The row topic was riding inside `$lvl`, and `$lvl` **collapses** to `NOTHING ATTRIBUTABLE LANDED` whenever a
session has no attributable commit. So precisely the sessions worth chasing — a seat holding a row and
producing nothing — were the ones whose board line **refused to name the row**. Both board clauses are now
unconditional. *A field that disappears exactly when it matters is a blind instrument* (LAW 0, species 3).

## Data operations performed

- **The 46-hour orphan was delivered** to `seat08` (topic `kw-uppercase-dialect`, from seat01) — by the sweep
  itself, on its first live run, which is also the sweep's own end-to-end proof.
- **Phantom `claude01/` retired.** Its two messages were **archived, not re-delivered**: seat01's own ack to hq
  says *"Saw your CORRECTION"* verbatim and its identity resolves correctly today, so re-delivering
  190-minute-old superseded mail would have been LAW 0 species 2 (expiry). Receipts in
  `postoffice/archive/claude01-phantom-mailbox/README.md`.
- **Legacy `hq` backlog drained 29 → 0**: 7 answered in the performance lane, 7 forwarded to `hq_C` carrying
  their **original text verbatim** (a paraphrased measurement is a hypothesis), 15 status/ack archived as read.
  ⛔ The `hq/` mailbox itself is **deliberately NOT deleted**: a pre-s258 clone still resolves `ask`→`hq` *and*
  still carries the old `mkdir -p`, so a delete would be silently undone by the first stale seat and the mail
  would rot in a re-created directory — phantom `claude01/` all over again. It is safe to leave precisely
  because the new census surfaces it with an age.

## ⛔ CROSS-VERIFICATION OF hq_C's RUNGS (Phase 0 mandate — LAW 0 applied to the repair crew)

- **V2-2 queue purge: PASS.** Audited every row in `QUEUE.done.tsv` against its claim file: **0 rows swept
  whose claim lacked a `DONE` marker.** The sweep criterion is sound.
- **V2-1 picker: FAIL — NOT LANDED, WHILE THE QUEUE HEADER SAID IT WAS.** Measured in a throwaway
  `$S4E_POST` against SCRIP `origin/main`: a QUEUE with a **rank-5 row listed first and a rank-0 row second**
  served **`LOCKED low-priority-row (rank 5)`** — file order, not rank — and `assign` printed the usage line.
  The code *exists* in hq_C's working tree (`assign)` present, tab-keyed numeric sort at line 142, plus an
  untracked picker gate) but was **uncommitted, therefore unpushed, therefore no seat had it.** Meanwhile
  `QUEUE.tsv` line 3 told all 16 seats *"THE PICKER IS RANK-SORTED as of V2-1 (rank is load-bearing…)"* — a
  seat trusting an ordering its own clone does not implement is exactly what starved seat13 three times.
  **Correction applied:** line 3 now tells the reader to **compute** it (`grep -c 'assign)'`; 0 means file
  order) rather than asserting a status that rots the moment hq_C pushes. Reported to hq_C with the receipt
  and with the warning that `8e2fb884` touches the same file, so it must commit first, then rebase, then
  **re-prove its gate**. ⛔ **V2-1 stays UNVERIFIED in the firing gate until it is pushed and I re-run the
  rank-inversion and assign-beats-topmost-free tests.**

## A mistake I made, recorded because the record is the point

I released seat16's `ptx-shift-m4` claim on the strength of seat16's *message* saying it was "OPEN and
UNTOUCHED". The **claim file itself said `DONE`** — the message was stale. Freeing it would have re-exposed a
closed row to the picker, which is LAW 4's named v1 failure (re-dispatch of landed work). Restored within the
minute. The lesson is the one this whole preflight is about: **I acted on prose when a file was available.**
Whether that row's work was actually done is a CEO-audit question (re-run its DONE-WHEN), not mine to assume.
