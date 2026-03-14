# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-runtime` (sprint 3/4 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `8c6d166` — fix(emit_byrd): emit_charset_cexpr — runtime charset for BREAK/SPAN/ANY/NOTANY |

---

## Sprint 3 Status — Parse Error on "START\n", root cause identified

Binary compiles clean, exits 0. Output is 10 lines: header comments + "Parse Error" + "START".

### What was done this session (committed at `8c6d166`):

**emit_charset_cexpr added to emit_byrd.c** — BREAK/SPAN/ANY/NOTANY were emitting
empty charset `""` for E_VAR, E_KEYWORD, E_CONCAT args. Fixed with runtime
`sno_to_str(sno_var_get(...))` and `sno_concat_sv(...)` expressions.
E_KEYWORD and E_DEREF cases also added. snoc_runtime.h macro collision
handled via `sno_concat_sv` with `SNO_STR_VAL` wrappers.

**T_FUNC wiring confirmed working** — `deferred_call_fn` fires for nPush/reduce/nPop.
Engine dispatch is correct. Struct layout is correct.

### Root cause of Parse Error — traced precisely:

The main loop matches: `POS(0) *snoParse *snoSpace RPOS(0)` on each input line.

On `"START\n"` (first line, 6 chars):
1. `POS(0)` — passes (cursor=0)
2. `*snoParse` — `sno_match_pattern_at` called, engine returns `matched=1 end=0` (zero-width, ARBNO matched zero commands)
3. Cursor stays at 0
4. `*snoSpace` — epsilon branch, cursor stays 0
5. `RPOS(0)` — `cursor(0) != slen(6)` → **FAILS** → Parse Error

`snoParse` matches zero commands because `snoCommand = nInc() FENCE(snoComment | snoControl | snoStmt)` fails on `"START\n"`. Specifically:

- `snoStmt = *snoLabel ...` calls `sno_match_pattern_at(snoLabel, "START\n", 6, 0)`
- `snoLabel = BREAK(' ' tab nl ';') ~ 'snoLabel'` — runs through **interpreter path** (sno_pat_break), not compiled Byrd boxes
- `sno_match_pattern_at` → `try_match_at` → `engine_match_ex` returns `matched=1 end=0`
- BREAK on `"START\n"` at position 0 should scan S,T,A,R,T and stop at `\n` → end=5
- Instead it returns end=0 — **zero-width BREAK match**

**Hypothesis**: The charset for `snoLabel`'s BREAK is being built as empty string at runtime.
`snoLabel = BREAK(' ' tab nl ';')` — `tab` and `nl` are variables. At the time `snoLabel`
is materialized, `tab` = `"\t"` and `nl` = `"\n"` (set in sno_inc_init). The charset should
be `" \t\n;"`. If `sno_to_str(sno_concat_sv(...))` returns `""` or `" ;"` (missing tab/nl),
BREAK would match zero chars on `'S'` because `'S'` is not in `" ;"` — but it's also not
a break char, so BREAK should scan forward. Wait — BREAK stops BEFORE a charset char.
If charset is `" ;"` only, `'S','T','A','R','T'` are all not in charset, `'\n'` is also
not in charset → BREAK scans to end of string and **fails** (never finds a break char).
End of string = slen, BREAK fails → returns -1 via `sno_match_pattern_at` returning -1.

Actually re-reading `scan_BREAK`:
```c
while (z->delta < z->OMEGA) {
    for (const char *c = z->PI->chars; *c; c++)
        if (*z->sigma == *c) return true;  // found break char
    z->sigma++; z->delta++;
}
return false;  // never found break char → BREAK fails
```
If charset is `" ;"` (no `\n`), BREAK scans all 6 chars of "START\n" without finding
a char in `" ;"`, returns false → BREAK fails → engine reports `matched=0`. But
`try_match_at` showed `matched=1 end=0`. Contradiction.

**Revised hypothesis**: BREAK is NOT failing — it's matching zero chars (end=0).
That means at position 0, `'S'` IS immediately in the charset — so BREAK stops
immediately at 0 chars. This would happen if charset contains `'S'`... which it
wouldn't. OR: the match is epsilon-branching before BREAK. OR the engine sees BREAK
as a zero-width match for another reason.

---

## ONE NEXT ACTION — trace BREAK inside engine on snoLabel

```bash
cd /home/claude/SNOBOL4-tiny
apt-get install -y m4 libgc-dev
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
TOKEN=TOKEN_SEE_LON
git clone https://$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-tiny.git
git clone https://$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-corpus.git

cp /mnt/user-data/uploads/snobol4-2_3_3_tar.gz .
tar xzf snobol4-2_3_3_tar.gz && cd snobol4-2.3.3
./configure --prefix=/home/claude/snobol4-install && make -j$(nproc)
cd ..

cd SNOBOL4-tiny && make -C src/sno2c

CORPUS=/home/claude/SNOBOL4-corpus
INC=$CORPUS/programs/inc
BEAUTY=$CORPUS/programs/beauty/beauty.sno
R=src/runtime

./src/sno2c/sno2c -I $INC $BEAUTY > /tmp/beauty_full.c
gcc -O0 -g -I $R/snobol4 -I $R \
    /tmp/beauty_full.c $R/snobol4/snobol4.c \
    $R/snobol4/snobol4_inc.c $R/snobol4/snobol4_pattern.c \
    $R/engine.c -lgc -lm -o /tmp/beauty_full_bin

SNO_PAT_DEBUG=1 timeout 5 /tmp/beauty_full_bin \
    < $BEAUTY > /dev/null 2>/tmp/pat_debug.txt
grep "engine_match_ex\|ENGINE_ENTRY\|BREAK\|T_BREAK\|try_match" /tmp/pat_debug.txt | head -40
```

The engine.c T_BREAK dispatch (`case T_BREAK<<2|PROCEED`) adds debug at slen<=8.
Check if slen=6 ENGINE_ENTRY appears AND what T_BREAK does. Add explicit trace:

```c
// In engine.c, case T_BREAK<<2|PROCEED — add after the existing debug block:
case T_BREAK<<2|PROCEED:
    fprintf(stderr, "T_BREAK: delta=%d OMEGA=%d chars='%s'\n",
            Z.delta, Z.OMEGA, Z.PI->chars ? Z.PI->chars : "(null)");
    if (scan_BREAK(&Z)) { ...
```

**If chars is "(null)" or ""** → snoLabel's BREAK pattern node has empty/null charset
→ `sno_pat_break()` in snobol4_pattern.c is not setting `chars` correctly when the
charset value involves variable concat at materialise time.

**If chars is correct** → look at why scan_BREAK returns false/true with that charset
on subject `"START\n"`.

The fix will be in `snobol4_pattern.c` `materialise()` case `SPAT_BREAK` — it calls
`sno_to_str()` on the charset SnoVal. Verify the SnoVal being passed is correct.

---

## CRITICAL: What Next Claude Must NOT Do

- Do NOT write the TOKEN into any file
- Do NOT remove fn_seen[] / byrd_fn_scope_reset()
- Do NOT reset byrd_uid_ctr
- Do NOT use engine_stub.c — link real engine.c (*snoParse needs it)
- Do NOT rewrite emit_byrd.c wholesale — only targeted fixes

---

## Container State (clone fresh each session)

    apt-get install -y m4 libgc-dev
    git config --global user.name "LCherryholmes"
    git config --global user.email "lcherryh@yahoo.com"
    TOKEN=TOKEN_SEE_LON
    git clone https://$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-tiny.git
    git clone https://$TOKEN@github.com/SNOBOL4-plus/SNOBOL4-corpus.git
    git clone https://$TOKEN@github.com/SNOBOL4-plus/.github.git dotgithub

    cp /mnt/user-data/uploads/snobol4-2_3_3_tar.gz .
    tar xzf snobol4-2_3_3_tar.gz && cd snobol4-2.3.3
    ./configure --prefix=/home/claude/snobol4-install && make -j$(nproc)
    cd ..

    cd SNOBOL4-tiny && make -C src/sno2c

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | sno_output_str fix — linker error resolved (e78d177) | sno_output(str_t) does not exist |
| 2026-03-14 | M-PYTHON-UNIFIED retired → M-BYRD-SPEC (HQ 0959202) | Python was scaffold, not destination |
| 2026-03-14 | JCON lessons recorded in MISC.md (HQ a120be6) | bounded flag, temp liveness, jvm guidance |
| 2026-03-15 | fn_seen[] + byrd_fn_scope_reset() — cross-pattern decl dedup | static redecl errors in Gen/Qize |
| 2026-03-15 | E_DEREF implemented with sno_match_pattern_at() | beauty uses *varname ~100x |
| 2026-03-14 | binary links and exits 0 (91d097c) | 3 gcc bugs fixed |
| 2026-03-15 | M-COMPILED-BYRD fired (560c56a) | engine_stub.c + ALL OK |
| 2026-03-15 | uid continuity fix (735c456) | duplicate labels across multiple patterns |
| 2026-03-15 | ARB scan wrap (735c456) | substring scan semantics |
| 2026-03-15 | emit.c wired — byrd_emit_pattern() called (1c2062a) | compiled path active |
| 2026-03-13 | emit_byrd.c written committed (cb3f97e) | C port of Python pipeline complete |
| 2026-03-16 | parse_lbin T_STAR fix + E_DEREF varname + E_REDUCE + SPAT_USER_CALL→T_FUNC (2379052) | *snoParse was E_MUL; USER_CALL fired at materialise not match time |
| 2026-03-16 | emit_charset_cexpr — BREAK/SPAN/ANY/NOTANY runtime charset (8c6d166) | E_VAR/E_KEYWORD/E_CONCAT args produced empty cs="" |
