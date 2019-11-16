import os
import re
from datetime import datetime
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests
from flask import Flask, request, url_for, abort, redirect, render_template

email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

app = Flask("slack-invite")

def requester_ip():
    if request.headers.getlist("X-Forwarded-For"):
        ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        app.logger.info(
            "forward from %s to %s",
            request.remote_addr,
            request.headers.getlist("X-Forwarded-For")[0],
        )
    else:
        ip_addr = request.remote_addr
    return ip_addr

class SlackInvitationException(BaseException):
    pass


class SlackInvitationClient(object):
    BASE_URL = "https://{}.slack.com"
    ENDPOINT = "/api/users.admin.invite"

    def __init__(self, team, token):
        self.token = token
        self.team = team

    @property
    def base_url(self):
        return self.BASE_URL.format(self.team)

    def invite(self, email, active=True):
        endpoint = urljoin(self.base_url, self.ENDPOINT)
        r = requests.post(
            endpoint, data={"email": email, "token": self.token, "set_active": active}
        )
        response_object = r.json()
        if r.status_code == 200 and response_object["ok"]:
            return True
        else:
            raise SlackInvitationException(response_object["error"])

last_invite = datetime.now()
MIN_SECONDS = 30

TOKEN = os.environ.get("SLACK_TOKEN")
WORKSPACE = os.environ.get("SLACK_WORKSPACE")

if TOKEN is None or WORKSPACE is None:
    raise Exception("Setup envs SLACK_TOKEN and SLACK_WORKSPACE")

slack_client = SlackInvitationClient(WORKSPACE, TOKEN)


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        # anti abuse
        #global last_invite
        #seconds_elapsed = (datetime.now() - last_invite).total_seconds()
        #if seconds_elapsed < MIN_SECONDS:
        #    app.logger.error("Invite sent while locked, %i seconds elapsed from %i", seconds_elapsed, MIN_SECONDS)
        #    abort(423)

        if not email_re.match(request.form["email"]):
            abort(400)

        try:
            app.logger.info("Inviting %s from %s to workspace", request.form["email"], requester_ip())
            slack_client.invite(request.form["email"])
        except SlackInvitationException as exc:
            app.logger.error(exc)
            abort(502)

        last_invite = datetime.now()
        redirect(url_for("/"))

    else:
        return render_template("index.html")
