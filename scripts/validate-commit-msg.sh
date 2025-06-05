#!/bin/bash

# Validate commit message format
# Expected format: <type>(<scope>): <subject>

commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\([a-z0-9-]+\))?: .{1,80}$'
error_msg="Commit message does not follow the conventional format.

Expected format: <type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scope: optional, lowercase with hyphens (e.g., auth, draft-api)
Subject: imperative mood, no period at end, max 80 chars

Examples:
  feat(auth): add JWT refresh token support
  fix(draft): resolve pick order calculation bug
  docs: update API documentation
  test(leagues): add integration tests

Your commit message:"

# Read the commit message
if [ -z "$1" ]; then
    echo "Error: No commit message file provided"
    exit 1
fi

commit_message=$(cat "$1")

# Check if the commit message matches the pattern
if ! echo "$commit_message" | grep -qE "$commit_regex"; then
    echo "$error_msg"
    echo "$commit_message"
    exit 1
fi

# Check for common issues
if echo "$commit_message" | grep -q "\.$$"; then
    echo "Error: Commit subject should not end with a period"
    echo "Your commit message: $commit_message"
    exit 1
fi

# Success
exit 0
