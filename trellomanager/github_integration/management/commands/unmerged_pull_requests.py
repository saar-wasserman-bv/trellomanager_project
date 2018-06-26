import logging
from itertools import groupby

from trello import TrelloClient
from github import Github

from github import UnknownObjectException

from django.core.management import BaseCommand
from django.template import Template, Context
from django.core.mail import EmailMessage

from bluevine import settings


logger = logging.getLogger(__file__)


class Command(BaseCommand):

    def __init__(self):

        self.trello_client = TrelloClient(settings.TRELLO_API_KEY, settings.TRELLO_API_TOKEN)
        self.github_client = Github(settings.GITHUB_TOKEN).get_organization('bluevine-dev')
        self.boards_names = {}

    def add_arguments(self, parser):  # pylint: disable=no-self-use
        """ Add extra arguments """

        super().add_arguments(parser)
        parser.add_argument('--csv',
                            action='store_true',
                            default=False,
                            help='attach a csv to the generated email')
        parser.add_argument('--user',
                            action='store',
                            help='run command for specified user')
        parser.add_argument('--group',
                            action='store',
                            help='run command for all members of the specified group')

    def handle(self, *args, **options):
        """ Run command """

        member_ids = []
        group = options.get('group')
        if group:
            member_ids = []
        else:
            email = options.get('user')
            if email:
                member_ids = [self.trello_client.get_member(email).id]
                print(member_ids)

        # generate unmerged pull request email to all desired users
        for member_id in member_ids:
            data = self._get_unmerged_pull_requests2(member_id)
            attachment = None
            if data and options['csv']:
                attachment = self.create_pull_requests_csv(data, member_id)
                logger.info(f'attachment {attachment} was created')

            # self.send_unmerged_pull_requests_data(data=data, recipients=[email], attachment=attachment)
        self.send_unmerged_pull_requests_data(data=data, recipients=[email], attachment=attachment)

    def _get_unmerged_pull_requests(self, member_id):
        """ Returns all unmerged pull requests related to cards """

        boards = self.trello_client.list_boards(board_filter='open')
        pull_requests_per_board = []
        for board in boards:
            cards = board.get_cards(card_filter='open')

            # get only member cards
            cards = [card for card in cards if member_id in card.member_id and not card.closed]
            pull_requests_per_card = []
            for card in cards:
                attachments = card.get_attachments()
                pr_attachments = [attachment for attachment in attachments if all(s in attachment.url
                                                                                  for s in['github.com', 'pull'])]
                # check for unmerged pull request in card
                unmerged_pull_requests = []
                for pr_attachment in pr_attachments:
                    try:
                        pull_request = self._get_pull_request_by_url(pr_attachment.url)
                    except UnknownObjectException as e:
                        logger.error(str(e))
                        continue

                    if not pull_request.is_merged() and not pull_request.closed_at:
                        pull_request_data = {
                            'name': pull_request.title,
                            "url": pr_attachment.url,
                        }

                        unmerged_pull_requests.append(pull_request_data)
                if unmerged_pull_requests:
                    card_data = {'name': card.name,
                                 'url': card.url,
                                 'pull_requests': unmerged_pull_requests}
                    pull_requests_per_card.append(card_data)

            if pull_requests_per_card:
                board_data = {'name': board.name,
                              'cards': pull_requests_per_card}
                pull_requests_per_board.append(board_data)

        return pull_requests_per_board

    @staticmethod
    def send_unmerged_pull_requests_data(data, recipients, attachment=None):
        """ Sends an email according to given data """

        html_content = Command.create_email_template(data)
        email_message = EmailMessage(subject='Trello Manager - Unmerged Pull Requests',
                                     body=html_content,
                                     from_email=settings.EMAIL_HOST_USER,
                                     to=recipients)
        email_message.content_subtype = 'html'
        if attachment:
            email_message.attach_file(attachment)
        email_message.send()

        logger.info(f'Email was sent to {recipients}')

    @staticmethod
    def create_pull_requests_csv(data, member_id):
        """ create a temporary csv file """

        import os, tempfile, csv
        from datetime import datetime

        now = datetime.now().strftime("%m_%d_%Y__%H%M%S")
        file_path = os.path.join(tempfile.gettempdir(), f'unmerged_pull_request_{member_id}_{now}.csv')
        with open(file_path, 'w') as csv_file:
            headers = ['board name', 'card name', 'card url', 'pull request name', 'pull request url']
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for board in data:
                cards = board['cards']
                for card in cards:
                    pull_requests = card['pull_requests']
                    for pull_request in pull_requests:
                        writer.writerow([board['name'], card['name'],
                                        card['url'], pull_request['name'],
                                        pull_request['url']])

        return file_path

    @staticmethod
    def fetch_data_from_pull_request_url(pull_request_url):
        """ Parses and returns pull request data from a pull request url """

        split_url = pull_request_url.split("/")
        owner = split_url[3]
        repo = split_url[4]
        number = int(split_url[-1])

        return owner, repo, number

    def _fetch_cards_by_member(self, member_id):
        """ Fetches all the cards for this member """

        cards = self.trello_client.fetch_json(
            '/members/' + member_id + '/cards',
            query_params={'filter': 'visible',
                          'fields': 'name,idBoard,url',
                          'attachments': 'true'})
        return sorted(cards, key=lambda card: card['idBoard'])

    def _get_board_name_by_id(self, board_id):
        """ Returns the name of the board """

        if board_id not in self.boards_names:
            self.boards_names[board_id] = self.trello_client.get_board(board_id).name

        return self.boards_names[board_id]

    def _get_pull_request_by_url(self, pull_request_url):

        owner, repo, number = self.fetch_data_from_pull_request_url(pull_request_url)
        return self.github_client.get_repo(repo).get_pull(int(number))

    @staticmethod
    def create_email_template(data):

        email_template = Template(EMAIL_TEMPLATE)
        return email_template.render(Context({'boards': data}))


EMAIL_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>"Trello Manager - Pull Requests"</title>
        </head>
        <body>
            {% if boards %}
                <h2>There are pull requests awaiting merge:</h2>

                {% for board in boards %}
                    <h3>{{board.name}} (Board)</h3>
                    {% for card in board.cards %}
                    <h4><a href={{card.url}}>{{card.name}} (Card)</a></h4>
                        {% for pull_request in card.pull_requests %}
                        <li><a href={{pull_request.url}}>{{pull_request.name}} (Pull Request)</a></li>
                        {% endfor %}
                    {% endfor %}
                {% endfor %}
            {% else %}
                There are no unmerged pull requests waiting for review
            {% endif %}
        </body>
    </html>
'''
