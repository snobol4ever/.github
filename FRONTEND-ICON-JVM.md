# FRONTEND-ICON-JVM.md — Tiny-ICON → JVM Backend (L3)

Icon → JVM backend emitter. The Icon **frontend** (lex → parse → AST) is shared
and lives in `src/frontend/icon/`; this sprint is about `icon_emit_jvm.c` — the
**JVM backend emitter** that consumes the `IcnNode*` AST and emits Jasmin `.j` files,
assembled by `jasmin.jar` into `.class` files. Despite the file's location under
`src/frontend/icon/`, the work here is backend emission, not parsing.

**Session trigger phrase:** `"I'm working on Icon JVM"` — also triggered by `"playing with ICON frontend ... with JVM backend"` or any phrasing that combines Icon with JVM.
**Session prefix:** `IJ` (e.g. IJ-1, IJ-2, IJ-3)
**Driver flag:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (the x64 ASM backend, rungs 1–2 known good)

*Session state → this file §NOW. Backend reference → BACKEND-JVM.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-11 — M-IJ-SCAN ✅; rung06_cset corpus committed; ij_emit_cset/any/many/upto open | `c166bfe` IJ-11 | M-IJ-CSET |

### Next session checklist (IJ-12)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Read FRONTEND-ICON-JVM.md §NOW
# Confirm rung01-05 29/29 still PASS before touching code
# Implement M-IJ-CSET per §IJ-11 findings below
```

### IJ-11 findings — M-IJ-CSET implementation plan

**Corpus:** `test/frontend/icon/corpus/rung06_cset/` — 5 tests committed `c166bfe`.

```
t01_any_basic.icn     "apple" ? write(any('aeiou'))          → 2
t02_any_fail.icn      "xyz" ? any('aeiou') fails, write(0)   → 0
t03_many_basic.icn    "aaabcd" ? write(many('abc'))           → 6
t04_upto_basic.icn    every ("hello world" ? write(upto(' ')))→ 6
t05_cset_var.icn      vowels:='aeiou'; "icon"?write(any(v))  → 2
```

**Position convention:** `icn_pos` is 0-based (reset to 0 on scan entry). Icon positions are 1-based.
`any`/`many`/`upto` return the new 1-based position *after* the match — i.e. `icn_pos + 2` after consuming one char, etc.
`write()` prints this as a long integer.

**What to implement in `icon_emit_jvm.c`:**

**1. `ICN_CSET` in dispatch and helpers** — cset literal is just a typed string:
- `ij_emit_str` already handles `ICN_STR`; add `case ICN_CSET:` → call same `ij_emit_str` (cset chars as ldc String)
- `ij_expr_is_string`: add `case ICN_CSET: return 1;`

**2. `any(cs)` in `ij_emit_call`** — single char match, one-shot (no resume):
```
; cs String on stack from arg eval → astore scratch_cs
; get icn_subject.length() → if icn_pos >= length → FAIL
; icn_subject.charAt(icn_pos) → (char)
; scratch_cs.indexOf(ch) >= 0?  → if < 0 → FAIL
; push (icn_pos + 2) as long   [new 1-based pos]
; iinc icn_pos 1               [advance icn_pos]  -- via putstatic
; → ports.γ
```
Use `java/lang/String/indexOf(I)I` with the char as int.
Use `java/lang/String/length()I` for bounds check.
Use `java/lang/String/charAt(I)C` to get the char.

**3. `many(cs)` in `ij_emit_call`** — span chars while in cset:
```
; astore scratch_cs
; if icn_pos >= subject.length() → FAIL
; if scratch_cs.indexOf(subject.charAt(icn_pos)) < 0 → FAIL (must match at least one)
; loop: while icn_pos < length && cs.indexOf(charAt(icn_pos)) >= 0: icn_pos++
; push (icn_pos + 1) as long   [new 1-based pos]
; → ports.γ
```
Implement loop with JVM branch instructions (goto/ifeq/etc).

**4. `upto(cs)` in `ij_emit_call`** — generator, yields each pos where char in cset:
Use the suspend/resume pattern via per-call static field `icn_upto_pos_N`:
```
α:  astore scratch_cs; goto check_N
check_N:
    if icn_pos >= length → FAIL
    cs.indexOf(subject.charAt(icn_pos)) < 0? → icn_pos++; goto check_N
    ; found match at icn_pos
    push (icn_pos + 1) as long
    iinc icn_pos 1
    → ports.γ
β:  goto check_N   ; simply re-enter the scan loop from current icn_pos
```
Note: unlike suspend/resume for procedures, `upto` resumes by re-entering the scan
loop which naturally reads the updated `icn_pos`. No tableswitch needed — just a
direct `goto check_N` from β.

**5. `run_rung06.sh`** — mirror `run_rung05.sh`, 5 tests.

**6. Cset variable assignment** — t05 uses `vowels := 'aeiou'`. Since `ICN_CSET` is
a String, the pre-pass type inference (`ij_expr_is_string`) will see the RHS as a
String and declare the var's static field as type 'A'. `ij_emit_assign` already handles
String-typed RHS. Should work automatically once `ICN_CSET` returns 1 from `ij_expr_is_string`.

**Key concern:** `any`/`many`/`upto` need the cset arg as a String on the JVM stack.
The arg is emitted via `ij_emit_expr` — for `ICN_CSET` or `ICN_STR` that leaves a
String ref. For `ICN_VAR` pointing to a String-typed var, `ij_emit_var` leaves a
String ref. Both cases work cleanly.

**`write(any(cs))`** — `any` returns a long (the new position). So `ij_expr_is_string`
for `ICN_CALL("any",...)` must return 0 (long). Same for `many` and `upto`.
`write()` will use `println(J)` path. Correct.

### IJ-11 findings — M-IJ-SCAN implementation (done)

**All 5 rung05_scan tests PASS. rung01-04 24/24 still clean. Total: 29/29.**

**What was implemented in `icon_emit_jvm.c`:**

1. **`ij_emit_scan(n, ports, oα, oβ)`** — four-port Byrd-box wiring:
   - Per-scan static save slots `icn_scan_oldsubj_N` (String) and `icn_scan_oldpos_N` (I)
   - Global fields `icn_subject` (String) and `icn_pos` (I) declared via `ij_declare_static_str/int`
   - `<clinit>` emitted (gated on `icn_subject` being in statics) initializing `icn_subject=""`, `icn_pos=0`
   - α → expr.α; expr.γ: save old subject/pos, install new subject (String from stack), reset pos=0, → body.α
   - expr.ω → ports.ω; body.γ: restore → ports.γ; body.ω: restore → expr.β (one-shot → ports.ω); β: restore → body.β

2. **`ij_emit_var` `&subject` branch** — checked before regular slot/global lookup:
   `getstatic icn_subject` → ports.γ

3. **`ij_expr_is_string`** — added `ICN_SCAN` (delegates to body child) and `ICN_VAR/"&subject"` cases.
   Critical: without these, statement-level drain emits `pop2` instead of `pop` for String-typed scan results → VerifyError.

4. **`run_rung05.sh`** committed alongside code.

**Key bug caught during IJ-11:** `ij_expr_is_string` missing ICN_SCAN caused `pop2` on 1-slot String result → `Unable to pop operand off an empty stack` VerifyError on all 5 tests. Fix: add ICN_SCAN and &subject to the type-inference function.

### IJ-10 findings — M-IJ-SCAN implementation plan

**Corpus:** `test/frontend/icon/corpus/rung05_scan/` — 5 tests committed `992a3a5`.

**What to implement in `icon_emit_jvm.c`:**

1. **Two global static fields** — declare once in `ij_emit_file` prologue:
   - `icn_subject` (`Ljava/lang/String;`) — current scan subject, init `""`
   - `icn_pos` (`I`) — current scan position, init `0`

2. **`&subject` keyword** — in `ij_emit_var`, if `n->val.sval` is `"&subject"`:
   `getstatic icn_subject` → String on stack → `ports.γ`. No push needed (String ref).

3. **`ij_emit_scan(n, ports, oα, oβ)`** — four-port wiring per JCON `ir_a_Scan` / JCON-ANALYSIS §`E ? body`:
   ```
   Allocate static fields: old_subject_N, old_pos_N  (save/restore slots)

   α:
     → expr.α

   expr.γ (new subject on stack as String ref):
     putstatic old_subject_N ← getstatic icn_subject  (save old)
     putstatic old_pos_N     ← getstatic icn_pos       (save old)
     putstatic icn_subject   ← new subject String
     putstatic icn_pos       ← iconst_0                (reset pos)
     → body.α

   expr.ω:
     → ports.ω   (scan expr failed → whole scan fails)

   body.γ:
     getstatic old_subject_N → putstatic icn_subject   (restore)
     getstatic old_pos_N     → putstatic icn_pos
     → ports.γ

   body.ω:
     getstatic old_subject_N → putstatic icn_subject   (restore)
     getstatic old_pos_N     → putstatic icn_pos
     → expr.β   (retry expr — expr is one-shot string, so this → ports.ω)

   β:
     getstatic old_subject_N → putstatic icn_subject
     getstatic old_pos_N     → putstatic icn_pos
     → body.β
   ```

4. **`case ICN_SCAN:` in dispatch** — `ij_emit_scan(n,ports,oα,oβ); break;`

5. **Write `run_rung05.sh`** mirroring `run_rung03.sh` — 5 tests, JVM oracle.

**Note on expr convention:** `ICN_STR` / `ICN_CONCAT` leave String ref on JVM stack at `expr.γ`. `ICN_VAR` (string-typed) also leaves String ref via `getstatic`. So at `expr.γ` we always have a String ref on stack — `putstatic icn_subject` consumes it cleanly.

### IJ-9 findings — suspend/resume architecture fix

**Root cause of IJ-7 no-output:** Zero-init loop (needed for JVM verifier) ran *after* param
load, clobbering `n=4→0`. Fixed by switching named locals/params to per-proc static fields
(`icn_pv_PROCNAME_VARNAME`) — static fields survive the `return`-based yield/resume cycle.

**Second bug (t05):** `icn_suspend_id` not cleared at `proc_done`, so second call to same
generator jumped to beta instead of fresh. Fixed: clear both `icn_suspended` and
`icn_suspend_id` at `proc_done`.

**Pre-existing failure:** t06_paper_expr — VerifyError "Unable to pop operand off an empty
stack" in `icn_main`. Not related to IJ-9 changes (confirmed by git stash test). Open issue.

### IJ-7 findings — (resolved in IJ-9, kept for reference)

**Confirmed:** bp.ω fix from IJ-6 is already applied at line 521 of `icon_emit_jvm.c`:
```c
strncpy(bp.ω, ports.γ, 63);  /* body fail: empty stack → jump direct, no pop */
```

**Build + rung03 x64 ASM:** confirmed 5/5 PASS (ASM backend remains clean).

**JVM t01_gen generates class but produces no output.**

**Diagnosis:** Jasmin for `icn_upto` reveals the while-loop condition check wiring:
```jasmin
icn_1_check:
    lload 4          ; left operand (i)
    lload 6          ; right operand (n)
    lcmp
    ifgt icn_2_β     ; i > n → fail
    lload 6          ; push n (WHY? this is the "passed value" pushed for condok drain)
    goto icn_0_condok
icn_0_condok:
    pop2             ; drains the pushed n
```
The `lload 6; goto icn_0_condok; icn_0_condok: pop2` pattern pushes n then immediately pops it. This is the x64 pattern translated literally: x64 pushes the "passed" right operand for the while condition's success port, and WHILE's `condok` discards it. In JVM the pattern is structurally correct — `pop2` consumes the long pushed by `lload 6`.

**The real issue:** `icn_14_docall` → `invokestatic icn_upto()V`. After upto **suspends** (`icn_upto_sret: return`), `icn_failed=0`, `icn_suspended=1`, `icn_retval=1`. Back in main:
```jasmin
icn_14_docall:
    invokestatic T01_gen/icn_upto()V
    getstatic T01_gen/icn_failed B
    ifne icn_14_after_call        ; if failed → done
    getstatic T01_gen/icn_retval J
    goto icn_13_call              ; → write → genb → 13β → 14β
icn_14_after_call:
    goto icn_main_done
```
This looks correct: `icn_failed=0` so `ifne` not taken, retval loaded, goes to write. **But `icn_14_after_call` is reached from the very first `ifne` check.** Hypothesis: `icn_upto` is setting `icn_failed=1` before returning — i.e., it's hitting `icn_upto_done` instead of `icn_upto_sret`.

**Most likely root cause:** The `while i <= n` condition check fires on first entry. `icn_1_check` loads `lload 4` (lc_slot for i) and `lload 6` (rc_slot for n). On first entry these slots hold **0** (zeroed in preamble), not the actual values. The `lconst_0; lstore` preamble zeroes all slots including the binop temp slots used by the LE compare. So `i=0`, `n=0` on first compare → `lcmp` = 0, `ifgt` not taken, proceeds — OK. But `n` (from param `icn_arg_0`) is loaded into `lstore 0` at proc entry, and `i := 1` stores to `lstore 2`. The LE compare uses `lc_slot=4` (i's relay) and `rc_slot=6` (n's relay) which are only populated when the left/right relay labels are hit. **On first entry to `icn_1_check` via `icn_1_α → icn_3_α → lload 2 → icn_1_lrelay → lstore 4` then `icn_1_lstore → icn_2_α → lload 0 → icn_1_rrelay → lstore 6 → icn_1_check`** — so both relays ARE populated before `icn_1_check` fires. This is correct.

**Remaining suspect:** After `icn_0_condok: pop2`, we go to `icn_4_yield`. `icn_5_α: lload 2; goto icn_4_yield`. `icn_4_yield: putstatic icn_retval J` — this correctly stores i=1. Then sets `icn_failed=0`, `icn_suspended=1`, `icn_suspend_id=1`, `goto icn_upto_sret`. `icn_upto_sret: return`. This ALL looks correct.

---

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | **TO CREATE** — this sprint's deliverable |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box logic oracle (49KB) |
| `src/frontend/icon/icon_driver.c` | Add `-jvm` flag → `ij_emit_file()` branch |
| `src/backend/jvm/emit_byrd_jvm.c` | JVM output format oracle — copy helpers verbatim |
| `src/backend/jvm/jasmin.jar` | Assembler — `java -jar jasmin.jar foo.j -d outdir/` |
| `test/frontend/icon/corpus/` | Same `.icn` tests; oracle = ASM backend output |

---

## Oracle Comparison Strategy

```bash
# ASM oracle
icon_driver foo.icn -o /tmp/foo.asm -run   # produces output via nasm+ld

# JVM candidate
icon_driver -jvm foo.icn -o /tmp/foo.j
java -jar src/backend/jvm/jasmin.jar /tmp/foo.j -d /tmp/
java -cp /tmp/ FooClass

diff <(icon_driver foo.icn -o /tmp/foo.asm -run 2>/dev/null) \
     <(java -cp /tmp/ FooClass 2>/dev/null)
```

Both must produce identical output for each milestone to fire.

---

## Session Bootstrap (every IJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read FRONTEND-ICON-JVM.md §NOW → start at first ❌
```

---

*FRONTEND-ICON-JVM.md = L3. ~3KB sprint content max per active section.*
*Completed milestones → MILESTONE_ARCHIVE.md on session end.*
