# GitHub Infrastructure Management

This directory contains Pulumi Infrastructure as Code (IaC) for managing GitHub repository settings and branch protection rules.

## Overview

The GitHub infrastructure manages:
- **Branch Protection**: Prevents direct commits to main branch
- **Pull Request Requirements**: Enforces code review workflow
- **Status Checks**: Integrates with CI/CD pipeline
- **Repository Governance**: Maintains security and quality standards

## Architecture

```
infrastructure/github/
├── __main__.py              # Main Pulumi program
├── branch_protection.py     # Branch protection logic
├── pyproject.toml          # Poetry dependencies
├── Pulumi.yaml             # Project configuration
├── Pulumi.dev.yaml         # Stack configuration
└── README.md               # This file
```

## Setup

### Prerequisites
- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/) installed
- GitHub Personal Access Token with `repo` permissions
- Poetry for dependency management

### Installation

```bash
# Navigate to infrastructure directory
cd infrastructure/github

# Install dependencies with Poetry
poetry install

# Initialize Pulumi stack (first time only)
pulumi stack init dev

# Configure GitHub settings
pulumi config set github:owner davidasnider
pulumi config set --secret github:token YOUR_GITHUB_TOKEN
```

### Configuration

The infrastructure supports the following configuration options:

| Setting | Default | Description |
|---------|---------|-------------|
| `repository_name` | `home-agent-suite` | Repository to manage |
| `protected_branch` | `main` | Branch to protect |
| `required_reviews` | `1` | Required PR reviewers |
| `dismiss_stale_reviews` | `true` | Dismiss reviews on new commits |
| `require_code_owner_reviews` | `false` | Require CODEOWNERS approval |
| `restrict_pushes` | `true` | Prevent direct pushes |
| `allow_force_pushes` | `false` | Allow force pushes |
| `require_status_checks` | `true` | Require CI checks |
| `enforce_admins` | `false` | Apply rules to admins |

## Deployment

```bash
# Preview changes
pulumi preview

# Apply changes
pulumi up

# View current stack outputs
pulumi stack output
```

## Branch Protection Rules

The configuration creates the following protection rules for the `main` branch:

### ✅ **Enabled Protections**
- **Pull Request Required**: Direct commits blocked
- **1 Required Reviewer**: Can be the same person pushing
- **Dismiss Stale Reviews**: Reviews cleared on new commits
- **Linear History**: Merge commits prevented
- **Conversation Resolution**: All comments must be resolved
- **Up-to-date Status**: Branch must be current with main

### ❌ **Disabled Protections**
- **Code Owner Reviews**: Not required (no CODEOWNERS file)
- **Admin Enforcement**: Admins can bypass rules
- **Force Pushes**: Blocked for safety
- **Branch Deletions**: Blocked for safety

### 🔄 **Status Checks**
The following CI checks are required:
- `ci/quality-checks` - Code formatting and linting
- `ci/tests` - Test suite execution

## Usage Examples

### Update Configuration
```bash
# Change required reviewers
pulumi config set github-management:required_reviews 2

# Enable admin enforcement
pulumi config set github-management:enforce_admins true

# Apply changes
pulumi up
```

### Add Status Checks
```bash
# Add new required status check
pulumi config set github-management:status_check_contexts '[\"ci/quality-checks\", \"ci/tests\", \"ci/security-scan\"]'

pulumi up
```

## Troubleshooting

### Common Issues

**Authentication Error**
```bash
# Verify token has correct permissions
pulumi config get --secret github:token

# Update token if needed
pulumi config set --secret github:token NEW_TOKEN
```

**Permission Denied**
- Ensure GitHub token has `repo` scope
- Verify you have admin access to the repository

**Branch Protection Not Applied**
- Check that the branch name matches exactly
- Verify the repository name is correct
- Ensure no existing rules conflict

### Validation

After deployment, verify the settings:

1. **GitHub UI**: Visit `https://github.com/davidasnider/home-agent-suite/settings/branches`
2. **CLI Check**:
   ```bash
   pulumi stack output branch_protection_url
   ```
3. **Test Protection**: Try pushing directly to main (should be blocked)

## Development Workflow

With branch protection enabled, the development workflow becomes:

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   git push -u origin feature/my-feature
   ```

2. **Create Pull Request**
   - Push changes to feature branch
   - Open PR in GitHub UI
   - Request review (can be self-review)

3. **Merge Process**
   - Address review comments
   - Ensure CI checks pass
   - Squash and merge (recommended)

## Security Considerations

- GitHub token is stored encrypted in Pulumi state
- Branch protection prevents accidental direct commits
- Status checks ensure code quality before merge
- Review requirements maintain code oversight

## Next Steps

Consider extending this infrastructure with:
- **Team Management**: Add team-based access controls
- **Repository Settings**: Manage additional repo configuration
- **Webhooks**: Configure automated integrations
- **Security Scanning**: Add required security checks
