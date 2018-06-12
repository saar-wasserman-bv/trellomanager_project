from django.core.management import BaseCommand
from utils import github
from trello import TrelloClient
from github import Github, PullRequest
from bluevine import settings
from utils.github import fetch_data_from_pull_request_url
from django.core.mail import send_mail, EmailMessage
from ...tasks import get_unmerged_pull_requests


class Command(BaseCommand):

    def add_arguments(self, parser):  # pylint: disable=no-self-use
        """ Add extra arguments """

        super().add_arguments(parser)
        parser.add_argument('--csv',
                            action='store_true',
                            default=False,
                            help='attach a csv to the sent email')
        #parser.add_argument('--to')

    def handle(self, *args, **options):
        # email_message = EmailMessage(
        #     'Test Trello Manager',
        #     'Verify csv is attached',
        #     'saarwasserman@gmail.com',
        #     ['saar.wasserman@bluevine.com', 'igal.kaufman@bluevine.com'],
        # )
        #
        # # email_message = ('Test Trello Manager', 'Verify csv is attached', 'saarwasserman@gmail.com',
        # #            ['saar.wasserman@bluevine.com',]) #'igal.kaufman@bluevine.com'])
        # email_message.attach_file('/Users/saar.wasserman/Documents/test.csv')
        # email_message.send()

        unmerged_pull_requests = get_unmerged_pull_requests()
        print(unmerged_pull_requests)
        #send_email()

