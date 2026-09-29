# FINDING 2026-09-29 — the six .sc parsers' pattern census: which named patterns are not constant folded

**Asked by Lon, 2026-09-29 ~14:05 CDT, in-chat to the ceo, verbatim:** *"First, report for one or a few parser.sc programs the names of the PATTERNS that are not CONSTANT FOLDED?"*

**Tree:** SCRIP `ae1882d60` (origin/main). **Instrument:** `wip-patches/patdiag-pattern-census-with-parts-2026-09-29.patch` (a `git apply`-able diff of `src/lower/lower_snobol4.c`: the 29f patdiag patch plus the variant-part listing for the statement, value and match routes); run by `wip-patches/patdiag-census-run-2026-09-29.py <worktree> <outdir> [langs]` (concatenates the driver chain `global case assign match counter stack tree ShiftReduce tdump gen qize semantic omega trace parser_<lang>` exactly as pcmp.sh does, compiles it with `SCRIP_PATDIAG=1 scrip --compile`, maps each line back to its file) and rendered by `wip-patches/patdiag-census-grid-2026-09-29.py`. A named pattern is FOLDED when its statement (`Name = <pattern>`) pre-compiles it with zero run-time parts; NOT FOLDED lists every part the statement snapshots at run time into `PAT$n$V<i>`: a bare variable (`var`), a non-literal primitive argument (`as an argument`), an eager call. `name:line` is the line the definition starts on.

| parser | named patterns | folded | not folded | only `epsilon` | `epsilon` + bare pattern names (fix `*X`) | a variable as a primitive argument |
|---|---:|---:|---:|---:|---:|---:|
| snobol4 | 91 | 50 | 41 | 32 | 2 | 7 |
| snocone | 113 | 58 | 55 | 35 | 19 | 1 |
| icon | 204 | 95 | 109 | 21 | 84 | 4 |
| prolog | 116 | 66 | 50 | 26 | 18 | 6 |
| rebus | 140 | 96 | 44 | 27 | 16 | 1 |
| pascal | 150 | 58 | 92 | 47 | 44 | 1 |

Lon's epsilon ruling (GOAL-SNOCONE-100 cursor 29f) alone folds 188 of the 391; `*` on the bare pattern names folds 183 more by hand in the source; about 20 remain, each naming `nl`, `tab`, `cr`, `X1xxxxxxx` or `bin_digits` as a SPAN/BREAK/ANY/NOTANY argument (the one-character variables `global.sc` cuts from `&ALPHABET`; a SPITBOL string literal cannot hold a newline) -- Lon's call.

## The worklist, per parser

### parser_snocone.sc — 113 named patterns: 58 folded, 55 not
- **epsilon** (35): Id:16 Real:39 CallArgs:84 ExprList:92 XList:93 Expr17:94 Expr16:110 Expr15:111 Expr13:125 Expr12:126 Expr11:132 Expr10:133 Expr9:134 Expr8:135 Expr7:136 Expr6:137 Expr5:138 Expr4:143 X4:144 Expr3:145 X3:146 Expr1:148 Expr0:149 ThenBlock:162 if_cmd:165 do_cmd:170 ForBody:173 DefaultArm:180 switch_cmd:182 Params:190 Locals:192 StructFields:215 stmt_body:220 Command:226 Compiland:247
- **Id** (17): break:17 case:18 continue:19 default:20 do:21 else:22 for:23 freturn:24 function:25 goto:26 if:27 nreturn:28 return:29 struct:30 switch:31 while:32 Ident:38
- **nl, nl (as an argument), tab (as an argument)** (1): white:8
- **white** (1): White:12
- **epsilon, White** (1): Gray:13
- match `Src ? ...` line 267: bare Compiland

### parser_snobol4.sc — 91 named patterns: 50 folded, 41 not
- **epsilon** (32): Real:54 Id:61 FnArgList:95 FnArgTail:96 ExprList:97 XList:101 Expr0:103 Expr1:104 Expr2:105 Expr3:110 X3:111 Expr4:112 X4:113 Expr5:114 Expr6:115 Expr7:117 Expr8:118 Expr9:119 Expr10:120 Expr10:121 Expr11:126 X11:127 Expr12tail:129 Expr13:130 Expr15:148 Expr16:150 Expr17:153 Goto:192 StmtRepl:205 StmtGoto:207 Stmt:208 Commands:225
- **nl (as an argument)** (4): DQ:51 SQ:52 Control:199 Comment:200
- **epsilon, nl, tab (as an argument)** (1): White:63
- **epsilon, White** (1): Gray:67
- **nl (as an argument), tab (as an argument)** (1): StmtLabel:204
- **nl** (1): Command:226
- **epsilon, nl (as an argument), tab (as an argument)** (1): Compiland:231
- match `Src ? ...` line 253: bare Compiland

### parser_rebus.sc — 140 named patterns: 96 folded, 44 not
- **epsilon** (27): Id:12 KW_body:16 X_sub:113 X_args:114 call_or_id:115 postfix_expr:127 pow_expr:148 mul_tail:153 add_tail:159 cmp_expr:163 cat_tail:178 X_alt:182 alt_expr:183 expr:184 match_or_expr:192 return_stmt:206 caseclause_guard:218 caseclause_default:220 func_body_stmt:228 func_body:229 X_params:230 opt_params:231 X_fields:232 opt_fields:233 X_locals:234 func_cmd:247 rec_cmd:248
- **epsilon, nl** (6): opt_nl:196 compound_item:212 caselist_tail:222 stmt:225 opt_locals:235 opt_initial:237
- **nl** (6): compound_stmt:214 func_end:226 blank_line:227 function_decl:238 record_decl:244 blank:249
- **nl (as an argument), tab (as an argument)** (1): white:3
- **white** (1): White:8
- **epsilon, White** (1): Gray:9
- **KW_open** (1): primary:118
- **epsilon, Command** (1): Compiland:251
- match `Src ? ...` line 267: bare Compiland

### parser_icon.sc — 204 named patterns: 95 folded, 109 not
- **Id** (30): id_pat:18 if:29 then:30 else:31 while:32 do:33 every:34 return:35 end:36 procedure:37 until:38 repeat:39 break:40 next:41 case:42 of:43 default:44 to:45 by:46 global:47 local:48 static:49 record:50 initial:51 suspend:52 fail:53 not:54 create:55 link:56 invocable:57
- **epsilon** (21): Id:13 int_pat:19 semi_opt:28 $'<':98 $'>':99 If:137 While:142 Until:147 Every:152 ArgRest:161 ConjRest:171 ListRest:195 IdxStar:208 Expr8:276 X3:306 ToStar:308 Expr1:316 ReturnExpr:353 SuspendExpr:357 Expr1a:364 Compiland:445
- **semi_opt** (6): CompoundFirst:184 CompoundRest:185 CaseClause:228 CaseDefault:229 ReturnStmt:374 FailStmt:396
- **id_pat** (6): FieldTail:206 DeclFirst:377 DeclRest:378 ParamFirst:405 ParamRest:406 RecordField:424
- **epsilon, DeclIds, semi_opt** (3): LocalDecl:382 StaticDecl:383 GlobalDecl:420
- **epsilon, White** (2): Gray:10 CaseGray:227
- **epsilon, nl, tab (as an argument)** (2): strchars:26 csetchars:27
- **epsilon, semi_opt** (2): InitialStmt:384 SuspendStmt:388
- **epsilon, LinkName, semi_opt** (2): LinkDecl:436 InvocableDecl:440
- **epsilon, nl, nl (as an argument), tab (as an argument)** (1): white:4
- **epsilon, white** (1): White:9
- **exp_part** (1): real_pat:21
- **ArgRest** (1): NullFirst:162
- **epsilon, ArgFirst, ArgRest, NullFirst** (1): CallArgs:163
- **epsilon, CallArgs, id_pat** (1): Call:164
- **epsilon, ConjRest, SeqRest** (1): Paren:173
- **epsilon, CompoundRest** (1): CompoundStar:186
- **epsilon, CompoundFirst** (1): Compound:187
- **ListRest** (1): NullListFirst:196
- **epsilon, ListFirst, ListRest, NullListFirst** (1): ListCtor:197
- **epsilon, CallArgs, CoArg, FieldTail** (1): Expr11tail:211
- **epsilon, CaseClause, CaseDefault** (1): Case:230
- **Call, Case, Compound, Create, Every, Id, If, ListCtor, Paren, Repeat, Until, While, csetchars, id_pat, int_pat, real_pat, strchars, tab (as an argument)** (1): Expr11:240
- **epsilon, Expr11tail** (1): Expr11rest:269
- **epsilon, Expr9tail** (1): Expr9rest:275
- **epsilon, Expr7tail** (1): Expr7rest:283
- **epsilon, Expr6tail** (1): Expr6rest:290
- **epsilon, Expr5tail** (1): Expr5rest:293
- **epsilon, Expr4tail** (1): Expr4rest:305
- **epsilon, X3** (1): Expr3:307
- **ReturnExpr, SuspendExpr** (1): ExprSeqRest:365
- **epsilon, ExprSeqRest** (1): ExprSeqStar:366
- **epsilon, ReturnExpr, SuspendExpr** (1): Expr:367
- **epsilon, DeclRest** (1): DeclStar:379
- **DeclFirst** (1): DeclIds:380
- **FailStmt, InitialStmt, LocalDecl, ReturnStmt, StaticDecl, SuspendStmt, semi_opt** (1): StmtBody:397
- **epsilon, ParamFirst, ParamRest** (1): Params:407
- **Params, id_pat, semi_opt** (1): Prochead:408
- **ProcbodyEnd, StmtBody** (1): Procbody:413
- **epsilon, Procbody, Prochead** (1): Proc:415
- **epsilon, RecordField, id_pat** (1): Record:426
- **epsilon, id_pat** (1): LinkName:434
- **epsilon, LinkName** (1): LinkStar:435
- **epsilon, GlobalDecl, InvocableDecl, LinkDecl, Proc, Record** (1): TopStar:444
- match `Src ? ...` line 465: bare Compiland

### parser_prolog.sc — 116 named patterns: 66 folded, 50 not
- **epsilon** (26): Qchars:13 Float:19 op_infix:147 op_postfix:148 arg_ite:169 arg_disj:170 arg_top:171 args:172 args_tail:173 list_body_tail:174 list_body:175 list:177 is_expr:293 eq_expr:319 conj:347 conj_tail:353 conj_arrow:354 disj_tail:355 disj:356 dcg_conj:371 dcg_disj:377 dcg_conj_tail:383 dcg_disj_tail:384 dcg_push:387 dcg_rule:388 Compiland:405
- **epsilon, op_infix** (5): mul_tail:268 add_tail:281 colon_expr:287 cmp_expr:298 op_tail:326
- **X1xxxxxxx (as an argument)** (2): Atom_first:10 Atom_rest:11
- **epsilon, Graphic_first, Graphic_rest** (2): Graphic_atom:59 Graphic_atom2:60
- **nl, nl (as an argument), tab (as an argument)** (1): white:2
- **epsilon, white** (1): White:6
- **epsilon, White** (1): Gray:7
- **epsilon, Atom_first, Atom_rest** (1): Atom:12
- **epsilon, Var_first, Var_rest** (1): Var:18
- **nl (as an argument)** (1): Char_code:20
- **epsilon, nl (as an argument), tab (as an argument)** (1): Int:21
- **Atom, Graphic_atom** (1): uop_tok:145
- **Graphic_atom** (1): arg:168
- **epsilon, Atom, Float, Graphic_atom, Graphic_atom2, Int, Qatom, Str, Tk_cut, Var, bin_digits (as an argument), nl (as an argument)** (1): primary:192
- **epsilon, op_infix, op_postfix** (1): pow_expr:259
- **epsilon, Atom, Graphic_atom, Int, op_type** (1): op_goal:333
- **pfx_kw_name** (1): body_goal:340
- **Tk_cut** (1): dcg_goal:365
- **epsilon, head** (1): clause:392
- match `Src ? ...` line 422: bare Compiland

### parser_pascal.sc — 150 named patterns: 58 folded, 92 not
- **epsilon** (47): Id:44 Real:85 StrChars:97 swap:139 WriteArg:149 WriteCall:151 ProcCall:157 FuncCall:160 SetMember:164 SetTail:165 SetCtor:166 IdxTail:170 Postfix:172 PostStar:176 Primary:177 MulStar:207 AddStar:213 Expr0:222 StmtRest:231 StmtStar:234 compound_cmd:235 if_cmd:238 repeat_cmd:244 CaseConst:251 ConstStar:253 CaseArm:254 ArmStar:256 case_cmd:257 with_cmd:262 SConst:291 VariantTail:298 VariantPart:299 FieldList:301 TypeSpec:302 ConstDecls:313 TypeDecls:316 VarGroups:319 ParamFirst:322 Params:327 SubBody:331 proc_decl:333 ProcDecls:341 Decls:342 MainBody:348 program_head:350 main_decl:351 Compiland:356
- **Id** (41): and:45 begin:46 div:47 do:48 downto:49 else:50 end:51 false:52 for:53 function:54 if:55 mod:56 not:57 or:58 procedure:59 program:60 repeat:61 then:62 to:63 true:64 until:65 var:66 while:67 with:68 array:69 case:70 const:71 file:72 forward:73 goto:74 in:75 label:76 nil:77 of:78 packed:79 record:80 set:81 type:82 Ident:100 WriteName:145 WritelnName:147
- **cr (as an argument), nl (as an argument), tab (as an argument)** (1): white:36
- **epsilon, white** (1): White:40
- **epsilon, White** (1): Gray:41
- **epsilon, Id** (1): TypeName:288
- match `Src ? ...` line 379: bare Compiland

## Beside the grammars (the shared modules of the driver chain)

- `ShiftReduce.sc:3` -- `v ? (POS(0) whitespace) = ;` runs on EVERY Shift (every token); `whitespace` is assigned nowhere in `bootstrap/`, so the statement matches the null string at 0 and replaces it with the null string: a run-time match per token that changes nothing.
- `parser_snobol4.sc:120-121` -- `Expr10` is defined twice, byte-identical.
- `global.sc:18-21` -- `POS(128 + 64)` .. `POS(128 + 64 + 32 + 16 + 8)`: integer-literal arithmetic in a primitive argument is NOT folded by the lowerer (each is a run-time part; once, at start-up).
- Outside the parse clock (tree printing and quoting): `tdump.sc` 11 value-route patterns on a bare `fval`, `qize.sc` 9 match sites (`QizeWierd`, `bSlash`, `nl`, `cr`, `tab`, `CQize_ctrl32` as arguments or bare), `gen.sc` 3, `case.sc:21` (`icase`, `upr()`, `lwr()`), `match.sc:5,11` (the pattern parameter), `omega.sc:29,40`, `tree.sc:61-62` (`epsilon`), `tree.sc:74-76` (`t()`, `v()`, `n()` eager calls).
