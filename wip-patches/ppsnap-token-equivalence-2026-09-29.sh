#!/usr/bin/env bash
# ppsnap.sh <tag> [files...] -- preprocess each file at RT_DIAG=0 and =1 with the Makefile's runtime includes, all white space removed
T=/home/satirical/.claude/jobs/ef0b4539/tmp; N=${ROOT:-/home/claude_ceo/SCRIP}; tag=$1; shift; mkdir -p $T/pp/$tag
S=$N/src; RT=$S/runtime; INC="-I$S -I$S/ir -I$S/lower -I$S/emitter -I$S/runtime/core -I$S/runtime/builtins -I$RT -I$RT/rt -I$S/parsers/snobol4 -I$S/parsers/raku -I$S/optimizer -I$S/templates/bb -I$S/templates/xa -I$S/templates/x86"
for f in "$@"; do case $f in *.cpp) l="-x c++ -std=c++17";; *.s) l="-x assembler-with-cpp";; *) l="-x c";; esac; b=$(echo $f | tr / _)
  for D in 0 1; do (cd $N && gcc -E -P $l -DRT_DIAG=$D $INC $f 2>/dev/null) | sed -E 's/(rt_gc_cb_close\(_cb_m, "[^"]*", )[0-9]+/\1LINE/g' | tr -d ' \t\n' > $T/pp/$tag/$b.$D; done
  echo "$tag $f d0=$(md5sum < $T/pp/$tag/$b.0 | cut -c1-12) d1=$(md5sum < $T/pp/$tag/$b.1 | cut -c1-12)"; done
