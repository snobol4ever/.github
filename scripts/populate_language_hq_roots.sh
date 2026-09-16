#!/usr/bin/env bash
# populate_language_hq_roots.sh -- CEO-767 (2026-09-16): the six language HQ roots Lon renamed (Lon, in-chat to ceo:
# "I will rename the folders from claude_C, claude_P, etc to be by language." / "I have all folders in /home ready for
# you to populate.") take their new identities: root /home/claude_<lang>, postoffice identity hq_<lang>.
#   icon <- claude_B (hq_B) · prolog <- claude_C (hq_C, hq_R folds in) · raku <- claude_T (hq_T) · pascal <- claude_S (hq_S)
#   snocone <- claude_I (hq_I) · snobol4 <- claude_P (hq_P) · hq_U folds into the cto · hq_V folds into the cfo
# Per root: the three repos fast-forwarded to origin (the bus, the hook and the gates already carry the new map on
# origin, SCRIP commit named in GOAL-CEO CEO-767); SCRIP/refs deleted (Lon 2026-09-16, CEO-765); the two hooks in
# .claude/settings*.json re-pointed at the new root; CLAUDE.md backed up and its OWN old identity and path rewritten,
# with a rename banner prepended (other seats' historical names stay as history). Postoffice: hq_<lang>/{inbox,archive}
# and an HQ file naming the officer; the legacy box's mail moved into the new box and the legacy box marked DRAINED
# naming its successor. QUEUE.tsv: every owner cell and ASSIGNED: state carrying a legacy identity rewritten to the
# successor; FREE rows re-laned by language prefix to their HQ; a handful of parked concern rows un-parked to the
# officer whose concern they are. Backups beside everything it touches. Idempotent: re-running changes nothing.
#   bash /home/claude_ceo/.github/scripts/populate_language_hq_roots.sh
# rc 0 = populated and verified by the three lane gates · rc 2 = refused, nothing half-done is hidden.
set -u
CEO=/home/claude_ceo; PO=/home/resources/postoffice; STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
declare -A OLD=([icon]=B [prolog]=C [raku]=T [pascal]=S [snocone]=I [snobol4]=P)
declare -A OFFICER=([icon]=cfo [prolog]=cto [raku]=cto [pascal]=cfo [snocone]=cfo [snobol4]=cfo)
declare -A LANGUC=([icon]=ICON [prolog]=PROLOG [raku]=RAKU [pascal]=PASCAL [snocone]=SNOCONE [snobol4]=SNOBOL4)
refuse(){ echo "REFUSED rc=2: $*"; exit 2; }
for lang in icon prolog raku pascal snocone snobol4; do
  R=/home/claude_$lang; o=${OLD[$lang]}; new=hq_$lang; old=hq_$o; off=${OFFICER[$lang]}
  [ -d "$R" ] || refuse "$R does not exist -- Lon creates the root"
  for r in SCRIP corpus .github; do
    [ -d "$R/$r/.git" ] || refuse "$R/$r is not a git repo"
    git -C "$R/$r" config user.name  LCherryholmes
    git -C "$R/$r" config user.email lcherryh@yahoo.com
    git -C "$R/$r" fetch -q origin || refuse "fetch of $R/$r failed"
    git -C "$R/$r" merge -q --ff-only origin/main || refuse "$R/$r did not fast-forward to origin/main (local commits? save them outside the root first)"
  done
  rm -rf "$R/SCRIP/refs"
  for f in "$R/.claude/settings.local.json" "$R/.claude/settings.json"; do
    [ -f "$f" ] || continue
    if grep -q "/home/claude_$o/" "$f"; then cp -p "$f" "$f.bak-$STAMP-rename"; sed -i "s|/home/claude_$o/|/home/claude_$lang/|g" "$f"; fi
  done
  if ! grep -q "RENAMED BY LANGUAGE 2026-09-16" "$R/CLAUDE.md"; then
    cp -p "$R/CLAUDE.md" "$R/CLAUDE.md.bak-$STAMP-rename-$lang"
    python3 - "$R/CLAUDE.md" "$old" "$new" "/home/claude_$o" "$R" "$lang" "$off" "${LANGUC[$lang]}" <<'PY'
import re, sys
p, old, new, oldroot, newroot, lang, off, LU = sys.argv[1:]
t = open(p, "rb").read().decode("utf-8")
t = re.sub(r"\b" + re.escape(old) + r"\b", new, t)
t = t.replace(oldroot + "/", newroot + "/").replace(oldroot + "`", newroot + "`").replace(oldroot + " ", newroot + " ").replace(oldroot + ")", newroot + ")")
banner = ("\n⛔⭐⭐⭐ **RENAMED BY LANGUAGE 2026-09-16 (Lon, in-chat to ceo; ceo CEO-767): THIS ROOT IS `%s`, IDENTITY `%s` (was `%s` at `%s`). "
          "MODE line 1 reads `DECTET`: six language HQs (Claude Opus 5) and four officers (Claude Fable 5.1). YOUR LANE IS %s, ALL THREE AXES -- completeness "
          "(the master and every package suite to FAIL=0 over the printed denominator, the ladder walked, each red ablated to a witness on its rung), then SPEED on the "
          "kernel convention and the two-number three-angle basis. Your cursor is `.github/GOAL-%s-100.md`; your officer is `%s` (postoffice `HQ` file) -- a change to any "
          "node another language lowers to (the spine, a shared box, the collector, the three zetas) is an ASK to your officer with the measurement, base-vs-head gate by "
          "gate, never a landing. Read MODE line 2 whole every sitting; every `%s` and `%s` below is history. `SCRIP/refs/` is deleted (read `/home/resources/` directly); "
          "the 09-15 reboot emptied the build cache, so your first `make` is a full rebuild and a runner before it refuses rc=2.**\n"
          % (newroot, new, old, oldroot, LU, LU, off, old, oldroot))
lines = t.split("\n")
i = next((k for k, l in enumerate(lines) if l.strip() == "# CLAUDE.md"), 0)
lines.insert(i + 1, banner)
open(p, "wb").write("\n".join(lines).encode("utf-8"))
print("digest rewritten:", p)
PY
  fi
  mkdir -p "$PO/$new/inbox" "$PO/$new/archive"
  printf '%s\n' "$off" > "$PO/$new/HQ"
  for src in "$old" $([ "$lang" = prolog ] && echo hq_R); do
    [ -d "$PO/$src/inbox" ] || continue
    for m in "$PO/$src/inbox/"*; do [ -f "$m" ] && mv "$m" "$PO/$new/inbox/"; done
    [ -f "$PO/$src/DRAINED" ] || printf 'DRAINED %s: renamed to %s on 2026-09-16 (ceo CEO-767, Lon renamed the roots by language); its mail moved to %s/inbox\n' "$src" "$new" "$new" > "$PO/$src/DRAINED"
  done
  printf '%-8s root=%s identity=%s officer=%s SCRIP=%s inbox=%s\n' "$lang" "$R" "$new" "$off" "$(git -C "$R/SCRIP" rev-parse --short=9 HEAD)" "$(ls "$PO/$new/inbox" | wc -l)"
done
for pair in hq_U:cto hq_V:cfo; do src=${pair%%:*}; dst=${pair##*:}
  [ -d "$PO/$src/inbox" ] || continue
  for m in "$PO/$src/inbox/"*; do [ -f "$m" ] && mv "$m" "$PO/$dst/inbox/"; done
  [ -f "$PO/$src/DRAINED" ] || printf 'DRAINED %s: its concern folded into the %s on 2026-09-16 (ceo CEO-767); its mail moved to %s/inbox\n' "$src" "$dst" "$dst" > "$PO/$src/DRAINED"
done
python3 - "$PO/QUEUE.tsv" "$STAMP" <<'PY'
import re, shutil, sys
Q, stamp = sys.argv[1:]
succ = {"hq_B": "hq_icon", "hq_C": "hq_prolog", "hq_R": "hq_prolog", "hq_T": "hq_raku", "hq_S": "hq_pascal", "hq_I": "hq_snocone", "hq_P": "hq_snobol4", "hq_U": "cto", "hq_V": "cfo"}
lane = [(r"^(icon|icn)-", "hq_icon"), (r"^(prolog|pl|swi|inria|logtalk|gnu)-", "hq_prolog"), (r"^(raku|roast)-", "hq_raku"),
        (r"^(pascal|pas|fpc|pat)-", "hq_pascal"), (r"^(snocone|snc)-", "hq_snocone"), (r"^(snobol4|sno|spitbol|gimpel|snoflake|csnobol4|ais)-", "hq_snobol4"), (r"^rebus-", "cfo")]
unpark = [(r"^(emit|zeta|engine|frame)-|-frame-|-zeta-|-spine-", "cto"), (r"^(gc|heap|collector)-|-gc-|-heap-|-collector-", "cfo")]
data = open(Q, "rb").read()
assert b"\r" not in data
lines = data.decode("utf-8").split("\n")
n_id = n_lane = n_unpark = 0
out = []
for l in lines:
    f = l.split("\t")
    if len(f) >= 4 and not f[0].startswith("#"):
        if f[2] in succ: f[2] = succ[f[2]]; n_id += 1
        for k, v in succ.items():
            if re.search(r"\b" + k + r"\b", f[3]): f[3] = re.sub(r"\b" + k + r"\b", v, f[3]); n_id += 1
        if f[3] == "FREE":
            for rx, o in lane:
                if re.match(rx, f[1]) and f[2] != o: f[2] = o; n_lane += 1; break
        elif f[3] == "PARKED-EXECUTIVE-NO-SEAT":
            for rx, o in unpark:
                if re.search(rx, f[1]): f[2] = o; f[3] = "FREE"; n_unpark += 1; break
        l = "\t".join(f)
    out.append(l)
new = "\n".join(out).encode("utf-8")
if new != data:
    shutil.copy2(Q, Q + ".bak.ceo-767-" + stamp)
    open(Q, "wb").write(new)
print("QUEUE: legacy identities rewritten %d, FREE rows re-laned %d, concern rows un-parked %d" % (n_id, n_lane, n_unpark))
PY
echo "--- verification (from the ceo clone, which carries the new map) ---"
cd "$CEO/SCRIP" || refuse "ceo SCRIP missing"
rc=0
for g in test_gate_seat_identity_one_map.sh test_gate_picker_lane_table_agrees_with_mode.sh test_gate_mode_line2_is_self_consistent.sh; do
  printf '%-52s ' "$g"; if timeout 180s bash "scripts/$g" >/dev/null 2>&1; then echo OK; else echo "RED rc=$?"; rc=2; fi
done
for lang in icon prolog raku pascal snocone snobol4; do
  ( cd "/home/claude_$lang/SCRIP" && printf '%-8s bus says: ' "$lang" && bash scripts/s4e_msg.sh check 2>/dev/null | head -1 )
done
exit $rc
