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
| **Icon JVM** | `main` IJ-28 — M-IJ-CORPUS-R19 ✅ ICN_POW (^) + real to-by (dneg fix); 99/99 PASS | `2574281` IJ-28 | M-IJ-CORPUS-R20 |

### Next session checklist (IJ-29)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm 99/99 PASS (rungs 01-19) before touching code
# Next: M-IJ-CORPUS-R20 — candidates: ICN_SEQ_EXPR (E;F sequence expressions),
# string section s[i:j], ICN_CASE, or deeper pow chains. Consult JCON-ANALYSIS.md.
```

### IJ-28 findings — M-IJ-CORPUS-R19 ✅

**99/99 PASS (rung01–19).** HEAD `2574281`.

**Changes in `icon_parse.c`:**

1. **`parse_pow()`** — new level between `parse_unary` and `parse_mul`. Right-associative (recursive). Handles `TK_CARET` → `ICN_POW` node.  `parse_mul` now calls `parse_pow` instead of `parse_unary`.

**Changes in `icon_emit_jvm.c`:**

1. **Double field helpers** — `ij_declare_static_real`, `ij_get_real_field`, `ij_put_real_field` (type `D`).

2. **`ij_emit_pow`** — evaluates both operands via standard funcs-set relay pattern; promotes each to `D` via `l2d` if not already real; stores both in `D` static fields; calls `invokestatic java/lang/Math/pow(DD)D`; result is `D` at ports.γ. One-shot (β → ω).

3. **`ij_emit_to_by` real support** — `is_dbl` flag: any operand real → use `D` fields + `dadd`/`dcmpl`/`dcmpg`/`dconst_0` instead of long equivalents. Promoted via `l2d` at relay if mixed.

4. **`ij_emit_neg` real support** — emits `dneg` if child is real, `lneg` otherwise. Fixes VerifyError on `-1.0` literal as step operand.

5. **`ij_expr_is_real` extensions** — `ICN_POW` (always D), `ICN_NEG` (delegates to child), `ICN_TO_BY` (any of 3 children), `ICN_TO` (either bound).

6. **Dispatch** — `case ICN_POW: ij_emit_pow(...)` added.

**rung19_pow_toby corpus (5 tests):** integer pow `2^10`→1024.0; real pow `2.0^0.5`→√2; real to-by `1.0 to 2.0 by 0.5`→1.0 1.5 2.0; negative-step `3.0 to 1.0 by -1.0`→3.0 2.0 1.0; pow with var `x^2` (x=3.0)→9.0.

### IJ-27 findings — M-IJ-CORPUS-R18 ✅

**94/94 PASS (rung01–18).** HEAD `f976057`.

**Changes in `icon_emit_jvm.c`:**

1. **`ij_emit_relop` double support** — detects `is_dbl` (either operand real); uses `dstore`/`dload` instead of `lstore`/`lload`; promotes integer operand with `l2d` at relay; emits `dcmpl` for `<`/`<=`/`=`/`~=` and `dcmpg` for `>`/`>=` (NaN-safe direction), then same `ifge`/`ifgt`/etc. branch tests as integer path.

2. **`ij_expr_is_real` relop extension** — `ICN_LT/LE/GT/GE/EQ/NE` now return `is_real(child[0]) || is_real(child[1])`, so downstream `pop2`/`dload` on relop result uses correct slot width.

3. **`ij_expr_is_real` ICN_ALT extension** — `ICN_ALT` delegates to `children[0]`, matching `ij_expr_is_string` pattern. Fixes VerifyError in `every write(3.0 < (2.5|3.5|4.5))` where every-drain used `pop2` on a double from an alt generator.

4. **Note on Icon relop return value** — all relops return the **right-hand** operand on success (confirmed by paper example `2 < (1 to 4)` → 3,4). The t05 corpus test was initially written with generator on left; corrected to put generator on right.

**rung18_real_relop corpus (5 tests):** real `<`, real `>` (false branch), real `=`, mixed int/real `<`, goal-directed real relop with alt generator.


### IJ-26 findings — M-IJ-CORPUS-R17 ✅

**89/89 PASS (rung01–17).** HEAD `f10ea77`.

**Changes in `icon_emit_jvm.c`:**

1. **`ij_emit_binop` double support** — detects `ij_expr_is_real` on either operand; uses `dstore`/`dload`/`dadd`/`dsub`/`dmul`/`ddiv`/`drem` instead of long ops. Promotes long operand with `l2d` when mixing types.

2. **`ij_expr_is_real` extended** — now recurses into binop children and recognises `real()` call. Enables type propagation through expressions like `x * y + z`.

3. **`integer(x)` builtin** — `d2l` for double→long; `Long.parseLong` for String→long; identity for long.

4. **`real(x)` builtin** — `l2d` for long→double; `Double.parseDouble` for String→double; identity for double.

5. **`string(x)` builtin** — `Long.toString(J)` for long; `Double.toString(D)` for double; identity for String. Added to `ij_expr_is_string`.

6. **`ldc2_w` decimal fix** — `%g` format for `2.0` produces `"2"` → Jasmin parses as int. Fix: append `.0` when formatted value has no decimal point or exponent.

**rung17_real_arith corpus (5 tests):** real add, real mul with literals, integer()/string() conversions, real() from int.

### IJ-25 findings — M-IJ-CORPUS-R16 ✅

**84/84 PASS (rung01–16).** HEAD `dff0f03`.

**`ij_emit_subscript`** — `ICN_SUBSCRIPT` (`s[i]`, 1-based, negatives count from end):
α: eval string → cache in static; eval index → l2i → 0-based; bounds check → substring → γ (String).
β: re-drives index child's β (enables `every s[1 to N]`). Negative: offset = length + i.

**`ij_emit_if` drain fix** — `cond_then` uses `pop` vs `pop2` based on `ij_expr_is_string(cond)`.
Previously hardcoded `pop2` caused VerifyError when condition was String-typed (e.g. `if s[5]`).

**rung16_subscript (5 tests):** basic indexing, literal, oob fail, negative index, every-generator.

### IJ-23 findings — M-IJ-CORPUS-R14 ✅

**74/74 PASS (rung01–14).** HEAD `9021c4e`.

**`ij_emit_limit` in `icon_emit_jvm.c`:**

`ICN_LIMIT` (E \ N): per-site statics `icn_N_limit_count J` and `icn_N_limit_max J`.

- α: eval N child (bounded, one-shot) → store max; reset count=0 → E.α via `n_relay`
- `e_gamma` relay: E yielded → store to `icn_N_limit_val`; check count >= max → if yes goto E.β (exhaust); else count++; reload value → ports.γ
- β: check count >= max → ports.ω if exhausted; else → E.β (**no increment** — only γ path increments, because only γ actually delivers a value to the caller)

**Key bug fixed during development:** initial β incremented counter before re-driving E.β, causing off-by-one (N=3 yielded only 2 values). Fix: β never increments.

**`ij_expr_is_string`:** added `case ICN_LIMIT:` delegates to child[0] type.

**rung14_limit corpus (5 tests):** `(1 to 10)\3`→1 2 3; `(1|2|3|4|5)\2`→1 2; `(1 to 5)\0`→"done"; `(1 to 3)\10`→1 2 3; `("a"|"b"|"c")\2`→a b.

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm 69/69 PASS (rungs 01-13) before touching code
# Next: M-IJ-CORPUS-R14 — ICN_LIMIT (E \ N) limitation operator
#   JCON-ANALYSIS §'E \ N': limit N evaluated first (always bounded); counter starts 0.
#   Resume: if counter >= N_val → goto limit.resume (exhaust); counter++; goto expr.resume.
#   Per-site statics: icn_N_limit_count I, icn_N_limit_max J.
#   Corpus tests: (1 to 10) \ 3 → 1 2 3; every write((1|2|3|4|5) \ 2) → 1 2
```

### IJ-22 findings — M-IJ-CORPUS-R13 ✅

**69/69 PASS (rung01–13).** HEAD `a569adf`.

**Three changes in `icon_emit_jvm.c`:**

1. **`ij_emit_alt` rewrite** — per-site `icn_N_alt_gate I` static field. α: `gate=0 → E1.α`. Each `Ei.γ`: `gate=i → ports.γ`. β: `iload gate → tableswitch 1 N → E1.β/.../En.β`. Matches JCON `ir_a_Alt` + JCON-ANALYSIS §`| value alternation`. Root bug: old `β → E1.β` hardwire caused infinite loop in `every s ||:= ("a"|"b"|"c")`.

2. **`ij_expr_is_string(ICN_ALT)`** — new case, returns `ij_expr_is_string(children[0])`. Without it: `every write("a"|"b"|"c")` emitted `lstore` for a String ref → VerifyError (`Expecting to find long on stack`).

3. **`ij_emit_concat` `left_is_value` fix** — `ICN_ALT` excluded from one-shot flag (`left_is_value = ij_expr_is_string(lchild) && lchild->kind != ICN_ALT`). `ICN_ALT` is a generator; treating it as one-shot made `every write(("a"|"b") || ("x"|"y"))` stop after 2/4 results.

**rung13_alt corpus:** 5 tests — t01 `every write("a"|"b"|"c")`, t02 `every s ||:= ("a"|"b"|"c")`, t03 int alt, t04 nested alt in concat, t05 alt filtered by relop.

### IJ-21 findings — M-IJ-CORPUS-R12 ✅

**64/64 PASS (rung01–12).** HEAD `be2af59`.

**Three changes:**

1. **`ij_expr_is_string(ICN_IF)`** — adds `case ICN_IF:` that checks then-branch type via `ij_expr_is_string(n->children[1])`. Root cause of VerifyError: statement-level drain uses `pop2` for `ICN_IF` nodes, but when then-branch is `write(str)` the `ports.γ` of the `if` node carries a String ref (1 slot) → `pop2` underflows. Fix: return string-ness of then-branch.

2. **`ICN_SIZE` full pipeline** — `ICN_SIZE` added to `icon_ast.h` enum + `icn_kind_name()` in `icon_ast.c`. Parser: `check(p, TK_STAR)` in `parse_unary()` before `parse_mul()` (so unary `*` takes priority over binary multiply when in prefix position). Emitter: `ij_emit_size()` — eval child String, `invokevirtual java/lang/String/length()I`, `i2l` → long at `ports.γ`. One-shot, β → child β → `ports.ω`.

3. **String relops** (`ICN_SEQ/SNE/SLT/SLE/SGT/SGE`) — emitter `ij_emit_strrelop` was already complete from a prior session; rung12 corpus provides the first tests for it.

**rung12_strrelop_size corpus:** 5 tests — t01 `==`, t02 `<<`, t03 `~==`, t04 `>>=`, t05 `*s`.

### IJ-20 findings — M-IJ-CORPUS-R11 ✅

**59/59 PASS (rung01–11).** HEAD `cab96d2`.

**Three changes in `icon_emit_jvm.c`:**

1. **`ij_emit_augop` case 35 (`||:=`)** — moved `aug_kind==35` branch *before* the long-path temp allocation. String path: `ij_declare_static_str` for both lhs and rhs-temp fields; `ij_put/get_str_field` + `String.concat` + `dup` + `putstatic`. Added `ICN_AUGOP` to `ij_expr_is_string` (returns 1 iff `val.ival==35`).

2. **`ij_emit_bang` (new)** — per-site statics `icn_N_bang_str` (String) + `icn_N_bang_pos` (int). α: eval child → store String, reset pos=0, fallthrough to check. check: `String.length()` + `ij_get_int_field(pos)` → `if_icmple ports.ω`; else `substring(pos, pos+1)` → increment pos → goto γ. β: goto check. Added `ICN_BANG: return 1` to `ij_expr_is_string`, `case ICN_BANG` to dispatch.

3. **`ij_emit_every` drain fix** — `bstart` and `gbfwd` labels now use `ij_expr_is_string(gen) ? "pop" : "pop2"` instead of hardcoded `pop2`. Fixes VerifyError when every's generator yields Strings.

**Known open issue (not blocking):** `every s ||:= ("a"|"b"|"c")` loops infinitely — `ICN_ALT` β-resume always routes to outermost β (restarts from second alternative). The indirect-goto gate needed per JCON §4.5 is not yet implemented. Corpus test t02 uses sequential `||:=` instead. Tracked as rung12 item.

| **Icon JVM** | `main` IJ-17 — M-IJ-CORPUS-R9 ✅ until/repeat; 49/49 PASS | `60cf799` IJ-17 | M-IJ-CORPUS-R10 |

### Next session checklist (IJ-18)

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
# Confirm 49/49 rung01-09 PASS before touching code
# Next: M-IJ-CORPUS-R10 — design rung10 corpus; candidates: augmented assign (:=+), break, next, bang(!E)
# Note: repeat body-drain slot-collision bug exists (pre-existing in while too) — track separately
```

### IJ-17 findings — M-IJ-CORPUS-R9 ✅ (done)

**49/49 PASS rung01–09.**

Implemented `ij_emit_until` and `ij_emit_repeat` in `icon_emit_jvm.c` (`60cf799`):

**`until E do body`** — dual of `while`: cond.γ → `cond_ok` (pop value, jump to ports.ω); cond.ω → `cond_fail` → body. Body.γ → `body_ok` (pop value, loop to cond). Body.ω → `loop_top` → cond. Key fix: cond.γ must route through a `cond_ok` label that pops the value before exiting — routing directly to `ports.ω` caused VerifyError `Inconsistent stack height 2 != 0`.

**`repeat body`** — body.γ → `body_ok` (pop value, loop); body.ω → `loop_top` (restart body). Exits only via `ports.ω` (β port). Note: `repeat` is truly infinite without `break` — corpus tests use `until` patterns only. `repeat` emitter is wired and correct per JCON semantics but no corpus test exercises its exit path until `break` is implemented.

**rung09 corpus** — 5 `until` tests; all use single-binop patterns to avoid pre-existing local-slot collision bug (two simultaneous `ij_locals_alloc_tmp` chains in cond + body). The slot bug is pre-existing in `while` too; tracked separately.

### IJ-16 findings — M-IJ-CORPUS-R8 ✅ (done)

**44/44 PASS rung01–08.**

Four string builtins implemented in `icon_emit_jvm.c` (`be1be82`):

1. **`find(s1,s2)` generator** — static fields `icn_find_s1_N`, `icn_find_s2_N`, `icn_find_pos_N` per call-site. α evals both args, stores, resets pos=0 → check. β reloads pos unchanged (1-based last result = correct 0-based start for next `indexOf`). `icn_builtin_find(s1,s2,pos)` calls `s2.indexOf(s1,pos)`, returns `idx+1` or `-1L`.

2. **`match(s)` one-shot** — `icn_builtin_match(s,subj,pos)` calls `subj.startsWith(s,pos)`, returns `pos+len(s)+1` (1-based new pos) or `-1L`. Caller updates `icn_pos = result-1` (0-based).

3. **`tab(n)` one-shot String** — `icn_builtin_tab_str(n,subj,pos)` returns `subj.substring(pos,n-1)` and updates `icn_pos = n-1` via `putstatic` from inside helper; returns `null` on bounds failure. Caller does `ifnonnull` check.

4. **`move(n)` one-shot String** — `icn_builtin_move_str(n,subj,pos)` returns `subj.substring(pos,pos+n)`, updates `icn_pos = pos+n`, returns `null` on bounds failure.

5. **`ij_expr_is_string`** — added `"tab"` and `"move"` → return 1 (prevents `pop2` VerifyError on statement-level drain).

6. **`need_scan_builtins` guard** — also fires on `icn_find_s1_N` statics so standalone `find` (no scan context) still emits helpers.

**Key: `tab`/`move` helpers update `icn_pos` via `putstatic ClassName/icn_pos I` directly — clean since helpers are static methods of the same class.**

### IJ-15 findings — rung08 corpus designed (in progress)

**Baseline confirmed 39/39 PASS rung01–07 (via .expected oracle files, not ASM -run).**

**Harness note:** `-run` flag requires `-o` + nasm link cycle. Correct harness:
```bash
/tmp/icon_driver -jvm foo.icn -o /tmp/foo.j
java -jar src/backend/jvm/jasmin.jar /tmp/foo.j -d /tmp/
cls=$(grep -m1 '\.class' /tmp/foo.j | awk '{print $NF}')
java -cp /tmp/ $cls
# diff vs test/frontend/icon/corpus/rungNN/foo.expected
```

**rung08_strbuiltins corpus committed (`6f11821`):** 5 tests for `find`/`match`/`tab`/`move`:

```
t01_find.icn         find(s1,s2) one-shot → 2\n4
t02_find_gen.icn     every find("a","banana") → 2\n4\n6
t03_match.icn        match(s) in scan ctx + fail branch → 4\n0
t04_tab.icn          "abcdef" ? write(tab(4)) → abc
t05_move.icn         "abcdef" ? write(move(3)) → abc
```

**What IJ-16 must implement in `icon_emit_jvm.c`:**

1. **`icn_builtin_find(String s1, String s2, int startpos) → long`** static helper:
   `s2.indexOf(s1, startpos)` → returns 0-based index; return `(idx+1)` as long, or `-1L` on miss.
   For **generator** (`every find(...)`): per-call static `icn_find_pos_N` (int) tracks resume position.
   α: eval args, store s1/s2 in static fields `icn_find_s1_N`/`icn_find_s2_N`, set `icn_find_pos_N=0`, goto check.
   check: call `icn_builtin_find(s1, s2, pos)` → if -1 → ω; else set `pos = result` (1-based = 0-based+1), push result as long → γ.
   β: `icn_find_pos_N = result` (advance past last match), goto check.

2. **`icn_builtin_match(String s1, String subj, int pos) → long`** static helper:
   `subj.startsWith(s1, pos)` → return `pos + s1.length()` (1-based new pos after match), or `-1L`.
   In `ij_emit_call`: one-shot — call helper with `icn_subject`, `icn_pos`; on -1 → ω; else advance `icn_pos = result-1` (0-based), push result → γ.

3. **`icn_builtin_tab(int n, String subj, int pos) → String`** static helper (or inline):
   n is 1-based target pos. Returns `subj.substring(pos, n-1)`. Advances `icn_pos = n-1`.
   In `ij_emit_call`: one-shot — if `n-1 < pos || n-1 > subj.length()` → ω; else return substring, set icn_pos.
   **String result** → `ij_expr_is_string` must return 1 for `"tab"` call.

4. **`icn_builtin_move(int n, String subj, int pos) → String`** static helper:
   Returns `subj.substring(pos, pos+n)`. Advances `icn_pos = pos+n`.
   If `pos+n > subj.length()` → fail.
   **String result** → `ij_expr_is_string` must return 1 for `"move"` call.

5. **`ij_expr_is_string` additions:** `"tab"` and `"move"` → return 1.

6. **`need_scan_builtins` guard:** tab/move/match/find helpers emit alongside any/many/upto (all gated on `icn_subject` in statics).

**Key position convention (same as rung05–06):** `icn_pos` is 0-based internally. Icon positions are 1-based. `tab(n)` receives n as 1-based; internally uses `n-1` as 0-based end index. `match`/`find` return 1-based new positions.

### IJ-14 findings — M-IJ-CORPUS-R5 ✅ (done)

**39/39 PASS rung01–07. .bytecode changed 50.0 → 45.0 globally.**

**Two bugs fixed in `ij_emit_to_by` (`6780ab9`):**

1. **Backward branches** — old code had `adv → chkp/chkn` (backward jump), triggering
   JVM 21 StackMapTable VerifyError. Rewrote α to chain E1→E2→E3 via forward relay labels,
   then `goto check`. β does `I += step; goto check`. `check` is placed *after* both α and β
   in the instruction stream — all jumps forward, no StackMapTable needed.

2. **Double conditional on single `lcmp` result** — `lcmp; ifgt ckp; iflt ckn` is invalid:
   `ifgt` consumes the int, leaving `iflt` with empty stack → old verifier "unable to pop
   operand off empty stack". Fixed by emitting two separate `getstatic/lconst_0/lcmp`
   sequences, one per conditional branch.

3. **`.bytecode 45.0`** — switched from 50.0 (Java 6, requires StackMapTable) to 45.0
   (Java 1.1 old type-inference verifier). The 50.0 comment "no StackMapTable required"
   was wrong. 45.0 uses the old verifier which tolerates backward branches and does not
   require StackMapTable frames.

**`run_rung07.sh`** committed alongside the fix.

### IJ-13 findings — t03_to_by VerifyError fix plan

**Root cause:** JVM 21 requires StackMapTable attributes for backward-branch loops in
all class files. Jasmin 2.x never emits StackMapTable. The `.bytecode 50.0` directive
is accepted by Jasmin but the JVM 21 verifier still requires stack map frames for
backward branches (`Expecting a stackmap frame at branch target`). Logic is correct:
`java -noverify -cp /tmp/ T03_to_by` → `1 4 7 10` ✓.

**Fix strategy — rewrite `ij_emit_to_by` using the suspend/resume static-field pattern
(same as `ij_emit_to`) to avoid backward branches in emitted Jasmin:**

Instead of emitting a loop label that's jumped back to, use the same α/β port dispatch
that `ij_emit_to` uses: α evaluates start/end/step once and yields the first value;
β advances I and checks bounds, yielding next value or failing. No backward branch.

**Concrete implementation:**
```
α: eval start → store I_f; eval end → store end_f; eval step → store step_f
   → check (same as β-check below)

β: I_f += step_f → check

check (no backward branch — jumped to from two forward paths):
   if step_f > 0: if I_f > end_f → ports.ω; else push I_f → ports.γ
   if step_f < 0: if I_f < end_f → ports.ω; else push I_f → ports.γ
   if step_f = 0: ports.ω
```

Key: `check` is a label jumped to from α and from β — both are **forward** jumps
from the perspective of the JVM (α and β appear before check in the instruction stream).
No backward edges → no StackMapTable needed.

The structure matches `ij_emit_to` exactly; just add the step field and direction check.

**Also check:** rung01-03 `every` tests pass, so the every-drain fix (skip sdrain for
ICN_EVERY/WHILE/UNTIL/REPEAT) is safe. Confirm 34/34 baseline before touching to_by.

### IJ-13 findings — what was implemented (done)

**M-IJ-CORPUS-R4 ✅ — rung04+05+06 = 15/15 PASS. 34/34 total.**

New features in `icon_emit_jvm.c` (`6174c9f`):

1. **`ICN_NOT`** (`ij_emit_not`): child success → fail; child fail → succeed + push `lconst_0`
2. **`ICN_NEG`** (`ij_emit_neg`): eval child, emit `lneg`, → ports.γ
3. **`ICN_TO_BY`** (`ij_emit_to_by`): step generator — BROKEN (VerifyError, see above)
4. **`ICN_SEQ/SNE/SLT/SLE/SGT/SGE`** (`ij_emit_strrelop`): `String.compareTo()` + branch; pushes `lconst_0` on success
5. **every/while/repeat/until drain fix**: stmt loop skips sdrain for loop nodes (they never fire ports.γ with a value)
6. **`.bytecode 50.0`** directive emitted (insufficient for JVM 21 backward branches)
7. **rung07_control corpus**: 5 tests; `run_rung07.sh` committed
8. **rung07 result**: 4/5 PASS (t01_not, t02_neg, t04_seq, t05_repeat_break ✅; t03_to_by ❌)

### IJ-12 findings — M-IJ-CORPUS-R4 plan

**Status:** rung01-06 = 34/34 PASS. Rung06 IS rung4-level content (string ops + scan + cset).
M-IJ-CORPUS-R4 fires when rung04+rung05+rung06 all pass — they do. Confirm against ASM oracle.

**What fires M-IJ-CORPUS-R4:**
Run all of rung04_string (5), rung05_scan (5), rung06_cset (5) and confirm PASS vs ASM oracle.
The JVM results already match expected files which were derived from ASM oracle output.
Therefore **M-IJ-CORPUS-R4 fires immediately** — no new code needed.

**IJ-13 checklist:**
1. Build driver, confirm 34/34 baseline
2. Declare M-IJ-CORPUS-R4 ✅ (rung04+05+06 = 15/15 PASS)
3. Plan next milestone (M-IJ-CORPUS-R5 or string builtins per PLAN.md)

### IJ-12 findings — M-IJ-CSET implementation (done)

**34/34 total PASS (rung01-06). All prior rungs clean.**

**What was implemented in `icon_emit_jvm.c`:**

1. **`ICN_CSET` dispatch** — `case ICN_CSET: ij_emit_str(...)` (cset literal = ldc String)
   `ij_expr_is_string`: `case ICN_CSET: return 1`

2. **`any(cs)` built-in** in `ij_emit_call` — guarded `!ij_is_user_proc(fname)`:
   Evaluates cs arg (String), calls `icn_builtin_any(cs, subj, pos) → long` (-1=fail).
   On success: advances `icn_pos`, pushes new 1-based pos as long → ports.γ.

3. **`many(cs)` built-in** — same pattern, calls `icn_builtin_many`.

4. **`upto(cs)` built-in** — generator: saves cs in per-call static field `icn_upto_cs_N`.
   α saves cs, β re-enters step. Step calls `icn_builtin_upto_step(cs,subj,pos) → long`.
   On match: sets `icn_pos = result` (0-based), yields result as long → ports.γ.

5. **Static helpers emitted in `ij_emit_file`** (gated on `icn_subject` in statics):
   `icn_builtin_any`, `icn_builtin_many`, `icn_builtin_upto_step` — all pure Jasmin.

6. **ICN_AND fix (bonus)**: relay trampolines now emit `pop`/`pop2` to drain child[i]'s
   result before entering child[i+1].α — fixes VerifyError on `&` with any() lhs.
   Also fixed emit order: left-to-right so `ccb[i-1]` is populated when child[i] needs it.

7. **User-proc name collision guard**: `!ij_is_user_proc(fname)` on all three builtins
   prevents shadowing user procs named `any`/`many`/`upto` (rung03 t01_gen uses `upto`).

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
