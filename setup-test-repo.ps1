#
# ForgeProof Test Project — Setup Script (PowerShell)
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
#   .\setup-test-repo.ps1
#

$ErrorActionPreference = "Stop"

Write-Host "=== ForgeProof Test Repo Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "Error: gh CLI not found. Install: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

$authCheck = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: gh not authenticated. Run: gh auth login" -ForegroundColor Red
    exit 1
}

# Get GitHub username
$GH_USER = gh api user -q ".login"
$REPO_NAME = "forgeproof-test-project"

Write-Host "GitHub user: $GH_USER"
Write-Host "Repo: $GH_USER/$REPO_NAME"
Write-Host ""

# Initialize git repo
if (-not (Test-Path ".git")) {
    git init
    git add -A
    git commit -m "Initial commit: taskflow library with tests"
    Write-Host "Initialized local repo" -ForegroundColor Green
} else {
    Write-Host "Git repo already exists, skipping init" -ForegroundColor Yellow
}

# Create GitHub repo
$repoCheck = gh repo view "$GH_USER/$REPO_NAME" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "GitHub repo already exists, skipping creation" -ForegroundColor Yellow
} else {
    gh repo create $REPO_NAME --public --source=. --push
    Write-Host "Created and pushed to GitHub" -ForegroundColor Green
}

# Push if not already pushed
$remoteCheck = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git"
}
git push -u origin main 2>$null
if ($LASTEXITCODE -ne 0) {
    git push -u origin master 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Already pushed" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Creating test issues ===" -ForegroundColor Cyan
Write-Host ""

# Issue 1: Simple bug fix
$body1 = @"
## Description

``Task.complete()`` can be called on a task that is already done, which resets ``completed_at`` to a new timestamp. It should be idempotent — calling ``complete()`` on an already-done task should be a no-op.

## Requirements

- REQ-1: ``complete()`` on a task with status DONE should not modify the task
- REQ-2: ``complete()`` on a task with status TODO or IN_PROGRESS should set status to DONE and record completed_at
- REQ-3: Add tests covering both cases

## Acceptance criteria

All existing tests continue to pass. New tests cover the idempotent behavior.
"@

gh issue create --title "Bug: Task.complete() doesn't validate current status" --body $body1 --label "bug" --assignee $GH_USER
Write-Host "Created issue #1: Bug fix" -ForegroundColor Green

# Issue 2: New feature
$body2 = @"
## Description

Tasks should support optional due dates. The TaskStore should be able to filter for overdue tasks.

## Requirements

- REQ-1: Add an optional ``due_date: datetime | None`` field to Task (default: None)
- REQ-2: Add ``TaskStore.filter_overdue()`` method that returns tasks past their due date that are not done
- REQ-3: Add ``TaskStore.filter_due_before(date)`` method that returns tasks due before a given date
- REQ-4: Add tests for all new functionality

## Notes

The ``is_overdue()`` method already exists on Task, but it requires passing a deadline. The new ``due_date`` field should be used by the store's filtering methods.
"@

gh issue create --title "Feature: Add due dates and overdue filtering to TaskStore" --body $body2 --label "enhancement" --assignee $GH_USER
Write-Host "Created issue #2: New feature" -ForegroundColor Green

# Issue 3: Refactor
$body3 = @"
## Description

The Task class should validate its inputs. Currently, you can create a task with an empty title or invalid priority/status combinations.

## Requirements

- REQ-1: Task.__init__ should raise ValueError if title is empty or whitespace-only
- REQ-2: Task.__init__ should raise TypeError if priority is not a Priority enum value
- REQ-3: Add a ``validate()`` method that checks all invariants and raises appropriate exceptions
- REQ-4: Add tests for validation edge cases

## Notes

This is a refactor of existing code — no new files should be needed. Modify ``task.py`` and add tests to ``test_task.py``.
"@

gh issue create --title "Refactor: Extract task validation into separate methods" --body $body3 --label "refactor" --assignee $GH_USER
Write-Host "Created issue #3: Refactor" -ForegroundColor Green

# Issue 4: Vague issue
$body4 = @"
Users should be able to search for tasks. It would be nice to search by title and maybe tags too. Not sure about the exact API yet — whatever makes sense for a simple library like this.
"@

gh issue create --title "Add task search functionality" --body $body4 --label "enhancement" --assignee $GH_USER
Write-Host "Created issue #4: Vague issue" -ForegroundColor Green

# Issue 5: Serialization
$body5 = @"
## Description

Tasks need to be serializable to JSON for persistence and API responses. Add ``to_dict()`` and ``from_dict()`` methods to the Task class.

## Requirements

- REQ-1: Add ``Task.to_dict()`` that returns a JSON-serializable dictionary with all fields
- REQ-2: Add ``Task.from_dict(data)`` class method that reconstructs a Task from a dictionary
- REQ-3: Enum fields (priority, status) should serialize as their string values
- REQ-4: Datetime fields should serialize as ISO 8601 strings
- REQ-5: Round-trip property: ``Task.from_dict(task.to_dict())`` should produce an equivalent task
- REQ-6: Add comprehensive tests including round-trip property test

## Notes

Use only stdlib — no pydantic or attrs.
"@

gh issue create --title "Feature: Task serialization to/from JSON" --body $body5 --label "enhancement" --assignee $GH_USER
Write-Host "Created issue #5: Serialization" -ForegroundColor Green

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repo: https://github.com/$GH_USER/$REPO_NAME"
Write-Host "Issues: https://github.com/$GH_USER/$REPO_NAME/issues"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open Claude Code in the $REPO_NAME folder"
Write-Host "  2. Install ForgeProof: claude plugin install /path/to/forgeproof.plugin"
Write-Host "  3. Run: /forgeproof 1    (start with the simple bug fix)"
