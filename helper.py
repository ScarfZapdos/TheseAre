import add_all_tracks as aat
import math
import json

def get_most_tracks(token, artists_list, tracks_count_per_artist):
    user_id = "21vksa4dfx6ba2r4zyfwjuyqa"
    artists_ids = aat.search_artists(token, artists_list)
    tracks_ids = {}
    for index, artist in enumerate(artists_ids):
        _ , tracks_ids[artist] = aat.get_artist_tracks(token, artists_list[index], tracks_count_per_artist)
    #json.dump(tracks_ids, file, indent=4)
    print(tracks_ids)
    flat_tracks_ids = []

    dict_tracks_weaved = {}
    # Determine the maximum number of elements in any sub-dictionary
    max_len = max(len(artist_tracks_ids) for artist_tracks_ids in tracks_ids.values())

    for i in range(max_len):
        for artist_tracks_ids in tracks_ids.values():
            if i < len(artist_tracks_ids):
                key, value = list(artist_tracks_ids.items())[i]
                dict_tracks_weaved[key] = value
    flat_tracks_ids = dict_tracks_weaved
    print(dict_tracks_weaved)
    return dict_tracks_weaved

def helper_final(token, playlist_name, artists_list, tracklist):
    user_id = "21vksa4dfx6ba2r4zyfwjuyqa"
    counter = 0
    playground = aat.get_user_playground(token, user_id, playlist_name, "The Creator Helper", aat.pretty_list(artists_list))
    for k in range(math.floor(len(tracklist)/90)+1):
        lacunar_flat_tracks = tracklist[k*90:90+k*90]
        counter += len(lacunar_flat_tracks)
        aat.add_to_playground(token, playground["id"], lacunar_flat_tracks)
    return counter, aat.pretty_list(artists_list)