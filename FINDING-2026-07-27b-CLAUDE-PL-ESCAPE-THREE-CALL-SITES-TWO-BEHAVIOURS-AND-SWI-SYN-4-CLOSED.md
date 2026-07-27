# FINDING 2026-07-27b (s156) — THE ESCAPE DEFECT IS THREE CALL SITES WITH TWO WRONG BEHAVIOURS, NOT ONE ARM; `PL-SWI-SYN-4` CLOSED; SWI SOURCE SECONDS THE INT/FLOAT DEFECT

**Session type:** source-read + document extension. **NO SOURCE MODIFIED. NOTHING BUILT, NOTHING RUN.**
Everything below is a read of `refs/swipl-devel-master` (SWI **10.1.5**) and
`SCRIP/src/parser/prolog/prolog_lex.c`, plus a re-reading of s155's committed probe results.
Read-vs-probe status is labelled per claim, per the s152 rule.

---

## 0. WHAT THIS SESSION PRODUCED

`PROLOG-SWI-SYNTAX-SEMANTICS.md` extended 384 → ~640 lines: **new §10 arithmetic · §11 standard order ·
§12 tokenizer char classes · §13 control constructs · §14 DCG**, plus **§2.1.1** (this finding's escape
table) and an updated §PROVENANCE / §8 honesty boundary.

---

## 1. ⭐⭐ THE ESCAPE DEFECT'S MECHANISM WAS MIS-BANKED — AND THE MIS-BANKING WOULD HAVE PRODUCED AN INCOMPLETE FIX

s155 banked: *"reader lexer (unknown escape silently passes char through) … Root cause:
`prolog_lex.c:98` default arm passes char through, never raises."* One arm, one behaviour.

**Source says otherwise.** `decode_escape()` (`prolog_lex.c:70`) is **three-valued**:

| return | meaning |
|---|---|
| `1` | escape recognised, `*code` valid |
| `0` | `\<newline>` line continuation |
| `-1` | unknown escape; `*code` = the raw char |

The `default:` arm is therefore **not** silent — it signals `-1`. **The behaviour is decided by the
callers, and there are THREE of them treating `-1` in TWO different ways:**

| Call site | Context | On `\q` | Result |
|---|---|---|---|
| :116 | quoted atom `'…'` | `buf_push('\\')` **then** `buf_push(q)` | 2 chars, `\q` |
| :138 | double-quoted `"…"` | same | 2 chars, `\q` |
| :157 | char-code `0'\q` | `t.ival = (st==1) ? code : (long)'\\'` | **92**, the `q` consumed and **DISCARDED** |

**Row :157 is a distinct defect and was never probed.** It does not "pass the char through" — it
*destroys* it and yields backslash. A fix that edits only the `default:` arm (what the banked wording
invites) leaves `0'\q` returning 92 unless the **call site** is fixed too.

**CONFIDENCE / STATUS:**
- :116 and :138 are **READ, CROSS-VALIDATED BY s155's PROBE** — my read predicts exactly the byte
  sequences s155 measured live (`'a\sb'` → `[97,92,115,98]`, `'a\zb'` → `[97,92,122,98]`). Agreement
  of an independent read with a committed probe is why I trust the read for the third row.
- :157 is **READ ONLY. NOT PROBED.** ⚠ Run `X is 0'\q` before closing anything on it.

**SWI comparison (read, `pl-read.c` `escape_char()`):** all three positions raise. The `undef:` label
calls `errorWarningA1("undefined_char_escape", …)` and returns `ESC_ERROR` (-2). SWI has no
pass-through path at all.

**This strengthens, not weakens, s155's SILENT-ACCEPTANCE CLASS.** The class is real; its lexer member
is *worse* than banked, because one of its three sites is lossy rather than merely permissive.

---

## 2. ⭐ `PL-SWI-SYN-4` CLOSED — THE FOUR ESCAPES MEASURED AGAINST SWI

The open rung asked whether `\u`/`\U`/`\e`/`\s` had ever been compared to the SWI axis. Answer:

| Escape | SWI 10.1.5 | GNU 1.4.5 (s155 live) | SCRIP | verdict |
|---|---|---|---|---|
| `\e` | 27 | **syntax error** | **27** | ⭐ SCRIP **matches SWI, not GNU** |
| `\s` | 32 | syntax error | `\`+`s` | diverges from both |
| `\u`XXXX | 4-hex | unsupported | `\`+`u` | diverges |
| `\U`XXXXXXXX | 8-hex | unsupported | `\`+`U` | diverges |
| `\c` | skip blanks | — | `\`+`c` | diverges |

⛔ **CONSEQUENCE FOR PL-SYNTAX-2/3's DIALECT QUESTION.** SCRIP is **not uniformly GNU-flavoured**. On
`\e` it already agrees with SWI while the installed GNU 1.4.5 *rejects* it. **A rung phrased as "align
the reader to GNU" would REGRESS `\e`.** This is the same shape as s155's §6 finding that
`double_quotes` has four values in play, not two: the dialect question is not binary, and the engine is
already a mixture. **Lon's ruling on the target dialect should be made per-axis, not once globally.**

---

## 3. ⭐⭐ SWI SOURCE INDEPENDENTLY SECONDS THE BANKED INT/FLOAT DEFECT — IT IS NOW TWO-ORACLE

s152 banked `rt_pl_term_compare` conflating int and float on **one** oracle (gprolog 1.4.5). SWI
10.1.5 source agrees with gprolog on **both** cases under default flags:

- **`1 == 1.0` → false.** `compare_primitives()` :1821 returns `CMP_NOTEQ` on tag mismatch when
  `eq=true`, *before* any numeric path. Flag-independent.
- **`1.0 @< 1` → true.** With `iso=false` (**the default** — `os/pl-prologflag.c:1996`), mixed
  int/float routes to `compare_mixed_float_rational()` :1759, which compares **by value** and then
  tie-breaks `rc = (tag(w1)==TAG_FLOAT) ? CMP_LESS : CMP_GREATER` — **Float before Int at equal value.**

SCRIP reportedly returns true/false respectively — **wrong on both, against both references.**

**Why this matters procedurally:** there is **no dialect choice to make here.** ISO, GNU and SWI want
the same answer, so the banked item needs no Lon ruling — only a rung. That is unusual in this
tracker's backlog and makes it cheap to schedule.

**Bonus, previously unrecorded:** under `iso=true` SWI drops value comparison entirely and sorts by raw
tag (`TAG_FLOAT(2) < TAG_INTEGER(3)`), so **every** float precedes **every** integer (`2.0 @< 1`
succeeds). If SCRIP ever grows an `iso` flag, standard order is one of the things it must switch.

---

## 4. §10's THREE TRAPS FOR WHOEVER AUDITS ARITHMETIC NEXT

79 evaluable functors, **single admission site proven** (raw `ADD(` count == resolved rows;
`registerFunction` called only from one loop over `ar_funcdefs`, :4978-4982).

1. **`atan` exists at BOTH arities, and `atan2/2` is a separate ISO-flagged alias** onto the same C
   function `ar_atan2`. A name-keyed table assuming one arity per name silently loses a row.
2. **⛔ `F_ISO` IS SWI'S SELF-ANNOTATION, NOT AN ISO ORACLE.** `//`/2 carries no `F_ISO` despite being
   ISO-evaluable. Do not use this column as the ISO axis; `PROLOG-ISO-TRACKER.md` is that axis.
3. **The six arithmetic comparisons are NOT in the functor table** — they are `PRED_IMPL(…, PL_FA_ISO)`
   at `pl-arith.c:672-702`. **This is structurally identical to the split s152 found on the GNU axis**,
   where the comparisons lived only in `lower_prolog.c`'s name arrays and *both* audits wrongly
   reported them as gaps. An arithmetic audit reading only `ar_funcdefs` will manufacture the same six
   false gaps on the SWI axis.

---

## 5. §12 IS THE SPEC `prolog_lex.c` IS MISSING

SWI's `_PL_char_types[]` (`os/pl-ctype.c:1007`) assigns every byte ≤0xFF exactly one class. The
load-bearing row is **`SY` (17 chars: `# $ & * + - . / : < = > ? @ \ ^ ~`)** — a maximal munch over
`SY` is *why* `=..`, `:-`, `-->`, `*->`, `@=<` lex as single tokens **without appearing in any operator
list**. The operator table is consulted only *after* the token is formed.

A lexer that instead matches known operator spellings accepts the same programs but **diverges on
errors and on user-defined symbol operators** — which is precisely the failure surface s155's
silent-acceptance class lives on. §12 is now written down as the diff target.

**SCRIP column: ABSENT — not read this session.** Next cheap rung: diff SCRIP's classifier against §12.

---

## 6. INSTRUMENT NOTES (three self-caught errors, logged per the s153 rule)

1. **My extractor emitted `atan/22` and `log/101`.** Non-greedy regex `FUNCTOR_(\w+?)(\d+)` split
   `FUNCTOR_atan22` as `atan`+`22`. Fixed by generating *every* candidate split and accepting only one
   the ATOMS `F`-table confirms; re-run gives 0 unresolved, 0 ambiguous. **RULE: a `<name><arity>`
   symbol cannot be split by regex when names may end in digits — it must be resolved against the
   table that defines the names.**
2. **I then "verified" the fix with a grep that used a literal space where ATOMS uses TABs**, and
   briefly concluded my (correct) parser was broken. The s153 rule — *verify the probe emitted what you
   think it emitted* — applies to **verification commands** as much as to probes.
3. **I grepped for `decode_escape`'s call sites with a pattern that omitted `decode_escape`.** Empty
   result nearly read as "no callers." Same class as s151's "grep came back empty — check the search
   path" note; here the path was fine and the *pattern* was wrong.

---

## 7. GATES / WATERMARK

**NO GATES RUN — NO SOURCE MODIFIED, NOTHING BUILT.** No rung suite, no `no_new_global`, no
medium-invisible; the **BB-CODEGEN DESIGN SET did not apply** (no IR / lower / template / codegen
touched). No `-O2` sought or used; nothing compiled at all.

**WATERMARK (files touched — push state NOT recorded here per the stale-orientation FACT RULE;
`scripts/handoff_status.sh` is the only ground truth):**
SCRIP `<none>` / corpus `<none>` / `.github` `PROLOG-SWI-SYNTAX-SEMANTICS.md (§2.1.1 + §10-§14 +
provenance + §8) · this FINDING (new) · GOAL-PROLOG-BB.md LIVE CURSOR`.

**NEXT:**
1. **Probe `X is 0'\q`** — the one unverified row in §1, and the row that changes the fix's shape.
2. **Diff SCRIP's lexer classifier against §12** (cheap; the reopened PL-SYNTAX-6's real spec).
3. **`PL-STRICT-1`** (s155's proposed silent-acceptance rung) — now with a sharper lexer member.
4. **The int/float rung** — two-oracle agreement, no dialect ruling needed (§3).
5. Lon ruling on target dialect **per axis, not globally** (§2).
