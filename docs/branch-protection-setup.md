# Branch Protection Setup Guide

This document explains how to configure branch protection rules for the ZERGO QR repository to ensure code quality and prevent issues from being merged.

## Required Branch Protection Rules

### Main Branch (`main`)

1. **Require a pull request before merging**

   - Require approvals: 1
   - Dismiss stale PR approvals when new commits are pushed: ✅
   - Require review from code owners: ✅

2. **Require status checks to pass before merging**

   - Require branches to be up to date before merging: ✅
   - Required status checks:
     - `Backend Tests`
     - `Frontend Tests`
     - `Integration Tests`
     - `Build Tests`
     - `Security Scan`

3. **Require conversation resolution before merging**: ✅

4. **Require signed commits**: ✅ (recommended)

5. **Include administrators**: ✅ (applies rules to admins too)

6. **Allow force pushes**: ❌

7. **Allow deletions**: ❌

### Develop Branch (`develop`)

1. **Require a pull request before merging**

   - Require approvals: 1
   - Dismiss stale PR approvals when new commits are pushed: ✅

2. **Require status checks to pass before merging**

   - Required status checks:
     - `Backend Tests`
     - `Frontend Tests`
     - `Build Tests`

3. **Require conversation resolution before merging**: ✅

## Setup Instructions

### Via GitHub Web Interface

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Navigate to **Branches** in the left sidebar
4. Click **Add rule** next to "Branch protection rules"
5. Configure the branch name pattern (e.g., `main` or `develop`)
6. Select the protection options as listed above
7. Click **Create** or **Save changes**

### Via GitHub CLI (if available)

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Set branch protection for main
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Backend Tests","Frontend Tests","Integration Tests","Build Tests"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null
```

### Via Repository Settings JSON (for automation)

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Backend Tests",
      "Frontend Tests",
      "Integration Tests",
      "Build Tests",
      "Security Scan"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

## CODEOWNERS File

Create a `.github/CODEOWNERS` file to automatically request reviews from specific team members:

```
# Global owners
* @team-leads

# Backend code
apps/backend/ @backend-team

# Frontend code
apps/frontend/ @frontend-team

# Infrastructure
.github/ @devops-team
infra/ @devops-team
docker-compose.yml @devops-team

# Documentation
docs/ @tech-writers @team-leads
README.md @tech-writers @team-leads

# Configuration files
*.yml @devops-team
*.yaml @devops-team
*.json @devops-team
```

## Verification

After setting up branch protection:

1. Create a test pull request
2. Verify that the required status checks appear
3. Confirm that merging is blocked until all checks pass
4. Test that the required number of approvals is enforced

## Troubleshooting

### Status Checks Not Appearing

- Ensure the workflow names in `.github/workflows/test.yml` match the required status checks
- Check that the workflow has run at least once on the target branch
- Verify the workflow is not disabled

### Cannot Merge Despite Passing Tests

- Check if "Require branches to be up to date" is enabled and branch needs updating
- Verify all required reviewers have approved
- Ensure all conversations are resolved

### Admin Override Needed

- If administrators are included in the rules, they will also need to follow the same process
- Consider if admin override is needed for emergency fixes

## Additional Recommendations

1. **Enable vulnerability alerts**: Go to Settings → Security & analysis → Enable Dependabot alerts
2. **Set up automated dependency updates**: Enable Dependabot version updates
3. **Configure security scanning**: Enable CodeQL analysis in the Security tab
4. **Review merge queue settings**: Consider enabling merge queue for high-traffic repositories

Remember to communicate these changes to your team and provide training on the new workflow!
