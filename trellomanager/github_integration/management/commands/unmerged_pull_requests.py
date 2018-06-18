from django.core.management import BaseCommand
from trello import TrelloClient
from github import Github
from bluevine import settings
from utils.github import fetch_data_from_pull_request_url
#from ...tasks import get_unmerged_pull_requests
from django.template import Template, Context
from django.core.mail import send_mail


class Command(BaseCommand):

    def add_arguments(self, parser):  # pylint: disable=no-self-use
        """ Add extra arguments """

        super().add_arguments(parser)
        parser.add_argument('--csv',
                            action='store_true',
                            default=False,
                            help='attach a csv to the sent email')
        parser.add_argument('--to',
                            action='store_true',
                            default=False,
                            help='attach a csv to the sent email')

    def handle(self, *args, **options):
        data = get_unmerged_pull_requests()
        send_unmerged_pull_requests_data(data)


def get_unmerged_pull_requests(member_id=None):
    """ Returns all unmerged pull requests related to cards """

    trello_client = TrelloClient(settings.TRELLO_API_KEY, settings.TRELLO_API_TOKEN)
    github_client = Github(settings.GITHUB_TOKEN)

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


def send_unmerged_pull_requests_data(data, csv=None):

    t = Template(EMAIL_TEMPLATE)

    html = t.render(Context({'boards': data}))
    send_mail(subject='Trello Manager - Unmerged Pull Requests',
              message='This are your unmerged pull requests',
              from_email='saarwasserman@gmail.com',
              recipient_list=['saar.wasserman@bluevine.com'],
              html_message=html)


EMAIL_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>"Trello Manager - Pull Requests"</title>
        </head>
        <body>
            {% if boards %}
                <h2>There are pull requests awaiting review:</h2>
    
                {% for board in boards %}
                    <h3>{{board.board_name}} (Board)</h3>
                    {% for card in board.cards %}
                    <h4><a href={{card.card_url}}>{{card.card_name}} (Card)</a></h4>
                        {% for pull_request in card.pull_requests %}
                        <li><a href={{pull_request.url}}>{{pull_request.title}} (Pull Request)</a></li>
                        {% endfor %}
                    {% endfor %}
                {% endfor %}
            {% else %}
                There are no unmerged pull requests waiting for review
            {% endif %}
        </body>
    </html>
'''