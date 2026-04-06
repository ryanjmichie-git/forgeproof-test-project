#!/usr/bin/env bash
#
# ForgeProof Test Project — Setup Script
#
# This script:
#   1. Initializes a git repo from the test project files
#   2. Creates a public GitHub repo
#   3. Pushes the code
#   4. Creates 5 GitHub issues for testing ForgeProof
#
# Prerequisites:
#   - gh CLI authenticated (run: gh auth login)
#   - git configured with name and email
#
# Usage:
#   cd forgeproof-test-project
#   chmod +x setup-test-repo.sh
#   ./setup-test-repo.sh
#

set -euo pipefail

echo "=== ForgeProof Test Repo Setup ==="
echo ""

# Check prerequisites
if ! command -v gh &>/dev/null; then
    echo "Error: gh CLI not found. Install: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &>/dev/null; then
    echo "Error: gh not authenticated. Run: gh auth login"
    exit 1
fi

# Get GitHub username
GH_USER=$(gh api user -q .login)
REPO_NAME="forgeproof-test-project"

echo "GitHub user: $GH_USER"
echo "Repo: $GH_USER/$REPO_NAME"
echo ""

# Initialize git repo
if [ ! -d .git ]; then
    git init
    git add -A
    git commit -m "Initial commit: taskflow library with tests"
    echo "Initialized local repo"
else
    echo "Git repo already exists, skipping init"
fi

# Create GitHub repo
if gh repo view "$GH_USER/$REPO_NAME" &>/dev/null; then
    echo "GitHub repo already exists, skipping creation"
else
    gh repo create "$REPO_NAME" --public --source=. --push
    echo "Created and pushed to GitHub"
fi

# Push if not already pushed
if ! git remote get-url origin &>/dev/null; then
    git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git"
fi
git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null || echo "Already pushed"

echo ""
echo "=== Creating test issues ==="
echo ""

# Issue 1: Simple bug fix (single file change)
gh issue create \
    --title "Bug: Task.complete() doesn't validate current status" \
    --body "$(cat <<'ISSUE'
## Description

`Task.complete()` can be called on a task that is already done, which resets `completed_at` to a new timestamp. It should be idempotent — calling `complete()` on an already-done task should be a no-op.

## Requirements

- REQ-1: `complete()` on a task with status DONE should not modify the task
- REQ-2: `complete()` on a task with status TODO or IN_PROGRESS should set status to DONE and record completed_at
- REQ-3: Add tests covering both cases

## Acceptance criteria

All existing tests continue to pass. New tests cover the idempotent behavior.
ISSUE
)" \
    --label "bug" \
    --assignee "$GH_USER"

echo "Created issue #1: Bug fix"

# Issue 2: New feature (multiple files + tests)
gh issue create \
    --title "Feature: Add due dates and overdue filtering to TaskStore" \
    --body "$(cat <<'ISSUE'
## Description

Tasks should support optional due dates. The TaskStore should be able to filter for overdue tasks.

## Requirements

- REQ-1: Add an optional `due_date: datetime | None` field to Task (default: None)
- REQ-2: Add `TaskStore.filter_overdue()` method that returns tasks past their due date that are not done
- REQ-3: Add `TaskStore.filter_due_before(date)` method that returns tasks due before a given date
- REQ-4: Add tests for all new functionality

## Notes

The `is_overdue()` method already exists on Task, but it requires passing a deadline. The new `due_date` field should be used by the store's filtering methods.
ISSUE
)" \
    --label "enhancement" \
    --assignee "$GH_USER"

echo "Created issue #2: New feature"

# Issue 3: Refactor (modify-only, no new files)
gh issue create \
    --title "Refactor: Extract task validation into separate methods" \
    --body "$(cat <<'ISSUE'
## Description

The Task class should validate its inputs. Currently, you can create a task with an empty title or invalid priority/status combinations.

## Requirements

- REQ-1: Task.__init__ should raise ValueError if title is empty or whitespace-only
- REQ-2: Task.__init__ should raise TypeError if priority is not a Priority enum value
- REQ-3: Add a `validate()` method that checks all invariants and raises appropriate exceptions
- REQ-4: Add tests for validation edge cases

## Notes

This is a refactor of existing code — no new files should be needed. Modify `task.py` and add tests to `test_task.py`.
ISSUE
)" \
    --label "refactor" \
    --assignee "$GH_USER"

echo "Created issue #3: Refactor"

# Issue 4: Vague issue (tests requirement extraction)
gh issue create \
    --title "Add task search functionality" \
    --body "$(cat <<'ISSUE'
Users should be able to search for tasks. It would be nice to search by title and maybe tags too. Not sure about the exact API yet — whatever makes sense for a simple library like this.
ISSUE
)" \
    --label "enhancement" \
    --assignee "$GH_USER"

echo "Created issue #4: Vague issue"

# Issue 5: Cross-cutting change (implementation + test files)
gh issue create \
    --title "Feature: Task serialization to/from JSON" \
    --body "$(cat <<'ISSUE'
## Description

Tasks need to be serializable to JSON for persistence and API responses. Add `to_dict()` and `from_dict()` methods to the Task class.

## Requirements

- REQ-1: Add `Task.to_dict()` that returns a JSON-serializable dictionary with all fields
- REQ-2: Add `Task.from_dict(data)` class method that reconstructs a Task from a dictionary
- REQ-3: Enum fields (priority, status) should serialize as their string values
- REQ-4: Datetime fields should serialize as ISO 8601 strings
- REQ-5: Round-trip property: `Task.from_dict(task.to_dict())` should produce an equivalent task
- REQ-6: Add comprehensive tests including round-trip property test

## Notes

Use only stdlib — no pydantic or attrs.
ISSUE
)" \
    --label "enhancement" \
    --assignee "$GH_USER"

echo "Created issue #5: Serialization"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Repo: https://github.com/$GH_USER/$REPO_NAME"
echo "Issues: https://github.com/$GH_USER/$REPO_NAME/issues"
echo ""
echo "Next steps:"
echo "  1. cd $REPO_NAME"
echo "  2. claude plugin install /path/to/forgeproof.plugin"
echo "  3. /forgeproof 1    (start with the simple bug fix)"
