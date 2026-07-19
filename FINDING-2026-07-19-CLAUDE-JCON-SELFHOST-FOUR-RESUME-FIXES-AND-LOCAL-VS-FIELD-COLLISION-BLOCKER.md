# FINDING 2026-07-19 — JCON self-host: four resume/value fixes land (interfacegen now BYTE-IDENTICAL to oracle); ast2ir blocker root-caused to LOCAL-VS-RECORD-FIELD name collision

Session (Lon: "get JCON compiler self-hosting under SCRIP, then benchmark vs Icon + JCON"). Base SCRIP `c555d01b`
(ahead of the prior finding's `6f56ca41` — parallel-session push). All work MEASURED against a same-sandbox
baseline (stash / rebuild / rerun / diff): unmodified HEAD = **Icon 241/20/32**, fail list byte-identical.
All four fixes below are VERIFIED zero-regression against that baseline (full `test_icon_all_rungs.sh`).

## Oracles / benchmark targets BUILT this session (all three live)
- **Canonical Icon** — `icon-master` configured `linux`, `make All` → `bin/icont` + `bin/iconx` (v9.5.25a). Oracle + perf target #1.
- **Canonical JCON** — `jcon-master` `make build` (needs `icont` on PATH + a real JDK; installed `default-jdk-headless` for `javac`) → `bin/jtran` + `bin/jlink` + `bin/jcon.zip`. Verified end-to-end (`jcont -o hello hello.icn` runs on the JVM). Oracle + perf target #2.
- **SCRIP** — perf target #3 (the self-host goal).

## THE BLOCKER, ROOT-CAUSED (ast2ir stage) — LOCAL VARIABLE SHADOWED BY A RECORD-FIELD ACCESSOR OF THE SAME NAME
The prior cursor's stage-5 blocker (`Expecting ;` / proc-body first-set) was a RED HERRING already cleared by
the parser fixes; the generated `do_ops.icn` hypothesis was ALSO disproven (SCRIP's `do_ops.icn` is
functionally byte-identical to icont's on a 33-operator battery — different table iteration ORDER, same
decision tree). The real wall is at **ast2ir**: `Run-time error 500, offending value: function a`.

Traced (probe ladder, all confirmed): `@parse` delivers a correct `a_ProcDecl`; `ir_a_ProcBody` sees
`p.nexprList[1] = function a` (should be the `write(...)` `a_Call`). Walked the parser: `parse_expr11a`
returns a correct `a_Call`, but `parse_expr1a` returns `function a`. The corruptor is **`parse_expr3`**
(parse.icn ~438): `local ret, a; ret := parse_expr4(); while ...lex_BAR... { /a := a_Alt(...) ...};
ret := \a; return ret`. Probe: **immediately after `ret := parse_expr4()`, the local `a` is already
`type=function img=function a`, NOT `&null`.** So `\a` (non-null filter) SUCCEEDS and `ret := \a` overwrites
the real `a_Call` with the function value.

MINIMAL REPRO (`/tmp/fieldcol.icn`, confirmed):
```
record u_cset(a)       # <-- a record ANYWHERE in the program with a field named `a`
record rec(x)
procedure g()
  local ret, a         # <-- local named `a`
  ret := someRecord()
  # here: type(a) == "function", image(a) == "function a"   (SCRIP)  vs  &null (icont)
  ret := \a            # \a wrongly succeeds -> ret clobbered
```
`gen_ucode.icn` declares `record u_cset(a)`, `record u_real(a)`, `record u_str(n,a)` — three record FIELDS
named `a`. In Icon a record field name becomes a global field-accessor. SCRIP resolves the BARE local `a` to
that global accessor instead of the local frame slot. **Renaming parse_expr3's local `a`→`zz_alt` makes
ast2ir SUCCEED and emit `ir_Function`** (proven) — but the frontend must not require renaming; local scope
must shadow a field-accessor global.

### Where the fix belongs (localized, not yet written)
Emitter `IR_VAR` dispatch (emit.cpp ~782): a var emits GLOBAL when `is_global(name) && !graph_has_local(g_emit_cfg,name)`.
`graph_has_local` (scrip_ir.c:237) checks the graph's `pnames`/`lnames`. Lnames are collected in lower_icon.c
~1315 from `TT_LOCAL` stmts. For the collision case `is_global("a")` is TRUE (field accessor) and the local
read still resolves global — so either (a) the local `a` is NOT landing in this graph's `lnames`, or (b) the
slot pass (`zeta_storage.c:327` uses the SAME `is_global && !graph_has_local` gate) skips granting `a` a slot,
so `bb_var()` reads garbage. NEXT SESSION: dump `graph_has_local(g,"a")` + the granted vslot for parse_expr3's
graph in the merged compile; the gate that lets a field-accessor win over an in-scope local is the land mine.
RELATED SUB-BUG (very likely the same fault, independently confirmed): **`type()`/`image()` report
`"function"`/`function <name>` for record CONSTRUCTORS and builtins where canonical Icon reports `"procedure"`
/ `record constructor <name>`** (`type(a_Foo)`=="function" in SCRIP, "procedure" in icont). This is why the
corrupted value reads as `function a`. by_name_dispatch.c type() DT_E branch (~4157) defaults "function" and
only upgrades named user procs; record-constructor and builtin values should be "procedure".

## FOUR FIXES LANDED (uncommitted in tree; files: src/lower/lower_icon.c, src/runtime/by_name_dispatch.c)

### FIX 1 — generator in a NON-LAST call argument (lower_icon.c `lower_call`)
`every f(!L, k)` (generator arg followed by a constant) produced ONE value, not the full iteration. The
call-failure/`cx->beta` resume wiring keyed on the LAST POSITIONAL arg's resumability (`is_resumable(la)`)
instead of whether ANY arg is resumable. Fix: gate on `chain_live = (aω != ω)` — the unconditional per-arg
`aω` threading (L126) already routes each arg's failure to the previous arg's β, so if any arg carried a
resume, `aω` points into the generator chain. Robust to `is_resumable`'s TT_LIMIT/TT_REPALT gaps (they reach
via the chain, not via `la`). NOTE: a first attempt that made the `aω` threading itself conditional caused 14
regressions (repalt/limit) precisely because `is_resumable` omits TT_LIMIT/TT_REPALT — the shipped version
keeps the unconditional threading and only changes the final gate. Repro `/tmp/argpos.icn`.

### FIX 2 — null-filter over a generator `\!gen` (lower_icon.c unop path)
`\!keys` stopped at the first null instead of filtering it and continuing. The `IR_UNOP_TEST` (`\`) failure
edge went to the outer ω instead of re-pumping the operand generator. Fix: capture the operand β and, for
`IR_UNOP_TEST`, `ω_to(op, uβ); cx->beta = uβ` (mirrors the binop path's opfail handling). Repro `/tmp/filt.icn`.

### FIX 3 — `image()` of a string that matches a builtin name (by_name_dispatch.c)
`image("pos")` returned `function pos` (spurious `proc_as_value` upgrade on a genuine DT_S string). A string
images as a quoted string by TYPE, always. Removed the upgrade in both the 1-arg and 2-arg `image` forms;
`image(copy)` on a bare function still works (separate DT_E path). Repro `/tmp/img.icn`.

### FIX 4 — trailing comma / empty slot in a list literal (lower_icon.c, new TT_NUL arm)
`[a,b,c,]` silently killed the program instead of yielding a 4-elem list with a trailing `&null` (canonical
Icon `*[a,b,c,]`==4). Parser mints TT_NUL (icon_parse.c L157/161/162) but the lowerer had no TT_NUL case → it
fell to the default `IR_SUCCEED` and pushed a value-less operand into `IR_MAKE_LIST`, corrupting construction.
Added `TT_NUL -> IR_VAR "&null"`. Repro `/tmp/tc.icn`.

## RESULT — self-host pipeline progress
- `interfacegen.icn` run under SCRIP now produces **BYTE-IDENTICAL** output to the icont-built oracle
  (415 lines, empty diff) — was 188 lines (truncated) before the fixes. `do_ops.icn` functionally equivalent.
- Build recipe (works): copy 18 modules from `corpus/programs/icon/jcon-compiler/`; generate `do_ops.icn`
  (`scrip --run oplexgen.icn`) and `interface.icn` (`scrip --run interfacegen.icn`); **semicolonize both**
  (`tools/semicolonize_icon.py` — freshly generated files lack SCRIP's required `;`); compile all 17 modules
  in one `scrip --run <mods> -- <pipeline args>` (SCRIP does native multi-module AST merge — no m4 needed);
  pipeline stages go AFTER `--`. Flag: `SCRIP_BETA_ELIDE_OFF=1` (else 1 unresolved `xchain*_β` label at emit).
- 17-module program: parses, lowers, LINKS, RUNS. Pipeline `preproc hello_t.icn : yylex : parse` all ✓
  (preproc emits correct `#line`+source; yylex 12 tokens; parse → `a_ProcDecl`). **`ast2ir` blocked ONLY by
  the local-vs-field collision above.** Workdir `/home/claude/jt`.

## NEXT SESSION
1. Fix the local-vs-field-accessor collision (localize: graph_has_local / slot-grant gate for a name that is
   both an in-scope local AND a record-field-accessor). Likely also fix type()/image() for constructors+builtins.
2. Rebuild, confirm ast2ir emits `ir_Function` on hello, advance pipeline: ast2ir → bc_File → .u1/.u2.
3. Byte-compare SCRIP-jtran ucode/bytecode vs icont-jtran (strict self-host bar).
4. Three-way benchmark: iconx vs JCON/JVM vs SCRIP-jtran (Makefile `bmark` compiles irgen.icn — natural load).

## Board (this sandbox)
Icon 241/20/32, fail list byte-identical to unmodified HEAD (verified after each of the 4 fixes). All four
fixes confirmed present in `git diff` (2 files, +16/-14). NOTHING committed or pushed — needs `perform hand
off` + credential. SCRIP working tree: `src/lower/lower_icon.c`, `src/runtime/by_name_dispatch.c`.
Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
