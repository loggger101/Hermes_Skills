#!/usr/bin/env bash
# Bisection-style polluter finder: which test creates unwanted files/state?
# Usage: ./find_polluter.sh <file_or_dir_to_check> <test_pattern> [runner]
# Example: ./find_polluter.sh '.git' 'tests/**/*.py'
#          ./find_polluter.sh '/tmp/leak.json' 'src/top.test.ts' 'npm test --'
#
# Adapted from obra/superpowers v6.3.0 (skills/systematic-debugging/find-polluter.sh, MIT):
# the npm runner line was generalized to a configurable RUNNER (default: pytest).

set -e

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
  echo "Usage: $0 <file_to_check> <test_pattern> [runner...]"
  echo "Example: $0 '.git' 'tests/**/*.py'"
  exit 1
fi

POLLUTION_CHECK="$1"
TEST_PATTERN="$2"
# Default runner for this repo's Python/pytest convention; override per project.
RUNNER="${@:3}"
if [ -z "$RUNNER" ]; then RUNNER="python -m pytest"; fi

echo "Searching for test that creates: $POLLUTION_CHECK"
echo "Test pattern: $TEST_PATTERN"
echo "Runner: $RUNNER"
echo ""

# Get list of test files. find . emits ./-prefixed paths, so accept the
# pattern written with or without a leading ./ (strip one if present).
TEST_PATTERN="${TEST_PATTERN#./}"
# find -path can't match '**/' against zero directory levels, so a pattern
# like tests/**/*.py would skip tests/top.py; also try the pattern with
# '**/' collapsed to cover files directly under the base directory.
TEST_FILES=$(find . \( -path "./$TEST_PATTERN" -o -path "./${TEST_PATTERN//\*\*\/}" \) | sort -u)
if [ -z "$TEST_FILES" ]; then
  TOTAL=0
else
  TOTAL=$(printf '%s\n' "$TEST_FILES" | wc -l | tr -d ' ')
fi

echo "Found $TOTAL test files"
echo ""

COUNT=0
for TEST_FILE in $TEST_FILES; do
  COUNT=$((COUNT + 1))

  # Skip if pollution already exists (prevents false attribution to later tests)
  if [ -e "$POLLUTION_CHECK" ]; then
    echo "WARNING: Pollution already exists before test $COUNT/$TOTAL"
    echo "   Skipping: $TEST_FILE"
    continue
  fi

  echo "[$COUNT/$TOTAL] Testing: $TEST_FILE"

  # Run the single test; a failing test can still create pollution, so allow failure.
  $RUNNER "$TEST_FILE" > /dev/null 2>&1 || true

  # Check if pollution appeared
  if [ -e "$POLLUTION_CHECK" ]; then
    echo ""
    echo "FOUND POLLUTER!"
    echo "   Test: $TEST_FILE"
    echo "   Created: $POLLUTION_CHECK"
    echo ""
    echo "Pollution details:"
    ls -la "$POLLUTION_CHECK"
    echo ""
    echo "To investigate:"
    echo "  $RUNNER $TEST_FILE    # Run just this test"
    echo "  cat $TEST_FILE        # Review test code"
    exit 1
  fi
done

echo ""
echo "No polluter found - all tests clean!"
exit 0
