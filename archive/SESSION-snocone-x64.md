# SESSION-snocone-x64.md — Snocone × x86 (one4all)

**Repo:** one4all · **Frontend:** Snocone · **Backend:** x86
**Session prefix:** `SC` · **Trigger:** "playing with snocone" or "playing with Snocone x64"

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Snocone language spec | `PARSER-SNOCONE.md` | syntax/AST questions |
| x64 emitter patterns | `EMITTER-X86.md` | codegen, register model |

---

## §BUILD

```bash
FRONTEND=snocone BACKEND=x64 TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/run_emit_check.sh                           # expect 981/4
CORPUS=/home/claude/corpus bash test/crosscheck/run_sc_corpus_rung.sh \
  /home/claude/corpus/crosscheck/snocone/rungB05                                  # expect 5/5
```

---

## §NOW — SC-8

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Snocone x86** | SC-8 | `465572c` one4all · `180a3ee` corpus | **M-SC-B07:** next unimplemented construct |

**M-SC-B06 ✅ DONE** (`~` negation / `?` query — 5 tests, rungB06 all pass)

Implementation: `sc_emit_cond` detects `E_FNC("NOT",...)` on condition subject, swaps S/F labels, unwraps inner expr. Handles `~~` double-negation by looping. Zero new runtime symbols. Unary `?x` → `DIFFER(x,"")` already worked via `APPLY_FN_N`. Note: `~(?x)` nested unary+paren form triggers parser stack underflow (shunting-yard issue, separate from B06 scope) — queued as known gap.

**Next action:** SC-9 — identify next rungB or new milestone. Check for unimplemented constructs in xfail list or open corpus gaps.

**Invariants gate:** `snobol4_x86` + `snocone_x86` (snocone is additive over snobol4).
Current baseline: snobol4_x86 `106/106` · snocone_x86 `119p/1f` (A16 pre-existing whitespace).
