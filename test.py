from github import Github

repo_url = "Swanchick/ksm-settings"

github = Github()

repo = github.get_repo(repo_url)
contents = repo.get_contents("")

for content in contents:
    print(content)