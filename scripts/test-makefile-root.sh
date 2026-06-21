#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/screenshare-root-control-XXXXXX")
ATTACKER_ROOT="$TEMP_ROOT/attacker-root"
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES ROOT PYTHON XCODEBUILD PYTHONDONTWRITEBYTECODE

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/screenshare's [gate] \"quoted\" \`touch SCREENSHARE_BACKTICK_MARKER\`"
COMMAND_LOG="$TEMP_ROOT/commands.log"
BAD_COMMAND_LOG="$TEMP_ROOT/bad-command.log"
FAKE_SHELL_LOG="$TEMP_ROOT/fake-shell.log"
PATH_SHADOW_LOG="$TEMP_ROOT/path-shadow.log"
export SCREENSHARE_PATH_SHADOW_LOG="$PATH_SHADOW_LOG"
mkdir "$CONTROL_DIR" "$CHECKOUT" "$CHECKOUT/scripts" "$CHECKOUT/bin" "$ATTACKER_ROOT"
CONTROL_DIR=$(CDPATH= cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"
printf '%s\n' '#!/bin/sh' 'exit 0' >"$CHECKOUT/build.sh"
chmod +x "$CHECKOUT/build.sh"

for command in python3 xcodebuild; do
  cat >"$CHECKOUT/bin/$command" <<'EOF'
#!/bin/sh
printf '%s\n' invoked >> "$SCREENSHARE_PATH_SHADOW_LOG"
EOF
  chmod +x "$CHECKOUT/bin/$command"
done
for command in run-python.sh run-xcodebuild.sh; do
  cat >"$CHECKOUT/scripts/$command" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|%s\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" "$*" >> "$SCREENSHARE_COMMAND_LOG"
EOF
  chmod +x "$CHECKOUT/scripts/$command"
done
cat >"$CHECKOUT/scripts/test-makefile-root.sh" <<'EOF'
#!/bin/sh
printf '%s|%s|%s|root-test\n' "$PWD" "$0" "${PYTHONDONTWRITEBYTECODE:-}" >> "$SCREENSHARE_COMMAND_LOG"
EOF
chmod +x "$CHECKOUT/scripts/test-makefile-root.sh"

BAD_COMMAND="$TEMP_ROOT/bad-command"
cat >"$BAD_COMMAND" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$BAD_COMMAND_LOG'
exit 91
EOF
chmod +x "$BAD_COMMAND"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
cat >"$FAKE_SHELL" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$FAKE_SHELL_LOG'
exec /bin/sh "\$@"
EOF
chmod +x "$FAKE_SHELL"

assert_commands_stayed_in_checkout() {
  scenario=$1
  target=$2
  if [ ! -s "$COMMAND_LOG" ]; then
    printf '%s\n' "$scenario $target executed no quality command" >&2
    exit 1
  fi
  while IFS= read -r command; do
    case "$command" in
      "$CONTROL_DIR|"*"$CHECKOUT"*"|1|"*) ;;
      "$CHECKOUT|"*"|1|"*) ;;
      *)
        printf '%s\n' "$scenario $target escaped the checkout or enabled bytecode: $command" >&2
        exit 1
        ;;
    esac
  done <"$COMMAND_LOG"
}

run_case() {
  scenario=$1
  target=$2
  mode=$3
  rm -f "$COMMAND_LOG" "$BAD_COMMAND_LOG" "$FAKE_SHELL_LOG" "$PATH_SHADOW_LOG"
  output="$TEMP_ROOT/output"
  set +e
  case "$mode" in
    default)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-root)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "ROOT=$ATTACKER_ROOT" "$target") >"$output" 2>&1 ;;
    environment-root)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" ROOT="$ATTACKER_ROOT" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-shell)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "SHELL=$FAKE_SHELL" "$target") >"$output" 2>&1 ;;
    environment-shell)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SHELL="$FAKE_SHELL" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-flags)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" '.SHELLFLAGS=-eu -c' "$target") >"$output" 2>&1 ;;
    environment-flags)
      (cd "$CONTROL_DIR" && env '.SHELLFLAGS=-eu -c' PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-python)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$BAD_COMMAND" "$target") >"$output" 2>&1 ;;
    environment-python)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" PYTHON="$BAD_COMMAND" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    command-xcodebuild)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "XCODEBUILD=$BAD_COMMAND" "$target") >"$output" 2>&1 ;;
    environment-xcodebuild)
      (cd "$CONTROL_DIR" && PATH="$CHECKOUT/bin:$PATH" XCODEBUILD="$BAD_COMMAND" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "$target") >"$output" 2>&1 ;;
    *)
      printf '%s\n' "unknown test mode: $mode" >&2
      exit 1 ;;
  esac
  result=$?
  set -e
  if [ "$result" -ne 0 ]; then
    printf '%s\n' "$scenario $target failed" >&2
    cat "$output" >&2
    exit 1
  fi
  assert_commands_stayed_in_checkout "$scenario" "$target"
  if [ -e "$BAD_COMMAND_LOG" ]; then
    printf '%s\n' "$scenario $target executed caller-controlled Python or xcodebuild" >&2
    exit 1
  fi
  if [ -e "$FAKE_SHELL_LOG" ]; then
    printf '%s\n' "$scenario $target executed caller-controlled shell" >&2
    exit 1
  fi
  if [ -e "$PATH_SHADOW_LOG" ]; then
    printf '%s\n' "$scenario $target executed a PATH-shadowed Python or xcodebuild" >&2
    exit 1
  fi
}

for target in build check lint root-test test verify; do
  run_case default "$target" default
  run_case command-root "$target" command-root
  run_case environment-root "$target" environment-root
  run_case command-shell "$target" command-shell
  run_case environment-shell "$target" environment-shell
  run_case command-flags "$target" command-flags
  run_case environment-flags "$target" environment-flags
  run_case command-python "$target" command-python
  run_case environment-python "$target" environment-python
  run_case command-xcodebuild "$target" command-xcodebuild
  run_case environment-xcodebuild "$target" environment-xcodebuild
done

DOLLAR_CHECKOUT="$TEMP_ROOT/screenshare \$(touch SCREENSHARE_DOLLAR_MARKER)"
mkdir "$DOLLAR_CHECKOUT" "$DOLLAR_CHECKOUT/scripts"
DOLLAR_CHECKOUT=$(CDPATH= cd -- "$DOLLAR_CHECKOUT" && /bin/pwd -P)
cp "$MAKEFILE" "$DOLLAR_CHECKOUT/Makefile"
cp "$CHECKOUT/build.sh" "$DOLLAR_CHECKOUT/build.sh"
cp "$CHECKOUT/scripts/run-python.sh" "$DOLLAR_CHECKOUT/scripts/run-python.sh"
rm -f "$COMMAND_LOG" "$PATH_SHADOW_LOG"
(cd "$DOLLAR_CHECKOUT" && PATH="$CHECKOUT/bin:$PATH" SCREENSHARE_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory lint) >"$TEMP_ROOT/dollar-path.out" 2>&1
case "$(cat "$COMMAND_LOG")" in
  "$DOLLAR_CHECKOUT|$DOLLAR_CHECKOUT/scripts/run-python.sh|1|"*) ;;
  *)
    printf '%s\n' "dollar-syntax checkout escaped repository-owned Python: $(cat "$COMMAND_LOG")" >&2
    exit 1 ;;
esac
if [ -e "$DOLLAR_CHECKOUT/SCREENSHARE_DOLLAR_MARKER" ] || [ -e "$PATH_SHADOW_LOG" ]; then
  printf '%s\n' "dollar-syntax checkout executed command syntax or a PATH-shadowed tool" >&2
  exit 1
fi

if [ -e "$CONTROL_DIR/SCREENSHARE_BACKTICK_MARKER" ]; then
  printf '%s\n' "checkout path executed a command substitution" >&2
  exit 1
fi

if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/command-list.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/command-list.out"
if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted /usr/bin/make --environment-overrides --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/environment-list.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/environment-list.out"
PRELOADED="$TEMP_ROOT/preloaded.mk"
printf '%s\n' 'ROOT := /tmp/preloaded' >"$PRELOADED"
if (cd "$CONTROL_DIR" && MAKEFILES="$PRELOADED" /usr/bin/make --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/preloaded.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILES must be empty" "$TEMP_ROOT/preloaded.out"
EARLIER="$TEMP_ROOT/earlier.mk"
printf '%s\n' '# earlier' >"$EARLIER"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$EARLIER" --file "$MAKEFILE" check) >"$TEMP_ROOT/multiple.out" 2>&1; then exit 1; fi
grep -Fq "repository Makefile path could not be resolved" "$TEMP_ROOT/multiple.out"
printf '%s\n' "Makefile root tests passed: 66 executed target/authority cases, 1 dollar-syntax checkout case, 2 MAKEFILE_LIST rejections, 1 MAKEFILES rejection, and 1 earlier-Makefile detection"
