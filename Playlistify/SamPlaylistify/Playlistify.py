import spotipy


class Playlistify:
    def __init__(self):
        self.spotipy = None
        self.access_token = ''
        self.playlist_title = ""
        self.playlist_url = ""
        self.text = ""
        self.username = ''

    def set_auth_details(self):
        self.spotipy = spotipy.Spotify(auth=self.access_token)
        self.username = self.get_username()
        print(self.username)
        return

    def create_playlist_on_spotify(self):
        response = self.spotipy.user_playlist_create(
            user=self.username,
            name=self.playlist_title,
            public=True,
            description="playlist created using Playlistify"
        )
        self.playlist_url = response['external_urls']['spotify']
        return response

    def get_username(self):
        response = self.spotipy.current_user()
        print(response)
        return response['id']

    def add_song_to_playlist(self, trackID, playListID):
        response = self.spotipy.playlist_add_items(
            playlist_id=playListID,
            items=trackID
        )
        return response

    def search_song(self, phrase, page):
        if page > 8:
            return -1
        response = self.spotipy.search(
            q=phrase,
            limit=50,
            offset=50 * page,
            type='track'
        )
        results = response['tracks']['items']
        if results:
            for current_track in results:
                print(current_track['name'])
                if current_track['name'].lower() == phrase.lower():
                    print(current_track['name'])
                    print("found")
                    return current_track['uri']
            if len(phrase.split()) <= 3:
                return self.search_song(phrase=phrase, page=page + 1)
            else:
                return -1
        else:
            return -1

    def parse_text_search(self):
        split_text = self.text.split()
        track_ids = []
        x = 0
        while x < len(split_text):
            phrase_size = 4
            for y in range(phrase_size, -1, -1):
                print(f'x:{x} y: {y}')
                if x + y < len(split_text):
                    temp_phrase = " ".join(split_text[x:x + y + 1])
                    print("temp_phrase: "+temp_phrase)
                    result = self.search_song(phrase=temp_phrase, page=0)
                    if result != -1:
                        track_ids.append(result)
                        x = x + y + 1
                    else:
                        if y == 0:
                            raise Exception(f"No song found for {temp_phrase}")

        return track_ids
