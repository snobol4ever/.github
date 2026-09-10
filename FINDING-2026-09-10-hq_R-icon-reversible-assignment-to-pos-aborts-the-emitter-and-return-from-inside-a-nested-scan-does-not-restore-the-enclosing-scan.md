# FINDING 2026-09-10 (hq_R) — Icon: a reversible assignment to `&pos` aborts the emitter in both modes, and `return` from inside a nested scan does not restore the enclosing scan

Both found by grading IPL programs against refs cut this sitting (CEO-458 fixture work) — D1 through `procs/ichartp.icn`, D2 through `progs/strimlen.icn`. Neither is in hq_R's lane — filed with minimal witnesses so whoever takes them does not re-derive either. Trees: SCRIP `8410097ca`, corpus `868600b6e`. `RT_OPT=-O0`.

The IPL path in for D1: `ichartp` links `rewrap`, whose line 153 is `suspend &subject[.&pos:&pos <- &pos+i to &pos by -1]`. ⛔ This FINDING originally claimed that one line carried **both** defects and that the second was a parse defect. **That second claim was retracted the same sitting and is corrected in place below** — it was my witness, not the compiler. The real D2 was found by pursuing the same line correctly.

## D1 — `&pos <- expr` aborts the emitter (TE-4), m3 and m4 alike

```icon
procedure main()
   "abcdef" ? {
      every write(&pos <- 3 to 5)
   }
end
```

Oracle: rc=0, `3\n4\n5\n`. SCRIP: **rc=134 (abort)**, both modes, on its own diagnostic:

```
[TE-4] IR_REV_ASSIGN '&pos': not a global (is_global checked, so not the bb_rev_assign_global path)
and no LOWER-granted varslot as a local — grant it in ir_drive_slot_assign, never in the emitter
```

`src/emitter/emit.cpp:1780-1790`, the `IR_REV_ASSIGN` arm, offers exactly two destinations: **global-by-name** (`is_global(vn)`) or **local varslot** (`bb_varslot_peek(vn)`). `&pos` is a keyword and is neither, so it falls off the end and aborts. `x <- 1 to 3` on a plain local is green, so the defect is specific to a keyword target.

⭐ **The cure already exists one box over, which is why this is worth naming precisely rather than filing as "no keyword support".** `IR_REV_SWAP` — Icon's `<->`, the same reversible family — solves this exact problem three times over and its diagnostic even says so:

- `src/templates/bb/bb_rev_swap.cpp:16` — `rsw_kind()` selects on the NAME: `0` plain slot, `1` `&pos`, `-1` unknown; `rsw_eff()` promotes to `2` global-by-name.
- `src/runtime/builtins/gen_runtime.c:200-207` — `rsw_get`/`rsw_set` implement kind `1` against the scan spill slots (`spill[0]` = pos-1, `spill[1]` = subject length, falling back to `scan_pos`/`scan_subj`), with `cvpos_of` doing Icon's negative-position conversion.
- The runtime's own refusal names the extension point: *"only plain vars and &pos are wired; add the kind to rsw_get/rsw_set"*.

So `IR_REV_ASSIGN` needs the **three-way kind selector `IR_REV_SWAP` already has**, and the runtime half is already written. ⛔ The emitter's own message points at `ir_drive_slot_assign` — that is right for a *local that was never granted a slot*, and it is the **wrong cure here**: granting `&pos` a varslot would make it a frame local and silently divorce it from the scan state that `rsw_set` maintains. The keyword is not a variable that lost its slot; it is a destination kind the box does not have.

⚠️ Lane: `bb_rev_assign*` is a template box, so this is a shared-node change — hq_B's Icon lane to author, hq_U co-signing per RULES.md § SHARED-NODE VERDICT SCOPE. hq_R is not taking it (rule 7: never a template).

## D2 — ⛔ RETRACTED, AND REPLACED BY A REAL ONE: `return` from inside a nested scan does not restore the enclosing scan

**The D2 originally filed here — "a reversible assignment inside a section bound does not parse" — was wrong, and it was my own error, not the compiler's.** SCRIP Icon is **semicolon-required** (`CLAUDE.md`, § Semantics: the front end does zero newline processing and icont-style Beginner/Ender insertion is forbidden). My witness was a three-statement procedure body written without semicolons, so SCRIP was correctly refusing it. With the semicolons it is required to have, `&subject[1 : x <- 2 to 3]` **parses and matches the oracle**, and so do the two other "parse defects" the same mistake produced (`\t["nope"]`, a braced block as an argument). ⭐ The tell was there and I walked past it three times: an "instrument" that reports a parse error on the *following* line, in four unrelated constructs, is describing the witness, not the tree.

Chasing the rest of `rewrap:153` with correct semicolons found the real second defect, and it is a better one.

```icon
procedure inner(x)
   x ? {
      return tab(0);
   };
end
procedure main()
   write("AB" ? (inner("zz") || move(1)));
end
```

| | result |
|---|---|
| iconx | `zzA` |
| SCRIP m3 | **`zzz`** |
| SCRIP m4 | **`zzz`** |

`inner` returns `"zz"`; the enclosing scan's `move(1)` should then yield `"A"`, the second character of the **outer** subject `"AB"`. SCRIP yields `"z"` — **the outer scan is still pointed at the inner subject.** A `return` executed from inside a `s ? {…}` block does not restore the enclosing `&subject`/`&pos`.

⭐ **The control arm is what makes this precise, and it exonerates everything else in the neighbourhood.** Moving the `return` *out* of the scan block — `x ? { r := tab(0); }; return r;` — is **green**. So nested scanning is fine, calling a scanning procedure from inside a scan is fine, and the save/restore works on the block's normal exit path. Only the **early-return path** out of a scan body is missing it. Also green: a non-scanning procedure in the same argument slot, and my own scanning procedure that returns after its block. It took a procedure that returns *from inside* its own scan to reach it — which is exactly what IPL's `procs/escape.icn` does (`return ns || tab(0)` sits inside `s ? { … }`), and `escape` is how `procs/ivalue.icn` decodes a string literal.

**How it was reached:** `progs/strimlen.icn` is `while write(*ivalue(read()))`. `ivalue("\"hello\"")` returns `&null` in SCRIP and `"hello"` in the oracle, so `*` prints `0` instead of `5` — because `ivalue`'s string-literal arm is `2(="\"", escape(tab(-1)), ="\"")` and the trailing `="\""` cannot match once `escape` has left `&pos` in the wrong subject.

## What this cost the board, and what it bought

`procs/ichartp.icn` now carries a cut ref (386 B, oracle-anchored, exercising a single parse, an ambiguous double parse, conjunction and the `can't parse` path) plus its two sidecars — `ichartp.dat` and `ichartp.fixtures/bnfs.byte`, the grammar the file's own header documents. It grades **RED in both modes** on D1.

That is the ref doing its job. The defect was in the tree the whole time and no instrument could see it, because the only IPL program that reaches `rewrap:153` had no ground truth pinned to it. ⭐ The general form is the one this package keeps re-learning from the other side: **a program outside the denominator is not a program that passes — it is a program nothing is asking about.**
