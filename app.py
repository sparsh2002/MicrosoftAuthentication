import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session

import app_config
from dotenv import load_dotenv

load_dotenv()

import os

app = Flask(__name__)
app.config.from_object(app_config)


Session(app)

REDIRECT_PATH = "/getAToken"
ENDPOINT = 'https://graph.microsoft.com/v1.0/me'
SCOPE = ["User.Read"]
SESSION_TYPE = "filesystem"

# print(app.config['CLIENT_ID'])

auth = identity.web.Auth(
    session=session,
    authority=os.getenv("AUTHORITY"),
    client_id=os.getenv("CLIENT_ID"),
    client_credential=os.getenv("CLIENT_SECRET"),
)


@app.route("/login")
def login():
    return render_template("login.html", **auth.log_in(
        scopes=SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True)
    ))


@app.route(REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))



@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))



@app.route("/")
def index():
    user = auth.get_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("index.html", user=user)



@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    
    print(token)
    # Use access token to call downstream api
    api_result = requests.get(
        ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)


if __name__ == "__main__":
    app.run(host='0.0.0.0' , port=3000)