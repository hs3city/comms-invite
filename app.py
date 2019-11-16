import os
from flask import Flask

TEMPLATE = """



"""

class SlackInvitationException(BaseException):
    pass

class SlackInvitationClient(object):
    BASE_URL = 'https://{}.slack.com'
    ENDPOINT = '/api/users.admin.invite'

    def __init__(self, team, token):
        self.token = token
        self.team = team

    @property
    def base_url(self):
        return self.BASE_URL.format(self.team)

    def invite(self, email, active=True):
        endpoint = urljoin(self.base_url, self.ENDPOINT)
        r = requests.post(endpoint, data={
            'email': email,
            'token': self.token,
            'set_active': active
        })
        response_object = r.json()
        if r.status_code == 200 and response_object['ok']:
            return True
        else:
            raise SlackInvitationException(response_object['error'])

TOKEN = os.get("SLACK_TOKEN")
WORKSPACE = os.get("SLACK_WORKSPACE")

slack_client = SlackInvitationClient(WORKSPACE, TOKEN)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

