# ⛔⭐⭐⭐ GOAL-RAKU-100 — RAKU AS THE FOURTH MUSKETEER: ONE Seq MACHINE, ONE PLAN, ONE FILE

Consolidated 2026-08-28 (seat15, on ceo/Lon's order — see LEDGER) from the five prior Raku goal files
(GOAL-LANG-RAKU.md, GOAL-PARSER-RAKU.md, GOAL-PST-RAKU.md, GOAL-RAKU-BB.md, GOAL-RAKU-FRONTEND.md — see
RETIRED NAMES), on the exact pattern of GOAL-SNOBOL4-100.md / GOAL-ICON-100.md / GOAL-PROLOG-100.md.
**Consolidation is a MOVE, not a rewrite** — this file carries every live law, ruling and open rung from
the five sources forward with its original wording and provenance; only settled/superseded history is
compressed to a pointer. Where two sources disagreed, both readings are kept, dated, with the conflict
named rather than silently resolved.

## ⭐⭐⭐ FRONT STATUS

Raku is a **goal-directed language riding the same four-port Byrd-box machine as SNOBOL4/Icon/Prolog** —
its generative core (`gather`/`take`, `map`/`grep`, lazy ranges, junctions) is ONE thing, a **Seq**, pulled
through the identical port protocol Icon's generators already use (see THE MODEL below). Raku is
**post-SMX-4**: there is no separate Stack-Machine engine; source lowers through the ONE unified
`src/lower/lower.c` (`lower2()`, `cx.lang==IR_LANG_RKU` arms inside the shared `tree_e` switch) to the
shared `IR_t` four-port graph, emitted by the ONE `src/emitter/emit_core.c` dispatch to per-box templates
under `src/emitter/BB_templates/bb_rk_*.cpp`. Mode 2 (`--run`, the old BB-graph interpreter) was **DELETED
2026-06-15**; only mode-3 (`--run`, BINARY) and mode-4 (`--compile`, TEXT) exist, matching every other
language in this repo.

**CURRENT WATERMARK: `test_smoke_raku.sh` = 724 PASS / 0 FAIL, both modes** (s2026-08-08b, SCRIP commit
`0ce21c92`, RK-GRAM-3d-m3-fix — see LIVE CURSOR). Peers at that commit: Icon 14/0, SNOBOL4 6/1
(pre-existing, unrelated), Prolog 4/1 (pre-existing, unrelated). **⛔ Do not quote the older 719/0 figure
from RK-ZC-8's own gate note as current — 724/0 supersedes it (+5 GALT alternation smokes landed after).**

**Raku runs on FOUR PARTLY-INDEPENDENT LADDERS, not one** — this is a genuine structural difference from
the SNOBOL4/Icon/Prolog files and is not papered over here: (1) the **goal-directed core** (ζ-storage
regime, generator/Seq machinery, grammar/regex engine — was GOAL-RAKU-BB.md), (2) the **pattern-based
Snocone frontend** `parser_raku.sc` on its own `parser` branch (was GOAL-PARSER-RAKU.md), (3) the **Pure
Syntax Tree** rewrite of that same frontend (was GOAL-PST-RAKU.md, PRF-14), and (4) two now-superseded
foundational ladders describing Raku's original C frontend and its pre-SMX-4 execution model (were
GOAL-LANG-RAKU.md and GOAL-RAKU-FRONTEND.md). See THE LADDERS below, one subsection per track.

## ⛔⛔⛔ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat)

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell,
parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit
in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We
do not do that here. ██** Enforcement: every diff is checked for new file-scope definitions; a commit adding
one without a cited in-chat grant is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires /
RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating. **⛔ THE ASK ITSELF
MUST BE A BANNER:** any session requesting this permission MUST display the request in-chat as a large
unmissable ⛔ banner — the proposed global's name, type, owning file, purpose, and why registers/the stack
cannot carry it. A quiet or inline ask does not count. (Lon 2026-08-13 s55, in-chat; carried byte-identical
from all five source files.)

## ⛔⛔ FACT RULE — NO `-O2` BUILDS. EVER (Lon s262 — supersedes this file's own retired O0-DEV text)

`RT_OPT` is `-O0` for development AND benchmarks AND demos. Never pass `RT_OPT="-O2 …"`, never build an
`-O2` RT_TAG, never quote an `-O2` number as current state. Authority: `RULES.md` § NO `-O2` BUILDS (s262).

⚠ **CONFLICT, NOTED RATHER THAN SILENTLY RESOLVED:** the retired GOAL-RAKU-BB.md carried its own dated FACT
RULE, **O0-DEV (Lon directive, 2026-07-21 s119)**: *"While developing, debugging, or iterating on any
FEATURE, EVERY build is `-O0`. `-O1` and `-O2` are FORBIDDEN during feature work and are reserved
EXCLUSIVELY for perf/benchmark/release measurement"* — i.e. s119 treated `-O2` as legitimate for
perf/bench/release. **s262 (2026-08-23, dated over a month later) is stricter and wins: there is no arm,
including perf/bench, that justifies `-O2` any more** — the reasons given at s262 are cost (~9m30 vs ~1m40
per template-touching rebuild) and that `-O2` grades a C runtime slated for deletion in favor of
register-aware ASM. The s119 mechanical anchor (`Makefile RT_OPT ?= -O0` default, `PERF=1
jcon_selfhost_build.sh` as the opt-in) is now itself stale in its framing (it still describes `-O2` as a
sanctioned perf path) but the underlying Makefile default (`-O0`) is exactly what s262 also wants, so no
build-system change follows from this correction — only the "when is `-O2` OK" answer changes, to "never."

## ⚙️ CONCURRENT BY DEFAULT — AND THE REPOS MOVE UNDER YOU

**Many seats run this file's siblings at the same time. Edit any file, commit and push whenever a rung is
buildable and green — mid-session, per rung. Never park work or refuse an edit on concurrency grounds;
stranding has cost this project far more than merging ever has.** `git pull --rebase` before every push;
**re-prove this file's gate/watermark after any rebase** — shared state moves under you and a watermark
measured pre-rebase is void. `git log origin/main..HEAD` at orientation AND before handoff — a clean `git
status` is NOT a clean tree, it hides local commits a peer seat left in a shared working copy. Push code
repos before `.github`, so no FINDING ever describes an unpushed tree. Semantic collisions (two seats
claiming one register) are caught MECHANICALLY by the claim gates, not by scheduling.

## ⛔ SHARED CROSS-LANGUAGE BB FACT RULES — POINTER, NOT DUPLICATED HERE

The retired GOAL-RAKU-BB.md carried ~250 lines of FACT RULE text explicitly declared **"byte-identical" in
GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md / GOAL-RAKU-BB.md** (and in places
GOAL-SNOCONE-IR-BB.md): **`bb_bin_t` IS ABOLISHED** (patch metadata travels in-band, no function counts
bytes), **ONE MEDIUM, INVISIBLE** (no `IF(MEDIUM_BINARY,…)` instruction branch, no raw-byte producer in a
template), **NO C BYRD-BOX FUNCTIONS** (a box is entered by jumping to its α/β labels, never a `(ζ, int
entry)` C call), **NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION** (except inside `EVAL()`/`CODE()`), **NO
VALUE STACK — EVER**, **NO DUPLICATED LOGIC**, **SHARED-LOWERER ONE-FILE CONCURRENCY** (the `lower.c`
discipline: one case per IR kind, language variation lives inside the case, edit only your own arm), and
**TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY** (the `emit_core.c` discipline: one dispatch case, one
template file per box, edit only your own language's boxes). **These bind Raku identically to the other
three languages and are NOT reproduced here** — this follows the precedent already set when SNOBOL4/Icon/
Prolog consolidated (neither GOAL-ICON-100.md nor GOAL-PROLOG-100.md reproduces this boilerplate either);
the authoritative text lives in `.github/RULES.md` and, for full historical wording with each rule's
COMPLETION TEST, in git history of the retired GOAL-RAKU-BB.md (and its still-live SNOBOL4/Icon/Prolog
siblings). Raku's own carve-outs inside these shared rules, where it deviates from the other three
languages, are preserved below because they are Raku-specific, not shared boilerplate:

- **Raku's emitter boxes live under their own `bb_rk_*` prefix** (`bb_rk_seq.cpp`, `bb_rk_jct.cpp`,
  `bb_rk_glit.cpp`, `bb_rk_gcc.cpp`, `bb_rk_nfa_*.cpp`, …) — the TEMPLATE-ONLY rule's "edit only your own
  boxes" clause holds with zero overlap onto the SNOBOL4/Prolog/Icon prefixes.
- **Raku's `lower.c` arms are `cx.lang==IR_LANG_RKU`** branches inside the existing shared cases; a Raku
  kind with no case yet routes to `lower_unhandled` (loud, never silent), same as the other three.

## ⭐ X86-64 REGISTER / SUBJECT-MODEL CONVENTION — RAKU'S CARVE-OUT

Locked callee-saved layout shared with SNOBOL4/Icon/Prolog (canonical origin: GOAL-ICON-BB "Subject model —
four names, zero redundancy"). Casing carries meaning: UPPERCASE = the fixed whole/bound, lowercase = the
moving position.

| Reg | Class | Name | Role |
|---|---|---|---|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, not durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` |
| rbx | callee-saved | — | FREE / callee-saved scratch |
| rbp | callee-saved | — | DEFINE'd / brokered function frame ptr when active, else scratch |

γ-success return packing: `rax = σ ptr`, `rdx = δ int`. Any change to this table is LOCKSTEP across all
four GOAL files in the same commit (the SHARED-LOWERER/EMITTER discipline applies here too).

**⚠ RAKU'S CARVE-OUT (md5 `8255d653` note, carried forward — Raku is a Seq/generator language, not a
subject-scanning pattern language at the top level):** the Σ/δ/Δ subject triad is used **ONLY inside the
isolated `IR_NFA_*` regex slab and the native grammar-engine boxes** (RK-GRAM; `Σ=subject base, δ=match
pos, Δ=slen`) — exactly the pattern-language use. Raku's generative core (Seq pull) uses **ζ (r12)** for
the per-box RW frame (resume cursors / counters) and SysV caller-saved scratch for transport; it does not
claim the subject triad outside regex/grammar.

## ⭐⭐⭐ THE MODEL — RAKU IS A Seq LANGUAGE: ONE FOUR-PORT PULL PROTOCOL

**The insight:** almost everything generative in Raku produces a **Seq**. `gather`/`take`, the `…` sequence
operator, lazy ranges, `map`, `grep` — all produce a Seq on demand. ONE four-port pull protocol (yield-one-
at-β, identical to Icon's generator PUMP) suffices; Raku adds almost no new IR kinds, it **reuses Icon's**.

**Port semantics (identical to Icon generators — reuse, never reinvent):**

| Port | Direction | Raku meaning |
|---|---|---|
| gamma | inherited DOWN | `take` yield / next Seq element delivered to the consumer |
| omega | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| alpha | synthesized UP | fresh-pull entry (first `.pull-one`) |
| beta | synthesized UP | resume entry (next `.pull-one` after a yield) |

The grammar/regex engine (RK-GRAM) is the one place Raku is a scanning language rather than a Seq language,
and it borrows Icon's Σ/δ/Δ discipline for exactly that reason (see register table above): **α**=fresh
entry, **β**=resume/backtrack-retry, **γ**=match advanced δ, **ω**=fail. Choice points save δ into the
per-activation ζ frame — a δ-snapshot slot, not a value stack (the Icon scan "save δ on β, restore and fail
on backtrack" discipline).

## ⛔ DEFINITION OF DONE — "100%"

The most authoritative statement of completion is the **RAKU-100 LADDER's own** (2026-07-10, Lon directive,
authored Claude Fable 5 — see TRACK 1 below), and it is adopted here as the file's Definition of Done,
computed rather than claimed by prose:

1. **100% of IN-TIER roast 6.c test files PASS UNMODIFIED under BOTH m3 `--run` and m4 `--compile`.** Oracle
   = **roast**, the official Raku specification test suite ("any compiler that passes the tests is deemed to
   implement that version"); manifest = `refs/rakudo-main/t/spectest.data.6.c` (1,154 files, counted
   2026-07-10). In-tier ≈ 985 files (tier table under TRACK 1 — Lon ratification of the tier boundary is
   still OPEN, see LON RULINGS WANTED). A fudged/skipped roast file maps 1:1 onto our XFAIL/EXCISE
   discipline — never a silent pass. Coverage claims come ONLY from `scripts/raku_roast_scoreboard.sh`
   stdout committed to `RAKU-COVERAGE.md`.
2. **m3 ≡ m4** — every rung both-modes-green; a mode-count gap that reopens after having closed is a stop,
   not a residual (RK-ZC's own standing rule).
3. **The grammar/regex engine (RK-GRAM) is native, not flattened:** `gram_expand`'s NFA-flatten fallback is
   retired for `.parse` (`re.c`/`nfa_build` KEPT for `~~ /regex/` only); recursive subrule calls
   (`rule TOP { "a" <TOP> | "a" }`) work — the milestone the flatten engine structurally cannot reach.
4. **The pattern-based frontend (`parser_raku.sc`, TRACK 2) reaches full official-grammar coverage** —
   `test_parser_raku_coverage.sh` COV_PASS covers every `Grammar.nqp` proto category through RK-50, oracle
   parity (`test_parser_raku.sh`) never regresses below its watermark.
5. **Gates strict and green:** `emit_no_lang`, `no_bb_bin_t`, `template_medium_invisible --strict`,
   `no_vstack --strict` (VSX-8), `pl_no_new_global`-style ratchets where Raku carries one, `handoff_status.sh`
   COMPLETE.

**MAGNITUDE, STATED HONESTLY (RAKU-100 LADDER's own words, carried forward so nobody re-derives false
optimism):** the S12 OO spike alone cost ~15 sessions for ~50 files of roast surface; in-tier is ~985 files
⇒ this is a **60–100-session arc**. Phase A (RK-BLK/RK-VAL/RK-AGG, "the three walls") is the highest-leverage
work — it gates more roast files than everything else combined.

## THE INSTRUMENT (boards are RUN, never transcribed; re-derive every count fresh)

```bash
bash scripts/test_smoke_raku.sh              # PRIMARY gate: m3+m4, ZERO FAIL floor, current watermark 724/0
bash scripts/test_raku_ir_rungs.sh           # legacy TRACK-4 rung sweep (test/raku/*.raku vs .expected)
bash scripts/test_raku_ir_full_suite.sh      # legacy TRACK-4, all 3 (now-retired) modes
bash scripts/test_raku_fileio.sh             # file I/O smokes
bash scripts/test_crosscheck_raku.sh         # 3-mode divergence check (mode terminology predates m3/m4-only)
bash scripts/test_parser_raku.sh             # TRACK 2: PAT-RK oracle-parity gate (watermark PASS=147)
bash scripts/test_parser_raku_coverage.sh    # TRACK 2: parse-only coverage gate, COV_PASS cumulative
bash scripts/regenerate_parser_and_lexer_from_sources.sh   # after any raku.y/raku.l edit
bash scripts/raku_roast_scoreboard.sh run|report   # RAKU-100 LADDER meta-instrument → RAKU-COVERAGE.md
bash scripts/audit_concurrency_invariants.sh
bash scripts/util_template_purity_audit.sh
./scrip --monitor file.raku                  # IR/SM/JIT step comparator (mode terminology predates m3/m4;
                                              # ICN frame locals + Prolog trail vars not yet in its snapshot)
```

**⛔ TESTING DIRECTIVE — ALWAYS RUN BOTH MODES.** Every time Raku is tested, exercise mode-3 (`--run`) AND
mode-4 (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run). Never report an m3 number
alone. A rung is promoted only when both m3 and m4 are PASS or LOUDLY EXCISED — never a silent FAIL or
abort. **KEY GOTCHA:** `scrip` statically links the runtime; `out/libscrip_rt.so` is mode-4 ONLY — after any
runtime `.c` edit, rebuild BOTH (`rm -f scrip && make -j4 scrip && make libscrip_rt`).

## ⛔ LAWS THAT BIND EVERY RUNG (compact; RULES.md is the parent)

BOTH-MEDIUM MANDATORY · TEMPLATE-ONLY (`x86(...)` sole producer) · ONE-AUTHORITY constants · PEERS RULE ·
NO-LANGUAGE-IDENTITY past LOWER · ZERO C BYRD BOXES · NO VALUE STACK · NO DUPLICATED LOGIC (value work is
ONE `rt_*` call, ports are the box's only job) · CONSULT CANONICAL SOURCES first — `refs/rakudo-main`
(roast + Rakudo source, gitignored, re-extract/re-clone every session; `src/core.c/*.rakumod` for semantics,
`Grammar.nqp` for the official parse spec) · killswitch per behavioral family, `=0` byte-identity a
completion criterion · ASM-DIFF-FIRST debugging (RULES.md) · ⛔⛔ **NO `-O2` BUILDS EVER** (see FACT RULE
above) · timeouts 8s/30s, `< /dev/null` · `git pull --rebase` before push, re-prove after · push mid-session
per rung · cursor moves every handoff · representation migrations keep the old path as a gated fallback so
the suite never regresses (the RK-GRAM flatten-fallback discipline) · **⛔ SESSION-CLOSE RULES LIVE IN
RULES.md — NOT DUPLICATED HERE** ("HANDOFF COMPLETE" is the verbatim, computed stdout of
`handoff_status.sh`, never assistant prose; the word "HANDOFF" itself is forbidden in the assistant's own
authored text at session close — both rules originate as FACT RULEs dated 2026-06-24 in the retired
GOAL-RAKU-BB.md, and both are project-wide, not Raku-specific; full text in RULES.md).

## Session Setup (every session)

```bash
git config --local user.name LCherryholmes && git config --local user.email lcherryh@yahoo.com   # SCRIP, corpus, .github
git -C SCRIP status --short && git -C SCRIP log origin/main..HEAD   # STANDING CONDITION concurrency pre-check
cd SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt      # rc=0 both; header edits not dep-tracked, rm -rf out/rt_pic first if suspect
bash scripts/test_smoke_raku.sh 2>/dev/null | tail -1   # fresh watermark FIRST — do not inherit one
```

Mandatory reads before touching a given track: TRACK 1 (goal-directed core) → `GOAL-ICON-100.md` first
(canonical four-port generator model Raku reuses) + `RULES.md` in full. TRACK 2/3 (either `parser_raku.sc`
rewrite) → `SNOBOL4-SNOCONE-PRIMER.md` first (per CLAUDE.md step 6) and read both this file's TRACK 2 and
TRACK 3 sections together — they are the same file's two rewrite generations. Touching corpus →
`CORPUS-LOCATIONS.md`. MODE-3/4-EMIT work → `ARCH-x86.md` AND `ARCH-SCRIP.md`.

---

## ⛔⭐⭐⭐ LIVE CURSOR — 2026-08-22 seat11 (cross-goal beneficiary note, NEWEST dated entry)

`bb_glit.cpp`/`bb_gcc.cpp` (`IR_GLIT`/`IR_GCC`, emitted only by `lower_raku.c` — Raku's grammar-
literal/char-class matcher) had their r11 alignment-padding (`push r11`/`pop r11` around a
`strchr`/`memcmp` call) converted to `sub rsp,8`/`add rsp,8` as part of the SNOBOL4-side r10/r11
register-contract ladder. Zero semantic change (nothing between the push and pop ever read r11); verified
via `test_smoke_raku.sh` (705/19 PASS — **this was this suite's OWN baseline at that moment, since
superseded by 724/0 below; do not read 705/19 as current**) and a direct run of
`corpus/programs/raku/parser/match_global.raku`. Not a Raku-ladder rung, just flagging the binary changed.
Detail: `FINDING-2026-08-22-seat11-free-r11-rung-e2-scan-idx-family-and-three-dead-templates.md`.

## ⛔⭐⭐⭐ LIVE CURSOR — s2026-08-08b (RK-GRAM-3d-m3-fix — Claude Sonnet 4.6) — **THE CURRENT STATE**

**COMMITTED — SCRIP commit `0ce21c92`.** ⛔ Push state is NOT recorded here — run `scripts/handoff_status.sh`
LIVE for ground truth (STALE-ORIENTATION rule (a)). **WATERMARK: m3 724/0, m4 724/0** (rc-aware harness;
+5 GALT alternation smokes added this session). Peers at this commit: Icon 14/0, SNOBOL4 6/1 (pre-existing),
Prolog 4/1 (pre-existing) — none Raku-caused. Lang-blind rc=0, no_bb_bin_t rc=0, raku_zframe gate PASS.

**ROOT CAUSE (worth preserving — a generalizable class):** `bb_rk_galt()` used bare
`x86("jmp", _.lbl_t0)` / `x86("jmp", _.lbl_t1)` for arm-entry jumps. Those label strings parse as `XK_SYM`
in the x86 dispatcher, and the `XK_SYM` arm returns EMPTY STRING in `MEDIUM_BINARY` — zero bytes, silently
dropping both jumps (m4 TEXT mode worked because `XK_SYM` emits the text directive there; this was a
BOTH-MEDIUM violation hiding in a "successful" text-mode build). Execution fell through to `x86_gamma()`
immediately, arm-1 never ran. **Fix:** `x86_jmp_lblptr(_.lbl_t0_p, _.lbl_t0)` — binary patches a rel32 via
the `bb_label_t*` pointer, text emits the directive, both media correct. **Generalizable:** any template
using a bare string label name for a jmp in binary mode silently emits nothing.

**NEXT RUNG (the actual current frontier): RK-GRAM-3d, remaining alternation work** — extend grammar
alternation to more complex patterns, multi-arm rules, and nested subrule alternation. See TRACK 1 → RK-GRAM
LADDER below for the full 3d→3e→3f→3g sequence; 3e (subrule recursion) is explicitly named as "the actual
seam" the whole RK-GRAM effort exists to reach.

**PRE-EXISTING, UNRELATED TO RAKU:** Icon `until` (1) and Prolog `clause` (1) failures in their own suites
at this commit.

---

## ⛔⭐⭐⭐ LON RULING 2026-08-30 (in-chat, direct to hq_C) — THE BISON/FLEX GRAMMAR IS THE WRONG INSTRUMENT

**Lon, verbatim in substance:** *"You simply take the parser spec from Rakudo/Roast and do mass
translation. Is the Raku parser written in Bison/Flex?"* — and, on being shown that Raku is not LALR:
**"If Raku has non LALR, then you must use another way."**

**This supersedes the incremental-construct strategy on row `raku-roast-100-percent-compile`.** That row
stays rank 0 and its DONE-WHEN (PARSE-FAIL=0) is unchanged; what changed is the INSTRUMENT that gets there.

**WHY — measured against `/home/resources/rakudo-main/src/Perl6/Grammar.nqp`, not asserted:**

| feature | count | why bison cannot express it |
|---|---|---|
| `proto token`/`proto rule` + `<sym>` uses | 34 / 405 | **longest-token-match protoregex dispatch** — runtime candidate selection, not a fixed table |
| `:my` parse-time locals | 390 | the grammar carries **mutable state** while parsing |
| `$*W` (the World/symbol table) | 171 | **parser↔symbol-table feedback**: whether `foo` is a listop, type or term depends on what has been *declared so far* |
| `$*IN_DECL` and friends | 45 | dynamic context variables steering the parse |
| `$*LANG`/`%*LANG`/`LANG(`/`quote_lang` | 17/21/27/29 | **slang switching** — regex, quoting and pod are separate grammars swapped in mid-parse |
| `<?before>`/`<!before>`/`<?after>` | 112/39/2 | arbitrary lookahead/lookbehind; LALR(1) has ONE token |
| `nqp::` ops inline | 219 | VM ops embedded in productions |

Grammar.nqp is **5,933 lines / 726 productions** (675 `token`, 47 `rule`, 4 `regex`); `Actions.nqp` is a
further 489KB. ⛔ The decisive fact is not any count above: **Raku's grammar is user-extensible AT PARSE
TIME** — `sub infix:<foo>` installs a new operator into the precedence table while the file is being
parsed. A bison table is frozen at build time, so no amount of grammar-writing closes this. Raku is not a
context-free language and `raku.y` can never be finished.

⭐ **Every feature that is IMPOSSIBLE in bison is NATURAL in recursive descent** — `:my` becomes a local,
`$*W` becomes a symbol table the parser consults, `<?before>` becomes a lookahead predicate, a protoregex
becomes a dispatch function. That is why the answer is a port, not a bigger `.y`.

**THE NEW INSTRUMENT: translate Grammar.nqp into a recursive-descent parser**, per Lon's "mass
translation". This is a BOUNDED, MECHANICAL job (726 small productions, each mapping to one function),
which is categorically different from the unbounded search the construct-by-construct approach was doing —
that approach was measured at **~3 files of PARSE-FAIL per pass against 924 remaining**, and does not
converge.

⛔⛔ **THE ONE SEMANTIC TRAP THAT WILL SILENTLY CORRUPT A NAIVE PORT: in Raku regex `|` is
LONGEST-TOKEN-MATCH, `||` is FIRST-MATCH (ordered).** A recursive-descent translation that renders `|` as
ordered choice — the obvious and idiomatic RD reading — is WRONG, and wrong in the worst way: it parses
most inputs correctly and silently mis-parses the ones where a later alternative matches longer. `|`
outnumbers `||` heavily in Grammar.nqp. Any translator MUST implement `|` as LTM.

⚠️ Precedent for a hand-written parser in this tree: the Snocone lexer is already a hand-written
threaded-code FSM, not flex (`snocone_lex.c`) — so this does not break a structural law.
⚠️ `raku.y`/`raku.l` STAY LIVE and are not to be deleted while the port is built: representation
migrations keep the old path as a gated fallback so the suite never regresses (this file's own RK-GRAM
flatten-fallback discipline, and the 724/0 `test_smoke_raku.sh` watermark rides on the bison parser).

## THE LADDERS — FOUR TRACKS

### TRACK 1 — GOAL-DIRECTED CORE (was GOAL-RAKU-BB.md)

**STATUS (carried from the retired file's own STATUS section):** Raku is LIVE through `lower.c`
(RK-LOWER-0..5 done). Post-SMX-4: no Stack Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; BB
run-path. Mode 2 (`--run`) DELETED 2026-06-15. Two native modes only.

**Mandatory reads before this track:** `GOAL-ICON-100.md` (the four-port generator model Raku reuses
wholesale) → `RULES.md` in full → this section, find the first incomplete `- [ ]` rung.

#### RK-ZC LADDER — carrying Raku onto `ZC_STORAGE_CELL_STACK` — **COMPLETE**

**THE PIVOT that minted this ladder (Lon, s2026-08-08 era): RAKU WAS NOT BROKEN BY RAKU WORK — IT WAS LEFT
BEHIND BY THE REGIME MIGRATION, AND THE FIX WAS TO CARRY IT ONTO `ZC_STORAGE_CELL_STACK`, NOT TO RESTORE THE
OLD SPINE.** Measured, A/B, same machine: BASE (last pre-drift Raku commit `6defd71a`) = 719/0 both modes;
HEAD at the time (+461 peer SN4-ζ/Icon-ZFRAME/RTX-port commits, 125 touching flat/wire/adopt/proc/frame) had
silently regressed to 513/206 m3, 465/254 m4 — **not because Raku rotted, but because the shared call/return
spine moved out from under it.** `IR_graph_t.zframe_graph` is set ONLY by `lower_icon.c`; Icon carried onto
the ζ-frame/cell-stack regime, Raku was never carried, so a `zframe_graph=0` graph took the legacy
`rt_outer_call` entry with no γ/ω exit wires and an epilogue that never unwinds the rsp cell carve —
producing both an exit-segfault class (a `ret` popping a ζ cell) and a return-wires-bomb class (every user
sub/method died `carries no return wires`).

**RUNGS (all `[x]` DONE):**
- **RK-ZC-0** — LIVE baseline computed before any edit: HEAD 513/206 m3, 465/254 m4; peers unaffected.
- **RK-ZC-1** — proved the boundary by A/B, not by reading: worktree-built `6defd71a` = 719/0 both modes ⟹
  regression is peer-side, the inherited cursor was honest.
- **RK-ZC-2** (commit `546603d9`) — set `zframe_graph` on Raku graphs in `lower_raku.c`, two lines mirroring
  `lower_icon.c:1422-1423`, killswitch `SCRIP_RK_ZFRAME=0`. Both witnesses fixed; 689/30 both modes; peers
  byte-unchanged; **not a language-identity violation** — `lower_raku.c` IS a lowerer, the flag it sets is a
  plain IR-graph property the emitter reads without knowing who set it (never reach for `is_raku`
  downstream — if a step seems to need one, the seam is wrong).
- **RK-ZC-3** — GRAMMAR family (28) resolved FREE by RK-ZC-2 (the native grammar boxes already used the
  ζ-frame entry, just gated behind `RK_GRAM_NATIVE=1`).
- **RK-ZC-4** (commit `d794b613`) — SLURPY family (18), a pure regression in `rt_frame_bind_args`.
- **RK-ZC-5** (commit `55d1598b`) — LOOP-CTL family (+11): root cause was the UCLAIM wholesale-flip claim
  assuming single-entry statement heads; `lower_raku.c` never called `bb_src_note` on loop-back landing
  nodes, so RSP drifted after iteration 1 on any loop with an interior omega exit. Fix: `bb_src_note` on
  each loop-back node. 695/24 → 706/13.
- **RK-ZC-6** — `bool_compare_store` (1), resolved free by a prior commit.
- **RK-ZC-7** (commit `3028fdc8`) — HARNESS SEES `rc`: a crash-after-correct-output used to score PASS
  because the harness never checked exit code; now checked, `raku_dies()` helper added for 17 die/type-error
  tests. Re-baseline exposed 17 hidden crashes, all recovered; watermark held at 719/0.
- **RK-ZC-8** (commit `3028fdc8`) — REGIME PIN GATE `test_gate_raku_zframe.sh`: Invariant A
  (`SCRIP_RK_ZFRAME=0` reproduces the return-wires bomb) + Invariant B (full suite 719/0 both modes).
  **This is the 719/0 figure superseded by 724/0 above — RK-ZC-8's own watermark, not the current one.**

**GENERALIZABLE FINDING (worth carrying to any future frontend):** `zframe_graph` is set by ONE lowerer;
every frontend that is not Icon is presumptively on the legacy entry and presumptively carries both failure
classes. A regime migration that lands per-lowerer is a migration that silently forgets the lowerers nobody
ran that day — the cheap check is two witness programs per language, not a code read.

#### RK-ZETA LADDER — un-park Raku ζ onto ARCH-ZETA §13's two-flavor law — **DONE, with one correction**

**DIRECTIVE (Lon 2026-07-14): "Move all BB's ZETA to the RSP-topped FORTH-like stack, except so-called
escapee-type BB's which go on the heap."** ESCAPEE = family-A LIFO-breaker: for Raku, block/closure values
with a captured ζ-env (RK-BLK) + EVAL/deferred thunks — heap-promote from birth, GC-visible. Everything else
= fixed cells on the RSP FORTH spine.

- [x] RK-ZETA-0, RK-ZETA-1 — DONE.
- [ ] **RK-ZETA-2 — escapee (family-A) Raku BBs heap-promote from birth.** Still open: block/closure
  captured-ζ-env (RK-BLK) + EVAL/deferred thunks → GC-visible heap block, construct-aware ω-free. Mind
  `FINDING-2026-07-13-CLAUDE-SN4-DEFER-RSP-64KB-DONATION-IS-THE-BLOCKER.md` — it lives in exactly this
  escapee/deferred-thunk path. GATE: closure/block-capture + EVAL smokes ASan-clean under MALLOC.
- [~] **RK-ZETA-3 — CLAIM CORRECTED (Opus 4.8, 2026-07-17b): the "byte-identical" was flag disconnection,
  not allocator agreement.** The original 2026-07-17 proof (MALLOC vs BUMP_LIFO, 283/0 both modes,
  DIVERGE=0) looked like proof the allocators agreed — but a follow-up established `ZC_ALLOC` had ZERO code
  consumers (sole ref = a debug label), so `-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO` changed NOTHING; the two builds
  were byte-identical because they were the SAME build. The axis is RETIRED (`c72e3e4b`). **The underlying
  claim — non-escapee Raku ζ correctly rides the RSP bump-LIFO FORTH spine — is TRUE and holds** (283/0 both
  modes at the committed default), just not provable via the now-deleted knob. Any real allocator A/B needs
  a knob with live consumers (`ZC_COLLECTION` is the live one today).
- [x] RK-ZETA-4 (`c72e3e4b`) — DONE.

#### RK-GRAM LADDER — native recursive-descent grammar engine — **THE STANDING FRONTIER, 3a-3c done, 3d-3g open**

**Un-parked by Lon 2026-06-27; RK-GRAM-3 (the recursive-descent seam) is THE LEAD** and carries a standing
requirement unchanged since minting: **a FRESH session with a FULL context budget, `ARCH-x86.md` +
`ARCH-SCRIP.md` (+ `ARCH-LANGUAGES.md` §String-scanning for the Σ/δ/Δ discipline) read FIRST** — do not tail this
onto a spent session.

**DIRECTION (Lon 2026-06-14):** NFA is the WRONG primary engine for top-down recursive descent — real
Raku's matcher IS recursive descent (a backtracking cursor machine), and subrule `<name>` recursion is
provably beyond any finite automaton. The NFA-on-Byrd-boxes apparatus was DELETED (`d63c374`). The C NFA
matcher `re.c` (`nfa_build`/`nfa_exec`) is KEPT for `~~ /regex/` only.

**Design (Σ/δ/Δ per the register table above; REPLACES `gram_expand`'s flatten-to-NFA depth-16 stopgap):**
δ is CALLEE-SAVED so it stays ambient across subrule recursion — the called rule's box advances δ and the
caller sees it on return, no arg marshaling. Choice points save δ into the per-activation ζ=r12
δ-snapshot slot (not a value stack). Captures record `(from=δ-at-α, pos=δ-at-γ)` → Rakudo `Match`
`$!from`/`$!pos`. Grammar compiles ONCE to box code; `.parse` loads Σ/δ/Δ and jumps to the TOP box; success =
TOP reaches γ with δ==Δ (full) or any γ (subparse). Templates stay language-blind — these boxes dispatch on
IR shape, never on `is_raku`; cross-language safety holds because only the Raku lowerer emits `IR_GLIT`/
`IR_GCC`/`IR_GSUBRULE`. Steps are each both-modes-green, flatten kept as a gated fallback so the suite never
regresses:

- [x] **RK-GRAM-3a** — enum-first (`IR_GLIT`/`IR_GCC`/`IR_GSUBRULE` added to `IR.h`, inert) + the lowering
  seam (pure-literal rules lower to a 1-node `IR_GLIT` graph, dump-visible, gated on `g_opt_dump_bb` so
  `--run`/`--compile` are untouched). Neutrality proven both times: Raku smoke unchanged, failure set
  byte-identical.
- [x] **RK-GRAM-3b** — the leaf boxes go LIVE: `bb_rk_glit.cpp` (literal match) + `bb_rk_gcc.cpp` (built-in
  char-class: digit/alpha/upper/lower/xdigit/alnum/space) both execute on the `.parse` path by default (no
  env flag). New `rk_gram_trampoline.S`: naked `rk_gram_enter_box` loads Σ/δ/Δ into r13/r14/r15, enters the
  box at α, reads δ back. `grammar_parse_core` resolves a native `gram__G__TOP` proc when one exists, else
  falls through to `nfa_build`. Default-ON flip via `lower_raku.c`'s gate; `RK_GRAM_NATIVE=0` is the escape
  hatch back to NFA. Two latent alignment/register-clobber bugs found and fixed by gdb (rsp 16-alignment at
  the call site; r8/out_delta clobbered by the box's own strchr).
- [x] **RK-GRAM-3c** — multi-leaf sequence via native chained leaf boxes: `rk_gram_seq_leaves()` parses a
  rule body into a leaf list (literals + builtin char-classes incl. `<.name>`; non-leaf bodies fall to NFA)
  and chains each leaf's γ to the next, tail γ to a success exit. Pure lowerer change, zero new templates.
- [ ] **RK-GRAM-3d — alternation (`IR_ALT`) with δ-restore-on-β. THE CURRENT FRONTIER (see LIVE CURSOR
  above — the m3-fix landed 2026-08-08, the alternation semantics themselves are the remaining work).**
  Try alt 1; on its ω, restore the saved δ and re-pump alt 2's α; all-ω → alt ω. GATE:
  `rule TOP { <digit> | <alpha> }` PASS both modes; backtracking proven by `rule TOP { "ab" | "ac" }` on
  "ac". ⚠ `IR_ALT` does not exist in live `IR.h` (only in parked files); SNOBOL4's `IR_MATCH_ALTERNATE`/
  `IR_PATTERN_ALT` are scan-semantics-specific — 3d needs its own `IR_GALT` or inline wiring (this is what
  `bb_rk_galt()`, the box whose jmp bug the LIVE CURSOR fixed, already began).
- [ ] **RK-GRAM-3e — subrule call = recursion into another box graph. THE ACTUAL SEAM this whole ladder
  exists to reach.** `<name>` lowers to recursion into the named rule's box graph with Σ/δ ambient in the
  callee-saved registers. GATE (two parts): (1) non-recursive `rule TOP { <word> }` PASS natively; (2) **the
  milestone the flatten engine cannot reach** — `rule TOP { "a" <TOP> | "a" }` on "aaa" PASS both modes.
- [ ] **RK-GRAM-3f — quantifiers `*`/`+`/`?` greedy with backtrack.** GATE: `rule TOP { <digit>+ }`,
  `rule TOP { <alpha>* <digit> }` PASS natively with backtracking (longest match then yield-back).
- [ ] **RK-GRAM-3g — retire the flatten fallback for `.parse`.** Delete `gram_expand`'s NFA route for
  grammar `.parse` once every grammar smoke passes natively (KEEP `re.c`/`nfa_build` for `~~ /regex/`).
  GATE: all grammar smokes green both modes, zero `nfa_build` on the `.parse` path.
- [ ] **RK-GRAM-4 — captures + Match tree.** Reify `(from,pos)` into a `Match` object; `$m<name>`/`$m[i]`
  access (parser gap noted: `$var<word>` Match-subscript not yet parsed). Sits on 3e.
- [ ] **RK-GRAM-5 — LTM + proto/`multi` token dispatch.** Longest-token-match alternation ordering;
  proto-token candidate dispatch. Sits on 3d/3e.
- [ ] **RK-GRAM-6 — actions + adverbs + control.** `make`/action-class invocation, `:i`/`:s`/`:ratchet`
  adverbs, `<?>`/`<!>` assertions. Sits on 4/5.
- [ ] **RK-RX-OPS** — `s///`, `.subst`/`.match`/`.comb`/`.split` with regex, `tr///`, `:g`/`:i`/`:x`
  adverbs, `$/` `$0` `$<name>` variables. Sits on the RK-GRAM ladder.

Earlier, smaller RK-GRAM landings preserved for provenance: literal strings in rules matched verbatim with
regex-metacharacters treated as literal (Raku semantics, not any-char); built-in character-class subrules
(`<digit>` etc.) resolving when no user subrule shadows the name.

#### RK-OO LADDER — **DONE** (every rung `[x]`/`[~]`; cheap wins exhausted, remaining items are named-cost tails folded into the RAKU-100 LADDER's Phase E)

Anchored to Rakudo `Metamodel/{BUILDPLAN,C3MRO,MROBasedMethodDispatch,RoleToClassApplier}.nqp`,
`Mu.rakumod`, `Attribute.rakumod`. Landed: RK-OO-A1..A4 (attribute mutation/accessors/typed-defaults/
array-hash attrs), RK-OO-B1..B4 (user-method new/bless, op-800, TWEAK, `is required`), RK-OO-C1..C6
(inheritance, C3 MRO infrastructure, `callsame`/`nextsame`/`callwith`, multiple inheritance + real
`c3_merge` with a pointer-aliasing bug found and fixed), RK-OO-D1..D4 (roles: compile-time flatten,
composition-lookup resolver own>role>inherited, conflict detection, yada-stub, punning), RK-OO-E1/E (multi
sub AND multi method dispatch, arity + type narrowness), RK-OO-F (`.isa`/`.does`/`.^parents`/`.^name`/
`.^methods`/`.^attributes`/`.WHAT`/`.clone`/`is required` close-out/plain-type param enforcement),
RK-OO-G1/G6 (`.Str`/`.gist`/`.raku` override routing through implicit stringification contexts, `.=`
method-assignment sugar). Open G-tail items (G2-G5) are named in the RAKU-100 LADDER's Phase E, not
duplicated here. One latent codegen bug found and fixed along the way, worth keeping for its own sake:
**mode-4 dense node-ids** — the `is_icon||is_raku` m4 branch never set `g_m4_dense_nid`, so multi-method
classes could draw colliding pointer-hash node-ids (`bbNNNNN_α already defined`); fixed by enabling the same
dense-sequential id scheme SNOBOL4/Prolog already used.

#### RAKU-100 LADDER — the roast-based full-language-coverage arc (Lon directive 2026-07-10, authored Claude Fable 5) — **THE MASTER LONG-TERM PLAN, mostly `[ ]` not started; this is the Definition of Done, not optional scope**

Completion, tier table, and instrument are stated under DEFINITION OF DONE / THE INSTRUMENT above — not
repeated here. **STANDING LAWS for every rung:** both-modes-green (m3+m4) + the named GATE; representation
migrations keep the old path as a gated fallback (the RK-GRAM flatten discipline); canonical semantics come
from `refs/rakudo-main/src/core.c/*.rakumod` FIRST, prose second; every FACT RULE in this file binds
unchanged.

**PHASE 0 — INSTRUMENT FIRST (session-tail-sized; may land in any session):**
- [~] **RK-100-0a — roast + rakudo oracle. HALF-DONE.** roast + rakudo cloned to `refs/`; manifest computed
  = 1,154; in-tier denominator computed = 986. **STILL OPEN:** a PREBUILT rakudo binary as the
  `.expected`-minting oracle (today the scoreboard trusts each file's own TAP self-report, which cannot
  catch a well-formed-but-wrong answer); 41 manifest files absent from the roast tree (repo-tag skew).
- [x] RK-100-0b, RK-100-0c — DONE.
- [ ] **RK-BLK — blocks/closures native.** `[~]` **RK-BLK-a STEP 1 LANDED:** `DT_BLK` descriptor carries a
  hoisted proc name; store + `$b()` invoke work via the runtime proc registry, anon `sub {…}` too.
  **REMAINING for RK-BLK-a:** no ζ-env pointer yet (no lexical capture — that's explicitly RK-BLK-c),
  `sub{…}()` immediate-invoke / block-args / top-level statement-blocks / pointy-params. Then
  [ ] **RK-BLK-b** pointy `-> $x { }` params, `.()`, implicit `$_`; [ ] **RK-BLK-c** lexical capture via
  ZLS2 activation chains — **COORDINATE with the ZB-ACT ladder in `GOAL-IR-IMMUTABLE-EMIT.md`, never fork a
  parallel activation mechanism**; [ ] **RK-BLK-d** value-position `map`/`sort`-comparator/closure attr
  defaults/BUILDPLAN op-400/`where` constraints.
- [ ] **RK-VAL — numeric tower.** [ ] RK-VAL-a Num floats end-to-end; [ ] **RK-VAL-b Rat** — decimal
  literals ARE Rat, normalized arith, `.nude`/`.numerator`/`.denominator`, faithful `.gist`/`.Str`
  (THE distinctive Raku numeric; roast assumes it everywhere); [ ] RK-VAL-c big Int (LON RULING WANTED:
  gmp vs own limbs); [ ] RK-VAL-d radix literals + allomorph tails.
- [ ] **RK-AGG — real aggregates** (retire the `\x01` string encoding; substrate to reuse: the Icon lists
  machinery landed 2026-07-06). [ ] RK-AGG-a descriptor Array behind existing entry points, `\x01` kept as
  fallback; [ ] RK-AGG-b nesting/lvalue/slices/Whatever-index; [ ] RK-AGG-c descriptor Hash + adverbs +
  autovivification; [ ] RK-AGG-d Pair/List-vs-Array split/Seq basics; [ ] **RK-AGG-e RETIRE `\x01`** —
  GATE: grep for the separator constant in runtime == zero live sites.

**PHASE B — statement/operator breadth (S03/S04):** [ ] RK-CTRL (loop/repeat/last/next/redo+labels,
statement modifiers, `do` blocks, ternary, `with`/`orwith`/`without`, `once`); [ ] RK-OPS (chained
comparisons, `//`/`andthen`/`orelse`, string relops, `x`/`xx`, Range-as-value, `...` sequence; post-AGG: `Z`/
`X`/`[op]`/`>>op<<`/meta-ops); [ ] RK-SMART (`~~` smartmatch dispatch table + given/when riding it);
[ ] RK-JUNC2 (true junction autothreading); [ ] RK-BUG-SWEEP (item 1 `if ($x<$y)` variable-operand relop
misthread — **FIXED s2026-07-23**, `lower_cond` `TT_SEQ` arm; item 2 callwith/call-arg binop marshaling
still open; item 3 `$var<word>` Match-subscript parse gap still open).

**PHASE C — GRAMMAR/REGEX** = the RK-GRAM-3a..g → 4 → 5 → 6 ladder above (single home, not duplicated).

**PHASE D — signatures (S06):** [ ] RK-SIG (named args, optional `$x?`, defaults post-BLK, slurpy `*@`/
`*%`, `|` capture pass-through, `-->` return-type, destructuring, `where` post-BLK); [ ] RK-FN2 (anon sub,
WhateverCode `* + 1`, `&foo` sigil, `proto sub {*}`).

**PHASE E — OO tails** (collection order for the deferred items each OO rung's own note names): enum/subset
→ `but` runtime mixin → prefix/postfix overload call-site seams → parametric roles `R[::T]` → role-does-role
→ `FALLBACK` → `AT-KEY`/`AT-POS` container protocols.

**PHASE F — exceptions + phasers (S04):** [ ] RK-EXC2 (typed `X::` hierarchy, `when X::Foo` inside CATCH,
`Failure`/`fail`, `$!` — try/CATCH base itself is LANDED, 13 smokes); [ ] RK-PHASE (ENTER/LEAVE/KEEP/UNDO,
FIRST/NEXT/LAST, `state` vars, BEGIN/END).

**PHASE G — S32 library sweep (191 files):** [ ] RK-LIB-STR/LIST/NUM/HASH — batch rungs ordered by
scoreboard yield (never guessed).

**PHASE H — system:** [ ] RK-IO2 (`IO::Path`, open/close/get/lines/slurp/spurt/dir, file tests);
[ ] RK-MAIN (`MAIN` + auto-usage); [ ] RK-MOD (single-file unit module/class, `use` of a sibling file,
EXPORT); [ ] RK-CONC (TIER-C, Lon decision: thin `start`/`await`/`Promise` over the pthread coexpr substrate,
or EXCLUDED).

**META-RUNG — RK-ROAST-CLIMB (standing):** every phase-close re-runs the scoreboard and commits the
`RAKU-COVERAGE.md` delta. Done when the scoreboard — not prose — prints 100% of in-tier files PASS
unmodified, both modes.

**Done (full history, condensed from the retired file's own running list — the individual dated
session-by-session watermark narratives behind each of these, July 9 through August 8, are DEEP/STALE
history and are not reproduced; git log of the retired GOAL-RAKU-BB.md and the `FINDING-*.md` files it cites
are the record):** RK-LOWER-0..5h · RK-NFA-ORACLE-FIX · RK-EMIT-1/2/3+GATHER · RK-HY-0..3 · RK-NFA-1/2/3 ·
RK-M34-1 · the post-GZ#5 union-clobber restoration (2026-07-09, Raku went from a segfault on `say "hello"`
to 204/0/12-of-216) · the β-discipline fix that flipped the final 12 EXCISED (2026-07-10, value-position
relops, assign-RHS Bool materialization, smartmatch+captures, `for`-over-gather/map/grep, 218/0/0) ·
try/CATCH on the ω-unwind spine (2026-07-10 session B, 230/0) · RK-OO-C1..C6, D1..D4, E1/E, F, G1/G6 (the OO
ladder above) · RK-GRAM literal-strings + built-in-charclass subrules (2026-06-27) · value-position relop
Bool materialization + `%%` divisibility (s2026-07-22e/f, s2026-07-23) · prefix/postfix `++`/`--` +
sprintf/printf/.fmt/string methods (s2026-07-22e) · the RK-ZC and RK-GRAM-3a/3b/3c/3d-m3-fix ladders above.

---

### TRACK 2 — PATTERN-BASED FRONTEND `parser_raku.sc` (was GOAL-PARSER-RAKU.md)

**Repo:** corpus+SCRIP. **Branch:** `parser` (SCRIP only — `corpus` and `.github` stay on `main`).
**Sibling ladder:** TRACK 4's GOAL-LANG-RAKU content and TRACK 3 (PST) below — same underlying grammar,
three different implementation generations.

**⚡ THE PIVOT (session 2026-05-07, post PARSER-RK-27):** the old goal (RK-0..RK-27, match the existing C
frontend's `--dump-ast` output byte-for-byte) is **CLOSED at PASS=147 FAIL=0** — ~95% of `raku.y`
productions covered. **The new goal (RK-28 onward): flush out the ENTIRE official Raku grammar** into
`parser_raku.sc`, anchored verbatim to `rakudo/src/Perl6/Grammar.nqp` (5,933 lines, 759 production rules,
495 unique non-terminals) — real-world Raku programs use features the C oracle has never seen. **Coverage
over conformance:** a parsed-and-treed program is a win even if the tree differs from `--dump-ast`; a Parse
Error is a loss. Where a construct has no clean IR mapping, lower to a generic
`(E_FNC raku_<name> args...)` placeholder call node — the tree must be well-formed and dumpable, it does
not need to round-trip through the runtime.

**Two gates, run after every micro-step, commit only when both green:** `test_parser_raku.sh` (oracle
parity, frozen at PASS=147 since the pivot — the 147 regression-guard fixtures must never break) and
`test_parser_raku_coverage.sh` (parse-only: exit 0, non-empty stdout, no `Parse Error`, first line starts
`(STMT` — no oracle compare, walks `corpus/programs/raku/parser-coverage/`).

**Rung-size discipline:** one `proto` category per rung (RK-28 = `statement_control`, RK-29 =
`statement_prefix`, …); inside a rung, one `:sym<X>` arm at a time, each its own coverage fixture, both
gates after every arm; a rung that breaks an earlier fixture is reverted on the spot, never pushed through.

**CURRENT STATE:** PARSER-RK-0 through PARSER-RK-27 (the pre-pivot ladder) all LANDED, PASS=147. Post-pivot:
**RK-28-A (coverage-gate infrastructure) and RK-28 (`statement_control:sym<...>`, all 19 arms) LANDED** —
smoke PASS=5, oracle PASS=147 (unchanged), COV_PASS=13. **RK-29 (`statement_prefix:sym<...>`, 26 arms:
15 block-only phasers + 6 block-value + 5 list adverbs) LANDED** — COV_PASS=39.

**Open, RK-30 onward (each: `Grammar.nqp` line-anchored spec, gate target = prior COV cumulative + arm
count):**
- [ ] **RK-30** — `package_declarator:sym<...>` (10 kinds: package/module/grammar/role/knowhow/native/
  slang/trusts/also; `class` already covered). Target COV ≥ 39.
- [ ] **RK-31** — `scope_declarator:sym<...>` (9: our/HAS/augment/anon/state/supersede/unit; `my`/`has`
  already covered). Target ≥ 45.
- [ ] **RK-32** — `routine_declarator` (submethod/macro) + `multi_declarator` (multi/proto/only). Target ≥ 50.
- [ ] **RK-33** — `regex_declarator` (rule/token/regex, bodies opaque this rung) + `type_declarator`
  (enum/subset/constant). Target ≥ 56.
- [ ] **RK-34** — `statement_mod_cond` (if/unless/when/with/without as postfix) + `statement_mod_loop`
  (while/until/for/given as postfix) — a Stmt-wrapper grammar shape change. Target ≥ 65.
- [ ] **RK-35** — `term:sym<...>` (25 terminal forms: circumfix, `**`/`*` whatever, lambda, unquote, `!!`,
  `::?IDENT`, time terms, etc.). Target ≥ 79.
- [ ] **RK-36** — `value:sym<...>`/`number:sym<...>` (version, rat, radix, complex literals). Target ≥ 84.
- [ ] **RK-37** — `infix:sym<...>` long tail (~80 operators: numeric bitwise, string bitwise, boolean
  xor/defined-or/andthen/orelse, three-way cmp, set ops, range/sequence tail, functional compose/reverse/
  cross/zip, bind `:=`). **Split into 37a-e, each a separate commit/gate.** Target ≥ 131.
- [ ] **RK-38** — `prefix`/`postfix:sym<...>` tail (`+`/`~`/`?`/`|`/`||`/`--`/`^`/`let`/`temp` prefixes;
  `++`/`--`/`.()`/`.[]`/`.{}`/`.<>` postfixes). Target ≥ 141.
- [ ] **RK-39** — `circumfix:sym<...>` (array literal `[...]`, quote-words, signature literal, eval-style).
  Target ≥ 147.
- [ ] **RK-40** — `quote:sym<...>` (13 variants: q/qq/Q/qw/qx/qqx/rx/tr/TR forms; apos/dblq/`/ /`/m/s already
  covered). Target ≥ 155.
- [ ] **RK-41** — Pod blocks (`=begin pod`, `=head*`, `=for`/`=item`/`=comment`, `#|`/`#=`). Target ≥ 160.
- [ ] **RK-42** — Regex/grammar body internals (the OTHER big one — replaces opaque E_QLIT bodies from
  RK-30/33/40 with structured trees: subrule calls, `||`/`|` alternation, ws/capture markers, quantifiers,
  `<commit>`/`<cut>`, character classes, adverbs, `:my` runtime decl). A fresh sub-grammar `RegexCompiland`
  inside `parser_raku.sc`. Target ≥ 170.
- [ ] **RK-43** — MAIN signature + full sub signatures (optional/default/slurpy/named/typed/constraints/
  sub-signatures/capture/trait modifiers). Target ≥ 178.
- [ ] **RK-44** — Pair/colonpair/fatarrow forms. Target ≥ 182.
- [ ] **RK-45** — Special variables (`$/` `$!` `$_` `@*ARGS` `%*ENV` `$*PROGRAM-NAME` etc.). Target ≥ 194.
- [ ] **RK-46** — `dotty:sym<...>` (`.+`/`.*`/`.?`/`.&`/`.=` method-call variants). Target ≥ 199.
- [ ] **RK-47** — Meta-operators (`[+]`/`[\+]`, `!==`, `>>op<<`, `«op»`, etc.). Target ≥ 209.
- [ ] **RK-48** — Trait modifiers (`is rw`/`does`/`hides`/`of`/`as`/`returns`/`handles`/`will`). Target ≥ 217.
- [ ] **RK-49** — Terminator/`eat_terminator` edge-case hardening (no new productions). No new fixtures
  unless edge cases surface.
- [ ] **RK-50** — Real-world program corpus (rosetta-code-raku, rakudo `t/`, popular-module examples) as the
  final "never breaks" verification; any Parse Error found here backfills into the rung that should have
  caught it. Target ≥ 250, covering ≥ 50 distinct real-world programs.
- Beyond RK-50: inner-body regex/rule/token parsing depth, full `make`/`made`/`match` action methods,
  `MAIN`-driven CLI auto-parse, full Pod content parsing.

**Cross-PARSER findings on record (apply to any `parser_*.sc`, not just Raku's):**
- `ARBNO(X)` captures `X`'s pattern value at DEFINITION TIME, not call time. When `X` is defined AFTER the
  `ARBNO(X)` site, use `ARBNO(*X)` for deferred lookup. (First hit: RK-4's `*CallArgTail`; recurred at
  RK-21's `*GatherBlock`/`*SubBlock_body`, RK-22's `*MethodTail`.)
- **Match-time side effects in failed alternations are NOT rolled back** (`&FULLSCAN=1` tries and abandons
  alternatives, but a fired `epsilon . *fn()` push/pop is permanent). Any grammar alternative using a
  `*fn()` helper inside a pattern that might fail must gate the helper behind `FENCE` — commit AFTER the
  disambiguating token, not before. (Found at RK-24's `class_and_main`; the fix pattern —
  `VarScalar FENCE ',' Push_var` — is now standing idiom, reapplied at RK-25.)
- `shift(p, t)` requires `p` to be a SUBJECT-CONSUMING pattern (`p . thx . *Shift(t, thx)` — the leaf value
  is the matched text `thx`); passing a value-typed scratch variable as `p` is a primitive misuse, not a
  style issue (this is the SAME underlying defect PST-RAKU's PRF-14-6, TRACK 3 below, exists to fix —
  `shift_value(expr, K)` is the correct primitive for a synthetic-value leaf).
- Two `Watermark`/`BUG-SCRIP-*` engine-level findings from the RK-WS2 canonicalization attempt remain on
  record: BUG-SCRIP-WS-1 (SIGSEGV under nested `ARBNO`+`&FULLSCAN=1`) is **RESOLVED** (engine-side fixes
  elsewhere cured it, re-verified 2026-05-07); **BUG-SCRIP-VAL-SCAN is OPEN** — a value-context `subj ? pat`
  extraction reads `g_last_match_subj` after the GC may have moved/freed it (SIGSEGV in
  `interp_eval.c:3958`); minimal repro and fix sketch (GC-protect the buffer in `stmt_exec.c`) are in the
  retired file's git history. The canonical `White = white ARBNO(white)` refactor that surfaced this bug is
  **WON'T DO** — the FENCE-based White/Gray already in the tree is correct and passes every gate; the
  canonical form's only payoff is cosmetic and it risks the regex-tier regression this bug hides behind.

---

### TRACK 3 — PURE SYNTAX TREE rewrite of `parser_raku.sc` (was GOAL-PST-RAKU.md)

**Repo:** SCRIP + corpus + .github. **Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`. This is a from-scratch
rewrite of the SAME `corpus/SCRIP/parser_raku.sc` TRACK 2 develops incrementally — the two tracks are not
independent, they are two generations of one file; whichever is more current when a session picks this up
should be re-verified against the other before trusting either.

**STATUS: Phase 1 C COMPLETE. Phase 2 PRF-14 — grammar rewrite landed, ONE architectural defect open,
THIS IS THE LIVE CURSOR for this track.**

**PRF-14 (rung):** full rewrite mirroring `raku.y` exactly, 426 LOC, style matching `parser_snocone.sc`/
`parser_rebus.sc` (two-column token table, `TT_*` constants up top, `nTop_count`, `X_*` recursive helpers).
Landed sub-steps PRF-14-1..4 (source read, structural-fit decision, the rewrite itself, grep-verified
against the Phase-2 rules). **PRF-14-5 (smoke test) is BLOCKED** in this container by the pre-existing
`&ALPHABET` segfault in `scrip --run` (`global.sc` line 3, same blocker as the Snocone PST's own SC-5 rung —
SCRIP `e1c8a4ac` / EC-3f); per the parent goal's own rule ("mechanical deletion and rewrite first, tree-
shape conformance debug after, in a separate session") the rewrite is committed and the smoke debug is
deferred.

**⛔ PRF-14-6 — ARCHITECTURAL FIX, NEXT STEP (opened 2026-05-19, still open):** the 23 `push_*` leaf-pusher
definitions misuse `shift` — each passes a value-typed scratch `tmp` to `shift`'s pattern argument, but
`shift(p, t)` expects `p` to be a SUBJECT-CONSUMING pattern (it generates `p . thx . *Shift(t, thx)`, and
`thx` is the leaf value — the matched text). This is the identical primitive misuse TRACK 2's cross-PARSER
findings name above. **The fix landed on the primitive, not yet on the file:** `shift_val` was renamed to
the clearer `shift_value(expr, K)` (Lon's direction) and reinstated as the legitimate synthetic-value
primitive; 50 historical `.github` doc references were renamed to match; `parser_raku.sc` itself is
**UNCHANGED** — still needs: delete all 23 `push_*` pattern-variable definitions and every `assign(...)`
call; for subject-text leaves (vars/idents/ints/floats/strings) rewrite as `shift(body_pat, K)` with the
sigil/quotes consumed by the outer rule; for synthetic-value leaves (`True`→'1', `self`→'self', `$*STDIN`→
'0', kind tags, the composed `LitSubst` payload) use `shift_value(expr, K)` directly. The corrected primitive
contract:

| primitive | when to use | mechanism |
|---|---|---|
| `shift(pat, K)` | leaf value = subject text matched by `pat` | `pat . thx . *Shift(K, thx)` |
| `shift_value(expr, K)` | leaf value = expression result (synthetic, no subject consumed) | `epsilon . *Shift(K, expr)` |
| `shift(epsilon, K)` | placeholder leaf, empty value | falls out of `shift(pat,K)` with `pat=epsilon` |

**Same misuse pattern exists in `parser_icon.sc` Expr11 (4 sites)** — filed as ICN-SC-2 under
`GOAL-PST-ICON.md`, not this file's problem to fix but worth knowing the defect class is shared.
`PST-SCRIP-AUDIT.md`'s own replacement template is ALSO wrong (says
`shift_value(VAL,K) → assign(.tmp,VAL) shift(tmp,K)`, the same broken indirection) and needs the same
one-line correction; deferred, flagged for whichever session next touches that file.

**Closed rungs (Phase 1 C, full history, compressed):** 25 PRF-12 sub-rungs (program, my-type, say, print,
arr-hash-ops, try, unless, given, smatch, new, mcall, die, hof, capture, twigil, sub, class, for, gather,
self, gather-splice, gather-hoist) across many sessions. PRF-13 REVERTED (the assign+shift mechanical
substitution was the same architecturally-wrong pattern PRF-14-6 now fixes properly).
PRF-14-CLEAN/GRAMMAR/GRAMMAR-RR/GRAMMAR-RR-FIX (prior Sonnet 4.6 sessions) stripped tree actions intending
to re-add them and never did (produced a "Parse OK"/"Parse Error"-only recognizer skeleton — an F1
violation, no tree on the channel) — PRF-14 itself (Opus 4.7) re-attached tree actions in one sweep using
the corrected architecture.

**Heads at last touch:** SCRIP `e1c8a4ac` · corpus `5d8e221`.

---

### TRACK 4 — SUPERSEDED FOUNDATIONAL LADDERS (were GOAL-LANG-RAKU.md, GOAL-RAKU-FRONTEND.md)

⛔ **Both sources in this track describe Raku's ORIGINAL execution architecture — three modes named
IR-run/SM-run/JIT-run, driven by a Stack Machine engine — which is now WHOLLY RETIRED.** TRACK 1's own
STATUS line says so directly: *"Post-SMX-4: no Stack Machine engine; ONE unified `lower.c`; `IR_*` node
taxonomy; BB run-path. Mode 2 (`--run`) DELETED 2026-06-15. Two native modes only."* Neither source's
"current state" framing (GOAL-LANG-RAKU's April 2026 "RK-47 next" cursor; GOAL-RAKU-FRONTEND's own even
older "Sprint 15" plan) should be read as live — TRACK 1's watermark (724/0, s2026-08-08b) is the actual
current state, four months and a full architecture migration later. This track is kept as a **feature
inventory and a source of not-yet-superseded open items**, not as an active cursor.

**GOAL-RAKU-FRONTEND.md (the original "Tiny Raku" charter) is ENTIRELY SUPERSEDED/DONE.** Its own
Done-when ("a `.raku` fenced block compiles to IR and runs under `--run`; `gather`/`take` maps to BB_PUMP; a
smoke test passes") was met and closed by RK-1 through RK-11 in 2026-04-14 (lexer/parser/lowering/driver/
integration/combinator-parser demo). Its "Phase 5" sprint plan (RK-12 through RK-26: string interpolation,
given/when, arrays, hashes, multi-dispatch, named/typed params, junctions, hyper-ops, standalone BB_PUMP,
basic OO, roles, grammar→BB_ONCE, lazy lists) landed through RK-15 (hashes) under this file directly, and
its remaining items (RK-16 onward) were **absorbed and superseded** by GOAL-LANG-RAKU's more complete rung
ladder below and, later, by the RAKU-100 LADDER's Phase-based plan (TRACK 1). Nothing here represents
open, un-superseded work.

**GOAL-LANG-RAKU.md's rung ladder (RK-1 through RK-69) is a feature-level inventory of what got built under
the old architecture** — most of it (RK-1 through RK-39, RK-56, most of Phase 4's RE engine) is `[x]` DONE
and, per the RAKU-100 LADDER's own framing, its outcomes (hash support, `gather`/`take`, string ops, OO
basics, the BB-native NFA regex engine RK-32..RK-37) survived the SMX-4 migration as runtime capability even
though the execution-mode framing describing HOW they ran is gone. **Genuinely still-open items from this
ladder, cross-checked against whether the RAKU-100 LADDER (TRACK 1) has since re-scoped or absorbed them:**

- **RK-36 — code assertions inside regex** (`{ }`, `<{ }>`, `<?{ }>`, `<!{ }>`, `<&sub>`) — marked
  `[ ]` DEFERRED here (NFA infra committed, executor skipped). **Superseded scope:** RK-GRAM-6 (TRACK 1)
  is the actions/adverbs rung of the NATIVE grammar engine and is the more authoritative home for this now
  — the NFA-based code-assertion executor described here was written against an engine (BB-native NFA
  simulation) that RK-GRAM's own direction note says was DELETED (`d63c374`) in favor of recursive descent.
  Do not resume RK-36 as written; its requirement (code assertions fire correctly, predicate failure
  backtracks) is the actual spec RK-GRAM-6 must satisfy.
- **RK-40 through RK-46 — BB-native Grammar machine** (grammar skeleton, primitive BB boxes, quantifier BB
  boxes, alternation/subrule calls, token/rule/regex semantics, `.parse`/Match object, grammar actions) —
  ALL `[ ]` NOT DONE here. **Fully superseded by RK-GRAM-3a through RK-GRAM-6 (TRACK 1)**, which is the
  live, actually-landed-partway implementation of exactly this design (the architecture descriptions even
  agree closely — Σ/δ/Δ subject triad, BB_PUMP-style boxes per rule). Do not re-open RK-40..46; TRACK 1's
  RK-GRAM ladder is where this work actually lives now.
- **RK-47 through RK-53, RK-55, RK-57 through RK-63, RK-65 through RK-68 — goal-directed features**
  (`last`/`next`/`redo`, `first`, junctions `any`/`all`/`one`/`none`, lazy infinite lists, `reduce`
  meta-op, `zip`/`roundrobin`, hyper-ops, bare `loop{}`, `dir()`, `flat`/`slip`, `unique`/`squish`,
  `rotor`/`batch`, `.pairs`, `combinations`/`permutations`, `multi` dispatch, subrule alias, `$/` Match
  interface, `lazy`/`eager` adverbs, `produce`) — **each maps onto a RAKU-100 LADDER phase** (junctions →
  RK-JUNC2 Phase B; hyper-ops/reduce/zip → RK-OPS Phase B post-AGG; lazy lists → RK-AGG Phase A / RK-VAL;
  multi dispatch → already substantially landed under RK-OO-E, TRACK 1; `$/` Match interface → RK-GRAM-4).
  **Treat this ladder's remaining `[ ]` items as a checklist of Raku surface area to fold into the RAKU-100
  LADDER's phase-by-phase work, not as a separate queue to work through directly** — the RAKU-100 LADDER is
  the authoritative plan and explicitly supersedes the earlier "~14% feature-weighted hand estimate" this
  file's Current-state section was still quoting.
- **RK-69 — extend the full test suite to RK-68** — moot as written (the harness this refers to,
  `test_raku_ir_full_suite.sh`, is TRACK 4's own legacy harness); `test_smoke_raku.sh` (TRACK 1) and the
  `raku_roast_scoreboard.sh` (RAKU-100 LADDER) are the current instruments.

**`--monitor` (documented in GOAL-LANG-RAKU.md, still functional, listed in THE INSTRUMENT above):**
in-process IR/SM/JIT step-by-step comparator; on divergence prints the first statement and variable where
two executors disagree. Its own doc caveat stands: ICN frame locals and Prolog trail variables are not yet
in its snapshot, and it drives all three internally so it is incompatible with plain `--run`/`--compile`
during the comparison itself. The mode names in its help text (IR/SM/JIT) predate the mode-3/4 consolidation
— read them as historical labels for the same three engines this whole track describes, not as currently
selectable `--run`/`--compile` targets.

## ⛔ LON RULINGS WANTED (strike when ruled)

(1) **RAKU-100 LADDER tier table** — ratify/adjust the EXCLUDED/TIER-C/IN-TIER boundary (freezes the
scoreboard denominator; S17 concurrency thin-vs-excluded is the concrete open question, Phase H).
(2) **RK-VAL-c bigint dependency** — gmp vs. own limbs.
(3) Nothing else is currently gated on a ruling across the five source files (the two RAKU-BB items above
are the only LON RULINGS WANTED entries found in any of the five retired files).

## RETIRED NAMES

The five files this consolidation replaces — every reference to any of these names resolves HERE:
- `GOAL-LANG-RAKU.md` — TRACK 4 (superseded execution-mode rung ladder RK-1..69).
- `GOAL-PARSER-RAKU.md` — TRACK 2 (pattern-based `parser_raku.sc` frontend, branch `parser`).
- `GOAL-PST-RAKU.md` — TRACK 3 (Pure Syntax Tree rewrite of the same frontend, PRF-14).
- `GOAL-RAKU-BB.md` — TRACK 1 (goal-directed core: ζ-storage, Seq/generator machinery, grammar engine).
- `GOAL-RAKU-FRONTEND.md` — TRACK 4 (the original "Tiny Raku" charter, fully superseded/closed).

Full text of all five, with every session's original dated narrative, remains in git history (each file's
own `git log` prior to its `git rm` in this consolidation's commit) and in the `FINDING-*.md` files each one
cites.

## LEDGER

- [seat15·2026-08-28] Consolidated the five files above into this one, on the pattern of
  GOAL-{SNOBOL4,ICON,PROLOG}-100.md, per ceo/Lon's order (GOAL-CEO.md CEO-30; task baton
  `goal-consolidate-raku`, rank 1, minted by ceo 2026-08-27 on Lon's in-chat order: "We want one GOAL file
  for each language at this point"). Procedure followed verbatim from the sibling task
  `goal-consolidate-snocone`'s `## NEXT` (that consolidation itself not yet done at time of writing — no
  finished `-100` example existed for Snocone to check against, only its task file's stated procedure).
  Two conflicts found and resolved by keeping both readings dated rather than picking one: (a) the O0-DEV
  FACT RULE (s119) vs. the later, stricter NO-`-O2`-EVER FACT RULE (s262) — s262 wins, both are quoted
  above; (b) GOAL-LANG-RAKU.md's "current state" cursor (April 2026, RK-47 next) vs. GOAL-RAKU-BB.md's
  (August 2026, RK-GRAM-3d next, watermark 724/0) — the August cursor is current, the April one is
  preserved as TRACK 4 feature history with an explicit non-supersession cross-check per item. The ~250
  lines of FACT RULE text GOAL-RAKU-BB.md itself declared "byte-identical" across the four/five GOAL-*-BB
  files were compressed to a pointer citing RULES.md, matching the precedent already set by GOAL-ICON-100.md
  and GOAL-PROLOG-100.md (neither reproduces that boilerplate either). Reference sweep run over `.github/`
  and `SCRIP/scripts/` for all five retired filenames; CLAUDE.md's own routing line was explicitly left
  untouched per the sibling task's own note ("outside git, ceo's edit, not this row's").
