"""
    github pull requests operations
"""

from github import Github

from bluevine import settings


def get_github_client():

    return Github(settings.GITHUB_TOKEN)


def fetch_data_from_pull_request_url(pull_request_url):
    """
    Retrieves data from pull request url https://github.com/<owner>/<repo/pull/<pull_request_number>

    Args:
        pull_request_url (str): a url related to the pull request

    Returns:
        A tuple containing three strings (owner_name, repo_name, pull_request_number)
    """

    split_url = pull_request_url.split("/")
    owner = split_url[3]
    repo = split_url[4]
    number = split_url[-1]

    return owner, repo, number
