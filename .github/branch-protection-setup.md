# GitHub Branch Protection Setup

Follow these steps to protect your branches on GitHub:

## 1. Navigate to Settings
1. Go to https://github.com/Dr-Payne25/fantasyduel
2. Click on "Settings" tab
3. In the left sidebar, click "Branches" under "Code and automation"

## 2. Protect the `main` branch
1. Click "Add rule" or "Add branch protection rule"
2. Branch name pattern: `main`
3. Check these options:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1 (or adjust based on team size)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
   - ✅ **Require conversation resolution before merging**
   - ✅ **Include administrators** (optional, but recommended)
   - ✅ **Restrict who can push to matching branches** (optional)
     - Add yourself and trusted collaborators

4. Click "Create" to save the rule

## 3. Protect the `dev` branch (lighter protection)
1. Click "Add rule" again
2. Branch name pattern: `dev`
3. Check these options:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1 (can be 0 for solo projects)
   - ✅ **Require conversation resolution before merging**
   - ✅ **Allow force pushes** → "Specify who can force push" → Add admins only

4. Click "Create" to save the rule

## 4. Recommended Additional Settings

### For `main` branch:
- **Do not allow bypassing the above settings**
- **Restrict who can dismiss pull request reviews**
- **Do not allow deletions**

### For `dev` branch:
- **Allow deletions** (for cleaning up merged feature branches)
- **Allow administrators to bypass** (for emergency fixes)

## 5. Team Workflow After Protection

### Working with protected branches:
1. Always create feature branches for new work
2. Push feature branches and create Pull Requests
3. Get reviews (if required) before merging
4. Delete feature branches after merging

### If working solo:
- You can set "Required approvals" to 0 for `dev`
- Still use PRs for better history and CI/CD integration
- Consider using "Auto-merge" for approved PRs

## Quick Commands Reference

```bash
# Check current branch
git branch

# Create PR via GitHub CLI (if installed)
gh pr create --base dev --head feature/your-branch

# View PR status
gh pr status

# Merge PR after approval
gh pr merge
```

## Bypass Protection (Emergency Only)
If you need to push directly in an emergency:
1. Go to Settings → Branches
2. Edit the rule
3. Temporarily disable or add yourself to bypass list
4. **Remember to re-enable protection after!**
