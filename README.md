# Neighborhood Helpboard

A simple neighborhood messaging app built in Python. This project runs a plain TCP backend, a browser-facing HTTP gateway, and a Supabase PostgreSQL persistence layer.

## What this project includes

* `server.py` — a plain TCP server that accepts text-based commands from clients.
* `routes.py` — parses TCP commands such as `POST`, `LIST`, `LISTJSON`, `GET`, `EXIT`, and `SHUTDOWN`.
* `bridge.py` — an HTTP gateway that translates browser requests into TCP server commands.
* `database.py` — a Supabase PostgreSQL storage layer using `psycopg2` connection pooling.
* `index.html` — a static web UI that runs in the browser and interacts with the bridge.
* `dump.sql` — Supabase PostgreSQL schema migration for the `posts` table.

## Key behavior

* The TCP server stores and retrieves posts using `database.py`.
* `database.py` connects to Supabase PostgreSQL through `DATABASE_URL` or `SUPABASE_DATABASE_URL`.
* The bridge serves the web UI at `http://localhost:8000/` and keeps the `/messages` API for browser POST and GET requests.
* The browser UI does not need direct access to the TCP port.

## Supabase setup

1. Create a Supabase project.
2. Open the Supabase SQL editor and run `dump.sql`.
3. Copy the PostgreSQL connection URI from Supabase Project Settings > Database > Connection string.
4. Set `DATABASE_URL` or `SUPABASE_DATABASE_URL` to that connection string.
5. Use the pooled connection string on port `6543` for serverless deployments such as Render, Railway, or Fly.io.

## Database behavior

The Supabase PostgreSQL `posts` table contains:

* `id` — unique integer primary key
* `username` — sender name
* `type` — category of the message, such as `info` or `alert`
* `message` — the content text
* `timestamp` — UNIX timestamp stored as a double-precision float

`database.py` exposes the same public methods used by `server.py`:

* `add_post(username, type_, message)` → returns a dict with the inserted post
* `list_posts(type_filter=None, limit=10)` → returns a list of dicts ordered oldest to newest
* `get_post(id_)` → returns a dict or `None`

## How to run it

1. Open a terminal in the project folder.
2. Install Python dependencies:

```powershell
python -m pip install -r .\requirements.txt
```

3. Copy `.env.example` to `.env` and add your Supabase PostgreSQL connection string:

```powershell
copy .env.example .env
```

4. Start the TCP server:

```powershell
python .\server.py
```

5. In a second terminal, start the HTTP bridge:

```powershell
python .\bridge.py
```

6. Open your browser and go to:

```text
http://localhost:8000/
```

7. Use the form to post a new message, then click `Refresh` to load the latest posts.

## Environment variables

You can override the defaults with environment variables:

* `DATABASE_URL` or `SUPABASE_DATABASE_URL` — Supabase PostgreSQL connection URI
* `SUPABASE_SCHEMA` — PostgreSQL schema for the `posts` table, default `public`
* `SUPABASE_POSTS_TABLE` — table name, default `posts`
* `DATABASE_SSL_MODE` — PostgreSQL SSL mode, default `require`
* `DATABASE_POOL_MIN` — minimum PostgreSQL connection pool size, default `1`
* `DATABASE_POOL_MAX` — maximum PostgreSQL connection pool size, default `10`
* `TCP_SERVER_IP` — TCP server bind address, default `0.0.0.0`
* `SERVER_PORT` or `PORT` — TCP server port, default `7000`
* `HTTP_PORT` — bridge HTTP port, default `8000`
* `HTTP_BIND` — bridge bind address, default `0.0.0.0`
* `SHOWN_HOST` — host name shown in the bridge log, default `localhost`
* `SHOWN_PORT` — port shown in the bridge log, default `HTTP_PORT`
* `TCP_SERVER_IP` — backend TCP server host for the bridge, default `127.0.0.1`
* `SERVER_PORT` or `TCP_PORT` — backend TCP server port for the bridge, default `7000`
* `ADMIN_TOKEN` — optional token for the `SHUTDOWN` command

Example:

```powershell
$env:DATABASE_URL = 'postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres'
python .\server.py
```

## Testing the setup

### Test the Supabase backend directly

Run this from the project root after setting `DATABASE_URL` or `SUPABASE_DATABASE_URL`:

```powershell
python -c "from database import Database; db=Database(); post=db.add_post('tester','info','Test Supabase post'); print(post); print(db.list_posts()); print(db.get_post(post['id'])); db.close()"
```

### Test the TCP server

Start `server.py`, then use a socket client to connect to `127.0.0.1:7000`.

### Test the browser UI

With `bridge.py` running, open `http://localhost:8000/` and confirm:

* the page loads
* you can submit a post
* the message list refreshes

## Docker support

A container image can bundle both services in one deployable unit.

The bridge listens on `HTTP_PORT` and connects to the TCP server at
`TCP_SERVER_IP:SERVER_PORT`. The TCP port is internal to the container and
does not need a Docker `-p` mapping. `SHOWN_HOST` and `SHOWN_PORT` only control
the URL printed in the bridge log; they do not change socket binding.

Build the image from the project root:

```powershell
docker build -t neighborhood-helpboard .
```

Run the container with the confirmed local configuration:

```powershell
docker run --rm `
  -p 9000:9000 `
  -e HTTP_PORT=9000 `
  -e SERVER_PORT=7001 `
  -e SHOWN_HOST=localhost `
  -e SHOWN_PORT=9000 `
  -e DATABASE_URL="$env:DATABASE_URL" `
  neighborhood-helpboard
```
or

```powershell
$env:DATABASE_URL = 'postgresql://postgres:URL_ENCODED_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres'
docker run --rm `
  --name neighborhood-helpboard `
  -p 9000:9000 `
  -e HTTP_PORT=9000 `
  -e SERVER_PORT=7001 `
  -e SHOWN_HOST=localhost `
  -e SHOWN_PORT=9000 `
  -e DATABASE_URL="$env:DATABASE_URL" `
  neighborhood-helpboard
```

To load the database URL from an environment file, put this in `.env`:

```text
DATABASE_URL=postgresql://postgres:URL_ENCODED_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
```

Then run:

```powershell
docker run --rm `
  --name neighborhood-helpboard `
  --env-file .env `
  -p 9000:9000 `
  -e HTTP_PORT=9000 `
  -e SERVER_PORT=7001 `
  -e SHOWN_HOST=localhost `
  -e SHOWN_PORT=9000 `
  neighborhood-helpboard
```

If you want to use the confirmed `9000` HTTP / `7001` internal TCP configuration:

```powershell
docker run --rm `
  -p 9000:9000 `
  -e HTTP_PORT=9000 `
  -e SERVER_PORT=7001 `
  -e SHOWN_HOST=localhost `
  -e SHOWN_PORT=9000 `
  neighborhood-helpboard
```
or

```powershell
$env:DATABASE_URL = 'postgresql://postgres:URL_ENCODED_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres'

```

Or load the same database URL from `.env`:

```powershell
docker run --rm `
  --name neighborhood-helpboard `
  --env-file .env `
  -p 9000:9000 `
  -e HTTP_PORT=9000 `
  -e SERVER_PORT=7001 `
  -e SHOWN_HOST=localhost `
  -e SHOWN_PORT=9000 `
  neighborhood-helpboard
```

Replace `URL_ENCODED_PASSWORD` and `YOUR_PROJECT_REF` with your Supabase values. Encode special password characters before placing the password in the URL.

> **Note:** Ensure `.env` is in `.gitignore` to prevent committing secrets. If port `9000` is already in use, choose another HTTP port consistently, such as `HTTP_PORT=9001` with `-p 9001:9001`.

## Deployment guidance

This project is not a static-only website. It requires a running Python backend and cannot be published as a complete app on Netlify by itself.

Recommended free hosts for this project:

* Render.com
* Railway.app
* Fly.io

Render is the simplest choice for beginners because it can deploy your existing `Dockerfile` directly.

### Deploy on Render with Docker

1. Push your repository to GitHub.
2. Create a free Render account.
3. Create a new `Web Service` and connect your GitHub repository.
4. Choose `Docker` as the environment so Render uses your `Dockerfile`.
5. Set environment variables if needed:

   * `DATABASE_URL`
   * `HTTP_PORT=8000`
   * `TCP_SERVER_IP=127.0.0.1`
   * `SERVER_PORT=7000`
   * `SERVER_PORT=7000`

6. Deploy and open the generated URL.

### Netlify note

Netlify can host only the static `index.html` file, but this app also needs `bridge.py` and `server.py` to run. For a complete working deployment, use Render, Railway, or Fly.io instead.

## Notes and recommendations

* `.env` is ignored by Git. Use environment variables in production.
* Supabase PostgreSQL connections require SSL, so `DATABASE_SSL_MODE=require` is used by default.
* The backend creates the `posts` table and indexes automatically on startup, but `dump.sql` should still be run once during project setup.
* The TCP command protocol is unchanged, so the bridge keeps compatibility with the original design.

## Future improvements

* Add authentication and request validation.
* Add better error handling for TCP/HTTP failures.
* Add pagination or filtering support on the UI.
* Convert `client.py` into a shared client module for both TCP and HTTP access.
* Add message deleting with an admin token.