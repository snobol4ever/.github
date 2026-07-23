# FINDING 2026-07-23 — PAS-PINT-7: aggregate-local alias under recursion (root cause found, fix pending)

**Outcome:** Root cause of PAS-PINT-7 (`a[k]:=99` compiled to scalar `sroi` with zero `ixa` by SCRIP-pcom)
is fully bracketed and reproduced in a 9-line standalone repro. **No code changed this session.**
Gates: M3 149/0 · M4 149/0 (unchanged). Next session: implement the fix in `lower_pascal.c`.

---

## Symptom recap

`t_arr2.pas` (`var a:array[1..3] of integer; k:integer; begin k:=2; a[k]:=99; writeln(a[k]) end.`):

- `scrip --run t_arr2.pas` directly → **correct** (`99`). SCRIP's own array handling is fine.
- SCRIP-pcom compiling `t_arr2.pas` → P-code has `lao 9; ldoi 10; ldci 99; sroi 10; lao 9; ldoi 10; indi 0` — **scalar** (`sroi`), zero `ixa`. Native-pcom emits `lao 9; ldoi 12; chki 1 3; deci 1; ixa 1; ldci 99; stoi`.

---

## Bracket (instrument-derived, per RULES.md MONITOR-FIRST methodology adapted to pcom-level)

Native fpc-3.2.2 oracle built at `/tmp/p4o/pcom` and `/tmp/p4o/pint` (`fpc -Mtp`).

**Instrumented `pcom_dbg2.pas`** (two writeln probes in `selector`):

1. Right after `lattr := gattr` (selector:2133): both native and SCRIP print `#DBG-COPY-NONNIL#` → copy itself is fine.
2. Right after the index `load` (selector:2140, the subscript `k` compiled): native prints `#DBG-LATTR-TYPTR-NONNIL#`; SCRIP prints **`#DBG-LATTR-TYPTR-NIL#`**.

The `ixa`-emitting block (selector:2145–2171) is guarded by `if lattr.typtr <> nil`. SCRIP's `lattr.typtr` is nil → block skipped → no `chki/deci/ixa` → `gattr.access` stays `drct` → `store` emits `sro` (scalar) instead of `sto` (indirect). No `error(138)` fires because `lattr.typtr` was non-nil at the guard (2136) that calls `error`.

Between lines 2133 and 2140, `loadaddress` (2138) and `expression(…)` (2139, compiling the subscript `k`) run. `expression` for `k` descends the full expression parser → `variable` → `selector` again (for the scalar variable `k`). This re-enters `selector` recursively, which declares its own `var lattr: attr`. **The inner `selector(k)` clobbers the outer `selector(a)`'s `lattr`.**

---

## Root cause

**Aggregate (record/array) locals are not per-activation — they map to a single per-proc global cell.**

`src/lower/lower_pascal.c` `pas_resolve_name` line 81:

```c
if (slot >= 0 && found_sc && found_sc->proc_name &&
    strcmp(found_sc->proc_name, "main") != 0 &&
    pas_is_agg_local(name)) {
    if (slot_out) *slot_out = -1;
    const char * m = pas_cap_mangle(found_sc->proc_name, name);  /* "__up_<proc>_<var>" */
    pas_reg_var(m);
    return m;
}
```

`pas_cap_mangle(proc, var)` returns `__up_<proc>_<var>` — a global NV cell keyed on (proc, var) only, with **no activation/depth component**. All recursive activations of the same proc resolve the same name to the same cell.

This was introduced in PAS-SELFHOST-3d to fix *sibling-proc* local collisions (correct for that case). It is not re-entrant: recursive calls all alias the same global.

---

## Minimal standalone repro (`ov6.pas`, 9 lines of substance)

```pascal
program ov6;
type rec = record a: integer; b: integer end;
procedure recur(n: integer);
var local: rec;
begin
  local.a := n * 100;  local.b := n;
  writeln('enter n=', n, ' set local.a=', local.a);
  if n < 3 then recur(n + 1);
  writeln('after-recur n=', n, ' local.a=', local.a, ' (expect ', n*100, ')');
end;
begin recur(1) end.
```

Native output:
```
enter n=1 … local.a=100
enter n=2 … local.a=200
enter n=3 … local.a=300
after-recur n=3 local.a=300 (expect 300)  ✓
after-recur n=2 local.a=200 (expect 200)  ✓
after-recur n=1 local.a=100 (expect 100)  ✓
```

SCRIP output:
```
enter n=1 … local.a=100
enter n=2 … local.a=200
enter n=3 … local.a=300
after-recur n=3 local.a=300 (expect 300)  ✓
after-recur n=2 local.a=300 (expect 200)  ✗  ← all share one cell
after-recur n=1 local.a=300 (expect 100)  ✗
```

**Scalar locals under recursion work correctly** — only aggregate (record/array) locals alias. Confirmed with a matching scalar-only repro (`ov7.pas`) that gives correct `300, 200, 100`.

---

## Why pcom triggers it

`pcom`'s `selector` procedure (pcom.pas:2086) is called recursively: compiling `a[k]` calls `selector(a)`, which at line 2139 calls `expression(…)` to compile the subscript `k`; that descends through `simpleexpression → term → factor → variable → selector(k)`. The inner `selector(k)` activation overwrites the outer `selector(a)`'s `lattr` (type `attr` — a nested-variant record), zeroing `lattr.typtr`. The array-arm guard `if lattr.typtr <> nil` at 2145 then fails silently → `ixa` not emitted → scalar treatment.

The OVERLAY hypothesis (prior session) is **falsified**: variant-field reads on a heap-pointer (`structure = ^record … case form … arrays:(aeltype,inxtype)`) survive cross-procedure and cross-copy correctly in isolation — the failure is entirely in the **frame aliasing**, not the variant field layout.

---

## Fix direction (for next session)

**Recommended: give aggregate locals real per-activation frame slots**, same as scalars already have (`[fb+16+k*16]`). This retires the `__up_` mangle path for locals, makes recursion correct for aggregates without needing any activation-tracking scaffold, and directly unblocks:

1. `pcom` → `selector` recurses correctly → `ixa` emitted → `a[k]` works → pcom compiles variable-index arrays.
2. General recursion with aggregate locals (needed for pint and pcom's deeper proc nesting).

Concretely in `lower_pascal.c` `pas_resolve_name`: when `pas_is_agg_local(name)` AND we are inside a proc that is known to recurse (or conservatively: always give frame slots for agg locals, not global cells), resolve to a frame slot instead of a mangled global. The Pascal frame layout (`[fb+16+k*16]`) already supports record aggregates — they're stored as multi-slot SOH strings at one address — so storing the whole aggregate at a frame slot (using `arr_get`/`arr_set_pure` addressed by slot index rather than NV name) is the cleanest path.

Alternative (smaller): push/pop a per-depth activation copy of each aggregate local around each recursive call site. Avoid — it requires tracking which procs recurse and adds call-site scaffolding; the frame-slot approach is cleaner and more general.

---

## Files touched this session

None (diagnosis only). Gate: M3 149/0 · M4 149/0 unchanged.

## Artifacts produced (in /tmp, ephemeral)

- `/tmp/p4o/pcom`, `/tmp/p4o/pint` — native fpc-built oracle binaries
- `/tmp/pint7b/ov3.pas` through `ov7.pas` — isolation repros
- `/tmp/p4o/pcom_dbg.pas`, `pcom_dbg2.pas` — instrumented pcom variants
- `ov6.pas` — the minimal record-alias-under-recursion repro (to be added to corpus as a gated probe once the fix lands)
