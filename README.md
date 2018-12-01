# albumd

Web service that generates a nice view of your music collection.

## Features

* Homepage displays a nice collage of your albums
* View track listing of an album
* View all albums under a particular artist
* Download zip file containing all songs in an album
* Generates m3u playlists for streaming (Works with VLC, Audacious can be a little picky)

## Screenshots

![Index page](https://i.witch.press/GAXtqf9n.png)

![Album view](https://i.witch.press/6ybPHloa.png)

## Setup

First, install dependencies:

```sh
python3 -m venv env
./env/bin/pip install -U pip setuptools
./env/bin/pip install -r requirements.txt
```

You need two environment variables:

`XDG_MUSIC_DIR`: this should point to the root of your music collection. The scanner walks everything below this path looking for music.  
`SERVER_NAME`: set to the fully qualified root URL of your app, e.g. `http://localhost:5000`

From here, you can test using `./env/bin/flask run`, but in a real deployment I'd suggest using a real WSGI server.
Personally, I use `flup`'s FCGI/WSGI bridge, but Gunicorn or similar would work perfectly fine.

## Known Issues

oh boy there's a bunch, feel free to submit PRs

* Tracks containing titles with slashes fail in all manner of ways: you can't stream them and zip generation doesn't escape them (idk how to fix this)
* Artists + albums with slashes probably fail hilariously too
* Titles with non-ascii characters appear to cause issues for the m3u generator. (I haven't looked into this fully)
* At the moment there's not really any template customization. You probably need to manually edit some of the templates as it has my username all over it.
