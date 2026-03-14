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
| **HEAD** | `35bc142 — artifact: beauty_full_session54.c` |

---

## Sprint 3 Status — Architecture documented, implementation not started

Session 54 was architecture-only. No code changed. The path forward is clear.

### What was decided and recorded in HQ (c7ccace, 8582351, fb02aea):

**TWO TECHNIQUES for *X:**
- Technique 1 (NOW, C target): named pattern → C function with struct locals.
  `pat_X(pat_X_t **zz, int entry)`. Child frames = pointer fields in parent struct.
  ARBNO depth = `int64_t stack[64]` in struct. calloc on first entry.
- Technique 2 (AFTER M-BEAUTY-FULL, ASM target): mmap + memcpy + relocate.
  TEXT=PROTECTED(RX), DATA=UNPROTECTED(RW). ~20 lines.

**Statement execution model (Session 27 eureka, now in PLAN.md):**
- Each statement = Byrd Box. Hot path = pure gotos. Cold path = longjmp for ABORT only.
- Per-statement setjmp (not yet done), glob-sequence optimization (not yet done),
  non-Gimpel DEFINE special case (not yet done). Per-function setjmp already done.

**ALL BYRD BOXES rule:** engine.c MUST NOT be linked in beauty_full_bin. engine_stub.c only.
Do NOT chase engine.c bugs. That is the smoke-test trap.

---

## ONE NEXT ACTION — implement byrd_emit_named_pattern (Technique 1)

This is the key function that makes *X work in the C target.

### What to implement

In `src/sno2c/emit_byrd.c`, add `byrd_emit_named_pattern(varname, expr, out)`:

```c
// Emits for: snoParse = nPush() ARBNO(*snoCommand) reduce(...) nPop()
//
// Output:
//   typedef struct pat_snoParse_t {
//       int64_t  saved_7;          // cursor saves — one per decl_buf entry
//       int      arbno_depth;      // ARBNO stack depth
//       int64_t  arbno_stack[64];  // ARBNO iteration stack
//       struct pat_snoCommand_t *snoCommand_z;  // child frame ptr for *snoCommand
//   } pat_snoParse_t;
//
//   static SnoVal pat_snoParse(pat_snoParse_t **_zz, int _entry);
//   static SnoVal pat_snoParse(pat_snoParse_t **_zz, int _entry) {
//       pat_snoParse_t *_z = *_zz;
//       if (_entry==0){if(!_z)_z=*_zz=calloc(1,sizeof(*_z));
//                      else memset(_z,0,sizeof(*_z)); goto snoParse_alpha;}
//       if (_entry==1){ goto snoParse_beta; }
//       snoParse_alpha: ...byrd box using _z->saved_7 etc...
//       snoParse_gamma: _np_cur_g = _np_cur; return <matched SnoVal>;
//       snoParse_omega: return FAIL_VAL;
//   }
```

### Key design points from the oracles (sprint9/sprint10)

1. ALL locals go in the struct — no statics, no inline declarations after goto
2. Child frame for *X = pointer field `struct pat_X_t *X_z` in parent struct
3. `*X` at a call site emits: `pat_X(&_z->X_z, 0)` / `pat_X(&_z->X_z, 1)`
4. ARBNO: `int arbno_depth` + `int64_t arbno_stack[64]` in struct (like test_sno_1.c `_1_t _1[64]`)
5. Forward declaration emitted before function body (for mutual recursion)
6. `byrd_register_pat(varname, alpha_label, beta_label)` called after emission
7. E_DEREF (*varname): check registry → emit call, not match_pattern_at()

### Global subject/cursor threading

Named pattern functions need the subject/cursor. Two options:
- Thread as function args (cleaner but changes signature)
- Use globals `_np_subj_g`, `_np_slen_g`, `_np_cur_g` set by caller before call

Session 53 partial implementation used globals. Stick with globals for now —
simpler, matches how the patterns are called from the main loop.

### Where to hook into emit.c

In `emit_stmt()` pure-assignment path (line ~710):
```c
if (expr_contains_pattern(s->replacement)) {
    // OLD: E("SnoVal _v%d = ", u); emit_pat(s->replacement); E(";\n");
    // NEW: if subject is E_VAR → emit named pattern function
    if (s->subject && s->subject->kind == E_VAR && s->subject->sval) {
        byrd_emit_named_pattern(s->subject->sval, s->replacement, out);
        // emit: set(_varname, <function-pointer-sentinel>);
    } else {
        E("SnoVal _v%d = ", u); emit_pat(s->replacement); E(";\n");
    }
}
```

### Build verification

After implementing, build with engine_stub.c (NOT engine.c):
```bash
cd /home/claude/SNOBOL4-tiny
CORPUS=/home/claude/SNOBOL4-corpus
INC=$CORPUS/programs/inc
BEAUTY=$CORPUS/programs/beauty/beauty.sno
R=src/runtime
./src/sno2c/sno2c -I $INC $BEAUTY > /tmp/beauty_full.c
gcc -O0 -g -I $R/snobol4 -I $R \
    /tmp/beauty_full.c $R/snobol4/snobol4.c \
    $R/snobol4/snobol4_inc.c \
    $R/engine_stub.c -lgc -lm -o /home/claude/beauty_full_bin
```

If `match_pattern_at` appears as undefined → good, engine.c is gone.
If it links clean → run on beauty.sno, chase crashes (not engine bugs).

---

## CRITICAL: What Next Claude Must NOT Do

- Do NOT write the TOKEN into any file
- Do NOT link engine.c in beauty_full_bin — engine_stub.c ONLY
- Do NOT chase engine.c / *snoParse interpreter bugs — that is the trap
- Do NOT remove fn_seen[] / byrd_fn_scope_reset()
- Do NOT reset byrd_uid_ctr
- Do NOT rewrite emit_byrd.c wholesale — add byrd_emit_named_pattern at the end

---

## Container State (clone fresh each session)

```bash
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
```

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
| 2026-03-16 | Strip sno_/SNO_ prefix, P4-style collision renames, snoc→sno2c (3ea9815) | readability — prefixes too long |
| 2026-03-14 | beauty-runtime → compiled-byrd-boxes-full (HQ 209701b) | engine.c chase = smoke-test trap again |
| 2026-03-14 | TWO TECHNIQUES for *X documented (HQ 8582351) | C target: struct+calloc; ASM: mmap+memcpy+relocate |
| 2026-03-14 | Statement execution model documented (HQ c7ccace) | per-stmt setjmp, glob-seq, non-Gimpel DEFINE |
| 2026-03-14 | artifact: session54.c — md5 matches 53, arch-only session (35bc142) | no code changes |
