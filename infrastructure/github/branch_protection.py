"""
GitHub Branch Protection Module

This module defines branch protection rules and repository governance policies
using Pulumi and the GitHub provider.

Key Features:
- Main branch protection with PR requirements
- Configurable review requirements
- Status check enforcement
- Admin enforcement settings

For GitHub repository management, this module:
- Prevents direct commits to protected branches
- Enforces code review workflows
- Maintains repository security standards
- Supports team-based governance
"""

import pulumi
import pulumi_github as github


class BranchProtectionConfig:
    """Configuration class for branch protection settings."""

    def __init__(self):
        """Initialize branch protection configuration from Pulumi config."""
        config = pulumi.Config()

        # Repository settings
        self.repository_name = config.get("repository_name", "home-agent-suite")
        self.protected_branch = config.get("protected_branch", "main")

        # Review requirements
        self.required_reviews = config.get_int("required_reviews", 1)
        self.dismiss_stale_reviews = config.get_bool("dismiss_stale_reviews", True)
        self.require_code_owner_reviews = config.get_bool(
            "require_code_owner_reviews", False
        )
        self.allow_review_dismissals = config.get_bool("allow_review_dismissals", True)

        # Push restrictions
        self.restrict_pushes = config.get_object("restrict_pushes", [])
        self.allow_force_pushes = config.get_bool("allow_force_pushes", False)
        self.allow_deletions = config.get_bool("allow_deletions", False)

        # Status checks
        self.require_status_checks = config.get_bool("require_status_checks", True)
        self.require_up_to_date = config.get_bool("require_up_to_date", True)
        self.status_check_contexts = config.get_object("status_check_contexts", [])

        # Admin settings - Enable by default for enhanced security
        self.enforce_admins = config.get_bool("enforce_admins", True)

        # Advanced security settings
        self.require_signed_commits = config.get_bool("require_signed_commits", True)
        self.lock_branch = config.get_bool("lock_branch", False)
        self.require_conversation_resolution = config.get_bool(
            "require_conversation_resolution", True
        )


def create_branch_protection_rule(
    repository_name: str, config: BranchProtectionConfig
) -> github.BranchProtection:
    """
    Creates a branch protection rule for the specified repository.

    This function sets up comprehensive branch protection including:
    - Pull request review requirements
    - Status check requirements
    - Push restrictions and admin enforcement

    Args:
        repository_name (str): Name of the repository to protect
        config (BranchProtectionConfig): Branch protection configuration

    Returns:
        github.BranchProtection: The created branch protection resource

    Example:
        config = BranchProtectionConfig()
        protection = create_branch_protection_rule("my-repo", config)
    """

    # Build status check contexts list
    status_contexts = []
    if isinstance(config.status_check_contexts, list):
        status_contexts = config.status_check_contexts

    # Create the branch protection rule
    branch_protection = github.BranchProtection(
        f"{repository_name}-{config.protected_branch}-protection",
        repository_id=repository_name,
        pattern=config.protected_branch,
        # Pull request review requirements
        required_pull_request_reviews=(
            [
                {
                    "required_approving_review_count": config.required_reviews,
                    "dismiss_stale_reviews": config.dismiss_stale_reviews,
                    "require_code_owner_reviews": config.require_code_owner_reviews,
                    "restrict_dismissals": not config.allow_review_dismissals,
                    "dismissal_restrictions": [],  # Empty means no restrictions
                }
            ]
            if config.required_reviews > 0
            else None
        ),
        # Status check requirements
        required_status_checks=(
            [
                {
                    "strict": config.require_up_to_date,
                    "contexts": status_contexts,
                }
            ]
            if config.require_status_checks
            else None
        ),
        # Push and deletion restrictions
        restrict_pushes=config.restrict_pushes,
        allows_force_pushes=config.allow_force_pushes,
        allows_deletions=config.allow_deletions,
        # Admin enforcement
        enforce_admins=config.enforce_admins,
        # Additional security settings
        required_linear_history=True,  # Enforce linear history
        require_conversation_resolution=config.require_conversation_resolution,
        require_signed_commits=config.require_signed_commits,
        lock_branch=config.lock_branch,
    )

    return branch_protection


def setup_repository_settings(
    repository_name: str, config: BranchProtectionConfig
) -> dict:
    """
    Sets up comprehensive repository settings and branch protection.

    This function creates all necessary GitHub repository governance settings
    including branch protection, default branch configuration, and security
    settings.

    Args:
        repository_name (str): Name of the repository to configure
        config (BranchProtectionConfig): Configuration settings

    Returns:
        dict: Dictionary containing created resources and their outputs

    Example:
        config = BranchProtectionConfig()
        resources = setup_repository_settings("my-repo", config)
        pulumi.export("branch_protection", resources["branch_protection"])
    """

    # Create branch protection rule
    branch_protection = create_branch_protection_rule(repository_name, config)

    # Return resource references for exports
    return {
        "branch_protection": branch_protection,
        "repository_name": repository_name,
        "protected_branch": config.protected_branch,
    }
