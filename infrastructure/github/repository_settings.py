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
        opts=pulumi.ResourceOptions(import_=config.repository_name),
    )

    # Configure GitHub Actions permissions
    actions_permissions = github.ActionsRepositoryPermissions(
        f"{config.repository_name}-actions-permissions",
        repository=repo.name,
        allowed_actions="all",
        enabled=True,
    )

    return {
        "repository": repo,
        "actions_permissions": actions_permissions,
    }
