from flask import Flask, session, request, redirect, render_template
from Playlistify import Playlistify
from spotipy.oauth2 import SpotifyOAuth
import time

app = Flask(__name__)
app.secret_key = 'MY-SUPER-SECRET-KEY'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
redirect_uri = 'https://www.playlistify.samcsd.com/authorize'


@app.route("/")
def homepage():
    return render_template('homepage.html')


@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    playlist = Playlistify()
    playlist.access_token = session.get('token_info').get('access_token')
    playlist.set_auth_details()
    return redirect('/inputs')


@app.route("/inputs")
def inputs():
    return render_template('inputs.html')


@app.route("/result")
def result():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    playlist = Playlistify()
    playlist.access_token = session.get('token_info').get('access_token')
    playlist.set_auth_details()
    playlist_name = request.args.get("playlist_name", "")
    input_text = request.args.get("input_text", "")
    if playlist_name and input_text:
        playlist.playlist_title = playlist_name
        playlist.text = input_text
        song_id = playlist.parse_text_search()
        playlist_id = playlist.create_playlist_on_spotify()
        snapshot_id = playlist.add_song_to_playlist(
            trackID=song_id,
            playListID=playlist_id['id']
        )
        return render_template('results.html', playlist_id=playlist_id['id'], playlist_url=playlist.playlist_url)
    else:
        return redirect("/inputs")


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


def get_token():
    token_valid = False
    token_info = session.get("token_info")

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="",
        client_secret="",
        redirect_uri=redirect_uri,
        scope="playlist-modify-public playlist-modify-private user-read-private user-read-email")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
