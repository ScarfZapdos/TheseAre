import requests
import json
import math

#prompted_playground_name = "G. Showcase"
#prompted_artists_list = ["AJR", "BLACKPINK", "Imagine Dragons"]
prompted_client_id = '0356a0d5fd974f4497a212601fa2b636'
file = open("tracks.json", "w")

def search_artist(access_token, artist):
    url = "https://api.spotify.com/v1/search"
    header = {"Authorization": f"Bearer {access_token}"}
    body = {"q":f"{artist}",
            "type":"artist",
            "market":"FR",
            "limit":"1",
            "offset":"0"}
    response = requests.get(url=url, headers=header, params=body)
    if response.status_code != 200:
        return response.status_code, None, None
    else:
        search_result_name = response.json()["artists"]["items"][0]["name"]
        search_result_id = response.json()["artists"]["items"][0]["id"]
        return response.status_code, search_result_name, search_result_id

def search_artists(access_token, artists):
    artists_ids = {}
    for artist in artists:
        _ , search_result_name, search_result_id = search_artist(access_token, artist)
        artists_ids[search_result_name] = search_result_id
    return artists_ids

def get_track(access_token, track_id):
    #Build HTTP Request
    tracks_ids = {}
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    header = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url=url, headers=header)
    print(response.json())
    if response.status_code != 200:
        return response.status_code, None
    else:
        return response.status_code, response.json()


def get_artist_tracks(access_token, artist, tracks_count_per_artist):
    #Build HTTP Request
    tracks_ids = {}
    url = "https://api.spotify.com/v1/search"
    header = {"Authorization": f"Bearer {access_token}"}
    body = {"q":f"{artist}",
            "type":"track",
            "market":"FR",
            "limit":"50",
            "offset":"0"}
    response = requests.get(url=url, headers=header, params=body)
    next_url = url
    #Get tracks loop, 50 per call
    while next_url != None:
        if next_url != url:
            response = requests.get(url=next_url, headers=header)
        #print(response.status_code)
        if response.status_code != 200:
            return response.status_code, None
        else:
            for track in response.json()["tracks"]["items"]:
                artist_targeted = False
                for featured in track["artists"]:
                    artist_targeted = artist_targeted or (featured["name"] == artist)
                if artist_targeted:
                    search_result_name = track["name"]
                    search_result_id = track["uri"]
                    tracks_ids[search_result_name] = search_result_id
                    if tracks_count_per_artist != -1 and len(tracks_ids) >= tracks_count_per_artist:
                        return response.status_code, tracks_ids
            next_url = response.json()["tracks"]["next"]
    return response.status_code, tracks_ids    

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    header = {"Content-Type" : "application/x-www-form-urlencoded"}
    body = {"grant_type":"client_credentials", 
            "client_id":"0356a0d5fd974f4497a212601fa2b636", 
            "client_secret":"0490e9dd613344979d6b1b68c82000f9"}
    response = requests.post(url=url, headers=header, data=body)
    print(f"Token : {response.json()}")
    if response.status_code != 200:
        return response.status_code, None
    else:
        return response.status_code,response.json()["access_token"]

def get_authorization():
    url = "https://accounts.spotify.com/authorize"
    body = {"client_id":"0356a0d5fd974f4497a212601fa2b636",
            "response_type":"code",
            "redirect_uri":"http://localhost:5000/callback",
            'scope': 'playlist-modify-private'}
    response = requests.post(url=url, data=body)
    print(response.status_code, response)
    if response.status_code != 200:
        return response.status_code, None
    else:
        return response.status_code,response.json()["access_token"]

def get_current_user(access_token):
    url = "https://api.spotify.com/v1/me"
    header = {"Authorization": f"'Bearer {access_token}'"}
    response = requests.get(url=url, headers=header)
    #print(f"Header : {header} User : {response.json()}")
    if response.status_code != 200:
        return response.status_code, None
    else:
        return response.status_code,response.json()["id"]

def get_user_playground(access_token, user_id, playlist_name, program, pretty_artists_list):
    header = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists?offset=0&limit=50"
    return_playlist = {}
    while url != None:
        response = requests.get(url=url, headers=header)
        #print(f"User Playlists : {response.json()}")
        print(f"URL : {url}, header : {header}")
        print(f"response code : {response.status_code}")
        if response.status_code == 200:
            for playlist in response.json()["items"]:
                if playlist["name"] == playlist_name:
                    return_playlist = playlist
            url = response.json()["next"]
    #If empty: create playlist named as given
    if return_playlist == {}:
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        header["Content-Type"] = "application/json"
        body = {"name":playlist_name,
            "description":f"Created with {program} from Hugo's wonderful app, using the best of {pretty_artists_list}"}
        response = requests.post(url=url, headers=header, json=body)
        return_playlist = response.json()
    return return_playlist

def add_to_playground(access_token, playground_id, uri_array):
    url = f"https://api.spotify.com/v1/playlists/{playground_id}/tracks"
    header = {"Authorization": f"Bearer {access_token}"}
    body = {"uris":uri_array}
    response = requests.post(url=url, headers=header, json=body)
    print(f"Added ? : {response.status_code} : {response.text}")
    
def pretty_list(L):
    ret = ""
    for i, e in enumerate(L):
        if i == len(L)-1:
            ret += f" and {e}"
        else:
            ret += f"{e}, "
    return ret

def mainstreambestof(token, playlist_name, artists_list, tracks_count_per_artist):
    user_id = "21vksa4dfx6ba2r4zyfwjuyqa"
    playground = get_user_playground(token, user_id, playlist_name, "The Mainstream BestOf", pretty_list(artists_list))
    artists_ids = search_artists(token, artists_list)
    tracks_ids = {}
    for index, artist in enumerate(artists_ids):
        _ , tracks_ids[artist] = get_artist_tracks(token, artists_list[index], tracks_count_per_artist)
    json.dump(tracks_ids, file, indent=4)
    flat_tracks_ids = []
    counter = 0
    for artist_tracks in tracks_ids.values():
        flat_tracks_ids.extend(artist_tracks.values())
    for k in range(math.floor(len(flat_tracks_ids)/90)+1):
        lacunar_flat_tracks = flat_tracks_ids[k*90:90+k*90]
        counter += len(lacunar_flat_tracks)
        add_to_playground(token, playground["id"], lacunar_flat_tracks)
    return counter, pretty_list(artists_list)

def completionist(token, playlist_name, artists_list):

    user_id = "21vksa4dfx6ba2r4zyfwjuyqa"
    playground = get_user_playground(token, user_id, playlist_name, "The Completionist", pretty_list(artists_list))
    artists_ids = search_artists(token, artists_list)
    tracks_ids = {}
    for index, artist in enumerate(artists_ids):
        _ , tracks_ids[artist] = get_artist_tracks(token, artists_list[index], -1)
    json.dump(tracks_ids, file, indent=4)
    flat_tracks_ids = []
    counter = 0
    for artist_tracks in tracks_ids.values():
        flat_tracks_ids.extend(artist_tracks.values())
    for k in range(math.floor(len(flat_tracks_ids)/90)+1):
        lacunar_flat_tracks = flat_tracks_ids[k*90:90+k*90]
        counter += len(lacunar_flat_tracks)
        add_to_playground(token, playground["id"], lacunar_flat_tracks)
    return counter, pretty_list(artists_list)