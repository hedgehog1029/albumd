from mutagen.mp3 import MP3
from zipfile import ZipFile
from io import BytesIO

import os
import os.path
import mutagen

class Track:
    def __init__(self, tags: mutagen.Tags, info: mutagen.mp3.MPEGInfo, path: str):
        self.name = tags["TIT2"].text[0]
        self.artist = tags["TPE1"].text[0]
        self.album = tags["TALB"].text[0]

        pos = tags["TRCK"].text[0].split("/")[0]
        self.index = int(pos)

        self.duration = info.length
        self.path = path

class Album:
    def __init__(self, tags: mutagen.Tags, path: str):
        self.name = tags["TALB"].text[0]
        self.artist = tags["TPE1"].text[0]
        self.cover = tags.get("APIC:", tags.get("APIC", None))
        self.alt_cover = os.path.join(os.path.dirname(path), "cover.jpg")
        self.tracks = {}

    def generate_m3u(self, url_root: str):
        header = "#EXTM3U\n\n"

        for track in self.tracks.values():
            line1 = f"#EXTINF:{int(track.duration):d},{self.artist} - {track.name}"
            line2 = f"{url_root}/{self.artist}/{self.name}/{track.name}.mp3"

            header = header + f"{line1}\n{line2}\n\n"

        return header

    def generate_zip(self):
        io = BytesIO()
        zip = ZipFile(io, "w")

        for track in self.tracks.values():
            zip.write(track.path, f"{track.name}.mp3")

        zip.close()

        io.seek(0)
        return io

    def sorted_tracks(self):
        return sorted(self.tracks.values(), key=lambda t: t.index)

class Artist:
    def __init__(self, tags: mutagen.Tags):
        self.name = tags["TPE1"].text[0]
        self.albums = {}

class MusicScanner:
    def __init__(self):
        self.artists = {}

    def add_file(self, path: str):
        try:
            info = MP3(path)
            tags = info.tags
            artist_name = tags["TPE1"].text[0]
            album_name = tags["TALB"].text[0]
            track_name = tags["TIT2"].text[0]

            artist = self.artists.get(artist_name, Artist(tags))
            album = artist.albums.get(album_name, Album(tags, path))
            track = album.tracks.get(track_name, Track(tags, info.info, path))

            album.tracks[track_name] = track
            artist.albums[album_name] = album
            self.artists[artist_name] = artist
        except (TypeError, KeyError):
            pass  # invalid id3 tags :(
        except mutagen.MutagenError:
            pass  # skip invalid files

    def scan_dir(self, path: str):
        for dir, subdirs, files in os.walk(path):
            for name in files:
                filepath = os.path.join(dir, name)

                self.add_file(filepath)

    def get_all_albums(self):
        albums = []
        for artist in self.artists.values():
            albums = albums + list(artist.albums.values())
        return sorted(albums, key=lambda a: a.name)
