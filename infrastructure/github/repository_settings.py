import pulumi
import pulumi_github as github


class RepositorySettingsConfig:
    def __init__(self):
        config = pulumi.Config()
        self.repository_name = config.get("repository_name", "home-agent-suite")
        self.delete_branch_on_merge = config.get_bool("delete_branch_on_merge", True)
        self.has_issues = config.get_bool("has_issues", True)
        self.allow_auto_merge = config.get_bool("allow_auto_merge", True)
        self.allow_merge_commit = config.get_bool("allow_merge_commit", True)
        self.allow_squash_merge = config.get_bool("allow_squash_merge", True)
        self.allow_rebase_merge = config.get_bool("allow_rebase_merge", True)

        # Security features
        self.vulnerability_alerts = config.get_bool("vulnerability_alerts", True)
        self.security_advisories = config.get_bool("security_advisories", True)
        self.secret_scanning = config.get_bool("secret_scanning", True)
        self.secret_scanning_push_protection = config.get_bool(
            "secret_scanning_push_protection", True
        )
        self.dependabot_security_updates = config.get_bool(
            "dependabot_security_updates", True
        )
        self.private_vulnerability_reporting = config.get_bool(
            "private_vulnerability_reporting", True
        )


def create_repository_settings(config: RepositorySettingsConfig) -> dict:
    repo = github.Repository(
        config.repository_name,
        name=config.repository_name,
        delete_branch_on_merge=config.delete_branch_on_merge,
        has_issues=config.has_issues,
        allow_auto_merge=config.allow_auto_merge,
        allow_merge_commit=config.allow_merge_commit,
        allow_squash_merge=config.allow_squash_merge,
        allow_rebase_merge=config.allow_rebase_merge,
        # Security settings
        vulnerability_alerts=config.vulnerability_alerts,
        security_and_analysis={
            "secret_scanning": {
                "status": "enabled" if config.secret_scanning else "disabled"
            },
            "secret_scanning_push_protection": {
                "status": (
                    "enabled" if config.secret_scanning_push_protection else "disabled"
                )
            },
        },
        opts=pulumi.ResourceOptions(import_=config.repository_name),
    )

    # Configure GitHub Actions permissions
    actions_permissions = github.ActionsRepositoryPermissions(
        f"{config.repository_name}-actions-permissions",
        repository=repo.name,
        allowed_actions="all",
        enabled=True,
    )

    # Configure Dependabot security updates
    dependabot_security_updates = None
    if config.dependabot_security_updates:
        dependabot_security_updates = github.RepositoryDependabotSecurityUpdates(
            f"{config.repository_name}-dependabot-security-updates",
            repository=repo.name,
            enabled=True,
        )

    return {
        "repository": repo,
        "actions_permissions": actions_permissions,
        "dependabot_security_updates": dependabot_security_updates,
    }
