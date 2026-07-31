# FINDING — s21x-x (2026-07-31, Claude)

**ZD-2h RETIRED AS VACUOUS BY CONSTRUCTION · THE VALUE SPINE IS CLOSED · THE CARVE DEBT IS UNMOVED AND THE REASON IS STRUCTURAL**

Commits: SCRIP `2318d7e8` (ZD-2k) · `37d7c7ca` (ZD-2h retirement) · `1f67dc26` (ZD-2l).
Watermark across all three: **m3 232/85 · m4 229/86/2 · DIV=1 {W04_arbno_basic}** — the s21x-w record exactly, **zero broke zero fixed by SET on m4**.

---

## 1. THE HEADLINE — SNOBOL4 HAS NO LEXICAL LOCALS, SO ZD-2h HAD NO NODE CLASS

The NEXT list carried, across several sessions: *"ZD-2h VAR-local/ASSIGN-local under the pin gate — the depth-immune-base question, the 'C-style RBP flavor' of the design (law 3/4: RSP until a genuine brick wall, then the RBP dance)."*

**It describes a node class that does not exist in this frontend.**

**MEASURED.** A gated probe (`SCRIP_ZDLOCAL=1`, retained in source, proven byte-neutral) scans **every** entry of `nodes[]` at the top of `zd_plan` and reports any `IR_VAR`/`IR_ASSIGN` failing `is_global && !graph_has_local`. Result over all 336 crosscheck programs: **ZERO**.

**⚠ THE FIRST INSTRUMENT WAS WRONG AND ITS NULL WAS DISCARDED.** It was first placed inside `zd_wl_kind` — which the run loop **breaks out of at the first bad node** — so it structurally cannot see a local sitting behind an earlier blocker. Its zero was an artifact. Rewritten to scan `nodes[]` independently of run membership, then **validated against a live control** per the s21x-w instrument-trap law: the same probe flipped to the GLOBAL arm fires **193 times in 40 programs**. *A null is evidence only after the instrument has been shown to fire on something.*

**THE REASON IS SEMANTIC AND PERMANENT, NOT A CORPUS GAP.** A name in a `DEFINE` prototype's local list is an **ordinary global**. The manual (Ch.4 p.24) is explicit: existing values are saved on a pushdown stack when the function is called, set to null, and restored to their previous values on return — and the formal arguments get the identical treatment. That is dynamic scoping over the one NV namespace, i.e. **law 7 of the s21x-c design of record**, where `IR_SAVE_RESTORE` handles them as globals.

`graph_has_local` is an **ICON-era LEXICAL frame-slot concept** (ARCH-ICON.md: Icon procedure params and `local`/`static` stay frame slots in BOTH variable-model modes). It has no SNOBOL4 customers, and no corpus growth can produce one.

**CONSEQUENCE.** The "occasional C-style RBP" of the design is still right — but it is not for locals. Law 4's RBP constructs with actual citizens here are the **match family** (ARBNO/FENCE1 variable-length housekeeping) and **IR_CALL's frame dance**. The retirement is written at the whitelist line itself, where a session would go to edit it.

---

## 2. THE CARVE DEBT HAS NOT MOVED, AND THE REASON IS THAT ZD ARMS ARE ADDITIVE

Ledger re-derived live at HEAD (THE MODEL's manifest was stale):

| item | THE MODEL (s21x-r) | HEAD (s21x-x) |
|---|---|---|
| `FR`/`FRQ`/`FRQB` reader sites | 1057 / 108 templates | **1054 / 109 templates** |
| `flat_frame_bytes` | 31 | **30** |
| `op_flat_disp` | 24 | **26** |
| `jcon_value_region` | 7 | **6** |
| `x86_frame_off` | 1 | **1** |

**Twelve armed kinds have decremented the reader debt by essentially nothing.** This is not a failure of the arming — it is structural. Every ZD arm is an `if (_.op_zres) return <ZD arm>;` placed **before** the legacy `FR/FRQ` body. The legacy arm survives untouched and stays **reachable for every declined statement**.

⇒ **Legacy-arm retirement (s21x-v NEXT 4) is gated behind the same two families as everything else.** A template's legacy arm dies only when no reachable staging can decline into it. **Nothing else decrements the 1054**, and this is the honest path to THE MODEL's completion gate.

---

## 3. A DECLINE COUNT IS NOT A BACKLOG — THREE RUNGS RUNNING

| rung | first-blockers cleared | declines | what rose |
|---|---|---|---|
| ZD-2k | 24 (COERCE_STRING 17 + COERCE_INTEGER 7) | 801 → **797** | MATCH_HEAD 227 → 247 |
| ZD-2l | 13 (KEYWORD_SNOBOL4) | 797 → **794** | CALL 508 → 518 |

The census ranks **first**-blockers. Clearing a cheap one mostly **promotes the expensive one behind it** — the same shape ZD-2f found when 106 `IR_SUBSCRIPT` first-blockers turned out to be DEREF+ASSIGN_VAR+CALL underneath. Do not read a decline count as work remaining.

---

## 4. ⚠ ZD-2k's COERCE_INTEGER HALF SHIPPED VACUOUS

**Zero nodes armed corpus-wide.** All 7 of its first-blockers re-exposed something else, so not one of its statements survives to arm. The arm is committed so the next rung need not rewrite it, but it is **UNEXERCISED CODE and must not be counted as proven**: per the `914_lgt` lesson a wrong ZD arm returns wrong **answers** rather than crashing, so an unexercised arm proves nothing until something arms it. COERCE_STRING (5) and KEYWORD_SNOBOL4 (4) *are* execution-validated against the refs.

Non-vacuity was measured with `SCRIP_ZD_DIAG` armed-line counts per kind — **never** by grepping the emitted `.s` for a template's comment string, which does not render and reports a live arm as vacuous.

---

## 5. MANUAL GROUNDING (the constructs this session touched)

- **Ch.17 — implicit vs explicit conversion.** Explicit `CONVERT()` *fails* when a conversion is impossible; **implicit** conversion — what the lowerer inserts for `IR_COERCE_*` — is attempted and raises an **error message** if it cannot be done. That is `core_runtime_error`, never a statement failure ⇒ the γ-only port topology with no ω is the **contract**, not an omission.
- **Ch.3 — numeric coercion.** String→numeric ignores leading/trailing blanks, the null string converts to integer 0, an interior blank or non-numeric body is an error; integer÷integer truncates; either operand real ⇒ real result. All of it lives inside `rt_coerce_int_d` and none of it reaches the port topology.
- **Ch.16 — keywords.** A keyword *read* always yields a value (protected keywords cannot be **assigned**, but reading never fails) ⇒ γ-only, no ω.
- **Ch.4 p.24 — DEFINE locals.** The save/restore pushdown-stack semantics quoted in §1.

---

## 6. ⚠ A SECOND HARNESS-ONLY FLAKE, NAMED

`213_gc_exhaustion_churn` joins `test_string`: it **fails under the harness** but passes **5/5 standalone with md5 matching its ref**. Both appeared as phantom "fixes" in every m3 diff this session. **COMPARE m4, NEVER m3.** The m4 fail set was byte-stable at 86 by SET across all three commits — which is what makes "zero broke" a measurement rather than a claim.

---

## 7. NEXT

1. ⭐⭐ **ZD-5 MATCH FAMILY / `IR_MATCH_HEAD` (247)** — the real target and the genuine law-4 RBP citizen. The HEAD..RELEASE bracket **is** the STATEMENT construct, so the shape to test is *RBP housekeeping bracket + RSP ζ cells for the value spine inside it* — **not** a ZD arm cloned onto a match box. ⚠ Weld the `stfh` 48B carve vs `bb_match_release`'s fixed head-cell reads (s21x-q root) first; it is the known mine in this family.
2. **`IR_CALL` (518)** — its own protocol rung; law 6's two-BB DEFINE world is the design.
3. **`IR_FIELD_VAR` + `IR_FIELD_GET` measured as a PAIR** — they share dispatch case `:1052`, so arming one alone declines on the sibling (the COERCE_NUMERIC/CMP_TEST pairing lesson).
4. **`IR_SAVE_RESTORE` (18)** — NOT clone material; its `:989` preamble mutates `g_emit` and IS the CALL2BB arg-window linkage. Goes with (2).
5. `IR_GOTO_DEFERRED` (6) rides the jmp-entry protocol rung, declined wholesale by design.
6. The 130/131 clean-HEAD segv, still unchased.
