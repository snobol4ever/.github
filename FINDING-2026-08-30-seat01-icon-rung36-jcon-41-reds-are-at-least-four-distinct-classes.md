# FINDING — the 41 red pairless icon rung/demo stems (icon-rung-ladder-absorption, hq_P's handoff)
# are NOT one bug and not even mostly one class. Triaged into (A) a long tail of small, distinct
# Icon parser grammar gaps, (B) generator/coexpr "N-2" BOMB refusals ALREADY covered by other live
# rows, (C) genuine unexamined output-content mismatches, (D) hangs. Two class-A gaps have their real
# semantics confirmed empirically against the live oracle (not from memory) — one is a safe-looking
# future fix, the other needs real design and collides with today's active coexpr work. No code
# touched.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`** (ceo all-hands, assigned hq_P+seat01;
hq_P's own handoff delegated "the 41 remaining pairless stems... YOURS IF YOU WANT IT" after wiring
the icon oracle and absorbing the first 13).

**Not a cure — triage only, same discipline as this project's other rows under active-development
risk** (the Pascal Site-1 row's history is the cautionary example: two rushed fixes on shared
machinery, both reverted). Nothing committed to SCRIP; this FINDING plus a task-file NEXT update are
the only changes.

## 0. Starting point

37 of the 41 red stems are `rung36_jcon_*` (an imported jcon-heritage suite). Re-ran
`capture-oracle-refs --lang icon` fresh (SCRIP `65d50f4a`, corpus `3813fae2c`, clean tree) to get
current per-stem reasons — unchanged from hq_P's counts (0 new green, still 41 red), confirming the
tree hasn't drifted under this row since their pass.

## 1. Class A — Icon parser grammar gaps (confirmed: SAME parse error in m3 AND m4, shared parser)

The harness's `m4=SKIP(rc=None)` label is misleading on its own: it just means `scrip --compile`
exited non-zero, collapsing "real codegen defect" and "the file doesn't even parse" into one bucket.
Direct testing shows at least 6 of the 37 are the SECOND kind — a parse error, not a compile/codegen
one — and the parser is IDENTICAL for m3/m4 (this project's own architecture: one shared
parser→lower→optimizer→emitter pipeline), so these are not m4-specific at all:

| stem | line | error |
|---|---|---|
| `proto` | 47 | `^x;` — expected expression, got `^` |
| `evalx`, `image`, `iobig` | — | same `^` gap (4 files total use bare prefix `^`) |
| `misc` | 14 | `t[]` — expected expression, got `]` |
| `recent` | 162 | same, `t[]` |
| `struct` | 81 | same, `t[]` (twice) |
| `others` | 9 | `? { ; ...}` — expected expression, got `;` |
| `errors` | 19 | `(c |||:= s)` — expected expression, got `:=` |
| `geddump` | 127 | record field list — expected `)`, got `;` |

⚠️ **Why `m3=AGREE` doesn't mean m3 actually works here, and this cost real time to notice:**
`capture-oracle-refs`'s agreement test is `kind=="PASS" and returncode==oracle_rc` — it does **not**
compare output text. A clean parse-error exit (`rc=1`) can coincidentally match an oracle `rc=1` that
happened for a completely unrelated reason. Confirmed directly: `proto` shows `m3=AGREE` against
`oracle=1`, but running `./scrip proto.icn` standalone reproduces the identical parse error at line 47,
`rc=1` — the "agreement" is two different `rc=1`s, not a working match.

**Two of these gaps had their REAL semantics checked empirically against the live oracle
(`/home/resources/icon-master/bin/icon`, resolved via `icon_bin()`) rather than trusted from memory —
memory was wrong on the first one:**

- **`^x` is NOT a general "create a new variable" operator** (my own first guess, WRONG). Empirically:
  `y := ^x` where `x` is a plain integer → `Run-time error 118: co-expression expected, offending
  value: 5`. Real Icon's `^` unary operator takes a **co-expression** and produces a refreshed copy of
  it (related to, but distinct from, the `create expr` keyword that builds a co-expression from
  scratch — `TT_CREATE`, already used at `icon_parse.c:617`, is almost certainly the WRONG node to
  reuse for this, since the two operations differ). ⛔ **Implementing this correctly means real design
  work in the co-expression runtime (`rt_coexpr.c`), and SCRIP's coexpr subsystem is under active,
  delicate development THIS SAME SESSION** — `git log` shows `42a6260f apply-call to generator CURED
  both modes: coswitch rax-clobber landmine + N-2 region for the coexpr window + spine_prep refusal +
  suspend_apply witness`, today. **Not attempting this — wrong week to add a second cook to that pot.**
- **`t[]` (empty subscript list) IS accepted by real Icon** and, empirically, produces zero results
  silently (`every write(t[])` on a populated table wrote nothing, `rc=0`, no error) — a much smaller
  ask than `^`: SCRIP's subscript-list grammar currently requires ≥1 expression inside `[...]`; real
  Icon allows zero, evaluating to an always-fails expression. **Looks like the safer candidate of the
  two** — parser-only in shape, well-understood target semantics — but NOT attempted here: confirming
  it doesn't also need lowering/emitter changes (subscript codegen presumably assumes ≥1 index) takes
  more runway than this pass had, and a half-verified parser change is exactly the kind of thing this
  project's own history (Pascal Site-1/Site-2) warns against landing without a control battery.
- `others`, `errors`, `geddump`'s gaps are NOT individually characterized this session — only located.

## 2. Class B — generator/coexpr "N-2" BOMB refusals, ALREADY TRACKED elsewhere, not new work

The `CRASH rc=-6` stems (`btrees`, `collate`, `cxprimes`, `genqueen`, `var`, `prefix`) are **not**
memory corruption. Checked `collate` directly: `--compile` succeeds (6796-line `.s`), and the crash is
a **deliberate, self-diagnosing refusal**: `libscrip_rt: BOMB — N-2 armed: generator call site has no
reserved region (flat_gen host or forward reference) -- transitive reserve is the follow-on row;
refusing loudly instead of emitting a wild-rbp protocol`. ⭐ **`grep -rl "N-2\|transitive reserve"
postoffice/tasks/` turns up an entire already-live family**: `icon-apply-to-generator-segv-bb-call-
value-has-no-n2-awareness.task.md`, `icn-recogn-genqueen-suspend-shape.task.md` (note: `genqueen` by
name — literally one of this row's own crash stems), `icon-n1-wire-stack-crossing.task.md`,
`icon-n3-scan-one-depth-authority.task.md`, `icon-n6-fail-zero-residue.task.md`, and today's git log
shows active same-day commits against exactly this machinery. **These 6 crash stems are very likely
going to clear on their own once that already-in-flight work lands — re-investigating them under this
row would duplicate work already owned elsewhere, not discover something new.** Recommend: track, do
not re-diagnose.

## 3. Class C — genuine output-content mismatches, NOT examined individually this session

Checked one (`args`): compiles and runs cleanly in both modes, `rc=0` matching the oracle, and produces
plausible-looking real output (`p0`, `p1 list`, `p2 list list`, ...) — the disagreement is somewhere in
the actual text, not a crash or parse error. Did not byte-diff against the oracle to find the exact
divergence. **Likely candidates for the same class** (rc agrees with oracle, kind is FAIL not
CRASH/SKIP): `arith`, `case`, `checkfpx`, `ck`, `errkwds`, `every`, `large`, `level`, `nargs`, `scan`,
`scan2`, `sets`, `sorting`, `gener`, `radix`, `fncs`. **Given this row's own class-A lesson — assume
this is ALSO a long tail of several distinct small bugs, not one shared cause, until checked** (the
inverse of the trap this project's RULES.md already names: don't assume unity any more than you'd
assume 41 independent causes without looking).

## 4. Class D — hangs (2 stems, different in kind)

- `lgint`: SCRIP itself hangs, both modes — a real defect, not characterized further.
- `toby`: **the ORACLE itself hangs** (per hq_P's original note, confirmed unchanged). This one may not
  be gradable against this oracle at all — a scope question, not a SCRIP defect.

## 5. Not investigated this session

`generators`, `meander` (non-rung36 stems), `rung38_cset_embedded_nul` — all separate, not looked at.
The config/ flatten (companions, docs) and `.s` artifact sweep hq_P's own NEXT named are also untouched
— this pass focused entirely on triaging the 41.

## 6. Not attempted

No code touched anywhere (`git status --short` clean throughout, checked not assumed) — same restraint
as every other row in this project under similar shared-machinery or active-concurrent-work risk.
**Concrete next steps, in the order this FINDING would prioritize them:**
1. `t[]` empty-subscript: verify whether it's parser-only or also needs lowering/emitter changes, then
   attempt it with the usual control battery (SNOBOL4 blocking set + a wider Icon board, not just the
   3 files it would directly fix).
2. Byte-diff two or three Class-C stems (`args` first, output already captured) to see whether Class C
   is itself one shared cause or, like Class A, several.
3. `others`/`errors`/`geddump`'s three remaining ungrouped parse gaps — same treatment as `^`/`t[]` got
   here (locate the exact grammar production, check real semantics empirically, don't guess).
4. Class B: nothing to do here — watch the existing `icon-n*` rows instead.
5. `^`: leave alone until the coexpr subsystem's active work settles; revisit then.

## 7. State

SCRIP `65d50f4a` · `.github` fbae126e (pre-this-commit) · corpus `3813fae2c` — all pulled fresh at
session start, zero local edits anywhere. Oracle: `/home/resources/icon-master/bin/icon`, resolved via
`lib_oracle_flags.sh icon_bin()`. Mailing hq_P (co-assignee, holds the row's claim).
