from flask import Flask, redirect, request, render_template
import subprocess
import requests
import json
import sys
sys.path.insert(0, "..")
import add_all_tracks

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

CLIENT_ID = '0356a0d5fd974f4497a212601fa2b636'
REDIRECT_URI = 'http://localhost:5000/callback'
AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
TOKTOKEN = ""
tokenfile = open("tokenfile.json", "w+")

@app.route('/')
def index():
    return render_template('theseare.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'playlist-modify-private playlist-modify-public'
    }
    auth_url = f"{AUTHORIZE_URL}?{'&'.join([f'{key}={value}' for key, value in auth_params.items()])}"
    print(auth_url)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global TOKTOKEN
    code = request.args.get('code')
    print(code)
    token_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': '0490e9dd613344979d6b1b68c82000f9',  # Replace with your actual client secret
    }
    response = requests.post(TOKEN_URL, data=token_params)
    token_data = response.json()

    access_token = token_data.get('access_token')
    # Now you can use the access_token to make authorized requests to the Spotify API
    print(access_token)
    TOKTOKEN = access_token
    return redirect('/')

@app.route('/startprogram', methods=['POST'])
def startprogram():
    global TOKTOKEN
    program = request.form['program']
    playlist = request.form['playlist']
    artists = request.form.getlist('artists')
    if program == "completionist":
        counter = add_all_tracks.main(TOKTOKEN, playlist, artists)
    return f"Congratulations ! The Completionist has created a playlist of {counter} tracks of the artists {artists} in your profile."

@app.route('/startprograms', methods=['POST'])
def startprograms():
    global TOKTOKEN
    program = request.form['program']
    playlist = request.form['playlist']
    artists = request.form.getlist('artists')
    if program == "completionist":
        ret = add_all_tracks.get_user_playground(TOKTOKEN, "21vksa4dfx6ba2r4zyfwjuyqa", playlist)
    return f"Congratulations ! The Completionist has created a playlist of ID {ret}"

if __name__ == '__main__':
    app.run(debug=True)