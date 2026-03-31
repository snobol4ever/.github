# SESSION-snocone-x64.md — Snocone × x86 (one4all)

**Repo:** one4all · **Frontend:** Snocone · **Backend:** x86
**Session prefix:** `SC` · **Trigger:** "playing with snocone" or "playing with Snocone x64"

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Snocone language spec | `FRONTEND-SNOCONE.md` | syntax/AST questions |
| x64 emitter patterns | `BACKEND-X64.md` | codegen, register model |

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

## §NOW — SC-7

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Snocone x86** | SC-6 | `663505c` one4all · `d0a6c86` corpus | **M-SC-B06:** `~` negation / `?` query (5 tests) |

### Next action

M-SC-B06 — implement `~` negation and `?` query operators. 5 tests:
negate-fail→succeed, negate-succeed→fail, query-discard-cursor, query-in-if, combined.

Check `SNOCONE_TILDE` (maps to `make_fnc1("NOT",...)`) and `SNOCONE_QUESTION` in `emit_x64_snocone.c`.
Verify via existing `E_NOT`/`E_QUERY` IR paths — may be free like B04. Write 5 corpus tests then confirm.

**Invariants gate:** `snobol4_x86` + `snocone_x86` (snocone is additive over snobol4).
Current baseline: snobol4_x86 `106/106` · snocone_x86 `121p/0f`.
