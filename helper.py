import add_all_tracks as aat
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
    flat_tracks_ids = list(dict_tracks_weaved)
    print(flat_tracks_ids)
    return flat_tracks_ids