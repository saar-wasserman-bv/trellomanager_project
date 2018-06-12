from trello import TrelloClient

from bluevine import settings


def get_trello_client():
    """ Returns a new trello client """

    return TrelloClient(api_key=settings.TRELLO_API_KEY, token=settings.TRELLO_API_TOKEN)