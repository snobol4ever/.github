# FINDING 2026-07-23 — PAS-PINT-6: whole-record array-element copy + chain-traversal limit → pcom→pint round-trip runs on SCRIP

**Session outcome:** The Pascal self-hosting round-trip now runs end-to-end on SCRIP for real programs.
`hi.pas` (writeln) AND `calc.pas` (`for i:=1 to 5 do s:=s+i; writeln(s)` — the `06_for` case the prior
cursor was stuck on) both compile via **SCRIP-pcom** to P-code and then execute under **SCRIP-pint**,
printing `HI` and `15` respectively — matching the native fpc-pcom/fpc-pint oracle chain.

Two independent bugs were bracketed and fixed. **Gates: M3 149/0, M4 149/0** (149 = prior 148 + the new
`recspan_copy` probe). Cross-language regression sweep clean, stash+rebuild-verified: Icon 4/0, Prolog 168/0,
Raku 51/0, SNOBOL4 M3 302/8 + M4 302/6 (the 8/6 are PRE-EXISTING — identical on a pristine stash-rebuild;
pattern-eval + indirect-goto families, unrelated to these changes).

---

## BUG 1 — whole-record array-element copy lost all fields (the pint blocker)

**Symptom.** `arr[k] := arr[j]` where `arr : array[..] of {record}` produced a destination whose fields all
read back 0. Affected ANY record with ≥2 fields (plain OR variant) — NOT variant-specific, correcting the
prior cursor's `nrec \x05-blob` framing.

**Bracket (IR, not guessed).** An `array[lo..hi] of {record with nf fields}` is stored FLATTENED into one 1-D
SOH array of `(hi+1)*nf` slots; record `i` occupies flat slots `[(i-lo)*nf .. +nf-1]`. A field access
`arr[i].f` correctly scales via `pas_arrrec_flatten` to `arr[(i-lo)*nf + f]`. BUT a bare record-element
selector `arr[j]` (no `.field`) is a plain `TT_IDX(arr, j)` carrying the RECORD index, unscaled. So
`arr[k]:=arr[j]` reached `mk_assign`'s fallback → `TT_ASSIGN(TT_IDX(arr,k), TT_IDX(arr,j))` →
`arr_set_pure(arr,k, arr_get(arr,j))` — a SINGLE-slot scalar copy using record indices as flat indices, no
`*nf`, only 1 of `nf` slots moved. `--dump-ir` on `p_multi.pas` showed exactly `arr_get(arr,1)` /
`arr_set_pure(arr,2,...)` where correct behavior needs slots `[2,3]`→`[4,5]`.

**Why it is the pint blocker.** `pint.pas` `store : array[0..overm] of record case datatype of …` and the
P-machine is DRIVEN by whole-element cross-index copies — `store[sp]:=store[ad]`, `store[q]:=store[sp]`, and
the `mov` opcode `for i:=0 to q-1 do store[i1+i]:=store[i2+i]`. Every value move on the P-stack hit this bug.
Canonical P4 confirms the intended semantics: `comp.p` `assignment` compiles a whole record/array assignment to
`gen1(40(*mov*), typtr^.size)`; `int.p` executes `mov` as a flat cell-range copy indifferent to the
destination's prior contents — i.e. copy the whole fixed-size record span.

**Fix (`src/parser/pascal/pascal.y`, parser-only).** New `pas_recspan_nf(e)` (returns `nf>1` for an arrrec
element or a plain record var) + `pas_recspan_slot(e,fi)` (flattens an element via `pas_arrrec_flatten`, or
indexes a record var). A clause at the top of `mk_assign`: when both sides are whole records of the same
`nf>1` **and at least one side is an array element** (`TT_IDX` — so working plain `recvar:=recvar`
whole-descriptor copy is left untouched), emit a `TT_SEQ_EXPR` of `nf` per-slot assignments
`arr[k*nf+fi]:=arr[j*nf+fi]`, reusing the natural `arr_get`/`arr_set_pure` lowering. This faithfully moves all
`nf` slots — including every variant field — matching P4's whole-span `mov`.

**Note — separate deferred bug:** variant OVERLAY (write `vi`, read `vb` on the SAME record → 0) because SCRIP
assigns variant fields DISTINCT sequential slots instead of overlapping offsets. NOT the pint blocker (pint's
dominant pattern is whole-copy, which the span fix moves faithfully); deferred.

---

## BUG 2 — chain-traversal queue guard aborted compiling pint (`CH_MAX` too small + over-strict guard)

**Symptom.** With BUG 1 fixed, SCRIP-pint aborted at compile time:
`[GZ-7] FATAL: chain traversal queue saturated (qt=8559 >= CH_MAX=8192)`.

**Bracket.** `codegen_flat_chain_body` (`src/emitter/emit.cpp`) BFS-collects a proc's flat IR nodes into
`nodes[CH_MAX]`; `queue[Q_MAX]` (Q_MAX = 16×CH_MAX). pint is large enough that ENQUEUES (`qt`, counts dups)
exceed `CH_MAX`. The line-1811 guard aborted on `qt >= CH_MAX` even though `queue` legitimately holds
`Q_MAX = 16×CH_MAX` — an over-conservative false positive (real overflow of the dedup'd node array is already
guarded by `n >= CH_MAX` at 1768/1793).

**Fix (`src/emitter/emit.cpp`, 3 lines).** (a) `CH_MAX` 8192→65536; (b) `nodes[]` → `static` so the larger
array does not blow the C stack (`queue` was already `static`, so the function is already treated as
non-reentrant during the walk); (c) the queue guard now checks `qt >= Q_MAX` (the true array bound), keeping
real-overflow protection while removing the false abort.

---

## Repros / harness (all under `/tmp`)
- `/tmp/pas6/` — `iso_var.pas` (variant cross-idx→7), `p_multi.pas` (plain 2-field cross-idx→`3 4`),
  `iso_copy.pas` (1-field→7), `r_plain.pas`/`iso_self.pas` (regression controls, whole-descriptor copy),
  `recspan_copy.pas`(+`.ref`) the comprehensive probe (now in corpus).
- `/tmp/p4o/` — native fpc `pcom`/`pint` oracles (fpc 3.2.2) + `hi.pas`/`calc.pas`. P4 file convention: pcom
  writes P-code to file `prr`; pint reads P-code from file `prd` (`assign(prd,'prd')`), stdin = program input
  (feed `/dev/null` or it blocks). SCRIP-pcom writes P-code to the `prr` FILE and the source LISTING to stdout
  (do NOT diff stdout as if it were the P-code — the prior confusion).

## New gated corpus probe
`corpus/programs/pascal/recspan_copy.pas` + `.ref` (SCRIP width-10 format, values fpc-cross-checked; M3==M4
byte-identical). Covers plain-2-field cross-idx (chained a[2]:=a[1]; a[3]:=a[2]), variant cross-idx. +1 → 149.

## Files touched
- `src/parser/pascal/pascal.y` (+ regen `pascal.tab.c`/`.tab.h`; bison 5 s/r == pristine)
- `src/emitter/emit.cpp` (shared — 4-lang sweep clean)
- `corpus/programs/pascal/recspan_copy.pas` + `.ref`

## Next rung candidates
- Drive the round-trip further: larger programs, then the pcom self-compile fixpoint (pcom compiling its own
  ppp-preprocessed source under SCRIP-pint, diffed against fpc P-code) — the PAS-SELFHOST milestone proper.
- Variant OVERLAY (shared-offset variant fields) if a corpus/pint path needs it.

---

## PAS-PINT-7 BRACKET (proven; root NOT yet found — recorded honestly, next session starts here)

**Symptom.** Pushing richer programs through the round-trip: `t_case.pas` PASSES fully; but `t_arr.pas`
(`for i:=1 to 3 do a[i]:=i*10; for i:=1 to 3 do writeln(a[i])`) → SCRIP round-trip prints `1 2 3`, native
`10 20 30`. `t_proc.pas`/`t_func.pas` also show bracket-1 DIFF (SCRIP-pcom P-code ≠ native). (`t_while.pas`
is a NATIVE-oracle anomaly — native pint itself prints nothing for my exact while syntax; set aside, likely a
probe-syntax quirk, not a SCRIP bug.)

**Bracket (P-code diff, minimal repro `t_arr2.pas` = `var a:array[1..3] of integer; k:integer; begin k:=2;
a[k]:=99; writeln(a[k]) end`).** SCRIP-pcom DROPS the array-subscript address arithmetic. Native emits, for
`a[k]`: `ldoi 12; chki 1 3; deci 1; ixa 1; stoi` (load array base, bounds-check, subtract lower bound,
index-address `ixa`, store-indirect). SCRIP-pcom emits `ldoi 10; … sroi 10` — a SCALAR global store (`sroi`),
**zero `ixa`**, treating `a[k]` as a scalar. `grep -c ixa`: native=2, SCRIP=0. (Storage addresses also differ,
12/13 vs 10/11 — pcom-under-SCRIP allocates globals from a different base; self-consistent, not itself fatal.)
Why the value still round-trips for `a[k]:=99;writeln(a[k])`: store AND load both use the same wrong (base)
address, so it's self-consistent; it only MANIFESTS when the index varies across accesses (the `t_arr` loop).
Artifacts saved: `/tmp/pint7/{t_arr.pas,t_arr2.pas,prr_nat_arr2,prr_scr_arr2}`.

**Locus in pcom.** `pcom.pas:2135-2170` (`selector`, array arm): guarded by `if typtr^.form <> arrays then
error(138)`; does `loadaddress` (2138), index `expression`+`load`, optional `chk`, `dec lmin`, then
`gen1(36 ixa, lsize)` (2169). For SCRIP to emit `sroi` (scalar) not `stoi`+`ixa`, pcom-under-SCRIP is NOT
taking the arrays arm / `loadaddress` is behaving as a scalar load.

**Hypothesis RAISED then PARTIALLY FALSIFIED (do not write up as root).** First guess: pcom's type descriptor
`structure` (`pcom.pas:118-132`) is a VARIANT record `case form: structform of … arrays:(aeltype,inxtype) …`
and the deferred variant-OVERLAY bug (SCRIP gives variant fields distinct slots, not shared offsets) corrupts
`^.form`/`^.aeltype` reads. BUT a direct repro of pcom's exact shape (`/tmp/pas6/pcom_shape.pas`: explicit-tag
variant record, set `form:=arrays`, set+read `aeltype`/`inxtype`, test `form=arrays`) PASSES in SCRIP
(`is-array`, `5 7`) matching native — because it reads back the SAME variant fields it wrote. The overlay bug
only bites when reading a DIFFERENT variant arm than written (`iso_overlay`: write `vi` read `vb`→0). So the
overlay is NOT proven to be the ixa-drop root; something else in the `loadaddress`/array-arm path is. NEXT
SESSION: bracket with the monitor / gdb which IR construct SCRIP mis-executes when running pcom's line-2138
`loadaddress` + line-2169 `ixa` path — do NOT assume overlay.

