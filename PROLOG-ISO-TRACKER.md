# PROLOG-ISO-TRACKER.md — mechanical coverage: SCRIP vs gprolog 1.4.5

**GENERATED — do not hand-edit.** Regenerate: `bash scripts/audit_prolog_iso_coverage.sh`
Source of truth: `refs/gprolog-master/src/BipsPl/*.pl` `set_bip_name/2` self-declarations.
Rung: GOAL-PROLOG-BB.md LADDER A → PL-ISO-10. **100% == UNASSIGNED 0 AND core-open 0.**

## Scoreboard

| metric | count |
|--------|-------|
| gprolog public exports (total) | 312 |
| DONE (SCRIP admits) | 128 (41%) |
| RUNG-ASSIGNED | 184 |
| **UNASSIGNED** | **0** |
| core scope | 237 |
| gprolog-ext scope | 75 |
| **core still open** | **110** |

## Per-file coverage

| file | scope | done | total | open |
|------|-------|------|-------|------|
| `stream.pl` | core | 14 | 43 | 29 |
| `os_interf.pl` | gprolog-ext | 0 | 35 | 35 |
| `const_io.pl` | core | 27 | 30 | 3 |
| `char_io.pl` | core | 24 | 28 | 4 |
| `src_rdr.pl` | core | 0 | 22 | 22 |
| `read.pl` | core | 4 | 17 | 13 |
| `atom.pl` | core | 11 | 15 | 4 |
| `dec10io.pl` | core | 5 | 12 | 7 |
| `write.pl` | core | 12 | 12 | 0 |
| `debugger.pl` | gprolog-ext | 0 | 11 | 11 |
| `term_inl.pl` | core | 5 | 11 | 6 |
| `sockets.pl` | gprolog-ext | 0 | 8 | 8 |
| `assert.pl` | core | 6 | 6 | 0 |
| `file.pl` | gprolog-ext | 0 | 6 | 6 |
| `flag.pl` | core | 2 | 6 | 4 |
| `sort.pl` | core | 3 | 6 | 3 |
| `stat.pl` | gprolog-ext | 0 | 6 | 6 |
| `pretty.pl` | core | 2 | 5 | 3 |
| `consult.pl` | core | 0 | 4 | 4 |
| `le_interf.pl` | gprolog-ext | 0 | 4 | 4 |
| `random.pl` | gprolog-ext | 0 | 4 | 4 |
| `arith_inl.pl` | core | 1 | 3 | 2 |
| `call.pl` | core | 0 | 3 | 3 |
| `control.pl` | core | 3 | 3 | 0 |
| `print.pl` | core | 2 | 3 | 1 |
| `format.pl` | core | 2 | 2 | 0 |
| `oper.pl` | core | 2 | 2 | 0 |
| `pred.pl` | core | 2 | 2 | 0 |
| `expand.pl` | core | 0 | 1 | 1 |
| `pl_error.pl` | core | 0 | 1 | 1 |
| `t.pl` | gprolog-ext | 1 | 1 | 0 |

## UNASSIGNED — no rung owns these (must reach 0)  (0)

*(none)*

## RUNG-ASSIGNED — owned, not yet landed  (184)

| predicate | file | scope | home |
|-----------|------|-------|------|
| `current_evaluable/1` | `arith_inl.pl` | core | PL-ISO-12 |
| `evaluable_property/2` | `arith_inl.pl` | core | PL-ISO-12 |
| `atom_property/2` | `atom.pl` | core | PL-ISO-4 |
| `current_atom/1` | `atom.pl` | core | PL-ISO-4 |
| `new_atom/1` | `atom.pl` | core | PL-ISO-4 |
| `new_atom/2` | `atom.pl` | core | PL-ISO-4 |
| `call_det/2` | `call.pl` | core | PL-ISO-12 |
| `call_nth/2` | `call.pl` | core | PL-ISO-12 |
| `countall/2` | `call.pl` | core | PL-ISO-12 |
| `get_key/1` | `char_io.pl` | core | PL-ISO-7b |
| `get_key/2` | `char_io.pl` | core | PL-ISO-7b |
| `get_key_no_echo/1` | `char_io.pl` | core | PL-ISO-7b |
| `get_key_no_echo/2` | `char_io.pl` | core | PL-ISO-7b |
| `read_token_from_atom/2` | `const_io.pl` | core | PL-ISO-7b |
| `read_token_from_chars/2` | `const_io.pl` | core | PL-ISO-7b |
| `read_token_from_codes/2` | `const_io.pl` | core | PL-ISO-7b |
| `listing/0` | `consult.pl` | core | PL-ISO-13 |
| `listing/1` | `consult.pl` | core | PL-ISO-13 |
| `load/1` | `consult.pl` | core | PL-ISO-13 |
| `write_default_include_file/1` | `consult.pl` | core | PL-ISO-13 |
| `debug/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `debugging/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `leash/1` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `nodebug/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `nospy/1` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `nospyall/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `notrace/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `spy/1` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `spypoint_condition/3` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `trace/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `wam_debug/0` | `debugger.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `append/1` | `dec10io.pl` | core | PL-ISO-7b |
| `see/1` | `dec10io.pl` | core | PL-ISO-7b |
| `seeing/1` | `dec10io.pl` | core | PL-ISO-7b |
| `seen/0` | `dec10io.pl` | core | PL-ISO-7b |
| `tell/1` | `dec10io.pl` | core | PL-ISO-7b |
| `telling/1` | `dec10io.pl` | core | PL-ISO-7b |
| `told/0` | `dec10io.pl` | core | PL-ISO-7b |
| `expand_term/2` | `expand.pl` | core | PL-ISO-13 |
| `absolute_file_name/2` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `decompose_file_name/4` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `is_absolute_file_name/1` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `is_relative_file_name/1` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `prolog_file_name/2` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `prolog_file_suffix/1` | `file.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `argument_counter/1` | `flag.pl` | core | PL-ISO-12 |
| `argument_list/1` | `flag.pl` | core | PL-ISO-12 |
| `argument_value/2` | `flag.pl` | core | PL-ISO-12 |
| `environ/2` | `flag.pl` | core | PL-ISO-12 |
| `add_linedit_completion/1` | `le_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `find_linedit_completion/2` | `le_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `get_linedit_prompt/1` | `le_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `set_linedit_prompt/1` | `le_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `architecture/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `change_directory/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `copy_file/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `create_pipe/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `date_time/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `delete_directory/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `delete_file/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `directory_files/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `exec/4` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `exec/5` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `file_exists/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `file_permission/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `file_property/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `fork_prolog/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `host_name/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `make_directory/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `os_version/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `popen/3` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `prolog_pid/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `rename_file/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `select/5` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `send_signal/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `shell/0` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `shell/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `shell/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `sleep/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `spawn/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `spawn/3` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `system/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `system/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `temporary_file/3` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `temporary_name/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `unlink/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `wait/2` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `working_directory/1` | `os_interf.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `syntax_error_info/4` | `pl_error.pl` | core | PL-ISO-13 |
| `bind_variables/2` | `pretty.pl` | core | PL-ISO-9 |
| `name_query_vars/2` | `pretty.pl` | core | PL-ISO-9 |
| `name_singleton_vars/1` | `pretty.pl` | core | PL-ISO-9 |
| `get_print_stream/1` | `print.pl` | core | PL-ISO-9 |
| `get_seed/1` | `random.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `random/1` | `random.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `random/3` | `random.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `set_seed/1` | `random.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `char_conversion/2` | `read.pl` | core | PL-ISO-7a |
| `current_char_conversion/2` | `read.pl` | core | PL-ISO-7a |
| `last_read_start_line_column/2` | `read.pl` | core | PL-ISO-7a |
| `read_atom/1` | `read.pl` | core | PL-ISO-7a |
| `read_atom/2` | `read.pl` | core | PL-ISO-7a |
| `read_integer/1` | `read.pl` | core | PL-ISO-7a |
| `read_integer/2` | `read.pl` | core | PL-ISO-7a |
| `read_line_to_chars/2` | `read.pl` | core | PL-ISO-7a |
| `read_line_to_codes/2` | `read.pl` | core | PL-ISO-7a |
| `read_number/1` | `read.pl` | core | PL-ISO-7a |
| `read_number/2` | `read.pl` | core | PL-ISO-7a |
| `read_token/1` | `read.pl` | core | PL-ISO-7a |
| `read_token/2` | `read.pl` | core | PL-ISO-7a |
| `hostname_address/2` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket/2` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket_accept/3` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket_accept/4` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket_bind/2` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket_close/1` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket_connect/4` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `socket_listen/2` | `sockets.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `keysort/1` | `sort.pl` | core | PL-ISO-11 |
| `msort/1` | `sort.pl` | core | PL-ISO-11 |
| `sort/1` | `sort.pl` | core | PL-ISO-11 |
| `sr_change_options/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_close/1` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_current_descriptor/1` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_error_from_exception/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_error_counters/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_file_name/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_include_list/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_include_stream_list/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_module/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_position/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_size_counters/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_get_stream/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_new_pass/1` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_open/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_read_term/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_set_error_counters/3` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_write_error/2` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_write_error/4` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_write_error/6` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_write_message/4` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_write_message/6` | `src_rdr.pl` | core | PL-ISO-7b |
| `sr_write_message/8` | `src_rdr.pl` | core | PL-ISO-7b |
| `cpu_time/1` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `real_time/1` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `statistics/0` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `statistics/2` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `system_time/1` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `user_time/1` | `stat.pl` | gprolog-ext | PL-EXT (out of PL-100 core scope) |
| `add_stream_alias/2` | `stream.pl` | core | PL-ISO-7b |
| `add_stream_mirror/2` | `stream.pl` | core | PL-ISO-7b |
| `character_count/2` | `stream.pl` | core | PL-ISO-7b |
| `close_input_atom_stream/1` | `stream.pl` | core | PL-ISO-7b |
| `close_input_chars_stream/1` | `stream.pl` | core | PL-ISO-7b |
| `close_input_codes_stream/1` | `stream.pl` | core | PL-ISO-7b |
| `close_output_atom_stream/2` | `stream.pl` | core | PL-ISO-7b |
| `close_output_chars_stream/2` | `stream.pl` | core | PL-ISO-7b |
| `close_output_codes_stream/2` | `stream.pl` | core | PL-ISO-7b |
| `current_alias/2` | `stream.pl` | core | PL-ISO-7b |
| `current_mirror/2` | `stream.pl` | core | PL-ISO-7b |
| `line_count/2` | `stream.pl` | core | PL-ISO-7b |
| `line_position/2` | `stream.pl` | core | PL-ISO-7b |
| `open_input_atom_stream/2` | `stream.pl` | core | PL-ISO-7b |
| `open_input_chars_stream/2` | `stream.pl` | core | PL-ISO-7b |
| `open_input_codes_stream/2` | `stream.pl` | core | PL-ISO-7b |
| `open_output_atom_stream/1` | `stream.pl` | core | PL-ISO-7b |
| `open_output_chars_stream/1` | `stream.pl` | core | PL-ISO-7b |
| `open_output_codes_stream/1` | `stream.pl` | core | PL-ISO-7b |
| `remove_stream_mirror/2` | `stream.pl` | core | PL-ISO-7b |
| `seek/4` | `stream.pl` | core | PL-ISO-7b |
| `set_stream_alias/2` | `stream.pl` | core | PL-ISO-7b |
| `set_stream_buffering/2` | `stream.pl` | core | PL-ISO-7b |
| `set_stream_eof_action/2` | `stream.pl` | core | PL-ISO-7b |
| `set_stream_line_column/3` | `stream.pl` | core | PL-ISO-7b |
| `set_stream_position/2` | `stream.pl` | core | PL-ISO-7b |
| `set_stream_type/2` | `stream.pl` | core | PL-ISO-7b |
| `stream_line_column/3` | `stream.pl` | core | PL-ISO-7b |
| `stream_position/2` | `stream.pl` | core | PL-ISO-7b |
| `nb_setarg/3` | `term_inl.pl` | core | PL-ISO-11 |
| `setarg/3` | `term_inl.pl` | core | PL-ISO-11 |
| `setarg/4` | `term_inl.pl` | core | PL-ISO-11 |
| `term_hash/2` | `term_inl.pl` | core | PL-ISO-11 |
| `term_hash/4` | `term_inl.pl` | core | PL-ISO-11 |
| `term_ref/2` | `term_inl.pl` | core | PL-ISO-11 |

## DONE — admitted by SCRIP  (128)

| predicate | file | scope | home |
|-----------|------|-------|------|
| `succ/2` | `arith_inl.pl` | core |  |
| `abolish/1` | `assert.pl` | core |  |
| `asserta/1` | `assert.pl` | core |  |
| `assertz/1` | `assert.pl` | core |  |
| `clause/2` | `assert.pl` | core |  |
| `retract/1` | `assert.pl` | core |  |
| `retractall/1` | `assert.pl` | core |  |
| `atom_chars/2` | `atom.pl` | core |  |
| `atom_codes/2` | `atom.pl` | core |  |
| `atom_concat/3` | `atom.pl` | core |  |
| `atom_length/2` | `atom.pl` | core |  |
| `char_code/2` | `atom.pl` | core |  |
| `lower_upper/2` | `atom.pl` | core |  |
| `name/2` | `atom.pl` | core |  |
| `number_atom/2` | `atom.pl` | core |  |
| `number_chars/2` | `atom.pl` | core |  |
| `number_codes/2` | `atom.pl` | core |  |
| `sub_atom/5` | `atom.pl` | core |  |
| `get_byte/1` | `char_io.pl` | core |  |
| `get_byte/2` | `char_io.pl` | core |  |
| `get_char/1` | `char_io.pl` | core |  |
| `get_char/2` | `char_io.pl` | core |  |
| `get_code/1` | `char_io.pl` | core |  |
| `get_code/2` | `char_io.pl` | core |  |
| `peek_byte/1` | `char_io.pl` | core |  |
| `peek_byte/2` | `char_io.pl` | core |  |
| `peek_char/1` | `char_io.pl` | core |  |
| `peek_char/2` | `char_io.pl` | core |  |
| `peek_code/1` | `char_io.pl` | core |  |
| `peek_code/2` | `char_io.pl` | core |  |
| `put_byte/1` | `char_io.pl` | core |  |
| `put_byte/2` | `char_io.pl` | core |  |
| `put_char/1` | `char_io.pl` | core |  |
| `put_char/2` | `char_io.pl` | core |  |
| `put_code/1` | `char_io.pl` | core |  |
| `put_code/2` | `char_io.pl` | core |  |
| `unget_byte/1` | `char_io.pl` | core |  |
| `unget_byte/2` | `char_io.pl` | core |  |
| `unget_char/1` | `char_io.pl` | core |  |
| `unget_char/2` | `char_io.pl` | core |  |
| `unget_code/1` | `char_io.pl` | core |  |
| `unget_code/2` | `char_io.pl` | core |  |
| `display_to_atom/2` | `const_io.pl` | core |  |
| `display_to_chars/2` | `const_io.pl` | core |  |
| `display_to_codes/2` | `const_io.pl` | core |  |
| `format_to_atom/3` | `const_io.pl` | core |  |
| `format_to_chars/3` | `const_io.pl` | core |  |
| `format_to_codes/3` | `const_io.pl` | core |  |
| `print_to_atom/2` | `const_io.pl` | core |  |
| `print_to_chars/2` | `const_io.pl` | core |  |
| `print_to_codes/2` | `const_io.pl` | core |  |
| `read_from_atom/2` | `const_io.pl` | core |  |
| `read_from_chars/2` | `const_io.pl` | core |  |
| `read_from_codes/2` | `const_io.pl` | core |  |
| `read_term_from_atom/3` | `const_io.pl` | core |  |
| `read_term_from_chars/3` | `const_io.pl` | core |  |
| `read_term_from_codes/3` | `const_io.pl` | core |  |
| `write_canonical_to_atom/2` | `const_io.pl` | core |  |
| `write_canonical_to_chars/2` | `const_io.pl` | core |  |
| `write_canonical_to_codes/2` | `const_io.pl` | core |  |
| `write_term_to_atom/3` | `const_io.pl` | core |  |
| `write_term_to_chars/3` | `const_io.pl` | core |  |
| `write_term_to_codes/3` | `const_io.pl` | core |  |
| `write_to_atom/2` | `const_io.pl` | core |  |
| `write_to_chars/2` | `const_io.pl` | core |  |
| `write_to_codes/2` | `const_io.pl` | core |  |
| `writeq_to_atom/2` | `const_io.pl` | core |  |
| `writeq_to_chars/2` | `const_io.pl` | core |  |
| `writeq_to_codes/2` | `const_io.pl` | core |  |
| `between/3` | `control.pl` | core |  |
| `for/3` | `control.pl` | core |  |
| `halt/1` | `control.pl` | core |  |
| `get/1` | `dec10io.pl` | core |  |
| `get0/1` | `dec10io.pl` | core |  |
| `put/1` | `dec10io.pl` | core |  |
| `skip/1` | `dec10io.pl` | core |  |
| `tab/1` | `dec10io.pl` | core |  |
| `current_prolog_flag/2` | `flag.pl` | core |  |
| `set_prolog_flag/2` | `flag.pl` | core |  |
| `format/2` | `format.pl` | core |  |
| `format/3` | `format.pl` | core |  |
| `current_op/3` | `oper.pl` | core |  |
| `op/3` | `oper.pl` | core |  |
| `current_predicate/1` | `pred.pl` | core |  |
| `predicate_property/2` | `pred.pl` | core |  |
| `numbervars/1` | `pretty.pl` | core |  |
| `numbervars/3` | `pretty.pl` | core |  |
| `print/1` | `print.pl` | core |  |
| `print/2` | `print.pl` | core |  |
| `read/1` | `read.pl` | core |  |
| `read/2` | `read.pl` | core |  |
| `read_term/2` | `read.pl` | core |  |
| `read_term/3` | `read.pl` | core |  |
| `keysort/2` | `sort.pl` | core |  |
| `msort/2` | `sort.pl` | core |  |
| `sort/2` | `sort.pl` | core |  |
| `at_end_of_stream/0` | `stream.pl` | core |  |
| `at_end_of_stream/1` | `stream.pl` | core |  |
| `close/1` | `stream.pl` | core |  |
| `close/2` | `stream.pl` | core |  |
| `current_input/1` | `stream.pl` | core |  |
| `current_output/1` | `stream.pl` | core |  |
| `current_stream/1` | `stream.pl` | core |  |
| `flush_output/0` | `stream.pl` | core |  |
| `flush_output/1` | `stream.pl` | core |  |
| `open/3` | `stream.pl` | core |  |
| `open/4` | `stream.pl` | core |  |
| `set_input/1` | `stream.pl` | core |  |
| `set_output/1` | `stream.pl` | core |  |
| `stream_property/2` | `stream.pl` | core |  |
| `setup_call_cleanup/3` | `t.pl` | gprolog-ext |  |
| `acyclic_term/1` | `term_inl.pl` | core |  |
| `copy_term/2` | `term_inl.pl` | core |  |
| `subsumes_term/2` | `term_inl.pl` | core |  |
| `term_variables/2` | `term_inl.pl` | core |  |
| `term_variables/3` | `term_inl.pl` | core |  |
| `display/1` | `write.pl` | core |  |
| `display/2` | `write.pl` | core |  |
| `nl/0` | `write.pl` | core |  |
| `nl/1` | `write.pl` | core |  |
| `write/1` | `write.pl` | core |  |
| `write/2` | `write.pl` | core |  |
| `write_canonical/1` | `write.pl` | core |  |
| `write_canonical/2` | `write.pl` | core |  |
| `write_term/2` | `write.pl` | core |  |
| `write_term/3` | `write.pl` | core |  |
| `writeq/1` | `write.pl` | core |  |
| `writeq/2` | `write.pl` | core |  |

