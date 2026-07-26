# FINDING-2026-07-26 — PL-SYNTAX-1: Operator Table Three-Way Diff + Three Confirmed Defects

**Session:** s153 · **Goal:** GOAL-PROLOG-BB.md → PL-SYNTAX-1 (the syntax axis, structurally invisible to PROLOG-ISO-TRACKER.md and PROLOG-DIALECT-TRACKER.md)

**New file:** `PROLOG-SYNTAX-TRACKER.md` (companion to the two predicate-row trackers)

---

## THE INSTRUMENT FINDING (the session-defining discovery)

s152's first pass on the operator table returned `gprolog=0 swi=1 SCRIP=0`. s152 correctly applied the harness-tell rule and stopped. This session found **three distinct extraction failures, one per system:**

| System | Failure mode | Real count |
|---|---|---|
| GNU | Operators are a C macro table `ADD_OPER(prec, TYPE, "name")` in `EnginePl/oper.c` (`Pl_Init_Oper`), **not** `op/3` directives in `BipsPl/` | 45 core + 22 FD |
| SWI | `OP(ATOM_star, OP_YFX, 400)` — operator text appears only in a trailing `/* * */` comment; grepping for literals found the comment at best | 64 active rows, 61 distinct names |
| SCRIP | `BIN_OPS[]` (infix) is findable — but **prefix operators are hardcoded `strcmp` arms in `parse_term`, not in any table** | 43 infix + 13 prefix |

⭐ **RULE ADDED TO TRACKER:** An operator census must enumerate admission *mechanisms*, not admission *tables*. SCRIP admits prefix operators by `strcmp` exactly as `lower_prolog.c` admits `< > =< >= =:= =\=` by static name-array — same defect class as s152's admission-site finding, different file.

⚠ **PATH LESSON REPEATED (s151's rule, hit again):** SWI's flag table is in `src/os/pl-prologflag.c` and its format engine in `src/os/pl-fmt.c` — `grep src/*.c` misses both. First pass returned 18 flags; the real count is 159.

---

## THREE CONFIRMED DEFECTS (static-found, then probed live — none falsified)

### ⛔ DEFECT 1 (HIGHEST SEVERITY) — `double_quotes` defaults to `atom` under `dialect(gnu)`

```
GNU default:   codes      (PF_QUOT_AS_CODES in flag_c.c)
ISO default:   codes
SCRIP default: atom       (g_pl_flags[] in unification.c:1588)
SCRIP dialect: gnu        (same table)
```

**Probe:** `X = "ab"` → `atom_SCRIP_divergent` / `ab` / `flag(atom)` / `dialect(gnu)`.

Every double-quoted literal in a GNU-conforming program silently becomes an atom instead of a code list. Silent wrong-behaviour, not a parse error. **Highest severity because it is invisible** — programs produce wrong results with no diagnostic.

### ⛔ DEFECT 2 — `:` has precedence 200 in SCRIP, 600 in both references

```
GNU:    ADD_OPER(600, XFY, ":")
SWI:    OP(ATOM_colon, OP_XFY, 600)
SCRIP:  { ":", 200, ASSOC_RIGHT }   ← prolog_parse.c BIN_OPS[]
```

**Probe:** `X = (a:b+c)` → `:(a,b)+c` (SCRIP), meaning parsed as `(a:b)+c`.
Both references (600 > 500) give `a:(b+c)` — `:` is looser than `+`.

**Fix is one token** — `200 → 600` in `BIN_OPS[]` — but a priority change reorders parses tree-wide and needs the full 164/164 ×3-mode gate board. Associativity (xfy) is already correct — `a:b:c` → `:(a,:(b,c))` verified live.

### ⛔ DEFECT 3 — `|` is absent as infix disjunction operator

```
GNU:    ADD_OPER(1105, XFY, "|")
SWI:    OP(ATOM_bar, OP_XFY, 1105)
SCRIP:  TK_PIPE in prolog_lex.c — list-tail syntax only, zero infix entries
```

**Probe:** `( t(9) | t(1) )` → `parse error: expected . at end of clause`.

Both references allow bare `|` as a 1105 xfy synonym for disjunction. Any source using it outside a list context fails to parse.

---

## SUPPLEMENTARY RESULTS (probed, no defect)

- **`?-` absent from operator table** — BENIGN. Directives are handled structurally, loads and runs correctly. §1.3 "unverified" flag cleared.
- **`@` at 900 xfx** — live in SCRIP, in no reference table. `a @ b` → `@(a,b)`. Wants justification or removal (PL-SYNTAX-3).
- **`?=` as operator** — live in SCRIP, absent from both reference operator tables (SWI has `?=/2` as a *predicate*, not an operator). Wants justification or removal.
- **Reader / number syntax §5** — ALL CORRECT: `0'a`→97, `0x1F`→31, `0o17`→15, `0b101`→5, `0'\n`→10, `0'\\`→92, `0' `→32, `{a,b}` parsed. No gap.
- **`write_term/2` GNU 8 options** — all accepted without error. `quoted` `ignore_ops` `max_depth` demonstrably functional. `space_args` accepted, no visible effect (suspected no-op; not a finding on one probe). Four options inconclusive by probe-design limits.

---

## HARNESS ERROR CAUGHT ON MYSELF

First reader probe reported `0'\n` as a parse error. The probe itself was the bug — `printf` emitted `0'\\n` (doubled backslash), so SCRIP correctly rejected malformed input. The tell was visible in the echoed value. Re-run via heredoc: 10. Nearly entered as a fourth defect.

⭐ **RULE ADDED TO TRACKER:** When a probe reports a defect, verify the probe emitted what you think it emitted — echo the generated source, not just the result. A false gap manufactured by the instrument is indistinguishable from a real one in the output.

---

## RUNG STATE (for GOAL-PROLOG-BB.md cursor)

- [x] PL-SYNTAX-1 — operator table three-way diff. STATIC + PROBED. Three defects confirmed live.
- [x] PL-SYNTAX-6 — reader/number syntax. PROBED. No gap.
- [~] PL-SYNTAX-4 — `write_term/2` 8 GNU options: all accepted. `space_args` suspected no-op; 4 inconclusive. Needs targeted per-option probes.
- [ ] PL-SYNTAX-2 ← **NEXT** — `double_quotes` default: decide `codes` (ISO+GNU) vs keep `atom`. One-line fix + flag.
- [ ] PL-SYNTAX-3 — fix `:` to 600; add `|` as 1105 xfy; justify-or-remove `@`/`?=`.
- [ ] PL-SYNTAX-5 — format directives: audit SCRIP against GNU's 22 (SCRIP format/2 not located).
- [ ] PL-SYNTAX-7 — flags: SCRIP 7 vs GNU 42; triage load-bearing subset.

**GATES RUN THIS SESSION:** `scrip` built `-O0`, zero errors. Mode-3 `--run` only — no 164/164 gate suite, no crosscheck, no corpus. This session's work is parser/lexer/flag reading only (no IR/lower/template/codegen touched), so the BB-CODEGEN DESIGN SET did not apply.

**BANKED (carried forward from s152):** int/float standard-order conflation in `rt_pl_term_compare` (NEW s152); NO-LCO deep-recursion segfault + cumulative exhaustion; nested-\+ binding leak; retractall/1 gaps; compiled-path silent-fail on undefined predicates.
