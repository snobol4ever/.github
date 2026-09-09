# FINDING 2026-09-08 hq_V — `$` of a value that is ALREADY a name was stringified to the cell's contents

**Seat** hq_V (HQ-VALIDATE) · **Mode** NONET · **Tree** SCRIP `458805e69`, corpus `9851eb79e`, RT_OPT=-O0
**Suite** snoflake (`test_snoflake_suite.sh`) · **Oracle** `sbl -bf` (`/home/resources/x64/bin/sbl`)

## The claim, measured

By-name assignment through a **plain variable** worked; by-name assignment through an
**aggregate cell** silently wrote the wrong variable. Minimal repro, both modes, oracle on the left:

```
        DEFINE('SWAP(P,Q)T')                    :(SWEND)
SWAP    T = $P
        $P = $Q
        $Q = T                                  :(RETURN)
SWEND
        A = ARRAY(2)
        A<1> = 'X'; A<2> = 'Y'
        SWAP(.A<1>, .A<2>)
        OUTPUT = 'ARRAY: ' A<1> ' ' A<2>
        U = 'P'; V = 'Q'
        SWAP(.U, .V)
        OUTPUT = 'VARS:  ' U ' ' V
END
```

| | `sbl -bf` | SCRIP before | SCRIP after |
|---|---|---|---|
| `ARRAY:` | `Y X` | `X Y` | `Y X` |
| `VARS:` | `Q P` | `Q P` | `Q P` |

## Where it was lost — one line, not the machinery

Everything the cure needed already existed and was already correct:

- `.A<1>` lowers through `sx_subscript_lv` to `IR_SUBSCRIPT` (`lower_snobol4.c`);
- `c_rt_subscript_var` returns `NAMETRAP(vc)` with `vc->cellp = &a->data[off]` (`pattern_match.c:1265`);
- `c_rt_assign_var_body` commits through `vc->cellp` (`pattern_match.c:1513`).

The reference survived assignment **and** argument binding. It was thrown away in exactly one
place: `bn_sno_name` (`by_name_dispatch.c:4722`), the `$` resolver, which called
`rt_sno_indirect_name` **unconditionally**. For a `DT_N` operand that function falls through to
`VARVAL_fn` (`core.c:2249`) and stringifies the name to the **value of the cell it names**.
`bn_sno_name` then rebuilt a name-by-string from that value, so with `A<1>` holding `'X'`,
`$P = 'Z'` created and wrote a global named `X` and left `A<1>` untouched. Confirmed directly:
`DATATYPE(N)` read `NAME`, `A<1>` stayed `X`, and a variable `X` appeared holding `Z`.

**Cure** (SCRIP `093ab602c`): an operand that is already a name passes through untouched.

```c
if (IS_VARREF_fn(args[0])) { *out = args[0]; return 1; }
```

## Why it presented as ERROR 246 stack overflow

Gimpel's `HSORT` is Hoare quicksort and partitions with `SWAP(.A<J>, .A<K>)`. With the swap a
no-op the partition never progresses, so the recursion never bottoms out and the board showed
`ERROR 246 -- stack overflow` — a symptom three suite-widths away from its cause. **An
ERROR 246 on a program SPITBOL completes should be read as a suspected silent-no-op upstream,
not as a depth problem.**

## Board movement — measured, and attributed honestly

Snoflake `102/124` → `106/124` on tree `458805e69`. That tree carries this cure **and** work
rebased in from other seats, so the four flips split:

| fixture | attributed to |
|---|---|
| `gimpel-sorting-functions` | this cure (proven by the minimal repro above) |
| `gimpel-binary-tree-linearize` | this cure (`LINEARIZ.INC` returns by name) |
| `gimpel-read-list-functions` | this cure (`READL.INC` returns by name) |
| `dump-variables` | **not this cure** — arrived with the rebase (`&FILE` reading empty) |

## Still red, and NOT this cause

`gimpel-conversions` and `gimpel-linked-list-functions` still reach `ERROR 246` on a **separate**
cause and are named on the row rather than quietly carried:

- `COPYL.INC` re-`DEFINE`s itself with an alternate entry label (`DEFINE('COPYL(L)', 'COPYL_1')`)
  and calls itself; if the redefinition does not take effect the call re-enters the original
  entry and recurses forever.
- `SPELL.INC` recurses through in-place pattern replacement (`N RTAB(3) . M =`); if the
  replacement does not shorten `N`, the recursion never terminates.

## Control arms — shared node

`src/runtime/by_name_dispatch.c` is a shared node. Per CEO-405 the census names the floor, so the
state actually touched was asked for: this changes only the `SNO$NAME` builtin body, reachable
only from `lower_snobol4.c`'s `sx_nameval`, and touches no global, no dedicated register and no
runtime entry point another frontend rides. Arms run anyway, all no worse than the clean tree:

| arm | reading |
|---|---|
| SNOBOL4 master | both-modes 1894/1894 |
| Icon master | both-modes 704/704 |
| Prolog master | m3 518 · m4 439 of 559 |
