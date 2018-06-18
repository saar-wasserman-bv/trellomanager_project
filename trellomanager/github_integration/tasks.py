from utils.github import fetch_data_from_pull_request_url, get_github_client
from utils.trello import get_trello_client


def get_unmerged_pull_requests(member_id=None):
    """ Returns all unmerged pull requests related to cards """

    trello_client = get_trello_client()
    github_client = get_github_client()

    boards = trello_client.list_boards()
    pull_requests_per_board = []
    for board in boards:
        cards = board.all_cards()
        if member_id:
            cards = [card for card in cards if member_id in card.member_id]

        pull_requests_per_card = []
        for card in cards:
            attachments = card.get_attachments()
            pr_attachments = [attachment for attachment in attachments if 'github.com' in attachment.url]

            # check for unmerged pull request in card
            unmerged_pull_requests = []
            for pr_attachment in pr_attachments:
                owner, repo, number = fetch_data_from_pull_request_url(pr_attachment.url)
                r = github_client.get_user().get_repo(repo)

                pull_request = r.get_pull(int(number))
                if not pull_request.is_merged():
                    pull_request_data = {
                        'title': pull_request.title,
                        "url": pr_attachment.url,
                    }

                    unmerged_pull_requests.append(pull_request_data)
            if unmerged_pull_requests:
                card_data = {'card_name': card.name,
                             'card_url': card.url,
                             'pull_requests': unmerged_pull_requests}
                pull_requests_per_card.append(card_data)

        if pull_requests_per_card:
            board_data = {'board_name': board.name,
                          'cards': pull_requests_per_card}
            pull_requests_per_board.append(board_data)

    return pull_requests_per_board


def get_unmerged_pull_requests_per_member(member_ids):
    """ Returns all unmerged pull requests related to cards """

    trello_client = get_trello_client()
    github_client = get_github_client()

    pull_requests_per_board = []
    for member_id in member_ids:
        boards = trello_client.list_boards()
        for board in boards:
            cards = [card for card in cards if member_id in card.member_id]

            pull_requests_per_card = []
            for card in cards:
                attachments = card.get_attachments()
                pr_attachments = [attachment for attachment in attachments if 'github.com' in attachment.url]

                # check for unmerged pull request in card
                unmerged_pull_requests = []
                for pr_attachment in pr_attachments:
                    owner, repo, number = fetch_data_from_pull_request_url(pr_attachment.url)
                    r = github_client.get_user().get_repo(repo)

                    pull_request = r.get_pull(int(number))
                    if not pull_request.is_merged():
                        pull_request_data = {
                            'title': pull_request.title,
                            "url": pr_attachment.url,
                        }

                        unmerged_pull_requests.append(pull_request_data)
                if unmerged_pull_requests:
                    card_data = {'card_name': card.name,
                                 'card_url': card.url,
                                 'pull_requests': unmerged_pull_requests}
                    pull_requests_per_card.append(card_data)

            if pull_requests_per_card:
                board_data = {'board_name': board.name,
                              'cards': pull_requests_per_card}
                pull_requests_per_board.append(board_data)

    return pull_requests_per_board
