"""
GitHub Infrastructure Management

This Pulumi program manages GitHub repository settings and branch protection
rules for the home-agent-suite repository.

The program configures:
- Branch protection for the main branch
- Pull request review requirements
- Status check enforcement
- Repository governance policies

Usage:
    cd infrastructure/github
    poetry install
    pulumi stack init dev
    pulumi config set github:owner davidasnider
    pulumi config set --secret github:token YOUR_GITHUB_TOKEN
    pulumi up
"""

import pulumi
from branch_protection import BranchProtectionConfig, setup_repository_settings
from repository_settings import RepositorySettingsConfig, create_repository_settings


def main():
    """
    Main Pulumi program for GitHub repository management.

    This function orchestrates the creation of GitHub repository governance
    settings including branch protection rules and security configurations.
    """

    # Initialize configuration
    bp_config = BranchProtectionConfig()
    repo_config = RepositorySettingsConfig()

    # Create repository with settings
    repository = create_repository_settings(repo_config)

    # Setup repository governance
    resources = setup_repository_settings(
        repository_name=bp_config.repository_name, config=bp_config
    )

    # Export important resource information
    pulumi.export("repository_name", resources["repository_name"])
    pulumi.export("protected_branch", resources["protected_branch"])
    pulumi.export("branch_protection_id", resources["branch_protection"].id)
    pulumi.export("repository_id", repository.id)

    # Export branch protection details for reference
    pulumi.export(
        "branch_protection_url",
        resources["branch_protection"].id.apply(
            lambda id: (
                f"https://github.com/{bp_config.repository_name}/"
                f"settings/branch_protection_rules/{id}"
            )
        ),
    )


if __name__ == "__main__":
    main()
