# FINDING 2026-07-17 — PAS-SELFHOST-2: the "record-field char-array store writes integer 0" bug is an SOH-ENCODING COLLISION on READBACK, plus a SEPARATE whole-char-array PRINT gap

**Session:** Claude, 2026-07-17. SCRIP HEAD (post-`409f3508`, plain default build). M3 gate re-confirmed 143/0/2 (PASS/FAIL/NOREF) at start.

**⭐ UPDATE — DEFECT #2 LANDED + FULLY VERIFIED (this session, `pascal.y`-only, cross-language-safe by construction).** The whole-char-array PRINT gap is FIXED: `pascal.y` `mk_call` IO-arg loop now wraps a bare-`TT_VAR` whole-char-array write arg in `pas_alpha_wrap` (`__pas_alpha_str(x, lo)`), exactly mirroring the adjacent `is_char`→`mk_chr_wrap`/width-−2 precedent. +2 forward decls (`pas_is_chararr`, `pas_alpha_wrap`) + 1 `else if`. Regen `pascal.tab.c` byte-verified: bison 3.8.2 == the version that made the committed file, in-place regen of the UNMODIFIED grammar is byte-identical to HEAD, and the post-edit diff is exactly my one substantive line + mechanical `#line`/`yyrline[]` renumbering (zero grammar-table change, 5 s/r conflicts before and after). **VERIFIED:** `cmp_plain2.pas`(`'abcdefgh'`)→`abcdefgh`, `cmp_plain.pas`(`'integer '`)→`integer ` — both match native pcom+pint. **NO REGRESSION:** Pascal M3 143/0/2 · M4 143/0/0/2 (both full recipe, fresh build). Cross-lang: SNOBOL4 + Icon smoke clean, Prolog `test/prolog/hello.pl` clean; `git status` shows ONLY `pascal.y`+`pascal.tab.{c,h}` changed (zero shared emitter/runtime/lowerer) → cross-language safety is structural (PAS-UNBOX-1 precedent). **DEFECT #1 (record-field readback collision, the `rec_store.pas`→`0` case) is UNCHANGED — still open, needs the shared-runtime fix below.** Session-close push pending credential.

**Directive (Lon/Jeffrey):** "Get PCOM.pas and PINT.pas working and self hosting. Continue." Also uploaded `7_pascal-p4-main.zip` = the canonical ETH/CDC Pascal-P4 (`comp.p`/`int.p`) — symlinked `SCRIP/refs/pascal-p4` as the SEMANTIC cross-reference (corpus `pcom.pas`/`pint.pas` remain the `.ref` oracle, per the standing rung landmine).

---

## TL;DR

The LIVE CURSOR's next sub-bracket ("RECORD-FIELD CHAR-ARRAY STORE WRITES INTEGER 0", repro `rec_store.pas` → SCRIP prints `0`, native prints `integer `) is REAL and reproduces, but the mechanism is NOT a missed lowering branch. It is a **representation collision** in the SHARED runtime: a Pascal **record** is stored as an SOH-separated string of field values, and a whole **char-array** is ALSO stored as an SOH-separated string of decimal ordinals — so when a char-array is a record field, `arr_get(record, field_idx)` walks SOH looking for "element field_idx" and stops at the FIRST SOH *inside the char-array*, returning just the leading `"0"` sentinel → parsed as `INTVAL(0)`. Diagnosis is airtight (IR dump + runtime source). A SECOND, independent defect surfaced alongside it: **`__pas_writeln` does not decode a whole SOH-ordinal char-array** (width −1 path is a raw `fputs`), so even a plain `writeln(chararr)` prints the raw storage. Both are on pcom's critical path (its `enterid` does `name := id` where `name` is an `alpha` record field — pcom.pas:1050, :1126). Fix is feasible and localized; the decode primitive already exists (`__pas_alpha_str`). NOT attempted this session because it is a four-language-blast-radius `by_name_dispatch.c` change needing the full 4-lang + M3/M4 143/0 recert, and context budget did not allow a safe land+verify.

---

## REPRO (minimal, pcom-independent) — both confirmed against the native fpc-pcom+pint oracle

Native oracle rebuilt live: `apt-get install -y fp-compiler`; in `/tmp/p4boot`, `fpc -Ci -Co -Cr -gl pcom.pas` + `pint.pas`. Pipeline: `pcom < prog.pas` writes P-code to file **`prr`** (pcom.pas:3995 `assign(prr,'prr');rewrite(prr)`; the source LISTING goes to stdout, NOT the P-code). Then `cp prr prd; pint < /dev/null` (pint reads file `prd`, pint.pas:164; **`< /dev/null` is mandatory** or pint blocks on stdin and looks like a hang).

**A. `rec_store.pas` — record-field char-array store+read:**
```pascal
program t;
type r = record name: packed array[1..8] of char end;
var g: r; id: packed array[1..8] of char;
begin id := 'integer '; g.name := id; writeln(g.name) end.
```
- SCRIP `--run`: `         0`  (width-10 integer zero)
- native pcom+pint: `integer `
- **FAIL.**

**B. `cmp_plain2.pas` — plain whole char-array PRINT (no record):**
```pascal
program t;
var id: packed array[1..8] of char;
begin id := 'abcdefgh'; writeln(id) end.
```
- SCRIP `--run`: `0\x0197\x0198\x0199\x01100\x01101\x01102\x01103\x01104`  (raw SOH-ordinal storage)
- native pcom+pint: `abcdefgh`
- **FAIL — a DISTINCT defect** (the cursor's `cmp_plain.pas` was a *compare*, which uses the `__pas_alpha_str` strcmp arm and is green; PRINT of a whole char-array is what's broken, and no green corpus probe exercises it — consistent with the 2026-07-10 "KNOWN GAP" note that pcom's insymbol builds identifiers PER-CHAR).

---

## DEFECT #1 — `arr_get(record, field_idx)` returns SOH-element-0, not the whole char-array field (the `rec_store` `0`)

**IR (`scrip --dump-ir rec_store.pas`), the load path:**
```
9   CALL [6,7,8] "arr_set_pure"   ; operands VAR g, LIT_INTEGER 0, VAR id   -- store id into g[0]
...
13  CALL [11,12] "arr_get"        ; operands VAR g, LIT_INTEGER 0            -- read g[0] back
15  CALL [13,14] "__pas_writeln"  ; operands arr_get-result, LIT_INTEGER -1
```
So `g.name := id` lowered (correctly, in principle) to `arr_set_pure(g, 0, id)` and `writeln(g.name)` to `__pas_writeln(arr_get(g,0), -1)`. The whole char-array `id` IS handed to the store as operand 8. Lowering is NOT dropping it.

**The collision is on readback.** `g` initializes to the plain string `"0"` (record field-0 default). `arr_set_pure` (`by_name_dispatch.c:2477`): `cur="0"` has no SOH → line 2486 branch, `idx==0` → line 2488 stores `rv = to_cstring(id)` as a fresh element-0 string. `to_cstring` (:238) on a STRING returns it verbatim, so `g` becomes the SOH-ordinal char-array string `"0\x01105\x01110\x01116..."`. **That store is actually fine.** Then `arr_get(g,0)` (:1809) with `cur="0\x01105\x01110..."`, `idx==0`: line 1816 needs idx≥1 (skip); the SOH walk at :1819 hits `k==0==idx` immediately, `nx=strchr(cur,SOH)` at the first `\x01`, so `elen = nx-cur = 1` (just `"0"`), `elem_to_descr("0",1)` (:244) parses "0" as an integer → **`INTVAL(0)`**. The whole char-array field collapses to its leading sentinel byte.

**Root:** record-field storage (SOH-separated field values) and char-array storage (SOH-separated ordinals) share the SOH delimiter, so a char-array field is indistinguishable from N integer fields once stored. `arr_get`/`arr_set_pure` index-0 semantics ("get SOH element 0") collide with "get the whole char-array field."

**LAND MINE COORDINATES:**
- `src/runtime/by_name_dispatch.c:1809` `arr_get` — the SOH-element-0 extraction (:1819-1828) is the exact instruction that returns the wrong value.
- `src/runtime/by_name_dispatch.c:2477` `arr_set_pure` — the store side (works today, but is the other half of the shared-SOH representation).

## DEFECT #2 — `__pas_writeln` does not decode a whole SOH-ordinal char-array (the `cmp_plain2` raw-junk print)

`by_name_dispatch.c:3436` `__pas_writeln`/`__pas_write`. For a non-int/non-real value at width −1 (the whole-char-array case), :3462-3468 does `const char *_ps = VARVAL_fn(av); ... fputs(_ps,_dest)` — it prints the storage string RAW. When `av` is a whole char-array `"0\x0197\x0198..."`, that dumps the SOH ordinals instead of decoding them to `abcdefgh`.

**LAND MINE:** `src/runtime/by_name_dispatch.c:3463-3467` — the `else` (string) arm of `__pas_writeln`, width<0 sub-branch (`else { fputs(_ps,_dest); }`).

---

## WHY THIS IS ON THE pcom CRITICAL PATH (not an academic corner)

pcom's `enterid` builds its identifier BST with `alpha` (`packed array[1..8] of char`, pcom.pas:140) record fields:
- **STORE:** pcom.pas:1050 `begin name := id; ...` and :1126 `begin name := id; ...` — whole-`alpha`-into-record-field, i.e. exactly `rec_store.pas`. EVERY identifier pcom enters hits this.
- **COMPARE:** pcom.pas:563/566/582/595/602 `lcp^.name = nam`, `fcp^.name = id`, `fcp^.name < id` — record-field char-array relops in the BST search. (These likely already ride the `__pas_alpha_str` strcmp arm; VERIFY after the store fix — a corrupted stored name will make the compare wrong regardless.)

If the stored `name` collapses to `INTVAL(0)` / a truncated element, pcom's symbol table is corrupt from the first identifier — this is a strong candidate for the deeper SELFHOST-3/5 stalls, not just a toy-probe failure.

---

## FIX DESIGN (feasible, localized; the decode primitive already exists)

The proven decoder is **`__pas_alpha_str`** (`by_name_dispatch.c:1502`): walks SOH-ordinal storage via `strtol` per segment, skipping below `lo`, emitting the decoded char string. It is what makes the char-array COMPARES green today. Reuse its logic (factor a static `pas_alpha_decode(const char *soh, long lo, char *out)` helper so writeln, arr_get-on-a-char-array-field, and `__pas_alpha_str` share ONE decoder — RULES.md "one comment / no dup" hygiene).

**Defect #2 (smallest, do FIRST — purely additive, near-zero blast radius):** in `__pas_writeln` :3463-3467, before the raw `fputs`, detect an SOH-ordinal char-array (a string whose SOH-separated segments are ALL decimal, leading `"0"` sentinel) and, if so, print `pas_alpha_decode(...)` instead. Gate on the shape of the value, NEVER on `LANG_PASCAL` (BB-TEMPLATES-LANG-AUDIT). Risk: a non-Pascal caller printing a genuinely-SOH-delimited numeric string at width −1 — audit for that (SNOBOL/Raku list `writeln`?) before landing; if ambiguous, thread a width sentinel (like the existing `-2`=char, `-3`=fixed-real) meaning "whole char-array" set by the Pascal lowerer for whole-`alpha` write args, so the decode fires ONLY for Pascal-emitted whole-char-array writes. The sentinel route is the safe one and matches the existing `__pas_chr`/`-2`/`-3` precedent.

**Defect #1 (the record-field readback):** the principled fix is to STOP overloading `arr_get`/`arr_set_pure` for char-array-typed record fields and route them through `__pas_field_set`/a new `__pas_field_get` that treats the field's whole value atomically (the `__pas_field_set` sink at :1509 already does whole-field replace; it needs a read twin that returns the whole field segment WITHOUT sub-walking its internal SOH). Where to branch: `lower_pascal.c` `lower_assign` (:294 general TT_IDX path) and the TT_IDX read arm (`lower`, :497) — when the record field's declared type is a char-array (the parser knows this: `pas_is_chararr`/the chararr registry that `pas_is_strtyped` already consults), emit a whole-field get/set that does NOT sub-index the char-array's SOH. This is the harder half; it needs the field-type to be threaded to the lowerer arm (the registries exist — `g_pas_recvars`, the chararr `.lo` registry from the 2026-07-10 STRARR work).
  - Cheaper alternative (characterize first): keep `arr_get`/`arr_set_pure` but make the char-array field a SINGLE opaque element in the record's SOH by escaping the char-array's internal SOH on store and unescaping on read — smaller, but adds an escape layer to the shared sink. Prefer the typed-field route unless it proves too invasive.

**Gate (per rung landmines):** full 4-language gate (SNOBOL/Icon/Prolog/Raku) + template byte-identity (`BB-TEMPLATES-LANG-AUDIT.md` grep==0) + Pascal M3/M4 143/0 recert, because `by_name_dispatch.c` is shared runtime → `make libscrip_rt` + landmines #4/#6. Add `rec_store.pas` and `cmp_plain2.pas` as passing corpus probes with native refs once fixed.

---

## STATE FOR NEXT SESSION

- **Refs ready:** `SCRIP/refs/{jcon-master,icon-master,pascal-p4}` all symlinked + verified. `pascal-p4` = the new upload (ETH `comp.p`/`int.p`, semantic cross-ref only).
- **Oracle rebuildable:** `/tmp/p4boot` fpc-pcom+pint (evaporates; recipe above). Native answers: `rec_store`→`integer `, `cmp_plain2`→`abcdefgh`.
- **Build:** plain `make -j4 scrip` + `make libscrip_rt` (NO `-lgc` — libgc-dev is GONE per GC-U-4/s67; the install script's own comment says so; both link lines are `-lm`/`-lm -lstdc++ -lpthread`). `install_system_packages.sh` first (`libgmp-dev m4 nasm wabt bison flex`).
- **Gate scripts:** reconstruct in /tmp (they evaporate): M3 = loop `corpus/programs/pascal/*.pas`, skip `pcom*|pint*|ppp*`, `.ref` sibling, stdin `$stem.in` or `/dev/null`; 143 have `.ref`, NOREF=2 (`chararr_probe`,`recursion`). M4 = `scrip --compile > f.s`; `gcc -c f.s -o f.o`; `gcc -no-pie f.o -L SCRIP/out -lscrip_rt -lm -Wl,-rpath,SCRIP/out -o f.bin`; run vs `.ref`.
- **DO FIRST next session:** Defect #2 (whole-char-array writeln decode via width sentinel — smallest, safest). Then Defect #1 (typed record-field char-array get/set). Then re-measure pcom on `l_var*`/identifier-entry probes — this may unblock SELFHOST-3/5.

## DOC-CONTRADICTIONS OBSERVED (flag for Lon — not fixed this session)

1. **GOAL-PASCAL-BB.md "Where things live" / landmines still say `src/emitter/BB_templates/` and `emit_bb.c`/`emit_core.c`.** The current tree is `src/emitter/emit.cpp`+`emit.h` (ONE driver) and `src/templates/*.cpp` (FLAT, no subdirs) — confirmed by `REPO-SCRIP.md` and the live `libscrip_rt` link line. Same stale-path class RULES.md already flags elsewhere.
2. **Bison regen:** GOAL-PASCAL-BB landmine #2 says "Pascal regen ONLY: `bison -d -o pascal.tab.c pascal.y`", but `REPO-SCRIP.md` says NEVER run bison/flex by hand against committed grammars (the `.tab.c` is the committed tested artifact, no Makefile rule regenerates it). If a `pascal.y` edit is ever needed, resolve this with Lon first.
3. **`-lgc`:** every GOAL-PASCAL-BB link recipe and landmine mentioning `libgc-dev`/`-lgc` is stale (removed s67). Harmless (build succeeds without it) but the docs mislead.
