from trello import TrelloClient

from django.core.management import BaseCommand
from django.core.mail import send_mail
from django.template import Template, Context

from trellomanager.profiles.models import User
from bluevine import settings


class Command(BaseCommand):

    task_config = {
        'date_time': ['', ],
        'boards': [
            {
                'name': 'Tello Reports',
                'id': '5b1a2a42be67484938a11d16',
                'lists': [
                    {
                        'name': 'To Do',
                        'id': '5b1a2a42be67484938a11d17'
                    },
                    {
                        'name': 'Doing',
                        'id': '5b1a2a42be67484938a11d18'
                    }
                ],
            },
            {
                'name': 'Another Board',
                'id': 'J5FqV9hR',
                'lists': [
                    {
                        'name': 'somthing else',
                        'id': '5b2ec4e499b93bf92586ebc4',
                    },
                ]
            }
        ],
        'roles': ['TL', ],
        'additional_emails': ['saarwasserman@gmail.com'],
    }

    def __init__(self):

        self.trello_client = TrelloClient(settings.TRELLO_API_KEY, settings.TRELLO_API_TOKEN)

    def handle(self, *args, **options):
        """ Run command """

        boards = Command.task_config['boards']
        cards = self.get_relevant_cards(boards)

        roles = Command.task_config['roles']
        users = User.objects.filter(role__in=roles)

        # send cards to its member based on role
        for user in users:
            member_id = self.trello_client.get_member(user.email).id
            member_cards = [card for card in cards if member_id in card.member_ids]
            if member_cards:
                self.send_data(member_cards, [user.email])

        # send cards to the additional emails
        additional_emails = Command.task_config.get('additional_emails')
        if additional_emails:
            self.send_data(cards, additional_emails)

    def send_data(self, cards, recipients):
        """ send relevant cards links to recipients """

        email_template = Template(EMAIL_TEMPLATE)
        html_content = email_template.render(Context({'cards': cards}))

        send_mail(subject="Trello Manager - Feature Freeze",
                  message="Cards left before feature freeze",
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=recipients,
                  html_message=html_content)

    def get_relevant_cards(self, boards):

        cards = []
        for board_dict in boards:
            board_obj = self.trello_client.get_board(board_dict['id'])
            for list_dict in board_dict['lists']:
                list_obj = board_obj.get_list(list_dict['id'])
                cards += list_obj.list_cards()

        return cards


EMAIL_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>"Trello Manager - Feature Freeze"</title>
        </head>
        <body>
            {% if cards %}
                <h3>These cards must be done before feature freeze:</h2>
                {% for card in cards %}
                    <h4><a href={{card.url}}>{{card.name}} ({{card.board.name}} - {{card.trello_list.name}})</a></h4>
                {% endfor %}
            {% endif %}
        </body>
    </html>
'''
