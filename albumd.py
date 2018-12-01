from flask import Flask, render_template, send_file, url_for
from jinja2 import Markup
from scanner import MusicScanner
from io import BytesIO

import os

app = Flask(__name__)
scanner = MusicScanner()

app.jinja_env.trim_blocks = True

hostname = os.getenv("SERVER_NAME")
music_dir = os.getenv("XDG_MUSIC_DIR")
scanner.scan_dir(music_dir)

@app.template_filter("breadcrumbize")
def breadcrumb(val: str):
    parts = []
    stack = ""

    for part in val.split("/"):
        stack = stack + part + "/"

        if part == "":
            parts.append(f'<a href="/"><-</a>')
        else:
            parts.append(f'<a href="{stack.rstrip("/")}">{part}</a>')

    return Markup(u" / ".join(parts))

@app.route("/")
def index():
    return render_template("index.html", albums=scanner.get_all_albums(), breadcrumb="")

@app.route("/<string:artist>")
def show_artist(artist: str):
    artist_info = scanner.artists[artist]

    return render_template("show_artist.html", artist=artist_info, breadcrumb=f"/{artist}")

@app.route("/<string:artist>/<string:album>")
def show_album(artist: str, album: str):
    album_info = scanner.artists[artist].albums[album]

    return render_template("show_album.html", album=album_info, breadcrumb=f"/{artist}/{album}")

@app.route("/<string:artist>/<string:album>.m3u")
def gen_playlist(artist: str, album: str):
    album_info = scanner.artists[artist].albums[album]

    return album_info.generate_m3u(hostname), 200, {
        "Content-Disposition": f"attachment; filename=\"{artist}-{album}.m3u\"",
        "Content-Type": "audio/x-mpegurl"
    }

@app.route("/<string:artist>/<string:album>.zip")
def gen_zip(artist: str, album: str):
    album_info = scanner.artists[artist].albums[album]

    return send_file(album_info.generate_zip(), mimetype="application/zip")

@app.route("/<string:artist>/<string:album>/cover.jpg")
def get_cover(artist: str, album: str):
    album = scanner.artists[artist].albums[album]
    album_cover = album.cover

    if album_cover is None:
        print(album.alt_cover)
        return send_file(album.alt_cover)
    else:
        io = BytesIO(album_cover.data)

    return send_file(io, mimetype=album_cover.mime)

@app.route("/<string:artist>/<string:album>/<path:track>.mp3")
def stream_track(artist: str, album: str, track: str):
    track_info = scanner.artists[artist].albums[album].tracks[track]

    return send_file(track_info.path)

@app.errorhandler(KeyError)
def handle_missing(err):
    return "Not found", 404
