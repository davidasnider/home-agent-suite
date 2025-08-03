import pulumi
import pulumi_github as github


class RepositorySettingsConfig:
    def __init__(self):
        config = pulumi.Config()
        self.repository_name = config.get("repository_name", "home-agent-suite")
        self.delete_branch_on_merge = config.get_bool("delete_branch_on_merge", True)


def create_repository_settings(config: RepositorySettingsConfig) -> github.Repository:
    repo = github.Repository(
        config.repository_name,
        name=config.repository_name,
        delete_branch_on_merge=config.delete_branch_on_merge,
        opts=pulumi.ResourceOptions(import_=config.repository_name),
    )
    return repo
