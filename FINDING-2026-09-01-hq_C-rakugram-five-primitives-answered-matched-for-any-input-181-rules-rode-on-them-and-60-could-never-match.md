# FINDING (hq_C, 2026-09-01): the Grammar.nqp port's five matching primitives were placeholders that answered "matched" for ANY input — 181 of 518 rules rode on them, 60 could never match, and all five were counted as MECHANICAL in the headline ladder

**Row:** `raku-roast-100-percent-compile` (hq_C). **Landed:** SCRIP `bcb0ec1e`. **Gate:** `scripts/test_gate_rakugram_precedence.sh` rc=0 (77 checks, rung-7 section added).

## The claim, measured

The rung-3 emitter (`tools/rakugram/nqp_emit.py`) rendered five AST node kinds through primitives it defined in its own header:

| primitive | what it did | consequence |
|---|---|---|
| `rk_cclass(c, spec)` | `(void)spec; c->pos++; return 1` | `<[0-9]>` matched `'z'`; `<?[…]>` guards **advanced** |
| `rk_esc_s(c, k)` | `(void)k; c->pos++; return 1` | `\d`, `\w`, `\h` each matched any character |
| `rk_anchor(c, k)` | `return 1` | `^^` / `$$` never constrained |
| `rk_wb(c)` | `return 1` | `«` / `»` never constrained |
| `rk_look_stub(c)` | `return 1`, **operand discarded** | positive lookahead always passed; **negative lookahead always failed** |

The last row is the destructive one. The emitter rendered `<!foo>` as `if (rk_look_stub(c)) goto fail;` — with the stub always 1, that is `if (1) goto fail`: **every rule containing a negative lookahead was unconditionally unmatchable.**

Census on the generated parser (same tree, before the cure):

```
rules touching >=1 silently-wrong primitive : 181 of 518
rules containing a negative lookahead        :  60   -> could never match anything
call sites: rk_look_stub 246 · rk_esc_s 118 · rk_cclass 54 · rk_anchor 21 · rk_wb 6
```

All five node kinds (`LOOK`, `CCLASS`, `ESC`, `ANCHOR`, `WB`) sat in `nqp_ast.MECHANICAL`, so the port's headline "% mechanical" counted every one of these rules as translated.

## Why it was invisible — and the general form

⭐ **Every one of these stubs passes every positive test.** A class that matches everything matches `'5'`; an anchor that always holds holds at line start; a lookahead that always succeeds succeeds when it should. The only thing a placeholder cannot fake is a **rejection** — which is why `rk_cc_test.c` is written entirely as accept/reject pairs and why a syntax-only "it parses" test would have graded the stubs green forever.

This is the `nqp_emit.py` header's own forbidden case, inverted and worse. The header says a production that cannot be emitted must **refuse**, never return a silent "no match", because "did not match" is indistinguishable from a correct decline. These returned a silent **"matched"** — indistinguishable from a correct accept, and additionally consuming input the grammar never asked to consume.

**General form (RULES.md § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE):** a stub that returns the *success* value is reachable from "implemented and matched" and from "not implemented"; nothing downstream can tell which. The correct stub value for a matching primitive is never `1` — it is a refusal the caller cannot mistake for a verdict.

## The cure — SCRIP `bcb0ec1e`

- **`tools/rakugram/nqp_cc.py`** (new): character classes, backslash escapes and anchors are lowered **at generation time**, in Python, into codepoint-range tables (`RkCCItem`). The emitted C (`rk_cc`, `rk_anchor`, `rk_wb`) is **total** — there is no spec it can fail to understand, so there is no path on which it guesses. A spec that will not lower **refuses** (`RK_UNIMPL`) at generation time. UTF-8 is decoded per codepoint (`<[-−]>` consumes U+2212 as one 3-byte character).
- **`LOOK` emits its operand** as a zero-width island (`save; run sub; restore; branch`). `<?{ code }>` (gates on NQP), `<?after …>` (backwards matching) and bare `<?>` **refuse**.
- **One resolver.** `look_operand()` moved to `nqp_ast.py` and is used by BOTH the emitter and `emit_all()`'s called-set walk. Resolving only at emit time manufactured phantom `rk_alpha` / `rk_ww` — implicit-declaration **warnings**, so the file compiled and would have linked against nothing. That is the phantom-rule class the `mkcall` docstring already records; one shared function is what stops it returning.
- **`nqp_ast.lowers(n)`** — the ladder now counts a shape as mechanical **only if it lowers**, by asking the same functions the emitter asks.

## Honest numbers — same tree, one change (REBASE-BASELINE COROLLARY honoured)

| | rung 3 (shape-only) | rung 7 (honest) |
|---|---|---|
| generated rules | 236 | **214** |
| refusing rules | 243 | **265** |
| rules on a silently-wrong primitive | 181 | **0** |
| rules that can never match | 60 | **0** |
| class tables emitted | — | 51 (identical classes share one) |
| "fully mechanical" over 739 | 419 (56.7%) | **384 (52.0%)** |

**The number went down because the instrument stopped lying.** 22 rules that looked translated now correctly refuse; 35 productions leave the mechanical count. This is the ledger's own doctrine (`calling-convention-depth-tracked` baton, ceo 2026-08-30): *an instrument getting more honest may legitimately worsen its number.*

⚠️ **The published "mechanical today: 477 (64.5%)" does not reproduce on today's tree even with the honest check disabled** — I measure 419 (56.7%) shape-only. It predates the reader fix that recovered 56 declarations and the exposure above. Flagged in `tools/rakugram/README.md`'s table and in the baton's QA, not silently rewritten. My delta (56.7% → 52.0%) is instrument-internal and apples-to-apples; the absolute 64.5% is not mine to adopt.

## Three Raku facts the lowering asserts, each of which misparses plausibly

1. **Ranges are `..`, not `-`.** `<[1..9]>` is a range; `<[-−]>` is two literals. The POSIX habit turns the latter into `'-'..U+2212` and silently swallows every ASCII letter and digit.
2. **Literal whitespace inside `<[...]>` is insignificant.** `<[ i g s m x c e ]>` is seven members, not nine. A space must be `\s` or `\x20`.
3. **`<?[…]>` / `<![…]>` are zero-width.** The six spellings vary on two independent axes (membership polarity × width); the stub advanced for all six, so every zero-width guard also ate a character.

## What this rung did NOT do — stated so the baton cannot be misread

**No real Raku program parses end to end yet.** The brief's next rung was "wire `comp_unit`, connect `rk_parse_term`, take the first program end to end"; doing that on primitives that answer "matched" for any input would have produced a confident wrong answer, so the primitives came first. The spine (`comp_unit` → `statementlist` → `statement`) still refuses on `:my` (68 declarations in `comp_unit` alone) and `{ code }` blocks. Measured: **32 rules refuse ONLY because of `:my`** (`xblock`, `signature`, `routine_declarator:sub`, `package_declarator:class` among them); CODE affects 123, UNSUPPORTED 73, MOD 54.

⛔ **The next step carries a correctness hazard of its own, named here so it is not walked into:** `:my` and `{ code }` consume no input and cannot fail, so treating them as no-ops *for matching* is sound — **but only at the declaration**. Rules that *consult* a parse-time variable (`<?{ $*IN_DECL }>`, `$*QSIGIL`, `$*GOAL`, `<.stopper>`) gate on its value; a no-op `:my` plus an un-modelled consultation is a silent wrong answer again. Those consultation sites must **keep refusing** until the variable is actually modelled. The `look_operand()` refusal of `<?{ … }>` is the first half of that discipline already in place.

## Reproduce

```bash
cd SCRIP && bash scripts/test_gate_rakugram_precedence.sh                  # rc=0; rung-7 rows are the REJECTS
python3 tools/rakugram/nqp_cc.py --selftest                                 # tables in rk_cc_test.c == generator output
python3 tools/rakugram/nqp_emit.py /home/resources/rakudo-main/src/Perl6/Grammar.nqp /tmp/g.c | tail -6
grep -c 'rk_look_stub\|rk_cclass(\|rk_esc_s(' /tmp/g.c                     # 0 -- no placeholder in the output
python3 tools/rakugram/nqp_ast.py | sed -n '3,8p'                          # 52.0% fully mechanical, honest
```
