# HANDOFF — 11th run (Claude Sonnet 4.6, 2026-06-07)

## Repo state
- Branch: `main`, HEAD SCRIP: `4f2ae74`, corpus: `794a8c58`
- Build: CLEAN (`make scrip` → `Built: scrip`)
- Gate: **m2 86/0 XFAIL=1** (recursion.pas known XFAIL)
- Session open:  76/1 (read2 fail, 76 pass)
- Session close: 86/0 (+10 pass, +5 probes committed)

## What landed this session

### Fix: `read2` EOF char (pre-existing bug)
`__pas_read_c` in `by_name_dispatch.c`: EOF returns `chr(26)` not `chr(0)` — pint semantics.
Gate: 76/1 → 77/0.

### PB-24: 2D comma-syntax arrays — LANDED
`pascal.y` changes:
- `g_pas_arrays` struct gains `long long ncols` field (−1 = 1D). New `pas_array_add2d(name, high, ncols)` and `pas_array_ncols(name)` lookup.
- New `g_pas_pend_arr_ncols` global tracks pending column count.
- New grammar arm: `ARRAYSY LBRACK simple_type COMMA simple_type RBRACK OFSY type` — flat high = `(row_high+1)*(col_high+1)-1`; stores `ncols = col_high+1`.
- `var_decl`: dispatches `pas_array_add2d` when `g_pas_pend_arr_ncols >= 0`.
- `type_decl`: passes `ndim2=1, ncols` to `pas_arrtype_add` for named 2D types.
- `selector LBRACK expression_list RBRACK`: when `count==2` and var has known ncols, **desugars `a[i,j]` → `TT_IDX(a, i*ncols+j)` at parse time** — zero changes to `lower_pascal.c`.
- Probes: `arr2d`, `arr2d2`, `arr2d3`, `matmul` (all oracle-verified).

### PB-27: record value params — LANDED
`pascal.y` changes:
- New `pas_recvar_add_from_type(vname, typename)` — registers recvar directly from named record type without going through pend.
- `id_list COLON IDENT` value param rule extended: if IDENT is a known record type → `pas_recvar_add_from_type` + `pas_array_add(name, nf-1)` so `q.x` resolves to `TT_IDX(q,0)` at parse time (not `TT_FIELD` → UNHANDLED).
- Also handles array-typed value params: if IDENT is known 1D/2D array type → `pas_array_add`/`pas_array_add2d` so `a[i]`/`a[i,j]` desugar correctly inside callee.
- Probes: `recparam`, `recparam2`, `recparam3`, `forward1`, `markrel` (all oracle-verified).

## Open bug: 2D named-type array VALUE PARAM (partially investigated)

**Symptom:** A procedure receiving a `type mat2 = array[0..1,0..1]` value param, where the procedure ALSO has local variables declared, produces wrong output.

**Reproduced:**
```pascal
type mat2 = array[0..1, 0..1] of integer;
var m: mat2;
procedure show(a: mat2);   { ← value param of named 2D type }
var i: integer;            { ← any local triggers the bug }
begin writeln(a[0,0]) end;
begin m[0,0]:=11; m[0,1]:=22; show(m) end.
```
Oracle: `11`. m2 output: `22` (index off by +1).

**Without locals** (no `var` in show): works correctly. `debug3.pas` passes.

**Root cause narrowed to:** The interaction between `g_pas_arrays` containing the formal param `'a'` (added in `PB-27` param rule) and the frame Scope slot ordering when locals are present. Hypotheses:
1. The program-level `mk_array_fill` init loop emits `a := mk_array_fill(3)` for the formal param (wrong — it's not a global). This runs BEFORE `show(m)` in main. BUT for flat (non-nested) procs, IR_VAR 'a' checks FRAME first, so NV['a'] shouldn't matter if FRAME is correct.
2. The Scope slot ordering when locals co-exist with params shifts the frame lookup. Specifically: `e[0]='a'` (param), `e[1]='i'` (local) — but `g_pas_arrays` may register 'a' in a way that makes `arr_get` receive the wrong argument.
3. The `pas_array_ncols('a')` lookup inside show's body returns the right ncols=2 (confirmed for the no-locals case). When a local is declared, something shifts.

**Investigation approach for next session:**
- Check whether `g_pas_arrays` needs to distinguish **formal params** from **globals** so the program init loop skips them. The cleanest fix: a `is_param` flag, or simply: don't add formal params to `g_pas_arrays` — instead maintain a SEPARATE `g_pas_param_arrays` table that the selector rule also checks.
- Alternatively: verify the frame env[slot] binding is actually receiving m's value not NV['a']. Add a single-char writeln probe to confirm what the frame contains.

**The 2D named array param with NO locals works** — only fails when locals are present. That's the exact boundary for the next session to dig into.

## Next session setup
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
```

Gate (run every session before any commit):
```bash
cat > /tmp/pascal_gate.sh << 'GATE'
#!/bin/bash
PASDIR=/home/claude/corpus/programs/pascal
SCRIP=/home/claude/SCRIP/scrip
cd "$PASDIR"
PASS=0; FAIL=0; XFAIL=0; FAILS=""
for f in *.pas; do
    base="${f%.pas}"
    case "$base" in pcom|pint|ppp) continue ;; esac
    if [ "$base" = "recursion" ]; then XFAIL=$((XFAIL+1)); continue; fi
    ref="${base}.ref"
    if [ ! -f "$ref" ]; then echo "NOREF $base"; FAIL=$((FAIL+1)); continue; fi
    got=$(timeout 8s "$SCRIP" --interp "$f" < /dev/null 2>/dev/null)
    exp=$(cat "$ref")
    if [ "$got" = "$exp" ]; then
        PASS=$((PASS+1))
    else
        FAIL=$((FAIL+1))
        FAILS="$FAILS FAIL:$base"
    fi
done
echo "m2 PASS=$PASS FAIL=$FAIL XFAIL=$XFAIL"
for x in $FAILS; do echo "  $x"; done
GATE
bash /tmp/pascal_gate.sh   # must be PASS=86 FAIL=0 XFAIL=1
```

**Probe generation (if .ref files missing):**
```bash
( cd /home/claude/corpus/programs/pascal && for f in *.pas; do
    base="${f%.pas}"
    case "$base" in pcom|pint|ppp|recursion) continue ;; esac
    ./pcom < "$f" > /dev/null 2>&1 && cp prr prd && printf '%s' "$(timeout 8s ./pint < /dev/null 2>/dev/null)" > "${base}.ref"
  done )
```

## Landmines (see GOAL-PASCAL-BB.md for full list)
- `rm -f scrip` before `make scrip` (no prerequisites; edits silently don't take)
- Pascal regen ONLY: `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (never full regen script)
- `touch` templates before `make scrip` after any template edit
- `fpc` needs `apt-get update` first
