from flask import Flask, redirect, request, render_template, session
from flask_socketio import SocketIO, send, emit
import subprocess
import requests
import json
import sys
sys.path.insert(0, "..")
import add_all_tracks
import helper

app = Flask(__name__)
app.secret_key = 'secretnotrlysecretfornow'
socketio = SocketIO(app)
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
    #print(auth_url)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    global TOKTOKEN
    code = request.args.get('code')
    #print(code)
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
    #print(access_token)
    TOKTOKEN = access_token
    return redirect('/')

@app.route('/startprogram', methods=['POST'])
def startprogram():
    global TOKTOKEN
    program = request.form['program']
    playlist = request.form['playlist']
    artists = request.form.getlist('artists')
    if program == "completionist":
        counter, pretty_artists_list = add_all_tracks.completionist(TOKTOKEN, playlist, artists)
        return f"Congratulations ! The Completionist has created a playlist of {counter} tracks of the artists {pretty_artists_list} in your profile."
    elif program == "bestof":
        tracks_count_per_artist = int(request.form['tracks_number_input'])
        counter, pretty_artists_list = add_all_tracks.mainstreambestof(TOKTOKEN, playlist, artists, tracks_count_per_artist)
        return f"Congratulations ! The MainstreamBestOf has created a playlist of {counter} tracks of the artists {pretty_artists_list} in your profile."
    elif program == "creatorhelper":
        tracks_count_per_artist = int(request.form['tracks_number_input'])
        flat_tracks_ids = helper.get_most_tracks(TOKTOKEN, artists, tracks_count_per_artist)
        session["flat_tracks_ids"] = flat_tracks_ids
        session["flat_tracks_ids_list"] = list(flat_tracks_ids.values())
        session["tracks_to_add"] = []
        session["playlist"] = playlist
        session["artists"] = artists
        return redirect('helperrun')
    return f"Program not recognised..."

@app.route('/helperrun')
def helperrun():
    return render_template('helper.html')

@app.route('/get_track_i')
def get_track_i():
    if request.method == 'POST':
        data = request.get_json()

# @app.route('/startprograms', methods=['POST'])
# def startprograms():
#     global TOKTOKEN
#     program = request.form['program']
#     playlist = request.form['playlist']
#     artists = request.form.getlist('artists')
#     if program == "completionist":
#         ret = add_all_tracks.get_user_playground(TOKTOKEN, "21vksa4dfx6ba2r4zyfwjuyqa", playlist)
#     return f"Congratulations ! The Completionist has created a playlist of ID {ret}"

@socketio.on('connect')
def send_tracklist():
    emit("startup", session["flat_tracks_ids"])

@socketio.on('next_track')
def send_nexttrack(i, comm):
    # Add track if needed
    if i > 0 and i <= len(session["flat_tracks_ids_list"]):
        if comm == "add":
            session["tracks_to_add"].append(session["flat_tracks_ids_list"][i-1])
        print(session["tracks_to_add"])
    
    # Prepare next track infos
    if i >= len(session["flat_tracks_ids_list"]):
        emit("time_to_end")
        return # TODO: Add return specific to end of tracklist to handle it on frontend
    response_code, track_info = add_all_tracks.get_track(TOKTOKEN, session["flat_tracks_ids_list"][i][14:])
    #Get track name
    track_name = track_info["name"]
    #Get Artists names
    artists_names = []
    for artist in track_info["artists"]:
        artists_names.append(artist["name"])
    #Get album name
    album_name = track_info["album"]["name"]
    #Get album cover
    album_cover = track_info["album"]["images"][0]["url"]
    #Get audio url
    audio_url = track_info["preview_url"] 
    emit("response_next_track",(track_name, artists_names, album_name, album_cover, audio_url))

@socketio.on('end_helper')
def end_helper():
    #add songs to playlist
    counter, pretty_artists_list = helper.helper_final(TOKTOKEN, session["playlist"], session["artists"], session["tracks_to_add"])
    #emit ok or ko TODO: KO
    emit("ok_helper", f"Congratulations ! The CreatorHelper has created a playlist of {counter} tracks of the artists {pretty_artists_list} in your profile.")


if __name__ == '__main__':
    socketio.run(app, debug=True)