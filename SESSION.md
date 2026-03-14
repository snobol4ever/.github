# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `compiled-byrd-boxes-full` (sprint 3/4 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `ace2883 — refactor: dyvide → divyde

---

## Sprint 3 Status — Parse Error on "START\n", root cause identified

Binary compiles clean, exits 0. Output is 10 lines: header comments + "Parse Error" + "START".

### What was done this session (committed at `3ea9815`):

**Complete prefix eradication** — `sno_` and `SNO_` stripped from all ~10,000 occurrences
across 40 files. P4/P5 misspelling technique used for collisions:

| Old | New | Reason |
|-----|-----|--------|
| `sno_int` | `vint` | C keyword |
| `sno_div` | `dyvide` | stdlib `div()` |
| `sno_pow` | `powr` | math.h `pow()` |
| `sno_exit` | `xit` | stdlib `exit()` |
| `sno_abort` | `abrt` | stdlib `abort()` |
| `sno_dup` | `dupl` | unistd.h `dup()` |
| `str` | `strv` | str* family / future |
| `match` | `mtch` | POSIX regmatch_t / future |
| `apply` | `aply` | C++ compat headers |
| `eval` | `evl` | future math/scripting |
| `concat` | `ccat` | future C string lib |
| `index` | `indx` | POSIX index() |
| `replace` | `replc` | future C string lib |
| `init` | `ini` | any lib's init |
| `enter` | `entr` | curses.h |
| `register` | `registr` | deprecated C keyword |

File renames: `snoc_runtime.h → runtime_shim.h`, `snoc.h → sno2c.h`.
`snoc → sno2c` throughout. Binary output unchanged.

### Root cause of Parse Error — traced precisely (carried from prior session):

The main loop matches: `POS(0) *snoParse *snoSpace RPOS(0)` on each input line.

On `"START\n"` (first line, 6 chars):
1. `POS(0)` — passes (cursor=0)
2. `*snoParse` — `mtch_pattern_at` called, engine returns `matched=1 end=0` (zero-width, ARBNO matched zero commands)
3. Cursor stays at 0
4. `*snoSpace` — epsilon branch, cursor stays 0
5. `RPOS(0)` — `cursor(0) != slen(6)` → **FAILS** → Parse Error

**Key debug finding:** ENGINE_ENTRY slen=6 fires, returns matched=1 end=0 — but
**T_BREAK trace never fires**. The engine exits SUCCEED before reaching the BREAK node.
This means the ARBNO in `*snoParse` takes the zero-iteration epsilon branch without
even attempting snoCommand.

**snoLabel's BREAK charset** (line ~16190 of generated C):
```c
SnoVal _v2173 = pat_cat(
    pat_break(to_strv(ccat_sv(ccat_sv(ccat_sv(strv(" "),get(_tab)),get(_nl)),strv(";")))),
    pat_lit("snoLabel")
);
```
The charset `to_strv(ccat_sv(...))` is evaluated at module init time via `get(_tab)`
and `get(_nl)`. If those vars aren't set yet when snoLabel is initialized, charset
may be incomplete.

**But the deeper issue:** ARBNO takes epsilon on "START\n" meaning snoCommand itself
fails before BREAK is ever reached. The engine exits SUCCEED=1 with end=0 from the
ARBNO epsilon path.

---

## ONE NEXT ACTION — inline ALL pattern variables as static Byrd boxes

**Sprint: `compiled-byrd-boxes-full`**

Goal: zero `pat_cat`/`pat_arbno`/`pat_ref` in beauty_full.c init section.
engine_stub.c only. No engine.c. No match_pattern_at().

Pattern variables like `snoParse`, `snoCommand`, `snoLabel` are assigned in the
SNOBOL4 source. sno2c sees the assignment AST. Instead of emitting runtime tree
construction, emit_byrd.c must emit the full static labeled-goto Byrd box C inline.

**E_DEREF (*varname) in pattern context** = look up the variable's assigned pattern
at compile time in the AST, inline its Byrd box. Not a runtime call.

Steps:
1. In emit.c: when emitting a pattern assignment `X = <pattern>`, call emit_byrd
   to emit the static Byrd box for that pattern AND register the label root so
   E_DEREF of X can jump to it directly.
2. In emit_byrd.c E_DEREF: replace match_pattern_at() call with direct goto to
   the inlined pattern's alpha label.
3. Remove pat_cat/pat_arbno/pat_ref/pat_ref from emitted init code entirely.
4. Build with engine_stub.c. Verify zero linker errors.
5. Run on beauty.sno — chase crashes, not engine bugs.

```bash
cd /home/claude/SNOBOL4-tiny
apt-get install -y m4 libgc-dev
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
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
```

Add to engine.c `T_ARBNO<<2|PROCEED` case:
```c
fprintf(stderr, "ARBNO: ctx=%d delta=%d OMEGA=%d yielded=%d\n",
        Z.ctx, Z.delta, Z.OMEGA, Z.yielded);
```

Run: `PAT_DEBUG=1 timeout 5 /tmp/beauty_full_bin < $BEAUTY > /dev/null 2>/tmp/dbg.txt`
Look for ARBNO lines where OMEGA=6 (slen of "START\n").

If ARBNO ctx=0 epsilon → snoCommand is failing on "START\n".
Then trace: which of `snoComment | snoControl | snoStmt` fails and why.
snoStmt = `*snoLabel ...` — is the inner ARBNO also epsilon-branching?

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
    git config user.name "LCherryholmes"
    git config user.email "lcherryh@yahoo.com"
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
| 2026-03-15 | E_DEREF implemented with mtch_pattern_at() | beauty uses *varname ~100x |
| 2026-03-14 | binary links and exits 0 (91d097c) | 3 gcc bugs fixed |
| 2026-03-15 | M-COMPILED-BYRD fired (560c56a) | engine_stub.c + ALL OK |
| 2026-03-15 | uid continuity fix (735c456) | duplicate labels across multiple patterns |
| 2026-03-15 | ARB scan wrap (735c456) | substring scan semantics |
| 2026-03-15 | emit.c wired — byrd_emit_pattern() called (1c2062a) | compiled path active |
| 2026-03-13 | emit_byrd.c written committed (cb3f97e) | C port of Python pipeline complete |
| 2026-03-16 | parse_lbin T_STAR fix + E_DEREF varname + E_REDUCE + SPAT_USER_CALL→T_FUNC (2379052) | *snoParse was E_MUL; USER_CALL fired at materialise not match time |
| 2026-03-16 | emit_charset_cexpr — BREAK/SPAN/ANY/NOTANY runtime charset (8c6d166) | E_VAR/E_KEYWORD/E_CONCAT args produced empty cs="" |
| 2026-03-14 | `beauty-runtime` → `compiled-byrd-boxes-full` — engine.c must not be linked, all patterns must be static Byrd boxes, milestone ordering corrected | Same smoke-test trap: chasing engine.c interpreter bugs that don't matter |
