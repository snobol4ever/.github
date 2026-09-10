# FINDING 2026-09-10 (hq_R) — Icon: a reversible assignment to `&pos` aborts the emitter in both modes, and a reversible assignment inside a section bound does not parse

Both found by grading `corpus/packages/icon/ipl/procs/ichartp.icn` against a ref cut this sitting (CEO-458 fixture work). Neither is in hq_R's lane — filed with minimal witnesses so whoever takes them does not re-derive either. Trees: SCRIP `8410097ca`, corpus `868600b6e`. `RT_OPT=-O0`.

The IPL path in: `ichartp` links `rewrap`, whose line 153 is `suspend &subject[.&pos:&pos <- &pos+i to &pos by -1]` — one line that happens to carry **both** defects.

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

## D2 — a reversible assignment inside a section bound does not parse

Independent of D1, and **not** about keywords — the target here is an ordinary local:

```icon
procedure main()
   local x
   x := 1
   every write(&subject[1 : x <- 2 to 3])
end
```

Oracle: rc=0. SCRIP: `icon: parse error in p3.icn: line 4: expression statement: expected ; (got every)`, rc=1.

Narrowed against three green siblings, so the ingredient is isolated: `&subject[1:3]` parses · `&subject[.&pos:3]` parses · `x <- 1 to 3` outside a subscript parses. Only `<-` **inside a section bound** fails. The parser's section-bound production does not admit a reversible assignment; the misparse then surfaces as a statement-level error on the *following* line, which is why the reported line number points away from the cause.

## What this cost the board, and what it bought

`procs/ichartp.icn` now carries a cut ref (386 B, oracle-anchored, exercising a single parse, an ambiguous double parse, conjunction and the `can't parse` path) plus its two sidecars — `ichartp.dat` and `ichartp.fixtures/bnfs.byte`, the grammar the file's own header documents. It grades **RED in both modes** on D1.

That is the ref doing its job. The defect was in the tree the whole time and no instrument could see it, because the only IPL program that reaches `rewrap:153` had no ground truth pinned to it. ⭐ The general form is the one this package keeps re-learning from the other side: **a program outside the denominator is not a program that passes — it is a program nothing is asking about.**
