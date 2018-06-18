from django.template import Template, Context
from django.core.mail import send_mail, EmailMessage


def send_unmerged_pull_requests_data(data, csv=None):

    # Simple way of using templates from the filesystem.
    # This is BAD because it doesn't account for missing files!
    fp = open('/Users/saar.wasserman/bluevine/trellomanager_project/utils/pull_requests_email.html')
    t = Template(fp.read())
    fp.close()

    html = t.render(Context({'boards': data}))
    send_mail(subject='Trello Manager - Unmerged Pull Requests',
              message='This are your unmerged pull requests',
              from_email='saarwasserman@gmail.com',
              recipient_list=['saar.wasserman@bluevine.com'],
              html_message=html)
