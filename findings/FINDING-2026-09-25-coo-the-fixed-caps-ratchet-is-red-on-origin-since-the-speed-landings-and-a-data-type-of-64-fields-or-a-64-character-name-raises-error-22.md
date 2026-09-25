# FINDING 2026-09-25 (coo): the fixed-caps ratchet is red on origin since the SNOBOL4 speed landings, and a DATA type of 64 fields or a 64-character name raises error 22

Measured by the coo 2026-09-25 15:17-15:29 CDT on SCRIP `62a21f70f` (built `-O0`, incremental), corpus `c4f7b0257`, .github `fdd92db1`. MODE TENET (CEO-1266). The oracle is `sbl_correctness_bin` = `/home/resources/x64/bin/sbl -bf`.

## 1. The ratchet (`test_gate_dyn_caps_ratchet.sh`, a wired `make test` arm)

2 of 11 arms red, 6 m 07 s at load 21-33:

- arm 2: file/static/field population 391 vs BASELINE 384
- arm 5: function-scope population 486 vs BASELINE_FUNCTION_SCOPE 483

Like-for-like attribution: HEAD's census script run on `git archive d416aef90` (this seat's last landing, where both read exactly baseline) and on HEAD, rows keyed by file, scope, name, bound, guard and fill.

| added | scope | bound | guard | commit | what it is | class it could take |
|---|---|---|---|---|---|---|
| `bb_match_capture.cpp` `b[8][40]` | static | 8 | NONE | `1a350a380` 09-24 23:11 | ring of `[reg + %d]` operand strings | B: an int formatted into 40 bytes |
| `bb_match_capture.cpp` `b[24]` (two) | static | 24 | NONE | `1a350a380` | `strtab_label` scratch | B, if the label format is bounded (to be measured) |
| `keywords.c` `words[4]` | static | 4 | const | `af773a80e` 09-25 00:08 | RETURN/FRETURN/NRETURN as 8-byte words | A (const data) |
| `by_name_dispatch.c` `g_bn_direct[BID_TABSZ]` | file | 1024 | const | `0f560a28e` 09-25 01:24 | direct builtin table indexed by bid | A (const, indexed by the builtin enum) |
| `by_name_dispatch.c` `g_ctor_ic[256]`, `g_field_ic[256]`, `g_tweak_none[64]` | file | 256/256/64 | NONE | `82b4a61a8` 09-25 03:27 | direct-mapped inline caches; a miss takes the full by-name path | B, as `g_nv_memo_*` and `g_dcap_nv_*` are declared |

Locals, the same commit `82b4a61a8`: `chain[64]` (CALLEE:dat_mro), `_fv[64]` twice (COUNTER, lines 5857 and 5880), `proc[256]` (FORMAT:snprintf `"%s__TWEAK"`). One local left: `lower_snobol4.c` `lk[16]`, which `2a81a02db` removed. Net +3. These four are DROP guards, a program can reach them, and they cannot be declared away:

- `_fv[64]` clamps `_nf = nfields > 64 ? 64 : nfields`. This copies the older sites at `by_name_dispatch.c:7014` and `:9028`, and it is bounded today only by `DatType`'s own cap (section 2).
- `proc[256]` truncates the `__TWEAK` or `__BUILD` name of a class whose name runs past 247 characters.
- `chain[64]` caps the method-resolution chain at 64.

## 2. The DATA caps (older than the speed landings; census rows `rt_runtime.c:34` `name[64]` and `fields[64][64]`, guard NONE)

`typedef struct { char name[64]; int nfields; char fields[64][64]; } DatType;` (`src/runtime/rt_runtime.c:34`).

Witness A. A generated `DATA('T(F1,...,Fn)')`, then `X = T(10,...,n*10)` and `OUTPUT = F1(X) ' ' Fn(X)`:

| n | sbl -bf | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| 10 | `10 100` | same | - |
| 63 | `10 630` | same | - |
| 64 | `10 640` | `error 22: Undefined function called` at the Fn line, rc 1 | - |
| 65 | `10 650` | error 22 | - |
| 70 | `10 700` | error 22, rc 1 | error 22, rc 1 |

At n = 64, `T(...)` builds, `DATATYPE(X)` is `T`, and `F1` and `F63` answer. `F64(X)` is the undefined function, so the 64th field's accessor is never defined.

Witness B. A type name and a field name of 70 characters, `DATA('TTT...T(FFF...F,G)')`: sbl prints `1 2 TTT...T`, while SCRIP m3 gives `error 22: Undefined function called` at the constructor, rc 1.

Both are legal SPITBOL programs, and SCRIP refuses them.

## 3. The asks

- **To the lander (ceo):**
  - declare the seven tables in `scripts/fixtures/dyn_caps/CLASS_AB.tsv`, each with its measurement, and raise BASELINE 384 -> 391 in the same commit; or convert them;
  - convert or refuse loudly at the four locals.
  - The ratchet stays red on arm 5 until the locals move. Declaring the tables alone does not green it.
- **To the ceo, a row for the SNOBOL4 lane:** `DatType`'s `name[64]` and `fields[64][64]`, with the `_fv`/`fv` clamps behind them. Witnesses A and B are its DONE-WHEN material.
