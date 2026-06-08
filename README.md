# Neighborhood Helpboard

A simple neighborhood messaging app built in Python. This project demonstrates a small TCP backend, a browser-facing HTTP gateway, and a lightweight SQLite persistence layer.

## What this project includes

- `server.py` — a plain TCP server that accepts text-based commands from clients.
- `routes.py` — parses TCP commands such as `POST`, `LIST`, `LISTJSON`, `GET`, `EXIT`, and `SHUTDOWN`.
- `bridge.py` — an HTTP gateway that translates browser requests into TCP server commands.
- `database.py` — an SQLite-backed storage layer for posts.
- `index.html` — a static web UI that runs in the browser and interacts with the bridge.

## Key behavior

- The TCP server stores and retrieves posts using `database.py`.
- `database.py` now uses `sqlite3` and creates `helpboard.db` automatically.
- The bridge serves the web UI at `http://localhost:8000/` and keeps the `/messages` API for browser POST and GET requests.
- The browser UI has been refreshed with improved styling for better usability.
- The browser UI does not need direct access to the TCP port.

## How the architecture works

1. `server.py` starts a TCP server on `127.0.0.1:7000`.
2. `database.py` initializes an SQLite database file called `helpboard.db` and ensures a `posts` table exists.
3. Clients send plain-text commands to the TCP server.
4. `routes.py` executes the commands and maps them to `Database` methods.
5. `bridge.py` listens on `http://localhost:8000` and converts HTTP requests into TCP commands.
6. `index.html` is served by `bridge.py` on `GET /` and performs AJAX requests against `/messages`.
7. `bridge.py` also exposes a health endpoint at `/health` so deployment platforms can confirm the app is running.

## Database behavior

The SQLite `posts` table contains:

- `id` — unique integer primary key
- `username` — sender name
- `type` — category of the message (e.g. `info`, `alert`)
- `message` — the content text
- `timestamp` — UNIX timestamp stored as a float

`database.py` exposes the same public methods used by `server.py`:

- `add_post(username, type_, message)` → returns a dict with the inserted post
- `list_posts(type_filter=None, limit=10)` → returns a list of dicts
- `get_post(id_)` → returns a dict or `None`

This preserves compatibility with the existing server and routes logic.

## How to run it

1. Open a terminal in the project folder.
2. Start the TCP server:

   ```powershell
   python .\server.py
   ```

3. In a second terminal, start the HTTP bridge:

   ```powershell
   python .\bridge.py
   ```

4. Open your browser and go to:

   ```text
   http://localhost:8000/
   ```

5. Use the form to post a new message, then click `Refresh` to load the latest posts.

> Generated SQLite files such as `helpboard.db`, `helpboard.db-shm`, and `helpboard.db-wal` are runtime artifacts and should not be committed to source control.

### Using environment variables

You can override the default ports and backend host with environment variables:

- `SERVER_IP` — TCP server bind address (default `0.0.0.0`)
- `SERVER_PORT` or `PORT` — TCP server port (default `7000`)
- `HTTP_PORT` — bridge HTTP port (default `8000`)
- `TCP_SERVER_IP` — backend TCP server host for the bridge (default `127.0.0.1`)
- `TCP_SERVER_PORT` or `TCP_PORT` — backend TCP server port for the bridge (default `7000`)

Example:

```powershell
$env:HTTP_PORT = '9000'
python .\bridge.py
```

## Testing the setup

### Test the SQLite backend directly

Run this from the project root:

```powershell
python - <<'PY'
from database import Database

db = Database()
post = db.add_post('tester', 'info', 'Test SQLite post')
print(post)
print(db.list_posts())
print(db.get_post(post['id']))
PY
```

### Test the TCP server

Start `server.py`, then use `client.py` or a socket script to connect to `127.0.0.1:7000`.

### Test the browser UI

With `bridge.py` running, open `http://localhost:8000/` and confirm:

- the page loads
- you can submit a post
- the message list refreshes

## Docker support

A container image can bundle both services in one deployable unit.

Build the image from the project root:

```powershell
docker build -t neighborhood-helpboard .
```

Run the container locally exposing the bridge port:

```powershell
docker run --rm -p 8000:8000 neighborhood-helpboard
```

If you want to override ports inside the container:

```powershell
docker run --rm -p 9000:9000 -e HTTP_PORT=9000 neighborhood-helpboard
```

## Deployment guidance

This project is not a static-only website. It requires a running Python backend and cannot be published as a complete app on Netlify by itself.

Recommended free hosts for this project:

- Render.com
- Railway.app
- Fly.io

Render is the simplest choice for beginners because it can deploy your existing `Dockerfile` directly.

### Deploy on Render with Docker

1. Push your repository to GitHub.
2. Create a free Render account.
3. Create a new `Web Service` and connect your GitHub repository.
4. Choose `Docker` as the environment so Render uses your `Dockerfile`.
5. Set environment variables if needed:
   - `HTTP_PORT=8000`
   - `TCP_SERVER_IP=127.0.0.1`
   - `TCP_SERVER_PORT=7000`
   - `SERVER_PORT=7000`
6. Deploy and open the generated URL.

### Netlify note

Netlify can host only the static `index.html` file, but this app also needs `bridge.py` and `server.py` to run. For a complete working deployment, use Render, Railway, or Fly.io instead.

## Notes and recommendations

- `helpboard.db` is created automatically when the app starts.
- `bridge.py` now serves `index.html` directly when a browser navigates to `/`.
- `server.py` still uses the same TCP command protocol, so the bridge keeps compatibility with the original design.

## Future improvements

- Add authentication and request validation.
- Add better error handling for TCP/HTTP failures.
- Add pagination or filtering support on the UI.
- Convert `client.py` into a shared client module for both TCP and HTTP access.
