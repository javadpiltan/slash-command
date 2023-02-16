import mysql.connector
import datetime
import os
import sys
import requests
from flask import Flask, request, jsonify

MT_BASE_URL = os.environ['MT_BASE_URL']
MT_MATTERMOST_TOKEN = os.environ['MT_MATTERMOST_TOKEN']
MT_MATTERMOST_HOST = os.environ['MT_MATTERMOST_HOST']
MT_MATTERMOST_LOGIN_ID = os.environ['MT_MATTERMOST_LOGIN_ID']
MT_MATTERMOST_PASSWORD = os.environ['MT_MATTERMOST_PASSWORD']

# Mattermost authentication
r = requests.post(
    url=MT_MATTERMOST_HOST + "api/v4/users/login",
    json={
        'login_id': MT_MATTERMOST_LOGIN_ID,
        'password': MT_MATTERMOST_PASSWORD
    }
)

if r.status_code != 200:
    print("Error in mattermost login", file=sys.stderr)
    sys.exit(1)
mattermost_login_token = r.headers['token']

# Flask initialization
app = Flask(__name__)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_username = requests.post(
        url=MT_MATTERMOST_HOST + "api/v4/users/ids",
        json=[
            data['user_id']
        ],
        headers={
            "Authorization": "Bearer " + mattermost_login_token
        }
    ).json()[0]["username"]

    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="150269378Ll",
            database="log_in"
        )

    except:
        sys.exit("Error connecting to the host.")

    my_cursor = mydb.cursor()

    t = datetime.datetime.now()
    sql = "INSERT INTO logdata(username, login) VALUES (%s, %s)"
    val = (user_username, t)
    my_cursor.execute(sql, val)

    mydb.commit()


@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    user_username = requests.post(
        url=MT_MATTERMOST_HOST + "api/v4/users/ids",
        json=[
            data['user_id']
        ],
        headers={
            "Authorization": "Bearer " + mattermost_login_token
        }
    ).json()[0]["username"]

    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="150269378Ll",
            database="log_in"
        )

    except:
        sys.exit("Error connecting to the host.")
    my_cursor = mydb.cursor()

    logout_db = "UPDATE logdata SET logout = now()  WHERE username=user_username AND logout IS NULL ;"
    my_cursor.execute(logout_db)

    mydb.commit()

    # Create a post in the channel that user logged in
    requests.post(
        url=MT_MATTERMOST_HOST + "api/v4/posts",
        json={
            'channel_id': data['channel_id'],
            'message': '#### ' + user_username + 'logged in '
        },
        headers={
            "Authorization": "Bearer " + mattermost_login_token
        }
    )

    return jsonify({})
