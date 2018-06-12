from utils.github import fetch_data_from_pull_request_url, get_github_client
from utils.trello import get_trello_client


def get_unmerged_pull_requests(user=None):
    """ Returns all unmerged pull requests related to cards """

    # TODO: get the clients from utils - some factory methods
    trello_client = get_trello_client()
    github_client = get_github_client()

    unmerged_pull_requests = []
    boards = trello_client.list_boards()
    for board in boards:
        #TODO: filter cards by user if given
        cards = board.get_cards()
        for card in cards:
            attachments = card.get_attachments()
            pr_attachments = [attachment for attachment in attachments if 'github.com' in attachment.url]
            for pr_attachment in pr_attachments:
                owner, repo, number = fetch_data_from_pull_request_url(pr_attachment.url)
                r = github_client.get_user().get_repo(repo)

                pull_request = r.get_pull(int(number))
                if not pull_request.is_merged():
                    data = {
                        "card_name": card.name,
                        "card_url": card.url,
                        "pull_request": pull_request.url
                    }

                    unmerged_pull_requests.append(data)

    return unmerged_pull_requests
